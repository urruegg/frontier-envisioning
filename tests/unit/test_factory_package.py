# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Exercise the exact nine-skill distribution, never a repository CLI substitute."""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from tests.factory_fixture import F, encode, prepare, save, zip_bytes
from tests.unit._util import load


def isolated_env():
    env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    return env


def build_candidate(root):
    """Sanctioned actual builds; keep each dist separate and return exact bytes."""
    package = load("tools/build_package.py")
    candidates = []
    for folder in ("package-a", "package-b"):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = package.main(["--dist", str(root / folder)])
        if code:
            raise AssertionError(output.getvalue())
        candidates.append((root / folder / "frontier-envisioning-plugin-1.11.0.zip").read_bytes())
    if candidates[0] != candidates[1]:
        raise AssertionError("Independent candidate builds differ")
    installed = root / "installed"
    with zipfile.ZipFile(io.BytesIO(candidates[0])) as archive:
        archive.extractall(installed)  # Trusted just-built plugin, never source intake.
    return installed, candidates[0]


def installed_command(script, args, cwd):
    return subprocess.run([sys.executable, "-S", "-B", str(script), *map(str, args)],
                          cwd=cwd, env=isolated_env(), capture_output=True,
                          text=True, encoding="utf-8", timeout=120)


def export_command(installed, fixture, cwd):
    """The actual installed CLI, with audit traps inside its process boundary."""
    script = installed / "skills/frontier-agent-factory/scripts/export_factory.py"
    harness = """
import runpy, sys
from pathlib import Path
script = sys.argv.pop(1)
sys.path.insert(0, str(Path(script).parent))
def offline(event, args):
    if event.startswith(('socket.', 'subprocess.', 'os.exec', 'os.spawn', 'os.posix_spawn')) or event == 'os.system':
        raise AssertionError('Exporter attempted network or child execution')
sys.addaudithook(offline)
runpy.run_path(script, run_name='__main__')
"""
    args = [sys.executable, "-S", "-B", "-c", harness, str(script)]
    for flag, key in (("request", "request_file"), ("template", "template"),
                      ("source-root", "source"), ("baseline-root", "baseline"), ("out", "out")):
        args.extend(["--" + flag, str(fixture[key])])
    return subprocess.run(args, cwd=cwd, env=isolated_env(), capture_output=True,
                          text=True, encoding="utf-8", timeout=120)


def check_inventory(case, raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = archive.namelist()
        case.assertEqual(len(names), len(set(names)))
        case.assertTrue(all("\\" not in name and not name.startswith("/")
                            and ".." not in name.split("/") for name in names))
        manifest = json.loads(archive.read("handover/manifest.json"))
        inventory = manifest["inventory"]
        case.assertNotIn("handover/manifest.json", inventory)
        case.assertEqual(set(inventory), set(names) - {"handover/manifest.json"})
        for name, row in inventory.items():
            contents = archive.read(name)
            case.assertEqual(row, {"sha256": hashlib.sha256(contents).hexdigest(),
                                   "bytes": len(contents), "mode": (archive.getinfo(name).external_attr >> 16) & 0o777})
        return manifest


class FactoryPackage(unittest.TestCase):
    def test_exact_package_registers_nine_skills(self):
        package = load("tools/build_package.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = package.main(["--dist", str(root / "dist")])
            self.assertEqual(code, 0, output.getvalue())
            with zipfile.ZipFile(root / "dist/frontier-envisioning-plugin-1.11.0.zip") as archive:
                manifest = json.loads(archive.read("manifest.json"))
                self.assertEqual(len(manifest["agentSkills"]), 9)
                self.assertIn("skills/frontier-agent-factory/SKILL.md", archive.namelist())

    def test_exact_installed_offline_exports_installer_and_optional_core(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installed, candidate = build_candidate(root)
            empty = root / "empty"
            empty.mkdir()
            installer = installed / "install/prepare_install.py"
            result = installed_command(installer, ["--root", installed, "--installed", empty], root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            plan = json.loads(result.stdout)
            self.assertTrue(plan["verified"])
            self.assertEqual(len(plan["copy_calls"]), 9)
            self.assertEqual(sum(row["maturity"] == "ga" for row in plan["skills"]), 7)
            previews = {row["name"]: row["requires_preview_ack"]
                        for row in plan["skills"] if row["maturity"] == "preview"}
            self.assertEqual(previews, {"frontier-finops": True, "frontier-agent-factory": False})
            self.assertEqual(list(empty.iterdir()), [])
            self.assertNotIn("preview_acknowledged", plan)
            self.assertIn("not GA", plan["preview_notice"])
            # Only AFTER the exact install plan was verified, remove optional
            # FinOps in this disposable extraction. Factory's own core still works.
            shutil.rmtree(installed / "skills/frontier-finops")
            shadow = root / "shadow"
            shadow.mkdir()
            for name in ("canon", "build_blueprint", "factory_common", "factory_contract", "socket"):
                (shadow / (name + ".py")).write_text("raise AssertionError('cwd shadow executed')\n",
                                                   encoding="utf-8", newline="\n")
            for accepted in (False, True):
                fixture = prepare(root / ("accepted" if accepted else "review"), accepted=accepted)
                with zipfile.ZipFile(fixture["template"]) as template:
                    foundation = {name: template.read(name) for name in template.namelist()}
                foundation["tools/member_trap.py"] = b"raise AssertionError('template executed')\n"
                fixture["template"].write_bytes(zip_bytes(foundation))
                # Exercise exact CRLF authored bytes, not a normalised rewrite.
                authored = b"# Caldova reviewed PRD\r\nFR-001: Show the reviewed status.\r\n"
                (fixture["source"] / "prd.md").write_bytes(authored)
                (fixture["baseline"] / "docs/intake/records/caldova-intake/artifacts/prd.md").write_bytes(authored)
                save(fixture)
                originals = {p: p.read_bytes() for folder in (fixture["source"], fixture["baseline"])
                             for p in folder.rglob("*") if p.is_file()}
                outputs, summaries = [], []
                for _ in range(2):
                    result = export_command(installed, fixture, shadow)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stderr, "")
                    raw = fixture["out"].read_bytes()
                    summary = json.loads(result.stdout)
                    self.assertEqual(summary["zip_sha256"], hashlib.sha256(raw).hexdigest())
                    self.assertEqual(summary["intake_disposition"], "accepted" if accepted else "needs-clarification")
                    self.assertEqual(summary["receiver_validation"], "not-performed")
                    self.assertEqual(summary["cowork_validation"], "not-performed")
                    self.assertEqual(summary["tenant_readiness"], "not-assessed")
                    self.assertEqual(summary["evidence_kind"], "synthetic-compatibility")
                    self.assertEqual(summary["financial_status"], "not-requested")
                    check_inventory(self, raw)
                    outputs.append(raw)
                    summaries.append(summary)
                self.assertEqual(outputs[0], outputs[1])
                self.assertEqual(summaries[0], summaries[1])
                with zipfile.ZipFile(io.BytesIO(outputs[0])) as archive:
                    for name, contents in foundation.items():
                        self.assertEqual(archive.read(name), contents)
                    for row in fixture["request"]["intake"]["artifacts"]:
                        if row["status"] == "provided":
                            self.assertEqual(archive.read(row["baseline"]["path"]),
                                             (fixture["baseline"] / row["baseline"]["path"]).read_bytes())
                # Invalid explicit acceptance cannot be silently downgraded.
                fixture["request"]["intake"]["review"]["status"] = "accepted"
                fixture["request"]["intake"]["review"]["approval"] = None
                save(fixture)
                refused = export_command(installed, fixture, shadow)
                self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
                self.assertEqual(fixture["out"].read_bytes(), outputs[0])
                self.assertEqual(originals, {p: p.read_bytes() for p in originals})
            # Existing real value/process/blueprint probes also remove Factory.
            # FinOps was removed above, so restore ONLY from exact candidate bytes.
            with zipfile.ZipFile(io.BytesIO(candidate)) as archive:
                for name in archive.namelist():
                    if name.startswith("skills/frontier-finops/"):
                        archive.extract(name, installed)
            selftest = load("tools/selftest.py")
            checks = []
            selftest.installed_core_check(installed, root, lambda name, ok, detail="": checks.append((name, ok, detail)))
            self.assertTrue(checks)
            self.assertTrue(all(ok for _, ok, _ in checks), checks)
            self.assertFalse((installed / "skills/frontier-agent-factory").exists())

    def test_installer_tampered_factory_metadata_refuses_without_copy_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installed, _ = build_candidate(root)
            spec = installed / "install/plugin-install.json"
            plan = json.loads(spec.read_bytes())
            factory = next(row for row in plan["skills"] if row["name"] == "frontier-agent-factory")
            factory["requires_preview_ack"] = 0  # bool and int compare equal, but are not interchangeable.
            spec.write_bytes(encode(plan))
            result = installed_command(installed / "install/prepare_install.py",
                                       ["--root", installed, "--installed", root / "empty"], root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["copy_calls"], [])
            self.assertFalse((root / "empty").exists())

    def test_developer_selftest_exercises_installed_factory(self):
        module = load("tools/selftest.py")
        self.assertTrue(callable(getattr(module, "factory_cli_checks", None)),
                        "Developer self-test must exercise the installed Factory CLI")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installed, _ = build_candidate(root)
            checks = []
            module.factory_cli_checks(installed, root, lambda name, ok, detail="": checks.append((name, ok, detail)))
            self.assertGreaterEqual(len(checks), 6)
            self.assertTrue(all(ok for _, ok, _ in checks), checks)


class InstalledFactoryFinancial(unittest.TestCase):
    """Narrow financial regressions against the actual audited installed CLI."""
    @classmethod
    def setUpClass(cls):
        cls.candidate_directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.candidate_directory.cleanup)
        cls.installed, raw = build_candidate(Path(cls.candidate_directory.name))
        cls.candidate_sha256 = hashlib.sha256(raw).hexdigest()
        script = "scripts/factory_projection.py"
        actual = (cls.installed / "skills/frontier-agent-factory" / script).read_bytes()
        if actual != (F / script).read_bytes():
            raise AssertionError("Installed candidate does not contain the actual producer bytes")

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.next_fixture = 0

    def selected_json(self, document, *, role="value", historical=False):
        from tests.unit.test_factory_finops import provide
        from tests.unit.test_factory_export import add_history, exporter
        fixture = prepare(self.root / str(self.next_fixture), accepted=historical)
        self.next_fixture += 1
        row = next(row for row in fixture["request"]["intake"]["artifacts"] if row["role"] == role)
        ordinary_current = copy.deepcopy(row)
        provide(fixture, "selected.json", encode(document), role=role, artifact_id=role)
        target = row["baseline"]["path"]
        if historical:
            # W1 helpers construct data only. Export always runs the installed CLI.
            producer = exporter(self)
            record, _ = add_history(fixture, producer.contract, producer.common)
            target = next(item["baseline"]["path"] for item in record["artifacts"] if item["id"] == role)
            row.clear()
            row.update(ordinary_current)
            if ordinary_current["status"] != "provided":
                del fixture["request"]["sharing_review"]["artifacts"]["caldova-intake:" + role]
        save(fixture)
        return fixture, target

    def refusal(self, document, *, role="value", historical=False):
        fixture, target = self.selected_json(document, role=role, historical=historical)
        fixture["out"].write_bytes(b"old-good")
        inputs = {path: path.read_bytes() for folder in (fixture["source"], fixture["baseline"])
                  for path in folder.rglob("*") if path.is_file()}
        result = export_command(self.installed, fixture, self.root)
        if result.returncode == 0:
            # Demonstrate the original installed-candidate failure copied actual
            # selected bytes, not a mock or a repository-only detection result.
            with zipfile.ZipFile(fixture["out"]) as archive:
                self.assertEqual(archive.read(target), encode(document))
                manifest = json.loads(archive.read("handover/manifest.json"))
                self.assertEqual(manifest["financial"]["status"], "not-requested")
        self.assertEqual(result.returncode, 1, (result.stdout, result.stderr))
        self.assertEqual(json.loads(result.stdout)["error"], "FACTORY_FINANCIAL_ACK")
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("12345", result.stdout)
        self.assertEqual(fixture["out"].read_bytes(), b"old-good")
        self.assertEqual(list(fixture["out"].parent.glob(".factory-*.tmp")), [])
        self.assertTrue(all(path.read_bytes() == raw for path, raw in inputs.items()))

    def test_installed_current_vars_financial_schemas_require_ack(self):
        legacy = {"schema": "frontier-finops/1.0", "results": {"totals": {"total_month": 12345}}}
        for role, document in (
                ("value", {"vars": legacy}), ("prd", {"vars": [{"nested": legacy}]}),
                ("value", {"results": {"vars": legacy}}),
                ("value", {"vars": {"schema": "frontier-finops-baseline/1.0"}}),
                ("value", {"nested": legacy})):
            with self.subTest(role=role, wrapper=list(document)):
                self.refusal(document, role=role)

    def test_installed_historical_vars_financial_schemas_require_ack(self):
        legacy = {"schema": "frontier-finops/1.0", "results": {"totals": {"total_month": 12345}}}
        for role, document in (
                ("value", {"vars": legacy}), ("prd", {"vars": [{"nested": legacy}]}),
                ("value", {"results": {"vars": legacy}})):
            with self.subTest(role=role, wrapper=list(document)):
                self.refusal(document, role=role, historical=True)

    def test_installed_nonfinancial_vars_work_without_finops(self):
        document = {"vars": {"schema": "caldova-variables/1.0", "count": 10 ** 400,
                             "id": ["ordinary", "data"], "finops": "ordinary-variable-binding"}}
        fixture, target = self.selected_json(document)
        optional = self.installed / "skills/frontier-finops"
        withdrawn = Path(self.candidate_directory.name) / "withdrawn-finops"
        optional.rename(withdrawn)
        try:
            result = export_command(self.installed, fixture, self.root)
        finally:
            withdrawn.rename(optional)
        self.assertEqual(result.returncode, 0, (result.stdout, result.stderr))
        self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["financial_status"], "not-requested")
        with zipfile.ZipFile(fixture["out"]) as archive:
            self.assertEqual(archive.read(target), encode(document))
