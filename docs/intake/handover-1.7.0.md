# Received 1.7.0 selective intake evidence

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-11 |
| Author | Original receipt author not recorded; Copilot AI-assisted evidence maintenance |
| Status | Received evidence; selective implementation in progress, final acceptance pending |
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

## Returned implementation evidence — 11 November

The parent/worker loop supplied the following checkpoints for P4; the prose
worker has no terminal and did not rerun these checks.

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

Implementation, final strict L1/L2 and distribution acceptance remain in
progress. This record must not be read as a completed 1.7.1 release, an actual
Cowork installation, deployment or external distribution approval.

Finished ZIP/privacy/checksum/rebuild and offline seven-skill install-plan checks
remain for P5, as does integrated review. The private repository and
Microsoft-internal development boundary remain; customer export, WIP/readiness
or metadata is not external/IP approval. Protected routing
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) remains human-only.
