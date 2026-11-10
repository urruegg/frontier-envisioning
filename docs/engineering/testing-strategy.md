# Testing strategy

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-10 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Test levels and evidence guide; document revision, not product version |
| References | [Documentation](../README.md), [Tests](../../tests/README.md), [Engineering handbook](handbook.md), [Product quality and testing](../solution-design.md#b9-quality-and-testing) |

## Levels

| Level | Tool | Where | What it proves | Gate |
|---|---|---|---|---|
| Static | Python compile, `tools/check_repo.py`, ruff, ESLint, neutrality scan | `tools/` | sources compile; versions, skill frontmatter, licence, data files, Copilot files and workflow pins are consistent; no customer names, no secrets | L0 |
| Unit and pipeline | `unittest` classes (run by pytest in CI) | `tests/unit/`, `tests/pipeline/` | tools, hooks, site builder and server, release tools, backlog, self-test wrapper and release reproduction behave as specified | L1 |
| Plugin end to end | `tools/selftest.py` (34 checks for 1.6.0) | plugin scripts against the Caldova examples | discovery, blueprint/feedback-loop/workflow validation and merge, design scaffold, identity kit, value/FinOps, package and install check | L1 |
| Release reproduction | `tools/verify_release.py` | `releases/<version>/manifest.json` | the sources still build the released artefacts byte for byte (while the version is released) | L1 |
| DOM | `node:test` with happy-dom | `tests/dom/` | the 14 views render; Agent Factory, attendees, architecture, use cases, readiness, identity, value and FinOps behave; notes are saved | L1 |
| Browser | Playwright, Chromium | `tests/e2e/` | the showcase works in a real browser under the hosting headers (CSP, sign-in routes off locally), screenshots of every view | L2 |
| Infrastructure | `az bicep build` | `infra/` | the templates compile | CI `IaC validation` |
| Deployment | `tools/smoke_site.py` | deployed showcase | sign-in enforced, GitHub sign-in off, headers present | L2 deploy |
| Cowork | Cowork skill validators and the behavioural prompts of PRD B.9 | Copilot Cowork | skills route correctly and pass Cowork's structural and security checks | release checklist |

## Test data

Only fictitious data: the Caldova examples in the plugin, synthetic transcripts and Office themes created inside the tests, stand-in terms (for example "Fabrikam Rail") for the neutrality tests. Never a real customer, person or engagement.

## Accessibility: automation and human acceptance

The target is WCAG 2.2 AA; passing automation is not certification.
`tests/dom/accessibility.test.mjs` adds structural regressions alongside the
existing DOM suites. `tests/e2e/accessibility.spec.mjs` exercises real browser
keyboard behaviour and injects the locally installed, development-only
axe-core **4.11.0** through browser evaluation. It checks actual hosting CSP
headers without a CDN, runtime dependency, `bypassCSP` or policy exception.

Applicable `wcag2a`, `wcag2aa`, `wcag21a`, `wcag21aa` and `wcag22aa` violations
fail the browser test. Soft assertions allow remaining states to run, not to
pass despite failures. Full reports retain best-practice-only violations and
incomplete checks separately; neither is silently discarded.

Coverage includes all fourteen views in light/dark, architecture tabs,
workflow properties, evidence modal, filtered Org/portfolio states, the site
index and identity catalogue. Sampled white, black and blue brand colours
preserve data/icon values while checking rendered foregrounds. Automated
keyboard regressions cover closed-drawer exclusion, modal focus/return and
prior inert-state restoration, replacement/reopen races, reduced motion,
labelled roving tabs and pressed filters. Target checks measure selected
checkbox/evidence/resource controls at least 24 × 24 CSS pixels. Reflow checks
measure all pages at 320 CSS pixels (maximum document width 321px) and preserve
local workflow scrolling. These are automated tests, not manual AT sign-off.

### Recorded blocker and targeted catalogue correction

The retained full browser report for renderer HEAD `4969c13` has **41 passed,
2 failed** tests. Blueprint states, the site index and sampled brand/filter
states are clean for applicable axe rules. Catalogue text contrast still
fails AA in both schemes: Later wave **4.40:1**, Finance header **4.33:1**
(required normal-text ratio 4.5:1). This is not merely the original
best-practice empty-header finding. Full L2 is red; no gating waiver,
catalogue assertion skip or hosted-copy workaround is authorised.

Those are the recorded pre-correction results, not a claim that the tests are
flaky. The user's subsequent request to solve PR #15's linked failure
authorises the targeted generator/current-version correction in
[A6](../plans/2026-11-09-accessibility-plan.md#task-a6-targeted-catalogue-ci-correction-2026-11-10).
Historical profile and release records remain excluded.

The correction must leave the AA assertions enabled. Unit tests cover rendered
status colour pairs and opaque header text. The 1.6.1 build separately verifies
its two deliberately changed catalogue inputs while retaining all other
historical input and PNG checks. A present current release record must match
the completed rebuilt identity archive, not be mistaken for the historical
archive that supplies raster provenance. Missing, malformed or tampered
verification data fails explicitly.

The [dated handoff](../intake/2026-11-10-accessibility-verification.md) retains
earlier results and records the fresh A6 local/cloud results separately.
Repeat builds must produce identical catalogue/identity hashes, without
copying a golden archive or updating immutable historical hashes.

Human #8 still owns Narrator/screen-reader, 200–400% zoom, real Windows
high-contrast and voice acceptance. Axe has incomplete SVG coverage; rendered
composites, focus indicators, screenshots and diagram reachability also need
review. Automated acceptance is recorded only after the actual L1/L2 results;
L1 success cannot waive L2 or
replace those human checks.

The initial A5 strict L1 attempt stopped at `ProductDocumentSplit` contracts
that pin PRD/design metadata to 2026-11-09 and hash the original patch note
and A.8/B.5/B.9 sections. Requested real-date maintenance and development
documentation needed the bounded correction `2703703`, which preserved
historical hashes/results while allowing actual dates and named development
additions. Do not backdate documents or silently update preservation fixtures.
The [handoff](../intake/2026-11-10-accessibility-verification.md#fresh-a5-checks-2026-11-10)
records that initial failure separately from the subsequently passing full
L1 verification.

## Rules

- Strict `python tools/dev.py ci` includes both unit and pipeline suites. A release-reproduction failure remains blocking even when other suites pass; do not bump a preserved baseline or rewrite expected hashes merely to bypass it.
- Package ordering uses case-sensitive relative paths and fixed Unix ZIP creator metadata on every host. PNG converter availability and generated metadata still require separate demo reproduction evidence.
- Demo text is canonicalised to LF before hashing; identity archives preserve binary data and fixed timestamps while using sorted entries and Unix creator metadata. The default demo requires the reported card/visual PNGs to exist. Only an explicit `--no-png` development build permits SVG-only output; it does not satisfy release reproduction.
- Restore the original raster renderer/version/font profile before expecting identity ZIP byte equality. Do not add general line-ending normalization to the verifier or rewrite release hashes. The existing generated-date comparison remains the only HTML verifier normalization.
- The preserved 1.4.0 baseline instead uses verified original raster inputs: 223 PNGs guarded by the inventory and hashes of all 205 regenerated non-raster files. The build regenerates the README and packages all 429 files; full artifact hashes are still checked. Reports distinguish `restored` pixels from live `converted` pixels. Changed inputs or tampered assets fail, and future versions do not inherit this historical profile automatically.
- A released demo's FinOps rate-age calculation uses its recorded release date through the script's existing `--today` input. This prevents an overnight build from changing the historical demo hash; customer-facing rate-age checks and the verifier's normalization rules remain unchanged. Explicit SVG-only development builds still use the current date.
- The received 1.5/1.6 releases explicitly share the historical raster profile only because their current release record expects the same original identity ZIP. Unsupported future versions and a changed identity hash are rejected. The new unit/DOM/browser cases cover feedback-loop animation, workshop verdicts, workflow derivation/validation, keyboard properties and designer layout.
- The 1.6.1 preview explicitly reuses unchanged identity inputs with 1.6.0 provenance only while its own release record is absent. An existing current record is always checked; other future versions remain unsupported. This does not create release hashes or claim a preview is published.
- Layout acceptance includes scrolled geometric non-intersection, actual pointer hit-testing, correct legend activation without agent changes, responsive keyboard input and preserved agent switching. Screenshots supplement these assertions rather than replace them.
- Browser tests use project-local Playwright downloads by default and do not prove Azure tenant authentication.
- Tests are deterministic and offline; they write only to temporary folders or `build/`.
- A bug fix comes with a regression test that fails before the fix.
- A flaky test is fixed or quarantined within a day; CI retries browser tests once at most.
- Assertions name the behaviour, not the implementation; DOM selectors live in the test files and change with the renderer.
- New views and interactions get DOM tests; layout-sensitive changes also the browser test.
