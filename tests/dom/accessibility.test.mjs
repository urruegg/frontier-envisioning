// A1 structural RED contracts for #7. Browser tests own actual focus and reflow.
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { openBlueprint, DEFAULT_HTML, txt, wait } from "./helpers.mjs";

function selectedTab(bp, listSelector, panelId, index) {
  const tabs = [...bp.doc.querySelectorAll(`${listSelector} [role="tab"]`)];
  assert.ok(tabs.length > 1, "genuine tab family exists");
  assert.equal(new Set(tabs.map((tab) => tab.id)).size, tabs.length, "unique stable IDs");
  tabs.forEach((tab, i) => {
    assert.ok(tab.id);
    assert.equal(tab.getAttribute("aria-selected"), String(i === index));
    assert.equal(tab.tabIndex, i === index ? 0 : -1);
    assert.equal(tab.getAttribute("aria-controls"), panelId);
  });
  const panel = bp.doc.getElementById(panelId);
  assert.ok(panel, "controlled panel exists");
  assert.equal(panel.getAttribute("role"), "tabpanel");
  assert.equal(panel.getAttribute("aria-labelledby"), tabs[index].id);
  assert.ok(txt(panel).length > 0, "selected content renders");
  return tabs[index];
}

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
    assert.ok(svg.getAttribute("aria-label"));
    assert.ok([...svg.querySelectorAll('[role="button"]')].every((node) =>
      node.getAttribute("tabindex") === "0" && node.getAttribute("aria-label")));
  });

  it("uses no aria-selected on ordinary organisation filter buttons", async () => {
    await bp.go("#/org");
    assert.ok(bp.view().querySelectorAll(".filters button").length > 1, "journey filters present");
    assert.equal(bp.view().querySelectorAll('button:not([role="tab"])[aria-selected]').length, 0);
    assert.equal(bp.view().querySelectorAll('.filters button[aria-pressed="true"]').length, 1);
    assert.equal(bp.view().querySelector(".filters button").getAttribute("aria-pressed"), "true");
    await bp.click(bp.view().querySelectorAll(".filters button")[1]);
    assert.equal(bp.view().querySelectorAll(".filters button")[1].getAttribute("aria-pressed"), "true");
    assert.equal(bp.view().querySelector(".filters button").getAttribute("aria-pressed"), "false");
    await bp.click(bp.view().querySelectorAll(".filters button")[1]);
    assert.equal(bp.view().querySelector(".filters button").getAttribute("aria-pressed"), "true");
  });

  it("keeps all filtered organisation labels opaque and all SVG buttons keyboard reachable", async () => {
    await bp.go("#/org");
    const count = bp.view().querySelectorAll(".orgsvg [role=button]").length;
    await bp.click(bp.view().querySelectorAll(".filters button")[1]);
    assert.equal(bp.view().querySelectorAll(".orgsvg [role=button]").length, count);
    for (const node of bp.view().querySelectorAll(".orgsvg [role=button]")) {
      assert.equal(node.tabIndex, 0);
    }
    for (const text of bp.view().querySelectorAll(".orgsvg text")) {
      for (let ancestor = text; ancestor; ancestor = ancestor.parentElement) {
        assert.equal(Number(bp.window.getComputedStyle(ancestor).opacity || 1), 1,
          `${txt(text)}: text and every ancestor stay opaque`);
      }
    }
    // Toggle back so this shared fixture does not leave a journey filter selected.
    await bp.click(bp.view().querySelector(".filters button"));
  });

  it("exposes matrix SVG controls independently rather than flattening them into an image", async () => {
    await bp.go("#/usecases");
    const svg = bp.view().querySelector("svg.matrix");
    assert.ok(svg.querySelectorAll('[role="button"]').length > 0, "interactive use case nodes");
    assert.equal(svg.getAttribute("role"), "group");
    assert.ok(svg.getAttribute("aria-label"));
    assert.ok([...svg.querySelectorAll('[role="button"]')].every((node) =>
      node.getAttribute("tabindex") === "0" && node.getAttribute("aria-label")));
  });

  it("uses no aria-selected on ordinary ADR filters", async () => {
    await bp.go("#/architecture");
    const decisions = [...bp.view().querySelectorAll(".atabs button")].find((tab) => /Decisions/.test(txt(tab)));
    assert.ok(decisions);
    await bp.click(decisions);
    assert.ok(bp.view().querySelectorAll(".filters button").length > 1, "ADR filters present");
    assert.equal(bp.view().querySelectorAll('button:not([role="tab"])[aria-selected]').length, 0);
    assert.equal(bp.view().querySelector(".filters button").getAttribute("aria-pressed"), "true");
    await bp.click(bp.view().querySelectorAll(".filters button")[1]);
    assert.equal(bp.view().querySelectorAll('.filters button[aria-pressed="true"]').length, 1);
    assert.equal(bp.view().querySelectorAll(".filters button")[1].getAttribute("aria-pressed"), "true");
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

  for (const route of ["blueprint", "journeys", "agents", "discovery"]) {
    it(`journey tabs label their panel and retain ${route} route and focus with roving keyboard navigation`, async () => {
      await bp.go(route === "agents" ? "#/agents/D3-A05" : `#/${route}/D1`);
      const count = bp.doc.querySelectorAll("#subnav [role=tab]").length;
      const start = route === "agents" ? 2 : 0;
      const tab = selectedTab(bp, "#subnav", "journey-panel", start);
      await bp.click(tab);
      assert.equal(bp.doc.activeElement.id, tab.id, "click restores focus after render");
      const expectedHash = (index) => route === "agents"
        ? new RegExp(`^#/agents/D${index + 1}-`)
        : new RegExp(`^#/${route}/D${index + 1}$`);
      assert.match(bp.window.location.hash, expectedHash(start));
      for (const [key, index] of [["ArrowRight", (start + 1) % count], ["Home", 0], ["ArrowLeft", count - 1], ["ArrowRight", 0], ["End", count - 1]]) {
        bp.doc.activeElement.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key, bubbles: true, cancelable: true }));
        const selected = selectedTab(bp, "#subnav", "journey-panel", index);
        assert.ok(bp.doc.activeElement === selected, `${key}: focus restored to activated tab`);
        assert.match(bp.window.location.hash, expectedHash(index), `${key}: same page, selected journey only`);
      }
      assert.deepEqual(bp.errors, []);
    });
  }

  for (const family of ["architecture", "factory"]) {
    it(`${family} tabs have stable controls, labelled panels and local Arrow/Home/End navigation`, async () => {
      await bp.go(family === "architecture" ? "#/architecture" : "#/journeys/D1");
      if (family === "factory") {
        await bp.click([...bp.doc.querySelectorAll("#subnav [role=tab]")].find((tab) => /factory/i.test(txt(tab))));
      }
      const selector = family === "architecture" ? ".atabs" : ".fsteps";
      const panelId = family === "architecture" ? "architecture-panel" : "factory-step-panel";
      const count = bp.doc.querySelectorAll(`${selector} [role=tab]`).length;
      const hash = bp.window.location.hash;
      const ids = [...bp.doc.querySelectorAll(`${selector} [role=tab]`)].map((tab) => tab.id);
      await bp.click(bp.doc.querySelector(`${selector} [role=tab]`));
      selectedTab(bp, selector, panelId, 0);
      for (const [key, index] of [["ArrowRight", 1], ["Home", 0], ["ArrowLeft", count - 1], ["ArrowRight", 0], ["End", count - 1]]) {
        bp.doc.activeElement.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key, bubbles: true, cancelable: true }));
        assert.ok(bp.doc.activeElement === selectedTab(bp, selector, panelId, index), `${key}: focus`);
        assert.equal(bp.window.location.hash, hash, `${key}: does not invoke global view shortcut`);
        assert.deepEqual([...bp.doc.querySelectorAll(`${selector} [role=tab]`)].map((tab) => tab.id), ids);
      }
      if (family === "architecture") {
        assert.equal(bp.view().querySelectorAll("h2.sec").length, 1);
        assert.equal(bp.doc.getElementById(panelId).contains(bp.view().querySelector("h2.sec")), false);
        assert.equal(bp.doc.getElementById(panelId).contains(bp.view().querySelector(".atabs")), false);
      } else {
        assert.equal(bp.view().querySelector(".fdetail").id, panelId, "reuse the existing detail panel");
        assert.ok(bp.doc.getElementById("journey-panel").contains(bp.doc.getElementById(panelId)));
      }
      assert.deepEqual(bp.errors, []);
    });
  }

  it("preserves modified keys, input guards, drawer priority and global shortcuts outside tablists", async () => {
    await bp.go("#/blueprint/D1");
    for (const modifier of ["altKey", "ctrlKey", "metaKey"]) {
      const tab = bp.doc.querySelector("#subnav [role=tab]");
      tab.focus();
      const event = new bp.window.KeyboardEvent("keydown", { key: "ArrowRight", [modifier]: true, bubbles: true, cancelable: true });
      tab.dispatchEvent(event);
      assert.equal(event.defaultPrevented, false);
      assert.equal(bp.window.location.hash, "#/blueprint/D1");
    }
    for (const tag of ["input", "textarea", "select"]) {
      const input = bp.doc.createElement(tag);
      bp.view().appendChild(input);
      input.focus();
      input.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
      assert.equal(bp.window.location.hash, "#/blueprint/D1");
      input.remove();
    }
    await bp.click(bp.view().querySelector(".leadcard"));
    bp.doc.activeElement.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
    assert.equal(bp.window.location.hash, "#/blueprint/D1", "open drawer takes precedence");
    bp.doc.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    bp.view().focus();
    bp.view().dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "ArrowRight", bubbles: true }));
    assert.equal(bp.window.location.hash, "#/journeys/D1", "global next view still works");
    bp.view().dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true }));
    assert.equal(bp.window.location.hash, "#/blueprint/D1", "global previous view still works");
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
      const tab = bp.doc.querySelector('#subnav [role=tab][aria-selected="true"]');
      const panel = bp.doc.getElementById("journey-panel");
      assert.equal(!!panel, !!tab, `${views[i]}: panel only when a journey tab exists`);
      if (panel) assert.equal(panel.getAttribute("aria-labelledby"), tab.id);
    }
    assert.deepEqual(bp.errors, []);
  } finally {
    if (bp) await bp.close();
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

it("renders older data with no journeys and untabbed classic architecture without orphan tabpanels", async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "frontier-a11y-no-tabs-"));
  let bp;
  try {
    const html = fs.readFileSync(process.env.BLUEPRINT_HTML || DEFAULT_HTML, "utf8");
    const sparse = {
      meta: { customer: "Caldova Industrial AG", version: "1.3.0" },
      domains: [],
      architecture: { layers: [{ name: "Service", blocks: [{ name: "Workflow" }] }] }
    };
    const file = path.join(directory, "sparse.html");
    fs.writeFileSync(file, html.replace(/(<script type="application\/json" id="bp-data">)[\s\S]*?(<\/script>)/,
      (_, start, end) => start + JSON.stringify(sparse) + end));
    bp = await openBlueprint(file);
    for (const route of ["blueprint", "journeys", "agents", "architecture"]) {
      await bp.go(`#/${route}`);
      assert.ok(txt(bp.view()).length > 0);
      assert.equal(bp.view().querySelector(".empty"), null);
      assert.equal(bp.doc.querySelectorAll('[role="tab"]').length, 0);
      assert.equal(bp.view().querySelectorAll('[role="tabpanel"]').length, 0);
    }
    assert.deepEqual(bp.errors, []);
  } finally {
    if (bp) await bp.close();
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

it("keeps rejected workshop agent and portfolio nodes opaque without losing saved notes or navigation", async () => {
  const bp = await openBlueprint();
  try {
    for (const [route, kind, selector] of [
      ["agents/D1-LEAD", "agent", ".orgsvg .node"],
      ["usecases", "uc", ".matrix .bub"]
    ]) {
      await bp.go(`#/${route}`);
      if (kind === "uc") await bp.click(bp.view().querySelector(".matrix .bub"));
      const reject = bp.view().querySelector('.valbox input[value="rejected"]');
      assert.ok(reject);
      reject.checked = true;
      reject.dispatchEvent(new bp.window.Event("change", { bubbles: true }));
      const saved = Object.entries(bp.notes()).find(([key]) => key.startsWith(`val|${kind}|`));
      assert.ok(saved, `${kind}: workshop verdict saved`);
      assert.equal(saved[1].status, "rejected");
      await bp.go(kind === "agent" ? "#/org" : "#/overview");
      if (kind === "uc") await bp.go("#/usecases");
      const nodes = [...bp.view().querySelectorAll(selector)];
      assert.ok(nodes.length > 0);
      for (const node of nodes) {
        assert.equal(node.tabIndex, 0);
        assert.equal(Number(node.getAttribute("opacity") || 1), 1, "operable node must not fade its text");
      }
    }
    assert.deepEqual(bp.errors, []);
  } finally {
    await bp.close();
  }
});

for (const [colour, foreground] of [
  ["#FFFFFF", "#000000"], ["#000000", "#FFFFFF"], ["#0000FF", "#FFFFFF"],
  ["#777777", "#000000"], ["#FFFF00", "#000000"], ["#00FFFF", "#000000"]
]) {
  it(`derives readable foregrounds from validated public data (${colour}) without altering icon art`, async () => {
    const directory = fs.mkdtempSync(path.join(os.tmpdir(), "frontier-a4-colour-"));
    let bp;
    try {
      const html = fs.readFileSync(process.env.BLUEPRINT_HTML || DEFAULT_HTML, "utf8");
      const island = /(<script type="application\/json" id="bp-data">)([\s\S]*?)(<\/script>)/;
      const data = JSON.parse(html.match(island)[2]);
      data.meta.accent = colour;
      for (const domain of data.domains) domain.color = colour;
      for (const journey of data.identity.journeys) {
        journey.colour = colour;
        journey.glyph = colour; // Renderer labels must not trust an unsuitable art glyph.
      }
      for (const environment of data.identity.environments) {
        if (environment.band) { environment.band = colour; environment.label = colour; }
      }
      const originalIcon = data.domains[0].agents[0].identity.icon;
      delete data.domains[0].orchestrator.identity.icon; // exercise the new Plan's generated fallback, not icon art
      data.meta.status_note = "A4 <>& \u2028\u2029";
      const escaped = JSON.stringify(data).replace(/</g, "\\u003c").replace(/>/g, "\\u003e")
        .replace(/&/g, "\\u0026").replace(/\u2028/g, "\\u2028").replace(/\u2029/g, "\\u2029");
      const file = path.join(directory, "variant.html");
      fs.writeFileSync(file, html.replace(island, (_, start, _json, end) => start + escaped + end));
      bp = await openBlueprint(file);
      assert.equal(bp.doc.documentElement.style.getPropertyValue("--accent-on"), foreground);
      assert.ok(bp.doc.getElementById("banner").textContent.includes(data.meta.status_note));
      await bp.go("#/blueprint/D1");
      const tabs = [...bp.doc.querySelectorAll("#subnav .tab")];
      assert.equal(tabs.length, data.domains.length);
      for (const tab of tabs) assert.equal(tab.style.getPropertyValue("--d-on"), foreground);
      await bp.go("#/identity");
      for (const selector of [".sw .chip", ".band .bchip:not(.clean)", ".family .fhead"]) {
        const nodes = [...bp.view().querySelectorAll(selector)];
        assert.ok(nodes.length > 0, selector);
        for (const node of nodes) {
          assert.equal(node.style.color.toUpperCase(), foreground);
        }
      }
      assert.ok([...bp.view().querySelectorAll("img.aicon")].some((image) =>
        image.getAttribute("src") === originalIcon), "embedded icon bytes unchanged");
      await bp.go("#/plan");
      const fallback = bp.view().querySelector(".kcard .ini");
      assert.ok(fallback, "plan fallback exists without identity artwork");
      assert.equal(fallback.style.color.toUpperCase(), foreground);
      assert.equal(bp.view().querySelector(".kcard").style.getPropertyValue("--d-on"), foreground);
      assert.deepEqual(bp.errors, []);
    } finally {
      if (bp) await bp.close();
      fs.rmSync(directory, { recursive: true, force: true });
    }
  });
}
