# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pyyaml>=6.0",
#   "python-pptx>=1.0",
# ]
# ///
"""AI Sniff Test: flag common LLM speech patterns in text and presentations.

Two detector layers:
  1. Pattern layer  - regex from patterns.yaml (lexical, syntactic, rhetorical).
  2. Structural layer - functions below (bold spam, colon headers, parallel bullets).

High-confidence hits are trusted. Heuristic hits are flagged for human/LLM review.
The score is a smell index, not proof of authorship.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_WEIGHT = 1.0


@dataclass
class Pattern:
    label: str
    regex: re.Pattern[str]
    weight: float
    confidence: str  # "high" | "heuristic"
    category: str


@dataclass
class Hit:
    category: str
    label: str
    confidence: str
    weight: float
    line: int
    excerpt: str


# --- loading ----------------------------------------------------------------


def _to_pattern(raw: object, category: str) -> Pattern:
    if isinstance(raw, str):
        rx = re.compile(rf"\b{re.escape(raw)}\b", re.IGNORECASE)
        return Pattern(raw, rx, DEFAULT_WEIGHT, "high", category)
    if isinstance(raw, dict):
        return Pattern(
            label=raw["label"],
            regex=re.compile(raw["regex"], re.IGNORECASE),
            weight=float(raw.get("weight", DEFAULT_WEIGHT)),
            confidence=raw.get("confidence", "high"),
            category=category,
        )
    raise ValueError(f"Bad pattern entry in {category}: {raw!r}")


def load_patterns(path: Path) -> list[Pattern]:
    data = yaml.safe_load(path.read_text())
    patterns: list[Pattern] = []
    for category, entries in (data or {}).items():
        for raw in entries or []:
            patterns.append(_to_pattern(raw, category))
    return patterns


# --- input ------------------------------------------------------------------


def read_text(source: str | None, raw_text: str | None) -> str:
    if raw_text is not None:
        return raw_text
    if source is None or source == "-":
        return sys.stdin.read()
    p = Path(source)
    if p.suffix.lower() == ".pptx":
        return _read_pptx(p)
    return p.read_text()


def _read_pptx(path: Path) -> str:
    try:
        from pptx import Presentation
    except ImportError:
        sys.exit("pptx input needs python-pptx. Run this script with uv run --script, which installs it.")
    prs = Presentation(str(path))
    lines: list[str] = []
    for i, slide in enumerate(prs.slides, 1):
        lines.append(f"# slide {i}")
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    text = "".join(run.text for run in para.runs)
                    if text.strip():
                        lines.append(text)
    return "\n".join(lines)


# --- pattern detection ------------------------------------------------------


def scan_patterns(text: str, patterns: list[Pattern]) -> list[Hit]:
    lines = text.splitlines()
    hits: list[Hit] = []
    for n, line in enumerate(lines, 1):
        for pat in patterns:
            for m in pat.regex.finditer(line):
                hits.append(
                    Hit(pat.category, pat.label, pat.confidence, pat.weight, n, m.group(0))
                )
    return hits


# --- structural detection ---------------------------------------------------

BULLET = re.compile(r"^\s*[-*+]\s+(.*\S)")
BOLD = re.compile(r"\*\*[^*]+\*\*")
HEADER_COLON = re.compile(r"^\s*#{1,6}\s+\S.*:\s+\S")


def scan_structural(text: str) -> list[Hit]:
    lines = text.splitlines()
    hits: list[Hit] = []

    # bold spam: 2+ bold runs on one line
    for n, line in enumerate(lines, 1):
        if len(BOLD.findall(line)) >= 2:
            hits.append(Hit("formatting", "bold spam (>=2 bold runs)", "high", 1.0, n, line.strip()[:60]))

    # header with colon subtitle: "## Feature: it ships faster"
    for n, line in enumerate(lines, 1):
        if HEADER_COLON.match(line):
            hits.append(Hit("formatting", "colon-subtitle header", "heuristic", 1.0, n, line.strip()[:60]))

    # parallel-fragment bullets: 3+ consecutive bullets, similar length,
    # capitalized, no terminal punctuation (the deck-bullet tell)
    hits.extend(_parallel_bullets(lines))
    return hits


def _parallel_bullets(lines: list[str]) -> list[Hit]:
    hits: list[Hit] = []
    run: list[tuple[int, str]] = []

    def flush() -> None:
        if len(run) >= 3:
            counts = [len(t.split()) for _, t in run]
            spread = max(counts) - min(counts)
            capped = all(t[:1].isupper() for _, t in run)
            no_period = all(not t.endswith((".", "!", "?")) for _, t in run)
            if spread <= 2 and capped and no_period:
                first = run[0][0]
                hits.append(
                    Hit("formatting", f"parallel fragments ({len(run)} bullets)", "heuristic", 1.5, first, run[0][1][:60])
                )
        run.clear()

    for n, line in enumerate(lines, 1):
        m = BULLET.match(line)
        if m:
            run.append((n, m.group(1)))
        else:
            flush()
    flush()
    return hits


# --- scoring & report -------------------------------------------------------

VERDICTS = [
    (15, "🟢 Clean. Reads human."),
    (35, "🟡 Some tells. Probably fine, light edit."),
    (60, "🟠 Smells AI-ish. Worth a rewrite pass."),
    (10**9, "🔴 Heavy AI signature. Rewrite."),
]


def score(hits: list[Hit], word_count: int) -> float:
    """Weighted hit density per 1000 words, capped at 100. Heuristic hits half-weight."""
    if word_count == 0:
        return 0.0
    total = sum(h.weight * (0.5 if h.confidence == "heuristic" else 1.0) for h in hits)
    per_1k = total / word_count * 1000
    return min(per_1k * 6, 100.0)


def verdict(s: float) -> str:
    for ceiling, label in VERDICTS:
        if s < ceiling:
            return label
    return VERDICTS[-1][1]


def render(hits: list[Hit], word_count: int) -> str:
    s = score(hits, word_count)
    cats = ["lexical", "syntactic", "rhetorical", "sycophancy", "formatting"]
    out = [f"## AI Sniff Test: {s:.0f}/100", "", verdict(s), "", f"{word_count} words, {len(hits)} hits", ""]

    out.append("| category | hits | high | heuristic |")
    out.append("|---|---|---|---|")
    for c in cats:
        ch = [h for h in hits if h.category == c]
        hi = sum(1 for h in ch if h.confidence == "high")
        he = len(ch) - hi
        out.append(f"| {c} | {len(ch)} | {hi} | {he} |")
    out.append("")

    for c in cats:
        ch = sorted([h for h in hits if h.category == c], key=lambda h: h.line)
        if not ch:
            continue
        out.append(f"### {c}")
        for h in ch:
            tag = "" if h.confidence == "high" else " _(review)_"
            out.append(f"- L{h.line}: **{h.label}**{tag} -> `{h.excerpt}`")
        out.append("")
    return "\n".join(out)


# --- cli --------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser(description="Flag LLM speech patterns in text/pptx.")
    ap.add_argument("source", nargs="?", help="file (.txt/.md/.pptx) or - for stdin")
    ap.add_argument("--text", help="inline text instead of a file")
    ap.add_argument("--patterns", default=str(Path(__file__).parent / "patterns.yaml"))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    text = read_text(args.source, args.text)
    patterns = load_patterns(Path(args.patterns))
    hits = scan_patterns(text, patterns) + scan_structural(text)
    word_count = len(text.split())

    if args.json:
        import json

        print(
            json.dumps(
                {
                    "score": round(score(hits, word_count), 1),
                    "word_count": word_count,
                    "hits": [h.__dict__ for h in hits],
                },
                indent=2,
            )
        )
    else:
        print(render(hits, word_count))


if __name__ == "__main__":
    main()
