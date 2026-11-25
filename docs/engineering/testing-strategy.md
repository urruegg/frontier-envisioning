# Testing strategy

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-25 |
| Author | Original author not recorded; Copilot AI-assisted maintenance; AI assistant (AI-assisted #70 release evidence guidance) |
| Status | Maintained; approval not inferred |
| Scope | Test levels and evidence guide; document revision, not product version |
| References | [Documentation](../README.md), [Tests](../../tests/README.md), [Engineering handbook](handbook.md), [Product quality and testing](../solution-design.md#b9-quality-and-testing), [Release evidence adoption](release-evidence-adoption.md), [Approved #67 spec](../specs/2026-11-24-release-evidence-simplification-design.md) |

## Levels

| Level | Tool | Where | What it proves | Gate |
|---|---|---|---|---|
| Static | Python compile, `tools/check_repo.py`, ruff, ESLint, neutrality scan | `tools/` | sources compile; versions, skill frontmatter, licence, data files, Copilot files and workflow pins are consistent; no customer names, no secrets | L0 |
| Unit and pipeline | `unittest` classes (run by pytest in CI) | `tests/unit/`, `tests/pipeline/` | tools, hooks, site builder and server, release tools, backlog, self-test wrapper and release reproduction behave as specified | L1 |
| Plugin end to end | `tools/selftest.py` (34 checks for 1.6.0) | plugin scripts against the Caldova examples | discovery, blueprint/feedback-loop/workflow validation and merge, design scaffold, identity kit, value/FinOps, package and install check | L1 |
| Release reproduction | `tools/verify_release.py` | exact-version GitHub Release assets; validated ignored cache offline; explicit retained manifests for history | matching source outputs reproduce the published artefacts, with the existing generated-date normalisation only; absent offline evidence is not verification | L1; fresh lookup in CI |
| DOM | `node:test` with happy-dom | `tests/dom/` | the 14 views render; Agent Factory, attendees, architecture, use cases, readiness, identity, value and FinOps behave; notes are saved | L1 |
| Browser | Playwright, Chromium | `tests/e2e/` | the showcase works in a real browser under the hosting headers (CSP, sign-in routes off locally), screenshots of every view | L2 |
| Infrastructure | `az bicep build` | `infra/` | the templates compile | CI `IaC validation` |
| Deployment | `tools/smoke_site.py` | deployed showcase | sign-in enforced, GitHub sign-in off, headers present | L2 deploy |
| Cowork | Cowork skill validators and the behavioural prompts of PRD B.9 | Copilot Cowork | skills route correctly and pass Cowork's structural and security checks | release checklist |

## Test data

Only fictitious data: the Caldova examples in the plugin, synthetic transcripts and Office themes created inside the tests, stand-in terms (for example "Fabrikam Rail") for the neutrality tests. Never a real customer, person or engagement.

## Release evidence modes

The [approved #67 spec](../specs/2026-11-24-release-evidence-simplification-design.md)
and [plan](../plans/2026-11-25-release-evidence-simplification-plan.md)
govern the developer-side resolver. Plugin scripts remain offline,
deterministic and standard-library-only; no feature/version change is involved.
Normally build the package/demo before comparison.

| Entry point | Network policy and outcome |
|---|---|
| `python tools/verify_release.py` | Offline by default. A valid matching cache is compared; a genuine miss reports `not-performed`, not development or verified publication. |
| `python tools/verify_release.py --online` or standalone with `CI=true` | Fresh authoritative lookup of the exact current plugin version, never `latest`; no cached absence claim. |
| `python tools/dev.py verify-release` or local `check` | Offline cache comparison. A miss remains visible in the step and final summary: `LOCAL CHECKS COMPLETED; published-release verification NOT PERFORMED`. Other local checks passing do not make that comparison pass. |
| `python tools/dev.py ci` or task runner with `CI=true` | Fresh lookup. Only successful reproduction or confirmed absence of both exact published release and conflicting tag permits the release step to pass. Other gates must also pass for `ALL GATES PASSED`. |
| Local `python tools/dev.py check --strict` | Requires installed development tools; does not itself enable networking. |
| Explicit `--manifest` (optionally `--force`), `--write` or `--local-source` paths | Network-free historical/writer interfaces, even in CI. A missing explicit manifest or wrong version without `--force` is `ERROR`, exit 1, never an unreleased-version skip. `--force` permits a different manifest version only with matching historical source outputs, not new-source substitution. |

The reviewed Python consumer is
`check(root, version, online=False)` (`online` is keyword-only). It returns
`status`, `version`, `source_commit`, `manifest` and `message`. Status is
`verified`, `development` or `not-performed`; the latter two carry no manifest
or source commit. Invalid evidence/comparison raises `ValueError`, including
`EvidenceError`; the CLI/gate fails, never a success fallback. The underlying
resolver's `published` state means validated evidence, not completed build
comparison.

An online lookup first establishes access to `github.com` repository
`urruegg/frontier-envisioning`, completes bounded release enumeration and
checks the exact tag. Authentication/404/network failures are not proof of
absence. Drafts, tag-without-release, missing/duplicate/unexpected assets,
wrong version/source/tag, malformed manifests, bad hashes/ZIPs and invalid
cache all fail explicitly. Requests and raw downloads are bounded; only
STORED/DEFLATED ZIP streams are accepted, with raw size/CRC/complete-stream
checks matching the actual published assets.

Validated evidence is cached only under ignored
`build/release-evidence/<version>/<source-commit>/`. Offline reuse requires
the exact local annotated tag and revalidates source/tag identity, all four
raw assets, checksum rows, manifest and ZIP limits. CI always looks up
authoritative evidence afresh. Cache consistency and SHA-256 are not signatures,
independent approval or protection against replacement of all local evidence.

The [asset inventories](release-evidence-adoption.md#two-distinct-inventories)
distinguish four downloads from four reproduction artefacts. Preserve
historical tags/assets/provenance/records and existing explicit-manifest use;
compare 1.10.0 only with its matching historical outputs, not current 1.10.1.
Future releases need no copied `releases/` manifest.

Unit fixtures exercise the real validation/cache code with deterministic
GitHub-boundary responses and temporary files, not a live service. Actual
read-only integration proof is recorded separately in the
[25 November verification checkpoint](../solution-design.md#release-evidence-verification-25-november-2026).
Normal CI has step-level read-only token wiring in #69; the protected
release workflow's equivalent remains a
[one-time human handover](release-evidence-adoption.md#one-time-protected-workflow-handover).
No final strict gate, PR #71 CI or protected adoption is claimed here.

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
- Unit tests are deterministic and offline; they write only to temporary folders or `build/`. CI's separate release-evidence lookup intentionally uses GitHub; access/network failures fail that gate rather than downgrade it.
- A bug fix comes with a regression test that fails before the fix.
- A flaky test is fixed or quarantined within a day; CI retries browser tests once at most.
- Assertions name the behaviour, not the implementation; DOM selectors live in the test files and change with the renderer.
- New views and interactions get DOM tests; layout-sensitive changes also the browser test.
