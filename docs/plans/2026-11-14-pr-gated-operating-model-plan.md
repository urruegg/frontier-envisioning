# PR-Gated Engineering Automation Implementation and Adoption Plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Written specification approved at 8de16ca; this plan/readiness approval pending |
| Scope | Staged proposal isolation, native human review, engineering/release automation and maintainer adoption |
| References | [Catalogue](README.md), [Decision #48](https://github.com/urruegg/frontier-envisioning/issues/48), [Idea](../ideas/2026-11-14-pr-gated-operating-model.md), [Approved specification](../specs/2026-11-14-pr-gated-operating-model-design.md), [SPRINT-010](../sprints/SPRINT-010-pr-gated-operating-model.md), [Proposed ADR-0030](../adr/0030-pr-gated-engineering-automation.md) |

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans for inline execution, or superpowers:subagent-driven-development only if separately selected. Execute test-first steps in order. Current person-only actions are stops, never implicit permission to bypass them.

**Goal:** Make actual eligible human PR approval the normal engineering/release
gate, with automated proposal, validation, merge and declared publication.

**Architecture:** Restricted workers write private proposal input. Trusted
GitHub App-backed coordination creates the real PR and checks source/control
facts. Native Pro protections and a trusted eligibility check gate merge;
separate trusted publication processes only the approved release intent.

**Tech stack:** Existing standard-library Python/GitHub CLI tooling, unittest,
existing GitHub Actions/Playwright and a repository-owned GitHub App. No
plugin dependency, npm release stack or Azure-hosted approval service.

## Approval and execution boundary

The maintainer selected `approve-written-pr-gated-spec` for specification
`8de16ca089ba0e2a1787496a4c65ecf17b7b6b4e`. This later plan is not yet
approved. Owner: `@urruegg`; protected labels/assignments are not inferred.

Use the separate `docs/48-pr-gated-operating-model` workspace for planning.
After actual plan/readiness approval, create one scoped implementation branch
per slice from its accepted prerequisite revision. Preserve the separate #47
branch at `aa838fbb`; do not reset it or copy its manual publication context
as the new approval contract.

The change is larger than M. Split implementation into these bounded work
packages, creating real linked child issues only after plan approval and
before starting/delegating them. These are plan IDs, not invented issue IDs:

| Slice | Objective | Prerequisites | Owner boundary |
|---|---|---|---|
| A | Pure authority/proposal contracts, bootstrap package and supported identity/isolation proof | Plan/readiness approval | Code/tests may be prepared; live identity/settings/adoption are person-only |
| B | Trusted App-authored proposal PRs and read-only validation coordination | A contracts and actual restricted identity setup | No unreviewed candidate execution with write credentials |
| C | Trusted eligibility and native Pro gate pilot | B; actual maintainer protections/configuration | No fake native review or routine bypass |
| D | Approved release intent, immutable publication and record PR | C pilot and accepted release controls | No current-agent merge/tag/publish; operational service only after real adoption |

Each child is size M or smaller and links the real idea/spec/plan/sprint,
testable acceptance and accountable owner. No agent is assigned a
non-delegable bootstrap action.

## File and authority map

Agent-editable proposals after plan approval:

- `tools/pr_gate.py`: pure proposal/candidate/action validators; no credentials.
- `tools/proposal_pr.py`: trusted data/API operation planning and coordination.
- `tools/release_control.py`: reviewed intent, source/evidence and safe release
  operation planning; reuse existing hashing/manifest helpers.
- `tools/governance_bootstrap.py`: generate reviewable bootstrap artefacts in
  ignored build output, without altering active protected files/settings.
- `tests/unit/test_pr_gate.py`, `test_proposal_pr.py`, `test_release_control.py`
  and focused additions to `test_guard_hook.py` / `test_release_tools.py`.
- Proposed `.github/workflows/proposal-pr.yml`,
  `.github/workflows/governance-eligibility.yml` and the validation adaptation
  in `.github/workflows/ci.yml`; no activation before adoption.
- Directly related current guides/customisations and the PR template.

Current **person-only adoption surfaces**:

- `AGENTS.md` and active authority/harness policy adoption.
- `.github/hooks/guardrails.json`, `.github/hooks/scripts/guard.py` and
  `session_start.py`; `.github/CODEOWNERS`.
- `.github/workflows/release.yml` and any active deployment gating change.
- Actual App/store provisioning, credential configuration, GitHub rules,
  variables, secrets, merge/tag/publication and protected release records.

Prepare proposed patches/content, not direct edits to these active surfaces.
Do not create a renamed publishing workflow or write wrapper to evade a
protected path/action. Future delegated permissions become valid only after
real maintainer adoption and verified supported enforcement.

## Task 0: Establish the baseline and non-secret capability inventory

**Files:** new tests/helpers only; generated bootstrap evidence under
`build/governance-bootstrap/`. **Slice:** A.

- [ ] Read the actual approved work package, active rules and source revision.
  Run `python tools/dev.py docs --strict` and the existing focused release/
  guard tests before edits:
  `python -m unittest tests.unit.test_guard_hook tests.unit.test_release_tools -v`.
  Record genuine baseline failures; do not suppress them.
- [ ] Inventory only non-secret capability facts: repository visibility,
  owner, actual rules/check origins, supported provider identity, current
  deployment/legacy publication flags and accepted control revision.
  Never dump tokens, private keys, credential-manager contents or secret
  environment variables.
- [ ] Prove the planned worker can have base read/preparation-request access
  and proposal-store write access **without** owner review/publish credentials.
  A shared owner-authenticated terminal/browser is not proof of isolation.
  If the current provider cannot support the boundary, stop activation and
  require the maintainer to configure an isolated supported worker profile.
- [ ] Keep `SHOWCASE_ENABLED` and legacy `RELEASE_ENABLED` unset/false for
  the engineering-only profile. Actual changes are person-only; merely
  documenting a desired value is not verification.

## Task 1: Test the authority contract before implementing it

**Files:** `tools/pr_gate.py`, `tests/unit/test_pr_gate.py`.
**Slice:** A; depends on Task 0 and plan approval.

- [ ] Add sanitized, deterministic GitHub-state fixtures for a Bot/App author,
  human `urruegg` review, distinct source/control SHAs, real-shaped run/check
  identifiers and explicit release intent. Use synthetic IDs/data only.
  Never present them as actual GitHub approval or pilot evidence.
- [ ] Add these focused test groups before code:

  ```python
  def test_action_requires_current_human_review(self):
      state, policy, intent = valid_action_fixture()
      authorize_action(state, intent, policy)
      for field, value in (
          ("review_state", "COMMENTED"),
          ("reviewer_type", "Bot"),
          ("reviewer_login", "another-user"),
          ("review_commit", "0" * 40),
          ("head_sha", "1" * 40),
      ):
          with self.subTest(field=field):
              changed = dict(state, **{field: value})
              with self.assertRaises(ValueError):
                  authorize_action(changed, intent, policy)
  ```

  Define `valid_action_fixture` in the test module with explicit normalized
  fields: fixed repository/base `main`, configured App login/type, human
  reviewer identity/state/review commit, current head/base/control, actual-shaped
  check origin/run/source/conclusion records and an in-scope intent.
  The live collector must obtain these facts from GitHub, never the candidate.

  Add a candidate group that rejects failed/skipped/unknown checks, wrong
  workflow/check origin, mismatched tested base/control and unsafe workflow
  proposals. Candidate eligibility does **not** require human review; action
  authorisation does, avoiding a circular eligibility dependency.

  Add an intent group for absent/false publish, version/tag mismatch,
  existing-tag identity mismatch, undeclared deployment/admin actions and
  extra asset destinations.
- [ ] Run `python -m unittest tests.unit.test_pr_gate -v` and record the
  expected RED from missing behaviour, not a dependency/setup failure.
- [ ] Implement the pure interfaces:

  | Interface | Contract |
  |---|---|
  | `validate_proposal(proposal, policy)` | Safe relative paths, known source/base and scope; no active-policy mutation, credential data or premature privileged workflow execution |
  | `validate_candidate(state, policy)` | Exact source/base/control and trusted successful validation; may report eligibility but never human approval |
  | `authorize_action(state, intent, policy)` | Actual current eligible native human review plus candidate/gate proof and declared action; stale/wrong scope raises `ValueError` |
  | `validate_release_intent(intent, policy)` | Versioned explicit publish intent, canonical tag/version/source mode and fixed destinations; no silent publishing default |

  Preserve this critical review predicate in the implementation:

  ```python
  if state["reviewer_login"] != policy["maintainer"] or state["reviewer_type"] != "User":
      raise ValueError("action requires the configured human reviewer")
  if state["review_state"] != "APPROVED" or state["review_commit"] != state["head_sha"]:
      raise ValueError("approval is absent or stale")
  if state["author_type"] != "Bot" or state["author_login"] != policy["app_login"]:
      raise ValueError("PR is not authored by the configured machine")
  ```

  Validate field types/full SHAs before accessing the predicate. Read the
  effective native review decision/change-request state too; do not reduce
  authorisation to a caller-provided `approved: true`.
- [ ] Run the focused tests GREEN and scoped Ruff. No function returns
  success for malformed input. The CLI catches only expected input/I/O errors,
  reports specific stderr reasons and exits non-zero; no credential/network
  operations belong in this pure module.

## Task 2: Generate and review the maintainer bootstrap package

**Files:** `tools/governance_bootstrap.py`, its focused tests and directly
related documentation. **Slice:** A.

- [ ] Write a failing test proving generation creates only reviewable output
  beneath `build/governance-bootstrap/`, preserves every active protected-file
  byte and never invokes a GitHub/Azure write.
- [ ] Generate a proposed migration patch, non-secret settings/App manifest
  descriptors, validation report and one operator checklist. This consolidates
  initial adoption; it is not a silent `--apply` mechanism.
- [ ] The migration proposal aligns working agreement, accepted policy,
  hooks/harness routing, skills/agents and workflow authority. Preserve
  customer neutrality, generators, licences, immutable records and the
  hard human-review/credential boundaries. Address #8's actual legacy routing
  dependency, not just its documentation.
- [ ] The proposed PR template removes the requirement that the summary be
  physically written by a person; retain human verification instead.
  Proposed heading: `## Summary`.
  Keep all other headings/comments/checklists/order and truthful release
  acceptance fields. Until that template change is adopted, do not fill a
  "written by a person" heading with falsely attributed machine content.
- [ ] Record actual public App metadata, not fake production identities or
  keys. Pin the verified token action for later trusted workflows:

  ```yaml
  - uses: actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510 # v3
    id: app-token
    with:
      client-id: ${{ vars.GOVERNANCE_APP_CLIENT_ID }}
      private-key: ${{ secrets.GOVERNANCE_APP_PRIVATE_KEY }}
      repositories: frontier-envisioning
      permission-checks: write
      permission-actions: read
      permission-contents: read
      permission-pull-requests: read
  ```

  This is a **trusted metadata-only reporter** example, not a PR/candidate
  job. Never return the App token to the worker, print it or pass it as a
  cross-job output. Explicitly scope every installation token's repository
  and permissions; do not request all repositories implicitly.
- [ ] **STOP for the maintainer.** App/private-store creation, key storage,
  scoped provider configuration, actual protections and current protected
  edits are person-only. No key/token is requested in chat. The owner records
  actual adoption revision and capability proof; a file marked Accepted is
  not that proof.
- [ ] Before activation, the owner verifies real PR/check requirements,
  CODEOWNERS `@urruegg`, current-head/stale/latest-push settings, no routine
  bypass, flags off and the restricted machine/human credential split.
  Incomplete provisioning or unsupported provider capability blocks the next
  stage; never fall back to owner-scoped agent authentication.

## Task 3: App-authored PR intake and isolated validation coordination

**Files:** `tools/proposal_pr.py`, `tests/unit/test_proposal_pr.py`,
proposed `.github/workflows/proposal-pr.yml` and validation adaptation.
**Slice:** B; requires A contracts and actual supported identity setup.

- [ ] Write failing tests for a private proposal pointer/hash, safe file
  changes and exact operation allowlist. A title/body containing shell
  syntax remains data; unsafe refs/paths, changed base, secrets or an
  unreviewed credential-bearing workflow are rejected before writes.
- [ ] Implement a dry-run operation plan first. Its write allowlist contains
  only blobs/trees/commits, a namespaced non-main feature ref and an App-authored
  Draft PR linked to the governing issue. No tags/releases/main/settings,
  review-approval or destructive endpoints.
- [ ] Example planned operation descriptor:

  ```python
  operation = {
      "kind": "create_proposal_pr",
      "repository": "urruegg/frontier-envisioning",
      "base_sha": accepted_base_sha,
      "head_ref": "automation/" + proposal_id,
      "proposal_sha": verified_proposal_sha,
      "draft": True,
  }
  ```

  `accepted_base_sha`, `proposal_id` and `verified_proposal_sha` come from
  validated public metadata/input facts, not shell interpolation. Gate any
  real execution in the human-adopted trusted coordinator; local dry-run
  output does not confer write authority.
- [ ] Apply proposed files as inert data via the controlled GitHub operation
  path, not by executing candidate hooks/scripts with the App key. Validate
  all proposed workflow execution/permission boundaries against the accepted
  policy before exposing the branch. The edited candidate policy cannot
  grant its own permission.
- [ ] Render the PR body from the adopted main-branch template, preserving
  headings/comments/checklists/order. Include actual scope, TDD/gate evidence,
  agent disclosure and residual risks. Do not infer manual Cowork results.
- [ ] A trusted metadata coordinator may read PR data and dispatch the
  main-defined read-only validator at the exact candidate SHA. It never
  checks out candidate code itself. Do not use privileged
  `pull_request_target` with a candidate checkout.
- [ ] Keep App private keys, publishing credentials, owner tokens and OIDC
  privileges out of validation. Test the actual worker/provider boundary,
  not merely the presence of `contents: read` in one file.
- [ ] Run the slice tests GREEN, scoped lint and the actual native-author/
  event pilot through the maintainer-adopted control path. Verify GitHub
  reports the expected App as PR author and does not add another manual
  workflow-run approval. No owner or second human account is substituted.

## Task 4: Trusted eligibility, fresh native review and safe auto-merge

**Files:** `tools/pr_gate.py`, related tests,
proposed `.github/workflows/governance-eligibility.yml`,
`.github/workflows/ci.yml` and active guide proposals.
**Slice:** C; depends on B and actual maintainer protection setup.

- [ ] Extend tests to prove forged same-name checks, wrong origin/control/
  source/run, stale owner review and late intent changes never authorise an
  action. A candidate can pass tests without acquiring human approval.
- [ ] Collect fresh GitHub PR/review/run facts in trusted control code.
  Never execute a candidate-supplied state file as an authorisation input.
  Record actual positive IDs, full SHAs, policy revision and linked facts.
- [ ] Report the eligibility check with the App identity only after actual
  L1/L2/IaC conclusions and candidate/control/base bindings match. Failure,
  skipped/unknown/cancelled results remain failing/blocked eligibility.
- [ ] Native main rules require one actual human code-owner review, stale
  dismissal/latest-push freshness, all three checks plus App-origin eligibility,
  resolved conversations and no routine bypass. Actual setup is person-only.
- [ ] Enable/complete native auto-merge only under those rules and revalidated
  current PR state. No `--admin`, force ref update, missing-check fallback,
  synthetic review or bot acting as the maintainer.
- [ ] Pilot a safe non-release PR. Record actual App author, source/base/
  control/check IDs, human review ID/head and merge result. New commits must
  invalidate approval. Assert zero tag/publication/deployment/admin action
  for a PR with no release intent.
- [ ] Run focused RED/GREEN and full `python tools/dev.py check --strict`
  on the actual implementation revision. Verify remote L1/L2/IaC/eligibility
  results separately; neither the local summary nor template is server proof.

## Task 5: Reviewed release intent, publication and immutable record PR

**Files:** `tools/release_control.py`, `tests/unit/test_release_control.py`,
approved adaptation of existing release helpers, release/current guides;
human-adopted `.github/workflows/release.yml`.
**Slice:** D; requires C's real pilot and accepted release authority.

- [ ] Test `frontier-release-intent/1.0` before code: absent/false publish,
  wrong repository/version/tag/source mode, changed approval/intent, wrong
  existing tag object, extra assets and undeclared deployment/admin fail.
- [ ] Test a no-write release operation planner before any operational
  integration. It derives only the approved exact source and four artefacts.
  Existing published tag/hash disagreement must fail, never update/delete.
- [ ] Reuse #47's proven hashing, package allowlist, byte comparison and
  legacy manifest compatibility selectively. Do not cherry-pick its whole
  manual-publication policy or turn off its context validation to fake
  automatic provenance. Implement the explicit new approval/action adapter.
- [ ] Preserve product/source/control distinction. Existing-tag mode uses
  source `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9` and tag object
  `5f9d21953db9c968ae56ac6d485baff3fc09b0ce` for 1.10.0 recovery.
  Merged-PR mode resolves the actual approved merge/source result.
- [ ] The source build is read-only. Independently reproduce the actual ZIP,
  run strict source/package checks, generate pinned SBOM/manifest/checksums
  and verify the exact output set before any publication:

  ```python
  expected_names = {
      f"frontier-envisioning-plugin-{version}.zip",
      "release-manifest.json", "sbom-spdx.zip", "SHA256SUMS.txt",
  }
  if actual_names != expected_names:
      raise ValueError("release assets differ from the approved allowlist")
  if independent_zip_bytes != candidate_zip_bytes:
      raise ValueError("independent package reproduction failed")
  ```

  Values are freshly measured from the fixed source/candidate, not an old
  candidate copied over a failure. Keep generated dates separate from
  publication and preserve existing normalization semantics.
- [ ] The post-approval publisher handles only validated data with its
  narrowly scoped write credential; it does not execute candidate/package
  scripts. Reject unassociated main pushes or approval/check/scope gaps.
- [ ] Publish the reviewed intent, verify actual tag/release/files/download
  digests, then create an App-authored immutable release-record PR using the
  same native gate. Do not direct-push main to avoid another review.
- [ ] Idempotency uses the approved repository/PR/head/intent/version.
  An already completed identical action is recorded honestly. A mismatch
  or partial failure blocks; material recovery requires a new reviewed PR.
  No deletion/replacement of published artefacts or force-push rollback.
- [ ] Do not add private native build-attestation/environment-reviewer
  dependencies to Pro. Record `cryptographic_attestation: not-provided`.
  Publish only the plugin/three verification assets; no registry wrapper,
  public-visibility or Teams/email change.

## Staged adoption evidence and PR handoff

- [ ] Pure contract tests, dry-run plans and generated migration content
  first. No source/metadata declaration is actual identity or enforcement.
- [ ] Actual maintainer adoption and non-release pilot next. Keep publication
  and Azure off while author/review/CI/credential boundaries are verified.
- [ ] Only then run the separately reviewed release pilot. Required manual
  acceptance evidence remains actual human evidence; approval does not
  manufacture tests that could not run.
- [ ] Update current engineering guides, working-agreement references,
  skills/agents/template and routing consistently through the adopted process.
  Historical/private-source/Preview/licence/immutable-record limits remain.
- [ ] For each slice: record real RED/GREEN, scoped lint and fresh full gate,
  use the actual adopted PR template and disclose App/agent roles. A person
  reviews the current head; nobody simulates independent human review.
- [ ] Activation needs real App/store/provider/native-rule/flag/pilot proof,
  not a chat approval or an Accepted status. If a stage cannot demonstrate
  its boundary, stop there and report the limitation.

This plan has executed no future stage. Plan/readiness approval and actual
maintainer adoption remain pending. Normal human participation is PR review;
initial administration/consent and exceptional credential recovery remain
explicit non-routine owner responsibilities.
