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
from tests.unit.test_docs_demo import html as core_demo_html

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
    def test_core_bundle_rejects_preview_or_incomplete_inputs_before_overwrite(self):
        bundle = load("tools/build_release.py")
        packager = load("tools/build_package.py")
        archive_bytes = io.BytesIO()
        with zipfile.ZipFile(archive_bytes, "w") as archive:
            archive.writestr("README.md", b"synthetic archive")
        nested_zip = archive_bytes.getvalue()
        cases = [
            (b'{"profile":"finops-preview","status":"built","variant":"full"}', None),
            (b'{"profile":"core","status":"incomplete","variant":"full"}', None),
            (b'{"profile":"core","status":"built","variant":"svg-only"}', None),
            (b'{"profile":"core","status":"built","variant":"full","value_finops":{"finops":"costs.json"}}', None),
            (b'{"profile":"core","status":"built","variant":"full","agent_finops":{}}', None),
            (b"malformed", None),
            (b"[]", None),
            *[(b'{"profile":"core","status":"built","variant":"full"}', f"ontology/{name}")
              for name in ("ontology.ttl", "ontology.md", "data-agents.md", "data-products.md")],
            (b'{"profile":"core","status":"built","variant":"full"}', "identity/kit.zip"),
        ]
        inputs = [(report, missing, core_demo_html()) for report, missing in cases]
        inputs.extend(
            (b'{"profile":"core","status":"built","variant":"full"}', None, raw)
            for raw in (
                core_demo_html(agent_finops={"schema": "frontier-agent-finops-view/1.0", "records": []}),
                core_demo_html(annotations={"agent_finops": {}}),
                core_demo_html(finops={"agents": []}),
                b"<html>not a blueprint</html>",
            )
        )
        for report, missing, raw in inputs:
            with self.subTest(report=report, missing=missing, html=raw[:90]), \
                    tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                dist, demo, plugin = root / "dist", root / "demo", root / "plugin"
                files = {
                    dist / "frontier-envisioning-plugin-1.9.1.zip": nested_zip,
                    demo / bundle.DEMO_HTML_NAME: raw,
                    demo / "identity" / "caldova-agent-identity" / "catalog.html": b"catalogue",
                    demo / "identity" / "kit.zip": nested_zip,
                    demo / "build-report.json": report,
                    **{demo / "ontology" / name: b"ontology output\n"
                       for name in ("ontology.ttl", "ontology.md", "data-agents.md", "data-products.md")},
                    plugin / "README.md": b"guide", plugin / "MIT.md": b"licence",
                    plugin / "THIRD-PARTY-NOTICES.md": b"notices",
                    root / "CHANGELOG.md": b"history",
                    root / "docs" / "prd.md": b"requirements",
                    root / "docs" / "solution-design.md": b"design",
                }
                if missing:
                    files.pop(demo / missing)
                for path, data in files.items():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                output = dist / "frontier-envisioning-1.9.1-complete.zip"
                sums = dist / "SHA256SUMS.txt"
                output.write_bytes(b"previous output")
                sums.write_bytes(b"previous checksums")
                with mock.patch.object(bundle, "ROOT", root), mock.patch.object(bundle, "PLUGIN", plugin), \
                        mock.patch.object(bundle, "DEMO_DIR", demo), \
                        mock.patch.object(bundle, "plugin_version", return_value="1.9.1"), \
                        mock.patch.object(bundle, "load_module", return_value=packager), \
                        contextlib.redirect_stdout(io.StringIO()) as messages:
                    self.assertEqual(bundle.main(["--dist", str(dist)]), 1)
                self.assertTrue(messages.getvalue())
                self.assertEqual(output.read_bytes(), b"previous output")
                self.assertEqual(sums.read_bytes(), b"previous checksums")

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
            ontology = {
                "ontology.ttl": b"ontology triples\n",
                "ontology.md": b"ontology design\n",
                "data-agents.md": b"agent proposals\n",
                "data-products.md": b"product proposals\n",
            }
            archive_bytes = io.BytesIO()
            with zipfile.ZipFile(archive_bytes, "w") as archive:
                archive.writestr("README.md", b"synthetic archive")
            nested_zip = archive_bytes.getvalue()
            core_html = core_demo_html(meta={"generated": "2026-11-12", "plugin_version": "1.6.1",
                                            "customer": "Caldova Industrial AG"})
            files = {
                dist / "frontier-envisioning-plugin-1.6.1.zip": nested_zip,
                demo / bundle.DEMO_HTML_NAME: core_html,
                demo / "identity" / "caldova-agent-identity" / "catalog.html": b"catalogue",
                demo / "identity" / "caldova-agent-identity.zip": nested_zip,
                demo / "build-report.json": b'{"profile":"core","status":"built","variant":"full"}',
                demo / "ontology" / "costs.json": b"optional Preview costs must not be bundled",
                **{demo / "ontology" / name: data for name, data in ontology.items()},
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
                f"demo/{bundle.DEMO_HTML_NAME}": core_html,
                "demo/Caldova - agent identity catalogue.html": b"catalogue",
                "demo/caldova-agent-identity.zip": nested_zip,
                **{f"demo/ontology/{name}": data for name, data in ontology.items()},
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
                self.assertEqual(len(archive.namelist()), 15)
                start = archive.read(prefix + "START-HERE.md").decode("utf-8")
                for name in documents:
                    self.assertIn(name if not name.startswith("docs/analysis/") else "docs/analysis/", start)
                self.assertNotIn("prd-and-solution-design.md", start)
                self.assertNotIn("docs/analysis/", start)
                self.assertIn("optional Preview FinOps", start)
                self.assertIn("demo/ontology/", start)
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


@unittest.skipUnless(shutil.which("git"), "git not installed")
class ReleasePreparation(unittest.TestCase):
    def setUp(self):
        self.module = load("tools/verify_release.py")
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source"
        self.control = self.root / "control"
        self.source_commit = self.make_repo(self.source)
        self.control_commit = self.make_repo(self.control)
        patch = mock.patch.object(self.module, "ROOT", self.control)
        patch.start()
        self.addCleanup(patch.stop)
        environment = mock.patch.dict("os.environ", {
            "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REF": "refs/heads/main", "GITHUB_REPOSITORY": "urruegg/frontier-envisioning",
            "GITHUB_WORKFLOW_REF": "urruegg/frontier-envisioning/.github/workflows/release.yml@refs/heads/main",
            "GITHUB_WORKFLOW_SHA": self.control_commit,
            "GITHUB_RUN_ID": "123", "GITHUB_RUN_ATTEMPT": "1",
        })
        environment.start()
        self.addCleanup(environment.stop)

    def git(self, root, *args):
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
             "-c", "init.defaultBranch=main", "-C", str(root), *args],
            check=True, capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()

    def make_repo(self, root):
        manifest = root / "plugin/.claude-plugin/plugin.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text('{"version":"1.10.0"}\n', encoding="utf-8")
        (root / "fixture.txt").write_text(root.name + "\n", encoding="utf-8")
        self.git(root, "init", "-q")
        self.git(root, "add", ".")
        self.git(root, "commit", "-qm", "synthetic release fixture")
        self.git(root, "tag", "-a", "v1.10.0", "-m", "synthetic release fixture")
        return self.git(root, "rev-parse", "HEAD")

    def call(self, args):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            try:
                code = self.module.main(args)
            except SystemExit as failure:
                code = failure.code
        return code, output.getvalue(), error.getvalue()

    def inspect(self, tag="v1.10.0", expected=None):
        return self.call(["--inspect-source", str(self.source), "--tag", tag,
                          "--expected-commit", expected or self.source_commit])

    def test_inspection_requires_the_exact_clean_annotated_source(self):
        code, output, error = self.inspect()
        self.assertEqual(code, 0, error)
        self.assertIn(self.source_commit, output)
        self.assertIn(self.control_commit, output)
        self.git(self.source, "tag", "v1.10.2")
        self.git(self.source, "tag", "-a", "v1.10.1", "-m", "version mismatch fixture")
        for tag, expected, message in (
            ("main", self.source_commit, "canonical"),
            ("v1.10.0;echo unsafe", self.source_commit, "canonical"),
            ("v1.10.0", "not-a-sha", "full SHA"),
            ("v1.10.0", "0" * 40, "agree"),
            ("v1.10.2", self.source_commit, "annotated"),
            ("v1.10.1", self.source_commit, "version"),
            ("v1.10.99", self.source_commit, "Git"),
        ):
            with self.subTest(tag=tag, expected=expected):
                code, _, error = self.inspect(tag, expected)
                self.assertNotEqual(code, 0)
                self.assertIn(message, error)
        (self.source / "fixture.txt").write_text("changed\n", encoding="utf-8")
        code, _, error = self.inspect()
        self.assertNotEqual(code, 0)
        self.assertIn("tracked changes", error)

    def test_inspection_rejects_non_main_or_fabricated_control_context(self):
        for changed, message in (
            ({"GITHUB_EVENT_NAME": "push"}, "workflow_dispatch"),
            ({"GITHUB_REF": "refs/heads/topic"}, "main"),
            ({"GITHUB_REPOSITORY": "example/other"}, "repository"),
            ({"GITHUB_WORKFLOW_SHA": "0" * 40}, "control"),
            ({"GITHUB_RUN_ATTEMPT": "0"}, "positive"),
        ):
            with self.subTest(changed=changed), mock.patch.dict("os.environ", changed):
                code, _, error = self.inspect()
                self.assertNotEqual(code, 0)
                self.assertIn(message, error)
        self.assertFalse((self.control / "build").exists())

    def prepare_fixture(self):
        for name, relative, _ in self.module.standard_artefacts("1.10.0"):
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if name.endswith(".zip"):
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("fixture.txt", "synthetic package\n")
            else:
                path.write_bytes(b'{"generated":"2026-11-14"}\n')
        code, _, error = self.call(["--prepare-source", str(self.source), "--tag", "v1.10.0",
                                   "--expected-commit", self.source_commit])
        self.assertEqual(code, 0, error)
        candidate = self.control / "build/release-preparation"
        with zipfile.ZipFile(candidate / "release/sbom-spdx.zip", "w") as archive:
            archive.writestr("fixture.spdx.json", '{"spdxVersion":"SPDX-2.2"}')
        code, _, error = self.call(["--finalize-candidate"])
        self.assertEqual(code, 0, error)
        independent = self.root / "independent"
        self.git(self.root, "clone", "--no-hardlinks", str(self.source), str(independent))
        package = independent / "dist/frontier-envisioning-plugin-1.10.0.zip"
        package.parent.mkdir()
        shutil.copyfile(self.source / "dist" / package.name, package)
        return candidate, independent

    def verify_fixture(self, candidate, independent, workflow=None):
        return self.call([
            "--verify-candidate", str(candidate), "--independent-source", str(independent),
            "--tag", "v1.10.0", "--expected-commit", self.source_commit,
            "--expected-workflow", workflow or self.control_commit,
        ])

    def rewrite_receipt(self, candidate):
        assets = candidate / "release"
        checksums = assets / "SHA256SUMS.txt"
        checksums.write_text("".join(
            f"{fe_lib.sha256_file(path)}  {path.name}\n"
            for path in sorted(assets.iterdir()) if path != checksums
        ), encoding="utf-8", newline="\n")
        manifest = json.loads((assets / "release-manifest.json").read_text(encoding="utf-8"))
        receipt = {"schema": "frontier-release-preparation/1.0", "build_evidence": manifest["build_evidence"],
                   "files": {p.name: fe_lib.sha256_file(p) for p in assets.iterdir()}}
        (candidate / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")

    def test_candidate_round_trip_preserves_manifest_and_separates_ci_facts(self):
        candidate, independent = self.prepare_fixture()
        assets = candidate / "release"
        self.assertEqual({p.name for p in assets.iterdir()}, {
            "frontier-envisioning-plugin-1.10.0.zip", "release-manifest.json",
            "sbom-spdx.zip", "SHA256SUMS.txt",
        })
        manifest = json.loads((assets / "release-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(self.module.verify(manifest, self.source), [])
        self.assertEqual(manifest["build_evidence"]["source_commit"], self.source_commit)
        self.assertEqual(manifest["build_evidence"]["workflow_commit"], self.control_commit)
        self.assertEqual(manifest["build_evidence"]["native_attestation"], "not-provided")
        with mock.patch.dict("os.environ", {"GITHUB_ACTIONS": "false"}):
            code, _, error = self.verify_fixture(candidate, independent)
        self.assertEqual(code, 0, error)
        self.assertEqual({p.name for p in (independent / "dist").iterdir()},
                         {"frontier-envisioning-plugin-1.10.0.zip"})

    def test_candidate_rejects_corruption_and_wrong_expected_bindings(self):
        candidate, independent = self.prepare_fixture()
        mutations = (
            lambda p: (p / "release/extra.txt").write_bytes(b"unexpected"),
            lambda p: (p / "release/sbom-spdx.zip").unlink(),
            lambda p: (p / "release/extra-directory").mkdir(),
            lambda p: (p / "receipt.json").write_text("[]", encoding="utf-8"),
            lambda p: (p / "release/SHA256SUMS.txt").write_text("invalid\n", encoding="utf-8"),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index), tempfile.TemporaryDirectory(dir=self.root) as temp:
                altered = Path(temp) / "candidate"
                shutil.copytree(candidate, altered)
                mutate(altered)
                code, _, error = self.verify_fixture(altered, independent)
                self.assertNotEqual(code, 0)
                self.assertIn("ERROR", error)
        code, _, error = self.verify_fixture(candidate, independent, "0" * 40)
        self.assertNotEqual(code, 0)
        self.assertIn("workflow", error)
        manifest_path = candidate / "release/release-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["build_evidence"]["approved"] = True
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.rewrite_receipt(candidate)
        code, _, error = self.verify_fixture(candidate, independent)
        self.assertNotEqual(code, 0)
        self.assertIn("evidence", error)

    def test_independent_bytes_reject_a_consistently_rewritten_candidate(self):
        candidate, independent = self.prepare_fixture()
        package = candidate / "release/frontier-envisioning-plugin-1.10.0.zip"
        package.write_bytes(b"changed package")
        manifest_path = candidate / "release/release-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artefacts"][0]["bytes"] = package.stat().st_size
        manifest["artefacts"][0]["sha256"] = fe_lib.sha256_file(package)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.rewrite_receipt(candidate)
        code, _, error = self.verify_fixture(candidate, independent)
        self.assertNotEqual(code, 0)
        self.assertIn("independent", error)

    def test_preparation_refuses_existing_or_overlapping_outputs(self):
        candidate, _ = self.prepare_fixture()
        before = {p.relative_to(candidate): p.read_bytes() for p in candidate.rglob("*") if p.is_file()}
        code, _, error = self.call(["--prepare-source", str(self.source), "--tag", "v1.10.0",
                                   "--expected-commit", self.source_commit])
        self.assertNotEqual(code, 0)
        self.assertIn("exists", error)
        self.assertEqual(before, {p.relative_to(candidate): p.read_bytes()
                                 for p in candidate.rglob("*") if p.is_file()})
        with mock.patch.object(self.module, "ROOT", self.source), mock.patch.dict(
                "os.environ", {"GITHUB_WORKFLOW_SHA": self.source_commit}):
            code, _, error = self.call(["--prepare-source", str(self.source), "--tag", "v1.10.0",
                                       "--expected-commit", self.source_commit])
        self.assertNotEqual(code, 0)
        self.assertIn("overlap", error)
        self.assertFalse((self.source / "build/release-preparation").exists())

    def test_legacy_write_uses_the_current_repository_without_ci_metadata(self):
        for _, relative, _ in self.module.standard_artefacts("1.10.0"):
            path = self.control / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"synthetic legacy repository output\n")
        package = self.control / "dist/frontier-envisioning-plugin-1.10.0.zip"
        for direct in (False, True):
            with self.subTest(direct=direct):
                target = self.control / "legacy-manifest.json"
                if direct:
                    self.module.write_manifest(target, "1.10.0")
                else:
                    code, _, error = self.call(["--write", str(target)])
                    self.assertEqual(code, 0, error)
                manifest = json.loads(target.read_text(encoding="utf-8"))
                self.assertNotIn("build_evidence", manifest)
                self.assertEqual(manifest["artefacts"][0]["sha256"], fe_lib.sha256_file(package))

    def test_new_modes_reject_arguments_they_would_otherwise_ignore(self):
        inspection = ["--inspect-source", str(self.source), "--tag", "v1.10.0",
                      "--expected-commit", self.source_commit]
        for args in (inspection + ["--manifest", "unused.json"], inspection + ["--force"],
                     ["--finalize-candidate", "--tag", "v9.9.9"]):
            with self.subTest(args=args):
                code, _, error = self.call(args)
                self.assertEqual(code, 2)
                self.assertIn("error:", error)
        self.assertFalse((self.control / "build").exists())


class ReleaseWorkflowContracts(unittest.TestCase):
    def test_preparation_has_no_automatic_or_release_write_path(self):
        import yaml

        workflow = yaml.load(
            (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader,
        )
        self.assertEqual(set(workflow["on"]), {"workflow_dispatch"})
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(set(workflow["jobs"]), {"build"})
        job = workflow["jobs"]["build"]
        self.assertEqual(job["permissions"], {"contents": "read"})
        self.assertNotIn("environment", job)
        self.assertNotIn("if", job)
        self.assertNotIn("secrets.", json.dumps(workflow))

    def test_preparation_pins_source_and_control_and_uploads_only_after_gates(self):
        import yaml

        workflow = yaml.load(
            (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader,
        )
        steps = workflow["jobs"]["build"]["steps"]
        names = [step.get("name", "") for step in steps]
        required = [
            "Check out control", "Check out source", "Inspect exact source and control context",
            "Gate L1 (strict) on the tag", "Gate L2 on the tag", "Build internal bundle",
            "Prepare exact publication candidates", "Check the extracted package",
            "SBOM (SPDX, pinned Microsoft SBOM tool)", "Finalize and verify candidate files",
            "Upload successful preparation", "Record actual platform artifact identity",
        ]
        for name in required:
            self.assertIn(name, names)
        positions = [names.index(name) for name in required]
        self.assertEqual(positions, sorted(positions))
        by_name = {step.get("name"): step for step in steps}
        for name, ref in (("Check out control", "${{ github.workflow_sha }}"),
                          ("Check out source", "${{ inputs.expected_commit }}")):
            self.assertEqual(by_name[name]["with"]["ref"], ref)
            self.assertEqual(by_name[name]["with"]["persist-credentials"], "false")
        for name in ("Gate L1 (strict) on the tag", "Gate L2 on the tag", "Build internal bundle"):
            self.assertEqual(by_name[name]["working-directory"], "source")
        self.assertNotIn("if", by_name["Upload successful preparation"])
        self.assertEqual(by_name["Upload successful preparation"]["with"]["if-no-files-found"], "error")


if __name__ == "__main__":
    unittest.main()
