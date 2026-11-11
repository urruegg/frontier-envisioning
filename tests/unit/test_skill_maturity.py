"""Product maturity is explicit and installation does not acknowledge Preview use."""
import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load


class SkillMaturity(unittest.TestCase):
    def test_packager_reads_maturity_and_optional_fields(self):
        package = load("tools/build_package.py")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "SKILL.md"
            path.write_text(
                '---\nname: frontier-finops\nmetadata:\n  version: "1.9.1"\n'
                '  maturity: preview\n  optional: true\n  requires_preview_ack: true\n---\n',
                encoding="utf-8",
            )
            fields = package.frontmatter(path)
            self.assertIn("maturity", fields, "package maturity fields missing")
            self.assertEqual(fields["maturity"], "preview")
            self.assertIs(fields["optional"], True)
            self.assertIs(fields["requires_preview_ack"], True)

    def test_eight_skill_product_maturity_is_explicit(self):
        read = load("tools/fe_lib.py").frontmatter
        skills = sorted((ROOT / "plugin/skills").glob("*/SKILL.md"))
        self.assertEqual(len(skills), 8)
        for path in skills:
            fields = read(path.read_text(encoding="utf-8"))
            expected = "preview" if path.parent.name == "frontier-finops" else "ga"
            self.assertEqual(fields.get("metadata.maturity"), expected, path.parent.name)

    def test_installer_reports_preview_but_does_not_acknowledge_it(self):
        self.install_probe("preview", True)

    def test_existing_finops_update_or_reinstall_never_inherits_cached_consent(self):
        for version in ("1.7.1", "1.9.1"):
            with self.subTest(installed_version=version):
                self.install_probe("preview", True, installed_version=version)

    def test_installer_rejects_maturity_metadata_mismatch(self):
        self.install_probe("ga", False)

    def test_installer_rejects_nonboolean_acknowledgement_metadata(self):
        self.install_probe("preview", False, requires_ack=1)

    def test_packager_rejects_nonoptional_finops_before_writing(self):
        package = load("tools/build_package.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "plugin"
            shutil.copytree(ROOT / "plugin", plugin)
            skill = plugin / "skills/frontier-finops/SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8").replace("  optional: true", "  optional: false"), encoding="utf-8")
            output = io.StringIO()
            with mock.patch.object(package, "PLUGIN", plugin), contextlib.redirect_stdout(output):
                code = package.main(["--dist", str(root / "dist")])
            self.assertEqual(code, 1)
            self.assertTrue("frontier-finops" in output.getvalue(), "missing explicit maturity error")
            self.assertFalse((root / "dist").exists())

    def install_probe(self, maturity, valid, requires_ack=True, installed_version=None):
        installer = load("plugin/install/prepare_install.py")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = (
                '---\nname: frontier-finops\nmetadata:\n  version: "1.9.1"\n'
                '  maturity: preview\n  optional: true\n  requires_preview_ack: true\n---\n'
            )
            skill = root / "skills/frontier-finops/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text(text, encoding="utf-8")
            spec = {
                "plugin": "frontier-envisioning", "version": "1.9.1",
                "skills": [{
                    "name": "frontier-finops", "folder": "skills/frontier-finops",
                    "files": {"SKILL.md": hashlib.sha256(skill.read_bytes()).hexdigest()},
                    "maturity": maturity, "optional": True, "requires_preview_ack": requires_ack,
                }],
            }
            plan = root / "install/plugin-install.json"
            plan.parent.mkdir()
            plan.write_text(json.dumps(spec), encoding="utf-8")
            installed = root / "installed"
            previous = installed / "frontier-finops" / "SKILL.md"
            if installed_version:
                previous.parent.mkdir(parents=True)
                previous.write_text(
                    f'---\nname: frontier-finops\nmetadata:\n  version: "{installed_version}"\n'
                    '  maturity: ga\n  preview_acknowledged: true\n---\n',
                    encoding="utf-8",
                )
                previous_bytes = previous.read_bytes()
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = installer.main(["--root", str(root), "--installed", str(installed)])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 0 if valid else 1)
            self.assertEqual(result["verified"], valid)
            if valid:
                self.assertEqual(result["skills"][0]["maturity"], "preview")
                self.assertIs(result["skills"][0]["requires_preview_ack"], True)
                self.assertIn("not GA", result["preview_notice"])
                self.assertNotIn("preview_acknowledged", result)
                self.assertNotIn("--acknowledge-finops-preview", "".join(result["copy_calls"]))
                if installed_version:
                    self.assertEqual(result["skills"][0]["installed_version"], installed_version)
                    self.assertEqual(result["skills"][0]["status"], "reinstall" if installed_version == "1.9.1" else "update")
                    self.assertEqual(previous.read_bytes(), previous_bytes)
            else:
                self.assertEqual(result["copy_calls"], [])
                self.assertTrue(result["problems"])
