// The committed sample must work as a downloaded offline file, not just on the hosted showcase.
import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const sample = path.resolve("docs", "demo", "caldova-blueprint.html");
const views = [
  ["#/overview", "Overview"], ["#/org", "Org model"], ["#/agents/D3-A05", "Agents"],
  ["#/identity", "Agent identity"], ["#/ontology", "Ontology"]
];

test("documentation Caldova download works offline across the five illustrated views", async ({ page }) => {
  const problems = [], external = [];
  page.on("pageerror", (error) => problems.push(error.message));
  page.on("console", (message) => { if (message.type() === "error") problems.push(message.text()); });
  await page.route(/^https?:/, async (route) => {
    external.push(route.request().url());
    await route.abort();
  });
  for (const [hash, label] of views) {
    await page.goto(pathToFileURL(sample).href + hash);
    await expect(page.locator("#crumb b")).toHaveText(label);
    await expect(page.locator("#view")).not.toBeEmpty();
    await expect(page.locator("#view .empty")).toHaveCount(0);
    await expect(page.locator("#rail button").filter({ hasText: /^FinOps/ })).toHaveCount(0);
  }
  const data = await page.locator("#bp-data").evaluate((node) => JSON.parse(node.textContent));
  expect(data.meta.customer).toBe("Caldova Industrial AG");
  expect(data.meta.plugin_version).toBe(JSON.parse(fs.readFileSync(path.join("plugin", ".claude-plugin", "plugin.json"), "utf8")).version);
  expect(data.finops).toBeFalsy();
  expect(data.value_case.finops_preview).toBeFalsy();
  expect(external).toEqual([]);
  expect(problems).toEqual([]);
});

test("documentation offline ontology downloads the actual generated Turtle", async ({ page }) => {
  await page.goto(pathToFileURL(sample).href + "#/ontology");
  const waiting = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download ontology.ttl", exact: true }).click();
  const download = await waiting;
  const chunks = [];
  for await (const chunk of await download.createReadStream()) chunks.push(chunk);
  expect(Buffer.concat(chunks)).toEqual(fs.readFileSync(path.join("build", "demo", "ontology", "ontology.ttl")));
  await expect(page.locator("#view")).toContainText("Native Fabric import is manual");
});
