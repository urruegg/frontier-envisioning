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

## Returned implementation checkpoint — 11 November 2026 (+01:00)

Copilot AI-assisted evidence maintenance; results below were returned by the
parent loop, not rerun by the prose worker. This receipt retains its historical
format. The [idea](../ideas/2026-11-11-handover-1.9-preview-finops.md),
[design](../specs/2026-11-11-handover-1.9-preview-finops-design.md),
[plan](../plans/2026-11-11-handover-1.9-preview-finops-plan.md) and
[SPRINT-004](../sprints/SPRINT-004-handover-1.9-preview-finops.md) link the approved
scope to current delivery evidence; [documentation catalogue](../README.md)
routes the maintained product records.

- D0 `e7e4db5`: exact receipt digest
  `904538ec9930aad2d3aa5e8067023f4a7230d46a5696faef7836896b444a01e9`;
  241 original protected/fixture hashes unchanged at last verification.
- D1 `f5e08f2`: SPEC PASS / QUALITY CLEAR, 111 tests/398 subtests.
  Five outputs deterministic under four hash seeds; strict pre-write/privacy
  tested. Integrated Caldova: 27 entities, 33 relationships, 126 properties,
  nine sources, four data agents/four semantic models, 18 data plus one knowledge
  product; six mappings to verify and Employee binding gap remain.
- D2 `d763833`: SPEC PASS / QUALITY CLEAR, 81 D2 tests/508 subtests,
  combined 197/906; fresh acknowledgement, lazy core, cache/provenance,
  private-component/selection matrix and named-variable fingerprint evidence.
- D3 `c64a815`: SPEC PASS / QUALITY CLEAR, 75 DOM/61 browser reported on
  frozen source; independent review 16 new DOM/two hosted checks plus 31 old
  DOM/three Turtle variations. Real CSP/axe and no new WCAG waiver, not exhaustive
  Preview AA, tenant import or manual AT certification.
- Parent pre-D4 strict L1 at `c64a815`: `ALL GATES PASSED`, 394 tests,
  one expected unreleased-manifest skip, 1337 subtests, 48 self-tests, 75 DOM;
  six existing ESLint warnings/zero errors. Not post-doc validation.
- Parent runner `ecdfdc8` / `e61bc6a`: isolated core/Preview fixtures with
  real CSP; 39 tools/site tests/four subtests pass and HTTP 200/CSP verified.
  Core and explicit Preview raster inputs were verified separately; actual
  pins and full qualifications are in the [design](../solution-design.md#191-development-intake).

Before D4, four read-only reference/pressure scenarios at `c64a815` safely
flagged contradictory/missing instructions, rather than inventing flags or
executing unsafe operations. They were not live Cowork validation. D4 prose
is prepared for parent review; its post-edit rerun and strict document/
product/maturity/history checks remain pending.

Candidate handoff measurements reported eight verified copy plans (seven GA/
one optional Preview), fifteen complete entries and passing nested privacy/
embedded-byte checks, before the new process reference. D5 must measure the
final source-file count, rebuild twice/compare digests, verify the final offline
installer/private guard, run final strict L1/L2 and review. A broader Preview AA
test matrix is in progress; final results/counts belong to D5. Actual Cowork
validators/behaviour, Fabric import/data-agent tenant tests and AT certification
remain manual, not proven. No new GA release, actual Cowork/Fabric installation,
deployment, formal approval or external/IP clearance is claimed.
