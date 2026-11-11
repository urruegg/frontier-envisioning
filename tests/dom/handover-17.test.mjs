import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { openBlueprint, DEFAULT_HTML, txt, wait } from "./helpers.mjs";

const VIEWS = ["Overview", "Org model", "Blueprint", "Journeys", "Use cases", "PRD",
  "Agents", "Agent identity", "Target architecture", "Ontology", "IT readiness",
  "Roadmap", "Plan", "Attendees", "Discovery", "Risks", "Evidence"];

describe("handover 1.7 renderer", () => {
  let bp;
  before(async () => { bp = await openBlueprint(); });
  after(async () => { await bp.close(); });

  it("lists all seventeen views in the four-part journey order", () => {
    assert.deepEqual([...bp.doc.querySelectorAll("#rail button")].map(txt), VIEWS);
    assert.deepEqual([...bp.doc.querySelectorAll("#rail .grp")].map(txt),
      ["Part 1 · Vision", "Part 2 · Design", "Part 3 · Build", "Part 4 · Workshops"]);
  });

  it("renders the 29-card plan in five lanes and seven stages", async () => {
    await bp.go("#/plan");
    assert.equal(bp.view().querySelectorAll(".kcard").length, 29);
    assert.equal(bp.view().querySelectorAll(".kblane").length, 5);
    assert.equal(bp.view().querySelectorAll(".kbst").length, 7);
    assert.equal(bp.view().querySelectorAll(".kbph").length, 4);
  });

  it("renders canonical and ontology risks with the reviewed rating totals", async () => {
    await bp.go("#/risks");
    assert.match(txt(bp.view().querySelector(".idstrip")).replace(/\s/g, ""), /22risks2high16medium4low/);
    assert.equal(bp.view().querySelectorAll(".riskrow").length, 22);
  });

  it("renders the MVP PRD and all semantic requirement IDs", async () => {
    await bp.go("#/prd");
    const data = JSON.parse(bp.doc.getElementById("bp-data").textContent);
    assert.equal(bp.view().querySelectorAll(".req tbody tr").length, 35);
    assert.equal(bp.view().querySelectorAll(".prd-nfr tbody tr").length, 12);
    for (const r of [...data.prd.platform, ...data.prd.agents.flatMap((a) => a.requirements), ...data.prd.nfr]) {
      assert.ok(txt(bp.view()).includes(r.id), r.id);
    }
  });

  it("shows eight attendees and thirteen sourced contributions", async () => {
    await bp.go("#/attendees");
    assert.equal(bp.view().querySelectorAll(".person").length, 8);
    assert.equal(bp.view().querySelectorAll(".contrib li").length, 13);
    assert.equal(bp.view().querySelectorAll(".contrib li .ev").length, 13);
    assert.match(txt(bp.view().querySelector(".contrib")), /\d\d:\d\d/);
  });

  it("filters Plan to two MVP cards, retains focus and opens their existing drawers", async () => {
    await bp.go("#/plan");
    const filter = bp.view().querySelector("#plan-mvp");
    assert.ok(filter, "MVP filter");
    filter.focus();
    filter.click();
    await wait(20);
    assert.equal(bp.doc.activeElement.id, "plan-mvp");
    assert.equal(bp.view().querySelectorAll(".kcard").length, 2);
    const journey = bp.view().querySelector("#plan-lane-D2");
    assert.ok(journey);
    journey.click();
    await wait(20);
    assert.equal(bp.doc.activeElement.id, "plan-lane-D2");
    assert.equal(bp.view().querySelector("#plan-lane-D2").getAttribute("aria-pressed"), "true");
    assert.equal(bp.view().querySelectorAll(".kcard").length, 1);
    await bp.click(bp.view().querySelector(".kcard"));
    assert.equal(bp.doc.getElementById("drawer").getAttribute("aria-hidden"), "false");
    bp.doc.getElementById("drawer-close").click();
  });

  it("keeps arrow keys inside the locally scrollable Plan instead of changing pages", async () => {
    await bp.go("#/plan");
    const board = bp.view().querySelector(".kbwrap");
    assert.ok(board);
    board.focus();
    board.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
    assert.equal(bp.window.location.hash, "#/plan");
    board.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true }));
    assert.equal(bp.window.location.hash, "#/plan");
  });

  it("saves risk ratings, status and notes with model-compatible feedback keys and focus", async () => {
    await bp.go("#/risks");
    const rating = bp.view().querySelector('select[id$="-likelihood"]');
    assert.ok(rating, "risk rating");
    const id = rating.id;
    rating.focus();
    rating.value = "5";
    rating.dispatchEvent(new bp.window.Event("change", { bubbles: true }));
    await wait(20);
    assert.equal(bp.doc.activeElement.id, id);
    const riskId = bp.view().querySelector("#rpanel").getAttribute("data-risk");
    assert.equal(bp.notes()[`val|risk|${riskId}`].likelihood, 5);
    const note = bp.view().querySelector("#rpanel textarea");
    note.value = "Confirm owner ✓";
    note.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    assert.equal(bp.notes()[`val|risk|${riskId}`].note, "Confirm owner ✓");
    await bp.go("#/prd");
    const scope = bp.view().querySelector('.valbox input[value="validated"]');
    assert.ok(scope);
    scope.click();
    assert.equal(bp.notes()["val|prd|scope"].status, "validated");
    await bp.go("#/agents/D3-A05");
    assert.match(txt(bp.view()), /Service Report/);
    assert.equal(bp.notes()[`val|risk|${riskId}`].likelihood, 5);
  });

  it("links use-case risks and Roadmap and Factory pages to the live Plan", async () => {
    await bp.go("#/usecases/UC09");
    const risk = bp.view().querySelector(".uc-risk-links button");
    assert.ok(risk, "use case risk links");
    const id = txt(risk);
    risk.click();
    assert.equal(bp.doc.querySelector("#rpanel").getAttribute("data-risk"), id);
    for (const route of ["#/roadmap", "#/journeys/D5"]) {
      await bp.go(route);
      const link = [...bp.view().querySelectorAll(".btn")].find((b) => txt(b) === "Plan");
      assert.ok(link, `${route} links Plan`);
      link.click();
      assert.equal(bp.window.location.hash, "#/plan");
    }
  });

  it("includes new PRD and risk verdicts in the human-readable notes export", async () => {
    let copied = "";
    bp.window.navigator.clipboard.writeText = async (text) => { copied = text; };
    await bp.go("#/discovery");
    const copy = [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Copy notes as text");
    copy.click();
    await wait(20);
    assert.match(copied, /PRD scope: validated/);
    assert.match(copied, /Risk .*Likelihood 5/);
    assert.match(copied, /Confirm owner ✓/);
  });
});

it("PRD scope badge follows a restored validated verdict becoming rejected with notes and focus", async () => {
  const bp = await openBlueprint();
  try {
    await bp.go("#/prd");
    bp.view().querySelector("#v-prd-scope-validated").click();
    const textarea = bp.view().querySelector(".valbox textarea");
    textarea.value = "Scope review ✓";
    textarea.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    await bp.go("#/overview");
    await bp.go("#/prd");
    assert.equal(txt(bp.view().querySelector(".idstrip > .pill")), "Validated");
    const reject = bp.view().querySelector("#v-prd-scope-rejected");
    reject.focus();
    reject.click();
    assert.equal(bp.notes()["val|prd|scope"].status, "rejected");
    assert.equal(bp.notes()["val|prd|scope"].note, "Scope review ✓");
    assert.equal(bp.view().querySelector("#v-prd-scope-rejected").checked, true);
    assert.equal(bp.doc.activeElement.id, "v-prd-scope-rejected");
    assert.equal(txt(bp.view().querySelector(".idstrip > .pill")), "Rejected");
    assert.deepEqual(bp.errors, []);
  } finally {
    await bp.close();
  }
});

async function fixture(change, run) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "frontier-17-"));
  const file = path.join(dir, "blueprint.html");
  const html = fs.readFileSync(DEFAULT_HTML, "utf8").replace(
    /(<script[^>]+id="bp-data"[^>]*>)([\s\S]*?)(<\/script>)/,
    (_, start, json, end) => {
      const data = JSON.parse(json);
      change(data);
      return start + JSON.stringify(data).replace(/</g, "\\u003c") + end;
    });
  fs.writeFileSync(file, html);
  const bp = await openBlueprint(file);
  try { await run(bp); } finally { await bp.close(); fs.rmSync(dir, { recursive: true, force: true }); }
}

it("uses part label/description overrides in rail and breadcrumb", async () => {
  await fixture((b) => { b.parts = { vision: { label: "Vision ✓", desc: "Workshop direction" } }; }, async (bp) => {
    assert.equal(txt(bp.doc.querySelector("#rail .grp")), "Vision ✓");
    assert.match(txt(bp.doc.getElementById("crumb")), /Vision ✓.*Workshop direction/);
  });
});

it("renders older data without parts, PRD, risks, board or structured contributions", async () => {
  await fixture((b) => {
    delete b.parts; delete b.prd; delete b.risks;
    if (b.factory) delete b.factory.board;
    b.attendees.people[0].contributions = ["Legacy contribution"];
    b.attendees.people[1].contributions = [{ text: "Unsourced contribution" }];
    delete b.attendees.people[1].src;
  }, async (bp) => {
    assert.equal(bp.doc.querySelectorAll("#rail button").length, 15);
    await bp.go("#/plan");
    assert.equal(bp.view().querySelectorAll(".kcard").length, 29);
    await bp.go("#/attendees");
    assert.match(txt(bp.view()), /Legacy contribution/);
    assert.match(txt(bp.view()), /No evidence yet/);
    assert.deepEqual(bp.errors, []);
  });
});

it("never keeps a filtered or closed selected risk, including an empty category", async () => {
  await fixture((b) => {
    b.risks.items = [
      { id: "R-A", title: "First", category: "data", likelihood: 3, impact: 3 },
      { id: "R-B", title: "Second", category: "cost", likelihood: 2, impact: 2 }
    ];
  }, async (bp) => {
    await bp.go("#/risks");
    assert.equal(bp.view().querySelector("#rpanel")?.getAttribute("data-risk"), "R-A");
    let category = bp.view().querySelector("#risk-category");
    assert.ok(category);
    category.value = "cost";
    category.dispatchEvent(new bp.window.Event("change", { bubbles: true }));
    assert.equal(bp.doc.activeElement.id, "risk-category");
    assert.equal(bp.view().querySelector("#rpanel").getAttribute("data-risk"), "R-B");
    bp.view().querySelector('#rpanel input[value="closed"]').click();
    await wait(20);
    assert.equal(bp.view().querySelector("#rpanel"), null);
    assert.equal(bp.view().querySelectorAll(".riskrow").length, 0);
    assert.match(txt(bp.view().querySelector('[role="status"]')), /No risk matches/);
    assert.equal(bp.doc.activeElement.id, "risk-category");
    bp.view().querySelector("#rk-closed").click();
    await wait(20);
    assert.equal(bp.view().querySelector("#rpanel").getAttribute("data-risk"), "R-B");
    assert.equal(bp.doc.activeElement.id, "rk-closed");
    assert.deepEqual(bp.errors, []);
  });

});

it("displays authored WIP limits as advisory without removing or disabling cards", async () => {
  await fixture((b) => { b.factory.board = { wip: { hypothesis: 0 } }; }, async (bp) => {
    await bp.go("#/plan");
    assert.ok(bp.view().querySelectorAll(".kbst.over").length > 0);
    assert.match(txt(bp.view()), /Above WIP limit \(advisory\)/);
    assert.equal(bp.view().querySelectorAll(".kcard").length, 29);
    assert.equal(bp.view().querySelectorAll(".kcard:disabled").length, 0);
  });

});

it("shows merged workshop risk notes and their evidence", async () => {
  await fixture((b) => {
    b.risks.items[0].workshop_notes = [{ date: "2026-11-11", note: "Mitigation owner agreed ✓", src: ["E01"] }];
  }, async (bp) => {
    await bp.go("#/risks");
    assert.match(txt(bp.view().querySelector("#rpanel")), /2026-11-11.*Mitigation owner agreed ✓/);
    assert.ok(bp.view().querySelector('#rpanel .workshop-risk-notes .ev'));
  });
});
