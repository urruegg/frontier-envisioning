# Testing strategy

## Levels

| Level | Tool | Where | What it proves | Gate |
|---|---|---|---|---|
| Static | Python compile, `tools/check_repo.py`, ruff, ESLint, neutrality scan | `tools/` | sources compile; versions, skill frontmatter, licence, data files, Copilot files and workflow pins are consistent; no customer names, no secrets | L0 |
| Unit and pipeline | `unittest` classes (run by pytest in CI) | `tests/unit/`, `tests/pipeline/` | tools, hooks, site builder and server, release tools, backlog, self-test wrapper and release reproduction behave as specified | L1 |
| Plugin end to end | `tools/selftest.py` (29 checks) | plugin scripts against the Caldova examples | discovery, blueprint build and merge, design scaffold, identity kit, value and FinOps (golden worked example), package and install check | L1 |
| Release reproduction | `tools/verify_release.py` | `releases/<version>/manifest.json` | the sources still build the released artefacts byte for byte (while the version is released) | L1 |
| DOM | `node:test` with happy-dom | `tests/dom/` | the 14 views render; Agent Factory, attendees, architecture, use cases, readiness, identity, value and FinOps behave; notes are saved | L1 |
| Browser | Playwright, Chromium | `tests/e2e/` | the showcase works in a real browser under the hosting headers (CSP, sign-in routes off locally), screenshots of every view | L2 |
| Infrastructure | `az bicep build` | `infra/` | the templates compile | CI `IaC validation` |
| Deployment | `tools/smoke_site.py` | deployed showcase | sign-in enforced, GitHub sign-in off, headers present | L2 deploy |
| Cowork | Cowork skill validators and the behavioural prompts of PRD B.9 | Copilot Cowork | skills route correctly and pass Cowork's structural and security checks | release checklist |

## Test data

Only fictitious data: the Caldova examples in the plugin, synthetic transcripts and Office themes created inside the tests, stand-in terms (for example "Fabrikam Rail") for the neutrality tests. Never a real customer, person or engagement.

## Rules

- Strict `python tools/dev.py ci` includes both unit and pipeline suites. A release-reproduction failure remains blocking even when other suites pass; do not bump a preserved baseline or rewrite expected hashes merely to bypass it.
- Package ordering uses case-sensitive relative paths and fixed Unix ZIP creator metadata on every host. PNG converter availability and generated metadata still require separate demo reproduction evidence.
- Demo text is canonicalised to LF before hashing; identity archives preserve binary data and fixed timestamps while using sorted entries and Unix creator metadata. The default demo requires the reported card/visual PNGs to exist. Only an explicit `--no-png` development build permits SVG-only output; it does not satisfy release reproduction.
- Restore the original raster renderer/version/font profile before expecting identity ZIP byte equality. Do not add general line-ending normalization to the verifier or rewrite release hashes. The existing generated-date comparison remains the only HTML verifier normalization.
- The preserved 1.4.0 baseline instead uses verified original raster inputs: 223 PNGs guarded by the inventory and hashes of all 205 regenerated non-raster files. The build regenerates the README and packages all 429 files; full artifact hashes are still checked. Reports distinguish `restored` pixels from live `converted` pixels. Changed inputs or tampered assets fail, and future versions do not inherit this historical profile automatically.
- Browser tests use project-local Playwright downloads by default and do not prove Azure tenant authentication.
- Tests are deterministic and offline; they write only to temporary folders or `build/`.
- A bug fix comes with a regression test that fails before the fix.
- A flaky test is fixed or quarantined within a day; CI retries browser tests once at most.
- Assertions name the behaviour, not the implementation; DOM selectors live in the test files and change with the renderer.
- New views and interactions get DOM tests; layout-sensitive changes also the browser test.
