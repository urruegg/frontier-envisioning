# Received 1.7.0 selective intake evidence

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-11 |
| Author | Original receipt author not recorded; Copilot AI-assisted evidence maintenance |
| Status | Selective implementation locally verified; human PR review/merge and release acceptance separate |
| Scope | 1.7.0 source receipt and unreleased 1.7.1 execution checkpoints; not release approval |
| References | [Documentation](../README.md), [Issue #22](https://github.com/urruegg/frontier-envisioning/issues/22), [Idea](../ideas/2026-11-10-handover-1.7-intake.md), [Design](../specs/2026-11-10-handover-1.7-intake-design.md), [Plan](../plans/2026-11-10-handover-1.7-intake-plan.md), [SPRINT-003](../sprints/SPRINT-003-handover-1.7-intake.md) |

The supplied snapshot is recorded by [262 source hashes](source-inventory-1.7.0.json)
and the [verbatim received manifest](received-1.7.0-manifest.json).
Its publication/reproduction claims are received evidence, not independently
verified releases. The integrated version is unreleased 1.7.1.

The maintainer approved the [design](../specs/2026-11-10-handover-1.7-intake-design.md)
on 10 November and the [written plan](../plans/2026-11-10-handover-1.7-intake-plan.md)
through human-merged [PR #23](https://github.com/urruegg/frontier-envisioning/pull/23)
and the 11 November instruction at **06:43 +01:00**:

> pr is approved and you can proceed

The source plan commit is `66b7b7b9d699a092c8edfb8203276ee2aac1ed28`; its main
merge is `fdaeec62416b91f5e4286f2849b8cbc27d65b02c`. Approval is recorded on
[#22](https://github.com/urruegg/frontier-envisioning/issues/22), separately from
any readiness/approval labels, which were not changed by an agent.

Execution uses an isolated feature worktree. The original source and existing
protected/release/raster hashes are retained. The P0 tests first failed on the
absent receipt and 1.6.1 version, then passed after generating the receipt and
running the standard 1.7.1 bump tool. Isolated baseline selectors passed
69 tests and 91 subtests before production changes.

## Returned implementation evidence — initial 11 November checkpoint

The parent/worker loop supplied the following historical checkpoints for P4;
the prose worker has no terminal and did not rerun them. Pending statements in
this section are superseded by the final coordinator verification below.

- **P0:** two expected receipt/version failures, then **2 PASS**.
- **P1:** ten received feature tests plus edge privacy, rating/source-ID and
  canonical-order/subset tests; models read-only review **PASS**. The self-test
  reports **39 checks**, retaining the original 34.
- **P2:** all **205 non-raster inputs and 223 rasters** verified for the finite
  1.7.1 demo path. A6 identity ZIP SHA-256:
  `e40b132d2e1d396ad7ee681d09931b3e35cd5728081cb01235b17396059cfdf9`.
  Separate 1.7.1 input-profile pin:
  `d9bd99a7a5ac020f1ade201e898dacd4cb8a6230839707188bb62f250e251a58`.
  These are current checkpoint values, not replacements for historical receipts.
- **P3:** worker completed and reports **58 DOM tests, 50 browser tests,
  168 axe scans, zero WCAG violations reported**. Read-only renderer review is
  pending at this handoff; automated scans are not conformance certification.
- **P4:** current [PRD](../prd.md#171-development-intake) and
  [solution design](../solution-design.md#171-development-intake), all seven
  skill procedures, related guides, Proposed [ADR-0025](../adr/0025-four-part-journey-structure.md)
  and catalogues updated. New acceptance rows remain Pending. Parent local
  header/link/traceability and contract validation has not yet returned.

## Final local integration verification — 11 November

The coordinator verified the complete integrated source after all bounded
reviews and corrections. Model review addressed promoted-risk privacy, current
source ancestry/citation corrections, PRD default/explicit/empty scope parity,
canonical IDs and all supported scaffold statuses. Renderer review addressed
complete Markdown business-value/KPI downloads and immediate scope-badge updates.
All reported findings were reproduced, fixed test-first and re-reviewed clear.
These are advisory reviews, not formal GitHub or human approvals.

| Exact command or inspection | Final result |
|---|---|
| `python tools/dev.py check --strict` | ALL GATES PASSED; 228 tests, 729 subtests, 59 DOM tests, 39 plugin self-checks |
| `python tools/dev.py site e2e --strict` | ALL GATES PASSED; 52 browser tests under the real hosting policy |
| Accessibility result inspection | 168 axe scan states; zero applicable WCAG violations; incomplete/best-practice findings reported separately |
| Responsive result inspection | All seventeen views have 320 CSS pixel document width; wide diagrams/tables/board scroll locally |
| Two normal builds into `dist/distribution-1.7.1` | Both plugin and complete ZIPs are byte-identical across rebuilds |
| Finished archive inspection | Three-file handoff; eleven-entry complete ZIP; embedded plugin and product documents match current source; no analysis/intake records |
| Privacy and checksum inspection | Nested names/content/comments pass the shared guard; zero exact legacy enterprise identifiers; both checksum lines match |
| Offline extracted install preparation | verified=true, no problems, seven skill plans and 73 verified skill files; no actual copy/install performed |
| Provenance inspection | All 240 original protected/fixture files, the 262 received source files, wrapper guide and received manifest remain unchanged |

The one L1 skip is the expected current-release reproduction comparison for
**unreleased 1.7.1**, which has no published release manifest. It is not a skipped
comparison of an existing release. The actual new profile still verifies
205 generated inputs and 223 original raster assets, and the corrected identity
ZIP remains the A6 hash above. The original 1.7.0 manifest is received evidence
only and does not describe these modified output bytes.

Handoff SHA-256:

```text
382ce7e05511e0482baab5afdb3abf44a1ed0e8a7e9dd0d0e9885c095f6bcb64  frontier-envisioning-plugin-1.7.1.zip
51aa9da7047498f3dbf01af072f7edc232ea7ab3efa5a26b1a0660ff0adc0792  frontier-envisioning-1.7.1-complete.zip
```

Generated review evidence:
[PRD desktop](previews/1.7.1/prd-desktop-light.png),
[Plan desktop](previews/1.7.1/plan-desktop-light.png),
[Risks mobile](previews/1.7.1/risks-mobile-dark.png).
These fictitious Caldova screenshots are private PR documentation, not bundle
contents or manual assistive-technology certification.

The draft PR and source-head evidence are linked on
[#22](https://github.com/urruegg/frontier-envisioning/issues/22).
Cloud CI, human review/merge and release acceptance are separate from these
local results. This is a Microsoft-internal development candidate, not a
published 1.7.1 release, actual Cowork install, deployment or external/IP clearance.
Protected routing [#8](https://github.com/urruegg/frontier-envisioning/issues/8)
remains human-only.
