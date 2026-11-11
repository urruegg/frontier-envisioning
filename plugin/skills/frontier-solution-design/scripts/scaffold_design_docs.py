#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Scaffold the PRD, the solution design and ADRs for the selected MVP agents.

Usage:
  python scaffold_design_docs.py --blueprint blueprint.normalized.json --out-dir design/
         [--mvp D3-A05 D2-A01] [--author "Innovation Hub"] [--prefix CUS]

Without --mvp, every agent flagged "mvp" in the blueprint is in scope.
Writes:
  design/prd.md                 platform + MVP requirements (FR-, NFR-, AC-, D- ids)
  design/solution-design.md     layered target architecture, components, flows,
                                connector inventory, security, ALM, observability
  design/adr/ADR-0001-<slug>.md one file per blueprint architecture decision (Hub canon ADR-F.. included)
  design/it-readiness.md        IT preparation and readiness checklist (when the blueprint has "it_readiness")
Every table is filled from the blueprint (canvas, declarations, personas, KPIs,
architecture layers, landing zone, Agent Factory, decisions, open decisions, IT readiness). Narrative the blueprint cannot
supply is marked "[To complete]" so a reviewer sees the gap instead of filler.
Identifiers are allocated once per run in document order.

Standard library only; no network access.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prd_model import DECL, TC, derive as prd_derive  # noqa: E402


PRODUCTS = {"m365copilot": "Microsoft 365 Copilot", "agentbuilder": "Agent Builder", "copilotstudio": "Microsoft Copilot Studio",
            "agent365": "Microsoft Agent 365", "foundry": "Microsoft Foundry", "agentframework": "Microsoft Agent Framework",
            "entra": "Microsoft Entra", "defender": "Microsoft Defender", "purview": "Microsoft Purview", "teams": "Microsoft Teams",
            "outlook": "Microsoft Outlook", "onedrive": "Microsoft OneDrive", "powerautomate": "Power Automate", "powerapps": "Power Apps",
            "powerbi": "Power BI", "github": "GitHub", "ghcopilot": "GitHub Copilot", "ghcopilot_lockup": "GitHub Copilot",
            "vscode": "Visual Studio Code"}
LZ_ORDER = ["A", "B", "C", "J", "D1", "D2", "D3", "D4", "H", "I", "E", "G", "X", "R"]


def as_list(x):
    return x if isinstance(x, list) else ([] if x in (None, "") else [x])


def cell(x) -> str:
    if isinstance(x, list):
        x = "; ".join(str(i) for i in x)
    return str(x if x not in (None, "") else TC).replace("|", "/").replace("\n", " ")


def slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(t).lower()).strip("-")[:50] or "decision"


WF_NODES = {"agent": ("Agent", "AI"), "classify": ("Classify", "AI"), "extract": ("Extract", "AI"), "copilot": ("Copilot", "AI"),
            "human_review": ("Human review", "Human"), "connector": ("Connector", "Rule"), "function": ("Function", "Rule"),
            "variable": ("Variable", "Rule"), "if_else": ("If/Else", "Rule"), "loop": ("Loop", "Rule"), "scope": ("Scope", "Rule"),
            "note": ("Note", ""), "respond": ("Respond to the agent", "Rule")}
WF_TRIGGERS = {"manual": "Manual", "recurrence": "Recurrence", "connector": "Connector event",
               "http": "When an HTTP request is received", "agent": "When an agent calls the workflow"}


def workflow_section(a) -> list:
    """The agent's workflow (blueprint canvas.workflow) as the Copilot Studio workflow to build: trigger, nodes, branches, outcome."""
    wf = (a.get("canvas") or {}).get("workflow")
    if not isinstance(wf, dict) or not as_list(wf.get("steps")):
        return []
    tr = wf.get("trigger") or {}
    rows, kinds = [], {"AI": 0, "Rule": 0, "Human": 0}

    def add(steps, prefix):
        for i, s in enumerate([x for x in as_list(steps) if isinstance(x, dict)], start=1):
            num = f"{prefix}{i}"
            label, kind = WF_NODES.get(s.get("type"), (str(s.get("type") or "Agent"), "AI"))
            if kind in kinds:
                kinds[kind] += 1
            extra = []
            if s.get("agent"):
                extra.append(f"agent {s['agent']}")
            if s.get("approver"):
                extra.append(f"decides: {s['approver']}")
            for b in as_list(s.get("branches")):
                if isinstance(b, dict):
                    tail = " \u2192 ".join(str(z.get("label")) for z in as_list(b.get("steps")) if isinstance(z, dict))
                    end = (b.get("then") == "end") or (b.get("end") and b.get("then") != "continue")
                    extra.append(f"branch {b.get('label')}: {tail or 'no steps'}" + (f" \u2192 ends ({b.get('end') or 'End'})" if end else " \u2192 rejoins"))
            if as_list(s.get("defaults")):
                extra.append("continues on: " + ", ".join(map(str, as_list(s.get("defaults")))))
            rows.append([num, label, s.get("label"), "; ".join([str(s.get("detail") or "")] + extra).strip("; ") or "\u2014", s.get("system") or "\u2014"])
            if s.get("type") in ("loop", "scope"):
                add(s.get("steps"), num + ".")
            for bi, b in enumerate([x for x in as_list(s.get("branches")) if isinstance(x, dict)]):
                if as_list(b.get("steps")):
                    add(b.get("steps"), f"{num}{chr(97 + bi % 26)}.")
    add(wf.get("steps"), "")
    derived = " \u2014 derived from the canvas plan; refine it before build" if wf.get("derived") else ""
    trig = WF_TRIGGERS.get(tr.get("type"), "Connector event")
    if tr.get("label") and str(tr.get("label")).strip().lower() != trig.lower():
        trig += f" \u2014 {tr.get('label')}"
    L = [f"### Workflow: {wf.get('name') or a.get('name')} ({a.get('name')})", "",
         f"Copilot Studio workflow (GitHub Copilot harness){derived}.", "",
         f"- Trigger: {trig}" + (f" ({tr.get('detail')})" if tr.get("detail") else ""),
         f"- Desired outcome: {wf.get('outcome') or TC}",
         f"- Steps: {kinds['AI']} AI (results can vary), {kinds['Rule']} deterministic, {kinds['Human']} human", ""]
    L += table(["#", "Node", "Step", "What it does", "System"], rows)
    return L


def table(cols, rows) -> list[str]:
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return out + [""]


_SCOPE_FROM_AGENTS = object()


def collect(bp: dict, ids: list[str] | None):
    agents, doms = [], {}
    for d in as_list(bp.get("domains")):
        team = ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + as_list(d.get("agents"))
        for a in team:
            if (ids is not None and a.get("id") in ids) or (ids is None and a.get("mvp")):
                agents.append((a, d))
                doms[d.get("id")] = d
    return agents, list(doms.values())


def build_prd(bp, agents, doms, author, today, *, scope_ids=_SCOPE_FROM_AGENTS) -> str:
    """Render the shared PRD model, preserving canonical requirement IDs.

    scope_ids=None uses the default MVP model; a list (including []) is exact.
    Omitting this keyword preserves the existing API's supplied-agent scope.
    """
    M = bp.get("meta", {})
    if scope_ids is _SCOPE_FROM_AGENTS:
        scope_ids = [a.get("id") for a, _ in agents]
    P = prd_derive(bp, scope_ids)
    A = bp.get("prd") if isinstance(bp.get("prd"), dict) else {}
    L = [f"# Product Requirements \u2014 {M.get('customer', 'Customer')} agentic platform (MVP)", ""]
    L += table(["Field", "Value"], [["Version", A.get("version") or "Draft 0.1"], ["Date", today], ["Author", A.get("owner") or author],
                                    ["Status", {"hypothesis": "Hypothesis", "draft": "Draft for review",
                                                "agreed": "Scope agreed in the workshop", "adjusted": "Adjusted in the workshop",
                                                "rejected": "Rejected in the workshop"}.get(str(A.get("status", "")).lower(), "Draft for review")],
                                    ["Basis", P["basis"]], ["Scope", ", ".join(str(x["name"]) for x in P["scope"]) or TC]])
    L += ["## 1. Purpose", "",
          "This document states what the agentic platform must do, once, so that no individual agent has to restate it, and what each MVP agent must do on top. "
          "A use-case requirement may add to the platform requirements; it may never weaken them. "
          "It continues the PRD page of the blueprint (Part 1 Vision) with the same requirement ids.", ""]
    if A.get("problem") or P["problems"]:
        L += ["### 1.1 Problem", ""]
        L += [f"- {x}" for x in as_list(A.get("problem"))]
        for pr in P["problems"]:
            L += [f"- {pr['name']} ({prov}): {text}" for prov, text in pr["items"]]
        L += [""]
    L += ["## 2. Product vision", "", f"> {P['vision'] or TC}", "", "Three commitments shape every requirement:", ""]
    L += [f"- **{c[0]}** {c[1]}" for c in P["commitments"]] + [""]
    if as_list(A.get("goals")):
        L += ["### Goals", ""] + [f"- {g}" for g in as_list(A.get("goals"))] + [""]
    if as_list(A.get("non_goals")):
        L += ["### Non-goals", ""] + [f"- {g}" for g in as_list(A.get("non_goals"))] + [""]
    L += ["### 2.1 Maturity position", ""]
    L += table(["Dimension", "Today", "Target"], P["maturity"])
    L += ["### 2.2 MVP scope", ""]
    L += table(["Agent", "Journey", "Autonomy", "Horizon", "What it proves"],
               [[x["name"], x["journey_name"], x["autonomy"], x["horizon"], x["proves"]] for x in P["scope"]])
    L += ["**Exit test.** " + (A.get("exit_test") or (TC + " (for example: the second MVP costs materially less to build than the first because it reuses the platform).")), ""]
    L += ["## 3. Scope", "", "### 3.1 In scope", ""]
    L += [f"- {x['name']}: {x['capability']}" for x in P["scope"]]
    L += ["- The shared platform: identities, environments, DLP, workflow pattern, audit, observability", "", "### 3.2 Out of scope", ""]
    L += [f"- {x}" for x in as_list(A.get("out_of_scope"))] or [f"- {TC}"]
    L += ["", "## 4. Users and personas", ""]
    L += table(["Persona", "Journey", "Goal", "Pain today", "Decides"],
               [[x["role"], x["journey_name"], x["goal"], x["pain"], x["decides"]] for x in P["personas"]] or [[TC, "", "", "", ""]])
    L += ["## 5. Functional requirements", "", "### 5.1 Platform (every agent)", ""]
    L += table(["ID", "Requirement", "Priority", "Verified by"], [[r["id"], r["text"], r["priority"], r["verify"]] for r in P["platform"]])
    for idx, ag in enumerate(P["agents"], start=2):
        L += [f"### 5.{idx} {ag['name']} ({ag['journey_name']})", "", f"{ag['capability']}", ""]
        L += table(["ID", "Requirement", "Priority", "Verified by"], [[r["id"], r["text"], r["priority"], r["verify"]] for r in ag["requirements"]])
        L += ["**The seven declarations**", ""]
        L += table(["Declaration", "Value"], ag["declarations"])
    L += ["## 6. Non-functional requirements", ""]
    L += table(["ID", "Category", "Requirement"], [[x["id"], x["category"], x["text"]] for x in P["nfr"]])
    L += ["## 7. Acceptance criteria", ""]
    L += table(["ID", "Agent", "Criterion"], [[x["id"], x["agent_name"], x["text"]] for x in P["acceptance"]] or [["AC-001", TC, TC]])
    L += ["## 8. KPIs and measurement", ""]
    L += table(["KPI", "Journey", "Definition", "Baseline", "Target"],
               [[k["kpi"], k["journey_name"], k["definition"], k["baseline"], k["target"]] for k in P["kpis"]] or [[TC, "", "", "", ""]])
    L += ["## 9. Roles and accountability", ""]
    L += table(["Scope", "Accountable", "Responsibility"], P["roles"])
    L += ["## 10. Dependencies", ""]
    L += [f"- {x}" for x in P["dependencies"]] or [f"- {TC}"]
    L += ["", "## 11. Risks", ""]
    L += [f"- {(r['id'] + ' ') if r.get('id') else ''}{r['title']}"
          + (f" (score {r['score']:g}; mitigation: {r['mitigation']})" if r.get("score") else "") for r in P["risks"]] + [""]
    L += ["## 12. Open decisions", ""]
    L += table(["ID", "Decision needed", "Owner"], [[x["id"], x["question"], x["owner"]] for x in P["decisions"]] or [["D-01", TC, TC]])
    L += ["## 13. Definition of Ready", ""] + [f"- {x}" for x in P["definition_of_ready"]] + [""]
    L += ["## 14. Release plan", ""]
    rp = [r for r in as_list(A.get("release_plan")) if isinstance(r, list) and len(r) >= 3] or P["release_plan_default"]
    L += table(["Phase", "Scope", "Exit criterion"], rp)
    L += ["---", f"_Generated from the blueprint by the Frontier Envisioning plugin on {today}. Sections marked {TC} need the workshop evidence or the customer's input._"]
    return "\n".join(L) + "\n"


def products(keys) -> str:
    return ", ".join(dict.fromkeys(PRODUCTS.get(k, k) for k in as_list(keys) if isinstance(k, str))) or "\u2014"


def lz_section(bp) -> list[str]:
    """3.1 Landing zone: CAF design areas, WAF and Responsible AI principles, one agent landing zone per journey."""
    lz = (bp.get("architecture") or {}).get("landing_zone")
    if not isinstance(lz, dict) or not isinstance(lz.get("areas"), dict) or not lz["areas"]:
        return []
    L = ["### 3.1 Landing zone (Cloud Adoption Framework, Well-Architected, Responsible AI)", ""]
    if lz.get("intro"):
        L += [str(lz["intro"]), ""]
    rows = []
    for key, blk in (lz.get("principles") or {}).items() if isinstance(lz.get("principles"), dict) else []:
        for it in as_list((blk or {}).get("items")):
            if isinstance(it, list) and len(it) >= 3:
                rows.append([(blk or {}).get("short") or key.upper(), it[1], it[2]])
    if rows:
        L += ["#### Principles", ""] + table(["Lens", "Principle", "Meaning"], rows)
    areas = lz["areas"]
    keys = [k for k in LZ_ORDER if k in areas] + [k for k in areas if k not in LZ_ORDER and k not in ("P", "D", "F")]
    rows = [[(areas[k] or {}).get("letter") or k, (areas[k] or {}).get("title"), (areas[k] or {}).get("sub") or "\u2014",
             "; ".join(str(b) for b in as_list((areas[k] or {}).get("bullets"))[:3]) or "\u2014", products((areas[k] or {}).get("logos"))] for k in keys]
    L += ["#### Design areas", ""] + table(["Area", "Title", "Design area", "Key points", "Microsoft products"], rows)
    zones = [z for z in as_list(lz.get("lz")) if isinstance(z, dict)]
    if zones:
        names = {d.get("id"): d.get("name") for d in as_list(bp.get("domains"))}
        cls = {c[0]: c[1] for c in as_list(lz.get("classes")) if isinstance(c, list) and len(c) >= 2}
        stg = lz.get("stages") if isinstance(lz.get("stages"), dict) else {}
        rows = []
        for z in zones:
            zs = z.get("stages") if isinstance(z.get("stages"), dict) else {}
            rows.append([names.get(z.get("domain"), z.get("domain")), *[stg.get(zs.get(e), zs.get(e)) or "\u2014" for e in ("DEV", "TEST", "PROD")],
                         ", ".join(cls.get(c, c) for c in as_list(z.get("classes"))) or "\u2014", z.get("mvp") or "\u2014"])
        L += ["#### Agent landing zones per journey", ""] + table(["Journey", "DEV", "TEST", "PROD", "Data classes allowed", "MVP"], rows)
    if as_list(lz.get("common")):
        L += [f"- {c}" for c in lz["common"]] + [""]
    return L


def factory_section(bp) -> list[str]:
    """8.x Agent Factory: lifecycle with gates, Definition of Ready, evaluation pyramid, controls."""
    f = bp.get("factory")
    if not isinstance(f, dict):
        return []
    L = []
    if as_list(f.get("lifecycle")):
        L += ["### 8.1 Agent Factory lifecycle (hypothesis to operate)", ""]
        L += table(["Stage", "What happens", "Gate to the next stage"], [[x.get("name"), x.get("what"), x.get("gate")] for x in f["lifecycle"] if isinstance(x, dict)])
    if as_list(f.get("handover")):
        L += ["### 8.2 Definition of Ready (handover to build)", ""]
        L += table(["Check", "Meaning"], [[x[0], x[1]] for x in f["handover"] if isinstance(x, list) and len(x) >= 2])
    if as_list(f.get("pyramid")):
        L += ["### 8.3 Evaluation pyramid", ""]
        L += table(["Level", "Name", "What is tested", "When", "Threshold"], [list(x[:5]) + [""] * (5 - len(x[:5])) for x in f["pyramid"] if isinstance(x, list)])
    if as_list(f.get("controls")):
        L += ["### 8.4 Factory controls", ""] + [f"- {c}" for c in f["controls"]] + [""]
    return L


def build_readiness(bp, today) -> str | None:
    r = bp.get("it_readiness")
    if not isinstance(r, dict) or not (r.get("groups") or r.get("checks")):
        return None
    M = bp.get("meta", {})
    L = [f"# IT preparation and readiness \u2014 {M.get('customer', 'Customer')}", ""]
    L += table(["Field", "Value"], [["Version", "Draft 0.1"], ["Date", today], ["Status", "Prepare before the architecture design workshop"],
                                    ["Companion", "solution-design.md, adr/"]])
    if r.get("intro"):
        L += [str(r["intro"]), ""]
    w = r.get("workshop") if isinstance(r.get("workshop"), dict) else {}
    if w:
        L += [f"## 1. {w.get('title') or 'Architecture design workshop'}", ""]
        if as_list(w.get("outcomes")):
            L += ["Outcomes:", ""] + [f"- {x}" for x in w["outcomes"]] + [""]
        if as_list(w.get("who")):
            L += ["Who should attend: " + ", ".join(str(x) for x in w["who"]) + ".", ""]
        if as_list(w.get("agenda")):
            L += table(["Time", "Topic"], [[x[0], x[1]] if isinstance(x, list) and len(x) >= 2 else ["", x] for x in w["agenda"]])
    cp = r.get("control_plane") if isinstance(r.get("control_plane"), dict) else {}
    if as_list(cp.get("options")):
        L += ["## 2. Engineering control plane", ""]
        L += table(["Option", "Name", "Fits when", "Strengths", "Watch"], [[o.get("id"), o.get("name"), o.get("fits"), o.get("strengths"), o.get("watch")] for o in cp["options"] if isinstance(o, dict)])
        if as_list(cp.get("criteria")):
            L += ["Decision criteria:", ""] + [f"- {c}" for c in cp["criteria"]] + [""]
    L += ["## 3. Preparation items", ""]
    for g in as_list(r.get("groups")):
        if not isinstance(g, dict):
            continue
        L += [f"### {g.get('title') or g.get('id')}", ""]
        L += table(["ID", "Item", "Why", "Owner", "Needed by", "Status"],
                   [[x.get("id"), x.get("item"), x.get("why"), x.get("owner"), x.get("stage"), x.get("status") or "open"] for x in as_list(g.get("items")) if isinstance(x, dict)])
    if as_list(r.get("checks")):
        L += ["## 4. Readiness checks", ""]
        L += table(["ID", "Kind", "Check", "Test", "Evidence", "Status"], [[x.get("id"), x.get("kind"), x.get("check"), x.get("test"), x.get("evidence"), x.get("status") or "open"] for x in r["checks"] if isinstance(x, dict)])
    if as_list(r.get("workstation")):
        L += ["## 5. Builder workstation", ""]
        L += table(["ID", "Check", "Expected", "Status"], [[x.get("id"), x.get("check"), x.get("expected"), x.get("status") or "open"] for x in r["workstation"] if isinstance(x, dict)])
    if as_list(r.get("questions")):
        L += ["## 6. Questions for IT", ""]
        L += table(["ID", "Topic", "Question", "Who answers", "Status", "Answer"], [[x.get("id"), x.get("group"), x.get("question"), x.get("who"), x.get("status") or "open", x.get("answer") or "\u2014"] for x in r["questions"] if isinstance(x, dict)])
    if as_list(r.get("decisions")):
        L += ["## 7. Decisions to take", ""]
        L += table(["ID", "Decision", "Options", "Recommendation", "Owner", "Status"], [[x.get("id"), x.get("decision"), x.get("options"), x.get("recommendation"), x.get("owner"), x.get("status") or "open"] for x in r["decisions"] if isinstance(x, dict)])
    if as_list(r.get("environments")):
        L += ["## 8. Environments", ""]
        L += table(["Environment", "Purpose", "Type", "Region", "Status"], [[x.get("name"), x.get("purpose"), x.get("type"), x.get("region"), x.get("status")] for x in r["environments"] if isinstance(x, dict)])
    if as_list(r.get("timeline")):
        L += ["## 9. Timeline", ""]
        L += table(["When", "What"], [[x[0], x[1]] for x in r["timeline"] if isinstance(x, list) and len(x) >= 2])
    L += ["---", f"_Generated from the blueprint by the Frontier Envisioning plugin on {today}. Status values are as captured in the blueprint and the workshop notes._"]
    return "\n".join(L) + "\n"


def build_sd(bp, agents, doms, author, today) -> str:
    M = bp.get("meta", {})
    A = bp.get("architecture") or {}
    L = [f"# Solution Design \u2014 {M.get('customer', 'Customer')} agentic platform (target architecture)", ""]
    L += table(["Field", "Value"], [["Version", "Draft 0.1"], ["Date", today], ["Author", author], ["Status", "Draft for review"],
                                    ["Companion", "prd.md (what the MVP must do)"]])
    L += ["## 1. Purpose", "", "The PRD states what the MVP agents must do; this document describes the architecture they run on, which every later agent reuses. "
          "It is written so the second use case costs materially less than the first.", ""]
    L += ["## 2. Architecture principles", ""]
    L += table(["Principle", "Meaning"], [[p.get("name"), p.get("desc")] for p in as_list(A.get("principles"))] or [[TC, TC]])
    L += ["## 3. Layered target architecture", "", "```"]
    for ly in as_list(A.get("layers")):
        names = " \u00b7 ".join(b.get("name", "") for b in as_list(ly.get("blocks")))
        L.append(f"{ly.get('name', '')[:46]:<46} {names}")
    L += ["```", ""]
    rows = []
    for ly in as_list(A.get("layers")):
        for b in as_list(ly.get("blocks")):
            rows.append([ly.get("name"), b.get("name"), b.get("desc") or "\u2014", b.get("status") or "Verify", b.get("tag") or "\u2014"])
    L += table(["Layer", "Component", "Role", "Availability", "MVP"], rows or [[TC, "", "", "", ""]])
    L += ["Availability reflects the sources cited at the time of writing; re-check on Microsoft Learn before build decisions.", ""]
    L += lz_section(bp)
    L += ["## 4. Component design per MVP agent", ""]
    for k, (a, d) in enumerate(agents, start=1):
        c = a.get("canvas") or {}
        L += [f"### 4.{k} {a.get('name')}", ""]
        L += table(["Aspect", "Design"], [
            ["Journey / stage", d.get("name")], ["Build choice", c.get("build") or a.get("technology")],
            ["Orchestration pattern", c.get("pattern")], ["Autonomy", c.get("autonomy") or a.get("autonomy")],
            ["Instructions (summary)", c.get("instructions")], ["Skills", c.get("skills")],
            ["Knowledge", c.get("data_sources")], ["Tools and connectors", c.get("connectors")],
            ["Approval seams", c.get("approval")], ["Owner (agent boss)", a.get("owner")]])
    L += ["## 5. Process design", ""]
    for a, d in agents:
        L += workflow_section(a)
    for f in as_list(A.get("flows")):
        L += [f"### {f.get('name', 'Flow')}", "", f.get("note") or "", ""]
        L += table(["#", "Actor", "Step"], [[str(i + 1), s.get("actor"), s.get("text")] for i, s in enumerate(as_list(f.get("steps")))])
    if not as_list(A.get("flows")) and not any(isinstance((a.get("canvas") or {}).get("workflow"), dict) for a, _ in agents):
        L += [f"{TC} \u2014 one flow per MVP agent: trigger, workflow steps, agent node(s), approval seam, write-back, notification.", ""]
    L += ["## 6. Integration and connector inventory", ""]
    rows = []
    for a, _ in agents:
        for con in as_list((a.get("canvas") or {}).get("connectors")):
            rows.append([con, a.get("name"), "Workflow / access layer (never the agent for writes)", "Verify (Standard / Premium)"])
    L += table(["Connector or tool", "Used by", "Held by", "Tier"], rows or [[TC, "", "", ""]])
    L += ["All connectors sit in one DLP data group per environment; anything that can send data outside the tenant is blocked unless reviewed.", ""]
    L += ["## 7. Security design", ""]
    L += table(["Identity", "Purpose", "Never"], [
        ["Agent identity (Microsoft Entra Agent ID), per environment", "Read grounding sources, call declared tools", "Hold system-of-record write credentials"],
        ["Workflow / service identity", "Own connections through connection references; perform declared writes", "Interactive sign-in; shared with people"],
        ["System-of-record integration user", "The credential the connection authenticates as", "Broader permissions than the write envelope"],
        ["Human users", "Start runs, approve at seams, resolve exceptions", "Bypass the approval workflow"]])
    L += ["Controls: outside content is data (injection defence), least privilege per agent, Conditional Access on agent identities, Purview DLP and audit, "
          "Defender threat protection, Agent 365 registry and policies.", ""]
    L += ["## 8. Application lifecycle", ""]
    L += table(["Stage", "Practice"], [["Source of truth", "Unmanaged solution in DEV, exported to source control"],
                                       ["Promotion", "Managed solutions to TEST and PROD through a pipeline"],
                                       ["Configuration", "Environment variables and connection references; nothing hard-coded"],
                                       ["Approval", "Recorded approval gate before PROD"], ["Rollback", "Roll forward with a corrected managed solution"]])
    L += factory_section(bp)
    L += ["## 9. Observability and evaluation", ""]
    L += table(["Signal", "Source", "Surfaced in"], [["Run status, counts, exceptions", "Workflow run records", "Control view / Teams"],
                                                    ["Agent quality", "Evaluation test sets (Copilot Studio, Foundry)", "Release gate, CI/CD"],
                                                    ["Traces, guardrails", "Foundry Control Plane / Application Insights", "Operations"],
                                                    ["Consumption", "Copilot Credits, capacity", "Admin center alerts"],
                                                    ["Data protection events", "Microsoft Purview", "Purview"]])
    L += ["## 10. Reuse model", "", f"{TC} \u2014 what the second agent reuses as-is (identities, environments, DLP, workflow pattern, refusal and escalation skills, audit) and what it adds.", ""]
    L += ["## 11. Orchestration patterns", ""]
    L += table(["Pattern", "Where", "Why"], [[p.get("pattern"), p.get("where"), p.get("why")] for p in as_list(A.get("patterns"))] or [[TC, "", ""]])
    L += ["## 12. Open technical decisions", ""]
    L += table(["ID", "Decision", "Owner"], [[x.get("id"), x.get("question"), x.get("owner")] for x in as_list(A.get("open_decisions"))] or [["TD-01", TC, TC]])
    L += ["## 13. Architecture decisions", ""]
    L += table(["ID", "Title", "Decision", "Status", "Landing-zone areas", "Origin"],
               [[x.get("id"), x.get("title"), x.get("decision") or TC, x.get("status") or "proposed", ", ".join(str(v) for v in as_list(x.get("areas"))) or "\u2014",
                 "Innovation Hub canon" if x.get("canon") else "Customer"] for x in as_list(A.get("decisions"))] or [[TC, "", "", "", "", ""]])
    if as_list(A.get("sources")):
        L += ["## Sources", ""] + [f"- {s}" for s in A["sources"]] + [""]
    L += ["---", f"_Generated from the blueprint by the Frontier Envisioning plugin on {today}._"]
    return "\n".join(L) + "\n"


def build_adr(x: dict, n: int, today: str) -> tuple[str, str]:
    num = f"ADR-{n:04d}"
    name = f"{num}-{slug(x.get('title', 'decision'))}.md"
    L = [f"# {num}: {x.get('title', TC)}", "", f"- Status: {x.get('status', 'proposed')}", f"- Date: {today}", f"- Blueprint reference: {x.get('id', '')}"]
    if as_list(x.get("areas")):
        L.append("- Landing-zone areas: " + ", ".join(str(v) for v in x["areas"]))
    if x.get("canon"):
        L.append("- Origin: Innovation Hub canon; confirm or adapt it with the customer")
    L += ["",
         "## Context", "", x.get("context") or TC, "", "## Decision", "", x.get("decision") or TC, "",
         "## Rationale", "", x.get("rationale") or TC, "", "## Alternatives considered", "", x.get("alternatives") or TC, "",
         "## Consequences", "", x.get("consequences") or TC, ""]
    notes = [n for n in as_list(x.get("workshop_notes")) if isinstance(n, dict)]
    if notes:
        L += ["## Workshop notes", ""] + [f"- {n.get('date', '')}: {n.get('note', '')}" for n in notes] + [""]
    return name, "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--mvp", nargs="*", default=None, help="agent ids in scope (omitted: agents flagged mvp; an empty list selects none)")
    ap.add_argument("--author", default="Microsoft Innovation Hub")
    a = ap.parse_args(argv)
    try:
        bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    agents, doms = collect(bp, a.mvp)
    if not agents:
        print("ERROR: no MVP agents found; flag agents with \"mvp\" or pass --mvp <agent ids>", file=sys.stderr)
        return 1
    today = _dt.date.today().isoformat()
    out = Path(a.out_dir)
    (out / "adr").mkdir(parents=True, exist_ok=True)
    (out / "prd.md").write_text(build_prd(bp, agents, doms, a.author, today, scope_ids=a.mvp), encoding="utf-8")
    (out / "solution-design.md").write_text(build_sd(bp, agents, doms, a.author, today), encoding="utf-8")
    adrs = []
    for i, x in enumerate(as_list((bp.get("architecture") or {}).get("decisions")), start=1):
        name, text = build_adr(x, i, today)
        (out / "adr" / name).write_text(text, encoding="utf-8")
        adrs.append(name)
    rd = build_readiness(bp, today)
    if rd:
        (out / "it-readiness.md").write_text(rd, encoding="utf-8")
    todo = sum(p.read_text(encoding="utf-8").count(TC) for p in [out / "prd.md", out / "solution-design.md"])
    print(json.dumps({"prd": str(out / "prd.md"), "solution_design": str(out / "solution-design.md"), "adrs": adrs,
                      "it_readiness": str(out / "it-readiness.md") if rd else None,
                      "mvp_agents": [x.get("id") for x, _ in agents], "to_complete_markers": todo}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
