# SPRINT-013: Agent Factory handover

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Written design approved at `7f650c4`; staged plan/W0 approval pending; no product implementation or host-proof claim |
| Scope | Planned 1.11.0 optional Agent Factory handover only; systems/D365 deferred |
| References | [Catalogue](README.md), [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [Idea](../ideas/2026-11-25-agent-factory-handover.md), [Design](../specs/2026-11-25-agent-factory-handover-design.md), [Staged plan](../plans/2026-11-25-agent-factory-handover-plan.md), [Actual written approval](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078), [#58 deferral](https://github.com/urruegg/frontier-envisioning/issues/58#issuecomment-7161780922) |

## Outcome and work item

Add **Envisioning Agent Factory**, registered as optional Preview
`frontier-agent-factory` inside the existing plugin. Prepare a full starter
repository ZIP from the exact selected template and relevant reviewed
envisioning files, with explicit gaps and real transfer/review evidence.
No business runtime, remote repository, tenant provisioning or deployment.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#72](https://github.com/urruegg/frontier-envisioning/issues/72) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-01-AF-16](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Roadmap and W0](../plans/2026-11-25-agent-factory-handover-plan.md) | `@urruegg` accountable | Written plan approval, real Cowork acquisition, pinned receiver proof, later exact approved slice plans | Not ready; W0 execution not yet approved; no implementation | [Written-spec approval receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078) |

Create real bounded child issues only when their actual execution plans are
approved, before delegation. Do not treat W0 evidence as approval for unwritten
W1-W4 plans. No assignee, milestone or protected label has been inferred.

## Actual human decisions

Conversational sections were approved with no changes: factory boundary,
artefact contract and validation. The human selected full-starter-repository,
review-starter-with-explicit-gaps, GitHub Cloud first, latest stable template
discovery with explicit immutable unreleased bootstrap only after a healthy
no-release lookup, and subagent-driven implementation.

The actual written specification was then presented at
`7f650c48bdce5c94f4f1745119e1ea87dd0b0f24` and separately approved:
`written_spec=approve-written-factory-spec`, `changes=no changes`.
The committed specification's automatically recorded SHA256 is
`7655d0340508e5f203aaeb7f9e1c11eff0f22efff58e0a3d6390099aa3eeb7d0`.
This is approval evidence for that document, not a recurring user hash step,
formal GitHub self-approval, plan approval, tenant permission or publication.

The independent systems/D365 programme #58 moves to a later unspecified
release. Its old 1.11 target is historical; this sprint does not absorb its
scope or invent a new deadline.

## Staged execution and blockers

| Work package | Exit / acceptance | Current state |
|---|---|---|
| W0: verification spike | Real latest/no-release and exact source acquisition in actual Cowork; actual pinned receiver fixtures/negative checks with real prerequisites; precise evidence, no simulated host pass | Plan written; actual approval and both exits pending |
| W1: local source/intake contract | Strict offline receipt/profile, ID/scope/role/evidence/review/history handling; real RED/GREEN and actual approved exact plan | Blocked by W0; not delegated or implementation-ready |
| W2: archive | Bounded raw ZIP validation, safe paths/modes/inventory, threshold and good-output-preservation tests, shared-helper reuse without release regression | Blocked by reviewed W1 and exact W2 plan approval |
| W3: projection/export | Approved authored bytes, scope/privacy/FinOps boundaries, deterministic full ZIP, separate truthful statuses | Blocked by reviewed W1/W2 and exact W3 plan approval |
| W4: integration/acceptance | Ninth optional Preview skill, current metadata/docs/installer/self-test, independent package/receiver proof, actual Cowork candidate install/export and exact-head gates | Blocked by reviewed W3 and exact W4 plan approval |

Actual Cowork exact-template archive retrieval is **not demonstrated** by this
VS Code session. If the necessary authorised capability is absent, stop and
escalate rather than add networking to the plugin or claim full support.
W0's fixture tests, when run, validate only the reference receiver. They do
not validate a producer that has not been built.

The receiver's 64 MiB cumulative validation budget counts baseline bytes
and, with `--source-root`, original bytes too. Later threshold tests must
exercise that actual traversal, not treat it as 64 MiB independently for each.
Engineering gaps can remain in valid needs-clarification intake; missing
mandatory structural/evidence fields cannot be filled with fictional values.

## Actual planning evidence

The design-only package at `7f650c4` changed five Markdown records/catalogues.
`python tools\dev.py docs --strict` passed with zero errors and its own
`ALL GATES PASSED` summary; `git --no-pager diff --check` passed.
Inline placeholder/consistency/scope review passed, and the planning branch
was clean and pushed before written-spec review.

During plan preparation, read-only API byte inspection confirmed reference
`0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d`:

- `docs/intake/intake.schema.json`: 8,381 bytes, SHA256
  `04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f`.
- `tools/intake.py`: 15,736 bytes, SHA256
  `4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370`.
- Actual receiver code confirms strict schema plus role/transfer/review/path/
  digest checks, and the shared source/baseline byte budget.
- Live #72 is open with no assignee/milestone and no protected approval/ready
  labels. That observation does not revoke the actual written-spec approval.
- Actual local inventory found Python 3.14/3.11 and Node `v26.13.1`.
  The available Python 3.14 meets the declared receiver minimum, not proof
  its dependencies/tests pass. Node 26 is not the Node 24 LTS profile;
  no full receiver toolchain readiness is claimed.

No upstream code, new producer test, template acquisition in Cowork, full
gate, customer ZIP, plugin bump or product change was performed by planning.
Future evidence must be appended with real commands, outcomes and source IDs.

## Human boundaries

Keep published 1.10.x records immutable; a 1.11.0 bump is for the approved
product change, not a way around failed reproduction. Only Caldova synthetic
samples belong in repository tests. Customer/internal transfer needs genuine
clearance regardless of public repository visibility.

Merges, releases/tags, protected labels/settings/workflows and tenant operations
remain human-only. Protected session-start routing under #8 remains an
outstanding human dependency, not silently migrated by this sprint.
