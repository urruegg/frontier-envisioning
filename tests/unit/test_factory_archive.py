# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Offline raw archive boundaries and atomic publication, using actual bytes."""
import importlib
import io
import json
import os
from pathlib import Path
import stat
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import warnings
import zipfile

from tests.factory_fixture import AT, F, zip_bytes
from tests.unit._util import ROOT
from tests.unit.test_release_evidence import changed_compressed_payload, forged_zip_size, tiny_zip

sys.path.insert(0, str(F / "scripts"))
c = importlib.import_module("factory_common")
MIB = c.MIB


class ArchiveCase(unittest.TestCase):
    def setUp(self):
        self.assertTrue((F / "scripts/factory_archive.py").is_file(),
                        "The bounded archive implementation must exist")
        self.m = importlib.import_module("factory_archive")

    def refused(self, code, function, *args, **kwargs):
        with self.assertRaisesRegex(c.FactoryError, "^" + code + "$"):
            function(*args, **kwargs)


class NamesCapacity(ArchiveCase):
    def test_portable_names_and_forbidden_components(self):
        self.assertEqual(self.m.safe_name(r".github\workflows\test.yml"), ".github/workflows/test.yml")
        self.assertEqual(self.m.safe_name(".gitattributes"), ".gitattributes")
        for name in ("../a", "/a", "//host/a", r"\\host\a", "C:/a", "C:a", "a:b",
                     "CON.txt", "a/NUL", "a//b", "a/./b", "a/../b", "a.", "a ",
                     "a\x00b", "a\x1fb", "a\x85b", "", "a/"):
            with self.subTest(name=repr(name)):
                self.refused("FACTORY_PATH", self.m.safe_name, name)
        for component in (".git", ".factory-local", "node_modules", "__pycache__", ".venv", "venv",
                          ".pytest_cache", ".ruff_cache", ".azure", ".aws", ".ssh", ".env",
                          ".ds_store", "thumbs.db", "module.pyc", "module.pyo"):
            self.refused("FACTORY_STATE", self.m.safe_name, "a/" + component.upper() + "/b")

    def test_root_policy_is_canonical_not_substring_pruning(self):
        for name in ("docs/intake/records/README.md", "solutions/README.md",
                     "tests/fixtures/x/docs/intake/records/real/intake.json"):
            self.m.foundation_shape(name)
        for name in ("docs/intake/records", "solutions"):
            self.m.foundation_shape(name, directory=True)
            self.refused("FACTORY_TEMPLATE", self.m.foundation_shape, name)
        for name in ("Docs/Intake/Records/real/intake.json", r"DOCS\INTAKE\RECORDS\real\intake.json",
                     "Solutions/unit/README.md", "SOLUTIONS/unit", "docs/intake/records/real"):
            for directory in (False, True):
                self.refused("FACTORY_TEMPLATE", self.m.foundation_shape, name, directory=directory)

    def test_completed_file_map_modes_collisions_and_bytes(self):
        self.m.capacity({"a/b": (b"", 0o755), "c": (b"x", 0o644)})
        for names in (("a", "A"), ("a/b", r"a\b"), ("a", "a/b"), ("a/b", "a"),
                      ("A/b", "a/c")):
            self.refused("FACTORY_COLLISION", self.m.capacity,
                         dict.fromkeys(names, (b"", 0o644)))
        for value in ((b"x", 0o777), (b"x", stat.S_IFREG | 0o644), ("text", 0o644), (b"",)):
            self.refused("FACTORY_MODE", self.m.capacity, {"a": value})
        self.refused("FACTORY_LIMIT", self.m.capacity, {"a": (b"xx", 0o644)}, expanded=1)
        self.refused("FACTORY_LIMIT", self.m.capacity, {"a": (b"", 0o644)}, members=0)


def compatible_files():
    return {
        "LICENSE": (ROOT / "tests/fixtures/factory/LICENSE.template.MIT").read_bytes(),
        ".agents/skills/LICENSE.superpowers": b"Synthetic notice, not authentic vendored code\n",
        ".agents/superpowers.lock.json": b'{"synthetic":true}\n',
        "AGENTS.md": b"# Passive synthetic policy\n",
        ".github/workflows/test.yml": b"name: Passive synthetic workflow\n",
        ".gitattributes": b"* text=auto\n",
        "solutions/README.md": b"# Passive catalogue\n",
        "docs/intake/records/README.md": b"# Passive catalogue\n",
        "tests/fixtures/x/docs/intake/records/synthetic/intake.json": b"{}",
        "docs/intake/intake.schema.json": (F / "references/intake.schema.json").read_bytes(),
        "tools/intake.py": (ROOT / "tests/fixtures/factory/intake-reference.py.txt").read_bytes(),
    }


def member_zip(rows):
    """Custom metadata without production parsing or executing any member."""
    stream = io.BytesIO()
    with warnings.catch_warnings(), zipfile.ZipFile(stream, "w") as archive:
        warnings.simplefilter("ignore", UserWarning)
        for name, raw, mode in rows:
            info = zipfile.ZipInfo(name, (2026, 11, 25, 12, 0, 0))
            info.create_system = 3
            info.external_attr = mode << 16
            archive.writestr(info, raw)
    return stream.getvalue()


class Foundation(ArchiveCase):
    def setUp(self):
        super().setUp()
        self.assertTrue(callable(getattr(self.m, "foundation", None)),
                        "Foundation parsing must validate real raw streams and the pinned profile")
        self.files = compatible_files()
        self.profile = json.loads((F / "references/template-profile.json").read_bytes())

    def test_complete_compatible_bytes_modes_and_legal_directories(self):
        rows = [("docs/", b"", stat.S_IFDIR | 0o755),
                ("docs/intake/", b"", stat.S_IFDIR | 0o755),
                ("docs/intake/records/", b"", stat.S_IFDIR | 0o755),
                ("solutions/", b"", stat.S_IFDIR | 0o755)]
        rows += [(name, raw, stat.S_IFREG | (0o755 if name == "tools/intake.py" else 0o644))
                 for name, raw in self.files.items()]
        for sequence in (rows, list(reversed(rows))):
            result = self.m.foundation(member_zip(sequence), "", self.profile)
            self.assertEqual({name: raw for name, (raw, _) in result.items()}, self.files)
            self.assertEqual(result["tools/intake.py"][1], 0o755)
            self.assertEqual(result["LICENSE"][1], 0o644)

    def test_explicit_wrapper_and_no_blind_nested_search(self):
        rows = [("wrapper/", b"", stat.S_IFDIR | 0o755)]
        rows += [("wrapper/" + name, raw, stat.S_IFREG | 0o644) for name, raw in self.files.items()]
        raw = member_zip(rows)
        self.assertEqual(set(self.m.foundation(raw, "wrapper/", self.profile)), set(self.files))
        for prefix in ("other", "wrap", "wrapper/sub"):
            self.refused("FACTORY_TEMPLATE", self.m.foundation, raw, prefix, self.profile)
        self.refused("FACTORY_STATE", self.m.foundation,
                     zip_bytes({".git/" + n: v for n, v in self.files.items()}), ".git", self.profile)
        self.refused("FACTORY_PATH", self.m.foundation,
                     zip_bytes({"../" + n: v for n, v in self.files.items()}), "..", self.profile)

    def test_windows_member_separators_become_portable_output_names(self):
        rows = [("docs\\", b"", stat.S_IFDIR | 0o755)]
        rows += [(name.replace("/", "\\"), raw, stat.S_IFREG | 0o644)
                 for name, raw in self.files.items()]
        result = self.m.foundation(member_zip(rows), "", self.profile)
        self.assertEqual({name: raw for name, (raw, _) in result.items()}, self.files)

    def test_profile_required_and_fingerprints(self):
        for name in self.profile["required"]:
            files = dict(self.files)
            del files[name]
            self.refused("FACTORY_TEMPLATE", self.m.foundation, zip_bytes(files), "", self.profile)
        for name in ("tools/intake.py", "docs/intake/intake.schema.json"):
            files = dict(self.files)
            files[name] += b"\n"
            self.refused("FACTORY_COMPATIBILITY", self.m.foundation, zip_bytes(files), "", self.profile)

    def test_root_population_refused_but_passive_catalogues_and_test_data_preserved(self):
        for name in ("Docs/Intake/Records/real/intake.json", r"DOCS\INTAKE\RECORDS\real\intake.json",
                     "Solutions/real/unit.json"):
            files = dict(self.files)
            # Test the root policy itself, not an earlier casing collision with a catalogue.
            files.pop("docs/intake/records/README.md")
            files.pop("solutions/README.md")
            files[name] = b"{}"
            self.refused("FACTORY_TEMPLATE", self.m.foundation, zip_bytes(files), "", self.profile)
        for name in ("docs/intake/records/real/", "Solutions/real/"):
            self.refused("FACTORY_TEMPLATE", self.m.foundation,
                         member_zip([(name, b"", stat.S_IFDIR | 0o755)]), "", self.profile)

    def test_unsafe_full_paths_and_original_nul_name(self):
        for name in ("../a", "/a", "//host/a", r"\\host\a", "C:/a", "C:a", "a:b",
                     "CON.txt", "a.", "a ", "a//b", ".git/config", ".aws/config",
                     "node_modules/code.js", ".env", "a.pyc"):
            with self.subTest(name=name), self.assertRaises(c.FactoryError) as raised:
                self.m.foundation(tiny_zip(name), "", self.profile)
            self.assertRegex(str(raised.exception), "^FACTORY_(PATH|STATE)$")
        raw = tiny_zip("badXname").replace(b"badXname", b"bad\x00name")
        self.refused("FACTORY_ZIP", self.m.foundation, raw, "", self.profile)

    def test_file_directory_case_slash_and_ancestor_collisions_both_orders(self):
        pairs = [
            (("a", False), ("a", False)),
            (("a", False), ("A", False)),
            (("a/b", False), (r"a\b", False)),
            (("a", False), ("a/b", False)),
            (("a", False), ("a", True)),
            (("a", False), ("a/b", True)),
            (("A", True), ("a/b", False)),
            (("A/b", False), ("a/c", False)),
            (("a", True), ("a", True)),
        ]
        for pair in pairs:
            rows = [(n + ("/" if directory else ""), b"",
                     (stat.S_IFDIR if directory else stat.S_IFREG) | 0o755)
                    for n, directory in pair]
            for order in (rows, list(reversed(rows))):
                with self.subTest(pair=pair):
                    self.refused("FACTORY_COLLISION", self.m.foundation, member_zip(order), "", self.profile)

    def test_links_special_modes_directory_payload_and_submodules(self):
        for mode in (stat.S_IFLNK | 0o777, stat.S_IFIFO | 0o644, 0o160000, stat.S_IFSOCK | 0o644):
            self.refused("FACTORY_LINK", self.m.foundation,
                         member_zip([("x", b"target", mode)]), "", self.profile)
        for name, mode in (("x/", stat.S_IFREG | 0o644), ("x", stat.S_IFDIR | 0o755),
                           ("x", stat.S_IFREG | 0o777), ("x", stat.S_IFREG | 0o4644)):
            self.refused("FACTORY_MODE", self.m.foundation, member_zip([(name, b"", mode)]), "", self.profile)
        self.refused("FACTORY_ZIP", self.m.foundation,
                     member_zip([("x/", b"data", stat.S_IFDIR | 0o755)]), "", self.profile)
        self.refused("FACTORY_TEMPLATE", self.m.foundation,
                     tiny_zip(".gitmodules", b"[submodule \"passive\"]\n"), "", self.profile)

    def test_header_name_encryption_unsupported_and_overlap(self):
        original = tiny_zip("same.txt", b"AA")
        central = original.index(b"PK\x01\x02")
        bads = [b"", b"not a zip", original[:20], original.replace(b"PK\x03\x04", b"PK\x03XX", 1)]
        for offset in (8, 14, 18, 22):  # local method, CRC, compressed/expanded sizes
            bad = bytearray(original)
            bad[offset] ^= 1
            bads.append(bytes(bad))
        bad = bytearray(original)
        bad[30] ^= 1  # local name only
        bads.append(bytes(bad))
        bad = bytearray(original)
        for offset in (6, central + 8):
            struct.pack_into("<H", bad, offset, 1)
        bads.append(bytes(bad))
        bad = bytearray(original)
        struct.pack_into("<I", bad, central + 38, (stat.S_IFREG | 0o644) << 16 | 0x400)
        bads.append(bytes(bad))
        for method in (zipfile.ZIP_LZMA, zipfile.ZIP_BZIP2):
            bads.append(tiny_zip(compression=method))
        overlap = bytearray(zip_bytes({"one": b"x", "two": b"x"}))
        first = overlap.index(b"PK\x01\x02")
        second = overlap.index(b"PK\x01\x02", first + 4)
        struct.pack_into("<I", overlap, second + 42, 0)
        bads.append(bytes(overlap))
        for bad in bads:
            with self.subTest(size=len(bad)), self.assertRaises(c.FactoryError) as raised:
                self.m.foundation(bad, "", self.profile)
            self.assertRegex(str(raised.exception), "^FACTORY_(ZIP|LINK|LIMIT)$")

    def test_actual_raw_size_crc_eof_and_no_extra_compressed_bytes(self):
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raw = tiny_zip(data=b"A" * 10000, compression=method)
            self.refused("FACTORY_ZIP", self.m.foundation, forged_zip_size(raw), "", self.profile)
            self.refused("FACTORY_ZIP", self.m.foundation,
                         forged_zip_size(raw, size=10000, crc=1), "", self.profile)
        raw = tiny_zip(data=b"A" * 10000, compression=zipfile.ZIP_DEFLATED)
        for mutate in (lambda p: p[:-1], lambda p: p + b"extra", lambda p: p + p, lambda p: b"\xff" + p):
            self.refused("FACTORY_ZIP", self.m.foundation,
                         changed_compressed_payload(raw, mutate), "", self.profile)

    def test_real_exact_32_mib_compressed_and_one_over(self):
        self.files["padding.dat"] = b""
        size = 32 * MIB - len(zip_bytes(self.files))
        self.files["padding.dat"] = b"A" * size
        raw = zip_bytes(self.files)
        self.assertEqual(len(raw), 32 * MIB)
        result = self.m.foundation(raw, "", self.profile)
        self.assertEqual(result["padding.dat"][0], self.files["padding.dat"])
        del raw, result
        self.files["padding.dat"] += b"B"
        self.refused("FACTORY_LIMIT", self.m.foundation, zip_bytes(self.files), "", self.profile)

    def test_real_exact_64_mib_expanded_and_one_over(self):
        size = 64 * MIB - sum(map(len, self.files.values()))
        self.files["padding.dat"] = b"A" * size
        raw = zip_bytes(self.files, zipfile.ZIP_DEFLATED)
        result = self.m.foundation(raw, "", self.profile)
        self.assertEqual(sum(len(value[0]) for value in result.values()), 64 * MIB)
        del result
        self.files["padding.dat"] += b"B"
        self.refused("FACTORY_LIMIT", self.m.foundation,
                     zip_bytes(self.files, zipfile.ZIP_DEFLATED), "", self.profile)

    def test_real_4096_source_entries_including_directories_and_one_over(self):
        rows = [(name, raw, stat.S_IFREG | 0o644) for name, raw in self.files.items()]
        rows.append(("empty/", b"", stat.S_IFDIR | 0o755))
        rows += [(f"padding/{index}", b"", stat.S_IFREG | 0o644) for index in range(4096 - len(rows))]
        self.assertEqual(len(rows), 4096)
        self.assertEqual(len(self.m.foundation(member_zip(rows), "", self.profile)), 4095)
        rows.append(("one-over", b"", stat.S_IFREG | 0o644))
        self.refused("FACTORY_LIMIT", self.m.foundation, member_zip(rows), "", self.profile)


class FinalArchive(ArchiveCase):
    def setUp(self):
        super().setUp()
        self.assertTrue(callable(getattr(self.m, "archive_bytes", None)),
                        "A validated deterministic ZIP writer must exist")

    def test_exact_bytes_order_portable_utf8_modes_stored_and_utc_metadata(self):
        entries = {"z": (b"last", 0o644), r"a\ü.txt": (b"first", 0o755)}
        raw = self.m.archive_bytes(entries, "2026-11-25T13:00:00+01:00")
        self.assertEqual(raw, self.m.archive_bytes(dict(reversed(list(entries.items()))), AT))
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(archive.namelist(), ["a/ü.txt", "z"])
            for entry in archive.infolist():
                self.assertEqual(entry.create_system, 3)
                self.assertEqual(entry.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(entry.date_time, (2026, 11, 25, 12, 0, 0))
                self.assertEqual(entry.extra, b"")
                self.assertEqual(entry.comment, b"")
                self.assertEqual(entry.external_attr >> 16,
                                 stat.S_IFREG | (0o755 if entry.filename.startswith("a/") else 0o644))
            self.assertTrue(archive.infolist()[0].flag_bits & 0x800)
            self.assertEqual(archive.read("a/ü.txt"), b"first")

    def test_dates_are_checked_after_utc_conversion_including_offset_overflow(self):
        for value, expected in (("1979-12-31T23:00:00-01:00", (1980, 1, 1, 0, 0, 0)),
                                ("2108-01-01T00:00:00+01:00", (2107, 12, 31, 23, 0, 0))):
            with zipfile.ZipFile(io.BytesIO(self.m.archive_bytes({"a": (b"", 0o644)}, value))) as archive:
                self.assertEqual(archive.infolist()[0].date_time, expected)
        for value in ("1979-12-31T23:59:59Z", "2108-01-01T00:00:00Z",
                      "0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00", "bad"):
            self.refused("FACTORY_DATE", self.m.archive_bytes, {}, value)

    def test_writer_validates_completed_set_not_only_source(self):
        for names in (("GENERATED.json", "generated.json"), ("a", "a/b"), ("a/b", "a"),
                      ("a/b", r"a\b")):
            self.refused("FACTORY_COLLISION", self.m.archive_bytes,
                         dict.fromkeys(names, (b"", 0o644)), AT)
        self.refused("FACTORY_MODE", self.m.archive_bytes, {"a": (b"", 0o777)}, AT)
        self.refused("FACTORY_STATE", self.m.archive_bytes, {".git/config": (b"", 0o644)}, AT)

    def test_real_exact_128_mib_expanded_and_one_over(self):
        chunk = b"A" * MIB
        entries = {f"generated/{index}.dat": (chunk, 0o644) for index in range(128)}
        self.m.capacity(entries)
        raw = self.m.archive_bytes(entries, AT)
        self.assertGreater(len(raw), 128 * MIB)  # Expanded cap, not container bytes.
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(sum(entry.file_size for entry in archive.infolist()), 128 * MIB)
            self.assertEqual(archive.read("generated/127.dat"), chunk)
        del raw
        entries["generated/127.dat"] = (chunk + b"B", 0o644)
        self.refused("FACTORY_LIMIT", self.m.capacity, entries)
        self.refused("FACTORY_LIMIT", self.m.archive_bytes, entries, AT)

    def test_real_4096_completed_files_including_generated_and_one_over(self):
        entries = {f"foundation/{index}": (b"", 0o644) for index in range(4095)}
        entries["generated/intake.json"] = (b"{}", 0o644)
        self.m.capacity(entries)
        raw = self.m.archive_bytes(entries, AT)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(len(archive.infolist()), 4096)
            self.assertEqual(archive.read("generated/intake.json"), b"{}")
        entries["generated/export.json"] = (b"{}", 0o644)
        self.refused("FACTORY_LIMIT", self.m.capacity, entries)
        self.refused("FACTORY_LIMIT", self.m.archive_bytes, entries, AT)


class Publish(ArchiveCase):
    def setUp(self):
        super().setUp()
        self.assertTrue(callable(getattr(self.m, "publish", None)),
                        "Atomic same-directory publication must exist")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root / "output.zip"
        self.inputs = self.root / "original.txt"
        self.inputs.write_bytes(b"untouched synthetic input")

    def assert_preserved(self, old=True):
        self.assertEqual(self.inputs.read_bytes(), b"untouched synthetic input")
        self.assertEqual({p.name for p in self.root.iterdir()},
                         {"original.txt", "output.zip"} if old else {"original.txt"})
        if old:
            self.assertEqual(self.out.read_bytes(), b"old-good")

    def test_successful_absent_and_existing_file_publication(self):
        raw = self.m.archive_bytes({"a": (b"reviewed", 0o644)}, AT)
        self.m.publish(self.out, raw)
        self.assertEqual(self.out.read_bytes(), raw)
        self.m.publish(self.out, b"completed replacement bytes")
        self.assertEqual(self.out.read_bytes(), b"completed replacement bytes")
        self.assertEqual({p.name for p in self.root.iterdir()}, {"original.txt", "output.zip"})

    def test_failures_create_no_partial_file_and_preserve_good_output(self):
        real_temporary = self.m.tempfile.NamedTemporaryFile

        def partial_write(*args, **kwargs):
            stream = real_temporary(*args, **kwargs)
            write = stream.write

            def fail(raw):
                write(raw[:1])
                raise OSError("synthetic private diagnostic must not escape")

            stream.write = fail
            return stream

        def failed_flush(*args, **kwargs):
            stream = real_temporary(*args, **kwargs)
            stream.flush = lambda: (_ for _ in ()).throw(OSError("synthetic flush failure"))
            return stream

        def short_write(*args, **kwargs):
            stream = real_temporary(*args, **kwargs)
            write = stream.write
            stream.write = lambda raw: write(raw[:1])
            return stream

        for old in (False, True):
            for target, attribute, effect in (
                (self.m.tempfile, "NamedTemporaryFile", OSError("before write")),
                (self.m.tempfile, "NamedTemporaryFile", partial_write),
                (self.m.tempfile, "NamedTemporaryFile", short_write),
                (self.m.tempfile, "NamedTemporaryFile", failed_flush),
                (self.m.os, "fsync", OSError("fsync failure")),
                (self.m.os, "replace", OSError("replace failure")),
            ):
                if old:
                    self.out.write_bytes(b"old-good")
                with patch.object(target, attribute, side_effect=effect):
                    self.refused("FACTORY_IO", self.m.publish, self.out, b"new")
                self.assert_preserved(old)

    def test_temp_is_same_directory_fsynced_before_replace(self):
        real_replace = self.m.os.replace
        real_fsync = self.m.os.fsync
        events = []

        def synced(fd):
            real_fsync(fd)
            events.append("fsync")

        def replace(source, destination):
            self.assertEqual(Path(source).parent, self.root)
            self.assertEqual(Path(destination), self.out)
            self.assertEqual(Path(source).read_bytes(), b"new")
            self.assertEqual(events, ["fsync"])
            real_replace(source, destination)
            events.append("replace")

        with patch.object(self.m.os, "fsync", side_effect=synced), patch.object(
                self.m.os, "replace", side_effect=replace):
            self.m.publish(self.out, b"new")
        self.assertEqual(events, ["fsync", "replace"])

    def test_invalid_raw_and_unsafe_destinations_never_start_write(self):
        self.out.write_bytes(b"old-good")
        with patch.object(self.m.tempfile, "NamedTemporaryFile") as create:
            self.refused("FACTORY_ZIP", self.m.publish, self.out, "not bytes")
            self.refused("FACTORY_OUTPUT", self.m.publish, self.root, b"new")
            with self.assertRaises(c.FactoryError):
                self.m.publish(self.root / "missing" / "out.zip", b"new")
            create.assert_not_called()
        self.assert_preserved()

    def test_portable_reparse_attribute_refuses_ancestor_before_resolve(self):
        ancestor = self.root / "ancestor"
        ancestor.mkdir()
        original = Path.lstat

        def reparse(path, *args, **kwargs):
            info = original(path, *args, **kwargs)
            return SimpleNamespace(st_mode=info.st_mode, st_file_attributes=0x400) if path == ancestor else info

        with patch.object(Path, "lstat", reparse), patch.object(Path, "resolve",
                                                               side_effect=AssertionError("must not resolve link")):
            self.refused("FACTORY_LINK", self.m.publish, ancestor / "new.zip", b"new")
        self.assertEqual(list(ancestor.iterdir()), [])

    def test_native_symlink_existing_and_dangling_leaves_and_ancestor(self):
        link = self.root / "link"
        try:
            link.symlink_to(self.inputs)
        except OSError as error:
            if getattr(error, "winerror", None) == 1314:
                self.skipTest("Windows symlink privilege unavailable (1314); native junction tested separately")
            raise
        try:
            self.refused("FACTORY_LINK", self.m.publish, link, b"new")
            self.inputs.unlink()
            self.refused("FACTORY_LINK", self.m.publish, link, b"new")
        finally:
            link.unlink()
        self.inputs.write_bytes(b"untouched synthetic input")
        link.symlink_to(self.root, target_is_directory=True)
        try:
            self.refused("FACTORY_LINK", self.m.publish, link / "new.zip", b"new")
        finally:
            link.unlink()
        self.assert_preserved(False)

    @unittest.skipUnless(os.name == "nt", "Windows junction coverage")
    def test_native_windows_junction_leaf_and_output_ancestor(self):
        target = self.root / "target"
        target.mkdir()
        sentinel = target / "untouched"
        sentinel.write_bytes(b"keep")
        link = self.root / "junction"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, "Test-owned junction creation must succeed")
        try:
            self.refused("FACTORY_LINK", self.m.publish, link, b"new")
            self.refused("FACTORY_LINK", self.m.publish, link / "new.zip", b"new")
            self.assertEqual(list(target.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_bytes(), b"keep")
        finally:
            link.rmdir()  # Remove only the junction, never recurse into the target.
