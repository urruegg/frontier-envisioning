#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Stamps environment-specific agent names and icons into an UNPACKED Power Platform solution, before packing.

Why: an agent imported as managed can't be renamed in the target environment, so names and icons are
stamped into the package before it is packed. The release stage stamps each test environment's names
and packs, then stamps the production names and packs. Stamping production is also the export
normaliser: it turns "... DEV" names from a development export back into the canonical names kept in Git.

What it changes (Copilot Studio agents only; everything else is left untouched)
  bots/<schemaname>/bot.xml   <name>            -> display name for the environment
                              <iconbase64>      -> colour icon for the environment (PNG, base64)
                              <applicationmanifestinformation> (only if present; JSON)
                                                -> teams.colorIcon / teams.outlineIcon, when those keys exist
The bot.xml element names follow Microsoft's published unpacked samples (CopilotStudioSamples,
bots/*/bot.xml). Verify once against your first real export: the dry run prints what would change.

Usage
  python scripts/stamp_identity.py --env TEST --solution-dir out/unpacked/<Solution>            # dry run
  python scripts/stamp_identity.py --env TEST --solution-dir out/unpacked/<Solution> --apply --strict \\
         --report out/identity-stamp-TEST.json
Exit codes: 0 ok, 1 error, 2 strict mode and an agent in the solution has no identity entry.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import identity_lib as L  # noqa: E402

RX_SCHEMA = re.compile(r'<bot\s[^>]*schemaname="([^"]+)"')


def element(xml: str, tag: str):
    return re.search(rf"<{tag}>(.*?)</{tag}>", xml, re.S)


def set_element(xml: str, tag: str, value_escaped: str):
    m = element(xml, tag)
    if not m:
        return xml, False
    return xml[:m.start(1)] + value_escaped + xml[m.end(1):], True


def find_agent(cfg: dict, schema: str):
    """Exact schema name, or the schema name plus a short suffix the platform appended on first save."""
    s = schema.lower()
    best = None
    for a in cfg["agents"]:
        sn = ((a.get("derived") or {}).get("schemaName") or "").lower()
        if not sn:
            continue
        if s == sn or s.startswith(sn + "_") or (s.startswith(sn) and len(s) - len(sn) <= 6):
            if best is None or len(sn) > len(best["derived"]["schemaName"]):
                best = a
    return best


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--env", required=True, help="environment name from config/agent-identity.json, e.g. DEV, TEST, PROD")
    ap.add_argument("--solution-dir", required=True, help="folder produced by 'pac solution unpack'")
    ap.add_argument("--root", default=str(L.ROOT), help="identity package root (config/ and agents/)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--strict", action="store_true", help="fail when a bot in the solution has no identity entry")
    ap.add_argument("--report", help="write a JSON report")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    cfg, _ = L.load_config(root)
    if args.env not in L.env_names(cfg):
        print(f"Unknown environment {args.env!r}; configured: {', '.join(L.env_names(cfg))}")
        return 1
    sol = Path(args.solution_dir).resolve()
    bots = sorted(sol.rglob("bots/*/bot.xml"))
    results, unmatched = [], []
    if not bots:
        print(f"No bots/*/bot.xml found under {sol} - nothing to stamp.")
    for bx in bots:
        xml = bx.read_text(encoding="utf-8")
        m = RX_SCHEMA.search(xml)
        schema = m.group(1) if m else bx.parent.name
        agent = find_agent(cfg, schema)
        if not agent:
            unmatched.append(schema)
            results.append({"bot": bx.relative_to(sol).as_posix(), "schema": schema, "status": "no identity entry"})
            continue
        d = agent["derived"]
        folder = root / "agents" / d["slug"] / "identity"
        sfx = L.env_suffix(cfg, args.env) if L.is_scoped(agent) else ""
        icon = folder / f"color-192{sfx}.png"
        outline = folder / "outline-32.png"
        new_name = d["displayName"][args.env]
        changes = []
        old_m = element(xml, "name")
        old_name = html.unescape(old_m.group(1)) if old_m else None
        xml2, ok = set_element(xml, "name", html.escape(new_name, quote=False))
        if not ok:
            changes.append("WARN no <name> element")
        elif old_name != new_name:
            changes.append(f"name: {old_name!r} -> {new_name!r}")
        if icon.exists():
            b64 = base64.b64encode(icon.read_bytes()).decode("ascii")
            old_icon = element(xml2, "iconbase64")
            xml2, ok = set_element(xml2, "iconbase64", b64)
            if not ok:
                changes.append("WARN no <iconbase64> element (set the icon in Copilot Studio once, then export again)")
            elif old_icon.group(1).strip() != b64:
                changes.append(f"iconbase64: {icon.name}")
        else:
            changes.append(f"WARN icon file missing: {icon}")
        ami = element(xml2, "applicationmanifestinformation")
        if ami:
            try:
                manifest = json.loads(html.unescape(ami.group(1)))
                teams = manifest.get("teams") if isinstance(manifest, dict) else None
                touched = []
                if isinstance(teams, dict):
                    if "colorIcon" in teams and icon.exists():
                        teams["colorIcon"] = base64.b64encode(icon.read_bytes()).decode("ascii")
                        touched.append("teams.colorIcon")
                    if "outlineIcon" in teams and outline.exists():
                        teams["outlineIcon"] = base64.b64encode(outline.read_bytes()).decode("ascii")
                        touched.append("teams.outlineIcon")
                if touched:
                    xml2, _ = set_element(xml2, "applicationmanifestinformation",
                                          html.escape(json.dumps(manifest, ensure_ascii=False), quote=False))
                    changes.append("applicationmanifestinformation: " + ", ".join(touched))
                else:
                    changes.append("INFO applicationmanifestinformation without teams icon keys - set the icons in the Teams channel once")
            except (ValueError, TypeError) as exc:
                changes.append(f"WARN applicationmanifestinformation is not JSON ({exc}); left unchanged")
        status = "unchanged" if xml2 == xml else ("stamped" if args.apply else "would stamp")
        if args.apply and xml2 != xml:
            bx.write_text(xml2, encoding="utf-8", newline="")
        results.append({"bot": bx.relative_to(sol).as_posix(), "schema": schema, "agent": agent["id"],
                        "env": args.env, "displayName": new_name, "status": status, "changes": changes})

    for r in results:
        print(f'{r["status"]:12} {r["schema"]:40} {r.get("displayName", "")}')
        for c in r.get("changes", []):
            print(f'{"":12}   - {c}')
    if args.report:
        Path(args.report).write_text(json.dumps({"env": args.env, "apply": args.apply, "results": results}, indent=2), encoding="utf-8")
    if unmatched:
        print(f"{len(unmatched)} bot(s) without an identity entry: {', '.join(unmatched)}")
        if args.strict:
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
