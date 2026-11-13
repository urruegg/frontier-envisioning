#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Assemble the showcase site for Azure Static Web Apps from the built demo.

  python tools/build_site.py [--out build/site] [--auth none|entra] [--tenant-id GUID] [--demo build/demo]
         [--preview-demo build/demo-finops-preview] [--baseline-demo build/demo-agent-finops-preview]

Output:
  index.html                 landing page (site/index.html with version, date and commit filled in)
  blueprint.html             the Caldova blueprint (from build/demo)
  identity-catalogue.html    the agent identity catalogue (from build/demo)
  blueprint-preview.html    only when an explicit developer Preview fixture is supplied
  blueprint-baseline.html   only when an explicit synthetic baseline fixture is supplied
  downloads/<plugin zip>     the plugin package, when dist/ holds it
  staticwebapp.config.json   routes, security headers and sign-in

Security: every HTML page gets a Content-Security-Policy that allows exactly its own inline scripts (by
SHA-256 hash), no external resources and no framing. With --auth entra (the default for deployments)
every route requires a signed-in user of the given Microsoft Entra tenant; the client id and secret are
app settings (AAD_CLIENT_ID, AAD_CLIENT_SECRET) set by the infrastructure, never in this file.
The tenant id may also come from SITE_AUTH_TENANT_ID, the mode from SITE_AUTH_MODE.
FRONTIER_PREVIEW_DEMO explicitly selects the optional browser-test fixture; it does not acknowledge
viewer use or include that fixture in the default distribution.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import DEMO_DIR, DEMO_HTML_NAME, DIST, ROOT, SITE_DIR, load_module, plugin_version  # noqa: E402

GUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
SCRIPT = re.compile(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.S | re.I)
GLOBAL_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Strict-Transport-Security": "max-age=31536000",
}


def csp_for(html: str) -> str:
    """CSP allowing exactly the page's executable inline scripts (JSON data islands are not scripts)."""
    hashes = []
    for m in SCRIPT.finditer(html):
        attrs = m.group("attrs").lower()
        tm = re.search(r'type\s*=\s*["\']?([^"\'\s>]+)', attrs)
        if tm and tm.group(1) not in ("text/javascript", "module", "application/javascript"):
            continue
        if "src=" in attrs:
            raise SystemExit("external scripts are not allowed in the showcase")
        digest = base64.b64encode(hashlib.sha256(m.group("body").encode("utf-8")).digest()).decode()
        hashes.append(f"'sha256-{digest}'")
    script_src = " ".join(sorted(set(hashes))) if hashes else "'none'"
    return ("default-src 'none'; " f"script-src {script_src}; " "style-src 'unsafe-inline'; " "img-src 'self' data: blob:; "
            "font-src 'self' data:; " "connect-src 'none'; " "base-uri 'none'; " "form-action 'none'; " "frame-ancestors 'none'")


def commit_id() -> str:
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha[:7]
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip() or "local"
    except (OSError, subprocess.CalledProcessError):
        return "local"


def build(out: Path, demo: Path, auth: str, tenant: str | None, *, preview_demo: Path | None = None,
          baseline_demo: Path | None = None) -> dict:
    if auth == "entra" and not (tenant and GUID.match(tenant)):
        raise SystemExit("--auth entra needs --tenant-id (a GUID) or SITE_AUTH_TENANT_ID")
    destination = out.resolve()
    for fixture in (demo, preview_demo, baseline_demo):
        if fixture is not None:
            source = fixture.resolve()
            if destination == source or destination in source.parents or source in destination.parents:
                raise SystemExit("site output must not overlap a consumed demo fixture")
    src_html = demo / DEMO_HTML_NAME
    catalogue = demo / "identity" / "caldova-agent-identity" / "catalog.html"
    if not src_html.exists() and demo.resolve() == DEMO_DIR.resolve():
        build_demo = load_module(ROOT / "tools" / "build_demo.py", "build_demo")
        if build_demo.main([]):
            raise SystemExit("the demo build failed")
    for need in (src_html, catalogue):
        if not need.exists():
            raise SystemExit(f"missing {need} - run: python tools/dev.py demo")
    optional_pages = {}
    for name, fixture in (("blueprint-preview.html", preview_demo), ("blueprint-baseline.html", baseline_demo)):
        if fixture is not None:
            fixture_html = fixture / DEMO_HTML_NAME
            if not fixture_html.is_file():
                raise SystemExit(f"missing {fixture_html} - build the explicitly acknowledged Preview fixture first")
            page = fixture_html.read_text(encoding="utf-8")
            csp_for(page)  # preflight before replacing an existing site
            optional_pages[name] = page
    if out.exists():
        shutil.rmtree(out)
    (out / "downloads").mkdir(parents=True)
    version = plugin_version()
    pkg = DIST / f"frontier-envisioning-plugin-{version}.zip"
    pages = {"blueprint.html": src_html.read_text(encoding="utf-8"),
             "identity-catalogue.html": catalogue.read_text(encoding="utf-8")}
    pages.update(optional_pages)
    package_href = "#"
    if pkg.exists():
        shutil.copyfile(pkg, out / "downloads" / pkg.name)
        package_href = f"downloads/{pkg.name}"
    index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
    fill = {"{{VERSION}}": version, "{{BUILD_DATE}}": dt.date.today().isoformat(), "{{COMMIT}}": commit_id(),
            "{{PACKAGE_HREF}}": package_href}
    for k, v in fill.items():
        index = index.replace(k, v)
    if "{{" in index:
        raise SystemExit("unfilled placeholder in site/index.html")
    pages["index.html"] = index
    routes = []
    if auth == "entra":
        routes += [{"route": "/.auth/login/github", "statusCode": 404}, {"route": "/.auth/login/twitter", "statusCode": 404}]
    for name, html in pages.items():
        (out / name).write_text(html, encoding="utf-8", newline="\n")
        route = {"route": "/" + name, "headers": {"Content-Security-Policy": csp_for(html)}}
        routes.append(route)
        if name == "index.html":
            routes.append({"route": "/", "headers": {"Content-Security-Policy": csp_for(html)}})
    routes.append({"route": "/*"})
    if auth == "entra":
        for r in routes:
            if "statusCode" not in r:
                r["allowedRoles"] = ["authenticated"]
    cfg: dict = {"routes": routes, "globalHeaders": GLOBAL_HEADERS,
                 "mimeTypes": {".json": "application/json"}}
    if auth == "entra":
        cfg["responseOverrides"] = {"401": {"redirect": "/.auth/login/aad?post_login_redirect_uri=.referrer", "statusCode": 302}}
        cfg["auth"] = {"identityProviders": {"azureActiveDirectory": {"registration": {
            "openIdIssuer": f"https://login.microsoftonline.com/{tenant}/v2.0",
            "clientIdSettingName": "AAD_CLIENT_ID", "clientSecretSettingName": "AAD_CLIENT_SECRET"}}}}
    (out / "staticwebapp.config.json").write_text(json.dumps(cfg, indent=1) + "\n", encoding="utf-8", newline="\n")
    return {"out": str(out), "auth": auth, "pages": sorted(pages), "package": package_href != "#"}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(SITE_DIR))
    ap.add_argument("--demo", default=str(DEMO_DIR))
    ap.add_argument("--preview-demo", default=os.environ.get("FRONTIER_PREVIEW_DEMO"),
                    help="explicit developer Preview fixture; omitted by default")
    ap.add_argument("--baseline-demo", help="explicit synthetic baseline test fixture; omitted by default")
    ap.add_argument("--auth", choices=("none", "entra"), default=os.environ.get("SITE_AUTH_MODE") or "none")
    ap.add_argument("--tenant-id", default=os.environ.get("SITE_AUTH_TENANT_ID"))
    a = ap.parse_args(argv)
    print(json.dumps(build(Path(a.out), Path(a.demo), a.auth, a.tenant_id,
                           preview_demo=Path(a.preview_demo) if a.preview_demo else None,
                           baseline_demo=Path(a.baseline_demo) if a.baseline_demo else None), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
