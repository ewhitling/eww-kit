# Configuration

Where `eww` reads its settings. Decisions behind this layout are in `ADR.md` (ADR 5, 11, 14, and 21).

There are three places. The repo holds everything that is shared and public. A notes vault holds private content, under `_meta/eww/`. Each machine holds a small folder at `~/.config/eww/`.

## In a notes vault: `_meta/eww/`

| Path | What it holds | Read by | From which vaults |
|---|---|---|---|
| `*.md` | Instruction suffixes. Each file is added after `instructions/base.md` when agent instructions are built. | `eww install` | Every listed vault |
| `skills/<skill>.md` | Text appended to the skill with that name. | `eww install` | Every listed vault |
| `home/` | Private home files. A file at `home/<path>` is linked to `~/<path>`. A private file wins over the same path in the repo's `home/`. | `eww install` | The primary vault only |
| `weekly/sources.md` | The source list, one source per line. | `eww weekly` | The primary vault |
| `daily/folders.md` | The folders of `collections/` that may be resurfaced, one `- name` line for each. Optional. | `eww daily` | The primary vault |

`eww install` links suffix and home files. It does not copy them, so an edit in the vault applies at once. Run `eww install` again after you add or remove a file.

### `daily/folders.md`

`eww daily` reads only the folders named here. A folder that is not named is ignored, so a new folder stays out until you add it.

- One line of the form `- name` for each folder, for example `- book`.
- A `collections/` prefix and a trailing slash are allowed.
- Every other line is prose and is skipped.
- When the note is missing, the default list is used: `article`, `book`, `definition`, `highlight`, `lesson`, `quote`, `video`.

`eww daily --dry-run` prints the folders it reads and the folders it ignores.

## On each machine: `~/.config/eww/`

| Path | What it holds | Who writes it |
|---|---|---|
| `vault` | Notes vaults, one path per line. The first line is the primary vault. A path may start with `~/`. | You |
| `denylist.txt` | Private words that the leak-check commit hook blocks. It does not come from a vault. Without it, the hook is not installed. | You |
| `eww.zsh` | A link to the shared shell settings in the repo. | `eww install` |
| `private.zsh` | A link to the private shell settings in the primary vault, when that file exists. | `eww install` |
| `suffixes/` | Links to every suffix file in the listed vaults. | `eww install` |

Do not edit the linked files here. Edit the file in the repo or the vault.

`eww install` moves a file it did not create to `~/.local/state/eww/backup/<time>/` before it replaces it.

## In the repo

| Path | What it holds |
|---|---|
| `instructions/base.md` | The shared agent instructions. |
| `home/` | Shared home files: shell, prompt, editor, terminal, and git settings. |
| `skills/` | Own skills. |
| `skills.lock` | Third-party skills, pinned to a commit. |
| `obsidian/defaults/` | Obsidian starting settings, copied into a vault only where a file is missing. |

The repo is public. Personal details, employer content, hostnames, and secrets belong in a vault or in `~/.config/eww/`.

## Settings outside eww that eww reads

- `<vault>/.obsidian/daily-notes.json`: `eww daily` writes to the day-note this Obsidian setting names.

## Environment variables

| Variable | Effect | Used by |
|---|---|---|
| `EWW_HOME` | Use this folder in place of the home folder. For tests and trial installs. | Most programs |
| `EWW_AGENT` | The agent to start: `claude` (default), `pi`, or any kind herdr supports. | `eww h` |
| `EWW_REPOS_DIR` | Where repos live. The default is `~/Developer`. | `eww h` |
| `EWW_DEFINE_COMMAND` | The agent command for definitions. It reads the prompt on standard input. | `eww define` |
| `EWW_COURSE_COMMAND` | The agent command for lessons. | `eww course` |
| `EWW_WEEKLY_COMMAND` | The agent command for the weekly note. | `eww weekly` |
| `EWW_DENYLIST` | The denylist file, in place of `~/.config/eww/denylist.txt`. | The leak-check hook |
| `EWW_NO_COLOR`, `NO_COLOR` | Turn off colored output. | Shell programs |
| `EWW_REPO_URL`, `EWW_DIR` | Where to clone from and to. | `setup.sh` |
