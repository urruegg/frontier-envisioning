# Agent FinOps baseline implementation plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Written specification approved; this implementation plan awaits explicit approval |
| Scope | Test-first 1.10.0 internal candidate, not publication or live deployment |
| References | [Catalogue](README.md), [Parent #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Decisions #36](https://github.com/urruegg/frontier-envisioning/issues/36), [D1 #38](https://github.com/urruegg/frontier-envisioning/issues/38), [D2 #37](https://github.com/urruegg/frontier-envisioning/issues/37), [D3 #39](https://github.com/urruegg/frontier-envisioning/issues/39), [Idea](../ideas/2026-11-12-agent-finops-baseline.md), [Approved design](../specs/2026-11-12-agent-finops-baseline-design.md), [SPRINT-007](../sprints/SPRINT-007-agent-finops-baseline.md), [ADR-0028](../adr/0028-versioned-agent-finops-baselines.md) |

> **For agentic workers:** REQUIRED SUB-SKILL: use
> `subagent-driven-development` or `executing-plans`, according to the
> maintainer's explicit execution choice. Steps use checkbox tracking.

**Goal:** Deliver the approved offline baseline-first flow from Agent Canvas
to meaningful scenarios, evidenced financial handover and safe exports.

**Architecture:** Add a versioned successor inside the existing FinOps skill.
Reuse Preview/fingerprint/privacy primitives and existing wrapper/renderer
conventions; preserve the legacy model and ordinary value path. Python owns
calculations and review validation; HTML is an offline review/feedback surface.

**Tech Stack:** Python 3.11+ standard library, `unittest`, existing Node DOM
tests, Playwright and self-contained HTML/CSS/JavaScript. No new dependencies.

---

## Approval, ownership and execution boundary

The maintainer approved the written specification at
`2e3c0e79dc45c9ab06775def9f31cfb3bad7a8aa` with
`approve-written-spec` (D35-08). That permits this plan, **not implementation**.
Wait for explicit plan/readiness approval and the execution-mode choice.
Stop for material questions even with autopilot enabled.

Work in the already consented native worktree on `feat/35-finops-baselines`.
The primary checkout remains separate. Accountable human owner: `@urruegg`.
The bounded packages are estimated M; split an expanding package before work,
rather than quietly expand its scope or claim an invented schedule.

| Package | Real issue | Scope | Prerequisite |
|---|---|---|---|
| D1 | [#38](https://github.com/urruegg/frontier-envisioning/issues/38) | Contract, calculator, version/review records, projection and CLI | Plan/readiness approval; version preparation |
| D2 | [#37](https://github.com/urruegg/frontier-envisioning/issues/37) | Optional wrapper, customer normalisation, Canvas/Factory/FinOps and exports | D1 contract/tests reviewed |
| D3 | [#39](https://github.com/urruegg/frontier-envisioning/issues/39) | Version provenance, user docs, installed self-test, L1/L2 and distribution proof | Version preparation first; final proof after D1 and D2 |

If subagent-driven execution is selected, use bounded `frontier-builder`,
`frontier-renderer` and eligible `docs-agent` work, with review checkpoints.
Do not delegate protected actions or infer an independent human approval.
Do not run L1 and L2 concurrently against shared demo outputs.

## File ownership and stable interfaces

New files inside `plugin/skills/frontier-finops/`:

| File | One responsibility |
|---|---|
| `scripts/baseline_model.py` | Contract/type/reference validation, explicit gaps, decimal parsing, source freshness and material-input fingerprint |
| `scripts/baseline_calc.py` | Guarded deterministic calculation, typed rate/FX resolution, result receipts and integrity validation |
| `scripts/baseline_records.py` | Draft seed/migration, frozen versions, external review records and financial handover evaluation |
| `scripts/baseline_projection.py` | Audience/dependency projection and Markdown/JSON/Blueprint report shaping before serialisation |
| `scripts/agent_finops.py` | Thin `main(argv=None) -> int` CLI over those modules; error/acknowledgement boundary |
| `examples/caldova-agent-baseline.json` | One explicit synthetic agent with independently auditable arithmetic, never actual commercial pricing |
| `references/agent-finops-baseline.md` | Contract, CLI, rounding, migration, scope and human-review procedure |
| `references/baseline-sources.json` | Four dated public reference records from the design, not a price sheet or copied documentation |

Do not add a generic application framework, expression language, ninth skill
or live provider. Reuse `require_preview_ack`, `NOTICE`, `fingerprint`,
`is_private` and `inherit_restrictions` from `finops_preview.py`.
Do not call legacy `bind_calculation` with an unsupported kind: its non-FinOps
branch assumes value-case receipts. The new receipt uses the shared fingerprint
primitive with an explicitly owned baseline payload and output shape.

Public interfaces, all inside the modules above. In this table, `ack=False`
means the keyword-only argument `acknowledge_finops_preview=False`;
operational callers must supply actual boolean `True`, never cached consent.

| Module | Interface | Result |
|---|---|---|
| `baseline_model` | `validate_model(model, *, as_of, blueprint=None)` | Explicit gap records; malformed types/references raise `ValueError` |
| `baseline_model` | `material_payload(model)`; `model_fingerprint(model)` | Material-input object; shared canonical fingerprint |
| `baseline_calc` | `calculate(model, *, as_of, ack=False)` | Fresh document with results/receipt, input unchanged |
| `baseline_calc` | `validate_receipt(model, *, as_of, ack=False)` | Validated calculation lineage or explicit refusal |
| `baseline_records` | `seed(blueprint, agent_id, *, as_of, ack=False)` | Draft with explicit unknowns |
| `baseline_records` | `migrate(legacy, blueprint, agent_id, *, as_of, ack=False)` | New draft with source restrictions, no inherited approval |
| `baseline_records` | `freeze(model, out_dir, *, as_of, ack=False)` | Exclusive versioned snapshot path |
| `baseline_records` | `record_review(snapshot, review, out_dir, *, as_of, ack=False)` | Exclusive external-review record path |
| `baseline_records` | `handover(snapshot, reviews, *, as_of, ack=False)` | Dated planning-readiness evidence and gaps |
| `baseline_projection` | `project(model, reviews=(), *, as_of, audience, customer_scope=None, ack=False)` | Safely projected report, never a new authoritative baseline |
| `baseline_projection` | `render_markdown(report)` | Markdown from the projected report only |
| `agent_finops` | `main(argv=None)` | Integer exit status, bounded JSON summary/stderr |

These are interface contracts, not production stubs. The tasks below define
their behaviour, examples and checks. Keep arithmetic helpers private; do not
restructure unrelated legacy modules.

### Input/output contract to establish in Task 1

Use schema `frontier-finops-baseline/1.0`. The document has `mode`
(`planning` or `synthetic`), profile, baseline, rates, FX and source records,
plus explicit sharing metadata. New monetary/quantity inputs use decimal
strings or explicit `null` gaps; versions/counts are integers, not booleans.

- Profile: `agent_id`, business/technical/finance owners, outcome definition,
  measurement plan, guardrails and customer scope where applicable.
- Baseline: ID/version, `as_of`, `start_month`, currency, explicit
  annualisation, scope, assumptions/exclusions/risks/confidence, three
  `scenarios` and `lines`. Source references are resolved, not followed.
- Scenario: ID `low|expected|high`, twelve `monthly_runs`, success share,
  outcomes per success and explicitly sourced driver values.
- Line: stable ID/cost-driver ID/category/service/meter, frequency
  `monthly|one-time`, quantity mode `per-run|fixed`, driver ID, quantity unit,
  rate ID and optional evidenced allocation policy.
- Rate: decimal amount, currency, unit/pricing block, effective dates,
  source ID, verification and declared freshness policy. FX additionally
  specifies from/to, date and method. Never use an implied list-price ratio.
- Source: ID/type, title, URL or opaque evidence reference, supported claim,
  validation date/status and sharing class. Synthetic evidence is explicit.

Results contain `scenarios` keyed by ID, monthly records, annual recurring,
one-time and first-year summaries, unit metrics, driver coverage and gaps.
Every money/metric carries `amount` (decimal string or `null`), currency where
relevant, status and reason. Unit metrics identify period/cost basis.
Complete monetary summaries round to cents with `ROUND_HALF_UP` at the
documented final aggregation boundary; unit metrics use six decimal places.
Retain supplied rate precision in calculations and explain rounding differences.

`material_payload` excludes only the owned root output fields `results`,
`finops_preview`, `review_records` and `handover`. It retains all authored
inputs and nested keys, including names such as `maturity`, classifications,
source/rate records and scenario drivers. Receipts bind that payload, dated
calculation context and calculated results. Projection is derivative output,
not a new authoritative baseline that can be imported as approval.

## Environment for commands

Run from the worktree. In each fresh PowerShell process:

```powershell
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
$env:PYTHONUTF8='1'
$env:PATH='C:\Users\urruegg\source\urruegg_microsoft\frontier-envisioning\.venv\Scripts;' + $env:PATH
$env:PLAYWRIGHT_BROWSERS_PATH='C:\Users\urruegg\source\urruegg_microsoft\frontier-envisioning\build\playwright-browsers'
$env:CI='true'
$env:SITE_AUTH_MODE='none'
```

No dependency installation until an actual missing-dependency failure.
Existing shared dependencies may be reused without changing manifests;
do not modify global authentication or inspect credentials.

## Task 0: Version preparation and measured identity provenance

**Files:** `tests/unit/test_demo_raster_110.py` (new);
`tests/fixtures/caldova-raster-1.10.0-inputs.json` (new after measurement);
`tools/demo_raster.py`, `tests/unit/test_demo_raster.py`,
`tests/unit/test_demo_raster_17.py`, `tests/unit/test_demo_raster_19.py`,
`tests/unit/test_demo_raster_192.py`, `tools/build_docs_demo.py`,
`tests/unit/test_docs_demo.py`; generator-owned version carriers.

- [ ] Freeze hashes of protected files, historical receipts/profiles/assets and
  the PRD/design historical suffixes in ignored build evidence.
- [ ] Add failing named-1.10.0 replay/input-drift and future-1.10.1 tests using
  the existing raster-test harness. Preserve unsupported 1.9.3 rejection.
- [ ] Run the focused raster/docs tests and confirm failure is specifically
  missing named support, not a dependency failure.
- [ ] Before any plugin edit, run the standard approved version operation:

```powershell
python tools\dev.py bump 1.10.0 --date 2026-11-12
python tools\build_demo.py --out build\finops-1.10.0\identity-probe --no-png
```

- [ ] Compare all 205 actual non-raster inputs with the approved 1.9.2/A6
  mapping. Stop on any unexpected input/count/hash difference. Only after
  equivalence, create the LF named record/pin and enable exactly 1.10.0.
  Keep all 223 raster assets and prior pins unchanged.
- [ ] Run related selectors GREEN:

```powershell
python -m pytest tests\unit\test_demo_raster.py tests\unit\test_demo_raster_17.py tests\unit\test_demo_raster_19.py tests\unit\test_demo_raster_192.py tests\unit\test_demo_raster_110.py tests\unit\test_docs_demo.py -q --tb=short
```

- [ ] Commit only version/provenance/test changes with #39 and the co-author
  trailer. Explicitly retain unreleased internal candidate status.

## Task 1: Contract, synthetic example and explicit validation gaps

**Files:** new `baseline_model.py`, `examples/caldova-agent-baseline.json`,
`references/baseline-sources.json`, `tests/unit/test_finops_baseline.py`.

- [ ] Write `unittest` cases before the module exists. Reuse the repository's
  `_util.load` plus a temporary `sys.path` context, as in Preview tests:

```python
import copy
import json
import sys
import unittest
from datetime import date
from unittest import mock
from tests.unit._util import ROOT, load

FIN = ROOT / "plugin" / "skills" / "frontier-finops"
DAY = date(2026, 11, 12)

def baseline_module(name):
    with mock.patch.object(sys, "path", [str(FIN / "scripts"), *sys.path]):
        return load(f"plugin/skills/frontier-finops/scripts/{name}.py",
                    f"agent_baseline_{name}")

def example():
    return json.loads((FIN / "examples" / "caldova-agent-baseline.json")
                      .read_text(encoding="utf-8"))

class BaselineContractTests(unittest.TestCase):
    def test_scenarios_need_another_driver_besides_demand(self):
        module = baseline_module("baseline_model")
        model = example()
        for scenario in model["baseline"]["scenarios"]:
            scenario["drivers"]["tokens_per_run"] = "1000"
        gaps = module.validate_model(model, as_of=DAY)
        self.assertIn("scenario-uncertainty", {gap["code"] for gap in gaps})

    def test_unknown_rate_reference_is_an_explicit_error(self):
        module = baseline_module("baseline_model")
        model = example()
        model["baseline"]["lines"][0]["rate_id"] = "NO-SUCH-RATE"
        with self.assertRaisesRegex(ValueError, "rate"):
            module.validate_model(model, as_of=DAY)

    def test_nested_authored_fields_remain_in_the_fingerprint(self):
        module = baseline_module("baseline_model")
        model = example()
        changed = copy.deepcopy(model)
        changed["baseline"]["assumptions"][0]["maturity"] = "changed"
        self.assertNotEqual(module.model_fingerprint(model),
                            module.model_fingerprint(changed))
```

- [ ] Run `python -m unittest tests.unit.test_finops_baseline -v`; expect RED
  for the absent module. Do not mask an unrelated loader failure.
- [ ] Define the contract above, including duplicate/reference checks, date
  order, positive pricing blocks/FX, finite decimal strings, shares in
  `[0,1]`, required owner/scope/evidence fields, known units/currencies and
  meaningful scenarios. Missing editable inputs return named gap records;
  malformed structure/types/reference contradictions raise field-specific
  `ValueError`. Never log the supplied price/source text in error messages.
- [ ] Author the synthetic example with an existing Caldova agent ID.
  For engineering arithmetic only, use demand 50/100/200 per month and
  tokens per run 500/1000/2000 across low/expected/high; token price is a
  fictitious CHF 1 per 1,000 tokens, fixed operations CHF 10/month and build
  CHF 200 once. Success share is 0.5 and outcomes per success is 2.
  All twelve months and the flat-demand assumption are explicit.
  Mark every invented rate/review synthetic; these are not Microsoft prices.
- [ ] Add focused subcases for duplicate IDs, unknown agent, malformed date,
  unsupported currency, boolean/negative/non-finite values and explicit empty
  scope. Add the four dated public reference metadata records, not prices.
- [ ] Run the new selector GREEN; commit the contract/fixture/tests with #38.

## Task 2: Decimal calculations, evidence gaps and result integrity

**Files:** new `baseline_calc.py`; extend `test_finops_baseline.py`.

- [ ] Add known-answer and missing-data tests before implementation:

```python
class BaselineCalculationTests(unittest.TestCase):
    def test_expected_scenario_and_first_year(self):
        calc = baseline_module("baseline_calc")
        result = calc.calculate(example(), as_of=DAY,
                                acknowledge_finops_preview=True)["results"]
        expected = result["scenarios"]["expected"]
        self.assertEqual(expected["months"][0]["total"]["amount"], "110.00")
        self.assertEqual(expected["annual_recurring"]["amount"], "1320.00")
        self.assertEqual(expected["one_time"]["amount"], "200.00")
        self.assertEqual(expected["first_year"]["amount"], "1520.00")
        self.assertEqual(expected["months"][0]["per_success"]["amount"], "2.200000")

    def test_missing_rate_never_becomes_zero_or_a_complete_total(self):
        calc = baseline_module("baseline_calc")
        model = example()
        model["rates"][0]["amount"] = None
        result = calc.calculate(model, as_of=DAY,
                                acknowledge_finops_preview=True)["results"]
        month = result["scenarios"]["expected"]["months"][0]
        self.assertIsNone(month["total"]["amount"])
        self.assertEqual(month["total"]["status"], "incomplete")
        self.assertIn("unpriced", {gap["code"] for gap in result["gaps"]})
```

- [ ] Run the same new unit selector RED, expecting an absent calculator.
- [ ] Implement the declared calculator, using these fixed rules rather than
  duplicating `fv_expr.py` or inheriting its legacy zero-division behaviour:

```python
from decimal import Decimal, ROUND_HALF_UP

def unit_metric(cost, denominator):
    if cost is None:
        return {"amount": None, "status": "unavailable", "reason": "incomplete-cost"}
    if denominator is None or denominator == 0:
        return {"amount": None, "status": "unavailable", "reason": "no-denominator"}
    amount = (cost / denominator).quantize(Decimal("0.000001"),
                                         rounding=ROUND_HALF_UP)
    return {"amount": format(amount, "f"), "status": "available", "reason": None}

def line_amount(quantity, rate, pricing_block, fx):
    return quantity * rate / pricing_block * fx
```

  Per-run quantity is monthly runs times the named per-run driver; fixed
  quantity is the named driver, once or each month according to frequency.
  Resolve units/pricing block and only explicit FX. Sum with decimal precision;
  round final period totals to cents and retain unrounded values until then.
  Annual recurring sums twelve authored months, first year adds one-time.
  Unit metrics name their matching period and recurring/first-year basis.
- [ ] Require acknowledgement before any operational calculation/receipt
  consumption. `True` is required; `1`, cached metadata and installation
  records do not grant it. Copy inputs rather than mutate them.
- [ ] Add typed gap results for missing demand/rate/FX, stale/unverified
  evidence, unsupported source applicability and missing quantities. An empty
  priced set yields `null`, not empty-sum zero. A synthetic mode may demonstrate
  calculations, but remains ineligible for real financial handover.
- [ ] Bind the shared fingerprint to material inputs and the exact calculated
  result. Receipt consumption checks shape, finite amounts, scenario coverage
  and recomputed outputs; rehashing a fabricated amount is not validation.
  Ignore only explicitly owned output metadata, not arbitrary nested fields.
- [ ] Add explicit FX known-answer, zero denominator, all-unpriced, stale source
  and tampered-input/result tests. Verify low/expected/high differ as authored.
  Run `test_finops_baseline` and all 81 legacy Preview cases GREEN.
- [ ] Commit calculator/tests with #38; review this stable contract before D2.

## Task 3: Frozen records, owner review, safe projection and CLI

**Files:** new `baseline_records.py`, `baseline_projection.py`,
`agent_finops.py`, `tests/unit/test_finops_baseline_io.py`;
`references/agent-finops-baseline.md`.

- [ ] Add failing `unittest`/temporary-folder cases for: missing acknowledgement
  writes nothing; a frozen filename cannot be overwritten; changed content
  cannot consume an old review; raw `approved` metadata cannot pass; unpriced
  still blocks; synthetic review is not commercial approval; migration leaves
  legacy bytes untouched and yields a draft.
- [ ] Run `python -m unittest tests.unit.test_finops_baseline_io -v` RED.
- [ ] Implement `seed`, `migrate`, `freeze`, `record_review`, `handover` with
  exclusive snapshot/review writes and material hash matching. Seed unknown
  quantities/prices as explicit gaps, not defaults. Migration links original
  evidence and preserves all consumed root/component restrictions; imported
  list-price ratios/statuses never become verified FX or approval.
  Validate IDs before using them in filenames; never accept traversal paths.
  Serialize before opening the destination and preserve existing files:

```python
import json

def write_exclusive(path, document):
    text = json.dumps(document, ensure_ascii=False, sort_keys=True,
                      indent=2, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
```

  `record_review` requires explicit decision/actor/date/evidence/version/hash
  and the accountable owner/delegation evidence. It records an external
  assertion, not authentication. Derived lifecycle uses these records, never
  a raw imported status. Financial readiness requires all design section 6
  conditions; no unpriced exception and no browser-note override.
- [ ] Implement dependency-aware projection with the four sharing classes and
  inherited legacy restrictions. Internal audience retains labelled private
  context; customer output requires the matching explicit scope for
  customer-specific material. Unknown validation/sharing and internal-only
  dependencies withhold affected values, totals, review evidence and hashes.
  Preserve independent public rows without reconstructing a complete total.
  Strip opaque internal notes before any final serialisation.
- [ ] Add leakage tests over root/line/quantity/rate/FX/source/review/outcome
  restrictions for JSON, Markdown and Blueprint report DTOs. Assert private
  sentinel strings/amounts/IDs are absent and withheld amounts are not zero.
- [ ] Implement CLI subcommands `seed`, `migrate`, `calculate`, `freeze`,
  `record-review`, `apply`, `export`; all require
  `--acknowledge-finops-preview` and explicit dated context before I/O effects.
  `--baseline`, `--blueprint`, `--agent-id`, `--review`, `--out`/`--out-dir`,
  `--as-of`, `--audience internal|customer` and `--customer-scope` apply where
  relevant. No subcommand follows source URLs or executes external programs.
  Catch only expected JSON/I/O/validation errors, report explicit stderr and
  return 2. Valid incomplete drafts return a labelled `partial` summary, not
  a success-shaped complete estimate. Stdout summaries contain no raw prices
  or private source data.
- [ ] Make `apply` validate the receipt and produce
  `agent_finops` schema `frontier-agent-finops-view/1.0` with safe profile,
  scenario, gap and handover records. Reject duplicate active agent revisions
  and legacy/new ambiguity; never silently replace value-case costs.
- [ ] Document exact CLI and money/null/status contracts, synthetic mode,
  external-review limits and explicit migration. Run both new unit modules
  and legacy Preview cases GREEN; commit with #38.

## Task 4: Optional wrapper and customer normalisation

**Files:** `plugin/skills/frontier-blueprint/scripts/build_with_identity.py`,
`plugin/skills/frontier-blueprint/scripts/build_blueprint.py`,
`tests/unit/test_finops_preview.py`, `tests/unit/test_finops_baseline_io.py`.

- [ ] Write failing tests for new baseline preflight without acknowledgement,
  missing optional skill, conflicting legacy/new input, invalid embedded
  `agent_finops` and core-only operation when the skill is absent.
  Assert no identity/output folders or input copies exist after refusal.
- [ ] Run both relevant modules RED, retaining existing tests unchanged.
- [ ] Add repeatable `--agent-finops` inputs to the wrapper, mutually exclusive
  with legacy `--finops`; preserve older direct callers with absent optional
  namespace fields. Parse and validate every requested baseline/agent/source
  before side effects. Keep ordinary value-only paths lazy and independent.
- [ ] Add a guarded baseline application chain on copies, with fresh
  acknowledgement forwarded only within that action. Reject pre-existing
  ambiguous legacy/new blocks and Preview-derived legacy value without its
  required source, rather than silently selecting or clearing a model.
- [ ] In standalone `build_blueprint.py`, accept the explicit acknowledgement
  flag when successor data is present, validate/project through lazy optional
  baseline helpers before any serialisation, then use existing customer
  scrub/CSP-safe JSON handling. Forward the flag at all new internal call
  sites, including ontology/customer rebuilds. Core paths never import FinOps.
- [ ] Run new wrapper and existing Preview/source-projection tests GREEN;
  commit with #37. Review the Python/renderer boundary before Task 5.

## Task 5: Explicit fixture, self-test and installed-package preparation

**Files:** `tools/build_demo.py`, `tools/dev.py`, `tools/build_site.py`,
`tools/selftest.py`, `tests/unit/test_demo_profiles.py`,
`tests/unit/test_tools_core.py`, `tests/unit/test_site.py`,
`tests/dom/helpers.mjs`.

- [ ] Add failing fixture/profile/site tests before adding the switches:
  no baseline in default core; explicit baseline without acknowledgement
  refuses before output cleanup; conflicting Preview modes reject; the new
  fixture gets exactly its own CSP and no deployment/default-download inclusion.
- [ ] Implement `--with-finops-baseline` as an explicit alternate demo mode.
  Build `build/demo-agent-finops-preview` separately from the legacy fixture.
  Add `BLUEPRINT_BASELINE_HTML` for DOM tests and an explicit
  `--baseline-demo` site input producing `blueprint-baseline.html`.
  Keep core and legacy fixture paths/defaults unchanged.
- [ ] Extend DOM/e2e preparation and mock only the new callback in the aggregate
  order unit test, not the production gate. Ensure the isolated e2e site passes
  the new fixture and per-page CSP to the child server. This fixture preparation
  precedes Task 6, so new UI tests have a real input without a dependency cycle.
- [ ] Extend self-test through the real new CLI using temporary directories:
  refused operation leaves no files; synthetic seed/calculate/apply/export
  works under technical acknowledgement; viewer consent remains separate.
- [ ] Build an initial actual package, extract into a temporary directory and
  run its installed `plugin/skills/frontier-finops/scripts/agent_finops.py`
  against installed examples. Verify refusal and acknowledged JSON/Markdown,
  frozen-review behaviour, core with FinOps absent and eight installer plans.
  Repeat this proof against the final archive in Task 8.
- [ ] Run focused profile/site/core/new tests GREEN and the self-test, without
  claiming the not-yet-built UI passed. Commit preparation changes with #39.

## Task 6: Review UI, financial handover and gated exports

**Files:** `src/renderer/template.js`, `src/renderer/template.css`,
`tests/dom/finops-baseline.test.mjs`, `tests/e2e/finops-baseline.spec.mjs`,
`tests/dom/helpers.mjs`; generated template only through the task runner.

- [ ] Add DOM tests using `openBlueprint`, `go`, `txt` and
  `acknowledgePreview`: no successor figures before acknowledgement; a missing
  baseline gives an actionable gap; raw approval/local notes do not pass;
  unpriced blocks; independent ordinary value stays available. Inject only
  the documented report DTO, not guessed future field names.
- [ ] Run the focused new DOM file RED using the real fixture from Task 5:

```powershell
python tools\build_demo.py --out build\demo-agent-finops-preview --with-finops-baseline --acknowledge-finops-preview
$env:BLUEPRINT_BASELINE_HTML=(Join-Path (Get-Location) 'build\demo-agent-finops-preview\Frontier Company Blueprint - Template (Caldova sample).html')
node --test tests\dom\finops-baseline.test.mjs
```
- [ ] Add a separate successor-data resolver; keep legacy `FO` and ordinary
  value provenance semantics. `previewPresent` recognises successor data,
  while `casePreview` is not changed merely because unconsumed baseline data
  exists. Reject conflicting data visibly rather than choosing an old cache.
- [ ] Extend existing FinOps rendering with profile/discovery, scenario,
  unit-economics, evidence/validation and export sections. Render decimal
  strings as escaped text, not newly recalculated JavaScript money:

```javascript
function baselineMoney(value) {
  if (!value || value.amount === null) return "Unavailable";
  return String(value.currency || "") + " " + String(value.amount);
}
```

  Show reason/status beside unavailable/partial values. No fallback from
  withheld successor values to old legacy totals. Keep the existing transient
  document acknowledgement and warning; no saved consent.
- [ ] Add Canvas and Factory/Plan financial summaries from validated report
  evidence, not workshop validation notes. Missing data stays blocked; valid
  fully priced, reviewed evidence supplies the financial check only. Preserve
  all other readiness checks and declared existing build/release/operate stages.
- [ ] Capture proposed workshop answers in existing feedback/export patterns,
  labelled as input to a new draft. They cannot mutate frozen data or approve.
  Markdown/JSON export uses the already projected DTO, warnings, dates,
  formulas and incomplete states; figures/export remain acknowledgement-gated.
- [ ] Rebuild the template, run new and adjacent DOM cases GREEN, then test
  real browser reload reset, keyboard/focus, dark/light, strict CSP, no external
  requests and actual downloads. Commit source/generated/test changes with #37.

## Task 7: User guidance, product authority and generated documentation

**Files:** `plugin/skills/frontier-finops/SKILL.md`,
`plugin/skills/frontier-finops/references/finops-for-agents.md`,
`plugin/skills/frontier-finops/references/guardrails.md`,
`plugin/skills/frontier-envisioning/SKILL.md`,
`plugin/skills/frontier-blueprint/SKILL.md`,
`plugin/skills/frontier-blueprint/references/blueprint-schema.md`,
`README.md`, `plugin/README.md`, `CHANGELOG.md`,
`docs/prd.md`, `docs/solution-design.md`, `docs/getting-started.md`,
`docs/starter-prompts.md`, `docs/demo/README.md`, `docs/README.md`,
`docs/sprints/SPRINT-007-agent-finops-baseline.md`.

- [ ] Update affected procedures/routing with the approved offline baseline
  path, fresh awareness, strict priced handover, explicit migration and
  externally evidenced review limits. Keep descriptions under 900 UTF-16 units.
  FinOps stays optional Preview; seven other skills remain GA.
- [ ] Add additive 1.10.0 requirements/architecture/current release-decision
  sections before historical product blocks. Do not rewrite A.12/A.13, prior
  IDs/results or release records. Reference #35/#36/ADR-0028 and AFB acceptance.
- [ ] Describe exact installed CLI examples, synthetic-vs-real data, scope and
  sharing. No live connector, authenticated approval, product GA promotion or
  quote claims. Remove no archival intake/evidence to polish presentation.
- [ ] Regenerate template/install metadata and the core-only tracked Caldova
  HTML/five genuine screenshots/manifest through existing generators:

```powershell
python tools\dev.py template package demo docs-demo
python tools\dev.py docs --strict
```

- [ ] Record actual evidence only after Task 8. Commit eligible prose/generated
  docs with #39, preserving historical/protected hash evidence.

## Task 8: Quality gates, repeatability, review and draft PR

- [ ] Run targeted new selectors together, then full strict gates sequentially:

```powershell
python -m unittest tests.unit.test_finops_baseline tests.unit.test_finops_baseline_io tests.unit.test_finops_preview -v
python tools\dev.py check --strict
python tools\dev.py site e2e --strict
python tools\build_package.py --dist dist\distribution-1.10.0
python tools\build_release.py --dist dist\distribution-1.10.0
```

  Both gates must end `ALL GATES PASSED`. Record actual test/subtest/self-test/
  DOM/browser counts and expected skips; do not reuse 1.9.2 counts as new proof.
- [ ] Save hashes of all three handoff files, rebuild core independently into
  a fresh named output folder, rebuild distribution and require exact equality.
  Inspect actual archive/source bytes, eight registered skills, current entry
  allowlist, nested privacy, checksum contents and offline installed CLI results.
  Never substitute a golden ZIP or infer inventory from the previous release.
- [ ] Repeat installed-CLI refusal/acknowledged exports, record integrity and
  core-with-skill-absent proof against the exact final plugin ZIP. Do not import
  working-tree modules as a substitute for this final installed execution.
- [ ] Verify protected/historical/profile/asset and PRD/design suffix hashes
  against Task 0, with only the specifically approved named profile/version
  additions. Keep physical source and archive text LF to avoid Windows drift.
- [ ] Review spec coverage and code logic at the package boundaries; fix
  meaningful findings and rerun covering checks. Technical review is not
  independent human approval or formal self-approval.
- [ ] Read the repository PR template before drafting its body. Push only the
  feature branch; open a draft PR with actual command results, hashes, red/green
  evidence, acceptance checklist, screenshot evidence and remaining human checks.
- [ ] Leave merge, protected labels/settings/files, tags/releases, live Cowork/
  tenant/financial authority verification and deployment to the maintainer.
  Protected routing #8 and release-cache #30 remain separate dependencies.

## Plan self-review and coverage

| Acceptance | Tasks |
|---|---|
| AFB-01 | 2, 3, 4, 5, 6 |
| AFB-02 | 1, 3, 4 |
| AFB-03 | 1, 2 |
| AFB-04 | 2, 6 |
| AFB-05 | 1, 2, 3, 5 |
| AFB-06 | 1, 3, 6 |
| AFB-07 | 3, 6 |
| AFB-08 | 2, 3, 4 |
| AFB-09 | 2, 3, 4, 5, 6 |
| AFB-10 | 1, 2, 3, 6 |
| AFB-11 | 5, 6, 8 |
| AFB-12 | 0, 6, 7, 8 |

All interfaces above are defined within a named task. The synthetic expected
values are engineering assertions, not a price recommendation. Pending human
plan approval is a real gate, not missing implementation content. No current
check/test/build success is claimed by this plan's future commands.
