# PR-gated engineering and release operating model

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted design |
| Status | Spec at 8de16ca and subagent plan/readiness at e8ea6bd approved; contracts verified, adoption pending |
| Scope | Private GitHub Pro engineering/release automation with genuine human PR approval |
| References | [Catalogue](README.md), [Decision #48](https://github.com/urruegg/frontier-envisioning/issues/48), [Idea](../ideas/2026-11-14-pr-gated-operating-model.md), [Plan](../plans/2026-11-14-pr-gated-operating-model-plan.md), [ADR-0030](../adr/0030-pr-gated-engineering-automation.md), [SPRINT-010](../sprints/SPRINT-010-pr-gated-operating-model.md), [Working agreement](../../AGENTS.md), [Policy catalogue](../../.github/agent-policy/README.md) |

## Outcome and authority

After a real maintainer bootstrap, the normal human gate is an actual GitHub
approving review of the current machine-authored PR. Agents prepare changes;
trusted automation handles approved merge/release mechanics. No routine manual
workflow paste, merge, tag, publication or workflow-run approval is required.

The sole human maintainer and code owner remains `@urruegg`. A GitHub App is
a machine identity, not an extra human or independent human reviewer.
Private `urruegg/frontier-envisioning` remains the source, issue and PR host.

The maintainer confirmed current GitHub Pro, selected
`formal-review-machine-author`, selected `engineering-and-releases`, then
`approve-pr-gated-engineering-concept` after the complete proposed flow.
The actual choices are recorded on #48. The separate
`approve-written-pr-gated-spec` response approved this written proposal at
`8de16ca089ba0e2a1787496a4c65ecf17b7b6b4e` for planning. The linked later
plan/readiness was then explicitly approved at `e8ea6bd`, selecting
subagent-driven implementation and actual end-to-end evidence.
ADR-0030 still awaits its normal human PR acceptance. Pure #49 contracts
are locally verified; no current-policy activation or publication is inferred.

This document does not activate the new model or override current human-only
rules. Approval of the concept is not permission to change current protected
files, settings or credentials. Scope is routine engineering and GitHub
release distribution, not Azure deployment, repository administration,
destructive operations, secret rotation or public visibility.

## Evidence checked on 14 November 2026

- GitHub documents [private branch protections](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
  and [auto-merge](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request)
  as supported by Pro. The maintainer's Pro clarification supersedes the
  previous Free-only architecture assumption.
- GitHub's [workflow-trigger documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
  says ordinary `GITHUB_TOKEN`-created/updated PR runs can require a separate
  workflow approval. App installation tokens support normal event propagation.
  App identity and actual behaviour must be tested, not inferred from a trailer.
- The reference [policy at b3e8f42](https://github.com/urruegg/ernaehrungundsportapp/blob/b3e8f42e05e29b37f68e74fea3cf1b7216d1fa02/.github/agent-policy/NON_DELEGABLE_WORK.md)
  permits scoped execution after written authorisation rather than imposing
  Frontier's blanket workflow-file edit ban. Its main-push release workflow
  had a [successful observed run](https://github.com/urruegg/ernaehrungundsportapp/actions/runs/43590243953).
  No application/health data or domain rules were adopted.
- The reference's inspected main rule requires one approval, only its P0
  deployment-safety check, an up-to-date branch and resolved conversations.
  Stale-review dismissal, latest-push approval and no-admin-bypass were
  unchecked. These are not the proposed Frontier defaults.
- Sampled reference PRs are owner-authored; that is not a formal self-approval
  solution. Full review-history API access was unavailable, so absent formal
  reviews or individual merge actors are not asserted.
- Current Frontier settings listed neither rulesets nor classic branch
  protection. Instructions and job names are not proof of server enforcement.
- The existing Azure workflow can deploy on matching main pushes when
  `SHOWCASE_ENABLED` is true. The current flag was not independently verified;
  engineering-only activation must require it unset/false.

## Roles, credentials and proposal boundary

| Role | Allowed responsibilities | Not allowed |
|---|---|---|
| Proposal worker | Read approved source, prepare scoped changes, tests and generated outputs, commit proposal input, request a Draft PR | Human review, owner credentials/browser writes, main/tag/release writes, App keys, administration or deployment |
| Trusted proposal coordinator | Validate inert proposal data using the accepted policy, create/update scoped feature refs and App-authored PRs | Execute candidate scripts/hooks with write credentials, grant rights from a label/comment, directly update main |
| Read-only validator | Execute candidate build/test commands in an isolated validation context | Publisher keys, owner credentials, write/OIDC permissions or self-issued eligibility |
| Trusted eligibility reporter | Match actual source/control/run/check facts and report the accepted policy result using the App identity | Trust candidate-written success/approval metadata or execute candidate code |
| Human maintainer | Review the current diff/evidence and submit an actual eligible approval | Formal self-approval or representation of an App as a second human |
| Native merge and release automation | Execute declared actions after the real review/check gates; record actual results | Bypass, stale approval, implicit deployment/admin rights or replacement of immutable published artefacts |

Use a private proposal-input store, with a dedicated private GitHub proposal
repository as the default implementation. It is transport, not a new
canonical source/issue/PR host, a public fork or a runtime loader. Its creation
and access are bootstrap tasks, not performed by this specification.

The worker may write that proposal store but has no base-repository
contents/review/publishing write capability. Base access is read-only except
an explicitly limited preparation-request channel. Current owner-scoped
credentials must not be reused as supposed restricted machine credentials.
Human-authenticated browser pages remain inspection-only for agents.

The App-backed coordinator runs from the accepted control revision, outside
candidate-controlled execution. It validates safe relative paths, scope,
data/secret restrictions and workflow execution boundaries before exposing
a branch/PR. It applies changes as data, not shell commands or candidate hooks.
Requests to create a proposal are not approval to merge or publish.

Host coordination in the reviewed GitHub Actions control plane; this first
slice does not introduce an external approval service or Azure-hosted
controller. App authentication is consumed only by trusted coordination/
reporting stages, not candidate execution. The implementation must prove
that proposed workflow changes cannot run credential-bearing code before merge.

Neither a PR's edited guard nor its edited workflow may become the active
authority checker before acceptance. The harness uses a supported trusted
policy/enforcement location, not an editable candidate copy. If the actual
provider cannot enforce the restricted credential/write boundary, stop
activation; do not fall back to the maintainer's broad token.

## Native GitHub review and CI gates

Main requires a PR and one genuine approving review from the maintainer,
including the correct sole-owner CODEOWNERS mapping. Enable stale-review
dismissal, approval of the latest reviewable push, required current checks,
resolved conversations and no routine bypass. Do not manufacture another
human reviewer or weaken requirements when the owner-authored PR is ineligible.

Require `L1 quality gate`, `L2 browser tests`, `IaC validation` and the trusted
governance-eligibility result. Pin eligibility to the expected App/check origin.
The trusted result checks source SHA, control revision, workflow/run identities,
scope and actual conclusions; a same-named candidate job is not sufficient.

Before auto-merge, verify the actual PR author is the configured machine
identity; the approving reviewer is the human owner; the review applies to
the current head; the tested base is current; no blocking change request or
required check is outstanding. New commits or changed action intent invalidate
the earlier decision. Draft/unknown/skipped/cancelled states are not success.

PR/workflow proposals cannot run with repository-write, publisher secret or
deployment privileges before protected merge. CI coordination uses trusted
control code. A privileged metadata coordinator must never check out/run
candidate code; it can dispatch a main-defined read-only validator with the
exact candidate SHA. Never use privileged `pull_request_target` with a
candidate checkout.

The App may mark a validated PR ready and arrange native auto-merge, but cannot
supply the human approval. Confirm in a real pilot that App-authored PRs run CI
without an additional manual workflow approval and that the human can actually
use GitHub's Approve review. A source-file declaration is not pilot proof.

## Normal engineering loop

1. A scoped issue/request identifies outcome, constraints and acceptance.
   Prepare a Draft proposal with the appropriate design/plan and TDD evidence.
2. The coordinator creates the real App-authored branch/PR. The accepted
   pre-review policy prevents premature privileged execution.
3. Read-only validation runs; trusted eligibility verifies the real results.
   Failed tests are fixed with new scoped proposal commits and fresh validation.
4. The human reviews the current head and submits the actual approval.
5. Native gates permit merge; trusted automation records the merge/result.

Keep Superpowers design, planning, TDD and evidence. Approval-required decisions
can use design/plan PRs; they do not require repeated chat confirmations or
manual file copies as the steady-state permission mechanism. Significant open
scope/business decisions still require the accountable human.
More than one PR may be needed for design, implementation or release records;
the normal human channel remains PR review, not manual operational commands.

## Release intent and execution

An ordinary code merge does not automatically authorise publication.
A code or dedicated release PR can carry an explicit release intent: version,
source commit/tag target, product asset allowlist, release-note scope and
required acceptance evidence. Intent is part of the reviewed change.
Do not use an agent-applied approval label as its authority.

The versioned `frontier-release-intent/1.0` record has an explicit `publish`
boolean, canonical version/tag and `source_mode` of `merged-pr` or
`existing-tag`. Existing-tag mode requires the exact expected commit and
annotated tag-object SHA. Merged-PR mode resolves and records the actual
approved merge result; it must not invent a future commit SHA.
Repository and asset names are fixed by this profile, not arbitrary input
destinations. Missing intent or `publish: false` never means publish.

After protected merge, the trusted release workflow revalidates the approved
intent and source/merge association, builds the exact source, runs required
gates and independently reproduces the plugin ZIP. Build/validation is
read-only; publication uses short-lived, narrowly scoped write capability in
a separate trusted stage that does not execute package/candidate scripts.

Publish only these uploaded files:

- `frontier-envisioning-plugin-<version>.zip`
- `release-manifest.json`
- `sbom-spdx.zip`
- `SHA256SUMS.txt`

GitHub's automatic source ZIP/tar downloads are separate. Keep complete
bundles, demo/identity files and diagnostic CI receipts out of product
downloads. Use existing Python package/version/generator/reproduction logic,
not the reference application's npm semantic-release stack.

Create/verify the intended tag without force or movement, publish after the
checks and real approval, verify the published source/files/digests, and open
an App-authored release-record PR as needed. Native main protections apply to
that follow-up too; no direct main push to avoid another review.

Preserve no-cryptographic-attestation limits already chosen for the private
distribution. Pro does not enable private environment-required reviewers or
native build attestations. This profile must not depend on them or claim
signed builder/publisher evidence or a SLSA level.

The published GitHub Release is the announcement; Watch > Custom > Releases
is opt-in. Do not claim every contributor received/read it or add
email/Teams/package-registry distribution. FinOps stays optional Preview;
engineering review is not financial authority or current-scenario awareness.

## Action evidence and recovery

The accepted action record binds the repository, PR, App author, actual human
review ID/reviewer/current head, validated base, policy/control revision,
real CI/check identities, merge/source result, reviewed intent and action
outcomes/digests. Write approved-state evidence only after the real approval;
CI preparation cannot declare it from its own environment or input fields.

Use `frontier-pr-approved-action/1.0` for the accepted record. PR/review/run/
check identifiers are actual positive integers; source, head, base and
control commits are full SHAs; intent/artefact digests are SHA-256 values.
Include the exact App/reviewer identities, original approval/check links,
resolved source mode, result and `cryptographic_attestation: not-provided`.
These are controller-observed facts, not caller-supplied approval booleans.

Use idempotency keyed to the approved PR/head, intent and version. If an
existing tag or published asset disagrees with the expected source/hash,
stop; do not move the tag or replace the artefact. Repeated execution of an
already verified action records that actual state, not a new fictional release.
Partial draft/upload failures require honest failure/recovery evidence.
Retries stay within the approved intent; material changes need a fresh PR.

Default rollback is a revert/recovery PR with current approval, not a
force push, deleted release or destructive local/cloud operation.
Keep immutable records and preserve failure evidence.

## One-time bootstrap and scope isolation

The maintainer adopts the reviewed governance migration under the existing
agreement. This cannot authorise itself through a chat response or a candidate
guard edit. Current protected-file/settings restrictions stay binding until
the real adoption and supported enforcement have been verified.

Bootstrap aligns AGENTS, policy catalogue, hooks/harness routing, relevant
instructions/skills/agents, CODEOWNERS and actual GitHub protections. Address
the outstanding protected session-start routing dependency under #8; do not
silently claim it already migrated. Do not broaden models/tools indiscriminately.

Configure the private proposal store, repository-owned App and short-lived
credential paths without exposing private keys/tokens to the model, PR or
validation context. Record actual App identity/installation and restricted
provider capabilities. Initial administration, account consent and recovery
are explicit exceptions, not normal coding-agent permissions.

Audit all main/tag-triggered workflows. `SHOWCASE_ENABLED` must remain
unset/false for this engineering-only profile; do not accidentally provision
or deploy Azure after merge. Keep legacy `RELEASE_ENABLED` unset/false so an
old tagged publishing workflow cannot be re-enabled as a side effect.
The owner verifies these actual states; no current value is assumed here.

Pilot first with a safe non-release PR. Verify machine authorship, actual
native review, CI/event behaviour, credential isolation, fresh-head gates,
merge and zero deployment. Only then permit an explicitly approved release
pilot. No successful pilot or adoption has yet been performed.

## Preserved 1.10.0 and existing implementation

| Item | Preserved identity or boundary |
|---|---|
| Canonical source | Private `urruegg/frontier-envisioning` |
| Existing tag | `v1.10.0` |
| Annotated tag object | `5f9d21953db9c968ae56ac6d485baff3fc09b0ce` |
| Product source commit | `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9` |
| Prior local plugin SHA-256 | `9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`, not new CI proof |
| Existing tooling work | #47, now committed at `aa838fbb6df96766a632d6f6ec3151ca93c7803d`; preserved, not reset |

An approved recovery release intent can name the existing exact product source
while using a later accepted control workflow. Record both identities; do not
move the tag or pretend the old skipped run succeeded.

The earlier [manual-publication proposal](https://github.com/urruegg/frontier-envisioning/blob/4450e46b2e5930ec41dee0f5218751b28d090dba/docs/specs/2026-11-14-free-private-releases-design.md)
and [ADR-0029](https://github.com/urruegg/frontier-envisioning/blob/4450e46b2e5930ec41dee0f5218751b28d090dba/docs/adr/0029-free-private-release-preparation.md)
remain historical, unmerged evidence. Their manual context/profile is not
silently relabelled as this automatic contract. Reuse proven hashing/package
checks with an explicit successor approval/context adapter and regression tests.
No plugin version/runtime/schema change is needed for governance alone.

## Acceptance and verification

| ID | Required measured outcome |
|---|---|
| G48-01 | A real App-authored PR allows the sole human owner to submit an eligible native approving review; no duplicate human account, fake review or co-author-based identity substitution. |
| G48-02 | For an unchanged valid routine PR, the human performs only the normal review/approval; CI, merge and declared release mechanics need no manual file paste, merge/tag/publish/run approval. Multiple distinct PRs remain possible. |
| G48-03 | Missing/wrong/bot/self/stale approval, changed intent/head/base, failed/unknown/skipped checks or wrong check origin cannot merge or publish. |
| G48-04 | Candidate workflow/guard changes cannot become active authority, expose write/owner/publisher credentials, create eligibility or execute privileged operations before acceptance. Test the actual provider boundary, not merely a branch-name rule. |
| G48-05 | Main's actual native rules enforce current human review, L1/L2/IaC/trusted eligibility and no routine bypass; worker lacks direct main/tag/release/admin capability. |
| G48-06 | No Azure deployment, public visibility, credential rotation or destructive/admin action follows the engineering-only path, including existing trigger side effects. |
| G48-07 | Only a reviewed release intent can publish; independent exact-source reproduction, four-file allowlist, real evidence and failure/idempotency/immutable-version checks pass. |
| G48-08 | Existing 1.10.0 tag/source and #46/#47 evidence stay unchanged; old manual profile/unsupported native attestation are not used as success-shaped shortcuts. |
| G48-09 | Real bootstrap/pilot evidence confirms identity, supported harness isolation, actual flags/protections and event propagation before activation; current restrictions are not changed by proposal status. |

After written-spec approval, the implementation plan separates proposal
transport/App identity, trusted eligibility/native gates, release orchestration
and maintainer-only adoption. It names exact files, tests, dependencies and
existing-code reuse. No production implementation, App/store installation,
setting change, protected edit or deployment is part of this written proposal.
