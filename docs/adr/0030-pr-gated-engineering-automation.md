# ADR-0030: Human PR approval with isolated machine execution

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted design |
| Status | Proposed; written specification approved at 8de16ca for planning, PR acceptance pending |
| Scope | Engineering/release authority boundary, not production deployment or agent identity branding |
| References | [Catalogue](README.md), [Decision #48](https://github.com/urruegg/frontier-envisioning/issues/48), [Idea](../ideas/2026-11-14-pr-gated-operating-model.md), [Specification](../specs/2026-11-14-pr-gated-operating-model-design.md), [ADR-0018](0018-quality-gates-and-release-reproduction.md), [ADR-0019](0019-versioning-and-releases.md), [ADR-0022](0022-deterministic-guardrails.md), [Earlier ADR-0029 proposal](https://github.com/urruegg/frontier-envisioning/blob/4450e46b2e5930ec41dee0f5218751b28d090dba/docs/adr/0029-free-private-release-preparation.md) |

## Context

Frontier's current working agreement categorically reserves workflow/guard
edits, merging, tags and publication for people. The maintainer wants actual
PR review/approval to be the routine human gate instead of repeated manual
file/command operations. Current GitHub Pro supports native private PR
protection and auto-merge, but ownership and credentials still matter.

The reference repository uses approval-conditioned execution and real
post-main release automation. Its administrator/stale-review gaps and
owner-authored PRs do not establish the desired strict formal-review model.
The selected human gate is an actual eligible review of a machine-authored
PR, not formal self-approval, a label or an agent-written owner statement.

## Proposed decision

Separate inert proposal preparation from trusted execution. Use a private
proposal boundary and a repository-owned GitHub App to create PRs; keep
owner, App and publisher credentials out of the worker/candidate context.
Validate proposal scope/workflow safety against the accepted control policy,
not the candidate's edited guard.

Native main protection requires the sole human owner's current approval,
actual L1/L2/IaC and trusted eligibility. Only then can native merge and
trusted post-approval automation execute the reviewed release intent.
No routine bypass, direct main push or implicit publication is allowed.

Privileged orchestration is trusted metadata/data handling, not execution
of unreviewed PR scripts or package output. Main/source/review/control and
actual action facts remain separately recorded. Labels/status/docs describe
evidence; they do not create it.

This first profile is engineering and private GitHub releases only. Azure,
administration, destructive changes, secrets and visibility remain outside
its routine authority. Keep immutable versions, generators, customer
neutrality, optional Preview FinOps and no-cryptographic-attestation limits.

## Consequences

Routine workflow changes can be prepared as PRs rather than pasted by a
person. A real machine author makes the single human owner's approving
review eligible. App event behaviour avoids the extra workflow-run approval
often attached to ordinary `GITHUB_TOKEN`-created PRs, subject to a real pilot.

This adds App/credential isolation, trusted coordination and one-time
maintainer adoption. Pro is a capability foundation, not proof that rules
or isolation already exist. A private proposal store is transport, not a
host cutover. Unsupported harness boundaries block activation rather than
justify using the owner's broad token.

Scope and legal/business decisions still need accountable humans where
required. Design/plan or release-record PRs may add reviews, but routine
operational file/merge/tag/publish actions are automated. Missing actual
manual acceptance evidence cannot be manufactured by an approval.

## Alternatives considered

- Copy the reference verbatim: less design work, but preserves stale/admin
  bypass gaps, owner self-review problems, different domain/npm tooling and
  separate manual production gates.
- Owner-authored PRs with sign-off comments: not the selected formal review
  mechanism and requires another trusted authorisation design, not a
  claim that self-approval works.
- Ordinary `GITHUB_TOKEN` PR automation: less App setup, but can add manual
  workflow approval and needs explicit event handling; not the preferred
  one-routine-gate route.
- Free/private custom approval controller: based on the superseded Free
  assumption; Pro provides the native review/merge foundation.
- Remove local guards and give the agent owner/publisher credentials:
  fails the required human-approval and credential boundaries.

## Status and adoption

The maintainer selected the formal machine-author model and engineering/release
scope, then approved writing this concept's specification/ADR on #48.
The separate `approve-written-pr-gated-spec` response approved the written
proposal at `8de16ca` for planning. This ADR remains Proposed; plan/readiness,
its required human PR acceptance and real adoption remain separate.

If accepted and implemented, it replaces the relevant routine manual-execution
aspects of the earlier engineering/release proposals. Preserve their source
evidence rather than rewrite them. ADR-0029's number is retained for its
existing unmerged proposal; do not reuse it.

The maintainer adopts/configures the migration under current rules and verifies
the actual provider, App, protections, flags and pilot. Neither this document
nor chat approval activates permissions or grants an agent a current exception
to protected edits, settings, merges, tags or publication.
