# Process governance and SAP grounding implementation plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-17 |
| Author | AI assistant (AI-assisted planning) |
| Status | Written specification approved; this plan awaits explicit human plan/readiness approval and execution-mode selection; implementation not started |
| Scope | Bounded #59 correction planned for 1.10.1; no new skill, integration runtime or release authorisation |
| References | [Catalogue](README.md), [Child #59](https://github.com/urruegg/frontier-envisioning/issues/59), [Parent #58](https://github.com/urruegg/frontier-envisioning/issues/58), [Idea and decisions](../ideas/2026-11-17-optional-systems-extensions.md), [Approved written specification](../specs/2026-11-17-process-governance-sap-grounding-design.md), [SPRINT-011](../sprints/SPRINT-011-process-grounding-and-optional-systems.md), [PRD](../prd.md), [Solution design](../solution-design.md), [ADR-0026](../adr/0026-process-ontology-fabric-iq.md), [ADR-0027](../adr/0027-cdm-grounding-and-data-products.md) |

> **For agentic workers — REQUIRED SUB-SKILL:** use `superpowers:executing-plans`
> for approved inline execution, or `superpowers:subagent-driven-development`
> only if the human selects it. Use the equivalent AGENTS method when a skill
> is unavailable. Execute the checkbox steps
> test-first, normally 2–5 minutes each; full verification commands take longer.
> No execution mode or delegated implementation is approved by this document.

**Goal:** Stop proposing retiring governance structures and unconfirmed SAP
routes as current, ready designs, without losing legacy evidence or privacy.

**Architecture:** Correct the existing process canon and detached
seed → normalise → apply → render/export pipeline. Use one explicit unresolved
source path and a small SAP prerequisite assessment, not a pack/route framework.
Separate saved choices from current sourced guidance in every consumer.

**Tech stack:** Existing offline Python standard library, JSON, `unittest`,
renderer JavaScript, `node:test`/happy-dom and Playwright; existing
`tools/dev.py` generators and distribution checks. No runtime dependency.

## Authority, readiness and stops

The human selected **`approve-written-correction-spec`** for the actual
`docs/specs/2026-11-17-process-governance-sap-grounding-design.md`, SHA-256
`8ab93d9542e3db44f132d4b352551b17ef3c00eb1567ed4e62f85ed93ef78c5f`.
The [actual written-approval receipt](https://github.com/urruegg/frontier-envisioning/issues/59#issuecomment-6949117136)
is separate from the earlier `approve-correction-design` direction.
Only approval receipts and real plan links have since been added to the
specification; its agreed behaviour and acceptance criteria are unchanged.

Real #59 is the bounded size M/P1 engineering chore; `@urruegg` is accountable,
not an inferred assignee. #58's choices are `one-skill-six-packs`, `d365-first`,
`approve-d365-slice`, `preview-wrapper`, `patch-then-d365` and
`approve-correction-design`. They do not approve all six brief catalogues.
Separate 1.11 systems/Dynamics 365 work covers Sales, Customer Insights -
Journeys/Data, Customer Service and Contact Center, not this patch.
Issue facts and source checks were verified by the coordinating assistant
using the approved `urruegg` account and the public sources cited in the spec.

**STOP — human plan decision:** this real plan is linked from SPRINT-011 and
the written approval is recorded. Initial early-intake validation reported
three missing-plan-link errors; the real links resolve that mismatch without
changing `tools/check_docs.py` or borrowing an unrelated plan. Before implementation,
obtain explicit human approval of this plan, readiness evidence under AGENTS
section 3, and an inline/subagent execution choice. Verify current issue and
blocking-decision evidence through the parent's authenticated interface.
Do not infer or set `status:ready`, `approved:*`, assignee or milestone fields.
No new product decision is required by the bounded representation below.

Planning uses the existing Windows `frontier-envisioning-wt-48` worktree,
branch `docs/58-optional-systems-design`, based on
`b88b9a2efa1eb342d5542475c63eee5f7bb43e4b`.
After actual approval, begin from the exact committed planning revision
reviewed by the human and create `fix/59-process-grounding` in this same
isolated worktree. Require a clean worktree before switching; never reset or
overwrite unrelated work. Do not create another worktree or touch the primary
checkout's editor settings or either untracked field brief.
This planning package changes only eight Markdown records/catalogues.

Published immutable **1.10.0** identities supplied by the parent:

- Release source: `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9`.
- Annotated tag object: `5f9d21953db9c968ae56ac6d485baff3fc09b0ce`.
- Plugin ZIP SHA-256: `9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`.

**STOP — human dependencies:** [#52](https://github.com/urruegg/frontier-envisioning/issues/52)
must retain the exact published manifest for final release/reproduction
acceptance; it is not permission to write protected records or skip a failed
baseline. Protected legacy session-start routing remains pending human
[#8](https://github.com/urruegg/frontier-envisioning/issues/8) action.
Neither dependency authorises App, hooks, rules, settings, labels, workflow,
merge, tag, publish or deploy changes. Do not assign those actions to a coder.

## Concrete representation and compatibility contract

Using only `status: later` would still produce a mirrored database or default
lakehouse. A general route/pack framework is unnecessary. Choose the following
additive representation; keep `frontier-blueprint/1.0`,
`frontier-ontology/1.0` and `frontier-fabric-iq-canon/1.0` unchanged.

New SAP sources have `path: "unresolved"`, `item: null`, `status: "later"`.
Add `paths.unresolved` with `item: null` to the process canon; it is a
recognised *absence of a selected route*, never a supported Fabric binding
item. Leave `binding_sources` and `SOURCE_STATUS` unchanged. The SAP rule
must intercept SAP names, including a name containing Datasphere, before
generic mirroring/pipeline rules. Non-SAP rules remain unchanged.

One source-local object carries the assessment:

```json
{
  "route_assessment": {
    "state": "conditional",
    "candidate_path": "mirroring",
    "prerequisites": {
      "supported_source": {"status": "unknown", "note": "Confirm the source family with its data owner.", "src": []},
      "fabric_capacity": {"status": "unknown", "note": "Confirm existing Fabric capacity.", "src": []},
      "datasphere_environment": {"status": "unknown", "note": "Confirm a suitable SAP Datasphere environment.", "src": []},
      "premium_outbound_integration": {"status": "unknown", "note": "Confirm Premium Outbound Integration entitlement.", "src": []},
      "adls_gen2_permissions": {"status": "unknown", "note": "Confirm ADLS Gen2 staging and required permissions.", "src": []}
    },
    "commercial_note": "SAP Datasphere Premium Outbound Integration: unpriced / to confirm.",
    "src": ["G59-P3", "G59-P7"]
  }
}
```

- Prerequisite status is exactly `unknown`, `confirmed` or `unsupported`.
  Missing legacy assessments become this explicit unknown checklist. Malformed
  objects/statuses/reference lists are errors, not truthy confirmation.
  `src`/`content_src` retain their existing evidence/privacy meaning.
- `candidate_path` is an option, not selected support. For an SAP family
  without source-qualified mirroring evidence (for example Ariba), seed it as
  `null`, not a ready fallback. Do not build an alternatives catalogue.
- Derive `state`, never trust a supplied `owner_confirmed` flag. It can be
  `owner_confirmed` only for an explicitly authored selected path/item, named
  owner, and all five confirmed records with non-empty notes and resolvable
  estate-evidence references in the supplied Blueprint `evidence` register.
  Without that context, retain the assertion but assess it as conditional;
  never fetch evidence or import a FinOps resolver. Public P3/P7 documentation
  alone is not estate evidence. Unknown/unsupported requirements warn.
  Even complete prerequisites do not auto-promote `path: unresolved`.
  This is an owner-asserted design selection, never tenant verification,
  licensing authority, provider GA or publication readiness.
- Preserve imported SAP `path`, `item`, scheduling `status`, entity bindings
  and evidence verbatim as recorded choices. Add the current conditional
  assessment and warning instead of bulk-renaming old records. Every
  readiness/binding display must honour it. New unresolved sources have no
  Fabric item; new default entity bindings referencing them are
  `{"layer":"silver","item":null,"table":null,"origin":"default"}`.
  Do not default these back to lakehouse on a second normalisation.
- Retain entity `source` as a relationship/provenance link, not proof of a
  binding. Exclude conditional sources from `stats.bound`, graph/panel
  “bound” claims and agent-kit mounted/bound-table claims. Preserve authored
  tables as explicitly recorded proposals. Add a named source-route gap to
  affected data products even when their other publication fields are filled.
  Keep valid independent eventhouse/secondary bindings working.
- Keep saved F-06/readiness feedback unchanged, but conditional SAP must not
  pass current readiness aggregates. The existing `rdStatus`/`readinessShare`
  path must assess process F-06 as open while a route is conditional, even
  when its recorded verdict is done. Label that verdict as recorded beside
  the current gap; do not overwrite notes or add a new readiness framework.
- Fresh derived domain rows retain the existing `fabric_domain` and
  `governance_domain` keys, with current grouping labels
  `Fabric domain (shared business objects)` / `Fabric domain (journey)`.
  Preserve authored/saved domain rows and their old labels by ID; show them
  as recorded, not new Purview creation guidance. Domain assignment is not
  visibility, access or an enforced security boundary.
- Add one derived `current_guidance` object to canon/normalised output with
  `governance` and `sap` entries, each `{text, src}`. It supplies current
  clarification alongside saved architecture/readiness/risk/build blocks,
  without rewriting them or their citations. Include it in HTML and all
  three Markdown downloads as well as Python design/agent/product documents.
  The SAP text names Datasphere → ADLS Gen2 → Fabric/OneLake, snapshot/changes,
  Delta tables and the read-only replicated SQL surface.
- Append six dated canon citations `G59-P1`, `G59-P2`, `G59-P3`, `G59-P5`,
  `G59-P6`, `G59-P7` using the exact titles/URLs and parent-checked
  **2026-11-17** evidence in the approved spec. Preserve S1–S44 identities
  and the canon's older overall `checked` date. Append missing new records
  to detached `sources_doc`; an occupied new ID with different content is
  an explicit collision error before writes, never a retargeted citation.
  Preserve nested internal ancestry when adding public guidance.

## Inspected file map

All paths below are future implementation surfaces, not edits made now.

| Surface | Concrete responsibility |
|---|---|
| `plugin/skills/frontier-process/scripts/seed_ontology.py` | `system_path`, `seed`, CLI copy-back of normalised bindings; avoid `canon["paths"][path]["item"]` manufacturing an item and preserve ancestry on reused sources |
| `plugin/skills/frontier-process/scripts/ontology_lib.py` | `normalize` source defaults, entity binding defaults, domains, product gaps and counts; `to_markdown`, `data_agent_kit`, `data_products_md`; retain existing privacy/feedback helpers |
| `plugin/skills/frontier-process/templates/fabric-iq-canon.json` | Note, SAP rule/path, B1/B7, F-05/F-06/F-14, OD-ONT-3, domains, discovery and dependent risk wording/citations |
| `plugin/skills/frontier-process/scripts/apply_ontology.py` | Existing `apply` preserves readiness statuses; retain recorded verdicts, verify current assessment survives this projection |
| `src/renderer/template.js` | Actual `ontGraph`, `ontPanel`, `ontMarkdown`, `renderOntology`, plus `rdStatus`, `readinessShare`, `renderReadiness`; no separate ontology fragment was found |
| `plugin/skills/frontier-process/examples/caldova-ontology.json` | Current synthetic SAP source currently says mirroring/now; dependent proposals must remain conditional, not invented confirmed entitlement |
| `tests/unit/test_ontology.py` | Existing `Rules`, `Caldova`, `CommonDataModel`, `BuildSafety`, privacy/feedback/wrapper/self-test suites; add focused G59 cases here, not a fictional architecture test module |
| `tests/dom/ontology-preview.test.mjs`, `tests/dom/blueprint.test.mjs`, `tests/e2e/ontology-preview.spec.mjs` | Current/legacy presentation, actual downloads, unchanged routes/feedback, no-FinOps and Python/browser Turtle parity |
| `tools/demo_raster.py`, `tools/build_demo.py`, `tests/unit/test_demo_raster*.py` | Explicit finite profile support and measured identity-input/raster protection; details in Task 9 |
| `tools/selftest.py`, `tests/unit/test_distribution.py` | Existing extracted installer/core checks and privacy guards; extend the former for installed process behaviour, retain the latter unchanged unless a reproduced G59 regression requires an assertion |

Inspection found only valid security/DLP/audit Purview references in
`plugin/skills/frontier-blueprint/templates/blueprint-defaults.json`; preserve
them. No blanket Purview or Synapse Link replacement. No new layout, view,
icon, live call, FinOps operation or extra ordinary-design acknowledgement.

## Task 1: Verify the approved execution boundary and baseline

**Files:** read-only work package, baseline sources and existing tests.

- [ ] After the human approval stop above, confirm cwd/branch/base and record
  `git status --short`, `git branch --show-current`, `git rev-parse HEAD`,
  `git rev-parse "v1.10.0^{commit}"` and `git rev-parse refs/tags/v1.10.0`.
  Match the supplied identities; report missing/mismatched evidence, not a
  fabricated clean checkout. The planning package must be committed and the
  worktree clean; preserve any unexpected edits rather than overwriting them.
- [ ] Use the existing primary virtual environment from this worktree:

  ```powershell
  Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
  $env:PYTHONUTF8 = '1'
  $primary = Join-Path (Split-Path (Get-Location) -Parent) 'frontier-envisioning'
  $env:Path = "$(Join-Path $primary '.venv\Scripts');$env:Path"
  ```

- [ ] Run `python tools/dev.py docs --strict` after parent link integration;
  expect zero errors, not approval verification. Run
  `python -m unittest tests.unit.test_ontology tests.unit.test_demo_raster_110 -v`
  and retain genuine baseline results. Do not install tools, waive failures or
  run a bump merely to escape a baseline mismatch.

## Task 2: Observe RED for SAP selection and normalisation

**File:** `tests/unit/test_ontology.py`.

- [ ] Change `Caldova.test_seed_from_the_blueprint` to assert unresolved/null/
  later plus the five unknown prerequisites for `src-sap-s-4hana`; retain its
  FI/CO, IoT, source ID, pattern and mapping assertions.
- [ ] Add class `ProcessGrounding` with
  `test_sap_name_never_selects_a_route` (S/4HANA, ECC, SAP Datasphere and
  SAP Ariba names), `test_unresolved_source_survives_normalize_twice`, and
  `test_sap_selected_route_requires_estate_evidence`. Use detached Caldova
  fixtures; assert no automatic pipeline or lakehouse substitution. Include
  empty/unsupported path subtests: diagnose them, never default to success.
- [ ] For the positive fixture only, author the selected mirroring/item,
  named synthetic data-owner role and five confirmed note/`src` records
  resolving to explicitly synthetic Blueprint evidence. Assert
  owner-confirmed selection, not deployed/GA/licensed. Negative subtests:
  no assessment, one unknown, unsupported source, public-doc-only evidence,
  malformed status/type, and forged `state`. Complete requirements with an
  unresolved path must still remain unselected.
- [ ] Run
  `python -m unittest tests.unit.test_ontology.Caldova.test_seed_from_the_blueprint tests.unit.test_ontology.ProcessGrounding -v`.
  **RED:** SAP currently becomes mirrored database/next; unresolved
  normalisation warns/defaults to lakehouse/next and has no assessment.
  Capture assertion failures, not import errors.
- [ ] Use these complete focused cases in the existing test module as the
  minimum executable seed/binding contract; keep the additional matrix above:

  ```python
  class ProcessGrounding(unittest.TestCase):
      def test_sap_name_never_selects_a_route(self):
          with tempfile.TemporaryDirectory() as directory:
              root = Path(directory)
              blueprint = normalized_blueprint(root)
              code, result = quiet(seed.main, [
                  "--blueprint", str(blueprint), "--out", str(root / "ontology.json"),
              ])
              self.assertEqual(code, 0, result)
              ontology = json.loads((root / "ontology.json").read_text(encoding="utf-8"))
          sap = next(row for row in ontology["sources"] if row["id"] == "src-sap-s-4hana")
          self.assertEqual((sap["path"], sap["item"], sap["status"]),
                           ("unresolved", None, "later"))
          self.assertEqual(sap["route_assessment"]["state"], "conditional")
          self.assertTrue(all(
              row["status"] == "unknown"
              for row in sap["route_assessment"]["prerequisites"].values()
          ))

      def test_unresolved_source_survives_normalize_twice(self):
          original = mini()
          original["sources"][0].update(path="unresolved", item=None, status="later")
          first = lib.normalize(copy.deepcopy(original))
          second = lib.normalize(copy.deepcopy(first))
          for model in (first, second):
              self.assertIsNone(model["sources"][0]["item"])
              self.assertEqual(model["stats"]["bound"], 0)
              self.assertTrue(all(
                  row["binding"]["item"] is None and row["binding"]["table"] is None
                  for row in model["entity_types"]
              ))
          self.assertEqual(original["sources"][0]["path"], "unresolved")
  ```
- [ ] Add the `ProcessGroundingDistribution` test described in Task 10 now,
  initially asserting SAP unknown state and corrected governance against
  the actual extracted package. Run its RED check immediately after the
  mandatory bump in Task 3, before manual source corrections.

## Task 3: Bump first, then implement the bounded source correction

**Files:** bump-owned carriers; `seed_ontology.py`, `ontology_lib.py`,
`fabric-iq-canon.json` under the exact process paths above.

- [ ] **First approved plugin change:** run
  `python tools/dev.py bump 1.10.1` before any manual plugin edit. Inspect its
  diff: manifests, eight skill metadata versions, `PLUGIN_VERSION`, plugin
  README and new CHANGELOG section only. Do not hand-edit version carriers,
  generated files or released archive dates; no backdated 1.9.3.
- [ ] Run `python -m unittest tests.unit.test_ontology.ProcessGroundingDistribution -v`
  before manual product changes. **RED:** the extracted bumped-but-uncorrected
  package still selects SAP mirroring and recommends retiring governance.
  Save its package digest and failures. Packaging uses the existing generator;
  it does not permit hand-edited install inventories.
- [ ] Add the recognised unresolved path and SAP intercept; build the fixed
  assessment in `seed` using canon text/evidence, including `_todo` owner
  confirmation. A system-name substring, including Datasphere, supplies no
  entitlement proof. Use `carry_content` for every contributing journey,
  including a reused source, not only its first occurrence.
- [ ] In `normalize`, branch before the current `setdefault(item, lakehouse)`
  and status defaults. Validate the checklist and derive its state. Keep
  unknown arbitrary paths diagnostic with no invented item/readiness.
  Preserve legacy selected fields; no promotion from assessment alone.
  Append the six new citation records without replacing existing identities.
- [ ] Re-run Task 2's exact command. **GREEN:** explicit conditional seed and
  second normalisation agree; the positive owner-authored fixture alone
  selects a route. Existing non-SAP rules and supported binding catalogue
  remain unchanged. Keep one bounded SAP check in the existing pipeline,
  not a new route engine or dependency on FinOps validators.

## Task 4: Prevent downstream bindings and publication from masking gaps

**Files:** `tests/unit/test_ontology.py`, process `ontology_lib.py` and
`seed_ontology.py`.

- [ ] Add `ProcessGrounding.test_conditional_sources_do_not_become_bound_or_publishable`.
  Run it alone with `python -m unittest tests.unit.test_ontology.ProcessGrounding.test_conditional_sources_do_not_become_bound_or_publishable -v`.
  **RED:** an entity with a source ID currently receives a plausible default
  silver lakehouse/table, increments `stats.bound`, and does not add a route
  publication gap.
- [ ] Implement the null default binding contract, including seed CLI
  copy-back. Preserve explicit old tables as recorded proposals, but exclude
  them from current bound counts while their route is conditional. Add
  deterministic source-ID-specific gaps to products depending on those
  entities; retain existing owner/access/quality/reference gaps.
- [ ] Cover SAP-only, mixed SAP/non-SAP products and independent eventhouse
  secondary bindings. Re-run the exact selector and
  `python -m unittest tests.unit.test_ontology.CommonDataModel -v`.
  **GREEN:** existing standard mappings, names, 19 product identities and
  eventhouse behaviour survive. Update only affected bound/ready counts and
  SAP-linked binding/gap expectations with explicit reasons; do not delete
  the current Customer/AlarmEvent/domain behavioural assertions.

## Task 5: Correct current canon and derived governance proposals

**Files:** process canon/library and `tests/unit/test_ontology.py`.

- [ ] Add `ProcessGrounding.test_current_governance_is_grouping_not_access`.
  Extend `CommonDataModel.test_domains_and_semantic_models` to require the
  new domain labels while retaining its source/semantic model assertions.
  Check B7/F-14/OD-ONT-3 and current discovery text, retained labels/DLP,
  legacy-estate migration context, no parity claim and domain-not-access text.
- [ ] Run
  `python -m unittest tests.unit.test_ontology.ProcessGrounding.test_current_governance_is_grouping_not_access tests.unit.test_ontology.CommonDataModel.test_domains_and_semantic_models -v`.
  **RED:** current new proposals use Data domain/Functional unit and new
  Unified Catalog setup.
- [ ] Correct the mapped canon surfaces and add `current_guidance`. F-06
  names the conditional SAP route/prerequisites; F-05/F-14 distinguish grouping
  from access and legacy transition gaps. Keep 15 readiness IDs and seven
  existing risk IDs; qualify relevant mitigation text without deleting
  historical source records. Preserve Purview security and F-10.
- [ ] Derive new grouping labels from current canon; Task 6 separately tests
  retention of saved domain rows. Update
  `Canon.test_sources_are_microsoft_learn`: retain original 44 rows, add the
  six specific official citations, narrowly admit the exact P2 blog URL,
  and verify referenced IDs and binding-source invariants. Do not broadly
  allow arbitrary hosts. Re-run the RED command plus
  `python -m unittest tests.unit.test_ontology.Canon tests.unit.test_ontology.CommonDataModel -v`;
  expect current guidance with intact mapping/security semantics.

## Task 6: Prove saved choices and source identities survive current guidance

**Files:** `tests/unit/test_ontology.py`, process `ontology_lib.py`.

- [ ] Add `ProcessGrounding.test_legacy_choices_and_citations_are_not_retargeted`
  and `test_new_citation_collision_fails_without_writes`. Construct a legacy
  `frontier-ontology/1.0` record in the test with SAP mirroring/now, explicit
  bindings, old governance domains, S38/S39 snapshots, readiness verdicts
  and `onto:<id>` feedback; snapshot the input bytes and source rows.
- [ ] Run
  `python -m unittest tests.unit.test_ontology.ProcessGrounding.test_legacy_choices_and_citations_are_not_retargeted tests.unit.test_ontology.ProcessGrounding.test_new_citation_collision_fails_without_writes -v`.
  **RED:** saved domains are still overwritten and a conflicting new citation
  is not yet diagnosed. Keep any already-passing preservation assertions as
  honest regression evidence, not invented failures.
- [ ] Complete the detached preservation/overlay logic. Preserve old sources,
  fields, IDs, notes, verdict evidence and namespace identities; append current
  citations/guidance without reusing S IDs. A conflicting `G59-P*` ID must
  diagnose an error and leave original inputs/good outputs byte-identical.
  Preserve saved domain rows by ID instead of overwriting them.
  Re-run the selectors and
  `python -m unittest tests.unit.test_ontology.FeedbackEdges tests.unit.test_ontology.BlueprintOntologyFeedback tests.unit.test_ontology.OntologyRiskLineage -v`; expect
  stable feedback and current warnings, not silent historical migration.

## Task 7: Test then correct Markdown, HTML and actual downloads

**Files:** `tests/unit/test_ontology.py`, `tests/dom/ontology-preview.test.mjs`,
`tests/dom/blueprint.test.mjs`, `tests/e2e/ontology-preview.spec.mjs`,
process `ontology_lib.py`, `src/renderer/template.js`.

- [ ] Add `ProcessGrounding.test_guidance_agrees_across_python_documents`,
  DOM tests named `G59 current and legacy grounding remain distinct` and
  `G59 conditional route downloads retain guidance and Turtle parity`,
  Blueprint DOM test `G59 saved readiness cannot certify conditional SAP`,
  and browser test `G59 governance and conditional SAP downloads under CSP`.
  Use `openBlueprint(..., {change})` for legacy/unknown/positive DOM variants;
  test actual Blob downloads, not constants or source-text presence alone.
- [ ] Before renderer fixes, build a development-only SVG fixture:
  `python tools/build_demo.py --no-png --out build/g59-dom`.
  Set `$env:BLUEPRINT_HTML = Join-Path (Get-Location) 'build/g59-dom/Frontier Company Blueprint - Template (Caldova sample).html'`;
  run `node --test --test-name-pattern=G59 tests/dom/ontology-preview.test.mjs tests/dom/blueprint.test.mjs`
  and `python -m unittest tests.unit.test_ontology.ProcessGrounding.test_guidance_agrees_across_python_documents -v`.
  **RED:** graph/panel equate source IDs with bound; Markdown still directs
  Purview setup and omits current clarification. With every recorded readiness
  item/feedback marked done, current readiness incorrectly says Yes.
- [ ] Correct `to_markdown`, `data_agent_kit`, `data_products_md`,
  `ontGraph`/`ontPanel`, `ontMarkdown` section lists and `renderOntology`.
  Label old route/table/domain choices as recorded and conditional; show
  prerequisite notes/citations, not `None`, plausible bindings or mounted
  sources. Include current governance/SAP clarification in every Markdown
  variant; keep actual controls separate from grouping.
- [ ] Correct the bounded process F-06 assessment in `rdStatus` and explain
  it in `renderReadiness`; `readinessShare` already uses that effective status.
  Test saved F-06 verdict/feedback byte preservation, current Not yet and
  unchanged non-process readiness. This is not a new approval/control system.
- [ ] Run `python tools/dev.py template`, rebuild the SVG fixture, repeat
  the exact DOM/Python selectors. **GREEN:** JSON/HTML/Markdown/download
  meaning agrees; Python/browser Turtle bytes still match. No new Turtle
  binding/import contract, layout, route, inline handler, unsafe HTML or
  resource request. Remove the temporary `BLUEPRINT_HTML` environment override.
  Run the browser selector after the site regeneration in Task 12.

## Task 8: Exercise privacy, strict warnings and deterministic failure safety

**Files:** `tests/unit/test_ontology.py`, process library only if tests expose
an assessment/guidance ancestry defect.

- [ ] Add `ProcessGrounding.test_assessment_ancestry_survives_projection_and_feedback`
  and `test_route_diagnostics_preserve_good_outputs`. Reuse existing
  `CustomerPrivacy`, `ReviewD1Regressions` and wrapper patterns: nested private
  prerequisite notes/`src`/`content_src`, source/journey ancestry, mixed public
  guidance, retired feedback snapshots and an internal-only binding.
- [ ] Run `python -m unittest tests.unit.test_ontology.ProcessGrounding -v`.
  Observe new failures before any needed privacy/safety fix; existing passing
  guards are regression evidence, not invented RED. Assert no sentinel in
  customer JSON, HTML, Turtle or any Markdown/download; public citations
  must not launder restricted notes or historical verdicts.
- [ ] For unknown/unsupported prerequisites, require a successful ordinary
  conditional draft with named warnings; with `--strict`, require exit 1,
  `files: {}`, no new output directory and no overwritten prior outputs.
  For malformed assessments/citation collisions, require failure even
  without strict. Exercise the seed failure boundary too. Run twice with
  fixed input dates and compare every output byte, including LF.
- [ ] Keep existing pre-write checks; repair only demonstrated assessment
  ancestry/defaulting faults. Run
  `python -m unittest tests.unit.test_ontology.BuildSafety tests.unit.test_ontology.CustomerPrivacy tests.unit.test_ontology.ProcessWrapper tests.unit.test_ontology.ReviewD1Regressions -v`.
  Expect fail-closed projection and original/good-output byte preservation;
  do not introduce wall-clock dates, live calls or sanitisation bypass flags.

## Task 9: Add only the necessary named 1.10.1 raster input profile

**Files:** `tools/demo_raster.py`; new
`tests/fixtures/caldova-raster-1.10.1-inputs.json` and
`tests/unit/test_demo_raster_1101.py`; narrowly affected finite-version
assertions in `tests/unit/test_demo_raster.py`, `test_demo_raster_17.py`,
`test_demo_raster_19.py`, `test_demo_raster_110.py`.

Inspection: `build_demo.py` uses frozen replay only for explicit supported
versions. `demo_raster.py` currently ends at 1.10.0 and requires a versioned,
byte-pinned input record overriding exactly `catalog.html` and
`scripts/identity_docs.py`. A normal 1.10.1 full demo otherwise falls back to
converter-dependent rasterisation. Thus this plan includes one finite profile;
no `build_demo.py` mechanism change is needed.

- [ ] Add `Patch1101Raster` tests using the existing `RasterReplay` temporary
  fixtures: named replay, exact old input hashes, all inventory/input/asset
  tampering failures before PNG writes, malformed/present release authority,
  finished ZIP tampering and rejection of 1.10.2/1.11.0/1.9.3.
  Run `python -m unittest tests.unit.test_demo_raster_1101 -v`.
  **RED:** replay explicitly rejects 1.10.1.
- [ ] Measure the SVG fixture's generated kit: require the same 205 non-raster
  input hashes as the 1.10.0 approved profile (two explicit overrides over
  the frozen base). Require unchanged 223 historical PNG hashes. Stop for
  human scope review on any unexpected identity-input change; do not adjust
  pins, identity runtime code or raster data to force agreement.
- [ ] Create the LF profile with schema
  `frontier-demo-current-inputs/1.0`, version `1.10.1`, unchanged
  `base_profile_sha256` and the measured identical two-input mapping.
  Pin its actual SHA-256 in `demo_raster.py` and add only 1.10.1 to its
  finite map/set. Historical files/pins remain byte-identical.
- [ ] Update only the four exact-set assertions to include this named patch.
  In `Baseline110Raster.test_future_1101_and_unsupported_193_cannot_inherit_support`,
  move the future negative to 1.10.2 and rename the method accordingly.
  Keep 1.9.3 rejected and all 1.10.0 schema/hash/release-authority tests.
  Run `python -m unittest tests.unit.test_demo_raster tests.unit.test_demo_raster_17 tests.unit.test_demo_raster_19 tests.unit.test_demo_raster_192 tests.unit.test_demo_raster_110 tests.unit.test_demo_raster_1101 -v`.
  **GREEN:** finite support with all historical/tamper guards intact, never
  a copied golden ZIP or widened all-version allowance.

## Task 10: Prove installed-package behaviour and core independence

**Files:** `tests/unit/test_ontology.py`, `tools/selftest.py`.

- [ ] Complete the Task 2 class `ProcessGroundingDistribution` and its
  `test_extracted_candidate_runs_corrected_process_without_finops`.
  Build the candidate into a temporary distribution using the existing
  packager, verify `install/prepare_install.py`, and execute the extracted
  seed/build/apply/Blueprint scripts, not working-tree imports. Use
  `sys.executable -E -s -B -X utf8`, a temporary cwd and an environment
  without `PYTHONPATH`/`PYTHONHOME`, as `installed_run` already does.
- [ ] Assert fresh SAP unknown state, current governance, five process
  artefacts, strict-warning no-overwrite, repeated bytes and unchanged input
  bytes. Remove FinOps only inside the verified temporary extraction and
  prove core/process/ordinary value still build; no cost output, licence
  claim, acknowledgement or zero-budget/readiness substitution.
- [ ] Extend the extracted fixture with a legacy SAP/domain/evidence variant
  and private ancestry sentinel. Check preserved IDs/originals, customer
  projection and current guidance. Run
  `python -m unittest tests.unit.test_ontology.ProcessGroundingDistribution -v`.
  **GREEN:** compare with the extracted-package RED observed in Task 3.
  Added legacy/privacy cases are regressions, not fictional new RED results.
  Do not substitute workspace-only tests for extraction proof.
- [ ] Extend `process_checks` and `installed_core_check` in `tools/selftest.py`
  with these focused current/conditional assertions, reusing existing helpers.
  First extend `ProcessSelftest.test_new_selftest_checks_execute_process_behavior`
  to require those executed checks and observe RED, then add them.
  Run `python -m unittest tests.unit.test_ontology.ProcessSelftest tests.unit.test_distribution -v`
  and `python tools/dev.py selftest`; expect installed behaviour and unchanged
  eight-skill/seven-GA/optional-Preview installer/tamper checks.

## Task 11: Update the example and current method/requirements documentation

**Files:** `plugin/skills/frontier-process/SKILL.md`,
`plugin/skills/frontier-process/references/ontology-method.md`,
`plugin/skills/frontier-process/examples/caldova-ontology.json`,
`plugin/skills/frontier-process/scripts/build_ontology.py` (descriptive docstring),
`plugin/skills/frontier-blueprint/references/blueprint-schema.md`,
`plugin/README.md`, `CHANGELOG.md`, `docs/prd.md`, `docs/solution-design.md`.

- [ ] Correct Caldova's current SAP source/intro and affected binding/product
  proposals to the unknown/conditional contract, keeping source/entity/
  product/feedback identities. It must not pretend real prerequisites were
  confirmed. Before changing it, strengthen the existing
  `Caldova.test_example_builds_and_applies` and CommonDataModel assertions
  for its route warning/gaps; observe RED, then update the example.
  Keep exact Employee-warning coverage alongside the new route warnings.
- [ ] Update Step 3 items 3/8, method source/date/legacy/current distinctions,
  read-only route/commercial prerequisite, domain-not-access warning,
  readiness/risk and ordinary draft/strict-handoff instructions. Document
  the additive fields in the schema reference; no schema version change.
  Replace the obsolete setup docstring, not executable behaviour.
- [ ] Add scoped **unreleased planned 1.10.1** requirements/acceptance linked
  to G59-01–08 in PRD and current flow/verification context in solution design.
  Record release/decision context at A.12/A.13 and verification at B.9 by
  adding dated current qualifications/links, not rewriting historical results.
  Preserve old release/approval records and repair only affected current
  local links. ADR-0027's old Purview direction remains historical rationale;
  link its current qualification from solution design, do not erase it or
  mark Proposed ADRs accepted. No new ADR is needed.
- [ ] Complete the bump-created CHANGELOG section and plugin README with the
  two fixes, conditional legacy treatment and unchanged eight-skill maturity.
  Validate prose with `python tools/dev.py docs --strict`; run
  `python -m unittest tests.unit.test_ontology -v` for example/output meaning.
  Record actual results only; no fictional test-first requirement for prose.

## Task 12: Regenerate, verify exact artefacts and return evidence

**Files:** generator-owned outputs only, plus actual verification notes in
`docs/solution-design.md` and the parent-integrated sprint when authorised.

- [ ] Run `python tools/dev.py template package demo docs-demo`.
  Inspect generated template/install inventory, current offline
  `docs/demo/caldova-blueprint.html`, `docs/demo/manifest.json` and generated
  `docs/images/caldova/` captures. `docs-demo` regenerates ten existing views;
  do not hand-edit HTML, screenshots or hashes. The generator's source
  fingerprint includes process sources and raster profiles, so stale tracked
  demo output cannot be left behind. No builders run in this planning turn.
- [ ] Run `node --test tests/dom/ontology-preview.test.mjs tests/dom/blueprint.test.mjs`
  with the normal core/Preview fixtures prepared by `python tools/dev.py dom`.
  Run `python tools/dev.py site`, then
  `node node_modules/@playwright/test/cli.js test tests/e2e/ontology-preview.spec.mjs --grep G59`,
  followed by `python tools/dev.py site e2e --strict`.
  Expect real downloads/CSP, unchanged routes, focus/reflow and no console
  errors. Retain the existing non-acknowledged/acknowledged FinOps regressions;
  technical fixture acknowledgement is not customer consent.
- [ ] Run `python tools/dev.py check --strict`. Expect `ALL GATES PASSED`,
  no optional-tool skips. Run `python tools/dev.py bundle`; repeat package/
  demo generation and compare plugin ZIP and process-output digests and
  identity ZIP bytes. Compare demo HTML only using the existing generated-date
  normalisation. Run Task 10's extracted-package selector again against the
  final generator inputs and bind its returned package digest to the candidate.
  A skipped current-version release comparison is not 1.10.0 reproduction.
- [ ] Verify `git diff --name-status b88b9a2efa1eb342d5542475c63eee5f7bb43e4b`
  and `git diff --check`; confirm no protected records, historical raster
  assets/profiles, original source IDs, raw inputs or editor settings changed.
  Record the exact reviewed candidate identity, focused RED/GREEN output,
  artefact hashes, strict L1/L2 results and outstanding manual checks in B.9/
  sprint evidence, without claiming native Fabric import or release approval.
- [ ] **STOP — human final reproduction/release dependency:** obtain #52's
  exact retained 1.10.0 manifest/archive evidence and source/tag/hash
  comparison before claiming G59-06/final reproduction accepted. Do not force
  the corrected 1.10.1 sources to reproduce 1.10.0 or write protected
  manifests. Missing evidence remains a named release dependency, not a
  passed check. Cowork install/behaviour, tenant prerequisite/licence/import
  checks, human sign-off and publication remain separate.
- [ ] After evidence/document updates, finish with:

  ```text
  python tools/dev.py docs --strict
  python tools/dev.py check
  ```

  Expect zero documentation errors and `ALL GATES PASSED`. If unavailable or
  failing, return exact gaps; never report planned commands as completed.

## Acceptance proof map

| Acceptance | Exact tasks and proof |
|---|---|
| G59-01 | Tasks 5–7, 11: current canon/domain RED→GREEN; saved-estate distinction; Python/DOM/download governance, labels/DLP and no-parity assertions |
| G59-02 | Tasks 2–4, 7: unknown/unsupported/malformed/positive/legacy source fixtures, second normalisation, no item or pipeline fallback; full route/read-only/prerequisite/unpriced text |
| G59-03 | Tasks 4–7, 11–12: grouping-not-access, method/readiness/risk/example coherence, HTML/JSON/Markdown/download checks and actual browser CSP |
| G59-04 | Tasks 6, 8, 10: original-byte/source-ID preservation, citation-collision refusal, legacy choices, retired feedback and restricted ancestry through every export |
| G59-05 | Tasks 10–12: extracted core/ordinary value with FinOps removed, existing decline/no-ack/ack/reload regressions; no automatic cost or licensing claims |
| G59-06 | Tasks 1, 3, 9, 12: supplied immutable identities, bump-first evidence, finite patch profile with historical bytes unchanged; #52 human final acceptance remains explicit |
| G59-07 | Tasks 2–4, 8–10, 12: fixed dates, repeated output bytes, stdlib/offline execution, malformed-input and strict-warning no-create/no-overwrite, isolated extraction |
| G59-08 | Tasks 2–10 focused observed RED/GREEN, then Task 12 regeneration, strict full gates/browser, final package hash/extraction and honest dependency report |

## Planning verification and handoff

The planner inspected AGENTS/path instructions, the complete approved spec,
idea/sprint, PRD A.12/A.13 and process requirements, solution design/B.9,
relevant ADRs, local development/renderer/release skills and the concrete
sources/tests named above. The coordinating assistant is using the available
Superpowers brainstorming/planning workflow. No product implementation or
build/test execution was performed by the planner; those remain the tasks
above, not completed validation results.

The coordinating assistant integrated all eight planning files and validated
them with `python tools/dev.py docs --strict` (zero errors) and whitespace/
placeholder/acceptance-mapping checks; see the linked sprint checkpoint.
Those are planning checks, not implementation results.
**This plan awaits explicit human plan approval and readiness.**
Present two options only: **inline execution** in this existing worktree with
checkpoint evidence, or **subagent-driven execution** for approved bounded
tasks if supported. Where supported, eligible prose may go to `docs-agent`,
checker/code to `frontier-builder` and HTML to `frontier-renderer`; no agents
are created now, and no configured handoff bypasses approval or expands scopes.
Do not commit, push or open a PR as part of this planning handoff.
