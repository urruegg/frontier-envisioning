# FinOps for agents (frontier-finops/1.0)

Microsoft gives every building block for an agent cost model but no tool joins them: credits are reported in the Power Platform and Microsoft 365 admin centres, Azure meters in Cost Management, licences per user in Microsoft 365 billing, each with its own agent identifier. The model joins them per agent, in CHF, and keys them to the agent identity.

## Preview boundary

> Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.

The rates, coverage rules and examples below describe the provisional model,
not independently validated current pricing. Follow the [skill awareness
gate](../SKILL.md#awareness-gate--before-any-cost-operation-or-figure) before
operations, recommendations or figures. Each top-level seed/calc/apply or
Preview-dependent value/feedback command needs `--acknowledge-finops-preview`
after real current-scenario confirmation. Operational APIs default keyword-only
`acknowledge_finops_preview=False`; arithmetic helpers grant no permission.
Wrapper forwarding is one chain only. Renew for any new invocation/scope/model/
rates/grounding. Caller metadata, old JSON/notes, installation or a GA claim is
not human approval; imported/legacy FinOps is always Preview.

Costs, derived ROI/NPV, unit economics, assumptions, PRD/design and exports retain
the notice and scenario/model/rate/source provenance. Browser acknowledgement
is separate, transient and document-local: reload resets it; no localStorage
consent and the warning persists. Flat/nested results and linked assumptions
are gated; unrelated ordinary value remains. Private components, rankings and
outcomes are withheld, not zero; never recover `internal_notes`. This is not
encryption or access control.

## Cost lines per agent and month

| Line | Formula | Fixed or variable |
|---|---|---|
| Copilot Credits | sessions x billable share x sum(events per session x credits per event) x USD per credit x CHF per USD | variable |
| Licences | incremental seats x price; fleet licences (for example Agent 365) x allocation share | fixed |
| Azure | sum(quantity x unit price): Foundry models and tools, Speech, search, hosting | variable |
| People | run hours (agent boss, maker) x loaded rate | fixed |
| Build | one-time effort, shown separately and used in NPV and payback | one-time |

**Coverage.** Employee-facing runtime of Standard and Copilot Chat harness agents is included for licensed Microsoft 365 Copilot users within fair use: billable share = 1 - licensed share. Workflow-started (autonomous) runs, the GitHub Copilot harness, computer use and external audiences are billed: billable share = 1. Work IQ API use is not included.

**Events** (rates file, credits each): classic answer 1, generative answer 2, agent action 5 (includes triggers, deep reasoning, computer use), tenant graph grounding 10, agent flow 0.13 per action (13 per 100), AI tools 0.1 / 1.5 / 10 per 1,000 tokens (basic / standard / premium), content processing 8 per page, reasoning 10 per 1,000 tokens, voice 10 per minute (higher tiers 35 and 75, verify). A grounded answer counts one generative answer plus one grounding event.

## Prices and exchange rate

1. The customer's price sheet (EA or MCA price list, CSP quote).
2. Swiss list prices (rates file): Microsoft 365 Copilot CHF 24.30, Copilot Business CHF 17.00, Microsoft 365 E7 CHF 85.92, Agent 365 CHF 12.10 per user and month, capacity pack CHF 162 per 25,000 credits; excluding VAT.
3. USD list prices x the documented billing exchange rate. The rates file's 0.81 CHF per USD is the ratio implied by Swiss list prices; a single rate across products is an approximation (products differ), MCA converts monthly and EA uses the agreement currency.

Every rate carries a source and a date. Stale (older than 90 days) or unverified
inputs may remain only as explicitly flagged draft gaps where allowed.
Labelling them "verify" does not pass F1, validate pricing or satisfy a
budget/purchase approval gate; obtain and record current verification first.

## Purchase options

| Option | Rule in the model |
|---|---|
| Pay-as-you-go | credits x USD 0.01 x CHF per USD; billed in arrears; draws down MACC |
| Capacity packs | ceil(monthly credits / 25,000) packs at the Swiss list price; no rollover; service denial when exhausted |
| Copilot Credit P3 | best of nine tiers (300,000 credits 5% ... 300 million 20%) plus pay-as-you-go above the tier; one year, no refunds; below the smallest tier the unused commitment is lost |
| Microsoft Agent P3 | best of three tiers (USD 20,000 5%, 100,000 10%, 500,000 15%) over credits plus eligible Foundry usage |

The comparison basis is credits plus Agent-P3-eligible Azure usage. A lowest
modelled option is provisional, not commitment advice. Independently verify
prices, terms and assumptions; the real budget owner decides.

## Unit economics and scenarios

Cost per session and per successful outcome (FinOps for AI), compared with the human cost per task in the value case. Credit scenarios override named variables (licensed share, grounding share, usage) to show what moves the credit cost; typical lessons: people often cost more than credits; tenant graph grounding drives most credits; the licence mix moves the credit cost by about two thirds; purchase options matter at scale.

## Gates

- **F1** cost model complete: every MVP agent has usage drivers and current
  verified rates no older than 90 days. Stale/unverified draft gaps do not pass;
  F1 itself is not validated pricing or budget/purchase approval.
- **F2** guardrails designed, each with an owner (references/guardrails.md).
- **F3** is the historical proposed operate-loop gate: actuals flowing and variance
  within an agreed threshold. The old release-1.4 target is not delivery evidence.

## Data contract (abridged)

```json
{"schema": "frontier-finops/1.0", "currency": "CHF", "fx": {"policy": "swiss-list-ratio", "chf_per_usd": 0.81, "source": "", "date": ""},
 "purchase": {"option": "payg", "note": "hypothesis"},
 "assumptions": [{"id": "ASS-101", "statement": "", "unit": "share", "low": 0.2, "base": 0.4, "high": 0.7, "scope": "finops"}],
 "agents": [{"id": "D2-A01", "harness": "standard", "audience": "employee", "coverage": "licensed users included",
             "vars": {"requests": "ASS-021", "licensed_share": "ASS-101", "sessions": "requests * 1.3"},
             "usage": {"sessions": "sessions", "billable_share": "1 - licensed_share",
                       "events_per_session": {"generative_answer": 3, "graph_grounding": "3 * 0.3", "flow_action": 6}},
             "azure": [{"name": "", "qty": "", "usd": 1.0, "agent_p3_eligible": true}],
             "licences": [{"sku": "AGENT_365", "seats": 100, "allocation_share": 0.2}],
             "people": {"run_hours_month": 24, "rate_chf": 120, "build_one_time_chf": 60000},
             "outcome": {"name": "purchase request routed", "per_month": "requests"}}],
 "credit_scenarios": [{"name": "No Microsoft 365 Copilot licences", "kind": "licences", "set": {"licensed_share": 0}}],
 "guardrails": {"headroom": 0.25, "alerts": [0.5, 0.8, 1.0]}}
```

Variables may refer to value assumptions (volumes).
After renewed confirmation,
`python scripts/finops_calc.py --finops finops.json --value value.json --acknowledge-finops-preview`
joins both registers. Cached/model/rates mismatch requires fresh calculation
before apply; see [standalone apply](../SKILL.md#standalone-apply-after-renewed-confirmation).
On decline, preserve originals and return to clean core/ordinary non-FinOps
inputs, not cached Preview value; no automatic legacy-field removal is promised.

## Sources

Rates file `sources` (B1 billing rates, B2 licensing guide, B3 credits guide, B4 Copilot Credit P3, B5 Agent P3, B6 Swiss price pages, B8 credit estimator, B9 Azure pricing calculator); FinOps Framework and FinOps for AI (finops.org); FOCUS specification (focus.finops.org).
