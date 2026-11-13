---
name: plan-work
description: Interview a manager to turn a vision, capability, or tentpole into assignable tasks with design review and validation.
disable-model-invocation: true
---

# Plan work

Turn an ambition into bounded work that junior engineers can own.
Produce platform-independent Markdown that can transfer into trackers such as Jira.
Keep readable task descriptions separate from confirmed tracker fields.
Do not create tickets in a particular service.
Plan software, processes, investigations, and adoption work without assuming everything needs code.

## 1. Interview for the outcome

Use the supplied topic as the starting point. Ask one or two questions per turn.
Use an available question tool where appropriate, with room for custom answers.
Reuse information already provided. Ask only questions that affect the plan.

Establish:
- Who needs which capability, and what currently prevents it.
- Observable success, baseline where available, and the smallest useful outcome.
- Commitments, priorities, exclusions, deadlines, and available delivery and review capacity.
- Team experience, existing systems or processes, access constraints, and applicable AI/data policies.

Distinguish confirmed facts, proposals, and unknowns. Challenge a proposed solution
that does not support the outcome. Do not invent targets, people, dates, or constraints.
Keep employer details in the conversation or an approved employer destination,
never in shared skill sources or personal notes.

Completion: summarize the outcome, evidence of success, boundaries, and constraints.
Obtain confirmation before decomposing the work.

## 2. Establish the approach and uncertainties

Explain how relevant components or process steps fit together using one concrete example.
Separate existing facts from proposed changes. Surface mismatched responsibilities,
missing interfaces, and assumptions requiring technical review.

Identify which decisions are fixed, which the assignee may make, and which need approval.
Preserve creativity within explicit boundaries rather than prescribing every implementation step.
Offer a small number of alternatives only where they affect the decision.

Turn unresolved feasibility or design questions into time-boxed investigation tasks.
Each investigation must answer a decision question and produce evidence and a recommendation.
Its timebox limits effort, not the obligation to report an inconclusive result.
Implementation dependent on that answer remains blocked or provisional.

Completion: the manager confirms the approach and decision boundaries.
Unknowns have a resolution path; they are not disguised as implementation requirements.

## 3. Decompose into assignable work

Read [the task template](references/task-template.md).
Write each description as Problem / Goal / First step / Done, with a concrete
picture of the result. Integrate safeguards into that story, not a list of parameters.
Keep assignee, state, milestone, priority, and subtasks outside the description;
include confirmed values only. Omit empty fields and administrative status labels.
Map outcome to milestones to tasks. Each milestone produces a demonstrable capability,
not merely a list of activities. Each task has one accountable owner and a reviewable deliverable.

Choose task size against team experience and the next useful feedback point.
Split work that mixes unrelated outcomes, hides a major decision, or postpones feedback.
Avoid artificial tasks for every mechanical step. Agree timeboxes or effort ranges;
label estimates as estimates, and include review and rework capacity.

Order dependencies explicitly. Detail the next executable work first.
Keep later work provisional where earlier findings can materially change it.
Name owners and reviewers only when confirmed. Explain consequential assignment
gaps in prose without adding empty owner or reviewer fields.

Completion: each detailed task can be understood without access to this interview,
has a clear dependency path, and supports an agreed milestone.

## 4. Build review into the work

Include design review and validation review in most tasks.
Scale their depth to risk. A familiar, small task can use a brief check or an
explicitly agreed exemption with a reason. Do not silently omit either checkpoint.

Design review happens before substantial execution. Specify what the assignee brings:
the problem, approach, relevant component roles or process responsibilities,
one worked example, and important tradeoffs or failure cases.
Review can approve, request changes, or require investigation.
State what work may proceed while approval is pending.

Validation review happens after execution. Specify checks, expected results,
evidence to submit, and who can accept it. Code review may contribute, but is not
a substitute for checking behavior. Processes need trials and exception handling;
investigations need evidence sufficient to support a decision.

Prefer a suitable peer reviewer, not the manager by default.
Consider knowledge, availability, and independence. Peer review is a preference,
not a mandate. A junior peer can help; unfamiliar critical boundaries require
someone with relevant expertise. Design and validation reviewers may differ.
Separate reviewer from decision owner: the latter resolves scope or commitment tradeoffs.
Flag missing reviewer capacity instead of silently assigning the manager.

For AI-assisted work, require the assignee to explain decisions and verify behavior.
AI-generated code, tests, or explanations are not independent acceptance evidence.
Apply the team's approved AI/data policy; do not invent a blanket AI ban or usage quota.

Completion: each task states its checkpoints or agreed exemptions, required evidence,
reviewer or reviewer gap, and escalation conditions.

## 5. Check readiness and hand off

Draft the plan in chat using the template. Audit every detailed task:
- Is its contribution to the outcome explicit?
- Can a junior engineer identify the deliverable and what is outside scope?
- Are technical assumptions and dependencies visible?
- Are decision freedom, review timing, and pause conditions clear?
- Does every acceptance criterion have a check, expected result, and evidence?
- Are reviewers and decision authority identified without assuming the manager?
- Is missing input shown as a blocker rather than false readiness?

Assess delivery readiness separately from completion. The following distinctions
are reasoning checks, not mandatory output labels or a tracker-state vocabulary:
- **Draft:** scope or assignment is unresolved.
- **Blocked:** a stated prerequisite prevents the next authorized step.
- **Ready:** inputs, ownership, review arrangements, and criteria support that step.
- **Ready for review:** the assignee has submitted the required material.
- **Accepted:** the authorized validation reviewer has accepted the evidence.
Identify which checkpoint is awaiting review. Design approval permits execution;
it does not mean the task is accepted. Never mark planned work as already validated.

Present the first assignable work, blocked work and its resolution path, and remaining
manager decisions in plain language. Explain uncertainty where it affects action;
avoid repeated labels such as Status: provisional. Use a confirmed tracker state only
in the separate fields section, without claiming planned work is already accepted.
Obtain approval before saving to a user-chosen destination.
Do not create external tickets, assign people through integrations, or execute the plan.
Stop at the planning handoff.

Completion: the manager has a readable plan with clear next actions, honest blockers,
and confirmed tracker fields separated from each description.
For skill evaluation, use [validation scenarios](references/validation.md).
