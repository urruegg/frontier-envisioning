import { test, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import net from "node:net";
import { spawn, execFileSync } from "node:child_process";
import { once } from "node:events";
import axe from "axe-core";

const ROOT = process.cwd();
const EVIDENCE = path.resolve("build/evidence/task6");
const python = process.platform === "win32" ? "python" : "python3";
const ack = (page) => page.locator("#finops-preview-ack").click();
const hash = (page, route) => page.evaluate((r) => { location.hash = "#/" + r; }, route);

function watch(page) {
  const problems = [], external = [];
  page.on("pageerror", (e) => problems.push(e.message));
  page.on("console", (m) => { if (m.type() === "error") problems.push(m.text()); });
  page.on("request", (r) => {
    if (/^https?:/.test(r.url()) && !/^http:\/\/127\.0\.0\.1:\d+\//.test(r.url())) external.push(r.url());
  });
  return { problems, external };
}
async function open(page, url = "/blueprint-baseline.html#/finops") {
  const response = await page.goto(url);
  expect(response.status()).toBe(200);
  const csp = response.headers()["content-security-policy"];
  expect(csp).toContain("default-src 'none'");
  expect(csp).toMatch(/script-src 'sha256-[A-Za-z0-9+/=]+'/);
  expect(csp).not.toContain("'unsafe-eval'");
  return response;
}
async function download(page, label, saveName) {
  const event = page.waitForEvent("download");
  await page.getByRole("button", { name: label, exact: true }).click();
  const d = await event, chunks = [];
  for await (const chunk of await d.createReadStream()) chunks.push(chunk);
  const bytes = Buffer.concat(chunks);
  if (saveName) { fs.mkdirSync(EVIDENCE, { recursive: true }); await d.saveAs(path.join(EVIDENCE, saveName)); }
  return bytes.toString("utf8");
}
async function scan(page) {
  await page.evaluate(axe.source);
  const results = await page.evaluate(async () => window.axe.run(document, {
    runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] }
  }));
  expect(results.violations).toEqual([]);
}
async function screenshot(page, info, name) {
  fs.mkdirSync(EVIDENCE, { recursive: true });
  const file = path.join(EVIDENCE, name + ".png");
  await page.screenshot({ path: file, fullPage: true });
  await info.attach(name, { path: file, contentType: "image/png" });
}

test("Task6 real successor gates financial exports, preserves independent value, downloads exact DTO and renews acknowledgement", async ({ page }) => {
  const watched = watch(page);
  await open(page);
  await expect(page.locator("#rail button")).toHaveCount(18);
  await expect(page.locator(".baseline-scenario, .baseline-export, .baseline-proposal textarea")).toHaveCount(0);
  await expect(page.locator("#view")).not.toContainText(/1320\.00|1\.100000|synthetic:task1/);
  await hash(page, "usecases");
  await expect(page.locator("#view")).toContainText("CHF 8.21M");
  await hash(page, "prd");
  const independent = await download(page, "Download the PRD (Markdown)");
  expect(independent).toContain("NPV CHF 7.22M");
  await hash(page, "finops");
  await ack(page);
  const dto = await page.locator("#bp-data").evaluate((n) => JSON.parse(n.textContent).agent_finops.records[0]);
  await expect(page.locator(".baseline-scenario")).toHaveCount(3);
  await expect(page.locator(".baseline-months tbody tr")).toHaveCount(36);
  const json = JSON.parse(await download(page, "Download projected report JSON", "projected-report.json"));
  expect(json).toEqual(dto);
  expect(json.financial_permission).toBe(false);
  expect(json.handover.ready).toBe(false);
  const actualLine = json.scenarios.expected.months[0].lines[0];
  expect(actualLine.cost.status).toBe("provisional");
  expect(actualLine.pricing_evidence.records[0].verification_status).toBe("synthetic");
  expect(actualLine.pricing_evidence.records[0].source_status).toBe("synthetic");
  const md = await download(page, "Download projected report Markdown", "projected-report.md");
  for (const token of ["Preview", "1320.00", "1.100000", "2026-11-12", "CHF", "formulas", "gaps", "handover", "not authenticated"]) expect(md).toContain(token);
  await page.locator(".baseline-proposal textarea").fill("Approved CHF 999.123 café ✓ — proposal only");
  await hash(page, "agents/D3-A05");
  await page.locator('.agrest .valbox input[value="validated"]').check();
  await expect(page.locator(".financial-summary")).toHaveAttribute("data-financial-ready", "false");
  await page.evaluate(() => {
    localStorage.setItem("finopsAcknowledged", "true");
    const key = Object.keys(localStorage).find((k) => k.startsWith("fbp:"));
    if (!key) throw new Error("Expected actual workshop-note storage");
    const notes = JSON.parse(localStorage.getItem(key));
    notes["val|finops|model"] = { status: "approved", note: "Raw approved status is not review." };
    notes["val|cost|D3-A05"] = { status: "validated" };
    localStorage.setItem(key, JSON.stringify(notes));
  });
  await page.reload();
  await expect(page.locator(".financial-summary")).toHaveAttribute("data-financial-ready", "false");
  await hash(page, "discovery");
  const before = await download(page, "Export workshop feedback (JSON)");
  expect(before).not.toContain("999.123");
  expect(JSON.parse(before).validations["finops:baseline-D3-A05"].note).toContain("withheld");
  await hash(page, "finops");
  await expect(page.locator("#finops-preview-ack")).toBeVisible();
  await expect(page.locator(".baseline-export, .baseline-proposal textarea")).toHaveCount(0);
  await ack(page);
  await expect(page.locator(".baseline-proposal textarea")).toHaveValue("Approved CHF 999.123 café ✓ — proposal only");
  await hash(page, "discovery");
  const after = await download(page, "Export workshop feedback (JSON)", "draft-proposal-feedback.json");
  expect(after).toContain("999.123");
  expect(after).toContain("new draft only; not financial approval");
  expect(watched).toEqual({ problems: [], external: [] });
});

for (const colorScheme of ["light", "dark"]) {
  test(`Task6 real FinOps and financial summary keyboard, accessibility and reflow (${colorScheme})`, async ({ page }, info) => {
    test.setTimeout(180_000);
    const watched = watch(page);
    await page.emulateMedia({ colorScheme });
    await open(page);
    await scan(page);
    await page.locator("#finops-preview-ack").focus();
    await page.keyboard.press("Enter");
    await expect(page.locator("#view")).toBeFocused();
    await expect(page.locator(".preview-notice")).toContainText("Frontier FinOps is Preview.");
    await expect(page.locator('.baseline-scenario[data-scenario="expected"]')).toContainText("CHF 1320.00");
    const evidence = page.locator(".baseline-details").filter({ has: page.locator("summary", { hasText: "Inspect projected sources, rates and FX" }) });
    await evidence.locator("summary").click();
    for (const token of ["RATE-TOKENS", "invented-tokens", "effective_from", "verified_at"]) await expect(evidence).toContainText(token);
    await scan(page);
    await screenshot(page, info, `baseline-finops-${colorScheme}`);
    for (const width of [1440, 320]) {
      await page.setViewportSize({ width, height: 900 });
      await scan(page);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
      const region = page.locator(".baseline-scenario .tscroll").first();
      await region.focus(); await page.keyboard.press("ArrowRight");
      await expect(region).toBeFocused();
      await expect(page).toHaveURL(/#\/finops$/);
      const details = page.locator(".baseline-details").first();
      await details.locator("summary").focus(); await page.keyboard.press("Enter");
      await expect(details).toHaveAttribute("open", "");
      await scan(page);
      await page.keyboard.press("Enter");
    }
    await page.setViewportSize({ width: 1440, height: 900 });
    await hash(page, "agents/D3-A05");
    await expect(page.locator(".financial-summary")).toContainText("Financial handover gap");
    await scan(page);
    await screenshot(page, info, `agent-financial-summary-${colorScheme}`);
    await page.setViewportSize({ width: 320, height: 900 });
    await scan(page);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true);
    await page.locator(".financial-summary button").focus();
    await page.keyboard.press("Enter");
    await expect(page).toHaveURL(/#\/finops$/);
    await expect(page.locator(".baseline-scenario")).toHaveCount(3);
    await page.reload();
    await expect(page.locator("#finops-preview-ack")).toBeVisible();
    await expect(page.locator(".baseline-export")).toHaveCount(0);
    expect(watched).toEqual({ problems: [], external: [] });
  });
}

// Real producer/builder/hosting policy, not page.route HTML replacement or a
// mocked financial DTO. Variants remain synthetic, blocked and test-only.
function buildVariants() {
  const script = String.raw`
import copy, json, re, subprocess, sys
from pathlib import Path
root = Path.cwd()
sys.path.insert(0, str(root / "tools"))
import build_site
out = root / "build/evidence/task6/browser-variants"
out.mkdir(parents=True, exist_ok=True)
html_name = "Frontier Company Blueprint - Template (Caldova sample).html"
core = (root / "build/demo" / html_name).read_text(encoding="utf-8")
data = json.loads(re.search(r'<script[^>]+id="bp-data"[^>]*>(.*?)</script>', core, re.S)[1])
assert "finops" not in data and "agent_finops" not in data
core_path = out / "core-input.json"
core_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
original = json.loads((root / "plugin/skills/frontier-finops/examples/caldova-agent-baseline.json").read_text(encoding="utf-8"))
sites = {}
for kind in ("private", "unpriced", "all-unpriced"):
    model = copy.deepcopy(original)
    if kind == "private":
        model["profile"]["sharingClassification"] = "internal-only"
        model["profile"]["name"] = "PRIVATE-PROFILE-TASK6"
        model["baseline"]["id"] = "PRIVATE-TARGET-TASK6"
    else:
        for rate in (model["rates"] if kind == "all-unpriced" else model["rates"][:1]):
            rate["amount"] = None
    model_path = out / (kind + "-input.json")
    model_path.write_text(json.dumps(model, ensure_ascii=False), encoding="utf-8")
    fixture = out / kind / "demo"
    command = [sys.executable, "-B", str(root / "plugin/skills/frontier-blueprint/scripts/build_blueprint.py"),
        "--data", str(core_path), "--out", str(fixture / html_name), "--agent-finops", str(model_path),
        "--as-of", "2026-11-12", "--audience", "customer" if kind == "private" else "internal",
        "--customer-scope", "synthetic-caldova", "--acknowledge-finops-preview"]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    site = out / kind / "site"
    build_site.build(site, root / "build/demo", "none", None, baseline_demo=fixture)
    sites[kind] = str(site)
print(json.dumps(sites))
`;
  return JSON.parse(execFileSync(python, ["-B", "-c", script], { cwd: ROOT, encoding: "utf8", timeout: 60_000 }).trim());
}
async function serve(site, page, run) {
  const reservation = net.createServer();
  await new Promise((resolve) => reservation.listen(0, "127.0.0.1", resolve));
  const port = reservation.address().port;
  await new Promise((resolve) => reservation.close(resolve));
  const child = spawn(python, ["-B", "tools/serve_site.py", "--dir", site, "--port", String(port)],
    { cwd: ROOT, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] });
  const exited = once(child, "exit");
  try {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error("Local variant server did not become ready")), 30_000);
      child.once("error", reject);
      child.stdout.on("data", (chunk) => { if (String(chunk).includes("serving ")) { clearTimeout(timer); resolve(); } });
    });
    const origin = `http://127.0.0.1:${port}`;
    expect((await page.request.get(origin + "/index.html")).status()).toBe(200);
    await run(origin);
  } finally {
    if (child.exitCode === null) {
      if (process.platform === "win32") execFileSync("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command", `Stop-Process -Id ${child.pid} -ErrorAction SilentlyContinue`]);
      else child.kill();
    }
    await exited;
  }
}

test("Task6 real private/unpriced producer outputs show supplied known subtotals and remain blocked, with no private download remainder", async ({ page }, info) => {
  test.setTimeout(180_000);
  const watched = watch(page), sites = buildVariants();
  for (const kind of ["private", "unpriced", "all-unpriced"]) await serve(sites[kind], page, async (origin) => {
    await open(page, origin + "/blueprint-baseline.html#/finops");
    await expect(page.locator(".baseline-export, .baseline-scenario")).toHaveCount(0);
    await ack(page);
    const jsonText = await download(page, "Download projected report JSON", `${kind}-projected-report.json`);
    const md = await download(page, "Download projected report Markdown", `${kind}-projected-report.md`);
    const r = JSON.parse(jsonText);
    expect(r.handover.ready).toBe(false);
    expect(r.financial_permission).toBe(false);
    if (kind === "private") {
      expect(r.agent_id).toBe(null);
      expect(r.baseline).toBe(null);
      expect(r.scenarios).toEqual({});
      expect(jsonText + md + await page.locator("#view").innerText()).not.toMatch(/PRIVATE-PROFILE-TASK6|PRIVATE-TARGET-TASK6|material_hash|1320\.00/);
    } else {
      expect(r.scenarios.expected.annual_recurring.amount).toBe(null);
      const expected = page.locator('.baseline-scenario[data-scenario="expected"]');
      await expect(expected).toContainText("incomplete-cost");
      expect(r.gaps.some((g) => g.code === "unpriced")).toBe(true);
      const annual = expected.locator(".baseline-contributions .baseline-known").first();
      await expect(annual).toBeVisible();
      await expect(annual).toContainText("Known-priced subtotal · not full cost");
      await expect(expected.locator(".grid3 > div > .baseline-money").first()).toContainText("Unavailable");
      const headers = await expected.locator(".baseline-months th").allTextContents();
      const index = headers.findIndex((text) => text.includes("Known-priced subtotal"));
      expect(index).toBeGreaterThan(-1);
      const monthly = expected.locator(".baseline-months tbody tr").first().locator("td").nth(index);
      if (kind === "unpriced") {
        expect(r.scenarios.expected.annual_recurring.known_priced_subtotal.amount).toBe("120.00");
        await expect(annual).toContainText("CHF 120.00");
        await expect(annual).toContainText("provisional");
        await expect(annual).toContainText("pricing-evidence-incomplete");
        await expect(monthly).toContainText("CHF 10.00");
        await expect(monthly).toContainText("provisional");
        const file = path.join(EVIDENCE, "unpriced-known-priced-subtotals.png");
        await expected.screenshot({ path: file });
        await info.attach("unpriced-known-priced-subtotals", { path: file, contentType: "image/png" });
      } else {
        expect(r.scenarios.expected.annual_recurring.known_priced_subtotal.amount).toBe(null);
        await expect(annual).toContainText("Unavailable");
        await expect(annual).toContainText("empty-priced-group");
        await expect(monthly).toContainText("Unavailable");
        await expect(monthly).toContainText("empty-priced-group");
        await expect(expected).not.toContainText("CHF 0.00");
      }
      await scan(page);
    }
    await hash(page, "agents/D3-A05");
    await expect(page.locator(".financial-summary")).toHaveAttribute("data-financial-ready", "false");
    await scan(page);
  });
  await open(page, "/blueprint.html#/agents/D3-A05");
  await expect(page.locator(".financial-summary")).toContainText("Supply an authoritative per-agent baseline");
  await expect(page.locator("#rail button")).toHaveCount(17);
  await hash(page, "plan");
  await expect(page.locator(".kcard")).toHaveCount(29);
  await expect(page.locator(".dor li")).toHaveCount(8);
  expect(watched).toEqual({ problems: [], external: [] });
});

function buildConsumerProbeSites() {
  // Deliberately contradictory DTOs cannot be emitted by the authoritative
  // producer. Exercise the consumer boundary with explicit TEST-ONLY projected
  // copies, rendered by the real assembler and hosted with build_site's actual
  // CSP. No page.route proxy, authoritative model, snapshot or review is written.
  const script = String.raw`
import copy, json, re, sys
from pathlib import Path
root = Path.cwd()
sys.path.insert(0, str(root / "tools"))
import build_site
sys.path.insert(0, str(root / "plugin/skills/frontier-blueprint/scripts"))
from build_blueprint import render
name = "Frontier Company Blueprint - Template (Caldova sample).html"
html = (root / "build/demo-agent-finops-preview" / name).read_text(encoding="utf-8")
original = json.loads(re.search(r'<script[^>]+id="bp-data"[^>]*>(.*?)</script>', html, re.S)[1])
template = (root / "plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html").read_text(encoding="utf-8")
def planning(r):
    def verified(v):
        if isinstance(v, list):
            for child in v: verified(child)
        elif isinstance(v, dict):
            v.pop("synthetic", None)
            if v.get("status") == "provisional": v.update(status="available", reason=None)
            if v.get("type") == "synthetic": v["type"] = "commercial"
            if v.get("status") == "synthetic": v["status"] = "verified"
            if v.get("validationStatus") == "synthetic": v["validationStatus"] = "validated"
            if v.get("verification_status") == "synthetic": v["verification_status"] = "verified"
            if v.get("source_status") == "synthetic": v["source_status"] = "validated"
            if isinstance(v.get("gaps"), list): v["gaps"] = []
            for child in list(v.values()): verified(child)
            if "verified_subtotal" in v and "provisional_subtotal" in v:
                total = v.get("total", v)
                v["verified_subtotal"].update(amount=total["amount"], status="available", reason=None)
                v["provisional_subtotal"].update(amount=None, status="unavailable", reason="empty-priced-group")
    verified(r)
    r.update(mode="planning", status="planning-ready", gaps=[])
    r["limitations"] = "TEST-ONLY projected consumer probe; not real finance approval. " + r["limitations"]
    r["profile"]["outcome"]["confirmation_status"] = "test-only-confirmed"
    target = dict(baseline_id=r["baseline"]["id"], version=r["baseline"]["version"], material_hash="f" * 64)
    review = dict(target, schema="frontier-finops-owner-review/1.0", id="TEST-ONLY-REVIEW", decision="approve",
        actor="Finance lead", finance_owner="Finance lead", date=r["as_of"], evidence_ref="test-only:external",
        mode="planning", recorded_as_of=r["as_of"], assertion="externally-asserted-not-authenticated",
        sharingClassification="customer-shareable", review_boundary="TEST-ONLY; not authentication or permission.")
    r["handover"] = dict(schema="frontier-finops-handover/1.0", as_of=r["as_of"], target=target,
        lifecycle="approved", structural_validation="valid", pricing_completeness="evidenced",
        ready=True, status="planning-ready", gaps=[], owner_review=review, financial_permission=False,
        limitations="TEST-ONLY projected assertion, not financial, build or deployment permission.")
sites = {}
for kind in ("positive", "association", "version", "rate", "source", "unused", "customer"):
    bp = copy.deepcopy(original)
    r = bp["agent_finops"]["records"][0]
    planning(r)
    if kind == "association":
        wrong = copy.deepcopy(r)
        wrong["agent_id"] = "D3-A04"
        bp["agent_finops"]["records"].append(wrong)
    elif kind == "version":
        for obj in (r["baseline"], r["handover"]["target"], r["handover"]["owner_review"]):
            obj.pop("version")
    elif kind == "rate": r["evidence"]["rates"][0]["verification"]["status"] = "unverified"
    elif kind == "source": r["evidence"]["sources"][0]["validationStatus"] = "unverified"
    elif kind == "unused":
        r["evidence"]["rates"].append(dict(id="UNUSED-RATE", amount="1", currency="CHF", source_id="UNUSED-SOURCE",
            verification=dict(status="unverified"), sharingClassification="internal-only"))
        r["evidence"]["sources"].append(dict(id="UNUSED-SOURCE", type="synthetic", validationStatus="unverified",
            sharingClassification="internal-only"))
    elif kind == "customer":
        bp["agent_finops"]["audience"] = r["audience"] = "customer"
        r["distribution"] = "scoped-derivative-not-authorisation"
        r["handover"].pop("target")
        r["handover"]["owner_review"].pop("material_hash")
    out = root / "build/evidence/task6/consumer-probes" / kind
    fixture = out / "demo"
    fixture.mkdir(parents=True, exist_ok=True)
    (fixture / name).write_text(render(bp, template), encoding="utf-8", newline="\n")
    build_site.build(out / "site", root / "build/demo", "none", None, baseline_demo=fixture)
    sites[kind] = str(out / "site")
print(json.dumps(sites))
`;
  return JSON.parse(execFileSync(python, ["-B", "-c", script], { cwd: ROOT, encoding: "utf8", timeout: 60_000 }).trim());
}

test("Task6 QUALITY browser consumer probes enforce agent, version and cached-evidence bindings without claiming approval", async ({ page }, info) => {
  test.setTimeout(180_000);
  const watched = watch(page), sites = buildConsumerProbeSites();
  for (const [kind, site] of Object.entries(sites)) await serve(site, page, async (origin) => {
    await open(page, origin + "/blueprint-baseline.html#/agents/D3-A05");
    const ready = ["positive", "association", "unused", "customer"].includes(kind);
    await expect(page.locator('.financial-summary[data-agent="D3-A05"]')).toHaveAttribute("data-financial-ready", String(ready));
    if (kind === "association") {
      await hash(page, "agents/D3-A04");
      await expect(page.locator('.financial-summary[data-agent="D3-A04"]')).toHaveAttribute("data-financial-ready", "false");
      await expect(page.locator(".financial-summary")).toContainText("binding conflicts");
      await screenshot(page, info, "quality-agent-association-gap");
    }
    await scan(page);
    await hash(page, "finops");
    await expect(page.locator(".baseline-export, .baseline-scenario")).toHaveCount(0);
    if (kind === "association") await expect(page.locator(".baseline-error")).toContainText("agent binding conflicts");
    await ack(page);
    await expect(page.locator('.baseline-record[data-agent="D3-A04"]')).toHaveCount(0);
    await expect(page.locator(".baseline-export")).toHaveCount(2);
    const expected = await page.locator("#bp-data").evaluate((n) => JSON.parse(n.textContent).agent_finops.records[0]);
    const json = JSON.parse(await download(page, "Download projected report JSON", `quality-${kind}-report.json`));
    expect(json).toEqual(expected);
    expect(json.agent_id).toBe("D3-A05");
    expect(json.profile.agent_id).toBe("D3-A05");
    expect(json.financial_permission).toBe(false);
    expect(json.limitations).toContain("TEST-ONLY");
    expect(json.scenarios.expected.annual_recurring.amount).toBe("1320.00");
    const md = await download(page, "Download projected report Markdown", `quality-${kind}-report.md`);
    expect(md).toContain("TEST-ONLY");
    expect(md).toContain("not authenticated");
    expect(md).toContain("1320.00");
    if (kind === "version") expect(json.baseline.version).toBeUndefined();
    if (kind === "rate") expect(json.evidence.rates[0].verification.status).toBe("unverified");
    if (kind === "source") expect(json.evidence.sources[0].validationStatus).toBe("unverified");
    if (kind === "customer") {
      expect(json.handover.target).toBeUndefined();
      expect(json.handover.owner_review.material_hash).toBeUndefined();
    }
    await page.reload();
    await expect(page.locator("#finops-preview-ack")).toBeVisible();
    await expect(page.locator(".baseline-export")).toHaveCount(0);
  });
  expect(watched).toEqual({ problems: [], external: [] });
});
