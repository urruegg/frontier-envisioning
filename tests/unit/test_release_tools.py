"""Version bump, Superpowers installer, GitHub bootstrap (dry run) and the seed backlog."""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load

bump = load("tools/bump_version.py")
superpowers = load("tools/superpowers.py")
bootstrap = load("tools/bootstrap_github.py")
fe_lib = load("tools/fe_lib.py")


class Bump(unittest.TestCase):
    def test_bump_updates_every_version_carrier(self):
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            for rel in ["plugin/.claude-plugin/plugin.json", "plugin/package/manifest.json", "plugin/README.md", "CHANGELOG.md",
                        "tools/build_package.py", "plugin/skills/frontier-blueprint/scripts/build_blueprint.py"]:
                (t / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, t / rel)
            for smd in (ROOT / "plugin/skills").glob("*/SKILL.md"):
                (t / "plugin/skills" / smd.parent.name).mkdir(parents=True, exist_ok=True)
                shutil.copyfile(smd, t / "plugin/skills" / smd.parent.name / "SKILL.md")
            changed = bump.bump(t, "9.8.7", "2027-01-31")
            self.assertGreaterEqual(len(changed), 13)
            self.assertEqual(json.loads((t / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"], "9.8.7")
            self.assertEqual(json.loads((t / "plugin/package/manifest.json").read_text(encoding="utf-8"))["version"], "9.8.7")
            for smd in (t / "plugin/skills").glob("*/SKILL.md"):
                self.assertEqual(fe_lib.frontmatter(smd.read_text(encoding="utf-8"))["metadata.version"], "9.8.7")
            self.assertIn('PLUGIN_VERSION = "9.8.7"', (t / "plugin/skills/frontier-blueprint/scripts/build_blueprint.py").read_text(encoding="utf-8"))
            self.assertIn("Version 9.8.7", (t / "plugin/README.md").read_text(encoding="utf-8"))
            self.assertIn("FIXED_DATE = (2027, 1, 31, 0, 0, 0)", (t / "tools/build_package.py").read_text(encoding="utf-8"))
            self.assertIn("## 9.8.7 — 2027-01-31", (t / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_versions_must_be_numeric(self):
        with self.assertRaises(SystemExit):
            bump.bump(ROOT, "1.5.0-beta")


@unittest.skipUnless(shutil.which("git"), "git not installed")
class Superpowers(unittest.TestCase):
    def test_install_and_verify_from_a_local_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src"
            (src / "skills" / "brainstorming").mkdir(parents=True)
            (src / "skills" / "brainstorming" / "SKILL.md").write_text("---\nname: brainstorming\ndescription: x\n---\n", encoding="utf-8")
            (src / "LICENSE").write_text("MIT", encoding="utf-8")
            git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "init.defaultBranch=main"]
            for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "init"], ["tag", "v7.0.2"]):
                subprocess.run(git + cmd, cwd=src, check=True, capture_output=True)
            vendor = Path(tmp) / "repo" / ".agents" / "skills"
            superpowers.VENDOR_DIR, superpowers.LOCK = vendor, vendor / "superpowers.lock.json"
            args = type("A", (), {"source": str(src), "version": "v7.0.2"})()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(superpowers.cmd_install(args, vendor=True), 0)
                self.assertEqual(superpowers.cmd_verify(), 0)
            lock = json.loads(superpowers.LOCK.read_text(encoding="utf-8"))
            self.assertEqual(lock["skills"], ["brainstorming"])
            self.assertEqual(lock["license"], "MIT")
            (vendor / "brainstorming" / "SKILL.md").write_text("tampered", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(superpowers.cmd_verify(), 1)


class Bootstrap(unittest.TestCase):
    def test_personalisation_updates_only_complete_owner_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owners = root / ".github" / "CODEOWNERS"
            owners.parent.mkdir()
            owners.write_text("* @urruegg\n/plugin/ @urruegg-team\n", encoding="utf-8")
            with mock.patch.object(bootstrap, "ROOT", root), contextlib.redirect_stdout(io.StringIO()):
                bootstrap.personalise("example-org", "frontier-envisioning", True)
            self.assertEqual(
                owners.read_text(encoding="utf-8"),
                "* @example-org\n/plugin/ @urruegg-team\n",
            )

    def test_ruleset_requires_the_m0_checks(self):
        status_rule = next(
            rule for rule in bootstrap.ruleset(1)["rules"]
            if rule["type"] == "required_status_checks"
        )
        contexts = {
            item["context"]
            for item in status_rule["parameters"]["required_status_checks"]
        }
        self.assertEqual(contexts, {"L1 quality gate", "L2 browser tests", "IaC validation"})

    def test_dry_run_changes_nothing_and_plans_everything(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(bootstrap.main(["--owner", "example"]), 0)
        out = buf.getvalue()
        self.assertIn("DRY RUN", out)
        self.assertNotIn("$ ", out.replace("would run: ", ""))
        self.assertIn("gh repo create example/frontier-envisioning --private", out)
        self.assertIn('"L1 quality gate"', json.dumps(bootstrap.ruleset(1)))
        self.assertEqual(out.count("gh issue create"), len(bootstrap.read_issues()))

    def test_backlog_is_consistent(self):
        backlog = json.loads((ROOT / "backlog/backlog.json").read_text(encoding="utf-8"))
        labels = {x["name"] for x in backlog["labels"]}
        milestones = {m["key"] for m in backlog["milestones"]}
        issues = bootstrap.read_issues()
        ids = [i["id"] for i in issues]
        self.assertEqual(len(ids), len(set(ids)))
        for i in issues:
            self.assertTrue(set(i["labels"]) <= labels, i["id"])
            self.assertTrue(i["milestone"] in milestones or i["milestone"] == "", i["id"])
            self.assertIn("## Acceptance criteria", i["body"], i["id"])
            self.assertTrue(any(lab.startswith("type:") for lab in i["labels"]), i["id"])


class ReleaseDocuments(unittest.TestCase):
    def test_complete_bundle_contains_both_authoritative_documents(self):
        bundle = load("tools/build_release.py")
        packager = load("tools/build_package.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dist = root / "dist"
            demo = root / "build" / "demo"
            plugin = root / "plugin"
            documents = {
                "docs/prd.md": b"requirements\r\n",
                "docs/solution-design.md": b"architecture\n",
            }
            archive_bytes = io.BytesIO()
            with zipfile.ZipFile(archive_bytes, "w") as archive:
                archive.writestr("README.md", b"synthetic archive")
            nested_zip = archive_bytes.getvalue()
            files = {
                dist / "frontier-envisioning-plugin-1.6.1.zip": nested_zip,
                demo / bundle.DEMO_HTML_NAME: b"blueprint",
                demo / "identity" / "caldova-agent-identity" / "catalog.html": b"catalogue",
                demo / "identity" / "caldova-agent-identity.zip": nested_zip,
                plugin / "README.md": b"guide",
                plugin / "MIT.md": b"licence",
                plugin / "THIRD-PARTY-NOTICES.md": b"notices",
                root / "CHANGELOG.md": b"history",
                root / ".github" / "agent-policy" / "policy.md": b"engineering policy",
                root / "docs" / "engineering" / "policy.md": b"engineering policy",
                root / "docs" / "sprint" / "S-001.md": b"sprint",
                root / "docs" / "intake" / "audit.json": b'{"raw": "audit evidence"}',
                root / "docs" / "analysis" / "existing.md": b"# Private\n| Classification | Microsoft internal |\n",
                root / "docs" / "prd-and-solution-design.md": b"retired index must not be bundled",
                **{root / name: data for name, data in documents.items()},
            }
            for path, data in files.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            with mock.patch.object(bundle, "ROOT", root), \
                    mock.patch.object(bundle, "PLUGIN", plugin), \
                    mock.patch.object(bundle, "DEMO_DIR", demo), \
                    mock.patch.object(bundle, "plugin_version", return_value="1.6.1"), \
                    mock.patch.object(bundle, "load_module", return_value=packager), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bundle.main(["--dist", str(dist)]), 0)
            expected = {
                "install/frontier-envisioning-plugin-1.6.1.zip": nested_zip,
                "README.md": b"guide",
                "MIT.md": b"licence",
                "THIRD-PARTY-NOTICES.md": b"notices",
                "CHANGELOG.md": b"history",
                f"demo/{bundle.DEMO_HTML_NAME}": b"blueprint",
                "demo/Caldova - agent identity catalogue.html": b"catalogue",
                "demo/caldova-agent-identity.zip": nested_zip,
                **documents,
            }
            with zipfile.ZipFile(dist / "frontier-envisioning-1.6.1-complete.zip") as archive:
                prefix = "frontier-envisioning-1.6.1/"
                for name, data in expected.items():
                    with self.subTest(path=name):
                        self.assertIn(prefix + name, archive.namelist())
                        self.assertEqual(archive.read(prefix + name), data)
                self.assertCountEqual(
                    archive.namelist(),
                    [prefix + name for name in [*expected, "START-HERE.md"]],
                )
                start = archive.read(prefix + "START-HERE.md").decode("utf-8")
                for name in documents:
                    self.assertIn(name if not name.startswith("docs/analysis/") else "docs/analysis/", start)
                self.assertNotIn("prd-and-solution-design.md", start)
                self.assertNotIn("docs/analysis/", start)
                for entry in archive.infolist():
                    self.assertEqual(entry.date_time, packager.FIXED_DATE)
                    self.assertEqual(entry.create_system, 3)
                    self.assertEqual(entry.compress_type, zipfile.ZIP_DEFLATED)
                    self.assertEqual(entry.external_attr, 0o644 << 16)
            self.assertEqual(
                (dist / "SHA256SUMS.txt").read_bytes(),
                "".join(
                    f"{fe_lib.sha256_file(path)}  {path.name}\n"
                    for path in sorted(dist.glob("*.zip"))
                ).encode("utf-8"),
            )


class ReleaseWorkflowContracts(unittest.TestCase):
    def test_release_requires_explicit_owner_enablement(self):
        import yaml

        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(workflow["jobs"]["build"].get("if"), "${{ vars.RELEASE_ENABLED == 'true' }}")

    def test_release_checks_the_tag_with_l1_and_l2(self):
        import yaml

        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        )
        steps = [step.get("name", "") for step in workflow["jobs"]["build"]["steps"]]
        self.assertIn("Gate L2 on the tag", steps)
        self.assertLess(steps.index("Gate L1 (strict) on the tag"), steps.index("Gate L2 on the tag"))
        self.assertLess(steps.index("Gate L2 on the tag"), steps.index("Release bundle and manifest"))
        self.assertEqual(workflow["jobs"]["publish"]["environment"], "release-approval")


if __name__ == "__main__":
    unittest.main()
