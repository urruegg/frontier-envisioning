#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Writes the value case into a Frontier Company Blueprint: business value per use case and the assumption register.

Usage:
  python apply_value.py --blueprint blueprint.json --value value.json --out blueprint.json

Run value_calc.py first. Each use case with a value case gets "business_value" (range per year, budget, capacity and
risk views, cost, NPV, ROI, payback, break-even, levers, assumptions, status); the blueprint gets
"value_case" (assumption register ranked by effect on NPV, workshop questions, totals, discipline, sources).
The Use cases page then sizes the matrix bubbles by value and lists the assumptions to clarify.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

KEEP = ("id", "statement", "unit", "low", "base", "high", "source_type", "confidence", "src", "owner", "question", "status", "note")
DISCIPLINE = [
    "Cash, capacity and risk stay apart: released time is capacity until the customer names a spend that stops.",
    "Every benefit is counted once, net of new review, standby and run effort.",
    "A baseline is measured before the agents touch the process.",
    "Released hours are multiplied by a realisation factor (default 50%, sensitivity 25-75%).",
    "Benchmarks are priors, not facts: Microsoft-commissioned studies of US composite firms set ranges, never customer numbers.",
    "No ROI claim beyond the data; value is measured per process, team or agent, never per employee.",
]
SOURCES = [
    {"id": "C1", "title": "Measure the ROI and business value of AI agents (Microsoft Learn)", "url": "https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agent-business-value-overview"},
    {"id": "C2", "title": "Agents hub: monitor, measure and report value (Microsoft Learn)", "url": "https://learn.microsoft.com/en-us/agents/center-of-excellence/measure-report-value"},
    {"id": "C3", "title": "Cloud Adoption Framework: business plan for AI agents", "url": "https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/business-strategy-plan"},
]


def r2(x):
    """Money keeps cents; small numbers (shares, rates, ratios) keep six significant digits."""
    if not isinstance(x, float):
        return x
    return round(x, 2) if abs(x) >= 1000 else float(f"{x:.6g}")


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if v is not None}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return r2(o)


def apply(bp: dict, doc: dict) -> dict:
    res = doc.get("results") or {}
    if not res:
        raise ValueError("value.json has no results: run value_calc.py first")
    reg = {a["id"]: a for a in doc.get("assumptions", [])}
    sens = {s["id"]: s for s in res.get("sensitivity", [])}
    where = {}
    for u in doc.get("use_cases", []):
        for r in res.get("use_cases", []):
            if r["id"] == u.get("id"):
                for aid in r.get("assumptions", []):
                    where.setdefault(aid, []).append(u["id"])
    ucs = [u for d in bp.get("domains", []) for u in d.get("use_cases", []) or []] + list(bp.get("use_cases", []) or [])
    by_id = {u.get("id"): u for u in ucs}
    applied, unknown = [], []
    for r in res.get("use_cases", []):
        u = by_id.get(r["id"])
        if u is None:
            unknown.append(r["id"])
            continue
        be = r.get("break_even")
        if be:
            a = reg.get(be.get("assumption"), {})
            be = dict(be, statement=a.get("statement"), unit=a.get("unit"))
        mf = r["monthly_full"]
        u["business_value"] = clean({
            "status": r["status"], "confidence": r["confidence"], "open_assumptions": r["open_assumptions"],
            "range_year": r["range_year"], "economic_year": mf["economic"] * 12, "budget_year": mf["budget"] * 12,
            "capacity_year": mf["capacity"] * 12, "risk_year": mf["risk"] * 12, "cost_year": r["cost_month_full"] * 12, "build": r["build"],
            "npv": r["npv"], "npv_budget": r["npv_budget"], "roi": r["roi"], "payback_months": r["payback_months"], "break_even": be,
            "levers": [{"name": x["name"], "driver": x["driver"], "category": x["category"], "formula": x["formula"], "annual": x["monthly"] * 12,
                        "booked": x["booked"], "rejected": x["rejected"], "note": x.get("note") or None, "assumptions": x["assumptions"]} for x in r["levers"]],
            "assumptions": r["assumptions"], "agents_missing_cost": r.get("agents_missing_cost") or None})
        applied.append(r["id"])
    ass = []
    for aid, a in reg.items():
        if aid not in where:
            continue
        row = {k: a.get(k) for k in KEEP}
        row.update({"use_cases": where[aid], "rank": sens.get(aid, {}).get("rank"), "swing_npv": sens.get(aid, {}).get("swing")})
        ass.append(row)
    ass.sort(key=lambda x: (x["rank"] is None, x["rank"] or 0))
    bp["value_case"] = clean({"title": doc.get("title"), "status": doc.get("status", "hypothesis"), "version": doc.get("version"), "date": doc.get("date"),
                              "currency": doc.get("currency", "CHF"), "horizon_years": doc.get("horizon_years"), "discount_rate": doc.get("discount_rate"),
                              "realisation_default": doc.get("realisation_default"), "totals": res.get("totals"), "scenarios": res.get("scenarios"),
                              "assumptions": ass, "questions": [q["id"] for q in res.get("questions", [])], "inputs_needed": res.get("inputs_needed"),
                              "discipline": doc.get("discipline") or DISCIPLINE, "sources": doc.get("sources") or SOURCES})
    return {"applied": applied, "unknown_use_cases": unknown, "assumptions": len(ass)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--value", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8"))
    doc = json.loads(Path(a.value).read_text(encoding="utf-8"))
    try:
        summary = apply(bp, doc)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    Path(a.out).write_text(json.dumps(bp, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(summary, out=a.out), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
