// DOM tests of the Frontier Company Blueprint (Caldova demo): views, navigation, Hub journey pages, notes.
// Run: python tools/dev.py dom   (or: node --test tests/dom/blueprint.test.mjs with BLUEPRINT_HTML set)
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { openBlueprint, txt, wait } from "./helpers.mjs";

const VIEWS = ["Overview", "Org model", "Blueprint", "Journeys", "Attendees", "Agents", "Agent identity", "Target architecture",
  "Use cases", "IT readiness", "FinOps", "Discovery", "Roadmap", "Evidence"];

describe("Frontier Company Blueprint (Caldova demo)", () => {
  let bp;
  before(async () => { bp = await openBlueprint(); });
  after(async () => { await bp.close(); });

  it("lists the 14 views of the Innovation Hub journey in order", () => {
    assert.deepEqual([...bp.doc.querySelectorAll("#rail button")].map(txt), VIEWS);
    assert.match(bp.doc.title, /Caldova Industrial AG/);
  });

  it("renders every view with a deep link and without errors", async () => {
    const count = bp.doc.querySelectorAll("#rail button").length;
    for (let i = 0; i < count; i++) {
      const button = bp.doc.querySelectorAll("#rail button")[i];
      button.click();
      await wait(20);
      const v = bp.view();
      assert.equal(v.querySelector(".empty"), null, `${txt(button)} shows an error`);
      assert.ok(v.textContent.length > 200, `${txt(button)} is nearly empty`);
      assert.match(bp.window.location.hash, /^#\//);
    }
    assert.deepEqual(bp.errors, []);
  });

  it("shows the Agent Factory journey: lifecycle, board, build steps, pyramid, roles, controls", async () => {
    await bp.go("#/journeys");
    const tab = [...bp.doc.querySelectorAll("#subnav .tab")].find((t) => /Agent Factory/.test(txt(t)));
    assert.ok(tab, "Agent Factory journey tab");
    tab.click();
    await wait(40);
    const v = bp.view();
    assert.equal(txt(v.querySelector("h2")), "Idea-to-Agent journey");
    assert.equal(v.querySelectorAll(".chev .chv").length, 7);
    assert.equal(v.querySelectorAll(".fboard .fcol2").length, 7);
    assert.ok(v.querySelectorAll(".fboard .agchip").length >= 20);
    assert.match([...v.querySelectorAll(".fboard .fch")].map(txt).join(" / "),
      /^Hypothesis\d+ \/ Validated\d+ \/ Designed\d+ \/ Ready for build\d+ \/ In build\d+ \/ Released\d+ \/ Operate & learn\d+$/);
    assert.equal(v.querySelectorAll(".fsteps .fstep").length, 7);
    assert.equal(v.querySelectorAll(".pyr .pyrow").length, 6);
    assert.equal(v.querySelectorAll(".roleg .rolec").length, 6);
    assert.equal(v.querySelectorAll("ul.ctrl li").length, 7);
  });

  it("lists the attendees with links to journeys and use cases", async () => {
    await bp.go("#/attendees");
    const v = bp.view();
    assert.equal(txt(v.querySelector("h2")), "Workshop attendees and their contributions");
    assert.equal(v.querySelectorAll(".person").length, 8);
    assert.ok(v.querySelectorAll(".person .linkp").length > 0);
  });

  it("shows the target architecture: landing zone, zones, lenses and ADRs", async () => {
    await bp.go("#/architecture");
    let v = bp.view();
    assert.deepEqual([...v.querySelectorAll(".atab")].map(txt), ["Landing zone", "Layers and integrations", "Flows", "Decisions (ADRs)"]);
    assert.equal(v.querySelectorAll("svg.lzsvg .lzhot").length, 20);
    assert.equal(v.querySelectorAll("svg.lzsvg .lzhot.zone").length, 4);
    await bp.click(v.querySelector("svg.lzsvg .lzhot.zone"));
    assert.ok(bp.view().querySelectorAll(".lzpanel .agchip").length > 0, "a zone lists its agents");
    const lens = [...bp.view().querySelectorAll(".lzlb")].find((b) => txt(b) === "Security");
    lens.click();
    await wait(30);
    v = bp.view();
    assert.ok(v.querySelectorAll("svg.lzsvg .lzhot.on").length > 0 && v.querySelectorAll("svg.lzsvg .lzhot.off").length > 0);
    [...v.querySelectorAll(".atab")].find((b) => /Decisions/.test(txt(b))).click();
    await wait(30);
    assert.equal(bp.view().querySelectorAll(".adr").length, 9);
    [...bp.view().querySelectorAll(".atab")].find((b) => /Layers/.test(txt(b))).click();
    await wait(30);
    assert.equal(bp.view().querySelectorAll(".layer").length, 9);
  });

  it("opens a use case detail page by deep link", async () => {
    await bp.go("#/usecases/UC09");
    const v = bp.view();
    assert.ok(v.querySelector("#ucdetail"));
    assert.equal(txt(v.querySelector(".uchead h2")), "Voice-to-service report");
    assert.deepEqual([...v.querySelectorAll(".ucs .bar")].map(txt), ["General", "Value", "Feasibility"]);
    assert.ok(v.querySelector("#ucdetail .valbox"), "workshop validation box");
  });

  it("records an IT readiness verdict in the workshop notes", async () => {
    await bp.go("#/readiness");
    const v = bp.view();
    assert.equal(txt(v.querySelector("h2")), "IT readiness: prepare discovery and design");
    assert.equal(v.querySelectorAll("details.rgroup").length, 6);
    v.querySelector('details.rgroup .assbox input[value="done"]').click();
    await wait(20);
    assert.ok(Object.keys(bp.notes()).some((k) => k.startsWith("val|ready|")), "readiness verdict saved");
  });

  it("navigates with the arrow keys", async () => {
    await bp.go("#/evidence");
    const before = bp.window.location.hash;
    bp.doc.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "ArrowLeft", bubbles: true }));
    await wait(40);
    assert.notEqual(bp.window.location.hash, before);
    assert.deepEqual(bp.errors, []);
  });
});
