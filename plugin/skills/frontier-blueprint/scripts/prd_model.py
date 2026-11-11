# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""PRD model shared by the blueprint (Part 1 Vision > PRD) and the design scaffold (design/prd.md).

One derivation, two renderings: build_blueprint.py embeds the model as bp["prd"] (the PRD page of the blueprint),
scaffold_design_docs.py writes prd.md from the same model, so requirement, acceptance and decision ids match.
Keep this file identical in frontier-blueprint/scripts and frontier-solution-design/scripts (the self-test checks it).

  derive(bp, ids=None)  the PRD model for the MVP agents (or the given agent ids)
  fill_prd(bp, rep)     authored PRD fields kept, derived fields recomputed (used by build_blueprint.py)
Standard library only.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

TC = "[To complete]"
DECL = [("write_envelope", "Write envelope"), ("refusal_set", "Refusal set"), ("escalation_path", "Escalation path"),
        ("grounding_sources", "Grounding sources"), ("data_classification", "Data classification"),
        ("people_decisions", "People-decision surface"), ("measurement", "Measurement")]
PLATFORM_FR = [
    ("Every agent identifies itself as an agent at the start of any interaction and never presents itself as a person.", "Conversation review"),
    ("Every agent operates within a declared write envelope (targets, fields, conditions); an undeclared write is not possible, not merely disallowed.", "Envelope document and negative test"),
    ("Every agent has a declared refusal set and records each refusal with its reason.", "Refusal test suite"),
    ("Every agent has a named escalation path to a human owner, reachable in Teams.", "Escalation test"),
    ("No agent makes or communicates a decision about a person (hiring, pay, performance, promotion, exit); agents prepare, people decide.", "Behaviour review at design and release"),
    ("Every process is implemented workflow-first; an agent is invoked only at steps that need reasoning a rule cannot express.", "Design review"),
    ("The audit record is written by deterministic workflow steps, never left to the agent's discretion.", "Audit export review; forced-failure test"),
    ("Every run surfaces its outcome, including everything it could not complete, to a named human owner. Silent partial success is a defect.", "Run-completion review"),
    ("Writes to systems of record pass through declared actions that enforce read-before-write, an allow-list and idempotency server-side.", "Negative test: out-of-envelope call is rejected"),
    ("Content from outside the platform (emails, documents, web pages, supplier or customer text) is treated as data, never as instruction.", "Prompt-injection test set"),
]
NFR = [
    ("Security", "Every identity holds least privilege; agent identities, workflow/service identities and system-of-record credentials are distinct and separately scoped (Microsoft Entra Agent ID)."),
    ("Security", "No long-lived secret where workload identity federation is available; unavoidable secrets live in Azure Key Vault with rotation."),
    ("Security", "Conditional Access and Agent 365 policies apply to every agent identity; every agent is registered with an owner."),
    ("Privacy", "No personal data in prompts, logs or telemetry beyond the references needed to act; retention is defined per artefact class."),
    ("Privacy", "Processing and storage respect the customer's data residency requirements (Swiss / EU regions where available) and revFADP / GDPR."),
    ("Governance", "A DLP policy covering the full connector inventory is applied to every environment before the first artefact is built."),
    ("Governance", "Each agent carries a risk tier, an autonomy level and the seven declarations; release requires a named human approval."),
    ("Reliability", "Integration calls retry with backoff inside the workflow or access layer, not in agent logic; writes are idempotent under retry."),
    ("Operability", "Run status, outcome distribution, exception rate, evaluation scores and Copilot Credit consumption are observable without reading logs."),
    ("Maintainability", "No environment-specific value is hard-coded; promotion uses managed solutions through a pipeline (DEV, TEST, PROD)."),
    ("Availability", "Capacity and consumption are monitored and alerted in every environment so that runs are never blocked silently."),
    ("Cost", "Reasoning is invoked only where needed; deterministic steps handle well-formed inputs; evaluation is budgeted as recurring spend."),
]
COMMITMENTS = [
    ("Systems of record stay authoritative.", "The platform makes them easier to keep correct; it never becomes an alternative to them."),
    ("Agents act within declared envelopes.", "What an agent may write is decided in advance, written down and enforced where the agent cannot reach it."),
    ("People decide.", "Agents prepare the evidence; named people approve at the seam."),
]
RELEASE_PLAN = [["MVP", "One journey stage, one region, read-only or narrow reversible write", TC],
                ["Pilot", "Declared writes after approval, real users", TC],
                ["Scale", "More regions and journeys on the same platform", TC]]
DOR = ["All seven declarations are written for every MVP agent and reviewed by its agent boss",
       "Data access confirmed: read path, declared write actions, service identity, test data under NDA",
       "Environments (DEV, TEST, PROD) and the DLP policy exist before the first artefact",
       "Licensing and Copilot Credit budget approved; capacity alerts configured",
       "Works council, data protection and security reviews scheduled where required"]
ROLES = [["Platform", "Customer IT / platform owner", "Environments, identities, DLP, ALM"],
         ["Agent lifecycle", "Intelligence Resources (IT + HR)", "Registry, onboarding, upskilling, retirement"],
         ["Security and privacy", "CISO / DPO", "Risk tier, data protection, release approval"]]
# fields an author may set in bp["prd"]; everything else in the block is derived again on every build
AUTHORED = ("title", "status", "owner", "version", "problem", "goals", "non_goals", "out_of_scope", "exit_test",
            "release_plan", "notes", "src", "workshop_notes", "internal")


def as_list(x):
    return x if isinstance(x, list) else ([] if x in (None, "") else [x])


def _team(d):
    return ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + [a for a in as_list(d.get("agents")) if isinstance(a, dict)]


def mvp_agents(bp: dict, ids=None) -> list:
    """(agent, journey) pairs in scope, in document order: the given agent ids, else every agent flagged mvp."""
    out = []
    for d in as_list(bp.get("domains")):
        if not isinstance(d, dict):
            continue
        for a in _team(d):
            if (ids is not None and a.get("id") in ids) or (ids is None and a.get("mvp")):
                out.append((a, d))
    return out


def _use_cases(bp):
    out = []
    for d in as_list(bp.get("domains")):
        if isinstance(d, dict):
            out += [(u, d) for u in as_list(d.get("use_cases")) if isinstance(u, dict)]
    dom = {d.get("id"): d for d in as_list(bp.get("domains")) if isinstance(d, dict)}
    out += [(u, dom.get(u.get("domain"), {})) for u in as_list(bp.get("use_cases")) if isinstance(u, dict)]
    return out


def _uses(u, agents) -> bool:
    names = {str(a.get("name", "")).lower() for a, _ in agents} | {str(a.get("id", "")).lower() for a, _ in agents}
    return any(str(x).lower() in names for x in as_list(u.get("agents")))


def derive(bp: dict, ids=None) -> dict:
    """The PRD model: scope, problem, goals, personas, requirements (FR-, NFR-, AC-), KPIs, dependencies, risks, decisions."""
    agents = mvp_agents(bp, ids)
    doms = []
    for _, d in agents:
        if d not in doms:
            doms.append(d)
    M, F = bp.get("meta") or {}, bp.get("frontier") or {}
    n, platform = 1, []
    for text, verify in PLATFORM_FR:
        platform.append({"id": f"FR-{n:04d}", "text": text, "priority": "Must", "verify": verify})
        n += 1
    ac, acs, per_agent = 1, [], []
    # Number the full canonical scope before selection. MVP agents retain the
    # original document-order IDs; other agents follow them in document order.
    canonical = mvp_agents(bp) + [
        (a, d) for d in as_list(bp.get("domains")) if isinstance(d, dict)
        for a in _team(d) if not a.get("mvp")
    ]
    for a, d in canonical:
        c = a.get("canvas") if isinstance(a.get("canvas"), dict) else {}
        items = []

        def add(kind, text, verify):
            nonlocal n
            items.append({"id": f"FR-{n:04d}", "kind": kind, "text": text, "priority": "Must", "verify": verify})
            n += 1
        for t in as_list(c.get("trigger") or a.get("trigger")):
            add("trigger", f"The agent run starts when: {t}", "Trigger test")
        for step in as_list(c.get("plan")):
            add("step", str(step), "Functional test")
        for ap in as_list(c.get("approval")):
            add("approval", f"Approval seam: {ap}", "Workflow test (state persisted at the gate)")
        if c.get("outcome") or a.get("outcome"):
            add("outcome", f"Outcome: {c.get('outcome') or a.get('outcome')}", "Acceptance test")
        if not items:
            add("todo", TC, "")
        decl = a.get("declarations") if isinstance(a.get("declarations"), dict) else {}
        for k, lbl in (("refusal_set", "refuses and records the reason when"), ("write_envelope", "never writes outside its envelope:"),
                       ("measurement", "is measured by")):
            if decl.get(k):
                acs.append({"id": f"AC-{ac:03d}", "agent": a.get("id"), "agent_name": a.get("name"), "text": f"The agent {lbl} {decl[k]}"})
                ac += 1
        per_agent.append({"agent": a.get("id"), "name": a.get("name"), "journey": d.get("id"), "journey_name": d.get("name"),
                          "capability": a.get("capability") or TC, "requirements": items,
                          "declarations": [[lbl, decl.get(k) or TC] for k, lbl in DECL]})
    selected = {a.get("id") for a, _ in agents}
    per_agent = [a for a in per_agent if a["agent"] in selected]
    acs = [a for a in acs if a["agent"] in selected]
    ucs = [(u, d) for u, d in _use_cases(bp) if _uses(u, agents) or (ids is None and u.get("mvp"))]
    did = {d.get("id") for d in doms}
    problems = []
    for u, d in ucs:
        pr = [p for p in as_list(u.get("problem")) if p]
        rows = [[str(p[0]), str(p[1])] if isinstance(p, list) and len(p) >= 2 else ["hypothesis", str(p)] for p in pr]
        if rows or u.get("pain"):
            problems.append({"use_case": u.get("id"), "name": u.get("name"), "journey": d.get("id"),
                             "items": rows or [["hypothesis", str(u.get("pain"))]], "src": as_list(u.get("src"))})
    kpis = [{"kpi": k.get("kpi"), "journey": d.get("id"), "journey_name": d.get("name"), "definition": k.get("definition"),
             "baseline": k.get("baseline"), "target": k.get("target")}
            for d in doms for k in as_list(d.get("kpis")) if isinstance(k, dict)]
    personas = [{"role": p.get("role"), "journey": d.get("id"), "journey_name": d.get("name"), "goal": p.get("goal"),
                 "pain": p.get("pain"), "decides": p.get("decides")}
                for d in doms for p in as_list(d.get("personas")) if isinstance(p, dict)]
    deps = []
    for u, _ in ucs:
        deps += [str(x) for x in as_list(u.get("dependencies"))]
    for m in as_list(bp.get("mvp_options")):
        if (isinstance(m, dict) and m.get("needs")
                and (ids is None or (_uses(m, agents) if m.get("agents") else m.get("domain") in did))):
            deps.append(str(m["needs"]))
    reg = bp.get("risks") if isinstance(bp.get("risks"), dict) else {}
    aid = {a.get("id") for a, _ in agents}
    uid = {u.get("id") for u, _ in ucs}
    risks = []
    for r in as_list(reg.get("items")):
        if not isinstance(r, dict) or str(r.get("status", "open")).lower() in ("closed", "rejected"):
            continue
        linked = (set(as_list(r.get("agents"))) & aid) or (set(as_list(r.get("use_cases"))) & uid) or (set(as_list(r.get("journeys"))) & did)
        sc = int(_num(r.get("likelihood"), 3) * _num(r.get("impact"), 3))
        include = linked or sc >= 12 or r.get("canon")
        if ids is not None:
            # Specific links constrain explicit scope; a high score cannot
            # import another agent or journey. Unlinked canon risks are platform-wide.
            agent_refs, uc_refs, journey_refs = (set(as_list(r.get(k))) for k in ("agents", "use_cases", "journeys"))
            scoped = bool(agent_refs & aid) if agent_refs else bool(uc_refs & uid) if uc_refs else bool(journey_refs & did)
            unlinked = not (agent_refs or uc_refs or journey_refs)
            include = bool(agents) and (scoped or (unlinked and r.get("canon")))
        if include:
            risks.append({"id": r.get("id"), "title": r.get("title"), "score": sc, "mitigation": r.get("mitigation") or TC})
    risks.sort(key=lambda x: -x["score"])
    for u, _ in ucs:
        for x in as_list(u.get("risks")):
            if isinstance(x, str) and not any(x == r["title"] for r in risks):
                risks.append({"id": None, "title": x, "score": None, "mitigation": TC})
    if not risks and (ids is None or agents):
        risks = [{"id": None, "title": "Prompt injection through outside content (mitigated by FR-0010 and declared write actions)", "score": None, "mitigation": "FR-0010"},
                 {"id": None, "title": "Preview capabilities change or are withdrawn (each preview item carries a status and an owner)", "score": None, "mitigation": TC}]
    decisions, i = [], 1
    for d in doms:
        for cat, qs in (d.get("discovery") or {}).items() if isinstance(d.get("discovery"), dict) else []:
            for q in as_list(qs):
                if isinstance(q, dict) and str(q.get("status", "open")).lower() != "answered":
                    decisions.append({"id": f"D-{i:02d}", "question": f"{q.get('q')} ({d.get('name')} \u00b7 {cat})", "ref": q.get("id"), "owner": q.get("owner") or TC})
                    i += 1
    return {
        "derived": True, "basis": f"Frontier Company Blueprint v{M.get('version', '0.1')} ({M.get('status', 'hypothesis')})",
        "mvp_agents": [a.get("id") for a, _ in agents],
        "vision": (bp.get("mission") or {}).get("statement") if isinstance(bp.get("mission"), dict) else None,
        "commitments": [list(x) for x in COMMITMENTS],
        "maturity": [["Frontier phase (Work Trend Index)", f"Phase {F.get('current_phase', 1)}", f"Phase {F.get('target_phase', 3)}"],
                     ["Process automation level", f"Level {F.get('automation_current', 2)}", f"Level {F.get('automation_target', 3)}"]],
        "scope": [{"agent": a.get("id"), "name": a.get("name"), "journey": d.get("id"), "journey_name": d.get("name"),
                   "autonomy": a.get("autonomy"), "horizon": a.get("horizon"), "proves": a.get("proves") or TC,
                   "capability": a.get("capability") or TC} for a, d in agents],
        "use_cases": [{"id": u.get("id"), "name": u.get("name"), "journey": d.get("id"), "mvp": bool(u.get("mvp"))} for u, d in ucs],
        "problems": problems, "personas": personas, "platform": platform, "agents": per_agent,
        "nfr": [{"id": f"NFR-{k + 1:04d}", "category": c, "text": t} for k, (c, t) in enumerate(NFR)],
        "acceptance": acs, "kpis": kpis,
        "roles": [[a.get("name"), a.get("owner") or TC, "Agent boss: owns mandate, instructions and KPIs"] for a, _ in agents] + [list(r) for r in ROLES],
        "dependencies": list(dict.fromkeys(deps)), "risks": risks, "decisions": decisions,
        "definition_of_ready": list(DOR), "release_plan_default": [list(r) for r in RELEASE_PLAN],
    }


def _num(v, default):
    if isinstance(v, bool):
        return default
    try:
        x = Decimal(str(v))
        return int(x) if x.is_finite() and 1 <= x <= 5 and x == x.to_integral_value() else default
    except (InvalidOperation, TypeError, ValueError):
        return default


def fill_prd(bp: dict, rep=None) -> dict:
    """Keep the authored PRD fields, recompute the derived ones. Returns the block written to bp["prd"]."""
    old = bp.get("prd") if isinstance(bp.get("prd"), dict) else {}
    if rep is not None and bp.get("prd") is not None and not isinstance(bp.get("prd"), dict):
        rep.warn("prd must be an object; its content is derived from the blueprint")
    kept = {k: old[k] for k in AUTHORED if k in old}
    model = derive(bp)
    model.update(kept)
    model.setdefault("status", "hypothesis")
    if rep is not None:
        if not model["mvp_agents"]:
            rep.warn("prd: no agent is flagged mvp, so the PRD page lists the platform requirements only")
        st = str(model.get("status", "")).lower()
        if st not in ("hypothesis", "draft", "agreed", "adjusted", "rejected"):
            rep.warn(f"prd.status {model.get('status')!r} should be hypothesis, draft, agreed, adjusted or rejected")
    bp["prd"] = model
    return model
