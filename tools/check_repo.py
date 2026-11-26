#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Repository rules that keep the plugin, the packages and the engineering setup consistent.

  python tools/check_repo.py [--strict]

Checks (errors fail the run; --strict also fails when an optional checker such as PyYAML is missing):
  version     plugin.json, manifest.json, every SKILL.md, build_blueprint.PLUGIN_VERSION, plugin-install.json,
              the plugin README header and CHANGELOG carry the same version
  skills      manifest agentSkills = skill folders; frontmatter name = folder; description present and within
              900 UTF-16 units (house rule for routing quality) and the 1,024-character Agent Skills limit
  licence     LICENSE and plugin/MIT.md carry the same MIT text; shared formula module identical in both skills
  data        every JSON file parses; every YAML file parses (PyYAML)
  copilot     custom agents have a description; repository skills are well formed; path instructions have
              applyTo; hook files are version 1 with known events
  workflows   actions are referenced by a version tag or a commit SHA (never a branch); a permissions block
  hygiene     no tracked secrets or key files, no file above 10 MB
Standard library only (PyYAML optional).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import (  # noqa: E402
    PLUGIN, ROOT, SKILLS, frontmatter, maturity_errors, maturity_fields,
    skill_inventory_errors, tracked_files, utf16_units,
)

HOOK_EVENTS = {"sessionStart", "sessionEnd", "userPromptSubmitted", "preToolUse", "postToolUse", "postToolUseFailure",
               "agentStop", "subagentStart", "subagentStop", "errorOccurred", "preCompact", "permissionRequest",
               "notification", "userPromptTransformed"}
SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b"), "GitHub fine-grained token"),
    (re.compile(r"AccountKey=[A-Za-z0-9+/=]{40,}"), "storage account key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
]
FORBIDDEN_FILES = re.compile(r"(^|/)(\.env(\..*)?|.*\.(pem|pfx|p12|key)|id_rsa|id_ed25519)$")


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.notes: list[str] = []

    def err(self, area: str, msg: str):
        self.errors.append(f"[{area}] {msg}")

    def note(self, area: str, msg: str):
        self.notes.append(f"[{area}] {msg}")


def check_version(r: Report) -> str:
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    manifest = json.loads((PLUGIN / "package" / "manifest.json").read_text(encoding="utf-8-sig"))
    v = plugin.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", v):
        r.err("version", f"plugin.json version {v!r} is not MAJOR.MINOR.PATCH (the Microsoft 365 manifest needs digits only)")
    if manifest.get("version") != v:
        r.err("version", f"manifest.json {manifest.get('version')} != plugin.json {v}")
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        fm = frontmatter((d / "SKILL.md").read_text(encoding="utf-8"))
        if fm.get("metadata.version") != v:
            r.err("version", f"{d.name}/SKILL.md metadata.version {fm.get('metadata.version')} != {v}")
    bb = (SKILLS / "frontier-blueprint" / "scripts" / "build_blueprint.py").read_text(encoding="utf-8")
    m = re.search(r'^PLUGIN_VERSION = "([^"]+)"', bb, re.M)
    if not m or m.group(1) != v:
        r.err("version", f"build_blueprint.PLUGIN_VERSION {m.group(1) if m else None} != {v}")
    spec = PLUGIN / "install" / "plugin-install.json"
    if spec.exists() and json.loads(spec.read_text(encoding="utf-8")).get("version") != v:
        r.err("version", "plugin/install/plugin-install.json is stale: run python tools/dev.py package")
    readme = (PLUGIN / "README.md").read_text(encoding="utf-8")
    if f"Version {v}" not in readme:
        r.err("version", f"plugin/README.md does not state 'Version {v}'")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"(?m)^## \[?{re.escape(v)}\]?(\s|$)", changelog):
        r.err("version", f"CHANGELOG.md has no '## {v}' section")
    return v


def check_skills(r: Report):
    manifest = json.loads((PLUGIN / "package" / "manifest.json").read_text(encoding="utf-8-sig"))
    listed = [e.get("folder") for e in manifest.get("agentSkills", [])]
    on_disk = sorted(f"skills/{p.name}" for p in SKILLS.iterdir() if p.is_dir())
    for error in skill_inventory_errors(
        manifest.get("version", ""), listed, on_disk, source_tree=True
    ):
        r.err("skills", error)
    for d in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        _skill_frontmatter(r, d, limit_units=900)
        fields = frontmatter((d / "SKILL.md").read_text(encoding="utf-8"))
        for error in maturity_errors(d.name, maturity_fields(fields)):
            r.err("skills", error)
    if (SKILLS / "frontier-finops/scripts/fv_expr.py").read_bytes() != (SKILLS / "frontier-value-case/scripts/fv_expr.py").read_bytes():
        r.err("skills", "fv_expr.py differs between frontier-finops and frontier-value-case (keep one shared copy)")
    if (ROOT / "tools/zip_stream.py").read_bytes() != (
        SKILLS / "frontier-agent-factory/scripts/zip_stream.py"
    ).read_bytes():
        r.err("skills", "zip_stream.py differs between tools and frontier-agent-factory")


def _skill_frontmatter(r: Report, d: Path, limit_units: int):
    smd = d / "SKILL.md"
    if not smd.is_file():
        r.err("skills", f"{d.relative_to(ROOT)} has no SKILL.md")
        return
    fm = frontmatter(smd.read_text(encoding="utf-8"))
    if fm.get("name") != d.name:
        r.err("skills", f"{d.relative_to(ROOT)}: frontmatter name {fm.get('name')!r} != folder")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", d.name) or len(d.name) > 64:
        r.err("skills", f"{d.relative_to(ROOT)}: skill names are lowercase words joined by hyphens, at most 64 characters")
    desc = fm.get("description", "")
    if not desc:
        r.err("skills", f"{d.relative_to(ROOT)}: description missing")
    elif len(desc) > 1024:
        r.err("skills", f"{d.relative_to(ROOT)}: description has {len(desc)} characters (limit 1,024)")
    elif utf16_units(desc) > limit_units:
        r.err("skills", f"{d.relative_to(ROOT)}: description has {utf16_units(desc)} UTF-16 units (house limit {limit_units})")


def check_licence(r: Report):
    def body(t: str) -> str:
        t = re.sub(r"^#\s*", "", t.strip())
        return re.sub(r"\s+", " ", t)
    lic, mit = ROOT / "LICENSE", PLUGIN / "MIT.md"
    if not lic.exists() or not mit.exists():
        r.err("licence", "LICENSE and plugin/MIT.md must both exist")
    elif body(lic.read_text(encoding="utf-8")) != body(mit.read_text(encoding="utf-8")):
        r.err("licence", "LICENSE and plugin/MIT.md differ")
    if not (PLUGIN / "THIRD-PARTY-NOTICES.md").exists():
        r.err("licence", "plugin/THIRD-PARTY-NOTICES.md missing (Microsoft product icons are not MIT)")


def check_data(r: Report, files: list[Path], strict: bool):
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
        (r.err if strict else r.note)("data", "PyYAML not installed: YAML files not parsed (pip install -r requirements-dev.txt)")
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        if p.suffix == ".json":
            try:
                json.loads(p.read_text(encoding="utf-8-sig"))
            except ValueError as e:
                if not rel.startswith(".vscode/"):  # VS Code files allow comments
                    r.err("data", f"{rel}: invalid JSON ({e})")
        elif p.suffix in (".yml", ".yaml") and yaml is not None:
            try:
                yaml.safe_load(p.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                r.err("data", f"{rel}: invalid YAML ({str(e).splitlines()[0]})")


def check_copilot(r: Report):
    gh = ROOT / ".github"
    for p in sorted((gh / "agents").glob("*.agent.md")) if (gh / "agents").exists() else []:
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if not fm.get("description"):
            r.err("copilot", f"{p.relative_to(ROOT)}: custom agents need a description")
    if (gh / "skills").exists():
        for d in sorted(x for x in (gh / "skills").iterdir() if x.is_dir()):
            _skill_frontmatter(r, d, limit_units=1024)
    for p in sorted((gh / "instructions").glob("*.instructions.md")) if (gh / "instructions").exists() else []:
        if not frontmatter(p.read_text(encoding="utf-8")).get("applyTo"):
            r.err("copilot", f"{p.relative_to(ROOT)}: path instructions need applyTo")
    for p in sorted((gh / "hooks").glob("*.json")) if (gh / "hooks").exists() else []:
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            r.err("copilot", f"{p.relative_to(ROOT)}: invalid JSON ({e})")
            continue
        if cfg.get("version") != 1 or not isinstance(cfg.get("hooks"), dict):
            r.err("copilot", f"{p.relative_to(ROOT)}: hook files need version 1 and a hooks object")
            continue
        for ev, entries in cfg["hooks"].items():
            if ev not in HOOK_EVENTS:
                r.err("copilot", f"{p.relative_to(ROOT)}: unknown hook event {ev}")
            if not isinstance(entries, list):
                r.err("copilot", f"{p.relative_to(ROOT)}: {ev} must be a list")
                continue
            for e in entries:
                if not (e.get("bash") or e.get("command")):
                    r.err("copilot", f"{p.relative_to(ROOT)}: {ev} entry without bash/command (the cloud agent runs bash only)")


def check_workflows(r: Report):
    wf = ROOT / ".github" / "workflows"
    if not wf.exists():
        return
    for p in sorted(wf.glob("*.yml")):
        text = p.read_text(encoding="utf-8")
        rel = p.relative_to(ROOT).as_posix()
        if not re.search(r"(?m)^permissions:", text):
            r.err("workflows", f"{rel}: add a top-level permissions block (least privilege)")
        for m in re.finditer(r"(?m)^\s*-?\s*uses:\s*([^\s#]+)", text):
            ref = m.group(1)
            if ref.startswith("./"):
                continue
            if "@" not in ref:
                r.err("workflows", f"{rel}: {ref} has no version")
                continue
            ver = ref.split("@", 1)[1]
            if not (re.fullmatch(r"v\d+(\.\d+){0,2}", ver) or re.fullmatch(r"[0-9a-f]{40}", ver)):
                r.err("workflows", f"{rel}: {ref} must use a version tag or a commit SHA, not a branch")


def check_hygiene(r: Report, files: list[Path]):
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        if FORBIDDEN_FILES.search(rel):
            r.err("hygiene", f"{rel}: key or environment files must not be committed")
        size = p.stat().st_size
        if size > 10 * 1024 * 1024:
            r.err("hygiene", f"{rel}: {size} bytes (limit 10 MB)")
        if p.suffix.lower() in {".png", ".zip", ".ico", ".jpg", ".jpeg", ".gif", ".pdf", ".pptx", ".docx", ".xlsx"}:
            continue
        if size > 4 * 1024 * 1024:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for rx, what in SECRET_PATTERNS:
            if rx.search(text):
                r.err("hygiene", f"{rel}: looks like a {what}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="fail when an optional checker is missing (CI)")
    a = ap.parse_args(argv)
    r = Report()
    files = tracked_files()
    v = check_version(r)
    check_skills(r)
    check_licence(r)
    check_data(r, files, a.strict)
    check_copilot(r)
    check_workflows(r)
    check_hygiene(r, files)
    for n in r.notes:
        print("NOTE  " + n)
    for e in r.errors:
        print("ERROR " + e)
    print(f"repository rules: version {v}, {len(files)} files, {len(r.errors)} errors")
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
