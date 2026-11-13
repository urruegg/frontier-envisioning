"""Explicit integrated preview support preserves historical raster checks."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load
from tests.unit import test_demo_raster as fixture_module


class IntegratedRasterPreview(unittest.TestCase):
    def test_only_named_integrated_preview_is_added(self):
        module = load("tools/demo_raster.py")
        self.assertEqual(module.SUPPORTED_VERSIONS, {"1.4.0", "1.5.0", "1.6.0"})
        self.assertEqual(module.PREVIEW_VERSIONS, {"1.6.1", "1.7.1", "1.9.1", "1.9.2", "1.10.0"})

    def test_integrated_record_is_byte_pinned_and_retains_exact_a6_inputs(self):
        module = load("tools/demo_raster.py")
        self.assertTrue(hasattr(module, "INTEGRATED_INPUT_PROFILE"), "integrated profile missing")
        data = (ROOT / module.INTEGRATED_INPUT_PROFILE).read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertEqual(hashlib.sha256(data).hexdigest(), module.INTEGRATED_INPUT_PROFILE_SHA256)
        record = json.loads(data)
        previous = json.loads((ROOT / "tests/fixtures/caldova-raster-1.6.1-inputs.json").read_text())
        self.assertEqual(record["version"], "1.7.1")
        self.assertEqual(record["inputs"], previous["inputs"])
        self.assertEqual(record["base_profile_sha256"], previous["base_profile_sha256"])

    def test_integrated_replay_and_all_failure_boundaries(self):
        fixtures = fixture_module.RasterReplay()
        for change in ("none", "record", "input", "asset", "release", "future"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                module = fixtures.module()
                kit, profile, old = fixtures.current_fixture(root)
                record = json.loads(old.read_text())
                record["version"] = "1.7.1"
                current = root / "tests/fixtures/caldova-raster-1.7.1-inputs.json"
                current.write_text(json.dumps(record), encoding="utf-8")
                digest = hashlib.sha256(current.read_bytes()).hexdigest()
                if change == "record":
                    current.write_text("{}", encoding="utf-8")
                elif change == "input":
                    (kit / "catalog.html").write_bytes(b"wrong")
                elif change == "asset":
                    (profile / "assets/agents/sample/identity/card.png").write_bytes(b"wrong")
                elif change == "release":
                    fixtures.release_record(root, "1.7.1", "bad")
                with fixtures.current_root(module, root, profile, old), mock.patch.multiple(
                    module, create=True,
                    INTEGRATED_INPUT_PROFILE=current.relative_to(root).as_posix(),
                    INTEGRATED_INPUT_PROFILE_SHA256=digest,
                ):
                    if change == "none":
                        report = module.replay(kit, profile, version="1.7.1")
                        self.assertTrue(report["preview"])
                        self.assertEqual(report["reference_version"], "1.6.0")
                        self.assertEqual(report["current_input_profile"]["version"], "1.7.1")
                        final = root / "identity.zip"
                        final.write_bytes(b"integrated")
                        module.verify_release_identity(final, report)
                    else:
                        with self.assertRaises(module.RasterProfileError):
                            module.replay(kit, profile, version="1.8.0" if change == "future" else "1.7.1")
                        self.assertFalse((kit / "agents/sample/identity/card.png").exists())
