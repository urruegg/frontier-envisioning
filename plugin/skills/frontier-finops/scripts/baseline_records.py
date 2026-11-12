# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Offline drafts, exclusive frozen targets and externally asserted review.

Snapshots are ordinary editable files, not authenticated/tamper-proof storage.
Planning readiness NEVER grants spending, purchase, deployment or other permission.
"""
from __future__ import annotations

import copy
import json
import re
from datetime import date
from pathlib import Path

from baseline_calc import _combine, calculate, validate_receipt
from baseline_model import _date, _gap, _integer, _object, _text, material_payload, model_fingerprint, validate_model
from finops_preview import NOTICE, fingerprint, require_preview_ack

SNAPSHOT_SCHEMA = "frontier-finops-snapshot/1.0"
REVIEW_SCHEMA = "frontier-finops-owner-review/1.0"
BOUNDARY = (
    "Externally asserted decisions, not authentication, permission or tamper-proof storage. "
    "Planning readiness is not budget, purchase, commitment, build or deployment approval."
)
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,119}\Z")
_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}
_CLASSES = {"customer-shareable", "customer-specific", "internal-only", "validation-required"}
_RESTRICTIONS = ("sharingClassification", "sharing_classes", "customer_scopes",
                 "internal", "visibility", "src", "content_src")


def _day(as_of):
    if type(as_of) is not date:
        raise ValueError("as_of must be an explicit datetime.date")
    return as_of.isoformat()


def _identity(value):
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value) or value.upper() in _RESERVED:
        raise ValueError("record identity must be a portable filename-safe ID")
    return value


def _target(model):
    baseline = _object(model.get("baseline"), "baseline")
    identity = _identity(baseline.get("id"))
    version = _integer(baseline.get("version"), "baseline.version", minimum=1)
    if version is None:
        raise ValueError("baseline.version is required for a frozen target")
    return {"baseline_id": identity, "version": version, "material_hash": model_fingerprint(model)}


def _json_text(document):
    try:
        return json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    except (TypeError, OverflowError):
        raise ValueError("document must contain finite JSON-compatible data") from None


def _write_exclusive(path, document):
    """Serialise before directories/open; never overwrite a history record."""
    text = _json_text(document)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    except FileExistsError:
        raise ValueError("record already exists; preserve history and use a new version/record ID") from None
    return path


def _agent(blueprint, agent_id):
    _object(blueprint, "blueprint")
    if blueprint.get("schema") != "frontier-blueprint/1.0":
        raise ValueError("unsupported blueprint schema")
    _identity(agent_id)
    found = []
    domains = blueprint.get("domains", [])
    if not isinstance(domains, list):
        raise ValueError("blueprint.domains must be a list")
    seen = set()
    for domain in domains:
        _object(domain, "blueprint.domain")
        agents = domain.get("agents", [])
        if not isinstance(agents, list):
            raise ValueError("blueprint.agents must be a list")
        for agent in [*agents, *[domain[k] for k in ("lead", "orchestrator") if domain.get(k) is not None]]:
            _object(agent, "blueprint.agent")
            identity = _identity(agent.get("id"))
            if identity in seen:
                raise ValueError("duplicate blueprint agent identity")
            seen.add(identity)
            if identity == agent_id:
                found.append((domain, agent))
    if len(found) != 1:
        raise ValueError("unknown or ambiguous blueprint agent")
    return found[0]


def _walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _refs(record):
    refs = []
    for key in ("src", "content_src", "source_id"):
        value = record.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            if _text(value, "provenance.reference") is None:
                continue
            value = value.replace(",", " ").split() if key != "source_id" else [value]
        if not isinstance(value, list) or any(not isinstance(r, str) for r in value):
            raise ValueError("provenance references must use source IDs")
        refs.extend(ref for ref in value if _text(ref, "provenance.reference") is not None)
    return refs


def _context(value):
    """Retain consumed authored ancestry, never import legacy approval/consent/results."""
    if isinstance(value, dict):
        excluded = {"results", "status", "approved", "approval", "acknowledgement", "finops_preview",
                    "review_records", "handover"}
        return {k: _context(v) for k, v in value.items() if k not in excluded}
    if isinstance(value, list):
        return [_context(v) for v in value]
    return copy.deepcopy(value)


def _merged_ancestry(contexts, scope):
    """Adapt authored ancestry to the existing calculator's class/flag merger.

    Do not duplicate dominance/union rules. Conflicting scope declarations add
    validation-required to that merger; they never choose a winning customer.
    """
    records = [{"sharing_classes": ["customer-specific" if scope else "validation-required"],
                "customer_scopes": [scope] if scope else []}]

    def visit(value, inherited_scope):
        if isinstance(value, dict):
            row = {key: copy.deepcopy(value[key]) for key in ("internal", "visibility", "src", "content_src")
                   if key in value}
            if "internal" in row and type(row["internal"]) is not bool:
                raise ValueError("ancestry.internal must be an actual boolean")
            visibility = _text(value.get("visibility"), "ancestry.visibility")
            classes = []
            if "sharingClassification" in value:
                classification = _text(value["sharingClassification"], "ancestry.sharingClassification")
                classes.append(classification if classification in _CLASSES else "validation-required")
            if "sharing_classes" in value:
                supplied = value["sharing_classes"]
                if not isinstance(supplied, list):
                    raise ValueError("ancestry.sharing_classes must be a list")
                for item in supplied:
                    item = _text(item, "ancestry.sharing_classes")
                    classes.append(item if item in _CLASSES else "validation-required")
            scopes = []
            supplied_scope = _text(value.get("customer_scope", inherited_scope), "ancestry.customer_scope")
            if supplied_scope:
                scopes.append(supplied_scope)
            if "customer_scopes" in value:
                supplied = value["customer_scopes"]
                if not isinstance(supplied, list):
                    raise ValueError("ancestry.customer_scopes must be a list")
                for item in supplied:
                    item = _text(item, "ancestry.customer_scopes")
                    if item is None:
                        classes.append("validation-required")
                    else:
                        scopes.append(item)
            if visibility is not None and visibility not in {"internal", "customer", "public"}:
                classes.append("validation-required")
            if "customer-specific" in classes and not scopes:
                classes.append("validation-required")
            row.update(sharing_classes=classes, customer_scopes=scopes)
            _refs(value)
            records.append(row)
            for child in value.values():
                visit(child, supplied_scope)
        elif isinstance(value, list):
            for child in value:
                visit(child, inherited_scope)

    inherited = scope
    for context in contexts:
        visit(context, inherited)
        if isinstance(context, dict):
            inherited = _text(context.get("customer_scope", inherited), "ancestry.customer_scope")
    merged = _combine(*records)
    if len(merged.get("customer_scopes", [])) > 1:
        merged = _combine(merged, {"sharing_classes": ["validation-required"]})
    return {key: merged[key] for key in _RESTRICTIONS if key in merged}


def _source(identity, raw=None, scope=None):
    raw = raw or {}
    restrictions = _merged_ancestry([raw], scope)
    scopes = restrictions.get("customer_scopes", [])
    return {
        "id": identity, "type": "customer-evidence", "title": raw.get("title"),
        "url": None, "evidence_ref": None, "supported_claim": None,
        "applicability": [], "lastValidatedAt": None, "validationStatus": "unverified",
        "freshness_policy": {"max_age_days": None},
        "customer_scope": scopes[0] if len(scopes) == 1 else None,
        **restrictions, "original_context": _context(raw),
    }


def seed(blueprint, agent_id, *, as_of, acknowledge_finops_preview=False):
    """Copy real Canvas context; ownership, money and economic scope stay unknown."""
    require_preview_ack(acknowledge_finops_preview)
    today = _day(as_of)
    domain, agent = _agent(blueprint, agent_id)
    scope = _text(blueprint.get("customer_scope"), "blueprint.customer_scope")
    actual_ancestry = [{k: v for k, v in blueprint.items() if k not in {"domains", "evidence", "sources"}},
                       {k: v for k, v in domain.items() if k not in {"agents", "lead", "orchestrator"}}, agent]
    restrictions = _merged_ancestry(actual_ancestry, scope)
    scopes = restrictions.get("customer_scopes", [])
    scope = scopes[0] if len(scopes) == 1 else None
    ancestry = [_context(context) for context in actual_ancestry]
    raw_sources = blueprint.get("sources", blueprint.get("evidence", []))
    if not isinstance(raw_sources, list):
        raise ValueError("blueprint source register must be a list")
    indexed = {}
    for row in raw_sources:
        _object(row, "blueprint.source")
        identity = _text(row.get("id"), "blueprint.source.id")
        if identity is None or identity in indexed:
            raise ValueError("blueprint source register requires unique IDs")
        indexed[identity] = row
    referenced = {ref for context in ancestry for row in _walk(context) for ref in _refs(row)}
    for row in raw_sources:
        referenced.update(ref for record in _walk(row) for ref in _refs(record))
    if referenced - set(indexed):
        raise ValueError("unresolved Blueprint source reference")
    sources = [_source(identity, indexed[identity], scope) for identity in sorted(indexed)]
    sharing = restrictions["sharingClassification"]
    draft = {
        "schema": "frontier-finops-baseline/1.0", "mode": "planning", "forecast_kind": "estimate",
        "preview_notice": NOTICE, "sharingClassification": sharing, "customer_scope": scope, **restrictions,
        "profile": {
            "agent_id": agent_id, "name": agent.get("name"), "canvas": copy.deepcopy(agent.get("canvas", {})),
            "owners": dict.fromkeys(("business", "technical", "finance")),
            "outcome": {"definition": agent.get("outcome"), "unit": None, "source_id": None,
                        "sharingClassification": sharing, "customer_scope": scope, **restrictions},
            "demand_context": None, "target_context": None, "measurement_plan": None, "guardrails": [],
            "sharingClassification": sharing, "customer_scope": scope, **restrictions,
        },
        "baseline": {
            "id": f"{agent_id}-BASELINE", "version": 1, "agent_id": agent_id, "as_of": today,
            "start_month": None, "currency": None, "annualisation": {},
            "scope": [], "assumptions": [], "exclusions": [], "risks": [], "confidence": {},
            "scenarios": [], "lines": [], "sharingClassification": sharing, "customer_scope": scope, **restrictions,
        },
        "rates": [], "fx": [], "sources": sources,
        "provenance": {"blueprint_fingerprint": fingerprint(blueprint), "consumed_context": ancestry,
                       "validationStatus": "unverified", "sharingClassification": sharing, "customer_scope": scope,
                       **restrictions},
    }
    validate_model(draft, as_of=as_of, blueprint=blueprint)
    return draft


def migrate(legacy, blueprint, agent_id, *, as_of, acknowledge_finops_preview=False):
    """Explicit legacy context only: no provable typed rate/FX/scenario mapping."""
    require_preview_ack(acknowledge_finops_preview)
    _day(as_of)
    legacy = _object(legacy, "legacy")
    if legacy.get("schema") != "frontier-finops/1.0":
        raise ValueError("migration accepts only explicit frontier-finops/1.0")
    draft = seed(blueprint, agent_id, as_of=as_of, acknowledge_finops_preview=True)
    context = _context(legacy)
    draft["provenance"]["legacy_fingerprint"] = fingerprint(legacy)
    draft["provenance"]["legacy_context"] = context
    restrictions = [{key: copy.deepcopy(record[key]) for key in
                     ("sharingClassification", "internal", "visibility", "src", "content_src", "customer_scope")
                     if key in record} for record in _walk(legacy)]
    restrictions = [record for record in restrictions if record]
    draft["provenance"]["legacy_restrictions"] = restrictions
    draft["provenance"]["migration"] = "context-only; typed quantities, rates, FX and scenarios require new evidence"
    seed_flags = {key: draft[key] for key in (*_RESTRICTIONS, "customer_scope") if key in draft}
    merged = _merged_ancestry([seed_flags, legacy], draft.get("customer_scope"))
    draft.update(merged)
    scopes = merged.get("customer_scopes", [])
    draft["customer_scope"] = scopes[0] if len(scopes) == 1 else None
    existing = {s["id"] for s in draft["sources"]}
    for identity in sorted({ref for r in _walk(draft["provenance"]) for ref in _refs(r)} - existing):
        draft["sources"].append(_source(identity))
    validate_model(draft, as_of=as_of, blueprint=blueprint)
    return draft


def _snapshot(snapshot, *, as_of):
    """Check original receipt at freeze date; dated readiness is evaluated separately."""
    _day(as_of)
    snapshot = _object(snapshot, "snapshot")
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("an explicit frozen snapshot is required")
    frozen = _date(snapshot.get("frozen_at"), "snapshot.frozen_at")
    if frozen is None or frozen > as_of:
        raise ValueError("snapshot date is missing or later than evaluation")
    model = _object(snapshot.get("model"), "snapshot.model")
    validate_receipt(model, as_of=frozen, acknowledge_finops_preview=True)
    target = _target(model)
    supplied = _object(snapshot.get("target"), "snapshot.target")
    if (type(supplied.get("version")) is not int or supplied != target):
        raise ValueError("snapshot target changed; create a new frozen version and review")
    return model, target, frozen


def freeze(model, out_dir, *, as_of, acknowledge_finops_preview=False):
    require_preview_ack(acknowledge_finops_preview)
    today = _day(as_of)
    validate_receipt(model, as_of=as_of, acknowledge_finops_preview=True)
    target = _target(model)
    document = {"schema": SNAPSHOT_SCHEMA, "frozen_at": today, "target": target,
                "model": copy.deepcopy(model), "review_boundary": BOUNDARY}
    return _write_exclusive(Path(out_dir) / f"{target['baseline_id']}.v{target['version']}.json", document)


def _review(snapshot, review, *, as_of, persisted=False):
    model, target, frozen = _snapshot(snapshot, as_of=as_of)
    review = _object(review, "review")
    if persisted and (review.get("schema") != REVIEW_SCHEMA or
                      review.get("assertion") != "externally-asserted-not-authenticated"):
        raise ValueError("explicit external-review record required")
    _identity(review.get("id"))
    sources = {source.get("id") for source in model.get("sources", [])}
    for record in _walk(review):
        for key in ("sharingClassification", "visibility", "customer_scope"):
            if key in record:
                _text(record[key], f"review.{key}")
        for key in ("internal", "synthetic"):
            if key in record and type(record[key]) is not bool:
                raise ValueError("review privacy/synthetic flags must be actual booleans")
        if set(_refs(record)) - sources:
            raise ValueError("review source-parent reference does not resolve")
    for key in ("actor", "finance_owner", "evidence_ref"):
        if _text(review.get(key), f"review.{key}") is None:
            raise ValueError("external actor, finance owner and evidence reference required")
    if (type(review.get("version")) is not int or
            {key: review.get(key) for key in target} != target):
        raise ValueError("review target does not exactly match the frozen version/hash")
    reviewed = _date(review.get("date"), "review.date")
    if reviewed is None or reviewed < frozen or reviewed > as_of:
        raise ValueError("review date must be between freeze and evaluation dates")
    owner = model.get("profile", {}).get("owners", {}).get("finance")
    if owner is None or review["finance_owner"] != owner:
        raise ValueError("review must identify the frozen accountable finance owner")
    if review["actor"] != owner and _text(review.get("delegation_evidence_ref"), "review.delegation_evidence_ref") is None:
        raise ValueError("delegate requires explicit delegation evidence")
    if _text(review.get("decision"), "review.decision") not in {"approve", "revise", "reject"}:
        raise ValueError("unsupported external review decision")
    if review.get("mode") != model.get("mode"):
        raise ValueError("review must explicitly match planning/synthetic mode")
    if persisted:
        recorded = _date(review.get("recorded_as_of"), "review.recorded_as_of")
        if recorded is None or recorded < reviewed or recorded > as_of:
            raise ValueError("invalid review recording date")
    return copy.deepcopy(review)


def record_review(snapshot, review, out_dir, *, as_of, acknowledge_finops_preview=False):
    require_preview_ack(acknowledge_finops_preview)
    today = _day(as_of)
    checked = _review(snapshot, review, as_of=as_of)
    checked.update(schema=REVIEW_SCHEMA, recorded_as_of=today, assertion="externally-asserted-not-authenticated",
                   review_boundary=BOUNDARY)
    checked.setdefault("sharingClassification", "validation-required")
    target = snapshot["target"]
    name = f"{target['baseline_id']}.v{target['version']}.{checked['id']}.json"
    return _write_exclusive(Path(out_dir) / name, checked)


def handover(snapshot, reviews, *, as_of, acknowledge_finops_preview=False):
    """Strict dated PLANNING gate; every model gap blocks, even after approve."""
    require_preview_ack(acknowledge_finops_preview)
    today = _day(as_of)
    model, target, _ = _snapshot(snapshot, as_of=as_of)
    if not isinstance(reviews, (tuple, list)):
        raise ValueError("reviews must be an explicit sequence")
    checked = [_review(snapshot, review, as_of=as_of, persisted=True) for review in reviews]
    if len(checked) > 1:
        raise ValueError("ambiguous active reviews; select one externally resolved decision explicitly")
    current = calculate(model, as_of=as_of, acknowledge_finops_preview=True)
    gaps = copy.deepcopy(current["results"]["gaps"])
    if any(record.get("visibility") is not None and record["visibility"] not in
           {"internal", "customer", "public"} for record in _walk(material_payload(model))):
        _gap(gaps, "sharing-validation", "model.provenance", "Legacy visibility requires explicit validation.")
    for scenario in current["results"]["scenarios"].values():
        if any(metric["amount"] is None or metric["status"] != "available"
               for family in scenario["unit_metrics"].values() for metric in family.values()):
            _gap(gaps, "unavailable-unit-metrics", "results.scenarios.unit_metrics",
                 "Required period unit metrics must be computable with evidenced inputs.")
    for review in checked:
        if _text(review.get("sharingClassification"), "review.sharingClassification") is None:
            _gap(gaps, "sharing-validation", "review", "Review sharing/provenance validation remains outstanding.")
        if any(record.get("synthetic") is True or
               any(record.get(key) == "synthetic" for key in ("mode", "type", "status", "validationStatus"))
               for record in _walk(review)):
            _gap(gaps, "synthetic-evidence", "review", "Synthetic review cannot satisfy financial handover.")
        for record in _walk(review):
            sharing = record.get("sharingClassification")
            if (sharing is not None and sharing not in
                    {"customer-shareable", "customer-specific", "internal-only"}) or (
                    record.get("visibility") is not None and record["visibility"] not in
                    {"internal", "customer", "public"}):
                _gap(gaps, "sharing-validation", "review", "Review sharing/provenance validation remains outstanding.")
            if sharing == "customer-specific" and not record.get("customer_scope"):
                _gap(gaps, "sharing-validation", "review", "Customer-specific review requires an explicit scope.")
    pricing = [g for g in gaps if any(word in g["code"] for word in
                                    ("rate", "fx", "source", "evidence", "unpriced", "quantity", "driver", "scope"))]
    decision = checked[0]["decision"] if checked else None
    lifecycle = "needs-validation" if gaps else "validated"
    if decision == "approve":
        lifecycle = "approved"
    if decision != "approve":
        gaps.append({"code": "missing-owner-review" if decision is None else "owner-review-not-approved",
                     "field": "review", "message": "Obtain externally evidenced finance-owner review of this frozen target.",
                     "blocks": ["handover"]})
    return {
        "schema": "frontier-finops-handover/1.0", "as_of": today, "target": target,
        "lifecycle": lifecycle, "structural_validation": "valid-with-gaps" if current["results"]["gaps"] else "valid",
        "pricing_completeness": "incomplete" if pricing else "evidenced",
        "ready": not gaps, "status": "blocked" if gaps else "planning-ready", "gaps": gaps,
        "owner_review": checked[0] if checked else None, "financial_permission": False, "limitations": BOUNDARY,
    }
