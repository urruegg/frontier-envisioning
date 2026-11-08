#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Print the CHANGELOG section of a version (the release notes of a GitHub release).

  python tools/release_notes.py [VERSION]      default: the plugin version
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import ROOT, plugin_version  # noqa: E402


def section(changelog: str, version: str) -> str:
    m = re.search(rf"(?ms)^## \[?{re.escape(version)}\]?[^\n]*\n(.*?)(?=^## |\Z)", changelog)
    if not m:
        raise SystemExit(f"CHANGELOG.md has no section for {version}")
    return m.group(1).strip() + "\n"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    version = (argv[0] if argv else plugin_version()).lstrip("v")
    notes = section((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), version)
    sys.stdout.write(notes + "\nInstall: attach the plugin package in a Copilot Cowork chat and say \"Install the Frontier PlugIn\".\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
