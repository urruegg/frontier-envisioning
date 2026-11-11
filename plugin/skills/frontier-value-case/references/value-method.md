# Value method (frontier-value/1.0)

The value case answers one question in CHF: what is the MVP worth, how sure are we, and which assumptions must the customer confirm? It follows Microsoft's guidance on measuring the value of AI agents (four value drivers), the Cloud Adoption Framework business plan for AI agents (scoring, KPI gates, ROI and NPV) and the Innovation Hub's value discipline.

## Discipline (house rules)

1. **Cash, capacity and risk stay apart.** Released working time is capacity, not cash, until the customer names a spend that stops (an outsourced service, overtime, a hire not made). Resilience and compliance gains are risk reduction, never a recurring saving.
2. **Count each benefit once** and test net effort: hours removed minus new review, standby and run effort.
3. **Baseline before agents.** Capture cycle time, cost, error rate or hours before the agents touch the process; avoid the time-savings trap.
4. **Realisation factor.** Released hours are multiplied by a recapture share: default 50% (Forrester's convention), sensitivity 25-75%.
5. **Benchmarks are priors, not facts.** Microsoft-commissioned studies (Forrester, IDC) of US composite firms may set ranges in hypothesis mode; they never replace customer numbers and are always labelled.
6. **No ROI claims beyond the data.** Present ranges, the budget view next to the economic view, and the assumptions the case depends on.
7. **Aggregate, never individual.** Value per process, team or agent; never per employee.

## Value tree

Per use case, levers with a driver and a category:

| Driver | Typical lever | Category |
|---|---|---|
| Efficiency | Time released: volume x (minutes before - minutes after) / 60 x loaded rate x realisation | capacity |
| Efficiency (cash) | The part of that time tied to a spend that stops (overtime, external service) | cash |
| Quality | Change in error rate x volume x cost per error | capacity or cash |
| Revenue | Change in conversion or price x volume x margin x attribution | revenue (counted with cash) |
| Strategic and risk | Change in probability x impact (expected loss avoided) | risk (separate) |

A lever with `"booked": false` is shown, never counted (for example employee search time without a named use). A lever that depends on a rejected assumption is left out until a new value is agreed. When part of a time saving becomes cash, take that share out of the capacity lever (count once).

## Assumption register

`ASS-001`...: statement, unit (`share` for 0-1 fractions), low, base, high, source type (customer, measured, benchmark, hypothesis), confidence (high, medium, low), `src` (evidence ids), owner (a role), question (what the owner is asked in the workshop), status (open, confirmed, adjusted, rejected), scope (value or finops). Low and high are the plausible numeric range; the scripts work out which end weakens the case. Empty values mean "to collect"; the use case is then listed under `inputs_needed` and not calculated.

## Calculation

Ordinary value work is independent of FinOps. Use sourced ordinary cost
assumptions, with ranges and accountable owners; if costs are missing, report
the budget gap and withhold unsupported ROI/payback, even if a formula emits
a number. Missing evidence is not zero or budget/readiness approval.

For requested Preview costs or Preview-derived value, first show the full
[FinOps notice](../../frontier-finops/SKILL.md#awareness-gate--before-any-cost-operation-or-figure)
and obtain actual current-scenario confirmation. Each operational value calc/
apply/feedback invocation needs `--acknowledge-finops-preview` for these inputs;
ordinary value-only use does not. Renew for new invocation/scope/model/rates/
grounding; wrapper forwarding is one chain only. Old JSON/notes/installation/
GA claims are not consent. Technical caller metadata is not human approval.
Recalculate before applying after a cache/model/rates mismatch.

On decline or absent unrequested FinOps, keep the original unchanged and use
clean core and ordinary non-FinOps value inputs, not the cached Preview model.
Requested-but-missing FinOps is an explicit error; no automatic cleansing is
promised. Legacy/imported FinOps remains Preview. Carry the full warning,
assumptions and scenario/model/rate/source provenance into derived ROI/NPV,
unit costs, comparisons, PRD/design, replies and exports. Browser acknowledgement
is independent, transient and document-local, resets on reload, never
localStorage consent; the warning persists. Gate flat/nested results and linked
assumptions while retaining ordinary own value. Private components/rankings/
outcomes are withheld, not zero; never recover `internal_notes`. Viewer
acknowledgement is not encryption or access control.

- Monthly simulation over the horizon (default 3 years); adoption ramp per quarter (`adoption_ramp`, last value repeats). Variable costs (credits, Azure) follow the ramp; licences and people are fixed.
- **Budget view** = cash + revenue. **Economic view** = budget + realised capacity. **Risk** = separate.
- **NPV** = PV(economic value) - PV(cost); annual discounting at the customer's rate (default 8%), build cost at year 0. **ROI** = NPV / PV(cost). **Payback** = first month with cumulative net >= 0, undiscounted, interpolated.
- **Break-even**: the value of one assumption (`break_even_on`, else the most sensitive) at which the steady-state monthly value equals the monthly run cost; "positive across the whole range" when it never crosses.
- **Sensitivity**: each assumption at its low and high, the others at base, costs held at base; ranked by the NPV swing. The ten largest become the workshop questions.
- **Range per year**: the individual effects combined by root-sum-square (not every assumption hits its extreme together). The corners (every assumption at its weak or strong end) are kept as `weak` and `strong` in the results.
- Optional risk adjustment by confidence (decision for the method sponsor): high 0-5%, medium 10-15%, low 20-30%.

## Gates

- **V1** value hypothesis complete: every MVP use case has a value tree; every number has a source or an assumption label; sensitivity done.
- **V2** validated: the five most sensitive assumptions confirmed or adjusted by named owners (workshop verdicts merged).
- **V3** baseline measured before go-live, with the measurement method agreed.

## Workshop clarification

Before: the customer version shows ranges and the top ten assumptions with the role expected to answer each (finance, process owner, IT). In the room (45 minutes after the MVP choice): walk the value tree of each MVP; confirm, adjust (type the agreed value) or reject assumptions live on the Use cases page; agree baseline owners. After: export the notes from Discovery; `merge_value_feedback.py` applies the verdicts, writes the changelog and bumps the version; frontier-context-discovery adds numbers from the transcript as evidence; rebuild to recalculate.

## Documents

**Business value assessment** (docx skill): 1 Executive summary (supported ranges, NPV/payback, budget view, gaps) · 2 Scope and baseline · 3 Value tree · 4 Assumptions with owners/status · 5 Ordinary costs, or explicitly acknowledged Preview costs with full notice/provenance · 6 Scenarios and sensitivity · 7 Risks and measurement · 8 Decisions and next steps · Sources.

**Excel model** (xlsx skill, live formulas, inputs colour-coded): Inputs · Assumptions · Value · Cost (ordinary inputs by default; Preview warning/provenance if used) · Scenarios · Sensitivity · Summary. Independently verify purchase prices, terms and assumptions; comparisons are not commitment advice.

## Data contract (abridged)

```json
{"schema": "frontier-value/1.0", "currency": "CHF", "horizon_years": 3, "discount_rate": 0.08, "realisation_default": 0.5,
 "assumptions": [{"id": "ASS-001", "statement": "", "unit": "", "low": 0, "base": 0, "high": 0, "source_type": "hypothesis",
                  "confidence": "low", "src": ["E05"], "owner": "", "question": "", "status": "open", "scope": "value"}],
 "use_cases": [{"id": "UC09", "name": "", "agents": ["D3-A05"], "adoption_ramp": [0.1, 0.4, 0.8, 0.9],
                "vars": {"jobs": "ASS-001", "hours": "jobs * (before - after) / 60"},
                "levers": [{"id": "L1", "name": "", "driver": "efficiency", "category": "capacity", "formula": "hours * rate * realisation"}],
                "break_even_on": "ASS-006"}]}
```

Formulas are arithmetic over named variables (numbers, + - * / **, parentheses, min, max, ceil, floor); nothing is executed.

## Sources

- Measure the ROI and business value of AI agents (Microsoft Learn): https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/agent-business-value-overview
- Agents hub: monitor, measure and report value: https://learn.microsoft.com/en-us/agents/center-of-excellence/measure-report-value
- Cloud Adoption Framework, business plan for AI agents: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/business-strategy-plan
- Forrester Total Economic Impact studies (Microsoft-commissioned): use as priors only, labelled.
