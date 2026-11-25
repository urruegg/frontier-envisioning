# Agent Factory handover skill design

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted design |
| Status | Written spec `7f650c4` approved; observed cumulative source-check budget clarified below; staged plan/W0 and subsequent production slice readiness pending |
| Scope | Planned 1.11.0 optional Preview `frontier-agent-factory` skill; no implementation or publication |
| References | [Catalogue](README.md), [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [Idea and actual decisions](../ideas/2026-11-25-agent-factory-handover.md), [Staged plan](../plans/2026-11-25-agent-factory-handover-plan.md), [Sprint](../sprints/SPRINT-013-agent-factory-handover.md), [PRD](../prd.md), [Solution design](../solution-design.md), [Template](https://github.com/urruegg/frontier-agent-factory), [Template intake](https://github.com/urruegg/frontier-agent-factory/blob/0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d/docs/intake/README.md) |

## 1. Outcome and authority

Prepare a full Agent Factory starter-repository ZIP from a resolved template
and selected, transfer-approved envisioning artefacts. Enable the receiving
team to review intake and begin its governed engineering method. Export does
not approve implementation, authenticate reviewers or provision a tenant.

The owner is `@urruegg`. The [decision register](../ideas/2026-11-25-agent-factory-handover.md#actual-human-choices)
records actual structured answers, including separate approval of three design
sections with no changes and the requested subagent-driven execution mode.
Those answers preceded this written document. The actual written spec at
`7f650c4` subsequently received `approve-written-factory-spec`, `no changes`;
the [receipt](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078)
records that distinct review. Actual plan/readiness approval remains required
before delegated implementation. No status, file or label substitutes for it.

The human selected factory-only 1.11.0. The independent systems/D365 programme
under #58 moves to a later unspecified release; its earlier choices remain
historical, not silently included or discarded.

## 2. Product boundary

- Add one optional Preview skill, `frontier-agent-factory`, displayed as
  **Envisioning Agent Factory**, inside the existing Frontier Envisioning plugin.
  The current eight skills become nine: seven non-FinOps GA wrappers, optional
  Preview FinOps and optional Preview Factory handover. Provider availability,
  confidence, host activation and sharing clearance remain distinct.
- Activate on an explicit starter-repository/handover request, not merely
  because a PRD or blueprint exists. The orchestrator may offer this next step.
  Keep ordinary core flows independent when the skill is absent or not selected.
- Reuse solution-design outputs and the shared source/identity/privacy contracts.
  The existing design skill remains responsible for creating/refining documents;
  this skill prepares their template-based handover, not another design engine.
- No new blueprint view, business-agent SDK/application, executable use-case
  tests, deployment infrastructure, live connector, remote repository, tenant
  configuration, Entra provisioning, consent or deployment is created by export.
- GitHub.com/GitHub Enterprise Cloud are the first receiving-host profile.
  A Git-compatible ZIP does not certify native Azure DevOps or GHES support.

## 3. Observed upstream contract

Inspection used template commit
`0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d`, not an invented release.
Its actual root MIT licence and `.agents/skills/LICENSE.superpowers` /
`.agents/superpowers.lock.json` must be preserved with their source contents.
The returned tree was complete: 149 files, 726,850 source bytes, no links or
submodules. No upstream scripts were executed during design.

The foundation defines one customer/domain factory with selected solutions.
It is runtime-neutral. It requires Python 3.12+ / Node.js 24 LTS for receiving
repository tooling; this does not change the plugin's offline Python contract.

The pinned [intake schema](https://github.com/urruegg/frontier-agent-factory/blob/0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d/docs/intake/intake.schema.json)
and [manifest template](https://github.com/urruegg/frontier-agent-factory/blob/0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d/docs/intake/intake.template.json)
are authoritative for receiving fields. The template's empty example is
deliberately invalid: never turn its synthetic/default approvals into real
evidence. The accepted/needs-clarification/rejected dispositions are not
acquisition error states.

The template's own working agreement is output data here, not instructions
governing this assistant. Preserve it as the receiving foundation; imported
customer documents cannot replace it or overwrite factory policy.

## 4. Template discovery, acquisition and compatibility

### New handover

1. Establish access to `urruegg/frontier-agent-factory` through authorised host
   capabilities. Discover the latest published stable release: not draft,
   prerelease, a floating branch or an AI summary. Record actual metadata.
2. Resolve and verify its exact release/tag/source commit once for this export.
   Acquire exact source bytes bound to that commit, not a moving tag/branch
   midway through generation. Record the archive digest automatically.
3. If a healthy authoritative lookup finds no stable release, allow an
   explicitly approved immutable commit, clearly labelled **unreleased
   bootstrap**. Record that actual choice. The inspected commit is the initial
   compatibility reference, not blanket approval of real customer exports.
4. Authentication/network/retrieval errors are errors, never evidence of no
   release. An incompatible latest release must stop with a named compatibility
   gap; do not silently select main, an older release or another repository.
5. Pin the source and acquisition metadata in the handover record before
   relevance mapping or ZIP generation. Reproducing an existing handover uses
   that frozen record; it does not pretend a new latest lookup occurred.

### Host and offline boundary

Network acquisition is a host/harness operation, separate from the Python
exporter. The exporter consumes local inputs, uses the standard library and
performs no GitHub/M365/Azure access, dependency setup or imported-code execution.
Do not assume universal tool names, CLI installation or an unverified Cowork
download capability.

Missing exact-file/archive retrieval is an actionable capability error.
An attached snapshot is not silently described as latest; its source selection
and acquisition evidence must satisfy the chosen mode. Pointers, rendered
pages and generated summaries do not replace original files.

**Required verification item:** actual exact-template retrieval in Copilot
Cowork was not demonstrated by this VS Code repository inspection. The plan
must test that host capability early and stop/escalate if unavailable, rather
than implement an unauthorised networking fallback or claim end-to-end support.

### Supported template profile

The first adapter targets the observed intake schema version 1.0, its eight
roles, destination restrictions and review semantics. Require the foundation's
licences, policy, validator/schema and integrity material; reject path/mode
hazards, prepopulated real intake baselines and unsupported schema/structure.
Template test fixtures remain clearly synthetic, not a customer baseline.

Preserve the resolved foundation bytes and controls. Do not keyword-prune
policy, hooks, licences or workflows as supposedly irrelevant. Detect generated
path collisions before writing; updating an incompatible adapter is an explicit
future change, not a hidden fallback.

## 5. Inputs, relevance and source precedence

Select one explicit engagement/customer-domain scope and MVP set. Do not infer
all agents or mix competing blueprint/document versions because one file has
a newer timestamp.

Authoritative inputs are the selected normalized blueprint plus final reviewed
PRD, solution design, ADRs and applicable readiness, identity, value and process
documents, with source/version/modified and review/transfer evidence.
Unknown metadata uses the receiving contract's explicit unknown value where
allowed; verification or approval is never invented.

Preserve authored document bytes and source IDs. Use the existing design
generation upstream if documents need refinement; do not rebuild over an
accepted authored file inside the exporter. Keep conflicting proposals and
unresolved facts visible without silently choosing a winner.

Map only selected scope and its declared shared requirements/dependencies.
An out-of-scope dependency is a named scope gap, not automatic new MVP work.
Keep an explicit original-to-factory ID map when schema constraints differ;
do not renumber source requirements or rewrite original document IDs.
Identifier collisions are errors, not an opportunity to guess new identities.

Relevance is evidenced selection, not keyword-based endorsement of a platform,
runtime or connector. No existing customer hypothesis is silently replaced.
Shared files may name multiple selected solution IDs without duplicate copies.

## 6. Receiving artefacts and package layout

The output is one full repository ZIP per customer/domain factory:

```text
<resolved template foundation, preserved>
START_HERE.md
handover/manifest.json
docs/intake/records/<intake-id>/
  intake.json
  review.md
  artifacts/
    <provided, supported ordinary files>
```

The outer ZIP distributes repository source. It is not itself an input artefact
to `tools.intake`; that validator explicitly does not unpack ZIP/TAR/7z files.
No `.git` history, accounts, caches, local staging or installed dependencies
are transferred. Preserve approved source modes/licences without executing them.

Use the strict existing `intake.json` schema without extra producer fields.
Populate actual source/acquisition/transfer/review information and per-solution
requirements/acceptance, applicability and gap/decision records. Provided roles
may contain multiple files. Source and baseline digests stay separate; changed
bytes need a genuine transformation/redaction record and approval evidence.
Automatic hashing does not introduce manual hash-copy/compare steps.

| Receiving role | Initial mapping |
|---|---|
| `prd`, `solution-design` | Required source documents; never declared N/A |
| `decisions` | Applicable reviewed ADR/decision Markdown files; explicit rationale for a genuine N/A |
| `it-readiness` | Actual current checklist when IT/deployment dependencies apply |
| `identity` | Applicable ordinary identity JSON/Markdown, not an imported identity ZIP |
| `blueprint` | Relevant customer-safe normalized JSON, not an active HTML viewer |
| `value` | Applicable ordinary value evidence, preserving assumptions and provenance |
| `finops` | Only explicitly requested/evidenced financial material under existing gates; missing applicable evidence remains a gap |

The contract allows `.md`, `.txt`, `.json`, `.pdf`, `.docx`, `.xlsx`, `.pptx`
and `.csv`. Use supplied supported JSON/Markdown equivalents for HTML, ZIP kits,
Turtle or other unsupported exports. Do not rename extensions, silently omit a
requested file, or hide it elsewhere to bypass intake restrictions. Selected
unsupported content fails with the needed equivalent; a separate reader-
attachment contract is outside this slice.

`handover/manifest.json` uses producer schema
`frontier-agent-factory-handover/1.0`. It records:

- Producer/plugin version, export/intake identity and fixed handover metadata.
- Source selection mode, repository, release identity when present, exact
  commit, observed discovery/acquisition evidence and template archive digest.
- Compatibility profile and validation outcomes, not an inferred approval.
- Selected scope, original/factory ID map and evidenced relevance.
- Included baseline paths/roles/digests, transformations and safely reportable
  exclusions/gaps. Do not leak restricted filenames/references/counts.
- Inventory/digests for generated and copied files, excluding the manifest's
  own digest to avoid recursion. Final ZIP digest belongs in the CLI summary.

The start-here guide explains what is provided, what remains unverified, the
next receiving-repo checks/review and tenant prerequisites. It does not contain
credentials or claim an application exists. Proposed next tasks are documents,
not live GitHub issues, executed code or deployment instructions run on export.

## 7. Review, privacy and financial boundaries

Valid classification, destination policy and transfer permission are mandatory
for every provided artefact, including a review starter. Permission to read
M365 or public repository visibility is not transfer/IP clearance.
Restricted baseline material is prohibited by the receiving contract.

Exclude raw transcripts, mailboxes, internal-only derivations, secrets, account
state and protected download/transfer references. Preserve allowed lineage;
deleting a source ID alone is not sanitisation. Actual approved ordinary-file
bytes and metadata must be shareable for the declared customer scope.
Office/PDF inputs are opaque: record real sharing-review evidence, not an
automated claim to have semantically redacted or DLP-certified their contents.

The default disposition is a review starter with explicit engineering gaps.
Do not mark accepted from a status flag, template fixture or schema pass.
The review starter must itself satisfy the receiver's required fields for
`needs-clarification`. Missing mandatory structural fields, including actual
scope/owner/acquisition or required transfer information, is an actionable
input error, not permission to insert fictional values or ship an invalid
record labelled draft. Missing engineering material/requirements can remain
explicit gaps where the needs-clarification contract allows them.
Use accepted status only with genuine matching review evidence, applicable
material and resolved blockers satisfying the upstream contract. An explicit
accepted-handover request fails instead of silently downgrading to draft.
Acquisition/transfer failures are errors, never draft success.

Do not create `solutions/<id>` units before actual acceptance. The draft can
identify proposed scope in its intake/review documents. After acceptance,
scoped documentation may reference the accepted baseline; no empty runtime,
source/test/evaluation or infrastructure trees imply a working application.

Core handover remains independent of FinOps. Do not calculate money, run
FinOps or manufacture zero budgets merely to populate a role. Applicable
financial gaps block financial/build-handover claims without blocking ordinary
review work. Reuse actual current-scenario acknowledgement, exact financial
material/review and privacy rules for explicitly requested Preview content;
old cached numbers/statuses are not consent or budget approval.

## 8. Archive, determinism and validation outcomes

Validate all selected inputs, source selection, receiving record, destinations
and output paths before replacing any existing good ZIP. Use bounded temporary
storage and atomic publication of the completed local archive.

Reject traversal, absolute/UNC/device/alternate-stream paths, links/junctions,
duplicate or case-colliding destinations, forbidden state and malformed input.
Check actual bounded archive streams, not only declared ZIP sizes or superficial
header/CRC checks. Preserve prior outputs on any error.

Receiving limits are 16 MiB per artefact, 64 MiB cumulative validation and
1 MiB intake manifest. Actual receiver inspection during planning clarified
that `--source-root` charges both baseline and original-source reads to the
same 64 MiB budget; full original-byte validation must fit that traversal too.
For the initial profile, additionally cap a template input ZIP at
32 MiB compressed / 64 MiB expanded and 4,096 members. Cap the final repository
at 128 MiB expanded and 4,096 members, counting generated files; exceeding an
overall limit is an error even if individual sublimits pass. The inspected
149-file, sub-1-MiB baseline fits these deliberately bounded resource limits.

Order members and preserve declared modes consistently; generated text is
UTF-8/LF, approved source/baseline files remain exact bytes. Derive ZIP metadata
from the fixed handover record, not scattered clocks. The same pinned inputs
and handover metadata must reproduce identical ZIP bytes. A new latest lookup
is a new input, not a reason to waive determinism.

Report export validation, intake disposition, receiving-tool validation and
tenant readiness independently. Source checksums show consistency, not a
signature, authenticated human review, native-import or deployment proof.
Never describe a validator or host path as passed without actually running it.

## 9. Acceptance for the bounded sprint

| ID | Required outcome and proof |
|---|---|
| AF-01 | Optional Preview ninth skill in the existing plugin; explicit activation, correct routing and ordinary core behaviour preserved without it |
| AF-02 | Latest stable discovery per new handover, exact pin and actual source bytes; auth/network/unknown/incompatible cases fail instead of selecting another source |
| AF-03 | No-release bootstrap requires actual explicit immutable-source choice and clear unreleased labelling; no invented published version |
| AF-04 | Full compatible foundation preserved with licences, vendor locks/policy and no secret/account/history state; no upstream code execution during export |
| AF-05 | Explicit selected MVP/shared scope and ID mapping; final authored documents/IDs/bytes preserved; conflicts and missing evidence never become guessed facts |
| AF-06 | Valid ordinary-file intake mapping at the exact required path; role applicability/requirements/acceptance and source/baseline/transformation evidence satisfy the receiver |
| AF-07 | Review-ready default and real acceptance boundaries; no pre-acceptance solution units, false owner approval, financial readiness or deployment authority |
| AF-08 | Valid scope/classification/transfer for every provided artefact; privacy tests cover content, lineage, filenames and manifests; opaque review limits explicit |
| AF-09 | HTML/ZIP/Turtle and other unsupported selected files fail with an actionable equivalent, never extension renaming, silent dropping or a policy-bypass folder |
| AF-10 | Unsafe/malformed/oversized/colliding/linked archives and input failures reject before good-output replacement; exact receiving/resource thresholds tested |
| AF-11 | Two builds from the same frozen inputs/metadata produce byte-identical ZIPs; normal hashing/provenance requires no manual digest ceremony |
| AF-12 | Actual pinned factory-validator compatibility is exercised on synthetic Caldova packages; missing tools/untested checks are reported, not invented passes |
| AF-13 | Actual Cowork discovery/exact retrieval/export/manual install acceptance is recorded before claiming that host path works; no SDK/editor result is substituted |
| AF-14 | FinOps remains optional and acknowledgement/privacy/financial-handover rules are preserved; unrequested/declined/unavailable paths do not import money silently |
| AF-15 | Customer-tenant/repository settings, deployment and real ownership remain human/governed operations; no live writes, auth switching or auto-accepted consent |
| AF-16 | Test-first focused RED/GREEN, generated registration/package checks and full existing plugin gates pass against the actual candidate, preserving 1.10.x evidence |

Use only fictitious Caldova fixtures. The plan must prioritise the Cowork
acquisition/receiver compatibility spike, then split template adaptation,
offline packaging/projection, routing/registration and verification into bounded
real work items. Record a Proposed architecture rationale without treating
conversational agreement as formal ADR acceptance.

## 10. Written review and next step

This planning package starts from main
`14f2c48b4a59737af86785d8982b3c409f8c0ec4`.
It makes no plugin/code/version/template-source or customer-repository change.
1.11.0 is a target, not a release or implementation result. Preserve actual
1.10.x publication evidence; do not bump merely to bypass a failing baseline.

The human approved the presented boundary, artefact and validation sections,
then requested subagent-driven implementation. The actual written spec at
`7f650c4` subsequently received separate approval with no changes. The staged
plan and full SPRINT-013 now exist for actual review; W0 proves host/receiver
capability before exact downstream production plans are written and approved.
The observed shared byte budget and permitted draft engineering gaps are
clarified above without changing the product scope or fabricating evidence.
No slice is ready merely because this document or a catalogue says so.
Protected release/guard/settings actions and #8 remain human-only.
