# Capabilities

Decisions behind this list are in `ADR.md`.

## Now

- **Notes cutover.** Applied on 2026-11-12. The Obsidian vault is the record. Awaiting one day of real use.
- **Launcher.** `eww` prints the map of every `eww-<verb>` program it finds and runs them. Aliases are symlinks.
- **`eww install`.** Links `home/` files and programs, deploys own and pinned third-party skills to Claude and Pi, builds instructions from the base plus local suffix files, installs the leak-check hook where a denylist exists. Existing files are backed up, never deleted.
- **`eww update`, `eww doctor`, `setup.sh`.**
- **Leak-check commit hook.** gitleaks plus a private denylist. Fails closed.

Tested with `make test` (59 checks in a temporary home folder) and `make lint`. Not yet tested: Ubuntu, a real install on a Mac, `setup.sh` end to end.

## In flight

2. **Repo, setup script, launcher.** The mechanism is built. Remaining: review and copy in the real content (`instructions/base.md`, `home/` files, skills, `skills.lock`), test on a fresh VPS, then install on a Mac. After that: `h` and `w`, `context`.

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
