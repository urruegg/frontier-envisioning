# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Pure baseline/1.0 contract validation, not a calculator or approval service.

Gaps have code/field/message/blocks. Every gap blocks ``handover``;
``calculation`` additionally marks missing cost-arithmetic inputs,
``unit-metrics`` missing denominators, and ``customer-export`` unresolved
sharing. Evidence-only gaps do not invent missing numbers. Synthetic inputs
may demonstrate arithmetic but can never establish commercial verification.
These checks do not perform owner review, audience projection or handover.

Decimal and date helpers are private reusable parsing boundaries for the
successor calculator. No helper reads files, retrieves URLs or mutates inputs.
"""
from __future__ import annotations

import copy
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit

from finops_preview import fingerprint

_SCHEMA = "frontier-finops-baseline/1.0"
_OUTPUTS = {"results", "finops_preview", "review_records", "handover"}
_CURRENCIES = {"CHF", "EUR", "USD"}
_SHARING = {"customer-shareable", "customer-specific", "internal-only", "validation-required"}
_UNITS = {"token", "operation", "build", "run", "call", "credit", "user", "hour",
          "GB", "GB-month", "outcome", "request", "retrieval", "share"}
_CATEGORIES = {"licence", "copilot-credit", "model-token", "agent-runtime", "tool-call", "data",
               "integration", "observability", "security-governance", "infrastructure",
               "support-operations", "build-one-time", "other"}
_SCENARIOS = {"low", "expected", "high"}
_DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def material_payload(model) -> dict:
    """Detach authored data; omit ONLY the four owned root output locations."""
    model = _object(model, "model")
    return copy.deepcopy({key: value for key, value in model.items() if key not in _OUTPUTS})


def model_fingerprint(model) -> str:
    """Use the existing canonical hash, without stripping nested authored keys."""
    return fingerprint(material_payload(model))


def _error(field, reason):
    # Never interpolate a supplied price, source body or reference value.
    raise ValueError(f"{field}: {reason}")


def _object(value, field):
    if not isinstance(value, dict):
        _error(field, "must be an object")
    return value


def _list(value, field):
    if not isinstance(value, list):
        _error(field, "must be a list")
    return value


def _text(value, field):
    if value is None:
        return None
    if not isinstance(value, str):
        _error(field, "must be a string or null")
    return value if value.strip() else None


def _enum(value, allowed, field):
    value = _text(value, field)
    if value is not None and value not in allowed:
        _error(field, "unsupported value")
    return value


def _integer(value, field, *, minimum=0):
    if value is None:
        return None
    if type(value) is not int or value < minimum:
        _error(field, f"must be an integer >= {minimum}, not a boolean")
    return value


def _decimal(value, field, *, positive=False, share=False):
    """Return Decimal or explicit unknown None; never infer zero."""
    if value is None:
        return None
    if not isinstance(value, str) or not _DECIMAL.fullmatch(value):
        _error(field, "must be a finite non-negative decimal string or null")
    try:
        number = Decimal(value)
    except InvalidOperation:
        _error(field, "must be a finite non-negative decimal string or null")
    if not number.is_finite() or number < 0 or (positive and number <= 0):
        _error(field, "must be a finite positive decimal string" if positive else "must be finite and non-negative")
    if share and number > 1:
        _error(field, "share must be in [0,1]")
    return number


def _date(value, field, *, timestamp=False):
    """ISO calendar dates; source timestamps must include an explicit timezone."""
    value = _text(value, field)
    if value is None:
        return None
    try:
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
            return date.fromisoformat(value)
        if timestamp and re.match(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T", value):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return parsed.date()
    except ValueError:
        pass
    _error(field, "must be an ISO date" + (" or timezone-qualified timestamp" if timestamp else ""))


def _gap(gaps, code, field, message, *blocks):
    gap = {"code": code, "field": field, "message": message,
           "blocks": ["handover", *dict.fromkeys(blocks)]}
    if gap not in gaps:
        gaps.append(gap)


def _needed(value, gaps, code, field, message, *blocks):
    if value is None or value == "" or value == []:
        _gap(gaps, code, field, message, *blocks)
    return value


def _mapping(parent, key, field):
    value = parent.get(key)
    return {} if value is None else _object(value, field)


def _rows(parent, key, field):
    value = parent.get(key)
    return [] if value is None else _list(value, field)


def _index(rows, field, gaps, *, key="id"):
    indexed = {}
    for i, row in enumerate(rows):
        path = f"{field}[{i}]"
        row = _object(row, path)
        identity = _text(row.get(key), f"{path}.{key}")
        if identity is None:
            _gap(gaps, "missing-identity", f"{path}.{key}", "Supply a stable record identity.")
        elif identity in indexed:
            _error(f"{path}.{key}", "duplicate identity")
        else:
            indexed[identity] = row
    return indexed


def _ref(value, index, field, gaps, *, code="missing-evidence", blocks=()):
    value = _text(value, field)
    if value is None:
        _gap(gaps, code, field, "Supply the explicit reference.", *blocks)
        return None
    if value not in index:
        _error(field, "unresolved reference")
    return index[value]


def _sharing(record, field, gaps):
    supplied = _text(record.get("sharingClassification"), f"{field}.sharingClassification")
    if supplied not in _SHARING or supplied == "validation-required":
        _gap(gaps, "sharing-validation", f"{field}.sharingClassification",
             "Unknown sharing remains validation-required; no distribution clearance is inferred.", "customer-export")
    scope = _text(record.get("customer_scope"), f"{field}.customer_scope")
    if supplied == "customer-specific":
        _needed(scope, gaps, "missing-customer-scope", f"{field}.customer_scope",
                "Identify the customer scope before customer-specific sharing.", "customer-export")


def _lineage(value, field, sources, gaps):
    """Validate, but never relocate or discard, material legacy restrictions."""
    if isinstance(value, dict):
        prefix = f"{field}." if field else ""
        if "sharingClassification" in value:
            _sharing(value, field or "model", gaps)
        if "internal" in value and type(value["internal"]) is not bool:
            _error(f"{prefix}internal", "must be a boolean")
        if "visibility" in value:
            _text(value["visibility"], f"{prefix}visibility")
        for key in ("src", "content_src"):
            if key in value and value[key] is not None:
                refs = value[key]
                if isinstance(refs, str):
                    refs = refs.replace(",", " ").split()
                for i, ref in enumerate(_list(refs, f"{prefix}{key}")):
                    _ref(ref, sources, f"{prefix}{key}[{i}]", gaps)
        for key, child in value.items():
            if key == "source_id":
                _ref(child, sources, f"{prefix}{key}", gaps)
            _lineage(child, f"{prefix}{key}", sources, gaps)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _lineage(child, f"{field}[{i}]", sources, gaps)


def _freshness(record, field, gaps):
    policy = record.get("freshness_policy")
    if policy is None:
        _gap(gaps, "missing-freshness-policy", f"{field}.freshness_policy",
             "Declare a freshness policy; no universal rate lifetime is assumed.")
        return None
    policy = _object(policy, f"{field}.freshness_policy")
    return _needed(_integer(policy.get("max_age_days"), f"{field}.freshness_policy.max_age_days"),
                   gaps, "missing-freshness-policy", f"{field}.freshness_policy.max_age_days",
                   "Declare the maximum evidence age in days.")


def _age(validated, as_of, max_age, field, gaps, stale_code):
    if validated is None:
        _gap(gaps, "missing-evidence", field, "Supply the dated evidence.")
    elif validated > as_of:
        _gap(gaps, "future-evidence", field, "Evidence is later than the evaluation date.")
    elif max_age is not None and (as_of - validated).days > max_age:
        _gap(gaps, stale_code, field, "Evidence exceeds the declared freshness policy.")


def _evidence(record, field, sources, gaps, *, claim, as_of, max_age=None):
    source = _ref(record.get("source_id"), sources, f"{field}.source_id", gaps)
    if source is None:
        return
    if claim not in _rows(source, "applicability", f"{field}.source.applicability") or (
            claim in {"rate", "fx"} and source.get("type") == "public-reference"):
        _gap(gaps, "source-applicability", f"{field}.source_id",
             "This source does not evidence the required claim; concept references do not verify prices.")
    status = source.get("validationStatus")
    if source.get("type") == "synthetic" or status == "synthetic":
        _gap(gaps, "synthetic-evidence", f"{field}.source_id",
             "Invented evidence is demonstrative, never commercial verification or financial approval.")
    elif status != "validated":
        _gap(gaps, "unverified-source", f"{field}.source_id", "Source validation remains outstanding.")
    if max_age is not None:
        _age(_date(source.get("lastValidatedAt"), f"{field}.source.lastValidatedAt", timestamp=True),
             as_of, max_age, f"{field}.source.lastValidatedAt", gaps, "stale-source")


def _validate_sources(rows, as_of, gaps):
    sources = _index(rows, "sources", gaps)
    for i, source in enumerate(rows):
        field = f"sources[{i}]"
        _sharing(source, field, gaps)
        _needed(_enum(source.get("type"), {"synthetic", "public-reference", "commercial",
                                         "customer-evidence", "internal-evidence"}, f"{field}.type"),
                gaps, "missing-evidence", f"{field}.type", "Declare the evidence type.")
        for key in ("title", "supported_claim"):
            _needed(_text(source.get(key), f"{field}.{key}"), gaps, "missing-evidence",
                    f"{field}.{key}", "Describe the source and the claim it supports.")
        url = _text(source.get("url"), f"{field}.url")
        evidence_ref = _text(source.get("evidence_ref"), f"{field}.evidence_ref")
        if not url and not evidence_ref:
            _gap(gaps, "missing-evidence", field, "Supply a URL or opaque evidence reference; no retrieval is performed.")
        if url:
            try:
                parts = urlsplit(url)
                valid_url = parts.scheme in {"http", "https"} and bool(parts.netloc)
            except ValueError:
                valid_url = False
            if not valid_url:
                _error(f"{field}.url", "must be an HTTP(S) reference URL")
        applicability = _rows(source, "applicability", f"{field}.applicability")
        _needed(applicability, gaps, "missing-evidence", f"{field}.applicability", "Declare supported claim types.")
        for j, claim in enumerate(applicability):
            path = f"{field}.applicability[{j}]"
            _needed(_enum(claim, {"concept", "quantity", "outcome", "assumption", "rate", "fx"}, path),
                    gaps, "source-applicability", path, "Declare the supported claim type for this entry.")
        status = _enum(source.get("validationStatus"), {"validated", "synthetic", "unverified", "validation-required"},
                       f"{field}.validationStatus")
        if source.get("type") == "synthetic" or status == "synthetic":
            _gap(gaps, "synthetic-evidence", field, "Synthetic evidence cannot satisfy financial handover.")
        elif status != "validated":
            _gap(gaps, "unverified-source", field, "Source validation remains outstanding.")
        max_age = _freshness(source, field, gaps)
        _age(_date(source.get("lastValidatedAt"), f"{field}.lastValidatedAt", timestamp=True),
             as_of, max_age, f"{field}.lastValidatedAt", gaps, "stale-source")
    return sources


def _verification(record, field, sources, as_of, gaps, *, kind):
    max_age = _freshness(record, field, gaps)
    verification = _mapping(record, "verification", f"{field}.verification")
    status = _enum(verification.get("status"), {"verified", "synthetic", "unverified"},
                   f"{field}.verification.status")
    if status == "synthetic":
        _gap(gaps, "synthetic-evidence", f"{field}.verification", "Synthetic verification is not commercial evidence.")
    elif status != "verified":
        _gap(gaps, f"unverified-{kind}", f"{field}.verification", "Current verification is required for handover.")
    _age(_date(verification.get("verified_at"), f"{field}.verification.verified_at", timestamp=True),
         as_of, max_age, f"{field}.verification.verified_at", gaps, f"stale-{kind}")
    _evidence(record, field, sources, gaps, claim=kind, as_of=as_of, max_age=max_age)


def _validate_rates(rows, sources, as_of, gaps):
    rates = _index(rows, "rates", gaps)
    for i, rate in enumerate(rows):
        # Retain parsed comparison fields without changing the authored record.
        rate = dict(rate)
        field = f"rates[{i}]"
        _sharing(rate, field, gaps)
        _needed(_integer(rate.get("version"), f"{field}.version", minimum=1), gaps,
                "missing-version", f"{field}.version", "Supply the rate version.")
        _needed(_decimal(rate.get("amount"), f"{field}.amount"), gaps, "unpriced", f"{field}.amount",
                "Supply an explicit rate; unknown is not zero.", "calculation")
        for key, allowed in (("currency", _CURRENCIES), ("unit", _UNITS)):
            rate[key] = _needed(_enum(rate.get(key), allowed, f"{field}.{key}"), gaps, "missing-rate-input",
                                f"{field}.{key}", "Declare the rate currency and typed unit.", "calculation")
        _needed(_decimal(rate.get("pricing_block"), f"{field}.pricing_block", positive=True), gaps,
                "missing-rate-input", f"{field}.pricing_block", "Declare the positive pricing block.", "calculation")
        for key in ("service", "meter"):
            rate[key] = _needed(_text(rate.get(key), f"{field}.{key}"), gaps, "missing-rate-input",
                                f"{field}.{key}", "Identify the priced service and meter.")
        identity = _text(rate.get("id"), f"{field}.id")
        if identity is not None:
            rates[identity] = rate
        start = _date(rate.get("effective_from"), f"{field}.effective_from")
        end = _date(rate.get("effective_to"), f"{field}.effective_to")
        if start is not None and end is not None and end < start:
            _error(f"{field}.effective_to", "precedes effective_from")
        if start is None or end is None:
            _gap(gaps, "missing-evidence", field, "Declare both rate effective dates.")
        if (start is not None and start > as_of) or (end is not None and end < as_of):
            _gap(gaps, "inactive-rate", field, "Rate is not effective at the evaluation date.")
        _verification(rate, field, sources, as_of, gaps, kind="rate")
    return rates


def _validate_fx(rows, sources, as_of, gaps):
    _index(rows, "fx", gaps)
    pairs = {}
    for i, fx in enumerate(rows):
        field = f"fx[{i}]"
        _sharing(fx, field, gaps)
        _needed(_integer(fx.get("version"), f"{field}.version", minimum=1), gaps,
                "missing-version", f"{field}.version", "Supply the FX version.")
        pair = tuple(_enum(fx.get(key), _CURRENCIES, f"{field}.{key}") for key in ("from_currency", "to_currency"))
        for key, value in zip(("from_currency", "to_currency"), pair):
            _needed(value, gaps, "missing-fx", f"{field}.{key}", "Declare the explicit currency pair.", "calculation")
        if all(pair):
            if pair[0] == pair[1]:
                _error(field, "FX pair must use distinct currencies")
            if pair in pairs:
                _error(field, "ambiguous duplicate fx pair")
            pairs[pair] = fx
        _needed(_decimal(fx.get("rate"), f"{field}.rate", positive=True), gaps,
                "missing-fx", f"{field}.rate", "Supply an explicit positive FX rate.", "calculation")
        method = _enum(fx.get("method"), {"evidenced", "spot", "contract", "synthetic"}, f"{field}.method")
        _needed(method, gaps, "missing-evidence", f"{field}.method", "Declare an evidenced FX method; never a list-price ratio.")
        if method == "synthetic":
            _gap(gaps, "synthetic-evidence", f"{field}.method", "Synthetic FX cannot establish commercial verification.")
        fx_date = _date(fx.get("date"), f"{field}.date")
        _verification(fx, field, sources, as_of, gaps, kind="fx")
        _age(fx_date, as_of, _freshness(fx, field, gaps), f"{field}.date", gaps, "stale-fx")
    return pairs


def _validate_profile(profile, sources, as_of, gaps, blueprint):
    field = "profile"
    _sharing(profile, field, gaps)
    agent_id = _needed(_text(profile.get("agent_id"), "profile.agent_id"), gaps, "missing-agent",
                       "profile.agent_id", "Link an existing Agent Canvas ID.")
    _needed(_text(profile.get("name"), "profile.name"), gaps, "missing-profile", "profile.name", "Name the agent.")
    owners = _mapping(profile, "owners", "profile.owners")
    for key in ("business", "technical", "finance"):
        _needed(_text(owners.get(key), f"profile.owners.{key}"), gaps, "missing-owner",
                f"profile.owners.{key}", "Name the accountable owner or role.")
    outcome = _mapping(profile, "outcome", "profile.outcome")
    _sharing(outcome, "profile.outcome", gaps)
    _needed(_text(outcome.get("definition"), "profile.outcome.definition"), gaps, "missing-outcome",
            "profile.outcome.definition", "Define the human-confirmed business outcome.", "unit-metrics")
    outcome_unit = _needed(_enum(outcome.get("unit"), _UNITS, "profile.outcome.unit"), gaps, "missing-outcome",
                           "profile.outcome.unit", "Declare the business outcome unit.", "unit-metrics")
    _evidence(outcome, "profile.outcome", sources, gaps, claim="outcome", as_of=as_of)
    for key, code in (("demand_context", "missing-demand-context"), ("target_context", "missing-target-context"),
                      ("measurement_plan", "missing-measurement")):
        _needed(_text(profile.get(key), f"profile.{key}"), gaps, code, f"profile.{key}", "Supply the editable profile context.")
    guardrails = _rows(profile, "guardrails", "profile.guardrails")
    _needed(guardrails, gaps, "missing-guardrails", "profile.guardrails", "Declare owner-set guardrails and controls.")
    for i, guardrail in enumerate(guardrails):
        _needed(_text(guardrail, f"profile.guardrails[{i}]"), gaps, "missing-guardrails",
                f"profile.guardrails[{i}]", "Describe the owner-set control.")
    if blueprint is not None:
        blueprint = _object(blueprint, "blueprint")
        if blueprint.get("schema") != "frontier-blueprint/1.0":
            _error("blueprint.schema", "unsupported blueprint schema")
        agents = []
        for i, domain in enumerate(_rows(blueprint, "domains", "blueprint.domains")):
            domain = _object(domain, f"blueprint.domains[{i}]")
            agents.extend(_rows(domain, "agents", f"blueprint.domains[{i}].agents"))
            if domain.get("lead") is not None:
                agents.append(_object(domain["lead"], f"blueprint.domains[{i}].lead"))
        known = _index(agents, "blueprint.agents", gaps)
        if agent_id is not None and agent_id not in known:
            _error("profile.agent_id", "unresolved blueprint agent reference")
    return agent_id, outcome_unit


def _validate_notes(baseline, sources, as_of, gaps):
    for key in ("assumptions", "exclusions", "risks"):
        rows = _rows(baseline, key, f"baseline.{key}")
        if baseline.get(key) is None or (not rows and key != "exclusions"):
            _gap(gaps, f"missing-{key}", f"baseline.{key}", "Record the declared scope context explicitly.")
        _index(rows, f"baseline.{key}", gaps)
        for i, row in enumerate(rows):
            field = f"baseline.{key}[{i}]"
            _sharing(row, field, gaps)
            _needed(_text(row.get("description"), f"{field}.description"), gaps, f"missing-{key}",
                    f"{field}.description", "Describe the authored scope context.")
            if key == "exclusions":
                _needed(_text(row.get("reason"), f"{field}.reason"), gaps, "missing-exclusions",
                        f"{field}.reason", "Explain the exclusion; declared coverage is not real-world completeness.")
            _evidence(row, field, sources, gaps, claim="assumption", as_of=as_of)
    confidence = _mapping(baseline, "confidence", "baseline.confidence")
    _needed(_enum(confidence.get("level"), {"low", "medium", "high"}, "baseline.confidence.level"), gaps,
            "missing-confidence", "baseline.confidence.level", "Declare confidence separately from validation.")
    _needed(_text(confidence.get("rationale"), "baseline.confidence.rationale"), gaps,
            "missing-confidence", "baseline.confidence.rationale", "Explain confidence and uncertainty.")
    _evidence(confidence, "baseline.confidence", sources, gaps, claim="assumption", as_of=as_of)


def _validate_scenarios(rows, sources, as_of, gaps, *, outcome_unit, line_driver_ids):
    scenarios = _index(rows, "baseline.scenarios", gaps)
    if set(scenarios) - _SCENARIOS:
        _error("baseline.scenarios", "only low, expected and high scenario IDs are supported")
    if set(scenarios) != _SCENARIOS:
        _gap(gaps, "missing-scenario", "baseline.scenarios", "Author exactly low, expected and high scenarios.", "calculation")
    driver_ids = set()
    parsed = []
    normalized_rows = []
    for i, scenario in enumerate(rows):
        field = f"baseline.scenarios[{i}]"
        _sharing(scenario, field, gaps)
        runs = scenario.get("monthly_runs")
        if runs is None:
            runs = [None] * 12
        runs = _list(runs, f"{field}.monthly_runs")
        if len(runs) != 12:
            _error(f"{field}.monthly_runs", "must contain exactly twelve authored months")
        demand = []
        for j, value in enumerate(runs):
            demand.append(_needed(_decimal(value, f"{field}.monthly_runs[{j}]"), gaps, "missing-quantity",
                                  f"{field}.monthly_runs[{j}]", "Supply monthly demand; unknown is not zero.", "calculation"))
        success = _needed(_decimal(scenario.get("success_share"), f"{field}.success_share", share=True), gaps,
                          "missing-outcome", f"{field}.success_share", "Supply the success share.", "unit-metrics")
        outcomes = _needed(_decimal(scenario.get("outcomes_per_success"), f"{field}.outcomes_per_success"), gaps,
                           "missing-outcome", f"{field}.outcomes_per_success", "Supply outcomes per successful run.", "unit-metrics")
        drivers = _mapping(scenario, "drivers", f"{field}.drivers")
        evidence = _mapping(scenario, "driver_evidence", f"{field}.driver_evidence")
        values = {key: _needed(_decimal(value, f"{field}.drivers.{key}"), gaps, "missing-quantity",
                              f"{field}.drivers.{key}", "Supply the explicit driver quantity.", "calculation")
                  for key, value in drivers.items()}
        driver_ids.update(drivers)
        units = {"monthly_runs": "run", "success_share": "share", "outcomes_per_success": outcome_unit}
        # Evidence declares the driver even while its editable quantity is absent.
        driver_ids.update(set(evidence) - set(units))
        sourced = set()
        normalized_evidence = {}
        for key in dict.fromkeys([*units, *drivers, *evidence]):
            path = f"{field}.driver_evidence.{key}"
            record = _mapping(evidence, key, path)
            _sharing(record, path, gaps)
            denominator = key in {"success_share", "outcomes_per_success"}
            unit = _needed(_enum(record.get("unit"), _UNITS, f"{path}.unit"), gaps,
                           "missing-outcome" if denominator else "missing-quantity",
                           f"{path}.unit", "Declare the typed driver unit.",
                           "unit-metrics" if denominator else "calculation")
            if key in units and units[key] is not None and unit is not None and unit != units[key]:
                _error(f"{path}.unit", "contradicts the declared driver unit")
            normalized_evidence[key] = {**record, "unit": unit}
            _evidence(record, path, sources, gaps, claim="quantity", as_of=as_of)
            source = sources.get(record.get("source_id"))
            if unit is not None and source is not None and "quantity" in (source.get("applicability") or []):
                sourced.add(key)
        parsed.append((demand, {"success_share": success, "outcomes_per_success": outcomes}, values, sourced))
        normalized_rows.append({**scenario, "driver_evidence": normalized_evidence})
    if len(parsed) == 3:
        demands = [tuple(row[0]) for row in parsed]
        if all(None not in row for row in demands) and len(set(demands)) == 1:
            _gap(gaps, "scenario-demand", "baseline.scenarios", "Demand must differ between the three scenarios.")
        # Only dependencies that affect a cost line or an outcome denominator
        # qualify; a familiar but unused driver name is not economic variation.
        uncertainties = [[row[1][key] if key in row[3] else None for row in parsed]
                         for key in ("success_share", "outcomes_per_success")]
        uncertainties.extend([[row[2].get(key) if key in row[3] else None for row in parsed]
                              for key in sorted(line_driver_ids)])
        if not any(all(v is not None for v in values) and len(set(values)) > 1 for values in uncertainties):
            _gap(gaps, "scenario-uncertainty", "baseline.scenarios",
                 "Vary a sourced uncertainty driver besides demand, not a blanket total multiplier.")
    return driver_ids, normalized_rows


def _validate_lines(rows, scope, scenarios, driver_ids, rates, fx_pairs, currency, sources, as_of, gaps):
    _index(rows, "baseline.lines", gaps)
    covered = set()
    for i, line in enumerate(rows):
        line = dict(line)
        field = f"baseline.lines[{i}]"
        _sharing(line, field, gaps)
        cost_driver = _text(line.get("cost_driver_id"), f"{field}.cost_driver_id")
        _ref(cost_driver, scope, f"{field}.cost_driver_id", gaps, code="missing-scope")
        covered.add(cost_driver)
        for key, allowed in (("category", _CATEGORIES), ("frequency", {"monthly", "one-time"}),
                             ("quantity_mode", {"per-run", "fixed"}), ("quantity_unit", _UNITS)):
            line[key] = _needed(_enum(line.get(key), allowed, f"{field}.{key}"), gaps, "missing-line-input",
                                f"{field}.{key}", "Declare the explicit cost-line contract.",
                                *(("calculation",) if key != "category" else ()))
        for key in ("service", "meter"):
            line[key] = _needed(_text(line.get(key), f"{field}.{key}"), gaps, "missing-line-input",
                                f"{field}.{key}", "Identify the service and meter.")
        driver_id = _text(line.get("driver_id"), f"{field}.driver_id")
        if driver_id is None:
            _gap(gaps, "missing-quantity", f"{field}.driver_id", "Declare the quantity driver.", "calculation")
        elif driver_id not in driver_ids:
            _error(f"{field}.driver_id", "unresolved driver reference")
        for j, scenario in enumerate(scenarios):
            path = f"baseline.scenarios[{j}]"
            if driver_id and driver_id not in (scenario.get("drivers") or {}):
                _gap(gaps, "missing-quantity", f"{path}.drivers.{driver_id}", "Supply this scenario's driver quantity.", "calculation")
            evidence = (scenario.get("driver_evidence") or {}).get(driver_id) or {}
            if evidence.get("unit") is not None and line.get("quantity_unit") is not None:
                if evidence["unit"] != line["quantity_unit"]:
                    _error(f"{path}.driver_evidence.{driver_id}.unit", "does not match the line quantity_unit")
        rate = _ref(line.get("rate_id"), rates, f"{field}.rate_id", gaps, code="unpriced", blocks=("calculation",))
        if rate is not None:
            for left, right in (("quantity_unit", "unit"), ("service", "service"), ("meter", "meter")):
                if line.get(left) is not None and rate.get(right) is not None and line[left] != rate[right]:
                    _error(f"{field}.{left}", f"does not match rate.{right}")
            if currency and rate.get("currency") and rate["currency"] != currency:
                if (rate["currency"], currency) not in fx_pairs:
                    _gap(gaps, "missing-fx", f"{field}.rate_id", "Supply an explicit evidenced FX pair.", "calculation")
        policy = line.get("allocation_policy")
        if "shared" in line and type(line["shared"]) is not bool:
            _error(f"{field}.shared", "must be a boolean")
        if line.get("shared") is True and policy is None:
            _gap(gaps, "missing-allocation", f"{field}.allocation_policy", "Shared costs require an explicit allocation policy.", "calculation")
        if policy is not None:
            policy = _object(policy, f"{field}.allocation_policy")
            path = f"{field}.allocation_policy"
            _sharing(policy, path, gaps)
            for key in ("id", "method"):
                _needed(_text(policy.get(key), f"{path}.{key}"), gaps, "missing-allocation",
                        f"{path}.{key}", "Name and explain the allocation policy.")
            _needed(_decimal(policy.get("share"), f"{path}.share", share=True), gaps, "missing-quantity",
                    f"{path}.share", "Supply the allocated share.", "calculation")
            _evidence(policy, path, sources, gaps, claim="assumption", as_of=as_of)
    for i, driver in enumerate(scope):
        if driver not in covered:
            _gap(gaps, "uncovered-driver", f"baseline.scope[{i}]", "This in-scope cost driver has no priced line.", "calculation")


def validate_model(model, *, as_of, blueprint=None) -> list:
    """Return draft gaps, or field-specific ValueError for malformed inputs.

    ``as_of`` is an explicit datetime.date (not datetime or an inferred clock).
    Validated structural shape is not pricing completeness or owner approval.
    No numeric result, receipt or review record is produced or consumed here.
    """
    if type(as_of) is not date:
        _error("as_of", "must be an explicit datetime.date")
    model = _object(model, "model")
    if model.get("schema") != _SCHEMA:
        _error("schema", "unsupported baseline schema")
    gaps = []
    _sharing(model, "model", gaps)
    mode = _needed(_enum(model.get("mode"), {"planning", "synthetic"}, "mode"), gaps,
                   "missing-mode", "mode", "Declare planning or synthetic mode.")
    if mode == "synthetic":
        _gap(gaps, "synthetic-evidence", "mode", "The entire forecast is synthetic and cannot pass financial handover.")
    _needed(_enum(model.get("forecast_kind"), {"estimate"}, "forecast_kind"), gaps, "missing-estimate-label",
            "forecast_kind", "All baseline forecasts remain estimates, never measured actuals.")
    sources = _validate_sources(_rows(model, "sources", "sources"), as_of, gaps)
    _lineage(material_payload(model), "", sources, gaps)
    profile = _mapping(model, "profile", "profile")
    agent_id, outcome_unit = _validate_profile(profile, sources, as_of, gaps, blueprint)
    baseline = _mapping(model, "baseline", "baseline")
    _sharing(baseline, "baseline", gaps)
    _needed(_text(baseline.get("id"), "baseline.id"), gaps, "missing-identity", "baseline.id", "Supply a stable baseline ID.")
    _needed(_integer(baseline.get("version"), "baseline.version", minimum=1), gaps,
            "missing-version", "baseline.version", "Supply the baseline version.")
    linked_agent = _needed(_text(baseline.get("agent_id"), "baseline.agent_id"), gaps,
                           "missing-agent", "baseline.agent_id", "Link the profile agent ID.")
    if agent_id and linked_agent and agent_id != linked_agent:
        _error("baseline.agent_id", "contradicts profile.agent_id")
    baseline_date = _date(baseline.get("as_of"), "baseline.as_of")
    _age(baseline_date, as_of, None, "baseline.as_of", gaps, "stale-source")
    month = _text(baseline.get("start_month"), "baseline.start_month")
    if month is not None:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", month):
            _error("baseline.start_month", "must be an ISO YYYY-MM month")
        _date(month + "-01", "baseline.start_month")
    _needed(month, gaps, "missing-period", "baseline.start_month", "Declare the first of twelve modelled months.", "calculation")
    currency = _needed(_enum(baseline.get("currency"), _CURRENCIES, "baseline.currency"), gaps,
                       "missing-currency", "baseline.currency", "Declare the reporting currency.", "calculation")
    annualisation = _mapping(baseline, "annualisation", "baseline.annualisation")
    annualisation_values = {}
    for key, allowed in (("method", {"sum-12-months"}), ("demand_profile", {"flat", "authored-monthly"})):
        annualisation_values[key] = _needed(
            _enum(annualisation.get(key), allowed, f"baseline.annualisation.{key}"), gaps,
            "missing-annualisation", f"baseline.annualisation.{key}", "Declare the twelve-month annualisation policy.")
    _evidence(annualisation, "baseline.annualisation", sources, gaps, claim="assumption", as_of=as_of)
    scope_rows = _rows(baseline, "scope", "baseline.scope")
    scope = _index(scope_rows, "baseline.scope", gaps, key="cost_driver_id")
    if not scope:
        _gap(gaps, "empty-scope", "baseline.scope", "Declare in-scope cost drivers; an empty scope is not complete.", "calculation")
    for i, row in enumerate(scope_rows):
        _sharing(row, f"baseline.scope[{i}]", gaps)
        _needed(_text(row.get("description"), f"baseline.scope[{i}].description"), gaps,
                "missing-scope", f"baseline.scope[{i}].description", "Describe the declared cost driver.")
    _validate_notes(baseline, sources, as_of, gaps)
    rates = _validate_rates(_rows(model, "rates", "rates"), sources, as_of, gaps)
    if model.get("fx") is None:
        _gap(gaps, "missing-fx", "fx", "Declare FX records explicitly; use an empty list when no conversion is needed.")
    fx_pairs = _validate_fx(_rows(model, "fx", "fx"), sources, as_of, gaps)
    scenarios = _rows(baseline, "scenarios", "baseline.scenarios")
    lines = _rows(baseline, "lines", "baseline.lines")
    line_driver_ids = {
        _text(_object(line, f"baseline.lines[{i}]").get("driver_id"), f"baseline.lines[{i}].driver_id")
        for i, line in enumerate(lines)
    } - {None}
    drivers, normalized_scenarios = _validate_scenarios(scenarios, sources, as_of, gaps,
                                                       outcome_unit=outcome_unit, line_driver_ids=line_driver_ids)
    _validate_lines(lines, scope, normalized_scenarios, drivers, rates, fx_pairs, currency, sources, as_of, gaps)
    if annualisation_values["demand_profile"] == "flat":
        for i, scenario in enumerate(scenarios):
            runs = scenario.get("monthly_runs")
            if runs is not None:
                known = [_decimal(v, f"baseline.scenarios[{i}].monthly_runs[{j}]") for j, v in enumerate(runs)]
                if None not in known and len(set(known)) > 1:
                    _error(f"baseline.scenarios[{i}].monthly_runs", "contradicts the flat annualisation profile")
    return gaps
