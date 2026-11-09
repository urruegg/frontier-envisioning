---
name: frontier-finops
description: |
  Models what a customer's Frontier agents cost per month in CHF: Copilot Credits by event with
  licence coverage, licences, Azure and run effort, unit economics, purchase options (pay-as-you-go,
  capacity packs, Copilot Credit P3, Agent P3), credit-cost sensitivity and guardrails keyed to the
  agent identity, shown on the blueprint's FinOps page. Use when asked "what will the agents cost
  per month", "Copilot Credits for <customer>", "cost per agent in CHF", "pay-as-you-go, packs or
  P3?" or "design the FinOps guardrails". Do NOT use for the value or ROI of the agents (use
  frontier-value-case), for the blueprint itself (use frontier-blueprint) or for Azure costs that
  are not about agents.
license: MIT
metadata:
  category: productivity
  icon: Money
  version: "1.6.1"
  plugin: frontier-envisioning
---

# FinOps for Frontier agents

One cost model per agent, in CHF: Copilot Credits by billable event (with the licence coverage rules), licences allocated by rule, Azure meters, the people who run the agent and the one-time build. From it: unit economics, the cheapest purchase option for the credits, how sensitive the credit cost is to the licence mix, the knowledge design and usage, and guardrails with owners. The blueprint shows it on a dedicated FinOps page; the value case takes the costs from here.

## Quick Start

```
User: "What will the Caldova agents cost per month?"
1. Find the blueprint (agents with canvases and identity), value.json and an existing finops.json
2. python scripts/seed_finops.py --blueprint blueprint.normalized.json --value value.json --out working/frontier/<slug>/finops.json
3. Review harness, audience, coverage and events per agent with the user; fill run and build effort
4. python scripts/finops_calc.py --finops finops.json --value value.json
5. python ../frontier-blueprint/scripts/build_with_identity.py --data blueprint.json --finops finops.json --value value.json --out-dir working/frontier/<slug> ...
6. Publish; reply with the cost per agent and month, the lowest purchase option and the top cost assumptions
```

Demo: the Caldova blueprint demo uses `examples/caldova-finops.json`. `examples/reference-hr-assistant.finops.json` is the method's worked example; the self-test checks the published results.

## When to Use

- The MVP agents have canvases and someone asks what they will cost, or which purchase model fits.
- The design needs cost ceilings, credit limits, alerts and tagging for the agents.
- Workshop feedback changed usage, licence or effort assumptions.

## When NOT to Use

- Running the whole engagement end to end: use frontier-envisioning instead.
- Agent names, colours and icons: use frontier-agent-identity instead.
- Gathering context or analysing transcripts: use frontier-context-discovery instead.
- The value, ROI or payback of the agents: use frontier-value-case instead.
- The blueprint HTML itself: use frontier-blueprint instead.
- PRD, NFRs and ADRs as documents: use frontier-solution-design instead (it takes the guardrails and the purchase model from here).
- Azure spend that is not about agents: use the customer's Azure Cost Management.

## Workflow

### Step 1: Locate the engagement
Read the normalized blueprint (agents, canvases, identity), `value.json` (volumes) and an existing `finops.json` from the engagement folder. One cost model per customer.

### Step 2: Prices and licence posture
Price order: the customer's own price sheet first, Swiss list prices second, USD list prices times the documented billing exchange rate third. Find the price sheet, licence counts and billing agreement (EA, MCA, CSP; MACC; existing packs or P3) with the `SearchM365` tool and read files with `ReadFileContent`. Rates come from `rates/rates-2026-11.json`, each with source and date; a rate older than 90 days must be verified (deep research or the browser; the sandbox has no internet). Never treat list prices as customer prices.

### Step 3: Usage model per agent
Seed with `seed_finops.py`, then review with the user and the agent maker: harness (standard, Copilot Chat, Foundry, GitHub), audience (employee or external), coverage (employee-facing standard and Copilot Chat use by licensed Microsoft 365 Copilot users is included within fair use; workflow-started runs, the GitHub harness and external audiences are billed), events per session (generative answers, tenant graph grounding, agent actions, flow actions, AI tools, content pages, voice), Azure lines, licences, run and build effort. Details: [references/finops-for-agents.md](references/finops-for-agents.md).

### Step 4: Calculate (gate F1)
`finops_calc.py` writes the results: cost lines per agent and month, unit costs, purchase options, credit scenarios, guardrails and lessons. Gate F1: every MVP agent has usage drivers and rates no older than 90 days.

### Step 5: Show it in the blueprint
`build_with_identity.py --finops --value` renders the FinOps page (cost per agent, where the credits come from, purchase options, sensitivity, guardrails, allocation keys from the agent identity, cost assumptions to clarify, rates and sources). The purchase model stays a hypothesis: no P3 commitment before a usage baseline.

### Step 6: Guardrails (gate F2)
Per agent: monthly credit limit with headroom, alerts and hard stop (Power Platform admin center); environment allocations; Microsoft 365 spending policies; Azure budgets and anomaly alerts; the tagging standard keyed to the agent identity; a monthly plan-versus-actual review. Hand them to **frontier-solution-design** as FinOps NFRs and a purchase-model ADR. Gate F2: guardrails designed, each with an owner. Rules: [references/guardrails.md](references/guardrails.md).

### Step 7: After the workshop
Cost assumptions are confirmed, adjusted or rejected on the FinOps page; `merge_value_feedback.py` (frontier-value-case) applies the verdicts to `finops.json` too. Rebuild to recalculate.

## Output format (reply)

- A table of the cost per agent and month (credits, licences, Azure, people) and the one-time build, in CHF.
- Unit cost per session and per outcome; the lowest purchase option and why to wait for a baseline.
- The two assumptions that move the cost most, with owners; the rates date and any "verify".
- File names of the HTML and `finops.json`.

## Guardrails

- Always show the usage model and the cost assumptions to the user before calculating, and the customer version before sharing.
- Never quote list prices as customer prices; always show the rates date and flag rates older than 90 days.
- Credits are not money until converted under the documented exchange-rate policy.
- Never recommend a P3 commitment before a usage baseline; purchases cannot be refunded.
- Always show people and build costs next to the credits; a credit-only view misleads.
- Customer versions never contain discounts, internal pricing guidance or internal milestone helpers.
- Mark preview features (agent dashboards, cost APIs) as preview with the date checked.

## Failure handling

- If `finops_calc.py` lists `missing` assumptions: collect them (volumes, effort) before showing costs.
- If an event name is unknown: use the names in the rates file; never invent a credit rate.
- If a rate is older than 90 days: verify it before the numbers leave Microsoft, or label it "verify".
- If the licence posture is unknown: keep the licensed share as a low-confidence assumption with the workplace team as owner.
- If the customer bills in another currency: set `fx` to the billing rate with its source and date.

## Files

- `rates/rates-2026-11.json` — credits per event, pay-as-you-go, packs, P3 and Agent P3 tiers, Swiss list prices, FX ratio; each with source and date
- `scripts/seed_finops.py` — cost model seed from the blueprint and the value case
- `scripts/finops_calc.py` — cost lines, unit economics, purchase options, scenarios, guardrails, lessons
- `scripts/apply_finops.py` — the FinOps page data into the blueprint JSON
- `scripts/fv_expr.py` — safe formulas (shared with frontier-value-case)
- `references/finops-for-agents.md`, `references/guardrails.md`
- `examples/caldova-finops.json` — Caldova MVP agents (fictitious); `examples/reference-hr-assistant.finops.json` — the method's worked example
