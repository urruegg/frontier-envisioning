# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Normalise authored, canon and derived blueprint risks. Standard library only."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from decimal import Decimal, InvalidOperation

CATEGORIES = {
    "value": "Business value", "adoption": "Adoption and change", "data": "Data and integration",
    "security": "Security and compliance", "rai": "Responsible AI", "technology": "Technology and platform",
    "cost": "Cost", "delivery": "Delivery and readiness", "people": "People and organisation",
}
STATUSES = ("open", "mitigating", "accepted", "closed")
CAT_RULES = [
    ("security", r"secur|privacy|gdpr|revfadp|works?[- ]council|legal|complian|dpo|ciso|data protection|approval for"),
    ("cost", r"credit|cost|licen[cs]|budget|capacity pack|spend"),
    ("rai", r"bias|fair|responsible|transparen|hallucinat|decision about a person"),
    ("data", r"\bapi\b|access|integrat|interface|sandbox|test data|data quality|master data|matrix|catalog"),
    ("technology", r"quality|speech|accuracy|model|noisy|ocr|latency|preview|availability"),
    ("adoption", r"adoption|users?\b|technician|employee|change|trust|champion|habit"),
    ("people", r"owner|sponsor|skills|team|staff|role"),
    ("delivery", r"timeline|delay|depend|readiness|environment|blocked|late"),
]


def as_list(x):
    return x if isinstance(x, list) else ([] if x in (None, "") else [x])


def classify(text: str) -> str:
    for key, pat in CAT_RULES:
        if re.search(pat, str(text or ""), re.I):
            return key
    return "delivery"


def rating(v, default=3):
    """Accept only finite integer values 1-5 (numeric strings remain compatible)."""
    if isinstance(v, bool):
        return default
    try:
        x = Decimal(str(v))
    except (InvalidOperation, TypeError, ValueError):
        return default
    return int(x) if x.is_finite() and 1 <= x <= 5 and x == x.to_integral_value() else default


def _rated(obj, field, rep, who, default=3):
    if field not in obj:
        return default
    value = rating(obj[field], 0)
    if value:
        return value
    if rep is not None:
        rep.warn(f"{who} {field} {obj[field]!r} should be 1-5; 3 is used")
    return 3


def level(score: float) -> str:
    return "high" if score >= 15 else ("medium" if score >= 8 else "low")


def _text(x) -> str:
    return (x.get("text") or x.get("title") or "") if isinstance(x, dict) else str(x or "")


def _source_key(origin, ref, title):
    """Content binding, independent of list position and mutable ratings/verdicts."""
    data = json.dumps([origin, ref, str(title).strip()], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def derive_risks(bp: dict, rep=None) -> list:
    """Use-case risk points and blocked IT readiness items, in source order."""
    out, names = [], {}
    for d in as_list(bp.get("domains")):
        if not isinstance(d, dict):
            continue
        for a in ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + [x for x in as_list(d.get("agents")) if isinstance(x, dict)]:
            for k in ("name", "id"):
                if a.get(k):
                    names[str(a[k]).lower()] = a.get("id")
    ucs = []
    domain_private = {d.get("id"): d.get("internal") is True for d in as_list(bp.get("domains")) if isinstance(d, dict)}
    for d in as_list(bp.get("domains")):
        if isinstance(d, dict):
            ucs += [(u, d.get("id"), d.get("internal") is True) for u in as_list(d.get("use_cases")) if isinstance(u, dict)]
    ucs += [(u, u.get("domain"), domain_private.get(u.get("domain"), False)) for u in as_list(bp.get("use_cases")) if isinstance(u, dict)]
    for u, did, private in ucs:
        pts = [p for p in (as_list(u.get("risk_points")) or as_list(u.get("risks"))) if _text(p).strip()]
        safeguards = "; ".join(str(s) for s in as_list(u.get("safeguards")) if s)
        for i, p in enumerate(pts, start=1):
            text = _text(p).strip()
            q = p if isinstance(p, dict) else {}
            out.append({"id": f"R-{u.get('id')}-{i}", "title": text, "category": q.get("category") if q.get("category") in CATEGORIES else classify(text),
                        "likelihood": _rated(q, "likelihood", rep, f"risk R-{u.get('id')}-{i}"),
                        "impact": _rated(q, "impact", rep, f"risk R-{u.get('id')}-{i}", 4 if u.get("mvp") else 3),
                        "owner": q.get("owner") or u.get("owner") or "",
                        "mitigation": q.get("mitigation") or safeguards, "status": "open", "journeys": [did] if did else [],
                        "use_cases": [u.get("id")], "agents": [names[str(n).lower()] for n in as_list(u.get("agents")) if str(n).lower() in names],
                        "src": as_list(q.get("src", u.get("src"))),
                        "content_src": list(as_list(q.get("src", u.get("src")))),
                        "internal": private or q.get("internal") is True or u.get("internal") is True,
                        "origin": "use case", "derived": True,
                        "source_key": _source_key("use case", u.get("id"), text)})
    rd = bp.get("it_readiness") if isinstance(bp.get("it_readiness"), dict) else {}
    for g in as_list(rd.get("groups")):
        for it in as_list((g or {}).get("items")) if isinstance(g, dict) else []:
            if isinstance(it, dict) and str(it.get("status", "")).lower() == "blocked":
                what = it.get("item") or it.get("name") or it.get("text") or it.get("id")
                out.append({"id": f"R-{it.get('id')}", "title": f"Blocked IT readiness item: {what}", "category": "delivery",
                            "likelihood": 4, "impact": 3, "owner": it.get("owner") or "", "mitigation": it.get("note") or it.get("why") or "",
                            "status": "open", "journeys": [], "use_cases": [], "agents": [], "src": as_list(it.get("src")),
                            "content_src": list(as_list(it.get("src"))),
                            "internal": it.get("internal") is True or g.get("internal") is True or rd.get("internal") is True,
                            "origin": "IT readiness", "derived": True, "ref": it.get("id"),
                            "source_key": _source_key("IT readiness", it.get("id"), f"Blocked IT readiness item: {what}")})
    return out


def _unique_id(base, key, used):
    candidate, n = f"{base}-{key[:10]}", 2
    while candidate in used:
        candidate = f"{base}-{key[:10]}-{n}"
        n += 1
    return candidate


def _bind_sources(reg, items, derived, rep):
    """Persist first-build legacy IDs, never reassigning an ID after a source edit.

    The normalised JSON is the continuing workshop record. source_ids retains
    tombstones as well as current bindings; source_key travels with a workshop
    risk, so edits/reorder cannot change what its verdict was about.
    """
    bindings = dict(reg.get("source_ids") or {})
    for r in as_list(reg.get("items")):
        if not isinstance(r, dict):
            continue
        # Migrate received normalised records using their old source and title,
        # never the possibly edited current point at the same list position.
        if not r.get("source_key"):
            refs = as_list(r.get("use_cases"))
            if r.get("origin") == "use case" and len(refs) == 1:
                r["source_key"] = _source_key("use case", refs[0], r.get("title"))
            elif r.get("origin") == "IT readiness" and r.get("ref"):
                r["source_key"] = _source_key("IT readiness", r["ref"], r.get("title"))
        if r.get("source_key") and r.get("id"):
            bindings.setdefault(r["source_key"], r["id"])
    reserved = set(bindings.values()) | {r["id"] for r in items}
    sources = {r["source_key"]: r for r in derived}
    current = set(sources)
    for r in items:
        source = sources.get(r.get("source_key"))
        if source is not None:
            # Recover visibility for promoted records predating content_src.
            # A verdict is not permission to publish the underlying content.
            r.setdefault("content_src", list(source["content_src"]))
            if source.get("internal") is True:
                r["internal"] = True
        if r.get("source_key") and r["source_key"] not in current and rep is not None:
            rep.warn(f"risk {r['id']}: source changed or removed; workshop content retained separately")
    for r in derived:
        key = r["source_key"]
        if key not in bindings:
            candidate = r["id"]
            if candidate in reserved:
                candidate = _unique_id(candidate, key, reserved)
            bindings[key] = candidate
            reserved.add(candidate)
        r["id"] = bindings[key]
    reg["source_ids"] = dict(sorted(bindings.items()))


def fill_risks(bp: dict, rep=None) -> dict:
    """Keep authored fields and recompute derived risks, scores and levels."""
    reg = bp.get("risks")
    if isinstance(reg, list):
        reg = {"items": reg}
    elif not isinstance(reg, dict):
        if reg is not None and rep is not None:
            rep.warn("risks must be an object with items (or a list); derived risks only")
        reg = {}
    items = [x for x in as_list(reg.get("items")) if isinstance(x, dict) and not x.get("derived")]
    doms = {d.get("id") for d in as_list(bp.get("domains")) if isinstance(d, dict)}
    agents, ucs = set(), set()
    for d in as_list(bp.get("domains")):
        if isinstance(d, dict):
            for a in ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + as_list(d.get("agents")):
                if isinstance(a, dict) and a.get("id"):
                    agents.add(a["id"])
            ucs |= {u.get("id") for u in as_list(d.get("use_cases")) if isinstance(u, dict)}
    ucs |= {u.get("id") for u in as_list(bp.get("use_cases")) if isinstance(u, dict)}
    used, n = {x.get("id") for x in items if x.get("id")}, 1
    duplicates = {rid for rid, count in Counter(x.get("id") for x in items if x.get("id")).items() if count > 1}
    for rid in sorted(duplicates):
        if rep is not None:
            rep.warn(f"duplicate authored risk id {rid!r}; all colliding risks receive content-bound IDs")
    for r in items:
        if r.get("id") in duplicates:
            key = hashlib.sha256(json.dumps(r, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
            r["id"] = _unique_id(r["id"], key, used)
            used.add(r["id"])
        if not r.get("id"):
            while f"R-{n:02d}" in used:
                n += 1
            r["id"] = f"R-{n:02d}"
            used.add(r["id"])
        who = f"risk {r['id']}"
        if not str(r.get("title") or "").strip():
            if rep is not None:
                rep.warn(f"{who} has no title")
            r["title"] = r.get("description") or "To be described"
        for k in ("likelihood", "impact"):
            r[k] = _rated(r, k, rep, who)
        cat = str(r.get("category") or "").lower()
        if cat not in CATEGORIES:
            if cat and rep is not None:
                rep.warn(f"{who} category {r.get('category')!r} unknown (use {', '.join(CATEGORIES)}); classified from its title")
            r["category"] = classify(r.get("title"))
        st = str(r.get("status") or "open").lower()
        if st not in STATUSES:
            if rep is not None:
                rep.warn(f"{who} status {r.get('status')!r} should be one of {', '.join(STATUSES)}")
            st = "open"
        r["status"] = st
        for key, pool, label in (("journeys", doms, "journey"), ("use_cases", ucs, "use case"), ("agents", agents, "agent")):
            for ref in as_list(r.get(key)):
                if ref not in pool and rep is not None:
                    rep.warn(f"{who} names an unknown {label} {ref!r}")
        r.setdefault("origin", "canon" if r.get("canon") else "workshop" if r.get("workshop_notes") else "author")
        r["score"] = r["likelihood"] * r["impact"]
        r["level"] = level(r["score"])
    derived = derive_risks(bp, rep)
    _bind_sources(reg, items, derived, rep)
    titles = {str(x.get("title", "")).strip().lower() for x in items if not x.get("source_key")}
    owned = {x.get("source_key") for x in items if x.get("source_key")}
    for r in derived:
        if r["source_key"] in owned or r["id"] in used or r["title"].strip().lower() in titles:
            continue
        r["score"] = r["likelihood"] * r["impact"]
        r["level"] = level(r["score"])
        items.append(r)
        used.add(r["id"])
    items.sort(key=lambda x: (-x["score"], str(x.get("id"))))
    reg["items"] = items
    bp["risks"] = reg
    return reg
