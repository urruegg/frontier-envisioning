# Received 1.7.0 selective intake evidence

Date: 2026-11-11

The supplied snapshot is recorded by [262 source hashes](source-inventory-1.7.0.json)
and the [verbatim received manifest](received-1.7.0-manifest.json).
Its publication/reproduction claims are received evidence, not independently
verified releases. The integrated version is unreleased 1.7.1.

The maintainer approved the [design](../specs/2026-11-10-handover-1.7-intake-design.md)
on 10 November and the [written plan](../plans/2026-11-10-handover-1.7-intake-plan.md)
through human-merged PR #23 and the 11 November instruction:

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

Implementation, final strict L1/L2 and distribution acceptance remain in
progress. This record must not be read as a completed 1.7.1 release, an actual
Cowork installation, deployment or external distribution approval.
