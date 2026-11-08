#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""SVG visuals for the agent identity package: identity cards, agent family, MVP identity sheet and
colour schema. SVG is always written (standard library); PNG copies are made when an SVG converter
is available (cairosvg, rsvg-convert, or Node.js with sharp)."""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess  # nosec B404 - fixed argument lists, resolved executables, no shell
import tempfile
from pathlib import Path

import identity_lib as L

# Helvetica/Arial advance widths per 1000 em (ASCII 32-126); other characters use 556.
_W = [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278, 556, 556, 556, 556, 556,
      556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278,
      500, 667, 556, 833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469,
      556, 333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500,
      278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]


def text_width(s: str, size: float, bold: bool = False, mono: bool = False) -> float:
    if mono:
        return len(s) * 0.6 * size
    w = sum(_W[ord(c) - 32] if 32 <= ord(c) <= 126 else 556 for c in s) / 1000.0 * size
    return w * (1.07 if bold else 1.0)


def wrap(s: str, size: float, max_w: float, bold: bool = False, max_lines: int = 2) -> list:
    words, lines, cur = [], [], ""
    for wd in s.split():
        if text_width(wd, size, bold) > max_w and "-" in wd:
            parts = wd.split("-")
            words += [p + "-" for p in parts[:-1]] + [parts[-1]]
        else:
            words.append(wd)
    joined = []
    for wd in words:
        if joined and joined[-1].endswith("-") and text_width(joined[-1] + wd, size, bold) <= max_w:
            joined[-1] += wd
        else:
            joined.append(wd)
    words = joined
    for wd in words:
        cand = (cur + wd) if cur.endswith("-") else (cur + " " + wd).strip()
        if text_width(cand, size, bold) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        last = " ".join(lines[max_lines - 1:])
        while text_width(last + "…", size, bold) > max_w and " " in last:
            last = last.rsplit(" ", 1)[0]
        lines = lines[:max_lines - 1] + [last + "…"]
    return lines


def fit(s: str, size: float, max_w: float, bold: bool = False, min_size: float = 10) -> float:
    while size > min_size and text_width(s, size, bold) > max_w:
        size -= 0.5
    return size


class Doc:
    """Small SVG builder with fonts from the palette."""

    def __init__(self, w: int, h: int, palette: dict, bg: str = "#FFFFFF"):
        self.w, self.h, self.p = w, h, palette
        ui = palette["ui"]
        self.font = f"{ui.get('bodyFont', 'Arial')}, 'Liberation Sans', 'DejaVu Sans', Arial, Helvetica, sans-serif"
        self.mono = "Consolas, 'Liberation Mono', 'DejaVu Sans Mono', monospace"
        self.parts = [f'<rect width="{w}" height="{h}" fill="{bg}"/>']
        self.n = 0

    def text(self, x, y, s, size=16, fill=None, bold=False, anchor="start", mono=False, opacity=None):
        fill = fill or self.p["ui"]["text"]
        attrs = f'x="{x:.1f}" y="{y:.1f}" font-family="{self.font if not mono else self.mono}" font-size="{size:g}" fill="{fill}"'
        if bold:
            attrs += ' font-weight="700"'
        if anchor != "start":
            attrs += f' text-anchor="{anchor}"'
        if opacity:
            attrs += f' opacity="{opacity}"'
        self.parts.append(f"<text {attrs}>{L.esc(s)}</text>")

    def rich(self, x, y, runs, size=16, fill=None):
        """runs: [(text, bold, colour|None, mono)]"""
        fill = fill or self.p["ui"]["text"]
        spans = []
        for t, b, c, m in runs:
            a = ' font-weight="700"' if b else ""
            a += f' fill="{c}"' if c else ""
            a += f' font-family="{self.mono}"' if m else ""
            spans.append(f"<tspan{a}>{L.esc(t)}</tspan>")
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{self.font}" font-size="{size:g}" fill="{fill}" '
                          f'xml:space="preserve">{"".join(spans)}</text>')

    def rect(self, x, y, w, h, fill, rx=0, stroke=None):
        s = f' stroke="{stroke}"' if stroke else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{s}/>')

    def chip(self, x, y, label, bg, fg, size=13, pad=9, h=None):
        h = h or size + 10
        w = text_width(label, size, True) + 2 * pad
        self.rect(x, y, w, h, bg, rx=h / 2)
        self.text(x + pad, y + h / 2 + size * 0.35, label, size, fg, bold=True)
        return w

    def icon(self, x, y, size, inner_svg, rx=None):
        """Embed a 192-unit icon SVG (its inner markup) at size px, with presentation-only rounded corners."""
        self.n += 1
        rx = size * 0.125 if rx is None else rx
        cid = f"c{self.n}"
        body = inner_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
        self.parts.append(f'<svg x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" viewBox="0 0 192 192">'
                          f'<clipPath id="{cid}"><rect width="192" height="192" rx="{rx * 192 / size:.1f}"/></clipPath>'
                          f'<g clip-path="url(#{cid})">{body}</g></svg>')

    def outline(self, x, y, size, outline_svg, tile=None):
        tile = tile or self.p["ui"]["dark"]
        self.rect(x, y, size, size, tile, rx=size * 0.15)
        body = outline_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
        g = size * 0.62
        self.parts.append(f'<svg x="{x + (size - g) / 2:.1f}" y="{y + (size - g) / 2:.1f}" width="{g:.1f}" height="{g:.1f}" viewBox="-2 -2 28 28">{body}</svg>')

    def logo(self, root: Path, x_right: float, y: float, h: float):
        lg = self.p.get("logo") or {}
        f = root / lg["file"] if lg.get("file") else None
        if f and f.exists():
            w = h * float(lg.get("aspect", 3.2))
            uri = "data:image/png;base64," + base64.b64encode(f.read_bytes()).decode("ascii")
            self.parts.append(f'<image x="{x_right - w:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" href="{uri}" preserveAspectRatio="xMaxYMid meet"/>')
        else:
            word = self.p.get("wordmark") or ""
            if word:
                self.text(x_right, y + h * 0.78, word, h * 0.8, self.p["ui"]["accent"], bold=True, anchor="end")

    def svg(self) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                + "".join(self.parts) + "</svg>")


def status_style(palette: dict, agent: dict):
    st = palette["statusStyles"].get(agent.get("statusClass", "hypothesis")) or palette["statusStyles"]["hypothesis"]
    label = agent.get("mvp") if agent.get("statusClass") == "mvp" and agent.get("mvp") else st["label"]
    return st["bg"], st["fg"], label


# ---------------------------------------------------------------- identity card 1200 x 630

def card(cfg, palette, lib, agent, root: Path) -> str:
    d = agent["derived"]
    j = palette["journeys"][agent["journey"]]
    ui = palette["ui"]
    prod = L.prod_env(cfg)
    doc = Doc(1200, 630, palette)
    doc.rect(0, 0, 20, 630, j["background"])
    jl = f"{agent['journey']} · {j['name']}"
    jw = text_width(jl, 20, True) + 36
    doc.rect(64, 43, jw, 40, j["tint"], rx=20)
    doc.text(82, 70, jl, 20, j["textOnWhite"], bold=True)
    doc.logo(root, 1136, 36, 56)
    doc.icon(64, 128, 192, L.icon_svg(cfg, palette, lib, agent, prod), rx=24)
    tiles = [prod] + (list(reversed(L.nonprod_envs(cfg))) if L.is_scoped(agent) else [])
    pos = [(68 + (i % 3) * 66, 352 + (i // 3) * 86) for i in range(len(tiles) + 1)]
    for (x, y), e in zip(pos, tiles):
        doc.icon(x, y, 52, L.icon_svg(cfg, palette, lib, agent, e), rx=8)
        doc.text(x + 26, y + 71, e, 14, ui["muted"], anchor="middle")
    ox, oy = pos[len(tiles)]
    doc.outline(ox, oy, 52, L.outline_svg(lib, agent))
    doc.text(ox + 26, oy + 71, "Outline", 14, ui["muted"], anchor="middle")
    name = d["displayName"][prod]
    doc.text(312, 172, name, fit(name, 54, 830, True, 30), ui["text"], bold=True)
    runs = [("PO area ", False, ui["muted"], False), (agent["po"], True, ui["text"], False),
            (" · Domain ", False, ui["muted"], False), (agent["domain"], True, ui["text"], False)]
    if agent.get("scope"):
        runs += [(" · Scope ", False, ui["muted"], False), (agent["scope"], True, ui["text"], False)]
    doc.rich(312, 215, runs, 20)
    used = text_width("".join(r[0] for r in runs), 20) + 18
    bg, fg, label = status_style(palette, agent)
    doc.chip(312 + used, 196, label, bg, fg, 16, 12, 28)
    y = 268
    for line in wrap(agent["shortDescription"], 27, 830, max_lines=2):
        doc.text(312, y, line, 27, ui["text"])
        y += 35
    y += 24
    facts = [("Audience", agent.get("audience") or "to confirm"),
             ("Process owner", L.po_area(cfg, agent["po"]).get("processOwner") or "to confirm")]
    for label_, val in facts:
        doc.text(312, y, label_, 19, ui["muted"])
        doc.text(478, y, wrap(val, 19, 650, max_lines=1)[0], 19, ui["text"])
        y += 33
    doc.text(312, y, "Names", 19, ui["muted"])
    if L.is_scoped(agent):
        runs = []
        for e in L.env_names(cfg):
            if runs:
                runs.append(("  |  ", False, ui["line"], False))
            runs.append((d["displayName"][e], e == prod, ui["text"], False))
        size = 19
        while size > 13 and text_width("".join(r[0] for r in runs), size) > 650:
            size -= 1
        doc.rich(478, y, runs, size)
    else:
        doc.rich(478, y, [(name, True, ui["text"], False), ("  (same name in every environment)", False, ui["muted"], False)], 19)
    y += 33
    tech = [x for x in (d["schemaName"], d["solutionUniqueName"]) if x]
    if not tech and d.get("technical"):
        tech = [d["technical"]["value"]]
    if tech:
        doc.text(312, y, "Technical", 19, ui["muted"])
        t = "  ·  ".join(tech)
        doc.text(478, y, t, max(12.0, min(19.0, 650 / max(1, len(t) * 0.6))), ui["text"], mono=True)
    doc.text(64, 596, f"{cfg['customer']['short']} agent identity v{cfg['version']} · {cfg.get('status', 'proposal')} · {cfg['date']}", 15, ui["muted"])
    doc.text(1136, 596, f"Icon {d['icon']['background']} / {d['icon']['glyphColor']} · contrast {d['icon']['contrast']}:1", 15, ui["muted"], anchor="end")
    return doc.svg()


# ---------------------------------------------------------------- agent family overview

def family(cfg, palette, lib, by_journey: dict, root: Path) -> tuple[str, int, int]:
    ui = palette["ui"]
    prod = L.prod_env(cfg)
    jids = list(by_journey)
    per_row = min(6, max(1, len(jids)))
    colw, gap, margin = 300, 22, 54
    width = max(1400, 2 * margin + per_row * colw + (per_row - 1) * gap)
    rows_of_cols = [jids[i:i + per_row] for i in range(0, len(jids), per_row)]
    mvps = sorted((a for items in by_journey.values() for a in items if a.get("statusClass") == "mvp"), key=lambda a: (a.get("mvp") or "", a["id"]))
    # height
    y = 172
    blocks = []
    for row in rows_of_cols:
        hdr_h = 0
        for jid in row:
            nm = wrap(f"{jid} · {palette['journeys'][jid]['name']}", 21, colw - 30, True, 2)
            hdr_h = max(hdr_h, 46 + 24 * len(nm))
        tallest = max(len(by_journey[jid]) for jid in row)
        blocks.append((row, y, hdr_h))
        y += hdr_h + 18 + tallest * 67 + 26
    strip_y = y + 10
    envs_shown = [prod] + list(reversed(L.nonprod_envs(cfg)))
    strip_h = 150 if mvps else 0
    height = strip_y + strip_h + (60 if mvps else 70)
    doc = Doc(width, height, palette)
    label = cfg.get("familyLabel") or cfg["customer"]["short"]
    doc.text(margin, 82, f"{label} agent family · names, colours and icons", 44, ui["text"], bold=True)
    rule = "<PO> <Domain> [Scope] [" + " | ".join(L.nonprod_envs(cfg)) + "]"
    doc.rich(margin, 122, [("Display name = ", False, ui["muted"], False), (rule, True, ui["text"], False),
                           (f" · {prod} carries no postfix · one colour per journey from {cfg['customer']['short']}'s own palette", False, ui["muted"], False)], 19)
    doc.logo(root, width - margin, 40, 52)
    for row, top, hdr_h in blocks:
        for ci, jid in enumerate(row):
            j = palette["journeys"][jid]
            x = margin + ci * (colw + gap)
            doc.rect(x, top, colw, hdr_h, j["background"], rx=10)
            nm = wrap(f"{jid} · {j['name']}", 21, colw - 30, True, 2)
            for li, line in enumerate(nm):
                doc.text(x + 15, top + 31 + li * 24, line, 21, j["glyph"], bold=True)
            pos = ", ".join(sorted({a["po"] for a in by_journey[jid]}))
            doc.text(x + 15, top + hdr_h - 14, wrap(f"PO area: {pos} · {j['background']}", 13.5, colw - 30, max_lines=1)[0], 13.5, j["glyph"])
            yy = top + hdr_h + 18
            for a in by_journey[jid]:
                doc.icon(x, yy, 54, L.icon_svg(cfg, palette, lib, a, prod), rx=8)
                nm2 = a["derived"]["displayName"][prod]
                doc.text(x + 65, yy + 20, nm2, fit(nm2, 18, colw - 70, True, 13), ui["text"], bold=True)
                bg, fg, lab = status_style(palette, a)
                doc.chip(x + 65, yy + 30, lab, bg, fg, 12, 8, 20)
                yy += 67
    if mvps:
        doc.rect(margin, strip_y - 12, width - 2 * margin, 1.5, ui["line"])
        x = margin
        for a in mvps:
            bg, fg, lab = status_style(palette, a)
            doc.chip(x, strip_y, lab, bg, fg, 12, 8, 20)
            xx = x
            shown = envs_shown if L.is_scoped(a) else [prod]
            for e in shown:
                doc.icon(xx + 22, strip_y + 28, 60, L.icon_svg(cfg, palette, lib, a, e), rx=8)
                for li, line in enumerate(wrap(a["derived"]["displayName"][e], 12.5, 128, max_lines=2)):
                    doc.text(xx + 52, strip_y + 106 + li * 15, line, 12.5, ui["text"], anchor="middle")
                xx += 140
            x = xx + 30
            if x > width - 400:
                break
    foot = [f"{cfg.get('status', 'Proposal')} · v{cfg['version']} · {cfg['date']}",
            f"Colours: {palette.get('sourceShort', 'customer brand')}", "Icon rules: Microsoft Learn agent icon guidance"]
    for i, t in enumerate(foot):
        doc.text(width - margin, height - 52 + i * 19, t, 13.5, ui["muted"], anchor="end")
    return doc.svg(), width, height


# ---------------------------------------------------------------- MVP identity sheet

def mvp_sheet(cfg, palette, lib, mvps: list, root: Path) -> tuple[str, int, int]:
    ui = palette["ui"]
    prod = L.prod_env(cfg)
    envs = [prod] + list(reversed(L.nonprod_envs(cfg)))
    width = 2000
    row_h = 262
    height = 150 + row_h * len(mvps) + 70
    doc = Doc(width, height, palette)
    labels = ", ".join(a.get("mvp") or a["id"] for a in mvps)
    doc.text(60, 82, f"{labels} · identity sheet", 44, ui["text"], bold=True)
    doc.text(60, 120, "Names and icons per environment, stamped at pack time; technical names never carry an environment", 19, ui["muted"])
    doc.logo(root, width - 60, 40, 52)
    y = 160
    for a in mvps:
        d = a["derived"]
        j = palette["journeys"][a["journey"]]
        bg, fg, lab = status_style(palette, a)
        doc.chip(60, y + 12, lab, bg, fg, 15, 10, 26)
        name = d["displayName"][prod]
        for li, line in enumerate(wrap(name, 29, 310, True, 2)):
            doc.text(60, y + 76 + li * 32, line, 29, ui["text"], bold=True)
        yy = y + 76 + 32 * len(wrap(name, 29, 310, True, 2))
        if a.get("workingName"):
            for line in wrap(f"Working name: {a['workingName']}", 15.5, 310, max_lines=2):
                doc.text(60, yy, line, 15.5, ui["muted"])
                yy += 19
        runs = [("PO ", False, ui["muted"], False), (a["po"], True, ui["text"], False), (" · Domain ", False, ui["muted"], False), (a["domain"], True, ui["text"], False)]
        if a.get("scope"):
            runs += [(" · Scope ", False, ui["muted"], False), (a["scope"], True, ui["text"], False)]
        doc.rich(60, yy + 4, runs, 15.5)
        doc.text(60, yy + 27, f"{a['journey']} · {j['name']}", 15.5, ui["muted"])
        x = 400
        shown = envs if L.is_scoped(a) else [prod]
        for e in shown:
            doc.icon(x, y + 26, 184, L.icon_svg(cfg, palette, lib, a, e), rx=24)
            doc.text(x + 92, y + 232, f"{e} · 192 × 192", 16, ui["muted"], anchor="middle")
            x += 204
        doc.icon(x + 26, y + 104, 32, L.icon_svg(cfg, palette, lib, a, prod), rx=5)
        doc.outline(x + 72, y + 92, 54, L.outline_svg(lib, a))
        doc.text(x + 76, y + 232, "32 colour · 32 outline", 16, ui["muted"], anchor="middle")
        tx, ty = x + 190, y + 38
        for e in L.env_names(cfg):
            if e != prod and not L.is_scoped(a):
                continue
            doc.rich(tx, ty, [(f"{e}  ", False, ui["muted"], False), (d["displayName"][e], True, ui["text"], False)], 16.5)
            ty += 25
        ty += 12
        facts = []
        if d["schemaName"]:
            facts += [("Schema", d["schemaName"]), ("Solution", d["solutionUniqueName"])]
        elif d.get("technical"):
            facts.append((d["technical"]["label"], d["technical"]["value"]))
        facts.append(("Repo folder", f"agents/{d['slug']}/"))
        if d["envVarPrefix"]:
            facts.append(("Variables", f"{d['envVarPrefix']}… · Connections {cfg['naming']['publisherPrefix']}_<Connector>{d['connectionContext']}"))
        for k_, v in facts:
            doc.rich(tx, ty, [(f"{k_} ", False, ui["muted"], False), (v, False, ui["text"], True)], 16)
            ty += 25
        y += row_h
        doc.rect(60, y - 14, width - 120, 1.5, ui["line"])
    bands = " · ".join(f"{e} band {palette['environments'][e].get('brandColour', palette['environments'][e]['band'])}" for e in L.nonprod_envs(cfg))
    doc.text(60, height - 30, f"{cfg.get('status', 'Proposal')} · v{cfg['version']} · {cfg['date']} · publisher prefix {cfg['naming']['publisherPrefix']}", 14, ui["muted"])
    doc.text(width - 60, height - 30, f"{bands} · {prod} clean", 14, ui["muted"], anchor="end")
    return doc.svg(), width, height


# ---------------------------------------------------------------- colour schema

def colour_schema(cfg, palette, lib, by_journey: dict, root: Path) -> tuple[str, int, int]:
    ui = palette["ui"]
    jids = list(by_journey)
    named = palette.get("named", [])[:12]
    width = max(1880, 128 + len(jids) * 290)
    swatch_rows = (len(named) + 9) // 10
    jt = 360 + (swatch_rows - 1) * 130
    height = jt + 470 + 160
    doc = Doc(width, height, palette)
    doc.text(64, 86, "Colour schema per journey", 46, ui["text"], bold=True)
    doc.text(64, 124, f"Built from {palette.get('sourceShort', 'the customer brand')} · every icon meets 4.5:1 contrast", 20, ui["muted"])
    doc.logo(root, width - 64, 42, 56)
    doc.text(64, 188, palette.get("themeLabel", "Brand palette"), 18, ui["muted"], bold=True)
    for i, c in enumerate(named):
        x = 64 + (i % 10) * 166
        y = 206 + (i // 10) * 130
        doc.rect(x, y, 148, 108, c["hex"], rx=8, stroke=ui["line"])
        fg = "#FFFFFF" if L.contrast(c["hex"], "#FFFFFF") >= 3 else ui["text"]
        doc.text(x + 12, y + 26, wrap(c.get("slot") or c["name"], 15, 126, True, 1)[0], 15, fg, bold=True)
        doc.text(x + 12, y + 45, c["hex"], 15, fg)
    doc.text(64, jt, "Journey colours (icon background, glyph, tints)", 18, ui["muted"], bold=True)
    for i, jid in enumerate(jids):
        j = palette["journeys"][jid]
        x = 64 + i * 290
        lead = by_journey[jid][0]
        doc.rect(x, jt + 26, 250, 250, j["background"], rx=24)
        sc = 140 / lib["viewBox"]
        doc.parts.append(f'<g transform="translate({x + 55} {jt + 81}) scale({sc:g})">'
                         f'{L.glyph_svg(lib, lead["glyph"], "filled", j["glyph"], j["background"])}</g>')
        ty = jt + 302
        for line in wrap(f"{jid} · {j['name']}", 20, 250, True, 2):
            doc.text(x, ty, line, 20, ui["text"], bold=True)
            ty += 24
        doc.rich(x, ty, [(f"{j['brandColour']} ", False, ui["muted"], False), (j["background"], False, ui["muted"], True)], 15)
        doc.rich(x, ty + 20, [("Glyph ", False, ui["muted"], False), (j["glyph"], False, ui["muted"], True),
                              (" · contrast ", False, ui["muted"], False), (f"{j['contrast']}:1", True, ui["text"], False)], 15)
        doc.rect(x, ty + 36, 78, 32, j["tint"], rx=5, stroke=ui["line"])
        doc.rect(x + 86, ty + 36, 78, 32, j["tintStrong"], rx=5, stroke=ui["line"])
    ey = height - 140
    doc.text(64, ey, f"Environment markers ({', '.join(L.nonprod_envs(cfg))} only)", 18, ui["muted"], bold=True)
    x = 64
    for e in L.nonprod_envs(cfg):
        m = palette["environments"][e]
        doc.rect(x, ey + 22, 220, 4, m["separator"])
        doc.rect(x, ey + 26, 220, 44, m["band"], stroke=ui["line"])
        label = L.env(cfg, e).get("postfix") or e
        doc.text(x + 110, ey + 57, " ".join(label), 22, m["label"], bold=True, anchor="middle")
        doc.rich(x + 236, ey + 54, [("band ", False, ui["muted"], False), (m["band"], False, ui["muted"], True),
                                     (" · label ", False, ui["muted"], False), (m["label"], False, ui["muted"], True),
                                     (f" · {L.contrast(m['band'], m['label'])}:1", False, ui["muted"], False)], 15)
        x += 600
    doc.text(64, height - 26, f"{cfg.get('status', 'Proposal')} · {palette.get('status', '')} · v{cfg['version']} · {cfg['date']}", 14, ui["muted"])
    return doc.svg(), width, height


# ---------------------------------------------------------------- SVG -> PNG (optional)

def _sharp_module():
    candidates = []
    npm = shutil.which("npm")
    try:
        root = subprocess.run([npm, "root", "-g"], capture_output=True, text=True, timeout=20).stdout.strip() if npm else ""  # nosec B603
        if root:
            candidates.append(os.path.join(root, "sharp"))
    except (OSError, subprocess.SubprocessError):
        pass
    candidates += ["/usr/lib/node_modules/sharp", "/usr/local/lib/node_modules/sharp"]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return None


def svgs_to_png(jobs: list) -> tuple[int, str | None]:
    """jobs: [(svg_path, png_path, width, height)]. Returns (count, method) - (0, None) when no converter exists."""
    if not jobs:
        return 0, None
    try:
        import cairosvg  # type: ignore
        for s, p, w, h in jobs:
            cairosvg.svg2png(url=str(s), write_to=str(p), output_width=w, output_height=h)
        return len(jobs), "cairosvg"
    except ImportError:
        pass
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        for s, p, w, h in jobs:
            subprocess.run([rsvg, "-w", str(w), "-h", str(h), "-o", str(p), str(s)], check=True)  # nosec B603
        return len(jobs), "rsvg-convert"
    node = shutil.which("node")
    sharp = _sharp_module() if node else None
    if sharp:
        with tempfile.TemporaryDirectory() as tmp:
            jf = Path(tmp) / "jobs.json"
            jf.write_text(json.dumps([[str(s), str(p), w, h] for s, p, w, h in jobs]), encoding="utf-8")
            js = Path(tmp) / "render.js"
            js.write_text("const sharp=require(process.argv[2]);const jobs=require(process.argv[3]);"
                          "(async()=>{for(const [s,p,w,h] of jobs){await sharp(s).resize(w,h).png({compressionLevel:9}).toFile(p);}})()"
                          ".catch(e=>{console.error(e);process.exit(1);});", encoding="utf-8")
            subprocess.run([node, str(js), sharp, str(jf)], check=True, capture_output=True, timeout=600)  # nosec B603
        return len(jobs), "sharp"
    return 0, None
