# SPRINT-010: PR-gated engineering and release automation

| Field | Value |
|---|---|
| Version | 0.4 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Subagent plan/readiness approved at e8ea6bd; #49 contracts and #50 bootstrap/full local gates verified, adoption pending |
| Scope | Staged private Pro machine-authored PRs, actual human review and trusted engineering/release execution |
| References | [Catalogue](README.md), [Decision #48](https://github.com/urruegg/frontier-envisioning/issues/48), [Idea](../ideas/2026-11-14-pr-gated-operating-model.md), [Specification](../specs/2026-11-14-pr-gated-operating-model-design.md), [Plan](../plans/2026-11-14-pr-gated-operating-model-plan.md), [ADR-0030](../adr/0030-pr-gated-engineering-automation.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#48](https://github.com/urruegg/frontier-envisioning/issues/48) | [Outcome](../ideas/2026-11-14-pr-gated-operating-model.md) | [G48-01 to G48-09](../specs/2026-11-14-pr-gated-operating-model-design.md#acceptance-and-verification) | [Slices A-D, Tasks 0-5](../plans/2026-11-14-pr-gated-operating-model-plan.md) | `@urruegg` accountable | Supported restricted identity; actual maintainer adoption/pilots | Slice A contracts verified; bootstrap/coordination/release not active | Spec `8de16ca`, plan/readiness `e8ea6bd`; no native-review/pilot/publication result |
| [#49](https://github.com/urruegg/frontier-envisioning/issues/49) | [Proposal boundary](../ideas/2026-11-14-pr-gated-operating-model.md) | [G48-03/G48-04/G48-07](../specs/2026-11-14-pr-gated-operating-model-design.md#acceptance-and-verification) | [Task 1](../plans/2026-11-14-pr-gated-operating-model-plan.md#task-1-test-the-authority-contract-before-implementing-it) | `@urruegg` accountable | Actual future trusted collector/adoption for operational use | Pure contracts locally implemented and reviewed | `b274e817`: 50 focused tests, both advisory stages passed, full strict local gate passed |
| [#50](https://github.com/urruegg/frontier-envisioning/issues/50) | [Bootstrap boundary](../ideas/2026-11-14-pr-gated-operating-model.md) | [G48-04/G48-06/G48-09](../specs/2026-11-14-pr-gated-operating-model-design.md#acceptance-and-verification) | [Task 2](../plans/2026-11-14-pr-gated-operating-model-plan.md#task-2-generate-and-review-the-maintainer-bootstrap-package) | `@urruegg` accountable | Verified #49 contracts; actual person adoption remains a later stop | Generator implemented, reviewed and locally verified; live adoption blocked | `5a61b400`: 41 focused tests, both advisory stages passed, actual five-file output, full strict local gate passed |

## Actual decisions

The maintainer confirmed current GitHub Pro, selected
`formal-review-machine-author`, selected `engineering-and-releases`,
then `approve-pr-gated-engineering-concept`. The specification/Proposed ADR
were written and committed at
`8de16ca089ba0e2a1787496a4c65ecf17b7b6b4e`.
The separate `approve-written-pr-gated-spec` response approved that actual
written proposal for planning. The later explicit plan/readiness approval
at `e8ea6bd` requested subagent-driven implementation and real end-to-end
evidence. The additional `releases-native-zip` choice retained Release
downloads rather than a Packages registry wrapper.

No current guard, native rule, App/key/store, owner credential, tag or
publication permission was activated. Protected labels, assignment/milestone
fields and formal GitHub review are not inferred.

## Slice readiness and preservation

A-D are bounded future implementation work packages, not invented GitHub
issues. Create real linked child issues after plan approval and before
starting/delegating them; split anything larger than M. Bootstrap/person-only
actions must not be assigned to coding agents.

Planning is isolated on `docs/48-pr-gated-operating-model`, based on actual
approved main `2d5a7cc`. #47 remains preserved at the maintainer-created
`aa838fbb`; its code/context is not silently converted into this successor
authority model. The existing 1.10.0 tag/product bytes remain unchanged.

The source/issue/PR host stays private. Azure, administration, destructive
operations, secrets and public visibility are outside routine execution.
One-time maintainer adoption and supported credential/provider isolation
remain real preconditions, including the protected routing dependency #8.

## Verification boundary

At `8de16ca`, documentation/neutrality validation passed for the design-only
changes. That is not production implementation, native gate, App identity,
pilot, source-build or publication evidence.

The proposed official App-token action v3 ref was verified read-only as
`64ab729a6294000f5aa4a4bc0b73d1f32bc45510`; its current documentation uses
`client-id`, not an invented private credential. No dependency, key or
resource was installed while planning.

## #49 pure-contract implementation and ordered review

The bounded builder changed only `tools/pr_gate.py` and
`tests/unit/test_pr_gate.py`. Actual RED/GREEN covered the four checking APIs
and CLI. Separate advisory review found canonical Git-path case widening,
inadequate annotated-tag facts, an unsafe Unicode diagnostic and a later
protected-directory-root gap. Each was fixed by the same implementer with
observed failing regressions, not waived.

At `b274e81703b5f27becff7a4a11ad6d764bf640fb`, all **50 focused tests**
passed; the reviewer confirmed both specification and correctness/quality,
with 14 targeted regressions and 72 bounded interface/purity probes.
This is advisory review and synthetic contract evidence, not actual human
GitHub approval or live App provenance.

An early full-gate attempt overlapped fixture edits and failed; it was not
accepted. Parent strict verification then exposed missing ESLint in the
new worktree. Existing lockfile dependencies were restored with
`npm ci --no-audit --no-fund`, without manifest changes. Partial runs stopped
before further code fixes were also not reported as passing.

The final stable `python tools/dev.py check --strict` at `b274e817` ended
**ALL GATES PASSED**:

- **762 unit/pipeline tests passed**, one expected current-unreleased-version
  skip; **2,551 subtests passed**.
- **68 plugin self-tests** and **183 DOM tests** passed.
- Repository/lint/docs/neutrality/template, actual package/demo, ten-image
  gallery drift and existing release-reproduction step passed. The current
  1.10.0 immutable publication manifest is still absent; that expected
  work-towards-release state is not a published-release comparison.
- Package SHA-256 remains
  `9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`.
  No plugin bytes/version or protected workflow changed.

Full log: `build/evidence/approval49-check-b274e817.log`.
Six inherited ESLint warnings remained; zero errors.

The later stable `python tools/dev.py site e2e --strict` at documentation
checkpoint `b706c5f13ceb51591bfa76d1c90df891dadfd42c` passed **75 Chromium
browser tests** and ended **ALL GATES PASSED**. The source was committed
before the run; no code or fixture edits overlapped it. Local testing used
`SITE_AUTH_MODE=none`, not a deployment/authentication change.
Full log: `build/evidence/approval49-l2-b706c5f.log`.
This verifies local product/showcase behaviour, not a real machine-authored
PR, native approval, credential boundary or publication pilot.

Read-only live inventory showed no repository variables/secrets or native
main protections. The planned App client/key and actual adoption were not
configured. The README already links to Releases, whose page still listed
none. Bootstrap preparation and actual identity/native-gate/publishing/
download evidence remain the next stages.

## #50 reviewable bootstrap package

The fresh bounded builder changed only
[the generator](../../tools/governance_bootstrap.py) and
[its tests](../../tests/unit/test_governance_bootstrap.py).
Ordered advisory review identified two specification gaps: operative legacy
release instructions survived contrary appended notes, and applicable
instruction-file amendments were missing. Semantic RED/GREEN reconstruction
tests verified their fixes at `4a77d895`.

The deferred quality stage then reproduced source-hardlink confinement and
JSON decoder/non-finite input bugs. These were fixed separately, test-first,
at `5a61b400470cdf19a259abde017d65841e20161e`.
The reviewer confirmed specification **PASS**, then quality **PASS**:

- **41 focused tests:** 37 passed, four Windows symlink-privilege skips.
  All four actual Windows junction cases passed.
- Three actual source-hardlink cases failed before any source-content read
  or output; immediate rechecks also blocked links introduced after preflight.
- Eleven JSON input cases failed explicitly without output, while unrelated
  programming errors propagated. The CLI's catch was not broadened.
- All 33 missing/drifted/duplicate-anchor or missing-instruction cases failed
  before output. Determinism, overwrite/path refusal, scoped Ruff and
  neutrality checks passed. The previous production had seven failing
  quality-regression cases when loaded in memory.

The parent verified clean committed source and ran
`python tools/governance_bootstrap.py`: **exit 0**, exactly five inert files
under `build/governance-bootstrap/`. Existing initial output was preserved
under ignored evidence; tracked source remained unchanged. Output comprises
the proposed migration patch, settings/App descriptors, validation report and
one operator checklist. Generation explicitly says **adoption BLOCKED;
publication not authorised**. No active template, guard, routing, workflow,
credential or setting was changed.

The stable `python tools/dev.py check --strict` at `5a61b400`, after both
review stages with no overlapping edits, ended **ALL GATES PASSED**:

- **799 unit/pipeline tests passed**, **five skips**: four Windows
  symlink-privilege cases and the expected current-unreleased-version case.
  **2,595 subtests passed**.
- **68 plugin self-tests** and **183 DOM tests** passed; zero DOM failures/skips.
- Lint/docs/neutrality/template, package/demo/gallery drift and the existing
  reproduction step passed. Six inherited ESLint warnings; zero errors.
- Plugin SHA-256 remains
  `9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`.

Full log: `build/evidence/approval50-check-5a61b400.log`.
The earlier 75-test local L2 product-preservation result remains separately
qualified to `b706c5f`; no new live governance/browser pilot is claimed.

This completes the bounded local generator preparation, not Slice A's actual
identity/adoption proof or stages B-D. Trusted collectors/parser/coordinator,
provider credential separation, native protections, real App-authored review
and publisher/download evidence remain absent or unverified. Current
person-only controls and the human #8 routing dependency still apply.
