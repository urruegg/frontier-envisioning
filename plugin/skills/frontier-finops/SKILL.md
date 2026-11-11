---
name: frontier-finops
description: |
  Optional Preview cost model for Frontier agents in CHF: credits, licences, Azure, people,
  unit costs, purchase comparisons and guardrails. Load to explain limitations; obtain actual
  current-scenario acknowledgement before any cost operation, recommendation or figure.
  Use for "what will the agents cost per month", "Copilot Credits for <customer>",
  "cost per agent in CHF" or "design the FinOps guardrails".
  Do NOT use for value/ROI alone (frontier-value-case), blueprint HTML (frontier-blueprint),
  or Azure costs unrelated to agents (Azure Cost Management).
license: MIT
metadata:
  category: productivity
  icon: Money
  version: "1.9.1"
  plugin: frontier-envisioning
  maturity: preview
  optional: true
  requires_preview_ack: true
---

# FinOps for Frontier agents

Optional Preview planning model per agent in CHF: credits, licences, Azure,
people and one-time build. Comparisons are provisional, not commitment advice.
The seven other skills are GA product wrappers and work without FinOps.

## Awareness gate — before any cost operation or figure

Show this notice in full:

> Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.

Ask for actual confirmation for the current scenario, scope, model, rates and
grounding. Loading this skill to explain limitations is allowed; seeding,
calculating, applying, cost recommendations and displaying figures must wait.
Do not infer awareness from installation, old JSON/notes, a request to calculate,
a GA claim or a previous run. A decline skips this optional subflow and records
the gap without blocking the core or passing budget/readiness.

Every top-level cost CLI invocation needs `--acknowledge-finops-preview`.
Operational Python APIs use keyword-only `acknowledge_finops_preview=False`;
set it true only after the actual confirmation. A wrapper forwards it only
inside one requested action chain. New invocation, scope, model, rates or
grounding means renewed acknowledgement. Metadata is a technical
caller/current-invocation record, not independent human approval. Pure
arithmetic helpers are not permission to operate a model.

## Quick Start

```
User: "What will the Caldova agents cost per month?"
1. Show the full notice above; obtain actual current-scenario confirmation, or skip with the cost gap stated
2. Find the blueprint, ordinary value inputs and any existing model; after confirmation: python scripts/seed_finops.py --blueprint blueprint.normalized.json --value value.json --out working/frontier/<slug>/finops.json --acknowledge-finops-preview
3. Review harness, audience, coverage and events per agent with the user; fill run and build effort
4. Renew confirmation for this invocation: python scripts/finops_calc.py --finops finops.json --value value.json --acknowledge-finops-preview
5. Renew confirmation for the wrapper chain: python ../frontier-blueprint/scripts/build_with_identity.py --data blueprint.json --finops finops.json --value value.json --out-dir working/frontier/<slug> --acknowledge-finops-preview
6. Review permitted outputs; retain the full Preview notice, provenance and assumptions in the HTML, reply and exports; independently verify prices and terms
```

The default Caldova demo does not invoke FinOps. An explicitly requested Preview
demo may use `examples/caldova-finops.json` after the same awareness gate.
Worked examples and legacy/imported FinOps remain Preview, not validated pricing.

### Standalone apply (after renewed confirmation)

```text
python scripts/apply_finops.py --blueprint <data> --finops <model> [--value <value>] [--rates <rates>] [--today YYYY-MM-DD] --out <out> --acknowledge-finops-preview
```

Brackets denote optional arguments. Calculate freshly before applying if the
cached results, model, value inputs or rates do not match; an acknowledgement
flag does not repair stale fingerprints or validate prices.

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
Apply the awareness gate first. Then read the normalized blueprint, value inputs
and existing model. Keep legacy originals unchanged. If cost work is declined,
return to clean core/ordinary non-FinOps inputs, not cached Preview-derived value.
Do not remove provenance or relabel legacy costs GA. There is no automatic old-
field removal or cleansing flag. Requested FinOps with the module missing is an
explicit error; without a request, the core continues without it.

### Step 2: Prices and licence posture
Price order: the customer's own price sheet first, Swiss list prices second, USD list prices times the documented billing exchange rate third. Find the price sheet, licence counts and billing agreement (EA, MCA, CSP; MACC; existing packs or P3) with the `SearchM365` tool and read files with `ReadFileContent`. Rates come from `rates/rates-2026-11.json`, each with source and date. Obtain current verification for stale or unverified rates (deep research or the browser; the sandbox has no internet) before F1 can pass. Where allowed, retain such inputs only as explicitly flagged draft gaps; a "verify" label is not verification. Never treat list prices as customer prices.

### Step 3: Usage model per agent
Seed with `seed_finops.py`, then review with the user and the agent maker: harness (standard, Copilot Chat, Foundry, GitHub), audience (employee or external), coverage (employee-facing standard and Copilot Chat use by licensed Microsoft 365 Copilot users is included within fair use; workflow-started runs, the GitHub harness and external audiences are billed), events per session (generative answers, tenant graph grounding, agent actions, flow actions, AI tools, content pages, voice), Azure lines, licences, run and build effort. Details: [references/finops-for-agents.md](references/finops-for-agents.md).

### Step 4: Calculate (gate F1)
`finops_calc.py` writes the results: cost lines per agent and month, unit costs, purchase options, credit scenarios, guardrails and lessons. Gate F1: every MVP agent has usage drivers and current verified rates no older than 90 days. Stale/unverified draft inputs do not pass F1 merely by being labelled. F1 is model completeness, not validated pricing, budget approval or a purchase gate.

### Step 5: Show it in the blueprint
Use `build_with_identity.py --data blueprint.json --out-dir working/frontier/<slug> --finops finops.json --value value.json --acknowledge-finops-preview` after
current confirmation. The wrapper calculates/applies on copies in one chain.
The purchase comparison stays provisional; independently verify prices, terms
and assumptions with the accountable budget owner before decisions.

Browser viewing requires a fresh explicit acknowledgement for that document,
independent of script acknowledgement. It is transient, not localStorage:
reload resets it and the warning persists after acknowledgement. Flat/nested
cost results and linked assumptions, cost-derived ROI/NPV, unit costs and PRD
summaries are gated. Ordinary non-FinOps value remains available. Private
components, rankings and outcomes are withheld, not zero; never recover
`internal_notes`. Viewer acknowledgement is not encryption or access control.

FinOps is in Build beside Roadmap and Plan; open cost assumptions also appear
in Workshops > Risks. WIP/readiness and owner/status metadata do not authorise
a purchase or deployment. Plan CSV is handover data requiring destination
mapping, not live integration or native import certification.

### Step 6: Guardrails (gate F2)
Per agent: monthly credit limit with headroom, alerts and hard stop (Power Platform admin center); environment allocations; Microsoft 365 spending policies; Azure budgets and anomaly alerts; the tagging standard keyed to the agent identity; a monthly plan-versus-actual review. Hand them to **frontier-solution-design** as FinOps NFRs and a purchase-model ADR. Gate F2: guardrails designed, each with an owner. Rules: [references/guardrails.md](references/guardrails.md).

### Step 7: After the workshop
Cost assumptions are confirmed, adjusted or rejected on the FinOps page.
After renewed scenario confirmation, use
`python ../frontier-value-case/scripts/merge_value_feedback.py --value value.json --finops finops.json --feedback <feedback.json> --date <YYYY-MM-DD> --acknowledge-finops-preview`.
Recalculate freshly before applying changed models. Workshop verdicts do not
replace a new invocation's acknowledgement or budget approval.

## Output format (reply)

- Start with the full Preview notice; include model/rate/source versions, dates,
  scenario and assumptions wherever costs or derived value travel (JSON, HTML,
  replies, PRD/design, downloads and comparisons).
- A table of the cost per agent and month (credits, licences, Azure, people) and the one-time build, in CHF.
- Unit cost per session and per outcome where permitted; provisional purchase
  comparisons, not a recommendation to commit.
- The two assumptions that move the cost most, with owners; the rates date and any "verify".
- File names of the HTML and `finops.json`.

## Guardrails

- Always show the usage model and the cost assumptions to the user before calculating, and the customer version before sharing.
- Never quote list prices as customer prices; always show the rates date and flag rates older than 90 days.
- Credits are not money until converted under the documented exchange-rate policy.
- Purchase comparisons are not commitment advice. Independently verify baseline,
  prices, refund/commitment terms and assumptions with the accountable budget owner.
- Always show people and build costs next to the credits; a credit-only view misleads.
- Customer versions never contain discounts, internal pricing guidance or internal milestone helpers.
- Preserve content provenance in risk/PRD projections: removing an internal
  source ID alone is not sanitisation. Customer export is not external/IP clearance.
- Mark preview features (agent dashboards, cost APIs) as preview with the date checked.

## Failure handling

- If `finops_calc.py` lists `missing` assumptions: collect them (volumes, effort) before showing costs.
- If an event name is unknown: use the names in the rates file; never invent a credit rate.
- If a rate is older than 90 days or unverified: obtain current verification and
  record its source/date before passing F1. Where draft use is allowed, flag the
  unresolved gap explicitly; the label does not pass F1, validate a price or
  satisfy any budget/purchase approval gate.
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
