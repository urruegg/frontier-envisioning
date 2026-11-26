# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Finite 1.11.0 replay preserves historical inputs, rasters and ZIP authority."""
import contextlib
import hashlib
import json

from tests.unit._util import ROOT, load
from tests.unit import test_demo_raster_1101 as patch_fixture


class Factory111Raster(patch_fixture.Patch1101Raster):
    @contextlib.contextmanager
    def factory_fixture(self):
        with self.fixture() as (module, fixtures, root, kit, profile, previous):
            record = json.loads(previous.read_bytes())
            record["version"] = "1.11.0"
            current = root / "tests/fixtures/caldova-raster-1.11.0-inputs.json"
            current.write_bytes((json.dumps(record, indent=2) + "\n").encode("utf-8"))
            module.FACTORY_INPUT_PROFILE = current.relative_to(root).as_posix()
            module.FACTORY_INPUT_PROFILE_SHA256 = hashlib.sha256(current.read_bytes()).hexdigest()
            yield module, fixtures, root, kit, profile, current

    def test_factory_only_named_profile_has_identical_pinned_inputs(self):
        module = load("tools/demo_raster.py")
        self.assertEqual(module.SUPPORTED_VERSIONS, {"1.4.0", "1.5.0", "1.6.0"})
        self.assertEqual(module.PREVIEW_VERSIONS,
                         {"1.6.1", "1.7.1", "1.9.1", "1.9.2", "1.10.0", "1.10.1", "1.11.0"})
        data = (ROOT / module.FACTORY_INPUT_PROFILE).read_bytes()
        previous = json.loads((ROOT / module.PATCH_INPUT_PROFILE).read_bytes())
        self.assertEqual(json.loads(data), dict(previous, version="1.11.0"))
        self.assertNotIn(b"\r", data)
        self.assertEqual(data, (json.dumps(json.loads(data), indent=2) + "\n").encode("utf-8"))
        self.assertEqual(hashlib.sha256(data).hexdigest(), module.FACTORY_INPUT_PROFILE_SHA256)
        base = json.loads((module.PROFILE / "manifest.json").read_bytes())
        self.assertEqual((len(base["inputs"]), len(base["assets"])), (205, 223))
        self.assertEqual(set(previous["inputs"]), {"catalog.html", "scripts/identity_docs.py"})

    def test_factory_replay_uses_named_profile_and_preserves_input_bytes(self):
        with self.factory_fixture() as (module, _, root, kit, profile, current):
            before = {p.relative_to(kit): p.read_bytes() for p in kit.rglob("*") if p.is_file()}
            try:
                report = module.replay(kit, profile, version="1.11.0")
            except module.RasterProfileError as exc:
                self.fail(f"named 1.11.0 replay rejected: {exc}")
            self.assertEqual(report["reference_version"], "1.6.0")
            self.assertTrue(report["preview"])
            self.assertIsNone(report["expected_release_identity_sha256"])
            self.assertEqual(report["current_input_profile"]["version"], "1.11.0")
            self.assertEqual(report["current_input_profile"]["sha256"],
                             hashlib.sha256(current.read_bytes()).hexdigest())
            self.assertEqual(report["verified_inputs"], 3)
            self.assertEqual(report["restored"], 2)
            for name, data in before.items():
                self.assertEqual((kit / name).read_bytes(), data)
            for name in ("agents/sample/identity/card.png", "visuals/second.png"):
                self.assertEqual((kit / name).read_bytes(), (profile / "assets" / name).read_bytes())
            final = root / "identity.zip"
            final.write_bytes(b"unreleased synthetic candidate")
            module.verify_release_identity(final, report)

    def test_factory_tampering_blocks_both_rasters_before_any_write(self):
        for change in ("recordbytes", "schema", "version", "baseprofilebytes",
                       "nonrasterinput", "asset", "extra-file"):
            with self.subTest(change=change), self.factory_fixture() as (module, _, _, kit, profile, current):
                self.assertIn("1.11.0", module.PREVIEW_VERSIONS, "named factory support missing")
                if change == "recordbytes":
                    current.write_bytes(current.read_bytes() + b"\n")
                elif change in ("schema", "version"):
                    record = json.loads(current.read_bytes())
                    record[change] = "unsupported"
                    current.write_bytes((json.dumps(record, indent=2) + "\n").encode("utf-8"))
                    module.FACTORY_INPUT_PROFILE_SHA256 = hashlib.sha256(current.read_bytes()).hexdigest()
                elif change == "baseprofilebytes":
                    manifest = profile / "manifest.json"
                    manifest.write_bytes(manifest.read_bytes() + b"\n")
                elif change == "nonrasterinput":
                    (kit / "catalog.html").write_bytes(b"unexpected change")
                elif change == "asset":
                    (profile / "assets/visuals/second.png").write_bytes(b"corrupt")
                elif change == "extra-file":
                    (kit / "unexpected.json").write_bytes(b"{}")
                reason = "inventory" if change == "extra-file" else "asset" if change == "asset" else "input"
                with self.assertRaisesRegex(module.RasterProfileError, reason):
                    module.replay(kit, profile, version="1.11.0")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())
                self.assertFalse((kit / "visuals/second.png").exists())

    def test_factory_present_release_controls_finished_zip_authority(self):
        with self.factory_fixture() as (module, fixtures, root, kit, profile, _):
            self.assertIn("1.11.0", module.PREVIEW_VERSIONS, "named factory support missing")
            final = root / "identity.zip"
            final.write_bytes(b"rebuilt synthetic identity")
            digest = hashlib.sha256(final.read_bytes()).hexdigest()
            fixtures.release_record(root, "1.11.0", digest)
            report = module.replay(kit, profile, version="1.11.0")
            self.assertFalse(report["preview"])
            self.assertEqual(report["reference_version"], "1.6.0")
            self.assertEqual(report["expected_release_identity_sha256"], digest)
            module.verify_release_identity(final, report)
            final.write_bytes(b"mutated synthetic identity")
            with self.assertRaisesRegex(module.RasterProfileError, "finished identity archive"):
                module.verify_release_identity(final, report)

    def test_factory_malformed_present_release_never_falls_back_to_preview(self):
        for record in ("{", "[]", "{}", '{"artefacts":[]}',
                       '{"artefacts":[{"name":"Caldova - agent identity package v1.0.zip","sha256":"bad"}]}'):
            with self.subTest(record=record), self.factory_fixture() as (module, fixtures, root, kit, profile, _):
                self.assertIn("1.11.0", module.PREVIEW_VERSIONS, "named factory support missing")
                release = fixtures.release_record(root, "1.11.0", "0" * 64)
                release.write_bytes(record.encode("utf-8"))
                with self.assertRaisesRegex(module.RasterProfileError, "release record"):
                    module.replay(kit, profile, version="1.11.0")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())
                self.assertFalse((kit / "visuals/second.png").exists())

    def test_factory_unnamed_versions_cannot_inherit_replay_or_archive_exemption(self):
        for version in ("1.11.1", "1.12.0"):
            with self.subTest(version=version), self.factory_fixture() as (module, _, root, kit, profile, _):
                with self.assertRaisesRegex(module.RasterProfileError, "not approved"):
                    module.replay(kit, profile, version=version)
                with self.assertRaisesRegex(module.RasterProfileError, "no authoritative release digest"):
                    module.verify_release_identity(root / "missing.zip", {"version": version, "preview": True})
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())
                self.assertFalse((kit / "visuals/second.png").exists())
