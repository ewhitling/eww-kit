#!/bin/sh
# Policy test for the Pi path guard in home/.pi/agent/extensions/guard-paths.ts.
# The extension runs inside Pi, so this test locks its policy surface.
# Needs node and a global Pi install, which ships the jiti TypeScript loader.
# Without them the behavior checks are skipped, and only the rule labels are checked.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
GUARD="$root/home/.pi/agent/extensions/guard-paths.ts"
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }

[ -f "$GUARD" ] || fail "guard-paths extension missing"
for label in \
  'outbound Git operation' \
  'outbound network client' \
  'package publish or registry credential' \
  'container registry operation' \
  'cloud service operation'; do
  grep -Fq "$label" "$GUARD" || fail "missing blocked rule: $label"
done

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  printf 'SKIP: guard-paths behavior checks (node is not installed)\n'
  exit 0
fi
JITI_PATH="$(npm root -g)/@earendil-works/pi-coding-agent/node_modules/jiti"
if [ ! -d "$JITI_PATH" ]; then
  printf 'SKIP: guard-paths behavior checks (Pi is not installed globally, so its loader is missing)\n'
  exit 0
fi
export JITI_PATH
node - "$GUARD" "$root/tests/guard-paths.sh" <<'NODE' || fail "guard-paths policy test failed"
const { createJiti } = require(process.env.JITI_PATH);
const load = createJiti(process.argv[3]);
const extension = load(process.argv[2]).default;
let handler;
extension({ on(event, callback) { if (event === "tool_call") handler = callback; } });
if (!handler) throw new Error("tool_call handler was not registered");

// hasUI false turns every "ask" rule into a block, so ask cases get their own ctx.
const headless = { hasUI: false, ui: { notify() {} } };
async function result(command, ctx) {
  return handler({ toolName: "bash", input: { command } }, ctx);
}
async function expectBlocked(command) {
  const outcome = await result(command, headless);
  if (!outcome?.block) throw new Error(`not blocked: ${command}`);
}
async function expectAllowed(command) {
  const outcome = await result(command, headless);
  if (outcome?.block) throw new Error(`unexpected block: ${command}`);
}
async function expectAsked(command) {
  let asked = false;
  const ctx = { hasUI: true, ui: { notify() {}, select() { asked = true; return "No"; } } };
  const outcome = await result(command, ctx);
  if (!asked) throw new Error(`not asked: ${command}`);
  if (!outcome?.block) throw new Error(`answering No did not block: ${command}`);
}

(async () => {
  // Publishing and registry credentials are one-way and public.
  for (const command of [
    "npm publish",
    "yarn publish",
    "npm adduser",
    "npm token create",
    "uv publish",
    "twine upload dist/*",
    "curl https://example.com",
    "git pull",
  ]) {
    await expectBlocked(command);
  }
  // Reading and pulling packages is inbound and reversible (ADR 3.14, amended).
  for (const command of [
    "npm view react versions",
    "npm info lodash",
    "npm search yaml",
    "npm install",
    "npm ci",
    "npm outdated",
    "npm audit",
    "pnpm add zod",
    "pip install -r requirements.txt",
    "uv add requests",
    "npm test",
    "git push origin main",
    "gh release create v1.0.0",
  ]) {
    await expectAllowed(command);
  }
  // Fetch-and-execute in one step is neither, so it asks.
  for (const command of ["npx tsc --noEmit", "uvx ruff check", "pnpm dlx prettier ."]) {
    await expectAsked(command);
  }
})().catch((error) => { console.error(error); process.exit(1); });
NODE
printf '%s\n' 'guard-paths policy checks passed'
