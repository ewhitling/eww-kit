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
mkdir -p "$COPY/home/.config/eww"
printf '# test shell settings\n' >"$COPY/home/.config/eww/eww.zsh"
printf '# Own skill\n' >"$COPY/skills/own-skill/SKILL.md"
printf '# Base instructions\n' >"$COPY/instructions/base.md"
ln -s eww-doctor "$COPY/bin/eww-alias"

# A local git repo that stands in for a third-party skill source.
UPSTREAM=$WORK/upstream
mkdir -p "$UPSTREAM/pack/their-skill"
printf '# Their skill v1\n' >"$UPSTREAM/pack/their-skill/SKILL.md"
mkdir -p "$UPSTREAM/pack/their-other"
printf '# Their other skill\n' >"$UPSTREAM/pack/their-other/SKILL.md"
git -C "$UPSTREAM" init -q
git -C "$UPSTREAM" -c user.name=t -c user.email=t@example.com add -A
git -C "$UPSTREAM" -c user.name=t -c user.email=t@example.com commit -q -m one
PINNED=$(git -C "$UPSTREAM" rev-parse HEAD)
printf '# Their skill v2\n' >"$UPSTREAM/pack/their-skill/SKILL.md"
git -C "$UPSTREAM" -c user.name=t -c user.email=t@example.com commit -q -am two
# The test uses its own lock file, so it never reaches the network.
: >"$COPY/skills.lock"
printf 'their-skill %s %s pack/their-skill\n' "$UPSTREAM" "$PINNED" >>"$COPY/skills.lock"
printf 'their-other %s %s pack/their-other\n' "$UPSTREAM" "$PINNED" >>"$COPY/skills.lock"

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
check "second third-party skill from the same source is deployed" grep -q 'other skill' "$EWW_HOME/.claude/skills/their-other/SKILL.md"
check "skills from one source and commit share one clone" test "$(find "$EWW_HOME/.local/share/eww/third-party" -mindepth 1 -maxdepth 1 -type d | wc -l)" -eq 1
check "hook is skipped with no denylist" sh -c "! test -e '$COPY/.git/hooks/pre-commit'"

check "a missing ~/.zshrc is created with the loading line" grep -q '.config/eww/eww.zsh' "$EWW_HOME/.zshrc"

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

# A vault path file links the vault's suffix files, for instructions and for skills.
mkdir -p "$WORK/vault/_meta/eww/skills"
printf '## From the vault\n' >"$WORK/vault/_meta/eww/40-vault.md"
printf 'Vault skill suffix\n' >"$WORK/vault/_meta/eww/skills/their-skill.md"
printf '%s\n' "$WORK/vault" >"$EWW_HOME/.config/eww/vault"
"$COPY/bin/eww-install" >/dev/null 2>&1
check "vault suffix is linked" is_link_to "$EWW_HOME/.config/eww/suffixes/40-vault.md" "$WORK/vault/_meta/eww/40-vault.md"
check "vault suffix reaches the instructions" grep -q 'From the vault' "$EWW_HOME/.claude/CLAUDE.md"
check "vault skill suffix reaches a third-party skill" grep -q 'Vault skill suffix' "$EWW_HOME/.claude/skills/their-skill/SKILL.md"
# Private home files in the vault are linked, and win over a repo file at the same path.
mkdir -p "$WORK/vault/_meta/eww/home/.config/demo"
printf 'private git settings\n' >"$WORK/vault/_meta/eww/home/.privaterc"
printf 'private demo setting\n' >"$WORK/vault/_meta/eww/home/.config/demo/settings"
"$COPY/bin/eww-install" >/dev/null 2>&1
check "private home file from the vault is linked" is_link_to "$EWW_HOME/.privaterc" "$WORK/vault/_meta/eww/home/.privaterc"
check "private file wins over the repo file" grep -q 'private demo setting' "$EWW_HOME/.config/demo/settings"
check "repo files without a private twin stay linked" is_link_to "$EWW_HOME/.demorc" "$COPY/home/.demorc"
links_before=$(find "$EWW_HOME/.local/state/eww/backup" | wc -l)
"$COPY/bin/eww-install" >/dev/null 2>&1
check "private override is stable across runs" test "$links_before" -eq "$(find "$EWW_HOME/.local/state/eww/backup" | wc -l)"
rm -rf "$WORK/vault/_meta/eww/home"
rm "$EWW_HOME/.privaterc" "$EWW_HOME/.config/demo/settings"
"$COPY/bin/eww-install" >/dev/null 2>&1
check "repo file returns when the private twin is removed" is_link_to "$EWW_HOME/.config/demo/settings" "$COPY/home/.config/demo/settings"

# The loading line is added once, and an existing ~/.zshrc keeps its content.
check "loading line appears once after many runs" test "$(grep -c '.config/eww/eww.zsh' "$EWW_HOME/.zshrc")" -eq 1
printf 'export KEEP_ME=1\n' >"$EWW_HOME/.zshrc"
"$COPY/bin/eww-install" >/dev/null 2>&1
check "existing ~/.zshrc content is kept" grep -q 'KEEP_ME' "$EWW_HOME/.zshrc"
check "loading line is appended to an existing ~/.zshrc" grep -q '.config/eww/eww.zsh' "$EWW_HOME/.zshrc"

printf '%s\n' "$WORK/no-such-vault" >"$EWW_HOME/.config/eww/vault"
check "a missing vault does not stop install" "$COPY/bin/eww-install"
rm "$EWW_HOME/.config/eww/vault"

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

# --- h, w, and context -----------------------------------------------------
# A stand-in for herdr records each call, so the tests never touch a real session.
STUB=$WORK/stub
mkdir -p "$STUB"
cat >"$STUB/herdr" <<'STUB_HERDR'
#!/bin/sh
printf '%s\n' "${*:-attach}" >>"$HERDR_LOG"
case "${1:-} ${2:-}" in
  "status server") [ -n "${STUB_SERVER_DOWN:-}" ] || echo "status: running" ;;
  "workspace list")
    if [ -n "${STUB_EXISTING:-}" ]; then
      printf '{"result":{"workspaces":[{"label":"%s","workspace_id":"ws9"}]}}\n' "$STUB_EXISTING"
    else
      echo '{"result":{"workspaces":[]}}'
    fi
    ;;
  "workspace create") echo '{"result":{"workspace":{"workspace_id":"ws1"},"root_pane":{"pane_id":"p1"}}}' ;;
  "pane split") echo '{"result":{"pane":{"pane_id":"p2"}}}' ;;
esac
STUB_HERDR
chmod +x "$STUB/herdr"
export HERDR_LOG="$WORK/herdr.log"
export EWW_REPOS_DIR="$WORK/repos"
mkdir -p "$EWW_REPOS_DIR/demo-repo/sub" "$EWW_REPOS_DIR/my.repo" "$EWW_REPOS_DIR/not-a-repo" "$WORK/vault2/projects/side-project"
git -C "$EWW_REPOS_DIR/demo-repo" init -q
git -C "$EWW_REPOS_DIR/my.repo" init -q
REPOS_REAL=$(cd "$EWW_REPOS_DIR" && pwd -P)
printf '%s\n' "$WORK/vault2" >"$EWW_HOME/.config/eww/vault"
run_h() { (PATH="$STUB:$PATH" HERDR_PANE_ID=inside "$COPY/bin/eww-h" "$@"); }
logged() { grep -q -F -- "$1" "$HERDR_LOG"; }

if command -v jq >/dev/null 2>&1; then
  : >"$HERDR_LOG"
  check "h NAME opens the repo" run_h demo-repo
  sleep 1
  check "h creates the workspace in the repo folder" logged "workspace create --cwd $EWW_REPOS_DIR/demo-repo --label demo-repo --no-focus"
  check "h splits a pane to the right" logged "pane split p1 --direction right"
  check "h runs context in the right pane" logged "pane run p2 $COPY/bin/eww-context"
  check "h starts claude in the left pane" logged "agent start demo-repo --kind claude --pane p1"
  check "h focuses the workspace" logged "workspace focus ws1"
  check "h does not attach when already inside herdr" sh -c "! grep -q -x attach '$HERDR_LOG'"

  : >"$HERDR_LOG"
  check "h focuses an existing workspace" sh -c "STUB_EXISTING=demo-repo PATH='$STUB':\"\$PATH\" HERDR_PANE_ID=inside '$COPY/bin/eww-h' demo-repo"
  check "an existing workspace is not created again" sh -c "! grep -q 'workspace create' '$HERDR_LOG'"
  check "the existing workspace id is focused" logged "workspace focus ws9"

  : >"$HERDR_LOG"
  check "h with no target opens the repo around the current folder" sh -c "cd '$EWW_REPOS_DIR/demo-repo/sub' && PATH='$STUB':\"\$PATH\" HERDR_PANE_ID=inside '$COPY/bin/eww-h'"
  check "the repo root is used, not the sub-folder" logged "workspace create --cwd $REPOS_REAL/demo-repo --label demo-repo"

  : >"$HERDR_LOG"
  check "h vault opens the vault" run_h vault
  check "the vault folder is used" logged "workspace create --cwd $WORK/vault2 --label vault2"

  : >"$HERDR_LOG"
  check "h NAME finds a vault project" run_h side-project
  check "the project folder is used" logged "--cwd $WORK/vault2/projects/side-project --label side-project"

  : >"$HERDR_LOG"
  check "a dot in the name becomes a dash in the label" sh -c "PATH='$STUB':\"\$PATH\" HERDR_PANE_ID=inside '$COPY/bin/eww-h' my.repo && grep -q -- '--label my-repo' '$HERDR_LOG'"

  : >"$HERDR_LOG"
  check "EWW_AGENT picks the agent" sh -c "EWW_AGENT=pi PATH='$STUB':\"\$PATH\" HERDR_PANE_ID=inside '$COPY/bin/eww-h' demo-repo && sleep 1 && grep -q -- '--kind pi' '$HERDR_LOG'"

  : >"$HERDR_LOG"
  check "outside herdr, h attaches after focusing" sh -c "PATH='$STUB':\"\$PATH\" HERDR_PANE_ID= '$COPY/bin/eww-h' demo-repo && grep -q -x attach '$HERDR_LOG'"

  : >"$HERDR_LOG"
  check "w is an alias for h" sh -c "PATH='$STUB':\"\$PATH\" HERDR_PANE_ID=inside '$COPY/bin/eww' w demo-repo && grep -q 'workspace focus ws1' '$HERDR_LOG'"

  check "a folder that is not a repo is not a target" sh -c "! PATH='$STUB':\"\$PATH\" '$COPY/bin/eww-h' not-a-repo"
  check "an unknown name exits 1 and says so" sh -c "PATH='$STUB':\"\$PATH\" '$COPY/bin/eww-h' nope 2>&1 | grep -q 'is not a repo'"
  check "an unknown option exits 2" sh -c "PATH='$STUB':\"\$PATH\" '$COPY/bin/eww-h' --bogus; test \$? -eq 2"

  : >"$HERDR_LOG"
  check "h stop stops the server" run_h stop
  check "the stop call reaches herdr" logged "server stop"
  : >"$HERDR_LOG"
  check "h stop does nothing when the server is down" sh -c "STUB_SERVER_DOWN=1 PATH='$STUB':\"\$PATH\" '$COPY/bin/eww-h' stop | grep -q 'not running' && ! grep -q 'server stop' '$HERDR_LOG'"
else
  printf 'SKIP: h tests (jq is not installed)\n'
fi
rm "$EWW_HOME/.config/eww/vault"

PROJECT=$WORK/ctx-project
mkdir -p "$PROJECT/.claude/skills/local-skill" "$PROJECT/.claude/agents"
printf 'project rules\n' >"$PROJECT/CLAUDE.md"
printf 'a reviewer\n' >"$PROJECT/.claude/agents/reviewer.md"
printf '{"mcpServers":{"alpha":{},"beta":{}}}\n' >"$PROJECT/.mcp.json"
printf '{"hooks":{"SessionStart":[]}}\n' >"$PROJECT/.claude/settings.json"
PROJECT_REAL=$(cd "$PROJECT" && pwd)
memory_dir=$EWW_HOME/.claude/projects/$(printf '%s' "$PROJECT_REAL" | sed 's|[^A-Za-z0-9]|-|g')/memory
mkdir -p "$memory_dir"
printf -- '- one\n- two\n' >"$memory_dir/MEMORY.md"
context=$("$COPY/bin/eww-context" "$PROJECT")
check "context names the folder" contains "$context" "session in ctx-project loads"
check "context marks instructions built by eww" contains "$context" "(built by eww)"
check "context counts the project instructions" sh -c "printf '%s' \"\$1\" | grep 'project' | grep -q '1 lines'" _ "$context"
check "context reports a missing file as none" sh -c "printf '%s' \"\$1\" | grep 'local' | grep -q '(none)'" _ "$context"
check "context counts memory entries" contains "$context" "2 entries"
check "context lists project skills" contains "$context" "local-skill"
check "context lists project agents" contains "$context" "reviewer"
check "context reports the preload total" contains "$context" "preload"
if command -v jq >/dev/null 2>&1; then
  check "context lists MCP servers" contains "$context" "alpha, beta"
  check "context lists hook events" contains "$context" "SessionStart"
fi
check "context defaults to the current folder" sh -c "cd '$PROJECT' && '$COPY/bin/eww-context' | grep -q 'ctx-project'"
check "context fails on a missing folder" sh -c "! '$COPY/bin/eww-context' '$WORK/no-such-folder'"

printf '%s passed, %s failed\n' "$passed" "$failed"
[ "$failed" -eq 0 ]
