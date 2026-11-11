#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Seed a process ontology (frontier-ontology/1.0) from a Frontier Company Blueprint, for Microsoft Fabric IQ.

Usage:
  python seed_ontology.py --blueprint blueprint.json --out ontology.json
         [--semantic-model model.bim --journey D3] [--patterns ../templates/ontology-patterns.json]

What the seed does (deterministic scaffolding, not the hypothesis itself):
  * one namespace per business journey plus "core" for entity types the journeys share (Customer, Product, Asset ...);
    the journey pattern (Lead-to-Order, Source-to-Pay, Request-to-Resolution, Record-to-Report, Hire-to-Retire,
    Plan-to-Produce, else generic) is chosen by keywords in the journey's name, stages and systems
  * business concepts the digital feedback loop names for Fabric IQ ("modelled as Customer, Opportunity ...") are added
    when no pattern entity type matches them
  * the journey's systems of record become OneLake sources with a proposed path (mirroring, shortcut, eventstream,
    pipeline, semantic model); documents, mail and web stay with Foundry IQ, Work IQ and Web IQ
  * entity types are bound to the source whose system matches their hint; the journey KPIs become metrics to define
  * the approval seam becomes a business rule; one data agent per journey with example questions and the journey's
    agents as consumers; an operations agent where the journey has live signals (alarms, telemetry, events)
  * each entity type gets its Microsoft standard entity (templates/cdm-map.json: Common Data Model, Dataverse tables of
    Dynamics 365, finance and operations tables) and a binding to a silver table conformed to it; each product of a
    data agent becomes a data product with owner, purpose and intended uses (knowledge stays with Foundry IQ)
  * --semantic-model: a Power BI semantic model in TMSL (model.bim) adds its tables as entity types, its relationships
    and its DAX measures as metrics (the semantic model stays the owner of the expressions)
Prints a JSON summary. Standard library only; no network access.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ontology_lib import (TYPES, as_list, business_domains, camel, carry_content, inherit_privacy, load_canon, load_json, load_patterns,  # noqa: E402
                          normalize, pascal, private_content, ptype, slug, text_of, Rep)

LIVE = re.compile(r"alarm|telemetry|sensor|live event|stream|real-time|iot", re.I)
MODELLED = re.compile(r"modell?ed as ([^.;]+)", re.I)
TMSL_SKIP = re.compile(r"^(date|calendar|time|localdatetable_|datetabletemplate_)", re.I)


def pick_pattern(d: dict, lib: dict) -> dict:
    txt = text_of(d.get("name"), d.get("journey_name"), d.get("function"), [s.get("name") for s in as_list(d.get("stages")) if isinstance(s, dict)],
                  d.get("systems")).lower()
    best, score = None, 0
    for p in lib["patterns"]:
        n = len(re.findall(p["match"], txt))
        if n > score:
            best, score = p, n
    return best or lib["fallback"]


def concept_names(text: str) -> list:
    m = MODELLED.search(text or "")
    if not m:
        return []
    parts = re.split(r",| and ", m.group(1))
    return [p.strip() for p in parts if p.strip() and len(p.strip()) < 40]


def system_path(system: str, canon: dict):
    s = system.lower()
    if any(w in s for w in canon.get("not_ontology", [])):
        return None
    for rx, path in canon.get("system_rules", []):
        if re.search(rx, s):
            return path
    return "pipeline"


def matches(entity: dict, name: str) -> bool:
    n = name.strip().lower()
    return n in {str(entity.get("name", "")).lower(), entity["id"].lower()} | {str(s).lower() for s in entity.get("synonyms", [])}


def seed(bp: dict, lib: dict, canon: dict) -> dict:
    meta = bp.get("meta") or {}
    short = meta.get("short") or str(meta.get("customer") or "Customer").split(" ")[0]
    core_lib = {e["id"]: e for e in lib["core"]}
    onto = {"schema": "frontier-ontology/1.0",
            "meta": {"customer": meta.get("customer"), "short": short, "blueprint": meta.get("id"), "version": "0.1", "status": "hypothesis",
                     "date": meta.get("date") or canon.get("checked") or "undated"},
            "title": f"{short} process ontology",
            "intro": "", "namespaces": [{"id": "core", "name": "Shared business objects", "journey": None, "owner": "Data platform owner"}],
            "entity_types": [], "relationship_types": [], "rules": [], "metrics": [], "sources": [], "data_agents": [], "operations_agents": [],
            "_todo": []}
    for field in ("src", "content_src", "visibility", "internal"):
        if field in bp:
            onto[field] = json.loads(json.dumps(bp[field]))
    if private_content(meta, bp):
        onto["internal"] = True
    ents = {}
    loop = (bp.get("feedback_loop") or {}).get("quadrants") or []
    agents_by_dom = {}
    for d in as_list(bp.get("domains")):
        if isinstance(d, dict):
            agents_by_dom[d.get("id")] = ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + [a for a in as_list(d.get("agents")) if isinstance(a, dict)]

    def add_entity(tpl: dict, ns: str, jid: str, origin: str):
        eid = tpl["id"]
        if eid in ents:
            if jid not in ents[eid]["journeys"]:
                ents[eid]["journeys"].append(jid)
            return ents[eid]
        e = {k: json.loads(json.dumps(v)) for k, v in tpl.items() if k != "system_hint"}
        e.update({"namespace": ns, "journeys": [jid], "status": "hypothesis", "origin": origin, "_hint": tpl.get("system_hint", "")})
        ents[eid] = e
        onto["entity_types"].append(e)
        return e

    sources = {}
    mcount = 0
    plan = []
    # pass 1: the journey patterns (so a concept named in the feedback loop finds its pattern entity type)
    for d in business_domains(bp):
        jid = d.get("id")
        pat = pick_pattern(d, lib)
        ns = slug(d.get("short") or d.get("name") or jid)
        lead = d.get("leader")
        lead = lead if isinstance(lead, dict) else next((x for x in as_list(bp.get("leaders")) if isinstance(x, dict) and x.get("id") == lead), {})
        onto["namespaces"].append(carry_content({"id": ns, "name": d.get("name"), "journey": jid, "pattern": pat["id"],
                                               "owner": lead.get("role") or d.get("owner")}, d, lead, bp=bp))
        mine = []
        for cid in pat.get("core", []):
            if cid in core_lib:
                mine.append(add_entity(core_lib[cid], "core", jid, "core"))
        for tpl in pat["entities"]:
            mine.append(add_entity(tpl, ns, jid, pat["id"]))
        plan.append((d, jid, pat, ns, mine))
    # pass 2: everything else per journey
    for d, jid, pat, ns, mine in plan:
        # concepts the feedback loop names for Fabric IQ (with the evidence of the signal)
        for q in loop:
            if jid not in as_list(q.get("journeys")):
                continue
            for s in as_list(q.get("signals")):
                if "fabric" not in as_list(s.get("iq")):
                    continue
                stext = str(s.get("text", "")).lower()
                for e in mine:
                    terms = [str(x).lower() for x in [e.get("name"), re.sub(r"([a-z])([A-Z])", r"\1 \2", e["id"])] + list(e.get("synonyms") or []) if x and len(str(x)) > 3]
                    if any(re.search(r"\b" + re.escape(x) + r"s?\b", stext) for x in terms):
                        carry_content(e, d, q, s, bp=bp)
                for c in concept_names(s.get("text", "")):
                    if not any(matches(e, c) for e in ents.values()):
                        eid = pascal(c)
                        mine.append(carry_content(add_entity({"id": eid, "name": c[:1].upper() + c[1:], "description": f"Named in the digital feedback loop: {s.get('text')}",
                                                "synonyms": [], "key": [camel(c) + "Id"], "properties": [{"name": camel(c) + "Id", "type": "string"},
                                                                                                          {"name": "status", "type": "string"}]},
                                               ns, jid, "feedback loop"), d, q, s, bp=bp))
        for r in pat.get("relationships", []):
            fr, name, to, card = r
            if fr in ents and to in ents:
                rid = f"{fr}_{name}_{to}"
                if not any(x["id"] == rid for x in onto["relationship_types"]):
                    onto["relationship_types"].append({"id": rid, "name": name, "from": fr, "to": to, "cardinality": card, "status": "hypothesis"})
        # systems of record -> OneLake sources; bind entity types by their hint
        for sysname in as_list(d.get("systems")):
            path = system_path(str(sysname), canon)
            if not path:
                continue
            base = re.sub(r"\s*\(.*?\)", "", str(sysname)).strip() or str(sysname)
            module = (re.search(r"\((.*?)\)", str(sysname)) or [None, None])[1]
            sid = "src-" + slug(base)
            if sid not in sources:
                sources[sid] = {"id": sid, "name": base, "system": str(sysname), "path": path, "_modules": [],
                                "item": canon["paths"][path]["item"], "journeys": [jid], "data_class": "confidential",
                                "status": "later" if re.search(r"to confirm", str(sysname), re.I) else "next", "owner": None}
                onto["sources"].append(sources[sid])
            elif jid not in sources[sid]["journeys"]:
                sources[sid]["journeys"].append(jid)
            if module and module.lower() != "to confirm" and module not in sources[sid]["_modules"]:
                sources[sid]["_modules"].append(module)
        for e in mine:
            if e.get("source"):
                continue
            hint = e.get("_hint") or ""
            for sysname in as_list(d.get("systems")):
                sid = "src-" + slug(re.sub(r"\s*\(.*?\)", "", str(sysname)).strip() or str(sysname))
                if sid in sources and hint and re.search(hint, str(sysname), re.I):
                    live_here = any(s2["item"] == "eventhouse" and jid in s2["journeys"] for s2 in sources.values())
                    if e.get("event") and sources[sid]["item"] != "eventhouse" and live_here:
                        continue  # an event entity type binds to the eventhouse
                    if e.get("timeseries") and sources[sid]["item"] == "eventhouse":
                        continue  # static data first; the time series follow as a secondary binding
                    e["source"] = sid
                    break
        # time series: live sources of the journey
        live = [s for s in sources.values() if s["item"] == "eventhouse" and jid in s["journeys"]]
        for e in mine:
            if e.get("timeseries") and live and not e.get("source"):
                e["source"] = live[0]["id"]
            if e.get("timeseries") and live and e.get("source") != live[0]["id"]:
                e.setdefault("secondary", []).append(live[0]["id"])
        # KPIs -> metrics
        for k in as_list(d.get("kpis")):
            if not isinstance(k, dict) or not k.get("kpi"):
                continue
            target = None
            for rx, eid in pat.get("kpi_map", {}).items():
                if re.search(rx, k["kpi"], re.I) and eid in ents:
                    target = eid
                    break
            mcount += 1
            onto["metrics"].append(carry_content({"id": f"M-{mcount:02d}", "name": k["kpi"], "kpi": k["kpi"], "journey": jid, "entity": target,
                                    "definition": k.get("definition"), "baseline": k.get("baseline"), "target": k.get("target"),
                                    "measure": None, "semantic_model": None, "status": "to define"}, d, k, bp=bp))
        # approval seam -> rule
        seam = d.get("approval_seam") or d.get("approval")
        seam_origin = seam if isinstance(seam, dict) else {}
        if isinstance(seam, dict):
            seam = seam.get("text") or seam.get("what")
        if seam:
            applies = [e["id"] for e in mine if e.get("namespace") == ns and re.search(r"\b(" + "|".join(re.escape(t.lower()) for t in [e.get("name", "")] + e.get("synonyms", []) if t) + r")", str(seam).lower())]
            onto["rules"].append(carry_content({"text": f"Approval seam ({d.get('name')}): {seam}",
                                  "applies_to": applies or [e["id"] for e in mine if e.get("namespace") == ns][:3], "journey": jid},
                                  d, seam_origin, bp=bp))
        # data agent per journey
        consumers = [a.get("id") for a in agents_by_dom.get(jid, []) if a.get("id")]
        own = [e["id"] for e in mine]
        qs = [{"q": q} for q in pat.get("questions", [])]
        for m in [m for m in onto["metrics"] if m["journey"] == jid and m.get("entity")][:2]:
            qs.append(carry_content({"q": f"How did {m['name'].lower()} develop by month over the last six months?"}, m, bp=bp))
        srcs = ["ontology"] + [s["id"] for s in live][:4]
        personas = [p.get("role") for p in as_list(d.get("personas")) if isinstance(p, dict) and p.get("role")]
        bda = d.get("data_agent") if isinstance(d.get("data_agent"), dict) else {}
        products = []
        for prod in as_list(bda.get("products")):
            product_origin = prod if isinstance(prod, dict) else {}
            product_name = product_origin.get("name") if product_origin else str(prod)
            pl = str(product_name).lower()
            if re.search(r"knowledge|article|manual|document|template|policy|policies", pl):
                products.append(carry_content({"name": product_name, "entities": [], "note": "documents: Foundry IQ"}, bda, product_origin, bp=bp))
                continue
            pairs = []
            for e in ents.values():
                if e.get("namespace") not in ("core", ns):
                    continue  # data products map to the journey's own and the shared entity types only
                terms = [str(x).lower() for x in [e.get("name"), re.sub(r"([a-z])([A-Z])", r"\1 \2", e["id"])] + list(e.get("synonyms") or []) if x and len(str(x)) > 3]
                best = max((x for x in terms if re.search(r"\b" + re.escape(x) + r"s?\b", pl) or (len(pl) > 6 and pl in x)), key=len, default=None)
                if best:
                    pairs.append((e["id"], best))
            hit = [eid for eid, term in pairs if not any(term != other and term in other for _, other in pairs)]
            for eid in hit:
                e = ents[eid]
                if jid not in e["journeys"]:
                    e["journeys"].append(jid)
                if eid not in own:
                    own.append(eid)
            products.append(carry_content({"name": product_name, "entities": hit, "note": None if hit else "to model"}, bda, product_origin, bp=bp))
        onto["data_agents"].append(carry_content({"name": bda.get("name") or f"{d.get('name')} data agent", "journey": jid,
                                    "scope": f"the {d.get('journey_name') or d.get('name')}",
                                    "description": f"Answers questions about the {d.get('journey_name') or d.get('name')} in business terms: "
                                                   + ", ".join(ents[x].get("name") for x in own) + ".",
                                    "journeys": [jid], "entities": own, "sources": srcs, "products": products,
                                    "audience": ", ".join(personas[:3]) or None,
                                    "consumers": [{"kind": "copilot_studio", "agents": consumers[:6]}],
                                    "questions": qs[:6], "status": "hypothesis"}, d, bda, bp=bp))
        # operations agent where the journey has live signals
        live_signals = [(q, s) for q in loop if jid in as_list(q.get("journeys")) for s in as_list(q.get("signals"))
                        if "fabric" in as_list(s.get("iq")) and LIVE.search(str(s.get("text")))]
        ts_ents = [e["id"] for e in mine if e.get("timeseries") or e.get("event")]
        if live or live_signals:
            approver = None
            m = re.search(r"\bthe (\w+) approves\b", str(seam or ""), re.I)
            if m:
                approver = m.group(1).capitalize()
            req = next((e["id"] for e in mine if e["id"] in ("ServiceRequest", "WorkOrder", "ProductionOrder")), None)
            watched = ts_ents + ([req] if req else [])
            onto["operations_agents"].append(carry_content({
                "name": f"{d.get('short') or d.get('name')} watch", "journeys": [jid], "entities": watched,
                "goal": "Act on live signals before the customer notices: " + (live_signals[0][1]["text"] if live_signals else "live events of the journey"),
                "rules": [f"When an asset raises an alarm of high severity and has no open {ents[req]['name'].lower() if req else 'request'}, recommend opening one with the alarm context.",
                          "When the same alarm repeats three times within 24 hours, recommend a remote diagnosis before a visit."] if any(ents[x].get("event") for x in ts_ents)
                         else ["When a live value leaves its agreed range, recommend the next step to the process owner."],
                "actions": [{"name": "Create" + (req or "Request"), "params": ["assetId", "alarmCode"] if "Asset" in ents else ["id"], "approver": approver or "Process owner"}],
                "notify": "Microsoft Teams", "status": "hypothesis"}, d, seam_origin, *(live_signals[0] if live_signals else ()), bp=bp))
    for i, a in enumerate(onto["data_agents"], start=1):
        a["id"] = f"DA-{i:02d}"
    for i, a in enumerate(onto["operations_agents"], start=1):
        a["id"] = f"OA-{i:02d}"
    for i, r in enumerate(onto["rules"], start=1):
        r["id"] = f"RU-{i:02d}"
    for e in onto["entity_types"]:
        e.pop("_hint", None)
    for s in onto["sources"]:
        mods = s.pop("_modules", [])
        s["system"] = s["name"] + (f" ({', '.join(mods)})" if mods else "")
    onto["_todo"] = ["Confirm the entity types, keys and relationships with the data owners of each journey",
                     "Confirm the path of every system of record into OneLake (mirroring, shortcut, eventstream, pipeline)",
                     "Name the semantic model and DAX measure behind each metric, or mark it to build",
                     "Review the data agents: audience, consumers, instructions and five realistic example questions each",
                     "Confirm the Microsoft standard entity of each entity type (Common Data Model) and verify its columns with the table definition browser",
                     "Name an accountable owner, the intended uses, the access process and the quality status of each data product",
                     "Decide OD-ONT-1 to OD-ONT-6 (see ontology.md)"]
    return inherit_privacy(onto, bp)


def singular(name: str) -> str:
    n = str(name)
    if re.search(r"ies$", n, re.I):
        return n[:-3] + "y"
    if re.search(r"(ss|us|is)$", n, re.I):
        return n
    if re.search(r"(ches|shes|xes|sses)$", n, re.I):
        return n[:-2]
    return n[:-1] if n.lower().endswith("s") else n


TMSL_TYPES = {"string": "string", "int64": "integer", "double": "double", "decimal": "double", "datetime": "datetime", "boolean": "boolean"}


def add_semantic_model(onto: dict, model: dict, jid: str | None, rep: Rep) -> dict:
    """Tables -> entity types, relationships -> relationship types, measures -> metrics (TMSL / model.bim)."""
    m = model.get("model", model)
    name = model.get("name") or m.get("name") or "Semantic model"
    sid = "src-sm-" + slug(name)
    if not any(s["id"] == sid for s in onto["sources"]):
        onto["sources"].append({"id": sid, "name": f"{name} (semantic model)", "system": name, "path": "semantic model", "item": "semantic model",
                                "journeys": [jid] if jid else [], "data_class": "confidential", "status": "now"})
    ns = next((n["id"] for n in onto["namespaces"] if jid and n.get("journey") == jid), "core")
    keycols = {}
    for r in as_list(m.get("relationships")):
        if isinstance(r, dict) and r.get("toTable") and r.get("toColumn"):
            keycols.setdefault(r["toTable"], r["toColumn"])
    tmap, added = {}, {"entities": 0, "merged": 0, "relationships": 0, "metrics": 0}
    for t in as_list(m.get("tables")):
        if not isinstance(t, dict) or not t.get("name") or TMSL_SKIP.match(t["name"]) or t.get("isHidden") or t.get("isPrivate"):
            continue
        cols = [c for c in as_list(t.get("columns")) if isinstance(c, dict) and c.get("name") and not str(c.get("name")).startswith("RowNumber")]
        names = {t["name"], re.sub(r"([a-z])([A-Z])", r"\1 \2", t["name"])}
        names |= {singular(n) for n in list(names)}
        existing = next((e for e in onto["entity_types"] if any(matches(e, n) or e["id"].lower() == pascal(n).lower() for n in names)), None)
        props = []
        for c in cols:
            pn = camel(c["name"])
            pt = TMSL_TYPES.get(str(c.get("dataType", "string")).lower(), ptype(c.get("dataType")) or "string")
            props.append({"name": pn, "type": pt if pt in TYPES else "string", "column": c["name"]})
        key = keycols.get(t["name"]) or next((c["name"] for c in cols if c.get("isKey")), None) \
            or next((c["name"] for c in cols if re.search(r"(id|key|code|number)$", c["name"], re.I)), None)
        if existing:
            have = {p["name"] for p in existing["properties"]}
            existing["properties"] += [p for p in props if p["name"] not in have]
            existing.setdefault("secondary", [])
            if sid not in existing["secondary"] and existing.get("source") != sid:
                existing["secondary"].append(sid)
            tmap[t["name"]] = existing["id"]
            added["merged"] += 1
        else:
            eid = pascal(t["name"])
            e = {"id": eid, "name": t["name"], "namespace": ns, "description": t.get("description") or f"Table {t['name']} of the semantic model {name}.",
                 "synonyms": [], "key": [camel(key)] if key else [], "properties": props, "journeys": [jid] if jid else [],
                 "source": sid, "table": t["name"], "status": "hypothesis", "origin": "semantic model"}
            onto["entity_types"].append(e)
            tmap[t["name"]] = eid
            added["entities"] += 1
        for ms in as_list(t.get("measures")):
            if isinstance(ms, dict) and ms.get("name"):
                onto["metrics"].append({"id": f"M-{len(onto['metrics']) + 1:02d}", "name": ms["name"], "entity": tmap[t["name"]], "journey": jid,
                                        "measure": f"[{ms['name']}]", "semantic_model": name, "definition": ms.get("description"), "status": "from semantic model"})
                added["metrics"] += 1
    for r in as_list(m.get("relationships")):
        if not isinstance(r, dict):
            continue
        fr, to = tmap.get(r.get("fromTable")), tmap.get(r.get("toTable"))
        if fr and to and fr != to:
            rid = f"{fr}_belongs_to_{to}"
            if not any(x["id"] == rid for x in onto["relationship_types"]):
                onto["relationship_types"].append({"id": rid, "name": "belongs_to", "from": fr, "to": to, "cardinality": "n:1", "status": "hypothesis",
                                                   "description": f"From the semantic model {name}: {r.get('fromTable')}[{r.get('fromColumn')}] -> {r.get('toTable')}[{r.get('toColumn')}]"})
                added["relationships"] += 1
    rep.warn(f"semantic model {name}: entity types bound to it can't serve data agents or operations agents yet (known issue R-ONT-2); bind those to tables")
    return added


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True, help="Frontier Company Blueprint JSON (the normalized one is best)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--patterns", help="journey pattern library (default: templates/ontology-patterns.json)")
    ap.add_argument("--semantic-model", help="Power BI semantic model in TMSL (model.bim): tables, relationships, measures")
    ap.add_argument("--journey", help="journey id the semantic model belongs to (for example D3)")
    a = ap.parse_args(argv)
    try:
        bp = load_json(a.blueprint)
        lib = load_json(a.patterns) if a.patterns else load_patterns()
        canon = load_canon()
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    if not business_domains(bp):
        print("ERROR: the blueprint has no business journey to model", file=sys.stderr)
        return 1
    rep = Rep()
    onto = seed(bp, lib, canon)
    sm = None
    if a.semantic_model:
        try:
            sm = add_semantic_model(onto, load_json(a.semantic_model), a.journey, rep)
        except (OSError, ValueError) as e:
            print(f"ERROR: semantic model: {e}", file=sys.stderr)
            return 2
    norm = normalize(onto, bp, rep, canon)
    if rep.errors:
        print(json.dumps({"status": "failed", "files": [], "requested_out": a.out, "stats": norm.get("stats"),
                          "errors": rep.errors, "warnings": rep.warnings}, ensure_ascii=False, indent=1))
        return 1
    # write the proposals the team refines: the standard entity and binding per entity type, the data products
    nby = {e["id"]: e for e in norm.get("entity_types", [])}
    for e in onto["entity_types"]:
        n = nby.get(e["id"]) or {}
        if n.get("standard"):
            e["standard"] = {k: v for k, v in n["standard"].items() if k not in ("mapped", "of")}
        if n.get("binding"):
            e["binding"] = dict(n["binding"])
    onto["data_products"] = [{k: v for k, v in d.items() if k != "gaps"} for d in norm.get("data_products", [])]
    todo = onto.get("_todo", [])
    for k in ("process", "stats"):
        onto.pop(k, None)
    onto["_todo"] = todo
    Path(a.out).write_text(json.dumps(onto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "ok" if not rep.errors else "errors", "out": a.out, "stats": norm["stats"], "semantic_model": sm,
                      "patterns": {n["id"]: n.get("pattern") for n in onto["namespaces"] if n.get("journey")},
                      "errors": rep.errors, "warnings": rep.warnings[:25]}, ensure_ascii=False, indent=1))
    return 0 if not rep.errors else 1


if __name__ == "__main__":
    sys.exit(main())
