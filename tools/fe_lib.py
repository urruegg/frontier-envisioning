# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Shared helpers for the repository tools (standard library only).

The repository layout these tools rely on:
  plugin/            the Copilot Cowork plugin, the packaged unit (skills, package, install, README, MIT, notices)
  src/renderer/      sources of the blueprint HTML template (assembled into plugin/skills/frontier-blueprint/templates)
  tools/             build, test and release tools (this folder)
  tests/             unit, pipeline, DOM and browser tests
  infra/, site/      showcase hosting (Bicep for Azure Static Web Apps, site sources)
  releases/<v>/      release manifests (hashes of the published artefacts)
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
SKILLS = PLUGIN / "skills"
RENDERER = ROOT / "src" / "renderer"
TEMPLATE = SKILLS / "frontier-blueprint" / "templates" / "frontier-blueprint-template.html"
BUILD = ROOT / "build"
DIST = ROOT / "dist"
DEMO_DIR = BUILD / "demo"
SITE_DIR = BUILD / "site"
DEMO_HTML_NAME = "Frontier Company Blueprint - Template (Caldova sample).html"

# folders never scanned or packaged
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist",
             ".venv", "venv", ".azure", "test-results", "playwright-report", ".superpowers-src"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".html", ".htm", ".css", ".js", ".mjs", ".cjs", ".ts", ".txt", ".yml",
                 ".yaml", ".bicep", ".bicepparam", ".ps1", ".sh", ".toml", ".cfg", ".ini", ".svg", ".vtt", ".csv",
                 ".xml", ".editorconfig", ".gitignore", ".gitattributes"}


def plugin_version() -> str:
    return json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: Path, name: str | None = None):
    """Import a script by path (the plugin scripts are not a package)."""
    spec = importlib.util.spec_from_file_location(name or path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def skill_inventory_errors(
    version: str, registered: list[str], disk: list[str], *, source_tree: bool
) -> list[str]:
    installer = load_module(PLUGIN / "install" / "prepare_install.py", "fe_install_inventory")
    return installer.skill_inventory_errors(version, registered, disk, source_tree=source_tree)


def call_main(mod, argv) -> tuple[int, str]:
    """Call mod.main(argv) and capture what it prints."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = mod.main(argv)
    return int(code or 0), buf.getvalue()


def which(name: str) -> str | None:
    return shutil.which(name)


def run(cmd: list[str], cwd: Path | None = None, env: dict | None = None, check: bool = False) -> int:
    print("$ " + " ".join(cmd), flush=True)
    merged = dict(os.environ, **(env or {}))
    try:
        proc = subprocess.run(cmd, cwd=str(cwd or ROOT), env=merged)
    except FileNotFoundError:
        print(f"not found: {cmd[0]}")
        if check:
            raise SystemExit(127)
        return 127
    if check and proc.returncode:
        raise SystemExit(proc.returncode)
    return proc.returncode


def in_git_repo() -> bool:
    return (ROOT / ".git").exists() and which("git") is not None


def tracked_files() -> list[Path]:
    """Files under version control (git ls-files), or every file outside SKIP_DIRS when Git is absent."""
    if in_git_repo():
        out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, check=True).stdout
        files = [ROOT / p for p in out.decode("utf-8").split("\0") if p]
        return sorted(p for p in files if p.is_file())
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in sorted(filenames):
            files.append(Path(dirpath) / f)
    return files


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", "CODEOWNERS", "Makefile", ".editorconfig",
                                                                  ".gitignore", ".gitattributes", "AGENTS.md"}


def utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def frontmatter(md: str) -> dict:
    """Read top-level fields and the owned version/maturity metadata."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", md, re.S)
    out: dict = {}
    if not m:
        return out
    block = m.group(1)
    for line in block.splitlines():
        km = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if km:
            val = km.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
                val = val[1:-1]
            out[km.group(1)] = val
    ver = re.search(r"(?m)^\s+version:\s*['\"]?([0-9][\w.\-]*)['\"]?\s*$", block)
    if ver:
        out["metadata.version"] = ver.group(1)
    metadata = False
    for line in block.splitlines():
        if line and not line[0].isspace():
            metadata = line.startswith("metadata:")
        elif metadata:
            field = re.match(r"^\s+(maturity|optional|requires_preview_ack):\s*(.*?)\s*$", line)
            if field:
                value = field[2].strip("'\"")
                out["metadata." + field[1]] = value
    if out.get("description") in (">", "|", ">-", "|-"):
        desc = re.search(r"(?ms)^description:\s*[>|]-?\s*\n(.*?)(?=^\S|\Z)", block)
        out["description"] = " ".join(x.strip() for x in desc.group(1).splitlines()) if desc else ""
    return out


def maturity_fields(fields: dict) -> dict:
    result = {}
    for key in ("maturity", "optional", "requires_preview_ack"):
        value = fields.get("metadata." + key)
        if value is not None:
            result[key] = value == "true" if value in {"true", "false"} else value
    return result


def maturity_errors(name: str, fields: dict) -> list[str]:
    errors = []
    expected = "preview" if name in {"frontier-finops", "frontier-agent-factory"} else "ga"
    if fields.get("maturity") != expected:
        errors.append(f"{name}: product maturity must be {expected}")
    for key in ("optional", "requires_preview_ack"):
        if type(fields.get(key)) is not bool:
            errors.append(f"{name}: {key} must be an explicit boolean")
    if name == "frontier-finops":
        if fields.get("optional") is not True or fields.get("requires_preview_ack") is not True:
            errors.append(f"{name}: FinOps must be optional Preview with acknowledgement required")
    elif name == "frontier-agent-factory":
        if fields.get("optional") is not True or fields.get("requires_preview_ack") is not False:
            errors.append(f"{name}: Factory must be optional Preview without a cost acknowledgement gate")
    elif fields.get("requires_preview_ack") is not False:
        errors.append(f"{name}: GA core must not require FinOps Preview acknowledgement")
    return errors
