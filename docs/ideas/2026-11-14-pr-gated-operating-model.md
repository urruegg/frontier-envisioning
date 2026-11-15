# PR approval as the routine human engineering gate

| Field | Value |
|---|---|
| Version | 0.4 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted intake |
| Status | Spec at 8de16ca and subagent plan/readiness at e8ea6bd approved; contracts/bootstrap verified, adoption pending |
| Scope | Private GitHub Pro engineering and release automation, not deployment or administration |
| References | [Catalogue](README.md), [Decision #48](https://github.com/urruegg/frontier-envisioning/issues/48), [Specification](../specs/2026-11-14-pr-gated-operating-model-design.md), [Plan](../plans/2026-11-14-pr-gated-operating-model-plan.md), [ADR-0030](../adr/0030-pr-gated-engineering-automation.md), [SPRINT-010](../sprints/SPRINT-010-pr-gated-operating-model.md), [Preserved work #47](https://github.com/urruegg/frontier-envisioning/issues/47) |

## Outcome and actual choices

The maintainer wants to review and approve PRs rather than repeatedly paste
workflow files, run merge/tag commands and publish releases manually.

The latest hosting clarification is GitHub Pro on `urruegg`, superseding the
earlier Free answer. The maintainer selected:

- `formal-review-machine-author`: real machine-authored PRs and an actual
  eligible GitHub approving review, not formal self-approval.
- `engineering-and-releases`: routine engineering, workflow proposals, merge,
  tagging, package preparation and GitHub publication; no Azure deployment
  or repository administration in this first slice.
- `approve-pr-gated-engineering-concept`: approve writing the specification
  and Proposed ADR for the presented isolated, approval-gated model.

These actual conversation decisions are recorded on #48. They do not activate
permissions, install an App, approve the written plan or change current rules.
The separate `approve-written-pr-gated-spec` response then approved the written
proposal at `8de16ca` for planning. The linked plan/sprint were written after
that answer. The later explicit plan/readiness approval at `e8ea6bd`
requested subagent implementation and evidence-based end-to-end tests.
The native Release ZIP choice was reconfirmed; no registry wrapper is needed.
Contracts and the inert bootstrap generator are locally verified; actual
identity/adoption/publishing remains pending.

## Reference and problem

The reviewed `urruegg/ernaehrungundsportapp` snapshot separates human
authorisation from scoped execution and has real release automation after
main changes. Its branch settings have stale-review/admin-bypass gaps, and
owner-authored PRs do not solve formal self-approval. Reuse the principle,
not those weaknesses, domain rules or npm tooling.

Frontier currently blocks workflow edits categorically and lists no native
rulesets/classic branch protections. The successor should allow proposals
while enforcing approval before activation, rather than remove the gate.
The specification contains source-qualified findings and the proposed checks.

## Boundaries and preservation

Use a repository-owned GitHub App, a private proposal-input boundary and
restricted agent credentials. Human review stays separate from machine
authorship/execution. Keep the source/issue/PR host private and unchanged.

One-time adoption, identity/credential setup and recovery remain accountable
maintainer actions. Current stricter rules remain active until actual adoption.
No agent rewrites its own active guard or uses the owner's browser/token to
approve a PR.

Preserve #46/#47 evidence and the existing 1.10.0 tag/source. The #47 tooling
work now has commit `aa838fbb6df96766a632d6f6ec3151ca93c7803d`; do not reset or
quietly relabel it as the new automated-publication contract.
No plugin/runtime/version change is part of this governance proposal.
