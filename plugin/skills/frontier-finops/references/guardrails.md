# Guardrails for agent costs

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

**Ledger.** Actuals land in a FOCUS-aligned ledger: BilledCost, EffectiveCost, BillingCurrency, ChargePeriodStart/End, ServiceName, ResourceId, ConsumedQuantity and ConsumedUnit, plus the identity tags; FOCUS 1.5 adds the agent as a principal and the consumption currency (credits). Imports of the admin-center reports and Cost Management exports are planned for release 1.4 (operate loop).

**Never** design a guardrail that measures individual employees; aggregate per agent, team or process.
