#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Offline Preview baseline CLI: seed, migrate, calculate, freeze, record-review,
apply and export. Explicit --as-of and current --acknowledge-finops-preview are
required. Outputs are local private files, never automatically published.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import date
from pathlib import Path

from baseline_calc import calculate, validate_receipt
from baseline_model import validate_model
from baseline_projection import VIEW_SCHEMA, _Projection, _withheld_report, project, render_markdown
from baseline_records import (
    BOUNDARY, SNAPSHOT_SCHEMA, _agent, _day, _json_text, _snapshot, _write_exclusive,
    freeze, migrate, record_review, seed,
)
from finops_preview import NOTICE, require_preview_ack


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # Argparse's supplied-value text can contain private material.
        raise ValueError("invalid or missing command arguments; use --help")


def _read(path):
    def reject_constant(value):
        raise ValueError("nonfinite JSON is not supported")
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON object keys are ambiguous")
            result[key] = value
        return result
    with Path(path).open(encoding="utf-8") as stream:
        document = json.load(stream, parse_constant=reject_constant, object_pairs_hook=unique_object)
    if not isinstance(document, dict):
        raise ValueError("JSON input must be an object")
    return document


def _authored(document, as_of):
    if document.get("schema") == SNAPSHOT_SCHEMA:
        model, _, _ = _snapshot(document, as_of=as_of)
        return model
    return document


def _link_private(blueprint, agent_id, audience, customer_scope):
    domain, agent = _agent(blueprint, agent_id)
    raw_sources = blueprint.get("sources", blueprint.get("evidence", []))
    if not isinstance(raw_sources, list) or any(not isinstance(s, dict) for s in raw_sources):
        raise ValueError("Blueprint source register must be a list of objects")
    identities = [s.get("id") for s in raw_sources]
    if any(not isinstance(identity, str) for identity in identities) or len(set(identities)) != len(identities):
        raise ValueError("Blueprint source register requires unique IDs")
    projection = _Projection({"sources": raw_sources}, audience, customer_scope, [])
    # Unrelated private agents/sources do not taint this agent's linkage.
    return (projection.restricted(blueprint) or
            projection.restricted(domain, inherited_scope=blueprint.get("customer_scope")) or
            projection.any_restricted(agent, "agent", domain.get("customer_scope", blueprint.get("customer_scope"))))


def apply_models(blueprint, baselines, reviews=(), *, as_of, audience, customer_scope=None,
                 acknowledge_finops_preview=False):
    """Preflight every input; attach ONLY derivative reports to a detached copy.

    The unchanged ordinary Blueprint still needs its normal customer scrub in
    the wrapper/renderer pipeline. This function does not publish or rewrite
    value-case data, and does not imply Blueprint-wide distribution clearance.
    """
    require_preview_ack(acknowledge_finops_preview)
    _day(as_of)
    if not isinstance(blueprint, dict):
        raise ValueError("blueprint must be an object")
    if any(key in blueprint for key in ("finops", "agent_finops")):
        raise ValueError("ambiguous legacy/new financial blocks; supply an explicit clean Blueprint copy")
    if not isinstance(baselines, (tuple, list)) or not baselines:
        raise ValueError("at least one explicit baseline is required")
    if not isinstance(reviews, (tuple, list)) or any(not isinstance(r, dict) for r in reviews):
        raise ValueError("reviews must be explicit review objects")
    agents, targets, reports, used = set(), set(), [], set()
    for document in baselines:
        if not isinstance(document, dict):
            raise ValueError("baseline must be an object")
        model = _authored(document, as_of)
        if document.get("schema") != SNAPSHOT_SCHEMA:
            validate_receipt(model, as_of=as_of, acknowledge_finops_preview=True)
        validate_model(model, as_of=as_of, blueprint=blueprint)
        agent = model.get("profile", {}).get("agent_id")
        _agent(blueprint, agent)
        if agent in agents:
            raise ValueError("duplicate active agent baseline versions; select one explicitly")
        agents.add(agent)
        baseline = model.get("baseline", {})
        target = (baseline.get("id"), baseline.get("version"))
        if target in targets:
            raise ValueError("duplicate active baseline target")
        targets.add(target)
        selected = []
        for i, review in enumerate(reviews):
            if (review.get("baseline_id"), review.get("version")) == target:
                used.add(i)
                selected.append(review)
        report = project(document, selected, as_of=as_of, audience=audience, customer_scope=customer_scope,
                         acknowledge_finops_preview=True)
        if _link_private(blueprint, agent, audience, customer_scope):
            report = _withheld_report(report)
        reports.append(report)
    if used != set(range(len(reviews))):
        raise ValueError("review does not match an explicitly supplied frozen baseline")
    output = copy.deepcopy(blueprint)
    output["agent_finops"] = {
        "schema": VIEW_SCHEMA, "notice": NOTICE, "maturity": "Preview", "as_of": as_of.isoformat(),
        "audience": audience, "records": reports, "financial_permission": False, "limitations": BOUNDARY,
    }
    return output


def _parser():
    parser = _Parser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    for command in ("seed", "migrate", "calculate", "freeze", "record-review", "apply", "export"):
        sub = commands.add_parser(command)
        sub.add_argument("--as-of", required=True, type=date.fromisoformat)
        sub.add_argument("--acknowledge-finops-preview", action="store_true")
        if command in {"seed", "migrate", "apply"}:
            sub.add_argument("--blueprint", required=True, type=Path)
        if command in {"seed", "migrate"}:
            sub.add_argument("--agent-id", required=True)
        if command != "seed":
            sub.add_argument("--baseline", required=True, type=Path, action="append" if command == "apply" else "store")
        if command in {"record-review", "apply", "export"}:
            sub.add_argument("--review", type=Path, action="append", required=command == "record-review", default=[])
        if command in {"freeze", "record-review", "export"}:
            sub.add_argument("--out-dir", required=True, type=Path)
        else:
            sub.add_argument("--out", required=True, type=Path)
        if command in {"apply", "export"}:
            sub.add_argument("--audience", required=True, choices=("internal", "customer"))
            sub.add_argument("--customer-scope")
    return parser


def _prevent_input_output_alias(args):
    inputs = []
    for key in ("baseline", "blueprint", "review"):
        value = getattr(args, key, None)
        inputs.extend(value if isinstance(value, list) else [value] if value is not None else [])
    output = getattr(args, "out", None)
    if output is not None and output.resolve() in {p.resolve() for p in inputs}:
        raise ValueError("output must not alias an input file")
    if args.command == "export":
        if any((args.out_dir / name).resolve() in {p.resolve() for p in inputs} for name in ("report.json", "report.md")):
            raise ValueError("export must not alias an input file")


def main(argv=None) -> int:
    try:
        args = _parser().parse_args(argv)
        require_preview_ack(args.acknowledge_finops_preview)  # before ANY input reads or output directories
        _prevent_input_output_alias(args)
        common = {"as_of": args.as_of, "acknowledge_finops_preview": True}
        command = args.command
        result = None
        if command == "seed":
            result = seed(_read(args.blueprint), args.agent_id, **common)
        elif command == "migrate":
            result = migrate(_read(args.baseline), _read(args.blueprint), args.agent_id, **common)
        elif command == "calculate":
            document = _read(args.baseline)
            if document.get("schema") == SNAPSHOT_SCHEMA:
                raise ValueError("a frozen snapshot is immutable; calculate a new editable version")
            result = calculate(document, **common)
        elif command == "freeze":
            freeze(_read(args.baseline), args.out_dir, **common)
        elif command == "record-review":
            if len(args.review) != 1:
                raise ValueError("record-review takes exactly one explicit decision")
            record_review(_read(args.baseline), _read(args.review[0]), args.out_dir, **common)
        elif command == "apply":
            result = apply_models(_read(args.blueprint), [_read(p) for p in args.baseline],
                                  [_read(p) for p in args.review], audience=args.audience,
                                  customer_scope=args.customer_scope, **common)
        elif command == "export":
            result = project(_read(args.baseline), [_read(p) for p in args.review],
                             audience=args.audience, customer_scope=args.customer_scope, **common)
            # Validate and serialise BOTH before output effects; refuse existing exports.
            json_text, markdown = _json_text(result), render_markdown(result)
            json_path, md_path = args.out_dir / "report.json", args.out_dir / "report.md"
            if json_path.exists() or md_path.exists():
                raise ValueError("export exists; select a new output directory")
            args.out_dir.mkdir(parents=True, exist_ok=True)
            with json_path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json_text)
            with md_path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(markdown)
        if result is not None and command != "export":
            _write_exclusive(args.out, result)
        # A successful local operation is not evidence that the whole forecast
        # is complete. Default summaries contain no paths, IDs, prices or notes.
        status = "partial"
        if command == "export" and result.get("status") == "planning-ready":
            status = "planning-ready"
        print(json.dumps({"command": command, "status": status, "maturity": "Preview",
                          "financial_permission": False}, sort_keys=True))
        return 0
    except SystemExit as error:
        return int(error.code)
    except (ValueError, OSError, UnicodeError):
        # Even field paths / OS filenames can contain private IDs. Do not echo them.
        message = NOTICE + " Explicit current acknowledgement required." if (
            "args" in locals() and not args.acknowledge_finops_preview) else (
                "FinOps operation refused: invalid input, review, receipt, output or I/O; no financial permission.")
        print(message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
