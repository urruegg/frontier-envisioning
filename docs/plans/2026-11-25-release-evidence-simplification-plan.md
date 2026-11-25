# Release Evidence Simplification Implementation Plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-25 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Written specification approved; this implementation plan/readiness awaits separate human approval |
| Scope | Issue #67 developer tooling, tests and active guidance; no plugin change or agent publication |
| References | [Catalogue](README.md), [#67](https://github.com/urruegg/frontier-envisioning/issues/67), [Idea](../ideas/2026-11-24-release-evidence-simplification.md), [Approved spec](../specs/2026-11-24-release-evidence-simplification-design.md), [SPRINT-012](../sprints/SPRINT-012-release-evidence-simplification.md), [Written-spec receipt](https://github.com/urruegg/frontier-envisioning/issues/67#issuecomment-7155486060), [#52](https://github.com/urruegg/frontier-envisioning/issues/52), [#8](https://github.com/urruegg/frontier-envisioning/issues/8) |

> **For agentic workers:** REQUIRED SUB-SKILL: use
> `superpowers:subagent-driven-development` after actual approval of this
> written plan. The human selected that execution mode. Steps use checkbox
> syntax; this document does not approve itself or grant protected permissions.

**Goal:** Replace recurring manual release-manifest retention with automatic
exact-version evidence verification, retaining offline local checks and human
publication.

**Architecture:** Keep `verify_release.py` responsible for build comparisons
and its existing historical/write interfaces. One developer-only
`release_evidence.py` resolves and validates published evidence/cache; `dev.py`
reports the resulting verification state. CI receives a read-only GitHub token
at its existing gate step. The protected release workflow needs a separately
documented human-applied equivalent, not an agent edit.

**Tech Stack:** Python 3.11+ standard library, existing `gh` CLI, GitHub REST
read operations, `unittest`/existing pytest runner, existing L1/L2 tools.

---

## Authority, baseline and execution stops

The actual 25 November answer was **"spec is approved and you can implement"**,
referring to written spec `67dc9a542d734ea7af91a2b40dda3ad823550375`,
SHA-256 `584b85e05780b1c276a637b48553191ebfd33c6ede0dc45ecf7c862f971d3926`.
The receipt above records that actual approval and selected subagent mode.
It is not approval of this subsequently written plan. Obtain that distinct
plan/readiness decision before delegated implementation; do not infer labels.

Use the existing isolated `frontier-envisioning-wt-48` worktree. Planning branch
is `docs/67-release-evidence-design`, based on merged main `b9e41e8`.
After actual plan approval, start `chore/67-release-evidence` from the exact
approved committed planning package, with no reset or unrelated checkout edits.
Do not touch the primary checkout's editor settings, field briefs or any
human-authored #52 copy/branch.

This is engineering-only: no plugin edits/version bump, raster-profile change,
generated HTML/gallery refresh, new dependency or hosted/runtime service.
Never edit `releases/**`, `.github/hooks/**`, `release.yml`, `azure-dev.yml`,
licences, CODEOWNERS or settings. Never merge, approve, dispatch, tag or publish.
Protected release-workflow adoption and #8 remain human actions.

**Actual baseline already observed:** existing `LocalReleaseManifest` and
`ManualReleaseWorkflow` selectors passed ten tests; strict docs passed with
zero errors. The published 1.10.0 manifest/checksums were read, not regenerated.
They contain four reproduction artefacts but only three checksummed download
payloads: plugin ZIP, manifest and SBOM ZIP. `SHA256SUMS.txt` is the fourth
download. Do not confuse those two inventories.

## File ownership and units

| Unit | Exact allowed files | Responsibility |
|---|---|---|
| Evidence builder slice | New `tools/release_evidence.py`, new `tests/unit/test_release_evidence.py` | Bounded GitHub GET/download adapter, exact-version/source checks, validated ignored cache; no plugin imports/networking |
| Gate builder slice | `tools/verify_release.py`, `tools/dev.py`, `tests/unit/test_release_tools.py`, `tests/unit/test_tools_core.py`, narrowly `tests/pipeline/test_release_reproduction.py`, `.github/workflows/ci.yml` | Existing comparisons/writers, explicit result propagation, automatic CI lookup and read-only credential wiring |
| Documentation slice | `.github/skills/frontier-release/SKILL.md`, `.github/agents/frontier-release-manager.agent.md`, `docs/engineering/github-setup.md`, `docs/engineering/handbook.md`, `docs/engineering/testing-strategy.md`, new `docs/engineering/release-evidence-adoption.md`, `docs/engineering/README.md` | Accurate normal workflow, offline/CI outcomes, bounded human adoption handover; no weakening of authorisation |
| Requirements/rationale/evidence | `docs/prd.md`, `docs/solution-design.md`, new Proposed `docs/adr/0031-release-assets-as-evidence.md`, `docs/adr/README.md`, narrowly coupled `tests/unit/test_docs_contract.py`, SPRINT-012 and directly related catalogues | Engineering acceptance, rationale and actual source-qualified test/adoption evidence |

Do not duplicate parsing/hash/normalisation logic across these units.
Preserve `standard_artefacts`, `verify`, `normalise`, local exact-tag writer
and release writer as the existing sources of their respective contracts.
Do not broaden generic `fe_lib` for this single use.

## Concrete interfaces and policies

The new evidence unit exposes:

```python
class EvidenceError(ValueError):
    """Release evidence could not be established or validated."""


def resolve(root, version, expected_artefacts, *, online=False):
    """Return a validated outcome; raise EvidenceError on invalid evidence."""
```

`root` is a `Path`; `version` is canonical `X.Y.Z`; `expected_artefacts` is the
existing `standard_artefacts(version)` list passed by the caller, avoiding a
circular import or duplicated file map. The returned dictionary has exactly
these stable consumer keys:

```python
{
    "status": "published",
    "version": "1.10.0",
    "source_commit": "2d5a7ccfe684b052197697e3e65d265ca2fd6cb9",
    "manifest": manifest,
    "message": "Published evidence validated for v1.10.0",
}
```

Other non-error statuses are `development` (online lookup confirmed neither a
release nor a conflicting tag/draft) and `not-performed` (offline evidence unavailable).
They carry `manifest: None`, `source_commit: None` and a truthful message.
Do not cache a `development` result as evidence of future absence.

In `verify_release.py`, add `check(root, version, *, online=False)`, using that
resolver and the existing `verify(manifest, base=root)`. Successful published
comparison becomes `verified`; missing/tampered built outputs are errors.
Keep the original immutable release source identity distinct from the current
developer commit performing a comparison; do not require a tool-only descendant
to have the original release's HEAD. Explicit historical CLI verification still
requires the matching historical version/source outputs, never `--force` as a
substitute for rebuilding the correct source.

### Remote resolution, validation and cache

- Fix the repository/host to `urruegg/frontier-envisioning` on `github.com`.
  Invoke `gh` without a shell or interpolated script. Let `gh` use its existing
  authentication; never read/print token values.
- Establish repository access with a successful metadata GET and matching
  `full_name`. Enumerate authenticated release pages (`per_page=100`, at most
  20 pages), matching the exact `tag_name`, and require successful responses.
  An exhausted page limit, failed request or malformed response is an error,
  not proof of absence. Never call `releases/latest`.
- For no published match, inspect the exact tag through successful
  `git/matching-refs/tags/vX.Y.Z` output. Empty exact matches plus completed
  release enumeration permits `development`. Draft releases, an existing tag
  without complete published evidence and conflicting source identities fail.
- A published release must be non-draft, have the exact tag, and resolve to an
  annotated tag object whose target is the source commit. Do not treat
  `target_commitish: main` as a full commit.
- Expect exactly the current four named release downloads. Retrieve only
  those exact names into a temporary directory, never paths/URLs supplied by
  a manifest. Limit metadata/evidence JSON to 1 MiB, checksums to 16 KiB,
  each ZIP to 32 MiB and total downloads to 64 MiB; use 30-second API and
  120-second download subprocess timeouts. Enforce advertised and actual
  sizes; reject duplicate names, unexpected files and symlinks.
- Check the three unique lowercase SHA-256 checksum rows against the actual
  three payloads before consuming a manifest. Refuse absolute/nested/traversal
  checksum names. Validate both ZIPs using the standard-library ZIP reader.
- Manifest schema/version, four exact artefact rows/names/build paths, sizes,
  SHA-256 values and the sole supported `generated-date` normalisation must
  match `expected_artefacts`. Require empty `not_reproduced`, no duplicate or
  escaping path, and valid evidence objects. Hash all raw bytes, not reserialised
  JSON. The downloaded plugin hash must also match its reproduction row.
- Preserve the two observed source-evidence profiles:
  `local-tag-manual-publication/1.0` and
  `github-owner-dispatch-publication/1.0`. Both bind the exact source commit
  to the resolved annotated tag. The local profile additionally retains its
  exact source tag/tag-object proof; the workflow profile must have the
  matching intended tag/repository. Unknown profiles fail. Existing historical
  records without these profiles remain usable through the explicit retained
  `--manifest` interface, not relabelled as newly validated online provenance.
- Cache only after complete validation under ignored
  `build/release-evidence/<version>/<source-commit>/`, containing the four raw
  downloads and `evidence.json` with schema
  `frontier-release-evidence-cache/1.0`, repository, version, release ID,
  tag object/source commit and all four raw file digests.
  Use a temporary sibling and atomic promotion; never replace invalid prior
  evidence silently. An identical validated cache is reusable.
- Offline reuse requires the locally resolvable annotated exact-version tag
  to match the cache source/tag object, plus revalidation of all file digests,
  checksum rows, archive integrity and manifest constraints. Wrong/stale/
  malformed cache is an error; genuine absence reports `not-performed`.
  Cache consistency is not a signature or protection against a local actor
  replacing all evidence. CI always performs fresh authoritative resolution.

## Task 1: Validated published evidence and offline cache

**Files:** new evidence module and its new unit-test file only.

- [ ] Write `ReleaseEvidence` `unittest.TestCase` fixtures using temporary
  directories, a real tiny ZIP, the existing standard artefact list, synthetic
  annotated Git tags and a fake `gh` boundary. Use no live network.
  A fake remote must log method/endpoint/arguments and fail any unexpected
  request, so missing code cannot accidentally exercise the real CLI.
- [ ] Add these focused test methods:

  ```python
  class ReleaseEvidence(unittest.TestCase):
      def test_exact_published_version_is_validated_and_cached(self):
          with self.published_fixture() as fixture:
              result = self.resolve_fixture(fixture, online=True)
              self.assertEqual(result["status"], "published")
              self.assertEqual(result["version"], "1.10.0")
              self.assertEqual(result["source_commit"], fixture["source_commit"])
              self.assertEqual(result["manifest"], fixture["manifest"])
              self.assertTrue(fixture["cache_record"].is_file())
              self.assertFalse(any("releases/latest" in item for item in fixture["requests"]))

      def test_offline_absence_is_not_a_published_or_development_pass(self):
          with self.empty_fixture() as fixture:
              result = self.resolve_fixture(fixture, online=False)
              self.assertEqual(result["status"], "not-performed")
              self.assertIsNone(result["manifest"])
              self.assertIn("not performed", result["message"].lower())
              self.assertEqual(fixture["requests"], [])
  ```

  `published_fixture`, `empty_fixture` and `resolve_fixture` are test-local
  helpers implemented in this task, not new production interfaces. They must
  create the exact file inventories above and patch only the external GitHub
  boundary; the JSON/hash/ZIP/cache implementation runs for real.
- [ ] Run RED:
  `python -m unittest tests.unit.test_release_evidence -v`.
  A missing-module failure establishes only the initial scaffold; then add the
  API scaffold and observe actual missing-behaviour assertions fail before
  implementing validation. Retain the genuine result, not an invented count.
- [ ] Implement `resolve` with the concrete remote/cache policy above. Use
  focused private helpers for JSON, checksums and source binding, not a generic
  transport/release framework. Surface specific `EvidenceError` diagnostics.
- [ ] Add subtests for both observed profiles; pagination; a healthy empty
  lookup; repository 404; 401/403; timeout; bad JSON; wrong repository/version/
  source/tag; missing/duplicate/unexpected assets; size limits; path escape;
  malformed checksums; tampered plugin/manifest/SBOM/cache; invalid ZIP; draft
  or tag-without-release. Assert no cache writes/replacement on failure.
- [ ] Add offline valid-hit, source/tag mismatch, modified payload and genuine
  cache-miss cases. Prove an offline lookup never calls `gh`.
- [ ] Run GREEN with the same unit selector, then scoped Ruff. Commit only
  these two files using `feat: resolve exact-version published release evidence`,
  body `Refs #67` and the standard Copilot co-author trailer.
- [ ] Complete specification review, then correctness review. Fix reproduced
  findings before the dependent gate task. A reviewer does not publish or
  authenticate human acceptance.

## Task 2: Gate/CLI integration and existing CI read access

**Files:** gate builder slice in the file map. Start only after Task 1 reviews.

- [ ] In `tests/unit/test_release_tools.py`, add
  `PublishedReleaseVerification` tests exercising `check`, preserving existing
  `LocalReleaseManifest` tests unchanged. Write the following actual error
  boundary before implementing it:

  ```python
  def test_explicit_missing_manifest_is_an_error_not_an_unreleased_pass(self):
      verifier = load("tools/verify_release.py", "missing_explicit_manifest")
      with tempfile.TemporaryDirectory() as directory:
          missing = Path(directory) / "missing.json"
          output = io.StringIO()
          with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
              self.assertEqual(verifier.main(["--manifest", str(missing)]), 1)
          self.assertIn("ERROR", output.getvalue())
  ```

- [ ] Observe RED using:
  `python -m unittest tests.unit.test_release_tools.PublishedReleaseVerification -v`.
  Add real temporary artefact fixtures to test verified comparison, tampered/
  missing output, wrong-version explicit manifests and unchanged writer bytes.
  The published fixture must come from the validated resolver, not an
  arbitrary success-shaped result from an unverified manifest.
- [ ] Implement `check`; preserve the existing four-row comparison and
  generated-date normalisation. Add a developer-only `--online` option to the
  existing verifier. Default standalone behaviour is online when `CI=true`,
  otherwise offline. Explicit existing `--manifest`, `--force`, `--write`
  and `--local-source` paths retain their documented purpose; a named missing
  manifest now fails, rather than silently pretending to be unreleased.
- [ ] In `test_tools_core.py::DevGateWiring`, observe RED for exact-state
  propagation using a stubbed `check` result at the module boundary. Verify
  `ci` and `CI=true` select online resolution, local `--strict` only tightens
  installed-tool requirements, and errors stop the gate. Retain pipeline-test
  coverage and the original command ordering.
- [ ] Change `dev.py::cmd_verify_release` to call `check` and return its actual
  status/message to `RESULTS`; do not lose the distinction through an
  integer-only `call_main`. A local unavailable comparison must say
  `not performed` in the summary and end with
  `LOCAL CHECKS COMPLETED; published-release verification NOT PERFORMED`,
  not an unqualified `ALL GATES PASSED`. Verified/confirmed-development CI
  runs may retain `ALL GATES PASSED`. Check policy is explicit, never based
  solely on missing files under `releases/`.
- [ ] Test these complete mode decisions:

  ```python
  for command, environment, online in (
      (["check"], {"CI": ""}, False),
      (["check", "--strict"], {"CI": ""}, False),
      (["ci"], {"CI": ""}, True),
      (["check"], {"CI": "true"}, True),
  ):
      with self.subTest(command=command, environment=environment):
          self.assert_release_mode(command, environment, online)
  ```

  Implement `assert_release_mode` as a test-local helper that patches the
  other gate commands and captures the real release check call/summary.
  Do not contact GitHub from unit tests or change global environment permanently.
- [ ] In `.github/workflows/ci.yml`, add only the existing read-only token
  to the existing L1 gate step:

  ```yaml
  - name: Gate L1 (strict)
    env:
      GH_TOKEN: ${{ github.token }}
    run: python tools/dev.py ci
  ```

  Top-level `contents: read`, events, job names, action pins and publication
  permissions remain unchanged. No token is printed or read into Python.
  Add a focused YAML contract assertion in `test_release_tools.py` verifying
  that exact step-level binding and unchanged least-privilege/event boundaries.
- [ ] Qualify the pipeline test's old missing-file skip as unavailable offline
  retained evidence, not proof that the current version is unreleased.
  Keep its explicit historical comparison when the retained record exists;
  the later gate is authoritative for fresh online resolution.
- [ ] Run one combined GREEN selector:

  ```powershell
  python -m unittest tests.unit.test_release_evidence tests.unit.test_release_tools tests.unit.test_tools_core.DevGateWiring tests.unit.test_docs_validation.DocumentationRunner -v
  ruff check tools\release_evidence.py tools\verify_release.py tools\dev.py tests\unit\test_release_evidence.py tests\unit\test_release_tools.py tests\unit\test_tools_core.py tests\pipeline\test_release_reproduction.py
  ```

- [ ] Commit this integration separately; perform ordered specification then
  correctness review, including the actual CLI and summary output. Do not
  edit the protected release workflow to make a review test pass.

## Task 3: Active guidance and bounded human adoption

**Files:** documentation/rationale slice in the file map; no plugin files.
Start after the reviewed actual CLI/JSON contract from Task 2 is available.

- [ ] Update active release skill/agent and the three engineering guides:
  normal future release flow is maintainer review/merge plus the existing
  owner dispatch; automated evidence handling replaces manual retention.
  Explain local offline `not performed`, fresh CI checks, exact-version
  historical comparison and preserved failure/recovery boundaries.
  Qualify old tag-driven instructions with the actually adopted owner
  workflow; do not change unrelated #48 automation or assert deployment.
- [ ] Record the engineering requirement/verification qualification in
  PRD A.12/A.13 and solution-design B.9. Preserve historical prose/tables and
  migration receipt hashes; use clearly separated current text and any
  narrowly coupled document-contract regression, not edited historical goldens.
- [ ] Create Proposed ADR-0031, retaining ADR-0029's reserved historical number.
  State that checksum/cache consistency is not cryptographic attestation;
  private GitHub access and release-asset availability are CI dependencies.
  Link the actual human spec receipt; do not mark the ADR Accepted.
- [ ] Create `docs/engineering/release-evidence-adoption.md` with the one-time
  protected handover, also copied into the eventual PR description. A person
  adds this environment binding to the protected workflow's existing step:

  ```yaml
  - name: Gate L1
    env:
      GH_TOKEN: ${{ github.token }}
    run: python tools/dev.py check --strict
  ```

  Its job stays `contents: read`; the write token remains confined to the
  publisher. Before human adoption, the new strict resolver must fail honestly
  if that workflow lacks access; it must not skip the comparison to make
  publication appear ready. No agent dispatch, modified duplicate executable
  workflow or settings/guard workaround is allowed.
- [ ] State #52 disposition as awaiting actual verified replacement/adoption,
  not completed manual retention. Preserve its human-authored copy and all
  historical files. Suggest a truthful human closure record after adoption;
  do not close #52 or tick its old incomplete acceptance as implementation proof.
- [ ] Validate with `python tools/dev.py docs --strict` and scoped neutrality.
  Prose has no fictional code RED. Commit only this bounded documentation,
  with `Refs #67, #52, #9`. Complete independent document/contract review.

## Task 4: Stable exact-version proof and final handover

Do not run full builders while any worker is changing source or fixtures.
Stop/reproduce/fix unexpected differences; never weaken hashes or gates.

- [ ] Run the combined targeted tests from Task 2 and strict documentation
  validation after all slice reviews. Inspect only a failed check's relevant
  code if new evidence requires it.
- [ ] Run the actual read-only online resolver for current 1.10.1. Expect
  confirmed development only if GitHub successfully establishes absence of
  both release and conflicting exact tag; otherwise surface the real error.
- [ ] In the existing clean independent worktree at source
  `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9`, rebuild 1.10.0 normally.
  Use the new control-side resolver to download/check that exact release into
  ignored storage, then the existing comparison against those historical
  outputs. Expect four matching artefacts and the actual published plugin hash
  `9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`.
  Do not modify the old checkout's code/version, tags or protected records.
  This optional developer proof is read-only publication-wise, not a new
  maintainer download ceremony or real release dispatch.
- [ ] Compare offline cache hit against the same source, then a genuine
  no-cache temporary fixture. Record verified versus not-performed honestly.
  No new cache is copied into tracked source.
- [ ] Run the required exact command in strict CI mode using the existing
  authenticated `gh` session, without reading credentials:

  ```powershell
  $env:CI = 'true'
  python tools\dev.py check
  ```

  Expect `ALL GATES PASSED` only after successful online resolution or
  authoritative development outcome. Missing GitHub access is a blocker,
  not permission to disable the new check. Restore session-local environment
  afterwards. No renderer change is planned; L2 remains the normal automatic
  PR CI job, with a local L2 run only if a coupled change requires it.
- [ ] Verify `git diff --check`, clean committed source, unchanged plugin bytes
  and no protected/raster/history edits. Open a draft PR using the repository
  template, paste actual command summaries and separate local/CI/adoption
  results. Wait for automatic checks; never dispatch workflows by hand.
- [ ] Keep publication/merge/settings/guard actions and protected workflow
  adoption assigned to the human. Completion of eligible software is not
  a claim that protected adoption or #52 historical retention happened.

## Coverage, review and delivery

| Specification | Tasks/proof |
|---|---|
| RE-01 | Tasks 2–3: automated normal gate and accurately qualified release guidance; no retention PR |
| RE-02 | Tasks 1/4: exact-version/page/tag/source checks and actual historical-source comparison |
| RE-03 | Tasks 1–2: failure matrix, fresh CI policy and read-only credential wiring |
| RE-04 | Tasks 1–2/4: offline cache/miss/tamper cases and explicit non-pass summary |
| RE-05 | Tasks 1–2/4: reused four-artefact comparison, unchanged writers/records/plugin/raster files |
| RE-06 | Tasks 1–2: deterministic temporary fixtures, external-boundary stubs and observed RED/GREEN |
| RE-07 | Task 3: active versus historical guidance, Proposed ADR and real human adoption/#52 handover |
| RE-08 | Task 4: actual targeted/full gate, exact-source proof and truthful PR evidence |

Use one bounded builder for the evidence unit, then one for its gate consumer;
do not parallelise their shared-contract edits. Route the subsequent prose to
`docs-agent`. Reuse reviewer context only for same-task findings; specification
review precedes correctness. Create real child allocations only after actual
plan approval and before delegation. Do not infer formal review or protected
approval from advisory agent findings.

The plan author inspected the existing verifier, task runner, workflow,
ten-test baseline, release/pipeline/task-runner tests, shared helpers, active
guidance and actual published evidence. The plan was checked inline against
RE-01–08 for scope, interfaces, failure states and protected boundaries.
This plan introduces no implementation or claimed future test result.
