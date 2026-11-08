#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Check an extracted Frontier Envisioning package and print the Copilot Cowork install plan.

Copilot Cowork runs this when a user uploads the plugin zip and says
"Install the Frontier PlugIn" (see README.md, section "For Copilot Cowork").

Usage:
  python install/prepare_install.py --root working/frontier-plugin
         [--installed /mnt/user-config/skills]

Checks, without changing anything:
  * install/plugin-install.json is present and names this plugin;
  * every file it lists exists under the package root with the recorded SHA-256;
  * every skill folder holds a SKILL.md whose frontmatter name equals the folder name;
  * no file outside the list sits in a skill folder (a repacked or altered package).
Then compares with the skills already installed for the user (read-only) and prints JSON:
  {"plugin", "version", "verified", "problems", "skills": [{"name", "source", "destination",
   "files", "status": "new|update|reinstall", "installed_version"}], "copy_calls", "after_install"}
Exit code 0 = ready to install, 1 = the package is damaged or incomplete, 2 = usage error.
Standard library only; reads files, writes nothing, no network access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PLUGIN = "frontier-envisioning"
DEFAULT_INSTALLED = "/mnt/user-config/skills"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def frontmatter(p: Path) -> dict:
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    out: dict = {}
    if not m:
        return out
    block = m.group(1)
    nm = re.search(r"(?m)^name:\s*(\S+)\s*$", block)
    if nm:
        out["name"] = nm.group(1).strip("'\"")
    ver = re.search(r"(?m)^\s+version:\s*['\"]?([0-9][\w.\-]*)['\"]?\s*$", block)
    if ver:
        out["version"] = ver.group(1)
    return out


def workspace_relative(root: Path, given: str) -> str:
    """CopyArtifact takes workspace-relative paths such as working/frontier-plugin/..."""
    g = given.replace("\\", "/").rstrip("/")
    if not g.startswith("/"):
        return g[2:] if g.startswith("./") else g
    idx = g.find("/working/")
    return g[idx + 1:] if idx >= 0 else g


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="folder the package was extracted to, e.g. working/frontier-plugin")
    ap.add_argument("--installed", default=DEFAULT_INSTALLED, help="the user's installed skills folder (read-only)")
    a = ap.parse_args(argv)
    root = Path(a.root)
    plan_file = root / "install" / "plugin-install.json"
    given = a.root
    if not plan_file.is_file():
        # Run from another working directory: fall back to the package this script sits in.
        here = Path(__file__).resolve().parent.parent
        if (here / "install" / "plugin-install.json").is_file():
            root, given = here, str(here)
            plan_file = root / "install" / "plugin-install.json"
    if not plan_file.is_file():
        print(json.dumps({"verified": False, "problems": [f"{plan_file} not found: extract the whole zip, keeping its folders"]}, indent=1))
        return 2
    try:
        spec = json.loads(plan_file.read_text(encoding="utf-8"))
    except ValueError as e:
        print(json.dumps({"verified": False, "problems": [f"plugin-install.json is not valid JSON: {e}"]}, indent=1))
        return 1

    problems: list[str] = []
    if spec.get("plugin") != PLUGIN:
        problems.append(f"this installer is for {PLUGIN}, the package says {spec.get('plugin')!r}")
    rel_root = workspace_relative(root, given)
    installed_dir = Path(a.installed)
    skills_out = []
    for sk in spec.get("skills", []):
        name, folder, files = sk.get("name"), sk.get("folder"), sk.get("files") or {}
        base = root / folder
        if not base.is_dir():
            problems.append(f"{folder} is missing")
            continue
        for rel, digest in files.items():
            f = base / rel
            if not f.is_file():
                problems.append(f"{folder}/{rel} is missing")
            elif sha256(f) != digest:
                problems.append(f"{folder}/{rel} differs from the released file (checksum)")
        listed = set(files)
        extra = sorted(p.relative_to(base).as_posix() for p in base.rglob("*")
                       if p.is_file() and "__pycache__" not in p.parts and p.relative_to(base).as_posix() not in listed)
        if extra:
            problems.append(f"{folder} holds files that are not part of the release: {', '.join(extra[:5])}")
        fm = frontmatter(base / "SKILL.md") if (base / "SKILL.md").is_file() else {}
        if fm.get("name") != name:
            problems.append(f"{folder}/SKILL.md name {fm.get('name')!r} does not match {name!r}")
        status, inst_ver = "new", None
        inst = installed_dir / name / "SKILL.md"
        try:
            if inst.is_file():
                inst_ver = frontmatter(inst).get("version")
                status = "reinstall" if inst_ver == spec.get("version") else "update"
        except OSError:
            status = "unknown"
        skills_out.append({"name": name, "source": f"{rel_root}/{folder}", "destination": f"skills/{name}",
                           "files": len(files), "status": status, "installed_version": inst_ver})

    verified = not problems and bool(skills_out)
    calls = [f'CopyArtifact(surface="user", source="{s["source"]}", destination="{s["destination"]}", recursive=true, overwrite=true)  # expect copied={s["files"]}'
             for s in skills_out]
    result = {
        "plugin": spec.get("plugin"), "display_name": spec.get("display_name"), "version": spec.get("version"),
        "verified": verified, "problems": problems, "skills": skills_out,
        "copy_calls": calls if verified else [],
        "after_install": ("Installed. Start a new Cowork chat (after OneDrive has synced) and try: "
                          + " | ".join(spec.get("start_prompts", []))) if verified else
                         "Do not install: re-download the original zip and upload it again without unpacking or repacking it.",
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
