#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Merge workshop feedback exported from the blueprint HTML into the blueprint JSON.

The HTML's Discovery view exports "<customer>-workshop-feedback.json":
  {"type": "frontier-blueprint-feedback", "blueprint": "<meta.id>", "version": "0.1",
   "exported": "2026-11-12T16:40:00Z",
   "validations": {"agent:D3-A05": {"status": "validated", "note": "..."},
                   "uc:UC09": {"status": "adjusted", "note": "..."}},
   "discovery":   {"D3-Q02": {"status": "answered", "note": "...", "discussed": true}}}

Usage:
  python merge_feedback.py --blueprint blueprint.json --feedback feedback.json --out blueprint.v0.2.json
         [--workshop-title "Envisioning workshop"] [--workshop-date 2026-11-12] [--no-bump]

Effects:
  * agents / use cases: status <- feedback status; note appended to "workshop_notes"
  * discovery questions: status <- feedback status; a note becomes the answer
    (the previous answer is kept in "previous_answer"), cited to a new workshop
    evidence item (type "workshop", visibility "customer")
  * meta.version is bumped (0.1 -> 0.2), meta.date set to today, meta.status_note updated
  * Agent identity page feedback ("identity:names"): kept in "identity_feedback" for the identity review
  * IT readiness ("ready:<id>"): status (open, in progress, done, blocked; answered; agreed) and notes of the item
  * architecture decisions ("adr:<id>"): verdict validated -> status "agreed"; adjusted / rejected kept;
    note appended to the decision's "workshop_notes" and the workshop evidence added to its "src"
  * digital feedback loop ("loop:<area>", Overview): status and notes of the area (engage_customers, ...)
  * assumption verdicts ("ass:<id>", with an agreed value) and the FinOps model ("finops:model"): kept in
    "assumption_feedback"; frontier-value-case's merge_value_feedback.py applies them to value.json and finops.json
Prints a JSON summary; unknown ids are reported, never invented.
Standard library only; no network access.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

VALID = {"validated", "adjusted", "adjust", "rejected", "open"}
QVALID = {"open", "partial", "answered"}


def as_list(x):
    return x if isinstance(x, list) else ([] if x in (None, "") else [x])


def bump(v: str) -> str:
    try:
        major, minor = (str(v).split(".") + ["0"])[:2]
        return f"{int(major)}.{int(minor) + 1}"
    except ValueError:
        return f"{v}.1"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--feedback", required=True, nargs="+", help="one or more exported feedback files")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workshop-title", default="Envisioning workshop")
    ap.add_argument("--workshop-date", default=None, help="YYYY-MM-DD (default: date of the export)")
    ap.add_argument("--no-bump", action="store_true", help="keep the version number")
    a = ap.parse_args(argv)

    try:
        bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        print(f"ERROR: cannot read blueprint: {e}", file=sys.stderr)
        return 2

    agents, ucs, qs = {}, {}, {}
    for d in as_list(bp.get("domains")):
        if isinstance(d.get("orchestrator"), dict) and d["orchestrator"].get("id"):
            agents[d["orchestrator"]["id"]] = d["orchestrator"]
        for x in as_list(d.get("agents")):
            if x.get("id"):
                agents[x["id"]] = x
        for u in as_list(d.get("use_cases")):
            if u.get("id"):
                ucs[u["id"]] = u
        for cat, items in (d.get("discovery") or {}).items():
            for q in as_list(items):
                if isinstance(q, dict) and q.get("id"):
                    qs[q["id"]] = q
    for u in as_list(bp.get("use_cases")):
        if u.get("id"):
            ucs[u["id"]] = u
    if not qs and any((d.get("discovery") or {}) for d in as_list(bp.get("domains"))):
        print("WARN: discovery questions have no ids; build the blueprint with --save-normalized first", file=sys.stderr)

    summary = {"agents_updated": 0, "use_cases_updated": 0, "questions_updated": 0, "unknown": [], "files": []}
    evidence = bp.setdefault("evidence", [])
    existing = {e.get("id") for e in evidence}
    for fpath in a.feedback:
        try:
            fb = json.loads(Path(fpath).read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as e:
            print(f"ERROR: cannot read feedback {fpath}: {e}", file=sys.stderr)
            return 2
        if fb.get("type") != "frontier-blueprint-feedback":
            print(f"ERROR: {fpath} is not a blueprint feedback export", file=sys.stderr)
            return 2
        bid = (bp.get("meta") or {}).get("id")
        if fb.get("blueprint") and bid and fb["blueprint"] != bid:
            print(f"ERROR: feedback is for blueprint {fb['blueprint']!r}, not {bid!r}", file=sys.stderr)
            return 1
        day = a.workshop_date or str(fb.get("exported", ""))[:10] or _dt.date.today().isoformat()
        n = 1
        while f"W{n:02d}" in existing:
            n += 1
        wid = f"W{n:02d}"
        existing.add(wid)
        evidence.append({"id": wid, "type": "workshop", "title": f"{a.workshop_title} ({day})", "date": day,
                         "source": "Workshop notes exported from the blueprint", "visibility": "customer",
                         "summary": "Validation and answers captured live during the workshop."})
        summary["files"].append({"file": fpath, "evidence_id": wid})

        for key, val in (fb.get("validations") or {}).items():
            kind, _, ident = key.partition(":")
            if kind == "ready":
                # IT readiness: status and note of a preparation item, readiness check, workstation check, question or decision
                rd = bp.get("it_readiness") if isinstance(bp.get("it_readiness"), dict) else {}
                pool = [it for g in as_list(rd.get("groups")) if isinstance(g, dict) for it in as_list(g.get("items"))]
                pool += [x for k in ("checks", "workstation", "questions", "decisions") for x in as_list(rd.get(k))]
                item = next((x for x in pool if isinstance(x, dict) and x.get("id") == ident), None)
                if item is None:
                    summary["unknown"].append(key)
                    continue
                st = str(val.get("status", "")).lower()
                if st:
                    item["status"] = st
                if val.get("note"):
                    item.setdefault("workshop_notes", []).append({"date": day, "note": val["note"], "src": [wid]})
                summary["readiness_updated"] = summary.get("readiness_updated", 0) + 1
                continue
            if kind == "adr":
                # architecture decision record (Target architecture > Decisions): workshop verdict and note
                arch = bp.get("architecture") if isinstance(bp.get("architecture"), dict) else {}
                dec = next((x for x in as_list(arch.get("decisions")) if isinstance(x, dict) and x.get("id") == ident), None)
                if dec is None:
                    summary["unknown"].append(key)
                    continue
                st = str(val.get("status", "")).lower()
                if st in ("validated", "agreed", "accepted"):
                    dec["status"] = "agreed"
                elif st in ("adjust", "adjusted", "rejected", "open"):
                    dec["status"] = {"adjust": "adjusted", "open": "proposed"}.get(st, st)
                if val.get("note"):
                    dec.setdefault("workshop_notes", []).append({"date": day, "note": val["note"], "src": [wid]})
                dec["src"] = sorted(set(as_list(dec.get("src")) + [wid]))
                summary["decisions_updated"] = summary.get("decisions_updated", 0) + 1
                continue
            if kind == "loop":
                # digital feedback loop (Overview): verdict and note of one area
                fl = bp.get("feedback_loop") if isinstance(bp.get("feedback_loop"), dict) else {}
                q = next((x for x in as_list(fl.get("quadrants")) if isinstance(x, dict) and x.get("pillar") == ident), None)
                if q is None:
                    summary["unknown"].append(key)
                    continue
                st = str(val.get("status", "")).lower()
                if st in VALID:
                    q["status"] = "adjusted" if st == "adjust" else st
                if val.get("note"):
                    q.setdefault("workshop_notes", []).append({"date": day, "note": val["note"], "src": [wid]})
                q["src"] = sorted(set(as_list(q.get("src")) + [wid]))
                summary["loop_updated"] = summary.get("loop_updated", 0) + 1
                continue
            if kind in ("ass", "finops"):
                # value and cost assumptions (and the FinOps model): kept for frontier-value-case's merge_value_feedback.py
                bp.setdefault("assumption_feedback", []).append({k: v for k, v in {
                    "date": day, "id": ident, "kind": kind, "status": str(val.get("status", "")).lower() or None,
                    "value": val.get("value"), "note": val.get("note") or None, "src": [wid]}.items() if v is not None and v != ""})
                summary["assumption_feedback"] = summary.get("assumption_feedback", 0) + 1
                continue
            if kind == "identity":
                # feedback on the Agent identity page (names, colours, icons): kept for the identity review
                bp.setdefault("identity_feedback", []).append({k: v for k, v in {
                    "date": day, "topic": ident, "status": str(val.get("status", "")).lower() or None,
                    "note": val.get("note") or None, "src": [wid]}.items() if v})
                summary["identity_feedback"] = summary.get("identity_feedback", 0) + 1
                continue
            target = agents.get(ident) if kind == "agent" else (ucs.get(ident) if kind == "uc" else None)
            if target is None:
                summary["unknown"].append(key)
                continue
            st = str(val.get("status", "")).lower()
            if st in VALID:
                target["status"] = "adjusted" if st == "adjust" else st
            if val.get("note"):
                target.setdefault("workshop_notes", []).append({"date": day, "note": val["note"], "src": [wid]})
            target["src"] = sorted(set(as_list(target.get("src")) + [wid]))
            summary["agents_updated" if kind == "agent" else "use_cases_updated"] += 1

        for qid, val in (fb.get("discovery") or {}).items():
            q = qs.get(qid)
            if q is None:
                summary["unknown"].append(qid)
                continue
            st = str(val.get("status", "")).lower()
            if st in QVALID:
                q["status"] = st
            if val.get("note"):
                if q.get("answer") and q["answer"] != val["note"]:
                    q["previous_answer"] = q["answer"]
                q["answer"] = val["note"]
                q["src"] = sorted(set(as_list(q.get("src")) + [wid]))
            if val.get("discussed"):
                q["discussed"] = True
            summary["questions_updated"] += 1

    meta = bp.setdefault("meta", {})
    if not a.no_bump:
        meta["version"] = bump(meta.get("version", "0.1"))
    meta["date"] = _dt.date.today().isoformat()
    meta["status_note"] = (f"Updated with workshop feedback ({', '.join(f['evidence_id'] for f in summary['files'])}); "
                           "items marked Validated were confirmed by the customer, the rest remain hypotheses.")
    Path(a.out).write_text(json.dumps(bp, ensure_ascii=False, indent=1), encoding="utf-8")
    summary["out"] = a.out
    summary["version"] = meta.get("version")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
