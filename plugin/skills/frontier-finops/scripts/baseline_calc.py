# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Pure Decimal baseline calculations and recomputable technical receipts.

No CLI, files, clock, prices or consent are inferred here. Callers must supply
``as_of`` and actual True acknowledgement to BOTH public operations.

Task3 consumption contract:
* results.scenarios[id]: twelve months, annual_recurring, one_time, first_year,
  one_time_lines and unit_metrics[annual_recurring|first_year].
* months: period, recurring lines, total, verified_subtotal,
  provisional_subtotal, known_priced_subtotal, per_run/per_success/per_outcome.
* Annual money objects also contain the three named subtotals. Money/metrics
  have amount (decimal string or null), currency, status, reason, period, basis.
  Metrics add denominator (decimal string or null) and denominator_unit.
* Lines: line_id, quantity (decimal string or null), quantity_unit, cost,
  pricing_evidence {as_of, records, gaps}. Records contain only IDs/dates/status,
  never evidence text. Explicit FX identities are in cost.fx_refs.
* Derived records carry dependency_refs (RFC6901 input pointers), source_refs,
  all sharing_classes and combined sharingClassification, plus inherited
  internal/visibility/src/content_src/customer_scopes. Source ancestry closes
  transitively over BOTH legacy source-reference fields and source_id.
* Derived gaps (root and pricing_evidence) have canonical content ordering,
  independent of authored object-key order. Authored arrays are never sorted.
* Available means computable, NOT approved. Provisional means usable supplied
  pricing with incomplete evidence. No full total/unit cost uses a partial
  priced sum. Empty priced groups are unavailable/null, never fictional zero.
* finops_preview.calculations.baseline binds material inputs, explicit as_of,
  exact scenario coverage and results_fingerprint. It is outside hashed results
  and is internal technical data, NOT authentication, review or viewer consent.

Raw Decimal arithmetic uses an explicitly configured local 80-digit context
with bounded exponents. Every inexact intermediate operation is refused,
including products/sums of individually representable inputs and nonterminating
line-price division. This is an explicit unsupported-representation error,
never a rounded input or a silent zero. HALF_UP rounding is allowed only at
final period money (cents) or unit metrics (six places); the latter use exact
Decimal quotient/remainder rounding, not a rounded intermediate ratio.
Annual sums use unrounded monthly contributions. Caller flags/traps are neither
inherited nor modified. No numeric bound is inferred from the caller context.
"""
from __future__ import annotations

import calendar
import copy
from datetime import date
from decimal import (Context, Decimal, DecimalException, DivisionByZero, FloatOperation,
                     Inexact, InvalidOperation, Overflow, ROUND_HALF_UP, Underflow, localcontext)

from baseline_model import _date, _decimal, _gap, _text, material_payload, model_fingerprint, validate_model
from finops_preview import NOTICE, fingerprint, inherit_restrictions, is_private, require_preview_ack

_CENT = Decimal("0.01")
_UNIT = Decimal("0.000001")
_CLASSES = {"customer-shareable", "customer-specific", "internal-only", "validation-required"}
_REF_KEYS = ("src", "content_src")
_ARITHMETIC_CONTEXT = Context(
    prec=80, rounding=ROUND_HALF_UP, Emin=-999, Emax=999, capitals=1, clamp=0,
    flags=[], traps=[InvalidOperation, DivisionByZero, Overflow, Underflow, Inexact, FloatOperation],
)


def _pointer(parts):
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts) if parts else ""


def _field(parts):
    field = ""
    for part in parts:
        field += f"[{part}]" if isinstance(part, int) else ("." if field else "") + str(part)
    return field or "model"


def _legacy_refs(value):
    """Parse optional legacy ancestry without altering the authored payload."""
    if value is None:
        return []
    values = value.replace(",", " ").split() if isinstance(value, str) else value
    return [ref for ref in values if _text(ref, "lineage.reference") is not None]


def _parsed_restrictions(record):
    parsed = dict(record)
    for key in _REF_KEYS:
        refs = _legacy_refs(record.get(key))
        if refs:
            parsed[key] = refs
        else:
            parsed.pop(key, None)
    return parsed


def _refs(record):
    refs = []
    if isinstance(record, dict):
        if _text(record.get("source_id"), "lineage.source_id") is not None:
            refs.append(record["source_id"])
        for key in _REF_KEYS:
            refs.extend(_legacy_refs(record.get(key)))
    return refs


def _combine(*records):
    """Combine already classified lineage, never copy supplied private prose."""
    records = [_parsed_restrictions(record) for record in records]
    flags = inherit_restrictions(*records)
    classes, scopes = set(), set()
    dependencies, sources, fx_refs, src = set(), set(), set(), set()
    for record in records:
        classes.update(record.get("sharing_classes", []))
        scopes.update(record.get("customer_scopes", []))
        dependencies.update(record.get("dependency_refs", []))
        sources.update(record.get("source_refs", []))
        fx_refs.update(record.get("fx_refs", []))
        value = record.get("src", [])
        src.update(value.replace(",", " ").split() if isinstance(value, str) else value)
    classification = next((c for c in ("internal-only", "validation-required", "customer-specific")
                           if c in classes), "customer-shareable")
    if any(is_private(r) for r in records):
        classification = "internal-only"
        classes.add("internal-only")
    flags.update(sharingClassification=classification, sharing_classes=sorted(classes),
                 dependency_refs=sorted(dependencies), source_refs=sorted(sources), fx_refs=sorted(fx_refs))
    if scopes:
        flags["customer_scopes"] = sorted(scopes)
    if src:
        flags["src"] = sorted(src)
    if any(record.get("synthetic") is True for record in records):
        flags["synthetic"] = True
    return flags


def _count(number):
    if number is None:
        return None
    return format(number, "f")


def _canonical_gaps(gaps):
    """Order derived diagnostics only; preserve every record and its contents."""
    return sorted(gaps, key=lambda gap: (gap["field"], gap["code"], gap["message"], tuple(gap["blocks"])))


def _final_amount(value, places):
    """Only final display quantization may intentionally discard precision."""
    with localcontext(_ARITHMETIC_CONTEXT) as context:
        context.traps[Inexact] = False
        return format(value.quantize(places, rounding=ROUND_HALF_UP), "f")


def _unit_value(numerator, denominator):
    """Round a non-negative final ratio once, without an approximate division."""
    whole, remainder = divmod(numerator / _UNIT, denominator)
    if remainder * 2 >= denominator:
        whole += 1
    return whole * _UNIT


def _money(value, meta, currency, period, basis, *, provisional=False, reason=None, incomplete=False, places=_CENT):
    status = "incomplete" if incomplete else "unavailable"
    if value is not None:
        status = "provisional" if provisional else "available"
        reason = "pricing-evidence-incomplete" if provisional else None
    return {**meta, "amount": _final_amount(value, places) if value is not None else None,
            "currency": currency, "status": status, "reason": reason, "period": period, "basis": basis}


def _entry(value, meta, provisional=False):
    return {"value": value, "meta": meta, "provisional": provisional}


def _sum_entries(entries):
    return sum((e["value"] for e in entries), Decimal(0)) if entries else None


def _group(entries, currency, period, basis, *, blocked=False):
    meta = _combine(*(e["meta"] for e in entries))
    known = [e for e in entries if e["value"] is not None]
    verified = [e for e in known if not e["provisional"]]
    provisional = [e for e in known if e["provisional"]]
    value = _sum_entries(known) if known and len(known) == len(entries) and not blocked else None
    full = _money(value, meta, currency, period, basis, provisional=bool(provisional),
                  incomplete=value is None, reason="incomplete-cost")
    for key, selected in (("verified_subtotal", verified), ("provisional_subtotal", provisional),
                          ("known_priced_subtotal", known)):
        full[key] = _money(_sum_entries(selected), _combine(*(e["meta"] for e in selected)), currency, period, basis,
                           provisional=any(e["provisional"] for e in selected), reason="empty-priced-group")
    return full, _entry(value, meta, bool(provisional))


class _Calculation:
    def __init__(self, model, as_of):
        self.model = model
        self.as_of = as_of
        self.gaps = validate_model(model, as_of=as_of)
        self.unresolved_sharing = {g["field"] for g in self.gaps if g["code"] == "sharing-validation"}
        self.baseline = model.get("baseline") or {}
        self.profile = model.get("profile") or {}
        self.currency = self.text(self.baseline, "currency", "baseline")
        self.sources = {r["id"]: (i, r) for i, r in enumerate(model.get("sources") or []) if r.get("id")}
        self.rates = {r["id"]: (i, r) for i, r in enumerate(model.get("rates") or []) if r.get("id")}
        self.fx = {(r.get("from_currency"), r.get("to_currency")): (i, r)
                   for i, r in enumerate(model.get("fx") or []) if r.get("from_currency") and r.get("to_currency")}
        self.scope = {r["cost_driver_id"]: i for i, r in enumerate(self.baseline.get("scope") or [])
                      if r.get("cost_driver_id")}
        # A wholly unrepresented cost driver has unknown frequency; no complete
        # period total can be asserted. Category/profile gaps do not do this.
        self.scope_blocked = any(g["code"] in {"empty-scope", "uncovered-driver"} for g in self.gaps)
        self.common = _combine(
            self.envelope((), {"profile", "baseline", "rates", "fx", "sources"}),
            self.envelope(("profile",), {"outcome"}),
            self.envelope(("baseline",), {"scenarios", "lines", "scope"}))
        self.context = self.ancestry([("baseline", key) for key in
                                     ("annualisation", "assumptions", "exclusions", "risks", "confidence")], deep=True)

    @staticmethod
    def text(record, key, field):
        return _text(record.get(key), f"{field}.{key}")

    def ancestry(self, paths, *, deep=False):
        records, dependencies, sources, visited = [], set(), set(), set()

        def visit(value, parts, recursive):
            dependencies.add(_pointer(parts))
            if _field(parts) + ".sharingClassification" in self.unresolved_sharing:
                records.append({"sharing_classes": ["validation-required"]})
            if isinstance(value, dict):
                sharing = value.get("sharingClassification")
                record = {key: copy.deepcopy(value[key]) for key in ("internal", "visibility", "src", "content_src")
                          if key in value}
                if sharing is not None:
                    record["sharing_classes"] = [sharing if sharing in _CLASSES else "validation-required"]
                if value.get("customer_scope"):
                    record["customer_scopes"] = [value["customer_scope"]]
                if value.get("type") == "synthetic" or value.get("validationStatus") == "synthetic" or value.get("mode") == "synthetic":
                    record["synthetic"] = True
                records.append(record)
                for ref in _refs(value):
                    sources.add(ref)
                    if ref not in visited and ref in self.sources:
                        visited.add(ref)
                        i, source = self.sources[ref]
                        visit(source, ("sources", i), True)
                if recursive:
                    for key, child in value.items():
                        if isinstance(child, (dict, list)):
                            visit(child, (*parts, key), True)
            elif isinstance(value, list) and recursive:
                for i, child in enumerate(value):
                    visit(child, (*parts, i), True)

        for parts in paths:
            value = self.model
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                elif isinstance(value, list) and isinstance(part, int) and part < len(value):
                    value = value[part]
                else:
                    value = None
                    break
            visit(value, parts, deep)
        return _combine(*records, {"dependency_refs": sorted(dependencies), "source_refs": sorted(sources)})

    def envelope(self, parts, excluded):
        """Inherit nested context, but not independent economic child branches."""
        value = self.model
        for part in parts:
            value = value.get(part) if isinstance(value, dict) else value[part]
            if value is None:
                value = {}
        nested = [(*parts, key) for key, child in value.items()
                  if key not in excluded and isinstance(child, (dict, list))]
        return _combine(self.ancestry([parts]), self.ancestry(nested, deep=True))

    def issue(self, code, field, message):
        _gap(self.gaps, code, field, message, "calculation")

    def price_evidence(self, records):
        """Return provisional state separately from mathematical applicability."""
        gaps, projected = [], []
        applicable = True
        for field, row, kind in records:
            source_id = self.text(row, "source_id", field)
            source_pair = self.sources.get(source_id)
            source = source_pair[1] if source_pair else {}
            source_field = f"sources[{source_pair[0]}]" if source_pair else None
            own = [g for g in self.gaps if (g["field"] == field or g["field"].startswith(field + ".")
                                          or (source_field and (g["field"] == source_field or
                                                               g["field"].startswith(source_field + "."))))]
            for gap in own:
                if gap not in gaps:
                    gaps.append(gap)
            # Missing source metadata is incomplete evidence, not a lost price.
            # An explicitly contradictory source claim cannot price this line.
            claims = [claim for claim in source.get("applicability") or []
                      if _text(claim, field + ".source.applicability") is not None]
            if source.get("type") == "public-reference" or (claims and kind not in claims):
                applicable = False
            if any(g["code"] == "future-evidence" for g in own):
                applicable = False
            verification = row.get("verification") or {}
            projected.append({
                "kind": kind, "id": row.get("id"), "version": row.get("version"),
                "source_id": source_id, "date": row.get("date"),
                "effective_from": row.get("effective_from"), "effective_to": row.get("effective_to"),
                "verified_at": verification.get("verified_at"), "verification_status": verification.get("status"),
                "source_date": source.get("lastValidatedAt"), "source_status": source.get("validationStatus"),
            })
        provisional = self.model.get("mode") != "planning" or bool(gaps)
        return applicable, provisional, {"as_of": self.as_of.isoformat(), "records": projected,
                                        "gaps": copy.deepcopy(_canonical_gaps(gaps))}

    def line(self, scenario, si, line, li, mi, period, start, end):
        field, sp = f"baseline.lines[{li}]", f"baseline.scenarios[{si}]"
        driver = self.text(line, "driver_id", field)
        evidence = scenario.get("driver_evidence") or {}
        driver_evidence = evidence.get(driver) or {}
        per_run = line.get("quantity_mode") == "per-run"
        meta = _combine(self.common, self.context,
                        self.envelope(("baseline", "scenarios", si), {"drivers", "driver_evidence", "monthly_runs"}),
                        self.ancestry([("baseline", "lines", li)], deep=True),
                        self.ancestry([("baseline", "scenarios", si, "driver_evidence", driver),
                                       ("baseline", "lines", li, "allocation_policy")], deep=True))
        if line.get("cost_driver_id") in self.scope:
            meta = _combine(meta, self.ancestry([("baseline", "scope", self.scope[line["cost_driver_id"]])], deep=True))
        quantity = _decimal((scenario.get("drivers") or {}).get(driver), sp + ".drivers")
        meta = _combine(meta, self.ancestry([("baseline", "scenarios", si, "drivers", driver)]))
        if per_run:
            runs = _decimal((scenario.get("monthly_runs") or [None] * 12)[mi], sp + ".monthly_runs")
            run_unit = self.text(evidence.get("monthly_runs") or {}, "unit", sp + ".driver_evidence.monthly_runs")
            meta = _combine(meta, self.ancestry([("baseline", "scenarios", si, "monthly_runs", mi),
                                               ("baseline", "scenarios", si, "driver_evidence", "monthly_runs")], deep=True))
            quantity = quantity * runs if quantity is not None and runs is not None and run_unit == "run" else None
        policy = line.get("allocation_policy")
        allocation_ok = not line.get("shared") or policy is not None
        if policy is not None:
            share = _decimal(policy.get("share"), field + ".allocation_policy.share", share=True)
            allocation_ok = all(self.text(policy, k, field + ".allocation_policy") for k in ("id", "method"))
            quantity = quantity * share if quantity is not None and share is not None else None
        rate_id = self.text(line, "rate_id", field)
        pair = self.rates.get(rate_id)
        rate = pair[1] if pair else {}
        rate_field = f"rates[{pair[0]}]" if pair else "rates"
        price_records = [(rate_field, rate, "rate")] if pair else []
        if pair:
            meta = _combine(meta, self.ancestry([("rates", pair[0])], deep=True))
        price = _decimal(rate.get("amount"), rate_field + ".amount")
        block = _decimal(rate.get("pricing_block"), rate_field + ".pricing_block", positive=True)
        rate_currency = self.text(rate, "currency", rate_field)
        factor, fx_ok = Decimal(1), True
        if rate_currency and self.currency and rate_currency != self.currency:
            selected = self.fx.get((rate_currency, self.currency))
            fx_ok = selected is not None
            factor = None
            if selected:
                fi, fx = selected
                factor = _decimal(fx.get("rate"), f"fx[{fi}].rate", positive=True)
                price_records.append((f"fx[{fi}]", fx, "fx"))
                fx_id = self.text(fx, "id", f"fx[{fi}]")
                meta = _combine(meta, self.ancestry([("fx", fi)], deep=True),
                                {"fx_refs": [fx_id] if fx_id is not None else []})
        applicable, provisional, pricing_evidence = self.price_evidence(price_records)
        provisional = provisional or meta.get("synthetic") is True
        effective_from = _date(rate.get("effective_from"), rate_field + ".effective_from")
        effective_to = _date(rate.get("effective_to"), rate_field + ".effective_to")
        active = (effective_from is not None and effective_to is not None and start is not None
                  and effective_from <= self.as_of <= effective_to and effective_from <= start and end <= effective_to)
        if pair and not active:
            self.issue("rate-period-unavailable", f"{field}.{period or 'missing-period'}",
                       "Rate must cover the evaluation date and whole authored period; no proration is inferred.")
        if not applicable:
            self.issue("pricing-source-inapplicable", field, "A supplied source does not support this pricing claim.")
        typed = all((self.text(line, "quantity_unit", field), self.text(driver_evidence, "unit", sp + ".driver_evidence"),
                     self.text(rate, "unit", rate_field), rate_currency, self.currency,
                     self.text(line, "service", field), self.text(line, "meter", field),
                     self.text(rate, "service", rate_field), self.text(rate, "meter", rate_field),
                     self.text(line, "frequency", field), self.text(line, "quantity_mode", field)))
        # Known mismatches/ambiguity have already been refused by validate_model.
        usable = typed and active and applicable and allocation_ok and fx_ok
        value = (quantity * price / block * factor if usable and all(
            v is not None for v in (quantity, price, block, factor)) else None)
        basis = "recurring" if line.get("frequency") == "monthly" else "one-time"
        cost = _money(value, meta, self.currency, period, basis, provisional=provisional,
                      reason="missing-or-inapplicable-input")
        return _entry(value, meta, provisional), {
            **meta, "line_id": line.get("id"), "quantity": _count(quantity),
            "quantity_unit": self.text(line, "quantity_unit", field), "cost": cost,
            "pricing_evidence": pricing_evidence,
        }

    def metrics(self, cost, scenario, si, runs, period, basis):
        sp = f"baseline.scenarios[{si}]"
        evidence = scenario.get("driver_evidence") or {}
        success = _decimal(scenario.get("success_share"), sp + ".success_share", share=True)
        outcomes = _decimal(scenario.get("outcomes_per_success"), sp + ".outcomes_per_success")
        outcome = self.profile.get("outcome") or {}
        business_unit = self.text(outcome, "unit", "profile.outcome")
        paths = [("baseline", "scenarios", si, "monthly_runs"),
                 ("baseline", "scenarios", si, "driver_evidence", "monthly_runs")]
        # Period metrics use only the consumed month's demand, not private unused
        # denominators. Annual metrics consume the whole authored array.
        if period and len(period) == 7:
            start = self.text(self.baseline, "start_month", "baseline")
            if start:
                y, m = map(int, start.split("-"))
                py, pm = map(int, period.split("-"))
                paths[0] = (*paths[0], (py - y) * 12 + pm - m)
        meta = _combine(cost["meta"], self.ancestry(paths, deep=True))
        run_unit = self.text(evidence.get("monthly_runs") or {}, "unit", sp + ".driver_evidence.monthly_runs")
        if run_unit != "run":
            runs = None
        denominators = [("per_run", runs, "run", meta)]
        meta = _combine(meta, self.ancestry([("baseline", "scenarios", si, "success_share"),
                                           ("baseline", "scenarios", si, "driver_evidence", "success_share")], deep=True))
        success_unit = self.text(evidence.get("success_share") or {}, "unit", sp + ".driver_evidence.success_share")
        successful = runs * success if runs is not None and success is not None and success_unit == "share" else None
        denominators.append(("per_success", successful, "successful-run", meta))
        meta = _combine(meta, self.ancestry([("profile", "outcome"),
                                           ("baseline", "scenarios", si, "outcomes_per_success"),
                                           ("baseline", "scenarios", si, "driver_evidence", "outcomes_per_success")], deep=True))
        outcome_unit = self.text(evidence.get("outcomes_per_success") or {}, "unit",
                                 sp + ".driver_evidence.outcomes_per_success")
        business = (successful * outcomes if successful is not None and outcomes is not None and
                    business_unit and outcome_unit == business_unit and self.text(outcome, "definition", "profile.outcome")
                    else None)
        denominators.append(("per_outcome", business, business_unit, meta))
        metrics = {}
        for name, denominator, unit, meta in denominators:
            reason = None
            if cost["value"] is None:
                reason = "incomplete-cost"
            elif denominator is None or denominator == 0:
                reason = "no-denominator"
            value = _unit_value(cost["value"], denominator) if reason is None else None
            metrics[name] = {**_money(value, meta, self.currency, period, basis,
                                     provisional=cost["provisional"], reason=reason, places=_UNIT),
                             "denominator": _count(denominator), "denominator_unit": unit}
        return metrics

    def results(self):
        start = self.text(self.baseline, "start_month", "baseline")
        periods = []
        for i in range(12):
            if start:
                year, month = map(int, start.split("-"))
                year, month = year + (month - 1 + i) // 12, (month - 1 + i) % 12 + 1
                try:
                    first, last = date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
                except ValueError:
                    raise ValueError("baseline.start_month: twelve-month period representation unavailable") from None
                periods.append((f"{year:04d}-{month:02d}", first, last))
            else:
                periods.append((None, None, None))
        scenarios = {}
        for si, scenario in enumerate(self.baseline.get("scenarios") or []):
            if not scenario.get("id"):
                continue
            months, recurring, once, once_lines = [], [], [], []
            lines = self.baseline.get("lines") or []
            unknown_frequency = any(not self.text(line, "frequency", f"baseline.lines[{li}]")
                                    for li, line in enumerate(lines))
            blocked = self.scope_blocked or unknown_frequency
            for mi, (period, first, last) in enumerate(periods):
                entries, line_records = [], []
                for li, line in enumerate(lines):
                    frequency = line.get("frequency")
                    if frequency == "monthly" or (frequency == "one-time" and mi == 0):
                        entry, record = self.line(scenario, si, line, li, mi, period, first, last)
                        if frequency == "monthly":
                            entries.append(entry)
                            recurring.append(entry)
                            line_records.append(record)
                        else:
                            once.append(entry)
                            once_lines.append(record)
                total, cost = _group(entries, self.currency, period, "recurring", blocked=blocked)
                runs = _decimal((scenario.get("monthly_runs") or [None] * 12)[mi], "baseline.scenarios.monthly_runs")
                months.append({"period": period, "lines": line_records, "total": total,
                               **{k: total[k] for k in ("verified_subtotal", "provisional_subtotal", "known_priced_subtotal")},
                               **self.metrics(cost, scenario, si, runs, period, "recurring")})
            annual, annual_cost = _group(recurring, self.currency, "12-months", "recurring", blocked=blocked)
            one_time, _ = _group(once, self.currency, "12-months", "one-time", blocked=blocked)
            first_year, year_cost = _group(recurring + once, self.currency, "12-months", "first-year", blocked=blocked)
            runs = [_decimal(v, "baseline.scenarios.monthly_runs") for v in scenario.get("monthly_runs") or [None] * 12]
            annual_runs = sum(runs, Decimal(0)) if all(v is not None for v in runs) else None
            scenarios[scenario["id"]] = {
                "months": months, "annual_recurring": annual, "one_time": one_time, "first_year": first_year,
                "one_time_lines": once_lines, "unit_metrics": {
                    "annual_recurring": self.metrics(annual_cost, scenario, si, annual_runs, "12-months", "recurring"),
                    "first_year": self.metrics(year_cost, scenario, si, annual_runs, "12-months", "first-year"),
                }}
        return {"schema": "frontier-finops-baseline-results/1.0", "as_of": self.as_of.isoformat(),
                "internal": True, "sharingClassification": "internal-only", "forecast_kind": "estimate",
                "synthetic": self.model.get("mode") == "synthetic", "notice": NOTICE,
                "handover_blocked": True, "financial_approval": False,
                "scenarios": scenarios, "gaps": _canonical_gaps(self.gaps)}


def calculate(model, *, as_of, acknowledge_finops_preview=False):
    """Return fresh authored data plus results/receipt; discard stale owned outputs."""
    metadata = require_preview_ack(acknowledge_finops_preview)
    try:
        with localcontext(_ARITHMETIC_CONTEXT):
            authored = material_payload(model)
            results = _Calculation(authored, as_of).results()
            receipt = {"kind": "baseline", "as_of": as_of.isoformat(),
                       "model_fingerprint": model_fingerprint(authored),
                       "scenario_ids": sorted(results["scenarios"]),
                       "results_fingerprint": fingerprint(results),
                       "internal": True, "sharingClassification": "internal-only"}
    except DecimalException:
        raise ValueError("baseline.results: arithmetic representation unavailable; revise the numeric inputs") from None
    metadata.update(internal=True, sharingClassification="internal-only", calculations={"baseline": receipt})
    return {**authored, "results": results, "finops_preview": metadata}


def _refuse():
    raise ValueError("baseline.results: missing, stale or malformed calculation lineage; recalculate with current Preview acknowledgement")


def validate_receipt(model, *, as_of, acknowledge_finops_preview=False):
    """Recompute and return detached technical lineage, never financial approval.

    Exact canonical comparison against freshly generated results validates every
    shape/type/finite amount and defeats rehashed fabricated results. A hash is
    only an integrity convenience, not authenticity or protection from authors.
    """
    require_preview_ack(acknowledge_finops_preview)
    if not isinstance(model, dict) or not isinstance(model.get("results"), dict):
        _refuse()
    metadata = model.get("finops_preview")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("calculations"), dict):
        _refuse()
    receipt = metadata["calculations"].get("baseline")
    if not isinstance(receipt, dict) or receipt.get("kind") != "baseline":
        _refuse()
    try:
        expected = calculate(model, as_of=as_of, acknowledge_finops_preview=True)
        if (fingerprint(model["results"]) != fingerprint(expected["results"]) or
                fingerprint(metadata) != fingerprint(expected["finops_preview"])):
            _refuse()
    except (ValueError, TypeError, OverflowError, RecursionError):
        _refuse()
    return copy.deepcopy(receipt)
