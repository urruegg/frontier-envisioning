#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Writes the FinOps model into a Frontier Company Blueprint: the data of the blueprint's FinOps page.

Usage:
  python apply_finops.py --blueprint blueprint.json --finops finops.json [--value value.json]
         [--rates rates/rates-2026-11.json] [--today 2026-11-04] --out blueprint.json

Run finops_calc.py first. Writes "finops" (cost per agent and month in CHF, cost lines, purchase options,
credit scenarios, guardrails, tagging keys from the agent identity, cost assumptions to clarify, rates with
source and date, lessons). Rates older than the rates file's verify_after_days are flagged "verify".
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_RATES = HERE.parent / "rates" / "rates-2026-11.json"
KEEP = ("id", "statement", "unit", "low", "base", "high", "source_type", "confidence", "src", "owner", "question", "status", "note")


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


def build_block(bp: dict, fin: dict, rates: dict, value: dict | None = None, today: _dt.date | None = None) -> dict:
    res = fin.get("results") or {}
    if not res:
        raise ValueError("finops.json has no results: run finops_calc.py first")
    today = today or _dt.date.today()
    checked = _dt.date.fromisoformat(rates.get("checked", rates.get("version")))
    age = (today - checked).days
    agents_bp = {}
    for d in bp.get("domains", []):
        for a in ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + list(d.get("agents", [])):
            agents_bp[a.get("id")] = (a, d)
    labels = rates["credits"].get("event_labels", {})
    per_event = rates["credits"]["per_event"]
    agents, tags = [], []
    for a in res.get("agents", []):
        bpa, dom = agents_bp.get(a["id"], ({}, {}))
        idn = bpa.get("identity") or {}
        events = [{"event": k, "label": labels.get(k, k), "credits_each": per_event.get(k), "credits_month": v}
                  for k, v in sorted(a["credits_by_event"].items(), key=lambda kv: -kv[1])]
        agents.append(dict({k: a.get(k) for k in ("id", "harness", "audience", "coverage", "owner", "sessions", "billable_share", "credits_per_session",
                                                   "credits_month", "lines", "total_month", "build", "unit", "run_hours_month", "azure_lines", "licence_lines")},
                           name=idn.get("display_name") or a.get("name") or bpa.get("name") or a["id"], journey=dom.get("id"), events=events))
        tags.append({"agent-id": a["id"], "agent-name": idn.get("display_name") or a.get("name") or a["id"], "schema": idn.get("schema", "to agree"),
                     "solution": idn.get("solution", "to agree"), "journey": dom.get("id", ""), "environment": " | ".join((idn.get("names") or {"PROD": ""}).keys()),
                     "cost-centre": "to agree with Finance"})
    reg = [x for x in (fin.get("assumptions") or [])]
    used_value = set()
    for ag in fin.get("agents", []):
        used_value |= {v for v in (ag.get("vars") or {}).values() if isinstance(v, str) and v.startswith("ASS-")}
    shared = [x for x in ((value or {}).get("assumptions") or []) if x.get("id") in used_value]
    srcs = rates.get("sources", [])
    rate_rows = [{"label": "Copilot Credit, pay-as-you-go", "value": f"USD {rates['credits']['payg_usd_per_credit']}", "source": "B2"},
                 {"label": "Capacity pack (25,000 credits per month)", "value": f"CHF {rates['credits']['pack']['chf_list']} (USD {rates['credits']['pack']['usd']})", "source": "B2, B6"},
                 {"label": "Copilot Credit P3 tiers", "value": " · ".join(f"{t / 1e6:g}M {d:.0%}" for t, d in rates['credits']['cc_p3_tiers']), "source": "B4"},
                 {"label": "Microsoft Agent P3 tiers (USD units)", "value": " · ".join(f"{u / 1e3:g}k {d:.0%}" for u, d in rates['credits']['agent_p3_tiers_usd']), "source": "B5"},
                 {"label": "CHF per USD", "value": f"{res.get('fx')}", "source": (fin.get("fx") or {}).get("source", "rates file")}]
    used_events = sorted({e["event"] for a in agents for e in a["events"]})
    rate_rows += [{"label": labels.get(k, k), "value": f"{per_event[k]:g} credits", "source": "B1"} for k in used_events]
    used_lic = sorted({l["sku"] for a in res.get("agents", []) for l in a.get("licence_lines", []) if l.get("sku")})
    rate_rows += [{"label": rates["licences"][k]["label"], "value": f"CHF {rates['licences'][k]['chf']:.2f}", "source": "B6"} for k in used_lic if k in rates["licences"]]
    block = {"title": fin.get("title"), "status": fin.get("status", "hypothesis"), "version": fin.get("version"), "date": fin.get("date"),
             "currency": fin.get("currency", "CHF"), "rates_version": rates.get("version"), "rates_checked": rates.get("checked"),
             "rates_age_days": age, "verify": age > int(rates.get("verify_after_days", 90)), "fx": dict(fin.get("fx") or {}, chf_per_usd=res.get("fx")),
             "purchase": fin.get("purchase"), "coverage_note": rates["credits"].get("coverage_note"), "agents": agents, "totals": res.get("totals"),
             "purchase_options": res.get("purchase_options"), "credit_scenarios": res.get("credit_scenarios"), "guardrails": res.get("guardrails"),
             "lessons": res.get("lessons"), "tags": tags, "missing": res.get("missing"),
             "assumptions": [{k: x.get(k) for k in KEEP} for x in reg + shared],
             "rates": rate_rows, "sources": [{k: s.get(k) for k in ("id", "title", "url", "date")} for s in srcs],
             "note": rates.get("note")}
    return clean(block)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--finops", required=True)
    ap.add_argument("--value")
    ap.add_argument("--rates", default=str(DEFAULT_RATES))
    ap.add_argument("--today", help="date for the rates age (default: today)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8"))
    fin = json.loads(Path(a.finops).read_text(encoding="utf-8"))
    value = json.loads(Path(a.value).read_text(encoding="utf-8")) if a.value else None
    rates = json.loads(Path(a.rates).read_text(encoding="utf-8"))
    try:
        bp["finops"] = build_block(bp, fin, rates, value, _dt.date.fromisoformat(a.today) if a.today else None)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    Path(a.out).write_text(json.dumps(bp, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    f = bp["finops"]
    print(json.dumps({"agents": len(f["agents"]), "total_month_chf": f["totals"]["total_month"], "rates_age_days": f["rates_age_days"],
                      "verify": f["verify"], "out": a.out}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
