#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Install or vendor the Superpowers skills (obra/superpowers, MIT) at a pinned version.

Superpowers is the engineering method this repository uses with GitHub Copilot: brainstorming, writing
plans, test-driven development, systematic debugging, verification before completion, code review and
finishing a branch. See docs/engineering/copilot-and-superpowers.md.

  python tools/superpowers.py status
  python tools/superpowers.py install-user  [--version v7.0.2] [--source URL|PATH]
        copy the skills into ~/.copilot/skills (personal skills: VS Code agent mode and Copilot CLI)
  python tools/superpowers.py vendor        [--version v7.0.2] [--source URL|PATH]
        copy the skills into .agents/skills/ with a lock file, so Copilot cloud agent sessions on
        GitHub Actions (which do not load personal skills) follow the same method; commit the result
        only after decision ENG-D2 (see backlog)
  python tools/superpowers.py verify
        check the vendored skills against .agents/skills/superpowers.lock.json (CI)

For Copilot CLI the plugin route is simpler and keeps hooks:  copilot plugin marketplace add obra/superpowers-marketplace
then  copilot plugin install superpowers@superpowers-marketplace
Needs git and network access to github.com (or --source with a local clone). Standard library only.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import ROOT, sha256_file  # noqa: E402

DEFAULT_VERSION = "v7.0.2"
DEFAULT_SOURCE = "https://github.com/obra/superpowers.git"
VENDOR_DIR = ROOT / ".agents" / "skills"
LOCK = VENDOR_DIR / "superpowers.lock.json"
NOTICE = "Superpowers (https://github.com/obra/superpowers) - MIT License - Copyright (c) Jesse Vincent and contributors"


def fetch(source: str, version: str, workdir: Path) -> tuple[Path, str]:
    dest = workdir / "superpowers"
    subprocess.run(["git", "-c", "advice.detachedHead=false", "clone", "--quiet", "--depth", "1", "--branch", version, source, str(dest)],
                   check=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=dest, capture_output=True, text=True, check=True).stdout.strip()
    if not (dest / "skills").is_dir():
        raise SystemExit("the source has no skills/ folder")
    return dest, commit


def copy_skills(src: Path, target: Path) -> list[str]:
    names = []
    target.mkdir(parents=True, exist_ok=True)
    for d in sorted(p for p in (src / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        out = target / d.name
        if out.exists():
            shutil.rmtree(out)
        shutil.copytree(d, out)
        names.append(d.name)
    return names


def lock_for(target: Path, names: list[str], version: str, commit: str, source: str) -> dict:
    files = {}
    for n in names:
        for p in sorted((target / n).rglob("*")):
            if p.is_file():
                files[p.relative_to(target).as_posix()] = sha256_file(p)
    return {"name": "superpowers", "version": version, "commit": commit, "source": source, "license": "MIT",
            "notice": NOTICE, "skills": names, "files": files}


def cmd_install(args, vendor: bool) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        src, commit = fetch(args.source, args.version, Path(tmp))
        if vendor:
            target = VENDOR_DIR
            names = copy_skills(src, target)
            if (src / "LICENSE").exists():
                shutil.copyfile(src / "LICENSE", target / "SUPERPOWERS-LICENSE")
            LOCK.write_text(json.dumps(lock_for(target, names, args.version, commit, args.source), indent=1) + "\n",
                            encoding="utf-8", newline="\n")
            print(f"vendored {len(names)} Superpowers skills {args.version} ({commit[:12]}) into .agents/skills")
        else:
            home = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot")
            names = copy_skills(src, home / "skills")
            print(f"installed {len(names)} Superpowers skills {args.version} into {home / 'skills'}")
    return 0


def cmd_verify() -> int:
    if not LOCK.exists():
        print("no vendored Superpowers skills (personal install or Copilot CLI plugin in use)")
        return 0
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    bad = [rel for rel, h in lock["files"].items() if not (VENDOR_DIR / rel).exists() or sha256_file(VENDOR_DIR / rel) != h]
    extra = [p.relative_to(VENDOR_DIR).as_posix() for n in lock["skills"] for p in (VENDOR_DIR / n).rglob("*")
             if p.is_file() and p.relative_to(VENDOR_DIR).as_posix() not in lock["files"]]
    for rel in bad:
        print("CHANGED " + rel)
    for rel in extra:
        print("EXTRA   " + rel)
    print(f"Superpowers {lock['version']}: {len(lock['files']) - len(bad)} of {len(lock['files'])} files match the lock")
    return 1 if bad or extra else 0


def cmd_status() -> int:
    home = Path(os.environ.get("COPILOT_HOME") or Path.home() / ".copilot") / "skills"
    personal = sorted(p.name for p in home.iterdir() if (p / "SKILL.md").exists()) if home.exists() else []
    vendored = json.loads(LOCK.read_text(encoding="utf-8")) if LOCK.exists() else None
    print(json.dumps({"personal_skills_dir": str(home), "personal_skills": personal,
                      "vendored": {"version": vendored["version"], "skills": vendored["skills"]} if vendored else None,
                      "copilot_cli": shutil.which("copilot") is not None}, indent=1))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("install-user", "vendor"):
        s = sub.add_parser(name)
        s.add_argument("--version", default=DEFAULT_VERSION)
        s.add_argument("--source", default=DEFAULT_SOURCE)
    sub.add_parser("verify")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    if a.cmd == "verify":
        return cmd_verify()
    if a.cmd == "status":
        return cmd_status()
    if not shutil.which("git"):
        print("git is required")
        return 1
    return cmd_install(a, vendor=(a.cmd == "vendor"))


if __name__ == "__main__":
    sys.exit(main())
