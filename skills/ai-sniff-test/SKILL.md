---
name: ai-sniff-test
description: Detect common LLM speech patterns in text, markdown, or presentations (.pptx). Use when the user wants to check whether writing reads as AI-generated, audit a deck or doc for "AI slop", flag buzzwords and template phrasing, or clean up LLM tells before publishing. Triggers on phrases like "does this sound like AI", "sniff test", "check for AI patterns", "AI slop", or pasting a deck/doc to audit.
---

# AI Sniff Test

Flags the speech patterns that mark text as LLM-generated, so they can be cut before publishing. Built for presentations and docs.

## Two layers, by design

1. **Deterministic** (`detect.py`): regex + structural detectors. Trust the `high` confidence hits.
2. **Rhetorical review** (you): the script flags `heuristic` hits with a signature but cannot read meaning. You judge those, plus the patterns regex misses.

Do not claim the script "detects AI". It detects *tells*. A high score means many tells, not proof of authorship.

## Run it

The script declares its own dependencies in an inline `# /// script` block.
`uv run --script` reads that block and installs them in an isolated environment, so
no project setup is needed. The script finds `patterns.yaml` beside itself.

```bash
detect="$HOME/.claude/skills/ai-sniff-test/detect.py"
uv run --quiet --script "$detect" path/to/file.md   # text or markdown
uv run --quiet --script "$detect" --text "paste here"
uv run --quiet --script "$detect" - < file          # stdin
uv run --quiet --script "$detect" file.md --json    # machine output
uv run --quiet --script "$detect" deck.pptx         # presentations
```

## Workflow

1. Run `detect.py` on the input. Report the score and the high-confidence hits as-is.
2. Triage the `_(review)_` heuristic hits. Confirm or dismiss each with a one-line reason. Common real offenders: value-prop conclusions ("you ship faster"), false profundity ("the power of X"), manufactured contrast.
3. Add a short manual pass for tells regex cannot catch:
   - **Rule of three everywhere** (every list is exactly three items).
   - **Antithesis scaffolding** (every point built as "not X, but Y").
   - **Hollow parallelism** (bullets engineered to the same rhythm/length).
   - **Conclusion inflation** (a modest feature framed as transformative).
   - **Symmetric paragraph openings** (each para starts the same shape).
4. Give a verdict and, only if asked, a rewritten version that keeps the content and drops the tells.

## The core deck formula to catch

The "N objects, aligned in your workspace, you ship faster" shape:

```
[noun phrase] -> [vague value prop] -> [overstated outcome]
```

This is three tells stacked: parallel fragment, hollow benefit, inflated conclusion. The structural detector catches the parallel fragments; the rhetorical regex catches the value-prop verb; you confirm the inflation.

## Editing the pattern library

`patterns.yaml` is MECE by category (lexical / syntactic / rhetorical / sycophancy). Add a plain string for a literal word, or a `{label, regex, weight, confidence}` dict for anything fancier. Keep regexes simple so non-programmers can edit them.
