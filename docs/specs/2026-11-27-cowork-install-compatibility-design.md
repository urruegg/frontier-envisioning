# Cowork install compatibility design for NEXT 1.11.1

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-27 |
| Author | AI assistant; AI-assisted drafting from the human decisions and supplied engineering evidence |
| Status | Written specification at b9647ea actually approved by later human follow-up; implementation plan Proposed, approval/readiness pending |
| Scope | NEXT 1.11.1 eight-skill install compatibility, lossless Identity source consolidation and bounded routing/metadata corrections; no implementation |
| References | [Catalogue](README.md), [Work item #87](https://github.com/urruegg/frontier-envisioning/issues/87), [Idea](../ideas/2026-11-27-cowork-install-compatibility.md), [Proposed implementation plan](../plans/2026-11-27-cowork-install-compatibility-plan.md), [SPRINT-014](../sprints/SPRINT-014-cowork-install-compatibility.md), [Host receipt #81](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7222569867), [Closeout hub #86](https://github.com/urruegg/frontier-envisioning/issues/86), [PRD](../prd.md), [Solution design](../solution-design.md), [Prior distribution design](2026-11-26-plugin-health-and-finops-exclusion-design.md), [Factory design](2026-11-25-agent-factory-handover-design.md) |

## 1. Outcome, authority and decision evidence

Make the NEXT compatible version, **1.11.1**, fit the observed Cowork install
contract without changing Identity-generated kit contents or weakening existing
validation, financial acknowledgement, privacy or Factory Preview boundaries.
The audience is the maintainer and subsequent specification/engineering review.
Accountable owner: `@urruegg`. Authorship is AI-assisted, not approval.

The user requested Superpowers brainstorming and selected
`source-consolidation-1111` over build-time projection and manual workarounds.
On **27 November 2026**, the user explicitly answered `approve_design=true`
to the install-flow, safety and verification design. This is actual
**conversational design approval**. The later real follow-up
**"true please proceed it's approved from my side"** approved the written
specification at `b9647ea8c824af180cd60975d3f4c4b9e9297e8a` for planning.
The [approval receipt](https://github.com/urruegg/frontier-envisioning/issues/87#issuecomment-7223211793)
records that scope. The new implementation plan remains Proposed and needs
its own explicit approval and readiness evidence.

No code/version bump, independent formal review, owner head sign-off, protected
`approved:*` label, Ready state, release publication or protected #8 execution
follows from either design approval. An implementation plan now exists but is
**not approved for execution**.
The earlier approved [H111 specification](2026-11-26-plugin-health-and-finops-exclusion-design.md),
[H111 plan](../plans/2026-11-26-plugin-health-and-finops-exclusion-plan.md)
and [SPRINT-013](../sprints/SPRINT-013-agent-factory-handover.md) govern their
historical 1.11.0 work, not execution of #87. The PRD and solution design remain
baseline product authority; this document records proposed NEXT behaviour only.

| Option | Decision |
|---|---|
| Canonical source consolidation | Selected: one authoritative shipped tree, with lossless reference/example preservation and explicit fixture-consumer parity. |
| Build-time projection | Rejected: introduces another tree and source/installed-reference divergence instead of fixing the canonical source. |
| Manual repacking or install workarounds | Rejected as the product solution: leaves source limits, path staging and false completion reporting unresolved. Preserve the installed workaround as evidence, not release acceptance. |

## 2. Supplied host evidence and limits

The human-supplied [#81 receipt](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7222569867)
summarises `Frontier Envisioning - identity skill Cowork repack.md`.
The supplied report is **17,031 bytes**, with SHA256
`1ee51d581d786e6246e8b7b22814bf9535995fce69f13eb069cf56a9551f7900`.
It pins the published **1.11.0 ZIP: 782,612 bytes / 93 entries**, SHA256
`22935d1c0197f373ff296fa7550a28626ae3851101d1b05f03bf955236eb11d2`.
These fingerprints are supplied evidence, not recomputed by this drafting agent.
Archive entries are not the per-skill file budget.

- Actual host refusals require all eight whole draft sources at
  `working/<name>` and destinations at `skills/<same name>`. Nested package
  sources were refused without writing.
- Identity had **23 extra files / 24 total**, above the observed recursive
  limit of **20 files besides root `SKILL.md`**. Its old 1.9.2 remained installed.
- Documentation-only consolidation yielded **20 extras / 21 total**.
  Successful host receipt, **21/21 installed equality**, identical **429-file
  Caldova kits** and generated-kit tests are reported human evidence only.
- Structural rescore was **not done**. No fresh all-eight 1.11.1 acceptance,
  routing success, OneDrive sync or native attestation is established here.
- The companion repack ZIP was absent at the report-relative path. No
  downloaded repack script was executed; the original report need not be
  copied into the repository.

Retain historical 1.11.0 fix/publication evidence and the installed workaround.
Older repository records describing the then-unreleased candidate are dated
history, not authority to overwrite published assets. The new package needs
its own evidence; #81 remains open for that acceptance.

## 3. Finite distribution and metadata contract

Carry forward this explicit **1.11.1** inventory, not an all-source or arbitrary
future-version rule:

| Shipped skill | Maturity | Logical optional | Logical requires_preview_ack |
|---|---|---|---|
| `frontier-envisioning` | GA | `false` | `false` |
| `frontier-context-discovery` | GA | `false` | `false` |
| `frontier-blueprint` | GA | `false` | `false` |
| `frontier-solution-design` | GA | `false` | `false` |
| `frontier-agent-identity` | GA | `false` | `false` |
| `frontier-value-case` | GA | `false` | `false` |
| `frontier-process` | GA | `true` | `false` |
| `frontier-agent-factory` | Preview | `true` | `false` |

Seven GA wrappers plus optional Preview Factory ship. The ninth source folder,
`frontier-finops`, and its regressions remain source-only: not registered,
packaged or copied. Older installed FinOps is not automatically uninstalled.

In all eight shipped `SKILL.md` metadata blocks, quote `optional` and
`requires_preview_ack` as `"true"` or `"false"` without changing their logical
meaning. Existing [fe_lib](../../tools/fe_lib.py) and
[installer](../../plugin/install/prepare_install.py) parsers strip quotes and
normalise these values to typed booleans. Generated installer JSON must retain
native booleans, not strings. Preserve GA/Preview/optional and financial
acknowledgement semantics. Factory's `requires_preview_ack=false` means ordinary
non-financial handover needs no cost acknowledgement; it is neither a generic
consent waiver nor a bypass of financial owner review or unavailable helpers.

The current installer special-cases **1.11.0 only**, both in its inventory
helper and preflight. Explicitly support 1.11.1 in those existing mechanisms
and their repository consumers. Reject missing, duplicated, unregistered or
extra shipped skills, including FinOps in a package. Keep the finite retained
source distinction and historical version rules; do not extend exclusions to
arbitrary future versions or merely disable the new-version check.

Only after later approvals and the production protection baseline, bump through
the existing version mechanism **before any approved plugin implementation**.
Use existing template/install generators and a finite raster profile when
required. Never hand-edit generated or old release artefacts, relax historical
205/223 identity/raster checks, or bump solely to bypass reproduction failures.
No bump or generation is performed in this documentation slice.

## 4. Install dataflow, states and errors

Reuse the existing package/installer helpers; do not introduce a generic
framework. Package verification, staged verification, actual installation and
OneDrive sync are separate evidence states.

| Phase | Input and required result | Write boundary |
|---|---|---|
| Read-only package preflight | Explicit extracted root, manifest, generated inventory and original bytes; validate names, versions, typed metadata, finite skill set, paths, recursive counts and every file hash. Read existing installed versions only for comparison. | No package, draft or user-config writes; no save calls on failure. |
| Authorised host staging | After package checks pass, copy exact complete skill bytes to clean whole drafts at `working/<name>`, one per shipped skill. | Actual available authorised host/workspace filesystem capability only; never Python networking or an invented host tool. |
| Read-only staged preflight | Verify all eight staged roots, exact names, complete recursive inventories and hashes against the verified package before any skill-save call. | Reads only; missing, stale, extra, cached or altered staged bytes block every save. |
| Individual host saves | Use verified `working/<name>` to save to `skills/<same name>` through the actual authorised host capability; capture each real receipt. | Whole-draft replacement is scoped only to the explicitly saved skill. No direct user-config deletion or unrelated uninstall. |
| Installed verification | Read actual installed inventory, version and every file hash; compare each skill with its verified staged/package bytes and reconcile its receipt. | Verification is read-only. A save receipt alone is not exact installed equality. |
| Sync and handoff | Record real OneDrive sync evidence and a fresh chat/routing/health receipt against the exact rebuilt ZIP. | No inferred sync, simulated fresh health or native attestation. |

Reject an invalid explicitly requested source root instead of silently falling
back to another root, including the installer's own package location.
There is no template-code execution, downloaded-script execution, network
fallback, silent source substitution or deletion of user configuration.
Staging must not retain old draft files. Changed staged bytes invalidate staged
verification; reverify before saving.

The present `prepare_install.py` emits **“Installed” after read-only package
checks**. Correct the reporting: package checks may report package verified and
staging required, never installation complete. Likewise, `new`, `update` and
`reinstall` comparisons are intended actions, not successful-save outcomes.
Save guidance/calls must refer to verified whole drafts, not nested package
sources. No save is authorised merely because `verified` is true for a package.

| Failure | Required visible result |
|---|---|
| Missing/bad package root, manifest, inventory, file or hash | Explicit phase/path/reason; no staging/save success or installation claim. Preserve existing validation errors. |
| Missing staging capability, wrong draft path/name, extra/cache file, count excess or staged hash mismatch | Explicit capability or expected/actual path/count/hash failure; staged verification fails and no saves occur. |
| Individual host-save refusal/failure | Preserve the old installed skill rather than delete it. Report the failed save and pre-save old version; confirm the retained old version through actual reads where possible. If retention cannot be read, mark current installed state unverified. Other successful saves remain individual outcomes, not full installation. |
| Missing receipt, installed inventory/version/hash mismatch or unavailable installed reads | Report the affected skill as not verified installed; no full-installation claim. |
| Missing OneDrive or fresh host evidence | Report installation verification and sync/host acceptance separately; missing evidence remains outstanding. |

The host's **copied** count includes every draft file, including root `SKILL.md`.
**Skipped** is not an additional count to add to copied. Compare actual inventory
and hashes rather than arithmetic alone. Replacement removes obsolete files
only within the saved skill; it must not delete older FinOps or other skills.
Only actual successful all-eight receipts plus installed equality justify a
full-installation result; OneDrive synced still needs its own evidence.

## 5. Recursive file budget and canonical Identity consolidation

Every shipped skill must have **at most 20 recursive files excluding only its
root `SKILL.md`**. Include files in subfolders and caches in the count. A nested
`SKILL.md` is not exempt. Reject cache and unexpected files even when the count
fits; never silently ignore them. Apply the same checks to source/package
inventory and staged drafts through the existing helpers.

Canonical Identity source changes, not build-time projection:

- Consolidate [identity-method.md](../../plugin/skills/frontier-agent-identity/references/identity-method.md)
  and its sibling notes `brand-discovery.md` and `kit-reference.md`
  into `identity-method.md`, preserving content, anchors and code blocks.
  Remove the two now-redundant notes from the canonical shipped tree.
- Embed the complete fictitious brand example in the consolidated reference.
  Move the literal `examples/caldova-brand.json` to a repository-only fixture,
  preserving its original data. Update the direct
  [tools/selftest.py](../../tools/selftest.py) seed consumer, currently around
  line 656, to read that fixture; do not blindly delete a live input.
- Keep Identity scripts, the kit template and the other two examples
  (`caldova-agent-identity.json`, `caldova-palette.json`) byte-identical.
  Update precise [SKILL links](../../plugin/skills/frontier-agent-identity/SKILL.md)
  to the consolidated sections and use the wording **“other demo examples”**
  for the remaining shipped examples.
- Fixture/source-example parity must preserve all original JSON data and seed
  behaviour. No reset, new synthetic values or golden-output substitution may
  hide a difference. Preserve historical source inventories/approvals and
  immutable releases, not obsolete links into the removed current notes.

Removing two notes and one shipped JSON from the observed 24-file tree gives
**21 total files: root `SKILL.md` plus exactly 20 extras**. That is the Identity
target, not a blanket budget exemption. Source consolidation must not change
generated kit content.

## 6. Factory guardrails and scope routing

Add explicit **When not to use** and **Guardrails** sections to the shipped
Factory procedure, consolidating its existing rules rather than weakening or
duplicating them. Preserve the full reviewed-artifact/pinned-template handover,
privacy and transfer review, financial ancestry/owner refusals, offline producer,
no template execution and no live repository/tenant/deployment boundaries.
Keep Factory optional Preview and core work independent.

| Request scope | Required routing/result |
|---|---|
| Explicit full starter-repository ZIP from reviewed artefacts and a pinned compatible template | Factory, subject to its existing source, sharing and verification gates. |
| Create/refine a PRD, architecture, solution design or ADRs | Solution Design, not automatic Factory export. |
| Vague “set up a repo” | Clarify intent and offline ZIP versus document work; do not invent or perform live setup. |
| Live remote repository, application implementation, tenant provisioning or deployment | Outside Factory's offline handover boundary; no fabricated live setup. |
| Work IQ evidence gathering for an explicit Frontier engagement | Context Discovery within that engagement's evidence/privacy scope. |
| Generic organisation-wide Work IQ request outside a Frontier engagement | Do not capture it merely because “Work IQ” appears; leave it outside the Frontier-specific route. |

Do not edit external `work-iq-sphere`. Preserve the existing Process/Value Case
responsibility boundary and description constraints. Description grep is not
routing success; a real host prompt matrix against the exact rebuilt ZIP must
cover vague and explicit cases, including both Work IQ scopes.

## 7. Acceptance and verification matrix

These seven stable IDs govern later verification, not implementation tasks.
All new-package proofs below remain **required, not run by this drafting agent**.
Reported workaround evidence in section 2 satisfies none of the fresh-package
acceptance by itself.

| ID | Required outcome | Verification evidence |
|---|---|---|
| CWI-01 | Read-only package validation, exact authorised whole-draft staging and read-only staged verification before any save; truthful phase reporting and old-version retention on individual failure. | Actual focused RED/GREEN for invalid/missing explicit root, nested/wrong-name drafts, stale/missing/changed staged bytes, unavailable staging, no premature save/“Installed”, individual failure/receipt handling and installed mismatch; real host receipts for final paths and retained versions. |
| CWI-02 | Recursive maximum 20 extras per shipped skill, excluding only root `SKILL.md`; Identity exactly 21 total; caches/unexpected files refused. | Real 20-positive / 21-negative tests, nested-file and nested-SKILL counting, cache/unexpected-file failures even below the limit, and source/extracted-package/staged inventories. No cache-ignore loophole. |
| CWI-03 | Lossless canonical reference/brand consolidation, direct fixture seed consumer and unchanged Identity scripts/kit/two examples and generated contents. | Content/anchor/code-block and fixture/embedded-original-data parity; byte inventory for unchanged files; generated-kit tests in actual configured outputs, not directly in the unconfigured kit template (which legitimately errors). Original versus consolidated complete 429-file Caldova kit path/byte equality under identical inputs, date and tools; no golden reset. |
| CWI-04 | Quoted metadata preserves all eight skills' typed logical values, maturity, optional and financial acknowledgement boundaries. | Actual RED/GREEN for the shipped frontmatter's quoted-value contract. Existing quoted-value parsing and native installer JSON booleans are already-supported regression checks, not fictional RED. Verify unchanged meanings and Factory optional Preview with no generic/financial bypass; preserve relevant financial provenance, missing-owner-helper and core regressions. |
| CWI-05 | Explicit consolidated Factory exclusions/guardrails and scope-qualified Factory/Solution Design/Context Discovery routing. | Review that no existing control is weakened or duplicated; real vague/explicit host prompt matrix for the routes in section 6, not description grep or a simulated host result. |
| CWI-06 | Explicit finite 1.11.1 eight-skill inventory with source-only FinOps and retained historical policies; authorised bump precedes plugin edits. | RED/GREEN on 1.11.1 installer/repository-helper coverage, missing/duplicate/extra/omitted skills and no arbitrary future exclusions; exact manifest/generated install inventory; original release/source/raster regressions, including unchanged 205/223 checks and finite new profile when required. |
| CWI-07 | Fresh exact-candidate engineering and actual all-eight Cowork/installed/sync/health acceptance, distinct from publication permission. | Strict existing L1/L2, actual extracted-package operation without repository fallback and repeated deterministic package proof; rebuilt ZIP identity; fresh real all-eight saves, exact installed inventory/hash and OneDrive receipt; publish-bar/structural rescore and CWI-05 host matrix against that same ZIP. Preserve advisory warnings and name every unavailable check. |

Use existing tests and helpers, not a new testing framework. Focused failures
must be actually observed RED, then GREEN with relevant regressions.
Generated-kit tests require generated, configured kits. Record exact commands,
results, source/package identities, dates and receipt links when they exist.
Existing L1/L2 or reported human results cannot stand in for rebuilt 1.11.1 proof.
No product builders, tests, dependency installation or host saves run here.

## 8. Boundaries and separate tracks

| Track | Separate responsibility and limit |
|---|---|
| [#8 protected baseline](https://github.com/urruegg/frontier-envisioning/issues/8) | Human-only protected plural session-start route correction and **Active native main** PR/check/freshness/force/deletion protection. Supplied current observation: live main `protected=false`, no rulesets. Actual existing GitHub Actions checks are `L1 quality gate`, `L2 browser tests` and `IaC validation`. Zero formal approving reviews is feasible for the sole maintainer; actual head-qualified maintainer sign-off is separate. No extra account, routine bypass or App is required. The missing baseline blocks new production implementation, not these planning records. |
| [#9 guidance/publication](https://github.com/urruegg/frontier-envisioning/issues/9) | Separate scoped engineering guidance, current publication and adoption records after actual review/clearance. Public visibility or blanket consent does not authorise internal-content publication. Existing internal material/classification remains untouched. |
| [Template foundation](https://github.com/urruegg/frontier-agent-factory) | Supplied complete authenticated release/tag enumeration found none. A human must verify and publish a genuinely compatible stable foundation; never invent stable/GA. Until then preserve explicit exact-commit `unreleased-bootstrap` consent after healthy no-stable discovery. Errors/incompatibility permit no older/main fallback. Template stable does not graduate Factory Preview. |
| [#81 real host acceptance](https://github.com/urruegg/frontier-envisioning/issues/81) | Remains open for final new-package host evidence. Preserve historical 1.11.0 fix/publication and installed workaround; do not overwrite release assets. Link #87 evidence through [#86](https://github.com/urruegg/frontier-envisioning/issues/86), without changing issue state here. |
| [#48](https://github.com/urruegg/frontier-envisioning/issues/48), [#58](https://github.com/urruegg/frontier-envisioning/issues/58) and Caldova | Deferred operating-model/systems work remains separate. No Caldova governance, tenant work or product expansion. |

This planning draft changes only the idea, specification and Draft sprint plus
their three catalogue updates. It does not edit plugin/code/generated or
protected files, settings, dependencies or releases/tags, and does not
distribute/reclassify existing internal material. Planning-branch publication
and issue-intake receipts are separate events, not implementation or release
approval.

## 9. Review and handoff

The written specification at `b9647ea` is approved for planning. The new Proposed
implementation plan needs its own explicit human approval and readiness;
historical plans are context, not substitutes.
No deadline, readiness, independent approval, owner sign-off or completed
product validation is recorded.

The [Draft sprint](../sprints/SPRINT-014-cowork-install-compatibility.md)
records document-validation provenance and now links the new Proposed 1.11.1
plan. The earlier 1.11.0 reference remains dated historical context, not approval
for the new plan. Do not invent a plan or approval to pass a document gate.
Run `python tools\dev.py docs --strict` on the planning records and record its
actual result separately from product verification.

## 10. Later actual written approval and plan reference

The preceding sections preserve the written design reviewed at
`b9647ea8c824af180cd60975d3f4c4b9e9297e8a`, including its then-pending
review/plan statements. Requirements CWI-01–CWI-07 are unchanged.
The later real user follow-up to that written-spec review request was
**“true please proceed it's approved from my side”**. This is actual approval
of the written specification and permission to write the implementation plan.
The earlier unavailable response was not approval. No approval time, label
change, readiness, implementation or protected permission is inferred.

The [new implementation plan](../plans/2026-11-27-cowork-install-compatibility-plan.md)
is **Proposed**, pending separate explicit human plan approval and readiness.
It replaces historical H111 context only for proposed NEW #87 execution;
H111's original scope/evidence remain intact. SPRINT-014 remains Draft/not Ready.
Human #8 protected plural routing/native main baseline still blocks production.
This record supersedes only earlier pending-written-review/no-new-plan status
statements, not the approved design content or evidence limits.
