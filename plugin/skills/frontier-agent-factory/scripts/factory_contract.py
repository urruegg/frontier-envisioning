# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Strict, passive source and intake contracts for the offline producer."""
from __future__ import annotations

import copy
from pathlib import Path
import re

from factory_common import (
    FactoryError, MIB, ROLES, EXTENSIONS, need, digest, encoded, decode,
    text, identity, timestamp, approval, parts, portable, claim_path, read, conforms,
)

_SCHEMA_SHA = "04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f"


def _installed_schema():
    raw = read(Path(__file__).absolute().parent.parent, "references/intake.schema.json", MIB)
    need(digest(raw) == _SCHEMA_SHA, "FACTORY_SCHEMA_PROFILE")
    return decode(raw)


def _fixed_schema(upstream):
    schema = _installed_schema()
    need(encoded(upstream) == encoded(schema), "FACTORY_SCHEMA_PROFILE")
    return schema


def _object(properties):
    return {"type": "object", "additionalProperties": False,
            "required": list(properties), "properties": properties}


def _array(items, maximum, minimum=0, unique=False):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum,
            "uniqueItems": unique}


def _ref(name):
    return {"$ref": "#/$defs/" + name}


def _input_intake(upstream):
    schema = copy.deepcopy(upstream)
    for name in ("sourceFile", "baselineFile"):
        schema["$defs"][name]["required"].remove("sha256")
        del schema["$defs"][name]["properties"]["sha256"]
    return schema


def _template_shape():
    nullable_text = {"oneOf": [_ref("text"), {"type": "null"}]}
    date_time = {"type": "string", "format": "date-time"}
    commit = {"type": "string", "pattern": "^[0-9a-f]{40}$"}
    release = _object({"id": {"type": "integer"}, "tag": _ref("text"),
                       "commit": commit, "published_at": date_time})
    row = _object({"id": {"type": "integer"}, "tag_name": nullable_text,
                   "published_at": nullable_text, "draft": {"type": "boolean"},
                   "prerelease": {"type": "boolean"}})
    return _object({
        "repository": {"const": "urruegg/frontier-agent-factory"},
        "selection": {"enum": ["stable-release", "unreleased-bootstrap"]}, "commit": commit,
        "release": {"oneOf": [release, {"type": "null"}]},
        "discovery": _object({"status": {"const": "succeeded"}, "complete": {"const": True},
                              "export_id": _ref("id"), "observed_at": date_time,
                              "evidence": _ref("text"), "releases": _array(row, 10000)}),
        "bootstrap_approval": _ref("optionalApproval"),
        "acquisition": _object({
            "status": {"const": "succeeded"},
            "method": {"enum": ["authorised-host", "explicit-local-source"]},
            "by": _ref("text"), "at": date_time, "evidence": _ref("text"),
            "archive_sha256": _ref("sha256"),
        }),
        "root_prefix": {"type": "string", "maxLength": 260},
    })


def request_shape(upstream):
    """Return a detached producer schema; the installed receiver remains unchanged."""
    schema = _input_intake(_fixed_schema(upstream))
    intake = {key: value for key, value in schema.items()
              if key not in ("$defs", "$schema", "$id", "title", "description")}
    selection = _object({"solution_id": _ref("id"), "original_solution_id": _ref("text"),
                         "original_agent_ids": _array(_ref("text"), 64, 1, True),
                         "rationale": _ref("text"), "dependency_gaps": _array(_ref("id"), 256, unique=True)})
    packet = _object({
        "artifact_ids": _array(_ref("text"), 256, 1, True),
        "kind": {"enum": ["baseline", "reviewed-document"]},
        "model_path": {"oneOf": [_ref("path"), {"type": "null"}]},
        "review_paths": _array(_ref("path"), 256, unique=True), "owner_review": _ref("approval"),
    })
    result = _object({
        "schema": {"const": "frontier-agent-factory-request/1.0"},
        "export_id": _ref("id"), "created_at": {"type": "string", "format": "date-time"},
        "customer_scope": _ref("text"),
        "evidence_kind": {"enum": ["externally-recorded", "synthetic-compatibility"]},
        "template": _template_shape(), "intake": intake,
        "blueprint": _object({"source_path": _ref("path"), "baseline_path": _ref("path")}),
        "id_map": _object({name: {"type": "object"} for name in ("solutions", "agents", "requirements")}),
        "selection_evidence": _array(selection, 32, 1),
        "sharing_review": _object({"customer_scope": _ref("text"), "metadata": _ref("approval"),
                                   "artifacts": {"type": "object"}}),
        "history": _array(_ref("id"), 127, unique=True),
        "financial": _object({"requested": {"type": "boolean"},
                               "as_of": {"oneOf": [{"type": "string", "format": "date"}, {"type": "null"}]},
                               "claim": {"enum": ["review", "build-handover"]},
                               "packets": _array(packet, 256)}),
    })
    result["$defs"] = schema["$defs"]
    return result


def _intake_input(data, schema):
    need(len(encoded(data)) <= MIB, "FACTORY_LIMIT")
    need(conforms(_input_intake(schema), data), "FACTORY_REQUEST_SHAPE")
    _record_ids(data)
    for row in data["artifacts"]:
        if row["status"] == "provided":
            parts(row["source"]["path"])
            parts(row["baseline"]["path"])


def prevalidate_request(request, upstream):
    """Validate every nested producer field before any caller indexes or reads sources."""
    need(len(encoded(request)) <= MIB, "FACTORY_LIMIT")
    need(conforms(request_shape(upstream), request), "FACTORY_REQUEST_SHAPE")
    identity(request["export_id"])
    _intake_input(request["intake"], upstream)
    template = request["template"]
    if template["root_prefix"]:
        parts(template["root_prefix"])
    for value in request["blueprint"].values():
        parts(value)
    for mapping in request["id_map"].values():
        need(len(mapping) <= 512 and len(set(encoded(value) for value in mapping.values())) == len(mapping))
        for original, factory_id in mapping.items():
            text(original)
            identity(factory_id)
    selected = {row["solution_id"] for row in request["intake"]["selected_solutions"]}
    selections = request["selection_evidence"]
    need({row["solution_id"] for row in selections} == selected and len(selections) == len(selected))
    for selection in selections:
        for gap_id in selection["dependency_gaps"]:
            identity(gap_id)
    need(set(request["id_map"]["solutions"].values()) == selected)
    need(request["sharing_review"]["customer_scope"] == request["customer_scope"], "FACTORY_SHARING")
    history = request["history"]
    need(request["intake"]["intake_id"] not in history, "FACTORY_HISTORY")
    allowed_records = {request["intake"]["intake_id"], *history}
    current_files = {row["id"] for row in request["intake"]["artifacts"] if row["status"] == "provided"}
    for qualified, evidence in request["sharing_review"]["artifacts"].items():
        need(qualified.count(":") == 1, "FACTORY_SHARING")
        record_id, artifact_id = qualified.split(":")
        identity(record_id)
        identity(artifact_id)
        need(record_id in allowed_records, "FACTORY_SHARING")
        if record_id == request["intake"]["intake_id"]:
            need(artifact_id in current_files, "FACTORY_SHARING")
        approval(evidence)
    for row in request["intake"]["artifacts"]:
        if row["status"] == "provided":
            need(request["intake"]["intake_id"] + ":" + row["id"] in request["sharing_review"]["artifacts"],
                 "FACTORY_SHARING")
    for packet in request["financial"]["packets"]:
        need((packet["kind"] == "baseline" and packet["model_path"] is not None)
             or (packet["kind"] == "reviewed-document" and packet["model_path"] is None
                 and packet["review_paths"] == []), "FACTORY_FINANCIAL_SHAPE")
        if packet["model_path"] is not None:
            parts(packet["model_path"])
        for path in packet["review_paths"]:
            parts(path)
        for qualified in packet["artifact_ids"]:
            need(qualified.count(":") == 1)
            record_id, artifact_id = qualified.split(":")
            identity(record_id)
            identity(artifact_id)
            need(record_id in allowed_records)


def source_receipt(receipt, export_id, created_at, archive_bytes):
    """Check frozen evidence consistency, not identity, permission or live freshness."""
    need(len(encoded(receipt)) <= MIB, "FACTORY_LIMIT")
    shape = _template_shape()
    shape["$defs"] = _installed_schema()["$defs"]
    need(conforms(shape, receipt), "FACTORY_DISCOVERY")
    need(re.fullmatch(r"[0-9a-f]{40}", receipt["commit"]) is not None, "FACTORY_DISCOVERY")
    identity(export_id)
    created = timestamp(created_at)
    discovery, acquisition = receipt["discovery"], receipt["acquisition"]
    need(discovery["export_id"] == export_id, "FACTORY_DISCOVERY")
    need(timestamp(discovery["observed_at"]) <= timestamp(acquisition["at"]) <= created,
         "FACTORY_DISCOVERY")
    need(isinstance(archive_bytes, bytes)
         and digest(archive_bytes) == acquisition["archive_sha256"], "FACTORY_SOURCE_HASH")
    if receipt["root_prefix"]:
        need(len(parts(receipt["root_prefix"])) == 1, "FACTORY_PATH")
    stable = []
    seen = set()
    for row in discovery["releases"]:
        need(row["id"] > 0 and row["id"] not in seen, "FACTORY_DISCOVERY")
        seen.add(row["id"])
        if row["draft"] or row["prerelease"]:
            continue
        need(row["tag_name"] is not None and row["published_at"] is not None, "FACTORY_DISCOVERY")
        tag = row["tag_name"]
        # Check the qualified refs/tags/<tag> syntax, not a release naming policy.
        need(re.search(r"[\x00-\x20\x7f~^:?*\[\\]", tag) is None
             and ".." not in tag and "@{" not in tag and not tag.endswith(".")
             and all(part and not part.startswith(".") and not part.endswith(".lock")
                     for part in tag.split("/")), "FACTORY_DISCOVERY")
        try:
            published = timestamp(row["published_at"])
        except FactoryError:
            raise FactoryError("FACTORY_DISCOVERY") from None
        need(published <= timestamp(discovery["observed_at"]), "FACTORY_DISCOVERY")
        stable.append((published, row))
    if stable:
        need(receipt["selection"] == "stable-release" and receipt["bootstrap_approval"] is None
             and receipt["release"] is not None, "FACTORY_DISCOVERY")
        latest = max(published for published, _row in stable)
        candidates = [row for published, row in stable if published == latest]
        need(len(candidates) == 1, "FACTORY_DISCOVERY")
        chosen = candidates[0]
        release = receipt["release"]
        need(release["id"] == chosen["id"] and release["tag"] == chosen["tag_name"]
             and release["published_at"] == chosen["published_at"]
             and release["commit"] == receipt["commit"], "FACTORY_DISCOVERY")
    else:
        need(receipt["selection"] == "unreleased-bootstrap" and receipt["release"] is None
             and receipt["bootstrap_approval"] is not None, "FACTORY_DISCOVERY")
        approval(receipt["bootstrap_approval"])
        need(re.search(r"(?<![0-9a-f])" + receipt["commit"] + r"(?![0-9a-f])",
                       receipt["bootstrap_approval"]["reference"]) is not None, "FACTORY_DISCOVERY")


def validate_intake(data, schema, baseline, originals=None, history=None):
    """Validate receiver records and actual bytes; no acceptance downgrade or authentication."""
    schema = _fixed_schema(schema)
    need(len(encoded(data)) <= MIB, "FACTORY_LIMIT")
    need(conforms(schema, data), "FACTORY_INTAKE_SCHEMA")
    _record_ids(data)
    baselines = _byte_map(baseline)
    sources = None if originals is None else _byte_map(originals)
    history = {} if history is None else history
    need(isinstance(history, dict) and len(history) <= 127, "FACTORY_HISTORY")
    need(data["intake_id"] not in history, "FACTORY_HISTORY")
    for record_id in history:
        identity(record_id)

    selected = [row["solution_id"] for row in data["selected_solutions"]]
    all_ids = list(selected)
    for field in ("artifacts", "requirements", "gaps", "decisions"):
        all_ids.extend(row["id"] for row in data[field])
    need(len(all_ids) == len(set(all_ids)), "FACTORY_DUPLICATE_ID")
    accepted = data["review"]["status"] == "accepted"
    if accepted:
        need(data["review"]["approval"] is not None, "FACTORY_ACCEPTANCE")
        for solution in selected:
            need(any(row["solution_id"] == solution for row in data["requirements"]), "FACTORY_ACCEPTANCE")
    for field in ("requirements", "gaps", "decisions"):
        for row in data[field]:
            need(row["solution_id"] in selected, "FACTORY_SELECTION")
            if field != "requirements" and accepted:
                need(not row["blocking"] or row["status"] == "resolved", "FACTORY_ACCEPTANCE")
    expected_method = ("exported-files" if data["source"]["kind"] == "exported-package"
                       else "exact-file-download")
    need(data["acquisition"]["method"] == expected_method, "FACTORY_ACQUISITION")
    transfer = data["transfer"]
    if transfer["permission"] == "approved":
        need(transfer["approval"] is not None, "FACTORY_TRANSFER")
    if accepted:
        need(transfer["permission"] == "approved", "FACTORY_ACCEPTANCE")
    declared = {(solution, role): [] for solution in selected for role in ROLES}
    for row in data["artifacts"]:
        for solution in row["solution_ids"]:
            need(solution in selected, "FACTORY_SELECTION")
            declared[(solution, row["role"])].append(row["status"])
        if row["status"] == "not-applicable":
            need(row["role"] not in ("prd", "solution-design"), "FACTORY_APPLICABILITY")
            need(row["rationale"].strip().lower().rstrip(".") not in
                 ("n/a", "na", "none", "unknown", "not applicable", "not-applicable", "tbd", "todo"),
                 "FACTORY_APPLICABILITY")
        if accepted:
            need(row["status"] != "missing", "FACTORY_ACCEPTANCE")
        if row["status"] == "provided":
            need(transfer["classification"] != "restricted" and transfer["permission"] == "approved"
                 and transfer["approval"] is not None, "FACTORY_TRANSFER")
    for statuses in declared.values():
        need(bool(statuses) and (len(statuses) == 1 or set(statuses) == {"provided"}), "FACTORY_APPLICABILITY")

    remaining = 64 * MIB
    for row, source_name, target_name in _artifact_paths(data):
        source, target, transform = row["source"], row["baseline"], row["transformation"]
        need(all(re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) is not None for record in (source, target)),
             "FACTORY_DIGEST")
        for record, name, files in ((target, target_name, baselines), (source, source_name, sources)):
            if files is None:
                continue
            need(name in files, "FACTORY_FILE")
            raw = files[name]
            need(0 < len(raw) <= min(16 * MIB, remaining), "FACTORY_LIMIT")
            remaining -= len(raw)
            need(digest(raw) == record["sha256"], "FACTORY_DIGEST")
        same = source["sha256"] == target["sha256"]
        if transform["kind"] == "none":
            need(same and transform["approval"] is None, "FACTORY_TRANSFORMATION")
        else:
            need(not same and transform["approval"] is not None, "FACTORY_TRANSFORMATION")

    prior, seen = data["supersedes"], {data["intake_id"]}
    while prior is not None:
        need(prior not in seen and len(seen) < 128 and prior in history, "FACTORY_HISTORY")
        seen.add(prior)
        previous = history[prior]
        need(len(encoded(previous)) <= MIB and conforms(schema, previous), "FACTORY_HISTORY")
        need(previous["intake_id"] == prior and previous["review"]["status"] == "accepted", "FACTORY_HISTORY")
        prior = previous["supersedes"]


def _record_ids(data):
    identity(data["intake_id"])
    if data["supersedes"] is not None:
        identity(data["supersedes"])
    for selected in data["selected_solutions"]:
        identity(selected["solution_id"])
        for agent_id in selected["agent_ids"]:
            identity(agent_id)
    for field in ("artifacts", "requirements", "gaps", "decisions"):
        for row in data[field]:
            identity(row["id"])
            for solution in row["solution_ids"] if field == "artifacts" else [row["solution_id"]]:
                identity(solution)


def _byte_map(value):
    need(isinstance(value, dict), "FACTORY_FILE_MAP")
    result, spellings = {}, {}
    for path, raw in value.items():
        name = claim_path(spellings, path)
        need(isinstance(raw, bytes), "FACTORY_FILE_MAP")
        result[name] = raw
    return result


def _artifact_paths(data):
    """Plan all names before reading content; never overwrite a canonical destination."""
    sources, destinations = {}, {}
    planned = []
    prefix = ("docs", "intake", "records", data["intake_id"], "artifacts")
    for row in data["artifacts"]:
        if row["status"] != "provided":
            continue
        source, target = row["source"]["path"], row["baseline"]["path"]
        target_parts = parts(target)
        need(target_parts[:5] == prefix and len(target_parts) >= 6, "FACTORY_BASELINE_PATH")
        for path in (source, target):
            need(Path(portable(path)).suffix.lower() in EXTENSIONS, "FACTORY_FORMAT")
        source_name = claim_path(sources, source, repeat=True)
        target_name = claim_path(destinations, target)
        planned.append((row, source_name, target_name))
    return planned


def materialize(data, baseline_root, source_root, read_file):
    """Compute hashes from ordinary bytes, never mutate supplied records or files."""
    _intake_input(data, _installed_schema())
    result, baseline, originals = copy.deepcopy(data), {}, {}
    planned = _artifact_paths(result)
    remaining = 64 * MIB
    for row, source_name, target_name in planned:
        for field, root, files, name in (
            ("source", source_root, originals, source_name),
            ("baseline", baseline_root, baseline, target_name),
        ):
            record = row[field]
            need(remaining > 0, "FACTORY_LIMIT")
            limit = min(16 * MIB, remaining)
            raw = read_file(root, record["path"], limit)
            need(isinstance(raw, bytes), "FACTORY_FILE")
            need(0 < len(raw) <= limit, "FACTORY_LIMIT")
            remaining -= len(raw)
            if name in files:
                need(files[name] == raw, "FACTORY_SOURCE_CHANGED")
            else:
                files[name] = raw
            record["sha256"] = digest(raw)
    need(len(encoded(result)) <= MIB, "FACTORY_LIMIT")
    return result, baseline, originals
