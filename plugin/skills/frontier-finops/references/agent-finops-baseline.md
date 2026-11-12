# Agent FinOps baseline — offline Preview contract

Use this successor for an explicitly requested, agent-linked planning baseline.
It does not replace the legacy `frontier-finops/1.0` model or the ordinary value
case. The bundled FinOps skill remains optional Preview; it is not a ninth skill.

> Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.

Every operation requires current, actual boolean `True` acknowledgement and an
explicit evaluation date. Installation, saved technical metadata, workshop notes
and an old `approved` field are not consent or external owner review. All
forecasts remain estimates. Nothing here authorises spending, purchases, build,
deployment or changes to protected repository labels.

## Python interfaces

Scripts live in `../scripts/`. Inputs are detached JSON-compatible dictionaries;
`as_of` is a `datetime.date`, not a timestamp, inferred clock or string.
Operational keyword-only `acknowledge_finops_preview` defaults to `False`.

| Module | Public operation | Return |
|---|---|---|
| `baseline_model` | `validate_model(model, *, as_of, blueprint=None)` | Gap list; malformed types, references or contradictory contracts raise `ValueError` |
| `baseline_model` | `material_payload(model)`; `model_fingerprint(model)` | Detached material; shared canonical fingerprint |
| `baseline_calc` | `calculate(model, *, as_of, acknowledge_finops_preview=False)` | Fresh calculated document |
| `baseline_calc` | `validate_receipt(model, *, as_of, acknowledge_finops_preview=False)` | Detached validated technical receipt |
| `baseline_records` | `seed(blueprint, agent_id, *, as_of, acknowledge_finops_preview=False)` | New incomplete draft |
| `baseline_records` | `migrate(legacy, blueprint, agent_id, *, as_of, acknowledge_finops_preview=False)` | New context-only draft |
| `baseline_records` | `freeze(model, out_dir, *, as_of, acknowledge_finops_preview=False)` | Exclusive snapshot `Path` |
| `baseline_records` | `record_review(snapshot, review, out_dir, *, as_of, acknowledge_finops_preview=False)` | Exclusive external-review record `Path` |
| `baseline_records` | `handover(snapshot, reviews, *, as_of, acknowledge_finops_preview=False)` | Dated planning-readiness dictionary |
| `baseline_projection` | `project(model, reviews=(), *, as_of, audience, customer_scope=None, acknowledge_finops_preview=False)` | Projected derivative report |
| `baseline_projection` | `render_markdown(report)` | String from a projected report, with escaped cells and plain-text evidence references |
| `agent_finops` | `apply_models(blueprint, baselines, reviews=(), *, as_of, audience, customer_scope=None, acknowledge_finops_preview=False)` | Detached Blueprint with derivative `agent_finops` block |
| `agent_finops` | `main(argv=None)` | Integer CLI exit status |

An operation checks acknowledgement before work or output directories. Public
operations do not mutate inputs. No script retrieves source URLs, reads
credentials or runs external programs.

## Drafts, evidence and arithmetic

The authoritative authored schema is `frontier-finops-baseline/1.0`. It contains
`mode` (`planning` or `synthetic`), `forecast_kind: estimate`, `profile`,
`baseline`, `rates`, `fx`, `sources` and explicit sharing/provenance.
The calculator adds `results` and `finops_preview`.

Seed resolves an existing Blueprint agent ID, keeps its Canvas and copies
consumed root/domain/agent/source context. It does **not** turn a generic
Blueprint owner or Canvas approval seam into business, technical or finance
ownership. Those owners, demand, periods, scope, rates, FX and currency stay
unknown until supplied. Empty scenarios/scope and null inputs have explicit
validation gaps; they are not complete zero-cost forecasts. Caller source
context is unverified, customer-specific when a scope is supplied, otherwise
validation-required. Unresolved existing Blueprint source references refuse.

Seed merges actual root/domain/agent and copied descendant sharing classes,
legacy flags and scope declarations through the calculator's existing lineage
merger. Customer-specific defaults never replace internal-only or
validation-required ancestry. Conflicting scopes retain the declared scope set,
leave the new scalar scope unknown and require validation; no customer is picked.
Unconsumed unrelated domains do not taint the selected Canvas. The complete
Blueprint fingerprint still binds them and is not customer-report content.
Migration uses the same merger for new and consumed legacy restrictions.
Source closure follows every supported `src`, `content_src` and `source_id`
edge at ancestor and nested levels through the supplied source registry.
Canonical list ancestry retains all edges; copied source context retains the
original reference kinds. Parent classes/scopes constrain descendants.
Unknown nonblank Blueprint references refuse. Explicit missing ancestry and
cycles remain validation-required, not customer-shareable; no silent parent or
customer selection occurs.

Every in-scope driver needs a typed, quantified line and applicable evidence.
Rate and FX records identify units, pricing blocks, currencies, sources,
verification dates and declared freshness policies. No licence coverage, price,
FX conversion, currency or universal evidence lifetime is inferred.

Calculator results use `frontier-finops-baseline-results/1.0`. Each
`results.scenarios.low|expected|high` contains:

- `months`: twelve `{period, lines, total, verified_subtotal,
  provisional_subtotal, known_priced_subtotal, per_run, per_success,
  per_outcome}` records.
- `annual_recurring`, `one_time`, `first_year`, `one_time_lines`.
- `unit_metrics.annual_recurring|first_year`, each with `per_run`,
  `per_success` and `per_outcome`.

Money has decimal-string `amount` or `null`, `currency`, `status`, `reason`,
`period` and `basis`. Unit metrics add `denominator` and `denominator_unit`.
Lines have `line_id`, quantity/unit, `cost` and dated `pricing_evidence`.
Every derived record carries technical dependency/source/FX lineage before
projection. Public output strips those technical pointers.

The D35-10 draft-reporting policy permits usable supplied stale/unverified
rates or FX to produce **provisional** figures. Verified, provisional and known
priced contributions stay distinguished. Unknown required quantities/prices
make full totals and dependent metrics `null`, not zero or a public/priced
subset labelled as the total. `available` means computable, not approved.
`unavailable`, `incomplete`, `provisional` and `withheld` are distinct states.

Arithmetic is isolated from the caller's Decimal context. Intermediate
arithmetic must be exact within the calculator's 80-digit context and bounded
exponents. Non-terminating intermediate line-price division and unsupported
high-precision products/sums explicitly refuse; they do not silently round
inputs. Only final money rounds to cents and final unit ratios to six places,
using `ROUND_HALF_UP`. Annual money sums unrounded monthly contributions.
Final ratios use exact quotient/remainder rounding. JavaScript must not
recalculate financial figures.

The [Caldova example](../examples/caldova-agent-baseline.json) is entirely
invented: expected recurring CHF 110 per month, CHF 1,320 annually, CHF 200
one-time and CHF 1,520 first year. It is not provider pricing, real customer
usage, commercial verification or actual owner approval. Synthetic mode,
sources, verification and review assertions never establish financial handover.

## Frozen snapshot and external-review shapes

Freeze takes a calculated document with a recomputable valid receipt. It writes
`<baseline-id>.v<version>.json` exclusively:

```text
{
  schema: "frontier-finops-snapshot/1.0",
  frozen_at: ISO date,
  target: {baseline_id: string, version: positive integer, material_hash: string},
  model: complete calculated frontier-finops-baseline/1.0 document,
  review_boundary: external-assertion limitation
}
```

The wrapper owns the target; no self-referential hash is added to calculation
material. `material_payload` omits **only** root `results`, `finops_preview`,
`review_records` and `handover`. Nested authored fields and source restrictions
remain material. The receipt also binds the evaluation date, scenario IDs and
recomputed results. Hashing a fabricated amount or diagnostic does not validate
it. Canonical object-key save/reload is supported; authored arrays retain their
meaningful order. Older receipts made before the determinism repair may require
explicit recalculation.

IDs used in filenames must be portable alphanumeric/hyphen/underscore IDs,
starting alphanumeric, at most 120 characters, and not Windows reserved device
names. Versions are positive integers, never booleans. Existing snapshot or
review files cannot be overwritten. Change material under a new version and
obtain new review; do not reuse old review against a different version/hash.
The local output directory is the history boundary, not a global version registry.

`record_review` requires these externally supplied fields:

| Field | Required meaning |
|---|---|
| `id` | Unique filename-safe review ID |
| `decision` | `approve`, `revise` or `reject`; not raw `approved` status |
| `actor`, `finance_owner` | Explicit external actor and the exact frozen finance owner/role |
| `delegation_evidence_ref` | Required nonblank external evidence if actor differs from finance owner |
| `date`, `evidence_ref` | ISO review date between freeze and evaluation, and nonblank opaque external evidence reference |
| `baseline_id`, `version`, `material_hash` | Exact snapshot target, copied from `snapshot.target` |
| `mode` | Exact frozen planning/synthetic mode |
| `sharingClassification`, optional `customer_scope` | Review sharing context; missing/unknown remains a blocking gap |
| Optional `synthetic` | Actual boolean; `true` prevents planning readiness |
| Optional `source_id`, `src`, `content_src` | Must resolve to frozen model sources; parent restrictions remain binding |

Known structured review markers also prevent readiness: `type`, `status`,
`validationStatus` or `mode` equal to `synthetic`, anywhere in review ancestry,
including nested evidence/verification records. A `false` boolean, planning mode
or raw approved status elsewhere does not cancel these markers. Ordinary prose
mentioning the word synthetic is not such a marker. Top-level review mode must
still match the frozen target.

The exclusive review file is
`<baseline-id>.v<version>.<review-id>.json`. It retains the explicit review
fields and adds `schema: frontier-finops-owner-review/1.0`, `recorded_as_of`,
`assertion: externally-asserted-not-authenticated` and `review_boundary`.
Missing sharing defaults to validation-required. Malformed fields refuse before
directory creation. Reviews do not authenticate the actor or validate the
external evidence. Files and hashes are **not tamper-proof audit storage**.

`handover` returns schema `frontier-finops-handover/1.0`, `as_of`, `target`,
`lifecycle`, `structural_validation`, `pricing_completeness`, `ready`, `status`,
`gaps`, `owner_review`, `financial_permission: false` and `limitations`.
Structural validity, pricing completeness, external lifecycle and dated
readiness are separate. An external approve decision can remain historically
`approved` while current evidence blocks readiness. No review means
`validated` or `needs-validation`, never approved. Editable reports are drafts.
No automatic supersession or silent last-review selection is performed.

Readiness rechecks every model gap, required unit metrics, unknown legacy
visibility, synthetic review and unresolved review sharing. Missing, provisional,
stale or synthetic evidence blocks. Duplicate active reviews refuse; callers
must explicitly resolve conflicting history. Later evaluation validates the
stored receipt at `frozen_at`, then recalculates dated evidence without rewriting
the frozen file. Raw status, browser notes and technical acknowledgement cannot
substitute for review. Even `ready: true` is **planning evidence**, not financial
permission, budget, purchase, build or deployment approval.

## Audience projection and exact derivative DTO

`project` accepts a valid calculated draft or frozen snapshot dictionary.
External reviews require the frozen wrapper. Audience is explicitly `internal`
or `customer`; invalid audiences refuse. Customer-specific material requires
the matching authored/inherited customer scope. Caller scope is **not
authorisation**, authentication or generic distribution clearance.

Projection resolves actual dependency pointers and both legacy source-reference
fields before serialisation. Source-parent, root and component restrictions
dominate approval flags. Sharing classes are customer-shareable,
customer-specific, internal-only and validation-required. Unknown classes or
legacy visibility fail closed. Root/profile-private material withholds the whole
linked target. A private baseline envelope withholds its child context and
scenario data while unrelated public profile context can remain.

Private line, quantity, rate, FX, source, outcome or review dependencies withhold
affected money, evidence, formula/unit/readiness context and identities. Public
independent rows may remain; aggregate totals are not rebuilt from them.
Protected reference keys use neutral `withheld-N` placeholders. Projection
collects known material/calculation and Blueprint/legacy/source/rate/FX ancestry
digests, plus private source/review identities and opaque evidence/URL references.
It checks dictionary keys and embedded strings, not only named fields or
whole-string equality. Aliases and redaction paths cannot expose those tokens.
Recognised digest registries include keys as well as values, lists and nested
entries; a digest used as a key with a boolean value is still protected.
Labelled external digest values remain withheld regardless of representation;
recognising them for redaction does not validate or authenticate those digests.
Validated monetary/quantity/unit/currency/date scalars are governed by dependency
classification instead of accidental textual collisions with an identifier.
Protocol field keys are recognised at actual schema positions. Authored driver
IDs and annotation/mapping keys remain redactable even when they spell the same
word, such as `drivers`. Literal dotted/bracketed keys do not create trusted
schema paths. Missing or withheld nested containers are guarded; they do not
produce traceback-shaped CLI failures or reconstructed inputs.
Independent public amounts and rows remain, even when unused private context
means the complete model hash must be hidden. Internal reports retain
private context and are labelled `private-context-not-shareable`. This is not
encryption or access control; the caller still governs file handling and truthful
classification.

The exact top-level report schema is `frontier-agent-finops-report/1.0`:

```text
schema, notice, maturity, forecast_kind, audience, distribution, as_of,
limitations, financial_permission, mode, status, agent_id, profile,
baseline, currency, context, formulas, scenarios, scenario_inputs,
evidence, gaps, handover
```

- `baseline`: safe ID/version/authored date/start month/currency/sharing envelope.
  Top-level `agent_id` and `currency` are strings or `null`, never placeholder
  objects or fallback legacy values.
- `context`: projected scope, annualisation, assumptions, exclusions, risks,
  confidence.
- `scenario_inputs`: authored scenario rows, with protected quantities and
  driver-evidence/reference keys withheld before serialisation.
- `scenarios`: the three calculator scenario objects described above, projected
  recursively. Technical hashes/pointers/legacy ancestry IDs are stripped.
- `evidence`: projected `sources`, `rates`, `fx`, including public dates and
  explicit provisional evidence.
- `handover`: projected dated planning evidence; customer-private context
  becomes `{status: withheld, ready: false, financial_permission: false, ...}`.
- Full-target withholding uses `agent_id`, `baseline`, `currency: null`,
  `mode/status: withheld`, empty scenarios/input rows and withheld context,
  profile/evidence/formulas. No private target/hash is returned.

Money withheld by a dependency becomes
`{amount: null, status: withheld, reason: restricted-dependency}`; protected
lines additionally withhold quantity, identity and pricing evidence.
Customer gaps omit private field paths. Markdown uses this same DTO, stable
object-key traversal, escaped table/HTML/link syntax and plain-text references.
Neither report format can be re-imported as an authoritative or approved model.

Blueprint application adds only:

```text
agent_finops: {
  schema: "frontier-agent-finops-view/1.0",
  notice, maturity: "Preview", as_of, audience,
  records: [projected report DTO, ...],
  financial_permission: false, limitations
}
```

It validates every explicit baseline/review/agent before output effects, checks
Blueprint root/domain/agent/source restrictions, and refuses duplicate active
agent revisions, unused reviews and existing `finops`/`agent_finops` ambiguity.
It uses copies, not value-case rewriting. The ordinary Blueprint is retained:
its normal customer scrub and wrapper/renderer integration are separate work.
This block does not grant Blueprint-wide distribution clearance.

## Thin CLI

Run `python plugin/skills/frontier-finops/scripts/agent_finops.py --help`.
Each command below also requires `--as-of YYYY-MM-DD` and
`--acknowledge-finops-preview`.

| Command | Required input/output flags |
|---|---|
| `seed` | `--blueprint BP.json --agent-id D3-A05 --out draft.json` |
| `migrate` | `--baseline legacy.json --blueprint BP.json --agent-id D3-A05 --out new-draft.json` |
| `calculate` | `--baseline draft.json --out calculated.json` |
| `freeze` | `--baseline calculated.json --out-dir snapshots` |
| `record-review` | `--baseline snapshot.json --review external-review.json --out-dir reviews` |
| `apply` | `--blueprint BP.json --baseline calculated-or-snapshot.json --out applied.json --audience internal\|customer` |
| `export` | `--baseline calculated-or-snapshot.json --out-dir reports --audience internal\|customer` |

`apply` accepts repeated `--baseline` and `--review` flags. `export` accepts
repeated `--review`; contradictory active reviews refuse. `record-review`
requires exactly one explicit review. `apply` and `export` accept optional
`--customer-scope`. No command selects a silent winner or follows a source URL.

`export` writes exclusive `report.json` and `report.md` from the same projected
DTO. All writes use UTF-8, LF and finite JSON; canonical JSON has sorted object
keys. Input aliases and existing outputs refuse. Draft edits are made in new
working files or in memory; the CLI never overwrites an input/frozen/legacy file.
An I/O interruption is not an atomic filesystem transaction: inspect any
partially created local output and choose a new directory for a retry.

Success stdout is only bounded JSON:
`{command, status, maturity: Preview, financial_permission: false}`.
Incomplete successful operations report `partial`; an evidenced exported
planning report may report `planning-ready`. No prices, private IDs, filenames
or source bodies appear in the default summary. Expected input/JSON/I/O/
validation errors return `2` with bounded stderr, not a traceback or
success-shaped fallback. Duplicate JSON object keys and nonfinite JSON refuse.
Local private output is never automatically published.

## Migration boundary

Only explicit `frontier-finops/1.0` input is accepted. Migration preserves an
original-context fingerprint, consumed legacy context and inherited technical
source restrictions in the **new** draft. It strips old results, raw lifecycle/
approval/consent fields; those are not new authority. Legacy list-price ratios,
monthly totals, licence coverage, currency, value NPV and old scenarios are not
proved typed unit rates/FX or new economic scenarios. No such mapping is inferred.
Unresolved legacy context references remain unverified, missing-evidence source
records; they cannot validate pricing or readiness. Collect the new inputs.
Original legacy bytes remain unchanged.
