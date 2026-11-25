# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Tiny synthetic compatibility data, never real acquisition or consent."""
import copy
import hashlib
import io
import json
from pathlib import Path
import zipfile

from tests.unit._util import load

ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "plugin/skills/frontier-agent-factory"
AT = "2026-11-25T12:00:00Z"
COMMIT = "0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d"


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def approved(reference="synthetic-review-not-authentication"):
    return {"by": "Caldova synthetic reviewer", "at": AT, "reference": reference}


def zip_bytes(files, compression=zipfile.ZIP_STORED):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 25, 12, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = compression
            archive.writestr(info, raw)
    return out.getvalue()


def prepare(root, *, accepted=False, foundation=None):
    root = Path(root)
    source, baseline = root / "originals", root / "approved"
    source.mkdir(parents=True)
    baseline.mkdir(parents=True)
    renderer = load("plugin/skills/frontier-blueprint/scripts/build_blueprint.py")
    report = renderer.Report()
    authored = {
        "meta": {"customer": "Caldova Industrial AG", "audience": "internal"},
        "evidence": [{"id": "SYN-INT", "visibility": "internal", "note": "Synthetic private working note."}],
        "domains": [{"id": "D1", "name": "Caldova service", "visibility": "public",
                     "agents": [{"id": "D1-A01", "name": "Caldova assistant", "visibility": "public",
                                 "autonomy": "Assist"}]}],
    }
    blueprint = renderer.normalise(copy.deepcopy(authored), report)
    blueprint["meta"]["generated"] = AT[:10]
    reviewed = renderer.customer_version(blueprint, report)
    if report.errors:
        raise AssertionError("Synthetic blueprint must pass the existing privacy helper")
    docs = {
        "prd.md": b"# Caldova synthetic PRD\n\nFR-001: Show the reviewed status.\n",
        "design.md": b"# Caldova synthetic design\n\nRetain FR-001 and a human review seam.\n",
        "blueprint.json": encode(blueprint),
    }
    baselines = dict(docs, **{"blueprint.json": encode(reviewed)})
    record = "caldova-intake"
    prefix = f"docs/intake/records/{record}/artifacts/"
    names = {"prd": "prd.md", "solution-design": "design.md", "blueprint": "blueprint.json"}
    rows = []
    for role in ("prd", "solution-design", "decisions", "it-readiness", "identity", "blueprint", "value", "finops"):
        name = names.get(role)
        provided = name is not None
        transformed = role == "blueprint"
        rows.append({
            "id": role, "solution_ids": ["caldova-service"], "role": role,
            "status": "provided" if provided else "not-applicable",
            "rationale": "Reviewed synthetic evidence." if provided else {
                "decisions": "No architecture alternatives in this local status view.",
                "it-readiness": "No tenant or service connection.",
                "identity": "No deployed identity.",
                "value": "No benefit claim.",
                "finops": "No cost operation requested.",
            }[role],
            "source": {"path": name, "reference": "synthetic-selected-source",
                       "version": "synthetic-v1", "modified_at": "unknown"} if provided else None,
            "baseline": {"path": prefix + name} if provided else None,
            "transformation": {
                "kind": "redaction" if transformed else "none",
                "rationale": "Customer privacy projection reviewed synthetically." if transformed else
                             "Exact reviewed synthetic bytes.",
                "approval": approved() if transformed else None,
            } if provided else None,
        })
    for name, raw in docs.items():
        (source / name).write_bytes(raw)
        path = baseline / (prefix + name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(baselines[name])
    intake = {
        "schema_version": "1.0", "intake_id": record, "supersedes": None,
        "selected_solutions": [{"solution_id": "caldova-service", "agent_ids": ["service-agent"],
                                "scope": "Caldova synthetic status review only.",
                                "owners": ["Caldova synthetic product owner"]}],
        "source": {"kind": "exported-package", "references": ["synthetic-selected-source"],
                   "plugin_version": "unknown", "blueprint_version": "unknown"},
        "acquisition": {"status": "succeeded", "method": "exported-files",
                        "verified_by": "Caldova synthetic fixture author", "verified_at": AT,
                        "evidence": "Actual local synthetic bytes; no tenant access."},
        "transfer": {"classification": "public", "destination": "Caldova synthetic review",
                     "permission": "approved", "approval": approved()},
        "artifacts": rows,
        "requirements": [{"id": "fr-001", "solution_id": "caldova-service",
                          "description": "Show the reviewed status.",
                          "acceptance_criteria": ["The selected status is visible."]}],
        "gaps": [] if accepted else [{"id": "implementation-gap", "solution_id": "caldova-service",
                                     "description": "Review implementation boundaries before acceptance.",
                                     "blocking": True, "status": "open", "resolution": None}],
        "decisions": [],
        "review": {"status": "accepted" if accepted else "needs-clarification",
                   "rationale": "Synthetic receiver compatibility, not real approval.",
                   "approval": approved() if accepted else None},
    }
    if foundation is None:
        foundation = zip_bytes({
            "LICENSE": (ROOT / "tests/fixtures/factory/LICENSE.template.MIT").read_bytes(),
            ".agents/skills/LICENSE.superpowers": b"Synthetic notice fixture; no vendored code.\n",
            ".agents/superpowers.lock.json": b'{"synthetic":true}\n',
            "AGENTS.md": b"# Passive synthetic receiving policy; not an authentic source checkout\n",
            ".github/workflows/test.yml": b"name: Passive synthetic fixture\n",
            "solutions/README.md": b"# No accepted solution units yet\n",
            "docs/intake/intake.schema.json": (F / "references/intake.schema.json").read_bytes(),
            "tools/intake.py": (ROOT / "tests/fixtures/factory/intake-reference.py.txt").read_bytes(),
        })
    archive = root / "template.zip"
    archive.write_bytes(foundation)
    request = {
        "schema": "frontier-agent-factory-request/1.0", "export_id": "caldova-export",
        "created_at": AT, "customer_scope": "Caldova synthetic service",
        "evidence_kind": "synthetic-compatibility",
        "template": {
            "repository": "urruegg/frontier-agent-factory", "selection": "unreleased-bootstrap",
            "commit": COMMIT, "release": None,
            "discovery": {"status": "succeeded", "complete": True, "export_id": "caldova-export",
                          "observed_at": AT, "evidence": "Synthetic healthy empty enumeration.",
                          "releases": []},
            "bootstrap_approval": approved("synthetic-bootstrap-" + COMMIT),
            "acquisition": {"status": "succeeded", "method": "explicit-local-source",
                            "by": "Caldova synthetic fixture author", "at": AT,
                            "evidence": "Synthetic acquisition, not current live discovery.",
                            "archive_sha256": hashlib.sha256(foundation).hexdigest()},
            "root_prefix": "",
        },
        "intake": intake,
        "blueprint": {"source_path": "blueprint.json", "baseline_path": prefix + "blueprint.json"},
        "id_map": {"solutions": {"D1": "caldova-service"}, "agents": {"D1-A01": "service-agent"},
                   "requirements": {"FR-001": "fr-001"}},
        "selection_evidence": [{"solution_id": "caldova-service", "original_solution_id": "D1",
                                "original_agent_ids": ["D1-A01"],
                                "rationale": "Explicit synthetic scope, not keyword selection.",
                                "dependency_gaps": []}],
        "sharing_review": {"customer_scope": "Caldova synthetic service", "metadata": approved(),
                           "artifacts": {record + ":" + row["id"]: approved()
                                         for row in rows if row["status"] == "provided"}},
        "history": [],
        "financial": {"requested": False, "as_of": None, "claim": "review", "packets": []},
    }
    result = {"request": request, "request_file": root / "request.json", "template": archive,
              "source": source, "baseline": baseline, "out": root / "factory.zip", "originals": docs}
    save(result)
    return result


def save(fixture):
    request = fixture["request"]
    request["template"]["acquisition"]["archive_sha256"] = hashlib.sha256(fixture["template"].read_bytes()).hexdigest()
    fixture["request_file"].write_bytes(encode(request))
