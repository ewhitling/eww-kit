---
name: teach
description: Teach one focused concept and save a standalone Markdown lesson in a confirmed location, with Mermaid when useful.
disable-model-invocation: true
argument-hint: "Topic or discussion to turn into a saved lesson"
---

# Teach and save a Markdown lesson

Explicit invocation requests teaching plus a saved lesson, subject to destination and notes-scope confirmation.
Use [eww-teach](../eww-teach/SKILL.md) for the teaching approach. This skill owns destination selection and the saved artifact.
If the user says chat-only or no save, teach conversationally without accessing a note store or creating files.

## 1. Confirm the lesson and destination

Infer the topic and goal from the request and conversation. Ask one focused question if the scope is unclear.
For a substantial lesson, agree the small learning route before writing it.

Notes live in an Obsidian vault of plain Markdown. Read `AGENTS.md` at the vault root before selecting a location.
The default destination for a lesson is the vault's `collections/lesson/` folder.
Confirm the exact folder or project directory and intended .md output with the user.
An explicit, unambiguous destination in the current request counts as confirmation; avoid asking twice.
A previous session's destination is only a suggestion.
Never infer a vault from the current directory. If the agent instructions do not name the vault on this machine, ask.

Follow any write limits the agent instructions set for this machine.
If the vault is missing or its rules conflict with the request, stop saving and explain the blocker. Teaching in chat can continue.
For a project artifact outside the vault, confirm the directory and read its applicable instructions.
Keep employer lesson content out of a personal vault.

Completion: a focused topic, confirmed destination, and applicable access/writing rules before content access.

## 2. Search before creating

Search only the approved destination for a relevant existing lesson. Start with titles, then inspect likely matches.
Read local AGENTS.md instructions before notes. Preserve existing filenames and naming conventions.
If several notes could be the target, ask which one. Never silently overwrite a same-name file.
For an existing lesson, propose a narrow addition or correction and obtain approval for that edit.
Preserve human prose, frontmatter, links, and authorship markers. Do not take ownership of old engine marker blocks.

For a new lesson, choose one descriptive .md filename within the confirmed root.
Create a missing folder only when explicitly approved. Refuse unexpected symlinks or paths outside scope.
Keep any needed backups private and outside shared/synced storage, following the applicable contract.

Completion: one new-file path or an approved edit to one existing lesson.

## 3. Teach for understanding

Follow eww-teach: motivate the problem, establish foundations, and connect each step to the next.
Use one concrete worked example. Distinguish observed facts, assumptions, and limitations.
Check sources when claims are unfamiliar, current, contested, or consequential. Prefer primary references.
Do not invent citations or send private notes to external research tools.
Check transfer with one application question when useful; do not require a quiz before saving.

The saved lesson must stand alone without this conversation.
Use the bounded structure in [Lesson format](references/lesson-format.md), adapting headings to the topic.
Save an explanation, not a transcript or session journal. Omit filler sections and automatic learning records.
One Markdown file is the default. No HTML lessons, course workspace, generated deck, or automatic resurfacing.

## 4. Add a diagram only when it helps

For a relationship that benefits from a diagram, read [visualization](../visualization/SKILL.md),
[house-style](../house-style/SKILL.md), and its [Mermaid guidance](../house-style/references/mermaid.md).
Write a fenced mermaid block directly in the Markdown lesson. There is no HTML renderer dependency.
Prefer vertical flowcharts for narrow note columns, short labels, and explicit arrow meanings.
Include a short prose equivalent so understanding does not depend on rendering or color.

Use the host's default Mermaid theme for notes that switch between light and dark modes.
Use the house-style dark directive only when the user wants a fixed dark diagram.
Do not install plugins, alter vault CSS, invoke a CDN, or generate another artifact to force a diagram to render.
If the destination lacks Mermaid support, use prose or a small text schematic instead.
Validate syntax with an available trusted tool when possible. Report renderer checks as unverified if unavailable.
Never treat an unrendered diagram as visually checked. A diagram is optional, not a quota.

## 5. Save and verify

Before writing, recheck the exact path and existing content. Stop if the file changed since review.
For a new file, verify it is still absent. Write only the approved lesson or edit.
Mark agent-written content using the destination contract. In mixed-authorship notes, mark the actual generated section.
For an all-new project lesson with no special contract, label it "Agent-written lesson" below the title.
Do not invent topic tags, alter vault settings, or enable a daily/teach automation service.

Read back the file and check authorship markers, Markdown fences, sources, and the scoped diff.
Confirm human content is intact for an update. Do not claim learning mastery from a saved file.
Report the saved path, whether it was created or updated, and any unverified diagram checks.
If saving was blocked, say that no file was written and give the next decision needed.

## Maintainer validation

Use [Scenarios](references/scenarios.md) for bounded walkthroughs or explicitly approved agent trials.
Static tests check the skill's structure and dependencies, not whether agents follow it in a live session.
