# SPRINT-013: Agent Factory handover

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Design/W0/host amendment actually approved; #73 source/reference and receiver proof verified with one skip; actual Cowork deferred; exact production plan next, no product implementation |
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
| [#72](https://github.com/urruegg/frontier-envisioning/issues/72) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [AF-01-AF-16](../specs/2026-11-25-agent-factory-handover-design.md#9-acceptance-for-the-bounded-sprint) | [Roadmap and W0](../plans/2026-11-25-agent-factory-handover-plan.md) | `@urruegg` accountable | Exact reviewed production plan after actual #73 evidence | Offline W0 verified; no product implementation | [Written-spec receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078), [W0 receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7165080818), [Host-amendment receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7166316613) |
| [#73](https://github.com/urruegg/frontier-envisioning/issues/73) | [Actual decisions](../ideas/2026-11-25-agent-factory-handover.md) | [Host/receiver boundary](../specs/2026-11-25-agent-factory-handover-design.md#4-template-discovery-acquisition-and-compatibility) | [W0 Tasks 1-4](../plans/2026-11-25-agent-factory-handover-plan.md#3-w0-task-1-baseline-and-exact-source) | `@urruegg` accountable and assigned; bounded receiver builder | Actual W0/host-amendment approval; pinned reference and isolated dependencies | Actual source/receiver exit verified: 30 pass, one privilege skip, four validators exit 0; Cowork deferred/not performed | Ordered parent specification then correctness review; attribution correction applied; no protected ready/approval label inferred |

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

The staged plan and full sprint at `c8cc5bb` were subsequently presented and
actually approved with `approve-w0-and-start-receiver-verification`,
`no changes`. A real bounded child #73 was then created and assigned before
dispatching a fresh developer receiver worker. The actual Cowork-evidence
request received **"we din't have it at all"**, not a host pass. The written
host-gate amendment at `f4b2609` was then separately presented and actually
approved: `approve-offline-preview-defer-cowork-validation`,
`no change please proceed`. The [actual receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7166316613)
approves offline Preview development with actual source/receiver proof;
Cowork remains not performed and cannot be advertised as validated.

## Staged execution and blockers

| Work package | Exit / acceptance | Current state |
|---|---|---|
| W0: verification spike | Genuine available-host source/reference acquisition and actual pinned receiver checks; actual Cowork explicitly deferred under approved amendment | Verified source/reference and receiver evidence, 30 tests passed/one skip and four validators exit 0; no simulated host pass |
| W1: local source/intake contract | Strict offline receipt/profile, ID/scope/role/evidence/review/history handling; real RED/GREEN and actual approved exact plan | W0 source/receiver exit verified; exact production plan pending before implementation |
| W2: archive | Bounded raw ZIP validation, safe paths/modes/inventory, threshold and good-output-preservation tests, shared-helper reuse without release regression | Blocked by reviewed W1 and exact W2 plan approval |
| W3: projection/export | Approved authored bytes, scope/privacy/FinOps boundaries, deterministic full ZIP, separate truthful statuses | Blocked by reviewed W1/W2 and exact W3 plan approval |
| W4: integration/acceptance | Ninth optional Preview skill, current metadata/docs/installer/self-test, independent package/receiver proof and exact-head gates; unavailable Cowork explicitly not performed | Blocked by reviewed W3 and actual production-plan approval |

Actual Cowork exact-template archive retrieval is **not demonstrated** by this
VS Code session. The approved amendment permits offline work, not networking
inside the plugin or a claim that the absent host is supported.
W0's actual fixture tests validate only the reference receiver. They do
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

## Actual W0 execution and ordered evidence review

The bounded worker successfully queried the complete release/tag lists:
both empty at its 25 November observation. It acquired an exact clean
reference checkout at `0bb2b1b`, verified all 149 ordinary source blobs /
726,850 bytes and both schema/validator fingerprints above. This does not
select a customer bootstrap, authenticate an archive signature or prove
continued latest-release absence.

The initial Python 3.14 command failed before intake tests ran because an
unrelated user-site `tools` package shadowed the pinned namespace. Process-only
user-site isolation resolved that collision and exposed a real missing
`jsonschema` dependency. The first official-PyPI restore failed TLS. The
second/final attempt used normal existing package-manager configuration and
restored the pinned `jsonschema==4.25.1` into the task's isolated receiver
environment. No shared environment, pin, certificate, proxy, authentication
or TLS-verification setting was changed; no feed/account details are retained.

Actual final receiver context:

```powershell
$factory = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
$python = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-receiver-env\Scripts\python.exe'
$fixtures = Join-Path $factory 'tests\fixtures\intake'
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
$env:PYTHONNOUSERSITE = '1'
Set-Location -LiteralPath $factory
```

| Actual command after that context | Result |
|---|---|
| `& $python -m unittest discover -s tests -p test_intake.py -v` | Exit 0: 31 tests, 30 passed, one skipped, zero failures/errors; `test_symlink_is_not_followed` skipped for Windows privilege error 1314 |
| `& $python -m tools.intake validate (Join-Path $fixtures 'accepted.json') --root (Join-Path $fixtures 'workspace') --source-root (Join-Path $fixtures 'source')` | Exit 0: baseline and source bytes; recorded human approval not authenticated |
| `& $python -m tools.intake validate (Join-Path $fixtures 'needs-clarification.json') --root (Join-Path $fixtures 'workspace') --source-root (Join-Path $fixtures 'source')` | Exit 0: baseline and source bytes; recorded human approval not authenticated |
| `& $python -m tools.intake validate (Join-Path $fixtures 'rejected.json') --root (Join-Path $fixtures 'workspace') --source-root (Join-Path $fixtures 'source')` | Exit 0: valid synthetic rejected disposition, no provided artefact bytes; not accepted scope or transfer permission |
| `& $python -m tools.intake validate (Join-Path $fixtures 'accepted.json') --root (Join-Path $fixtures 'workspace')` | Exit 0: baseline bytes and recorded evidence only; originals explicitly not checked |

These are real reference-receiver results, not tests of a future producer.
All fixture identities and approvals remain synthetic. Node 24/full receiving
toolchain certification and actual Cowork checks remain not performed.

The parent reviewed specification compliance first, then correctness of the
bounded evidence. A narrow attribution issue was corrected: the normal-source
recovery instruction came from the controller, not an additional human
approval or a newly supplied feed identity. The actual human W0 and host
amendment receipts remain separate. No further receiver defect was inferred.

Required new producer coverage remains explicit: restricted material,
approved transfer with absent approval, junction/reparse safety, unexecuted
symlink rejection, generic/equal-digest transformation errors, non-finite JSON
and exact-at/one-byte-over limits including the shared source/baseline budget.
Do not treat the reference's absent tests as passing coverage.

The source checkout and restored receiver environment are task-owned and
retained for directly dependent implementation planning and actual produced-
package acceptance; no background helpers remain. No current/upstream
repository source was edited by the receiver worker. Existing historical
failures stay in the session evidence report rather than being rewritten as
passes. No plugin bump, new exporter, customer ZIP or protected action occurred.

## Human boundaries

Keep published 1.10.x records immutable; a 1.11.0 bump is for the approved
product change, not a way around failed reproduction. Only Caldova synthetic
samples belong in repository tests. Customer/internal transfer needs genuine
clearance regardless of public repository visibility.

Merges, releases/tags, protected labels/settings/workflows and tenant operations
remain human-only. Protected session-start routing under #8 remains an
outstanding human dependency, not silently migrated by this sprint.
