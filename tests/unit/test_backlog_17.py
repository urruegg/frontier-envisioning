"""Seed planning milestones are independent from product release numbers."""
import json
import unittest

from tests.unit._util import ROOT, load


class NamedPlanningMilestones(unittest.TestCase):
    def test_seed_keys_are_named_and_all_issue_seeds_resolve(self):
        data = json.loads((ROOT / "backlog/backlog.json").read_text(encoding="utf-8"))
        keys = {item["key"] for item in data["milestones"]}
        self.assertEqual(keys, {"M0", "M1", "M2", "Later"})
        issues = load("tools/bootstrap_github.py").read_issues()
        self.assertTrue(all(not issue["milestone"] or issue["milestone"] in keys for issue in issues))
