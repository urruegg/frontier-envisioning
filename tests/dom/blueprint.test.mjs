// DOM tests of the Frontier Company Blueprint (Caldova demo): views, navigation, Hub journey pages, notes.
// Run: python tools/dev.py dom   (or: node --test tests/dom/blueprint.test.mjs with BLUEPRINT_HTML set)
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { openBlueprint, txt, wait } from "./helpers.mjs";

const VIEWS = ["Overview", "Org model", "Blueprint", "Journeys", "Use cases", "PRD", "Agents", "Agent identity", "Target architecture",
  "Ontology", "IT readiness", "Roadmap", "Plan", "Attendees", "Discovery", "Risks", "Evidence"];

describe("Frontier Company Blueprint (Caldova demo)", () => {
  let bp;
  before(async () => { bp = await openBlueprint(); });
  after(async () => { await bp.close(); });

  it("lists the 17 views of the Innovation Hub journey in order", () => {
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

  it("explains the digital feedback loop on the Overview: four areas around Microsoft IQ", async () => {
    await bp.go("#/overview");
    const v = bp.view();
    assert.match(txt(v.querySelector("#feedback-loop")), /^Digital feedback loop: signals, actions and outcomes/);
    const svg = v.querySelector("svg.flsvg");
    assert.ok(svg, "loop diagram");
    assert.deepEqual([...svg.querySelectorAll(".flq .fleyb")].map(txt),
      ["ENGAGE CUSTOMERS", "OPTIMIZE OPERATIONS", "EMPOWER EMPLOYEES", "TRANSFORM PRODUCTS"]);
    assert.deepEqual([...svg.querySelectorAll(".flchip text")].map(txt), ["Work IQ", "Fabric IQ", "Foundry IQ", "Web IQ"]);
    assert.equal(svg.querySelectorAll("animateMotion").length, 16, "signals, actions and outcomes are animated");
    assert.equal([...svg.querySelectorAll(".flapprt")].map(txt).join(" "), "Human approval before every action");
    // only official Microsoft IQ names anywhere in the loop
    const names = (txt(v.querySelector("#flwrap")) + " " + txt(v.querySelector(".fliqrow")) + " " + txt(v.querySelector("#flpanel"))).match(/\b[A-Z][a-z]+ IQ\b/g) || [];
    assert.deepEqual([...new Set(names)].filter((n) => !["Microsoft IQ", "Work IQ", "Fabric IQ", "Foundry IQ", "Web IQ"].includes(n)), []);
    // the panel follows the selected area; the IQ layers it does not use are dimmed
    assert.match(txt(v.querySelector("#flpanel h3")), /Answer every lead within a day/);
    await bp.click(svg.querySelector('.flq[data-q="2"]'));
    assert.equal(txt(v.querySelector("#flpanel h3")), "Every technician fully informed");
    assert.deepEqual([...svg.querySelectorAll(".flchip.off")].map((c) => c.getAttribute("data-iq")), ["web"]);
    assert.ok(v.querySelectorAll("#flpanel .agchip").length >= 2, "actions name their agents");
    assert.ok(v.querySelectorAll("#flpanel .flassi").length >= 2, "outcomes carry the value hypotheses");
    // the animation can be paused; a workshop verdict is kept with the notes
    const btn = v.querySelector(".flbtn");
    assert.match(txt(btn), /Pause animation/);
    await bp.click(btn);
    assert.match(txt(btn), /Play animation/);
    assert.ok(v.querySelector("#flwrap").classList.contains("paused"));
    v.querySelector('#flpanel .valbox input[value="validated"]').click();
    await wait(20);
    assert.ok(Object.keys(bp.notes()).includes("val|loop|empower_employees"), "loop verdict saved");
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

  it("keeps sticky navigation in a bounded summary before the full-width workflow", async () => {
    await bp.go("#/agents/D3-A05");
    const v = bp.view();
    const top = v.querySelector(".agtop");
    const list = v.querySelector(".alist");
    const flow = v.querySelector(".agfull");
    assert.ok(top, "upper summary containing block");
    assert.equal(list.parentElement, top);
    assert.ok(top.querySelector(".canvas"), "summary and trigger canvas share the navigation boundary");
    assert.equal(top.contains(flow), false);
    assert.equal(top.nextElementSibling, flow, "workflow occupies the next full-width row");
  });

  it("draws the agent workflow like the Copilot Studio designer: trigger, nodes, branches, outcome", async () => {
    await bp.go("#/agents/D3-A05");
    let v = bp.view();
    assert.equal(txt(v.querySelector("#workflow")), "Workflow \u00b7 from trigger to outcome");
    assert.match(txt(v.querySelector(".wfbar")), /^Service report from voice notes ?Draft ?3 AI ?8 deterministic ?2 human ?Copilot Studio workflow \u00b7 GitHub Copilot harness$/);
    assert.deepEqual([...v.querySelectorAll(".wfadd button")].map((b) => b.getAttribute("data-t")),
      ["agent", "classify", "extract", "copilot", "human_review", "connector", "function", "variable", "if_else", "loop", "note"]);
    let svg = v.querySelector("svg.wfsvg");
    const order = () => [...v.querySelectorAll("svg.wfsvg .wfn")].map((g) => g.getAttribute("data-t"));
    assert.deepEqual(order(), ["trigger", "variable", "connector", "loop", "connector", "extract", "agent", "function", "if_else",
      "human_review", "human_review", "connector", "end", "connector", "copilot", "outcome"], "nodes follow the flow (keyboard order)");
    assert.equal(svg.querySelector('.wfn[data-t="trigger"]').getAttribute("aria-label"), "Trigger: When a work order is completed on site (Connector event)");
    assert.deepEqual([...svg.querySelectorAll(".wfpt")].map(txt), ["Missing", "Complete", "Changes needed", "Confirmed"]);
    assert.equal(svg.querySelectorAll(".wfnote").length, 2);
    assert.ok(svg.querySelectorAll(".wfe").length >= 16, "edges connect every node");
    assert.ok(svg.querySelector('.wfn[data-t="agent"] image'), "the agent node shows the agent identity icon");
    // the properties panel opens on a node, closes with Escape or the close button
    const props = () => v.querySelector(".wfprops");
    assert.equal(props().hidden, true);
    await bp.click(svg.querySelector('.wfn[data-t="human_review"]'));
    assert.equal(props().hidden, false);
    assert.match(txt(props()), /^Ask the technician once ?Human review \u00b7 Human step/);
    assert.match(txt(props()), /Microsoft Teams/);
    v.querySelector("svg.wfsvg .wfn.sel").dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    await wait(20);
    assert.equal(props().hidden, true);
    v.querySelector('svg.wfsvg .wfn[data-t="trigger"]').dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    await wait(20);
    assert.match(txt(props()), /Trigger \u00b7 Connector event/);
    v.querySelector(".wfprops .wfx").click();
    await wait(10);
    assert.equal(props().hidden, true);
    // Add highlights a node type; the toolbar zooms and switches to the single designer row
    const hb = v.querySelector('.wfadd button[data-t="human_review"]');
    hb.click();
    await wait(10);
    assert.equal(hb.getAttribute("aria-pressed"), "true");
    assert.deepEqual([...v.querySelectorAll("svg.wfsvg .wfn:not(.dim)")].map((g) => g.getAttribute("data-t")), ["human_review", "human_review"]);
    hb.click();
    await wait(10);
    assert.equal(v.querySelectorAll("svg.wfsvg .wfn.dim").length, 0);
    const width = () => Number(v.querySelector("svg.wfsvg").getAttribute("width"));
    const w0 = width();
    v.querySelector('.wftools button[aria-label="Zoom in"]').click();
    await wait(10);
    assert.equal(txt(v.querySelector(".wfzl")), "115%");
    assert.ok(width() > w0);
    const lay = v.querySelector(".wflay");
    assert.equal(txt(lay), "Designer row");
    lay.click();
    await wait(20);
    assert.equal(txt(v.querySelector(".wflay")), "Overview");
    assert.ok(Number(v.querySelector("svg.wfsvg").getAttribute("height")) < 600, "one row with the branch lanes below");
    // the second MVP agent is called by an agent: Classify routes, If/Else escalates, the workflow responds to the agent
    await bp.go("#/agents/D2-A01");
    v = bp.view();
    svg = v.querySelector("svg.wfsvg");
    assert.equal(svg.querySelector('.wfn[data-t="trigger"]').getAttribute("aria-label"), "Trigger: When an agent calls the workflow");
    assert.deepEqual([...svg.querySelectorAll(".wfpt")].map(txt), ["Quote or sourcing", "Catalogue", "Frame contract", "Above limit", "Within limit", "Confirmed"]);
    assert.deepEqual([...svg.querySelectorAll('.wfn[data-t="end"]')].map((g) => g.getAttribute("aria-label")), ["End: Buyer takes over"]);
    assert.ok(svg.querySelector('.wfn[data-t="respond"]'), "Respond to the agent");
    // an agent without a canvas plan has no workflow yet
    await bp.go("#/agents/D1-A03");
    assert.match(txt(bp.view().querySelector(".agfull")), /No workflow yet/);
    assert.deepEqual(bp.errors, []);
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
    assert.equal(v.querySelectorAll("details.rgroup").length, 7, "includes the reviewed ontology readiness group");
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
