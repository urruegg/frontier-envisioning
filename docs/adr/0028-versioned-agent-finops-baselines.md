# ADR-0028: A versioned offline successor for Agent FinOps baselines

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted design preparation |
| Status | Proposed; conversation architecture choice recorded, written/PR acceptance separate |
| Scope | Versioned baseline contracts, legacy compatibility and financial handover boundaries |
| References | [Catalogue](README.md), [Issue #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36), [Design](../specs/2026-11-12-agent-finops-baseline-design.md), [Idea](../ideas/2026-11-12-agent-finops-baseline.md), [Draft sprint row](../sprints/README.md), [Solution design](../solution-design.md) |

## Context

The current `frontier-finops/1.0` model is an optional Preview CHF estimator
with guarded value integration, calculation receipts and extensive privacy
regressions. A new brief asks for per-agent versioned baselines, explicit
currencies/FX, three scenarios, source evidence and financial handover checks.
It also describes a live FinOps Agent programme beyond the first slice.

The plugin must remain offline, deterministic and standard-library-only.
Existing artifacts and numerical/provenance semantics must remain readable.
Changing the old contract in place would blur migration, currency and approval
meaning. A new live application would exceed the chosen baseline-first scope.

## Decision

Propose a distinct `frontier-finops-baseline/1.0` contract inside the existing
`frontier-finops` skill. Reuse agent IDs, Preview/privacy boundaries, wrapper
preflight, renderer conventions and build gates. Retain eight skills and
legacy behaviour. Explicit migration yields a draft with preserved lineage,
not an automatically approved baseline.

Separate structural validation, complete pricing and externally evidenced
owner review. Bind review to a frozen version/content hash and create a new
version after material change. Unknown costs never become zero, and unpriced
in-scope drivers block financial handover under the chosen strict policy.

Financial completeness is required at build handover, not draft creation.
Readiness/approval records are not authenticated financial authority, tamper-
proof storage, budget approval or deployment permission. Current Preview
awareness and source restrictions remain binding.

## Consequences

The first slice adds explicit contracts and adapters instead of changing every
legacy calculator. It must test migration, receipts, privacy and both paths.
Currency/units, partial amounts and source freshness become visible rather
than silently inherited. Browser notes cannot manufacture baseline approval.

The Blueprint uses separate active-baseline projections; it does not blend
legacy and successor totals or silently change old CHF value calculations.
Live providers, the three-target FinOps Agent factory and the operating loop
remain separate future work with their own runtime/authority boundaries.

## Alternatives considered

- In-place legacy mutation: fewer contracts, but greater numerical, receipt,
  value-integration and migration risk.
- Separate deployable FinOps service now: stronger possible runtime authority
  and storage, but a new application/operations scope outside this sprint.
- Entirely optional finance or conditional unpriced handover: not the
  maintainer's selected build-handover/strict-pricing policy.

## Status and evidence

The maintainer selected `versioned-successor` for architecture section 1 and
approved the other three design sections in structured conversation on
12 November. Exact choices D35-01 to D35-07 are recorded on #35/#36.
This ADR remains Proposed until the repository's human acceptance step;
written-spec/plan approval, ready/approval labels and implementation are not
inferred from its existence.
