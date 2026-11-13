#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Render a validated learning artifact from YAML as standalone HTML."""

from __future__ import annotations

import argparse
import html
import math
from pathlib import Path
from typing import Any

import yaml

VALID_KINDS = {"prose", "comparison", "table", "diagram", "decision", "custom", "chart"}
FORMAT_SLIDE_RANGES = {
    "brief": (1, 1),
    "path": (3, 7),
    "worked-example": (3, 6),
    "comparison": (1, 3),
    "reference": (2, 5),
}
def load_token_css() -> str:
    """Load shared Strata tokens for embedding in a standalone artifact."""
    return (Path(__file__).resolve().parents[1] / "assets" / "tokens.css").read_text(encoding="utf-8")


SHELL_CSS = """
*{box-sizing:border-box}::selection{background:var(--action-soft);color:var(--ink)}html{background:var(--ground)}body{margin:0;color:var(--ink);background:var(--ground);font-family:var(--font-sans);font-size:17px;line-height:1.65}.deck{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}.nav{position:sticky;top:0;height:100vh;padding:32px 20px;border-right:1px solid var(--line)}.nav h1{font-size:16px;font-weight:500;line-height:1.3;margin:0 0 30px}.nav ol{list-style:none;padding:0;margin:0}.nav a{display:flex;align-items:center;gap:10px;min-height:44px;padding:6px 8px;color:var(--ink-muted);text-decoration:none;line-height:1.25;border-radius:4px}.nav a:focus-visible,.nav a:hover{outline:2px solid var(--action);outline-offset:2px}.nav a.active{color:var(--ink);background:var(--wash)}.number{font-family:var(--font-mono);font-size:12px;color:var(--action);font-variant-numeric:tabular-nums}.slides{min-width:0}.slide{display:none;max-width:980px;padding:72px var(--gutter) 100px}@media screen{[hidden]{display:none!important}}.slide:target{display:block}.slide:first-child:not(:target){display:block}.slide-label{font:12px/1.3 var(--font-mono);color:var(--ink-muted);letter-spacing:.08em;text-transform:uppercase;margin:0 0 18px}.slide h2{font-size:clamp(32px,5vw,58px);font-weight:500;letter-spacing:-.03em;line-height:1.04;max-width:100%;overflow-wrap:break-word;margin:0 0 22px}.takeaway{font-size:21px;line-height:1.45;color:var(--ink-muted);max-width:38em;margin:0 0 42px}.content{max-width:var(--measure)}p{margin:0 0 18px}.note{font-size:14px;color:var(--ink-faint);margin-top:42px}.columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;max-width:760px}.columns section{padding:18px 0;border-top:1px solid var(--line)}.columns h3{font:500 13px/1.3 var(--font-mono);color:var(--ink-muted);margin:0 0 12px}.columns ul{margin:0;padding-left:20px}.table-wrap{overflow-x:auto;max-width:900px}table{border-collapse:collapse;width:100%;font-size:15px}th,td{text-align:left;vertical-align:top;padding:12px 14px;border-bottom:1px solid var(--line)}th{font:500 12px/1.3 var(--font-mono);color:var(--ink-muted)}pre{overflow-x:auto;padding:20px;background:var(--wash);font:14px/1.55 var(--font-mono);white-space:pre-wrap}.decision{background:var(--wash);padding:20px}.decision h3{font:500 13px/1.3 var(--font-mono);color:var(--ink-muted);margin:0 0 10px}.decision p{margin-bottom:12px}@media(max-width:720px){.deck{display:block}.nav{z-index:1;display:flex;align-items:center;gap:14px;height:auto;padding:10px var(--gutter);border-right:0;border-bottom:1px solid var(--line);overflow-x:auto;white-space:nowrap}.nav h1{flex:0 0 auto;font-size:13px;margin:0}.nav ol{display:flex;gap:4px}.nav a{gap:6px;min-height:44px;padding:6px}.slide{padding-top:48px}.columns{grid-template-columns:1fr}.slide h2{max-width:100%}}@media print{.deck{display:block}.nav{display:none}.slide,.slide:first-child:not(:target){display:block;page-break-after:always;padding:36px}.slide h2{font-size:34px}}
"""
SHELL_CSS += """
.dot-chart{margin:0}.dot-chart figcaption{color:var(--ink-muted);font-size:15px;margin-bottom:20px}.dot-chart ol{list-style:none;padding:0;margin:0}.dot-row,.dot-axis{display:grid;grid-template-columns:minmax(0,102px) minmax(0,1fr) 51px;gap:12px;align-items:center}.dot-row{min-height:48px}.dot-label{overflow-wrap:anywhere;line-height:1.3}.dot-track{padding:0 6px;min-width:0}.dot-track svg{display:block;width:100%;height:32px;overflow:visible}.dot-track circle{fill:var(--series-2)}.dot-value{font-family:var(--font-mono);font-variant-numeric:tabular-nums;text-align:right;overflow-wrap:anywhere}.dot-axis{color:var(--ink-muted);font:13px var(--font-mono);margin-top:12px}.dot-axis-scale{display:flex;justify-content:space-between;border-top:1px solid var(--ink-muted);padding-top:6px}.dot-source{font-size:14px;color:var(--ink-muted);margin-top:24px}
"""
SCRIPT = """
const slides=[...document.querySelectorAll('.slide')];
const links=[...document.querySelectorAll('.nav a')];
function current(){return Number(location.hash.slice(1))||1}
function centerNav(){const active=links[current()-1],nav=document.querySelector('.nav');if(!active||!nav||nav.scrollWidth<=nav.clientWidth+1)return;const a=active.getBoundingClientRect(),c=nav.getBoundingClientRect();nav.scrollLeft+=a.left-c.left-(c.width-a.width)/2}
function update(){const n=current();slides.forEach((slide,i)=>slide.hidden=i+1!==n);links.forEach((link,i)=>link.classList.toggle('active',i+1===n));requestAnimationFrame(centerNav)}
window.addEventListener('hashchange',update);window.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight'].includes(event.key)||event.target.matches('input,textarea'))return;const n=current()+ (event.key==='ArrowRight'?1:-1);if(n>=1&&n<=slides.length)location.hash='#'+n});if(!location.hash)location.hash='#1';update();
"""


def fail(message: str) -> None:
    raise ValueError(message)


def text(value: Any) -> str:
    if not isinstance(value, str):
        fail("deck text values must be strings")
    return html.escape(value)


def string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        fail(f"{field} must be a list of strings")
    return value


def validate_deck(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        fail("deck YAML must contain a mapping")
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        fail("artifact title is required")
    artifact_format = data.get("format", "path")
    if not isinstance(artifact_format, str) or artifact_format not in FORMAT_SLIDE_RANGES:
        fail(f"format must be one of {', '.join(FORMAT_SLIDE_RANGES)}")
    slides = data.get("slides")
    minimum, maximum = FORMAT_SLIDE_RANGES[artifact_format]
    if not isinstance(slides, list) or not minimum <= len(slides) <= maximum:
        fail(f"{artifact_format} format requires {minimum} to {maximum} slides")
    for index, slide in enumerate(slides, start=1):
        if not isinstance(slide, dict):
            fail(f"slide {index} must be a mapping")
        for field in ("label", "title", "takeaway", "kind"):
            if not isinstance(slide.get(field), str) or not slide[field].strip():
                fail(f"slide {index}: {field} is required")
        if slide["kind"] not in VALID_KINDS:
            fail(f"slide {index}: unknown kind {slide['kind']!r}")
    data["format"] = artifact_format
    return data


def render_prose(slide: dict[str, Any]) -> str:
    return "".join(f"<p>{text(item)}</p>" for item in string_list(slide.get("body", []), "body"))


def render_comparison(slide: dict[str, Any]) -> str:
    columns = slide.get("columns")
    if not isinstance(columns, list) or not columns:
        fail("comparison slide requires columns")
    output = []
    for column in columns:
        if not isinstance(column, dict) or not isinstance(column.get("heading"), str):
            fail("comparison columns require a heading")
        items = string_list(column.get("items", []), "comparison items")
        output.append(f"<section><h3>{text(column['heading'])}</h3><ul>{''.join(f'<li>{text(item)}</li>' for item in items)}</ul></section>")
    return f"<div class=\"columns\">{''.join(output)}</div>"


def render_table(slide: dict[str, Any]) -> str:
    headers = string_list(slide.get("headers", []), "table headers")
    rows = slide.get("rows")
    if not headers or not isinstance(rows, list):
        fail("table slide requires headers and rows")
    rendered_rows = []
    for row in rows:
        values = string_list(row, "table row")
        if len(values) != len(headers):
            fail("each table row must match the header count")
        rendered_rows.append("<tr>" + "".join(f"<td>{text(value)}</td>" for value in values) + "</tr>")
    return "<div class=\"table-wrap\"><table><thead><tr>" + "".join(f"<th>{text(header)}</th>" for header in headers) + "</tr></thead><tbody>" + "".join(rendered_rows) + "</tbody></table></div>"


def render_diagram(slide: dict[str, Any]) -> str:
    diagram = slide.get("diagram")
    if not isinstance(diagram, str) or not diagram.strip():
        fail("diagram slide requires diagram text")
    return f"<pre>{text(diagram)}</pre>"


def validate_chart(chart: Any) -> dict[str, Any]:
    """Validate the bounded, nonnegative dot-plot contract without mutation."""
    if not isinstance(chart, dict):
        fail("chart must be a mapping")
    if set(chart) - {"type", "unit", "period", "source", "sort", "data"}:
        fail("unknown chart field")
    if chart.get("type") != "dot":
        fail("chart type must be dot")
    for field in ("unit", "period", "source"):
        if not isinstance(chart.get(field), str) or not chart[field].strip():
            fail(f"chart {field} is required")
    if chart.get("sort", "descending") not in ("ascending", "descending", "input"):
        fail("chart sort must be ascending, descending, or input")
    rows = chart.get("data")
    if not isinstance(rows, list) or not rows:
        fail("chart data must be a nonempty list")
    labels = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"label", "value"}:
            fail("chart rows require only label and value")
        label = row["label"]
        if not isinstance(label, str) or not label.strip():
            fail("chart labels must be nonempty strings")
        if label.strip() in labels:
            fail("chart labels must be unique")
        labels.add(label.strip())
        value = row["value"]
        try:
            valid = type(value) in (int, float) and math.isfinite(value) and value >= 0
        except OverflowError:
            valid = False
        if not valid:
            fail("dot values must be finite nonnegative numbers")
    return chart


def render_chart(slide: dict[str, Any]) -> str:
    """Render responsive SVG marks with directly labeled, accessible values."""
    chart = validate_chart(slide.get("chart"))
    rows = list(chart["data"])
    order = chart.get("sort", "descending")
    if order != "input":
        rows.sort(key=lambda row: row["value"], reverse=order == "descending")
    maximum = max(row["value"] for row in rows) or 1
    marks = []
    for row in rows:
        position = row["value"] / maximum * 100
        value = str(row["value"])
        marks.append(
            f'<li class="dot-row"><span class="dot-label">{text(row["label"])}</span>'
            f'<span class="dot-track"><svg aria-hidden="true" focusable="false" '
            f'xmlns="http://www.w3.org/2000/svg"><circle cx="{position:.6f}%" cy="16" r="5"/></svg></span>'
            f'<span class="dot-value">{text(value)}</span></li>'
        )
    return (
        f'<figure class="dot-chart"><figcaption>{text(chart["unit"])} · {text(chart["period"])}</figcaption>'
        f'<ol>{"".join(marks)}</ol><div class="dot-axis" aria-hidden="true"><span></span>'
        f'<div class="dot-track"><div class="dot-axis-scale"><span>0</span><span>{text(str(maximum))}</span></div></div>'
        f'<span></span></div><p class="dot-source">Source: {text(chart["source"])}</p></figure>'
    )


def render_decision(slide: dict[str, Any]) -> str:
    choice = slide.get("choice")
    why = slide.get("why")
    if not isinstance(choice, str) or not isinstance(why, str):
        fail("decision slide requires choice and why")
    return f"<div class=\"decision\"><h3>Choice</h3><p>{text(choice)}</p><h3>Why</h3><p>{text(why)}</p></div>"


def render_custom(slide: dict[str, Any]) -> str:
    markup = slide.get("html")
    if not isinstance(markup, str) or not markup.strip():
        fail("custom slide requires html")
    return markup


def render_content(slide: dict[str, Any]) -> str:
    renderers = {
        "prose": render_prose,
        "comparison": render_comparison,
        "table": render_table,
        "diagram": render_diagram,
        "decision": render_decision,
        "custom": render_custom,
        "chart": render_chart,
    }
    return renderers[slide["kind"]](slide)


def render_slide(index: int, slide: dict[str, Any]) -> str:
    try:
        note = f'<p class="note">{text(slide["note"])}</p>' if isinstance(slide.get("note"), str) else ""
        return f'<article class="slide" id="{index}"><p class="slide-label">{index:02} / {text(slide["label"])}</p><h2>{text(slide["title"])}</h2><p class="takeaway">{text(slide["takeaway"])}</p><div class="content">{render_content(slide)}</div>{note}</article>'
    except ValueError as error:
        fail(f"slide {index}: {error}")
        raise  # unreachable; fail always raises


def render_deck(deck: dict[str, Any]) -> str:
    slides = deck["slides"]
    navigation = "".join(
        f'<li><a href="#{index}"><span class="number">{index:02}</span><span>{text(slide["label"])}</span></a></li>'
        for index, slide in enumerate(slides, start=1)
    )
    pages = "".join(render_slide(index, slide) for index, slide in enumerate(slides, start=1))
    return f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{text(deck['title'])}</title><style>{load_token_css()}{SHELL_CSS}</style></head><body><main class=\"deck\"><nav class=\"nav\" aria-label=\"Deck navigation\"><h1>{text(deck['title'])}</h1><ol>{navigation}</ol></nav><section class=\"slides\">{pages}</section></main><script>{SCRIPT}</script></body></html>\n"


def output_path(source: Path) -> Path:
    return source.with_suffix(".html")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--force", action="store_true", help="overwrite an existing HTML deck")
    args = parser.parse_args()
    try:
        data = validate_deck(yaml.safe_load(args.source.read_text(encoding="utf-8")))
        destination = output_path(args.source)
        if destination.exists() and not args.force:
            fail(f"output exists: {destination} (use --force to overwrite)")
        destination.write_text(render_deck(data), encoding="utf-8")
    except (OSError, ValueError, yaml.YAMLError) as error:
        parser.error(str(error))
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
