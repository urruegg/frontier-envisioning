"""Template assembly, neutrality scanner, repository rules, release notes and the release manifest."""
from __future__ import annotations

import io
import contextlib
import json
import os
import subprocess
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load

assemble = load("tools/assemble_template.py")
neutrality = load("tools/neutrality.py")
check_repo = load("tools/check_repo.py")
release_notes = load("tools/release_notes.py")
verify_release = load("tools/verify_release.py")
fe_lib = load("tools/fe_lib.py")
build_package = load("tools/build_package.py")
build_demo = load("tools/build_demo.py")


class Template(unittest.TestCase):
    def test_committed_template_is_assembled_from_the_sources(self):
        self.assertEqual(assemble.assemble(), fe_lib.TEMPLATE.read_bytes())

    def test_drift_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.html"
            out.write_bytes(b"stale")
            self.assertEqual(assemble.main(["--check", "--out", str(out)]), 1)
            self.assertEqual(assemble.main(["--out", str(out)]), 0)
            self.assertEqual(assemble.main(["--check", "--out", str(out)]), 0)


class PackagePortability(unittest.TestCase):
    def test_skill_files_use_case_sensitive_relative_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "references").mkdir()
            (root / "SKILL.md").write_text("skill", encoding="utf-8")
            (root / "references" / "method.md").write_text("reference", encoding="utf-8")
            with mock.patch.object(build_package, "PLUGIN", root):
                names = [p.relative_to(root).as_posix() for p in build_package.files_under(root)]
        self.assertEqual(names, ["SKILL.md", "references/method.md"])

    def test_archive_creator_metadata_is_portable(self):
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w") as archive:
            build_package.add_bytes(archive, b"content", "SKILL.md")
        with zipfile.ZipFile(data) as archive:
            info = archive.getinfo("SKILL.md")
        self.assertEqual(info.create_system, 3)
        self.assertEqual(info.date_time, build_package.FIXED_DATE)
        self.assertEqual(info.external_attr, 0o644 << 16)


class DemoPortability(unittest.TestCase):
    def setUp(self):
        version = mock.patch.object(build_demo, "plugin_version", return_value="2.0.0", create=True)
        version.start()
        self.addCleanup(version.stop)

    def test_generated_text_and_zip_are_canonical_without_changing_binary_data(self):
        self.assertTrue(hasattr(build_demo, "canonicalise_outputs"), "demo output canonicalisation is missing")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "demo.html").write_bytes(b"<html>\r\nCaldova\r\n</html>\r\n")
            kit = out / "identity"
            kit.mkdir()
            text = kit / "README.md"
            text.write_bytes(b"Caldova\r\nidentity\r\n")
            png = kit / "icon.png"
            binary = b"\x89PNG\r\n\x1a\nbinary\r\n"
            png.write_bytes(binary)
            archive_path = out / "identity.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.comment = b"Caldova identity"
                for name, data in (("identity/icon.png", binary), ("identity/README.md", text.read_bytes())):
                    info = zipfile.ZipInfo(name, date_time=(2026, 10, 30, 0, 0, 0))
                    info.create_system = 0
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o644 << 16
                    archive.writestr(info, data)
            build_demo.canonicalise_outputs(out, archive_path)
            self.assertEqual((out / "demo.html").read_bytes(), b"<html>\nCaldova\n</html>\n")
            self.assertEqual(text.read_bytes(), b"Caldova\nidentity\n")
            self.assertEqual(png.read_bytes(), binary)
            with zipfile.ZipFile(archive_path) as archive:
                self.assertEqual(archive.comment, b"Caldova identity")
                self.assertEqual(archive.namelist(), ["identity/README.md", "identity/icon.png"])
                self.assertEqual(archive.read("identity/README.md"), text.read_bytes())
                self.assertEqual(archive.read("identity/icon.png"), binary)
                for info in archive.infolist():
                    self.assertEqual(info.create_system, 3)
                    self.assertEqual(info.date_time, (2026, 10, 30, 0, 0, 0))
                    self.assertEqual(info.external_attr, 0o644 << 16)
            first = archive_path.read_bytes()
            build_demo.canonicalise_outputs(out, archive_path)
            self.assertEqual(archive_path.read_bytes(), first)

    def wrapper_without_converter(self, cmd, **kwargs):
        out = Path(cmd[cmd.index("--out-dir") + 1])
        kit = out / "identity" / "caldova-agent-identity"
        card = kit / "agents" / "sample" / "identity" / "card.svg"
        card.parent.mkdir(parents=True)
        card.write_text("<svg/>\n", encoding="utf-8")
        catalogue = kit / "catalog.html"
        catalogue.write_text("<html/>\n", encoding="utf-8")
        archive = kit.parent / "Caldova - agent identity package v1.0.zip"
        with zipfile.ZipFile(archive, "w") as zip_file:
            zip_file.writestr("caldova-agent-identity/catalog.html", catalogue.read_bytes())
        (out / fe_lib.DEMO_HTML_NAME).write_bytes(b"<html/>\r\n")
        summary = {
            "identity": {
                "kit": str(kit), "zip": str(archive), "catalogue": str(catalogue),
                "tests": "passed", "validation": {"errors": []}, "without_identity": [],
                "png": {"converted": 0, "method": None},
            },
            "blueprint": {"stats": {}},
        }
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(summary), stderr="")

    def test_default_demo_reports_missing_raster_conversion_as_failure(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(build_demo.subprocess, "run", side_effect=self.wrapper_without_converter), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            out = Path(tmp) / "demo"
            code = build_demo.main(["--out", str(out)])
            report = json.loads((out / "build-report.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 1)
        self.assertEqual(report.get("status"), "incomplete")
        self.assertIn("raster conversion incomplete", output.getvalue())
        self.assertIn("unavailable", output.getvalue())

    def test_explicit_svg_only_demo_is_labelled_and_still_writes_lf(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(build_demo.subprocess, "run", side_effect=self.wrapper_without_converter), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            out = Path(tmp) / "demo"
            self.assertEqual(build_demo.main(["--out", str(out), "--no-png"]), 0)
            self.assertEqual((out / fe_lib.DEMO_HTML_NAME).read_bytes(), b"<html/>\n")
        self.assertIn('"variant": "svg-only"', output.getvalue())

    def test_full_demo_requires_the_reported_png_to_exist(self):
        def reported_conversion(cmd, **kwargs):
            result = self.wrapper_without_converter(cmd, **kwargs)
            summary = json.loads(result.stdout)
            summary["identity"]["png"] = {"converted": 1, "method": "fixture"}
            result.stdout = json.dumps(summary)
            return result

        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(build_demo.subprocess, "run", side_effect=reported_conversion), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(build_demo.main(["--out", str(Path(tmp) / "demo")]), 1)
        self.assertIn("1 missing PNGs", output.getvalue())

    def test_full_demo_with_complete_conversion_retains_renderer_evidence(self):
        def complete_conversion(cmd, **kwargs):
            result = self.wrapper_without_converter(cmd, **kwargs)
            summary = json.loads(result.stdout)
            kit = Path(summary["identity"]["kit"])
            (kit / "agents" / "sample" / "identity" / "card.png").write_bytes(b"\x89PNG\r\n\x1a\n")
            summary["identity"]["png"] = {"converted": 1, "method": "fixture"}
            result.stdout = json.dumps(summary)
            return result

        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(build_demo.subprocess, "run", side_effect=complete_conversion), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            out = Path(tmp) / "demo"
            self.assertEqual(build_demo.main(["--out", str(out)]), 0)
            report = json.loads((out / "build-report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["identity"]["png"], {"converted": 1, "method": "fixture"})
        self.assertEqual(report.get("status"), "built")
        self.assertIn('"variant": "full"', output.getvalue())


class DemoReleaseDate(unittest.TestCase):
    def test_baseline_rate_age_uses_the_explicit_build_date(self):
        self.assertTrue(hasattr(build_demo, "build_at_release_date"), "release-date model generation is missing")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            folder = out / "value-finops"
            folder.mkdir()
            data = folder / "blueprint-value-finops.json"
            finops, value = folder / "finops.json", folder / "value.json"
            shutil.copyfile(build_demo.EXAMPLES["data"], data)
            shutil.copyfile(build_demo.EXAMPLES["finops"], finops)
            shutil.copyfile(build_demo.EXAMPLES["value"], value)
            with mock.patch.object(sys, "path", [str(fe_lib.SKILLS / "frontier-finops" / "scripts"), *sys.path]):
                calculator = load("plugin/skills/frontier-finops/scripts/finops_calc.py", "test_date_finops")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(calculator.main(["--finops", str(finops), "--value", str(value),
                                                  "--acknowledge-finops-preview"]), 0)
                summary = {"value_finops": {"folder": str(folder), "finops": str(finops), "value": str(value)}}
                self.assertEqual(build_demo.build_at_release_date(
                    out, summary, "2026-11-08", acknowledge_finops_preview=True), 0)
                self.assertEqual(json.loads(data.read_text(encoding="utf-8"))["finops"]["rates_age_days"], 4)
                self.assertEqual(build_demo.build_at_release_date(
                    out, summary, "2026-11-09", acknowledge_finops_preview=True), 0)
                self.assertEqual(json.loads(data.read_text(encoding="utf-8"))["finops"]["rates_age_days"], 5)
                self.assertTrue((out / fe_lib.DEMO_HTML_NAME).is_file())


class DevGateWiring(unittest.TestCase):
    def test_ci_includes_pipeline_tests(self):
        dev = load("tools/dev.py", "dev_gate_wiring")
        with mock.patch.multiple(
            dev,
            cmd_template_check=mock.DEFAULT,
            cmd_lint=mock.DEFAULT,
            cmd_scan=mock.DEFAULT,
            cmd_test=mock.DEFAULT,
            cmd_selftest=mock.DEFAULT,
            cmd_package=mock.DEFAULT,
            cmd_demo=mock.DEFAULT,
            cmd_verify_release=mock.DEFAULT,
            cmd_dom=mock.DEFAULT,
        ) as commands:
            self.assertEqual(dev.main(["ci"]), 0)
        commands["cmd_test"].assert_called_once_with(include_slow=True)


class BrowserCache(unittest.TestCase):
    def test_default_cache_is_project_local(self):
        dev = load("tools/dev.py", "browser_cache_default")
        self.assertTrue(hasattr(dev, "browser_env"), "browser environment helper is missing")
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                dev.browser_env(),
                {"PLAYWRIGHT_BROWSERS_PATH": str(fe_lib.BUILD / "playwright-browsers")},
            )

    def test_explicit_cache_override_is_preserved(self):
        dev = load("tools/dev.py", "browser_cache_override")
        self.assertTrue(hasattr(dev, "browser_env"), "browser environment helper is missing")
        with mock.patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": "custom-cache"}, clear=True):
            self.assertEqual(dev.browser_env(), {"PLAYWRIGHT_BROWSERS_PATH": "custom-cache"})

    def test_setup_passes_the_browser_cache(self):
        dev = load("tools/dev.py", "browser_cache_setup")
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(dev, "run", return_value=0) as run, \
                mock.patch.object(dev, "which", return_value="npm"), \
                mock.patch.object(dev, "npx", return_value="npx"):
            self.assertEqual(dev.cmd_setup(), 0)
        self.assertEqual(
            run.call_args.kwargs.get("env"),
            {"PLAYWRIGHT_BROWSERS_PATH": str(fe_lib.BUILD / "playwright-browsers")},
        )

    def test_e2e_passes_the_browser_cache(self):
        dev = load("tools/dev.py", "browser_cache_e2e")
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(dev, "run", return_value=0) as run, \
                mock.patch.object(dev, "node_modules", return_value=True), \
                mock.patch.object(dev, "cmd_demo"), \
                mock.patch.object(dev, "tool", return_value=0):
            dev.cmd_e2e()
        self.assertEqual(
            run.call_args.kwargs.get("env"),
            {"PLAYWRIGHT_BROWSERS_PATH": str(fe_lib.BUILD / "playwright-browsers"),
             "FRONTIER_SITE_DIR": str(fe_lib.BUILD / "site-e2e")},
        )


class PreviewGateFixtures(unittest.TestCase):
    def test_ci_browser_job_uses_the_isolated_fixture_runner(self):
        import yaml

        workflow = yaml.safe_load((fe_lib.ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
        browser_step = next(step for step in workflow["jobs"]["l2"]["steps"] if step.get("name") == "Browser tests")
        self.assertEqual(browser_step["run"], "python tools/dev.py e2e --strict")

    def test_dom_prepares_explicit_preview_and_passes_both_fixtures(self):
        dev = load("tools/dev.py")
        with mock.patch.object(dev, "which", return_value="node"), \
                mock.patch.object(dev, "node_modules", return_value=True), \
                mock.patch.object(dev, "cmd_demo"), \
                mock.patch.object(dev, "tool", return_value=0) as tool, \
                mock.patch.object(dev, "run", return_value=0) as run:
            dev.cmd_dom()
        preview = fe_lib.BUILD / "demo-finops-preview"
        tool.assert_any_call("build_demo", [
            "--out", str(preview), "--with-finops-preview", "--acknowledge-finops-preview",
        ])
        self.assertEqual(run.call_args.kwargs["env"], {
            "BLUEPRINT_HTML": str(fe_lib.DEMO_DIR / fe_lib.DEMO_HTML_NAME),
            "BLUEPRINT_PREVIEW_HTML": str(preview / fe_lib.DEMO_HTML_NAME),
        })

    def test_e2e_prepares_an_isolated_site_with_both_real_csp_fixtures(self):
        dev = load("tools/dev.py")
        with mock.patch.object(dev, "node_modules", return_value=True), \
                mock.patch.object(dev, "cmd_demo"), \
                mock.patch.object(dev, "tool", return_value=0) as tool, \
                mock.patch.object(dev, "run", return_value=0) as run:
            dev.cmd_e2e()
        preview = fe_lib.BUILD / "demo-finops-preview"
        tool.assert_any_call("build_demo", [
            "--out", str(preview), "--with-finops-preview", "--acknowledge-finops-preview",
        ])
        tool.assert_any_call("build_site", [
            "--out", str(fe_lib.BUILD / "site-e2e"), "--preview-demo", str(preview), "--auth", "none",
        ])
        self.assertEqual(run.call_args.kwargs["env"]["FRONTIER_SITE_DIR"], str(fe_lib.BUILD / "site-e2e"))

    def test_failed_preview_build_stops_the_test_runner(self):
        for command in ("cmd_dom", "cmd_e2e"):
            with self.subTest(command=command):
                dev = load("tools/dev.py")
                with mock.patch.object(dev, "which", return_value="node"), \
                        mock.patch.object(dev, "node_modules", return_value=True), \
                        mock.patch.object(dev, "cmd_demo"), \
                        mock.patch.object(dev, "tool", return_value=1), \
                        mock.patch.object(dev, "run") as run:
                    with self.assertRaises(dev.GateFailure):
                        getattr(dev, command)()
                    run.assert_not_called()


class Neutrality(unittest.TestCase):
    def test_terms_match_whole_words_case_and_form_insensitive(self):
        h = {neutrality.term_hash("Acme Widgets"), neutrality.term_hash("Zürich")}
        self.assertEqual([w for _, w in neutrality.find_terms("Meeting with ACME   widgets", h)], ["acme widgets"])
        self.assertEqual(neutrality.find_terms("acmewidgets and acme alone", h), [])
        self.assertTrue(neutrality.find_terms("in Zu\u0308rich", h), "combining umlaut is normalised")

    def test_denylist_holds_hashes_only(self):
        lines = [ln for ln in neutrality.DENYLIST.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
        self.assertTrue(lines)
        self.assertTrue(all(len(ln) == 64 and all(c in "0123456789abcdef" for c in ln) for ln in lines))

    def test_extra_terms_from_the_environment(self):
        old = os.environ.get("FRONTIER_NEUTRALITY_EXTRA")
        os.environ["FRONTIER_NEUTRALITY_EXTRA"] = "Secret Corp"
        try:
            self.assertTrue(neutrality.find_terms("hello secret corp"))
        finally:
            if old is None:
                del os.environ["FRONTIER_NEUTRALITY_EXTRA"]
            else:
                os.environ["FRONTIER_NEUTRALITY_EXTRA"] = old

    def test_repository_is_customer_neutral(self):
        self.assertEqual(neutrality.scan_paths(fe_lib.tracked_files()), [])


class RepositoryRules(unittest.TestCase):
    def test_repository_passes(self):
        r = check_repo.Report()
        files = fe_lib.tracked_files()
        check_repo.check_version(r)
        check_repo.check_skills(r)
        check_repo.check_licence(r)
        check_repo.check_copilot(r)
        check_repo.check_workflows(r)
        check_repo.check_hygiene(r, files)
        self.assertEqual(r.errors, [])

    def test_secret_patterns(self):
        hits = [what for rx, what in check_repo.SECRET_PATTERNS if rx.search("token ghp_" + "a" * 36)]
        self.assertEqual(hits, ["GitHub token"])

    def test_utf16_units(self):
        self.assertEqual(fe_lib.utf16_units("a\U0001F600"), 3)


class ReleaseNotes(unittest.TestCase):
    def test_section_of_a_version(self):
        notes = release_notes.section((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), "1.4.0")
        self.assertIn("Innovation Hub journey", notes)
        self.assertNotIn("## 1.3.0", notes)


class ReleaseManifest(unittest.TestCase):
    def test_manifest_1_4_0_is_well_formed(self):
        m = json.loads((ROOT / "releases/1.4.0/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["version"], "1.4.0")
        self.assertEqual(len(m["artefacts"]), 4)
        for a in m["artefacts"]:
            self.assertEqual(len(a["sha256"]), 64)

    def test_generated_date_is_normalised(self):
        a = b'{"meta":{"generated":"2026-11-08","x":1}}'
        b = b'{"meta":{"generated":"2027-01-01","x":1}}'
        self.assertEqual(verify_release.normalise(a, "generated-date"), verify_release.normalise(b, "generated-date"))
        self.assertNotEqual(verify_release.normalise(a, None), verify_release.normalise(b, None))

    def test_missing_artefacts_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            m = {"artefacts": [{"name": "x", "build_path": "dist/x.zip", "sha256": "0" * 64}]}
            self.assertEqual(len(verify_release.verify(m, base=Path(tmp))), 1)


if __name__ == "__main__":
    unittest.main()
