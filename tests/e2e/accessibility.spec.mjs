// #7 accessibility regressions. Use the real hosting CSP and locally installed axe;
// best-practice-only findings and incomplete checks are not WCAG conformance failures.
// axe has incomplete SVG coverage; these samples are not a full manual certification.
import { test, expect } from "@playwright/test";
import axe from "axe-core";

const WCAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const VIEWS = ["Overview", "Org model", "Blueprint", "Journeys", "Use cases", "PRD", "Agents", "Agent identity",
  "Target architecture", "Ontology", "IT readiness", "Roadmap", "Plan", "Attendees", "Discovery", "Risks", "Evidence"];
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
  if (/^\/blueprint(?:-preview)?\.html/.test(path)) {
    expect.soft(policy).toMatch(/script-src 'sha256-[A-Za-z0-9+/=]+'/);
    const expected = path.startsWith("/blueprint-preview.html")
      ? [...VIEWS.slice(0, 13), "FinOps", ...VIEWS.slice(13)] : VIEWS;
    await expect(page.locator("#rail button")).toHaveText(expected);
  }
}

async function scan(page, info, label) {
  // DevTools evaluation of the local source: no CDN, script tag or bypassCSP.
  await page.evaluate(axe.source);
  const report = await page.evaluate(async (tags) =>
    window.axe.run(document, { runOnly: { type: "tag", values: tags } }),
  [...WCAG, "best-practice"]);
  await info.attach(label, {
    body: Buffer.from(JSON.stringify(report, null, 2)),
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
  test(`blueprint AA all views, architecture, workflow and modal (${colorScheme})`, async ({ page }, info) => {
    await page.emulateMedia({ colorScheme });
    const problems = watchProblems(page);
    const summaries = [];
    await open(page, "/blueprint.html");
    for (let i = 0; i < VIEWS.length; i++) {
      await page.locator("#rail button").nth(i).click();
      await expect(page.locator("#crumb b")).toHaveText(VIEWS[i]);
      summaries.push(await scan(page, info, `${colorScheme}-view-${VIEWS[i]}`));
    }

    await open(page, "/blueprint.html#/prd");
    for (const summary of await page.locator("details.prdx > summary").all()) await summary.click();
    summaries.push(await scan(page, info, `${colorScheme}-prd-expanded-requirements`));

    await open(page, "/blueprint.html#/plan");
    await page.locator("#plan-mvp").check();
    await expect(page.locator(".kcard")).toHaveCount(2);
    summaries.push(await scan(page, info, `${colorScheme}-plan-mvp-filter`));

    await open(page, "/blueprint.html#/risks");
    await page.locator("#risk-category").selectOption("cost");
    await expect(page.locator(".riskrow")).toHaveCount(2);
    expect(await page.locator(".riskrow .linkp").evaluateAll((buttons) =>
      buttons.map((b) => b.textContent).filter((id) => /^R-/.test(id)).sort())).toEqual(["R-C05", "R-ONT-5"]);
    summaries.push(await scan(page, info, `${colorScheme}-risk-category-filter`));
    await page.locator('#rpanel input[value="closed"]').click();
    await expect(page.locator(".riskrow")).toHaveCount(1);
    await page.locator('#rpanel input[value="closed"]').click();
    await expect(page.locator("#rpanel")).toHaveCount(0);
    await expect(page.locator("#risk-category")).toBeFocused();
    summaries.push(await scan(page, info, `${colorScheme}-risk-empty-filter`));

    await open(page, "/blueprint.html#/org");
    await page.locator(".orgside .filters button").nth(1).click();
    summaries.push(await scan(page, info, `${colorScheme}-org-filtered-journey`));

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
    await info.attach(`${colorScheme}-scan-summary`, {
      body: Buffer.from(JSON.stringify({ summaries, problems }, null, 2)),
      contentType: "application/json"
    });
    expect(summaries).toHaveLength(29);
    expect(problems, "page errors and CSP/console errors").toEqual([]);
  });

  test(`site and identity catalogue AA (${colorScheme})`, async ({ page }, info) => {
    await page.emulateMedia({ colorScheme });
    const problems = watchProblems(page);
    const summaries = [];
    for (const path of ["/index.html", "/identity-catalogue.html"]) {
      await open(page, path);
      summaries.push(await scan(page, info, `${colorScheme}-${path.slice(1)}`));
    }
    await info.attach(`${colorScheme}-site-scan-summary`, {
      body: Buffer.from(JSON.stringify({ summaries, problems }, null, 2)), contentType: "application/json"
    });
    expect(summaries).toHaveLength(2);
    expect(problems, "page errors and CSP/console errors").toEqual([]);
  });

  test(`blueprint target sizes for checkboxes, evidence and resources (${colorScheme})`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    const problems = watchProblems(page);
    for (const [route, selector] of [
      ["org", 'input[type="checkbox"]'],
      ["evidence", ".pill.ev"],
      ["overview", ".flsrc a"],
      ["architecture", ".idrules a"]
    ]) {
      await open(page, `/blueprint.html#/${route}`);
      const targets = await page.locator(selector).evaluateAll((nodes) => nodes.map((node) => {
        const rect = node.getBoundingClientRect();
        return { text: node.textContent, width: rect.width, height: rect.height };
      }));
      expect(targets.length, `${route} has actual targets`).toBeGreaterThan(0);
      for (const target of targets) {
        expect.soft(target.width, `${route}: ${target.text} width`).toBeGreaterThanOrEqual(24);
        expect.soft(target.height, `${route}: ${target.text} height`).toBeGreaterThanOrEqual(24);
      }
    }
    expect(problems).toEqual([]);
  });

  test(`blueprint all 17 views reflow at 320px without clipping diagrams (${colorScheme})`, async ({ page }, info) => {
    await page.emulateMedia({ colorScheme, reducedMotion: "reduce" });
    await page.setViewportSize({ width: 320, height: 900 });
    const problems = watchProblems(page);
    await open(page, "/blueprint.html");
    for (let i = 0; i < VIEWS.length; i++) {
      await page.locator("#rail button").nth(i).click();
      await expect(page.locator("#crumb b")).toHaveText(VIEWS[i]);
      expect.soft(await page.evaluate(() => document.documentElement.scrollWidth),
        `${VIEWS[i]}: document width`).toBeLessThanOrEqual(321);
    }
    await open(page, "/blueprint.html#/agents/D3-A05");
    await expect(page.locator("svg.wfsvg .wfn")).toHaveCount(16);
    expect(await page.locator(".wfcanvas").evaluate((node) => ({
      scrolls: node.scrollWidth > node.clientWidth, overflow: getComputedStyle(node).overflowX
    }))).toEqual({ scrolls: true, overflow: "auto" });
    await info.attach(`a4-reflow-${colorScheme}`, { body: await page.screenshot(), contentType: "image/png" });
    expect(problems).toEqual([]);
  });
}

for (const colorScheme of ["light", "dark"]) {
  for (const colour of ["#FFFFFF", "#000000", "#0000FF"]) {
    test(`blueprint public colour outcomes ${colour} (${colorScheme})`, async ({ page }, info) => {
      await page.emulateMedia({ colorScheme, reducedMotion: "reduce" });
      const problems = watchProblems(page);
      await page.route("**/blueprint.html", async (route) => {
        const response = await route.fetch();
        const html = await response.text();
        const body = html.replace(/(<script type="application\/json" id="bp-data">)([\s\S]*?)(<\/script>)/,
          (_, start, json, end) => {
            const data = JSON.parse(json);
            data.meta.accent = colour;
            data.meta.status_note = "A4 <>& \u2028\u2029";
            for (const domain of data.domains) {
              domain.color = colour;
              // Exercise generated initials, not embedded icon art (which is never recoloured).
              for (const agent of [...domain.agents, domain.orchestrator].filter(Boolean)) {
                if (agent.identity) { delete agent.identity.icon; delete agent.identity.icons; }
              }
            }
            for (const journey of data.identity.journeys) { journey.colour = colour; journey.glyph = colour; }
            for (const environment of data.identity.environments) {
              if (environment.band) { environment.band = colour; environment.label = colour; }
            }
            const escaped = JSON.stringify(data).replace(/</g, "\\u003c").replace(/>/g, "\\u003e")
              .replace(/&/g, "\\u0026").replace(/\u2028/g, "\\u2028").replace(/\u2029/g, "\\u2029");
            return start + escaped + end;
          });
        await route.fulfill({ response, body });
      });
      await open(page, "/blueprint.html");
      await expect(page.locator("#banner")).toContainText("A4 <>&");
      for (let i = 0; i < VIEWS.length; i++) {
        await page.locator("#rail button").nth(i).click();
        await expect(page.locator("#crumb b")).toHaveText(VIEWS[i]);
        await scan(page, info, `${colorScheme}-${colour.slice(1)}-${VIEWS[i]}`);
        const fills = await page.locator(
          ".logo,.pill.acc,.btn.primary,.tab .num,.tab[aria-selected=true],.tab[aria-pressed=true]," +
          ".stage .sh,.stage .sh .n,.av2,.chn .no,.scale .on,.sw .chip,.bchip:not(.clean)," +
          ".fhead,.aicon.ini,.uchead .n,.lzbadge2"
        ).evaluateAll((nodes) => nodes.filter((node) => node.textContent.trim()).map((node) => ({
          text: node.textContent, ink: getComputedStyle(node).color, background: getComputedStyle(node).backgroundColor
        })));
        expect(fills.length, "filled label outcomes, including selected number badges").toBeGreaterThan(0);
        for (const pair of fills) {
          expect.soft(contrast(pair.ink, pair.background), `${VIEWS[i]} ${pair.text}: filled HTML contrast`).toBeGreaterThanOrEqual(4.5);
        }
      }
      // Check the actual filled shape AND the opacity chain, not raw RGB alone.
      for (const route of ["org", "usecases", "architecture"]) {
        await open(page, `/blueprint.html#/${route}`);
        await expectSvgTextContrast(page, ".orgsvg .ring + text,.matrix [role=button] text,.lzini,.stgt");
      }
      await info.attach(`a4-colours-${colorScheme}-${colour.slice(1)}`, {
        body: await page.screenshot(), contentType: "image/png"
      });
      expect(problems, "variant preserves real CSP and data-island escaping").toEqual([]);
    });
  }
}

async function expectSvgTextContrast(page, selector) {
  const pairs = await page.locator(selector).evaluateAll((nodes) => nodes.map((node) => {
    const previous = node.previousElementSibling;
    const shape = node.closest("svg.matrix") ? node.parentElement.querySelector("circle")
      : previous && ["circle", "rect"].includes(previous.tagName) ? previous : null;
    const opacityChain = [];
    for (let ancestor = node; ancestor; ancestor = ancestor.parentElement) {
      opacityChain.push(Number(getComputedStyle(ancestor).opacity));
    }
    return {
      text: node.textContent, ink: getComputedStyle(node).fill,
      background: shape ? getComputedStyle(shape).fill : getComputedStyle(node.closest("svg")).backgroundColor,
      opacityChain, fillOpacity: Number(getComputedStyle(node).fillOpacity),
      backgroundOpacity: shape ? Number(getComputedStyle(shape).opacity) * Number(getComputedStyle(shape).fillOpacity) : 1
    };
  }));
  expect(pairs.length, `${selector}: actual SVG text samples`).toBeGreaterThan(0);
  const faded = pairs.filter((pair) => pair.opacityChain.some((opacity) => opacity !== 1)
    || pair.fillOpacity !== 1 || pair.backgroundOpacity !== 1);
  expect.soft(faded.length, `opaque ink/background/ancestors: ${JSON.stringify(faded.slice(0, 3))}`).toBe(0);
  for (const pair of pairs) {
    // Raw colour contrast is valid only when neither ink nor its background is faded.
    expect.soft(contrast(pair.ink, pair.background), `${pair.text}: SVG contrast`).toBeGreaterThanOrEqual(4.5);
  }
}

for (const colorScheme of ["light", "dark"]) {
  test(`blueprint operable diagram contrast through journey and lifecycle filters (${colorScheme})`, async ({ page }, info) => {
    await page.emulateMedia({ colorScheme, reducedMotion: "reduce" });
    const problems = watchProblems(page);
    // Authored lifecycle/status values, including planned and retired lead/specialist nodes.
    await page.route("**/blueprint.html", async (route) => {
      const response = await route.fetch();
      const body = (await response.text()).replace(
        /(<script type="application\/json" id="bp-data">)([\s\S]*?)(<\/script>)/,
        (_, start, json, end) => {
          const data = JSON.parse(json);
          const domain = data.domains[0];
          domain.orchestrator.lifecycle = "Retired";
          domain.agents[0].lifecycle = "Planned";
          domain.agents[1].lifecycle = "Retired";
          domain.agents[2].status = "rejected";
          domain.use_cases[0].status = "rejected";
          return start + JSON.stringify(data).replace(/</g, "\\u003c") + end;
        });
      await route.fulfill({ response, body });
    });
    await open(page, "/blueprint.html#/org");
    const org = page.locator(".orgsvg");
    const count = await org.getByRole("button").count();
    expect(count).toBeGreaterThan(20);
    await expect(org.locator(".node.faded")).toHaveCount(3);
    expect(await org.locator('.ring[stroke-dasharray="5 4"]').count()).toBeGreaterThan(0);
    await expectSvgTextContrast(page, ".orgsvg text");
    const filters = page.locator(".orgside .filters button");
    for (let i = 1; i < await filters.count(); i++) {
      await filters.nth(i).click();
      await expect(filters.nth(i)).toHaveAttribute("aria-pressed", "true");
      await expect(org.getByRole("button")).toHaveCount(count);
      expect(await org.getByRole("button").evaluateAll((nodes) => nodes.every((node) => node.tabIndex === 0))).toBe(true);
      await expectSvgTextContrast(page, ".orgsvg text");
    }
    await scan(page, info, `${colorScheme}-org-filtered-retired-rejected-planned`);
    await info.attach(`a4-operable-org-${colorScheme}`, { body: await page.screenshot(), contentType: "image/png" });
    // A filtered-out retired lead still opens by Enter and regains focus on Escape.
    const lead = org.getByRole("button", { name: /lead agent for/ }).first();
    await lead.focus();
    await page.keyboard.press("Shift+Tab");
    await page.keyboard.press("Tab");
    await expect(lead).toBeFocused();
    expect(await lead.locator(".ring").evaluate((node) => getComputedStyle(node).strokeOpacity)).toBe("1");
    await page.keyboard.press("Enter");
    await expect(page.locator("#drawer")).toHaveAttribute("aria-hidden", "false");
    await page.keyboard.press("Escape");
    await expect(lead).toBeFocused();
    // The dimmed journey arc still filters by Space; Tab reaches a retired specialist.
    await org.getByRole("button", { name: /^Filter on/ }).first().focus();
    await page.keyboard.press("Space");
    await expect(filters.nth(1)).toHaveAttribute("aria-pressed", "true");
    await org.getByRole("button", { name: /specialist agent in/ }).first().focus();
    await page.keyboard.press("Tab");
    await expect(org.getByRole("button", { name: /specialist agent in/ }).nth(1)).toBeFocused();
    await page.keyboard.press("Space");
    await expect(page.locator("#drawer")).toHaveAttribute("aria-hidden", "false");
    await page.keyboard.press("Escape");

    await open(page, "/blueprint.html#/usecases");
    const bubbles = page.locator(".matrix [role=button]");
    await expect(bubbles).toHaveCount(16);
    await expect(bubbles.first()).toHaveClass(/faded/);
    await expectSvgTextContrast(page, ".matrix [role=button] text");
    await scan(page, info, `${colorScheme}-portfolio-rejected`);
    await info.attach(`a4-operable-portfolio-${colorScheme}`, { body: await page.screenshot(), contentType: "image/png" });
    await bubbles.first().focus();
    await page.keyboard.press("Shift+Tab");
    await page.keyboard.press("Tab");
    await expect(bubbles.first()).toBeFocused();
    expect(await bubbles.first().locator("circle").first().evaluate((node) => getComputedStyle(node).strokeOpacity)).toBe("1");
    await page.keyboard.press("Space");
    await expect(page.locator("#ucdetail")).toBeVisible();
    expect(problems).toEqual([]);
  });
}

function contrast(first, second) {
  const luminance = (colour) => {
    const rgb = colour.match(/[\d.]+/g).slice(0, 3).map(Number).map((channel) => {
      const value = channel / 255;
      return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
    });
    return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
  };
  const a = luminance(first), b = luminance(second);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
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
  await open(page, "/blueprint-preview.html#/finops");
  await page.locator("#finops-preview-ack").click();
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

test("narrow header reserves readable title space rather than one-word columns", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await open(page, "/blueprint.html");
  const title = await page.locator("#top .ttl").boundingBox();
  const branding = await page.locator("#top .cobrand").boundingBox();
  expect(title.width).toBeGreaterThanOrEqual(200);
  expect(branding.y).toBeGreaterThanOrEqual(title.y + title.height);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(321);
});

test("all 17 views reflow at 320 CSS pixels without document overflow", async ({ page }, info) => {
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
