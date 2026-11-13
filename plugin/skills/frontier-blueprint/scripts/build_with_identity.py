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
import copy
import io
import importlib.util
import json
import os
import re
import subprocess  # nosec B404 - runs the plugin's own scripts with fixed arguments, never a shell
import sys
import tempfile
import unicodedata
from pathlib import Path
from contextlib import redirect_stdout

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


def identity_component(value):
    """Untrusted identity labels must be filename components, never paths."""
    if (not isinstance(value, str) or not value.strip() or value in {".", ".."}
            or any(c in '<>:"/\\|?*' or unicodedata.category(c) in {"Cc", "Cs"} for c in value)):
        raise IdentityError("Identity filenames require plain components without paths or control characters")
    return value


def identity_layout(a, out, short, slug):
    # Inspect supplied configuration before theme/seed/kit scripts run. The seed
    # command below pins the same documented 1.0.0 version explicitly.
    config = json.loads(Path(a.identity_config).read_text(encoding="utf-8")) if a.identity_config else None
    if config is not None and not isinstance(config, dict):
        raise IdentityError("Identity configuration must be an object")
    identity_component(short)
    identity_component(slug)
    version = identity_component(config.get("version", "1.0.0") if config is not None else "1.0.0")
    ver = identity_component(".".join(version.split(".")[:2]))
    kitname = identity_component(f"{slug}-agent-identity")
    bpiname = identity_component(f"{slug}-blueprint-identity.json")
    zipname = identity_component(f"{short} - agent identity package v{ver}")
    identity_component(zipname + ".zip")
    work = out / "identity"
    kit, bpi = work / kitname, work / bpiname
    files = [kit / "catalog.html", bpi, work / (zipname + ".zip")]
    targets = [work, kit, *files]
    if not a.identity_config:
        files += [work / "config/agent-identity.json", work / "config/palette.json", work / "config/seed-report.md"]
        targets += [work / "config", *files[-3:]]
    if a.theme and not a.brand:
        files.append(work / "brand.json")
        targets.append(files[-1])
    root = out.resolve()
    if any(not path.resolve().is_relative_to(root) for path in targets):
        raise IdentityError("Derived identity destination escapes its owned staging directory")
    inputs = [getattr(a, name, None) for name in ("data", "identity_config", "palette", "brand", "theme")]
    for source in (Path(p).resolve() for p in inputs if p):
        if source.is_relative_to(kit.resolve()) or any(source == target.resolve() for target in files):
            raise IdentityError("Derived identity destination aliases an input")
    return work, kit, bpi, zipname, config


def blueprint_library():
    spec = importlib.util.spec_from_file_location("wrapper_blueprint", HERE / "build_blueprint.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def agent_finops_flags(a):
    """Forward only explicit current-invocation source/date/scope arguments."""
    if not (getattr(a, "agent_finops", None) or getattr(a, "agent_finops_review", None)):
        return []
    flags = []
    for path in getattr(a, "agent_finops", ()) or ():
        flags += ["--agent-finops", path]
    for path in getattr(a, "agent_finops_review", ()) or ():
        flags += ["--agent-finops-review", path]
    for flag, value in (("--as-of", getattr(a, "as_of", None)),
                        ("--customer-scope", getattr(a, "customer_scope", None))):
        if value is not None:
            flags += [flag, value]
    if getattr(a, "acknowledge_finops_preview", False) is True:
        flags.append("--acknowledge-finops-preview")
    return flags


def agent_finops_preflight(a, data, *, acknowledge_finops_preview=False):
    lib = blueprint_library()
    bp = lib.read_document(data)
    baselines = getattr(a, "agent_finops", ()) or ()
    if getattr(a, "finops", None) and (baselines or "agent_finops" in bp):
        raise ValueError("ambiguous legacy/new financial sources: --finops and --agent-finops are mutually exclusive")
    common = {
        "baselines": baselines, "reviews": getattr(a, "agent_finops_review", ()) or (),
        "as_of": getattr(a, "as_of", None),
        "audience": getattr(a, "audience", None) or str((bp.get("meta") or {}).get("audience", "internal")).lower(),
        "customer_scope": getattr(a, "customer_scope", None),
        "acknowledge_finops_preview": acknowledge_finops_preview,
    }
    if baselines and getattr(a, "ontology", None) and acknowledge_finops_preview is True:
        ontology = lib.read_document(a.ontology)
        original = copy.deepcopy(bp)
        original["ontology"] = ontology
        # Shared policy must see the ORIGINAL authored graph before the process
        # applier can drop an invalid consumer or reference. No output effects.
        lib.agent_finops_preflight(original, **common)
        bp = prepare_agent_ontology(bp, ontology)
    value = None
    if baselines and getattr(a, "value", None) and acknowledge_finops_preview is True:
        bp, value = prepare_agent_value(bp, lib.read_document(a.value))
    prepared = lib.agent_finops_preflight(bp, **common)
    if prepared is not None:
        prepared["value"] = value
    return lib, bp, prepared


def value_library(name):
    path = VAL_SCRIPTS / f"{name}.py"
    if not path.is_file():
        raise ValueError("Requested value case requires frontier-value-case; install the skill next to frontier-blueprint")
    previous = sys.path[:]
    try:
        sys.path.insert(0, str(VAL_SCRIPTS))
        spec = importlib.util.spec_from_file_location(f"blueprint_{name}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = previous


def prepare_agent_value(bp, value):
    """Successor only: real ordinary value computation/application, before I/O."""
    calculator = value_library("value_calc")
    if calculator.has_finops_dependency(value):
        raise ValueError("Preview-derived value requires --finops with its legacy cost source; "
                         "new agent baselines cannot replace it")
    document = copy.deepcopy(value)
    applied = copy.deepcopy(bp)
    try:
        document["results"] = calculator.run(document, None, acknowledge_finops_preview=True)
        value_library("apply_value").apply(applied, document, acknowledge_finops_preview=True)
        json.dumps(document, allow_nan=False)
    except (ValueError, KeyError, TypeError):
        raise ValueError("Requested value preflight refused: invalid input or calculation") from None
    return applied, document


def prepare_agent_ontology(bp, ontology):
    if ontology.get("schema") != "frontier-ontology/1.0":
        raise ValueError("unsupported ontology source namespace")
    if not (ONT_SCRIPTS / "apply_ontology.py").is_file():
        raise ValueError("Requested ontology requires frontier-process; install it next to frontier-blueprint")
    previous = sys.path[:]
    try:
        sys.path.insert(0, str(ONT_SCRIPTS))
        spec = importlib.util.spec_from_file_location("finops_process_apply", ONT_SCRIPTS / "apply_ontology.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rep = module.Rep()
        result = module.apply(copy.deepcopy(bp), copy.deepcopy(ontology), rep)
        if rep.errors:
            raise ValueError("Agent FinOps ontology source preflight refused: invalid process model")
        return result
    finally:
        sys.path[:] = previous


def agent_finops_destinations(out, prepared, audience):
    work = out / "agent-finops"
    names = []
    if audience != "customer":
        names += [f"source-{i:03}.json" for i in range(1, len(prepared["sources"]) + 1)]
        names += [f"review-{i:03}.json" for i in range(1, len(prepared["reviews"]) + 1)]
    for i in range(1, len(prepared["sources"]) + 1):
        names += [f"report-{i:03}.json", f"report-{i:03}.md"]
    return [work / name for name in names]


def write_agent_finops(out, prepared, view, audience):
    """Customer folders contain ONLY projected DTOs, never raw working sources."""
    lib = prepared["library"]
    documents = {}
    if audience != "customer":
        for kind, values in (("source", prepared["sources"]), ("review", prepared["reviews"])):
            for i, value in enumerate(values, 1):
                documents[f"{kind}-{i:03}.json"] = lib._json_text(value)
    for i, report in enumerate(view["records"], 1):
        documents[f"report-{i:03}.json"] = lib._json_text(report)
        documents[f"report-{i:03}.md"] = lib.render_markdown(report)
    work = out / "agent-finops"
    work.mkdir(parents=True, exist_ok=True)
    for name, text in documents.items():
        with (work / name).open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)


def successor_inputs(a):
    return [getattr(a, name, None) for name in (
        "data", "value", "ontology", "identity_config", "palette", "brand", "theme"
    )] + list(a.agent_finops) + list(a.agent_finops_review)


def successor_output_preflight(a, inputs, html_name):
    """Reserve a new publication tree; source paths are always read-only."""
    out = Path(a.out_dir)
    if out.exists() and not out.is_dir():
        raise ValueError("Agent FinOps output directory is not available")
    if Path(html_name).name != html_name or html_name in {".", ".."}:
        raise ValueError("Blueprint HTML name must be a filename inside the new output directory")
    for source in (Path(p) for p in inputs if p):
        if source.resolve().is_relative_to(out.resolve()) or source.absolute().is_relative_to(out.absolute()):
            raise ValueError("Agent FinOps inputs must not be inside the reserved output directory")


def publish_successor(a, lib, private_work, summary, inputs):
    """Publish only after ALL components pass, with a complete collision plan.

    Raw source/identity/value intermediates never escape private working storage.
    Identity products were generated from a customer-projected seed; ordinary
    Blueprint intermediates are projected separately AFTER financial validation.
    """
    stage, out = private_work / "artifacts", Path(a.out_dir)
    customer = summary["agent_finops"]["audience"] == "customer"
    value_copy = stage / "value-finops" / "value-source.json"
    plan = []
    for path in sorted(stage.rglob("*")):
        if not path.is_file() or (customer and path == value_copy):
            continue
        content = path.read_bytes()
        if customer and path.suffix == ".json":
            document = lib.read_document(path)
            if document.get("schema") == "frontier-blueprint/1.0":
                rep = lib.Report()
                document = lib.customer_version(document, rep)
                if rep.errors:
                    raise ValueError("Customer intermediate projection refused")
                content = (json.dumps(document, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        plan.append((out / path.relative_to(stage), content))
    for name, target in (("normalized.json", a.save_normalized), ("report.json", a.report)):
        if target:
            path = private_work / name
            document = lib.read_document(path)
            if name == "report.json":
                document["out"] = str(out / summary["html_name"])
                if a.save_normalized:
                    document["normalized"] = str(a.save_normalized)
                else:
                    document.pop("normalized", None)
            plan.append((Path(target), (json.dumps(document, ensure_ascii=False, indent=1) + "\n").encode("utf-8")))
    lib.agent_finops_output_paths(inputs, [path for path, _ in plan])
    for path, _ in plan:
        if path.exists() or any(parent.exists() and not parent.is_dir() for parent in path.parents):
            raise ValueError("Agent FinOps publication destination exists or is unavailable; select new outputs")
    # No public directories or files exist before the entire plan is validated.
    for path, content in plan:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)

    def public_paths(value):
        if isinstance(value, dict):
            return {key: public_paths(child) for key, child in value.items()}
        if isinstance(value, list):
            return [public_paths(child) for child in value]
        if isinstance(value, str) and value.startswith(str(stage)):
            return str(out) + value[len(str(stage)):]
        return value

    summary = public_paths(summary)
    summary.pop("html_name", None)
    if customer:
        if summary.get("value_finops"):
            summary["value_finops"]["value"] = None
        if summary.get("value"):
            summary["value"].pop("out", None)
        if summary.get("identity"):
            missing = summary["identity"].get("without_identity")
            if isinstance(missing, list):
                summary["identity"]["without_identity"] = len(missing)
    print(json.dumps(summary, indent=1, ensure_ascii=False))


def build_identity(a, out: Path, short: str, slug: str, summary: dict, *, seed_data: Path | None = None) -> Path:
    if not (ID_SCRIPTS / "make_kit.py").is_file():
        raise IdentityError("the frontier-agent-identity skill is not installed next to frontier-blueprint")
    work, kit, bpi, zipname, config = identity_layout(a, out, short, slug)
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
        args = ["--blueprint", seed_data or a.data, "--out-dir", cdir, "--version", "1.0.0"]
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
    if config is None:
        config = json.loads(cfg.read_text(encoding="utf-8"))
    # Recheck the actual seed output before invoking the next script.
    identity_component(config.get("version", "1.0.0"))
    args = ["--config", cfg, "--palette", pal, "--out", kit, "--zip", zipname] + (["--no-png"] if a.no_png else [])
    code, so, err = run(ID_SCRIPTS / "make_kit.py", *args)
    res = summary_json(so) or {}
    if code or (res.get("validation") or {}).get("errors"):
        raise IdentityError("the identity kit did not validate: " + json.dumps(res.get("validation") or err.strip()[-300:])[:400])
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
        # Value owns legacy dependency detection. Loading value does not load
        # FinOps unless that particular value/blueprint actually consumes it.
        value_module = value_library("value_calc")
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
    agent_finops_preflight(a, data, acknowledge_finops_preview=acknowledge_finops_preview)
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
            if preview or getattr(a, "agent_finops", None):
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
            if preview or getattr(a, "agent_finops", None):
                raise ValueError("Preview-dependent value not applied: " + err.strip())
            summary["notes"].append("Business value left out: " + err.strip()[-300:])
        else:
            current = target
    summary["value_finops"] = {"folder": str(work), "value": str(val) if val else None, "finops": str(fin) if fin else None}
    if preview:
        summary["finops_preview"] = preview
    return current


def build_ontology(a, data: Path, out: Path, summary: dict, *, preapplied: bool = False) -> Path:
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
    if preapplied:
        # The detached raw ontology was already applied and source-validated in
        # preflight. Keep that ancestry for final financial projection; replacing
        # it with customer-scrubbed ontology here would launder private citations.
        # The standalone process artifacts above still use the requested audience.
        return data
    target = work / "blueprint-ontology.json"
    with tempfile.TemporaryDirectory() as directory:
        if audience == "customer":
            # The apply intermediate is also an exported JSON file. Project its
            # blueprint source now, not only when the final HTML is rendered.
            projected = Path(directory) / "customer-blueprint.json"
            code, _, err = run(HERE / "build_blueprint.py", "--data", data, "--audience", "customer",
                                "--save-normalized", projected, "--no-product-icons", *agent_finops_flags(a))
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
    blueprint_library().agent_finops_arguments(ap)
    a = ap.parse_args(argv)
    try:
        lib, bp, successor = agent_finops_preflight(
            a, Path(a.data), acknowledge_finops_preview=a.acknowledge_finops_preview)
        if a.value or a.finops:
            preview_preflight(a, Path(a.data), acknowledge_finops_preview=a.acknowledge_finops_preview)
        if successor:
            meta = bp.get("meta") or {}
            short = str(meta.get("short") or str(meta.get("customer") or "Customer").split(" ")[0])
            html_name = a.html or f"{short} - Frontier Company Blueprint.html"
            html = Path(a.out_dir) / html_name
            audience = a.audience or str(meta.get("audience", "internal")).lower()
            destinations = agent_finops_destinations(Path(a.out_dir), successor, audience)
            inputs = successor_inputs(a)
            successor_output_preflight(a, inputs, html_name)
            lib.agent_finops_output_paths(inputs,
                                         [html, a.save_normalized, a.report, *destinations])
            if any(path.exists() for path in destinations):
                raise ValueError("Agent FinOps output exists; select a new output directory")
    except (OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    try:
        with tempfile.TemporaryDirectory() as directory:
            private_work = Path(directory)
            if successor:
                # Legacy/core-only paths keep their historical publication and
                # fallback behaviour. The successor chain stages every component.
                output = io.StringIO()
                with redirect_stdout(output):
                    code = build(a, bp, successor, lib, private_work)
                if code:
                    return code
                publish_successor(a, lib, private_work, summary_json(output.getvalue()), inputs)
                return 0
            return build(a, bp, successor, lib, private_work)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        if not successor:
            raise
        print("ERROR: Agent FinOps output operation refused; no financial permission", file=sys.stderr)
        return 2


def build(a, bp, successor, lib, private_work):
    out = private_work / "artifacts" if successor else Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = bp.get("meta") or {}
    short = str(meta.get("short") or str(meta.get("customer") or "Customer").split(" ")[0])
    html = out / (a.html or f"{short} - Frontier Company Blueprint.html")
    summary = {"html": str(html), "identity": None, "notes": []}
    data = Path(a.data)
    if successor:
        data = private_work / "blueprint-source.json"
        data.write_text(json.dumps(successor["blueprint"], ensure_ascii=False), encoding="utf-8", newline="\n")
        # Identity seeding/apply also uses the detached, cache-free source.
        a.data = str(data)
        # Pin this invocation to the inputs that passed preflight. Original
        # paths are not read again after side effects begin. Raw customer
        # working sources exist only in the private temporary directory.
        for attribute, kind, documents in (("agent_finops", "source", successor["sources"]),
                                           ("agent_finops_review", "review", successor["reviews"])):
            paths = []
            for i, document in enumerate(documents, 1):
                path = private_work / f"{kind}-{i:03}.json"
                successor["library"]._write_exclusive(path, document)
                paths.append(str(path))
            setattr(a, attribute, paths)
        if a.ontology:
            path = private_work / "ontology-source.json"
            successor["library"]._write_exclusive(path, successor["blueprint"]["ontology"])
            a.ontology = str(path)
        if a.value:
            path = private_work / "value-source.json"
            successor["library"]._write_exclusive(path, successor["value"])
            a.value = str(path)
    customer = (a.audience or str(meta.get("audience", "internal")).lower()) == "customer"
    if not a.no_identity:
        try:
            seed_data = None
            if successor and customer:
                rep = lib.Report()
                projected = lib.customer_version(copy.deepcopy(successor["blueprint"]), rep)
                if rep.errors:
                    raise ValueError("Customer identity seed projection refused")
                seed_data = private_work / "identity-seed.json"
                seed_data.write_text(json.dumps(projected, ensure_ascii=False), encoding="utf-8", newline="\n")
                # Explicit identity configuration/palette must use that same
                # ordinary customer policy; never rewrite the caller's files.
                for attribute in ("identity_config", "palette"):
                    source = getattr(a, attribute, None)
                    if source:
                        wrapper = {"evidence": successor["blueprint"].get("evidence", []),
                                   "identity_input": lib.read_document(source)}
                        projected_input = lib.customer_version(wrapper, lib.Report()).get("identity_input")
                        if projected_input is None:
                            raise ValueError("Customer identity input is internal-only")
                        path = private_work / f"{attribute}.json"
                        path.write_text(json.dumps(projected_input, ensure_ascii=False), encoding="utf-8", newline="\n")
                        setattr(a, attribute, str(path))
            data = build_identity(a, out, short, slugify(short), summary, seed_data=seed_data) if successor else (
                build_identity(a, out, short, slugify(short), summary))
        except IdentityError as exc:
            if successor:
                raise ValueError("Requested identity component failed; no artifacts published") from None
            summary["notes"].append(f"Identity kit not built: {exc}. The blueprint was built without identity.")
    if a.value or a.finops:
        try:
            data = build_value_finops(a, Path(data), out, summary,
                                      acknowledge_finops_preview=a.acknowledge_finops_preview)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
    if a.ontology:
        data = build_ontology(a, Path(data), out, summary, preapplied=bool(successor))
        if summary["ontology"]["status"] == "failed":
            print(json.dumps(summary, indent=1, ensure_ascii=False))
            return 1
    args = ["--data", data, "--out", html] + (["--audience", a.audience] if a.audience else [])
    normalized = private_work / "normalized.json" if successor else a.save_normalized
    report = private_work / "report.json" if successor else a.report
    for flag, value in (("--save-normalized", normalized), ("--report", report)):
        if value:
            args += [flag, value]
    args += agent_finops_flags(a)
    code, so, err = run(HERE / "build_blueprint.py", *args)
    if successor and code:
        print("ERROR: Agent FinOps final Blueprint source validation/build refused; no financial permission",
              file=sys.stderr)
        return 2
    if successor:
        try:
            final = lib.read_document(normalized)
            write_agent_finops(out, successor, final["agent_finops"], final["agent_finops"]["audience"])
        except (OSError, ValueError, KeyError, TypeError, UnicodeError):
            print("ERROR: Agent FinOps projected reports not written; no financial permission", file=sys.stderr)
            return 2
        summary["agent_finops"] = {"status": "partial", "maturity": "Preview",
                                  "records": len(final["agent_finops"]["records"]), "financial_permission": False,
                                  "audience": final["agent_finops"]["audience"]}
        summary["html_name"] = html.name
    summary["blueprint"] = summary_json(so) or {"status": "failed", "detail": err.strip()[-600:]}
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return 0 if code == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
