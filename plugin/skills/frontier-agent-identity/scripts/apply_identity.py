#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Writes the agent identity into a Frontier Company Blueprint: names per environment, icons, technical names
and the kit summary that the blueprint shows on its Agent identity page (below Agents).

Usage:
  python apply_identity.py --blueprint blueprint.json --kit <identity kit folder> --out blueprint.json
         [--colours] [--package "<Customer> - agent identity package v1.0.zip"]

Each blueprint agent whose id matches an identity agent gets an "identity" block: display_name, names
{ENV: name}, icon (production) and icons {ENV: icon} as SVG data URIs, outline, tokens (po, domain, scope),
kind, schema, solution, repo, colour, contrast, glyph, status, status_class, short_description, description,
slug and kit. Data agents match "<journey>-DATA". The blueprint also gets a top-level "identity" block: rule,
environments with their bands, journey colours, PO areas, decisions, Microsoft guidance, validation result and
the package name. --colours also sets every journey colour to the identity palette, so the blueprint and the
agents wear the same colours.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path


def _uri(p: Path):
    return "data:image/svg+xml;base64," + base64.b64encode(p.read_bytes()).decode("ascii") if p.is_file() else None


def _clean(d: dict) -> dict:
    return {k: v for k, v in d.items() if v not in (None, "", [], {})}


def _kit_modules(kit: Path):
    """identity_docs (Microsoft guidance, naming rule) and validate_identity from the kit's own scripts."""
    scripts = kit / "scripts"
    if not (scripts / "identity_docs.py").is_file() or not (scripts / "validate_identity.py").is_file():
        return None, None
    sys.path.insert(0, str(scripts))
    try:
        import identity_docs  # kit script, standard library only
        import validate_identity  # kit script, standard library only
        return identity_docs, validate_identity
    except Exception as exc:  # noqa: BLE001 - the page then shows less; names and icons still apply
        print(f"note: kit scripts not loaded ({exc}); guidance and validation left out", file=sys.stderr)
        return None, None
    finally:
        sys.path.remove(str(scripts))


def _status(pal: dict, x: dict):
    styles = pal.get("statusStyles") or {}
    cls = x.get("statusClass") or "hypothesis"
    st = styles.get(cls) or styles.get("hypothesis") or {"label": cls.replace("-", " ").capitalize()}
    return (x.get("mvp") if cls == "mvp" and x.get("mvp") else st.get("label")), cls


def build_identity(bp: dict, kit: Path, colours: bool = False, package: str | None = None) -> dict:
    cfg = json.loads((kit / "config" / "agent-identity.json").read_text(encoding="utf-8"))
    pal = json.loads((kit / "config" / "palette.json").read_text(encoding="utf-8"))
    envs_cfg = cfg["environments"]
    prod = next((e["name"] for e in envs_cfg if e.get("production")), envs_cfg[-1]["name"])
    by_id = {x["id"]: x for x in cfg["agents"] if x.get("derived")}
    label = f"{cfg['customer']['short']} agent identity v{cfg['version']}"
    matched, missing = [], []

    def ident(agent_id: str):
        x = by_id.get(agent_id)
        if not x:
            return None
        d = x["derived"]
        folder = kit / "agents" / d["slug"] / "identity"
        icon = _uri(folder / "icon.svg")
        if not icon:
            return None
        rec = json.loads((folder / "identity.json").read_text(encoding="utf-8")) if (folder / "identity.json").is_file() else {}
        scoped = x.get("environmentScoped", True)
        names = d["displayName"] if scoped else {prod: d["displayName"][prod]}
        ic = rec.get("icon") or {}
        files = ic.get("files") or {}
        icons = {}
        if scoped:
            for env in names:
                if env != prod:
                    u = _uri(folder / ((files.get(env) or {}).get("svg") or f"icon-{env.lower()}.svg"))
                    if u:
                        icons[env] = u
        status, cls = _status(pal, x)
        return _clean({
            "display_name": d["displayName"][prod], "names": names, "icon": icon, "icons": icons,
            "outline": _uri(folder / "outline.svg"), "slug": d["slug"], "kit": label,
            "tokens": _clean({"po": x.get("po"), "domain": x.get("domain"), "scope": x.get("scope")}),
            "kind": rec.get("kindLabel") or x.get("kind"), "schema": rec.get("schemaName"),
            "solution": (rec.get("solution") or {}).get("uniqueName"), "repo": f"agents/{d['slug']}/",
            "colour": ic.get("background"), "contrast": ic.get("contrast"), "glyph": ic.get("glyph"),
            "status": status, "status_class": cls,
            "short_description": (rec.get("shortDescription") or {}).get(prod) or x.get("shortDescription"),
            "description": (rec.get("fullDescription") or {}).get(prod) or x.get("fullDescription"),
        })

    for dom in bp.get("domains", []):
        team = ([dom["orchestrator"]] if isinstance(dom.get("orchestrator"), dict) else []) + list(dom.get("agents", []))
        for ag in team:
            idn = ident(ag.get("id", ""))
            if idn:
                ag["identity"] = idn
                matched.append(ag["id"])
            else:
                missing.append(ag.get("id", "?"))
        if isinstance(dom.get("data_agent"), dict):
            idn = ident(f"{dom['id']}-DATA")
            if idn:
                dom["data_agent"]["identity"] = idn
                matched.append(f"{dom['id']}-DATA")
        if colours and dom.get("id") in pal.get("journeys", {}):
            dom["color"] = pal["journeys"][dom["id"]]["background"]

    docs, val = _kit_modules(kit)
    naming = cfg.get("naming") or {}
    pal_env = pal.get("environments") or {}
    envs = [_clean({"name": e["name"], "postfix": e.get("postfix"), "production": e["name"] == prod,
                    "band": (pal_env.get(e["name"]) or {}).get("band"), "label": (pal_env.get(e["name"]) or {}).get("label"),
                    "band_name": (pal_env.get(e["name"]) or {}).get("brandColour"),
                    "label_contrast": (pal_env.get(e["name"]) or {}).get("labelContrast"), "banner": e.get("fullBanner")})
            for e in envs_cfg]
    pj = pal.get("journeys") or {}
    journeys = [_clean({"id": dom["id"], "name": pj[dom["id"]].get("name") or dom.get("journey_name") or dom.get("name"),
                        "po": pj[dom["id"]].get("short"), "colour": pj[dom["id"]].get("background"), "glyph": pj[dom["id"]].get("glyph"),
                        "colour_name": pj[dom["id"]].get("brandColour"), "contrast": pj[dom["id"]].get("contrast")})
                for dom in bp.get("domains", []) if dom.get("id") in pj]
    if docs:
        rule = docs._rule(cfg)
        rules = [{"title": t, "url": u, "text": x} for t, u, x in docs.MS_SOURCES]
    else:
        post = [e.get("postfix") or e["name"] for e in envs_cfg if e["name"] != prod]
        rule = "<PO> <Domain> [<Scope>]" + (f" [{' | '.join(post)}]" if post else "")
        rules = []
    validation = None
    if val:
        rep = val.validate(kit)
        validation = {"errors": len(rep.get("errors", [])), "warnings": len(rep.get("warnings", []))}
    if not package:
        zips = sorted(kit.parent.glob("*agent identity package*.zip"))
        package = zips[0].name if len(zips) == 1 else None
    bp["identity"] = _clean({
        "kit": label, "version": cfg.get("version"), "date": cfg.get("date"), "status": cfg.get("status"),
        "customer": (cfg.get("customer") or {}).get("short"), "rule": rule, "max_length": naming.get("maxDisplayLength"),
        "prefix": naming.get("publisherPrefix"), "prefix_note": naming.get("prefixDecision"), "solution_prefix": naming.get("solutionPrefix"),
        "environments": envs, "journeys": journeys,
        "po_areas": [_clean({"token": p.get("token"), "owner": p.get("processOwner"), "journeys": p.get("journeys"), "assumed": bool(p.get("assumed")) or None})
                     for p in cfg.get("poAreas", [])],
        "decisions": [_clean({k: dd.get(k) for k in ("id", "decision", "owner", "when")}) for dd in cfg.get("decisions", [])],
        "rules": rules, "brand": _clean({"source": pal.get("sourceShort"), "status": pal.get("status")}),
        "validation": validation, "package": package,
    })
    return {"matched": len(matched), "without_identity": missing, "colours": bool(colours), "validation": validation, "package": package}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--kit", required=True, help="identity kit folder (with config/ and agents/)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--colours", action="store_true", help="use the identity palette for the journey colours")
    ap.add_argument("--package", help="file name of the zipped identity package, shown on the identity page")
    a = ap.parse_args(argv)
    bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8"))
    summary = build_identity(bp, Path(a.kit), a.colours, a.package)
    Path(a.out).write_text(json.dumps(bp, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(summary, out=a.out), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
