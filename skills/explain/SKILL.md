---
name: explain
description: Create a compact visual explanation of a response, selected discussion, or decision when visuals materially improve understanding. Choose the relationship and smallest useful format, then write YAML for the shared renderer.
---

# Explain it

Explain the selected response, discussion, or decision. Without an explicit selection, use the immediately preceding assistant response. Read relevant earlier turns for context.

When considering this skill proactively, prefer a short text answer if sufficient. Ask before creating artifact files unless already authorized. An explicit `/explain` request authorizes the standard artifact files.

Choose the smallest learning format that makes the point clear. A five-slide deck is not a default.

Prefer the shared renderer in the `house-style` skill for supported content. It owns the shell, navigation, responsive layout, and house-style tokens. Approved visual components may sit inside that shell. It does not determine which visual relationship the evidence needs. Write concise YAML when the supported contract fits; do not hand-write HTML or restyle the shell to bypass a limitation.

## Output contract

- Work in the current project. If no project is established, ask for an output directory before creating files. Do not assume the current directory is a project.
- Create two files in `lab/`, without overwriting either:
  - `lab/explain-<topic>.yaml`, the editable source.
  - `lab/explain-<topic>.html`, rendered from it.
- Use a clear kebab-case topic. If either file exists, add a meaningful suffix such as `-v2`.
- Create `lab/` when it does not exist.
- Report both paths, the chosen format, and one command to open the HTML locally.

## Arguments

- With no argument, explain the assistant response immediately before this skill.
- Plain text after `/explain` is steering for that explanation. It can set the audience, emphasis, depth, or question to answer.
- Use `discussion: <selection>` to explain a named discussion or decision across multiple turns. Preserve the relevant evidence, alternatives, and unresolved questions.
- Use `topic: <subject>` to explain a standalone topic. Read relevant session context and project files first. If the evidence is insufficient, say so and ask for the missing source rather than inventing content.
- Use `format: <name>` to select a learning format. This overrides the selection rule.
- Use `steer: <direction>` when the intent could otherwise be confused with a standalone topic.

Examples:

```text
/explain for a non-technical reader
/explain format: worked-example
/explain steer: focus on the mobile layout
/explain topic: Bayesian updating
```

## Before writing

1. Read the selected response, discussion, or decision and relevant session context.
2. Read `house-style` and `visualization`. This is a `lab / operate` surface. Keep the renderer-owned shell.
3. Inspect any referenced project files when they are available and relevant.
4. Separate observed facts from assumptions and proposals.
5. If essential evidence is unavailable, state that limitation in the artifact. Do not invent it.

## Choose the relationship before the format

Use `visualization` to identify the reader's question, supporting evidence, visual form, and the meaning of its marks.

- Prefer a labeled visual plus a short explanation when it makes a relationship easier to understand than paragraphs.
- For a mechanism, show the changing part. For a sequence, show order and conditions. For a comparison, align the differences.
- Let titles and takeaways interpret the visual rather than repeat every label.
- Keep prose for claims without a useful spatial relationship. A diagram made of paragraph-filled boxes is not an improvement.
- No visual quota applies. Each visual must answer: what becomes easier to understand because this is visual?
- Check the installed renderer's schema or examples before writing visual YAML. `kind: diagram` does not imply support for every diagram or chart form.
- If the best form is unsupported, state the gap. Offer a supported alternative only if it preserves the important relationship. Otherwise ask to use an appropriate component or another rendering path. Do not invent YAML fields, use raw `custom` HTML, or silently bypass the shell.
- The current `diagram` kind displays preformatted text, not graphical diagrams. Use it only when a text schematic is sufficient. A chart or diagram library requires an approved integration; its existence in a lab trial does not make it a supported renderer feature.
- Use a deck only when sequence or progressive disclosure improves understanding. A single-view explanation can use `brief`. If scrolling or another composition fits better, ask for that rendering path rather than splitting content merely to satisfy slide counts.

## Choose the learning format

Use this rule unless the user names a format:

- `brief`, one slide: one claim, decision, or result needs clarification.
- `path`, three to seven slides: the learner needs a sequence or progressive disclosure.
- `worked-example`, three to six slides: applying a method is the point.
- `comparison`, one to three slides: the learner must distinguish real alternatives.
- `reference`, two to five slides: the learner needs a concise definition, model, examples, and limits to revisit later.

State the selected format in the final response. Do not make a deck longer to fill space.

## YAML schema

Every source needs `title`, `format`, and `slides`. A slide needs `label`, `title`, `takeaway`, and `kind`. An optional `note` renders as the quiet source or limitation line.

`kind` is one of `prose`, `comparison`, `table`, `diagram`, `decision`, or `chart`. Do not use `custom`. Check the installed renderer's validation code or maintained examples for the current field contract before writing YAML. If none of these kinds can express the content, explain the limitation and ask before adding a renderer feature.

The current `chart` kind supports `chart.type: dot`. It requires `unit`, `period`, `source`, and nonempty `data` rows with unique `label` strings and finite nonnegative `value` numbers. Optional `sort` is `ascending`, `descending`, or `input`. Verify this against the installed renderer rather than assuming all chart types are supported.

```yaml
title: What the run showed
format: worked-example
slides:
  - label: Starting point
    title: Begin with the input.
    takeaway: Name what is known before reasoning from it.
    kind: prose
    body:
      - The observed input is X.
    note: Source or limitation, stated plainly.
```

Use `comparison` when two sets face off, `table` for real measures, and `decision` for a choice and its reason.

## Render

Render with the shared renderer. The `house-style` skill's "Renderer" section has the exact command and its fallback path for each harness:

```sh
uv run --quiet --script "$renderer" lab/explain-<topic>.yaml
```

Add `--force` only when deliberately replacing an artifact you just rendered.

## Writing

- Write with the economy and clarity associated with Hemingway.
- Prefer short, concrete sentences and active verbs.
- Lead with the point. Cut throat-clearing, filler, and self-reference.
- Use plain words. Avoid corporate language and vague intensifiers. Remove vague qualifiers; retain uncertainty supported by the evidence.
- Make each claim traceable to a named input, calculation, or explicitly marked assumption.
- Do not turn a proposal, pattern, or absence of evidence into a fact.
- State uncertainty plainly when the evidence cannot support a conclusion.
- Use fewer words when the artifact remains clear.

## Content and house style

The shell handles palette, type, navigation, and layout. These rules govern what you put inside it.

- Optimize for scanning, inspection, and a real decision.
- Do not add decorative eyebrows, generic metric tiles, nested cards, gradients, icons, or emoji.
- A `comparison` or `table` must compare, group, or measure something real. Neither is page scaffolding.
- Let the renderer control title wrapping. Do not force short, dramatic line breaks.
- Use direct labels and readable tables, and end a slide with a quiet source or limitation note where one helps.
- Give a slide a visual composition only when it clarifies the result.

## Quality check

Inspect the rendered HTML at a 1440x900 desktop viewport and a 390x844 vertical phone viewport. If browser inspection is unavailable, report visual checks as unverified. Do not claim that rendering alone verifies layout. Fix findings in one batch, then confirm once more. Verify:

- the format and slide count match the learning task
- navigation reaches each slide when the artifact has more than one slide
- the artifact reflects the selected response, discussion, or decision rather than generic filler
- claims distinguish evidence from assumptions
- the chosen visual answers the reader's question and reduces reading effort
- arrows, scales, units, and groupings match the evidence rather than imply unsupported relationships
- essential visual information has a short text equivalent and does not depend on hover or color alone
- the output paths are inside `lab/`
- no horizontal page overflow at either width

A defect in the shell itself belongs in `scripts/render_deck.py`, not worked around in one artifact's YAML. Say so when you find one.
