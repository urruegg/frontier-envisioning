#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Validate a Frontier Company Blueprint JSON and render it into the HTML template.

Usage:
  python build_blueprint.py --data blueprint.json --out "Customer Frontier Blueprint.html"
         [--template ../templates/frontier-blueprint-template.html]
         [--audience internal|customer] [--save-normalized blueprint.normalized.json]
         [--strict] [--report build-report.json]

What it does:
  1. Loads the blueprint JSON and normalises it (stable ids for agents, use cases,
     discovery questions and evidence, so workshop feedback can be merged later).
  2. Validates references: stage -> agent, use case -> domain/agents, src -> evidence,
     domain -> leader, MVP option -> domain. Problems are ERROR or WARN.
  3. --audience customer removes Microsoft-internal evidence (visibility "internal"),
     every item flagged "internal": true, every key named "internal_notes", and
     refuses to build if any meta.internal_terms string is still present.
  4. Injects the JSON into the template (HTML-safe escaping) and writes the file.

Standard library only. No network access, no code execution from the data.
Exit code 0 = built, 1 = validation errors (nothing written), 2 = usage/IO error.
"""
from __future__ import annotations

import argparse
import copy
import datetime as _dt
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from canon import PILLARS, add_canon, fill_feedback_loop, load_defaults  # noqa: E402
from workflow import fill_workflows  # noqa: E402
from risks import fill_risks  # noqa: E402
from prd_model import AUTHORED as PRD_AUTHORED, fill_prd  # noqa: E402

PLACEHOLDER = '"__BLUEPRINT_DATA__"'
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
SLUG = re.compile(r"[^a-z0-9]+")
LOGO_OK = re.compile(r"^data:image/(png|jpeg|gif|webp);base64,[A-Za-z0-9+/=\s]+$")
ICON_OK = re.compile(r"^data:image/(svg\+xml|png);base64,[A-Za-z0-9+/=]+$")
URL = re.compile(r"https?://", re.I)
AUTONOMY_WORDS = ("assist", "approval", "approve", "guardrail", "autonom", "mandate", "budget", "semi")
STATUS_OK = {"hypothesis", "validated", "adjusted", "adjust", "rejected", "open", "partial", "answered"}
DECLARATIONS = ("write_envelope", "refusal_set", "escalation_path", "grounding_sources",
                "data_classification", "people_decisions", "measurement")
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "frontier-blueprint-template.html"
DEFAULTS = Path(__file__).resolve().parent.parent / "templates" / "blueprint-defaults.json"
ICONS = Path(__file__).resolve().parent.parent / "templates" / "product-icons.json"
PLUGIN_VERSION = "1.9.2"


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.removed: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def as_list(x):
    if x is None or x == "":
        return []
    return x if isinstance(x, list) else [x]


def src_ids(src) -> list[str]:
    if src is None or src == "":
        return []
    if isinstance(src, list):
        return [str(s).strip() for s in src if str(s).strip()]
    return [s for s in re.split(r"[,\s]+", str(src)) if s]


def walk(obj, fn, path="$"):
    """Call fn(container, key, value, path) for every dict entry, recursively."""
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            fn(obj, k, obj[k], f"{path}.{k}")
            if k in obj:
                walk(obj[k], fn, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, fn, f"{path}[{i}]")


def clean_agent_identity(idn: dict, who, rep: "Report") -> None:
    """Keeps only safe icon data URIs and colours in an agent's identity block (written by the identity kit)."""
    icons = idn.get("icons")
    if icons is not None:
        ok = {k: v for k, v in icons.items() if isinstance(v, str) and ICON_OK.match(v)} if isinstance(icons, dict) else {}
        if not isinstance(icons, dict) or len(ok) != len(icons):
            rep.warn(f"agent {who}: identity icons must be base64 SVG or PNG data URIs; invalid icons ignored")
        idn["icons"] = ok
    if "outline" in idn and not ICON_OK.match(str(idn["outline"])):
        rep.warn(f"agent {who}: identity outline icon must be a base64 SVG or PNG data URI; ignored")
        idn.pop("outline")
    if "colour" in idn and not HEX.match(str(idn["colour"])):
        idn.pop("colour")


def clean_identity_block(bp: dict, rep: "Report") -> None:
    """Checks the top-level identity block (Agent identity page) written by the identity kit's apply_identity.py."""
    b = bp.get("identity")
    if b is None:
        return
    if not isinstance(b, dict):
        rep.warn("identity must be an object; the Agent identity page uses the agents' identity only")
        bp.pop("identity")
        return
    for key in ("environments", "journeys", "po_areas", "decisions", "rules"):
        if key in b and not isinstance(b[key], list):
            rep.warn(f"identity.{key} must be a list; ignored")
            b.pop(key)
    for key, cols in (("environments", ("band", "label")), ("journeys", ("colour", "glyph"))):
        for item in b.get(key, []):
            for c in cols:
                if isinstance(item, dict) and c in item and not HEX.match(str(item[c])):
                    item.pop(c)
    rules = [r for r in b.get("rules", []) if isinstance(r, dict) and str(r.get("url", "https://")).startswith("https://")]
    if rules:
        b["rules"] = rules
    else:
        b.pop("rules", None)


def clean_value_finops(bp: dict, rep: "Report") -> None:
    """Checks the value case and FinOps blocks written by frontier-value-case and frontier-finops (apply_value.py, apply_finops.py)."""
    for key in ("value_case", "finops"):
        b = bp.get(key)
        if b is None:
            continue
        if not isinstance(b, dict):
            rep.warn(f"{key} must be an object; ignored")
            bp.pop(key)
            continue
        for lk in ("assumptions", "agents", "purchase_options", "credit_scenarios", "guardrails", "tags", "rates", "sources", "lessons", "discipline", "questions"):
            if lk in b and not isinstance(b[lk], list):
                rep.warn(f"{key}.{lk} must be a list; ignored")
                b.pop(lk)
        if "sources" in b:
            b["sources"] = [x for x in b["sources"] if isinstance(x, dict) and str(x.get("url", "https://")).startswith("https://")]
    for d in as_list(bp.get("domains")):
        for u in as_list(d.get("use_cases") if isinstance(d, dict) else None):
            if isinstance(u, dict) and "business_value" in u and not isinstance(u["business_value"], dict):
                u.pop("business_value")
    for u in as_list(bp.get("use_cases")):
        if isinstance(u, dict) and "business_value" in u and not isinstance(u["business_value"], dict):
            rep.warn(f"use case {u.get('id')}: business_value must be an object (written by apply_value.py); ignored")
            u.pop("business_value")


def embed_product_icons(bp: dict, rep: "Report", library: Path) -> int:
    """Embeds the Microsoft and GitHub product icons the blueprint uses (exact keys or the library's text rules)."""
    try:
        lib = json.loads(library.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        rep.warn(f"product icons not embedded: {e}")
        return 0
    icons, rules = lib.get("icons") or {}, [r for r in lib.get("rules") or [] if isinstance(r, list) and len(r) == 2]
    texts = []
    walk(bp, lambda c, k, v, p: texts.append(v) if isinstance(v, str) and not v.startswith("data:") else None)
    blob = "\n".join(texts)
    used = {t for t in texts if t in icons}
    for pat, key in rules:
        try:
            if key in icons and re.search(pat, blob, re.I):
                used.add(key)
        except re.error:
            rep.warn(f"product icon rule {pat!r} is not a valid pattern; ignored")
    have = bp.get("logos") if isinstance(bp.get("logos"), dict) else {}
    out = {k: dict(v) for k, v in have.items() if isinstance(v, dict) and ICON_OK.match(str(v.get("uri", "")))}
    for k in sorted(used):
        if k not in out:
            out[k] = {kk: vv for kk, vv in icons[k].items() if kk in ("name", "uri", "uri_white")}
    for k, v in list(out.items()):
        for kk in ("uri", "uri_white"):
            if kk in v and not ICON_OK.match(str(v[kk])):
                v.pop(kk)
        if "uri" not in v:
            out.pop(k)
    if out:
        bp["logos"] = out
        bp["logo_rules"] = [r for r in rules if r[1] in out]
        bp["logos_note"] = bp.get("logos_note") or lib.get("notice", "")
    return len(out)


def clean_canon_blocks(bp: dict, rep: "Report") -> None:
    """Light checks of the attendees, Agent Factory, landing zone and IT readiness blocks."""
    for key, lists in (("attendees", ("people",)), ("factory", ("lifecycle", "steps", "pyramid", "controls", "roles", "phases", "handover", "resources", "sources")),
                       ("it_readiness", ("groups", "checks", "workstation", "questions", "decisions", "environments", "timeline"))):
        b = bp.get(key)
        if b is None:
            continue
        if not isinstance(b, dict):
            rep.warn(f"{key} must be an object; ignored")
            bp.pop(key)
            continue
        for lk in lists:
            if lk in b and not isinstance(b[lk], list):
                rep.warn(f"{key}.{lk} must be a list; ignored")
                b.pop(lk)
    for lk in ("resources", "sources"):
        f = bp.get("factory") or {}
        if isinstance(f.get(lk), list):
            f[lk] = [x for x in f[lk] if isinstance(x, dict) and str(x.get("url", "https://")).startswith("https://")]
    lz = (bp.get("architecture") or {}).get("landing_zone")
    if lz is not None and not (isinstance(lz, dict) and isinstance(lz.get("areas", {}), dict)):
        rep.warn("architecture.landing_zone must be an object with areas; ignored")
        bp["architecture"].pop("landing_zone")
    elif isinstance(lz, dict) and isinstance(lz.get("sources"), list):
        lz["sources"] = [x for x in lz["sources"] if isinstance(x, dict) and str(x.get("url", "https://")).startswith("https://")]
    ids = [d.get("id") for d in as_list(bp.get("domains")) if isinstance(d, dict) and d.get("kind") == "factory"]
    if len(ids) > 1:
        rep.warn("more than one Agent Factory journey: " + ", ".join(map(str, ids)))
    for x in as_list((bp.get("architecture") or {}).get("decisions")):
        if isinstance(x, dict) and not x.get("id"):
            rep.warn(f"architecture decision without id: {str(x.get('title'))[:60]}")


OFFICIAL_IQ = ("microsoft iq", "work iq", "fabric iq", "foundry iq", "web iq")
IQ_IDS = {"work", "fabric", "foundry", "web"}
IQ_NAME = re.compile(r"\b([A-Z][A-Za-z]+) IQ\b")


def clean_feedback_loop(bp: dict, rep: "Report") -> None:
    """Checks the digital feedback loop (Overview): four areas, known journeys, and only official Microsoft IQ names."""
    fl = bp.get("feedback_loop")
    if fl is None:
        return
    if not isinstance(fl, dict):
        rep.warn("feedback_loop must be an object; ignored")
        bp.pop("feedback_loop")
        return
    fl.pop("pillar_rules", None)
    fl.pop("iq_rules", None)
    quads = fl.get("quadrants")
    if quads is not None and not isinstance(quads, list):
        rep.warn("feedback_loop.quadrants must be a list; ignored")
        quads = []
    dom_ids = {d.get("id") for d in as_list(bp.get("domains")) if isinstance(d, dict)}
    seen, keep = set(), []
    for q in quads or []:
        pillar = q.get("pillar") if isinstance(q, dict) else None
        if pillar not in PILLARS:
            rep.warn(f"feedback_loop: area {pillar!r} ignored; use {', '.join(PILLARS)}")
            continue
        if pillar in seen:
            rep.warn(f"feedback_loop: a second {pillar} area is ignored")
            continue
        seen.add(pillar)
        for lk in ("journeys", "signals", "actions", "outcomes", "use_cases", "iq"):
            if lk in q and not isinstance(q[lk], list):
                q[lk] = as_list(q[lk])
        for j in as_list(q.get("journeys")):
            if j not in dom_ids:
                rep.warn(f"feedback_loop {pillar}: unknown journey {j}")
        layers = list(as_list(q.get("iq"))) + [i for x in as_list(q.get("signals")) if isinstance(x, dict) for i in as_list(x.get("iq"))]
        bad = sorted({str(i) for i in layers if re.sub(r"[^a-z]", "", str(i).lower()).removesuffix("iq") not in IQ_IDS})
        if bad:
            rep.warn(f"feedback_loop {pillar}: unknown Microsoft IQ layer {', '.join(bad)} (use work, fabric, foundry or web)")
        keep.append(q)
    if quads is not None:
        fl["quadrants"] = keep
    if isinstance(fl.get("sources"), list):
        fl["sources"] = [x for x in fl["sources"] if isinstance(x, dict) and str(x.get("url", "")).startswith("https://")]
    texts = []
    walk(fl, lambda c, k, v, p: texts.append(v) if isinstance(v, str) and k != "url" else None)
    odd = sorted({m.group(0) for s in texts for m in IQ_NAME.finditer(s) if m.group(0).lower() not in OFFICIAL_IQ})
    if odd:
        rep.warn("feedback_loop uses " + ", ".join(repr(x) for x in odd) + ", which is not an official Microsoft IQ name; "
                 "use Microsoft IQ, Work IQ, Fabric IQ, Foundry IQ or Web IQ")


def clean_attendees(bp: dict, rep: "Report") -> None:
    """Contributions are text or {text, src, at, focus}, backed by evidence."""
    attendees = bp.get("attendees")
    if attendees is None:
        return
    if not isinstance(attendees, dict):
        rep.warn("attendees must be an object with people")
        return
    for i, person in enumerate(as_list(attendees.get("people"))):
        if not isinstance(person, dict):
            continue
        who = person.get("name") or person.get("role") or f"people[{i}]"
        contrib = [c for c in as_list(person.get("contributions")) if c]
        bare = [c for c in contrib if not (isinstance(c, dict) and src_ids(c.get("src")))]
        if bare and not src_ids(person.get("src")):
            rep.warn(f"attendee {who}: {len(bare)} contribution(s) without evidence; cite the transcript or notes (src)")
        for c in contrib:
            if isinstance(c, dict) and not str(c.get("text") or "").strip():
                rep.warn(f"attendee {who}: a contribution has no text")


def normalise(bp: dict, rep: Report) -> dict:
    meta = bp.setdefault("meta", {})
    if not str(meta.get("customer", "")).strip():
        rep.err("meta.customer is required")
    meta.setdefault("short", str(meta.get("customer", "Customer")).split(" ")[0])
    if not meta.get("id"):
        meta["id"] = SLUG.sub("-", str(meta.get("customer", "blueprint")).lower()).strip("-") + "-frontier"
    meta.setdefault("version", "0.1")
    meta.setdefault("status", "hypothesis")
    meta["generated"] = _dt.date.today().isoformat()
    meta["plugin_version"] = PLUGIN_VERSION
    if meta.get("accent") and not HEX.match(str(meta["accent"])):
        rep.warn(f"meta.accent {meta['accent']!r} is not #RRGGBB; the default accent is used")
    if meta.get("logo_data_uri") and not LOGO_OK.match(str(meta["logo_data_uri"])):
        rep.err("meta.logo_data_uri must be a base64 PNG, JPEG, GIF or WebP data URI")

    domains = as_list(bp.get("domains"))
    bp["domains"] = domains
    if not domains:
        rep.err("at least one domain (journey) is required in 'domains'")
    seen_dom, seen_agent_ids, seen_agent_names = set(), set(), {}
    for di, d in enumerate(domains):
        if not isinstance(d, dict):
            rep.err(f"domains[{di}] is not an object")
            continue
        d.setdefault("id", f"D{di + 1}")
        if d["id"] in seen_dom:
            rep.err(f"duplicate domain id {d['id']}")
        seen_dom.add(d["id"])
        if not d.get("name"):
            rep.err(f"domain {d['id']} has no name")
        if d.get("color") and not HEX.match(str(d["color"])):
            rep.warn(f"domain {d['id']} color {d['color']!r} is not #RRGGBB; a palette colour is used")
        if not d.get("orchestrator"):
            rep.warn(f"domain {d['id']} has no orchestrator (lead agent)")
        team = []
        if isinstance(d.get("orchestrator"), dict):
            o = d["orchestrator"]
            o.setdefault("id", f"{d['id']}-LEAD")
            team.append(o)
        d["agents"] = as_list(d.get("agents"))
        for ai, a in enumerate(d["agents"]):
            if not isinstance(a, dict):
                rep.err(f"{d['id']}.agents[{ai}] is not an object")
                continue
            a.setdefault("id", f"{d['id']}-A{ai + 1:02d}")
            team.append(a)
        for a in team + ([d["data_agent"]] if isinstance(d.get("data_agent"), dict) else []):
            idn = a.get("identity")
            if idn is not None and (not isinstance(idn, dict) or (idn.get("icon") and not ICON_OK.match(str(idn["icon"])))):
                rep.warn(f"agent {a.get('id', a.get('name'))}: identity icon must be a base64 SVG or PNG data URI; identity ignored")
                a.pop("identity", None)
            elif isinstance(idn, dict):
                clean_agent_identity(idn, a.get("id", a.get("name")), rep)
        for a in team:
            if not a.get("name"):
                rep.err(f"agent {a.get('id')} has no name")
            if a["id"] in seen_agent_ids:
                rep.err(f"duplicate agent id {a['id']}")
            seen_agent_ids.add(a["id"])
            nm = str(a.get("name", "")).lower()
            if nm in seen_agent_names:
                rep.warn(f"agent name {a.get('name')!r} is used twice ({seen_agent_names[nm]} and {a['id']}); stage links resolve to the first")
            else:
                seen_agent_names[nm] = a["id"]
            au = str(a.get("autonomy", "")).lower()
            if not au and not a.get("autonomy_level"):
                rep.warn(f"agent {a['id']} has no autonomy level")
            elif au and not any(w in au for w in AUTONOMY_WORDS):
                rep.warn(f"agent {a['id']} autonomy {a.get('autonomy')!r} does not map to Assist / Act with approval / Act within guardrails")
            st = str(a.get("status", "hypothesis")).lower()
            if st not in STATUS_OK:
                rep.warn(f"agent {a['id']} status {a.get('status')!r} is not a known status")
            if a.get("mvp"):
                decl = a.get("declarations") or {}
                missing = [k for k in DECLARATIONS if not decl.get(k)]
                if missing:
                    rep.warn(f"MVP agent {a['id']} is missing declarations: {', '.join(missing)}")
                if not a.get("canvas"):
                    rep.warn(f"MVP agent {a['id']} has no trigger canvas")
        # discovery question ids
        disc = d.get("discovery") or {}
        if not isinstance(disc, dict):
            rep.err(f"domain {d['id']} discovery must be an object of category -> questions")
            disc = {}
        n = 0
        seen_q = set()
        for cat, qs in disc.items():
            fixed = []
            for q in as_list(qs):
                n += 1
                if isinstance(q, str):
                    q = {"q": q}
                q.setdefault("id", f"{d['id']}-Q{n:02d}")
                while q["id"] in seen_q:
                    n += 1
                    q["id"] = f"{d['id']}-Q{n:02d}"
                seen_q.add(q["id"])
                if q.get("status") and str(q["status"]).lower() not in ("open", "partial", "answered"):
                    rep.warn(f"question {q['id']} status {q['status']!r} should be open, partial or answered")
                fixed.append(q)
            disc[cat] = fixed
        if disc:
            d["discovery"] = disc

    # agent lookup by name and id
    by_name = {}
    for d in domains:
        if not isinstance(d, dict):
            continue
        for a in ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + d.get("agents", []):
            if isinstance(a, dict):
                by_name.setdefault(str(a.get("name", "")).lower(), a)
                by_name.setdefault(str(a.get("id", "")).lower(), a)
    for d in domains:
        if not isinstance(d, dict):
            continue
        for si, st in enumerate(as_list(d.get("stages"))):
            ag = st.get("agent") if isinstance(st, dict) else None
            if ag and str(ag).lower() not in by_name:
                rep.warn(f"{d['id']} stage {si + 1} ({st.get('name')}) names agent {ag!r}, which is not defined")

    # leaders
    leaders = as_list(bp.get("leaders"))
    lids = set()
    for i, L in enumerate(leaders):
        L.setdefault("id", f"L{i + 1}")
        if L["id"] in lids:
            rep.err(f"duplicate leader id {L['id']}")
        lids.add(L["id"])
    for d in domains:
        if isinstance(d, dict) and d.get("leader") and d["leader"] not in lids:
            rep.warn(f"domain {d['id']} leader {d['leader']!r} is not in 'leaders'")
    if len(leaders) > 7:
        rep.warn("more than 7 leaders crowd the centre of the org model; keep the accountable few")

    # use cases
    ucs = []
    for d in domains:
        if isinstance(d, dict):
            for u in as_list(d.get("use_cases")):
                u.setdefault("domain", d["id"])
                ucs.append(u)
    ucs += as_list(bp.get("use_cases"))
    seen_uc = set()
    for i, u in enumerate(ucs):
        u.setdefault("id", f"UC{i + 1:02d}")
        if u["id"] in seen_uc:
            rep.err(f"duplicate use case id {u['id']}")
        seen_uc.add(u["id"])
        if u.get("domain") and u["domain"] not in seen_dom:
            rep.warn(f"use case {u['id']} domain {u['domain']!r} is unknown")
        for k in ("value", "feasibility"):
            v = u.get(k)
            if isinstance(v, (int, float)):
                if not 1 <= v <= 5:
                    rep.warn(f"use case {u['id']} {k} {v} is outside 1-5")
            elif v is not None and str(v).lower() not in ("high", "medium", "low"):
                rep.warn(f"use case {u['id']} {k} {v!r} should be 1-5 or High/Medium/Low")
        for an in as_list(u.get("agents")):
            if str(an).lower() not in by_name:
                rep.warn(f"use case {u['id']} names agent {an!r}, which is not defined")

    for m in as_list(bp.get("mvp_options")):
        if m.get("domain") and m["domain"] not in seen_dom:
            rep.warn(f"MVP option {m.get('option')} domain {m['domain']!r} is unknown")

    # evidence
    ev = as_list(bp.get("evidence"))
    bp["evidence"] = ev
    eids = set()
    for i, e in enumerate(ev):
        e.setdefault("id", f"E{i + 1:02d}")
        if e["id"] in eids:
            rep.err(f"duplicate evidence id {e['id']}")
        eids.add(e["id"])
        if not e.get("title"):
            rep.warn(f"evidence {e['id']} has no title")
        vis = str(e.get("visibility", "")).lower()
        if vis not in ("internal", "customer"):
            rep.warn(f"evidence {e['id']} visibility should be 'internal' or 'customer' (treated as customer)")

    def check_src(container, key, value, path):
        if key == "src":
            for sid in src_ids(value):
                if sid not in eids:
                    rep.warn(f"{path} cites {sid}, which is not in the evidence register")
        if isinstance(value, str) and URL.search(value) and key not in ("source",) and not (key == "url" and path.startswith(("$.identity.rules", "$.value_case.sources", "$.finops.sources", "$.factory.resources", "$.factory.sources", "$.architecture.landing_zone.sources", "$.feedback_loop.sources", "$.logos_note", "$.ontology.sources_doc"))) and path != "$.logos_note":
            rep.warn(f"{path} contains a URL; links are not rendered (keep sources in the evidence register)")
    clean_identity_block(bp, rep)
    clean_value_finops(bp, rep)
    clean_canon_blocks(bp, rep)
    clean_feedback_loop(bp, rep)
    clean_attendees(bp, rep)
    walk(bp, check_src)
    return bp


def process_library():
    """Load the optional process model only for a blueprint that has one."""
    process = Path(__file__).resolve().parents[2] / "frontier-process" / "scripts"
    sys.path.insert(0, str(process))
    import ontology_lib
    return ontology_lib


def prepare_ontology_privacy(bp: dict, rep: Report | None = None) -> None:
    """Re-evaluate root/target provenance before projecting promoted content."""
    onto = bp.get("ontology")
    if not isinstance(onto, dict) and not bp.get("ontology_feedback"):
        return
    onto = onto if isinstance(onto, dict) else {}
    lib = process_library()
    lib.inherit_privacy(onto, bp)
    rd = bp.get("it_readiness") if isinstance(bp.get("it_readiness"), dict) else {}
    rows = {r.get("id"): r for r in as_list(onto.get("readiness")) if isinstance(r, dict)}
    for group in as_list(rd.get("groups")):
        if not isinstance(group, dict) or group.get("id") != "fabric-iq":
            continue
        if lib.private_content(onto, bp):
            group["internal"] = True
        for item in as_list(group.get("items")):
            if isinstance(item, dict) and lib.private_content(rows.get(item.get("id"), {}), bp):
                item["internal"] = True
    for verdict in as_list(bp.get("ontology_feedback")):
        if isinstance(verdict, dict):
            restricted, unresolved = lib.feedback_privacy(onto, verdict, bp)
            if restricted:
                verdict["internal"] = True
            if unresolved:
                verdict["ancestry_status"] = "unresolved"
                message = f"ontology feedback {verdict.get('id')}: ancestry unresolved ({', '.join(unresolved)}); retained internally"
                if rep is not None and message not in rep.warnings:
                    rep.warn(message)


def customer_version(bp: dict, rep: Report) -> dict:
    out = copy.deepcopy(bp)
    prepare_ontology_privacy(out, rep)
    internal_ids = {e["id"] for e in as_list(out.get("evidence")) if str(e.get("visibility", "")).lower() == "internal"}
    out["evidence"] = [e for e in as_list(out.get("evidence")) if e["id"] not in internal_ids]
    if internal_ids:
        rep.removed.append(f"internal evidence: {', '.join(sorted(internal_ids))}")

    def hidden(obj):
        if not isinstance(obj, dict):
            return False
        # A workshop verdict may add a public src without making the content
        # it discusses public. content_src retains that independent provenance.
        refs = src_ids(obj.get("content_src", obj.get("src")))
        return obj.get("internal") is True or str(obj.get("visibility", "")).lower() == "internal" or bool(refs and all(s in internal_ids for s in refs))

    def scrub(obj, path="$"):
        if isinstance(obj, dict):
            for k in list(obj.keys()):
                if k == "internal_notes":
                    del obj[k]
                    rep.removed.append(f"{path}.internal_notes")
                    continue
                if k in ("src", "content_src"):
                    kept = [s for s in src_ids(obj[k]) if s not in internal_ids]
                    if kept:
                        obj[k] = kept
                    else:
                        del obj[k]
                    continue
                if hidden(obj[k]):
                    del obj[k]
                    rep.removed.append(f"{path}.{k} (internal-only content)")
                    continue
                scrub(obj[k], f"{path}.{k}")
        elif isinstance(obj, list):
            keep = []
            for i, v in enumerate(obj):
                if hidden(v):
                    rep.removed.append(f"{path}[{i}] (internal-only content)")
                    continue
                scrub(v, f"{path}[{i}]")
                keep.append(v)
            obj[:] = keep
    scrub(out)
    if isinstance(out.get("ontology"), dict):
        lib = process_library()
        authored = lib.customer_ontology(out["ontology"], out)
        if authored is None:
            out.pop("ontology")
        else:
            onto = lib.normalize(authored, out, rep)
            entities = {e["id"]: e for e in onto["entity_types"]}
            for agent in onto["data_agents"]:
                if not agent.get("instructions"):
                    agent["instructions_default"] = lib.default_instructions(agent, onto, entities)
            out["ontology"] = onto
    # Evaluate block visibility before projecting retained fields. Discard
    # cached PRD copies afterwards; derive them again from scrubbed sources.
    if isinstance(out.get("prd"), dict):
        out["prd"] = {k: v for k, v in out["prd"].items() if k in PRD_AUTHORED}
    meta = out.setdefault("meta", {})
    terms = [t for t in as_list(meta.pop("internal_terms", None)) if str(t).strip()]
    meta["audience"] = "customer"
    blob = json.dumps(out, ensure_ascii=False).lower()
    for t in terms:
        if str(t).lower() in blob:
            rep.err(f"customer version still contains the internal term {t!r}; rewrite or flag the item internal")
    return out


def stats(bp: dict) -> dict:
    doms = [d for d in as_list(bp.get("domains")) if isinstance(d, dict)]
    leads = sum(1 for d in doms if isinstance(d.get("orchestrator"), dict))
    specs = sum(len(as_list(d.get("agents"))) for d in doms)
    ucs = sum(len(as_list(d.get("use_cases"))) for d in doms) + len(as_list(bp.get("use_cases")))
    qs = sum(len(as_list(q)) for d in doms for q in (d.get("discovery") or {}).values())
    mvp = [a.get("id") for d in doms for a in as_list(d.get("agents")) + ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) if a.get("mvp")]
    rd = bp.get("it_readiness") if isinstance(bp.get("it_readiness"), dict) else {}
    lz = (bp.get("architecture") or {}).get("landing_zone") if isinstance(bp.get("architecture"), dict) else None
    return {"domains": len(doms), "lead_agents": leads, "specialist_agents": specs, "use_cases": ucs,
            "discovery_questions": qs, "evidence": len(as_list(bp.get("evidence"))), "mvp_agents": mvp,
            "factory_journey": next((d.get("id") for d in doms if d.get("kind") == "factory"), None),
            "attendees": len(as_list((bp.get("attendees") or {}).get("people"))) if isinstance(bp.get("attendees"), dict) else 0,
            "landing_zone_areas": len((lz or {}).get("areas") or {}) if isinstance(lz, dict) else 0,
            "decisions": len(as_list((bp.get("architecture") or {}).get("decisions"))) if isinstance(bp.get("architecture"), dict) else 0,
            "readiness_items": sum(len(as_list(g.get("items"))) for g in as_list(rd.get("groups")) if isinstance(g, dict)),
            "feedback_loop_areas": len(as_list((bp.get("feedback_loop") or {}).get("quadrants"))) if isinstance(bp.get("feedback_loop"), dict) else 0,
            "workflows": sum(1 for d in doms for a in as_list(d.get("agents")) + ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else [])
                             if isinstance(a, dict) and isinstance(a.get("canvas"), dict) and isinstance(a["canvas"].get("workflow"), dict)),
            "product_icons": len(bp.get("logos") or {}) if isinstance(bp.get("logos"), dict) else 0,
            "risks": len(as_list((bp.get("risks") or {}).get("items"))) if isinstance(bp.get("risks"), dict) else 0,
            "ontology_entity_types": len(as_list((bp.get("ontology") or {}).get("entity_types"))) if isinstance(bp.get("ontology"), dict) else 0,
            "prd_requirements": (len(as_list((bp.get("prd") or {}).get("platform")))
                                 + sum(len(as_list(x.get("requirements"))) for x in as_list((bp.get("prd") or {}).get("agents")) if isinstance(x, dict)))
            if isinstance(bp.get("prd"), dict) else 0,
            "contributions_with_evidence": sum(1 for p in as_list((bp.get("attendees") or {}).get("people")) if isinstance(p, dict)
                                               for c in as_list(p.get("contributions"))
                                               if c and ((isinstance(c, dict) and src_ids(c.get("src"))) or src_ids(p.get("src"))))
            if isinstance(bp.get("attendees"), dict) else 0}


def render(bp: dict, template: str) -> str:
    if PLACEHOLDER not in template:
        raise ValueError("template does not contain the data placeholder \"__BLUEPRINT_DATA__\"")
    data = json.dumps(bp, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    data = data.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    meta = bp.get("meta", {})
    title = meta.get("title") or f"{meta.get('customer', 'Customer')} \u00b7 Frontier Company Blueprint"
    out = template.replace(PLACEHOLDER, data, 1)
    out = re.sub(r"<title>.*?</title>", "<title>" + html.escape(title) + "</title>", out, count=1, flags=re.S)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="blueprint JSON file")
    ap.add_argument("--out", help="HTML file to write (omit to validate only)")
    ap.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="template HTML")
    ap.add_argument("--audience", choices=("internal", "customer"), default=None,
                    help="customer = strip Microsoft-internal evidence and flagged items")
    ap.add_argument("--save-normalized", help="write the normalised JSON (stable ids) here")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--report", help="write the build report JSON here")
    ap.add_argument("--canon", action="store_true", help="add missing Innovation Hub canon: Agent Factory journey and plan board, landing zone, canon ADRs, IT readiness, digital feedback loop, canon risks")
    ap.add_argument("--defaults", default=str(DEFAULTS), help="canon defaults (templates/blueprint-defaults.json)")
    ap.add_argument("--no-product-icons", action="store_true", help="do not embed Microsoft and GitHub product icons")
    a = ap.parse_args(argv)

    rep = Report()
    try:
        bp = json.loads(Path(a.data).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        print(f"ERROR: cannot read {a.data}: {e}", file=sys.stderr)
        return 2
    if not isinstance(bp, dict):
        print("ERROR: the blueprint must be a JSON object", file=sys.stderr)
        return 2
    if a.canon:
        added = add_canon(bp, load_defaults(a.defaults))
        if added:
            rep.removed.append("canon added: " + ", ".join(added))
    bp = normalise(bp, rep)
    if isinstance(bp.get("feedback_loop"), dict):
        try:
            fill_feedback_loop(bp, load_defaults(a.defaults))
        except (OSError, ValueError) as e:
            rep.warn(f"feedback loop not completed from the journeys: {e}")
    fill_workflows(bp, rep)
    audience = a.audience or str(bp.get("meta", {}).get("audience", "internal")).lower()
    if audience == "customer":
        prepare_ontology_privacy(bp, rep)
        # Resolve bound content privacy while the original source still exists.
        # Scrubbing it first loses new flags and legacy provenance recovery.
        fill_risks(bp, rep)
        bp = customer_version(bp, rep)
    else:
        bp.setdefault("meta", {})["audience"] = "internal"
    # Final models are derived from the scrubbed sources.
    fill_risks(bp, rep)
    fill_prd(bp, rep)
    if not a.no_product_icons:
        embed_product_icons(bp, rep, ICONS)
    if a.strict and rep.warnings:
        rep.errors += [f"(strict) {w}" for w in rep.warnings]

    result = {"status": "error" if rep.errors else "ok", "audience": audience, "stats": stats(bp),
              "errors": rep.errors, "warnings": rep.warnings, "removed_for_customer": rep.removed}
    if not rep.errors:
        if a.save_normalized:
            Path(a.save_normalized).write_text(json.dumps(bp, ensure_ascii=False, indent=1), encoding="utf-8")
            result["normalized"] = a.save_normalized
        if a.out:
            try:
                tpl = Path(a.template).read_text(encoding="utf-8")
                Path(a.out).write_text(render(bp, tpl), encoding="utf-8")
                result["out"] = a.out
            except (OSError, ValueError) as e:
                print(f"ERROR: {e}", file=sys.stderr)
                return 2
    if a.report:
        Path(a.report).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    for e in rep.errors:
        print("ERROR:", e)
    for w in rep.warnings:
        print("WARN:", w)
    print(json.dumps({k: result[k] for k in ("status", "audience", "stats")}, ensure_ascii=False))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
