"""Selective intake version and received-source provenance."""
from __future__ import annotations

import hashlib
import json
import unittest

from tests.unit._util import ROOT


class Handover17(unittest.TestCase):
    def test_package_descriptions_advertise_the_integrated_features(self):
        plugin = json.loads((ROOT / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "plugin/package/manifest.json").read_text(encoding="utf-8"))
        for description in (plugin["description"], manifest["description"]["full"]):
            for term in ("four parts", "prd", "plan", "risks"):
                with self.subTest(term=term):
                    self.assertTrue(term in description.casefold(), f"package description missing {term}")

    def test_integrated_version_is_distinct_from_received_release(self):
        plugin = json.loads((ROOT / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], "1.7.1")

    def test_received_inventory_fingerprint_is_preserved(self):
        path = ROOT / "docs/intake/source-inventory-1.7.0.json"
        self.assertTrue(path.is_file(), "received 1.7.0 inventory missing")
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(record["version"], "1.7.0")
        self.assertEqual(len(record["files"]), 262)
        digest = hashlib.sha256(json.dumps(record["files"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, "1d9063faa40222d5aacb2e1d3172ef6b953057831090ede8d6eaf4bb20ad7f48")
