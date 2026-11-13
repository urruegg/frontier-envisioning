# Guardrails for agent costs

*AI-assisted procedure maintenance, 13 November 2026; original authorship retained.*

These are optional Preview design proposals. First follow the full
[FinOps notice and current-scenario confirmation](../SKILL.md#awareness-gate--before-any-cost-operation-or-figure);
no cost operation, recommendation or figure before that gate. Model-derived
limits keep the non-GA grounding/model warning, assumptions and provenance.
Named owners must independently verify rates, terms and limits. Neither a
technical acknowledgement nor a guardrail-design gate is budget/purchase approval.
Decline leaves a documented budget gap, not an automatic readiness pass.
Draft workshops, ordinary value, identity and clean core preparation may
continue without FinOps. A deadline never waives awareness, pricing evidence
or external review.

## Strict financial build handover

Use the [versioned baseline procedure](../SKILL.md#quick-start--requested-versioned-baseline)
and [complete offline contract](agent-finops-baseline.md) for requested new work.
At **build handover**, financial readiness needs a complete validated per-agent
profile, owners, measurement and guardrails; meaningful twelve-month
low/expected/high demand/dependency scenarios and denominators; every in-scope
driver priced with current applicable evidenced rates/FX; a frozen exact
ID/version/material hash; matching external finance-owner/delegation review;
and current lineage, sharing and customer-scope validation.

**No conditional exception for unpriced costs.** Known usable supplied
stale/unverified prices may support explicitly provisional drafts with separated
contributions, not readiness. Unknown quantities/rates/necessary FX stay
unavailable, not zero. Synthetic Caldova prices/reviews never support real
financial handover; do not relabel example statuses as actual approval.

Keep structural validity, pricing, recorded review and current readiness
separate. CLI acknowledgement is technical only. Installation, saved consent/
approval, previous-day acknowledgement, local notes and workshop verdicts
supply neither current awareness nor owner review. Browser awareness is
separate, transient per document and resets on reload, not stored consent.

Snapshots are immutable only by local convention/application guards, not
authenticated, tamper-proof archival storage. Independently verify external
actor, finance owner/delegation and evidence: a review record authenticates none
of these and grants no financial/purchase permission. Material edits need a new
version and review; historical approval cannot override today's evidence gaps.
Migration preserves originals/provenance as a new draft without inherited
approval, acknowledgement or implicit FX. Legacy F1/F2 is not this strict gate.
Even planning-ready grants no budget, purchase, build, deployment or
protected-label authority.

Classify rates, FX and evidence; retain current transitive source, parent and
customer-scope restrictions. Customer JSON/Markdown and Blueprint records are
already projected: withheld is not zero or a complete public total. Never
reconstruct raw private dependencies client-side, fall back to legacy costs or
expose private headers, hashes or notes. Scope/classification is not clearance
or access control. Independent ordinary value stays independent;
legacy-derived Preview value must not be laundered into clean core work.

## Proposed operational controls — not implemented integrations

No single control spans the three billing systems: Azure budgets do not stop Copilot Studio consumption, and hard stops exist only per agent or environment (Power Platform admin center) or per policy (Microsoft 365 admin center). Design one control per system and key everything to the agent identity.

The legacy thresholds below are illustrative proposals, not automatic baseline
defaults or verified current provider behaviour. Confirm actual capabilities,
limits and owner-set thresholds independently; the named roles are proposed
responsibilities, not appointments or financial authority.

| Control | Where | Rule of thumb | Owner |
|---|---|---|---|
| Credit allocation per environment | Power Platform admin center | DEV and TEST small fixed allocations; PROD = sum of the agent limits | Power Platform team |
| Monthly credit limit per agent | Power Platform admin center | base credits + 25% headroom, rounded up to 1,000; alerts at 50%, 80%, 100%; hard stop at 100% | agent boss |
| Billing policy | Power Platform admin center / Azure | pay-as-you-go linked to the right subscription and cost centre | FinOps lead |
| Spending policy | Microsoft 365 admin center | monthly cap for Copilot Credits used by Cowork and Work IQ calls | Microsoft 365 admin |
| Budget and anomaly alerts | Azure Cost Management | base Azure cost + 25% headroom on the agent resources; anomaly alerts on | FinOps lead |
| Tagging standard | Power Platform, Azure, Foundry | agent-id, agent-name, environment, schema, journey, cost-centre (from the identity kit) | Power Platform team |
| Plan versus actual | Cowork digest or Power BI | monthly; variance threshold 20%; review in the agent board | FinOps lead |

**Kill switch.** Each agent has an owner who can disable it; the hard stop protects the budget, the owner protects the customer experience (tell users before a stop bites).

**Proposed ledger.** Record actuals with billing/effective cost, currency, charge
period, service/resource IDs, quantity/unit and identity tags. Verify the current
FOCUS specification before choosing fields. The historical release-1.4 target
for admin-centre/Cost Management imports is not evidence of an implemented
operate loop or live connector. The four public concept sources checked on
12 November 2026 are [reference metadata](baseline-sources.json), not rate
quotes, implemented APIs or FOCUS conformance. Future factories, live billing/
provider imports, cloud deployment and identity provisioning remain outside
this offline procedure. **1.10.0 is an unreleased internal candidate**; this
offline baseline capability does not promote FinOps to GA.

**Never** design a guardrail that measures individual employees; aggregate per agent, team or process.
