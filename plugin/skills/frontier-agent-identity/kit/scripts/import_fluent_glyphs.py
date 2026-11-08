#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Adds a Fluent UI System Icons glyph to scripts/glyphs/glyphs.json from its two 24 px SVG files.

Download the filled and regular 24 px SVGs from https://github.com/microsoft/fluentui-system-icons
(assets/<Name>/SVG/ic_fluent_<name>_24_filled.svg and ..._24_regular.svg), then:

  python scripts/import_fluent_glyphs.py cart scripts/ic_fluent_cart_24_filled.svg scripts/ic_fluent_cart_24_regular.svg \\
         --keywords "buying, purchase, order"

Only <path d="..."> data inside a 24 x 24 viewBox is accepted. Existing glyphs are replaced only with --replace.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import identity_lib as L  # noqa: E402
import raster as R  # noqa: E402


def paths_of(svg: Path) -> list:
    text = svg.read_text(encoding="utf-8")
    vb = re.search(r'viewBox="([^"]+)"', text)
    if vb and [float(x) for x in vb.group(1).split()] != [0.0, 0.0, 24.0, 24.0]:
        raise ValueError(f"{svg.name}: viewBox must be 0 0 24 24, found {vb.group(1)}")
    ds = re.findall(r'<path[^>]*\sd="([^"]+)"', text)
    if not ds:
        raise ValueError(f"{svg.name}: no <path d=...> found")
    for d in ds:
        R.parse_path(d)          # fails early on anything the renderer can't draw
    return ds


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="glyph name, e.g. cart")
    ap.add_argument("filled", help="24 px filled SVG")
    ap.add_argument("regular", help="24 px regular SVG")
    ap.add_argument("--keywords", default="", help="comma-separated words used by the seed to suggest the glyph")
    ap.add_argument("--root", default=str(L.ROOT))
    ap.add_argument("--replace", action="store_true")
    a = ap.parse_args(argv)
    lib_path = Path(a.root) / "scripts" / "glyphs" / "glyphs.json"
    lib = L.load_json(lib_path)
    if a.name in lib["glyphs"] and not a.replace:
        print(f"{a.name} exists; use --replace")
        return 1
    lib["glyphs"][a.name] = {"source": "fluent", "keywords": [k.strip() for k in a.keywords.split(",") if k.strip()],
                             "filled": paths_of(Path(a.filled)), "regular": paths_of(Path(a.regular))}
    lib["glyphs"] = dict(sorted(lib["glyphs"].items()))
    L.save_json(lib_path, lib)
    print(f"added {a.name}; {len(lib['glyphs'])} glyphs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
