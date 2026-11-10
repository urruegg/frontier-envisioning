# Traceable documentation and accessible Frontier Envisioning

| Field | Value |
|---|---|
| Version | 0.5 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; user-requested work; AI-assisted maintenance |
| Status | Delivered through human-merged #15; final sign-off recorded on #8; sole-account refinement requested; protected operations not inferred complete |
| Scope | Repository documentation, engineering intake, agent governance and HTML accessibility |
| References | [Idea catalogue](README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/6), [Spec](../specs/2026-11-09-docs-governance-and-accessibility-design.md), [Plan](../plans/2026-11-09-docs-governance-implementation.md), [Sprint](../sprints/SPRINT-001-docs-governance-and-accessibility.md) |

## Plural-layout amendment (2026-11-10)

The maintainer moved the documentation into plural ideas/specs/plans/sprints
folders, with historical designs in specs and implementation plans in plans,
and explicitly requested removal of the combined product-document index and
remaining singular plan directory. [#18](https://github.com/urruegg/frontier-envisioning/issues/18)
tracks this scoped amendment, its [spec](../specs/2026-11-10-documentation-layout-design.md)
and [plan](../plans/2026-11-10-documentation-layout-plan.md). The existing
[sprint](../sprints/SPRINT-001-docs-governance-and-accessibility.md) records
delivery separately. No protected routing change or new product behaviour is
authorised by the cleanup.

## Problem and outcome

Documentation and engineering guidance must remain current as the Cowork plugin
evolves. At intake, requirements and architecture shared one document and
records lacked a dedicated linked sprint catalogue. D1-D5 now address those
foundations in [draft PR #12](https://github.com/urruegg/frontier-envisioning/pull/12),
not merged. G1-G3 are delivered in
[draft PR #13](https://github.com/urruegg/frontier-envisioning/pull/13);
policies remain Proposed. A1-A4 renderer changes and A5 documentation are
implemented, but catalogue AA failures block A4/A5 acceptance.

The outcome is a constrained documentation agent, two authoritative product
documents, traceable idea/spec/plan/sprint/issue records, clear Frontier-specific
policy and an evidence-led accessibility improvement.

## Alternatives and decision

| Alternative | Assessment |
|---|---|
| Copy the reference repository | Rejected: wrong host authority, HR assumptions, excessive metrics and incompatible tooling |
| Split documents only | Insufficient: leaves governance, traceability and accessibility disconnected |
| Adapt in bounded workstreams | Accepted design: preserve contracts and add measurable checks with human governance seams |

Non-agent alternatives remain appropriate for mechanical validation and human
approvals. A documentation persona assists maintenance; deterministic checks
prove structure, and people retain decisions and permissions.

## Evidence, constraints and ownership

- [134-file header assessment](../intake/2026-11-09-markdown-header-audit.csv).
- [38-scan Microsoft Edge accessibility evidence](../intake/2026-11-09-accessibility-audit.json).
- The repository remains the approved private `urruegg/frontier-envisioning`
  source/issue/PR host. No Azure Repos/Azure Boards migration is included.
- Caldova Industrial AG is the fictitious sample. No customer data or secrets
  are introduced.
- Sole accountable maintainer/intended code owner: `@urruegg`. The user's
  10 November account correction rules out the enterprise-only account as a
  second collaborator. Human-owned ownership/routing changes and recorded
  maintainer sign-off are tracked in [#8](https://github.com/urruegg/frontier-envisioning/issues/8);
  formal self-approval is not claimed.
- Scope excludes releases, deployments, permissions, protected hook edits by
  agents, historical rewriting and blanket packaged-document header changes.

## Approval provenance

The quotation below retains the original design-stage approval record. Current
plans/readiness approval is linked in the metadata; this quotation alone did not
authorise implementation.

On 9 November 2026 the user wrote:

> Okay design is approved and you can write the plan to implement it sub agent delegated implementation after plan approval

That first quotation approved design and planning, not implementation.

On 9 November 2026 the user separately wrote:

> pr is approved and you can proceed.

The parent's [plan-approval/preflight comment on #6](https://github.com/urruegg/frontier-envisioning/issues/6#issuecomment-6740481819)
records this quote, human merge of [PR #11](https://github.com/urruegg/frontier-envisioning/pull/11)
at 12:46:18Z and main `b0b4776`. It also records the then-blocking absence
of readiness labels; that earlier preflight is not the current approval state.

The user then explicitly resolved readiness:

> Okay enclose my approval to deblock and proceed with
> - `status:ready` on #10, #9 and #7
> - `approved:design` on #6

The parent's [readiness comment on #6](https://github.com/urruegg/frontier-envisioning/issues/6#issuecomment-6742446199)
records that decision at 14:24:36Z. These are real human approval decisions,
not inferred from document status. No agent applied protected labels, and
label-field changes are not claimed. Human synchronisation remains under #8.
Plan/readiness approval does not accept Proposed policies, grant access or
authorise protected operations.

Current delivery and outstanding acceptance are indexed in
[SPRINT-001](../sprints/SPRINT-001-docs-governance-and-accessibility.md):
D1-D5 implemented/reviewed in draft PR #12; G1-G3 delivered in draft PR #13
with policies still Proposed; A1-A4 implemented and A5 documentation handed
off. Both PRs remain open drafts. The
[implementation finding](../specs/2026-11-09-docs-governance-and-accessibility-design.md#implementation-finding-2026-11-10)
records catalogue AA contrast, full L2 red and the required new human scope
decision without changing original approval. A4/A5 acceptance and human #8
remain pending.
