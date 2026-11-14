# Private GitHub Free Releases Implementation Plan

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-14 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Inline plan/readiness approved at 4450e46; tooling verified, human workflow edit pending |
| Scope | Exact-tag read-only preparation, verification and human publication |
| References | [Catalogue](README.md), [Implementation #47](https://github.com/urruegg/frontier-envisioning/issues/47), [Decision #46](https://github.com/urruegg/frontier-envisioning/issues/46), [Idea](../ideas/2026-11-14-free-private-releases.md), [Approved design](../specs/2026-11-14-free-private-releases-design.md), [SPRINT-009](../sprints/SPRINT-009-free-private-releases.md), [Proposed ADR-0029](../adr/0029-free-private-release-preparation.md) |

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans for inline execution, or superpowers:subagent-driven-development only if separately selected and approved. Execute the test-first steps in order. Human-only steps are stops, not delegated implementation.

**Goal:** Prepare the existing 1.10.0 source and future approved tags on GitHub
Free without repository-write CI, then hand verified files to the maintainer
for publication.

**Architecture:** Extend the existing release verifier rather than introduce
a second packaging framework. A reviewed main-branch workflow checks out
control and source separately, runs strict source gates and prepares exactly
four release files. Human verification includes an independent package build.

**Tech stack:** Existing Python 3.11+ standard-library tooling and unittest,
existing PyYAML workflow tests, pinned GitHub Actions, Microsoft SBOM tool and
Playwright. No plugin dependency or version change.

## Authority, prerequisites and isolation

The maintainer selected `approve-written-free-private-design` for the written
specification at `65f06ffa60e5a8d1b70d46993636105768a50452`. The separate
`approve-plan-inline` response then approved this plan/readiness at
`4450e46b2e5930ec41dee0f5218751b28d090dba` and selected inline execution.
Owner: `@urruegg`. No protected label-field change is inferred.

The recorded plan/readiness approval covers agent-editable implementation
only. Do not infer protected labels, assignment or milestone fields.
Use the existing clean isolated worktree; create
`chore/47-free-release-preparation` from the reviewed planning head.
Do not modify the primary checkout, move the existing tag or activate
`RELEASE_ENABLED`.

Agent-editable files after plan approval:

- `tools/verify_release.py`
- `tests/unit/test_release_tools.py`
- `docs/engineering/github-setup.md`, `docs/engineering/handbook.md`
- the current release context in `docs/solution-design.md`
- `.github/skills/frontier-release/SKILL.md`,
  `.github/skills/frontier-dev-loop/SKILL.md`
- `.github/agents/frontier-release-manager.agent.md`
- these linked planning/evidence records and their catalogues.

**Person only:** edit, stage, commit and push `.github/workflows/release.yml`;
accept the policy through review/merge; trigger workflows; create/publish
releases; change settings or protected labels; retain protected release files.
The agent supplies a proposal and verifies the saved result, never applies
the protected edit. No hooks, licences, CODEOWNERS, Azure or plugin edits.

## Task 1: Pin source identity before running its code

**Files:** `tests/unit/test_release_tools.py`, `tools/verify_release.py`.
**Depends on:** explicit plan/readiness approval.

- [ ] Establish the baseline with
  `python -m unittest tests.unit.test_release_tools -v`.
- [ ] Add a focused `ReleasePreparation` unittest class. Reuse the file's
  temporary-folder, `load`, `mock` and Git-fixture patterns. Commit only
  synthetic fixture data, using `t@example.com`, never the user's identity.
  Add this identity test around a real temporary annotated tag:

  ```python
  def test_source_identity_requires_the_exact_clean_annotated_tag(self):
      with self.source_fixture("1.10.0") as (root, commit):
          info = self.module.source_identity(root, "v1.10.0", commit)
          self.assertEqual(info["source_commit"], commit)
          for tag, expected in (
              ("main", commit), ("v1.10.0;echo unsafe", commit),
              ("v1.10.0", "0" * 40), ("v1.10.1", commit),
          ):
              with self.subTest(tag=tag, expected=expected):
                  with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                      self.module.source_identity(root, tag, expected)
          (root / "plugin/.claude-plugin/plugin.json").write_text(
              '{"version":"1.10.1"}\n', encoding="utf-8")
          with self.assertRaises(ValueError):
              self.module.source_identity(root, "v1.10.0", commit)
  ```

  Define `source_fixture` in that class with `contextlib.contextmanager`:
  make a temporary Git repository, write the declared plugin JSON, run the
  same local `git -c user.name=t -c user.email=t@example.com` init/add/commit
  pattern already used in this test file, create `git tag -a v1.10.0 -m test`,
  yield the root and actual HEAD, then let `TemporaryDirectory` clean up.
  Add subtests replacing the annotated tag with a lightweight tag and changing
  only the JSON version in a separately committed fixture. Both must fail.
- [ ] Run the same unittest command. Record RED for the missing new identity
  behaviour, not a missing package or unrelated baseline failure.
- [ ] Add `os` and `subprocess` imports and the following source inspection.
  Reuse `fe_lib.sha256_file` for later hashing; do not add another hash helper.

  ```python
  def git_value(root: Path, *args: str) -> str:
      return subprocess.run(
          ["git", "-C", str(root), *args], check=True,
          capture_output=True, text=True, encoding="utf-8",
      ).stdout.strip()

  def source_identity(source: Path, tag: str, expected: str) -> dict[str, str]:
      if not re.fullmatch(r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", tag):
          raise ValueError("release tag must be canonical vX.Y.Z")
      if not re.fullmatch(r"[0-9a-f]{40}", expected):
          raise ValueError("expected source commit must be a full SHA")
      source = source.resolve()
      if Path(git_value(source, "rev-parse", "--show-toplevel")).resolve() != source:
          raise ValueError("source must be the checkout root")
      ref = "refs/tags/" + tag
      if git_value(source, "cat-file", "-t", ref) != "tag":
          raise ValueError("release tag must be annotated")
      actual = git_value(source, "rev-parse", ref + "^{commit}")
      if actual != expected or git_value(source, "rev-parse", "HEAD") != expected:
          raise ValueError("tag, expected commit and source HEAD must agree")
      if git_value(source, "status", "--porcelain", "--untracked-files=no"):
          raise ValueError("source has tracked changes")
      value = json.loads((source / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
      if not isinstance(value, dict) or value.get("version") != tag[1:]:
          raise ValueError("tag does not match the source plugin version")
      return {"source_tag": tag, "source_commit": actual,
              "tag_object": git_value(source, "rev-parse", ref)}
  ```

- [ ] Add the `--inspect-source PATH`, `--tag`, `--expected-commit` CLI route.
  Require both strings before calling `source_identity`. Before inspecting
  source, require `GITHUB_ACTIONS=true`, `GITHUB_EVENT_NAME=workflow_dispatch`,
  `GITHUB_REF=refs/heads/main` and
  `GITHUB_REPOSITORY=urruegg/frontier-envisioning`. Read only these named,
  non-sensitive variables; no token/environment dump. A non-main dispatch
  must fail explicitly, not produce a skipped-success result.
- [ ] Run the focused tests GREEN. Add a CLI negative case proving an invalid
  context returns non-zero with a specific stderr message before any write.

## Task 2: Reuse the manifest writer and verify the four-file handover

**Files:** `tools/verify_release.py`, `tests/unit/test_release_tools.py`.
**Depends on:** Task 1.

- [ ] Add a fixture-backed candidate test before changing the implementation:

  ```python
  def test_candidate_rejects_tampering_even_with_a_rewritten_receipt(self):
      with self.candidate_fixture() as case:
          self.module.verify_candidate(**case)
          package = case["candidate"] / "release/frontier-envisioning-plugin-1.10.0.zip"
          package.write_bytes(b"changed package")
          self.rewrite_fixture_checksums_and_receipt(case["candidate"])
          with self.assertRaises(ValueError):
              self.module.verify_candidate(**case)
  ```

  Define `candidate_fixture` using the same real source fixture and a separate
  temporary candidate directory. Build a small deterministic ZIP in the
  source `dist` and copy it as the CI candidate; create a manifest containing
  its real bytes/hash plus synthetic, explicitly test-only CI facts.
  `rewrite_fixture_checksums_and_receipt` recalculates those actual fixture
  files, not the independent ZIP. Thus the failure tests independent
  reproduction, not just a stale checksum.

  In the same fixture test group, remove/add one asset, alter one checksum
  line, corrupt the receipt shape, change the source/workflow binding, and
  add a false `approved` or `signature` evidence field. Each must fail.
  Retain existing manifest/reproduction tests.
- [ ] Record focused RED. Implement these exact public operations in the
  existing module, not a generic release framework:

  | Operation | Required behaviour |
  |---|---|
  | `source_identity(source, tag, expected)` | Task 1; reused before preparation and for the independent checkout |
  | `prepare_source(source, tag, expected)` | Validate source and CI context, emit manifest and copy only the exact plugin into `ROOT / "build/release-preparation/release"`; reject any existing candidate directory and any source/output overlap |
  | `finalize_candidate()` | Require exactly plugin/manifest/SBOM, generate canonical checksums and the internal receipt, then validate the completed handover |
  | `verify_candidate(candidate, source, tag, expected, workflow)` | Read-only verification against the independent source package and expected reviewed workflow SHA; never requires synthetic CI variables locally |

  Extend `write_manifest` compatibly, with an optional `base` whose effective
  default remains the current `ROOT`, and `evidence: dict | None = None`;
  change its artefact
  reads from `ROOT / build_path` to `base / build_path`. Preserve the existing
  default output and normalization behaviour. In preparation mode add
  `build_evidence` and truthful preparation provenance; do not change the
  published manifest schema/artefact semantics. Correct the verifier's
  docstrings to distinguish internal reproduction entries from uploaded
  release assets.

  The one source of publication names is:

  ```python
  def publication_names(version: str) -> tuple[str, ...]:
      return (standard_artefacts(version)[0][0], "release-manifest.json",
              "sbom-spdx.zip", "SHA256SUMS.txt")
  ```

  Generate/verify canonical checksums with the shared hash helper:

  ```python
  checksum_text = "".join(
      f"{sha256_file(assets / name)}  {name}\n"
      for name in sorted(publication_names(version))
      if name != "SHA256SUMS.txt"
  )
  ```

  Reject extra/missing entries, directories or symlinks in the release asset
  directory. Compare checksum bytes as UTF-8/LF, not by accepting unvalidated
  path names from checksum text.

  Build evidence contains exactly the fields/types in the approved design.
  `workflow_commit` comes from `GITHUB_WORKFLOW_SHA` and must match the clean
  control checkout HEAD, not the source commit copied twice.
  `workflow_ref` must be
  `urruegg/frontier-envisioning/.github/workflows/release.yml@refs/heads/main`.
  Run ID/attempt are positive integers read from their named GitHub
  variables; construct the approved-repository run URL from the actual ID.
  Keep `native_attestation=not-provided`; no human approval/signature fields.

  The internal `receipt.json` has schema
  `frontier-release-preparation/1.0`, the exact same `build_evidence` object
  and a `files` mapping of all four publication names to their actual
  SHA-256 digests. It is not a fifth release asset or a signature.
  Verify its exact shape, name set, evidence match and all digests.
  Keep the upload ID/digest outside it until the platform returns them.
  Share these file-contract checks between finalization and publisher
  verification; the independent-source comparison belongs only to the
  publisher path and must not be falsely claimed during CI finalization.

  Independent verification additionally requires the actual clean source
  identity, the manifest's matching tag object/source commit, a full matching
  expected workflow SHA and exact bytes/hash of that checkout's rebuilt
  `dist/frontier-envisioning-plugin-<version>.zip`. Check the package entry's
  recorded byte length/hash too. Do not require independently regenerated
  SBOM/run metadata to be byte-identical or require demo files for this
  package-only check. Existing `verify()` still owns the wider historical
  reproduction comparison.
- [ ] Put `--write` and the four preparation modes in one mutually exclusive
  argparse group. Add `--prepare-source PATH`, `--finalize-candidate`,
  `--verify-candidate PATH`, `--independent-source PATH`,
  `--expected-workflow SHA`. Require mode-specific arguments explicitly.
  Route successful operations to exit 0 only after their checks complete.
  Catch only `ValueError`, `OSError` and `subprocess.CalledProcessError` for
  these new modes, print their specific failure to stderr and return 1.
  Do not hide existing legacy verifier failures or introduce skipped-success
  fallbacks. Write every generated text file as UTF-8/LF.
- [ ] Run the focused tests GREEN, including preservation of legacy
  `write_manifest` and normalization results. Run scoped Ruff:
  `python -m ruff check tools/verify_release.py tests/unit/test_release_tools.py`.

## Task 3: Test the read-only workflow, then stop for the human edit

**Files:** `tests/unit/test_release_tools.py`; human-only
`.github/workflows/release.yml`.
**Depends on:** Task 2.

- [ ] Replace the two obsolete native-profile workflow assertions with
  behavioural contracts for the accepted Free/private profile. Use
  `yaml.BaseLoader` so the YAML `on` key is not parsed as a boolean.

  ```python
  def test_preparation_has_no_automatic_or_release_write_path(self):
      import yaml
      workflow = yaml.load(
          (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8"),
          Loader=yaml.BaseLoader,
      )
      self.assertEqual(set(workflow["on"]), {"workflow_dispatch"})
      self.assertEqual(workflow["permissions"], {"contents": "read"})
      self.assertEqual(set(workflow["jobs"]), {"build"})
      job = workflow["jobs"]["build"]
      self.assertEqual(job["permissions"], {"contents": "read"})
      self.assertNotIn("environment", job)
      steps = {step.get("name"): step for step in job["steps"]}
      self.assertEqual(steps["Check out control"]["with"]["ref"], "${{ github.workflow_sha }}")
      self.assertEqual(steps["Check out source"]["with"]["ref"], "${{ inputs.expected_commit }}")
  ```

  Add the ordering assertion for source inspection, strict L1, strict L2,
  bundle, preparation, pinned SBOM, finalize and successful artifact upload.
  Verify neither checkout persists credentials and no step receives a
  repository secret/write credential. Preserve action-pin validation.
- [ ] Run the focused tests and record the expected RED against the old
  automatic/native workflow.
- [ ] **STOP.** Give the maintainer the following complete replacement.
  Only the maintainer saves, stages, commits and pushes this protected file.
  Do not run a shell/patch/script to write it or push that protected commit
  on the person's behalf.

  ```yaml
  # Human-maintained: read-only preparation; a person creates/publishes releases.
  name: release

  on:
    workflow_dispatch:
      inputs:
        tag:
          description: Existing annotated tag, for example v1.10.0
          required: true
          type: string
        expected_commit:
          description: Reviewed full source commit SHA
          required: true
          type: string

  permissions:
    contents: read

  jobs:
    build:
      name: Prepare release ${{ inputs.tag }}
      runs-on: ubuntu-latest
      timeout-minutes: 30
      permissions:
        contents: read
      env:
        SOURCE_TAG: ${{ inputs.tag }}
        EXPECTED_COMMIT: ${{ inputs.expected_commit }}
        PLAYWRIGHT_BROWSERS_PATH: ${{ github.workspace }}/build/playwright-browsers
      steps:
        - name: Check out control
          uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
          with:
            ref: ${{ github.workflow_sha }}
            path: control
            persist-credentials: false
        - uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7
          with:
            python-version: "3.12"
        - name: Check out source
          uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
          with:
            ref: ${{ inputs.expected_commit }}
            path: source
            fetch-depth: 0
            persist-credentials: false
        - name: Inspect exact source and control context
          run: python control/tools/verify_release.py --inspect-source source --tag "$SOURCE_TAG" --expected-commit "$EXPECTED_COMMIT"
        - uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7
          with:
            node-version: "22"
        - name: Install source development dependencies
          working-directory: source
          run: |
            python -m pip install -r requirements-dev.txt
            if [ -f package-lock.json ]; then npm ci --no-audit --no-fund; else npm install --no-audit --no-fund; fi
        - name: Gate L1 (strict) on the tag
          working-directory: source
          run: python tools/dev.py ci
        - name: Gate L2 on the tag
          working-directory: source
          run: |
            npx playwright install --with-deps chromium
            python tools/dev.py site e2e --strict
        - name: Build internal bundle
          working-directory: source
          run: python tools/dev.py bundle
        - name: Prepare exact publication candidates
          run: |
            python control/tools/verify_release.py --prepare-source source --tag "$SOURCE_TAG" --expected-commit "$EXPECTED_COMMIT"
            python source/tools/release_notes.py "$SOURCE_TAG" > control/build/release-preparation/release-notes.md
        - name: Check the extracted package
          run: |
            version="${SOURCE_TAG#v}"
            python -m zipfile -e "control/build/release-preparation/release/frontier-envisioning-plugin-${version}.zip" control/build/release-extracted
            mkdir control/build/installed-empty
            python control/build/release-extracted/install/prepare_install.py --root control/build/release-extracted --installed control/build/installed-empty
        - name: SBOM (SPDX, pinned Microsoft SBOM tool)
          run: |
            curl -sSfLo "$RUNNER_TEMP/sbom-tool" https://github.com/microsoft/sbom-tool/releases/download/v4.1.5/sbom-tool-linux-x64
            echo "bf5d4f99bc98c119d549d08fc02ae92598a7a42772f17317c01031a92632e05b  $RUNNER_TEMP/sbom-tool" | sha256sum --check --strict
            chmod +x "$RUNNER_TEMP/sbom-tool"
            "$RUNNER_TEMP/sbom-tool" generate -b control/build/release-preparation/release -bc source/plugin -pn frontier-envisioning -pv "${SOURCE_TAG#v}" -ps "Microsoft Innovation Hub Switzerland" -nsb "https://github.com/${GITHUB_REPOSITORY}"
            (cd control/build/release-preparation/release/_manifest && zip -qr ../sbom-spdx.zip .)
            python -c "import shutil; shutil.rmtree('control/build/release-preparation/release/_manifest')"
        - name: Finalize and verify candidate files
          run: python control/tools/verify_release.py --finalize-candidate
        - name: Upload successful preparation
          id: upload
          uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7
          with:
            name: release-preparation-${{ inputs.tag }}
            path: control/build/release-preparation/
            if-no-files-found: error
            retention-days: 90
        - name: Record actual platform artifact identity
          env:
            ARTIFACT_ID: ${{ steps.upload.outputs.artifact-id }}
            ARTIFACT_DIGEST: ${{ steps.upload.outputs.artifact-digest }}
          run: |
            test -n "$ARTIFACT_ID"
            test -n "$ARTIFACT_DIGEST"
            printf 'Artifact ID: %s\nArtifact digest: %s\n' "$ARTIFACT_ID" "$ARTIFACT_DIGEST" >> "$GITHUB_STEP_SUMMARY"
  ```

  Do not override `GITHUB_SHA`, `GITHUB_REF` or other platform facts to pretend
  this manual main-branch run was a tag-push run.

- [ ] The maintainer commits/pushes **only the protected workflow file** to
  the implementation branch. Do not open a PR or dispatch that branch while
  its new helper/tests are not yet committed. The agent may then commit/push
  its separately reviewed, non-protected changes; it never stages or pushes
  the protected change. If a guard denies an action, stop rather than bypass it.
- [ ] After the real saved edit, run focused tests GREEN and inspect only
  relevant failed hunks if needed. No parser fixture substitutes for the
  actual workflow file's read-only/trigger/order checks.

## Task 4: Align active guidance without rewriting history

**Files:** the current engineering/customisation files listed above,
ADR-0029 and sprint records. **Depends on:** Tasks 1-3 and actual approval
evidence; no runtime change.

- [ ] Replace current setup/handbook/release-skill/dev-loop/release-manager
  native-profile instructions with this exact operational sequence:

  > Keep the legacy publication flag off. A person reviews and merges the
  > preparation control revision, preserves or creates the annotated source
  > tag, and manually dispatches preparation from main with the expected
  > source commit. CI runs strict source gates and provides candidates, not a
  > draft or publication. Independently rebuild and verify the package,
  > record source/control/run/artifact-qualified human sign-off, then create
  > and publish the normal GitHub Release as a person. Retain the actual
  > release manifest through the protected human follow-up process.

  Keep the explicit no-cryptographic-attestation assurance limit and
  GitHub-only opt-in announcement policy beside this sequence.
- [ ] Update only the current engineering/release context of solution-design
  B.9 to link this accepted profile and actual verification evidence.
  Do not edit frozen historical suffixes, old sprint proof, released
  manifests or the plugin README just to restate engineering policy.
  Preserve every human-only restriction and the outstanding protected
  legacy session-start routing limitation under #8.
- [ ] Record actual plan/readiness and human protected-file commit evidence.
  ADR status changes only when its required real human acceptance occurs;
  never infer a formal review or protected label.
- [ ] Run `python tools/dev.py docs --strict`.

## Task 5: Verify the implementation and hand over the pull request

**Depends on:** Tasks 1-4; the human protected edit must actually be present.

- [ ] Run the focused unittest/Ruff command again, then
  `python tools/dev.py check --strict`. Require the actual
  `ALL GATES PASSED` summary; retain its source commit/log and paste the
  exact summary into the eventual PR.
- [ ] Check the branch changed only approved tooling/tests/current guidance
  and the separately human-authored workflow. Verify plugin source/version,
  `v1.10.0` and frozen records are unchanged.
- [ ] Commit agent-owned changes with `Refs #47` and the required Copilot
  co-author trailer. Do not stage the protected workflow. Push only after
  the human's protected commit is already on the remote branch.
- [ ] Read the repository PR template, fill every heading/checklist
  truthfully, disclose the human workflow edit and no-attestation model,
  and open a draft PR. No manual result or L3 execution is inferred.
- [ ] Verify actual L1/L2/IaC PR results, address findings, then hand off.
  A person records head-qualified sign-off and accepts/merges the change.
  Agent review is advisory, never an independent human approval.

## Task 6: Human preparation and publication of the existing 1.10.0 tag

**Depends on:** human-merged implementation/policy, successful actual main
control checks, actual manual release-check evidence.
**Owner:** `@urruegg`; the agent observes and verifies read-only.

- [ ] Verify legacy activation remains unset/false. Do not change visibility,
  add another reviewer account, rerun the skipped original workflow or move
  the existing tag.
- [ ] A person dispatches the new main-branch workflow with tag `v1.10.0`
  and expected commit `2d5a7ccfe684b052197697e3e65d265ca2fd6cb9`.
  Verify actual source tag object
  `5f9d21953db9c968ae56ac6d485baff3fc09b0ce`, control SHA, run/attempt,
  all gates, SBOM, final files and returned artifact ID/digest.
- [ ] Download the **single** successful preparation artifact as an
  authorised reader. Compare the downloaded ZIP's SHA-256 with the
  authenticated platform artifact digest before extracting it into
  `build/release-download`. Do not trust the unsigned receipt as its own
  authority or compare the digest of a different outer "download all" ZIP.
- [ ] From the clean reviewed control checkout, independently prepare source:

  ```powershell
  git clone --no-hardlinks --no-checkout . build\independent-source
  git -C build\independent-source checkout --detach v1.10.0
  python build\independent-source\tools\dev.py package
  ```

  Require all three commands to succeed. They create a separate source
  checkout, not a new tag or a product change. Do not manufacture CI
  variables or call CI-only preparation locally.
- [ ] After personally comparing the receipt's workflow/source/run fields
  with the authenticated successful run and reviewed control revision:

  ```powershell
  $receipt = Get-Content -LiteralPath build\release-download\receipt.json -Raw | ConvertFrom-Json
  python tools\verify_release.py --verify-candidate build\release-download --independent-source build\independent-source --tag v1.10.0 --expected-commit 2d5a7ccfe684b052197697e3e65d265ca2fd6cb9 --expected-workflow $receipt.build_evidence.workflow_commit
  ```

  Exit 0 verifies file consistency and exact independent package bytes, not
  an authenticated cryptographic builder. Compare the newly measured plugin
  hash with the prior local reference
  `9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89`;
  investigate any difference, never substitute the older candidate.
- [ ] Preserve the actual four digests, tag/source/control, run/attempt,
  artifact ID/digest, independent reproduction and actual manual-check
  evidence in the human sign-off. CI artifacts expire; do not treat their
  download/log retention as a permanent release record.
- [ ] A person creates/reviews/publishes the normal 1.10.0 Release using the
  prepared change summary, actual links and exactly four allowed files.
  Inspect a real authorised-reader download afterwards. Owner access does
  not prove everyone else's permissions or a Cowork installation.
- [ ] A person preserves the actual manifest under
  `releases/1.10.0/manifest.json` through the existing follow-up process.
  Verify immutable reproduction separately; never let a missing/changed
  baseline become an excuse to suppress a gate.
- [ ] Record publication/download evidence on the linked work items. The
  Release is the GitHub announcement; subscribers opt in. Do not claim every
  contributor received it, or create npm/container/Teams/email distribution.

## Completion evidence, not predictions

Before claiming implementation complete: actual focused RED/GREEN,
source-qualified full gate, real protected-file authorship and PR checks.
Before claiming publication complete: actual new preparation run, independent
package identity, human sign-off, published release/download and retained
manifest. Actual checkpoint evidence belongs in SPRINT-009; unchecked task
instructions are not a claim that those future outcomes occurred.
