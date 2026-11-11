# Guardrails for agent costs

These are optional Preview design proposals. First follow the full
[FinOps notice and current-scenario confirmation](../SKILL.md#awareness-gate--before-any-cost-operation-or-figure);
no cost operation, recommendation or figure before that gate. Model-derived
limits keep the non-GA grounding/model warning, assumptions and provenance.
Named owners must independently verify rates, terms and limits. Neither a
technical acknowledgement nor a guardrail-design gate is budget/purchase approval.
Decline leaves a documented budget gap, not an automatic readiness pass.

No single control spans the three billing systems: Azure budgets do not stop Copilot Studio consumption, and hard stops exist only per agent or environment (Power Platform admin center) or per policy (Microsoft 365 admin center). Design one control per system and key everything to the agent identity.

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
operate loop or live connector.

**Never** design a guardrail that measures individual employees; aggregate per agent, team or process.
