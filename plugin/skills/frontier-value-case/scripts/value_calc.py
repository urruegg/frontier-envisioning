#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Calculates the value case (frontier-value/1.0) in CHF and writes the results into the file.

Usage:
  python value_calc.py --value value.json [--finops finops.json] [--out value.json]

Per use case and month: each lever's formula over the assumption register (the realisation factor sits in
the formula), the adoption ramp per quarter, and the run cost of the use case's agents from the FinOps
results (finops_calc.py first; variable costs follow the ramp). Views: budget (cash and revenue), economic
(budget plus realised capacity) and risk reduction, always separate; levers with "booked": false are shown,
never counted; levers that depend on a rejected assumption are left out. NPV at the discount rate (annual
discounting, build at year 0), ROI = NPV / PV cost, payback in months (undiscounted), break-even value of one
assumption. Sensitivity: every assumption at its low and high with the others at base (costs held at base);
the ten largest NPV swings become the workshop questions. Scenarios: weak and strong, each assumption at the
end that lowers or raises the NPV. Standard library only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fv_expr import MissingInput, evaluate, names, register_of, resolve

CASH, CAPACITY, RISK = {"cash", "revenue"}, {"capacity"}, {"risk"}
CONF = {"high": 3, "medium": 2, "low": 1}


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ramp_factor(ramp, m: int) -> float:
    if not ramp:
        return 1.0
    return float(ramp[min((m - 1) // 3, len(ramp) - 1)])


def deps_of(uc: dict, expr, register: dict) -> list:
    """Assumption ids behind a formula, following the use case's variables."""
    spec, seen, out, todo = uc.get("vars") or {}, set(), set(), list(names(expr))
    while todo:
        n = todo.pop()
        if n in seen:
            continue
        seen.add(n)
        s = spec.get(n)
        if isinstance(s, str) and s in register:
            out.add(s)
        elif isinstance(s, str):
            todo += names(s)
    return sorted(out)


def uc_costs(uc: dict, fin_results: dict | None):
    agents = {a["id"]: a for a in (fin_results or {}).get("agents", [])}
    ids = [i for i in uc.get("agents", []) if i in agents]
    return (sum(agents[i]["fixed_month"] for i in ids), sum(agents[i]["variable_month"] for i in ids),
            sum(agents[i]["build"] for i in ids), ids)


def uc_eval(uc: dict, register: dict, doc: dict, fin_results, scenario="base", overrides=None) -> dict:
    env = resolve(uc.get("vars") or {}, register, scenario, overrides)
    ramp = uc.get("adoption_ramp") or doc.get("adoption_ramp") or [1.0]
    horizon = int(doc.get("horizon_years", 3))
    rate = float(doc.get("discount_rate") or 0.0)
    levers = []
    for lv in uc.get("levers", []):
        deps = deps_of(uc, lv["formula"], register)
        rejected = any(str(register[i].get("status", "")).lower() == "rejected" for i in deps if not (overrides and i in overrides))
        monthly = 0.0 if rejected else evaluate(lv["formula"], env)
        levers.append({"id": lv.get("id"), "name": lv.get("name", ""), "driver": lv.get("driver", "efficiency"),
                       "category": lv.get("category", "capacity"), "formula": lv["formula"], "monthly": monthly,
                       "booked": bool(lv.get("booked", True)) and not rejected, "rejected": rejected,
                       "ramp": bool(lv.get("ramp", True)), "assumptions": deps, "note": lv.get("note", "")})
    fixed, var, build, modelled = uc_costs(uc, fin_results)
    years = [{"budget": 0.0, "economic": 0.0, "risk": 0.0, "cost": 0.0} for _ in range(horizon)]
    cum, payback = -build, None
    for m in range(1, horizon * 12 + 1):
        f = ramp_factor(ramp, m)
        part = lambda cats: sum(x["monthly"] * (f if x["ramp"] else 1.0) for x in levers if x["booked"] and x["category"] in cats)
        cash, cap, risk = part(CASH), part(CAPACITY), part(RISK)
        cost = fixed + var * f
        y = years[(m - 1) // 12]
        y["budget"] += cash
        y["economic"] += cash + cap
        y["risk"] += risk
        y["cost"] += cost
        net = cash + cap - cost
        if payback is None and net > 0 and cum + net >= 0:
            payback = (m - 1) + (-cum / net if cum < 0 else 0.0)
        cum += net
    disc = [1.0 / (1.0 + rate) ** (i + 1) for i in range(horizon)]
    pv = {k: sum(years[i][k] * disc[i] for i in range(horizon)) for k in ("budget", "economic", "risk", "cost")}
    pv_cost = build + pv["cost"]
    full = {k: sum(x["monthly"] for x in levers if x["booked"] and x["category"] in cats)
            for k, cats in (("budget", CASH), ("capacity", CAPACITY), ("risk", RISK))}
    full["economic"] = full["budget"] + full["capacity"]
    return {"id": uc.get("id"), "levers": levers, "years": years, "pv": pv, "pv_cost": pv_cost, "build": build,
            "npv": pv["economic"] - pv_cost, "npv_budget": pv["budget"] - pv_cost,
            "roi": (pv["economic"] - pv_cost) / pv_cost if pv_cost else None,
            "payback_months": payback, "monthly_full": full, "cost_month_full": fixed + var,
            "agents_costed": modelled, "agents_missing_cost": [i for i in uc.get("agents", []) if i not in modelled]}


def break_even(uc, register, doc, fin_results, aid):
    a = register.get(aid)
    if not a or a.get("base") is None:
        return None
    def gap(x):
        r = uc_eval(uc, register, doc, fin_results, overrides={aid: x})
        return r["monthly_full"]["economic"] - r["cost_month_full"]
    hi = max(abs(float(a.get("base") or 0)), abs(float(a.get("high") or 0)), 1e-9) * 100.0
    lo = 0.0
    glo, ghi = gap(lo), gap(hi)
    if (glo > 0) == (ghi > 0):
        return {"assumption": aid, "value": None, "always_positive": glo > 0}
    for _ in range(80):
        mid = (lo + hi) / 2
        gm = gap(mid)
        if (gm > 0) == (glo > 0):
            lo, glo = mid, gm
        else:
            hi = mid
    return {"assumption": aid, "value": (lo + hi) / 2}


def portfolio(doc, register, fin_results, scenario="base", overrides=None):
    out, missing = [], []
    for uc in doc.get("use_cases", []):
        try:
            out.append(uc_eval(uc, register, doc, fin_results, scenario, overrides))
        except MissingInput as exc:
            missing.append({"use_case": uc.get("id"), "assumptions": exc.ids})
    return out, missing


def totals_of(rows):
    t = {"npv": sum(r["npv"] for r in rows), "npv_budget": sum(r["npv_budget"] for r in rows),
         "pv_cost": sum(r["pv_cost"] for r in rows), "build": sum(r["build"] for r in rows),
         "economic_year": sum(r["monthly_full"]["economic"] for r in rows) * 12,
         "budget_year": sum(r["monthly_full"]["budget"] for r in rows) * 12,
         "risk_year": sum(r["monthly_full"]["risk"] for r in rows) * 12,
         "cost_year": sum(r["cost_month_full"] for r in rows) * 12}
    t["roi"] = t["npv"] / t["pv_cost"] if t["pv_cost"] else None
    return t


def run(doc: dict, fin: dict | None) -> dict:
    register = register_of(doc, fin or {})
    fin_results = (fin or {}).get("results")
    base_rows, missing = portfolio(doc, register, fin_results)
    base_npv = sum(r["npv"] for r in base_rows)
    used = sorted({i for r in base_rows for lv in r["levers"] for i in lv["assumptions"]})
    sens = []
    for aid in used:
        a = register[aid]
        if a.get("low") is None or a.get("high") is None or str(a.get("status", "")).lower() == "rejected":
            continue
        lo_rows, _ = portfolio(doc, register, fin_results, overrides={aid: a["low"]})
        hi_rows, _ = portfolio(doc, register, fin_results, overrides={aid: a["high"]})
        nl, nh = sum(r["npv"] for r in lo_rows), sum(r["npv"] for r in hi_rows)
        sens.append({"id": aid, "npv_low": nl, "npv_high": nh, "swing": abs(nh - nl)})
    sens.sort(key=lambda x: -x["swing"])
    for i, s in enumerate(sens):
        s["rank"] = i + 1
    weak = {s["id"]: (register[s["id"]]["low"] if s["npv_low"] <= s["npv_high"] else register[s["id"]]["high"]) for s in sens}
    strong = {s["id"]: (register[s["id"]]["high"] if s["npv_low"] <= s["npv_high"] else register[s["id"]]["low"]) for s in sens}
    scen = {"weak": totals_of(portfolio(doc, register, fin_results, overrides=weak)[0]),
            "base": totals_of(base_rows),
            "strong": totals_of(portfolio(doc, register, fin_results, overrides=strong)[0])}
    rank = {s["id"]: s for s in sens}
    ucs = []
    for uc, r in zip([u for u in doc.get("use_cases", []) if u.get("id") in {x["id"] for x in base_rows}], base_rows):
        deps = sorted({i for lv in r["levers"] for i in lv["assumptions"]})
        be_id = uc.get("break_even_on") or next((s["id"] for s in sens if s["id"] in deps), None)
        be = break_even(uc, register, doc, fin_results, be_id) if be_id else None
        confs = [CONF.get(str(register[i].get("confidence", "low")).lower(), 1) for i in deps]
        st = [str(register[i].get("status", "open")).lower() for i in deps]
        done = sum(1 for x in st if x in ("confirmed", "adjusted"))
        r.update({"name": uc.get("name", ""), "agents": uc.get("agents", []), "assumptions": deps,
                  "confidence": {3: "high", 2: "medium", 1: "low"}[min(confs)] if confs else "low",
                  "status": "validated" if deps and done == len(deps) else ("partly validated" if done else "hypothesis"),
                  "open_assumptions": sum(1 for x in st if x == "open"),
                  "break_even": be,
                  "weak": next((x for x in portfolio({**doc, "use_cases": [uc]}, register, fin_results, overrides=weak)[0]), None),
                  "strong": next((x for x in portfolio({**doc, "use_cases": [uc]}, register, fin_results, overrides=strong)[0]), None)})
        # range: individual effects combined by root-sum-square (independent uncertainties); corners kept as weak/strong
        base_y = r["monthly_full"]["economic"] * 12
        down = up = 0.0
        for aid in deps:
            a = register[aid]
            if a.get("low") is None or a.get("high") is None or str(a.get("status", "")).lower() == "rejected":
                continue
            ys = [uc_eval(uc, register, doc, fin_results, overrides={aid: a[k]})["monthly_full"]["economic"] * 12 - base_y for k in ("low", "high")]
            down += min(0.0, *ys) ** 2
            up += max(0.0, *ys) ** 2
        r["range_year"] = {"low": max(0.0, base_y - down ** 0.5), "base": base_y, "high": base_y + up ** 0.5,
                           "weak": (r["weak"] or r)["monthly_full"]["economic"] * 12, "strong": (r["strong"] or r)["monthly_full"]["economic"] * 12,
                           "method": "root-sum-square of the individual effects"}
        r.pop("weak"), r.pop("strong")
        ucs.append(r)
    questions = [dict(rank[s["id"]], **{k: register[s["id"]].get(k) for k in ("statement", "question", "owner", "unit", "low", "base", "high", "confidence", "source_type")})
                 for s in [x for x in sens if x["swing"] > 0][:10]]
    return {"use_cases": ucs, "totals": totals_of(base_rows), "inputs_needed": missing, "sensitivity": sens,
            "questions": questions, "scenarios": scen, "npv_base": base_npv}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--value", required=True)
    ap.add_argument("--finops", help="finops.json with results (run finops_calc.py first)")
    ap.add_argument("--out", help="defaults to --value (results are written into the file)")
    a = ap.parse_args(argv)
    doc = load(a.value)
    fin = load(a.finops) if a.finops else None
    try:
        res = run(doc, fin)
    except (ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    doc["results"] = res
    Path(a.out or a.value).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    t = res["totals"]
    print(json.dumps({"use_cases": len(res["use_cases"]), "inputs_needed": res["inputs_needed"],
                      "npv": round(t["npv"], 2), "roi": round(t["roi"], 4) if t["roi"] is not None else None,
                      "economic_per_year": round(t["economic_year"], 2), "budget_per_year": round(t["budget_year"], 2),
                      "top_assumptions": [q["id"] for q in res["questions"][:5]], "out": a.out or a.value}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
