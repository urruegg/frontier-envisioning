# 1.11.0 Cowork Health and FinOps Exclusion Implementation Plan

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-26 |
| Author | AI assistant using Copilot SDK in VS Code; AI-assisted planning |
| Status | Plan/execution at `b3174a1` approved for task-by-task subagent implementation; actual results still required; no release approval implied |
| Scope | Bug #81 only; no source retirement, financial formulas, Studio metadata, tenant or protected-workflow changes |
| References | [Bug #81](https://github.com/urruegg/frontier-envisioning/issues/81), [approved spec](../specs/2026-11-26-plugin-health-and-finops-exclusion-design.md), [actual written approval](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7193888412), [idea](../ideas/2026-11-26-plugin-health-and-finops-exclusion.md), [SPRINT-013](../sprints/SPRINT-013-agent-factory-handover.md), [draft PR #80](https://github.com/urruegg/frontier-envisioning/pull/80) |

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Use available invocation names or the AGENTS method, never an assumed installation path.

**Goal:** Ship the eight-skill 1.11.0 Cowork ZIP without FinOps, retain working Value Case and Factory, and correct the reported Process/Value Case routing.

**Architecture:** Keep FinOps source/tests, but distinguish retained source from the exact distributed inventory. Put the finite inventory rule in the existing standalone installer and reuse it from repository tools; do not introduce a configurable exclusion mechanism. Preserve financial safeguards and validate the actual extracted package independently of repository imports.

**Tech Stack:** Python 3.11+ standard library, existing unittest/pytest, Markdown/YAML/JSON, existing package/self-test/DOM/Playwright gates.

---

## 1. Authority, baseline and file boundaries

The human approved written spec `c26991eefd6a03be1f0d41fc65af669b5f35eb79`
with `written_spec_review=approve-written-health-amendment`.
The separate choices were release-only exclusion, retained source/tests and
Cowork ZIP installation. The plan at `b3174a1` subsequently received:
**"approved the plan and the implementation, please implement it sub agent
drive end to end"**. The [actual receipt](https://github.com/urruegg/frontier-envisioning/issues/81#issuecomment-7194451667)
authorises all four tasks with fresh bounded workers and ordered review,
not repeated human stage approvals inside the agreed scope.
`@urruegg` remains accountable. No protected label, merge or publication is
authorised by these records.

Reuse the existing isolated `feat/72-agent-factory` worktree. Preserve unrelated
primary-worktree changes. The previous nine-skill candidate at `ab9b10b`
passed full local/server gates; those results are not the new eight-skill
candidate's verification. Do not repeatedly rebuild the unchanged old baseline.

Before any product edit, check PR #80 and exact release/tag `v1.11.0` again
using read-only `gh`. A genuine not-found response differs from access/network
failure. If release/tag state changed, stop for the maintainer's version
decision; never overwrite a release or bump merely to bypass reproduction.
Otherwise retain unreleased version 1.11.0.

| Files | Responsibility |
|---|---|
| `plugin/install/prepare_install.py` | Canonical finite source/distribution rule and current-package preflight; standalone, no repository imports |
| `tools/fe_lib.py`, `tools/build_package.py`, `tools/check_repo.py` | Reuse that rule; keep source maturity/version/copy checks and strict omission errors |
| `plugin/package/manifest.json` | Register the exact eight distributed folders; no version change unless the maintainer resolves a changed release boundary |
| `tests/unit/test_skill_maturity.py`, `tests/unit/test_factory_package.py` | Source/distribution split, tampering, actual installed core and financial refusal |
| `tools/selftest.py` | Separate retained-source FinOps regression from actual installed-package checks |
| `tests/unit/test_docs_contract.py` | Current eight-skill catalogue versus nine retained source folders; preserve all historical mutation tests |
| Eight shipped `SKILL.md` files, listed in Task 3 | Active scope, Process/Value Case routing and no broken links into an excluded skill |
| Five packaged references listed in Task 3, `plugin/README.md` | Clear release notice and coherent local references |
| `README.md`, `AGENTS.md` section 1, `CHANGELOG.md`, current PRD/design/sprint sections | Current release truth and source-qualified evidence, not historical rewrites |
| `plugin/install/plugin-install.json` | Generated only by `python tools\dev.py package` |
| `tests/pipeline/test_factory_receiver.py` | Run unchanged against the retained actual reference; no opt-in skip substituted for the required run |

No renderer or site change is planned. Do not edit protected files, licences,
release manifests or workflows. Do not delete FinOps source or weaken
`maturity_errors`, shared `fv_expr.py` identity, financial validation or frozen
raster/source comparisons.

## 2. Task 1: strict source/distribution inventory

**Files:** `tests/unit/test_skill_maturity.py`,
`plugin/install/prepare_install.py`, `tools/fe_lib.py`,
`tools/build_package.py`, `tools/check_repo.py`,
`plugin/package/manifest.json`.

- [ ] Add `import zipfile` to the existing maturity tests and this behavioural
  regression. It builds from a disposable copy, not a fabricated ZIP:

```python
def test_111_distribution_keeps_value_case_without_finops(self):
    package = load("tools/build_package.py")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        plugin = root / "plugin"
        shutil.copytree(ROOT / "plugin", plugin)
        path = plugin / "package/manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["agentSkills"] = [
            row for row in manifest["agentSkills"]
            if row["folder"] != "skills/frontier-finops"
        ]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(package, "PLUGIN", plugin), contextlib.redirect_stdout(output):
            code = package.main(["--dist", str(root / "dist")])
        self.assertEqual(code, 0, output.getvalue())
        self.assertTrue((plugin / "skills/frontier-finops/SKILL.md").is_file())
        with zipfile.ZipFile(root / "dist/frontier-envisioning-plugin-1.11.0.zip") as archive:
            names = archive.namelist()
            self.assertFalse(any(name.startswith("skills/frontier-finops/") for name in names))
            self.assertIn("skills/frontier-value-case/SKILL.md", names)
            self.assertIn("skills/frontier-agent-factory/SKILL.md", names)
            install = json.loads(archive.read("install/plugin-install.json"))
            self.assertEqual(len(install["skills"]), 8)
            self.assertEqual(
                {row["folder"] for row in install["skills"]},
                {row["folder"] for row in manifest["agentSkills"]},
            )
```

- [ ] Run `python -m unittest tests.unit.test_skill_maturity.SkillMaturity.test_111_distribution_keeps_value_case_without_finops -v`.
  Observe RED from the old rejection of unregistered FinOps source. Record the
  actual failure; do not remove FinOps source to make the test pass.

- [ ] Add the canonical rule to the existing standalone installer, before
  `main`. The values are archive-relative folders, not caller paths:

```python
RELEASE_SKILLS_1110 = frozenset("skills/" + name for name in (
    "frontier-envisioning",
    "frontier-context-discovery",
    "frontier-blueprint",
    "frontier-solution-design",
    "frontier-agent-identity",
    "frontier-value-case",
    "frontier-process",
    "frontier-agent-factory",
))
RETAINED_SOURCE_1110 = frozenset({"skills/frontier-finops"})


def skill_inventory_errors(
    version: str, registered: list[str], disk: list[str], *, source_tree: bool
) -> list[str]:
    if not all(isinstance(value, str) for value in [*registered, *disk]):
        return ["skill inventory folders must be strings"]
    listed, present = set(registered), set(disk)
    if version != "1.11.0":
        if not source_tree:
            return []
        expected, expected_disk = present, present
    else:
        expected = RELEASE_SKILLS_1110
        expected_disk = expected | RETAINED_SOURCE_1110 if source_tree else expected
    problems = []
    if len(registered) != len(listed):
        problems.append("duplicate registered skill folder")
    for folder in sorted(expected - listed):
        problems.append(f"{folder} is not listed in manifest agentSkills")
    for folder in sorted(listed - expected):
        problems.append(f"{folder} is not a distributed skill for {version}")
    for folder in sorted(expected_disk - present):
        problems.append(f"{folder} is missing from the expected skill tree")
    for folder in sorted(present - expected_disk):
        problems.append(f"{folder} is unexpected in the skill tree")
    return problems
```

Non-1.11 repository inventories keep the previous equality rule. Legacy
installer probes remain unchanged; they are not made subject to the 1.11
profile. The current finite rule never permits arbitrary omitted folders.

- [ ] Add the repository forwarder in `tools/fe_lib.py`, after `load_module`,
  using the trusted repository installer, not an incoming package:

```python
def skill_inventory_errors(
    version: str, registered: list[str], disk: list[str], *, source_tree: bool
) -> list[str]:
    installer = load_module(PLUGIN / "install" / "prepare_install.py", "fe_install_inventory")
    return installer.skill_inventory_errors(version, registered, disk, source_tree=source_tree)
```

- [ ] Import this helper in packager/checker. In `build_package.main`, validate
  frontmatter for **all** `on_disk` source folders, not only registered ones:
  change the existing `for f in folders` metadata loop to `for f in on_disk`.
  Replace its unregistered-folder loop with:

```python
errors.extend(skill_inventory_errors(version, folders, on_disk, source_tree=True))
```

Retain required-file/distribution inspection and the early error return
before writes. This preserves the existing nonoptional-FinOps source test.
In `check_repo.check_skills`, replace the two manifest/disk equality loops:

```python
for error in skill_inventory_errors(
    manifest.get("version", ""), listed, on_disk, source_tree=True
):
    r.err("skills", error)
```

Keep all source frontmatter/version/maturity and shared-copy checks unchanged.
Do not alter `test_factory_shared_zip`'s versionless three-skill fixture:
the legacy equality branch still applies.

- [ ] Remove only the `skills/frontier-finops` row from `agentSkills` in the
  production manifest. Remove the exact FinOps starter prompt
  `"What will the <customer> agents cost per month?"` from `START_PROMPTS`.
  Do not remove the Value Case prompt or Factory registration.

- [ ] Change the maturity inventory test to distinguish retained source from
  release, retaining its nine-source count and all maturity assertions:

```python
registered = {Path(row["folder"]).name for row in manifest["agentSkills"]}
self.assertEqual(len(registered), 8)
self.assertEqual({p.parent.name for p in skills} - {"frontier-finops"}, registered)
```

- [ ] Add this companion packager regression using the same disposable-copy
  pattern; retain `test_packager_rejects_nonoptional_finops_before_writing`:

```python
def test_111_does_not_allow_an_additional_omitted_skill(self):
    package = load("tools/build_package.py")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        plugin = root / "plugin"
        shutil.copytree(ROOT / "plugin", plugin)
        path = plugin / "package/manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["agentSkills"] = [
            row for row in manifest["agentSkills"]
            if row["folder"] != "skills/frontier-value-case"
        ]
        path.write_text(json.dumps(manifest), encoding="utf-8")
        output = io.StringIO()
        with mock.patch.object(package, "PLUGIN", plugin), contextlib.redirect_stdout(output):
            code = package.main(["--dist", str(root / "dist")])
        self.assertEqual(code, 1)
        self.assertIn("frontier-value-case", output.getvalue())
        self.assertFalse((root / "dist").exists())
```

- [ ] Run `python -m unittest tests.unit.test_skill_maturity tests.unit.test_factory_shared_zip -v`.
  Expect exit 0. Run `python -m ruff check plugin\install\prepare_install.py tools\fe_lib.py tools\build_package.py tools\check_repo.py tests\unit\test_skill_maturity.py`
  and `git --no-pager diff --check`.
  Commit only Task 1 files with `fix: define the 1.11 distribution inventory`,
  `Refs #81` and the required Copilot co-author trailer.

## 3. Task 2: standalone installer and exact installed behaviours

**Files:** `plugin/install/prepare_install.py`, `tools/selftest.py`,
`tests/unit/test_factory_package.py`.

- [ ] In `FactoryPackage`, change the existing registration assertion to eight
  and add the ZIP absence/Value Case/Factory assertions from Task 1 to that
  actual-package test. This is a changed behavioural expectation, not a
  replacement golden ZIP.

- [ ] Add a real repacking negative test before adding installer preflight:

```python
def test_installer_rejects_an_extra_skill_tree(self):
    for name in ("frontier-finops", "frontier-unexpected"):
        with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            installed, _ = build_candidate(root)
            extra = installed / "skills" / name
            extra.mkdir()
            (extra / "SKILL.md").write_text("Not a released skill\n", encoding="utf-8")
            result = installed_command(
                installed / "install/prepare_install.py",
                ["--root", installed, "--installed", root / "empty"], root,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["verified"])
            self.assertEqual(report["copy_calls"], [])
            self.assertFalse((root / "empty").exists())
```

- [ ] Run that selector, observe RED (old installer ignores extra unlisted
  top-level skill folders), then add this preflight immediately after the
  existing plugin-identity check. It uses only bundled/local data:

```python
if spec.get("version") == "1.11.0":
    skill_root = root / "skills"
    disk = [
        "skills/" + path.name for path in skill_root.iterdir() if path.is_dir()
    ] if skill_root.is_dir() else []
    rows = spec.get("skills")
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        problems.append("installer skills must be a list of objects")
    else:
        problems.extend(skill_inventory_errors(
            "1.11.0", [row.get("folder") for row in rows], disk, source_tree=False
        ))
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        problems.append("release manifest is missing or invalid JSON")
    else:
        if not isinstance(manifest, dict) or manifest.get("version") != spec["version"]:
            problems.append("release manifest version differs from the installer")
        else:
            entries = manifest.get("agentSkills")
            if not isinstance(entries, list) or not all(isinstance(row, dict) for row in entries):
                problems.append("manifest agentSkills must be a list of objects")
            else:
                problems.extend(skill_inventory_errors(
                    "1.11.0", [row.get("folder") for row in entries], disk, source_tree=False
                ))
    if problems:
        print(json.dumps({
            "plugin": spec.get("plugin"), "version": spec.get("version"),
            "verified": False, "problems": problems, "skills": [], "copy_calls": [],
            "preview_notice": "", "after_install": "Do not install: use the original release ZIP.",
        }, indent=1))
        return 1
```

Keep the existing per-file hashes, frontmatter/maturity checks, read-only
behaviour and legacy installer probes. Do not add broad exception handling
or relax other metadata validation.

- [ ] Update the existing exact installed-package test: eight copy calls,
  seven GA wrappers and only `{"frontier-agent-factory": False}` in the
  Preview map. Replace the unconditional FinOps `rmtree` with an assertion
  that it is absent. Delete its later FinOps restoration loop. Keep the
  repeated deterministic Factory exports and real installed core check.
  In `InstalledFactoryFinancial.test_installed_nonfinancial_vars_work_without_finops`,
  replace the FinOps directory rename/restore block with:

```python
self.assertFalse((self.installed / "skills/frontier-finops").exists())
result = export_command(self.installed, fixture, self.root)
```

Keep the original nonfinancial `vars` payload, financial-status and exact
exported-byte assertions; do not skip the test because FinOps is now absent.

- [ ] In `installed_core_check`, assert/check FinOps is already absent; do not
  remove a nonexistent directory. Remove Factory only, then keep every
  existing ordinary value/process/Blueprint check and input-byte assertion.
  Update the main installer assertions to eight and absence of a FinOps row.
  Preserve the source-only FinOps baseline regression with this explicit call
  instead of running that regression against an incomplete extraction:

```python
source_work = installed_work / "retained-finops-source"
source_work.mkdir()
baseline_cli_checks(
    ROOT / "plugin", source_work,
    lambda name, ok, detail="": check("retained FinOps source: " + name, ok, detail),
)
factory_cli_checks(t / "pkg", installed_work, check)
```

Do not restore FinOps into the released extraction or describe retained-source
checks as installed capability. All earlier source FinOps/value checks in
`selftest.main` remain; update the baseline helper docstring accordingly.

- [ ] Add the acknowledged-but-unavailable financial-owner regression:

```python
def test_installed_financial_owner_absence_is_explicit(self):
    from tests.unit.test_factory_finops import financial_packet
    from tests.unit.test_factory_privacy import projection

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        installed, _ = build_candidate(root)
        fixture = prepare(root / "financial")
        financial_packet(projection(self), fixture)
        fixture["out"].write_bytes(b"old-good")
        args = []
        for flag, key in (
            ("request", "request_file"), ("template", "template"),
            ("source-root", "source"), ("baseline-root", "baseline"), ("out", "out"),
        ):
            args.extend(["--" + flag, fixture[key]])
        result = installed_command(
            installed / "skills/frontier-agent-factory/scripts/export_factory.py",
            [*args, "--acknowledge-finops-preview"], root,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["error"], "FACTORY_HELPER")
        self.assertEqual(result.stderr, "")
        self.assertEqual(fixture["out"].read_bytes(), b"old-good")
```

The technical fixture uses retained source to prepare an authoritative-shaped
synthetic packet. The producer being tested must use only its extraction.
Do not change the existing financial detection, error codes, receipts or
owner helpers to accommodate this test.

- [ ] Run `python -m unittest tests.unit.test_factory_package tests.unit.test_factory_finops -v`.
  Expect exit 0, preserving current/history acknowledgement and ordinary
  nonfinancial controls. Run `python tools\dev.py selftest --strict`; expect
  real retained-source and exact-installed checks to pass, not skips.
  Run `python -m ruff check plugin\install\prepare_install.py tools\selftest.py tests\unit\test_factory_package.py`.
  Commit Task 2 files with `fix: verify the FinOps-free installed package`,
  `Refs #81` and the required trailer.

## 4. Task 3: routing, release notice and current documentation

**Files:** `plugin/README.md`, the eight shipped skills' `SKILL.md`,
`plugin/skills/frontier-blueprint/references/blueprint-schema.md`,
`plugin/skills/frontier-process/references/ontology-method.md`,
`plugin/skills/frontier-value-case/references/value-method.md`,
`plugin/skills/frontier-solution-design/references/design-rules.md`,
`plugin/skills/frontier-envisioning/references/method.md`,
`plugin/package/manifest.json`, `README.md`, `AGENTS.md` section 1,
`CHANGELOG.md`, `docs/prd.md`, `docs/solution-design.md`,
`docs/sprints/SPRINT-013-agent-factory-handover.md`,
`tests/unit/test_docs_contract.py`.

- [ ] Replace only Value Case's frontmatter description with:

```yaml
description: |
  Builds a business value case in CHF for Frontier use cases: evidence-backed value trees,
  owned assumptions, NPV, ROI, payback, break-even and sensitivity. Use for "build the value
  case for <customer>", "ROI in CHF for the MVP", "what is the MVP worth" or "update value
  assumptions from workshop feedback". Do NOT use for process ontology, CDM mappings or
  data products (use frontier-process), the blueprint itself (frontier-blueprint), PRD and
  solution design (frontier-solution-design), or CRM sales-deal cases (sales skills).
  FinOps cost modelling and Copilot Credits are not included in this release.
```

- [ ] Replace only Process's frontmatter description with:

```yaml
description: |
  Designs process ontologies, business objects, proposed CDM mappings, OneLake layers,
  data products and agent grounding. Writes local Turtle and design files for the blueprint
  Ontology page; Fabric ontology/agent/operations remain Preview. Use for "build the process
  ontology for <customer>", "map to the Common Data Model" or "define the data products".
  Do NOT use for business value, ROI, NPV or payback (use frontier-value-case), Power BI
  questions (powerbi or Fabric IQ plugin), blueprint HTML alone (frontier-blueprint), or
  PRD/design documents (frontier-solution-design). FinOps is not included in this release.
```

Use the existing When NOT to Use sections for the same mutual responsibility
boundary. Do not reject generic agent/Blueprint/build requests.

- [ ] Add this canonical release notice to `plugin/README.md`:

```markdown
## FinOps not included in 1.11.0

This Cowork ZIP contains eight skills: the seven existing GA wrappers,
including Business Value Case, plus optional Preview Envisioning Agent Factory.
The FinOps skill is not registered, copied or installed by this release.
Its source and regression tests remain in the repository for later work.

Ordinary business value and sourced cost assumptions remain supported.
FinOps cost modelling, Copilot Credits and FinOps-derived financial validation
are unavailable in this distribution. Name missing budget evidence; do not
invent zero costs, strip provenance or accept unverified financial figures.
An explicit unavailable financial operation must fail with a clear error.
```

- [ ] In all eight shipped SKILL files, replace active instructions to load
  FinOps with this release-boundary paragraph, adjusted only for the existing
  heading grammar:

```markdown
For 1.11.0, follow the [FinOps distribution boundary](../../README.md#finops-not-included-in-1110).
FinOps is not bundled. Continue ordinary non-FinOps work with explicit budget
gaps; do not invoke an absent skill or reuse derived financial figures.
```

Mark retained legacy/financial-protocol discussion as source-compatibility
reference, not runnable 1.11.0 instructions. Keep provenance/refusal language.
Envisioning and Factory descriptions must no longer route costs to an
installed FinOps skill; replace that clause with
`FinOps cost operations are not included in this release`.

- [ ] In the listed five references, change local links into the absent
  FinOps folder to `../../../README.md#finops-not-included-in-1110`.
  In shipped SKILL files use `../../README.md#finops-not-included-in-1110`;
  in the root plugin README use its own anchor. Keep other references and
  historical source records unchanged. All replacement links must resolve
  inside the actual ZIP.

- [ ] Replace `manifest.description.full` with this current-release text:

```text
Frontier Envisioning supports evidence-led workshops, customer context discovery,
an interactive Company Blueprint, agent identity kits, business value cases in CHF,
PRD and solution design, and optional process ontology design. Version 1.11.0
ships seven GA product wrappers and optional Preview Envisioning Agent Factory,
which prepares a reviewed starter-repository ZIP from a pinned template and
envisioning artefacts. FinOps is not included. Outputs distinguish assumptions,
evidence, gaps and human decisions; no installation grants financial, repository,
source-transfer or tenant permission. The repository and current development
distribution remain private and Microsoft internal; technical export checks
do not grant external publication clearance.
```

- [ ] Update the current skill tables and 1.11 release sections in the listed
  product/engineering docs. Use the exact eight-name list from the spec and
  explicitly identify retained-source FinOps outside the shipped set. Preserve
  all prior approval, release, nine-skill candidate and CI evidence at its
  named source. Update only AGENTS section 1, never its controls.

- [ ] Change the current working-agreement inventory test to eight manifest
  names, with `manifest_names == source_names - {"frontier-finops"}` and
  `AGENTS_table_names == manifest_names`. Keep the independent retained-source
  FinOps notice test and every historical preservation/mutation test.
  Rename only current nine-skill test descriptions, not historical records.

- [ ] Validate with `python tools\dev.py docs --strict`,
  `python -m unittest tests.unit.test_docs_contract tests.unit.test_skill_maturity -v`
  and `python tools\dev.py precommit`. Expect exit 0, descriptions within 900
  UTF-16 units and no new neutrality findings. Prose is not fictional TDD:
  report actual document checks and review the mutual routing meaning.
  Commit as `fix: clarify release routing and retain Value Case`, with
  `Refs #81` and the required trailer.

## 5. Task 4: actual package, receiver, gates and bug traceability

**Files:** generated `plugin/install/plugin-install.json`; evidence-only
current sections of `docs/solution-design.md`,
`docs/sprints/SPRINT-013-agent-factory-handover.md` and the PR/bug records.
No new manual release manifest or synthetic health report.

- [ ] Run the following sequentially, not alongside mutable browser builds:

```powershell
python tools\dev.py package
if ($LASTEXITCODE -ne 0) { throw 'Package failed' }
python -m unittest tests.unit.test_skill_maturity tests.unit.test_factory_package tests.unit.test_factory_finops tests.unit.test_docs_contract -v
if ($LASTEXITCODE -ne 0) { throw 'Distribution or regression checks failed' }
```

The existing exact-package helper performs two independent package builds;
the existing Factory tests compare frozen exports. Record newly measured
digests, never the old nine-skill ZIP hash.

- [ ] Run the actual retained-reference receiver suite. The controller supplies
  the two real retained paths from the verified Factory session; they are
  external test inputs, not product defaults or new customer evidence.
  This complete PowerShell sequence takes those paths explicitly and sets
  all three variables in the same shell:

```powershell
param(
    [Parameter(Mandatory=$true)][string]$Reference,
    [Parameter(Mandatory=$true)][string]$ReceiverPython
)
$ErrorActionPreference = 'Stop'
$env:FRONTIER_FACTORY_REFERENCE = (Resolve-Path -LiteralPath $Reference).Path
$env:FRONTIER_FACTORY_RECEIVER_PYTHON = (Resolve-Path -LiteralPath $ReceiverPython).Path
$env:FRONTIER_FACTORY_RECEIVER_REQUIRED = '1'
python -m unittest tests.pipeline.test_factory_receiver -v
if ($LASTEXITCODE -ne 0) { throw 'Required actual receiver proof failed' }
```

Require `FRONTIER_FACTORY_RECEIVER_REQUIRED=1`; use the retained reference
`0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d` and its actual isolated Python.
Missing/partial prerequisites must fail, not skip. This is synthetic
compatibility, not new latest-template discovery or customer approval.

- [ ] Run the authoritative full gate in a fresh ordinary authenticated shell:

```powershell
$env:CI = 'true'
python tools\dev.py docs --strict
if ($LASTEXITCODE -ne 0) { throw 'Strict documentation failed' }
python tools\dev.py check
if ($LASTEXITCODE -ne 0) { throw 'Full authoritative gate failed' }
```

Require actual `ALL GATES PASSED`; preserve development/verified distinction
from the fresh exact-version lookup. No token inspection, workflow dispatch,
TLS bypass or invented release absence.

- [ ] Run applicable local L2 with `python tools\dev.py site e2e --strict`
  when Playwright is present. If a timeout occurs, preserve the full result,
  inspect/reproduce that case and never increase timeouts or weaken assertions
  just to green the build. Do not misconfigure a direct run against the
  core-only site. No full-suite pass is inferred from separate targeted passes.
  Require a complete automatic PR CI L2 pass before engineering handoff.

- [ ] Inspect the actual ZIP and extracted installer plan: eight skills,
  Value Case and Factory present, zero FinOps skill entries/copy calls,
  no dangling local Markdown links into the omitted folder. Inspect remaining
  FinOps references to distinguish a source-compatibility note or guard from
  an active instruction to execute unavailable functionality.

- [ ] Obtain a fresh report using the real host health workflow that produced
  the supplied report, if available. Do not invent a validator CLI or
  generate substitute HTML. Bind its observed package digest, timestamp and
  eight names to the rebuilt ZIP and record the conflict result in #81.
  If unavailable, explicitly leave host revalidation outstanding and the bug
  open for that evidence; offline gates are not that host result.

- [ ] Record real commands, RED/GREEN, commits, package and receiver evidence
  and remaining host checks in B.9/SPRINT-013/#81. Commit generated inventory
  only after sanctioned package generation. Recheck docs/whitespace after
  evidence-only prose; confirm the ZIP digest is unchanged by that prose.

- [ ] Push only the feature branch and update #80 with its full original
  template. Leave the person-written Summary and human sign-off untouched.
  Use `Refs #81`, not an unconditional closure claim while host verification
  is outstanding. Observe automatic exact-head L1/L2/IaC/CodeQL; never
  dispatch them manually. Record actual final checks without creating an
  endless evidence-commit/check cycle.

- [ ] Keep #81's timeline current: implementation commit and date, verification
  commit/check links, fresh health result or explicit outstanding check, then
  actual human merge/published version/date only after those events occur.
  No agent merge, release, tag, main push or protected-label/settings change.

## 6. Coverage, review and execution approval

| Spec | Task |
|---|---|
| H111-01 exact distribution | Tasks 1, 2 and actual ZIP inspection in Task 4 |
| H111-02 retained source/strict omissions | Task 1 positive/negative/maturity and unchanged shared-copy checks |
| H111-03 actual Value Case | Task 2 preserved installed core/ordinary value test |
| H111-04 Factory/financial guards | Task 2 isolated exports/financial absence plus required receiver in Task 4 |
| H111-05 routing/guidance | Task 3 semantic mutual exclusions, release notice and packaged links |
| H111-06 RED/GREEN/full verification | Tasks 1, 2 and sequential exact-candidate gates in Task 4 |
| H111-07 real host health | Task 4 real checker/report or explicit outstanding state |
| H111-08 traceability | Task 4 #81/#80 and actual event timeline |

Self-review must confirm these task APIs agree: archive-relative folder names,
`skill_inventory_errors(..., source_tree=...)`, standalone historical-version
behaviour and source-only versus installed test labels. Fix concrete
inconsistencies before presenting the plan. No production code is executed
while writing or reviewing this document.

The human selected fresh bounded implementation workers with
subagent-driven-development. Execute the approved tasks without repeated
stage approval requests, escalating only actual blockers or scope decisions.
Keep ordered specification then correctness review proportional to the
evidence; do not infer human GitHub approval from an agent review.
