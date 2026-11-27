# Frontier Envisioning Cowork install compatibility implementation plan

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-27 |
| Author | AI assistant; AI-assisted planning from the approved written specification and inspected repository files |
| Status | Plan at 7c522ca approved for subagent-driven execution; Task 0 blocked on actual human #8 baseline/readiness |
| Scope | Issue #87, NEXT 1.11.1: finite eight-skill distribution, verified whole drafts, lossless Identity consolidation, metadata and scoped routing |
| References | [Catalogue](README.md), [Issue #87](https://github.com/urruegg/frontier-envisioning/issues/87), [Approved written design](../specs/2026-11-27-cowork-install-compatibility-design.md), [Idea](../ideas/2026-11-27-cowork-install-compatibility.md), [Draft SPRINT-014](../sprints/SPRINT-014-cowork-install-compatibility.md), [PRD](../prd.md), [Architecture and B.9](../solution-design.md), [ADR catalogue](../adr/README.md) |

> **For agentic workers:** REQUIRED SUB-SKILL: use available Superpowers `executing-plans` or `subagent-driven-development` only after explicit plan/readiness approval. Otherwise follow AGENTS.md section 3. Checkboxes track work, not permission. No nested delegation is authorised by this planning request; the controller creates real bounded tasks only after approval.

**Goal:** Make the NEXT eight-skill ZIP fit Cowork's observed whole-draft and recursive-file contracts without changing generated Identity kits or weakening financial, privacy or Preview controls.

**Architecture:** Keep one canonical shipped tree. Extend the existing standalone installer and its `fe_lib` forwarder, not a second projection/repack framework. Package preflight and optional staged preflight are read-only. Only the real host saves; Python neither stages nor installs nor authenticates host receipts. Full installation and OneDrive sync need separate actual human-operated evidence.

**Tech Stack:** Python 3.11+ standard library, existing `unittest` helpers, Markdown/YAML/JSON, existing version/template/package/demo/release-reproduction and DOM/Playwright gates. No new dependencies, renderer source, settings or frameworks.

---

## 1. Authority and execution stop

The reviewed source is `b9647ea8c824af180cd60975d3f4c4b9e9297e8a`,
on supplied branch `docs/87-cowork-compatibility`, source base `482aa816`,
in the supplied isolated `frontier-envisioning-wt-87` worktree.
These are parent-provided identities, not a git check by this writer.
The entire written design was read in bounded ranges, including CWI-01–07.
The later real user follow-up **“true please proceed it's approved from my side”**
to the written-spec review request approves that written design and writing
this plan. The earlier unavailable response is not approval.
It does **not** approve execution, readiness, labels or protected actions.
Owner: `@urruegg`.

AGENTS.md, the documentation instructions, the intake/dev-loop/skill-authoring
references, engineering handbook, PRD A.12/A.13, solution design B.9 and
ADRs 0018/0019/0032 govern this work. Available Superpowers brainstorming,
worktree and writing-plans skills were invoked through the parent harness.
Execution-skill availability remains harness-dependent; use the available
skills or the AGENTS method, never an assumed installation path.
The linked #87 is the supplied real work item. Its live body/labels and live #8
state were not re-read here: there is no authenticated issue/terminal tool in
this session, and the request excludes GitHub operations. Task 0 must verify
them before implementation. This is an offline Proposed plan, not Ready work.

The supplied evidence remains human-reported: the 17,031-byte repack report
SHA256 `1ee51d581d786e6246e8b7b22814bf9535995fce69f13eb069cf56a9551f7900`,
published old ZIP SHA256
`22935d1c0197f373ff296fa7550a28626ae3851101d1b05f03bf955236eb11d2`,
23-extra Identity refusal, successful 21-file save/21-of-21 equality and
equal 429-file kits. No structural rescore was done; the companion ZIP was
absent and no repack script was executed. Published 1.11.0 assets are immutable.
None of those observations is a fresh 1.11.1 result.

### Definition of Ready

Issue/idea/spec/this plan/sprint, owner, affected files and testable CWI criteria
are linked. Written-spec approval is actual. The plan at `7c522cabe872bc1390ac15acb7df117ebad5d6a8` now has actual
human approval for subagent-driven execution. The following remain blocking:

- Human readiness evidence, including actual execution of the #8 baseline;
  the already-recorded plan approval is not requested again.
- Fresh live #87 intake/decision/label verification; approval does not prove
  `status:ready` or `approved:*` fields changed.
- Human #8: protected plural session-start correction and **Active native main**
  PR, `L1 quality gate`, `L2 browser tests`, `IaC validation`, freshness and
  force/deletion protection. Supplied state is `protected=false`, no rulesets.
  Zero formal reviews is distinct from actual maintainer sign-off at the
  reviewed head. No new account, routine bypass or App is required.
- Fresh release/tag conflict check for the intended 1.11.1 boundary.

Planning may continue while #8 blocks production. **No implementation step,
including test/checker changes or bump, starts until those gates are evidenced.**
Protected hook/settings mutations are never agent tasks. Broader #9 engineering
guidance/clearance, human-only genuinely stable template publication, final #81
host acceptance and deferred #48/#58 remain separate. Template has no supplied
releases/tags; preserve healthy no-stable discovery plus exact-commit
`unreleased-bootstrap` consent, not nominal stability or older/main fallback.
Factory stays Preview. Caldova governance/tenant work is untouched.

## 2. Slices, dependencies and files

Every numbered checkbox below is a 2–5 minute edit/run/review checkpoint.
Long full-suite runs are queued checkpoints, not a promise of five-minute
completion. Stop on unexpected RED causes or input/approval drift.
Run from the isolated approved execution worktree, not the dirty primary tree.
Commands below are **future instructions, not results from this session**.

| Slice | Depends on | Existing files / new responsibilities |
|---|---|---|
| 0 | Human approval | Recheck real intake, conflicts and #8; no code while blocked |
| 1 | 0 | `tools/bump_version.py`/`tools/dev.py` unchanged generators; installer finite policy; existing version-sensitive package/export/privacy tests |
| 2 | 1 | `plugin/install/prepare_install.py`: typed inputs, exact tree/hash/budget and staged mode; `tools/fe_lib.py`: forwarders; new focused `tests/unit/test_cowork_install.py` |
| 3 | 2 | Identity three references → one; brand → `tests/fixtures/caldova-brand.json`; `tools/selftest.py` seed caller; new lossless source test/fixture |
| 4 | 3 | Eight shipped SKILL frontmatter; Factory/Design/Context descriptions and procedure scope; existing maturity tests |
| 5 | 4 | `tools/build_package.py`, `tools/check_repo.py`, `tools/build_release.py`: source/byte and finite notice gates; `tools/demo_raster.py`: named 1.11.1 profile; existing/new raster tests |
| 6 | 5 | Existing package/selftest callers, generated template/inventory, directly coupled installer/product docs, exact-package and complete-kit verification |
| H | 6 and actual host availability | Person-operated all-eight receipt/equality/sync/health/routing; publication is a separate human decision |

Identity `scripts/**`, `kit/**`, `examples/caldova-agent-identity.json` and
`examples/caldova-palette.json` must remain byte-identical. No blueprint schema
change: retain `frontier-blueprint/1.0` and all existing additive fields.
Install inventory remains `frontier-plugin-install/1.0`; stdout gets an explicit
report schema, not a change to blueprint or native boolean semantics.
FinOps source has only the standard bump's version-carrier update; its
procedure, acknowledgement values, financial tests/formulas/rates are untouched.

### Coverage map

| Acceptance | Tasks |
|---|---|
| CWI-01 | 2, 6; H1–H4 for actual staging/save receipts and retained old version |
| CWI-02 | 2, 3, 5, 6 |
| CWI-03 | 3, 5, 6 complete 429-file equality and configured-kit tests |
| CWI-04 | 4, 6; H5 actual raw-metadata/health rescore |
| CWI-05 | 4; H6 real prompt matrix, not grep-only success |
| CWI-06 | 0, 1, 5, 6 |
| CWI-07 | 6, H1–H7; publication never inferred |

## 3. Task 0 — human readiness and conflict checkpoint

### Actual approval and prerequisite check, 27 November

At **18:25:02 +01:00**, the maintainer replied:
**"okay the plan is approved please implement it sub agent driven"**.
The [actual receipt](https://github.com/urruegg/frontier-envisioning/issues/87#issuecomment-7224405112)
approves the completed plan at `7c522ca` and the requested execution mode.
It does not prove readiness/approval labels changed or authorise protected edits.

Fresh authenticated checks found the execution worktree clean at `7c522ca`.
Live main remains `482aa816e8867575a2557230d596788e694d64fe`,
`protected:false`, with no rulesets or effective main rules. The protected
session-start source still routes both specification and plan to `docs/plans/`.
#8 remains open. Complete release/tag enumeration found no `v1.11.1` conflict.

**Task 0 is blocked on #8, not on plan approval.** No production implementer,
test/checker edit, version bump or package build starts while that prerequisite
is missing. Record the actual human route/control changes and passing evidence,
then resume the approved tasks without re-requesting the same approval.
No baseline bypass, protected change or formal independent review is claimed.

- [ ] **0.1 (person/controller, 3 minutes):** re-open the real #87 body,
  linked design/plan/sprint and any `type:decision`/PRD A.13 blockers. Record
  actual plan approval and readiness evidence, not a label inference.
  The controller may then create real bounded tasks; do not invent child IDs.
- [ ] **0.2 (person, 3 minutes):** verify actual #8 controls described above,
  including protected plural hook routing and native Active main protections.
  Missing/unknown baseline means **stop**, not “offline implementation”.
- [ ] **0.3 (person/controller, 3 minutes):** read-only exact release/tag
  enumeration for `v1.11.1` and source boundary. Auth/network/access errors
  are not absence. Any conflict stops for the maintainer's version decision.
  Do not overwrite 1.11.0, tag, publish or change settings.
- [ ] **0.4 (controller, 2 minutes):** verify approved worktree/head and
  tool availability without reading secrets; record actual identities.
  Preserve unrelated work. No dependency installation or account/bypass change
  belongs to this plan.

## 4. Task 1 — finite inventory, then standard first bump

**Files:** `tests/unit/test_skill_maturity.py`,
`plugin/install/prepare_install.py`, standard bump outputs,
`tests/unit/test_factory_package.py`, `tests/unit/test_factory_export.py`,
`tests/unit/test_factory_privacy.py`.

- [ ] **1.1 (3 minutes):** add this method to existing `SkillMaturity`.
  It exercises the real canonical installer and repository forwarder; no mocks
  manufacture the new-version policy.

```python
def test_1111_inventory_is_finite_and_retains_only_source_finops(self):
    installer = load("plugin/install/prepare_install.py")
    lib = load("tools/fe_lib.py")
    shipped = sorted(installer.RELEASE_SKILLS_1110)
    source = shipped + ["skills/frontier-finops"]
    for check in (installer.skill_inventory_errors, lib.skill_inventory_errors):
        self.assertEqual(check("1.11.1", shipped, source, source_tree=True), [])
        self.assertEqual(check("1.11.1", shipped, shipped, source_tree=False), [])
        for listed, disk, source_tree in (
            (shipped[:-1], source, True),
            (shipped + [shipped[0]], shipped, False),
            (shipped, shipped[:-1], False),
            (source, source, False),
            (shipped, source + ["skills/frontier-unexpected"], True),
        ):
            with self.subTest(listed=listed, disk=disk, source_tree=source_tree):
                self.assertTrue(check("1.11.1", listed, disk, source_tree=source_tree))
        self.assertTrue(check("1.12.0", shipped, source, source_tree=True))
        self.assertEqual(check("1.11.0", shipped, source, source_tree=True), [])
```

- [ ] **1.2 (2 minutes):** RED:
  `python -B -m unittest tests.unit.test_skill_maturity.SkillMaturity.test_1111_inventory_is_finite_and_retains_only_source_finops -v`.
  Expected meaningful failure: 1.11.1 treats retained FinOps as an omitted
  all-source skill. Not an import error or an unsupported fictional parser.
- [ ] **1.3 (3 minutes):** **before the first plugin edit**, run
  `python tools/dev.py bump 1.11.1`. Do not pass `--date`: this is unreleased,
  and the existing fixed archive date stays unchanged.
  Existing `bump` updates both JSON version carriers, all nine SKILL metadata
  versions, `build_blueprint.PLUGIN_VERSION`, the plugin README version/package
  names and a new unreleased changelog section. Run
  `python -B -m unittest tests.unit.test_release_tools.Bump -v`;
  expected two existing version-mechanism regressions pass.
  **“Unreleased compatibility work for #87; verification and host acceptance
  pending.”** Finalise the bounded notes in Task 6. No release manifest is created.
- [ ] **1.4 (3 minutes):** keep `RELEASE_SKILLS_1110` and
  `RETAINED_SOURCE_1110` intact. Immediately after them add:

```python
RELEASE_SKILLS_1111 = RELEASE_SKILLS_1110
RETAINED_SOURCE_1111 = RETAINED_SOURCE_1110
FINITE_SKILLS = {
    "1.11.0": (RELEASE_SKILLS_1110, RETAINED_SOURCE_1110),
    "1.11.1": (RELEASE_SKILLS_1111, RETAINED_SOURCE_1111),
}
```

Replace only the policy branch in `skill_inventory_errors`; keep its current
typed-folder, duplicate, missing and extra error loops:

```python
if version not in FINITE_SKILLS:
    if not source_tree:
        return []
    expected, expected_disk = present, present
else:
    expected, retained = FINITE_SKILLS[version]
    expected_disk = expected | retained if source_tree else expected
```

- [ ] **1.5 (2 minutes):** rerun 1.2; expected GREEN for both helpers and all
  subtests, with 1.12.0 retaining the prior all-source equality rule.
- [ ] **1.6 (3 minutes):** repair directly version-sensitive tests, not
  historical literals. Apply these exact substitutions:

```diff
--- tests/unit/test_factory_package.py
+++ tests/unit/test_factory_package.py
@@
-        candidates.append((root / folder / "frontier-envisioning-plugin-1.11.0.zip").read_bytes())
+        candidates.append((root / folder / "frontier-envisioning-plugin-1.11.1.zip").read_bytes())
@@
-            with zipfile.ZipFile(root / "dist/frontier-envisioning-plugin-1.11.0.zip") as archive:
+            with zipfile.ZipFile(root / "dist/frontier-envisioning-plugin-1.11.1.zip") as archive:
--- tests/unit/test_skill_maturity.py
+++ tests/unit/test_skill_maturity.py
@@
-            with zipfile.ZipFile(root / "dist/frontier-envisioning-plugin-1.11.0.zip") as archive:
+            with zipfile.ZipFile(root / "dist/frontier-envisioning-plugin-1.11.1.zip") as archive:
--- tests/unit/test_factory_export.py
+++ tests/unit/test_factory_export.py
@@
-        self.assertEqual(summary["plugin_version"], "1.11.0")
+        self.assertEqual(summary["plugin_version"], "1.11.1")
--- tests/unit/test_factory_privacy.py
+++ tests/unit/test_factory_privacy.py
@@
-                self.assertEqual(module.PLUGIN_VERSION, "1.11.0")
+                self.assertEqual(module.PLUGIN_VERSION, "1.11.1")
```

Leave calls intentionally testing `assemble(..., "1.11.0", ...)`,
`export_metadata(..., "1.11.0", ...)`, old notice anchors and release fixtures
unchanged. Before the first focused commit, run
`python tools/dev.py package` to refresh the generated version inventory needed
by the existing L0 version gate. This **intermediate** candidate is not host
acceptance or permission to install: Identity consolidation, staged mode and
budget/metadata/routing gates remain unfinished. Do not share or install it.
Final packaging/acceptance waits for all slices. The new source budget is
activated only after canonical consolidation.
- [ ] **1.7 (2 minutes):** focused commit after GREEN and scope review:

```text
chore: prepare finite 1.11.1 inventory

Refs #87. Bump before compatibility plugin edits; retain historical policies.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Commit commands are future authorised execution only; none is run in this
planning session. Use exact reviewed paths, not `git add -A`.

## 5. Task 2 — read-only installer paths, budget and truthful state

**Files:** new `tests/unit/test_cowork_install.py`,
`plugin/install/prepare_install.py`, `tools/fe_lib.py`.

### Exact CLI and stdout contract

```text
python install/prepare_install.py --root quarantine/frontier-plugin --installed /mnt/user-config/skills
python install/prepare_install.py --root quarantine/frontier-plugin --staged-root working --installed /mnt/user-config/skills
```

`--root` is mandatory and exact; invalid input never falls back to `__file__`.
The first command verifies the extracted package and emits **no save calls**.
An authorised host stages only after that succeeds. `--staged-root` names the
actual directory whose final component is `working`; its eight direct children
must be `working/<skill-name>`, not `working/frontier-plugin/skills/<name>`.
Reject missing/wrong-name selected drafts and unexpected files within a draft.
The shared `working` root may hold unrelated files and an extracted package
such as `working/install1110/pkg`; leave those siblings untouched. Reject
overlap between any selected `working/<name>` draft and the package root,
not the normal ancestry between the shared working root and a nested package.
The second command re-verifies the package **and every staged byte**, globally,
before emitting any save guidance. Python makes no filesystem writes.

Report schema: `frontier-cowork-preflight/1.0`. Keep existing `plugin`,
`display_name`, `version`, `verified`, `problems`, `skills`, `copy_calls`,
`preview_notice`, `after_install` keys. `verified` means only the requested
preflight phase, never installation. Add:

| Field | Type / meaning |
|---|---|
| `phase` | `"package"` or `"staged"` |
| `package_verified`, `staged_verified` | Native bool; all eight succeed together for finite profiles |
| `installation`, `onedrive_sync` | Always `"not-verified"` in Python; no receipts/sync capability exists here |
| `skills[].package_source` | Resolved local package skill path, explicitly read-only |
| `skills[].source` | `null` until global staged verification; then exactly `"working/<name>"` |
| `skills[].destination` | Exactly `"skills/<same name>"` |
| `skills[].files` | Total inventory count including root SKILL; skipped is never additive |
| `skills[].status` | Existing advisory `"new"`, `"update"`, `"reinstall"`, `"unknown"` comparison; not a save outcome |
| `skills[].installed_version` | Observed old/current version or null |
| `skills[].installed_equal` | Native bool or null if reads unavailable; exact read comparison, not successful-save evidence |
| `skills[].installed_problems` | Array of explicit read/equality reasons; separate from package/staged errors |

Exit 0: requested read-only preflight passed. Exit 1: invalid bytes/schema/tree.
Exit 2: CLI usage or explicit root inventory absent. All available report fields
are emitted on validation failures. No `Installed` completion message, success
fallback, installation acknowledgement or financial permission.
`copy_calls` retains the existing *guidance string* format, but only after global
staged verification, and only using whole drafts. It is not a host invocation
or receipt; the person must check actual available authorised capability.

- [ ] **2.1 (5 minutes):** create the new focused test module with the
  following complete initial code. Synthetic fixtures are explicitly test data.
  `ROOT`/`load` are the existing `_util` helpers, not repository imports in
  the shipped installer.

```python
"""Read-only Cowork package/staged preflight; host saves are separate."""
import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.unit._util import load


class CoworkInstall(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.installer = load("plugin/install/prepare_install.py")
        self.root = self.work / "quarantine"
        self.staged = self.work / "working"
        self.installed = self.work / "installed"
        self.names = sorted(Path(p).name for p in self.installer.RELEASE_SKILLS_1110)
        rows = []
        for name in self.names:
            base = self.root / "skills" / name
            base.mkdir(parents=True)
            preview = name == "frontier-agent-factory"
            optional = preview or name == "frontier-process"
            (base / "SKILL.md").write_text(
                f'---\nname: {name}\nmetadata:\n  version: "1.11.1"\n'
                f'  maturity: {"preview" if preview else "ga"}\n'
                f'  optional: "{str(optional).lower()}"\n'
                '  requires_preview_ack: "false"\n---\n',
                encoding="utf-8",
            )
            (base / "references").mkdir()
            (base / "references/data.txt").write_bytes(b"Caldova test data\n")
            rows.append({
                "name": name, "folder": "skills/" + name,
                "files": self.hashes(base), "maturity": "preview" if preview else "ga",
                "optional": optional, "requires_preview_ack": False,
            })
        self.spec = {
            "schema": "frontier-plugin-install/1.0", "plugin": "frontier-envisioning",
            "display_name": "Frontier Envisioning", "version": "1.11.1",
            "start_prompts": ["Build the identity kit demo for Caldova"], "skills": rows,
        }
        (self.root / "install").mkdir()
        self.save_spec()
        (self.root / "manifest.json").write_text(json.dumps({
            "version": "1.11.1",
            "agentSkills": [{"folder": r["folder"]} for r in rows],
        }), encoding="utf-8")

    @staticmethod
    def hashes(base):
        return {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in base.rglob("*") if p.is_file()}

    def save_spec(self):
        (self.root / "install/plugin-install.json").write_text(
            json.dumps(self.spec), encoding="utf-8",
        )

    def stage(self):
        for name in self.names:
            shutil.copytree(self.root / "skills" / name, self.staged / name)

    def call(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.installer.main([
                "--root", str(self.root), "--installed", str(self.installed), *extra,
            ])
        return code, json.loads(out.getvalue())

    def test_package_only_never_claims_installation_or_authorises_saves(self):
        before = self.hashes(self.root)
        code, result = self.call()
        self.assertEqual(code, 0, result)
        self.assertTrue(result["verified"])
        self.assertNotIn("Installed", result["after_install"])
        self.assertEqual(result["copy_calls"], [])
        self.assertTrue(result["package_verified"])
        self.assertFalse(result["staged_verified"])
        self.assertEqual(result["installation"], "not-verified")
        self.assertEqual(result["onedrive_sync"], "not-verified")
        self.assertTrue(all(r["source"] is None for r in result["skills"]))
        self.assertEqual(self.hashes(self.root), before)
        self.assertFalse(self.installed.exists())
        self.assertFalse(self.staged.exists())

    def test_explicit_missing_root_never_substitutes_the_installers_package(self):
        code, result = self.call("--root", str(self.work / "absent"))
        self.assertEqual(code, 2, result)
        self.assertFalse(result["verified"])
        self.assertEqual(result["copy_calls"], [])
        self.assertIn("absent", " ".join(result["problems"]))

    def test_all_whole_drafts_are_verified_before_any_save_guidance(self):
        self.stage()
        before = self.hashes(self.work)
        code, result = self.call("--staged-root", str(self.staged))
        self.assertEqual(code, 0, result)
        self.assertTrue(result["staged_verified"])
        self.assertEqual(len(result["copy_calls"]), 8)
        for row, call in zip(result["skills"], result["copy_calls"]):
            self.assertEqual(row["source"], "working/" + row["name"])
            self.assertEqual(row["destination"], "skills/" + row["name"])
            self.assertEqual(row["files"], 2)
            self.assertIn('source="' + row["source"] + '"', call)
            self.assertNotIn("quarantine", call)
        self.assertEqual(self.hashes(self.work), before)

    def test_working_siblings_and_nested_package_are_preserved(self):
        self.staged.mkdir()
        nested_package = self.staged / "install1110" / "pkg"
        shutil.copytree(self.root, nested_package)
        self.root = nested_package
        self.stage()
        (self.staged / "workshop-notes.txt").write_bytes(b"Caldova notes\n")
        (self.staged / "frontier-finops").mkdir()
        (self.staged / "frontier-finops/retained.txt").write_bytes(b"unselected draft\n")
        before = self.hashes(self.work)
        code, result = self.call("--staged-root", str(self.staged))
        self.assertEqual(code, 0, result)
        self.assertTrue(result["staged_verified"])
        self.assertEqual(len(result["copy_calls"]), 8)
        self.assertEqual(self.hashes(self.work), before)

    def test_older_package_over_host_budget_never_emits_save_calls(self):
        self.spec["version"] = "1.11.0"
        for row in self.spec["skills"]:
            base = self.root / row["folder"]
            skill = base / "SKILL.md"
            skill.write_bytes(skill.read_bytes().replace(b"1.11.1", b"1.11.0"))
            if row["name"] == "frontier-agent-identity":
                for index in range(20):
                    (base / "references" / f"extra-{index}.txt").write_bytes(b"test data")
            row["files"] = self.hashes(base)
        manifest_path = self.root / "manifest.json"
        manifest = json.loads(manifest_path.read_bytes())
        manifest["version"] = "1.11.0"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.save_spec()
        before = self.hashes(self.work)
        code, result = self.call()
        self.assertEqual(code, 1, result)
        self.assertIn("21 extra files", " ".join(result["problems"]))
        self.assertEqual(result["copy_calls"], [])
        self.assertEqual(self.hashes(self.work), before)

    def test_staged_missing_changed_extra_cache_and_wrong_paths_block_all_calls(self):
        for change in ("missing", "changed", "extra", "cache", "nested", "wrong-name"):
            with self.subTest(change=change):
                if self.staged.exists():
                    shutil.rmtree(self.staged)
                self.stage()
                first = self.staged / self.names[0]
                if change == "missing":
                    (first / "references/data.txt").unlink()
                elif change == "changed":
                    (first / "references/data.txt").write_bytes(b"stale\n")
                elif change == "extra":
                    (first / "extra.txt").write_bytes(b"extra\n")
                elif change == "cache":
                    (first / "__pycache__").mkdir()
                    (first / "__pycache__/cached.pyc").write_bytes(b"cache")
                elif change == "nested":
                    first.rename(self.staged / "nested")
                else:
                    first.rename(self.staged / "frontier-wrong-name")
                before = self.hashes(self.work)
                code, result = self.call("--staged-root", str(self.staged))
                self.assertEqual(code, 1, result)
                self.assertFalse(result["staged_verified"])
                self.assertEqual(result["copy_calls"], [])
                self.assertTrue(result["problems"])
                self.assertEqual(self.hashes(self.work), before)

    def test_unavailable_or_nonworking_staging_and_overlap_are_explicit(self):
        for path in (self.staged, self.root, self.root / "working"):
            with self.subTest(path=path):
                code, result = self.call("--staged-root", str(path))
                self.assertEqual(code, 1, result)
                self.assertEqual(result["copy_calls"], [])
                self.assertTrue(result["problems"])

    def test_1111_package_inventory_and_typed_paths_fail_closed(self):
        original = json.loads(json.dumps(self.spec))
        for change in ("missing", "duplicate", "finops", "bad-folder", "bad-files", "bad-digest"):
            with self.subTest(change=change):
                self.spec = json.loads(json.dumps(original))
                if change == "missing":
                    self.spec["skills"].pop()
                elif change == "duplicate":
                    self.spec["skills"].append(self.spec["skills"][0])
                elif change == "finops":
                    self.spec["skills"][0]["folder"] = "skills/frontier-finops"
                elif change == "bad-folder":
                    self.spec["skills"][0]["folder"] = "../../outside"
                elif change == "bad-files":
                    self.spec["skills"][0]["files"] = ["SKILL.md"]
                else:
                    self.spec["skills"][0]["files"]["SKILL.md"] = "bad"
                self.save_spec()
                code, result = self.call()
                self.assertEqual(code, 1, result)
                self.assertEqual(result["copy_calls"], [])
                self.assertTrue(result["problems"])
        self.spec = original
        self.save_spec()

    def test_failed_host_save_cannot_turn_old_version_into_installed_success(self):
        # A refused save makes no writes. Python has no actual host receipt API.
        old = self.installed / self.names[0]
        shutil.copytree(self.root / "skills" / self.names[0], old)
        skill = old / "SKILL.md"
        skill.write_bytes(skill.read_bytes().replace(b"1.11.1", b"1.9.2"))
        before = self.hashes(self.installed)
        self.stage()
        code, result = self.call("--staged-root", str(self.staged))
        self.assertEqual(code, 0, result)
        row = next(r for r in result["skills"] if r["name"] == self.names[0])
        self.assertEqual(row["installed_version"], "1.9.2")
        self.assertEqual(row["status"], "update")
        self.assertFalse(row["installed_equal"])
        self.assertEqual(result["installation"], "not-verified")
        self.assertEqual(before, self.hashes(self.installed))

    def test_installed_equality_still_needs_actual_receipts_and_sync(self):
        shutil.copytree(self.root / "skills", self.installed)
        self.stage()
        code, result = self.call("--staged-root", str(self.staged))
        self.assertEqual(code, 0, result)
        self.assertTrue(all(r["installed_equal"] for r in result["skills"]))
        self.assertEqual(result["installation"], "not-verified")
        self.assertEqual(result["onedrive_sync"], "not-verified")
        extra = self.installed / self.names[0] / "extra.txt"
        extra.write_bytes(b"obsolete")
        code, result = self.call("--staged-root", str(self.staged))
        self.assertEqual(code, 0, result)
        self.assertFalse(result["skills"][0]["installed_equal"])
        self.assertTrue(extra.is_file())

    def test_recursive_twenty_extras_nested_skill_and_cache_are_counted(self):
        base = self.work / "budget"
        base.mkdir()
        (base / "SKILL.md").write_bytes(b"root")
        (base / "nested").mkdir()
        for index in range(19):
            (base / "nested" / f"{index}.txt").write_bytes(b"data")
        (base / "nested/SKILL.md").write_bytes(b"nested is not exempt")
        expected = self.hashes(base)
        self.assertEqual(len(expected), 21)
        self.assertEqual(self.installer.skill_file_errors(base, expected, "budget"), [])
        (base / "nested/overflow.txt").write_bytes(b"extra")
        self.assertIn("21 extra files", " ".join(
            self.installer.skill_file_errors(base, self.hashes(base), "budget"),
        ))
        (base / "nested/overflow.txt").unlink()
        (base / "nested/0.txt").unlink()
        (base / "__pycache__").mkdir()
        (base / "__pycache__/cached.pyc").write_bytes(b"cache")
        self.assertEqual(len(self.hashes(base)), 21)
        self.assertIn("cache", " ".join(
            self.installer.skill_file_errors(base, self.hashes(base), "budget"),
        ))
```

- [ ] **2.2 (2 minutes):** initial RED:
  `python -B -m unittest tests.unit.test_cowork_install.CoworkInstall.test_package_only_never_claims_installation_or_authorises_saves tests.unit.test_cowork_install.CoworkInstall.test_explicit_missing_root_never_substitutes_the_installers_package -v`.
  Expected failures: present “Installed”/nested copy guidance and fallback to
  the installer's own root, not parser support for quoted metadata.
  Keep the nested-package/shared-workspace and older over-budget controls in
  the full-module run. They reject a false requirement for an empty workspace
  and a version-specific exemption from the current host file limit.
- [ ] **2.3 (5 minutes):** add `import os` and `import stat` to the installer.
  Add these small canonical read-only helpers before `main`. They read regular
  files only; symlinks/junctions/reparse points cannot escape either root.
  No cache filtering hides files before the recursive count.

```python
CACHE_PARTS = {"__pycache__", ".pytest_cache", ".ruff_cache", ".DS_Store", "dist"}


def checked_child(root: Path, relative: str) -> Path:
    path = root
    paths = [path]
    for part in relative.split("/") if relative else ():
        path = path / part
        paths.append(path)
    for candidate in paths:
        info = candidate.lstat()
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError(f"{candidate}: link or reparse point is not a package/draft path")
    return path


def tree_hashes(base: Path) -> dict[str, str]:
    result: dict[str, str] = {}

    def visit(path: Path) -> None:
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0)
            & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        ):
            raise ValueError(f"{path}: link or reparse point is not a regular draft")
        if stat.S_ISDIR(info.st_mode):
            with os.scandir(path) as entries:
                children = sorted(Path(entry.path) for entry in entries)
            for child in children:
                visit(child)
        elif stat.S_ISREG(info.st_mode):
            result[path.relative_to(base).as_posix()] = sha256(path)
        else:
            raise ValueError(f"{path}: not a regular file or directory")

    if not base.is_dir():
        raise ValueError(f"{base}: skill directory missing")
    visit(base)
    return result


def skill_file_errors(
    base: Path, files: object, label: str, *, budget: bool = True
) -> list[str]:
    if not isinstance(files, dict) or "SKILL.md" not in files:
        return [f"{label}: files must be an object including root SKILL.md"]
    for relative, digest in files.items():
        if (
            not isinstance(relative, str) or not relative
            or "\\" in relative or ":" in relative
            or any(part in {"", ".", ".."} for part in relative.split("/"))
            or Path(relative).is_absolute()
            or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
        ):
            return [f"{label}: invalid file path or SHA256 in inventory"]
    try:
        actual = tree_hashes(base)
    except (OSError, ValueError) as exc:
        return [f"{label}: {exc}"]
    problems = []
    extras = len(set(actual) - {"SKILL.md"})
    if budget and extras > 20:
        problems.append(f"{label}: {extras} extra files exceeds 20 (root SKILL.md only is exempt)")
    for relative in sorted(actual):
        if set(relative.split("/")) & CACHE_PARTS or relative.endswith((".pyc", ".pyo", ".new")):
            problems.append(f"{label}/{relative}: cache or temporary file is not shipped")
    for relative in sorted(set(files) - set(actual)):
        problems.append(f"{label}/{relative} is missing")
    for relative in sorted(set(actual) - set(files)):
        problems.append(f"{label}/{relative} is not part of the release")
    for relative in sorted(set(actual) & set(files)):
        if actual[relative] != files[relative]:
            problems.append(f"{label}/{relative} differs from the released file (checksum)")
    return problems


def compare_installed(installed: Path, name: str, version: str, files: dict) -> dict:
    base = installed / name
    try:
        if installed.exists() and not installed.is_dir():
            raise ValueError(f"{installed}: installed skills root is not a directory")
        if not base.exists():
            return {"status": "new", "installed_version": None,
                    "installed_equal": False, "installed_problems": [f"{name}: not installed"]}
        checked_child(installed, name)
        tree_hashes(base)  # Unavailable reads yield unknown, not installed mismatch.
        fm = frontmatter(base / "SKILL.md")
        old = fm.get("version")
        problems = skill_file_errors(base, files, f"installed/{name}")
        if fm.get("name") != name or old != version:
            problems.append(f"installed/{name}: name/version does not equal candidate {version}")
        return {"status": "unknown" if old is None else "reinstall" if old == version else "update",
                "installed_version": old, "installed_equal": not problems,
                "installed_problems": problems}
    except (OSError, ValueError) as exc:
        return {"status": "unknown", "installed_version": None,
                "installed_equal": None, "installed_problems": [f"installed/{name}: {exc}"]}
```

- [ ] **2.4 (5 minutes):** replace `main` with the following complete
  implementation, keeping `frontmatter`, finite inventory, `sha256` and the
  entry-point intact. Remove unused `workspace_relative` after callers are
  updated: package paths are read-only local paths, save sources are exact
  workspace whole drafts. An explicit inventory with bad types fails before
  path composition. Existing legacy maturity probes keep their version-scoped
  inventory behaviour and Preview notice.

```python
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, help="exact extracted package root (read-only)")
    ap.add_argument("--installed", default=DEFAULT_INSTALLED, help="installed skills root (read-only)")
    ap.add_argument("--staged-root", help="actual working directory of whole drafts (read-only)")
    a = ap.parse_args(argv)
    root = Path(a.root).absolute()
    result = {
        "schema": "frontier-cowork-preflight/1.0",
        "plugin": None, "display_name": None, "version": None,
        "phase": "staged" if a.staged_root else "package",
        "verified": False, "package_verified": False, "staged_verified": False,
        "installation": "not-verified", "onedrive_sync": "not-verified",
        "problems": [], "skills": [], "copy_calls": [], "preview_notice": "",
        "after_install": "Preflight failed. Do not stage or save skills.",
    }
    problems = result["problems"]

    def emit(code: int) -> int:
        print(json.dumps(result, ensure_ascii=False, indent=1))
        return code

    plan_file = root / "install/plugin-install.json"
    try:
        checked_child(root, "install/plugin-install.json")
        if not plan_file.is_file():
            raise ValueError("installer inventory is not a regular file")
    except (OSError, ValueError) as exc:
        problems.append(f"{plan_file}: {exc}; extract the whole ZIP; no root substitution")
        return emit(2)
    try:
        spec = json.loads(plan_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"{plan_file}: invalid or unreadable JSON: {exc}")
        return emit(1)
    if not isinstance(spec, dict):
        problems.append("installer inventory must be an object")
        return emit(1)
    for key in ("plugin", "display_name", "version"):
        result[key] = spec.get(key)
    version = spec.get("version")
    if spec.get("plugin") != PLUGIN:
        problems.append(f"this installer is for {PLUGIN}")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        problems.append("installer version must be MAJOR.MINOR.PATCH")
    rows = spec.get("skills")
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        problems.append("installer skills must be a nonempty list of objects")
        return emit(1)
    names = []
    for row in rows:
        name = row.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            problems.append("installer skill name must be lowercase hyphenated words")
        elif row.get("folder") != "skills/" + name:
            problems.append(f"{name}: folder must be skills/{name}")
        names.append(name)
        if not isinstance(row.get("files"), dict):
            problems.append(f"{name}: files must be an object")
    if problems:
        return emit(1)
    if len(names) != len(set(names)):
        problems.append("duplicate installer skill name")
    if version in FINITE_SKILLS:
        if spec.get("schema") != "frontier-plugin-install/1.0":
            problems.append("current installer inventory schema must be frontier-plugin-install/1.0")
        skill_root = root / "skills"
        try:
            checked_child(root, "skills")
            disk = ["skills/" + p.name for p in skill_root.iterdir() if p.is_dir()]
            if any(not p.is_dir() for p in skill_root.iterdir()):
                problems.append("package skills root holds an unexpected non-directory")
        except (OSError, ValueError) as exc:
            disk = []
            problems.append(f"{skill_root}: {exc}")
        problems.extend(skill_inventory_errors(
            version, [row["folder"] for row in rows], disk, source_tree=False,
        ))
        try:
            manifest_path = checked_child(root, "manifest.json")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problems.append(f"release manifest missing or invalid: {exc}")
        else:
            if not isinstance(manifest, dict) or manifest.get("version") != version:
                problems.append("release manifest version differs from installer")
            else:
                entries = manifest.get("agentSkills")
                if not isinstance(entries, list) or not all(isinstance(row, dict) for row in entries):
                    problems.append("manifest agentSkills must be a list of objects")
                else:
                    problems.extend(skill_inventory_errors(
                        version, [row.get("folder") for row in entries], disk, source_tree=False,
                    ))
    if problems:
        return emit(1)
    for sk in rows:
        name, folder, files = sk["name"], sk["folder"], sk["files"]
        base = root / folder
        try:
            checked_child(root, folder)
        except (OSError, ValueError) as exc:
            problems.append(f"{folder}: {exc}")
            continue
        problems.extend(skill_file_errors(base, files, folder))
        try:
            fm = frontmatter(base / "SKILL.md")
        except OSError as exc:
            problems.append(f"{folder}/SKILL.md: {exc}")
            fm = {}
        if fm.get("name") != name or fm.get("version") != version:
            problems.append(f"{folder}/SKILL.md name/version does not equal {name}/{version}")
        maturity = {key: sk.get(key) for key in ("maturity", "optional", "requires_preview_ack")}
        for key, value in maturity.items():
            if key == "maturity":
                if not isinstance(value, str) or value not in {"ga", "preview"}:
                    problems.append(f"{folder}: unknown product maturity")
            elif type(value) is not bool:
                problems.append(f"{folder}: {key} must be a boolean")
            if value != fm.get(key):
                problems.append(f"{folder}: {key} metadata differs from SKILL.md")
        expected = (
            {"maturity": "preview", "optional": True, "requires_preview_ack": True}
            if name == "frontier-finops" else
            {"maturity": "preview", "optional": True, "requires_preview_ack": False}
            if name == "frontier-agent-factory" else
            {"maturity": "ga", "optional": name == "frontier-process", "requires_preview_ack": False}
        )
        if maturity != expected:
            problems.append(f"{folder}: maturity/optional/acknowledgement contract differs")
        result["skills"].append({
            "name": name, "package_source": str(base.resolve()), "source": None,
            "destination": "skills/" + name, "files": len(files), **maturity,
            **compare_installed(Path(a.installed), name, version, files),
        })
    if problems:
        return emit(1)
    result["package_verified"] = True
    notices = []
    if any(row["requires_preview_ack"] is True for row in rows):
        notices.append(
            "Frontier FinOps is Preview, not GA; grounding and model need refinement. "
            "Installation is not acknowledgement of use; cost operations need explicit acknowledgement."
        )
    if "frontier-agent-factory" in names:
        notices.append(
            "Envisioning Agent Factory is optional Preview, not GA. Installation grants "
            "no source-transfer, review, repository, tenant or deployment permission. "
            "Actual Cowork validation is not performed."
        )
    result["preview_notice"] = " ".join(notices)
    if a.staged_root:
        staged = Path(a.staged_root).absolute()
        if staged.name != "working":
            problems.append(f"{staged}: expected whole drafts under working/<name>")
        try:
            checked_child(staged, "")
            package_resolved = root.resolve()
            for name in names:
                draft = (staged / name).resolve()
                if (draft == package_resolved
                        or draft.is_relative_to(package_resolved)
                        or package_resolved.is_relative_to(draft)):
                    problems.append(f"working/{name}: selected draft overlaps the package root")
        except (OSError, ValueError, RuntimeError) as exc:
            problems.append(f"{staged}: staging unavailable or directory unreadable: {exc}")
        if not problems:
            for sk in rows:
                try:
                    checked_child(staged, sk["name"])
                except (OSError, ValueError) as exc:
                    problems.append(f"working/{sk['name']}: {exc}")
                    continue
                problems.extend(skill_file_errors(
                    staged / sk["name"], sk["files"], "working/" + sk["name"],
                ))
        if problems:
            result["after_install"] = "Package verified; staged verification failed. Do not save any skill."
            return emit(1)
        result["staged_verified"] = True
        for row in result["skills"]:
            row["source"] = "working/" + row["name"]
        result["copy_calls"] = [
            f'CopyArtifact(surface="user", source="{row["source"]}", '
            f'destination="{row["destination"]}", recursive=true, overwrite=true)'
            f'  # expect copied={row["files"]} total files; skipped is not additive'
            for row in result["skills"]
        ]
        result["after_install"] = (
            "Package and staged bytes verified; installation and OneDrive sync not verified. "
            "Use actual authorised host saves, retain each receipt and verify installed bytes."
        )
    else:
        result["after_install"] = (
            "Package verified; authorised whole-draft staging and staged verification required "
            "before any save. Installation and OneDrive sync not verified."
        )
    result["verified"] = True
    return emit(0)
```

The current host budget applies to every package/draft for which this new
installer emits save guidance, including an older requested package. Do not
modify old release bytes or old source-qualified reproduction tools. Existing
historical source/packaging profiles stay unchanged; a too-large old package
gets an explicit install-preflight failure, not misleading guidance.

Keep `maturity`/`version` validated before set/map membership and names
validated before constructing sets. `files` is validated before reads; expected
digests are never computed from staged bytes. This implementation strengthens
current logical optional checks (Process true, other GA false) without changing
their values.
- [ ] **2.5 (2 minutes):** GREEN: rerun 2.2, then
  `python -B -m unittest tests.unit.test_cowork_install -v`.
  All focused installer tests should pass. Missing/wrong staged paths and tampered bytes
  must return 1 with no save guidance. No test says it executed a host save.
- [ ] **2.6 (3 minutes):** add these two forwarders in `tools/fe_lib.py`
  next to the existing `skill_inventory_errors`; this keeps the shipped
  installer stdlib-only and repository imports one-way:

```python
def skill_file_errors(
    base: Path, files: object, label: str, *, budget: bool = True
) -> list[str]:
    installer = load_module(PLUGIN / "install" / "prepare_install.py", "fe_install_files")
    return installer.skill_file_errors(base, files, label, budget=budget)


def tree_hashes(base: Path) -> dict[str, str]:
    installer = load_module(PLUGIN / "install" / "prepare_install.py", "fe_install_tree")
    return installer.tree_hashes(base)
```

- [ ] **2.7 (3 minutes):** update the installer module docstring to the
  exact CLI/fields/exit semantics above; remove “Exit 0 = ready to install”,
  package-only `Installed` and fallback claims. Delete unused
  `workspace_relative` (no remaining planned caller). Run the existing
  `python -B -m unittest tests.unit.test_skill_maturity -v` after Task 3/5
  integration is available; until then run its installer-only methods:

```text
python -B -m unittest tests.unit.test_skill_maturity.SkillMaturity.test_factory_installer_matrix_and_reinstall_never_grants_consent tests.unit.test_skill_maturity.SkillMaturity.test_existing_finops_update_or_reinstall_never_inherits_cached_consent tests.unit.test_skill_maturity.SkillMaturity.test_installer_rejects_nonboolean_acknowledgement_metadata -v
```

Expected existing regressions pass; parser quote support was already GREEN.
- [ ] **2.8 (2 minutes):** review read-only behaviour, type/path guards and
  package/staged/installed state separation; commit:

```text
fix: verify Cowork whole drafts before save guidance

Refs #87. Read-only preflight; exact inventories, hashes and truthful phase state.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## 6. Task 3 — canonical Identity, original-data fixture and parity

**Files:** Identity `references/identity-method.md`,
delete current `references/brand-discovery.md`, `references/kit-reference.md`,
move `examples/caldova-brand.json` to `tests/fixtures/caldova-brand.json`,
Identity `SKILL.md`, `tools/selftest.py`;
new `tests/fixtures/cowork-identity-originals.json`,
new `tests/unit/test_cowork_identity.py`.
The repository-only snapshot is preservation evidence/test input, not a
shipped second tree or generic build-time repacker.

- [ ] **3.1 (3 minutes):** before consolidation, capture the three literal
  original references, brand bytes and unchanged path/digest inventory.
  Use this exact one-time offline fixture command. It asserts the actually
  inspected 24-file source and excludes only the four explicitly changed
  files plus root SKILL from the byte-preservation inventory. It cannot reset
  an existing snapshot:

```text
python -B -c "import hashlib,json; from pathlib import Path; a=Path('plugin/skills/frontier-agent-identity'); target=Path('tests/fixtures/cowork-identity-originals.json'); assert not target.exists(); paths=sorted(p for p in a.rglob('*') if p.is_file()); assert len(paths)==24; refs={name:(a/'references'/name).read_text(encoding='utf-8') for name in ('identity-method.md','brand-discovery.md','kit-reference.md')}; changed={'SKILL.md','references/identity-method.md','references/brand-discovery.md','references/kit-reference.md','examples/caldova-brand.json'}; install=json.loads(Path('plugin/install/plugin-install.json').read_bytes()); assert len(install['skills'])==8; record={'references':refs,'brand_hex':(a/'examples/caldova-brand.json').read_bytes().hex(),'unchanged':{p.relative_to(a).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.relative_to(a).as_posix() not in changed},'shipped_paths':{row['name']:sorted(row['files']) for row in install['skills']}}; target.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')"
```

Review the captured source against approved `b9647ea`; standard version-carrier
changes do not affect these references/scripts/kit/example bytes. Never refresh
this snapshot to bless a failed parity check.
- [ ] **3.2 (5 minutes):** add this complete test module:

```python
"""Lossless current Identity consolidation and configured full-kit equality."""
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.unit._util import ROOT, load

IDENTITY = ROOT / "plugin/skills/frontier-agent-identity"
SNAPSHOT = ROOT / "tests/fixtures/cowork-identity-originals.json"
BRAND = ROOT / "tests/fixtures/caldova-brand.json"


def consolidated(record):
    refs = record["references"]
    brand = bytes.fromhex(record["brand_hex"]).decode("utf-8")
    return (
        refs["identity-method.md"]
        + '\n<a id="brand-discovery"></a>\n\n## Brand discovery for the identity kit\n\n'
        + refs["brand-discovery.md"].split("\n", 1)[1].lstrip("\n")
        + '\n<a id="kit-reference"></a>\n\n## Identity kit reference\n\n'
        + refs["kit-reference.md"].split("\n", 1)[1].lstrip("\n")
        + '\n<a id="caldova-brand-example"></a>\n\n## Complete Caldova brand example\n\n```json\n'
        + brand.rstrip("\n") + "\n```\n"
    )


def file_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


class CoworkIdentity(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    def test_references_brand_anchors_and_fences_are_lossless(self):
        actual = (IDENTITY / "references/identity-method.md").read_text(encoding="utf-8")
        self.assertEqual(actual, consolidated(self.record))
        self.assertEqual(BRAND.read_bytes(), bytes.fromhex(self.record["brand_hex"]))
        embedded = actual.rsplit("```json\n", 1)[1].split("\n```", 1)[0]
        self.assertEqual(json.loads(embedded), json.loads(BRAND.read_bytes()))
        for name in ("brand-discovery.md", "kit-reference.md"):
            self.assertFalse((IDENTITY / "references" / name).exists())
        self.assertFalse((IDENTITY / "examples/caldova-brand.json").exists())
        skill = (IDENTITY / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/identity-method.md#brand-discovery", skill)
        self.assertIn("references/identity-method.md#kit-reference", skill)
        self.assertIn("other demo examples", skill)
        self.assertNotIn("references/brand-discovery.md", skill)
        self.assertNotIn("references/kit-reference.md", skill)
        self.assertIn("tests/fixtures/caldova-brand.json",
                      (ROOT / "tools/selftest.py").read_text(encoding="utf-8"))

    def test_scripts_kit_two_examples_and_exact_twenty_extras_are_preserved(self):
        lib = load("tools/fe_lib.py")
        actual = lib.tree_hashes(IDENTITY)
        self.assertEqual(len(actual), 21)
        self.assertEqual(lib.skill_file_errors(IDENTITY, actual, "Identity"), [])
        for name, digest in self.record["unchanged"].items():
            self.assertEqual(actual[name], digest, name)
        self.assertEqual(
            set(actual),
            set(self.record["unchanged"]) | {"SKILL.md", "references/identity-method.md"},
        )

    def test_all_shipped_source_paths_and_budgets_match_the_bounded_change(self):
        lib = load("tools/fe_lib.py")
        installer = load("plugin/install/prepare_install.py")
        names = {Path(folder).name for folder in installer.RELEASE_SKILLS_1111}
        self.assertEqual(set(self.record["shipped_paths"]), names)
        removed = {"references/brand-discovery.md", "references/kit-reference.md",
                   "examples/caldova-brand.json"}
        for name, original_paths in self.record["shipped_paths"].items():
            expected = set(original_paths)
            if name == "frontier-agent-identity":
                expected -= removed
            base = ROOT / "plugin/skills" / name
            actual = lib.tree_hashes(base)
            self.assertEqual(set(actual), expected, name)
            self.assertEqual(lib.skill_file_errors(base, actual, name), [])
        # Reuse the same source inventory/hash helper to refuse an unexpected
        # ordinary file even when a small shipped skill remains below 20 extras.
        base = ROOT / "plugin/skills/frontier-process"
        expected_files = lib.tree_hashes(base)
        with tempfile.TemporaryDirectory() as directory:
            draft = Path(directory) / "frontier-process"
            shutil.copytree(base, draft)
            (draft / "unexpected.txt").write_bytes(b"not in approved source inventory")
            self.assertLessEqual(len(lib.tree_hashes(draft)) - 1, 20)
            self.assertTrue(any("not part of the release" in error
                                for error in lib.skill_file_errors(draft, expected_files, "source")))

    def build_full(self, source, out):
        lib = load("tools/fe_lib.py")
        maker = lib.load_module(source / "scripts/make_kit.py", "cwi_make_kit")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = maker.main([
                "--config", str(source / "examples/caldova-agent-identity.json"),
                "--palette", str(source / "examples/caldova-palette.json"),
                "--out", str(out), "--no-png",
            ])
        self.assertEqual(code, 0, buffer.getvalue())
        self.assertEqual(json.loads(buffer.getvalue())["tests"], "passed")
        raster = load("tools/demo_raster.py")
        # Identical pinned inputs/profile/date/tools for original and consolidated.
        report = raster.replay(out, version="1.11.0")
        builder = maker.load_kit_module(out / "scripts", "build_identity_assets")
        docs = maker.load_kit_module(out / "scripts", "identity_docs")
        config = json.loads((out / "config/agent-identity.json").read_bytes())
        palette = json.loads((out / "config/palette.json").read_bytes())
        readme = docs.readme_md(config, palette, builder.by_journey(config, palette), True).encode()
        self.assertEqual(hashlib.sha256(readme).hexdigest(), report["readme_sha256"])
        (out / "README.md").write_bytes(readme)
        result = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", "scripts/tests", "-v"],
            cwd=out, capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return file_bytes(out)

    def test_original_and_consolidated_complete_429_file_kits_are_identical(self):
        for name, digest in self.record["unchanged"].items():
            self.assertEqual(hashlib.sha256((IDENTITY / name).read_bytes()).hexdigest(), digest)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "original-source"
            shutil.copytree(IDENTITY, original, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for name, text in self.record["references"].items():
                (original / "references" / name).write_text(text, encoding="utf-8", newline="\n")
            (original / "examples/caldova-brand.json").write_bytes(bytes.fromhex(self.record["brand_hex"]))
            before = self.build_full(original, root / "original" / "caldova-agent-identity")
            after = self.build_full(IDENTITY, root / "consolidated" / "caldova-agent-identity")
            self.assertEqual(len(before), 429)
            self.assertEqual(len(after), 429)
            self.assertEqual(set(before), set(after))
            self.assertEqual(before, after)
```

The reconstructed original is strictly the snapshot's original references/
brand plus hash-proven unchanged scripts/kit/two examples. It executes only
trusted repository kit code, never a downloaded repack/template script.
Full raster restoration happens **after** all pinned non-raster inputs match.
No golden ZIP overwrite, invented ZIP digest or incomplete SVG-only 429 claim.
- [ ] **3.3 (2 minutes):** RED:
  `python -B -m unittest tests.unit.test_cowork_identity.CoworkIdentity.test_references_brand_anchors_and_fences_are_lossless tests.unit.test_cowork_identity.CoworkIdentity.test_scripts_kit_two_examples_and_exact_twenty_extras_are_preserved -v`.
  Expected current separate reference tree fails exact reconstruction and
  Identity's 24-versus-21 file count. The unavailable moved fixture is also a
  required new artifact, not a reason to invent data.
- [ ] **3.4 (5 minutes):** using `apply_patch`, move the **literal** original
  brand JSON to `tests/fixtures/caldova-brand.json`, with identical bytes.
  Consolidate `identity-method.md` to the exact `consolidated(record)` result
  above. Keep its original content first, convert only the other two H1s to
  the two displayed H2s, preserve their complete remaining text/fences and
  append the complete literal brand example. Delete only the two redundant
  current source notes. No build-time transformation or new product tool.
  The equality test defines the complete edit, including anchors and fences.
- [ ] **3.5 (3 minutes):** apply these exact directly coupled edits:

```diff
--- plugin/skills/frontier-agent-identity/SKILL.md
+++ plugin/skills/frontier-agent-identity/SKILL.md
@@
-Follow [references/brand-discovery.md](references/brand-discovery.md).
+Follow [Brand discovery](references/identity-method.md#brand-discovery).
@@
-Layout and options: [references/kit-reference.md](references/kit-reference.md).
+Layout and options: [Identity kit reference](references/identity-method.md#kit-reference).
@@
-- `examples/caldova-brand.json`, `examples/caldova-agent-identity.json`, `examples/caldova-palette.json` - fictitious demo
-- `references/identity-method.md`, `references/brand-discovery.md`, `references/kit-reference.md`
+- [Complete Caldova brand example](references/identity-method.md#caldova-brand-example); other demo examples: `examples/caldova-agent-identity.json`, `examples/caldova-palette.json`
+- `references/identity-method.md` - naming method, brand discovery and kit reference
--- tools/selftest.py
+++ tools/selftest.py
@@
-        code, out = run(si, ["--blueprint", str(sample), "--brand", str(ai / "examples/caldova-brand.json"), "--prefix", "cal",
+        code, out = run(si, ["--blueprint", str(sample), "--brand", str(ROOT / "tests/fixtures/caldova-brand.json"), "--prefix", "cal",
```

The two first SKILL replacements are substrings of the actual long workflow
paragraphs; keep the surrounding sentences exactly. Do not change Identity
scripts, kit bytes, the other demo inputs or historical source inventories.
- [ ] **3.6 (2 minutes):** GREEN: rerun 3.3. Then queue
  `python -B -m unittest tests.unit.test_cowork_identity -v`.
  Expected all initial four tests pass, including actual configured generated-kit
  test execution and complete 429-path/byte equality. Record actual counts,
  duration and any failure; the supplied report is not this run.
- [ ] **3.7 (2 minutes):** document review of content/anchors/fences, fixture
  ancestry and exact removed files; focused commit:

```text
refactor: consolidate Identity references losslessly

Refs #87. Keep kit scripts and demo bytes; retain exact brand fixture and seed input.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## 7. Task 4 — quoted metadata and scope-qualified procedures

**Files:** all eight shipped `plugin/skills/<name>/SKILL.md` files named in
the approved design, `tests/unit/test_skill_maturity.py`, `tools/fe_lib.py`,
`tools/check_repo.py`. FinOps's existing unquoted Preview acknowledgement is
source-only and unchanged (apart from Task 1's standard version carrier).

- [ ] **4.1 (3 minutes):** add this test to the existing `SkillMaturity`
  class; no new imports are needed:

```python
def test_shipped_raw_booleans_are_quoted_with_unchanged_typed_values(self):
    lib = load("tools/fe_lib.py")
    installer = load("plugin/install/prepare_install.py")
    for folder in sorted(installer.RELEASE_SKILLS_1111):
        path = ROOT / "plugin" / folder / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        block = text.split("---", 2)[1]
        name = path.parent.name
        optional = name in {"frontier-process", "frontier-agent-factory"}
        for key, value in (("optional", optional), ("requires_preview_ack", False)):
            expected = f'  {key}: "{str(value).lower()}"'
            self.assertIn(expected, block.splitlines(), name)
        fields = lib.maturity_fields(lib.frontmatter(text))
        self.assertIs(fields["optional"], optional)
        self.assertIs(fields["requires_preview_ack"], False)
        self.assertEqual(fields["maturity"], "preview" if name == "frontier-agent-factory" else "ga")
        self.assertEqual(installer.frontmatter(path)["optional"], optional)
```

- [ ] **4.2 (2 minutes):** RED:
  `python -B -m unittest tests.unit.test_skill_maturity.SkillMaturity.test_shipped_raw_booleans_are_quoted_with_unchanged_typed_values -v`.
  Expected actual unquoted shipped frontmatter fails. **Do not claim either
  existing parser fails to support quotes.**
- [ ] **4.3 (3 minutes):** only in the eight shipped frontmatter blocks,
  replace these exact logical values:

```yaml
  maturity: ga
  optional: "false"
  requires_preview_ack: "false"
```

Process keeps `maturity: ga`, with:

```yaml
  optional: "true"
  requires_preview_ack: "false"
```

Factory keeps:

```yaml
  maturity: preview
  optional: "true"
  requires_preview_ack: "false"
```

Do not quote JSON booleans, change metadata schema, alter core financial
acknowledgements or touch FinOps's `requires_preview_ack: true`.
- [ ] **4.4 (2 minutes):** GREEN: rerun 4.2. Existing
  `test_packager_reads_maturity_and_optional_fields` remains an unquoted parser
  regression. Add this separate *already-supported* quoted parser regression,
  not a fictional RED:

```python
def test_quoted_values_already_parse_as_native_installer_booleans(self):
    package = load("tools/build_package.py")
    installer = load("plugin/install/prepare_install.py")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "SKILL.md"
        path.write_text(
            '---\nname: frontier-process\nmetadata:\n  version: "1.11.1"\n'
            '  maturity: ga\n  optional: "true"\n  requires_preview_ack: "false"\n---\n',
            encoding="utf-8",
        )
        for fields in (package.frontmatter(path), installer.frontmatter(path)):
            self.assertIs(fields["optional"], True)
            self.assertIs(fields["requires_preview_ack"], False)
```

- [ ] **4.5 (3 minutes):** add a checker regression to `SkillMaturity`.
  This is a new raw-contract checker, not a parser change:

```python
def test_raw_quote_checker_refuses_unquoted_and_wrongly_typed_spelling(self):
    lib = load("tools/fe_lib.py")
    good = ('---\nname: frontier-process\nmetadata:\n'
            '  optional: "true"\n  requires_preview_ack: "false"\n---\n')
    self.assertEqual(lib.quoted_metadata_errors(good), [])
    for bad in (good.replace('"true"', "true"), good.replace('"false"', '"0"'),
                good.replace('  optional: "true"\n', ""),
                good.replace('  optional: "true"\n', '  optional: "true"\n  optional: true\n')):
        self.assertTrue(lib.quoted_metadata_errors(bad))
```

RED command:
`python -B -m unittest tests.unit.test_skill_maturity.SkillMaturity.test_raw_quote_checker_refuses_unquoted_and_wrongly_typed_spelling -v`.
Expected missing new checker API before implementation, not a failing parser.
Add the complete helper to `fe_lib` next to its frontmatter helpers:

```python
def quoted_metadata_errors(text: str) -> list[str]:
    block = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not block:
        return ["SKILL.md frontmatter missing"]
    errors = []
    for key in ("optional", "requires_preview_ack"):
        values = re.findall(rf"(?m)^  {key}:\s*([^\r\n]*)\r?$", block[1])
        if len(values) != 1 or values[0] not in {'"true"', '"false"'}:
            errors.append(f"{key} must use one quoted true/false in shipped SKILL metadata")
    return errors
```

Import `quoted_metadata_errors` in `check_repo`'s existing `fe_lib` import.
Add this exact bounded gate at the end of the existing `check_skills` metadata
loop, not to FinOps or the versionless shared-copy fixture:

```python
if manifest.get("version") == "1.11.1" and "skills/" + d.name in listed:
    for error in quoted_metadata_errors((d / "SKILL.md").read_text(encoding="utf-8")):
        r.err("skills", f"{d.name}: {error}")
```

GREEN: rerun the checker regression and the raw shipped regression together.
Run `python tools/check_repo.py --strict` after Task 5/6 generated inventory
is refreshed; no assertion is weakened merely to bypass stale version metadata.
- [ ] **4.6 (4 minutes):** replace only Factory's root description with:

```yaml
description: |
  Prepares an explicitly requested full starter-repository ZIP from a pinned
  compatible template and reviewed Frontier envisioning artefacts. Optional Preview.
  Use for "prepare a full Caldova starter-repository ZIP" or "package the reviewed
  MVP as a full starter ZIP". Do NOT use for writing PRDs, target architecture or
  ADRs (frontier-solution-design), HTML (frontier-blueprint), application code,
  live repository or tenant operations, or deployment. For vague "set up a repo",
  clarify document work versus an offline full ZIP; do not perform live setup.
  FinOps cost operations are not included in this release.
```

Replace only Solution Design's description with:

```yaml
description: |
  Writes or refines PRDs, target architecture, solution design, ADRs and IT readiness
  documents for MVP agents in a Frontier envisioning, grounded in Microsoft's
  Frontier guidance and the customer's blueprint and workshop evidence.
  Use for "write the Caldova MVP PRD", "design the target architecture" or
  "create the solution design and ADRs". Repository document scaffolding means
  Markdown design documents, not a full starter ZIP. For an explicit full
  starter-repository ZIP from reviewed artefacts, use optional Preview
  frontier-agent-factory. For vague "set up a repo", clarify intent.
  Do NOT use for blueprint HTML (frontier-blueprint), discovery
  (frontier-context-discovery), application code or live repository setup.
```

Replace only Context Discovery's description with:

```yaml
description: |
  Gathers scoped business context and Work IQ evidence for an explicit Frontier
  engagement or workshop: cited strategy, journeys, pains, KPIs, systems,
  stakeholders, constraints and open questions. Use for "gather the Caldova
  context for the Frontier workshop" or "analyse the Frontier engagement transcript".
  Generic organisation-wide Work IQ requests outside a Frontier engagement are
  not captured by this skill merely because Work IQ is mentioned.
  Do NOT use for blueprint HTML (frontier-blueprint), PRD or architecture
  (frontier-solution-design), or a plain meeting recap (meeting-intel).
```

Keep all other descriptions, especially Process/Value Case mutual scope, intact.
Update Solution Design's “scaffold the design repository” When-to-Use bullet
to **“Scaffold design documents in a repository (Markdown files only, not a
full starter-repository ZIP)”**. Add its vague-repo clarification to Inputs
before any scaffold command. Add Context Discovery's explicit Frontier
engagement scope check to Step 1, and its generic organisation-wide Work IQ
exclusion to When NOT to Use. Do not edit external `work-iq-sphere`.
- [ ] **4.7 (5 minutes):** add Factory **When not to use**, before Step 1,
  with the exact six scope outcomes from design section 6. Consolidate existing
  controls into an explicit **Guardrails** section without duplicating them:
  move, verbatim, these actual paragraph groups to its named subheadings:

| New Guardrails subheading | Move the existing exact paragraph group |
|---|---|
| Host capability and passive code | Before Step 1: “Actual Cowork discovery, install, acquisition and export…” through “a Python network fallback.” |
| Source selection and consent | Step 2: “Unknown metadata, auth/access/network errors…” through “A local ZIP alone proves neither latest selection nor consent.” |
| Financial authority | Step 4: the bold source-compatibility notice and all following financial paragraphs through “financial permission.” |
| Fixed limits and safe output | Step 5: “Limits: source ZIP 32 MiB…” through “Absent requested helpers are errors.” |
| No live operations | Final paragraph: “The receiver/human must inspect…” through “provisioning or deployment.” |

At each former procedural location insert a short link to the corresponding
Guardrails anchor and apply it before that phase. Do not relocate the privacy
inspection procedure, source/sharing evidence or full foundation obligations
out of the workflow. Keep every actual financial refusal, ancestry/owner gate,
no template execution, pinned/latest/no-fallback consent and privacy/transfer
boundary. Existing financial unavailable-operation semantics remain.
The new When-not-to-use bullets distinguish explicit reviewed full ZIP,
PRD/architecture/ADRs, vague repo, live setup and both Work IQ scopes.
Add one current-version qualifier before the verbatim retained controls:
**“The retained 1.11.0 distribution/financial notices below also apply to the
finite 1.11.1 distribution; an unavailable owner helper remains unavailable.”**
Review prose against the original moved paragraphs, not a keyword-only test.
- [ ] **4.8 (2 minutes):** run the new raw/checker/parser tests:

```text
python -B -m unittest tests.unit.test_skill_maturity.SkillMaturity.test_shipped_raw_booleans_are_quoted_with_unchanged_typed_values tests.unit.test_skill_maturity.SkillMaturity.test_quoted_values_already_parse_as_native_installer_booleans tests.unit.test_skill_maturity.SkillMaturity.test_raw_quote_checker_refuses_unquoted_and_wrongly_typed_spelling -v
```

Run `python tools/check_repo.py --strict` after generated inventory refresh for
the actual 900 UTF-16-unit description and source checks. Prose uses review
and strict docs validation, not fictional routing RED/GREEN. H6 supplies real
host routing on the exact NEW ZIP.
- [ ] **4.9 (2 minutes):** focused commit:

```text
fix: quote shipped metadata and clarify Frontier routing

Refs #87. Preserve typed values and consolidate Factory controls without weakening consent.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## 8. Task 5 — source/byte gates and finite measured raster profile

**Files:** `tools/build_package.py`, `tools/check_repo.py`,
`tools/build_release.py`, `tools/demo_raster.py`,
`tests/unit/test_distribution.py`, `tests/unit/test_release_tools.py`,
new `tests/unit/test_demo_raster_1111.py`,
new `tests/fixtures/caldova-raster-1.11.1-inputs.json`;
six existing raster modules' finite-set assertions and two unnamed-version
negative controls.

- [ ] **5.1 (3 minutes):** add to existing `DistributionPrivacy`:

```python
def test_shipped_source_cache_or_twenty_first_extra_blocks_all_package_writes(self):
    for change in ("cache", "overflow"):
        with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugin"
            shutil.copytree(ROOT / "plugin", plugin)
            inventory = plugin / "install/plugin-install.json"
            before = inventory.read_bytes()
            if change == "cache":
                extra = plugin / "skills/frontier-process/__pycache__/cache.pyc"
            else:
                extra = plugin / "skills/frontier-agent-identity/references/overflow.txt"
            extra.parent.mkdir(parents=True, exist_ok=True)
            extra.write_bytes(b"not shipped")
            output = io.StringIO()
            with mock.patch.object(packager, "PLUGIN", plugin), contextlib.redirect_stdout(output):
                code = packager.main(["--dist", str(root / "dist")])
            self.assertEqual(code, 1, output.getvalue())
            self.assertIn("cache" if change == "cache" else "21 extra files", output.getvalue())
            self.assertEqual(inventory.read_bytes(), before)
            self.assertFalse((root / "dist").exists())
```

- [ ] **5.2 (2 minutes):** RED:
  `python -B -m unittest tests.unit.test_distribution.DistributionPrivacy.test_shipped_source_cache_or_twenty_first_extra_blocks_all_package_writes -v`.
  Expected existing packager silently ignores cache and allows overflow, so
  code 0 violates the required code 1. Do not remove failing source inputs.

Add this companion test to the same existing class before changing
`check_repo`'s budget gate. It probes the real checker and raw-metadata caller,
not only helper methods. It copies the existing shared ZIP helper needed by
`check_skills`, without weakening its shared-copy regression:

```python
def test_repository_shipped_quote_cache_and_budget_gates_are_wired(self):
    checker = load("tools/check_repo.py")
    for change, reason in (("quote", "quoted"), ("cache", "cache"), ("overflow", "21 extra files")):
        with self.subTest(change=change), tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugin"
            shutil.copytree(ROOT / "plugin", plugin)
            (root / "tools").mkdir()
            shutil.copyfile(ROOT / "tools/zip_stream.py", root / "tools/zip_stream.py")
            if change == "quote":
                path = plugin / "skills/frontier-process/SKILL.md"
                path.write_bytes(path.read_bytes().replace(b'optional: "true"', b"optional: true"))
            else:
                relative = ("skills/frontier-process/__pycache__/cache.pyc" if change == "cache"
                            else "skills/frontier-agent-identity/references/overflow.txt")
                path = plugin / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"unexpected")
            report = checker.Report()
            with mock.patch.multiple(checker, ROOT=root, PLUGIN=plugin, SKILLS=plugin / "skills"):
                checker.check_skills(report)
            self.assertTrue(any(reason in error for error in report.errors), report.errors)
```

RED:
`python -B -m unittest tests.unit.test_distribution.DistributionPrivacy.test_repository_shipped_quote_cache_and_budget_gates_are_wired -v`.
Expected missing cache/budget errors before 5.4; the already implemented quote
gate must still refuse its injected unquoted shipped value.
GREEN after 5.4: rerun this exact command, then the full distribution module.
- [ ] **5.3 (3 minutes):** import `skill_file_errors` from `fe_lib` in
  `build_package.py`. Immediately after its existing
  `errors.extend(maturity_errors(Path(f).name, fm))`, add:

```python
if version == "1.11.1" and f in folders:
    base = PLUGIN / f
    files = {p.relative_to(base).as_posix(): sha256_bytes(p.read_bytes())
             for p in files_under(base)}
    errors.extend(skill_file_errors(base, files, f))
```

Keep all nine-source maturity/version checks and distribution privacy checks.
The original iterator may still omit recognised cache files for legacy bytes,
but the new source gate reads the **full** tree and refuses those omitted files
before writes. FinOps is not subject to the shipped budget. Installer inventory/
entries use the existing exact file generator, not a projection/repack tool.
Recheck the serialized generated inventory through the extracted installer in
Task 6; this proves the shipped byte inventory, not just source counting.
- [ ] **5.4 (3 minutes):** add `skill_file_errors` and `tree_hashes` to
  `check_repo`'s existing `fe_lib` imports. Add this exact source-tree gate in
  the same bounded 1.11.1 shipped loop used by Task 4's raw metadata gate:

```python
try:
    files = tree_hashes(d)
except (OSError, ValueError) as exc:
    r.err("skills", f"{d.name}: {exc}")
else:
    for error in skill_file_errors(d, files, "skills/" + d.name):
        r.err("skills", error)
```

Do not check all nine source folders against the Cowork file budget. Historical
versionless shared-copy fixtures and financial source tests remain unchanged.
GREEN: rerun 5.2 and
`python -B -m unittest tests.unit.test_distribution -v`.
- [ ] **5.5 (3 minutes):** add this test to existing `ReleaseDocuments`:

```python
def test_1111_complete_bundle_uses_finite_factory_distribution_notice(self):
    bundle = load("tools/build_release.py")
    notice = bundle.skill_notice("1.11.1")
    self.assertIn("optional Preview Envisioning Agent Factory", notice)
    self.assertIn("FinOps is not included in 1.11.1", notice)
    self.assertEqual(bundle.skill_notice("1.11.0"), bundle.SKILL_NOTICE_1110)
    self.assertEqual(bundle.skill_notice("1.12.0"), bundle.LEGACY_SKILL_NOTICE)
```

RED:
`python -B -m unittest tests.unit.test_release_tools.ReleaseDocuments.test_1111_complete_bundle_uses_finite_factory_distribution_notice -v`.
Expected new helper absent; the existing `v == "1.11.0"` caller would otherwise
emit the wrong legacy FinOps distribution for 1.11.1.
Add immediately after the existing `SKILL_NOTICE_1110` definition:

```python
def skill_notice(version: str) -> str:
    notices = {
        "1.11.0": SKILL_NOTICE_1110,
        "1.11.1": SKILL_NOTICE_1110.replace("1.11.0", "1.11.1"),
    }
    return notices.get(version, LEGACY_SKILL_NOTICE)
```

Replace the `START.format` call's notice selector:

```python
(START.format(v=v, skill_notice=skill_notice(v)).encode("utf-8"), "START-HERE.md"),
```

GREEN: rerun the new test. Historical notice strings and bundle inventory,
classification and privacy tests remain intact.
- [ ] **5.6 (5 minutes):** create this complete new finite raster test:

```python
"""Only named 1.11.1 may reuse fully verified historical rasters."""
import contextlib
import hashlib
import json
import unittest

from tests.unit._util import ROOT, load
from tests.unit import test_demo_raster_1101 as fixtures


class Cowork1111Raster(unittest.TestCase):
    @contextlib.contextmanager
    def fixture(self):
        with fixtures.Patch1101Raster().fixture() as (module, helper, root, kit, profile, previous):
            record = json.loads(previous.read_bytes())
            record["version"] = "1.11.1"
            current = root / "tests/fixtures/caldova-raster-1.11.1-inputs.json"
            current.write_bytes((json.dumps(record, indent=2) + "\n").encode())
            module.COWORK_INPUT_PROFILE = current.relative_to(root).as_posix()
            module.COWORK_INPUT_PROFILE_SHA256 = hashlib.sha256(current.read_bytes()).hexdigest()
            yield module, helper, root, kit, profile, current

    def test_named_1111_replay_and_present_release_authority(self):
        with self.fixture() as (module, helper, root, kit, profile, current):
            before = {p.relative_to(kit): p.read_bytes() for p in kit.rglob("*") if p.is_file()}
            report = module.replay(kit, profile, version="1.11.1")
            self.assertTrue(report["preview"])
            self.assertEqual(report["reference_version"], "1.6.0")
            self.assertEqual(report["current_input_profile"]["sha256"],
                             hashlib.sha256(current.read_bytes()).hexdigest())
            self.assertEqual((report["verified_inputs"], report["restored"]), (3, 2))
            for path, raw in before.items():
                self.assertEqual((kit / path).read_bytes(), raw)
            final = root / "identity.zip"
            final.write_bytes(b"synthetic candidate")
            module.verify_release_identity(final, report)
            digest = hashlib.sha256(final.read_bytes()).hexdigest()
            helper.release_record(root, "1.11.1", digest)
            report = module.replay(kit, profile, version="1.11.1")
            self.assertFalse(report["preview"])
            self.assertEqual(report["expected_release_identity_sha256"], digest)
            final.write_bytes(b"changed")
            with self.assertRaisesRegex(module.RasterProfileError, "finished identity archive"):
                module.verify_release_identity(final, report)

    def test_tampered_profile_inputs_assets_and_extra_file_block_before_png_writes(self):
        for change in ("profile", "input", "asset", "extra"):
            with self.subTest(change=change), self.fixture() as (module, _, _, kit, profile, current):
                if change == "profile":
                    current.write_bytes(current.read_bytes() + b"\n")
                elif change == "input":
                    (kit / "catalog.html").write_bytes(b"changed input")
                elif change == "asset":
                    (profile / "assets/visuals/second.png").write_bytes(b"bad PNG")
                else:
                    (kit / "extra.txt").write_bytes(b"extra")
                with self.assertRaises(module.RasterProfileError):
                    module.replay(kit, profile, version="1.11.1")
                self.assertFalse((kit / "agents/sample/identity/card.png").exists())
                self.assertFalse((kit / "visuals/second.png").exists())

    def test_malformed_present_release_never_falls_back_and_future_versions_are_rejected(self):
        with self.fixture() as (module, helper, root, kit, profile, _):
            release = helper.release_record(root, "1.11.1", "0" * 64)
            release.write_bytes(b"{}")
            with self.assertRaisesRegex(module.RasterProfileError, "release record"):
                module.replay(kit, profile, version="1.11.1")
            for version in ("1.11.2", "1.12.0"):
                with self.assertRaisesRegex(module.RasterProfileError, "not approved"):
                    module.replay(kit, profile, version=version)
                with self.assertRaisesRegex(module.RasterProfileError, "no authoritative release digest"):
                    module.verify_release_identity(root / "absent.zip", {"version": version, "preview": True})

    def test_real_profile_pins_identical_measured_inputs_and_preserves_205_223(self):
        module = load("tools/demo_raster.py")
        self.assertIn("1.11.1", module.PREVIEW_VERSIONS)
        data = (ROOT / module.COWORK_INPUT_PROFILE).read_bytes()
        previous = json.loads((ROOT / module.FACTORY_INPUT_PROFILE).read_bytes())
        self.assertEqual(json.loads(data), dict(previous, version="1.11.1"))
        self.assertEqual(hashlib.sha256(data).hexdigest(), module.COWORK_INPUT_PROFILE_SHA256)
        base = json.loads((module.PROFILE / "manifest.json").read_bytes())
        self.assertEqual((len(base["inputs"]), len(base["assets"])), (205, 223))
```

- [ ] **5.7 (2 minutes):** RED:
  `python -B -m unittest tests.unit.test_demo_raster_1111.Cowork1111Raster.test_named_1111_replay_and_present_release_authority -v`.
  Expected actual `RasterProfileError: historical raster replay is not approved
  for 1.11.1`, not a guessed ZIP hash or input golden reset.
- [ ] **5.8 (3 minutes):** queue
  `python -B tools/build_demo.py --out build/cwi87-profile --no-png`.
  This **measurement-only SVG variant is not full release proof**.
  Only after successful configured output, use this one-time measurement
  command. It reads the real wrapper report's kit path, verifies every original
  non-raster input against the pinned existing profile, and creates only a
  finite new input record. It prints the **complete measured SHA assignment**
  for a manual `apply_patch`; no future digest is invented in this plan:

```text
python -B -c "import hashlib,json,sys; from pathlib import Path; sys.path.insert(0,'tools'); import demo_raster as d; old=Path(d.FACTORY_INPUT_PROFILE); assert hashlib.sha256(old.read_bytes()).hexdigest()==d.FACTORY_INPUT_PROFILE_SHA256; record=json.loads(old.read_bytes()); base=json.loads((d.PROFILE/'manifest.json').read_bytes()); report=json.loads(Path('build/cwi87-profile/build-report.json').read_bytes()); kit=Path(report['identity']['kit']); expected=dict(base['inputs'],**record['inputs']); actual={p.relative_to(kit).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in kit.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix.lower()!='.png' and p!=kit/'README.md'}; assert len(expected)==205 and len(base['assets'])==223 and actual==expected; record['version']='1.11.1'; target=Path('tests/fixtures/caldova-raster-1.11.1-inputs.json'); assert not target.exists(); data=(json.dumps(record,indent=2)+'\n').encode(); target.write_bytes(data); print('COWORK_INPUT_PROFILE_SHA256 = '+json.dumps(hashlib.sha256(data).hexdigest()))"
```

A mismatch means stop and investigate; do not expand the allowed paths, edit
old profiles/assets or overwrite a golden ZIP. The supplied equal-kit report
does not substitute for this measurement.
- [ ] **5.9 (3 minutes):** in `tools/demo_raster.py`, add only `"1.11.1"` to
  `PREVIEW_VERSIONS`; add this constant next to the Factory profile constants:

```python
COWORK_INPUT_PROFILE = "tests/fixtures/caldova-raster-1.11.1-inputs.json"
```

Paste **the entire actual assignment printed by 5.8** as
`COWORK_INPUT_PROFILE_SHA256`, with no placeholder or guessed hash.
Add only this entry to `_current_inputs`' existing finite `profiles` map:

```python
"1.11.1": (COWORK_INPUT_PROFILE, COWORK_INPUT_PROFILE_SHA256),
```

Leave SUPPORTED_VERSIONS, all older constants, exact-two-override-path checks,
205 non-raster/223 PNG checks, release authority and hash-before-write logic
unchanged. No alias permits arbitrary future versions or automatic exemptions.
- [ ] **5.10 (4 minutes):** update finite-set expectations to the following
  complete set, only in the six existing assertion sites identified by the
  source reads:

```python
{"1.6.1", "1.7.1", "1.9.1", "1.9.2", "1.10.0", "1.10.1", "1.11.0", "1.11.1"}
```

Exact files: `tests/unit/test_demo_raster.py`,
`tests/unit/test_demo_raster_17.py`, `tests/unit/test_demo_raster_19.py`,
`tests/unit/test_demo_raster_110.py`, `tests/unit/test_demo_raster_1101.py`,
`tests/unit/test_demo_raster_111.py`. Preserve historical records.
In the two explicit future-version loops make exactly these substitutions:

```diff
--- tests/unit/test_demo_raster_1101.py
+++ tests/unit/test_demo_raster_1101.py
@@
-        for version in ("1.10.2", "1.11.1", "1.9.3"):
+        for version in ("1.10.2", "1.11.2", "1.9.3"):
--- tests/unit/test_demo_raster_111.py
+++ tests/unit/test_demo_raster_111.py
@@
-        for version in ("1.11.1", "1.12.0"):
+        for version in ("1.11.2", "1.12.0"):
```

Every existing tampering/provenance/finished-ZIP assertion stays intact.
- [ ] **5.11 (2 minutes):** GREEN:

```text
python -B -m unittest tests.unit.test_demo_raster_1111 -v
python -B -m unittest tests.unit.test_demo_raster tests.unit.test_demo_raster_17 tests.unit.test_demo_raster_19 tests.unit.test_demo_raster_192 tests.unit.test_demo_raster_110 tests.unit.test_demo_raster_1101 tests.unit.test_demo_raster_111 -v
```

Expected new finite profile and retained historical regressions pass. Capture
actual failed/passed counts; do not claim frozen rasters were reconverted.
- [ ] **5.12 (2 minutes):** focused commit:

```text
fix: enforce shipped budgets and pin finite Cowork replay

Refs #87. Measure 1.11.1 inputs; preserve all historical raster and release authority.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

## 9. Task 6 — exact package, caller consistency, docs and final gates

**Files:** `tests/unit/test_factory_package.py`, `tools/selftest.py`,
new tests from Tasks 2/3; generated
`plugin/install/plugin-install.json` and
`plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html`
through existing generators only; `plugin/README.md`, `CHANGELOG.md`,
directly coupled current PRD/solution-design sections and #87 sprint links.
No old release artifacts, protected files, site/renderer source or broad #9
engineering documentation changes.

- [ ] **6.1 (5 minutes):** add this integration test to existing
  `FactoryPackage`, reusing its **actual** `build_candidate`,
  `installed_command` and isolated environment helpers:

```python
def test_exact_extracted_package_staged_contract_has_no_source_fallback(self):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        package, raw = build_candidate(root)  # Two actual builds, byte equality.
        installer = package / "install/prepare_install.py"
        old = root / "user/skills/frontier-finops/SKILL.md"
        old.parent.mkdir(parents=True)
        old.write_bytes(b'---\nname: frontier-finops\nmetadata:\n  version: "1.9.2"\n---\n')
        old_bytes = old.read_bytes()
        shadow = root / "shadow"
        shadow.mkdir()
        for name in ("fe_lib", "build_package", "factory_common"):
            (shadow / (name + ".py")).write_bytes(b"raise AssertionError('repository fallback')\n")
        args = ["--root", package, "--installed", root / "user/skills"]
        first = installed_command(installer, args, shadow)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        report = json.loads(first.stdout)
        self.assertTrue(report["package_verified"])
        self.assertFalse(report["staged_verified"])
        self.assertEqual(report["copy_calls"], [])
        self.assertEqual(len(report["skills"]), 8)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            inventory = json.loads(archive.read("install/plugin-install.json"))
            for row in inventory["skills"]:
                self.assertLessEqual(len(row["files"]) - 1, 20)
                self.assertIs(type(row["optional"]), bool)
                self.assertIs(type(row["requires_preview_ack"]), bool)
            identity = next(r for r in inventory["skills"] if r["name"] == "frontier-agent-identity")
            self.assertEqual(len(identity["files"]), 21)
        # Local test staging, not an actual Cowork save receipt.
        staged = root / "working"
        for row in report["skills"]:
            shutil.copytree(Path(row["package_source"]), staged / row["name"])
        second = installed_command(installer, [*args, "--staged-root", staged], shadow)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        verified = json.loads(second.stdout)
        self.assertTrue(verified["staged_verified"])
        self.assertEqual(len(verified["copy_calls"]), 8)
        self.assertTrue(all(r["source"] == "working/" + r["name"] for r in verified["skills"]))
        altered = staged / "frontier-agent-identity/references/identity-method.md"
        altered.write_bytes(altered.read_bytes() + b"\nchanged after verification\n")
        refused = installed_command(installer, [*args, "--staged-root", staged], shadow)
        self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
        self.assertEqual(json.loads(refused.stdout)["copy_calls"], [])
        missing = installed_command(installer, ["--root", root / "absent"], shadow)
        self.assertEqual(missing.returncode, 2, missing.stdout + missing.stderr)
        self.assertFalse(json.loads(missing.stdout)["verified"])
        self.assertEqual(old.read_bytes(), old_bytes)
        self.assertEqual(verified["installation"], "not-verified")
```

Integration regression (expected already GREEN after Tasks 1–5): run
`python -B -m unittest tests.unit.test_factory_package.FactoryPackage.test_exact_extracted_package_staged_contract_has_no_source_fallback -v`.
Record the actual result; a stale candidate/build error is not a claimed
functional RED. Rerun after 6.2–6.5. The functional path/budget/state REDs were
already isolated in Tasks 1–5. Before repairing the actual dependent callers,
run this separate exact RED command:

```text
python -B -m unittest tests.unit.test_factory_package.FactoryPackage.test_boundary_links_survive_skill_only_installation tests.unit.test_factory_package.FactoryPackage.test_exact_installed_offline_exports_installer_and_optional_core -v
```

Expected meaningful caller failures: package-only `source=None` cannot be used
as a saved draft path, and package-only copy guidance has length 0, not 8.
GREEN after 6.2: rerun this exact two-test command; both must pass without
weakening the link mutation or installed export/core assertions.
- [ ] **6.2 (4 minutes):** in
  `test_boundary_links_survive_skill_only_installation`, replace the original
  `for skill ... copytree(Path(skill["source"]), ...)` block with:

```python
self.assertEqual(plan["copy_calls"], [])
staged = root / "working"
for skill in plan["skills"]:
    shutil.copytree(Path(skill["package_source"]), staged / skill["name"])
prepared = installed_command(
    installed / "install/prepare_install.py",
    ["--root", installed, "--staged-root", staged, "--installed", root / "empty"], root,
)
self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
staged_plan = json.loads(prepared.stdout)
self.assertTrue(staged_plan["staged_verified"])
for skill in staged_plan["skills"]:
    shutil.copytree(root / skill["source"], user / skill["destination"])
```

This is a local whole-draft copy simulation for the link test, not a real
host receipt. Keep the actual legacy
`#finops-not-included-in-1110` notice/link regression and mutation intact.
Do not rename old anchors or weaken skill-only link checks.
In `test_exact_installed_offline_exports_installer_and_optional_core`, replace
the package-only `len(plan["copy_calls"]) == 8` assertion with:

```python
self.assertTrue(plan["package_verified"])
self.assertFalse(plan["staged_verified"])
self.assertEqual(plan["copy_calls"], [])
self.assertEqual(len(plan["skills"]), 8)
```

All existing Factory export, missing-owner-helper, financial ancestry/history/
legacy controls and independent core execution remain unchanged.
`test_skill_maturity.install_probe` only reads advisory status/native booleans
and absence of copy calls on error: it stays compatible with package-phase
`verified`; do not rewrite it to simulate successful installation.
The two `test_ontology.py` callers assert package `verified` only and require
**no changes**. Historical plan code examples remain historical.
- [ ] **6.3 (4 minutes):** in the existing selftest packaged-candidate block,
  insert the following after parsing the first package-only `plan`, before
  assigning `installed = plan.get("skills", [])`:

```python
check("package preflight does not claim installation",
      code == 0 and plan.get("package_verified") is True
      and plan.get("staged_verified") is False
      and plan.get("copy_calls") == []
      and plan.get("installation") == "not-verified"
      and plan.get("onedrive_sync") == "not-verified",
      out[-300:])
if code == 0:
    for row in plan["skills"]:
        shutil.copytree(Path(row["package_source"]), t / "working" / row["name"])
    code, out = run(inst, [
        "--root", str(t / "pkg"), "--staged-root", str(t / "working"),
        "--installed", str(t / "empty"),
    ])
    plan = json.loads(out) if code == 0 else {}
```

Keep the existing all-eight/native maturity/GA/Preview checks, but augment its
condition immediately after `plan.get("verified")` with:

```python
and plan.get("package_verified") is True and plan.get("staged_verified") is True
```

After that existing check, add:

```python
check("whole draft sources and exact Identity total",
      code == 0
      and all(row["source"] == "working/" + row["name"] for row in installed)
      and next((row["files"] for row in installed if row["name"] == "frontier-agent-identity"), None) == 21,
      out[-300:])
```

The existing read-only installed-empty check remains. The test's explicit
local staging is not an installer write or a claimed host save. Preserve
retained FinOps source probes, altered-package refusal, installed Factory/
core calls and all financial results; selftest seed now uses Task 3's fixture.
- [ ] **6.4 (3 minutes):** add to the new `CoworkInstall` class these
  explicit read-error and below-limit unexpected/cache package controls:

```python
def test_unreadable_installed_skill_state_is_unknown_not_success(self):
    broken = self.installed / self.names[0] / "SKILL.md"
    broken.mkdir(parents=True)  # Real invalid installed read, no permission mock.
    code, result = self.call()
    self.assertEqual(code, 0, result)
    row = result["skills"][0]
    self.assertEqual(row["status"], "unknown")
    self.assertIsNone(row["installed_equal"])
    self.assertTrue(row["installed_problems"])
    self.assertEqual(result["installation"], "not-verified")
    self.assertTrue(broken.is_dir())

def test_package_cache_and_unexpected_file_below_budget_are_not_ignored(self):
    base = self.root / "skills" / self.names[0]
    for relative in ("extra.txt", "__pycache__/extra.pyc"):
        path = base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"unexpected")
        code, result = self.call()
        self.assertEqual(code, 1, result)
        self.assertEqual(result["copy_calls"], [])
        self.assertTrue(result["problems"])
        path.unlink()
```

No receipt-shaped file is invented for Python. H3–H4 reconcile actual failed
saves, retained old versions and receipt/equality evidence.

Add this seed-behaviour regression to `CoworkIdentity`, using the existing
trusted `seed_identity.py` CLI and the snapshot's literal original brand:

```python
def test_moved_brand_fixture_preserves_complete_seed_outputs(self):
  with tempfile.TemporaryDirectory() as directory:
      root = Path(directory)
      original = root / "original-brand.json"
      original.write_bytes(bytes.fromhex(self.record["brand_hex"]))
      outputs = []
      for index, brand in enumerate((original, BRAND)):
          out = root / str(index)
          result = subprocess.run([
              sys.executable, "-B", str(IDENTITY / "scripts/seed_identity.py"),
              "--blueprint", str(ROOT / "plugin/skills/frontier-blueprint/examples/caldova-blueprint.json"),
              "--brand", str(brand), "--prefix", "cal", "--date", "2026-10-30",
              "--out-dir", str(out),
          ], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
          self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
          outputs.append(file_bytes(out))
      self.assertEqual(outputs[0], outputs[1])
      self.assertEqual(set(outputs[0]), {"agent-identity.json", "palette.json", "seed-report.md"})
```

Run
`python -B -m unittest tests.unit.test_cowork_identity.CoworkIdentity.test_moved_brand_fixture_preserves_complete_seed_outputs -v`;
expected the actual paired seed files match exactly. Snapshot/fixture byte
equality is already required; this additionally proves the actual caller input
behaviour under the same date/prefix rather than relying on the old report.
- [ ] **6.5 (3 minutes):** run existing generators, not manual edits:

```text
python tools/dev.py template
python tools/dev.py package
```

Expected template unchanged (no renderer edit); generated installer refreshed
to 1.11.1, eight native-boolean rows, Identity exactly 21 total.
The generator's printed ZIP SHA256 is measured evidence, not a prescribed
new hash. Inspect actual ZIP member inventory and reverify extracted bytes
through the integration test. Do not modify a release/golden ZIP.
- [ ] **6.6 (2 minutes):** queue focused GREEN and preserved regressions:

```text
python -B -m unittest tests.unit.test_cowork_install tests.unit.test_cowork_identity tests.unit.test_skill_maturity tests.unit.test_factory_package tests.unit.test_factory_export tests.unit.test_factory_privacy tests.unit.test_factory_finops tests.unit.test_factory_shared_zip tests.unit.test_distribution tests.unit.test_release_tools -v
python -B tools/selftest.py
python -B -m unittest tests.pipeline.test_factory_receiver -v
```

Expected all applicable focused tests pass; selftest ends `ALL PASSED`;
required actual reference receiver runs, no opt-in skip substitute.
Record real skips/errors/toolchain limitations. No old total is copied.
The configured generated-kit test command, when inspecting either actual
generated kit, is **from that kit's directory**:

```text
python -B -m unittest discover -s scripts/tests -v
```

Do not run `unittest discover` in unconfigured
`plugin/skills/frontier-agent-identity/kit`; it legitimately lacks generated
config. Task 3's test already runs the correct configured command twice.
- [ ] **6.7 (5 minutes):** update only directly coupled user/product docs.
  Prose uses review and strict document validation, not invented failing tests.
  Replace the entire current **For Copilot Cowork: how to install this plugin**
  section in `plugin/README.md` with:

```markdown
## For Copilot Cowork: how to install this plugin

The NEXT 1.11.1 package has eight shipped skills: seven GA wrappers and optional
Preview Factory. FinOps remains source-only; an older installed copy is not
automatically uninstalled. Installation grants no financial or sharing consent.

1. Keep the uploaded ZIP and extract its normal tree into a quarantined local
   package directory, for example `quarantine/frontier-plugin`. Do not execute
   downloaded repack scripts or acquired template code, rewrite skills or
   repack the ZIP. Treat package bytes as
   read-only after extraction.
2. Run `python quarantine/frontier-plugin/install/prepare_install.py --root quarantine/frontier-plugin`.
   Require exit 0 and `package_verified=true`. This is package verification,
   not installation: `copy_calls` is empty and no skill may yet be saved.
   Invalid explicit roots never fall back to another package.
3. Only with actual authorised host staging capability, copy each complete
   verified package skill into a clean whole draft `working/<name>`. No old
   files may remain. Never directly delete user configuration. If staging is
   unavailable, stop and report it; do not invent a tool or Python fallback.
4. Before any save, run `python quarantine/frontier-plugin/install/prepare_install.py --root quarantine/frontier-plugin --staged-root working`.
   Require exit 0 and both verification booleans true for all eight.
   Missing, extra, cached, wrongly named or changed staged files block every
   save. Changed drafts require a new verification. Each skill may contain
   at most 20 recursive files besides only root SKILL.md; Identity is 21 total.
5. Use the actual available authorised host save capability, one whole draft
   `working/<name>` to `skills/<same name>` per skill. The emitted CopyArtifact
   strings are guidance, not executed calls or receipts. Obtain the person's
   actual approval and keep each actual receipt. No tool means no installation.
6. Compare actual installed paths, complete inventories, versions and every
   SHA256 to verified staged/package bytes. Copied includes root SKILL.md;
   skipped is not additive. A receipt or count alone is not installed equality.
   An individual refused/failed save retains the old version: report the failure
   and pre-save version, verify retention by actual reads, or mark it unverified.
   Other successes are individual outcomes, not full installation.
7. Report full installation only with all eight successful actual receipts and
   installed equality. Record OneDrive sync separately. Only after actual sync,
   start a fresh chat and collect new package-qualified health/routing evidence.
   Python preflight always reports installation and sync as not verified.
```

Preserve product/download/classification/financial boundaries. Qualify other
*current* install paragraphs to the new staged contract and unreleased 1.11.1;
replace the old misleading package-only “not published” claim about 1.11.0
with the supplied historical publication evidence, not a fictional new lookup.
Leave old engineering result paragraphs/history source-qualified; no old hash
verifies the changed guide/new ZIP. Manual removal is person-operated only,
not part of installer tasks.
- [ ] **6.8 (4 minutes):** fill only the new unreleased changelog section:
  whole-draft preflight/truthful states, 20-extra budget/21-total Identity,
  lossless references/brand fixture, quoted logical metadata and scoped routing.
  In `docs/prd.md` append a bounded **NEXT 1.11.1 Cowork compatibility** section
  linking the approved CWI-01–07 matrix and this plan; add current qualifications
  at A.12/A.13 without editing historical tables/decisions or inventing approvals.
  In `docs/solution-design.md` append the corresponding read-only phase/CLI/
  stdout flow and B.9 verification requirements, plus current Identity
  knowledge mapping to `identity-method.md#brand-discovery`,
  `#kit-reference` and `#caldova-brand-example`. Historic knowledge inventories
  stay dated history; repair only genuine current local hyperlinks if removed
  source notes are referenced. No historical inventory/approval is rewritten.
  Record whether exact checks ran; missing host proof remains required.
  Broad engineering-doc correction/clearance is #9, not this task.
- [ ] **6.9 (2 minutes):** queue actual full candidate checks after outputs
  and directly related prose are current:

```text
python tools/dev.py package demo
python tools/dev.py docs-demo
python tools/dev.py site e2e --strict
```

`docs-demo` is the existing sanctioned generator **only if required by measured
drift**, not hand edits to demo HTML/images; review its directly generated
changes. No site/renderer source change is planned. Do not treat targeted
timeout reruns as a full L2 pass or dispatch workflows. No dependency is installed
during planning. During approved execution, restore only existing declared/pinned
dependencies after a chosen validation command actually fails for a missing
dependency, then rerun that validation. Do not add tooling or dependencies.
Exact potential tracked outputs from the inspected generator:
`docs/demo/caldova-blueprint.html`, `docs/demo/manifest.json`, and
`docs/images/caldova/overview.png`, `org-model.png`, `agents.png`,
`agent-identity.png`, `ontology.png`, `landing-zone.png`,
`architecture-layers.png`, `discovery.png`, `risks.png`, `evidence.png`.
The ten PNG names above are all within `docs/images/caldova/`; no other
generated/document files belong to this slice.
Final L1 below must verify the resulting tracked outputs and all repeat-byte
proof on the exact candidate. Automatic native PR L1/L2/IaC evidence at the
reviewed head belongs to the human/controller handoff, not a local CI claim.
- [ ] **6.10 (3 minutes):** bounded specification review then quality review:
  CWI map, source/package/staged counts/hashes, no root substitution,
  old-version/advisory versus actual receipt states, typed fields and all
  call sites, complete Identity parity and preserved financial/privacy controls.
  Return findings to the controller; do not delegate during this planning
  request or infer formal independent approval. Maintainer sign-off names the
  actual reviewed head and check receipts after they exist.
- [ ] **6.11 (2 minutes):** focused commit after actual GREEN/review:

```text
test: integrate exact Cowork package verification

Refs #87. Align callers and installer guidance; preserve full-kit and financial regressions.

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

Include only exact reviewed code/tests/generated/current-document paths.
No release/tag/push/merge or protected action is part of this commit checkpoint.

### Exact future focused-commit commands

Run each pair **at its named slice after its GREEN/review checkpoint**, not as
a batch. These are documentation of future separately approved execution;
this planning session performs no git operation. Hooks remain enabled.
Messages include the real #87 and required co-author trailer.

```text
git add -- plugin/.claude-plugin/plugin.json plugin/package/manifest.json plugin/install/plugin-install.json plugin/README.md CHANGELOG.md plugin/skills/frontier-blueprint/scripts/build_blueprint.py plugin/skills/frontier-envisioning/SKILL.md plugin/skills/frontier-context-discovery/SKILL.md plugin/skills/frontier-blueprint/SKILL.md plugin/skills/frontier-solution-design/SKILL.md plugin/skills/frontier-agent-identity/SKILL.md plugin/skills/frontier-value-case/SKILL.md plugin/skills/frontier-process/SKILL.md plugin/skills/frontier-agent-factory/SKILL.md plugin/skills/frontier-finops/SKILL.md plugin/install/prepare_install.py tests/unit/test_skill_maturity.py tests/unit/test_factory_package.py tests/unit/test_factory_export.py tests/unit/test_factory_privacy.py
git commit -m "chore: prepare finite 1.11.1 inventory" -m "Refs #87. Bump before compatibility plugin edits; retain historical policies." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git add -- plugin/install/prepare_install.py tools/fe_lib.py tests/unit/test_cowork_install.py
git commit -m "fix: verify Cowork whole drafts before save guidance" -m "Refs #87. Read-only preflight; exact inventories, hashes and truthful phase state." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git add -- plugin/skills/frontier-agent-identity/references/identity-method.md plugin/skills/frontier-agent-identity/references/brand-discovery.md plugin/skills/frontier-agent-identity/references/kit-reference.md plugin/skills/frontier-agent-identity/examples/caldova-brand.json plugin/skills/frontier-agent-identity/SKILL.md tests/fixtures/caldova-brand.json tests/fixtures/cowork-identity-originals.json tests/unit/test_cowork_identity.py tools/selftest.py
git commit -m "refactor: consolidate Identity references losslessly" -m "Refs #87. Keep kit scripts and demo bytes; retain exact brand fixture and seed input." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git add -- plugin/skills/frontier-envisioning/SKILL.md plugin/skills/frontier-context-discovery/SKILL.md plugin/skills/frontier-blueprint/SKILL.md plugin/skills/frontier-solution-design/SKILL.md plugin/skills/frontier-agent-identity/SKILL.md plugin/skills/frontier-value-case/SKILL.md plugin/skills/frontier-process/SKILL.md plugin/skills/frontier-agent-factory/SKILL.md tools/fe_lib.py tools/check_repo.py tests/unit/test_skill_maturity.py
git commit -m "fix: quote shipped metadata and clarify Frontier routing" -m "Refs #87. Preserve typed values and consolidate Factory controls without weakening consent." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git add -- tools/build_package.py tools/check_repo.py tools/build_release.py tools/demo_raster.py tests/unit/test_distribution.py tests/unit/test_release_tools.py tests/unit/test_demo_raster.py tests/unit/test_demo_raster_17.py tests/unit/test_demo_raster_19.py tests/unit/test_demo_raster_110.py tests/unit/test_demo_raster_1101.py tests/unit/test_demo_raster_111.py tests/unit/test_demo_raster_1111.py tests/fixtures/caldova-raster-1.11.1-inputs.json
git commit -m "fix: enforce shipped budgets and pin finite Cowork replay" -m "Refs #87. Measure 1.11.1 inputs; preserve all historical raster and release authority." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

git add -- tests/unit/test_factory_package.py tests/unit/test_cowork_install.py tests/unit/test_cowork_identity.py tools/selftest.py plugin/install/plugin-install.json plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html plugin/README.md CHANGELOG.md docs/prd.md docs/solution-design.md
git commit -m "test: integrate exact Cowork package verification" -m "Refs #87. Align callers and installer guidance; preserve full-kit and financial regressions." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

If the sanctioned docs-demo generator produced reviewed changes, stage its
exact tracked paths before the last commit, not an entire directory:

```text
git add -- docs/demo/caldova-blueprint.html docs/demo/manifest.json docs/images/caldova/overview.png docs/images/caldova/org-model.png docs/images/caldova/agents.png docs/images/caldova/agent-identity.png docs/images/caldova/ontology.png docs/images/caldova/landing-zone.png docs/images/caldova/architecture-layers.png docs/images/caldova/discovery.png docs/images/caldova/risks.png docs/images/caldova/evidence.png
```

## 10. Person-operated host acceptance and publication handoff

These are **not agent execution tasks**. No invented host API, receipt,
acknowledgement, OneDrive result, structural score or publication is acceptable.
The package/source identity, actual command/result and actual evidence link
must be recorded when they exist; an unavailable operation stays outstanding.

- [ ] **H1 — exact candidate identity:** obtain the actual freshly built
  1.11.1 ZIP and measured SHA256/bytes/member inventory from Task 6, not the
  published old ZIP or reported repack. Verify all eight names, seven GA/
  optional Preview Factory and no FinOps shipped bytes. Keep the extracted
  normal package quarantined/read-only. Record host version and actual date.
- [ ] **H2 — staging and global preflight:** run package preflight; use only
  actually available authorised host capability to create clean
  `working/<name>` whole drafts. Run read-only full staged inventory/hash
  verification before **any** save. Demonstrate nested/wrong path and file
  limit refusals without writes. Identity must be exactly 21 total files.
  Missing staging capability blocks acceptance; never run a downloaded repacker.
- [ ] **H3 — actual saves and failed-save retention:** for each of eight
  skills, record actual approval/save receipt, source `working/<name>`,
  destination `skills/<same name>`, total copied and host skipped.
  Copied already includes every file; skipped is not additive. If a save is
  refused/fails, record the failure and observed pre-save version; verify
  retained old version/inventory where possible. Otherwise mark current
  installed state unverified. No direct deletion or automatic old FinOps uninstall.
  Do not deliberately damage a user's installed skill to manufacture a failure.
- [ ] **H4 — actual installed equality and sync:** reconcile each receipt
  against actual installed full inventory, version and hashes. Record individual
  successes separately. **Only** all-eight actual successful receipts **and**
  installed equality permit full installation; preflight equality alone does
  not. Record actual OneDrive sync separately. Missing receipt/reads/equality/
  sync remains outstanding, never a success-shaped fallback.
- [ ] **H5 — fresh health and structural rescore:** fresh chat after actual
  sync, exact NEW ZIP identity, all eight raw metadata/structure/description/
  security/package checks, actual publish-bar/structural rescore.
  Preserve advisory warnings and unavailable checks. The supplied repack had
  no structural rescore; it supplies no pass here.
- [ ] **H6 — actual host routing matrix:** retain each real prompt, selected
  skill/clarification, result and evidence for the following bounded matrix.
  Description grep, a mock classifier and local tests are not host routing proof.

| Real prompt using fictitious Caldova | Required observed route |
|---|---|
| Prepare a full starter-repository ZIP from these reviewed Caldova MVP artifacts and this pinned compatible template. | Factory; apply existing source/sharing/financial gates |
| Write the Caldova MVP PRD, target architecture and ADRs. | Solution Design; no automatic Factory |
| Set up a repo for Caldova. | Clarify documents versus offline full ZIP; no live setup |
| Create a live remote repository and deploy the Caldova agents. | Outside offline Factory; no fabricated live operations |
| Gather Work IQ evidence for the Caldova Frontier engagement workshop. | Context Discovery, scoped evidence/privacy |
| Use Work IQ to analyse organisation-wide activity; this is not a Frontier engagement. | Not keyword-captured by Frontier Context Discovery |
| Build the Caldova ordinary value case; then define process data products. | Preserve Value Case/Process division; no FinOps invocation |

- [ ] **H7 — separate human tracks:** link genuine new results through #87/
  #81/#86; #81 remains open until actual final acceptance. The maintainer reviews
  the exact head and native automatic PR checks and records head-qualified
  sign-off, distinct from zero formal approving reviews. Publication/clearance
  and any release/tag workflow are separate human decisions after all applicable
  gates. #8 protection is prerequisite, not an agent mutation. #9 broad doc/
  publication clearance remains separate. A genuinely compatible stable template
  release/tag requires human verification/publication; no nominal GA/stable
  workaround for exact-commit bootstrap consent. Factory remains Preview.
  No #48/#58 activation or Caldova tenant/governance changes.

### Handoff receipt shape (person records actual values)

Use one row per skill: package ZIP identity; package/staged preflight result;
actual source/destination; observed old version; actual save disposition and
receipt link; copied total/skipped; actual installed version/full-inventory/hash
comparison; retained-old-version evidence on failure or explicit unverified
state. Keep separate rows for actual sync, fresh-chat health/structural scores,
host routing, reviewed head/native L1/L2/IaC/sign-off and later publication.
Empty/missing evidence is **outstanding**, not approval or success.
Do not populate any row from synthetic unit-test receipts.

## 11. Planning-session validation and final implementation gate

This writer used read/edit/search tools only. No terminal tool is exposed, so
`python tools\dev.py docs --strict` and `git diff --check` **could not be run**
in this session. That is inability, not a failed or passed automated check.
The earlier sprint's parent-reported b9647ea document pass remains historical
and does not validate these new plan/link changes. Manual review checks current
relative links, six-field metadata, code/field/caller consistency and scope;
the parent must run actual post-edit document validation before publication.
No code/test/build, bump, dependency installation, git/GitHub or host operation
was executed here.

### Parent planning checks and self-review

On 27 November the parent ran `python tools/dev.py docs --strict`: **0 errors;
documentation-only ALL GATES PASSED** (7.8 seconds). `git diff --check` passed.
Thirty complete Python fences parsed without execution; the two explicit map/
condition insertion fragments were reviewed in their documented contexts.
The three proposed descriptions measured 610, 722 and 590 UTF-16 units against
the 900-unit limit.

The parent self-review mapped every CWI requirement to the tasks above and
corrected shared-workspace handling: unrelated working siblings and a package
under `working/install1110/pkg` are preserved; overlap is rejected only against
selected skill drafts. It also removed an old-version loophole in the current
host budget, retained the allowed missing-dependency restoration workflow and
reconciled written-spec approval/plan status. The checker was not weakened.
These are planning-document/syntax checks, not executed implementation tests,
package/host acceptance or effective protected controls.

After approved implementation, record actual outcomes for these final commands
in order. Missing strict tooling, evidence or protection remains blocking;
never turn offline `not-performed` release verification into a full L1 pass.
Fresh online release evidence is required in CI; human/controller must provide
that permitted environment, not expose credentials to the plugin.

```text
git diff --check
python tools/dev.py docs --strict
python tools/dev.py check --strict
```

Expected only after actual successful execution: no whitespace errors,
zero strict document errors, and full L1 `ALL GATES PASSED` with applicable
strict tooling/fresh exact-version evidence. Preserve actual REDs, advisory
warnings, genuine skips and unavailable host checks in the handoff.
