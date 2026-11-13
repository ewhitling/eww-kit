# Capabilities

Decisions behind this list are in `ADR.md`.

## Now

- **Notes cutover.** Applied on 2026-11-12. The Obsidian vault is the record. Awaiting one day of real use.
- **Launcher.** `eww` prints the map of every `eww-<verb>` program it finds and runs them. Aliases are symlinks.
- **Private files from the vault.** `~/.config/eww/vault` lists one vault per line. The first is the primary and supplies private home files. Every listed vault supplies suffixes from its `_meta/eww/` folder.
- **Shared settings.** zsh settings, the starship prompt, the nvim config, Ghostty settings, and a global git ignore file are in `home/`.
- **Skills.** 17 own skills in `skills/` and 33 pinned third-party skills in `skills.lock`.
- **`eww install`.** Links `home/` files and programs, deploys own and pinned third-party skills to Claude and Pi, builds instructions from the base plus local suffix files, installs the leak-check hook where a denylist exists. Existing files are backed up, never deleted.
- **`eww update`, `eww doctor`, `setup.sh`.** `eww doctor` also reports when the published repo has newer commits. Nothing pulls on a schedule.
- **`eww h` (alias `eww w`).** Opens a herdr workspace for a repo, a vault project, or the vault: agent on the left, `eww context` on the right. Bare `eww h` opens the repo around the current folder, or shows a picker. `eww h stop` stops the herdr server.
- **`eww context`.** Lists what an agent session in a folder loads, with token estimates.
- **Leak-check commit hook.** gitleaks plus a private denylist. Fails closed.
- **Theme generator.** `make themes` writes every house-style export from `skills/house-style/tokens/tokens.json`: CSS, chart styles, Swift, Streamlit, Ghostty themes, the nvim color scheme, and the palette of the Hood plugin for Obsidian. `make test` fails when an export is out of date.
- **Hood plugin for Obsidian.** Kept in `obsidian/plugins/hood/`. `eww install` copies it into the vault on machines that name one.
- **Obsidian starting settings.** `make obsidian-snapshot` copies the vault's settings into `obsidian/defaults/`. `eww install` copies them, and the Atom theme, into a vault only where a file is missing.

Tested with `make test` (145 checks in a temporary home folder, with herdr replaced by a stand-in, plus the export check and 36 tests for the generator, the snapshot, and `eww daily`), `make lint`, and a trial install into a temporary home using the real vault. Installed for real on one Mac on 2026-11-12; `eww doctor` passes there, and `eww h`, the numbered picker, and the map colors work in real use. Not yet tested: Ubuntu, `setup.sh` end to end, the `fzf` picker. Hood's hand-written CSS rules and cursor code have no tests here.

## In flight

2. **Repo, setup script, launcher.** Built, published, and installed on one Mac. Remaining: the fresh VPS test, one day of real use, then archive the old tool repos.
3. **Design tokens.** The generator, the Ghostty themes, the Hood palette, and an nvim color scheme are done. Remaining: one day of real use.
4. **`eww daily`.** Built and tested, with a dry run on the real vault. It adds three passages from `collections/` to the day-note that Obsidian's Daily notes setting names, uses no LLM, and keeps no state outside the vault. Remaining: the first real write, one day of hand use, then a schedule.

## Next

5. **`eww weekly`.** Up to five rising concepts from primary sources. `eww define` ships with it or just after.
6. **Lab design session.**

## To verify before relying on it

- Obsidian Sync carries CSS snippets and plugin settings.
- Obsidian Sync can sign in on a pull-only machine without any other personal account.
- Where Pi reads instructions and skills.

## Done means

One day of real use with no interface change.
