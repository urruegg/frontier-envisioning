#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Build the Caldova demo with portable text/archive output and complete identity assets.

  python tools/build_demo.py [--out build/demo] [--no-png]

Runs the plugin's one-step build (frontier-blueprint/scripts/build_with_identity.py) on the Caldova
examples with the reviewed identity config and palette, the value case and the FinOps model - the same
inputs as the published 1.4.0 demo, so tools/verify_release.py can compare the results byte for byte.
Text is written as LF, and identity ZIP entries use stable ordering and Unix creator metadata.
The 1.4.0 baseline uses verified frozen raster inputs guarded by every generated non-raster file.
Other versions require successful card/visual conversion; --no-png is an explicitly SVG-only
development variant, not release reproduction. Full wrapper evidence is saved as build-report.json.
For released versions, the FinOps rate-age calculation uses the recorded release date rather
than the wall clock. The plugin's explicit --today input is used; verification hashes are unchanged.
Caldova Industrial AG is fictitious.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import demo_raster  # noqa: E402
from fe_lib import DEMO_DIR, DEMO_HTML_NAME, ROOT, SKILLS, TEXT_SUFFIXES, call_main, load_module, plugin_version, sha256_bytes  # noqa: E402

EXAMPLES = {
    "data": SKILLS / "frontier-blueprint/examples/caldova-blueprint.json",
    "identity-config": SKILLS / "frontier-agent-identity/examples/caldova-agent-identity.json",
    "palette": SKILLS / "frontier-agent-identity/examples/caldova-palette.json",
    "value": SKILLS / "frontier-value-case/examples/caldova-value.json",
    "finops": SKILLS / "frontier-finops/examples/caldova-finops.json",
}


def canonicalise_outputs(out: Path, archive_path: Path) -> None:
    for path in out.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            data = path.read_bytes()
            lf = data.replace(b"\r\n", b"\n")
            if lf != data:
                path.write_bytes(lf)
    with zipfile.ZipFile(archive_path) as archive:
        comment = archive.comment
        entries = [(info, archive.read(info)) for info in archive.infolist()]
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.comment = comment
        for info, data in sorted(entries, key=lambda entry: entry[0].filename):
            info.create_system = 3
            if Path(info.filename).suffix.lower() in TEXT_SUFFIXES:
                data = data.replace(b"\r\n", b"\n")
            archive.writestr(info, data)


def build_at_release_date(out: Path, summary: dict, day: str) -> int:
    model = summary["value_finops"]
    data = Path(model["folder"]) / "blueprint-value-finops.json"
    args = ["--blueprint", str(data), "--finops", model["finops"], "--today", day, "--out", str(data)]
    if model.get("value"):
        args += ["--value", model["value"]]
    finops = load_module(SKILLS / "frontier-finops" / "scripts" / "apply_finops.py", "fe_demo_finops_date")
    code, output = call_main(finops, args)
    if code:
        print(output)
        return code
    blueprint = load_module(SKILLS / "frontier-blueprint" / "scripts" / "build_blueprint.py", "fe_demo_blueprint_date")
    code, output = call_main(blueprint, ["--data", str(data), "--out", str(out / DEMO_HTML_NAME)])
    if code:
        print(output)
    return code


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(DEMO_DIR))
    ap.add_argument("--no-png", action="store_true", help="skip PNG copies (faster; the identity zip then differs from the release)")
    a = ap.parse_args(argv)
    frozen_profile = not a.no_png and plugin_version() in demo_raster.SUPPORTED_VERSIONS | demo_raster.PREVIEW_VERSIONS
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    cmd = [sys.executable, "-B", str(SKILLS / "frontier-blueprint/scripts/build_with_identity.py"),
           "--out-dir", str(out), "--html", DEMO_HTML_NAME]
    for key, path in EXAMPLES.items():
        cmd += [f"--{key}", str(path)]
    if a.no_png or frozen_profile:
        cmd.append("--no-png")
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode:
        print(proc.stdout[-2000:], proc.stderr[-2000:])
        print("demo build failed")
        return proc.returncode
    i = proc.stdout.find("{")
    if i < 0:
        print("ERROR: demo wrapper did not return a JSON summary")
        return 1
    summary = json.loads(proc.stdout[i:])
    manifest = ROOT / "releases" / plugin_version() / "manifest.json"
    if not a.no_png and manifest.is_file():
        day = json.loads(manifest.read_text(encoding="utf-8"))["date"]
        if not (summary.get("value_finops") or {}).get("finops"):
            print("ERROR: released demo did not produce its FinOps model")
            return 1
        if build_at_release_date(out, summary, day):
            print("ERROR: released demo model generation failed")
            return 1
        summary["baseline_date"] = day
    html = out / DEMO_HTML_NAME
    identity = summary.get("identity")
    if not html.is_file() or not isinstance(identity, dict):
        print("ERROR: demo wrapper did not produce the blueprint and identity kit")
        return 1
    paths = {}
    for name in ("kit", "zip", "catalogue"):
        value = identity.get(name)
        if not isinstance(value, str) or not value or not Path(value).exists():
            print(f"ERROR: identity {name} artifact is missing")
            return 1
        paths[name] = Path(value)
    canonicalise_outputs(out, paths["zip"])
    summary["variant"] = "svg-only" if a.no_png else "full"
    summary["status"] = "incomplete"
    (out / "build-report.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    if identity.get("tests") != "passed" or (identity.get("validation") or {}).get("errors") or identity.get("without_identity"):
        print("ERROR: identity kit tests, validation or agent matching did not complete")
        return 1
    if frozen_profile:
        try:
            rasters = demo_raster.replay(paths["kit"], version=plugin_version())
            maker = load_module(SKILLS / "frontier-agent-identity" / "scripts" / "make_kit.py", "fe_demo_kit")
            builder = maker.load_kit_module(paths["kit"] / "scripts", "build_identity_assets")
            docs = maker.load_kit_module(paths["kit"] / "scripts", "identity_docs")
            config = json.loads((paths["kit"] / "config" / "agent-identity.json").read_text(encoding="utf-8"))
            palette = json.loads((paths["kit"] / "config" / "palette.json").read_text(encoding="utf-8"))
            readme = docs.readme_md(config, palette, builder.by_journey(config, palette), True).encode("utf-8")
            if sha256_bytes(readme) != rasters["readme_sha256"]:
                raise demo_raster.RasterProfileError("regenerated raster-mode README differs from the release")
            (paths["kit"] / "README.md").write_bytes(readme)
            maker.zip_dir(paths["kit"], paths["zip"])
            canonicalise_outputs(out, paths["zip"])
            identity["png"] = rasters
        except demo_raster.RasterProfileError as exc:
            print(f"ERROR: {exc}")
            return 1
    if not a.no_png:
        targets = list(paths["kit"].glob("agents/*/identity/card.svg")) + list((paths["kit"] / "visuals").glob("*.svg"))
        missing = sum(not path.with_suffix(".png").is_file() for path in targets)
        png = identity.get("png") or {}
        completed = png.get("restored_visuals", 0) if frozen_profile else png.get("converted", 0)
        if not targets or missing or completed != len(targets) or not png.get("method"):
            print(f"ERROR: identity raster conversion incomplete: {completed}/{len(targets)} reported, "
                  f"{missing} missing PNGs; converter: {png.get('method') or 'unavailable'}. "
                  "Restore the recorded release renderer; --no-png is only an SVG-only development variant.")
            return 1
    summary["status"] = "built"
    (out / "build-report.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8", newline="\n")
    stats = (summary.get("blueprint") or {}).get("stats", {})
    print(json.dumps({"out": str(out), "html": str(html), "stats": stats, "variant": summary["variant"],
                      "png": identity.get("png"), "report": str(out / "build-report.json")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
