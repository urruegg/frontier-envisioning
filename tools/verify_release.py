#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Compare freshly built artefacts with a release manifest (releases/<version>/manifest.json).

  python tools/verify_release.py [--manifest releases/1.4.0/manifest.json] [--force]

A release manifest records the SHA-256 of every published artefact. Building the same version from the
repository must give the same bytes: the plugin package, the identity kit and the catalogue exactly, the
demo blueprint after normalising its build date ("generated"). Run tools/build_package.py and
tools/build_demo.py first (python tools/dev.py check does both).

By default the manifest of the current plugin version is used. When the plugin version has no manifest
(work towards the next release), the check is skipped - unless --force names a manifest explicitly.

  python tools/verify_release.py --write release-manifest.json
      write a manifest for the current version from the built artefacts (the release workflow attaches it;
      the release manager commits it as releases/<version>/manifest.json after publishing)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import DEMO_HTML_NAME, ROOT, plugin_version, sha256_bytes  # noqa: E402

GENERATED = re.compile(rb'"generated":"\d{4}-\d{2}-\d{2}"')


def normalise(data: bytes, how: str | None) -> bytes:
    if how == "generated-date":
        return GENERATED.sub(b'"generated":"0000-00-00"', data)
    return data


def verify(manifest: dict, base: Path = ROOT) -> list[str]:
    problems = []
    for art in manifest.get("artefacts", []):
        path = base / art["build_path"]
        if not path.exists():
            problems.append(f"missing: {art['build_path']} (build it first)")
            continue
        data = path.read_bytes()
        if art.get("normalise"):
            got = sha256_bytes(normalise(data, art["normalise"]))
            want = art["sha256_normalised"]
        else:
            got, want = sha256_bytes(data), art["sha256"]
        status = "ok" if got == want else "DIFFERENT"
        print(f"{status:9} {art['name']}")
        if got != want:
            problems.append(f"{art['name']}: sha256 {got} != released {want}")
    return problems


def standard_artefacts(version: str) -> list[tuple[str, str, str | None]]:
    """(published name, build path, normalisation) of the artefacts every release carries."""
    return [
        (f"frontier-envisioning-plugin-{version}.zip", f"dist/frontier-envisioning-plugin-{version}.zip", None),
        (DEMO_HTML_NAME, f"build/demo/{DEMO_HTML_NAME}", "generated-date"),
        ("Caldova - agent identity package v1.0.zip", "build/demo/identity/Caldova - agent identity package v1.0.zip", None),
        ("Caldova - agent identity catalogue.html", "build/demo/identity/caldova-agent-identity/catalog.html", None),
    ]


def write_manifest(out: Path, version: str) -> int:
    import datetime as dt
    arts = []
    for name, build_path, how in standard_artefacts(version):
        data = (ROOT / build_path).read_bytes()
        art = {"name": name, "build_path": build_path, "bytes": len(data), "sha256": sha256_bytes(data)}
        if how:
            art["normalise"] = how
            art["sha256_normalised"] = sha256_bytes(normalise(data, how))
        arts.append(art)
    manifest = {"schema": "frontier-release-manifest/1.0", "version": version, "date": dt.date.today().isoformat(),
                "provenance": "Built by the release workflow from the tag v" + version + ".", "artefacts": arts, "not_reproduced": []}
    out.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"manifest written: {out}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", help="release manifest (default: releases/<plugin version>/manifest.json)")
    ap.add_argument("--force", action="store_true", help="verify even when the manifest is for another version")
    ap.add_argument("--write", help="write a manifest for the current version from the built artefacts")
    a = ap.parse_args(argv)
    version = plugin_version()
    if a.write:
        return write_manifest(Path(a.write), version)
    path = Path(a.manifest) if a.manifest else ROOT / "releases" / version / "manifest.json"
    if not path.exists():
        print(f"no release manifest for {version}: nothing to compare (work towards the next release)")
        return 0
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("version") != version and not a.force:
        print(f"manifest is for {manifest.get('version')}, the plugin is {version}: skipped")
        return 0
    problems = verify(manifest)
    for p in problems:
        print("ERROR " + p)
    if problems and manifest.get("version") == version:
        print(f"The sources no longer reproduce the released {version}. A released version is immutable: "
              "bump the version for the next release (python tools/dev.py bump X.Y.Z) before changing the plugin.")
    print(f"release {manifest.get('version')}: {len(manifest.get('artefacts', [])) - len(problems)} of "
          f"{len(manifest.get('artefacts', []))} artefacts reproduced")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
