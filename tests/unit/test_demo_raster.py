"""Historical raster replay validates generated inputs and immutable asset bytes."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load


class RasterReplay(unittest.TestCase):
    def test_received_releases_reuse_only_the_verified_identity_profile(self):
        module = self.module()
        self.assertTrue(hasattr(module, "SUPPORTED_VERSIONS"), "explicit received-release compatibility is missing")
        self.assertEqual(module.SUPPORTED_VERSIONS, {"1.4.0", "1.5.0", "1.6.0"})

    def test_future_release_cannot_inherit_the_profile(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            kit, profile, _, _, _ = self.fixture(Path(tmp))
            with self.assertRaisesRegex(module.RasterProfileError, "not approved"):
                module.replay(kit, profile, version="1.7.0")

    def test_current_release_record_must_expect_the_original_identity(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit, profile, _, _, _ = self.fixture(root)
            record = root / "releases" / "1.6.0" / "manifest.json"
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({"artefacts": [{
                "name": "Caldova - agent identity package v1.0.zip", "sha256": "0" * 64,
            }]}), encoding="utf-8")
            with mock.patch.object(module, "ROOT", root):
                with self.assertRaisesRegex(module.RasterProfileError, "provenance"):
                    module.replay(kit, profile, version="1.6.0")
            self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def module(self):
        self.assertTrue((ROOT / "tools/demo_raster.py").is_file(), "historical raster replay is missing")
        return load("tools/demo_raster.py", "test_demo_raster")

    def fixture(self, root):
        kit, profile = root / "kit", root / "profile"
        svg = kit / "agents/sample/identity/card.svg"
        svg.parent.mkdir(parents=True)
        svg.write_bytes(b"<svg>Caldova</svg>\n")
        relative = "agents/sample/identity/card.png"
        asset = profile / "assets" / relative
        asset.parent.mkdir(parents=True)
        asset.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        manifest = {
            "schema": "frontier-demo-raster/1.0",
            "version": "1.4.0",
            "source_archive_sha256": "2026c84c5806e0b8c2003e837f15e635fb78f2fa79f247164c47c1a5b51a5400",
            "inputs": {"agents/sample/identity/card.svg": hashlib.sha256(svg.read_bytes()).hexdigest()},
            "assets": {relative: hashlib.sha256(asset.read_bytes()).hexdigest()},
            "readme_sha256": hashlib.sha256(b"README\n").hexdigest(),
        }
        (profile / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return kit, profile, svg, asset, manifest

    def test_replays_verified_assets_without_changing_generated_inputs(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            kit, profile, svg, asset, _ = self.fixture(Path(tmp))
            original = svg.read_bytes()
            report = module.replay(kit, profile)
            self.assertEqual((kit / "agents/sample/identity/card.png").read_bytes(), asset.read_bytes())
            self.assertEqual(svg.read_bytes(), original)
            self.assertEqual(report["restored"], 1)
            self.assertEqual(report["restored_visuals"], 1)
            self.assertEqual(report["converted"], 0)

    def test_changed_generated_input_blocks_replay(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            kit, profile, svg, _, _ = self.fixture(Path(tmp))
            svg.write_bytes(b"<svg>changed</svg>\n")
            with self.assertRaisesRegex(module.RasterProfileError, "input"):
                module.replay(kit, profile)
            self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_tampered_raster_blocks_replay(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            kit, profile, _, asset, _ = self.fixture(Path(tmp))
            asset.write_bytes(b"tampered")
            with self.assertRaisesRegex(module.RasterProfileError, "asset"):
                module.replay(kit, profile)
            self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_unexpected_generated_input_blocks_replay(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            kit, profile, _, _, _ = self.fixture(Path(tmp))
            (kit / "extra.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(module.RasterProfileError, "inventory"):
                module.replay(kit, profile)

    def test_profile_cannot_write_outside_the_kit(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as tmp:
            kit, profile, _, _, manifest = self.fixture(Path(tmp))
            manifest["assets"] = {"../escape.png": "0" * 64}
            (profile / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(module.RasterProfileError, "path"):
                module.replay(kit, profile)
            self.assertFalse((kit.parent / "escape.png").exists())


if __name__ == "__main__":
    unittest.main()
