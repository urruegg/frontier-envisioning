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

test("journey tabs keep the blueprint route and activate/focus ArrowRight, Home and End destinations", async ({ page }) => {
  const problems = watchProblems(page);
  for (const key of ["ArrowRight", "Home", "End"]) {
    // Reset each scenario so a broken ArrowRight cannot mask Home/End.
    await open(page, "/blueprint.html#/blueprint");
    const tabs = page.locator("#subnav [role=tab]");
    expect(await tabs.count()).toBeGreaterThan(1);
    await (key === "Home" ? tabs.last() : tabs.first()).focus();
    await page.keyboard.press(key);
    expect.soft(page.url(), `${key}: route`).toMatch(/#\/blueprint\//);
    const destination = key === "ArrowRight" ? tabs.nth(1) : key === "Home" ? tabs.first() : tabs.last();
    await expect.soft(destination, `${key}: focus`).toBeFocused();
    await expect.soft(destination, `${key}: activation`).toHaveAttribute("aria-selected", "true");
  }
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
