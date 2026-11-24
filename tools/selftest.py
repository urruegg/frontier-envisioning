#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""End-to-end self-test of the plugin scripts against the bundled examples.

Usage (from the repository root):  python tools/selftest.py   (the plugin lives in plugin/)

Runs, in a temporary folder:
  1. context_pack.py validate + render on the example context pack
  2. parse_transcript.py on a small synthetic WebVTT transcript
  3. seed_blueprint.py from the context pack, then build_blueprint.py on the seed
  4. build_blueprint.py on the Caldova example (internal and customer audiences); the agent workflows
     (authored, derived from the canvas plan, checked for unknown node types and agents)
  5. merge_feedback.py with a synthetic workshop feedback export
  6. scaffold_design_docs.py for the MVP agents (with each MVP agent's workflow);
     shared PRD model, Plan board, risk register, evidence-based contributions
  7. agent identity: read_office_theme.py on a synthetic deck, seed_identity.py from the Caldova blueprint,
     make_kit.py on the Caldova example (validator 0 errors, kit unit tests pass), apply_identity.py and a
     blueprint build with the Agent identity page; build_with_identity.py (blueprint and identity kit in one
     step, seeded from the blueprint without a brand file)
  7b. business value and FinOps: finops_calc.py and value_calc.py reproduce the method's worked example
     (credits, purchase options, scenarios, NPV, ROI, payback, break-even); the Caldova value case and FinOps
     model built into the blueprint; workshop verdicts merged; seeds that leave volumes to collect
  8. build_package.py, then the Cowork install check on the extracted package (and on an altered copy)
Most scripts are imported and their main(argv) called. Baseline CLI preparation
also executes the actual extracted scripts in isolated subprocesses. Nothing is
fetched from the network; technical fixture acknowledgement is not viewer consent.
Exit code 0 when every step passes.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "plugin" / "skills"


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, argv) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = mod.main(argv)
    return code, buf.getvalue()


THEME = """<?xml version="1.0" encoding="UTF-8"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Synthetic Theme"><a:themeElements>
<a:clrScheme name="Synthetic"><a:dk1><a:sysClr val="windowText" lastClr="111111"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
<a:dk2><a:srgbClr val="0B3954"/></a:dk2><a:lt2><a:srgbClr val="E8EEF2"/></a:lt2><a:accent1><a:srgbClr val="0F6CBD"/></a:accent1>
<a:accent2><a:srgbClr val="00827F"/></a:accent2><a:accent3><a:srgbClr val="107C41"/></a:accent3><a:accent4><a:srgbClr val="C0541A"/></a:accent4>
<a:accent5><a:srgbClr val="6B4FA0"/></a:accent5><a:accent6><a:srgbClr val="F2B544"/></a:accent6><a:hlink><a:srgbClr val="0F6CBD"/></a:hlink>
<a:folHlink><a:srgbClr val="6B4FA0"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Synthetic"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
</a:themeElements></a:theme>"""
MASTER_RELS = """<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>"""

VTT = """WEBVTT

00:00:01.000 --> 00:00:06.000
<v Head of Service>Our technicians write reports manually in the evening.</v>

00:00:06.500 --> 00:00:12.000
<v Facilitator>Which system holds the work orders?</v>

00:00:12.500 --> 00:00:18.000
<v Head of Service>Dynamics 365 Field Service. We agreed to share 20 reports by Friday.</v>
"""


def process_checks(t: Path, sample: Path, check) -> None:
    """Exercise process commands independently of the optional FinOps flow."""
    process = S / "frontier-process"
    seed = load(process / "scripts/seed_ontology.py")
    build = load(process / "scripts/build_ontology.py")
    apply = load(process / "scripts/apply_ontology.py")
    merge = load(process / "scripts/merge_ontology_feedback.py")
    blueprint = load(S / "frontier-blueprint/scripts/build_blueprint.py")
    work = t / "process-checks"
    work.mkdir()
    example = process / "examples/caldova-ontology.json"
    originals = {path: path.read_bytes() for path in (sample, example)}
    code, text = run(seed, ["--blueprint", str(sample), "--out", str(work / "seed.json")])
    seeded = json.loads((work / "seed.json").read_text(encoding="utf-8")) if code == 0 else {}
    check("process seed derives standard entities and OneLake sources", code == 0
          and {"Customer", "WorkOrder", "AlarmEvent"} <= {e["id"] for e in seeded.get("entity_types", [])}
          and len(seeded.get("sources", [])) == 9, text[-300:])
    sap = [source for source in seeded.get("sources", []) if source["id"].startswith("src-sap")]
    prerequisites = {"supported_source", "fabric_capacity", "datasphere_environment",
                     "premium_outbound_integration", "adls_gen2_permissions"}
    check("process SAP seeds retain five unknown prerequisites", bool(sap) and all(
        (source["path"], source["item"], source["status"]) == ("unresolved", None, "later")
        and source["route_assessment"]["state"] == "conditional"
        and set(source["route_assessment"]["prerequisites"]) == prerequisites
        and all(row["status"] == "unknown" and row["src"] == []
                for row in source["route_assessment"]["prerequisites"].values()) for source in sap))
    args = ["--ontology", str(example), "--blueprint", str(sample), "--out-dir", str(work / "artifacts")]
    code, text = run(build, args)
    files = {p.name: p.read_bytes() for p in (work / "artifacts").iterdir()} if code == 0 else {}
    expected = {"ontology.normalized.json", "ontology.ttl", "ontology.md", "data-agents.md", "data-products.md"}
    norm = json.loads(files.get("ontology.normalized.json", b"{}"))
    check("process builds five deterministic artifacts with explicit mapping gaps",
          code == 0 and set(files) == expected and norm.get("stats", {}).get("to_verify") == 6
          and files.get("ontology.ttl", b"").count(b" a owl:Class") == 27, text[-300:])
    governance = norm.get("current_guidance", {}).get("governance", {}).get("text", "")
    check("process current governance separates grouping from access",
          all(term in governance for term in ("OneLake catalog", "Fabric domain", "does not", "access", "DLP", "parity")))
    products = {row["id"]: row for row in norm.get("data_products", [])}
    check("process conditional SAP products remain unpublishable",
          all(f"source route {source}: conditional" in products.get(product, {}).get("gaps", [])
              for product, source in (("DP-07", "src-sap-s-4hana"), ("DP-08", "src-sap-ariba"),
                                      ("DP-16", "src-sap-s-4hana")))
          and norm.get("current_readiness", {}).get("F-06", {}).get("status") == "open")
    code2, _ = run(build, args)
    check("process rebuild is byte-identical and LF-only", code2 == 0 and files == {p.name: p.read_bytes() for p in (work / "artifacts").iterdir()}
          and all(b"\r\n" not in content for content in files.values()))
    code, text = run(build, args + ["--strict"])
    check("strict process warnings preserve previous good artifacts", code == 1 and files == {p.name: p.read_bytes() for p in (work / "artifacts").iterdir()}, text[-300:])
    code, text = run(apply, ["--blueprint", str(sample), "--ontology", str(work / "artifacts/ontology.normalized.json"), "--out", str(work / "bp.json")])
    bp = json.loads((work / "bp.json").read_text(encoding="utf-8")) if code == 0 else {}
    groups = [g for g in (bp.get("it_readiness") or {}).get("groups", []) if g.get("id") == "fabric-iq"]
    check("process apply writes the model and one readiness group", code == 0 and len(groups) == 1 and len(groups[0]["items"]) == 15, text[-300:])
    feedback = work / "feedback.json"
    feedback.write_text(json.dumps({"type": "frontier-blueprint-feedback", "exported": "2026-11-12T10:00:00Z",
        "validations": {"onto:WorkOrder": {"status": "validated", "note": "Synthetic confirmation"}, "onto:DP-999": {"status": "validated"}}}),
        encoding="utf-8", newline="\n")
    merged = work / "merged.json"
    code, text = run(merge, ["--ontology", str(work / "artifacts/ontology.normalized.json"), "--feedback", str(feedback), "--out", str(merged)])
    summary = json.loads(text) if code == 0 else {}
    before = merged.read_bytes() if code == 0 else b""
    code2, _ = run(merge, ["--ontology", str(merged), "--feedback", str(feedback), "--out", str(merged)]) if code == 0 else (1, "")
    check("process feedback reports unknown IDs and repeats without duplication", code == 0 and code2 == 0
          and summary.get("unknown") == ["onto:DP-999"] and before == merged.read_bytes(), text[-300:])
    sentinel = "SYNTHETIC_PROCESS_PRIVACY_SELFTEST"
    if bp.get("ontology"):
        bp["ontology"]["visibility"] = "internal"
        bp["ontology"]["entity_types"][0]["description"] = sentinel
        bp["ontology"]["readiness"][0]["item"] = sentinel
    (work / "private.json").write_text(json.dumps(bp), encoding="utf-8", newline="\n")
    code, text = run(blueprint, ["--data", str(work / "private.json"), "--audience", "customer",
                                "--save-normalized", str(work / "customer.json"), "--no-product-icons"])
    customer = (work / "customer.json").read_text(encoding="utf-8") if code == 0 else sentinel
    check("process root privacy precedes customer projection", code == 0 and sentinel not in customer and '"ontology"' not in customer, text[-300:])
    check("process inputs remain byte-identical", originals == {path: path.read_bytes() for path in originals})


def installed_run(script: Path, argv: list[str], work: Path) -> subprocess.CompletedProcess:
    """Run the supplied installation, not in-process working-tree modules or PYTHONPATH."""
    env = {key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}}
    return subprocess.run([sys.executable, "-E", "-s", "-B", "-X", "utf8", str(script), *argv], cwd=work,
                          env=env, capture_output=True, text=True, encoding="utf-8", timeout=120)


def baseline_cli_checks(package: Path, work: Path, check) -> None:
    """Initial offline CLI proof; repeat against the exact final archive after UI/docs."""
    skills = package / "skills"
    script = skills / "frontier-finops/scripts/agent_finops.py"
    example = skills / "frontier-finops/examples/caldova-agent-baseline.json"
    sample = skills / "frontier-blueprint/examples/caldova-blueprint.json"
    originals = {path: path.read_bytes() for path in (example, sample)}
    authored = json.loads(originals[example])
    day, agent = authored["baseline"]["as_of"], authored["profile"]["agent_id"]
    ack = ["--as-of", day, "--acknowledge-finops-preview"]
    notice = authored["preview_notice"]

    def cli(command, *args, acknowledged=True):
        flags = ack if acknowledged else ["--as-of", day]
        return installed_run(script, [command, *map(str, args), *flags], work)

    def read(path):
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def write(path, document):
        path.write_text(json.dumps(document, allow_nan=False) + "\n", encoding="utf-8", newline="\n")

    def partial(proc, command):
        return proc.returncode == 0 and json.loads(proc.stdout) == {
            "command": command, "status": "partial", "maturity": "Preview", "financial_permission": False,
        }

    refusals = {
        "seed": ["--blueprint", sample, "--agent-id", agent],
        "calculate": ["--baseline", example],
        "apply": ["--blueprint", sample, "--baseline", example, "--audience", "internal"],
        "export": ["--baseline", example, "--audience", "customer"],
    }
    for command, args in refusals.items():
        target = work / ("refused-" + command) / "output"
        proc = cli(command, *args, "--out-dir" if command == "export" else "--out", target, acknowledged=False)
        check(f"installed baseline {command} requires fresh acknowledgement before outputs",
              proc.returncode == 2 and notice in proc.stderr and not target.parent.exists(), proc.stderr[-300:])

    seeded = work / "seed.json"
    proc = cli("seed", "--blueprint", sample, "--agent-id", agent, "--out", seeded)
    seed = read(seeded)
    check("installed baseline seed retains explicit unknowns without financial authority",
          partial(proc, "seed") and seed.get("schema") == "frontier-finops-baseline/1.0"
          and seed.get("profile", {}).get("agent_id") == agent and seed.get("rates") == [], proc.stderr[-300:])
    seeded_calc = work / "seed-calculated.json"
    proc = cli("calculate", "--baseline", seeded, "--out", seeded_calc)
    seed_results = read(seeded_calc).get("results", {})
    check("installed incomplete seed calculates as gaps, not zero-cost completeness",
          partial(proc, "calculate") and bool(seed_results.get("gaps"))
          and all(row["annual_recurring"]["amount"] is None for row in seed_results.get("scenarios", {}).values()),
          proc.stderr[-300:])

    calculated = work / "calculated.json"
    proc = cli("calculate", "--baseline", example, "--out", calculated)
    model = read(calculated)
    expected = model.get("results", {}).get("scenarios", {}).get("expected", {})
    check("installed synthetic baseline calculates provisional estimates with safe summary",
          partial(proc, "calculate") and model.get("forecast_kind") == "estimate"
          and expected.get("annual_recurring", {}).get("amount") == "1320.00"
          and expected.get("annual_recurring", {}).get("status") == "provisional", proc.stderr[-300:])
    frozen_dir = work / "snapshots"
    proc = cli("freeze", "--baseline", calculated, "--out-dir", frozen_dir)
    snapshots = list(frozen_dir.glob("*.json"))
    check("installed baseline freezes exactly one snapshot", partial(proc, "freeze") and len(snapshots) == 1, proc.stderr[-300:])
    if len(snapshots) != 1:
        return
    snapshot_path = snapshots[0]
    snapshot = read(snapshot_path)
    frozen_bytes = snapshot_path.read_bytes()
    proc = cli("freeze", "--baseline", calculated, "--out-dir", frozen_dir)
    check("installed snapshot cannot be overwritten",
          proc.returncode == 2 and snapshot_path.read_bytes() == frozen_bytes and len(list(frozen_dir.iterdir())) == 1)

    review_input = work / "synthetic-review.json"
    review = {**snapshot["target"], "id": "SELFTEST-SYNTHETIC", "decision": "approve",
              "actor": authored["profile"]["owners"]["finance"], "finance_owner": authored["profile"]["owners"]["finance"],
              "date": day, "evidence_ref": "synthetic-selftest-not-a-human-decision", "mode": "synthetic",
              "synthetic": True, "sharingClassification": "customer-shareable"}
    write(review_input, review)
    reviews_dir = work / "reviews"
    proc = cli("record-review", "--baseline", snapshot_path, "--review", review_input, "--out-dir", reviews_dir)
    reviews = list(reviews_dir.glob("*.json"))
    recorded = read(reviews[0]) if len(reviews) == 1 else {}
    check("installed review is an external synthetic assertion, not authenticated approval",
          partial(proc, "record-review") and len(reviews) == 1 and recorded.get("synthetic") is True
          and recorded.get("assertion") == "externally-asserted-not-authenticated", proc.stderr[-300:])
    if len(reviews) != 1:
        return
    applied = work / "applied.json"
    proc = cli("apply", "--blueprint", sample, "--baseline", snapshot_path, "--review", reviews[0],
               "--audience", "internal", "--out", applied)
    view = read(applied).get("agent_finops", {})
    check("installed apply produces the derivative Preview DTO, never viewer consent",
          partial(proc, "apply") and view.get("schema") == "frontier-agent-finops-view/1.0"
          and view.get("notice") == notice and view.get("financial_permission") is False
          and len(view.get("records", [])) == 1 and "preview_acknowledged" not in view, proc.stderr[-300:])

    exported = work / "internal-export"
    proc = cli("export", "--baseline", snapshot_path, "--review", reviews[0], "--audience", "internal",
               "--out-dir", exported)
    report = read(exported / "report.json")
    markdown = (exported / "report.md").read_text(encoding="utf-8") if (exported / "report.md").is_file() else ""
    handover = report.get("handover", {})
    check("installed JSON and Markdown keep notice, estimates and strict synthetic handover block",
          partial(proc, "export") and report.get("forecast_kind") == "estimate" and notice in markdown
          and handover.get("ready") is False and handover.get("financial_permission") is False
          and any("synthetic" in str(gap) for gap in handover.get("gaps", [])), proc.stderr[-300:])
    saved = {path: path.read_bytes() for path in exported.glob("*")}
    proc = cli("export", "--baseline", snapshot_path, "--audience", "internal", "--out-dir", exported)
    check("installed export refuses overwrite and preserves both files",
          proc.returncode == 2 and len(saved) == 2 and saved == {path: path.read_bytes() for path in exported.glob("*")})

    # Bounded corruptions of our own technical records; these are not audit-storage claims.
    corrupt = read(calculated)
    corrupt["results"]["scenarios"]["expected"]["annual_recurring"]["amount"] = "999999.00"
    corrupt_path = work / "tampered-receipt.json"
    write(corrupt_path, corrupt)
    target = work / "refused-receipt" / "output.json"
    proc = cli("apply", "--blueprint", sample, "--baseline", corrupt_path, "--audience", "internal", "--out", target)
    check("installed apply rejects a tampered calculation before outputs", proc.returncode == 2 and not target.parent.exists())
    corrupt = read(snapshot_path)
    corrupt["target"]["material_hash"] = "0" * 64
    corrupt_path = work / "tampered-snapshot.json"
    write(corrupt_path, corrupt)
    target = work / "refused-snapshot"
    proc = cli("export", "--baseline", corrupt_path, "--audience", "internal", "--out-dir", target)
    check("installed export rejects a tampered snapshot before outputs", proc.returncode == 2 and not target.exists())
    review["material_hash"] = "0" * 64
    write(review_input, review)
    target = work / "refused-review"
    proc = cli("record-review", "--baseline", snapshot_path, "--review", review_input, "--out-dir", target)
    check("installed review rejects a mismatched target hash", proc.returncode == 2 and not target.exists())

    private = json.loads(originals[example])
    sentinel = "SYNTHETIC_PRIVATE_BASELINE_SELFTEST"
    private["rates"][0]["sharingClassification"] = "internal-only"
    private["rates"][0]["note"] = sentinel
    private_input, private_calc = work / "private.json", work / "private-calculated.json"
    write(private_input, private)
    calc = cli("calculate", "--baseline", private_input, "--out", private_calc)
    customer_dir = work / "customer-export"
    proc = cli("export", "--baseline", private_calc, "--audience", "customer", "--customer-scope", "synthetic-caldova",
               "--out-dir", customer_dir)
    customer = read(customer_dir / "report.json")
    serialised = "".join(path.read_text(encoding="utf-8") for path in customer_dir.glob("*"))
    total = customer.get("scenarios", {}).get("expected", {}).get("annual_recurring", {})
    check("installed customer JSON/Markdown withhold private dependencies rather than rebuilding totals",
          partial(calc, "calculate") and partial(proc, "export") and notice in serialised
          and sentinel not in serialised and "RATE-TOKENS" not in serialised and "material_hash" not in serialised
          and total.get("amount") is None and total.get("status") == "withheld", proc.stderr[-300:])
    check("installed CLI preserves authored inputs and frozen records",
          originals == {path: path.read_bytes() for path in originals} and frozen_bytes == snapshot_path.read_bytes())


def installed_core_check(package: Path, work: Path, check) -> None:
    """Only call on our temporary extracted package, after installer verification."""
    skills = package / "skills"
    shutil.rmtree(skills / "frontier-finops")
    sample = skills / "frontier-blueprint/examples/caldova-blueprint.json"
    value = skills / "frontier-value-case/examples/caldova-value.json"
    example = skills / "frontier-process/examples/caldova-ontology.json"
    originals = {path: path.read_bytes() for path in (sample, value, example)}
    process = skills / "frontier-process/scripts"
    model = work / "installed-process-seed.json"
    proc = installed_run(process / "seed_ontology.py", ["--blueprint", str(sample), "--out", str(model)], work)
    seeded = json.loads(model.read_text(encoding="utf-8")) if proc.returncode == 0 else {}
    sap = [source for source in seeded.get("sources", []) if source["id"].startswith("src-sap")]
    prerequisites = {"supported_source", "fabric_capacity", "datasphere_environment",
                     "premium_outbound_integration", "adls_gen2_permissions"}
    check("installed process seeds unknown SAP prerequisites", proc.returncode == 0 and bool(sap) and all(
        (source["path"], source["item"], source["status"]) == ("unresolved", None, "later")
        and source["route_assessment"]["state"] == "conditional"
        and set(source["route_assessment"]["prerequisites"]) == prerequisites
        and all(row["status"] == "unknown" and row["src"] == []
                for row in source["route_assessment"]["prerequisites"].values()) for source in sap), proc.stderr[-300:])
    if model.is_file():
        originals[model] = model.read_bytes()
    artifacts = work / "installed-process"
    args = ["--ontology", str(model), "--blueprint", str(sample), "--out-dir", str(artifacts)]
    proc = installed_run(process / "build_ontology.py", args, work)
    files = {path.name: path.read_bytes() for path in artifacts.iterdir()} if artifacts.is_dir() else {}
    normalized = json.loads(files.get("ontology.normalized.json", b"{}"))
    governance = normalized.get("current_guidance", {}).get("governance", {}).get("text", "")
    check("installed process current guidance and five artifacts", proc.returncode == 0
          and set(files) == {"ontology.normalized.json", "ontology.ttl", "ontology.md", "data-agents.md", "data-products.md"}
          and all(term in governance for term in ("OneLake catalog", "does not", "access", "DLP", "parity")), proc.stderr[-300:])
    repeated = installed_run(process / "build_ontology.py", args, work)
    refused = installed_run(process / "build_ontology.py", args + ["--strict"], work)
    absent = work / "installed-strict-no-create"
    no_create = installed_run(process / "build_ontology.py", args[:-1] + [str(absent), "--strict"], work)
    applied = work / "installed-process-applied.json"
    apply = installed_run(process / "apply_ontology.py",
                          ["--blueprint", str(sample), "--ontology", str(artifacts / "ontology.normalized.json"),
                           "--out", str(applied)], work)
    applied_model = json.loads(applied.read_text(encoding="utf-8")).get("ontology", {}) if applied.is_file() else {}
    check("installed process strict warnings preserve outputs and inputs",
          repeated.returncode == 0 and refused.returncode == 1 and no_create.returncode == 1 and not absent.exists()
          and json.loads(refused.stdout).get("files") == {}
          and files == {path.name: path.read_bytes() for path in artifacts.iterdir()}
          and apply.returncode == 0 and applied_model.get("current_guidance") == normalized.get("current_guidance")
          and originals == {path: path.read_bytes() for path in originals}, refused.stderr[-300:])
    output = work / "core-without-finops"
    proc = installed_run(skills / "frontier-blueprint/scripts/build_with_identity.py", [
        "--data", str(sample), "--value", str(value), "--ontology", str(example),
        "--no-identity", "--out-dir", str(output),
    ], work)
    summary = json.loads(proc.stdout[proc.stdout.index("{"):]) if proc.returncode == 0 else {}
    html_path = Path(summary["html"]) if summary.get("html") else work / "missing.html"
    html = html_path.read_text(encoding="utf-8") if html_path.is_file() else ""
    island = re.search(r'<script[^>]+id="bp-data"[^>]*>(.*?)</script>', html, re.S)
    data = json.loads(island[1]) if island else {}
    check("installed core value/ontology build works with FinOps removed",
          proc.returncode == 0 and bool(data.get("value_case")) and bool(data.get("ontology"))
          and "finops" not in data and "agent_finops" not in data, proc.stderr[-300:])
    serialised = json.dumps(data)
    check("installed core has no financial output or consent", proc.returncode == 0
          and not any(term in serialised for term in ('"finops"', '"agent_finops"', '"financial_permission"', '"preview_ack"'))
          and summary.get("value_finops", {}).get("finops") is None
          and not any(key in summary for key in ("finops", "agent_finops", "finops_preview"))
          and all('"finops_preview"' not in path.read_text(encoding="utf-8")
                  for path in output.rglob("*.json"))
          and originals == {path: path.read_bytes() for path in originals})
    ontology = data.get("ontology", {})
    check("installed core current conditional SAP guidance survives",
          bool(ontology.get("current_guidance")) and ontology.get("current_readiness", {}).get("F-06", {}).get("status") == "open"
          and all(source.get("route_assessment", {}).get("state") == "conditional"
                  for source in ontology.get("sources", []) if source["id"].startswith("src-sap")))


def main() -> int:
    ok = True
    results = []

    def check(name, cond, detail=""):
        nonlocal ok
        results.append(("PASS" if cond else "FAIL", name, detail))
        ok = ok and cond

    cp = load(S / "frontier-context-discovery/scripts/context_pack.py")
    pt = load(S / "frontier-context-discovery/scripts/parse_transcript.py")
    sb = load(S / "frontier-blueprint/scripts/seed_blueprint.py")
    bb = load(S / "frontier-blueprint/scripts/build_blueprint.py")
    mf = load(S / "frontier-blueprint/scripts/merge_feedback.py")
    sd = load(S / "frontier-solution-design/scripts/scaffold_design_docs.py")
    ctx = S / "frontier-context-discovery/examples/caldova-context.json"
    sample = S / "frontier-blueprint/examples/caldova-blueprint.json"

    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        code, out = run(cp, ["validate", str(ctx)])
        check("context pack validates", code == 0, out[-200:] if code else "")
        code, _ = run(cp, ["render", str(ctx), "--out", str(t / "log.md"), "--audience", "customer"])
        log = (t / "log.md").read_text(encoding="utf-8") if (t / "log.md").exists() else ""
        check("evidence log renders without internal sources", code == 0 and "E02" not in log)

        (t / "t.vtt").write_text(VTT, encoding="utf-8")
        code, _ = run(pt, [str(t / "t.vtt"), "--evidence-id", "E09", "--out", str(t / "t.json")])
        turns = json.loads((t / "t.json").read_text(encoding="utf-8")) if code == 0 else {}
        cats = {s["category"] for s in turns.get("signals", [])}
        check("transcript parses into turns and signals", code == 0 and turns.get("stats", {}).get("turns") == 3 and {"pain", "system", "decision"} <= cats, str(cats))

        code, _ = run(sb, ["--context", str(ctx), "--out", str(t / "seed.json")])
        check("seed blueprint from context", code == 0)
        code, out = run(bb, ["--data", str(t / "seed.json"), "--out", str(t / "seed.html")])
        check("seed blueprint builds", code == 0, out[-300:] if code else "")

        code, out = run(bb, ["--data", str(sample), "--out", str(t / "bp.html"), "--save-normalized", str(t / "bp.json")])
        html = (t / "bp.html").read_text(encoding="utf-8") if code == 0 else ""
        check("example blueprint builds", code == 0 and '"__BLUEPRINT_DATA__"' not in html and "Caldova" in html, out[-300:] if code else "")
        check("no raw '<' inside the embedded data", code == 0 and "</script" not in html.split('id="bp-data">', 1)[1].split("</script>", 1)[0])
        code, out = run(bb, ["--data", str(sample), "--out", str(t / "bp-c.html"), "--audience", "customer"])
        chtml = (t / "bp-c.html").read_text(encoding="utf-8") if code == 0 else ""
        check("customer version strips internal evidence", code == 0 and "Caldova account plan FY27" not in chtml)
        process_checks(t, sample, check)

        # 1.4: Innovation Hub canon (Agent Factory journey, landing zone, ADRs, IT readiness), product icons, Hub journey views
        def stats_of(text):
            i = text.find('{"status"')
            try:
                return json.loads(text[i:]).get("stats", {}) if i >= 0 else {}
            except ValueError:
                return {}
        seedbp = json.loads((t / "seed.json").read_text(encoding="utf-8")) if (t / "seed.json").exists() else {}
        sfac = [d for d in seedbp.get("domains", []) if d.get("kind") == "factory"]
        sarch, srd = seedbp.get("architecture") or {}, seedbp.get("it_readiness") or {}
        check("seed adds the Hub canon (factory journey, landing zone, ADRs, IT readiness)", len(sfac) == 1 and len(sfac[0].get("agents", [])) == 5
              and all(p_.get("role") for p_ in sfac[0].get("personas", [])) and len((sarch.get("landing_zone") or {}).get("areas", {})) >= 14
              and sum(1 for x in sarch.get("decisions", []) if x.get("canon")) >= 6 and sum(len(g.get("items", [])) for g in srd.get("groups", [])) == 30
              and len(srd.get("checks", [])) == 15 and len(seedbp.get("factory", {}).get("lifecycle", [])) == 7)
        lean = json.loads(sample.read_text(encoding="utf-8"))
        lean["domains"] = [d for d in lean["domains"] if d.get("kind") != "factory"]
        for k in ("factory", "it_readiness", "feedback_loop"):
            lean.pop(k, None)
        lean["architecture"].pop("landing_zone", None)
        lean["architecture"]["decisions"] = [x for x in lean["architecture"].get("decisions", []) if not x.get("canon")]
        (t / "lean.json").write_text(json.dumps(lean), encoding="utf-8")
        code, out = run(bb, ["--data", str(t / "lean.json"), "--out", str(t / "lean.html"), "--canon"])
        st = stats_of(out)
        check("--canon completes an earlier blueprint (factory, landing zone, ADRs, readiness)", code == 0 and st.get("factory_journey") == "D5"
              and st.get("landing_zone_areas", 0) >= 14 and st.get("readiness_items") == 30 and st.get("decisions") == 9
              and st.get("feedback_loop_areas") == 4, out[-300:])
        code, out = run(bb, ["--data", str(sample), "--out", str(t / "icons.html")])
        st1, ihtml = stats_of(out), (t / "icons.html").read_text(encoding="utf-8") if code == 0 else ""
        code2, out2 = run(bb, ["--data", str(sample), "--out", str(t / "noicons.html"), "--no-product-icons"])
        check("Microsoft product icons embedded only when used, with their notice", code == 0 and code2 == 0 and st1.get("product_icons", 0) >= 10
              and '"logo_rules"' in ihtml and '"logos_note"' in ihtml and stats_of(out2).get("product_icons") == 0 and st1.get("attendees") == 8, (out + out2)[-300:])
        tplv = (S / "frontier-blueprint/templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
        check("template has the Hub journey views (attendees, factory, landing zone, ADRs, IT readiness)",
              all(f in tplv for f in ("function renderAttendees", "function renderFactorySections", "function renderLandingZone", "function lzSvg",
                                      "function renderDecisions", "function renderReadiness", 'id:"readiness", label:"IT readiness"', 'id:"attendees", label:"Attendees"')))

        # 1.5: Microsoft's digital feedback loop on the Overview (Microsoft IQ; official names only)
        sfl = {q.get("pillar"): q for q in (seedbp.get("feedback_loop") or {}).get("quadrants", [])}
        jid = {d.get("name"): d.get("id") for d in seedbp.get("domains", [])}
        sig_iq = [i for q in sfl.values() for x in q.get("signals", []) for i in x.get("iq", [])]
        check("seed adds the digital feedback loop with each journey in one area", len(sfl) == 4
              and jid.get("Commercial") in sfl.get("engage_customers", {}).get("journeys", [])
              and jid.get("Service") in sfl.get("optimize_operations", {}).get("journeys", [])
              and bool(sig_iq) and set(sig_iq) <= {"work", "fabric", "foundry", "web"})
        bpn = json.loads((t / "bp.json").read_text(encoding="utf-8")) if (t / "bp.json").exists() else {}
        odd = json.loads(sample.read_text(encoding="utf-8"))
        odd["feedback_loop"]["quadrants"][0]["signals"].append({"text": "Governance IQ checks every case", "iq": ["governance"]})
        (t / "odd.json").write_text(json.dumps(odd), encoding="utf-8")
        code, out = run(bb, ["--data", str(t / "odd.json")])
        check("digital feedback loop builds with official Microsoft IQ names only", len((bpn.get("feedback_loop") or {}).get("quadrants", [])) == 4
              and all(f in tplv for f in ("function flSvg", "animateMotion", "pauseAnimations", "prefers-reduced-motion"))
              and code == 0 and "'Governance IQ', which is not an official Microsoft IQ name" in out and "unknown Microsoft IQ layer governance" in out, out[-300:])

        # 1.6: agent workflows as Copilot Studio workflows (trigger, designer nodes, branches, desired outcome)
        wfs = {a.get("id"): a["canvas"]["workflow"] for d in bpn.get("domains", []) for a in d.get("agents", [])
               if isinstance(a.get("canvas"), dict) and isinstance(a["canvas"].get("workflow"), dict)}
        odd2 = json.loads(sample.read_text(encoding="utf-8"))
        for d in odd2["domains"]:
            for a_ in d.get("agents", []):
                if a_.get("id") == "D2-A01":
                    a_["canvas"].pop("workflow", None)
                if a_.get("id") == "D3-A05":
                    a_["canvas"]["workflow"]["steps"].append({"type": "magic", "label": "Do magic", "agent": "D9-A99"})
        (t / "wf.json").write_text(json.dumps(odd2), encoding="utf-8")
        code, out = run(bb, ["--data", str(t / "wf.json"), "--out", str(t / "wf.html"), "--save-normalized", str(t / "wf-n.json")])
        wn = json.loads((t / "wf-n.json").read_text(encoding="utf-8")) if code == 0 else {}
        dwf = next(((a_.get("canvas") or {}).get("workflow") or {} for d in wn.get("domains", []) for a_ in d.get("agents", []) if a_.get("id") == "D2-A01"), {})
        check("agent workflows build; a missing one is derived from the plan; unknown nodes and agents warn",
              set(wfs) == {"D2-A01", "D3-A05"} and st1.get("workflows") == 2 and wfs["D3-A05"]["trigger"]["type"] == "connector"
              and all(x.get("id") for x in wfs["D3-A05"]["steps"]) and code == 0 and dwf.get("derived") is True
              and dwf.get("trigger", {}).get("type") == "agent" and any(x.get("type") == "classify" for x in dwf.get("steps", []))
              and "node type 'magic' unknown" in out and "unknown agent 'D9-A99'" in out
              and all(f in tplv for f in ("function wfLayout", "function wfSvg", "function wfSection", "function wfPanel")), out[-300:])

        fb = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "version": "0.1",
              "exported": "2026-11-12T16:00:00Z",
              "validations": {"agent:D3-A05": {"status": "validated", "note": "Confirmed; start in region West"},
                              "uc:UC05": {"status": "adjusted", "note": "Pilot in plant B"}},
              "discovery": {"D3-Q02": {"status": "answered", "note": "12 mandatory fields; list shared"}}}
        (t / "fb.json").write_text(json.dumps(fb), encoding="utf-8")
        code, out = run(mf, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb.json"), "--out", str(t / "bp2.json")])
        merged = json.loads((t / "bp2.json").read_text(encoding="utf-8")) if code == 0 else {}
        a = next((x for d in merged.get("domains", []) for x in d.get("agents", []) if x.get("id") == "D3-A05"), {})
        check("feedback merges (status, notes, version bump)", code == 0 and a.get("status") == "validated" and merged["meta"]["version"] == "0.2", out[-300:] if code else "")
        fb2 = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "exported": "2026-11-12T16:00:00Z",
               "validations": {"ready:P-01": {"status": "done", "note": "Pay-as-you-go plan linked"}, "adr:ADR-F01": {"status": "validated", "note": "Agreed with IT"},
                               "adr:ADR-X99": {"status": "validated"}}}
        (t / "fb2.json").write_text(json.dumps(fb2), encoding="utf-8")
        code, out = run(mf, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb2.json"), "--out", str(t / "bp3.json")])
        m3 = json.loads((t / "bp3.json").read_text(encoding="utf-8")) if code == 0 else {}
        p01 = next((x for g in (m3.get("it_readiness") or {}).get("groups", []) for x in g.get("items", []) if x.get("id") == "P-01"), {})
        f01 = next((x for x in (m3.get("architecture") or {}).get("decisions", []) if x.get("id") == "ADR-F01"), {})
        check("workshop verdicts update IT readiness and architecture decisions", code == 0 and p01.get("status") == "done" and f01.get("status") == "agreed"
              and bool(f01.get("workshop_notes")) and '"adr:ADR-X99"' in out, out[-300:])

        fb3 = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "exported": "2026-11-12T16:00:00Z",
               "validations": {"loop:transform_products": {"status": "adjusted", "note": "Telemetry only for the new machine series"}}}
        (t / "fb3.json").write_text(json.dumps(fb3), encoding="utf-8")
        code, out = run(mf, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb3.json"), "--out", str(t / "bp4.json")])
        m4 = json.loads((t / "bp4.json").read_text(encoding="utf-8")) if code == 0 else {}
        tq = next((q for q in (m4.get("feedback_loop") or {}).get("quadrants", []) if q.get("pillar") == "transform_products"), {})
        check("workshop verdicts update the digital feedback loop", code == 0 and tq.get("status") == "adjusted" and bool(tq.get("workshop_notes")), out[-300:])

        code, out = run(sd, ["--blueprint", str(t / "bp2.json"), "--out-dir", str(t / "design")])
        prd = (t / "design/prd.md").read_text(encoding="utf-8") if code == 0 else ""
        sdoc = (t / "design/solution-design.md").read_text(encoding="utf-8") if code == 0 else ""
        rdoc = (t / "design/it-readiness.md").read_text(encoding="utf-8") if (t / "design/it-readiness.md").exists() else ""
        check("PRD and solution design scaffold", code == 0 and "FR-0001" in prd and sdoc and any((t / "design/adr").iterdir()))
        check("solution design carries the landing zone, the Agent Factory and the IT readiness checklist", "### 3.1 Landing zone" in sdoc
              and "### 8.2 Definition of Ready" in sdoc and "Innovation Hub canon" in sdoc and "P-30" in rdoc and "R-15" in rdoc and "D-08" in rdoc)
        check("solution design lists each MVP workflow (trigger, nodes, branches)", "### Workflow: Service report from voice notes (Service Report Agent)" in sdoc
              and "| 3.1 | Connector | Transcribe the voice note |" in sdoc and "- Trigger: When an agent calls the workflow" in sdoc)

        # DOM/browser tests verify the rendered parts; this check exercises the data flow.
        part_input = json.loads(json.dumps(bpn))
        part_input["parts"] = {
            "vision": {"label": "Synthetic vision", "desc": "Requirements first"},
            "design": {"label": "Synthetic design"}, "build": {"label": "Synthetic build"},
            "workshops": {"label": "Synthetic workshop"},
        }
        (t / "parts-input.json").write_text(json.dumps(part_input), encoding="utf-8")
        code, out = run(bb, ["--data", str(t / "parts-input.json"), "--save-normalized", str(t / "parts-output.json")])
        part_output = json.loads((t / "parts-output.json").read_text(encoding="utf-8")) if code == 0 else {}
        check("blueprint preserves authored part overrides and PRD/risk data",
              code == 0 and part_output.get("parts") == part_input["parts"]
              and bool(part_output.get("prd")) and bool((part_output.get("risks") or {}).get("items")), out[-300:])
        bprd = bpn.get("prd") or {}
        check("risk register, PRD and attendee evidence built from the blueprint", st1.get("risks") == 15 and st1.get("prd_requirements") == 35
              and st1.get("contributions_with_evidence") == 13 and bprd.get("mvp_agents") == ["D2-A01", "D3-A05"]
              and [r.get("id") for r in (bpn.get("risks") or {}).get("items", [])][:2] == ["R-UC09-1", "R-C03"]
              and (bpn.get("factory") or {}).get("board", {}).get("phases", [{}])[0].get("id") == "idea", json.dumps(st1)[:300])
        fr_ids = [r.get("id") for x in bprd.get("agents", []) for r in x.get("requirements", [])] + [r.get("id") for r in bprd.get("acceptance", [])]
        check("PRD model identical in both skills; design/prd.md carries the same requirement ids",
              (S / "frontier-blueprint/scripts/prd_model.py").read_bytes() == (S / "frontier-solution-design/scripts/prd_model.py").read_bytes()
              and len(fr_ids) >= 20 and all(i in prd for i in fr_ids))
        check("seed adds the Hub canon risks and the plan board", sum(1 for r in (seedbp.get("risks") or {}).get("items", []) if r.get("canon")) == 7
              and len((seedbp.get("factory") or {}).get("board", {}).get("phases", [])) == 4)
        fb4 = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "exported": "2026-11-12T16:00:00Z",
               "validations": {"risk:R-UC09-1": {"status": "mitigating", "likelihood": 3, "impact": 5, "note": "Works council briefing booked"},
                               "risk:R-C05": {"status": "rejected"}, "risk:R-X99": {"status": "open"},
                               "prd:scope": {"status": "validated", "note": "Two MVP agents agreed"}}}
        (t / "fb4.json").write_text(json.dumps(fb4), encoding="utf-8")
        code, out = run(mf, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb4.json"), "--out", str(t / "bp5.json")])
        code2, out2 = run(bb, ["--data", str(t / "bp5.json"), "--out", str(t / "bp5.html"), "--save-normalized", str(t / "bp6.json")])
        m6 = json.loads((t / "bp6.json").read_text(encoding="utf-8")) if code == 0 and code2 == 0 else {}
        r6 = {r.get("id"): r for r in (m6.get("risks") or {}).get("items", [])}
        check("workshop verdicts update the risk register and the PRD (kept on rebuild)", code == 0 and code2 == 0
              and (r6.get("R-UC09-1") or {}).get("score") == 15 and (r6.get("R-UC09-1") or {}).get("derived") is False
              and (r6.get("R-C05") or {}).get("resolution") == "not a risk" and (m6.get("prd") or {}).get("status") == "agreed"
              and sum(1 for r in (m6.get("risks") or {}).get("items", []) if r.get("id") == "R-UC09-1") == 1 and '"risk:R-X99"' in out, (out + out2)[-300:])

        # agent identity kit
        ai = S / "frontier-agent-identity"
        rot = load(ai / "scripts/read_office_theme.py")
        with zipfile.ZipFile(t / "deck.pptx", "w") as z:
            z.writestr("ppt/slideMasters/slideMaster1.xml", "<p:sldMaster xmlns:p='p'/>")
            z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", MASTER_RELS)
            z.writestr("ppt/theme/theme1.xml", THEME)
        code, out = run(rot, [str(t / "deck.pptx"), "--out", str(t / "brand.json"), "--customer", "Caldova Industrial AG", "--short", "Caldova", "--evidence-id", "E10"])
        brand = json.loads((t / "brand.json").read_text(encoding="utf-8")) if code == 0 else {}
        th = brand.get("theme", {})
        check("Office theme read into a brand file", code == 0 and th.get("accent1") == "#0F6CBD" and th.get("dk1") == "#111111"
              and th.get("fonts", {}).get("body") == "Aptos", out[-300:] if code else "")
        si = load(ai / "scripts/seed_identity.py")
        code, out = run(si, ["--blueprint", str(sample), "--brand", str(ai / "examples/caldova-brand.json"), "--prefix", "cal",
                             "--out-dir", str(t / "idseed"), "--date", "2026-10-30"])
        seeded = json.loads((t / "idseed/agent-identity.json").read_text(encoding="utf-8")) if code == 0 else {"agents": []}
        names_ok = all(len(f"{x['po']} {x['domain']}") <= 25 for x in seeded["agents"])
        fac_ok = all(x["kind"] == "repository-agent" for x in seeded["agents"] if x["po"] == "Factory")
        check("identity seeded from the blueprint (33 agents incl. the factory, names fit)", code == 0 and len(seeded["agents"]) == 33 and names_ok and fac_ok
              and (t / "idseed/seed-report.md").exists(), out[-300:] if code else "")
        mk = load(ai / "scripts/make_kit.py")
        code, out = run(mk, ["--config", str(ai / "examples/caldova-agent-identity.json"), "--palette", str(ai / "examples/caldova-palette.json"),
                             "--out", str(t / "kit/caldova-agent-identity"), "--no-png", "--zip", "Caldova - agent identity package v1.0"])
        summary = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        kit = t / "kit/caldova-agent-identity"
        icon_ok = (kit / "agents/service-report/identity/color-192-dev.png").exists() and (kit / "agents/service-report/identity/outline-32.png").exists()
        check("identity kit builds, validates and passes its unit tests", code == 0 and not summary.get("validation", {}).get("errors")
              and summary.get("tests") == "passed" and icon_ok and (t / "kit/Caldova - agent identity package v1.0.zip").exists(), out[-400:])
        ap_ = load(ai / "scripts/apply_identity.py")
        code, out = run(ap_, ["--blueprint", str(sample), "--kit", str(kit), "--out", str(t / "bp-id.json"), "--colours"])
        code2, out2 = run(bb, ["--data", str(t / "bp-id.json"), "--out", str(t / "bp-id.html")]) if code == 0 else (1, out)
        idhtml = (t / "bp-id.html").read_text(encoding="utf-8") if code2 == 0 else ""
        bpid = json.loads((t / "bp-id.json").read_text(encoding="utf-8")) if code == 0 else {}
        blk = bpid.get("identity") or {}
        mvp = next((a for d in bpid.get("domains", []) for a in d.get("agents", []) if a.get("id") == "D3-A05"), {}).get("identity") or {}
        page_ok = (len(blk.get("environments", [])) == 3 and len(blk.get("journeys", [])) == 5 and len(blk.get("rules", [])) >= 6
                   and blk.get("validation") == {"errors": 0, "warnings": 0} and set(mvp.get("icons", {})) == {"DEV", "TEST"}
                   and mvp.get("schema") == "cal_ServiceReport" and mvp.get("outline", "").startswith("data:image/svg+xml;base64,"))
        tpl = (S / "frontier-blueprint/templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
        check("blueprint shows the Agent identity page", code2 == 0 and page_ok and idhtml.count("data:image/svg+xml;base64,") >= 33 * 3
              and 'id:"identity", label:"Agent identity"' in tpl and "function renderIdentity" in tpl, (out + out2)[-300:])
        bwi = load(S / "frontier-blueprint/scripts/build_with_identity.py")
        code, out = run(bwi, ["--data", str(sample), "--out-dir", str(t / "onestep"), "--no-png"])
        one = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        oi = one.get("identity") or {}
        one_html = Path(one.get("html", t / "missing.html"))
        # business value and FinOps
        fdir, vdir = S / "frontier-finops", S / "frontier-value-case"
        check("shared formula module identical in both skills", (fdir / "scripts/fv_expr.py").read_bytes() == (vdir / "scripts/fv_expr.py").read_bytes())
        sys.path[:0] = [str(fdir / "scripts"), str(vdir / "scripts")]
        fc, vc = load(fdir / "scripts/finops_calc.py"), load(vdir / "scripts/value_calc.py")
        rates = json.loads((fdir / "rates/rates-2026-11.json").read_text(encoding="utf-8"))
        rv = json.loads((vdir / "examples/reference-hr-assistant.value.json").read_text(encoding="utf-8"))
        rf = json.loads((fdir / "examples/reference-hr-assistant.finops.json").read_text(encoding="utf-8"))
        rf["results"] = fc.run(rf, rv, rates, acknowledge_finops_preview=True)
        ag = rf["results"]["agents"][0]
        po = {o["option"]: o for o in rf["results"]["purchase_options"]}
        sc = [round(x["credits_month"]) for x in rf["results"]["credit_scenarios"]]
        uc = vc.run(rv, rf, acknowledge_finops_preview=True)["use_cases"][0]
        near = lambda a, b, tol: a is not None and abs(a - b) <= tol
        golden = (round(ag["credits_month"]) == 81780 and near(ag["lines"]["credits"], 662.42, 0.01) and near(ag["total_month"], 2582.42, 0.01)
                  and near(po["packs"]["annual_chf"], 7776.0, 0.01) and near(po["cc-p3"]["annual_chf"], 7827.52, 0.01) and sc == [136300, 27260, 18780, 163560]
                  and near(ag["unit"]["per_session"], 0.26, 0.005) and near(ag["unit"]["per_outcome"], 1.03, 0.005) and near(uc["npv"], 540413, 1.0)
                  and near(uc["roi"], 5.20, 0.005) and near(uc["payback_months"], 1.3, 0.05) and near((uc["break_even"] or {}).get("value"), 0.031, 0.0005))
        check("value and FinOps reproduce the method's worked example", golden,
              json.dumps({"credits": ag["credits_month"], "npv": uc["npv"], "roi": uc["roi"], "payback": uc["payback_months"], "scenarios": sc})[:300])
        bwi_vf = load(S / "frontier-blueprint/scripts/build_with_identity.py")
        refused_dir = t / "unacknowledged-preview"
        refused_code, refused_out = run(bwi_vf, [
            "--data", str(sample), "--finops", str(fdir / "examples/caldova-finops.json"),
            "--out-dir", str(refused_dir), "--no-identity",
        ])
        check("unacknowledged FinOps refuses before creating output",
              refused_code == 2 and not refused_dir.exists()
              and "--acknowledge-finops-preview" in refused_out, refused_out[-300:])
        cached = json.loads(json.dumps(rf))
        cached["maturity"] = "ga"
        cached["preview_acknowledged"] = True
        refused = False
        try:
            fc.run(cached, rv, rates)
        except ValueError as exc:
            refused = "--acknowledge-finops-preview" in str(exc)
        check("cached or forged GA cost metadata cannot acknowledge a new invocation", refused)
        code, out = run(bwi_vf, ["--data", str(sample), "--value", str(vdir / "examples/caldova-value.json"), "--finops", str(fdir / "examples/caldova-finops.json"),
                                 "--out-dir", str(t / "vfdemo"), "--no-identity", "--acknowledge-finops-preview"])
        vf = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        vf_html = Path(vf.get("html", t / "missing.html"))
        vf_text = vf_html.read_text(encoding="utf-8") if vf_html.exists() else ""
        tpl = (S / "frontier-blueprint/templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
        check("value case and FinOps model in the blueprint (Caldova demo)", code == 0 and not vf.get("notes") and (vf.get("finops") or {}).get("agents") == 2
              and not (vf.get("value") or {}).get("inputs_needed") and '"finops":{' in vf_text and '"value_case":{' in vf_text and '"business_value":{' in vf_text
              and "function renderFinops" in tpl and 'id:"finops", label:"FinOps"' in tpl, out[-400:])
        mv = load(vdir / "scripts/merge_value_feedback.py")
        (t / "merge").mkdir()
        shutil.copyfile(vdir / "examples/caldova-value.json", t / "merge/value.json")
        shutil.copyfile(fdir / "examples/caldova-finops.json", t / "merge/finops.json")
        (t / "merge/fb.json").write_text(json.dumps({"type": "frontier-blueprint-feedback", "exported": "2026-11-12T16:40:00Z", "validations": {
            "ass:ASS-003": {"status": "adjusted", "value": 12, "note": "Head of Service"}, "ass:ASS-101": {"status": "validated"}, "ass:ASS-999": {"status": "validated"},
            "uc:UC09": {"status": "validated"}}}), encoding="utf-8")
        code, out = run(mv, ["--value", str(t / "merge/value.json"), "--finops", str(t / "merge/finops.json"), "--feedback", str(t / "merge/fb.json"),
                            "--acknowledge-finops-preview"])
        mres = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        mval = json.loads((t / "merge/value.json").read_text(encoding="utf-8"))
        mfin = json.loads((t / "merge/finops.json").read_text(encoding="utf-8"))
        a3 = next(a for a in mval["assumptions"] if a["id"] == "ASS-003")
        a101 = next(a for a in mfin["assumptions"] if a["id"] == "ASS-101")
        check("workshop verdicts merge into the value case and the FinOps model", code == 0 and mres.get("changed") == 2 and mres.get("unknown") == ["ASS-999"]
              and a3["base"] == 12 and a3["status"] == "adjusted" and a101["status"] == "confirmed" and mval["version"] == "0.2" and mfin["version"] == "0.2", out[-300:])
        sv, sf = load(vdir / "scripts/seed_value.py"), load(fdir / "scripts/seed_finops.py")
        c1, o1 = run(sv, ["--blueprint", str(sample), "--out", str(t / "seed-value.json")])
        c2, o2 = run(sf, ["--blueprint", str(sample), "--value", str(t / "seed-value.json"), "--out", str(t / "seed-finops.json"),
                        "--acknowledge-finops-preview"])
        seeded_v = json.loads((t / "seed-value.json").read_text(encoding="utf-8")) if c1 == 0 else {}
        seeded_f = json.loads((t / "seed-finops.json").read_text(encoding="utf-8")) if c2 == 0 else {}
        if c1 == 0 and c2 == 0:
            seeded_f["results"] = fc.run(seeded_f, seeded_v, rates, acknowledge_finops_preview=True)
        sres = vc.run(seeded_v, seeded_f, acknowledge_finops_preview=True) if c1 == 0 and c2 == 0 else {}
        cov = {a["id"]: a["usage"]["billable_share"] for a in seeded_f.get("agents", [])}
        check("value and FinOps seeds leave volumes to collect", c1 == 0 and c2 == 0 and len(sres.get("inputs_needed", [])) == 2 and not sres.get("use_cases")
              and cov.get("D2-A01") == "1 - licensed_share" and cov.get("D3-A05") == 1, (o1 + o2)[-300:])
        check("blueprint and identity kit built in one step", code == 0 and oi.get("matched") == 33 and oi.get("tests") == "passed"
              and not (oi.get("validation") or {}).get("errors") and oi.get("seeded") is True and one_html.exists()
              and '"identity":{"kit":' in one_html.read_text(encoding="utf-8") and (one.get("blueprint") or {}).get("status") == "ok", out[-400:])

        # install simulation: build the package, extract it like Cowork does, check it, then tamper with it
        bp_ = load(ROOT / "tools/build_package.py")
        code, out = run(bp_, ["--dist", str(t / "dist")])
        pkgs = sorted((t / "dist").glob("frontier-envisioning-plugin-*.zip")) if code == 0 else []
        check("package builds", code == 0 and len(pkgs) == 1, out[-300:] if code else "")
        if pkgs:
            with zipfile.ZipFile(pkgs[0]) as z:
                z.extractall(t / "pkg")
            inst = load(t / "pkg/install/prepare_install.py")
            (t / "empty").mkdir()
            code, out = run(inst, ["--root", str(t / "pkg"), "--installed", str(t / "empty")])
            plan = json.loads(out) if code == 0 else {}
            expected = json.loads((ROOT / "plugin/package/manifest.json").read_text(encoding="utf-8"))["agentSkills"]
            installed = plan.get("skills", [])
            finops = next((x for x in installed if x.get("name") == "frontier-finops"), {})
            check("install check passes on the packaged candidate",
                  code == 0 and plan.get("verified") and len(plan.get("copy_calls", [])) == len(expected) == 8
                  and all(x["status"] == "new" for x in installed)
                  and sum(x.get("maturity") == "ga" for x in installed) == 7
                  and finops.get("maturity") == "preview" and finops.get("optional") is True
                  and finops.get("requires_preview_ack") is True
                  and "preview_acknowledged" not in plan, out[-300:] if code else "")
            check("eight installer plans are read-only",
                  not list((t / "empty").iterdir()) and len(installed) == 8)
            installed_work = t / "installed-cli"
            installed_work.mkdir()
            baseline_cli_checks(t / "pkg", installed_work, check)
            with open(t / "pkg/skills/frontier-blueprint/SKILL.md", "a", encoding="utf-8") as fh:
                fh.write("\n<!-- altered -->\n")
            code, out = run(inst, ["--root", str(t / "pkg"), "--installed", str(t / "empty")])
            check("install check refuses an altered package", code == 1 and '"verified": false' in out)
            installed_core_check(t / "pkg", installed_work, check)

    for status, name, detail in results:
        print(f"{status}  {name}" + (f"  ({detail})" if detail and status == "FAIL" else ""))
    print("ALL PASSED" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
