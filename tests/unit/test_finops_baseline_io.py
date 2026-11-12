"""Task3 lifecycle, dependency projection and real temporary-folder CLI tests.

All verification/review claims below are simulated in-memory test assertions,
NOT real commercial evidence, finance decisions or customer data.
"""
from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

from tests.unit.test_finops_baseline import DAY, FIN, baseline_module, example

ACK = {"as_of": DAY, "acknowledge_finops_preview": True}
ROOT = FIN.parents[2]
CLI = FIN / "scripts" / "agent_finops.py"
BP = ROOT / "plugin/skills/frontier-blueprint/examples/caldova-blueprint.json"


def blueprint():
    return json.loads(BP.read_text(encoding="utf-8"))


def seed_blueprint():
    """Simulated shareable control; avoid unrelated stock internal evidence taint."""
    bp = blueprint()
    bp.update(customer_scope="caldova-scope", sharingClassification="customer-shareable")
    for source in bp["evidence"]:
        source.update(internal=False, visibility="customer", sharingClassification="customer-specific",
                      customer_scope="caldova-scope")
    return bp


def simulated():
    """Fully evidenced ONLY within this test; never a persisted commercial claim."""
    model = example()
    model["mode"] = "planning"
    for source in model["sources"]:
        source.update(type="customer-evidence", validationStatus="validated")
    for rate in model["rates"]:
        rate["verification"]["status"] = "verified"
    return model


def nullable_model(kind):
    """Contract-accepted incomplete inputs; remove incompatible dangling refs."""
    model = example()
    if kind == "sources":
        model["sources"] = None

        def clear_refs(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"source_id", "src", "content_src"}:
                        value[key] = None
                    else:
                        clear_refs(child)
            elif isinstance(value, list):
                for child in value:
                    clear_refs(child)
        clear_refs(model)
    elif kind in {"scenarios", "lines"}:
        model["baseline"][kind] = None
        if kind == "scenarios":
            model["baseline"]["lines"] = None
    elif kind == "rates":
        model["rates"] = None
        for line in model["baseline"]["lines"]:
            line["rate_id"] = None
    elif kind == "fx":
        model["fx"] = None
    elif kind in {"baseline", "profile"}:
        model[kind] = None
        if kind == "profile":
            model["baseline"]["agent_id"] = None
    else:
        model["baseline"][kind] = None
    return model


def review_for(snapshot, **changes):
    review = {
        "id": "SIMULATED-REVIEW", "decision": "approve",
        "actor": snapshot["model"]["profile"]["owners"]["finance"],
        "finance_owner": snapshot["model"]["profile"]["owners"]["finance"],
        "date": DAY.isoformat(), "evidence_ref": "test:external-assertion-only",
        **snapshot["target"], "mode": snapshot["model"]["mode"],
        "sharingClassification": "customer-shareable",
    }
    return {**review, **changes}


class IOCase(unittest.TestCase):
    def setUp(self):
        for name in ("baseline_records", "baseline_projection", "agent_finops"):
            self.assertTrue((FIN / "scripts" / f"{name}.py").is_file(),
                            f"Task3 {name} behavior has not been implemented")
        self.records = baseline_module("baseline_records")
        self.projection = baseline_module("baseline_projection")
        self.cli = baseline_module("agent_finops")
        self.calc = baseline_module("baseline_calc")
        self.model = baseline_module()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def calculated(self, model=None):
        return self.calc.calculate(model or example(), **ACK)

    def snapshot(self, model=None, folder="frozen"):
        path = self.records.freeze(self.calculated(model), self.dir / folder, **ACK)
        return path, json.loads(path.read_text(encoding="utf-8"))

    def review(self, snapshot, **changes):
        path = self.records.record_review(snapshot, review_for(snapshot, **changes), self.dir / "reviews", **ACK)
        return json.loads(path.read_text(encoding="utf-8"))

    def project(self, model=None, **kw):
        return self.projection.project(self.calculated(model), **ACK, audience="customer", **kw)

    def write(self, name, data):
        path = self.dir / name
        path.write_text(json.dumps(data, allow_nan=False), encoding="utf-8", newline="\n")
        return path

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)], cwd=ROOT,
                              capture_output=True, text=True, encoding="utf-8", check=False)


class LifecycleTests(IOCase):
    def test_receipt_survives_canonical_json_before_frozen_record_consumption(self):
        calculated = self.calculated()
        self.calc.validate_receipt(calculated, **ACK)
        canonical = json.loads(json.dumps(calculated, ensure_ascii=False, sort_keys=True, allow_nan=False))
        try:
            self.calc.validate_receipt(canonical, **ACK)
        except ValueError as error:
            self.fail(f"Task2 receipt rejects unchanged canonical JSON; blocks frozen record consumption: {error}")

    def test_every_operation_requires_current_actual_boolean_before_work(self):
        out = self.dir / "must-not-exist"
        for ack in (False, None, 1, "true", {"acknowledged": True}):
            for operation, args in (
                (self.records.seed, (None, None)),
                (self.records.migrate, (None, None, None)),
                (self.records.freeze, (None, out)),
                (self.records.record_review, (None, None, out)),
                (self.records.handover, (None, [])),
                (self.projection.project, (None,)),
            ):
                with self.subTest(operation=operation.__name__, ack=ack):
                    kw = {"audience": "internal"} if operation == self.projection.project else {}
                    with self.assertRaises(ValueError):
                        operation(*args, as_of=DAY, acknowledge_finops_preview=ack, **kw)
                    self.assertFalse(out.exists())

    def test_seed_links_actual_canvas_but_invents_no_owners_currency_or_prices(self):
        bp = blueprint()
        original = copy.deepcopy(bp)
        draft = self.records.seed(bp, "D3-A05", **ACK)
        self.assertEqual(bp, original)
        self.assertEqual(draft["profile"]["agent_id"], "D3-A05")
        agent = next(a for d in bp["domains"] for a in d["agents"] if a["id"] == "D3-A05")
        self.assertEqual(draft["profile"]["canvas"], agent["canvas"])
        self.assertEqual(draft["profile"]["owners"], dict.fromkeys(("business", "technical", "finance")))
        self.assertIsNone(draft["baseline"]["currency"])
        self.assertEqual(draft["rates"], [])
        self.assertNotIn("acknowledgement", draft)
        gaps = self.model.validate_model(draft, as_of=DAY, blueprint=bp)
        self.assertIn("empty-scope", {g["code"] for g in gaps})
        self.assertIn("missing-owner", {g["code"] for g in gaps})
        with self.assertRaises(ValueError):
            self.records.seed(bp, "UNKNOWN", **ACK)

    def test_seed_preserves_root_domain_agent_and_source_privacy(self):
        bp = blueprint()
        bp["internal"] = True
        domain = next(d for d in bp["domains"] if any(a["id"] == "D3-A05" for a in d["agents"]))
        domain["visibility"] = "internal"
        agent = next(a for a in domain["agents"] if a["id"] == "D3-A05")
        agent["internal"] = True
        draft = self.records.seed(bp, "D3-A05", **ACK)
        self.assertTrue(draft["internal"])
        self.assertIn("internal", json.dumps(draft["provenance"]))
        self.assertTrue(all(s["validationStatus"] != "validated" for s in draft["sources"]))

    def test_migration_new_draft_no_inherited_approval_prices_or_fx(self):
        legacy = json.loads((FIN / "examples/caldova-finops.json").read_text(encoding="utf-8"))
        legacy.update(status="approved", internal=True, results={"total": 99999},
                      finops_preview={"acknowledgement": True})
        legacy["technical"] = {"visibility": "internal", "note": "LEGACY-PRIVATE-SENTINEL"}
        path = self.write("legacy.json", legacy)
        before = path.read_bytes()
        draft = self.records.migrate(legacy, blueprint(), "D3-A05", **ACK)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(draft["schema"], "frontier-finops-baseline/1.0")
        self.assertEqual(draft["rates"], [])
        self.assertEqual(draft["fx"], [])
        self.assertEqual(draft["baseline"]["scenarios"], [])
        self.assertNotIn("results", draft)
        self.assertNotIn("review_records", draft)
        self.assertTrue(draft["internal"])
        self.assertIn("LEGACY-PRIVATE-SENTINEL", json.dumps(draft["provenance"]))
        with self.assertRaises(ValueError):
            self.records.migrate({**legacy, "schema": "unknown"}, blueprint(), "D3-A05", **ACK)

    def test_frozen_version_is_exclusive_utf8_lf_and_receipt_bound(self):
        model = self.calculated()
        path = self.records.freeze(model, self.dir / "frozen", **ACK)
        original = path.read_bytes()
        self.assertNotIn(b"\r", original)
        snapshot = json.loads(original)
        self.assertEqual(snapshot["target"]["material_hash"], self.model.model_fingerprint(model))
        self.assertEqual(snapshot["model"], model)
        self.assertNotIn("material_hash", model)
        with self.assertRaises(ValueError):
            self.records.freeze(model, path.parent, **ACK)
        self.assertEqual(path.read_bytes(), original)
        model["baseline"]["version"] = 2
        with self.assertRaises(ValueError):
            self.records.freeze(model, path.parent, **ACK)
        newer = self.records.freeze(self.calculated(model), path.parent, **ACK)
        self.assertNotEqual(path, newer)

    def test_immutable_identity_path_and_date_validation_before_directory(self):
        for bad in ("../escape", "a/b", "a\\b", ".", "CON", "a:stream", "a."):
            model = example()
            model["baseline"]["id"] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.records.freeze(self.calculated(model), self.dir / "no", **ACK)
            self.assertFalse((self.dir / "no").exists())
        with self.assertRaises(ValueError):
            self.records.seed(blueprint(), "D3-A05", as_of="2026-11-12", acknowledge_finops_preview=True)

    def test_old_review_cannot_review_changed_material_or_new_version(self):
        _, snapshot = self.snapshot(simulated())
        review = self.review(snapshot)
        changed = copy.deepcopy(snapshot)
        changed["model"]["baseline"]["assumptions"][0]["description"] += " changed"
        with self.assertRaises(ValueError):
            self.records.handover(changed, [review], **ACK)
        model = copy.deepcopy(snapshot["model"])
        model["baseline"]["version"] = 2
        _, newer = self.snapshot(model, "v2")
        with self.assertRaises(ValueError):
            self.records.handover(newer, [review], **ACK)

    def test_external_review_requires_exact_target_actor_evidence_and_dates(self):
        _, snapshot = self.snapshot(simulated())
        for patch in ({"material_hash": "wrong"}, {"version": True}, {"actor": "other"},
                      {"evidence_ref": " "}, {"date": "2026-11-13"}, {"date": "2026-11-11"},
                      {"finance_owner": "other"}, {"decision": "approved"}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.records.record_review(snapshot, review_for(snapshot, **patch), self.dir / "no", **ACK)
        self.assertFalse((self.dir / "no").exists())
        review = self.review(snapshot, actor="Delegate", delegation_evidence_ref="test:delegation")
        self.assertEqual(review["assertion"], "externally-asserted-not-authenticated")
        with self.assertRaises(ValueError):
            self.review(snapshot, actor="Delegate", delegation_evidence_ref="test:delegation")
        with self.assertRaises(ValueError):
            self.records.handover(snapshot, [review, review], **ACK)

    def test_raw_approved_workshop_notes_and_cached_consent_are_not_review(self):
        model = simulated()
        model.update(status="approved", workshop={"approved": True}, handover={"ready": True})
        _, snapshot = self.snapshot(model)
        result = self.records.handover(snapshot, [], **ACK)
        self.assertFalse(result["ready"])
        self.assertEqual(result["lifecycle"], "validated")
        self.assertIn("missing-owner-review", {g["code"] for g in result["gaps"]})
        with self.assertRaises(ValueError):
            self.records.handover(snapshot, [{"status": "approved"}], **ACK)

    def test_simulated_positive_planning_gate_is_separate_from_financial_permission(self):
        _, snapshot = self.snapshot(simulated())
        result = self.records.handover(snapshot, [self.review(snapshot)], **ACK)
        self.assertTrue(result["ready"])
        self.assertEqual(result["lifecycle"], "approved")
        self.assertEqual(result["as_of"], DAY.isoformat())
        self.assertFalse(result["financial_permission"])
        self.assertEqual(result["gaps"], [])

    def test_every_gap_blocks_even_with_matching_approve(self):
        for kind in ("unpriced", "provisional", "stale", "synthetic", "guardrails", "owner", "uncovered"):
            model = simulated()
            if kind == "unpriced":
                model["rates"][0]["amount"] = None
            elif kind == "provisional":
                model["rates"][0]["verification"]["status"] = "unverified"
            elif kind == "stale":
                model["sources"][0]["lastValidatedAt"] = "2026-01-01"
            elif kind == "synthetic":
                model = example()
            elif kind == "guardrails":
                model["profile"]["guardrails"] = []
            elif kind == "owner":
                model["profile"]["owners"]["business"] = None
            else:
                model["baseline"]["scope"].append({"cost_driver_id": "uncovered", "description": "Unknown",
                                                   "sharingClassification": "customer-shareable"})
            with self.subTest(kind=kind):
                _, snapshot = self.snapshot(model, kind)
                review = self.review(snapshot, id=f"REVIEW-{kind}")
                result = self.records.handover(snapshot, [review], **ACK)
                self.assertFalse(result["ready"])
                self.assertTrue(result["gaps"])

    def test_later_readiness_rechecks_freshness_without_rewriting_history(self):
        path, snapshot = self.snapshot(simulated())
        before = path.read_bytes()
        review = self.review(snapshot)
        result = self.records.handover(snapshot, [review], as_of=date(2027, 1, 1),
                                       acknowledge_finops_preview=True)
        self.assertFalse(result["ready"])
        self.assertIn("stale-source", {g["code"] for g in result["gaps"]})
        self.assertEqual(path.read_bytes(), before)

    def test_undefined_required_unit_metrics_block_planning_even_after_review(self):
        model = simulated()
        for scenario in model["baseline"]["scenarios"]:
            scenario["success_share"] = "0"
        _, snapshot = self.snapshot(model)
        result = self.records.handover(snapshot, [self.review(snapshot)], **ACK)
        self.assertFalse(result["ready"])
        self.assertIn("unavailable-unit-metrics", {g["code"] for g in result["gaps"]})

    def test_review_unknown_sharing_and_explicit_synthetic_assertion_never_ready(self):
        for kind, changes in (("sharing", {"sharingClassification": "validation-required"}),
                              ("unknown", {"sharingClassification": "unknown"}),
                              ("absent", {"sharingClassification": None}),
                              ("blank", {"sharingClassification": "   "}),
                              ("synthetic", {"synthetic": True})):
            _, snapshot = self.snapshot(simulated(), kind)
            review = self.review(snapshot, id=f"REVIEW-{kind}", **changes)
            result = self.records.handover(snapshot, [review], **ACK)
            self.assertFalse(result["ready"])
            self.assertTrue(result["gaps"])

    def test_malformed_review_and_snapshot_fields_raise_valueerror_before_io(self):
        _, snapshot = self.snapshot(simulated())
        for patch in ({"decision": []}, {"actor": True}, {"date": []},
                      {"internal": "yes"}, {"visibility": []}, {"customer_scope": []}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.records.record_review(snapshot, review_for(snapshot, **patch), self.dir / "no", **ACK)
        self.assertFalse((self.dir / "no").exists())
        bad = copy.deepcopy(snapshot)
        bad["target"]["version"] = True
        with self.assertRaises(ValueError):
            self.records.handover(bad, [], **ACK)

    def test_seed_rejects_malformed_agents_and_unresolved_existing_source_refs(self):
        bp = blueprint()
        bp["domains"][0]["agents"][0]["id"] = []
        with self.assertRaises(ValueError):
            self.records.seed(bp, "D3-A05", **ACK)
        bp = blueprint()
        agent = next(a for d in bp["domains"] for a in d["agents"] if a["id"] == "D3-A05")
        agent["src"] = ["DOES-NOT-EXIST"]
        with self.assertRaises(ValueError):
            self.records.seed(bp, "D3-A05", **ACK)

    def test_record_review_withholding_is_external_not_raw_status_or_metadata(self):
        _, snapshot = self.snapshot(simulated())
        for patch in ({"id": "../escape"}, {"mode": "synthetic"}, {"evidence_ref": None},
                      {"date": None}, {"actor": "Delegate", "delegation_evidence_ref": None}):
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.records.record_review(snapshot, review_for(snapshot, **patch), self.dir / "no", **ACK)
        self.assertFalse((self.dir / "no").exists())
        before = copy.deepcopy(snapshot)
        self.records.handover(snapshot, [], **ACK)
        self.assertEqual(snapshot, before)

    def test_migration_retains_technical_source_privacy_without_cached_consent(self):
        legacy = {"schema": "frontier-finops/1.0", "currency": "USD",
                  "finops_preview": {"acknowledgement": True, "internal": True,
                                     "provenance": {"inputs": {"rates": {"visibility": "internal"}}}}}
        draft = self.records.migrate(legacy, blueprint(), "D3-A05", **ACK)
        self.assertTrue(draft.get("internal"))
        self.assertIsNone(draft["baseline"]["currency"])
        self.assertNotIn("acknowledgement", json.dumps(draft))

    def test_review_source_parent_references_must_resolve_and_remain_private(self):
        _, snapshot = self.snapshot(simulated())
        with self.assertRaises(ValueError):
            self.records.record_review(snapshot, review_for(snapshot, source_id="UNKNOWN"),
                                       self.dir / "no", **ACK)
        self.assertFalse((self.dir / "no").exists())
        snapshot["model"]["sources"][0]["internal"] = True
        # Material changed: this must be a new calculated frozen target, not a patched review.
        _, snapshot = self.snapshot(snapshot["model"], "private-source")
        review = self.review(snapshot, source_id="SYN-ENGINEERING")
        report = self.projection.project(snapshot, [review], **ACK, audience="customer")
        self.assertEqual(report["handover"]["status"], "withheld")

    def test_unknown_legacy_visibility_cannot_pass_planning_gate(self):
        model = simulated()
        model["rates"][0]["visibility"] = "unresolved"
        _, snapshot = self.snapshot(model)
        result = self.records.handover(snapshot, [self.review(snapshot)], **ACK)
        self.assertFalse(result["ready"])
        self.assertIn("sharing-validation", {g["code"] for g in result["gaps"]})

    def test_malformed_legacy_sharing_is_valueerror_and_migration_is_pure(self):
        legacy = {"schema": "frontier-finops/1.0", "sharingClassification": []}
        with self.assertRaises(ValueError):
            self.records.migrate(legacy, blueprint(), "D3-A05", **ACK)
        legacy = {"schema": "frontier-finops/1.0", "currency": "USD", "fx": {"chf_per_usd": 0.81}}
        before = copy.deepcopy(legacy)
        self.records.migrate(legacy, blueprint(), "D3-A05", **ACK)
        self.assertEqual(legacy, before)

    def test_seed_merges_actual_ancestor_classes_before_copying_canvas(self):
        for location in ("root", "domain", "agent", "meta", "nested"):
            for classification in ("internal-only", "validation-required", "unknown", None):
                bp = seed_blueprint()
                bp.update(customer_scope="caldova-scope", sharingClassification="customer-shareable")
                domain = next(d for d in bp["domains"] if any(a["id"] == "D3-A05" for a in d["agents"]))
                agent = next(a for a in domain["agents"] if a["id"] == "D3-A05")
                agent["canvas"]["instructions"] = "SEED-PRIVATE-SENTINEL"
                agent["canvas"]["copied_context"] = {}
                private = (bp if location == "root" else domain if location == "domain" else agent
                           if location == "agent" else bp["meta"] if location == "meta"
                           else agent["canvas"]["copied_context"])
                private["sharingClassification"] = classification
                with self.subTest(location=location, classification=classification):
                    draft = self.records.seed(bp, "D3-A05", **ACK)
                    report = self.projection.project(self.calculated(draft), **ACK, audience="customer",
                                                     customer_scope="caldova-scope")
                    for text in (json.dumps(report), self.projection.render_markdown(report),
                                 json.dumps({"schema": "frontier-agent-finops-view/1.0", "records": [report]})):
                        self.assertNotIn("SEED-PRIVATE-SENTINEL", text)
                    self.assertIn(draft["sharingClassification"], {"internal-only", "validation-required"})

    def test_seed_conflicting_scope_ancestry_never_picks_a_customer(self):
        for location in ("domain", "agent", "meta", "nested", "scope-list"):
            bp = seed_blueprint()
            bp.update(customer_scope="caldova-scope", sharingClassification="customer-specific")
            domain = next(d for d in bp["domains"] if any(a["id"] == "D3-A05" for a in d["agents"]))
            agent = next(a for a in domain["agents"] if a["id"] == "D3-A05")
            agent["canvas"]["instructions"] = "SCOPE-CONFLICT-SENTINEL"
            agent["canvas"]["copied_context"] = {}
            conflicting = (domain if location == "domain" else agent if location == "agent"
                           else bp["meta"] if location == "meta" else agent["canvas"]["copied_context"])
            if location == "scope-list":
                conflicting["customer_scopes"] = ["caldova-scope", "other-scope"]
            else:
                conflicting.update(sharingClassification="customer-specific", customer_scope="other-scope")
            draft = self.records.seed(bp, "D3-A05", **ACK)
            for scope in ("caldova-scope", "other-scope"):
                with self.subTest(location=location, scope=scope):
                    report = self.projection.project(self.calculated(draft), **ACK, audience="customer",
                                                     customer_scope=scope)
                    self.assertNotIn("SCOPE-CONFLICT-SENTINEL", json.dumps(report))
            self.assertEqual(draft["sharingClassification"], "validation-required")
            self.assertEqual(set(draft["customer_scopes"]), {"caldova-scope", "other-scope"})

    def test_seed_public_canvas_control_and_unrelated_private_domain(self):
        bp = seed_blueprint()
        bp.update(customer_scope="caldova-scope", sharingClassification="customer-shareable")
        domain = next(d for d in bp["domains"] if any(a["id"] == "D3-A05" for a in d["agents"]))
        agent = next(a for a in domain["agents"] if a["id"] == "D3-A05")
        domain["sharingClassification"] = agent["sharingClassification"] = "customer-shareable"
        agent["canvas"]["instructions"] = "PUBLIC-CANVAS-CONTROL"
        next(d for d in bp["domains"] if d is not domain)["sharingClassification"] = "internal-only"
        draft = self.records.seed(bp, "D3-A05", **ACK)
        report = self.projection.project(self.calculated(draft), **ACK, audience="customer",
                                         customer_scope="caldova-scope")
        self.assertIn("PUBLIC-CANVAS-CONTROL", json.dumps(report))
        self.assertIn("PUBLIC-CANVAS-CONTROL", self.projection.render_markdown(report))

    def test_migration_scope_conflict_cannot_declassify_new_blueprint_context(self):
        bp = seed_blueprint()
        bp.update(customer_scope="caldova-scope", sharingClassification="customer-specific")
        legacy = {"schema": "frontier-finops/1.0", "sharingClassification": "customer-specific",
                  "customer_scope": "other-scope"}
        draft = self.records.migrate(legacy, bp, "D3-A05", **ACK)
        self.assertEqual(draft["sharingClassification"], "validation-required")
        self.assertEqual(set(draft["customer_scopes"]), {"caldova-scope", "other-scope"})

    def test_structured_synthetic_review_ancestry_never_passes_planning_handover(self):
        markers = [
            {"type": "synthetic"}, {"validationStatus": "synthetic"}, {"status": "synthetic"},
            {"context": {"synthetic": True}}, {"context": {"mode": "synthetic"}},
            {"context": {"type": "synthetic"}}, {"context": {"status": "synthetic"}},
            {"context": {"validationStatus": "synthetic"}}, {"verification": {"status": "synthetic"}},
            {"evidence": [{"type": "synthetic"}]},
            {"type": "synthetic", "synthetic": False, "status": "approved", "validationStatus": "validated"},
            {"synthetic": False, "evidence": [{"type": "synthetic", "mode": "planning", "synthetic": False}]},
        ]
        for mode in ("planning", "synthetic"):
            for verification in ("verified", "unverified", "synthetic"):
                model = simulated()
                model["mode"] = mode
                for rate in model["rates"]:
                    rate["verification"]["status"] = verification
                _, snapshot = self.snapshot(model, f"{mode}-{verification}")
                for i, marker in enumerate(markers):
                    with self.subTest(mode=mode, verification=verification, marker=marker):
                        review = self.review(snapshot, id=f"MARKER-{mode}-{verification}-{i}", **marker)
                        result = self.records.handover(snapshot, [review], **ACK)
                        self.assertFalse(result["ready"])
                        self.assertFalse(result["financial_permission"])
                        self.assertIn("synthetic-evidence", {g["code"] for g in result["gaps"]})

    def test_arbitrary_synthetic_prose_is_not_a_structured_review_assertion(self):
        _, snapshot = self.snapshot(simulated())
        review = self.review(snapshot, synthetic=False, note="synthetic",
                             context={"description": "This prose mentions synthetic, not a structured assertion."})
        result = self.records.handover(snapshot, [review], **ACK)
        self.assertTrue(result["ready"])  # simulated verified-input test only
        self.assertFalse(result["financial_permission"])

    def test_direct_snapshot_source_cycles_block_reviewed_handover_and_customer_costs(self):
        for nested in (False, True):
            model = simulated()
            first = {**model["sources"][0], "id": "CYCLE-A", "src": ["CYCLE-B"]}
            second = {**model["sources"][0], "id": "CYCLE-B"}
            if nested:
                second["provenance"] = {"source_id": "CYCLE-A"}
            else:
                second["content_src"] = ["CYCLE-A"]
            model["sources"].extend([first, second])
            model["rates"][0]["source_id"] = "CYCLE-A"
            with self.subTest(nested=nested):
                _, snapshot = self.snapshot(model, f"cycle-{nested}")
                review = self.review(snapshot, id=f"REVIEW-{nested}")
                result = self.records.handover(snapshot, [review], **ACK)
                self.assertFalse(result["ready"])
                self.assertFalse(result["financial_permission"])
                self.assertIn("source-ancestry-cycle", {g["code"] for g in result["gaps"]})
                report = self.projection.project(snapshot, [review], **ACK, audience="customer")
                month = report["scenarios"]["expected"]["months"][0]
                self.assertEqual(month["total"]["status"], "withheld")
                self.assertIsNone(month["total"]["amount"])
                self.assertEqual(month["lines"][1]["cost"]["amount"], "10.00")
                self.assertNotEqual(report["status"], "planning-ready")

    def test_unused_cycles_do_not_hide_independent_rows_and_shared_dag_is_not_cycle(self):
        for cycle in (False, True):
            model = simulated()
            model["sources"].extend([
                {**model["sources"][0], "id": "GRAPH-A", "src": ["GRAPH-C"]},
                {**model["sources"][0], "id": "GRAPH-B", "content_src": ["GRAPH-C"]},
                {**model["sources"][0], "id": "GRAPH-C", **({"source_id": "GRAPH-A"} if cycle else {})},
            ])
            _, snapshot = self.snapshot(model, f"graph-{cycle}")
            review = self.review(snapshot, id=f"REVIEW-{cycle}")
            result = self.records.handover(snapshot, [review], **ACK)
            report = self.projection.project(snapshot, [review], **ACK, audience="customer")
            with self.subTest(cycle=cycle):
                self.assertEqual(result["ready"], not cycle)
                self.assertEqual("source-ancestry-cycle" in {g["code"] for g in result["gaps"]}, cycle)
                self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")

    def test_nullable_source_registry_review_records_remain_partial_not_typeerror(self):
        _, snapshot = self.snapshot(nullable_model("sources"))
        review = self.review(snapshot)
        result = self.records.handover(snapshot, [review], **ACK)
        self.assertFalse(result["ready"])
        self.assertFalse(result["financial_permission"])

    def test_missing_nullable_finance_owner_refuses_review_with_valueerror(self):
        for absent in ("profile", "owners"):
            model = nullable_model("profile") if absent == "profile" else example()
            if absent == "owners":
                model["profile"]["owners"] = None
            _, snapshot = self.snapshot(model, f"no-{absent}")
            review = {"id": "NO-OWNER", "actor": "Finance lead", "finance_owner": "Finance lead",
                      "decision": "approve", "date": DAY.isoformat(), "evidence_ref": "test:not-real-approval",
                      "mode": model["mode"], "sharingClassification": "customer-shareable", **snapshot["target"]}
            with self.subTest(absent=absent), self.assertRaises(ValueError):
                self.records.record_review(snapshot, review, self.dir / "no-review", **ACK)
            self.assertFalse((self.dir / "no-review").exists())

    def test_seed_closes_every_reference_kind_through_chained_source_parents(self):
        for ancestor_kind in ("src", "content_src", "source_id"):
            for parent_kind in ("src", "content_src", "source_id"):
                for nested in (False, True):
                    bp = seed_blueprint()
                    agent = next(a for d in bp["domains"] for a in d["agents"] if a["id"] == "D3-A05")
                    agent["canvas"]["instructions"] = "TRANSITIVE-PRIVATE-CANVAS"
                    holder = agent if not nested else agent["canvas"].setdefault("context", {})
                    holder[ancestor_kind] = "GRAPH-CHILD" if ancestor_kind == "source_id" else ["GRAPH-CHILD"]
                    parent = {**bp["evidence"][0], "id": "GRAPH-PARENT", "source_id": "GRAPH-GRANDPARENT"}
                    child = {**bp["evidence"][0], "id": "GRAPH-CHILD",
                             parent_kind: "GRAPH-PARENT" if parent_kind == "source_id" else ["GRAPH-PARENT"]}
                    grandparent = {**bp["evidence"][0], "id": "GRAPH-GRANDPARENT",
                                   "sharingClassification": "internal-only"}
                    bp["evidence"].extend([child, parent, grandparent])
                    with self.subTest(ancestor=ancestor_kind, parent=parent_kind, nested=nested):
                        draft = self.records.seed(bp, "D3-A05", **ACK)
                        report = self.projection.project(self.calculated(draft), **ACK, audience="customer",
                                                         customer_scope="caldova-scope")
                        for text in (json.dumps(report), self.projection.render_markdown(report),
                                     json.dumps({"schema": "frontier-agent-finops-view/1.0", "records": [report]})):
                            self.assertNotIn("TRANSITIVE-PRIVATE-CANVAS", text)
                        self.assertEqual(draft["sharingClassification"], "internal-only")
                        self.assertIn("GRAPH-GRANDPARENT", draft.get("src", []))

    def test_seed_source_closure_scope_cycle_missing_unknown_and_public_control(self):
        for case in ("scope", "cycle", "missing", "unknown", "public"):
            bp = seed_blueprint()
            agent = next(a for d in bp["domains"] for a in d["agents"] if a["id"] == "D3-A05")
            agent["canvas"]["instructions"] = "CLOSURE-CONTROL-CANVAS"
            agent["source_id"] = "GRAPH-CHILD"
            child = {**bp["evidence"][0], "id": "GRAPH-CHILD", "source_id": "GRAPH-PARENT"}
            parent = {**bp["evidence"][0], "id": "GRAPH-PARENT"}
            if case == "scope":
                parent["customer_scope"] = "other-scope"
            elif case == "cycle":
                parent["source_id"] = "GRAPH-CHILD"
            elif case == "missing":
                child["source_id"] = None
            elif case == "unknown":
                child["source_id"] = "UNKNOWN-PARENT"
            bp["evidence"].extend([child, parent])
            with self.subTest(case=case):
                if case == "unknown":
                    with self.assertRaises(ValueError):
                        self.records.seed(bp, "D3-A05", **ACK)
                    continue
                draft = self.records.seed(bp, "D3-A05", **ACK)
                report = self.projection.project(self.calculated(draft), **ACK, audience="customer",
                                                 customer_scope="caldova-scope")
                if case == "public":
                    self.assertIn("CLOSURE-CONTROL-CANVAS", json.dumps(report))
                    self.assertIn("GRAPH-PARENT", draft.get("src", []))
                else:
                    self.assertNotIn("CLOSURE-CONTROL-CANVAS", json.dumps(report))
                    self.assertEqual(draft["sharingClassification"], "validation-required")


class ProjectionTests(IOCase):
    def serialisations(self, report):
        return (json.dumps(report, ensure_ascii=False), self.projection.render_markdown(report),
                json.dumps({"agent_finops": {"schema": "frontier-agent-finops-view/1.0",
                                            "records": [report]}}))

    def test_public_report_is_derivative_with_scenarios_units_evidence_and_notice(self):
        report = self.project()
        self.assertEqual(report["schema"], "frontier-agent-finops-report/1.0")
        self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
        self.assertEqual(report["scenarios"]["expected"]["months"][0]["total"]["amount"], "110.00")
        self.assertIn("unit_metrics", report["scenarios"]["expected"])
        self.assertIn("Preview", report["notice"])
        self.assertIn("assumptions", report["context"])
        self.assertIn("sources", report["evidence"])
        self.assertFalse(report["handover"]["ready"])
        self.assertNotIn("model_fingerprint", json.dumps(report))
        self.assertIn("1320.00", self.projection.render_markdown(report))
        with self.assertRaises(ValueError):
            self.model.validate_model(report, as_of=DAY)
        with self.assertRaises(ValueError):
            self.projection.render_markdown(example())

    def test_private_dependency_matrix_never_leaks_in_any_serialisation(self):
        cases = {
            "root": lambda m: m,
            "line": lambda m: m["baseline"]["lines"][0],
            "quantity": lambda m: m["baseline"]["scenarios"][1]["driver_evidence"]["tokens_per_run"],
            "rate": lambda m: m["rates"][0],
            "source": lambda m: m["sources"][0],
            "outcome": lambda m: m["profile"]["outcome"],
            "unknown": lambda m: m["rates"][0],
        }
        for kind, locate in cases.items():
            model = example()
            private = locate(model)
            private.update(sharingClassification="unrecognised" if kind == "unknown" else "internal-only",
                           note="PRIVATE-NOTE-SENTINEL")
            # The sentinel must be protected data, not a separately public rate.
            # Private outcome context does not declassify or hide unrelated costs.
            if kind in {"root", "rate", "source", "unknown"}:
                model["rates"][0]["amount"] = "987654.321"
            elif kind == "quantity":
                model["baseline"]["scenarios"][1]["drivers"]["tokens_per_run"] = "987654.321"
            if kind == "rate":
                private["id"] = "PRIVATE-RATE-SENTINEL"
                model["baseline"]["lines"][0]["rate_id"] = private["id"]
            report = self.project(model)
            with self.subTest(kind=kind):
                for serialised in self.serialisations(report):
                    self.assertNotIn("PRIVATE-NOTE-SENTINEL", serialised)
                    self.assertNotIn("PRIVATE-RATE-SENTINEL", serialised)
                    if kind != "outcome":
                        self.assertNotIn("987654.321", serialised)
                if kind != "outcome":
                    if kind == "root":
                        self.assertEqual(report["status"], "withheld")
                    else:
                        self.assertIsNone(report["scenarios"]["expected"]["months"][0]["total"]["amount"])
                        self.assertEqual(report["scenarios"]["expected"]["months"][0]["total"]["status"], "withheld")
                else:
                    metric = report["scenarios"]["expected"]["unit_metrics"]["annual_recurring"]["per_outcome"]
                    self.assertEqual(metric["status"], "withheld")

    def test_independent_public_line_remains_not_public_subset_full_total(self):
        model = example()
        model["rates"][0]["sharingClassification"] = "internal-only"
        report = self.project(model)
        month = report["scenarios"]["expected"]["months"][0]
        self.assertEqual(month["lines"][1]["cost"]["amount"], "10.00")
        self.assertIsNone(month["total"]["amount"])
        self.assertEqual(month["total"]["status"], "withheld")
        self.assertIsNone(month["known_priced_subtotal"]["amount"])
        self.assertEqual(report["handover"]["status"], "withheld")

    def test_actual_fx_and_transitive_legacy_source_restrictions_dominate_flags(self):
        for flag in ({"internal": True}, {"visibility": "internal"},
                     {"sharingClassification": "validation-required"}):
            model = example()
            model["rates"][0]["currency"] = "USD"
            model["fx"] = [{"id": "PRIVATE-FX-SENTINEL", "from_currency": "USD", "to_currency": "CHF",
                            "rate": "0.5", "date": DAY.isoformat(), "method": "synthetic",
                            "source_id": "SYN-ENGINEERING", "verification": {"status": "synthetic", "verified_at": DAY.isoformat()},
                            "freshness_policy": {"max_age_days": 30}, "sharingClassification": "customer-shareable",
                            **flag}]
            report = self.project(model)
            for text in self.serialisations(report):
                self.assertNotIn("PRIVATE-FX-SENTINEL", text)
            self.assertEqual(report["scenarios"]["expected"]["months"][0]["total"]["status"], "withheld")
        model = example()
        private_source = {**model["sources"][0], "id": "PRIVATE-SOURCE-SENTINEL", "internal": True}
        model["sources"].append(private_source)
        model["sources"][0]["src"] = private_source["id"]
        report = self.project(model)
        for text in self.serialisations(report):
            self.assertNotIn(private_source["id"], text)
        self.assertEqual(report["scenarios"]["expected"]["months"][0]["total"]["status"], "withheld")

    def test_scope_is_required_not_authorisation_unknown_audience_refuses(self):
        model = example()
        model["rates"][0].update(sharingClassification="customer-specific", customer_scope="caldova-test")
        self.assertEqual(self.project(model)["scenarios"]["expected"]["annual_recurring"]["status"], "withheld")
        scoped = self.project(model, customer_scope="caldova-test")
        self.assertEqual(scoped["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
        self.assertIn("not authorisation", scoped["limitations"])
        with self.assertRaises(ValueError):
            self.projection.project(self.calculated(), **ACK, audience="unknown")

    def test_unused_private_context_hides_hash_not_independent_public_amounts(self):
        model = example()
        model["sources"].append({**model["sources"][0], "id": "UNUSED-PRIVATE",
                                 "internal": True, "title": "UNUSED-SECRET"})
        report = self.project(model)
        self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
        for text in self.serialisations(report):
            self.assertNotIn("UNUSED-PRIVATE", text)
            self.assertNotIn("UNUSED-SECRET", text)
            self.assertNotIn(self.model.model_fingerprint(model), text)

    def test_private_external_review_withholds_review_and_readiness(self):
        _, snapshot = self.snapshot(simulated())
        review = self.review(snapshot, sharingClassification="internal-only", evidence_ref="PRIVATE-REVIEW-SENTINEL")
        report = self.projection.project(snapshot, [review], **ACK, audience="customer")
        self.assertEqual(report["handover"]["status"], "withheld")
        for text in self.serialisations(report):
            self.assertNotIn("PRIVATE-REVIEW-SENTINEL", text)
            self.assertNotIn(snapshot["target"]["material_hash"], text)
        internal = self.projection.project(snapshot, [review], **ACK, audience="internal")
        self.assertEqual(internal["distribution"], "private-context-not-shareable")

    def test_markdown_escapes_cells_and_does_not_make_evidence_links(self):
        model = example()
        model["baseline"]["assumptions"][0]["description"] = "| [click](javascript:bad)\n<b>HTML</b>"
        text = self.projection.render_markdown(self.project(model))
        self.assertNotIn("[click](javascript:bad)", text)
        self.assertNotIn("<b>", text)
        self.assertIn("\\|", text)

    def test_forged_receipt_and_private_error_content_never_get_serialised(self):
        model = self.calculated()
        model["results"]["scenarios"]["expected"]["annual_recurring"]["amount"] = "999999"
        for audience in ("customer", "internal"):
            with self.assertRaises(ValueError):
                self.projection.project(model, **ACK, audience=audience)

    def test_missing_and_provisional_prices_remain_distinct_from_withheld(self):
        missing = example()
        missing["rates"][0]["amount"] = None
        absent = self.project(missing)["scenarios"]["expected"]["months"][0]["total"]
        self.assertIsNone(absent["amount"])
        self.assertEqual(absent["status"], "incomplete")
        provided = self.project()["scenarios"]["expected"]["months"][0]
        self.assertEqual(provided["total"]["status"], "provisional")
        self.assertEqual(provided["provisional_subtotal"]["amount"], "110.00")
        missing["rates"][0]["sharingClassification"] = "internal-only"
        self.assertEqual(self.project(missing)["scenarios"]["expected"]["months"][0]["total"]["status"], "withheld")

    def test_deep_note_and_legacy_visibility_unknown_classification_fail_closed(self):
        for flag in ({"internal": True}, {"visibility": "internal"}, {"visibility": "unknown"},
                     {"sharingClassification": "unknown"}):
            model = example()
            model["rates"][0]["verification"]["context"] = {
                "note": "NESTED-PRIVATE-SENTINEL", **flag}
            report = self.project(model)
            self.assertEqual(report["scenarios"]["expected"]["months"][0]["total"]["status"], "withheld")
            for text in self.serialisations(report):
                self.assertNotIn("NESTED-PRIVATE-SENTINEL", text)

    def test_actual_private_source_identity_never_appears_in_rate_or_scenario_metadata(self):
        model = example()
        model["sources"][0].update(id="PRIVATE-SOURCE", internal=True, title="SOURCE-TEXT-SENTINEL")
        for rate in model["rates"]:
            if rate.get("source_id") == "SYN-ENGINEERING":
                rate["source_id"] = "PRIVATE-SOURCE"

        def replace(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "source_id" and child == "SYN-ENGINEERING":
                        value[key] = "PRIVATE-SOURCE"
                    else:
                        replace(child)
            elif isinstance(value, list):
                for child in value:
                    replace(child)
        replace(model)
        report = self.project(model)
        for text in self.serialisations(report):
            self.assertNotIn("PRIVATE-SOURCE", text)
            self.assertNotIn("SOURCE-TEXT-SENTINEL", text)

    def test_profile_envelope_privacy_withholds_linked_identity_and_baseline(self):
        model = example()
        model["profile"].update(sharingClassification="internal-only", name="PRIVATE-PROFILE-SENTINEL")
        report = self.project(model)
        for text in self.serialisations(report):
            self.assertNotIn("PRIVATE-PROFILE-SENTINEL", text)
            self.assertNotIn("D3-A05", text)

    def test_invalid_audience_types_refuse_and_internal_projection_is_labelled(self):
        for audience in (None, [], {}, True, "public"):
            with self.subTest(audience=audience), self.assertRaises(ValueError):
                self.projection.project(self.calculated(), **ACK, audience=audience)
        model = example()
        model["rates"][0].update(internal=True, note="PRIVATE-LOCAL-CONTEXT")
        internal = self.projection.project(self.calculated(model), **ACK, audience="internal")
        self.assertEqual(internal["distribution"], "private-context-not-shareable")
        self.assertIn("PRIVATE-LOCAL-CONTEXT", json.dumps(internal))

    def test_report_supplies_authored_scenarios_scope_and_quantities_after_projection(self):
        report = self.project()
        expected = report["scenario_inputs"][1]
        self.assertEqual(expected["id"], "expected")
        self.assertEqual(expected["monthly_runs"], ["100"] * 12)
        model = example()
        model["baseline"]["scenarios"][1]["driver_evidence"]["tokens_per_run"]["internal"] = True
        model["baseline"]["scenarios"][1]["drivers"]["tokens_per_run"] = "987654.321"
        private = self.project(model)
        for text in self.serialisations(private):
            self.assertNotIn("987654.321", text)
        self.assertIn({"status": "withheld"}, private["scenario_inputs"][1]["drivers"].values())

    def test_private_cost_and_driver_ids_are_not_exposed_as_public_reference_keys(self):
        model = example()
        model["baseline"]["lines"][0].update(internal=True, cost_driver_id="PRIVATE-COST-ID")
        model["baseline"]["scope"][0]["cost_driver_id"] = "PRIVATE-COST-ID"
        report = self.project(model)
        for text in self.serialisations(report):
            self.assertNotIn("PRIVATE-COST-ID", text)
        model = example()
        for scenario in model["baseline"]["scenarios"]:
            scenario["drivers"]["PRIVATE-QUANTITY-ID"] = scenario["drivers"].pop("tokens_per_run")
            evidence = scenario["driver_evidence"].pop("tokens_per_run")
            scenario["driver_evidence"]["PRIVATE-QUANTITY-ID"] = {**evidence, "internal": True}
        model["baseline"]["lines"][0]["driver_id"] = "PRIVATE-QUANTITY-ID"
        report = self.project(model)
        for text in self.serialisations(report):
            self.assertNotIn("PRIVATE-QUANTITY-ID", text)

    def test_explicit_mode_and_monetary_basis_survive_roundtrip_in_derivative(self):
        report = self.project()
        self.assertEqual(report["mode"], "synthetic")
        self.assertEqual(report["baseline"]["version"], 1)
        self.assertEqual(report["scenarios"]["expected"]["unit_metrics"]["first_year"]["per_run"]["basis"], "first-year")
        encoded = json.loads(json.dumps(report, sort_keys=True))
        self.assertEqual(self.projection.render_markdown(report), self.projection.render_markdown(encoded))

    def test_technical_target_hash_cannot_escape_through_review_alias_fields(self):
        _, snapshot = self.snapshot(simulated())
        results_hash = snapshot["model"]["finops_preview"]["calculations"]["baseline"]["results_fingerprint"]
        review = self.review(snapshot, extra_context={"copied_target": snapshot["target"]["material_hash"],
                                                      "copied_results": results_hash})
        report = self.projection.project(snapshot, [review], **ACK, audience="customer")
        for text in self.serialisations(report):
            self.assertNotIn(snapshot["target"]["material_hash"], text)
            self.assertNotIn(results_hash, text)

    def test_baseline_parent_restriction_withholds_child_context_and_inputs(self):
        model = example()
        model["baseline"]["internal"] = True
        model["baseline"]["assumptions"][0]["description"] = "BASELINE-PRIVATE-CONTEXT"
        model["baseline"]["scenarios"][1]["drivers"]["tokens_per_run"] = "987654.321"
        report = self.project(model)
        for text in self.serialisations(report):
            self.assertNotIn("BASELINE-PRIVATE-CONTEXT", text)
            self.assertNotIn("987654.321", text)
        self.assertEqual(report["profile"]["agent_id"], "D3-A05")
        self.assertEqual(report["context"]["status"], "withheld")

    def test_private_placeholder_keys_are_canonical_across_input_object_order(self):
        model = example()
        for scenario in model["baseline"]["scenarios"]:
            scenario["driver_evidence"]["tokens_per_run"]["internal"] = True
        ordered = json.loads(json.dumps(model, sort_keys=True))
        first, second = self.project(model), self.project(ordered)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))

    def test_customer_redacts_known_ancestry_digest_aliases_in_keys_and_strings(self):
        for field in ("blueprint_fingerprint", "legacy_fingerprint", "source_fingerprint",
                      "rate_hash", "fx_digest", "sha256"):
            model = example()
            digest = "abcdef1234567890" * 4
            model["provenance"] = {"inputs": {field: digest}}
            model["sources"].append({**model["sources"][0], "id": "UNUSED-PRIVATE-SOURCE", "internal": True})
            model["sources"][0]["annotations"] = {
                "copied_blueprint_digest": digest,
                "embedded": f"prefix/{digest.upper()}/suffix",
                f"digest-key-{digest}": "must not expose the original key",
            }
            report = self.project(model)
            with self.subTest(field=field):
                for text in self.serialisations(report):
                    self.assertNotIn(digest, text.lower())
                self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")

    def test_customer_redacts_material_and_result_hashes_used_as_review_dictionary_keys(self):
        _, snapshot = self.snapshot(simulated())
        hashes = [snapshot["target"]["material_hash"],
                  snapshot["model"]["finops_preview"]["calculations"]["baseline"]["results_fingerprint"]]
        review = self.review(snapshot, annotations={hashes[0]: "target alias",
                                                   f"embedded-key/{hashes[1]}/suffix": "result alias"})
        report = self.projection.project(snapshot, [review], **ACK, audience="customer")
        for text in self.serialisations(report):
            for digest in hashes:
                self.assertNotIn(digest, text.lower())
        self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")

    def test_customer_redacts_private_source_and_evidence_references_embedded_or_as_keys(self):
        model = example()
        private = {**model["sources"][0], "id": "PRIVATE-SOURCE-TOKEN", "internal": True,
                   "evidence_ref": "private:evidence/reference", "url": "https://example.invalid/private/evidence"}
        model["sources"].append(private)
        tokens = [private["id"], private["evidence_ref"], private["url"]]
        model["sources"][0]["public_annotations"] = {
            f"key-prefix/{token}/suffix": f"note mentions prefix/{token}/suffix" for token in tokens}
        model["profile"]["demand_context"] = f"Public sentence quotes [{private['id']}] as an embedded reference."
        report = self.project(model)
        for text in self.serialisations(report):
            for token in tokens:
                self.assertNotIn(token, text)
        month = report["scenarios"]["expected"]["months"][0]
        self.assertEqual(month["lines"][1]["cost"]["amount"], "10.00")
        self.assertEqual(month["total"]["amount"], "110.00")

    def test_reference_token_collisions_do_not_redact_dependency_approved_financial_values(self):
        model = example()
        model["sources"].append({**model["sources"][0], "id": "10", "internal": True, "evidence_ref": "0.5"})
        model["sources"][0]["note"] = "Reference token 10 and private evidence 0.5 are not public annotations."
        report = self.project(model)
        self.assertEqual(report["evidence"]["sources"][0]["note"], {"status": "withheld"})
        self.assertEqual(report["evidence"]["rates"][1]["amount"], "10")
        expected = report["scenario_inputs"][1]
        self.assertEqual(expected["monthly_runs"], ["100"] * 12)
        self.assertEqual(expected["success_share"], "0.5")
        month = report["scenarios"]["expected"]["months"][0]
        self.assertEqual(month["lines"][1]["cost"]["amount"], "10.00")
        self.assertEqual(month["total"]["amount"], "110.00")

    def test_review_ancestry_digest_aliases_are_known_before_serialising_public_review(self):
        _, snapshot = self.snapshot(simulated())
        digest = "fedcba0123456789" * 4
        review = self.review(snapshot, external_context={"source_fingerprint": digest,
                                                         f"alias/{digest}/key": f"embedded/{digest}/value"})
        report = self.projection.project(snapshot, [review], **ACK, audience="customer")
        for text in self.serialisations(report):
            self.assertNotIn(digest, text)
        self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")

    def test_known_external_digest_values_are_not_declassified_by_format(self):
        for digest in ("0123456789abcdef" * 2, "opaque:external-source-digest", "sha256:" + "abcd1234" * 8):
            model = example()
            model["provenance"] = {"inputs": {"source_fingerprint": digest}}
            model["sources"][0]["alias_context"] = {f"embedded/{digest}/key": f"prefix/{digest}/value"}
            report = self.project(model)
            with self.subTest(digest=digest):
                for text in self.serialisations(report):
                    self.assertNotIn(digest, text)
                self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")

    def test_digest_registry_keys_lists_values_and_nested_entries_protect_aliases(self):
        digest = "fed01234" * 8
        formats = [{digest: True}, {"entries": [{digest: False}]},
                   {"nested": {"registry": {digest: {"checked": True}}}},
                   {"values": [digest]}, {"record": {"value": digest}}]
        for registry in formats:
            model = example()
            model["provenance"] = {"source_hashes": registry}
            model["sources"][0]["annotations"] = {f"alias-key/{digest}": f"embedded/{digest}/text",
                                                   "public_control": "PUBLIC-ANNOTATION-CONTROL"}
            report = self.project(model)
            with self.subTest(registry=registry):
                for text in self.serialisations(report):
                    self.assertNotIn(digest, text)
                self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
                self.assertIn("PUBLIC-ANNOTATION-CONTROL", json.dumps(report))

    def test_fixed_schema_keys_survive_private_unused_identifier_collisions(self):
        tokens = ("drivers", "driver_evidence", "monthly_runs", "amount", "unit", "source_id",
                  "id", "assumptions", "confidence", "owners")
        for token in tokens:
            for restricted in (False, True):
                model = example()
                model["sources"].append({**model["sources"][0], "id": token, "internal": True,
                                         "evidence_ref": f"private:collision/{token}"})
                model["sources"][0]["annotations"] = {token: "AUTHORED-PRIVATE-MAPPING-VALUE",
                                                       "public_control": "PUBLIC-MAPPING-CONTROL"}
                if token == "source_id":
                    # source_id is a supported reference kind at ALL levels,
                    # unlike an arbitrary authored mapping identifier.
                    model["sources"][0]["annotations"]["source_id"] = "SYN-CONTEXT"
                if restricted:
                    model["baseline"]["scenarios"][1]["driver_evidence"]["tokens_per_run"]["internal"] = True
                with self.subTest(token=token, restricted=restricted):
                    report = self.project(model)
                    row = report["scenario_inputs"][1]
                    self.assertIsInstance(row["drivers"], dict)
                    self.assertIsInstance(row["driver_evidence"], dict)
                    self.assertEqual(row["monthly_runs"], ["100"] * 12)
                    self.assertIn("owners", report["profile"])
                    month = report["scenarios"]["expected"]["months"][0]
                    self.assertEqual(month["lines"][1]["cost"]["amount"], "10.00")
                    if not restricted:
                        self.assertEqual(month["total"]["amount"], "110.00")
                    else:
                        self.assertEqual(month["total"]["status"], "withheld")
                    annotations = report["evidence"]["sources"][0]["annotations"]
                    if token == "source_id":
                        self.assertEqual(annotations["source_id"], "SYN-CONTEXT")
                    else:
                        self.assertNotIn(token, annotations)
                    for text in self.serialisations(report):
                        self.assertNotIn("AUTHORED-PRIVATE-MAPPING-VALUE", text)

    def test_protocol_container_and_authored_driver_key_with_same_name_are_distinct(self):
        model = example()
        model["sources"].append({**model["sources"][0], "id": "drivers", "internal": True})
        for scenario in model["baseline"]["scenarios"]:
            scenario["drivers"]["drivers"] = scenario["drivers"].pop("tokens_per_run")
            scenario["driver_evidence"]["drivers"] = scenario["driver_evidence"].pop("tokens_per_run")
        model["baseline"]["lines"][0]["driver_id"] = "drivers"
        report = self.project(model)
        self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
        for row in report["scenario_inputs"]:
            self.assertIn("drivers", row)  # trusted protocol container
            self.assertNotIn("drivers", row["drivers"])  # authored identifier
            self.assertNotIn("drivers", row["driver_evidence"])

    def test_authored_dotted_keys_cannot_spoof_trusted_financial_schema_positions(self):
        model = example()
        model["sources"].append({**model["sources"][0], "id": "PRIVATE-DOTTED-TOKEN", "internal": True})
        model["profile"]["outcome.unit"] = "PRIVATE-DOTTED-TOKEN"
        model["sources"][0]["annotations"] = {"rates[0].amount": "PRIVATE-DOTTED-TOKEN"}
        report = self.project(model)
        for text in self.serialisations(report):
            self.assertNotIn("PRIVATE-DOTTED-TOKEN", text)
        self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")

    def test_incomplete_nested_driver_containers_remain_unavailable_not_reconstructed(self):
        model = example()
        model["baseline"]["scenarios"][1]["drivers"] = None
        model["baseline"]["scenarios"][1]["driver_evidence"] = None
        report = self.project(model)
        self.assertIsNone(report["scenario_inputs"][1]["drivers"])
        self.assertIsNone(report["scenario_inputs"][1]["driver_evidence"])
        self.assertIsNone(report["scenarios"]["expected"]["months"][0]["total"]["amount"])
        self.assertFalse(report["handover"]["ready"])

    def test_contract_accepted_nullable_containers_project_purely_with_explicit_partial_state(self):
        kinds = ("scenarios", "sources", "rates", "fx", "lines", "baseline", "profile",
                 "annualisation", "confidence", "assumptions", "exclusions", "risks")
        for kind in kinds:
            model = nullable_model(kind)
            calculated = self.calculated(model)
            before = copy.deepcopy(calculated)
            self.calc.validate_receipt(calculated, **ACK)
            with self.subTest(kind=kind):
                report = self.projection.project(calculated, **ACK, audience="customer")
                self.assertIn(report["status"], {"partial", "withheld"})
                self.assertFalse(report["handover"]["ready"])
                self.assertEqual(calculated, before)
                self.projection.render_markdown(report)
                if kind in {"sources", "fx"}:
                    self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
                if kind == "scenarios":
                    self.assertEqual(report["scenarios"], {})
                    self.assertEqual(report["scenario_inputs"], [])

    def test_malformed_container_types_are_not_normalised_to_empty(self):
        for kind in ("scenarios", "sources", "rates", "fx", "baseline", "profile"):
            for bad in (False, 0, "invalid", [] if kind in {"baseline", "profile"} else {}):
                model = example()
                if kind == "scenarios":
                    model["baseline"][kind] = bad
                else:
                    model[kind] = bad
                with self.subTest(kind=kind, bad=bad), self.assertRaises(ValueError):
                    self.calc.calculate(model, **ACK)

    def test_required_evidence_null_absent_empty_and_blank_are_equally_fail_closed(self):
        for key in ("tokens_per_run", "operations_units", "monthly_runs", "success_share", "outcomes_per_success"):
            for shape in ("null", "absent", "empty", "blank", "missing-container"):
                model = example()
                scenario = model["baseline"]["scenarios"][1]
                secret = "0.987654321" if key == "success_share" else "987654.321"
                if key == "monthly_runs":
                    scenario[key] = [secret] * 12
                elif key in ("success_share", "outcomes_per_success"):
                    scenario[key] = secret
                else:
                    scenario["drivers"][key] = secret
                evidence = scenario["driver_evidence"]
                if shape == "absent":
                    del evidence[key]
                elif shape == "missing-container":
                    scenario["driver_evidence"] = None
                else:
                    evidence[key] = {"null": None, "empty": {},
                                     "blank": {"unit": " ", "source_id": " ", "sharingClassification": " "}}[shape]
                with self.subTest(key=key, shape=shape):
                    report = self.project(model)
                    for text in self.serialisations(report):
                        self.assertNotIn(secret, text)
                        self.assertNotIn(self.model.model_fingerprint(model), text)
                    self.assertFalse(report["handover"]["ready"])
                    self.assertEqual(report["handover"]["status"], "withheld")
                    month = report["scenarios"]["expected"]["months"][0]
                    if key in ("tokens_per_run", "monthly_runs") and shape != "missing-container":
                        self.assertEqual(month["lines"][1]["cost"]["amount"], "10.00")
                    if key in ("success_share", "outcomes_per_success") and shape != "missing-container":
                        self.assertEqual(month["total"]["amount"], "110.00")

    def test_required_outcome_and_rate_sharing_gaps_are_not_public_metadata(self):
        for kind in ("outcome", "rate"):
            for shape in ("null", "absent", "empty", "blank"):
                model = example()
                if kind == "outcome":
                    model["baseline"]["scenarios"][1]["outcomes_per_success"] = "987654.321"
                    if shape == "absent":
                        del model["profile"]["outcome"]
                    else:
                        model["profile"]["outcome"] = {"null": None, "empty": {}, "blank": {
                            "definition": " ", "unit": " ", "source_id": " ", "sharingClassification": " "}}[shape]
                else:
                    model["rates"][0]["amount"] = "987654.321"
                    if shape == "absent":
                        del model["rates"][0]["sharingClassification"]
                    else:
                        model["rates"][0]["sharingClassification"] = None if shape in ("null", "empty") else " "
                with self.subTest(kind=kind, shape=shape):
                    report = self.project(model)
                    for text in self.serialisations(report):
                        self.assertNotIn("987654.321", text)
                    month = report["scenarios"]["expected"]["months"][0]
                    self.assertEqual(month["lines"][1]["cost"]["amount"], "10.00")
                    if kind == "outcome":
                        self.assertEqual(month["total"]["amount"], "110.00")

    def test_missing_customer_scope_export_gap_withholds_only_affected_dependencies(self):
        model = example()
        model["rates"][0].update(sharingClassification="customer-specific", customer_scope=None)
        report = self.project(model)
        self.assertEqual(report["handover"]["status"], "withheld")
        self.assertEqual(report["scenarios"]["expected"]["months"][0]["total"]["status"], "withheld")
        self.assertEqual(report["scenarios"]["expected"]["months"][0]["lines"][1]["cost"]["amount"], "10.00")

    def test_reports_keep_all_current_calculator_diagnostics_including_period_coverage(self):
        for kind in ("period", "applicability"):
            model = simulated()
            if kind == "period":
                model["rates"][0]["effective_to"] = "2026-12-31"
            else:
                model["sources"][0]["applicability"].remove("rate")
            calculated = self.calculated(model)
            before = copy.deepcopy(calculated)
            calc_gaps = calculated["results"]["gaps"]
            authored_gaps = self.model.validate_model(model, as_of=DAY)
            extra = [gap for gap in calc_gaps if gap not in authored_gaps]
            self.assertTrue(extra, "Fixture must exercise calculator-only diagnostics")
            for audience in ("internal", "customer"):
                with self.subTest(kind=kind, audience=audience):
                    report = self.projection.project(calculated, **ACK, audience=audience)
                    self.assertTrue(report["gaps"])
                    self.assertTrue({g["code"] for g in extra} <= {g["code"] for g in report["gaps"]})
                    if audience == "internal":
                        self.assertEqual(report["gaps"], calc_gaps)
                    self.assertIsNone(report["scenarios"]["expected"]["annual_recurring"]["amount"])
                    self.assertFalse(report["handover"]["ready"])
                    self.assertIn(extra[0]["code"], self.projection.render_markdown(report))
                    self.assertEqual(calculated, before)

    def test_report_gap_merge_keeps_period_and_block_context_with_consumer_cycles(self):
        model = simulated()
        model["rates"][0]["effective_to"] = "2026-12-31"
        model["sources"].extend([
            {**model["sources"][0], "id": "GAP-CYCLE-A", "src": ["GAP-CYCLE-B"]},
            {**model["sources"][0], "id": "GAP-CYCLE-B", "content_src": ["GAP-CYCLE-A"]},
        ])
        calculated = self.calculated(model)
        period_gaps = [g for g in calculated["results"]["gaps"] if g["code"] == "rate-period-unavailable"]
        self.assertGreater(len(period_gaps), 1)
        report = self.projection.project(calculated, **ACK, audience="internal")
        for gap in period_gaps:
            self.assertIn(gap, report["gaps"])
        self.assertIn("source-ancestry-cycle", {g["code"] for g in report["gaps"]})
        duplicate = copy.deepcopy(period_gaps[0])
        different_blocks = {**duplicate, "blocks": ["handover", "customer-export"]}
        with mock.patch.object(self.projection, "_source_cycle_gaps",
                               return_value=[duplicate, different_blocks]):
            merged = self.projection.project(calculated, **ACK, audience="internal")["gaps"]
        self.assertEqual(merged.count(duplicate), 1)
        self.assertIn(different_blocks, merged)
        self.assertTrue(all(g in merged for g in period_gaps))

    def test_singular_plural_technical_registry_families_share_one_privacy_policy(self):
        digest = "faced123" * 8
        families = ("fingerprint", "fingerprints", "hash", "hashes", "digest", "digests",
                    "sha256", "source_fingerprint", "source_fingerprints", "source_hashes", "source_digests")
        for family in families:
            for shape in ({digest: True}, [digest], {"nested": [{"value": digest}]}, {"nested": {digest: False}}):
                model = example()
                model["provenance"] = {family: shape}
                model["sources"][0]["annotations"] = {f"embedded-key/{digest}": f"copied/{digest}/value"}
                report = self.project(model)
                with self.subTest(family=family, shape=shape):
                    for text in self.serialisations(report):
                        self.assertNotIn(digest, text)
                    self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
                    self.assertEqual(report["evidence"]["rates"][1]["amount"], "10")

    def test_private_review_id_and_evidence_aliases_in_public_notes_are_withheld(self):
        model = simulated()
        model["sources"][0]["annotation"] = "Quoted PRIVATE-REVIEW-TOKEN and private:review/evidence references."
        _, snapshot = self.snapshot(model)
        review = self.review(snapshot, id="PRIVATE-REVIEW-TOKEN", sharingClassification="internal-only",
                             evidence_ref="private:review/evidence")
        report = self.projection.project(snapshot, [review], **ACK, audience="customer")
        for text in self.serialisations(report):
            self.assertNotIn("PRIVATE-REVIEW-TOKEN", text)
            self.assertNotIn("private:review/evidence", text)
        self.assertEqual(report["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")

    def test_link_and_currency_dto_scalars_are_null_not_withheld_objects_on_id_collision(self):
        model = example()
        model["rates"][0].update(id="CHF", internal=True)
        model["baseline"]["lines"][0].update(id="D3-A05", rate_id="CHF")
        report = self.project(model)
        self.assertTrue(report["agent_id"] is None or isinstance(report["agent_id"], str))
        self.assertTrue(report["currency"] is None or isinstance(report["currency"], str))


class CLITests(IOCase):
    def test_no_ack_does_not_even_read_inputs_or_create_output(self):
        out = self.dir / "absent/out.json"
        result = self.run_cli("seed", "--blueprint", self.dir / "missing.json", "--agent-id", "D3-A05",
                              "--out", out, "--as-of", DAY)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Preview", result.stderr)
        self.assertNotIn("missing.json", result.stderr)
        self.assertFalse(out.parent.exists())

    def test_real_cli_seed_calculate_freeze_review_export_apply_on_copies(self):
        common = ("--as-of", DAY, "--acknowledge-finops-preview")
        seed = self.dir / "seed.json"
        result = self.run_cli("seed", "--blueprint", BP, "--agent-id", "D3-A05", "--out", seed, *common)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "partial")
        raw = self.write("input.json", example())
        calculated = self.dir / "calculated.json"
        result = self.run_cli("calculate", "--baseline", raw, "--out", calculated, *common)
        self.assertEqual(result.returncode, 0, result.stderr)
        before = calculated.read_bytes()
        frozen = self.dir / "frozen"
        result = self.run_cli("freeze", "--baseline", calculated, "--out-dir", frozen, *common)
        self.assertEqual(result.returncode, 0, result.stderr)
        snapshot_path = next(frozen.glob("*.json"))
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        review = self.write("review-input.json", review_for(snapshot))
        result = self.run_cli("record-review", "--baseline", snapshot_path, "--review", review,
                              "--out-dir", self.dir / "reviews", *common)
        self.assertEqual(result.returncode, 0, result.stderr)
        review_path = next((self.dir / "reviews").glob("*.json"))
        result = self.run_cli("export", "--baseline", snapshot_path, "--review", review_path,
                              "--out-dir", self.dir / "export", "--audience", "customer", *common)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.dir / "export/report.json").read_text(encoding="utf-8"))
        self.assertEqual((self.dir / "export/report.md").read_text(encoding="utf-8"),
                         self.projection.render_markdown(report))
        applied = self.dir / "applied.json"
        # A positive customer apply needs public/scoped input. The stock
        # Blueprint contains internal E04 ancestry and must now be withheld.
        public_bp = self.write("public-apply.json", seed_blueprint())
        result = self.run_cli("apply", "--blueprint", public_bp, "--baseline", calculated,
                              "--out", applied, "--audience", "customer", "--customer-scope", "caldova-scope", *common)
        self.assertEqual(result.returncode, 0, result.stderr)
        dto = json.loads(applied.read_text(encoding="utf-8"))["agent_finops"]
        self.assertEqual(dto["schema"], "frontier-agent-finops-view/1.0")
        self.assertEqual(dto["records"][0]["agent_id"], "D3-A05")
        self.assertEqual(calculated.read_bytes(), before)
        self.assertNotIn("1320", result.stdout)
        self.assertNotIn("SYN-", result.stdout)

    def test_apply_preflights_every_input_rejects_duplicates_unknown_and_legacy(self):
        model = self.write("model.json", self.calculated())
        common = ("--as-of", DAY, "--acknowledge-finops-preview", "--audience", "customer")
        for bp, baselines in ((blueprint(), [model, model]),
                              ({**blueprint(), "finops": {}}, [model]),
                              ({**blueprint(), "agent_finops": {}}, [model]),
                              ({**blueprint(), "domains": []}, [model]),
                              (blueprint(), [model, self.write("bad.json", {"schema": "unknown"})])):
            path = self.write("bp.json", bp)
            out = self.dir / "no/output.json"
            result = self.run_cli("apply", "--blueprint", path, "--out", out,
                                  *[v for b in baselines for v in ("--baseline", b)], *common)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(out.parent.exists())

    def test_expected_cli_failures_are_bounded_no_input_overwrite(self):
        source = self.write("input.json", self.calculated())
        original = source.read_bytes()
        common = ("--as-of", DAY, "--acknowledge-finops-preview")
        result = self.run_cli("calculate", "--baseline", source, "--out", source, *common)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(source.read_bytes(), original)
        bad = self.dir / "bad.json"
        bad.write_text('{"PRIVATE-SENTINEL":invalid}', encoding="utf-8")
        result = self.run_cli("calculate", "--baseline", bad, "--out", self.dir / "no/out.json", *common)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("PRIVATE-SENTINEL", result.stderr)
        self.assertFalse((self.dir / "no").exists())
        help_result = self.run_cli("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("record-review", help_result.stdout)

    def test_main_returns_two_and_migration_refuses_same_input_path(self):
        stderr, stdout = io.StringIO(), io.StringIO()
        with redirect_stderr(stderr), redirect_stdout(stdout):
            result = self.cli.main(["calculate", "--baseline", "absent", "--out", "absent",
                                    "--as-of", DAY.isoformat()])
        self.assertEqual(result, 2)
        self.assertEqual(stdout.getvalue(), "")
        legacy = self.write("legacy.json", {"schema": "frontier-finops/1.0"})
        before = legacy.read_bytes()
        result = self.run_cli("migrate", "--baseline", legacy, "--blueprint", BP, "--agent-id", "D3-A05",
                              "--out", legacy, "--as-of", DAY, "--acknowledge-finops-preview")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(legacy.read_bytes(), before)

    def test_all_cli_commands_require_ack_before_reads(self):
        common = ["--as-of", DAY, "--baseline", self.dir / "missing"]
        variants = [
            ["migrate", *common, "--blueprint", BP, "--agent-id", "D3-A05", "--out", self.dir / "no/x"],
            ["calculate", *common, "--out", self.dir / "no/x"],
            ["freeze", *common, "--out-dir", self.dir / "no"],
            ["record-review", *common, "--review", self.dir / "missing", "--out-dir", self.dir / "no"],
            ["apply", *common, "--blueprint", BP, "--audience", "customer", "--out", self.dir / "no/x"],
            ["export", *common, "--audience", "customer", "--out-dir", self.dir / "no"],
        ]
        for args in variants:
            with self.subTest(command=args[0]):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Preview", result.stderr)
                self.assertNotIn("missing", result.stderr)
                self.assertFalse((self.dir / "no").exists())

    def test_cli_rejects_duplicate_json_keys_and_malformed_review_without_tracebacks(self):
        model = self.write("model.json", self.calculated())
        common = ("--as-of", DAY, "--acknowledge-finops-preview")
        ambiguous = self.dir / "ambiguous.json"
        text = model.read_text(encoding="utf-8")
        ambiguous.write_text('{"schema":"unknown",' + text[1:], encoding="utf-8")
        result = self.run_cli("calculate", "--baseline", ambiguous, "--out", self.dir / "no/x", *common)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.dir / "no").exists())
        snapshot_path, snapshot = self.snapshot(simulated())
        bad = self.write("review.json", review_for(snapshot, decision=[]))
        result = self.run_cli("record-review", "--baseline", snapshot_path, "--review", bad,
                              "--out-dir", self.dir / "no", *common)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_apply_keeps_value_case_and_rejects_unused_reviews_before_output(self):
        bp = blueprint()
        bp["value_case"] = {"sentinel": "ordinary-value-unchanged", "amount": 123}
        original = copy.deepcopy(bp)
        result = self.cli.apply_models(bp, [self.calculated()], **ACK, audience="internal")
        self.assertEqual(bp, original)
        self.assertEqual(result["value_case"], bp["value_case"])
        with self.assertRaises(ValueError):
            self.cli.apply_models(bp, [self.calculated()], [{"baseline_id": "unused", "version": 1}],
                                  **ACK, audience="internal")

    def test_blueprint_ancestry_private_source_cannot_publish_new_financial_record(self):
        for location in ("root", "domain", "agent", "source"):
            bp = blueprint()
            domain = next(d for d in bp["domains"] if any(a["id"] == "D3-A05" for a in d["agents"]))
            agent = next(a for a in domain["agents"] if a["id"] == "D3-A05")
            private = (bp if location == "root" else domain if location == "domain" else agent
                       if location == "agent" else next(s for s in bp["evidence"] if s["id"] == "E05"))
            private["internal"] = True
            result = self.cli.apply_models(bp, [self.calculated()], **ACK, audience="customer")
            record = result["agent_finops"]["records"][0]
            with self.subTest(location=location):
                self.assertEqual(record["status"], "withheld")
                self.assertNotIn("1320.00", json.dumps(record))

    def test_cli_exports_private_summary_without_any_private_prices_or_ids(self):
        model = example()
        model["rates"][0].update(id="PRIVATE-RATE-ID", internal=True, note="PRIVATE-NOTE")
        model["baseline"]["lines"][0]["rate_id"] = "PRIVATE-RATE-ID"
        calculated = self.write("private.json", self.calculated(model))
        result = self.run_cli("export", "--baseline", calculated, "--out-dir", self.dir / "exports",
                              "--audience", "customer", "--as-of", DAY, "--acknowledge-finops-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        for text in (result.stdout, result.stderr, (self.dir / "exports/report.json").read_text(encoding="utf-8"),
                     (self.dir / "exports/report.md").read_text(encoding="utf-8")):
            self.assertNotIn("PRIVATE-RATE-ID", text)
            self.assertNotIn("PRIVATE-NOTE", text)

    def test_cli_migrates_to_new_draft_without_reusing_legacy_currency_or_mutating_input(self):
        legacy = self.write("legacy.json", {"schema": "frontier-finops/1.0", "currency": "USD",
                                          "status": "approved", "results": {"total": 9999}})
        before = legacy.read_bytes()
        result = self.run_cli("migrate", "--baseline", legacy, "--blueprint", BP, "--agent-id", "D3-A05",
                              "--out", self.dir / "draft.json", "--as-of", DAY, "--acknowledge-finops-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "partial")
        draft = json.loads((self.dir / "draft.json").read_text(encoding="utf-8"))
        self.assertIsNone(draft["baseline"]["currency"])
        self.assertNotIn("results", draft)
        self.assertEqual(legacy.read_bytes(), before)

    def test_apply_malformed_blueprint_privacy_is_explicit_valueerror(self):
        for patch in ({"internal": 1}, {"sharingClassification": []}, {"visibility": []}):
            bp = {**blueprint(), **patch}
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.cli.apply_models(bp, [self.calculated()], **ACK, audience="customer")
        bp = {**blueprint(), "sharingClassification": None}
        report = self.cli.apply_models(bp, [self.calculated()], **ACK, audience="customer")["agent_finops"]["records"][0]
        self.assertEqual(report["status"], "withheld")

    def test_cli_customer_export_obeys_transitive_source_id_privacy(self):
        bp = seed_blueprint()
        agent = next(a for d in bp["domains"] for a in d["agents"] if a["id"] == "D3-A05")
        agent["src"] = ["GRAPH-CHILD"]
        agent["canvas"]["instructions"] = "CLI-TRANSITIVE-PRIVATE-CANVAS"
        bp["evidence"].extend([
            {**bp["evidence"][0], "id": "GRAPH-CHILD", "source_id": "GRAPH-PARENT"},
            {**bp["evidence"][0], "id": "GRAPH-PARENT", "sharingClassification": "internal-only"},
        ])
        source = self.write("blueprint.json", bp)
        draft, calculated = self.dir / "draft.json", self.dir / "calculated.json"
        common = ("--as-of", DAY, "--acknowledge-finops-preview")
        for args in (("seed", "--blueprint", source, "--agent-id", "D3-A05", "--out", draft),
                     ("calculate", "--baseline", draft, "--out", calculated),
                     ("export", "--baseline", calculated, "--out-dir", self.dir / "export",
                      "--audience", "customer", "--customer-scope", "caldova-scope")):
            result = self.run_cli(*args, *common)
            self.assertEqual(result.returncode, 0, result.stderr)
        for path in (self.dir / "export/report.json", self.dir / "export/report.md"):
            self.assertNotIn("CLI-TRANSITIVE-PRIVATE-CANVAS", path.read_text(encoding="utf-8"))

    def test_cli_customer_exports_redact_key_only_digest_registry_aliases(self):
        digest = "abc90123" * 8
        model = example()
        model["provenance"] = {"source_hashes": {digest: True}}
        model["sources"][0]["annotations"] = {digest: f"copied digest {digest}"}
        source = self.write("calculated.json", self.calculated(model))
        result = self.run_cli("export", "--baseline", source, "--out-dir", self.dir / "export",
                              "--audience", "customer", "--as-of", DAY, "--acknowledge-finops-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in (self.dir / "export/report.json", self.dir / "export/report.md"):
            self.assertNotIn(digest, path.read_text(encoding="utf-8"))

    def test_cli_private_fixed_key_collisions_export_valid_partial_reports(self):
        for i, token in enumerate(("drivers", "driver_evidence", "monthly_runs", "amount")):
            for restricted in (False, True):
                model = example()
                model["sources"].append({**model["sources"][0], "id": token, "internal": True})
                if restricted:
                    model["baseline"]["scenarios"][1]["driver_evidence"]["tokens_per_run"]["internal"] = True
                source = self.write(f"input-{i}-{restricted}.json", self.calculated(model))
                out = self.dir / f"export-{i}-{restricted}"
                result = self.run_cli("export", "--baseline", source, "--out-dir", out, "--audience", "customer",
                                      "--as-of", DAY, "--acknowledge-finops-preview")
                with self.subTest(token=token, restricted=restricted):
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)
                    self.assertEqual(json.loads(result.stdout)["status"], "partial")
                    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
                    self.assertIn("drivers", report["scenario_inputs"][1])
                    self.assertEqual(report["scenarios"]["expected"]["months"][0]["lines"][1]["cost"]["amount"], "10.00")

    def test_cli_customer_export_withholds_quantities_with_null_or_absent_evidence(self):
        for i, shape in enumerate(("null", "absent", "empty", "missing-container")):
            model = example()
            scenario = model["baseline"]["scenarios"][1]
            scenario["drivers"]["tokens_per_run"] = "987654.321"
            if shape == "absent":
                del scenario["driver_evidence"]["tokens_per_run"]
            elif shape == "missing-container":
                del scenario["driver_evidence"]
            else:
                scenario["driver_evidence"]["tokens_per_run"] = None if shape == "null" else {}
            source = self.write(f"missing-{i}.json", self.calculated(model))
            out = self.dir / f"export-{i}"
            result = self.run_cli("export", "--baseline", source, "--out-dir", out, "--audience", "customer",
                                  "--as-of", DAY, "--acknowledge-finops-preview")
            self.assertEqual(result.returncode, 0, result.stderr)
            for path in (out / "report.json", out / "report.md"):
                self.assertNotIn("987654.321", path.read_text(encoding="utf-8"))

    def test_cli_customer_export_recognises_bare_plural_fingerprints_registry(self):
        digest = "deaf1234" * 8
        model = example()
        model["provenance"] = {"fingerprints": {digest: True}}
        model["sources"][0]["annotation"] = f"embedded digest {digest}"
        source = self.write("plural.json", self.calculated(model))
        out = self.dir / "plural-export"
        result = self.run_cli("export", "--baseline", source, "--out-dir", out, "--audience", "customer",
                              "--as-of", DAY, "--acknowledge-finops-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in (out / "report.json", out / "report.md"):
            self.assertNotIn(digest, path.read_text(encoding="utf-8"))

    def test_cli_json_and_markdown_keep_forecast_rate_coverage_diagnostics(self):
        model = simulated()
        model["rates"][0]["effective_to"] = "2026-12-31"
        source = self.write("coverage.json", self.calculated(model))
        before = source.read_bytes()
        for audience in ("internal", "customer"):
            out = self.dir / f"coverage-{audience}"
            result = self.run_cli("export", "--baseline", source, "--out-dir", out, "--audience", audience,
                                  "--as-of", DAY, "--acknowledge-finops-preview")
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((out / "report.json").read_text(encoding="utf-8"))
            self.assertIn("rate-period-unavailable", {g["code"] for g in report["gaps"]})
            self.assertIn("rate-period-unavailable", (out / "report.md").read_text(encoding="utf-8"))
            self.assertIsNone(report["scenarios"]["expected"]["annual_recurring"]["amount"])
            self.assertFalse(report["handover"]["ready"])
        self.assertEqual(source.read_bytes(), before)

    def test_cli_exports_contract_accepted_null_containers_without_tracebacks(self):
        for kind in ("scenarios", "sources", "rates", "fx", "lines", "baseline", "profile"):
            source = self.write(f"nullable-{kind}.json", self.calculated(nullable_model(kind)))
            before = source.read_bytes()
            out = self.dir / f"nullable-export-{kind}"
            result = self.run_cli("export", "--baseline", source, "--out-dir", out, "--audience", "customer",
                                  "--as-of", DAY, "--acknowledge-finops-preview")
            with self.subTest(kind=kind):
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], "partial")
                self.assertEqual(source.read_bytes(), before)
                self.assertTrue((out / "report.json").is_file())
                self.assertTrue((out / "report.md").is_file())

    def test_cli_direct_model_cycle_export_is_partial_and_keeps_independent_public_cost(self):
        model = simulated()
        model["sources"].extend([
            {**model["sources"][0], "id": "CYCLE-A", "src": ["CYCLE-B"]},
            {**model["sources"][0], "id": "CYCLE-B", "content_src": ["CYCLE-A"]},
        ])
        model["rates"][0]["source_id"] = "CYCLE-A"
        source = self.write("cycle-model.json", self.calculated(model))
        before = source.read_bytes()
        out = self.dir / "cycle-export"
        result = self.run_cli("export", "--baseline", source, "--out-dir", out, "--audience", "customer",
                              "--as-of", DAY, "--acknowledge-finops-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((out / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["scenarios"]["expected"]["months"][0]["total"]["status"], "withheld")
        self.assertEqual(report["scenarios"]["expected"]["months"][0]["lines"][1]["cost"]["amount"], "10.00")
        self.assertEqual(source.read_bytes(), before)

    def test_apply_nullable_profile_refuses_known_agent_link_with_valueerror(self):
        with self.assertRaises(ValueError):
            self.cli.apply_models(seed_blueprint(), [self.calculated(nullable_model("profile"))],
                                  **ACK, audience="customer", customer_scope="caldova-scope")
        result = self.cli.apply_models(seed_blueprint(), [self.calculated(nullable_model("baseline"))],
                                      **ACK, audience="customer", customer_scope="caldova-scope")
        self.assertFalse(result["agent_finops"]["records"][0]["handover"]["ready"])

    def test_apply_reuses_consumed_blueprint_closure_not_standalone_baseline_privacy(self):
        for private in (False, True):
            bp = seed_blueprint()
            agent = next(a for d in bp["domains"] for a in d["agents"] if a["id"] == "D3-A05")
            agent["src"] = ["APPLY-CHILD"]
            bp["evidence"].extend([
                {**bp["evidence"][0], "id": "APPLY-CHILD", "provenance": {"source_id": "APPLY-PARENT"}},
                {**bp["evidence"][0], "id": "APPLY-PARENT",
                 "sharingClassification": "internal-only" if private else "customer-shareable"},
                {**bp["evidence"][0], "id": "UNRELATED-PRIVATE", "internal": True},
            ])
            before = copy.deepcopy(bp)
            calculated = self.calculated()
            standalone = self.projection.project(calculated, **ACK, audience="customer")
            self.assertEqual(standalone["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
            result = self.cli.apply_models(bp, [calculated], **ACK, audience="customer", customer_scope="caldova-scope")
            record = result["agent_finops"]["records"][0]
            with self.subTest(private=private):
                if private:
                    self.assertEqual(record["status"], "withheld")
                    self.assertNotIn("1320.00", json.dumps(result["agent_finops"]))
                else:
                    self.assertEqual(record["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")
                self.assertEqual(bp, before)

    def test_cli_apply_reuses_nested_source_ancestry_with_public_control(self):
        for private in (False, True):
            bp = seed_blueprint()
            agent = next(a for d in bp["domains"] for a in d["agents"] if a["id"] == "D3-A05")
            agent["content_src"] = ["APPLY-CHILD"]
            bp["evidence"].extend([
                {**bp["evidence"][0], "id": "APPLY-CHILD", "provenance": {"source_id": "APPLY-PARENT"}},
                {**bp["evidence"][0], "id": "APPLY-PARENT",
                 "sharingClassification": "internal-only" if private else "customer-shareable"},
            ])
            source = self.write(f"bp-{private}.json", bp)
            model = self.write(f"model-{private}.json", self.calculated())
            output = self.dir / f"apply-{private}.json"
            result = self.run_cli("apply", "--blueprint", source, "--baseline", model, "--out", output,
                                  "--audience", "customer", "--customer-scope", "caldova-scope",
                                  "--as-of", DAY, "--acknowledge-finops-preview")
            self.assertEqual(result.returncode, 0, result.stderr)
            dto = json.loads(output.read_text(encoding="utf-8"))["agent_finops"]
            if private:
                self.assertNotIn("1320.00", json.dumps(dto))
                self.assertEqual(dto["records"][0]["status"], "withheld")
            else:
                self.assertEqual(dto["records"][0]["scenarios"]["expected"]["annual_recurring"]["amount"], "1320.00")


if __name__ == "__main__":
    unittest.main()
