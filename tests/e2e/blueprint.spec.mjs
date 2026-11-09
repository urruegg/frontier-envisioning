// Browser tests (gate L2): the showcase site in Chromium, served with the hosting headers
// (tools/serve_site.py), so a Content-Security-Policy violation or a script error fails the test.
// Run: python tools/dev.py site e2e   (needs: npm install && npx playwright install chromium)
import { test, expect } from "@playwright/test";

const VIEWS = ["Overview", "Org model", "Blueprint", "Journeys", "Attendees", "Agents", "Agent identity", "Target architecture",
  "Use cases", "IT readiness", "FinOps", "Discovery", "Roadmap", "Evidence"];

function watchProblems(page) {
  const problems = [];
  page.on("pageerror", (e) => problems.push(`page error: ${e.message}`));
  page.on("console", (m) => { if (m.type() === "error") problems.push(`console: ${m.text()}`); });
  return problems;
}

async function go(page, hash) {
  await page.evaluate((h) => { window.location.hash = h; }, hash);
  await page.waitForFunction((h) => window.location.hash === h, hash);
}

test("landing page links to the blueprint, the catalogue and the plugin", async ({ page }) => {
  const problems = watchProblems(page);
  const response = await page.goto("/index.html");
  expect(response.status()).toBe(200);
  expect(response.headers()["content-security-policy"]).toContain("default-src 'none'");
  expect(response.headers()["x-content-type-options"]).toBe("nosniff");
  await expect(page.getByRole("link", { name: "Open the blueprint" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open the catalogue" })).toBeVisible();
  expect(problems).toEqual([]);
});

test("blueprint renders the 14 views in Chromium under the security policy", async ({ page }, testInfo) => {
  const problems = watchProblems(page);
  const response = await page.goto("/blueprint.html");
  expect(response.headers()["content-security-policy"]).toMatch(/script-src 'sha256-[A-Za-z0-9+/=]+'/);
  const rail = page.locator("#rail button");
  await expect(rail).toHaveCount(VIEWS.length);
  await expect(rail).toHaveText(VIEWS);
  for (let i = 0; i < VIEWS.length; i++) {
    await rail.nth(i).click();
    const view = page.locator("#view");
    await expect(view).not.toBeEmpty();
    await expect(view.locator(".empty")).toHaveCount(0);
    await testInfo.attach(`${String(i + 1).padStart(2, "0")} ${VIEWS[i]}`, {
      body: await page.screenshot({ fullPage: true }),
      contentType: "image/png"
    });
  }
  expect(problems).toEqual([]);
});

test("landing zone, use case deep link and workshop notes", async ({ page }) => {
  const problems = watchProblems(page);
  await page.goto("/blueprint.html");
  await go(page, "#/architecture");
  await expect(page.locator("svg.lzsvg .lzhot")).toHaveCount(20);
  await go(page, "#/usecases/UC09");
  await expect(page.locator(".uchead h2")).toHaveText("Voice-to-service report");
  await go(page, "#/readiness");
  const group = page.locator("details.rgroup").first();
  await group.evaluate((d) => { d.open = true; });
  await group.locator('.assbox input[value="done"]').first().check({ force: true });
  const notes = await page.evaluate(() => Object.keys(localStorage).map((k) => localStorage.getItem(k)).join(" "));
  expect(notes).toContain("val|ready|");
  expect(problems).toEqual([]);
});

test("agent identity catalogue renders under its policy", async ({ page }) => {
  const problems = watchProblems(page);
  const response = await page.goto("/identity-catalogue.html");
  expect(response.status()).toBe(200);
  await expect(page.locator("body")).toContainText("Caldova");
  expect(problems).toEqual([]);
});
