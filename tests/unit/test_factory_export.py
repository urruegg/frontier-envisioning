# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Actual local CLI, immutable history, complete inventory and atomic refusals."""
import copy
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

from tests.factory_fixture import AT, F, approved, encode, prepare, save, zip_bytes
from tests.unit.test_factory_privacy import projection

CLI = F / "scripts/export_factory.py"


def exporter(test):
    test.assertTrue(CLI.is_file(), "W3 local export behaviour has not been implemented")
    with mock.patch.object(sys, "path", [str(F / "scripts"), *sys.path]):
        return importlib.import_module("export_factory")


def invoke(fixture, *extra, cli=CLI, cwd=None):
    command = [sys.executable, str(cli), "--request", str(fixture["request_file"]),
               "--template", str(fixture["template"]), "--source-root", str(fixture["source"]),
               "--baseline-root", str(fixture["baseline"]), "--out", str(fixture["out"]), *extra]
    return subprocess.run(command, cwd=cwd, capture_output=True, encoding="utf-8", check=False)


def add_history(fixture, contract, common, *, windows=False):
    record, files, _ = contract.materialize(fixture["request"]["intake"], fixture["baseline"],
                                           fixture["source"], common.read)
    record["intake_id"] = "previous-intake"
    record["review"] = {"status": "accepted", "rationale": "Synthetic compatibility only.",
                        "approval": approved()}
    record["gaps"] = []
    for row in record["artifacts"]:
        if row["status"] != "provided":
            continue
        old = row["baseline"]["path"]
        name = old.replace("caldova-intake", "previous-intake")
        target = fixture["baseline"] / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(files[old])
        row["baseline"]["path"] = name.replace("/", "\\") if windows else name
        if windows:
            row["source"]["path"] = "old\\nested\\" + row["source"]["path"]
        fixture["request"]["sharing_review"]["artifacts"]["previous-intake:" + row["id"]] = approved()
    raw = encode(record).replace(b"\n", b"\r\n")
    path = fixture["baseline"] / "docs/intake/records/previous-intake/intake.json"
    path.write_bytes(raw)
    fixture["request"]["history"] = ["previous-intake"]
    fixture["request"]["intake"]["supersedes"] = "previous-intake"
    save(fixture)
    return record, raw


class Export(unittest.TestCase):
    def setUp(self):
        self.m = exporter(self)
        self.p = projection(self)
        self.c = self.m.common
        self.contract = self.m.contract
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.f = prepare(self.root / "case")

    def success(self, fixture=None, *flags, **kwargs):
        run = invoke(self.f if fixture is None else fixture, *flags, **kwargs)
        self.assertEqual(run.returncode, 0, (run.stdout, run.stderr))
        self.assertEqual(run.stderr, "")
        self.assertEqual(len(run.stdout.splitlines()), 1)
        return json.loads(run.stdout)

    def refusal(self, fixture=None, *flags):
        f = self.f if fixture is None else fixture
        f["out"].write_bytes(b"old-good")
        before = {p: p.read_bytes() for root in (f["source"], f["baseline"])
                  for p in root.rglob("*") if p.is_file()}
        run = invoke(f, *flags)
        self.assertEqual(run.returncode, 1, (run.stdout, run.stderr))
        result = json.loads(run.stdout)
        self.assertRegex(result["error"], r"^FACTORY_[A-Z_]+$")
        self.assertNotIn("private-fixture-token", run.stdout + run.stderr)
        self.assertEqual(run.stderr, "")
        self.assertEqual(f["out"].read_bytes(), b"old-good")
        self.assertTrue(all(path.read_bytes() == raw for path, raw in before.items()))
        self.assertEqual(list(f["out"].parent.glob(".factory-*.tmp")), [])
        return result

    def test_cli_frozen_builds_identical_complete_inventory_and_final_sha(self):
        summary = self.success()
        first = self.f["out"].read_bytes()
        self.success()
        self.assertEqual(self.f["out"].read_bytes(), first)
        self.assertEqual(summary["zip_sha256"], hashlib.sha256(first).hexdigest())
        self.assertEqual(summary["export_validation"], "passed")
        self.assertEqual(summary["plugin_version"], "1.11.0")
        self.assertEqual(summary["receiver_validation"], "not-performed")
        self.assertEqual(summary["cowork_validation"], "not-performed")
        self.assertEqual(summary["tenant_readiness"], "not-assessed")
        self.assertEqual(summary["financial_status"], "not-requested")
        with zipfile.ZipFile(io.BytesIO(first)) as archive:
            manifest = json.loads(archive.read("handover/manifest.json"))
            inventory = manifest["inventory"]
            self.assertEqual(manifest.get("original_source_validation", {}).get("history"),
                             "not-performed-originals-unavailable")
            self.assertEqual(set(inventory), set(archive.namelist()) - {"handover/manifest.json"})
            for name, row in inventory.items():
                raw = archive.read(name)
                self.assertEqual(row["sha256"], hashlib.sha256(raw).hexdigest())
                self.assertEqual(row["bytes"], len(raw))
                self.assertEqual(row["mode"], (archive.getinfo(name).external_attr >> 16) & 0o777)
            for name in ("START_HERE.md", "docs/intake/records/caldova-intake/review.md"):
                text = archive.read(name).decode()
                self.assertIn("synthetic-compatibility", text)
                self.assertNotIn("\r", text)
            self.assertFalse(any(name.startswith("solutions/") and name != "solutions/README.md"
                                 for name in archive.namelist()))
            with zipfile.ZipFile(self.f["template"]) as template:
                for name in template.namelist():
                    self.assertEqual(archive.read(name), template.read(name))

    def test_authored_bytes_and_windows_raw_history_never_reencoded(self):
        record, raw = add_history(self.f, self.contract, self.c, windows=True)
        current = self.f["request"]["intake"]
        for row in current["artifacts"]:
            if row["status"] == "provided":
                row["baseline"]["path"] = row["baseline"]["path"].replace("/", "\\")
        self.f["request"]["blueprint"]["baseline_path"] = self.f["request"]["blueprint"][
            "baseline_path"].replace("/", "\\")
        prd = self.f["source"] / "prd.md"
        authored = "# Caldova café\r\nFR-001: Reviewed status.\r\n".encode()
        prd.write_bytes(authored)
        (self.f["baseline"] / "docs/intake/records/caldova-intake/artifacts/prd.md").write_bytes(authored)
        save(self.f)
        self.success()
        with zipfile.ZipFile(self.f["out"]) as archive:
            self.assertEqual(archive.read("docs/intake/records/previous-intake/intake.json"), raw)
            self.assertEqual(archive.read("docs/intake/records/caldova-intake/artifacts/prd.md"), authored)
            self.assertNotIn("docs/intake/records/previous-intake/review.md", archive.namelist())
            for row in record["artifacts"]:
                if row["status"] == "provided":
                    name = self.c.portable(row["baseline"]["path"])
                    self.assertEqual(archive.read(name), (self.f["baseline"] / name).read_bytes())

    def test_accepted_compatibility_still_no_runtime_and_never_downgrades(self):
        f = prepare(self.root / "accepted", accepted=True)
        self.assertEqual(self.success(f)["intake_disposition"], "accepted")
        f["request"]["intake"]["artifacts"][0]["status"] = "missing"
        save(f)
        self.refusal(f)

    def test_usage_fixed_json_and_malformed_nested_request_precedes_materialize(self):
        run = subprocess.run([sys.executable, str(CLI), "--unknown", "private-fixture-token"],
                             capture_output=True, encoding="utf-8", check=False)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)["error"], "FACTORY_USAGE")
        self.assertNotIn("private-fixture-token", run.stdout + run.stderr)
        self.f["request"]["financial"]["packets"] = [{"kind": "baseline"}]
        save(self.f)
        with mock.patch.object(self.contract, "materialize", side_effect=AssertionError("too early")):
            with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
                code = self.m.main(["--request", str(self.f["request_file"]),
                                    "--template", str(self.f["template"]),
                                    "--source-root", str(self.f["source"]),
                                    "--baseline-root", str(self.f["baseline"]),
                                    "--out", str(self.f["out"])])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stdout.getvalue())["error"], "FACTORY_REQUEST_SHAPE")
        self.assertFalse(self.f["out"].exists())

    def test_programmer_errors_not_relabelled(self):
        with mock.patch.object(self.m, "assemble", side_effect=KeyError("programmer defect")):
            with self.assertRaises(KeyError):
                self.m.main(["--request", str(self.f["request_file"]), "--template", str(self.f["template"]),
                             "--source-root", str(self.f["source"]), "--baseline-root", str(self.f["baseline"]),
                             "--out", str(self.f["out"])])

    def test_unsupported_content_actionable_and_old_good_unchanged(self):
        path = self.f["baseline"] / "docs/intake/records/caldova-intake/artifacts/prd.md"
        path.write_bytes(b"<html>private-fixture-token</html>")
        self.f["request"]["intake"]["artifacts"][0]["transformation"] = {
            "kind": "redaction", "rationale": "Synthetic changed content.", "approval": approved()}
        save(self.f)
        error = self.refusal()
        self.assertIn("reviewed JSON or Markdown equivalent", error["guidance"])

    def test_output_roots_case_aliases_and_all_input_hardlinks_are_protected(self):
        paths = [self.f["request_file"], self.f["template"], self.f["source"] / "prd.md",
                 self.f["baseline"] / "docs/intake/records/caldova-intake/artifacts/prd.md"]
        add_history(self.f, self.contract, self.c)
        paths.append(self.f["baseline"] / "docs/intake/records/previous-intake/intake.json")
        paths.append(self.f["baseline"] / "docs/intake/records/previous-intake/artifacts/prd.md")
        for path in paths:
            output = self.root / "linked.zip"
            os.link(path, output)
            before = path.read_bytes()
            f = dict(self.f, out=output)
            run = invoke(f)
            with self.subTest(kind=path.suffix):
                self.assertEqual(run.returncode, 1, run.stdout)
                self.assertEqual(output.read_bytes(), before)
            output.unlink()
        for output in (self.f["source"] / "new.zip", self.f["baseline"] / "new.zip",
                       self.f["source"], self.f["request_file"]):
            with self.subTest(output=output.name), self.assertRaises(self.c.FactoryError):
                self.m.protect_output(output, paths, [self.f["source"], self.f["baseline"]])
        with self.assertRaises(self.c.FactoryError):
            self.m.protect_output(self.root / "INPUT.JSON", [self.root / "input.json"], [])

    def test_history_missing_accepted_chain_and_collision_checks(self):
        record, _ = add_history(self.f, self.contract, self.c)
        schema = self.c.decode((F / "references/intake.schema.json").read_bytes())
        records, files, raw = self.m.load_history(["previous-intake"], self.f["baseline"], schema,
                                                self.contract.validate_intake)
        self.assertEqual(records["previous-intake"], record)
        self.assertEqual(len(files), 3)
        self.assertEqual(len(raw), 1)
        for ids in (["previous-intake", "previous-intake"], ["../bad"], ["absent"]):
            with self.subTest(ids=ids), self.assertRaises(self.c.FactoryError):
                self.m.load_history(ids, self.f["baseline"], schema, self.contract.validate_intake)
        record["review"]["status"] = "needs-clarification"
        (self.f["baseline"] / next(iter(raw))).write_bytes(encode(record))
        self.refusal()

    def test_assemble_checks_before_merge_and_capacity_includes_manifest(self):
        intake, files, _ = self.contract.materialize(self.f["request"]["intake"], self.f["baseline"],
                                                    self.f["source"], self.c.read)
        path = next(iter(files))
        for foundation in ({path.upper(): (b"forged", 0o644)},
                           {"docs/intake/records/caldova-intake": (b"parent", 0o644)},
                           {"handover/manifest.json": (b"forged", 0o644)}):
            with self.subTest(names=list(foundation)), self.assertRaises(self.c.FactoryError):
                self.m.assemble(self.f["request"], foundation, intake, files, {}, "1.11.0", "not-requested")
        observed = []
        real = self.m.archive.capacity
        def capacity(entries, **kwargs):
            observed.append(set(entries))
            return real(entries, **kwargs)
        with mock.patch.object(self.m.archive, "capacity", side_effect=capacity):
            self.m.assemble(self.f["request"], {}, intake, files, {}, "1.11.0", "not-requested")
        self.assertIn("handover/manifest.json", observed[-1])

    def test_installed_core_works_without_optional_finops_and_ignores_cwd_shadow(self):
        installed = self.root / "installed/skills"
        for skill in ("frontier-agent-factory", "frontier-blueprint", "frontier-process", "frontier-value-case"):
            shutil.copytree(F.parent / skill, installed / skill)
        trap = self.root / "shadow"
        trap.mkdir()
        (trap / "canon.py").write_text("raise AssertionError('cwd executed')\n", encoding="utf-8")
        (trap / "build_blueprint.py").write_text("raise AssertionError('cwd executed')\n", encoding="utf-8")
        self.success(cli=installed / "frontier-agent-factory/scripts/export_factory.py", cwd=trap)

    def test_template_code_is_passive_even_with_member_trap(self):
        with zipfile.ZipFile(self.f["template"]) as template:
            files = {name: template.read(name) for name in template.namelist()}
        files["tools/member_trap.py"] = b"raise AssertionError('template code executed')\n"
        self.f["template"].write_bytes(zip_bytes(files))
        save(self.f)
        self.success()
        with zipfile.ZipFile(self.f["out"]) as archive:
            self.assertEqual(archive.read("tools/member_trap.py"), files["tools/member_trap.py"])

    def test_source_zip_error_has_template_not_ordinary_guidance(self):
        self.f["template"].write_bytes(b"not-a-zip")
        save(self.f)
        result = self.refusal()
        self.assertEqual(result["error"], "FACTORY_ZIP")
        self.assertIn("template", result["guidance"].lower())

    def test_shared_authored_prd_design_and_adr_copied_once_for_two_solutions(self):
        request = self.f["request"]
        original = json.loads((self.f["source"] / "blueprint.json").read_bytes())
        second = copy.deepcopy(original["domains"][0])
        second["id"], second["agents"][0]["id"] = "D2", "D2-A01"
        original["domains"].append(second)
        with self.p.sibling("frontier-blueprint", "build_blueprint") as bp:
            report = bp.Report()
            customer = bp.customer_version(original, report)
            self.assertEqual(report.errors, [])
        (self.f["source"] / "blueprint.json").write_bytes(encode(original))
        (self.f["baseline"] / request["blueprint"]["baseline_path"]).write_bytes(encode(customer))
        selected = copy.deepcopy(request["intake"]["selected_solutions"][0])
        selected.update(solution_id="caldova-second", agent_ids=["second-agent"])
        request["intake"]["selected_solutions"].append(selected)
        requirement = copy.deepcopy(request["intake"]["requirements"][0])
        requirement.update(id="fr-002", solution_id="caldova-second")
        request["intake"]["requirements"].append(requirement)
        request["id_map"]["solutions"]["D2"] = "caldova-second"
        request["id_map"]["agents"]["D2-A01"] = "second-agent"
        request["id_map"]["requirements"]["FR-002"] = "fr-002"
        request["selection_evidence"].append({
            "solution_id": "caldova-second", "original_solution_id": "D2",
            "original_agent_ids": ["D2-A01"], "rationale": "Explicit synthetic second selection.",
            "dependency_gaps": ["implementation-gap"]})
        adr = "# ADR-0001: café\r\nKeep FR-001 and FR-002; no runtime generation.\r\n".encode()
        for row in request["intake"]["artifacts"]:
            row["solution_ids"].append("caldova-second")
            if row["role"] == "decisions":
                path = "docs/intake/records/caldova-intake/artifacts/adr-0001.md"
                row.update(status="provided", source={"path": "adr-0001.md", "reference": "synthetic-ADR-0001",
                           "version": "v1", "modified_at": "unknown"}, baseline={"path": path},
                           transformation={"kind": "none", "rationale": "Exact authored ADR.", "approval": None})
                (self.f["source"] / "adr-0001.md").write_bytes(adr)
                (self.f["baseline"] / path).write_bytes(adr)
                request["sharing_review"]["artifacts"]["caldova-intake:decisions"] = approved()
        save(self.f)
        self.success()
        with zipfile.ZipFile(self.f["out"]) as archive:
            self.assertEqual(archive.read(path), adr)
            self.assertEqual(archive.namelist().count(path), 1)
            manifest = json.loads(archive.read("handover/manifest.json"))
            self.assertEqual(manifest["id_map"], request["id_map"])
            self.assertTrue(all(len(row["solution_ids"]) == 2 for row in manifest["provided_artifacts"]))

    def test_history_aggregate_actual_128mib_budget_precedes_oversized_read(self):
        first, _ = add_history(self.f, self.contract, self.c)
        raw = b"A" * (16 * self.c.MIB)
        digest = self.c.digest(raw)
        for index in range(3):
            record = copy.deepcopy(first)
            record_id = f"previous-{index}"
            record["intake_id"] = record_id
            for row in record["artifacts"]:
                if row["status"] != "provided":
                    continue
                name = row["baseline"]["path"].replace("previous-intake", record_id)
                row["baseline"].update(path=name, sha256=digest)
                row["source"]["sha256"] = digest
                row["transformation"] = {"kind": "none", "rationale": "Synthetic exact-byte data.",
                                         "approval": None}
                path = self.f["baseline"] / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            (self.f["baseline"] / f"docs/intake/records/{record_id}/intake.json").write_bytes(encode(record))
        schema = self.c.decode((F / "references/intake.schema.json").read_bytes())
        with mock.patch.object(self.m, "read", wraps=self.c.read) as reads:
            with self.assertRaisesRegex(self.c.FactoryError, "FACTORY_LIMIT"):
                self.m.load_history([f"previous-{i}" for i in range(3)], self.f["baseline"], schema,
                                    self.contract.validate_intake)
        self.assertEqual(reads.call_count, 11)  # 3 bounded records + 7 files, then refused eighth file.
        self.assertLess(reads.call_args.args[-1], 16 * self.c.MIB)
