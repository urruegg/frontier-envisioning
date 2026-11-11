// DOM tests of the agent identity page, the identity icons across views, the business value and FinOps.
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { openBlueprint, PREVIEW_HTML, acknowledgePreview, txt, wait } from "./helpers.mjs";

describe("Agent identity, business value and FinOps (Caldova demo)", () => {
  let bp;
  before(async () => { bp = await openBlueprint(); });
  after(async () => { await bp.close(); });

  it("shows the agent identity page for all 33 agents without validation errors", async () => {
    await bp.go("#/identity");
    const v = bp.view();
    assert.equal(v.querySelector(".empty"), null);
    const headings = [...v.querySelectorAll("h3.sub")].map(txt);
    for (const h of ["Naming rule", "Journey colours", "Agent family", "All names per environment", "Decisions to confirm"]) {
      assert.ok(headings.includes(h), `section ${h}`);
    }
    assert.equal(txt(v.querySelector(".rulebox code")), "<PO> <Domain> [<Scope>] [DEV | TEST]");
    assert.equal(v.querySelectorAll(".fitem").length, 33);
    assert.equal(v.querySelectorAll(".fitem img.aicon").length, 33);
    assert.equal(v.querySelectorAll("table.idt tbody tr").length, 33);
    assert.equal(v.querySelectorAll("table.idt .pill.int").length, 0, "no name too long for Microsoft 365");
    assert.match(txt(v.querySelector(".idstrip")), /33 agents.*0 errors · 0 warnings/);
  });

  it("uses the identity icons wherever agents appear", async () => {
    const counts = {};
    for (const [hash, label] of [["#/org", "org"], ["#/usecases", "usecases"], ["#/agents/D3-A05", "agents"]]) {
      await bp.go(hash);
      counts[label] = bp.view().querySelectorAll("img.aicon").length;
    }
    assert.ok(counts.org >= 29, `org model icons ${counts.org}`);
    assert.ok(counts.usecases >= 15, `use case icons ${counts.usecases}`);
    assert.ok(counts.agents >= 1, `agent canvas icons ${counts.agents}`);
    assert.ok(bp.view().querySelector(".idpanel"), "identity panel on the agent canvas");
  });

  it("shows the business value in the use cases and records an assumption verdict", async () => {
    await bp.go("#/usecases");
    const v = bp.view();
    assert.equal(v.querySelectorAll("svg.matrix g.bub").length, 16);
    assert.ok(v.querySelector(".mxlegend"), "matrix legend");
    assert.equal(v.querySelectorAll("table.asst tbody tr").length, 21);
    const box = v.querySelector("table.asst .assbox");
    box.querySelector('input[value="adjusted"]').click();
    const input = box.querySelector("input.assval");
    input.value = "12";
    input.dispatchEvent(new bp.window.Event("input", { bubbles: true }));
    await wait(20);
    const verdicts = Object.entries(bp.notes()).filter(([k]) => k.startsWith("val|ass|"));
    assert.ok(verdicts.some(([, x]) => x.status === "adjusted" && String(x.value) === "12"), "assumption verdict saved");
  });

  it("shows the FinOps page with cost per agent, purchase options and guardrails", async () => {
    const preview = await openBlueprint(PREVIEW_HTML);
    try {
      await preview.go("#/finops");
      await acknowledgePreview(preview);
      const v = preview.view();
      assert.equal(txt(v.querySelector("h2")), "FinOps · what the agents cost");
      const subs = [...v.querySelectorAll("h3.sub")].map(txt);
      for (const s of ["Cost per agent and month", "Purchase options for the credits", "Guardrails", "Cost assumptions to clarify in the workshop"]) {
        assert.ok(subs.includes(s), `section ${s}`);
      }
      assert.equal(v.querySelectorAll(".tscroll")[0].querySelectorAll("tbody tr").length, 2, "two modelled agents");
      assert.equal(v.querySelector(".empty"), null);
      assert.deepEqual(preview.errors, []);
    } finally { await preview.close(); }
  });
});
