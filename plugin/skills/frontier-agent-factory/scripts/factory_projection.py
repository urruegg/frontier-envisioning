# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Passive customer projections and explicit sharing; never acquire or execute input."""
from __future__ import annotations

import copy
from contextlib import contextmanager
import datetime as dt
import importlib.util
from pathlib import Path
import sys
import sysconfig

from factory_common import (
    EXTENSIONS, FactoryError, MIB, approval, decode, encoded, identity, keys,
    need, portable, read, text, timestamp_key,
)

SKILLS = Path(__file__).resolve().parents[2]
EXCLUSION_POLICY = (
    "Only the compatible foundation and explicitly declared, reviewed baseline files are copied. "
    "Original working files, local state and financial authority staging are not copied. "
    "No withheld names or counts are disclosed. No application or solution runtime is generated."
)


@contextmanager
def sibling(skill, module):
    """Isolate trusted installed siblings from cwd, PYTHONPATH and cached homonyms.

    The lifetime includes calls into the loaded module (some helpers import lazily).
    No tools/tests/repository imports and no optional FinOps execution on core paths.
    """
    need(skill in {"frontier-blueprint", "frontier-process", "frontier-value-case", "frontier-finops"}
         and module.isidentifier(), "FACTORY_HELPER")
    scripts = SKILLS / skill / "scripts"
    path = scripts / (module + ".py")
    need(path.is_file(), "FACTORY_HELPER")
    names = {p.stem for folder in SKILLS.glob("*/scripts") for p in folder.glob("*.py")}
    saved = {name: sys.modules[name] for name in names if name in sys.modules}
    previous = sys.path[:]
    # CPython standard-library roots only; exclude site-packages and all caller paths.
    stdlib = sysconfig.get_path("stdlib")
    platstdlib = sysconfig.get_path("platstdlib")
    libraries = [stdlib, platstdlib, str(Path(sys.base_prefix) / "DLLs"),
                 str(Path(stdlib) / "lib-dynload"),
                 str(Path(sys.base_prefix) / f"python{sys.version_info.major}{sys.version_info.minor}.zip")]
    try:
        for name in names:
            sys.modules.pop(name, None)
        sys.path[:] = [str(scripts), *dict.fromkeys(libraries)]
        spec = importlib.util.spec_from_file_location(module, path)
        loaded = importlib.util.module_from_spec(spec)
        sys.modules[module] = loaded
        spec.loader.exec_module(loaded)
        yield loaded
    finally:
        sys.path[:] = previous
        for name in names:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


@contextmanager
def validation_input(code):
    """Only documented user-data ValueErrors; programmer defects remain visible."""
    try:
        yield
    except ValueError:
        raise FactoryError(code) from None


def _objects(value, field):
    if field in value:
        need(isinstance(value[field], list) and all(isinstance(row, dict) for row in value[field]),
             "FACTORY_BLUEPRINT")


def blueprint_shape(document):
    """Guard the container/identity shapes consumed by the existing customer helper."""
    need(isinstance(document, dict), "FACTORY_BLUEPRINT")
    encoded(document)
    for field in ("meta", "ontology", "prd", "it_readiness"):
        if field in document:
            need(isinstance(document[field], dict), "FACTORY_BLUEPRINT")
    for field in ("domains", "evidence", "ontology_feedback"):
        _objects(document, field)
    for row in document.get("evidence", []):
        text(row.get("id"))
    for domain in document.get("domains", []):
        text(domain.get("id"))
        _objects(domain, "agents")
        for row in domain.get("agents", []):
            text(row.get("id"))
        if domain.get("orchestrator") is not None:
            need(isinstance(domain["orchestrator"], dict), "FACTORY_BLUEPRINT")
            text(domain["orchestrator"].get("id"))
    onto = document.get("ontology")
    if onto is not None:
        for field in ("entity_types", "relationship_types", "sources", "namespaces", "data_agents",
                      "operations_agents", "data_products", "metrics", "rules", "risks", "readiness",
                      "decisions", "semantic_models", "domains"):
            _objects(onto, field)
    if "groups" in document.get("it_readiness", {}):
        _objects(document["it_readiness"], "groups")
    _flag_shapes(document)


def _nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nodes(child)


def _strings(value):
    """Actual strings, including keys; JSON escaping must not hide known tokens."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)
    elif isinstance(value, str):
        yield value


def _flag_shapes(value):
    for node in _nodes(value):
        if "internal" in node:
            need(type(node["internal"]) is bool, "FACTORY_SHARING")
        for field in ("visibility", "sharingClassification", "customer_scope", "ancestry_status"):
            if field in node:
                need(node[field] is None or isinstance(node[field], str), "FACTORY_SHARING")
        for field in ("src", "content_src"):
            if field in node:
                refs = node[field]
                need(refs is None or isinstance(refs, str)
                     or (isinstance(refs, list) and all(isinstance(ref, str) for ref in refs)),
                     "FACTORY_SHARING")
        if "content_origins" in node:
            need(isinstance(node["content_origins"], list)
                 and all(isinstance(row, dict) for row in node["content_origins"]), "FACTORY_SHARING")


def check_blueprint(request, baseline, originals):
    descriptor = request["blueprint"]
    keys(descriptor, ("source_path", "baseline_path"))
    source, target = (portable(descriptor[key]) for key in ("source_path", "baseline_path"))
    need(source in originals and target in baseline, "FACTORY_BLUEPRINT")
    need(any(row["status"] == "provided" and row["role"] == "blueprint"
             and portable(row["source"]["path"]) == source
             and portable(row["baseline"]["path"]) == target
             for row in request["intake"]["artifacts"]), "FACTORY_BLUEPRINT")
    original, approved = decode(originals[source], 16 * MIB), decode(baseline[target], 16 * MIB)
    blueprint_shape(original)
    blueprint_shape(approved)
    # A cached financial view cannot authorise its own removal or republication.
    need("agent_finops" not in original, "FACTORY_BLUEPRINT_FINANCIAL_CONTEXT")
    with sibling("frontier-blueprint", "build_blueprint") as bp:
        report = bp.Report()
        with validation_input("FACTORY_BLUEPRINT"):
            expected = bp.customer_version(copy.deepcopy(original), report)
        need(not report.errors and expected == approved, "FACTORY_BLUEPRINT")
    return original, approved


def check_selection(request, customer_blueprint, intake):
    mappings = request["id_map"]
    keys(mappings, ("solutions", "agents", "requirements"))
    for mapping in mappings.values():
        need(isinstance(mapping, dict) and len(set(mapping.values())) == len(mapping),
             "FACTORY_SELECTION")
        for original, factory in mapping.items():
            text(original)
            identity(factory)
    selected = {row["solution_id"]: row for row in intake["selected_solutions"]}
    need(set(mappings["solutions"].values()) == set(selected)
         and set(mappings["agents"].values()) ==
         {agent for row in selected.values() for agent in row["agent_ids"]}
         and set(mappings["requirements"].values()) == {row["id"] for row in intake["requirements"]},
         "FACTORY_SELECTION")
    domains, agents = {}, {}
    for domain in customer_blueprint.get("domains", []):
        need(domain["id"] not in domains, "FACTORY_SELECTION")
        domains[domain["id"]] = domain
        team = domain.get("agents", []) + ([domain["orchestrator"]]
                                          if isinstance(domain.get("orchestrator"), dict) else [])
        for agent in team:
            need(agent["id"] not in agents, "FACTORY_SELECTION")
            agents[agent["id"]] = domain["id"]
    need(set(mappings["solutions"]) <= set(domains) and set(mappings["agents"]) <= set(agents),
         "FACTORY_SELECTION")
    evidence = request["selection_evidence"]
    need(len(evidence) == len(selected), "FACTORY_SELECTION")
    gaps = {row["id"] for field in ("gaps", "decisions") for row in intake[field]}
    seen = set()
    for row in evidence:
        sid, originals = row["solution_id"], row["original_agent_ids"]
        need(sid in selected and sid not in seen
             and mappings["solutions"].get(row["original_solution_id"]) == sid, "FACTORY_SELECTION")
        seen.add(sid)
        need(bool(originals) and len(set(originals)) == len(originals)
             and all(agent in mappings["agents"] and agents.get(agent) == row["original_solution_id"]
                     for agent in originals), "FACTORY_SELECTION")
        need({mappings["agents"][agent] for agent in originals} == set(selected[sid]["agent_ids"])
             and set(row["dependency_gaps"]) <= gaps, "FACTORY_SELECTION")
        text(row["rationale"])


def check_ordinary(name, raw):
    extension = Path(portable(name)).suffix.lower()
    need(extension in EXTENSIONS, "FACTORY_FORMAT")
    need(isinstance(raw, bytes) and 0 < len(raw) <= 16 * MIB, "FACTORY_LIMIT")
    if extension in {".pdf", ".docx", ".xlsx", ".pptx"}:
        return  # Opaque, explicitly reviewed documents; no DLP/semantic certification.
    try:
        value = raw.decode("utf-8")
    except UnicodeError:
        raise FactoryError("FACTORY_FORMAT") from None
    start = value.lstrip("\ufeff \t\r\n").lower()
    need("\x00" not in value and not start.startswith(
        ("pk\x03\x04", "pk\x05\x06", "pk\x07\x08", "%pdf-", "<!doctype html", "<html", "<head", "<body")),
        "FACTORY_FORMAT")
    if extension == ".json":
        decode(raw, 16 * MIB)


def export_metadata(request, intake, producer_version, financial_status):
    """The one prospective export projection, also used for sharing validation.

    Deliberately excludes absolute CLI paths and non-exported authority staging paths.
    """
    financial = request["financial"]
    return copy.deepcopy({
        "schema": "frontier-agent-factory-handover/1.0",
        "producer": {"name": "frontier-envisioning", "plugin_version": producer_version},
        "export_id": request["export_id"], "intake_id": intake["intake_id"],
        "history": request["history"],
        "created_at": request["created_at"], "customer_scope": request["customer_scope"],
        "evidence_kind": request["evidence_kind"], "template": request["template"],
        "supported_profile": "frontier-agent-factory-template-profile/1.0",
        "id_map": request["id_map"], "selection_evidence": request["selection_evidence"],
        "provided_artifacts": [row for row in intake["artifacts"] if row["status"] == "provided"],
        "gaps": intake["gaps"], "decisions": intake["decisions"],
        "sharing_review": request["sharing_review"], "exclusion_policy": EXCLUSION_POLICY,
        "financial": {"requested": financial["requested"], "as_of": financial["as_of"],
                      "claim": financial["claim"], "status": financial_status,
                      "packets": [{k: p[k] for k in ("artifact_ids", "kind", "owner_review")}
                                  for p in financial["packets"]]},
        "validation": {"export": "passed", "receiver": "not-performed", "cowork": "not-performed",
                       "tenant_readiness": "not-assessed", "source_checksums": "consistency-not-signature"},
        "intake_disposition": intake["review"]["status"],
        "original_source_validation": {
            "current": "hashes-computed-from-local-bytes",
            "history": "not-performed-originals-unavailable",
        },
        "opaque_review_limit": "Human sharing evidence is not semantic DLP certification.",
    })


def _refs(node, bp):
    return bp.src_ids(node.get("src")) + bp.src_ids(node.get("content_src"))


def check_sharing(request, records, baseline, original_blueprint):
    sharing = request["sharing_review"]
    need(sharing["customer_scope"] == request["customer_scope"], "FACTORY_SHARING")
    approval(sharing["metadata"])
    provided = {record["intake_id"] + ":" + row["id"]
                for record in records for row in record["artifacts"] if row["status"] == "provided"}
    need(set(sharing["artifacts"]) == provided, "FACTORY_SHARING")
    for evidence in sharing["artifacts"].values():
        approval(evidence)
    for record in records:
        transfer = record["transfer"]
        need(transfer["classification"] != "restricted" and transfer["permission"] == "approved"
             and transfer["approval"] is not None, "FACTORY_SHARING")
        approval(transfer["approval"])
    # Preserve the entire original graph while determining known restricted identities.
    with sibling("frontier-process", "ontology_lib") as process:
        need(not process.private_content(original_blueprint, original_blueprint), "FACTORY_SHARING")
        context = copy.deepcopy(original_blueprint)
        if isinstance(context.get("ontology"), dict):
            process.inherit_privacy(context["ontology"], context)
        private_strings = set()

        def private_tokens(value, inherited=False, private_field=False):
            if isinstance(value, dict):
                restricted = inherited or process.private_content(value, context)
                for key, child in value.items():
                    child_private_field = private_field or key == "internal_notes"
                    if not child_private_field and isinstance(child, str) and key in {
                            "visibility", "sharingClassification", "customer_scope", "status", "schema"}:
                        continue
                    # The customer helpers strip internal_notes independently
                    # of visibility. Its entire value is private, even when a
                    # note's arbitrary keys resemble protocol metadata.
                    private_tokens(child, restricted or child_private_field, child_private_field)
            elif isinstance(value, list):
                for child in value:
                    private_tokens(child, inherited, private_field)
            elif isinstance(value, str) and inherited and value.strip():
                private_strings.add(value.casefold())
        private_tokens(context)
        terms = context.get("meta", {}).get("internal_terms", [])
        need(isinstance(terms, list) and all(isinstance(t, str) for t in terms), "FACTORY_SHARING")
        private_strings.update(t.casefold() for t in terms if t.strip())
        public_ids = {row["id"] for row in context.get("evidence", [])
                      if not process.private_content(row, context)}
        structured = list(records)
        texts = []
        for record in records:
            for row in record["artifacts"]:
                if row["status"] != "provided":
                    continue
                name = portable(row["baseline"]["path"])
                need(name in baseline, "FACTORY_SHARING")
                raw = baseline[name]
                check_ordinary(name, raw)
                extension = Path(name).suffix.lower()
                if extension == ".json":
                    document = decode(raw, 16 * MIB)
                    structured.append(document)
                elif extension in {".md", ".txt", ".csv"}:
                    texts.append(raw.decode("utf-8"))
        with sibling("frontier-blueprint", "build_blueprint") as bp:
            structured.insert(0, export_metadata(request, records[0], bp.PLUGIN_VERSION, "pending-verification"))
            for document in structured:
                _flag_shapes(document)
                for node in _nodes(document):
                    onto = node if node.get("schema") == process.SCHEMA else node.get("ontology")
                    if isinstance(onto, dict):
                        with validation_input("FACTORY_SHARING"):
                            process.strict_reference_graph(onto, context)
                            report = process.Rep()
                            valid = (process.validate_route_assessments(onto, report)
                                     and process.validate_reserved_citations(onto, report))
                        need(valid and not report.errors, "FACTORY_SHARING")
                local_public = public_ids | {
                    row.get("id") for node in _nodes(document)
                    for row in (node["evidence"] if isinstance(node.get("evidence"), list) else [])
                    if isinstance(row, dict) and isinstance(row.get("id"), str)
                    and not process.private_content(row, context)
                }
                for node in _nodes(document):
                    need(not process.private_content(node, context), "FACTORY_SHARING")
                    need("internal_notes" not in node and node.get("ancestry_status") != "unresolved",
                         "FACTORY_SHARING")
                    if "visibility" in node:
                        need(node["visibility"] in {"customer", "public"}, "FACTORY_SHARING")
                    if "sharingClassification" in node:
                        need(node["sharingClassification"] in {"customer-shareable", "customer-specific"},
                             "FACTORY_SHARING")
                    if node.get("sharingClassification") == "customer-specific":
                        need(node.get("customer_scope") == request["customer_scope"], "FACTORY_SHARING")
                    refs = _refs(node, bp)
                    need(all(ref in local_public for ref in refs), "FACTORY_SHARING")
                need(not any(token in value.casefold() for value in _strings(document)
                             for token in private_strings), "FACTORY_SHARING")
            blob = "\n".join(texts).casefold()
            need(not any(token in blob for token in private_strings), "FACTORY_SHARING")


def _financial_schema(document):
    return any(isinstance(node.get("schema"), str)
                   and node["schema"].startswith(("frontier-finops-", "frontier-agent-finops-"))
                   for node in _nodes(document))


def financial_check(request, records, baseline, source_root, acknowledged):
    """Verify explicitly reviewed costs; never estimate by default or infer consent.

    All financial operations are below the current-invocation gate. Model/review
    reads are bounded, detached and not exported. The owner modules own arithmetic,
    receipts, privacy and the stricter financial handover decision.
    """
    provided, documents, detected = {}, {}, set()
    with sibling("frontier-value-case", "value_calc") as value:
        for record in records:
                for row in record["artifacts"]:
                    if row["status"] != "provided":
                        continue
                    qualified = record["intake_id"] + ":" + row["id"]
                    need(qualified not in provided, "FACTORY_FINANCIAL_COVERAGE")
                    name = portable(row["baseline"]["path"])
                    need(name in baseline, "FACTORY_FINANCIAL_COVERAGE")
                    provided[qualified] = (name, baseline[name])
                    if row["role"] == "finops":
                        detected.add(qualified)
                    if Path(name).suffix.lower() == ".json":
                        document = decode(baseline[name], 16 * MIB)
                        documents[qualified] = document
                        if value.has_finops_dependency(document) or _financial_schema(document):
                            detected.add(qualified)
    financial = request["financial"]
    if not financial["requested"]:
        need(financial["claim"] == "review", "FACTORY_FINANCIAL_READY")
        need(not detected and not financial["packets"] and financial["as_of"] is None,
                 "FACTORY_FINANCIAL_ACK")
        return "not-requested"
    need(acknowledged is True, "FACTORY_FINANCIAL_ACK")
    need(isinstance(financial["as_of"], str), "FACTORY_FINANCIAL_DATE")
    with validation_input("FACTORY_FINANCIAL_DATE"):
        as_of = dt.date.fromisoformat(financial["as_of"])
    need(as_of.isoformat() == financial["as_of"], "FACTORY_FINANCIAL_DATE")
    packets = financial["packets"]
    need(bool(packets), "FACTORY_FINANCIAL_COVERAGE")
    covered = set()
    for packet in packets:
        approval(packet["owner_review"])
        need(timestamp_key(packet["owner_review"]["at"]) <= timestamp_key(request["created_at"]),
                 "FACTORY_FINANCIAL_REVIEW")
        for qualified in packet["artifact_ids"]:
                need(qualified in provided and qualified not in covered, "FACTORY_FINANCIAL_COVERAGE")
                covered.add(qualified)
    need(detected <= covered, "FACTORY_FINANCIAL_COVERAGE")
    # Packet declaration itself classifies additional reviewed financial files.
    need(all(isinstance(documents[q], dict) for q in covered if q in documents),
         "FACTORY_FINANCIAL_SHAPE")
    ready, reviewed_documents = [], False
    remaining = 128 * MIB
    with sibling("frontier-finops", "finops_preview") as preview:
        with validation_input("FACTORY_FINANCIAL"):
                preview.require_preview_ack(acknowledged)
        for packet in packets:
                if packet["kind"] == "reviewed-document":
                    need(packet["model_path"] is None and packet["review_paths"] == [], "FACTORY_FINANCIAL")
                    for qualified in packet["artifact_ids"]:
                        document = documents.get(qualified)
                        if document is None:
                            continue
                        need(not _financial_schema(document), "FACTORY_FINANCIAL_AUTHORITY")
                        for node in _nodes(document):
                            if str(node.get("schema", "")).startswith("frontier-finops/"):
                                with validation_input("FACTORY_FINANCIAL"):
                                    preview.validate_finops_results(node, acknowledge_finops_preview=True)
                        with sibling("frontier-value-case", "value_calc") as value:
                            with validation_input("FACTORY_FINANCIAL"):
                                value.preview_for(document, acknowledge_finops_preview=True,
                                                  operation="apply-value" if "results" in document else "consume-value")
                    reviewed_documents = True
                    ready.append(False)
                    continue
                need(packet["kind"] == "baseline" and packet["model_path"] is not None
                     and bool(packet["review_paths"]), "FACTORY_FINANCIAL_AUTHORITY")
                loaded = []
                for name in [packet["model_path"], *packet["review_paths"]]:
                    need(remaining > 0, "FACTORY_LIMIT")
                    raw = read(source_root, name, min(16 * MIB, remaining))
                    remaining -= len(raw)
                    document = decode(raw, 16 * MIB)
                    need(isinstance(document, dict), "FACTORY_FINANCIAL_SHAPE")
                    loaded.append(document)
                model, reviews = loaded[0], loaded[1:]
                need(model.get("schema") == "frontier-finops-snapshot/1.0", "FACTORY_FINANCIAL_AUTHORITY")
                with sibling("frontier-finops", "baseline_projection") as projector:
                    with validation_input("FACTORY_FINANCIAL"):
                        report = projector.project(model, reviews, as_of=as_of, audience="customer",
                                                   customer_scope=request["customer_scope"],
                                                   acknowledge_finops_preview=True)
                        markdown = projector.render_markdown(report).encode("utf-8")
                    need(not any(node.get("status") == "withheld" for node in _nodes(report)),
                         "FACTORY_FINANCIAL_PRIVACY")
                    for qualified in packet["artifact_ids"]:
                        name, raw = provided[qualified]
                        extension = Path(name).suffix.lower()
                        need((extension == ".json" and documents[qualified] == report)
                             or (extension == ".md" and raw == markdown), "FACTORY_FINANCIAL_PROJECTION")
                    ready.append(report["handover"].get("ready") is True
                                 and report["status"] == "planning-ready")
    all_ready = bool(ready) and all(ready)
    need(financial["claim"] != "build-handover" or all_ready, "FACTORY_FINANCIAL_READY")
    if all_ready:
        return "planning-ready-not-financial-permission"
    if reviewed_documents:
        return "reviewed-documents-not-financially-ready"
    return "review-with-financial-gaps"
