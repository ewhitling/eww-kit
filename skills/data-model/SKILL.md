---
name: data-model
description: Review or propose a data model as a five-slide deck, then materialize an explicitly approved Python model.
---

# Data model

Review a model before creating application code. The job is to expose decisions that implementation would otherwise freeze.

## Modes

- `topic: <problem>` proposes a model for a new problem.
- `review: <schema, path, or concern>` assesses an existing model.
- With no argument, review the data model implied by the immediately preceding discussion.
- `materialize: <lab/<slug>.yaml>` is explicit human approval to create code from an already reviewed proposal.

Plain text after `/data-model` is steering for the current review. It does not approve materialization.

## Review phase

1. Read the relevant project instructions, data models, migrations, schemas, and tests.
2. Separate observed facts, derived measurements, and authored judgments.
3. Identify rebuildable inputs and durable human state.
4. State where evidence, authorship, alternatives, and uncertainty must live.
5. If any load-bearing distinction is unknown, ask a question before proposing a field. Do not invent it.
6. Read the `house-style` skill. This is a `lab / operate` surface.

Create two files in `lab/`, without overwriting either:

- `data-model-<slug>.yaml`, the editable proposal and review record.
- `data-model-<slug>.html`, rendered from that YAML by the shared renderer in the `house-style` skill.

Use a clear kebab-case slug. If either file exists, add a meaningful suffix such as `-v2`.

The YAML must contain exactly five `slides`. It may also contain a `proposal` mapping with these fields:

```yaml
title: Library lending model
proposal:
  status: draft
  question: What must the system answer?
  assumptions: []
  open_questions: []
  lifecycle:
    rebuildable: []
    durable: []
  model:
    language: python
    target: null
    entities: []
slides: []
```

Use this slide order and labels:

1. **Question**: the decision or research question the model serves.
2. **Things**: entities, events, relationships, and cardinality.
3. **Lifecycle**: rebuildable inputs, durable state, and stable references.
4. **Integrity**: authorship, evidence, alternatives, uncertainty, and validation.
5. **Decision**: proposed shape, unresolved choices, and the review request.

Every slide needs a title, a one-sentence takeaway, and one of the renderer kinds: `prose`, `comparison`, `table`, `diagram`, `decision`, or `custom`.

Run the shared renderer. The `house-style` skill's "Renderer" section has the exact command and its fallback path for each harness:

```sh
uv run --quiet --script "$renderer" lab/data-model-<slug>.yaml
```

Inspect the rendered deck at a 1440×900 desktop viewport and a 390×844 phone viewport. If browser inspection is unavailable, report visual checks as unverified. Fix findings in one batch. Report both paths and ask the reviewer to comment.

## Materialization phase

Only enter this phase when the user invokes `materialize:` with the reviewed YAML path. That command is the approval record.

1. Re-read the YAML, reviewer comments in the session, and the target project's instructions.
2. Confirm the proposal has a Python target. If it does not, stop and ask where the code belongs.
3. Inspect existing package layout, dependency declarations, conventions, and tests.
4. Use Pydantic `BaseModel` for data validation by default. Use an ABC only for genuinely interchangeable behaviour, never as a default model base.
5. Add Pydantic with `uv add pydantic` only when it is absent and the user has approved materialization.
6. Create the models, focused validation tests, and only the documentation necessary to explain hard-to-reverse choices.
7. Do not create migrations, persistence, routes, or APIs unless the approved proposal explicitly calls for them.
8. Update `proposal.status` to `materialized` and re-render the deck with `--force`.
9. Run the project's relevant checks. State what passed and what remains unvalidated.

## Hard stops

Stop and ask before materializing when any of these is unclear:

- whether one target can have multiple valid values
- who authored a judgment and which evidence supports it
- whether a value is observation, measurement, or reading
- whether state must survive a rebuild
- the target module or package

## Writing

Use short, concrete sentences. Lead with the decision. Mark assumptions and uncertainty plainly. Never turn a proposal into a fact.
