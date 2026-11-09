# Documentation, governance and accessibility design

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-09 |
| Author | Copilot SDK in VS Code; AI-assisted design and maintenance |
| Status | Design, implementation plans and readiness approved by the user on [#6](https://github.com/urruegg/frontier-envisioning/issues/6); delivery evidence separate |
| Scope | The eight approved repository improvements, delivered in bounded workstreams |
| References | [Spec catalogue](README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/6), [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md), [Plan](../plan/2026-11-09-docs-governance-implementation.md), [Sprint](../sprint/SPRINT-001-docs-governance-and-accessibility.md), [Product requirements](../prd.md), [Solution design](../solution-design.md) |

The design-stage approval statements below are retained as recorded evidence.
Current plan/readiness approval is linked in the metadata; it does not accept
policies, grant protected permissions or prove delivery.

## Approved source and approval boundary

The user approved `frontier-docs-governance-proposal.md` on 9 November 2026.
Its SHA-256 is
`1a82b7be5241bdd1108439c3aedc97a7ec2aa9ec6557c86d2d1a93957156c46c`.
This repository spec records that design as a portable work package; it does
not promote proposed policies, plans or permissions to active state.

The user explicitly requested delegated implementation **after plan approval**.
No implementation worker starts until that approval is recorded. People also
retain protected readiness/approval labels and all existing human-only actions.
Current protected instructions/hooks remain binding during migration.

Planning baseline: `d249fcab0fae2fc8b161ccce848cc911ffcd76f4`, merged PR #5.
The HTML audit used renderer commit
`e86774024851ebe7024ea655e066f3107fce0457`, which is included in that main.

## Scope and requirements

| ID | Approved requirement | Acceptance |
|---|---|---|
| DG-01 | Add `.github/agents/docs-agent.agent.md` | Repository-owned documentation persona; `read/search/edit/todo`; no model override, terminal/admin/deployment authority or invented approvals |
| DG-02 | Split repository requirements and architecture | `docs/prd.md` owns Part A; `docs/solution-design.md` owns Part B and inventory; original IDs, historical claims and known legacy anchors retained; bundle includes both |
| DG-03 | Adapt Copilot instructions | Concise authority map, factual evidence, correct private GitHub host, Frontier invariants and existing Superpowers fallback; no HR/host-cutover assumptions |
| DG-04 | Establish linked intake | Singular `docs/idea`, `docs/spec`, `docs/plan`, `docs/sprint`; direct-child catalogues; every ready implementation item links a real issue and governing records |
| DG-05 | Add Frontier agent policy | Proposed policy catalogue, workflow, non-delegable boundaries, proportional aggregate KPIs and human-only emergency procedure; no weakened guardrails |
| DG-06 | Refine ownership and collaboration | Human-only #8; default `@urruegg`, appropriate shared ownership, actual write-access eligibility/invitation, existing infrastructure owner retained unless explicitly transferred |
| DG-07 | Standardise eligible headers and references | Six-field metadata and deterministic checks with explicit historical/licence/generated/template/machine/product exemptions; no bulk modification of guarded output inputs |
| DG-08 | Improve measured accessibility | Source-based focus/ARIA/contrast/target/reflow remediation, development-only axe integration and real keyboard checks; manual acceptance and best-practice/incomplete findings reported separately |

## Documentation architecture

New work uses the requested singular directories. Existing `docs/plans/`
remains a historical catalogue; no bulk move breaks earlier PR links.
Product ADRs remain distinguished from engineering ADRs.

The documentation agent maintains eligible prose, catalogues, status and
references. Existing planner, builder, renderer and reviewer roles retain
their responsibilities. Reusable procedures live in skills, policy lives in
agent-policy, and deterministic validation lives in the existing Python tools.

Each eligible document has one H1 followed by:

`Version | Date | Author | Status | Scope | References`.

Required YAML frontmatter remains first. Document version/date/authorship are
truthful and distinct from product releases and accountable ownership. Status
does not prove approval; a real human approval record is required when needed.
Plan worker/Goal/Architecture/Tech Stack sections follow the metadata table to
honour this approved header convention.

Header eligibility initially covers active owned docs, ordinary root/area
guides and new policy documents. Preserve licences/notices, historical intake
and legacy plans, tracker/PR formats, vendor files, central CHANGELOG and
machine/product contracts. The [audit](../intake/2026-11-09-markdown-header-audit.csv)
classifies all 134 original tracked Markdown files; not all are migration targets.

## Intake and sprint contract

Idea states the problem/evidence and alternatives. Spec owns approved behaviour,
acceptance and constraints. Solution design/ADRs record architecture changes.
Plan owns files, failing tests, commands and dependencies. Sprint is the delivery
index, not an approval or a substitute for those documents.

Every implementation item, including documentation, belongs to a sprint and
has issue/idea/spec/plan links. Related issues may reuse applicable approved
governing records; unrelated changes do not share a package merely to avoid
the contract. Offline drafts remain drafts until real issues are verified.

Sprint work-item columns:

`Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence`.

Catalogues and backlinks change in the same PR. Stable IDs are allocated once
and retain successor links. Labels remain existing human-owned ready/approval
controls, not a new inferred tracker state machine.

## Document split and compatibility

Retain all FR/NFR/AC/D/TD/ADR IDs and A/B section labels during migration.
The PRD owns release plan/product decisions and historical Part A acceptance.
Solution design owns components, flows, security, verification approach,
technical decisions/sources and the historical file inventory.

Keep a short old-path landing page with explicit anchor mappings and links,
not a third maintained content copy. Update active references, the bundler and
START-HERE text. Historical source inventories/releases remain unchanged.
The customer-engagement scaffold already outputs two files and is not redesigned.

Protected session-start routing still names legacy paths. A person changes it
under #8; agents do not edit protected hooks as part of prose migration.

## Governance and ownership

The new policy files are Proposed until actual human acceptance. AGENTS remains
the entry point. Prose, tools, labels, GitHub rulesets and permissions are
different layers; instructions are not an access-control boundary.

Retain customer neutrality, stdlib/offline processing, input-as-data boundaries,
source-generated output, immutable releases and icon terms. Branding is not
identity provisioning. HubWorks integration remains controlled source
contribution, not an assumed dynamic external-repository loader.

Initial evidence completeness/link/gate metrics use applicable 100% targets;
drift, prohibited data/secret incidents and non-delegable violations use zero
targets. Relative lead-time/rework targets wait for aggregate baselines.
Do not rank people, minimise escalations or weaken tests to improve a metric.

CODEOWNERS does not grant access or require approval from every named owner.
Last matching pattern wins. `/infra/` currently belongs to
`@urruegg_microsoft`; the approved design preserves that owner unless a human
explicitly transfers it. A future `/data/` pattern does not create a data folder.
The second contributor's actual write-access eligibility/invitation is human-only.

## Accessibility architecture and evidence

Use [Microsoft's accessibility testing guidance](https://learn.microsoft.com/en-us/microsoft-edge/accessibility/test)
and WCAG 2.2 AA as the target. Existing
[38-scan evidence](../intake/2026-11-09-accessibility-audit.json) records Edge
157.0.4341.42 and axe-core 4.11.0, all fourteen views/light-dark, site/catalogue
and selected states, plus real keyboard and 320px measurements.

The evidence contains ten rule types, including invalid filter attributes,
focusable SVG nodes under `role=img`, 1.86:1 text contrast, small targets and
confirmed dialog focus faults. Repeated occurrences are not unique bugs.
Incomplete/best-practice findings are not silently suppressed or called WCAG failures.

Fix the drawer's closed/open focus semantics and meaningful roles; scope tab
keyboard handling separately from global shortcuts; preserve brand/icon data
while making rendered text and hit areas accessible. Narrow layout changes
must target measured causes and keep real 2D diagram/table scrolling local.
Do not hide page overflow globally.

Axe is development-only and uses the existing Playwright suite. No external
resource, CDN or CSP exception is introduced into the offline product.
Historical raster/profile/identity inputs remain guarded.

The identity catalogue's empty-header findings are best-practice-only in this
baseline and arise in a guarded product generator. They stay explicitly
tracked for separate versioned identity-output approval; this initial renderer
plan neither masks them in hosting nor changes golden/profile hashes.

Human zoom, screen-reader, voice and real Windows high-contrast assessment
are distinct acceptance records. Passing automation is not full WCAG certification.

## Delivery, dependencies and safeguards

- Documentation #10 establishes the reusable records and document/checker surfaces.
- Governance prose #9 follows those authoritative paths; human #8 handles
  ownership, permissions and protected routing.
- Renderer #7 can implement source-only changes independently, but its final
  product-document updates wait for the document split.
- Shared files, generated output, version changes and final gates have one
  owner at a time. No parallel writers or reusable agent worker pool.
- New branches/worktrees start from updated approved main. No force push,
  main push, merge, tag, release, deployment or protected edit is delegated.
- Repository-only planning/docs does not require a plugin bump. A packaged
  change uses an unreleased version or bumps before the first post-release edit.
- Changes beyond approved contracts, unexplained failures, altered identity
  inputs or protected boundaries stop the relevant task and require review.

## Design approval record

On 9 November 2026 the user wrote:

> Okay design is approved and you can write the plan to implement it sub agent delegated implementation after plan approval

This is the design approval. The linked plans and sprint remain Proposed until
separate plan approval; no protected approval label was applied by an agent.
