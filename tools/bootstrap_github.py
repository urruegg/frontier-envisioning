#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Create and configure the GitHub repository and seed the intake backlog (people only).

  python tools/bootstrap_github.py --owner <user-or-org> [--repo frontier-envisioning] [--visibility private]
                                   [--approvals 1] [--skip-issues] [--apply]

Without --apply nothing changes: the script prints every command it would run (a dry run). With --apply it
runs them through Git and the GitHub CLI (gh, signed in with `gh auth login`) and continues when a
setting is not available on your GitHub plan, listing those at the end.

Steps
  1  git init and the import commit (when this folder is not yet a Git repository)
  2  gh repo create --source . --push (when the remote does not exist)
  3  merge settings: squash only, delete branches after merge
  4  security: Dependabot alerts and security updates, secret scanning and push protection
  5  ruleset 'main': pull request, code owner review, status check 'L1 quality gate', no force push, no deletion
  6  environments: dev (main only) and prod (main only, required reviewer: you)
  7  labels and milestones from backlog/backlog.json
  8  issues from backlog/issues/*.md (skipped when an issue with the same id prefix exists)
Then follow docs/engineering/github-setup.md for the settings that need the web UI (Copilot).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import ROOT, plugin_version  # noqa: E402

BACKLOG = ROOT / "backlog"
REQUIRED_CHECKS = ("L1 quality gate", "L2 browser tests", "IaC validation")


def read_issues() -> list[dict]:
    issues = []
    for p in sorted((BACKLOG / "issues").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if not m:
            raise SystemExit(f"{p}: missing frontmatter")
        meta = {}
        for line in m.group(1).splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
        labels = [x.strip() for x in meta.get("labels", "").strip("[]").split(",") if x.strip()]
        issues.append({"id": meta["id"], "title": meta["title"].strip('"'), "milestone": meta.get("milestone", "").strip('"'),
                       "labels": labels, "body": m.group(2).strip() + "\n"})
    return issues


def personalise(owner: str, repo: str, apply: bool) -> None:
    """Point CODEOWNERS and the issue-form links at the chosen owner (the starting point uses urruegg)."""
    edits = [(ROOT / ".github" / "CODEOWNERS", "@urruegg", f"@{owner}"),
             (ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml", "urruegg/frontier-envisioning", f"{owner}/{repo}")]
    if owner == "urruegg" and repo == "frontier-envisioning":
        print("references already point to urruegg/frontier-envisioning")
        return
    for path, old, new in edits:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        updated = re.sub(re.escape(old) + r"(?=\s|$)", new, text) if path.name == "CODEOWNERS" else text.replace(old, new)
        if updated != text:
            print(("updated " if apply else "would update ") + f"{path.relative_to(ROOT).as_posix()}: {old} -> {new}")
            if apply:
                path.write_text(updated, encoding="utf-8", newline="\n")
    print("note: for an organisation, replace the CODEOWNERS entry with a team (@org/team) in the first pull request")


class Runner:
    def __init__(self, apply: bool):
        self.apply = apply
        self.skipped: list[str] = []

    def __call__(self, cmd: list[str], stdin: str | None = None, ok_fail: str | None = None, capture=False, probe=False) -> str:
        shown = " ".join(c if re.fullmatch(r"[\w@./:=,+-]+", c) else json.dumps(c, ensure_ascii=False) for c in cmd)
        print(("$ " if self.apply else "would run: ") + shown + (" <<JSON" if stdin else ""))
        if not self.apply:
            return ""
        proc = subprocess.run(cmd, cwd=ROOT, input=stdin, capture_output=True, text=True, encoding="utf-8")
        if proc.returncode:
            msg = (proc.stderr or proc.stdout).strip().splitlines()[-1:] or ["failed"]
            if probe:
                return ""
            if ok_fail:
                print(f"  skipped: {ok_fail} ({msg[0]})")
                self.skipped.append(f"{ok_fail}: {msg[0]}")
                return ""
            raise SystemExit(f"command failed: {msg[0]}")
        return proc.stdout if capture else ""


def ruleset(approvals: int) -> dict:
    return {
        "name": "main", "target": "branch", "enforcement": "active",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "bypass_actors": [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request"}],
        "rules": [
            {"type": "deletion"}, {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {"required_approving_review_count": approvals, "dismiss_stale_reviews_on_push": True,
                                                    "require_code_owner_review": True, "require_last_push_approval": False,
                                                    "required_review_thread_resolution": True}},
            {"type": "required_status_checks", "parameters": {"strict_required_status_checks_policy": False,
                                                              "required_status_checks": [{"context": name} for name in REQUIRED_CHECKS]}},
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owner", required=True, help="GitHub user or organisation")
    ap.add_argument("--repo", default="frontier-envisioning")
    ap.add_argument("--visibility", choices=("private", "internal", "public"), default="private")
    ap.add_argument("--approvals", type=int, default=1, help="required approvals on main (admins can merge their own PRs through the bypass)")
    ap.add_argument("--skip-issues", action="store_true")
    ap.add_argument("--apply", action="store_true", help="make the changes (default: dry run)")
    a = ap.parse_args(argv)
    full = f"{a.owner}/{a.repo}"
    run = Runner(a.apply)
    for tool in ("git", "gh"):
        if a.apply and not shutil.which(tool):
            raise SystemExit(f"{tool} is required (GitHub CLI: https://cli.github.com, then gh auth login)")
    backlog = json.loads((BACKLOG / "backlog.json").read_text(encoding="utf-8"))
    issues = read_issues()
    print(f"# {'APPLY' if a.apply else 'DRY RUN'}: {full} ({a.visibility}), plugin {plugin_version()}, "
          f"{len(backlog['labels'])} labels, {len(backlog['milestones'])} milestones, {len(issues)} issues\n")

    print("## 0 Owner references")
    personalise(a.owner, a.repo, a.apply)

    print("\n## 1 Git")
    if not (ROOT / ".git").exists():
        run(["git", "init", "-b", "main"])
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", f"chore: import Frontier Envisioning {plugin_version()} as the engineering baseline"])
    else:
        print("already a Git repository")

    print("\n## 2 Repository")
    exists = bool(run(["gh", "repo", "view", full, "--json", "name"], capture=True, probe=True)) if a.apply else False
    if not exists:
        run(["gh", "repo", "create", full, f"--{a.visibility}", "--source", ".", "--remote", "origin", "--push",
             "--description", "Innovation Hub Frontier solution envisioning and architecture design - Copilot Cowork plugin, MIT"])

    print("\n## 3 Merge settings")
    run(["gh", "repo", "edit", full, "--enable-squash-merge", "--enable-merge-commit=false", "--enable-rebase-merge=false",
         "--delete-branch-on-merge", "--enable-wiki=false"], ok_fail="merge settings")

    print("\n## 4 Security")
    run(["gh", "api", "-X", "PUT", f"repos/{full}/vulnerability-alerts"], ok_fail="Dependabot alerts")
    run(["gh", "api", "-X", "PUT", f"repos/{full}/automated-security-fixes"], ok_fail="Dependabot security updates")
    run(["gh", "api", "-X", "PATCH", f"repos/{full}", "--input", "-"],
        stdin=json.dumps({"security_and_analysis": {"secret_scanning": {"status": "enabled"},
                                                    "secret_scanning_push_protection": {"status": "enabled"}}}),
        ok_fail="secret scanning (needs a public repository or GitHub Secret Protection)")

    print("\n## 5 Ruleset for main")
    existing = run(["gh", "api", f"repos/{full}/rulesets", "--jq", ".[].name"], ok_fail="list rulesets", capture=True) if a.apply else ""
    if "main" in existing.split():
        print("ruleset 'main' exists")
    else:
        run(["gh", "api", "-X", "POST", f"repos/{full}/rulesets", "--input", "-"], stdin=json.dumps(ruleset(a.approvals)),
            ok_fail="ruleset (private repositories need GitHub Pro, Team or Enterprise)")

    print("\n## 6 Environments")
    me = run(["gh", "api", "user", "--jq", ".id"], capture=True).strip() if a.apply else "<your user id>"
    run(["gh", "api", "-X", "PUT", f"repos/{full}/environments/dev", "--input", "-"],
        stdin=json.dumps({"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}}), ok_fail="environment dev")
    prod = {"deployment_branch_policy": {"protected_branches": True, "custom_branch_policies": False}}
    if me.isdigit():
        prod["reviewers"] = [{"type": "User", "id": int(me)}]
    run(["gh", "api", "-X", "PUT", f"repos/{full}/environments/prod", "--input", "-"], stdin=json.dumps(prod),
        ok_fail="environment prod with a required reviewer (private repositories need a paid plan)")

    print("\n## 7 Labels and milestones")
    for lab in backlog["labels"]:
        run(["gh", "label", "create", lab["name"], "--repo", full, "--color", lab["color"], "--description", lab["description"], "--force"],
            ok_fail=f"label {lab['name']}")
    have = run(["gh", "api", f"repos/{full}/milestones?state=all&per_page=100", "--jq", ".[].title"], ok_fail="list milestones",
               capture=True) if a.apply else ""
    titles = {m["key"]: m["title"] for m in backlog["milestones"]}
    for m in backlog["milestones"]:
        if m["title"] in have.splitlines():
            print(f"milestone '{m['title']}' exists")
            continue
        run(["gh", "api", "-X", "POST", f"repos/{full}/milestones", "--input", "-"],
            stdin=json.dumps({"title": m["title"], "description": m["description"]}), ok_fail=f"milestone {m['title']}")

    if not a.skip_issues:
        print("\n## 8 Issues")
        known = run(["gh", "issue", "list", "--repo", full, "--state", "all", "--limit", "500", "--json", "title", "--jq", ".[].title"],
                    ok_fail="list issues", capture=True) if a.apply else ""
        known_ids = {t.split(" · ", 1)[0] for t in known.splitlines()}
        for it in issues:
            if it["id"] in known_ids:
                print(f"issue {it['id']} exists")
                continue
            cmd = ["gh", "issue", "create", "--repo", full, "--title", f"{it['id']} · {it['title']}", "--body-file", "-"]
            for lab in it["labels"]:
                cmd += ["--label", lab]
            if it["milestone"]:
                cmd += ["--milestone", titles.get(it["milestone"], it["milestone"])]
            run(cmd, stdin=it["body"], ok_fail=f"issue {it['id']}")

    print("\n## Next (web UI): enable Copilot cloud agent and automatic Copilot code review, check Actions permissions,"
          " then follow docs/engineering/github-setup.md")
    if run.skipped:
        print("\nNot applied (plan limits or errors):")
        for s in run.skipped:
            print("  - " + s)
    if not a.apply:
        print("\nDry run only. Re-run with --apply to make these changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
