"""Showcase site build (security headers, sign-in) and the local server that applies them."""
from __future__ import annotations

import base64
import hashlib
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

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
