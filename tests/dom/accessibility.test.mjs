// A1 structural RED contracts for #7. Browser tests own actual focus and reflow.
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { openBlueprint, DEFAULT_HTML, txt, wait } from "./helpers.mjs";

describe("accessibility structure", () => {
  let bp;
  before(async () => { bp = await openBlueprint(); });
  after(async () => { await bp.close(); });

  it("uses a neutral DIV shell for the modal, not a complementary landmark", () => {
    assert.equal(bp.doc.getElementById("drawer").tagName, "DIV");
  });

  it("keeps the closed drawer hidden, not just translated off screen", () => {
    assert.equal(bp.doc.getElementById("drawer").hidden, true);
  });

  it("keeps closed drawer descendants inert", () => {
    assert.equal(bp.doc.getElementById("drawer").hasAttribute("inert"), true);
  });

  it("keeps modal chrome out of document landmarks and names the status region", () => {
    const drawer = bp.doc.getElementById("drawer");
    assert.equal(drawer.querySelectorAll("header").length, 0);
    assert.equal(drawer.querySelectorAll(".drawer-head #drawer-close").length, 1);
    assert.equal(bp.doc.getElementById("scrim").getAttribute("aria-hidden"), "true");
    assert.equal(bp.doc.getElementById("banner").parentElement.getAttribute("aria-label"), "Blueprint status");
    assert.equal(bp.doc.getElementById("banner").parentElement.tagName, "SECTION");
  });

  it("exposes organisation SVG controls independently rather than flattening them into an image", async () => {
    await bp.go("#/org");
    const svg = bp.view().querySelector("svg.orgsvg");
    assert.ok(svg.querySelectorAll('[role="button"]').length > 0, "interactive organisation nodes");
    assert.equal(svg.getAttribute("role"), "group");
  });

  it("uses no aria-selected on ordinary organisation filter buttons", async () => {
    await bp.go("#/org");
    assert.ok(bp.view().querySelectorAll(".filters button").length > 1, "journey filters present");
    assert.equal(bp.view().querySelectorAll('button:not([role="tab"])[aria-selected]').length, 0);
  });

  it("exposes matrix SVG controls independently rather than flattening them into an image", async () => {
    await bp.go("#/usecases");
    const svg = bp.view().querySelector("svg.matrix");
    assert.ok(svg.querySelectorAll('[role="button"]').length > 0, "interactive use case nodes");
    assert.equal(svg.getAttribute("role"), "group");
  });

  it("uses no aria-selected on ordinary ADR filters", async () => {
    await bp.go("#/architecture");
    const decisions = [...bp.view().querySelectorAll(".atabs button")].find((tab) => /Decisions/.test(txt(tab)));
    assert.ok(decisions);
    await bp.click(decisions);
    assert.ok(bp.view().querySelectorAll(".filters button").length > 1, "ADR filters present");
    assert.equal(bp.view().querySelectorAll('button:not([role="tab"])[aria-selected]').length, 0);
  });

  it("uses no aria-selected on ordinary discovery filters", async () => {
    await bp.go("#/discovery");
    assert.ok(bp.view().querySelectorAll(".filters button").length > 1, "discovery filters present");
    assert.equal(bp.view().querySelectorAll('button:not([role="tab"])[aria-selected]').length, 0);
  });

  it("preserves navigation and localStorage workshop notes", async () => {
    await bp.go("#/readiness");
    const verdict = bp.view().querySelector('details.rgroup .assbox input[value="done"]');
    assert.ok(verdict);
    await bp.click(verdict);
    await wait(20);
    const saved = Object.entries(bp.notes()).find(([key]) => key.startsWith("val|ready|"));
    assert.ok(saved, "readiness verdict saved to localStorage");
    assert.equal(saved[1].status, "done");
    await bp.go("#/overview");
    await bp.go("#/readiness");
    assert.equal(bp.view().querySelector('details.rgroup .assbox input[value="done"]').checked, true);
    assert.deepEqual(bp.errors, []);
  });
});

it("restores original background inert states after repeated evidence drawer opens", async () => {
  const bp = await openBlueprint();
  try {
    await bp.go("#/evidence");
    const background = [".page", ".rail", ".skip"].map((selector) => bp.doc.querySelector(selector));
    const trigger = bp.view().querySelector(".pill.ev");
    assert.ok(trigger);
    for (const original of [[false, true, false], [true, false, true]]) {
      background.forEach((node, index) => { node.inert = original[index]; });
      await bp.click(trigger);
      assert.deepEqual(background.map((node) => node.inert), [true, true, true]);
      await bp.click(trigger);
      bp.doc.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      assert.deepEqual(background.map((node) => node.inert), original, "Escape restores the first-open snapshot");
    }
    assert.deepEqual(bp.errors, []);
  } finally {
    await bp.close();
  }
});

it("keeps pre-optional-field sparse blueprints rendering without inventing unavailable views", async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "frontier-a11y-sparse-"));
  let bp;
  try {
    const html = fs.readFileSync(process.env.BLUEPRINT_HTML || DEFAULT_HTML, "utf8");
    const sparse = {
      meta: { customer: "Caldova Industrial AG", short: "Caldova", version: "1.3.0" },
      domains: [{ id: "D1", name: "Service", color: "#005A9E", agents: [] }]
    };
    const island = /(<script type="application\/json" id="bp-data">)[\s\S]*?(<\/script>)/;
    assert.match(html, island, "built data island exists");
    const file = path.join(directory, "sparse.html");
    fs.writeFileSync(file, html.replace(island, (_, start, end) => start + JSON.stringify(sparse) + end));
    bp = await openBlueprint(file);
    const views = [...bp.doc.querySelectorAll("#rail button")].map(txt);
    assert.deepEqual(views, ["Overview", "Org model", "Blueprint", "Journeys", "Agents"]);
    for (let i = 0; i < views.length; i++) {
      await bp.click(bp.doc.querySelectorAll("#rail button")[i]);
      assert.ok(txt(bp.view()).length > 0, `${views[i]} renders with sparse data`);
      assert.equal(bp.view().querySelector(".empty"), null, `${views[i]} has no rendering error`);
    }
    assert.deepEqual(bp.errors, []);
  } finally {
    if (bp) await bp.close();
    fs.rmSync(directory, { recursive: true, force: true });
  }
});
