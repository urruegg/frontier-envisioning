"""Digital feedback loop (Overview): canon derivation from the journeys, build checks, workshop merge."""
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
canon = load(f"{SKILL}/scripts/canon.py", "fl_canon")
build = load(f"{SKILL}/scripts/build_blueprint.py", "fl_build")
merge = load(f"{SKILL}/scripts/merge_feedback.py", "fl_merge")
DEFAULTS = json.loads((ROOT / SKILL / "templates/blueprint-defaults.json").read_text(encoding="utf-8"))
OFFICIAL = {"work", "fabric", "foundry", "web"}


def journeys():
    return [
        {"id": "D1", "name": "Sales", "journey_name": "Lead-to-Order", "systems": ["Dynamics 365 Sales", "Public web (company news)"],
         "orchestrator": {"id": "D1-LEAD", "name": "Sales Lead Agent"},
         "agents": [{"id": "D1-A01", "name": "Quote Agent", "capability": "Drafts quotes", "mvp": True}],
         "approval_seam": "The sales manager signs every price", "kpis": [{"kpi": "Quote cycle time", "definition": "Days to a sent quote"}],
         "use_cases": [{"id": "UC01", "name": "Quote drafting", "mvp": True}]},
        {"id": "D2", "name": "People", "journey_name": "Hire-to-Retire", "systems": ["Workday", "SharePoint: HR policies", "Teams"]},
        {"id": "D3", "name": "Procurement", "journey_name": "Source-to-Pay", "systems": ["SAP S/4HANA"]},
        {"id": "D4", "name": "Product engineering", "journey_name": "Idea-to-Launch", "systems": ["IoT telemetry"]},
    ]


def run_build(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = build.main(argv)
    return code, out.getvalue()


class Canon(unittest.TestCase):
    def test_journeys_map_to_the_four_areas_with_their_systems_agents_and_kpis(self):
        bp = {"domains": journeys(), "approval_seam": "Nothing leaves without a person"}
        self.assertEqual(canon.add_canon(bp, DEFAULTS, parts=("feedback_loop",)), ["digital feedback loop"])
        fl = bp["feedback_loop"]
        q = {x["pillar"]: x for x in fl["quadrants"]}
        self.assertEqual(list(q), list(canon.PILLARS))
        self.assertEqual((q["engage_customers"]["journeys"], q["empower_employees"]["journeys"],
                          q["optimize_operations"]["journeys"], q["transform_products"]["journeys"]), (["D1"], ["D2"], ["D3"], ["D4"]))
        iq = {s["text"]: s["iq"] for x in q.values() for s in x["signals"]}
        self.assertEqual(iq["Dynamics 365 Sales (Sales)"], ["fabric"])
        self.assertEqual(iq["Public web (company news) (Sales)"], ["web"])
        self.assertEqual(iq["SharePoint: HR policies (People)"], ["foundry"])
        self.assertEqual(iq["Teams (People)"], ["work"])
        self.assertEqual(q["engage_customers"]["actions"], [{"text": "Drafts quotes", "agents": ["D1-A01"], "approval": "The sales manager signs every price"}])
        self.assertEqual(q["engage_customers"]["outcomes"][0]["kpi"], "Quote cycle time")
        self.assertEqual(q["engage_customers"]["use_cases"], ["UC01"])
        self.assertNotIn("pillar_rules", fl)
        self.assertNotIn("iq_rules", fl)
        self.assertTrue(all(i in OFFICIAL for x in q.values() for s in x["signals"] for i in s["iq"]))

    def test_existing_loop_is_kept_and_only_completed(self):
        bp = {"domains": journeys(), "feedback_loop": {"quadrants": [
            {"pillar": "engage_customers", "journeys": ["D1"], "signals": [{"text": "RFQs in Outlook", "iq": ["work"]}]}]}}
        self.assertEqual(canon.add_canon(bp, DEFAULTS, parts=("feedback_loop",)), [])
        self.assertEqual(canon.fill_feedback_loop(bp, DEFAULTS), 1)
        q = bp["feedback_loop"]["quadrants"][0]
        self.assertEqual(q["signals"], [{"text": "RFQs in Outlook", "iq": ["work"]}])
        self.assertEqual(q["actions"][0]["agents"], ["D1-A01"])
        self.assertEqual(q["outcomes"][0]["kpi"], "Quote cycle time")
        self.assertEqual(canon.fill_feedback_loop(bp, DEFAULTS), 0)

    def test_defaults_use_official_names_only(self):
        fl = DEFAULTS["feedback_loop"]
        self.assertEqual([x["name"] for x in fl["iq"]], ["Work IQ", "Fabric IQ", "Foundry IQ", "Web IQ"])
        self.assertEqual([x["pillar"] for x in fl["quadrants"]], ["engage_customers", "optimize_operations", "empower_employees", "transform_products"])
        self.assertTrue(all(s["url"].startswith("https://") for s in fl["sources"]))


class Build(unittest.TestCase):
    def test_unofficial_iq_names_unknown_areas_and_layers_are_reported(self):
        sample = json.loads((ROOT / SKILL / "examples/caldova-blueprint.json").read_text(encoding="utf-8"))
        bp = copy.deepcopy(sample)
        q = bp["feedback_loop"]["quadrants"]
        q[0]["signals"].append({"text": "Process IQ shows where cases wait", "iq": ["process"]})
        q.append({"pillar": "engage_partners", "title": "Not an area"})
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "bp.json"
            data.write_text(json.dumps(bp), encoding="utf-8")
            code, out = run_build(["--data", str(data), "--save-normalized", str(Path(tmp) / "n.json")])
            self.assertEqual(code, 0)
            self.assertIn("'Process IQ', which is not an official Microsoft IQ name", out)
            self.assertIn("unknown Microsoft IQ layer process", out)
            self.assertIn("area 'engage_partners' ignored", out)
            norm = json.loads((Path(tmp) / "n.json").read_text(encoding="utf-8"))
            self.assertEqual(len(norm["feedback_loop"]["quadrants"]), 4)

    def test_caldova_loop_builds_without_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out = run_build(["--data", str(ROOT / SKILL / "examples/caldova-blueprint.json"), "--out", str(Path(tmp) / "bp.html")])
            self.assertEqual(code, 0)
            self.assertNotIn("feedback_loop", "\n".join(line for line in out.splitlines() if line.startswith("WARN")))
            self.assertIn('"feedback_loop_areas": 4', out)


class Merge(unittest.TestCase):
    def test_workshop_verdict_updates_the_area(self):
        sample = ROOT / SKILL / "examples/caldova-blueprint.json"
        fb = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "exported": "2026-11-12T16:00:00Z",
              "validations": {"loop:empower_employees": {"status": "validated", "note": "Start with region West"},
                              "loop:engage_partners": {"status": "validated"}}}
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "fb.json"
            f.write_text(json.dumps(fb), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = merge.main(["--blueprint", str(sample), "--feedback", str(f), "--out", str(Path(tmp) / "bp2.json")])
            self.assertEqual(code, 0)
            summary = json.loads(out.getvalue())
            self.assertEqual(summary["loop_updated"], 1)
            self.assertIn("loop:engage_partners", summary["unknown"])
            merged = json.loads((Path(tmp) / "bp2.json").read_text(encoding="utf-8"))
            q = next(x for x in merged["feedback_loop"]["quadrants"] if x["pillar"] == "empower_employees")
            self.assertEqual(q["status"], "validated")
            self.assertEqual(q["workshop_notes"][0]["note"], "Start with region West")


class Template(unittest.TestCase):
    def test_animation_respects_reduced_motion_and_can_be_paused(self):
        tpl = (ROOT / SKILL / "templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
        for needle in ("prefers-reduced-motion", "pauseAnimations", "animateMotion", "function flSvg", "Human approval before every action"):
            self.assertIn(needle, tpl)


if __name__ == "__main__":
    unittest.main()
