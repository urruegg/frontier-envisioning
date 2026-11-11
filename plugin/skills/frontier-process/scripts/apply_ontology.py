#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Write a process ontology into a Frontier Company Blueprint: the Ontology page (Part 2 Design).

Usage:
  python apply_ontology.py --blueprint blueprint.json --ontology ontology.json --out blueprint.json

The blueprint gets "ontology": the checked model (entity types with their Microsoft standard entity and binding,
relationship types, process map, OneLake sources, domains, semantic models, data products, rules, metrics, data agents,
operations agents, build steps, readiness, risks, decisions, sources). The page writes ontology.ttl and a short data
agent kit from it in the browser (the full files come from build_ontology.py), which keeps the page small. The IT readiness page gets a "Fabric IQ and
OneLake" group (once; existing statuses are kept) and the risk register picks up the ontology risks on the next
build. Errors in the ontology stop the apply (exit 1). Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology_lib import Rep, as_list, default_instructions, load_json, normalize  # noqa: E402

GROUP_ID = "fabric-iq"


def apply(bp: dict, onto: dict, rep: Rep) -> dict:
    norm = normalize(onto, bp, rep)
    if rep.errors:
        return bp
    norm.pop("ttl", None)
    norm.pop("kit", None)
    ents = {e["id"]: e for e in norm.get("entity_types", [])}
    for a in norm.get("data_agents", []):
        if not a.get("instructions"):
            a["instructions_default"] = default_instructions(a, norm, ents)
    old = bp.get("ontology") if isinstance(bp.get("ontology"), dict) else {}
    if old.get("workshop_notes") and not norm.get("workshop_notes"):
        norm["workshop_notes"] = old["workshop_notes"]
    bp["ontology"] = norm
    rd = bp.get("it_readiness")
    if isinstance(rd, dict):
        groups = rd.setdefault("groups", [])
        have = next((g for g in groups if isinstance(g, dict) and g.get("id") == GROUP_ID), None)
        status = {it.get("id"): it.get("status") for it in as_list((have or {}).get("items")) if isinstance(it, dict)}
        items = []
        for r in as_list(norm.get("readiness")):
            it = {k: r[k] for k in ("id", "item", "why", "owner", "stage", "src", "content_src", "internal", "visibility") if k in r}
            it["status"] = status.get(r["id"]) or r.get("status") or "open"
            items.append(it)
        group = {"id": GROUP_ID, "title": "Fabric IQ and OneLake (process ontology)", "logos": ["powerbi"], "items": items}
        if have:
            have.update(group)
        else:
            groups.append(group)
    return bp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--ontology", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        bp = load_json(a.blueprint)
        onto = load_json(a.ontology)
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    rep = Rep()
    bp = apply(bp, onto, rep)
    if rep.errors:
        print(json.dumps({"status": "failed", "errors": rep.errors, "warnings": rep.warnings}, ensure_ascii=False, indent=1))
        return 1
    Path(a.out).write_text(json.dumps(bp, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "ok", "out": a.out, "stats": bp["ontology"]["stats"], "warnings": rep.warnings}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
