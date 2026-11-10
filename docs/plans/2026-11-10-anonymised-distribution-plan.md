# Anonymised distribution implementation plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Maintainer-directed inline cleanup; internal-audience assumption, no invented formal approval |
| Scope | Exact current-reference redaction, shared distribution validation and verified output |
| References | [Catalogue](README.md), [Issue #20](https://github.com/urruegg/frontier-envisioning/issues/20), [Idea](../ideas/2026-11-10-anonymised-distribution.md), [Spec](../specs/2026-11-10-anonymised-distribution-design.md), [Sprint](../sprints/SPRINT-002-anonymised-distribution.md) |

**Goal:** No legacy enterprise handle in current tracked content or new ZIPs,
with restricted engineering analyses excluded from the complete bundle.

**Architecture:** Reuse the existing package builder for shared byte inspection.
The complete builder already loads that module, so it can validate nested assets
without another policy implementation. Keep valid bytes/order unchanged.

**Tech Stack:** Python 3.11+ standard library, unittest/pytest, existing dev runner.

**Execution:** Inline in `chore/20-anonymised-distribution`; no delegated worker.
No new formal approval or readiness label is inferred from an unavailable form.

## 1. Prove the original failures

Files: create `tests/unit/test_distribution.py`; update the complete-bundle
fixture in `tests/unit/test_release_tools.py` to contain a classified analysis
decoy outside its exact expected output. Use real synthetic ZIPs, not fake ZIP
bytes, because nested members are now part of the output contract.

Example negative fixture:

```python
entries = [(b"Owner @sample_microsoft", "README.md")]
errors = packager.distribution_errors(entries)
assert any("enterprise account" in error for error in errors)
```

- [ ] Run `python -m pytest tests/unit/test_distribution.py tests/unit/test_release_tools.py -q --tb=short`.
  Expect missing privacy-guard assertions, absent explicit receipt redaction,
  unsafe builder success and the unapproved analysis entry to fail.
- [ ] Cover encoded identifiers, personal paths, credential patterns, classified
  metadata, benign privacy labels, nested/malformed ZIPs and ZIP comments.
- [ ] Verify unsafe inputs cannot overwrite the archive, inventory or checksums.

## 2. Implement the content and builder changes

Depends on step 1.

- [ ] In `tools/build_package.py`, implement
  `distribution_errors(entries: list[tuple[bytes, str]]) -> list[str]`.
  Reuse `check_repo.SECRET_PATTERNS`, `check_repo.FORBIDDEN_FILES` and
  `fe_lib.is_text`. Return redacted, actionable error locations. Construct the
  same ordered entry list, validate it, then write inventory/ZIP/checksum.
- [ ] In `tools/build_release.py`, remove the analysis wildcard/START row and
  validate its complete ordered entry list before writing output:

```python
errors = bp.distribution_errors(entries)
if errors:
    for error in errors:
        print("ERROR:", error)
    return 1
```

- [ ] Clean the eleven located current files: working agreement, Copilot
  instructions, root README, GitHub setup, intake receipt, two specs, three
  plans and bootstrap test. Keep receipt file hashes unchanged and explicitly
  declare the owner field redacted rather than silently changing provenance.
- [ ] Document the distribution boundary in plugin README, bundle START,
  engineering handbook, PRD/design development notes and changelog.

## 3. Verify and hand off

Depends on step 2.

- [ ] Run distribution, release-tools, tools-core and docs-contract tests together;
  expect all passing, including existing content/ID/hash/byte-shape guards.
- [ ] Run `python tools/dev.py package demo bundle`, then inspect the finished ZIP
  entries/nested content/comments and verify checksums. No analysis/intake
  records or real personal paths may ship.
- [ ] Generate the handoff in a version-specific directory containing only the
  current plugin ZIP, complete ZIP and checksums, using
  `python tools/build_package.py --dist dist/distribution-1.6.1` then
  `python tools/build_release.py --dist dist/distribution-1.6.1`.
- [ ] Extract the plugin to a temporary directory, run its install preparation
  script read-only and require verified=true, no problems, seven skill plans
  and matching file hashes. Remove only that temporary directory afterwards.
- [ ] Run a case-insensitive exact legacy-identifier search over current tracked
  file contents; require zero. This does not search or rewrite private history.
- [ ] Run `python tools/dev.py check --strict` and require `ALL GATES PASSED`;
  validate all new document links/catalogues and leave protected files unchanged.
- [ ] Record exact evidence in SPRINT-002, commit/push the bounded branch and
  create a draft PR using the repository template. A person reviews/merges.
  Keep the repository private; external distribution needs separate clearance.
