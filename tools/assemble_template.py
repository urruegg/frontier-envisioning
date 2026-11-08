#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Assemble the blueprint HTML template from its sources.

  python tools/assemble_template.py            write plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html
  python tools/assemble_template.py --check    fail when the committed template differs from the sources (CI drift check)
  python tools/assemble_template.py --out X    write to another file

Sources: src/renderer/skeleton.html (page shell with /*__CSS__*/ and /*__JS__*/ slots),
src/renderer/template.css and src/renderer/template.js. The template is a generated file: change the
sources, then assemble. Output is written as UTF-8 with LF line endings on every platform.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import RENDERER, TEMPLATE, ROOT  # noqa: E402


def assemble() -> bytes:
    sk = (RENDERER / "skeleton.html").read_text(encoding="utf-8")
    css = (RENDERER / "template.css").read_text(encoding="utf-8")
    js = (RENDERER / "template.js").read_text(encoding="utf-8")
    if "</script" in js.lower():
        raise SystemExit("template.js contains '</script' - it would end the inline script early")
    for slot in ("/*__CSS__*/", "/*__JS__*/", '"__BLUEPRINT_DATA__"'):
        if sk.count(slot) != 1:
            raise SystemExit(f"skeleton.html must contain {slot} exactly once")
    out = sk.replace("/*__CSS__*/", css).replace("/*__JS__*/", js)
    return out.encode("utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the committed template instead of writing")
    ap.add_argument("--out", help="output file (default: the plugin template)")
    a = ap.parse_args(argv)
    data = assemble()
    target = Path(a.out) if a.out else TEMPLATE
    if a.check:
        current = target.read_bytes() if target.exists() else b""
        if current != data:
            print(f"DRIFT: {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target} differs from src/renderer "
                  "(edit src/renderer/*, then run: python tools/dev.py template)")
            return 1
        print(f"template up to date ({len(data)} bytes)")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.read_bytes() != data:
        target.write_bytes(data)
        print(f"template written ({len(data)} bytes)")
    else:
        print(f"template unchanged ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
