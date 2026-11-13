---
name: house-style
description: The house visual style, Strata. Use before creating styled HTML, infographics, diagrams, charts, slides, visual reports, or app prototypes unless another style is requested. Also covers Strata exports for Python charts, terminals, Streamlit, and SwiftUI.
---

# House Style: Strata

Strata is the house style. `tokens/tokens.json` defines its colors, typography, spacing, and semantic roles.
Use those tokens rather than a palette copied from the website or an earlier artifact.

## Choose the surface

- **Lab / Operate:** local analysis, decks, and tools. Optimize for scanning. Save working artifacts in `lab/`. No decorative illustration.
- **Publication / Read:** public notes and explainers. Use natural scrolling and calm prose. A ridgeline motif may appear once.
- **Publication / Experience:** interactive public work. Let the artifact lead; keep controls quiet.

Local artifacts are not publishable by default. Build for a public site only when requested.

## Construct the artifact

1. Load `visualization` for charts, diagrams, and visual explanations. Choose the relationship before the composition.
2. Prefer `scripts/render_deck.py` when its supported forms fit. Inspect its schema before writing YAML.
3. For approved standalone HTML, start from `assets/template.html`. Keep the shared token block.
4. Read `references/diagrams.md` for diagrams and infographics. Also read `references/mermaid.md` before writing Mermaid.
5. If the renderer cannot express the relationship, explain the gap and ask before extending it or changing rendering paths.

The renderer supports text schematics and dot plots, not arbitrary graphical diagrams.
Its YAML format remains unchanged. Dot plots use one data series, colored with `series-2`.
They do not infer a focal category from the largest value. Direct labels expose every value.

## Visual rules

- **Layers, not shadows:** `ground`, `surface`, then `raised`. Shadows belong only to floating controls.
- **One editorial emphasis:** orange `sun` identifies one emphasis per page or slide. A data series may use `series-2` across all marks.
- **Action blue:** `action` is for interaction, not decorative labels or data marks.
- **Semantic status:** use `ok`, `warn`, or `fail` with a visible word or shape. Color alone is insufficient.
- **Type:** Avenir Next, then Figtree and system sans for prose. DM Mono for code, labels, captions, and measures.
- **Headings:** weight 500 to 600. Use available width without forced line breaks or character-count limits.
- **Prose:** 17px with at least 1.65 line height. Limit prose to `measure`; charts may use wider space.
- **Space before boxes:** neutral ground and generous spacing. Cards are for comparison or controls, never generic page scaffolding.
- **Evidence:** direct labels, units, sources, and clear limitations. Supply readable values alongside chart marks.
- **Restraint:** no decorative borders, gradients, nested cards, or metric-tile grids. No emoji. Control icons need text labels.
- **Responsive layout:** wide content scrolls inside its container, never the page. Reflow rather than shrinking labels.
- **Copy:** short sentences. Titles state supported findings. Mark fictional data and proposed models explicitly.

## Themes and tokens

`night` is the reference theme, using the approved Hood-inspired backgrounds:
ground #161619, surface #19191D, and raised #222226. Softer neutral text and muted
blue actions replace the earlier Charcoal palette; this is not a third theme. `paper` supports light surfaces, documents, and print-oriented artifacts.
Both themes must remain readable.

- `data-theme="night"` and `data-theme="dark"` select night.
- `data-theme="paper"` and `data-theme="light"` select paper.
- Without an explicit theme, the system light preference selects paper; otherwise night applies.
- Use `ink`, `ink-muted`, and `ink-faint` for text. Use `line-strong` for meaningful connectors and axes.
- Use `sun` for editorial emphasis, `series-2` for the focus data series, and `series-context` for context.
- For categorical charts, use the six `series-*` tokens. Split or filter before exceeding six categories.
- Pair category colors with labels or shapes. Do not imply causal or quantitative meaning through decoration.

## Supporting files

| Need | File |
|---|---|
| Authoritative tokens | `tokens/tokens.json` |
| Resolved theme colors | `tokens/resolved.json` |
| Standalone CSS and template | `assets/tokens.css`, `assets/template.html` |
| CSS with local font files | `assets/fonts/strata.css` |
| Python chart styling | `viz/strata_viz.py`, `viz/*.mplstyle` |
| SwiftUI | `swift/Strata.swift` |
| Streamlit | `streamlit/night/config.toml`, `streamlit/paper/config.toml` |
| Terminal themes | `terminal/strata-night.ghostty`, `terminal/strata-paper.ghostty` |
| Publication motifs | `assets/svg/` |

Hood is Strata's Obsidian adapter over pinned Atom. Its self-contained CSS maps
these tokens into Obsidian roles. Night uses surface for the editor and ground for
the sidebar; Paper keeps its existing mapping. Hood owns editor behavior, 1.7 line height,
mobile geometry, and the optional cursor. Hood lives in the eww repo at `obsidian/plugins/hood/`.
`make themes` writes its palette from these tokens, and `eww install` copies it into the vault.

Standalone renderer output embeds token CSS and uses local font fallbacks. It does not fetch fonts.
The bundled font CSS requires its adjacent font files; do not paste its relative URLs into standalone output.

## Render

Run the renderer belonging to the skill being used. For deployed settings:

```sh
renderer="$HOME/.claude/skills/house-style/scripts/render_deck.py"
uv run --quiet --script "$renderer" lab/<name>.yaml
```

Use `--force` only to replace a deliberately regenerated artifact.
If uv or the renderer is unavailable, report the blocker rather than silently hand-writing a replacement.

## Change the style

Edit `tokens/tokens.json`, then run `make themes` in the eww repo. It rewrites every export.
Do not edit an export by hand. `make test` fails when an export differs from the tokens.
The renderer reads `assets/tokens.css` at render time; it has no independent palette.
Keep the template token block and font CSS token block identical to the shared CSS.

## Verify

Inspect actual output at desktop and phone widths in night and paper themes.
Check contrast, focus, selection, overflow, labels, and reading order.
Check print and interaction states when relevant. Honor reduced motion if motion is added.
Use a bounded review: inspect, fix findings together, then confirm.
Report unavailable browser checks as unverified. Rendering alone is not visual validation.
