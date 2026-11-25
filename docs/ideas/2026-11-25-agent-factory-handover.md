# Agent Factory starter-repository handover

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted design |
| Status | Written spec `7f650c4` actually approved; staged plan/W0 and later production slice readiness pending |
| Scope | Planned 1.11.0 optional Agent Factory handover skill inside the existing plugin |
| References | [Catalogue](README.md), [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [Written design](../specs/2026-11-25-agent-factory-handover-design.md), [Staged plan](../plans/2026-11-25-agent-factory-handover-plan.md), [Sprint](../sprints/SPRINT-013-agent-factory-handover.md), [Prior systems programme #58](https://github.com/urruegg/frontier-envisioning/issues/58), [Template](https://github.com/urruegg/frontier-agent-factory) |

## Outcome

Turn selected reviewed envisioning outputs into a self-contained, customer-ready
review package based on the Agent Factory template. The ZIP is a repository
starting point, not proof of accepted engineering scope, tenant readiness,
deployed resources or permission to build.

Reuse the existing PRD/design/ADR/readiness and privacy contracts. Do not
replace supplied final documents with a competing scaffold generator.
Examples in this repository remain fictitious Caldova Industrial AG.

## Actual human choices

| Decision | Actual answer | Agreed meaning |
|---|---|---|
| Upstream | `https://github.com/urruegg/frontier-agent-factory` | Authoritative template source, not a change to this repository's issue/PR host |
| Release scope | `factory-only-defer-systems` | Target 1.11.0 is this extension only; systems/D365 moves to a later unspecified release |
| Template freshness | Discover latest template release | Resolve a stable published release per new handover, then pin exact identity |
| No-release case | `explicit-commit-bootstrap` | An explicitly approved immutable commit may bootstrap while no stable release exists; label it unreleased |
| Package | `full-starter-repository` | Full pinned foundation plus relevant intake/documents, not an overlay or documents-only ZIP |
| Readiness | `review-starter-with-explicit-gaps` | Review starter by default; real complete evidence is required for accepted status; explicit accepted requests do not silently downgrade |
| Receiving host | `github-cloud-first` | GitHub.com and GitHub Enterprise Cloud first, not native Azure DevOps/GHES |
| Boundary/name/maturity | `approve-factory-boundary`, no changes | Optional Preview `frontier-agent-factory`, displayed as Envisioning Agent Factory; ninth skill in the current plugin |
| Artefact contract | `approve-artifact-contract`, no changes | Exact ordinary-file intake/provenance; supported JSON/Markdown forms instead of unsupported HTML/ZIP/Turtle imports |
| Validation | `approve-validation-design`, no changes | Passive inputs, preserved controls/licences, bounded deterministic ZIP, accurate separate validation/readiness statuses |
| Intended execution | Requested subagent-driven implementation | Selected mode after actual written-spec and subsequently written plan approvals; not approval of unwritten records |
| Actual written review | `approve-written-factory-spec`, `no changes` | Approved the presented committed spec `7f650c4`; [actual receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078), not later plan approval |

The [#58 scope receipt](https://github.com/urruegg/frontier-envisioning/issues/58#issuecomment-7161780922)
records the explicit deferral rather than silently combining independent
extensions. Owner: `@urruegg`; no assignee, milestone or protected ready/approval
label is inferred here.

## Verified template facts

Read-only inspection used
[`0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d`](https://github.com/urruegg/frontier-agent-factory/commit/0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d).
GitHub identifies it as a public template; the actual root licence is MIT.
It contains 149 source files, 726,850 bytes, no symlinks/submodules in the
complete returned tree, and preserved Superpowers licence/lock material.

The foundation represents one customer/domain factory and chooses no application
runtime. Its receiving tooling requires Python 3.12+ and Node.js 24 LTS.
The strict intake contract uses ordinary files, explicitly rejects archive
imports and distinguishes review evidence from authorisation. Accepted scope
precedes creation of real solution units.

At inspection, authenticated release and tag queries both returned empty lists.
This commit is an inspected reference, not a published release or automatic
approval to use it for an actual customer handover. No template code was run.

## Next gate and limits

The [written specification](../specs/2026-11-25-agent-factory-handover-design.md)
at `7f650c4` received actual review/approval. The [staged plan](../plans/2026-11-25-agent-factory-handover-plan.md)
now prioritises actual Cowork acquisition and receiver compatibility as W0,
then separately approved exact production slices. The [full sprint](../sprints/SPRINT-013-agent-factory-handover.md)
remains not ready; W0 approval/results and downstream plans are not inferred.
No plugin bump, registration, code or generated customer repository is
produced by these planning records.

Protected release/guard/settings work remains human-only. Public repository
visibility does not permit transferring customer/internal material.
