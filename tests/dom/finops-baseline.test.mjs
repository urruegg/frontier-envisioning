import { it } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { openBlueprint, BASELINE_HTML, acknowledgePreview, txt, wait } from "./helpers.mjs";

const record = (data) => data.agent_finops.records[0];
const summary = (bp, id = "D3-A05") => bp.view().querySelector(`.financial-summary[data-agent="${id}"]`);
const button = (bp, name) => [...bp.view().querySelectorAll("button")].find((b) => txt(b) === name);
function downloadsFor(bp) {
  const blobs = [];
  bp.window.URL.createObjectURL = (blob) => { blobs.push(blob); return "blob:test"; };
  bp.window.URL.revokeObjectURL = () => {};
  // happy-dom does not implement blob navigation; capture the actual Blob bytes
  // as adjacent tests do. Chromium below verifies the real download operation.
  bp.doc.addEventListener("click", (e) => { if (e.target.closest("a[download]")) e.preventDefault(); });
  return blobs;
}

const unpricedReports = new Map();
function unpricedReport(all = false) {
  if (!unpricedReports.has(all)) {
    // Real pure producer DTO, not guessed totals. Modify a test-only in-memory
    // copy of the authoritative example; never write the example or a review.
    const script = String.raw`
import json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, "plugin/skills/frontier-finops/scripts")
from baseline_calc import calculate
from baseline_projection import project
model = json.loads(Path("plugin/skills/frontier-finops/examples/caldova-agent-baseline.json").read_text(encoding="utf-8"))
for rate in (model["rates"] if sys.argv[1] == "all" else model["rates"][:1]):
    rate["amount"] = None
day = date.fromisoformat(model["baseline"]["as_of"])
calculated = calculate(model, as_of=day, acknowledge_finops_preview=True)
print(json.dumps(project(calculated, as_of=day, audience="internal", acknowledge_finops_preview=True)))
`;
    const python = process.platform === "win32" ? "python" : "python3";
    unpricedReports.set(all, JSON.parse(execFileSync(python, ["-B", "-c", script, all ? "all" : "one"],
      { cwd: process.cwd(), encoding: "utf8", timeout: 30_000 })));
  }
  return structuredClone(unpricedReports.get(all));
}

let projectedFxReport;
function fxReport() {
  if (!projectedFxReport) {
    // Actual producer shape, including consumed FX and a distinct FX source.
    // This calculated synthetic derivative is only made planning-shaped by the
    // explicit in-memory fixture below; it is never real approval evidence.
    const script = String.raw`
import copy, json, sys
from datetime import date
from pathlib import Path
sys.path.insert(0, "plugin/skills/frontier-finops/scripts")
from baseline_calc import calculate
from baseline_projection import project
model = json.loads(Path("plugin/skills/frontier-finops/examples/caldova-agent-baseline.json").read_text(encoding="utf-8"))
source = copy.deepcopy(model["sources"][0])
source["id"] = "SYN-FX"
model["sources"].append(source)
model["rates"][0]["currency"] = "USD"
model["fx"] = [{"id": "FX-TEST", "version": 1, "from_currency": "USD", "to_currency": "CHF",
    "rate": "0.9", "date": "2026-11-12", "method": "spot", "source_id": "SYN-FX",
    "src": ["SYN-FX"], "content_src": ["SYN-FX"],
    "verification": {"status": "synthetic", "verified_at": "2026-11-12"},
    "freshness_policy": {"max_age_days": 30}, "sharingClassification": "customer-shareable"}]
day = date.fromisoformat(model["baseline"]["as_of"])
calculated = calculate(model, as_of=day, acknowledge_finops_preview=True)
print(json.dumps(project(calculated, as_of=day, audience="internal", acknowledge_finops_preview=True)))
`;
    const python = process.platform === "win32" ? "python" : "python3";
    projectedFxReport = JSON.parse(execFileSync(python, ["-B", "-c", script],
      { cwd: process.cwd(), encoding: "utf8", timeout: 30_000 }));
  }
  return structuredClone(projectedFxReport);
}

const reviewedScopes = new Map();
function reviewedScopeReports(kind) {
  if (!reviewedScopes.has(kind)) {
    // Real calculate -> freeze -> record-review -> apply control. All source
    // verification/owner assertions are simulated test inputs, not commercial
    // evidence. Authoritative files exist only in this owned TemporaryDirectory.
    const script = String.raw`
import copy, json, sys, tempfile
from datetime import date
from pathlib import Path
root = Path.cwd()
with tempfile.TemporaryDirectory(prefix="task6-reviewed-scope-") as folder:
    out = Path(folder)
    scripts = root / "plugin/skills/frontier-finops/scripts"
    sys.path.insert(0, str(scripts))
    from baseline_calc import calculate
    from baseline_records import freeze, record_review
    from agent_finops import apply_models
    model = json.loads((root / "plugin/skills/frontier-finops/examples/caldova-agent-baseline.json").read_text(encoding="utf-8"))
    kind = sys.argv[1]
    if kind != "provisional":
        model["mode"] = "planning"
        for source in model["sources"]:
            source.update(type="customer-evidence", validationStatus="validated")
        for rate in model["rates"]:
            rate["verification"]["status"] = "verified"
    if kind == "recurring-only":
        model["baseline"]["lines"] = [line for line in model["baseline"]["lines"] if line["frequency"] != "one-time"]
        model["baseline"]["scope"] = [driver for driver in model["baseline"]["scope"] if driver["cost_driver_id"] != "build"]
        model["baseline"]["exclusions"].append(dict(id="EXC-BUILD", cost_driver_id="build",
            description="TEST-ONLY reviewed recurring-only scope excludes one-time build costs.",
            reason="Build funding is explicitly outside this frozen target; no zero build cost is asserted.",
            source_id="SYN-ENGINEERING", sharingClassification="customer-shareable"))
    elif kind == "unpriced-one-time":
        next(rate for rate in model["rates"] if rate["id"] == "RATE-BUILD")["amount"] = None
    elif kind == "private-one-time":
        next(line for line in model["baseline"]["lines"] if line["frequency"] == "one-time")["sharingClassification"] = "internal-only"
    elif kind == "empty-scope":
        model["baseline"]["scope"] = []
        model["baseline"]["lines"] = []
    elif kind == "private-outcome":
        model["profile"]["outcome"]["sharingClassification"] = "internal-only"
    elif kind == "private-unused":
        source = copy.deepcopy(model["sources"][0])
        source.update(id="PRIVATE-UNUSED-SOURCE", sharingClassification="internal-only")
        model["sources"].append(source)
        rate = copy.deepcopy(model["rates"][0])
        rate.update(id="PRIVATE-UNUSED-RATE", source_id="PRIVATE-UNUSED-SOURCE", sharingClassification="internal-only")
        model["rates"].append(rate)
    elif kind == "full-cost-fx":
        source = copy.deepcopy(model["sources"][0])
        source["id"] = "SYN-FX"
        model["sources"].append(source)
        model["rates"][0]["currency"] = "USD"
        model["fx"] = [dict(id="FX-TEST", version=1, from_currency="USD", to_currency="CHF",
            rate="0.9", date="2026-11-12", method="spot", source_id="SYN-FX",
            src=["SYN-FX"], content_src=["SYN-FX"],
            verification=dict(status="verified", verified_at="2026-11-12"),
            freshness_policy=dict(max_age_days=30), sharingClassification="customer-shareable")]
    bp = json.loads((root / "plugin/skills/frontier-blueprint/examples/caldova-blueprint.json").read_text(encoding="utf-8"))
    bp.update(customer_scope="caldova-scope", sharingClassification="customer-shareable")
    for source in bp["evidence"]:
        source.update(internal=False, visibility="customer", sharingClassification="customer-specific", customer_scope="caldova-scope")
    ack = dict(as_of=date(2026, 11, 12), acknowledge_finops_preview=True)
    calculated = calculate(model, **ack)
    snapshot = json.loads(freeze(calculated, out / "frozen", **ack).read_text(encoding="utf-8"))
    review = dict(id="TEST-ONLY-SCOPE-REVIEW", decision="approve",
        actor=model["profile"]["owners"]["finance"], finance_owner=model["profile"]["owners"]["finance"],
        date="2026-11-12", evidence_ref="test:external-assertion-only", **snapshot["target"],
        mode=model["mode"], sharingClassification="customer-shareable")
    recorded = json.loads(record_review(snapshot, review, out / "reviews", **ack).read_text(encoding="utf-8"))
    reports = {audience: apply_models(bp, [snapshot], [recorded], **ack, audience=audience,
        customer_scope="caldova-scope")["agent_finops"] for audience in ("internal", "customer")}
    print(json.dumps(reports))
`;
    const python = process.platform === "win32" ? "python" : "python3";
    reviewedScopes.set(kind, JSON.parse(execFileSync(python, ["-B", "-c", script, kind],
      { cwd: process.cwd(), encoding: "utf8", timeout: 60_000 })));
  }
  return structuredClone(reviewedScopes.get(kind));
}

// Real producer-calculated/frozen/reviewed/projected fixture, with simulated
// test-only verification and owner assertions. Never real approval or a changed
// shipped example. Newly required derived metrics come from the producer too.
function planningEvidence(data) {
  const hasFx = Array.isArray(record(data).evidence.fx) && record(data).evidence.fx.length > 0;
  data.agent_finops = reviewedScopeReports(hasFx ? "full-cost-fx" : "full-cost").internal;
}

it("Task6 real successor adds only the eighteenth route, gates figures/exports and leaves ordinary value usable", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { storage: { finopsAcknowledged: "true" } });
  try {
    assert.equal(bp.doc.querySelectorAll("#rail button").length, 18);
    await bp.go("#/finops");
    assert.ok(bp.view().querySelector("#finops-preview-ack"));
    assert.equal(bp.view().querySelectorAll(".baseline-scenario, .baseline-export").length, 0);
    assert.doesNotMatch(txt(bp.view()), /1320\.00|1\.100000|1000|synthetic:task1/);
    await bp.go("#/usecases");
    assert.match(txt(bp.view()), /CHF 8.21M/);
    await bp.go("#/prd");
    const blobs = downloadsFor(bp);
    button(bp, "Download the PRD (Markdown)").click();
    await wait(20);
    assert.match(await blobs[0].text(), /NPV CHF 7.22M/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 acknowledged real DTO shows exact three twelve-month scenarios, units, evidence and draft limits", async () => {
  const bp = await openBlueprint(BASELINE_HTML);
  try {
    await bp.go("#/finops");
    await acknowledgePreview(bp);
    assert.equal(bp.view().querySelectorAll(".baseline-scenario").length, 3);
    assert.equal(bp.view().querySelectorAll(".baseline-months tbody tr").length, 36);
    const expected = bp.view().querySelector('.baseline-scenario[data-scenario="expected"]');
    assert.match(txt(expected), /CHF 1320\.00/);
    assert.match(txt(expected), /CHF 1520\.00/);
    assert.match(txt(expected), /CHF 1\.100000/);
    assert.match(txt(expected), /provisional.*pricing-evidence-incomplete/);
    assert.match(txt(expected), /Verified contributions.*Unavailable.*Provisional contributions.*CHF 1320\.00/);
    for (const term of ["Profile and discovery", "Projected evidence", "Validation and external review",
      "2026-11-12", "synthetic", "new draft", "not authenticated", "HALF_UP"]) assert.ok(txt(bp.view()).includes(term), term);
    assert.equal(bp.view().querySelectorAll(".baseline-export").length, 2);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 projected rate evidence retains meter, units, applicability dates and verification, not only its amount", async () => {
  const bp = await openBlueprint(BASELINE_HTML);
  try {
    await bp.go("#/finops"); await acknowledgePreview(bp);
    const evidence = [...bp.view().querySelectorAll(".baseline-details")].find((d) => txt(d.querySelector("summary")) === "Inspect projected sources, rates and FX");
    for (const token of ["RATE-TOKENS", "invented-tokens", "pricing_block", "effective_from", "effective_to", "verified_at", "synthetic-model"]) assert.ok(txt(evidence).includes(token), token);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 opaque source annotations named amount are not interpreted as financial metric objects", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    record(data).evidence.sources[0].original_context = { amount: "not a price", explanation: "Source annotation, not a financial scalar" };
  } });
  try {
    await bp.go("#/finops"); await acknowledgePreview(bp);
    assert.equal(bp.view().querySelectorAll(".baseline-scenario").length, 3);
    assert.match(txt(bp.view()), /not a price.*Source annotation, not a financial scalar/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 missing baseline is an actionable financial gap without preventing core workshops", async () => {
  const bp = await openBlueprint();
  try {
    await bp.go("#/agents/D3-A05");
    assert.match(txt(summary(bp)), /Financial handover gap.*authoritative.*freeze.*external.*review/i);
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    await bp.go("#/plan");
    assert.equal(bp.view().querySelectorAll(".kcard").length, 29);
    assert.match(txt(bp.view()), /financial.*planning evidence/i);
    assert.equal(bp.view().querySelectorAll(".dor li").length, 8);
    assert.equal(bp.doc.querySelectorAll('#rail button[data-view="finops"]').length, 0);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 raw approved status and local agent/cost/model verdicts never approve synthetic/provisional evidence", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    const r = record(data);
    r.status = "approved";
    r.handover.lifecycle = "approved";
    data.domains.flatMap((d) => d.agents).find((a) => a.id === r.agent_id).status = "approved";
  } });
  try {
    await bp.go("#/finops");
    await acknowledgePreview(bp);
    const proposal = bp.view().querySelector("#v-finops-baseline-D3_A05-note");
    assert.ok(proposal);
    proposal.value = "Approved CHF 999.123 <img src=x onerror=alert(1)> café ✓";
    proposal.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    assert.match(bp.notes()["val|finops|baseline-D3-A05"].note, /999\.123/);
    assert.equal(bp.view().querySelector('img[src="x"]'), null);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.match(txt(summary(bp)), /synthetic|provisional|blocked/i);
    await bp.go("#/plan");
    const card = [...bp.view().querySelectorAll(".kcard")].find((c) => txt(c).includes("Service Report"));
    assert.match(txt(card), /Financial handover gap/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 generic feedback and text exports withhold saved financial proposals until fresh acknowledgement", async () => {
  const bp = await openBlueprint(BASELINE_HTML);
  let reload;
  try {
    await bp.go("#/finops"); await acknowledgePreview(bp);
    const field = bp.view().querySelector("#v-finops-baseline-D3_A05-note");
    assert.ok(field);
    field.value = "Proposed CHF 999.123, new draft only";
    field.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    reload = await openBlueprint(BASELINE_HTML, { storage: { ...bp.window.localStorage } });
    await reload.go("#/discovery");
    let copied = "";
    reload.window.navigator.clipboard.writeText = async (text) => { copied = text; };
    const blobs = downloadsFor(reload);
    button(reload, "Export workshop feedback (JSON)").click();
    assert.doesNotMatch(await blobs[0].text(), /999\.123/);
    assert.match(JSON.parse(await blobs[0].text()).validations["finops:baseline-D3-A05"].note, /withheld/);
    button(reload, "Copy notes as text").click(); await wait(20);
    assert.doesNotMatch(copied, /999\.123/);
    assert.match(copied, /withheld/i);
    await reload.go("#/finops");
    assert.ok(reload.view().querySelector("#finops-preview-ack"));
    assert.equal(reload.view().querySelectorAll("textarea, .baseline-export").length, 0);
    await acknowledgePreview(reload);
    assert.equal(reload.view().querySelector("#v-finops-baseline-D3_A05-note").value, field.value);
    await reload.go("#/discovery");
    button(reload, "Copy notes as text").click(); await wait(20);
    assert.match(copied, /999\.123/);
    assert.match(copied, /new draft.*not.*approval/i);
    assert.deepEqual(reload.errors, []);
  } finally { if (reload) await reload.close(); await bp.close(); }
});

for (const [label, change] of [
  ["unsupported", (d) => { d.agent_finops.schema = "frontier-agent-finops-view/9.0"; }],
  ["malformed", (d) => { record(d).scenarios.expected.annual_recurring.amount = 1320; }],
  ["duplicate", (d) => { d.agent_finops.records.push(structuredClone(record(d))); }],
  ["conflicting legacy", (d) => { d.finops = { totals: { total_month: 999777 } }; }]
]) it(`Task6 ${label} successor data is visibly incomplete, never a legacy/cached fallback`, async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change });
  try {
    await bp.go("#/finops");
    assert.match(txt(bp.view().querySelector(".baseline-error")), /incomplete.*rebuild/i);
    await acknowledgePreview(bp);
    assert.equal(bp.view().querySelectorAll(".baseline-export, .baseline-scenario").length, 0);
    assert.doesNotMatch(txt(bp.view()), /999777|999,777|1320\.00/);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

for (const [label, change] of [
  ["empty", (d) => { d.agent_finops.records = []; }],
  ["withheld", (d) => { Object.assign(record(d), {
    mode: "withheld", status: "withheld", agent_id: null, baseline: null, currency: null,
    profile: { status: "withheld" }, context: { status: "withheld" }, scenarios: {}, scenario_inputs: [],
    evidence: { status: "withheld" }, formulas: { status: "withheld" },
    gaps: [{ code: "withheld-context", blocks: ["handover"] }],
    handover: { status: "withheld", ready: false, financial_permission: false }
  }); }],
  ["unpriced", (d) => { const r = record(d);
    r.scenarios.expected.annual_recurring = { amount: null, currency: "CHF", status: "unavailable", reason: "unpriced-driver" };
    r.handover.pricing_completeness = "incomplete";
  }]
]) it(`Task6 ${label} records remain gaps, not zero or financial readiness`, async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change });
  try {
    await bp.go("#/finops"); await acknowledgePreview(bp);
    assert.match(txt(bp.view()), /gap|withheld|unavailable/i);
    assert.doesNotMatch(txt(bp.view()), /CHF 0\.00/);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 dated generated planning evidence passes only financial criterion, not permission or other seven checks", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change: planningEvidence });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    assert.match(txt(summary(bp)), /planning evidence.*2026-11-12.*not.*permission/i);
    await bp.go("#/journeys/D5");
    const row = [...bp.view().querySelectorAll("table.hand tbody tr")].find((r) => txt(r).includes("Service Report"));
    assert.ok(row);
    assert.equal(row.querySelectorAll("td")[6].querySelector(".hv").getAttribute("title"), "Done");
    assert.match(txt(row.lastElementChild), /Not yet/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

const priceRecord = (r) => r.scenarios.expected.months[0].lines[0].pricing_evidence.records[0];
for (const [label, change] of [
  ["synthetic pricing verification", (r) => { priceRecord(r).verification_status = "synthetic"; }],
  ["synthetic pricing source", (r) => { priceRecord(r).source_status = "synthetic"; }],
  ["unverified pricing verification", (r) => { priceRecord(r).verification_status = "unverified"; }],
  ["unverified pricing source", (r) => { priceRecord(r).source_status = "unverified"; }],
  ["missing pricing status", (r) => { delete priceRecord(r).verification_status; }],
  ["missing pricing records", (r) => { r.scenarios.expected.months[0].lines[0].pricing_evidence.records = []; }],
  ["provisional monthly line", (r) => { r.scenarios.expected.months[0].lines[0].cost.status = "provisional"; }],
  ["provisional one-time line", (r) => { r.scenarios.expected.one_time_lines[0].cost.status = "provisional"; }],
  ["provisional annual verified contribution", (r) => { r.scenarios.expected.annual_recurring.verified_subtotal.status = "provisional"; }],
  ["nonempty annual provisional contribution", (r) => { Object.assign(r.scenarios.expected.annual_recurring.provisional_subtotal,
    { amount: "1320.00", status: "provisional", reason: "pricing-evidence-incomplete" }); }],
  ["nonempty monthly provisional contribution", (r) => { Object.assign(r.scenarios.expected.months[0].provisional_subtotal,
    { amount: "110.00", status: "provisional", reason: "pricing-evidence-incomplete" }); }],
  ["provisional known-priced contribution", (r) => { r.scenarios.expected.annual_recurring.known_priced_subtotal.status = "provisional"; }]
]) it(`Task6 SPEC1 rejects ${label} despite a ready root assertion`, async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { planningEvidence(data); change(record(data)); } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.match(txt(summary(bp)), /Financial handover gap/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 SPEC1 fully verified test-only evidence permits legitimately empty provisional groups", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change: planningEvidence });
  try {
    const r = JSON.parse(bp.doc.getElementById("bp-data").textContent).agent_finops.records[0];
    for (const sc of Object.values(r.scenarios)) {
      for (const line of [...sc.months.flatMap((m) => m.lines), ...sc.one_time_lines]) {
        assert.equal(line.cost.status, "available");
        for (const p of line.pricing_evidence.records) {
          assert.equal(p.verification_status, "verified");
          assert.equal(p.source_status, "validated");
        }
      }
      for (const group of [sc.annual_recurring, sc.one_time, sc.first_year, ...sc.months]) {
        assert.equal(group.verified_subtotal.status, "available");
        assert.equal(group.provisional_subtotal.amount, null);
        assert.equal(group.provisional_subtotal.reason, "empty-priced-group");
      }
    }
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    assert.match(txt(summary(bp)), /not authenticated.*[Nn]ot.*permission/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

for (const [label, change] of [
  ["actor without delegation", (r) => { r.handover.owner_review.actor = "Test-only delegate"; }],
  ["missing profile finance owner", (r) => { delete r.profile.owners.finance; }],
  ["future review date", (r) => { r.handover.owner_review.date = "2099-01-01"; }],
  ["mismatched finance owner", (r) => { r.handover.owner_review.finance_owner = "Different test-only owner"; }],
  ["blank actor", (r) => { r.handover.owner_review.actor = " "; }],
  ["missing evidence reference", (r) => { delete r.handover.owner_review.evidence_ref; }],
  ["blank delegation reference", (r) => { Object.assign(r.handover.owner_review, { actor: "Test-only delegate", delegation_evidence_ref: " " }); }],
  ["missing review date", (r) => { delete r.handover.owner_review.date; }],
  ["invalid calendar date", (r) => { r.handover.owner_review.date = "2026-02-30"; }],
  ["missing recording date", (r) => { delete r.handover.owner_review.recorded_as_of; }],
  ["recording before review", (r) => { r.handover.owner_review.recorded_as_of = "2026-11-11"; }],
  ["future recording date", (r) => { r.handover.owner_review.recorded_as_of = "2099-01-01"; }]
]) it(`Task6 SPEC2 rejects ${label} despite a ready root assertion`, async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { planningEvidence(data); change(record(data)); } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.match(txt(summary(bp)), /Financial handover gap/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 SPEC2 accepts test-only exact-owner and evidenced delegation at the evaluation-date boundary", async () => {
  for (const delegated of [false, true]) {
    const bp = await openBlueprint(BASELINE_HTML, { change(data) {
      planningEvidence(data);
      if (delegated) Object.assign(record(data).handover.owner_review,
        { actor: "Test-only delegate", delegation_evidence_ref: "test-only:external-delegation" });
    } });
    try {
      const r = JSON.parse(bp.doc.getElementById("bp-data").textContent).agent_finops.records[0];
      assert.equal(r.handover.owner_review.finance_owner, r.profile.owners.finance);
      assert.equal(r.handover.owner_review.date, r.handover.owner_review.recorded_as_of);
      assert.equal(r.handover.owner_review.recorded_as_of, r.as_of);
      await bp.go("#/agents/D3-A05");
      assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
      assert.match(txt(summary(bp)), /not authenticated.*[Nn]ot.*permission/);
      assert.deepEqual(bp.errors, []);
    } finally { await bp.close(); }
  }
});

it("Task6 SPEC3 shows the actual unpriced annual known-priced subtotal, never a full cost", async () => {
  const report = unpricedReport();
  assert.equal(report.scenarios.expected.annual_recurring.amount, null);
  assert.equal(report.scenarios.expected.annual_recurring.known_priced_subtotal.amount, "120.00");
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops.records = [report]; } });
  try {
    await bp.go("#/finops");
    assert.equal(bp.view().querySelectorAll(".baseline-known").length, 0, "ack gate still covers known amounts");
    await acknowledgePreview(bp);
    const expected = bp.view().querySelector('.baseline-scenario[data-scenario="expected"]');
    const annual = expected.querySelector(".baseline-contributions .baseline-known");
    assert.ok(annual, "annual known-priced subtotal is visible outside collapsed details");
    assert.match(txt(annual), /Known-priced subtotal.*not full cost.*CHF 120\.00.*provisional.*pricing-evidence-incomplete/);
    assert.match(txt(expected.querySelector(".grid3 > div > .baseline-money")), /Unavailable.*incomplete.*incomplete-cost/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 SPEC3 shows actual monthly known-priced subtotals beside unavailable full totals", async () => {
  const report = unpricedReport();
  const month = report.scenarios.expected.months[0];
  assert.equal(month.total.amount, null);
  assert.equal(month.known_priced_subtotal.amount, "10.00");
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops.records = [report]; } });
  try {
    await bp.go("#/finops"); await acknowledgePreview(bp);
    const table = bp.view().querySelector('.baseline-scenario[data-scenario="expected"] .baseline-months');
    const index = [...table.querySelectorAll("th")].findIndex((th) => txt(th).includes("Known-priced subtotal"));
    assert.notEqual(index, -1, "monthly table explicitly labels known-priced, not full cost");
    const cells = table.querySelector("tbody tr").children;
    assert.match(txt(cells[index]), /CHF 10\.00.*provisional.*pricing-evidence-incomplete/);
    assert.match(txt(cells[1]), /Unavailable.*incomplete.*incomplete-cost/);
    assert.doesNotMatch(txt(cells[1]), /CHF 0\.00/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 SPEC3 all-unpriced known groups stay unavailable, not zero or financial readiness", async () => {
  const report = unpricedReport(true);
  assert.equal(report.scenarios.expected.annual_recurring.known_priced_subtotal.amount, null);
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops.records = [report]; } });
  try {
    await bp.go("#/finops"); await acknowledgePreview(bp);
    const known = [...bp.view().querySelectorAll(".baseline-known")];
    assert.equal(known.length, 9);
    for (const group of known) assert.match(txt(group), /Known-priced subtotal.*Unavailable.*empty-priced-group/);
    assert.doesNotMatch(txt(bp.view()), /CHF 0\.00/);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 QUALITY1 a relabelled A05 report cannot complete A04 or taint independent A05", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    planningEvidence(data);
    const wrong = structuredClone(record(data));
    wrong.agent_id = "D3-A04";
    data.agent_finops.records.push(wrong);
  } });
  try {
    await bp.go("#/agents/D3-A04");
    assert.equal(summary(bp, "D3-A04").getAttribute("data-financial-ready"), "false");
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    await bp.go("#/plan");
    const cards = [...bp.view().querySelectorAll(".kcard")];
    assert.match(txt(cards.find((c) => txt(c).includes("Service Field Assistant"))), /Financial handover gap/);
    assert.match(txt(cards.find((c) => txt(c).includes("Service Report"))), /Financial handover: planning evidence/);
    await bp.go("#/finops");
    assert.match(txt(bp.view().querySelector(".baseline-error")), /agent.*(binding|association).*rebuild/i);
    await acknowledgePreview(bp);
    assert.equal(bp.view().querySelectorAll('.baseline-record[data-agent="D3-A04"]').length, 0);
    assert.equal(bp.view().querySelectorAll('.baseline-record[data-agent="D3-A05"]').length, 1);
    assert.equal(bp.view().querySelectorAll(".baseline-export").length, 2);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 QUALITY1 a conflicting explicit profile binding is not reassigned to either agent", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    planningEvidence(data);
    record(data).profile.agent_id = "D3-A04";
  } });
  try {
    for (const id of ["D3-A04", "D3-A05"]) {
      await bp.go("#/agents/" + id);
      assert.equal(summary(bp, id).getAttribute("data-financial-ready"), "false");
    }
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 QUALITY1 a consistent agent binding passes only its own financial criterion", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change: planningEvidence });
  try {
    const r = JSON.parse(bp.doc.getElementById("bp-data").textContent).agent_finops.records[0];
    assert.equal(r.agent_id, r.profile.agent_id);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    await bp.go("#/agents/D3-A04");
    assert.equal(summary(bp, "D3-A04").getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

for (const [label, key, value] of [
  ["missing version", "version", undefined], ["zero version", "version", 0],
  ["blank version", "version", ""], ["negative version", "version", -1],
  ["boolean version", "version", true], ["text version", "version", "1"],
  ["fractional version", "version", 1.5], ["missing ID", "id", undefined],
  ["blank ID", "id", " "], ["non-string ID", "id", 1]
]) it(`Task6 QUALITY2 rejects ${label} even when all target copies agree`, async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    planningEvidence(data);
    const r = record(data);
    const targetKey = key === "id" ? "baseline_id" : key;
    for (const [object, field] of [[r.baseline, key], [r.handover.target, targetKey], [r.handover.owner_review, targetKey]]) {
      if (value === undefined) delete object[field]; else object[field] = value;
    }
  } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 QUALITY2 a positive integer customer target passes without projected private hashes", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    planningEvidence(data);
    data.agent_finops.audience = "customer";
    const r = record(data);
    r.audience = "customer";
    r.distribution = "scoped-derivative-not-authorisation";
    delete r.handover.target;
    delete r.handover.owner_review.material_hash;
  } });
  try {
    const r = JSON.parse(bp.doc.getElementById("bp-data").textContent).agent_finops.records[0];
    assert.equal(r.baseline.version, 1);
    assert.equal(r.handover.target, undefined);
    assert.equal(r.handover.owner_review.material_hash, undefined);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

for (const [label, change, fx] of [
  ["unverified cached rate", (r) => { r.evidence.rates[0].verification.status = "unverified"; }],
  ["unverified cached source", (r) => { r.evidence.sources[0].validationStatus = "unverified"; }],
  ["missing consumed rate", (r) => { r.evidence.rates.shift(); }],
  ["missing consumed source", (r) => { r.evidence.sources.shift(); }],
  ["contradictory explicit rate source", (r) => { r.evidence.rates[0].source_id = "MISSING-SOURCE"; }],
  ["missing pricing source identity", (r) => { delete priceRecord(r).source_id; }],
  ["ambiguous cached rate", (r) => { r.evidence.rates.push(structuredClone(r.evidence.rates[0])); }],
  ["ambiguous cached source", (r) => { r.evidence.sources.push(structuredClone(r.evidence.sources[0])); }],
  ["unverified consumed FX", (r) => { r.evidence.fx[0].verification.status = "unverified"; }, true],
  ["missing consumed FX", (r) => { r.evidence.fx = []; }, true],
  ["contradictory explicit FX source", (r) => { r.evidence.fx[0].source_id = "SYN-ENGINEERING"; }, true],
  ["unverified consumed FX source", (r) => { r.evidence.sources.find((s) => s.id === "SYN-FX").validationStatus = "unverified"; }, true]
]) it(`Task6 QUALITY3 rejects ${label} despite verified copied line statuses`, async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    if (fx) data.agent_finops.records = [fxReport()];
    planningEvidence(data);
    change(record(data));
  } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 QUALITY3 accepts actual consumed FX links without stripped legacy aliases", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    data.agent_finops.records = [fxReport()];
    planningEvidence(data);
  } });
  try {
    const r = JSON.parse(bp.doc.getElementById("bp-data").textContent).agent_finops.records[0];
    const fx = r.evidence.fx[0];
    assert.equal(fx.src, undefined);
    assert.equal(fx.content_src, undefined);
    const used = r.scenarios.expected.months[0].lines[0].pricing_evidence.records.find((p) => p.kind === "fx");
    assert.equal(used.id, fx.id);
    assert.equal(used.source_id, fx.source_id);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 QUALITY3 explicit consumed metadata stays sufficient when optional cache aliases are absent", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    data.agent_finops.records = [fxReport()];
    planningEvidence(data);
    delete record(data).evidence.rates[0].source_id;
    delete record(data).evidence.fx[0].source_id;
  } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 QUALITY3 unused bad/private cached evidence does not taint consumed verified evidence", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    planningEvidence(data);
    const r = record(data);
    r.evidence.rates.push({ id: "UNUSED-RATE", amount: "1", currency: "CHF", source_id: "UNUSED-SOURCE",
      verification: { status: "unverified" }, sharingClassification: "internal-only" });
    r.evidence.sources.push({ id: "UNUSED-SOURCE", type: "synthetic", validationStatus: "unverified",
      sharingClassification: "internal-only" });
  } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

for (const audience of ["internal", "customer"]) it(`Task6 FINAL1 actual reviewed recurring-only ${audience} scope passes without inventing one-time cost`, async () => {
  const view = reviewedScopeReports("recurring-only")[audience];
  const r = view.records[0];
  assert.equal(r.handover.ready, true, "actual dated producer decision");
  assert.deepEqual(r.gaps, []);
  assert.deepEqual(r.handover.gaps, []);
  assert.ok(r.context.exclusions.some((e) => e.id === "EXC-BUILD" && e.reason));
  for (const sc of Object.values(r.scenarios)) {
    assert.deepEqual(sc.one_time_lines, []);
    assert.equal(sc.one_time.amount, null);
    assert.equal(sc.one_time.status, "incomplete");
    assert.equal(sc.one_time.reason, "incomplete-cost");
    assert.equal(sc.first_year.amount, sc.annual_recurring.amount);
    assert.equal(sc.first_year.status, "available");
  }
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops = view; } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    await bp.go("#/finops"); await acknowledgePreview(bp);
    assert.match(txt(bp.view()), /Unavailable.*incomplete.*incomplete-cost/);
    assert.match(txt(bp.view()), /No one-time lines in the supplied scope; no zero cost is asserted/);
    assert.doesNotMatch(txt(bp.view()), /CHF 0\.00/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 FINAL1 actual reviewed full-cost controls retain their declared one-time evidence", async () => {
  const reports = reviewedScopeReports("full-cost");
  for (const view of Object.values(reports)) {
    const r = view.records[0];
    assert.equal(r.handover.ready, true);
    assert.equal(r.scenarios.expected.one_time_lines.length, 1);
    assert.equal(r.scenarios.expected.one_time.status, "available");
    const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops = view; } });
    try {
      await bp.go("#/agents/D3-A05");
      assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
      assert.deepEqual(bp.errors, []);
    } finally { await bp.close(); }
  }
});

it("Task6 FINAL1 actual declared unpriced one-time lines remain a financial gap", async () => {
  for (const view of Object.values(reviewedScopeReports("unpriced-one-time"))) {
    const r = view.records[0];
    assert.equal(r.handover.ready, false);
    assert.equal(r.scenarios.expected.one_time_lines.length, 1);
    assert.equal(r.scenarios.expected.one_time.amount, null);
    const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops = view; } });
    try {
      await bp.go("#/agents/D3-A05");
      assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
      assert.deepEqual(bp.errors, []);
    } finally { await bp.close(); }
  }
});

it("Task6 FINAL1 actual customer-withheld one-time costs are not reviewed absence", async () => {
  const view = reviewedScopeReports("private-one-time").customer, r = view.records[0];
  assert.equal(r.handover.ready, false);
  assert.equal(r.scenarios.expected.one_time.amount, null);
  assert.equal(r.scenarios.expected.one_time.status, "withheld");
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops = view; } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

const coverageCore = (coverage) => Object.fromEntries(
  ["priced_driver_count", "in_scope_driver_count", "status", "reason"].map((key) => [key, coverage[key]]));
for (const [kind, audience, priced, scope, status, reason] of [
  ["full-cost", "internal", 3, 3, "complete", null],
  ["recurring-only", "customer", 2, 2, "complete", null],
  ["provisional", "internal", 0, 3, "incomplete", "incomplete-evidenced-pricing"],
  ["unpriced-one-time", "internal", 2, 3, "incomplete", "incomplete-evidenced-pricing"],
  ["empty-scope", "internal", 0, 0, "unavailable", "empty-scope"],
  ["private-one-time", "customer", null, null, "withheld", "restricted-dependency"],
  ["private-unused", "customer", 3, 3, "complete", null],
  ["private-outcome", "customer", 3, 3, "complete", null]
]) it(`Task6 FINAL2 displays supplied ${kind}/${audience} coverage without deriving driver counts`, async () => {
  const view = reviewedScopeReports(kind)[audience], r = view.records[0];
  assert.deepEqual(coverageCore(r.driver_coverage), {
    priced_driver_count: priced, in_scope_driver_count: scope, status, reason
  });
  assert.deepEqual(coverageCore(r.handover.driver_coverage), coverageCore(r.driver_coverage));
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops = view; } });
  try {
    await bp.go("#/finops");
    assert.equal(bp.view().querySelectorAll(".driver-coverage").length, 0, "financial counts require fresh acknowledgement");
    await acknowledgePreview(bp);
    const coverage = bp.view().querySelector(".driver-coverage");
    assert.ok(coverage, "explicit aggregate cost-driver coverage panel");
    assert.match(txt(coverage), /Evidenced priced drivers \/ in-scope drivers/);
    assert.ok(txt(coverage).includes(status), status);
    if (priced === null) {
      assert.match(txt(coverage), /Withheld.*restricted-dependency/);
      assert.doesNotMatch(txt(coverage), /0 \/ 0|2 \/ 2|3 \/ 3/);
    } else assert.ok(txt(coverage).includes(`${priced} / ${scope}`));
    if (reason) assert.ok(txt(coverage).includes(reason), reason);
    assert.match(txt(coverage), /all.*scenarios.*periods.*declared scope/i);
    assert.doesNotMatch(txt(coverage), /%|CHF|EUR|USD/);
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), String(r.handover.ready));
    assert.ok(summary(bp).querySelector(".driver-coverage"));
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

for (const [label, change] of [
  ["missing report coverage", (r) => { delete r.driver_coverage; }],
  ["missing dated handover coverage", (r) => { delete r.handover.driver_coverage; }],
  ["incomplete coverage", (r) => {
    r.driver_coverage = reviewedScopeReports("unpriced-one-time").internal.records[0].driver_coverage;
    r.handover.driver_coverage = structuredClone(r.driver_coverage);
  }],
  ["withheld coverage", (r) => {
    r.driver_coverage = reviewedScopeReports("private-one-time").customer.records[0].driver_coverage;
    r.handover.driver_coverage = structuredClone(r.driver_coverage);
  }],
  ["empty coverage", (r) => {
    r.driver_coverage = reviewedScopeReports("empty-scope").internal.records[0].driver_coverage;
    r.handover.driver_coverage = structuredClone(r.driver_coverage);
  }],
  ["different complete handover scope", (r) => {
    r.handover.driver_coverage = reviewedScopeReports("recurring-only").internal.records[0].driver_coverage;
  }],
  ["non-integer count", (r) => { r.driver_coverage.priced_driver_count = 2.5; }],
  ["unsafe count", (r) => {
    Object.assign(r.driver_coverage, { priced_driver_count: Number.MAX_SAFE_INTEGER + 1, in_scope_driver_count: Number.MAX_SAFE_INTEGER + 1 });
    r.handover.driver_coverage = structuredClone(r.driver_coverage);
  }]
]) it(`Task6 FINAL2 ${label} cannot inherit financial readiness from a root assertion`, async () => {
  const view = reviewedScopeReports("full-cost").internal, r = view.records[0];
  assert.equal(r.handover.ready, true);
  change(r);
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops = view; } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.match(txt(summary(bp)), /[Rr]ebuild/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 FINAL2 coverage JSON and labelled Markdown retain the same supplied metric after acknowledgement", async () => {
  const view = reviewedScopeReports("full-cost").internal, r = view.records[0];
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { data.agent_finops = view; } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.doesNotMatch(txt(summary(bp)), /3 \/ 3/, "Canvas must not reveal counts before acknowledgement");
    await bp.go("#/finops"); await acknowledgePreview(bp);
    const blobs = downloadsFor(bp);
    button(bp, "Download projected report JSON").click();
    button(bp, "Download projected report Markdown").click();
    assert.deepEqual(JSON.parse(await blobs[0].text()), r);
    const md = await blobs[1].text();
    assert.match(md, /Evidenced priced drivers \/ in-scope drivers: 3 \/ 3.*complete/);
    assert.match(md, /declared scope.*not.*real-world/i);
    assert.match(md, /priced\\?_driver\\?_count/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

for (const [label, change] of [
  ["dated mismatch", (r) => { r.handover.as_of = "2026-11-11"; }],
  ["raw approval only", (r) => { delete r.handover.schema; }],
  ["missing external review", (r) => { r.handover.owner_review = null; }],
  ["unpriced", (r) => { r.handover.pricing_completeness = "incomplete"; }],
  ["synthetic", (r) => { r.mode = "synthetic"; }],
  ["contradictory provisional total", (r) => { r.scenarios.expected.annual_recurring.status = "provisional"; }],
  ["missing scenario", (r) => { delete r.scenarios.high; }],
  ["missing month", (r) => { r.scenarios.low.months.pop(); }],
  ["synthetic evidence marker", (r) => { r.evidence.sources[0].type = "synthetic"; }],
  ["mismatched frozen review", (r) => { r.handover.owner_review.material_hash = "different-test-target"; }]
]) it(`Task6 ${label} cannot pass even with ready true`, async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) { planningEvidence(data); change(record(data)); } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "false");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 customer-projected planning evidence needs no reconstructed technical hash", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    planningEvidence(data);
    data.agent_finops.audience = "customer";
    const r = record(data);
    r.audience = "customer";
    r.distribution = "scoped-derivative-not-authorisation";
    delete r.handover.target;
    delete r.handover.owner_review.material_hash;
  } });
  try {
    await bp.go("#/agents/D3-A05");
    assert.equal(summary(bp).getAttribute("data-financial-ready"), "true");
    assert.doesNotMatch(txt(summary(bp)), /test-only-frozen-target/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 downloads serialize the projected DTO exactly, escape Markdown and never mutate results through proposals", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    record(data).profile.name = "<b>Escaped</b> [label](https://example.invalid) | café";
  } });
  try {
    const original = JSON.parse(bp.doc.getElementById("bp-data").textContent).agent_finops.records[0];
    await bp.go("#/finops"); await acknowledgePreview(bp);
    const blobs = downloadsFor(bp);
    const proposal = bp.view().querySelector(".baseline-proposal textarea");
    proposal.value = "Proposed CHF 999.123";
    proposal.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    button(bp, "Download projected report JSON").click();
    button(bp, "Download projected report Markdown").click();
    assert.deepEqual(JSON.parse(await blobs[0].text()), original);
    const md = await blobs[1].text();
    for (const token of ["Preview", "1320.00", "1.100000", "2026-11-12", "CHF", "formulas", "gaps", "handover", "not authenticated"]) assert.ok(md.includes(token), token);
    assert.match(md, /&lt;b&gt;Escaped&lt;\/b&gt;/);
    assert.match(md, /\\\[label\\\]\\\(https:\/\/example\.invalid\\\)/);
    assert.doesNotMatch(md, /999\.123/);
    assert.equal(bp.view().querySelector(".baseline-record h3 b"), null);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("Task6 financial gaps preserve explicitly declared build/release/operate stages", async () => {
  const bp = await openBlueprint(BASELINE_HTML, { change(data) {
    const agents = data.domains[0].agents;
    ["In build", "Released", "In production"].forEach((lifecycle, i) => { agents[i].lifecycle = lifecycle; });
  } });
  try {
    await bp.go("#/plan");
    for (const stage of ["In build", "Released", "Operate & learn"]) {
      const cell = [...bp.view().querySelectorAll(".kbcell")].find((c) => c.getAttribute("aria-label").includes(` · ${stage}:`) && c.querySelector(".kcard"));
      assert.ok(cell, stage);
      assert.match(txt(cell), /Financial handover gap/);
    }
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});
