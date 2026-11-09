"""Agent workflows (Agents > workflow): node and trigger types, derivation from the canvas plan, checks, build and design."""
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
wf = load(f"{SKILL}/scripts/workflow.py", "wf_workflow")
build = load(f"{SKILL}/scripts/build_blueprint.py", "wf_build")
scaffold = load("plugin/skills/frontier-solution-design/scripts/scaffold_design_docs.py", "wf_scaffold")
SAMPLE = ROOT / SKILL / "examples/caldova-blueprint.json"
DESIGNER = {"agent", "classify", "extract", "copilot", "human_review", "connector", "function", "variable", "if_else", "loop", "note"}


class Rep:
    def __init__(self):
        self.warnings = []

    def warn(self, msg):
        self.warnings.append(msg)


def agent(**canvas):
    return {"id": "D9-A01", "name": "Invoice Check Agent", "canvas": canvas}


def blueprint(*agents):
    return {"domains": [{"id": "D9", "name": "Finance", "orchestrator": {"id": "D9-LEAD", "name": "Finance Lead Agent"},
                         "agents": list(agents)}]}


def walk(steps):
    for s in steps:
        yield s
        yield from walk(s.get("steps") or [] if s.get("type") in ("loop", "scope") else [])
        for b in s.get("branches") or []:
            yield from walk(b.get("steps") or [])


class Types(unittest.TestCase):
    def test_designer_node_types_and_triggers(self):
        self.assertTrue(DESIGNER <= set(wf.NODE_TYPES), "every node of the designer's Add panel is a node type")
        self.assertEqual(set(wf.TRIGGERS), {"manual", "recurrence", "connector", "http", "agent"})
        self.assertEqual(wf.NODE_TYPES["human_review"][1], "human")
        self.assertEqual({wf.NODE_TYPES[k][1] for k in ("agent", "classify", "extract", "copilot")}, {"ai"})

    def test_aliases(self):
        for raw, want in [("If/Else", "if_else"), ("if", "if_else"), ("Human review", "human_review"), ("approval", "human_review"),
                          ("Request for information", "human_review"), ("for each", "loop"), ("Connector", "connector"),
                          ("respond to the agent", "respond"), ("magic", None), ("", None)]:
            self.assertEqual(wf.node_type(raw), want, raw)
        for raw, want in [("schedule", "recurrence"), ("webhook", "http"), ("event", "connector"), ("agent", "agent"), ("cron", None)]:
            self.assertEqual(wf.trigger_type(raw), want, raw)


class Rules(unittest.TestCase):
    def test_plan_sentences_become_designer_nodes(self):
        for text, want in [
            ("The finance manager approves the payment", "human_review"),
            ("Collect missing details from the requester", "human_review"),
            ("For each attachment of the email", "loop"),
            ("Classify the email: invoice, credit note or reminder", "classify"),
            ("Extract totals, VAT and the IBAN from the invoice", "extract"),
            ("Flag invoices outside the tolerance", "if_else"),
            ("Calculate the landed cost per line", "function"),
            ("Initialize the case variables", "variable"),
            ("Summarize the supplier news of the week", "copilot"),
            ("Post a message to the buyers channel", "connector"),
            ("Hand the confirmed report to the workflow for write-back", "connector"),
            ("Draft the cover letter in the customer's language", "agent"),
        ]:
            self.assertEqual(wf.classify_step(text), want, text)

    def test_trigger_rules(self):
        for text, want in [("Every morning at 7:00", "recurrence"), ("Employee asks in Teams", "agent"),
                           ("A webhook from the supplier portal", "http"), ("On demand from a button", "manual"),
                           ("A new invoice arrives in the shared mailbox", "connector")]:
            self.assertEqual(wf.classify_trigger(text), want, text)


class Derive(unittest.TestCase):
    def test_derived_workflow_is_a_marked_hypothesis(self):
        a = agent(trigger="A new invoice arrives in the shared mailbox",
                  plan=["Extract totals, VAT and the IBAN from the invoice",
                        "Classify the invoice: standard, credit note or reminder",
                        "Draft the posting proposal with the reasons",
                        "Create the record in SAP through a declared action"],
                  approval=["The accountant approves every posting"],
                  connectors=["SAP S/4HANA (declared action)", "Outlook shared mailbox"],
                  outcome="Invoices posted within a day")
        w = wf.derive_workflow(a)
        self.assertTrue(w["derived"])
        self.assertEqual(w["status"], "draft")
        self.assertEqual(w["trigger"]["type"], "connector")
        self.assertEqual([s["type"] for s in w["steps"]], ["extract", "classify", "agent", "human_review", "connector"])
        self.assertEqual(w["steps"][1]["defaults"], ["Standard", "Credit note", "Reminder"])
        self.assertEqual(w["steps"][2]["agent"], "D9-A01")
        self.assertEqual(w["steps"][3]["approver"], "The accountant approves every posting",
                         "the approval is inserted before the first write")
        self.assertEqual(w["outcome"], "Invoices posted within a day")
        self.assertEqual(w["name"], "Invoice Check workflow")

    def test_no_plan_no_workflow_and_if_else_defaults(self):
        self.assertIsNone(wf.derive_workflow(agent(trigger="Daily")))
        w = wf.derive_workflow(agent(plan=["Flag lines outside the tolerance"]))
        self.assertEqual(w["trigger"]["type"], "manual")
        self.assertEqual(w["steps"][0]["defaults"], ["Yes", "No"])


class Clean(unittest.TestCase):
    def test_authored_workflow_warnings_and_ids(self):
        rep = Rep()
        w = {"trigger": {"type": "cron", "label": "Nightly at 02:00"},
             "steps": [{"type": "magic", "label": "Do something"},
                       {"type": "Connector", "label": "Read", "branches": ["x"]},
                       {"type": "loop", "label": "For each line", "steps": [
                           {"type": "loop", "label": "For each cell", "steps": [{"type": "scope", "label": "Inner", "steps": ["Calculate the sum"]}]}]},
                       {"type": "If/Else", "label": "Above limit?", "branches": [{"label": "Above", "then": "later", "steps": ["Manager approves"]}, "Within"]},
                       {"type": "agent", "label": "Draft", "agent": "D9-A99"}]}
        out = wf.clean_workflow(copy.deepcopy(w), {"D9-A01"}, rep, "agent D9-A01")
        text = "\n".join(rep.warnings)
        for needle in ["trigger type 'cron' unknown", "node type 'magic' unknown", "branches on a Connector node are ignored",
                       "is drawn flat", "then must be continue or end", "unknown agent 'D9-A99'"]:
            self.assertIn(needle, text)
        self.assertEqual(out["trigger"]["type"], "recurrence", "an unknown trigger type falls back to the label")
        self.assertNotIn("branches", out["steps"][1])
        self.assertEqual(out["steps"][3]["type"], "if_else")
        self.assertEqual(out["steps"][3]["branches"][0]["then"], "continue")
        self.assertEqual([b["label"] for b in out["steps"][3]["branches"]], ["Above", "Within"])
        self.assertEqual(out["steps"][3]["branches"][0]["steps"][0]["type"], "human_review")
        ids = [s["id"] for s in walk(out["steps"])]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "n1")

    def test_invalid_shapes(self):
        rep = Rep()
        self.assertIsNone(wf.clean_workflow("not an object", set(), rep, "agent X"))
        out = wf.clean_workflow({"trigger": "Employee asks in Teams", "steps": []}, set(), rep, "agent X")
        self.assertEqual(out["trigger"]["type"], "agent")
        self.assertIn("workflow has no steps", "\n".join(rep.warnings))


class Fill(unittest.TestCase):
    def test_fill_keeps_authored_and_rederives_derived(self):
        authored = {"id": "D9-A02", "name": "Posting Agent", "canvas": {"plan": ["Calculate the totals"],
                    "workflow": {"name": "Authored", "trigger": {"type": "manual"}, "steps": [{"type": "agent", "label": "Post", "agent": "D9-A01"}]}}}
        stale = {"id": "D9-A03", "name": "Reminder Agent", "canvas": {"plan": ["Send the reminder to the supplier"],
                 "workflow": {"derived": True, "trigger": {"type": "manual"}, "steps": [{"type": "agent", "label": "Old step"}]}}}
        bp = blueprint(agent(plan=["Summarize the open invoices"]), authored, stale,
                       {"id": "D9-A04", "name": "No Plan Agent", "canvas": {"trigger": "Daily", "workflow": {"derived": True, "steps": []}}})
        rep = Rep()
        res = wf.fill_workflows(bp, rep)
        self.assertEqual((res["authored"], res["derived"]), (1, 2))
        a1, a2, a3, a4 = bp["domains"][0]["agents"]
        self.assertTrue(a1["canvas"]["workflow"]["derived"])
        self.assertEqual(a1["canvas"]["workflow"]["steps"][0]["type"], "copilot")
        self.assertEqual(a2["canvas"]["workflow"]["name"], "Authored")
        self.assertEqual(a2["canvas"]["workflow"]["steps"][0]["id"], "n1")
        self.assertEqual(a3["canvas"]["workflow"]["steps"][0]["label"], "Send the reminder to the supplier", "derived workflows follow the plan")
        self.assertNotIn("workflow", a4["canvas"], "no plan, no derived workflow")
        self.assertEqual(rep.warnings, [])


class SampleBuild(unittest.TestCase):
    def test_sample_workflows_build_and_scaffold(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = build.main(["--data", str(SAMPLE), "--out", str(t / "bp.html"), "--save-normalized", str(t / "bp.json"),
                                   "--report", str(t / "report.json")])
            self.assertEqual(code, 0)
            report = json.loads((t / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["stats"]["workflows"], 2)
            self.assertFalse([w for w in report.get("warnings", []) if "workflow" in w], "the sample workflows are clean")
            bp = json.loads((t / "bp.json").read_text(encoding="utf-8"))
            flows = {a["id"]: a["canvas"]["workflow"] for d in bp["domains"] for a in d.get("agents", [])
                     if isinstance(a.get("canvas"), dict) and a["canvas"].get("workflow")}
            self.assertEqual(set(flows), {"D2-A01", "D3-A05"})
            self.assertEqual(flows["D3-A05"]["trigger"]["type"], "connector")
            self.assertEqual(flows["D2-A01"]["trigger"]["type"], "agent")
            types = {s["type"] for w in flows.values() for s in walk(w["steps"])}
            self.assertTrue({"agent", "classify", "extract", "copilot", "human_review", "connector", "function", "variable",
                             "if_else", "loop", "respond"} <= types, "the sample shows every designer node type")
            self.assertTrue(all(s.get("id") for w in flows.values() for s in walk(w["steps"])))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(scaffold.main(["--blueprint", str(t / "bp.json"), "--out-dir", str(t / "design")]), 0)
            sd = (t / "design/solution-design.md").read_text(encoding="utf-8")
            self.assertIn("### Workflow: Service report from voice notes (Service Report Agent)", sd)
            self.assertIn("- Trigger: Connector event \u2014 When a work order is completed on site", sd)
            self.assertIn("| 3.1 | Connector | Transcribe the voice note |", sd)
            self.assertIn("| 7a.1 | Human review | Ask the technician once |", sd)
            self.assertIn("- Trigger: When an agent calls the workflow (", sd)


if __name__ == "__main__":
    unittest.main()
