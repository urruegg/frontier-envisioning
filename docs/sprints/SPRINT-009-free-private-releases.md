# SPRINT-009: Private GitHub Free release preparation

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Inline plan/readiness approved at 4450e46; tooling verified, human workflow edit pending |
| Scope | Exact-tag read-only preparation and verified human publication |
| References | [Catalogue](README.md), [Implementation #47](https://github.com/urruegg/frontier-envisioning/issues/47), [Decision #46](https://github.com/urruegg/frontier-envisioning/issues/46), [Idea](../ideas/2026-11-14-free-private-releases.md), [Spec](../specs/2026-11-14-free-private-releases-design.md), [Plan](../plans/2026-11-14-free-private-releases-plan.md), [ADR-0029](../adr/0029-free-private-release-preparation.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#47](https://github.com/urruegg/frontier-envisioning/issues/47) | [Outcome](../ideas/2026-11-14-free-private-releases.md) | [F46-01 to F46-08](../specs/2026-11-14-free-private-releases-design.md#acceptance-and-verification) | [Tasks 1-6](../plans/2026-11-14-free-private-releases-plan.md) | `@urruegg` accountable | Actual human workflow edit and review/merge | Tooling verified; paused for person-only workflow replacement | Working tree based on `4450e46`; 17 tests pass, two expected workflow-contract failures; no full gate/L3/publication claim |

## Actual human choices

The maintainer confirmed GitHub Free, chose `design-free-private`, then
`ci-evidence-and-reproduction`. After the written proposal was committed and
pushed, the separate `approve-written-free-private-design` response approved
the specification at `65f06ffa60e5a8d1b70d46993636105768a50452` for planning.
These choices are recorded on #46. The separate `approve-plan-inline`
response approved plan/readiness at
`4450e46b2e5930ec41dee0f5218751b28d090dba` and selected inline execution.

The selected model explicitly provides no cryptographic attestation or
publisher signature. It requires actual CI evidence, independent package
reproduction and human source-qualified sign-off/publication. No protected
label, assignment, milestone field or formal review is inferred.

## Readiness and validation boundary

The problem, source identities, affected tooling/guides, owner, eight
acceptance criteria and actual plan have linked records. The existing clean
isolated worktree was reused on `chore/47-free-release-preparation` from
planning head `4450e46`; primary checkout, plugin bytes and existing tag are
unchanged. Implementation is currently uncommitted pending the planned
human-only workflow handoff; the code has not been presented as merged.

At `65f06ff`, strict documentation and neutrality validation passed for the
design-only changes. That is not future tool, workflow, L1/L2/L3 or publication
evidence. The original tagged workflow was skipped and the Releases page
still listed no releases when checked on 14 November.

The protected workflow edit, its commit/push, acceptance/merge, dispatch,
settings and publication remain human-only. Keep legacy `RELEASE_ENABLED`
off and preserve the existing annotated `v1.10.0` tag. The historical
session-start routing dependency under #8 is unchanged.

## Test-first tooling checkpoint

- Baseline: all 11 existing release-tool tests passed.
- Source/control inspection: six expected assertion failures before the new
  CLI mode; 13 tests passed after implementation.
- Candidate preparation/verification: four expected failures before the new
  modes; 17 tests passed after implementation.
- Additional focused RED/GREEN caught a newly introduced captured-ROOT
  default in the legacy writer and silently ignored mode arguments. The
  writer now retains its dynamic legacy ROOT default for direct and CLI
  calls, while new preparation explicitly supplies the source checkout.
- Before updating the workflow contracts, all 19 release-tool tests passed.
  After replacing the old native-profile assertions, the current result is
  **17 passed, two expected workflow-contract failures**: the protected file
  still has tag-push/native publication rather than the approved manual
  read-only preparation. These are not suppressed or reported as green.
- Scoped Ruff and whitespace passed. The protected workflow still matches
  its base blob `76ec229d1055d7df7d7c0f5ae5c2b2671e5142e0`. Remote tag object
  and peeled commit still match the approved 1.10.0 identities.

Tests use temporary synthetic repositories/CI facts, not fabricated real
workflow evidence. Current helpers cover exact source/control binding, four
assets, receipt/checksum integrity, a consistently rewritten malicious
candidate rejected by independent package bytes, output preservation and
legacy manifest compatibility.

Next: the maintainer applies, stages, commits and pushes only the protected
workflow replacement from plan Task 3. No new PR or workflow is triggered
while its helper/test changes remain uncommitted. Full gates, current-guide
alignment, PR/CI, actual preparation and publication remain pending.
