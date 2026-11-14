# SPRINT-009: Private GitHub Free release preparation

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Written spec approved at 65f06ff; plan/readiness approval pending |
| Scope | Exact-tag read-only preparation and verified human publication |
| References | [Catalogue](README.md), [Implementation #47](https://github.com/urruegg/frontier-envisioning/issues/47), [Decision #46](https://github.com/urruegg/frontier-envisioning/issues/46), [Idea](../ideas/2026-11-14-free-private-releases.md), [Spec](../specs/2026-11-14-free-private-releases-design.md), [Plan](../plans/2026-11-14-free-private-releases-plan.md), [ADR-0029](../adr/0029-free-private-release-preparation.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#47](https://github.com/urruegg/frontier-envisioning/issues/47) | [Outcome](../ideas/2026-11-14-free-private-releases.md) | [F46-01 to F46-08](../specs/2026-11-14-free-private-releases-design.md#acceptance-and-verification) | [Tasks 1-6](../plans/2026-11-14-free-private-releases-plan.md) | `@urruegg` accountable | Written plan/readiness approval; actual human workflow edit and review/merge | Planning; not ready or implemented | Written spec reviewed at `65f06ff`; real run/publication separate |

## Actual human choices

The maintainer confirmed GitHub Free, chose `design-free-private`, then
`ci-evidence-and-reproduction`. After the written proposal was committed and
pushed, the separate `approve-written-free-private-design` response approved
the specification at `65f06ffa60e5a8d1b70d46993636105768a50452` for planning.
These choices are recorded on #46 and do not approve this subsequent plan.

The selected model explicitly provides no cryptographic attestation or
publisher signature. It requires actual CI evidence, independent package
reproduction and human source-qualified sign-off/publication. No protected
label, assignment, milestone field or formal review is inferred.

## Readiness and validation boundary

The problem, source identities, affected tooling/guides, owner, eight
acceptance criteria and actual plan now have linked records. Plan/readiness
approval is still missing, so implementation has not started. The existing
isolated worktree uses `docs/46-free-private-release-design` from approved
main/source `2d5a7cc`; primary checkout and plugin bytes are unchanged.

At `65f06ff`, strict documentation and neutrality validation passed for the
design-only changes. That is not future tool, workflow, L1/L2/L3 or publication
evidence. The original tagged workflow was skipped and the Releases page
still listed no releases when checked on 14 November.

The protected workflow edit, its commit/push, acceptance/merge, dispatch,
settings and publication remain human-only. Keep legacy `RELEASE_ENABLED`
off and preserve the existing annotated `v1.10.0` tag. The historical
session-start routing dependency under #8 is unchanged.
