---
name: frontier-dev-loop
description: Build, test and verify changes in the Frontier Envisioning repository with its quality gates L0 to L3 (python tools/dev.py). Use when asked to run the tests, check a change, fix a failing gate or CI run, rebuild the template, package or demo, or before declaring any task done in this repository.
---
# Frontier dev loop

## Gates

| Gate | Command | Runs where | Contents |
|---|---|---|---|
| L0 | `python tools/dev.py precommit` | pre-commit, CI | template drift, Python compile, repository rules, ruff, ESLint, customer neutrality |
| L1 | `python tools/dev.py check` (`ci` = strict) | CI job `L1 quality gate` | L0, unit and pipeline tests, plugin self-test (34 checks for 1.6.0), package, Caldova demo, release reproduction, DOM tests, scan of built archives |
| L2 | `python tools/dev.py site e2e` | CI job `L2 browser tests`, deploy to dev | showcase site with hosting headers, Playwright on Chromium, screenshots |
| L3 | tag `vX.Y.Z` (people) | enabled `release` workflow, `release-approval` | strict L1 and L2 on the tag, bundle, pinned SBOM, provenance attestation, draft release |

## Loop

1. `python tools/dev.py doctor` once per machine; `python tools/dev.py setup` installs pytest, ruff, PyYAML, happy-dom, ESLint and Playwright.
2. While working: `python tools/dev.py test` (fast) and the specific step you touch: `template`, `selftest`, `package`, `demo`, `dom`.
3. Before you finish: `python tools/dev.py check`. Quote the summary block in the pull request.

## Fixing failures

- **Template drift**: edit `src/renderer/*`, run `python tools/dev.py template`, commit the generated template.
- **Stale `plugin-install.json`**: `python tools/dev.py package`, commit the file.
- **Release reproduction failed**: compare source hashes, archive metadata/order, converter availability and generated data before assuming a product change. Preserve release records and report unresolved differences. Bump only for an approved shipped-product change, never merely to skip the baseline check.
- **Historical raster profile failed**: the received 1.4/1.5/1.6 records must expect the original identity ZIP hash. Inspect the reported generated-input difference; all 205 non-raster inputs are checked before replaying 223 PNGs. Never loosen hashes, enable arbitrary future versions or copy the golden ZIP over a changed build.
- **Neutrality finding**: replace the content with Caldova data. Never add the term anywhere else.
- **Repository rules**: the message names the file and the rule (versions, skill frontmatter, licence, JSON/YAML, workflow pins, secrets).
- **DOM test failed**: run `node --test tests/dom/blueprint.test.mjs` with `BLUEPRINT_HTML` pointing at `build/demo/...html` and read the assertion; selectors live in the test file.
