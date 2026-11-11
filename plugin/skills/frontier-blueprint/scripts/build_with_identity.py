#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Builds the Frontier Company Blueprint HTML and the agent identity kit together, in one step, and (with --value and
--finops) the business value case and the FinOps model.

Usage:
  python build_with_identity.py --data blueprint.json --out-dir <folder>
         [--brand brand.json | --theme <customer deck or template: .pptx .potx .docx .dotx .xlsx .thmx>]
         [--identity-config agent-identity.json --palette palette.json]
         [--prefix cal] [--po "D1=Sales,D2=Procurement"] [--envs DEV,TEST,PROD]
         [--audience internal|customer] [--html "<Customer> - Frontier Company Blueprint.html"]
         [--save-normalized blueprint.normalized.json] [--report build-report.json] [--no-png] [--no-identity]
         [--value value.json] [--finops finops.json]

Steps (the identity steps run the frontier-agent-identity skill installed next to this skill):
  1. Brand: --brand as given, or the Office theme read from --theme; without either, the blueprint colours (flagged).
  2. Identity proposal: names, colours and glyphs seeded from the blueprint (skipped with --identity-config).
  3. Kit: names, icons per environment, cards, catalogue, scripts and pipelines; validated, tested and zipped.
  4. Blueprint: identity written into every agent; journey colours from the identity palette.
  5. Value and FinOps (when given): copied to <out-dir>/value-finops/, calculated (finops_calc.py, value_calc.py) and
     written into the blueprint (apply_finops.py, apply_value.py); the inputs are never changed.
  6. HTML: the blueprint with the Agent identity page below Agents, business value in Use cases and the FinOps page.
Prints a JSON summary. If an identity step fails, the blueprint is still built, without identity, and the
summary says why.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess  # nosec B404 - runs the plugin's own scripts with fixed arguments, never a shell
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ID_SCRIPTS = HERE.parents[1] / "frontier-agent-identity" / "scripts"
FIN_SCRIPTS = HERE.parents[1] / "frontier-finops" / "scripts"
VAL_SCRIPTS = HERE.parents[1] / "frontier-value-case" / "scripts"
ONT_SCRIPTS = HERE.parents[1] / "frontier-process" / "scripts"


class IdentityError(Exception):
    pass


def run(script: Path, *args) -> tuple[int, str, str]:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, str(script), *[str(x) for x in args]],  # nosec B603 - fixed local script, no shell
                       capture_output=True, text=True, check=False, env=env)
    return p.returncode, p.stdout, p.stderr


def summary_json(text: str):
    """The JSON object a script printed as its summary (the first '{' line that parses to the end)."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.lstrip().startswith("{"):
            try:
                return json.loads("\n".join(lines[i:]))
            except json.JSONDecodeError:
                continue
    return None


def slugify(s: str) -> str:
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "customer"


def build_identity(a, out: Path, short: str, slug: str, summary: dict) -> Path:
    if not (ID_SCRIPTS / "make_kit.py").is_file():
        raise IdentityError("the frontier-agent-identity skill is not installed next to frontier-blueprint")
    work = out / "identity"
    work.mkdir(parents=True, exist_ok=True)
    brand = Path(a.brand) if a.brand else None
    if a.theme and not brand:
        brand = work / "brand.json"
        code, _, err = run(ID_SCRIPTS / "read_office_theme.py", a.theme, "--out", brand, "--short", short)
        if code:
            summary["notes"].append(f"Office theme not read ({err.strip()[-200:]}); journey colours come from the blueprint")
            brand = None
    if a.identity_config:
        if not a.palette:
            raise IdentityError("--identity-config needs --palette")
        cfg, pal, seeded = Path(a.identity_config), Path(a.palette), False
    else:
        cdir = work / "config"
        args = ["--blueprint", a.data, "--out-dir", cdir]
        for flag, value in (("--brand", brand), ("--prefix", a.prefix), ("--po", a.po), ("--envs", a.envs)):
            if value:
                args += [flag, value]
        code, so, err = run(ID_SCRIPTS / "seed_identity.py", *args)
        if code:
            raise IdentityError("seeding the identity failed: " + (err.strip() or so.strip())[-300:])
        cfg, pal, seeded = cdir / "agent-identity.json", cdir / "palette.json", True
        summary["seed_report"] = str(cdir / "seed-report.md")
        if not brand:
            summary["notes"].append("No brand file: journey colours come from the blueprint. Collect the customer's Office theme and build again.")
    config = json.loads(cfg.read_text(encoding="utf-8"))
    ver = ".".join(str(config.get("version", "1.0.0")).split(".")[:2])
    kit = work / f"{slug}-agent-identity"
    zipname = f"{short} - agent identity package v{ver}"
    args = ["--config", cfg, "--palette", pal, "--out", kit, "--zip", zipname] + (["--no-png"] if a.no_png else [])
    code, so, err = run(ID_SCRIPTS / "make_kit.py", *args)
    res = summary_json(so) or {}
    if code or (res.get("validation") or {}).get("errors"):
        raise IdentityError("the identity kit did not validate: " + json.dumps(res.get("validation") or err.strip()[-300:])[:400])
    bpi = work / f"{slug}-blueprint-identity.json"
    code, so, err = run(ID_SCRIPTS / "apply_identity.py", "--blueprint", a.data, "--kit", kit, "--out", bpi,
                        "--colours", "--package", zipname + ".zip")
    if code:
        raise IdentityError("writing the identity into the blueprint failed: " + err.strip()[-300:])
    applied = summary_json(so) or {}
    summary["identity"] = {"kit": str(kit), "zip": (res.get("zip") or {}).get("path"), "catalogue": str(kit / "catalog.html"),
                           "agents": res.get("agents"), "validation": res.get("validation"), "tests": res.get("tests"),
                           "png": res.get("png"), "matched": applied.get("matched"), "without_identity": applied.get("without_identity"),
                           "seeded": seeded, "status": config.get("status"), "blueprint_data": str(bpi)}
    return bpi


def preview_preflight(a, data: Path, *, acknowledge_finops_preview: bool = False) -> dict | None:
    """Refuse before identity, output directories or model copies are created."""
    fin = None
    if a.finops:
        helper_path = FIN_SCRIPTS / "finops_preview.py"
        if not helper_path.is_file():
            raise ValueError("Requested Preview requires frontier-finops/scripts/finops_preview.py; "
                             "install the optional frontier-finops skill next to frontier-blueprint")
        spec = importlib.util.spec_from_file_location("blueprint_finops_preview", helper_path)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        helper.require_preview_ack(acknowledge_finops_preview)
        for name in ("finops_calc.py", "apply_finops.py"):
            if not (FIN_SCRIPTS / name).is_file():
                raise ValueError(f"Requested Preview requires frontier-finops/scripts/{name}; reinstall the optional skill")
        fin = json.loads(Path(a.finops).read_text(encoding="utf-8"))
        if not isinstance(fin, dict):
            raise ValueError("finops input must be an object")
        preview = helper.preview_metadata(acknowledge_finops_preview, operation="blueprint-chain",
                                          finops=fin, inherited=fin.get("finops_preview", {}))
    else:
        preview = None
    if a.value:
        path = VAL_SCRIPTS / "value_calc.py"
        if not path.is_file():
            raise ValueError("Requested value case requires frontier-value-case; install the skill next to frontier-blueprint")
        # Value owns legacy dependency detection. Loading value does not load
        # FinOps unless that particular value/blueprint actually consumes it.
        previous = sys.path[:]
        try:
            sys.path.insert(0, str(VAL_SCRIPTS))
            spec = importlib.util.spec_from_file_location("blueprint_value_preview", path)
            value_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(value_module)
        finally:
            sys.path[:] = previous
        value = json.loads(Path(a.value).read_text(encoding="utf-8"))
        preview = value_module.preview_for(
            value, fin=fin, blueprint=json.loads(data.read_text(encoding="utf-8")),
            acknowledge_finops_preview=acknowledge_finops_preview, operation="blueprint-chain")
        if fin is None and value_module.has_finops_dependency(value):
            raise ValueError("Preview-derived value requires --finops with its source cost model; "
                             "acknowledgement alone cannot replace the missing source")
    return preview


def build_value_finops(a, data: Path, out: Path, summary: dict,
                       *, acknowledge_finops_preview: bool = False) -> Path:
    """Calculates the FinOps model and the value case on copies and writes both into the blueprint data."""
    import shutil
    preview = preview_preflight(a, data, acknowledge_finops_preview=acknowledge_finops_preview)
    flags = ["--acknowledge-finops-preview"] if preview else []
    work = out / "value-finops"
    work.mkdir(parents=True, exist_ok=True)
    fin = val = None
    if a.finops:
        fin = work / Path(a.finops).name
        shutil.copyfile(a.finops, fin)
    if a.value:
        if not (VAL_SCRIPTS / "value_calc.py").is_file():
            summary["notes"].append("Value case not built: the frontier-value-case skill is not installed next to frontier-blueprint")
        else:
            val = work / Path(a.value).name
            shutil.copyfile(a.value, val)
    if fin:
        code, so, err = run(FIN_SCRIPTS / "finops_calc.py", "--finops", fin, *(["--value", val] if val else []), *flags)
        summary["finops"] = summary_json(so) or {"status": "failed", "detail": err.strip()[-400:]}
        if code:
            raise ValueError("FinOps model not calculated: " + (err.strip() or so.strip()))
    if val:
        code, so, err = run(VAL_SCRIPTS / "value_calc.py", "--value", val, *(["--finops", fin] if fin else []), *flags)
        summary["value"] = summary_json(so) or {"status": "failed", "detail": err.strip()[-400:]}
        if code:
            if preview:
                raise ValueError("Preview-dependent value not calculated: " + (err.strip() or so.strip()))
            summary["notes"].append("Value case not calculated: " + err.strip()[-300:])
            val = None
    current, target = data, work / "blueprint-value-finops.json"
    if fin:
        code, _, err = run(FIN_SCRIPTS / "apply_finops.py", "--blueprint", current, "--finops", fin, *(["--value", val] if val else []), "--out", target, *flags)
        if code:
            raise ValueError("FinOps model not applied: " + err.strip())
        else:
            current = target
    if val:
        code, _, err = run(VAL_SCRIPTS / "apply_value.py", "--blueprint", current, "--value", val, "--out", target, *flags)
        if code:
            if preview:
                raise ValueError("Preview-dependent value not applied: " + err.strip())
            summary["notes"].append("Business value left out: " + err.strip()[-300:])
        else:
            current = target
    summary["value_finops"] = {"folder": str(work), "value": str(val) if val else None, "finops": str(fin) if fin else None}
    if preview:
        summary["finops_preview"] = preview
    return current


def build_ontology(a, data: Path, out: Path, summary: dict) -> Path:
    """Build requested process artifacts without invoking value or FinOps."""
    if not (ONT_SCRIPTS / "apply_ontology.py").is_file():
        summary["notes"].append("Ontology left out: frontier-process is not installed next to frontier-blueprint")
        summary["ontology"] = {"status": "failed"}
        return data
    work = out / "ontology"
    audience = a.audience or str((json.loads(data.read_text(encoding="utf-8")).get("meta") or {}).get("audience") or "internal")
    code, so, err = run(ONT_SCRIPTS / "build_ontology.py", "--ontology", a.ontology, "--blueprint", data,
                        "--out-dir", work, "--audience", audience)
    res = summary_json(so) or {"status": "failed", "detail": err.strip()[-400:]}
    summary["ontology"] = {"folder": str(work), "status": res.get("status"), "stats": res.get("stats"),
                           "errors": res.get("errors"), "warnings": res.get("warnings") or []}
    if code:
        summary["notes"].append("Ontology not built: see ontology.errors and warnings")
        return data
    target = work / "blueprint-ontology.json"
    with tempfile.TemporaryDirectory() as directory:
        if audience == "customer":
            # The apply intermediate is also an exported JSON file. Project its
            # blueprint source now, not only when the final HTML is rendered.
            projected = Path(directory) / "customer-blueprint.json"
            code, _, err = run(HERE / "build_blueprint.py", "--data", data, "--audience", "customer",
                                "--save-normalized", projected, "--no-product-icons")
            if code:
                summary["ontology"]["status"] = "failed"
                summary["notes"].append("Customer blueprint projection failed: " + err.strip()[-300:])
                return data
            data = projected
        code, _, err = run(ONT_SCRIPTS / "apply_ontology.py", "--blueprint", data,
                            "--ontology", work / "ontology.normalized.json", "--out", target)
    if code:
        summary["ontology"]["status"] = "failed"
        summary["notes"].append("Ontology not applied: " + err.strip()[-300:])
        return data
    return target


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="blueprint JSON")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--brand", help="brand file (read_office_theme.py output or hand-made)")
    ap.add_argument("--theme", help="customer-authored Office file to read the theme colours from")
    ap.add_argument("--identity-config", help="reviewed agent-identity.json (skips seeding)")
    ap.add_argument("--palette", help="palette.json that belongs to --identity-config")
    ap.add_argument("--prefix", help="Power Platform publisher prefix for the proposal")
    ap.add_argument("--po", help='PO token per journey, e.g. "D1=Sales,D2=Procurement"')
    ap.add_argument("--envs", help="ordered environments, production last (default DEV,TEST,PROD)")
    ap.add_argument("--audience", choices=("internal", "customer"))
    ap.add_argument("--html", help="file name of the blueprint HTML")
    ap.add_argument("--save-normalized", help="passed to build_blueprint.py: the canonical blueprint JSON for the next version")
    ap.add_argument("--report", help="passed to build_blueprint.py: build report JSON")
    ap.add_argument("--no-png", action="store_true", help="skip PNG copies of cards and visuals")
    ap.add_argument("--no-identity", action="store_true", help="build the blueprint without the identity kit")
    ap.add_argument("--value", help="value case (frontier-value/1.0): business value in Use cases and the matrix")
    ap.add_argument("--finops", help="FinOps model (frontier-finops/1.0): the FinOps page")
    ap.add_argument("--acknowledge-finops-preview", action="store_true", help="explicit caller assertion for this one action chain, not approval")
    ap.add_argument("--ontology", help="process ontology (frontier-ontology/1.0): local model, Turtle and design artifacts")
    a = ap.parse_args(argv)
    try:
        if a.value or a.finops:
            preview_preflight(a, Path(a.data), acknowledge_finops_preview=a.acknowledge_finops_preview)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bp = json.loads(Path(a.data).read_text(encoding="utf-8"))
    meta = bp.get("meta") or {}
    short = str(meta.get("short") or str(meta.get("customer") or "Customer").split(" ")[0])
    html = out / (a.html or f"{short} - Frontier Company Blueprint.html")
    summary = {"html": str(html), "identity": None, "notes": []}
    data = Path(a.data)
    if not a.no_identity:
        try:
            data = build_identity(a, out, short, slugify(short), summary)
        except IdentityError as exc:
            summary["notes"].append(f"Identity kit not built: {exc}. The blueprint was built without identity.")
    if a.value or a.finops:
        try:
            data = build_value_finops(a, Path(data), out, summary,
                                      acknowledge_finops_preview=a.acknowledge_finops_preview)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
    if a.ontology:
        data = build_ontology(a, Path(data), out, summary)
        if summary["ontology"]["status"] == "failed":
            print(json.dumps(summary, indent=1, ensure_ascii=False))
            return 1
    args = ["--data", data, "--out", html] + (["--audience", a.audience] if a.audience else [])
    for flag, value in (("--save-normalized", a.save_normalized), ("--report", a.report)):
        if value:
            args += [flag, value]
    code, so, err = run(HERE / "build_blueprint.py", *args)
    summary["blueprint"] = summary_json(so) or {"status": "failed", "detail": err.strip()[-600:]}
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0 if code == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
