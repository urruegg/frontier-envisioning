"""Only a reviewed explicit 1.9.1 profile can reuse the historical rasters."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load
from tests.unit import test_demo_raster as fixture_module


class ProcessRasterPreview(unittest.TestCase):
    def test_only_named_process_preview_is_added(self):
        module = load("tools/demo_raster.py")
        self.assertEqual(module.SUPPORTED_VERSIONS, {"1.4.0", "1.5.0", "1.6.0"})
        self.assertEqual(module.PREVIEW_VERSIONS, {"1.6.1", "1.7.1", "1.9.1", "1.9.2", "1.10.0", "1.10.1"})

    def test_process_profile_preserves_the_exact_reviewed_a6_inputs(self):
        module = load("tools/demo_raster.py")
        self.assertTrue(hasattr(module, "PROCESS_INPUT_PROFILE"), "1.9.1 profile missing")
        data = (ROOT / module.PROCESS_INPUT_PROFILE).read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertEqual(hashlib.sha256(data).hexdigest(), module.PROCESS_INPUT_PROFILE_SHA256)
        record = json.loads(data)
        previous = json.loads((ROOT / "tests/fixtures/caldova-raster-1.7.1-inputs.json").read_text())
        self.assertEqual(record["version"], "1.9.1")
        self.assertEqual(record["inputs"], previous["inputs"])
        self.assertEqual(record["base_profile_sha256"], previous["base_profile_sha256"])

    def test_process_replay_keeps_all_failure_boundaries(self):
        fixtures = fixture_module.RasterReplay()
        for change in ("none", "record", "input", "asset", "release", "future"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                module = fixtures.module()
                kit, profile, old = fixtures.current_fixture(root)
                record = json.loads(old.read_text())
                record["version"] = "1.9.1"
                current = root / "tests/fixtures/caldova-raster-1.9.1-inputs.json"
                current.write_text(json.dumps(record), encoding="utf-8")
                digest = hashlib.sha256(current.read_bytes()).hexdigest()
                if change == "record":
                    current.write_text("{}", encoding="utf-8")
                elif change == "input":
                    (kit / "catalog.html").write_bytes(b"unreviewed")
                elif change == "asset":
                    (profile / "assets/agents/sample/identity/card.png").write_bytes(b"tampered")
                elif change == "release":
                    fixtures.release_record(root, "1.9.1", "bad")
                with fixtures.current_root(module, root, profile, old), mock.patch.multiple(
                    module, PROCESS_INPUT_PROFILE=current.relative_to(root).as_posix(),
                    PROCESS_INPUT_PROFILE_SHA256=digest,
                ):
                    if change == "none":
                        report = module.replay(kit, profile, version="1.9.1")
                        self.assertEqual(report["reference_version"], "1.6.0")
                        self.assertTrue(report["preview"])
                        final = root / "identity.zip"
                        final.write_bytes(b"current identity")
                        module.verify_release_identity(final, report)
                    else:
                        with self.assertRaises(module.RasterProfileError):
                            module.replay(kit, profile, version="1.9.3" if change == "future" else "1.9.1")
                        self.assertFalse((kit / "agents/sample/identity/card.png").exists())
