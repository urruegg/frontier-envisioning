# Cowork health correction and 1.11.0 FinOps exclusion

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-26 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted intake |
| Status | Written specification `c26991e` approved; proposed implementation plan awaits approval; no fix or release approval claimed |
| Scope | Cowork ZIP routing correction; release-only FinOps exclusion, with Value Case and Agent Factory retained |
| References | [Bug #81](https://github.com/urruegg/frontier-envisioning/issues/81), [Draft PR #80](https://github.com/urruegg/frontier-envisioning/pull/80), [Design](../specs/2026-11-26-plugin-health-and-finops-exclusion-design.md), [Proposed plan](../plans/2026-11-26-plugin-health-and-finops-exclusion-plan.md), [Actual written approval](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7193888412), [SPRINT-013](../sprints/SPRINT-013-agent-factory-handover.md) |

## Problem and evidence

The supplied Cowork report `plugin-health.html`, generated on 26 November
2026 at 12:36 UTC, passes eight skills with average score 98. Value Case
scores 100/100. Two routing conflicts remain: FinOps/Process and Process/
Value Case. It does not establish a Value Case installation failure.
The report lists no Agent Factory and identifies neither its input package
version nor ZIP digest; it cannot certify the current nine-skill candidate.

The automatically computed original-report SHA256 is
`20902064efa12cfa4a0a4079c9b346f104ef6afd947e4295d24501ec57f5592a`.
The original is retained locally, not attached to the issue or copied into
the product. The bug preserves the findings, advisories and status timeline.

## Actual requested outcome and choices

The maintainer selected `exclude-from-111-distribution`, `cowork-zip` and
`approve-bounded-health-amendment` in this session. Retain FinOps source/tests,
but omit its entire skill from 1.11.0 distribution. Keep the seven existing
GA wrappers, including Value Case, plus Preview Agent Factory: eight shipped
skills. Clarify the actual Process/Value Case responsibility boundary.

The recommended approach is an explicit version-scoped distribution inventory.
Moving FinOps source outside the plugin would require broader path/import
changes and was not selected. Unrecognised omissions must remain errors.
No missing financial authority becomes zero costs or accepted evidence.

## Boundaries and next decision

Ordinary Cowork ZIP installation is the target, not Studio-backed MOS3
publication. Do not invent builder IDs, add dummy connectors or alter passing
security checks merely to suppress advisory warnings.

The [written design](../specs/2026-11-26-plugin-health-and-finops-exclusion-design.md)
at `c26991e` actually received `approve-written-health-amendment`;
the [receipt](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7193888412)
records it separately from the earlier conversational design.
The new implementation plan is proposed and still needs approval.
The previous Factory plan and passing checks are baseline evidence, not
approval or verification of this amendment. No release/tag was found at intake;
recheck before editing product bytes. Human merge/publication and #8 routing
remain separate.
