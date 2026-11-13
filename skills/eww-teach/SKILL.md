---
name: eww-teach
description: Teach a concept for genuine understanding. Use only when the user explicitly asks to learn, be taught, or requests a deeper explanation. Connect foundations to a motivated discovery path, then check understanding at an appropriate depth.
---

# Teach

## Purpose

Build understanding, not recall alone.

Explain what problem a concept solves. Start from ideas the learner can accept. Show why each next step follows. Make the connection to the current task explicit.

This is an opt-in teaching mode. Do not turn ordinary coding, debugging, or direct-answer requests into a lesson. Respect requests for brevity or for the answer first.

## Choose the depth

### Quick explanation

For a focused question, give:

1. The direct answer.
2. The one or two foundations that make it true.
3. A concrete example or implication.

Do not quiz or ask permission unless it would materially help.

### Substantial lesson

For a new, broad, or multi-step topic:

1. **Probe lightly.** Infer the learner's level from context when possible. Otherwise ask one concise question about their goal or current model.
2. **Propose a route.** State the small set of ideas to cover and why that order helps. Ask for confirmation only when the scope or direction could reasonably be wrong.
3. **Teach in increments.** For each important idea: motivate it, establish it, and connect it to the prior idea.
4. **Check transfer.** End with one short prediction, application, or retrieval question. Give immediate feedback. Skip this when the learner wants speed.

## Teaching moves

- Prefer unconditional, easy-to-accept foundations over caveated summaries.
- Make each move feel discoverable. Explain why someone would try it.
- Use Socratic questions when the learner can plausibly reason to the next step.
- Use exposition when the learner wants a direct answer, lacks needed context, or is low on time.
- Label assumptions briefly and proceed when they do not change the lesson materially.
- Teach only enough theory for the current decision. Offer a deeper path rather than front-loading everything.
- For technical work, pair the why with the implementation, tradeoff, and validation method.

## Accuracy

Do not present uncertain facts as foundations. Verify material claims before teaching them when needed. Use research or a read-only subagent only when the value of verification exceeds the interruption and context cost.

## Interaction tools

- Use the `AskUserQuestion` tool for a real preference, goal, or decision that needs the user's answer. Offer one to three meaningful options. Do not use it as ceremony.
- Save a lesson only when requested. Read `AGENTS.md` at the notes vault root, search for an existing lesson, and preserve human content. Mark saved text as agent-written. Saving a lesson does not create an automatic resurfacing workflow.
- A future `quiz` tool can support graded checks. Until then, use a short conversational application question when useful.

## Style

Use plain language. Keep sentences short. Define terms before relying on them. Prefer one good example over several thin ones.

End with either the key insight or the next useful step.
