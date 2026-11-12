# Agent FinOps: a reviewable baseline before build handover

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted design preparation |
| Status | Design sections agreed; written-spec review and implementation plan pending |
| Scope | Offline baseline-first sprint; not a deployed FinOps Agent or live billing integration |
| References | [Catalogue](README.md), [Issue #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36), [Design](../specs/2026-11-12-agent-finops-baseline-design.md), [Draft sprint row](../sprints/README.md), [ADR-0028](../adr/0028-versioned-agent-finops-baselines.md) |

## Problem and desired outcome

An agent canvas describes an agent, but does not yet provide a versioned,
reviewed financial baseline suitable for build handover. The existing optional
Preview cost model is useful planning evidence, not an approved baseline.
Unknown costs, source freshness and review evidence must remain visible.

The maintainer supplied an Agent FinOps blueprint and requested brainstorming,
design and eventual implementation. The requested outcome is a reproducible
offline flow from agent discovery to scenarios, validation, unit economics and
safe Markdown/JSON handover. Draft workshops must continue without finance
work; financial completeness becomes mandatory at build handover.

## Input and evidence

The read-only document, **Frontier Envisioning Agent FinOps Blueprint**, has
1,315 lines and 39,037 bytes. Its SHA-256 is
`f42abed24fac0f93bbb62420ad3d5e0d7e194eb86d75adccfc94c295c2d797c7`.
The original is not copied into the repository or package. Personal local paths
are not part of the distribution.

The document describes a multi-phase programme. Its section 23 proposes an
offline first vertical slice, without live Azure, Copilot Studio, Foundry or
billing access. Product/design requirements in the brief are not themselves a
dated validation report for rates, APIs, licensing or sharing clearance.

Current source is human-merged main
`510c907b9bb020a28b352c2910d5f5abcbe8e3a6`, version 1.9.2.
The [design](../specs/2026-11-12-agent-finops-baseline-design.md) separates
verified public references, current implementation and proposed changes.

## Actual choices, not inferred approval

Seven structured conversation answers on 12 November govern the design:
build-handover gating, baseline-first scope, strict pricing completeness,
a versioned successor, the calculation policy, evidence/sharing safeguards
and the UI/delivery boundary. Exact selections and their limits are recorded
on [#35](https://github.com/urruegg/frontier-envisioning/issues/35) and
[#36](https://github.com/urruegg/frontier-envisioning/issues/36).

The chosen architecture adds a successor contract inside `frontier-finops`,
not a ninth skill or a new live application. Legacy `frontier-finops/1.0`
behaviour remains available. Migration creates a draft; it does not inherit
approval or silently change old CHF calculations.

All in-scope cost drivers need evidenced rates for financial handover
readiness. No conditional exception for unpriced costs was selected.
Drafts may show explicitly partial priced subtotals; unknown is never zero.

## First sprint and follow-ups

The first sprint covers profiles, versioned baselines, three meaningful
scenarios, explicit currencies/FX, source/rate validation, units, readiness,
safe exports, a synthetic Caldova example and end-to-end engineering proof.
The proposed product version is **1.10.0, an unreleased internal candidate**.
FinOps stays Preview; the seven other skills remain GA.

The dedicated three-target FinOps Agent factory, observed-data operating loop,
live providers and reference deployment are follow-ups. No connector,
authenticated financial-approval service or production integration is implied.

## Next gates and ownership

Accountable human owner: `@urruegg`. Design-section approval is not written-spec
approval, plan approval, a GitHub label change or permission to implement.
The user explicitly requires stopping for questions despite autopilot.

The draft SPRINT-007 catalogue row exists early. Its full work-item record
will link the actual implementation plan once the written spec is reviewed.
No placeholder plan or unrelated historical plan stands in for that gate.
Implementation must be split into reviewable work packages no larger than M.

Protected routing [#8](https://github.com/urruegg/frontier-envisioning/issues/8)
and release-cache [#30](https://github.com/urruegg/frontier-envisioning/issues/30)
remain human-owned. No merge, tag/release, deployment, settings change or
protected edit is included.
