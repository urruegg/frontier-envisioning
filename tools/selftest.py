#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""End-to-end self-test of the plugin scripts against the bundled examples.

Usage (from the repository root):  python tools/selftest.py   (the plugin lives in plugin/)

Runs, in a temporary folder:
  1. context_pack.py validate + render on the example context pack
  2. parse_transcript.py on a small synthetic WebVTT transcript
  3. seed_blueprint.py from the context pack, then build_blueprint.py on the seed
  4. build_blueprint.py on the Caldova example (internal and customer audiences); the agent workflows
     (authored, derived from the canvas plan, checked for unknown node types and agents)
  5. merge_feedback.py with a synthetic workshop feedback export
  6. scaffold_design_docs.py for the MVP agents (with each MVP agent's workflow)
  7. agent identity: read_office_theme.py on a synthetic deck, seed_identity.py from the Caldova blueprint,
     make_kit.py on the Caldova example (validator 0 errors, kit unit tests pass), apply_identity.py and a
     blueprint build with the Agent identity page; build_with_identity.py (blueprint and identity kit in one
     step, seeded from the blueprint without a brand file)
  7b. business value and FinOps: finops_calc.py and value_calc.py reproduce the method's worked example
     (credits, purchase options, scenarios, NPV, ROI, payback, break-even); the Caldova value case and FinOps
     model built into the blueprint; workshop verdicts merged; seeds that leave volumes to collect
  8. build_package.py, then the Cowork install check on the extracted package (and on an altered copy)
Each script is imported and its main(argv) called; nothing is fetched from the network.
Exit code 0 when every step passes.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "plugin" / "skills"


def load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(mod, argv) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        code = mod.main(argv)
    return code, buf.getvalue()


THEME = """<?xml version="1.0" encoding="UTF-8"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Synthetic Theme"><a:themeElements>
<a:clrScheme name="Synthetic"><a:dk1><a:sysClr val="windowText" lastClr="111111"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
<a:dk2><a:srgbClr val="0B3954"/></a:dk2><a:lt2><a:srgbClr val="E8EEF2"/></a:lt2><a:accent1><a:srgbClr val="0F6CBD"/></a:accent1>
<a:accent2><a:srgbClr val="00827F"/></a:accent2><a:accent3><a:srgbClr val="107C41"/></a:accent3><a:accent4><a:srgbClr val="C0541A"/></a:accent4>
<a:accent5><a:srgbClr val="6B4FA0"/></a:accent5><a:accent6><a:srgbClr val="F2B544"/></a:accent6><a:hlink><a:srgbClr val="0F6CBD"/></a:hlink>
<a:folHlink><a:srgbClr val="6B4FA0"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Synthetic"><a:majorFont><a:latin typeface="Aptos Display"/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/></a:minorFont></a:fontScheme>
</a:themeElements></a:theme>"""
MASTER_RELS = """<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/></Relationships>"""

VTT = """WEBVTT

00:00:01.000 --> 00:00:06.000
<v Head of Service>Our technicians write reports manually in the evening.</v>

00:00:06.500 --> 00:00:12.000
<v Facilitator>Which system holds the work orders?</v>

00:00:12.500 --> 00:00:18.000
<v Head of Service>Dynamics 365 Field Service. We agreed to share 20 reports by Friday.</v>
"""


def main() -> int:
    ok = True
    results = []

    def check(name, cond, detail=""):
        nonlocal ok
        results.append(("PASS" if cond else "FAIL", name, detail))
        ok = ok and cond

    cp = load(S / "frontier-context-discovery/scripts/context_pack.py")
    pt = load(S / "frontier-context-discovery/scripts/parse_transcript.py")
    sb = load(S / "frontier-blueprint/scripts/seed_blueprint.py")
    bb = load(S / "frontier-blueprint/scripts/build_blueprint.py")
    mf = load(S / "frontier-blueprint/scripts/merge_feedback.py")
    sd = load(S / "frontier-solution-design/scripts/scaffold_design_docs.py")
    ctx = S / "frontier-context-discovery/examples/caldova-context.json"
    sample = S / "frontier-blueprint/examples/caldova-blueprint.json"

    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        code, out = run(cp, ["validate", str(ctx)])
        check("context pack validates", code == 0, out[-200:] if code else "")
        code, _ = run(cp, ["render", str(ctx), "--out", str(t / "log.md"), "--audience", "customer"])
        log = (t / "log.md").read_text(encoding="utf-8") if (t / "log.md").exists() else ""
        check("evidence log renders without internal sources", code == 0 and "E02" not in log)

        (t / "t.vtt").write_text(VTT, encoding="utf-8")
        code, _ = run(pt, [str(t / "t.vtt"), "--evidence-id", "E09", "--out", str(t / "t.json")])
        turns = json.loads((t / "t.json").read_text(encoding="utf-8")) if code == 0 else {}
        cats = {s["category"] for s in turns.get("signals", [])}
        check("transcript parses into turns and signals", code == 0 and turns.get("stats", {}).get("turns") == 3 and {"pain", "system", "decision"} <= cats, str(cats))

        code, _ = run(sb, ["--context", str(ctx), "--out", str(t / "seed.json")])
        check("seed blueprint from context", code == 0)
        code, out = run(bb, ["--data", str(t / "seed.json"), "--out", str(t / "seed.html")])
        check("seed blueprint builds", code == 0, out[-300:] if code else "")

        code, out = run(bb, ["--data", str(sample), "--out", str(t / "bp.html"), "--save-normalized", str(t / "bp.json")])
        html = (t / "bp.html").read_text(encoding="utf-8") if code == 0 else ""
        check("example blueprint builds", code == 0 and '"__BLUEPRINT_DATA__"' not in html and "Caldova" in html, out[-300:] if code else "")
        check("no raw '<' inside the embedded data", code == 0 and "</script" not in html.split('id="bp-data">', 1)[1].split("</script>", 1)[0])
        code, out = run(bb, ["--data", str(sample), "--out", str(t / "bp-c.html"), "--audience", "customer"])
        chtml = (t / "bp-c.html").read_text(encoding="utf-8") if code == 0 else ""
        check("customer version strips internal evidence", code == 0 and "Caldova account plan FY27" not in chtml)

        # 1.4: Innovation Hub canon (Agent Factory journey, landing zone, ADRs, IT readiness), product icons, Hub journey views
        def stats_of(text):
            i = text.find('{"status"')
            try:
                return json.loads(text[i:]).get("stats", {}) if i >= 0 else {}
            except ValueError:
                return {}
        seedbp = json.loads((t / "seed.json").read_text(encoding="utf-8")) if (t / "seed.json").exists() else {}
        sfac = [d for d in seedbp.get("domains", []) if d.get("kind") == "factory"]
        sarch, srd = seedbp.get("architecture") or {}, seedbp.get("it_readiness") or {}
        check("seed adds the Hub canon (factory journey, landing zone, ADRs, IT readiness)", len(sfac) == 1 and len(sfac[0].get("agents", [])) == 5
              and all(p_.get("role") for p_ in sfac[0].get("personas", [])) and len((sarch.get("landing_zone") or {}).get("areas", {})) >= 14
              and sum(1 for x in sarch.get("decisions", []) if x.get("canon")) >= 6 and sum(len(g.get("items", [])) for g in srd.get("groups", [])) == 30
              and len(srd.get("checks", [])) == 15 and len(seedbp.get("factory", {}).get("lifecycle", [])) == 7)
        lean = json.loads(sample.read_text(encoding="utf-8"))
        lean["domains"] = [d for d in lean["domains"] if d.get("kind") != "factory"]
        for k in ("factory", "it_readiness", "feedback_loop"):
            lean.pop(k, None)
        lean["architecture"].pop("landing_zone", None)
        lean["architecture"]["decisions"] = [x for x in lean["architecture"].get("decisions", []) if not x.get("canon")]
        (t / "lean.json").write_text(json.dumps(lean), encoding="utf-8")
        code, out = run(bb, ["--data", str(t / "lean.json"), "--out", str(t / "lean.html"), "--canon"])
        st = stats_of(out)
        check("--canon completes an earlier blueprint (factory, landing zone, ADRs, readiness)", code == 0 and st.get("factory_journey") == "D5"
              and st.get("landing_zone_areas", 0) >= 14 and st.get("readiness_items") == 30 and st.get("decisions") == 9
              and st.get("feedback_loop_areas") == 4, out[-300:])
        code, out = run(bb, ["--data", str(sample), "--out", str(t / "icons.html")])
        st1, ihtml = stats_of(out), (t / "icons.html").read_text(encoding="utf-8") if code == 0 else ""
        code2, out2 = run(bb, ["--data", str(sample), "--out", str(t / "noicons.html"), "--no-product-icons"])
        check("Microsoft product icons embedded only when used, with their notice", code == 0 and code2 == 0 and st1.get("product_icons", 0) >= 10
              and '"logo_rules"' in ihtml and '"logos_note"' in ihtml and stats_of(out2).get("product_icons") == 0 and st1.get("attendees") == 8, (out + out2)[-300:])
        tplv = (S / "frontier-blueprint/templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
        check("template has the Hub journey views (attendees, factory, landing zone, ADRs, IT readiness)",
              all(f in tplv for f in ("function renderAttendees", "function renderFactorySections", "function renderLandingZone", "function lzSvg",
                                      "function renderDecisions", "function renderReadiness", 'id:"readiness", label:"IT readiness"', 'id:"attendees", label:"Attendees"')))

        # 1.5: Microsoft's digital feedback loop on the Overview (Microsoft IQ; official names only)
        sfl = {q.get("pillar"): q for q in (seedbp.get("feedback_loop") or {}).get("quadrants", [])}
        jid = {d.get("name"): d.get("id") for d in seedbp.get("domains", [])}
        sig_iq = [i for q in sfl.values() for x in q.get("signals", []) for i in x.get("iq", [])]
        check("seed adds the digital feedback loop with each journey in one area", len(sfl) == 4
              and jid.get("Commercial") in sfl.get("engage_customers", {}).get("journeys", [])
              and jid.get("Service") in sfl.get("optimize_operations", {}).get("journeys", [])
              and bool(sig_iq) and set(sig_iq) <= {"work", "fabric", "foundry", "web"})
        bpn = json.loads((t / "bp.json").read_text(encoding="utf-8")) if (t / "bp.json").exists() else {}
        odd = json.loads(sample.read_text(encoding="utf-8"))
        odd["feedback_loop"]["quadrants"][0]["signals"].append({"text": "Governance IQ checks every case", "iq": ["governance"]})
        (t / "odd.json").write_text(json.dumps(odd), encoding="utf-8")
        code, out = run(bb, ["--data", str(t / "odd.json")])
        check("digital feedback loop builds with official Microsoft IQ names only", len((bpn.get("feedback_loop") or {}).get("quadrants", [])) == 4
              and all(f in tplv for f in ("function flSvg", "animateMotion", "pauseAnimations", "prefers-reduced-motion"))
              and code == 0 and "'Governance IQ', which is not an official Microsoft IQ name" in out and "unknown Microsoft IQ layer governance" in out, out[-300:])

        # 1.6: agent workflows as Copilot Studio workflows (trigger, designer nodes, branches, desired outcome)
        wfs = {a.get("id"): a["canvas"]["workflow"] for d in bpn.get("domains", []) for a in d.get("agents", [])
               if isinstance(a.get("canvas"), dict) and isinstance(a["canvas"].get("workflow"), dict)}
        odd2 = json.loads(sample.read_text(encoding="utf-8"))
        for d in odd2["domains"]:
            for a_ in d.get("agents", []):
                if a_.get("id") == "D2-A01":
                    a_["canvas"].pop("workflow", None)
                if a_.get("id") == "D3-A05":
                    a_["canvas"]["workflow"]["steps"].append({"type": "magic", "label": "Do magic", "agent": "D9-A99"})
        (t / "wf.json").write_text(json.dumps(odd2), encoding="utf-8")
        code, out = run(bb, ["--data", str(t / "wf.json"), "--out", str(t / "wf.html"), "--save-normalized", str(t / "wf-n.json")])
        wn = json.loads((t / "wf-n.json").read_text(encoding="utf-8")) if code == 0 else {}
        dwf = next(((a_.get("canvas") or {}).get("workflow") or {} for d in wn.get("domains", []) for a_ in d.get("agents", []) if a_.get("id") == "D2-A01"), {})
        check("agent workflows build; a missing one is derived from the plan; unknown nodes and agents warn",
              set(wfs) == {"D2-A01", "D3-A05"} and st1.get("workflows") == 2 and wfs["D3-A05"]["trigger"]["type"] == "connector"
              and all(x.get("id") for x in wfs["D3-A05"]["steps"]) and code == 0 and dwf.get("derived") is True
              and dwf.get("trigger", {}).get("type") == "agent" and any(x.get("type") == "classify" for x in dwf.get("steps", []))
              and "node type 'magic' unknown" in out and "unknown agent 'D9-A99'" in out
              and all(f in tplv for f in ("function wfLayout", "function wfSvg", "function wfSection", "function wfPanel")), out[-300:])

        fb = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "version": "0.1",
              "exported": "2026-11-12T16:00:00Z",
              "validations": {"agent:D3-A05": {"status": "validated", "note": "Confirmed; start in region West"},
                              "uc:UC05": {"status": "adjusted", "note": "Pilot in plant B"}},
              "discovery": {"D3-Q02": {"status": "answered", "note": "12 mandatory fields; list shared"}}}
        (t / "fb.json").write_text(json.dumps(fb), encoding="utf-8")
        code, out = run(mf, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb.json"), "--out", str(t / "bp2.json")])
        merged = json.loads((t / "bp2.json").read_text(encoding="utf-8")) if code == 0 else {}
        a = next((x for d in merged.get("domains", []) for x in d.get("agents", []) if x.get("id") == "D3-A05"), {})
        check("feedback merges (status, notes, version bump)", code == 0 and a.get("status") == "validated" and merged["meta"]["version"] == "0.2", out[-300:] if code else "")
        fb2 = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "exported": "2026-11-12T16:00:00Z",
               "validations": {"ready:P-01": {"status": "done", "note": "Pay-as-you-go plan linked"}, "adr:ADR-F01": {"status": "validated", "note": "Agreed with IT"},
                               "adr:ADR-X99": {"status": "validated"}}}
        (t / "fb2.json").write_text(json.dumps(fb2), encoding="utf-8")
        code, out = run(mf, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb2.json"), "--out", str(t / "bp3.json")])
        m3 = json.loads((t / "bp3.json").read_text(encoding="utf-8")) if code == 0 else {}
        p01 = next((x for g in (m3.get("it_readiness") or {}).get("groups", []) for x in g.get("items", []) if x.get("id") == "P-01"), {})
        f01 = next((x for x in (m3.get("architecture") or {}).get("decisions", []) if x.get("id") == "ADR-F01"), {})
        check("workshop verdicts update IT readiness and architecture decisions", code == 0 and p01.get("status") == "done" and f01.get("status") == "agreed"
              and bool(f01.get("workshop_notes")) and '"adr:ADR-X99"' in out, out[-300:])

        fb3 = {"type": "frontier-blueprint-feedback", "blueprint": "caldova-industrial-frontier", "exported": "2026-11-12T16:00:00Z",
               "validations": {"loop:transform_products": {"status": "adjusted", "note": "Telemetry only for the new machine series"}}}
        (t / "fb3.json").write_text(json.dumps(fb3), encoding="utf-8")
        code, out = run(mf, ["--blueprint", str(t / "bp.json"), "--feedback", str(t / "fb3.json"), "--out", str(t / "bp4.json")])
        m4 = json.loads((t / "bp4.json").read_text(encoding="utf-8")) if code == 0 else {}
        tq = next((q for q in (m4.get("feedback_loop") or {}).get("quadrants", []) if q.get("pillar") == "transform_products"), {})
        check("workshop verdicts update the digital feedback loop", code == 0 and tq.get("status") == "adjusted" and bool(tq.get("workshop_notes")), out[-300:])

        code, out = run(sd, ["--blueprint", str(t / "bp2.json"), "--out-dir", str(t / "design")])
        prd = (t / "design/prd.md").read_text(encoding="utf-8") if code == 0 else ""
        sdoc = (t / "design/solution-design.md").read_text(encoding="utf-8") if code == 0 else ""
        rdoc = (t / "design/it-readiness.md").read_text(encoding="utf-8") if (t / "design/it-readiness.md").exists() else ""
        check("PRD and solution design scaffold", code == 0 and "FR-0001" in prd and sdoc and any((t / "design/adr").iterdir()))
        check("solution design carries the landing zone, the Agent Factory and the IT readiness checklist", "### 3.1 Landing zone" in sdoc
              and "### 8.2 Definition of Ready" in sdoc and "Innovation Hub canon" in sdoc and "P-30" in rdoc and "R-15" in rdoc and "D-08" in rdoc)
        check("solution design lists each MVP workflow (trigger, nodes, branches)", "### Workflow: Service report from voice notes (Service Report Agent)" in sdoc
              and "| 3.1 | Connector | Transcribe the voice note |" in sdoc and "- Trigger: When an agent calls the workflow" in sdoc)

        # agent identity kit
        ai = S / "frontier-agent-identity"
        rot = load(ai / "scripts/read_office_theme.py")
        with zipfile.ZipFile(t / "deck.pptx", "w") as z:
            z.writestr("ppt/slideMasters/slideMaster1.xml", "<p:sldMaster xmlns:p='p'/>")
            z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", MASTER_RELS)
            z.writestr("ppt/theme/theme1.xml", THEME)
        code, out = run(rot, [str(t / "deck.pptx"), "--out", str(t / "brand.json"), "--customer", "Caldova Industrial AG", "--short", "Caldova", "--evidence-id", "E10"])
        brand = json.loads((t / "brand.json").read_text(encoding="utf-8")) if code == 0 else {}
        th = brand.get("theme", {})
        check("Office theme read into a brand file", code == 0 and th.get("accent1") == "#0F6CBD" and th.get("dk1") == "#111111"
              and th.get("fonts", {}).get("body") == "Aptos", out[-300:] if code else "")
        si = load(ai / "scripts/seed_identity.py")
        code, out = run(si, ["--blueprint", str(sample), "--brand", str(ai / "examples/caldova-brand.json"), "--prefix", "cal",
                             "--out-dir", str(t / "idseed"), "--date", "2026-10-30"])
        seeded = json.loads((t / "idseed/agent-identity.json").read_text(encoding="utf-8")) if code == 0 else {"agents": []}
        names_ok = all(len(f"{x['po']} {x['domain']}") <= 25 for x in seeded["agents"])
        fac_ok = all(x["kind"] == "repository-agent" for x in seeded["agents"] if x["po"] == "Factory")
        check("identity seeded from the blueprint (33 agents incl. the factory, names fit)", code == 0 and len(seeded["agents"]) == 33 and names_ok and fac_ok
              and (t / "idseed/seed-report.md").exists(), out[-300:] if code else "")
        mk = load(ai / "scripts/make_kit.py")
        code, out = run(mk, ["--config", str(ai / "examples/caldova-agent-identity.json"), "--palette", str(ai / "examples/caldova-palette.json"),
                             "--out", str(t / "kit/caldova-agent-identity"), "--no-png", "--zip", "Caldova - agent identity package v1.0"])
        summary = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        kit = t / "kit/caldova-agent-identity"
        icon_ok = (kit / "agents/service-report/identity/color-192-dev.png").exists() and (kit / "agents/service-report/identity/outline-32.png").exists()
        check("identity kit builds, validates and passes its unit tests", code == 0 and not summary.get("validation", {}).get("errors")
              and summary.get("tests") == "passed" and icon_ok and (t / "kit/Caldova - agent identity package v1.0.zip").exists(), out[-400:])
        ap_ = load(ai / "scripts/apply_identity.py")
        code, out = run(ap_, ["--blueprint", str(sample), "--kit", str(kit), "--out", str(t / "bp-id.json"), "--colours"])
        code2, out2 = run(bb, ["--data", str(t / "bp-id.json"), "--out", str(t / "bp-id.html")]) if code == 0 else (1, out)
        idhtml = (t / "bp-id.html").read_text(encoding="utf-8") if code2 == 0 else ""
        bpid = json.loads((t / "bp-id.json").read_text(encoding="utf-8")) if code == 0 else {}
        blk = bpid.get("identity") or {}
        mvp = next((a for d in bpid.get("domains", []) for a in d.get("agents", []) if a.get("id") == "D3-A05"), {}).get("identity") or {}
        page_ok = (len(blk.get("environments", [])) == 3 and len(blk.get("journeys", [])) == 5 and len(blk.get("rules", [])) >= 6
                   and blk.get("validation") == {"errors": 0, "warnings": 0} and set(mvp.get("icons", {})) == {"DEV", "TEST"}
                   and mvp.get("schema") == "cal_ServiceReport" and mvp.get("outline", "").startswith("data:image/svg+xml;base64,"))
        tpl = (S / "frontier-blueprint/templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
        check("blueprint shows the Agent identity page", code2 == 0 and page_ok and idhtml.count("data:image/svg+xml;base64,") >= 33 * 3
              and 'id:"identity", label:"Agent identity"' in tpl and "function renderIdentity" in tpl, (out + out2)[-300:])
        bwi = load(S / "frontier-blueprint/scripts/build_with_identity.py")
        code, out = run(bwi, ["--data", str(sample), "--out-dir", str(t / "onestep"), "--no-png"])
        one = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        oi = one.get("identity") or {}
        one_html = Path(one.get("html", t / "missing.html"))
        # business value and FinOps
        fdir, vdir = S / "frontier-finops", S / "frontier-value-case"
        check("shared formula module identical in both skills", (fdir / "scripts/fv_expr.py").read_bytes() == (vdir / "scripts/fv_expr.py").read_bytes())
        sys.path[:0] = [str(fdir / "scripts"), str(vdir / "scripts")]
        fc, vc = load(fdir / "scripts/finops_calc.py"), load(vdir / "scripts/value_calc.py")
        rates = json.loads((fdir / "rates/rates-2026-11.json").read_text(encoding="utf-8"))
        rv = json.loads((vdir / "examples/reference-hr-assistant.value.json").read_text(encoding="utf-8"))
        rf = json.loads((fdir / "examples/reference-hr-assistant.finops.json").read_text(encoding="utf-8"))
        rf["results"] = fc.run(rf, rv, rates)
        ag = rf["results"]["agents"][0]
        po = {o["option"]: o for o in rf["results"]["purchase_options"]}
        sc = [round(x["credits_month"]) for x in rf["results"]["credit_scenarios"]]
        uc = vc.run(rv, rf)["use_cases"][0]
        near = lambda a, b, tol: a is not None and abs(a - b) <= tol
        golden = (round(ag["credits_month"]) == 81780 and near(ag["lines"]["credits"], 662.42, 0.01) and near(ag["total_month"], 2582.42, 0.01)
                  and near(po["packs"]["annual_chf"], 7776.0, 0.01) and near(po["cc-p3"]["annual_chf"], 7827.52, 0.01) and sc == [136300, 27260, 18780, 163560]
                  and near(ag["unit"]["per_session"], 0.26, 0.005) and near(ag["unit"]["per_outcome"], 1.03, 0.005) and near(uc["npv"], 540413, 1.0)
                  and near(uc["roi"], 5.20, 0.005) and near(uc["payback_months"], 1.3, 0.05) and near((uc["break_even"] or {}).get("value"), 0.031, 0.0005))
        check("value and FinOps reproduce the method's worked example", golden,
              json.dumps({"credits": ag["credits_month"], "npv": uc["npv"], "roi": uc["roi"], "payback": uc["payback_months"], "scenarios": sc})[:300])
        bwi_vf = load(S / "frontier-blueprint/scripts/build_with_identity.py")
        code, out = run(bwi_vf, ["--data", str(sample), "--value", str(vdir / "examples/caldova-value.json"), "--finops", str(fdir / "examples/caldova-finops.json"),
                                 "--out-dir", str(t / "vfdemo"), "--no-identity"])
        vf = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        vf_html = Path(vf.get("html", t / "missing.html"))
        vf_text = vf_html.read_text(encoding="utf-8") if vf_html.exists() else ""
        tpl = (S / "frontier-blueprint/templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
        check("value case and FinOps model in the blueprint (Caldova demo)", code == 0 and not vf.get("notes") and (vf.get("finops") or {}).get("agents") == 2
              and not (vf.get("value") or {}).get("inputs_needed") and '"finops":{' in vf_text and '"value_case":{' in vf_text and '"business_value":{' in vf_text
              and "function renderFinops" in tpl and 'id:"finops", label:"FinOps"' in tpl, out[-400:])
        mv = load(vdir / "scripts/merge_value_feedback.py")
        (t / "merge").mkdir()
        shutil.copyfile(vdir / "examples/caldova-value.json", t / "merge/value.json")
        shutil.copyfile(fdir / "examples/caldova-finops.json", t / "merge/finops.json")
        (t / "merge/fb.json").write_text(json.dumps({"type": "frontier-blueprint-feedback", "exported": "2026-11-12T16:40:00Z", "validations": {
            "ass:ASS-003": {"status": "adjusted", "value": 12, "note": "Head of Service"}, "ass:ASS-101": {"status": "validated"}, "ass:ASS-999": {"status": "validated"},
            "uc:UC09": {"status": "validated"}}}), encoding="utf-8")
        code, out = run(mv, ["--value", str(t / "merge/value.json"), "--finops", str(t / "merge/finops.json"), "--feedback", str(t / "merge/fb.json")])
        mres = json.loads(out[out.index("{"):]) if code == 0 and "{" in out else {}
        mval = json.loads((t / "merge/value.json").read_text(encoding="utf-8"))
        mfin = json.loads((t / "merge/finops.json").read_text(encoding="utf-8"))
        a3 = next(a for a in mval["assumptions"] if a["id"] == "ASS-003")
        a101 = next(a for a in mfin["assumptions"] if a["id"] == "ASS-101")
        check("workshop verdicts merge into the value case and the FinOps model", code == 0 and mres.get("changed") == 2 and mres.get("unknown") == ["ASS-999"]
              and a3["base"] == 12 and a3["status"] == "adjusted" and a101["status"] == "confirmed" and mval["version"] == "0.2" and mfin["version"] == "0.2", out[-300:])
        sv, sf = load(vdir / "scripts/seed_value.py"), load(fdir / "scripts/seed_finops.py")
        c1, o1 = run(sv, ["--blueprint", str(sample), "--out", str(t / "seed-value.json")])
        c2, o2 = run(sf, ["--blueprint", str(sample), "--value", str(t / "seed-value.json"), "--out", str(t / "seed-finops.json")])
        seeded_v = json.loads((t / "seed-value.json").read_text(encoding="utf-8")) if c1 == 0 else {}
        seeded_f = json.loads((t / "seed-finops.json").read_text(encoding="utf-8")) if c2 == 0 else {}
        sres = vc.run(seeded_v, seeded_f) if c1 == 0 and c2 == 0 else {}
        cov = {a["id"]: a["usage"]["billable_share"] for a in seeded_f.get("agents", [])}
        check("value and FinOps seeds leave volumes to collect", c1 == 0 and c2 == 0 and len(sres.get("inputs_needed", [])) == 2 and not sres.get("use_cases")
              and cov.get("D2-A01") == "1 - licensed_share" and cov.get("D3-A05") == 1, (o1 + o2)[-300:])
        check("blueprint and identity kit built in one step", code == 0 and oi.get("matched") == 33 and oi.get("tests") == "passed"
              and not (oi.get("validation") or {}).get("errors") and oi.get("seeded") is True and one_html.exists()
              and '"identity":{"kit":' in one_html.read_text(encoding="utf-8") and (one.get("blueprint") or {}).get("status") == "ok", out[-400:])

        # install simulation: build the package, extract it like Cowork does, check it, then tamper with it
        bp_ = load(ROOT / "tools/build_package.py")
        code, out = run(bp_, ["--dist", str(t / "dist")])
        pkgs = sorted((t / "dist").glob("frontier-envisioning-plugin-*.zip")) if code == 0 else []
        check("package builds", code == 0 and len(pkgs) == 1, out[-300:] if code else "")
        if pkgs:
            with zipfile.ZipFile(pkgs[0]) as z:
                z.extractall(t / "pkg")
            inst = load(t / "pkg/install/prepare_install.py")
            (t / "empty").mkdir()
            code, out = run(inst, ["--root", str(t / "pkg"), "--installed", str(t / "empty")])
            plan = json.loads(out) if code == 0 else {}
            check("install check passes on the released package", code == 0 and plan.get("verified") and len(plan.get("copy_calls", [])) == 7
                  and all(x["status"] == "new" for x in plan.get("skills", [])), out[-300:] if code else "")
            with open(t / "pkg/skills/frontier-blueprint/SKILL.md", "a", encoding="utf-8") as fh:
                fh.write("\n<!-- altered -->\n")
            code, out = run(inst, ["--root", str(t / "pkg"), "--installed", str(t / "empty")])
            check("install check refuses an altered package", code == 1 and '"verified": false' in out)

    for status, name, detail in results:
        print(f"{status}  {name}" + (f"  ({detail})" if detail and status == "FAIL" else ""))
    print("ALL PASSED" if ok else "FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
