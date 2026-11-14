# SPRINT-010: PR-gated engineering and release automation

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Written specification approved at 8de16ca; plan/readiness and adoption pending |
| Scope | Staged private Pro machine-authored PRs, actual human review and trusted engineering/release execution |
| References | [Catalogue](README.md), [Decision #48](https://github.com/urruegg/frontier-envisioning/issues/48), [Idea](../ideas/2026-11-14-pr-gated-operating-model.md), [Specification](../specs/2026-11-14-pr-gated-operating-model-design.md), [Plan](../plans/2026-11-14-pr-gated-operating-model-plan.md), [ADR-0030](../adr/0030-pr-gated-engineering-automation.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#48](https://github.com/urruegg/frontier-envisioning/issues/48) | [Outcome](../ideas/2026-11-14-pr-gated-operating-model.md) | [G48-01 to G48-09](../specs/2026-11-14-pr-gated-operating-model-design.md#acceptance-and-verification) | [Slices A-D, Tasks 0-5](../plans/2026-11-14-pr-gated-operating-model-plan.md) | `@urruegg` accountable | Plan/readiness approval; supported restricted identity; actual maintainer adoption/pilots | Planning; not active or implemented | Written spec reviewed at `8de16ca`; no native-review/pilot/publication result yet |

## Actual decisions

The maintainer confirmed current GitHub Pro, selected
`formal-review-machine-author`, selected `engineering-and-releases`,
then `approve-pr-gated-engineering-concept`. The specification/Proposed ADR
were written and committed at
`8de16ca089ba0e2a1787496a4c65ecf17b7b6b4e`.
The separate `approve-written-pr-gated-spec` response approved that actual
written proposal for planning. This subsequent plan is not yet approved.

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
