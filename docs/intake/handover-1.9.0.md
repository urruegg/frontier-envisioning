# Received 1.9.0 selective intake evidence

Date: 2026-11-11

Evidence revision: D5, 2026-11-11; Copilot AI-assisted maintenance.

[279 source hashes](source-inventory-1.9.0.json) and verbatim
[1.8.0](received-1.8.0-manifest.json) / [1.9.0](received-1.9.0-manifest.json)
manifests preserve the supplied evidence. Claims in those records are received,
not independently verified publications or release reproduction.

The maintainer approved the design at 11:02 +01:00 and subsequently the written
[SPRINT-004 plan](../plans/2026-11-11-handover-1.9-preview-finops-plan.md):

> okay the plan is approved please implement it sub agent driven now

This actual approval is recorded on [#25](https://github.com/urruegg/frontier-envisioning/issues/25);
it is not an inferred readiness/approval label or permission for protected work.

The isolated worktree starts from the saved planning commit
`2157c1335e8dc1b08f71904758e209c086a20043`, based on main
`907c3ca5d1ce94ca479ec7c9a3887187574cc0f4`.
D0 tests failed on the missing receipt and old version, then passed after
receipt generation and the standard 1.9.1 bump. Baseline selectors passed
16 tests and 27 subtests. All 241 original protected/fixture hashes were captured.

## Returned implementation checkpoint — 11 November 2026 (+01:00)

Copilot AI-assisted evidence maintenance; results below were returned by the
parent loop, not rerun by the prose worker. This receipt retains its historical
format and qualified earlier checkpoints. The
[idea](../ideas/2026-11-11-handover-1.9-preview-finops.md),
[design](../specs/2026-11-11-handover-1.9-preview-finops-design.md),
[plan](../plans/2026-11-11-handover-1.9-preview-finops-plan.md) and
[SPRINT-004](../sprints/SPRINT-004-handover-1.9-preview-finops.md) link the approved
scope to current delivery evidence; [documentation catalogue](../README.md)
routes the maintained product records.

- D0 `e7e4db5`: exact receipt digest
  `904538ec9930aad2d3aa5e8067023f4a7230d46a5696faef7836896b444a01e9`;
  241 original protected/fixture hashes unchanged at last verification.
- D1 `f5e08f2`: SPEC PASS / QUALITY CLEAR, 111 tests/398 subtests.
  Five outputs deterministic under four hash seeds; strict pre-write/privacy
  tested. Integrated Caldova: 27 entities, 33 relationships, 126 properties,
  nine sources, four data agents/four semantic models, 18 data plus one knowledge
  product; six mappings to verify and Employee binding gap remain.
- D2 `d763833`: SPEC PASS / QUALITY CLEAR, 81 D2 tests/508 subtests,
  combined 197/906; fresh acknowledgement, lazy core, cache/provenance,
  private-component/selection matrix and named-variable fingerprint evidence.
- D3 `c64a815`: SPEC PASS / QUALITY CLEAR, 75 DOM/61 browser reported on
  frozen source; independent review 16 new DOM/two hosted checks plus 31 old
  DOM/three Turtle variations. Real CSP/axe and no new WCAG waiver, not exhaustive
  Preview AA, tenant import or manual AT certification.
- Parent pre-D4 strict L1 at `c64a815`: `ALL GATES PASSED`, 394 tests,
  one expected unreleased-manifest skip, 1337 subtests, 48 self-tests, 75 DOM;
  six existing ESLint warnings/zero errors. Not post-doc validation.
- Parent runner `ecdfdc8` / `e61bc6a`: isolated core/Preview fixtures with
  real CSP; 39 tools/site tests/four subtests pass and HTTP 200/CSP verified.
  Core and explicit Preview raster inputs were verified separately; actual
  pins and full qualifications are in the [design](../solution-design.md#191-development-intake).

## D4 reference evidence

D0–D4 are committed and SPEC PASS / QUALITY CLEAR; D4 is `afd6cd4`.
Four document-only reference/pressure scenarios A–D had six baseline gaps at
`c64a815`, safely flagged rather than bypassed. The parent returned GREEN after
D4. This is not live Cowork routing validation. The scaffold flag boundary is
explicit: acknowledgement belongs to upstream FinOps, not the scaffold CLI;
a stale GA label cannot pass F1. The actual scaffold does not automatically
generate financial tables.

Earlier candidate measurements were eight verified copy plans (seven GA/one
optional Preview), fifteen complete entries and passing nested privacy/embedded
bytes, before the new process reference. Final measurements below supersede
that candidate, not its historical evidence.

## D5 final local technical evidence

**Local technical verification complete; PR/CI handoff pending.** The checked
canonical source is `d614979` on `feat/25-handover191`, after D4 `afd6cd4`,
legacy regression `8208155` and measured AA/shared-control fixes `4cb4d4e`.
These are parent-returned local results, not CI or human sign-off. Version
1.9.1 remains unreleased, private engineering work. This record and
[SPRINT-004](../sprints/SPRINT-004-handover-1.9-preview-finops.md) are excluded
from both handoff ZIPs; this evidence-only update changes no packaged input.
This is a source-qualified verification checkpoint, not a live PR tracker.
Use the PR linked from [parent #25](https://github.com/urruegg/frontier-envisioning/issues/25)
for current CI and maintainer-review status.

### Canonical strict gates and bounded accessibility

- At `d614979`, `python tools/dev.py check --strict` ended `ALL GATES PASSED`
  (exit 0): 399 unit/pipeline tests passed, one expected unreleased-manifest
  skip, 1440 subtests passed, 48 self-test checks and 75 DOM tests.
  Repository check: 586 files, zero errors; docs: zero errors; neutrality:
  zero findings; Ruff passed; ESLint: zero errors, six existing warnings.
  Full summary: `build/evidence/final-l1.log` (ignored local evidence).
  The pre-canonical 398-test/1349-subtest result is superseded for this head.
- At `d614979`, `python tools/dev.py site e2e --strict` ended `ALL GATES PASSED`
  (exit 0), with 67 browser tests passed on actual core and Preview routes
  under real CSP. There were 32 unique Preview axe/layout states: four views ×
  before/after genuine acknowledgement × light/dark × 1440/320 widths.
  Those states had zero applicable WCAG violations, undersized controls,
  document overflow or bad local scroll. Another 168 logged core/identity axe
  states had zero WCAG findings. The earlier 61-browser `c64a815` checkpoint
  is historical, not exhaustive.
- Measured target regression: 20/32 bad states RED → 0/32. Radio and `ucag`
  targets measured 24 × 24 CSS px, labels and agent links at least 24, and
  the mobile bubble at least 27.9 through bounded local scroll. DOM labels/
  groups are unique; shared widgets reflect one feedback key without DOM
  rerender or caret loss; hidden numeric inputs are never revealed.
  Two focused RED → GREEN checks and the parent's independent six-browser-test/
  32-state run support the fixes. Evidence:
  `build/evidence/d5-preview-target-{red,green}/` and
  `build/evidence/d5-shared-assumption-{red,green}/`; eight post-fix screenshots.

This is bounded automated evidence, not all possible AA coverage or assistive
technology (AT) certification. Colour-contrast incompletes and manual AT remain
unproven; existing manual checks are not waived.

### Final canonical handoff

C1 built the isolated package/core bundle; the full L1 independently deleted
and rebuilt core output; C2 rebuilt package, complete bundle and checksums.
All three files had identical byte hashes and sizes across C1/C2.
`dist/distribution-1.9.1` contains exactly:

| File | Bytes | SHA-256 |
|---|---:|---|
| `frontier-envisioning-plugin-1.9.1.zip` | 726939 | `81a58267b286ad96921f70b912b68b1501f1913c9799a6c75c1359b49f075b4e` |
| `frontier-envisioning-1.9.1-complete.zip` | 4465335 | `e81618b16bbc09e3d717e81ec2cb8ce51fcff6c9f706cb66c486d49030cec67b` |
| `SHA256SUMS.txt` | 210 | `5828a361188c10618a65747ecb4c3276af5878ecdef86830b59d49af6ddee1b3` |

All 93 plugin archive entries match raw working-tree and Git HEAD `d614979`
bytes. Archive-root `manifest.json`, `color.png` and `outline.png` map from
`plugin/package/`. There are eight skills and 85 skill files: seven GA and one
optional, acknowledgement-required Preview; FinOps is not automatic.
The complete bundle has exactly fifteen allowlisted entries, including four
ontology documents. Embedded plugin, documents, current core HTML and identity
catalogue/ZIP match actual source outputs. Explicit Preview demo/JSON, private
analysis, intake and arbitrary sources are excluded.

Both archives passed the defined whole/nested name, text, escaped-variant and
comment privacy guard. Checksum contents, fixed ZIP dates and Unix metadata
were verified. This is a defined technical scan, not exhaustive secret
clearance, IP clearance or external/publication permission.

Read-only `prepare_install.py` from the actual final extracted ZIP returned
`verified=true`, no problems and eight new copy plans for a clean target.
The legacy seven-skill 1.7.1/forged-GA/cached-ack simulation returned seven
updates plus new process: eight plans, 85 files, seven GA/one optional Preview
requiring acknowledgement. There was no implicit acknowledgement or cost call,
zero actual copies, and existing temporary files were unchanged. Separate
update/reinstall unit checks passed for two versions. No real OneDrive or
Cowork installation was performed.

### Preserved inputs and verification correction

Both full core and explicit Preview profiles passed the actual 205 identity
input checks/223 PNGs. Both actual A6 ZIPs have SHA-256
`e40b132d2e1d396ad7ee681d09931b3e35cd5728081cb01235b17396059cfdf9`;
the finite 1.9.1 pin is
`d91044f03bb34f6559eddc8debf035a5d3aa697d7800d723a700528b23004453`.
No golden/profile broadening occurred. All 241 original protected/fixture files
and five pre-existing intake JSON files remain byte-unchanged. The actual 279
received paths/hashes still match frozen inventory
`904538ec9930aad2d3aa5e8067023f4a7230d46a5696faef7836896b444a01e9`.

The verifier first assumed an incorrect direct plugin-path mapping for the
archive-root manifest; the correct mapping is recorded above. It then found
two new physical CRLF working files against already-committed LF:
`plugin/skills/frontier-finops/scripts/finops_preview.py` (412 lines) and
`plugin/skills/frontier-process/references/ontology-method.md` (133 lines).
Two real source-LF checks went RED. Only those files were normalised to the
already-committed bytes; two normally generated inventory hashes were corrected
with regression evidence in `d614979`. There was no semantic code change or
historical asset rewrite. Earlier Windows-only plugin/complete hashes are
superseded; only the canonical hashes above describe the final handoff.

### Review and remaining handoff

Bounded integration-contract review `74251a45` returned no Critical, Important
or Minor findings and closed the actual C2/gate proof with technical CLEAR at
`d614979`. This is advisory technical evidence, not human review or release approval.

The parent still owns record-only strict docs/header/link/traceability and
product-contract validation, confirmation that handoff hashes are unchanged,
the record commit, feature-only push, draft PR creation and new-head CI checks.
These post-record checks have not been run by this prose worker. No draft PR
number is known or invented. Sole-maintainer sign-off against the final head is
pending; it is not formal self-approval.

Live Cowork validators/behavioural prompts, Fabric import/data-agent tenant
tests, manual AT and external/IP clearance remain separate and unproven.
Keep the repository private. Human-only labels/approvals/settings, protected
[#8 routing](https://github.com/urruegg/frontier-envisioning/issues/8),
merge/tag/release/deployment and publication remain untouched and unclaimed.
