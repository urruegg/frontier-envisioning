# SPRINT-004: 1.9 intake and optional Preview FinOps

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-11 |
| Author | Copilot SDK in VS Code; AI-assisted sprint planning and evidence maintenance |
| Status | Design/plan approved; D0–D4 SPEC/QUALITY clear; D5 local technical verification complete, PR/CI handoff pending |
| Scope | Unreleased private 1.9.1 engineering evidence: process/ontology intake, seven GA skills and acknowledged optional Preview FinOps |
| References | [Catalogue](README.md), [Parent #25](https://github.com/urruegg/frontier-envisioning/issues/25), [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md), [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md), [Plan](../plans/2026-11-11-handover-1.9-preview-finops-plan.md), [Receipt](../intake/handover-1.9.0.md) |

## Outcome and work items

Keep the received process improvements while making FinOps genuinely optional
and Preview, with actual awareness before operations/figures and no hidden
dependency of the GA core. Product maturity is separate from provider Preview,
mapping confidence, release, deployment and external clearance.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#25](https://github.com/urruegg/frontier-envisioning/issues/25) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D0-D5](../plans/2026-11-11-handover-1.9-preview-finops-plan.md) | `@urruegg`; parent coordinator | Actual written-plan approval recorded | D0–D4 clear/committed; D5 local technical verification complete, PR/CI handoff pending | D4 `afd6cd4`; canonical `d614979`: strict L1/L2 exit 0; final C1/C2 handoff in [receipt](../intake/handover-1.9.0.md#final-canonical-handoff) |
| [#28 process](https://github.com/urruegg/frontier-envisioning/issues/28) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D1](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d1-process-models-and-deterministic-artifacts) | `@urruegg`; bounded builder | D0 and plan approval | SPEC PASS / QUALITY CLEAR returned | `f5e08f2`; local process/privacy/determinism evidence, not tenant import |
| [#26 FinOps](https://github.com/urruegg/frontier-envisioning/issues/26) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D2](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d2-operational-finops-preview-gating) | `@urruegg`; bounded builder | D1; single wrapper writer | SPEC PASS / QUALITY CLEAR returned | `d763833`; operational acknowledgement/lazy-core/provenance checks, not human pricing approval |
| [#27 renderer](https://github.com/urruegg/frontier-envisioning/issues/27) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D3](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d3-ontology-and-preview-aware-ui) | `@urruegg`; bounded renderer | D1-D2 and built fixtures | SPEC PASS / QUALITY CLEAR returned | `c64a815`: historical 75 DOM/61 browser; `4cb4d4e` measured controls; `d614979`: 67 browser, bounded 32-state Preview matrix, not AT certification |

## Approval and readiness

At `2026-11-11T10:29:30.009+01:00` the maintainer specified the optional Preview
FinOps/non-GA grounding and model boundary, and GA status for the other skills.
After the proposal, at `2026-11-11T11:02:02.033+01:00`:

> design is approved and you can proceed

Actual approval is recorded on #25 and in the linked idea. The earlier unavailable
form did not grant approval; this later instruction approves the design direction.
The new written plan did not exist then; its later separate approval is recorded
below and on #25.

- [x] Real parent and child issues, owner, sample data and affected paths defined.
- [x] Source version 1.9.0 / 279-file fingerprint identified and unchanged.
- [x] Bundled-but-gated design direction and product-maturity boundaries approved.
- [x] Per-invocation/scenario acknowledgement and default/Preview modes explicit
  in the plan for review; no cached/global consent.
- [x] After the written plan was presented, the maintainer explicitly stated
  "okay the plan is approved please implement it sub agent driven now".
  This is recorded on #25; the earlier unavailable form is not the approval.
- [ ] Human label state checked separately if applied; no agent mutation.

## Evidence and constraints

Pre-intake main baseline: `907c3ca5d1ce94ca479ec7c9a3887187574cc0f4`, 1.7.1.
Received path/hash inventory:
`904538ec9930aad2d3aa5e8067023f4a7230d46a5696faef7836896b444a01e9`.
The original comparison has 214 unchanged, 48 changed and seventeen new files
against the 1.7 receipt. The wrapper guide remains historical 1.7 context.

The preceding intake analysis checked static syntax and limited redacted hygiene,
not incoming runtime correctness. Its 1.7.1 results remain baseline evidence;
the later implementation evidence below is separately qualified.

## Returned implementation evidence — 11 November 2026 (+01:00)

The parent supplied these results. This D5 record-only update follows committed
D4 `afd6cd4`; it is not new product prose. The prose worker used file reads and
patches, with no terminal/runtime execution, nested agents or validation runs.
Checked source: canonical `d614979` on `feat/25-handover191`; 1.9.1 remains
unreleased and private. These two evidence records are excluded from both ZIPs;
no packaged input is changed. See the
[receipt](../intake/handover-1.9.0.md#d5-final-local-technical-evidence) for final
measurements and the
[design verification](../solution-design.md#191-development-intake) for the
earlier architecture/profile checkpoint.
This is a source-qualified verification checkpoint, not a live PR tracker.
Use the PR linked from [parent #25](https://github.com/urruegg/frontier-envisioning/issues/25)
for current CI and maintainer-review status.

| Stage | Commit/evidence | Qualification |
|---|---|---|
| D0 | `e7e4db5`: 279-file receipt with digest above; 241 protected/fixture hashes unchanged at last verification | Original received/release/profile evidence preserved, not new publication verification |
| D1 | `f5e08f2`: 111 tests/398 subtests; 27 entities, 33 relationships, 126 properties, nine sources, four data agents/four semantic models; 18 data plus one knowledge product | Five outputs deterministic under four hash seeds; strict pre-write/customer privacy tested; six mappings to verify and Employee binding gap remain |
| D2 | `d763833`: 81 D2 tests/508 subtests; combined 197/906 | Fresh acknowledgement, lazy core, cache/provenance, private-component/selection matrix and named-variable fingerprint checks; no formal/human pricing approval |
| D3 | `c64a815`: 75 DOM/61 browser reported on frozen source; independent review 16 new DOM/two hosted checks plus 31 old DOM/three Turtle variations | Byte parity/determinism, real CSP/axe, no new WCAG waiver; four light/dark 1440/320 screenshots reported; not exhaustive Preview AA or manual AT certification |
| Parent pre-D4 L1 | At `c64a815`, `python tools/dev.py check --strict` ended `ALL GATES PASSED`: 394 tests, one expected unreleased-manifest skip, 1337 subtests, 48 self-tests, 75 DOM; six existing ESLint warnings, zero errors | Before prose edits, not final post-doc L1/L2 |
| Parent runner | `ecdfdc8` / `e61bc6a`: 39 tools/site tests/four subtests pass, HTTP 200/CSP verified and helper stopped | DOM explicit technical-ack Preview fixture and isolated core/Preview browser site with real hashed CSP; normal site stays core |
| Candidate before D4 (historical) | Eight verified copy plans, seven GA/one optional Preview, fifteen complete entries, nested guard clear and matching embedded bytes | Measured before the new process reference; superseded by final D5 handoff below |
| D4 | `afd6cd4`: SPEC PASS / QUALITY CLEAR; all D0–D4 clear and committed | Four document-only A–D scenarios: six baseline gaps → GREEN after D4; not live Cowork routing validation |
| Final L1 | `d614979`: `python tools/dev.py check --strict`, `ALL GATES PASSED`, exit 0; 399 unit/pipeline tests passed, one expected unreleased-manifest skip, 1440 subtests passed, 48 self-test checks, 75 DOM tests | 586 repository files/zero errors; docs zero errors; neutrality zero findings; Ruff pass; ESLint zero errors/six existing warnings. Ignored summary: `build/evidence/final-l1.log`. Pre-canonical 398/1349 proof is superseded |
| Final L2 | `d614979`: `python tools/dev.py site e2e --strict`, `ALL GATES PASSED`, exit 0; 67 browser tests passed | Actual real-CSP core/Preview routes; 32 unique Preview axe/layout states and 168 other logged core/identity axe states, with qualifications below; local, not CI |
| Final bounded review | `74251a45`: no Critical/Important/Minor integration-contract findings | Final C2/gate proof supplied; review closure turn pending; advisory, not human sign-off |

Parent reports the full 205 verified identity inputs/223 PNGs for core and explicit
Preview profiles; both actual A6 ZIPs have SHA-256
`e40b132d2e1d396ad7ee681d09931b3e35cd5728081cb01235b17396059cfdf9`.
The finite current 1.9.1 profile pin is
`d91044f03bb34f6559eddc8debf035a5d3aa697d7800d723a700528b23004453`;
original profile/assets remain unchanged, with no golden/profile broadening.
All 241 original protected/fixture files and five pre-existing intake JSON files
are byte-unchanged; the actual 279 received paths/hashes match the frozen
inventory above.

### D4 document-only reference/pressure closure

Before editing, the parent ran four read-only scenarios A–D at `c64a815`.
Actual documents contradicted maturity metadata: unconditional orchestration/
value dependency, absent decline/missing-module branches, missing full notice/
scenario confirmation/flag examples/standalone apply, stale GA/JSON consent and
downstream Preview handling, missing process method/optional routing.
The simulated assistant safely flagged these gaps rather than inventing flags;
it did not execute unsafe operations. This is RED reference/behavioural evidence,
not live Cowork validation.

D4 prose addressed those paths in all eight skills and relevant references,
root/plugin guides, bounded product sections, Proposed process/CDM ADRs and
catalogues. The exact notice/flag/API default, renewed scenario acknowledgement,
clean declined core/legacy handling, independent viewer gate and provenance are
documented. Parent returned GREEN for all four A–D scenarios after D4, closing
the six baseline gaps. The flag is upstream FinOps acknowledgement, not a
scaffold CLI flag; stale labels cannot pass F1, and the scaffold does not
automatically generate financial tables. No actual Cowork installation,
live routing validation or Fabric import is claimed.

### D5 measured accessibility and shared controls

The final 32 unique Preview states cover four views × before/after genuine
acknowledgement × light/dark × 1440/320 widths: zero applicable WCAG violations,
undersized controls, document overflow or bad local scroll. The other 168 logged
core/identity axe states had zero WCAG findings. This is not all possible AA
coverage; colour-contrast incompletes/manual AT remain unproven.

The measured target regression went from 20/32 bad states RED to 0/32:
radio/`ucag` 24 × 24 CSS px, labels/agent links at least 24, mobile bubble at
least 27.9 through bounded local scroll. Labels/groups are unique; shared
widgets reflect one feedback key without DOM rerender/caret loss, and hidden
numeric inputs stay hidden. Two focused RED → GREEN checks plus the parent's
independent six-browser-test/32-state run and eight post-fix screenshots support
the fix. Evidence is under `build/evidence/d5-preview-target-{red,green}/` and
`build/evidence/d5-shared-assumption-{red,green}/`. Manual checks are not waived.

### D5 canonical handoff and offline preparation

C1 isolated package/core build, independent full-L1 core deletion/rebuild and
C2 package/complete/checksum rebuild yielded identical hashes/sizes for all
three files. The exact three-file `dist/distribution-1.9.1` inventory, byte
sizes and final SHA-256 values are in the
[canonical handoff receipt](../intake/handover-1.9.0.md#final-canonical-handoff).
The plugin has 93 entries, all raw-byte equal to working source and Git HEAD
`d614979`: eight skills, 85 skill files, seven GA/one optional Preview.
The complete bundle has exactly fifteen allowlisted entries including four
ontology documents; embedded plugin/docs/core HTML/identity catalogue and ZIP
match actual outputs. Explicit Preview demo/JSON, analysis, intake and arbitrary
sources are excluded. Both archives passed defined whole/nested privacy scans,
checksum-content and fixed-date/Unix-metadata checks, not exhaustive secret/IP
clearance or external publication permission.

Actual final-ZIP read-only install preparation returned `verified=true`,
no problems and eight new clean-target plans. Legacy 1.7.1 seven-skill/
forged-GA/cached-ack simulation returned seven updates plus new process,
eight plans/85 files, seven GA/one optional acknowledgement-required Preview.
No implicit acknowledgement/cost call, no actual copies and no existing
temporary-file changes occurred. Separate two-version update/reinstall unit
checks passed; no real OneDrive/Cowork installation occurred.

The parent corrected an initial archive-root manifest mapping assumption, then
observed two real source-LF RED checks: two new physical CRLF working files
(FinOps guard, 412 lines; process method, 133) differed from committed LF.
Only those named files were normalised to already-committed bytes; two generated
inventory hashes and regression evidence were corrected in `d614979`.
The [receipt](../intake/handover-1.9.0.md#preserved-inputs-and-verification-correction)
names the files. No semantic change or historical asset rewrite occurred;
earlier Windows-only ZIP hashes are superseded. Legacy regression `8208155`
and measured controls `4cb4d4e` precede this canonical head.

### Remaining record/PR/CI handoff and human checks

- Parent owns post-record strict docs/header/local-link/traceability and
  product-contract checks, unchanged handoff-hash verification, the record
  commit, feature-only push, draft PR creation and new-head CI checks.
  These post-record checks were not run by this prose worker.
- Bounded integration review closed the actual C2/gate proof with technical
  CLEAR at `d614979`, with no Critical, Important or Minor findings.
  No draft PR number/link is known. D5 is locally technically verified,
  not fully closed, merged, published or released.
- Sole-maintainer sign-off against the final head remains pending, not formal
  self-approval. Human label state is not inferred.
- Live Cowork validators/behavioural prompts, native Fabric import/data-agent
  tenant tests, manual AT and external/IP clearance remain separate/unproven.

Keep the repository private. Protected #8 routing, approvals/labels, licences/
releases/workflows, merge/tag/release/deploy and external/public clearance remain
human work. No new release, deployment or independent approval is implied.
