"""Contract-only checkpoint: explicit gaps, typed inputs and material lineage."""
from __future__ import annotations

import copy
import itertools
import json
import sys
import unittest
from datetime import date
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


if __name__ == "__main__":
    unittest.main()
