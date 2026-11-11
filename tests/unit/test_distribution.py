# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Distribution privacy and transparent intake-owner redaction."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load

packager = load("tools/build_package.py")


def zip_bytes(files: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    return stream.getvalue()


class DistributionPrivacy(unittest.TestCase):
    def errors(self, entries: list[tuple[bytes, str]]) -> list[str]:
        checker = getattr(packager, "distribution_errors", None)
        self.assertTrue(callable(checker), "distribution content guard is missing")
        return checker(entries)

    def test_enterprise_identity_and_encoded_variants_are_rejected_without_values(self):
        for text in ("@sample_microsoft", "@first_last_microsoft", "https://github.com/Sample_Microsoft/project",
                     "sample%5Fmicrosoft", "sample&#95;microsoft",
                     r'{"owner":"sample\u005fmicrosoft"}'):
            with self.subTest(text=text):
                errors = self.errors([(text.encode(), "README.md")])
                self.assertTrue(any("enterprise account" in error for error in errors))
                self.assertNotIn("sample", "\n".join(errors).lower())

    def test_personal_profile_paths_and_secret_files_are_rejected(self):
        for text in (r"C:\Users\person\source", r"C:\\Users\\person\\source", "/Users/person/source"):
            with self.subTest(text=text):
                self.assertTrue(any("profile path" in e for e in self.errors([(text.encode(), "README.md")])))
        self.assertTrue(self.errors([(b"not a real key", "skills/example/.env.local")]))
        self.assertTrue(self.errors([(b"guide", "sample_microsoft/README.md")]))

    def test_credentials_and_classified_documents_are_rejected(self):
        errors = self.errors([(("ghp_" + "x" * 36).encode(), "README.md")])
        self.assertTrue(any("GitHub token" in error for error in errors))
        for field in ("Classification", "Status"):
            for name in ("docs/private.md", "docs/private.txt"):
                with self.subTest(field=field, name=name):
                    self.assertTrue(any("classified" in e for e in self.errors([
                        (f"# Private\n| {field} | Microsoft internal |\n".encode(), name)
                    ])))

    def test_privacy_feature_labels_and_portable_examples_are_allowed(self):
        entries = [
            (b'print("Microsoft internal")', "skills/example/scripts/label.py"),
            (b"Use ${USERPROFILE} or a workspace-relative working directory.", "README.md"),
            (b"\x89PNG\r\n\x1a\n", "color.png"),
        ]
        self.assertEqual(self.errors(entries), [])

    def test_nested_archives_are_checked_and_malformed_archives_fail_explicitly(self):
        nested = zip_bytes({"README.md": b"@sample_microsoft"})
        errors = self.errors([(zip_bytes({"nested.zip": nested}), "kit.zip")])
        self.assertTrue(any("enterprise account" in error and "!" in error for error in errors))
        self.assertTrue(any("invalid ZIP" in e for e in self.errors([(b"not a zip", "kit.zip")])))

    def test_archive_and_member_comments_are_checked(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.comment = b"@sample_microsoft"
            entry = zipfile.ZipInfo("README.md")
            entry.comment = b"C:\\Users\\person\\source"
            archive.writestr(entry, b"guide")
        errors = self.errors([(stream.getvalue(), "kit.zip")])
        self.assertTrue(any("enterprise account" in error for error in errors))
        self.assertTrue(any("profile path" in error for error in errors))

    def test_root_secret_files_in_nested_archives_are_rejected(self):
        errors = self.errors([(zip_bytes({".env.local": b"private configuration"}), "kit.zip")])
        self.assertTrue(any("secret/key file" in error for error in errors))

    def test_plugin_rejects_private_content_before_writing_archive_or_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugin"
            shutil.copytree(ROOT / "plugin", plugin)
            spec = plugin / "install" / "plugin-install.json"
            before = spec.read_bytes()
            (plugin / "README.md").write_text("Owner @sample_microsoft\n", encoding="utf-8")
            output = io.StringIO()
            with mock.patch.object(packager, "PLUGIN", plugin), contextlib.redirect_stdout(output):
                self.assertEqual(packager.main(["--dist", str(root / "dist")]), 1)
            self.assertIn("enterprise account", output.getvalue())
            self.assertEqual(spec.read_bytes(), before)
            self.assertFalse((root / "dist").exists())

    def test_bundle_rejects_private_nested_package_before_overwriting_output(self):
        bundle = load("tools/build_release.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dist, demo, plugin = root / "dist", root / "demo", root / "plugin"
            files = {
                dist / "frontier-envisioning-plugin-1.6.1.zip": zip_bytes({"README.md": b"@sample_microsoft"}),
                demo / bundle.DEMO_HTML_NAME: b"demo",
                demo / "identity" / "caldova-agent-identity" / "catalog.html": b"catalogue",
                demo / "identity" / "kit.zip": zip_bytes({"README.md": b"identity"}),
                demo / "build-report.json": b'{"profile":"core","status":"built","variant":"full"}',
                **{demo / "ontology" / name: b"ontology output\n"
                   for name in ("ontology.ttl", "ontology.md", "data-agents.md", "data-products.md")},
                plugin / "README.md": b"guide", plugin / "MIT.md": b"licence",
                plugin / "THIRD-PARTY-NOTICES.md": b"notices",
                root / "CHANGELOG.md": b"history", root / "docs" / "prd.md": b"requirements",
                root / "docs" / "solution-design.md": b"design",
            }
            for path, data in files.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            output = dist / "frontier-envisioning-1.6.1-complete.zip"
            output.write_bytes(b"previous output")
            with mock.patch.object(bundle, "ROOT", root), mock.patch.object(bundle, "PLUGIN", plugin), \
                    mock.patch.object(bundle, "DEMO_DIR", demo), \
                    mock.patch.object(bundle, "plugin_version", return_value="1.6.1"), \
                    mock.patch.object(bundle, "load_module", return_value=packager), \
                    contextlib.redirect_stdout(io.StringIO()) as messages:
                self.assertEqual(bundle.main(["--dist", str(dist)]), 1)
            self.assertIn("enterprise account", messages.getvalue())
            self.assertEqual(output.read_bytes(), b"previous output")
            self.assertFalse((dist / "SHA256SUMS.txt").exists())

    def test_intake_owner_redaction_preserves_all_original_file_records(self):
        receipt = json.loads((ROOT / "docs" / "intake" / "source-inventory.json").read_text(encoding="utf-8"))
        self.assertTrue(receipt.get("repositoryRedacted"))
        self.assertIn("private Git history", receipt["redactionNote"])
        self.assertEqual(len(receipt["files"]), 249)
        digest = hashlib.sha256(json.dumps(receipt["files"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, "6ea788a8cf56423fcbec5a20eca1bf60f2ee077c9247fbe7dbd4138220f35845")
