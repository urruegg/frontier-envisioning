#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Build the complete release bundle (one zip for people without GitHub access).

  python tools/build_release.py [--dist dist]

Needs dist/frontier-envisioning-plugin-<v>.zip and build/demo (python tools/dev.py package demo).
Writes dist/frontier-envisioning-<v>-complete.zip with START-HERE.md, the plugin package, its README,
licence and notices, the documentation, the CHANGELOG and the Caldova demo; then rewrites
dist/SHA256SUMS.txt for every archive in dist/. Entries carry the fixed archive date of the package build.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import DEMO_DIR, DEMO_HTML_NAME, DIST, PLUGIN, ROOT, load_module, plugin_version, sha256_file  # noqa: E402

ONTOLOGY_DOCUMENTS = ("ontology.ttl", "ontology.md", "data-agents.md", "data-products.md")

START = """# Frontier Envisioning {v} - start here

Microsoft Innovation Hub · complete package

This bundle holds the Frontier Envisioning plugin for Copilot Cowork, its documentation and the demo
built for the fictitious Caldova Industrial AG. The source of truth is the Git repository.
Published releases are built from tag v{v}; local unreleased builds are development candidates.

Private repository analyses and intake records are not included. The current distribution is for
Microsoft-internal use; a successful technical build is not external publication or IP clearance.
Retain all licences and product-icon notices.

The eight-skill plugin contains seven GA product skills and optional Preview FinOps.
Installation does not acknowledge FinOps use. Its grounding and cost model are not GA and
need refinement; each cost invocation requires explicit acknowledgement. The included demo
uses the core profile without FinOps. Process proposals retain their Fabric Preview and
mapping-verification limitations; GA product labels do not imply deployment or validated results.

## Install the plugin (two minutes)

1. Open Copilot Cowork and start a new chat.
2. Attach `install/frontier-envisioning-plugin-{v}.zip` (keep it zipped) and type: **Install the Frontier PlugIn**
3. Approve each step. Full guide: `README.md`.

## Contents

| Path | What it is |
|---|---|
| `install/frontier-envisioning-plugin-{v}.zip` | The plugin package (Cowork chat install or organisation catalogue) |
| `README.md`, `MIT.md`, `THIRD-PARTY-NOTICES.md` | Setup guide, licence (MIT) and the notice for Microsoft product icons |
| `CHANGELOG.md` | What changed in each release |
| `docs/prd.md` | Product requirements, release plan and product decisions |
| `docs/solution-design.md` | Architecture, components, flows and verification |
| `demo/` | The Caldova blueprint, the agent identity kit and its catalogue (all fictitious) |
| `demo/ontology/` | Ontology Turtle, design, data-agent and data-product proposals; no tenant import is performed |
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dist", default=str(DIST))
    a = ap.parse_args(argv)
    dist = Path(a.dist)
    v = plugin_version()
    bp = load_module(ROOT / "tools" / "build_package.py", "build_package")
    pkg = dist / f"frontier-envisioning-plugin-{v}.zip"
    demo_html = DEMO_DIR / DEMO_HTML_NAME
    kit_zips = sorted((DEMO_DIR / "identity").glob("*.zip"))
    catalogue = DEMO_DIR / "identity" / "caldova-agent-identity" / "catalog.html"
    report_path = DEMO_DIR / "build-report.json"
    ontology = [(DEMO_DIR / "ontology" / name, f"demo/ontology/{name}") for name in ONTOLOGY_DOCUMENTS]
    for need in (pkg, demo_html, catalogue, report_path, *(path for path, _ in ontology)):
        if not need.is_file():
            print(f"missing {need} - run: python tools/dev.py package demo")
            return 1
    if len(kit_zips) != 1:
        print("ERROR: core demo must contain exactly one complete identity archive - rebuild the demo")
        return 1
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR: core demo build report is invalid: {exc}")
        return 1
    if not isinstance(report, dict) or report.get("profile") != "core" \
            or report.get("status") != "built" or report.get("variant") != "full":
        print("ERROR: the complete bundle requires a built full core demo, not an optional Preview or incomplete variant")
        return 1
    model = report.get("value_finops")
    if report.get("finops") or (model is not None and (not isinstance(model, dict) or model.get("finops"))):
        print("ERROR: the core demo unexpectedly contains optional Preview FinOps output")
        return 1
    entries = [
        (START.format(v=v).encode("utf-8"), "START-HERE.md"),
        (pkg.read_bytes(), f"install/{pkg.name}"),
        ((PLUGIN / "README.md").read_bytes(), "README.md"),
        ((PLUGIN / "MIT.md").read_bytes(), "MIT.md"),
        ((PLUGIN / "THIRD-PARTY-NOTICES.md").read_bytes(), "THIRD-PARTY-NOTICES.md"),
        ((ROOT / "CHANGELOG.md").read_bytes(), "CHANGELOG.md"),
        ((ROOT / "docs" / "prd.md").read_bytes(), "docs/prd.md"),
        ((ROOT / "docs" / "solution-design.md").read_bytes(), "docs/solution-design.md"),
        (demo_html.read_bytes(), f"demo/{DEMO_HTML_NAME}"),
        (catalogue.read_bytes(), "demo/Caldova - agent identity catalogue.html"),
        (kit_zips[0].read_bytes(), f"demo/{kit_zips[0].name}"),
        *((path.read_bytes(), name) for path, name in ontology),
    ]
    errors = bp.distribution_errors(entries)
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    out = dist / f"frontier-envisioning-{v}-complete.zip"
    top = f"frontier-envisioning-{v}"
    with zipfile.ZipFile(out, "w") as zf:
        zf.comment = f"Frontier Envisioning {v} - complete package. Start with START-HERE.md".encode("utf-8")
        for data, name in entries:
            bp.add_bytes(zf, data, f"{top}/{name}")
    sums = "".join(f"{sha256_file(p)}  {p.name}\n" for p in sorted(dist.glob("*.zip")))
    (dist / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")
    print(f"bundle: {out} ({out.stat().st_size} bytes, {len(entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
