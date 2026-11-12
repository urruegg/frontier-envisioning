# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Audience projection BEFORE serialisation; no arithmetic or access-control claim.

The report is a derivative, not an importable authoritative baseline. Customer
outputs omit ALL technical hashes/pointers. Independent public cost rows can
remain visible; affected totals, units, evidence and readiness are withheld,
never rebuilt from a priced/public subset.
"""
from __future__ import annotations

import copy
import html
import re
from baseline_calc import calculate, validate_receipt
from baseline_model import _text, material_payload, model_fingerprint, validate_model
from baseline_records import BOUNDARY, SNAPSHOT_SCHEMA, _day, _refs, _snapshot, handover
from finops_preview import NOTICE, is_private, require_preview_ack

REPORT_SCHEMA = "frontier-agent-finops-report/1.0"
VIEW_SCHEMA = "frontier-agent-finops-view/1.0"
_CLASSES = {"customer-shareable", "customer-specific", "internal-only", "validation-required"}
_TECHNICAL = {"dependency_refs", "source_refs", "fx_refs", "src", "content_src", "sharing_classes",
              "customer_scopes", "internal", "visibility", "model_fingerprint", "results_fingerprint",
              "material_hash", "blueprint_fingerprint", "legacy_fingerprint"}
_WITHHELD = {"amount": None, "status": "withheld", "reason": "restricted-dependency"}
LIMITATIONS = BOUNDARY + " Customer scope is not authorisation. Internal output is private context, not shareable."


class _Projection:
    def __init__(self, model, audience, customer_scope, gaps):
        self.model, self.audience, self.scope = model, audience, customer_scope
        self.sources = {s["id"]: s for s in model.get("sources", []) if s.get("id")}
        self.unresolved = {g["field"].removesuffix(".sharingClassification")
                           for g in gaps if g["code"] == "sharing-validation"}
        self.private_ids = set()
        self.private_refs = set()
        self.technical_hashes = {model_fingerprint(model)} if audience == "customer" else set()
        self._collect_digests(model)
        self._collect_private_ids(model)

    def _collect_digests(self, value, digest_context=False):
        """Recognise known technical/ancestry digest values, not just output keys."""
        if self.audience != "customer":
            return
        if isinstance(value, dict):
            for key, child in value.items():
                name = key.lower()
                known = (name in {"fingerprint", "hash", "digest", "sha256", "hashes", "digests"}
                         or name.endswith(("_fingerprint", "_hash", "_digest", "_sha256",
                                           "_fingerprints", "_hashes", "_digests")))
                self._collect_digests(child, digest_context or known)
        elif isinstance(value, list):
            for child in value:
                self._collect_digests(child, digest_context)
        elif digest_context and isinstance(value, str):
            # A labelled external digest remains sensitive even when its
            # representation is not our SHA256 format. This is redaction,
            # not hash validation or financial receipt trust.
            if value.strip():
                self.technical_hashes.add(value.casefold())
            match = re.fullmatch(r"(?:sha256:)?([0-9a-f]{64})", value, re.IGNORECASE)
            if match:
                self.technical_hashes.add(match[1].lower())

    def _hidden_token(self, value):
        if self.audience != "customer" or not isinstance(value, str):
            return False
        folded = value.casefold()
        return (any(token.casefold() in folded for token in self.private_ids | self.private_refs)
                or any(digest.lower() in folded for digest in self.technical_hashes))

    @staticmethod
    def _financial_scalar(field):
        """Only validated schema positions, never arbitrary prose/digest fields."""
        return any(re.fullmatch(pattern, field) for pattern in (
            r"rates\[\d+\]\.(amount|pricing_block|currency|unit|effective_from|effective_to)",
            r"rates\[\d+\]\.verification\.verified_at",
            r"fx\[\d+\]\.(rate|from_currency|to_currency|date)",
            r"fx\[\d+\]\.verification\.verified_at",
            r"sources\[\d+\]\.lastValidatedAt",
            r"baseline\.(currency|as_of|start_month)",
            r"profile\.outcome\.unit",
            r"baseline\.scenarios\[\d+\]\.(monthly_runs\[\d+\]|success_share|outcomes_per_success|drivers\..+)",
        ))

    def _collect_private_ids(self, value, field="model", scope=None, parent_private=False, dynamic_key=None):
        if isinstance(value, dict):
            private = parent_private or self.restricted(value, field=field, inherited_scope=scope)
            if private:
                # Foreign keys to independently public entities do not make
                # those entities private. Gather protected identity definitions.
                self.private_ids.update(value[k] for k in ("id", "cost_driver_id") if isinstance(value.get(k), str))
                self.private_refs.update(value[k] for k in ("evidence_ref", "url", "delegation_evidence_ref")
                                         if isinstance(value.get(k), str) and value[k].strip())
                if dynamic_key is not None:
                    self.private_ids.add(dynamic_key)
            scope = value.get("customer_scope", scope)
            for key, child in value.items():
                self._collect_private_ids(child, key if field == "model" else f"{field}.{key}", scope, private,
                                          key if field.endswith(".driver_evidence") else None)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                self._collect_private_ids(child, f"{field}[{i}]", scope, parent_private)

    def restricted(self, record, *, field=None, inherited_scope=None, visited=None):
        """Classify actual source-parent ancestry, never an approval flag."""
        if not isinstance(record, dict):
            return False
        sharing = _text(record.get("sharingClassification"), "projection.sharingClassification")
        visibility = _text(record.get("visibility"), "projection.visibility")
        scope = _text(record.get("customer_scope", inherited_scope), "projection.customer_scope")
        if "internal" in record and type(record["internal"]) is not bool:
            raise ValueError("projection.internal must be an actual boolean")
        if self.audience == "internal":
            return False
        if is_private(record) or (field in self.unresolved):
            return True
        if "sharingClassification" in record and sharing is None:
            return True
        if visibility is not None and visibility not in {"internal", "customer", "public"}:
            return True
        if sharing is not None and (sharing not in _CLASSES or sharing in {"internal-only", "validation-required"}):
            return True
        if sharing == "customer-specific" and (not self.scope or scope != self.scope):
            return True
        visited = set() if visited is None else set(visited)
        for ref in _refs(record):
            source = self.sources.get(ref)
            if source is None:
                return True
            if ref not in visited:
                if self.restricted(source, field=self.source_field(ref), inherited_scope=scope, visited=visited | {ref}):
                    return True
        return False

    def source_field(self, ref):
        for i, row in enumerate(self.model.get("sources", [])):
            if row.get("id") == ref:
                return f"sources[{i}]"
        return None

    def raw(self, value, field="", inherited_scope=None):
        """Project authored context recursively; no unsafe opaque serialised blob."""
        if isinstance(value, dict):
            if self.restricted(value, field=field, inherited_scope=inherited_scope):
                return {"status": "withheld"}
            scope = value.get("customer_scope", inherited_scope)
            output = {}
            for k in sorted(value):
                v = value[k]
                if k in _TECHNICAL or k in {"finops_preview", "review_records", "handover", "results"}:
                    continue
                child_field = f"{field}.{k}" if field else k
                # Dynamic driver keys are identifiers, not numeric scalar names.
                fixed_financial_key = self._financial_scalar(child_field) and not field.endswith(".drivers")
                if not fixed_financial_key and self._hidden_token(k):
                    output[f"withheld-{len(output) + 1}"] = {"status": "withheld"}
                else:
                    output[k] = self.raw(v, child_field, scope)
            return output
        if isinstance(value, list):
            return [self.raw(v, f"{field}[{i}]", inherited_scope) for i, v in enumerate(value)]
        if not self._financial_scalar(field) and self._hidden_token(value):
            return {"status": "withheld"}
        return copy.deepcopy(value)

    def pointer_restricted(self, pointer):
        if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
            return True
        parts = pointer[1:].split("/") if pointer else []
        value, field, scope = self.model, "model", None
        if self.restricted(value, field=field):
            return True
        for encoded in parts:
            part = encoded.replace("~1", "/").replace("~0", "~")
            if isinstance(value, dict):
                scope = value.get("customer_scope", scope)
                value = value.get(part)
                field = part if field == "model" else f"{field}.{part}"
            elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                value = value[int(part)]
                field += f"[{int(part)}]"
            else:
                # Optional absent allocation policies are known explicit unknowns,
                # not a reason to declassify any present ancestor.
                value = None
            if self.restricted(value, field=field, inherited_scope=scope):
                return True
        return False

    def derived_restricted(self, record):
        if self.audience == "internal":
            return False
        if is_private(record):
            return True
        classes = list(record.get("sharing_classes", []))
        if "sharingClassification" in record:
            classes.append(record["sharingClassification"])
        if any(c not in _CLASSES or c in {"internal-only", "validation-required"} for c in classes):
            return True
        # Aggregate customer_scopes include PUBLIC context scopes too. Resolve
        # each actual classified dependency instead of treating that union as
        # a list of customer-specific access requirements.
        if "customer-specific" in classes and not record.get("dependency_refs"):
            return True
        if any(self.pointer_restricted(p) for p in record.get("dependency_refs", [])):
            return True
        return any(ref not in self.sources or self.restricted(self.sources[ref], field=self.source_field(ref))
                   for ref in record.get("source_refs", []))

    def derived(self, value):
        if isinstance(value, dict):
            if self.derived_restricted(value):
                if "cost" in value:  # withhold identity, quantity, evidence AND money
                    return {"status": "withheld", "quantity": None, "cost": dict(_WITHHELD)}
                return dict(_WITHHELD) if "amount" in value else {"status": "withheld"}
            # Recomputed result keys are fixed schema, not authored dictionary
            # aliases. Monetary/unit scalars are governed by dependency privacy,
            # never by coincident text tokens (e.g. private source ID "10").
            financial = {"amount", "currency", "quantity", "quantity_unit", "denominator",
                         "denominator_unit", "period", "basis", "status", "reason",
                         "date", "effective_from", "effective_to", "verified_at", "source_date"}
            return {k: copy.deepcopy(v) if k in financial else self.derived(v)
                    for k, v in value.items() if k not in _TECHNICAL}
        if isinstance(value, list):
            return [self.derived(v) for v in value]
        return {"status": "withheld"} if self._hidden_token(value) else copy.deepcopy(value)

    def any_restricted(self, value, field="model", scope=None):
        if isinstance(value, dict):
            if self.restricted(value, field=field, inherited_scope=scope):
                return True
            scope = value.get("customer_scope", scope)
            return any(self.any_restricted(v, k if field == "model" else f"{field}.{k}", scope)
                       for k, v in value.items())
        if isinstance(value, list):
            return any(self.any_restricted(v, f"{field}[{i}]", scope) for i, v in enumerate(value))
        return False

    def scenario_inputs(self):
        projected = []
        for i, scenario in enumerate(self.model.get("baseline", {}).get("scenarios", [])):
            field = f"baseline.scenarios[{i}]"
            row = self.raw(scenario, field, self.model.get("customer_scope"))
            if row.get("status") == "withheld":
                projected.append(row)
                continue
            for key in ("monthly_runs", "success_share", "outcomes_per_success"):
                pointer = f"/baseline/scenarios/{i}/driver_evidence/{key}"
                if self.pointer_restricted(pointer) or (key == "outcomes_per_success" and
                                                       self.pointer_restricted("/profile/outcome")):
                    row[key] = {"status": "withheld"}
            for key in scenario.get("drivers", {}):
                escaped = key.replace("~", "~0").replace("/", "~1")
                if self.pointer_restricted(f"/baseline/scenarios/{i}/driver_evidence/{escaped}"):
                    row["drivers"].pop(key, None)
                    row["drivers"][f"withheld-{len(row['drivers']) + 1}"] = {"status": "withheld"}
            projected.append(row)
        return projected


def _withheld_report(base):
    """Remove the whole linked target without exposing private identity/hash."""
    safe = {key: base[key] for key in ("schema", "notice", "maturity", "forecast_kind", "audience", "distribution",
                                      "as_of", "limitations", "financial_permission")}
    return {**safe, "mode": "withheld", "status": "withheld", "agent_id": None, "baseline": None, "currency": None,
            "profile": {"status": "withheld"}, "context": {"status": "withheld"},
            "scenarios": {}, "scenario_inputs": [], "evidence": {"status": "withheld"},
            "gaps": [{"code": "withheld-context", "blocks": ["handover"]}],
            "handover": {"status": "withheld", "ready": False, "financial_permission": False},
            "formulas": {"status": "withheld"}}


def project(model, reviews=(), *, as_of, audience, customer_scope=None, acknowledge_finops_preview=False):
    """Return one exact report DTO; accept calculated draft OR frozen wrapper."""
    require_preview_ack(acknowledge_finops_preview)
    _day(as_of)
    if not isinstance(audience, str) or audience not in {"internal", "customer"}:
        raise ValueError("audience must be internal or customer")
    if customer_scope is not None and (not isinstance(customer_scope, str) or not customer_scope.strip()):
        raise ValueError("customer_scope must be a nonblank string or null")
    if not isinstance(reviews, (tuple, list)):
        raise ValueError("reviews must be an explicit sequence")
    snapshot = None
    if isinstance(model, dict) and model.get("schema") == SNAPSHOT_SCHEMA:
        snapshot = model
        model, _, _ = _snapshot(snapshot, as_of=as_of)
    else:
        validate_receipt(model, as_of=as_of, acknowledge_finops_preview=True)
    gaps = validate_model(model, as_of=as_of)
    current = calculate(model, as_of=as_of, acknowledge_finops_preview=True)
    material = material_payload(model)
    projector = _Projection(material, audience, customer_scope, gaps)
    if audience == "customer":
        # Both receipts have already been recomputed/validated. Recognise their
        # digests for redaction only, never as a substitute for calculation.
        projector.technical_hashes.update({
            model["finops_preview"]["calculations"]["baseline"]["results_fingerprint"],
            current["finops_preview"]["calculations"]["baseline"]["results_fingerprint"],
        })
    base = {
        "schema": REPORT_SCHEMA, "notice": NOTICE, "maturity": "Preview", "forecast_kind": "estimate",
        "audience": audience, "distribution": "private-context-not-shareable" if audience == "internal"
        else "scoped-derivative-not-authorisation",
        "as_of": as_of.isoformat(), "limitations": LIMITATIONS, "financial_permission": False,
    }
    if snapshot:
        readiness = handover(snapshot, reviews, as_of=as_of, acknowledge_finops_preview=True)
    else:
        if reviews:
            raise ValueError("external reviews require a frozen snapshot, not an editable draft")
        readiness = {"status": "blocked", "ready": False, "lifecycle": "draft", "as_of": as_of.isoformat(),
                     "pricing_completeness": "not-reviewed", "structural_validation": "valid-with-gaps" if gaps else "valid",
                     "gaps": [*gaps, {"code": "unfrozen-draft", "field": "review",
                                     "message": "Freeze and obtain externally evidenced owner review.", "blocks": ["handover"]}],
                     "owner_review": None, "financial_permission": False, "limitations": BOUNDARY}
    # Snapshot/review validation above must precede collecting externally
    # asserted ancestry. These tokens govern redaction, never receipt trust.
    for review in reviews:
        projector._collect_digests(review)
        projector._collect_private_ids(review, "review")
    # Do not expose even the link/version when the whole baseline envelope is private.
    if (projector.restricted(material, field="model") or
            projector.restricted(material.get("profile", {}), field="profile",
                                 inherited_scope=material.get("customer_scope"))):
        return _withheld_report(base)
    private_context = projector.any_restricted(material)
    private_review = any(not r.get("sharingClassification") or projector.any_restricted(r, "review")
                         or not str(r.get("sharingClassification")).strip() for r in reviews)
    if audience == "customer":
        if private_context or private_review:
            readiness = {"status": "withheld", "ready": False, "financial_permission": False,
                         "limitations": BOUNDARY}
            visible_gaps = [{"code": "withheld-context", "blocks": ["handover"]}]
        else:
            readiness = projector.raw(readiness, "handover")
            # Hashes bind all material, not only visible arithmetic dependencies.
            readiness.pop("target", None)
            if isinstance(readiness.get("owner_review"), dict):
                readiness["owner_review"].pop("material_hash", None)
            visible_gaps = [{"code": g["code"], "message": g["message"], "blocks": g["blocks"]}
                            for g in current["results"]["gaps"]]
    else:
        visible_gaps = copy.deepcopy(current["results"]["gaps"])
    baseline = material.get("baseline", {})
    baseline_private = projector.restricted(baseline, field="baseline",
                                            inherited_scope=material.get("customer_scope"))
    profile = projector.raw(material.get("profile", {}), "profile", material.get("customer_scope"))
    baseline_envelope = projector.raw({k: baseline[k] for k in
                                      ("id", "version", "as_of", "start_month", "currency", "sharingClassification",
                                       "customer_scope", "internal", "visibility", "src", "content_src") if k in baseline},
                                     "baseline", material.get("customer_scope"))
    return {
        **base, "mode": material.get("mode"), "status": "partial" if gaps or not readiness.get("ready") else "planning-ready",
        "agent_id": profile.get("agent_id") if isinstance(profile.get("agent_id"), str) else None, "profile": profile,
        "baseline": baseline_envelope,
        "currency": baseline_envelope.get("currency") if isinstance(baseline_envelope.get("currency"), str) else None,
        "context": {"status": "withheld"} if baseline_private else {
                    k: projector.raw(baseline.get(k), f"baseline.{k}", baseline.get("customer_scope",
                                                                                material.get("customer_scope")))
                    for k in ("scope", "annualisation", "assumptions", "exclusions", "risks", "confidence")},
        "formulas": {"status": "withheld"} if baseline_private else {
                     "monthly": "runs × driver quantity ÷ pricing block × rate × evidenced FX; plus fixed lines",
                     "annual_recurring": "sum of twelve unrounded monthly recurring contributions",
                     "first_year": "annual recurring + one-time build",
                     "units": "period cost / attempted runs, successful runs or confirmed outcome units",
                     "rounding": "HALF_UP: final money 2 places; final unit ratios 6 places; no JS financial arithmetic"},
        "scenarios": {} if baseline_private else projector.derived(current["results"]["scenarios"]),
        "scenario_inputs": [] if baseline_private else projector.scenario_inputs(),
        "evidence": {"status": "withheld"} if baseline_private else {
                     k: projector.raw(material.get(k, []), k, material.get("customer_scope"))
                     for k in ("sources", "rates", "fx")},
        "gaps": visible_gaps, "handover": readiness,
    }


def _cell(value):
    text = html.escape(str(value) if value is not None else "unavailable", quote=True)
    text = text.replace("\r", " ").replace("\n", " / ")
    return re.sub(r"([\\|`*_\[\]()!#])", r"\\\1", text)


def render_markdown(report):
    """Only projected DTOs; evidence references are plain escaped text, not links."""
    if not isinstance(report, dict) or report.get("schema") != REPORT_SCHEMA:
        raise ValueError("render_markdown requires a projected report DTO")
    rows = ["# Agent FinOps — Preview", "", _cell(report.get("notice")), "", _cell(report.get("limitations")), "",
            f"Status: {_cell(report.get('status'))}; date: {_cell(report.get('as_of'))}; "
            f"currency: {_cell(report.get('currency'))}", "",
            "| Scenario | Annual recurring | One-time | First year |",
            "|---|---|---|---|"]
    for identity in ("low", "expected", "high"):
        if identity not in report.get("scenarios", {}):
            continue
        scenario = report["scenarios"][identity]
        cells = []
        for key in ("annual_recurring", "one_time", "first_year"):
            money = scenario.get(key, {})
            cells.append(_cell(money.get("amount")) + " — " + _cell(money.get("status")))
        rows.append("| " + " | ".join([_cell(identity), *cells]) + " |")

    def detail(value, path=""):
        if isinstance(value, dict):
            for key in sorted(value):
                child = value[key]
                detail(child, f"{path} / {key}" if path else key)
        elif isinstance(value, list):
            for i, child in enumerate(value):
                detail(child, f"{path} / {i + 1}")
        else:
            rows.append(f"- {_cell(path)}: {_cell(value)}")

    for key in ("baseline", "profile", "formulas", "context", "scenario_inputs", "scenarios", "evidence", "gaps", "handover"):
        rows.extend(["", f"## {_cell(key)}", ""])
        detail(report.get(key))
    return "\n".join(rows) + "\n"
