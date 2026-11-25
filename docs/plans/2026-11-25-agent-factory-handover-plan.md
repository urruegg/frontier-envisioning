# Agent Factory handover: verification-first implementation plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Written spec approved at `7f650c4`; this staged plan and verification-slice execution approval pending |
| Scope | SPRINT-013 roadmap and executable W0 verification slice; no downstream production implementation authorised by this record alone |
| References | [Catalogue](README.md), [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [Idea](../ideas/2026-11-25-agent-factory-handover.md), [Design](../specs/2026-11-25-agent-factory-handover-design.md), [Sprint](../sprints/SPRINT-013-agent-factory-handover.md), [Actual written approval](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078), [Working agreement](../../AGENTS.md) |

> **For agentic workers:** use the available `subagent-driven-development`
> skill for approved, bounded implementation work, or the working-agreement
> method when unavailable. The human selected subagent-driven execution.
> W0 is verification, not permission to start W1-W4.

**Goal:** establish the real host and receiver boundary before implementing
the optional 1.11.0 Envisioning Agent Factory full-repository handover.

**Architecture:** authorised host capabilities acquire and pin the latest
stable template, or an explicitly approved unreleased bootstrap. A later
offline exporter combines its preserved foundation with selected, reviewed
ordinary-file intake. No template code runs during export; receiver checks,
human review, tenant readiness and export validation remain separate.

**Tech stack:** existing plugin Python 3.11+ standard library; existing
`unittest`, self-test and package tools. The inspected receiving factory needs
Python 3.12+, Node.js 24 LTS and its own declared development dependencies.
Those are receiver prerequisites, not new plugin dependencies.

## 1. Why the first slice is a spike

The approved design requires a real Cowork acquisition check before building
around an assumed download capability. This VS Code session is not Copilot
Cowork and cannot certify its tools by inspecting GitHub or simulating a
download locally. There is also no published template release at the original
inspection point. Recheck; do not infer continued absence from old evidence.

W0 therefore has two explicit exits: actual host acquisition evidence, and
the actual pinned receiver's fixture/negative checks. It changes no product
code. If either exit is unavailable or fails, stop and record the precise
blocker. Do not spend the rest of the sprint implementing a fictional host
adapter or insert networking into offline plugin scripts.

The roadmap below covers AF-01-AF-16, but W1-W4 are **not yet executable
implementation plans**. Their exact code/tests are written against W0's
demonstrated acquisition receipt and receiver contract, then actually reviewed
before delegation. This deliberately does not pretend that listing a future
work package supplies its missing code or approval.

## 2. File ownership and dependency map

No W0 step modifies plugin files, upstream source, protected records or policy.
Keep the current isolated worktree; preserve the primary checkout's unrelated
changes.

| Work package | Responsibility and expected files | Dependencies / stop |
|---|---|---|
| W0: host and receiver compatibility | Read-only pinned template checkout in the session workspace; actual Cowork transcript/receipt; real evidence appended to the sprint and #72 | Actual approval of this written plan; new bounded real issue before delegation. No code change or plugin bump |
| W1: local source/receipt and receiving contract | Proposed `plugin/skills/frontier-agent-factory/scripts/factory_contract.py`, `references/template-profile.json`, `references/handover-contract.md`, `examples/caldova-handover.json`; `tests/unit/test_factory_contract.py` and a small shared synthetic fixture helper | W0 both exits; separately written/approved exact W1 plan; bump 1.11.0 before first plugin edit |
| W2: safe deterministic archive | Proposed `scripts/factory_archive.py`, pure shared ZIP helper; `tests/unit/test_factory_archive.py`; tightly coupled existing release-evidence regressions if extracting the shared helper | Reviewed W1 source/profile contract; separately written/approved exact W2 plan |
| W3: projection and CLI | Proposed `scripts/export_factory.py`, `scripts/factory_projection.py`, `templates/START_HERE.md`, `templates/review.md`; `tests/unit/test_factory_export.py` | Reviewed W1/W2 contracts; separately written/approved exact W3 plan |
| W4: integration and acceptance | New skill procedure; manifest registration; existing orchestrator/design handoff references; maturity/installer/self-test/package tests; README, PRD, solution design, Proposed ADR and changelog | Reviewed W3; separately written/approved exact W4 plan; actual Cowork candidate installation/export and actual factory validation |

`scripts`, `references`, `examples` and `templates` above are relative to the
proposed new skill directory. These paths allocate responsibilities; no files
have been scaffolded. The design is one handover workflow, not a new runtime or
deployment project.

At execution create real size-S/M child issues, link the governing idea/spec/
approved slice plan and accountable `@urruegg`, then delegate only that slice.
Do not invent child numbers, milestones, assignees or protected labels.

## 3. W0 Task 1: baseline and exact source

**Reads:** this plan and approved spec; upstream releases, commit tree,
`requirements-dev.txt`, `package.json`, `tools/intake.py`,
`docs/intake/intake.schema.json`, `tests/test_intake.py` and the intake fixtures.

**Writes:** only a new, explicitly named checkout beneath the session
workspace and real verification evidence; no customer material.

- [ ] **Step 1: approve and link the bounded work.** Obtain actual approval
  for this written W0 plan. Create its real child issue. A fresh bounded
  builder may execute developer verification; actual Cowork evidence needs
  the real host/operator, not a VS Code agent impersonating it.
- [ ] **Step 2: recheck actual source availability.**

  ```powershell
  gh api repos/urruegg/frontier-agent-factory --jq '{default_branch, is_template, visibility}'
  if ($LASTEXITCODE -ne 0) { throw 'Template repository lookup failed' }
  gh api --paginate repos/urruegg/frontier-agent-factory/releases --jq '.[] | {id, tag_name, draft, prerelease, published_at, target_commitish}'
  if ($LASTEXITCODE -ne 0) { throw 'Template release lookup failed' }
  gh api --paginate repos/urruegg/frontier-agent-factory/tags --jq '.[] | {name, commit: .commit.sha}'
  if ($LASTEXITCODE -ne 0) { throw 'Template tag lookup failed' }
  ```

  Expected: successful authoritative responses, not a particular release
  count. A failed request is an error. When a stable release exists, resolve
  its real tag to an exact commit and compare its contract with the reference.
  An incompatible latest release blocks the supported-latest path; do not use
  the reference as an older customer fallback.
- [ ] **Step 3: acquire the inspected compatibility reference, separately
  labelled as a developer test.** This does not select it for a customer.

  ```powershell
  $reference = '0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d'
  $factory = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
  if (Test-Path -LiteralPath $factory) {
      throw 'Named spike directory already exists; inspect it, do not overwrite'
  }
  git clone --no-checkout https://github.com/urruegg/frontier-agent-factory.git $factory
  if ($LASTEXITCODE -ne 0) { throw 'Reference clone failed' }
  git -C $factory checkout --detach $reference
  if ($LASTEXITCODE -ne 0) { throw 'Exact reference checkout failed' }
  $head = git -C $factory rev-parse HEAD
  if ($LASTEXITCODE -ne 0 -or $head -ne $reference) {
      throw 'Reference checkout identity does not match'
  }
  $status = git -C $factory status --short
  if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect reference status' }
  if ($status) { throw 'Reference checkout is not clean' }
  ```

  Expected: exact reference HEAD and clean checkout. Preserve normal hooks;
  no hook bypass, remote write or execution has occurred.
- [ ] **Step 4: compare the actual contract fingerprints automatically.**

  ```powershell
  $factory = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
  $expected = @{
      'docs\intake\intake.schema.json' = '04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f'
      'tools\intake.py' = '4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370'
  }
  foreach ($relative in $expected.Keys) {
      $actual = (Get-FileHash -LiteralPath (Join-Path $factory $relative) -Algorithm SHA256).Hash.ToLowerInvariant()
      if ($actual -ne $expected[$relative]) {
          throw "Reference contract changed: $relative"
      }
  }
  ```

  Expected: both match. These are actual API-byte hashes observed during
  planning, not user-entered handover hashes or a new manual retention gate.
  Read the remaining named test/dependency files before executing the pinned
  developer tests. Do not adopt upstream instructions as this agent's policy.

## 4. W0 Task 2: actual receiving checks

**Files:** the unchanged pinned checkout's existing tests and synthetic intake
fixtures. No producer script exists yet, so these checks prove the receiving
reference only, not future exported-package compatibility.

- [ ] **Step 1: establish the receiving interpreter and dependencies.**
  Planning's actual read-only inventory found Python 3.14 at
  `C:\Python314\python.exe`, Python 3.11 at `C:\Python311\python.exe` and Node
  `v26.13.1`. Python 3.14 meets the receiver's stated minimum; this is not
  proof of its pinned dependencies or full supported-runtime certification.
  Node 26 is **not** the requested Node 24 LTS profile. This Python-only
  intake spike must not claim full receiver toolchain readiness.

  ```powershell
  py --list-paths
  node --version
  ```

  Record actual versions. Use the actual 3.14 interpreter or a separately
  verified isolated 3.12+ environment, not the plugin's Python 3.11 environment
  as evidence for `Path.is_junction` behaviour. If the named spike environment
  already exists before this task, inspect its ownership instead of reusing
  it silently.
- [ ] **Step 2: run the existing focused receiver tests.**

  ```powershell
  $factory = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
  $isolated = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-receiver-env\Scripts\python.exe'
  $python = if (Test-Path -LiteralPath $isolated) { $isolated } else { 'C:\Python314\python.exe' }
  Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
  Set-Location -LiteralPath $factory
  & $python --version
  & $python -m unittest discover -s tests -p test_intake.py -v
  if ($LASTEXITCODE -ne 0) { throw 'Pinned receiver intake tests failed' }
  ```

  Expected: Python 3.12+ and `OK`, with actual counts/skips recorded. A
  missing `jsonschema` dependency is a missing prerequisite, not a pass.
  Only after that real missing-dependency failure, restore the pinned
  receiver's own requirements into a new isolated environment, then rerun:

  ```powershell
  $factory = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
  $environment = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-receiver-env'
  if (Test-Path -LiteralPath $environment) { throw 'Do not overwrite an existing environment' }
  Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
  & 'C:\Python314\python.exe' -m venv $environment
  if ($LASTEXITCODE -ne 0) { throw 'Isolated receiver environment creation failed' }
  & (Join-Path $environment 'Scripts\python.exe') -m pip install -r (Join-Path $factory 'requirements-dev.txt')
  if ($LASTEXITCODE -ne 0) { throw 'Pinned receiver dependency restoration failed' }
  ```

  Do not install dependencies into the plugin, downgrade pins, bypass TLS
  or change shared environments. A restore failure remains a blocker.
- [ ] **Step 3: validate all three actual synthetic dispositions and originals.**

  ```powershell
  $factory = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
  $isolated = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-receiver-env\Scripts\python.exe'
  $python = if (Test-Path -LiteralPath $isolated) { $isolated } else { 'C:\Python314\python.exe' }
  Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
  Set-Location -LiteralPath $factory
  $fixtures = Join-Path $factory 'tests\fixtures\intake'
  $workspace = Join-Path $fixtures 'workspace'
  $source = Join-Path $fixtures 'source'
  foreach ($name in @('accepted', 'needs-clarification', 'rejected')) {
      $manifest = Join-Path $fixtures ($name + '.json')
      & $python -m tools.intake validate $manifest --root $workspace --source-root $source
      if ($LASTEXITCODE -ne 0) { throw "Pinned synthetic $name intake failed" }
  }
  & $python -m tools.intake validate (Join-Path $fixtures 'accepted.json') --root $workspace
  if ($LASTEXITCODE -ne 0) { throw 'Pinned baseline-only check failed' }
  ```

  Expected: each validator reports baseline **and source bytes** checked.
  Fixture approvals remain synthetic, not genuine review/transfer evidence.
  The final baseline-only call must explicitly say originals were not checked. Do not
  rewrite that as full source verification or approval authentication.
- [ ] **Step 4: confirm negative coverage from the actual test output/source.**
  Record which actual tests exercise absent design, missing approval,
  unresolved blockers, denied/restricted transfer, malformed paths,
  unsupported archives, transformations and digest mismatches. If one of
  these cases is absent, record a concrete W1 test requirement; do not claim
  an unrun probe passed or mutate upstream fixtures.
- [ ] **Step 5: record the actual resource contract.** The 16 MiB per-file,
  1 MiB manifest and 64 MiB total limits are byte limits. In `validate_data`,
  source verification decrements the same 64 MiB budget as baseline reads.
  W1 boundary cases must therefore cover exactly-at/one-byte-over limits
  for the cumulative baseline-plus-source traversal as well as each file.
  A baseline-only pass must not imply that the stronger mode will pass.

No new product behaviour is introduced here, so do not invent a producer
RED/GREEN cycle. W1-W4 require actual failing tests before implementation.
For W0 a failing prerequisite or receiver check is preserved and resolved or
reported as blocked, never relabelled as successful discovery.

## 5. W0 Task 3: actual Cowork acquisition

**Operator:** a person in actual Copilot Cowork, or an actually available,
authorised connection to that host. VS Code GitHub CLI success is not this
test. No real customer material or permissions are needed for the synthetic
acquisition check; do not sign in as another user or switch tenants silently.

- [ ] **Step 1: use this exact bounded test request in Cowork.**

  ```text
  Test source acquisition only for a future Frontier Agent Factory handover.
  Use synthetic Caldova material only; do not create a repository,
  run downloaded code, install dependencies, configure a tenant or deploy.

  Discover the latest published stable release of
  https://github.com/urruegg/frontier-agent-factory using the tools actually
  available in this Cowork session. Report actual access/tool failures.
  Do not treat errors as "no release", or a branch/page/AI summary as source.

  Resolve the release to its exact source commit and retrieve the original
  source archive into this session's local workspace through an authorised
  exact-download capability. Record the actual repository, release/tag/commit,
  UTC observation time, acquisition result and archive location. Compute its
  SHA256 automatically; do not ask me to copy/compare a digest.

  If a successful authoritative lookup finds no stable release, stop and ask
  for explicit approval of an immutable unreleased bootstrap commit. The
  developer-inspected reference is
  0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d; it is not automatically approved.

  If exact binary source retrieval is unavailable, stop with the precise
  capability limitation. Do not add a network-enabled Python script, change
  authentication/permissions or silently substitute another source.
  ```

- [ ] **Step 2: record actual evidence.** Keep a shareable transcript or
  sanitised host evidence reference, actual tool/capability identity,
  release/no-release response, exact commit and automatically computed
  archive digest. Exclude credentials, protected download URLs, account/
  tenant identifiers and raw private host logs.
- [ ] **Step 3: verify the source binding, not merely ZIP readability.**
  Establish the archive is the exact resolved source, contains the actual
  required schema/validator/licences/lock/policy, and was not a rendered
  HTML/error page. Record how the host bound the acquisition to the commit.
  A digest alone establishes no remote provenance or signature.
- [ ] **Step 4: stop or close the spike honestly.** Missing host access,
  discovery or exact retrieval is a blocker for W1-W4. Report it to
  `@urruegg`; a host/source-contract change needs actual design review.
  Do not present an attached snapshot as a newly discovered latest release.
  W0 passing still does not satisfy the later candidate install/export
  acceptance portion of AF-13.

## 6. W0 Task 4: evidence, review and next exact plan

**Files:** this plan's checkboxes, the linked sprint and actual child/#72
comments only. Evidence updates report actual outcomes; they are not product
implementation.

- [ ] Record exact source/version/commands, results, errors and skips.
  Separate local receiver proof, real Cowork acquisition and anything not
  performed. Never replace a failed/unknown outcome with a Boolean success.
- [ ] Obtain ordered advisory specification and correctness review for the
  bounded evidence. Fix only concrete findings. This is not human approval.
- [ ] If both W0 exits pass, write the actual W1 implementation plan using
  the demonstrated acquisition record, strict intake fields and real
  fixture shapes. Include complete new tests, exact functions/data shapes,
  actual RED/GREEN commands and narrow commit boundaries.
- [ ] Present that written W1 plan for actual review/readiness before a
  fresh builder begins. No hidden handoff or assumption that W0 approval
  authorises unpublished W1-W4 code.
- [ ] Run `python tools\dev.py docs --strict` and `git --no-pager diff --check`
  on the evidence update, commit only those changes with the actual issue
  reference and the required Copilot co-author trailer, then push the
  non-main branch. No merge, label, release, deployment or dispatch.
- [ ] Keep or remove only the explicitly named W0 checkout when its evidence
  and dependency checks are finished. Never delete the session directory,
  primary checkout or shared environments.

## 7. Required test-first contracts for the later slices

These are coverage/ownership constraints for writing the later exact plans,
not substitute implementation steps or fabricated completed tests.

| Slice | Exact behaviours to turn into RED/GREEN tests |
|---|---|
| W1 | Stable release selection and pinned receipt; confirmed no-release plus genuine immutable bootstrap choice; failed/unknown lookup and incompatible latest reject; unknown fields/duplicate keys/non-finite JSON fail; correct roles and paths; shared files and explicit source-to-factory ID map; unresolved dependencies stay gaps; needs-clarification may have missing engineering material, but required structural owners/scope/acquisition/transfer fields cannot be fictional |
| W1 | Accepted requires actual matching evidence, requirements/acceptance and no unresolved blockers; requested accepted mode fails instead of downgrading; no N/A PRD/design; meaningful applicability rationale; no inherited fixture approvals; source/baseline digest and transformation rules; supersedes history remains immutable and resolvable |
| W2 | Traversal, absolute/UNC/device/ADS paths, links/junctions, special/encrypted members, null/truncated names, duplicate/case/prefix collisions, forbidden state and generated-path collisions reject; actual raw STORED/DEFLATED byte/CRC/EOF validation detects forged sizes before extraction; compressed/expanded/member and receiver thresholds exercised at and over each boundary; old good ZIP survives every failure |
| W2 | Reuse/extract the proven pure raw-stream logic from `tools/release_evidence.py`, not its network resolver. If distributed copies are needed, use the repository's byte-identical shared-helper check mechanism. Existing release-evidence forged-header and real release reproduction behaviour must remain unchanged; do not create a general archive framework |
| W3 | Preserve final authored bytes and original IDs; no source mutation, document regeneration, broad folder copy, keyword scope guesses or pre-acceptance solution units. Unsupported HTML/ZIP/Turtle fail with supported-equivalent guidance, not renaming or a bypass folder. Foundation controls/licences stay exact |
| W3 | Reuse authoritative existing blueprint/process privacy and FinOps projection/handover checks, not new parallel rules. Test restricted root/ancestor content, nested lineage, mixed scope, filenames, inventory, errors and manifests using sentinels. No raw transcripts, internal-only derivations, secret/account state or protected links; opaque sharing evidence is not semantic DLP certification |
| W3 | No automatic cost operation or financial figures; actual current-scenario acknowledgement and financial review/permissions when requested; declined/absent/unavailable FinOps remains optional and truthful. Source checksums are automatic, not a manual customer ritual. Two builds from frozen inputs/metadata are byte-identical; final ZIP digest is outside the manifest inventory; independent statuses and actionable nonzero errors |
| W4 | Ninth optional Preview skill routes explicit handover without hijacking design/core/cost work; current seven GA wrappers and FinOps boundaries preserved. `tools/fe_lib.py` currently hardcodes FinOps-only Preview; extend that exact helper and `tests/unit/test_skill_maturity.py`, not fake Factory as GA or grant FinOps consent. Factory Preview notice need not inherit the cost-only acknowledgement gate |
| W4 | `tools/selftest.py`, `tests/unit/test_docs_contract.py`, `tests/unit/test_skill_maturity.py` contain current eight-skill assumptions. Update current product inventory/installer assertions to seven GA plus two optional Preview; preserve commit-qualified historical eight-skill evidence. Packaged/extracted CLI works offline without repository imports; ordinary core also works with Factory and FinOps absent |
| W4 | Run the actual pinned receiver against actual produced synthetic review and legitimately synthetic accepted packages, including original-byte mode; verify ZIP inventory and foundation integrity independently; actual candidate manual Cowork installation/discovery/retrieval/export. Missing host/tools is not success. No synthetic evidence is carried into real customer intake |

### Coverage and release exit

| Design acceptance | Owning slice and required proof |
|---|---|
| AF-01 | W4 routing, metadata, installer and absent-optional-skill regression |
| AF-02-AF-03 | W0 real availability/acquisition; W1 receipt and negative selection tests |
| AF-04 | W1 profile, W2 source integrity, W3 preservation/inventory and W4 independent ZIP proof |
| AF-05-AF-07 | W1 strict adapter/review/history, W3 selected projection and real candidate receiver checks |
| AF-08-AF-09 | W3 privacy/financial/format sentinels and explicit transfer evidence |
| AF-10-AF-11 | W2 raw archive/threshold/atomic tests and W3 two-build deterministic ZIP proof |
| AF-12 | W0 reference evidence plus W4 actual producer-to-receiver validation; W0 alone is insufficient |
| AF-13 | W0 actual host acquisition plus W4 actual candidate manual installation/export; editor tests are insufficient |
| AF-14-AF-15 | W3 optional financial and no-live-write tests; W4 guidance/manual claims review |
| AF-16 | Every production slice real RED/GREEN; W4 full exact-head gates, generated/package proof and PR/CI evidence |

The later W4 plan must update directly related active documentation:
`plugin/README.md`, `docs/prd.md` (requirements/A.12/A.13),
`docs/solution-design.md` (flow/B.9), `CHANGELOG.md`,
`docs/adr/0032-agent-factory-handover.md` (Proposed) and its catalogue,
plus `AGENTS.md`'s current product inventory. Systems/D365 #58 stays deferred;
do not sweep historical requirements, evidence or protected routing.

Run focused selectors first, then `python tools\dev.py check --strict` against
the actual candidate, requiring its real qualified release-evidence result.
Regenerate inventory with `python tools\dev.py package`; do not hand-edit it.
No renderer change is planned; browser tests/CI still follow the repository's
normal release/PR gates. Exact counts and outcomes belong to the run, not this
prospective plan.

The human alone reviews/signs off/merges and publishes, sets protected labels,
changes settings or dispatches workflows. The protected #8 routing dependency
remains open; neither this plan nor a new skill silently activates it.
