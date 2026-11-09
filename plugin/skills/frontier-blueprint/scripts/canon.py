# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Innovation Hub canon blocks for a Frontier Company Blueprint (shared by seed_blueprint.py and build_blueprint.py).

add_canon(bp, defaults) adds what is missing and never overwrites what the blueprint already has:
  * the Agent Factory journey (a domain with kind "factory") and the factory block (lifecycle, steps, pyramid, controls, roles)
  * architecture.landing_zone (CAF design areas, WAF, CAF and Responsible AI principles) with one zone per business journey
  * canon architecture decisions (ADR-F01 ...) that are not in the blueprint yet
  * it_readiness (preparation items, readiness checks, workstation checks, questions, decisions)
Returns the list of what was added.
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


def add_canon(bp: dict, dfl: dict, parts=("factory", "landing_zone", "adrs", "it_readiness")) -> list:
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
    return added


def load_defaults(path) -> dict:
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)
