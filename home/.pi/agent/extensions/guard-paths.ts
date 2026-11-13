/**
 * Guard Paths Extension
 *
 * Credential stores are never written. Hard block, no prompt.
 * System paths and destructive local actions require confirmation.
 * Known outbound network commands are blocked, except `gh` and `git push`.
 * Reading and installing packages is allowed; publishing them is not.
 *
 * Coverage:
 *   - `write` and `edit` are checked by resolved path. Reliable.
 *   - `bash` is checked by scanning command text. This blocks known network
 *     clients and package publishing, but it is not an OS firewall.
 *     A determined command can still evade this. For real enforcement you
 *     need an OS sandbox that denies network access.
 *
 * Linked by `eww install` to ~/.pi/agent/extensions/guard-paths.ts.
 * `eww doctor` reports it as broken when Pi is installed and the guard is missing.
 * Disable for one run with `pi --no-extension guard-paths`.
 */

import { existsSync, realpathSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, isAbsolute, resolve, sep } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

type Rule = { label: string; dir: string; mode: "block" | "ask" };

const HOME = homedir();

const AGENT_DIR = process.env.PI_CODING_AGENT_DIR
	? resolve(process.env.PI_CODING_AGENT_DIR)
	: resolve(HOME, ".pi", "agent");

const RULES: Rule[] = [
	{ label: "~/.ssh", dir: resolve(HOME, ".ssh"), mode: "block" },
	{ label: "~/.gnupg", dir: resolve(HOME, ".gnupg"), mode: "block" },
	{ label: "~/.aws", dir: resolve(HOME, ".aws"), mode: "block" },
	{ label: "~/.kube", dir: resolve(HOME, ".kube"), mode: "block" },
	{ label: "~/.docker/config.json", dir: resolve(HOME, ".docker", "config.json"), mode: "block" },
	{ label: "~/.netrc", dir: resolve(HOME, ".netrc"), mode: "block" },
	{ label: "~/.pypirc", dir: resolve(HOME, ".pypirc"), mode: "block" },
	{ label: "~/.npmrc", dir: resolve(HOME, ".npmrc"), mode: "block" },
	{ label: "~/.git-credentials", dir: resolve(HOME, ".git-credentials"), mode: "block" },
	{ label: "~/.config/gh", dir: resolve(HOME, ".config", "gh"), mode: "block" },
	{ label: "~/.config/gcloud", dir: resolve(HOME, ".config", "gcloud"), mode: "block" },
	{ label: "~/.config/1Password", dir: resolve(HOME, ".config", "1Password"), mode: "block" },
	{ label: "~/Library/Keychains", dir: resolve(HOME, "Library", "Keychains"), mode: "block" },
	{ label: "/etc", dir: "/etc", mode: "ask" },
	{ label: "/Library", dir: "/Library", mode: "ask" },
	{ label: "/System", dir: "/System", mode: "ask" },
	{ label: "/usr", dir: "/usr", mode: "ask" },
	{ label: "~/Library/LaunchAgents", dir: resolve(HOME, "Library", "LaunchAgents"), mode: "ask" },
	{ label: "~/.zshrc", dir: resolve(HOME, ".zshrc"), mode: "ask" },
	{ label: "~/.gitconfig", dir: resolve(HOME, ".gitconfig"), mode: "ask" },
	{ label: "~/.pi/agent", dir: AGENT_DIR, mode: "ask" },
];

/** Resolve a path the way the tool will see it: expand ~, make absolute, follow symlinks. */
function canonical(raw: string, cwd: string): string {
	let p = raw.trim();
	if (p === "~") p = HOME;
	else if (p.startsWith("~/")) p = resolve(HOME, p.slice(2));
	if (!isAbsolute(p)) p = resolve(cwd, p);

	// Follow symlinks on the deepest ancestor that exists, so a symlinked
	// parent cannot be used to sneak into a guarded directory.
	let probe = p;
	const tail: string[] = [];
	while (!existsSync(probe)) {
		const parent = dirname(probe);
		if (parent === probe) return p;
		tail.unshift(probe.slice(parent.length + 1));
		probe = parent;
	}
	try {
		return resolve(realpathSync(probe), ...tail);
	} catch {
		return p;
	}
}

function isInside(target: string, dir: string): boolean {
	return target === dir || target.startsWith(dir + sep);
}

function ruleFor(path: string, cwd: string): Rule | undefined {
	const target = canonical(path, cwd);
	return RULES.find((r) => isInside(target, r.dir));
}

/** Shell tokens that can create or modify a file. Used for the bash heuristic. */
const WRITE_TOKENS =
	/(^|[\s;&|(`])(rm|mv|cp|tee|touch|mkdir|chmod|chown|ln|truncate|dd|sed\s+-i|install|shred|unlink|rsync)(\s|$)|>>?[^&]/;

type BashRule = { label: string; test: RegExp; mode: "block" | "ask" };

const BASH_RULES: BashRule[] = [
	// `gh` is deliberately exempt. It is the reviewed GitHub workflow.
	// `git push` is exempt for the same reason, but every other remote Git
	// command is blocked because it opens an outbound connection.
	{ label: "outbound Git operation", test: /(?:^|[;&|]\s*)git(?:\s+(?:-C\s+\S+|--git-dir=\S+|--work-tree=\S+))*\s+(?!(?:push)\b)(?:pull|fetch|clone|ls-remote|submodule\s+update|remote\s+(?:add|remove|rename|set-url)|config\s+remote\.)\b/, mode: "block" },
	{ label: "outbound network client", test: /\b(?:curl|wget|httpie|xh|aria2c|nc|ncat|netcat|ssh|scp|sftp)\b|\bopen\s+https?:\/\//, mode: "block" },
	// Package rules split by direction. Publishing is one-way and public, so it
	// is blocked. Fetching is inbound and reversible, so reads and installs are
	// allowed. Fetch-and-execute in one step sits between the two and asks.
	{ label: "package publish or registry credential", test: /\b(?:npm|pnpm|yarn)\s+(?:npm\s+)?(?:publish|unpublish|deprecate|login|logout|adduser|token|access|owner|dist-tag)\b|\b(?:uv|twine|poetry|flit)\s+(?:publish|upload)\b/, mode: "block" },
	{ label: "container registry operation", test: /\b(?:docker|podman)\s+(?:push|pull|login|logout|search)\b/, mode: "block" },
	{ label: "cloud service operation", test: /\b(?:aws|gcloud|az|kubectl)\b/, mode: "block" },
	{ label: "remote package execution", test: /\b(?:npx|bunx|uvx)\b|\b(?:pnpm|yarn)\s+dlx\b|\bpipx\s+run\b/, mode: "ask" },
	{ label: "destructive Git operation", test: /(?:^|[;&|]\s*)git(?:\s+-C\s+\S+)*\s+(?:clean\b|reset\s+--hard\b|branch\s+-[dD]\b)/, mode: "ask" },
	{ label: "recursive deletion outside the project", test: /\brm\b[^;\n]*(?:^|\s)(?:\/|~|\$HOME)(?:\/|\s|$)/, mode: "ask" },
	{ label: "machine service change", test: /\b(?:sudo|launchctl)\b|\bdefaults\s+write\b/, mode: "ask" },
];

/** Ways a command could name a guarded directory. */
function bashRefs(dir: string, label: string): RegExp {
	const literal = dir.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
	const short = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
	return new RegExp(`(${literal}|${short}|\\$HOME/${short.replace(/^~\//, "")})`);
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_call", async (event, ctx) => {
		const cwd = process.cwd();
		let rule: Rule | undefined;
		let what = "";

		if (event.toolName === "write" || event.toolName === "edit") {
			const path = event.input.path as string | undefined;
			if (!path) return undefined;
			rule = ruleFor(path, cwd);
			what = path;
		} else if (event.toolName === "bash") {
			const command = event.input.command as string | undefined;
			if (!command) return undefined;
			const bashRule = BASH_RULES.find((r) => r.test.test(command));
			if (bashRule) rule = { ...bashRule, dir: "" };
			else if (WRITE_TOKENS.test(command)) rule = RULES.find((r) => bashRefs(r.dir, r.label).test(command));
			what = command;
		} else {
			return undefined;
		}

		if (!rule) return undefined;

		// Path rules name a directory; command rules name an action. Word the
		// message for whichever one matched, so an `npx` prompt does not say "write".
		const subject = rule.dir ? `write to ${rule.label}` : rule.label;

		if (rule.mode === "block") {
			if (ctx.hasUI) ctx.ui.notify(`Blocked ${subject}`, "warning");
			return { block: true, reason: `${subject} is blocked by guard-paths` };
		}

		// mode "ask"
		if (!ctx.hasUI) {
			return { block: true, reason: `${subject} needs confirmation, and there is no UI` };
		}

		const choice = await ctx.ui.select(`Allow ${subject}?\n\n  ${what}`, ["No", "Yes"]);
		if (choice !== "Yes") {
			return { block: true, reason: "Blocked by user" };
		}

		return undefined;
	});
}
