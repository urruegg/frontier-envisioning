#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Generate or check the tracked, offline Caldova documentation showcase.

  python tools/build_docs_demo.py
  python tools/build_docs_demo.py --check [--demo build/demo]

Generation builds the core demo and captures five real Playwright views.
Checks need no browser. Only meta.generated is ignored when comparing a fresh
build with the dated snapshot; all stored bytes and relevant sources are hashed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import DEMO_DIR, DEMO_HTML_NAME, ROOT, call_main, load_module, sha256_bytes  # noqa: E402

VIEWS = (("overview", "#/overview"), ("org-model", "#/org"), ("agents", "#/agents/D3-A05"),
         ("agent-identity", "#/identity"), ("ontology", "#/ontology"))
DATA = re.compile(rb'<script\b[^>]*\bid="bp-data"[^>]*>(.*?)</script>', re.S)
HTML = Path("docs") / "demo" / "caldova-blueprint.html"
MANIFEST = Path("docs") / "demo" / "manifest.json"
IMAGES = Path("docs") / "images" / "caldova"


def blueprint(raw: bytes) -> dict:
    match = DATA.search(raw)
    if match is None:
        raise ValueError("blueprint data island is missing")
    data = json.loads(match[1])
    if not isinstance(data, dict) or not isinstance(data.get("meta"), dict):
        raise ValueError("blueprint metadata is invalid")
    return data


def canonical_html(raw: bytes) -> bytes:
    blueprint(raw)
    match = DATA.search(raw)
    text = match[1].decode("utf-8")
    meta_start, meta_end = member_span(text, "meta")
    start, end = member_span(text[meta_start:meta_end], "generated")
    start, end = start + meta_start, end + meta_start
    if not re.fullmatch(r'"\d{4}-\d{2}-\d{2}"', text[start:end]):
        raise ValueError("meta.generated must be a literal ISO calendar date")
    dt.date.fromisoformat(text[start + 1:end - 1])
    canonical = (text[:start] + '"GENERATION-DAY"' + text[end:]).encode("utf-8")
    return raw[:match.start(1)] + canonical + raw[match.end(1):]


def member_span(text: str, member: str) -> tuple[int, int]:
    """Locate a direct JSON member without rewriting unrelated JSON bytes."""
    decoder = json.JSONDecoder()
    position = len(text) - len(text.lstrip())
    if text[position:position + 1] != "{":
        raise ValueError("expected a JSON object")
    position += 1
    found = None
    while True:
        position += len(text[position:]) - len(text[position:].lstrip())
        if text[position:position + 1] == "}":
            break
        key, position = decoder.raw_decode(text, position)
        position += len(text[position:]) - len(text[position:].lstrip())
        if text[position:position + 1] != ":":
            raise ValueError("invalid JSON member")
        position += 1
        position += len(text[position:]) - len(text[position:].lstrip())
        start = position
        _, position = decoder.raw_decode(text, position)
        if key == member:
            if found is not None:
                raise ValueError("duplicate JSON member: " + member)
            found = (start, position)
        position += len(text[position:]) - len(text[position:].lstrip())
        if text[position:position + 1] == "}":
            break
        if text[position:position + 1] != ",":
            raise ValueError("invalid JSON object separator")
        position += 1
    if found is None:
        raise ValueError("required JSON member is missing: " + member)
    return found


def require_core(raw: bytes) -> dict:
    data = blueprint(raw)

    def has_costs(value):
        if isinstance(value, dict):
            return any((key in ("finops", "finops_preview") and item is not None)
                       or has_costs(item) for key, item in value.items())
        return isinstance(value, list) and any(has_costs(item) for item in value)

    if has_costs(data):
        raise ValueError("documentation sample must be core-only, without FinOps or Preview-derived figures")
    if data["meta"].get("customer") != "Caldova Industrial AG":
        raise ValueError("documentation sample must use fictitious Caldova Industrial AG")
    ontology = data.get("ontology")
    if not isinstance(data.get("identity"), dict) or not data["identity"] \
            or not isinstance(ontology, dict) or not isinstance(ontology.get("entity_types"), list) \
            or not ontology["entity_types"]:
        raise ValueError("core sample must include identity and the requested ontology")
    if not isinstance(data["meta"].get("plugin_version"), str):
        raise ValueError("sample plugin version is missing")
    value = data.get("value_case")
    if not isinstance(value, dict) or not isinstance(value.get("totals"), dict) or value.get("inputs_needed"):
        raise ValueError("core sample is missing the ordinary value results")
    results = {case.get("id"): case.get("business_value")
               for domain in data.get("domains", []) if isinstance(domain, dict)
               for case in domain.get("use_cases", []) if isinstance(case, dict)}
    for result in (value["totals"], results.get("UC05"), results.get("UC09")):
        if not isinstance(result, dict) or any(
            type(result.get(key)) not in (int, float) or not math.isfinite(result[key])
            for key in ("npv", "economic_year", "budget_year")
        ):
            raise ValueError("core sample is missing calculated ordinary value for UC05/UC09")
    return data


def source_fingerprint(root: Path) -> str:
    paths = {path for name in ("skeleton.html", "template.js", "template.css")
             if (path := root / "src" / "renderer" / name).is_file()}
    for skill in ("frontier-blueprint", "frontier-agent-identity", "frontier-value-case", "frontier-process"):
        for folder in ("scripts", "templates", "examples", "kit"):
            paths.update(path for path in (root / "plugin" / "skills" / skill / folder).rglob("*")
                         if path.is_file() and "__pycache__" not in path.parts)
    for name in ("build_demo.py", "demo_raster.py", "fe_lib.py", "build_docs_demo.py", "capture_docs.mjs"):
        if (path := root / "tools" / name).is_file():
            paths.add(path)
    for folder, name in ((".claude-plugin", "plugin.json"), ("package", "manifest.json")):
        if (path := root / "plugin" / folder / name).is_file():
            paths.add(path)
    paths.update(path for path in (root / "tests" / "fixtures").glob("caldova-raster-*-inputs.json")
                 if path.is_file())
    rows = [(path.relative_to(root).as_posix(), sha256_bytes(path.read_bytes()))
            for path in sorted(paths, key=lambda p: p.relative_to(root).as_posix())]
    return sha256_bytes(json.dumps(rows, separators=(",", ":")).encode())


def png_size(raw: bytes) -> tuple[int, int]:
    if len(raw) < 33 or raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
        raise ValueError("capture did not produce a PNG")
    width, height, depth, colour, compression, filtering, interlace = struct.unpack(">IIBBBBB", raw[16:29])
    if (width, height) != (1440, 1000) or depth != 8 or colour not in (2, 6) \
            or compression or filtering or interlace:
        raise ValueError("capture must be a non-interlaced 1440 x 1000 RGB/RGBA PNG")
    position, chunks, ended = 8, [], False
    while position + 12 <= len(raw):
        length = struct.unpack(">I", raw[position:position + 4])[0]
        kind = raw[position + 4:position + 8]
        end = position + 12 + length
        if end > len(raw):
            raise ValueError("PNG capture is truncated")
        payload = raw[position + 8:end - 4]
        if zlib.crc32(kind + payload) != struct.unpack(">I", raw[end - 4:end])[0]:
            raise ValueError("PNG capture has an invalid chunk CRC")
        if kind == b"IHDR" and (position != 8 or length != 13):
            raise ValueError("PNG capture must contain exactly one 13-byte header")
        if kind == b"IDAT":
            chunks.append(payload)
        elif kind == b"IEND":
            if length:
                raise ValueError("PNG end chunk is malformed")
            ended = True
            position = end
            break
        position = end
    if not ended or position != len(raw) or not chunks:
        raise ValueError("PNG capture is incomplete")
    stride = 1 + width * (3 if colour == 2 else 4)
    expected = stride * height
    decoder = zlib.decompressobj()
    try:
        pixels = decoder.decompress(b"".join(chunks), expected + 1)
    except zlib.error as exc:
        raise ValueError("PNG pixel data is invalid") from exc
    if len(pixels) != expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail \
            or any(value > 4 for value in pixels[::stride]):
        raise ValueError("PNG pixel rows are incomplete or invalid")
    return width, height


def require_capture(report: dict) -> list[dict]:
    if not isinstance(report, dict) or not isinstance(report.get("screenshots"), list):
        raise ValueError("capture metadata is invalid")
    settings = {"viewport": {"width": 1440, "height": 1000}, "color_scheme": "light",
                "reduced_motion": "reduce", "locale": "en-GB", "timezone": "UTC"}
    if any(report.get(key) != value for key, value in settings.items()):
        raise ValueError("capture settings differ from the documented viewport/scheme/locale/timezone")
    if any(not isinstance(report.get(key), str) or not report[key].strip() for key in ("browser", "playwright")):
        raise ValueError("capture browser/tool versions are missing")
    rows = report["screenshots"]
    actual = [(row.get("name"), row.get("route"), row.get("file"))
              for row in rows if isinstance(row, dict)]
    if len(actual) != len(rows) or actual != [(name, route, name + ".png") for name, route in VIEWS]:
        raise ValueError("capture must contain exactly the five requested views")
    if any((row.get("width"), row.get("height")) != (1440, 1000) for row in rows):
        raise ValueError("capture dimensions must be 1440 x 1000")
    return rows


def capture_views(source: Path, output: Path) -> dict:
    env = dict(os.environ)
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / "build" / "playwright-browsers"))
    result = subprocess.run(
        ["node", str(ROOT / "tools" / "capture_docs.mjs"), "--html", str(source), "--out", str(output)],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode:
        raise ValueError("Playwright capture failed: " + (result.stderr or result.stdout)[-1500:])
    report = json.loads(result.stdout)
    if not isinstance(report, dict):
        raise ValueError("Playwright capture returned an invalid report")
    return report


def publish(source: Path, root: Path = ROOT, *, capture=capture_views) -> dict:
    raw = source.read_bytes()
    data = require_core(raw)
    with tempfile.TemporaryDirectory(prefix="frontier-docs-") as directory:
        staged = Path(directory)
        staged_html = staged / "caldova-blueprint.html"
        staged_html.write_bytes(raw)
        images = staged / "images"
        report = capture(staged_html, images)
        rows = require_capture(report)
        if {p.name for p in images.iterdir()} != {name + ".png" for name, _ in VIEWS}:
            raise ValueError("capture must contain exactly the five requested views")
        outputs = {HTML: raw}
        for row in rows:
            payload = (images / row["file"]).read_bytes()
            size = png_size(payload)
            if size != (1440, 1000) or size != (row.get("width"), row.get("height")):
                raise ValueError("capture dimensions must be 1440 x 1000")
            row["sha256"] = sha256_bytes(payload)
            outputs[IMAGES / row["file"]] = payload
        manifest = {
            "schema": "frontier-docs-demo/1.0", "profile": "core",
            "plugin_version": data["meta"]["plugin_version"], "source_sha256": source_fingerprint(root),
            "html": {"file": HTML.name, "sha256": sha256_bytes(raw),
                     "canonical_sha256": sha256_bytes(canonical_html(raw)),
                     "generated": data["meta"].get("generated")},
            "capture": report,
        }
        outputs[MANIFEST] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        for relative, payload in outputs.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    return manifest


def verify(root: Path = ROOT, fresh_html: Path | None = None) -> list[str]:
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("schema") != "frontier-docs-demo/1.0":
            raise ValueError("documentation manifest schema is invalid")
        raw = (root / HTML).read_bytes()
        data = require_core(raw)
        if manifest.get("profile") != "core" or manifest.get("plugin_version") != data["meta"]["plugin_version"]:
            raise ValueError("documentation profile/version differs from the sample")
        if manifest.get("source_sha256") != source_fingerprint(root):
            raise ValueError("demo sources changed; regenerate with python tools/dev.py docs-demo")
        info = manifest["html"]
        if info["file"] != HTML.name or info["sha256"] != sha256_bytes(raw) \
                or info["canonical_sha256"] != sha256_bytes(canonical_html(raw)):
            raise ValueError("documentation HTML hash differs from its manifest")
        rows = require_capture(manifest["capture"])
        if {p.name for p in (root / IMAGES).iterdir()} != {name + ".png" for name, _ in VIEWS}:
            raise ValueError("documentation screenshot directory has unexpected files")
        for row in rows:
            payload = (root / IMAGES / row["file"]).read_bytes()
            if png_size(payload) != (1440, 1000) or row["sha256"] != sha256_bytes(payload):
                raise ValueError("documentation screenshot hash/dimensions differ: " + row["name"])
        if fresh_html is not None and canonical_html(fresh_html.read_bytes()) != canonical_html(raw):
            raise ValueError("tracked sample differs from the actual core build; regenerate docs-demo")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [str(exc)]
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--demo", type=Path, help="existing core demo directory (generation builds it when omitted)")
    args = ap.parse_args(argv)
    try:
        source = (args.demo / DEMO_HTML_NAME) if args.demo is not None else DEMO_DIR / DEMO_HTML_NAME
        if args.check:
            errors = verify(fresh_html=source if args.demo is not None else None)
            if errors:
                for error in errors:
                    print("ERROR:", error)
                return 1
            print("Documentation demo: core HTML, source fingerprint and five screenshots verified.")
        else:
            if args.demo is None:
                code, output = call_main(load_module(ROOT / "tools" / "build_demo.py", "fe_docs_core"), [])
                if code:
                    print(output)
                    return code
            manifest = publish(source)
            print(json.dumps({"html": str(HTML), "images": str(IMAGES), "profile": manifest["profile"],
                              "screenshots": len(manifest["capture"]["screenshots"])}, indent=1))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
