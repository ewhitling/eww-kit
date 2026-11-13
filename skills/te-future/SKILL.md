---
name: te-future
description: Run a future-cone thought experiment as a driven conversation. The user steers; agents fan out from hostile standpoints to generate structurally-distinct branches, which are filtered against an altitude bar, grouped by shared causal root, and attacked. Stops at a gate after every phase so the user's priors can move mid-run. Writes a durable revisable artifact to studio/<slug>/ in an output folder the user confirms. Triggers on "future cone", "te future", "what's the future of", "scenario planning", "how does X evolve", or when the user wants speculation that beats the consensus median.
argument-hint: '[the question (e.g. "what is the future of remote work?") optionally followed by a studio slug]'
---

# te future: Future Cone

A thought experiment that produces **claims**, not a document. Every branch kept must be checkable later, or it does not belong in the artifact.

## How this runs: read this first

**This is a driven conversation, not a batch job. The user steers. You supply.**

The tool exists because the user's priors move when they talk to real people about the question. A run that goes away for twenty minutes and returns a finished document cannot capture that, and worse, it silently deletes the phases that need him. An earlier version of this skill was a single end-to-end `Workflow`; it skipped Phase 1 on four consecutive runs, because a script has no way to stop and ask. The phase where he drives was structurally impossible to reach.

So:

- **Every phase ends at a gate.** Present the output, state the decision in front of the user, stop. Do not run the next phase in the same turn.
- **Only Phase 2 is a `Workflow`.** It is the one phase with no human decision inside it: seven independent standpoint agents, ~4 minutes. Everything else is a conversation turn measured in seconds.
- **Where a judgment must be blind, spawn one scoped `Agent`** with only the fields that judgment needs. You have seen the standpoint labels; a sub-agent given an anonymized payload has not. This is how the anti-inflation discipline survives moving into conversation.
- **All counting happens in code.** Never in your head, never by an agent.

### Gate format

Every gate looks the same. Short, and the options are the user's, not yours:

```
<the phase output, compact>

Gate N. <the one decision>
  - <option a>
  - <option b>
  - or: change an assumption, add a standpoint, kill something, stop
```

The final line is not decoration. Always leave the frame open: the phases below are what you know how to do, not the limit of what the user is allowed to ask for.

### Auto mode

If the user says "auto", or the run is unattended, take the stated **default** at each gate and proceed without stopping. Say once at the start that you are in auto mode, and record it in the artifact. Auto mode is the degraded form. It exists so a tired evening still produces something, not because it is equivalent.

## Why this exists

Asking one model for N scenarios produces synonyms of the consensus. The output reads like a trend report because that is what it interpolates. This skill fixes that structurally, not with adjectives:

- **divergence comes from standpoint diversity**, not from asking one agent to be creative
- **an altitude bar** rejects trend restatements before they reach the artifact
- **an adversary** supplies the branch the user would rather not consider
- **a pathfinder** backcasts routes, and must name what the route depends on
- **gates** let the user's priors move mid-run, which is the actual point

## Input

The question: $ARGUMENTS

If `$ARGUMENTS` is empty, ask: "What's the question? Phrase it as *how does X evolve* rather than *will X happen*."

Derive a kebab-case studio slug from the question unless the user gave one (e.g. "what is the future of remote work?" → `remote-work`). Confirm the slug before writing anything.

## The altitude bar

The single most important contract in the skill. Every generated branch is measured against it.

A branch **fails** if it is a trend restatement: a directional claim about more/better/faster that a consultancy deck would already contain.

> ❌ "AI will personalize advertising more precisely."

A branch **passes** if it is a **structural claim**: an assertion about what changes shape: what unbundles, who captures value, which constraint stops binding, what becomes verifiable, which role disappears.

> ✅ "The agency retainer unbundles, because agent output is machine-verifiable and clients stop paying for the assurance the retainer was really selling."

Rule of thumb: if the branch cannot be wrong in a specific, observable way, it is at the wrong altitude.

---

## Phase 1: Frame

**Conversation. No agents. This is the steering wheel: never skip it.**

1. Restate the question in one sentence. Confirm.
2. Propose 4-6 **assumptions** you believe the question rests on, as `A1…An`. Do not ask the user to generate them from nothing; that is work, and they are here to correct, not to author.
3. Mark which you think are **load-bearing**: if false, the whole picture changes.

The user corrects, deletes, adds. What survives is the record against which later prior-drift is measured, and the perturbation surface for re-runs.

If a prior `te-future.md` exists for this slug, read its `## Assumptions` and open with those instead of fresh ones. The interesting question on a re-run is always *which of these has moved*.

> **Gate 1.** The assumption set, and which standpoints Phase 2 should use.
> **Default (auto):** your proposed assumptions stand; use the generic roster.

## Phase 2: Diverge

**The only `Workflow` in the skill.** The user invoked the skill; that is the opt-in.

One agent **per standpoint**, not N scenarios per agent. Choose 5-7 standpoints that would genuinely disagree about *this* question. The roster below is a starting point to adapt, never to use verbatim: it was derived from one run on one question and carries that question's fingerprints:

- **the incumbent**: someone whose P&L depends on the current arrangement
- **the new entrant**: someone with no legacy cost structure to defend
- **the technologist**: what the capability curve permits regardless of demand
- **the regulator / institutional check**: what gets constrained, and when
- **the labor economist**: which roles decompose into tasks, which tasks resist
- **the customer**: whose willingness to pay moves, and for what
- **the historical analogue**: the closest prior structural transition, and where the analogy breaks

Pass Phase 1's assumptions into every standpoint brief. An assumption the user corrected must constrain the fan-out, or the correction did nothing.

Each agent returns branches under a schema: `claim`, `mechanism` (why it happens, not that it happens), `standpoint`, `plausibility`, `supporting`, `disconfirming`, `resolution` (a dated, observable criterion).

**Plausibility is ordinal, never a percentage.** Bands: `probable` / `plausible` / `possible`. LLM-elicited point probabilities on novel futures are anchored on phrasing and narrative fluency, not calibrated. A number here would assert precision the method cannot support.

Instruct every lens agent: *exclude any scenario that already appears in a mainstream trend report on this topic.*

> **Gate 2.** Raw branch count per standpoint, and any standpoint that produced nothing structural. Ask whether to re-run a weak standpoint before converging.
> **Default (auto):** proceed with what came back.

## Phase 3: Converge

Convergence across hostile lenses is the strongest signal this method can produce, which makes it the easiest number to corrupt. **Never let an agent report how many standpoints agreed.** An agent that can see the standpoint labels will inflate the count, and the inflated number is exactly the one he would repeat out loud in a room.

Four steps, in order:

**3a. Anonymize.** In code: assign opaque ids (`b01…bNN`), strip the standpoint from every branch. Keep an id → standpoint map no agent ever sees.

**3b. Cluster blind.** One scoped `Agent` sees only the anonymized branches, and only the fields the judgment needs: `claim`, `mechanism`, `resolution`. Evidence and plausibility play no part in deciding sameness, so they are withheld. The merge test is **resolution identity**, not similarity:

> Two branches are the same claim only if the same observable would confirm both and the same observable would falsify both. If you can construct a world where one is true and the other is false, they are different claims.

Shared subject matter is not sameness. Shared mechanism is not sameness. Err toward splitting: a wrong merge destroys information, a wrong split costs nothing. Singletons are expected; a single-lens branch is not a weak branch.

**3c. Count mechanically.** Map member ids back to standpoints in code. Convergence is now arithmetic. The agent could not inflate a number it never saw.

**3d. Carry the rest through in code.** Plausibility is the modal value across members (ties break conservative). Supporting and disconfirming evidence are joined from the members. The clusterer never sees these fields and never re-synthesizes them, so there is nothing for it to invent.

> **An attribution audit was tried here and removed.** It ran one blind judge per (cluster, standpoint) pair to confirm each standpoint independently asserted the claim. Across two runs it dropped 0 of 7 attributions while costing seven agents and a serial stage. The deflation from inflated counts came from blind clustering alone. If a run shows the clusterer merging loosely, reinstate it, but do not carry it as insurance against a failure that has never occurred.

> **Gate 3.** The clusters, with mechanical lens counts. Ask whether any merge is wrong. The user knows the domain; the clusterer does not.
> **Default (auto):** clusters stand.

## Phase 4: Altitude filter

One scoped `Agent` whose **primary job is rejection**. Merging is the only thing it may not do.

Say that prohibition once. An earlier version fenced the critic four different ways ("do not merge, do not regroup, do not change the counts, return in order") and it rejected nothing: the don't-touch-anything framing suppressed the rejection authority along with the merge authority. Never show it the lens counts either; a count reads as a prior endorsement.

Give it a rejection target: **expect to kill a quarter to a third.** A critic that retains everything has failed, and a silent pass rate near 100% is the signature.

Reject under one of six named failure modes. Each is a real rejection this method has produced, but all six were derived from a single question in one domain, so **treat them as a starting vocabulary, not a fixed taxonomy.** On a new domain, expect to retire some and name new ones.

- **not-domain-specific**: true of every B2B category. "Approved-vendor status becomes valuable" is generic procurement inertia with a domain label on it.
- **stapled**: two claims in one coat that would resolve on different observables.
- **litigation-forecast**: predicts a remedy or enforcement outcome, not a market-structure change. Resolves on nothing observable until settlements land.
- **economics-costume**: a trend restatement in technical vocabulary. Strip the jargon; if what remains is "AI cuts headcount while spend holds", it is a trend restatement. Naming Baumol does not raise altitude.
- **trend-restatement**: plain directional more/better/faster.
- **unresolvable**: no dated observable could confirm or falsify it.

Enforce shape on everything retained: **one sentence, max 35 words, one assertion.** If it needs "and because", keep the load-bearing half and move the rest into `mechanism`.

**Join on stable cluster ids, never on position.** Every input id comes back in exactly one of `retained` or `rejected`, echoed verbatim; unaccounted ids get logged. A positional join silently misattributes everything below a dropped row, which is worse than the error it replaced because it still looks precise.

> **Gate 4.** Rejections first, with their failure modes: the rejections are usually more interesting than the survivors. Then the retained set. Ask whether any rejection was wrong.
> **Default (auto):** the critic's verdicts stand.
>
> **The critic is not stable across runs.** On byte-identical cached input, one claim was retained in one run and rejected in the next. Present its verdicts as one opinion, never as a finding.

## Phase 5: Theme

Splitting is not free. Enforcing resolution-identity correctly separates claims that share a **causal root**, and that relationship is real signal the split throws away. Two different things are easy to conflate:

- **Convergence**: different lenses assert the *same* claim. Rare, and strong.
- **Theme**: different claims share a *causal root*, so they fail together. Broader, and it is what a cone's sectors should show.

A theme of four mutually reinforcing claims can be stronger evidence than one claim three lenses agree on. Measure both; never let one stand in for the other.

**The theme test is shared failure, not shared topic:**

> Two claims belong to the same theme only if there is a single causal root such that, if that root turned out to be false, both claims would be damaged at once. If one could survive intact while the other collapses, they are different themes.

You are identifying correlated risk. Same industry, same actors, same technology are not themes.

This agent **must not merge or rewrite any claim.** It draws a boundary; claims stay distinct and keep their own separate resolutions. Blind to standpoints, like the clusterer. Each theme requires:

- **root**: the one mechanism every member depends on, stated as a factual assertion that could be false
- **root_falsifier**: a single dated observable that would damage every member simultaneously. If you cannot write one that hits every member, the theme is too loose.

Themes need 2+ members and **2+ distinct lenses**. A theme built from one standpoint's output is one analyst's related thoughts, not correlated evidence: bar it or flag it. Claims sharing no root go unthemed; that is a normal outcome, expect several. **Breadth is counted in code**, same discipline as convergence.

> **Gate 5.** Themes with roots and falsifiers, ordered by breadth. Ask which roots are worth attacking.
> **Default (auto):** attack all roots.

## Phase 6: Attack

One `Agent`, three jobs:

1. **The unwelcome branch**: the future the user would find personally or professionally bad, stated without softening. This is usually where the information is, and it is the branch a compliant model omits.
2. **Attack every retained branch**: the strongest specific reason it does not happen. Not "uncertainty exists." A mechanism.
3. **Attack every theme root**: the highest-value target available, because a false root damages every member claim at once. A theme whose root falls is worth more to know than any single branch dying.

**The adversary does not kill anything. The user does.**

This is the change that gating buys. The adversary's job is to produce the best attack it can; the verdict is the user's at the gate. Two runs of evidence for why: it killed 12 of 18 claims, then 16 of 18, on a single unchecked verdict each, and in the second run, roots fell while their member claims individually survived, a contradiction nothing reconciled. An adversary with no cost for being wrong is as uninformative as one that kills nothing.

So the artifact carries **claim + strongest attack**, and a status only where the user set one. A branch that survived a specific attack the user read is worth more than one an agent waved through.

> **Gate 6.** Every claim with its attack, and the unwelcome branch on its own. Ask which claims the attacks actually kill.
> **Default (auto):** nothing is killed; every claim is recorded as `unjudged` with its attack attached.

## Phase 7: Path

Ask which 1-3 branches the user wants routes to. Do not do this for all branches.

For each, a pathfinder agent works **backwards** from the branch to the present: what sequence of decisions and events reaches it.

**A pathfinder always succeeds.** It will produce a plausible route to nearly anything, including the near-impossible. So the steps are not the deliverable. Required output, in this order:

1. **Load-bearing assumption**: the one thing the route depends on
2. **Earliest failure signal**: the soonest observable that would tell you the route is dead
3. Then the decision sequence

If the agent cannot name 1 and 2 concretely, the route is narrative, and it is marked as such in the artifact.

> **Gate 7.** The routes, load-bearing assumption first. Ask whether any load-bearing assumption contradicts an `A1…An` from Phase 1. That contradiction is the most valuable output the method produces.
> **Default (auto):** skip Phase 7 entirely: choosing branches is the user's job and there is no sane default.

## Phase 8: Write

Ask the user for the output folder, as an absolute path, unless they already named one in this conversation. Never assume a vault or notes location, and never hardcode a path. Confirm the full path before writing: `<folder>/studio/<slug>/te-future.md`. Create `studio/<slug>/` if it does not exist.

If the file exists, **do not overwrite.** Append a revision.

```markdown
# Future cone: <question>
#llm-generated

## Brief
<the question and its framing, 3-5 sentences>

## Assumptions
- **A1** <assumption> · load-bearing: yes|no · <who set it: proposed | corrected by the user>
- **A2** …

## Themes
Claims grouped by shared causal root. Members stay distinct and resolve separately.

### T1: <name>
- **Root:** the assertion every member depends on
- **Falsified by:** one dated observable that damages all members at once
- **Members:** B2, B5, B9 · breadth: N lenses
- **Adversary on the root:** the attack, and the user's verdict if they gave one

## Branches

### B1: <structural claim, one sentence, max 35 words>
- **Status:** stands | killed by the user at gate 6 | unjudged
- **Mechanism:** why this happens
- **Standpoints:** N lenses (computed)
- **Plausibility:** probable | plausible | possible
- **Supporting:** …
- **Disconfirming:** …
- **Attack:** the adversary's strongest specific objection
- **Resolution:** by YYYY-MM-DD we would know, because <observable>

## The unwelcome branch
### BX: <the one the user would rather not consider>
<same fields>

## Rejected at the altitude bar
- **<failure mode>**: <claim> · <why>

## Paths
### Route to B<n>
- **Load-bearing assumption:** …
- **Earliest failure signal:** …
- **Contradicts:** A<n>, or none
- **Sequence:** …

## Method
- **Mode:** driven | auto
- **Funnel:** N raw → N clusters → N retained / N rejected → N themes
- **Gates where the user overrode the machine:** …

## Revisions
### YYYY-MM-DD: initial
```

### Revisions

Prior drift is the most valuable output of this exercise, and re-runs are the primary operation, not the exception. When the user returns after real-world input (a conversation, a data point, an event) do not rewrite. Append:

```markdown
### YYYY-MM-DD: <what moved>
- **Trigger:** what caused the update (conversation with X, published data, event)
- **Assumption changed:** A2 no longer holds, because …
- **Branch effect:** B3 downgraded to `possible`; B5 added
```

The diff between revisions is the record of how the user's thinking actually moved. Never destroy it.

## Rules

- **The user drives.** Stop at every gate. Never run two phases in one turn unless in auto mode.
- **Leave the frame open at every gate.** The listed options are what you know how to do, not the limit of what the user may ask for.
- **Never overwrite.** The artifact accumulates.
- **Ordinal plausibility only.** No percentages, no fake precision.
- **Never let an agent report a count.** Convergence and theme breadth are computed in code from blind groupings. An agent that can see the labels will inflate the number, and the inflated number is the one he would repeat out loud in a room.
- **Convergence and theme are different signals.** Never let one stand in for the other.
- **One claim per branch.** One sentence, max 35 words, one assertion.
- **Join on ids, never on position.** Log anything unaccounted for.
- **Scoped payloads.** Give each agent only the fields its judgment needs. A field a model never sees is a field it cannot corrupt. (This is about correctness, not speed: trimming payloads was measured against wall clock and made no difference. Time is reasoning at high effort, roughly constant per stage.)
- **Watch for any stage that accepts ~100% of its input.** It has happened twice: a critic that rejected nothing, a theme grouper that themed everything. A near-perfect pass rate is the signature of a stage that has stopped discriminating, not of clean input.
- **Every branch carries a dated resolution criterion.** A branch that cannot resolve is not a claim, and it does not go in.
- **Tag `#llm-generated`** at the top of the file: this is an AI-owned artifact.
- Do not produce the visual. That is a separate step against the finished markdown.

## Known defects

State these when reporting results. Do not let them become invisible.

1. **The critic is unstable.** Byte-identical input produced opposite verdicts on the same claim across two runs. Nothing measures the variance. Candidate fix: three independent critics, majority vote.
2. **The adversary is unverified.** No fix is in place beyond removing its authority to kill (Phase 6). Its attacks are still one opinion each.
3. **The method is validated on one question.** Every calibration constant here: the roster, the six failure modes, the rejection target, the altitude bar's worked example: was fitted to a single run in one domain. Until a second domain has been run, assume some of it is residue.
4. **Phases 1 and 7 have never been exercised.** They were unreachable in the batch design this replaced.

## After

Offer, do not perform:

- render the cone as a static HTML Artifact from the finished markdown
