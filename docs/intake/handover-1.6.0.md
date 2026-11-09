# 1.6.0 handover intake evidence

Date: 2026-11-09

## Scope

Selective intake of the Cowork 1.6.0 product into the approved private
`urruegg/frontier-envisioning` repository. Base:
`4ad94506fdf3a21b59806a58572784085421d36a`, the merged 1.4.0 intake.

The user requested intake. The follow-up scope form was unavailable, so the
preservation-first default was used: import the released product and matching
tests/documents, retain hardened engineering, and deliver a draft PR.
No readiness/approval labels, server settings, merge, tag, release or
deployment actions were performed.

Sources: the supplied local 1.6.0 engineering folder and original OneDrive
task output. [Received source inventory](source-inventory-1.6.0.json).
[Design](../plans/2026-11-09-handover-1.6-design.md) and
[implementation plan](../plans/2026-11-09-handover-1.6-plan.md).

## Product changes received

- 1.5.0: digital feedback loop with four areas and the official Microsoft IQ
  layers, animation/pause/reduced-motion and workshop verdicts.
- 1.6.0: authored/derived workflows, typed nodes and triggers, branch/container
  validation, properties/keyboard/zoom/layout interactions and solution-design
  node tables.
- Seven skills retained; blueprint skill gains `workflow.py`.
- Version-aligned product README, CHANGELOG, PRD, analysis, ADRs and backlog.
- Supplied feature unit, DOM and browser tests.
- Supplied 1.5.0/1.6.0 owner-authored release records copied verbatim.

The received snapshot has 256 files: seven added and 72 changed relative to the
captured 1.4.0 export, with no removals. A curated 149-file import included
unchanged source companions; only actual delta files appear in the commit.

The 84 product/renderer files match the supplied snapshot, including generated
template and installation inventory after regeneration. No hand editing of
those generated files occurred.

## Preserved engineering

The following remained byte-identical to merged main:

- Python/Node locks and pre-commit pins.
- CODEOWNERS and guard hooks.
- All existing GitHub workflows and Actions pins.
- Developer runner, package portability fixes and original 1.4.0 record.
- Historical raster fixture manifest/assets.

The demo/raster helpers were extended only to explicitly support the received
1.5/1.6 versions. Current records must expect the same original identity hash;
changed inputs, tampered assets and unsupported future versions still fail.
Customer-facing plugin behavior and historical verification rules are not
replaced by a silent fallback.

## Test-first evidence

The supplied DOM tests were run on 1.4.0 before implementation:
eight passed and two failed for the missing feedback loop and workflow view.
The explicit received-version raster compatibility assertion also failed
before the supported set was added.

After intake:

| Check | Result |
|---|---|
| Targeted feedback-loop/workflow/profile selection | 25 passed |
| Strict unit/pipeline suite | 83 passed |
| Plugin self-test | 34 passed |
| DOM suite | 14 passed |
| Chromium suite | 7 passed |
| Template drift and repository checks | Passed |
| Ruff | Passed |
| ESLint | 0 errors; 6 received warnings retained |
| Neutrality source/archive checks | 0 findings |
| Original 1.6.0 artifact reproduction | 4 of 4 matched |

Exact commands:

```powershell
node --test tests\dom\blueprint.test.mjs
# Before implementation: two expected feature failures.

python -m pytest tests\unit\test_feedback_loop.py tests\unit\test_workflow.py tests\unit\test_demo_raster.py -q
# Passed: 25 tests.

python tools\dev.py check --strict
# ALL GATES PASSED.

python tools\dev.py site e2e --strict
# Passed: Chromium 7/7.
```

Strict gate summary:

```text
ok  template drift: 301711-byte template
ok  lint and repository checks
ok  customer-neutrality scan
ok  unit/pipeline tests: 83 passed
ok  plugin self-test: 34 passed
ok  package
ok  Caldova demo
ok  release reproduction: 4 of 4 artefacts reproduced
ok  DOM tests: 14 passed
ok  source/built-artifact neutrality scan
ALL GATES PASSED
```

## Immutable artifact evidence

| Artifact | Expected and reproduced SHA-256 |
|---|---|
| Plugin ZIP, 570571 bytes | `fa70f00ce604fdc59fec08f91979f02670e9ce4ead395a042d70eaa61ddc1207` |
| Blueprint HTML, generated-date normalized | `46ad35f1c5d171607ad80860e3ba28d55f1a01e4f5453cc51f2fd0c94de5fe15` |
| Identity ZIP, 3308707 bytes | `2026c84c5806e0b8c2003e837f15e635fb78f2fa79f247164c47c1a5b51a5400` |
| Identity catalogue | `08e2da864f13575d0a630d90954e81a06283a1082a32cf10adfd30d038fa20f1` |

The original plugin ZIP was also hashed directly from the OneDrive output.
The original complete 1.6.0 bundle is 4235094 bytes with SHA-256
`d10628751cd2812883194f3f8252245eaf474226c4f2e5ca73526c590b78c6cc`.
That Cowork bundle is provenance evidence, not a claim that our custom
complete-bundle builder reproduces it.

The identity ZIP and catalogue are unchanged from 1.4.0. Their explicit reuse
retains all non-raster input guards and verifies the current 1.6.0 record.
Historical FinOps age uses the release date. No expected hash was rewritten.

## Visual review and remaining human checks

Chromium exercised fourteen views, feedback-loop animation/pause/reduced
motion, workflow keyboard/properties/designer layout, notes, deep links and CSP.
Screenshots are under ignored test output and the Playwright report.

Visual inspection of the scrolled designer-row screenshot shows the sticky
agent list overlapping the workflow's left legend. This is present in the
received, byte-verified renderer; the behavioral tests do not assert that
occlusion. It is recorded as a baseline visual limitation for review, not
silently repaired inside an immutable 1.6.0 import. A correction needs a
separate versioned change and a layout regression test.

Actual Cowork installation/connector/persistence validation and server
CODEOWNERS/review/environment setup remain human checks. Local success is not
tenant deployment or release publication.

Logs: `v16-dom-red.log`, `v16-unit-targeted.log`, `v16-check.log` and
`v16-browser.log` under ignored `build/intake/`. The existing isolated
Python 3.11/Node 24 toolchain was used; CI retains Python 3.12/Node 22.
