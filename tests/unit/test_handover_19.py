"""Received 1.9 provenance and the distinct integrated development version."""
import hashlib
import json
import unittest

from tests.unit._util import ROOT


class Handover19(unittest.TestCase):
    def test_integrated_version_is_distinct_from_received_release(self):
        plugin = json.loads((ROOT / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertNotEqual(plugin["version"], "1.9.0")
        manifest = json.loads((ROOT / "plugin/package/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], manifest["version"])

    def test_received_inventory_is_frozen(self):
        path = ROOT / "docs/intake/source-inventory-1.9.0.json"
        self.assertTrue(path.is_file(), "received 1.9 inventory missing")
        record = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(record["version"], "1.9.0")
        self.assertEqual(len(record["files"]), 279)
        digest = hashlib.sha256(json.dumps(record["files"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, "904538ec9930aad2d3aa5e8067023f4a7230d46a5696faef7836896b444a01e9")
