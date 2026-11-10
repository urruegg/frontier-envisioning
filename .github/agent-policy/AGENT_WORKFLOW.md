# Agent delivery workflow

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-10 |
| Author | Copilot; AI-assisted drafting |
| Status | Proposed; human acceptance pending |
| Scope | Linked intake, approved bounded implementation and truthful delivery evidence |
| References | [AGENTS](../../AGENTS.md), [Issue #9](https://github.com/urruegg/frontier-envisioning/issues/9), [Idea](../../docs/ideas/2026-11-09-docs-governance-and-accessibility.md), [Spec](../../docs/specs/2026-11-09-docs-governance-and-accessibility-design.md), [G1 plan](../../docs/plans/2026-11-09-agent-governance-plan.md), [Master plan](../../docs/plans/2026-11-09-docs-governance-implementation.md), [Sprint](../../docs/sprints/SPRINT-001-docs-governance-and-accessibility.md), [Policy catalogue](README.md), [Human boundaries](NON_DELEGABLE_WORK.md), [Evidence measures](KPI_BASELINE.md) |

## From evidence to delivery

1. Frame the problem and evidence in [docs/ideas](../../docs/ideas/README.md)
   and a real GitHub issue.
2. Agree testable behaviour and constraints in
   [docs/specs](../../docs/specs/README.md). Update the
   [solution design](../../docs/solution-design.md) and a Proposed
   [ADR](../../docs/adr/README.md) when architecture changes.
3. Record actual human design approval; document status is not proof.
4. Write exact files, dependencies, tests and commands in
   [docs/plans](../../docs/plans/README.md).
5. Link issue, idea, spec and plan in a
   [docs/sprints](../../docs/sprints/README.md) work-item row.
6. Wait for explicit human plan approval and required human readiness before
   delegating implementation.
7. Work on a bounded branch/worktree. Test code/checker changes red-to-green;
   validate prose proportionally without fictional failing tests.
8. Regenerate product outputs through tools, run applicable gates, disclose
   agent involvement and open a scoped draft PR with real evidence.
9. People review and merge; releases and deployments are separate human decisions.

For this single-user repository, the human maintainer is `@urruegg`, not the
enterprise-only account. Record their review/sign-off against the current
head and passing checks. GitHub does not allow a PR author to formally approve
their own PR; neither an agent review nor the same person's second account
supplies independent human approval. If actual server requirements block the intended model, stop
for a human governance decision; do not bypass or alter them.
See the [sole-maintainer model](../../docs/engineering/github-setup.md#4-sole-maintainer-review-and-merge).

Every implementation item, including documentation, belongs to a real linked
governing package and sprint. Related items may reuse applicable approved
records; unrelated work does not borrow a package merely to avoid this contract.
Missing service access, issue links, approvals or measurements remain missing,
not inferred.

## Execution and evidence

Use fresh workers per independent task, one writer per shared surface and
spec-compliance/correctness review checkpoints. Stop for unexpected overlapping
changes, unexplained failures, scope expansion or
[non-delegable work](NON_DELEGABLE_WORK.md).

Use the approved private source, issue and PR host,
`urruegg/frontier-envisioning` on GitHub. No Azure Boards state transition or
synchronisation is claimed. Local link checks validate local targets and URL
shape, not live issue existence or approval. The parent checks the real issue
and actual human approval/readiness through authenticated service access before
delegated implementation; inaccessible records are not treated as verified.

Report actual local and cloud command/check results separately, including
failures, skipped checks and checks not run or unavailable. Local success does
not prove cloud success or human acceptance. The
[aggregate evidence measures](KPI_BASELINE.md) do not replace applicable gates.
