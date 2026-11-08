#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Serve the built showcase locally with the same headers as Azure Static Web Apps.

  python tools/serve_site.py [--dir build/site] [--port 4173]

Applies globalHeaders and the matching route headers and status codes from staticwebapp.config.json, so
browser tests see the real Content-Security-Policy. Sign-in rules (allowedRoles) are not emulated: the
server binds to 127.0.0.1 only. Standard library only.
"""
from __future__ import annotations

import argparse
import functools
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import SITE_DIR  # noqa: E402


def match(route: str, path: str) -> bool:
    if route.endswith("/*"):
        return path.startswith(route[:-1]) or path == route[:-2]
    return route == path


def make_handler(root: Path):
    cfg_path = root / "staticwebapp.config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}

    class Handler(SimpleHTTPRequestHandler):
        def _route(self):
            path = self.path.split("?", 1)[0]
            for r in cfg.get("routes", []):
                if match(r.get("route", ""), path):
                    return r
            return {}

        def end_headers(self):
            for k, v in cfg.get("globalHeaders", {}).items():
                self.send_header(k, v)
            for k, v in self._route().get("headers", {}).items():
                self.send_header(k, v)
            super().end_headers()

        def do_GET(self):  # noqa: N802
            status = self._route().get("statusCode")
            if status:
                self.send_error(int(status))
                return
            super().do_GET()

        def log_message(self, fmt, *args):  # quiet
            pass

    return functools.partial(Handler, directory=str(root))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=str(SITE_DIR))
    ap.add_argument("--port", type=int, default=4173)
    a = ap.parse_args(argv)
    root = Path(a.dir)
    if not (root / "index.html").exists():
        print(f"{root} has no index.html - run: python tools/dev.py site")
        return 1
    httpd = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(root))
    print(f"serving {root} on http://127.0.0.1:{a.port}/", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
