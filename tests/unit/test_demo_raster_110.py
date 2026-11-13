"""Named 1.10.0 replay retains measured A6 inputs and finite provenance guards."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load
from tests.unit import test_demo_raster as fixture_module


class Baseline110Raster(unittest.TestCase):
    def test_only_named_baseline_candidate_is_added(self):
        module = load("tools/demo_raster.py")
        self.assertEqual(module.SUPPORTED_VERSIONS, {"1.4.0", "1.5.0", "1.6.0"})
        self.assertEqual(module.PREVIEW_VERSIONS, {"1.6.1", "1.7.1", "1.9.1", "1.9.2", "1.10.0"})

    def test_measured_record_is_lf_pinned_and_preserves_192_a6_inputs(self):
        module = load("tools/demo_raster.py")
        self.assertIn("1.10.0", module.PREVIEW_VERSIONS, "named 1.10.0 support is missing")
        data = (ROOT / module.BASELINE_INPUT_PROFILE).read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertEqual(hashlib.sha256(data).hexdigest(), module.BASELINE_INPUT_PROFILE_SHA256)
        record = json.loads(data)
        previous = json.loads((ROOT / "tests/fixtures/caldova-raster-1.9.2-inputs.json").read_text())
        self.assertEqual(set(record), {"schema", "version", "base_profile_sha256", "inputs"})
        self.assertEqual(record["schema"], "frontier-demo-current-inputs/1.0")
        self.assertEqual(record["version"], "1.10.0")
        self.assertEqual(record["inputs"], previous["inputs"])
        self.assertEqual(record["base_profile_sha256"], previous["base_profile_sha256"])

    def test_named_replay_and_failure_boundaries(self):
        fixtures = fixture_module.RasterReplay()
        for change in ("none", "record", "missing-record", "version", "base", "input",
                       "unrelated-input", "extra-input", "missing-input", "asset", "release"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                module = fixtures.module()
                kit, profile, old = fixtures.current_fixture(root)
                record = json.loads(old.read_text())
                record["version"] = "1.10.0"
                current = root / "tests/fixtures/caldova-raster-1.10.0-inputs.json"
                current.write_text(json.dumps(record), encoding="utf-8")
                digest = hashlib.sha256(current.read_bytes()).hexdigest()
                if change == "record":
                    current.write_text("{}", encoding="utf-8")
                elif change == "missing-record":
                    current.unlink()
                elif change == "version":
                    record["version"] = "1.10.1"
                    current.write_text(json.dumps(record), encoding="utf-8")
                    digest = hashlib.sha256(current.read_bytes()).hexdigest()
                elif change == "input":
                    (kit / "catalog.html").write_bytes(b"unexpected change")
                elif change == "unrelated-input":
                    (kit / "agents/sample/identity/card.svg").write_bytes(b"unexpected change")
                elif change == "extra-input":
                    (kit / "extra.json").write_bytes(b"{}")
                elif change == "missing-input":
                    (kit / "catalog.html").unlink()
                elif change == "asset":
                    (profile / "assets/agents/sample/identity/card.png").write_bytes(b"tampered")
                elif change == "release":
                    fixtures.release_record(root, "1.10.0", "invalid")
                with fixtures.current_root(module, root, profile, old), mock.patch.multiple(
                    module, create=True, BASELINE_INPUT_PROFILE=current.relative_to(root).as_posix(),
                    BASELINE_INPUT_PROFILE_SHA256=digest,
                ):
                    if change == "base":
                        manifest = profile / "manifest.json"
                        manifest.write_bytes(manifest.read_bytes() + b"\n")
                    if change == "none":
                        report = module.replay(kit, profile, version="1.10.0")
                        self.assertTrue(report["preview"])
                        self.assertEqual(report["reference_version"], "1.6.0")
                        self.assertEqual(report["current_input_profile"]["version"], "1.10.0")
                        self.assertEqual(report["current_input_profile"]["sha256"], digest)
                        self.assertEqual(report["verified_inputs"], 3)
                        self.assertEqual(report["restored"], 1)
                        self.assertIsNone(report["expected_release_identity_sha256"])
                        final = root / "identity.zip"
                        final.write_bytes(b"unreleased internal candidate")
                        module.verify_release_identity(final, report)
                    else:
                        reason = ("inventory" if change in ("extra-input", "missing-input") else
                                  "release record" if change == "release" else
                                  "asset" if change == "asset" else
                                  "input")
                        with self.assertRaisesRegex(module.RasterProfileError, reason):
                            module.replay(kit, profile, version="1.10.0")
                        self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_110_release_record_remains_authority_for_finished_archive(self):
        fixtures = fixture_module.RasterReplay()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = fixtures.module()
            kit, profile, old = fixtures.current_fixture(root)
            record = json.loads(old.read_text())
            record["version"] = "1.10.0"
            current = root / "tests/fixtures/caldova-raster-1.10.0-inputs.json"
            current.write_text(json.dumps(record), encoding="utf-8")
            final = root / "identity.zip"
            final.write_bytes(b"rebuilt identity")
            expected = hashlib.sha256(final.read_bytes()).hexdigest()
            fixtures.release_record(root, "1.10.0", expected)
            with fixtures.current_root(module, root, profile, old), mock.patch.multiple(
                module, create=True, BASELINE_INPUT_PROFILE=current.relative_to(root).as_posix(),
                BASELINE_INPUT_PROFILE_SHA256=hashlib.sha256(current.read_bytes()).hexdigest(),
            ):
                report = module.replay(kit, profile, version="1.10.0")
                self.assertFalse(report["preview"])
                self.assertEqual(report["expected_release_identity_sha256"], expected)
                module.verify_release_identity(final, report)
                final.write_bytes(b"wrong archive")
                with self.assertRaisesRegex(module.RasterProfileError, "finished identity archive"):
                    module.verify_release_identity(final, report)

    def test_future_1101_and_unsupported_193_cannot_inherit_support(self):
        fixtures = fixture_module.RasterReplay()
        for version in ("1.10.1", "1.9.3"):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as directory:
                module = fixtures.module()
                kit, profile, _ = fixtures.current_fixture(Path(directory))
                with self.assertRaisesRegex(module.RasterProfileError, "not approved"):
                    module.replay(kit, profile, version=version)
                with self.assertRaisesRegex(module.RasterProfileError, "no authoritative release digest"):
                    module.verify_release_identity(Path(directory) / "missing.zip",
                                                   {"version": version, "preview": True})
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())
