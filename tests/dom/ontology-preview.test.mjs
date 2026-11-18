import { it } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { openBlueprint, DEFAULT_HTML, PREVIEW_HTML, acknowledgePreview, txt, wait } from "./helpers.mjs";

const NOTICE = "Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.";
const CORE = ["overview", "org", "blueprint", "journeys", "usecases", "prd", "agents", "identity",
  "architecture", "ontology", "readiness", "roadmap", "plan", "attendees", "discovery", "risks", "evidence"];
const routes = (bp) => [...bp.doc.querySelectorAll("#rail button")].map((n) => n.dataset.view);
const uses = (data) => data.domains.flatMap((d) => d.use_cases || []);

it("D3 core and Preview expose exact route identities, and sparse ontology is unavailable", async () => {
  for (const [file, expected] of [[undefined, CORE], [PREVIEW_HTML, [...CORE.slice(0, 13), "finops", ...CORE.slice(13)]]]) {
    const bp = await openBlueprint(file);
    try { assert.deepEqual(routes(bp), expected); } finally { await bp.close(); }
  }
  for (const ontology of [undefined, {}, { entity_types: [] }, { entity_types: [null, {}] }]) {
    const bp = await openBlueprint(undefined, { change: (data) => { data.ontology = ontology; } });
    try {
      assert.ok(!routes(bp).includes("ontology"));
      await bp.go("#/ontology");
      assert.notEqual(txt(bp.doc.querySelector("#crumb b")), "Ontology");
      assert.deepEqual(bp.errors, []);
    } finally { await bp.close(); }
  }
});

it("D3 ontology has actual entities, mapping checks, governance, provider warnings and stable feedback", async () => {
  const bp = await openBlueprint();
  try {
    await bp.go("#/ontology");
    assert.equal(bp.view().querySelectorAll(".onode").length, 27);
    assert.equal(bp.view().querySelectorAll(".oedge").length, 33);
    assert.equal(bp.view().querySelectorAll(".ocdm tbody tr").length, 27);
    assert.equal(bp.view().querySelectorAll(".ocdm .mapping-gap").length, 6);
    assert.equal(bp.view().querySelectorAll(".oproduct").length, 19);
    assert.ok(bp.view().querySelectorAll("details.ontsection").length >= 10, "large design sections are keyboard-expandable rather than all expanded");
    for (const term of ["Preview", "manual", "Bronze", "Silver", "Gold", "Data agents", "Operations agents", "Rules", "Metrics", "Readiness"]) assert.ok(txt(bp.view()).includes(term), term);
    const node = bp.view().querySelector('.onode[data-entity="Employee"]');
    node.focus();
    node.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
    await wait(20);
    assert.equal(bp.doc.activeElement.getAttribute("data-entity"), "Employee");
    assert.equal(bp.view().querySelector("#opanel").dataset.entity, "Employee");
    assert.match(txt(bp.view().querySelector("#opanel")), /[Nn]ot bound|[Tt]o bind/);
    const textarea = bp.view().querySelector("#v-onto-Employee-note");
    textarea.value = "Verify Employee binding ✓";
    textarea.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    assert.equal(bp.notes()["val|onto|Employee"].note, "Verify Employee binding ✓");
    await bp.go("#/overview"); await bp.go("#/ontology");
    assert.equal(bp.view().querySelector("#v-onto-Employee-note").value, "Verify Employee binding ✓");
    const filter = bp.view().querySelector("#ontology-journey-D2");
    filter.focus(); filter.click(); await wait(20);
    assert.equal(bp.doc.activeElement.id, filter.id);
    assert.equal(bp.view().querySelector("#ontology-journey-D2").getAttribute("aria-pressed"), "true");
    const visible = [...bp.view().querySelectorAll(".onode")].map((n) => n.dataset.entity);
    assert.ok(visible.length < 27 && visible.length > 0);
    const selected = bp.view().querySelector("#opanel");
    assert.ok(!selected || visible.includes(selected.dataset.entity), "filtered selection cannot stay hidden");
    await bp.go("#/discovery");
    let copied = ""; bp.window.navigator.clipboard.writeText = async (text) => { copied = text; };
    [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Copy notes as text").click();
    await wait(20);
    assert.match(copied, /Ontology Employee.*Verify Employee binding ✓/);
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("D3 ontology exports Python-identical Turtle and semantic Markdown without opaque notes", async () => {
  const bp = await openBlueprint(undefined, { change(data) {
    data.ontology.internal_notes = { secret: "OPAQUE-SECRET" };
  } });
  try {
    await bp.go("#/ontology");
    const downloads = [];
    bp.window.URL.createObjectURL = (blob) => { downloads.push(blob); return "blob:test"; };
    bp.doc.addEventListener("click", (e) => { if (e.target.closest("a[download]")) e.preventDefault(); });
    for (const name of ["Download ontology.ttl", "Download ontology.md", "Download data-agents.md", "Download data-products.md"]) {
      const b = [...bp.view().querySelectorAll("button")].find((b) => txt(b) === name);
      assert.ok(b, name); b.click();
    }
    const texts = await Promise.all(downloads.map((b) => b.text()));
    assert.equal(texts[0], fs.readFileSync(path.join(path.dirname(process.env.BLUEPRINT_HTML || DEFAULT_HTML), "ontology", "ontology.ttl"), "utf8"));
    for (const token of ["customerId", "accountnumber", "core_silver.customer", "to verify", "Rules", "Metrics"]) assert.ok(texts[1].includes(token), token);
    for (const token of ["DA-01", "instructions", "questions", "sources"]) assert.ok(texts[2].includes(token), token);
    for (const token of ["DP-01", "quality", "access", "commitment"]) assert.ok(texts[3].includes(token), token);
    assert.ok(texts[1].includes("**internal**: true"), "source restrictions remain attached to internal design records");
    for (const text of texts) assert.ok(!text.includes("OPAQUE-SECRET") && !text.includes("internal_notes"));
  } finally { await bp.close(); }
});

it("D3 imported Preview costs and derived PRD/value figures require transient acknowledgement on every load", async () => {
  const bp = await openBlueprint(PREVIEW_HTML);
  try {
    for (const route of ["finops", "usecases/UC09", "prd", "usecases"]) {
      await bp.go("#/" + route);
      assert.ok(txt(bp.view()).includes(NOTICE), route);
      assert.doesNotMatch(txt(bp.view()), /CHF 177|CHF 17,708|ROI 545%|NPV CHF 838k|1516%/);
    }
    await bp.go("#/finops");
    assert.equal(bp.view().querySelectorAll(".vkpis").length, 0);
    await acknowledgePreview(bp);
    assert.ok(txt(bp.view()).includes(NOTICE));
    assert.match(txt(bp.view()), /CHF 17,708/);
    assert.match(txt(bp.view()), /[Pp]rovisional comparisons.*not recommendations/);
    await bp.go("#/prd");
    assert.match(txt(bp.view()), /ROI 545%/);
    assert.match(txt(bp.view()), /[Pp]rovisional/);
    assert.ok(Object.values(bp.notes()).every((n) => !JSON.stringify(n).includes("acknowledg")));
    const reload = await openBlueprint(PREVIEW_HTML, { storage: { ...bp.window.localStorage } });
    try { await reload.go("#/finops"); assert.equal(reload.view().querySelectorAll(".vkpis").length, 0); } finally { await reload.close(); }
  } finally { await bp.close(); }
});

it("D3 legacy forged GA/cached technical metadata never acknowledges; independent GA value is usable", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change(data) {
    data.finops.finops_preview = { maturity: "ga", acknowledgement: { kind: "human", scope: "forever" } };
    delete data.value_case.finops_preview;
    uses(data).forEach((u) => { if (u.business_value) delete u.business_value.finops_preview; });
  }, storage: { finopsAcknowledged: "true" } });
  try {
    await bp.go("#/prd"); assert.ok(txt(bp.view()).includes(NOTICE));
    assert.doesNotMatch(txt(bp.view()), /ROI 545%/);
  } finally { await bp.close(); }
  const core = await openBlueprint();
  try {
    await core.go("#/usecases");
    assert.ok(!txt(core.view()).includes(NOTICE));
    assert.match(txt(core.view()), /CHF 8.21M/);
    await core.go("#/prd");
    assert.ok(!core.view().querySelector("#finops-preview-ack"));
  } finally { await core.close(); }
});

it("D3 unavailable totals/ranking are not presented as zero or recovered from internal notes", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change(data) {
    delete data.finops.totals;
    data.finops.internal_notes = { totals: { total_month: 999777 }, marker: "OPAQUE-COST" };
    data.finops.purchase_options.forEach((o) => { delete o.lowest; delete o.vs_payg; });
    data.finops.agents.forEach((a) => { delete a.sessions; delete a.credits_month; delete a.unit; });
  } });
  try {
    await bp.go("#/finops"); await acknowledgePreview(bp);
    assert.equal(txt(bp.view().querySelector(".vkpis .vkpi b")), "To be confirmed");
    assert.doesNotMatch(txt(bp.view()), /999777|999,777|OPAQUE-COST|NaN|undefined/);
    assert.ok(!txt(bp.view()).includes("Lowest credit option"));
    for (const row of bp.view().querySelectorAll(".finops-agents tbody tr")) {
      assert.equal(txt(row.children[2]).startsWith("To be confirmed"), true);
    }
  } finally { await bp.close(); }
});

it("D3 detached Preview-derived value provenance gates portfolio totals even without a FinOps block", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change(data) {
    delete data.finops;
    uses(data).forEach((u) => { if (u.business_value) delete u.business_value.finops_preview; });
  } });
  try {
    await bp.go("#/usecases");
    assert.ok(txt(bp.view()).includes(NOTICE));
    assert.doesNotMatch(txt(bp.view().querySelector(".vkpis")), /7.61M|284,986|212k|150k/);
    await bp.go("#/prd");
    assert.doesNotMatch(txt(bp.view()), /ROI 545%|NPV CHF 838k/);
    await bp.go("#/usecases");
    await acknowledgePreview(bp);
    assert.match(txt(bp.view().querySelector(".vkpis")), /7.61M/);
  } finally { await bp.close(); }
});

it("D3 ontology preserves UTF-8/escaping with Python parity, opaque-note privacy and unknown feedback", async () => {
  let data;
  const seed = await openBlueprint();
  data = JSON.parse(seed.doc.getElementById("bp-data").textContent);
  await seed.close();
  const key = "fbp:" + (data.meta.id || data.meta.customer || "blueprint") + ":" + (data.meta.version || "0");
  const text = 'Café "quoted" \\ line\n第二行 <img src=x onerror=alert(1)>';
  const bp = await openBlueprint(undefined, { storage: { [key]: JSON.stringify({ "val|onto|UNKNOWN-ENTITY": { status: "adjusted", note: "Keep for review ✓" } }) },
    change(data) {
      data.ontology.entity_types[0].description = text;
      data.ontology.data_agents[0].instructions = text;
      data.ontology.data_products[0].quality = text;
      data.ontology.data_products[0].internal_notes = { secret: "DO-NOT-RECOVER" };
    } });
  try {
    await bp.go("#/ontology");
    assert.match(txt(bp.view()), /Unknown ontology feedback IDs retained for review: UNKNOWN-ENTITY/);
    assert.equal(bp.view().querySelectorAll('img[src="x"]').length, 0);
    const ontology = JSON.parse(bp.doc.getElementById("bp-data").textContent).ontology;
    const python = spawnSync(process.platform === "win32" ? "python" : "python3", ["-c",
      "import json,sys;sys.path.insert(0,'plugin/skills/frontier-process/scripts');from ontology_lib import to_turtle;sys.stdout.buffer.write(to_turtle(json.load(sys.stdin)).encode('utf-8'))"],
    { input: JSON.stringify(ontology), encoding: "utf8" });
    assert.equal(python.status, 0, python.stderr);
    const downloads = [];
    bp.window.URL.createObjectURL = (blob) => { downloads.push(blob); return "blob:test"; };
    bp.doc.addEventListener("click", (e) => { if (e.target.closest("a[download]")) e.preventDefault(); });
    for (const name of ["ontology.ttl", "ontology.md", "data-agents.md", "data-products.md"]) {
      [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download " + name).click();
    }
    const exports = await Promise.all(downloads.map((b) => b.text()));
    assert.equal(exports[0], python.stdout);
    for (const output of exports.slice(1)) {
      assert.match(output, /Café/); assert.match(output, /第二行/);
      assert.ok(output.includes("&lt;img"));
      assert.ok(!output.includes("DO-NOT-RECOVER") && !output.includes("<img"));
    }
    await bp.go("#/discovery");
    const blobs = downloads.length;
    [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Export workshop feedback (JSON)").click();
    const feedback = JSON.parse(await downloads[blobs].text());
    assert.equal(feedback.validations["onto:UNKNOWN-ENTITY"].note, "Keep for review ✓");
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

function inverseDetachment(data, mixed = false) {
  delete data.finops;
  delete data.value_case.finops_preview;
  if (mixed) {
    const publicValue = uses(data).find((u) => u.id === "UC05").business_value;
    delete publicValue.finops_preview;
    publicValue.npv = 777123;
    publicValue.roi = 0.777;
  }
}
function linkedCostAssumption(data, detached = false) {
  const cost = data.finops.assumptions.find((a) => a.id === "ASS-114");
  cost.statement = "Build effort, source figure 90,000 CHF";
  if (detached) cost.finops_preview = { maturity: "ga", acknowledgement: { kind: "cached" } };
  data.value_case.assumptions.push(structuredClone(cost), {
    id: "ASS-PUBLIC", statement: "Independent user amount", unit: "CHF", base: 424242,
    low: 400000, high: 450000, source_type: "customer", src: ["E04"], status: "open"
  });
  uses(data).find((u) => u.id === "UC05").business_value.assumptions.push("ASS-114", "ASS-PUBLIC");
  data.feedback_loop.quadrants[0].outcomes.push({ text: "Linked assumptions", assumptions: ["ASS-114", "ASS-PUBLIC"] });
  if (detached) {
    delete data.finops;
    delete data.value_case.finops_preview;
    uses(data).forEach((u) => { if (u.business_value) delete u.business_value.finops_preview; });
  }
}
function costRow(bp) {
  return [...bp.view().querySelectorAll(".assrow")].find((row) => txt(row.querySelector("b")) === "ASS-114");
}
function downloadsFor(bp) {
  const blobs = [];
  bp.window.URL.createObjectURL = (blob) => { blobs.push(blob); return "blob:test"; };
  bp.doc.addEventListener("click", (e) => { if (e.target.closest("a[download]")) e.preventDefault(); });
  return blobs;
}

// Exercise the reviewed consumer contract, not a JS imitation of owner validation
// or customer projection. Turtle expectations come from this same process library.
function g59Change(data, variant) {
  const o = data.ontology, sap = o.sources.find((s) => s.id === "src-sap-s-4hana");
  if (variant !== "legacy") {
    Object.assign(sap, { path: "unresolved", item: null, status: "later" });
    for (const e of o.entity_types.filter((e) => e.source === sap.id)) {
      e.binding = { layer: "silver", item: null, table: null, origin: "default" };
    }
  }
  if (variant === "legacy") {
    o.entity_types.find((e) => e.id === "Product").binding.table = "recorded.product";
    o.domains.push({ id: "saved-domain", name: "Saved public grouping", owner: "Synthetic governance owner",
      governance_domain: "Functional unit", note: "Recorded domain choice", src: ["G59-P6"] });
    o.build_steps.push({ id: "saved-step", text: "Create a Purview functional unit (saved choice)", src: ["S38"] });
  }
  if (variant === "selected") {
    Object.assign(sap, { path: "mirroring", item: "mirrored database", owner: "Synthetic SAP data owner" });
    for (const [i, record] of Object.values(sap.route_assessment.prerequisites).entries()) {
      Object.assign(record, { status: "confirmed", note: "Synthetic offline owner assertion", src: ["ESTATE-G59-" + i] });
      data.evidence.push({ id: "ESTATE-G59-" + i, type: "estate", title: "Synthetic owner record" });
    }
    o.entity_types.find((e) => e.id === "Product").binding =
      { layer: "silver", item: "lakehouse", table: "selected.product" };
  }
  o.domains.push({ id: "private-g59", name: "PRIVATE-G59-NOTE", internal: true, src: ["G59-P6"] });
  const python = spawnSync(process.platform === "win32" ? "python" : "python3", ["-c",
    "import json,sys;sys.path.insert(0,'plugin/skills/frontier-process/scripts');import ontology_lib as lib;bp=json.load(sys.stdin);rep=lib.Rep();o=lib.normalize(bp['ontology'],bp,rep);assert not rep.errors,rep.errors;o=lib.customer_ontology(o,bp) if sys.argv[1]=='projected' else o;print(json.dumps(o))",
    variant], { input: JSON.stringify(data), encoding: "utf8", maxBuffer: 8 * 1024 * 1024 });
  assert.equal(python.status, 0, python.stderr);
  data.ontology = JSON.parse(python.stdout);
  if (variant === "empty-refs") {
    for (const g of Object.values(data.ontology.current_guidance)) g.src = [];
    data.ontology.current_guidance.governance.text += ' Café <img src=x onerror="alert(1)">';
  }
  if (variant === "no-current") {
    delete data.ontology.current_guidance;
    delete data.ontology.current_readiness;
    // This compatibility fixture predates additive fields but explicitly has
    // an unresolved route. No SAP-name heuristic may manufacture support.
    delete data.ontology.sources.find((s) => s.id === sap.id).route_assessment;
  }
}

it("G59 current and legacy grounding remain distinct", async (t) => {
  for (const variant of ["unknown", "legacy", "selected", "no-current", "empty-refs"]) {
    await t.test(variant, async () => {
      const bp = await openBlueprint(undefined, { change: (data) => g59Change(data, variant) });
      try {
        await bp.go("#/ontology");
        assert.deepEqual(routes(bp), CORE);
        const node = bp.view().querySelector('.onode[data-entity="Product"]');
        assert.ok(!node.closest("details"), "graph stays available outside design disclosures");
        assert.ok(![...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download ontology.ttl").closest("details"));
        const conditional = variant !== "selected";
        assert.match(txt(node.querySelector(".osub")), conditional ? /conditional|to bind/i : /bound/);
        assert.equal(node.querySelector("rect").classList.contains("unbound"), conditional);
        node.focus();
        node.dispatchEvent(new bp.window.KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
        await wait(20);
        const panel = bp.view().querySelector("#opanel");
        assert.match(txt(panel), conditional ? /conditional|unresolved/i : /owner-asserted design selection/i);
        if (variant === "legacy") {
          assert.match(txt(panel), /[Rr]ecorded proposal.*recorded\.product/);
          assert.match(txt(bp.view()), /[Rr]ecorded choices/);
          assert.match(txt(bp.view()), /Saved public grouping.*Functional unit.*Recorded domain choice/);
        } else if (conditional) {
          assert.match(txt(panel), /[Nn]o selected table|[Nn]ot bound/);
          assert.doesNotMatch(txt(panel), /core_silver\.product/);
        } else {
          assert.match(txt(panel), /selected\.product/);
          assert.match(txt(panel), /not tenant verification/i);
        }
        const alarm = bp.view().querySelector('.onode[data-entity="AlarmEvent"] .osub');
        assert.match(txt(alarm), /\bbound\b/, "independent eventhouse remains bound");
        if (variant !== "no-current") {
          assert.match(txt(bp.view()), /OneLake catalog.*Fabric domains.*not an ACL/);
          assert.match(txt(bp.view()), /SAP Datasphere -> ADLS Gen2 -> Fabric\/OneLake/);
          assert.ok(bp.view().querySelectorAll(".ev").length > 0);
        }
        assert.equal(bp.view().querySelectorAll('img[src="x"]').length, 0);
        assert.doesNotMatch(txt(bp.view()), /\bundefined\b|\bNone\b.*selected|mounted-confirmed/);
        assert.deepEqual(bp.errors, []);
      } finally { await bp.close(); }
    });
  }
});

it("G59 conditional route downloads retain guidance and Turtle parity", async (t) => {
  for (const variant of ["unknown", "legacy", "selected", "projected", "empty-refs"]) {
    await t.test(variant, async () => {
      const bp = await openBlueprint(undefined, { change: (data) => g59Change(data, variant) });
      try {
        await bp.go("#/ontology");
        const o = JSON.parse(bp.doc.getElementById("bp-data").textContent).ontology;
        const python = spawnSync(process.platform === "win32" ? "python" : "python3", ["-c",
          "import json,sys;sys.path.insert(0,'plugin/skills/frontier-process/scripts');from ontology_lib import to_turtle;sys.stdout.buffer.write(to_turtle(json.load(sys.stdin)).encode('utf-8'))"],
        { input: JSON.stringify(o), encoding: "utf8" });
        assert.equal(python.status, 0, python.stderr);
        const blobs = downloadsFor(bp);
        for (const name of ["ontology.ttl", "ontology.md", "data-agents.md", "data-products.md"]) {
          [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download " + name).click();
        }
        assert.equal(await blobs[0].text(), python.stdout);
        for (const blob of blobs.slice(1)) {
          const text = await blob.text();
          for (const token of ["Current guidance", "Recorded choices", "OneLake catalog", "not an ACL",
            "sensitivity labels and DLP", "SAP Datasphere", "ADLS Gen2", "snapshot", "Delta tables",
            "read-only SQL replica", "unpriced / to confirm", "G59-P3", "G59-P6", "source route src-sap-ariba: conditional"]) {
            assert.ok(text.includes(token), token);
          }
          assert.doesNotMatch(text, /\bundefined\b|\bNone\b|\bnull\b|mounted-confirmed/);
          if (variant === "legacy") {
            assert.match(text, /[Rr]ecorded proposal \(conditional\).*recorded\.product/);
          }
          if (variant === "selected") assert.match(text, /owner-asserted design selection/i);
          if (variant === "projected") assert.ok(!text.includes("PRIVATE-G59-NOTE"));
          if (variant === "empty-refs") {
            assert.ok(text.includes("Café &lt;img"));
            assert.ok(!text.includes("<img"));
          }
        }
        if (variant === "projected") assert.ok(!txt(bp.view()).includes("PRIVATE-G59-NOTE"));
        assert.deepEqual(bp.errors, []);
      } finally { await bp.close(); }
    });
  }
});

it("D3 review inverse-detachment gates aggregate costs, NPV, ranking and sensitivity from contributing cases", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change: inverseDetachment });
  try {
    await bp.go("#/usecases");
    const kpis = txt(bp.view().querySelector(".vkpis"));
    assert.doesNotMatch(kpis, /212k|150k|7.61M/, "child provenance must reach aggregate financial fields");
    assert.match(kpis, /4.57M/, "public economic amounts are not suppressed");
    const rows = [...bp.view().querySelectorAll("table.asst tbody tr")];
    assert.ok(rows.every((r) => !txt(r.children[0]).includes("#") && txt(r.children[4]) === "To be confirmed"));
    assert.deepEqual(rows.map((r) => txt(r.querySelector("b"))), rows.map((r) => txt(r.querySelector("b"))).sort(), "no top-question subset or ranked order before acknowledgement");
    const blobs = downloadsFor(bp);
    await bp.go("#/prd");
    [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download the PRD (Markdown)").click();
    assert.doesNotMatch(await blobs[0].text(), /ROI 545%|NPV CHF 838k/);
    await bp.go("#/usecases");
    await acknowledgePreview(bp);
    assert.match(txt(bp.view().querySelector(".vkpis")), /212k.*150k.*7.61M/);
    assert.ok([...bp.view().querySelectorAll("table.asst tbody tr")].some((r) => txt(r.children[0]).includes("#") && txt(r.children[4]) !== "To be confirmed"));
    assert.ok(txt(bp.view()).includes(NOTICE));
    assert.deepEqual(bp.errors, []);
  } finally { await bp.close(); }
});

it("D3 review mixed/public contributors keep public case values without substituting a partial portfolio total", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change: (data) => inverseDetachment(data, true) });
  try {
    await bp.go("#/usecases");
    assert.doesNotMatch(txt(bp.view().querySelector(".vkpis")), /212k|150k|7.61M|777k/);
    assert.match(txt(bp.view()), /CHF 777k/, "the public case remains available");
    const blobs = downloadsFor(bp);
    await bp.go("#/prd");
    [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download the PRD (Markdown)").click();
    const md = await blobs[0].text();
    assert.match(md, /NPV CHF 777k/);
    assert.doesNotMatch(md, /NPV CHF 6.78M|ROI 1516%/);
    assert.ok(md.includes(NOTICE));
    await bp.go("#/usecases/UC05");
    assert.match(txt(bp.view().querySelector(".ucval")), /NPVCHF 777k/);
    await bp.go("#/usecases/UC09");
    assert.doesNotMatch(txt(bp.view().querySelector(".ucval")), /NPVCHF 6.78M/);
  } finally { await bp.close(); }
  const core = await openBlueprint();
  try {
    await core.go("#/usecases");
    assert.match(txt(core.view().querySelector(".vkpis")), /8.21M/);
    assert.ok([...core.view().querySelectorAll("table.asst tbody tr")].some((r) => txt(r.children[0]).includes("#")));
    assert.equal(core.doc.querySelector("#finops-preview-ack"), null);
  } finally { await core.close(); }
});

it("D3 review linked FinOps assumptions are withheld on cards, tables and feedback loop, not ordinary GA assumptions", async () => {
  for (const detached of [false, true]) {
    const bp = await openBlueprint(PREVIEW_HTML, { change: (data) => linkedCostAssumption(data, detached) });
    try {
      await bp.go("#/usecases/UC05");
      assert.doesNotMatch(txt(costRow(bp)), /90,000|60,000|130,000/);
      assert.equal(costRow(bp).querySelector(".assval"), null, "no numeric Preview input before acknowledgement");
      assert.ok(txt(bp.view()).includes("424,242 CHF"), "independent user assumption remains usable");
      await bp.go("#/overview");
      const cost = [...bp.view().querySelectorAll(".flassi")].find((n) => txt(n).includes("ASS-114"));
      assert.ok(cost);
      assert.doesNotMatch(txt(cost), /90,000|60,000|130,000/);
      assert.match(txt(bp.view().querySelector("#flpanel")), /424,242 CHF/);
      await bp.go("#/usecases");
      const row = [...bp.view().querySelectorAll("table.asst tbody tr")].find((r) => txt(r.querySelector("b")) === "ASS-114");
      assert.ok(row);
      assert.doesNotMatch(txt(row), /90,000|60,000|130,000/);
      await acknowledgePreview(bp);
      await bp.go("#/usecases/UC05");
      assert.match(txt(costRow(bp)), /90,000 CHF.*60,000 CHF.*130,000 CHF/);
      assert.ok(costRow(bp).querySelector(".assval"));
      assert.ok(txt(bp.view()).includes(NOTICE));
      await bp.go("#/overview");
      assert.match(txt(bp.view().querySelector("#flpanel")), /90,000 CHF/);
      assert.ok(txt(bp.view()).includes(NOTICE));
      assert.deepEqual(bp.errors, []);
    } finally { await bp.close(); }
  }
});

it("D3 review restored numeric Preview verdicts are gated in inputs and feedback exports while notes survive", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change: linkedCostAssumption });
  let storage;
  try {
    await bp.go("#/usecases/UC05"); await acknowledgePreview(bp);
    const row = costRow(bp), number = row.querySelector(".assval"), note = row.querySelector(".assnote");
    number.value = "90013";
    number.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    note.value = "Owner and source retained ✓"; note.focus();
    note.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    assert.equal(bp.doc.activeElement, note);
    storage = Object.fromEntries(Object.keys(bp.window.localStorage).map((k) => [k, bp.window.localStorage.getItem(k)]));
  } finally { await bp.close(); }
  const reload = await openBlueprint(PREVIEW_HTML, { change: linkedCostAssumption, storage });
  try {
    await reload.go("#/usecases/UC05");
    const inputExposed = !!costRow(reload).querySelector(".assval");
    assert.equal(costRow(reload).querySelector(".assnote").value, "Owner and source retained ✓");
    assert.equal(reload.notes()["val|ass|ASS-114"].value, 90013, "stored notes are not mutated by a presentation gate");
    const blobs = downloadsFor(reload);
    await reload.go("#/discovery");
    [...reload.view().querySelectorAll("button")].find((b) => txt(b) === "Export workshop feedback (JSON)").click();
    const feedback = JSON.parse(await blobs[0].text());
    let copied = "";
    reload.window.navigator.clipboard.writeText = async (text) => { copied = text; };
    [...reload.view().querySelectorAll("button")].find((b) => txt(b) === "Copy notes as text").click();
    await wait(20);
    assert.deepEqual({ inputExposed, jsonExposed: "value" in feedback.validations["ass:ASS-114"], textExposed: copied.includes("90013") },
      { inputExposed: false, jsonExposed: false, textExposed: false });
    assert.equal(feedback.validations["ass:ASS-114"].note, "Owner and source retained ✓");
    await acknowledgePreview(reload);
    [...reload.view().querySelectorAll("button")].find((b) => txt(b) === "Export workshop feedback (JSON)").click();
    assert.equal(JSON.parse(await blobs[1].text()).validations["ass:ASS-114"].value, 90013);
    await reload.go("#/usecases/UC05");
    assert.equal(costRow(reload).querySelector(".assval").value, "90013");
    assert.equal(costRow(reload).querySelector(".assnote").value, "Owner and source retained ✓");
    assert.ok(txt(reload.view()).includes(NOTICE));
  } finally { await reload.close(); }
});

const FINANCIAL_FIELDS = ["npv", "npv_budget", "roi", "payback_months", "cost_year", "build", "pv_cost", "break_even", "scenarios", "rank", "swing_npv"];
function nestCase(data, id = "UC05") {
  const value = uses(data).find((u) => u.id === id).business_value;
  const result = {};
  for (const key of [...FINANCIAL_FIELDS, "finops_preview"]) {
    if (key in value) { result[key] = value[key]; delete value[key]; }
  }
  value.results = result;
  return value;
}

it("D3 nested result marker gates actual PRD DOM and Blob bytes before ack and restores provisional figures after ack", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change(data) {
    delete data.finops; delete data.value_case.finops_preview;
    const value = nestCase(data);
    value.results.finops_preview = { maturity: "ga", acknowledgement: { kind: "cached-human", scope: "forever" } };
  } });
  let storage;
  try {
    const blobs = downloadsFor(bp);
    await bp.go("#/prd");
    [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download the PRD (Markdown)").click();
    const md = await blobs[0].text();
    assert.ok(txt(bp.view()).includes(NOTICE) && md.includes(NOTICE));
    assert.deepEqual({ domLeaks: /NPV CHF 838k|ROI 545%|payback 4.6 months/.test(txt(bp.view())),
      blobLeaks: /NPV CHF 838k|ROI 545%|payback 4.6 months/.test(md) }, { domLeaks: false, blobLeaks: false });
    await acknowledgePreview(bp);
    [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download the PRD (Markdown)").click();
    for (const text of [txt(bp.view()), await blobs[1].text()]) {
      assert.match(text, /NPV CHF 838k.*ROI 545%.*payback 4.6 months/);
      assert.ok(text.includes(NOTICE) && /[Pp]rovisional/.test(text));
    }
    await bp.go("#/usecases/UC05");
    assert.match(txt(bp.view().querySelector(".ucval")), /NPVCHF 838k.*ROI 545%/);
    storage = Object.fromEntries(Object.keys(bp.window.localStorage).map((k) => [k, bp.window.localStorage.getItem(k)]));
  } finally { await bp.close(); }
  const reload = await openBlueprint(PREVIEW_HTML, { storage, change(data) {
    delete data.finops; delete data.value_case.finops_preview; nestCase(data);
  } });
  try {
    await reload.go("#/prd");
    assert.doesNotMatch(txt(reload.view()), /NPV CHF 838k|ROI 545%|payback 4.6 months/);
    assert.ok(reload.doc.querySelector("#finops-preview-ack"));
  } finally { await reload.close(); }
});

it("D3 nested sole contributor carries provenance into portfolio totals ranking and NPV effects", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change(data) {
    delete data.finops; delete data.value_case.finops_preview;
    uses(data).forEach((u) => { if (u.business_value && u.id !== "UC05") delete u.business_value.finops_preview; });
    nestCase(data);
  } });
  try {
    await bp.go("#/usecases");
    assert.ok(txt(bp.view()).includes(NOTICE));
    assert.doesNotMatch(txt(bp.view().querySelector(".vkpis")), /212k|150k|7.61M/);
    const rows = [...bp.view().querySelectorAll(".asst tbody tr")];
    assert.ok(rows.every((r) => !txt(r.children[0]).includes("#") && txt(r.children[4]) === "To be confirmed"));
    assert.match(txt(bp.view().querySelector(".vkpis")), /4.57M/);
    await acknowledgePreview(bp);
    assert.match(txt(bp.view().querySelector(".vkpis")), /7.61M/);
    assert.ok([...bp.view().querySelectorAll(".asst tbody tr")].some((r) => txt(r.children[0]).includes("#")));
  } finally { await bp.close(); }
});

it("D3 nested result assumption links use the same source selection and preserve Preview ancestry", async () => {
  const bp = await openBlueprint(PREVIEW_HTML, { change(data) {
    const cost = data.finops.assumptions.find((a) => a.id === "ASS-114");
    cost.finops_preview = { maturity: "ga", acknowledgement: { kind: "cached" } };
    data.value_case.assumptions.push(cost);
    delete data.finops; delete data.value_case.finops_preview;
    uses(data).forEach((u) => { if (u.business_value) delete u.business_value.finops_preview; });
    const value = nestCase(data);
    value.results.assumptions = ["ASS-114"];
  } });
  try {
    const blobs = downloadsFor(bp);
    await bp.go("#/prd");
    [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download the PRD (Markdown)").click();
    assert.doesNotMatch(await blobs[0].text(), /NPV CHF 838k|ROI 545%|payback 4.6 months/);
    await bp.go("#/usecases/UC05");
    const row = costRow(bp);
    assert.ok(row, "assumptions on the selected result are actually presented");
    assert.doesNotMatch(txt(row), /90,000|60,000|130,000/);
    assert.equal(row.querySelector(".assval"), null);
    await acknowledgePreview(bp);
    assert.match(txt(costRow(bp)), /90,000 CHF/);
    assert.match(txt(bp.view().querySelector(".ucval")), /NPVCHF 838k/);
  } finally { await bp.close(); }
});

it("D3 nested public results remain usable without ack and never fall back to stale outer financial fields", async () => {
  for (const mixed of [false, true]) {
    const bp = await openBlueprint(mixed ? PREVIEW_HTML : undefined, { change(data) {
      delete data.finops; delete data.value_case.finops_preview;
      const value = nestCase(data);
      delete value.results.finops_preview;
      value.results.npv = 777123; value.results.roi = 0.777; value.results.payback_months = 4.6;
      value.npv = 999999; // Stale cache, not the selected result.
    } });
    try {
      await bp.go("#/usecases/UC05");
      assert.match(txt(bp.view().querySelector(".ucval")), /NPVCHF 777k.*ROI 78%/);
      assert.doesNotMatch(txt(bp.view().querySelector(".ucval")), /999k|1.00M/);
      const blobs = downloadsFor(bp);
      await bp.go("#/prd");
      [...bp.view().querySelectorAll("button")].find((b) => txt(b) === "Download the PRD (Markdown)").click();
      assert.match(await blobs[0].text(), /NPV CHF 777k.*ROI 78%.*payback 4.6 months/);
      assert.equal(!!bp.doc.querySelector("#finops-preview-ack"), mixed);
      assert.deepEqual(bp.errors, []);
    } finally { await bp.close(); }
  }
  const partial = await openBlueprint(undefined, { change(data) {
    const value = nestCase(data);
    value.npv = 999999; value.payback_months = 4.6;
    value.results = { roi: 0.777 }; // Missing result amounts are unavailable, not cached values or zero.
  } });
  try {
    await partial.go("#/usecases/UC05");
    assert.match(txt(partial.view().querySelector(".ucval")), /NPVTo be confirmed.*ROI 78%/);
    assert.doesNotMatch(txt(partial.view().querySelector(".ucval")), /NPVCHF|Payback4.6/);
    await partial.go("#/prd");
    const item = [...partial.view().querySelectorAll("ul.clean > li")].find((li) => txt(li).includes("UC05") && txt(li).includes("ROI"));
    assert.ok(item);
    assert.doesNotMatch(txt(item), /NPV CHF|payback/);
  } finally { await partial.close(); }
});
