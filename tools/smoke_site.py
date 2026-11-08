#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Smoke check of a deployed showcase (or the local server).

  python tools/smoke_site.py --url https://<site> [--auth entra|none]

entra: the landing page and the blueprint redirect to the Microsoft Entra sign-in; GitHub sign-in is off.
none : the landing page, the blueprint and the catalogue answer 200 with the security headers.
Standard library only; follows no redirects.
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

NEEDED = ("x-content-type-options", "referrer-policy", "x-frame-options")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url: str):
    opener = urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(urllib.request.Request(url, method="GET"), timeout=30)
        return r.status, {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", required=True)
    ap.add_argument("--auth", choices=("entra", "none"), default="entra")
    a = ap.parse_args(argv)
    base = a.url.rstrip("/")
    problems = []
    for path in ("/", "/blueprint.html", "/identity-catalogue.html"):
        status, headers = fetch(base + path)
        if a.auth == "entra":
            ok = status in (301, 302, 401) and (status == 401 or "/.auth/login/aad" in headers.get("location", ""))
        else:
            ok = status == 200 and all(h in headers for h in NEEDED) and "content-security-policy" in headers
        print(f"{'ok  ' if ok else 'FAIL'} {status} {path}")
        if not ok:
            problems.append(path)
    if a.auth == "entra":
        status, _ = fetch(base + "/.auth/login/github")
        print(f"{'ok  ' if status == 404 else 'FAIL'} {status} /.auth/login/github (must be off)")
        if status != 404:
            problems.append("/.auth/login/github")
    print("smoke check passed" if not problems else f"smoke check failed: {', '.join(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
