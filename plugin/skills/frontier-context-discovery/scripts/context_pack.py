#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Validate and render the customer context pack gathered with Work IQ and transcripts.

Usage:
  python context_pack.py validate customer-context.json
  python context_pack.py render   customer-context.json --out "Customer - evidence log.md" [--audience customer]

The context pack (schema "frontier-context/1.0") is the single source the
blueprint is seeded from. See references/context-pack.md for every field.

validate  checks ids, citations (every fact cites a known source), visibility
          values, confidence values, and reports coverage gaps the discovery
          should still close (journeys without pains or KPIs, no systems, no
          stakeholders, no constraints). Exit 1 on errors.
render    writes a readable evidence log (markdown): sources, facts by category
          with citations, stakeholders, journeys, open questions and gaps.
          --audience customer leaves out internal sources and internal facts.

Standard library only; no network access.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TYPES = {"transcript", "meeting", "email", "chat", "file", "web", "crm", "note", "workshop"}
CATS = ["strategy", "pain", "metric", "kpi", "system", "data", "governance", "constraint", "stakeholder",
        "idea", "decision", "action", "risk", "other"]
CONF = {"high", "medium", "low"}
LABEL = {"transcript": "Transcript", "meeting": "Meeting", "email": "Email", "chat": "Teams chat", "file": "Document",
         "web": "Public web", "crm": "CRM record", "note": "Note", "workshop": "Workshop"}


def as_list(x):
    return x if isinstance(x, list) else ([] if x in (None, "") else [x])


def cites(item) -> list[str]:
    out = []
    for e in as_list(item.get("evidence")):
        if isinstance(e, dict) and e.get("source"):
            out.append(str(e["source"]))
        elif isinstance(e, str):
            out.append(e)
    out += [str(s) for s in as_list(item.get("src"))]
    return out


def load(path: str) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("the context pack must be a JSON object")
    return data


def validate(ctx: dict) -> dict:
    errors, warnings, gaps = [], [], []
    if not (ctx.get("customer") or {}).get("name"):
        errors.append("customer.name is required")
    sources = as_list(ctx.get("sources"))
    sids = set()
    for i, s in enumerate(sources):
        sid = s.get("id")
        if not sid:
            errors.append(f"sources[{i}] has no id")
            continue
        if sid in sids:
            errors.append(f"duplicate source id {sid}")
        sids.add(sid)
        if s.get("type") not in TYPES:
            warnings.append(f"source {sid} type {s.get('type')!r} is not one of {sorted(TYPES)}")
        if str(s.get("visibility", "")).lower() not in ("internal", "customer"):
            errors.append(f"source {sid} needs visibility 'internal' or 'customer'")
        if not s.get("title"):
            warnings.append(f"source {sid} has no title")
    fids = set()
    facts = as_list(ctx.get("facts"))
    for i, f in enumerate(facts):
        fid = f.get("id") or f"F{i + 1:03d}"
        f["id"] = fid
        if fid in fids:
            errors.append(f"duplicate fact id {fid}")
        fids.add(fid)
        if f.get("category") not in CATS:
            warnings.append(f"fact {fid} category {f.get('category')!r} is not one of {CATS}")
        c = cites(f)
        if not c:
            errors.append(f"fact {fid} cites no source; every fact needs evidence (or move it to open_questions)")
        for sid in c:
            if sid not in sids:
                errors.append(f"fact {fid} cites unknown source {sid}")
        if f.get("confidence") and str(f["confidence"]).lower() not in CONF:
            warnings.append(f"fact {fid} confidence should be high, medium or low")
        if not f.get("statement"):
            errors.append(f"fact {fid} has no statement")
    for key in ("stakeholders", "journeys", "systems", "kpis", "constraints", "ideas", "decisions", "actions"):
        for i, item in enumerate(as_list(ctx.get(key))):
            for sid in cites(item) if isinstance(item, dict) else []:
                if sid not in sids:
                    warnings.append(f"{key}[{i}] cites unknown source {sid}")
    journeys = as_list(ctx.get("journeys"))
    if not journeys:
        gaps.append("No journeys identified yet: ask which end-to-end processes matter most")
    for j in journeys:
        name = j.get("name", "?")
        jf = [f for f in facts if str(f.get("journey", "")).lower() == str(name).lower()]
        if not any(f.get("category") == "pain" for f in jf) and not as_list(j.get("pains")):
            gaps.append(f"Journey '{name}': no evidenced pain points")
        if not any(f.get("category") in ("metric", "kpi") for f in jf) and not [k for k in as_list(ctx.get("kpis")) if str(k.get("journey", "")).lower() == str(name).lower()]:
            gaps.append(f"Journey '{name}': no baseline numbers or KPIs")
    if not as_list(ctx.get("systems")) and not any(f.get("category") == "system" for f in facts):
        gaps.append("No systems of record identified")
    if not as_list(ctx.get("stakeholders")):
        gaps.append("No stakeholders identified (sponsor, process owners, IT)")
    if not as_list(ctx.get("constraints")) and not any(f.get("category") in ("governance", "constraint") for f in facts):
        gaps.append("No governance constraints captured (data protection, residency, works council, NDA)")
    if not any(s.get("type") in ("transcript", "workshop") for s in sources):
        gaps.append("No transcript or workshop source: the hypothesis rests on secondary material only")
    internal = sum(1 for s in sources if str(s.get("visibility", "")).lower() == "internal")
    stats = {"sources": len(sources), "internal_sources": internal, "facts": len(facts),
             "facts_by_category": {c: sum(1 for f in facts if f.get("category") == c) for c in CATS if any(f.get("category") == c for f in facts)},
             "journeys": len(journeys), "stakeholders": len(as_list(ctx.get("stakeholders"))),
             "open_questions": len(as_list(ctx.get("open_questions")))}
    return {"status": "error" if errors else "ok", "errors": errors, "warnings": warnings, "gaps": gaps, "stats": stats}


def md_escape(t) -> str:
    return str(t if t is not None else "").replace("|", "/").replace("\n", " ").strip()


def render(ctx: dict, audience: str) -> str:
    sources = as_list(ctx.get("sources"))
    if audience == "customer":
        hidden = {s.get("id") for s in sources if str(s.get("visibility", "")).lower() == "internal"}
        sources = [s for s in sources if s.get("id") not in hidden]
    else:
        hidden = set()
    cust = ctx.get("customer") or {}
    eng = ctx.get("engagement") or {}
    L = [f"# {cust.get('name', 'Customer')} \u2014 envisioning evidence log", ""]
    L.append(f"Engagement: {eng.get('title', 'Frontier solution envisioning')}  ")
    if eng.get("workshop_date"):
        L.append(f"Workshop: {eng['workshop_date']}  ")
    L.append(f"Audience: {'customer-shareable' if audience == 'customer' else 'Microsoft internal'}")
    L += ["", "## Sources", "", "| ID | Type | Title | Date | Visibility |", "|---|---|---|---|---|"]
    for s in sources:
        L.append(f"| {md_escape(s.get('id'))} | {LABEL.get(s.get('type'), md_escape(s.get('type')))} | {md_escape(s.get('title'))} | {md_escape(s.get('date'))} | {md_escape(s.get('visibility'))} |")
    facts = [f for f in as_list(ctx.get("facts"))
             if not (audience == "customer" and (str(f.get("visibility", "")).lower() == "internal" or set(cites(f)) & hidden))]
    L += ["", "## Facts by category", ""]
    for c in CATS:
        items = [f for f in facts if f.get("category") == c]
        if not items:
            continue
        L += [f"### {c.capitalize()}", ""]
        for f in items:
            refs = []
            for e in as_list(f.get("evidence")):
                if isinstance(e, dict) and e.get("source") not in hidden:
                    refs.append(e["source"] + (f" @ {e['at']}" if e.get("at") else ""))
            refs += [s for s in as_list(f.get("src")) if s not in hidden]
            conf = f" _(confidence: {f['confidence']})_" if f.get("confidence") else ""
            jn = f" [{f['journey']}]" if f.get("journey") else ""
            L.append(f"- **{f.get('id')}**{jn} {md_escape(f.get('statement'))} \u2014 {', '.join(refs) or 'no source'}{conf}")
            for e in as_list(f.get("evidence")):
                if isinstance(e, dict) and e.get("quote") and e.get("source") not in hidden:
                    L.append(f"  > {md_escape(e['quote'])[:240]}")
        L.append("")
    st = as_list(ctx.get("stakeholders"))
    if st:
        L += ["## Stakeholders", "", "| Name / role | Organisation | Stance | Interests |", "|---|---|---|---|"]
        for s in st:
            if audience == "customer" and s.get("internal"):
                continue
            L.append(f"| {md_escape(s.get('name') or '')} {('(' + md_escape(s.get('role')) + ')') if s.get('role') else ''} | {md_escape(s.get('org'))} | {md_escape(s.get('stance'))} | {md_escape(s.get('interests'))} |")
        L.append("")
    js = as_list(ctx.get("journeys"))
    if js:
        L += ["## Journeys in scope", ""]
        for j in js:
            L.append(f"- **{md_escape(j.get('name'))}** \u2014 {md_escape(j.get('why'))}")
        L.append("")
    oq = as_list(ctx.get("open_questions"))
    if oq:
        L += ["## Open questions for the workshop", ""]
        for q in oq:
            L.append(f"- [{md_escape(q.get('journey') or 'All')} \u00b7 {md_escape(q.get('category') or 'General')}] {md_escape(q.get('q'))}")
        L.append("")
    v = validate(json.loads(json.dumps(ctx)))
    if v["gaps"]:
        L += ["## Coverage gaps", ""] + [f"- {g}" for g in v["gaps"]] + [""]
    L.append("_Facts are summarised from the cited sources; quotes are short excerpts. Verify before external use._")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("context")
    r = sub.add_parser("render")
    r.add_argument("context")
    r.add_argument("--out", required=True)
    r.add_argument("--audience", choices=("internal", "customer"), default="internal")
    a = ap.parse_args(argv)
    try:
        ctx = load(a.context)
    except (OSError, ValueError) as e:
        print(f"ERROR: cannot read {a.context}: {e}", file=sys.stderr)
        return 2
    if a.cmd == "validate":
        res = validate(ctx)
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 1 if res["errors"] else 0
    Path(a.out).write_text(render(ctx, a.audience), encoding="utf-8")
    print(json.dumps({"out": a.out, "audience": a.audience}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
