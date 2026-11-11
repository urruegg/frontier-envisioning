"""Historical raster replay validates generated inputs and immutable asset bytes."""
from __future__ import annotations

import hashlib
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from tests.unit._util import ROOT, load


class RasterReplay(unittest.TestCase):
    def test_reviewed_current_input_record_uses_canonical_lf_bytes(self):
        data = (ROOT / "tests/fixtures/caldova-raster-1.6.1-inputs.json").read_bytes()
        self.assertNotIn(b"\r", data)

    def test_reviewed_current_input_record_pin_matches_canonical_checkout(self):
        module = self.module()
        data = (ROOT / "tests/fixtures/caldova-raster-1.6.1-inputs.json").read_bytes()
        self.assertEqual(module.CURRENT_INPUT_PROFILE_SHA256, hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest())

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

    def test_explicit_patch_preview_uses_base_rasters_and_reviewed_current_inputs(self):
        module = self.module()
        self.assertTrue(hasattr(module, "PREVIEW_VERSIONS"), "explicit patch-preview support is missing")
        self.assertEqual(module.PREVIEW_VERSIONS, {"1.6.1", "1.7.1", "1.9.1"})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit, profile, current = self.current_fixture(root)
            with self.current_root(module, root, profile, current):
                report = module.replay(kit, profile, version="1.6.1")
            self.assertEqual(report["reference_version"], "1.6.0")
            self.assertTrue(report["preview"])
            self.assertEqual(report["restored"], 1)
            self.assertIsNone(report["expected_release_identity_sha256"])
            self.assertEqual(report["current_input_profile"], {
                "version": "1.6.1", "path": "tests/fixtures/caldova-raster-1.6.1-inputs.json",
                "sha256": hashlib.sha256(current.read_bytes()).hexdigest(),
                "changed_paths": ["catalog.html", "scripts/identity_docs.py"],
            })

    def test_present_patch_release_is_authority_for_finished_archive_not_old_rasters(self):
        module = self.module()
        self.assertTrue(hasattr(module, "PREVIEW_VERSIONS"), "explicit patch-preview support is missing")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kit, profile, current = self.current_fixture(root)
            final = root / "finished.zip"
            final.write_bytes(b"rebuilt current identity")
            digest = hashlib.sha256(final.read_bytes()).hexdigest()
            self.release_record(root, "1.6.1", digest)
            with self.current_root(module, root, profile, current):
                report = module.replay(kit, profile, version="1.6.1")
                self.assertFalse(report["preview"])
                self.assertEqual(report["reference_version"], "1.6.0")
                self.assertEqual(report["expected_release_identity_sha256"], digest)
                self.assertTrue(hasattr(module, "verify_release_identity"), "finished archive verification is missing")
                module.verify_release_identity(final, report)
                final.write_bytes(b"wrong final archive")
                with self.assertRaisesRegex(module.RasterProfileError, "identity archive"):
                    module.verify_release_identity(final, report)

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

    def release_record(self, root, version, digest):
        record = root / "releases" / version / "manifest.json"
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(json.dumps({"date": "2026-11-10", "artefacts": [{
            "name": "Caldova - agent identity package v1.0.zip", "sha256": digest,
        }]}), encoding="utf-8")
        return record

    def current_fixture(self, root):
        kit, profile, _, _, manifest = self.fixture(root)
        self.release_record(root, "1.6.0", manifest["source_archive_sha256"])
        overrides = {}
        for name in ("catalog.html", "scripts/identity_docs.py"):
            target = kit / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"old input\n")
            manifest["inputs"][name] = hashlib.sha256(target.read_bytes()).hexdigest()
            target.write_bytes(b"reviewed current input\n")
            overrides[name] = hashlib.sha256(target.read_bytes()).hexdigest()
        (profile / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        current = root / "tests/fixtures/caldova-raster-1.6.1-inputs.json"
        current.parent.mkdir(parents=True)
        current.write_text(json.dumps({
            "schema": "frontier-demo-current-inputs/1.0", "version": "1.6.1",
            "base_profile_sha256": hashlib.sha256((profile / "manifest.json").read_bytes()).hexdigest(),
            "inputs": overrides,
        }), encoding="utf-8")
        return kit, profile, current

    @contextlib.contextmanager
    def current_root(self, module, root, profile, current):
        with mock.patch.multiple(module, ROOT=root, create=True,
                                 BASE_PROFILE_SHA256=hashlib.sha256((profile / "manifest.json").read_bytes()).hexdigest(),
                                 CURRENT_INPUT_PROFILE_SHA256=hashlib.sha256(current.read_bytes()).hexdigest()):
            yield

    def test_current_profile_is_required_and_byte_pinned(self):
        for change in ("missing", "tampered", "base"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                module = self.module()
                kit, profile, current = self.current_fixture(root)
                with self.current_root(module, root, profile, current):
                    if change == "missing":
                        current.unlink()
                    elif change == "tampered":
                        current.write_bytes(current.read_bytes() + b"\n")
                    else:
                        base = profile / "manifest.json"
                        base.write_bytes(base.read_bytes() + b"\n")
                    with self.assertRaisesRegex(module.RasterProfileError, "current input profile"):
                        module.replay(kit, profile, version="1.6.1")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_current_profile_strict_schema_version_base_paths_and_sha(self):
        for change in ("schema", "version", "base", "extra-key", "missing-input", "extra-input",
                       "invalid-path", "bad-sha", "unchanged-input", "malformed", "not-object"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                module = self.module()
                kit, profile, current = self.current_fixture(root)
                record = json.loads(current.read_text())
                if change in ("schema", "version"):
                    record[change] = "unsupported"
                elif change == "base":
                    record["base_profile_sha256"] = "0" * 64
                elif change == "extra-key":
                    record["extra"] = True
                elif change == "missing-input":
                    del record["inputs"]["catalog.html"]
                elif change == "extra-input":
                    record["inputs"]["other.py"] = "0" * 64
                elif change == "invalid-path":
                    record["inputs"]["../escape.py"] = record["inputs"].pop("scripts/identity_docs.py")
                elif change == "bad-sha":
                    record["inputs"]["catalog.html"] = "not-a-sha256"
                elif change == "unchanged-input":
                    record["inputs"]["catalog.html"] = json.loads((profile / "manifest.json").read_text())["inputs"]["catalog.html"]
                elif change == "not-object":
                    record = []
                current.write_text("{" if change == "malformed" else json.dumps(record), encoding="utf-8")
                with self.current_root(module, root, profile, current):
                    with self.assertRaisesRegex(module.RasterProfileError, "current input profile"):
                        module.replay(kit, profile, version="1.6.1")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_current_profile_preserves_all_other_input_and_raster_guards(self):
        for change in ("unrelated", "allowed-but-wrong", "extra", "missing", "png"):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                module = self.module()
                kit, profile, current = self.current_fixture(root)
                if change == "unrelated":
                    (kit / "agents/sample/identity/card.svg").write_bytes(b"changed")
                elif change == "allowed-but-wrong":
                    (kit / "catalog.html").write_bytes(b"unreviewed")
                elif change == "extra":
                    (kit / "extra.json").write_bytes(b"{}")
                elif change == "missing":
                    (kit / "catalog.html").unlink()
                else:
                    (profile / "assets/agents/sample/identity/card.png").write_bytes(b"tampered")
                with self.current_root(module, root, profile, current):
                    with self.assertRaises(module.RasterProfileError):
                        module.replay(kit, profile, version="1.6.1")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_present_malformed_current_release_never_falls_back_to_preview(self):
        for record in ("{", "[]", "{}", '{"artefacts":[]}', '{"artefacts":[{"name":"Caldova - agent identity package v1.0.zip","sha256":"bad"}]}'):
            with self.subTest(record=record), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                module = self.module()
                kit, profile, current = self.current_fixture(root)
                release = self.release_record(root, "1.6.1", "0" * 64)
                release.write_text(record, encoding="utf-8")
                with self.current_root(module, root, profile, current):
                    with self.assertRaisesRegex(module.RasterProfileError, "release record"):
                        module.replay(kit, profile, version="1.6.1")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())

    def test_only_explicit_unreleased_current_build_can_skip_final_archive_digest(self):
        module = self.module()
        self.assertTrue(hasattr(module, "verify_release_identity"), "finished archive verification is missing")
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "identity.zip"
            archive.write_bytes(b"current")
            report = {"version": "1.6.1", "preview": True, "expected_release_identity_sha256": None}
            module.verify_release_identity(archive, report)
            for change in ({"version": "1.6.0"}, {"version": "1.7.0"}, {"preview": False},
                           {"expected_release_identity_sha256": "bad"}):
                with self.subTest(change=change), self.assertRaises(module.RasterProfileError):
                    module.verify_release_identity(archive, dict(report, **change))

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


class FinishedDemoArchive(unittest.TestCase):
    def test_build_verifies_release_digest_after_rebuild_and_canonicalisation(self):
        build = load("tools/build_demo.py", "current_identity_build")
        maker = load("plugin/skills/frontier-agent-identity/scripts/make_kit.py", "current_identity_maker")
        for matches in (True, False):
            with self.subTest(matches=matches), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                out = root / "demo"
                expected_kit = root / "expected/kit"

                def populate(kit):
                    (kit / "config").mkdir(parents=True)
                    for name in ("agent-identity", "palette"):
                        (kit / f"config/{name}.json").write_bytes(b"{}\n")
                    (kit / "catalog.html").write_bytes(b"<html/>\n")
                    card = kit / "agents/sample/identity/card.svg"
                    card.parent.mkdir(parents=True)
                    card.write_bytes(b"<svg/>\n")

                populate(expected_kit)
                (expected_kit / "README.md").write_bytes(b"README\n")
                (expected_kit / "agents/sample/identity/card.png").write_bytes(b"PNG")
                expected_zip = root / "expected.zip"
                maker.zip_dir(expected_kit, expected_zip)
                build.canonicalise_outputs(root / "expected", expected_zip)
                digest = hashlib.sha256(expected_zip.read_bytes()).hexdigest() if matches else "0" * 64
                RasterReplay().release_record(root, "1.6.1", digest)

                def wrapper(cmd, **kwargs):
                    kit = out / "kit"
                    populate(kit)
                    archive = out / "identity.zip"
                    maker.zip_dir(kit, archive)
                    (out / build.DEMO_HTML_NAME).write_bytes(b"<html/>\n")
                    summary = {"identity": {
                        "kit": str(kit), "zip": str(archive), "catalogue": str(kit / "catalog.html"),
                        "tests": "passed", "validation": {"errors": []}, "without_identity": [],
                    }, "value_finops": {"finops": "fixture"}}
                    return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(summary), stderr="")

                def replay(kit, **kwargs):
                    (kit / "agents/sample/identity/card.png").write_bytes(b"PNG")
                    return {
                        "version": "1.6.1", "preview": False, "reference_version": "1.6.0",
                        "expected_release_identity_sha256": digest,
                        "method": "frozen-release-raster", "restored_visuals": 1,
                        "readme_sha256": hashlib.sha256(b"README\n").hexdigest(),
                    }

                fake_maker = SimpleNamespace(
                    zip_dir=maker.zip_dir,
                    load_kit_module=lambda scripts, name: SimpleNamespace(
                        by_journey=lambda *args: {}, readme_md=lambda *args: "README\n"),
                )
                with mock.patch.object(build, "ROOT", root), \
                        mock.patch.object(build, "plugin_version", return_value="1.6.1"), \
                        mock.patch.object(build.subprocess, "run", side_effect=wrapper), \
                        mock.patch.object(build, "build_at_release_date", return_value=0), \
                        mock.patch.object(build, "load_module", return_value=fake_maker), \
                        mock.patch.object(build.demo_raster, "replay", side_effect=replay), \
                        contextlib.redirect_stdout(io.StringIO()) as output:
                    code = build.main(["--out", str(out)])
                report = json.loads((out / "build-report.json").read_text())
                self.assertEqual(code, 0 if matches else 1)
                self.assertEqual(report["status"], "built" if matches else "incomplete")
                if matches:
                    self.assertEqual(hashlib.sha256((out / "identity.zip").read_bytes()).hexdigest(), digest)
                else:
                    self.assertIn("identity archive", output.getvalue())


if __name__ == "__main__":
    unittest.main()
