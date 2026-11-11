# ADR-0025: Four-part journey, shared PRD model, Plan board and risk register

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-11 |
| Author | Original author not recorded in received ADR; Copilot AI-assisted selective adaptation |
| Status | Proposed; received proposal is not a separately accepted ADR |
| Scope | Received 1.7.0 product rationale adapted for unreleased 1.7.1; not release approval |
| References | [Catalogue](README.md), [PRD intake](../prd.md#171-development-intake), [Solution design intake](../solution-design.md#171-development-intake), [Approved integration design](../specs/2026-11-10-handover-1.7-intake-design.md), [Plan](../plans/2026-11-10-handover-1.7-intake-plan.md), [Received evidence](../intake/handover-1.7.0.md), [Issue #22](https://github.com/urruegg/frontier-envisioning/issues/22) |

## Context

The received ADR was Proposed on 10 November 2026. It describes why the earlier
three-part navigation mixed envisioning and design, left the MVP requirements
visible only in a later design document, and lacked a cross-agent delivery board
and rated risk register. It also calls for attendee contributions tied to evidence.
These are received design motivations, not new claims about customer workshops.

The selective integration design and written plan were human-approved separately.
Their approval does not mark this ADR Accepted or approve a 1.7.1 release.

## Decision proposed

- **Four parts, one question each.** Vision: Overview, Org model, Blueprint,
  Journeys, Use cases, PRD. Design: Agents, Agent identity, Target architecture,
  IT readiness. Build: Roadmap, Plan, FinOps. Workshops: Attendees, Discovery,
  Risks, Evidence. Blueprint `parts` can override labels and descriptions.
- **One PRD model.** Identical `prd_model.py` copies derive the embedded PRD and
  scaffolded `design/prd.md`. Authored presentation fields survive rebuilds;
  IDs use the complete blueprint's canonical agent order before subset selection.
- **Plan from Agent Factory.** Compute stages from the existing eight handover
  checks; display journey lanes, stage columns, phases and WIP limits. CSV is
  handover data requiring destination mapping, not live integration or native
  import certification. Readiness/WIP is not approval.
- **Risk register.** Derive use-case/readiness risks, add canon and retain
  authored/workshop content. Rate likelihood and impact from 1 to 5; export
  `risk:<id>` feedback and merge it. Preserve normalised source bindings,
  retired-ID history and independent content provenance across source edits.
  Discarding that history cannot guarantee old ID-only feedback identity.
- **Evidence-based attendees.** Contributions cite sources and transcript times;
  missing evidence is flagged. Seed from transcript speakers, without inventing
  participation or consent.

## Consequences

The PRD is visible before architecture design, remaining a hypothesis until the
workshop agrees its scope (`prd:scope`). FinOps accompanies the build scope and
remains optional. Seventeen views require navigation, keyboard, download and
feedback regression coverage. Named M1/M2 planning milestones remain separate
from product release numbers and live server changes.

Keep current accessibility, privacy and attribution corrections rather than
copying the received files wholesale. Resolve risk visibility before customer
scrubbing and derive final risk/PRD models afterwards; customer export is not
external/IP clearance. The source host stays private and development distribution
Microsoft internal. Actual Cowork installation, publication and deployment are
not consequences of this proposal.

## Alternatives considered

- Keep three parts: envisioning and design questions remain mixed.
- Keep PRD only in the design folder: requirements are absent from the workshop
  view and independent derivation can drift.
- Require a separate planning service: needs tenant/accounts; CSV supports a
  bounded handover without claiming live integration.
- Leave risks as use-case prose: lacks a shared rating, owner and heat map.
