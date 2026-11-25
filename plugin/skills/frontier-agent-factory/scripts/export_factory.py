#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Validate local reviewed inputs and atomically export a passive factory source ZIP.

No acquisition, template execution, application generation or deployment is performed.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import sys

import factory_archive as archive
import factory_common as common
import factory_contract as contract
import factory_projection as projection
from factory_common import (
    FactoryError, MIB, claim_path, conforms, decode, digest, encoded, identity,
    need, parts, plain_path, portable, read,
)

HERE = Path(__file__).resolve().parent.parent


def load_history(ids, baseline_root, schema, validate):
    """Load only declared accepted history; preserve raw records and author bytes."""
    need(isinstance(ids, list) and len(ids) <= 127, "FACTORY_HISTORY")
    for record_id in ids:
        identity(record_id)
    need(len(ids) == len(set(ids)), "FACTORY_HISTORY")
    records, files, raw_records, claims = {}, {}, {}, {}
    remaining = 128 * MIB
    for record_id in ids:
        path = f"docs/intake/records/{record_id}/intake.json"
        claim_path(claims, path)
        raw = read(baseline_root, path, min(MIB, remaining))
        remaining -= len(raw)
        record = decode(raw)
        need(conforms(schema, record), "FACTORY_HISTORY")
        need(record["intake_id"] == record_id and record["review"]["status"] == "accepted",
             "FACTORY_HISTORY")
        records[record_id], raw_records[path] = record, raw
    # Reserve the complete set of names before reading any artifact.
    planned = []
    for record in records.values():
        for row in record["artifacts"]:
            if row["status"] == "provided":
                name = claim_path(claims, row["baseline"]["path"])
                planned.append((row["baseline"]["path"], name))
    for spelling, name in planned:
        need(remaining > 0, "FACTORY_LIMIT")
        raw = read(baseline_root, spelling, min(16 * MIB, remaining))
        remaining -= len(raw)
        files[name] = raw
    for record_id, record in records.items():
        validate(record, schema, files, originals=None,
                 history={key: row for key, row in records.items() if key != record_id})
    return records, files, raw_records


def _disjoint(*groups):
    claims = {}
    for group in groups:
        for path in group:
            claim_path(claims, path)


def _generated_docs(request, intake, financial_status):
    label = request["evidence_kind"]
    prefix = f"docs/intake/records/{intake['intake_id']}"
    start = f"""# Start here

This ZIP contains source and reviewed intake documents, not a working application.
Evidence label: {label}. Synthetic compatibility evidence is not real approval.

## What to do next

1. Review the receiving foundation's AGENTS.md and policies. Inspect the intake
   and its provided files. A recorded acceptance is not authentication or permission.
2. Use Python 3.12 or later and Node 24 LTS, plus the tools required by the
   foundation. Those are receiver prerequisites, not certified on this producer.
3. From the extracted repository, check the frozen baseline:

   `python tools/intake.py validate {prefix}/intake.json`

   On Windows use:

   `python tools\\intake.py validate {prefix.replace('/', chr(92))}\\intake.json`

   To ALSO compare original source hashes, add `--source-root` with the local
   originals directory, for example `--source-root C:\\reviewed\\originals` on
   Windows. Originals are not in this ZIP. Baseline-only validation does not
   verify unavailable originals. Check the tool's help for local prerequisites.
4. Run the foundation's documented tool checks and obtain the accountable
   owners' review of gaps, decisions, scope, transfer and next governed tasks.
   Do not generate solution units or start implementation from this ZIP alone.
5. Before any tenant work, check access, identities, licences, connectors, DLP,
   security, capacity and applicable approvals with their human owners.

Export validation is distinct from receiver validation (not performed),
Cowork validation (not performed), and tenant readiness (not assessed).
Cowork discovery, install, acquisition and export were NOT PERFORMED.
Native Azure DevOps and GitHub Enterprise Server support is not certified.
An unavailable host capability must be reported by the host; there is no
network-enabled Python fallback.

Financial status: {financial_status}. Preview acknowledgement is awareness,
not budget, purchase, commitment, deployment or financial permission.
Opaque document sharing review is not semantic DLP certification.

Foundation MIT notices are preserved. They do not relicense customer artefacts,
grant IP rights or supply transfer clearance. Source checksums prove consistency,
not a signature. No credentials, deployment or runtime application are supplied.
"""
    review = f"""# Intake review

Evidence label: {label}. Synthetic compatibility is not real approval.
Intake disposition: {intake['review']['status']}.
Financial status: {financial_status}; never financial permission.

The immutable intake records retain the authored review, gaps and decisions.
Provided files are copied exactly, not rewritten or independently authenticated.
All declared current and historical files require explicit sharing review.
Opaque PDF and Office review is a human assertion, not semantic DLP.
Receiver and Cowork validation: not performed. Tenant readiness: not assessed.
Cowork discovery, install, acquisition and export: NOT PERFORMED.
Next: manual accountable-owner review, receiver tool checks and governed planning.
No application, solution source, tests, evaluations, IaC or remote issues are generated.
"""
    return {"START_HERE.md": start.encode("utf-8"),
            prefix + "/review.md": review.encode("utf-8")}


def assemble(request, foundation, intake, baseline, history_raw, producer_version, financial_status):
    """Return a complete, collision-checked entry set; the manifest never hashes itself."""
    current = f"docs/intake/records/{intake['intake_id']}/intake.json"
    manifest_path = "handover/manifest.json"
    generated = _generated_docs(request, intake, financial_status)
    generated[current] = encoded(intake)
    _disjoint(foundation, baseline, history_raw, generated, [manifest_path])
    entries = {portable(name): value for name, value in foundation.items()}
    for group in (baseline, history_raw, generated):
        for name, raw in group.items():
            entries[portable(name)] = (raw, 0o644)
    metadata = projection.export_metadata(request, intake, producer_version, financial_status)
    metadata["inventory"] = {
        name: {"sha256": digest(raw), "bytes": len(raw), "mode": mode}
        for name, (raw, mode) in sorted(entries.items())
    }
    entries[manifest_path] = (encoded(metadata), 0o644)
    archive.capacity(entries)  # Includes the manifest, not just its inventory.
    return entries


def _absolute_key(path):
    return str(path).replace("\\", "/").rstrip("/").casefold()


def _local(path, *, missing=False):
    raw = os.fspath(path)
    need(not raw.replace("\\", "/").startswith("//"), "FACTORY_PATH")
    return plain_path(path, missing=missing)


def protect_output(output, inputs, roots):
    """Check ancestry, portable aliases and existing hardlinks, not just resolve()."""
    output = _local(output, missing=True)
    key = _absolute_key(output)
    need(output.parent.is_dir() and (not output.exists() or output.is_file()), "FACTORY_OUTPUT")
    for root in roots:
        root = _local(root)
        other = _absolute_key(root)
        need(key != other and not key.startswith(other + "/")
             and not other.startswith(key + "/"), "FACTORY_OUTPUT")
    for original in inputs:
        # A prospective input name can be absent on case-sensitive platforms.
        original = _local(original, missing=True)
        other = _absolute_key(original)
        need(key != other and not key.startswith(other + "/")
             and not other.startswith(key + "/"), "FACTORY_OUTPUT")
        if output.exists() and original.exists():
            need(not os.path.samefile(output, original), "FACTORY_OUTPUT")
    return output


def _inventory(request, args, records):
    inputs = [args.request, args.template]
    for row in request["intake"]["artifacts"]:
        if row["status"] == "provided":
            inputs.extend([args.source_root.joinpath(*parts(row["source"]["path"])),
                           args.baseline_root.joinpath(*parts(row["baseline"]["path"]))])
    for record_id, record in records.items():
        inputs.append(args.baseline_root / f"docs/intake/records/{record_id}/intake.json")
        inputs.extend(args.baseline_root.joinpath(*parts(row["baseline"]["path"]))
                      for row in record["artifacts"] if row["status"] == "provided")
    for packet in request["financial"]["packets"]:
        if packet["model_path"] is not None:
            inputs.append(args.source_root.joinpath(*parts(packet["model_path"])))
        inputs.extend(args.source_root.joinpath(*parts(path)) for path in packet["review_paths"])
    return inputs


class _Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise FactoryError("FACTORY_USAGE")


def _parse(argv):
    parser = _Parser(description=__doc__, allow_abbrev=False)
    for name in ("request", "template", "source-root", "baseline-root", "out"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--acknowledge-finops-preview", action="store_true",
                        help="Acknowledge the full optional FinOps Preview notice for this invocation.")
    return parser.parse_args(argv)


def _export(args):
    args.request, args.template = _local(args.request), _local(args.template)
    args.source_root, args.baseline_root = _local(args.source_root), _local(args.baseline_root)
    need(args.request.is_file() and args.template.is_file()
         and args.source_root.is_dir() and args.baseline_root.is_dir(), "FACTORY_FILE")
    roots = [args.source_root, args.baseline_root]
    protect_output(args.out, [args.request, args.template], roots)
    request = decode(read(args.request.parent, args.request.name, MIB))
    schema = decode(read(HERE, "references/intake.schema.json", MIB))
    contract.prevalidate_request(request, schema)  # Before all nested indexing/customer reads.
    protect_output(args.out, _inventory(request, args, {}), roots)
    profile = decode(read(HERE, "references/template-profile.json", MIB))
    source = read(args.template.parent, args.template.name, 32 * MIB)
    contract.source_receipt(request["template"], request["export_id"], request["created_at"], source)
    foundation = archive.foundation(source, request["template"]["root_prefix"], profile)
    history, old_files, old_raw = load_history(request["history"], args.baseline_root, schema,
                                              contract.validate_intake)
    intake, baseline, originals = contract.materialize(request["intake"], args.baseline_root,
                                                       args.source_root, read)
    current_record = f"docs/intake/records/{intake['intake_id']}/intake.json"
    _disjoint(baseline, old_files, old_raw, [current_record])
    contract.validate_intake(intake, schema, baseline, originals=originals, history=history)
    all_files = {**old_files, **baseline}
    for name, raw in all_files.items():
        projection.check_ordinary(name, raw)
    financial_status = projection.financial_check(request, [intake, *history.values()], all_files,
                                                   args.source_root, args.acknowledge_finops_preview)
    original, customer = projection.check_blueprint(request, baseline, originals)
    projection.check_selection(request, customer, intake)
    projection.check_sharing(request, [intake, *history.values()], all_files, original)
    with projection.sibling("frontier-blueprint", "build_blueprint") as bp:
        producer_version = bp.PLUGIN_VERSION
    entries = assemble(request, foundation, intake, all_files, old_raw, producer_version, financial_status)
    raw = archive.archive_bytes(entries, request["created_at"])
    protect_output(args.out, _inventory(request, args, history), roots)
    archive.publish(args.out, raw)
    return {"export_validation": "passed", "plugin_version": producer_version,
            "zip_sha256": digest(raw), "intake_disposition": intake["review"]["status"],
            "receiver_validation": "not-performed", "cowork_validation": "not-performed",
            "tenant_readiness": "not-assessed", "financial_status": financial_status,
            "evidence_kind": request["evidence_kind"]}


def _guidance(code):
    if code == "FACTORY_USAGE":
        return "Use the five required local paths; consult --help. No bypass or acquisition option exists."
    if code == "FACTORY_FORMAT":
        return ("Supply a reviewed JSON or Markdown equivalent for unsupported selected content; "
                "do not rename, silently drop or bypass it. PDF and Office remain opaque reviewed files.")
    if code in {"FACTORY_ZIP", "FACTORY_TEMPLATE", "FACTORY_COMPATIBILITY", "FACTORY_SCHEMA_PROFILE"}:
        return "Supply the actual compatible frozen template source ZIP and its matching fixed-profile receipt."
    if code == "FACTORY_BLUEPRINT_FINANCIAL_CONTEXT":
        return ("Derived agent_finops is not authority. Supply compatible authoritative financial inputs "
                "and a separately reviewed Blueprint projection; this cached Blueprint form is unsupported.")
    if code.startswith("FACTORY_FINANCIAL"):
        return ("Optional financial content requires the current --acknowledge-finops-preview, explicit "
                "source packets and owner review. Read frontier-finops/SKILL.md for the full Preview notice. "
                "Acknowledgement never grants financial permission.")
    return "Review local input structure, compatibility, scope, sharing and explicit evidence; no output was published."


def main(argv=None) -> int:
    try:
        args = _parse(argv)
        summary = _export(args)
    except FactoryError as error:
        code = str(error)
        print(json.dumps({"error": code, "guidance": _guidance(code)}, ensure_ascii=True, sort_keys=True))
        return 2 if code == "FACTORY_USAGE" else 1
    except OSError:
        print(json.dumps({"error": "FACTORY_IO", "guidance": _guidance("FACTORY_IO")}, sort_keys=True))
        return 1
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
