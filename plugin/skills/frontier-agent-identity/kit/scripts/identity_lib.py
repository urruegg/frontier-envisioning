#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Shared helpers for the agent identity package: names, colours, glyphs and icons.

Naming is derived from tokens held in config/agent-identity.json:
  display name = <PO> <Domain> [<Scope>] [<ENV>]   (no environment postfix in production)
Everything technical (schema names, solutions, slugs, variables) is environment-neutral.
Standard library only, so the validator, the stamping step and the icon build run on any build agent.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import raster as R

ROOT = Path(__file__).resolve().parent.parent

# What each kind of agent carries. Power Platform kinds get schema, solution, variable and
# connection-reference names; kinds without environments keep one name everywhere.
KINDS = {
    "copilot-studio": {"label": "Copilot Studio agent", "powerPlatform": True, "teams": True, "scoped": True, "descMax": 4000},
    "ess": {"label": "Employee Self-Service agent (Microsoft-managed, customised)", "powerPlatform": True, "teams": True, "scoped": True, "descMax": 4000},
    "declarative-agent": {"label": "Declarative agent for Microsoft 365 Copilot", "powerPlatform": False, "teams": True, "scoped": True, "descMax": 1000},
    "foundry-agent": {"label": "Microsoft Foundry agent", "powerPlatform": False, "teams": True, "scoped": True, "descMax": 4000},
    "fabric-data-agent": {"label": "Fabric data agent", "powerPlatform": False, "teams": False, "scoped": False, "descMax": 4000},
    "repository-agent": {"label": "GitHub Copilot custom agent (repository)", "powerPlatform": False, "teams": False, "scoped": False, "descMax": 4000},
}

ICON = {"size": 192, "glyphBox": 96, "glyphOffset": 48, "separatorY": 152, "separatorH": 4,
        "bandY": 156, "bandH": 36, "labelCap": 15.0, "labelStroke": 3.2}


# ---------------------------------------------------------------- files

def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_config(root: Path = ROOT):
    return load_json(root / "config" / "agent-identity.json"), load_json(root / "config" / "palette.json")


def load_glyphs(root: Path = ROOT):
    return load_json(root / "scripts" / "glyphs" / "glyphs.json")


# ---------------------------------------------------------------- colour

def norm_hex(c: str) -> str:
    h = c.strip().lstrip("#").upper()
    if len(h) == 3:
        h = "".join(x * 2 for x in h)
    if not re.fullmatch(r"[0-9A-F]{6}", h):
        raise ValueError(f"not a hex colour: {c!r}")
    return "#" + h


def _channel(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    h = norm_hex(hex_colour)[1:]
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def mix(hex_colour: str, other: str = "#FFFFFF", share_other: float = 0.88) -> str:
    h1, h2 = norm_hex(hex_colour)[1:], norm_hex(other)[1:]
    out = []
    for i in (0, 2, 4):
        c1, c2 = int(h1[i:i + 2], 16), int(h2[i:i + 2], 16)
        out.append(round(c1 * (1 - share_other) + c2 * share_other))
    return "#" + "".join(f"{c:02X}" for c in out)


def accessible_shade(hex_colour: str, against: str = "#FFFFFF", target: float = 4.5) -> str:
    """Darkens (or lightens, against a dark colour) in small steps until the contrast target is met."""
    darker = luminance(against) > 0.5
    c = norm_hex(hex_colour)
    for step in range(0, 101):
        cand = mix(c, "#000000" if darker else "#FFFFFF", step / 100.0)
        if contrast(cand, against) >= target:
            return cand
    return "#000000" if darker else "#FFFFFF"


# ---------------------------------------------------------------- environments

def environments(cfg: dict) -> list:
    return cfg["environments"]


def env_names(cfg: dict) -> list:
    return [e["name"] for e in cfg["environments"]]


def prod_env(cfg: dict) -> str:
    for e in cfg["environments"]:
        if e.get("production"):
            return e["name"]
    return cfg["environments"][-1]["name"]


def nonprod_envs(cfg: dict) -> list:
    p = prod_env(cfg)
    return [e["name"] for e in cfg["environments"] if e["name"] != p]


def env(cfg: dict, name: str) -> dict:
    for e in cfg["environments"]:
        if e["name"] == name:
            return e
    raise KeyError(name)


def env_suffix(cfg: dict, name: str) -> str:
    """File-name suffix: '' for production, '-dev', '-test', ... otherwise."""
    return "" if name == prod_env(cfg) else "-" + name.lower()


# ---------------------------------------------------------------- naming

def _pascal(text: str) -> str:
    out = []
    for w in re.split(r"[^A-Za-z0-9]+", text):
        if w:
            out.append(w if w.isupper() else w[:1].upper() + w[1:])
    return "".join(out)


def kebab(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def po_area(cfg: dict, token: str) -> dict:
    for area in cfg["poAreas"]:
        if area["token"] == token:
            return area
    raise KeyError(f"Unknown PO area token: {token!r} (add it to poAreas)")


def kind_info(agent: dict) -> dict:
    return KINDS.get(agent.get("kind", "copilot-studio"), KINDS["copilot-studio"])


def is_scoped(agent: dict) -> bool:
    return bool(agent.get("environmentScoped", kind_info(agent)["scoped"]))


def _fill(tpl: str, agent: dict, env_word: str) -> str:
    text = tpl.format(po=agent["po"], domain=agent["domain"], scope=agent.get("scope", "") or "", env=env_word)
    return re.sub(r"\s+", " ", text).strip()


def base_name(cfg: dict, agent: dict) -> str:
    """Production display name: the template without the environment token."""
    return _fill(cfg["naming"]["displayTemplate"], agent, "")


def display_name(cfg: dict, agent: dict, env_name: str) -> str:
    if not is_scoped(agent) or env_name == prod_env(cfg):
        return base_name(cfg, agent)
    return _fill(cfg["naming"]["displayTemplate"], agent, env(cfg, env_name).get("postfix", env_name))


def max_base_length(cfg: dict) -> int:
    longest = max((len(e.get("postfix", "")) for e in cfg["environments"]), default=0)
    return cfg["naming"]["maxDisplayLength"] - (1 + longest if longest else 0)


def derive(cfg: dict, agent: dict, palette: dict) -> dict:
    """Every derived name and identity fact for one agent (environment-neutral unless keyed by environment)."""
    n = cfg["naming"]
    area = po_area(cfg, agent["po"])
    prefix = n["publisherPrefix"]
    scope = (agent.get("scope") or "").upper()
    stem = area["code"] + _pascal(agent["domain"]) + scope
    base = base_name(cfg, agent)
    sol_stem = stem
    for lead in n.get("stripLeadingFromStem", []):
        if sol_stem.startswith(lead) and len(sol_stem) > len(lead):
            sol_stem = sol_stem[len(lead):]
            break
    k = kind_info(agent)
    pp = k["powerPlatform"]
    ov = agent.get("overrides") or {}
    names = {e: display_name(cfg, agent, e) for e in env_names(cfg)}
    full = {e: f"{n['fullNamePrefix']}{base}" + ("" if names[e] == base else f" ({e})") for e in names}
    j = palette["journeys"][agent["journey"]]
    slug = ov.get("slug", kebab(base))
    technical = None
    if agent["kind"] == "foundry-agent":
        technical = {"label": "Foundry agent name", "value": slug}
    elif agent["kind"] == "fabric-data-agent":
        technical = {"label": "Fabric item name", "value": base}
    elif agent["kind"] == "declarative-agent":
        technical = {"label": "App package folder", "value": f"appPackage/{slug}"}
    elif agent["kind"] == "repository-agent" and agent.get("githubAgent"):
        technical = {"label": "Custom agent file", "value": f".github/agents/{agent['githubAgent']}.agent.md"}
    return {
        "displayName": names,
        "slug": slug,
        "schemaStem": stem,
        "schemaName": (ov.get("schemaName") or f"{prefix}_{stem}") if pp else None,
        "solutionUniqueName": ov.get("solutionUniqueName", f"{n['solutionPrefix']}{sol_stem}") if pp else None,
        "solutionDisplayName": ov.get("solutionDisplayName", f"{n['solutionDisplayPrefix']}{base}") if pp else None,
        "envVarPrefix": f"{prefix}_{area['code']}" if pp else None,
        "connectionContext": area["code"] + scope if pp else None,
        "flowNamePrefix": f"{base} - " if pp else None,
        "technical": technical,
        "githubAgentName": agent.get("githubAgent") if agent["kind"] == "repository-agent" else None,
        "githubAgentFile": f".github/agents/{agent['githubAgent']}.agent.md" if agent["kind"] == "repository-agent" and agent.get("githubAgent") else None,
        "teams": {"shortName": names, "fullName": full, "accentColor": j["background"]} if k["teams"] else None,
        "icon": {"background": j["background"], "glyphColor": j["glyph"],
                 "contrast": contrast(j["background"], j["glyph"]), "glyph": agent["glyph"]},
    }


def env_description(cfg: dict, agent: dict, env_name: str, kind: str = "short") -> str:
    """Short (<= 80 with the marker) or full description for an environment; non-production carries a marker."""
    e = env(cfg, env_name)
    scoped = is_scoped(agent)
    if kind == "short":
        return (e.get("shortPrefix", "") if scoped else "") + agent["shortDescription"]
    banner = e.get("fullBanner", "") if scoped else ""
    return (banner + "\n\n" if banner else "") + agent["fullDescription"]


# ---------------------------------------------------------------- glyphs

def glyph(lib: dict, name: str) -> dict:
    if name not in lib["glyphs"]:
        raise KeyError(f"Glyph {name!r} is not in scripts/glyphs/glyphs.json")
    return lib["glyphs"][name]


def glyph_svg(lib: dict, name: str, style: str, colour: str, background: str | None = None) -> str:
    """SVG elements in the 24-unit glyph grid."""
    g = glyph(lib, name)
    if g["source"] != "frontier":
        return "".join(f'<path fill="{colour}" d="{d}"/>' for d in g[style])
    s = lib["stroke"]
    sh = g["shape"]
    line = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if style == "filled":
        out = [f'<path fill="{colour}" d="{d}"/>' for d in sh["fills"]]
        if sh["lines"]:
            out.append(f'<path {line} stroke="{colour}" stroke-width="{s["filled"]}" d="{"".join(sh["lines"])}"/>')
        if sh["inner"] and background:
            out.append(f'<path {line} stroke="{background}" stroke-width="{s["knockout"]}" d="{"".join(sh["inner"])}"/>')
        return "".join(out)
    every = sh.get("regular") or (sh["fills"] + sh["lines"] + sh["inner"])
    return f'<path {line} stroke="{colour}" stroke-width="{s["regular"]}" d="{"".join(every)}"/>'


def glyph_coverage(lib: dict, name: str, style: str, w: int, h: int, transform) -> list:
    """Anti-aliased coverage of a glyph (knock-outs already removed)."""
    g = glyph(lib, name)
    scale = transform[0]
    if g["source"] != "frontier":
        polys = [p for d in g[style] for p in R.flatten(d, transform)]
        return R.fill_coverage(polys, w, h)
    s = lib["stroke"]
    sh = g["shape"]
    if style == "filled":
        cov = R.fill_coverage([p for d in sh["fills"] for p in R.flatten(d, transform)], w, h) if sh["fills"] else [0.0] * (w * h)
        if sh["lines"]:
            R.stroke_coverage([p for d in sh["lines"] for p in R.flatten(d, transform)], s["filled"] * scale, w, h, cov)
        if sh["inner"]:
            ko = R.stroke_coverage([p for d in sh["inner"] for p in R.flatten(d, transform)], s["knockout"] * scale, w, h)
            cov = [c * (1.0 - k) for c, k in zip(cov, ko)]
        return cov
    every = sh.get("regular") or (sh["fills"] + sh["lines"] + sh["inner"])
    polys = [p for d in every for p in R.flatten(d, transform)]
    return R.stroke_coverage(polys, s["regular"] * scale, w, h)


# ---------------------------------------------------------------- icons

def _band(cfg: dict, palette: dict, agent: dict, env_name: str):
    if not is_scoped(agent) or env_name == prod_env(cfg):
        return None
    return palette["environments"].get(env_name)


def icon_svg(cfg: dict, palette: dict, lib: dict, agent: dict, env_name: str, size: int = 192) -> str:
    j = palette["journeys"][agent["journey"]]
    I = ICON
    sc = I["glyphBox"] / lib["viewBox"]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 192 192">',
             f'<rect width="192" height="192" fill="{j["background"]}"/>',
             f'<g transform="translate({I["glyphOffset"]} {I["glyphOffset"]}) scale({sc:g})">'
             f'{glyph_svg(lib, agent["glyph"], "filled", j["glyph"], j["background"])}</g>']
    band = _band(cfg, palette, agent, env_name)
    if band:
        label = env(cfg, env_name).get("postfix") or env_name
        cap = I["labelCap"] if R.label_width(label, I["labelCap"]) <= 168 else I["labelCap"] * 168 / R.label_width(label, I["labelCap"])
        top = I["bandY"] + (I["bandH"] - cap) / 2
        d = R.polylines_to_path(R.label_polylines(label, 96, top, cap))
        parts += [f'<rect x="0" y="{I["separatorY"]}" width="192" height="{I["separatorH"]}" fill="{band["separator"]}"/>',
                  f'<rect x="0" y="{I["bandY"]}" width="192" height="{I["bandH"]}" fill="{band["band"]}"/>',
                  f'<path fill="none" stroke="{band["label"]}" stroke-width="{I["labelStroke"] * cap / I["labelCap"]:.2f}" '
                  f'stroke-linecap="round" stroke-linejoin="round" d="{d}"/>']
    parts.append("</svg>")
    return "".join(parts)


def outline_svg(lib: dict, agent: dict, size: int = 32) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="-2 -2 28 28">'
            f'{glyph_svg(lib, agent["glyph"], "regular", "#FFFFFF")}</svg>')


def icon_png(cfg: dict, palette: dict, lib: dict, agent: dict, env_name: str, size: int = 192) -> bytes:
    j = palette["journeys"][agent["journey"]]
    I = ICON
    k = size / 192.0
    c = R.Canvas(size, size, j["background"])
    sc = I["glyphBox"] / lib["viewBox"] * k
    off = I["glyphOffset"] * k
    c.blend(glyph_coverage(lib, agent["glyph"], "filled", size, size, (sc, sc, off, off)), j["glyph"])
    band = _band(cfg, palette, agent, env_name)
    if band:
        sep_y, band_y = I["separatorY"] * k, I["bandY"] * k
        c.fill_rect(0, sep_y, size, max(1.0, I["separatorH"] * k), band["separator"])
        c.fill_rect(0, band_y, size, size - band_y, band["band"])
        if size >= 96:
            label = env(cfg, env_name).get("postfix") or env_name
            cap = I["labelCap"] if R.label_width(label, I["labelCap"]) <= 168 else I["labelCap"] * 168 / R.label_width(label, I["labelCap"])
            top = I["bandY"] + (I["bandH"] - cap) / 2
            polys = [[(x * k, y * k) for x, y in pl] for pl in R.label_polylines(label, 96, top, cap)]
            c.blend(R.stroke_coverage(polys, I["labelStroke"] * cap / I["labelCap"] * k, size, size), band["label"])
    return c.png()


def outline_png(lib: dict, agent: dict, size: int = 32) -> bytes:
    c = R.Canvas(size, size, None)
    sc = size / 28.0
    c.blend(glyph_coverage(lib, agent["glyph"], "regular", size, size, (sc, sc, 2 * sc, 2 * sc)), "#FFFFFF")
    return c.png()


def esc(text) -> str:
    return html.escape(str(text if text is not None else ""))
