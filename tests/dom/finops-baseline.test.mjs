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

// In-memory contract fixture ONLY. Not an authoritative model/review, not shipped
// evidence or finance approval. No recalculation or alteration of the demo files.
// All projected pricing/source statuses and contribution groups are made
// internally consistent, including nested pricing_evidence records. Decimal
// strings are copied, not recalculated; the test hash is not a real receipt.
function planningEvidence(data) {
  const r = record(data);
  function available(value) {
    if (!value || typeof value !== "object") return;
    delete value.synthetic;
    if (value.status === "provisional") { value.status = "available"; value.reason = null; }
    if (value.type === "synthetic") value.type = "commercial";
    if (value.status === "synthetic") value.status = "verified";
    if (value.validationStatus === "synthetic") value.validationStatus = "validated";
    if (value.verification_status === "synthetic") value.verification_status = "verified";
    if (value.source_status === "synthetic") value.source_status = "validated";
    if (Array.isArray(value.gaps)) value.gaps = [];
    Object.values(value).forEach(available);
    if (value.verified_subtotal && value.provisional_subtotal) {
      const total = value.total || value;
      Object.assign(value.verified_subtotal, { amount: total.amount, status: "available", reason: null });
      Object.assign(value.provisional_subtotal, { amount: null, status: "unavailable", reason: "empty-priced-group" });
    }
  }
  available(r);
  r.mode = "planning";
  r.status = "planning-ready";
  r.gaps = [];
  r.profile.outcome.confirmation_status = "test-only-confirmed";
  r.handover = {
    schema: "frontier-finops-handover/1.0", as_of: r.as_of,
    target: { baseline_id: r.baseline.id, version: r.baseline.version, material_hash: "f".repeat(64) },
    lifecycle: "approved", structural_validation: "valid", pricing_completeness: "evidenced",
    ready: true, status: "planning-ready", gaps: [], financial_permission: false,
    owner_review: {
      schema: "frontier-finops-owner-review/1.0", id: "TEST-ONLY-REVIEW", decision: "approve",
      actor: "Finance lead", finance_owner: "Finance lead", date: r.as_of, evidence_ref: "test-only:external",
      baseline_id: r.baseline.id, version: r.baseline.version, material_hash: "f".repeat(64),
      mode: "planning", recorded_as_of: r.as_of, assertion: "externally-asserted-not-authenticated",
      sharingClassification: "customer-shareable",
      review_boundary: "Test-only external assertion, not authentication or permission."
    },
    limitations: "Planning evidence only; not budget, build or deployment permission."
  };
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
