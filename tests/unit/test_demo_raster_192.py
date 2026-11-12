"""Named 1.9.2 raster support preserves all existing provenance boundaries."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load
from tests.unit import test_demo_raster as fixture_module


class Candidate192Raster(unittest.TestCase):
    def test_candidate_record_is_pinned_without_changing_reviewed_inputs(self):
        module = load("tools/demo_raster.py")
        self.assertIn("1.9.2", module.PREVIEW_VERSIONS, "named 1.9.2 support is missing")
        self.assertNotIn("1.9.3", module.PREVIEW_VERSIONS)
        path = ROOT / module.CANDIDATE_INPUT_PROFILE
        data = path.read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertEqual(hashlib.sha256(data).hexdigest(), module.CANDIDATE_INPUT_PROFILE_SHA256)
        record = json.loads(data)
        previous = json.loads((ROOT / "tests/fixtures/caldova-raster-1.9.1-inputs.json").read_text())
        self.assertEqual(record["version"], "1.9.2")
        self.assertEqual(record["inputs"], previous["inputs"])
        self.assertEqual(record["base_profile_sha256"], previous["base_profile_sha256"])

    def test_candidate_replay_and_all_failure_boundaries(self):
        fixtures = fixture_module.RasterReplay()
        for change in ("none", "record", "input", "asset", "release", "future"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                module = fixtures.module()
                kit, profile, old = fixtures.current_fixture(root)
                record = json.loads(old.read_text())
                record["version"] = "1.9.2"
                current = root / "tests/fixtures/caldova-raster-1.9.2-inputs.json"
                current.write_text(json.dumps(record), encoding="utf-8")
                digest = hashlib.sha256(current.read_bytes()).hexdigest()
                if change == "record":
                    current.write_text("{}", encoding="utf-8")
                elif change == "input":
                    (kit / "catalog.html").write_bytes(b"unexpected change")
                elif change == "asset":
                    (profile / "assets/agents/sample/identity/card.png").write_bytes(b"tampered")
                elif change == "release":
                    fixtures.release_record(root, "1.9.2", "invalid")
                with fixtures.current_root(module, root, profile, old), mock.patch.multiple(
                    module, create=True, CANDIDATE_INPUT_PROFILE=current.relative_to(root).as_posix(),
                    CANDIDATE_INPUT_PROFILE_SHA256=digest,
                ):
                    if change == "none":
                        report = module.replay(kit, profile, version="1.9.2")
                        self.assertTrue(report["preview"])
                        self.assertEqual(report["reference_version"], "1.6.0")
                        self.assertEqual(report["current_input_profile"]["version"], "1.9.2")
                        final = root / "identity.zip"
                        final.write_bytes(b"candidate")
                        module.verify_release_identity(final, report)
                    else:
                        with self.assertRaises(module.RasterProfileError):
                            module.replay(kit, profile, version="1.9.3" if change == "future" else "1.9.2")
                        self.assertFalse((kit / "agents/sample/identity/card.png").exists())
