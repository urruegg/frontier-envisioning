#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Seed a blueprint JSON from a customer context pack (frontier-context/1.0).

Usage:
  python seed_blueprint.py --context customer-context.json --out blueprint.json
         [--defaults ../templates/blueprint-defaults.json] [--scope-label Journey]

The seed is deterministic scaffolding, not the hypothesis itself:
  * meta, evidence register, journeys (domains), stage names, KPIs, systems,
    stakeholder roles (as leaders), ideas (as use cases), actions (as next steps)
    and open questions are copied from the context pack with their citations;
  * the Innovation Hub canon (governance, security, knowledge, build & run,
    foundation, target-architecture layers, horizons) comes from the defaults;
  * every field the hypothesis still needs is listed in "_todo" and left empty,
    so the build shows "To be confirmed" rather than invented content.
Nothing is invented here: the agent team, stage details, approval seams and
autonomy levels are written next, by the person or Copilot running the skill.

Standard library only; no network access.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

PALETTE = ["#2B88D8", "#8764B8", "#107C41", "#CA5010", "#038387", "#C239B3", "#986F0B", "#4F6BED"]
DEFAULTS = Path(__file__).resolve().parent.parent / "templates" / "blueprint-defaults.json"
CATS = ["Business & process", "Data", "Systems & integration", "Governance & risk", "Value & KPIs", "Adoption & change"]


def as_list(x):
    return x if isinstance(x, list) else ([] if x in (None, "") else [x])


def cites(item) -> list[str]:
    out = [str(e["source"]) for e in as_list(item.get("evidence")) if isinstance(e, dict) and e.get("source")]
    out += [str(s) for s in as_list(item.get("src"))]
    return sorted(set(out))


def abbrev(role: str) -> str:
    known = {"chief executive officer": "CEO", "chief financial officer": "CFO", "chief information officer": "CIO",
             "chief technology officer": "CTO", "chief procurement officer": "CPO", "chief operating officer": "COO",
             "chief human resources officer": "CHRO", "chief commercial officer": "CCO", "chief digital officer": "CDO"}
    r = str(role or "").strip()
    if r.lower() in known:
        return known[r.lower()]
    if re.fullmatch(r"[A-Z]{2,5}", r):
        return r
    words = [w for w in re.split(r"[\s/&-]+", r) if w and w[0].isalpha() and w.lower() not in ("of", "and", "the", "for")]
    return "".join(w[0].upper() for w in words[:3]) or "?"


sys.path.insert(0, str(Path(__file__).resolve().parent))
from canon import add_canon  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--context", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--defaults", default=str(DEFAULTS))
    ap.add_argument("--scope-label", default="Journey", help="label for a domain, e.g. Journey or Pillar")
    a = ap.parse_args(argv)
    try:
        ctx = json.loads(Path(a.context).read_text(encoding="utf-8-sig"))
        dfl = json.loads(Path(a.defaults).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    cust = ctx.get("customer") or {}
    eng = ctx.get("engagement") or {}
    name = cust.get("name") or "Customer"
    short = cust.get("short") or name.split(" ")[0]
    fn = eng.get("function")
    todo: list[str] = []
    bp: dict = {
        "schema": "frontier-blueprint/1.0",
        "meta": {
            "id": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") + "-frontier",
            "customer": name, "short": short,
            "eyebrow": "Frontier Company Blueprint",
            "headline": f"{short}{' ' + fn if fn else ''} \u2014 a human-led, agent-operated {'function' if fn else 'company'}",
            "subtitle": "Hypothesis for the envisioning workshop",
            "engagement": eng.get("title") or "Solution envisioning & architecture design",
            "prepared_by": "Microsoft Innovation Hub",
            "workshop_date": eng.get("workshop_date", ""), "location": eng.get("location", ""),
            "status": "hypothesis", "audience": "internal", "version": "0.1",
            "date": _dt.date.today().isoformat(),
            "domain_label": a.scope_label, "domain_label_plural": a.scope_label.lower() + "s",
            "internal_terms": [],
        },
        "mission": {"label": "Mission (draft)", "statement": "", "attribution": "", "src": [],
                    "prompt": f"Does this mission reflect {short}'s ambition?"},
        "frontier": dict(dfl.get("frontier", {})),
        "outcomes": [], "measured_by": "",
        "human_led": dict(dfl.get("human_led", {})),
        "approval_seam": dfl.get("approval_seam", ""),
    }
    todo.append("mission.statement: draft from the strategy facts and cite them")
    todo.append("outcomes: 3-5 business outcomes with a short description each; measured_by")
    strategy = [f for f in as_list(ctx.get("facts")) if f.get("category") == "strategy"]
    if strategy:
        bp["mission"]["src"] = sorted({s for f in strategy for s in cites(f)})

    # evidence register
    bp["evidence"] = []
    for s in as_list(ctx.get("sources")):
        bp["evidence"].append({k: s[k] for k in ("id", "type", "title", "date", "source", "participants", "visibility", "summary", "quote") if s.get(k)})

    # leaders from stakeholders (roles only, customer side)
    leaders = []
    for st in as_list(ctx.get("stakeholders")):
        if str(st.get("org", "customer")).lower() != "customer" or not st.get("role"):
            continue
        leaders.append({"id": f"L{len(leaders) + 1}", "role": st["role"], "short": abbrev(st["role"]), "initials": abbrev(st["role"])[:3],
                        "direction": st.get("interests", ""), "decides": "", "src": cites(st)})
        if len(leaders) == 6:
            break
    bp["leaders"] = leaders
    if not leaders:
        todo.append("leaders: the accountable human leaders (roles) for the centre of the org model")

    facts = as_list(ctx.get("facts"))
    systems = as_list(ctx.get("systems"))
    bank = dfl.get("discovery_bank", {})
    domains = []
    for i, j in enumerate(as_list(ctx.get("journeys"))):
        jn = j.get("name") or f"Journey {i + 1}"
        did = f"D{i + 1}"
        mine = lambda x: str(x.get("journey", "")).lower() == jn.lower()  # noqa: E731
        d = {
            "id": did, "name": jn, "short_name": jn, "color": PALETTE[i % len(PALETTE)],
            "journey_name": j.get("journey_name") or f"{jn} journey", "journey_tagline": j.get("why", ""),
            "vision": "", "ai_contribution": "", "business_impact": "", "src": cites(j),
            "stages": [{"name": s if isinstance(s, str) else s.get("name", ""), "happens": "", "pain": "", "ai": "", "agent": ""} for s in as_list(j.get("stages"))],
            "personas": [],
            "orchestrator": {"id": f"{did}-LEAD", "name": f"{jn} Lead Agent", "mission": "", "owner": "", "autonomy": "Act with approval",
                             "horizon": "H2", "lifecycle": "Planned", "status": "hypothesis"},
            "agents": [],
            "systems": [x.get("name") for x in systems if x.get("name") and (mine(x) or not x.get("journey"))],
            "channels": {"people": ["Teams", "Microsoft 365 Copilot"], "triggered": []},
            "kpis": [{"kpi": k.get("kpi"), "definition": k.get("definition", ""), "baseline": k.get("baseline", ""), "target": k.get("target", ""), "src": cites(k)}
                     for k in as_list(ctx.get("kpis")) if mine(k)],
            "context_pains": [{"text": f.get("statement"), "src": cites(f)} for f in facts if f.get("category") == "pain" and mine(f)],
            "context_metrics": [{"text": f.get("statement"), "src": cites(f)} for f in facts if f.get("category") in ("metric", "kpi") and mine(f)],
            "horizon_plan": {"H1": "", "H2": "", "H3": ""},
            "use_cases": [],
        }
        disc = {c: [] for c in CATS}
        for q in as_list(ctx.get("open_questions")):
            if mine(q) or not q.get("journey"):
                cat = q.get("category") if q.get("category") in CATS else "Business & process"
                disc[cat].append({"q": q.get("q"), "why": q.get("why", ""), "status": "open"})
        for cat in CATS:
            if not disc[cat]:
                disc[cat] = [{"q": x, "status": "open"} for x in as_list(bank.get(cat))[:2]]
        d["discovery"] = disc
        for idea in as_list(ctx.get("ideas")):
            if mine(idea):
                d["use_cases"].append({"name": idea.get("name"), "horizon": "H1", "value": 3, "feasibility": 3, "status": "hypothesis", "src": cites(idea)})
        if j.get("leader_role"):
            for L in leaders:
                if L["role"].lower() == str(j["leader_role"]).lower():
                    d["leader"] = L["id"]
        domains.append(d)
        todo.append(f"{did} {jn}: stage details (happens, pain, ai, agent), personas, lead agent mission/owner, 3-6 specialist agents, approval_seam, use case scores, horizon_plan")
    if not domains:
        todo.append("domains: no journeys in the context pack; add at least one")
    bp["domains"] = domains

    for key in ("governance", "intelligence_resources", "security", "knowledge", "build_run", "foundation", "horizons", "architecture"):
        if key in dfl:
            bp[key] = json.loads(json.dumps(dfl[key]))
    sysnames = [x.get("name") for x in systems if x.get("name")]
    if sysnames and bp.get("architecture"):
        for L in bp["architecture"].get("layers", []):
            for b in L.get("blocks", []):
                if b.get("desc") == "[ERP, CRM, HCM to confirm]":
                    b["desc"] = ", ".join(sysnames[:6])
                if b.get("desc") == "[Fill from the context pack]":
                    b["desc"] = ", ".join(d["name"] for d in domains) or b["desc"]
    bp["architecture"]["decisions"] = []
    added = add_canon(bp, dfl)
    people = []
    for st in as_list(ctx.get("stakeholders")):
        if not st.get("name"):
            continue
        org = str(st.get("org", "customer")).lower()
        people.append({"name": st["name"], "org": short if org == "customer" else ("Microsoft" if org == "microsoft" else st.get("org")),
                       "role": st.get("role", ""), "focus": [], "contributions": [st["interests"]] if st.get("interests") else [], "src": cites(st)})
    if people:
        bp["attendees"] = {"title": "Workshop attendees and their contributions", "date": eng.get("workshop_date", ""), "place": eng.get("location", ""),
                           "note": "Roles and contributions are summarised from the workshop transcripts and whiteboards; names only for people who attended.",
                           "people": people}
    todo.append("attendees: after the workshop, each participant's focus (journeys, use cases) and contributions from the transcript and whiteboards")
    if added:
        todo.append("canon added (" + ", ".join(added) + "): adapt the Agent Factory to the customer's control plane, set the landing-zone stages and data classes per journey, review the canon ADRs, and agree IT-readiness owners and dates")
    bp["architecture"]["open_decisions"] = [
        {"id": f"TD-{i + 1:02d}", "question": c.get("text"), "owner": ""} for i, c in enumerate(as_list(ctx.get("constraints")))]
    bp["mvp_options"] = []
    bp["next_steps"] = [{"step": x.get("text"), "owner": x.get("owner", ""), "when": x.get("due", ""), "status": "Planned", "src": cites(x)}
                        for x in as_list(ctx.get("actions"))]
    todo.append("mvp_options: 2-3 MVP candidates with why and needs, after scoring the use cases")
    todo.append("architecture: flows for the MVP candidates, decisions (ADRs), patterns per journey")
    bp["_todo"] = todo
    Path(a.out).write_text(json.dumps(bp, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"out": a.out, "domains": len(domains), "evidence": len(bp["evidence"]), "leaders": len(leaders), "todo": todo}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
