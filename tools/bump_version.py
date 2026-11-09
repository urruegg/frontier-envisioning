#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Set a new plugin version in every place that carries it.

  python tools/bump_version.py 1.5.0 [--date 2026-11-20]

Updates plugin/.claude-plugin/plugin.json, plugin/package/manifest.json, the metadata version of every
SKILL.md, PLUGIN_VERSION in build_blueprint.py, the version line and package names in plugin/README.md,
and (with --date) the fixed archive date in tools/build_package.py. Adds an empty CHANGELOG section.
Then run `python tools/dev.py package` to regenerate plugin/install/plugin-install.json.
The version must be MAJOR.MINOR.PATCH (the Microsoft 365 app manifest accepts digits only).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import ROOT  # noqa: E402


def _sub_once(text: str, pattern: str, repl: str, what: str, flags=0) -> str:
    new, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f"could not update {what}")
    return new


def bump(root: Path, new: str, date: str | None = None) -> list[str]:
    if not re.fullmatch(r"\d+\.\d+\.\d+", new):
        raise SystemExit("version must be MAJOR.MINOR.PATCH, for example 1.5.0")
    plugin = root / "plugin"
    changed = []
    pj = plugin / ".claude-plugin" / "plugin.json"
    old = json.loads(pj.read_text(encoding="utf-8"))["version"]
    if old == new:
        raise SystemExit(f"already at {new}")

    def edit(path: Path, fn):
        t = path.read_text(encoding="utf-8")
        n = fn(t)
        if n != t:
            path.write_text(n, encoding="utf-8", newline="\n")
            changed.append(path.relative_to(root).as_posix())

    edit(pj, lambda t: _sub_once(t, r'("version":\s*")[^"]+(")', rf"\g<1>{new}\g<2>", "plugin.json"))
    edit(plugin / "package" / "manifest.json", lambda t: _sub_once(t, r'("version":\s*")[^"]+(")', rf"\g<1>{new}\g<2>", "manifest.json"))
    for smd in sorted((plugin / "skills").glob("*/SKILL.md")):
        edit(smd, lambda t: _sub_once(t, r'(?m)^(\s+version:\s*)"[^"]+"', rf'\g<1>"{new}"', f"{smd.parent.name}/SKILL.md"))
    edit(plugin / "skills" / "frontier-blueprint" / "scripts" / "build_blueprint.py",
         lambda t: _sub_once(t, r'(?m)^PLUGIN_VERSION = "[^"]+"', f'PLUGIN_VERSION = "{new}"', "PLUGIN_VERSION"))

    def readme(t: str) -> str:
        t = t.replace(f"Version {old}", f"Version {new}")
        t = t.replace(f"frontier-envisioning-plugin-{old}.zip", f"frontier-envisioning-plugin-{new}.zip")
        return t.replace(f"frontier-envisioning-{old}-source.zip", f"frontier-envisioning-{new}-source.zip")
    edit(plugin / "README.md", readme)
    if date:
        d = dt.date.fromisoformat(date)
        edit(root / "tools" / "build_package.py",
             lambda t: _sub_once(t, r"(?m)^FIXED_DATE = \([^)]*\)", f"FIXED_DATE = ({d.year}, {d.month}, {d.day}, 0, 0, 0)", "FIXED_DATE"))

    def changelog(t: str) -> str:
        if re.search(rf"(?m)^## \[?{re.escape(new)}\]?(\s|$)", t):
            return t
        head = f"## {new} — {date or 'unreleased'}\n\n- \n\n"
        i = t.find("\n## ")
        return t[: i + 1] + head + t[i + 1:] if i >= 0 else t + "\n" + head
    edit(root / "CHANGELOG.md", changelog)
    return changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("version")
    ap.add_argument("--date", help="release date YYYY-MM-DD (sets the fixed archive date)")
    a = ap.parse_args(argv)
    for p in bump(ROOT, a.version, a.date):
        print("updated " + p)
    print("next: python tools/dev.py package   (regenerates plugin/install/plugin-install.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
