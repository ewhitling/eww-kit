# Mermaid in house style

Two lanes, two recipes. The structure was validated against Mermaid v11 before the Strata migration.
The Strata token mapping still needs a browser check in both themes.

**Artifact / HTML page lane:** CSS token overrides. The only route that
follows the theme toggle. Use it whenever the page carries the house
token block.

**Plain markdown lane** (GitHub, Obsidian, any renderer where page CSS
can't reach): a `%%{init}%%` directive with dark hexes baked in. It is
single-theme by nature: it looks house-dark everywhere, including on a
light ground. Acceptable for working diagrams; if the host renders
light-only, skip the directive and take the renderer's default.

When to redraw as hand-authored SVG instead: when the diagram is the
centerpiece of a finished infographic, or needs exact layout control.
Mermaid with the recipe is fine for structural diagrams inside a page.

## Orientation: design vertical first

Diagrams headed for a note store (Obsidian, anything read on a
phone) render in a narrow column that scrolls vertically. A `flowchart
LR` gets shrunk to fit the column width and the labels become
unreadable; a `flowchart TD` just gets taller, which scrolling handles.

- Default to `flowchart TD` for any diagram destined for a note or
  phone reading. Height is free; width is not.
- `LR` is reserved for wide desktop surfaces (artifacts, HTML pages)
  where the diagram earns the horizontal room.
- Keep the diagram at most ~2 nodes wide. Parallel branches beyond
  that get width back; restructure as sequential stages or split into
  two diagrams.
- Sequence diagrams grow horizontally with each actor. On a phone
  surface, cap at 3 actors or redraw as a TD flowchart.
- Node labels: 1-3 words. Long labels widen the whole column in TD.

## Lane 1: artifacts and HTML pages

Wrap each diagram in a `.mermaid-house` container (keep an unwrapped
diagram unstyled on purpose, e.g. in a comparison):

```html
<div class="diagram-box mermaid-house">
  <pre class="mermaid">
flowchart LR
  A[Capture] --> B[Daily briefing]:::focal
  classDef focal stroke-width:2px
  </pre>
</div>
```

Then include this CSS. Every rule needs `!important`: mermaid injects
its own scoped style block plus inline styles, and both beat plain
author CSS. The focal rule must stay declared after the base node rule;
it wins their `!important` tie by source order.

```css
/* fonts */
.mermaid-house svg,
.mermaid-house svg text,
.mermaid-house .nodeLabel,
.mermaid-house .edgeLabel {
  font-family: var(--font-sans) !important;
}

/* flowchart nodes */
.mermaid-house .node rect,
.mermaid-house .node circle,
.mermaid-house .node ellipse,
.mermaid-house .node polygon,
.mermaid-house .node path {
  fill: var(--surface) !important;
  stroke: var(--line-strong) !important;
  stroke-width: 1px !important;
}
.mermaid-house .nodeLabel,
.mermaid-house .label,
.mermaid-house .label text,
.mermaid-house .node .label span {
  color: var(--ink) !important;
  fill: var(--ink) !important;
}

/* flowchart edges + arrowheads */
.mermaid-house .edgePath .path,
.mermaid-house .flowchart-link {
  stroke: var(--line-strong) !important;
  stroke-width: 1px !important;
}
.mermaid-house .marker,
.mermaid-house .marker path {
  fill: var(--line-strong) !important;
  stroke: var(--line-strong) !important;
}
.mermaid-house .edgeLabel,
.mermaid-house .edgeLabel span {
  color: var(--ink-muted) !important;
  background-color: var(--surface) !important;
}
.mermaid-house .edgeLabel rect,
.mermaid-house .edgeLabel .labelBkg {
  fill: var(--surface) !important;
  opacity: 1 !important;
}
/* mermaid v11 paints the visible edge-label box on an inner <p>
   and a .labelBkg div, with hardcoded rgba grey */
.mermaid-house .edgeLabel p,
.mermaid-house .labelBkg {
  background-color: var(--surface) !important;
  color: var(--ink-muted) !important;
}

/* subgraph clusters */
.mermaid-house .cluster rect {
  fill: var(--wash) !important;
  stroke: var(--line) !important;
}
.mermaid-house .cluster-label span,
.mermaid-house .cluster-label text {
  color: var(--ink-muted) !important;
  fill: var(--ink-muted) !important;
}

/* focal accent: nodes tagged :::focal in the diagram source.
   Keep declared after the base node rule (source-order tie-break). */
.mermaid-house .node.focal rect,
.mermaid-house .focal rect {
  stroke: var(--sun) !important;
  stroke-width: 1.5px !important;
}

/* sequence diagrams */
.mermaid-house .actor {
  fill: var(--surface) !important;
  stroke: var(--line-strong) !important;
}
.mermaid-house text.actor,
.mermaid-house text.actor > tspan {
  fill: var(--ink) !important;
  stroke: none !important;
}
.mermaid-house .actor-line {
  stroke: var(--line) !important;
}
.mermaid-house .messageLine0,
.mermaid-house .messageLine1 {
  stroke: var(--line-strong) !important;
}
.mermaid-house .messageText {
  fill: var(--ink-muted) !important;
  stroke: none !important;
}
.mermaid-house .activation0,
.mermaid-house .activation1,
.mermaid-house .activation2 {
  fill: var(--wash) !important;
  stroke: var(--line-strong) !important;
}
.mermaid-house .note {
  fill: var(--wash) !important;
  stroke: var(--line) !important;
}
.mermaid-house .noteText,
.mermaid-house .noteText > tspan {
  fill: var(--ink-muted) !important;
}
.mermaid-house .loopLine {
  stroke: var(--line-strong) !important;
}
.mermaid-house .loopText,
.mermaid-house .loopText > tspan,
.mermaid-house .labelText,
.mermaid-house .labelText > tspan {
  fill: var(--ink-muted) !important;
}
.mermaid-house .labelBox {
  fill: var(--surface) !important;
  stroke: var(--line-strong) !important;
}
.mermaid-house #arrowhead path,
.mermaid-house .sequenceNumber {
  fill: var(--line-strong) !important;
}
```

The color mapping follows `references/diagrams.md`: surfaces for fills,
`--line-strong` for connectors (the token `--line` is too faint for
a 1px diagram stroke), `--sun` only on the focal element.

## Lane 2: plain markdown

Paste this directive as the first line of the fence. Hex values are the
dark tokens from `assets/tokens.css`; update together.

```
%%{init: {"theme": "base", "themeVariables": {
  "background": "#161619",
  "primaryColor": "#19191D",
  "primaryTextColor": "#D4D4D8",
  "primaryBorderColor": "#777780",
  "lineColor": "#777780",
  "secondaryColor": "#19191D",
  "tertiaryColor": "#19191D"
}}}%%
```

For the focal accent in this lane, put the color in the diagram source:
`classDef focal stroke:#F2894F,stroke-width:2px` plus `:::focal` on the
node.

## Gotchas (each one cost a debug round)

1. **Never set `fontFamily` in the directive.** Mermaid measures label
   width before the font applies; every label gets clipped.
2. **Edge labels hide their background** on an inner `<p>` and a
   `.labelBkg` div, not on the SVG rect. Both need the override.
3. **`!important` is not optional.** Without it, mermaid's injected
   styles and inline attributes win.
4. **Coverage is flowchart + sequence.** Other diagram types (state,
   gantt, ER) use different class sets. Check the rendered SVG classes
   and extend the block before trusting them.
