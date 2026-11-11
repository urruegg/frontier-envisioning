import { test, expect } from "@playwright/test";
import fs from "node:fs";
import axe from "axe-core";

const NOTICE = "Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.";
async function bytes(page, name) {
  const event = page.waitForEvent("download");
  await page.getByRole("button", { name, exact: true }).click();
  const download = await event, chunks = [];
  for await (const chunk of await download.createReadStream()) chunks.push(chunk);
  return Buffer.concat(chunks);
}
async function open(page, url) {
  await page.goto("about:blank");
  const response = await page.goto(url);
  expect(response.headers()["content-security-policy"]).toContain("default-src 'none'");
  expect(response.headers()["content-security-policy"]).toMatch(/script-src 'sha256-/);
}
async function scan(page) {
  await page.evaluate(axe.source);
  const results = await page.evaluate(async () => window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } }));
  expect(results.violations).toEqual([]);
}
test("D3 real ontology downloads match Python output and preserve semantic design UTF-8", async ({ page }) => {
  await open(page, "/blueprint.html#/ontology");
  expect(await bytes(page, "Download ontology.ttl")).toEqual(fs.readFileSync("build/demo/ontology/ontology.ttl"));
  for (const [name, tokens] of [
    ["ontology.md", ["customerId", "accountnumber", "core_silver.customer", "to verify"]],
    ["data-agents.md", ["DA-01", "instructions", "questions", "sources"]],
    ["data-products.md", ["DP-01", "quality", "access", "commitment"]]
  ]) {
    const text = (await bytes(page, "Download " + name)).toString("utf8");
    for (const token of tokens) expect(text).toContain(token);
    expect(text).not.toContain("\uFFFD");
  }
});
for (const colorScheme of ["light", "dark"]) {
  test(`D3 ontology keyboard feedback reflow and Preview no-ack/ack/reload (${colorScheme})`, async ({ page }, info) => {
    test.setTimeout(240_000);
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
    await page.emulateMedia({ colorScheme });
    await open(page, "/blueprint.html#/ontology");
    await scan(page);
    const node = page.locator('.onode[data-entity="Customer"]');
    await node.focus(); await page.keyboard.press("Enter");
    await expect(node).toBeFocused();
    await expect(page.locator("#opanel")).toHaveAttribute("data-entity", "Customer");
    await page.locator("#v-onto-Customer-note").fill("Binding reviewed café ✓");
    await page.reload();
    await page.locator('.onode[data-entity="Customer"]').click();
    await expect(page.locator("#v-onto-Customer-note")).toHaveValue("Binding reviewed café ✓");
    await page.locator("#ontology-journey-D2").click();
    await expect(page.locator("#ontology-journey-D2")).toBeFocused();
    await expect(page.locator("#opanel")).toHaveCount(0);
    await page.locator("#ontology-journey-all").click();
    await page.locator('.onode[data-entity="Customer"]').click();
    await page.locator("#opanel .ev").first().click();
    await expect(page.locator("#drawer")).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator("#opanel .ev").first()).toBeFocused();
    for (const width of [1440, 320]) {
      await page.setViewportSize({ width, height: 900 });
      await scan(page);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
      const target = await node.boundingBox();
      expect(target.width).toBeGreaterThanOrEqual(24);
      expect(target.height).toBeGreaterThanOrEqual(24);
      await info.attach(`ontology-${colorScheme}-${width}`, { body: await page.screenshot({ fullPage: true }), contentType: "image/png" });
    }
    // All selectively ported sections, including governance and instructions,
    // remain subject to the same axe rules when actually expanded at 320px.
    for (const summary of await page.locator("details.ontsection > summary").all()) {
      await summary.click();
      await scan(page);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
      await summary.click();
    }
    await open(page, "/blueprint-preview.html#/finops");
    await expect(page.locator(".preview-notice")).toContainText(NOTICE);
    await expect(page.locator(".vkpis")).toHaveCount(0);
    await scan(page);
    await page.locator("#finops-preview-ack").click();
    await expect(page.locator(".preview-notice")).toContainText(NOTICE);
    await expect(page.locator("#view")).toContainText("CHF 17,708");
    expect(await page.locator(".preview-notice").evaluate((notice) =>
      !!(notice.compareDocumentPosition(document.querySelector(".vkpis")) & Node.DOCUMENT_POSITION_FOLLOWING))).toBe(true);
    await scan(page);
    await page.goto("/blueprint-preview.html#/prd");
    await expect(page.locator("#view")).toContainText("ROI 545%");
    expect((await bytes(page, "Download the PRD (Markdown)")).toString("utf8")).toContain(NOTICE);
    await page.reload();
    await expect(page.locator("#view")).not.toContainText("ROI 545%");
    expect((await bytes(page, "Download the PRD (Markdown)")).toString("utf8")).not.toContain("ROI 545%");
    await scan(page);
    expect(errors).toEqual([]);
  });
}

test("D3 legacy forged GA/cached consent stays gated, while ordinary core value needs no FinOps", async ({ page }) => {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  await page.route("**/blueprint-preview.html", async (route) => {
    const response = await route.fetch();
    const body = (await response.text()).replace(/(<script[^>]+id="bp-data"[^>]*>)([\s\S]*?)(<\/script>)/, (_, a, json, b) => {
      const data = JSON.parse(json);
      data.finops.finops_preview = { maturity: "ga", acknowledgement: { kind: "human", scope: "forever" } };
      delete data.value_case.finops_preview;
      for (const domain of data.domains) for (const u of domain.use_cases || []) if (u.business_value) delete u.business_value.finops_preview;
      return a + JSON.stringify(data).replace(/</g, "\\u003c") + b;
    });
    await route.fulfill({ response, body }); // Actual unchanged script hashes and hosting policy.
  });
  await open(page, "/blueprint-preview.html#/prd");
  await page.evaluate(() => localStorage.setItem("finopsAcknowledged", "true"));
  await page.reload();
  await expect(page.locator(".preview-notice")).toContainText(NOTICE);
  await expect(page.locator("#view")).not.toContainText("ROI 545%");
  expect((await bytes(page, "Download the PRD (Markdown)")).toString("utf8")).not.toContain("ROI 545%");
  await page.goto("/blueprint-preview.html#/finops");
  await expect(page.locator(".vkpis")).toHaveCount(0);
  await page.locator("#finops-preview-ack").click();
  await expect(page.locator(".vkpis")).toHaveCount(1);
  await open(page, "/blueprint.html#/usecases");
  await expect(page.locator(".preview-notice")).toHaveCount(0);
  await expect(page.locator("#view")).toContainText("CHF 8.21M");
  await expect(page.locator('#rail button[data-view="finops"]')).toHaveCount(0);
  await scan(page);
  await open(page, "/blueprint-preview.html#/finops");
  await expect(page.locator(".vkpis")).toHaveCount(0);
  expect(errors).toEqual([]);
});

async function previewData(page, change) {
  await page.route("**/blueprint-preview.html", async (route) => {
    const response = await route.fetch();
    const body = (await response.text()).replace(/(<script[^>]+id="bp-data"[^>]*>)([\s\S]*?)(<\/script>)/, (_, a, json, b) => {
      const data = JSON.parse(json);
      change(data);
      return a + JSON.stringify(data).replace(/</g, "\\u003c") + b;
    });
    await route.fulfill({ response, body }); // Retain actual hosting CSP and script hashes.
  });
}
const caseData = (data) => data.domains.flatMap((d) => d.use_cases || []);

test("D3 review inverse-detachment gates portfolio ranking and actual PRD export under CSP", async ({ page }) => {
  await previewData(page, (data) => { delete data.finops; delete data.value_case.finops_preview; });
  await open(page, "/blueprint-preview.html#/usecases");
  await expect(page.locator(".preview-notice")).toContainText(NOTICE);
  await expect(page.locator(".vkpis")).not.toContainText(/212k|150k|7.61M/);
  await expect(page.locator(".vkpis")).toContainText("4.57M");
  expect(await page.locator(".asst tbody tr td:first-child").allTextContents()).not.toContainEqual(expect.stringMatching(/#/));
  for (const cell of await page.locator(".asst tbody tr td:nth-child(5)").all()) await expect(cell).toHaveText("To be confirmed");
  await scan(page);
  await page.goto("/blueprint-preview.html#/prd");
  const before = (await bytes(page, "Download the PRD (Markdown)")).toString("utf8");
  expect(before).toContain(NOTICE);
  expect(before).not.toMatch(/NPV CHF 838k|ROI 545%|NPV CHF 6.78M/);
  await page.locator("#finops-preview-ack").click();
  const after = (await bytes(page, "Download the PRD (Markdown)")).toString("utf8");
  expect(after).toContain(NOTICE);
  expect(after).toContain("ROI 545%");
  await page.goto("/blueprint-preview.html#/usecases");
  await expect(page.locator(".vkpis")).toContainText("7.61M");
  expect((await page.locator(".asst tbody tr td:first-child").allTextContents()).some((s) => s.includes("#"))).toBe(true);
  await scan(page);
  await page.reload();
  await expect(page.locator(".vkpis")).not.toContainText(/212k|150k|7.61M/);
});

test("D3 review mixed/public provenance keeps public cases without a replacement partial total", async ({ page }) => {
  await previewData(page, (data) => {
    delete data.finops; delete data.value_case.finops_preview;
    const value = caseData(data).find((u) => u.id === "UC05").business_value;
    delete value.finops_preview; value.npv = 777123; value.roi = 0.777;
  });
  await open(page, "/blueprint-preview.html#/usecases");
  await expect(page.locator(".vkpis")).not.toContainText(/212k|150k|7.61M|777k/);
  await expect(page.locator("#view")).toContainText("CHF 777k");
  await page.goto("/blueprint-preview.html#/prd");
  const md = (await bytes(page, "Download the PRD (Markdown)")).toString("utf8");
  expect(md).toContain("NPV CHF 777k");
  expect(md).not.toMatch(/NPV CHF 6.78M|ROI 1516%/);
  await scan(page);
  await open(page, "/blueprint.html#/usecases");
  await expect(page.locator(".preview-notice")).toHaveCount(0);
  await expect(page.locator(".vkpis")).toContainText("8.21M");
});

test("D3 review linked assumption identity gates cards loop inputs and real feedback downloads without losing notes", async ({ page }, info) => {
  let detached = false;
  await previewData(page, (data) => {
    const cost = data.finops.assumptions.find((a) => a.id === "ASS-114");
    cost.statement = "Build effort, source figure 90,000 CHF";
    if (detached) cost.finops_preview = { maturity: "ga", acknowledgement: { kind: "cached" } };
    data.value_case.assumptions.push(structuredClone(cost), {
      id: "ASS-PUBLIC", statement: "Independent user amount", unit: "CHF", base: 424242,
      low: 400000, high: 450000, source_type: "customer", src: ["E04"], status: "open"
    });
    caseData(data).find((u) => u.id === "UC05").business_value.assumptions.push("ASS-114", "ASS-PUBLIC");
    data.feedback_loop.quadrants[0].outcomes.push({ text: "Linked assumptions", assumptions: ["ASS-114", "ASS-PUBLIC"] });
    if (detached) {
      delete data.finops; delete data.value_case.finops_preview;
      caseData(data).forEach((u) => { if (u.business_value) delete u.business_value.finops_preview; });
    }
  });
  const cost = page.locator(".assrow").filter({ hasText: "ASS-114" });
  await open(page, "/blueprint-preview.html#/usecases/UC05");
  await expect(cost).not.toContainText(/90,000|60,000|130,000/);
  await expect(cost.locator(".assval")).toHaveCount(0);
  await expect(page.locator(".assrow").filter({ hasText: "ASS-PUBLIC" })).toContainText("424,242 CHF");
  await page.goto("/blueprint-preview.html#/overview");
  await expect(page.locator(".flassi").filter({ hasText: "ASS-114" })).not.toContainText("90,000");
  await expect(page.locator(".flassi").filter({ hasText: "ASS-PUBLIC" })).toContainText("424,242 CHF");
  await page.goto("/blueprint-preview.html#/usecases");
  await expect(page.locator(".asst tr").filter({ hasText: "ASS-114" })).not.toContainText(/90,000|60,000|130,000/);
  await page.goto("/blueprint-preview.html#/usecases/UC05");
  await scan(page);
  await info.attach("linked-assumption-withheld", { body: await page.screenshot({ fullPage: true }), contentType: "image/png" });
  await page.locator("#finops-preview-ack").click();
  await expect(cost).toContainText("90,000 CHF");
  await expect(cost).toContainText("60,000 CHF");
  await expect(cost).toContainText("130,000 CHF");
  await expect(page.locator(".preview-notice")).toContainText(NOTICE);
  await cost.locator(".assval").fill("90013");
  await cost.locator(".assnote").fill("Owner and source retained ✓");
  await expect(cost.locator(".assnote")).toBeFocused();
  await page.goto("/blueprint-preview.html#/discovery");
  const acknowledged = JSON.parse((await bytes(page, "Export workshop feedback (JSON)")).toString("utf8"));
  expect(acknowledged.validations["ass:ASS-114"]).toMatchObject({ value: 90013, note: "Owner and source retained ✓" });
  expect(acknowledged.finops_preview_notice).toBe(NOTICE);
  await page.reload();
  const withheld = JSON.parse((await bytes(page, "Export workshop feedback (JSON)")).toString("utf8"));
  expect(withheld.validations["ass:ASS-114"]).not.toHaveProperty("value");
  expect(withheld.validations["ass:ASS-114"].note).toBe("Owner and source retained ✓");
  await page.goto("/blueprint-preview.html#/usecases/UC05");
  await expect(cost.locator(".assval")).toHaveCount(0);
  await expect(cost.locator(".assnote")).toHaveValue("Owner and source retained ✓");
  detached = true;
  await page.reload();
  await expect(cost).not.toContainText(/90,000|60,000|130,000/);
  await expect(page.locator(".preview-notice")).toContainText(NOTICE);
  await scan(page);
});

const NESTED_FINANCIAL_FIELDS = ["npv", "npv_budget", "roi", "payback_months", "cost_year", "build", "pv_cost", "break_even", "scenarios", "rank", "swing_npv"];
function nestFinancialValue(data) {
  const value = caseData(data).find((u) => u.id === "UC05").business_value;
  value.results = {};
  for (const key of [...NESTED_FINANCIAL_FIELDS, "finops_preview"]) {
    if (key in value) { value.results[key] = value[key]; delete value[key]; }
  }
  return value;
}

test("D3 nested result and linked-input ancestry gate real PRD download streams before ack and on reload", async ({ page }) => {
  test.setTimeout(120_000);
  let mode = "result";
  await previewData(page, (data) => {
    const value = nestFinancialValue(data), cost = data.finops.assumptions.find((a) => a.id === "ASS-114");
    delete data.finops; delete data.value_case.finops_preview;
    caseData(data).forEach((u) => { if (u.id !== "UC05" && u.business_value) delete u.business_value.finops_preview; });
    if (mode === "input") {
      delete value.results.finops_preview;
      cost.finops_preview = { maturity: "ga", acknowledgement: { kind: "cached" } };
      data.value_case.assumptions.push(cost);
      value.results.assumptions = ["ASS-114"];
    } else {
      value.results.finops_preview = { maturity: "ga", acknowledgement: { kind: "cached-human", scope: "forever" } };
      if (mode === "outer") value.finops_preview = { maturity: "preview" };
    }
  });
  for (mode of ["result", "input", "outer"]) {
    await open(page, "/blueprint-preview.html#/prd");
    await expect(page.locator(".preview-notice")).toContainText(NOTICE);
    await expect(page.locator("#view")).not.toContainText(/NPV CHF 838k|ROI 545%|payback 4.6 months/);
    const before = (await bytes(page, "Download the PRD (Markdown)")).toString("utf8");
    expect(before).toContain(NOTICE);
    expect(before).not.toMatch(/NPV CHF 838k|ROI 545%|payback 4.6 months/);
    await page.goto("/blueprint-preview.html#/usecases");
    await expect(page.locator(".vkpis")).not.toContainText(/212k|150k|7.61M/);
    expect((await page.locator(".asst tbody tr td:first-child").allTextContents()).some((s) => s.includes("#"))).toBe(false);
    for (const cell of await page.locator(".asst tbody tr td:nth-child(5)").all()) await expect(cell).toHaveText("To be confirmed");
    await page.goto("/blueprint-preview.html#/usecases/UC05");
    if (mode === "input") {
      const input = page.locator(".assrow").filter({ hasText: "ASS-114" });
      await expect(input.locator(".assval")).toHaveCount(0);
      await expect(input).not.toContainText("90,000 CHF");
    }
    await scan(page);
    await page.locator("#finops-preview-ack").click();
    await expect(page.locator(".ucval")).toContainText("CHF 838k");
    await expect(page.locator(".ucval")).toContainText("ROI 545%");
    if (mode === "input") await expect(page.locator(".assrow").filter({ hasText: "ASS-114" })).toContainText("90,000 CHF");
    await page.goto("/blueprint-preview.html#/prd");
    const after = (await bytes(page, "Download the PRD (Markdown)")).toString("utf8");
    expect(after).toMatch(/NPV CHF 838k.*ROI 545%.*payback 4.6 months/);
    expect(after).toContain(NOTICE);
    expect(after).toMatch(/[Pp]rovisional/);
    await page.reload();
    const reset = (await bytes(page, "Download the PRD (Markdown)")).toString("utf8");
    expect(reset).not.toMatch(/NPV CHF 838k|ROI 545%|payback 4.6 months/);
    await expect(page.locator("#finops-preview-ack")).toBeVisible();
  }
});

test("D3 nested public counterparts remain available and selected-result gaps do not recover stale outer figures", async ({ page }) => {
  let state = "mixed";
  await previewData(page, (data) => {
    const value = nestFinancialValue(data);
    delete data.finops; delete data.value_case.finops_preview; delete value.results.finops_preview;
    value.results.npv = 777123; value.results.roi = 0.777; value.results.payback_months = 4.6;
    value.npv = 999999; value.payback_months = 4.6;
    if (state !== "mixed") caseData(data).forEach((u) => { if (u.business_value) delete u.business_value.finops_preview; });
    if (state === "partial") value.results = { roi: 0.777 };
  });
  for (state of ["mixed", "public", "partial"]) {
    await open(page, "/blueprint-preview.html#/usecases/UC05");
    await expect(page.locator("#finops-preview-ack")).toHaveCount(state === "mixed" ? 1 : 0);
    await expect(page.locator(".ucval")).toContainText("ROI 78%");
    await expect(page.locator(".ucval")).not.toContainText(/999k|1.00M/);
    if (state !== "partial") await expect(page.locator(".ucval")).toContainText("CHF 777k");
    else await expect(page.locator(".ucval")).toContainText("NPVTo be confirmed");
    await page.goto("/blueprint-preview.html#/prd");
    const md = (await bytes(page, "Download the PRD (Markdown)")).toString("utf8");
    const summary = md.split("\n").find((line) => /UC05.*ROI 78%/.test(line));
    expect(summary).toBeTruthy();
    if (state !== "partial") expect(summary).toMatch(/NPV CHF 777k.*ROI 78%.*payback 4.6 months/);
    else expect(summary).not.toMatch(/NPV CHF|payback/);
  }
  await scan(page);
});
