import { test, expect } from "@playwright/test";

async function bytes(page, button) {
  const event = page.waitForEvent("download");
  await page.getByRole("button", { name: button, exact: true }).click();
  const download = await event;
  const stream = await download.createReadStream();
  const chunks = [];
  for await (const chunk of stream) chunks.push(chunk);
  return { name: download.suggestedFilename(), text: Buffer.concat(chunks).toString("utf8") };
}

// Real RFC-style field parsing: newline/quote assertions must not split CSV records naively.
function csvRows(text) {
  const rows = [];
  let row = [], field = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (c === '"') {
      if (quoted && text[i + 1] === '"') { field += '"'; i++; }
      else quoted = !quoted;
    } else if (c === "," && !quoted) { row.push(field); field = ""; }
    else if ((c === "\r" || c === "\n") && !quoted) {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field); rows.push(row); row = []; field = "";
    } else field += c;
  }
  if (row.length || field) { row.push(field); rows.push(row); }
  return rows;
}

function watch(page) {
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  return errors;
}

async function model(page) {
  return page.locator("#bp-data").evaluate((n) => JSON.parse(n.textContent));
}

test("handover PRD download has model requirement IDs, text and scope verdict", async ({ page }) => {
  const errors = watch(page);
  await page.goto("/blueprint.html#/prd");
  const data = await model(page);
  await expect(page.locator(".req tbody tr")).toHaveCount(35);
  await expect(page.locator(".prd-nfr tbody tr")).toHaveCount(12);
  await page.locator('.valbox input[value="validated"]').check();
  await page.locator(".valbox textarea").fill("Scope agreed ✓");
  const md = await bytes(page, "Download the PRD (Markdown)");
  expect(md.name).toMatch(/-prd\.md$/);
  const requirements = [...data.prd.platform, ...data.prd.agents.flatMap((a) => a.requirements),
    ...data.prd.nfr, ...data.prd.acceptance];
  for (const r of requirements) {
    expect(md.text.match(new RegExp(`\\| ${r.id} \\|`, "g"))?.length, r.id).toBe(1);
    expect(md.text).toContain(r.text.replace(/\|/g, "\\|").replace(/\r?\n/g, " "));
    expect(await page.locator("#view").textContent()).toContain(r.id);
  }
  for (const value of [data.prd.problem, data.prd.owner, data.prd.exit_test, ...data.prd.goals,
    ...data.prd.out_of_scope, ...data.prd.definition_of_ready]) expect(md.text).toContain(value);
  expect(md.text).toContain("Status: validated");
  expect(md.text).toContain("Scope agreed ✓");
  expect(md.text).toContain("## 9. Release plan");
  await page.locator("#rail button").filter({ hasText: /^Discovery$/ }).click();
  const feedback = JSON.parse((await bytes(page, "Export workshop feedback (JSON)")).text);
  expect(feedback.validations["prd:scope"]).toMatchObject({ status: "validated", note: "Scope agreed ✓" });
  expect(errors).toEqual([]);
});

test("handover PRD business-value download matches every rendered summary and KPI definition", async ({ page }) => {
  const errors = watch(page);
  await page.goto("/blueprint-preview.html#/prd");
  await page.locator("#finops-preview-ack").click();
  const data = await model(page);
  const values = await page.locator("#view ul.clean > li").filter({ hasText: /NPV/ }).allTextContents();
  expect(values).toHaveLength(2);
  const rendered = values.map((text) => text.replace(/\s+/g, " ").trim());
  expect(rendered.join(" ")).toContain("NPV CHF 838k");
  expect(rendered.join(" ")).toContain("ROI 545%");
  expect(rendered.join(" ")).toContain("NPV CHF 6.78M");
  expect(rendered.join(" ")).toContain("ROI 1516%");
  const md = await bytes(page, "Download the PRD (Markdown)");
  for (const summary of rendered) expect.soft(md.text, summary).toContain(summary);
  for (const kpi of data.prd.kpis) {
    expect(await page.locator("#view").textContent()).toContain(kpi.definition);
    expect.soft(md.text, kpi.kpi).toContain(kpi.definition);
  }
  expect(errors).toEqual([]);
});

test("handover PRD scope rejection updates the restored badge, notes and actual download with focus", async ({ page }) => {
  const errors = watch(page);
  await page.goto("/blueprint.html#/prd");
  await page.locator("#v-prd-scope-validated").check();
  await page.locator(".valbox textarea").fill("Scope review ✓");
  await page.reload();
  await expect(page.locator(".idstrip > .pill").first()).toHaveText("Validated");
  await expect(page.locator("#v-prd-scope-validated")).toBeChecked();
  await page.locator("#v-prd-scope-rejected").check();
  await expect(page.locator("#v-prd-scope-rejected")).toBeFocused();
  await expect(page.locator("#v-prd-scope-rejected")).toBeChecked();
  await expect.soft(page.locator(".idstrip > .pill").first()).toHaveText("Rejected");
  await expect(page.locator(".valbox textarea")).toHaveValue("Scope review ✓");
  const stored = await page.evaluate(() => {
    for (const key of Object.keys(localStorage)) {
      const note = JSON.parse(localStorage.getItem(key))["val|prd|scope"];
      if (note) return note;
    }
  });
  expect(stored).toMatchObject({ status: "rejected", note: "Scope review ✓" });
  const md = await bytes(page, "Download the PRD (Markdown)");
  expect(md.text).toContain("Status: rejected");
  expect(md.text).toContain("Scope review ✓");
  await page.reload();
  await expect(page.locator(".idstrip > .pill").first()).toHaveText("Rejected");
  await expect(page.locator("#v-prd-scope-rejected")).toBeChecked();
  expect(errors).toEqual([]);
});

test("handover Plan downloads actual all/MVP/journey CSV rows and retains filter focus", async ({ page }) => {
  const errors = watch(page);
  await page.goto("/blueprint.html#/plan");
  await expect(page.locator(".kcard")).toHaveCount(29);
  await expect(page.locator(".kblane")).toHaveCount(5);
  await expect(page.locator(".kbst")).toHaveCount(7);
  await expect(page.locator(".kbph")).toHaveCount(4);
  const all = await bytes(page, "Export backlog (CSV)");
  expect(all.text.split("\r\n")[0]).toBe("ID,Title,Work Item Type,State,Area Path,Tags,Description,Acceptance Criteria,Owner");
  expect(csvRows(all.text)).toHaveLength(30);
  await page.setViewportSize({ width: 320, height: 900 });
  const scroll = page.locator(".kbwrap");
  await scroll.focus();
  await page.keyboard.press("ArrowRight");
  await expect(page).toHaveURL(/#\/plan$/);
  await expect.poll(() => scroll.evaluate((n) => n.scrollLeft)).toBeGreaterThan(0);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.locator("#plan-mvp").check();
  await expect(page.locator("#plan-mvp")).toBeFocused();
  await expect(page.locator(".kcard")).toHaveCount(2);
  const mvp = csvRows((await bytes(page, "Export backlog (CSV)")).text);
  expect(mvp.slice(1).map((r) => r[0]).sort()).toEqual(["D2-A01", "D3-A05"]);
  await page.locator("#plan-lane-D2").click();
  await expect(page.locator("#plan-lane-D2")).toBeFocused();
  await expect(page.locator("#plan-lane-D2")).toHaveAttribute("aria-pressed", "true");
  expect(csvRows((await bytes(page, "Export backlog (CSV)")).text)).toHaveLength(2);
  const card = page.locator(".kcard");
  await card.focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#drawer")).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(card).toBeFocused();
  expect(errors).toEqual([]);
});

test("handover CSV preserves quotes newline Unicode and neutralises spreadsheet prefixes", async ({ page }) => {
  const errors = watch(page);
  const samples = ['=1+1', ' +SUM(1,2)', '-1+2', '@SUM(A1)', '\t=2+2', '\r=3+3', 'Normal "quoted", café\n第二行'];
  await page.route("**/blueprint.html", async (route) => {
    const response = await route.fetch();
    const html = (await response.text()).replace(
      /(<script[^>]+id="bp-data"[^>]*>)([\s\S]*?)(<\/script>)/,
      (_, start, json, end) => {
        const data = JSON.parse(json);
        const agents = data.domains.flatMap((d) => [d.orchestrator, ...d.agents].filter(Boolean));
        samples.forEach((value, i) => { agents[i].capability = value; agents[i].owner = value; });
        return start + JSON.stringify(data).replace(/</g, "\\u003c") + end;
      });
    await route.fulfill({ response, body: html });
  });
  await page.goto("/blueprint.html#/plan");
  const csv = (await bytes(page, "Export backlog (CSV)")).text;
  const rows = csvRows(csv).slice(1);
  for (let i = 0; i < samples.length; i++) {
    const expected = i < 6 ? "'" + samples[i] : samples[i];
    expect(rows[i][6]).toBe(expected);
    expect(rows[i][8]).toBe(expected);
    expect(rows[i]).toHaveLength(9);
  }
  expect(csv).toContain('"Normal ""quoted"", café\n第二行"');
  expect(errors).toEqual([]);
});

test("handover risks live ratings, closed selection, filters and feedback bytes", async ({ page }) => {
  const errors = watch(page);
  await page.goto("/blueprint.html#/risks");
  await expect(page.locator(".riskrow")).toHaveCount(22);
  await expect(page.locator(".idstrip")).toContainText("2 high");
  await expect(page.locator(".idstrip")).toContainText("16 medium");
  await expect(page.locator(".idstrip")).toContainText("4 low");
  const risk = await page.locator("#rpanel").getAttribute("data-risk");
  const likelihood = page.locator('#rpanel select[id$="-likelihood"]');
  const ratingId = await likelihood.getAttribute("id");
  await likelihood.selectOption("1");
  await expect(page.locator(`[id="${ratingId}"]`)).toBeFocused();
  await page.locator('#rpanel select[id$="-impact"]').selectOption("1");
  await expect(page.locator("#rpanel .ptitle")).toContainText("Score 1");
  await page.locator("#rpanel textarea").fill("Owner confirmed ✓");
  await page.locator('#rpanel input[value="closed"]').click();
  await expect(page.locator("#rpanel")).not.toHaveAttribute("data-risk", risk);
  await expect(page.locator("#risk-category")).toBeFocused();
  await expect(page.locator(".riskrow")).toHaveCount(21);
  await page.locator("#rk-closed").check();
  await expect(page.locator("#rk-closed")).toBeFocused();
  await expect(page.locator(".riskrow")).toHaveCount(22);
  await page.locator("#risk-row-" + risk).click();
  await expect(page.locator("#risk-row-" + risk)).toBeFocused();
  await expect(page.locator("#rpanel textarea")).toHaveValue("Owner confirmed ✓");
  await page.reload();
  await page.locator("#rk-closed").check();
  await page.locator("#risk-row-" + risk).click();
  await expect(page.locator("#rpanel textarea")).toHaveValue("Owner confirmed ✓");
  await page.locator("#rail button").filter({ hasText: /^Discovery$/ }).click();
  const feedback = JSON.parse((await bytes(page, "Export workshop feedback (JSON)")).text);
  expect(feedback.validations[`risk:${risk}`]).toMatchObject({
    likelihood: 1, impact: 1, status: "closed", note: "Owner confirmed ✓"
  });
  expect(errors).toEqual([]);
});

for (const colorScheme of ["light", "dark"]) {
  test(`handover new pages reflow, targets and screenshots (${colorScheme})`, async ({ page }, info) => {
    const errors = watch(page);
    await page.emulateMedia({ colorScheme, reducedMotion: "reduce" });
    for (const width of [1440, 320]) {
      await page.setViewportSize({ width, height: 900 });
      for (const view of ["prd", "plan", "risks"]) {
        await page.goto(`/blueprint.html#/${view}`);
        await expect(page.locator("#crumb b")).toHaveText({ prd: "PRD", plan: "Plan", risks: "Risks" }[view]);
        expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width + 1);
        const targets = await page.locator("#view button, #view input, #view select, #view summary").evaluateAll((nodes) =>
          nodes.filter((n) => n.getClientRects().length).map((n) => {
            const r = n.getBoundingClientRect();
            return { text: n.textContent || n.id, width: r.width, height: r.height };
          }));
        for (const target of targets) {
          expect.soft(target.width, `${view}: ${target.text} width`).toBeGreaterThanOrEqual(24);
          expect.soft(target.height, `${view}: ${target.text} height`).toBeGreaterThanOrEqual(24);
        }
        const screenshot = info.outputPath(`${view}-${width}-${colorScheme}.png`);
        await page.screenshot({ path: screenshot, fullPage: true });
        await info.attach(`${view}-${width}-${colorScheme}`, { path: screenshot, contentType: "image/png" });
      }
    }
    expect(errors).toEqual([]);
  });
}
