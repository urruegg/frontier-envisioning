#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Validates the agent identity package (names, colours, icon files) - run it on every pull request.

Checks (errors block; warnings inform)
  N1  display names fit naming.maxDisplayLength (30) in every environment, allowed characters only,
      non-production names end with their environment postfix
  N2  the production name fits maxBaseLength, so the longest postfix still fits
  N3  environment words appear only in display names - never in schema, solution, variable,
      connection-reference or folder names
  N4  display names, slugs, schema names and solution names are unique
  N5  publisher prefix: 2-8 lower-case letters or digits, starts with a letter, not 'mscrm', and in
      naming.allowedPrefixes when that list is set; schema names are <prefix>_<Letter><LettersOrDigits>
  N6  PO token from poAreas; derived names match the tokens (no drift); journey and glyph exist
  D1  short description <= 72 characters (<= 80 with the environment marker); full description
      <= 4,000 (Microsoft 365 app manifest) and <= 1,000 for declarative agents
  C1  glyph/background contrast >= 4.5:1;  C2  environment label/band contrast >= 4.5:1
  F1  icon files exist (colour 192 and 32 per environment, outline 32); every PNG <= 100 KB
  F2  outline icon transparent, colour icon opaque and square
  F3  identity.json per agent matches the config
  W1  warning: the same glyph twice in one journey;  W2  warning: PO area not linked to the agent's journey

Usage: python scripts/validate_identity.py [--root .] [--json report.json] [--skip-files]
Exit code 0 = no errors, 1 = at least one error.
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import identity_lib as L  # noqa: E402

COMMON_ENV_WORDS = ("dev", "test", "prod", "uat", "sit", "qa", "preprod", "staging", "stage", "int", "sandbox")


def png_meta(path: Path) -> dict:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
    return {"width": w, "height": h, "bitDepth": depth, "colourType": ctype, "bytes": len(data), "data": data}


def corner_alpha(meta: dict):
    """Alpha of the top-left pixel for 8-bit RGBA PNGs (None if the PNG has no alpha channel)."""
    if meta["colourType"] != 6 or meta["bitDepth"] != 8:
        return None
    data, pos, idat = meta["data"], 8, b""
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        if data[pos + 4:pos + 8] == b"IDAT":
            idat += data[pos + 8:pos + 8 + length]
        pos += 12 + length
    return zlib.decompress(idat)[4]   # filter byte + RGBA of pixel 0 (filters 0 and 1 keep pixel 0 as is)


def split_words(value: str) -> str:
    return re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value).replace("_", " ").replace("-", " ").replace("/", " ")


def validate(root: Path, skip_files: bool = False) -> dict:
    cfg, palette = L.load_config(root)
    lib = L.load_glyphs(root)
    errors, warnings = [], []
    n = cfg["naming"]
    rx_chars = re.compile(n["allowedDisplayCharacters"])
    prefix = n["publisherPrefix"]
    tokens = {p["token"]: p for p in cfg["poAreas"]}
    envs = L.env_names(cfg)
    prod = L.prod_env(cfg)
    configured = {e.lower() for e in envs} | {(L.env(cfg, e).get("postfix") or "").lower() for e in envs}
    configured.discard("")
    hard_env = re.compile(r"(?i)(?:^|[^a-z])(" + "|".join(sorted(configured, key=len, reverse=True)) + r")(?:[^a-z]|$)") if configured else None
    soft_env = re.compile(r"(?i)(?:^|[^a-z])(" + "|".join(COMMON_ENV_WORDS) + r")(?:[^a-z]|$)")
    max_base = L.max_base_length(cfg)
    seen = {"display": {}, "slug": {}, "schema": {}, "solution": {}}
    glyph_by_journey = {}

    if not re.fullmatch(r"[a-z][a-z0-9]{1,7}", prefix) or prefix.startswith("mscrm"):
        errors.append(f"N5 publisher prefix '{prefix}' must be 2-8 lower-case letters or digits, start with a letter, not 'mscrm'")
    if n.get("allowedPrefixes") and prefix not in n["allowedPrefixes"]:
        errors.append(f"N5 publisher prefix '{prefix}' not in {n['allowedPrefixes']}")
    if n.get("maxBaseLength") and n["maxBaseLength"] > max_base:
        errors.append(f"N2 naming.maxBaseLength {n['maxBaseLength']} leaves no room for the longest postfix (max {max_base})")
    for e in envs:
        if e == prod:
            continue
        band = palette["environments"].get(e)
        if not band:
            errors.append(f"C2 palette has no marker colours for environment {e}")
            continue
        c = L.contrast(band["band"], band["label"])
        if c < 4.5:
            errors.append(f"C2 environment {e}: label contrast {c}:1 below 4.5:1")

    for a in cfg["agents"]:
        aid = a["id"]
        if a["po"] not in tokens:
            errors.append(f"N6 {aid}: PO token '{a['po']}' is not in poAreas")
            continue
        if a["journey"] not in palette["journeys"]:
            errors.append(f"N6 {aid}: journey '{a['journey']}' has no colour in palette.json")
            continue
        if a["glyph"] not in lib["glyphs"]:
            errors.append(f"N6 {aid}: glyph '{a['glyph']}' is not in scripts/glyphs/glyphs.json")
            continue
        if a.get("kind") not in L.KINDS:
            errors.append(f"N6 {aid}: kind '{a.get('kind')}' is not one of {sorted(L.KINDS)}")
            continue
        if tokens[a["po"]].get("journeys") and a["journey"] not in tokens[a["po"]]["journeys"]:
            warnings.append(f"W2 {aid}: PO area '{a['po']}' is not linked to journey {a['journey']}")
        fresh = L.derive(cfg, a, palette)
        if fresh != a.get("derived"):
            errors.append(f"N6 {aid}: derived names are out of date - run scripts/build_identity_assets.py")
        d = fresh
        base = d["displayName"][prod]
        if len(base) > max_base:
            errors.append(f"N2 {aid}: '{base}' has {len(base)} characters (max {max_base})")
        for env_name, name in d["displayName"].items():
            if len(name) > n["maxDisplayLength"]:
                errors.append(f"N1 {aid}: {env_name} name '{name}' has {len(name)} characters (max {n['maxDisplayLength']})")
            if not rx_chars.match(name):
                errors.append(f"N1 {aid}: {env_name} name '{name}' has characters outside {n['allowedDisplayCharacters']}")
            postfix = L.env(cfg, env_name).get("postfix", "")
            if env_name != prod and L.is_scoped(a) and postfix and not name.endswith(" " + postfix):
                errors.append(f"N1 {aid}: {env_name} name '{name}' does not end with ' {postfix}'")
        if hard_env and hard_env.search(base):
            errors.append(f"N3 {aid}: production name '{base}' contains an environment word")
        elif soft_env.search(base):
            warnings.append(f"N3 {aid}: production name '{base}' contains a word often used for environments")
        for key in ("schemaName", "solutionUniqueName", "solutionDisplayName", "envVarPrefix", "connectionContext", "slug"):
            val = d.get(key)
            if val and hard_env and hard_env.search(split_words(val)):
                errors.append(f"N3 {aid}: {key} '{val}' contains an environment word")
        if d["schemaName"] and not re.fullmatch(rf"{re.escape(prefix)}_[A-Za-z][A-Za-z0-9]*", d["schemaName"]):
            errors.append(f"N5 {aid}: schema name '{d['schemaName']}' must be {prefix}_<Letter><LettersOrDigits>")
        for kind, val in (("display", base), ("slug", d["slug"]), ("schema", d["schemaName"]), ("solution", d["solutionUniqueName"])):
            if not val:
                continue
            k = val.lower()
            if k in seen[kind]:
                errors.append(f"N4 {aid}: {kind} '{val}' also used by {seen[kind][k]}")
            seen[kind][k] = aid
        if len(a["shortDescription"]) > 72:
            errors.append(f"D1 {aid}: short description has {len(a['shortDescription'])} characters (max 72)")
        limit = L.kind_info(a)["descMax"]
        for env_name in envs:
            if len(L.env_description(cfg, a, env_name, "short")) > 80:
                errors.append(f"D1 {aid}: {env_name} short description exceeds 80 characters")
            if len(L.env_description(cfg, a, env_name, "full")) > limit:
                errors.append(f"D1 {aid}: {env_name} full description exceeds {limit} characters")
        c = L.contrast(d["icon"]["background"], d["icon"]["glyphColor"])
        if c < 4.5:
            errors.append(f"C1 {aid}: icon contrast {c}:1 below 4.5:1")
        glyph_by_journey.setdefault((a["journey"], a["glyph"]), []).append(aid)

        if skip_files:
            continue
        folder = root / "agents" / d["slug"] / "identity"
        scoped_envs = envs if L.is_scoped(a) else [prod]
        expected = []
        for env_name in scoped_envs:
            sfx = L.env_suffix(cfg, env_name)
            expected += [(f"color-192{sfx}.png", 192, False), (f"color-32{sfx}.png", 32, False)]
        expected.append(("outline-32.png", 32, True))
        for name, size, transparent in expected:
            p = folder / name
            if not p.exists():
                errors.append(f"F1 {aid}: missing {p.relative_to(root).as_posix()}")
                continue
            m = png_meta(p)
            if (m["width"], m["height"]) != (size, size):
                errors.append(f"F1 {aid}: {name} is {m['width']}x{m['height']}, expected {size}x{size}")
            if m["bytes"] > 100 * 1024:
                errors.append(f"F1 {aid}: {name} is {m['bytes']} bytes (max 100 KB)")
            alpha = corner_alpha(m)
            if transparent and alpha is None:
                errors.append(f"F2 {aid}: {name} has no alpha channel")
            elif transparent and alpha != 0:
                errors.append(f"F2 {aid}: {name} should have a transparent background")
            if not transparent and alpha not in (None, 255):
                errors.append(f"F2 {aid}: {name} must be opaque (full-bleed colour)")
        ij = folder / "identity.json"
        if not ij.exists():
            errors.append(f"F3 {aid}: missing identity.json")
        else:
            rec = L.load_json(ij)
            if rec.get("displayName", {}).get(prod) != base or rec.get("schemaName") != d["schemaName"]:
                errors.append(f"F3 {aid}: identity.json is out of date - rebuild")

    for (journey, glyph_name), ids in glyph_by_journey.items():
        if len(ids) > 1:
            warnings.append(f"W1 journey {journey}: glyph '{glyph_name}' used by {', '.join(ids)}")
    return {"agents": len(cfg["agents"]), "errors": errors, "warnings": warnings, "ok": not errors}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(L.ROOT))
    ap.add_argument("--json", help="write a JSON report")
    ap.add_argument("--skip-files", action="store_true", help="only check names and colours")
    args = ap.parse_args(argv)
    report = validate(Path(args.root).resolve(), args.skip_files)
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")
    for e in report["errors"]:
        print("ERROR", e)
    for w in report["warnings"]:
        print("WARN ", w)
    print(f"{report['agents']} agents checked: {len(report['errors'])} error(s), {len(report['warnings'])} warning(s)")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
