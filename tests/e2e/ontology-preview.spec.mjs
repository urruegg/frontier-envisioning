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
  return response;
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

const PREVIEW_MATRIX_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const PREVIEW_MATRIX_VIEWS = [
  { id: "finops", route: "finops", label: "FinOps" },
  { id: "portfolio", route: "usecases", label: "Use cases" },
  { id: "uc05", route: "usecases/UC05", label: "Use cases" },
  { id: "prd", route: "prd", label: "PRD" }
];

async function matrixKpi(page, label, view) {
  const root = page.locator(view === "uc05" ? ".ucval" : "#view");
  return root.locator(".vkpi").filter({ has: page.locator(".kl").filter({ hasText: new RegExp("^" + label + "$") }) }).locator("b").textContent();
}

async function expectPreviewMatrixFigures(page, view, acknowledged) {
  await expect(page.locator(".preview-notice")).toContainText(NOTICE);
  await expect(page.locator("#finops-preview-ack")).toHaveCount(acknowledged ? 0 : 1);
  if (acknowledged) await expect(page.locator(".preview-notice")).toContainText("Provisional comparisons, not recommendations.");
  if (view === "finops") {
    await expect(page.locator(".vkpis")).toHaveCount(acknowledged ? 1 : 0);
    if (acknowledged) {
      expect(await matrixKpi(page, "Run cost per month", view)).toBe("CHF 17,708");
      await expect(page.locator(".finops-agents tbody tr")).toHaveCount(2);
      await expect(page.locator("#view")).toContainText("Purchase options for the credits");
    } else await expect(page.locator("#view")).not.toContainText(/CHF 17,708|CHF 212k|CHF 150k/);
  } else if (view === "portfolio" || view === "uc05") {
    expect(await matrixKpi(page, "Cost per year", view)).toBe(acknowledged ? (view === "portfolio" ? "CHF 212k" : "CHF 37k") : "To be confirmed");
    expect(await matrixKpi(page, "NPV", view)).toBe(acknowledged ? (view === "portfolio" ? "CHF 7.61M" : "CHF 838k") : "To be confirmed");
    if (view === "portfolio") {
      expect(await matrixKpi(page, "Value per year", view)).toBe("CHF 4.57M");
      if (acknowledged) await expect(page.locator("#view")).toContainText("545%");
      else {
        await expect(page.locator("#view")).not.toContainText(/ROI 545%|NPV CHF 838k/);
        for (const cell of await page.locator(".asst tbody tr td:nth-child(5)").all()) await expect(cell).toHaveText("To be confirmed");
      }
    } else {
      await expect(page.locator("#ucdetail")).toContainText("UC05");
      if (acknowledged) await expect(page.locator(".ucval")).toContainText("ROI 545%");
      else await expect(page.locator(".ucval")).not.toContainText(/ROI 545%|4.6 months/);
    }
  } else {
    const problem = await page.locator("#bp-data").evaluate((n) => JSON.parse(n.textContent).prd.problem);
    await expect(page.locator("#view")).toContainText(problem);
    await expect(page.locator(".req tbody tr")).toHaveCount(35);
    if (acknowledged) {
      await expect(page.locator("#view")).toContainText("NPV CHF 838k");
      await expect(page.locator("#view")).toContainText("ROI 545%");
      await expect(page.locator("#view")).toContainText("NPV CHF 6.78M");
    } else await expect(page.locator("#view")).not.toContainText(/NPV CHF 838k|ROI 545%|NPV CHF 6.78M|ROI 1516%/);
  }
}

async function attachPreviewMatrixJson(info, name, data) {
  const file = info.outputPath(name + ".json");
  fs.writeFileSync(file, JSON.stringify(data, null, 2));
  await info.attach(name, { path: file, contentType: "application/json" });
}

async function measurePreviewMatrixState(page, info, label, width, policy) {
  // One actual local-axe invocation per labelled state. Screenshots, target and
  // functional checks are additional measurements, never counted as axe scans.
  await page.evaluate(axe.source);
  const report = await page.evaluate(async (tags) =>
    window.axe.run(document, { runOnly: { type: "tag", values: tags } }), PREVIEW_MATRIX_TAGS);
  await attachPreviewMatrixJson(info, label + "-axe", report);
  const layout = await page.evaluate(() => {
    const visible = (n) => n.getClientRects().length && !n.closest("[hidden],[inert]") &&
      getComputedStyle(n).visibility !== "hidden" && getComputedStyle(n).display !== "none";
    const identify = (n) => n.localName + (n.id ? "#" + n.id : "") +
      (n.getAttribute("class") ? "." + n.getAttribute("class").trim().split(/\s+/).join(".") : "");
    const targets = [...document.querySelectorAll(
      "#view button,#view input,#view select,#view textarea,#view summary,#view a[href],#view [role=button],#view [role=tab]"
    )].filter((n) => visible(n) && !n.matches(":disabled")).map((n) => {
      // Radio/checkbox labels are real associated hit areas, not a fictional
      // enlargement of the native input. SVG controls use their actual shape.
      let hit = n;
      if (n.matches('input[type="radio"],input[type="checkbox"]')) hit = [...n.labels || []].find(visible) || n;
      if (n.namespaceURI === "http://www.w3.org/2000/svg") hit = n.querySelector("rect,circle,ellipse,polygon,path") || n;
      const rect = hit.getBoundingClientRect();
      return { control: identify(n), name: (n.getAttribute("aria-label") || n.textContent || n.name || "").trim().replace(/\s+/g, " ").slice(0, 100),
        hitRegion: identify(hit), width: rect.width, height: rect.height };
    });
    const tables = [...document.querySelectorAll("#view .tscroll")].filter(visible).map((n) => ({
      name: n.getAttribute("aria-label"), clientWidth: n.clientWidth, scrollWidth: n.scrollWidth,
      overflowX: getComputedStyle(n).overflowX, tabIndex: n.tabIndex
    }));
    return { documentWidth: document.documentElement.scrollWidth, viewportWidth: innerWidth, targets, tables };
  });
  const undersized = layout.targets.filter((t) => t.width < 24 || t.height < 24);
  const scrollingTables = layout.tables.filter((t) => t.scrollWidth > t.clientWidth + 1);
  const badScrolls = scrollingTables.filter((t) => !["auto", "scroll"].includes(t.overflowX) || t.tabIndex < 0);
  const summary = { label, axeScans: 1, wcag: report.violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })),
    incomplete: report.incomplete.map((v) => ({ id: v.id, nodes: v.nodes.length })), documentWidth: layout.documentWidth,
    viewportWidth: width, targetCount: layout.targets.length, undersized, scrollingTables, badScrolls };
  await attachPreviewMatrixJson(info, label + "-layout-targets", { ...summary, policy, measurements: layout });
  console.log(JSON.stringify({ previewMatrix: label, axeScans: 1, wcagViolations: report.violations.length,
    documentWidth: layout.documentWidth, targets: layout.targets.length, undersized: undersized.length, localTableScrolls: scrollingTables.length }));
  // Soft checks collect the complete measured matrix even if a real issue is
  // found. Failures stay failures; no excluded rules, target waivers or CSS edits.
  expect.soft(report.violations, label + ": WCAG axe violations").toEqual([]);
  expect.soft(layout.documentWidth, label + ": no document overflow").toBeLessThanOrEqual(width + 1);
  expect.soft(layout.targets.length, label + ": actual interactive targets").toBeGreaterThan(0);
  expect.soft(undersized, label + ": associated labels/SVG hit regions must be at least 24px").toEqual([]);
  expect.soft(badScrolls, label + ": wide tables scroll locally and remain keyboard reachable").toEqual([]);
  return summary;
}

for (const colorScheme of ["light", "dark"]) {
  for (const width of [1440, 320]) {
    test(`D5 Preview AA/layout matrix ${colorScheme} ${width}`, async ({ page }, info) => {
      test.setTimeout(180_000);
      const problems = [], states = [];
      page.on("pageerror", (e) => problems.push(e.message));
      page.on("console", (m) => { if (m.type() === "error") problems.push(m.text()); });
      await page.emulateMedia({ colorScheme, reducedMotion: "reduce" });
      await page.setViewportSize({ width, height: 900 });
      for (const view of PREVIEW_MATRIX_VIEWS) {
        // A new document for every route: fixture/caller metadata and prior
        // routes never stand in for a genuine transient viewer acknowledgement.
        const response = await open(page, "/blueprint-preview.html#/" + view.route);
        expect(response.status()).toBe(200);
        const policy = response.headers()["content-security-policy"];
        await expect(page.locator("#crumb b")).toHaveText(view.label);
        let publicValues;
        for (const acknowledged of [false, true]) {
          if (acknowledged) await page.locator("#finops-preview-ack").click();
          await expectPreviewMatrixFigures(page, view.id, acknowledged);
          if (view.id === "portfolio" || view.id === "uc05") {
            const current = [await matrixKpi(page, "Value per year", view.id), await matrixKpi(page, "Cash per year", view.id)];
            if (!acknowledged) {
              publicValues = current;
              for (const value of current) expect(value).toMatch(/^CHF /);
            } else expect(current, "independent public value survives acknowledgement").toEqual(publicValues);
          }
          const label = `preview-${view.id}-${acknowledged ? "after-ack" : "before-ack"}-${colorScheme}-${width}`;
          states.push(await measurePreviewMatrixState(page, info, label, width, policy));
          if (acknowledged && ["finops", "prd"].includes(view.id)) {
            const screenshot = info.outputPath(label + ".png");
            await page.screenshot({ path: screenshot, fullPage: true });
            await info.attach(label, { path: screenshot, contentType: "image/png" });
          }
        }

      }
      expect(states).toHaveLength(8);
      expect(new Set(states.map((s) => s.label)).size).toBe(8);
      expect(states.reduce((count, s) => count + s.axeScans, 0)).toBe(8);
      expect(problems, "real CSP/page errors").toEqual([]);
      await attachPreviewMatrixJson(info, `preview-matrix-${colorScheme}-${width}`, states);
    });
  }
}

test("D5 assumption instances label clicks preserve feedback and matrix scroll keeps keyboard navigation local", async ({ page }) => {
  await open(page, "/blueprint-preview.html#/usecases/UC05");
  const assumption = (selector) => page.locator(selector).filter({
    has: page.locator("b").filter({ hasText: /^ASS-006$/ })
  });
  const detail = assumption(".ucval .assrow");
  const portfolio = assumption(".asst tbody tr");
  await expect(detail).toHaveCount(1);
  await expect(portfolio).toHaveCount(1);
  for (const row of [detail, portfolio]) {
    const sizes = await row.locator('input[type="radio"]').evaluateAll((nodes) => nodes.map((n) => {
      const rect = n.getBoundingClientRect();
      return { width: rect.width, height: rect.height };
    }));
    expect(sizes).toHaveLength(4);
    for (const size of sizes) {
      expect(size.width, "actual native radio width, not only its label").toBeGreaterThanOrEqual(24);
      expect(size.height, "actual native radio height, not only its label").toBeGreaterThanOrEqual(24);
    }
  }
  const duplicates = await page.locator("[id]").evaluateAll((nodes) => {
    const counts = new Map();
    for (const n of nodes) counts.set(n.id, (counts.get(n.id) || 0) + 1);
    return [...counts].filter(([, count]) => count > 1).map(([id, count]) => ({ id, count }));
  });
  expect.soft(duplicates, "repeated assumption renderings must not duplicate DOM IDs").toEqual([]);
  expect.soft(await detail.locator('input[value="adjusted"]').getAttribute("name"),
    "native radio groups are local to the rendered instance").not.toBe(await portfolio.locator('input[value="adjusted"]').getAttribute("name"));
  const portfolioLabel = portfolio.locator("label.opt").filter({ hasText: /^Adjust$/ });
  expect.soft(await portfolioLabel.evaluate((label) => label.control === label.querySelector("input")),
    "label must activate its own instance, not the first matching ID elsewhere").toBe(true);
  await detail.locator("label.opt").filter({ hasText: /^Confirm$/ }).click();
  expect.soft(await portfolio.locator('input[value="validated"]').isChecked(), "peer reflects the saved Confirm verdict immediately").toBe(true);
  await portfolioLabel.click();
  expect.soft({ detailAdjusted: await detail.locator('input[value="adjusted"]').isChecked(),
    portfolioAdjusted: await portfolio.locator('input[value="adjusted"]').isChecked() })
    .toEqual({ detailAdjusted: true, portfolioAdjusted: true });
  for (const row of [detail, portfolio]) {
    expect.soft((await row.locator(".pill").allTextContents()).some((text) => text.startsWith("Adjusted")), "status badge reflects the same saved verdict").toBe(true);
    expect.soft(await row.locator(".assbox .status").textContent()).toBe("Saved");
  }
  await portfolio.locator(".assval").fill("0.62");
  expect.soft(await detail.locator(".assval").inputValue(), "numeric value echoes without reload").toBe("0.62");
  await portfolio.locator(".assnote").fill("Assumption scope continuity ✓");
  expect.soft(await detail.locator(".assnote").inputValue(), "note echoes without reload").toBe("Assumption scope continuity ✓");
  await detail.locator(".assval").fill("0.73");
  expect.soft(await portfolio.locator(".assval").inputValue(), "numeric editing works in either instance").toBe("0.73");
  await detail.locator(".assnote").fill("Updated shared assumption ✓");
  expect.soft(await portfolio.locator(".assnote").inputValue(), "note editing works in either instance").toBe("Updated shared assumption ✓");
  await expect(detail.locator(".assnote")).toBeFocused();
  const saved = await page.evaluate(() => {
    for (const key of Object.keys(localStorage).filter((k) => k.startsWith("fbp:"))) {
      const value = JSON.parse(localStorage.getItem(key))["val|ass|ASS-006"];
      if (value) return value;
    }
  });
  expect(saved).toMatchObject({ status: "adjusted", value: 0.73, note: "Updated shared assumption ✓" });
  await page.goto("/blueprint-preview.html#/overview");
  await page.goto("/blueprint-preview.html#/usecases/UC05");
  await page.reload();
  for (const row of [detail, portfolio]) {
    await expect(row.locator('input[value="adjusted"]')).toBeChecked();
    await expect(row.locator(".assval")).toHaveValue("0.73");
    await expect(row.locator(".assnote")).toHaveValue("Updated shared assumption ✓");
  }
  await expect(page.locator("#finops-preview-ack")).toBeVisible();
  await page.setViewportSize({ width: 320, height: 900 });
  const matrix = page.locator(".matrixwrap");
  await expect(matrix).toHaveAttribute("tabindex", "0");
  expect(await matrix.evaluate((n) => ({
    scrolls: n.scrollWidth > n.clientWidth, overflow: getComputedStyle(n).overflowX
  }))).toEqual({ scrolls: true, overflow: "auto" });
  const url = page.url();
  await matrix.focus();
  await page.keyboard.press("ArrowRight");
  await expect.poll(() => matrix.evaluate((n) => n.scrollLeft)).toBeGreaterThan(0);
  expect(page.url()).toBe(url);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(321);
  await page.locator('svg.matrix .bub[aria-label^="UC05 "]').focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#ucdetail")).toContainText("UC05");
  await expect(detail.locator(".assnote")).toHaveValue("Updated shared assumption ✓");
});

test("D5 shared assumption live updates preserve active caret independence and withheld values", async ({ page }) => {
  await previewData(page, (data) => {
    const cost = data.finops.assumptions.find((a) => a.id === "ASS-114");
    data.value_case.assumptions.push(structuredClone(cost));
    caseData(data).find((u) => u.id === "UC05").business_value.assumptions.push("ASS-114");
  });
  await open(page, "/blueprint-preview.html#/usecases/UC05");
  const row = (selector, id) => page.locator(selector).filter({ has: page.locator("b").filter({ hasText: new RegExp("^" + id + "$") }) });
  const detail = row(".ucval .assrow", "ASS-006"), peer = row(".asst tbody tr", "ASS-006");
  const other = row(".asst tbody tr", "ASS-003");
  await other.locator(".assval").fill("17");
  await other.locator(".assnote").fill("Independent assumption ✓");
  await other.locator("label.opt").filter({ hasText: /^Reject$/ }).click();
  await detail.locator(".assval").fill("0.84");
  expect.soft(await peer.locator(".assval").inputValue()).toBe("0.84");
  await peer.locator(".assval").fill("0.91");
  expect.soft(await detail.locator(".assval").inputValue()).toBe("0.91");
  await detail.locator(".assval").fill("");
  expect.soft(await peer.locator(".assval").inputValue(), "clearing is not reconstructed as a base value or zero").toBe("");
  const active = detail.locator(".assnote");
  const original = await active.elementHandle();
  await active.fill("Alpha omega");
  await active.evaluate((n) => n.setSelectionRange(6, 6));
  await page.keyboard.insertText("live ");
  expect(await original.evaluate((n) => ({
    connected: n.isConnected, active: n === document.activeElement, start: n.selectionStart, end: n.selectionEnd, value: n.value
  }))).toEqual({ connected: true, active: true, start: 11, end: 11, value: "Alpha live omega" });
  expect.soft(await peer.locator(".assnote").inputValue()).toBe("Alpha live omega");
  await peer.locator(".assnote").fill("Peer source change ✓");
  expect.soft(await active.inputValue()).toBe("Peer source change ✓");
  await expect(peer.locator(".assnote")).toBeFocused();
  await expect(other.locator(".assval")).toHaveValue("17");
  await expect(other.locator(".assnote")).toHaveValue("Independent assumption ✓");
  await expect(other.locator('input[value="rejected"]')).toBeChecked();
  await page.locator("#finops-preview-ack").click();
  const privateDetail = row(".ucval .assrow", "ASS-114"), privatePeer = row(".asst tbody tr", "ASS-114");
  await privateDetail.locator(".assval").fill("90013");
  await page.reload(); // Numeric verdict stays stored, viewer acknowledgement does not.
  await privateDetail.locator(".assnote").fill("Withheld note live ✓");
  expect.soft(await privatePeer.locator(".assnote").inputValue()).toBe("Withheld note live ✓");
  await privatePeer.locator("label.opt").filter({ hasText: /^Adjust$/ }).click();
  expect.soft(await privateDetail.locator('input[value="adjusted"]').isChecked()).toBe(true);
  for (const target of [privateDetail, privatePeer]) {
    await expect(target.locator(".assval")).toHaveCount(0);
    await expect(target).not.toContainText(/90013|90,000|60,000|130,000/);
  }
  await expect(page.locator("#finops-preview-ack")).toBeVisible();
  const saved = await page.evaluate(() => {
    for (const key of Object.keys(localStorage).filter((k) => k.startsWith("fbp:"))) {
      const value = JSON.parse(localStorage.getItem(key))["val|ass|ASS-114"];
      if (value) return value;
    }
  });
  expect(saved).toMatchObject({ status: "adjusted", value: 90013, note: "Withheld note live ✓" });
});
