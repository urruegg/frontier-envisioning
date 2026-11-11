#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Describe Preview limitations and bind explicit caller acknowledgement to one action."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys

NOTICE = (
    "Frontier FinOps is Preview. Its grounding and cost model are not GA "
    "and need refinement. Results are provisional planning estimates, not "
    "validated pricing, budget approval or purchase/commitment advice. "
    "Verify rates and assumptions independently before decisions."
)
_UNRECORDED = object()


class FinOpsPreviewError(ValueError):
    pass


def require_preview_ack(acknowledged: bool) -> dict:
    if acknowledged is not True:
        raise FinOpsPreviewError(
            NOTICE + " Explicit --acknowledge-finops-preview is required."
        )
    return {
        "maturity": "preview",
        "grounding_status": "non-ga-refinement-required",
        "model_status": "non-ga-refinement-required",
        "notice": NOTICE,
        "acknowledgement": {
            "kind": "explicit-caller",
            "scope": "current-invocation",
        },
    }


def fingerprint(data, *, result_kind=None) -> str:
    """Canonical semantic data; omit receipts only at owned schema locations."""
    projected = data
    if isinstance(data, dict):
        projected = dict(data)
        schema = data.get("schema")
        if isinstance(schema, str) and schema.startswith(("frontier-finops/", "frontier-value/")):
            projected.pop("results", None)
            projected.pop("finops_preview", None)
            if schema.startswith("frontier-finops/"):
                projected.pop("rates_version", None)
        if result_kind in {"finops", "value"}:
            projected.pop("finops_preview", None)
            if result_kind == "value" and isinstance(data.get("use_cases"), list):
                projected["use_cases"] = [
                    {key: value for key, value in row.items() if key != "finops_preview"}
                    if isinstance(row, dict) else row for row in data["use_cases"]
                ]
    encoded = json.dumps(projected, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def preview_metadata(acknowledged: bool, *, operation: str, finops=None, value=None,
                     rates=None, blueprint=None, inherited=_UNRECORDED, scenario="base",
                     overrides=None, var_overrides=None, consume_finops_results=False,
                     consume_value_results=False) -> dict:
    """Record actual inputs; inherited provenance is lineage, never acknowledgement.

    Only source identities/dates/versions and hashes are projected here, not
    source text, private rate notes or internal discounts. Missing legacy rate
    provenance remains absent, rather than inventing a current rate version.
    """
    metadata = require_preview_ack(acknowledged)
    provenance = {}
    if inherited is not _UNRECORDED:
        if not isinstance(inherited, dict):
            raise FinOpsPreviewError("finops_preview must be an object; recalculate from the source model")
        if "acknowledgement" in inherited and not isinstance(inherited["acknowledgement"], dict):
            raise FinOpsPreviewError("finops_preview.acknowledgement must be an object, not consent")
        old = inherited.get("provenance", {})
        if not isinstance(old, dict):
            raise FinOpsPreviewError("finops_preview.provenance must be an object")
        provenance = {k: copy.deepcopy(old[k]) for k in ("inputs", "sources", "scenario") if k in old}
        if "calculations" in inherited:
            calculations = inherited["calculations"]
            if not isinstance(calculations, dict) or any(not isinstance(r, dict) for r in calculations.values()):
                raise FinOpsPreviewError("finops_preview.calculations must contain receipt objects")
            metadata["calculations"] = copy.deepcopy(calculations)
    inputs = provenance.setdefault("inputs", {})
    if not isinstance(inputs, dict):
        raise FinOpsPreviewError("finops_preview.provenance.inputs must be an object")
    for name, record in list(inputs.items()):
        if not isinstance(record, dict):
            raise FinOpsPreviewError(f"finops_preview.provenance.inputs.{name} must be an object")
        if name not in {"finops", "value", "rates", "blueprint", "finops_results", "value_results"}:
            inputs.pop(name)
        else:
            inputs[name] = {k: record[k] for k in ("schema", "version", "date", "fingerprint", "checked",
                                                 "internal", "visibility", "src", "content_src", "agents") if k in record}
    if "scenario" in provenance and not isinstance(provenance["scenario"], dict):
        raise FinOpsPreviewError("finops_preview.provenance.scenario must be an object")
    if "scenario" in provenance:
        provenance["scenario"] = {k: v for k, v in provenance["scenario"].items()
                                  if k in {"name", "agent_ids", "credit_scenarios_fingerprint",
                                           "overrides_fingerprint", "register_fingerprint", "internal", "visibility"}}
    for name, doc in (("finops", finops), ("value", value), ("rates", rates), ("blueprint", blueprint)):
        if doc is not None:
            if not isinstance(doc, dict):
                raise FinOpsPreviewError(f"{name} input must be an object")
            if name in {"finops", "value"} and doc.get("results") is not None and not isinstance(doc["results"], dict):
                raise FinOpsPreviewError(f"{name}.results must be an object; recalculate the source model")
            inputs[name] = {"schema": doc.get("schema"), "version": doc.get("version"),
                            "date": doc.get("date"), "fingerprint": fingerprint(doc),
                            **{k: doc[k] for k in ("internal", "visibility", "src", "content_src") if k in doc}}
            if name == "rates":
                inputs[name]["checked"] = doc.get("checked")
            if name == "finops":
                inputs[name]["agents"] = agent_ancestry(doc.get("agents", []), doc.get("date"))
    for name, doc, consumed in (("finops_results", finops, consume_finops_results),
                                ("value_results", value, consume_value_results)):
        if doc is not None and consumed and doc.get("results") is not None:
            inputs[name] = {"schema": doc.get("schema"), "version": doc.get("version"),
                            "fingerprint": fingerprint(doc["results"], result_kind="finops" if name == "finops_results" else "value")}
            if name == "finops_results":
                inputs[name]["agents"] = agent_ancestry(doc["results"].get("agents", []), doc.get("date"))
    if finops is not None and "rates" not in inputs:
        result = finops.get("results") or {}
        version = result.get("rates_version", finops.get("rates_version"))
        if version is not None:
            inputs["rates"] = {"schema": None, "version": version, "fingerprint": None}
    sources = provenance.get("sources", [])
    if not isinstance(sources, list) or any(not isinstance(s, dict) for s in sources):
        raise FinOpsPreviewError("finops_preview.provenance.sources must be a list of objects")
    if rates is not None:
        sources = []
        for source in rates.get("sources", []):
            if not isinstance(source, dict):
                raise FinOpsPreviewError("rates.sources must contain objects")
            sources.append({"id": source.get("id"), "version": source.get("version"),
                            "date": source.get("date"), "fingerprint": fingerprint(source),
                            **{k: source[k] for k in ("internal", "visibility") if k in source}})
    # Retain only the projection contract even when older metadata contains text.
    provenance["sources"] = [{k: s[k] for k in ("id", "version", "date", "fingerprint", "internal", "visibility") if k in s}
                             for s in sources]
    provenance["operation"] = operation
    if finops is not None and not (consume_finops_results and "scenario" in provenance):
        provenance["scenario"] = {
            "name": scenario,
            "agent_ids": [a.get("id") for a in finops.get("agents", [])],
            "credit_scenarios_fingerprint": fingerprint(finops.get("credit_scenarios", [])),
            "overrides_fingerprint": fingerprint({"assumptions": overrides, "variables": var_overrides}),
        }
        if any(is_private(a) for a in inputs["finops"].get("agents", [])):
            provenance["scenario"]["internal"] = True
    else:
        provenance.setdefault("scenario", {"name": scenario})
    provenance["missing_inputs"] = [name for name in ("finops", "rates")
                                    if not (inputs.get(name) or {}).get("fingerprint")]
    metadata["provenance"] = provenance
    return metadata


def privacy_flags(metadata: dict) -> dict:
    """Keep source restrictions independent of confidence and caller acknowledgement."""
    flags = {}
    for name in ("finops", "value", "rates"):
        source = metadata.get("provenance", {}).get("inputs", {}).get(name, {})
        if source.get("internal") is True:
            flags["internal"] = True
        if str(source.get("visibility", "")).lower() == "internal":
            flags["visibility"] = "internal"
        refs = source.get("content_src", source.get("src"))
        if refs:
            refs = refs.replace(",", " ").split() if isinstance(refs, str) else refs
            if not isinstance(refs, list) or any(not isinstance(r, str) for r in refs):
                raise FinOpsPreviewError("source privacy ancestry must use source IDs")
            flags.setdefault("content_src", []).extend(refs)
    if "content_src" in flags:
        flags["content_src"] = sorted(set(flags["content_src"]))
    return flags


def is_private(record) -> bool:
    return isinstance(record, dict) and (record.get("internal") is True or
                                        str(record.get("visibility", "")).lower() == "internal")


def inherit_restrictions(*records) -> dict:
    """Carry conservative item ancestry and the most specific supplied date."""
    attributes = {}
    refs = []
    for record in records:
        if not isinstance(record, dict):
            continue
        if record.get("internal") is True:
            attributes["internal"] = True
        if str(record.get("visibility", "")).lower() == "internal":
            attributes["visibility"] = "internal"
        if record.get("date") is not None:
            attributes.setdefault("date", record["date"])
        source = record.get("content_src", record.get("src"))
        if source:
            source = source.replace(",", " ").split() if isinstance(source, str) else source
            if not isinstance(source, list) or any(not isinstance(s, str) for s in source):
                raise FinOpsPreviewError("item ancestry must use source IDs")
            refs.extend(source)
    if refs:
        attributes["content_src"] = sorted(set(refs))
    return attributes


def agent_ancestry(agents, date=None):
    rows = []
    for agent in agents:
        row = {"id": agent.get("id"), "fingerprint": fingerprint(agent),
               **inherit_restrictions(agent, agent.get("people"), agent.get("people_source"),
                                      *(agent.get("azure") or []), *(agent.get("licences") or []), {"date": date})}
        if agent.get("outcome"):
            row["outcome_source"] = {"fingerprint": fingerprint(agent["outcome"]),
                                     **inherit_restrictions(agent["outcome"])}
        rows.append(row)
    return rows


def bind_calculation(result: dict, kind: str, model: dict, *, register=None, rates=None,
                     acknowledge_finops_preview: bool = False) -> None:
    """Bind generated figures to inputs; receipts are integrity data, not approval."""
    require_preview_ack(acknowledge_finops_preview)
    metadata = result["finops_preview"]
    receipt = {
        "kind": kind, "model_fingerprint": fingerprint(model), "results_fingerprint": fingerprint(result, result_kind=kind),
        "scenario_fingerprint": fingerprint(metadata["provenance"]["scenario"]),
        "inputs": copy.deepcopy(metadata["provenance"]["inputs"]),
        "sources": copy.deepcopy(metadata["provenance"]["sources"]),
    }
    if kind == "finops":
        receipt.update(register_fingerprint=fingerprint(register), rates_fingerprint=fingerprint(rates))
    else:
        receipt["finops_results_fingerprint"] = metadata["provenance"]["inputs"]["finops_results"]["fingerprint"]
    metadata.setdefault("calculations", {})[kind] = receipt


def _cache_error(kind: str, detail: str):
    raise FinOpsPreviewError(f"{kind}.results {detail}; recalculate with {kind}_calc.py and --acknowledge-finops-preview")


def _number(value, kind: str, field: str, *, positive=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
            or (value <= 0 if positive else value < 0)):
        _cache_error(kind, f"has invalid {field}")


def _receipt(result: dict, kind: str) -> tuple[dict, dict]:
    metadata = result.get("finops_preview")
    if not isinstance(metadata, dict):
        _cache_error(kind, "requires an object finops_preview and calculation lineage")
    provenance = metadata.get("provenance")
    if (not isinstance(provenance, dict) or not isinstance(provenance.get("inputs"), dict)
            or not isinstance(provenance.get("scenario"), dict) or not isinstance(provenance.get("sources"), list)):
        _cache_error(kind, "requires object provenance, inputs/scenario and source records")
    calculations = metadata.get("calculations")
    if not isinstance(calculations, dict):
        _cache_error(kind, "requires calculation lineage")
    receipt = calculations.get(kind)
    if not isinstance(receipt, dict) or receipt.get("kind") != kind:
        _cache_error(kind, "requires calculation lineage")
    if receipt.get("scenario_fingerprint") != fingerprint(metadata.get("provenance", {}).get("scenario")):
        _cache_error(kind, "has stale calculation scenario lineage")
    if receipt.get("results_fingerprint") != fingerprint(result, result_kind=kind):
        _cache_error(kind, "has stale or changed calculation figures")
    validate_snapshots(metadata, receipt, kind)
    return metadata, receipt


def validate_snapshots(metadata: dict, receipt: dict, kind: str, names=None):
    """Reject contradictory consumed facts; hashes/snapshots are not authentication."""
    provenance = metadata.get("provenance")
    snapshots = receipt.get("inputs")
    if not isinstance(provenance, dict) or not isinstance(provenance.get("inputs"), dict) or not isinstance(snapshots, dict):
        _cache_error(kind, "requires provenance input snapshots")
    fields = ("schema", "version", "date", "fingerprint", "checked", "internal", "visibility", "src", "content_src", "agents")
    def projection(record, keys):
        if not isinstance(record, dict):
            _cache_error(kind, "requires object provenance snapshots")
        return {key: record[key] for key in keys if record.get(key) is not None}
    for name in snapshots if names is None else names:
        if name not in snapshots or name not in provenance["inputs"]:
            _cache_error(kind, f"requires {name} provenance snapshots")
        if projection(snapshots[name], fields) != projection(provenance["inputs"][name], fields):
            _cache_error(kind, f"has contradictory {name} provenance snapshots")
    sources = provenance.get("sources")
    snapshot_sources = receipt.get("sources")
    if not isinstance(sources, list) or not isinstance(snapshot_sources, list):
        _cache_error(kind, "requires source provenance snapshots")
    source_fields = ("id", "version", "date", "fingerprint", "internal", "visibility")
    if [projection(s, source_fields) for s in sources] != [projection(s, source_fields) for s in snapshot_sources]:
        _cache_error(kind, "has contradictory source provenance snapshots")


def _input(metadata: dict, name: str, kind: str) -> dict:
    provenance = metadata.get("provenance")
    if not isinstance(provenance, dict) or not isinstance(provenance.get("inputs"), dict):
        _cache_error(kind, "requires input calculation lineage")
    record = provenance["inputs"].get(name)
    if not isinstance(record, dict) or not isinstance(record.get("fingerprint"), str) or len(record["fingerprint"]) != 64:
        _cache_error(kind, f"requires {name} calculation lineage")
    return record


def validate_finops_results(fin: dict, *, value=None, rates=None, register=None,
                            acknowledge_finops_preview: bool = False) -> dict:
    require_preview_ack(acknowledge_finops_preview)
    result = fin.get("results")
    if not isinstance(result, dict):
        _cache_error("finops", "is absent or not an object")
    if not isinstance(result.get("agents"), list) or not isinstance(result.get("missing"), list):
        _cache_error("finops", "requires agents and missing-input reports")
    totals = result.get("totals")
    if not isinstance(totals, dict) or not isinstance(totals.get("lines"), dict):
        _cache_error("finops", "requires calculated totals and cost lines")
    for key in ("credits_month", "total_month", "build", "sessions", "annual"):
        _number(totals.get(key), "finops", f"totals.{key}")
    for key in ("credits", "licences", "azure", "people"):
        _number(totals["lines"].get(key), "finops", f"totals.lines.{key}")
    _number(result.get("fx"), "finops", "fx", positive=True)
    known, reported = {a["id"] for a in fin.get("agents", [])}, set()
    for row in result["agents"]:
        if not isinstance(row, dict) or row.get("id") not in known or row["id"] in reported:
            _cache_error("finops", "has invalid or duplicate agent results")
        reported.add(row["id"])
        for key in ("fixed_month", "variable_month", "total_month", "build", "sessions", "credits_month"):
            _number(row.get(key), "finops", f"agent.{key}")
        if not isinstance(row.get("credits_by_event"), dict) or not isinstance(row.get("lines"), dict):
            _cache_error("finops", "requires agent credit events and cost lines")
    for gap in result["missing"]:
        if (not isinstance(gap, dict) or gap.get("agent") not in known or gap["agent"] in reported
                or not isinstance(gap.get("assumptions"), list) or not gap["assumptions"]):
            _cache_error("finops", "has invalid missing-input reports")
        reported.add(gap["agent"])
    if known != reported:
        _cache_error("finops", "omits agents without a missing-input report")
    metadata, receipt = _receipt(result, "finops")
    model_input, rate_input = _input(metadata, "finops", "finops"), _input(metadata, "rates", "finops")
    if receipt.get("model_fingerprint") != fingerprint(fin) or model_input["fingerprint"] != receipt["model_fingerprint"]:
        _cache_error("finops", "has a stale model calculation")
    if receipt.get("rates_fingerprint") != rate_input["fingerprint"]:
        _cache_error("finops", "has mismatched rates calculation lineage")
    if rates is not None and fingerprint(rates) != receipt["rates_fingerprint"]:
        _cache_error("finops", "was calculated with different rates")
    if result.get("rates_version", rate_input.get("version")) != rate_input.get("version"):
        _cache_error("finops", "has mismatched rates versions")
    if register is not None and fingerprint(register) != receipt.get("register_fingerprint"):
        _cache_error("finops", "has a stale assumption-register calculation")
    if value is not None:
        assumptions = [a for doc in (value, fin) for a in doc.get("assumptions", []) or []]
        reg = {a["id"]: a for a in assumptions}
        if len(reg) != len(assumptions) or fingerprint(reg) != receipt.get("register_fingerprint"):
            _cache_error("finops", "has a stale assumption-register calculation")
    return metadata


def validate_value_results(doc: dict, *, blueprint=None, acknowledge_finops_preview: bool = False) -> dict:
    require_preview_ack(acknowledge_finops_preview)
    result = doc.get("results")
    if (not isinstance(result, dict) or not isinstance(result.get("use_cases"), list)
            or not isinstance(result.get("totals"), dict) or not isinstance(result.get("inputs_needed"), list)):
        _cache_error("value", "requires calculated use cases, totals and missing-input reports")
    metadata, receipt = _receipt(result, "value")
    value_input = _input(metadata, "value", "value")
    if receipt.get("model_fingerprint") != fingerprint(doc) or value_input["fingerprint"] != receipt["model_fingerprint"]:
        _cache_error("value", "has a stale model calculation")
    fin_receipt = metadata.get("calculations", {}).get("finops")
    cost_input = _input(metadata, "finops_results", "value")
    if (not isinstance(fin_receipt, dict) or receipt.get("finops_results_fingerprint") != cost_input["fingerprint"]
            or fin_receipt.get("results_fingerprint") != cost_input["fingerprint"]):
        _cache_error("value", "has mismatched cost calculation lineage")
    if fin_receipt.get("model_fingerprint") != _input(metadata, "finops", "value")["fingerprint"]:
        _cache_error("value", "has mismatched cost model lineage")
    if fin_receipt.get("rates_fingerprint") != _input(metadata, "rates", "value")["fingerprint"]:
        _cache_error("value", "has mismatched cost rates lineage")
    # The value input is a new model at this boundary. Cost model/rates retain
    # the meanings they had in the consumed FinOps calculation.
    validate_snapshots(metadata, fin_receipt, "value", names=("finops", "rates"))
    applied = (blueprint or {}).get("finops") or {}
    applied_meta = applied.get("finops_preview") if isinstance(applied, dict) else None
    if isinstance(applied_meta, dict):
        applied_receipt = applied_meta.get("calculations", {}).get("finops")
        if isinstance(applied_receipt, dict):
            validate_snapshots(applied_meta, applied_receipt, "value", names=("finops", "rates"))
            if applied_receipt.get("results_fingerprint") != cost_input["fingerprint"]:
                _cache_error("value", "does not match the blueprint's applied cost calculation")
    return metadata


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--acknowledge-finops-preview", action="store_true")
    args = ap.parse_args(argv)
    info = (require_preview_ack(args.acknowledge_finops_preview) if args.acknowledge_finops_preview else {
        "maturity": "preview", "grounding_status": "non-ga-refinement-required",
        "model_status": "non-ga-refinement-required", "notice": NOTICE,
    })
    print(json.dumps(info, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
