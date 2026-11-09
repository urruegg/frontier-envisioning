#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Turn a meeting or workshop transcript into speaker turns plus envisioning signals.

Accepts:
  * WebVTT (.vtt) as returned by GetMeetingTranscript or downloaded from Teams
    (speaker in <v Name> tags or "Name:" prefixes)
  * plain text / markdown with "Name: text", "[00:12:31] Name: text" or
    "Name  0:03" + next-line text (Teams .docx export pasted as text)
  * .docx Teams transcript downloads (read as XML from the zip; nothing is executed)
  * JSON with a "content" string (a saved tool result)

Output JSON (stdout or --out):
  {"source": ..., "evidence_id": "E05", "turns": [{"i", "start", "end", "speaker", "text"}],
   "speakers": {"Name": {"turns", "words", "seconds"}},
   "signals": [{"turn", "start", "speaker", "category", "match", "text"}],
   "stats": {...}}

Signal categories (English and German keywords): pain, metric, system, goal,
decision, action, risk, idea, stakeholder. Signals are pointers for the reader,
not conclusions: every fact that goes into the context pack is still read and
judged from the turn text, and cited as "<evidence_id> @ <start>".

Standard library only. The file is read as data; no network access, no execution.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import zipfile
from pathlib import Path

TS = r"(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?"
CUE = re.compile(rf"^\s*({TS})\s*-->\s*({TS})")
VTAG = re.compile(r"<v(?:\.[^ >]+)?\s+([^>]+)>(.*?)(?:</v>|$)", re.S)
PREFIX = re.compile(rf"^\s*(?:\[?({TS})\]?\s*[-\u2013]?\s*)?([A-Z\u00c4\u00d6\u00dc][\w.'\u2019\- ]{{1,60}}?)\s*:\s+(.+)$")
DOCX_HEAD = re.compile(rf"^\s*([A-Z\u00c4\u00d6\u00dc][\w.'\u2019\- ,()]{{1,80}}?)\s{{2,}}({TS})\s*$")
TAGS = re.compile(r"<[^>]+>")

SIGNALS = {
    "pain": r"\b(problem|issue|pain|challenge|manual(ly)?|slow|delay|error|frustrat\w*|workaround|re-?key\w*|bottleneck|takes (days|weeks|hours)|"
            r"Herausforderung|Problem\w*|manuell|langsam|Fehler|Aufwand|m\u00fchsam|Verz\u00f6gerung|doppelt erfass\w*)\b",
    "metric": r"(\b\d[\d'\u2019.,]*\s?(%|percent|Prozent|CHF|EUR|USD|\u20ac|\$|k\b|M\b|Mio\.?|million|Millionen|bn|hours?|Stunden|days?|Tage[n]?|weeks?|Wochen|"
              r"months?|Monate[n]?|FTEs?|people|Personen|Mitarbeitende|employees|users|Nutzer\w*|suppliers|Lieferanten|tickets|orders|Auftr\u00e4ge|"
              r"technicians|Techniker\w*|visits|Eins\u00e4tze|reports|Berichte|calls|cases|F\u00e4lle|leads|quotes|Angebote|invoices|Rechnungen|countries|L\u00e4nder|sites|Standorte))",
    "system": r"\b(SAP|S/4\s?HANA|Ariba|Dynamics( 365)?|Salesforce|ServiceNow|Workday|Excel|SharePoint|Teams|Power BI|Fabric|OneLake|Coupa|Oracle|"
              r"data ?lake|ERP|CRM|HCM|MES|PLM|Copilot|Copilot Studio|Foundry|Databricks|Snowflake|Jira|Confluence|Power Automate)\b",
    "goal": r"\b(goal|vision|ambition|target|strateg\w*|objective|priorit\w*|north star|Ziel\w*|Vision|Strategie|Ambition|Priorit\u00e4t\w*)\b",
    "decision": r"\b(we decided|decided|agreed|we will|let'?s go with|go with|sign(ed)? off|approved|beschlossen|entschieden|vereinbart|wir machen|freigegeben)\b",
    "action": r"\b(action item|next step|follow[- ]?up|to-?do|I will send|we will send|share (the|a)|by (monday|tuesday|wednesday|thursday|friday|next week|end of)|"
              r"bis (Montag|Dienstag|Mittwoch|Donnerstag|Freitag|n\u00e4chste Woche|Ende)|n\u00e4chste[rn]? Schritt\w*|Aufgabe)\b",
    "risk": r"\b(risk|compliance|GDPR|FADP|revFADP|DSG|nDSG|data protection|privacy|works council|security|audit|NDA|legal|EU AI Act|residency|"
            r"Risiko|Datenschutz|Betriebsrat|Sicherheit|Revision|Rechtsabteilung|Datenresidenz)\b",
    "idea": r"\b(agent|copilot|automat\w*|AI\b|KI\b|use case|Anwendungsfall|could we|what if|it would be great|w\u00e4re (gut|toll|super)|k\u00f6nnten wir)\b",
    "stakeholder": r"\b(CEO|CFO|CIO|CTO|CPO|COO|CHRO|head of|director|manager|owner|board|Gesch\u00e4ftsleitung|Verwaltungsrat|Leiter\w*|Bereichsleit\w*)\b",
}
SIG_RE = {k: re.compile(v, re.I) for k, v in SIGNALS.items()}
ORDER = ["decision", "action", "metric", "pain", "risk", "goal", "system", "stakeholder", "idea"]


def to_seconds(ts):
    if not ts:
        return None
    parts = ts.replace(",", ".").split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    total = 0.0
    for p in nums:
        total = total * 60 + p
    return total


def fmt(sec):
    if sec is None:
        return None
    sec = int(sec)
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        # Read the paragraph text with a narrow pattern instead of an XML parser:
        # no entity expansion, no DTD processing, nothing executed.
        with zipfile.ZipFile(path) as z:
            info = z.getinfo("word/document.xml")
            if info.file_size > 30 * 1024 * 1024:
                raise ValueError("document.xml is unreasonably large")
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        if "<!DOCTYPE" in xml or "<!ENTITY" in xml:
            raise ValueError("document.xml declares a DTD or entities; refusing to read it")
        paras = re.findall(r"<w:p[ >].*?</w:p>|<w:p/>", xml, re.S)
        return "\n".join(html.unescape("".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", p, re.S))) for p in paras)
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(raw)
        except ValueError:
            return raw
        if isinstance(data, dict):
            for k in ("content", "transcript", "text", "value"):
                if isinstance(data.get(k), str):
                    return data[k]
    return raw


def parse(text: str) -> list[dict]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    turns: list[dict] = []
    is_vtt = bool(lines) and (lines[0].strip().upper().startswith("WEBVTT") or any(CUE.match(l) for l in lines[:40]))
    if is_vtt:
        cur = None
        for line in lines:
            m = CUE.match(line)
            if m:
                cur = {"start": to_seconds(m.group(1)), "end": to_seconds(m.group(2)), "speaker": None, "text": ""}
                turns.append(cur)
                continue
            stripped = line.strip()
            if cur is None or not stripped or stripped.isdigit() or stripped.upper() == "WEBVTT" or "-->" in stripped:
                continue
            vm = VTAG.search(line)
            if vm:
                cur["speaker"] = vm.group(1).strip()
                body = vm.group(2)
            else:
                pm = PREFIX.match(TAGS.sub("", line))
                if pm and not cur["text"]:
                    cur["speaker"] = pm.group(2).strip()
                    body = pm.group(3)
                else:
                    body = line
            cur["text"] = (cur["text"] + " " + TAGS.sub("", body).strip()).strip()
    else:
        head = None
        for line in lines:
            if not line.strip():
                continue
            hm = DOCX_HEAD.match(line)
            if hm:
                head = {"speaker": hm.group(1).strip(), "start": to_seconds(hm.group(2)), "end": None, "text": ""}
                turns.append(head)
                continue
            pm = PREFIX.match(line)
            if pm and len(pm.group(2).split()) <= 6:
                turns.append({"speaker": pm.group(2).strip(), "start": to_seconds(pm.group(1)), "end": None, "text": pm.group(3).strip()})
                head = None
                continue
            if head is not None:
                head["text"] = (head["text"] + " " + line.strip()).strip()
            elif turns:
                turns[-1]["text"] = (turns[-1]["text"] + " " + line.strip()).strip()
            else:
                turns.append({"speaker": None, "start": None, "end": None, "text": line.strip()})
    turns = [t for t in turns if t["text"]]
    merged: list[dict] = []
    for t in turns:
        if merged and t["speaker"] and merged[-1]["speaker"] == t["speaker"] and len(merged[-1]["text"]) < 1200:
            merged[-1]["text"] += " " + t["text"]
            if t.get("end") is not None:
                merged[-1]["end"] = t["end"]
        else:
            merged.append(dict(t))
    for i, t in enumerate(merged):
        t["i"] = i
    return merged


def analyse(turns: list[dict], max_signals: int):
    speakers: dict[str, dict] = {}
    signals: list[dict] = []
    for t in turns:
        sp = t.get("speaker") or "Unknown"
        s = speakers.setdefault(sp, {"turns": 0, "words": 0, "seconds": 0.0})
        s["turns"] += 1
        s["words"] += len(t["text"].split())
        if t.get("start") is not None and t.get("end") is not None and t["end"] >= t["start"]:
            s["seconds"] += t["end"] - t["start"]
        for cat, rx in SIG_RE.items():
            m = rx.search(t["text"])
            if m:
                signals.append({"turn": t["i"], "start": fmt(t.get("start")), "speaker": sp, "category": cat,
                                "match": m.group(0), "text": t["text"][:400]})
    for s in speakers.values():
        s["seconds"] = round(s["seconds"])
    if len(signals) > max_signals:
        signals.sort(key=lambda x: (ORDER.index(x["category"]), x["turn"]))
        signals = sorted(signals[:max_signals], key=lambda x: x["turn"])
    return speakers, signals


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("transcript", help="transcript file (.vtt, .txt, .md, .docx, .json)")
    ap.add_argument("--evidence-id", default=None, help="evidence id to cite, e.g. E05")
    ap.add_argument("--title", default=None, help="meeting title")
    ap.add_argument("--date", default=None, help="meeting date YYYY-MM-DD")
    ap.add_argument("--max-signals", type=int, default=400)
    ap.add_argument("--out", default=None, help="write JSON here instead of stdout")
    a = ap.parse_args(argv)
    path = Path(a.transcript)
    try:
        text = read_text(path)
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as e:
        print(f"ERROR: cannot read {path.name}: {e}", file=sys.stderr)
        return 2
    turns = parse(text)
    if not turns:
        print("ERROR: no speaker turns found; is this a transcript?", file=sys.stderr)
        return 1
    speakers, signals = analyse(turns, a.max_signals)
    counts: dict[str, int] = {}
    for s in signals:
        counts[s["category"]] = counts.get(s["category"], 0) + 1
    last = max(((t.get("end") or t.get("start") or 0) for t in turns), default=0)
    out = {
        "source": a.title or path.name, "date": a.date, "evidence_id": a.evidence_id,
        "turns": [{"i": t["i"], "start": fmt(t.get("start")), "end": fmt(t.get("end")), "speaker": t.get("speaker"), "text": t["text"]} for t in turns],
        "speakers": speakers, "signals": signals,
        "stats": {"turns": len(turns), "speakers": len(speakers), "words": sum(s["words"] for s in speakers.values()),
                  "duration": fmt(last), "signals_by_category": counts},
    }
    js = json.dumps(out, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(js, encoding="utf-8")
        print(json.dumps({"out": a.out, "stats": out["stats"]}, ensure_ascii=False))
    else:
        print(js)
    return 0


if __name__ == "__main__":
    sys.exit(main())
