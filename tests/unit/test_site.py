"""Showcase site build (security headers, sign-in) and the local server that applies them."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

from tests.unit._util import load

build_site = load("tools/build_site.py")
serve_site = load("tools/serve_site.py")
fe_lib = load("tools/fe_lib.py")

PAGE = ('<!doctype html><html><head><title>t</title></head><body><div id="view"></div>'
        '<script type="application/json" id="bp-data">{"a":1}</script>\n<script>\nconsole.log("hi");\n</script></body></html>')
TENANT = "00000000-0000-4000-8000-000000000000"


def fake_demo(root: Path) -> Path:
    demo = root / "demo"
    (demo / "identity" / "caldova-agent-identity").mkdir(parents=True)
    (demo / fe_lib.DEMO_HTML_NAME).write_text(PAGE, encoding="utf-8")
    (demo / "identity" / "caldova-agent-identity" / "catalog.html").write_text("<!doctype html><p>Caldova</p>", encoding="utf-8")
    return demo


class BuildSite(unittest.TestCase):
    def test_consumed_fixture_output_overlap_refuses_before_writes(self):
        for kind in ("core", "preview", "baseline"):
            for relation in ("equal", "fixture-inside-output", "output-inside-fixture"):
                with self.subTest(kind=kind, relation=relation), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "controlled"
                    demo = fake_demo(root)
                    fixture = demo if kind == "core" else root / kind
                    if kind != "core":
                        fixture.mkdir()
                        (fixture / fe_lib.DEMO_HTML_NAME).write_text(PAGE, encoding="utf-8")
                    out = fixture if relation == "equal" else fixture.parent if relation == "fixture-inside-output" else fixture / "site"
                    out.mkdir(parents=True, exist_ok=True)
                    (out / "keep").write_bytes(b"existing output")
                    before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                    options = {kind + "_demo": fixture} if kind != "core" else {}
                    try:
                        with self.assertRaisesRegex(SystemExit, "overlap"):
                            build_site.build(out, demo, "none", None, **options)
                    except OSError as exc:
                        self.fail(f"cleanup reached a consumed source before overlap refusal: {exc}")
                    self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_resolved_directory_alias_overlap_preserves_sources(self):
        for alias_role in ("fixture", "output"):
            with self.subTest(alias_role=alias_role), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                demo = fake_demo(root)
                output = root / "site"
                fixture = output / "baseline"
                fixture.mkdir(parents=True)
                original = fixture / fe_lib.DEMO_HTML_NAME
                original.write_text(PAGE, encoding="utf-8")
                (output / "keep").write_bytes(b"existing output")
                target = fixture if alias_role == "fixture" else output
                alias = root / "alias"
                try:
                    alias.symlink_to(target, target_is_directory=True)
                except OSError:
                    if os.name != "nt":
                        self.skipTest("directory symlinks unavailable")
                    link_text = str(alias).replace("'", "''")
                    target_text = str(target).replace("'", "''")
                    result = subprocess.run([
                        "powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                        f"New-Item -ItemType Junction -Path '{link_text}' -Target '{target_text}' -ErrorAction Stop | Out-Null",
                    ], capture_output=True, text=True, timeout=30)
                    if result.returncode:
                        self.skipTest("directory symlinks and junctions unavailable")
                self.assertEqual(alias.resolve(), target.resolve())
                try:
                    with self.assertRaisesRegex(SystemExit, "overlap"):
                        build_site.build(alias if alias_role == "output" else output, demo, "none", None,
                                         baseline_demo=alias if alias_role == "fixture" else fixture)
                except OSError as exc:
                    self.fail(f"cleanup reached a directory alias before overlap refusal: {exc}")
                self.assertEqual(original.read_text(encoding="utf-8"), PAGE)
                self.assertEqual((output / "keep").read_bytes(), b"existing output")
                self.assertEqual(alias.resolve(), target.resolve())
                self.assertFalse((output / "staticwebapp.config.json").exists())

    def test_explicit_baseline_is_isolated_and_uses_its_exact_csp(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            demo = fake_demo(root)
            baseline = root / "baseline"
            baseline.mkdir()
            page = PAGE.replace('console.log("hi");', 'console.log("baseline");')
            (baseline / fe_lib.DEMO_HTML_NAME).write_text(page, encoding="utf-8")
            preview = root / "preview"
            preview.mkdir()
            preview_page = PAGE.replace('console.log("hi");', 'console.log("legacy");')
            (preview / fe_lib.DEMO_HTML_NAME).write_text(preview_page, encoding="utf-8")
            out = root / "site"
            try:
                build_site.build(out, demo, "entra", TENANT, preview_demo=preview, baseline_demo=baseline)
            except TypeError as exc:
                self.fail(f"explicit baseline site support missing: {exc}")
            self.assertEqual((out / "blueprint-baseline.html").read_text(encoding="utf-8"), page)
            cfg = json.loads((out / "staticwebapp.config.json").read_text(encoding="utf-8"))
            routes = {route["route"]: route for route in cfg["routes"]}
            policy = routes["/blueprint-baseline.html"]["headers"]["Content-Security-Policy"]
            self.assertEqual(policy, build_site.csp_for(page))
            self.assertNotEqual(policy, routes["/blueprint.html"]["headers"]["Content-Security-Policy"])
            self.assertEqual(routes["/blueprint-preview.html"]["headers"]["Content-Security-Policy"],
                             build_site.csp_for(preview_page))
            self.assertNotEqual(policy, routes["/blueprint-preview.html"]["headers"]["Content-Security-Policy"])
            self.assertEqual(routes["/blueprint-baseline.html"]["allowedRoles"], ["authenticated"])
            self.assertEqual(cfg["globalHeaders"], build_site.GLOBAL_HEADERS)
            self.assertIn("connect-src 'none'", policy)
            self.assertNotIn("blueprint-baseline", (out / "index.html").read_text(encoding="utf-8"))
            self.assertNotIn("blueprint-baseline.html", [p.name for p in (out / "downloads").iterdir()])
            default = root / "default"
            build_site.build(default, demo, "none", None)
            self.assertFalse((default / "blueprint-baseline.html").exists())

    def test_baseline_cli_is_explicit_and_has_no_environment_toggle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch.dict(os.environ, {"FRONTIER_BASELINE_DEMO": str(root / "ignored")}), \
                    mock.patch.object(build_site, "build", return_value={}) as build:
                self.assertEqual(build_site.main([]), 0)
                self.assertIsNone(build.call_args.kwargs.get("baseline_demo"))
                try:
                    code = build_site.main(["--baseline-demo", str(root / "baseline")])
                except SystemExit as exc:
                    code = exc.code
                self.assertEqual(code, 0)
                self.assertEqual(build.call_args.kwargs.get("baseline_demo"), root / "baseline")

    def test_invalid_baseline_preserves_site_before_cleanup(self):
        for invalid in (None, '<script src="https://cdn.example.com/x.js"></script>'):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                demo = fake_demo(root)
                baseline = root / "baseline"
                baseline.mkdir()
                if invalid:
                    (baseline / fe_lib.DEMO_HTML_NAME).write_text(invalid, encoding="utf-8")
                out = root / "site"
                out.mkdir()
                sentinel = out / "keep"
                sentinel.write_bytes(b"good")
                try:
                    with self.assertRaises(SystemExit):
                        build_site.build(out, demo, "none", None, baseline_demo=baseline)
                except TypeError as exc:
                    self.fail(f"baseline preflight missing: {exc}")
                self.assertEqual(sentinel.read_bytes(), b"good")

    def test_explicit_preview_fixture_has_its_own_real_csp_and_auth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            demo = fake_demo(root)
            preview = root / "preview"
            preview.mkdir()
            preview_page = PAGE.replace('console.log("hi");', 'console.log("preview");')
            (preview / fe_lib.DEMO_HTML_NAME).write_text(preview_page, encoding="utf-8")
            out = root / "site"
            build_site.build(out, demo, "entra", TENANT, preview_demo=preview)
            self.assertEqual((out / "blueprint-preview.html").read_text(encoding="utf-8"), preview_page)
            cfg = json.loads((out / "staticwebapp.config.json").read_text(encoding="utf-8"))
            routes = {route["route"]: route for route in cfg["routes"]}
            policy = routes["/blueprint-preview.html"]["headers"]["Content-Security-Policy"]
            self.assertEqual(policy, build_site.csp_for(preview_page))
            self.assertNotEqual(policy, routes["/blueprint.html"]["headers"]["Content-Security-Policy"])
            self.assertEqual(routes["/blueprint-preview.html"]["allowedRoles"], ["authenticated"])
            self.assertNotIn("unsafe-eval", policy)
            self.assertNotIn("script-src 'unsafe-inline'", policy)
            default_out = root / "default-site"
            build_site.build(default_out, demo, "none", None)
            self.assertFalse((default_out / "blueprint-preview.html").exists())

    def test_invalid_preview_fixture_refuses_before_deleting_existing_site(self):
        for invalid in (None, '<script src="https://cdn.example.com/x.js"></script>'):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                demo = fake_demo(root)
                preview = root / "preview"
                preview.mkdir()
                if invalid is not None:
                    (preview / fe_lib.DEMO_HTML_NAME).write_text(invalid, encoding="utf-8")
                out = root / "site"
                out.mkdir()
                sentinel = out / "good.txt"
                sentinel.write_bytes(b"good site")
                with self.assertRaises(SystemExit):
                    build_site.build(out, demo, "none", None, preview_demo=preview)
                self.assertEqual(sentinel.read_bytes(), b"good site")

    def test_csp_allows_exactly_the_inline_script(self):
        csp = build_site.csp_for(PAGE)
        digest = base64.b64encode(hashlib.sha256('\nconsole.log("hi");\n'.encode()).digest()).decode()
        self.assertIn(f"script-src 'sha256-{digest}'", csp)
        self.assertEqual(csp.count("sha256-"), 1, "the JSON data island is not a script")
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn("script-src 'none'", build_site.csp_for("<p>no scripts</p>"))

    def test_external_scripts_are_refused(self):
        with self.assertRaises(SystemExit):
            build_site.csp_for('<script src="https://cdn.example.com/x.js"></script>')

    def test_entra_mode_protects_every_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            build_site.build(out, fake_demo(Path(tmp)), "entra", TENANT)
            cfg = json.loads((out / "staticwebapp.config.json").read_text(encoding="utf-8"))
            self.assertIn(TENANT, cfg["auth"]["identityProviders"]["azureActiveDirectory"]["registration"]["openIdIssuer"])
            for r in cfg["routes"]:
                self.assertTrue("statusCode" in r or r.get("allowedRoles") == ["authenticated"], r)
            self.assertEqual(cfg["responseOverrides"]["401"]["statusCode"], 302)
            self.assertTrue((out / "index.html").exists() and (out / "blueprint.html").exists() and (out / "identity-catalogue.html").exists())
            self.assertNotIn("{{", (out / "index.html").read_text(encoding="utf-8"))

    def test_entra_mode_needs_a_tenant(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                build_site.build(Path(tmp) / "site", fake_demo(Path(tmp)), "entra", "not-a-guid")

    def test_public_mode_has_no_sign_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            build_site.build(out, fake_demo(Path(tmp)), "none", None)
            cfg = json.loads((out / "staticwebapp.config.json").read_text(encoding="utf-8"))
            self.assertNotIn("auth", cfg)
            self.assertFalse(any("allowedRoles" in r for r in cfg["routes"]))


class ServeSite(unittest.TestCase):
    def test_explicit_test_site_environment_selects_only_the_local_server_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site-e2e"
            out.mkdir()
            (out / "index.html").write_text("test site", encoding="utf-8")
            with mock.patch.dict(os.environ, {"FRONTIER_SITE_DIR": str(out)}), \
                    mock.patch.object(serve_site, "make_handler") as handler, \
                    mock.patch.object(serve_site, "ThreadingHTTPServer") as server:
                server.return_value.serve_forever.side_effect = KeyboardInterrupt
                self.assertEqual(serve_site.main(["--port", "0"]), 0)
            handler.assert_called_once_with(out)

    def test_headers_and_status_codes_follow_the_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            build_site.build(out, fake_demo(Path(tmp)), "entra", TENANT)
            httpd = ThreadingHTTPServer(("127.0.0.1", 0), serve_site.make_handler(out))
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            base = f"http://127.0.0.1:{httpd.server_address[1]}"
            try:
                with urllib.request.urlopen(base + "/blueprint.html", timeout=10) as r:
                    self.assertEqual(r.status, 200)
                    self.assertIn("sha256-", r.headers["Content-Security-Policy"])
                    self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
                with self.assertRaises(urllib.error.HTTPError) as e:
                    urllib.request.urlopen(base + "/.auth/login/github", timeout=10)
                self.assertEqual(e.exception.code, 404)
            finally:
                httpd.shutdown()
                httpd.server_close()


if __name__ == "__main__":
    unittest.main()
