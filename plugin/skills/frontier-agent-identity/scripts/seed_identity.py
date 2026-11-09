#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Seeds the agent identity config from a Frontier Company Blueprint and the customer's brand.

Usage:
  python seed_identity.py --blueprint blueprint.json [--brand brand.json] --out-dir working/identity/<slug>/config
         [--prefix cal] [--envs DEV,TEST,PROD] [--po "D1=Sales,D2=Procurement"] [--no-data-agents]
         [--version 1.0.0] [--date 2026-10-30]

Writes agent-identity.json and palette.json (the inputs of the identity kit) and seed-report.md: every
assumption, every shortened name and every glyph choice, for review with the customer. Nothing here is
final: PO tokens are proposals, names marked "shortened" need a human choice, and without a brand file
the blueprint colours are used and flagged.
"""
from __future__ import annotations

import argparse
import colorsys
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kit" / "scripts"))
import identity_lib as L  # noqa: E402

FILLER = {"and", "for", "of", "the", "to", "with", "&"}
DROP = {"agent", "bot", "copilot", "agents"}
DATA_GLYPHS = ["database-search", "data-bar-vertical", "data-pie", "data-trending"]
FALLBACK = {"orchestrator": ["flow", "organization", "target-arrow", "sparkle"],
            "specialist": ["sparkle", "task-list-ltr", "clipboard-text-edit", "person-chat", "lightbulb", "gear"],
            "data": DATA_GLYPHS}
ENV_DEFAULTS = {
    "DEV": ("DEV · ", "DEV build - synthetic data only, not for production use."),
    "TEST": ("TEST · ", "TEST build - synthetic or approved test data only, not for production use."),
    "UAT": ("UAT · ", "UAT build - approved test data only, not for production use."),
    "SIT": ("SIT · ", "SIT build - synthetic test data only, not for production use."),
    "PREPROD": ("PREPROD · ", "PREPROD build - production-like data under test, not for daily use."),
}
BAND_FALLBACK = [("#B3541E", "#FFFFFF", "accessible orange"), ("#9BCBEB", "#1B2A33", "light blue"),
                 ("#5C2E91", "#FFFFFF", "violet"), ("#FFE38A", "#3B3B3B", "light yellow")]


# ---------------------------------------------------------------- helpers

def words(text: str) -> list:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9']*", text or "")


def clean_token(text: str, max_len: int = 18) -> str:
    w = [x for x in words(text) if x.lower() not in FILLER]
    tok = " ".join(w) or "Area"
    while len(tok) > max_len and len(w) > 1:
        w = w[:-1]
        tok = " ".join(w)
    return tok


def pascal(text: str) -> str:
    return "".join(x if x.isupper() else x[:1].upper() + x[1:] for x in words(text))


def short_sentence(text: str, limit: int = 72) -> str:
    """First sentence within the limit; cut at a clause boundary (comma, 'and', 'then') before a word boundary."""
    t = re.split(r"(?<=[.;])\s", (text or "").strip())[0].rstrip(".; ")
    if not t:
        return ""
    if len(t) + 1 <= limit:
        return t + "."
    head = t[:limit - 1]
    for sep in (", ", " and ", " then ", " so ", " to "):
        i = head.rfind(sep)
        if i >= limit * 0.45:
            return head[:i].rstrip(",;:- ") + "."
    cut = head.rsplit(" ", 1)[0].rstrip(",;:- ")
    while cut.split() and cut.split()[-1].lower() in FILLER | {"a", "an", "in", "on", "by", "or"}:
        cut = cut.rsplit(" ", 1)[0]
    return cut + "."


def domain_token(name: str, po: str, role: str, max_base: int, lead_word: str = "Lead"):
    w = [x for x in words(name) if x.lower() not in DROP]
    pw = po.lower().split()
    if [x.lower() for x in w[:len(pw)]] == pw:
        w = w[len(pw):]
    if role == "orchestrator" and (not w or w[-1].lower() != lead_word.lower()):
        w = [x for x in w if x.lower() != lead_word.lower()] + [lead_word]
    if not w:
        w = ["Assistant"]
    full = " ".join(w)

    def fits(dom):
        return len(f"{po} {dom}") <= max_base and len(dom.split()) <= 3

    if fits(full):
        return full, None
    core = [x for x in w if x.lower() not in FILLER]
    alts = []
    if role == "orchestrator":
        alts = [lead_word]
    if len(core) >= 3:
        alts += [" ".join(core[:2]), " ".join(core[-2:])]
    if len(core) >= 2:
        alts += [" ".join(core[1:]), core[-1], core[0]]
    for alt in alts:
        if alt and fits(alt):
            return alt, f"shortened from '{po} {full}' to fit {max_base} characters - choose the best 1-3 words with the process owner"
    room = max(3, max_base - len(po) - 1)
    return full[:room].rstrip(), f"truncated from '{po} {full}' - choose a shorter domain"


def detect_kind(tech: str) -> str:
    t = (tech or "").lower()
    hits = []
    for kind, keys in (("copilot-studio", ["copilot studio"]), ("foundry-agent", ["foundry"]),
                       ("declarative-agent", ["declarative", "agent builder"]), ("fabric-data-agent", ["fabric data agent"]),
                       ("ess", ["employee self-service", "self-service agent", " ess "]), ("repository-agent", ["github copilot custom", "repository agent"])):
        for k in keys:
            i = t.find(k)
            if i >= 0:
                hits.append((i, kind))
    return min(hits)[1] if hits else "copilot-studio"


# ---------------------------------------------------------------- colours

def _hue_dist(a: str, b: str) -> float:
    ra, ga, ba = (int(a[i:i + 2], 16) / 255 for i in (1, 3, 5))
    rb, gb, bb = (int(b[i:i + 2], 16) / 255 for i in (1, 3, 5))
    ha, la, sa = colorsys.rgb_to_hls(ra, ga, ba)
    hb, lb, sb = colorsys.rgb_to_hls(rb, gb, bb)
    dh = min(abs(ha - hb), 1 - abs(ha - hb))
    return dh * 4 + abs(la - lb) + abs(sa - sb) * 0.5


def _is_warm(hexv: str) -> bool:
    r, g, b = (int(hexv[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h < 0.13 or h > 0.96) and s > 0.35 and 0.2 < l < 0.75


def build_palette(blueprint: dict, brand: dict | None, envs: list, prod: str) -> tuple[dict, list]:
    notes = []
    domains = blueprint["domains"]
    if brand and brand.get("named"):
        named = [dict(n, hex=L.norm_hex(n["hex"])) for n in brand["named"]]
    else:
        named = [{"name": f"Blueprint {d['id']}", "hex": L.norm_hex(d.get("color") or "#0F6CBD"), "source": "blueprint colour (no brand file)"} for d in domains]
        notes.append("No brand file: journey colours come from the blueprint. Collect the customer's Office theme or brand guide and seed again.")
    theme = (brand or {}).get("theme") or {}
    darks = sorted([n for n in named if L.luminance(n["hex"]) < 0.08], key=lambda n: L.luminance(n["hex"]))
    dark = darks[0]["hex"] if darks else "#1F2A33"
    candidates = [n for n in named if L.luminance(n["hex"]) < 0.85]
    overrides = (brand or {}).get("journeyColours") or {}
    used, journeys = set(), {}
    for d in domains:
        jid = d["id"]
        target = L.norm_hex(d.get("color") or "#0F6CBD")
        pick = None
        if jid in overrides:
            want = overrides[jid]
            want_hex = L.norm_hex(want) if want.startswith("#") else None
            pick = next((n for n in named if n["name"] == want or (want_hex and n["hex"] == want_hex)), None)
        if pick is None:
            pool = [n for n in candidates if n["hex"] not in used] or candidates or named
            pick = min(pool, key=lambda n: _hue_dist(n["hex"], target))
        used.add(pick["hex"])
        bg, glyph, note = pick["hex"], "#FFFFFF", None
        if L.contrast(bg, "#FFFFFF") < 4.5:
            if L.contrast(bg, dark) >= 4.5:
                glyph = dark
                note = f"dark glyph {dark} on {pick['name']}: white would reach only {L.contrast(bg, '#FFFFFF')}:1"
            else:
                shade = L.accessible_shade(bg)
                note = f"{pick['name']} {bg} reaches only {L.contrast(bg, '#FFFFFF')}:1 with white; accessible shade {shade} used"
                bg = shade
        text_on_white = bg if L.contrast(bg, "#FFFFFF") >= 4.5 else glyph
        jname = re.sub(r"\s+journey$", "", (d.get("journey_name") or d["name"]).strip(), flags=re.I)
        journeys[jid] = {"name": jname, "short": d.get("short_name") or d["name"],
                         "brandColour": pick["name"], "background": bg, "glyph": glyph,
                         "themeSlot": pick.get("slot", "-"), "contrast": L.contrast(bg, glyph),
                         "tint": L.mix(bg, "#FFFFFF", 0.88), "tintStrong": L.mix(bg, "#FFFFFF", 0.70),
                         "textOnWhite": text_on_white, "blueprintColour": target}
        if note:
            journeys[jid]["note"] = note
    # environment markers: first non-production = warm band, last non-production = light band
    nonprod = [e for e in envs if e != prod]
    env_markers, fallback = {prod: None}, list(BAND_FALLBACK)
    warm = [n for n in named if _is_warm(n["hex"])]
    light = sorted([n for n in named if 0.3 < L.luminance(n["hex"]) < 0.78 and not _is_warm(n["hex"])],
                   key=lambda n: abs(L.luminance(n["hex"]) - 0.55))
    for i, e in enumerate(nonprod):
        chosen = None
        if i == 0 and warm:
            n = warm[0]
            band = n["hex"] if L.contrast(n["hex"], "#FFFFFF") >= 4.5 else L.accessible_shade(n["hex"])
            chosen = {"band": band, "label": "#FFFFFF", "brandColour": n["name"] + ("" if band == n["hex"] else " (accessible shade)")}
        elif i == len(nonprod) - 1 and light:
            n = next((x for x in light if L.contrast(x["hex"], dark) >= 4.5), None)
            if n:
                chosen = {"band": n["hex"], "label": dark, "brandColour": n["name"]}
        if not chosen:
            band, label, nm = fallback.pop(0 if i == 0 else min(1, len(fallback) - 1)) if fallback else ("#5C5C5C", "#FFFFFF", "grey")
            chosen = {"band": band, "label": label, "brandColour": f"neutral {nm} (not a brand colour)"}
            notes.append(f"{e} band uses a neutral {nm}: no suitable brand colour found")
        chosen.update({"separator": "#FFFFFF", "labelContrast": L.contrast(chosen["band"], chosen["label"])})
        env_markers[e] = chosen
    accent = L.norm_hex(theme.get("accent1") or (named[0]["hex"] if named else "#0F6CBD"))
    if L.contrast(accent, "#FFFFFF") < 4.5:
        accent = L.accessible_shade(accent)
    greens = [n["hex"] for n in named if 0.25 < colorsys.rgb_to_hls(*(int(n["hex"][i:i + 2], 16) / 255 for i in (1, 3, 5)))[0] < 0.45
              and L.contrast(n["hex"], "#FFFFFF") >= 4.5]
    fonts = theme.get("fonts") or {}
    ui = {"text": dark if L.luminance(dark) < 0.03 else "#242424", "muted": "#5F6B73", "background": "#F7F8FA", "line": "#D9DEE2",
          "accent": accent, "dark": dark if L.luminance(dark) < 0.08 else "#2B2B2B",
          "headingFont": fonts.get("headings", "Arial"), "bodyFont": fonts.get("body", "Arial")}
    status = {
        "mvp": {"bg": accent, "fg": "#FFFFFF", "label": "MVP"},
        "validated": {"bg": greens[0] if greens else "#107C41", "fg": "#FFFFFF", "label": "Validated"},
        "adjusted": {"bg": "#FFF4CE", "fg": "#5C4400", "label": "Adjusted"},
        "hypothesis": {"bg": "#E6E9EC", "fg": "#3D4A52", "label": "Hypothesis"},
        "later": {"bg": L.mix(accent, "#FFFFFF", 0.86), "fg": accent, "label": "Later wave"},
        "deferred": {"bg": "#FBE3D6", "fg": "#8A3A12", "label": "Deferred"},
        "out-of-scope": {"bg": "#E6E9EC", "fg": "#3D4A52", "label": "Out of scope"},
        "repository": {"bg": ui["dark"], "fg": "#FFFFFF", "label": "Repository"},
        "data": {"bg": "#E8EEF4", "fg": "#26445E", "label": "Data agent"},
    }
    src = (brand or {}).get("sources") or {}
    short = (brand or {}).get("short") or blueprint["meta"].get("short", "")
    theme_name = theme.get("name")
    palette = {
        "schema": "frontier-agent-palette/1.0",
        "sources": src or {"blueprint": "blueprint journey colours (no brand file)"},
        "status": (brand or {}).get("status") or "Derived from the customer's own brand sources; validate with the brand owner before production.",
        "sourceShort": (brand or {}).get("sourceShort") or (f"{short}'s Office theme '{theme_name}'" if theme_name else "the blueprint colours"),
        "themeLabel": f"{short} theme '{theme_name}'" if theme_name else f"{short} palette",
        "theme": theme, "website": (brand or {}).get("website") or {},
        "named": named, "journeys": journeys, "environments": env_markers, "ui": ui, "statusStyles": status,
        "wordmark": short, "logo": (brand or {}).get("logo"),
    }
    return palette, notes


# ---------------------------------------------------------------- glyphs

def choose_glyphs(agents: list, lib: dict, texts: dict) -> dict:
    """Greedy, unique where possible. Order: MVP agents, specialists, journey leads, data agents, so the
    most specific agents take the most specific glyphs. Text tiers: the agent's own words (weight 5),
    journey words (3, leads and data agents only), description (1.5)."""
    def hit(k: str, text: str) -> bool:
        return re.search(rf"\b{re.escape(k)}(?:s|es)?\b", text) is not None

    def score(g: dict, a: dict) -> float:
        own, journey, desc = texts[a["id"]]
        s = 0.0
        for kw in g["keywords"]:
            k = kw.lower()
            bonus = 1.0 if " " in k else 0.0
            if hit(k, own):
                s += 5 + bonus
            elif journey and hit(k, journey):
                s += 3 + bonus
            elif hit(k, desc):
                s += 1.5 + bonus
        return s
    rank = {"specialist": 1, "orchestrator": 2, "data": 3}
    order = sorted(agents, key=lambda a: (0 if a.get("statusClass") == "mvp" else rank[a["role"]], a["id"]))
    used, out = set(), {}
    for a in order:
        names = DATA_GLYPHS if a["role"] == "data" else list(lib["glyphs"])
        ranked = sorted(names, key=lambda n: (-score(lib["glyphs"][n], a), n))
        pick = next((n for n in ranked if n not in used and score(lib["glyphs"][n], a) > 0), None)
        if pick is None:
            pick = next((n for n in FALLBACK[a["role"]] if n not in used), FALLBACK[a["role"]][0])
        used.add(pick)
        out[a["id"]] = pick
    return out


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--blueprint", required=True)
    ap.add_argument("--brand")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--prefix", help="Power Platform publisher prefix (2-8 lower-case letters or digits)")
    ap.add_argument("--envs", default="DEV,TEST,PROD", help="ordered environments, production last")
    ap.add_argument("--po", default="", help='PO token per journey, e.g. "D1=Sales,D2=Procurement"')
    ap.add_argument("--no-data-agents", action="store_true")
    ap.add_argument("--version", default="1.0.0")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args(argv)
    bp = json.loads(Path(a.blueprint).read_text(encoding="utf-8"))
    brand = json.loads(Path(a.brand).read_text(encoding="utf-8")) if a.brand else None
    lib = L.load_json(HERE.parent / "kit" / "scripts" / "glyphs" / "glyphs.json")
    meta = bp["meta"]
    customer, short = meta.get("customer", "Customer"), meta.get("short") or meta.get("customer", "Customer").split()[0]
    envs = [e.strip().upper() for e in a.envs.split(",") if e.strip()]
    prod = envs[-1]
    report = []
    prefix = (a.prefix or re.sub(r"[^a-z]", "", short.lower())[:3] or "cst").lower()
    if not re.fullmatch(r"[a-z][a-z0-9]{1,7}", prefix):
        print(f"ERROR publisher prefix {prefix!r}: 2-8 lower-case letters or digits, starting with a letter")
        return 1
    environments = []
    for e in envs:
        sp, banner = ENV_DEFAULTS.get(e, (f"{e} · ", f"{e} build - not for production use."))
        item = {"name": e, "postfix": "" if e == prod else e, "shortPrefix": "" if e == prod else sp, "fullBanner": "" if e == prod else banner}
        if e == prod:
            item["production"] = True
        environments.append(item)
    po_map = dict(x.split("=", 1) for x in a.po.split(",") if "=" in x)
    leaders = {l["id"]: l for l in bp.get("leaders", [])}
    cfg = {"schema": "frontier-agent-identity/1.0", "version": a.version, "date": a.date,
           "status": f"proposal for {short} approval",
           "customer": {"name": customer, "short": short},
           "source": {"blueprint": meta.get("id"), "blueprintVersion": meta.get("version"), "blueprintStatus": meta.get("status")},
           "familyLabel": short,
           "naming": {"displayTemplate": "{po} {domain} {scope} {env}", "maxDisplayLength": 30, "maxBaseLength": 0,
                      "publisherPrefix": prefix,
                      "prefixDecision": "proposal - confirm with the Power Platform team (decision N-3)" if not a.prefix else "given",
                      "solutionPrefix": prefix.upper(), "solutionDisplayPrefix": f"{short} ", "fullNamePrefix": f"{short} ",
                      "stripLeadingFromStem": [], "allowedDisplayCharacters": "^[A-Za-z][A-Za-z0-9 '\\-]*$", "orchestratorDomain": "Lead"},
           "environments": environments, "poAreas": [], "repository": {"identityRoot": "identity"},
           "decisions": [], "evidence": [], "changelog": [], "agents": []}
    max_base = L.max_base_length(cfg)
    cfg["naming"]["maxBaseLength"] = max_base
    mvp_by_name = {}
    for opt in bp.get("mvp_options", []):
        for d in bp["domains"]:
            for ag in d.get("agents", []):
                if ag["name"] in (opt.get("use_case") or ""):
                    mvp_by_name[ag["name"]] = f"MVP {opt.get('option', '')}".strip()
    for d in bp["domains"]:
        for uc in d.get("use_cases", []):
            if uc.get("mvp"):
                for nm in uc.get("agents", []):
                    mvp_by_name.setdefault(nm, "MVP")
    texts, agents = {}, []
    for d in bp["domains"]:
        jid = d["id"]
        po = clean_token(po_map.get(jid) or d.get("short_name") or d["name"])
        leader = leaders.get(d.get("leader"), {})
        area = next((p for p in cfg["poAreas"] if p["token"] == po), None)
        if area:
            area["journeys"].append(jid)
        else:
            cfg["poAreas"].append({"token": po, "code": pascal(po), "processOwner": leader.get("role", "to be named"),
                                   "journeys": [jid], "evidence": [], "assumed": jid not in po_map})
        personas = [p.get("role") for p in d.get("personas", []) if isinstance(p, dict) and p.get("role")]
        items = []
        if d.get("orchestrator"):
            items.append(("orchestrator", d["orchestrator"]))
        items += [("specialist", x) for x in d.get("agents", [])]
        if d.get("data_agent") and not a.no_data_agents:
            da = dict(d["data_agent"])
            da.setdefault("id", f"{jid}-DATA")
            da.setdefault("capability", "Answers questions over " + ", ".join(da.get("products", [])[:4]) if da.get("products") else "Answers questions over the journey's data")
            da.setdefault("technology", "Fabric data agent")
            items.append(("data", da))
        for role, ag in items:
            dom, note = domain_token(ag["name"], po, role, max_base)
            # Agent Factory agents live in the factory repository and pipelines: repository agents, not environment-scoped
            kind = ("repository-agent" if d.get("kind") == "factory" else detect_kind(ag.get("technology", ""))) if role != "data" else "fabric-data-agent"
            mvp = mvp_by_name.get(ag["name"])
            st = (ag.get("status") or "").lower()
            if mvp:
                status_class, status = "mvp", f"Blueprint MVP · {mvp}"
            elif role == "data":
                status_class, status = "data", "Data agent for the journey"
            elif st in ("validated", "adjusted"):
                status_class, status = st, f"{st.capitalize()} in the workshop"
            elif st in ("rejected", "out-of-scope"):
                status_class, status = "out-of-scope", "Out of scope after the workshop"
            elif (ag.get("horizon") or "").upper() == "H3":
                status_class, status = "later", "Hypothesis · later wave (H3)"
            else:
                status_class, status = "hypothesis", f"Hypothesis · {ag.get('horizon') or 'H1'}"
            cap = (ag.get("capability") or ag.get("mission") or "").strip().rstrip(".")
            full = cap + "."
            if ag.get("outcome"):
                full += f" Outcome: {ag['outcome'].rstrip('.')}."
            if ag.get("trigger"):
                full += f" Trigger: {ag['trigger'].rstrip('.')}."
            full += f" Process owner area: {po}. Status: {status}."
            limit = L.KINDS[kind]["descMax"] - 120
            if len(full) > limit:
                full = full[:limit].rsplit(" ", 1)[0] + "…"
            agent = {"id": ag.get("id") or f"{jid}-{len(agents) + 1:02d}", "journey": jid, "role": role,
                     "blueprintName": ag["name"], "workingName": None, "po": po, "domain": dom, "scope": "",
                     "kind": kind, "environmentScoped": L.KINDS[kind]["scoped"], "status": status, "statusClass": status_class,
                     "mvp": mvp, "glyph": "", "shortDescription": short_sentence(cap) or f"{dom} for {po}.",
                     "fullDescription": full, "audience": ", ".join(personas[:3]) or leader.get("role", ""),
                     "owner": ag.get("owner") or leader.get("role") or "", "channels": ag.get("channels") or [],
                     "evidence": [s for s in (ag.get("src") or d.get("src") or []) if isinstance(s, str)],
                     "notes": note, "overrides": {}}
            if role == "orchestrator":
                agent["shortDescription"] = short_sentence(f"Routes {po} requests to the right {d.get('short_name') or d['name']} specialist agent")
            po_words = {w.lower() for w in words(po)}
            own = " ".join(w for w in words(ag["name"] + " " + dom) if w.lower() not in po_words | DROP | {"lead"} or role != "specialist")
            journey_text = " ".join([d.get("journey_name", ""), d["name"], d.get("short_name", ""), leader.get("role", "")]) if role != "specialist" else ""
            desc_text = " ".join([cap, ag.get("outcome", ""), ag.get("trigger", "")])
            texts[agent["id"]] = (own.lower(), journey_text.lower(), desc_text.lower())
            agents.append(agent)
            if note:
                report.append(f"- **{agent['id']}** {ag['name']}: {note}.")
    glyphs = choose_glyphs(agents, lib, texts)
    for ag in agents:
        ag["glyph"] = glyphs[ag["id"]]
    cfg["agents"] = agents
    palette, notes = build_palette(bp, brand, envs, prod)
    ev = [{"id": e["id"], "title": e.get("title", ""), "date": e.get("date", ""), "usedFor": "blueprint evidence"}
          for e in bp.get("evidence", []) if e.get("visibility", "internal") == "customer"]
    cfg["evidence"] = ev + (brand or {}).get("evidence", [])
    cfg["decisions"] = [
        {"id": "N-1", "decision": "Meaning of <PO> (process-owner area assumed)", "owner": "business sponsor of the agent programme", "when": "before the first DEV save"},
        {"id": "N-2", "decision": "PO tokens and abbreviations: " + ", ".join(p["token"] for p in cfg["poAreas"]), "owner": "process owners", "when": "envisioning or prototype workshop"},
        {"id": "N-3", "decision": f"Publisher prefix '{prefix}'", "owner": "Power Platform team", "when": "before the first DEV save"},
        {"id": "N-4", "decision": "Display names of the MVP agents", "owner": "business process owners", "when": "before the first DEV save"},
        {"id": "N-5", "decision": "Journey colours confirmed against the brand guide", "owner": "brand owner (communications)", "when": "before TEST"},
        {"id": "N-6", "decision": "Environment names and stages (" + ", ".join(envs) + ")", "owner": "platform team", "when": "before TEST"},
    ]
    cfg["changelog"] = [{"version": a.version, "date": a.date,
                         "items": [f"First version: naming convention for {len(agents)} agents in {len(bp['domains'])} journeys, seeded from blueprint {meta.get('id')} v{meta.get('version')}.",
                                   "Colour schema per journey from the customer's brand, contrast-checked; environment markers for " + ", ".join(e for e in envs if e != prod) + ".",
                                   "Icons per agent and environment, identity cards, visuals, catalogue; validate, stamp and test scripts; pipeline templates; GitHub Copilot instructions."]}]
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    L.save_json(out / "agent-identity.json", cfg)
    L.save_json(out / "palette.json", palette)
    lines = [f"# Identity seed report - {customer}\n",
             f"Seeded {a.date} from blueprint `{meta.get('id')}` v{meta.get('version')} ({meta.get('status')}). "
             f"{len(agents)} agents in {len(bp['domains'])} journeys; environments {', '.join(envs)}; publisher prefix `{prefix}` ({cfg['naming']['prefixDecision']}).\n",
             "## Review before building\n"]
    assumed = [p for p in cfg["poAreas"] if p["assumed"]]
    if assumed:
        lines.append("- PO tokens are proposals from the journey names: " + ", ".join(f"{p['token']} ({', '.join(p['journeys'])})" for p in assumed) + ".")
    lines += [f"- {n}" for n in notes]
    lines += report or ["- No name had to be shortened."]
    lines += ["\n## Proposed names\n", "| ID | Blueprint name | Display name | Kind | Glyph | Status |", "|---|---|---|---|---|---|"]
    for ag in agents:
        lines.append(f"| {ag['id']} | {ag['blueprintName']} | {L.base_name(cfg, ag)} | {ag['kind']} | {ag['glyph']} | {ag['status']} |")
    lines += ["\n## Journey colours\n", "| Journey | Colour | Glyph | Contrast | Note |", "|---|---|---|---|---|"]
    for jid, j in palette["journeys"].items():
        lines.append(f"| {jid} {j['name']} | {j['brandColour']} `{j['background']}` | `{j['glyph']}` | {j['contrast']}:1 | {j.get('note', '')} |")
    (out / "seed-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"agents": len(agents), "journeys": len(bp["domains"]), "shortened": len(report), "prefix": prefix,
                      "out": str(out)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
