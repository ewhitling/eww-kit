# Behavioral validation

Run these fictional cases against the skill before claiming reliable behavior.
These are evaluation scenarios, not completed tests or employer project records.
Check the conversation as well as the final plan.
Repository checks verify packaging, not interview quality.

## 1. Vague ambition

Input: "Make the team better with AI."

Expected: ask about beneficiaries, current work, and observable improvement.
Ask at most two questions per turn. Confirm the outcome before decomposition.
Do not assume a chatbot, training course, platform, or numerical productivity target.

## 2. Mistaken technical substitution

During a fictional data-service plan, say:
"The junior engineer proposes replacing S3 with SQLite."

Expected: ask about the actual storage and access requirements.
Explain the different responsibilities in context without asserting they can never be alternatives.
Require a worked data-flow example at design review.
If the fit is uncertain, create a bounded investigation and block dependent implementation.
Fail if the plan accepts the substitution without examining requirements.

## 3. Process rather than software

Input: "Create a repeatable onboarding process for new analysts."

After questions, supply fictional constraints and a reviewer.

Expected: tasks include process design review, a representative trial, an exception case,
and evidence-based acceptance. Publishing a document alone does not validate onboarding.
No repository or code review is required merely because the assignees are engineers.

## 4. No suitable peer available

Say: "Both juniors are unfamiliar with this boundary; I cannot review this week."

Expected: record a reviewer capacity gap.
Seek someone with relevant expertise or propose changing sequencing/scope for approval.
Do not assign the manager silently, treat a junior peer as sufficient automatically,
or mark gated implementation ready.

## 5. Creativity and AI

Say: "They want to use AI to build a larger framework than the agreed small deliverable."

Expected: preserve implementation freedom within agreed boundaries.
Route the scope expansion to the decision owner.
Require understanding, demonstrated behavior, and applicable policy compliance.
Do not accept generated tests as proof by themselves or impose an arbitrary AI quota.

## 6. Small routine work

Supply a familiar, low-risk change with a clear acceptance check.

Expected: propose proportionate reviews, not a large design document.
Omit a checkpoint only with an explicitly agreed reason.
Keep acceptance evidence even if a separate review is waived.

## 7. Investigation with an inconclusive result

Supply an investigation whose findings do not establish feasibility within its timebox.

Expected: accept sound, traceable investigation evidence without inventing certainty.
Leave dependent delivery work provisional or blocked.
Identify the decision owner for further investigation, scope change, or stopping.

## 8. Handoff and persistence

Ask for the final plan with some owners and dates still unknown.

Expected: stable task IDs, explicit gaps, dependencies, and criterion-to-evidence mappings.
Distinguish design approval, ready for validation review, and accepted.
Ask before saving; do not create tickets or write employer content into this repository.

## 9. Readable software task

Input: "Preserve the Starship prompt when removing old shell settings."
Supply synthetic evidence that initialization sits inside a tool-managed block.

Expected: Problem explains the lost prompt; Goal shows a fresh terminal retaining it.
First step proposes a disposable fixture and proportionate design review. Done maps
preserved initialization, no duplicates, repeat removal, and unchanged neighboring
settings to checks and evidence. No separate mandatory design-review form.
The description uses Problem / Goal / First step / Done, not parameter lists.

## 10. Tracker-ready process task

Input: "Create a repeatable onboarding process for new analysts."
Confirm assignee Alex, milestone First cohort, and priority High. Leave state unknown.

Expected: four-section description paints the first analyst's successful experience.
First step includes process design review. Done includes a representative trial,
an exception case, and reviewer acceptance of evidence. Keep confirmed assignee,
milestone, and priority in separate fields; omit state and empty subtasks.
No Status: provisional, duplicate metadata, invented values, or Jira-specific workflow
assumptions. Copying the description requires no removal of tracker fields.

## Evaluation record

For each actual trial, record the supplied fictional inputs, observed behavior,
pass/fail against expectations, and limitations in an approved evaluation destination.
Do not report a static read-through as an independent runtime trial.
