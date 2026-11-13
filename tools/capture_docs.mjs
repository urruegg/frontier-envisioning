// Real offline Caldova captures. Screenshots are evidence, not cross-platform pixel goldens.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";
import { chromium } from "@playwright/test";

const require = createRequire(import.meta.url);
const args = process.argv.slice(2);
const input = args.indexOf("--html"), output = args.indexOf("--out");
if (input < 0 || output < 0 || !args[input + 1] || !args[output + 1]) {
  throw new Error("Usage: node tools/capture_docs.mjs --html <core.html> --out <images>");
}
const file = path.resolve(args[input + 1]), folder = path.resolve(args[output + 1]);
const views = [
  ["overview", "#/overview", "Overview"],
  ["org-model", "#/org", "Org model"],
  ["agents", "#/agents/D3-A05", "Agents"],
  ["agent-identity", "#/identity", "Agent identity"],
  ["ontology", "#/ontology", "Ontology"],
  ["landing-zone", "#/architecture", "Target architecture", "lz"],
  ["architecture-layers", "#/architecture", "Target architecture", "layers"],
  ["discovery", "#/discovery", "Discovery"],
  ["risks", "#/risks", "Risks"],
  ["evidence", "#/evidence", "Evidence"]
];
const browser = await chromium.launch();
try {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1000 }, colorScheme: "light",
    reducedMotion: "reduce", locale: "en-GB", timezoneId: "UTC", deviceScaleFactor: 1
  });
  const problems = [], screenshots = [];
  await context.route(/^https?:/, async (route) => {
    problems.push("External resource requested: " + route.request().url());
    await route.abort();
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => problems.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") problems.push(message.text()); });
  fs.mkdirSync(folder, { recursive: true });
  for (const [name, hash, label, tab] of views) {
    await page.goto(pathToFileURL(file).href + hash);
    await page.waitForFunction((wanted) => document.querySelector("#crumb b")?.textContent === wanted, label);
    await page.locator("#view").waitFor();
    await page.evaluate(() => document.fonts.ready);
    if (await page.locator("#rail button").filter({ hasText: /^FinOps/ }).count()) {
      throw new Error("The documentation sample unexpectedly includes optional FinOps");
    }
    if (name === "agents") {
      await page.locator("svg.wfsvg").waitFor();
    }
    let selectedTab;
    if (tab) {
      const tabLabel = tab === "lz" ? "Landing zone" : "Layers and integrations";
      const tabId = "architecture-tab-" + tab;
      await page.getByRole("tab", { name: tabLabel, exact: true }).click();
      await page.waitForFunction((id) =>
        document.getElementById(id)?.getAttribute("aria-selected") === "true", tabId);
      const active = await page.locator("#architecture-panel").getAttribute("aria-labelledby");
      if (active !== tabId) throw new Error("Architecture capture selected the wrong panel");
      selectedTab = active.replace("architecture-tab-", "");
    }
    const content = {
      "landing-zone": ".lzfig svg", "architecture-layers": ".layers .layer",
      discovery: ".qgroup .q", risks: ".riskgrid", evidence: ".evstats"
    };
    if (content[name]) await page.locator(content[name]).first().waitFor();
    if (name === "evidence") await page.locator("#view tbody tr").first().waitFor();
    await page.evaluate(() => scrollTo(0, 0));
    if (name === "agent-identity") await page.locator(".idstrip").waitFor();
    if (name === "ontology") await page.locator('.onode[data-entity="Customer"]').waitFor();
    const target = path.join(folder, name + ".png");
    await page.screenshot({ path: target, animations: "disabled" });
    const row = { name, route: hash, file: path.basename(target), width: 1440, height: 1000 };
    if (selectedTab) row.selected_tab = selectedTab;
    screenshots.push(row);
  }
  if (problems.length) throw new Error(problems.join("\n"));
  console.log(JSON.stringify({
    browser: browser.version(), playwright: require("@playwright/test/package.json").version,
    viewport: { width: 1440, height: 1000 }, color_scheme: "light",
    reduced_motion: "reduce", locale: "en-GB", timezone: "UTC", screenshots
  }));
  await context.close();
} finally {
  await browser.close();
}
