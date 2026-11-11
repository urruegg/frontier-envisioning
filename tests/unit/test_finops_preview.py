"""Per-action Preview gates: old artifacts and installation never grant consent."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load

SKILLS = ROOT / "plugin/skills"
FIN = SKILLS / "frontier-finops"
VAL = SKILLS / "frontier-value-case"
BLUE = SKILLS / "frontier-blueprint"
ACK = "--acknowledge-finops-preview"

# Finite inventory of EXISTING inputs -> constructed numeric/presentation outputs.
# Arrays of numeric purchase tiers/event rates keep their current input types;
# restrictions belong to their existing dictionary container, never a new SKU.
# "first" = affected USD/credit/licence case; independent CHF-only case survives.
COMPONENT_PRIVACY_MATRIX = (
    ("model-root", "fin", "agents/totals/value/replies", "all"),
    ("rates-root", "rates", "rates/agents/comparisons/value/replies", "all"),
    ("agent", "fin.agents[0]", "agent/tags/controls/value/aggregate replies", "first"),
    ("people", "agent.people", "people/build lines/agent/value/replies", "first"),
    ("build", "agent.people", "build/pv-cost/agent/value/replies", "first"),
    ("azure", "agent.azure[0]", "azure line/unit/agent/value/replies", "first"),
    ("licence-selection", "agent.licences[0]", "selected unit/line/rate row/agent/value", "first"),
    ("licence-sku", "rates.licences.M365_COPILOT", "selected SKU label/price/rate row/value", "first"),
    ("licence-container", "rates.licences", "selected SKU lines/rate rows/value", "first"),
    ("capacity-pack", "rates.credits.pack", "pack rate/pack option/comparison prose", "comparison"),
    ("purchase-tiers", "rates.credits", "tier rate/cc-p3/agent-p3/prose + consumed credits", "first"),
    ("fx-model", "fin.fx (explicit selected)", "USD costs/FX rate/agent/value/replies", "first"),
    ("fx-fallback", "rates.fx (only when selected)", "USD costs/FX rate/agent/value/replies", "first"),
    ("usage", "agent.usage", "sessions/events/unit costs/agent/value/replies", "first"),
    ("outcome", "agent.outcome", "outcome name/count/per-outcome only; independent cost/value remains public", "presentation"),
    ("credits", "rates.credits", "PAYG/event costs/rate rows/comparisons/value", "first"),
    ("events", "rates.credits.per_event", "used event rates/credits/unit costs/value", "first"),
    ("event-labels", "rates.credits.event_labels", "used event label/rate presentation only", "presentation"),
    ("assumption", "used ASS-106 (not unused register entries)", "resolved people cost/agent/value/replies", "first"),
    ("scenario", "fin.credit_scenarios[-1]", "scenario amount/name/change + dependent prose", "scenario"),
    ("guardrails", "fin.guardrails", "headroom/alerts/variance control rows", "controls"),
    ("purchase-note", "fin.purchase", "authored purchase display, not unconsumed cost selection", "presentation"),
)


def script(skill, name):
    with mock.patch.object(sys, "path", [str(skill / "scripts"), *sys.path]):
        return load(f"plugin/skills/{skill.name}/scripts/{name}.py", f"preview_{name}")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, doc):
    path.write_text(json.dumps(doc) + "\n", encoding="utf-8", newline="\n")
    return path


class PreviewBoundaries(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fin = read(FIN / "examples/reference-hr-assistant.finops.json")
        self.value = read(VAL / "examples/reference-hr-assistant.value.json")
        self.rates = read(FIN / "rates/rates-2026-11.json")
        self.fc = script(FIN, "finops_calc")
        self.vc = script(VAL, "value_calc")
        self.af = script(FIN, "apply_finops")
        self.av = script(VAL, "apply_value")
        self.mv = script(VAL, "merge_value_feedback")
        self.seed = script(FIN, "seed_finops")
        self.wrapper = script(BLUE, "build_with_identity")
        self.bp = {"meta": {"customer": "Caldova Industrial AG", "short": "Caldova"},
                   "domains": [{"id": "D1", "name": "People", "agents": [{"id": "HR-A01", "name": "HR policy assistant",
                                                       "mvp": True, "technology": "Copilot Studio"}],
                                "use_cases": [{"id": "UC-HR", "agents": ["HR-A01"]}]}]}
        # Assemble an old result using arithmetic helpers, not operational run APIs.
        register = self.fc.register_of(self.value, self.fin)
        agent = self.fc.agent_cost(self.fin["agents"][0], register, self.rates, 0.81)
        totals = {"total_month": agent["total_month"], "credits_month": agent["credits_month"],
                  "lines": agent["lines"], "build": agent["build"], "annual": agent["total_month"] * 12}
        self.fin["results"] = {"agents": [agent], "totals": totals, "fx": 0.81,
                               "purchase_options": [], "credit_scenarios": [], "guardrails": [], "lessons": [], "missing": []}
        self.derived = copy.deepcopy(self.value)
        self.derived["results"] = self.vc.run(self.value, None)
        self.derived["results"]["use_cases"][0]["agents_costed"] = ["HR-A01"]
        self.bpp = write(self.root / "blueprint.json", self.bp)
        self.fp = write(self.root / "finops.json", self.fin)
        self.vp = write(self.root / "value.json", self.value)
        self.dp = write(self.root / "derived.json", self.derived)
        self.fb = write(self.root / "feedback.json", {
            "type": "frontier-blueprint-feedback", "exported": "2026-11-12",
            "validations": {"ass:ASS-003": {"status": "adjusted", "value": 0.3},
                            "ass:ASS-101": {"status": "validated"}}})

    def call(self, module, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = module.main([str(x) for x in args])
        return code, out.getvalue(), err.getvalue()

    def assert_refused(self, module, args, paths):
        before = {p: p.read_bytes() if p.exists() else None for p in paths}
        code, out, err = self.call(module, args)
        self.assertEqual(code, 2, (out, err))
        self.assertIn("Frontier FinOps is Preview", err)
        self.assertIn(ACK, err)
        self.assertEqual(out, "", "A refused cost operation must not print figures")
        for p, content in before.items():
            self.assertEqual(p.read_bytes() if p.exists() else None, content, str(p))

    def test_cli_refuses_each_operational_path_without_writes(self):
        target = self.root / "out.json"
        write(target, {"previous": "good"})
        cases = [
            (self.seed, ["--blueprint", self.bpp, "--out", target], [target]),
            (self.fc, ["--finops", self.fp, "--value", self.vp], [self.fp]),
            (self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--out", target], [target, self.bpp]),
            (self.vc, ["--value", self.vp, "--finops", self.fp], [self.vp]),
            (self.av, ["--blueprint", self.bpp, "--value", self.dp, "--out", target], [target]),
            (self.mv, ["--value", self.vp, "--finops", self.fp, "--feedback", self.fb], [self.vp, self.fp]),
            (self.mv, ["--value", self.dp, "--feedback", self.fb], [self.dp]),
        ]
        for module, args, paths in cases:
            with self.subTest(module=module.__name__, args=args):
                self.assert_refused(module, args, paths)

    def test_cli_refuses_seed_before_creating_output(self):
        target = self.root / "new.json"
        self.assert_refused(self.seed, ["--blueprint", self.bpp, "--out", target], [target])

    def test_api_refuses_model_operations_before_mutation(self):
        register = self.fc.register_of(self.value, self.fin)
        cases = [
            lambda: self.fc.run(self.fin, self.value, self.rates),
            lambda: self.fc.compute(self.fin, register, self.rates),
            lambda: self.af.build_block(self.bp, self.fin, self.rates, self.value),
            lambda: self.vc.run(self.value, self.fin),
            lambda: self.vc.run(self.derived, None),
            lambda: self.av.apply(self.bp, self.derived),
            lambda: self.mv.merge([self.value, self.fin], self.mv.verdicts_from(read(self.fb)), "2026-11-12"),
            lambda: self.mv.merge([self.derived], self.mv.verdicts_from(read(self.fb)), "2026-11-12"),
        ]
        before = copy.deepcopy((self.bp, self.fin, self.value, self.derived))
        for i, action in enumerate(cases):
            with self.subTest(action=i):
                with self.assertRaisesRegex(ValueError, ACK):
                    action()
                self.assertEqual((self.bp, self.fin, self.value, self.derived), before)

    def test_legacy_forged_ga_and_cached_acceptance_do_not_grant_consent(self):
        for marker in ({}, {"maturity": "ga", "acknowledged": True},
                       {"finops_preview": {"maturity": "ga", "acknowledgement": True}},
                       {"preview_acknowledged": True}):
            with self.subTest(marker=marker):
                forged = dict(self.fin, **marker)
                with self.assertRaisesRegex(ValueError, ACK):
                    self.fc.run(forged, self.value, self.rates)

    def test_wrapper_refuses_finops_before_any_side_effect(self):
        target = self.root / "output"
        with mock.patch.object(self.wrapper, "run", return_value=(0, "{}", "")) as child, \
                mock.patch.object(self.wrapper, "build_identity", return_value=self.bpp) as identity:
            self.assert_refused(self.wrapper, [
                "--data", self.bpp, "--out-dir", target, "--finops", self.fp], [target])
            child.assert_not_called()
            identity.assert_not_called()
        self.assertFalse(target.exists())

    def preview(self, result):
        metadata = result["finops_preview"]
        self.assertEqual(metadata["maturity"], "preview")
        self.assertEqual(metadata["grounding_status"], "non-ga-refinement-required")
        self.assertEqual(metadata["model_status"], "non-ga-refinement-required")
        self.assertIn("provisional planning estimates", metadata["notice"])
        self.assertEqual(metadata["acknowledgement"],
                         {"kind": "explicit-caller", "scope": "current-invocation"})
        self.assertIn("inputs", metadata["provenance"])
        self.assertIn("scenario", metadata["provenance"])
        return metadata

    def calculated(self):
        fin = copy.deepcopy(self.fin)
        fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
        return fin

    def test_owned_helper_exact_notice_and_strict_boolean(self):
        self.assertTrue((FIN / "scripts/finops_preview.py").is_file(), "Owned Preview helper is missing")
        helper = script(FIN, "finops_preview")
        notice = ("Frontier FinOps is Preview. Its grounding and cost model are not GA "
                  "and need refinement. Results are provisional planning estimates, not "
                  "validated pricing, budget approval or purchase/commitment advice. "
                  "Verify rates and assumptions independently before decisions.")
        self.assertEqual(helper.NOTICE, notice)
        self.assertTrue(issubclass(helper.FinOpsPreviewError, ValueError))
        for flag in (False, None, 1, "true", {}, {"acknowledged": True}):
            with self.subTest(flag=flag), self.assertRaisesRegex(helper.FinOpsPreviewError, ACK):
                helper.require_preview_ack(flag)
        accepted = helper.require_preview_ack(True)
        self.assertEqual(accepted["notice"], notice)
        self.assertEqual(accepted["acknowledgement"]["scope"], "current-invocation")

    def test_seed_api_and_summary_keep_preview(self):
        self.assertTrue(hasattr(self.seed, "seed"), "Seed model API must also guard caller acknowledgement")
        with self.assertRaisesRegex(ValueError, ACK):
            self.seed.seed(self.bp, self.value)
        seeded = self.seed.seed(self.bp, self.value, acknowledge_finops_preview=True)
        meta = self.preview(seeded)
        self.assertEqual(meta["provenance"]["inputs"]["finops"]["schema"], "frontier-finops/1.0")
        self.assertEqual(meta["provenance"]["inputs"]["finops"]["version"], "0.1")
        target = self.root / "seeded.json"
        code, out, err = self.call(self.seed, ["--blueprint", self.bpp, "--value", self.vp, "--out", target, ACK])
        self.assertEqual(code, 0, err)
        self.preview(read(target))
        self.preview(json.loads(out))

    def test_explicit_run_preserves_all_worked_example_numbers(self):
        fin = self.calculated()
        res = fin["results"]
        meta = self.preview(res)
        inputs = meta["provenance"]["inputs"]
        self.assertEqual(inputs["rates"]["version"], self.rates["version"])
        self.assertEqual(inputs["rates"]["schema"], self.rates["schema"])
        self.assertEqual(len(inputs["rates"]["fingerprint"]), 64)
        self.assertEqual(inputs["value"]["version"], self.value["version"])
        self.assertTrue(meta["provenance"]["sources"])
        agent = res["agents"][0]
        options = {o["option"]: o for o in res["purchase_options"]}
        self.assertEqual(round(agent["credits_month"]), 81780)
        self.assertAlmostEqual(agent["lines"]["credits"], 662.42, delta=0.01)
        self.assertAlmostEqual(agent["total_month"], 2582.42, delta=0.01)
        self.assertAlmostEqual(options["packs"]["annual_chf"], 7776.0, delta=0.01)
        self.assertAlmostEqual(options["cc-p3"]["annual_chf"], 7827.52, delta=0.01)
        self.assertEqual([round(x["credits_month"]) for x in res["credit_scenarios"]],
                         [136300, 27260, 18780, 163560])
        self.assertAlmostEqual(agent["unit"]["per_session"], 0.26, delta=0.005)
        self.assertAlmostEqual(agent["unit"]["per_outcome"], 1.03, delta=0.005)
        for option in options.values():
            self.assertEqual(option["assessment"], "provisional-comparison-not-recommendation")
        value = self.vc.run(self.value, fin, acknowledge_finops_preview=True)
        self.preview(value)
        row = value["use_cases"][0]
        self.preview(row)
        self.assertAlmostEqual(row["npv"], 540413, delta=1.0)
        self.assertAlmostEqual(row["roi"], 5.20, delta=0.005)
        self.assertAlmostEqual(row["payback_months"], 1.3, delta=0.05)
        self.assertAlmostEqual(row["break_even"]["value"], 0.031, delta=0.0005)

    def test_pure_arithmetic_helpers_need_no_acknowledgement(self):
        register = self.fc.register_of(self.value, self.fin)
        agent = self.fc.agent_cost(self.fin["agents"][0], register, self.rates, 0.81)
        self.assertAlmostEqual(agent["total_month"], 2582.42, delta=0.01)
        row = self.vc.uc_eval(self.value["use_cases"][0], register, self.value, self.fin["results"])
        self.assertAlmostEqual(row["npv"], 540413, delta=1.0)
        self.assertEqual(self.fc.purchase_options(81780, 0, self.rates, 0.81)[1]["annual_chf"], 7776)

    def test_each_new_invocation_and_input_version_needs_fresh_ack(self):
        fin = self.calculated()
        for change in ("none", "model", "rates", "scenario", "scope"):
            model, rates = copy.deepcopy(fin), copy.deepcopy(self.rates)
            if change == "model":
                model["version"] = "2.0"
            elif change == "rates":
                rates["version"] = "2026-11-12"
                rates["credits"]["payg_usd_per_credit"] *= 2
            elif change == "scenario":
                model["credit_scenarios"][0]["set"]["licensed_share"] = 0.1
            elif change == "scope":
                model["agents"][0]["id"] = "HR-A02"
            with self.subTest(change=change):
                with self.assertRaisesRegex(ValueError, ACK):
                    self.fc.run(model, self.value, rates)
                new = self.fc.run(model, self.value, rates, acknowledge_finops_preview=True)
                self.preview(new)
                if change in ("model", "scenario", "scope"):
                    self.assertNotEqual(new["finops_preview"]["provenance"]["inputs"]["finops"]["fingerprint"],
                                        fin["results"]["finops_preview"]["provenance"]["inputs"]["finops"]["fingerprint"])
                if change == "rates":
                    self.assertNotEqual(new["finops_preview"]["provenance"]["inputs"]["rates"]["fingerprint"],
                                        fin["results"]["finops_preview"]["provenance"]["inputs"]["rates"]["fingerprint"])

    def test_accepted_cli_chain_labels_every_json_and_cost_reply(self):
        cases = [
            (self.fc, ["--finops", self.fp, "--value", self.vp, ACK], self.fp),
            (self.vc, ["--value", self.vp, "--finops", self.fp, ACK], self.vp),
            (self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--value", self.vp,
                       "--out", self.bpp, "--today", "2026-11-11", ACK], self.bpp),
            (self.av, ["--blueprint", self.bpp, "--value", self.vp, "--out", self.bpp, ACK], self.bpp),
        ]
        for module, args, target in cases:
            with self.subTest(module=module.__name__):
                code, out, err = self.call(module, args)
                self.assertEqual(code, 0, err)
                self.preview(json.loads(out))
                doc = read(target)
                if module is self.fc or module is self.vc:
                    self.preview(doc)
                    self.preview(doc["results"])
                elif module is self.af:
                    self.preview(doc["finops"])
                else:
                    self.preview(doc["value_case"])
                    self.preview(doc["domains"][0]["use_cases"][0]["business_value"])
        self.assert_refused(self.fc, ["--finops", self.fp, "--value", self.vp], [self.fp])
        self.assert_refused(self.av, ["--blueprint", self.bpp, "--value", self.vp, "--out", self.bpp], [self.bpp])

    def test_value_recalculation_cannot_silently_erase_preview_costs(self):
        for marker in ({"finops_preview": {"maturity": "ga"}},
                       {"results": {"use_cases": [{"agents_costed": ["HR-A01"]}]}},
                       {"cost_modelled": True}):
            doc = dict(self.value, **marker)
            with self.subTest(marker=marker):
                with self.assertRaisesRegex(ValueError, ACK):
                    self.vc.run(doc, None)
                with self.assertRaisesRegex(ValueError, "--finops"):
                    self.vc.run(doc, None, acknowledge_finops_preview=True)
        self.assert_refused(self.vc, ["--value", self.dp], [self.dp])

    def test_feedback_keeps_preview_and_invalidates_results(self):
        fin = self.calculated()
        derived = dict(self.value, results=self.vc.run(self.value, fin, acknowledge_finops_preview=True))
        write(self.fp, fin)
        write(self.vp, derived)
        code, out, err = self.call(self.mv, ["--value", self.vp, "--finops", self.fp, "--feedback", self.fb, ACK])
        self.assertEqual(code, 0, err)
        self.preview(json.loads(out))
        for path in (self.fp, self.vp):
            doc = read(path)
            self.preview(doc)
            self.assertEqual(doc["version"], "1.1")
            self.assertNotIn("results", doc)
        self.assert_refused(self.mv, ["--value", self.vp, "--feedback", self.fb], [self.vp])
        code, out, err = self.call(self.mv, ["--value", self.vp, "--feedback", self.fb, ACK])
        self.assertEqual(code, 0, err)
        self.preview(json.loads(out))

    def test_malformed_preview_metadata_is_not_success_fallback(self):
        doc = dict(self.derived, finops_preview="not-an-object")
        with self.assertRaisesRegex(ValueError, "finops_preview"):
            self.av.apply(self.bp, doc, acknowledge_finops_preview=True)
        self.assertNotIn("value_case", self.bp)

    def test_core_without_optional_install_and_ack_alone_does_not_request_finops(self):
        installed = self.root / "skills"
        shutil.copytree(VAL / "scripts", installed / VAL.name / "scripts")
        shutil.copytree(BLUE, installed / BLUE.name)
        self.assertFalse((installed / FIN.name).exists())
        for flags in ([], [ACK]):
            with self.subTest(flags=flags):
                value = self.root / ("ga-ack.json" if flags else "ga.json")
                write(value, self.value)
                command = [sys.executable, str(installed / VAL.name / "scripts/value_calc.py"),
                           "--value", str(value), *flags]
                result = subprocess.run(command, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("finops_preview", read(value))
                out = self.root / ("core-ack" if flags else "core")
                result = subprocess.run([
                    sys.executable, str(installed / BLUE.name / "scripts/build_with_identity.py"),
                    "--data", str(self.bpp), "--out-dir", str(out), "--no-identity", *flags],
                    capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertFalse((out / "value-finops").exists())
        out = self.root / "missing-preview"
        result = subprocess.run([
            sys.executable, str(installed / BLUE.name / "scripts/build_with_identity.py"),
            "--data", str(self.bpp), "--out-dir", str(out), "--finops", str(self.fp), ACK],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("frontier-finops", result.stderr)
        self.assertIn("install", result.stderr.lower())
        self.assertFalse(out.exists())
        result = subprocess.run([
            sys.executable, str(installed / VAL.name / "scripts/value_calc.py"),
            "--value", str(self.vp), "--finops", str(self.fp), ACK],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("install", result.stderr.lower())

    def test_wrapper_forwards_flag_only_with_finops_consumption(self):
        seen = []
        original = self.wrapper.run
        def run(path, *args):
            seen.append((path.name, [str(x) for x in args]))
            return original(path, *args)
        with mock.patch.object(self.wrapper, "run", side_effect=run):
            code, out, err = self.call(self.wrapper, [
                "--data", self.bpp, "--out-dir", self.root / "combined", "--no-identity",
                "--value", self.vp, "--finops", self.fp, ACK])
        self.assertEqual(code, 0, (out, err))
        for name in ("finops_calc.py", "apply_finops.py", "value_calc.py", "apply_value.py"):
            args = next(args for child, args in seen if child == name)
            self.assertIn(ACK, args, name)
        summary = json.loads(out)
        self.preview(summary["finops"])
        self.preview(summary["value"])
        seen.clear()
        with mock.patch.object(self.wrapper, "run", side_effect=run):
            code, out, err = self.call(self.wrapper, [
                "--data", self.bpp, "--out-dir", self.root / "value-only", "--no-identity",
                "--value", self.vp, ACK])
        self.assertEqual(code, 0, (out, err))
        self.assertFalse(any(name in ("finops_calc.py", "apply_finops.py") for name, _ in seen))
        self.assertFalse(any(ACK in args for _, args in seen))

    def test_wrapper_child_error_is_not_silent_core_success(self):
        target = self.root / "broken"
        write(self.fp, dict(self.fin, fx={"chf_per_usd": "invalid"}))
        code, out, err = self.call(self.wrapper, [
            "--data", self.bpp, "--out-dir", target, "--no-identity", "--finops", self.fp, ACK])
        self.assertEqual(code, 2, (out, err))
        self.assertIn("ERROR:", err)
        self.assertFalse(any(target.glob("*.html")))

    def test_new_value_rate_provenance_wins_over_old_blueprint_lineage(self):
        old_fin = self.calculated()
        old_value = dict(self.value, results=self.vc.run(self.value, old_fin, acknowledge_finops_preview=True))
        self.av.apply(self.bp, old_value, acknowledge_finops_preview=True)
        new_rates = copy.deepcopy(self.rates)
        new_rates["version"] = "2026-11-12"
        new_fin = copy.deepcopy(self.fin)
        new_fin["results"] = self.fc.run(new_fin, self.value, new_rates, acknowledge_finops_preview=True)
        new_value = dict(self.value, results=self.vc.run(self.value, new_fin, acknowledge_finops_preview=True))
        self.av.apply(self.bp, new_value, acknowledge_finops_preview=True)
        inputs = self.bp["value_case"]["finops_preview"]["provenance"]["inputs"]
        self.assertEqual(inputs["rates"]["version"], "2026-11-12", "Old blueprint metadata must not replace new cost inputs")

    def test_null_and_bad_provenance_are_explicit_errors_before_mutation(self):
        for metadata in (None, {"provenance": {"scenario": "bad"}},
                         {"provenance": {"inputs": {"rates": "bad"}}}):
            with self.subTest(metadata=metadata):
                doc = dict(self.derived, finops_preview=metadata)
                bp = copy.deepcopy(self.bp)
                with self.assertRaisesRegex(ValueError, "finops_preview"):
                    self.av.apply(bp, doc, acknowledge_finops_preview=True)
                self.assertEqual(bp, self.bp)
                model = dict(self.fin, finops_preview=metadata)
                with self.assertRaisesRegex(ValueError, "finops_preview"):
                    self.fc.run(model, self.value, self.rates, acknowledge_finops_preview=True)

    def test_inherited_provenance_does_not_project_private_source_text(self):
        fin = self.calculated()
        derived = dict(self.value, results=self.vc.run(self.value, fin, acknowledge_finops_preview=True))
        metadata = derived["results"]["finops_preview"]
        metadata["provenance"]["internal_discount"] = "PRIVATE-RATE-SENTINEL"
        metadata["provenance"]["inputs"]["rates"]["internal_notes"] = "PRIVATE-RATE-SENTINEL"
        metadata["provenance"]["sources"][0]["title"] = "PRIVATE-SOURCE-SENTINEL"
        self.av.apply(self.bp, derived, acknowledge_finops_preview=True)
        projected = json.dumps(self.bp)
        self.assertNotIn("PRIVATE-RATE-SENTINEL", projected)
        self.assertNotIn("PRIVATE-SOURCE-SENTINEL", projected)

    def test_apply_finops_preserves_privacy_markers_for_customer_projection(self):
        rates = copy.deepcopy(self.rates)
        rates["sources"][0].update({"title": "PRIVATE-SOURCE-SENTINEL", "internal": True})
        self.fin["assumptions"][0].update({"statement": "PRIVATE-ASSUMPTION-SENTINEL", "internal": True})
        self.fin["results"] = self.fc.run(self.fin, self.value, rates, acknowledge_finops_preview=True)
        block = self.af.build_block(self.bp, self.fin, rates, self.value, acknowledge_finops_preview=True)
        bp = dict(self.bp, finops=block)
        builder = script(BLUE, "build_blueprint")
        customer = builder.customer_version(bp, builder.Report())
        self.assertNotIn("PRIVATE-SOURCE-SENTINEL", json.dumps(customer))
        self.assertNotIn("PRIVATE-ASSUMPTION-SENTINEL", json.dumps(customer))
        self.assertEqual(customer["finops"]["finops_preview"]["maturity"], "preview")
        self.assertIn("provisional planning estimates", customer["finops"]["finops_preview"]["notice"])
        self.assertNotIn("scenario", customer["finops"]["finops_preview"]["provenance"],
                         "An internal calculation scope is not a public provenance claim")
        self.assertNotIn("totals", customer["finops"])

    def test_legacy_applied_purchase_comparisons_are_provisional_not_recommendations(self):
        self.fin["results"]["purchase_options"] = [
            {"option": "cc-p3", "annual_chf": 7827.52, "lowest": True, "assessment": "approved"}]
        with self.assertRaises(ValueError):
            self.af.build_block(self.bp, self.fin, self.rates, self.value, acknowledge_finops_preview=True)
        self.fin["results"] = self.fc.run(self.fin, self.value, self.rates, acknowledge_finops_preview=True)
        block = self.af.build_block(self.bp, self.fin, self.rates, self.value, acknowledge_finops_preview=True)
        for option in block["purchase_options"]:
            self.assertEqual(option["assessment"], "provisional-comparison-not-recommendation")

    def test_bad_rates_and_fx_do_not_compute_success_shaped_defaults(self):
        for fx in (0, False, -1, float("nan")):
            with self.subTest(fx=fx):
                fin = dict(self.fin, fx={"chf_per_usd": fx})
                with self.assertRaises(ValueError):
                    self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
        fin = copy.deepcopy(self.fin)
        fin["agents"][0]["licences"] = [{"sku": "missing-rate", "seats": 5}]
        with self.assertRaisesRegex(ValueError, "licence"):
            self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)

    def test_scoped_finops_assumptions_remain_a_legacy_dependency(self):
        doc = copy.deepcopy(self.value)
        doc["assumptions"][0]["scope"] = "finops"
        with self.assertRaisesRegex(ValueError, ACK):
            self.vc.run(doc, None)
        write(self.dp, doc)
        self.assert_refused(self.mv, ["--value", self.dp, "--feedback", self.fb], [self.dp])

    def test_core_apply_and_feedback_without_finops_installed(self):
        installed = self.root / "core/skills"
        shutil.copytree(VAL / "scripts", installed / VAL.name / "scripts")
        for name, args in (
            ("value_calc.py", ["--value", str(self.vp)]),
            ("apply_value.py", ["--blueprint", str(self.bpp), "--value", str(self.vp), "--out", str(self.bpp)]),
            ("merge_value_feedback.py", ["--value", str(self.vp), "--feedback", str(self.fb)]),
        ):
            result = subprocess.run([sys.executable, str(installed / VAL.name / "scripts" / name), *args],
                                    capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("finops_preview", json.loads(result.stdout))
        self.assertEqual(read(self.vp)["version"], "1.1")

    def test_ga_value_with_user_supplied_cost_formula_never_imports_finops(self):
        doc = copy.deepcopy(self.value)
        doc["use_cases"][0]["levers"].append({
            "id": "USER-COST", "name": "Customer-supplied run cost",
            "category": "cash", "formula": "-1200", "ramp": False})
        with mock.patch.object(self.vc.importlib.util, "spec_from_file_location",
                               side_effect=AssertionError("No FinOps import in the GA value path")):
            result = self.vc.run(doc, None, acknowledge_finops_preview=True)
        self.assertNotIn("finops_preview", result)
        self.assertEqual(result["totals"]["budget_year"], -14400)

    def test_helper_description_needs_no_consent_and_stores_none(self):
        helper = script(FIN, "finops_preview")
        code, out, err = self.call(helper, [])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["notice"], helper.NOTICE)
        self.assertNotIn("acknowledgement", json.loads(out))

    def test_consumed_cost_results_have_their_own_fingerprint(self):
        fin = self.calculated()
        first = self.vc.run(self.value, fin, acknowledge_finops_preview=True)
        changed = copy.deepcopy(fin)
        changed["results"]["agents"][0]["fixed_month"] += 120
        with self.assertRaisesRegex(ValueError, "stale|calculation"):
            self.vc.run(self.value, changed, acknowledge_finops_preview=True)
        next(a for a in changed["assumptions"] if a["id"] == "ASS-106")["base"] = 32
        changed["results"] = self.fc.run(changed, self.value, self.rates, acknowledge_finops_preview=True)
        second = self.vc.run(self.value, changed, acknowledge_finops_preview=True)
        self.assertNotEqual(first["totals"]["npv"], second["totals"]["npv"])
        one = first["finops_preview"]["provenance"]["inputs"]
        two = second["finops_preview"]["provenance"]["inputs"]
        self.assertIn("finops_results", one, "Consumed cached figures must be bound, not just their authored model")
        self.assertNotEqual(one["finops_results"]["fingerprint"], two["finops_results"]["fingerprint"])
        derived = dict(self.value, results=second)
        applied = self.av.apply(self.bp, derived, acknowledge_finops_preview=True)
        inputs = applied["finops_preview"]["provenance"]["inputs"]
        self.assertIn("value_results", inputs)

    def test_legacy_known_rate_version_is_retained_without_inventing_hash_or_sources(self):
        self.fin["results"]["rates_version"] = "2026-10-30"
        with self.assertRaises(ValueError):
            self.vc.run(self.value, self.fin, acknowledge_finops_preview=True)
        helper = script(FIN, "finops_preview")
        described = helper.preview_metadata(True, operation="describe-legacy", finops=self.fin, value=self.value)
        provenance = described["provenance"]
        self.assertIn("rates", provenance["inputs"])
        rate = provenance["inputs"]["rates"]
        self.assertEqual(rate["version"], "2026-10-30")
        self.assertIsNone(rate.get("fingerprint"))
        self.assertEqual(provenance["sources"], [])
        self.assertIn("rates", provenance["missing_inputs"], "A version string is not the actual rate model")

    def test_compute_binds_the_actual_supplied_assumption_register(self):
        register = self.fc.register_of(self.value, self.fin)
        result = self.fc.compute(self.fin, register, self.rates, acknowledge_finops_preview=True)
        scenario = result["finops_preview"]["provenance"]["scenario"]
        self.assertIn("register_fingerprint", scenario)
        changed = copy.deepcopy(register)
        changed["ASS-106"]["base"] = 32
        other = self.fc.compute(self.fin, changed, self.rates, acknowledge_finops_preview=True)
        self.assertNotEqual(scenario["register_fingerprint"],
                            other["finops_preview"]["provenance"]["scenario"]["register_fingerprint"])

    def test_purchase_lessons_describe_provisional_comparison_not_commitment_advice(self):
        rates = copy.deepcopy(self.rates)
        rates["credits"]["pack"]["chf_list"] = 80
        result = self.fc.run(self.fin, self.value, rates, acknowledge_finops_preview=True)
        comparison = next(line for line in result["lessons"] if "urchase" in line)
        self.assertIn("Provisional purchase comparison", comparison)
        self.assertNotIn("commit to", comparison)

    def test_malformed_models_report_cli_errors_without_overwriting(self):
        for module, path, model, args in (
            (self.fc, self.fp, [], ["--finops", self.fp, "--value", self.vp, ACK]),
            (self.vc, self.fp, dict(self.fin, results="invalid"), ["--value", self.vp, "--finops", self.fp, ACK]),
            (self.af, self.fp, dict(self.fin, results="invalid"),
             ["--blueprint", self.bpp, "--finops", self.fp, "--out", self.bpp, ACK]),
            (self.av, self.dp, dict(self.derived, results="invalid", cost_modelled=True),
             ["--blueprint", self.bpp, "--value", self.dp, "--out", self.bpp, ACK]),
        ):
            with self.subTest(module=module.__name__):
                write(path, model)
                before = (self.bpp.read_bytes(), self.vp.read_bytes(), path.read_bytes())
                code, out, err = self.call(module, args)
                self.assertEqual(code, 2, (out, err))
                self.assertIn("ERROR:", err)
                self.assertEqual(out, "")
                self.assertEqual((self.bpp.read_bytes(), self.vp.read_bytes(), path.read_bytes()), before)

    def test_empty_optional_slots_do_not_request_finops_in_value_only_builds(self):
        for slot in (None, {}):
            with self.subTest(slot=slot):
                bp = dict(self.bp, finops=slot)
                write(self.bpp, bp)
                with mock.patch.object(self.vc.importlib.util, "spec_from_file_location",
                                       side_effect=AssertionError("An empty optional slot must not load FinOps")):
                    self.assertIsNone(self.vc.preview_for(self.value, blueprint=bp))
                installed = self.root / ("null-skills" if slot is None else "empty-skills")
                shutil.copytree(VAL / "scripts", installed / VAL.name / "scripts")
                shutil.copytree(BLUE, installed / BLUE.name)
                result = subprocess.run([
                    sys.executable, str(installed / BLUE.name / "scripts/build_with_identity.py"),
                    "--data", str(self.bpp), "--value", str(self.vp), "--out-dir", str(installed / "out"),
                    "--no-identity"], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("finops_preview", json.loads(result.stdout))

    def test_feedback_api_binds_updated_models_not_pre_mutation_inputs(self):
        helper = script(FIN, "finops_preview")
        fin, value = self.calculated(), copy.deepcopy(self.value)
        summary = self.mv.merge([value, fin], self.mv.verdicts_from(read(self.fb)), "2026-11-12",
                                acknowledge_finops_preview=True)
        inputs = summary["finops_preview"]["provenance"]["inputs"]
        self.assertEqual(inputs["finops"]["fingerprint"], helper.fingerprint(fin))
        self.assertEqual(inputs["value"]["fingerprint"], helper.fingerprint(value))
        self.assertEqual(inputs["value"]["schema"], "frontier-value/1.0")
        self.preview(value)
        self.preview(fin)

    def test_feedback_cli_preserves_value_and_finops_input_roles(self):
        code, out, err = self.call(self.mv, ["--value", self.vp, "--finops", self.fp, "--feedback", self.fb, ACK])
        self.assertEqual(code, 0, err)
        for doc in (read(self.vp), read(self.fp), json.loads(out)):
            inputs = self.preview(doc)["provenance"]["inputs"]
            self.assertEqual(inputs["value"]["schema"], "frontier-value/1.0")
            self.assertEqual(inputs["finops"]["schema"], "frontier-finops/1.0")

    def costed_models(self):
        fin = self.calculated()
        value = copy.deepcopy(self.value)
        value["results"] = self.vc.run(value, fin, acknowledge_finops_preview=True)
        value["finops_preview"] = copy.deepcopy(value["results"]["finops_preview"])
        fin["finops_preview"] = copy.deepcopy(fin["results"]["finops_preview"])
        return fin, value

    def assert_error_no_write(self, module, args, paths):
        before = {p: p.read_bytes() if p.exists() else None for p in paths}
        code, out, err = self.call(module, args)
        self.assertEqual(code, 2, (out, err))
        self.assertIn("ERROR:", err)
        self.assertEqual(out, "")
        for path, content in before.items():
            self.assertEqual(path.read_bytes() if path.exists() else None, content)

    def test_spec1_finops_feedback_invalidates_dependent_value_api_cache(self):
        fin, value = self.costed_models()
        self.mv.merge([value, fin], [{"id": "ASS-106", "status": "adjusted", "value": 32}],
                      "2026-11-12", acknowledge_finops_preview=True)
        self.assertNotIn("results", fin)
        self.assertNotIn("results", value, "Cost feedback must invalidate dependent value, not retain stale NPV")
        with self.assertRaises(ValueError):
            self.av.apply(self.bp, value, acknowledge_finops_preview=True)

    def test_spec1_finops_only_feedback_writes_dependent_value_invalidation(self):
        fin, value = self.costed_models()
        write(self.fp, fin); write(self.vp, value)
        write(self.fb, {"type": "frontier-blueprint-feedback", "validations": {
            "ass:ASS-106": {"status": "adjusted", "value": 32}}})
        code, out, err = self.call(self.mv, ["--value", self.vp, "--finops", self.fp, "--feedback", self.fb, ACK])
        self.assertEqual(code, 0, err)
        self.assertNotIn("results", read(self.fp))
        self.assertNotIn("results", read(self.vp), "Invalidation must be saved even with no direct value verdict")
        self.assert_error_no_write(self.av, ["--blueprint", self.bpp, "--value", self.vp, "--out", self.bpp, ACK],
                                   [self.bpp])

    def test_spec1_direct_cost_assumption_drift_requires_recalculation(self):
        fin, _ = self.costed_models()
        next(a for a in fin["assumptions"] if a["id"] == "ASS-106")["base"] = 32
        with self.assertRaisesRegex(ValueError, "stale|recalculate|calculation"):
            self.vc.run(self.value, fin, acknowledge_finops_preview=True)
        fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
        result = self.vc.run(self.value, fin, acknowledge_finops_preview=True)
        self.assertAlmostEqual(result["use_cases"][0]["cost_month_full"], 4502.418, places=3)

    def test_spec1_value_assumption_drift_cannot_apply_cached_npv(self):
        _, value = self.costed_models()
        value["assumptions"][2]["base"] = 0.4
        bp = copy.deepcopy(self.bp)
        with self.assertRaisesRegex(ValueError, "stale|recalculate|calculation"):
            self.av.apply(bp, value, acknowledge_finops_preview=True)
        self.assertEqual(bp, self.bp)

    def test_spec2_applying_new_rates_rejects_old_calculated_figures_api_and_cli(self):
        fin, value = self.costed_models()
        rates = copy.deepcopy(self.rates)
        rates["version"] = rates["checked"] = "2026-11-12"
        rates["credits"]["payg_usd_per_credit"] *= 2
        bp = copy.deepcopy(self.bp)
        with self.assertRaisesRegex(ValueError, "rates|calculation|recalculate"):
            self.af.build_block(bp, fin, rates, value, acknowledge_finops_preview=True)
        self.assertEqual(bp, self.bp)
        write(self.fp, fin); write(self.vp, value)
        rp = write(self.root / "new-rates.json", rates)
        self.assert_error_no_write(self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--value", self.vp,
                                           "--rates", rp, "--out", self.bpp, ACK], [self.bpp])

    def test_spec2_changed_finops_model_cannot_apply_old_cost_cache(self):
        fin, value = self.costed_models()
        fin["agents"][0]["usage"]["billable_share"] = 1
        with self.assertRaisesRegex(ValueError, "stale|recalculate|calculation"):
            self.af.build_block(self.bp, fin, self.rates, value, acknowledge_finops_preview=True)

    def test_spec2_application_preserves_the_consumed_calculation_scenario(self):
        fin = copy.deepcopy(self.fin)
        register = self.fc.register_of(self.value, fin)
        fin["results"] = self.fc.compute(fin, register, self.rates, scenario="high",
                                         acknowledge_finops_preview=True)
        receipt = fin["results"]["finops_preview"]["calculations"]["finops"]
        self.assertIn("inputs", receipt, "Consumed calculations must retain their own source snapshots")
        self.assertEqual(receipt["inputs"]["rates"]["version"], self.rates["version"])
        applied = self.af.build_block(self.bp, fin, self.rates, self.value, acknowledge_finops_preview=True)
        self.assertEqual(applied["finops_preview"]["provenance"]["scenario"]["name"], "high")

    def test_spec3_consumed_results_override_stale_outer_provenance(self):
        fin, value = self.costed_models()
        old_fin_meta = copy.deepcopy(fin["finops_preview"])
        old_value_meta = copy.deepcopy(value["finops_preview"])
        rates = copy.deepcopy(self.rates)
        rates["version"] = rates["checked"] = "2026-11-12"
        rates["credits"]["payg_usd_per_credit"] *= 2
        fin["results"] = self.fc.run(fin, self.value, rates, acknowledge_finops_preview=True)
        fin["finops_preview"] = old_fin_meta
        value["results"] = self.vc.run(value, fin, acknowledge_finops_preview=True)
        value["finops_preview"] = old_value_meta
        summary = self.av.apply(self.bp, value, acknowledge_finops_preview=True)
        for metadata in (value["results"]["finops_preview"], summary["finops_preview"],
                         self.bp["value_case"]["finops_preview"]):
            self.assertEqual(metadata["provenance"]["inputs"]["rates"]["version"], "2026-11-12")

    def test_spec4_malformed_cost_cache_never_becomes_zero_cost_value(self):
        for cache in ({"agents": []}, {"totals": {}}):
            with self.subTest(cache=cache):
                fin = self.calculated()
                fin["results"] = cache
                with self.assertRaisesRegex(ValueError, "results|calculation|recalculate"):
                    self.vc.run(self.value, fin, acknowledge_finops_preview=True)
                with self.assertRaisesRegex(ValueError, "results|calculation|recalculate"):
                    self.af.build_block(self.bp, fin, self.rates, self.value, acknowledge_finops_preview=True)

    def test_spec4_missing_or_null_result_lineage_cannot_be_applied(self):
        for null in (False, True):
            with self.subTest(null=null):
                fin = self.calculated()
                if null:
                    fin["results"]["finops_preview"] = None
                else:
                    fin["results"].pop("finops_preview")
                with self.assertRaisesRegex(ValueError, "finops_preview|lineage|recalculate"):
                    self.af.build_block(self.bp, fin, self.rates, self.value, acknowledge_finops_preview=True)

    def test_spec4_legitimate_calculated_missing_input_reports_remain_usable(self):
        value = copy.deepcopy(self.value)
        value["assumptions"][0]["base"] = None
        fin = self.seed.seed(self.bp, value, acknowledge_finops_preview=True)
        fin["results"] = self.fc.run(fin, value, self.rates, acknowledge_finops_preview=True)
        self.assertTrue(fin["results"]["missing"])
        result = self.vc.run(value, fin, acknowledge_finops_preview=True)
        self.assertTrue(result["inputs_needed"])
        block = self.af.build_block(self.bp, fin, self.rates, value, acknowledge_finops_preview=True)
        self.assertTrue(block["missing"])

    def test_spec5_cost_model_date_and_privacy_ancestry_reach_derived_value(self):
        for restriction in ({"internal": True}, {"visibility": "internal"}):
            with self.subTest(restriction=restriction):
                fin = copy.deepcopy(self.fin)
                fin.update(restriction)
                fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
                value = dict(self.value, results=self.vc.run(self.value, fin, acknowledge_finops_preview=True))
                inputs = value["results"]["finops_preview"]["provenance"]["inputs"]
                self.assertEqual(inputs["finops"].get("date"), fin["date"])
                for key, flag in restriction.items():
                    self.assertEqual(inputs["finops"].get(key), flag)
                    self.assertEqual(value["results"].get(key), flag)
                bp = copy.deepcopy(self.bp)
                bp["finops"] = self.af.build_block(bp, fin, self.rates, self.value, acknowledge_finops_preview=True)
                summary = self.av.apply(bp, value, acknowledge_finops_preview=True)
                for record in (bp["value_case"], bp["domains"][0]["use_cases"][0]["business_value"], summary):
                    for key, flag in restriction.items():
                        self.assertEqual(record.get(key), flag, "Derived aggregate and per-case figures must retain restrictions")

    def test_spec5_private_rate_model_restricts_derived_cost_and_value(self):
        rates = dict(self.rates, internal=True)
        fin = copy.deepcopy(self.fin)
        fin["results"] = self.fc.run(fin, self.value, rates, acknowledge_finops_preview=True)
        value = dict(self.value, results=self.vc.run(self.value, fin, acknowledge_finops_preview=True))
        self.assertIs(value["results"].get("internal"), True)
        bp = copy.deepcopy(self.bp)
        bp["finops"] = self.af.build_block(bp, fin, rates, self.value, acknowledge_finops_preview=True)
        self.av.apply(bp, value, acknowledge_finops_preview=True)
        builder = script(BLUE, "build_blueprint")
        customer = builder.customer_version(bp, builder.Report())
        self.assertNotIn("finops", customer)
        self.assertNotIn("value_case", customer)

    def test_spec5_customer_exports_remove_private_cost_derived_value_but_keep_public_counterpart(self):
        builder = script(BLUE, "build_blueprint")
        scaffold = script(SKILLS / "frontier-solution-design", "scaffold_design_docs")
        for private in (False, True):
            with self.subTest(private=private):
                fin = copy.deepcopy(self.fin)
                if private:
                    fin["internal"] = True
                fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
                value = dict(self.value, results=self.vc.run(self.value, fin, acknowledge_finops_preview=True))
                bp = copy.deepcopy(self.bp)
                bp["finops"] = self.af.build_block(bp, fin, self.rates, self.value, acknowledge_finops_preview=True)
                self.av.apply(bp, value, acknowledge_finops_preview=True)
                customer = builder.customer_version(bp, builder.Report())
                for field, record in (("finops", customer), ("value_case", customer),
                                      ("business_value", customer["domains"][0]["use_cases"][0])):
                    with self.subTest(channel="projected-json", field=field):
                        self.assertEqual(field in record, not private)
                inp = write(self.root / f"export-{private}.json", bp)
                normalized = self.root / f"customer-{private}.json"
                html = self.root / f"customer-{private}.html"
                code, out, err = self.call(builder, ["--data", inp, "--audience", "customer",
                                                    "--save-normalized", normalized, "--out", html])
                self.assertEqual(code, 0, (out, err))
                with self.subTest(channel="normalized-json"):
                    self.assertEqual("value_case" in read(normalized), not private)
                if private:
                    with self.subTest(channel="customer-html-cost"):
                        self.assertFalse('"cost_year":30989.02' in html.read_text(encoding="utf-8"), "Private cost leaked into HTML")
                    with self.subTest(channel="customer-html-npv"):
                        self.assertFalse('"npv":540412.55' in html.read_text(encoding="utf-8"), "Private NPV leaked into HTML")
                agents, doms = scaffold.collect(read(normalized), None)
                prd = scaffold.build_prd(read(normalized), agents, doms, "Workshop team", "2026-11-12")
                if private:
                    with self.subTest(channel="customer-scaffold"):
                        self.assertNotIn("30989.02", prd)
                        self.assertNotIn("540412.55", prd)

    def test_spec6_missing_cost_source_refuses_wrapper_before_side_effects(self):
        _, value = self.costed_models()
        write(self.vp, value)
        target = self.root / "missing-source"
        with mock.patch.object(self.wrapper, "build_identity", return_value=self.bpp) as identity, \
                mock.patch.object(self.wrapper, "run", return_value=(0, "{}", "")) as child:
            code, out, err = self.call(self.wrapper, ["--data", self.bpp, "--value", self.vp,
                                                     "--out-dir", target, ACK])
        self.assertEqual(code, 2, (out, err))
        identity.assert_not_called()
        child.assert_not_called()
        self.assertFalse(target.exists())
        self.assertIn("--finops", err)

    def test_spec7_selected_fx_and_used_cost_rates_reject_invalid_numeric_ranges(self):
        cases = [
            ("fallback-zero", ("fx", "swiss_list_ratio"), 0),
            ("fallback-negative", ("fx", "swiss_list_ratio"), -0.81),
            ("fallback-bool", ("fx", "swiss_list_ratio"), True),
            ("negative-payg", ("credits", "payg_usd_per_credit"), -0.01),
            ("bool-payg", ("credits", "payg_usd_per_credit"), True),
            ("negative-event", ("credits", "per_event", "generative_answer"), -2),
            ("bool-event", ("credits", "per_event", "graph_grounding"), True),
            ("bad-discount", ("credits", "cc_p3_tiers"), [[1000000, 1.5]]),
            ("nan-payg", ("credits", "payg_usd_per_credit"), float("nan")),
            ("infinite-fx", ("fx", "swiss_list_ratio"), float("inf")),
            ("infinite-event", ("credits", "per_event", "graph_grounding"), float("inf")),
        ]
        for label, keys, bad in cases:
            with self.subTest(label=label):
                fin, rates = copy.deepcopy(self.fin), copy.deepcopy(self.rates)
                fin["fx"]["chf_per_usd"] = None
                target = rates
                for key in keys[:-1]:
                    target = target[key]
                target[keys[-1]] = bad
                with self.assertRaises(ValueError):
                    self.fc.run(fin, self.value, rates, acknowledge_finops_preview=True)

    def test_spec7_invalid_rates_cli_never_overwrites_previous_cost_output(self):
        rates = copy.deepcopy(self.rates)
        rates["credits"]["payg_usd_per_credit"] = -0.01
        rp = write(self.root / "invalid-rates.json", rates)
        self.assert_error_no_write(self.fc, ["--finops", self.fp, "--value", self.vp, "--rates", rp, ACK], [self.fp])

    def customer_exports(self, bp, tag):
        builder = script(BLUE, "build_blueprint")
        source = write(self.root / f"{tag}-source.json", bp)
        normalized, html = self.root / f"{tag}-customer.json", self.root / f"{tag}-customer.html"
        code, out, err = self.call(builder, ["--data", source, "--audience", "customer",
                                            "--save-normalized", normalized, "--out", html])
        self.assertEqual(code, 0, (out, err))
        customer = read(normalized)
        scaffold = script(SKILLS / "frontier-solution-design", "scaffold_design_docs")
        agents, domains = scaffold.collect(customer, None)
        prd = scaffold.build_prd(customer, agents, domains, "Workshop team", "2026-11-12")
        return customer, html.read_text(encoding="utf-8"), prd

    def test_residual1_tampered_privacy_provenance_rejects_api_and_cli_without_writes(self):
        fin = dict(self.fin, internal=True)
        fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
        value = dict(self.value, results=self.vc.run(self.value, fin, acknowledge_finops_preview=True))
        self.assertIs(value["results"]["internal"], True)
        value["results"]["finops_preview"]["provenance"]["inputs"]["finops"]["internal"] = False
        before = copy.deepcopy(self.bp)
        with self.assertRaisesRegex(ValueError, "snapshot|provenance|lineage"):
            self.av.apply(self.bp, value, acknowledge_finops_preview=True)
        self.assertEqual(self.bp, before)
        write(self.vp, value)
        self.assert_error_no_write(self.av, ["--blueprint", self.bpp, "--value", self.vp, "--out", self.bpp, ACK],
                                   [self.bpp])
        customer, html, prd = self.customer_exports(read(self.bpp), "tampered-privacy")
        for blob in (json.dumps(customer), html, prd):
            self.assertFalse("30989.02" in blob or "540412.55" in blob, "Refused private figures leaked in export")

    def test_residual1_checked_date_contradiction_rejects_finops_and_value_consumers(self):
        fin, value = self.costed_models()
        for kind in ("finops", "value"):
            with self.subTest(kind=kind):
                model = copy.deepcopy(fin if kind == "finops" else value)
                model["results"]["finops_preview"]["provenance"]["inputs"]["rates"]["checked"] = "2099-01-01"
                with self.assertRaisesRegex(ValueError, "snapshot|provenance|lineage"):
                    if kind == "finops":
                        self.af.build_block(self.bp, model, self.rates, self.value, acknowledge_finops_preview=True)
                    else:
                        self.av.apply(self.bp, model, acknowledge_finops_preview=True)

    def test_residual1_conservative_result_restrictions_and_public_counterpart_survive_application(self):
        for private in (False, True):
            with self.subTest(private=private):
                fin = dict(self.fin, **({"internal": True} if private else {}))
                fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
                value = dict(self.value, results=self.vc.run(self.value, fin, acknowledge_finops_preview=True))
                bp = copy.deepcopy(self.bp)
                self.av.apply(bp, value, acknowledge_finops_preview=True)
                customer, html, _ = self.customer_exports(bp, f"restriction-{private}")
                self.assertEqual("business_value" in customer["domains"][0]["use_cases"][0], not private)
                self.assertEqual('"cost_year":30989.02' in html, not private)

    def nested_models(self, *, source_private=False):
        fin, value = copy.deepcopy(self.fin), copy.deepcopy(self.value)
        private = fin["agents"][0]
        private.update(name="PRIVATE-AGENT-SENTINEL", date="2026-11-05")
        if source_private is True:
            private["azure"] = [{"name": "PRIVATE-RATE-SENTINEL", "qty": 1, "chf": 17,
                                  "internal": True, "date": "2026-11-06"}]
        elif source_private == "assumption":
            next(a for a in fin["assumptions"] if a["id"] == "ASS-106").update(internal=True, date="2026-11-06")
        elif source_private == "people":
            private["people"].update(internal=True, date="2026-11-06")
        else:
            private["internal"] = True
        public = copy.deepcopy(private)
        public.update(id="HR-PUB", name="PUBLIC-AGENT", date="2026-11-07")
        public.pop("internal", None)
        public["azure"] = []
        public["people"] = {"run_hours_month": 1, "rate_chf": 10, "build_one_time_chf": 0}
        public["usage"] = {"sessions": 1, "billable_share": 1, "events_per_session": {"generative_answer": 1}}
        public["vars"] = {}
        public.pop("outcome", None)
        fin["agents"].append(public)
        value["use_cases"].append({
            "id": "UC-PUB", "name": "Public case", "agents": ["HR-PUB"], "vars": {},
            "levers": [{"id": "PUB-L1", "name": "Public value", "category": "cash", "formula": "100"}]})
        bp = copy.deepcopy(self.bp)
        bp["domains"][0]["agents"].append({"id": "HR-PUB", "name": "PUBLIC-AGENT"})
        bp["domains"][0]["use_cases"].append({"id": "UC-PUB", "name": "Public case", "agents": ["HR-PUB"]})
        fin["results"] = self.fc.run(fin, value, self.rates, acknowledge_finops_preview=True)
        value["results"] = self.vc.run(value, fin, acknowledge_finops_preview=True)
        return fin, value, bp

    def test_residual2_nested_agent_and_source_privacy_dates_are_retained(self):
        for source_private in (False, True, "assumption"):
            with self.subTest(source_private=source_private):
                fin, value, bp = self.nested_models(source_private=source_private)
                private, public = fin["results"]["agents"]
                self.assertIs(private.get("internal"), True)
                self.assertEqual(private.get("date"), "2026-11-05")
                self.assertIsNot(public.get("internal"), True)
                if source_private is True:
                    self.assertIs(private["azure_lines"][0].get("internal"), True)
                    self.assertEqual(private["azure_lines"][0].get("date"), "2026-11-06")
                bp["finops"] = self.af.build_block(bp, fin, self.rates, value, acknowledge_finops_preview=True)
                self.assertIs(bp["finops"]["agents"][0].get("internal"), True)
                self.assertEqual(bp["finops"]["agents"][0].get("date"), "2026-11-05")
                rows = {r["id"]: r for r in value["results"]["use_cases"]}
                self.assertIs(rows["UC-HR"].get("internal"), True)
                self.assertIsNot(rows["UC-PUB"].get("internal"), True)

    def test_residual2_customer_exports_hide_nested_private_costs_and_keep_public_counterparts(self):
        for source_private in (False, True, "assumption"):
            with self.subTest(source_private=source_private):
                fin, value, bp = self.nested_models(source_private=source_private)
                bp["finops"] = self.af.build_block(bp, fin, self.rates, value, acknowledge_finops_preview=True)
                self.av.apply(bp, value, acknowledge_finops_preview=True)
                customer, html, prd = self.customer_exports(bp, f"nested-{source_private}")
                for blob in (json.dumps(customer), html, prd):
                    with self.subTest(channel="export"):
                        self.assertFalse("PRIVATE-AGENT-SENTINEL" in blob or "PRIVATE-RATE-SENTINEL" in blob,
                                         "Nested private source/name leaked")
                self.assertEqual([a["id"] for a in customer["finops"]["agents"]], ["HR-PUB"])
                cases = {u["id"]: u for u in customer["domains"][0]["use_cases"]}
                self.assertNotIn("business_value", cases["UC-HR"])
                self.assertIn("business_value", cases["UC-PUB"])
                self.assertNotIn("value_case", customer, "The full aggregate contains private contributions")
                self.assertNotIn("totals", customer["finops"], "Full totals must not masquerade as public-only totals")

    def test_residual2_seeding_keeps_private_agent_date_and_source_restrictions(self):
        bp = copy.deepcopy(self.bp)
        bp["domains"][0]["agents"][0].update(internal=True, date="2026-11-05")
        seeded = self.seed.seed(bp, self.value, acknowledge_finops_preview=True)
        self.assertIs(seeded["agents"][0].get("internal"), True)
        self.assertEqual(seeded["agents"][0].get("date"), "2026-11-05")

    def test_residual3_source_only_feedback_is_a_change_and_invalidates_api_caches(self):
        fin, value = self.costed_models()
        value["assumptions"][2]["src"] = ["OLD"]
        result = self.mv.merge([value, fin], [{"id": "ASS-003", "src": ["NEW"]}],
                               "2026-11-12", acknowledge_finops_preview=True)
        self.assertEqual(len(result["changes"]), 1)
        self.assertEqual(result["changes"][0]["from"]["src"], ["OLD"])
        self.assertEqual(result["changes"][0]["to"]["src"], ["NEW", "OLD"])
        self.assertNotIn("results", value)
        self.assertNotIn("results", fin)
        self.assertEqual(value["assumptions"][2]["status"], "open")

    def test_residual3_source_only_feedback_cli_persists_and_invalidates_both_models(self):
        fin, value = self.costed_models()
        value["assumptions"][2]["src"] = ["OLD"]
        write(self.fp, fin); write(self.vp, value)
        write(self.fb, {"assumption_feedback": [{"kind": "ass", "id": "ASS-003", "src": ["NEW"]}]})
        code, out, err = self.call(self.mv, ["--value", self.vp, "--finops", self.fp, "--feedback", self.fb, ACK])
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["changed"], 1)
        self.assertEqual(read(self.vp)["assumptions"][2]["src"], ["NEW", "OLD"])
        self.assertEqual(read(self.vp)["assumptions"][2]["status"], "open", "A source is not approval")
        self.assertNotIn("results", read(self.vp))
        self.assertNotIn("results", read(self.fp))

    def test_residual4_null_provenance_reports_cli_error_without_overwrite(self):
        fin = self.calculated()
        fin["results"]["finops_preview"]["provenance"] = None
        write(self.fp, fin)
        self.assert_error_no_write(self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--out", self.bpp, ACK],
                                   [self.bpp])

    def test_gap1_cli_aggregates_retain_actual_private_restrictions_and_public_counterparts(self):
        for private in (False, True):
            with self.subTest(private=private):
                fin, value, bp = self.nested_models()
                if not private:
                    fin["agents"][0].pop("internal")
                write(self.fp, fin); write(self.vp, value); write(self.bpp, bp)
                for name, module, argv in (
                    ("calc", self.fc, ["--finops", self.fp, "--value", self.vp, ACK]),
                    ("apply", self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--value", self.vp,
                                        "--out", self.bpp, ACK]),
                    ("value", self.vc, ["--value", self.vp, "--finops", self.fp, ACK]),
                ):
                    with self.subTest(cli=name):
                        code, out, err = self.call(module, argv)
                        self.assertEqual(code, 0, err)
                        summary = json.loads(out)
                        self.preview(summary)
                        self.assertEqual(summary.get("internal") is True, private,
                                         "CLI aggregates must carry the actual result/totals restriction")
                        key = "npv" if name == "value" else "total_month_chf"
                        self.assertGreater(summary[key], 0, "No withheld/private total may be presented as zero")
                saved = read(self.fp)
                public = next(a for a in saved["results"]["agents"] if a["id"] == "HR-PUB")
                self.assertAlmostEqual(public["total_month"], 10.0162, places=4)
                self.assertIsNot(public.get("internal"), True)
                public_value = next(u for u in read(self.vp)["results"]["use_cases"] if u["id"] == "UC-PUB")
                self.assertAlmostEqual(public_value["cost_month_full"], 10.0162, places=4)
                self.assertIsNot(public_value.get("internal"), True)

    def test_gap2_consumed_people_object_privacy_and_date_reach_cost_and_value(self):
        fin, value, bp = self.nested_models(source_private="people")
        private, public = fin["results"]["agents"]
        self.assertIs(private.get("internal"), True)
        self.assertIsNot(public.get("internal"), True)
        self.assertIs(private["people_source"].get("internal"), True)
        self.assertEqual(private["people_source"].get("date"), "2026-11-06")
        bp["finops"] = self.af.build_block(bp, fin, self.rates, value, acknowledge_finops_preview=True)
        self.assertIs(bp["finops"]["agents"][0]["people_source"].get("internal"), True)
        rows = {r["id"]: r for r in value["results"]["use_cases"]}
        self.assertIs(rows["UC-HR"].get("internal"), True)
        self.assertIsNot(rows["UC-PUB"].get("internal"), True)

    def test_gap2_people_object_privacy_is_enforced_in_real_customer_exports(self):
        fin, value, bp = self.nested_models(source_private="people")
        bp["finops"] = self.af.build_block(bp, fin, self.rates, value, acknowledge_finops_preview=True)
        self.av.apply(bp, value, acknowledge_finops_preview=True)
        customer, html, prd = self.customer_exports(bp, "people-private")
        for blob in (json.dumps(customer), html, prd):
            with self.subTest(channel="export"):
                self.assertFalse("PRIVATE-AGENT-SENTINEL" in blob or "30989.02" in blob or "540412.55" in blob,
                                 "Private people-derived figures/name leaked")
        self.assertEqual([a["id"] for a in customer["finops"]["agents"]], ["HR-PUB"])
        cases = {c["id"]: c for c in customer["domains"][0]["use_cases"]}
        self.assertNotIn("business_value", cases["UC-HR"])
        self.assertIn("business_value", cases["UC-PUB"])
        self.assertNotIn("totals", customer["finops"])

    def test_gap2_people_ancestry_contradiction_is_rejected_before_application(self):
        _, value, bp = self.nested_models(source_private="people")
        metadata = value["results"]["finops_preview"]
        self.assertIs(metadata["provenance"]["inputs"]["finops"]["agents"][0].get("internal"), True)
        metadata["provenance"]["inputs"]["finops"]["agents"][0]["internal"] = False
        before = copy.deepcopy(bp)
        with self.assertRaisesRegex(ValueError, "snapshot|provenance|lineage"):
            self.av.apply(bp, value, acknowledge_finops_preview=True)
        self.assertEqual(bp, before)

    def test_gap2_private_people_missing_input_reports_keep_affected_case_restrictions(self):
        fin, value, _ = self.nested_models(source_private="people")
        next(a for a in fin["assumptions"] if a["id"] == "ASS-108")["base"] = None
        fin["results"] = self.fc.run(fin, value, self.rates, acknowledge_finops_preview=True)
        self.assertIs(fin["results"]["missing"][0].get("internal"), True)
        result = self.vc.run(value, fin, acknowledge_finops_preview=True)
        rows = {r["id"]: r for r in result["use_cases"]}
        self.assertIs(rows["UC-HR"].get("internal"), True)
        self.assertIsNot(rows["UC-PUB"].get("internal"), True)

    def matrix_models(self, component, private):
        fin, value, bp = copy.deepcopy(self.fin), copy.deepcopy(self.value), copy.deepcopy(self.bp)
        rates = copy.deepcopy(self.rates)
        fin["agents"].append({
            "id": "HR-PUB", "name": "CHF-only public agent", "vars": {},
            "usage": {"sessions": 1, "billable_share": 1, "events_per_session": {}},
            "people": {"run_hours_month": 1, "rate_chf": 10, "build_one_time_chf": 0}})
        value["use_cases"].append({"id": "UC-PUB", "name": "Public case", "agents": ["HR-PUB"], "vars": {},
                                  "levers": [{"id": "PUB-L1", "name": "Public cash", "category": "cash", "formula": 100}]})
        bp["domains"][0]["agents"].append({"id": "HR-PUB", "name": "CHF-only public agent"})
        bp["domains"][0]["use_cases"].append({"id": "UC-PUB", "name": "Public case", "agents": ["HR-PUB"]})
        agent = fin["agents"][0]
        target = {
            "model-root": fin, "rates-root": rates, "agent": agent,
            "people": agent["people"], "build": agent["people"], "usage": agent["usage"],
            "outcome": agent["outcome"],
            "credits": rates["credits"], "purchase-tiers": rates["credits"],
            "events": rates["credits"]["per_event"], "event-labels": rates["credits"]["event_labels"],
            "fx-model": fin["fx"], "fx-fallback": rates["fx"], "capacity-pack": rates["credits"]["pack"],
            "guardrails": fin.setdefault("guardrails", {}), "purchase-note": fin["purchase"],
            "assumption": next(a for a in fin["assumptions"] if a["id"] == "ASS-106"),
        }.get(component)
        if component.startswith("licence"):
            agent["licences"] = [{"sku": "M365_COPILOT", "seats": 1}]
            rates["licences"]["M365_COPILOT"].update(label="LICENCE-MATRIX-SENTINEL", chf=1234.56)
            target = (agent["licences"][0] if component == "licence-selection" else
                      rates["licences"] if component == "licence-container" else rates["licences"]["M365_COPILOT"])
        elif component == "azure":
            agent["azure"] = [{"name": "AZURE-MATRIX-SENTINEL", "qty": 1, "usd": 17}]
            target = agent["azure"][0]
        elif component == "scenario":
            fin["credit_scenarios"].append({"name": "SCENARIO-MATRIX-SENTINEL", "kind": "licences", "set": {"run_hours": 17}})
            target = fin["credit_scenarios"][-1]
        if component == "fx-fallback":
            fin["fx"]["chf_per_usd"] = None
        elif component == "fx-model":
            fin["fx"]["chf_per_usd"] = 0.777777
        if component == "capacity-pack":
            target["chf_list"] = 1234.56
        if component == "outcome":
            target["name"] = "PRIVATE-OUTCOME-SENTINEL"
        if private:
            target.update(internal=True, date="2026-11-06")
        return fin, value, rates, bp, target

    def test_matrix_existing_components_propagate_to_actual_cli_and_customer_outputs(self):
        for component, _, _, scope in COMPONENT_PRIVACY_MATRIX:
            for private in (False, True):
                with self.subTest(component=component, private=private):
                    fin, value, rates, bp, _ = self.matrix_models(component, private)
                    rp = write(self.root / "matrix-rates.json", rates)
                    write(self.fp, fin); write(self.vp, value); write(self.bpp, bp)
                    replies = {}
                    for name, module, args in (
                        ("calc", self.fc, ["--finops", self.fp, "--value", self.vp, "--rates", rp, ACK]),
                        ("value", self.vc, ["--value", self.vp, "--finops", self.fp, ACK]),
                        ("apply", self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--value", self.vp,
                                           "--rates", rp, "--out", self.bpp, ACK]),
                    ):
                        code, out, err = self.call(module, args)
                        self.assertEqual(code, 0, err)
                        replies[name] = json.loads(out)
                    fin, value, bp = read(self.fp), read(self.vp), read(self.bpp)
                    self.av.apply(bp, value, acknowledge_finops_preview=True)
                    customer, html, prd = self.customer_exports(bp, "matrix")
                    hidden = private and scope in {"first", "all"}
                    for name, reply in replies.items():
                        with self.subTest(output=f"stdout-{name}"):
                            self.assertEqual(reply.get("internal") is True, hidden)
                    cases = {u["id"]: u for u in customer["domains"][0]["use_cases"]}
                    with self.subTest(output="dependent-value"):
                        self.assertEqual("business_value" in cases["UC-HR"], not hidden)
                        self.assertEqual("business_value" in cases["UC-PUB"], not (private and scope == "all"))
                    f = customer.get("finops", {})
                    with self.subTest(output="public-agent"):
                        self.assertEqual(any(a["id"] == "HR-PUB" for a in f.get("agents", [])), not (private and scope == "all"))
                    if component.startswith("licence") and private:
                        with self.subTest(output="sku-rate-exports"):
                            self.assertFalse(any("LICENCE-MATRIX-SENTINEL" in text or "1234.56" in text
                                                 for text in (json.dumps(customer), html, prd)))
                    if component == "capacity-pack":
                        with self.subTest(output="pack-rate-option"):
                            self.assertEqual(any(r.get("label", "").startswith("Capacity pack") for r in f.get("rates", [])), not private)
                            self.assertEqual(any(o["option"] == "packs" for o in f.get("purchase_options", [])), not private)
                            self.assertEqual("internal_notes" in f, False)
                    if component == "scenario":
                        with self.subTest(output="scenario-exports"):
                            self.assertEqual("SCENARIO-MATRIX-SENTINEL" in html, not private)
                            self.assertEqual(any(s["name"] == "SCENARIO-MATRIX-SENTINEL"
                                                 for s in f.get("credit_scenarios", [])), not private)
                    if component == "guardrails" and private:
                        with self.subTest(output="control-rows"):
                            self.assertEqual(f.get("guardrails"), [])
                    if component == "outcome":
                        with self.subTest(output="outcome-unit-exports"):
                            self.assertEqual("PRIVATE-OUTCOME-SENTINEL" in html, not private)
                            unit = next(a for a in f["agents"] if a["id"] == "HR-A01")["unit"]
                            self.assertIn("per_session", unit)
                            self.assertEqual("per_outcome" in unit, not private)
                    if private and scope in {"comparison", "scenario"}:
                        with self.subTest(output="aggregate-prose"):
                            self.assertEqual(f.get("lessons"), [])

    def test_matrix_unused_private_optional_components_are_not_consumed_or_presented(self):
        fin, value, rates, bp, _ = self.matrix_models("agent", False)
        # Explicit FX and licence price/label: these private alternatives are NOT selected.
        rates["fx"].update(internal=True, swiss_list_ratio=0.987654)
        rates["licences"]["M365_COPILOT"].update(internal=True, label="UNUSED-SKU-SENTINEL", chf=1234.56)
        fin["agents"][0]["licences"] = [{"sku": "M365_COPILOT", "chf": 10, "label": "Public explicit licence", "seats": 1}]
        fin["assumptions"].append({"id": "UNUSED-PRIVATE", "internal": True, "base": 999999})
        fin["results"] = self.fc.run(fin, value, rates, acknowledge_finops_preview=True)
        value["results"] = self.vc.run(value, fin, acknowledge_finops_preview=True)
        bp["finops"] = self.af.build_block(bp, fin, rates, value, acknowledge_finops_preview=True)
        self.av.apply(bp, value, acknowledge_finops_preview=True)
        customer, html, _ = self.customer_exports(bp, "unused-matrix")
        self.assertIn("business_value", customer["domains"][0]["use_cases"][0])
        self.assertFalse("UNUSED-SKU-SENTINEL" in html or "1234.56" in html or "0.987654" in html)

    def test_matrix_private_consumed_components_mutated_after_calculation_are_rejected(self):
        for component, _, _, _ in COMPONENT_PRIVACY_MATRIX:
            with self.subTest(component=component):
                fin, value, rates, bp, target = self.matrix_models(component, True)
                fin["results"] = self.fc.run(fin, value, rates, acknowledge_finops_preview=True)
                value["results"] = self.vc.run(value, fin, acknowledge_finops_preview=True)
                target["date"] = "2099-01-01"
                with self.assertRaisesRegex(ValueError, "stale|different rates|calculation"):
                    self.af.build_block(bp, fin, rates, value, acknowledge_finops_preview=True)

    def test_matrix_missing_input_reports_keep_selected_component_ancestry(self):
        for component, _, _, scope in COMPONENT_PRIVACY_MATRIX:
            if scope not in {"first", "all"}:
                continue
            with self.subTest(component=component):
                fin, value, rates, _, _ = self.matrix_models(component, True)
                next(a for a in fin["assumptions"] if a["id"] == "ASS-108")["base"] = None
                fin["results"] = self.fc.run(fin, value, rates, acknowledge_finops_preview=True)
                result = self.vc.run(value, fin, acknowledge_finops_preview=True)
                self.assertTrue(fin["results"]["missing"])
                self.assertIs(next(r for r in result["use_cases"] if r["id"] == "UC-HR").get("internal"), True)
                public = next(r for r in result["use_cases"] if r["id"] == "UC-PUB")
                self.assertEqual(public.get("internal") is True, scope == "all")

    def test_boundary_outcome_private_details_preserve_public_costs_and_cli_values(self):
        for private in (False, True):
            with self.subTest(private=private):
                fin, value, rates, bp, _ = self.matrix_models("outcome", private)
                rp = write(self.root / "outcome-rates.json", rates)
                write(self.fp, fin); write(self.vp, value); write(self.bpp, bp)
                for module, args in (
                    (self.fc, ["--finops", self.fp, "--value", self.vp, "--rates", rp, ACK]),
                    (self.vc, ["--value", self.vp, "--finops", self.fp, ACK]),
                    (self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--value", self.vp,
                               "--rates", rp, "--out", self.bpp, ACK]),
                ):
                    code, out, err = self.call(module, args)
                    self.assertEqual(code, 0, err)
                    self.assertIsNot(json.loads(out).get("internal"), True)
                    self.assertFalse("PRIVATE-OUTCOME-SENTINEL" in out)
                value, bp = read(self.vp), read(self.bpp)
                self.av.apply(bp, value, acknowledge_finops_preview=True)
                customer, html, prd = self.customer_exports(bp, f"outcome-{private}")
                unit = next(a for a in customer["finops"]["agents"] if a["id"] == "HR-A01")["unit"]
                self.assertIn("per_session", unit)
                with self.subTest(output="unit-json"):
                    self.assertEqual("per_outcome" in unit, not private)
                with self.subTest(output="customer-html"):
                    self.assertEqual("PRIVATE-OUTCOME-SENTINEL" in html, not private)
                self.assertIn("business_value", customer["domains"][0]["use_cases"][0])
                self.assertNotIn("PRIVATE-OUTCOME-SENTINEL", prd)

    def test_boundary_outcome_ancestry_dates_and_fingerprint_are_preserved(self):
        fin, value, rates, _, _ = self.matrix_models("outcome", True)
        fin["agents"][0]["outcome"]["date"] = "2026-11-06"
        fin["results"] = self.fc.run(fin, value, rates, acknowledge_finops_preview=True)
        unit = fin["results"]["agents"][0]["unit"]
        self.assertIn("internal_notes", unit, "Private outcome details need an independently projectable container")
        private_details = unit["internal_notes"]["outcome"]
        self.assertIs(private_details["internal"], True)
        self.assertEqual(private_details["date"], "2026-11-06")
        self.assertEqual(len(private_details["fingerprint"]), 64)
        value["results"] = self.vc.run(value, fin, acknowledge_finops_preview=True)
        ancestry = value["results"]["finops_preview"]["provenance"]["inputs"]["finops"]["agents"][0]
        self.assertIs(ancestry["outcome_source"]["internal"], True)
        self.assertIsNot(ancestry.get("internal"), True)
        ancestry["outcome_source"]["date"] = "2099-01-01"
        with self.assertRaisesRegex(ValueError, "snapshot|provenance|lineage"):
            self.av.apply(self.bp, value, acknowledge_finops_preview=True)

    def test_boundary_chf_only_comparisons_select_actual_explicit_or_fallback_fx(self):
        for component in ("fx-model", "fx-fallback"):
            for private in (False, True):
                with self.subTest(component=component, private=private):
                    fin, value, rates, bp, _ = self.matrix_models(component, private)
                    for agent in fin["agents"]:
                        agent["usage"]["events_per_session"] = {}
                        agent["azure"] = []
                    fin["results"] = self.fc.run(fin, value, rates, acknowledge_finops_preview=True)
                    options = {o["option"]: o for o in fin["results"]["purchase_options"]}
                    for option in ("cc-p3", "agent-p3"):
                        with self.subTest(output=option):
                            self.assertEqual(options[option].get("internal") is True, private)
                    self.assertIsNot(fin["results"]["totals"].get("internal"), True)
                    self.assertIsNot(options["packs"].get("internal"), True)
                    self.assertIsNot(options["payg"].get("internal"), True)
                    value["results"] = self.vc.run(value, fin, acknowledge_finops_preview=True)
                    bp["finops"] = self.af.build_block(bp, fin, rates, value, acknowledge_finops_preview=True)
                    self.av.apply(bp, value, acknowledge_finops_preview=True)
                    customer, html, _ = self.customer_exports(bp, f"chf-fx-{component}-{private}")
                    ids = {o["option"] for o in customer["finops"]["purchase_options"]}
                    self.assertEqual(ids, {"payg", "packs"} if private else {"payg", "packs", "cc-p3", "agent-p3"})
                    self.assertIn("business_value", customer["domains"][0]["use_cases"][0])
                    self.assertIn("totals", customer["finops"])
                    if private:
                        self.assertEqual(customer["finops"]["lessons"], [])
                        self.assertFalse('"annual_chf":2216.66' in html or '"annual_chf":14777.76' in html)

    def test_ranking_private_candidate_withholds_selection_not_public_amounts(self):
        for private in (False, True):
            for pack_price in (1, 1234.56):
                with self.subTest(private=private, pack_price=pack_price):
                    fin, value, rates, bp, _ = self.matrix_models("capacity-pack", private)
                    rates["credits"]["pack"]["chf_list"] = pack_price
                    rp = write(self.root / "ranking-rates.json", rates)
                    write(self.fp, fin); write(self.vp, value); write(self.bpp, bp)
                    code, out, err = self.call(self.fc, ["--finops", self.fp, "--value", self.vp, "--rates", rp, ACK])
                    self.assertEqual(code, 0, err)
                    reply = json.loads(out)
                    with self.subTest(output="cli-selection"):
                        self.assertEqual("lowest_option" in reply, not private)
                        if private:
                            self.assertEqual(reply["ranking_status"], "withheld-private-candidates")
                    fin = read(self.fp)
                    code, out, err = self.call(self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--value", self.vp,
                                                        "--rates", rp, "--out", self.bpp, ACK])
                    self.assertEqual(code, 0, err)
                    customer, html, _ = self.customer_exports(read(self.bpp), f"ranking-{private}-{pack_price}")
                    options = customer["finops"]["purchase_options"]
                    self.assertTrue(options, "Do not blanket-hide independent public price amounts")
                    for option in options:
                        with self.subTest(output=f"row-{option['option']}"):
                            self.assertGreaterEqual(option["annual_chf"], 0)
                            self.assertEqual("lowest" in option, not private)
                            self.assertIn("vs_payg", option, "Public pairwise PAYG comparisons stay public")
                    if private:
                        self.assertFalse('"lowest":false' in html or '"lowest":true' in html)
                    else:
                        winner = next(o for o in options if o["lowest"])
                        self.assertEqual(reply["lowest_option"], winner["label"])
                        self.assertEqual(winner["option"] == "packs", pack_price == 1)

    def test_ranking_private_payg_withholds_pairwise_flags_without_zero_fallback(self):
        # With public CHF pack prices, the pack amount is independent of private
        # FX, but its relative-to-PAYG percentage and cross-option rank are not.
        fin, value, rates, bp, _ = self.matrix_models("fx-model", True)
        fin["results"] = self.fc.run(fin, value, rates, acknowledge_finops_preview=True)
        bp["finops"] = self.af.build_block(bp, fin, rates, value, acknowledge_finops_preview=True)
        customer, html, _ = self.customer_exports(bp, "private-payg-ranking")
        # Some fixtures restrict the complete candidate due to base inputs. Any
        # retained public candidate must never publish derived private flags.
        for option in customer["finops"]["purchase_options"]:
            self.assertNotIn("lowest", option)
            self.assertNotIn("vs_payg", option)
        self.assertFalse('"lowest":false' in html or '"lowest":true' in html)

    def test_quality_fingerprint_binds_authored_metadata_named_arithmetic_variables(self):
        helper = script(FIN, "finops_preview")
        for name in ("results", "finops_preview", "maturity", "acknowledgement",
                     "acknowledged", "preview_acknowledged", "rates_version"):
            with self.subTest(variable=name):
                fin = copy.deepcopy(self.fin)
                fin["agents"][0]["vars"][name] = 1.0
                fin["agents"][0]["usage"]["billable_share"] = name
                fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
                original = helper.fingerprint(fin)
                fin["agents"][0]["vars"][name] = 0.5
                with self.subTest(check="fingerprint"):
                    self.assertNotEqual(helper.fingerprint(fin), original, "Authored variables must not be projected away")
                with self.subTest(check="api-refusal"):
                    with self.assertRaisesRegex(ValueError, "stale|calculation|recalculate"):
                        self.vc.run(self.value, fin, acknowledge_finops_preview=True)
                fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
                result = self.vc.run(self.value, fin, acknowledge_finops_preview=True)
                self.assertAlmostEqual(result["use_cases"][0]["cost_month_full"], 2472.015, places=3)

    def test_quality_stale_metadata_named_variable_cli_refuses_without_overwrite(self):
        fin = copy.deepcopy(self.fin)
        fin["agents"][0]["vars"]["maturity"] = 1.0
        fin["agents"][0]["usage"]["billable_share"] = "maturity"
        fin["results"] = self.fc.run(fin, self.value, self.rates, acknowledge_finops_preview=True)
        self.assertAlmostEqual(fin["results"]["totals"]["total_month"], 3024.03, places=3)
        fin["agents"][0]["vars"]["maturity"] = 0.5
        write(self.fp, fin)
        self.assert_error_no_write(self.af, ["--blueprint", self.bpp, "--finops", self.fp, "--value", self.vp,
                                            "--out", self.bpp, ACK], [self.bpp])
        self.assert_error_no_write(self.vc, ["--value", self.vp, "--finops", self.fp, ACK], [self.vp])

    def test_quality_fingerprint_preserves_all_other_authored_mappings(self):
        helper = script(FIN, "finops_preview")
        for name in ("results", "finops_preview", "maturity", "acknowledgement",
                     "acknowledged", "preview_acknowledged", "rates_version"):
            for schema in ("frontier-finops/1.0", "frontier-value/1.0", "frontier-rates/1.0"):
                with self.subTest(name=name, schema=schema):
                    doc = {"schema": schema, "authored": {name: 1.0},
                           "rows": [{"vars": {name: 1.0}}]}
                    changed = copy.deepcopy(doc)
                    changed["authored"][name] = 0.5
                    self.assertNotEqual(helper.fingerprint(doc), helper.fingerprint(changed))

    def test_quality_generated_receipt_updates_do_not_change_model_or_result_hashes(self):
        helper = script(FIN, "finops_preview")
        fin, value = self.costed_models()
        model_fp, result_fp = helper.fingerprint(fin), helper.fingerprint(value["results"], result_kind="value")
        fin["finops_preview"]["acknowledgement"]["scope"] = "changed-metadata-only"
        fin["results"]["finops_preview"]["calculations"]["finops"]["results_fingerprint"] = "0" * 64
        self.assertEqual(helper.fingerprint(fin), model_fp)
        value["results"]["finops_preview"]["acknowledgement"]["scope"] = "changed-metadata-only"
        self.assertEqual(helper.fingerprint(value["results"], result_kind="value"), result_fp)
        # Metadata cannot supply a fresh invocation's acknowledgement.
        with self.assertRaisesRegex(ValueError, ACK):
            self.vc.run(self.value, fin)

    def test_quality_arithmetic_variable_is_not_a_preview_metadata_location(self):
        value = copy.deepcopy(self.value)
        value["use_cases"][0]["vars"]["finops_preview"] = 10
        value["use_cases"][0]["levers"][0]["formula"] = "finops_preview"
        with mock.patch.object(self.vc, "FINOPS_PREVIEW", self.root / "not-installed.py"):
            result = self.vc.run(value, None)
        self.assertNotIn("finops_preview", result)
        self.assertEqual(result["use_cases"][0]["monthly_full"]["economic"], 10)

    def test_wrapper_domain_api_refuses_before_copying_models(self):
        args = type("Args", (), {"finops": str(self.fp), "value": str(self.vp),
                                  "acknowledge_finops_preview": False})()
        target = self.root / "output"
        with mock.patch.object(self.wrapper, "run", return_value=(0, "{}", "")) as child:
            with self.assertRaisesRegex(ValueError, ACK):
                self.wrapper.build_value_finops(args, self.bpp, target, {"notes": []})
            child.assert_not_called()
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
