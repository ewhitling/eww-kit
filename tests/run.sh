#!/bin/sh
# Tests for the launcher, install, update, doctor, and the leak-check hook.
# Everything runs against a copy of the repo and a temporary home folder.
# The real home folder is never touched.
set -eu

REPO=$(cd "$(dirname "$0")/.." && pwd -P)
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
export NO_COLOR=1

passed=0
failed=0
check() {
  description=$1
  shift
  if "$@" >/dev/null 2>&1; then
    passed=$((passed + 1))
  else
    failed=$((failed + 1))
    printf 'FAIL: %s\n' "$description"
  fi
}
contains() { printf '%s' "$1" | grep -q -F -- "$2"; }
is_link_to() { [ -L "$1" ] && [ "$(readlink "$1")" = "$2" ]; }

# A copy of the repo with fixture content, so the tests do not depend on real content.
COPY=$WORK/repo
mkdir -p "$COPY"
(cd "$REPO" && tar cf - --exclude .git .) | (cd "$COPY" && tar xf -)
COPY=$(cd "$COPY" && pwd -P)
mkdir -p "$COPY/home/.config/demo" "$COPY/skills/own-skill" "$COPY/instructions"
printf 'demo setting\n' >"$COPY/home/.config/demo/settings"
printf 'rc file\n' >"$COPY/home/.demorc"
printf '# Own skill\n' >"$COPY/skills/own-skill/SKILL.md"
printf '# Base instructions\n' >"$COPY/instructions/base.md"
ln -s eww-doctor "$COPY/bin/eww-alias"

# A local git repo that stands in for a third-party skill source.
UPSTREAM=$WORK/upstream
mkdir -p "$UPSTREAM/pack/their-skill"
printf '# Their skill v1\n' >"$UPSTREAM/pack/their-skill/SKILL.md"
git -C "$UPSTREAM" init -q
git -C "$UPSTREAM" -c user.name=t -c user.email=t@example.com add -A
git -C "$UPSTREAM" -c user.name=t -c user.email=t@example.com commit -q -m one
PINNED=$(git -C "$UPSTREAM" rev-parse HEAD)
printf '# Their skill v2\n' >"$UPSTREAM/pack/their-skill/SKILL.md"
git -C "$UPSTREAM" -c user.name=t -c user.email=t@example.com commit -q -am two
printf 'their-skill %s %s pack/their-skill\n' "$UPSTREAM" "$PINNED" >>"$COPY/skills.lock"

# A home folder that already holds files eww did not create.
export EWW_HOME="$WORK/home"
mkdir -p "$EWW_HOME/.claude/skills/own-skill" "$EWW_HOME/.config/eww/suffixes/skills" "$EWW_HOME/.local/bin"
printf 'old rc\n' >"$EWW_HOME/.demorc"
printf 'hand-written instructions\n' >"$EWW_HOME/.claude/CLAUDE.md"
printf 'old skill\n' >"$EWW_HOME/.claude/skills/own-skill/SKILL.md"
printf 'not ours\n' >"$EWW_HOME/.claude/skills/untouched.md"
printf '## Personal\n' >"$EWW_HOME/.config/eww/suffixes/10-personal.md"
printf '## Work\n' >"$EWW_HOME/.config/eww/suffixes/20-work.md"
printf 'Skill suffix line\n' >"$EWW_HOME/.config/eww/suffixes/skills/own-skill.md"
ln -s "$WORK/missing.md" "$EWW_HOME/.config/eww/suffixes/30-dangling.md"

# --- install ---------------------------------------------------------------
first_run=$("$COPY/bin/eww-install" 2>&1) || true
check "install exits 0" "$COPY/bin/eww-install"
check "home file is linked" is_link_to "$EWW_HOME/.demorc" "$COPY/home/.demorc"
check "nested home file is linked" is_link_to "$EWW_HOME/.config/demo/settings" "$COPY/home/.config/demo/settings"
check "launcher is linked" is_link_to "$EWW_HOME/.local/bin/eww" "$COPY/bin/eww"
check "program is linked" is_link_to "$EWW_HOME/.local/bin/eww-install" "$COPY/bin/eww-install"
check "existing rc file was backed up" sh -c "grep -q -r 'old rc' '$EWW_HOME/.local/state/eww/backup'"
check "existing instructions were backed up" sh -c "grep -q -r 'hand-written instructions' '$EWW_HOME/.local/state/eww/backup'"
check "existing skill folder was backed up" sh -c "grep -q -r 'old skill' '$EWW_HOME/.local/state/eww/backup'"
check "unrelated file in skills folder is untouched" grep -q 'not ours' "$EWW_HOME/.claude/skills/untouched.md"
check "first run reports the backups" contains "$first_run" "moved existing"
check "first run warns about the dangling suffix" contains "$first_run" "30-dangling.md"

claude_file=$(cat "$EWW_HOME/.claude/CLAUDE.md")
check "instructions start with the marker" sh -c "head -n 1 '$EWW_HOME/.claude/CLAUDE.md' | grep -q 'Built by eww install'"
check "instructions hold the base" contains "$claude_file" "# Base instructions"
check "instructions hold the personal suffix" contains "$claude_file" "## Personal"
check "instructions hold the work suffix" contains "$claude_file" "## Work"
check "suffixes are in name order" sh -c "grep -n '## ' '$EWW_HOME/.claude/CLAUDE.md' | tr '\n' ' ' | grep -q 'Personal.*Work'"
check "Pi gets the same instructions" cmp -s "$EWW_HOME/.claude/CLAUDE.md" "$EWW_HOME/.pi/agent/AGENTS.md"

check "own skill with a suffix is a built copy" is_link_to "$EWW_HOME/.claude/skills/own-skill" "$EWW_HOME/.local/share/eww/built-skills/own-skill"
check "built skill keeps the original text" grep -q '# Own skill' "$EWW_HOME/.claude/skills/own-skill/SKILL.md"
check "built skill ends with the suffix" grep -q 'Skill suffix line' "$EWW_HOME/.claude/skills/own-skill/SKILL.md"
check "repo skill file is not changed by the suffix" sh -c "! grep -q 'Skill suffix line' '$COPY/skills/own-skill/SKILL.md'"
check "Pi gets the skill" test -f "$EWW_HOME/.pi/agent/skills/own-skill/SKILL.md"
check "third-party skill is at the pinned commit" grep -q 'v1' "$EWW_HOME/.claude/skills/their-skill/SKILL.md"
check "hook is skipped with no denylist" sh -c "! test -e '$COPY/.git/hooks/pre-commit'"

# --- install again ---------------------------------------------------------
backups_before=$(find "$EWW_HOME/.local/state/eww/backup" -type f | wc -l)
second_run=$("$COPY/bin/eww-install" 2>&1)
backups_after=$(find "$EWW_HOME/.local/state/eww/backup" -type f | wc -l)
check "second run makes no new backups" test "$backups_before" -eq "$backups_after"
check "second run makes no new links" contains "$second_run" "install complete: 0 new link(s)"

# A changed suffix is picked up, and eww's own output is replaced with no backup.
printf '## Personal changed\n' >"$EWW_HOME/.config/eww/suffixes/10-personal.md"
"$COPY/bin/eww-install" >/dev/null 2>&1
check "changed suffix is rebuilt" grep -q 'Personal changed' "$EWW_HOME/.claude/CLAUDE.md"
check "rebuild makes no backup" test "$backups_before" -eq "$(find "$EWW_HOME/.local/state/eww/backup" -type f | wc -l)"

# A skill removed from the repo loses its link.
rm "$EWW_HOME/.config/eww/suffixes/skills/own-skill.md"
"$COPY/bin/eww-install" >/dev/null 2>&1
check "skill without a suffix links to the repo" is_link_to "$EWW_HOME/.claude/skills/own-skill" "$COPY/skills/own-skill"
rm -rf "$COPY/skills/own-skill"
"$COPY/bin/eww-install" >/dev/null 2>&1
check "removed skill loses its link" sh -c "! test -L '$EWW_HOME/.claude/skills/own-skill'"

# A third-party skill that cannot be fetched makes install fail.
cp "$COPY/skills.lock" "$WORK/skills.lock.saved"
printf 'broken-skill %s/nowhere 0000000000000000000000000000000000000000\n' "$WORK" >>"$COPY/skills.lock"
check "unfetchable skill makes install fail" sh -c "! '$COPY/bin/eww-install'"
cp "$WORK/skills.lock.saved" "$COPY/skills.lock"

# --- launcher --------------------------------------------------------------
mkdir -p "$WORK/extra"
printf '#!/bin/sh\n# eww: work | A machine-only command.\necho "local ran: $*"\n' >"$WORK/extra/eww-local"
printf '#!/bin/sh\necho plain\n' >"$WORK/extra/eww-plain"
chmod +x "$WORK/extra/eww-local" "$WORK/extra/eww-plain"
PATH_FOR_TEST=$WORK/extra:$EWW_HOME/.local/bin:$PATH

map=$(PATH=$PATH_FOR_TEST "$EWW_HOME/.local/bin/eww")
check "bare eww prints the map" contains "$map" "mise-en-place"
check "map lists install with its summary" contains "$map" "Install everything. Safe to run again."
check "map has the place group" contains "$map" "─ place"
check "map lists a program found only on the path" contains "$map" "A machine-only command."
check "map puts a program with no description under other" sh -c "printf '%s' \"\$1\" | grep -A3 '─ other' | grep -q plain" _ "$map"
check "map leaves aliases out" sh -c "! printf '%s' \"\$1\" | grep -q 'alias'" _ "$map"
check "map lists each verb once" test "$(printf '%s\n' "$map" | grep -c '  install ')" -eq 1
check "eww help prints the map" sh -c "PATH='$PATH_FOR_TEST' '$COPY/bin/eww' help | grep -q 'mise-en-place'"
check "eww version prints the version" sh -c "'$COPY/bin/eww' version | grep -q \"^eww \$(cat '$COPY/VERSION')\$\""
check "verb arguments are passed through" sh -c "PATH='$PATH_FOR_TEST' '$COPY/bin/eww' local a 'b c' | grep -q 'local ran: a b c'"
check "an alias runs its target" sh -c "PATH='$PATH_FOR_TEST' '$COPY/bin/eww' alias --help | grep -q 'eww doctor'"
check "eww help <verb> shows that verb's help" sh -c "'$COPY/bin/eww' help install | grep -q 'Safe to run again'"
check "unknown verb exits 1" sh -c "'$COPY/bin/eww' nonsense; test \$? -eq 1"
check "unknown verb names the verb" sh -c "'$COPY/bin/eww' nonsense 2>&1 | grep -q 'unknown command \"nonsense\"'"

# --- doctor ----------------------------------------------------------------
doctor=$(PATH=$PATH_FOR_TEST "$COPY/bin/eww-doctor" 2>&1) || true
check "doctor sees the linked programs" contains "$doctor" "programs linked"
check "doctor sees eww-built instructions" contains "$doctor" ".claude/CLAUDE.md was built by eww"
check "doctor reports the dangling suffix" contains "$doctor" "30-dangling.md points at a missing file"
check "doctor exits 1 when something is broken" sh -c "! PATH='$PATH_FOR_TEST' '$COPY/bin/eww-doctor'"
rm "$EWW_HOME/.config/eww/suffixes/30-dangling.md"
check "doctor treats a machine with no denylist as pull-only" sh -c "PATH='$PATH_FOR_TEST' '$COPY/bin/eww-doctor' | grep -q 'pull-only'"

# --- update ----------------------------------------------------------------
ORIGIN=$WORK/origin
CLONE=$WORK/clone
cp -R "$COPY" "$ORIGIN"
git -C "$ORIGIN" init -q
git -C "$ORIGIN" -c user.name=t -c user.email=t@example.com add -A
git -C "$ORIGIN" -c user.name=t -c user.email=t@example.com commit -q -m base
git clone -q "$ORIGIN" "$CLONE"
CLONE=$(cd "$CLONE" && pwd -P)
printf '# Base instructions, updated\n' >"$ORIGIN/instructions/base.md"
git -C "$ORIGIN" -c user.name=t -c user.email=t@example.com commit -q -am change
check "update pulls and installs" "$CLONE/bin/eww-update"
check "update brings the new base into the instructions" grep -q 'Base instructions, updated' "$EWW_HOME/.claude/CLAUDE.md"
check "update relinks programs to the pulled checkout" is_link_to "$EWW_HOME/.local/bin/eww" "$CLONE/bin/eww"

# --- leak-check hook -------------------------------------------------------
if command -v gitleaks >/dev/null 2>&1; then
  printf '# comment\n\nSecretProjectName\n' >"$EWW_HOME/.config/eww/denylist.txt"
  "$CLONE/bin/eww-install" >/dev/null 2>&1
  check "hook is installed when a denylist exists" is_link_to "$CLONE/.git/hooks/pre-commit" "$CLONE/hooks/pre-commit"
  commit() { EWW_DENYLIST=$EWW_HOME/.config/eww/denylist.txt git -C "$CLONE" -c user.name=t -c user.email=t@example.com commit -q -m "$1"; }
  printf 'a harmless line\n' >"$CLONE/notes.txt"
  git -C "$CLONE" add notes.txt
  check "hook allows a clean commit" commit clean
  printf 'this mentions secretprojectname in lower case\n' >>"$CLONE/notes.txt"
  git -C "$CLONE" add notes.txt
  check "hook refuses denylisted text, ignoring case" sh -c "! EWW_DENYLIST='$EWW_HOME/.config/eww/denylist.txt' git -C '$CLONE' -c user.name=t -c user.email=t@example.com commit -q -m bad"
  git -C "$CLONE" reset -q --hard
  printf 'x\n' >"$CLONE/SecretProjectName.txt"
  git -C "$CLONE" add SecretProjectName.txt
  check "hook refuses a denylisted file name" sh -c "! EWW_DENYLIST='$EWW_HOME/.config/eww/denylist.txt' git -C '$CLONE' -c user.name=t -c user.email=t@example.com commit -q -m bad"
  git -C "$CLONE" reset -q --hard
  # Built at run time so this test file holds no key-shaped text itself.
  printf 'aws_secret_access_key = "%s%s"\n' 'wJalrXUtnFEMI/K7MDENG/' 'bPxRfiCYzT9qLmN2vKpQ' >"$CLONE/config.txt"
  git -C "$CLONE" add config.txt
  check "hook refuses a secret found by gitleaks" sh -c "! EWW_DENYLIST='$EWW_HOME/.config/eww/denylist.txt' git -C '$CLONE' -c user.name=t -c user.email=t@example.com commit -q -m bad"
  git -C "$CLONE" reset -q --hard
  printf 'fine\n' >>"$CLONE/notes.txt"
  git -C "$CLONE" add notes.txt
  check "hook refuses when the denylist is missing" sh -c "! EWW_DENYLIST='$WORK/none.txt' git -C '$CLONE' -c user.name=t -c user.email=t@example.com commit -q -m bad"
else
  printf 'SKIP: leak-check hook tests (gitleaks is not installed)\n'
fi

printf '%s passed, %s failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
