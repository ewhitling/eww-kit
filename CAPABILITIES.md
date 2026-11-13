# Capabilities

Decisions behind this list are in `ADR.md`.

## Now

- **Notes cutover.** Applied on 2026-11-12. The Obsidian vault is the record. Awaiting one day of real use.
- **Launcher.** `eww` prints the map of every `eww-<verb>` program it finds and runs them. Aliases are symlinks.
- **Private files from the vault.** A machine with `~/.config/eww/vault` gets private home files and suffixes from the vault's `_meta/eww/` folder.
- **Shared settings.** zsh settings, the starship prompt, the nvim config, and a global git ignore file are in `home/`.
- **Skills.** 17 own skills in `skills/` and 33 pinned third-party skills in `skills.lock`.
- **`eww install`.** Links `home/` files and programs, deploys own and pinned third-party skills to Claude and Pi, builds instructions from the base plus local suffix files, installs the leak-check hook where a denylist exists. Existing files are backed up, never deleted.
- **`eww update`, `eww doctor`, `setup.sh`.**
- **`eww h` (alias `eww w`).** Opens a herdr workspace for a repo, a vault project, or the vault: agent on the left, `eww context` on the right. Bare `eww h` opens the repo around the current folder, or shows a picker. `eww h stop` stops the herdr server.
- **`eww context`.** Lists what an agent session in a folder loads, with token estimates.
- **Leak-check commit hook.** gitleaks plus a private denylist. Fails closed.

Tested with `make test` (112 checks in a temporary home folder; herdr is replaced by a stand-in), `make lint`, and a trial install into a temporary home using the real vault. Installed for real on one Mac on 2026-11-12; `eww doctor` passes there, and `eww h`, the numbered picker, and the map colors work in real use. Not yet tested: Ubuntu, `setup.sh` end to end, the `fzf` picker.

## In flight

2. **Repo, setup script, launcher.** Built, published, and installed on one Mac. Remaining: the fresh VPS test, one day of real use, then archive the old tool repos.

## Next

3. **Design tokens.** One token file and generators for CSS, Obsidian, terminal, editor, and charts.
4. **`eww daily`.** Three resurfaced items in the day-note.
5. **`eww weekly`.** Up to five rising concepts from primary sources. `eww define` ships with it or just after.
6. **Lab design session.**

## To verify before relying on it

- Obsidian Sync carries CSS snippets and plugin settings.
- Obsidian Sync can sign in on a pull-only machine without any other personal account.
- Where Pi reads instructions and skills.

## Done means

One day of real use with no interface change.
