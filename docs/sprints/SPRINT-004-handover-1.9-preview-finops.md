# SPRINT-004: 1.9 intake and optional Preview FinOps

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-11 |
| Author | Copilot SDK in VS Code; AI-assisted sprint planning and evidence maintenance |
| Status | Design/plan approved; D0–D3 returned evidence, D4 prose for parent review, D5 pending |
| Scope | Selective process/ontology intake and seven GA skills plus acknowledged optional Preview FinOps |
| References | [Catalogue](README.md), [Parent #25](https://github.com/urruegg/frontier-envisioning/issues/25), [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md), [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md), [Plan](../plans/2026-11-11-handover-1.9-preview-finops-plan.md) |

## Outcome and work items

Keep the received process improvements while making FinOps genuinely optional
and Preview, with actual awareness before operations/figures and no hidden
dependency of the GA core. Product maturity is separate from provider Preview,
mapping confidence, release, deployment and external clearance.

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#25](https://github.com/urruegg/frontier-envisioning/issues/25) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D0-D5](../plans/2026-11-11-handover-1.9-preview-finops-plan.md) | `@urruegg`; parent coordinator | Actual written-plan approval recorded | D4 prose for review; D5 pending | D0 `e7e4db5`; pre-D4 strict L1 at `c64a815`, not final post-doc validation |
| [#28 process](https://github.com/urruegg/frontier-envisioning/issues/28) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D1](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d1-process-models-and-deterministic-artifacts) | `@urruegg`; bounded builder | D0 and plan approval | SPEC PASS / QUALITY CLEAR returned | `f5e08f2`; local process/privacy/determinism evidence, not tenant import |
| [#26 FinOps](https://github.com/urruegg/frontier-envisioning/issues/26) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D2](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d2-operational-finops-preview-gating) | `@urruegg`; bounded builder | D1; single wrapper writer | SPEC PASS / QUALITY CLEAR returned | `d763833`; operational acknowledgement/lazy-core/provenance checks, not human pricing approval |
| [#27 renderer](https://github.com/urruegg/frontier-envisioning/issues/27) | [Idea](../ideas/2026-11-11-handover-1.9-preview-finops.md) | [Design](../specs/2026-11-11-handover-1.9-preview-finops-design.md) | [D3](../plans/2026-11-11-handover-1.9-preview-finops-plan.md#d3-ontology-and-preview-aware-ui) | `@urruegg`; bounded renderer | D1-D2 and built fixtures | SPEC PASS / QUALITY CLEAR returned | `c64a815`; qualified 75 DOM/61 browser checkpoint; broader AA matrix and final gates remain D5 |

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

The parent supplied these results. The D4 prose worker used read-only files and
prose patches, with no terminal/runtime execution, nested agents or validation
runs. See the [design verification](../solution-design.md#191-development-intake)
for current architecture, profiles and evidence detail.

| Stage | Commit/evidence | Qualification |
|---|---|---|
| D0 | `e7e4db5`: 279-file receipt with digest above; 241 protected/fixture hashes unchanged at last verification | Original received/release/profile evidence preserved, not new publication verification |
| D1 | `f5e08f2`: 111 tests/398 subtests; 27 entities, 33 relationships, 126 properties, nine sources, four data agents/four semantic models; 18 data plus one knowledge product | Five outputs deterministic under four hash seeds; strict pre-write/customer privacy tested; six mappings to verify and Employee binding gap remain |
| D2 | `d763833`: 81 D2 tests/508 subtests; combined 197/906 | Fresh acknowledgement, lazy core, cache/provenance, private-component/selection matrix and named-variable fingerprint checks; no formal/human pricing approval |
| D3 | `c64a815`: 75 DOM/61 browser reported on frozen source; independent review 16 new DOM/two hosted checks plus 31 old DOM/three Turtle variations | Byte parity/determinism, real CSP/axe, no new WCAG waiver; four light/dark 1440/320 screenshots reported; not exhaustive Preview AA or manual AT certification |
| Parent pre-D4 L1 | At `c64a815`, `python tools/dev.py check --strict` ended `ALL GATES PASSED`: 394 tests, one expected unreleased-manifest skip, 1337 subtests, 48 self-tests, 75 DOM; six existing ESLint warnings, zero errors | Before prose edits, not final post-doc L1/L2 |
| Parent runner | `ecdfdc8` / `e61bc6a`: 39 tools/site tests/four subtests pass, HTTP 200/CSP verified and helper stopped | DOM explicit technical-ack Preview fixture and isolated core/Preview browser site with real hashed CSP; normal site stays core |
| Candidate, not final handoff | Eight verified copy plans, seven GA/one optional Preview, fifteen complete entries, nested guard clear and matching embedded bytes | Skill-file count was measured before the new process reference; final D5 count/digests and rebuilds still needed |

Parent reports 205 verified identity inputs/223 PNGs for core and explicit
Preview profiles; both actual A6 ZIPs have SHA-256
`e40b132d2e1d396ad7ee681d09931b3e35cd5728081cb01235b17396059cfdf9`.
The finite current 1.9.1 profile pin is
`d91044f03bb34f6559eddc8debf035a5d3aa697d7800d723a700528b23004453`;
original profile/assets remain unchanged.

### D4 reference/pressure gap closure awaiting rerun

Before editing, the parent ran four read-only scenarios A–D at `c64a815`.
Actual documents contradicted maturity metadata: unconditional orchestration/
value dependency, absent decline/missing-module branches, missing full notice/
scenario confirmation/flag examples/standalone apply, stale GA/JSON consent and
downstream Preview handling, missing process method/optional routing.
The simulated assistant safely flagged these gaps rather than inventing flags;
it did not execute unsafe operations. This is RED reference/behavioural evidence,
not live Cowork validation.

D4 prose now addresses those paths in all eight skills and relevant references,
root/plugin guides, bounded product sections, Proposed process/CDM ADRs and
catalogues. The exact notice/flag/API default, renewed scenario acknowledgement,
clean declined core/legacy handling, independent viewer gate and provenance are
documented. Parent must rerun the same A–D cases and strict local contracts;
no post-edit GREEN or actual Cowork behaviour is claimed here.

### Remaining D5 and human checks

- Parent owns strict docs/local links/traceability, checkrepo, description limits,
  maturity/installer/product/history contracts and the post-edit pressure rerun.
- Run final strict L1/L2 against the reviewed head, including isolated core/
  Preview fixtures. The 61-browser checkpoint lacked direct acknowledged PRD/
  use-case-detail axe and narrow portfolio coverage; parent reports a tests-only
  32-state Preview AA/layout matrix in progress. Do not infer its results or final
  counts from D3, and keep manual AT certification separate.
- Rebuild final core handoff twice, compare ZIP bytes/digests, measure current
  source-file count, verify fifteen-entry allowlist/exclusions/nested privacy,
  original protected/received hashes and eight-skill offline install plans.
- Final advisory/spec/quality review, feature push/draft PR and maintainer review
  remain parent/human handoff work, not done by this prose worker.
- Actual Cowork validators/behavioural prompts, native Fabric import/data-agent
  tenant tests, content/IP clearance and AT certification remain manual/unproven.

Keep the repository private. Protected #8 routing, approvals/labels, licences/
releases/workflows, merge/tag/release/deploy and external/public clearance remain
human work. No new release, deployment or independent approval is implied.
