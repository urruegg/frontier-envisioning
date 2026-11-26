# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Opt-in actual pinned receiver proof, separate from the offline producer."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest import mock
import zipfile

from tests.factory_fixture import COMMIT, approved, encode, prepare, save
from tests.unit.test_factory_package import build_candidate, check_inventory, export_command, isolated_env

MIB = 1024 * 1024
RECORD = "docs/intake/records/caldova-intake/intake.json"


def receiver_prerequisites():
    names = ("FRONTIER_FACTORY_REFERENCE", "FRONTIER_FACTORY_RECEIVER_PYTHON")
    values = [os.environ.get(name) for name in names]
    requested = any(values) or os.environ.get("FRONTIER_FACTORY_RECEIVER_REQUIRED") == "1"
    if not requested:
        raise unittest.SkipTest("Explicit retained receiver integration not requested")
    if not all(values):
        raise RuntimeError("Explicit receiver integration requires the retained reference and interpreter")
    reference, receiver = map(Path, values)
    if not reference.is_dir() or not receiver.is_file():
        raise RuntimeError("Retained receiver reference/interpreter unavailable")
    command = [str(receiver), "-B", "-c",
               "import importlib.metadata, sys; "
               "assert sys.version_info[:3] == (3,14,10); "
               "assert importlib.metadata.version('jsonschema') == '4.25.1'"]
    try:
        result = subprocess.run(command, cwd=reference, env=isolated_env(), capture_output=True,
                                text=True, encoding="utf-8", timeout=120)
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError("Retained pinned receiver prerequisites unavailable") from error
    if result.returncode:
        raise RuntimeError("Retained Python 3.14.10/jsonschema 4.25.1 prerequisite failed")
    return reference, str(receiver)


class ReceiverOptIn(unittest.TestCase):
    def test_optional_missing_is_explicit_skip_but_required_or_partial_is_error(self):
        keys = ("FRONTIER_FACTORY_REFERENCE", "FRONTIER_FACTORY_RECEIVER_PYTHON",
                "FRONTIER_FACTORY_RECEIVER_REQUIRED")
        for values, expected in (({}, unittest.SkipTest),
                                 ({keys[2]: "1"}, RuntimeError),
                                 ({keys[0]: "missing"}, RuntimeError),
                                 ({keys[0]: "missing", keys[1]: "missing"}, RuntimeError)):
            with self.subTest(values=values), mock.patch.dict(os.environ, values, clear=True):
                with self.assertRaises(expected):
                    receiver_prerequisites()


class FactoryReceiver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference, cls.receiver = receiver_prerequisites()
        cls.storage = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.storage.cleanup)
        cls.root = Path(cls.storage.name)
        cls.expected = {}
        if cls.git("rev-parse", "HEAD").decode().strip() != COMMIT:
            raise RuntimeError("Retained reference HEAD is not the approved fixed commit")
        if cls.git("status", "--porcelain"):
            raise RuntimeError("Retained reference is not clean")
        for line in cls.git("ls-tree", "-r", COMMIT).splitlines():
            description, name = line.split(b"\t", 1)
            mode, kind, _ = description.split()
            if (mode, kind) != (b"100644", b"blob"):
                raise RuntimeError("Reference contains nonordinary modes or a submodule")
            path = name.decode("utf-8")
            cls.expected[path] = cls.git("show", COMMIT + ":" + path)
        if len(cls.expected) != 149 or sum(map(len, cls.expected.values())) != 726850:
            raise RuntimeError("Retained fixed source inventory differs")
        for name, size, digest in (
            ("docs/intake/intake.schema.json", 8381,
             "04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f"),
            ("tools/intake.py", 15736,
             "4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370"),
        ):
            raw = cls.expected[name]
            if len(raw) != size or hashlib.sha256(raw).hexdigest() != digest:
                raise RuntimeError("Retained fixed schema/validator fingerprint differs")
        template = cls.root / "actual-reference.zip"
        cls.git("archive", "--format=zip", "--output=" + str(template), COMMIT)
        cls.foundation = template.read_bytes()
        cls.installed, cls.candidate = build_candidate(cls.root)
        print("REFERENCE", COMMIT, "149 blobs 726850 bytes; archive SHA256",
              hashlib.sha256(cls.foundation).hexdigest())
        print("CANDIDATE two independent byte-identical builds SHA256",
              hashlib.sha256(cls.candidate).hexdigest())

    @classmethod
    def git(cls, *args):
        return subprocess.run(["git", "--no-pager", "-C", str(cls.reference), *args],
                              check=True, capture_output=True, env=isolated_env(), timeout=120).stdout

    def fixture(self, name, accepted=False):
        fixture = prepare(self.root / name, accepted=accepted, foundation=self.foundation)
        receipt = fixture["request"]["template"]
        receipt["discovery"]["evidence"] = "Synthetic simulated lookup for developer reference compatibility only."
        receipt["acquisition"]["evidence"] = "Actual retained reference archive; synthetic customer acquisition assertion."
        save(fixture)
        return fixture

    def exported(self, fixture):
        result = export_command(self.installed, fixture, self.root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        raw = fixture["out"].read_bytes()
        summary = json.loads(result.stdout)
        self.assertEqual(summary["zip_sha256"], hashlib.sha256(raw).hexdigest())
        return raw, summary

    def unpack(self, fixture, raw):
        output = fixture["out"].parent / "receiver-output"
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            archive.extractall(output)  # Only an already validated producer result.
        return output

    def receiver_run(self, output, originals=None, record=RECORD):
        args = [self.receiver, "-B", "-m", "tools.intake", "validate",
                str(output / record), "--root", str(output)]
        if originals is not None:
            args.extend(["--source-root", str(originals)])
        return subprocess.run(args, cwd=self.reference, env=isolated_env(), capture_output=True,
                              text=True, encoding="utf-8", timeout=120)

    def valid_receiver(self, output, originals=None, record=RECORD):
        result = self.receiver_run(output, originals, record)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        scope = ("baseline and source bytes" if originals is not None else
                 "baseline bytes and recorded source evidence (original bytes not checked)")
        self.assertIn(scope, result.stdout)
        self.assertIn("human approvals are not authenticated", result.stdout)
        return result.stdout.strip()

    def producer_refused(self, fixture, old):
        save(fixture)
        result = export_command(self.installed, fixture, self.root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertRegex(json.loads(result.stdout)["error"], r"^FACTORY_[A-Z_]+$")
        self.assertEqual(fixture["out"].read_bytes(), old)

    def test_exact_package_actual_foundation_and_default_accepted_receiver(self):
        for accepted in (False, True):
            with self.subTest(accepted=accepted):
                fixture = self.fixture("accepted" if accepted else "review", accepted=accepted)
                before = {p: p.read_bytes() for folder in (fixture["source"], fixture["baseline"])
                          for p in folder.rglob("*") if p.is_file()}
                raw, summary = self.exported(fixture)
                again, repeated = self.exported(fixture)
                self.assertEqual(raw, again)
                self.assertEqual(summary, repeated)
                self.assertEqual(summary["intake_disposition"], "accepted" if accepted else "needs-clarification")
                self.assertEqual(summary["evidence_kind"], "synthetic-compatibility")
                self.assertEqual(summary["receiver_validation"], "not-performed")
                check_inventory(self, raw)
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    # ALL source names/bytes/modes, independently from Git objects.
                    foundation_names = set(archive.namelist()) - {
                        RECORD, "START_HERE.md", "handover/manifest.json",
                        "docs/intake/records/caldova-intake/review.md",
                        *(row["baseline"]["path"] for row in fixture["request"]["intake"]["artifacts"]
                          if row["status"] == "provided"),
                    }
                    self.assertEqual(foundation_names, set(self.expected))
                    for name, contents in self.expected.items():
                        self.assertEqual(archive.read(name), contents, name)
                        self.assertEqual(stat.S_IMODE(archive.getinfo(name).external_attr >> 16), 0o644, name)
                output = self.unpack(fixture, raw)
                baseline = self.valid_receiver(output)
                full = self.valid_receiver(output, fixture["source"])
                print("RECEIPT", summary["intake_disposition"], "ZIP SHA256", summary["zip_sha256"])
                print(baseline)
                print(full)
                # External proof stays separate; never rewrite frozen ZIP metadata.
                self.assertEqual(fixture["out"].read_bytes(), raw)
                self.assertEqual(before, {p: p.read_bytes() for p in before})
                record = output / RECORD
                original_record = record.read_bytes()
                for extra, code in ((0, 0), (1, 1)):
                    record.write_bytes(original_record + b" " * (MIB - len(original_record) + extra))
                    result = self.receiver_run(output, fixture["source"])
                    self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                record.write_bytes(original_record)

    def test_generated_record_negative_probes_and_producer_old_good_preservation(self):
        fixture = self.fixture("negative", accepted=True)
        raw, _ = self.exported(fixture)
        output = self.unpack(fixture, raw)
        original_request = copy.deepcopy(fixture["request"])
        original_record = json.loads((output / RECORD).read_bytes())

        def mutate(data, kind):
            if kind == "missing-design":
                row = next(row for row in data["artifacts"] if row["role"] == "solution-design")
                row.update(status="missing", source=None, baseline=None, transformation=None)
            elif kind == "review-approval":
                data["review"]["approval"] = None
            elif kind == "restricted":
                data["transfer"]["classification"] = "restricted"
            elif kind == "transfer-approved-null":
                data["transfer"]["approval"] = None
            elif kind == "generic-transform":
                data["artifacts"][0]["transformation"] = {
                    "kind": "transformation", "rationale": "Transformed.", "approval": None}
            elif kind == "equal-transform-digests":
                data["artifacts"][0]["transformation"] = {
                    "kind": "redaction", "rationale": "Synthetic recorded transform.", "approval": approved()}
            else:
                raise AssertionError("Unknown negative probe")

        for kind in ("missing-design", "review-approval", "restricted",
                     "transfer-approved-null", "generic-transform", "equal-transform-digests"):
            with self.subTest(probe=kind):
                fixture["request"] = copy.deepcopy(original_request)
                mutate(fixture["request"]["intake"], kind)
                self.producer_refused(fixture, raw)
                record = copy.deepcopy(original_record)
                mutate(record, kind)
                (output / RECORD).write_bytes(encode(record))
                result = self.receiver_run(output, fixture["source"])
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        fixture["request"] = original_request
        save(fixture)
        request_raw = fixture["request_file"].read_bytes()
        record_raw = encode(original_record)
        for suffix in (b',"schema_version":"1.0"}', b',"nonfinite":NaN}'):
            with self.subTest(json=suffix):
                # Duplicate the EXISTING schema_version field in the record,
                # and the existing schema field in the producer request.
                bad_request = request_raw.rstrip()[:-1] + (
                    b',"schema":"frontier-agent-factory-request/1.0"}'
                    if b"schema_version" in suffix else suffix)
                fixture["request_file"].write_bytes(bad_request)
                result = export_command(self.installed, fixture, self.root)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(fixture["out"].read_bytes(), raw)
                (output / RECORD).write_bytes(record_raw.rstrip()[:-1] + suffix)
                result = self.receiver_run(output, fixture["source"])
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        # A digest mismatch is a RECEIVER-side integrity probe: producer hashes
        # actual bytes automatically, so supplied manual hashes must be refused.
        fixture["request"] = copy.deepcopy(original_request)
        fixture["request"]["intake"]["artifacts"][0]["baseline"]["sha256"] = "0" * 64
        self.producer_refused(fixture, raw)
        record = copy.deepcopy(original_record)
        record["artifacts"][0]["baseline"]["sha256"] = "0" * 64
        (output / RECORD).write_bytes(encode(record))
        result = self.receiver_run(output, fixture["source"])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("SHA-256 mismatch", result.stderr)
        print("NEGATIVES missing-design/review/transfer/restricted/transform/duplicate/nonfinite/hash: rejected")

    def test_real_shared_64mib_exact_then_one_over_and_baseline_only_scope(self):
        fixture = self.fixture("budget", accepted=True)
        provided = [row for row in fixture["request"]["intake"]["artifacts"] if row["status"] == "provided"]
        blueprint = next(row for row in provided if row["role"] == "blueprint")
        bp_source = fixture["source"] / blueprint["source"]["path"]
        bp_baseline = fixture["baseline"] / blueprint["baseline"]["path"]
        remaining = 64 * MIB - len(bp_source.read_bytes()) - len(bp_baseline.read_bytes())
        for index, row in enumerate(provided[:2]):
            pair = 32 * MIB if index == 0 else remaining - 32 * MIB
            baseline_size = pair // 2
            source_size = pair - baseline_size
            original = b"# Caldova synthetic budget evidence\n"
            baseline = original + b"A" * (baseline_size - len(original))
            source = baseline + b"\n" * (source_size - baseline_size)
            (fixture["source"] / row["source"]["path"]).write_bytes(source)
            (fixture["baseline"] / row["baseline"]["path"]).write_bytes(baseline)
            if source != baseline:
                row["transformation"] = {"kind": "redaction", "rationale": "Synthetic whitespace redaction.",
                                         "approval": approved()}
        measured = sum((fixture[key] / row[descriptor]["path"]).stat().st_size
                       for row in provided for key, descriptor in (("source", "source"), ("baseline", "baseline")))
        self.assertEqual(measured, 64 * MIB)
        save(fixture)
        raw, summary = self.exported(fixture)
        output = self.unpack(fixture, raw)
        self.valid_receiver(output, fixture["source"])
        self.valid_receiver(output)
        # Actual extra source byte, valid JSON whitespace, no patched constants.
        bp_source.write_bytes(bp_source.read_bytes() + b" ")
        self.producer_refused(fixture, raw)
        record = json.loads((output / RECORD).read_bytes())
        next(row for row in record["artifacts"] if row["role"] == "blueprint")["source"]["sha256"] = (
            hashlib.sha256(bp_source.read_bytes()).hexdigest())
        (output / RECORD).write_bytes(encode(record))
        self.valid_receiver(output)  # Original bytes genuinely not checked here.
        result = self.receiver_run(output, fixture["source"])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("size limit", result.stderr)
        print("BUDGET actual 67108864 bytes PASS; 67108865 full-source FAIL; baseline-only PASS; ZIP SHA256",
              summary["zip_sha256"])

    @unittest.skipUnless(os.name == "nt", "Windows native junction probe")
    def test_native_junction_is_rejected_by_producer_and_receiver(self):
        fixture = self.fixture("junction", accepted=True)
        raw, _ = self.exported(fixture)
        output = self.unpack(fixture, raw)
        real = fixture["source"] / "real"
        real.mkdir()
        (real / "prd.md").write_bytes((fixture["source"] / "prd.md").read_bytes())
        junction = fixture["source"] / "junction"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(real)],
                                cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        try:
            fixture["request"]["intake"]["artifacts"][0]["source"]["path"] = "junction/prd.md"
            self.producer_refused(fixture, raw)
            record = json.loads((output / RECORD).read_bytes())
            record["artifacts"][0]["source"]["path"] = "junction/prd.md"
            (output / RECORD).write_bytes(encode(record))
            result = self.receiver_run(output, fixture["source"])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("links are not allowed", result.stderr)
        finally:
            junction.rmdir()  # Remove only our link, not its target.

    def test_actual_windows_history_bytes_and_supersedes_validate(self):
        fixture = self.fixture("history")
        upstream = self.reference / "tests/fixtures/intake"
        old_raw = (upstream / "accepted.json").read_bytes()
        old = json.loads(old_raw)
        old_path = f"docs/intake/records/{old['intake_id']}/intake.json"
        target = fixture["baseline"] / old_path
        target.parent.mkdir(parents=True)
        target.write_bytes(old_raw)
        expected_files = {}
        provided = [row for row in old["artifacts"] if row["status"] == "provided"]
        self.assertTrue(any("\\" in row["baseline"]["path"] for row in provided))
        for row in provided:
            name = row["baseline"]["path"].replace("\\", "/")
            contents = (upstream / "workspace" / name).read_bytes()
            self.assertEqual(hashlib.sha256(contents).hexdigest(), row["baseline"]["sha256"])
            destination = fixture["baseline"] / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(contents)
            expected_files[name] = contents
            fixture["request"]["sharing_review"]["artifacts"][old["intake_id"] + ":" + row["id"]] = approved()
        fixture["request"]["history"] = [old["intake_id"]]
        fixture["request"]["intake"]["supersedes"] = old["intake_id"]
        for row in fixture["request"]["intake"]["artifacts"]:
            if row["status"] == "provided":
                row["baseline"]["path"] = row["baseline"]["path"].replace("/", "\\")
        descriptor = fixture["request"]["blueprint"]
        descriptor["baseline_path"] = descriptor["baseline_path"].replace("/", "\\")
        save(fixture)
        before = {p: p.read_bytes() for folder in (fixture["source"], fixture["baseline"])
                  for p in folder.rglob("*") if p.is_file()}
        raw, summary = self.exported(fixture)
        check_inventory(self, raw)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(archive.read(old_path), old_raw)
            for name, contents in expected_files.items():
                self.assertEqual(archive.read(name), contents)
        output = self.unpack(fixture, raw)
        self.valid_receiver(output, fixture["source"])
        self.valid_receiver(output, upstream / "source", old_path)
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        print("HISTORY actual Windows-spelled accepted JSON and authored bytes preserved; supersedes/current+old full receiver PASS")
