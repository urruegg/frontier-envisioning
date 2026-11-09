# Frontier Envisioning M0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for inline execution, or superpowers:subagent-driven-development when independent implementation tasks warrant delegation. Steps use checkbox syntax for tracking.

**Goal:** Preserve the supplied 1.4.0 product in the existing repository and establish evidenced, controlled engineering gates without silently changing product behavior.

**Architecture:** Import the audited export into a branch while retaining target Git history, source layout and product bytes. Harden the engineering harness in separate changes. Native HubWorks adaptation and Azure showcase deployment remain separate approved workstreams.

**Tech Stack:** PowerShell on Windows; Python 3.12; Node 22; existing unittest/pytest, Ruff, ESLint, happy-dom and Playwright tooling; GitHub Actions and human-controlled repository policy.

---

## Execution authorization

Update, 9 November 2026: the user confirmed Microsoft approval to use the
private `urruegg/frontier-envisioning` repository and requested proceeding.
The earlier commit/push request now applies to this approved destination.
Preserve the original work connection and intake branch, base the new intake
on the personal repository's `main`, and keep server administration, protected
ownership files, merges, releases and deployments with people.

The user initially approved this plan's creation, **documentation only**.
Subsequent approval allowed local intake on a new branch, planned local
engineering changes and isolated Python 3.11/Node 24 validation, without
commits, pushes, administration, vendoring or deployment.

Execution results are in [M0 evidence](../intake/m0-evidence.md). Source intake
and local checks are recorded there. Root-cause investigation resolved the HTML
hash through build-time LF output and canonicalised identity archive metadata.
The original OneDrive artifact was subsequently recovered and verified. A
guarded historical raster profile resolves the identity ZIP mismatch without
changing shipped source or release records; all four artifact hashes and local
strict L1 now pass. Remote/tenant acceptance remains a separate human action.
`--no-png` remains development-only; future versions need their own renderer
profile rather than silently reusing the 1.4.0 fixture.

Read the [approved intake specification](2026-11-08-cowork-intake-design.md).
Local import, source execution and isolated dependency restoration were approved.
Committing, pushing and external operations still require separate approval.
The original checklist below is retained as the plan; actual completion and
blocked steps are recorded in the M0 evidence.

GitHub administration, protected-file changes, third-party vendoring, merges,
release tags/publication and Azure changes require their specific maintainer
approvals. Do not infer those permissions from an approved implementation plan.

Default to inline execution for this single intake trace. Do not launch a
subagent to recheck the same work.

## File responsibilities

| Files after import | Responsibility and ownership |
|---|---|
| `plugin/**`, `src/renderer/**` | Preserved product and renderer; no behavior edits in M0 |
| `plugin/install/plugin-install.json`, generated blueprint template | Tracked generated files; their existing generators must reproduce them |
| `tools/dev.py` | Small CI/test-selection correction |
| `tools/bootstrap_github.py` | Required-check schema correction; not a shortcut to creating/pushing another repo |
| `tests/unit/test_tools_core.py`, `tests/unit/test_release_tools.py` | Regression tests for the engineering changes |
| `package-lock.json`, `requirements-dev.txt` | Reproducible development dependency graph |
| `.github/workflows/*.yml` | Pinned Actions; release checks and approval environment; protected files need maintainer permission |
| `.github/CODEOWNERS` | Eligible ownership, maintained by an authorized person |
| `.agents/skills/**` | Optional approved Superpowers vendor snapshot, never personal/global installation changes |
| `docs/intake/source-inventory.json` | Relative paths, source hashes and intake classification |
| `docs/intake/m0-evidence.md` | Actual checks, failures/skips, artifact hashes, policy and host evidence |
| `docs/engineering/**`, README, VS Code tasks | Commands and evidence expectations updated to match implementation |

Keep these two planning documents. Do not copy source Git metadata, caches,
dependencies, customer output or generated distributions.

## Task 1: Resolve the execution and governance gates

**Files:** read the specification and export
[working agreement](../../AGENTS.md),
[notices](../../plugin/THIRD-PARTY-NOTICES.md),
and [release record](../../releases/1.4.0/manifest.json).

- [ ] Obtain approval for M0-A source import and local execution.
- [ ] Obtain approval to copy the supplied human-maintained configuration files.
      Separate copying from permission to modify them later.
- [ ] Record whether the internal analysis documents may enter this private
      repository. If not approved, stop and revise the exact import inventory;
      do not silently discard product documentation.
- [ ] Record original-artifact availability. If originals remain unavailable,
      accept only reproduction against supplied hash records, with that explicit
      provenance limitation.
- [ ] Confirm an eligible reviewer and code owner, and the mandatory GitHub
      controls available on this private repository. The source `@urruegg`
      account has no target access; do not assume its reviews satisfy CODEOWNERS.
- [ ] Confirm the authenticated publishing path can write workflows. The
      initially observed CLI scopes did not list `workflow`; any authentication
      refresh is a human action, not an agent operation.

Expected result: written permission boundaries and no unresolved mandatory
ownership/control requirement concealed as "setup complete." If a required
control is unavailable, keep release/deployment blocked or approve a compliant
alternative. Do not make the repository public to obtain features.

## Task 2: Create the preservation branch and copy only audited source

**Files:** import the root allowlist below; create
`docs/intake/source-inventory.json`; preserve target Git metadata and planning
documents.

- [ ] Verify the destination still has only the expected documentation changes.

```powershell
Set-Location 'C:\Users\urruegg\source\urruegg_microsoft\frontier-envisioning'
git --no-pager status --short --branch
git remote get-url origin
```

Expected: `main` tracking `origin/main`; only the two approved plan files under
`docs/`; origin is the existing frontier-envisioning repository. Stop on any
unexpected user changes.

- [ ] Create the branch without reinitializing Git or changing remotes.

```powershell
git switch -c chore/cowork-intake-1.4.0
```

Expected: a new local branch; the initial commit and `origin` remain intact.

- [ ] Run this bulk-copy preflight and import only after Task 1 approval.
      It rejects unexpected roots, reparse points and conflicting existing
      files. The three starter-file replacements require the approved import
      scope; license meaning must remain unchanged.

```powershell
$ErrorActionPreference = 'Stop'
$source = 'C:\Users\urruegg\source\urruegg_microsoft\frontier-envisioning-github-repo\frontier-envisioning'
$target = 'C:\Users\urruegg\source\urruegg_microsoft\frontier-envisioning'
$roots = @(
  '.devcontainer', '.editorconfig', '.gitattributes', '.github', '.gitignore',
  '.pre-commit-config.yaml', '.vscode', 'AGENTS.md', 'CHANGELOG.md',
  'CONTRIBUTING.md', 'LICENSE', 'README.md', 'SECURITY.md', 'azure.yaml',
  'backlog', 'docs', 'eslint.config.mjs', 'infra', 'package.json',
  'playwright.config.mjs', 'plugin', 'pyproject.toml', 'releases',
  'requirements-dev.txt', 'site', 'src', 'tests', 'tools'
)
$unknown = @(Get-ChildItem -LiteralPath $source -Force |
  Where-Object { $_.Name -notin $roots })
if ($unknown.Count) { throw "Unexpected export roots: $($unknown.Name -join ', ')" }
$entries = @(Get-ChildItem -LiteralPath $source -Force -Recurse)
if ($entries | Where-Object {
  $_.Attributes -band [IO.FileAttributes]::ReparsePoint
}) { throw 'Reparse points require separate review; import stopped.' }
$files = @($entries | Where-Object { -not $_.PSIsContainer })
$replace = @('README.md', '.gitignore', 'LICENSE')
$inventory = foreach ($file in $files) {
  $relative = [IO.Path]::GetRelativePath($source, $file.FullName)
  $destination = Join-Path $target $relative
  $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  if ((Test-Path -LiteralPath $destination) -and $relative -notin $replace) {
    $existing = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($existing -ne $hash) { throw "Conflicting target file: $relative" }
  }
  [pscustomobject]@{
    path = $relative.Replace('\', '/')
    sha256 = $hash
    classification = $(if ($relative.StartsWith('docs\analysis\')) {
      'internal-review-required'
    } else { 'source-not-public-clearance' })
  }
}
foreach ($file in $files) {
  $relative = [IO.Path]::GetRelativePath($source, $file.FullName)
  $destination = Join-Path $target $relative
  New-Item -ItemType Directory -Path (Split-Path $destination) -Force | Out-Null
  Copy-Item -LiteralPath $file.FullName -Destination $destination -Force
  if ((Get-FileHash -LiteralPath $file.FullName).Hash -ne
      (Get-FileHash -LiteralPath $destination).Hash) {
    throw "Copied bytes differ: $relative"
  }
}
New-Item -ItemType Directory -Path (Join-Path $target 'docs\intake') -Force | Out-Null
[ordered]@{
  baselineVersion = '1.4.0'
  repository = 'urruegg_microsoft/frontier-envisioning'
  files = @($inventory)
} | ConvertTo-Json -Depth 5 |
  Set-Content -LiteralPath (Join-Path $target 'docs\intake\source-inventory.json') -Encoding utf8
```

Expected: admitted files have identical source/destination bytes; no target
`.git` changes; both approved plan files survive. The inventory is not a
public-distribution approval.

- [ ] Inspect only import conflicts/classification questions and the exact
      staging list. Obtain maintainer permission before protected-file edits.
- [ ] When commits are authorized, stage only admitted source and documents.
      Create a preservation commit, not a release tag.

```powershell
git add -- .devcontainer .editorconfig .gitattributes .github .gitignore .pre-commit-config.yaml .vscode AGENTS.md CHANGELOG.md CONTRIBUTING.md LICENSE README.md SECURITY.md azure.yaml backlog docs eslint.config.mjs infra package.json playwright.config.mjs plugin pyproject.toml releases requirements-dev.txt site src tests tools
git commit -m "chore: intake Frontier Envisioning 1.4.0 source baseline" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

Do not merge, push `main`, create a tag, seed fifty issues, or run bootstrap
`--apply` as part of copying source.

## Task 3: Restore an isolated, reproducible development toolchain

**Files:** create `package-lock.json`; pin `requirements-dev.txt`; update
the existing pre-commit dependency pins after resolved versions are known.

- [ ] Prefer the supplied Python 3.12/Node 22 devcontainer after reviewing its
      automatic setup command. Alternatively use an explicitly selected local
      Python 3.12 environment. Do not install into the shared/global Python.
- [ ] Once the imported manifests exist and installation is authorized, restore
      dependencies in that isolated environment.

```powershell
python --version
node --version
python -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency restoration failed.' }
npm install --package-lock-only --ignore-scripts --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw 'Node dependency resolution failed.' }
npm ci --ignore-scripts --no-audit --no-fund
if ($LASTEXITCODE -ne 0) { throw 'Node dependency restoration failed.' }
python -m pip freeze > requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency pin generation failed.' }
npx playwright install chromium
if ($LASTEXITCODE -ne 0) { throw 'Chromium installation failed.' }
```

Expected: the selected environment reports Python 3.12 and Node 22; the lockfile
exists; Python requirements carry resolved versions; the explicit browser
installation succeeds. Stop if the intended environment is unavailable.
The current local Python 3.14/Node 24 availability does not satisfy this parity
check by itself.

- [ ] Resolve the exact PyYAML and Ruff versions for the pre-commit environment.

```powershell
python -c "from importlib.metadata import version; print('PyYAML==' + version('PyYAML')); print('ruff==' + version('ruff'))"
```

Use those exact output strings in the existing
`.pre-commit-config.yaml` `additional_dependencies` list through a reviewed
patch. Do not invent versions or install another dependency resolver.

- [ ] Run the smallest tool-availability check and record missing tools as
      failures/skips, not success.

```powershell
python tools\dev.py doctor
python tools\dev.py lint --strict
```

- [ ] Commit only the dependency and pre-commit changes when authorized.

```powershell
git add -- package-lock.json requirements-dev.txt .pre-commit-config.yaml
git commit -m "chore: lock the intake development toolchain" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Task 4: Establish the unchanged 1.4.0 reproduction evidence

**Files:** read `releases/1.4.0/manifest.json`; generate ignored `build/` and
`dist/`; create `docs/intake/m0-evidence.md`.

- [ ] Run the existing explicit checks; do not regenerate source to hide drift.

```powershell
python tools\assemble_template.py --check
python tools\check_repo.py --strict
python tools\dev.py ci
python tools\dev.py test-all --strict
python tools\dev.py site e2e --strict
```

Expected: no template drift, all strict checks pass, both pipeline wrappers run,
and browser tests pass. At this point the separate `test-all` invocation is
necessary because the supplied CI runner omits pipeline tests.

- [ ] Enforce the mandatory baseline record before the reproduction command.

```powershell
if (-not (Test-Path -LiteralPath 'releases\1.4.0\manifest.json')) {
  throw 'The 1.4.0 baseline manifest is mandatory.'
}
python tools\verify_release.py --manifest releases\1.4.0\manifest.json --force
if ($LASTEXITCODE -ne 0) { throw 'The build does not reproduce the baseline record.' }
```

Expected: four recorded artifacts reproduce. Compare the plugin ZIP, identity
ZIP and catalogue raw hashes; compare the blueprint using only its documented
generated-date normalization. Retain raw blueprint results separately.

- [ ] Confirm package-root assets, all seven skills, their 69 indexed files,
      and the full demo outputs. Exit zero from a wrapper is not evidence that
      identity/value/FinOps all succeeded.
- [ ] If artifacts differ, investigate converter/toolchain/archive/date effects.
      Do not run `verify_release --write` against the preserved manifest or
      rewrite its expected hashes.
- [ ] Record source commit, toolchain, exact commands, actual test counts,
      failures/skips, four comparisons, original-artifact limitations, converter
      availability and known product limitations in the evidence document.
      Keep transient logs under ignored build output.

M0-A can report source preservation independently of native HubWorks or Azure
readiness. Any unexecuted host checks must remain explicitly pending.

## Task 5: Test-first repair of CI coverage and required-check schema

**Modify:** `tools/dev.py`, `tools/bootstrap_github.py`,
`tests/unit/test_tools_core.py`, `tests/unit/test_release_tools.py`,
`docs/engineering/testing-strategy.md`, `docs/engineering/github-setup.md`.

- [ ] Add this regression class to `test_tools_core.py`, adding
      `from unittest import mock` to its imports.

```python
class DevGateWiring(unittest.TestCase):
    def test_ci_includes_pipeline_tests(self):
        dev = load("tools/dev.py", "dev_gate_wiring")
        with mock.patch.multiple(
            dev,
            cmd_template_check=mock.DEFAULT,
            cmd_lint=mock.DEFAULT,
            cmd_scan=mock.DEFAULT,
            cmd_test=mock.DEFAULT,
            cmd_selftest=mock.DEFAULT,
            cmd_package=mock.DEFAULT,
            cmd_demo=mock.DEFAULT,
            cmd_verify_release=mock.DEFAULT,
            cmd_dom=mock.DEFAULT,
        ) as commands:
            self.assertEqual(dev.main(["ci"]), 0)
        commands["cmd_test"].assert_called_once_with(include_slow=True)
```

- [ ] Add this method to the existing `Bootstrap` test class.

```python
    def test_ruleset_requires_the_m0_checks(self):
        status_rule = next(
            rule for rule in bootstrap.ruleset(1)["rules"]
            if rule["type"] == "required_status_checks"
        )
        contexts = {
            item["context"]
            for item in status_rule["parameters"]["required_status_checks"]
        }
        self.assertEqual(
            contexts,
            {"L1 quality gate", "L2 browser tests", "IaC validation"},
        )
```

- [ ] Run both selectors together and confirm the expected failures.

```powershell
python -m pytest tests\unit\test_tools_core.py::DevGateWiring tests\unit\test_release_tools.py::Bootstrap::test_ruleset_requires_the_m0_checks -q
```

Expected failures: `cmd_test()` lacked `include_slow=True`; required contexts
contained only L1.

- [ ] Make the smallest implementation changes.

In the `check` command's existing sequence, replace:

```python
cmd_test()
```

with:

```python
cmd_test(include_slow=True)
```

Replace the bootstrap's single required-check constant with:

```python
REQUIRED_CHECKS = (
    "L1 quality gate",
    "L2 browser tests",
    "IaC validation",
)
```

Replace the existing `required_status_checks` list with:

```python
"required_status_checks": [
    {"context": name} for name in REQUIRED_CHECKS
],
```

Do not run bootstrap administration. These changes make its intended schema
accurate; server policy must still be applied and verified by the maintainer.

- [ ] Rerun the same selectors, then `python tools\dev.py ci`. Update the two
      engineering guides to state that strict CI includes pipeline wrappers and
      all three checks must be configured. Preserve actual behavior elsewhere.
- [ ] Commit the implementation, regression tests and directly related docs.

```powershell
git add -- tools\dev.py tools\bootstrap_github.py tests\unit\test_tools_core.py tests\unit\test_release_tools.py docs\engineering\testing-strategy.md docs\engineering\github-setup.md
git commit -m "fix: include pipeline tests and complete M0 check requirements" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Task 6: Pin release tooling and validate the release candidate

**Modify:** `.github/workflows/*.yml`; `tests/unit/test_release_tools.py`.
Protected release/deployment workflow edits require maintainer approval.

### 6.1 Exact inspected pins

These are actual commit objects, not annotated tag-object SHAs. Reconfirm the
release association before execution; never silently substitute another revision.

| Reference | Commit |
|---|---|
| actions/checkout v7 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| actions/setup-python v7 | `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0` |
| actions/setup-node v7 | `949feb2413d6458794dcd2491c4babbbce0c15c1` |
| actions/upload-artifact v7 | `cf430e030ddbb5b0abf93d22962f4752f3646cd9` |
| actions/download-artifact v8 | `9000827ccba6bdab643e8b6fd33ac0654aef8333` |
| actions/attest-build-provenance v4 | `4d101475d8b20a2381f78447822ac1eab6504dd8` |
| Azure/setup-azd v2 | `0b7e3a35ab00f2eee7080c845eb39c3f0ebfa553` |
| github/codeql-action v4 | `33d7b85da1a04171e211befe2c739303b9a4c066` |

- [ ] Replace each matching reference in existing workflow files with its
      full commit and a version comment. For example:

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7
- uses: actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7
- uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7
```

For both CodeQL `init` and `analyze`, preserve the subpath and use the same
CodeQL commit. Do not enable CodeQL/showcase features as part of pinning.

- [ ] Replace the SBOM download with this inspected version and checksum,
      retaining the existing generation command after the verified download:

```bash
curl -sSfLo "$RUNNER_TEMP/sbom-tool" https://github.com/microsoft/sbom-tool/releases/download/v4.1.5/sbom-tool-linux-x64
echo "bf5d4f99bc98c119d549d08fc02ae92598a7a42772f17317c01031a92632e05b  $RUNNER_TEMP/sbom-tool" | sha256sum --check --strict
chmod +x "$RUNNER_TEMP/sbom-tool"
```

This checksum was read from the public release asset metadata; the binary was
not downloaded/executed during planning. The SBOM's product scope is not a claim
to cover every development tool or optional runtime converter.

### 6.2 Release regression

- [ ] Add this class to `tests/unit/test_release_tools.py`. PyYAML is already a
      declared development dependency.

```python
class ReleaseWorkflowContracts(unittest.TestCase):
    def test_release_checks_the_tag_with_l1_and_l2(self):
        import yaml

        workflow = yaml.safe_load(
            (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        )
        steps = [
            step.get("name", "")
            for step in workflow["jobs"]["build"]["steps"]
        ]
        self.assertIn("Gate L2 on the tag", steps)
        self.assertLess(
            steps.index("Gate L1 (strict) on the tag"),
            steps.index("Gate L2 on the tag"),
        )
        self.assertLess(
            steps.index("Gate L2 on the tag"),
            steps.index("Release bundle and manifest"),
        )
        self.assertEqual(
            workflow["jobs"]["publish"]["environment"],
            "release-approval",
        )
```

- [ ] Run the focused test and confirm failure because the L2 step/approval
      boundary are absent.

```powershell
python -m pytest tests\unit\test_release_tools.py::ReleaseWorkflowContracts -q
```

- [ ] After maintainer approval, insert this step after strict L1 and before
      release bundling:

```yaml
- name: Gate L2 on the tag
  run: |
    npx playwright install --with-deps chromium
    python tools/dev.py site e2e --strict
```

Change the publish job's environment to:

```yaml
environment: release-approval
```

The Ubuntu workflow keeps Linux command syntax. Local commands in this plan
use PowerShell/Windows paths.

- [ ] Rerun the focused test, existing release-tool tests and strict L1.
      Validate the workflow through a maintainer-controlled candidate run
      before claiming it operates. Do not create a release tag during M0
      agent execution.
- [ ] Commit only after protected-file approval. Record that complete bundles
      containing analysis documents remain internal until cleared.

## Task 7: Prove server policy and Copilot behavior

**Owner:** maintainer for settings, approvals and protected configuration.
**Files:** `.github/CODEOWNERS`, related engineering guides and M0 evidence.

- [ ] Set CODEOWNERS to an eligible maintainer/team. If the correct initial
      owner is the target repository owner, use `@urruegg_microsoft`; do not
      invent a team or reviewer.
- [ ] Require L1, L2 and IaC on the intended branch and prove an intentionally
      failing PR cannot merge. Verify actual ruleset enforcement; branch
      metadata alone is insufficient.
- [ ] Create/verify `release-approval` with the approved reviewer and selected
      version-tag policy. Keep showcase `dev`/`prod` policy separate.
      If private-repository reviewer gates are unavailable, block release
      readiness until a compliant alternative is approved.
- [ ] Keep `SHOWCASE_ENABLED` false/unset. M0 does not provision Azure.
- [ ] Verify actual hook activation and denial on each claimed Copilot
      harness. Use only synthetic harmless test operations. Unit tests of
      `guard.decide` and instruction discovery alone are not this evidence.
- [ ] Record that internal guard errors are fail-open and authoritative
      permissions/reviews remain the controlling boundary.

### Optional approved cloud-agent Superpowers lane

The current session already has working Superpowers. Do not overwrite personal
skills or change global settings during intake.

If ENG-D2 vendoring is approved, the inspected v7.0.2 commit is:
`22f0b463e7a5e579904dd6211a520321035526f7`.

- [ ] The maintainer creates a temporary local clone, verifies its commit
      before vendoring, and uses the existing tool against that checked source.

```powershell
$checkedSource = Join-Path $env:TEMP ('frontier-superpowers-' + [guid]::NewGuid())
git clone --depth 1 --branch v7.0.2 https://github.com/obra/superpowers.git $checkedSource
if ($LASTEXITCODE -ne 0) { throw 'Superpowers source clone failed.' }
$actual = git -C $checkedSource rev-parse HEAD
if ($actual -ne '22f0b463e7a5e579904dd6211a520321035526f7') {
  throw 'Superpowers source differs from the approved commit.'
}
python tools\superpowers.py vendor --version v7.0.2 --source $checkedSource
if ($LASTEXITCODE -ne 0) { throw 'Superpowers vendoring failed.' }
python tools\superpowers.py verify
if ($LASTEXITCODE -ne 0) { throw 'Superpowers lock verification failed.' }
```

Check for target skill-name conflicts before copying. Review the vendor
inventory/license/lock and demonstrate cloud-agent discovery before committing.
The source tool must not be used to overwrite existing personal/global skills.
Clean up only the specifically created temporary clone under approved cleanup
scope, never a broad temp/home/source directory.

- [ ] Open a reviewable branch PR only after publishing authorization is
      confirmed. A person reviews and merges; no agent approval, merge or tag.

## Task 8: Actual-host acceptance and M0 handoff

**Files:** `docs/intake/m0-evidence.md`, engineering guides and this plan's
completed checklist.

- [ ] A person installs the freshly built standalone ZIP in a new Cowork
      session, approves the documented installation and verifies seven-skill
      discovery.
- [ ] Exercise the synthetic workshop loop: discovery/evidence, blueprint,
      solution design/readiness, identity, value/FinOps and feedback export/merge.
- [ ] Confirm writable host storage, Python subprocess/sibling paths,
      complete artifact publication and OneDrive persistence. Do not equate
      developer-machine execution with customer-host execution.
- [ ] Verify the populated demo identity kit, catalogue and modeled outputs,
      including the expected 33-agent sample. Check negative/missing-input cases
      and explicitly report degraded or incomplete output.
- [ ] Preserve the documented wrapper-option, partial-success and stale-feedback
      limitations. Corrections belong to a separate versioned change.
- [ ] Record exact checked SHA, package hashes, actual CI counts, host evidence,
      policy proof, limitations and remaining blockers. Update local source
      references in the planning documents to imported relative paths.
- [ ] Reproduce the four baseline artifacts after all engineering changes.
      Do not bump the product version for an engineering-only intake unless
      shipped product bytes intentionally change.
- [ ] Hand over the PR and evidence. Only mark M0-B complete if mandatory
      checks, ownership and approved release controls are demonstrably effective.

## Deferred work and stop conditions

- HubWorks: separate native-host capability proof, packaging/export, routing,
  shared engagement ownership and upstream PR. No dynamic-loader claim.
- Product fixes: separately versioned tests for wrapper flags, full-output
  failure semantics and feedback identity/version validation.
- Showcase: separate approved Azure plan, exact-SHA CI dependency, authentication
  acceptance, subscription/identity/cost decisions and deployment runbook.
- Public distribution: separate documentation/icon/reuse-rights review.

Stop on unexpected source changes, conflicting user files, mandatory missing
controls, unexplained hash differences, unavailable runtime capabilities or
incomplete artifacts. Keep the best evidence and an explicit blocked status.
Do not replace those conditions with skipped checks, updated expected hashes,
silent reduced output or an unverified success claim.
