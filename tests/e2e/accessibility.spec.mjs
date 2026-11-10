// A1 RED baseline for #7. Use the real hosting CSP and locally installed axe;
// best-practice-only findings and incomplete checks are not WCAG conformance failures.
import { test, expect } from "@playwright/test";
import axe from "axe-core";

const WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const VIEWS = ["Overview", "Org model", "Blueprint", "Journeys", "Attendees", "Agents", "Agent identity",
  "Target architecture", "Use cases", "IT readiness", "FinOps", "Discovery", "Roadmap", "Evidence"];
const ARCHITECTURE = ["Landing zone", "Layers and integrations", "Flows", "Decisions (ADRs)"];
test.setTimeout(180_000);

function watchProblems(page) {
  const problems = [];
  page.on("pageerror", (error) => problems.push(`page error: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") problems.push(`console: ${message.text()}`);
  });
  return problems;
}

async function open(page, path) {
  // Force a document navigation: hash-only page.goto otherwise returns null,
  // leaving no response whose actual hosting headers we can verify.
  await page.goto("about:blank");
  const response = await page.goto(path);
  expect.soft(response.status(), path).toBe(200);
  const policy = response.headers()["content-security-policy"];
  expect.soft(policy, `${path}: real hosting CSP`).toContain("default-src 'none'");
  if (path.startsWith("/blueprint.html")) {
    expect.soft(policy).toMatch(/script-src 'sha256-[A-Za-z0-9+/=]+'/);
    await expect(page.locator("#rail button")).toHaveText(VIEWS);
  }
}

async function scan(page, info, label) {
  // DevTools evaluation of the local source: no CDN, script tag or bypassCSP.
  await page.evaluate(axe.source);
  const report = await page.evaluate(async (tags) =>
    window.axe.run(document, { runOnly: { type: "tag", values: tags } }),
  [...WCAG, "best-practice"]);
  await info.attach(label, {
    body: Buffer.from(JSON.stringify({ violations: report.violations, incomplete: report.incomplete }, null, 2)),
    contentType: "application/json"
  });
  const applicable = report.violations.filter((rule) => rule.tags.some((tag) => WCAG.includes(tag)));
  const bestPracticeOnly = report.violations.filter((rule) => !rule.tags.some((tag) => WCAG.includes(tag)));
  const summary = {
    label,
    wcag: applicable.map((rule) => ({
      id: rule.id, nodes: rule.nodes.length, targets: rule.nodes.map((node) => node.target)
    })),
    bestPracticeOnly: bestPracticeOnly.map((rule) => ({ id: rule.id, nodes: rule.nodes.length })),
    incomplete: report.incomplete.map((rule) => ({ id: rule.id, nodes: rule.nodes.length }))
  };
  console.log(JSON.stringify(summary));
  // Soft assertions deliberately let every state run, even on a red baseline.
  expect.soft(summary.wcag, `${label}: applicable WCAG violations`).toEqual([]);
  return summary;
}

for (const colorScheme of ["light", "dark"]) {
  test(`accessibility all views, architecture, workflow, modal and site (${colorScheme})`, async ({ page }, info) => {
    await page.emulateMedia({ colorScheme });
    const problems = watchProblems(page);
    const summaries = [];
    await open(page, "/blueprint.html");
    for (let i = 0; i < VIEWS.length; i++) {
      await page.locator("#rail button").nth(i).click();
      await expect(page.locator("#crumb b")).toHaveText(VIEWS[i]);
      summaries.push(await scan(page, info, `${colorScheme}-view-${VIEWS[i]}`));
    }

    await page.locator("#rail button").filter({ hasText: "Target architecture" }).click();
    await expect(page.locator(".atabs button")).toHaveText(ARCHITECTURE);
    for (let i = 0; i < ARCHITECTURE.length; i++) {
      await page.locator(".atabs button").nth(i).click();
      await expect(page.locator(".atabs button").nth(i)).toHaveAttribute("aria-selected", "true");
      summaries.push(await scan(page, info, `${colorScheme}-architecture-${ARCHITECTURE[i]}`));
    }

    await open(page, "/blueprint.html#/agents/D3-A05");
    await expect(page.locator("svg.wfsvg .wfn")).toHaveCount(16);
    summaries.push(await scan(page, info, `${colorScheme}-service-workflow-D3-A05`));
    await page.locator("svg.wfsvg .wfn").first().focus();
    await page.keyboard.press("Enter");
    await expect(page.locator(".wfprops")).toBeVisible();
    summaries.push(await scan(page, info, `${colorScheme}-workflow-properties`));

    await open(page, "/blueprint.html#/evidence");
    await page.locator("#view .pill.ev").first().click();
    await expect(page.locator("#drawer")).toHaveAttribute("aria-hidden", "false");
    await expect(page.locator("#drawer-close")).toBeFocused();
    summaries.push(await scan(page, info, `${colorScheme}-evidence-modal`));
    for (const path of ["/index.html", "/identity-catalogue.html"]) {
      await open(page, path);
      summaries.push(await scan(page, info, `${colorScheme}-${path.slice(1)}`));
    }
    await info.attach(`${colorScheme}-scan-summary`, {
      body: Buffer.from(JSON.stringify({ summaries, problems }, null, 2)),
      contentType: "application/json"
    });
    expect(summaries).toHaveLength(23);
    expect(problems, "page errors and CSP/console errors").toEqual([]);
  });
}

test("closed evidence drawer is outside the real Tab sequence after the pager", async ({ page }) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/evidence");
  await page.locator("#view .pager button").last().focus();
  await page.keyboard.press("Tab");
  expect(await page.evaluate(() => !!document.activeElement.closest("#drawer"))).toBe(false);
  expect(problems).toEqual([]);
});

test("evidence drawer traps Shift+Tab and Tab, then Escape restores the exact trigger", async ({ page }) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/evidence");
  const trigger = page.locator("#view .pill.ev").first();
  await trigger.click();
  const close = page.locator("#drawer-close");
  await expect.soft(close).toBeFocused();
  expect.soft(await page.locator(".page,.rail,.skip").evaluateAll((nodes) =>
    nodes.every((node) => node.inert)), "background must be inert while modal is open").toBe(true);
  await page.keyboard.press("Shift+Tab");
  expect.soft(await page.evaluate(() => !!document.activeElement.closest("#drawer")),
    "reverse Tab must remain inside modal").toBe(true);
  // Independently exercise the forward boundary, even if reverse Tab escaped.
  await close.focus();
  await page.keyboard.press("Tab");
  expect.soft(await page.evaluate(() => !!document.activeElement.closest("#drawer")),
    "forward Tab must remain inside modal").toBe(true);
  await page.keyboard.press("Escape");
  await expect.soft(page.locator("#drawer")).toHaveAttribute("aria-hidden", "true");
  await expect.soft(trigger).toBeFocused();
  expect.soft(await page.locator(".page,.rail,.skip").evaluateAll((nodes) =>
    nodes.some((node) => node.inert)), "Escape removes background inert").toBe(false);
  expect(problems).toEqual([]);
});

test("evidence drawer Escape preserves an already inert rail through repeated opens", async ({ page }) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/evidence");
  await page.locator("#rail").evaluate((node) => { node.inert = true; });
  const trigger = page.locator("#view .pill.ev").first();
  for (const repeat of [false, true]) {
    await trigger.click();
    if (repeat) await trigger.evaluate((node) => node.click());
    expect(await page.locator(".page,.rail,.skip").evaluateAll((nodes) => nodes.every((node) => node.inert))).toBe(true);
    await page.keyboard.press("Escape");
    await expect(page.locator("#drawer")).toHaveAttribute("aria-hidden", "true");
    await expect(page.locator("#rail")).toHaveJSProperty("inert", true);
    await expect(page.locator(".page")).toHaveJSProperty("inert", false);
    await expect(page.locator(".skip")).toHaveJSProperty("inert", false);
    await expect(trigger).toBeFocused();
  }
  expect(problems).toEqual([]);
});

test("drawer replacement preserves the outer trigger and prior inert state through role profile navigation", async ({ page }, info) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/finops");
  await page.locator("#rail").evaluate((node) => { node.inert = true; });
  const trigger = page.locator("#view .agentlink").first();
  await trigger.click();
  await page.locator("#drawer").getByRole("button", { name: "Open role profile", exact: true }).click();
  await expect(page.locator("#drawer-title")).toContainText("role profile");
  await expect(page.locator("#drawer-close")).toBeFocused();
  await info.attach("a2-role-profile-dialog", { body: await page.screenshot(), contentType: "image/png" });
  await page.keyboard.press("Escape");
  await expect(trigger).toBeFocused();
  await expect(page.locator("#rail")).toHaveJSProperty("inert", true);
  await expect(page.locator(".page")).toHaveJSProperty("inert", false);
  await expect(page.locator(".skip")).toHaveJSProperty("inert", false);
  expect(problems).toEqual([]);
});

test("drawer Tab stops exclude hidden, invisible, disabled and inert controls", async ({ page }) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/evidence");
  await page.locator("#view .pill.ev").first().click();
  await page.locator("#drawer-body").evaluate((body) => {
    function button(id, parent = body) {
      const node = document.createElement("button");
      node.id = id;
      node.textContent = id;
      parent.append(node);
      return node;
    }
    button("first-stop");
    button("last-stop");
    button("negative-stop").tabIndex = -1;
    button("invisible-stop").style.visibility = "hidden";
    button("disabled-stop").disabled = true;
    const hidden = document.createElement("div");
    hidden.hidden = true;
    body.append(hidden);
    button("hidden-stop", hidden);
    const inert = document.createElement("div");
    inert.inert = true;
    body.append(inert);
    button("inert-stop", inert);
    const disabled = document.createElement("fieldset");
    disabled.disabled = true;
    body.append(disabled);
    button("fieldset-stop", disabled);
  });
  await page.keyboard.press("Shift+Tab");
  await expect(page.locator("#last-stop")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.locator("#drawer-close")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.locator("#first-stop")).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.locator("#last-stop")).toBeFocused();
  await page.keyboard.press("Escape");
  expect(problems).toEqual([]);
});

test("drawer Escape falls back to the view when its trigger is no longer focusable", async ({ page }) => {
  const problems = watchProblems(page);
  for (const reason of ["removed", "disabled", "hidden", "inert", "invisible"]) {
    await open(page, "/blueprint.html#/evidence");
    const trigger = page.locator("#view .pill.ev").first();
    await trigger.click();
    await trigger.evaluate((node, why) => {
      if (why === "removed") node.remove();
      if (why === "disabled") node.disabled = true;
      if (why === "hidden") node.hidden = true;
      if (why === "inert") node.inert = true;
      if (why === "invisible") node.style.visibility = "hidden";
    }, reason);
    await page.keyboard.press("Escape");
    await expect(page.locator("#view"), reason).toBeFocused();
    expect(await page.locator(".page,.rail,.skip").evaluateAll((nodes) => nodes.some((node) => node.inert)),
      `${reason}: no frozen background`).toBe(false);
  }
  expect(problems).toEqual([]);
});

test("drawer rapid close and reopen cancels the delayed hide and scrim close restores focus", async ({ page }) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/evidence");
  await page.locator("#rail").evaluate((node) => { node.inert = true; });
  await page.locator("#view .pill.ev").first().evaluate((trigger) => {
    trigger.focus();
    trigger.click();
    document.getElementById("drawer-close").click();
    document.getElementById("drawer-close").click();
    trigger.click();
  });
  // Observe beyond the normal close timer: the reopened dialog must not be hidden.
  await page.waitForTimeout(250);
  await expect(page.locator("#drawer")).toBeVisible();
  expect(await page.locator("#drawer").evaluate((node) => node.inert)).toBe(false);
  await expect(page.locator("#drawer-close")).toBeFocused();
  await page.locator("#scrim").click({ position: { x: 10, y: 10 } });
  await expect(page.locator("#view .pill.ev").first()).toBeFocused();
  await expect(page.locator("#drawer")).toHaveJSProperty("hidden", true);
  await expect(page.locator("#rail")).toHaveJSProperty("inert", true);
  await expect(page.locator(".page")).toHaveJSProperty("inert", false);
  await expect(page.locator(".skip")).toHaveJSProperty("inert", false);
  expect(problems).toEqual([]);
});

for (const reducedMotion of ["no-preference", "reduce"]) {
  test(`drawer close preserves normal motion and hides instantly for reduced motion (${reducedMotion})`, async ({ page }) => {
    const problems = watchProblems(page);
    await page.emulateMedia({ reducedMotion });
    await open(page, "/blueprint.html#/evidence");
    const trigger = page.locator("#view .pill.ev").first();
    await trigger.click();
    const durations = await page.locator("#drawer,#scrim").evaluateAll((nodes) =>
      nodes.map((node) => parseFloat(getComputedStyle(node).transitionDuration)));
    expect(durations.every((duration) => reducedMotion === "reduce" ? duration === 0 : duration > 0)).toBe(true);
    const closing = await page.locator("#drawer-close").evaluate((button) => {
      button.click();
      const drawer = document.getElementById("drawer");
      return { hidden: drawer.hidden, inert: drawer.inert, ariaHidden: drawer.getAttribute("aria-hidden") };
    });
    expect(closing).toEqual({ hidden: reducedMotion === "reduce", inert: true, ariaHidden: "true" });
    await expect(trigger).toBeFocused();
    await expect(page.locator("#drawer")).toHaveJSProperty("hidden", true);
    expect(problems).toEqual([]);
  });
}

async function tabState(page, selector, panelId, index) {
  const tabs = page.locator(`${selector} [role=tab]`);
  const count = await tabs.count();
  expect(count).toBeGreaterThan(1);
  for (let i = 0; i < count; i++) {
    await expect(tabs.nth(i)).toHaveAttribute("aria-controls", panelId);
    await expect(tabs.nth(i)).toHaveAttribute("aria-selected", String(i === index));
    await expect(tabs.nth(i)).toHaveAttribute("tabindex", i === index ? "0" : "-1");
  }
  const selected = tabs.nth(index);
  const panel = page.locator(`#${panelId}`);
  await expect(panel).toHaveAttribute("role", "tabpanel");
  await expect(panel).toHaveAttribute("aria-labelledby", await selected.getAttribute("id"));
  await expect(panel).toHaveAccessibleName(/\S/);
  await expect(selected).toBeFocused();
}

for (const route of ["blueprint", "journeys", "agents", "discovery"]) {
  test(`journey tabs keep the ${route} route, roving focus and labelled panel`, async ({ page }) => {
    const problems = watchProblems(page);
    await open(page, route === "agents" ? "/blueprint.html#/agents/D3-A05" : `/blueprint.html#/${route}/D1`);
    const tabs = page.locator("#subnav [role=tab]");
    const count = await tabs.count();
    const start = route === "agents" ? 2 : 0;
    const expectedUrl = (index) => route === "agents"
      ? new RegExp(`#/agents/D${index + 1}-`)
      : new RegExp(`#/${route}/D${index + 1}$`);
    await tabs.nth(start).click();
    await tabState(page, "#subnav", "journey-panel", start);
    await expect(page).toHaveURL(expectedUrl(start));
    for (const [key, index] of [["ArrowRight", (start + 1) % count], ["Home", 0], ["ArrowLeft", count - 1], ["ArrowRight", 0], ["End", count - 1]]) {
      await page.keyboard.press(key);
      await tabState(page, "#subnav", "journey-panel", index);
      await expect(page).toHaveURL(expectedUrl(index));
    }
    // Only the active journey participates in the real Tab sequence.
    await page.keyboard.press("Tab");
    expect(await page.evaluate(() => !!document.activeElement.closest("#subnav"))).toBe(false);
    await page.keyboard.press("Shift+Tab");
    await expect(tabs.last()).toBeFocused();
    expect(problems).toEqual([]);
  });
}

for (const family of ["architecture", "factory"]) {
  test(`${family} tabs keep the page, activate Arrow/Home/End and label selected content`, async ({ page }, info) => {
    const problems = watchProblems(page);
    await open(page, family === "architecture" ? "/blueprint.html#/architecture" : "/blueprint.html#/journeys/D1");
    if (family === "factory") {
      // Select the actual Factory journey, not whichever journey the default opens.
      await page.locator("#subnav [role=tab]").filter({ hasText: /factory/i }).click();
    }
    const selector = family === "architecture" ? ".atabs" : ".fsteps";
    const panelId = family === "architecture" ? "architecture-panel" : "factory-step-panel";
    const tabs = page.locator(`${selector} [role=tab]`);
    const count = await tabs.count();
    const url = page.url();
    await tabs.first().click();
    await tabState(page, selector, panelId, 0);
    const ids = await tabs.evaluateAll((nodes) => nodes.map((node) => node.id));
    for (const [key, index] of [["ArrowRight", 1], ["Home", 0], ["ArrowLeft", count - 1], ["ArrowRight", 0], ["End", count - 1]]) {
      await page.keyboard.press(key);
      await tabState(page, selector, panelId, index);
      await expect(page).toHaveURL(url);
      expect(await tabs.evaluateAll((nodes) => nodes.map((node) => node.id))).toEqual(ids);
    }
    // Enter/Space remain native button activation, not document shortcuts.
    for (const key of ["Enter", "Space"]) {
      await tabs.first().focus();
      await page.keyboard.press(key);
      await tabState(page, selector, panelId, 0);
    }
    await info.attach(`a3-${family}-selected-panel`, { body: await page.screenshot(), contentType: "image/png" });
    expect(problems).toEqual([]);
  });
}

test("tab navigation preserves modifiers, input guards, drawer priority and global view shortcuts", async ({ page }) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/blueprint/D1");
  const first = page.locator("#subnav [role=tab]").first();
  await first.click();
  for (const modifier of ["Alt", "Control", "Meta"]) {
    await page.keyboard.press(`${modifier}+ArrowRight`);
    await tabState(page, "#subnav", "journey-panel", 0);
    await expect(page).toHaveURL(/#\/blueprint\/D1$/);
  }
  await page.locator("#view .leadcard").click();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#drawer-close")).toBeFocused();
  await expect(page).toHaveURL(/#\/blueprint\/D1$/);
  await page.keyboard.press("Escape");
  await page.locator("#view").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page).toHaveURL(/#\/journeys\/D1$/);
  await page.keyboard.press("ArrowLeft");
  await expect(page).toHaveURL(/#\/blueprint\/D1$/);
  await open(page, "/blueprint.html#/readiness");
  const input = page.locator("details.rgroup[open] .assnote").first();
  await input.focus();
  await page.keyboard.press("ArrowRight");
  await expect(page).toHaveURL(/#\/readiness$/);
  await expect(input).toBeFocused();
  expect(problems).toEqual([]);
});

test("organisation and ADR filters expose pressed state and interactive SVG groups retain keyboard nodes", async ({ page }, info) => {
  const problems = watchProblems(page);
  await open(page, "/blueprint.html#/org");
  const org = page.locator("svg.orgsvg");
  await expect(org).toHaveAttribute("role", "group");
  await expect(org).toHaveAccessibleName(/Hybrid organisation model/);
  expect(await org.getByRole("button").count()).toBeGreaterThan(1);
  const filters = page.locator("#view .filters button");
  await expect(filters.first()).toHaveAttribute("aria-pressed", "true");
  const inactiveColour = await filters.nth(1).evaluate((node) => getComputedStyle(node).backgroundColor);
  await filters.nth(1).click();
  await expect(filters.nth(1)).toHaveAttribute("aria-pressed", "true");
  await expect(filters.first()).toHaveAttribute("aria-pressed", "false");
  expect(await filters.nth(1).evaluate((node) => getComputedStyle(node).backgroundColor)).not.toBe(inactiveColour);
  await filters.nth(1).click();
  await org.getByRole("button").first().focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("#drawer")).toHaveAttribute("aria-hidden", "false");
  await page.keyboard.press("Escape");
  await info.attach("a3-org-filter-and-svg", { body: await page.screenshot(), contentType: "image/png" });
  await open(page, "/blueprint.html#/usecases");
  const matrix = page.locator("svg.matrix");
  await expect(matrix).toHaveAttribute("role", "group");
  await expect(matrix).toHaveAccessibleName(/\S/);
  expect(await matrix.getByRole("button").count()).toBeGreaterThan(1);
  await matrix.getByRole("button").first().focus();
  await page.keyboard.press("Space");
  await expect(page.locator("#ucdetail")).toBeVisible();
  await open(page, "/blueprint.html#/architecture");
  await page.locator(".atabs button").filter({ hasText: "Decisions" }).click();
  await expect(filters.first()).toHaveAttribute("aria-pressed", "true");
  await filters.nth(1).click();
  await expect(filters.nth(1)).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator('button:not([role=tab])[aria-selected]')).toHaveCount(0);
  expect(problems).toEqual([]);
});

test("all 14 views reflow at 320 CSS pixels without document overflow", async ({ page }, info) => {
  await page.setViewportSize({ width: 320, height: 900 });
  const problems = watchProblems(page);
  await open(page, "/blueprint.html");
  const widths = [];
  for (let i = 0; i < VIEWS.length; i++) {
    await page.locator("#rail button").nth(i).click();
    await expect(page.locator("#crumb b")).toHaveText(VIEWS[i]);
    // Diagram-local scrolling is allowed, but never excuses page overflow.
    const width = await page.evaluate(() => document.documentElement.scrollWidth);
    widths.push({ view: VIEWS[i], width });
    expect.soft(width, VIEWS[i]).toBeLessThanOrEqual(321);
  }
  console.log(JSON.stringify({ reflow: widths }));
  await info.attach("all-views-320px-document-widths", {
    body: Buffer.from(JSON.stringify(widths, null, 2)), contentType: "application/json"
  });
  expect(problems).toEqual([]);
});
