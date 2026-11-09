#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Seeds a value case (frontier-value/1.0) from a Frontier Company Blueprint: one value tree per use case,
every number a labelled assumption.

Usage:
  python seed_value.py --blueprint blueprint.json --out value.json [--use-cases UC05,UC09] [--rate 100]
         [--horizon 3] [--discount 0.08]

Without --use-cases the MVP use cases are seeded. Each gets an efficiency lever (volume x minutes saved / 60 x
loaded rate x realisation) and its assumptions: volume and minutes stay empty ("to collect") until evidence or
the customer provides them; the loaded rate and the realisation factor start from the method's defaults and are
labelled. The use case's KPIs are listed as baseline candidates. Add quality, revenue, cash and risk levers by
hand (references/value-method.md), then run value_calc.py.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--use-cases", help="comma-separated use-case ids (default: the MVP use cases)")
    ap.add_argument("--rate", type=float, default=100.0, help="default loaded rate per hour (labelled hypothesis)")
    ap.add_argument("--horizon", type=int, default=3)
    ap.add_argument("--discount", type=float, default=0.08)
    a = ap.parse_args(argv)
    bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8"))
    meta = bp.get("meta") or {}
    agents = {}
    for d in bp.get("domains", []):
        for ag in ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + list(d.get("agents", [])):
            agents[ag.get("name")] = ag
    ucs = [u for d in bp.get("domains", []) for u in d.get("use_cases", []) or []] + list(bp.get("use_cases", []) or [])
    want = [x.strip() for x in a.use_cases.split(",")] if a.use_cases else [u.get("id") for u in ucs if u.get("mvp")]
    if not want:
        print("ERROR: no MVP use cases in the blueprint; pass --use-cases", file=sys.stderr)
        return 2
    n = [0]

    def aid():
        n[0] += 1
        return f"ASS-{n[0]:03d}"

    realisation = {"id": aid(), "statement": "Realisation factor for released time", "unit": "share", "low": 0.25, "base": 0.5, "high": 0.75,
                   "source_type": "benchmark", "confidence": "medium", "owner": "Finance", "status": "open", "scope": "value",
                   "question": "How much of the released time will be redeployed to planned or billable work?",
                   "note": "Method default (Forrester convention; Microsoft-commissioned studies, US composite firms)"}
    out_ass, out_uc, missing = [realisation], [], []
    for uid in want:
        u = next((x for x in ucs if x.get("id") == uid), None)
        if not u:
            missing.append(uid)
            continue
        ag = [agents[nm] for nm in u.get("agents", []) or [] if nm in agents]
        owner = next((x.get("owner") for x in ag if x.get("owner")), "Process owner")
        name = u.get("name", uid)
        vol = {"id": aid(), "statement": f"{name}: cases per month", "unit": "per month", "low": None, "base": None, "high": None, "source_type": "hypothesis",
               "confidence": "low", "owner": owner, "status": "open", "scope": "value", "question": f"How many {name.lower()} cases happen in a month?"}
        bef = {"id": aid(), "statement": f"{name}: minutes per case today", "unit": "minutes", "low": None, "base": None, "high": None, "source_type": "hypothesis",
               "confidence": "low", "owner": owner, "status": "open", "scope": "value", "question": "How long does one case take today, end to end?"}
        aft = {"id": aid(), "statement": f"{name}: minutes per case with the agent", "unit": "minutes", "low": None, "base": None, "high": None, "source_type": "hypothesis",
               "confidence": "low", "owner": owner, "status": "open", "scope": "value", "question": "How long will reviewing and confirming the agent's work take?"}
        rate = {"id": aid(), "statement": f"{name}: loaded cost per hour", "unit": "CHF/h", "low": round(a.rate * 0.8), "base": a.rate, "high": round(a.rate * 1.2),
                "source_type": "hypothesis", "confidence": "low", "owner": "Finance", "status": "open", "scope": "value", "question": "What loaded hourly cost should we use for this role?"}
        out_ass += [vol, bef, aft, rate]
        out_uc.append({"id": uid, "name": name, "agents": [x.get("id") for x in ag if x.get("id")],
                       "vars": {"volume": vol["id"], "before": bef["id"], "after": aft["id"], "rate": rate["id"], "realisation": realisation["id"]},
                       "levers": [{"id": "L1", "name": "Time released", "driver": "efficiency", "category": "capacity",
                                   "formula": "volume * (before - after) / 60 * rate * realisation"}],
                       "baseline_candidates": u.get("kpis") or [], "break_even_on": vol["id"]})
    doc = {"schema": "frontier-value/1.0", "customer": meta.get("customer"), "short": meta.get("short"),
           "title": f"Value case for {meta.get('short') or meta.get('customer')} (seed)", "version": "0.1", "date": _dt.date.today().isoformat(),
           "status": "hypothesis", "currency": "CHF", "horizon_years": a.horizon, "discount_rate": a.discount, "realisation_default": 0.5,
           "assumptions": out_ass, "use_cases": out_uc}
    Path(a.out).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"use_cases": [u["id"] for u in out_uc], "assumptions": len(out_ass), "to_collect": sum(1 for x in out_ass if x["base"] is None),
                      "unknown_use_cases": missing, "out": a.out}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
