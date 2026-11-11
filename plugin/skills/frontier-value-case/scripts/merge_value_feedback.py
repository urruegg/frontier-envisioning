#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Applies the workshop's assumption verdicts to the value case and the FinOps model.

Usage:
  python merge_value_feedback.py --value value.json [--finops finops.json] --feedback <workshop-feedback.json> [...]
         [--date 2026-11-12] [--no-bump]

Reads the blueprint's feedback export ("validations": {"ass:ASS-003": {"status": "adjusted", "value": 12, "note": ...}})
or a merged blueprint with "assumption_feedback". Per assumption: validated -> confirmed; adjusted (or an agreed
value) -> base = the agreed value, low and high widened to include it; rejected -> rejected (levers that depend on
it are left out until a new value is agreed); open -> unchanged. Every change is written to the file's changelog
with the date and the note, and the version is bumped (0.1 -> 0.2). Recalculate afterwards: finops_calc.py and
value_calc.py, or the blueprint build with --value and --finops. Unknown ids are reported, never invented.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

from value_calc import preview_for

MAP = {"validated": "confirmed", "confirmed": "confirmed", "adjusted": "adjusted", "rejected": "rejected"}


def verdicts_from(doc: dict) -> list:
    out = []
    if doc.get("type") == "frontier-blueprint-feedback":
        day = str(doc.get("exported", ""))[:10] or None
        for k, v in (doc.get("validations") or {}).items():
            kind, _, ident = k.partition(":")
            if kind == "ass" and isinstance(v, dict):
                out.append({"id": ident, "status": v.get("status"), "value": v.get("value"), "note": v.get("note"), "date": day})
    for f in doc.get("assumption_feedback") or []:
        if f.get("kind") == "ass":
            out.append({"id": f.get("id"), "status": f.get("status"), "value": f.get("value"), "note": f.get("note"), "date": f.get("date"), "src": f.get("src")})
    return out


def bump(v: str) -> str:
    try:
        major, minor = str(v).split(".")[:2]
        return f"{major}.{int(minor) + 1}"
    except (ValueError, IndexError):
        return str(v)


def merge(docs: list, verdicts: list, day: str, *, acknowledge_finops_preview: bool = False) -> dict:
    previews = [preview_for(doc, acknowledge_finops_preview=acknowledge_finops_preview,
                            fin=docs[1] if len(docs) > 1 else None, operation="feedback")
                for doc in docs]
    where = {a["id"]: (d, a) for d in docs for a in d.get("assumptions", []) or []}
    changes, unknown, touched = [], [], set()
    for vd in verdicts:
        hit = where.get(vd.get("id"))
        if not hit:
            unknown.append(vd.get("id"))
            continue
        doc, a = hit
        st = MAP.get(str(vd.get("status") or "").lower())
        val = vd.get("value")
        before = {"status": a.get("status", "open"), "base": a.get("base"), "src": list(a.get("src") or [])}
        if isinstance(val, (int, float)) and not isinstance(val, bool) and st != "rejected":
            if a.get("base") != val:
                a["previous_base"] = a.get("base")
                a["base"] = val
                if a.get("low") is not None and val < a["low"]:
                    a["low"] = val
                if a.get("high") is not None and val > a["high"]:
                    a["high"] = val
                st = "adjusted"
            st = st or "confirmed"
        if st:
            a["status"] = st
        when = vd.get("date") or day
        if vd.get("note"):
            a.setdefault("workshop_notes", []).append({"date": when, "note": vd["note"]})
        if vd.get("src"):
            a["src"] = sorted(set(list(a.get("src") or []) + list(vd["src"])))
        after = {"status": a.get("status", "open"), "base": a.get("base"), "src": list(a.get("src") or [])}
        if after != before or vd.get("note"):
            changes.append({"id": a["id"], "statement": a.get("statement"), "from": before, "to": after, "note": vd.get("note"), "date": when})
            touched.add(id(doc))
    # The FinOps register also uses value assumptions. Any change in this
    # explicit action chain invalidates both cost and dependent value caches.
    invalidated = set(touched)
    if len(docs) > 1 and touched:
        invalidated.update(id(doc) for doc in docs)
    summary = {"changes": changes, "unknown": unknown, "touched": touched, "invalidated": invalidated}
    for doc, preview in zip(docs, previews):
        if preview:
            doc["finops_preview"] = preview
        if id(doc) in invalidated:
            doc.pop("results", None)
    if any(previews):
        preview = preview_for(docs[0], acknowledge_finops_preview=acknowledge_finops_preview,
                              fin=docs[1] if len(docs) > 1 else None, operation="feedback")
        if invalidated:
            preview["calculation_status"] = "invalidated-recalculate-required"
        for doc in docs:
            doc["finops_preview"] = preview
        summary["finops_preview"] = preview
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--value", required=True)
    ap.add_argument("--finops")
    ap.add_argument("--feedback", required=True, nargs="+")
    ap.add_argument("--date", help="workshop date (default: the export date or today)")
    ap.add_argument("--no-bump", action="store_true")
    ap.add_argument("--acknowledge-finops-preview", action="store_true")
    a = ap.parse_args(argv)
    paths = [Path(a.value)] + ([Path(a.finops)] if a.finops else [])
    try:
        docs = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
        for doc in docs:
            preview_for(doc, acknowledge_finops_preview=a.acknowledge_finops_preview,
                        fin=docs[1] if a.finops else None, operation="feedback")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    verdicts = []
    for f in a.feedback:
        try:
            verdicts += verdicts_from(json.loads(Path(f).read_text(encoding="utf-8-sig")))
        except (OSError, ValueError) as exc:
            print(f"ERROR: cannot read feedback {f}: {exc}", file=sys.stderr)
            return 2
    day = a.date or _dt.date.today().isoformat()
    try:
        res = merge(docs, verdicts, day, acknowledge_finops_preview=a.acknowledge_finops_preview)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    # Prepare all changed models before writing any, including the new versions.
    updates = []
    for p, d in zip(paths, docs):
        mine = [c for c in res["changes"] if any(x.get("id") == c["id"] for x in d.get("assumptions", []))]
        if mine or id(d) in res["invalidated"]:
            old = d.get("version", "0.1")
            if not a.no_bump:
                d["version"] = bump(old)
            d.setdefault("changelog", []).append({"date": day, "version": d.get("version"), "from_version": old,
                                                  "summary": (f"{len(mine)} assumption(s) changed in the workshop" if mine else
                                                              "Dependent calculation invalidated after cost/value feedback"),
                                                  "changes": mine})
            d.pop("results", None)
            updates.append((p, d))
    try:
        for _, d in updates:
            preview = preview_for(docs[0], acknowledge_finops_preview=a.acknowledge_finops_preview,
                                  fin=docs[1] if a.finops else None, operation="feedback")
            if preview:
                if id(d) in res["invalidated"]:
                    preview["calculation_status"] = "invalidated-recalculate-required"
                d["finops_preview"] = preview
                res["finops_preview"] = preview
    except (ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for p, d in updates:
        p.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({**({"finops_preview": res["finops_preview"]} if "finops_preview" in res else {}),
                      "verdicts": len(verdicts), "changed": len(res["changes"]), "unknown": res["unknown"],
                      "changes": [{"id": c["id"], "from": c["from"], "to": c["to"]} for c in res["changes"]],
                      "next": "recalculate: finops_calc.py, then value_calc.py (or build the blueprint with --value and --finops)"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
