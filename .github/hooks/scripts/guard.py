#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""preToolUse guardrail for GitHub Copilot agents in this repository (Copilot CLI and Copilot cloud agent).

Reads the hook payload (JSON on stdin) and denies tool calls that are human-only or would break the
repository's rules. Allowed calls print nothing (default behaviour). A denial prints
{"permissionDecision": "deny", "permissionDecisionReason": "..."} so the agent learns what to do instead.

Human-only (decided by people, executed by people or by workflows with approvals):
  merging pull requests, approving reviews, releases and release tags, force pushes, pushes to main,
  repository settings, secrets and variables, labels that mark readiness or approval, Azure changes and
  deployments, running workflows by hand, bypassing commit hooks.
Protected files: the guardrails themselves (.github/hooks), CODEOWNERS, the licence, the release and
deployment workflows, release manifests, the neutrality denylist, vendored third-party skills and every
generated file (edit the source and run the generator instead).
Content: no real customer names (tools/neutrality-denylist.txt); the demo company is Caldova.

Robustness: an unexpected error allows the call and reports it on stderr (a crashing preToolUse hook
would deny every tool call). Covered by tests/unit/test_guard_hook.py. Standard library only.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROTECTED_LABELS = re.compile(r"(^|,)\s*(status:ready|approved:[\w-]+)\s*(,|$)")
PROTECTED_FILES = [
    (re.compile(r"^\.github/hooks/"), "the agent guardrails are maintained by people"),
    (re.compile(r"^\.github/CODEOWNERS$"), "code ownership is maintained by people"),
    (re.compile(r"^(LICENSE|plugin/MIT\.md)$"), "the licence is maintained by people"),
    (re.compile(r"^\.github/workflows/(release|azure-dev)\.yml$"), "the release and deployment workflows are maintained by people"),
    (re.compile(r"^releases/"), "release manifests are written after a release by the release manager"),
    (re.compile(r"^tools/neutrality-denylist\.txt$"), "use 'python tools/neutrality.py add' (people only)"),
    (re.compile(r"^\.agents/skills/"), "vendored third-party skills change only through tools/superpowers.py"),
    (re.compile(r"^plugin/skills/frontier-blueprint/templates/frontier-blueprint-template\.html$"),
     "this file is generated: edit src/renderer/* and run 'python tools/dev.py template'"),
    (re.compile(r"^plugin/install/plugin-install\.json$"), "this file is generated: run 'python tools/dev.py package'"),
    (re.compile(r"^(dist|build)/"), "build output: run the build instead of editing it"),
]
EDIT_TOOLS = {"create", "edit", "write", "multiedit", "str_replace_editor", "str_replace_based_edit_tool", "apply_patch",
              "notebookedit", "insert", "replace", "editfiles", "createfile"}
SHELL_TOOLS = {"bash", "powershell", "shell", "execute", "run_in_terminal", "runinterminal"}
PATH_KEYS = ("path", "file_path", "filePath", "target_file", "filename", "file", "notebook_path")
CONTENT_KEYS = ("file_text", "content", "new_str", "new_string", "newText", "new_text", "text", "insert_text", "code")
SECRET_VARS = re.compile(r"\$\{?(GITHUB_COPILOT_\w+|GITHUB_TOKEN|GH_TOKEN|COPILOT_\w*TOKEN\w*|AZURE_CLIENT_SECRET|AAD_CLIENT_SECRET|"
                         r"\w*_SECRET\w*|\w*PASSWORD\w*)\b|\$env:(GITHUB_\w*TOKEN|\w*SECRET\w*|\w*PASSWORD\w*)", re.I)


def deny(reason: str) -> dict:
    return {"permissionDecision": "deny", "permissionDecisionReason": reason}


def rel_path(raw: str, cwd: str | None) -> str:
    p = Path(raw)
    if not p.is_absolute():
        p = Path(cwd or REPO) / p
    try:
        return p.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return p.as_posix()


def strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


# --------------------------------------------------------------------------- shell commands
def split_commands(cmd: str) -> list[list[str]]:
    """Split a shell line into simple commands (on ; && || | and newlines) and tokenise each."""
    parts = re.split(r"(?:&&|\|\||;|\n|\|)", cmd)
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            tokens = shlex.split(part, posix=True)
        except ValueError:
            tokens = part.split()
        while tokens and re.fullmatch(r"\w+=\S*", tokens[0]):  # leading VAR=value
            tokens = tokens[1:]
        while tokens and tokens[0] in ("sudo", "env", "command", "exec", "time", "nohup"):
            tokens = tokens[1:]
        if tokens:
            out.append(tokens)
    return out


def check_git(t: list[str]) -> str | None:
    sub = next((x for x in t[1:] if not x.startswith("-")), "")
    rest = t[t.index(sub) + 1:] if sub in t else []
    if "--no-verify" in t or (sub == "commit" and "-n" in rest):
        return "commit hooks are part of the quality gate L0: do not bypass them with --no-verify"
    if sub == "config" and any(x.startswith("core.hooksPath") for x in rest):
        return "do not change the Git hooks path"
    if sub == "push":
        if any(x in ("--force", "-f", "--force-with-lease", "--mirror", "--delete", "-d", "--prune") or x.startswith("--force")
               for x in rest):
            return "force, mirror and delete pushes are human-only; push a new commit to your branch instead"
        refs = [x for x in rest if not x.startswith("-")]
        for ref in refs[1:] if len(refs) > 1 else []:
            if ref.startswith("+") or ref.startswith(":"):
                return "force and delete refspecs are human-only"
            target = ref.split(":")[-1].removeprefix("refs/heads/")
            if target in ("main", "master"):
                return "main is protected: push your branch and open a pull request"
            if re.fullmatch(r"(refs/tags/)?v\d+(\.\d+)*.*", target):
                return "release tags are created by the release manager (a person), not by agents"
        if "--tags" in rest or "--follow-tags" in rest:
            return "release tags are created by the release manager (a person), not by agents"
    if sub == "tag":
        listing = any(x in ("-l", "--list", "-n", "--contains", "--points-at", "--merged", "--no-merged") for x in rest)
        names = [x for x in rest if not x.startswith("-")]
        if not listing and names:
            return "release tags are created by the release manager (a person), not by agents"
    if sub == "clean" and any(re.fullmatch(r"-\w*[xX]\w*", x) for x in rest):
        return "git clean -x would delete ignored local files (dependencies, environments); clean specific paths instead"
    return None


def check_gh(t: list[str]) -> str | None:
    if len(t) < 2:
        return None
    group, action = t[1], (t[2] if len(t) > 2 else "")
    args = t[3:]
    if group == "pr" and action == "merge":
        return "merging is human-only: request a review and leave the pull request open"
    if group == "pr" and action == "review" and any(x in ("--approve", "-a") for x in args):
        return "approvals are human-only"
    if group == "release" and action in ("create", "delete", "edit", "upload", "delete-asset"):
        return "releases are human-only: prepare the release pull request and hand over to the release manager"
    if group == "repo" and action in ("delete", "edit", "archive", "rename", "unarchive", "set-default"):
        return "repository settings are human-only"
    if group in ("secret", "variable", "ruleset", "auth"):
        return f"'gh {group}' is human-only in agent sessions"
    if group == "label" and action in ("create", "edit", "delete", "clone"):
        return "labels are managed by tools/bootstrap_github.py (people)"
    if group == "workflow" and action in ("run", "enable", "disable"):
        return "workflows run on their triggers; deployments and releases are started by people"
    if group in ("issue", "pr") and action in ("edit", "create"):
        for i, x in enumerate(args):
            val = None
            if x in ("--add-label", "--remove-label", "--label", "-l"):
                val = args[i + 1] if i + 1 < len(args) else ""
            elif x.startswith(("--add-label=", "--remove-label=", "--label=")):
                val = x.split("=", 1)[1]
            if val is not None and PROTECTED_LABELS.search(val):
                return "readiness and approval labels (status:ready, approved:*) are set by people"
    if group == "api":
        method = None
        for i, x in enumerate(t[2:], 2):
            if x in ("-X", "--method") and i + 1 < len(t):
                method = t[i + 1].upper()
            elif x.startswith("--method="):
                method = x.split("=", 1)[1].upper()
            elif re.fullmatch(r"-X[A-Za-z]+", x):
                method = x[2:].upper()
        writes = any(x in ("-f", "-F", "--field", "--raw-field", "--input") or x.startswith(("--field=", "--raw-field=", "--input="))
                     for x in t[2:])
        if (method and method != "GET") or (writes and method != "GET"):
            return "write calls to the GitHub API are human-only in agent sessions (read with GET)"
    return None


def check_repo_tool(t: list[str]) -> str | None:
    """Repository tools whose effect is human-only even though they run as a script."""
    joined = " ".join(t)
    if "Initialize-GitHubRepo" in joined or ("bootstrap_github.py" in joined and "--apply" in t):
        return "bootstrapping the GitHub repository (settings, rulesets, labels, issues) is done by people; a dry run is fine"
    if "superpowers.py" in joined and any(x in ("vendor", "install-user") for x in t):
        return "installing or vendoring third-party skills is a human decision (ENG-D2); 'status' and 'verify' are fine"
    if "neutrality.py" in joined and "add" in t:
        return "the neutrality denylist is maintained by people"
    return None


def check_shell(cmd: str) -> str | None:
    if SECRET_VARS.search(cmd):
        return "do not read tokens or secrets in agent sessions"
    low = cmd.lower()
    if re.search(r"\b(curl|wget|iwr|invoke-webrequest)\b[^|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", low) or \
            re.search(r"\biex\b|\binvoke-expression\b", low):
        return "piping downloads into a shell is not allowed: download, review and run a pinned script instead"
    for t in split_commands(cmd):
        exe = Path(t[0]).name.lower().removesuffix(".exe")
        if exe == "git":
            r = check_git(t)
        elif exe == "gh":
            r = check_gh(t)
        elif exe == "azd":
            r = None if len(t) > 1 and t[1] in ("version", "--version", "help", "--help", "config") and "set" not in t else \
                "Azure provisioning and deployment run in the azure-dev workflow with approvals, not in agent sessions"
        elif exe == "az":
            r = None if len(t) > 1 and (t[1] in ("bicep", "version", "--version", "help", "--help")) and "install" not in t[1:] \
                and "upgrade" not in t[1:] else "Azure changes run in the azure-dev workflow; agents may use 'az bicep build' and 'az bicep lint'"
        elif exe == "rm":
            flags = "".join(x for x in t[1:] if x.startswith("-"))
            targets = [x for x in t[1:] if not x.startswith("-")]
            r = None
            if ("r" in flags.lower() or "--recursive" in t) and any(
                    x in ("/", "/*", "~", "~/", "*", ".", "..", "./", "$HOME", ".git", "./.git", "/workspace") or x.startswith(".git/")
                    for x in targets):
                r = "this recursive delete would remove the repository or the home folder"
            elif any(rel_path(x, None).startswith(".github/hooks") for x in targets):
                r = "the agent guardrails are maintained by people"
        elif exe in ("sed", "perl", "mv", "cp", "tee", "truncate", "chmod") and any(
                ".github/hooks" in x for x in t[1:]):
            r = "the agent guardrails are maintained by people"
        elif exe.startswith("python") or exe in ("py", "pwsh", "powershell") or exe.endswith(".ps1"):
            r = check_repo_tool(t)
        else:
            r = None
        if r:
            return r
    return None


# --------------------------------------------------------------------------- file edits
def edit_targets(args: dict, cwd: str | None) -> list[str]:
    paths = []
    for k in PATH_KEYS:
        v = args.get(k)
        if isinstance(v, str) and v:
            paths.append(rel_path(v, cwd))
    for s in strings(args):
        for m in re.finditer(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$|^\*\*\* Move to: (.+)$", s, re.M):
            paths.append(rel_path((m.group(1) or m.group(2)).strip(), cwd))
    return paths


def new_content(args: dict) -> str:
    chunks = [args[k] for k in CONTENT_KEYS if isinstance(args.get(k), str)]
    for s in strings(args):
        if s.startswith("*** Begin Patch"):
            chunks += [ln[1:] for ln in s.splitlines() if ln.startswith("+") and not ln.startswith("+++")]
    edits = args.get("edits")
    if isinstance(edits, list):
        chunks += [e.get("new_string", "") for e in edits if isinstance(e, dict)]
    return "\n".join(chunks)


def neutrality_hits(text: str) -> list:
    if not text.strip():
        return []
    sys.path.insert(0, str(REPO / "tools"))
    try:
        import neutrality  # noqa: PLC0415
        return neutrality.find_terms(text)
    finally:
        sys.path.pop(0)


def check_edit(args: dict, cwd: str | None) -> str | None:
    for p in edit_targets(args, cwd):
        for rx, why in PROTECTED_FILES:
            if rx.search(p):
                return f"{p}: {why}"
    hits = neutrality_hits(new_content(args))
    if hits:
        return ("real customer names must not enter the repository (found: " + ", ".join(sorted({h[1] for h in hits}))
                + "); use the fictitious Caldova Industrial AG")
    return None


# --------------------------------------------------------------------------- entry point
def decide(payload: dict) -> dict | None:
    name = str(payload.get("toolName") or payload.get("tool_name") or "").lower()
    args = payload.get("toolArgs", payload.get("tool_input", {}))
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {"command": args}
    if not isinstance(args, dict):
        args = {}
    cwd = payload.get("cwd")
    reason = None
    if name in SHELL_TOOLS:
        cmd = args.get("command") or args.get("cmd") or args.get("script") or ""
        reason = check_shell(cmd if isinstance(cmd, str) else " ".join(map(str, cmd)))
    elif name in EDIT_TOOLS or any(k in args for k in CONTENT_KEYS):
        reason = check_edit(args, cwd)
    return deny(reason) if reason else None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        result = decide(payload if isinstance(payload, dict) else {})
        if result:
            print(json.dumps(result))
    except Exception as e:  # noqa: BLE001 - never crash: a crashing preToolUse hook denies every call
        print(f"guard: internal error, call allowed ({type(e).__name__}: {e})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
