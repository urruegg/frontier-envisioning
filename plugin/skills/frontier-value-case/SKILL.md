---
name: frontier-value-case
description: |
  Builds and refines the business value case in CHF for a customer's Frontier agents: a value
  tree per use case (efficiency, quality, revenue, strategic; cash, capacity or risk), an
  assumption register with owners and evidence, NPV, ROI, payback, break-even, sensitivity and
  the assumptions to clarify in the workshop, shown in the blueprint's use cases and matrix.
  Use when asked to "build the value case for <customer>", "ROI in CHF for the MVP agents",
  "what is the MVP worth",
  "which assumptions should we clarify in the workshop" or "update the value case with the
  workshop feedback". Do NOT use for agent costs or Copilot Credits (use frontier-finops), for
  the blueprint itself (use frontier-blueprint) or for a CRM sales-deal business case (use the
  sales skills).
license: MIT
metadata:
  category: productivity
  icon: DataTrending
  version: "1.9.1"
  plugin: frontier-envisioning
---

# Business value case

Turns the blueprint's use cases into a CFO-credible value case in CHF. Every number is either evidence (a customer statement, a measurement) or a labelled assumption with an owner, a range and a question for the workshop. A deterministic script calculates; the blueprint shows the value in the use cases and the matrix, and lets the workshop confirm, adjust or reject each assumption live. The verdicts come back as a feedback file and are merged into the next version.

## Quick Start

```
User: "Build the value case for Caldova"
1. Find the blueprint (normalized JSON), the context pack and an existing value.json in the engagement folder
2. python scripts/seed_value.py --blueprint blueprint.normalized.json --out working/frontier/<slug>/value.json
3. Fill the value tree and the assumptions from evidence (volumes, minutes, rates, error costs); label the rest
4. frontier-finops: the cost model for the same agents (finops.json)
5. python ../frontier-blueprint/scripts/build_with_identity.py --data blueprint.json --value value.json --finops finops.json --out-dir working/frontier/<slug> ...
6. Publish the HTML; reply with value per year (range), NPV, payback, the budget view and the top assumptions with owners
```

Demo: "Build the Frontier blueprint demo for Caldova" (frontier-blueprint) uses `examples/caldova-value.json`. `examples/reference-hr-assistant.value.json` is the method's worked example; the self-test checks that the scripts reproduce its published results.

## When to Use

- The blueprint has MVP candidates and the sponsor asks what they are worth.
- A workshop must confirm volumes, handling times, rates and the realisation factor.
- Workshop feedback with assumption verdicts must be merged, or a transcript added numbers.
- A business value assessment document or a value slide is needed from validated numbers.

## When NOT to Use

- Running the whole engagement end to end: use frontier-envisioning instead.
- Agent names, colours and icons: use frontier-agent-identity instead.
- Costs, Copilot Credits, licences, purchase options or guardrails: use frontier-finops instead.
- The blueprint HTML, journeys and agents: use frontier-blueprint instead.
- Gathering context or analysing transcripts: use frontier-context-discovery instead.
- A business case for a CRM sales deal: use the sales business case skill instead.
- PRD and solution design: use frontier-solution-design instead.

## Workflow

### Step 1: Locate the engagement
Read `engagement.json`, the normalized blueprint and the context pack from the engagement folder (OneDrive `Documents/Cowork/frontier-envisioning/<slug>/`, then `input/`). Reuse an existing `value.json`; never start a second one for the same customer.

### Step 2: Evidence first
Look for numbers before assuming them: volumes, handling times, loaded rates, error costs, spends that could stop, current tool and licence costs. Search with the `SearchM365` tool (meetings, transcripts, mail, files) and read documents with `ReadFileContent`; run **frontier-context-discovery** on new transcripts. Fact mode uses customer numbers; hypothesis mode uses labelled defaults; mixed is normal. Record evidence ids in `src`.

### Step 3: Write the value tree and the assumption register
Seed with `seed_value.py` (volume and minutes stay empty until evidence or the customer provides them), then write each lever: driver (efficiency, quality, revenue, strategic), category (cash, capacity, risk, revenue) and formula over named variables. Each assumption has a statement, unit, low, base, high, source type, confidence, owner, question and status. Rules: [references/value-method.md](references/value-method.md). Show the levers and the assumptions to the user before calculating.

### Step 4: Costs from frontier-finops
The run cost of each use case comes from the FinOps results of its agents. Build or update `finops.json` with **frontier-finops** first.

### Step 5: Calculate (gate V1)
`build_with_identity.py --value --finops` runs `finops_calc.py`, `value_calc.py` and the apply scripts on copies and renders the blueprint. Gate V1: every MVP use case has a value tree, every number has a source or an assumption label, sensitivity done. Check `inputs_needed` and fill the gaps.

### Step 6: Prepare the workshop
The Use cases page sizes the matrix bubbles by value (dashed while a hypothesis) and lists the assumptions ranked by their effect on the NPV, each with its owner and question. Put the top ten on the agenda ("Value and cost of the MVP agents", 45 minutes after the MVP choice) and build the customer version before anything leaves Microsoft.

Use cases and the MVP PRD now sit in Vision; the shared PRD model includes the
value of the selected use cases. Workshops > Risks also surfaces open value/cost
assumptions. Keep assumption evidence and owners; a scope verdict or computed
Plan readiness is not validation of value or permission to build.

### Step 7: Merge the workshop (gate V2)
`python scripts/merge_value_feedback.py --value value.json --finops finops.json --feedback <customer>-workshop-feedback.json --date <YYYY-MM-DD>` applies confirm, adjust (with the agreed value) and reject; it writes a changelog and bumps the version. Rebuild to recalculate. Gate V2: the five most sensitive assumptions are confirmed or adjusted by their owners; then set `status` to `validated`.

### Step 8: Deliver
A business value assessment document (docx skill, structure in the method reference) and, when asked, an Excel model with live formulas (xlsx skill, sheet layout in the method reference). Gate V3: the baseline is measured before go-live, with the method agreed.

## Output format (reply)

- A table per use case: value per year (range), NPV, payback, the budget view (cash only) next to the economic view; risk reduction separately.
- The break-even sentence and the payback.
- The top five assumptions with owner and question; inputs still to collect.
- File names of the HTML and of `value.json`.

## Guardrails

- Never fabricate: a number without evidence is an assumption with a range, an owner and a question.
- Never book capacity as cash: released time is capacity until the customer names a spend that stops; count each benefit once.
- Always keep risk reduction out of the budget view, and label benchmarks "Microsoft-commissioned, US composite".
- Never measure value per employee; aggregate per process, team or agent.
- Always show the value tree and the assumptions to the user before calculating, and the customer version before sharing.
- No ROI claims beyond the data: present ranges and the budget view next to the economic view.
- Customer generation must exclude internal-derived value/risk/PRD content,
  not merely remove its source IDs. Customer export is not external/IP clearance.

## Failure handling

- If `value_calc.py` reports `inputs_needed`: collect those assumptions (evidence or customer) before quoting numbers.
- If an assumption id is missing from the register: add it or fix the variable; never invent a value.
- If the feedback file belongs to another blueprint or names unknown ids: report them and ask which version was shown.
- If no FinOps results are available: the costs are zero and flagged; build the cost model before presenting ROI.
- If the sponsor asks for a single number: give the base case with its range and the two assumptions it depends on most.

## Files

- `scripts/seed_value.py` — value case seed from the blueprint (MVP use cases)
- `scripts/value_calc.py` — calculation: views, NPV, ROI, payback, break-even, sensitivity, ranges, questions
- `scripts/apply_value.py` — business value and assumption register into the blueprint JSON
- `scripts/merge_value_feedback.py` — workshop verdicts into value.json and finops.json
- `scripts/fv_expr.py` — safe formulas (shared with frontier-finops)
- `references/value-method.md` — discipline, formulas, defaults, ranges, gates, documents
- `examples/caldova-value.json` — Caldova MVP value case (fictitious); `examples/reference-hr-assistant.value.json` — the method's worked example
