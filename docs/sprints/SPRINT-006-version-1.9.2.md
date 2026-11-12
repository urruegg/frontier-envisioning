# SPRINT-006: Version 1.9.2 internal candidate

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted build preparation |
| Status | Local candidate built and verified; PR/CI and human release decisions separate |
| Scope | Current merged functionality rebuilt as unreleased 1.9.2 |
| References | [Catalogue](README.md), [Issue #33](https://github.com/urruegg/frontier-envisioning/issues/33), [Idea](../ideas/2026-11-12-version-1.9.2.md), [Design](../specs/2026-11-12-version-1.9.2-design.md), [Plan](../plans/2026-11-12-version-1.9.2-plan.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#33](https://github.com/urruegg/frontier-envisioning/issues/33) | [Version-only request](../ideas/2026-11-12-version-1.9.2.md) | [Candidate contract](../specs/2026-11-12-version-1.9.2-design.md) | [Build sequence](../plans/2026-11-12-version-1.9.2-plan.md) | `@urruegg`; parent preparation | Clean merged #32 source; direct 1.9.2 build instruction | Locally verified; no ready/approval labels inferred | Checked implementation `5f04458`; results below; current PR/CI status on #33 |

The direct request on 12 November at 09:21 (+01) authorises this mechanical
candidate scope, not a claim of separate written-plan review or publication.
All previous protected/fixture/receipt hashes are frozen before changes.
Feature behaviour, release records, original raster assets and the private
sharing boundary remain unchanged. Human-only #8/#30 remain separate.

## Version-only source and identity proof

The checked implementation is `5f044585bbda8647363ce32fed981e4048135150`.
The standard bump updated the canonical carriers and archive date. The only
plugin Python change is `PLUGIN_VERSION`; no runtime algorithm changed.
Active reader references are 1.9.2; the starter prompt is unchanged.
Both entire product-document suffixes from the 1.9.1 heading onward and all
262 frozen protected/historical/fixture files remain byte-identical.

Before enabling raster reuse, an actual 1.9.2 SVG probe matched all 205
generated non-raster paths and SHA-256 values against the approved 1.9.1/A6
inputs. Only the named 1.9.2 profile was added; its LF record is pinned at
`b3326eb48d42862979f537c788aa88f16bd40caa0fb96185bc410b9c3e1851c0`.
The same two A6 overrides and original raster assets are retained.
Three expected RED cases became 43 focused tests/82 subtests passing; tampered
record/input/asset/release and unsupported 1.9.3 still reject before writes.

Actual full core and explicit, technically acknowledged Preview builds each
verify 205 inputs and 223 PNGs. Both corrected identity ZIPs remain
`e40b132d2e1d396ad7ee681d09931b3e35cd5728081cb01235b17396059cfdf9`.
The rendered HTML, not intermediate example metadata, identifies 1.9.2.
Core contains no FinOps model; the separate Preview fixture retains its cost
and derived-value limitations and invocation awareness.

## Local quality gates

- `python tools/dev.py check --strict`: `ALL GATES PASSED`, 416 tests,
  one expected unreleased-manifest skip, 1481 subtests, 48 self-test checks
  and 75 DOM tests. Repository/docs/neutrality report zero errors/findings;
  Ruff passes; six existing ESLint warnings remain.
- `python tools/dev.py site e2e --strict`: `ALL GATES PASSED`, 69 browser
  tests, including the actual offline documentation file and Turtle download.
  The inherited 32 unique Preview matrix states remain green under real CSP.
- The tracked HTML, manifest and five actual browser recaptures were regenerated
  and pass stored/fresh documentation drift checks. The five PNG bytes remain
  unchanged because their selected viewports have no visible version change.
  Source, HTML and plugin-version provenance are updated.
- Parent bounded review covers the finite registry/pin, unchanged algorithms,
  current version references, preserved history and actual build contracts.
  No review finding remains. This is technical review, not independent human
  approval, live Cowork validation or manual accessibility certification.

Ignored local logs are `build/evidence/version-1.9.2-l1.log` and
`build/evidence/version-1.9.2-l2.log`. This record is a source-qualified
checkpoint, not a live PR tracker; use #33 for current CI and human review.

## Reproducible internal handoff

`dist/distribution-1.9.2/` contains exactly:

| File | Bytes | SHA-256 |
|---|---:|---|
| `frontier-envisioning-plugin-1.9.2.zip` | 727277 | `093b230893bb9240904c2773c1b58da9433d3a2f66eeeddb0d7f9725883889ac` |
| `frontier-envisioning-1.9.2-complete.zip` | 4468087 | `96498e7976133161f48697001e2dbbdbafd76cb220826682454c11e64e0b3269` |
| `SHA256SUMS.txt` | 210 | `faa83cdb4274566585a70758c3cc6c7c45a3d5fa7ebcaa8da544f93afa2757e8` |

Two actual handoff builds match byte for byte. Between them an independent
full core build in another output directory produced the same seven packaged
HTML/identity/ontology outputs. No golden ZIP was substituted.

Actual archive validation verifies 93 plugin entries against source, eight
skills/85 skill files (seven GA, one optional acknowledgement-required
Preview), fifteen explicit complete entries, fixed 12 November ZIP metadata,
matching embedded bytes/checksums and a clean whole/nested privacy guard.
Actual extracted read-only install preparation verifies eight fresh plans and
eight update plans from a simulated 1.9.1 installation. No files are actually
copied and no saved acknowledgement is inherited.

The ZIPs are internal build candidates, not a published release. Live Cowork
validators/installation, Fabric tenant checks, manual AT/contrast assessment,
external/IP clearance, merge, tag/release, deployment and protected #8/#30 work
remain separate human decisions.
