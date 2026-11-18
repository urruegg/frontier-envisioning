#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Check a process ontology and write what Fabric IQ and the build team need.

Usage:
  python build_ontology.py --ontology ontology.json [--blueprint blueprint.json] --out-dir <folder> [--strict]

Writes into <folder>:
  ontology.normalized.json  the checked model with the process map and counts (input for apply_ontology.py)
  ontology.ttl              OWL in Turtle: import into a new, empty ontology (preview) item in Fabric
  ontology.md               design document: entity types, relationships, the grounding of each entity type in the
                            Common Data Model, process map, semantic data layer (bronze, silver, gold, domains,
                            semantic models), data products, rules, metrics, data agents, operations agents, build
                            steps, readiness, risks, decisions, diagram
  data-agents.md            per data agent: instructions, source descriptions, bound tables and example questions
  data-products.md          per data product: owner, purpose, intended uses, output ports, quality, access, what is
                            open before publication; the set-up in Fabric domains and Purview Unified Catalog
Checks follow the ontology (preview) rules: names, string or integer keys, supported property types, one type per
property name, relationship ends, inheritance, at most five sources per data agent, known issues; standard entities,
bindings and data products are checked against the Common Data Model map and the data product standard. Errors stop the
build (exit 1); warnings are listed in the JSON summary (--strict makes them errors).
Standard library only; no network access.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology_lib import Rep, customer_context, customer_ontology, data_agent_kit, data_products_md, load_json, normalize, to_markdown, to_turtle, validate_route_assessments  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ontology", required=True)
    ap.add_argument("--blueprint", help="the blueprint the ontology belongs to (checks journeys and agents, adds the process map)")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--audience", choices=("internal", "customer"), default="internal")
    a = ap.parse_args(argv)
    try:
        onto = load_json(a.ontology)
        bp = load_json(a.blueprint) if a.blueprint else None
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    rep = Rep()
    if not validate_route_assessments(onto, rep):
        print(json.dumps({"status": "failed", "stats": {}, "files": {}, "errors": rep.errors, "warnings": rep.warnings}))
        return 1
    if a.audience == "customer":
        onto = customer_ontology(onto, bp)
        if onto is None:
            print(json.dumps({"status": "failed", "files": {}, "errors": ["ontology is internal-only"], "warnings": []}))
            return 1
        if bp:
            bp = customer_context(bp)
    norm = normalize(onto, bp, rep)
    out = Path(a.out_dir)
    failed = bool(rep.errors) or (a.strict and bool(rep.warnings))
    files = {}
    if not failed:
        # Validate and render everything before creating publishable output.
        files = {"normalized": out / "ontology.normalized.json", "turtle": out / "ontology.ttl", "design": out / "ontology.md",
                 "data_agents": out / "data-agents.md", "data_products": out / "data-products.md"}
        contents = {"normalized": json.dumps(norm, ensure_ascii=False, indent=1) + "\n",
                    "turtle": to_turtle(norm), "design": to_markdown(norm, bp),
                    "data_agents": data_agent_kit(norm), "data_products": data_products_md(norm, bp)}
        out.mkdir(parents=True, exist_ok=True)
        for key, path in files.items():
            path.write_text(contents[key], encoding="utf-8", newline="\n")
    print(json.dumps({"status": "failed" if failed else "ok", "stats": norm.get("stats"), "files": {k: str(v) for k, v in files.items()},
                      "errors": rep.errors, "warnings": rep.warnings}, ensure_ascii=False, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
