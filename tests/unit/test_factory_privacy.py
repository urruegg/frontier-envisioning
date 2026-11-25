# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Passive projections use actual bundled privacy contracts, not consent guesses."""
import copy
import importlib
import json
import sys
import tempfile
import unittest
from unittest import mock

from tests.factory_fixture import F, approved, encode, prepare


def projection(test):
    test.assertTrue((F / "scripts/factory_projection.py").is_file(),
                    "W3 passive projection behaviour has not been implemented")
    with mock.patch.object(sys, "path", [str(F / "scripts"), *sys.path]):
        return importlib.import_module("factory_projection")


class Privacy(unittest.TestCase):
    def setUp(self):
        self.p = projection(self)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.f = prepare(self.tmp.name)
        self.r = self.f["request"]
        with mock.patch.object(sys, "path", [str(F / "scripts"), *sys.path]):
            self.c = importlib.import_module("factory_common")
            self.contract = importlib.import_module("factory_contract")
        self.intake, self.files, self.originals = self.contract.materialize(
            self.r["intake"], self.f["baseline"], self.f["source"], self.c.read)

    def blueprint(self):
        return self.p.check_blueprint(self.r, self.files, self.originals)

    def sharing(self, original=None):
        self.p.check_sharing(self.r, [self.intake], self.files,
                             self.blueprint()[0] if original is None else original)

    def test_exact_customer_projection_and_explicit_selection(self):
        before = copy.deepcopy(self.r)
        original, customer = self.blueprint()
        self.assertNotEqual(original, customer)
        self.assertEqual(self.p.check_selection(self.r, customer, self.intake), None)
        self.sharing(original)
        self.assertEqual(self.r, before)

    def test_approved_projection_cannot_be_substituted_or_rewritten(self):
        path = self.r["blueprint"]["baseline_path"]
        customer = json.loads(self.files[path])
        customer["domains"][0]["name"] = "Unreviewed replacement"
        self.files[path] = encode(customer)
        with self.assertRaisesRegex(self.c.FactoryError, "FACTORY_BLUEPRINT"):
            self.blueprint()

    def test_shape_guard_precedes_helper_and_programmer_errors_propagate(self):
        with self.assertRaises(self.c.FactoryError):
            self.p.blueprint_shape({"meta": [], "domains": [1], "evidence": ["x"]})
        for error in (KeyError("bug"), TypeError("bug"), AttributeError("bug")):
            with self.subTest(kind=type(error)), self.assertRaises(type(error)):
                with self.p.validation_input("FACTORY_BLUEPRINT"):
                    raise error
        with self.assertRaisesRegex(self.c.FactoryError, "^FACTORY_BLUEPRINT$"):
            with self.p.validation_input("FACTORY_BLUEPRINT"):
                raise ValueError("private diagnostic must not survive")

    def test_selection_rejects_private_removed_agent_and_unselected_requirements(self):
        _, customer = self.blueprint()
        for field, mapping in (("agents", {"removed-private-agent": "service-agent"}),
                               ("requirements", {"FR-001": "not-selected"})):
            request = copy.deepcopy(self.r)
            request["id_map"][field] = mapping
            with self.subTest(field=field), self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SELECTION"):
                self.p.check_selection(request, customer, self.intake)

    def test_selection_dependency_gaps_must_resolve_without_widening(self):
        _, customer = self.blueprint()
        self.r["selection_evidence"][0]["dependency_gaps"] = ["not-declared"]
        with self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SELECTION"):
            self.p.check_selection(self.r, customer, self.intake)
        self.r["selection_evidence"][0]["dependency_gaps"] = ["implementation-gap"]
        self.p.check_selection(self.r, customer, self.intake)
        self.assertEqual(len(self.intake["selected_solutions"]), 1)

    def test_ordinary_formats_check_actual_bytes_and_strict_json(self):
        for name, raw in (("x.html", b"<html>"), ("x.zip", b"PK"),
                          ("x.ttl", b"@prefix"), ("x.md", b"PK\x03\x04fake"),
                          ("x.txt", b"%PDF-1.7"), ("x.csv", b"<html>secret"),
                          ("x.md", b"\xff"), ("x.txt", b"a\x00b"),
                          ("x.json", b'{"a":1,"a":2}'), ("x.json", b'{"n":NaN}')):
            with self.subTest(name=name, raw=raw[:12]), self.assertRaises(self.c.FactoryError):
                self.p.check_ordinary(name, raw)
        for name, raw in (("x.md", "Caldova café\r\n".encode()),
                          ("x.json", b'{"reviewed":true}'), ("x.pdf", b"%PDF-1.7\nopaque"),
                          ("x.docx", b"PK\x03\x04opaque-reviewed")):
            self.p.check_ordinary(name, raw)

    def test_every_provided_file_needs_qualified_actual_sharing_review(self):
        del self.r["sharing_review"]["artifacts"]["caldova-intake:prd"]
        with self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SHARING"):
            self.sharing()
        self.r["sharing_review"]["artifacts"]["caldova-intake:prd"] = approved()
        self.intake["transfer"]["classification"] = "restricted"
        with self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SHARING"):
            self.sharing()

    def test_whole_original_private_terms_cannot_leak_through_export_metadata(self):
        original, _ = self.blueprint()
        original["meta"]["internal_terms"] = ["private-fixture-token"]
        self.intake["source"]["references"] = ["private-fixture-token"]
        with self.assertRaisesRegex(self.c.FactoryError, "^FACTORY_SHARING$"):
            self.sharing(original)

    def test_structured_json_flags_and_ancestry_checked_current_and_history(self):
        original, _ = self.blueprint()
        cases = [
            {"internal": True, "note": "private-fixture-token"},
            {"visibility": "internal", "note": "private-fixture-token"},
            {"ancestry_status": "unresolved", "note": "private-fixture-token"},
            {"content_src": ["SYN-INT"], "src": ["PUBLIC"], "note": "private-fixture-token"},
            {"sharingClassification": "validation-required"},
            {"sharingClassification": "customer-specific", "customer_scope": "wrong-scope"},
            {"content_origins": [{"internal": True}], "note": "promoted"},
        ]
        path = next(row["baseline"]["path"] for row in self.intake["artifacts"] if row["id"] == "prd")
        for historic in (False, True):
            for content in cases:
                record = copy.deepcopy(self.intake)
                files = dict(self.files)
                row = next(row for row in record["artifacts"] if row["id"] == "prd")
                row["baseline"]["path"] = path[:-3] + ".json"
                files[row["baseline"]["path"]] = encode({"nested": content})
                request = copy.deepcopy(self.r)
                if historic:
                    record["intake_id"] = "prior-intake"
                    request["sharing_review"]["artifacts"].update({
                        "prior-intake:" + r["id"]: approved()
                        for r in record["artifacts"] if r["status"] == "provided"})
                with self.subTest(historic=historic, flags=list(content)), self.assertRaisesRegex(
                        self.c.FactoryError, "^FACTORY_SHARING$"):
                    self.p.check_sharing(request, [record], files, original)

    def test_private_root_is_not_laundered_by_projection(self):
        original, _ = self.blueprint()
        original["internal"] = True
        with self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SHARING"):
            self.sharing(original)

    def test_internal_notes_and_escaped_known_tokens_are_not_opaque_json(self):
        original, _ = self.blueprint()
        original["meta"]["internal_terms"] = ["private-fixture-token\nline"]
        row = next(row for row in self.intake["artifacts"] if row["id"] == "prd")
        name = row["baseline"]["path"][:-3] + ".json"
        row["baseline"]["path"] = name
        for document in ({"internal_notes": "private text"},
                         {"ordinary": "private-fixture-token\nline"}):
            files = dict(self.files, **{name: encode(document)})
            with self.subTest(keys=list(document)), self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SHARING"):
                self.p.check_sharing(self.r, [self.intake], files, original)

    def test_arbitrary_json_evidence_scalar_does_not_become_programmer_error(self):
        row = next(row for row in self.intake["artifacts"] if row["id"] == "prd")
        name = row["baseline"]["path"][:-3] + ".json"
        row["baseline"]["path"] = name
        files = dict(self.files, **{name: encode({"evidence": 1, "reviewed": True})})
        self.p.check_sharing(self.r, [self.intake], files, self.blueprint()[0])

    def test_unknown_and_mixed_private_references_are_refused(self):
        original, _ = self.blueprint()
        original["evidence"].append({"id": "PUBLIC", "visibility": "customer"})
        row = next(row for row in self.intake["artifacts"] if row["id"] == "prd")
        name = row["baseline"]["path"][:-3] + ".json"
        row["baseline"]["path"] = name
        for refs in (["SYN-INT", "PUBLIC"], ["NO-SUCH-SOURCE"]):
            files = dict(self.files, **{name: encode({"content_src": refs})})
            with self.subTest(refs=refs), self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SHARING"):
                self.p.check_sharing(self.r, [self.intake], files, original)

    def test_unselected_mvp_agent_never_auto_widens_scope(self):
        _, customer = self.blueprint()
        customer["domains"][0]["agents"].append({"id": "D1-A99", "name": "Unselected", "mvp": True})
        self.p.check_selection(self.r, customer, self.intake)
        self.assertEqual(self.r["id_map"]["agents"], {"D1-A01": "service-agent"})

    def test_schema_owned_process_unknown_dependencies_cannot_be_opaque_json(self):
        row = next(row for row in self.intake["artifacts"] if row["id"] == "prd")
        name = row["baseline"]["path"][:-3] + ".json"
        row["baseline"]["path"] = name
        document = {"schema": "frontier-ontology/1.0", "sources": [],
                    "entity_types": [{"id": "E1", "source": "NO-SUCH-SOURCE", "properties": []}]}
        files = dict(self.files, **{name: encode(document)})
        with self.assertRaisesRegex(self.c.FactoryError, "FACTORY_SHARING"):
            self.p.check_sharing(self.r, [self.intake], files, self.blueprint()[0])

    def test_actual_cli_rejects_current_and_history_private_json_without_leaking(self):
        from tests.factory_fixture import save
        from tests.unit.test_factory_export import add_history, exporter, invoke
        module = exporter(self)
        for historic in (False, True):
            with tempfile.TemporaryDirectory() as folder:
                fixture = prepare(folder)
                if historic:
                    record, _ = add_history(fixture, module.contract, module.common)
                else:
                    record = fixture["request"]["intake"]
                row = next(row for row in record["artifacts"] if row["id"] == "prd")
                name = row["baseline"]["path"][:-3] + ".json"
                raw = encode({"nested": {"internal": True, "name": "private-fixture-token"}})
                row["baseline"]["path"] = name
                (fixture["baseline"] / name).write_bytes(raw)
                if historic:
                    row["baseline"]["sha256"] = module.common.digest(raw)
                    row["source"]["sha256"] = module.common.digest(raw)
                    path = fixture["baseline"] / "docs/intake/records/previous-intake/intake.json"
                    path.write_bytes(encode(record))
                else:
                    row["source"]["path"] = "prd.json"
                    (fixture["source"] / "prd.json").write_bytes(raw)
                save(fixture)
                fixture["out"].write_bytes(b"old-good")
                run = invoke(fixture)
                with self.subTest(historic=historic):
                    self.assertEqual(run.returncode, 1)
                    self.assertEqual(json.loads(run.stdout)["error"], "FACTORY_SHARING")
                    self.assertNotIn("private-fixture-token", run.stdout + run.stderr)
                    self.assertEqual(fixture["out"].read_bytes(), b"old-good")

    def test_internal_financial_paths_are_not_export_metadata(self):
        original, _ = self.blueprint()
        original["meta"]["internal_terms"] = ["private-staging-name"]
        self.r["financial"]["packets"] = [{
            "artifact_ids": [], "kind": "baseline", "model_path": "private-staging-name/model.json",
            "review_paths": ["private-staging-name/review.json"], "owner_review": approved(),
        }]
        self.sharing(original)
        metadata = self.p.export_metadata(self.r, self.intake, "1.11.0", "not-requested")
        self.assertNotIn("private-staging-name", json.dumps(metadata))

    def test_sibling_loading_restores_paths_and_does_not_trust_cached_module(self):
        prior = sys.path[:]
        fake = mock.Mock()
        with mock.patch.dict(sys.modules, {"canon": fake, "build_blueprint": fake}):
            with self.p.sibling("frontier-blueprint", "build_blueprint") as module:
                self.assertEqual(module.PLUGIN_VERSION, "1.11.0")
                self.assertIsNot(module, fake)
            self.assertIs(sys.modules["canon"], fake)
        self.assertEqual(sys.path, prior)
