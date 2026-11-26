"""Finite 1.10.1 replay preserves measured inputs and historical raster authority."""
import contextlib
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load
from tests.unit import test_demo_raster as fixture_module


class Patch1101Raster(unittest.TestCase):
    @contextlib.contextmanager
    def fixture(self):
        fixtures = fixture_module.RasterReplay()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            module = fixtures.module()
            kit, profile, old = fixtures.current_fixture(root)
            # A corrupt later asset must block even the earlier valid PNG.
            second = profile / "assets/visuals/second.png"
            second.parent.mkdir(parents=True)
            second.write_bytes(b"\x89PNG\r\n\x1a\nsecond fixture")
            manifest = profile / "manifest.json"
            base = json.loads(manifest.read_bytes())
            base["assets"]["visuals/second.png"] = hashlib.sha256(second.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(base), encoding="utf-8")
            record = json.loads(old.read_text())
            record["version"] = "1.10.1"
            record["base_profile_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
            current = root / "tests/fixtures/caldova-raster-1.10.1-inputs.json"
            current.write_text(json.dumps(record), encoding="utf-8")
            with fixtures.current_root(module, root, profile, old), mock.patch.multiple(
                module, create=True, PATCH_INPUT_PROFILE=current.relative_to(root).as_posix(),
                PATCH_INPUT_PROFILE_SHA256=hashlib.sha256(current.read_bytes()).hexdigest(),
            ):
                yield module, fixtures, root, kit, profile, current

    def test_only_named_patch_is_added_with_identical_pinned_inputs(self):
        module = load("tools/demo_raster.py")
        self.assertEqual(module.SUPPORTED_VERSIONS, {"1.4.0", "1.5.0", "1.6.0"})
        self.assertEqual(module.PREVIEW_VERSIONS,
                         {"1.6.1", "1.7.1", "1.9.1", "1.9.2", "1.10.0", "1.10.1", "1.11.0"})
        data = (ROOT / module.PATCH_INPUT_PROFILE).read_bytes()
        self.assertNotIn(b"\r", data)
        self.assertEqual(hashlib.sha256(data).hexdigest(), module.PATCH_INPUT_PROFILE_SHA256)
        previous = json.loads((ROOT / module.BASELINE_INPUT_PROFILE).read_bytes())
        self.assertEqual(json.loads(data), dict(previous, version="1.10.1"))
        base = json.loads((ROOT / "tests/fixtures/caldova-raster-1.4.0/manifest.json").read_bytes())
        self.assertEqual(len(base["inputs"]), 205)
        self.assertEqual(len(base["assets"]), 223)
        self.assertEqual(set(previous["inputs"]), {"catalog.html", "scripts/identity_docs.py"})

    def test_named_replay_retains_old_rasters_and_all_generated_input_bytes(self):
        with self.fixture() as (module, _, root, kit, profile, current):
            before = {p.relative_to(kit): p.read_bytes() for p in kit.rglob("*") if p.is_file()}
            try:
                report = module.replay(kit, profile, version="1.10.1")
            except module.RasterProfileError as exc:
                self.fail(f"named 1.10.1 replay rejected: {exc}")
            self.assertTrue(report["preview"])
            self.assertEqual(report["reference_version"], "1.6.0")
            self.assertEqual(report["verified_inputs"], 3)
            self.assertEqual(report["restored"], 2)
            self.assertEqual(report["current_input_profile"]["version"], "1.10.1")
            self.assertEqual(report["current_input_profile"]["sha256"],
                             hashlib.sha256(current.read_bytes()).hexdigest())
            for name, data in before.items():
                self.assertEqual((kit / name).read_bytes(), data)
            self.assertEqual((kit / "agents/sample/identity/card.png").read_bytes(),
                             (profile / "assets/agents/sample/identity/card.png").read_bytes())
            self.assertIsNone(report["expected_release_identity_sha256"])
            final = root / "identity.zip"
            final.write_bytes(b"unreleased internal candidate")
            module.verify_release_identity(final, report)

    def test_tampering_blocks_replay_before_any_png_write(self):
        for change in ("record", "missing-record", "schema", "version", "base", "input",
                       "unrelated-input", "extra-input", "missing-input", "extra-png", "asset"):
            with self.subTest(change=change), self.fixture() as (module, _, _, kit, profile, current):
                self.assertIn("1.10.1", module.PREVIEW_VERSIONS, "named patch support missing")
                if change == "record":
                    current.write_text("{}", encoding="utf-8")
                elif change == "missing-record":
                    current.unlink()
                elif change in ("schema", "version"):
                    record = json.loads(current.read_bytes())
                    record[change] = "unsupported"
                    current.write_text(json.dumps(record), encoding="utf-8")
                    module.PATCH_INPUT_PROFILE_SHA256 = hashlib.sha256(current.read_bytes()).hexdigest()
                elif change == "base":
                    manifest = profile / "manifest.json"
                    manifest.write_bytes(manifest.read_bytes() + b"\n")
                elif change == "input":
                    (kit / "catalog.html").write_bytes(b"unexpected change")
                elif change == "unrelated-input":
                    (kit / "agents/sample/identity/card.svg").write_bytes(b"unexpected change")
                elif change == "extra-input":
                    (kit / "extra.json").write_bytes(b"{}")
                elif change == "missing-input":
                    (kit / "catalog.html").unlink()
                elif change == "extra-png":
                    (kit / "unexpected.png").write_bytes(b"unapproved")
                elif change == "asset":
                    (profile / "assets/visuals/second.png").write_bytes(b"tampered")
                reason = ("inventory" if change in ("extra-input", "missing-input", "extra-png") else
                          "asset" if change == "asset" else "input")
                with self.assertRaisesRegex(module.RasterProfileError, reason):
                    module.replay(kit, profile, version="1.10.1")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())
                self.assertFalse((kit / "visuals/second.png").exists())

    def test_malformed_present_release_never_falls_back_to_preview(self):
        for record in ("{", "[]", "{}", '{"artefacts":[]}',
                       '{"artefacts":[{"name":"Caldova - agent identity package v1.0.zip","sha256":"bad"}]}'):
            with self.subTest(record=record), self.fixture() as (module, fixtures, root, kit, profile, _):
                self.assertIn("1.10.1", module.PREVIEW_VERSIONS, "named patch support missing")
                release = fixtures.release_record(root, "1.10.1", "0" * 64)
                release.write_text(record, encoding="utf-8")
                with self.assertRaisesRegex(module.RasterProfileError, "release record"):
                    module.replay(kit, profile, version="1.10.1")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_present_release_is_authority_and_detects_finished_zip_tampering(self):
        with self.fixture() as (module, fixtures, root, kit, profile, _):
            self.assertIn("1.10.1", module.PREVIEW_VERSIONS, "named patch support missing")
            final = root / "identity.zip"
            final.write_bytes(b"rebuilt identity")
            digest = hashlib.sha256(final.read_bytes()).hexdigest()
            fixtures.release_record(root, "1.10.1", digest)
            report = module.replay(kit, profile, version="1.10.1")
            self.assertFalse(report["preview"])
            self.assertEqual(report["expected_release_identity_sha256"], digest)
            module.verify_release_identity(final, report)
            final.write_bytes(b"wrong archive")
            with self.assertRaisesRegex(module.RasterProfileError, "finished identity archive"):
                module.verify_release_identity(final, report)

    def test_unnamed_versions_cannot_inherit_replay_or_skip_archive_authority(self):
        for version in ("1.10.2", "1.11.1", "1.9.3"):
            with self.subTest(version=version), self.fixture() as (module, _, root, kit, profile, _):
                with self.assertRaisesRegex(module.RasterProfileError, "not approved"):
                    module.replay(kit, profile, version=version)
                with self.assertRaisesRegex(module.RasterProfileError, "no authoritative release digest"):
                    module.verify_release_identity(root / "missing.zip", {"version": version, "preview": True})
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())
