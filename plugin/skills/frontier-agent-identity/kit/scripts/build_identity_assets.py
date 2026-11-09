#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Regenerates every derived identity artefact from config/: names, icons, identity records, identity
cards, visuals, documentation and the catalogue.

Usage:
  python scripts/build_identity_assets.py               # everything
  python scripts/build_identity_assets.py --no-png      # skip PNG copies of cards and visuals
  python scripts/build_identity_assets.py --names-only  # derive names and identity.json only

Icons (SVG and PNG) are drawn with the Python standard library (scripts/raster.py) - no browser, Node.js or
image library. PNG copies of cards and visuals need an SVG converter (cairosvg, rsvg-convert, or Node.js
with sharp); without one they stay SVG.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import identity_docs as D  # noqa: E402
import identity_lib as L  # noqa: E402
import identity_visuals as V  # noqa: E402


def by_journey(cfg: dict, palette: dict) -> dict:
    order = list(palette["journeys"])
    groups = {j: [] for j in order}
    role_rank = {"orchestrator": 0, "specialist": 1, "data": 2}
    for a in cfg["agents"]:
        groups.setdefault(a["journey"], []).append(a)
    for j in groups:
        groups[j].sort(key=lambda a: (role_rank.get(a.get("role"), 1), a["id"]))
    return {j: v for j, v in groups.items() if v}


def identity_record(cfg: dict, palette: dict, lib: dict, agent: dict) -> dict:
    d = agent["derived"]
    envs = L.env_names(cfg) if L.is_scoped(agent) else [L.prod_env(cfg)]
    files = {}
    for e in L.env_names(cfg):
        sfx = L.env_suffix(cfg, e) if L.is_scoped(agent) else ""
        files[e] = {"color192": f"color-192{sfx}.png", "color32": f"color-32{sfx}.png", "outline32": "outline-32.png", "svg": f"icon{sfx}.svg"}
    g = lib["glyphs"][agent["glyph"]]
    src = "Fluent UI System Icons" if g["source"] == "fluent" else "Frontier glyphs"
    rec = {
        "id": agent["id"], "kind": agent["kind"], "kindLabel": L.KINDS[agent["kind"]]["label"], "role": agent.get("role"),
        "journey": {"id": agent["journey"], "name": palette["journeys"][agent["journey"]]["name"]},
        "tokens": {"po": agent["po"], "domain": agent["domain"], "scope": agent.get("scope", "")},
        "displayName": d["displayName"],
        "shortDescription": {e: L.env_description(cfg, agent, e, "short") for e in L.env_names(cfg)},
        "fullDescription": {e: L.env_description(cfg, agent, e, "full") for e in L.env_names(cfg)},
        "slug": d["slug"], "schemaName": d["schemaName"],
        "solution": {"uniqueName": d["solutionUniqueName"], "displayName": d["solutionDisplayName"]} if d["solutionUniqueName"] else None,
        "envVarPrefix": d["envVarPrefix"], "connectionContext": d["connectionContext"], "flowNamePrefix": d["flowNamePrefix"],
        "technical": d["technical"],
        "github": {"agent": d["githubAgentName"], "file": d["githubAgentFile"]} if d["githubAgentName"] else None,
        "environments": envs,
        "icon": {"background": d["icon"]["background"], "glyphColour": d["icon"]["glyphColor"], "contrast": d["icon"]["contrast"],
                 "glyph": f"{src}: {agent['glyph']} (filled / regular)", "files": {e: files[e] for e in envs}},
        "teams": None,
        "status": agent.get("status"), "mvp": agent.get("mvp"), "workingName": agent.get("workingName") or agent.get("blueprintName"),
        "owner": agent.get("owner"), "audience": agent.get("audience"), "channels": agent.get("channels") or [],
        "evidence": agent.get("evidence") or [],
        "generated": "scripts/build_identity_assets.py - do not edit by hand",
    }
    if d["teams"]:
        rec["teams"] = dict(d["teams"], shortDescription=rec["shortDescription"],
                            fullDescription=rec["fullDescription"])
    return rec


def palette_css(cfg: dict, palette: dict) -> str:
    def var(name):
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    ui = palette["ui"]
    lines = [f"/* {cfg['customer']['short']} agent identity - generated from config/palette.json */", ":root {"]
    for nc in palette.get("named", []):
        lines.append(f"  --brand-{var(nc['name'])}: {nc['hex']};")
    for jid, j in palette["journeys"].items():
        k = var(jid)
        lines += [f"  --{k}-bg: {j['background']};", f"  --{k}-glyph: {j['glyph']};", f"  --{k}-tint: {j['tint']};",
                  f"  --{k}-tint-strong: {j['tintStrong']};", f"  --{k}-text: {j['textOnWhite']};"]
    for e, m in palette["environments"].items():
        if m:
            lines += [f"  --env-{var(e)}-band: {m['band']};", f"  --env-{var(e)}-label: {m['label']};"]
    lines += [f"  --ui-text: {ui['text']};", f"  --ui-muted: {ui['muted']};", f"  --ui-background: {ui['background']};",
              f"  --ui-line: {ui['line']};", f"  --ui-accent: {ui['accent']};",
              f"  --font-heading: {ui.get('headingFont', 'Arial')}, Arial, Helvetica, sans-serif;",
              f"  --font-body: {ui.get('bodyFont', 'Arial')}, 'Liberation Sans', Arial, Helvetica, sans-serif;", "}", ""]
    return "\n".join(lines)


def precheck(cfg, palette, lib) -> list:
    problems = []
    tokens = {p["token"] for p in cfg["poAreas"]}
    for a in cfg["agents"]:
        if a["po"] not in tokens:
            problems.append(f"{a['id']}: PO token {a['po']!r} is not in poAreas")
        if a["journey"] not in palette["journeys"]:
            problems.append(f"{a['id']}: journey {a['journey']!r} has no colour in palette.json")
        if a["glyph"] not in lib["glyphs"]:
            problems.append(f"{a['id']}: glyph {a['glyph']!r} is not in scripts/glyphs/glyphs.json")
        if a.get("kind") not in L.KINDS:
            problems.append(f"{a['id']}: kind {a.get('kind')!r} is not one of {sorted(L.KINDS)}")
    for e in L.nonprod_envs(cfg):
        if e not in palette["environments"]:
            problems.append(f"palette.json has no marker for environment {e}")
    return problems


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(L.ROOT))
    ap.add_argument("--no-png", action="store_true", help="skip PNG copies of cards and visuals")
    ap.add_argument("--names-only", action="store_true", help="derive names and identity.json only")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    cfg, palette = L.load_config(root)
    lib = L.load_glyphs(root)
    problems = precheck(cfg, palette, lib)
    if problems:
        for p in problems:
            print("ERROR", p)
        return 1
    for a in cfg["agents"]:
        a["derived"] = L.derive(cfg, a, palette)
    cfg["naming"]["maxBaseLength"] = L.max_base_length(cfg)
    L.save_json(root / "config" / "agent-identity.json", cfg)
    groups = by_journey(cfg, palette)
    prod = L.prod_env(cfg)
    png_jobs = []
    slugs = set()
    for a in cfg["agents"]:
        d = a["derived"]
        slugs.add(d["slug"])
        folder = root / "agents" / d["slug"] / "identity"
        folder.mkdir(parents=True, exist_ok=True)
        L.save_json(folder / "identity.json", identity_record(cfg, palette, lib, a))
        if args.names_only:
            continue
        envs = L.env_names(cfg) if L.is_scoped(a) else [prod]
        for e in envs:
            sfx = L.env_suffix(cfg, e)
            write(folder / f"icon{sfx}.svg", L.icon_svg(cfg, palette, lib, a, e))
            (folder / f"color-192{sfx}.png").write_bytes(L.icon_png(cfg, palette, lib, a, e, 192))
            (folder / f"color-32{sfx}.png").write_bytes(L.icon_png(cfg, palette, lib, a, e, 32))
        for stale in folder.glob("*"):
            m = re.fullmatch(r"(?:icon|color-192|color-32)(-[a-z0-9]+)?\.(?:svg|png)", stale.name)
            if m and m.group(1) and m.group(1)[1:].upper() not in [x.upper() for x in envs]:
                stale.unlink()
        write(folder / "outline.svg", L.outline_svg(lib, a))
        (folder / "outline-32.png").write_bytes(L.outline_png(lib, a))
        write(folder / "card.svg", V.card(cfg, palette, lib, a, root))
        if not args.no_png:
            png_jobs.append((folder / "card.svg", folder / "card.png", 1200, 630))
    # remove folders of agents that were renamed or removed (only generated ones)
    agents_dir = root / "agents"
    for sub in sorted(agents_dir.iterdir()) if agents_dir.exists() else []:
        rec = sub / "identity" / "identity.json"
        if sub.is_dir() and sub.name not in slugs and rec.exists() and "build_identity_assets" in rec.read_text(encoding="utf-8"):
            shutil.rmtree(sub)
    summary = {"agents": len(cfg["agents"]), "journeys": len(groups), "png": None}
    if not args.names_only:
        vis = root / "visuals"
        svg, w, h = V.family(cfg, palette, lib, groups, root)
        write(vis / "agent-family.svg", svg)
        png_jobs.append((vis / "agent-family.svg", vis / "agent-family.png", w, h))
        mvps = sorted((a for a in cfg["agents"] if a.get("statusClass") == "mvp"), key=lambda a: (a.get("mvp") or "", a["id"]))
        if mvps:
            svg, w, h = V.mvp_sheet(cfg, palette, lib, mvps, root)
            write(vis / "mvp-identity-sheet.svg", svg)
            png_jobs.append((vis / "mvp-identity-sheet.svg", vis / "mvp-identity-sheet.png", w, h))
        svg, w, h = V.colour_schema(cfg, palette, lib, groups, root)
        write(vis / "colour-schema.svg", svg)
        png_jobs.append((vis / "colour-schema.svg", vis / "colour-schema.png", w, h))
        if not args.no_png:
            try:
                count, method = V.svgs_to_png(png_jobs)
            except Exception as exc:  # converter present but failed: keep the SVGs
                count, method = 0, f"failed ({exc.__class__.__name__})"
            summary["png"] = {"converted": count, "method": method}
        write(root / "brand" / "palette.css", palette_css(cfg, palette))
    have_png = (root / "visuals" / "agent-family.png").exists()
    docs = root / "docs"
    write(docs / "naming-convention.md", D.naming_md(cfg, palette))
    write(docs / "color-schema.md", D.colour_md(cfg, palette))
    write(docs / "icons-and-visuals.md", D.icons_md(cfg, palette, lib))
    write(docs / "harness-integration.md", D.harness_md(cfg))
    write(docs / "evidence.md", D.evidence_md(cfg))
    write(docs / "agent-identity-catalog.md", D.catalog_md(cfg, palette, groups))
    write(root / "README.md", D.readme_md(cfg, palette, groups, have_png))
    write(root / "CHANGELOG.md", D.changelog_md(cfg))
    write(root / "THIRD-PARTY-NOTICES.md", D.notices_md(cfg, palette))
    write(root / "github" / "instructions" / "agent-identity.instructions.md", D.instructions_md(cfg))
    if not args.names_only:
        write(root / "catalog.html", D.catalog_html(cfg, palette, groups, root))
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main())
