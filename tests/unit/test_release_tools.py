"""Version bump, Superpowers installer, GitHub bootstrap (dry run) and the seed backlog."""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
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


def release_workflow():
    import yaml

    path = Path(os.environ.get("FRONTIER_RELEASE_WORKFLOW", ROOT / ".github/workflows/release.yml"))
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class PublishedReleaseVerification(unittest.TestCase):
    def setUp(self):
        self.verifier = load("tools/verify_release.py", "published_release_verifier")
        # Unit tests never inherit the host's network policy.
        policy = mock.patch.dict(os.environ, {"CI": ""})
        policy.start()
        self.addCleanup(policy.stop)

    @contextlib.contextmanager
    def published_fixture(self, workflow=False):
        from tests.unit import test_release_evidence as fixtures

        fixture = fixtures.ReleaseEvidence()
        fixture.setUp()
        try:
            if workflow:
                fixture.manifest["build_evidence"] = {
                    "profile": "github-owner-dispatch-publication/1.0", "repository": fixtures.REPOSITORY,
                    "source_commit": fixture.source, "control_commit": fixture.source, "intended_tag": fixtures.TAG,
                    "run_id": "123", "run_attempt": "1",
                    "run_url": f"https://github.com/{fixtures.REPOSITORY}/actions/runs/123",
                    "manual_checks": "confirmed by dispatching maintainer", "native_attestation": "not-provided",
                }
            for name, relative, how in fixture.expected:
                data = fixture.assets.get(name, b'{"generated":"2026-01-01","sample":"synthetic"}')
                path = fixture.root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                row = next(row for row in fixture.manifest["artefacts"] if row["name"] == name)
                row.update(bytes=len(data), sha256=fixtures.digest(data))
                if how:
                    row["sha256_normalised"] = fixtures.digest(self.verifier.normalise(data, how))
            fixture.refresh()
            yield fixture
        finally:
            fixture.doCleanups()

    def check(self, fixture, online=False):
        self.assertTrue(callable(getattr(self.verifier, "check", None)), "structured check API is missing")
        return self.verifier.check(fixture.root, "1.10.0", online=online)

    def invoke(self, fixture, args, version="1.10.0", ci=""):
        output = io.StringIO()
        with mock.patch.object(self.verifier, "ROOT", fixture.root), \
                mock.patch.object(self.verifier, "plugin_version", return_value=version), \
                mock.patch.dict(os.environ, {"CI": ci}), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = self.verifier.main(args)
        return code, output.getvalue()

    def test_explicit_missing_manifest_is_an_error_not_an_unreleased_pass(self):
        verifier = load("tools/verify_release.py", "missing_explicit_manifest")
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.json"
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                self.assertEqual(verifier.main(["--manifest", str(missing)]), 1)
            self.assertIn("ERROR", output.getvalue())

    def test_published_profiles_compare_real_outputs_online_and_offline(self):
        for workflow in (False, True):
            with self.subTest(workflow=workflow), self.published_fixture(workflow) as fixture, \
                    contextlib.redirect_stdout(io.StringIO()):
                # Tool-only descendants must not be mistaken for the released source.
                fixture.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                            "commit", "--allow-empty", "-qm", "Tool-only descendant")
                self.assertNotEqual(fixture.git("rev-parse", "HEAD"), fixture.source)
                result = self.check(fixture, online=True)
                self.assertEqual(result["status"], "verified")
                self.assertEqual(result["source_commit"], fixture.source)
                self.assertEqual(result["manifest"], fixture.manifest)
                self.assertEqual(result["version"], "1.10.0")
                self.assertIn("4 of 4", result["message"])
                fixture.requests.clear()
                self.assertEqual(self.check(fixture), result)
                self.assertEqual(fixture.requests, [])

    def test_generated_date_is_the_only_normalised_difference(self):
        with self.published_fixture() as fixture, contextlib.redirect_stdout(io.StringIO()):
            self.check(fixture, online=True)
            path = fixture.root / fixture.expected[1][1]
            path.write_bytes(path.read_bytes().replace(b"2026-01-01", b"2027-02-02"))
            self.assertEqual(self.check(fixture)["status"], "verified")
            path.write_bytes(path.read_bytes().replace(b"synthetic", b"changed"))
            with self.assertRaisesRegex(ValueError, "sha256"):
                self.check(fixture)

    def test_missing_and_tampered_outputs_fail_with_diagnostics(self):
        for missing in (False, True):
            with self.subTest(missing=missing), self.published_fixture() as fixture, \
                    contextlib.redirect_stdout(io.StringIO()):
                self.check(fixture, online=True)
                path = fixture.root / fixture.expected[0][1]
                if missing:
                    path.unlink()
                else:
                    path.write_bytes(b"tampered")
                with self.assertRaisesRegex(ValueError, "missing:|sha256"):
                    self.check(fixture)
                code, output = self.invoke(fixture, [])
                self.assertEqual(code, 1)
                self.assertIn("ERROR", output)
                self.assertNotIn("status: verified", output)

    def test_unavailable_offline_is_not_confirmed_development(self):
        with self.published_fixture() as fixture:
            result = self.check(fixture)
            self.assertEqual(result["status"], "not-performed")
            self.assertIsNone(result["manifest"])
            self.assertIsNone(result["source_commit"])
            self.assertIn("not performed", result["message"].lower())
            self.assertEqual(fixture.requests, [])

    def test_online_healthy_absence_is_development(self):
        from tests.unit import test_release_evidence as fixtures

        with self.published_fixture() as fixture:
            fixture.routes[fixtures.BASE + "/releases?per_page=100&page=1"] = []
            fixture.routes[fixtures.BASE + "/git/matching-refs/tags/" + fixtures.TAG] = []
            result = self.check(fixture, online=True)
            self.assertEqual(result["status"], "development")
            self.assertIsNone(result["manifest"])
            self.assertIsNone(result["source_commit"])
            self.assertTrue(fixture.requests)

    def test_online_authentication_failure_never_falls_back_to_cache(self):
        from tests.unit import test_release_evidence as fixtures

        with self.published_fixture() as fixture, contextlib.redirect_stdout(io.StringIO()):
            self.check(fixture, online=True)
            fixture.routes[fixtures.BASE] = (b"", 1)
            with self.assertRaises(ValueError):
                self.check(fixture, online=True)
            code, output = self.invoke(fixture, [], ci="true")
            self.assertEqual(code, 1)
            self.assertIn("ERROR", output)

    def test_standalone_policy_is_offline_unless_online_or_ci(self):
        for args, ci, online in (([], "", False), (["--online"], "", True), ([], "true", True)):
            with self.subTest(args=args, ci=ci), self.published_fixture() as fixture:
                code, output = self.invoke(fixture, args, ci=ci)
                self.assertEqual(code, 0)
                self.assertEqual(bool(fixture.requests), online)
                self.assertIn("verified" if online else "not-performed", output)
                self.assertIn(fixture.source if online else "unavailable", output)

    def test_explicit_wrong_version_fails_without_force(self):
        with self.published_fixture() as fixture:
            path = fixture.root / "historical.json"
            path.write_text(json.dumps(fixture.manifest), encoding="utf-8")
            code, output = self.invoke(fixture, ["--manifest", str(path)], version="1.10.1", ci="true")
            self.assertEqual(code, 1)
            self.assertIn("ERROR", output)
            self.assertNotIn("skipped", output)
            self.assertEqual(fixture.requests, [])

    def test_force_compares_historical_outputs_without_remote_or_fake_source(self):
        with self.published_fixture() as fixture:
            path = fixture.root / "historical.json"
            retained = {key: value for key, value in fixture.manifest.items() if key != "build_evidence"}
            path.write_text(json.dumps(retained), encoding="utf-8")
            args = ["--manifest", str(path), "--force"]
            code, output = self.invoke(fixture, args, version="1.10.1", ci="true")
            self.assertEqual(code, 0)
            self.assertIn("release 1.10.0: 4 of 4", output)
            (fixture.root / fixture.expected[0][1]).unlink()
            code, output = self.invoke(fixture, args, version="1.10.1", ci="true")
            self.assertEqual(code, 1)
            self.assertIn("missing:", output)
            self.assertEqual(fixture.requests, [])

    def test_writer_bytes_and_cli_remain_unchanged_under_ci(self):
        import datetime as dt

        with self.published_fixture() as fixture:
            out = fixture.root / "written.json"
            code, _ = self.invoke(fixture, ["--write", str(out)], ci="true")
            self.assertEqual(code, 0)
            expected = {
                "schema": "frontier-release-manifest/1.0", "version": "1.10.0",
                "date": dt.date.today().isoformat(),
                "provenance": "Built by the release workflow from the tag v1.10.0.",
                "artefacts": fixture.manifest["artefacts"], "not_reproduced": [],
            }
            self.assertEqual(out.read_bytes(), (json.dumps(expected, indent=1, ensure_ascii=False) + "\n").encode())
            self.assertEqual(fixture.requests, [])

    def test_local_writer_under_ci_never_resolves_remote_evidence(self):
        with self.published_fixture() as fixture:
            metadata = fixture.root / "plugin/.claude-plugin/plugin.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text('{"version":"1.10.0"}', encoding="utf-8")
            out = fixture.root.parent / (fixture.root.name + "-local.json")
            self.addCleanup(out.unlink, missing_ok=True)
            code, output = self.invoke(fixture, [
                "--local-source", str(fixture.root), "--tag", "v1.10.0",
                "--expected-commit", fixture.source, "--write", str(out),
            ], ci="true")
            self.assertEqual(code, 0, output)
            self.assertEqual(fixture.requests, [])
            self.assertEqual(json.loads(out.read_bytes())["build_evidence"]["source_commit"], fixture.source)

    def test_malformed_explicit_manifest_is_diagnostic_failure(self):
        with self.published_fixture() as fixture:
            path = fixture.root / "broken.json"
            for data in ("{", "[]"):
                with self.subTest(data=data):
                    path.write_text(data, encoding="utf-8")
                    code, output = self.invoke(fixture, ["--manifest", str(path)], ci="true")
                    self.assertEqual(code, 1)
                    self.assertIn("ERROR", output)
                    self.assertEqual(fixture.requests, [])

    def test_explicit_empty_comparison_is_not_a_verified_release(self):
        with self.published_fixture() as fixture:
            path = fixture.root / "empty.json"
            for rows in (None, [], {}):
                with self.subTest(rows=rows):
                    path.write_text(json.dumps({"version": "1.10.0", "artefacts": rows}), encoding="utf-8")
                    code, output = self.invoke(fixture, ["--manifest", str(path), "--force"])
                    self.assertEqual(code, 1)
                    self.assertIn("ERROR", output)
                    self.assertNotIn("0 of 0 artefacts reproduced", output)
                    self.assertEqual(fixture.requests, [])


@unittest.skipUnless(shutil.which("git"), "git not installed")
class LocalReleaseManifest(unittest.TestCase):
    def setUp(self):
        self.verifier = load("tools/verify_release.py")

    @contextlib.contextmanager
    def source_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            root.mkdir()
            metadata = root / "plugin/.claude-plugin/plugin.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text('{"version":"1.10.0"}\n', encoding="utf-8")
            (root / ".gitignore").write_text("dist/\nbuild/\n", encoding="utf-8")
            for _, relative, _ in self.verifier.standard_artefacts("1.10.0"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'{"generated":"2026-11-15","sample":"synthetic"}\n')

            def git(*args):
                return subprocess.run(
                    ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                    cwd=root, check=True, capture_output=True, text=True, encoding="utf-8",
                ).stdout.strip()

            git("init", "-q")
            git("add", ".gitignore", "plugin")
            git("commit", "-qm", "synthetic source")
            commit = git("rev-parse", "HEAD")
            git("tag", "-a", "v1.10.0", "-m", "synthetic release")
            yield root, Path(tmp) / "release-manifest.json", commit, git

    def invoke_local(self, root, output, commit, tag="v1.10.0"):
        args = ["--local-source", str(root), "--write", str(output),
                "--tag", tag, "--expected-commit", commit]
        with mock.patch.object(self.verifier, "ROOT", root), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as error:
            try:
                code = self.verifier.main(args)
            except SystemExit as exc:
                code = exc.code
        return code, error.getvalue()

    def test_local_manifest_records_real_tag_without_workflow_or_approval_claims(self):
        with self.source_fixture() as (root, output, commit, git):
            code, error = self.invoke_local(root, output, commit)
            self.assertEqual((code, error), (0, ""))
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertIn("locally", manifest["provenance"])
            self.assertNotIn("release workflow", manifest["provenance"])
            evidence = manifest["build_evidence"]
            self.assertEqual(evidence["source_commit"], commit)
            self.assertEqual(evidence["tag_object"], git("rev-parse", "refs/tags/v1.10.0"))
            self.assertEqual(evidence["control_commit"], commit)
            self.assertNotIn("run_id", evidence)
            self.assertNotIn("workflow_ref", evidence)
            self.assertNotIn("approved", evidence)
            self.assertEqual(evidence["native_attestation"], "not-provided")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(self.verifier.verify(manifest, root), [])

    def test_local_manifest_rejects_invalid_source_before_writing(self):
        for case in ("wrong-sha", "malformed-tag", "dirty", "lightweight", "wrong-version", "nested-root"):
            with self.subTest(case=case), self.source_fixture() as (root, output, commit, git):
                tag = "v1.10.0"
                if case == "wrong-sha":
                    commit = "0" * 40
                elif case == "malformed-tag":
                    tag = "v1.10.0;echo unsafe"
                elif case == "dirty":
                    (root / ".gitignore").write_text("changed\n", encoding="utf-8")
                elif case == "lightweight":
                    git("tag", "-d", tag)
                    git("tag", tag)
                elif case == "wrong-version":
                    (root / "plugin/.claude-plugin/plugin.json").write_text(
                        '{"version":"1.10.1"}\n', encoding="utf-8")
                    git("add", "plugin")
                    git("commit", "-qm", "synthetic version mismatch")
                    commit = git("rev-parse", "HEAD")
                    git("tag", "-d", tag)
                    git("tag", "-a", tag, "-m", "synthetic mismatch")
                elif case == "nested-root":
                    root = root / "plugin"
                code, error = self.invoke_local(root, output, commit, tag)
                self.assertEqual(code, 1)
                self.assertIn("ERROR:", error)
                self.assertFalse(output.exists())

    def test_existing_workflow_manifest_writer_keeps_reproduction_contract(self):
        with self.source_fixture() as (root, output, _, _), \
                mock.patch.object(self.verifier, "ROOT", root), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.verifier.write_manifest(output, "1.10.0"), 0)
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertNotIn("build_evidence", manifest)
            self.assertIn("release workflow", manifest["provenance"])
            self.assertEqual(self.verifier.verify(manifest, root), [])

    def test_local_manifest_never_overwrites_tagged_source_or_previous_output(self):
        with self.source_fixture() as (root, output, commit, _):
            metadata = root / "plugin/.claude-plugin/plugin.json"
            before = metadata.read_bytes()
            code, error = self.invoke_local(root, metadata, commit)
            self.assertEqual(code, 1)
            self.assertIn("ERROR:", error)
            self.assertEqual(metadata.read_bytes(), before)
            output.write_bytes(b"previous handoff")
            code, error = self.invoke_local(root, output, commit)
            self.assertEqual(code, 1)
            self.assertIn("ERROR:", error)
            self.assertEqual(output.read_bytes(), b"previous handoff")


class ReleaseWorkflowContracts(unittest.TestCase):
    def test_ci_read_only_token_is_scoped_to_existing_l1_gate(self):
        import yaml

        workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(workflow.get("on", workflow.get(True)), {
            "pull_request": None, "push": {"branches": ["main"]}, "workflow_dispatch": None,
        })
        self.assertEqual({key: job["name"] for key, job in workflow["jobs"].items()}, {
            "l1": "L1 quality gate", "l2": "L2 browser tests", "iac": "IaC validation",
        })
        gate = next(step for step in workflow["jobs"]["l1"]["steps"] if step.get("name") == "Gate L1 (strict)")
        self.assertEqual(gate["run"], "python tools/dev.py ci")
        self.assertEqual(gate.get("env"), {"GH_TOKEN": "${{ github.token }}"})
        self.assertNotIn("env", workflow)
        pins = {
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",
            "actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1",
            "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9",
        }
        for job in workflow["jobs"].values():
            self.assertNotIn("permissions", job)
            self.assertNotIn("GH_TOKEN", job.get("env", {}))
            for step in job["steps"]:
                if "uses" in step:
                    self.assertIn(step["uses"], pins)
                if step is not gate:
                    self.assertNotIn("GH_TOKEN", step.get("env", {}))

    def test_release_requires_explicit_owner_enablement(self):
        workflow = release_workflow()
        if "workflow_dispatch" in workflow.get("on", workflow.get(True, {})):
            self.skipTest("owner-dispatch contract replaces legacy variable enablement")
        self.assertEqual(workflow["jobs"]["build"].get("if"), "${{ vars.RELEASE_ENABLED == 'true' }}")

    def test_release_checks_the_tag_with_l1_and_l2(self):
        workflow = release_workflow()
        if "workflow_dispatch" in workflow.get("on", workflow.get(True, {})):
            self.skipTest("owner-dispatch gates the immutable source before creating its tag")
        steps = [step.get("name", "") for step in workflow["jobs"]["build"]["steps"]]
        self.assertIn("Gate L2 on the tag", steps)
        self.assertLess(steps.index("Gate L1 (strict) on the tag"), steps.index("Gate L2 on the tag"))
        self.assertLess(steps.index("Gate L2 on the tag"), steps.index("Release bundle and manifest"))
        self.assertEqual(workflow["jobs"]["publish"]["environment"], "release-approval")


class ManualReleaseWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = release_workflow()
        event = self.workflow.get("on", self.workflow.get(True, {}))
        if "workflow_dispatch" not in event and not os.environ.get("FRONTIER_RELEASE_WORKFLOW"):
            self.skipTest("protected owner-dispatch proposal has not been adopted")

    def step(self, job, name):
        return next(s for s in self.workflow["jobs"][job]["steps"] if s.get("name") == name)

    def script(self, job, name):
        run = self.step(job, name)["run"]
        match = re.search(r"python - <<'PY'\n(.*?)\nPY(?:\n|$)", run, re.S)
        self.assertIsNotNone(match, name)
        return match.group(1)

    def execute(self, script, root, env):
        with mock.patch.dict(os.environ, env, clear=True), \
                contextlib.redirect_stdout(io.StringIO()), \
                contextlib.chdir(root):
            exec(compile(script, "<release-workflow-test>", "exec"), {"__name__": "__main__"})

    def test_owner_dispatch_is_explicit_main_only_and_not_a_tag_trigger(self):
        event = self.workflow.get("on", self.workflow.get(True, {}))
        self.assertEqual(set(event), {"workflow_dispatch"})
        inputs = event["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["version"]["type"], "string")
        for key in ("publish", "manual_checks"):
            self.assertEqual(inputs[key]["type"], "boolean")
            self.assertIs(inputs[key]["default"], False)
        self.assertIs(self.workflow["concurrency"]["cancel-in-progress"], False)

    def test_write_token_is_confined_to_publishing_without_a_checkout(self):
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        build, publish = (self.workflow["jobs"][name] for name in ("build", "publish"))
        self.assertEqual(build["permissions"], {"contents": "read"})
        self.assertEqual(publish["permissions"], {"contents": "write", "actions": "read"})
        self.assertEqual(publish["needs"], "build")
        self.assertNotIn("environment", publish)
        for step in publish["steps"]:
            self.assertNotIn("checkout@", step.get("uses", ""))
        for job in self.workflow["jobs"].values():
            for step in job["steps"]:
                self.assertNotIn("attest-build-provenance", step.get("uses", ""))
                if "uses" in step:
                    self.assertRegex(step["uses"], r"@[0-9a-f]{40}$")
                if "checkout@" in step.get("uses", ""):
                    self.assertIs(step["with"]["persist-credentials"], False)

    def test_full_source_gates_and_independent_rebuild_precede_handover(self):
        names = [s.get("name") for s in self.workflow["jobs"]["build"]["steps"]]
        ordered = ["Validate release request", "Gate L1", "Gate L2", "Independent plugin comparison",
                   "Prepare release files", "SBOM", "Checksums and handover", "Upload verified files"]
        self.assertEqual([names.index(n) for n in ordered], sorted(names.index(n) for n in ordered))
        self.assertIn("tools/dev.py check --strict", self.step("build", "Gate L1")["run"])
        self.assertIn("tools/dev.py site e2e --strict", self.step("build", "Gate L2")["run"])
        self.assertIn("cmp ", self.step("build", "Independent plugin comparison")["run"])
        sbom = self.step("build", "SBOM")["run"]
        self.assertIn("bf5d4f99bc98c119d549d08fc02ae92598a7a42772f17317c01031a92632e05b", sbom)
        self.assertIn("-li false", sbom)
        self.assertIn("PLAYWRIGHT_BROWSERS_PATH", self.workflow["jobs"]["build"]["env"])

    def test_preflight_rejects_wrong_authority_version_or_confirmation(self):
        script = self.script("build", "Validate release request")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = root / "plugin/.claude-plugin/plugin.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text('{"version":"1.11.0"}', encoding="utf-8")
            env = {"REPOSITORY": "urruegg/frontier-envisioning", "REF": "refs/heads/main",
                   "ACTOR": "urruegg", "TRIGGERING_ACTOR": "urruegg", "EVENT": "workflow_dispatch",
                   "VERSION": "1.11.0", "PUBLISH": "true", "MANUAL_CHECKS": "true",
                   "SOURCE_SHA": "a" * 40}
            self.execute(script, root, env)
            for key, value in (("ACTOR", "urruegg_microsoft"), ("TRIGGERING_ACTOR", "another-user"),
                               ("REF", "refs/heads/feature"), ("REPOSITORY", "other/repo"),
                               ("EVENT", "push"), ("VERSION", "1.10.0"), ("VERSION", "1.11.0;echo bad"),
                               ("PUBLISH", "false"), ("MANUAL_CHECKS", "false"), ("SOURCE_SHA", "short")):
                with self.subTest(key=key, value=value), self.assertRaises((ValueError, SystemExit)):
                    self.execute(script, root, dict(env, **{key: value}))

    def test_publisher_verifies_exact_files_hashes_and_source_before_any_write(self):
        script = self.script("publish", "Verify downloaded files")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / "release"
            assets.mkdir()
            package = "frontier-envisioning-plugin-1.11.0.zip"
            manifest = {
                "version": "1.11.0",
                "build_evidence": {"profile": "github-owner-dispatch-publication/1.0",
                                   "repository": "urruegg/frontier-envisioning",
                                   "source_commit": "a" * 40, "control_commit": "a" * 40,
                                   "run_id": "123", "run_attempt": "1"},
            }
            for name in (package, "sbom-spdx.zip"):
                with zipfile.ZipFile(assets / name, "w") as archive:
                    archive.writestr("synthetic.txt", "offline fixture")
            (assets / "release-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            import hashlib
            names = (package, "release-manifest.json", "sbom-spdx.zip")
            sums = "".join(hashlib.sha256((assets / n).read_bytes()).hexdigest() + "  " + n + "\n" for n in names)
            (assets / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")
            (root / "release-notes.md").write_text("Synthetic release notes.\n", encoding="utf-8")
            env = {"VERSION": "1.11.0", "SOURCE_SHA": "a" * 40, "REPOSITORY": "urruegg/frontier-envisioning",
                   "RUN_ID": "123", "RUN_ATTEMPT": "1",
                   "EXPECTED_SUMS": hashlib.sha256((assets / "SHA256SUMS.txt").read_bytes()).hexdigest(),
                   "EXPECTED_NOTES": hashlib.sha256((root / "release-notes.md").read_bytes()).hexdigest()}
            self.execute(script, root, env)
            for name in (*names, "SHA256SUMS.txt", "../release-notes.md"):
                path = assets / name
                original = path.read_bytes()
                path.write_bytes(b"tampered")
                with self.subTest(name=name), self.assertRaises((ValueError, SystemExit, zipfile.BadZipFile)):
                    self.execute(script, root, env)
                path.write_bytes(original)
            extra = assets / "complete.zip"
            extra.write_bytes(b"not an allowed download")
            with self.assertRaises((ValueError, SystemExit)):
                self.execute(script, root, env)

    def test_tagging_rejects_stale_or_conflicting_state_without_overwriting(self):
        import urllib.error
        import urllib.request

        script = self.script("publish", "Create or verify annotated tag")
        env = {"REPOSITORY": "urruegg/frontier-envisioning", "REF": "refs/heads/main",
               "ACTOR": "urruegg", "TRIGGERING_ACTOR": "urruegg", "EVENT": "workflow_dispatch",
               "VERSION": "1.11.0", "PUBLISH": "true", "MANUAL_CHECKS": "true",
               "SOURCE_SHA": "a" * 40, "GH_TOKEN": "synthetic-never-sent"}
        cases = ("main-changed", "published", "draft", "rollback", "lightweight",
                 "different-source", "different-tag-name", "permission-error", "wrong-actor")
        with tempfile.TemporaryDirectory() as tmp:
            for case in (*cases, "new", "resume-same-tag"):
                requests = []

                def respond(request):
                    method = request.get_method()
                    path = request.full_url.split("/frontier-envisioning/", 1)[1]
                    requests.append((method, path))
                    if case == "permission-error":
                        raise urllib.error.HTTPError(request.full_url, 403, "synthetic forbidden", {}, None)
                    if method == "POST":
                        data = {"sha": "b" * 40}
                    elif path == "git/ref/heads/main":
                        data = {"object": {"sha": ("c" if case == "main-changed" else "a") * 40}}
                    elif path == "releases/tags/v1.11.0" and case in ("published", "draft"):
                        data = {"draft": case == "draft"}
                    elif path == "releases/latest":
                        data = {"tag_name": "v1.12.0" if case == "rollback" else "v1.10.0"}
                    elif path == "git/ref/tags/v1.11.0" and case != "new":
                        data = {"object": {"type": "commit" if case == "lightweight" else "tag", "sha": "b" * 40}}
                    elif path == "git/tags/" + "b" * 40:
                        data = {"tag": "v1.9.0" if case == "different-tag-name" else "v1.11.0",
                                "object": {"type": "commit", "sha": ("c" if case == "different-source" else "a") * 40}}
                    else:
                        raise urllib.error.HTTPError(request.full_url, 404, "synthetic absent", {}, None)
                    return io.BytesIO(json.dumps(data).encode("utf-8"))

                with self.subTest(case=case), mock.patch.object(urllib.request, "urlopen", side_effect=respond):
                    values = dict(env, ACTOR="another-user") if case == "wrong-actor" else env
                    if case in cases:
                        with self.assertRaises((ValueError, urllib.error.HTTPError)):
                            self.execute(script, Path(tmp), values)
                        self.assertFalse(any(method != "GET" for method, _ in requests), requests)
                    else:
                        self.execute(script, Path(tmp), values)
                        writes = [(method, path) for method, path in requests if method != "GET"]
                        self.assertEqual(writes, [("POST", "git/tags"), ("POST", "git/refs")] if case == "new" else [])


if __name__ == "__main__":
    unittest.main()
