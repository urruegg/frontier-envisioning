#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Build the distributable package of the Frontier Envisioning plugin.

Usage (from the repository root):
  python tools/build_package.py [--dist dist]

The plugin lives in plugin/ (the packaged unit). Produces:
  dist/frontier-envisioning-plugin-<version>.zip   THE package to share. Upload it in a Copilot Cowork
                                                   chat and say "Install the Frontier PlugIn" (plugin/README.md).
                                                   It is also a valid Microsoft 365 (MOS3) plugin package
                                                   for the organisation catalogue:
                                                     README.md, MIT.md, THIRD-PARTY-NOTICES.md, manifest.json, color.png, outline.png,
                                                     install/plugin-install.json, install/prepare_install.py,
                                                     skills/<name>/...
  dist/SHA256SUMS.txt                              checksum of the package

The source archive of a release is the Git tag (GitHub attaches it to every release); the complete
bundle is built by tools/build_release.py.

Checks before packaging: every manifest agentSkills folder exists and holds a SKILL.md whose
frontmatter name equals the folder name and whose metadata version equals the release version;
no skill folder is left out of the manifest; manifest.json and .claude-plugin/plugin.json carry the
same version. Writes plugin/install/plugin-install.json (file list with SHA-256 per skill) into the
repository and the package; CI fails when the committed copy is stale. Entries carry a fixed date,
so the same sources always give the same bytes. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
SKIP_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache", "dist"}
FIXED_DATE = (2026, 11, 8, 0, 0, 0)
START_PROMPTS = [
    "Prepare the Frontier envisioning for <customer>, workshop on <date>",
    "Build the Frontier blueprint demo for Caldova",
    "Build the identity kit demo for Caldova",
    "Build the value case for <customer>",
    "What will the <customer> agents cost per month?",
    "Gather the customer context for <customer>",
    "Prepare the IT readiness and architecture design workshop for <customer>",
]


def files_under(folder: Path):
    for p in sorted(folder.rglob("*"), key=lambda path: path.relative_to(folder).as_posix()):
        rel = p.relative_to(PLUGIN).parts
        if p.is_file() and not (set(rel) & SKIP_PARTS) and not p.name.endswith((".pyc", ".new")):
            yield p


def add_bytes(zf: zipfile.ZipFile, data: bytes, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, data)


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    out = {}
    if m:
        nm = re.search(r"(?m)^name:\s*(\S+)\s*$", m.group(1))
        ver = re.search(r"(?m)^\s+version:\s*['\"]?([0-9][\w.\-]*)['\"]?\s*$", m.group(1))
        out = {"name": nm.group(1) if nm else None, "version": ver.group(1) if ver else None}
    return out


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dist", default=str(ROOT / "dist"))
    a = ap.parse_args(argv)
    manifest = json.loads((PLUGIN / "package" / "manifest.json").read_text(encoding="utf-8-sig"))
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = manifest.get("version")
    errors = []
    if plugin.get("version") != version:
        errors.append(f"version mismatch: manifest {version} vs plugin.json {plugin.get('version')}")
    folders = [e.get("folder") for e in manifest.get("agentSkills", [])]
    on_disk = sorted(f"skills/{p.name}" for p in (PLUGIN / "skills").iterdir() if p.is_dir())
    for f in folders:
        smd = PLUGIN / f / "SKILL.md"
        if not smd.is_file():
            errors.append(f"{f}: SKILL.md missing")
            continue
        fm = frontmatter(smd)
        if fm.get("name") != Path(f).name:
            errors.append(f"{f}: frontmatter name {fm.get('name')!r} does not match the folder")
        if fm.get("version") != version:
            errors.append(f"{f}: metadata version {fm.get('version')!r} is not the release version {version}")
    for f in on_disk:
        if f not in folders:
            errors.append(f"{f} exists but is not listed in manifest agentSkills")
    for need in ("package/color.png", "package/outline.png", "README.md", "MIT.md", "THIRD-PARTY-NOTICES.md", "install/prepare_install.py"):
        if not (PLUGIN / need).is_file():
            errors.append(f"{need} missing")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1

    # install manifest: every released skill file with its checksum
    install_spec = {"schema": "frontier-plugin-install/1.0", "plugin": plugin["name"], "display_name": manifest["name"]["short"],
                    "version": version, "start_prompts": START_PROMPTS, "skills": []}
    for f in folders:
        base = PLUGIN / f
        files = {p.relative_to(base).as_posix(): sha256_bytes(p.read_bytes()) for p in files_under(base)}
        install_spec["skills"].append({"name": Path(f).name, "folder": f, "files": files})
    spec_bytes = (json.dumps(install_spec, indent=1) + "\n").encode("utf-8")
    spec_path = PLUGIN / "install" / "plugin-install.json"
    if not spec_path.is_file() or spec_path.read_bytes() != spec_bytes:
        spec_path.write_bytes(spec_bytes)

    dist = Path(a.dist)
    dist.mkdir(parents=True, exist_ok=True)
    pkg = dist / f"frontier-envisioning-plugin-{version}.zip"
    with zipfile.ZipFile(pkg, "w") as zf:
        zf.comment = (f"Frontier Envisioning plugin {version}. Upload this zip in a Copilot Cowork chat and say "
                      "'Install the Frontier PlugIn'. Instructions: README.md").encode("utf-8")
        add_bytes(zf, (PLUGIN / "README.md").read_bytes(), "README.md")
        add_bytes(zf, (PLUGIN / "MIT.md").read_bytes(), "MIT.md")
        add_bytes(zf, (PLUGIN / "THIRD-PARTY-NOTICES.md").read_bytes(), "THIRD-PARTY-NOTICES.md")
        add_bytes(zf, (PLUGIN / "package" / "manifest.json").read_bytes(), "manifest.json")
        add_bytes(zf, (PLUGIN / "package" / "color.png").read_bytes(), "color.png")
        add_bytes(zf, (PLUGIN / "package" / "outline.png").read_bytes(), "outline.png")
        add_bytes(zf, spec_bytes, "install/plugin-install.json")
        add_bytes(zf, (PLUGIN / "install" / "prepare_install.py").read_bytes(), "install/prepare_install.py")
        for f in folders:
            for p in files_under(PLUGIN / f):
                add_bytes(zf, p.read_bytes(), p.relative_to(PLUGIN).as_posix())
    sums = f"{sha256_bytes(pkg.read_bytes())}  {pkg.name}\n"
    (dist / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")
    print(json.dumps({"version": version, "package": str(pkg), "sha256": sha256_bytes(pkg.read_bytes()),
                      "skills": {s["name"]: len(s["files"]) for s in install_spec["skills"]}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
