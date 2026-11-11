#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Apply the workshop verdicts from the blueprint's Ontology page to the process ontology.

Usage:
  python merge_ontology_feedback.py --ontology ontology.json --feedback <customer>-workshop-feedback.json
         --out ontology.v0.2.json [--workshop-date 2026-11-12] [--no-bump]

The feedback export of the blueprint carries "onto:<id>" verdicts (validated, adjusted, rejected, open) and notes for
entity types, relationship types, data agents, operations agents, data products (DP-..) and the model as a whole
("onto:model"); data products derived from the data agents are written into the ontology first. Each verdict
sets the element's status and appends the note to its "workshop_notes"; a validated model sets meta.status. Unknown
ids are reported, never invented. The version is bumped (0.1 -> 0.2) unless --no-bump. Standard library only.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology_lib import Rep, as_list, load_json, normalize  # noqa: E402

VERDICT = {"validated": "validated", "agreed": "validated", "adjust": "adjusted", "adjusted": "adjusted", "rejected": "rejected", "open": "hypothesis"}


def bump(v: str) -> str:
    try:
        major, minor = str(v).split(".")[:2]
        return f"{int(major)}.{int(minor) + 1}"
    except ValueError:
        return "0.2"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ontology", required=True)
    ap.add_argument("--feedback", required=True, nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workshop-date", default=None)
    ap.add_argument("--no-bump", action="store_true")
    a = ap.parse_args(argv)
    try:
        onto = load_json(a.ontology)
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    rep = Rep()
    normalized = normalize(onto, None, rep)
    if rep.errors:
        print(json.dumps({"status": "failed", "errors": rep.errors, "warnings": rep.warnings}, ensure_ascii=False, indent=1))
        return 1
    # Feedback targets the IDs shown by the normalized build, including rows
    # whose authored input did not yet have an ID. Do not persist derived gaps.
    for key in ("relationship_types", "data_agents", "operations_agents"):
        for row, norm in zip(as_list(onto.get(key)), normalized[key]):
            if isinstance(row, dict):
                row.setdefault("id", norm["id"])
    if not as_list(onto.get("data_products")):
        derived = normalized.get("data_products") or []
        onto["data_products"] = [{k: v for k, v in d.items() if k != "gaps"} for d in derived]
    pools = {}
    for key in ("entity_types", "relationship_types", "data_agents", "operations_agents", "data_products"):
        for x in as_list(onto.get(key)):
            if isinstance(x, dict) and x.get("id"):
                pools[x["id"]] = x
    summary = {"changed": 0, "unknown": [], "files": []}
    last_day = None
    for f in a.feedback:
        try:
            fb = load_json(f)
        except (OSError, ValueError) as e:
            print(f"ERROR: cannot read feedback {f}: {e}", file=sys.stderr)
            return 2
        if fb.get("type") != "frontier-blueprint-feedback":
            print(f"ERROR: {f} is not a blueprint feedback export", file=sys.stderr)
            return 2
        day = a.workshop_date or str(fb.get("exported", ""))[:10] or str((onto.get("meta") or {}).get("date") or "")
        summary["files"].append(f)
        for key, val in (fb.get("validations") or {}).items():
            kind, _, ident = key.partition(":")
            if kind != "onto":
                continue
            if not isinstance(val, dict) or str(val.get("status", "")).lower() not in VERDICT or ("note" in val and not isinstance(val["note"], str)):
                summary.setdefault("invalid", []).append(key)
                continue
            st = VERDICT.get(str(val.get("status", "")).lower())
            if ident == "model":
                tgt = onto.setdefault("meta", {})
                notes_target = onto
            else:
                tgt = pools.get(ident)
                if tgt is None:
                    if key not in summary["unknown"]:
                        summary["unknown"].append(key)
                    continue
                notes_target = tgt
            before = copy.deepcopy(tgt)
            old_notes = copy.deepcopy(notes_target.get("workshop_notes"))
            if st:
                tgt["status"] = st
            if val.get("note"):
                note = {"date": day, "note": val["note"]}
                for field in ("src", "content_src", "internal", "visibility"):
                    if field in val:
                        note[field] = copy.deepcopy(val[field])
                notes = notes_target.setdefault("workshop_notes", [])
                if note not in notes:
                    notes.append(note)
            if tgt != before or notes_target.get("workshop_notes") != old_notes:
                summary["changed"] += 1
                last_day = day
    meta = onto.setdefault("meta", {})
    if not a.no_bump and summary["changed"]:
        meta["version"] = bump(meta.get("version", "0.1"))
    if last_day:
        meta["date"] = last_day
    Path(a.out).write_text(json.dumps(onto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    summary.update({"out": a.out, "version": meta.get("version")})
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
