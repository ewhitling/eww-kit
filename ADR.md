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
- Status: Accepted

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
- Status: Accepted

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
- Status: Accepted

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
