# FinOps for agents

*AI-assisted procedure maintenance, 13 November 2026; original authorship retained.*

For requested new work, use the versioned offline
`frontier-finops-baseline/1.0` path inside the existing optional Preview skill.
The older `frontier-finops/1.0` CHF path remains explicit and backward-compatible;
there is no automatic conversion. **Release build 1.10.0**;
FinOps remains optional Preview.

## Preview boundary

> Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.

The rates, coverage rules and examples below describe the provisional model,
not independently validated current pricing. Follow the [skill awareness
gate](../SKILL.md#awareness-gate--before-any-cost-operation-or-figure) before
operations, recommendations or figures. Every successor operation and each
legacy seed/calc/apply or Preview-dependent value/feedback command needs
`--acknowledge-finops-preview`
after real current-scenario confirmation. Operational APIs default keyword-only
`acknowledge_finops_preview=False`; arithmetic helpers grant no permission.
Wrapper forwarding is one chain only. Renew for any new invocation/scope/model/
rates/grounding. Caller metadata, old JSON/notes, installation or a GA claim is
not human approval or financial consent. Yesterday's acknowledgement and saved
approval are not current awareness; imported/legacy FinOps stays Preview.

Costs, derived ROI/NPV, unit economics, assumptions, PRD/design and exports retain
the notice and scenario/model/rate/source provenance. Browser acknowledgement
is separate, transient and document-local: reload resets it; no localStorage
consent and the warning persists. Flat/nested results and linked assumptions
are gated; unrelated ordinary value remains. Private components, rankings and
outcomes are withheld, not zero; never recover `internal_notes`. This is not
encryption or access control.

## Versioned baseline — new work

Follow the [working lifecycle commands](../SKILL.md#quick-start--requested-versioned-baseline):
seed an existing agent, complete a draft, calculate, freeze, obtain and record
external review, then apply/export for an explicit audience. All operations
require an explicit `--as-of YYYY-MM-DD` and fresh awareness. The
[complete baseline contract](agent-finops-baseline.md) owns the exact schema,
CLI, review fields, arithmetic bounds and output shapes; do not guess
aggregate flags or use a projected report as an authoritative input.

### Inputs and draft arithmetic

- Complete the linked per-agent profile: business/technical/finance owners,
  outcome, demand, scope, measurement and guardrails. Canvas approval or a
  generic Blueprint owner does not supply these roles.
- Author exactly low/expected/high, each with twelve monthly demand values.
  Vary demand and another sourced dependency affecting cost or an outcome
  denominator, such as tokens per run, retries or success share. Final-total
  multipliers and unused decorative drivers are not meaningful scenarios.
  Declare flat or authored monthly demand, assumptions, exclusions, risks and
  confidence; do not hide an unresolved driver as an exclusion.
- Use decimal-string quantities/rates, typed units/pricing blocks and explicit
  allocations. Report monthly/annual recurring, one-time and first-year
  estimates. Per-run, per-success and per-outcome metrics need explicit
  denominators, period and cost basis. Missing or zero denominators make the
  metric unavailable, not zero or infinity.
- Initial currencies are CHF, EUR and USD, one reporting currency per baseline.
  Cross-currency amounts require explicit pair/date/method and evidenced FX.
  No currency, licence coverage, implicit list-price-ratio conversion or
  universal rate-freshness lifetime is inferred.
- Known usable supplied stale/unverified rates or explicit FX may support
  **PROVISIONAL — pricing evidence incomplete** drafts. Retain sources, dates
  and gaps; distinguish verified, provisional and known-priced contributions.
  This does not verify the combined figure or pass handover. Inapplicable or
  contradictory inputs still refuse or retain blocking diagnostics.
- Unknown numeric quantities, rates or necessary FX leave full totals and
  dependent metrics unavailable (`null` with reason), never zero. A priced
  subtotal is not the full total; an empty contribution group is unavailable.
  `available`, `incomplete`, `provisional`, `unavailable` and `withheld` differ.
- Python owns exact intermediate decimal arithmetic. Unsupported
  representations, including non-terminating intermediate line-price division,
  explicitly refuse rather than silently round inputs. Only final money rounds
  to cents and final unit ratios to six places, `ROUND_HALF_UP`; JavaScript
  must not recalculate figures.

The [synthetic Caldova D3-A05 example](../examples/caldova-agent-baseline.json)
demonstrates twelve-month scenarios, not a complete real deployment scope.
Its invented CHF 1 per 1,000 tokens is **not** a quote, actual current retail
price or commercial verification. Synthetic model/source/rate/review markers
always block real financial handover. Never edit example statuses to fabricate
real approval or unqualified financial readiness.

### Review, migration and sharing

Draft workshops and clean core/ordinary value/identity work can continue when
FinOps is absent or declined, with financial gaps and actual owners recorded.
At **build handover**, apply the [strict financial gate](guardrails.md#strict-financial-build-handover):
complete validated profile and scenarios, all in-scope drivers currently
evidenced/priced, denominators, frozen exact ID/version/material hash,
externally evidenced finance-owner/delegation review and current lineage/scope.
Unpriced costs have no conditional exception. Structural validity, pricing,
external lifecycle and dated readiness are separate; historical approval may
remain while current evidence blocks readiness.

Freeze protects local snapshots by convention/application guards only, not
authenticated, tamper-proof archival storage. Review records assert external
evidence but do not authenticate the actor, delegation or evidence. Material
changes need a new version and review. A raw `approved` field, workshop verdict,
local notes, cached DTO, deadline or technical acknowledgement cannot replace
review. Even `ready: true` grants no financial, purchase, build or deployment
permission.

Use only [explicit migration](../SKILL.md#explicit-migration-never-automatic-conversion)
for a selected legacy original. Unproved numeric mappings yield a context-only
draft with gaps. Preserve original bytes and source/classification provenance;
inherit no approval, acknowledgement, currency, licence coverage, old results/
scenarios or implied FX as new arithmetic authority. New baseline data alone
does not make independent ordinary value Preview or automatically feed legacy
CHF NPV/ROI. Legacy-derived value remains Preview; never reuse it as clean core.

Classify rates, FX and review/evidence context as well as profile and lines.
Current transitive source dependencies, parent restrictions and customer scopes
constrain derivatives regardless of status. Unknown ancestry fails closed.
Sharing classes and matching caller scope are classifiers, not authorisation,
clearance or access control. Customer JSON/Markdown and Blueprint `agent_finops`
records are already projected: use them, not client-side raw reconstruction.
Withheld dependencies are not zero, public rows are not a full total, and no
fallback legacy costs, private headers, hashes or notes may be recovered.
Internal reports retain private context; exports are derivatives, not approved
models or general redistribution clearance.

Apply accepts repeated `--baseline`/`--review`; the existing wrapper accepts
repeated `--agent-finops`/`--agent-finops-review`, with explicit date and relevant
audience/scope. Supply authoritative drafts/snapshots and matching review
records, not cached views; legacy and successor costs are mutually exclusive.
Combined ontology/baseline source resolution uses detached namespaces,
preserves consumed restrictions and rejects ambiguous collisions before
outputs. Unrelated context must not taint independent financial records.
This opt-in strict graph does not globally harden ordinary GA process handling.

Future FinOps Agent factories, operating loops, live billing/provider imports,
cloud deployment and identity provisioning are outside this offline path.
The four [public concept sources](baseline-sources.json), checked on
12 November 2026, ground unit economics, estimates and FOCUS terminology only:
not actual rate quotes, current commercial verification, implemented APIs,
connectors or FOCUS conformance.

## Legacy model — `frontier-finops/1.0` only

The remaining formulas, coverage assumptions, prices, F1/F2 gates and abridged
contract describe the existing legacy path, not successor defaults or its
strict financial handover gate. Credits, Azure meters and licences belong to
different billing systems; this planning model groups them per agent in CHF
and keys them to the agent identity. It does not ingest live bills.

### Cost lines per agent and month

| Line | Formula | Fixed or variable |
|---|---|---|
| Copilot Credits | sessions x billable share x sum(events per session x credits per event) x USD per credit x CHF per USD | variable |
| Licences | incremental seats x price; fleet licences (for example Agent 365) x allocation share | fixed |
| Azure | sum(quantity x unit price): Foundry models and tools, Speech, search, hosting | variable |
| People | run hours (agent boss, maker) x loaded rate | fixed |
| Build | one-time effort, shown separately and used in NPV and payback | one-time |

**Coverage.** Employee-facing runtime of Standard and Copilot Chat harness agents is included for licensed Microsoft 365 Copilot users within fair use: billable share = 1 - licensed share. Workflow-started (autonomous) runs, the GitHub Copilot harness, computer use and external audiences are billed: billable share = 1. Work IQ API use is not included.

**Events** (rates file, credits each): classic answer 1, generative answer 2, agent action 5 (includes triggers, deep reasoning, computer use), tenant graph grounding 10, agent flow 0.13 per action (13 per 100), AI tools 0.1 / 1.5 / 10 per 1,000 tokens (basic / standard / premium), content processing 8 per page, reasoning 10 per 1,000 tokens, voice 10 per minute (higher tiers 35 and 75, verify). A grounded answer counts one generative answer plus one grounding event.

### Prices and exchange rate

1. The customer's price sheet (EA or MCA price list, CSP quote).
2. Swiss list prices (rates file): Microsoft 365 Copilot CHF 24.30, Copilot Business CHF 17.00, Microsoft 365 E7 CHF 85.92, Agent 365 CHF 12.10 per user and month, capacity pack CHF 162 per 25,000 credits; excluding VAT.
3. USD list prices x the documented billing exchange rate. The rates file's 0.81 CHF per USD is the ratio implied by Swiss list prices; a single rate across products is an approximation (products differ), MCA converts monthly and EA uses the agreement currency.

Every rate carries a source and a date. Stale (older than 90 days) or unverified
inputs may remain only as explicitly flagged draft gaps where allowed.
Labelling them "verify" does not pass F1, validate pricing or satisfy a
budget/purchase approval gate; obtain and record current verification first.

### Purchase options

| Option | Rule in the model |
|---|---|
| Pay-as-you-go | credits x USD 0.01 x CHF per USD; billed in arrears; draws down MACC |
| Capacity packs | ceil(monthly credits / 25,000) packs at the Swiss list price; no rollover; service denial when exhausted |
| Copilot Credit P3 | best of nine tiers (300,000 credits 5% ... 300 million 20%) plus pay-as-you-go above the tier; one year, no refunds; below the smallest tier the unused commitment is lost |
| Microsoft Agent P3 | best of three tiers (USD 20,000 5%, 100,000 10%, 500,000 15%) over credits plus eligible Foundry usage |

The comparison basis is credits plus Agent-P3-eligible Azure usage. A lowest
modelled option is provisional, not commitment advice. Independently verify
prices, terms and assumptions; the real budget owner decides.

### Unit economics and scenarios

Cost per session and per successful outcome (FinOps for AI), compared with the human cost per task in the value case. Credit scenarios override named variables (licensed share, grounding share, usage) to show what moves the credit cost; typical lessons: people often cost more than credits; tenant graph grounding drives most credits; the licence mix moves the credit cost by about two thirds; purchase options matter at scale.

### Gates

- **F1** cost model complete: every MVP agent has usage drivers and current
  verified rates no older than 90 days. Stale/unverified draft gaps do not pass;
  F1 itself is not validated pricing or budget/purchase approval.
- **F2** guardrails designed, each with an owner (references/guardrails.md).
- **F3** is the historical proposed operate-loop gate: actuals flowing and variance
  within an agreed threshold. The old release-1.4 target is not delivery evidence.

### Data contract (abridged)

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

### Sources

Rates file `sources` (B1 billing rates, B2 licensing guide, B3 credits guide, B4 Copilot Credit P3, B5 Agent P3, B6 Swiss price pages, B8 credit estimator, B9 Azure pricing calculator); FinOps Framework and FinOps for AI (finops.org); FOCUS specification (focus.finops.org).
