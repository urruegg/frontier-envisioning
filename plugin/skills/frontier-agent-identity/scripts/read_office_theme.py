#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Reads the Office theme (colours and fonts) from a customer-authored file into a brand file.

Supported: .pptx .potx .ppsx .pptm .docx .dotx .docm .xlsx .xltx .xlsm .thmx (all OOXML packages).
For presentations the theme of the first slide master is used.

Usage:
  python read_office_theme.py <file> --out brand.json [--customer "Caldova Industrial AG" --short Caldova]
         [--evidence-id E07] [--merge existing-brand.json]

Writes (frontier-brand/1.0): {"schema", "customer", "short", "theme": {"name", "dk1".."folHlink", "fonts"},
"named": [...], "sources": {...}}. Standard library only; reads nothing but the given file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET  # nosec B405 - parsed only through safe_xml(): no DTD, no entities, size-capped
from pathlib import Path, PurePosixPath

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
MAX_PART = 5 * 1024 * 1024


def safe_xml(data: bytes):
    """Parse an OOXML part. Office parts never carry a DTD, so any DOCTYPE or ENTITY is refused
    (blocks entity-expansion attacks); parts larger than 5 MB are refused."""
    if len(data) > MAX_PART:
        raise ValueError("XML part too large")
    head = data[:4096].upper()
    if b"<!DOCTYPE" in head or b"<!ENTITY" in data.upper():
        raise ValueError("XML with a DTD or entities is not accepted")
    return ET.fromstring(data)  # nosec B314 - guarded above


SLOTS = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"]


def theme_part(z: zipfile.ZipFile) -> str:
    names = z.namelist()
    masters = sorted(n for n in names if re.fullmatch(r"ppt/slideMasters/slideMaster\d+\.xml", n))
    if masters:
        rels = PurePosixPath(masters[0]).parent / "_rels" / (PurePosixPath(masters[0]).name + ".rels")
        if str(rels) in names:
            for rel in safe_xml(z.read(str(rels))).findall("rel:Relationship", NS):
                if rel.get("Type", "").endswith("/theme"):
                    target = PurePosixPath(masters[0]).parent / rel.get("Target")
                    parts = []
                    for p in target.parts:
                        if p == "..":
                            parts.pop()
                        else:
                            parts.append(p)
                    return "/".join(parts)
    for cand in ("word/theme/theme1.xml", "xl/theme/theme1.xml", "ppt/theme/theme1.xml", "theme/theme/theme1.xml"):
        if cand in names:
            return cand
    themes = sorted(n for n in names if re.search(r"theme/theme\d+\.xml$", n))
    if themes:
        return themes[0]
    raise ValueError("no Office theme found in the file")


def read_theme(path: Path) -> dict:
    with zipfile.ZipFile(path) as z:
        part = theme_part(z)
        root = safe_xml(z.read(part))
    scheme = root.find(".//a:clrScheme", NS)
    if scheme is None:
        raise ValueError("theme has no colour scheme")
    theme = {"name": root.get("name") or scheme.get("name") or "", "colourScheme": scheme.get("name") or ""}
    for slot in SLOTS:
        el = scheme.find(f"a:{slot}", NS)
        if el is None:
            continue
        srgb = el.find("a:srgbClr", NS)
        sysc = el.find("a:sysClr", NS)
        val = srgb.get("val") if srgb is not None else (sysc.get("lastClr") if sysc is not None else None)
        if val:
            theme[slot] = "#" + val.upper()
    fonts = {}
    for key, tag in (("headings", "a:majorFont"), ("body", "a:minorFont")):
        latin = root.find(f".//a:fontScheme/{tag}/a:latin", NS)
        if latin is not None and latin.get("typeface"):
            fonts[key] = latin.get("typeface")
    theme["fonts"] = fonts
    theme["part"] = part
    return theme


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--customer", default="")
    ap.add_argument("--short", default="")
    ap.add_argument("--evidence-id", default="")
    ap.add_argument("--merge", help="existing brand file to update (keeps website colours, logo and names)")
    a = ap.parse_args(argv)
    src = Path(a.file)
    try:
        theme = read_theme(src)
    except (zipfile.BadZipFile, ValueError, KeyError, ET.ParseError) as exc:
        print(f"ERROR {src.name}: {exc}")
        return 1
    brand = json.loads(Path(a.merge).read_text(encoding="utf-8")) if a.merge else {"schema": "frontier-brand/1.0"}
    brand["customer"] = a.customer or brand.get("customer", "")
    brand["short"] = a.short or brand.get("short", "")
    brand["theme"] = {k: v for k, v in theme.items() if k != "part"}
    ev = f" ({a.evidence_id})" if a.evidence_id else ""
    brand.setdefault("sources", {})["theme"] = f"Office theme '{theme['name']}' read from {src.name}{ev}"
    named = {n["hex"]: n for n in brand.get("named", [])}
    for slot in SLOTS[:10]:
        hexv = theme.get(slot)
        if hexv and hexv not in named:
            named[hexv] = {"name": f"{brand['short'] or 'Brand'} {slot}", "hex": hexv, "slot": slot,
                           "source": f"Office theme {slot}{ev}"}
    brand["named"] = list(named.values())
    Path(a.out).write_text(json.dumps(brand, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"theme": theme["name"], "part": theme["part"], "colours": {s: theme.get(s) for s in SLOTS if theme.get(s)},
                      "fonts": theme["fonts"], "out": a.out}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
