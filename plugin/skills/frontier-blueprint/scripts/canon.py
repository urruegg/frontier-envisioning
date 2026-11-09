# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Innovation Hub canon blocks for a Frontier Company Blueprint (shared by seed_blueprint.py and build_blueprint.py).

add_canon(bp, defaults) adds what is missing and never overwrites what the blueprint already has:
  * the Agent Factory journey (a domain with kind "factory") and the factory block (lifecycle, steps, pyramid, controls, roles)
  * architecture.landing_zone (CAF design areas, WAF, CAF and Responsible AI principles) with one zone per business journey
  * canon architecture decisions (ADR-F01 ...) that are not in the blueprint yet
  * it_readiness (preparation items, readiness checks, workstation checks, questions, decisions)
  * feedback_loop: Microsoft's digital feedback loop for the Overview (engage customers, empower employees,
    optimize operations, transform products around Microsoft IQ), with each business journey mapped to one area
    and the signals, actions and outcomes taken from the journey's systems, agents and KPIs
Returns the list of what was added.

fill_feedback_loop(bp, defaults) completes an existing loop: a quadrant linked to journeys gets the signals, actions,
outcomes and use cases it does not have yet from those journeys (used by build_blueprint.py on every build).
"""
from __future__ import annotations

import copy
import re
import json


def _business(domains):
    return [d for d in domains if isinstance(d, dict) and d.get("kind") != "factory"]


def factory_domain(bp: dict):
    for d in bp.get("domains") or []:
        if isinstance(d, dict) and d.get("kind") == "factory":
            return d
    return None


def _norm(t) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(t or "").lower()).strip()


def add_canon(bp: dict, dfl: dict, parts=("factory", "landing_zone", "adrs", "it_readiness", "feedback_loop")) -> list:
    added = []
    domains = bp.setdefault("domains", [])
    if "factory" in parts and dfl.get("factory") and not factory_domain(bp):
        canon = copy.deepcopy(dfl["factory"])
        jd = canon.pop("journey")
        used = {d.get("id") for d in domains if isinstance(d, dict)}
        n = len(domains) + 1
        while f"D{n}" in used:
            n += 1
        fid = f"D{n}"
        jd["id"] = fid
        jd["orchestrator"]["id"] = f"{fid}-LEAD"
        for i, a in enumerate(jd.get("agents", [])):
            a["id"] = f"{fid}-A{i + 1:02d}"
            a.setdefault("lifecycle", "Planned")
            a.setdefault("status", "hypothesis")
        jd.setdefault("use_cases", [])
        domains.append(jd)
        canon["journey"] = fid
        canon["roles"] = [{"id": f"{fid}-{r[0]}", "decides": r[1]} for r in canon.get("roles", [])]
        if not isinstance(bp.get("factory"), dict):
            bp["factory"] = canon
        added.append(f"factory journey {fid}")
    arch = bp.setdefault("architecture", {})
    if "landing_zone" in parts and dfl.get("landing_zone") and not isinstance(arch.get("landing_zone"), dict):
        lz = copy.deepcopy(dfl["landing_zone"])
        mvp_domains = {u.get("domain") for u in bp.get("use_cases") or [] if isinstance(u, dict) and u.get("mvp")}
        for d in _business(domains):
            for u in d.get("use_cases") or []:
                if isinstance(u, dict) and u.get("mvp"):
                    mvp_domains.add(d.get("id"))
        lz["lz"] = [{"id": f"F{i + 1}", "domain": d.get("id"), "stages": {"DEV": "next" if d.get("id") in mvp_domains else "later", "TEST": "later", "PROD": "later"},
                     "classes": ["public", "internal"], "mvp": d.get("id") in mvp_domains}
                    for i, d in enumerate(_business(domains))]
        arch["landing_zone"] = lz
        added.append("landing zone")
    if "adrs" in parts and dfl.get("adr_canon"):
        have = {x.get("id") for x in arch.get("decisions") or [] if isinstance(x, dict)}
        titles = {_norm(x.get("title")) for x in arch.get("decisions") or [] if isinstance(x, dict)}
        # a canon decision is skipped when the blueprint already has it by id or by title (customer wording wins)
        new = [copy.deepcopy(x) for x in dfl["adr_canon"] if x.get("id") not in have and _norm(x.get("title")) not in titles]
        if new:
            arch["decisions"] = list(arch.get("decisions") or []) + new
            added.append(f"{len(new)} canon decisions")
    if "it_readiness" in parts and dfl.get("it_readiness") and not isinstance(bp.get("it_readiness"), dict):
        bp["it_readiness"] = copy.deepcopy(dfl["it_readiness"])
        added.append("IT readiness")
    if "feedback_loop" in parts and dfl.get("feedback_loop") and not isinstance(bp.get("feedback_loop"), dict):
        bp["feedback_loop"] = feedback_loop(bp, dfl)
        added.append("digital feedback loop")
    return added


# ---------------- digital feedback loop (Overview) ----------------
PILLARS = ("engage_customers", "optimize_operations", "empower_employees", "transform_products")


def _rules(rules) -> list:
    return [r for r in rules or [] if isinstance(r, (list, tuple)) and len(r) == 2]


def _match(text, rules, default=None):
    for pat, key in rules:
        try:
            if re.search(pat, str(text or ""), re.I):
                return key
        except re.error:
            continue
    return default


def _jtext(d: dict) -> str:
    return " ".join(str(d.get(k) or "") for k in ("name", "short_name", "journey_name", "journey_tagline", "function"))


def _derive(q: dict, doms: list, iq_rules: list, approval) -> None:
    """Fill what the quadrant does not have yet from its journeys: systems -> signals (with the Microsoft IQ layer),
    lead or MVP agents -> actions, KPIs -> outcomes, MVP use cases -> use_cases. Never overwrites."""
    if not doms:
        return
    if not q.get("signals"):
        sig = []
        for d in doms:
            for name in [x for x in d.get("systems") or [] if isinstance(x, str) and x.strip()][:4]:
                sig.append({"text": f"{name} ({d.get('short_name') or d.get('name')})", "iq": [_match(name, iq_rules, "fabric")]})
        if sig:
            q["signals"] = sig[:6]
    if not q.get("actions"):
        act = []
        for d in doms:
            team = [a for a in [d.get("orchestrator")] + list(d.get("agents") or []) if isinstance(a, dict) and (a.get("name") or a.get("id"))]
            pick = [a for a in team if a.get("mvp")] or team[1:2] or team[:1]
            seam = d.get("approval_seam") if isinstance(d.get("approval_seam"), str) else approval
            for a in pick[:2]:
                act.append({k: v for k, v in {"text": str(a.get("capability") or a.get("mission") or a.get("name")),
                                               "agents": [a.get("id") or a.get("name")], "approval": seam}.items() if v})
        if act:
            q["actions"] = act[:4]
    if not q.get("outcomes"):
        out = []
        for d in doms:
            for k in [x for x in d.get("kpis") or [] if isinstance(x, dict) and x.get("kpi")][:2]:
                out.append({k2: v for k2, v in {"text": str(k.get("definition") or k["kpi"]), "kpi": k["kpi"], "journey": d.get("id"),
                                                 "src": k.get("src")}.items() if v})
        if out:
            q["outcomes"] = out[:4]
    if not q.get("use_cases"):
        ucs = [u.get("id") for d in doms for u in d.get("use_cases") or [] if isinstance(u, dict) and u.get("id") and u.get("mvp")]
        if ucs:
            q["use_cases"] = ucs[:4]


def feedback_loop(bp: dict, dfl: dict) -> dict:
    """A customer-specific starting point: the canon loop with every business journey mapped to one of the four areas."""
    fl = copy.deepcopy(dfl["feedback_loop"])
    prules, irules = _rules(fl.pop("pillar_rules", None)), _rules(fl.pop("iq_rules", None))
    quads = {q.get("pillar"): q for q in fl.get("quadrants") or [] if isinstance(q, dict) and q.get("pillar") in PILLARS}
    for d in _business(bp.get("domains") or []):
        if not d.get("id"):
            continue
        q = quads.get(_match(_jtext(d), prules, "optimize_operations"))
        if q is not None:
            q.setdefault("journeys", []).append(d["id"])
    approval = bp.get("approval_seam") if isinstance(bp.get("approval_seam"), str) else None
    for q in quads.values():
        doms = [d for d in _business(bp.get("domains") or []) if d.get("id") in (q.get("journeys") or [])]
        if doms:
            # journey-specific content replaces the generic lists
            for k in ("signals", "actions", "outcomes"):
                q.pop(k, None)
            _derive(q, doms, irules, approval)
            for k, v in (("signals", "signal"), ("actions", "action"), ("outcomes", "outcome")):
                if not q.get(k):
                    q[k] = copy.deepcopy(next((x.get(k) for x in dfl["feedback_loop"].get("quadrants") or [] if x.get("pillar") == q.get("pillar")), []))
                elif k != "signals":
                    q.pop(v, None)  # the card shows the first item instead of the generic line
    fl["derived"] = True
    return fl


def fill_feedback_loop(bp: dict, dfl: dict) -> int:
    """Complete an existing loop from the journeys it links (build time). Returns the number of quadrants completed."""
    fl = bp.get("feedback_loop")
    if not isinstance(fl, dict) or not isinstance(dfl.get("feedback_loop"), dict):
        return 0
    irules = _rules(dfl["feedback_loop"].get("iq_rules"))
    approval = bp.get("approval_seam") if isinstance(bp.get("approval_seam"), str) else None
    by_id = {d.get("id"): d for d in _business(bp.get("domains") or []) if d.get("id")}
    n = 0
    for q in fl.get("quadrants") or []:
        if not isinstance(q, dict):
            continue
        doms = [by_id[j] for j in q.get("journeys") or [] if j in by_id]
        before = {k: bool(q.get(k)) for k in ("signals", "actions", "outcomes", "use_cases")}
        _derive(q, doms, irules, approval)
        if any(bool(q.get(k)) != v for k, v in before.items()):
            n += 1
    return n


def load_defaults(path) -> dict:
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)
