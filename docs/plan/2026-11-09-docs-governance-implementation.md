# Documentation, Governance and Accessibility Implementation Plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Copilot SDK in VS Code |
| Status | Proposed plan; design approved, implementation not approved |
| Scope | Coordinated delegated implementation of the eight approved requirements |
| References | [Issue](https://github.com/urruegg/frontier-envisioning/issues/6), [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md), [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [Sprint](../sprint/SPRINT-001-docs-governance-and-accessibility.md) |

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `subagent-driven-development` after separate human plan approval. Execute the
> checkbox steps in the linked task plans, using a fresh bounded worker per
> implementation task and review checkpoints. Do not execute this plan now.

**Goal:** Deliver maintainable documents, a linked engineering work package,
clear agent governance and measured accessibility improvements without weakening
the offline plugin or human controls.

**Architecture:** Documentation and deterministic checks share existing
Python tooling; governance separates policy from permissions; renderer changes
remain in source and use existing DOM/Playwright gates. A person owns protected
ownership/access/hook changes and manual assistive-technology acceptance.

**Tech Stack:** Python 3.11+ standard library/unittest, existing node:test/happy-dom,
Playwright, pinned development-only axe-core 4.11.0, GitHub issues/PRs and Markdown.

---

The metadata table precedes the worker/Goal/Architecture/Tech Stack sections
to follow the user-approved six-field documentation header convention.

## 1. Workstreams and approved boundaries

| Workstream | Tracking | Exact plan | Executor |
|---|---|---|---|
| Documentation/checker | [#10](https://github.com/urruegg/frontier-envisioning/issues/10) | [Documentation foundation](2026-11-09-documentation-foundation-plan.md) | Fresh bounded builder/docs workers |
| Governance prose | [#9](https://github.com/urruegg/frontier-envisioning/issues/9) | [Agent governance](2026-11-09-agent-governance-plan.md) | Fresh bounded governance worker |
| Renderer accessibility | [#7](https://github.com/urruegg/frontier-envisioning/issues/7) | [Accessibility](2026-11-09-accessibility-plan.md) | Fresh renderer workers |
| Protected/manual controls | [#8](https://github.com/urruegg/frontier-envisioning/issues/8) | [Human handoff](2026-11-09-human-governance-plan.md) | Person only; never an agent |

Planning baseline is main `d249fcab0fae2fc8b161ccce848cc911ffcd76f4`.
Planning records and imported audit evidence are not implementation.
The first renderer change uses the current unreleased version, or a new patch
when a release exists by execution time. A single coordinator owns versioning.

## 2. Dependency and scheduling contract

```text
User design approval (recorded)
    -> user plan approval (not recorded)
    -> documentation D1-D5 (#10)
         -> governance G1-G3 (#9) -> human H1-H3 (#8)
         -> renderer A1-A5 (#7)
    -> integration/review checkpoint
    -> human manual acceptance / merge / release decisions
```

Documentation and governance run sequentially because they touch the same
catalogues/instructions. Renderer source-only tasks may run alongside governance
only in isolated worktrees with disjoint file allowlists; its final PRD/design
updates wait for the split and governance writer to finish.

No two workers own `tools/dev.py`, product documents, dependency manifests,
version carriers or generated template/install files concurrently. Prefer
serial execution over a complicated coordination mechanism.

## 3. Pre-execution gate

- [ ] A person explicitly approves the plan and records that decision against
      #6; the approved design alone is insufficient.
- [ ] The planning-only PR is merged by a person before workers branch from
      main. If a person instead approves an explicit stacked base, record that
      SHA and dependency; never pretend the plan is already on main.
- [ ] A person sets required ready/design labels when applicable. The parent
      verifies actual issue links/readiness through the authenticated GitHub
      integration; it does not infer readiness from local metadata.
- [ ] Parent confirms a clean checkout, current main and unchanged protected
      files. Unexpected overlapping user changes stop the affected task.
- [ ] Parent invokes `subagent-driven-development` and, when isolation is
      needed, `using-git-worktrees`; uses existing dependencies before installs.
- [ ] Person keeps #8 and manual accessibility checks outside agent delegation.

Per-command Windows environment:

```powershell
if (Test-Path Env:PYTHONHOME) { Remove-Item Env:PYTHONHOME }
$primary = 'C:\Users\urruegg\source\urruegg_microsoft\frontier-envisioning'
Set-Location $primary
$env:PATH = (Join-Path $primary '.venv\Scripts') + ';' + $env:PATH
$env:PYTHONUTF8 = '1'
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $primary 'build\playwright-browsers'
```

Inside a worktree, set the working location to the exact path supplied by the
parent while retaining the primary Python/browser-cache locations unless a
local environment exists. Do not assume a worktree has `.venv` or
`node_modules`. Restore dependencies only after a manifest change or an actual
missing-dependency failure. Shell settings are process-local; repeat them for
a new command process.

## 4. Delegation contract

Each implementation worker receives:

- its one task ID and issue; the approved spec and exact subplan section;
- current base SHA and branch/worktree;
- explicit create/modify/test allowlist and non-goals;
- exact red/green command and stop condition;
- no protected-file, permission, merge, release or deployment authority.

Use registered `frontier-builder` for Python/checker/document-bundle tasks and
`frontier-renderer` for renderer tasks. Once the docs agent is registered, use
it for bounded prose work; if it is not registered in the task tool, use a
registered worker with the approved docs-agent file as its scoped instructions.
Do not invent a task-tool agent type. Leave model/reasoning/context overrides
unset.

Dispatch one fresh implementation subagent per numbered task. Do not reuse the
earlier research agent or a fixed worker pool. A task finishes with owned paths,
red/green evidence, commit, unresolved findings and generated-file status.

After each task, the parent checks results and runs the relevant validation,
then performs two review checkpoints: spec/acceptance compliance and code/
documentation correctness. Use a bounded read-only `frontier-reviewer` for
substantial delegated diffs; combine both checkpoints in one review dispatch
when the evidence fits. Do not duplicate the worker's exploration.

Fix blocking findings in the same task context; a follow-up message is for that
same task only. New independent tasks use new workers. The parent integrates
reviewed commits; no agent merges the final PR.

## 5. Coverage and completion conditions

| Requirement | Implementing tasks | Required proof |
|---|---|---|
| DG-01 docs agent | D1 | Exact discovery/tool/boundary checks |
| DG-02 PRD/design split | D2-D3 | Preserved IDs/anchors, two-doc bundle test |
| DG-03 instructions | G1-G2 | Authority/path/guardrail contract tests |
| DG-04 linked intake | D4-D5, G1-G2 | Catalogues, metadata, issue-shape/local links and real readiness verification |
| DG-05 policy | G1-G3 | Proposed state, no delegation of protected rights, evidence/KPI contract |
| DG-06 ownership/access | H1-H3 | Human invitation/eligibility, CODEOWNERS and routing evidence |
| DG-07 headers | D4-D5 | Eligible-file checks; exemptions and historic/product hashes unchanged |
| DG-08 accessibility | A1-A5, H4 | WCAG-tagged checks, keyboard/reflow/contrast/targets, explicit manual/report limitations |

Identity-catalogue empty-header findings are best-practice-only and remain
explicitly tracked for a separately approved identity-output/version/profile
change. No hosting patch masks them and no existing profile hash is loosened.
Manual assistive-technology approval is not inferred from automated tests.

## 6. Final gates and handoff

- [ ] Parent regenerates only required product files through the task runner.
- [ ] `python tools\dev.py docs --strict` passes after D4 introduces that command.
- [ ] `python tools\dev.py check --strict` ends with `ALL GATES PASSED`.
- [ ] `python tools\dev.py site e2e --strict` ends with `ALL GATES PASSED`.
- [ ] Exact artifact shapes, preserved identifiers/links, eligible headers,
      protected-path diff and version/raster guards are verified.
- [ ] Draft PRs use the repository template, actual results, agent disclosure
      and renderer screenshots. They reference child issues, not falsely close
      #6 while human work or acceptance remains outstanding.
- [ ] Parent verifies cloud L1/L2/IaC and reports neutral/skipped checks honestly.
- [ ] Sprint links real PR/evidence and retains open human/manual actions.
- [ ] People review/merge; people separately tag, release and deploy.

Current state: the design is approved; this plan is ready for separate approval.
No production, agent-definition, instruction, checker, renderer, dependency,
ownership or permission implementation has started.
