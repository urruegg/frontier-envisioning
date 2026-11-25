---
name: frontier-finops
description: |
  Optional Preview agent costs and versioned 12-month low/expected/high baselines in
  CHF, EUR or USD: demand, rates, unit costs, frozen-version review and safe exports.
  Load to explain limitations; obtain actual current-scenario acknowledgement before
  any cost operation, recommendation or figure. Use for "what will the agents cost
  per month", "baseline for D3-A05", "Copilot Credits for <customer>", "cost per
  agent in CHF" or "design the FinOps guardrails".
  Do NOT use for value/ROI alone (frontier-value-case), blueprint HTML
  (frontier-blueprint), or Azure costs unrelated to agents (Azure Cost Management).
license: MIT
metadata:
  category: productivity
  icon: Money
  version: "1.11.0"
  plugin: frontier-envisioning
  maturity: preview
  optional: true
  requires_preview_ack: true
---

# FinOps for Frontier agents

*AI-assisted procedure maintenance, 13 November 2026; original authorship retained.*

**Release build 1.10.0.** Build metadata is not publication evidence.
Optional Preview planning costs:
credits, licences, models, tools, infrastructure, people and one-time build.
For a requested new baseline, use `frontier-finops-baseline/1.0` below.
The legacy CHF model remains available only as an explicit separate path.
Comparisons are provisional, not commitment advice. There are still eight
skills; the seven non-FinOps GA wrappers work without FinOps.

## Awareness gate — before any cost operation or figure

Show this notice in full:

> Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.

Ask for actual confirmation for the current scenario, scope, model, rates and
grounding. Loading this skill to explain limitations is allowed; seed, migrate,
calculate, freeze, record-review, apply, export, cost recommendations and
displaying figures must wait.
Do not infer awareness from installation, old JSON/notes, a request to calculate,
a saved approval, a GA claim, yesterday's acknowledgement or a previous run.
A decline skips this optional subflow: continue draft workshops and clean core,
ordinary value and identity work with named financial gaps. Do not assume zero
costs, validated cost-derived ROI or financial/build-handover readiness.

Every top-level cost CLI invocation needs `--acknowledge-finops-preview`.
Operational Python APIs use keyword-only `acknowledge_finops_preview=False`;
set it true only after the actual confirmation. A wrapper forwards it only
inside one requested action chain. New invocation, scope, model, rates or
grounding means renewed acknowledgement. Metadata is a technical
caller/current-invocation record, not independent human approval. Pure
arithmetic helpers are not permission to operate a model.

## Quick Start — requested versioned baseline

Use the offline successor for an existing agent, for example `D3-A05`.
Commands below run from this skill directory. Replace `YYYY-MM-DD` with the
explicit evaluation date and choose unused output paths. These are separate
actions, **not a batch**: obtain current confirmation before each invocation;
the flag records a technical assertion only.

1. After the awareness gate, seed from the engagement Blueprint:

   ```text
   python scripts/agent_finops.py seed --blueprint blueprint.normalized.json --agent-id D3-A05 --out working/baseline/draft.json --as-of YYYY-MM-DD --acknowledge-finops-preview
   ```

2. Complete a new working file, `working/baseline/draft-v1.json`, with the user
   and accountable owners. Supply the profile, scope, twelve monthly demand
   values for each low/expected/high scenario, another meaningful dependency
   driver, decimal-string quantities/rates, units, denominators, currency,
   applicable rate/FX evidence and sharing context. Seeded unknowns are not
   defaults. See [baseline inputs and draft rules](references/finops-for-agents.md#versioned-baseline--new-work).

3. After renewed confirmation, calculate and inspect all gaps and contribution
   states; a successful command is not financial readiness:

   ```text
   python scripts/agent_finops.py calculate --baseline working/baseline/draft-v1.json --out working/baseline/calculated-v1.json --as-of YYYY-MM-DD --acknowledge-finops-preview
   ```

4. After renewed confirmation, freeze the exact calculated revision:

   ```text
   python scripts/agent_finops.py freeze --baseline working/baseline/calculated-v1.json --out-dir working/baseline/snapshots --as-of YYYY-MM-DD --acknowledge-finops-preview
   ```

   This creates `<baseline-id>.v<version>.json`. Use that actual file as
   `<snapshot.json>` below. Preserve its `target.baseline_id`, `version` and
   `material_hash`; review must name that exact target.

5. Obtain external finance-owner review, or evidenced delegation, before
   recording a decision. Prepare `external-review.json` from actual evidence
   using the [review fields and authority limits](references/agent-finops-baseline.md#frozen-snapshot-and-external-review-shapes),
   not a fabricated approval or workshop verdict. After renewed confirmation:

   ```text
   python scripts/agent_finops.py record-review --baseline <snapshot.json> --review external-review.json --out-dir working/baseline/reviews --as-of YYYY-MM-DD --acknowledge-finops-preview
   ```

   The created `<baseline-id>.v<version>.<review-id>.json` is
   `<recorded-review.json>` below. Local files/hashes are not authenticated or
   tamper-proof archival storage. Material edits need a new version and review.

6. After renewed confirmation for **each** action, apply or export the same
   target and recorded review:

   ```text
   python scripts/agent_finops.py apply --blueprint blueprint.normalized.json --baseline <snapshot.json> --review <recorded-review.json> --out working/baseline/applied.json --audience internal --as-of YYYY-MM-DD --acknowledge-finops-preview
   python scripts/agent_finops.py export --baseline <snapshot.json> --review <recorded-review.json> --out-dir working/baseline/reports-internal --audience internal --as-of YYYY-MM-DD --acknowledge-finops-preview
   ```

   Export creates `report.json` and `report.md` from one audience-projected
   report. For customer output use `--audience customer` and the matching
   `--customer-scope <scope>` for customer-specific inputs, with new output
   paths. Scope/classification is not clearance or access control. Drafts may
   be applied/exported without `--review`; they do not become approved.

`apply` accepts repeated `--baseline` and `--review`; `export` accepts repeated
`--review`. Conflicting active revisions/reviews refuse, with no silent winner.
For the existing build wrapper, supply authoritative sources, not an applied
view, report or cached DTO:

```text
python ../frontier-blueprint/scripts/build_with_identity.py --data blueprint.json --agent-finops <snapshot.json> --agent-finops-review <recorded-review.json> --as-of YYYY-MM-DD --audience internal --out-dir working/baseline/blueprint --acknowledge-finops-preview
```

Repeat `--agent-finops` and `--agent-finops-review` for additional explicit
inputs; add matching `--customer-scope` for customer-specific output. Do not
combine successor sources with legacy `--finops` or embedded legacy costs.

**Build handover is strict.** Draft/core preparation can continue with gaps;
financial handover needs a validated complete profile, meaningful twelve-month
scenarios, every in-scope cost driver priced with current applicable evidenced
rates/FX, explicit denominators, the frozen exact target, externally evidenced
owner/delegation review and current lineage/scope validation. Unpriced has no
conditional exception. Provisional or synthetic evidence cannot pass.
Even planning-ready evidence grants no budget, purchase, build or deployment
permission. See [handover guardrails](references/guardrails.md#strict-financial-build-handover).

### Explicit migration, never automatic conversion

After fresh awareness, choose migration instead of seed only for an explicitly
selected `frontier-finops/1.0` original:

```text
python scripts/agent_finops.py migrate --baseline legacy-finops.json --blueprint blueprint.normalized.json --agent-id D3-A05 --out working/baseline/migrated-draft.json --as-of YYYY-MM-DD --acknowledge-finops-preview
```

This preserves originals/provenance and creates a context-only draft where
numeric mapping is unproved. It inherits no approval, acknowledgement, licence
coverage or implicit legacy FX. Collect the new typed inputs before calculation.
Full schema, arithmetic, CLI and projection details:
[offline baseline contract](references/agent-finops-baseline.md).

## Legacy quick start — explicit `frontier-finops/1.0` only

Keep this backward-compatible path for existing legacy work; do not select it
automatically for a requested new baseline or treat its F1/F2 gates as the
successor's financial handover check.

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

- A new versioned twelve-month agent baseline, frozen review target or safe JSON/Markdown report is requested.
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

## Legacy workflow — not the successor handover gate

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
For successor data, consume the already projected `agent_finops` report only:
do not reconstruct private costs, totals, headers or hashes from raw sources
or fall back to legacy amounts. New baseline data alone does not make
independent ordinary value Preview; legacy-derived value remains Preview.

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
- Successor: low/expected/high monthly, annual, one-time and first-year
  estimates in the declared reporting currency, with verified/provisional
  contributions and explicit unavailable/withheld states; never zero-fill gaps.
- Legacy: a table of per-agent monthly costs (credits, licences, Azure, people)
  and one-time build costs in CHF, without inventing successor scenarios.
- Unit cost per session and per outcome where permitted; provisional purchase
  comparisons, not a recommendation to commit.
- The two assumptions that move the cost most, with owners; the rates date and any "verify".
- Actual output paths: baseline revision/snapshot and projected `report.json`/
  `report.md`, or legacy `finops.json` and HTML where actually produced.

## Guardrails

- Always show the usage model and the cost assumptions to the user before calculating, and the customer version before sharing.
- Never quote list prices as customer prices; retain the source and date. The
  legacy model flags rates older than 90 days; the successor uses declared
  freshness policies and evidenced FX, not the legacy list-price-ratio policy.
- Credits are not money until converted under the applicable documented pricing and exchange-rate policy.
- Purchase comparisons are not commitment advice. Independently verify baseline,
  prices, refund/commitment terms and assumptions with the accountable budget owner.
- Always show people and build costs next to the credits; a credit-only view misleads.
- Customer versions never contain discounts, internal pricing guidance or internal milestone helpers.
- Preserve content provenance in risk/PRD projections: removing an internal
  source ID alone is not sanitisation. Customer export is not external/IP clearance.
- Mark preview features (agent dashboards, cost APIs) as preview with the date checked.
- The [Caldova D3-A05 baseline](examples/caldova-agent-baseline.json) is invented.
  Its CHF 1 per 1,000 tokens is not a quote, current retail price or commercial
  verification. Synthetic markers always block real financial handover;
  never change example statuses to demonstrate fake real approval/readiness.

## Failure handling

- For the successor, retain validation/pricing/review gaps separately. Unknown
  quantities, rates or necessary FX leave full totals/dependent metrics
  unavailable; usable supplied stale/unverified prices may support explicitly
  **PROVISIONAL — pricing evidence incomplete** drafts only. See the
  [draft rules](references/finops-for-agents.md#versioned-baseline--new-work).
- A deadline, raw `approved` status, local notes or cached acknowledgement never
  replaces current awareness, evidence or exact-target external owner review.
- The remaining calculator/rates-file guidance here applies to legacy inputs:
- If `finops_calc.py` lists `missing` assumptions: collect them (volumes, effort) before showing costs.
- If an event name is unknown: use the names in the rates file; never invent a credit rate.
- If a rate is older than 90 days or unverified: obtain current verification and
  record its source/date before passing F1. Where draft use is allowed, flag the
  unresolved gap explicitly; the label does not pass F1, validate a price or
  satisfy any budget/purchase approval gate.
- If the licence posture is unknown: keep the licensed share as a low-confidence assumption with the workplace team as owner.
- If the customer bills in another currency: set `fx` to the billing rate with its source and date.

## Files

- `scripts/agent_finops.py` — successor seed, migrate, calculate, freeze, record-review, apply and JSON/Markdown export
- [references/agent-finops-baseline.md](references/agent-finops-baseline.md) — complete successor contract, exact CLI, review fields, rounding and projection limits
- [examples/caldova-agent-baseline.json](examples/caldova-agent-baseline.json) — synthetic D3-A05 baseline, never commercial pricing or real approval
- [references/baseline-sources.json](references/baseline-sources.json) — four public concept sources checked 12 November 2026; no rate quotes or implemented APIs
- `rates/rates-2026-11.json` — credits per event, pay-as-you-go, packs, P3 and Agent P3 tiers, Swiss list prices, FX ratio; each with source and date
- `scripts/seed_finops.py` — cost model seed from the blueprint and the value case
- `scripts/finops_calc.py` — cost lines, unit economics, purchase options, scenarios, guardrails, lessons
- `scripts/apply_finops.py` — the FinOps page data into the blueprint JSON
- `scripts/fv_expr.py` — safe formulas (shared with frontier-value-case)
- `references/finops-for-agents.md`, `references/guardrails.md`
- `examples/caldova-finops.json` — Caldova MVP agents (fictitious); `examples/reference-hr-assistant.finops.json` — the method's worked example
