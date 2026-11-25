# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""The raw validator is portable, shared verbatim, and enforced behaviourally."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tests.unit._util import ROOT, load
from tests.unit.test_release_evidence import changed_compressed_payload, forged_zip_size, tiny_zip


class SharedZip(unittest.TestCase):
    def module(self):
        path = ROOT / "tools/zip_stream.py"
        self.assertTrue(path.is_file(), "The pure raw-stream validator must exist")
        return load("tools/zip_stream.py")

    def test_identical_packaged_copy(self):
        self.module()
        self.assertEqual((ROOT / "tools/zip_stream.py").read_bytes(),
                         (ROOT / "plugin/skills/frontier-agent-factory/scripts/zip_stream.py").read_bytes())

    def test_real_streams_and_raw_forgery(self):
        module = self.module()
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raw = tiny_zip(data=b"A" * 100000, compression=method)
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                entry = archive.infolist()[0]
                self.assertEqual(module.raw_member(raw, entry, 100000), 100000)
                with self.assertRaisesRegex(ValueError, "exceeds allowed size"):
                    module.raw_member(raw, entry, 99999)
            forged = forged_zip_size(raw)
            with zipfile.ZipFile(io.BytesIO(forged)) as archive:
                with self.assertRaisesRegex(ValueError, "exceeds allowed size"):
                    module.raw_member(forged, archive.infolist()[0], 100000)

    def test_eof_crc_headers_and_unsupported_compression(self):
        module = self.module()
        raw = tiny_zip(data=b"A" * 1000, compression=zipfile.ZIP_DEFLATED)
        for change in (lambda p: p[:-1], lambda p: p + b"extra", lambda p: p + p):
            bad = changed_compressed_payload(raw, change)
            with zipfile.ZipFile(io.BytesIO(bad)) as archive:
                with self.assertRaisesRegex(ValueError, "DEFLATE stream"):
                    module.raw_member(bad, archive.infolist()[0], 1000)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entry = archive.infolist()[0]
            for offset in (-1, len(raw) - 20):
                entry.header_offset = offset
                with self.assertRaisesRegex(ValueError, "local header offset"):
                    module.raw_member(raw, entry, 1000)
        raw = tiny_zip(data=b"AA")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entry = archive.infolist()[0]
            damaged = bytearray(raw)
            damaged[30 + len(entry.filename)] ^= 1
            with self.assertRaisesRegex(ValueError, "CRC mismatch"):
                module.raw_member(bytes(damaged), entry, 1000)
        for method in (zipfile.ZIP_LZMA, zipfile.ZIP_BZIP2):
            raw = tiny_zip(compression=method)
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                with self.assertRaisesRegex(ValueError, "Unsupported ZIP compression"):
                    module.raw_member(raw, archive.infolist()[0], 1000)

    def test_release_wrapper_keeps_error_type_and_messages(self):
        from tools import release_evidence as evidence
        raw = forged_zip_size(tiny_zip(data=b"AA"))
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            with self.assertRaisesRegex(evidence.EvidenceError, "exceeds allowed size"):
                evidence._zip_member(raw, archive.infolist()[0], 1024)

    def test_release_package_import_without_test_path_setup(self):
        result = subprocess.run(
            [sys.executable, "-c", "from tools import release_evidence; "
             "assert callable(release_evidence._zip_member)"],
            cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_pure_copy_runs_without_repository_imports(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "zip_stream.py").write_bytes(Path(module.__file__).read_bytes())
            (root / "input.zip").write_bytes(tiny_zip(data=b"AA", compression=zipfile.ZIP_DEFLATED))
            result = subprocess.run(
                [sys.executable, "-I", "-c",
                 "import importlib.util, io, pathlib, sys, zipfile; "
                 "root=pathlib.Path(sys.argv[1]); "
                 "spec=importlib.util.spec_from_file_location('standalone', root/'zip_stream.py'); "
                 "m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); "
                 "raw=(root/'input.zip').read_bytes(); "
                 "z=zipfile.ZipFile(io.BytesIO(raw)); "
                 "assert m.raw_member(raw,z.infolist()[0],2)==2", str(root)],
                cwd=root, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_actual_size_below_declaration_is_not_a_valid_stream(self):
        module = self.module()
        raw = forged_zip_size(tiny_zip(data=b"AA"), size=3)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            with self.assertRaisesRegex(ValueError, "actual decoded size differs"):
                module.raw_member(raw, archive.infolist()[0], 1024)

    def test_checker_detects_copy_drift_in_owned_fixture(self):
        checker = load("tools/check_repo.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "plugin"
            skills = plugin / "skills"
            names = ("frontier-finops", "frontier-value-case", "frontier-agent-factory")
            for name in names:
                folder = skills / name
                (folder / "scripts").mkdir(parents=True)
                preview = name == "frontier-finops"
                (folder / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: Synthetic checker fixture\nmetadata:\n"
                    f"  maturity: {'preview' if preview else 'ga'}\n  optional: true\n"
                    f"  requires_preview_ack: {str(preview).lower()}\n---\n", encoding="utf-8")
            for name in names[:2]:
                (skills / name / "scripts/fv_expr.py").write_bytes(b"# same\n")
            (plugin / "package").mkdir()
            (plugin / "package/manifest.json").write_text(json.dumps({
                "agentSkills": [{"folder": "skills/" + name} for name in names]
            }), encoding="utf-8")
            (root / "tools").mkdir()
            (root / "tools/zip_stream.py").write_bytes(b"# shared\n")
            installed = skills / names[-1] / "scripts/zip_stream.py"
            installed.write_bytes(b"# shared\n")
            with patch.multiple(checker, ROOT=root, PLUGIN=plugin, SKILLS=skills):
                clean = checker.Report()
                checker.check_skills(clean)
                self.assertEqual(clean.errors, [])
                installed.write_bytes(b"# changed\n")
                drift = checker.Report()
                checker.check_skills(drift)
                self.assertEqual(drift.errors, [
                    "[skills] zip_stream.py differs between tools and frontier-agent-factory"])
                installed.write_bytes(b"# shared\n")
                restored = checker.Report()
                checker.check_skills(restored)
                self.assertEqual(restored.errors, [])
