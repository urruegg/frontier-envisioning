# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Exercise the exact nine-skill distribution, never a repository CLI substitute."""
import contextlib
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

from tests.factory_fixture import encode, prepare, save, zip_bytes
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
