#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Seeds the agent cost model (frontier-finops/1.0) from a Frontier Company Blueprint and its value case.

Usage:
  python seed_finops.py --blueprint blueprint.json --out finops.json [--value value.json] [--agents D3-A05,D2-A01]
         [--licensed-share 0.4]

Agents: --agents, else the agents of the value case's use cases, else the MVP agents. From each agent's canvas:
harness (Copilot Studio standard, declarative Copilot Chat, Foundry, GitHub), audience (employee or external),
licence coverage (employee-facing standard or Copilot Chat use by licensed users is included; workflow-started
runs and external audiences are billed), and events per session as labelled assumptions: generative answers,
tenant graph grounding when the agent uses SharePoint, OneDrive or Teams knowledge, agent actions for declared
actions, flow actions for workflows. Sessions come from the value case's volume assumption. Run and build effort
stay to collect. Every number is an assumption with an owner; review them before finops_calc.py.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

CALLED = re.compile(r"\b(called by|triggered by|started by|autonomous)\b", re.I)
HUMAN = re.compile(r"\b(employee|user|technician|manager|agent boss|customer|person|people|asks?|describes?|requests?|uploads?|opens?|types?)\b", re.I)
GRAPH = re.compile(r"\b(sharepoint|onedrive|teams|microsoft graph|outlook|mailbox)\b", re.I)
FLOW = re.compile(r"\b(workflow|agent flow|power automate|flow)\b", re.I)


def text(*parts) -> str:
    out = []
    for p in parts:
        out += p if isinstance(p, list) else [p]
    return " ".join(str(x) for x in out if x)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--value")
    ap.add_argument("--agents")
    ap.add_argument("--licensed-share", type=float, default=0.4)
    a = ap.parse_args(argv)
    bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8"))
    value = json.loads(Path(a.value).read_text(encoding="utf-8")) if a.value else {}
    agents = {}
    for d in bp.get("domains", []):
        for ag in ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + list(d.get("agents", [])):
            agents[ag.get("id")] = ag
    if a.agents:
        ids = [x.strip() for x in a.agents.split(",")]
    elif value.get("use_cases"):
        ids = [i for u in value["use_cases"] for i in u.get("agents", [])]
    else:
        ids = [i for i, ag in agents.items() if ag.get("mvp")]
    vol_of = {}
    for u in value.get("use_cases", []):
        for i in u.get("agents", []):
            vol_of.setdefault(i, (u.get("vars") or {}).get("volume"))
    taken = {x["id"] for x in value.get("assumptions", [])}
    n = [100]

    def new(**kw):
        while True:
            n[0] += 1
            i = f"ASS-{n[0]:03d}"
            if i not in taken:
                taken.add(i)
                break
        return dict({"id": i, "source_type": "hypothesis", "confidence": "low", "status": "open", "scope": "finops"}, **kw)

    lic = new(statement="Employees with a Microsoft 365 Copilot licence", unit="share", low=round(a.licensed_share / 2, 2), base=a.licensed_share,
              high=min(1.0, round(a.licensed_share * 1.75, 2)), owner="Microsoft 365 workplace team",
              question="How many employees will hold Microsoft 365 Copilot when the agents go live?")
    rate = new(statement="Loaded rate for run effort", unit="CHF/h", low=100, base=120, high=140, owner="Finance", confidence="medium",
               question="Which internal rate applies to the agent boss and maker?")
    ass, out, unknown, need_lic = [rate], [], [], False
    for i in ids:
        ag = agents.get(i)
        if not ag:
            unknown.append(i)
            continue
        c = ag.get("canvas") or {}
        tech = text(ag.get("technology"), c.get("build"), c.get("pattern"))
        harness = "copilot-chat" if re.search(r"declarative", tech, re.I) else ("foundry" if re.search(r"foundry", tech, re.I) else ("github" if re.search(r"github", tech, re.I) else "standard"))
        audience = "external" if re.search(r"\b(web|portal|customer|external|public)\b", text(ag.get("channels")), re.I) else "employee"
        triggers = [str(t) for t in (c.get("trigger") if isinstance(c.get("trigger"), list) else [c.get("trigger")]) if t]
        autonomous = bool(CALLED.search(text(ag.get("technology"), c.get("pattern")))) or (bool(triggers) and not any(HUMAN.search(t) for t in triggers))
        covered = audience == "employee" and harness in ("standard", "copilot-chat") and not autonomous
        need_lic = need_lic or covered
        name = ag.get("name", i)
        vol = vol_of.get(i)
        per = new(statement=f"{name}: sessions per case", unit="sessions", low=1, base=1, high=2, owner="Agent maker", question="How many conversations or runs does one case need?")
        ans = new(statement=f"{name}: generative answers per session", unit="answers", low=1, base=2, high=4, owner="Agent maker", question="How many answers does a typical session need?")
        act = new(statement=f"{name}: agent actions per session", unit="actions", low=0, base=max(1, sum(1 for x in c.get("connectors") or [] if "action" in str(x).lower())), high=4,
                  owner="Agent maker", question="Which actions does the agent call per session (including the trigger)?")
        ev = {"generative_answer": "answers", "agent_action": "actions"}
        vars_ = {"per_case": per["id"], "answers": ans["id"], "actions": act["id"]}
        extra = [per, ans, act]
        if GRAPH.search(text(c.get("data_sources"))):
            g = new(statement=f"{name}: answers grounded through tenant graph grounding", unit="share", low=0.1, base=0.5, high=0.9, owner="Agent maker",
                    question="Which knowledge needs tenant graph grounding rather than a scoped SharePoint source?")
            extra.append(g); vars_["grounded"] = g["id"]; ev["graph_grounding"] = "answers * grounded"
        if FLOW.search(tech):
            f = new(statement=f"{name}: flow actions per session", unit="actions", low=4, base=8, high=15, owner="Agent maker", question="How many flow actions does the workflow run per session?")
            extra.append(f); vars_["flow"] = f["id"]; ev["flow_action"] = "flow"
        if vol:
            vars_["volume"] = vol
        else:
            v = new(statement=f"{name}: cases per month", unit="per month", low=None, base=None, high=None, owner=ag.get("owner") or "Process owner",
                    question="How many cases per month will the agent handle?")
            extra.append(v); vars_["volume"] = v["id"]
        run = new(statement=f"{name}: run effort", unit="hours/month", low=8, base=16, high=32, owner=ag.get("owner") or "Agent boss", confidence="medium",
                  question="Who runs the agent, and for how many hours a month?")
        build = new(statement=f"{name}: build effort (one-time)", unit="CHF", low=None, base=None, high=None, owner="IT project lead", question="What does the build cost, including integrations?")
        extra += [run, build]
        vars_.update({"run_hours": run["id"], "run_rate": rate["id"], "build": build["id"], "sessions": "volume * per_case"})
        if covered:
            vars_["licensed_share"] = lic["id"]
        ass += extra
        out.append({"id": i, "name": (ag.get("identity") or {}).get("display_name") or name, "harness": harness, "audience": audience,
                    "coverage": "licensed users included" if covered else ("none: started by a workflow or schedule, every run is billed" if autonomous else "none: billed"),
                    "owner": ag.get("owner"), "vars": vars_,
                    "usage": {"sessions": "sessions", "billable_share": "1 - licensed_share" if covered else 1, "events_per_session": ev},
                    "people": {"run_hours_month": "run_hours", "rate_chf": "run_rate", "build_one_time_chf": "build"},
                    "outcome": {"name": "case handled", "per_month": "volume"}})
    if need_lic:
        ass.insert(0, lic)
    meta = bp.get("meta") or {}
    doc = {"schema": "frontier-finops/1.0", "customer": meta.get("customer"), "short": meta.get("short"),
           "title": f"Cost model for {meta.get('short') or meta.get('customer')} (seed)", "version": "0.1", "date": _dt.date.today().isoformat(),
           "status": "hypothesis", "currency": "CHF",
           "fx": {"policy": "swiss-list-ratio", "chf_per_usd": None, "source": "rates file (ratio implied by Swiss list prices); replace with the billing rate"},
           "purchase": {"option": "payg", "note": "Hypothesis: start on pay-as-you-go; decide on packs or P3 after a usage baseline"},
           "assumptions": ass, "agents": out,
           "credit_scenarios": ([{"name": "No Microsoft 365 Copilot licences", "kind": "licences", "set": {"licensed_share": 0}}] if need_lic else [])
                               + [{"name": "Twice the sessions per case", "kind": "usage", "set": {"per_case": 2}}]}
    Path(a.out).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"agents": [x["id"] for x in out], "assumptions": len(ass), "to_collect": sum(1 for x in ass if x.get("base") is None),
                      "unknown_agents": unknown, "out": a.out}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
