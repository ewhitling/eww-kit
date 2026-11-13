# Strata diagrams and infographics

Load `visualization` to choose the form and preserve its meaning.
Use the tokens in `../tokens/tokens.json`; appearance does not establish evidence.

## Color and type

- Use `ground` or `surface` behind diagrams.
- Use `ink` for labels and `ink-muted` for secondary context.
- Use `line-strong` for meaningful connectors and axes.
- Use `sun` for one editorial focal path or element, not interaction.
- Use `action` for controls and links.
- Use `series-2` for a focal data series and `series-context` for other data.
- Use Avenir Next with the shared sans fallback for prose and node labels.
- Use DM Mono for measures, captions, and machine labels.

## Composition

Each arrow needs a clear meaning. Direct labels are preferred to legends.
Keep nodes short. Use space before borders and borders before containers.
Avoid decorative gridlines, icons, gradients, and shadows.
Use 1px structural strokes and 2px data lines where needed.
Charts and tables stay flat. Nodes may use the shared small radius.

Infographics use a single column with generous section spacing.
On phones, reflow or split diagrams rather than shrinking labels.
Wide content scrolls in its own container, never the whole page.

## Evidence

State units, source, time window, and limitations.
Expose readable values beside marks or in a table.
Use labels or shapes alongside color. Do not invent a focal category from rank.
Check night and paper themes at desktop and mobile widths.

## Mermaid

Read `mermaid.md` for CSS mapping and markdown guidance.
A graphical library integration still requires approval when the renderer lacks it.
