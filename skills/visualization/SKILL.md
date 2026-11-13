---
name: visualization
description: Choose and validate a visual representation for an explanation, analysis, or decision. Use for charts, systems diagrams, stocks and flows, processes, flowcharts, clustering, comparisons, maps, uncertainty, or requests to explain visually. Owns visual meaning and form selection; house-style owns appearance.
---

# Show the relationship the reader needs to understand

Choose a visual by the question it answers, not by its novelty. Prefer a labeled visual over paragraphs when spatial relationships reduce reading effort. Keep prose when a visual would only put sentences inside boxes.

## Boundaries

- This skill owns form selection, visual meaning, and evidence checks.
- Load `house-style` for palette, typography, layout, and accessible presentation. Do not duplicate its tokens here.
- `explain` owns learning sequence and its YAML output contract. This skill does not add renderer capabilities or override that contract.
- Use the current project's rendering tools. Inspect their supported schema before writing source. Do not invent fields or silently switch renderers.
- A selection-only request needs a recommendation, not generated files.

## Before constructing a visual

Write a short visual brief in working notes or the response, not a new required file format:

1. **Question:** What should the reader understand or decide?
2. **Evidence:** Which data, source, or explicitly proposed model supports it? Name units and missing inputs.
3. **Relationship:** Comparison, sequence, connection, accumulation, distribution, or another relationship below.
4. **Form and meaning:** What do position, size, color, grouping, and connectors encode? State unused channels when ambiguity matters.
5. **Takeaway and limitation:** What can the reader conclude, and what remains unsupported?

This is a reasoning checklist, not a renderer schema. Keep it brief for simple figures. Follow the user's approval gates when the model or representation is contested.

## Choose by question

| Reader's question | Useful forms | Selection rule |
|---|---|---|
| What connects to what? | Systems diagram, network, dependency graph | Name the connection type. Use a matrix when edges become unreadable. |
| What accumulates or moves? | Stock-and-flow diagram, Sankey | Stocks accumulate; flows change stocks per unit time. Sankey widths require measured quantities. |
| What changes over time? | Line chart, slope chart, timeline | Lines show quantitative change; timelines show events. Slope charts suit two time points. |
| What happens next? | Process diagram, flowchart | Use a process for a sequence and a flowchart for conditional branches. Label branch conditions. |
| Who acts, or what state changes? | Swimlanes, sequence diagram, state-transition diagram | Lanes show responsibility; sequences show messages; transitions show valid state changes. |
| How do groups compare or rank? | Dot plot, bars, small multiples | Prefer aligned positions for precise comparison. Sort when order is not intrinsic. |
| How do values vary within groups? | Strip plot, histogram, box plot | Show observations when feasible. Summaries can hide sample size and multiple peaks. |
| What varies together? | Scatterplot, heatmap | Show association, not causation. Define heatmap cells and color scale. |
| What groups emerge? | Similarity matrix, dendrogram, cluster projection | Name features, distance, and method. A two-dimensional projection can distort separation. |
| What contains what? | Tree, nested groups, treemap | Trees show hierarchy; treemap areas require a meaningful quantity. |
| What makes up the whole? | Stacked bars, part-to-whole bars | State the denominator. Use separate aligned plots when precise component comparison matters. |
| What contributes to a change? | Waterfall, contribution bars | Waterfalls require additive contributions that reconcile to the total change. |
| Where does it happen? | Map, spatial layout | Use geography only when location matters. Distinguish counts from rates. |
| What might cause what? | Causal graph, causal-loop diagram | Mark hypotheses. Feedback loops require a cyclic form, not a causal DAG. |
| How uncertain is it? | Interval plot, distribution, scenario bands | Name the interval or scenario meaning. Scenarios are not probabilities without a model. |
| How does a mechanism work? | Annotated schematic, before-and-after, worked visual example | Show the changing part and what stays fixed. Mark illustrative values as illustrative. |

These are starting points, not an exhaustive catalog. Combine forms only when each answers a distinct part of the question.

## Preserve meaning

### Diagrams

- Give each arrow a consistent meaning: sequence, dependency, influence, message, or material flow. Label mixed edge types explicitly.
- Separate stocks from rates. A stock uses units such as people; a flow uses people per day.
- For measured stocks and flows, check initial stock plus inflows minus outflows against final stock over the same period.
- For causal loops, label influence polarity and delays where known. Positive and negative mean direction of influence, not good and bad.
- Mark proposed architecture or causal structure as proposed. A tidy diagram is not evidence that its relationships exist.
- Use position to show sequence, grouping, or containment deliberately. Do not imply measured distance through arbitrary layout.
- Split a dense diagram by reader question, not arbitrary node count. Preserve cross-links and conditions when simplifying.

### Quantitative charts

- Name units, population, time window, source, transformations, and denominators where relevant.
- Bars encoding magnitude start at zero. A cropped line-chart axis must be explicit and must not exaggerate the claim.
- Use consistent scales across comparable small multiples, or clearly mark differences. Prefer separate panels over dual axes.
- Keep missing values distinct from zero. Do not connect across missing periods without making the gap explicit.
- Label logarithmic scales. Encode quantities by area, not radius, when using sized circles.
- Avoid decorative 3D, smoothing that invents a trend, and color categories unsupported by the evidence.
- Show sample sizes and uncertainty when they change the interpretation. Distinguish spread among observations from uncertainty in an estimate.
- Do not infer causality from correlation, or real clusters from a visually separated projection alone.

## Compose for comprehension

- Let the title state the supported finding. Label an unresolved question as a question.
- Make the relevant relationship visible before adding explanatory prose. Use captions for interpretation, not a second description of every mark.
- Prefer direct labels. Use color for emphasis, not as the only way to distinguish groups.
- Use small multiples, line styles, and grouping before adding more colors. Follow the house-style color budget.
- A table is valid when exact lookup matters more than a pattern. Prose is valid when there is no useful spatial relationship.
- On narrow screens, reflow or split rather than shrinking labels. Read house-style's Mermaid reference before writing Mermaid.
- Provide a short text equivalent stating the relationship and takeaway. Essential information must not require hover or color vision.

## Validate

1. **Evidence:** Reconcile plotted values with sources and calculations. Verify totals, units, denominators, and missingness.
2. **Meaning:** Read every arrow and visual channel as a claim. Remove unsupported implications of causality, precision, or distance.
3. **Comprehension:** Can the reader answer the brief's question without reading a surrounding essay? Does the visual reduce effort?
4. **Rendering:** Inspect the actual output at desktop and phone widths, in both supported themes. Check clipping, labels, contrast, and reading order.
5. **Report:** State the chosen form, why it fits, and any unverified evidence or rendering checks. Do not claim visual inspection from source review alone.

If the best form is unsupported by the renderer, name the gap. Offer an honest supported alternative or ask before extending the renderer.

## Decision record

A shared visualization skill separates visual meaning from house-style appearance and explain's learning sequence. No visual quota is imposed. Renderer expansion requires a separate decision.
