#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Calculates the agent cost model (frontier-finops/1.0) in CHF and writes the results into the file.

Usage:
  python finops_calc.py --finops finops.json [--value value.json] [--rates rates/rates-2026-11.json] [--out finops.json]

Per agent and month: sessions x billable share (licence coverage) x events per session x credits per event;
credit cost at pay-as-you-go (USD per credit x CHF per USD); licences (incremental seats, fleet licences by
allocation share); Azure lines; people (run hours x rate); one-time build. Then unit economics (per session,
per outcome), the purchase options for the credits (pay-as-you-go, capacity packs, Copilot Credit P3, Agent
P3), credit-cost scenarios, guardrails and the lessons the numbers teach. Variables refer to the assumption
register (finops.json and, with --value, value.json). Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from fv_expr import MissingInput, evaluate, register_of, resolve

HERE = Path(__file__).resolve().parent
DEFAULT_RATES = HERE.parent / "rates" / "rates-2026-11.json"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def fx_of(fin: dict, rates: dict) -> float:
    return float((fin.get("fx") or {}).get("chf_per_usd") or rates["fx"]["swiss_list_ratio"])


def agent_cost(ag: dict, register: dict, rates: dict, fx: float, scenario="base", overrides=None, var_overrides=None) -> dict:
    env = resolve(ag.get("vars", {}), register, scenario, overrides, var_overrides)
    u = ag.get("usage") or {}
    sessions = evaluate(u.get("sessions", 0), env)
    billable = evaluate(u.get("billable_share", 1), env)
    per_event = rates["credits"]["per_event"]
    events = {}
    for k, v in (u.get("events_per_session") or {}).items():
        if k not in per_event:
            raise ValueError(f"agent {ag.get('id')}: unknown credit event {k!r} (see the rates file)")
        events[k] = evaluate(v, env)
    by_event = {k: sessions * billable * events[k] * per_event[k] for k in events}
    credits = sum(by_event.values())
    credit_chf = credits * rates["credits"]["payg_usd_per_credit"] * fx
    azure_lines = []
    for line in ag.get("azure") or []:
        qty = evaluate(line.get("qty", 0), env)
        unit_chf = evaluate(line["chf"], env) if "chf" in line else evaluate(line.get("usd", 0), env) * fx
        azure_lines.append({"name": line.get("name", ""), "unit": line.get("unit", ""), "qty": qty, "chf": qty * unit_chf,
                            "agent_p3": bool(line.get("agent_p3_eligible")), "source": line.get("source", "")})
    lic_lines = []
    for lic in ag.get("licences") or []:
        sku = rates["licences"].get(lic.get("sku", ""), {})
        price = float(lic["chf"]) if "chf" in lic else float(sku.get("chf", 0))
        seats = evaluate(lic.get("seats", 0), env)
        share = evaluate(lic.get("allocation_share", 1), env)
        lic_lines.append({"sku": lic.get("sku", ""), "label": lic.get("label") or sku.get("label", ""), "seats": seats,
                          "share": share, "chf": seats * price * share})
    p = ag.get("people") or {}
    run_hours = evaluate(p.get("run_hours_month", 0), env)
    people = run_hours * evaluate(p.get("rate_chf", 0), env)
    build = evaluate(p.get("build_one_time_chf", 0), env)
    azure = sum(x["chf"] for x in azure_lines)
    licences = sum(x["chf"] for x in lic_lines)
    total = credit_chf + azure + licences + people
    out = {"id": ag.get("id"), "name": ag.get("name", ""), "harness": ag.get("harness", ""), "audience": ag.get("audience", ""),
           "coverage": ag.get("coverage", ""), "sessions": sessions, "billable_share": billable,
           "credits_per_session": sum(events[k] * per_event[k] for k in events), "credits_month": credits, "credits_by_event": by_event,
           "lines": {"credits": credit_chf, "licences": licences, "azure": azure, "people": people},
           "variable_month": credit_chf + azure, "fixed_month": licences + people, "total_month": total, "build": build,
           "run_hours_month": run_hours, "azure_lines": azure_lines, "licence_lines": lic_lines,
           "agent_p3_usd_month": sum(x["chf"] for x in azure_lines if x["agent_p3"]) / fx if fx else 0.0,
           "unit": {"per_session": total / sessions if sessions else None}}
    if ag.get("outcome"):
        n = evaluate(ag["outcome"].get("per_month", 0), env)
        out["unit"].update({"outcome": ag["outcome"].get("name", "outcome"), "outcomes_month": n, "per_outcome": total / n if n else None})
    return out


def purchase_options(credits_month: float, agent_p3_usd_month: float, rates: dict, fx: float) -> list:
    c = rates["credits"]
    usd = c["payg_usd_per_credit"]
    annual = credits_month * 12
    eligible_azure_chf = agent_p3_usd_month * 12 * fx       # Foundry usage Agent P3 could also cover
    payg = annual * usd * fx
    pack = c["pack"]
    packs = math.ceil(credits_month / pack["credits"]) if credits_month > 0 else 0
    pack_chf = pack.get("chf_list") or pack["usd"] * fx
    best_p3 = min(((t * usd * (1 - d) * fx + max(0.0, annual - t) * usd * fx, t, d) for t, d in c["cc_p3_tiers"]), key=lambda x: x[0])
    eligible_usd = annual * usd + agent_p3_usd_month * 12
    best_ap3 = min(((u_ * (1 - d) * fx + max(0.0, eligible_usd - u_) * fx, u_, d) for u_, d in c["agent_p3_tiers_usd"]), key=lambda x: x[0])
    first_p3, first_ap3 = c["cc_p3_tiers"][0][0], c["agent_p3_tiers_usd"][0][0]
    opts = [
        {"option": "payg", "label": "Pay-as-you-go", "annual_chf": payg + eligible_azure_chf,
         "note": "USD 0.01 per credit, billed in arrears; draws down MACC; not Azure Prepayment eligible"},
        {"option": "packs", "label": f"Capacity packs ({packs} per month)", "annual_chf": packs * pack_chf * 12 + eligible_azure_chf,
         "utilisation": credits_month / (packs * pack["credits"]) if packs else 0.0,
         "note": "25,000 credits per pack and month at the Swiss list price; no rollover; service denial when exhausted"},
        {"option": "cc-p3", "label": f"Copilot Credit P3 ({best_p3[1]:,} credits, {best_p3[2]:.0%} off) + pay-as-you-go",
         "annual_chf": best_p3[0] + eligible_azure_chf,
         "note": "One-year pre-purchase, no refunds" + (" - below the smallest tier the unused commitment is lost" if annual < first_p3 else "")},
        {"option": "agent-p3", "label": f"Microsoft Agent P3 (USD {best_ap3[1]:,} units, {best_ap3[2]:.0%} off) + pay-as-you-go",
         "annual_chf": best_ap3[0],
         "note": "Covers credits and Foundry usage; one-year pre-purchase" + (f"; not economical below USD {first_ap3:,} a year" if eligible_usd < first_ap3 else "")},
    ]
    low = min(o["annual_chf"] for o in opts)
    for o in opts:
        o["vs_payg"] = (o["annual_chf"] / opts[0]["annual_chf"] - 1) if opts[0]["annual_chf"] else 0.0
        o["lowest"] = abs(o["annual_chf"] - low) < 0.005
    return opts


def lessons(agents: list, totals: dict, options: list, scenarios: list) -> list:
    out = []
    credits, people = totals["lines"]["credits"], totals["lines"]["people"]
    if credits and people > credits * 1.5:
        out.append(f"People cost more than credits: run effort is about {people / credits:.1f} times the credit cost; a FinOps view that shows only credits misleads.")
    grounding = sum(a["credits_by_event"].get("graph_grounding", 0) for a in agents)
    if totals["credits_month"] and grounding / totals["credits_month"] > 0.5:
        out.append(f"Knowledge design is a cost lever: tenant graph grounding drives {grounding / totals['credits_month']:.0%} of the credits; weigh it against freshness and permission trimming in the design review.")
    lic = [s for s in scenarios if s.get("kind") == "licences"]
    if lic:
        swing = max(abs(s["change"]) for s in lic)
        out.append(f"The licence mix moves the credit cost by up to {swing:.0%}; align the agent case with the Microsoft 365 Copilot roll-out plan.")
    payg = options[0]["annual_chf"]
    best = min(options, key=lambda o: o["annual_chf"])
    if payg:
        diff = (payg - best["annual_chf"]) / payg
        out.append(f"Purchase options differ by {diff:.0%} at this volume (lowest: {best['label']}); commit to P3 only after a usage baseline, because purchases cannot be refunded.")
    return out


def guardrails(fin: dict, agents: list, totals: dict) -> list:
    g = fin.get("guardrails") or {}
    head = float(g.get("headroom", 0.25))
    alerts = g.get("alerts", [0.5, 0.8, 1.0])
    al = "/".join(f"{x:.0%}" for x in alerts)
    rows = [{"control": "Credit allocation per environment", "where": "Power Platform admin center",
             "setting": "DEV and TEST small fixed allocations; PROD = sum of the agent limits below", "owner": g.get("platform_owner", "Power Platform team")}]
    for a in agents:
        limit = math.ceil(a["credits_month"] * (1 + head) / 1000.0) * 1000 if a["credits_month"] else 0
        rows.append({"control": f"Monthly credit limit: {a['name'] or a['id']}", "where": "Power Platform admin center", "agent": a["id"],
                     "setting": f"{limit:,} credits (base {a['credits_month']:,.0f} + {head:.0%} headroom); alerts at {al}; hard stop at 100%",
                     "owner": a.get("owner") or g.get("agent_owner", "Agent boss")})
    if totals["lines"]["azure"]:
        rows.append({"control": "Azure budget and anomaly alerts", "where": "Azure Cost Management",
                     "setting": f"CHF {totals['lines']['azure'] * (1 + head):,.0f} per month on the agent resources; alerts at {al}", "owner": g.get("finops_owner", "FinOps lead")})
    rows += [
        {"control": "Microsoft 365 spending policy", "where": "Microsoft 365 admin center", "setting": "Copilot Credits for Cowork and Work IQ calls with a monthly cap per policy", "owner": g.get("m365_owner", "Microsoft 365 admin")},
        {"control": "Tagging standard", "where": "Power Platform, Azure, Foundry", "setting": "agent-id, agent-name, environment, schema, journey and cost-centre on every resource (keys from the agent identity kit)", "owner": g.get("platform_owner", "Power Platform team")},
        {"control": "Monthly plan versus actual", "where": "Cowork digest or Power BI", "setting": f"Variance threshold {g.get('variance', 0.2):.0%}; review in the agent board", "owner": g.get("finops_owner", "FinOps lead")},
    ]
    return rows


def compute(fin: dict, register: dict, rates: dict, scenario="base", overrides=None, var_overrides=None) -> dict:
    fx = fx_of(fin, rates)
    agents, missing = [], []
    owners = {a.get("id"): a.get("owner") for a in fin.get("agents", [])}
    for ag in fin.get("agents", []):
        try:
            r = agent_cost(ag, register, rates, fx, scenario, overrides, var_overrides)
            r["owner"] = owners.get(ag.get("id"))
            agents.append(r)
        except MissingInput as exc:
            missing.append({"agent": ag.get("id"), "assumptions": exc.ids})
    keys = ("credits", "licences", "azure", "people")
    totals = {"credits_month": sum(a["credits_month"] for a in agents), "total_month": sum(a["total_month"] for a in agents),
              "build": sum(a["build"] for a in agents), "sessions": sum(a["sessions"] for a in agents),
              "lines": {k: sum(a["lines"][k] for a in agents) for k in keys}}
    totals["annual"] = totals["total_month"] * 12
    return {"fx": fx, "agents": agents, "totals": totals, "missing": missing,
            "agent_p3_usd_month": sum(a["agent_p3_usd_month"] for a in agents)}


def run(fin: dict, value: dict | None, rates: dict) -> dict:
    register = register_of(value or {}, fin)
    base = compute(fin, register, rates)
    scen = []
    for sc in fin.get("credit_scenarios") or []:
        r = compute(fin, register, rates, var_overrides=sc.get("set") or {})
        cr, chf = r["totals"]["credits_month"], r["totals"]["lines"]["credits"]
        bchf = base["totals"]["lines"]["credits"]
        scen.append({"name": sc.get("name", ""), "kind": sc.get("kind", ""), "credits_month": cr, "chf_month": chf,
                     "change": (chf / bchf - 1) if bchf else 0.0})
    opts = purchase_options(base["totals"]["credits_month"], base["agent_p3_usd_month"], rates, base["fx"])
    res = {"rates_version": rates.get("version"), "fx": base["fx"], "agents": base["agents"], "totals": base["totals"],
           "missing": base["missing"], "purchase_options": opts, "credit_scenarios": scen,
           "guardrails": guardrails(fin, base["agents"], base["totals"])}
    res["lessons"] = lessons(base["agents"], base["totals"], opts, scen) if base["agents"] else []
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--finops", required=True)
    ap.add_argument("--value", help="value.json, for assumptions shared with the value case")
    ap.add_argument("--rates", default=str(DEFAULT_RATES))
    ap.add_argument("--out", help="defaults to --finops (results are written into the file)")
    a = ap.parse_args(argv)
    fin = load(a.finops)
    value = load(a.value) if a.value else None
    rates = load(a.rates)
    try:
        res = run(fin, value, rates)
    except (ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    fin["results"] = res
    fin["rates_version"] = rates.get("version")
    Path(a.out or a.finops).write_text(json.dumps(fin, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    t = res["totals"]
    print(json.dumps({"agents": len(res["agents"]), "missing": res["missing"], "credits_month": round(t["credits_month"], 2),
                      "total_month_chf": round(t["total_month"], 2), "annual_chf": round(t["annual"], 2), "build_chf": round(t["build"], 2),
                      "lowest_option": min(res["purchase_options"], key=lambda o: o["annual_chf"])["label"] if res["agents"] else None,
                      "out": a.out or a.finops}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
