# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Financial verification is explicit, current, authoritative and non-mutating."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tests.factory_fixture import F, approved, encode, prepare, save
from tests.unit.test_factory_privacy import projection
from tests.unit.test_factory_export import add_history, exporter, invoke
from tests.unit.test_finops_baseline import DAY, example


def provide(fixture, name, raw, *, role="finops", artifact_id="finops", replace=True):
    request = fixture["request"]
    row = next(row for row in request["intake"]["artifacts"] if row["role"] == role)
    if not replace:
        row = copy.deepcopy(row)
        request["intake"]["artifacts"].append(row)
    path = "docs/intake/records/caldova-intake/artifacts/" + name
    row.update(id=artifact_id, status="provided", rationale="Synthetic explicit financial review.",
               source={"path": name, "reference": "synthetic-financial", "version": "v1",
                       "modified_at": "unknown"}, baseline={"path": path},
               transformation={"kind": "none", "rationale": "Exact approved synthetic bytes.",
                               "approval": None})
    (fixture["source"] / name).write_bytes(raw)
    (fixture["baseline"] / path).write_bytes(raw)
    request["sharing_review"]["artifacts"]["caldova-intake:" + artifact_id] = approved()
    return "caldova-intake:" + artifact_id


def financial_packet(p, fixture, *, planning=False):
    """Actual frozen/reviewed helper fixture; all assertions remain synthetic."""
    source = fixture["source"]
    if planning:
        from tests.unit.test_finops_baseline_io import simulated
        authored = simulated()
    else:
        authored = example()
    with p.sibling("frontier-finops", "baseline_calc") as calc:
        model = calc.calculate(authored, as_of=DAY, acknowledge_finops_preview=True)
    with p.sibling("frontier-finops", "baseline_records") as records:
        frozen = records.freeze(model, source / "private-staging-name/frozen", as_of=DAY,
                                acknowledge_finops_preview=True)
        snapshot = json.loads(frozen.read_bytes())
        review = {
            "id": "SYNTHETIC-REVIEW", "decision": "approve",
            "actor": snapshot["model"]["profile"]["owners"]["finance"],
            "finance_owner": snapshot["model"]["profile"]["owners"]["finance"],
            "date": DAY.isoformat(), "evidence_ref": "test:synthetic-only",
            **snapshot["target"], "mode": snapshot["model"]["mode"],
            "sharingClassification": "customer-shareable", "synthetic": not planning,
        }
        reviewed = records.record_review(snapshot, review, source / "private-staging-name/reviews",
                                         as_of=DAY, acknowledge_finops_preview=True)
    with p.sibling("frontier-finops", "baseline_projection") as projector:
        report = projector.project(snapshot, [json.loads(reviewed.read_bytes())], as_of=DAY,
                                   audience="customer", customer_scope=fixture["request"]["customer_scope"],
                                   acknowledge_finops_preview=True)
        markdown = projector.render_markdown(report).encode("utf-8")
    first = provide(fixture, "financial.json", encode(report))
    second = provide(fixture, "financial.md", markdown, artifact_id="financial-markdown", replace=False)
    fixture["request"]["financial"] = {
        "requested": True, "as_of": DAY.isoformat(), "claim": "review",
        "packets": [{"artifact_ids": [first, second], "kind": "baseline",
                     "model_path": frozen.relative_to(source).as_posix(),
                     "review_paths": [reviewed.relative_to(source).as_posix()], "owner_review": approved()}],
    }
    save(fixture)
    return frozen, reviewed, report


def legacy_documents(p):
    """Actual bundled examples and native receipts, including JSON round trips."""
    fin = json.loads((F.parent / "frontier-finops/examples/caldova-finops.json").read_bytes())
    value = json.loads((F.parent / "frontier-value-case/examples/caldova-value.json").read_bytes())
    rates = json.loads((F.parent / "frontier-finops/rates/rates-2026-11.json").read_bytes())
    with p.sibling("frontier-finops", "finops_calc") as calculator:
        fin["results"] = calculator.run(fin, value, rates, acknowledge_finops_preview=True)
    fin = json.loads(encode(fin))
    with p.sibling("frontier-finops", "finops_preview") as owner:
        owner.validate_finops_results(fin, value=value, rates=rates, acknowledge_finops_preview=True)
    with p.sibling("frontier-value-case", "value_calc") as owner:
        value["results"] = owner.run(value, fin, acknowledge_finops_preview=True)
    value = json.loads(encode(value))
    with p.sibling("frontier-value-case", "value_calc") as owner:
        owner.preview_for(value, operation="apply-value", acknowledge_finops_preview=True)
    return fin, value


class Financial(unittest.TestCase):
    def setUp(self):
        self.p = projection(self)
        self.assertTrue(callable(getattr(self.p, "financial_check", None)),
                        "W3 current-invocation financial verification has not been implemented")
        self.m = exporter(self)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.f = prepare(Path(self.tmp.name) / "case")

    def check(self, acknowledged=False):
        intake, files, _ = self.m.contract.materialize(self.f["request"]["intake"], self.f["baseline"],
                                                      self.f["source"], self.m.common.read)
        return self.p.financial_check(self.f["request"], [intake], files, self.f["source"], acknowledged)

    def reviewed_document(self, document, *, role="finops"):
        # Native examples cite E05/E06 from the bundled authored Blueprint.
        # Supply those actual customer-visible records, not invented clearance
        # or a production exception for unresolved references.
        path = self.f["source"] / "blueprint.json"
        blueprint = json.loads(path.read_bytes())
        native = json.loads((F.parent / "frontier-blueprint/examples/caldova-blueprint.json").read_bytes())
        known = {row["id"] for row in blueprint["evidence"]}
        for row in native["evidence"]:
            if row["id"] in {"E05", "E06"} and row["id"] not in known:
                self.assertEqual(row["visibility"], "customer")
                blueprint["evidence"].append(copy.deepcopy(row))
        with self.p.sibling("frontier-blueprint", "build_blueprint") as owner:
            report = owner.Report()
            customer = owner.customer_version(blueprint, report)
            self.assertEqual(report.errors, [])
        path.write_bytes(encode(blueprint))
        (self.f["baseline"] / self.f["request"]["blueprint"]["baseline_path"]).write_bytes(encode(customer))
        raw = encode(document)
        qualified = provide(self.f, "reviewed.json", raw, role=role, artifact_id="reviewed-financial")
        self.f["request"]["financial"] = {
            "requested": True, "as_of": DAY.isoformat(), "claim": "review",
            "packets": [{"artifact_ids": [qualified], "kind": "reviewed-document",
                         "model_path": None, "review_paths": [], "owner_review": approved()}],
        }
        save(self.f)
        return raw

    def financial_refusal(self):
        self.f["out"].write_bytes(b"old-good")
        run = invoke(self.f, "--acknowledge-finops-preview")
        self.assertEqual(run.returncode, 1, (run.stdout, run.stderr))
        self.assertTrue(run.stdout.strip(), "Expected a safe financial error JSON, not an empty traceback failure")
        self.assertTrue(json.loads(run.stdout)["error"].startswith("FACTORY_FINANCIAL"))
        self.assertEqual(run.stderr, "")
        self.assertNotIn("12345", run.stdout)
        self.assertEqual(self.f["out"].read_bytes(), b"old-good")
        self.assertEqual(list(self.f["out"].parent.glob(".factory-*.tmp")), [])

    def test_nested_value_payload_requires_its_own_receipt(self):
        malformed = {"schema": "frontier-value/1.0", "agents_costed": ["D1-A01"],
                     "results": {"totals": {"cost": 12345}}}
        for nested in (False, True):
            with self.subTest(nested=nested):
                self.reviewed_document({"nested": malformed} if nested else malformed, role="value")
                self.financial_refusal()

    def result_local_value_cases(self):
        for schema in (None, "caldova-value-review/1.0", "frontier-value/1.0"):
            document = {"results": {"finops_preview": {}, "agents_costed": ["D1-A01"],
                                   "use_cases": [], "totals": {"cost": 12345}, "inputs_needed": []}}
            if schema is not None:
                document["schema"] = schema
            for wrapper in ("root", "nested", "results-wrapper"):
                candidate = (document if wrapper == "root" else {"nested": document}
                             if wrapper == "nested" else {"results": {"nested": document}})
                yield schema, wrapper, candidate

    def test_result_local_financial_markers_require_value_receipt(self):
        for schema, wrapper, document in self.result_local_value_cases():
            with self.subTest(schema=schema, wrapper=wrapper):
                payload = document
                if wrapper == "nested":
                    payload = document["nested"]
                elif wrapper == "results-wrapper":
                    payload = document["results"]["nested"]
                with self.p.sibling("frontier-value-case", "value_calc") as owner:
                    self.assertTrue(owner.has_finops_dependency(payload))
                    with self.assertRaises(ValueError):
                        owner.preview_for(payload, operation="apply-value", acknowledge_finops_preview=True)
                self.reviewed_document(document, role="value")
                with self.assertRaisesRegex(self.m.common.FactoryError, "^FACTORY_FINANCIAL$"):
                    self.check(True)

    def test_cli_result_local_financial_markers_require_value_receipt(self):
        for schema, wrapper, document in self.result_local_value_cases():
            with self.subTest(schema=schema, wrapper=wrapper):
                self.reviewed_document(document, role="value")
                self.financial_refusal()

    def test_result_local_owner_dispatch_preserves_native_wrappers(self):
        fin, value = legacy_documents(self.p)
        fin["finops_preview"] = copy.deepcopy(fin["results"]["finops_preview"])
        value["finops_preview"] = copy.deepcopy(value["results"]["finops_preview"])
        for name, document in (
                ("value-root", value), ("value-nested", {"nested": value}),
                ("deep-results-wrapper", {"results": {"nested": value}}),
                ("direct-value-wrapper", {"results": value}),
                ("direct-finops-wrapper", {"results": fin})):
            with self.subTest(context=name):
                self.reviewed_document(document, role="value")
                run = invoke(self.f, "--acknowledge-finops-preview")
                self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
                self.assertEqual(json.loads(run.stdout)["financial_status"],
                                 "reviewed-documents-not-financially-ready")

    def test_native_legacy_finops_roundtrip_exports_review_only(self):
        import zipfile
        fin, _ = legacy_documents(self.p)
        raw = self.reviewed_document(fin)
        run = invoke(self.f, "--acknowledge-finops-preview")
        self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
        self.assertEqual(json.loads(run.stdout)["financial_status"], "reviewed-documents-not-financially-ready")
        with zipfile.ZipFile(self.f["out"]) as archive:
            self.assertEqual(archive.read("docs/intake/records/caldova-intake/artifacts/reviewed.json"), raw)
        self.f["request"]["financial"]["claim"] = "build-handover"
        save(self.f)
        self.financial_refusal()

    def test_native_nested_value_payload_uses_value_owner(self):
        fin, value = legacy_documents(self.p)
        # Native model-level metadata may repeat its already validated result receipt.
        fin["finops_preview"] = copy.deepcopy(fin["results"]["finops_preview"])
        self.reviewed_document({"cost_source": fin, "nested": [value]}, role="value")
        run = invoke(self.f, "--acknowledge-finops-preview")
        self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
        self.assertEqual(json.loads(run.stdout)["financial_status"], "reviewed-documents-not-financially-ready")

    def test_native_provenance_descriptors_cannot_hide_financial_payloads(self):
        fin, value = legacy_documents(self.p)
        descriptor = fin["results"]["finops_preview"]["provenance"]["inputs"]["finops"]
        value_descriptor = value["results"]["finops_preview"]["provenance"]["inputs"]["value"]
        for document in (descriptor, {"nested": descriptor},
                         value_descriptor, {"nested": value_descriptor},
                         {"finops_preview": {"provenance": {"inputs": {"finops": descriptor}}}},
                         {"schema": "frontier-agent-finops-report/1.0"}):
            with self.subTest(context=list(document)):
                self.reviewed_document(document)
                self.financial_refusal()
        for location in ("extra-key", "native-agents-slot"):
            altered = copy.deepcopy(fin)
            metadata = altered["results"]["finops_preview"]
            payload = {"schema": "frontier-value/1.0", "agents_costed": ["D1-A01"],
                       "results": {"totals": {"cost": 12345}}}
            target = metadata["provenance"]["inputs"]["finops"]
            if location == "extra-key":
                target["unowned_payload"] = payload
            else:
                target.setdefault("agents", []).append(payload)
            metadata["calculations"]["finops"]["inputs"]["finops"] = copy.deepcopy(target)
            # The owner validates its projected lineage. Extra nested payloads
            # still need their own owner validation; the outer receipt is not proof.
            with self.p.sibling("frontier-finops", "finops_preview") as owner:
                owner.validate_finops_results(altered, acknowledge_finops_preview=True)
            with self.subTest(location=location):
                self.reviewed_document(altered)
                self.financial_refusal()

    def test_malformed_native_finops_identities_are_safe_input_errors(self):
        fin, _ = legacy_documents(self.p)
        for location in ("model-agent", "result-agent", "missing-agent"):
            altered = copy.deepcopy(fin)
            if location == "model-agent":
                altered["agents"][0]["id"] = ["malformed"]
            elif location == "result-agent":
                altered["results"]["agents"][0]["id"] = ["malformed"]
            else:
                altered["results"]["missing"] = [{"agent": ["malformed"], "assumptions": ["declared"]}]
            with self.subTest(location=location):
                self.reviewed_document(altered)
                self.financial_refusal()

    def test_core_does_not_import_or_run_finops_even_if_acknowledged(self):
        original = self.p.sibling
        def guarded(skill, module):
            self.assertNotEqual(skill, "frontier-finops", "Ordinary core imported optional FinOps")
            return original(skill, module)
        with mock.patch.object(self.p, "sibling", side_effect=guarded):
            self.assertEqual(self.check(), "not-requested")
            self.assertEqual(self.check(True), "not-requested")

    def test_unrequested_build_handover_cannot_bypass_strict_readiness(self):
        self.f["request"]["financial"]["claim"] = "build-handover"
        original = self.p.sibling
        def guarded(skill, module):
            self.assertNotEqual(skill, "frontier-finops", "Unrequested content imported optional FinOps")
            return original(skill, module)
        with mock.patch.object(self.p, "sibling", side_effect=guarded):
            for acknowledged in (False, True):
                with self.subTest(acknowledged=acknowledged), self.assertRaisesRegex(
                        self.m.common.FactoryError, "^FACTORY_FINANCIAL_READY$"):
                    self.check(acknowledged)

    def test_cli_unrequested_build_handover_without_ack_preserves_old_good(self):
        self.f["request"]["financial"]["claim"] = "build-handover"
        save(self.f)
        self.f["out"].write_bytes(b"old-good")
        inputs = {path: path.read_bytes() for root in (self.f["source"], self.f["baseline"])
                  for path in root.rglob("*") if path.is_file()}
        run = invoke(self.f)
        self.assertEqual(run.returncode, 1, (run.stdout, run.stderr))
        self.assertEqual(json.loads(run.stdout)["error"], "FACTORY_FINANCIAL_READY")
        self.assertEqual(len(run.stdout.splitlines()), 1)
        self.assertEqual(run.stderr, "")
        self.assertEqual(self.f["out"].read_bytes(), b"old-good")
        self.assertEqual(list(self.f["out"].parent.glob(".factory-*.tmp")), [])
        self.assertTrue(all(path.read_bytes() == raw for path, raw in inputs.items()))

    def test_role_schema_and_nested_markers_require_request_and_current_ack(self):
        cases = [
            ("finops", b"%PDF-1.7 opaque financial review", "costs.pdf"),
            ("value", encode({"schema": "frontier-finops/1.0"}), "costs.json"),
            ("value", encode({"schema": "frontier-finops-baseline/1.0"}), "costs.json"),
            ("value", encode({"nested": {"schema": "frontier-agent-finops-report/1.0"}}), "costs.json"),
            ("value", encode({"nested": {"agents_costed": ["D1-A01"]}}), "costs.json"),
        ]
        for index, (role, raw, name) in enumerate(cases):
            self.f = prepare(Path(self.tmp.name) / f"case-{index}")
            provide(self.f, name, raw, role=role, artifact_id="costs")
            save(self.f)
            with self.subTest(role=role, name=name), self.assertRaisesRegex(
                    self.m.common.FactoryError, "FACTORY_FINANCIAL_ACK"):
                self.check()
            self.f["request"]["financial"].update(requested=True, as_of=DAY.isoformat())
            with self.assertRaisesRegex(self.m.common.FactoryError, "FACTORY_FINANCIAL_ACK"):
                self.check()

    def test_actual_frozen_projection_and_markdown_exact_preserve_authority(self):
        frozen, reviewed, _ = financial_packet(self.p, self.f)
        before = frozen.read_bytes(), reviewed.read_bytes()
        self.assertEqual(self.check(True), "review-with-financial-gaps")
        run = invoke(self.f, "--acknowledge-finops-preview")
        self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
        self.assertEqual(json.loads(run.stdout)["financial_status"], "review-with-financial-gaps")
        self.assertEqual((frozen.read_bytes(), reviewed.read_bytes()), before)
        without = invoke(self.f)
        self.assertEqual(without.returncode, 1)
        self.assertEqual(json.loads(without.stdout)["error"], "FACTORY_FINANCIAL_ACK")
        self.assertNotIn("1320", without.stdout + without.stderr)

    def test_private_internal_authority_basename_not_exported_or_transfer_required(self):
        financial_packet(self.p, self.f)
        path = self.f["source"] / "blueprint.json"
        blueprint = json.loads(path.read_bytes())
        blueprint["meta"]["internal_terms"] = ["private-staging-name"]
        path.write_bytes(encode(blueprint))
        save(self.f)
        run = invoke(self.f, "--acknowledge-finops-preview")
        self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
        import zipfile
        with zipfile.ZipFile(self.f["out"]) as archive:
            for name in archive.namelist():
                self.assertNotIn(b"private-staging-name", archive.read(name))
                self.assertNotIn("private-staging-name", name)

    def test_derivatives_cannot_bypass_authority_with_packet_kind_or_role(self):
        financial_packet(self.p, self.f)
        packet = self.f["request"]["financial"]["packets"][0]
        packet.update(kind="reviewed-document", model_path=None, review_paths=[])
        with self.assertRaisesRegex(self.m.common.FactoryError, "FACTORY_FINANCIAL"):
            self.check(True)

    def test_baseline_requires_snapshot_actual_projection_scope_date_and_owner(self):
        frozen, _, _ = financial_packet(self.p, self.f)
        packet = self.f["request"]["financial"]["packets"][0]
        for mutation in ("digest", "date", "owner", "projection"):
            f = copy.deepcopy(self.f["request"])
            before = frozen.read_bytes()
            report_path = self.f["baseline"] / "docs/intake/records/caldova-intake/artifacts/financial.json"
            original = report_path.read_bytes()
            if mutation == "digest":
                model = json.loads(before)
                model["target"]["material_hash"] = "0" * 64
                frozen.write_bytes(encode(model))
            elif mutation == "date":
                self.f["request"]["financial"]["as_of"] = "2026-02-29"
            elif mutation == "owner":
                packet["owner_review"] = {}
            else:
                report = json.loads(original)
                report["as_of"] = "2025-01-01"
                report_path.write_bytes(encode(report))
            with self.subTest(mutation=mutation), self.assertRaises(self.m.common.FactoryError):
                self.check(True)
            self.f["request"] = f
            packet = f["financial"]["packets"][0]
            frozen.write_bytes(before)
            report_path.write_bytes(original)

    def test_explicit_build_handover_claim_does_not_promote_synthetic_review(self):
        financial_packet(self.p, self.f)
        self.f["request"]["financial"]["claim"] = "build-handover"
        with self.assertRaisesRegex(self.m.common.FactoryError, "FACTORY_FINANCIAL_READY"):
            self.check(True)

    def test_reviewed_opaque_packet_has_limits_never_financial_readiness(self):
        qualified = provide(self.f, "costs.pdf", b"%PDF-1.7\nsynthetic reviewed document")
        self.f["request"]["financial"] = {
            "requested": True, "as_of": DAY.isoformat(), "claim": "review",
            "packets": [{"artifact_ids": [qualified], "kind": "reviewed-document",
                         "model_path": None, "review_paths": [], "owner_review": approved()}],
        }
        self.assertEqual(self.check(True), "reviewed-documents-not-financially-ready")
        self.f["request"]["financial"]["claim"] = "build-handover"
        with self.assertRaises(self.m.common.FactoryError):
            self.check(True)

    def test_coverage_unknown_overlap_and_legacy_results_are_validated(self):
        financial_packet(self.p, self.f)
        request = copy.deepcopy(self.f["request"])
        for kind in ("missing", "overlap", "unknown"):
            self.f["request"] = copy.deepcopy(request)
            packets = self.f["request"]["financial"]["packets"]
            if kind == "missing":
                packets[0]["artifact_ids"].pop()
            elif kind == "overlap":
                packets.append(copy.deepcopy(packets[0]))
            else:
                packets[0]["artifact_ids"].append("caldova-intake:not-provided")
            with self.subTest(kind=kind), self.assertRaises(self.m.common.FactoryError):
                self.check(True)
        self.f = prepare(Path(self.tmp.name) / "legacy")
        qualified = provide(self.f, "legacy.json", encode({"schema": "frontier-finops/1.0",
                                                         "results": {"agents": []}}))
        self.f["request"]["financial"] = {
            "requested": True, "as_of": DAY.isoformat(), "claim": "review",
            "packets": [{"artifact_ids": [qualified], "kind": "reviewed-document",
                         "model_path": None, "review_paths": [], "owner_review": approved()}]}
        with self.assertRaisesRegex(self.m.common.FactoryError, "FACTORY_FINANCIAL"):
            self.check(True)

    def test_historical_financial_material_not_ignored(self):
        financial_packet(self.p, self.f)
        add_history(self.f, self.m.contract, self.m.common)
        # Current ordinary files do not remove the need to cover historical cost files.
        request = self.f["request"]
        request["financial"].update(requested=False, packets=[], as_of=None)
        save(self.f)
        run = invoke(self.f)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)["error"], "FACTORY_FINANCIAL_ACK")

    def test_financial_model_hardlink_cannot_be_output(self):
        frozen, reviewed, _ = financial_packet(self.p, self.f)
        import os
        output = Path(self.tmp.name) / "alias.zip"
        for path in (frozen, reviewed):
            os.link(path, output)
            before = path.read_bytes()
            self.f["out"] = output
            run = invoke(self.f, "--acknowledge-finops-preview")
            with self.subTest(kind=path.parent.name):
                self.assertEqual(run.returncode, 1)
                self.assertEqual(path.read_bytes(), before)
            output.unlink()

    def test_existing_strict_ready_gate_only_planning_not_financial_permission(self):
        _, _, report = financial_packet(self.p, self.f, planning=True)
        self.assertTrue(report["handover"]["ready"], "Existing helper fixture must actually satisfy its gate")
        self.assertFalse(report["financial_permission"])
        self.f["request"]["financial"]["claim"] = "build-handover"
        self.assertEqual(self.check(True), "planning-ready-not-financial-permission")
        save(self.f)
        run = invoke(self.f, "--acknowledge-finops-preview")
        self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
        self.assertEqual(json.loads(run.stdout)["financial_status"], "planning-ready-not-financial-permission")
