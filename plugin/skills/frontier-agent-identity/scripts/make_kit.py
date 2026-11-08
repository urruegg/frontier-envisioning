#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Assembles a customer's agent identity package from the kit template and a reviewed config.

Usage:
  python make_kit.py --config agent-identity.json --palette palette.json --out working/identity/<slug>/<kit-folder>
         [--logo logo.png --logo-aspect 3.2] [--identity-root identity] [--no-png] [--zip "<Customer> - agent identity package v1.0"]

Steps: copy the kit (scripts, glyph library, tests, pipelines, schema) -> write the config -> build names,
icons, cards, visuals, docs and catalogue -> validate (0 errors required) -> run the unit tests -> zip.
Prints a JSON summary. Standard library only (PNG copies of cards and visuals use an SVG converter when
one is installed).
"""
from __future__ import annotations

import argparse
import contextlib
import importlib
import io
import json
import shutil
import subprocess  # nosec B404 - runs the kit's unit tests with the current interpreter
import sys
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "kit"
FIXED_DATE = (2026, 10, 30, 0, 0, 0)


def load_kit_module(scripts: Path, name: str):
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    for m in ("raster", "identity_lib", "identity_visuals", "identity_docs", name):
        if m in sys.modules and not str(getattr(sys.modules[m], "__file__", "")).startswith(str(scripts)):
            del sys.modules[m]
    return importlib.import_module(name)


def zip_dir(folder: Path, target: Path) -> None:
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                info = zipfile.ZipInfo(f"{folder.name}/{p.relative_to(folder).as_posix()}", date_time=FIXED_DATE)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, p.read_bytes())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--palette", required=True)
    ap.add_argument("--out", required=True, help="kit folder to create (replaced if it exists)")
    ap.add_argument("--logo", help="customer logo PNG (use only where the customer's brand rules allow it)")
    ap.add_argument("--logo-aspect", type=float, default=3.2, help="logo width / height")
    ap.add_argument("--identity-root", default=None, help="where the package will live in the customer's repository")
    ap.add_argument("--no-png", action="store_true", help="skip PNG copies of cards and visuals")
    ap.add_argument("--zip", help="zip name without extension; written next to the kit folder")
    a = ap.parse_args(argv)
    out = Path(a.out).resolve()
    if out.exists():
        shutil.rmtree(out)
    (out / "config").mkdir(parents=True)
    shutil.copytree(KIT / "scripts", out / "scripts", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(KIT / "pipelines", out / "pipelines")
    shutil.copy2(KIT / "config" / "agent-identity.schema.json", out / "config" / "agent-identity.schema.json")
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))
    palette = json.loads(Path(a.palette).read_text(encoding="utf-8"))
    root_in_repo = a.identity_root or (cfg.get("repository") or {}).get("identityRoot") or "identity"
    cfg.setdefault("repository", {})["identityRoot"] = root_in_repo
    if a.logo:
        (out / "brand").mkdir(parents=True, exist_ok=True)
        shutil.copy2(a.logo, out / "brand" / "logo.png")
        palette["logo"] = dict(palette.get("logo") or {}, file="brand/logo.png", aspect=a.logo_aspect)
    elif palette.get("logo") and not (out / palette["logo"].get("file", "-")).exists():
        palette["logo"] = None
    (out / "config" / "agent-identity.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "config" / "palette.json").write_text(json.dumps(palette, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for yml in (out / "pipelines").rglob("*.yml"):
        yml.write_text(yml.read_text(encoding="utf-8").replace("__IDENTITY_ROOT__", root_in_repo), encoding="utf-8")
    scripts = out / "scripts"
    build = load_kit_module(scripts, "build_identity_assets")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = build.main(["--root", str(out)] + (["--no-png"] if a.no_png else []))
    if code != 0:
        print(buf.getvalue())
        return code
    built = json.loads(buf.getvalue().strip().splitlines()[-1])
    validate = load_kit_module(scripts, "validate_identity")
    report = validate.validate(out)
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(scripts / "tests")],  # nosec B603
                           capture_output=True, text=True, cwd=str(out))
    for p in out.rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)
    summary = {"kit": str(out), "agents": built["agents"], "journeys": built["journeys"], "png": built["png"],
               "validation": {"errors": report["errors"], "warnings": report["warnings"]},
               "tests": "passed" if tests.returncode == 0 else "failed",
               "files": sum(1 for p in out.rglob("*") if p.is_file())}
    if tests.returncode != 0:
        summary["testOutput"] = tests.stderr[-1500:]
    ok = not report["errors"] and tests.returncode == 0
    if a.zip and ok:
        target = out.parent / f"{a.zip}.zip"
        zip_dir(out, target)
        summary["zip"] = {"path": str(target), "bytes": target.stat().st_size}
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
