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

from finops_preview import inherit_restrictions, preview_metadata, privacy_flags, require_preview_ack, validate_finops_results

HERE = Path(__file__).resolve().parent
DEFAULT_RATES = HERE.parent / "rates" / "rates-2026-11.json"
KEEP = ("id", "statement", "unit", "low", "base", "high", "source_type", "confidence", "src", "owner", "question", "status", "note",
        "internal", "visibility")


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


def build_block(bp: dict, fin: dict, rates: dict, value: dict | None = None, today: _dt.date | None = None,
                *, acknowledge_finops_preview: bool = False) -> dict:
    require_preview_ack(acknowledge_finops_preview)
    if not isinstance(fin, dict):
        raise ValueError("finops input must be an object")
    consumed = validate_finops_results(fin, value=value, rates=rates,
                                       acknowledge_finops_preview=acknowledge_finops_preview)
    preview = preview_metadata(acknowledge_finops_preview, operation="apply", finops=fin,
                               value=value, rates=rates, blueprint=bp,
                               inherited=consumed, consume_finops_results=True)
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
        for event in events:
            event.update(inherit_restrictions(rates, rates["credits"], per_event, labels))
        agents.append(dict({k: a.get(k) for k in ("id", "harness", "audience", "coverage", "owner", "sessions", "billable_share", "credits_per_session",
                                                   "credits_month", "lines", "total_month", "build", "unit", "run_hours_month", "azure_lines",
                                                   "licence_lines", "people_source")},
                           name=idn.get("display_name") or a.get("name") or bpa.get("name") or a["id"], journey=dom.get("id"), events=events,
                           **inherit_restrictions(a)))
        tags.append({"agent-id": a["id"], "agent-name": idn.get("display_name") or a.get("name") or a["id"], "schema": idn.get("schema", "to agree"),
                     "solution": idn.get("solution", "to agree"), "journey": dom.get("id", ""), "environment": " | ".join((idn.get("names") or {"PROD": ""}).keys()),
                     "cost-centre": "to agree with Finance", **inherit_restrictions(a)})
    reg = [x for x in (fin.get("assumptions") or [])]
    used_value = set()
    for ag in fin.get("agents", []):
        used_value |= {v for v in (ag.get("vars") or {}).values() if isinstance(v, str) and v.startswith("ASS-")}
    shared = [x for x in ((value or {}).get("assumptions") or []) if x.get("id") in used_value]
    srcs = rates.get("sources", [])
    credit_source = inherit_restrictions(rates, rates["credits"])
    rate_rows = [{"label": "Copilot Credit, pay-as-you-go", "value": f"USD {rates['credits']['payg_usd_per_credit']}", "source": "B2",
                  **credit_source},
                 {"label": "Capacity pack (25,000 credits per month)", "value": f"CHF {rates['credits']['pack']['chf_list']} (USD {rates['credits']['pack']['usd']})", "source": "B2, B6",
                  **inherit_restrictions(rates["credits"]["pack"], credit_source)},
                 {"label": "Copilot Credit P3 tiers", "value": " · ".join(f"{t / 1e6:g}M {d:.0%}" for t, d in rates['credits']['cc_p3_tiers']), "source": "B4",
                  **credit_source},
                 {"label": "Microsoft Agent P3 tiers (USD units)", "value": " · ".join(f"{u / 1e3:g}k {d:.0%}" for u, d in rates['credits']['agent_p3_tiers_usd']), "source": "B5",
                  **credit_source},
                 {"label": "CHF per USD", "value": f"{res.get('fx')}", "source": (fin.get("fx") or {}).get("source", "rates file"),
                  **inherit_restrictions(res.get("fx_source"), rates)}]
    used_events = sorted({e["event"] for a in agents for e in a["events"]})
    rate_rows += [{"label": labels.get(k, k), "value": f"{per_event[k]:g} credits", "source": "B1",
                   **inherit_restrictions(credit_source, per_event, labels)} for k in used_events]
    rate_rows += [{"label": line["label"], "value": f"CHF {line['unit_chf']:.2f}", "source": "B6",
                   **inherit_restrictions(line)}
                  for a in res.get("agents", []) for line in a.get("licence_lines", []) if line.get("sku")]
    block = {"finops_preview": preview, "title": fin.get("title"), "status": fin.get("status", "hypothesis"), "version": fin.get("version"), "date": fin.get("date"),
             "currency": fin.get("currency", "CHF"), "rates_version": rates.get("version"), "rates_checked": rates.get("checked"),
             "rates_age_days": age, "verify": age > int(rates.get("verify_after_days", 90)),
             "fx": dict(fin.get("fx") or {}, chf_per_usd=res.get("fx"), **inherit_restrictions(res.get("fx_source"))),
             "purchase": fin.get("purchase"), "coverage_note": rates["credits"].get("coverage_note"), "agents": agents, "totals": res.get("totals"),
             "purchase_options": [dict(option, assessment="provisional-comparison-not-recommendation")
                                  for option in res.get("purchase_options", [])],
             "credit_scenarios": res.get("credit_scenarios"), "guardrails": res.get("guardrails"),
             "lessons": res.get("lessons"), "tags": tags, "missing": res.get("missing"),
             "assumptions": [{k: x.get(k) for k in KEEP} for x in reg + shared],
             "rates": rate_rows, "sources": [{k: s.get(k) for k in ("id", "title", "url", "date", "internal", "visibility")} for s in srcs],
             "note": rates.get("note")}
    if "internal_notes" in res:
        block["internal_notes"] = res["internal_notes"]
    if "ranking_status" in res:
        block["ranking_status"] = res["ranking_status"]
    block.update({k: fin[k] for k in ("internal", "visibility", "src") if k in fin})
    block.update(privacy_flags(preview))
    return clean(block)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--finops", required=True)
    ap.add_argument("--value")
    ap.add_argument("--rates", default=str(DEFAULT_RATES))
    ap.add_argument("--today", help="date for the rates age (default: today)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--acknowledge-finops-preview", action="store_true")
    a = ap.parse_args(argv)
    try:
        require_preview_ack(a.acknowledge_finops_preview)
        bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8"))
        fin = json.loads(Path(a.finops).read_text(encoding="utf-8"))
        value = json.loads(Path(a.value).read_text(encoding="utf-8")) if a.value else None
        rates = json.loads(Path(a.rates).read_text(encoding="utf-8"))
        bp["finops"] = build_block(bp, fin, rates, value, _dt.date.fromisoformat(a.today) if a.today else None,
                                   acknowledge_finops_preview=a.acknowledge_finops_preview)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    Path(a.out).write_text(json.dumps(bp, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    f = bp["finops"]
    print(json.dumps({**inherit_restrictions(privacy_flags(f["finops_preview"]), f, f["totals"]),
                      "finops_preview": f["finops_preview"],
                      "agents": len(f["agents"]), "total_month_chf": f["totals"]["total_month"], "rates_age_days": f["rates_age_days"],
                      "verify": f["verify"], "out": a.out}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
