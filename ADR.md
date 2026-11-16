# Architecture decision records

Each record states context, decision, consequences, date, and status. When a decision changes, update its status and add a new record. Current evidence takes precedence over old decisions.

This repo is public. Records must not contain personal details, employer names, hostnames, or secrets.

## ADR 1: A suite of independent tools behind one launcher

- Date: 2026-11-12
- Status: Accepted

**Context.** Earlier attempts built one tool that did everything. Its shared layer kept growing and never finished. The version used daily was small. Later versions were too clumsy for daily use.

**Decision.** `eww` is a launcher with no logic. `eww <name>` finds and runs a standalone program named `eww-<name>`. Each program lives in its own folder, shares no code with the others, and also works when called directly. Bare `eww` prints the map of tools.

**Consequences.** One name to remember. Any tool can be rewritten or removed alone. Test for each tool: delete its folder and nothing else breaks. A machine can add its own commands by placing an `eww-<name>` program on its path. Some small duplication between tools is accepted.

## ADR 2: The command surface is frozen

- Date: 2026-11-12
- Status: Accepted. ADR 20 and ADR 22 record exceptions to the standalone-script rule.

**Context.** The old tool went through seven major versions in about five weeks. Verbs were renamed and retired in each one. That erased learned habits. Shell history shows mostly bare verbs and few flags.

**Decision.** The first verbs keep their old names and bare-verb behaviour: `w` and `h` (the same workspace), `context` (run automatically at session start), `daily`, `doctor`, `install`, `update`. Added: `weekly` and `define`. A verb is never renamed or removed. A new verb is added only after real use as a standalone script. Help keeps three groups (place, work, capture) and one meaning per output glyph.

**Consequences.** Muscle memory is protected. A poorly named verb stays, so names need care. These old verbs are not rebuilt at first and may return under the same rule: `journal`, `task`, `gh-project`, `llm`, `new`, `adopt`, `collab`. `sync` and bundle transport are gone.

## ADR 3: Public repo, fresh history, automatic leak checks

- Date: 2026-11-12
- Status: Accepted

**Context.** Some machines must never sign in to the personal GitHub account. A public repo can be cloned with no account or token. Old repos contain personal details in their history.

**Decision.** This repo is public and starts with no imported history. Files are copied in after review. Every commit is scanned for secrets and for a private list of personal strings kept outside the repo. Machines other than the personal ones pull anonymously and never push.

**Consequences.** No sign-in is needed on any machine to receive tooling. Everything here is readable by anyone, so personal content must live elsewhere (see ADR 5). Improvements made on a pull-only machine must be redone on a personal machine.

## ADR 4: Setup is one shell script with symlinks

- Date: 2026-11-12
- Status: Accepted

**Context.** A new server is set up about once a month. A new server has only a shell. Earlier setup needed review steps and a separate apply step.

**Decision.** One unattended shell script clones the repo, symlinks files into place, and fetches third-party skills from their original sources at pinned commits. `eww update` pulls and reinstalls. All other tools are Python run through `uv`. A hosting agent may run the script, but the script is the source of truth.

**Consequences.** The same result on macOS and Ubuntu. No dotfile manager to learn. Machine differences are handled by small conditions inside the files. Only skills written for this repo are stored here.

## ADR 5: Instructions are assembled from a base plus local suffixes

- Date: 2026-11-12
- Status: Accepted

**Context.** Agent instructions and skills need a generic public part, a personal part, and on some machines a separate private part.

**Decision.** `eww install` builds each deployed instruction file from the generic base in this repo plus every suffix file found in one local folder on that machine. A skill gets a suffix by file name. The personal suffix is a link to a file in the notes vault. Other suffixes are plain local files that never sync. Secrets stay in per-machine environment files.

**Consequences.** The public files stay generic. The output is plain files, so it works for any agent harness. Deployed files are generated, so edits belong in the base or a suffix.

## ADR 6: Obsidian vault is the record for notes

- Date: 2026-11-12
- Status: Accepted

**Context.** Notes lived in two stores with different structures. Tools need plain files.

**Decision.** One Obsidian vault of plain Markdown is the record, synced by Obsidian Sync. A one-time cutover moves notes from the previous store, which wins conflicts. Archived, trashed, and config mirror notes are not moved. Folders: `notes` (general notes that have no source type), `collections` (subfolders by source type), `drawings`, `journal`, `projects` (flat, with a `kind` property of `lab` or `studio`), `writing`, `inbox`, `_meta`. Topics are tags. Agent-written text is marked `#llm-generated`. A pull-only machine writes only to `inbox`, by convention.

**Consequences.** Every note has one home. Tools read and write files directly. The `inbox` rule is a convention, not enforcement. The current vault is backed up before the cutover.

## ADR 7: Teach is three small commands that write notes

- Date: 2026-11-12
- Status: Accepted. Refined by ADR 15, ADR 16, and ADR 21. Extended by ADR 20 and ADR 22. On 2026-11-13 the owner chose to run `eww daily` and `eww weekly` by hand, so neither has a schedule.

**Context.** The goal is to resurface existing notes daily, learn new concepts on demand, and see rising ideas before aggregators cover them.

**Decision.** `eww daily` adds three resurfaced items to the day-note. Each is a link plus a short excerpt, picked at random with a preference for items not shown recently. It uses no LLM and skips notes tagged `#no-resurface`. "Shown recently" is read from past day-notes. `eww weekly` runs a headless agent over a source list kept as a note, primary sources only, and writes up to five concepts. Ideas seen in two or more independent sources rank higher. `eww define <term>` writes a definition note with a short mechanism statement and one static diagram in the house style. Animation is used only for processes that change over time. Jobs run on a schedule on a personal Mac.

**Consequences.** No app, database, or state file. Daily runs are instant and free. The mechanism statement lets a wrong diagram be caught as a wrong sentence. Weekly quality depends on the source list.

## ADR 8: One token file generates every theme

- Date: 2026-11-12
- Status: Accepted

**Context.** The house style must match across HTML, Obsidian, the terminal, the editor, and charts.

**Decision.** One token file (colours, fonts, spacing) is the source. Generators write CSS, the Obsidian snippet, terminal and editor colours, and chart styles. The existing house style supplies the starting values. The Obsidian snippet is written into the vault and travels by Obsidian Sync.

**Consequences.** Consistency comes from generation. A colour change is one edit. Whether Obsidian Sync carries snippets must be verified before relying on it.

## ADR 9: Lab is parked, Studio needs no new code

- Date: 2026-11-12
- Status: Accepted. The Lab design session ran on 2026-11-13: see ADR 19.

**Context.** The Lab is the flagship capability but depends on the foundations. Past Lab work produced much one-off code and few reusable capabilities.

**Decision.** The Lab gets its own design session after the foundations. Two constraints are fixed now: it starts as skills and agents, with a terminal interface and then an app only if needed, and its work must build reusable methods. The Studio is covered by existing skills plus a short written workflow.

**Consequences.** No Lab code is written against tools that do not exist yet.

## ADR 10: Build order and the test for done

- Date: 2026-11-12
- Status: Accepted

**Context.** Daily use was the measure of the version that worked.

**Decision.** Build in this order: notes cutover, repo with setup script and launcher, design tokens, `daily`, `weekly`, Lab session. A step is done after one day of real use with no interface change. The old tool repos are archived after the first new install works.

**Consequences.** Each step is usable alone. A working system stays in place during the build.

## ADR 11: Private files come from the notes vault

- Date: 2026-11-12
- Status: Accepted. Extends ADR 3, ADR 4, and ADR 5.

**Context.** A public repo cannot hold git identity, machine paths, or personal profile text. Leaving those files on each machine left them unmanaged and unsynced, which was rejected. The other option was a private repo moved by git bundles. That brings back a manual transport step for every update and a credential on every server. The notes vault already reaches every machine the owner chooses.

**Decision.** The repo stays public. Private content lives in the vault under `_meta/eww/`. A machine opts in by writing the vault path into `~/.config/eww/vault`. When that file exists, `eww install`:

- links every file under the vault's `_meta/eww/home/` into the home folder. A private file wins over a repo file at the same path.
- links the vault's suffix files into `~/.config/eww/suffixes/`.

`~/.zshrc` is not linked, because installers append machine-specific lines to it. Install adds one line to it that loads `~/.config/eww/eww.zsh`. That file loads `~/.config/eww/private.zsh` when the vault provides one.

**Consequences.** Every managed file has one source: the repo for shared files, the vault for private ones. A machine with no `~/.config/eww/vault` file gets only public content, which suits a pull-only machine. Private files depend on the vault being present before install runs. A program that replaces its config file, in place of writing through the link, will break that link until the next install.

## ADR 12: The old generator and the Hood plugin are reused

- Date: 2026-11-13
- Status: Accepted. Refines ADR 8.

**Context.** ADR 8 called for a generator and an Obsidian snippet. Two existing pieces already did this work. A generator from the previous settings repo reproduced every current export exactly. The vault already ran Hood, an Obsidian plugin that adapts the house style and adds a custom cursor, with its colors written by hand.

**Decision.** The generator moves to `tools/themes/build.py` and runs with `make themes`. It is not an `eww` verb. `make test` fails when an export differs from the tokens. Hood moves to `obsidian/plugins/hood/`. The generator writes its palette block; the rest of its CSS stays hand-written. `eww install` copies the plugin into the vault on machines that name one. It copies, not links, because the vault is carried by a sync service. It never touches the plugin's settings file or the list of enabled plugins. Ghostty theme files under `home/` are generator outputs too.

**Consequences.** No new generator and no new Obsidian snippet. Exports are read-only outputs. A token change reaches Obsidian after `make themes` and `eww install`, then travels to other machines by Obsidian Sync. Hood's hand-written rules and its cursor code have no tests in this repo yet.

## ADR 13: Obsidian settings are seeded, never synced

- Date: 2026-11-13
- Status: Accepted

**Context.** Obsidian rewrites its settings files whenever a setting changes, and a sync service carries them between machines. A new vault still needs a starting place: the settings, the base theme, and the Hood plugin.

**Decision.** `make obsidian-snapshot` copies six settings files from the vault into `obsidian/defaults/`: app, appearance, hotkeys, core plugins, community plugins, and daily notes. Window layout, bookmarks, and plugin data are left out. The snapshot drops CSS snippets whose file is missing and plugins this repo does not ship. The Atom theme is kept in `obsidian/themes/Atom/` with its license. `eww install` copies each of these into the vault only when the vault lacks the file. It never replaces one.

**Consequences.** A setting changed by hand always wins. The defaults go stale until the next snapshot, which is acceptable for a starting place. For a new vault, install must run before Obsidian first opens it, because Obsidian writes its own defaults on first open. Community plugins must still be switched on once per device, because Obsidian keeps that choice outside the vault.

## ADR 14: A machine may list several vaults

- Date: 2026-11-13
- Status: Accepted. Extends ADR 11.

**Context.** ADR 11 let a machine name one vault. One machine needs two: a vault that must stay on that machine, and the personal vault. Other machines must hold only the personal vault. Naming the personal vault on the two-vault machine would have linked its private home files, including git identity, over that machine's own.

**Decision.** `~/.config/eww/vault` holds one vault path per line. The first line is the primary vault. Only the primary supplies private home files. Every listed vault supplies suffix files, and gets the Obsidian starting settings and the Hood plugin. When two vaults hold a suffix with the same name, the vault listed first wins and install reports it. `eww h vault`, `eww daily`, and the `vault` shell command use the primary. `eww h NAME` opens any listed vault by its folder name.

**Consequences.** Which vaults a machine has is decided by that machine's file and by what is synced to it. A vault that is not listed and not synced cannot leak to that machine. Git identity always follows the primary vault. Nothing in code stops an agent from writing into the wrong vault when two are present. That guard is an instruction in a suffix file on the two-vault machine.

## ADR 15: Day-notes start at the vault root, and eww daily follows Obsidian

- Date: 2026-11-13
- Status: Accepted. Refines ADR 6 and ADR 7.

**Context.** Day-notes were first created under `journal/<year>/`. The owner wants a new day-note at the vault root, where it is in view. `eww daily` had its own fixed idea of where the day-note lives, so it wrote to a different file from the one Obsidian opened.

**Decision.** New day-notes are created at the vault root, named `YYYY-MM-DD.md`. `journal/<year>/` holds filed ones. `eww daily` reads the folder and date format from Obsidian's Daily notes setting, and supports the YYYY, MM, and DD parts. It reads the 60-day history from any note named `YYYY-MM-DD`, wherever it sits in the vault.

**Consequences.** Obsidian and `eww daily` cannot disagree on the day-note. Filing a day-note into `journal/` does not lose its history. The owner files old day-notes into `journal/<year>/` by hand. No tool moves them, by choice.

## ADR 16: eww weekly fetches itself and gives the agent no tools

- Date: 2026-11-13
- Status: Accepted. Refines ADR 7.

**Context.** ADR 7 called for a headless agent over a list of primary sources. An agent that browses reads untrusted web text while holding tools, so a page could steer it. It is also slow, and its sources cannot be checked.

**Decision.** The program fetches every source in the vault note `_meta/eww/weekly/sources.md`. A feed gives items from the last 7 days. A web page is read from the top, taking links no earlier weekly note lists, and stopping after a run of links already listed. The agent runs with every tool turned off, in two calls. The first picks up to five concepts from the titles and summaries, and cites items by number, so each link in the note is one the program fetched. The program then fetches the article behind each cited item. The second call explains each concept in four parts: what it is, the problem it solves, why it is being discussed this week, and its mechanism. The first use of the tool showed that a mechanism alone gave too little context. A concept known only by a title is dropped. Concepts already held, as a definition note or in an earlier weekly note, are dropped. The note goes to `inbox/Weekly YYYY-Www.md` and lists every item read. That list is the history, so no state is kept outside the vault. `eww define` turns a concept worth keeping into a lasting note.

**Consequences.** A web page cannot make the agent act, and the agent cannot invent a source. The agent may use background knowledge to say what a concept is, but what happened this week must come from the article text. Some sites refuse article requests from a script. For those, the feed's own text is used, and no browser is imitated to get around the refusal. A source that gives titles only, with articles as PDF files, rarely yields a concept. The first run on a page source includes older items, because nothing is listed yet. A page that does not list its newest work first is a poor source; a feed is better.

## ADR 17: Notes carry no properties

- Date: 2026-11-13
- Status: Accepted. Refines ADR 6.

**Context.** The notes cutover wrote a properties block (YAML front matter) on most notes: topic tags, a creation date, a project kind, and an importance mark. The owner wants one way to sort and one way to filter. The stored creation dates turned out to be import dates, with over half of them on a single day, so they recorded little.

**Decision.** Folders are the primary sort. Inline tags carry topics, as `#topic/<name>` on a line under the title. Notes carry no properties block, and no tool or agent writes one. A one-time migration moved topic tags inline and removed the creation date and the project kind with no replacement. Notes marked important moved to `collections/_important/`, which `eww daily` never reads. An Excalidraw drawing keeps its property, because the plugin needs it.

**Consequences.** One mechanism fewer, and tags are plain text that any editor keeps. Notes cannot be sorted by a stored date, and database views that work on properties are not available. Alternate note names (aliases) are not available either. How a lab project is marked is left to the Lab design session. The vault backup taken before the migration holds every original block.

## ADR 18: Pi and Claude are both supported, and Pi keeps its path guard

- Date: 2026-11-13
- Status: Accepted

**Context.** An earlier settings repo dropped Pi and deleted its safety extension, leaving Claude Code as the only supported harness. The stack chosen for this repo lists both. `eww install` already deploys instructions and skills to Pi, but Pi was running with no guard.

**Decision.** Both harnesses are supported. The Pi path guard is restored as a home file, so `eww install` links it into `~/.pi/agent/extensions/`. It blocks writes to credential stores, asks before changes to system paths and destructive actions, and blocks known outbound network commands other than `gh` and `git push`. `eww doctor` counts a machine as broken when Pi is installed and the guard is missing. The guard's policy has its own test.

**Consequences.** Pi cannot fetch from the network, so `eww update` and `eww weekly` are run by a person or from Claude, not from inside Pi. The guard scans command text and is not an operating-system sandbox, so a determined command can evade it. A convenience extension that aliased the exit command was not restored.

## ADR 19: The Lab is a contract proved by hand before any eww code

- Date: 2026-11-13
- Status: Accepted. Refines ADR 9. Settles the question ADR 17 left open.

**Context.** Earlier lab work stalled. The cause was not missing analysis skills. A model settled interpretations that the owner never observed or chose, and too much was generated with no overall view. Earlier versions of this toolkit also built tooling before use.

**Decision.** The Lab exists so the owner learns concepts, methods, and insights. The unit of work is a discovery. The agent builds instruments freely. One test decides when to stop: if a choice changes what counts as evidence or how a result is read, the owner and the agent decide together. The owner reads a small set of real instances before any measurement runs at scale. A technique new to the owner is taught on a small example first. At a method choice the agent presents two or three researched options and offers a one-line concept check. The owner reads a result first, and the agent then gives a competing reading. An LLM may be an instrument only as a gated choice, with outputs tied to quotes and a sample checked by hand.

The record is one plain Markdown card per idea, in the project repo. States: incubating, observing, testing, settled, parked. A settled card records supported, contradicted, or unclear, with the belief before and after. Each test is one Makefile command that rebuilds its result from the data and stated assumptions. Every session opens with a map built from the cards. A lab project is marked by a `LAB.md` contract file in its repo, with no marker in the notes vault. Accepted concept explanations and one short insight per settled card are written to the vault.

Build order: the contract and card template are written by hand in one project repo. One discovery runs through the full loop. Only then do the proven parts move here as a skill and an `eww lab` command. A second project is required before the Lab counts as general.

**Consequences.** Nothing enforces the contract; it is a convention until a manual step repeats and earns a command. No Lab code lands in this repo until the first discovery is settled. Friction with the contract is logged in the contract file, and those lines decide what moves here. Analysis skills, the `eww lab` command, and publishing results are not designed yet.

## ADR 20: eww course writes a longer lesson, and is a verb from its first day

- Date: 2026-11-16
- Status: Accepted. Extends ADR 7. One exception to ADR 2.

**Context.** `eww define` is short by design: one paragraph and one diagram. The owner wanted a next step from that note, a first lesson of about eight paragraphs, without opening an agent session. The `teach` skill writes lessons, but it is interactive and has no fixed length. ADR 2 says a new verb is added only after real use as a standalone script. Any program named `bin/eww-<verb>` is a verb at once.

**Decision.** `eww course TERM` writes `collections/lesson/TERM.md` from one headless agent call with no tools. The note has eight headed parts in the order of the Teach lesson format: why it matters, what you need first, the mechanism with one Mermaid diagram, how it works, a worked example, variations, limits and common mistakes, and a question with a labelled answer. When a definition note exists for the term, its text goes into the prompt, so the lesson extends the definition and agrees with it. The reply is checked for shape before it is written, and an existing note is never replaced. The note is a separate command and a separate folder from `eww define`, so `eww daily` keeps resurfacing only definitions among machine-written notes. The owner chose to add the verb now, without the standalone period ADR 2 requires. The name `course` was chosen over `extend`, which suggests editing the definition note. Shared helper functions are copied from `eww-define`, per ADR 1.

**Consequences.** The name is permanent under ADR 2 before it has had real use. The agent has no tools and checks no sources, and eight parts give more room for a wrong fact than one paragraph. The shape checks cannot catch a wrong fact. Each note says that no sources were checked. A lesson that needs verified sources still goes through the `teach` skill. Two programs now hold copies of the same helpers and can drift.

## ADR 21: eww daily reads only the folders it is told to read

- Date: 2026-11-16
- Status: Accepted. Refines ADR 7.

**Context.** `eww daily` held a fixed list of folders to skip and read every other folder of `collections/`. New folders appeared in the vault that hold reference material, not ideas to revisit. They were resurfaced until someone noticed. Each new folder of that kind needed a code change in a public repo.

**Decision.** The rule is reversed. `eww daily` reads only the folders named in the vault note `_meta/eww/daily/folders.md`, one `- name` line for each. Every other folder is ignored, and so is a note placed directly in `collections/`. When the note is missing, a default list in the code is used: `article`, `book`, `definition`, `highlight`, `lesson`, `quote`, `video`. `eww daily --dry-run` prints the folders it reads and the folders it ignores. The tag rules are unchanged. `CONFIGURATION.md` now lists every settings file.

**Consequences.** A new folder never reaches the day-note by accident. A new folder that should be resurfaced stays silent until one line is added, and the dry run is the only place that shows it. The list of personal folders can live in the vault, outside the public repo. A folders note with no names makes `eww daily` stop with a message.

## ADR 22: eww chat opens a tutoring session on a lesson or definition

- Date: 2026-11-16
- Status: Accepted. Extends ADR 7. A second exception to ADR 2.

**Context.** `eww define` and `eww course` write notes, and reading a note is one-way. The owner wanted to talk through a note with an agent, started from the launcher, and to see the available notes when no topic is given.

**Decision.** `eww chat [TOPIC]` starts an interactive agent session on one topic. A topic is a note title in `collections/definition` or `collections/lesson`, and the agent gets both notes when both exist. Notes written by hand are included. An exact title opens at once. Otherwise titles that contain the words are used: one match opens, and several show a picker. With no topic, or no match, the picker shows every topic. The picker is `fzf` where installed and a numbered list otherwise. The agent gets the note text and a teaching instruction in its system prompt. The instruction restates the `eww-teach` approach, because skills are turned off in the session. After the first real session the owner set one rule: the owner asks the questions, and the agent gives a practice question or an understanding check only on request. The `eww-teach` and `teach` skills were changed to the same rule. The agent has the web search and web fetch tools, allowed without a prompt, and no file or shell tools. The chat is not saved. The owner chose to add the verb now, as in ADR 20, and chose the name `chat` over a flag on `eww course`, which would not fit definitions.

**Consequences.** The name is permanent under ADR 2 before real use. The agent cannot change the vault. The owner's questions and the topic can reach a search service, and a fetched page is untrusted text in a session that holds the note. With no file or shell tools, that text can do little. The teaching instruction is a copy of the skill's approach and can drift from it. Keeping something from a chat is a manual copy. An interactive session cannot be covered by the automated tests, which use a stand-in agent.
