"""Baseline contract and pure Decimal calculator checkpoint tests."""
from __future__ import annotations

import copy
import itertools
import json
import sys
import unittest
from datetime import date
from decimal import Inexact, ROUND_FLOOR, Rounded, localcontext
from unittest import mock

from tests.unit._util import ROOT, load

FIN = ROOT / "plugin" / "skills" / "frontier-finops"
DAY = date(2026, 11, 12)
_NAMES = itertools.count()


def baseline_module(name="baseline_model"):
    with mock.patch.object(sys, "path", [str(FIN / "scripts"), *sys.path]):
        return load(f"plugin/skills/frontier-finops/scripts/{name}.py",
                    f"agent_baseline_{name}_{next(_NAMES)}")


def example():
    return json.loads((FIN / "examples" / "caldova-agent-baseline.json").read_text(encoding="utf-8"))


def put(model, path, value):
    row = model
    for key in path[:-1]:
        row = row[key]
    row[path[-1]] = value


def reorder_objects(value, order):
    """Permute object keys recursively, never authored array order."""
    if isinstance(value, dict):
        keys = list(value)
        if order == "sorted":
            keys.sort()
        elif order == "reverse":
            keys.reverse()
        elif keys:
            keys = keys[1:] + keys[:1]
        return {key: reorder_objects(value[key], order) for key in keys}
    if isinstance(value, list):
        return [reorder_objects(child, order) for child in value]
    return copy.deepcopy(value)


class BaselineContractTests(unittest.TestCase):
    def setUp(self):
        # An absent implementation must be an intentional assertion RED, not a loader error.
        self.assertTrue((FIN / "scripts" / "baseline_model.py").is_file(),
                        "Task1 baseline_model.py/API has not been implemented")
        self.module = baseline_module()
        self.model = example()

    def gaps(self, model=None, **kwargs):
        return self.module.validate_model(self.model if model is None else model, as_of=DAY, **kwargs)

    def assert_missing_text_equivalent(self, path, code, field):
        canonical = example()
        put(canonical, path, None)
        expected = self.gaps(canonical)
        self.assertTrue(any(g["code"] == code and g["field"] == field for g in expected))
        for value in (None, "", "   "):
            model = example()
            put(model, path, value)
            original = copy.deepcopy(model)
            with self.subTest(field=field, value=value):
                try:
                    actual = self.gaps(model)
                except ValueError as error:
                    self.fail(f"Missing editable metadata must return gaps, not a contradiction: {error}")
                self.assertEqual(actual, expected)
                self.assertEqual(model, original)
        return expected

    def test_synthetic_example_has_math_inputs_but_never_financial_readiness(self):
        gaps = self.gaps()
        self.assertIn("synthetic-evidence", {g["code"] for g in gaps})
        self.assertFalse(any("calculation" in g["blocks"] or "unit-metrics" in g["blocks"] for g in gaps))
        self.assertTrue(all("handover" in g["blocks"] for g in gaps))
        for g in gaps:
            self.assertEqual(set(g), {"code", "field", "message", "blocks"})
            self.assertTrue(g["field"])
        self.assertEqual(self.model["profile"]["agent_id"], "D3-A05")
        self.assertEqual(self.model["profile"]["name"], "Service Report Agent")
        self.assertEqual(self.model["profile"]["canvas"]["lifecycle"], "Planned")
        self.assertEqual(self.model["profile"]["canvas"]["autonomy"], "Act with approval")
        self.assertEqual(self.model["profile"]["owners"]["finance"], "Finance lead")
        self.assertEqual(self.model["preview_notice"], baseline_module("finops_preview").NOTICE)
        self.assertNotIn("acknowledgement", self.model)
        for scenario, demand, tokens in zip(self.model["baseline"]["scenarios"],
                                            ("50", "100", "200"), ("500", "1000", "2000")):
            self.assertEqual(scenario["monthly_runs"], [demand] * 12)
            self.assertEqual(scenario["drivers"]["tokens_per_run"], tokens)
            self.assertEqual(scenario["success_share"], "0.5")
            self.assertEqual(scenario["outcomes_per_success"], "2")

    def test_validation_is_pure_and_deterministic(self):
        original = copy.deepcopy(self.model)
        self.assertEqual(self.gaps(), self.gaps())
        self.assertEqual(self.model, original)

    def test_scenarios_need_another_driver_besides_demand(self):
        for scenario in self.model["baseline"]["scenarios"]:
            scenario["drivers"]["tokens_per_run"] = "1000"
        self.assertIn("scenario-uncertainty", {g["code"] for g in self.gaps()})

    def test_other_uncertainty_does_not_replace_varying_demand(self):
        for scenario in self.model["baseline"]["scenarios"]:
            scenario["monthly_runs"] = ["100"] * 12
        self.assertIn("scenario-demand", {g["code"] for g in self.gaps()})

    def test_success_can_be_the_other_uncertainty_driver(self):
        for scenario, share in zip(self.model["baseline"]["scenarios"], ("0.3", "0.5", "0.7")):
            scenario["drivers"]["tokens_per_run"] = "1000"
            scenario["success_share"] = share
        self.assertNotIn("scenario-uncertainty", {g["code"] for g in self.gaps()})

    def test_uncertainty_dependency_referenced_fixed_quantity_qualifies(self):
        for scenario, quantity in zip(self.model["baseline"]["scenarios"], ("1", "2", "3")):
            scenario["drivers"]["tokens_per_run"] = "1000"
            scenario["drivers"]["operations_units"] = quantity
        self.assertNotIn("scenario-uncertainty", {g["code"] for g in self.gaps()})

    def test_uncertainty_dependency_unused_retries_cannot_qualify(self):
        for scenario, retries in zip(self.model["baseline"]["scenarios"], ("1", "2", "3")):
            scenario["drivers"]["tokens_per_run"] = "1000"
            scenario["drivers"]["retries"] = retries
            scenario["driver_evidence"]["retries"] = {
                "unit": "call", "source_id": "SYN-ENGINEERING",
                "sharingClassification": "customer-shareable",
            }
        self.assertIn("scenario-uncertainty", {g["code"] for g in self.gaps()})

    def test_uncertainty_dependency_outcomes_per_success_qualifies(self):
        for scenario, outcomes in zip(self.model["baseline"]["scenarios"], ("1", "2", "3")):
            scenario["drivers"]["tokens_per_run"] = "1000"
            scenario["outcomes_per_success"] = outcomes
        self.assertNotIn("scenario-uncertainty", {g["code"] for g in self.gaps()})

    def test_uncertainty_dependency_renamed_referenced_driver_qualifies(self):
        for scenario in self.model["baseline"]["scenarios"]:
            scenario["drivers"]["input_volume"] = scenario["drivers"].pop("tokens_per_run")
            scenario["driver_evidence"]["input_volume"] = scenario["driver_evidence"].pop("tokens_per_run")
        self.model["baseline"]["lines"][0]["driver_id"] = "input_volume"
        self.assertNotIn("scenario-uncertainty", {g["code"] for g in self.gaps()})

    def test_uncertainty_dependency_compares_decimal_values_not_spellings(self):
        for scenario, tokens, units in zip(self.model["baseline"]["scenarios"],
                                           ("1000", "1000.0", "1e3"), ("1", "1.0", "1e0")):
            scenario["drivers"]["tokens_per_run"] = tokens
            scenario["drivers"]["operations_units"] = units
        self.assertIn("scenario-uncertainty", {g["code"] for g in self.gaps()})

    def test_uncertainty_dependency_demand_must_still_vary(self):
        for scenario, quantity in zip(self.model["baseline"]["scenarios"], ("1", "2", "3")):
            scenario["monthly_runs"] = ["100"] * 12
            scenario["drivers"]["tokens_per_run"] = "1000"
            scenario["drivers"]["operations_units"] = quantity
        codes = {g["code"] for g in self.gaps()}
        self.assertIn("scenario-demand", codes)
        self.assertNotIn("scenario-uncertainty", codes)

    def test_uncertainty_dependency_variation_needs_its_source_reference(self):
        for key, values in (("operations_units", ("1", "2", "3")),
                            ("success_share", ("0.3", "0.5", "0.7")),
                            ("outcomes_per_success", ("1", "2", "3"))):
            model = example()
            for scenario, value in zip(model["baseline"]["scenarios"], values):
                scenario["drivers"]["tokens_per_run"] = "1000"
                if key in scenario["drivers"]:
                    scenario["drivers"][key] = value
                else:
                    scenario[key] = value
                scenario["driver_evidence"][key]["source_id"] = None
            with self.subTest(key=key):
                codes = {g["code"] for g in self.gaps(model)}
                self.assertIn("missing-evidence", codes)
                self.assertIn("scenario-uncertainty", codes)

    def test_uncertainty_dependency_concept_evidence_does_not_source_quantities(self):
        for scenario, share in zip(self.model["baseline"]["scenarios"], ("0.3", "0.5", "0.7")):
            scenario["drivers"]["tokens_per_run"] = "1000"
            scenario["success_share"] = share
        self.model["sources"][1]["applicability"] = ["concept"]
        codes = {g["code"] for g in self.gaps()}
        self.assertIn("source-applicability", codes)
        self.assertIn("scenario-uncertainty", codes)

    def test_unknown_rate_reference_is_an_explicit_error(self):
        self.model["baseline"]["lines"][0]["rate_id"] = "NO-SUCH-RATE"
        with self.assertRaisesRegex(ValueError, "rate"):
            self.gaps()

    def test_duplicate_ids_are_rejected_in_owned_collections(self):
        for path in (("rates",), ("sources",), ("baseline", "lines"),
                     ("baseline", "scenarios"), ("baseline", "scope"),
                     ("baseline", "assumptions")):
            model = example()
            rows = model
            for key in path:
                rows = rows[key]
            rows.append(copy.deepcopy(rows[0]))
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "duplicate"):
                self.gaps(model)

    def test_optional_blueprint_checks_the_actual_domain_agent_link(self):
        blueprint = json.loads((ROOT / "plugin/skills/frontier-blueprint/examples/caldova-blueprint.json")
                               .read_text(encoding="utf-8"))
        self.gaps(blueprint=blueprint)
        self.model["profile"]["agent_id"] = "UNKNOWN-AGENT"
        self.model["baseline"]["agent_id"] = "UNKNOWN-AGENT"
        with self.assertRaisesRegex(ValueError, "agent_id"):
            self.gaps(blueprint=blueprint)

    def test_profile_and_baseline_agent_references_must_agree(self):
        self.model["baseline"]["agent_id"] = "D1-A01"
        with self.assertRaisesRegex(ValueError, "agent_id"):
            self.gaps()

    def test_schema_structure_enums_and_month_count_are_checked(self):
        cases = [
            (("schema",), "frontier-finops-baseline/9.0", "schema"),
            (("mode",), "actual", "mode"),
            (("forecast_kind",), "measured-actual", "forecast_kind"),
            (("baseline",), [], "baseline"),
            (("baseline", "version"), True, "version"),
            (("baseline", "version"), 0, "version"),
            (("baseline", "scenarios", 0, "monthly_runs"), ["50"], "monthly_runs"),
            (("baseline", "lines", 0, "frequency"), "annual", "frequency"),
            (("baseline", "lines", 0, "quantity_mode"), "guessed", "quantity_mode"),
            (("baseline", "scenarios", 0, "drivers"), [], "drivers"),
        ]
        for path, value, field in cases:
            model = example()
            put(model, path, value)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, field):
                self.gaps(model)

    def test_dates_and_date_order_are_checked_without_echoing_input(self):
        for path in (("baseline", "as_of"), ("baseline", "start_month"),
                     ("rates", 0, "effective_from"), ("sources", 0, "lastValidatedAt")):
            model = example()
            put(model, path, "PRIVATE invalid date")
            with self.subTest(path=path), self.assertRaises(ValueError) as caught:
                self.gaps(model)
            self.assertIn(path[-1], str(caught.exception))
            self.assertNotIn("PRIVATE", str(caught.exception))
        self.model["rates"][0]["effective_to"] = "2026-01-01"
        with self.assertRaisesRegex(ValueError, "effective_to"):
            self.gaps()
        with self.assertRaisesRegex(ValueError, "as_of"):
            self.module.validate_model(example(), as_of="2026-11-12")

    def test_unsupported_currencies_are_not_inferred(self):
        for path in (("baseline", "currency"), ("rates", 0, "currency")):
            model = example()
            put(model, path, "GBP")
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "currency"):
                self.gaps(model)

    def test_decimal_inputs_reject_booleans_native_numbers_negative_and_nonfinite(self):
        paths = (("rates", 0, "amount"), ("rates", 0, "pricing_block"),
                 ("baseline", "scenarios", 0, "monthly_runs", 0),
                 ("baseline", "scenarios", 0, "success_share"),
                 ("baseline", "scenarios", 0, "outcomes_per_success"),
                 ("baseline", "scenarios", 0, "drivers", "tokens_per_run"))
        for path in paths:
            for value in (True, 1, 0.5, "-1", "NaN", "Infinity", "-Infinity", ""):
                model = example()
                put(model, path, value)
                with self.subTest(path=path, value=value), self.assertRaises(ValueError) as caught:
                    self.gaps(model)
                self.assertIn(str(path[-1]), str(caught.exception))
        for path, value in ((("rates", 0, "pricing_block"), "0"),
                            (("baseline", "scenarios", 0, "success_share"), "1.01"),
                            (("rates", 0, "freshness_policy", "max_age_days"), True)):
            model = example()
            put(model, path, value)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, str(path[-1])):
                self.gaps(model)

    def test_known_zero_denominators_are_data_not_missing_inputs(self):
        scenario = self.model["baseline"]["scenarios"][0]
        scenario["monthly_runs"] = ["0"] * 12
        scenario["success_share"] = "0"
        scenario["outcomes_per_success"] = "0"
        self.assertFalse(any("unit-metrics" in g["blocks"] or "calculation" in g["blocks"] for g in self.gaps()))

    def test_null_rate_quantity_and_denominator_have_different_named_gaps(self):
        self.model["rates"][0]["amount"] = None
        self.model["baseline"]["scenarios"][0]["monthly_runs"][0] = None
        self.model["baseline"]["scenarios"][1]["outcomes_per_success"] = None
        gaps = self.gaps()
        for code, block in (("unpriced", "calculation"), ("missing-quantity", "calculation"),
                            ("missing-outcome", "unit-metrics")):
            self.assertTrue(any(g["code"] == code and block in g["blocks"] for g in gaps))
        self.assertTrue(all("handover" in g["blocks"] for g in gaps))

    def test_denominator_metadata_and_category_gaps_do_not_erase_known_cost_inputs(self):
        self.model["baseline"]["scenarios"][0]["driver_evidence"]["success_share"] = None
        self.model["baseline"]["scenarios"][1]["driver_evidence"]["outcomes_per_success"]["unit"] = None
        self.model["baseline"]["lines"][0]["category"] = None
        gaps = self.gaps()
        self.assertFalse(any("calculation" in g["blocks"] for g in gaps))
        self.assertTrue(any("unit-metrics" in g["blocks"] for g in gaps))
        self.assertIn("missing-line-input", {g["code"] for g in gaps})

    def test_empty_scope_and_unrepresented_driver_are_gaps_not_empty_complete_coverage(self):
        self.model["baseline"]["scope"] = []
        self.model["baseline"]["lines"] = []  # Empty draft, not supplied dangling references.
        self.assertIn("empty-scope", {g["code"] for g in self.gaps()})
        self.model = example()
        self.model["baseline"]["lines"].pop()
        self.assertIn("uncovered-driver", {g["code"] for g in self.gaps()})

    def test_empty_scope_reference_unknown_id_still_raises(self):
        self.model["baseline"]["scope"] = []
        self.model["baseline"]["lines"] = self.model["baseline"]["lines"][:1]
        self.model["baseline"]["lines"][0]["cost_driver_id"] = "UNKNOWN"
        with self.assertRaisesRegex(ValueError, r"baseline\.lines\[0\]\.cost_driver_id"):
            self.gaps()

    def test_empty_scope_reference_absent_lines_remains_a_draft_gap(self):
        self.model["baseline"]["scope"] = []
        self.model["baseline"]["lines"] = []
        gaps = self.gaps()
        self.assertTrue(any(g["code"] == "empty-scope" and g["field"] == "baseline.scope" for g in gaps))

    def test_empty_scope_reference_missing_id_remains_a_field_specific_gap(self):
        for value in (None, "", " "):
            model = example()
            model["baseline"]["scope"] = []
            model["baseline"]["lines"] = model["baseline"]["lines"][:1]
            model["baseline"]["lines"][0]["cost_driver_id"] = value
            with self.subTest(value=value):
                self.assertTrue(any(g["code"] == "missing-scope" and g["field"] == "baseline.lines[0].cost_driver_id"
                                    for g in self.gaps(model)))

    def test_missing_editable_profile_and_baseline_inputs_are_explicit(self):
        self.model["profile"]["owners"]["finance"] = None
        self.model["profile"]["outcome"]["definition"] = None
        self.model["profile"]["measurement_plan"] = ""
        self.model["profile"]["guardrails"] = []
        self.model["baseline"]["confidence"] = None
        codes = {g["code"] for g in self.gaps()}
        self.assertTrue({"missing-owner", "missing-outcome", "missing-measurement",
                         "missing-guardrails", "missing-confidence"} <= codes)

    def test_missing_driver_is_a_gap_but_unknown_driver_and_source_ids_are_errors(self):
        del self.model["baseline"]["scenarios"][0]["drivers"]["tokens_per_run"]
        self.assertIn("missing-quantity", {g["code"] for g in self.gaps()})
        for path in (("baseline", "lines", 0, "driver_id"),
                     ("baseline", "scenarios", 0, "driver_evidence", "tokens_per_run", "source_id"),
                     ("rates", 0, "source_id")):
            model = example()
            put(model, path, "NO-SUCH-REFERENCE")
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, str(path[-1])):
                self.gaps(model)

    def test_line_rate_and_driver_units_service_and_meter_must_match(self):
        for path, value in ((("baseline", "lines", 0, "quantity_unit"), "hour"),
                            (("rates", 0, "unit"), "unknown-unit"),
                            (("rates", 0, "service"), "another-service"),
                            (("rates", 0, "meter"), "another-meter"),
                            (("baseline", "scenarios", 0, "driver_evidence",
                              "tokens_per_run", "unit"), "call")):
            model = example()
            put(model, path, value)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unit|service|meter"):
                self.gaps(model)

    def test_outcome_driver_unit_must_match_the_profile_business_unit(self):
        self.model["profile"]["outcome"]["unit"] = "run"
        with self.assertRaisesRegex(ValueError, "unit"):
            self.gaps()
        for scenario in self.model["baseline"]["scenarios"]:
            scenario["driver_evidence"]["outcomes_per_success"]["unit"] = "run"
        self.gaps()

    def test_missing_metadata_normalization_outcome_unit_preserves_known_cost_inputs(self):
        gaps = self.assert_missing_text_equivalent(
            ("profile", "outcome", "unit"), "missing-outcome", "profile.outcome.unit")
        self.assertFalse(any("calculation" in g["blocks"] for g in gaps))
        self.assertTrue(any(g["code"] == "missing-outcome" and g["blocks"] == ["handover", "unit-metrics"]
                            for g in gaps))

    def test_missing_metadata_normalization_line_units_service_and_meter(self):
        for key in ("quantity_unit", "service", "meter"):
            self.assert_missing_text_equivalent(
                ("baseline", "lines", 0, key), "missing-line-input", f"baseline.lines[0].{key}")

    def test_missing_metadata_normalization_rate_units_service_meter_and_currency(self):
        for key in ("unit", "service", "meter", "currency"):
            gaps = self.assert_missing_text_equivalent(
                ("rates", 0, key), "missing-rate-input", f"rates[0].{key}")
            self.assertFalse(any(g["code"] == "missing-fx" for g in gaps))

    def test_missing_metadata_normalization_scenario_driver_units(self):
        for key, code in (("tokens_per_run", "missing-quantity"),
                          ("success_share", "missing-outcome"), ("outcomes_per_success", "missing-outcome")):
            gaps = self.assert_missing_text_equivalent(
                ("baseline", "scenarios", 0, "driver_evidence", key, "unit"), code,
                f"baseline.scenarios[0].driver_evidence.{key}.unit")
            if code == "missing-outcome":
                self.assertFalse(any("calculation" in g["blocks"] for g in gaps))

    def test_missing_metadata_normalization_references_keep_field_specific_gaps(self):
        for path, code, field in (
            (("profile", "agent_id"), "missing-agent", "profile.agent_id"),
            (("baseline", "agent_id"), "missing-agent", "baseline.agent_id"),
            (("baseline", "lines", 0, "cost_driver_id"), "missing-scope", "baseline.lines[0].cost_driver_id"),
            (("baseline", "lines", 0, "driver_id"), "missing-quantity", "baseline.lines[0].driver_id"),
            (("baseline", "lines", 0, "rate_id"), "unpriced", "baseline.lines[0].rate_id"),
            (("rates", 0, "source_id"), "missing-evidence", "rates[0].source_id"),
        ):
            self.assert_missing_text_equivalent(path, code, field)

    def test_missing_metadata_normalization_does_not_hide_known_mismatches_or_unknown_enums(self):
        cases = [
            (("profile", "outcome", "unit"), "run", "unit"),
            (("baseline", "lines", 0, "quantity_unit"), "hour", "unit"),
            (("rates", 0, "unit"), "hour", "unit"),
            (("baseline", "scenarios", 0, "driver_evidence", "tokens_per_run", "unit"), "call", "unit"),
            (("baseline", "lines", 0, "service"), "another-service", "service"),
            (("baseline", "lines", 0, "meter"), "another-meter", "meter"),
            (("rates", 0, "service"), "another-service", "service"),
            (("rates", 0, "meter"), "another-meter", "meter"),
            (("profile", "outcome", "unit"), "unknown-unit", "unit"),
            (("baseline", "lines", 0, "quantity_unit"), "unknown-unit", "unit"),
            (("rates", 0, "unit"), "unknown-unit", "unit"),
            (("rates", 0, "currency"), "GBP", "currency"),
            (("baseline", "agent_id"), "UNKNOWN-AGENT", "agent_id"),
            (("baseline", "lines", 0, "rate_id"), "UNKNOWN-RATE", "rate_id"),
            (("baseline", "lines", 0, "driver_id"), "UNKNOWN-DRIVER", "driver_id"),
        ]
        for path, value, field in cases:
            model = example()
            put(model, path, value)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, field):
                self.gaps(model)
        # A missing counterpart must not suppress validation of a nonblank enum.
        for path, counterpart in (
            (("rates", 0, "unit"), ("baseline", "lines", 0, "quantity_unit")),
            (("baseline", "lines", 0, "quantity_unit"), ("rates", 0, "unit")),
        ):
            model = example()
            put(model, path, "unknown-unit")
            put(model, counterpart, "   ")
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unit"):
                self.gaps(model)

    def test_absent_fx_declaration_is_not_an_implicit_conversion_policy(self):
        self.model["fx"] = None
        gaps = [g for g in self.gaps() if g["code"] == "missing-fx"]
        self.assertTrue(gaps)
        # The fixture needs no conversion, so its arithmetic inputs remain known.
        self.assertFalse(any("calculation" in g["blocks"] for g in gaps))

    def test_source_freshness_future_timestamps_and_missing_evidence_are_diagnostic(self):
        for value, code in (("2026-01-01", "stale-source"), ("2026-11-13", "future-evidence"),
                            (None, "missing-evidence")):
            model = example()
            model["sources"][0]["lastValidatedAt"] = value
            self.assertIn(code, {g["code"] for g in self.gaps(model)})
        self.model["sources"][0]["lastValidatedAt"] = "2026-11-12T10:00:00+00:00"
        self.gaps()
        self.model["sources"][0]["lastValidatedAt"] = "2026-11-12T10:00:00"
        with self.assertRaisesRegex(ValueError, "lastValidatedAt"):
            self.gaps()

    def test_rate_effectivity_verification_and_freshness_are_separate(self):
        for patch, code in (({"effective_from": "2026-01-01", "effective_to": "2026-11-11"}, "inactive-rate"),
                            ({"freshness_policy": None}, "missing-freshness-policy"),
                            ({"verification": {"status": "unverified", "verified_at": None}}, "unverified-rate")):
            model = example()
            model["rates"][0].update(patch)
            self.assertIn(code, {g["code"] for g in self.gaps(model)})
        self.model["rates"][0]["verification"]["verified_at"] = "2026-01-01"
        self.assertIn("stale-rate", {g["code"] for g in self.gaps()})

    def test_public_concept_source_never_verifies_a_price(self):
        reference = json.loads((FIN / "references" / "baseline-sources.json").read_text(encoding="utf-8"))["sources"][0]
        self.model["sources"].append(reference)
        self.model["rates"][0]["source_id"] = reference["id"]
        self.model["rates"][0]["verification"] = {"status": "verified", "verified_at": "2026-11-12"}
        self.assertIn("source-applicability", {g["code"] for g in self.gaps()})

    def test_synthetic_evidence_cannot_be_promoted_by_a_verified_flag(self):
        self.model["mode"] = "planning"
        for rate in self.model["rates"]:
            rate["verification"]["status"] = "verified"
        for source in self.model["sources"]:
            source["validationStatus"] = "validated"
        gaps = self.gaps()
        self.assertIn("synthetic-evidence", {g["code"] for g in gaps})
        self.assertTrue(any("handover" in g["blocks"] for g in gaps))

    def test_cross_currency_requires_explicit_positive_evidenced_fx(self):
        self.model["rates"][0]["currency"] = "USD"
        self.assertIn("missing-fx", {g["code"] for g in self.gaps()})
        fx = {
            "id": "FX-USD-CHF", "version": 1, "from_currency": "USD", "to_currency": "CHF",
            "rate": "0.9", "date": "2026-11-12", "method": "synthetic",
            "source_id": "SYN-ENGINEERING", "verification": {"status": "synthetic", "verified_at": "2026-11-12"},
            "freshness_policy": {"max_age_days": 30}, "sharingClassification": "customer-shareable",
        }
        self.model["fx"] = [fx]
        self.assertNotIn("missing-fx", {g["code"] for g in self.gaps()})
        for key, value in (("rate", "0"), ("rate", "-1"), ("rate", True),
                           ("method", "list-price-ratio"), ("to_currency", "GBP")):
            model = copy.deepcopy(self.model)
            model["fx"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaisesRegex(ValueError, key):
                self.gaps(model)
        self.model["fx"].append({**fx, "id": "FX-AMBIGUOUS"})
        with self.assertRaisesRegex(ValueError, "fx"):
            self.gaps()

    def test_allocation_requires_an_evidenced_policy_and_valid_share(self):
        line = self.model["baseline"]["lines"][0]
        line["allocation_policy"] = {
            "id": "ALLOC-01", "method": "declared fixed share", "share": "0.25",
            "source_id": "SYN-ENGINEERING", "sharingClassification": "customer-shareable",
        }
        self.gaps()
        line["allocation_policy"]["share"] = "1.1"
        with self.assertRaisesRegex(ValueError, "share"):
            self.gaps()

    def test_unknown_sharing_stays_validation_required_and_legacy_lineage_is_material(self):
        source = self.model["sources"][0]
        source.update(sharingClassification="unknown", internal=True, visibility="internal",
                      src=["SYN-ENGINEERING"], content_src=["SYN-ENGINEERING"])
        original = copy.deepcopy(self.model)
        self.assertIn("sharing-validation", {g["code"] for g in self.gaps()})
        self.assertEqual(self.model, original)
        self.assertEqual(self.module.material_payload(self.model)["sources"][0], source)
        changed = copy.deepcopy(self.model)
        changed["sources"][0]["internal"] = False
        self.assertNotEqual(self.module.model_fingerprint(self.model), self.module.model_fingerprint(changed))

    def test_source_locations_and_lineage_are_validated_without_retrieval(self):
        self.model["sources"][0].update(url=None, evidence_ref=None)
        self.assertIn("missing-evidence", {g["code"] for g in self.gaps()})
        self.model = example()
        self.model["rates"][0]["content_src"] = ["UNRESOLVED"]
        with self.assertRaisesRegex(ValueError, "content_src"):
            self.gaps()

    def test_explicit_null_source_applicability_remains_an_evidence_gap(self):
        self.model["sources"][0]["applicability"] = None
        self.assertIn("missing-evidence", {g["code"] for g in self.gaps()})

    def test_source_applicability_entry_null_has_an_explicit_indexed_gap(self):
        self.model["sources"][0]["applicability"].insert(1, None)
        original = copy.deepcopy(self.model)
        gaps = [g for g in self.gaps() if g["code"] == "source-applicability"
                and g["field"] == "sources[0].applicability[1]"]
        self.assertTrue(gaps)
        self.assertTrue(all(g["blocks"] == ["handover"] for g in gaps))
        self.assertEqual(self.model, original)

    def test_source_applicability_entry_blank_has_an_explicit_indexed_gap(self):
        for value in ("", " \t "):
            model = example()
            model["sources"][0]["applicability"].append(value)
            original = copy.deepcopy(model)
            with self.subTest(value=value):
                gaps = [g for g in self.gaps(model) if g["code"] == "source-applicability"
                        and g["field"] == "sources[0].applicability[4]"]
                self.assertTrue(gaps)
                self.assertTrue(all(g["blocks"] == ["handover"] for g in gaps))
                self.assertEqual(model, original)

    def test_explicit_null_driver_evidence_remains_a_gap(self):
        self.model["baseline"]["scenarios"][0]["driver_evidence"]["tokens_per_run"] = None
        self.assertIn("missing-evidence", {g["code"] for g in self.gaps()})

    def test_missing_quantities_for_all_declared_scenarios_are_not_unknown_driver_ids(self):
        for scenario in self.model["baseline"]["scenarios"]:
            del scenario["drivers"]["tokens_per_run"]
        gaps = self.gaps()
        self.assertEqual(len([g for g in gaps if g["code"] == "missing-quantity"
                             and g["field"].endswith(".drivers.tokens_per_run")]), 3)

    def test_nested_sharing_metadata_requires_validation_even_inside_authored_notes(self):
        self.model["baseline"]["assumptions"][0]["supporting_note"] = {
            "sharingClassification": "unknown", "internal": True,
            "content_src": ["SYN-ENGINEERING"],
        }
        self.assertTrue(any(g["code"] == "sharing-validation" and "supporting_note" in g["field"]
                            and "customer-export" in g["blocks"] for g in self.gaps()))

    def test_unknown_blueprint_schema_is_not_accepted_as_agent_evidence(self):
        blueprint = {"schema": "frontier-blueprint/9.0", "domains": [
            {"agents": [{"id": "D3-A05"}]}
        ]}
        with self.assertRaisesRegex(ValueError, "blueprint.schema"):
            self.gaps(blueprint=blueprint)

    def test_errors_do_not_echo_supplied_prices_or_source_text(self):
        self.model["rates"][0]["amount"] = "PRIVATE-PRICE-DO-NOT-LOG"
        with self.assertRaisesRegex(ValueError, "amount") as caught:
            self.gaps()
        self.assertNotIn("PRIVATE-PRICE", str(caught.exception))
        self.model = example()
        self.model["sources"][0]["title"] = {"PRIVATE-SOURCE-TEXT": "private"}
        with self.assertRaisesRegex(ValueError, "title") as caught:
            self.gaps()
        self.assertNotIn("PRIVATE-SOURCE", str(caught.exception))

    def test_nested_authored_fields_remain_in_the_fingerprint(self):
        changed = copy.deepcopy(self.model)
        changed["baseline"]["assumptions"][0]["maturity"] = "changed"
        self.assertNotEqual(self.module.model_fingerprint(self.model), self.module.model_fingerprint(changed))

    def test_fingerprint_omits_only_owned_root_outputs_and_returns_detached_material(self):
        hashed = self.module.model_fingerprint(self.model)
        for key in ("results", "finops_preview", "review_records", "handover"):
            self.model[key] = {"output": "ignored"}
        self.assertEqual(hashed, self.module.model_fingerprint(self.model))
        self.model["baseline"]["assumptions"][0]["results"] = "authored"
        self.assertNotEqual(hashed, self.module.model_fingerprint(self.model))
        payload = self.module.material_payload(self.model)
        self.assertEqual(set(self.model) - set(payload), {"results", "finops_preview", "review_records", "handover"})
        payload["baseline"]["assumptions"][0]["maturity"] = "detached"
        self.assertNotEqual(payload["baseline"], self.model["baseline"])
        self.assertEqual(self.module.model_fingerprint(self.model), baseline_module("finops_preview").fingerprint(
            self.module.material_payload(self.model)))

    def test_every_authored_input_class_changes_the_fingerprint(self):
        for path, value in ((("rates", 0, "amount"), "1.1"),
                            (("sources", 0, "sharingClassification"), "internal-only"),
                            (("profile", "customer_scope"), "another-scope"),
                            (("baseline", "scenarios", 0, "drivers", "tokens_per_run"), "501"),
                            (("rates", 0, "freshness_policy", "max_age_days"), 31)):
            changed = copy.deepcopy(self.model)
            put(changed, path, value)
            with self.subTest(path=path):
                self.assertNotEqual(self.module.model_fingerprint(self.model), self.module.model_fingerprint(changed))

    def test_public_reference_metadata_is_concepts_only_and_not_a_price_sheet(self):
        data = json.loads((FIN / "references" / "baseline-sources.json").read_text(encoding="utf-8"))
        self.assertEqual({s["id"] for s in data["sources"]}, {"PUB-UE", "PUB-PRICE", "PUB-FOCUS-MS", "PUB-FOCUS"})
        for source in data["sources"]:
            self.assertEqual(source["lastValidatedAt"], "2026-11-12")
            self.assertEqual(source["type"], "public-reference")
            self.assertEqual(source["applicability"], ["concept"])
            self.assertEqual(source["sharingClassification"], "customer-shareable")
            self.assertTrue(source["supported_claim"])
            self.assertTrue(source["limitations"])
            self.assertNotIn("amount", source)


class BaselineCalculationTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((FIN / "scripts" / "baseline_calc.py").is_file(),
                        "Task2 calculate/validate_receipt have not been implemented")
        self.calc = baseline_module("baseline_calc")
        self.assertTrue(callable(getattr(self.calc, "calculate", None)), "Task2 calculate API is absent")
        self.assertTrue(callable(getattr(self.calc, "validate_receipt", None)), "Task2 receipt API is absent")
        self.model = example()

    def calculate(self, model=None, **kwargs):
        return self.calc.calculate(self.model if model is None else model, as_of=DAY,
                                   acknowledge_finops_preview=True, **kwargs)

    def expected(self, model=None):
        return self.calculate(model)["results"]["scenarios"]["expected"]

    def verified_test_data(self):
        """Simulated unit-test evidence only; never real commercial approval."""
        self.model["mode"] = "planning"
        for source in self.model["sources"]:
            source.update(type="internal-evidence", validationStatus="validated",
                          evidence_ref="testdata:not-real-commercial-verification")
        for rate in self.model["rates"]:
            rate["verification"]["status"] = "verified"

    def add_fx(self, *, status="synthetic", amount="0.9"):
        self.model["rates"][0]["currency"] = "USD"
        self.model["fx"] = [{
            "id": "FX-TEST", "version": 1, "from_currency": "USD", "to_currency": "CHF",
            "rate": amount, "date": "2026-11-12", "method": "spot", "source_id": "SYN-ENGINEERING",
            "verification": {"status": status, "verified_at": "2026-11-12"},
            "freshness_policy": {"max_age_days": 30}, "sharingClassification": "customer-shareable",
        }]

    def assert_driver_coverage(self, result, priced, scope, status):
        coverage = result.get("driver_coverage")
        self.assertIsInstance(coverage, dict, "Calculated results must expose evidenced driver coverage")
        self.assertEqual(coverage.get("priced_driver_count"), priced)
        self.assertEqual(coverage.get("in_scope_driver_count"), scope)
        self.assertIs(type(coverage["priced_driver_count"]), int)
        self.assertIs(type(coverage["in_scope_driver_count"]), int)
        self.assertEqual(coverage.get("status"), status)
        self.assertEqual(coverage.get("reason"),
                         None if status == "complete" else
                         "empty-scope" if status == "unavailable" else "incomplete-evidenced-pricing")
        return coverage

    def test_driver_coverage_complete_and_unpriced_keep_integer_scope_counts(self):
        self.verified_test_data()
        complete = self.calculate()
        self.assert_driver_coverage(complete["results"], 3, 3, "complete")
        self.model["rates"][0]["amount"] = None
        partial = self.calculate()
        self.assert_driver_coverage(partial["results"], 2, 3, "incomplete")
        month = partial["results"]["scenarios"]["expected"]["months"][0]
        self.assertEqual(month["known_priced_subtotal"]["amount"], "10.00")
        self.assertIsNone(month["total"]["amount"])

    def test_driver_coverage_requires_every_scenario_period_and_evidenced_price(self):
        cases = [
            (("rates", 0, "verification", "status"), "unverified"),
            (("rates", 0, "verification", "verified_at"), "2026-01-01"),
            (("rates", 0, "source_id"), None),
            (("rates", 0, "effective_to"), "2026-12-31"),
            (("baseline", "scenarios", 2, "drivers", "tokens_per_run"), None),
            (("baseline", "scenarios", 2, "monthly_runs", 11), None),
            (("baseline", "scenarios", 2, "driver_evidence", "tokens_per_run", "source_id"), None),
        ]
        for path, value in cases:
            self.model = example()
            self.verified_test_data()
            put(self.model, path, value)
            with self.subTest(path=path):
                result = self.calculate()["results"]
                self.assert_driver_coverage(result, 2, 3, "incomplete")
                if path[-1] in {"status", "verified_at", "source_id"} and path[0] == "rates":
                    month = result["scenarios"]["expected"]["months"][0]
                    self.assertEqual(month["total"]["amount"], "110.00")
                    self.assertEqual(month["total"]["status"], "provisional")
        for status in ("verified", "unverified", None):
            self.model = example()
            self.verified_test_data()
            self.add_fx(status=status or "verified")
            if status is None:
                self.model["fx"] = []
            with self.subTest(fx=status):
                self.assert_driver_coverage(self.calculate()["results"], 3 if status == "verified" else 2,
                                            3, "complete" if status == "verified" else "incomplete")

    def test_driver_coverage_multiline_and_unrepresented_drivers_cannot_disappear(self):
        self.verified_test_data()
        base = copy.deepcopy(self.model)
        extra_rate = {**copy.deepcopy(self.model["rates"][0]), "id": "TEST-SECOND-RATE", "amount": None}
        self.model["rates"].append(extra_rate)
        self.model["baseline"]["lines"].append({
            **copy.deepcopy(self.model["baseline"]["lines"][0]),
            "id": "TEST-SECOND-LINE", "rate_id": extra_rate["id"],
        })
        self.assert_driver_coverage(self.calculate()["results"], 2, 3, "incomplete")
        self.model = copy.deepcopy(base)
        self.model["baseline"]["lines"].pop(0)
        self.assert_driver_coverage(self.calculate()["results"], 2, 3, "incomplete")
        self.model = base
        self.model["baseline"]["scope"].append({
            "cost_driver_id": "TEST-UNREPRESENTED", "description": "Unrepresented declared scope",
            "sharingClassification": "customer-shareable",
        })
        self.assert_driver_coverage(self.calculate()["results"], 3, 4, "incomplete")

    def test_driver_coverage_empty_unpriced_and_recurring_only_scopes(self):
        self.verified_test_data()
        base = copy.deepcopy(self.model)
        for rate in self.model["rates"]:
            rate["amount"] = None
        self.assert_driver_coverage(self.calculate()["results"], 0, 3, "incomplete")
        self.model = copy.deepcopy(base)
        self.model["baseline"]["scope"] = []
        self.model["baseline"]["lines"] = []
        self.assert_driver_coverage(self.calculate()["results"], 0, 0, "unavailable")
        self.model = copy.deepcopy(base)
        self.model["baseline"]["scenarios"] = []
        self.model["baseline"]["lines"] = []
        self.assert_driver_coverage(self.calculate()["results"], 0, 3, "incomplete")
        self.model = base
        build_driver = self.model["baseline"]["lines"][-1]["cost_driver_id"]
        self.model["baseline"]["lines"] = [line for line in self.model["baseline"]["lines"]
                                           if line["frequency"] == "monthly"]
        self.model["baseline"]["scope"] = [row for row in self.model["baseline"]["scope"]
                                           if row["cost_driver_id"] != build_driver]
        self.model["baseline"]["exclusions"][0]["description"] = (
            "Test-only reviewed exclusion: no one-time build costs are in this scope.")
        self.assert_driver_coverage(self.calculate()["results"], 2, 2, "complete")

    def test_driver_coverage_is_recomputed_and_receipt_bound_not_cached_authority(self):
        self.verified_test_data()
        before = copy.deepcopy(self.model)
        document = self.calculate()
        self.assert_driver_coverage(document["results"], 3, 3, "complete")
        self.assertEqual(self.model, before)
        for remove in (False, True):
            bad = copy.deepcopy(document)
            if remove:
                bad["results"].pop("driver_coverage")
            else:
                bad["results"]["driver_coverage"]["priced_driver_count"] = 2
            bad["finops_preview"]["calculations"]["baseline"]["results_fingerprint"] = (
                baseline_module("finops_preview").fingerprint(bad["results"]))
            with self.subTest(remove=remove), self.assertRaisesRegex(ValueError, "recalculate"):
                self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)
            fresh = self.calculate(bad)
            self.assertEqual(fresh["results"], document["results"])
            self.assertEqual(baseline_module().model_fingerprint(bad), baseline_module().model_fingerprint(before))

    def test_known_answers_and_period_bases(self):
        result = self.calculate()["results"]
        expected = result["scenarios"]["expected"]
        self.assertEqual(expected["months"][0]["total"]["amount"], "110.00")
        self.assertEqual(expected["annual_recurring"]["amount"], "1320.00")
        self.assertEqual(expected["one_time"]["amount"], "200.00")
        self.assertEqual(expected["first_year"]["amount"], "1520.00")
        self.assertEqual(expected["months"][0]["per_success"]["amount"], "2.200000")
        self.assertEqual(expected["months"][0]["per_run"]["basis"], "recurring")
        self.assertEqual(expected["unit_metrics"]["first_year"]["per_run"]["basis"], "first-year")
        self.assertEqual(expected["unit_metrics"]["first_year"]["per_run"]["amount"], "1.266667")
        self.assertEqual(expected["unit_metrics"]["annual_recurring"]["per_success"]["amount"], "2.200000")
        for key, monthly, yearly in (("low", "35.00", "620.00"), ("high", "410.00", "5120.00")):
            self.assertEqual(result["scenarios"][key]["months"][0]["total"]["amount"], monthly)
            self.assertEqual(result["scenarios"][key]["first_year"]["amount"], yearly)
        self.assertEqual(len(expected["months"]), 12)
        self.assertEqual(expected["months"][0]["period"], "2026-12")
        self.assertEqual(expected["months"][-1]["period"], "2027-11")
        self.assertEqual(expected["months"][0]["total"]["status"], "provisional")
        self.assertEqual(expected["months"][0]["total"]["reason"], "pricing-evidence-incomplete")
        self.assertTrue(result["internal"])
        self.assertEqual(result["forecast_kind"], "estimate")
        self.assertTrue(result["handover_blocked"])
        self.assertIn("synthetic-evidence", {g["code"] for g in result["gaps"]})
        json.dumps(result, allow_nan=False)

    def test_missing_rate_keeps_known_subtotal_not_full_unit_cost(self):
        self.model["rates"][0]["amount"] = None
        document = self.calculate()
        month = document["results"]["scenarios"]["expected"]["months"][0]
        self.assertIsNone(month["total"]["amount"])
        self.assertEqual(month["total"]["status"], "incomplete")
        self.assertEqual(month["known_priced_subtotal"]["amount"], "10.00")
        self.assertIsNone(month["verified_subtotal"]["amount"])
        self.assertIsNone(month["per_run"]["amount"])
        self.assertEqual(month["per_run"]["reason"], "incomplete-cost")
        self.assertIn("unpriced", {g["code"] for g in document["results"]["gaps"]})

    def test_current_actual_true_ack_is_required_before_any_work(self):
        result = self.calculate()
        for operation, model in ((self.calc.calculate, self.model), (self.calc.validate_receipt, result)):
            before = copy.deepcopy(model)
            for value in (False, None, 1, "true", {}, result["finops_preview"]):
                with self.subTest(operation=operation.__name__, value=type(value).__name__):
                    with self.assertRaisesRegex(ValueError, "Explicit"):
                        operation(model, as_of=DAY, acknowledge_finops_preview=value)
            with self.assertRaisesRegex(ValueError, "Explicit"):
                operation(object(), as_of=None)
            self.assertEqual(model, before)

    def test_receipt_recomputes_and_rejects_rehashed_fabricated_amount(self):
        document = self.calculate()
        receipt = self.calc.validate_receipt(document, as_of=DAY, acknowledge_finops_preview=True)
        self.assertEqual(receipt["kind"], "baseline")
        self.assertEqual(receipt["scenario_ids"], ["expected", "high", "low"])
        self.assertEqual(receipt["as_of"], DAY.isoformat())
        self.assertEqual(receipt["model_fingerprint"], baseline_module().model_fingerprint(self.model))
        bad = copy.deepcopy(document)
        bad["results"]["scenarios"]["expected"]["months"][0]["total"]["amount"] = "999999.00"
        bad["finops_preview"]["calculations"]["baseline"]["results_fingerprint"] = (
            baseline_module("finops_preview").fingerprint(bad["results"]))
        with self.assertRaisesRegex(ValueError, "recalculate"):
            self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)
        receipt["kind"] = "mutated-return"
        self.assertEqual(document["finops_preview"]["calculations"]["baseline"]["kind"], "baseline")

    def test_authored_monthly_variation_sums_twelve_not_first_times_twelve(self):
        self.model["baseline"]["annualisation"]["demand_profile"] = "authored-monthly"
        self.model["baseline"]["scenarios"][1]["monthly_runs"] = [str(n) for n in range(1, 13)]
        result = self.expected()
        self.assertEqual(result["months"][0]["total"]["amount"], "11.00")
        self.assertEqual(result["months"][-1]["total"]["amount"], "22.00")
        self.assertEqual(result["annual_recurring"]["amount"], "198.00")
        self.assertEqual(result["first_year"]["amount"], "398.00")
        self.assertEqual(result["unit_metrics"]["annual_recurring"]["per_run"]["denominator"], "78")

    def test_pricing_block_explicit_fx_and_raw_precision(self):
        self.add_fx(amount="0.9")
        self.model["rates"][0].update(amount="1.23456789", pricing_block="100")
        result = self.expected()
        self.assertEqual(result["months"][0]["total"]["amount"], "1121.11")
        self.assertEqual(result["annual_recurring"]["amount"], "13453.33")
        self.assertEqual(self.model["rates"][0]["amount"], "1.23456789")
        self.assertIn("FX-TEST", result["months"][0]["lines"][0]["cost"]["fx_refs"])

    def test_rounding_is_half_up_on_final_period_not_each_component(self):
        self.model["rates"][0]["amount"] = "0.00005"  # expected tokens cost .005
        self.model["rates"][1]["amount"] = "0.005"
        result = self.expected()
        self.assertEqual(result["months"][0]["total"]["amount"], "0.01")
        self.assertEqual(result["months"][0]["lines"][0]["cost"]["amount"], "0.01")
        self.assertEqual(result["annual_recurring"]["amount"], "0.12")

    def test_fixed_and_per_run_one_time_and_explicit_allocation(self):
        line = self.model["baseline"]["lines"][2]
        line.update(quantity_mode="per-run", shared=True, allocation_policy={
            "id": "ALLOC-TEST", "method": "explicit test share", "share": "0.25",
            "source_id": "SYN-ENGINEERING", "sharingClassification": "customer-shareable",
        })
        result = self.expected()
        self.assertEqual(result["one_time"]["amount"], "5000.00")
        self.assertEqual(result["first_year"]["amount"], "6320.00")
        self.assertEqual(len(result["one_time_lines"]), 1)
        del line["allocation_policy"]
        result = self.expected()
        self.assertIsNone(result["one_time"]["amount"])
        self.assertEqual(result["annual_recurring"]["amount"], "1320.00")
        self.assertIsNone(result["first_year"]["amount"])

    def test_zero_rate_and_numerator_are_real_zero(self):
        for rate in self.model["rates"]:
            rate["amount"] = "0"
        result = self.expected()
        self.assertEqual(result["annual_recurring"]["amount"], "0.00")
        self.assertEqual(result["months"][0]["per_run"]["amount"], "0.000000")
        self.assertEqual(result["months"][0]["per_outcome"]["amount"], "0.000000")

    def test_missing_and_zero_denominators_are_independent(self):
        scenario = self.model["baseline"]["scenarios"][1]
        for key in ("success_share", "outcomes_per_success"):
            for value in (None, "0"):
                scenario["success_share"] = "0.5"
                scenario["outcomes_per_success"] = "2"
                scenario[key] = value
                with self.subTest(key=key, value=value):
                    month = self.expected()["months"][0]
                    self.assertEqual(month["total"]["amount"], "110.00")
                    self.assertEqual(month["per_run"]["amount"], "1.100000")
                    if key == "outcomes_per_success":
                        self.assertEqual(month["per_success"]["amount"], "2.200000")
                    else:
                        self.assertIsNone(month["per_success"]["amount"])
                    self.assertIsNone(month["per_outcome"]["amount"])
                    self.assertEqual(month["per_outcome"]["reason"], "no-denominator")

    def test_zero_runs_do_not_invent_denominators_or_erase_fixed_cost(self):
        self.model["baseline"]["scenarios"][1]["monthly_runs"] = ["0"] * 12
        month = self.expected()["months"][0]
        self.assertEqual(month["total"]["amount"], "10.00")
        for metric in ("per_run", "per_success", "per_outcome"):
            self.assertIsNone(month[metric]["amount"])
            self.assertEqual(month[metric]["reason"], "no-denominator")

    def test_missing_outcome_metadata_leaves_independent_cost_and_run_metrics(self):
        for path in (("profile", "outcome", "unit"), ("profile", "outcome", "definition"),
                     ("baseline", "scenarios", 1, "driver_evidence", "outcomes_per_success", "unit")):
            for value in (None, "", "   "):
                model = example()
                put(model, path, value)
                with self.subTest(path=path, value=value):
                    month = self.expected(model)["months"][0]
                    self.assertEqual(month["total"]["amount"], "110.00")
                    self.assertEqual(month["per_run"]["amount"], "1.100000")
                    self.assertEqual(month["per_success"]["amount"], "2.200000")
                    self.assertIsNone(month["per_outcome"]["amount"])

    def test_missing_runs_only_affect_the_authored_period_and_dependent_line(self):
        self.model["baseline"]["scenarios"][1]["monthly_runs"][3] = None
        result = self.expected()
        self.assertEqual(result["months"][0]["total"]["amount"], "110.00")
        month = result["months"][3]
        self.assertIsNone(month["total"]["amount"])
        self.assertIsNone(month["lines"][0]["quantity"])
        self.assertEqual(month["known_priced_subtotal"]["amount"], "10.00")
        self.assertIsNone(result["annual_recurring"]["amount"])
        self.assertEqual(result["one_time"]["amount"], "200.00")

    def test_missing_driver_or_unit_never_defaults_to_zero(self):
        for path in (("baseline", "scenarios", 1, "drivers", "tokens_per_run"),
                     ("baseline", "scenarios", 1, "driver_evidence", "tokens_per_run", "unit"),
                     ("rates", 0, "unit"), ("rates", 0, "currency"), ("rates", 0, "pricing_block"),
                     ("baseline", "lines", 0, "quantity_unit")):
            model = example()
            put(model, path, None)
            with self.subTest(path=path):
                month = self.expected(model)["months"][0]
                self.assertIsNone(month["total"]["amount"])
                self.assertEqual(month["known_priced_subtotal"]["amount"], "10.00")

    def test_missing_fx_never_uses_inverse_or_ratio(self):
        self.model["rates"][0]["currency"] = "USD"
        month = self.expected()["months"][0]
        self.assertIsNone(month["total"]["amount"])
        self.assertEqual(month["known_priced_subtotal"]["amount"], "10.00")
        self.add_fx()
        self.model["fx"][0].update(from_currency="CHF", to_currency="USD")
        self.assertIsNone(self.expected()["months"][0]["total"]["amount"])

    def test_all_unpriced_and_empty_groups_are_null_not_zero(self):
        for rate in self.model["rates"]:
            rate["amount"] = None
        result = self.expected()
        for key in ("total", "known_priced_subtotal", "verified_subtotal", "provisional_subtotal"):
            self.assertIsNone(result["months"][0][key]["amount"])
        self.assertIsNone(result["first_year"]["amount"])
        self.model["baseline"]["lines"] = []
        result = self.expected()
        self.assertIsNone(result["annual_recurring"]["amount"])
        self.assertIsNone(result["one_time"]["amount"])

    def test_uncovered_scope_does_not_label_partial_cost_as_full(self):
        self.model["baseline"]["scope"].append({
            "cost_driver_id": "test-missing", "description": "Unrepresented test scope",
            "sharingClassification": "customer-shareable"})
        result = self.expected()
        self.assertIsNone(result["months"][0]["total"]["amount"])
        self.assertEqual(result["months"][0]["known_priced_subtotal"]["amount"], "110.00")
        self.assertIsNone(result["months"][0]["per_run"]["amount"])

    def test_stale_unverified_rates_keep_provisional_figures_and_dated_gaps(self):
        self.verified_test_data()
        for status, day in (("unverified", "2026-11-12"), ("verified", "2026-01-01")):
            self.model["rates"][0]["verification"].update(status=status, verified_at=day)
            result = self.calculate()["results"]
            month = result["scenarios"]["expected"]["months"][0]
            self.assertEqual(month["total"]["amount"], "110.00")
            self.assertEqual(month["total"]["status"], "provisional")
            self.assertEqual(month["per_run"]["status"], "provisional")
            self.assertTrue(result["handover_blocked"])
            evidence = month["lines"][0]["pricing_evidence"]
            self.assertEqual(evidence["as_of"], DAY.isoformat())
            self.assertTrue(evidence["gaps"])
            self.assertEqual(evidence["records"][0]["verified_at"], day)

    def test_mixed_verified_provisional_contributions_never_silently_mix(self):
        self.verified_test_data()
        self.model["rates"][0]["verification"]["status"] = "unverified"
        result = self.expected()
        month = result["months"][0]
        self.assertEqual(month["verified_subtotal"]["amount"], "10.00")
        self.assertEqual(month["provisional_subtotal"]["amount"], "100.00")
        self.assertEqual(month["known_priced_subtotal"]["amount"], "110.00")
        self.assertEqual(month["known_priced_subtotal"]["status"], "provisional")
        self.assertEqual(month["total"]["status"], "provisional")
        self.assertEqual(result["annual_recurring"]["verified_subtotal"]["amount"], "120.00")
        self.assertEqual(result["annual_recurring"]["provisional_subtotal"]["amount"], "1200.00")

    def test_provisional_fx_and_synthetic_sources_cannot_be_promoted(self):
        self.verified_test_data()
        self.add_fx(status="unverified")
        month = self.expected()["months"][0]
        self.assertEqual(month["total"]["amount"], "100.00")
        self.assertEqual(month["total"]["status"], "provisional")
        self.assertEqual(month["provisional_subtotal"]["amount"], "90.00")
        self.model = example()
        for rate in self.model["rates"]:
            rate["verification"]["status"] = "verified"
        self.assertEqual(self.expected()["months"][0]["total"]["status"], "provisional")

    def test_simulated_verified_price_is_not_financial_approval(self):
        self.verified_test_data()
        document = self.calculate()
        month = document["results"]["scenarios"]["expected"]["months"][0]
        self.assertEqual(month["total"]["status"], "available")
        self.assertEqual(month["verified_subtotal"]["amount"], "110.00")
        self.assertIsNone(month["provisional_subtotal"]["amount"])
        self.assertTrue(document["results"]["handover_blocked"])
        self.assertFalse(document["results"]["financial_approval"])

    def test_inapplicable_sources_and_periods_are_not_rescued_by_provisional_policy(self):
        for path, value in ((("sources", 0, "applicability"), ["concept"]),
                            (("sources", 0, "type"), "public-reference"),
                            (("rates", 0, "effective_to"), "2026-12-31")):
            model = example()
            put(model, path, value)
            with self.subTest(path=path):
                result = self.expected(model)
                if path[-1] == "effective_to":
                    self.assertEqual(result["months"][0]["total"]["amount"], "110.00")
                    self.assertIsNone(result["months"][1]["total"]["amount"])
                else:
                    self.assertIsNone(result["months"][0]["total"]["amount"])
                self.assertIsNone(result["annual_recurring"]["amount"])

    def test_inactive_at_as_of_and_ambiguous_fx_are_refused(self):
        self.model["rates"][0]["effective_from"] = "2026-12-01"
        self.assertIsNone(self.expected()["months"][0]["total"]["amount"])
        self.model = example()
        self.add_fx()
        other = copy.deepcopy(self.model["fx"][0])
        other["id"] = "FX-OTHER"
        self.model["fx"].append(other)
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            self.calculate()

    def test_metadata_only_gaps_do_not_erase_numbers(self):
        for path in (("profile", "name"), ("profile", "owners", "finance"),
                     ("baseline", "lines", 0, "category"),
                     ("rates", 0, "source_id"), ("rates", 0, "verification"),
                     ("sources", 0, "supported_claim")):
            model = example()
            put(model, path, None)
            with self.subTest(path=path):
                self.assertEqual(self.expected(model)["months"][0]["total"]["amount"], "110.00")

    def test_no_input_mutation_stale_outputs_replaced_and_calls_deterministic(self):
        self.model.update(results={"bad": "stale"}, finops_preview={"approved": True},
                          review_records=[{"approved": True}], handover={"approved": True})
        original = copy.deepcopy(self.model)
        first = self.calculate()
        self.assertEqual(self.model, original)
        self.assertEqual(first, self.calculate())
        self.assertNotIn("review_records", first)
        self.assertNotIn("handover", first)
        self.assertNotIn("approved", first["finops_preview"])
        self.assertFalse(first["results"]["financial_approval"])

    def test_receipt_input_date_nested_maturity_and_fp_binding(self):
        document = self.calculate()
        for path, value in ((("baseline", "assumptions", 0, "maturity"), "reviewed"),
                            (("rates", 0, "amount"), "9"),
                            (("sources", 0, "internal"), True),
                            (("baseline", "scenarios", 1, "drivers", "tokens_per_run"), "42"),
                            (("finops_preview", "calculations", "baseline", "model_fingerprint"), "forged")):
            bad = copy.deepcopy(document)
            put(bad, path, value)
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "recalculate"):
                self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)
        with self.assertRaisesRegex(ValueError, "recalculate"):
            self.calc.validate_receipt(document, as_of=date(2026, 11, 13), acknowledge_finops_preview=True)

    def test_malformed_receipts_results_scenario_coverage_and_nonfinite_amounts(self):
        document = self.calculate()
        cases = [(("finops_preview",), None), (("results",), []),
                 (("finops_preview", "calculations", "baseline"), []),
                 (("results", "scenarios", "expected"), None),
                 (("finops_preview", "calculations", "baseline", "scenario_ids"), ["expected"])]
        for value in ("NaN", "Infinity", True, 110.0, None, "999"):
            cases.append((("results", "scenarios", "expected", "months", 0, "total", "amount"), value))
        for path, value in cases:
            bad = copy.deepcopy(document)
            put(bad, path, value)
            with self.subTest(path=path, value=value), self.assertRaisesRegex(ValueError, "recalculate"):
                self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)
        bad = copy.deepcopy(document)
        del bad["results"]["scenarios"]["low"]
        with self.assertRaisesRegex(ValueError, "recalculate"):
            self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)

    def test_private_rate_source_fx_and_nested_policy_ancestry_stays_on_derived_values(self):
        self.add_fx()
        self.model["fx"][0].update(internal=True, visibility="internal")
        self.model["rates"][0]["sharingClassification"] = "internal-only"
        month = self.expected()["months"][0]
        tokens, operations = month["lines"][:2]
        self.assertTrue(tokens["cost"]["internal"])
        self.assertEqual(tokens["cost"]["sharingClassification"], "internal-only")
        self.assertNotIn("internal", operations["cost"])
        self.assertTrue(month["total"]["internal"])
        self.assertTrue(month["per_run"]["internal"])
        self.assertIn("/profile", tokens["cost"]["dependency_refs"])
        self.assertIn("/baseline/scenarios/1/driver_evidence/tokens_per_run",
                      tokens["cost"]["dependency_refs"])
        self.assertIn("SYN-ENGINEERING", tokens["cost"]["source_refs"])

    def test_consumed_legacy_sources_transitive_private_restrictions_and_unused_sources(self):
        source = copy.deepcopy(self.model["sources"][0])
        source.update(id="TEST-PRIVATE", internal=True, visibility="internal",
                      sharingClassification="internal-only", content_src=["SYN-CONTEXT"])
        self.model["sources"].append(source)
        month = self.expected()["months"][0]
        self.assertNotIn("TEST-PRIVATE", month["total"]["source_refs"])
        self.assertNotIn("internal", month["total"])
        self.model["rates"][0].update(src=["TEST-PRIVATE"], content_src=["SYN-ENGINEERING"])
        month = self.expected()["months"][0]
        self.assertTrue(month["lines"][0]["cost"]["internal"])
        self.assertIn("TEST-PRIVATE", month["lines"][0]["cost"]["source_refs"])
        self.assertIn("SYN-CONTEXT", month["lines"][0]["cost"]["source_refs"])
        self.assertNotIn("internal", month["lines"][1]["cost"])

    def test_private_outcome_does_not_taint_independent_costs_or_per_run(self):
        self.model["profile"]["outcome"]["internal"] = True
        month = self.expected()["months"][0]
        self.assertNotIn("internal", month["total"])
        self.assertNotIn("internal", month["per_run"])
        self.assertTrue(month["per_outcome"]["internal"])

    def test_arithmetic_representation_errors_are_field_safe_and_nondestructive(self):
        for value in ("1e999999999", "1e-999999999"):
            model = example()
            model["rates"][0]["amount"] = value
            before = copy.deepcopy(model)
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "arithmetic|representation") as caught:
                self.calculate(model)
            self.assertNotIn(value, str(caught.exception))
            self.assertEqual(model, before)

    def test_blank_source_metadata_never_becomes_a_derived_source_identity(self):
        for value in (None, "", "   "):
            self.model["rates"][0]["source_id"] = value
            month = self.expected()["months"][0]
            self.assertEqual(month["total"]["amount"], "110.00")
            self.assertNotIn("   ", month["total"]["source_refs"])

    def test_nested_line_and_scenario_restrictions_reach_actual_derived_costs(self):
        for path in (("baseline", "lines", 0), ("baseline", "scenarios", 1)):
            model = example()
            parent = model
            for key in path:
                parent = parent[key]
            parent["supporting_note"] = {"internal": True, "sharingClassification": "internal-only"}
            month = self.expected(model)["months"][0]
            with self.subTest(path=path):
                self.assertTrue(month["lines"][0]["cost"].get("internal"))
                self.assertTrue(month["total"].get("internal"))
                if path[1] == "lines":
                    self.assertNotIn("internal", month["lines"][1]["cost"])

    def test_all_four_sharing_classes_and_customer_scope_reach_dependencies(self):
        for sharing in ("customer-shareable", "customer-specific", "internal-only", "validation-required"):
            self.model["rates"][0].update(sharingClassification=sharing, customer_scope="test-scope")
            line = self.expected()["months"][0]["lines"][0]
            self.assertIn(sharing, line["cost"]["sharing_classes"])
            self.assertIn("test-scope", line["cost"]["customer_scopes"])
            self.assertEqual(line["cost"]["sharingClassification"], sharing)

    def test_missing_sharing_on_consumed_records_remains_validation_required(self):
        for path in (("rates", 0), ("baseline", "lines", 0),
                     ("baseline", "scenarios", 1, "driver_evidence", "tokens_per_run"),
                     ("profile",)):
            model = example()
            row = model
            for key in path:
                row = row[key]
            row["sharingClassification"] = None
            with self.subTest(path=path):
                month = self.expected(model)["months"][0]
                self.assertEqual(month["total"]["amount"], "110.00")
                self.assertEqual(month["lines"][0]["cost"]["sharingClassification"], "validation-required")

    def test_future_fx_evidence_is_not_a_stale_price_amendment(self):
        self.add_fx()
        self.model["fx"][0]["date"] = "2026-11-13"
        month = self.expected()["months"][0]
        self.assertIsNone(month["total"]["amount"])
        self.assertEqual(month["known_priced_subtotal"]["amount"], "10.00")

    def test_synthetic_consumed_quantity_is_labelled_even_with_verified_test_prices(self):
        self.verified_test_data()
        source = copy.deepcopy(example()["sources"][0])
        source["id"] = "TEST-SYNTHETIC-QUANTITY"
        self.model["sources"].append(source)
        self.model["baseline"]["scenarios"][1]["driver_evidence"]["tokens_per_run"]["source_id"] = source["id"]
        line = self.expected()["months"][0]["lines"][0]
        self.assertTrue(line["cost"].get("synthetic"))
        self.assertEqual(line["cost"]["status"], "provisional")

    def test_forged_hash_cannot_hide_missing_scenario_or_invalid_amount_type(self):
        document = self.calculate()
        for path, value in ((("results", "scenarios", "expected", "months", 0, "per_success", "amount"), 2.2),
                            (("results", "scenarios", "expected"), {}),
                            (("finops_preview", "acknowledgement", "scope"), "cached-approval")):
            bad = copy.deepcopy(document)
            put(bad, path, value)
            bad["finops_preview"]["calculations"]["baseline"]["results_fingerprint"] = (
                baseline_module("finops_preview").fingerprint(bad["results"]))
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "recalculate"):
                self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)

    def test_review_precision_boundary_never_returns_a_wrong_cent(self):
        self.model["rates"][2]["amount"] = "0.004" + "9" * 85
        before = copy.deepcopy(self.model)
        try:
            result = self.expected()
        except ValueError as error:
            self.assertIn("arithmetic representation", str(error))
            self.assertNotIn(self.model["rates"][2]["amount"], str(error))
        else:
            self.assertEqual(result["one_time"]["amount"], "0.00",
                             "Intermediate rounding must not cross the HALF_UP cent boundary")
        self.assertEqual(self.model, before)

    def test_review_precision_product_loss_is_explicit_even_when_inputs_fit(self):
        for scenario in self.model["baseline"]["scenarios"]:
            scenario["drivers"]["build_units"] = "1." + "1" * 50
        self.model["rates"][2]["amount"] = "0." + "1" * 50
        before = copy.deepcopy(self.model)
        with self.assertRaisesRegex(ValueError, "arithmetic representation"):
            self.calculate()
        self.assertEqual(self.model, before)

    def test_review_precision_sum_loss_is_explicit_even_when_inputs_fit(self):
        self.model["rates"][0]["amount"] = "1e-100"
        self.model["rates"][1]["amount"] = "0.004" + "9" * 77
        before = copy.deepcopy(self.model)
        with self.assertRaisesRegex(ValueError, "arithmetic representation"):
            self.calculate()
        self.assertEqual(self.model, before)

    def test_review_precision_nonterminating_line_division_is_explicit(self):
        self.model["rates"][0]["pricing_block"] = "3"
        with self.assertRaisesRegex(ValueError, "arithmetic representation"):
            self.calculate()

    def test_review_caller_decimal_context_cannot_change_results_or_receipt(self):
        expected = self.calculate()
        with localcontext() as caller:
            caller.prec, caller.rounding = 7, ROUND_FLOOR
            caller.Emin, caller.Emax, caller.clamp, caller.capitals = -9, 9, 1, 0
            for signal in caller.traps:
                caller.traps[signal] = True
            caller.flags[Inexact] = caller.flags[Rounded] = True
            state = (dict(caller.traps), dict(caller.flags), caller.prec, caller.rounding,
                     caller.Emin, caller.Emax, caller.clamp, caller.capitals)
            self.assertEqual(self.calculate(), expected)
            self.assertEqual(self.calc.validate_receipt(expected, as_of=DAY, acknowledge_finops_preview=True),
                             expected["finops_preview"]["calculations"]["baseline"])
            self.assertEqual((dict(caller.traps), dict(caller.flags), caller.prec, caller.rounding,
                              caller.Emin, caller.Emax, caller.clamp, caller.capitals), state)

    def test_review_nullable_blank_legacy_refs_are_parsed_before_derivation(self):
        private = copy.deepcopy(self.model["sources"][0])
        private.update(id="TEST-PRIVATE", internal=True, visibility="internal",
                       sharingClassification="internal-only", content_src=["SYN-CONTEXT"])
        self.model["sources"].append(private)
        for key in ("src", "content_src"):
            for value in (None, [], ["", "   ", None], ["", "TEST-PRIVATE", "   ", None]):
                model = copy.deepcopy(self.model)
                model["rates"][0][key] = value
                before = copy.deepcopy(model)
                gaps = baseline_module().validate_model(model, as_of=DAY)
                with self.subTest(key=key, value=value):
                    result = self.calculate(model)["results"]
                    month = result["scenarios"]["expected"]["months"][0]
                    self.assertEqual(month["total"]["amount"], "110.00")
                    line = month["lines"][0]["cost"]
                    for field in ("src", "content_src", "source_refs"):
                        self.assertTrue(all(isinstance(ref, str) and ref.strip() for ref in line.get(field, [])))
                    for gap in gaps:
                        self.assertIn(gap, result["gaps"])
                    if value and "TEST-PRIVATE" in value:
                        self.assertTrue(line["internal"])
                        self.assertIn("TEST-PRIVATE", line["source_refs"])
                        self.assertIn("SYN-CONTEXT", line["source_refs"])
                        self.assertNotIn("internal", month["lines"][1]["cost"])
                    else:
                        self.assertNotIn("internal", line)
                    self.assertEqual(model, before)

    def test_review_absent_rate_applicability_keeps_dated_provisional_figures(self):
        self.verified_test_data()
        for value in (None, [], [None], [""], ["   "], [None, "", "   "]):
            self.model["sources"][0]["applicability"] = value
            before = copy.deepcopy(self.model)
            with self.subTest(value=value):
                result = self.calculate()["results"]
                month = result["scenarios"]["expected"]["months"][0]
                self.assertEqual(month["total"]["amount"], "110.00")
                self.assertEqual(month["total"]["status"], "provisional")
                self.assertEqual(month["per_run"]["amount"], "1.100000")
                self.assertEqual(month["per_run"]["status"], "provisional")
                self.assertTrue(result["handover_blocked"])
                evidence = month["lines"][0]["pricing_evidence"]
                self.assertEqual(evidence["as_of"], DAY.isoformat())
                self.assertEqual(evidence["records"][0]["source_date"], "2026-11-12")
                self.assertEqual(evidence["records"][0]["source_id"], "SYN-ENGINEERING")
                self.assertIn("source-applicability", {g["code"] for g in evidence["gaps"]})
                self.assertTrue(any(g["field"].startswith("sources[0]") for g in evidence["gaps"]))
                self.assertEqual(self.model, before)

    def test_review_absent_fx_applicability_keeps_known_explicit_fx_only(self):
        self.verified_test_data()
        self.add_fx(status="verified")
        source = copy.deepcopy(self.model["sources"][0])
        source["id"] = "TEST-FX-SOURCE"
        self.model["sources"].append(source)
        self.model["fx"][0]["source_id"] = source["id"]
        for value in (None, [], [None, "", "   "]):
            source["applicability"] = value
            with self.subTest(value=value):
                month = self.expected()["months"][0]
                self.assertEqual(month["total"]["amount"], "100.00")
                self.assertEqual(month["provisional_subtotal"]["amount"], "90.00")
                self.assertEqual(month["verified_subtotal"]["amount"], "10.00")
                self.assertEqual(month["per_run"]["status"], "provisional")
                evidence = month["lines"][0]["pricing_evidence"]
                self.assertTrue(evidence["gaps"])
                self.assertEqual(evidence["records"][1]["source_date"], "2026-11-12")
        self.model["fx"][0]["rate"] = None
        self.assertIsNone(self.expected()["months"][0]["total"]["amount"])

    def test_review_explicit_incompatible_applicability_is_still_unavailable(self):
        for value in (["concept"], ["outcome"], [None, "", "concept"]):
            self.model["sources"][0]["applicability"] = value
            with self.subTest(value=value):
                month = self.expected()["months"][0]
                self.assertIsNone(month["total"]["amount"])
                self.assertIsNone(month["per_run"]["amount"])
        self.model = example()
        self.add_fx()
        self.model["sources"][0]["applicability"] = ["rate"]
        self.assertIsNone(self.expected()["months"][0]["total"]["amount"])

    def test_review_final_metric_rounding_allows_repeating_division_and_half_up(self):
        self.model["rates"][0]["amount"] = "0"
        self.model["baseline"]["scenarios"][1]["monthly_runs"] = ["3"] * 12
        for rate, expected in (("0.000001499999999999999999999999", "0.000000"),
                               ("0.0000015", "0.000001"), ("0.0000016", "0.000001")):
            self.model["rates"][1]["amount"] = rate
            with self.subTest(rate=rate):
                self.assertEqual(self.expected()["months"][0]["per_run"]["amount"], expected)

    def missing_fx_identity_models(self):
        self.verified_test_data()
        self.add_fx(status="verified")
        self.model["fx"][0].update(internal=True, visibility="internal", content_src=["SYN-CONTEXT"])
        for label, identity in (("absent", None), ("null", None), ("empty", ""), ("whitespace", "   ")):
            model = copy.deepcopy(self.model)
            if label == "absent":
                del model["fx"][0]["id"]
            else:
                model["fx"][0]["id"] = identity
            yield label, model

    def test_review_missing_fx_identity_keeps_calculation_dependencies_not_fake_refs(self):
        for label, model in self.missing_fx_identity_models():
            with self.subTest(identity=label):
                before = copy.deepcopy(model)
                gaps = baseline_module().validate_model(model, as_of=DAY)
                identity_gap = next(g for g in gaps if g["code"] == "missing-identity" and g["field"] == "fx[0].id")
                document = self.calculate(model)
                result = document["results"]
                expected = result["scenarios"]["expected"]
                month = expected["months"][0]
                self.assertEqual(month["total"]["amount"], "100.00")
                self.assertEqual(month["total"]["status"], "provisional")
                self.assertIn(identity_gap, result["gaps"])
                self.assertIn("handover", identity_gap["blocks"])
                self.assertTrue(result["handover_blocked"])
                for derived in (month["lines"][0]["cost"], month["total"], month["per_run"],
                                expected["annual_recurring"], expected["first_year"]):
                    self.assertEqual(derived["fx_refs"], [])
                    self.assertIn("/fx/0", derived["dependency_refs"])
                    self.assertTrue(derived["internal"])
                    self.assertIn("SYN-CONTEXT", derived["source_refs"])
                self.assertNotIn("internal", month["lines"][1]["cost"])
                evidence = month["lines"][0]["pricing_evidence"]
                self.assertEqual(evidence["as_of"], DAY.isoformat())
                self.assertEqual(evidence["records"][1]["date"], "2026-11-12")
                self.assertIn(identity_gap, evidence["gaps"])
                self.assertEqual(self.calc.validate_receipt(document, as_of=DAY, acknowledge_finops_preview=True),
                                 document["finops_preview"]["calculations"]["baseline"])
                self.assertEqual(model, before)

    def test_review_missing_fx_identity_receipt_refuses_stale_or_rehashed_outputs_not_keyerror(self):
        cases = list(self.missing_fx_identity_models())
        valid = copy.deepcopy(cases[0][1])
        valid["fx"][0]["id"] = "FX-TEST"
        cached = self.calculate(valid)
        for label, model in cases:
            with self.subTest(identity=label):
                stale = {**copy.deepcopy(model), "results": copy.deepcopy(cached["results"]),
                         "finops_preview": copy.deepcopy(cached["finops_preview"])}
                for ack in (False, None, 1, "true"):
                    with self.assertRaisesRegex(ValueError, "Explicit"):
                        self.calc.validate_receipt(stale, as_of=DAY, acknowledge_finops_preview=ack)
                with self.assertRaisesRegex(ValueError, "recalculate"):
                    self.calc.validate_receipt(stale, as_of=DAY, acknowledge_finops_preview=True)
                fresh = self.calculate(model)
                fresh["results"]["scenarios"]["expected"]["months"][0]["total"]["amount"] = "999.00"
                fresh["finops_preview"]["calculations"]["baseline"]["results_fingerprint"] = (
                    baseline_module("finops_preview").fingerprint(fresh["results"]))
                before = copy.deepcopy(fresh)
                with self.assertRaisesRegex(ValueError, "recalculate"):
                    self.calc.validate_receipt(fresh, as_of=DAY, acknowledge_finops_preview=True)
                self.assertEqual(fresh, before)

    def test_review_object_order_canonical_json_roundtrip_preserves_receipt(self):
        document = self.calculate()
        receipt = self.calc.validate_receipt(document, as_of=DAY, acknowledge_finops_preview=True)
        canonical = json.loads(json.dumps(document, sort_keys=True, allow_nan=False))
        before = copy.deepcopy(canonical)
        self.assertEqual(self.calc.validate_receipt(canonical, as_of=DAY, acknowledge_finops_preview=True), receipt)
        self.assertEqual(self.calculate(canonical)["results"], document["results"])
        self.assertEqual(canonical, before)

    def object_order_evidence_model(self):
        self.add_fx(status="unverified")
        self.model["fx"][0].update(internal=True, visibility="internal")
        self.model["rates"][0]["verification"]["verified_at"] = "2026-01-01"
        self.model["rates"][0]["source_id"] = None
        self.model["sources"][0]["lastValidatedAt"] = "2026-01-01"
        self.model["sources"][0]["applicability"] = None
        self.model["profile"]["outcome"]["unit"] = None
        self.model["baseline"]["assumptions"][0]["supporting_note"] = {
            "source_id": None, "sharingClassification": None, "src": [None, ""],
        }
        return copy.deepcopy(self.model)

    def test_review_object_order_permutations_preserve_all_results_and_evidence(self):
        for model in (example(), self.object_order_evidence_model()):
            expected = self.calculate(model)
            month = expected["results"]["scenarios"]["expected"]["months"][0]
            rich = bool(model["fx"])
            self.assertEqual(month["total"]["amount"], "100.00" if rich else "110.00")
            self.assertEqual(month["total"]["status"], "provisional")
            self.assertEqual(month["per_run"]["amount"], "1.000000" if rich else "1.100000")
            if rich:
                self.assertTrue(month["lines"][0]["cost"]["internal"])
                self.assertNotIn("internal", month["lines"][1]["cost"])
                self.assertIsNone(month["per_outcome"]["amount"])
                self.assertTrue(month["lines"][0]["pricing_evidence"]["gaps"])
            for order in ("sorted", "reverse", "rotate"):
                with self.subTest(rich=rich, order=order):
                    reordered = reorder_objects(model, order)
                    before = copy.deepcopy(reordered)
                    self.assertEqual(reordered, model)  # Dict order is immaterial; every authored list remains exact.
                    actual = self.calculate(reordered)
                    # Whole-result comparison covers root gaps AND every line's
                    # pricing_evidence.gaps, without normalising any arrays here.
                    self.assertEqual(actual["results"], expected["results"])
                    self.assertEqual(actual["finops_preview"], expected["finops_preview"])
                    canonical = reorder_objects(expected, order)
                    self.assertEqual(self.calc.validate_receipt(canonical, as_of=DAY, acknowledge_finops_preview=True),
                                     expected["finops_preview"]["calculations"]["baseline"])
                    self.assertEqual(reordered, before)

    def test_review_object_order_fix_does_not_accept_forged_diagnostics(self):
        document = self.calculate(self.object_order_evidence_model())
        for path in (("results", "gaps"),
                     ("results", "scenarios", "expected", "months", 0, "lines", 0, "pricing_evidence", "gaps")):
            for mutation in ("message", "blocks", "delete", "duplicate"):
                with self.subTest(path=path, mutation=mutation):
                    bad = copy.deepcopy(document)
                    gaps = bad
                    for key in path:
                        gaps = gaps[key]
                    if mutation == "message":
                        gaps[0]["message"] = "Fabricated diagnostic"
                    elif mutation == "blocks":
                        gaps[0]["blocks"] = []
                    elif mutation == "delete":
                        del gaps[0]
                    else:
                        gaps.append(copy.deepcopy(gaps[0]))
                    bad["finops_preview"]["calculations"]["baseline"]["results_fingerprint"] = (
                        baseline_module("finops_preview").fingerprint(bad["results"]))
                    before = copy.deepcopy(bad)
                    with self.assertRaisesRegex(ValueError, "recalculate"):
                        self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)
                    self.assertEqual(bad, before)

    def test_review_object_order_fix_preserves_meaningful_output_array_order(self):
        document = self.calculate(self.object_order_evidence_model())
        for path in (("results", "scenarios", "expected", "months"),
                     ("results", "scenarios", "expected", "months", 0, "lines"),
                     ("results", "scenarios", "expected", "months", 0, "lines", 0, "pricing_evidence", "records")):
            with self.subTest(path=path):
                bad = copy.deepcopy(document)
                rows = bad
                for key in path:
                    rows = rows[key]
                self.assertGreater(len(rows), 1)
                rows.reverse()
                bad["finops_preview"]["calculations"]["baseline"]["results_fingerprint"] = (
                    baseline_module("finops_preview").fingerprint(bad["results"]))
                with self.assertRaisesRegex(ValueError, "recalculate"):
                    self.calc.validate_receipt(bad, as_of=DAY, acknowledge_finops_preview=True)


if __name__ == "__main__":
    unittest.main()
