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

from fv_expr import MissingInput, evaluate, names, register_of, resolve
from finops_preview import (
    bind_calculation, fingerprint, inherit_restrictions, is_private, preview_metadata, privacy_flags, require_preview_ack,
)

HERE = Path(__file__).resolve().parent
DEFAULT_RATES = HERE.parent / "rates" / "rates-2026-11.json"


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def fx_of(fin: dict, rates: dict) -> float:
    selected = (fin.get("fx") or {}).get("chf_per_usd")
    selected = rates["fx"]["swiss_list_ratio"] if selected is None else selected
    return cost_rate(selected, "selected CHF per USD", positive=True)


def cost_rate(value, label: str, *, positive=False, share=False) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
            or (value <= 0 if positive else value < 0) or (share and value > 1)):
        raise ValueError(f"{label} must be a finite {'positive' if positive else 'non-negative'} rate"
                         + (" in [0, 1]" if share else ""))
    return float(value)


def validate_rates(fin: dict, rates: dict) -> None:
    """Only the prices/events and purchase comparison rates this model consumes."""
    credits = rates["credits"]
    cost_rate(credits["payg_usd_per_credit"], "PAYG USD per credit")
    pack = credits["pack"]
    cost_rate(pack["credits"], "capacity pack credits", positive=True)
    cost_rate(pack["usd"], "capacity pack USD")
    if pack.get("chf_list") is not None:
        cost_rate(pack["chf_list"], "capacity pack CHF")
    for key in ("cc_p3_tiers", "agent_p3_tiers_usd"):
        tiers = credits[key]
        if not isinstance(tiers, list) or not tiers:
            raise ValueError(f"{key} must provide purchase comparison tiers")
        for tier in tiers:
            if not isinstance(tier, list) or len(tier) != 2:
                raise ValueError(f"{key} must contain [quantity, discount] rates")
            cost_rate(tier[0], f"{key} quantity", positive=True)
            cost_rate(tier[1], f"{key} discount", share=True)
    for agent in fin.get("agents", []):
        for event in (agent.get("usage") or {}).get("events_per_session", {}):
            if event not in credits["per_event"]:
                raise ValueError(f"agent {agent.get('id')}: unknown credit event {event!r}")
            cost_rate(credits["per_event"][event], f"{event} credits per event")
        for licence in agent.get("licences", []):
            if "chf" in licence:
                price = licence["chf"]
            elif licence.get("sku") in rates["licences"]:
                price = rates["licences"][licence["sku"]].get("chf")
            else:
                raise ValueError(f"agent {agent.get('id')}: unknown licence rate {licence.get('sku')!r}")
            cost_rate(price, f"licence {licence.get('sku')} CHF")


def validate_agent_rates(agent, env):
    for line in agent.get("azure") or []:
        key = "chf" if "chf" in line else "usd"
        if key not in line:
            raise ValueError(f"agent {agent.get('id')}: Azure line requires a CHF or USD unit rate")
        if isinstance(line[key], bool):
            raise ValueError("Azure unit rate must not be boolean")
        cost_rate(evaluate(line[key], env), f"Azure {key} unit rate")
    people = agent.get("people") or {}
    for key in ("rate_chf", "build_one_time_chf"):
        if key in people:
            if isinstance(people[key], bool):
                raise ValueError(f"people.{key} must not be boolean")
            cost_rate(evaluate(people[key], env), f"people.{key}")
    if "run_hours_month" in people and "rate_chf" not in people:
        raise ValueError("people.run_hours_month requires a run rate_chf")


def assumption_sources(agent, register, *, outcome_only=False):
    """Follow only formula dependencies, not unrelated/unused register entries."""
    usage, people = agent.get("usage") or {}, agent.get("people") or {}
    expressions = [usage.get("sessions", 0), usage.get("billable_share", 1),
                   *(usage.get("events_per_session") or {}).values(),
                   *(people.get(key, 0) for key in ("run_hours_month", "rate_chf", "build_one_time_chf"))]
    for line in agent.get("azure") or []:
        expressions.extend([line.get("qty", 0), line.get("chf", line.get("usd", 0))])
    for licence in agent.get("licences") or []:
        expressions.extend([licence.get("seats", 0), licence.get("allocation_share", 1)])
    if outcome_only:
        expressions = [(agent.get("outcome") or {}).get("per_month", 0)]
    pending = [n for expression in expressions for n in names(expression)]
    seen, used = set(), set()
    while pending:
        variable = pending.pop()
        if variable in seen:
            continue
        seen.add(variable)
        spec = (agent.get("vars") or {}).get(variable)
        if isinstance(spec, str) and spec in register:
            used.add(spec)
        elif isinstance(spec, str):
            pending.extend(names(spec))
    return [register[key] for key in sorted(used)]


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
                            "agent_p3": bool(line.get("agent_p3_eligible")), "source": line.get("source", ""),
                            **inherit_restrictions(line)})
    lic_lines = []
    for lic in ag.get("licences") or []:
        sku = rates["licences"].get(lic.get("sku", ""), {})
        price = float(lic["chf"]) if "chf" in lic else float(sku.get("chf", 0))
        seats = evaluate(lic.get("seats", 0), env)
        share = evaluate(lic.get("allocation_share", 1), env)
        selected_sku = sku if "chf" not in lic or not lic.get("label") else {}
        selected_container = rates["licences"] if selected_sku else {}
        lic_lines.append({"sku": lic.get("sku", ""), "label": lic.get("label") or sku.get("label", ""), "seats": seats,
                          "share": share, "unit_chf": price, "chf": seats * price * share,
                          **inherit_restrictions(lic, selected_sku, selected_container)})
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
        outcome = {"outcome": ag["outcome"].get("name", "outcome"), "outcomes_month": n,
                   "per_outcome": total / n if n else None, "fingerprint": fingerprint(ag["outcome"]),
                   **inherit_restrictions(ag["outcome"], *assumption_sources(ag, register, outcome_only=True))}
        if is_private(outcome):
            out["unit"]["internal_notes"] = {"outcome": outcome}
        else:
            out["unit"].update(outcome)
    if p:
        out["people_source"] = {"fingerprint": fingerprint(p), **inherit_restrictions(p)}
    credit_inputs = inherit_restrictions(rates["credits"], per_event) if events else {}
    out.update(inherit_restrictions(ag, u, p, credit_inputs, *azure_lines, *lic_lines, *assumption_sources(ag, register)))
    return out


def purchase_options(credits_month: float, agent_p3_usd_month: float, rates: dict, fx: float) -> list:
    c = rates["credits"]
    usd = c["payg_usd_per_credit"]
    annual = credits_month * 12
    eligible_azure_chf = agent_p3_usd_month * 12 * fx       # Foundry usage Agent P3 could also cover
    payg = annual * usd * fx
    pack = c["pack"]
    packs = math.ceil(credits_month / pack["credits"]) if credits_month > 0 else 0
    pack_chf = pack["usd"] * fx if pack.get("chf_list") is None else pack["chf_list"]
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
        o.update(inherit_restrictions(rates, c, pack if o["option"] == "packs" else {}))
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
        out.append(f"Provisional purchase comparison: options differ by {diff:.0%} at this volume "
                   f"(lowest modelled estimate: {best['label']}); this is not a purchasing recommendation. "
                   "Verify rates and a usage baseline independently; pre-purchases cannot be refunded.")
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
                     "owner": a.get("owner") or g.get("agent_owner", "Agent boss"), **inherit_restrictions(g, a)})
    if totals["lines"]["azure"]:
        rows.append({"control": "Azure budget and anomaly alerts", "where": "Azure Cost Management",
                     "setting": f"CHF {totals['lines']['azure'] * (1 + head):,.0f} per month on the agent resources; alerts at {al}", "owner": g.get("finops_owner", "FinOps lead")})
    rows += [
        {"control": "Microsoft 365 spending policy", "where": "Microsoft 365 admin center", "setting": "Copilot Credits for Cowork and Work IQ calls with a monthly cap per policy", "owner": g.get("m365_owner", "Microsoft 365 admin")},
        {"control": "Tagging standard", "where": "Power Platform, Azure, Foundry", "setting": "agent-id, agent-name, environment, schema, journey and cost-centre on every resource (keys from the agent identity kit)", "owner": g.get("platform_owner", "Power Platform team")},
        {"control": "Monthly plan versus actual", "where": "Cowork digest or Power BI", "setting": f"Variance threshold {g.get('variance', 0.2):.0%}; review in the agent board", "owner": g.get("finops_owner", "FinOps lead")},
    ]
    for row in rows:
        row.update(inherit_restrictions(g))
    return rows


def compute(fin: dict, register: dict, rates: dict, scenario="base", overrides=None, var_overrides=None,
            *, acknowledge_finops_preview: bool = False) -> dict:
    require_preview_ack(acknowledge_finops_preview)
    if not isinstance(fin, dict):
        raise ValueError("finops input must be an object")
    preview = preview_metadata(acknowledge_finops_preview, operation="compute", finops=fin, rates=rates,
                               scenario=scenario, overrides=overrides, var_overrides=var_overrides,
                               inherited=fin.get("finops_preview", {}))
    preview["provenance"]["scenario"]["register_fingerprint"] = fingerprint(register)
    validate_rates(fin, rates)
    fx = fx_of(fin, rates)
    fx_source = fin.get("fx") or {}
    fx_source = rates["fx"] if fx_source.get("chf_per_usd") is None else fx_source
    agents, missing = [], []
    owners = {a.get("id"): a.get("owner") for a in fin.get("agents", [])}
    for ag in fin.get("agents", []):
        usage = ag.get("usage") or {}
        consumed_inputs = [ag, usage, ag.get("people"), *assumption_sources(ag, register)]
        if usage.get("events_per_session"):
            consumed_inputs.extend([rates["credits"], rates["credits"]["per_event"], fx_source])
        for line in ag.get("azure") or []:
            consumed_inputs.append(line)
            if "chf" not in line:
                consumed_inputs.append(fx_source)
        for licence in ag.get("licences") or []:
            consumed_inputs.append(licence)
            if "chf" not in licence or not licence.get("label"):
                consumed_inputs.extend([rates["licences"], rates["licences"].get(licence.get("sku"), {})])
        try:
            env = resolve(ag.get("vars", {}), register, scenario, overrides, var_overrides)
            validate_agent_rates(ag, env)
            r = agent_cost(ag, register, rates, fx, scenario, overrides, var_overrides)
            r.update(inherit_restrictions(r, *consumed_inputs))
            for original, line in zip(ag.get("azure", []), r["azure_lines"]):
                if "chf" not in original:
                    line.update(inherit_restrictions(line, fx_source))
            r["owner"] = owners.get(ag.get("id"))
            if fin.get("date") is not None:
                r.setdefault("date", fin["date"])
            agents.append(r)
        except MissingInput as exc:
            missing.append({"agent": ag.get("id"), "assumptions": exc.ids,
                            **inherit_restrictions(*consumed_inputs, {"date": fin.get("date")})})
    keys = ("credits", "licences", "azure", "people")
    totals = {"credits_month": sum(a["credits_month"] for a in agents), "total_month": sum(a["total_month"] for a in agents),
              "build": sum(a["build"] for a in agents), "sessions": sum(a["sessions"] for a in agents),
              "lines": {k: sum(a["lines"][k] for a in agents) for k in keys}}
    totals["annual"] = totals["total_month"] * 12
    result = {"finops_preview": preview, "fx": fx, "agents": agents, "totals": totals, "missing": missing,
              "fx_source": {"fingerprint": fingerprint(fx_source), **inherit_restrictions(fx_source)},
              "agent_p3_usd_month": sum(a["agent_p3_usd_month"] for a in agents)}
    restrictions = privacy_flags(preview)
    result.update(restrictions)
    totals.update(restrictions)
    if any(is_private(a) for a in agents):
        totals.update(inherit_restrictions(*(a for a in agents if is_private(a))))
        preview["provenance"]["scenario"]["internal"] = True
    bind_calculation(result, "finops", fin, register=register, rates=rates,
                     acknowledge_finops_preview=acknowledge_finops_preview)
    return result


def run(fin: dict, value: dict | None, rates: dict, *, acknowledge_finops_preview: bool = False) -> dict:
    require_preview_ack(acknowledge_finops_preview)
    if not isinstance(fin, dict):
        raise ValueError("finops input must be an object")
    preview = preview_metadata(acknowledge_finops_preview, operation="calculate", finops=fin,
                               value=value, rates=rates, inherited=fin.get("finops_preview", {}))
    register = register_of(value or {}, fin)
    base = compute(fin, register, rates, acknowledge_finops_preview=acknowledge_finops_preview)
    scen = []
    for sc in fin.get("credit_scenarios") or []:
        r = compute(fin, register, rates, var_overrides=sc.get("set") or {},
                    acknowledge_finops_preview=acknowledge_finops_preview)
        cr, chf = r["totals"]["credits_month"], r["totals"]["lines"]["credits"]
        bchf = base["totals"]["lines"]["credits"]
        scen.append({"name": sc.get("name", ""), "kind": sc.get("kind", ""), "credits_month": cr, "chf_month": chf,
                     "change": (chf / bchf - 1) if bchf else 0.0,
                     **inherit_restrictions(sc, r["totals"], base["totals"])})
    opts = purchase_options(base["totals"]["credits_month"], base["agent_p3_usd_month"], rates, base["fx"])
    for option in opts:
        option["assessment"] = "provisional-comparison-not-recommendation"
        # Comparison commitments use FX independently of base agent costs.
        uses_fx = (option["option"] in {"cc-p3", "agent-p3"}
                   or (option["option"] == "payg" and
                       (base["totals"]["credits_month"] or base["agent_p3_usd_month"]))
                   or (option["option"] == "packs" and
                       (rates["credits"]["pack"].get("chf_list") is None or base["agent_p3_usd_month"])))
        if uses_fx:
            option.update(inherit_restrictions(option, base["fx_source"]))
    res = {"finops_preview": preview, "rates_version": rates.get("version"), "fx": base["fx"], "fx_source": base["fx_source"],
           "agents": base["agents"], "totals": base["totals"],
           "missing": base["missing"], "purchase_options": opts, "credit_scenarios": scen,
           "guardrails": guardrails(fin, base["agents"], base["totals"])}
    res["lessons"] = lessons(base["agents"], base["totals"], opts, scen) if base["agents"] else []
    res.update(privacy_flags(preview))
    private_agents = {a["id"]: a for a in base["agents"] if is_private(a)}
    aggregate = inherit_restrictions(base["totals"])
    for option in opts:
        option.update(aggregate)
    if private_agents:
        preview["provenance"]["scenario"]["internal"] = True
        aggregate = inherit_restrictions(*private_agents.values())
        for row in opts + scen:
            row.update(inherit_restrictions(row, aggregate))
        for row in res["guardrails"]:
            if row.get("agent") in private_agents:
                row.update(inherit_restrictions(private_agents[row["agent"]]))
            elif row["control"] == "Azure budget and anomaly alerts":
                row.update(aggregate)
        # Opaque aggregate prose cannot carry per-item tags. Keep it available
        # in the internal-only field understood by the existing projector.
    if any(is_private(row) for row in opts + scen) or is_private(base["totals"]):
        res["internal_notes"] = {"lessons": res["lessons"]}
        res["lessons"] = []
    private_candidates = [option for option in opts if is_private(option)]
    if private_candidates:
        # A candidate amount and a rank across ALL candidates have different
        # dependencies. Keep public amounts; do not encode unavailable ranks
        # as False or recompute a misleading public-subset winner.
        ranking = inherit_restrictions(*private_candidates)
        res["ranking_status"] = "withheld-private-candidates"
        for option in opts:
            notes = option.setdefault("internal_notes", {})
            notes["ranking"] = {"lowest": option.pop("lowest"), **ranking}
            if is_private(opts[0]):
                notes["payg_comparison"] = {"vs_payg": option.pop("vs_payg"),
                                            **inherit_restrictions(option, opts[0])}
    bind_calculation(res, "finops", fin, register=register, rates=rates,
                     acknowledge_finops_preview=acknowledge_finops_preview)
    return res


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--finops", required=True)
    ap.add_argument("--value", help="value.json, for assumptions shared with the value case")
    ap.add_argument("--rates", default=str(DEFAULT_RATES))
    ap.add_argument("--out", help="defaults to --finops (results are written into the file)")
    ap.add_argument("--acknowledge-finops-preview", action="store_true", help="explicit caller assertion for this invocation, not approval")
    a = ap.parse_args(argv)
    try:
        require_preview_ack(a.acknowledge_finops_preview)
        fin = load(a.finops)
        value = load(a.value) if a.value else None
        rates = load(a.rates)
        res = run(fin, value, rates, acknowledge_finops_preview=a.acknowledge_finops_preview)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    fin["results"] = res
    fin["finops_preview"] = res["finops_preview"]
    fin["rates_version"] = rates.get("version")
    Path(a.out or a.finops).write_text(json.dumps(fin, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    t = res["totals"]
    print(json.dumps({**inherit_restrictions(privacy_flags(res["finops_preview"]), res, t),
                      "finops_preview": res["finops_preview"],
                      "agents": len(res["agents"]), "missing": res["missing"], "credits_month": round(t["credits_month"], 2),
                      "total_month_chf": round(t["total_month"], 2), "annual_chf": round(t["annual"], 2), "build_chf": round(t["build"], 2),
                      **({"ranking_status": res["ranking_status"]} if "ranking_status" in res else
                         {"lowest_option": min(res["purchase_options"], key=lambda o: o["annual_chf"])["label"] if res["agents"] else None}),
                      "out": a.out or a.finops}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
