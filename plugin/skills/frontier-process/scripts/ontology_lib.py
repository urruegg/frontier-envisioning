#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Process ontology library (frontier-process): checks, derived views and the outputs for Microsoft Fabric IQ.

  load_canon()                     the Fabric IQ canon (templates/fabric-iq-canon.json)
  normalize(onto, bp=None, rep)    check and complete an ontology (frontier-ontology/1.0); adds "process" and "stats"
  process_map(onto, bp)            which entity types each journey stage touches
  to_turtle(onto)                  OWL in Turtle for the import into an empty Fabric ontology (preview) item
  to_markdown(onto, bp=None)       the design document (ontology.md)
  data_agent_kit(onto)             instructions, source descriptions and example questions per data agent

The model follows the ontology (preview) concepts of Fabric IQ: entity types with properties and a key, relationship
types, business rules in natural language, metrics from semantic-model measures, data bindings to OneLake sources,
namespaces; consumers are Fabric data agents and operations agents. Standard library only.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"
SCHEMA = "frontier-ontology/1.0"
TYPES = ("string", "integer", "double", "boolean", "datetime")
KEY_TYPES = ("string", "integer")
XSD = {"string": "xsd:string", "integer": "xsd:integer", "double": "xsd:double", "boolean": "xsd:boolean", "datetime": "xsd:dateTime"}
TYPE_ALIASES = {"str": "string", "text": "string", "int": "integer", "int64": "integer", "long": "integer", "bigint": "integer",
                "decimal": "double", "float": "double", "number": "double", "currency": "double", "real": "double",
                "bool": "boolean", "date": "datetime", "datetime2": "datetime", "timestamp": "datetime", "time": "datetime"}
CARD = ("1:1", "1:n", "n:1", "n:n")
STATUS = ("hypothesis", "validated", "adjusted", "rejected", "open")
SOURCE_STATUS = ("now", "next", "later")
SAP = re.compile(r"\bsap\b|\bs/?4(?:hana)?\b|\becc\b|\bdatasphere\b|\bariba\b|\bsuccessfactors\b", re.I)
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,99}$")
CONSUMER_KINDS = ("copilot_studio", "m365_copilot", "foundry", "teams")
STANDARDS = ("cdm", "dataverse", "operations", "custom")
MATCH = ("exact", "extends", "related", "custom")
ROLES = ("fact", "dimension")
LAYERS = ("bronze", "silver", "gold")
USES = ("analytics", "grounding", "actions")
SENSITIVITY = {"public": 0, "general": 1, "internal": 2, "confidential": 3, "highly confidential": 4, "restricted": 4}


class Rep:
    """Collects errors and warnings; scripts print them and decide the exit code."""

    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def as_list(x):
    return x if isinstance(x, list) else ([] if x in (None, "") else [x])


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def load_canon():
    return load_json(TEMPLATES / "fabric-iq-canon.json")


def load_patterns():
    return load_json(TEMPLATES / "ontology-patterns.json")


def load_cdm():
    return load_json(TEMPLATES / "cdm-map.json")


def snake(text) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", str(text or ""))
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "x"


def guess_role(e: dict) -> str:
    """Fact for events and transactions (a datetime property), dimension for business entities."""
    if e.get("event"):
        return "fact"
    return "fact" if any(p.get("type") == "datetime" for p in as_list(e.get("properties"))) and not e.get("base") else "dimension"


def standard_text(st: dict) -> str:
    st = st or {}
    k = st.get("standard")
    if k == "cdm":
        return f"Common Data Model: {st.get('entity')}" + (f" (Dataverse table {st['table']})" if st.get("table") else "")
    if k == "dataverse":
        return f"Dataverse, {st.get('folder') or 'Dynamics 365'}: {st.get('entity')}" + (f" ({st['table']})" if st.get("table") else "")
    if k == "operations":
        return f"Common Data Model, finance and operations: {st.get('entity')}"
    return "Custom extension (no standard entity)"


def slug(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", str(text or "").strip().lower()).strip("-")
    return s or "x"


def pascal(text: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", str(text or ""))
    s = "".join(p[:1].upper() + p[1:] for p in parts)
    return s if s and s[0].isalpha() else ("E" + s if s else "Entity")


def camel(text: str) -> str:
    p = pascal(text)
    return p[:1].lower() + p[1:]


def ptype(t) -> str:
    t = str(t or "string").strip().lower()
    return t if t in TYPES else TYPE_ALIASES.get(t, "")


def text_of(*parts) -> str:
    out = []
    for p in parts:
        if isinstance(p, dict):
            out.append(" ".join(str(v) for v in p.values() if isinstance(v, (str, int, float))))
        elif isinstance(p, list):
            out.append(" ".join(text_of(x) for x in p))
        elif p is not None:
            out.append(str(p))
    return " ".join(out)


def business_domains(bp: dict) -> list:
    return [d for d in as_list((bp or {}).get("domains")) if isinstance(d, dict) and d.get("kind") != "factory"]


def agent_ids(bp: dict) -> dict:
    out = {}
    for d in as_list((bp or {}).get("domains")):
        if not isinstance(d, dict):
            continue
        for a in ([d["orchestrator"]] if isinstance(d.get("orchestrator"), dict) else []) + [x for x in as_list(d.get("agents")) if isinstance(x, dict)]:
            if a.get("id"):
                out[a["id"]] = a
    return out


def sap_source(source: dict) -> bool:
    return bool(SAP.search(text_of(source.get("name"), source.get("system"), source.get("id"))))


def new_route_assessment(source: dict, canon: dict) -> dict:
    assessment = copy.deepcopy(canon["sap_route_assessment"])
    name = text_of(source.get("name"), source.get("system"), source.get("id"))
    if re.search(r"ariba", name, re.I) or not re.search(r"\bs/?4(?:hana)?\b|ecc|erp|datasphere|\bhana\b|\bbw\b", name, re.I):
        assessment["candidate_path"] = None
    return assessment


def assess_route(source: dict, bp: dict | None, canon: dict, rep: Rep) -> None:
    """Derive an owner-asserted design assessment, never tenant/licence readiness."""
    assessment = source.get("route_assessment")
    if "route_assessment" not in source:
        assessment = source["route_assessment"] = new_route_assessment(source, canon)
    prefix = f"source {source['id']} route_assessment"
    if not isinstance(assessment, dict):
        rep.err(f"{prefix} must be an object")
        return
    assessment["state"] = "conditional"
    prerequisites = assessment.get("prerequisites")
    expected = canon["sap_route_assessment"]["prerequisites"]
    if not isinstance(prerequisites, dict) or set(prerequisites) != set(expected):
        rep.err(f"{prefix} prerequisites must contain exactly {', '.join(expected)}")
        return
    errors_before = len(rep.errors)

    def refs_valid(value):
        return isinstance(value, list) and all(isinstance(ref, str) and ref.strip() for ref in value)

    if assessment.get("candidate_path") not in (None, "mirroring"):
        rep.err(f"{prefix} candidate_path must be mirroring or null")
    else:
        assessment["candidate_path"] = new_route_assessment(source, canon)["candidate_path"]
    if not isinstance(assessment.get("commercial_note"), str) or not refs_valid(assessment.get("src")):
        rep.err(f"{prefix} requires commercial_note text and a src reference list")
    estate = {row["id"]: row for row in as_list((bp or {}).get("evidence"))
              if isinstance(row, dict) and isinstance(row.get("id"), str)
              and (row.get("type") == "estate" or row["id"].startswith("ESTATE-"))
              and row.get("type") not in ("public", "documentation")
              and not str(row.get("url") or "").startswith(("https://learn.microsoft.com/", "https://techcommunity.microsoft.com/"))}
    complete = True
    for key, record in prerequisites.items():
        if (not isinstance(record, dict) or record.get("status") not in ("unknown", "confirmed", "unsupported")
                or not isinstance(record.get("note"), str) or not refs_valid(record.get("src"))):
            rep.err(f"{prefix} prerequisite {key} requires status, note text and a src reference list")
            complete = False
            continue
        confirmed = (record["status"] == "confirmed" and bool(record["note"].strip())
                     and bool(record["src"]) and all(ref in estate for ref in record["src"]))
        if not confirmed:
            rep.warn(f"source {source['id']} route prerequisite {key}: {record['status']}; estate confirmation required")
            complete = False
    path = source.get("path")
    chosen = (isinstance(path, str) and path in canon["paths"] and path != "unresolved"
              and "item" in source and source["item"] == canon["paths"][path]["item"])
    owner = source.get("owner")
    named_owner = isinstance(owner, str) and owner.strip().lower() not in ("", "unknown", "to confirm", "tbc", "tbd", "unassigned", "none")
    if complete and chosen and named_owner and len(rep.errors) == errors_before:
        assessment["state"] = "owner_confirmed"
    else:
        rep.warn(f"source {source['id']} route is conditional; recorded choices are not binding or publication proof")


def conditional_source(source: dict) -> bool:
    assessment = source.get("route_assessment")
    return (source.get("path") == "unresolved" or (bool(source.get("id")) and source.get("item") is None) or
            ("route_assessment" in source and
             (not isinstance(assessment, dict) or assessment.get("state") != "owner_confirmed")))


def source_route_gaps(entities: list, sources: dict) -> list[str]:
    ids = {sid for entity in entities for sid in [entity.get("source"), *as_list(entity.get("secondary"))]
           if isinstance(sid, str) and sid in sources and conditional_source(sources[sid])}
    return [f"source route {sid}: conditional" for sid in sorted(ids)]


# --------------------------------------------------------------------------- normalise and check

def private_content(obj: dict, bp: dict | None = None) -> bool:
    """Visibility is independent of a later public workshop citation."""
    private_ids = {e.get("id") for e in as_list((bp or {}).get("evidence"))
                   if isinstance(e, dict) and (e.get("internal") is True or str(e.get("visibility", "")).lower() == "internal")}
    refs = as_list(obj.get("content_src", obj.get("src")))
    return (obj.get("internal") is True or str(obj.get("visibility", "")).lower() == "internal"
            or bool(refs and all(isinstance(s, str) and s in private_ids for s in refs))
            or any(private_content(origin, bp) for origin in as_list(obj.get("content_origins")) if isinstance(origin, dict)))


def carry_content(target: dict, *origins: dict, bp: dict | None = None) -> dict:
    """Record each contributing origin independently; a public parent cannot
    launder a private child into public generated text or a binding."""
    provenance = list(as_list(target.get("content_origins")))
    refs = list(as_list(target.get("content_src", target.get("src"))))
    sources = list(as_list(target.get("src")))
    for origin in origins:
        if not isinstance(origin, dict):
            continue
        recorded = {key: copy.deepcopy(origin[key]) for key in ("src", "content_src", "visibility", "internal") if key in origin}
        if recorded and recorded not in provenance:
            provenance.append(recorded)
        for inherited in as_list(origin.get("content_origins")):
            if isinstance(inherited, dict) and inherited not in provenance:
                provenance.append(copy.deepcopy(inherited))
        refs += as_list(origin.get("content_src", origin.get("src")))
        sources += as_list(origin.get("src"))
        if private_content(origin, bp):
            target["internal"] = True
    if provenance:
        target["content_origins"] = provenance
    if refs:
        target["content_src"] = list(dict.fromkeys(refs))
    if sources:
        target["src"] = list(dict.fromkeys(sources))
    return target


def _ancestry_pools(onto: dict, bp: dict | None = None) -> dict:
    pools = {key: {row["id"]: row for row in as_list(onto.get(key)) if isinstance(row, dict) and isinstance(row.get("id"), str)}
             for key in ("entity_types", "relationship_types", "sources", "namespaces", "data_agents", "operations_agents", "data_products",
                         "metrics", "rules", "risks", "readiness", "decisions", "semantic_models")}
    pools["ontology"] = {"model": onto} if onto else {}
    pools["blueprint.domains"] = {d["id"]: d for d in business_domains(bp) if isinstance(d.get("id"), str)}
    pools["blueprint.agents"] = agent_ids(bp)
    return pools


def strict_reference_graph(onto: dict, bp: dict | None = None) -> dict:
    """Opt-in, pure typed-reference validation; never normalise or drop input.

    Nodes/edges use (schema collection, identity), not an any-pool ID lookup.
    Returned node copies may carry the schema's stable implicit identities.
    This does not change the GA normalizer's warnings, output or approval policy.
    Source citations/provenance remain owned by the caller's evidence registry.
    """
    if not isinstance(onto, dict) or (bp is not None and not isinstance(bp, dict)):
        raise ValueError("typed reference inputs must be objects")
    defaults = {"data_agents": "DA", "operations_agents": "OA", "data_products": "DP",
                "semantic_models": "SM", "metrics": "M", "rules": "RU"}
    fields = {
        "namespaces": {"journey": "blueprint.domains"},
        "entity_types": {"namespace": "namespaces", "journeys": "blueprint.domains", "source": "sources",
                         "secondary": "sources", "base": "entity_types"},
        "relationship_types": {"from": "entity_types", "to": "entity_types"},
        "sources": {"journeys": "blueprint.domains"},
        "rules": {"applies_to": "entity_types"},
        "metrics": {"entity": "entity_types", "journey": "blueprint.domains"},
        "data_agents": {"entities": "entity_types", "sources": "sources", "journey": "blueprint.domains"},
        "operations_agents": {"entities": "entity_types", "journeys": "blueprint.domains"},
        "semantic_models": {"facts": "entity_types", "dimensions": "entity_types",
                            "namespace": "namespaces", "journey": "blueprint.domains"},
        "data_products": {"entities": "entity_types", "agents": "data_agents", "journey": "blueprint.domains"},
        "domains": {"namespace": "namespaces", "journey": "blueprint.domains"},
        "risks": {"entity": "entity_types", "entities": "entity_types", "source": "sources", "sources": "sources",
                  "secondary": "sources", "namespace": "namespaces", "data_agents": "data_agents",
                  "operations_agents": "operations_agents", "data_products": "data_products",
                  "journey": "blueprint.domains", "journeys": "blueprint.domains"},
        "readiness": {"journey": "blueprint.domains"},
        "decisions": {"journey": "blueprint.domains"},
    }
    nodes, pools, edges = {}, {}, {}

    def index(pool, rows, implicit=False):
        pools[pool] = set()
        for i, original in enumerate(rows, 1):
            if pool == "rules" and isinstance(original, str):
                original = {"text": original}
            if not isinstance(original, dict):
                raise ValueError("typed collections require object records")
            row = copy.deepcopy(original)
            identity = row.get("id")
            if "id" not in row and implicit:
                identity = (f"{defaults[pool]}-{i:02d}" if pool in defaults else
                            f"{row.get('from')}_{row.get('name', 'relates_to')}_{row.get('to')}"
                            if pool == "relationship_types" else f"@{i}")
                row["id"] = identity
            if not isinstance(identity, str) or not identity.strip() or identity in pools[pool]:
                raise ValueError("typed namespace requires unique nonblank identities")
            pools[pool].add(identity)
            nodes[(pool, identity)] = row
            edges[(pool, identity)] = set()

    for pool in fields:
        index(pool, as_list(onto.get(pool)), implicit=pool not in {"entity_types", "sources", "namespaces"})
    # A parent node is its ownership/provenance header, not an implicit
    # dependency on every sibling agent in that domain.
    index("blueprint.domains", [
        {key: value for key, value in domain.items() if key not in {"agents", "lead", "orchestrator", "data_agent"}}
        for domain in business_domains(bp)
    ])
    index("blueprint.agents", list(agent_ids(bp).values()))

    def link(owner, row, field, target, builtins=()):
        value = row.get(field)
        if value is None or value == "":
            return
        for reference in as_list(value):
            if not isinstance(reference, str) or not reference.strip():
                raise ValueError("typed reference must be a nonblank identity")
            if reference in builtins:
                continue
            if reference not in pools[target]:
                raise ValueError(f"unresolved or wrong-namespace reference to {target}")
            edges[owner].add((target, reference))

    for owner, row in nodes.items():
        pool = owner[0]
        for field, target in fields.get(pool, {}).items():
            builtins = (("ontology",) if (pool, field) == ("data_agents", "sources") else
                        ("Date",) if pool == "semantic_models" and field in {"facts", "dimensions"} else ())
            link(owner, row, field, target, builtins)
        if pool == "data_agents":
            for consumer in as_list(row.get("consumers")):
                consumer = {"kind": consumer} if isinstance(consumer, str) else consumer
                if not isinstance(consumer, dict) or consumer.get("kind") not in CONSUMER_KINDS:
                    raise ValueError("invalid typed data-agent consumer kind")
                link(owner, consumer, "agents", "blueprint.agents")
            for product in as_list(row.get("products")):
                if isinstance(product, str):
                    continue  # the schema also accepts a product's authored name
                if not isinstance(product, dict):
                    raise ValueError("invalid data-agent product definition")
                link(owner, product, "entities", "entity_types")
        if pool == "data_products":
            for use in as_list(row.get("uses")):
                if not isinstance(use, dict) or use.get("use") not in USES:
                    raise ValueError("invalid typed data-product use")
                target = {"analytics": "semantic_models", "grounding": "data_agents",
                          "actions": "operations_agents"}[use["use"]]
                link(owner, use, "via", target)
    return {"nodes": nodes, "edges": {key: tuple(sorted(edges[key])) for key in sorted(edges)}}


def _content_metadata(node: dict) -> dict:
    """Only provenance is snapshotted, never the private descriptive payload."""
    fields = ("src", "content_src", "internal", "visibility", "content_origins")
    metadata = {key: copy.deepcopy(node[key]) for key in fields if key in node}
    def nested(value):
        if isinstance(value, dict):
            origin = {key: copy.deepcopy(value[key]) for key in fields if key in value}
            if origin:
                origins = metadata.setdefault("content_origins", [])
                if origin not in origins:
                    origins.append(origin)
            for key, child in value.items():
                if key not in fields:
                    nested(child)
        elif isinstance(value, list):
            for child in value:
                nested(child)
    for key, value in node.items():
        if key not in fields:
            nested(value)
    return metadata


def feedback_ancestry(onto: dict, ident: str, bp: dict | None = None) -> list[dict]:
    """Persist typed target/dependency anchors so retiring a target cannot
    erase the provenance of a workshop comment."""
    pools = _ancestry_pools(onto, bp)
    targets = [(key, ident) for key in ("entity_types", "relationship_types", "data_agents", "operations_agents", "data_products")
               if ident in pools[key]]
    if ident == "model":
        targets = [("ontology", "model")]
    queue = targets[:]
    rows = {("ontology", "model"): {"pool": "ontology", "id": "model",
            **{key: copy.deepcopy(onto[key]) for key in ("src", "content_src", "internal", "visibility", "content_origins") if key in onto}}}
    seen = set()
    references = ("entity", "entities", "source", "sources", "secondary", "namespace", "base", "from", "to",
                  "applies_to", "agents", "data_agents", "operations_agents", "data_products", "journey", "journeys", "via",
                  "facts", "dimensions")
    while queue:
        pool, key = queue.pop(0)
        if (pool, key) in seen:
            continue
        seen.add((pool, key))
        node = pools[pool].get(key)
        if node is None:
            rows[(pool, key)] = {"pool": pool, "id": key, "unresolved": True}
            continue
        # The root anchor is not all unrelated contents of the ontology.
        metadata = (_content_metadata(node) if pool not in ("ontology", "blueprint.domains") or (pool == "ontology" and ident == "model")
                    else {field: copy.deepcopy(node[field]) for field in ("src", "content_src", "internal", "visibility", "content_origins") if field in node})
        rows[(pool, key)] = {"pool": pool, "id": key, **metadata, "target": (pool, key) in targets}
        if pool == "ontology" and ident == "model":
            queue.extend((p, child) for p in pools if p not in ("ontology", "blueprint.domains", "blueprint.agents") for child in pools[p])
        def discover(value):
            if isinstance(value, dict):
                for field, child in value.items():
                    if field in references:
                        for ref in as_list(child):
                            if not isinstance(ref, str) or ref in ("ontology", "Date"):
                                continue
                            matches = [(p, ref) for p in pools if p != "ontology" and ref in pools[p]]
                            if matches:
                                queue.extend(matches)
                            else:
                                rows[("unresolved", ref)] = {"pool": "unresolved", "id": ref, "unresolved": True}
                    elif field not in ("src", "content_src", "content_origins", "standard"):
                        discover(child)
            elif isinstance(value, list):
                for child in value:
                    discover(child)
        if pool not in ("ontology", "blueprint.domains"):
            discover(node)
    return [rows[key] for key in sorted(rows)]


def feedback_privacy(onto: dict, verdict: dict, bp: dict | None = None) -> tuple[bool, list[str]]:
    """Resolve current restrictions using the retained anchors. Missing target
    alone is retirement; missing dependency ancestry fails closed."""
    pools = _ancestry_pools(onto, bp)
    snapshot = as_list(verdict.get("target_ancestry"))
    if not snapshot:
        current = any(verdict.get("id") in pool for pool in pools.values())
        if not current:
            return True, ["no retained target ancestry"]
        snapshot = feedback_ancestry(onto, verdict["id"], bp)
    restricted = private_content(verdict, bp)
    unresolved = []
    resolved_dependencies = 0
    target_present = False
    for anchor in snapshot:
        if not isinstance(anchor, dict):
            unresolved.append("invalid anchor")
            continue
        restricted = restricted or private_content(anchor, bp)
        pool, ident = anchor.get("pool"), anchor.get("id")
        node = pools.get(pool, {}).get(ident)
        if node is None:
            if not anchor.get("target"):
                unresolved.append(f"{pool}:{ident}")
            continue
        if anchor.get("target"):
            target_present = True
        elif pool != "ontology":
            resolved_dependencies += 1
        metadata = (_content_metadata(node) if pool not in ("ontology", "blueprint.domains") or (pool == "ontology" and anchor.get("target"))
                    else {field: node[field] for field in ("src", "content_src", "internal", "visibility", "content_origins") if field in node})
        restricted = restricted or private_content(metadata, bp)
    if not target_present and not resolved_dependencies:
        unresolved.append("retired target without resolvable dependencies")
    return restricted or bool(unresolved), unresolved


def risk_ancestors(onto: dict, risk: dict, bp: dict | None = None) -> list[dict]:
    """Current ontology ancestry, also for a workshop-owned retired title.

    The stable source ref identifies its container, not a replacement verdict.
    Retained entity/source refs still restrict old content after a title edit.
    """
    pools = {key: {x.get("id"): x for x in as_list(onto.get(key)) if isinstance(x, dict) and x.get("id")}
             for key in ("risks", "entity_types", "sources", "namespaces", "data_agents", "operations_agents", "data_products")}
    links = {"entities": "entity_types", "entity": "entity_types", "source": "sources", "sources": "sources",
             "secondary": "sources", "namespace": "namespaces", "data_agents": "data_agents",
             "operations_agents": "operations_agents", "data_products": "data_products"}
    domains = {d.get("id"): d for d in business_domains(bp)}
    ref = risk.get("ref") or risk.get("id")
    current = pools["risks"].get(ref)
    queue = [risk] + ([current] if current is not None and current is not risk else [])
    nodes, seen = [onto], set()
    while queue:
        node = queue.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        nodes.append(node)
        for field, pool in links.items():
            for ident in as_list(node.get(field)):
                if isinstance(ident, str) and ident in pools[pool]:
                    queue.append(pools[pool][ident])
        for field in ("journey", "journeys"):
            for ident in as_list(node.get(field)):
                if isinstance(ident, str) and ident in domains:
                    queue.append(domains[ident])
        for field in ("binding", "standard", "properties", "timeseries"):
            queue += [x for x in as_list(node.get(field)) if isinstance(x, dict)]
    return nodes


def inherit_privacy(onto: dict, bp: dict | None = None) -> dict:
    """Carry restrictions through containers and source/entity/consumer dependencies."""
    for source in as_list(onto.get("sources")):
        if not isinstance(source, dict) or not isinstance(source.get("route_assessment"), dict):
            continue
        metadata = _content_metadata(source["route_assessment"])
        origins = [metadata, *as_list(metadata.get("content_origins"))]
        # Malformed reference payloads remain for the explicit route validator;
        # do not hash them or treat them as provenance during projection.
        if all(isinstance(ref, str) for origin in origins if isinstance(origin, dict)
               for field in ("src", "content_src") for ref in as_list(origin.get(field))):
            # Each prerequisite reference contributes independently. Appending
            # public route documentation must not dilute a private estate ref.
            references = [{"src": [ref]} for origin in origins if isinstance(origin, dict)
                          for ref in as_list(origin.get("content_src", origin.get("src")))]
            carry_content(source, metadata, *references, bp=bp)
    # Resolve the same stable default IDs used by normalize before projection.
    # Otherwise a via:DA-01 link loses its private target while that target is
    # still anonymous in authored input.
    for key, prefix in (("data_agents", "DA"), ("operations_agents", "OA"), ("data_products", "DP"), ("semantic_models", "SM"), ("metrics", "M")):
        for index, row in enumerate(as_list(onto.get(key)), start=1):
            if isinstance(row, dict):
                row.setdefault("id", f"{prefix}-{index:02d}")
    def visit(value):
        if isinstance(value, dict):
            if private_content(value, bp):
                value["internal"] = True
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(onto)
    if private_content(onto, bp):
        for rows in onto.values():
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict):
                        row["internal"] = True
    # A generated model/product/instruction can repeat a dependency's names or
    # bindings. Restrict the whole dependent row, not just its source IDs.
    while True:
        private_ids = {row.get("id") for key in ("sources", "namespaces", "entity_types", "data_agents", "operations_agents", "metrics", "semantic_models")
                       for row in as_list(onto.get(key)) if isinstance(row, dict) and private_content(row, bp)}
        private_ids |= {d.get("id") for d in business_domains(bp) if private_content(d, bp)}
        changed = False
        for risk in as_list(onto.get("risks")):
            if isinstance(risk, dict) and risk.get("internal") is not True and any(private_content(node, bp) for node in risk_ancestors(onto, risk, bp)):
                risk["internal"] = True
                changed = True
        for key in ("namespaces", "sources", "entity_types", "relationship_types", "rules", "metrics", "data_agents", "operations_agents", "data_products", "semantic_models", "domains"):
            for row in as_list(onto.get(key)):
                if not isinstance(row, dict) or row.get("internal") is True:
                    continue
                refs = []
                for field in ("source", "secondary", "namespace", "journey", "journeys", "base", "from", "to", "entities", "entity", "agents", "sources", "applies_to", "facts", "dimensions"):
                    refs += as_list(row.get(field))
                if key == "data_products":
                    refs += [ref for use in as_list(row.get("uses")) if isinstance(use, dict) for ref in as_list(use.get("via"))]
                if any(isinstance(ref, str) and ref in private_ids for ref in refs):
                    row["internal"] = True
                    changed = True
        if not changed:
            return onto


def customer_ontology(onto: dict, bp: dict | None = None) -> dict | None:
    """Project authored content before regenerating derived customer artifacts."""
    o = inherit_privacy(copy.deepcopy(onto), bp)
    if private_content(o, bp):
        return None

    def scrub(value):
        if isinstance(value, dict):
            return {k: scrub(v) for k, v in value.items()
                    if k not in ("internal_notes", "instructions_default")
                    and not (isinstance(v, dict) and private_content(v, bp))}
        if isinstance(value, list):
            return [scrub(v) for v in value if not (isinstance(v, dict) and private_content(v, bp))]
        return value

    o = scrub(o)
    # Blueprint's generic customer scrub compacts empty reference lists.
    # Restore only absent references on explicitly unconfirmed records; never
    # repair a supplied malformed list or a confirmed assertion.
    for source in as_list(o.get("sources")):
        assessment = source.get("route_assessment") if isinstance(source, dict) else None
        prerequisites = assessment.get("prerequisites") if isinstance(assessment, dict) else None
        if isinstance(prerequisites, dict):
            for record in prerequisites.values():
                if isinstance(record, dict) and record.get("status") in ("unknown", "unsupported"):
                    record.setdefault("src", [])
    # Never reuse projected material that was derived from the internal model.
    for key in ("domains", "process", "stats"):
        o.pop(key, None)
    for key in ("data_products", "semantic_models"):
        o[key] = [row for row in as_list(o.get(key)) if row.get("origin") not in ("data agent", "derived")]
    return o


def customer_context(bp: dict) -> dict:
    """Sanitise blueprint context before it can be quoted by standalone designs."""
    def scrub(value):
        if isinstance(value, dict):
            return {k: scrub(v) for k, v in value.items() if k != "internal_notes"
                    and not (isinstance(v, dict) and private_content(v, bp))}
        if isinstance(value, list):
            return [scrub(v) for v in value if not (isinstance(v, dict) and private_content(v, bp))]
        return value
    return scrub(bp)


def normalize(onto: dict, bp: dict | None = None, rep: Rep | None = None, canon: dict | None = None) -> dict:
    """Checks the model against the Fabric ontology (preview) rules and completes defaults. Returns a new dict."""
    rep = rep or Rep()
    canon = canon or load_canon()
    if not isinstance(onto, dict):
        rep.err("ontology must be an object")
        return {"schema": SCHEMA, "stats": {}}
    o = inherit_privacy(copy.deepcopy(onto), bp)
    if o.get("schema") not in (None, SCHEMA):
        rep.warn(f"schema {o.get('schema')!r} is not {SCHEMA}; read as {SCHEMA}")
    o["schema"] = SCHEMA
    if "meta" in o and not isinstance(o["meta"], dict):
        rep.err("ontology meta must be an object")
        o["meta"] = {}
    meta = o.setdefault("meta", {})
    if bp:
        bm = bp.get("meta") or {}
        meta.setdefault("customer", bm.get("customer"))
        meta.setdefault("short", bm.get("short"))
        meta.setdefault("blueprint", bm.get("id"))
    meta.setdefault("version", "0.1")
    meta.setdefault("status", "hypothesis")
    meta.setdefault("date", canon.get("checked") or "undated")
    o.setdefault("title", f"{meta.get('short') or meta.get('customer') or 'Customer'} process ontology")
    doms = {d.get("id"): d for d in business_domains(bp)} if bp else {}
    agents = agent_ids(bp) if bp else {}

    # namespaces
    ns_ids = []
    for n in as_list(o.get("namespaces")):
        if not isinstance(n, dict) or not n.get("id"):
            rep.err("namespace without id")
            continue
        if n["id"] in ns_ids:
            rep.err(f"duplicate namespace {n['id']!r}")
        ns_ids.append(n["id"])
        if n.get("journey") and doms and n["journey"] not in doms:
            rep.warn(f"namespace {n['id']!r} names an unknown journey {n['journey']!r}")
    o["namespaces"] = [n for n in as_list(o.get("namespaces")) if isinstance(n, dict) and n.get("id")]

    # entity types
    ents, seen = [], set()
    ptypes = {}
    for e in as_list(o.get("entity_types")):
        if not isinstance(e, dict):
            rep.err("entity type is not an object")
            continue
        eid = str(e.get("id") or "")
        if not NAME_RE.match(eid):
            rep.err(f"entity type id {eid!r} must start with a letter and use letters, digits or _ only")
            continue
        if eid in seen:
            rep.err(f"duplicate entity type {eid!r}")
            continue
        seen.add(eid)
        e.setdefault("name", eid)
        e["synonyms"] = [str(s) for s in as_list(e.get("synonyms")) if s]
        if e.get("namespace") and ns_ids and e["namespace"] not in ns_ids:
            rep.warn(f"entity type {eid} is in an unknown namespace {e['namespace']!r}")
        props, pn = [], set()
        for p in as_list(e.get("properties")):
            if not isinstance(p, dict) or not p.get("name"):
                rep.err(f"entity type {eid} has a property without a name")
                continue
            if not NAME_RE.match(str(p["name"])):
                rep.err(f"property {eid}.{p['name']!r} must start with a letter and use letters, digits or _ only")
                continue
            t = ptype(p.get("type"))
            if not t:
                rep.err(f"property {eid}.{p['name']} type {p.get('type')!r} is not supported by ontology (preview)")
                t = "string"
            p["type"] = t
            if p["name"] in pn:
                rep.err(f"entity type {eid} has the property {p['name']!r} twice")
                continue
            pn.add(p["name"])
            props.append(p)
        ts = []
        for p in as_list(e.get("timeseries")):
            if not isinstance(p, dict) or not p.get("name") or not NAME_RE.match(str(p.get("name"))):
                rep.err(f"entity type {eid} has an invalid time-series property")
                continue
            t = ptype(p.get("type"))
            if not t:
                rep.err(f"time-series property {eid}.{p['name']} type {p.get('type')!r} is not supported by ontology (preview)")
            p["type"] = t or "double"
            if p["name"] in pn:
                rep.err(f"entity type {eid} has the property {p['name']!r} as static and as time series")
                continue
            pn.add(p["name"])
            ts.append(p)
        e["properties"], e["timeseries"] = props, ts
        for p in props + ts:
            prev = ptypes.get(p["name"])
            if prev and prev[0] != p["type"]:
                rep.err(f"property name {p['name']!r} is {prev[0]} on {prev[1]} and {p['type']} on {eid}: ontology (preview) reuses a property name only with the same type")
            else:
                ptypes.setdefault(p["name"], (p["type"], eid))
        keys = [str(k) for k in as_list(e.get("key"))]
        if len(keys) != len(set(keys)):
            rep.err(f"entity type {eid} has a duplicate key property")
        for k in keys:
            kp = next((p for p in props if p["name"] == k), None)
            if kp is None:
                rep.err(f"key {eid}.{k} is not a static property of the entity type")
            elif kp["type"] not in KEY_TYPES:
                rep.err(f"key {eid}.{k} is {kp['type']}: an entity type key must be string or integer")
        if not keys:
            rep.warn(f"entity type {eid} has no key: keyless entity types can't identify instances across sources")
        e["key"] = keys
        e["journeys"] = [j for j in as_list(e.get("journeys")) if j]
        for j in e["journeys"]:
            if doms and j not in doms:
                rep.warn(f"entity type {eid} names an unknown journey {j!r}")
        st = str(e.get("status") or "hypothesis").lower()
        e["status"] = st if st in STATUS else "hypothesis"
        e["src"] = [s for s in as_list(e.get("src")) if s]
        ents.append(e)
    by_id = {e["id"]: e for e in ents}
    for e in ents:
        if e.get("base"):
            if e["base"] not in by_id:
                rep.err(f"entity type {e['id']} inherits from an unknown entity type {e['base']!r}")
                e["base"] = None
        seen_chain, cur = set(), e
        while cur and cur.get("base"):
            if cur["id"] in seen_chain:
                rep.err(f"inheritance cycle at {e['id']}")
                e["base"] = None
                break
            seen_chain.add(cur["id"])
            cur = by_id.get(cur["base"])
    o["entity_types"] = ents

    # relationship types
    rels, rids = [], set()
    for r in as_list(o.get("relationship_types")):
        if not isinstance(r, dict):
            continue
        fr, to = r.get("from"), r.get("to")
        if fr not in by_id or to not in by_id:
            rep.err(f"relationship {r.get('name') or r.get('id')!r} connects unknown entity types {fr!r} -> {to!r}")
            continue
        r.setdefault("name", "relates_to")
        if not NAME_RE.match(str(r["name"])):
            rep.err(f"relationship name {r['name']!r} must start with a letter and use letters, digits or _ only")
            continue
        r.setdefault("id", f"{fr}_{r['name']}_{to}")
        if not NAME_RE.match(str(r["id"])):
            rep.err(f"relationship id {r['id']!r} must start with a letter and use letters, digits or _ only")
            continue
        if r["id"] in rids:
            rep.err(f"duplicate relationship type {r['id']!r}")
            continue
        rids.add(r["id"])
        c = str(r.get("cardinality") or "n:1").lower()
        if c not in CARD:
            rep.err(f"relationship {r['id']} cardinality {r.get('cardinality')!r} should be one of {', '.join(CARD)}")
            c = "n:1"
        r["cardinality"] = c
        st = str(r.get("status") or "hypothesis").lower()
        r["status"] = st if st in STATUS else "hypothesis"
        rels.append(r)
    names = {}
    for r in rels:
        names.setdefault(r["name"], []).append(r)
    for r in rels:
        base = r["name"].replace("_", " ")
        r["label"] = base if len(names[r["name"]]) == 1 else f"{base} {by_id[r['to']]['name'].lower()}"
    o["relationship_types"] = rels
    identities = set(by_id)
    for eid in [f"{e['id']}_{p['name']}" for e in ents for p in e["properties"] + e["timeseries"]] + [r["id"] for r in rels]:
        if eid in identities:
            rep.err(f"RDF identifier {eid!r} is used by more than one class/property")
        identities.add(eid)

    # sources (OneLake)
    srcs, sids = [], set()
    items = set(canon.get("binding_sources", []))
    for s in as_list(o.get("sources")):
        if not isinstance(s, dict) or not s.get("id"):
            rep.err("OneLake source without id")
            continue
        if s["id"] in sids:
            rep.err(f"duplicate source {s['id']!r}")
            continue
        sids.add(s["id"])
        path = str(s.get("path") or "")
        if sap_source(s) or "route_assessment" in s:
            assess_route(s, bp, canon, rep)
        if path not in canon.get("paths", {}):
            rep.warn(f"source {s['id']} path {path!r} should be one of {', '.join(canon.get('paths', {}))}")
        s.setdefault("item", None if sap_source(s) or "route_assessment" in s else (canon.get("paths", {}).get(path) or {}).get("item"))
        if s["item"] not in items and path != "unresolved":
            rep.warn(f"source {s['id']} item {s['item']!r} is not a supported binding source ({', '.join(sorted(items))})")
        default_status = "later" if conditional_source(s) else "next"
        st = str(s.get("status") or default_status).lower()
        s["status"] = st if st in SOURCE_STATUS else default_status
        srcs.append(s)
    o["sources"] = srcs
    sby = {s["id"]: s for s in srcs}
    for e in ents:
        sid = e.get("source")
        if sid and sid not in sby:
            rep.err(f"entity type {e['id']} is bound to an unknown source {sid!r}")
            e["source"] = None
        for x in as_list(e.get("secondary")):
            if x not in sby:
                rep.err(f"entity type {e['id']} names an unknown secondary source {x!r}")
        if not e.get("source"):
            rep.warn(f"entity type {e['id']} has no data binding yet")
        if e.get("timeseries") and e.get("source") and sby[e["source"]]["item"] not in ("eventhouse", "KQL database", "lakehouse"):
            rep.warn(f"entity type {e['id']} has time series bound to a {sby[e['source']]['item']}: time series bind from OneLake or an eventhouse")

    # Microsoft standard entity (Common Data Model) and the silver-layer binding of each entity type
    cmap = load_cdm().get("entities", {})
    mapping_sources = {s.get("id") for s in as_list(canon.get("sources")) + as_list(o.get("sources_doc"))
                       if isinstance(s, dict) and isinstance(s.get("id"), str)}
    naming = (canon.get("data_architecture") or {}).get("naming") or {"silver": "{ns}_silver", "gold": "{ns}_gold", "events": "{ns}_events"}
    for e in ents:
        st = e.get("standard")
        mapping_errors = len(rep.errors)
        automatic_standard = not isinstance(st, dict) or not st
        if not isinstance(st, dict) or not st:
            tpl = cmap.get(e["id"])
            st = copy.deepcopy(tpl) if tpl else {"standard": "custom", "entity": e.get("name"), "match": "custom", "attributes": {}, "src": [], "checked": False,
                                                  "note": "No standard entity proposed yet: confirm with the data owner whether a Common Data Model entity fits."}
            st["origin"] = "map" if tpl else "default"
        if st.get("standard") not in STANDARDS:
            rep.warn(f"entity type {e['id']} standard {st.get('standard')!r} should be one of {', '.join(STANDARDS)}; custom is used")
            st["standard"] = "custom"
        if st.get("match") not in MATCH:
            st["match"] = "custom" if st["standard"] == "custom" else "related"
        if st["standard"] == "custom":
            st["match"] = "custom"
        if st.get("role") not in ROLES:
            st["role"] = guess_role(e)
        pnames = {p["name"] for p in e["properties"] + e["timeseries"]}
        attrs = {}
        if "attributes" in st and not isinstance(st["attributes"], dict):
            rep.err(f"entity type {e['id']} standard attributes must be an object")
            st["attributes"] = {}
        for k, v in (st.get("attributes") or {}).items():
            if k in pnames and v:
                attrs[k] = str(v)
            elif k not in pnames and not automatic_standard:
                rep.warn(f"entity type {e['id']} maps an unknown property {k!r} to the standard attribute {v!r}")
                st["checked"] = False
        st["attributes"] = attrs
        st["mapped"] = len(attrs)
        st["of"] = len(e["properties"])
        st["src"] = [s for s in as_list(st.get("src")) if s]
        if "checked" in st and not isinstance(st["checked"], bool):
            rep.err(f"entity type {e['id']} standard checked must be a boolean, not a verification claim")
        if st["standard"] != "custom":
            for field in ("entity", "table"):
                if not isinstance(st.get(field), str) or not st[field].strip():
                    rep.err(f"entity type {e['id']} noncustom standard requires {field}")
            if not st["src"]:
                rep.err(f"entity type {e['id']} noncustom standard requires source references")
            for ref in st["src"]:
                if not isinstance(ref, str) or ref not in mapping_sources:
                    rep.err(f"entity type {e['id']} standard cites unknown source {ref!r}")
        st["checked"] = st.get("checked") is True and len(rep.errors) == mapping_errors
        e["standard"] = st
        ns = e.get("namespace") or "core"
        b = e.get("binding")
        item = (sby.get(e.get("source")) or {}).get("item")
        conditional = conditional_source(sby.get(e.get("source")) or {})
        if not isinstance(b, dict) or not b.get("table"):
            if conditional:
                b = {"layer": "silver", "item": None, "table": None}
            elif item == "semantic model":
                b = {"layer": "gold", "item": "semantic model", "table": e.get("table") or e.get("name") or e["id"]}
            elif e.get("event"):
                b = {"layer": "silver", "item": "eventhouse", "table": naming["events"].format(ns=ns) + "." + snake(e["id"])}
            else:
                b = {"layer": "silver", "item": "lakehouse", "table": naming["silver"].format(ns=ns) + "." + snake(e["id"])}
            b["origin"] = "default"
        if b.get("layer") not in LAYERS:
            rep.warn(f"entity type {e['id']} binds to layer {b.get('layer')!r}; one of {', '.join(LAYERS)} is expected (silver is used)")
            b["layer"] = "silver"
        if b.get("item") not in items and not (conditional and b.get("item") is None):
            rep.warn(f"entity type {e['id']} binds to a {b.get('item')!r}, which is not a supported binding source")
        if e.get("timeseries") and not b.get("timeseries_table"):
            live = [sby[x] for x in as_list(e.get("secondary")) + [e.get("source")] if x in sby and sby[x].get("item") == "eventhouse"]
            lj = as_list(live[0].get("journeys"))[:1] if live else []
            lns = next((n["id"] for n in o["namespaces"] if lj and n.get("journey") == lj[0]), ns)
            b["timeseries_table"] = naming["events"].format(ns=lns) + "." + snake(e["id"]) + "_telemetry"
        e["binding"] = b

    # rules and metrics
    rules = []
    for i, r in enumerate(as_list(o.get("rules")), start=1):
        if isinstance(r, str):
            r = {"text": r}
        if not isinstance(r, dict) or not str(r.get("text") or "").strip():
            rep.warn("rule without text skipped")
            continue
        r.setdefault("id", f"RU-{i:02d}")
        r["applies_to"] = [x for x in as_list(r.get("applies_to")) if x]
        for x in r["applies_to"]:
            if x not in by_id:
                rep.warn(f"rule {r['id']} applies to an unknown entity type {x!r}")
        rules.append(r)
    o["rules"] = rules
    mets = []
    for i, m in enumerate(as_list(o.get("metrics")), start=1):
        if not isinstance(m, dict) or not m.get("name"):
            continue
        m.setdefault("id", f"M-{i:02d}")
        if m.get("entity") and m["entity"] not in by_id:
            rep.err(f"metric {m['id']} belongs to an unknown entity type {m['entity']!r}")
            m["entity"] = None
        m.setdefault("status", "from semantic model" if m.get("measure") and m.get("semantic_model") else "to define")
        mets.append(m)
    o["metrics"] = mets

    # data agents and operations agents
    maxs = int(canon.get("data_agent_max_sources", 5))
    used_ent = {}
    das = []
    for i, a in enumerate(as_list(o.get("data_agents")), start=1):
        if not isinstance(a, dict):
            continue
        a.setdefault("id", f"DA-{i:02d}")
        a.setdefault("name", f"Data agent {i}")
        a["entities"] = [x for x in as_list(a.get("entities")) if x]
        for x in a["entities"]:
            if x not in by_id:
                rep.err(f"data agent {a['id']} uses an unknown entity type {x!r}")
            used_ent.setdefault(x, []).append(a["id"])
        a["sources"] = [x for x in as_list(a.get("sources")) if x] or ["ontology"]
        if len(a["sources"]) > maxs:
            rep.err(f"data agent {a['id']} has {len(a['sources'])} sources: a Fabric data agent uses up to {maxs}")
        for x in a["sources"]:
            if x != "ontology" and x not in sby:
                rep.err(f"data agent {a['id']} names an unknown source {x!r}")
        cons = []
        for c in as_list(a.get("consumers")):
            c = {"kind": c} if isinstance(c, str) else c
            if not isinstance(c, dict) or c.get("kind") not in CONSUMER_KINDS:
                rep.warn(f"data agent {a['id']} consumer {c!r} should be one of {', '.join(CONSUMER_KINDS)}")
                continue
            c["agents"] = [x for x in as_list(c.get("agents")) if x]
            for x in c["agents"]:
                if agents and x not in agents:
                    rep.warn(f"data agent {a['id']} names an unknown blueprint agent {x!r}")
            cons.append(c)
        a["consumers"] = cons
        qs, seen = [], {}
        for q in as_list(a.get("questions")):
            if not q:
                continue
            q = q if isinstance(q, dict) else {"q": str(q)}
            k = " ".join(str(q.get("q") or "").lower().split())
            if k in seen:
                first = seen[k]
                preferred = q.get("query") and q.get("verified") is True and first.get("verified") is not True
                if preferred or (q.get("query") and not first.get("query")):
                    for f in ("language", "query", "verified", "src", "content_src", "visibility", "internal"):
                        if f in q:
                            first[f] = copy.deepcopy(q[f])
                        elif preferred:
                            first.pop(f, None)
                rep.warn(f"data agent {a['id']}: duplicate example question merged: {q.get('q')!r}")
                continue
            seen[k] = q
            qs.append(q)
        a["questions"] = qs
        st = str(a.get("status") or "hypothesis").lower()
        a["status"] = st if st in STATUS else "hypothesis"
        if any(sby.get(e.get("source"), {}).get("item") == "semantic model" for e in ents if e["id"] in a["entities"]):
            rep.warn(f"data agent {a['id']} uses entity types bound to a semantic model: known issue, data agents don't work with an ontology that uses semantic models for binding (R-ONT-2)")
        das.append(a)
    o["data_agents"] = das
    oas = []
    for i, a in enumerate(as_list(o.get("operations_agents")), start=1):
        if not isinstance(a, dict):
            continue
        a.setdefault("id", f"OA-{i:02d}")
        a.setdefault("name", f"Operations agent {i}")
        a["entities"] = [x for x in as_list(a.get("entities")) if x]
        for x in a["entities"]:
            if x not in by_id:
                rep.err(f"operations agent {a['id']} monitors an unknown entity type {x!r}")
        a["rules"] = [str(x) for x in as_list(a.get("rules")) if x]
        if not a["rules"]:
            rep.warn(f"operations agent {a['id']} has no rule in natural language")
        acts = []
        for x in as_list(a.get("actions")):
            x = {"name": x} if isinstance(x, str) else x
            if isinstance(x, dict) and x.get("name"):
                x["params"] = [str(p) for p in as_list(x.get("params"))]
                acts.append(x)
        a["actions"] = acts
        a.setdefault("notify", "Microsoft Teams")
        st = str(a.get("status") or "hypothesis").lower()
        a["status"] = st if st in STATUS else "hypothesis"
        oas.append(a)
    o["operations_agents"] = oas

    # domains, semantic models and data products (the data architecture under the ontology)
    arch = canon.get("data_architecture") or {}
    pv = (arch.get("domains") or {}).get("purview") or {"core": "Data domain", "journey": "Functional unit"}
    nsby = {n["id"]: n for n in o["namespaces"]}
    jname = {n.get("journey"): (n.get("name") or n["id"]) for n in o["namespaces"] if n.get("journey")}
    if doms:
        jname.update({k: v.get("journey_name") or v.get("name") or k for k, v in doms.items()})
    domains = [d for d in as_list(o.get("domains")) if isinstance(d, dict)]
    saved_domains = {d.get("id") for d in domains}
    for n in o["namespaces"]:
        if n["id"] in saved_domains:
            continue
        mine = [e for e in ents if (e.get("namespace") or "core") == n["id"]]
        domains.append({"id": n["id"], "name": n.get("name") or n["id"], "journey": n.get("journey"), "fabric_domain": n.get("name") or n["id"],
                        "governance_domain": pv["journey"] if n.get("journey") else pv["core"], "owner": n.get("owner"),
                        "silver": naming["silver"].format(ns=n["id"]), "gold": naming["gold"].format(ns=n["id"]) if n.get("journey") else None,
                        "events": naming["events"].format(ns=n["id"]) if any(str((e.get("binding") or {}).get(k) or "").startswith(naming["events"].format(ns=n["id"]) + ".")
                                                                               for e in ents for k in ("table", "timeseries_table")) else None,
                        "entities": [e["id"] for e in mine], "origin": "derived"})
    o["domains"] = domains
    sms = [m for m in as_list(o.get("semantic_models")) if isinstance(m, dict)]
    if not sms:
        for n in o["namespaces"]:
            j = n.get("journey")
            if not j:
                continue
            inj = [e for e in ents if j in e["journeys"]]
            facts = [e["id"] for e in inj if e["standard"]["role"] == "fact"]
            if not facts:
                continue
            meas = [m for m in mets if m.get("journey") == j]
            named = [m.get("semantic_model") for m in meas if m.get("semantic_model")]
            sms.append({"name": min(set(named), key=lambda name: (-named.count(name), name)) if named else f"{n.get('name') or j} model", "journey": j, "namespace": n["id"],
                        "lakehouse": naming["gold"].format(ns=n["id"]), "mode": "Direct Lake on OneLake", "facts": facts,
                        "dimensions": [e["id"] for e in inj if e["standard"]["role"] == "dimension"] + ["Date"],
                        "measures": [{"metric": m["id"], "name": m.get("name"), "measure": m.get("measure"), "status": m.get("status")} for m in meas],
                        "status": "hypothesis", "origin": "derived"})
    for i, m in enumerate(sms, start=1):
        m.setdefault("id", f"SM-{i:02d}")
        m.setdefault("mode", "Direct Lake on OneLake")
        for x in as_list(m.get("facts")) + as_list(m.get("dimensions")):
            if x != "Date" and x not in by_id:
                rep.warn(f"semantic model {m['id']} names an unknown entity type {x!r}")
    o["semantic_models"] = sms
    smj = {m.get("journey"): m for m in sms}
    dps_in = [d for d in as_list(o.get("data_products")) if isinstance(d, dict)]
    if not dps_in:
        for a in das:
            for p in as_list(a.get("products")):
                p = p if isinstance(p, dict) else {"name": str(p)}
                if not p.get("name"):
                    continue
                know = str(p.get("note") or "").startswith("documents")
                dps_in.append(carry_content({"name": p["name"], "journey": a.get("journey"), "entities": list(as_list(p.get("entities"))),
                               "kind": "knowledge" if know else "data product", "agents": [a["id"]], "origin": "data agent"}, a, p, bp=bp))
    std = canon.get("data_product_standard") or {}
    pub = [x["id"] for x in as_list(std.get("publication"))] or ["owner", "purpose", "uses", "access", "quality"]
    use_pools = {"grounding": {a["id"] for a in das}, "actions": {a["id"] for a in oas},
                 "analytics": {m["id"] for m in sms}}
    dps = []
    for i, d in enumerate(dps_in, start=1):
        d.setdefault("id", f"DP-{i:02d}")
        reference_gaps = []
        d["entities"] = [x for x in as_list(d.get("entities")) if x]
        for x in d["entities"]:
            if x not in by_id:
                rep.warn(f"data product {d['id']} names an unknown entity type {x!r}")
                reference_gaps.append(f"unknown entity type {x}")
        d["entities"] = [x for x in d["entities"] if x in by_id]
        ns = next((n["id"] for n in o["namespaces"] if d.get("journey") and n.get("journey") == d.get("journey")), "core")
        d.setdefault("domain", (nsby.get(ns) or {}).get("name") or ns)
        d["kind"] = d.get("kind") if d.get("kind") in ("data product", "knowledge") else "data product"
        st = str(d.get("status") or "hypothesis").lower()
        d["status"] = st if st in STATUS else "hypothesis"
        for agent in as_list(d.get("agents")):
            if not isinstance(agent, str):
                rep.err(f"data product {d['id']} producer agent reference must be text")
                reference_gaps.append("invalid producer agent reference")
            elif agent not in use_pools["grounding"]:
                rep.warn(f"data product {d['id']} has an unknown producer data agent {agent!r}")
                reference_gaps.append(f"unknown producer data agent {agent}")
        if d["kind"] == "knowledge":
            d.setdefault("purpose", "Documents for grounding: they stay in Microsoft 365 or SharePoint and reach the agents through Foundry IQ, not through OneLake")
            d["gaps"] = reference_gaps
            dps.append(d)
            continue
        d.setdefault("owner", (nsby.get(ns) or {}).get("owner"))
        d.setdefault("purpose", f"Trusted {str(d.get('name')).lower()} for the {jname.get(d.get('journey'), d.get('domain'))}: reports and the journey's agents")
        if not as_list(d.get("uses")):
            uses = [{"use": "analytics"}]
            via = [a["id"] for a in das if any(x in a["entities"] for x in d["entities"]) and (not d.get("journey") or a.get("journey") == d.get("journey"))]
            producers = [agent for agent in as_list(d.get("agents")) if isinstance(agent, str)]
            if via or producers:
                uses.append({"use": "grounding", "via": sorted(set(via + producers))})
            act = [a["id"] for a in oas if any(x in a["entities"] for x in d["entities"]) and (not d.get("journey") or d.get("journey") in as_list(a.get("journeys")))]
            if act:
                uses.append({"use": "actions", "via": act, "review": True})
            d["uses"] = uses
        d["uses"] = as_list(d["uses"])
        for u in d["uses"]:
            if not isinstance(u, dict):
                rep.err(f"data product {d['id']} intended use must be an object")
                reference_gaps.append("invalid intended use")
                continue
            if u.get("use") not in USES:
                rep.warn(f"data product {d['id']} use {u.get('use')!r} should be one of {', '.join(USES)}")
                reference_gaps.append(f"unknown intended use {u.get('use')}")
                continue
            kind = u["use"]
            if "via" in u:
                u["via"] = as_list(u["via"])
            refs = as_list(u.get("via"))
            if kind in ("grounding", "actions") and not refs:
                rep.warn(f"data product {d['id']} {kind} has no agent binding")
                reference_gaps.append(f"{kind} agent to define")
            for agent in refs:
                if not isinstance(agent, str):
                    rep.err(f"data product {d['id']} {kind} binding reference must be text")
                    reference_gaps.append(f"invalid {kind} binding reference")
                elif agent not in use_pools[kind]:
                    rep.warn(f"data product {d['id']} {kind} names an unknown {'semantic model' if kind == 'analytics' else 'agent'} {agent!r}")
                    reference_gaps.append(f"unknown {kind} binding {agent}")
            if u.get("use") == "actions":
                u["review"] = True
        d.setdefault("layer", "gold")
        sm = smj.get(d.get("journey"))
        d.setdefault("outputs", [naming["gold"].format(ns=ns) + "." + snake(d.get("name")) if ns != "core" else naming["silver"].format(ns=ns) + "." + snake(d.get("name"))]
                     + ([f"{sm['name']} (semantic model)"] if sm else []) + (["Ontology: " + ", ".join(by_id[x].get("name") or x for x in d["entities"])] if d["entities"] else []))
        classes = [str((sby.get(by_id[x].get("source")) or {}).get("data_class") or "").lower() for x in d["entities"]]
        classes = [c for c in classes if c in SENSITIVITY]
        d.setdefault("sensitivity", max(classes, key=lambda c: SENSITIVITY[c]) if classes else None)
        d.setdefault("endorsement", "promoted")
        d.setdefault("glossary", [by_id[x].get("name") or x for x in d["entities"]])
        d.setdefault("cde", [f"{by_id[x].get('name') or x} ID" for x in d["entities"] if by_id[x].get("key")])
        d["gaps"] = ([x for x in pub if not d.get(x)] + (["entity types to model"] if not d["entities"] else [])
                     + list(dict.fromkeys(reference_gaps)) + source_route_gaps([by_id[x] for x in d["entities"]], sby))
        dps.append(d)
    o["data_products"] = dps
    o["data_architecture"] = o.get("data_architecture") or copy.deepcopy({k: arch.get(k) for k in ("principle", "layers", "intake", "domains", "semantic_models") if arch.get(k)})
    o["data_product_standard"] = o.get("data_product_standard") or copy.deepcopy(std)

    # canon blocks (kept when authored)
    for k in ("readiness", "risks", "decisions"):
        if not o.get(k):
            o[k] = copy.deepcopy(canon.get(k, []))
    o["current_guidance"] = copy.deepcopy(canon["current_guidance"])
    route_gaps = [f"source route {source['id']}: conditional" for source in sorted(srcs, key=lambda source: source["id"])
                  if conditional_source(source)]
    recorded_f06 = next((row for row in as_list(o.get("readiness")) if isinstance(row, dict) and row.get("id") == "F-06"), {})
    o["current_readiness"] = {"F-06": {"status": "open" if route_gaps else recorded_f06.get("status", "open"), "gaps": route_gaps}}
    o["sources_doc"] = o.get("sources_doc") or copy.deepcopy(canon.get("sources", []))
    for citation in canon.get("sources", []):
        if not citation["id"].startswith("G59-"):
            continue
        occupied = [row for row in as_list(o["sources_doc"]) if isinstance(row, dict) and row.get("id") == citation["id"]]
        if occupied and any(row != citation for row in occupied):
            rep.err(f"citation collision for {citation['id']}; saved evidence was not retargeted")
        elif not occupied:
            o["sources_doc"].append(copy.deepcopy(citation))
    o["build_steps"] = o.get("build_steps") or copy.deepcopy(canon.get("build_steps", []))
    o["stack"] = o.get("stack") or copy.deepcopy(canon.get("stack", []))
    if bp:
        o["process"] = process_map(o, bp)
    o["stats"] = {
        "namespaces": len(o["namespaces"]), "entity_types": len(ents), "relationship_types": len(rels),
        "properties": sum(len(e["properties"]) for e in ents), "timeseries": sum(len(e["timeseries"]) for e in ents),
        "rules": len(rules), "metrics": len(mets), "sources": len(srcs),
        "bound": sum(1 for e in ents if e.get("source") and not conditional_source(sby.get(e["source"]) or {})),
        "data_agents": len(das), "operations_agents": len(oas), "validated": sum(1 for e in ents if e["status"] == "validated"),
        "standard": sum(1 for e in ents if e["standard"]["standard"] != "custom"), "custom": sum(1 for e in ents if e["standard"]["standard"] == "custom"),
        "to_verify": sum(1 for e in ents if e["standard"]["standard"] != "custom" and not e["standard"].get("checked")),
        "mapped_properties": sum(e["standard"]["mapped"] for e in ents),
        "data_products": sum(1 for d in dps if d["kind"] == "data product"), "knowledge_products": sum(1 for d in dps if d["kind"] == "knowledge"),
        "data_products_ready": sum(1 for d in dps if d["kind"] == "data product" and not d["gaps"]),
        "semantic_models": len(sms), "domains": len(domains),
    }
    return inherit_privacy(o, bp)


# --------------------------------------------------------------------------- the process on the ontology

def _terms(e: dict) -> list:
    t = [e.get("name") or "", re.sub(r"([a-z])([A-Z])", r"\1 \2", e["id"])] + list(e.get("synonyms") or [])
    out = []
    for x in t:
        x = str(x).strip().lower()
        if len(x) >= 3 and x not in out:
            out.append(x)
    return out


def _hit(e: dict, txt: str) -> bool:
    return any(re.search(r"\b" + re.escape(t) + r"(s|es|d|ed|ing)?\b", txt) for t in _terms(e))


def process_map(onto: dict, bp: dict) -> list:
    """Journey x stage -> entity types the stage touches: the journey's own entity types named in the stage (name or
    synonym), else the shared ones it names, else the journey's entity types in pattern order."""
    ents = as_list(onto.get("entity_types"))
    out = []
    for d in business_domains(bp):
        mine = [e for e in ents if d.get("id") in as_list(e.get("journeys"))]
        stages = [s for s in as_list(d.get("stages")) if isinstance(s, dict)]
        if not stages or not mine:
            continue
        own = [e for e in mine if e.get("namespace") != "core"] or mine
        shared = [e for e in mine if e not in own]
        rows = []
        for j, s in enumerate(stages):
            txt = text_of({k: v for k, v in s.items() if k not in ("agent", "agents", "src", "icons", "id")}).lower()
            hit = [e["id"] for e in own if _hit(e, txt)] or [e["id"] for e in shared if _hit(e, txt)]
            if not hit:
                hit = [e["id"] for i, e in enumerate(own) if (i * len(stages)) // max(1, len(own)) == j]
            rows.append({"stage": s.get("name") or f"Stage {j + 1}", "entities": hit})
        out.append({"journey": d.get("id"), "name": d.get("name"), "stages": rows})
    return out


# --------------------------------------------------------------------------- Turtle (OWL) for Fabric import

def _lit(s) -> str:
    s = str(s if s is not None else "")
    s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return f'"{s}"'


def namespace_uri(onto: dict) -> str:
    meta = onto.get("meta") or {}
    uri = meta.get("namespace_uri")
    if uri and re.match(r"^https?://[^\s<>\"{}|\\^`]+[#/]$", uri):
        return uri
    return f"https://example.org/frontier/{slug(meta.get('short') or meta.get('customer') or 'customer')}/ontology#"


def to_turtle(onto: dict) -> str:
    """Entity types as owl:Class, properties as owl:DatatypeProperty (one per entity type, so names repeat safely),
    relationship types as owl:ObjectProperty; labels, descriptions and synonyms as rdfs:label, rdfs:comment and
    skos:altLabel; inheritance as rdfs:subClassOf. Keys, bindings, rules and metrics are set in Fabric."""
    meta = onto.get("meta") or {}
    L = ["@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
         "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
         "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
         "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
         "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
         f"@prefix : <{namespace_uri(onto)}> .", "",
         f"# {onto.get('title') or 'Process ontology'} v{meta.get('version', '0.1')} ({meta.get('status', 'hypothesis')})",
         "# Generated by the Frontier Envisioning plugin (frontier-process). Import into a new, empty ontology (preview) item.",
         "# Keys, data bindings, rules and metrics are configured in Fabric (see ontology.md).", "",
         f"<{namespace_uri(onto).rstrip('#/')}> a owl:Ontology ;",
         f"  rdfs:label {_lit(onto.get('title') or 'Process ontology')} ;",
         f"  owl:versionInfo {_lit(meta.get('version', '0.1'))} .", ""]
    for e in as_list(onto.get("entity_types")):
        parts = [f":{e['id']} a owl:Class", f"  rdfs:label {_lit(e.get('name') or e['id'])}"]
        desc = str(e.get("description") or "").strip()
        if e.get("key"):
            desc = (desc + " " if desc else "") + "Key: " + ", ".join(e["key"]) + "."
        st = e.get("standard") or {}
        if st:
            desc = (desc + " " if desc else "") + standard_text(st) + "."
        if desc:
            parts.append(f"  rdfs:comment {_lit(desc)}")
        syn = list(e.get("synonyms") or [])
        short = re.sub(r"\s*\(.*?\)", "", str(st.get("entity") or "")).strip()
        if st.get("standard") in ("cdm", "dataverse") and short and short.lower() not in {str(x).lower() for x in syn + [e.get("name"), e["id"]]}:
            syn.append(short)
        if syn:
            parts.append("  skos:altLabel " + ", ".join(_lit(s) for s in syn))
        if e.get("base"):
            parts.append(f"  rdfs:subClassOf :{e['base']}")
        L.append(" ;\n".join(parts) + " .")
        for p in list(e.get("properties") or []) + list(e.get("timeseries") or []):
            pp = [f":{e['id']}_{p['name']} a owl:DatatypeProperty", f"  rdfs:label {_lit(p['name'])}",
                  f"  rdfs:domain :{e['id']}", f"  rdfs:range {XSD.get(p.get('type'), 'xsd:string')}"]
            note = str(p.get("description") or "").strip()
            col = ((e.get("standard") or {}).get("attributes") or {}).get(p["name"])
            if col:
                note = (note + " " if note else "") + f"Standard column: {col}."
            if p in (e.get("timeseries") or []):
                note = (note + " " if note else "") + "Time series" + (f" ({p['unit']})" if p.get("unit") else "") + ": bind with a timestamp column."
            if note:
                pp.append(f"  rdfs:comment {_lit(note)}")
            L.append(" ;\n".join(pp) + " .")
        L.append("")
    for r in as_list(onto.get("relationship_types")):
        rr = [f":{r['id']} a owl:ObjectProperty", f"  rdfs:label {_lit(r.get('label') or r['name'])}",
              f"  rdfs:domain :{r['from']}", f"  rdfs:range :{r['to']}"]
        desc = str(r.get("description") or "").strip()
        desc = (desc + " " if desc else "") + f"Cardinality {r.get('cardinality', 'n:1')}."
        rr.append(f"  rdfs:comment {_lit(desc)}")
        L.append(" ;\n".join(rr) + " .")
    return "\n".join(L).rstrip() + "\n"


# --------------------------------------------------------------------------- Markdown: design document and data agent kit

def _md(x) -> str:
    return str(x if x not in (None, "") else "[To complete]").replace("|", "/").replace("\n", " ")


def _table(cols, rows) -> list:
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(_md(c) for c in r) + " |" for r in rows]
    return out


MERMAID_CARD = {"1:1": "||--||", "1:n": "||--o{", "n:1": "}o--||", "n:n": "}o--o{"}


def mermaid(onto: dict) -> str:
    L = ["erDiagram"]
    for e in as_list(onto.get("entity_types")):
        L.append(f"  {e['id']} {{")
        keys = set(e.get("key") or [])
        for p in list(e.get("properties") or []) + list(e.get("timeseries") or []):
            L.append(f"    {p['type']} {p['name']}{' PK' if p['name'] in keys else ''}")
        L.append("  }")
    for r in as_list(onto.get("relationship_types")):
        L.append(f"  {r['from']} {MERMAID_CARD.get(r.get('cardinality'), '}o--||')} {r['to']} : \"{(r.get('label') or r['name']).replace(chr(34), '')}\"")
    return "\n".join(L)


def _std_line(a: dict, ents: dict) -> str:
    pairs = []
    for x in a.get("entities", []):
        e = ents.get(x) or {}
        st = e.get("standard") or {}
        short = re.sub(r"\s*\(.*?\)", "", str(st.get("entity") or "")).strip()
        if st.get("standard") in ("cdm", "dataverse") and short and short.lower() != str(e.get("name") or "").lower():
            pairs.append(f"{e.get('name')} is {short}")
    if not pairs:
        return "The tables follow the Common Data Model where a standard entity exists."
    return "The tables follow the Common Data Model: " + "; ".join(pairs[:6]) + "."


def default_instructions(a: dict, onto: dict, ents: dict) -> str:
    meta = onto.get("meta") or {}
    who = meta.get("short") or meta.get("customer") or "the company"
    names = ", ".join(ents[x].get("name") or x for x in a.get("entities", []) if x in ents)
    return "\n".join([
        f"You answer questions about {a.get('scope') or a.get('name')} for {who}, using the {onto.get('title') or 'process ontology'}.",
        f"Use the business terms of the ontology: {names}." if names else "Use the business terms of the ontology.",
        _std_line(a, ents),
        "Answer only from the connected sources. When a question needs data you don't have, say so and name the missing data.",
        "You are read-only: never suggest that you changed a record. Actions follow the approval seam of the journey and stay with a person.",
        "Don't evaluate or rank individual people; answer about processes, teams and assets.",
        "Say which entity types, filters and time window you used, and give amounts with their currency.",
        "Support group by in GQL.",
    ])


def data_agent_kit(onto: dict) -> str:
    ents = {e["id"]: e for e in as_list(onto.get("entity_types"))}
    sby = {s["id"]: s for s in as_list(onto.get("sources"))}
    canon = load_canon()
    meta = onto.get("meta") or {}
    L = [f"# Data agent kit: {onto.get('title') or 'Process ontology'}", "",
         f"Version {meta.get('version', '0.1')} ({meta.get('status', 'hypothesis')}). One Fabric data agent per journey, grounded in the ontology "
         "(preview) as its context source. Paste the instructions into **Agent instructions**, mount the underlying sources you want to tune, "
         "and add the example questions with the verified source-native query (SQL, KQL or DAX) as **example queries**. A data agent uses up to "
         f"{canon.get('data_agent_max_sources', 5)} sources and answers with the user's permissions.", ""]
    L += current_guidance_md(onto)
    for a in as_list(onto.get("data_agents")):
        L += [f"## {a['id']} · {a.get('name')}", "", f"**Status** {a.get('status', 'hypothesis')} · **Audience** {_md(a.get('audience'))}", "",
              a.get("description") or "", ""]
        L += ["**Entity types in scope**: " + (", ".join(ents[x].get("name") or x for x in a.get("entities", []) if x in ents) or "[To complete]"), ""]
        L += ["**Sources**", ""]
        for s in a.get("sources", []):
            if s == "ontology":
                L.append(f"- Ontology: {onto.get('title')} (context source; queries run on its bound sources)")
            elif s in sby:
                L.append(f"- {sby[s].get('name')} ({'conditional recorded proposal' if conditional_source(sby[s]) else sby[s].get('item')})")
        L.append("")
        cons = []
        for c in a.get("consumers", []):
            nm = (canon.get("consumers", {}).get(c["kind"]) or {}).get("name", c["kind"])
            cons.append(nm + (f": {', '.join(c['agents'])}" if c.get("agents") else ""))
        L += ["**Consumed by**: " + ("; ".join(cons) or "Fabric only"), "", "### Agent instructions", "", "```text",
              (a.get("instructions") or default_instructions(a, onto, ents)).strip(), "```", ""]
        under = [sby[s] for s in a.get("sources", []) if s in sby and not conditional_source(sby[s])]
        bound = sorted({ents[x].get("source") for x in a.get("entities", [])
                        if x in ents and ents[x].get("source") and not conditional_source(sby.get(ents[x]["source"]) or {})})
        under += [sby[s] for s in bound if s in sby and sby[s] not in under]
        if under:
            L += ["### Data source descriptions (for mounted underlying sources)", ""]
            for s in under:
                es = [ents[x].get("name") or x for x in a.get("entities", []) if x in ents and ents[x].get("source") == s["id"]]
                L.append(f"- **{s.get('name')}** ({s.get('item')}): {', '.join(es) or 'supporting data'} from {s.get('system') or s.get('name')}.")
            L.append("")
        tabs = [ents[x] for x in a.get("entities", []) if x in ents and (ents[x].get("binding") or {}).get("table")
                and not conditional_source(sby.get(ents[x].get("source")) or {})]
        if tabs:
            L += ["### Bound tables (silver layer, Common Data Model names)", ""]
            L += [f"- `{e['binding']['table']}`: {e.get('name')} · {standard_text(e.get('standard'))}" for e in tabs]
            L.append("")
        proposals = [ents[x] for x in a.get("entities", []) if x in ents and conditional_source(sby.get(ents[x].get("source")) or {})]
        if proposals:
            L += ["### Conditional table proposals (not mounted/bound)", ""]
            L += [f"- {e.get('name')}: {binding_text(e, sby)}" for e in proposals]
            L.append("")
        L += ["### Example questions", ""]
        for i, q in enumerate(a.get("questions", []), start=1):
            L.append(f"{i}. {q.get('q')}" + (f"  \n   Query ({q.get('language', 'source-native')}): `{q['query']}`" if q.get("query") else ""))
        L += ["", ""]
    return "\n".join(L).rstrip() + "\n"


def _uses_text(d: dict) -> str:
    lab = {"analytics": "analytics", "grounding": "AI grounding", "actions": "agent actions (review)"}
    return "; ".join(lab.get(u.get("use"), u.get("use") or "") + (f" via {', '.join(u['via'])}" if u.get("via") else "") for u in as_list(d.get("uses")))


def current_guidance_md(onto: dict) -> list[str]:
    """Current public clarification stays separate from saved blocks and verdicts."""
    lines = ["## Current guidance (17 November 2026)", "",
             "Saved choices and verdicts below are recorded proposals, not verification or publication authority.", ""]
    for key in ("governance", "sap"):
        guidance = (onto.get("current_guidance") or {}).get(key) or {}
        lines += [guidance.get("text") or "", "Sources: " + ", ".join(guidance.get("src", [])), ""]
    for source in as_list(onto.get("sources")):
        assessment = source.get("route_assessment")
        if not isinstance(assessment, dict):
            continue
        lines += [f"### {source['id']}: {assessment['state']}", "",
                  f"Recorded choice: {source.get('path') or 'unselected'} / {source.get('item') or 'no selected item'} / {source.get('status')}.",
                  assessment.get("commercial_note") or "", ""]
        if conditional_source(source):
            lines += [f"Open: source route {source['id']}: conditional", ""]
        lines += _table(["Prerequisite", "Status", "Owner note", "Estate references"],
                        [[key, record["status"], record["note"], ", ".join(record["src"])]
                         for key, record in assessment["prerequisites"].items()])
        lines += ["", "Sources: " + ", ".join(assessment.get("src", [])), ""]
    for identity, current in (onto.get("current_readiness") or {}).items():
        lines += [f"Current {identity}: {current['status']}" + ("; " + ", ".join(current["gaps"]) if current["gaps"] else ""), ""]
    return lines


def binding_text(entity: dict, sources: dict) -> str:
    table = (entity.get("binding") or {}).get("table")
    if conditional_source(sources.get(entity.get("source")) or {}):
        return f"Recorded proposal (conditional): `{table}`" if table else "Unresolved source route; no selected table"
    return f"`{table}`" if table else "[To bind]"


def to_markdown(onto: dict, bp: dict | None = None) -> str:
    meta = onto.get("meta") or {}
    ents = as_list(onto.get("entity_types"))
    eby = {e["id"]: e for e in ents}
    sby = {s["id"]: s for s in as_list(onto.get("sources"))}
    jn = {d.get("id"): d.get("name") for d in business_domains(bp)} if bp else {}
    st = onto.get("stats") or {}
    arch = onto.get("data_architecture") or {}
    L = [f"# {onto.get('title')}", "",
         "| | |", "|---|---|",
         f"| Customer | {_md(meta.get('customer'))} |", f"| Version | {meta.get('version', '0.1')} ({meta.get('status', 'hypothesis')}) |",
         f"| Date | {meta.get('date') or 'undated'} |", f"| Blueprint | {_md(meta.get('blueprint'))} |",
         f"| Scope | {st.get('entity_types', 0)} entity types, {st.get('relationship_types', 0)} relationship types, {st.get('properties', 0)} properties, "
         f"{st.get('rules', 0)} rules, {st.get('metrics', 0)} metrics, {st.get('sources', 0)} OneLake sources, {st.get('data_agents', 0)} data agents, "
         f"{st.get('operations_agents', 0)} operations agents |",
         f"| Grounding | {st.get('standard', 0)} of {st.get('entity_types', 0)} entity types on a Microsoft standard entity (Common Data Model), "
         f"{st.get('custom', 0)} custom extensions, {st.get('to_verify', 0)} to verify; {st.get('data_products', 0)} data products "
         f"({st.get('data_products_ready', 0)} ready to publish), {st.get('semantic_models', 0)} semantic models |", "",
         "A hypothesis of the customer's process ontology in Microsoft Fabric IQ, derived from the Frontier Company Blueprint. "
         "It names the business concepts the journeys run on, grounds each in a Microsoft standard entity of the Common Data Model where one exists, "
         "binds them to conformed data in OneLake and grounds the data agents and operations agents in one vocabulary. Every element is a hypothesis "
         "until the workshop and the data owners confirm it.", ""]
    if onto.get("intro"):
        L += [onto["intro"], ""]
    L += current_guidance_md(onto)
    L += ["## 1 How it fits in Fabric IQ", ""]
    L += _table(["Layer", "What it does", "Source"], [[s["name"], s["what"], ", ".join(s.get("src", []))] for s in as_list(onto.get("stack"))])
    L += ["", "## 2 Entity types", ""]
    L += _table(["Entity type", "Namespace", "Description", "Key", "Properties", "Standard entity", "Bound to"],
                [[e.get("name"), e.get("namespace") or "", e.get("description"), ", ".join(e.get("key") or []) or "keyless",
                  str(len(e.get("properties") or [])) + (f" + {len(e['timeseries'])} time series" if e.get("timeseries") else ""),
                  standard_text(e.get("standard")), binding_text(e, sby)] for e in ents])
    for e in ents:
        sd = e.get("standard") or {}
        cols = sd.get("attributes") or {}
        L += ["", f"### {e.get('name')} (`{e['id']}`)", "", e.get("description") or "", ""]
        if e.get("synonyms"):
            L += ["Synonyms: " + ", ".join(e["synonyms"]), ""]
        if e.get("base"):
            L += [f"Inherits from {eby[e['base']].get('name')}.", ""]
        L += [f"Standard: {standard_text(sd)} ({sd.get('match')} match, {sd.get('role')}{'' if sd.get('checked') or sd.get('standard') == 'custom' else ', to verify'}). "
              + (sd.get("note") or ""), ""]
        if e.get("source") or e.get("binding"):
            L += [f"Source: {(sby.get(e.get('source')) or {}).get('name') or '[To confirm]'} · {binding_text(e, sby)}"
                  + (f" · time series `{e['binding']['timeseries_table']}`" if (e.get("binding") or {}).get("timeseries_table") else ""), ""]
        L += _table(["Property", "Type", "Standard column", "Notes"],
                    [[p["name"], p["type"], cols.get(p["name"]) or "", ("key" if p["name"] in (e.get("key") or []) else "") + (" " + p.get("description", "") if p.get("description") else "")]
                     for p in e.get("properties") or []]
                    + [[p["name"], p["type"], "", "time series" + (f" ({p['unit']})" if p.get("unit") else "")] for p in e.get("timeseries") or []])
    L += ["", "## 3 Relationship types", ""]
    L += _table(["Relationship", "From", "To", "Cardinality"], [[r.get("label") or r["name"], eby[r["from"]].get("name"), eby[r["to"]].get("name"), r.get("cardinality")]
                                                                 for r in as_list(onto.get("relationship_types"))])
    L += ["", "## 4 Grounding in the Common Data Model", "", arch.get("principle") or "", ""]
    L += _table(["Entity type", "Standard", "Standard entity", "Table", "Match", "Role", "Columns mapped", "Checked"],
                [[e.get("name"), (e.get("standard") or {}).get("standard"), (e.get("standard") or {}).get("entity"),
                  (e.get("standard") or {}).get("table") or "custom table",
                  (e.get("standard") or {}).get("match"), (e.get("standard") or {}).get("role"),
                  f"{(e.get('standard') or {}).get('mapped', 0)} of {(e.get('standard') or {}).get('of', 0)}",
                  "custom" if (e.get("standard") or {}).get("standard") == "custom" else ("yes" if (e.get("standard") or {}).get("checked") else "to verify")] for e in ents])
    L += ["", "Column names are the Dataverse logical names as they appear in the lakehouse of Link to Fabric; finance and operations tables keep their field "
              "names. Verify each column with the table definition browser of the customer's environment before binding.", ""]
    if onto.get("process"):
        L += ["## 5 The process on the ontology", ""]
        for p in onto["process"]:
            L += [f"**{p.get('name')}**", ""]
            L += _table(["Stage", "Entity types"], [[s["stage"], ", ".join(eby[x].get("name") for x in s["entities"] if x in eby)] for s in p["stages"]])
            L.append("")
    L += ["## 6 Semantic data layer", ""]
    L += _table(["Layer", "What it holds", "Source"], [[x.get("name"), x.get("what"), ", ".join(x.get("src", []))] for x in as_list(arch.get("layers"))])
    if arch.get("intake"):
        L += ["", f"**Into OneLake.** {arch['intake']}", ""]
    L += ["**Bronze: the systems of record in OneLake**", ""]
    L += _table(["Source", "System of record", "Path into OneLake", "Fabric item", "Entity types", "Data class", "Owner", "Status"],
                [[s.get("name"), s.get("system"), s.get("path"), s.get("item"), ", ".join(e.get("name") for e in ents if e.get("source") == s["id"]),
                  s.get("data_class"), s.get("owner"), s.get("status")] for s in as_list(onto.get("sources"))])
    L += ["", "**Domains: grouping proposals (saved labels are recorded, not access controls)**", ""]
    L += _table(["Domain", "Grouping / recorded label", "Owner", "Silver lakehouse", "Gold lakehouse", "Eventhouse", "Entity types"],
                [[d.get("fabric_domain"), d.get("governance_domain"), d.get("owner"), d.get("silver"), d.get("gold") or "", d.get("events") or "",
                  ", ".join(eby[x].get("name") for x in d.get("entities", []) if x in eby)] for d in as_list(onto.get("domains"))])
    L += ["", "**Gold: one semantic model per journey (star schema, Direct Lake on OneLake)**", ""]
    L += _table(["Semantic model", "Journey", "Gold lakehouse", "Fact tables", "Dimensions", "Measures"],
                [[m.get("name"), jn.get(m.get("journey"), m.get("journey")), m.get("lakehouse"), ", ".join(eby[x].get("name") for x in as_list(m.get("facts")) if x in eby),
                  ", ".join((eby[x].get("name") if x in eby else x) for x in as_list(m.get("dimensions"))),
                  ", ".join((x.get("name") or "") + (f" {x['measure']}" if x.get("measure") else " (to define)") for x in as_list(m.get("measures"))) or "to define"]
                 for m in as_list(onto.get("semantic_models"))])
    if arch.get("semantic_models"):
        L += ["", arch["semantic_models"]]
    L += ["", "## 7 Data products", "", "Canvases, publication gaps and current Fabric/OneLake guidance: `data-products.md`.", ""]
    L += _table(["ID", "Data product", "Domain", "Owner", "Entity types", "Intended uses", "Open for publication"],
                [[d["id"], d.get("name") + (" (knowledge)" if d.get("kind") == "knowledge" else ""), d.get("domain"), d.get("owner") if d.get("kind") != "knowledge" else "\u2014",
                  ", ".join(eby[x].get("name") for x in d.get("entities", []) if x in eby) or ("\u2014" if d.get("kind") == "knowledge" else "to model"),
                  _uses_text(d) if d.get("kind") != "knowledge" else "Foundry IQ",
                  ", ".join(d.get("gaps") or []) or ("ready" if d.get("kind") != "knowledge" else "\u2014")] for d in as_list(onto.get("data_products"))])
    L += ["", "## 8 Rules and metrics", "", "**Business rules** (natural language, linked to entity types)", ""]
    L += _table(["ID", "Rule", "Applies to"], [[r["id"], r["text"], ", ".join(eby[x].get("name") for x in r.get("applies_to", []) if x in eby)] for r in as_list(onto.get("rules"))])
    L += ["", "**Metrics** (DAX measures from the journey's semantic model; the semantic model stays the owner of the expression)", ""]
    L += _table(["ID", "Metric", "Entity type", "Journey", "Measure", "Status"],
                [[m["id"], m.get("name"), (eby.get(m.get("entity")) or {}).get("name"), jn.get(m.get("journey"), m.get("journey")),
                  (f"{m.get('semantic_model')} · {m.get('measure')}" if m.get("measure") else None), m.get("status")] for m in as_list(onto.get("metrics"))])
    L += ["", "## 9 Data agents", "", "Details, instructions and example questions: `data-agents.md`.", ""]
    L += _table(["ID", "Data agent", "Entity types", "Sources", "Consumed by"],
                [[a["id"], a.get("name"), ", ".join(eby[x].get("name") for x in a.get("entities", []) if x in eby), ", ".join(a.get("sources", [])),
                  "; ".join(c["kind"] + (f" ({', '.join(c.get('agents', []))})" if c.get("agents") else "") for c in a.get("consumers", []))] for a in as_list(onto.get("data_agents"))])
    L += ["", "## 10 Operations agents", ""]
    for a in as_list(onto.get("operations_agents")):
        L += [f"**{a['id']} · {a.get('name')}**: {a.get('goal') or ''}", ""]
        L += ["- Monitors: " + ", ".join(eby[x].get("name") for x in a.get("entities", []) if x in eby)]
        L += [f"- Rule: {r}" for r in a.get("rules", [])]
        L += [f"- Action: {x['name']}({', '.join(x.get('params', []))}), approved by {x.get('approver') or 'a named person'} in {a.get('notify')}" for x in a.get("actions", [])]
        L.append("")
    if not as_list(onto.get("operations_agents")):
        L += ["None yet: an operations agent is proposed where the journey has live signals in OneLake or an eventhouse.", ""]
    L += ["## 11 Build it in Fabric IQ", ""]
    for b in as_list(onto.get("build_steps")):
        L.append(f"{b['id'][1:]}. **{b['name']}**: {b['what']} ({', '.join(b.get('src', []))})")
    L += ["", "## 12 Readiness, risks and open decisions", ""]
    L += _table(["ID", "Item", "Owner", "Stage", "Status"], [[r["id"], r["item"], r.get("owner"), r.get("stage"), r.get("status", "open")] for r in as_list(onto.get("readiness"))])
    L.append("")
    L += _table(["ID", "Risk", "L", "I", "Mitigation"], [[r["id"], r["title"], r.get("likelihood"), r.get("impact"), r.get("mitigation")] for r in as_list(onto.get("risks"))])
    L.append("")
    L += _table(["ID", "Decision", "Recommendation", "Owner"], [[d["id"], d["question"], d.get("recommendation"), d.get("owner")] for d in as_list(onto.get("decisions"))])
    L += ["", "## 13 Diagram", "", "```mermaid", mermaid(onto), "```", "", "## Sources", ""]
    for s in as_list(onto.get("sources_doc")):
        L.append(f"- {s['id']}: [{s['title']}]({s['url']})")
    L += ["", f"Checked against Microsoft Learn on {load_canon().get('checked')}. Ontology and its agent integrations are in preview."]
    return "\n".join(L).rstrip() + "\n"


def data_products_md(onto: dict, bp: dict | None = None) -> str:
    """The data product canvases: what each data product offers, who owns it, how it may be used and what is open before publication."""
    meta = onto.get("meta") or {}
    eby = {e["id"]: e for e in as_list(onto.get("entity_types"))}
    std = onto.get("data_product_standard") or {}
    arch = onto.get("data_architecture") or {}
    jn = {d.get("id"): d.get("journey_name") or d.get("name") for d in business_domains(bp)} if bp else {}
    dps = as_list(onto.get("data_products"))
    dash = "\u2014"
    L = [f"# Data products: {onto.get('title')}", "",
         f"Version {meta.get('version', '0.1')} ({meta.get('status', 'hypothesis')}). {std.get('what') or ''} "
         "Each data product below is a proposal from the blueprint's data agents; the owning domain confirms it.", "",
         "## The standard", "", std.get("publication_note") or "", "",
         "- **Endorsement**: " + "; ".join(f"{k}: {v}" for k, v in (std.get("endorsement") or {}).items()),
         "- **Approved use**: " + (std.get("consumption") or ""),
         "- **Discovery**: " + (std.get("discovery") or ""),
         "- **Security**: " + (std.get("security") or ""), "",
         "Sources: " + ", ".join(std.get("src", [])), ""]
    L += current_guidance_md(onto)
    L += ["## Overview", ""]
    L += _table(["ID", "Data product", "Domain", "Owner", "Sensitivity", "Endorsement", "Open for publication"],
                [[d["id"], d.get("name"), d.get("domain"), d.get("owner") if d.get("kind") != "knowledge" else dash,
                  (d.get("sensitivity") or "") if d.get("kind") != "knowledge" else dash, d.get("endorsement") if d.get("kind") != "knowledge" else dash,
                  ", ".join(d.get("gaps") or []) or ("ready" if d.get("kind") != "knowledge" else "knowledge source (Foundry IQ)")] for d in dps])
    for d in dps:
        L += ["", f"## {d['id']} · {d.get('name')}", ""]
        if d.get("kind") == "knowledge":
            L += [f"Knowledge source, not a data product in OneLake. {d.get('purpose') or ''}", ""]
            continue
        rows = [["Domain", f"{d.get('domain')} ({jn.get(d.get('journey'), d.get('journey') or 'shared')})"],
                ["Accountable owner", d.get("owner")], ["Business purpose", d.get("purpose")], ["Intended uses", _uses_text(d)],
                ["Entity types", ", ".join(f"{eby[x].get('name')} ({standard_text(eby[x].get('standard'))})" for x in d.get("entities", []) if x in eby) or "to model"],
                ["Output ports", "; ".join(d.get("outputs") or [])], ["Layer", d.get("layer")], ["Quality status", d.get("quality")],
                ["Access process", d.get("access")], ["Operational commitment", d.get("commitment")], ["Sensitivity", d.get("sensitivity")],
                ["Endorsement", d.get("endorsement")], ["Glossary terms", ", ".join(d.get("glossary") or [])], ["Critical data elements", ", ".join(d.get("cde") or [])],
                ["Status", d.get("status")]]
        L += _table(["Field", "Value"], rows)
        if any(u.get("review") for u in as_list(d.get("uses"))):
            L += ["", "Agent actions need an additional review: approval for analytics or AI grounding does not cover an agent that acts."]
        if d.get("gaps"):
            L += ["", "Open before publication: " + ", ".join(d["gaps"]) + "."]
    dom = arch.get("domains") or {}
    L += ["", "## Set it up in Fabric and OneLake catalog", "",
          f"1. **Domains.** {dom.get('fabric') or ''}",
          "2. **Layers.** " + " ".join(f"{x.get('name')}: {x.get('what')}" for x in as_list(arch.get("layers"))[:3]),
          "3. **Publish.** Give each data product its owner, purpose, intended uses, access process and quality status; apply the sensitivity label; promote it, certify it after review.",
          f"4. **Catalog.** {std.get('discovery') or ''} {dom.get('purview_what') or ''}",
          "5. **Consume.** Data agents and Power BI keep the user's identity; agent actions and external sharing go through the domain's review.", ""]
    L += ["## Sources", ""]
    ids = set(std.get("src", [])) | set((arch.get("domains") or {}).get("src", [])) | {s for x in as_list(arch.get("layers")) for s in x.get("src", [])}
    for s in as_list(onto.get("sources_doc")):
        if s["id"] in ids:
            L.append(f"- {s['id']}: [{s['title']}]({s['url']})")
    return "\n".join(L).rstrip() + "\n"
