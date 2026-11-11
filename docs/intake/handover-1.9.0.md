# Received 1.9.0 selective intake evidence

Date: 2026-11-11

[279 source hashes](source-inventory-1.9.0.json) and verbatim
[1.8.0](received-1.8.0-manifest.json) / [1.9.0](received-1.9.0-manifest.json)
manifests preserve the supplied evidence. Claims in those records are received,
not independently verified publications or release reproduction.

The maintainer approved the design at 11:02 +01:00 and subsequently the written
[SPRINT-004 plan](../plans/2026-11-11-handover-1.9-preview-finops-plan.md):

> okay the plan is approved please implement it sub agent driven now

This actual approval is recorded on [#25](https://github.com/urruegg/frontier-envisioning/issues/25);
it is not an inferred readiness/approval label or permission for protected work.

The isolated worktree starts from the saved planning commit
`2157c1335e8dc1b08f71904758e209c086a20043`, based on main
`907c3ca5d1ce94ca479ec7c9a3887187574cc0f4`.
D0 tests failed on the missing receipt and old version, then passed after
receipt generation and the standard 1.9.1 bump. Baseline selectors passed
16 tests and 27 subtests. All 241 original protected/fixture hashes were captured.

Implementation, optional Preview gating, maturity metadata, full build/browser
and distribution acceptance remain in progress. No new GA release, actual
Cowork/Fabric installation, deployment or external/IP clearance is claimed.
