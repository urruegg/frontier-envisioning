"""Risk register (Workshops > Risks), PRD model (Vision > PRD), workshop verdicts on both and seeded attendee contributions."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

from tests.unit._util import ROOT, load

SKILL = "plugin/skills/frontier-blueprint"
risks = load(f"{SKILL}/scripts/risks.py", "rp_risks")
prd = load(f"{SKILL}/scripts/prd_model.py", "rp_prd")
build = load(f"{SKILL}/scripts/build_blueprint.py", "rp_build")
merge = load(f"{SKILL}/scripts/merge_feedback.py", "rp_merge")
seed = load(f"{SKILL}/scripts/seed_blueprint.py", "rp_seed")
scaffold = load("plugin/skills/frontier-solution-design/scripts/scaffold_design_docs.py", "rp_scaffold")
SAMPLE = ROOT / SKILL / "examples/caldova-blueprint.json"
CONTEXT = ROOT / "plugin/skills/frontier-context-discovery/examples/caldova-context.json"


class Rep:
    def __init__(self):
        self.warnings = []

    def warn(self, msg):
        self.warnings.append(msg)


def sample():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


def mini():
    return {"meta": {"version": "0.1"},
            "domains": [{"id": "D1", "name": "Service", "orchestrator": {"id": "D1-LEAD", "name": "Service Lead"},
                         "agents": [{"id": "D1-A01", "name": "Report Agent", "mvp": True,
                                     "canvas": {"trigger": "Visit closed", "plan": ["Transcribe", "Draft the report"], "outcome": "Report filed"},
                                     "declarations": {"refusal_set": "asked for a price", "measurement": "first-time-right rate"}}],
                         "use_cases": [{"id": "UC01", "name": "Voice report", "mvp": True, "agents": ["Report Agent"], "owner": "Head of Service",
                                        "problem": [["customer", "Reports take 40 minutes"]],
                                        "risk_points": [{"text": "Works-council approval for voice processing", "likelihood": 4, "impact": 5},
                                                        "Speech accuracy in noisy plants"]}]}],
            "it_readiness": {"groups": [{"items": [{"id": "IR-03", "item": "Test tenant", "status": "blocked", "owner": "IT"}]}]}}


class RiskRules(unittest.TestCase):
    def test_classify_rating_level(self):
        self.assertEqual(risks.classify("Works-council approval for voice processing"), "security")
        self.assertEqual(risks.classify("Copilot Credit budget overrun"), "cost")
        self.assertEqual(risks.classify("Speech accuracy in noisy plants"), "technology")
        self.assertEqual(risks.classify("Something unforeseen"), "delivery")
        self.assertEqual(risks.rating("4"), 4)
        self.assertEqual(risks.rating(9), 3)
        self.assertEqual(risks.rating(None, 2), 2)
        self.assertEqual([risks.level(s) for s in (25, 15, 12, 8, 7, 1)], ["high", "high", "medium", "medium", "low", "low"])

    def test_derives_use_case_and_readiness_risks(self):
        got = {r["id"]: r for r in risks.derive_risks(mini())}
        self.assertEqual(sorted(got), ["R-IR-03", "R-UC01-1", "R-UC01-2"])
        r1 = got["R-UC01-1"]
        self.assertEqual((r1["likelihood"], r1["impact"], r1["category"], r1["origin"]), (4, 5, "security", "use case"))
        self.assertEqual(r1["agents"], ["D1-A01"])
        self.assertEqual(got["R-UC01-2"]["impact"], 4, "MVP use cases default to impact 4")
        self.assertTrue(got["R-IR-03"]["title"].endswith("Test tenant"))
        self.assertTrue(all(r["derived"] for r in got.values()))

    def test_fill_keeps_authored_drops_stale_and_never_duplicates(self):
        bp = mini()
        bp["risks"] = {"items": [
            {"title": "Works-council approval for voice processing", "likelihood": 2, "impact": 5, "status": "mitigating"},
            {"id": "R-UC09-1", "title": "stale derived risk", "derived": True},
            {"title": "Unknown links", "category": "weird", "status": "maybe", "agents": ["D9-A99"], "likelihood": 7}]}
        rep = Rep()
        reg = risks.fill_risks(bp, rep)
        ids = [r["id"] for r in reg["items"]]
        self.assertNotIn("R-UC09-1", ids, "stale derived risks are rebuilt, not kept")
        self.assertIn("R-01", ids)
        self.assertNotIn("R-UC01-1", ids, "an authored risk with the same title wins over the derived one")
        self.assertIn("R-UC01-2", ids)
        self.assertEqual(reg["items"], sorted(reg["items"], key=lambda r: (-r["score"], r["id"])))
        authored = next(r for r in reg["items"] if r["id"] == "R-01")
        self.assertEqual((authored["score"], authored["level"], authored["status"]), (10, "medium", "mitigating"))
        text = " | ".join(rep.warnings)
        for part in ("category 'weird'", "status 'maybe'", "unknown agent 'D9-A99'", "likelihood 7"):
            self.assertIn(part, text)

    def test_caldova_register(self):
        bp = sample()
        reg = risks.fill_risks(bp, Rep())
        self.assertEqual(len(reg["items"]), 15)
        self.assertEqual([r["id"] for r in reg["items"][:2]], ["R-UC09-1", "R-C03"])
        self.assertEqual(sum(1 for r in reg["items"] if r["level"] == "high"), 2)
        self.assertEqual(sum(1 for r in reg["items"] if r.get("canon")), 7)


class PrdModel(unittest.TestCase):
    def test_copies_are_identical(self):
        a = (ROOT / SKILL / "scripts/prd_model.py").read_bytes()
        b = (ROOT / "plugin/skills/frontier-solution-design/scripts/prd_model.py").read_bytes()
        self.assertEqual(a, b, "keep prd_model.py identical in frontier-blueprint and frontier-solution-design")

    def test_derive_numbers_requirements_and_links(self):
        bp = mini()
        risks.fill_risks(bp)
        m = prd.derive(bp)
        self.assertEqual(m["mvp_agents"], ["D1-A01"])
        self.assertEqual([r["id"] for r in m["platform"]][:2], ["FR-0001", "FR-0002"])
        reqs = m["agents"][0]["requirements"]
        self.assertEqual([r["id"] for r in reqs], ["FR-0011", "FR-0012", "FR-0013", "FR-0014"])
        self.assertEqual([r["kind"] for r in reqs], ["trigger", "step", "step", "outcome"])
        self.assertEqual([a["id"] for a in m["acceptance"]], ["AC-001", "AC-002"])
        self.assertEqual(len(m["nfr"]), 12)
        self.assertEqual(m["problems"][0]["items"], [["customer", "Reports take 40 minutes"]])
        self.assertEqual(m["risks"][0]["id"], "R-UC01-1")
        self.assertIsInstance(m["risks"][0]["score"], int)

    def test_fill_keeps_authored_fields(self):
        bp = mini()
        bp["prd"] = {"status": "agreed", "problem": "Reports are slow", "scope": ["stale"], "workshop_notes": [{"note": "ok"}]}
        rep = Rep()
        m = prd.fill_prd(bp, rep)
        self.assertEqual((m["status"], m["problem"]), ("agreed", "Reports are slow"))
        self.assertEqual(m["scope"][0]["agent"], "D1-A01", "derived fields are recomputed")
        self.assertEqual(m["workshop_notes"], [{"note": "ok"}])
        self.assertEqual(rep.warnings, [])
        bp["prd"]["status"] = "maybe"
        prd.fill_prd(bp, rep)
        self.assertTrue(any("prd.status" in w for w in rep.warnings))

    def test_blueprint_and_design_prd_share_ids(self):
        bp = sample()
        rep = Rep()
        risks.fill_risks(bp, rep)
        m = prd.fill_prd(bp, rep)
        self.assertEqual(sum(len(a["requirements"]) for a in m["agents"]) + len(m["platform"]), 35)
        agents = prd.mvp_agents(bp)
        doms = list({id(d): d for _, d in agents}.values())
        text = scaffold.build_prd(bp, agents, doms, "Microsoft Innovation Hub", "2026-11-12")
        for r in m["agents"][0]["requirements"][:3] + m["acceptance"][:2] + m["nfr"][:2]:
            self.assertIn(r["id"], text)


class WorkshopVerdicts(unittest.TestCase):
    def test_merge_risk_and_prd_verdicts(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            quiet(build.main, ["--data", str(SAMPLE), "--out", str(t / "bp.html"), "--save-normalized", str(t / "bp.json")])
            bid = json.loads((t / "bp.json").read_text(encoding="utf-8"))["meta"].get("id")
            fb = {"type": "frontier-blueprint-feedback", "blueprint": bid, "exported": "2026-11-12T16:40:00Z",
                  "validations": {"risk:R-UC09-1": {"status": "mitigating", "likelihood": 3, "impact": 5, "note": "Briefing booked"},
                                  "risk:R-C05": {"status": "rejected"}, "risk:R-NOPE": {"status": "open"},
                                  "prd:scope": {"status": "validated", "note": "Two MVP agents agreed"}}}
            (t / "fb.json").write_text(json.dumps(fb), encoding="utf-8")
            code = quiet(merge.main, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb.json"), "--out", str(t / "bp2.json")])
            self.assertEqual(code, 0)
            quiet(build.main, ["--data", str(t / "bp2.json"), "--out", str(t / "bp2.html"), "--save-normalized", str(t / "bp3.json")])
            out = json.loads((t / "bp3.json").read_text(encoding="utf-8"))
            its = {r["id"]: r for r in out["risks"]["items"]}
            r = its["R-UC09-1"]
            self.assertEqual((r["status"], r["likelihood"], r["impact"], r["score"], r["derived"]), ("mitigating", 3, 5, 15, False))
            self.assertEqual(r["workshop_notes"][0]["note"], "Briefing booked")
            self.assertIn("W01", r["src"])
            self.assertEqual(sum(1 for x in out["risks"]["items"] if x["id"] == "R-UC09-1"), 1, "no duplicate after the rebuild")
            self.assertEqual((its["R-C05"]["status"], its["R-C05"]["resolution"]), ("closed", "not a risk"))
            self.assertEqual(out["prd"]["status"], "agreed")
            self.assertEqual(out["prd"]["workshop_notes"][0]["src"], ["W01"])
            self.assertNotIn("R-C05", [x["id"] for x in out["prd"]["risks"]], "closed risks leave the PRD")


class SeededAttendees(unittest.TestCase):
    def test_contributions_from_transcript_speakers(self):
        ctx = json.loads(CONTEXT.read_text(encoding="utf-8"))
        ctx = copy.deepcopy(ctx)
        ctx["stakeholders"][0]["name"] = "Anna Keller"
        ctx["facts"][0]["evidence"][0]["speaker"] = "Anna Keller"
        with tempfile.TemporaryDirectory() as t:
            p, o = Path(t) / "ctx.json", Path(t) / "bp.json"
            p.write_text(json.dumps(ctx), encoding="utf-8")
            self.assertEqual(quiet(seed.main, ["--context", str(p), "--out", str(o)]), 0)
            bp = json.loads(o.read_text(encoding="utf-8"))
        person = bp["attendees"]["people"][0]
        said = [c for c in person["contributions"] if isinstance(c, dict) and c.get("at")]
        self.assertEqual(said[0]["at"], ctx["facts"][0]["evidence"][0]["at"])
        self.assertEqual(said[0]["src"], [ctx["facts"][0]["evidence"][0]["source"]])
        self.assertTrue(all(isinstance(c, dict) and c.get("src") for c in person["contributions"]))
        self.assertEqual([r["id"] for r in bp["risks"]["items"]][:2], ["R-C01", "R-C02"], "Hub canon risks seeded")
        self.assertIn("board", bp["factory"])


class P1Regressions(unittest.TestCase):
    INVALID_RATINGS = (True, False, float("nan"), float("inf"), -float("inf"), 2.5, "2.5",
                       "3.00000000000000000001", 0, 6, -1, "bad", None)

    def merge_model(self, bp, validations):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "bp.json").write_text(json.dumps(bp), encoding="utf-8")
            (p / "fb.json").write_text(json.dumps({
                "type": "frontier-blueprint-feedback", "exported": "2026-11-12T16:00:00Z",
                "validations": validations,
            }), encoding="utf-8")
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                code = merge.main(["--blueprint", str(p / "bp.json"), "--feedback", str(p / "fb.json"),
                                   "--out", str(p / "out.json"), "--no-bump"])
            self.assertEqual(code, 0)
            return json.loads((p / "out.json").read_text(encoding="utf-8")), json.loads(capture.getvalue())

    def test_ratings_require_finite_integer_in_range(self):
        for value in self.INVALID_RATINGS:
            with self.subTest(value=value):
                self.assertEqual(risks.rating(value, 0), 0)
        for value in (1, 2, 3, 4, 5, "4", 4.0):
            with self.subTest(valid=value):
                self.assertEqual(risks.rating(value, 0), int(value))

    def test_invalid_authored_ratings_warn_and_default(self):
        for value in self.INVALID_RATINGS:
            for field in ("likelihood", "impact"):
                with self.subTest(value=value, field=field):
                    bp = mini()
                    bp["risks"] = {"items": [{"id": "R-X", "title": "Synthetic", field: value}]}
                    rep = Rep()
                    risks.fill_risks(bp, rep)
                    risk = next(r for r in bp["risks"]["items"] if r["id"] == "R-X")
                    self.assertEqual(risk[field], 3)
                    self.assertTrue(any(field in w and "1-5" in w for w in rep.warnings))

    def test_invalid_source_ratings_warn_and_default(self):
        bp = mini()
        bp["domains"][0]["use_cases"][0]["risk_points"][0]["impact"] = 2.5
        rep = Rep()
        risks.fill_risks(bp, rep)
        self.assertEqual(next(r for r in bp["risks"]["items"] if r["id"] == "R-UC01-1")["impact"], 3)
        self.assertTrue(any("impact" in w for w in rep.warnings))

    def test_strict_build_fails_for_invalid_authored_rating(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            bp = sample()
            bp["risks"]["items"][0]["likelihood"] = 2.5
            (p / "input.json").write_text(json.dumps(bp), encoding="utf-8")
            code = quiet(build.main, ["--data", str(p / "input.json"), "--out", str(p / "bp.html"),
                                     "--report", str(p / "report.json"), "--strict"])
            self.assertNotEqual(code, 0)
            self.assertFalse((p / "bp.html").exists())
            rep = json.loads((p / "report.json").read_text(encoding="utf-8"))
            self.assertTrue(any("likelihood" in w for w in rep["warnings"]))

    def test_invalid_feedback_is_atomic_reported_and_not_owned(self):
        bp = mini()
        risks.fill_risks(bp)
        for value in self.INVALID_RATINGS:
            for field in ("likelihood", "impact"):
                with self.subTest(value=value, field=field):
                    before = copy.deepcopy(bp["risks"])
                    out, summary = self.merge_model(bp, {"risk:R-UC01-1": {
                        "status": "accepted", field: value, "note": "Must not apply",
                    }})
                    self.assertEqual(out["risks"], before)
                    self.assertEqual(summary.get("risks_updated", 0), 0)
                    self.assertTrue(summary.get("invalid"), summary)

    def test_unknown_and_invalid_verdicts_are_explicit(self):
        bp = mini()
        risks.fill_risks(bp)
        prd.fill_prd(bp)
        out, summary = self.merge_model(bp, {
            "risk:R-UC01-1": {"status": "maybe"}, "prd:scope": {"status": "maybe"},
            "risk:R-NOT-FOUND": {"status": "open"}, "prd:unknown": {"status": "validated"},
        })
        self.assertEqual(out["risks"], bp["risks"])
        self.assertEqual(out["prd"], bp["prd"])
        self.assertEqual(summary.get("risks_updated", 0), 0)
        self.assertEqual(summary.get("prd_updated", 0), 0)
        self.assertEqual(len(summary.get("invalid", [])), 2)
        self.assertEqual(set(summary["unknown"]), {"risk:R-NOT-FOUND", "prd:unknown"})

    def test_subset_prd_keeps_full_requirement_and_acceptance_ids(self):
        bp = mini()
        second = copy.deepcopy(bp["domains"][0]["agents"][0])
        second.update(id="D1-A02", name="Second Agent")
        bp["domains"][0]["agents"].append(second)
        full = prd.derive(bp)
        subset = prd.derive(bp, ["D1-A02"])
        self.assertEqual(subset["agents"][0], full["agents"][1])
        self.assertEqual(subset["acceptance"], [a for a in full["acceptance"] if a["agent"] == "D1-A02"])
        agents = prd.mvp_agents(bp, ["D1-A02"])
        text = scaffold.build_prd(bp, agents, [bp["domains"][0]], "Hub", "2026-11-12")
        for req in full["agents"][1]["requirements"]:
            self.assertIn(req["id"], text)
        for ac in subset["acceptance"]:
            self.assertIn(ac["id"], text)
        self.assertEqual(prd.derive(bp, [])["agents"], [], "an explicit empty selection is not the default")

    def test_scaffold_uses_authored_fields_and_shared_risks(self):
        bp = mini()
        bp["prd"] = {"problem": "Authored problem marker", "goals": ["Authored goal marker"],
                     "out_of_scope": ["Authored exclusion marker"], "exit_test": "Authored exit marker"}
        risks.fill_risks(bp)
        prd.fill_prd(bp)
        text = scaffold.build_prd(bp, prd.mvp_agents(bp), [bp["domains"][0]], "Hub", "2026-11-12")
        for marker in ("Authored problem marker", "Authored goal marker", "Authored exclusion marker", "Authored exit marker",
                       "R-UC01-1"):
            self.assertIn(marker, text)

    def test_source_reordering_preserves_risk_ids_and_workshop_content(self):
        bp = mini()
        risks.fill_risks(bp)
        bp, _ = self.merge_model(bp, {"risk:R-UC01-1": {"status": "accepted", "note": "Original verdict"}})
        bp["domains"][0]["use_cases"][0]["risk_points"].reverse()
        rep = Rep()
        risks.fill_risks(bp, rep)
        items = bp["risks"]["items"]
        first = next(r for r in items if r["id"] == "R-UC01-1")
        self.assertIn("Works-council", first["title"])
        self.assertEqual(first["status"], "accepted")
        self.assertEqual(first["workshop_notes"][0]["note"], "Original verdict")
        second = next(r for r in items if r["title"] == "Speech accuracy in noisy plants")
        self.assertEqual(second["id"], "R-UC01-2")
        before = copy.deepcopy(bp["risks"])
        risks.fill_risks(bp)
        self.assertEqual(bp["risks"], before)
        self.assertEqual(len(items), 3)

    def test_source_edit_does_not_transfer_exported_verdict(self):
        bp = mini()
        risks.fill_risks(bp)
        bp["domains"][0]["use_cases"][0]["risk_points"][0]["text"] = "Different source risk"
        out, summary = self.merge_model(bp, {"risk:R-UC01-1": {"status": "accepted", "note": "Stale verdict"}})
        self.assertIn("risk:R-UC01-1", summary["unknown"])
        risks.fill_risks(out)
        new = next(r for r in out["risks"]["items"] if r["title"] == "Different source risk")
        self.assertNotEqual(new["id"], "R-UC01-1")
        self.assertEqual(new["status"], "open")
        self.assertNotIn("workshop_notes", new)

    def test_source_edit_keeps_prior_workshop_risk_separate(self):
        bp = mini()
        risks.fill_risks(bp)
        bp, _ = self.merge_model(bp, {"risk:R-UC01-1": {"status": "accepted", "note": "Kept verdict"}})
        bp["domains"][0]["use_cases"][0]["risk_points"][0]["text"] = "New risk after editing"
        rep = Rep()
        risks.fill_risks(bp, rep)
        items = bp["risks"]["items"]
        old = next(r for r in items if r["id"] == "R-UC01-1")
        self.assertIn("Works-council", old["title"])
        new = next(r for r in items if r["title"] == "New risk after editing")
        self.assertNotEqual(new["id"], old["id"])
        self.assertEqual(new["status"], "open")
        self.assertTrue(rep.warnings)

    def test_pre_binding_derived_record_does_not_transfer_stale_feedback(self):
        bp = mini()
        risks.fill_risks(bp)
        bp["risks"].pop("source_ids", None)
        for r in bp["risks"]["items"]:
            r.pop("source_key", None)
        bp["domains"][0]["use_cases"][0]["risk_points"][0]["text"] = "Edited legacy source risk"
        out, summary = self.merge_model(bp, {"risk:R-UC01-1": {"status": "accepted"}})
        self.assertIn("risk:R-UC01-1", summary["unknown"])
        self.assertEqual(next(r for r in out["risks"]["items"] if r["title"] == "Edited legacy source risk")["status"], "open")

    def test_feedback_source_binding_mismatch_is_rejected(self):
        bp = mini()
        risks.fill_risks(bp)
        out, summary = self.merge_model(bp, {"risk:R-UC01-1": {"status": "accepted", "source_key": "different-source"}})
        self.assertEqual(out["risks"], bp["risks"])
        self.assertEqual(summary.get("risks_updated", 0), 0)
        self.assertTrue(summary.get("invalid"))

    def test_non_mvp_subset_ids_do_not_depend_on_selected_siblings(self):
        bp = mini()
        for n in (2, 3):
            agent = copy.deepcopy(bp["domains"][0]["agents"][0])
            agent.update(id=f"D1-A0{n}", name=f"Extra {n}", mvp=False)
            bp["domains"][0]["agents"].append(agent)
        all_selected = prd.derive(bp, ["D1-A01", "D1-A02", "D1-A03"])
        one = prd.derive(bp, ["D1-A03"])
        self.assertEqual(one["agents"], [all_selected["agents"][2]])
        self.assertEqual(one["acceptance"], [a for a in all_selected["acceptance"] if a["agent"] == "D1-A03"])

    def test_duplicate_authored_ids_preserve_content_without_ambiguous_feedback(self):
        bp = mini()
        bp["risks"] = {"items": [{"id": "R-DUP", "title": "First authored", "notes": "Keep one"},
                                  {"id": "R-DUP", "title": "Second authored", "notes": "Keep two"}]}
        original = copy.deepcopy(bp)
        out, summary = self.merge_model(bp, {"risk:R-DUP": {"status": "accepted"}})
        self.assertEqual(summary.get("risks_updated", 0), 0)
        self.assertTrue(summary.get("invalid"))
        self.assertFalse(any(r.get("status") == "accepted" for r in out["risks"]["items"]))
        rep = Rep()
        risks.fill_risks(bp, rep)
        self.assertTrue(any("duplicate" in w.lower() for w in rep.warnings))
        self.assertEqual(len({r["id"] for r in bp["risks"]["items"]}), len(bp["risks"]["items"]))
        authored = {r["title"]: (r["id"], r["notes"]) for r in bp["risks"]["items"] if r.get("notes")}
        original["risks"]["items"].reverse()
        risks.fill_risks(original)
        self.assertEqual(authored, {r["title"]: (r["id"], r["notes"]) for r in original["risks"]["items"] if r.get("notes")})

    def test_customer_scrub_removes_internal_only_copies_across_outputs(self):
        bp = sample()
        markers = ("P1RISKPRIVATE71", "P1PRDPRIVATE72", "P1CONTRIBPRIVATE73", "P1SOURCEPRIVATE74", "P1AGENTPRIVATE75")
        bp["evidence"].append({"id": "I-PRIVATE", "visibility": "internal", "title": "Internal evidence"})
        bp["risks"]["items"].append({"id": "R-PRIVATE", "title": markers[0], "src": ["I-PRIVATE"]})
        bp["prd"] = {"problem": markers[1], "goals": [markers[1]], "src": ["I-PRIVATE"]}
        bp["attendees"]["people"][0]["contributions"].append({"text": markers[2], "src": ["I-PRIVATE"]})
        uc = bp["domains"][1]["use_cases"][0]
        uc["risk_points"] = [{"text": markers[3], "src": ["I-PRIVATE"]}]
        bp["domains"][1]["agents"][0]["canvas"]["plan"].append(markers[4])
        bp["domains"][1]["agents"][0]["canvas"]["src"] = ["I-PRIVATE"]
        # A privacy classification is not a visibility flag.
        bp["domains"][1]["agents"][0]["declarations"]["data_classification"] = "Internal / confidential"
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "input.json").write_text(json.dumps(bp), encoding="utf-8")
            quiet(build.main, ["--data", str(p / "input.json"), "--out", str(p / "internal.html"),
                              "--save-normalized", str(p / "internal.json")])
            self.assertTrue((p / "internal.json").exists())
            quiet(build.main, ["--data", str(p / "internal.json"), "--audience", "customer",
                              "--out", str(p / "customer.html"), "--save-normalized", str(p / "customer.json")])
            self.assertEqual(quiet(scaffold.main, ["--blueprint", str(p / "customer.json"), "--out-dir", str(p / "design")]), 0)
            for path in [p / "customer.json", p / "customer.html", *(p / "design").rglob("*.md")]:
                text = path.read_text(encoding="utf-8")
                for marker in markers:
                    self.assertNotIn(marker, text, f"{marker} leaked to {path.name}")
            self.assertIn("Internal / confidential", (p / "customer.json").read_text(encoding="utf-8"))

    def test_caldova_normalized_model_shapes(self):
        bp = sample()
        rep = build.Report()
        build.normalise(bp, rep)
        risks.fill_risks(bp, rep)
        prd.fill_prd(bp, rep)
        stats = build.stats(bp)
        self.assertEqual(stats["risks"], 15)
        self.assertEqual([sum(r["level"] == level for r in bp["risks"]["items"]) for level in ("high", "medium", "low")], [2, 9, 4])
        self.assertEqual((stats["prd_requirements"], len(bp["prd"]["nfr"]), len(bp["prd"]["mvp_agents"])), (35, 12, 2))
        self.assertEqual((stats["attendees"], stats["contributions_with_evidence"]), (8, 13))
        self.assertEqual(rep.warnings, [])


class DisclosureRoundTrips(unittest.TestCase):
    """Content visibility must survive model projection and workshop promotion."""

    merge_model = P1Regressions.merge_model

    def build_saved(self, bp, folder, name, audience="internal"):
        source, normalized, html = (folder / f"{name}{suffix}" for suffix in ("-input.json", ".json", ".html"))
        source.write_text(json.dumps(bp), encoding="utf-8", newline="\n")
        code = quiet(build.main, ["--data", str(source), "--audience", audience, "--out", str(html),
                                  "--save-normalized", str(normalized)])
        self.assertEqual(code, 0)
        return json.loads(normalized.read_text(encoding="utf-8"))

    def assert_customer_outputs_hide(self, bp, folder, marker):
        customer = self.build_saved(bp, folder, "customer", "customer")
        self.assertEqual(quiet(scaffold.main, ["--blueprint", str(folder / "customer.json"),
                                             "--out-dir", str(folder / "design")]), 0)
        paths = [folder / "customer.json", folder / "customer.html", *(folder / "design").rglob("*.md")]
        for path in paths:
            with self.subTest(output=path.relative_to(folder).as_posix()):
                self.assertFalse(marker in path.read_text(encoding="utf-8"), f"private content leaked to {path.name}")
        return customer

    def promoted_private_risk(self, marker, explicit_flag=False, legacy_content=False, flag_location="point"):
        bp = sample()
        private_id = "I-PROMOTED-RISK"
        bp["evidence"].append({"id": private_id, "visibility": "internal", "title": "Private source"})
        domain, uc = next((d, u) for d in bp["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
        point = {"text": marker, "likelihood": 4, "impact": 5, "mitigation": f"Mitigate {marker}",
                 "src": list(uc.get("src", [])) if explicit_flag else [private_id]}
        if explicit_flag:
            {"point": point, "use_case": uc, "journey": domain}[flag_location]["internal"] = True
        uc["risk_points"].append(point)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            internal = self.build_saved(bp, folder, "internal")
            risk = next(r for r in internal["risks"]["items"] if r["id"] == "R-UC05-3")
            self.assertEqual(risk["title"], marker)
            self.assertTrue(risk["derived"])
            promoted, summary = self.merge_model(internal, {
                "risk:R-UC05-3": {"status": "accepted"},
                "risk:R-C05": {"status": "accepted", "note": "Public risk remains visible"},
            })
            self.assertEqual(summary["risks_updated"], 2)
            if legacy_content:
                # Received/previously saved promoted rows may predate the
                # content-visibility metadata, but still have their bound source.
                prior = next(r for r in promoted["risks"]["items"] if r["id"] == "R-UC05-3")
                prior.pop("content_src", None)
                prior.pop("internal", None)
            accepted = self.build_saved(promoted, folder, "accepted")
            risk = next(r for r in accepted["risks"]["items"] if r["id"] == "R-UC05-3")
            self.assertEqual((risk["title"], risk["status"], risk["derived"]), (marker, "accepted", False))
            self.assertIn("W01", risk["src"], "verdict provenance remains available internally")
            if not explicit_flag:
                self.assertIn(private_id, risk["src"])
            customer = self.assert_customer_outputs_hide(accepted, folder, marker)
            self.assertFalse(any(r["id"] == "R-UC05-3" for r in customer["risks"]["items"]))
            public = next(r for r in customer["risks"]["items"] if r["id"] == "R-C05")
            self.assertEqual(public["status"], "accepted")
            self.assertEqual(public["workshop_notes"][0]["note"], "Public risk remains visible")

    def test_promoted_internal_source_risk_stays_private(self):
        self.promoted_private_risk("P1PROMOTEDSRCPRIVATE81")

    def test_promoted_explicit_internal_risk_stays_private(self):
        self.promoted_private_risk("P1PROMOTEDFLAGPRIVATE82", explicit_flag=True)

    def test_promoted_legacy_risk_recovers_bound_source_visibility(self):
        for flag in (False, True):
            with self.subTest(explicit_flag=flag):
                self.promoted_private_risk(f"P1PROMOTEDLEGACYPRIVATE{flag}", explicit_flag=flag, legacy_content=True)

    def test_promoted_risk_inherits_source_container_visibility(self):
        for location in ("use_case", "journey"):
            with self.subTest(location=location):
                self.promoted_private_risk(f"P1PROMOTEDCONTAINERPRIVATE{location}", explicit_flag=True, flag_location=location)

    def test_promoted_readiness_risk_inherits_group_visibility(self):
        bp = sample()
        marker = "P1PROMOTEDREADINESSPRIVATE85"
        bp["it_readiness"]["groups"].append({
            "internal": True, "items": [{"id": "IR-PRIVATE", "item": marker, "status": "blocked", "src": ["E08"]}],
        })
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            internal = self.build_saved(bp, folder, "internal")
            promoted, summary = self.merge_model(internal, {"risk:R-IR-PRIVATE": {"status": "accepted"}})
            self.assertEqual(summary["risks_updated"], 1)
            accepted = self.build_saved(promoted, folder, "accepted")
            self.assert_customer_outputs_hide(accepted, folder, marker)

    def test_direct_customer_rechecks_newly_private_bound_source(self):
        bp = sample()
        marker = "P1DIRECTNEWLYPRIVATE86"
        uc = next(u for d in bp["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
        uc["risk_points"].append({"text": marker, "likelihood": 4, "impact": 5, "src": ["E06"]})
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            internal = self.build_saved(bp, folder, "internal")
            promoted, summary = self.merge_model(internal, {"risk:R-UC05-3": {"status": "accepted"}})
            self.assertEqual(summary["risks_updated"], 1)
            self.assertEqual(summary["unknown"], [])
            risk = next(r for r in promoted["risks"]["items"] if r["id"] == "R-UC05-3")
            self.assertEqual((risk["status"], risk["derived"], risk["internal"]), ("accepted", False, False))
            self.assertEqual(promoted["risks"]["source_ids"][risk["source_key"]], risk["id"])
            source = next(p for d in promoted["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05"
                          for p in u["risk_points"] if isinstance(p, dict) and p.get("text") == marker)
            source["internal"] = True
            # No internal build/normalisation between this edit and customer export.
            customer = self.assert_customer_outputs_hide(promoted, folder, marker)
            self.assertFalse(any(r["id"] == "R-UC05-3" for r in customer["risks"]["items"]))

    def test_direct_customer_recovers_legacy_promoted_content_privacy(self):
        for flag in (False, True):
            with self.subTest(explicit_flag=flag), tempfile.TemporaryDirectory() as tmp:
                bp = sample()
                marker = f"P1DIRECTLEGACYPRIVATE87{flag}"
                bp["evidence"].append({"id": "I-DIRECT", "visibility": "internal", "title": "Private content"})
                uc = next(u for d in bp["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
                point = {"text": marker, "likelihood": 4, "impact": 5, "src": ["E06"] if flag else ["I-DIRECT"]}
                if flag:
                    point["internal"] = True
                uc["risk_points"].append(point)
                folder = Path(tmp)
                internal = self.build_saved(bp, folder, "internal")
                promoted, summary = self.merge_model(internal, {"risk:R-UC05-3": {"status": "accepted"}})
                self.assertEqual(summary["risks_updated"], 1)
                risk = next(r for r in promoted["risks"]["items"] if r["id"] == "R-UC05-3")
                risk.pop("content_src")
                risk.pop("internal")
                self.assertEqual((risk["status"], risk["derived"]), ("accepted", False))
                self.assertIn("W01", risk["src"])
                self.assertEqual(promoted["risks"]["source_ids"][risk["source_key"]], risk["id"])
                # Direct customer build must recover privacy before losing its source.
                customer = self.assert_customer_outputs_hide(promoted, folder, marker)
                self.assertFalse(any(r["id"] == "R-UC05-3" for r in customer["risks"]["items"]))

    def test_explicit_internal_prd_direct_customer_build_is_private(self):
        bp = sample()
        marker = "P1PRIVATEPRDFLAGDIRECT83"
        bp["prd"] = {"internal": True, "problem": marker, "goals": [f"Goal {marker}"]}
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_customer_outputs_hide(bp, Path(tmp), marker)

    def test_explicit_internal_prd_internal_customer_round_trip_is_private(self):
        bp = sample()
        marker = "P1PRIVATEPRDFLAGROUNDTRIP84"
        bp["prd"] = {"internal": True, "problem": marker, "goals": [f"Goal {marker}"]}
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            internal = self.build_saved(bp, folder, "internal")
            self.assertEqual(internal["prd"]["problem"], marker)
            self.assert_customer_outputs_hide(internal, folder, marker)

    def test_prd_projection_keeps_internal_flag(self):
        bp = mini()
        bp["prd"] = {"internal": True, "problem": "Kept only in internal models"}
        self.assertIs(prd.fill_prd(bp).get("internal"), True)

    def test_current_source_citation_correction_restricts_promoted_content(self):
        bp = sample()
        marker = "P1CURRENTCITATIONPRIVATE91"
        bp["evidence"].append({"id": "I-CORRECTED", "visibility": "internal", "title": "Corrected source"})
        uc = next(u for d in bp["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
        uc["risk_points"].append({"text": marker, "likelihood": 4, "impact": 5, "src": ["E06"]})
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            internal = self.build_saved(bp, folder, "internal")
            promoted, summary = self.merge_model(internal, {"risk:R-UC05-3": {"status": "accepted", "note": "Keep verdict"}})
            self.assertEqual(summary["risks_updated"], 1)
            source = next(p for d in promoted["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05"
                          for p in u["risk_points"] if isinstance(p, dict) and p.get("text") == marker)
            source["src"] = ["I-CORRECTED"]
            before = copy.deepcopy(promoted)
            customer = self.assert_customer_outputs_hide(promoted, folder, marker)
            self.assertFalse(any(r["id"] == "R-UC05-3" for r in customer["risks"]["items"]))
            self.assertEqual(promoted, before, "customer export does not alter the internal workshop record")
            refreshed = copy.deepcopy(promoted)
            risks.fill_risks(refreshed)
            row = next(r for r in refreshed["risks"]["items"] if r["id"] == "R-UC05-3")
            self.assertEqual(row["content_src"], ["I-CORRECTED"])
            self.assertEqual((row["title"], row["status"], row["derived"]), (marker, "accepted", False))
            self.assertEqual(row["workshop_notes"][0]["note"], "Keep verdict")

    def test_retired_risk_lineage_inherits_current_use_case_privacy(self):
        for private_mode in ("flag", "citations"):
            with self.subTest(private_mode=private_mode), tempfile.TemporaryDirectory() as tmp:
                bp = sample()
                marker = f"P1RETIREDLINEAGEPRIVATE92{private_mode}"
                bp["evidence"].append({"id": "I-LINEAGE", "visibility": "internal", "title": "Private use case"})
                uc = next(u for d in bp["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
                uc["risk_points"].append({"text": marker, "likelihood": 4, "impact": 5, "src": ["E06"]})
                folder = Path(tmp)
                internal = self.build_saved(bp, folder, "internal")
                promoted, summary = self.merge_model(internal, {"risk:R-UC05-3": {"status": "accepted", "note": "Historical verdict"}})
                self.assertEqual(summary["risks_updated"], 1)
                uc = next(u for d in promoted["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
                if private_mode == "flag":
                    uc["internal"] = True
                else:
                    uc["src"] = ["I-LINEAGE"]
                source = next(p for p in uc["risk_points"] if isinstance(p, dict) and p.get("text") == marker)
                source["text"] = f"Replacement of {marker}"
                customer = self.assert_customer_outputs_hide(promoted, folder, marker)
                self.assertFalse(any(r["id"] == "R-UC05-3" for r in customer["risks"]["items"]))
                refreshed = copy.deepcopy(promoted)
                risks.fill_risks(refreshed)
                old = next(r for r in refreshed["risks"]["items"] if r["id"] == "R-UC05-3")
                self.assertTrue(old.get("internal"), "retired content still inherits its current parent visibility")
                self.assertEqual((old["title"], old["status"], old["derived"]), (marker, "accepted", False))
                new = next(r for r in refreshed["risks"]["items"] if r["title"] == source["text"])
                self.assertNotEqual(new["id"], old["id"])
                self.assertEqual(new["status"], "open", "historical verdict is not transferred to edited content")

    def test_source_correction_does_not_declassify_retained_private_content(self):
        bp = sample()
        marker = "P1RETAINEDPRIVATEHISTORY93"
        bp["evidence"].append({"id": "I-HISTORY", "visibility": "internal", "title": "Retained private evidence"})
        uc = next(u for d in bp["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
        uc["risk_points"].append({"text": marker, "likelihood": 4, "impact": 5, "src": ["I-HISTORY"]})
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            internal = self.build_saved(bp, folder, "internal")
            promoted, _ = self.merge_model(internal, {"risk:R-UC05-3": {"status": "accepted"}})
            risk = next(r for r in promoted["risks"]["items"] if r["id"] == "R-UC05-3")
            self.assertEqual(risk["content_src"], ["I-HISTORY"])
            risk.pop("internal", None)  # Legacy record still has its content provenance.
            uc = next(u for d in promoted["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
            source = next(p for p in uc["risk_points"] if p.get("text") == marker)
            source["src"] = ["E06"]
            source.pop("internal", None)
            self.assert_customer_outputs_hide(promoted, folder, marker)


class ExplicitPrdScope(unittest.TestCase):
    def test_cross_journey_selection_excludes_other_use_case_and_dependencies(self):
        bp = sample()
        risks.fill_risks(bp)
        full = prd.derive(bp)
        for aid, did, uid, excluded_uid, excluded_dependency in (
            ("D2-A01", "D2", "UC05", "UC09", "Field Service write actions"),
            ("D3-A05", "D3", "UC09", "UC05", "Ariba requisition API"),
        ):
            with self.subTest(agent=aid):
                model = prd.derive(bp, [aid])
                self.assertEqual([u["id"] for u in model["use_cases"]], [uid])
                self.assertTrue(all(p["use_case"] == uid for p in model["problems"]))
                self.assertNotIn(excluded_dependency, model["dependencies"])
                other_option = next(m["needs"] for m in bp["mvp_options"] if m["domain"] != did)
                self.assertNotIn(other_option, model["dependencies"])
                self.assertTrue(all(k["journey"] == did for k in model["kpis"]))
                self.assertTrue(all(p["journey"] == did for p in model["personas"]))
                self.assertFalse(any(str(r["id"]).startswith(f"R-{excluded_uid}-") for r in model["risks"]))
                self.assertEqual(model["agents"][0], next(a for a in full["agents"] if a["agent"] == aid))
                self.assertEqual(model["acceptance"], [a for a in full["acceptance"] if a["agent"] == aid])
                agents = prd.mvp_agents(bp, [aid])
                text = scaffold.build_prd(bp, agents, [agents[0][1]], "Hub", "2026-11-12")
                dependencies = text.split("## 10. Dependencies", 1)[1].split("## 11. Risks", 1)[0]
                self.assertNotIn(excluded_dependency, dependencies)
                self.assertNotIn(other_option, dependencies)

    def test_explicit_empty_selection_has_no_customer_scope(self):
        bp = sample()
        risks.fill_risks(bp)
        self.assertEqual(prd.derive(bp)["mvp_agents"], ["D2-A01", "D3-A05"])
        empty = prd.derive(bp, [])
        for field in ("mvp_agents", "scope", "agents", "use_cases", "problems", "acceptance", "kpis",
                      "personas", "dependencies", "risks", "decisions"):
            with self.subTest(field=field):
                self.assertEqual(empty[field], [])
        self.assertEqual(len(empty["platform"]), 10)
        self.assertEqual(len(empty["nfr"]), 12)

    def test_specific_risk_links_do_not_leak_via_shared_journey_or_severity(self):
        bp = mini()
        second = copy.deepcopy(bp["domains"][0]["agents"][0])
        second.update(id="D1-A02", name="Other Agent")
        bp["domains"][0]["agents"].append(second)
        bp["risks"] = {"items": [
            {"id": "R-OTHER", "title": "Other agent only", "agents": ["D1-A02"], "journeys": ["D1"], "likelihood": 5, "impact": 5},
            {"id": "R-PLATFORM", "title": "Platform applies to all agents", "canon": True},
            {"id": "R-UNSCOPED", "title": "Unknown applicability", "likelihood": 5, "impact": 5},
        ]}
        risks.fill_risks(bp)
        model = prd.derive(bp, ["D1-A01"])
        self.assertNotIn("R-OTHER", [r["id"] for r in model["risks"]])
        self.assertNotIn("R-UNSCOPED", [r["id"] for r in model["risks"]])
        self.assertIn("R-PLATFORM", [r["id"] for r in model["risks"]])

    def test_scaffold_status_matches_every_supported_model_verdict(self):
        for status in ("hypothesis", "draft", "agreed", "adjusted", "rejected"):
            with self.subTest(status=status):
                bp = mini()
                bp["prd"] = {"status": status}
                model = prd.fill_prd(bp)
                text = scaffold.build_prd(bp, prd.mvp_agents(bp), [bp["domains"][0]], "Hub", "2026-11-12")
                row = next(line for line in text.splitlines() if line.startswith("| Status |"))
                self.assertIn(model["status"], row.lower())
                if status in ("hypothesis", "adjusted", "rejected"):
                    self.assertNotIn("draft", row.lower())


class ScaffoldScopeBoundary(unittest.TestCase):
    build_saved = DisclosureRoundTrips.build_saved
    DEPENDENCY = "P1DEFAULTDEPENDENCY94"
    RISK = "P1DEFAULTRISK95"

    def fixture(self):
        bp = sample()
        uc = next(u for d in bp["domains"] for u in d.get("use_cases", []) if u["id"] == "UC05")
        uc.pop("agents", None)
        self.assertTrue(uc["mvp"])
        uc["dependencies"].append(self.DEPENDENCY)
        bp["risks"]["items"].append({"id": "R-DEFAULT-SCOPE", "title": self.RISK, "likelihood": 5, "impact": 5})
        return bp

    def test_direct_default_scaffold_matches_default_page_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            bp = self.build_saved(self.fixture(), Path(tmp), "bp")
            self.assertIn(self.DEPENDENCY, bp["prd"]["dependencies"])
            self.assertIn(self.RISK, [r["title"] for r in bp["prd"]["risks"]])
            agents = prd.mvp_agents(bp)
            doms = list({d["id"]: d for _, d in agents}.values())
            text = scaffold.build_prd(bp, agents, doms, "Hub", "2026-11-12", scope_ids=None)
            for marker in (self.DEPENDENCY, self.RISK):
                self.assertTrue(marker in text, f"default scaffold omitted {marker}")

    def test_direct_scope_parameter_distinguishes_explicit_and_empty(self):
        bp = self.fixture()
        risks.fill_risks(bp)
        agents = prd.mvp_agents(bp)
        doms = list({d["id"]: d for _, d in agents}.values())
        for ids in (["D2-A01", "D3-A05"], ["D3-A05"], []):
            with self.subTest(ids=ids):
                text = scaffold.build_prd(bp, agents, doms, "Hub", "2026-11-12", scope_ids=ids)
                self.assertFalse(self.DEPENDENCY in text)
                self.assertFalse(self.RISK in text)
                expected = prd.derive(bp, ids)
                for agent in expected["agents"]:
                    for req in agent["requirements"]:
                        self.assertIn(req["id"], text)

    def test_direct_existing_selected_agent_api_remains_compatible(self):
        bp = self.fixture()
        risks.fill_risks(bp)
        agents = prd.mvp_agents(bp, ["D3-A05"])
        text = scaffold.build_prd(bp, agents, [agents[0][1]], "Hub", "2026-11-12")
        self.assertFalse(self.DEPENDENCY in text)
        self.assertFalse(self.RISK in text)
        for req in prd.derive(bp, ["D3-A05"])["agents"][0]["requirements"]:
            self.assertIn(req["id"], text)

    def test_cli_preserves_omitted_explicit_subset_and_empty_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            bp = self.build_saved(self.fixture(), folder, "bp")
            full = prd.derive(bp)
            for name, ids in (("omitted", None), ("explicit", ["D2-A01", "D3-A05"]),
                              ("subset", ["D3-A05"]), ("empty", [])):
                with self.subTest(mode=name):
                    out = folder / name
                    args = ["--blueprint", str(folder / "bp.json"), "--out-dir", str(out)]
                    if ids is not None:
                        args += ["--mvp", *ids]
                    capture = io.StringIO()
                    with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(io.StringIO()):
                        code = scaffold.main(args)
                    if ids == []:
                        self.assertEqual(code, 1, "an explicit empty scope must not become default MVP")
                        self.assertFalse(out.exists())
                        continue
                    self.assertEqual(code, 0)
                    summary = json.loads(capture.getvalue())
                    self.assertEqual(summary["mvp_agents"], full["mvp_agents"] if ids is None else ids)
                    text = (out / "prd.md").read_text(encoding="utf-8")
                    for marker in (self.DEPENDENCY, self.RISK):
                        self.assertEqual(marker in text, ids is None, f"{name}: wrong scope for {marker}")
                    expected = prd.derive(bp, ids)
                    for agent in expected["agents"]:
                        canonical = next(a for a in full["agents"] if a["agent"] == agent["agent"])
                        self.assertEqual(agent["requirements"], canonical["requirements"])
                        for req in agent["requirements"]:
                            self.assertIn(req["id"], text)


if __name__ == "__main__":
    unittest.main()
