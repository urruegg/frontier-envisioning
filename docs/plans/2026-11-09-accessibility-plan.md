# Accessibility Implementation Plan

| Field | Value |
|---|---|
| Version | 0.4 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Plan/readiness human-approved on #6; A1-A4 implemented, A5 docs handed off; A4/A5 acceptance blocked by catalogue AA; final parent verification and human acceptance pending |
| Scope | DG-08: measured renderer barriers and repeatable WCAG 2.2 AA-oriented checks |
| References | [Plan catalogue](README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/7), [Idea](../ideas/2026-11-09-docs-governance-and-accessibility.md), [Spec](../specs/2026-11-09-docs-governance-and-accessibility-design.md), [Sprint](../sprints/SPRINT-001-docs-governance-and-accessibility.md), [Master](2026-11-09-docs-governance-implementation.md), [Baseline](../intake/2026-11-09-accessibility-audit.json) |

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `subagent-driven-development` after plan approval. Give each A-task to a
> fresh registered `frontier-renderer` worker with only its named paths.

**Goal:** Remove verified focus, semantic, contrast, target and page-reflow
barriers, with honest automated/manual acceptance boundaries.

**Architecture:** Fix `src/renderer` and regenerate; test through existing
DOM/Playwright and real CSP. Axe is a pinned development dependency, never a
resource in the self-contained product. Historical identity/raster inputs
stay unchanged.

**Tech Stack:** Vanilla JS/CSS/HTML, node:test/happy-dom, Playwright,
axe-core 4.11.0, existing Python build/version/gate tooling.

## Delivery note (2026-11-10)

The approved task instructions below remain the execution contract, not
completed acceptance checkboxes. A1 is `1a10453`; A2 is `5478918`/`4b8d653`;
A3 is `463dc99`; A4 is `0857eda`/`4969c13`. A5 documentation is handed off
with [new verification evidence](../intake/2026-11-10-accessibility-verification.md).
The branch is stacked on governance draft PR #13, following foundation
draft PR #12; neither PR is merged.

The prior full browser run has 41 passed and 2 failed tests. The catalogue
has actual AA contrast failures (Later wave 4.40:1; Finance header 4.33:1)
in both schemes, beyond the design-stage best-practice finding below.
Full L2 is red. The excluded identity generator requires a separate human
scope decision; none is approved. Preserve its assertions, generated inputs
and historical guards. Parent final L2, screenshot review and #8 manual AT
acceptance are still pending; A4/A5 acceptance is not complete.
The single fresh A5 strict L1 attempt also failed on document-contract date
and content pins. Its exact summary and separate passing 41-test DOM run
are in the handoff; resolving those contracts needs a bounded parent task,
not backdating or out-of-scope test changes by this documentation worker.

---

## Ownership and exclusions

Own `src/renderer/skeleton.html`, `template.js`, `template.css`,
`tests/dom/accessibility.test.mjs`, `tests/e2e/accessibility.spec.mjs`,
`package.json`, `package-lock.json`, relevant renderer/user docs and generated
template/install inventory through the task runner.

Do not edit `tools/demo_raster.py`, frozen fixture manifests/assets,
`releases/**`, protected workflows/hooks/settings, Microsoft icon artwork or
the identity kit generator. The catalogue's ten empty-table-header occurrences
are best-practice-only here, not a claim that its full accessibility passes.
Keep that separate guarded product-output decision recorded; do not mask it
by rewriting only the hosted copy.

## Task A6: targeted catalogue CI correction (2026-11-10)

The user's request to solve the linked PR #15 job now authorises this small
correction, superseding only the original catalogue-generator exclusion.
All historical data, raster bytes, release records and human controls remain
outside the edit scope. Implement on the existing PR #15 branch.

**Files:** `plugin/skills/frontier-agent-identity/kit/scripts/identity_docs.py`,
`tools/demo_raster.py`, `tools/build_demo.py`, new focused unit tests and a
new version-scoped current-input record under `tests/fixtures/`.
Do not edit `tests/fixtures/caldova-raster-1.4.0/`.

- [ ] Reproduce the two existing browser failures unchanged.
- [ ] Write focused generator tests proving the status text's rendered
      contrast is at least 4.5:1 and header text has no lowering opacity.
- [ ] Replace only rendered status foreground and subtitle opacity:

```python
foreground = L.accessible_shade(st["fg"], st["bg"], target=4.6)
```

```css
.jhead small{font-size:14px}
```

- [ ] Test and implement an explicit 1.6.1 current-input record, pinned to
      the base profile. It may override exactly the two named inputs;
      unrelated input changes, unsupported versions and tampered PNGs fail.
- [ ] Keep historical archive provenance distinct from current release
      output identity. Validate any present release record against the
      completed canonical identity archive; a mismatch fails the build.
- [ ] Regenerate current expected inputs through the real generator; inspect
      and prove that only the two allowed inputs change. Do not copy a golden
      ZIP or change historical hashes to make the build pass.
- [ ] Run focused unit tests, both unchanged catalogue AA cases, full strict
      L1/L2, repeat-build identity hashing and the protected/historical diff.
- [ ] Update the changelog, current verification report and sprint with actual
      results. Commit/push the fix to PR #15, verify cloud checks and leave
      approval, merge, release and manual acceptance to people.

```powershell
python -m pytest tests\unit\test_demo_raster.py tests\unit\test_identity_catalogue.py -q
npx playwright test --grep "site and identity catalogue AA" --retries=0 --workers=1
python tools\dev.py check --strict
python tools\dev.py site e2e --strict
```

Expected: catalogue assertions and complete gates pass without exclusions.
The existing unreleased-version reproduction skip remains honest; no release
manifest is fabricated. This task does not authorise #8's human-only actions.

## Task A1: development-only accessibility checks and failing regressions

**Create:** `tests/e2e/accessibility.spec.mjs`,
`tests/dom/accessibility.test.mjs`.
**Modify:** `package.json`, `package-lock.json`.

- [ ] Parent checks actual current version and performs any required patch bump
      before the first product edit. Only the coordinator writes version
      carriers/generates outputs; never two workers.

```powershell
$version = (Get-Content -Raw -LiteralPath 'plugin\.claude-plugin\plugin.json' | ConvertFrom-Json).version
if (Test-Path "releases\$version\manifest.json") {
  $parts = $version.Split('.')
  $next = '{0}.{1}.{2}' -f $parts[0], $parts[1], ([int]$parts[2] + 1)
  if (Test-Path "releases\$next\manifest.json") { throw 'Next patch already released; stop for version review.' }
  python tools\dev.py bump $next --date (Get-Date -Format yyyy-MM-dd)
  if ($LASTEXITCODE -ne 0) { throw 'Version bump failed.' }
} else {
  Write-Output "Using current unreleased version $version."
}
```

If a new version cannot use the existing explicitly approved demo profile,
stop for a version/profile decision; do not enable arbitrary future versions
or loosen generated-input hashes as a shortcut.

- [ ] Use the package manager once to add the approved missing development
      dependency and lockfile, after plan approval:

```powershell
npm install --save-dev --save-exact axe-core@4.11.0 --no-audit --no-fund
```

No product or plugin runtime dependency is added. Do not modify CI workflow
files: existing `npm ci` and Playwright discovery cover the new spec.

- [ ] Write the browser baseline/keyboard suite below:

```javascript
import { test, expect } from "@playwright/test";
import axe from "axe-core";

const AA = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
test.setTimeout(180_000);

async function scan(page, info, label) {
  await page.evaluate(axe.source);
  const report = await page.evaluate(async (tags) =>
    window.axe.run(document, { runOnly: { type: "tag", values: tags } }),
  AA.concat("best-practice"));
  await info.attach(label, {
    body: Buffer.from(JSON.stringify({
      violations: report.violations, incomplete: report.incomplete
    }, null, 2)), contentType: "application/json"
  });
  const failures = report.violations.filter(v => v.tags.some(tag => AA.includes(tag)));
  expect(failures, `${label}: applicable WCAG failures`).toEqual([]);
}

for (const colorScheme of ["light", "dark"]) {
  test(`accessibility all views and site ${colorScheme}`, async ({ page }, info) => {
    await page.emulateMedia({ colorScheme });
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    const response = await page.goto("/blueprint.html");
    expect(response.headers()["content-security-policy"]).toContain("script-src 'sha256-");
    const names = await page.locator("#rail button").allTextContents();
    expect(names).toHaveLength(14);
    for (let i = 0; i < names.length; i++) {
      await page.locator("#rail button").nth(i).click();
      await scan(page, info, `${colorScheme}-${names[i]}`);
    }
    for (const path of ["/index.html", "/identity-catalogue.html"]) {
      await page.goto(path);
      await scan(page, info, `${colorScheme}-${path}`);
    }
    expect(errors).toEqual([]);
  });
}

test("accessibility drawer focus boundary and return", async ({ page }, info) => {
  await page.goto("/blueprint.html#/evidence");
  await page.locator("#view .pager button").last().focus();
  await page.keyboard.press("Tab");
  expect(await page.evaluate(() => !!document.activeElement.closest("#drawer"))).toBe(false);
  const trigger = page.locator("#view .pill.ev").first();
  await trigger.click();
  await expect(page.locator("#drawer-close")).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  expect(await page.evaluate(() => !!document.activeElement.closest("#drawer"))).toBe(true);
  await scan(page, info, "drawer-open");
  await page.keyboard.press("Escape");
  await expect(page.locator("#drawer")).toHaveAttribute("aria-hidden", "true");
  await expect(trigger).toBeFocused();
  await expect(page.locator(".page")).not.toHaveAttribute("inert", "");
});

test("accessibility journey tabs retain route and keyboard focus", async ({ page }) => {
  await page.goto("/blueprint.html#/blueprint");
  await page.locator("#subnav [role=tab]").first().focus();
  await page.keyboard.press("ArrowRight");
  await expect(page).toHaveURL(/#\/blueprint\//);
  await expect(page.locator("#subnav [role=tab]").nth(1)).toBeFocused();
  await expect(page.locator("#subnav [role=tab]").nth(1)).toHaveAttribute("aria-selected", "true");
  await page.keyboard.press("Home");
  await expect(page.locator("#subnav [role=tab]").first()).toBeFocused();
  await page.keyboard.press("End");
  await expect(page.locator("#subnav [role=tab]").last()).toBeFocused();
});

test("accessibility all views reflow at 320 CSS pixels", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/blueprint.html");
  const names = await page.locator("#rail button").allTextContents();
  for (let i = 0; i < names.length; i++) {
    await page.locator("#rail button").nth(i).click();
    const width = await page.evaluate(() => document.documentElement.scrollWidth);
    expect(width, names[i]).toBeLessThanOrEqual(321);
  }
});

test("accessibility architecture states and service workflow", async ({ page }, info) => {
  await page.goto("/blueprint.html#/architecture");
  const names = await page.locator(".atabs button").allTextContents();
  for (let i = 0; i < names.length; i++) {
    await page.locator(".atabs button").nth(i).click();
    await scan(page, info, `architecture-${names[i]}`);
  }
  await page.goto("/blueprint.html#/agents/D3-A05");
  await scan(page, info, "service-workflow");
  await page.locator("svg.wfsvg .wfn").first().focus();
  await page.keyboard.press("Enter");
  await scan(page, info, "workflow-properties");
});
```

- [ ] Add the DOM contract below, using the existing helper API:

```javascript
import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import { openBlueprint } from "./helpers.mjs";

describe("accessibility structure", () => {
  let bp;
  before(async () => { bp = await openBlueprint(); });
  after(async () => { await bp.close(); });
  it("uses hidden inert dialog and independently exposed SVG controls", async () => {
    const dialog = bp.doc.getElementById("drawer");
    assert.equal(dialog.tagName, "DIV");
    assert.equal(dialog.hidden, true);
    assert.equal(dialog.hasAttribute("inert"), true);
    await bp.go("#/org");
    assert.equal(bp.view().querySelector("svg.orgsvg").getAttribute("role"), "group");
    assert.equal(bp.view().querySelectorAll('button:not([role="tab"])[aria-selected]').length, 0);
    await bp.go("#/usecases");
    assert.equal(bp.view().querySelector("svg.matrix").getAttribute("role"), "group");
    assert.deepEqual(bp.errors, []);
  });
});
```

- [ ] Run:

```powershell
python tools\dev.py site
npx playwright test tests\e2e\accessibility.spec.mjs
```

Expected red: real WCAG/keyboard/reflow assertions expose the measured faults.
Dependency/fixture/server failures are not accepted as the red regression proof.
Run `python tools\dev.py dom` for the structural red case too.
Commit A1 dependency/tests with `test: expose measured accessibility barriers`,
body `Refs #7.` and the standard co-author trailer. Do not claim A1 is green.

## Task A2: modal shell, closed state and focus containment

**Modify:** `src/renderer/skeleton.html`, `template.js`, `template.css`.
**Tests:** A1 drawer/DOM selectors; existing workshop/drawer tests.

- [ ] In skeleton replace the drawer `aside` shell with this matched `div`;
      preserve its existing inner body/close control and use `.drawer-head`
      instead of a second document `header` landmark:

```html
<div class="drawer" id="drawer" hidden inert aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
  <div class="drawer-head"><div><h2 id="drawer-title"></h2><p id="drawer-sub"></p></div><button type="button" class="x" id="drawer-close" aria-label="Close">&times;</button></div>
  <div class="body" id="drawer-body"></div>
</div>
```

Make the existing scrim decorative with `aria-hidden="true"`. Wrap the existing
banner in a named region without changing its ID or `renderBanner()`:

```html
<section aria-label="Blueprint status">
  <div class="banner" id="banner" role="note"></div>
</section>
```

- [ ] Replace the existing drawer variable declaration and open/close functions
      with the block below, adding its shared focus functions in that section.
      Preserve the existing close-button/scrim listeners.

```javascript
var drawer = document.getElementById("drawer");
var scrim = document.getElementById("scrim"), lastFocus = null, drawerTimer = null;
function backgroundInert(value) {
  document.querySelectorAll(".page,.rail,.skip").forEach(function(node) {
    node.inert = value;
  });
}
function drawerStops() {
  return Array.from(drawer.querySelectorAll(
    'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])'
  )).filter(function(node) {
    return node.getClientRects().length > 0 && !node.closest("[hidden],[inert]");
  });
}
function hideClosedDrawer() {
  if (!drawer.classList.contains("open")) drawer.hidden = true;
}
function openDrawer(title, sub, body) {
  clearTimeout(drawerTimer);
  lastFocus = document.activeElement;
  document.getElementById("drawer-title").textContent = title || "";
  document.getElementById("drawer-sub").textContent = sub || "";
  var content = document.getElementById("drawer-body");
  content.replaceChildren(); add(content, body);
  content.scrollTop = 0;
  drawer.hidden = false;
  drawer.inert = false;
  drawer.setAttribute("aria-hidden", "false");
  backgroundInert(true);
  drawer.classList.add("open"); scrim.classList.add("open");
  document.getElementById("drawer-close").focus();
}
function closeDrawer() {
  drawer.classList.remove("open"); scrim.classList.remove("open");
  drawer.inert = true;
  drawer.setAttribute("aria-hidden", "true");
  backgroundInert(false);
  if (lastFocus && lastFocus.isConnected && typeof lastFocus.focus === "function" &&
      !lastFocus.closest("[hidden],[inert]")) lastFocus.focus();
  else document.getElementById("view").focus({preventScroll:true});
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) hideClosedDrawer();
  else drawerTimer = setTimeout(hideClosedDrawer, 200);
}
function containDrawerTab(event) {
  if (event.key !== "Tab" || !drawer.classList.contains("open")) return false;
  var stops = drawerStops(), first = stops[0], last = stops[stops.length - 1];
  if (!first) {
    event.preventDefault();
    document.getElementById("drawer-close").focus();
  } else if (event.shiftKey && (document.activeElement === first || !drawer.contains(document.activeElement))) {
    event.preventDefault(); last.focus();
  } else if (!event.shiftKey && (document.activeElement === last || !drawer.contains(document.activeElement))) {
    event.preventDefault(); first.focus();
  }
  return true;
}
```

Call `containDrawerTab(e)` at the start of the existing document keydown handler,
returning when true; keep Escape/arrow handling otherwise. Do not install a
second conflicting global handler.

- [ ] In CSS add `.drawer[hidden]{display:none}`. Rename only `.drawer header`,
      `.drawer header h2` and `.drawer header p` selectors to the corresponding
      `.drawer .drawer-head` selectors. In the reduced-motion rule disable
      drawer/scrim transitions. Normal close retains its existing short motion
      before hiding; reduced motion closes without the delay.
- [ ] Run:

```powershell
python tools\dev.py template demo dom site
npx playwright test tests\e2e\accessibility.spec.mjs --grep "drawer focus"
```

Expected green for drawer/structure; other AA tests may still fail until A3/A4.
Verify Escape restores the exact evidence trigger, background cannot receive
Tab/Shift+Tab, closed controls are excluded, and no new page/CSP errors occur.
Commit A2 owned source/tests/generated outputs with `fix: contain accessible dialog focus`,
body `Refs #7.` and the standard co-author trailer.

## Task A3: tab/filter/SVG semantics without shortcut regressions

**Modify:** `src/renderer/template.js`, `template.css`.
**Tests:** `tests/dom/accessibility.test.mjs`, browser tab/architecture cases.

- [ ] Add shared helpers before the existing global keyboard handler:

```javascript
function activateTab(id, update) {
  update();
  render();
  var tab = document.getElementById(id);
  if (!tab) throw new Error("Rendered tab is missing: " + id);
  tab.focus();
}
function navigateTabs(event) {
  var tab = event.target && event.target.closest
    ? event.target.closest('[role="tab"]') : null;
  if (!tab) return false;
  var list = tab.closest('[role="tablist"]');
  if (!list) return false;
  var tabs = Array.from(list.querySelectorAll('[role="tab"]')).filter(function(node) {
    return node.closest('[role="tablist"]') === list;
  });
  var index = tabs.indexOf(tab), next = index;
  if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
  else if (event.key === "ArrowLeft") next = (index + tabs.length - 1) % tabs.length;
  else if (event.key === "Home") next = 0;
  else if (event.key === "End") next = tabs.length - 1;
  else return false;
  event.preventDefault(); event.stopPropagation();
  tabs[next].click();
  return true;
}
```

Replace the existing keydown handler with the complete version below. Browser/
system modifiers remain untouched; Enter/Space remain native button and existing
SVG activation. Do not install a second global handler:

```javascript
document.addEventListener("keydown",function(e){
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  if (containDrawerTab(e)) return;
  if (e.key === "Escape" && drawer.classList.contains("open")) {
    e.preventDefault(); closeDrawer(); return;
  }
  if (drawer.classList.contains("open")) return;
  var tag = e.target && e.target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
  if (navigateTabs(e)) return;
  var index = ORDER.indexOf(state.view);
  if (e.key === "ArrowRight" && ORDER[index + 1]) go(ORDER[index + 1]);
  if (e.key === "ArrowLeft" && ORDER[index - 1]) go(ORDER[index - 1]);
});
```

- [ ] Add stable IDs, `aria-controls` and roving `tabindex` at the three
      existing tab construction sites:

| Site | ID / controls | Click state mutation |
|---|---|---|
| `renderSubnav()` | `journey-tab-` + index / `journey-panel` | `state.d=i`; clear `state.agent` only on Agents |
| `renderArchitecture()` | `architecture-tab-` + tab key / `architecture-panel` | `state.archTab=t[0]` |
| `factorySteps()` | `factory-tab-` + index / `factory-step-panel` | `state.fstep=i` |

Each selected tab has `tabindex:0`; others `-1`. Replace the existing journey
button attribute object with the complete expression below, retaining its
existing number/name children:

```javascript
({
  type:"button",id:"journey-tab-" + i,role:"tab",class:"tab",
  style:"--d:" + d.color,"aria-controls":"journey-panel",
  "aria-selected":i === state.d ? "true" : "false",tabindex:i === state.d ? "0" : "-1",
  onclick:function(){
    activateTab("journey-tab-" + i,function(){
      state.d = i;
      if (state.view === "agents") state.agent = null;
    });
  }
})
```

Architecture and factory button attribute objects are:

```javascript
({
  type:"button",id:"architecture-tab-" + t[0],role:"tab",class:"atab",
  "aria-controls":"architecture-panel",
  "aria-selected":t[0] === state.archTab ? "true" : "false",
  tabindex:t[0] === state.archTab ? "0" : "-1",
  onclick:function(){
    activateTab("architecture-tab-" + t[0],function(){ state.archTab = t[0]; });
  }
})
```

```javascript
({
  type:"button",id:"factory-tab-" + i,role:"tab",class:"fstep lp-" + x.loop,
  "aria-controls":"factory-step-panel",
  "aria-selected":i === state.fstep ? "true" : "false",
  tabindex:i === state.fstep ? "0" : "-1",
  onclick:function(){
    activateTab("factory-tab-" + i,function(){ state.fstep = i; });
  }
})
```

Give each controlled panel `role:"tabpanel"` and `aria-labelledby` pointing to
the selected tab. In `factorySteps()` these attributes belong on its existing
`.fdetail`, replacing only its attributes:

```javascript
({
  class:"fdetail lp-" + st.loop,id:"factory-step-panel",role:"tabpanel",
  "aria-labelledby":"factory-tab-" + state.fstep
})
```

In architecture replace the three final return branches with:

```javascript
var content = state.archTab === "lz" ? renderLandingZone()
  : state.archTab === "decisions" ? renderDecisions(A)
  : renderArchitectureClassic(state.archTab);
return out.concat([h("section",{
  id:"architecture-panel",role:"tabpanel",
  "aria-labelledby":"architecture-tab-" + state.archTab
},content)]);
```

In `render()` wrap journey content only when a selected
journey tab actually exists; sparse data without tabs must still render:

```javascript
var selectedJourney = document.querySelector('#subnav [role="tab"][aria-selected="true"]');
var content = selectedJourney
  ? h("section",{id:"journey-panel",role:"tabpanel","aria-labelledby":selectedJourney.id}, out)
  : out;
v.replaceChildren(); add(v, content); v.appendChild(pager());
```

- [ ] Change ordinary Org/ADR filter buttons from `aria-selected` to
      `aria-pressed`. Add the pressed selector to their existing active-tab CSS;
      do not change genuine tab attributes. Change only the organisation and
      portfolio outer SVG roles from `img` to labelled `group`, retaining all
      independently named keyboard node buttons and meaningful diagram labels.
- [ ] Add this browser case before implementing the architecture/factory
      changes, then run it red-to-green:

```javascript
test("accessibility architecture factory tabs and global shortcut", async ({ page }, info) => {
  await page.goto("/blueprint.html#/architecture");
  const architecture = page.locator(".atabs [role=tab]");
  await architecture.first().focus();
  await page.keyboard.press("ArrowRight");
  await expect(architecture.nth(1)).toBeFocused();
  await expect(page).toHaveURL(/#\/architecture/);
  await page.keyboard.press("Home");
  await expect(architecture.first()).toBeFocused();
  await page.keyboard.press("End");
  await expect(architecture.last()).toBeFocused();
  await expect(page.locator("#architecture-panel")).toHaveAttribute("role", "tabpanel");
  await page.goto("/blueprint.html#/journeys");
  await page.locator("#subnav [role=tab]").filter({hasText:/factory/i}).click();
  const steps = page.locator(".fsteps [role=tab]");
  expect(await steps.count()).toBeGreaterThan(1);
  await steps.first().focus();
  await page.keyboard.press("ArrowRight");
  await expect(steps.nth(1)).toBeFocused();
  await expect(page).toHaveURL(/#\/journeys\//);
  await page.keyboard.press("Home");
  await expect(steps.first()).toBeFocused();
  await page.keyboard.press("End");
  await expect(steps.last()).toBeFocused();
  await expect(page.locator("#factory-step-panel")).toHaveAttribute("role", "tabpanel");
  await scan(page, info, "factory-selected-step");
  await page.goto("/blueprint.html#/blueprint");
  await page.locator("#view").focus();
  await page.keyboard.press("ArrowRight");
  await expect(page).toHaveURL(/#\/journeys\//);
});
```

- [ ] Run the structural/browser tab selectors and existing `agent workflow`
      and legend cases to preserve their keyboard behaviour.
- [ ] Regenerate and commit source/generated changes with `fix: scope accessible tab and filter semantics`,
      body `Refs #7.` and the standard co-author trailer.

## Task A4: measured contrast, target sizing and narrow layout

**Modify:** `src/renderer/template.js`, `template.css`.
**Tests:** browser AA/light-dark/320px cases and customer-accent variants.

- [ ] Run the remaining AA cases and inspect their exact foreground/background,
      size and source selectors. The baseline has a specific cascade bug:
      `.ladder .rung span` overrides the accent pill's white foreground.
- [ ] Add this small private helper beside `hex()`/`soft()`, mirroring the
      existing identity library's sRGB calculation without importing Python
      into the offline browser:

```javascript
function onColour(colour) {
  var safe = hex(colour, ACCENT);
  var channels = [1,3,5].map(function(index){
    var value = parseInt(safe.slice(index,index + 2),16) / 255;
    return value <= .04045 ? value / 12.92 : Math.pow((value + .055) / 1.055, 2.4);
  });
  var luminance = .2126 * channels[0] + .7152 * channels[1] + .0722 * channels[2];
  return luminance > .1791287847 ? "#000000" : "#FFFFFF";
}
```

After the existing validated `ACCENT` assignment set `--accent-on` to
`onColour(ACCENT)`. Use that variable for solid accent badge/button/logo text.
For raw data-colour badge backgrounds, use matching `onColour()` foregrounds
from the same validated colour. Preserve original brand data, borders, swatches
and Microsoft images.

For coloured labels/links/SVG text on neutral panels, replace the direct
data-colour foreground with `var(--ink)` while retaining the journey colour in
its border/shape/swatch and its textual label. Do not recolour icon artwork or
remove meaning; this avoids low-contrast data colours as the sole text colour.
For selected journey/filter tabs declare the actual `--d` background and its
matching `--d-on` foreground; the neutral All filter uses `--ink`/`--bg`.

The corrective CSS selectors include:

```css
.pill.acc,.btn.primary,.logo{color:var(--accent-on)}
.ladder .rung .pill.acc{color:var(--accent-on)}
.tab[aria-selected="true"],.tab[aria-pressed="true"]{
  color:var(--d-on,var(--accent-on));
}
.tab .num{color:var(--d-on,var(--accent-on))}
.tab[aria-selected="true"] .num,.tab[aria-pressed="true"] .num{
  background:var(--d) !important;
}
.atab[aria-selected="true"]{color:var(--accent-on)}
.chk input{inline-size:24px;block-size:24px;flex-shrink:0}
.pill.ev{min-inline-size:24px;min-block-size:24px}
#view li > a[target="_blank"][rel="noopener"]{
  display:inline-block;min-block-size:24px;
}
```

When adapting existing selectors, preserve their other declarations rather
than replacing whole rules. Replace the old selected-number translucent overlay
with its actual opaque matching background; do not assume contrast against the
button also proves contrast against a lighter nested number badge.
For the Org All badge use the actual grey's `onColour()` foreground when
unselected and `var(--bg)` when selected against `var(--ink)`.
Ensure every solid-background text site has the
matching foreground and actual AA scan proof; no contrast-rule exclusions.

- [ ] Add the following to the existing narrow media rule, not desktop styles:

```css
@media (max-width:700px){
  .banner .pill{white-space:normal;max-inline-size:100%;overflow-wrap:anywhere}
  .outcomes,.foundation,.grid2,.agtop,.mrow,.kv,.q .row{
    grid-template-columns:minmax(0,1fr);
  }
  .alist,.mrow > div,.kv dd{min-inline-size:0;overflow-wrap:anywhere}
  .aitem .anm{white-space:normal}
}
```

Planning diagnostics isolated these actual causes: the nonwrapping internal
banner, fixed 200px+150px foundation/outcomes tracks, min-content agent/
definition-list columns, readiness two-column grid and Discovery status row.
The exact CSS above was tested **in memory only** in Edge: all fourteen
document scroll widths became 320px. Hiding the drawer alone left 418px, so it
is not used as a false reflow fix. No repository source was altered by that probe.

Preserve local `.tscroll`, feedback-loop/workflow and journey diagram scrolling.
Do not add global `overflow-x:hidden`, clip content, shrink text to illegibility
or declare every page a two-dimensional exception.

- [ ] Add accent variants before final green. Route only the test's data island,
      preserving app script/CSP and HTML-safe JSON:

```javascript
for (const accent of ["#FFFFFF", "#000000", "#0F6CBD"]) {
  test(`accessibility filled accent contrast ${accent}`, async ({ page }, info) => {
    await page.route("**/blueprint.html", async route => {
      const response = await route.fetch();
      const html = await response.text();
      const body = html.replace(
        /(<script type="application\/json" id="bp-data">)([\s\S]*?)(<\/script>)/,
        (whole, open, json, close) => {
          const data = JSON.parse(json);
          data.meta.accent = accent;
          const safe = JSON.stringify(data).replace(/</g,"\\u003c")
            .replace(/>/g,"\\u003e").replace(/&/g,"\\u0026")
            .replace(/\u2028/g,"\\u2028").replace(/\u2029/g,"\\u2029");
          return open + safe + close;
        }
      );
      await route.fulfill({ response, body });
    });
    await page.goto("/blueprint.html");
    await scan(page, info, `accent-${accent}`);
  });
}
```

The existing baseline contrast test must fail before the foreground fix, and
each variant passes only with actual computed accessible colours. If a
previously hidden contrast failure appears after better SVG semantics, inspect
and fix its rendered foreground/background within this task; never hide it.

- [ ] Run:

```powershell
python tools\dev.py template demo dom site
npx playwright test tests\e2e\accessibility.spec.mjs
npx playwright test tests\e2e\blueprint.spec.mjs --grep "legend remains|agent workflow|reduced motion"
```

Expected green: applicable AA findings zero in the covered states, all fourteen
320px page widths at most 321px, preserved local diagram scrolling, keyboard
and reduced motion. Best-practice/incomplete reports remain attached and honest.
- [ ] Commit with `fix: improve rendered contrast targets and narrow reflow`,
      body `Refs #7.` and the standard co-author trailer.

## Task A5: final product documentation, guards and human acceptance handoff

**Modify:** split PRD/solution design, `docs/engineering/testing-strategy.md`,
`plugin/skills/frontier-blueprint/references/authoring-guide.md`,
CHANGELOG under the actual development version, sprints/issue evidence.
**Generate:** template/install index through existing commands.

- [ ] Wait for the docs split and the governance writer before touching shared
      product docs. Update NFR-0012 with the WCAG 2.2 AA target and actual
      automated/keyboard criteria without retroactively changing 1.6.0 results.
- [ ] Document accessible modal/tab semantics, 24px targets, 320px page reflow,
      theme/brand contrast, test coverage and the remaining manual/catalogue
      findings. Product authoring-guide changes trigger package regeneration.
- [ ] Run exact full commands:

```powershell
python tools\dev.py template package demo
python tools\dev.py check --strict
python tools\dev.py site e2e --strict
```

Expected full gates end with `ALL GATES PASSED`. Preserve source backward
compatibility through existing sparse/older-data self-tests. If identity
generated-input, README, archive or raster guards change, stop; do not refresh
their hashes to conceal the difference.
- [ ] Inspect desktop, 1024px and 320px screenshots, focus indicators, dialog
      state and diagram scroll reachability. Preserve 1.6.1 legend behaviour.
- [ ] Publish a scoped renderer draft PR using the template and real local/
      cloud results. Link #7 and the sprint; do not claim manual AT acceptance,
      catalogue best-practice closure or full WCAG certification.
- [ ] Hand manual zoom/Narrator/real high-contrast/voice checks to H4. Keep #6
      open while required human controls or acceptance remain outstanding.
