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
import html
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote

from check_repo import FORBIDDEN_FILES, SECRET_PATTERNS
from fe_lib import frontmatter as read_frontmatter, is_text, maturity_errors, maturity_fields

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
SKIP_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache", "dist"}
FIXED_DATE = (2026, 11, 9, 0, 0, 0)
START_PROMPTS = [
    "Prepare the Frontier envisioning for <customer>, workshop on <date>",
    "Build the Frontier blueprint demo for Caldova",
    "Build the identity kit demo for Caldova",
    "Build the value case for <customer>",
    "What will the <customer> agents cost per month?",
    "Gather the customer context for <customer>",
    "Prepare the IT readiness and architecture design workshop for <customer>",
]
ENTERPRISE_ACCOUNT = re.compile(r"(?<![\w.-])[a-z0-9][a-z0-9._-]*_microsoft(?![\w.-])", re.I)
PROFILE_PATH = re.compile(r"(?:\b[A-Z]:[\\/]+Users[\\/]+|/Users/)[^\\/\s\"<>]+", re.I)
CLASSIFIED_MARKDOWN = re.compile(r"^\|\s*(?:Classification|Status)\s*\|[^\n|]*Microsoft internal\b", re.I | re.M)


def distribution_errors(entries: list[tuple[bytes, str]]) -> list[str]:
    """Validate distribution bytes, including nested ZIPs, without exposing matches."""
    errors = []

    def normalise(text: str) -> str:
        text = re.sub(r"\\u([0-9a-fA-F]{4})", lambda match: chr(int(match[1], 16)), text)
        return html.unescape(unquote(text))

    def inspect(data: bytes, name: str, depth: int) -> None:
        decoded_name = normalise(name)
        label = PROFILE_PATH.sub("[redacted-profile]", ENTERPRISE_ACCOUNT.sub("[redacted-account]", decoded_name))
        for pattern, kind in ((ENTERPRISE_ACCOUNT, "enterprise account"), (PROFILE_PATH, "profile path")):
            if pattern.search(decoded_name):
                errors.append(f"{label}: distribution member name contains {kind} (value withheld)")
        if FORBIDDEN_FILES.search(decoded_name.replace("!", "/")):
            errors.append(f"{label}: secret/key file must not be distributed")
        path = Path(name)
        if path.suffix.lower() == ".zip":
            if depth >= 3 or len(data) > 8 * 1024 * 1024:
                errors.append(f"{label}: nested ZIP exceeds inspection limits")
                return
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    inspect(archive.comment, f"{name}!archive-comment.txt", depth + 1)
                    for entry in archive.infolist():
                        inspect(entry.comment, f"{name}!{entry.filename}.comment.txt", depth + 1)
                        if entry.file_size > 8 * 1024 * 1024 or entry.flag_bits & 1:
                            errors.append(f"{label}: oversized or encrypted ZIP member cannot be inspected")
                        else:
                            inspect(archive.read(entry), f"{name}!{entry.filename}", depth + 1)
            except zipfile.BadZipFile:
                errors.append(f"{label}: invalid ZIP cannot be inspected")
        elif is_text(path):
            if len(data) > 8 * 1024 * 1024:
                errors.append(f"{label}: distribution text exceeds inspection limit")
                return
            try:
                text = normalise(data.decode("utf-8-sig"))
            except UnicodeDecodeError:
                errors.append(f"{label}: distribution text must be UTF-8")
                return
            for pattern, kind in [(ENTERPRISE_ACCOUNT, "enterprise account"), (PROFILE_PATH, "profile path"),
                                  *SECRET_PATTERNS]:
                if pattern.search(text):
                    errors.append(f"{label}: distribution text contains {kind} (value withheld)")
            if CLASSIFIED_MARKDOWN.search(text):
                errors.append(f"{label}: classified internal document must not be distributed")

    for data, name in entries:
        inspect(data, name, 0)
    return errors


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
    fields = read_frontmatter(skill_md.read_text(encoding="utf-8"))
    out = {"name": fields.get("name"), "version": fields.get("metadata.version")}
    out.update(maturity_fields(fields))
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
        errors.extend(maturity_errors(Path(f).name, fm))
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
        fields = frontmatter(base / "SKILL.md")
        install_spec["skills"].append({
            "name": Path(f).name, "folder": f, "files": files,
            **{key: fields[key] for key in ("maturity", "optional", "requires_preview_ack")},
        })
    spec_bytes = (json.dumps(install_spec, indent=1) + "\n").encode("utf-8")
    entries = [
        ((PLUGIN / "README.md").read_bytes(), "README.md"),
        ((PLUGIN / "MIT.md").read_bytes(), "MIT.md"),
        ((PLUGIN / "THIRD-PARTY-NOTICES.md").read_bytes(), "THIRD-PARTY-NOTICES.md"),
        ((PLUGIN / "package" / "manifest.json").read_bytes(), "manifest.json"),
        ((PLUGIN / "package" / "color.png").read_bytes(), "color.png"),
        ((PLUGIN / "package" / "outline.png").read_bytes(), "outline.png"),
        (spec_bytes, "install/plugin-install.json"),
        ((PLUGIN / "install" / "prepare_install.py").read_bytes(), "install/prepare_install.py"),
    ]
    for folder in folders:
        entries.extend((p.read_bytes(), p.relative_to(PLUGIN).as_posix()) for p in files_under(PLUGIN / folder))
    errors = distribution_errors(entries)
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    spec_path = PLUGIN / "install" / "plugin-install.json"
    if not spec_path.is_file() or spec_path.read_bytes() != spec_bytes:
        spec_path.write_bytes(spec_bytes)

    dist = Path(a.dist)
    dist.mkdir(parents=True, exist_ok=True)
    pkg = dist / f"frontier-envisioning-plugin-{version}.zip"
    with zipfile.ZipFile(pkg, "w") as zf:
        zf.comment = (f"Frontier Envisioning plugin {version}. Upload this zip in a Copilot Cowork chat and say "
                      "'Install the Frontier PlugIn'. Instructions: README.md").encode("utf-8")
        for data, name in entries:
            add_bytes(zf, data, name)
    sums = f"{sha256_bytes(pkg.read_bytes())}  {pkg.name}\n"
    (dist / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")
    print(json.dumps({"version": version, "package": str(pkg), "sha256": sha256_bytes(pkg.read_bytes()),
                      "skills": {s["name"]: len(s["files"]) for s in install_spec["skills"]}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
