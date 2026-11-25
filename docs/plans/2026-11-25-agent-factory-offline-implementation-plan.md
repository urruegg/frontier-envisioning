# Agent Factory 1.11.0: combined offline production implementation plan

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-25 |
| Author | AI assistant; AI-assisted implementation planning |
| Status | Written for one human W1–W4 plan/readiness approval; not implementation authority or completed verification |
| Scope | Complete optional Preview offline Agent Factory producer, registration and verification for 1.11.0; actual Cowork validation deferred |
| References | [Catalogue](README.md), [#72](https://github.com/urruegg/frontier-envisioning/issues/72), [W0 #73](https://github.com/urruegg/frontier-envisioning/issues/73), [Idea](../ideas/2026-11-25-agent-factory-handover.md), [Approved design](../specs/2026-11-25-agent-factory-handover-design.md), [W0 plan](2026-11-25-agent-factory-handover-plan.md), [SPRINT-013](../sprints/SPRINT-013-agent-factory-handover.md), [AGENTS](../../AGENTS.md), [Requirements](../prd.md), [Architecture and verification](../solution-design.md), [Engineering rationale](../adr/README.md) |

> **For agentic workers:** subagent-driven development was explicitly selected.
> After actual approval of this complete document and recorded readiness, the
> controller creates each real bounded child issue before its fresh worker.
> Use `frontier-builder` for code/checkers and eligible `docs-agent` work for
> prose where supported, with existing tools/models only. Use the AGENTS method
> when Superpowers is unavailable. This planning session dispatches nobody.
> One actual approval can cover all the written W1–W4 tasks below. Sequential
> task completion and technical reviews are not repeated human approval gates.

**Goal:** ship Envisioning Agent Factory as the ninth, optional Preview skill
in the existing 1.11.0 plugin. Produce a complete, deterministic, reviewable
factory repository ZIP from genuinely acquired, frozen source and selected,
transfer-approved ordinary files.

**Architecture:** host acquisition is outside the plugin. A frozen receipt
binds a complete stable-release lookup, exact immutable source and archive
bytes. The installed offline producer checks that receipt, preserves the
whole compatible foundation, validates and copies reviewed intake bytes, and
atomically publishes one ZIP. Producer metadata stays outside the strict
upstream intake record. The original source, baseline, export validation,
receiver validation, financial readiness and tenant authority are distinct.
Neither template code nor imported documents are executed.

**Tech stack:** Python 3.11+ standard library in the plugin; `unittest` and
existing repository gates; existing package/installer machinery. Developer
receiver integration uses the retained Python 3.14.10 environment with pinned
`jsonschema==4.25.1`. No plugin dependency or runtime SDK is added.

## 1. Authority, evidence and readiness

Accountable owner: `@urruegg`. Main baseline is
`14f2c48b4a59737af86785d8982b3c409f8c0ec4`; planning branch is
`docs/72-agent-factory-design`, parent committed head
`f4b2609f9cdc1c24b7e31fad0b08d55f11162453` when intake began. The parent
subsequently committed/pushed activation and reviewed W0 evidence as
`86a35b3eda0771faca3bc5975c2e96464446844c` (eight parent-owned Markdown
files; parent reports strict docs zero errors and whitespace PASS).
That report is not a validation run by this planning worker. Do not reset,
stage, overwrite or revert parent changes.
The parent owns catalogue integration, the existing idea/spec/W0 plan/sprint,
and their actual evidence updates. This planning delivery owns this new file
only. Implementation ownership below applies only after approval and dispatch.

Actual written approvals, not inferred permissions:

1. Spec `7f650c4`: [7164505078](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7164505078).
2. W0 plan/sprint `c8cc5bb`: [7165080818](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7165080818);
   real child #73 is assigned to the accountable owner.
3. Written section 11 at `f4b2609`: [7166316613](https://github.com/urruegg/frontier-envisioning/issues/72#issuecomment-7166316613),
   `approve-offline-preview-defer-cowork-validation`, no change. The working
   spec 0.4 activates that decision. This is not new product scope.

The real #72/#73 bodies and #72 amendment receipt were read during planning.
Their older early-Cowork wording is historical and qualified by the later
actual amendment, not silently deleted. `type:decision` does not mean that
the recorded decisions remain unanswered; nor does a decision prove that
protected labels changed. Do not set `status:ready` or `approved:*`.

### W0 facts to retain, not rerun by assertion

- Genuine public MIT reference:
  `urruegg/frontier-agent-factory@0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d`.
  At observation, healthy complete releases and tags enumerations were empty.
  That is dated evidence, not perpetual absence or permission for another export.
- Complete source: 149 ordinary `100644` blobs, 726,850 bytes, no links or
  submodules. Preserve all foundation bytes, workflows, policies, locks and
  licences. In particular retain `LICENSE`,
  `.agents/skills/LICENSE.superpowers`, `.agents/superpowers.lock.json`.
- Schema: 8,381 bytes, SHA256
  `04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f`.
  Receiver `tools/intake.py`: 15,736 bytes, SHA256
  `4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370`.
- Actual receiver suite: 31 run, 30 passed, one Windows symlink privilege
  1314 skip, zero errors/failures. All three original-source fixture checks
  and accepted baseline-only validation exited zero. Synthetic approvals
  authenticate nobody. Node 26.13.1 is not the required Node 24 LTS profile;
  no full receiver toolchain certification exists.
- Originals and baseline reads share **one** 64 MiB receiver budget; each
  file is at most 16 MiB and intake JSON at most 1 MiB.
- Cowork discovery, install, acquisition and export: **not performed**.
  The offline amendment does not waive protected/manual release review.

### Definition of Ready check before the first implementation worker

The controller records the actual approval of this complete written plan,
links it from #72 and SPRINT-013, confirms the activated spec and reviewed #73
evidence, and provides each real child with owner, scope, exact files,
dependencies and AF acceptance. A person handles any required ready/approval
labels; check their actual state separately. The parent adds the new direct-child
catalogue entry. An otherwise isolated uncatalogued-plan documentation error
is that integration dependency, not a product-design blocker.

No unresolved product choice was found in the supplied, approved boundary.
If source/schema drift or a new substantive design ambiguity changes it,
return **NEEDS_CONTEXT** with the concrete discrepancy and question; do not
insert a string standing in for an answer. Missing tools/evidence remain real
verification failures, not fabricated passes. Timebox additional exploration
to 15 minutes per newly failing interface; stop when facts no longer change
the design.

### Approaches considered

An overlay loses the promised receiving foundation. A network-enabled exporter
couples host authentication to offline packaging and violates the runtime
boundary. Use the approved third approach: host-acquired immutable source plus
an offline full-foundation producer. Its trade-off is an explicit acquisition
receipt and separate actual receiver proof. There is no new choice for the
person to make here.

## 2. Interfaces, ownership and dependency order

All paths below are repository-relative unless a developer evidence path is
explicitly absolute. New plugin paths are beneath
`plugin/skills/frontier-agent-factory/` (abbreviated **F** in file tables,
never in executable commands).

| Work/commit scope | Exact owned files after dispatch | Depends on |
|---|---|---|
| Baseline and version | `plugin/.claude-plugin/plugin.json`, `plugin/package/manifest.json`, existing eight `SKILL.md` version carriers, `plugin/skills/frontier-blueprint/scripts/build_blueprint.py` version constant, `plugin/README.md`, `CHANGELOG.md`; sanctioned `tools/demo_raster.py`, new `tests/fixtures/caldova-raster-1.11.0-inputs.json`, new `tests/unit/test_demo_raster_111.py`, current raster assertion in `tests/unit/test_demo_raster_1101.py` | Actual plan/readiness; clean implementation worktree; exact current-version proof |
| W1 source/intake | F `scripts/factory_common.py`, `scripts/factory_contract.py`, `references/intake.schema.json`, `references/template-profile.json`, `references/handover-contract.md`, `examples/caldova-handover.json`; `tests/factory_fixture.py`, `tests/fixtures/factory/intake-reference.py.txt`, `tests/fixtures/factory/LICENSE.template.MIT`, `tests/unit/test_factory_contract.py` | Baseline/bump |
| W2 archive | `tools/zip_stream.py`, identical F `scripts/zip_stream.py`; wrapper-only `tools/release_evidence.py`; shared-copy assertion `tools/check_repo.py`; F `scripts/factory_archive.py`; `tests/unit/test_factory_archive.py`, `tests/unit/test_factory_shared_zip.py` | W1 |
| W3 projection/CLI | F `scripts/factory_projection.py`, `scripts/export_factory.py`; `tests/unit/test_factory_export.py`, `tests/unit/test_factory_privacy.py`, `tests/unit/test_factory_finops.py` | W1, W2 |
| W4 integration | F `SKILL.md`; current routing references in `plugin/skills/frontier-envisioning/SKILL.md`, `plugin/skills/frontier-solution-design/SKILL.md`; `tools/fe_lib.py`, `plugin/install/prepare_install.py`, `tools/selftest.py`, `tests/unit/test_skill_maturity.py`, current inventory test in `tests/unit/test_docs_contract.py`, `tests/unit/test_factory_package.py`, `tests/pipeline/test_factory_receiver.py`; current `README.md`, `AGENTS.md`, `plugin/README.md`, `plugin/skills/frontier-finops/SKILL.md`; `docs/prd.md`, `docs/solution-design.md`, new `docs/adr/0032-offline-agent-factory-handover.md`, `docs/adr/README.md`, `CHANGELOG.md`; generated `plugin/install/plugin-install.json` | W3 reviewed, then candidate/package/receiver gates |

The controller creates real bounded child issues for these scopes after plan
approval and before each fresh worker; no child number is invented here.
Split W4 code/checker and eligible prose ownership if the harness supports it.
Do not let workers concurrently edit a shared manifest or the parent records.
Review specification first, then correctness, for each returned scope.

Use conventional bounded commits during approved execution only: version/profile,
W1 contract, W2 archive/shared extraction, W3 exporter, W4 integration, W4 prose.
Each commit body links its actual child and #72. Stage explicit owned paths,
never `git add .`; no automatic merge, tag, release or workflow dispatch.
New Python files retain the repository's MIT copyright/SPDX header convention;
the extracted ZIP algorithm and copied upstream data retain their attribution.
Code blocks are logical file contents/complete functions, not licence removal.

### Public producer interface

```powershell
python plugin\skills\frontier-agent-factory\scripts\export_factory.py --request request.json --template template.zip --source-root originals --baseline-root approved --out Caldova-factory.zip
```

Optional `--acknowledge-finops-preview` applies only to actually requested
financial content for the current invocation. There is no networking,
auto-acquire, execute-template, skip-validation, force-accept, drop-file,
unsafe-path or arbitrary-profile CLI switch.

`main(argv=None) -> int`: zero only after atomic publication; one for bounded
input/compatibility/privacy/I/O failure; two for usage error. Success is one
UTF-8 JSON object on stdout, including final ZIP SHA256. Errors contain fixed
codes and equivalent-format guidance, never supplied filenames, private
terms, OS exception strings or selected-source counts. Generated text is
UTF-8/LF. Caller input files are read-only.

`request.json` is producer schema `frontier-agent-factory-request/1.0`.
It has exactly these fields:

| Field | Contract |
|---|---|
| `schema`, `export_id`, `created_at`, `customer_scope` | Exact schema; receiver-compatible export ID; explicit RFC3339 fixed time in ZIP's 1980–2107 range; nonblank, explicitly reviewed customer/domain scope |
| `evidence_kind` | `externally-recorded` or `synthetic-compatibility`; the latter is visibly synthetic throughout, never actual review/authentication |
| `template` | Receipt described below; all acquisition data is real for a handover, explicitly synthetic only in isolated tests |
| `intake` | Upstream intake 1.0 fields, with `source.sha256` and `baseline.sha256` **absent** on provided rows; producer calculates them automatically. No other upstream extension |
| `blueprint` | `{source_path, baseline_path}` identifying the original normalized blueprint and approved customer-safe normalized JSON; the latter is a provided `blueprint` artefact |
| `id_map` | Exactly `solutions`, `agents`, `requirements`: objects mapping preserved original IDs to unique factory IDs; source documents retain original IDs/bytes |
| `selection_evidence` | One `{solution_id, original_solution_id, original_agent_ids, rationale, dependency_gaps}` per selected solution. Explicit mapping, not keyword/MVP inference. Gap IDs refer to declared gaps/decisions |
| `sharing_review` | `{customer_scope, metadata, artifacts}`; matching scope, actual approval evidence for all exported metadata and each provided artefact, keyed by `<intake-id>:<artifact-id>`; includes history, paths, references, filenames and opaque sharing review |
| `history` | Explicit list of prior accepted intake IDs supplied under baseline root; at most 127. Preserve their records/files byte-for-byte, validate them, never edit an old accepted record |
| `financial` | `{requested, as_of, claim, packets}`. Default `false, null, "review", []`. Packet contract in Task 9. `claim` is `review` or explicit `build-handover`, not inferred from accepted intake |

Template receipt fields are exactly `repository`, `selection`, `commit`,
`release`, `discovery`, `bootstrap_approval`, `acquisition`, `root_prefix`.
Repository is `urruegg/frontier-agent-factory`; commit is 40 lowercase hex.
`selection` is `stable-release` or `unreleased-bootstrap`.
`release` is null or `{id, tag, commit, published_at}`.
Discovery is `{status, complete, export_id, observed_at, evidence, releases}`.
`releases` retains exactly the minimal projection of actual `id`, `tag_name`,
`published_at`, `draft`, `prerelease` values for **every** enumerated release;
extra keys are rejected. Complete enumeration means complete actual pagination,
not serialising complete GitHub API objects. Keep the whole live response
outside producer inputs/export; never copy release bodies, author profiles,
assets, protected URLs or other unnecessary API fields into request/sidecar
or launder them through `evidence`.
Draft/prerelease rows may retain actual null tag/publication fields and need
no resolved Git object. Every non-draft, non-prerelease candidate must have a
valid RFC3339 publication time and usable tag metadata before ordering.
Null/malformed time or missing/unusable tag is **unknown discovery**, never
healthy absence or permission to choose an older stable release.
Latest means the most recently published valid stable candidate;
ambiguous tied identities fail. Only that selected release must have its
actual tag resolved to the exact commit in `release.commit` and the matching
top-level `commit`. Its `release.tag` equals the selected `tag_name`.
Do not resolve historical/ignored tags, manufacture commits/times for drafts,
or confuse an ignored old-tag failure with selected-source acquisition failure.
Acquisition is `{status, method, by, at, evidence, archive_sha256}`, with
`authorised-host` or `explicit-local-source` method. The host computes hashes
automatically. `root_prefix` is the exact archive wrapper directory or empty;
never blindly strip ancestry. A local file is not proof of latest source.

New handovers require a new successful complete discovery receipt bound to
that export ID. Reproduction reuses the same frozen receipt/bytes; it does not
pretend a fresh lookup. Healthy no-stable-release permits only actual explicit
bootstrap approval `{by, at, reference}` of the exact commit. Access, auth,
network, incomplete lookup and incompatible latest source always fail.
Checksums/receipts prove consistency, not signatures or authenticated approval.

Producer output schema is `frontier-agent-factory-handover/1.0`, in
`handover/manifest.json`. Blueprint schema remains unchanged. The plugin
version **must** become 1.11.0 before the first approved plugin edit.

## 3. Task 1 — baseline, then bump, then finite raster profile

Each numbered substep is a separate short action; preserve actual output.
Commands in this plan are future execution instructions, not previously run
production tests.

1. In the approved implementation worktree inspect `git status --short`,
   `git rev-parse HEAD`, current manifest version and actual linked approvals.
   Record the starting head/version and path ownership. Do not assume the
   planning worktree's unrelated changes are yours.
2. Run current-version focused/full baseline **before bumping**:

   ```powershell
   python -m unittest tests.unit.test_release_evidence tests.unit.test_demo_raster_1101 -v
   if ($LASTEXITCODE -ne 0) { throw 'Current-version focused baseline failed' }
   python tools\dev.py package demo
   if ($LASTEXITCODE -ne 0) { throw 'Current-version artefact build failed' }
   python tools\verify_release.py --online
   if ($LASTEXITCODE -ne 0) { throw 'Exact current-version evidence failed' }
   python tools\dev.py check --strict
   if ($LASTEXITCODE -ne 0) { throw 'Current-version strict baseline failed' }
   ```

   Record `verified`, authoritative `development`, or `not-performed` exactly.
   Local cache absence is not confirmed development or a reproduction pass.
   A failed current-version comparison/access check is not bypassed by bumping.
   Use matching historical source/outputs for a published 1.10.0 comparison;
   never compare current 1.10.1 outputs with 1.10.0 using `--force`.
   This is bounded baseline verification, not renewed release monitoring.
   Baseline generators must leave tracked files unchanged. If a stale generated
   inventory is reported/written, stop and report that baseline drift; do not
   commit it as this feature or bump merely to escape it.
   A standalone online probe does not make the later offline whole-check
   authoritative. Before bumping, open a fresh validation-only PowerShell at
   that implementation worktree root and run the actual online full baseline:

   ```powershell
   $env:CI = 'true'
   python tools\dev.py check --strict
   if ($LASTEXITCODE -ne 0) { throw 'Authoritative online full baseline failed' }
   ```

   Require its actual `ALL GATES PASSED` summary. Existing normal `gh`
   read-only authentication is used; do not read/print tokens, switch
   credentials, dispatch a workflow or change settings. Close that shell after
   the validation so its process-local CI flag does not affect other work.
3. Run `python tools\dev.py bump 1.11.0` as the **first plugin edit**. Do not
   pass `--date`: this is unreleased development, not publication.
   Inspect only its listed version carriers and replace the new empty changelog
   bullet with the factual candidate summary. Do not edit historical sections.
4. RED: add `tests/unit/test_demo_raster_111.py` using the executable class
   below. Run
   `python -m unittest tests.unit.test_demo_raster_111 -v`; named support must
   fail on the current finite allowlist. An unexpected pass needs explanation.

   ```python
   import contextlib
   import hashlib
   import json
   import unittest
   from tests.unit._util import ROOT, load
   from tests.unit.test_demo_raster_1101 import Patch1101Raster

   class Factory111Raster(Patch1101Raster):
       @contextlib.contextmanager
       def factory_fixture(self):
           with self.fixture() as (m, fixtures, root, kit, profile, previous):
               record = json.loads(previous.read_bytes())
               record["version"] = "1.11.0"
               current = root / "tests/fixtures/caldova-raster-1.11.0-inputs.json"
               current.write_bytes((json.dumps(record, indent=2) + "\n").encode())
               m.FACTORY_INPUT_PROFILE = current.relative_to(root).as_posix()
               m.FACTORY_INPUT_PROFILE_SHA256 = hashlib.sha256(current.read_bytes()).hexdigest()
               yield m, fixtures, root, kit, profile, current

       def test_only_named_patch_is_added_with_identical_pinned_inputs(self):
           m = load("tools/demo_raster.py")
           self.assertEqual(m.SUPPORTED_VERSIONS, {"1.4.0", "1.5.0", "1.6.0"})
           self.assertEqual(m.PREVIEW_VERSIONS,
                            {"1.6.1", "1.7.1", "1.9.1", "1.9.2",
                             "1.10.0", "1.10.1", "1.11.0"})
           data = (ROOT / m.FACTORY_INPUT_PROFILE).read_bytes()
           previous = json.loads((ROOT / m.PATCH_INPUT_PROFILE).read_bytes())
           self.assertEqual(json.loads(data), dict(previous, version="1.11.0"))
           self.assertNotIn(b"\r", data)
           self.assertEqual(hashlib.sha256(data).hexdigest(),
                            m.FACTORY_INPUT_PROFILE_SHA256)
           base = json.loads((m.PROFILE / "manifest.json").read_bytes())
           self.assertEqual((len(base["inputs"]), len(base["assets"])), (205, 223))

       def test_factory_replay_uses_the_named_profile(self):
           with self.factory_fixture() as (m, _, root, kit, profile, current):
               report = m.replay(kit, profile, version="1.11.0")
               self.assertEqual(report["reference_version"], "1.6.0")
               self.assertTrue(report["preview"])
               self.assertIsNone(report["expected_release_identity_sha256"])
               self.assertEqual(report["current_input_profile"]["version"], "1.11.0")

       def test_factory_tampering_is_refused_before_any_raster_write(self):
           for change in ("record", "schema", "version", "base", "input", "asset", "extra"):
               with self.subTest(change=change), self.factory_fixture() as (m, _, _, kit, profile, current):
                   if change == "record":
                       current.write_bytes(current.read_bytes() + b"\n")
                   elif change in {"schema", "version"}:
                       data = json.loads(current.read_bytes())
                       data[change] = "unsupported"
                       current.write_bytes((json.dumps(data) + "\n").encode())
                       m.FACTORY_INPUT_PROFILE_SHA256 = hashlib.sha256(current.read_bytes()).hexdigest()
                   elif change == "base":
                       manifest = profile / "manifest.json"
                       manifest.write_bytes(manifest.read_bytes() + b"\n")
                   elif change == "input":
                       (kit / "catalog.html").write_bytes(b"unexpected change")
                   elif change == "asset":
                       (profile / "assets/visuals/second.png").write_bytes(b"corrupt")
                   else:
                       (kit / "unexpected.json").write_bytes(b"{}")
                   with self.assertRaises(m.RasterProfileError):
                       m.replay(kit, profile, version="1.11.0")
                   self.assertFalse((kit / "agents/sample/identity/card.png").exists())
                   self.assertFalse((kit / "visuals/second.png").exists())

       def test_factory_present_record_controls_finished_zip(self):
           with self.factory_fixture() as (m, fixtures, root, kit, profile, _):
               final = root / "identity.zip"
               final.write_bytes(b"rebuilt synthetic identity")
               fixtures.release_record(root, "1.11.0", hashlib.sha256(final.read_bytes()).hexdigest())
               report = m.replay(kit, profile, version="1.11.0")
               self.assertFalse(report["preview"])
               m.verify_release_identity(final, report)
               final.write_bytes(b"tampered")
               with self.assertRaises(m.RasterProfileError):
                   m.verify_release_identity(final, report)
   ```

5. GREEN: add only `"1.11.0"` to `PREVIEW_VERSIONS`; add
   `FACTORY_INPUT_PROFILE = "tests/fixtures/caldova-raster-1.11.0-inputs.json"`.
   Add that exact version to `_current_inputs`' `profiles` map. New profile is
   the unchanged 1.10.1 profile with only `"version": "1.11.0"` changed, UTF-8/LF,
   two-space indentation and final LF. Its complete content is:

   ```json
   {
     "schema": "frontier-demo-current-inputs/1.0",
     "version": "1.11.0",
     "base_profile_sha256": "46d37eef1a55f8655c4d09447b6335e39ec3b356621186339404c813ecfa5d15",
     "inputs": {
       "catalog.html": "5eb2902c5ec2e03c3c2d33a883a375347afd3913e89527fb4c22723d9672d63c",
       "scripts/identity_docs.py": "0add18be32170798c79f2b982c9073bb21ae4b4e1a38562a9cd5d576d62ae959"
     }
   }
   ```

   Compute its actual digest once with
   `python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('tests/fixtures/caldova-raster-1.11.0-inputs.json').read_bytes()).hexdigest())"`
   and pin that actual value as `FACTORY_INPUT_PROFILE_SHA256`. This is a
   developer profile pin, not a recurring user digest ceremony. Add only the
   corresponding finite map entry; no broad future-version match.
6. Preserve the existing 1.10.1 profile/replay/ZIP-authority tests. Update only
   its *current allowlist assertion* to include 1.11.0 and move `"1.11.0"` in
   its unsupported-version loop to `"1.11.1"`. Extend the new subclass with
   the same existing tamper and present-release cases parameterised for
   `"1.11.0"`; the new methods above use its `FACTORY_*` constants, not
   `PATCH_*`. Also cover a malformed present record and unnamed 1.11.1/1.12.0
   with those same existing assertions. Do not replace
   old tests with tests only for the new version.
7. Run all `test_demo_raster*.py`, then `python tools\dev.py package demo`.
   Expected: all 205 non-raster inputs still match, 223 pinned PNGs restored,
   new unreleased identity output rebuilt, not a copied golden ZIP. A changed
   input stops this task; no historical hashes/fixtures or release records
   may be relaxed. Commit only the named version/profile scope after GREEN.

## 4. Task 2 — W1 strict data, safe local reads and fixed schema subset

Create the new skill directory only after Task 1. Copy the exact pinned
`docs/intake/intake.schema.json` to F `references/intake.schema.json` as
reviewed **data**. Copy exact pinned `tools/intake.py` to
`tests/fixtures/factory/intake-reference.py.txt`, never to executable plugin
code. Retain the upstream MIT notice in
`tests/fixtures/factory/LICENSE.template.MIT` and record that schema attribution
in `references/handover-contract.md`. Because the copied schema ships in the
plugin, `references/handover-contract.md` must ALSO retain the exact upstream
copyright/permission/disclaimer notice for that copied packaged schema, not
just a source link. Keep `tests/fixtures/factory/LICENSE.template.MIT` for the
vendored test-text copy; no new file or protected root/plugin licence edit
is needed. Verify the two recorded fingerprints
automatically in tests. No template binary/full checkout goes into fixtures.

### RED

Add these complete tests to `tests/unit/test_factory_contract.py` first.
All imports below use the repository's existing script-by-path test helper.

```python
import json
import tempfile
import unittest
from pathlib import Path
from tests.unit._util import load

BASE = "plugin/skills/frontier-agent-factory/scripts/"

class FactoryCommon(unittest.TestCase):
    def setUp(self):
        self.m = load(BASE + "factory_common.py")

    def test_strict_json_and_real_manifest_boundary(self):
        m = self.m
        self.assertEqual(m.decode(b"{}" + b" " * (m.MIB - 2)), {})
        for raw in (b"{}" + b" " * (m.MIB - 1), b'{"a":1,"a":2}',
                    b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
                    b"\xff", b"[" * 1500, b"[" * 300 + b"0" + b"]" * 300):
            with self.subTest(raw_size=len(raw)), self.assertRaises(m.FactoryError):
                m.decode(raw)

    def test_portable_paths(self):
        m = self.m
        self.assertEqual(m.parts("docs/intake/a.md"), ("docs", "intake", "a.md"))
        self.assertEqual(m.parts(r"docs\intake\a.md"), ("docs", "intake", "a.md"))
        for value in ("../a", "/a", "//host/a", "C:/a", "a:b", "a//b",
                      "a/./b", r"\\host\a", r"a\..\b", "a.", "a ", "CON.txt", "a/\x00b"):
            with self.subTest(value=value), self.assertRaises(m.FactoryError):
                m.parts(value)
        with self.assertRaises(m.FactoryError):
            m.plain_path("bad\x00path", missing=True)

    def test_regular_reads_and_actual_byte_limit(self):
        m = self.m
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.md"
            p.write_bytes(b"A" * (16 * m.MIB))
            self.assertEqual(len(m.read(Path(d), "a.md", 16 * m.MIB)), 16 * m.MIB)
            with p.open("ab") as stream:
                stream.write(b"B")
            with self.assertRaises(m.FactoryError):
                m.read(Path(d), "a.md", 16 * m.MIB)

    def test_unknown_schema_keyword_is_not_silently_ignored(self):
        m = self.m
        self.assertTrue(m.conforms({"type": "string", "minLength": 1}, "Caldova"))
        self.assertFalse(m.conforms({"type": "integer"}, True))
        with self.assertRaises(m.FactoryError):
            m.conforms({"type": "string", "minProperties": 2}, "Caldova")
```

Run `python -m unittest tests.unit.test_factory_contract -v`.
Expected RED: missing new module first; after introducing it, assertions must
exercise the actual rules, not just imports. Record each behavioural failure.

### GREEN — complete `scripts/factory_common.py` kernel

```python
"""Bounded offline data helpers. Supplied values never enter diagnostics."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat

MIB = 1024 * 1024
ROLES = ("prd", "solution-design", "decisions", "it-readiness",
         "identity", "blueprint", "value", "finops")
EXTENSIONS = {".md", ".txt", ".json", ".pdf", ".docx", ".xlsx", ".pptx", ".csv"}
ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")

class FactoryError(ValueError):
    pass

def need(condition, code="FACTORY_INPUT"):
    if not condition:
        raise FactoryError(code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False) + "\n").encode("utf-8")

def decode(raw, limit=MIB):
    need(len(raw) <= limit, "FACTORY_LIMIT")
    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, "FACTORY_JSON")
            result[key] = value
        return result
    def constant(_value):
        raise FactoryError("FACTORY_JSON")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_constant=constant)
        pending = [(value, 0)]
        while pending:
            item, depth = pending.pop()
            need(depth <= 128, "FACTORY_JSON")
            if isinstance(item, dict):
                pending.extend((child, depth + 1) for child in item.values())
            elif isinstance(item, list):
                pending.extend((child, depth + 1) for child in item)
        encoded(value)  # Also rejects overflow-to-infinity and surrogate escapes.
        return value
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise FactoryError("FACTORY_JSON") from None

def keys(value, expected):
    need(isinstance(value, dict) and set(value) == set(expected))

def text(value):
    need(isinstance(value, str) and 0 < len(value) <= 4000 and value.strip())
    return value

def identity(value):
    need(isinstance(value, str) and len(value) <= 80 and ID.fullmatch(value))
    return value

def timestamp(value):
    need(isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})", value))
    try:
        return dt.datetime.fromisoformat(value[:-1] + "+00:00"
                                        if value[-1].lower() == "z" else value)
    except ValueError:
        raise FactoryError("FACTORY_DATE") from None

def approval(value):
    keys(value, ("by", "at", "reference"))
    text(value["by"])
    timestamp(value["at"])
    text(value["reference"])

def parts(value):
    need(isinstance(value, str) and 0 < len(value) <= 260, "FACTORY_PATH")
    result = value.replace("\\", "/").split("/")
    need(all(p not in ("", ".", "..") and
             not re.search(r'[<>:"|?*\x00-\x1f]', p) and
             not p.endswith((" ", ".")) and
             not re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p)
             for p in result), "FACTORY_PATH")
    return tuple(result)

def portable(value):
    """Canonical map/ZIP key only; never rewrite a record's path spelling."""
    return "/".join(parts(value))

def path_key(value):
    return portable(value).casefold()

def claim_path(spellings, value, *, repeat=False):
    name, key = portable(value), path_key(value)
    if key in spellings:
        need(repeat and spellings[key] == value, "FACTORY_COLLISION")
    else:
        spellings[key] = value
    return name

def plain_path(path, *, missing=False):
    value = os.fspath(path)
    need(isinstance(value, str) and "\x00" not in value, "FACTORY_PATH")
    path = Path(os.path.abspath(value))
    for candidate in (*reversed(path.parents), path):
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            need(missing, "FACTORY_PATH")
            continue
        need(not stat.S_ISLNK(info.st_mode) and
             not getattr(info, "st_file_attributes", 0) & 0x400, "FACTORY_LINK")
    return path

def read(root, relative, limit):
    root = plain_path(root)
    path = plain_path(root.joinpath(*parts(relative)))
    need(path.is_relative_to(root), "FACTORY_PATH")
    try:
        before = path.lstat()
        need(stat.S_ISREG(before.st_mode), "FACTORY_PATH")
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            need(stat.S_ISREG(opened.st_mode) and
                 (before.st_dev, before.st_ino) == (opened.st_dev, opened.st_ino),
                 "FACTORY_PATH")
            need(opened.st_size <= limit, "FACTORY_LIMIT")
            raw = stream.read(limit + 1)
        need(len(raw) <= limit, "FACTORY_LIMIT")
        plain_path(path)
        return raw
    except OSError:
        raise FactoryError("FACTORY_IO") from None

def conforms(rule, value, root=None, depth=0):
    """Only the fixed, fingerprinted upstream schema's keyword vocabulary."""
    need(depth <= 128, "FACTORY_SCHEMA")
    root = rule if root is None else root
    vocabulary = {"$schema", "$id", "title", "description", "$defs", "$ref",
                  "type", "additionalProperties", "required", "properties",
                  "const", "enum", "oneOf", "allOf", "if", "then", "else",
                  "minItems", "maxItems", "uniqueItems", "items", "minLength",
                  "maxLength", "pattern", "format"}
    need(set(rule) <= vocabulary, "FACTORY_SCHEMA")
    def check(child, item=value):
        return conforms(child, item, root, depth + 1)
    if "$ref" in rule:
        ref = rule["$ref"]
        need(ref.startswith("#/$defs/") and ref.count("/") == 2, "FACTORY_SCHEMA")
        return check(root["$defs"][ref.split("/")[-1]])
    types = {"object": dict, "array": list, "string": str,
             "boolean": bool, "null": type(None), "integer": int}
    if "type" in rule and type(value) is not types[rule["type"]]:
        return False
    if "const" in rule and (type(value) is not type(rule["const"]) or value != rule["const"]):
        return False
    if "enum" in rule and value not in rule["enum"]:
        return False
    if "oneOf" in rule and sum(check(r) for r in rule["oneOf"]) != 1:
        return False
    if "allOf" in rule and not all(check(r) for r in rule["allOf"]):
        return False
    if "if" in rule and not check(rule.get("then" if check(rule["if"]) else "else", {})):
        return False
    if isinstance(value, dict):
        properties = rule.get("properties", {})
        if not set(rule.get("required", ())) <= set(value):
            return False
        if rule.get("additionalProperties") is False and not set(value) <= set(properties):
            return False
        if any(not check(properties[k], v) for k, v in value.items() if k in properties):
            return False
    if isinstance(value, list):
        if not rule.get("minItems", 0) <= len(value) <= rule.get("maxItems", len(value)):
            return False
        if rule.get("uniqueItems") and len({encoded(v) for v in value}) != len(value):
            return False
        if "items" in rule and any(not check(rule["items"], v) for v in value):
            return False
    if isinstance(value, str):
        if not rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", len(value)):
            return False
        if "pattern" in rule and re.search(rule["pattern"], value) is None:
            return False
        if rule.get("format") == "date-time":
            try:
                timestamp(value)
            except FactoryError:
                return False
    return True
```

Catch filesystem failures at the CLI boundary too. Roots and output ancestry
are checked **before** resolving them: Python 3.11 cannot rely on the newer
`Path.is_junction`. Windows reparse attributes are not optional protection.
Work in owned private staging with no concurrent writer; this does not claim
an operating-system sandbox or eliminate hostile filesystem races.

Path spellings follow the actual receiver: both slash styles are valid.
`parts` validates either spelling; `portable` and `path_key` are used only
for filesystem/archive keys and alias comparisons. Never assign a canonical
spelling back into a parsed historical record. `claim_path` rejects
case/slash aliases before publication; only an exactly repeated source
spelling can be read again for distinct provided destinations, still charged
again to the receiver budget. Final ZIP/inventory keys use `/`.

Run the RED command again; expected GREEN. Refactor only after it passes.

## 5. Task 3 — W1 source selection and receiver semantics

F `references/template-profile.json` is the fixed compatibility profile:

```json
{
  "schema": "frontier-agent-factory-template-profile/1.0",
  "intake_schema_sha256": "04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f",
  "intake_validator_sha256": "4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370",
  "required": ["LICENSE", ".agents/skills/LICENSE.superpowers", ".agents/superpowers.lock.json", "docs/intake/intake.schema.json", "tools/intake.py", "AGENTS.md"]
}
```

Implement `factory_contract.py` with these complete functions, importing
`copy`, `re`, `Path`, and the named common helpers. `schema` always comes from
the installed, fingerprinted reference, not a schema supplied by the request.

```python
import copy
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factory_common import (FactoryError, MIB, ROLES, EXTENSIONS, approval, claim_path, conforms, digest,
                            encoded, identity, keys, need, parts, path_key, portable, text, timestamp)

def request_shape(upstream):
    """Derive only the producer request shape; never extend emitted intake."""
    intake = copy.deepcopy(upstream)
    definitions = intake.pop("$defs")
    for name in ("sourceFile", "baselineFile"):
        definitions[name]["required"].remove("sha256")
        del definitions[name]["properties"]["sha256"]
    def obj(properties):
        return {"type": "object", "additionalProperties": False,
                "required": list(properties), "properties": properties}
    def array(items, minimum=0, maximum=256):
        return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}
    def ref(name):
        return {"$ref": "#/$defs/" + name}
    def optional(rule):
        return {"oneOf": [rule, {"type": "null"}]}
    date_time = {"type": "string", "format": "date-time"}
    sha = {"type": "string", "pattern": "^[0-9a-f]{40}$"}
    selected_release = obj({"id": {"type": "integer"}, "tag": ref("text"),
                            "commit": sha, "published_at": date_time})
    # Exact value projection for every row, not raw API response retention.
    # Null ignored fields are real data; stable-candidate semantics follow.
    enumerated_release = obj({
        "id": {"type": "integer"}, "tag_name": optional({"type": "string"}),
        "published_at": optional({"type": "string"}),
        "draft": {"type": "boolean"}, "prerelease": {"type": "boolean"}})
    packet = obj({
        "artifact_ids": dict(array({"type": "string", "minLength": 3, "maxLength": 161,
                                    "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*$"},
                                   1), uniqueItems=True),
        "kind": {"enum": ["baseline", "reviewed-document"]},
        "model_path": optional(ref("path")),
        "review_paths": dict(array(ref("path"), maximum=64), uniqueItems=True),
        "owner_review": ref("approval")})
    packet["allOf"] = [{
        "if": {"properties": {"kind": {"const": "baseline"}}},
        "then": {"properties": {"model_path": ref("path")}},
        "else": {"properties": {"model_path": {"type": "null"},
                                "review_paths": {"maxItems": 0}}}}]
    shape = obj({
        "schema": {"const": "frontier-agent-factory-request/1.0"},
        "export_id": ref("id"), "created_at": date_time, "customer_scope": ref("text"),
        "evidence_kind": {"enum": ["externally-recorded", "synthetic-compatibility"]},
        "template": obj({
            "repository": {"const": "urruegg/frontier-agent-factory"},
            "selection": {"enum": ["stable-release", "unreleased-bootstrap"]},
            "commit": sha, "release": optional(selected_release),
            "discovery": obj({"status": ref("text"), "complete": {"type": "boolean"},
                              "export_id": ref("id"), "observed_at": date_time,
                              "evidence": ref("text"),
                              "releases": array(enumerated_release, maximum=2000)}),
            "bootstrap_approval": ref("optionalApproval"),
            "acquisition": obj({"status": ref("text"),
                                "method": {"enum": ["authorised-host", "explicit-local-source"]},
                                "by": ref("text"), "at": date_time, "evidence": ref("text"),
                                "archive_sha256": ref("sha256")}),
            "root_prefix": {"type": "string", "maxLength": 260}}),
        "intake": intake,
        "blueprint": obj({"source_path": ref("path"), "baseline_path": ref("path")}),
        "id_map": obj({kind: {"type": "object"} for kind in ("solutions", "agents", "requirements")}),
        "selection_evidence": array(obj({
            "solution_id": ref("id"), "original_solution_id": ref("text"),
            "original_agent_ids": dict(array(ref("text"), 1, 64), uniqueItems=True),
            "rationale": ref("text"),
            "dependency_gaps": dict(array(ref("id")), uniqueItems=True)}), 1, 32),
        "sharing_review": obj({"customer_scope": ref("text"), "metadata": ref("approval"),
                               "artifacts": {"type": "object"}}),
        "history": dict(array(ref("id"), maximum=127), uniqueItems=True),
        "financial": obj({"requested": {"type": "boolean"},
                           "as_of": optional({"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}),
                           "claim": {"enum": ["review", "build-handover"]},
                           "packets": array(packet)})})
    shape["$defs"] = definitions
    return shape

def prevalidate_request(request, upstream):
    shape = request_shape(upstream)
    need(conforms(shape, request), "FACTORY_REQUEST_SHAPE")
    # These dynamic maps have no invented wildcard-schema implementation.
    # Their containers are checked above; validate all keys/values explicitly.
    for mapping in request["id_map"].values():
        need(len(mapping) <= 512, "FACTORY_REQUEST_SHAPE")
        for original, factory in mapping.items():
            text(original)
            identity(factory)
    for qualified, evidence in request["sharing_review"]["artifacts"].items():
        need(isinstance(qualified, str), "FACTORY_REQUEST_SHAPE")
        components = qualified.split(":")
        need(len(components) == 2, "FACTORY_REQUEST_SHAPE")
        for component in components:
            identity(component)
        need(conforms(shape["$defs"]["approval"], evidence, root=shape), "FACTORY_REQUEST_SHAPE")
    for row in request["intake"]["artifacts"]:
        if row["status"] == "provided":
            parts(row["source"]["path"])
            parts(row["baseline"]["path"])
    for value in request["blueprint"].values():
        parts(value)
    for packet in request["financial"]["packets"]:
        if packet["model_path"] is not None:
            parts(packet["model_path"])
        for value in packet["review_paths"]:
            parts(value)
    # Schema permits missing engineering documents, null review approval and
    # open gaps for a legitimate clarification intake. This is shape validation,
    # not automatic acceptance, transfer approval or invention of missing data.

def source_receipt(receipt, export_id, created_at, archive_bytes):
    keys(receipt, ("repository", "selection", "commit", "release", "discovery",
                   "bootstrap_approval", "acquisition", "root_prefix"))
    need(receipt["repository"] == "urruegg/frontier-agent-factory", "FACTORY_SOURCE")
    need(isinstance(receipt["commit"], str) and
         re.fullmatch("[0-9a-f]{40}", receipt["commit"]), "FACTORY_SOURCE")
    discovery = receipt["discovery"]
    keys(discovery, ("status", "complete", "export_id", "observed_at", "evidence", "releases"))
    need(discovery["status"] == "succeeded" and discovery["complete"] is True and
         discovery["export_id"] == export_id, "FACTORY_DISCOVERY")
    need(timestamp(discovery["observed_at"]) <= timestamp(created_at), "FACTORY_DATE")
    text(discovery["evidence"])
    need(isinstance(discovery["releases"], list) and len(discovery["releases"]) <= 2000)
    stable = []
    seen = set()
    for row in discovery["releases"]:
        need(isinstance(row, dict) and
             set(row) == {"id", "tag_name", "published_at", "draft", "prerelease"},
             "FACTORY_DISCOVERY")
        need(type(row["id"]) is int and row["id"] > 0 and row["id"] not in seen,
             "FACTORY_DISCOVERY")
        seen.add(row["id"])
        need(type(row["draft"]) is bool and type(row["prerelease"]) is bool,
             "FACTORY_DISCOVERY")
        if not row["draft"] and not row["prerelease"]:
            try:
                tag = text(row["tag_name"])
                need(not any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in tag),
                     "FACTORY_DISCOVERY")
                published = timestamp(row["published_at"])
            except FactoryError:
                raise FactoryError("FACTORY_DISCOVERY") from None
            stable.append((published, row))
    if stable:
        stable.sort(key=lambda pair: pair[0])
        need(len(stable) == 1 or stable[-1][0] != stable[-2][0], "FACTORY_SOURCE")
        latest = stable[-1][1]
        text(latest["tag_name"])
        selected = receipt["release"]
        keys(selected, ("id", "tag", "commit", "published_at"))
        need(receipt["selection"] == "stable-release" and
             selected["id"] == latest["id"] and selected["tag"] == latest["tag_name"] and
             selected["published_at"] == latest["published_at"] and
             isinstance(selected["commit"], str) and
             re.fullmatch("[0-9a-f]{40}", selected["commit"]) and
             receipt["commit"] == selected["commit"] and receipt["bootstrap_approval"] is None,
             "FACTORY_SOURCE")
    else:
        need(receipt["selection"] == "unreleased-bootstrap" and receipt["release"] is None,
             "FACTORY_BOOTSTRAP")
        approval(receipt["bootstrap_approval"])
        need(receipt["commit"] in receipt["bootstrap_approval"]["reference"], "FACTORY_BOOTSTRAP")
    acquisition = receipt["acquisition"]
    keys(acquisition, ("status", "method", "by", "at", "evidence", "archive_sha256"))
    need(acquisition["status"] == "succeeded" and
         acquisition["method"] in {"authorised-host", "explicit-local-source"} and
         acquisition["archive_sha256"] == digest(archive_bytes), "FACTORY_ACQUISITION")
    text(acquisition["by"])
    text(acquisition["evidence"])
    need(timestamp(discovery["observed_at"]) <= timestamp(acquisition["at"]) <=
         timestamp(created_at), "FACTORY_DATE")
    prefix = receipt["root_prefix"]
    need(isinstance(prefix, str) and (not prefix or prefix.endswith(("/", "\\"))), "FACTORY_PATH")
    if prefix:
        parts(prefix.rstrip("/\\"))

def validate_intake(data, schema, baseline, originals=None, history=None):
    """Maps contain exact bytes keyed by portable relative path."""
    need(conforms(schema, data), "FACTORY_INTAKE_SCHEMA")
    need(len(encoded(data)) <= MIB, "FACTORY_LIMIT")
    history = {} if history is None else history
    selected = [s["solution_id"] for s in data["selected_solutions"]]
    need(len(set(selected)) == len(selected), "FACTORY_IDS")
    selected = set(selected)
    accepted = data["review"]["status"] == "accepted"
    for field in ("artifacts", "requirements", "gaps", "decisions"):
        ids = [row["id"] for row in data[field]]
        need(len(set(ids)) == len(ids), "FACTORY_IDS")
    for field in ("requirements", "gaps", "decisions"):
        need(all(row["solution_id"] in selected for row in data[field]), "FACTORY_SCOPE")
    if accepted:
        approval(data["review"]["approval"])
        need(all(any(r["solution_id"] == s for r in data["requirements"]) for s in selected),
             "FACTORY_ACCEPTANCE")
        need(all(not r["blocking"] or r["status"] == "resolved"
                 for field in ("gaps", "decisions") for r in data[field]), "FACTORY_ACCEPTANCE")
        need(data["transfer"]["permission"] == "approved", "FACTORY_TRANSFER")
    transfer = data["transfer"]
    if transfer["permission"] == "approved":
        approval(transfer["approval"])
    expected_method = ("exported-files" if data["source"]["kind"] == "exported-package"
                       else "exact-file-download")
    need(data["acquisition"]["method"] == expected_method, "FACTORY_ACQUISITION")
    declared = {(s, role): [] for s in selected for role in ROLES}
    destinations = set()
    budget = 64 * MIB
    prefix = ("docs", "intake", "records", data["intake_id"], "artifacts")
    for row in data["artifacts"]:
        need(set(row["solution_ids"]) <= selected, "FACTORY_SCOPE")
        for solution in row["solution_ids"]:
            declared[solution, row["role"]].append(row["status"])
        if row["status"] == "not-applicable":
            need(row["role"] not in {"prd", "solution-design"}, "FACTORY_APPLICABILITY")
            need(row["rationale"].strip().lower().rstrip(".") not in {
                "n/a", "na", "none", "unknown", "not applicable", "not-applicable", "tbd", "todo",
            }, "FACTORY_APPLICABILITY")
        if accepted:
            need(row["status"] != "missing", "FACTORY_ACCEPTANCE")
        if row["status"] != "provided":
            continue
        need(transfer["permission"] == "approved" and transfer["approval"] is not None and
             transfer["classification"] != "restricted", "FACTORY_TRANSFER")
        source, target, transform = row["source"], row["baseline"], row["transformation"]
        sp, tp = parts(source["path"]), parts(target["path"])
        need(tp[:5] == prefix and len(tp) > 5, "FACTORY_DESTINATION")
        need(all(Path(p[-1]).suffix.lower() in EXTENSIONS for p in (sp, tp)),
             "FACTORY_FORMAT")
        destination = "/".join(tp).casefold()
        need(destination not in destinations, "FACTORY_COLLISION")
        destinations.add(destination)
        reads = [(baseline, target)]
        if originals is not None:
            reads.append((originals, source))
        for files, record in reads:
            name = portable(record["path"])
            need(name in files, "FACTORY_MISSING")
            raw = files[name]
            need(0 < len(raw) <= min(16 * MIB, budget), "FACTORY_LIMIT")
            budget -= len(raw)
            need(digest(raw) == record["sha256"], "FACTORY_DIGEST")
        same = source["sha256"] == target["sha256"]
        if transform["kind"] == "none":
            need(same and transform["approval"] is None, "FACTORY_TRANSFORMATION")
        else:
            need(not same, "FACTORY_TRANSFORMATION")
            approval(transform["approval"])
    for statuses in declared.values():
        need(statuses and (len(statuses) == 1 or set(statuses) == {"provided"}),
             "FACTORY_APPLICABILITY")
    prior, seen = data["supersedes"], {data["intake_id"]}
    while prior is not None:
        need(prior not in seen and len(seen) < 128 and prior in history, "FACTORY_HISTORY")
        seen.add(prior)
        previous = history[prior]
        need(conforms(schema, previous) and previous["intake_id"] == prior and
             previous["review"]["status"] == "accepted", "FACTORY_HISTORY")
        prior = previous["supersedes"]

def materialize(data, baseline_root, source_root, read_file):
    """Request digests are absent, so users never copy or compare hashes."""
    result, baseline, originals = copy.deepcopy(data), {}, {}
    remaining = 64 * MIB
    source_spellings, baseline_spellings = {}, {}
    for row in result["artifacts"]:
        if row["status"] != "provided":
            continue
        for key, root, files in (("source", source_root, originals),
                                 ("baseline", baseline_root, baseline)):
            record = row[key]
            need("sha256" not in record, "FACTORY_INPUT")
            name = claim_path(source_spellings if key == "source" else baseline_spellings,
                              record["path"], repeat=key == "source")
            need(Path(name).suffix.lower() in EXTENSIONS, "FACTORY_FORMAT")
            need(remaining > 0, "FACTORY_LIMIT")
            raw = read_file(root, record["path"], min(16 * MIB, remaining))
            need(len(raw) > 0, "FACTORY_EMPTY")
            remaining -= len(raw)
            files[name] = raw
            record["sha256"] = digest(raw)
    return result, baseline, originals
```

`prevalidate_request(request, upstream_schema)` is mandatory before any
request indexing by the CLI, file materialisation or sibling invocation.
The installed upstream schema is fingerprinted first; its deepcopy supplies
the exact nested intake shape with only the two automatic digest fields
absent. Emitted/current and raw historical records still use the unchanged
upstream schema. Dynamic ID/review maps are checked before hashing or indexing.
Serializer/programming exceptions outside the JSON decoder are not converted
to ordinary input errors. The lowercase short tokens in the N/A sentinel
set are actual upstream rejected input values, not unfinished instructions.

The decoder's documented 128-level structural resource bound is checked
iteratively before recursive validation/deepcopy. Malformed/deep JSON and
NUL-containing filesystem arguments therefore become deliberate input errors
at their actual parser/path boundary; an injected producer `RecursionError`
or other programming exception still propagates. No blanket CLI fallback
is reintroduced.

### RED/GREEN sequence for semantics

Extend `test_factory_contract.py` using the shared fixture in Task 4. Add and
run each group **before** its matching function/branch:

1. Receipt: real-shaped stable, healthy empty/bootstrap, missing approval,
   wrong commit/repository/hash, draft/prerelease excluded, incomplete lookup,
   auth/network/error status, stale export ID, ambiguous stable releases,
   incompatible profile. Include draft-null fields and an older valid
   candidate whose Git tag no longer resolves; neither needs a commit in its
   enumeration row. Reject raw API extra fields. A stable candidate with
   unknown time/tag must block bootstrap and older-stable selection; only the
   selected valid candidate needs actual Git resolution. Never assert live
   GitHub state in unit tests.
2. All eight roles per selected solution; shared file uses one row with two
   `solution_ids`; missing selected scope/owner/acquisition/transfer fails
   even in needs-clarification. PRD/design N/A fails. Use the exact upstream
   `.strip().lower().rstrip(".")` sentinel comparison: short specific N/A
   explanations pass; short and arbitrarily padded sentinel strings fail.
   There is no new length threshold or NLP classifier.
3. Accepted missing design, missing approval, missing requirements, unresolved
   blockers and denied transfer fail. Needs-clarification with engineering
   gaps passes. Explicit accepted requests do not become draft success.
4. Restricted baseline, approved transfer/null approval; unchanged bytes with
   claimed transformation; redaction **and generic transformation** without
   approval; changed bytes with `none`; approved distinct digests. Validate
   originals as well as baseline, with the single shared budget.
5. Prior accepted records: preserve raw JSON and artefacts; mismatching ID,
   cycle, missing prior, unaccepted prior, reused current ID and 128th ancestor
   fail. Never modify previous records to make a new one pass.

Tests compare exact fixed error codes, not private path echoes.

The receipt/semantic mutation kernel is executable; add it to the same test
module, one case at a time before its corresponding GREEN branch:

```python
class FactoryContractCases(unittest.TestCase):
    def test_receipt_failures_are_not_no_release(self):
        import copy
        from tests.factory_fixture import prepare
        m = load(BASE + "factory_contract.py")
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            receipt = f["request"]["template"]
            raw = f["template"].read_bytes()
            m.source_receipt(receipt, "caldova-export", f["request"]["created_at"], raw)
            for case in ("network", "auth", "incomplete", "different-export", "approval", "digest"):
                r = copy.deepcopy(receipt)
                if case in {"network", "auth"}:
                    r["discovery"]["status"] = case + "-error"
                elif case == "incomplete":
                    r["discovery"]["complete"] = False
                elif case == "different-export":
                    r["discovery"]["export_id"] = "another-export"
                elif case == "approval":
                    r["bootstrap_approval"] = None
                else:
                    r["acquisition"]["archive_sha256"] = "0" * 64
                with self.subTest(case=case), self.assertRaises(ValueError):
                    m.source_receipt(r, "caldova-export", f["request"]["created_at"], raw)
            stable = {"id": 1, "tag_name": "v1.0.0",
                      "published_at": "2026-11-24T12:00:00Z", "draft": False, "prerelease": False}
            r = copy.deepcopy(receipt)
            r["discovery"]["releases"] = [stable]
            with self.assertRaises(ValueError):  # Cannot bootstrap over an available stable release.
                m.source_receipt(r, "caldova-export", f["request"]["created_at"], raw)
            r.update(selection="stable-release", commit="a" * 40,
                     release={"id": stable["id"], "tag": stable["tag_name"],
                              "commit": "a" * 40, "published_at": stable["published_at"]},
                     bootstrap_approval=None)
            m.source_receipt(r, "caldova-export", f["request"]["created_at"], raw)
            ignored = [
                {"id": 2, "tag_name": None, "published_at": None,
                 "draft": True, "prerelease": False},
                {"id": 3, "tag_name": "deleted-preview-tag", "published_at": None,
                 "draft": False, "prerelease": True},
                {"id": 4, "tag_name": "old-tag-no-longer-resolves",
                 "published_at": "2026-11-20T12:00:00Z", "draft": False,
                 "prerelease": False}]
            r["discovery"]["releases"].extend(ignored)
            before = copy.deepcopy(r)
            # No resolver/API is called by the producer. Missing ignored tag
            # objects/commits do not prevent selecting the valid latest release.
            m.source_receipt(r, "caldova-export", f["request"]["created_at"], raw)
            self.assertEqual(r, before)
            r["release"]["commit"] = None
            with self.assertRaises(ValueError):
                m.source_receipt(r, "caldova-export", f["request"]["created_at"], raw)
            r = copy.deepcopy(receipt)
            r["discovery"]["releases"] = [ignored[0], ignored[1]]
            m.source_receipt(r, "caldova-export", f["request"]["created_at"], raw)

    def test_raw_api_extra_fields_are_rejected_not_exported(self):
        import copy
        from tests.factory_fixture import prepare
        from tests.unit._util import ROOT
        m = load(BASE + "factory_contract.py")
        c = load(BASE + "factory_common.py")
        schema = c.decode((ROOT / "plugin/skills/frontier-agent-factory/references/intake.schema.json").read_bytes())
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            minimal = {"id": 2, "tag_name": None, "published_at": None,
                       "draft": True, "prerelease": False}
            for key, value in (
                ("body", "Synthetic API body must remain outside export."),
                ("author", {"login": "synthetic-author-profile"}),
                ("assets", [{"url": "https://example.invalid/protected-download"}])):
                request = copy.deepcopy(f["request"])
                request["template"]["discovery"]["releases"] = [dict(minimal, **{key: value})]
                with self.subTest(extra=key):
                    with self.assertRaisesRegex(ValueError, "FACTORY_REQUEST_SHAPE"):
                        m.prevalidate_request(request, schema)
                    with self.assertRaisesRegex(ValueError, "FACTORY_DISCOVERY"):
                        m.source_receipt(request["template"], request["export_id"],
                                         request["created_at"], f["template"].read_bytes())

    def test_unknown_stable_metadata_blocks_bootstrap_and_older_selection(self):
        import copy
        from tests.factory_fixture import prepare
        m = load(BASE + "factory_contract.py")
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            old = {"id": 1, "tag_name": "v1.0.0", "published_at": "2026-11-24T12:00:00Z",
                   "draft": False, "prerelease": False}
            for field, value in (
                ("published_at", None), ("published_at", "not-a-date"),
                ("tag_name", None), ("tag_name", ""), ("tag_name", " "),
                ("tag_name", "not a usable tag"), ("missing-tag", None)):
                for has_older in (False, True):
                    receipt = copy.deepcopy(f["request"]["template"])
                    bad = dict(old, id=99, tag_name="v2.0.0", published_at="2026-11-25T11:00:00Z")
                    if field == "missing-tag":
                        del bad["tag_name"]
                    else:
                        bad[field] = value
                    receipt["discovery"]["releases"] = ([old] if has_older else []) + [bad]
                    if has_older:
                        receipt.update(selection="stable-release", commit="a" * 40,
                                       release={"id": old["id"], "tag": old["tag_name"],
                                                "commit": "a" * 40, "published_at": old["published_at"]},
                                       bootstrap_approval=None)
                    with self.subTest(field=field, value=value, older=has_older), \
                         self.assertRaisesRegex(ValueError, "FACTORY_DISCOVERY"):
                        m.source_receipt(receipt, f["request"]["export_id"],
                                         f["request"]["created_at"], f["template"].read_bytes())

    def test_receiver_semantic_negatives(self):
        import copy
        from tests.factory_fixture import approved, prepare
        from tests.unit._util import ROOT
        m = load(BASE + "factory_contract.py")
        c = load(BASE + "factory_common.py")
        schema = c.decode((ROOT / "plugin/skills/frontier-agent-factory/references/intake.schema.json").read_bytes())
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d), accepted=True)
            good, baseline, originals = m.materialize(f["request"]["intake"],
                                                      f["baseline"], f["source"], c.read)
            m.validate_intake(good, schema, baseline, originals)
            for case in ("restricted", "null-transfer", "review", "missing-design",
                         "not-applicable-prd", "generic-transform", "redaction", "duplicate"):
                data = copy.deepcopy(good)
                if case == "restricted":
                    data["transfer"]["classification"] = "restricted"
                elif case == "null-transfer":
                    data["transfer"]["approval"] = None
                elif case == "review":
                    data["review"]["approval"] = None
                elif case in {"missing-design", "not-applicable-prd"}:
                    role = "solution-design" if case == "missing-design" else "prd"
                    row = next(r for r in data["artifacts"] if r["role"] == role)
                    row.update(status="missing" if case == "missing-design" else "not-applicable",
                               source=None, baseline=None, transformation=None)
                elif case in {"generic-transform", "redaction"}:
                    data["artifacts"][0]["transformation"] = {
                        "kind": "transformation" if case == "generic-transform" else "redaction",
                        "rationale": "Synthetic equal digests must not claim changed bytes.",
                        "approval": approved()}
                else:
                    data["artifacts"].append(copy.deepcopy(data["artifacts"][0]))
                with self.subTest(case=case), self.assertRaises(ValueError):
                    m.validate_intake(data, schema, baseline, originals)

    def test_specific_short_na_passes_and_padded_sentinels_fail(self):
        import copy
        from tests.factory_fixture import prepare
        from tests.unit._util import ROOT
        m = load(BASE + "factory_contract.py")
        c = load(BASE + "factory_common.py")
        schema = c.decode((ROOT / "plugin/skills/frontier-agent-factory/references/intake.schema.json").read_bytes())
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d), accepted=True)
            good, baseline, originals = m.materialize(f["request"]["intake"],
                                                      f["baseline"], f["source"], c.read)
            row = next(r for r in good["artifacts"] if r["role"] == "identity")
            row["rationale"] = "No runtime."
            m.validate_intake(good, schema, baseline, originals)
            for sentinel in ("n/a", "na", "none", "unknown", "not applicable",
                             "not-applicable", "tbd", "todo"):
                for padding in ("", "." * 40):
                    bad = copy.deepcopy(good)
                    target = next(r for r in bad["artifacts"] if r["role"] == "identity")
                    target["rationale"] = " \t" + sentinel.upper() + padding + "  "
                    with self.subTest(sentinel=sentinel, padding=len(padding)), self.assertRaises(ValueError):
                        m.validate_intake(bad, schema, baseline, originals)
```

## 6. Task 4 — W1 reusable tiny Caldova fixture and boundary regressions

Create `tests/factory_fixture.py`. It is repository test support, never
imported from installed plugin code. This complete fixture is also the base
for packaged/export integration; all synthetic approvals are labelled.

```python
import copy
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "plugin/skills/frontier-agent-factory"
AT = "2026-11-25T12:00:00Z"
COMMIT = "0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d"

def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()

def approved(reference="synthetic-review-not-authentication"):
    return {"by": "Caldova synthetic reviewer", "at": AT, "reference": reference}

def zip_bytes(files, compression=zipfile.ZIP_STORED):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as archive:
        for name, raw in sorted(files.items()):
            info = zipfile.ZipInfo(name, (2026, 11, 25, 12, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = compression
            archive.writestr(info, raw)
    return out.getvalue()

def prepare(root, *, accepted=False, foundation=None):
    root = Path(root)
    source, baseline = root / "originals", root / "approved"
    source.mkdir(parents=True)
    baseline.mkdir(parents=True)
    blueprint = {"meta": {"audience": "customer"}, "evidence": [],
                 "domains": [{"id": "D1", "agents": [{"id": "D1-A01", "name": "Caldova assistant"}]}]}
    docs = {"prd.md": b"# Caldova PRD\n\nFR-001: Show the reviewed status.\n",
            "blueprint.json": encode(blueprint)}
    if accepted:
        docs["design.md"] = b"# Caldova design\n\nRetain FR-001 and a human review seam.\n"
    record = "caldova-intake"
    prefix = f"docs/intake/records/{record}/artifacts/"
    rows = []
    names = {"prd": "prd.md", "blueprint": "blueprint.json", "solution-design": "design.md"}
    for role in ("prd", "solution-design", "decisions", "it-readiness", "identity", "blueprint", "value", "finops"):
        name = names.get(role)
        provided = name in docs
        required = role in ("prd", "solution-design")
        rows.append({
            "id": role, "solution_ids": ["caldova-service"], "role": role,
            "status": "provided" if provided else "missing" if required else "not-applicable",
            "rationale": "Selected synthetic evidence." if provided else
                         "Obtain the reviewed design before acceptance." if required else
                         "This synthetic local review has no dependency in this role.",
            "source": {"path": name, "reference": "synthetic-selected-source",
                       "version": "synthetic-v1", "modified_at": "unknown"} if provided else None,
            "baseline": {"path": prefix + name} if provided else None,
            "transformation": {"kind": "none", "rationale": "Exact reviewed synthetic bytes.",
                               "approval": None} if provided else None})
    for name, raw in docs.items():
        (source / name).write_bytes(raw)
        path = baseline / (prefix + name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    intake = {
        "schema_version": "1.0", "intake_id": record, "supersedes": None,
        "selected_solutions": [{"solution_id": "caldova-service", "agent_ids": ["service-agent"],
                                "scope": "Caldova synthetic status review only.",
                                "owners": ["Caldova synthetic product owner"]}],
        "source": {"kind": "exported-package", "references": ["synthetic-selected-source"],
                   "plugin_version": "unknown", "blueprint_version": "unknown"},
        "acquisition": {"status": "succeeded", "method": "exported-files",
                        "verified_by": "Caldova synthetic fixture author", "verified_at": AT,
                        "evidence": "Actual local synthetic bytes; no tenant access."},
        "transfer": {"classification": "public", "destination": "Caldova synthetic review",
                     "permission": "approved", "approval": approved()},
        "artifacts": rows,
        "requirements": [{"id": "fr-001", "solution_id": "caldova-service",
                          "description": "Show the reviewed status.",
                          "acceptance_criteria": ["The selected status is visible."]}],
        "gaps": [] if accepted else [{"id": "design-gap", "solution_id": "caldova-service",
                                      "description": "Obtain the reviewed design.", "blocking": True,
                                      "status": "open", "resolution": None}],
        "decisions": [],
        "review": {"status": "accepted" if accepted else "needs-clarification",
                   "rationale": "Synthetic receiver compatibility, not real approval.",
                   "approval": approved() if accepted else None}}
    if foundation is None:
        files = {
            "LICENSE": b"Synthetic foundation licence fixture; not upstream attribution.\n",
            ".agents/skills/LICENSE.superpowers": b"Synthetic vendor notice fixture.\n",
            ".agents/superpowers.lock.json": b'{"synthetic":true}\n',
            "AGENTS.md": b"# Passive synthetic receiving policy\n",
            ".github/workflows/test.yml": b"name: Passive synthetic fixture\n",
            "solutions/README.md": b"# No accepted solution units yet\n",
            "docs/intake/intake.schema.json": (F / "references/intake.schema.json").read_bytes(),
            "tools/intake.py": (ROOT / "tests/fixtures/factory/intake-reference.py.txt").read_bytes()}
        foundation = zip_bytes(files)
    archive = root / "template.zip"
    archive.write_bytes(foundation)
    request = {
        "schema": "frontier-agent-factory-request/1.0", "export_id": "caldova-export",
        "created_at": AT, "customer_scope": "Caldova synthetic service",
        "evidence_kind": "synthetic-compatibility",
        "template": {
            "repository": "urruegg/frontier-agent-factory", "selection": "unreleased-bootstrap",
            "commit": COMMIT, "release": None,
            "discovery": {"status": "succeeded", "complete": True, "export_id": "caldova-export",
                          "observed_at": AT, "evidence": "Synthetic healthy empty enumeration.",
                          "releases": []},
            "bootstrap_approval": approved("synthetic-bootstrap-" + COMMIT),
            "acquisition": {"status": "succeeded", "method": "explicit-local-source",
                            "by": "Caldova synthetic fixture author", "at": AT,
                            "evidence": "Synthetic acquisition, not current live discovery.",
                            "archive_sha256": hashlib.sha256(foundation).hexdigest()},
            "root_prefix": ""},
        "intake": intake,
        "blueprint": {"source_path": "blueprint.json", "baseline_path": prefix + "blueprint.json"},
        "id_map": {"solutions": {"D1": "caldova-service"}, "agents": {"D1-A01": "service-agent"},
                   "requirements": {"FR-001": "fr-001"}},
        "selection_evidence": [{"solution_id": "caldova-service", "original_solution_id": "D1",
                                "original_agent_ids": ["D1-A01"],
                                "rationale": "Explicit synthetic scope, not keyword selection.",
                                "dependency_gaps": []}],
        "sharing_review": {"customer_scope": "Caldova synthetic service", "metadata": approved(),
                           "artifacts": {record + ":" + r["id"]: approved()
                                         for r in rows if r["status"] == "provided"}},
        "history": [],
        "financial": {"requested": False, "as_of": None, "claim": "review", "packets": []}}
    request_file = root / "request.json"
    request_file.write_bytes(encode(request))
    return {"request": request, "request_file": request_file, "template": archive,
            "source": source, "baseline": baseline, "out": root / "factory.zip"}

def save(fixture):
    fixture["request_file"].write_bytes(encode(fixture["request"]))
```

Remove unused `copy` only in the post-GREEN refactor. Do not label the tiny
foundation an authentic acquired upstream checkout. Its two fingerprinted text
files anchor compatibility; Task 13 proves all actual foundation bytes.

Add complete budget test below to the contract test class; then add the
receipt/semantic mutation tests as individual 2–5 minute RED/GREEN pairs.

```python
def test_one_real_shared_budget_not_one_budget_per_root(self):
    import copy
    from tests.factory_fixture import prepare
    from tests.unit._util import ROOT
    m = load(BASE + "factory_contract.py")
    c = load(BASE + "factory_common.py")
    schema = c.decode((ROOT / "plugin/skills/frontier-agent-factory/references/intake.schema.json").read_bytes())
    with tempfile.TemporaryDirectory() as d:
        f = prepare(Path(d), accepted=True)
        data, baseline, originals = m.materialize(f["request"]["intake"],
                                                 f["baseline"], f["source"], c.read)
        # Four 8 MiB artefacts, each original also read: exactly 64 MiB.
        template = copy.deepcopy(data["artifacts"][0])
        others = [r for r in data["artifacts"] if r["status"] != "provided"]
        rows, baseline, originals = [], {}, {}
        for index, role in enumerate(("prd", "solution-design", "blueprint", "decisions")):
            row = copy.deepcopy(template)
            row.update(id=f"large-{index}", role=role)
            row["source"]["path"] = f"large-{index}.txt"
            row["baseline"]["path"] = f"docs/intake/records/caldova-intake/artifacts/large-{index}.txt"
            raw = b"A" * (8 * c.MIB)
            row["source"]["sha256"] = row["baseline"]["sha256"] = c.digest(raw)
            originals[row["source"]["path"]] = baseline[row["baseline"]["path"]] = raw
            rows.append(row)
        data["artifacts"] = rows + [r for r in others if r["role"] != "decisions"]
        m.validate_intake(data, schema, baseline, originals)
        last = rows[-1]
        changed = originals[last["source"]["path"]] + b"B"
        originals[last["source"]["path"]] = changed
        last["source"]["sha256"] = c.digest(changed)
        last["transformation"] = {"kind": "transformation",
                                  "rationale": "Synthetic distinct original byte.",
                                  "approval": {"by": "Synthetic reviewer",
                                               "at": "2026-11-25T12:00:00Z",
                                               "reference": "synthetic-only"}}
        m.validate_intake(data, schema, baseline)  # Baseline-only still fits.
        with self.assertRaisesRegex(ValueError, "FACTORY_LIMIT"):
            m.validate_intake(data, schema, baseline, originals)  # 64 MiB + one.
```

The test uses `_util.ROOT`; production never depends on the test process's
working directory. Cross-module tests catch `ValueError` with the exact error
code because `_util.load` can load a second module/class identity by path.

Required real boundaries, not patched smaller constants: manifest 1 MiB /
one byte over, artefact 16 MiB / one over, combined originals+baseline 64 MiB /
one over. Repeat approved-transfer/null, restricted-baseline, generic
transformation/equal-digest and non-finite JSON cases here: those are W0 coverage
gaps, not requests to edit upstream tests. Run
`python -m unittest tests.unit.test_factory_contract -v`; commit W1 only
after all intended negatives are observed and GREEN.

## 7. Task 5 — W2 extract the proven raw ZIP mechanism without release drift

RED first: add `tests/unit/test_factory_shared_zip.py`:

```python
import unittest
from tests.unit._util import ROOT, load

class SharedZip(unittest.TestCase):
    def test_tools_and_installed_raw_mechanism_are_identical(self):
        a = ROOT / "tools/zip_stream.py"
        b = ROOT / "plugin/skills/frontier-agent-factory/scripts/zip_stream.py"
        self.assertTrue(a.is_file() and b.is_file())
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_release_wrapper_keeps_its_error_type_and_raw_checks(self):
        from tests.unit.test_release_evidence import tiny_zip, forged_zip_size
        import io
        import zipfile
        evidence = load("tools/release_evidence.py")
        raw = forged_zip_size(tiny_zip(data=b"AA"))
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            with self.assertRaises(evidence.EvidenceError):
                evidence._zip_member(raw, archive.infolist()[0], 1024)
```

Run that module plus `tests.unit.test_release_evidence`. The new shared-copy
test is RED; the unchanged release regressions must retain their baseline.

GREEN: move the **entire existing** `_zip_member(data, entry, remaining)`
body from `tools/release_evidence.py` to new `tools/zip_stream.py`.
Preserve copyright/SPDX. Name it `raw_member(data, entry, remaining, *,
error=ValueError)` and define its private `_require` as a nested function:

```python
import struct
import zipfile
import zlib

def raw_member(data, entry, remaining, *, error=ValueError):
    """Validate actual STORED/DEFLATED bytes, CRC, exact size and stream EOF."""
    def _require(condition, message):
        if not condition:
            raise error(message)
    _require(entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
             "Unsupported ZIP compression method; only STORED and DEFLATED are accepted")
    offset = entry.header_offset
    _require(0 <= offset <= len(data) - 30, "Invalid ZIP local header offset")
    header = struct.unpack_from("<4s5H3I2H", data, offset)
    _require(header[0] == b"PK\x03\x04" and header[2] == entry.flag_bits and header[3] == entry.compress_type,
             "ZIP local/central header mismatch")
    if not entry.flag_bits & 8:
        _require(header[6:9] == (entry.CRC, entry.compress_size, entry.file_size), "ZIP local/central size or CRC mismatch")
    position = offset + 30 + header[-2] + header[-1]
    end = position + entry.compress_size
    _require(position <= end <= len(data), "ZIP compressed span exceeds archive")
    allowed = min(entry.file_size, remaining)
    count = crc = 0
    decoder = zlib.decompressobj(-zlib.MAX_WBITS) if entry.compress_type == zipfile.ZIP_DEFLATED else None
    pending = b""
    while True:
        maximum = min(65536, allowed - count + 1)
        if decoder is None:
            output = data[position:min(end, position + maximum)]
            position += len(output)
        else:
            if not pending and position < end:
                pending = data[position:min(end, position + 65536)]
                position += len(pending)
            output = decoder.decompress(pending, maximum)
            pending = decoder.unconsumed_tail
        count += len(output)
        _require(count <= allowed, f"ZIP expanded content exceeds allowed size ({count} > {allowed})")
        crc = zlib.crc32(output, crc)
        if decoder is None:
            if position == end:
                break
        elif decoder.eof:
            _require(not decoder.unused_data and not pending and position == end, "Extra bytes after complete DEFLATE stream")
            break
        else:
            _require(pending or position < end or output, "Incomplete DEFLATE stream")
    _require(count == entry.file_size, "ZIP actual decoded size differs from declared size")
    _require(crc == entry.CRC, "ZIP actual decoded CRC mismatch")
    return count
```

This is a mechanical extraction of
`tools/release_evidence.py::_zip_member`: all validation statements and
messages remain unchanged; only the injected error class and function name
differ. Module imports are exactly `struct`, `zipfile`, `zlib`. Copy the resulting
module byte-identically to F `scripts/zip_stream.py`. There is one algorithm,
not two separately maintained implementations or a new archive framework.

Replace the old release function with this complete compatibility wrapper,
and add its import next to the existing imports:

```python
from zip_stream import raw_member

def _zip_member(data, entry, remaining):
    return raw_member(data, entry, remaining, error=EvidenceError)
```

Keep release `_zip` validation, limits, exception mapping and post-raw
`testzip()` unchanged. Keep existing forged-size, LZMA/BZIP2, truncated EOF,
trailing compressed bytes, CRC/cache-preservation tests unchanged.
Remove only now-unused `struct`/`zlib` imports if the rest of the module no
longer needs them; both are still used by `_zip`'s exception tuple, so retain
them with the current source.

Extend `tools/check_repo.py::check_skills` precisely beside its `fv_expr.py`
byte-identity assertion:

```python
if (ROOT / "tools/zip_stream.py").read_bytes() != (
    SKILLS / "frontier-agent-factory/scripts/zip_stream.py"
).read_bytes():
    r.err("skills", "zip_stream.py differs between tools and frontier-agent-factory")
```

Add a checker mutation test using a temporary ROOT/SKILLS fixture: change one
copy byte and assert that exact error; restore it and assert absence. Never
weaken the existing formula or release checks. Rerun the two modules and
`python tools\check_repo.py --strict`. Only actual GREEN supports extraction.

## 8. Task 6 — W2 bounded foundation, deterministic ZIP and atomic publication

Add `tests/unit/test_factory_archive.py` first; use the existing
`tiny_zip`, `forged_zip_size`, `changed_compressed_payload` test helpers from
`tests.unit.test_release_evidence`, not new production imports. Minimal tests:

```python
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import zipfile
from tests.unit._util import ROOT, load
from tests.factory_fixture import prepare, zip_bytes
from tests.unit.test_release_evidence import tiny_zip, forged_zip_size, changed_compressed_payload

class FactoryArchive(unittest.TestCase):
    def setUp(self):
        self.m = load("plugin/skills/frontier-agent-factory/scripts/factory_archive.py")

    def test_raw_forgery_and_eof_are_rejected(self):
        for method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
            raw = tiny_zip(data=b"A" * 10000, compression=method)
            with self.subTest(method=method), self.assertRaises(ValueError):
                self.m.foundation(forged_zip_size(raw), "", {})
        raw = tiny_zip(data=b"A" * 10000, compression=zipfile.ZIP_DEFLATED)
        for mutate in (lambda p: p[:-1], lambda p: p + b"extra"):
            with self.assertRaises(ValueError):
                self.m.foundation(changed_compressed_payload(raw, mutate), "", {})

    def test_fixed_inputs_produce_exact_bytes_and_no_manifest_self_hash(self):
        entries = {"START_HERE.md": (b"# Caldova\n", 0o644)}
        a = self.m.archive_bytes(entries, "2026-11-25T12:00:00Z")
        b = self.m.archive_bytes(dict(reversed(list(entries.items()))),
                                 "2026-11-25T12:00:00Z")
        self.assertEqual(a, b)

    def test_failed_replace_preserves_good_output_and_removes_temporary(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "good.zip"
            out.write_bytes(b"old-good")
            with mock.patch.object(self.m.os, "replace", side_effect=OSError):
                with self.assertRaises(ValueError):
                    self.m.publish(out, b"new")
            self.assertEqual(out.read_bytes(), b"old-good")
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ["good.zip"])
```

Run `python -m unittest tests.unit.test_factory_archive -v`, observe RED, then
implement this complete `scripts/factory_archive.py`:

```python
from __future__ import annotations
import io
import os
from pathlib import Path
import stat
import struct
import sys
import tempfile
import zipfile
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factory_common import (FactoryError, MIB, digest, need, parts, path_key, portable,
                            plain_path, timestamp)
from zip_stream import raw_member

FORBIDDEN = {".git", ".factory-local", "node_modules", "__pycache__", ".venv", "venv",
             ".pytest_cache", ".ruff_cache", ".azure", ".aws", ".ssh", ".env",
             ".ds_store", "thumbs.db"}

def safe_name(name):
    path = parts(name)
    need(not any(p.casefold() in FORBIDDEN or p.casefold().endswith((".pyc", ".pyo"))
                 for p in path), "FACTORY_STATE")
    return "/".join(path)

def foundation_shape(name, *, directory=False):
    components = parts(name)
    folded = tuple(p.casefold() for p in components)
    for root in (("docs", "intake", "records"), ("solutions",)):
        if folded[:len(root)] != root:
            continue
        if len(components) == len(root):
            need(directory, "FACTORY_TEMPLATE")
        else:
            # Passive catalogues at the root are foundation data, not a
            # populated baseline or solution unit. No descendant unit tree.
            need(not directory and len(components) == len(root) + 1 and
                 Path(components[-1]).suffix.lower() == ".md", "FACTORY_TEMPLATE")

def capacity(entries, *, expanded=128 * MIB, members=4096):
    need(len(entries) <= members, "FACTORY_LIMIT")
    seen, total = set(), 0
    for name, (raw, mode) in entries.items():
        safe_name(name)
        key = path_key(name)
        need(key not in seen and mode in (0o644, 0o755), "FACTORY_COLLISION")
        # Also refuse a file used as another file's directory.
        need(not any("/".join(parts(name)[:i]).casefold() in seen
                     for i in range(1, len(parts(name)))), "FACTORY_COLLISION")
        seen.add(key)
        total += len(raw)
        need(total <= expanded, "FACTORY_LIMIT")
    need(not any("/".join(parts(name)[:i]).casefold() in seen
                 for name in entries for i in range(1, len(parts(name)))),
         "FACTORY_COLLISION")

def foundation(raw, prefix, profile):
    need(0 < len(raw) <= 32 * MIB, "FACTORY_LIMIT")
    prefix = portable(prefix.rstrip("/\\")) + "/" if prefix else ""
    result = {}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members = archive.infolist()
            need(len(members) <= 4096, "FACTORY_LIMIT")
            seen, total = set(), 0
            for entry in members:
                need(entry.filename == entry.orig_filename and not entry.flag_bits & 1, "FACTORY_ZIP")
                name = entry.filename.replace("\\", "/")
                directory = name.endswith("/")
                safe_name(name[:-1] if directory else name)
                key = path_key(name[:-1] if directory else name)
                need(key not in seen, "FACTORY_COLLISION")
                seen.add(key)
                mode = entry.external_attr >> 16
                kind = stat.S_IFMT(mode)
                need(kind in (0, stat.S_IFREG, stat.S_IFDIR), "FACTORY_LINK")
                need(kind == 0 or (kind == stat.S_IFDIR) == directory, "FACTORY_MODE")
                need(entry.file_size <= 64 * MIB - total, "FACTORY_LIMIT")
                total += raw_member(raw, entry, 64 * MIB - total, error=FactoryError)
                if prefix:
                    need(name.startswith(prefix), "FACTORY_TEMPLATE")
                    name = name[len(prefix):]
                if directory:
                    need(entry.file_size == 0, "FACTORY_ZIP")
                    if name:
                        foundation_shape(name.rstrip("/"), directory=True)
                    continue
                name = safe_name(name)
                foundation_shape(name)
                permissions = stat.S_IMODE(mode) if mode else 0o644
                need(permissions in (0o644, 0o755), "FACTORY_MODE")
                result[name] = (archive.read(entry), permissions)
            need(archive.testzip() is None, "FACTORY_ZIP")
        capacity(result, expanded=64 * MIB)
        need(set(profile["required"]) <= set(result), "FACTORY_TEMPLATE")
        need(digest(result["docs/intake/intake.schema.json"][0]) ==
             profile["intake_schema_sha256"] and
             digest(result["tools/intake.py"][0]) == profile["intake_validator_sha256"],
             "FACTORY_COMPATIBILITY")
        return result
    except FactoryError:
        raise
    except (ValueError, OSError, RuntimeError, EOFError, NotImplementedError,
            zipfile.BadZipFile, struct.error, zlib.error):
        raise FactoryError("FACTORY_ZIP") from None

def archive_bytes(entries, created_at):
    capacity(entries)
    time = timestamp(created_at).astimezone(__import__("datetime").timezone.utc)
    need(1980 <= time.year <= 2107, "FACTORY_DATE")
    stamp = (time.year, time.month, time.day, time.hour, time.minute, time.second)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", allowZip64=False) as archive:
        for name, (raw, permissions) in sorted(entries.items(), key=lambda row: portable(row[0])):
            info = zipfile.ZipInfo(safe_name(name), stamp)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | permissions) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, raw)
    return out.getvalue()

def publish(output, raw):
    output = plain_path(output, missing=True)
    need(output.parent.is_dir(), "FACTORY_OUTPUT")
    need(not output.exists() or output.is_file(), "FACTORY_OUTPUT")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".factory-", suffix=".tmp",
                                         dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        plain_path(output, missing=True)
        os.replace(temporary, output)
    except OSError:
        raise FactoryError("FACTORY_IO") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
```

Before calling it GREEN, add the following actual adversarial cases as
separate failing tests, then minimal corrections, then rerun:

- Raw malformed local/central sizes, forged decoded size, STORED and DEFLATED
  CRC mismatch, missing EOF, trailing compressed bytes, unsupported methods,
  encrypted flag, duplicate/case-fold collisions, embedded NUL/original-name
  mismatch, traversal/absolute/UNC/device/ADS, symlink/special file, file/parent
  alias in either order. Structural `testzip` is **after** raw validation.
- Exact source compressed 32 MiB / one over: use a valid tiny archive and
  legal archive padding to the exact byte count; ensure the positive reaches
  profile checks. Expanded 64 MiB / one over: valid DEFLATED ordinary member
  bytes, not forged advertised sizes. Exact source 4096 / 4097 members.
- Exact final 128 MiB / one over and 4096 / 4097 **including generated files**;
  check with real buffers and actual `archive_bytes`, not patched constants.
  Use repeated shared buffers and sequential tests to bound test memory.
- Prepopulated real intake, precreated solution units, missing required
  licence/lock/schema/validator, changed schema/validator fingerprints,
  explicit wrapper prefix, mismatched wrapper, state/cache/dependency paths.
  Permit direct passive Markdown catalogues, including
  `docs/intake/records/README.md`, instead of blanket-rejecting that prefix;
  reject `<record-id>/intake.json`, `<solution-id>/` and even empty unit
  directory entries. Preserve all permitted foundation bytes.
- Output aliases request/template/original/baseline/history inputs; existing
  output directory, symlink, dangling link, Windows junction/reparse ancestor;
  failure before publication and at `os.replace` preserves old good bytes.

The complete function catches raw decode and structural ZIP exceptions as in
the release caller. Observe these corrupt-payload tests failing before adding
the catch in the minimal GREEN iteration. This does not change release behaviour.

For Windows junction coverage use a test-owned directory junction created by
`cmd /c mklink /J`, with subprocess capture and explicit return-code handling.
Test both file-root and output-ancestor refusal; remove the junction itself
in `finally`, never recursively remove its target. A genuine inability to
create a symlink can be a recorded privilege skip; mock a reparse `lstat`
as an additional portable test, not a substitute for available junction proof.

The real-limit tests can be added as these complete methods on
`FactoryArchive`, before their respective GREEN checks:

```python
def test_real_source_compressed_boundary(self):
    import json
    with tempfile.TemporaryDirectory() as d:
        f = prepare(Path(d))
        with zipfile.ZipFile(f["template"]) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        profile = json.loads((ROOT / "plugin/skills/frontier-agent-factory/references/template-profile.json").read_bytes())
        files["padding.dat"] = b""
        size = 32 * 1024 * 1024 - len(zip_bytes(files))
        files["padding.dat"] = b"A" * size
        raw = zip_bytes(files)
        self.assertEqual(len(raw), 32 * 1024 * 1024)
        self.m.foundation(raw, "", profile)
        files["padding.dat"] += b"B"
        with self.assertRaisesRegex(ValueError, "FACTORY_LIMIT"):
            self.m.foundation(zip_bytes(files), "", profile)

def test_real_source_expanded_and_member_limits(self):
    import json
    with tempfile.TemporaryDirectory() as d:
        f = prepare(Path(d))
        with zipfile.ZipFile(f["template"]) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        profile = json.loads((ROOT / "plugin/skills/frontier-agent-factory/references/template-profile.json").read_bytes())
        files["padding.dat"] = b"A" * (64 * 1024 * 1024 - sum(map(len, files.values())))
        self.m.foundation(zip_bytes(files, zipfile.ZIP_DEFLATED), "", profile)
        files["padding.dat"] += b"B"
        with self.assertRaisesRegex(ValueError, "FACTORY_LIMIT"):
            self.m.foundation(zip_bytes(files, zipfile.ZIP_DEFLATED), "", profile)
        del files["padding.dat"]
        while len(files) < 4096:
            files[f"member-{len(files)}.txt"] = b"A"
        self.m.foundation(zip_bytes(files), "", profile)
        files["one-too-many.txt"] = b"B"
        with self.assertRaisesRegex(ValueError, "FACTORY_LIMIT"):
            self.m.foundation(zip_bytes(files), "", profile)

def test_real_final_expanded_and_member_limits(self):
    mib = 1024 * 1024
    chunk = b"A" * (16 * mib)
    entries = {f"data-{n}.txt": (chunk, 0o644) for n in range(8)}
    raw = self.m.archive_bytes(entries, "2026-11-25T12:00:00Z")
    self.assertGreater(len(raw), 128 * mib)  # Actual ZIP includes container overhead.
    del raw
    with self.assertRaisesRegex(ValueError, "FACTORY_LIMIT"):
        self.m.archive_bytes(dict(entries, **{"one-byte.txt": (b"B", 0o644)}),
                             "2026-11-25T12:00:00Z")
    small = {f"item-{n}.txt": (b"A", 0o644) for n in range(4096)}
    self.m.archive_bytes(small, "2026-11-25T12:00:00Z")
    small["item-4096.txt"] = (b"A", 0o644)
    with self.assertRaisesRegex(ValueError, "FACTORY_LIMIT"):
        self.m.archive_bytes(small, "2026-11-25T12:00:00Z")
```

Both source positives contain a complete compatible synthetic foundation and
exercise actual bytes, not forged declarations or a missing-profile failure.
The 32 MiB case uses a normal STORED member; it does not depend on ZIP
end-search behaviour for arbitrary trailing padding.

Actual reference path-policy review: the retained reference has no root
`docs/intake/records` tree and `solutions` contains only `README.md`. Its
synthetic intake fixtures live beneath `tests/fixtures`, not a real baseline,
and must remain preserved. The known 149-blob source passes this revised
baseline/solution shape rule. The retained checkout also has ignored local
test state and Python caches; those are not source blobs. Acquire with the
exact-commit Git archive, not a recursive ZIP of the checkout. This is a
read-only path-policy assessment, not an executed producer/ZIP-validator pass.

Add these methods to `FactoryArchive` before the corresponding GREEN branches:

```python
def test_passive_catalogues_are_not_prepopulated_units(self):
    import json
    with tempfile.TemporaryDirectory() as d:
        f = prepare(Path(d))
        with zipfile.ZipFile(f["template"]) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        profile = json.loads((ROOT / "plugin/skills/frontier-agent-factory/references/template-profile.json").read_bytes())
        files.update({"docs/intake/records/README.md": b"# Passive intake catalogue\n",
                      "docs/intake/records/INDEX.md": b"# Passive catalogue index\n",
                      "solutions/INDEX.md": b"# Passive solution catalogue\n"})
        self.m.foundation(zip_bytes(files), "", profile)
        for name in ("docs/intake/records/old/intake.json", "solutions/old/README.md"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "FACTORY_TEMPLATE"):
                self.m.foundation(zip_bytes({**files, name: b"synthetic populated unit"}), "", profile)
        out = io.BytesIO(zip_bytes(files))
        with zipfile.ZipFile(out, "a") as archive:
            info = zipfile.ZipInfo("solutions/empty-unit/")
            info.create_system = 3
            info.external_attr = 0o40755 << 16
            archive.writestr(info, b"")
        with self.assertRaisesRegex(ValueError, "FACTORY_TEMPLATE"):
            self.m.foundation(out.getvalue(), "", profile)

def test_mixed_slash_archive_alias_is_a_collision(self):
    entries = {r"docs\intake\a.md": (b"A", 0o644), "docs/intake/a.md": (b"A", 0o644)}
    with self.assertRaisesRegex(ValueError, "FACTORY_COLLISION"):
        self.m.archive_bytes(entries, "2026-11-25T12:00:00Z")
```

Run shared, archive and existing release suites together. Commit W2 only after
the old release behaviour remains GREEN.

## 9. Task 7 — W3 passive authored-byte projection and explicit selection

Write `tests/unit/test_factory_export.py` first. The first end-to-end RED is:

```python
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from tests.unit._util import load
from tests.factory_fixture import prepare, save

class FactoryExport(unittest.TestCase):
    def invoke(self, f, *extra):
        m = load("plugin/skills/frontier-agent-factory/scripts/export_factory.py")
        stream = io.StringIO()
        args = ["--request", str(f["request_file"]), "--template", str(f["template"]),
                "--source-root", str(f["source"]), "--baseline-root", str(f["baseline"]),
                "--out", str(f["out"]), *extra]
        with contextlib.redirect_stdout(stream):
            code = m.main(args)
        return code, json.loads(stream.getvalue())

    def test_default_is_valid_review_starter_and_is_reproducible(self):
        import zipfile
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            code, summary = self.invoke(f)
            self.assertEqual(code, 0, summary)
            first = f["out"].read_bytes()
            self.assertEqual(summary["intake_disposition"], "needs-clarification")
            self.assertEqual(summary["receiver_validation"], "not-performed")
            self.assertEqual(summary["cowork_validation"], "not-performed")
            self.assertEqual(self.invoke(f)[0], 0)
            self.assertEqual(first, f["out"].read_bytes())
            with zipfile.ZipFile(f["out"]) as z:
                self.assertFalse(any(n.startswith("solutions/") and n != "solutions/README.md"
                                     for n in z.namelist()))
                manifest = json.loads(z.read("handover/manifest.json"))
                self.assertNotIn("handover/manifest.json", manifest["inventory"])
                self.assertEqual(z.read("docs/intake/records/caldova-intake/artifacts/prd.md"),
                                 (f["source"] / "prd.md").read_bytes())

    def test_explicit_accepted_with_missing_design_is_error_not_downgrade(self):
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            f["out"].write_bytes(b"old-good")
            f["request"]["intake"]["review"]["status"] = "accepted"
            save(f)
            code, result = self.invoke(f)
            self.assertEqual(code, 1)
            self.assertIn("error", result)
            self.assertEqual(f["out"].read_bytes(), b"old-good")
```

Implement F `scripts/factory_projection.py`. Start with this complete
installed-sibling loader and immutable blueprint check:

```python
import contextlib
import copy
import importlib.util
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factory_common import (MIB, FactoryError, approval, claim_path, conforms, decode, digest, encoded,
                            identity, keys, need, parts, path_key, portable, read, text)

SKILLS = Path(__file__).resolve().parents[2]

@contextlib.contextmanager
def sibling(skill, module):
    directory = SKILLS / skill / "scripts"
    path = directory / (module + ".py")
    need(path.is_file(), "FACTORY_OPTIONAL_SKILL")
    previous = sys.path[:]
    try:
        sys.path.insert(0, str(directory))
        spec = importlib.util.spec_from_file_location("factory_" + module, path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        yield loaded
    finally:
        sys.path[:] = previous

@contextlib.contextmanager
def validation_input(code):
    """Only documented ValueError validation failures of a named input API."""
    try:
        yield
    except FactoryError:
        raise
    except ValueError:
        raise FactoryError(code) from None

def blueprint_shape(document):
    need(isinstance(document, dict), "FACTORY_BLUEPRINT")
    meta = document.get("meta", {})
    need(isinstance(meta, dict), "FACTORY_BLUEPRINT")
    terms = meta.get("internal_terms", [])
    need(terms is None or isinstance(terms, str) or
         (isinstance(terms, list) and all(isinstance(t, str) for t in terms)),
         "FACTORY_BLUEPRINT")
    evidence = document.get("evidence", [])
    need(isinstance(evidence, list), "FACTORY_BLUEPRINT")
    for row in evidence:
        need(isinstance(row, dict) and isinstance(row.get("id"), str), "FACTORY_BLUEPRINT")
        text(row["id"])
    domains = document.get("domains", [])
    need(isinstance(domains, list), "FACTORY_BLUEPRINT")
    for domain in domains:
        need(isinstance(domain, dict) and isinstance(domain.get("id"), str), "FACTORY_BLUEPRINT")
        text(domain["id"])
        agents = domain.get("agents", [])
        need(isinstance(agents, list), "FACTORY_BLUEPRINT")
        lead = domain.get("orchestrator")
        if lead is not None:
            need(isinstance(lead, dict), "FACTORY_BLUEPRINT")
            agents = [*agents, lead]
        for agent in agents:
            need(isinstance(agent, dict) and isinstance(agent.get("id"), str), "FACTORY_BLUEPRINT")
            text(agent["id"])
    if "ontology" in document:
        need(document["ontology"] is None or isinstance(document["ontology"], dict),
             "FACTORY_BLUEPRINT")

def check_blueprint(request, baseline, originals):
    descriptor = request["blueprint"]
    keys(descriptor, ("source_path", "baseline_path"))
    source_name, baseline_name = portable(descriptor["source_path"]), portable(descriptor["baseline_path"])
    need(source_name in originals and baseline_name in baseline,
         "FACTORY_BLUEPRINT")
    raw = decode(originals[source_name], 16 * MIB)
    approved_blueprint = decode(baseline[baseline_name], 16 * MIB)
    blueprint_shape(raw)
    blueprint_shape(approved_blueprint)
    with sibling("frontier-blueprint", "build_blueprint") as bp:
        report = bp.Report()
        # Whole original ancestry is present here. Never shorten src first.
        with validation_input("FACTORY_BLUEPRINT"):
            expected = bp.customer_version(copy.deepcopy(raw), report)
        need(not report.errors and expected == approved_blueprint, "FACTORY_PRIVACY")
    need(any(r["role"] == "blueprint" and r["status"] == "provided" and
             portable(r["source"]["path"]) == source_name and
             portable(r["baseline"]["path"]) == baseline_name
             for r in request["intake"]["artifacts"]), "FACTORY_BLUEPRINT")
    return raw, approved_blueprint

def check_selection(request, customer_blueprint, intake):
    mappings = request["id_map"]
    keys(mappings, ("solutions", "agents", "requirements"))
    for mapping in mappings.values():
        need(isinstance(mapping, dict) and len(set(mapping.values())) == len(mapping),
             "FACTORY_IDS")
        for original, factory in mapping.items():
            text(original)
            identity(factory)
    selected = {r["solution_id"]: r for r in intake["selected_solutions"]}
    need(set(mappings["solutions"].values()) == set(selected), "FACTORY_SCOPE")
    need(set(mappings["agents"].values()) ==
         {a for s in selected.values() for a in s["agent_ids"]}, "FACTORY_SCOPE")
    need(set(mappings["requirements"].values()) == {r["id"] for r in intake["requirements"]},
         "FACTORY_SCOPE")
    agents = {}
    domains = {d["id"] for d in customer_blueprint.get("domains", [])}
    need(set(mappings["solutions"]) <= domains, "FACTORY_SCOPE")
    for domain in customer_blueprint.get("domains", []):
        for agent in [*domain.get("agents", []),
                      *([domain["orchestrator"]] if isinstance(domain.get("orchestrator"), dict) else [])]:
            need(agent["id"] not in agents, "FACTORY_IDS")
            agents[agent["id"]] = domain["id"]
    need(set(mappings["agents"]) <= set(agents), "FACTORY_SCOPE")
    evidence = request["selection_evidence"]
    need(isinstance(evidence, list) and len(evidence) == len(selected), "FACTORY_SCOPE")
    seen = set()
    gaps = {r["id"] for field in ("gaps", "decisions") for r in intake[field]}
    for row in evidence:
        keys(row, ("solution_id", "original_solution_id", "original_agent_ids",
                   "rationale", "dependency_gaps"))
        sid = row["solution_id"]
        need(sid in selected and sid not in seen, "FACTORY_SCOPE")
        seen.add(sid)
        need(mappings["solutions"].get(row["original_solution_id"]) == sid, "FACTORY_SCOPE")
        originals = row["original_agent_ids"]
        need(isinstance(originals, list) and originals and len(set(originals)) == len(originals),
             "FACTORY_SCOPE")
        need(all(a in agents and a in mappings["agents"] for a in originals), "FACTORY_SCOPE")
        need({mappings["agents"][a] for a in originals} == set(selected[sid]["agent_ids"]),
             "FACTORY_SCOPE")
        text(row["rationale"])
        need(isinstance(row["dependency_gaps"], list) and
             set(row["dependency_gaps"]) <= gaps, "FACTORY_SCOPE")

def check_sharing(request, records, baseline, original_blueprint):
    sharing = request["sharing_review"]
    keys(sharing, ("customer_scope", "metadata", "artifacts"))
    need(sharing["customer_scope"] == request["customer_scope"], "FACTORY_TRANSFER")
    approval(sharing["metadata"])
    provided = {r["intake_id"] + ":" + a["id"]
                for r in records for a in r["artifacts"] if a["status"] == "provided"}
    need(set(sharing["artifacts"]) == provided, "FACTORY_TRANSFER")
    for value in sharing["artifacts"].values():
        approval(value)
    # Reuse the existing customer policy to refuse known internal terms in
    # otherwise approved metadata/text. Do not print Report errors or removals.
    terms = original_blueprint.get("meta", {}).get("internal_terms", [])
    payload = {"request": request, "records": records,
               "text": [raw.decode("utf-8") for name, raw in baseline.items()
                        if Path(name).suffix.lower() in {".md", ".txt", ".json", ".csv"}]}
    with sibling("frontier-blueprint", "build_blueprint") as bp:
        report = bp.Report()
        wrapper = {"meta": {"internal_terms": terms}, "payload": copy.deepcopy(payload)}
        with validation_input("FACTORY_PRIVACY"):
            projected = bp.customer_version(wrapper, report)
        need(not report.errors and projected.get("payload") == payload, "FACTORY_PRIVACY")
```

`check_blueprint -> (original, customer_safe)` keeps the original only for
whole-ancestry/privacy/provenance checks. `check_selection` receives only the
approved customer-safe tree. Original domain/agent keys in maps and selected
scope must survive that projection; requirement mappings still refer to the
reviewed authored requirement documents, not guessed keyword matches.
No source or baseline document is rewritten. `validation_input` surrounds
only named existing validation APIs with a documented `ValueError` contract;
`KeyError`, `TypeError`, `AttributeError`, recursion and overflow defects are
not converted to successful-looking ordinary-input diagnostics.

Add behavioural tests **before** implementing each remaining branch:

- Reviewed PRD/design/ADRs and source IDs remain exact bytes, including CRLF
  or non-ASCII; no call to `scaffold_design_docs`, no ID renumbering.
- Two selected solutions sharing a provided file use one destination and
  explicit `solution_ids`; collision or ambiguous mappings fails. Original
  solution/domain/agent IDs and requirement IDs remain in the sidecar.
- No keyword-based MVP inference; source `mvp` flags do not widen selection.
  Explicit out-of-scope dependencies stay named gap IDs in review/manifest.
- Selected `.html`, `.zip`, `.ttl`, `.turtle` and renamed unsupported payload
  attempts fail with ordinary JSON/Markdown equivalent guidance. A ZIP/PDF
  signature mismatch in a claimed text/JSON file fails; do not accept extension
  renaming as a supported equivalent. Office containers remain opaque and
  require their genuine sharing review; this is not semantic DLP.
- All supplied JSON artefacts are strictly decoded even outside blueprint;
  reject duplicate keys, non-finite numbers, invalid UTF-8 and trailing data.
- Missing metadata/file-sharing review, restricted baseline, mixed customer
  scope, internal blueprint ancestry, process-promoted internal material,
  `content_src`, source cycles/unresolved ancestry and private filenames/
  references in metadata fail without leaking them in stdout, manifest or
  previous good output. Use actual process privacy helpers via the blueprint
  check, not a new ontology scrubber.

For text/JSON format checks, add this complete function, then call it on every
current and historical baseline file before sharing validation:

```python
def check_ordinary(name, raw):
    suffix = Path(name).suffix.lower()
    need(suffix in {".md", ".txt", ".json", ".pdf", ".docx", ".xlsx", ".pptx", ".csv"},
         "FACTORY_FORMAT")
    if suffix in {".md", ".txt", ".json", ".csv"}:
        need(not raw.startswith((b"PK\x03\x04", b"%PDF-")), "FACTORY_FORMAT")
        try:
            text_value = raw.decode("utf-8")
        except UnicodeError:
            raise FactoryError("FACTORY_FORMAT") from None
        need("\x00" not in text_value, "FACTORY_FORMAT")
        if suffix == ".json":
            decode(raw, 16 * MIB)
        need(not text_value.lstrip().lower().startswith(("<!doctype html", "<html")),
             "FACTORY_FORMAT")
```

This is signature/format validation, not a claim that arbitrary renamed or
opaque content can be semantically certified. Human exact-file review remains
mandatory. The exporter never rewrites an authored document to make it pass.

Create `tests/unit/test_factory_privacy.py` with this executable regression
kernel. Add the listed process/transitive-ancestry cases to this same class
against the existing process examples/helpers, never a competing scrubber:

```python
import copy
import json
import tempfile
import unittest
from pathlib import Path
from tests.factory_fixture import approved, encode, prepare, save
from tests.unit.test_factory_export import FactoryExport

class FactoryPrivacy(unittest.TestCase):
    invoke = FactoryExport.invoke

    def test_internal_content_and_metadata_are_refused_without_leakage(self):
        for case in ("internal-agent", "content-src", "private-metadata", "scope"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as d:
                f = prepare(Path(d))
                request = f["request"]
                bp = json.loads((f["source"] / "blueprint.json").read_bytes())
                row = next(r for r in request["intake"]["artifacts"] if r["role"] == "blueprint")
                baseline_path = f["baseline"] / row["baseline"]["path"]
                if case == "scope":
                    request["sharing_review"]["customer_scope"] = "Different synthetic scope"
                elif case == "private-metadata":
                    bp["meta"]["internal_terms"] = ["private-fixture-token"]
                    (f["source"] / "blueprint.json").write_bytes(encode(bp))
                    row["transformation"] = {"kind": "redaction", "rationale": "Reviewed source envelope removal.",
                                              "approval": approved()}
                    request["intake"]["source"]["references"] = ["private-fixture-token"]
                else:
                    agent = bp["domains"][0]["agents"][0]
                    if case == "internal-agent":
                        agent["internal"] = True
                    else:
                        bp["evidence"] = [{"id": "public-e", "visibility": "public"},
                                          {"id": "private-e", "visibility": "internal"}]
                        agent.update(src=["public-e"], content_src=["private-e"])
                    # Bytes are genuinely unchanged source -> baseline, but not safe to transfer.
                    (f["source"] / "blueprint.json").write_bytes(encode(bp))
                    baseline_path.write_bytes(encode(bp))
                save(f)
                f["out"].write_bytes(b"old-good")
                code, result = self.invoke(f)
                self.assertEqual(code, 1)
                self.assertNotIn("private-fixture-token", json.dumps(result))
                self.assertEqual(f["out"].read_bytes(), b"old-good")

    def test_renamed_binary_is_not_an_ordinary_text_equivalent(self):
        for raw in (b"PK\x03\x04synthetic", b"%PDF-1.7\nsynthetic", b"<html>synthetic</html>"):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as d:
                f = prepare(Path(d))
                row = f["request"]["intake"]["artifacts"][0]
                (f["source"] / "prd.md").write_bytes(raw)
                (f["baseline"] / row["baseline"]["path"]).write_bytes(raw)
                f["out"].write_bytes(b"old-good")
                self.assertEqual(self.invoke(f)[0], 1)
                self.assertEqual(f["out"].read_bytes(), b"old-good")

    def test_removed_original_agent_cannot_enter_selection_or_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            request = f["request"]
            original = json.loads((f["source"] / "blueprint.json").read_bytes())
            original["domains"][0]["agents"][0]["internal"] = True
            approved_blueprint = copy.deepcopy(original)
            approved_blueprint["domains"][0]["agents"] = []
            row = next(r for r in request["intake"]["artifacts"] if r["role"] == "blueprint")
            source_path = f["source"] / "blueprint.json"
            baseline_path = f["baseline"] / row["baseline"]["path"]
            source_path.write_bytes(encode(original))
            baseline_path.write_bytes(encode(approved_blueprint))
            row["transformation"] = {"kind": "redaction", "rationale": "Synthetic approved private-agent removal.",
                                      "approval": approved()}
            # The frozen input still selects/maps D1-A01, which is not present
            # in the valid customer-safe projection. No silent ID rewriting.
            save(f)
            before = (source_path.read_bytes(), baseline_path.read_bytes())
            f["out"].write_bytes(b"old-good")
            code, result = self.invoke(f)
            self.assertEqual(code, 1)
            self.assertEqual(result["error"], "FACTORY_SCOPE")
            self.assertNotIn("D1-A01", json.dumps(result))
            self.assertEqual(f["out"].read_bytes(), b"old-good")
            self.assertEqual(before, (source_path.read_bytes(), baseline_path.read_bytes()))
```

## 10. Task 8 — W3 immutable history and complete assembly

Add tests for historical raw-record and artefact byte preservation, collision
with current record, source/baseline digest separation, output inventory
excluding its own manifest hash, and no generated runtime/unit trees.
Run `python -m unittest tests.unit.test_factory_export -v` to observe RED.

In `factory_projection.py` add these complete history/assembly functions:

```python
def load_history(ids, baseline_root, schema, validate):
    need(isinstance(ids, list) and len(ids) <= 127 and len(set(ids)) == len(ids),
         "FACTORY_HISTORY")
    records, files, raw_records = {}, {}, {}
    spellings = {}
    remaining = 128 * MIB
    for old_id in ids:
        identity(old_id)
        name = f"docs/intake/records/{old_id}/intake.json"
        raw = read(baseline_root, name, min(MIB, remaining))
        remaining -= len(raw)
        record = decode(raw)
        need(conforms(schema, record) and record["intake_id"] == old_id and
             record["review"]["status"] == "accepted",
             "FACTORY_HISTORY")
        records[old_id], raw_records[name] = record, raw
        for row in record["artifacts"]:
            if row["status"] == "provided":
                raw_path = row["baseline"]["path"]
                name = claim_path(spellings, raw_path)
                files[name] = read(baseline_root, raw_path, min(16 * MIB, remaining))
                remaining -= len(files[name])
    for record in records.values():
        validate(record, schema, files, history=records)
    return records, files, raw_records

def assemble(request, foundation, intake, baseline, history_raw, producer_version,
             financial_status):
    entries = dict(foundation)
    def add(name, raw):
        name = portable(name)
        need(path_key(name) not in {path_key(key) for key in entries}, "FACTORY_COLLISION")
        entries[name] = (raw, 0o644)
    for name, raw in {**baseline, **history_raw}.items():
        add(name, raw)
    record_path = f"docs/intake/records/{intake['intake_id']}"
    add(record_path + "/intake.json", encoded(intake))
    synthetic = request["evidence_kind"] == "synthetic-compatibility"
    boundary = ("Synthetic compatibility fixture; no real approval or customer transfer."
                if synthetic else
                "Externally recorded evidence; reviewer identity is not authenticated by export.")
    review = (
        "# Intake review\n\n" + boundary + "\n\n"
        "Disposition: " + intake["review"]["status"] + ".\n\n"
        "No build, budget, repository, tenant or deployment permission is granted.\n\n"
        "Selected scope, requirement mappings, gaps and decisions:\n\n```json\n" +
        encoded({k: intake[k] for k in ("selected_solutions", "requirements", "gaps", "decisions")})
        .decode("utf-8") + "```\n")
    add(record_path + "/review.md", review.encode("utf-8"))
    start = (
        "# Start here\n\nEnvisioning Agent Factory — optional Preview.\n\n" + boundary + "\n\n"
        "This is preserved repository source and reviewed ordinary-file intake, not an application.\n\n"
        f"Read `{record_path}/review.md` and `{record_path}/intake.json`.\n\n"
        "In a separately prepared receiving environment run:\n\n"
        "```powershell\n"
        "python -m tools.intake validate " + record_path.replace("/", "\\") + "\\intake.json\n"
        "```\n\n"
        "That baseline-only check does not verify original files. Use `--source-root` "
        "with separately retained originals for the stronger check.\n\n"
        "Receiver validation during export: not performed. Cowork discovery, install, "
        "acquisition and export: not performed. No native ADO/GHES support is certified.\n\n"
        "Resolve named engineering gaps and obtain actual receiving-owner review before "
        "creating solution units. Tenant prerequisites, settings, credentials, consent, "
        "runtime choice and deployment remain governed human work.\n")
    add("START_HERE.md", start.encode("utf-8"))
    manifest = {
        "schema": "frontier-agent-factory-handover/1.0",
        "producer": {"name": "frontier-agent-factory", "plugin_version": producer_version},
        "export_id": request["export_id"], "intake_id": intake["intake_id"],
        "created_at": request["created_at"], "customer_scope": request["customer_scope"],
        "evidence_kind": request["evidence_kind"], "template": request["template"],
        "compatibility_profile": "frontier-agent-factory-template-profile/1.0",
        "id_map": request["id_map"], "selection_evidence": request["selection_evidence"],
        "artifacts": intake["artifacts"], "gaps": intake["gaps"], "decisions": intake["decisions"],
        "sharing_review": request["sharing_review"],
        "exclusion_policy": "Only explicitly selected, approved material; withheld details are not recorded.",
        "validation": {"producer": "passed", "intake_disposition": intake["review"]["status"],
                       "receiver": "not-performed", "cowork": "not-performed",
                       "reviewer_authentication": "not-performed",
                       "tenant_readiness": "not-assessed", "financial": financial_status},
        "inventory": {name: {"sha256": digest(raw), "bytes": len(raw), "mode": mode}
                      for name, (raw, mode) in sorted(entries.items())}}
    add("handover/manifest.json", encoded(manifest))
    return entries
```

The `baseline` argument is the collision-checked union of current and historical
provided files; never use dictionary unpacking to conceal a duplicate between
them. Before `assemble`, require `set(current).isdisjoint(history_files)` and
the same check for history JSON destinations. The raw original documents
remain in excluded source staging, not copied into another bypass directory.
No prior `review.md` is overwritten: the history input transfers accepted
`intake.json` and provided artefacts only; a separately selected old review is
ordinary reviewed evidence or is left in its original repository.

The projection import includes `conforms` for the history schema preflight.
Materialisation enforces the shared 64 MiB
while reading, not after buffering potentially gigabytes. History ingestion
also has a running 128 MiB ceiling before final whole-repository capacity
checks; it cannot collect 127 independently oversized histories first.
The final 128 MiB limit still includes foundation and every generated file.

All `baseline`, `originals` and history-file map keys are `portable(path)`.
Record lookups and blueprint descriptors use that same function; protected
inputs use `parts`, and collision/union checks use `path_key`. Raw accepted
JSON and its Windows path strings are retained byte-for-byte, not serialised
again to change separators. Add the actual upstream Windows-path history
receiver regression in Task 13 and the mixed-slash CLI regression in Task 10.

## 11. Task 9 — W3 optional financial evidence, no automatic money operation

Add `tests/unit/test_factory_finops.py` before code:

1. Mock `factory_projection.sibling` with a wrapper that raises if asked for
   `frontier-finops`; export ordinary core and ordinary value successfully.
   Also extract the plugin, remove the unrequested optional FinOps folder in
   the isolated installed fixture, and export core successfully.
2. A provided `finops` row, a declared financial packet, a known baseline/report
   schema, embedded legacy `finops_preview`/cost lineage or cost-derived value
   without a current invocation acknowledgement fails **before** output effects.
   Cached acknowledgement and forged GA metadata do not satisfy it.
3. Requested-but-missing optional skill fails explicitly; declined or unavailable
   unrequested work stays ordinary review with named financial gaps, not zeros.
4. Exercise actual `value_calc.has_finops_dependency`, `preview_for`,
   `finops_preview.validate_finops_results`, `validate_value_results` and
   `baseline_projection.project` on synthetic existing example-derived inputs.
   For fixture preparation only, explicitly call existing `baseline_calc.calculate`
   with its authored as-of date and technical acknowledgement. Production export
   never seeds, migrates, freezes, records review, invokes a calculator command,
   alters a financial record or manufactures financial approval.
5. An actual draft baseline projection remains blocked/not ready, retains the
   full notice, and cannot satisfy an explicit financial build-handover claim.
   Test mismatched report bytes, stale/replaced snapshot/review, private customer
   scope, withheld projection and synthetic financial approval. Only an actual
   complete strict existing handover result may support a planning-ready claim;
   still `financial_permission` is false.

Financial packet fields are exactly
`artifact_ids`, `kind`, `model_path`, `review_paths`, `owner_review`.
Packet artefact IDs use the same qualified `<intake-id>:<artifact-id>` keys
as sharing review, so historical and current IDs cannot shadow one another.
`kind` is `baseline` or `reviewed-document`. Baseline means an explicitly supplied
authoritative calculated baseline/frozen snapshot plus matching reviews, not an
imported report as authority. `reviewed-document` covers already authored legacy
or opaque financial evidence without inventing automated financial readiness.
All financial/derived artefacts must be covered once; packet files are read-only
local verification inputs and are not automatically transferred.

Implement this complete function in `factory_projection.py`:

```python
def financial_check(request, records, baseline, source_root, acknowledged):
    import datetime as dt
    import re
    finance = request["financial"]
    keys(finance, ("requested", "as_of", "claim", "packets"))
    need(type(finance["requested"]) is bool and finance["claim"] in {"review", "build-handover"})
    by_id = {record["intake_id"] + ":" + row["id"]: row
             for record in records for row in record["artifacts"] if row["status"] == "provided"}
    financial_ids = {key for key, row in by_id.items() if row["role"] == "finops"}
    json_documents = {}
    with sibling("frontier-value-case", "value_calc") as value:
        for qualified_id, row in by_id.items():
            path = portable(row["baseline"]["path"])
            if Path(path).suffix.lower() != ".json":
                continue
            document = decode(baseline[path], 16 * MIB)
            json_documents[qualified_id] = document
            schema = document.get("schema", "") if isinstance(document, dict) else ""
            if value.has_finops_dependency(document) or str(schema).startswith(
                    ("frontier-finops/", "frontier-finops-", "frontier-agent-finops-")):
                financial_ids.add(qualified_id)
            if qualified_id in financial_ids:
                need(isinstance(document, dict), "FACTORY_FINOPS_EVIDENCE")
    if not finance["requested"]:
        need(not financial_ids and not finance["packets"] and finance["as_of"] is None and
             finance["claim"] == "review", "FACTORY_FINOPS_ACK")
        return "not-requested"
    need(acknowledged is True, "FACTORY_FINOPS_ACK")
    need(isinstance(finance["as_of"], str) and
         re.fullmatch(r"\d{4}-\d{2}-\d{2}", finance["as_of"]), "FACTORY_FINOPS_DATE")
    try:
        day = dt.date.fromisoformat(finance["as_of"])
    except ValueError:
        raise FactoryError("FACTORY_FINOPS_DATE") from None
    need(isinstance(finance["packets"], list) and 0 < len(finance["packets"]) <= 256,
         "FACTORY_FINOPS_EVIDENCE")
    covered, all_ready = set(), True
    with sibling("frontier-finops", "finops_preview") as preview:
        preview.require_preview_ack(acknowledged)
        for packet in finance["packets"]:
            keys(packet, ("artifact_ids", "kind", "model_path", "review_paths", "owner_review"))
            ids = packet["artifact_ids"]
            need(isinstance(ids, list) and ids and len(ids) == len(set(ids)) and
                 set(ids) <= set(by_id) and not set(ids) & covered, "FACTORY_FINOPS_EVIDENCE")
            covered.update(ids)
            approval(packet["owner_review"])
            if packet["kind"] == "baseline":
                model = decode(read(source_root, packet["model_path"], 16 * MIB), 16 * MIB)
                need(isinstance(model, dict), "FACTORY_FINOPS_EVIDENCE")
                need(isinstance(packet["review_paths"], list), "FACTORY_FINOPS_EVIDENCE")
                reviews = [decode(read(source_root, p, MIB)) for p in packet["review_paths"]]
                need(all(isinstance(review, dict) for review in reviews), "FACTORY_FINOPS_EVIDENCE")
                with sibling("frontier-finops", "baseline_projection") as projector:
                    with validation_input("FACTORY_FINOPS_EVIDENCE"):
                        report = projector.project(model, reviews, as_of=day, audience="customer",
                                                   customer_scope=request["customer_scope"],
                                                   acknowledge_finops_preview=True)
                    need(report.get("mode") != "withheld" and
                         report.get("handover", {}).get("status") != "withheld", "FACTORY_PRIVACY")
                    for artifact_id in ids:
                        name = portable(by_id[artifact_id]["baseline"]["path"])
                        raw = baseline[name]
                        suffix = Path(name).suffix.lower()
                        need((suffix == ".json" and decode(raw, 16 * MIB) == report) or
                             (suffix == ".md" and raw == projector.render_markdown(report).encode("utf-8")),
                             "FACTORY_FINOPS_EVIDENCE")
                    all_ready = all_ready and report["handover"]["ready"] is True
            else:
                need(packet["kind"] == "reviewed-document" and packet["model_path"] is None and
                     packet["review_paths"] == [], "FACTORY_FINOPS_EVIDENCE")
                all_ready = False  # Human-reviewed evidence is not automated financial certification.
                for artifact_id in ids:
                    doc = json_documents.get(artifact_id)
                    if not isinstance(doc, dict):
                        continue  # Opaque/Markdown sharing review is explicit, not semantic DLP.
                    need(not str(doc.get("schema", "")).startswith(
                        ("frontier-finops-", "frontier-agent-finops-")),
                        "FACTORY_FINOPS_EVIDENCE")
                    if str(doc.get("schema", "")).startswith("frontier-finops/"):
                        need(isinstance(doc.get("agents"), list) and all(
                            isinstance(agent, dict) and isinstance(agent.get("id"), str)
                            for agent in doc["agents"]), "FACTORY_FINOPS_EVIDENCE")
                        with validation_input("FACTORY_FINOPS_EVIDENCE"):
                            preview.validate_finops_results(doc, acknowledge_finops_preview=True)
                    with sibling("frontier-value-case", "value_calc") as value:
                        if value.has_finops_dependency(doc) and not str(
                                doc.get("schema", "")).startswith("frontier-finops/"):
                            with validation_input("FACTORY_FINOPS_EVIDENCE"):
                                value.preview_for(doc, acknowledge_finops_preview=True,
                                                  operation="apply-value")
    need(financial_ids <= covered, "FACTORY_FINOPS_EVIDENCE")
    if finance["claim"] == "build-handover":
        need(all_ready, "FACTORY_FINANCIAL_HANDOVER")
    return "planning-ready-not-financial-permission" if all_ready else "review-only-financial-gaps"
```

`project` internally recomputes/validates existing receipts under the explicitly
requested acknowledged verification action. It is not an implicit new estimate
or a side-effect calculator chain. Carry its exact notice/limitations; do not
write recalculated models. For financial opaque/legacy documents preserve actual
reviewed bytes and limitations; no automatic build-ready certification is added.
If the exact existing Markdown renderer has a different terminal-newline
convention, test and use its **actual returned bytes**, not a guessed normaliser.

Before GREEN add tests for baseline/report/view documents in
`reviewed-document` packets: derivative reports cannot bypass authoritative
baseline verification by choosing that kind. Supplied financial JSON
must be an object. Add non-finite `as_of`, ambiguous packet coverage
and review scope tests. Do not infer a current scenario acknowledgement from
`requested: true`. Scan current **and historical** supplied records; an old
financial packet does not silently become unacknowledged core content.

Executable initial `tests/unit/test_factory_finops.py`:

```python
import contextlib
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from tests.factory_fixture import approved, encode, prepare, save
from tests.unit._util import ROOT, load
from tests.unit.test_factory_export import FactoryExport

class FactoryFinancial(unittest.TestCase):
    invoke = FactoryExport.invoke

    def test_core_does_not_load_optional_finops(self):
        m = load("plugin/skills/frontier-agent-factory/scripts/factory_projection.py")
        real_sibling = m.sibling
        @contextlib.contextmanager
        def core_only(skill, module):
            self.assertNotEqual(skill, "frontier-finops")
            with real_sibling(skill, module) as library:
                yield library
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            baseline = {r["baseline"]["path"]: (f["baseline"] / r["baseline"]["path"]).read_bytes()
                        for r in f["request"]["intake"]["artifacts"] if r["status"] == "provided"}
            with mock.patch.object(m, "sibling", core_only):
                result = m.financial_check(f["request"], [f["request"]["intake"]], baseline,
                                           f["source"], False)
            self.assertEqual(result, "not-requested")

    def test_requested_document_requires_current_ack_and_is_not_build_ready(self):
        m = load("plugin/skills/frontier-agent-factory/scripts/factory_projection.py")
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            request = f["request"]
            record = request["intake"]
            baseline = {r["baseline"]["path"]: (f["baseline"] / r["baseline"]["path"]).read_bytes()
                        for r in record["artifacts"] if r["status"] == "provided"}
            row = next(r for r in record["artifacts"] if r["role"] == "finops")
            row.update(status="provided", baseline={"path": "costs.md"})
            request["financial"] = {
                "requested": True, "as_of": "2026-11-25", "claim": "review",
                "packets": [{"artifact_ids": ["caldova-intake:finops"],
                             "kind": "reviewed-document", "model_path": None,
                             "review_paths": [], "owner_review": approved()}]}
            baseline["costs.md"] = b"# Synthetic reviewed planning evidence\n"
            with self.assertRaisesRegex(ValueError, "FACTORY_FINOPS_ACK"):
                m.financial_check(request, [record], baseline, f["source"], False)
            self.assertEqual(m.financial_check(request, [record], baseline, f["source"], True),
                             "review-only-financial-gaps")
            request["financial"]["claim"] = "build-handover"
            with self.assertRaisesRegex(ValueError, "FACTORY_FINANCIAL_HANDOVER"):
                m.financial_check(request, [record], baseline, f["source"], True)

    def test_legacy_financial_schema_under_another_role_still_requires_ack(self):
        import copy
        m = load("plugin/skills/frontier-agent-factory/scripts/factory_projection.py")
        legacy = {"schema": "frontier-finops/1.0", "agents": []}
        with m.sibling("frontier-value-case", "value_calc") as value:
            self.assertTrue(value.has_finops_dependency(legacy))  # Actual shared helper.
            self.assertFalse(value.has_finops_dependency(
                {"schema": "frontier-value/1.0", "assumptions": []}))
        for schema, expected in (("frontier-finops/1.0", 1), ("frontier-value/1.0", 0)):
            with self.subTest(schema=schema), tempfile.TemporaryDirectory() as d:
                f = prepare(Path(d))
                r = f["request"]
                row = next(item for item in r["intake"]["artifacts"] if item["role"] == "value")
                provided = copy.deepcopy(r["intake"]["artifacts"][0])
                provided.update(id=row["id"], role="value")
                provided["source"]["path"] = "value-context.json"
                provided["baseline"]["path"] = "docs/intake/records/caldova-intake/artifacts/value-context.json"
                row.clear()
                row.update(provided)
                raw = encode({"schema": schema, "agents": [], "assumptions": []})
                (f["source"] / "value-context.json").write_bytes(raw)
                (f["baseline"] / row["baseline"]["path"]).write_bytes(raw)
                r["sharing_review"]["artifacts"]["caldova-intake:value"] = approved()
                save(f)
                code, summary = self.invoke(f)
                self.assertEqual(code, expected)
                if expected:
                    self.assertEqual(summary["error"], "FACTORY_FINOPS_ACK")
                else:
                    self.assertEqual(summary["financial"], "not-requested")

    def test_derivative_json_cannot_bypass_authority_as_reviewed_document(self):
        m = load("plugin/skills/frontier-agent-factory/scripts/factory_projection.py")
        with tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            request, record = f["request"], f["request"]["intake"]
            baseline = {r["baseline"]["path"]: (f["baseline"] / r["baseline"]["path"]).read_bytes()
                        for r in record["artifacts"] if r["status"] == "provided"}
            row = next(r for r in record["artifacts"] if r["role"] == "value")
            row.update(status="provided", baseline={"path": "report.json"})
            baseline["report.json"] = encode({"schema": "frontier-agent-finops-report/1.0"})
            request["financial"] = {
                "requested": True, "as_of": "2026-11-25", "claim": "review",
                "packets": [{"artifact_ids": ["caldova-intake:value"], "kind": "reviewed-document",
                             "model_path": None, "review_paths": [], "owner_review": approved()}]}
            with self.assertRaisesRegex(ValueError, "FACTORY_FINOPS_EVIDENCE"):
                m.financial_check(request, [record], baseline, f["source"], True)

    def test_actual_existing_baseline_projection_does_not_promote_a_draft(self):
        m = load("plugin/skills/frontier-agent-factory/scripts/factory_projection.py")
        model = json.loads((ROOT / "plugin/skills/frontier-finops/examples/caldova-agent-baseline.json").read_bytes())
        day = dt.date.fromisoformat(model["baseline"]["as_of"])
        with m.sibling("frontier-finops", "baseline_calc") as calculator:
            calculated = calculator.calculate(model, as_of=day, acknowledge_finops_preview=True)
        with m.sibling("frontier-finops", "baseline_projection") as projector:
            report = projector.project(calculated, as_of=day, audience="customer",
                                       customer_scope=model.get("customer_scope"),
                                       acknowledge_finops_preview=True)
        self.assertIs(report["financial_permission"], False)
        self.assertIs(report["handover"]["ready"], False)
        self.assertIn("Preview", report["notice"])
```

The first test uses the same provided-byte map the exporter passes; no
financial operation is requested.
Add recognition tests for hidden/cached legacy lineage and derivative reports
one at a time before GREEN. Test fixtures can calculate explicitly to prepare
inputs; the exporter cannot silently calculate for ordinary core work.

## 12. Task 10 — W3 complete CLI, no output effect before validation

Implement F `scripts/export_factory.py` with this complete entry point.
Keep the fixed public usage contract and catch only bounded standard failures,
not `BaseException` or silent success.

```python
from __future__ import annotations
import argparse
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factory_common import (FactoryError, MIB, decode, digest,
                            need, parts, path_key, plain_path, read)
from factory_contract import materialize, prevalidate_request, source_receipt, validate_intake
from factory_archive import archive_bytes, foundation, publish
from factory_projection import (assemble, check_blueprint, check_ordinary, check_selection,
                                check_sharing, financial_check, load_history, sibling)

REFERENCES = Path(__file__).resolve().parents[1] / "references"

GUIDANCE = {
    "FACTORY_REQUEST_SHAPE": "Supply the documented request object and nested field types; missing engineering material must be declared as gaps, not malformed objects.",
    "FACTORY_DISCOVERY": "Obtain a successful complete latest-stable lookup through an authorised host; access/network errors are not absence.",
    "FACTORY_SOURCE": "Use the exact discovered stable release/tag/commit; do not select a different source or floating branch.",
    "FACTORY_BOOTSTRAP": "After a healthy no-stable-release lookup, record actual approval of the exact immutable unreleased commit.",
    "FACTORY_ACQUISITION": "Supply actual exact-source bytes and their acquisition receipt through an available authorised host or explicit local-source input.",
    "FACTORY_COMPATIBILITY": "The selected source does not match the supported intake profile; report this compatibility gap without falling back.",
    "FACTORY_TRANSFER": "Obtain actual scope, classification, destination and sharing/transfer review for every provided file and exported metadata.",
    "FACTORY_PRIVACY": "Supply separately reviewed customer-safe bytes with intact original ancestry and any actual transformation approval.",
    "FACTORY_FINOPS_ACK": "Use clean ordinary core inputs, or obtain current-scenario FinOps Preview acknowledgement before explicitly requested financial verification.",
    "FACTORY_FINANCIAL_HANDOVER": "Financial evidence is not planning-ready under the existing strict handover contract; retain the named financial gaps.",
    "FACTORY_OPTIONAL_SKILL": "Install the explicitly requested sibling skill next to Factory, or resolve the selected scope; do not claim the missing operation succeeded.",
    "FACTORY_LIMIT": "Selected bytes exceed a documented template, receiver or final-repository limit; reduce scope or obtain supported reviewed equivalents without silent omission.",
}

class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise FactoryError("FACTORY_USAGE")

def protect_output(output, inputs, roots):
    """Portable aliases and existing hardlinks cannot replace any input."""
    output = plain_path(output, missing=True)
    target = output.as_posix().casefold()
    need(output.parent.is_dir() and (not output.exists() or output.is_file()), "FACTORY_OUTPUT")
    for root in roots:
        parent = root.as_posix().casefold().rstrip("/")
        need(target != parent and not target.startswith(parent + "/") and
             not parent.startswith(target.rstrip("/") + "/"), "FACTORY_OUTPUT")
    for source in inputs:
        source = plain_path(source)
        need(target != source.as_posix().casefold(), "FACTORY_OUTPUT")
        if output.exists():
            need(not os.path.samefile(output, source), "FACTORY_OUTPUT")

def main(argv=None):
    try:
        parser = Parser(description="Prepare an offline Preview factory review repository.")
        for name in ("request", "template", "source-root", "baseline-root", "out"):
            parser.add_argument("--" + name, required=True, type=Path)
        parser.add_argument("--acknowledge-finops-preview", action="store_true")
        args = parser.parse_args(argv)
        inputs = [plain_path(args.request), plain_path(args.template)]
        source_root, baseline_root = plain_path(args.source_root), plain_path(args.baseline_root)
        output = plain_path(args.out, missing=True)
        need(source_root.is_dir() and baseline_root.is_dir(), "FACTORY_PATH")
        protect_output(output, inputs, (source_root, baseline_root))
        request = decode(read(args.request.parent, args.request.name, MIB))
        profile = decode(read(REFERENCES, "template-profile.json", MIB))
        schema_bytes = read(REFERENCES, "intake.schema.json", MIB)
        need(digest(schema_bytes) == profile["intake_schema_sha256"], "FACTORY_COMPATIBILITY")
        schema = decode(schema_bytes)
        prevalidate_request(request, schema)
        template = read(args.template.parent, args.template.name, 32 * MIB)
        source_receipt(request["template"], request["export_id"], request["created_at"], template)
        base = foundation(template, request["template"]["root_prefix"], profile)
        old, old_files, old_raw = load_history(request["history"], baseline_root,
                                              schema, validate_intake)
        intake, current, originals = materialize(request["intake"], baseline_root, source_root, read)
        need(intake["intake_id"] not in old and
             {path_key(p) for p in current}.isdisjoint(path_key(p) for p in old_files) and
             {path_key(p) for p in current}.isdisjoint(path_key(p) for p in old_raw),
             "FACTORY_HISTORY")
        validate_intake(intake, schema, current, originals, old)
        all_files = {**old_files, **current}
        for name, raw in all_files.items():
            check_ordinary(name, raw)
        # Set the materialised record only on a detached request copy.
        request = dict(request, intake=intake)
        original_blueprint, customer_blueprint = check_blueprint(request, current, originals)
        check_selection(request, customer_blueprint, intake)
        check_sharing(request, [*old.values(), intake], all_files, original_blueprint)
        financial = financial_check(request, [*old.values(), intake], all_files, source_root,
                                     args.acknowledge_finops_preview)
        protected = [*inputs,
                     *(baseline_root.joinpath(*parts(p)) for p in all_files),
                     *(baseline_root.joinpath(*parts(p)) for p in old_raw),
                     *(source_root.joinpath(*parts(p)) for p in originals)]
        for packet in request["financial"]["packets"]:
            if packet["model_path"] is not None:
                protected.append(source_root.joinpath(*parts(packet["model_path"])))
            protected.extend(source_root.joinpath(*parts(p)) for p in packet["review_paths"])
        protect_output(output, protected, (source_root, baseline_root))
        with sibling("frontier-blueprint", "build_blueprint") as blueprint:
            producer_version = blueprint.PLUGIN_VERSION
        entries = assemble(request, base, intake, all_files, old_raw, producer_version, financial)
        raw = archive_bytes(entries, request["created_at"])
        # All validation and bytes exist before the first publication effect.
        publish(output, raw)
        import json
        print(json.dumps({"export_validation": "passed", "plugin_version": producer_version,
                          "zip_sha256": digest(raw), "intake_disposition": intake["review"]["status"],
                          "receiver_validation": "not-performed", "cowork_validation": "not-performed",
                          "tenant_readiness": "not-assessed", "financial": financial,
                          "evidence_kind": request["evidence_kind"]}, ensure_ascii=False))
        return 0
    except (FactoryError, OSError) as error:
        import json
        code = str(error) if isinstance(error, FactoryError) else "FACTORY_IO"
        if not code.startswith("FACTORY_") or not code.replace("_", "").isupper():
            code = "FACTORY_INPUT"
        print(json.dumps({"error": code,
                          "guidance": GUIDANCE.get(code, "Supply acquired, scope/transfer-reviewed ordinary files. "
                                      "Use reviewed JSON/Markdown equivalents for HTML, ZIP or Turtle; "
                                      "do not rename, omit or relocate unsupported selected content.")}))
        return 2 if code == "FACTORY_USAGE" else 1

if __name__ == "__main__":
    sys.exit(main())
```

Add output-alias tests using case-folded absolute paths and hardlinks before
implementing `protect_output`. It holds the full selected/history/financial
read-only input inventory, including request/template, during preflight.
This prevents replacement through a syntactically different root. Do not
claim that `Path.resolve` alone detects hardlinks. The union of file maps is
made only after explicit disjointness checks.

Add these complete methods to `FactoryExport`. Shape failures must happen
before source/materialisation/sibling work; injected programming defects must
escape instead of being labelled malformed customer input:

```python
def test_malformed_nested_shapes_have_safe_nonzero_diagnostics_before_work(self):
    from unittest import mock
    cases = [
        ((), []), (("intake",), []), (("intake", "artifacts"), {}),
        (("intake", "artifacts", 0, "source"), ["private-fixture-token"]),
        (("intake", "selected_solutions", 0, "owners"), []),
        (("blueprint", "source_path"), ["private-fixture-token"]),
        (("id_map", "agents"), {"private-fixture-token": []}),
        (("sharing_review", "artifacts"), {"caldova-intake:prd": []}),
        (("template", "discovery", "releases"), [None]),
        (("financial", "packets"), [None])]
    for path, value in cases:
        with self.subTest(path=path), tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            if path:
                target = f["request"]
                for component in path[:-1]:
                    target = target[component]
                target[path[-1]] = value
            else:
                f["request"] = value
            save(f)
            f["out"].write_bytes(b"old-good")
            m = load("plugin/skills/frontier-agent-factory/scripts/export_factory.py")
            args = ["--request", str(f["request_file"]), "--template", str(f["template"]),
                    "--source-root", str(f["source"]), "--baseline-root", str(f["baseline"]),
                    "--out", str(f["out"])]
            stream = io.StringIO()
            with mock.patch.object(m, "source_receipt", side_effect=AssertionError("shape must be first")), \
                 mock.patch.object(m, "materialize", side_effect=AssertionError("shape must be first")), \
                 mock.patch.object(m, "sibling", side_effect=AssertionError("shape must be first")), \
                 contextlib.redirect_stdout(stream):
                code = m.main(args)
            self.assertEqual(code, 1)
            self.assertTrue(json.loads(stream.getvalue())["error"].startswith("FACTORY_"))
            self.assertNotIn("private-fixture-token", stream.getvalue())
            self.assertEqual(f["out"].read_bytes(), b"old-good")

def test_programming_exceptions_are_not_reclassified_as_input(self):
    from unittest import mock
    for failure in (KeyError, TypeError, AttributeError, RecursionError, OverflowError):
        with self.subTest(failure=failure.__name__), tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            m = load("plugin/skills/frontier-agent-factory/scripts/export_factory.py")
            args = ["--request", str(f["request_file"]), "--template", str(f["template"]),
                    "--source-root", str(f["source"]), "--baseline-root", str(f["baseline"]),
                    "--out", str(f["out"])]
            f["out"].write_bytes(b"old-good")
            with mock.patch.object(m, "materialize", side_effect=failure("injected producer defect")), \
                 self.assertRaises(failure):
                m.main(args)
            self.assertEqual(f["out"].read_bytes(), b"old-good")

def test_mixed_slash_baseline_alias_never_replaces_output(self):
    import copy
    from tests.factory_fixture import approved
    with tempfile.TemporaryDirectory() as d:
        f = prepare(Path(d))
        row = copy.deepcopy(f["request"]["intake"]["artifacts"][0])
        row["id"] = "aliased-prd"
        row["baseline"]["path"] = row["baseline"]["path"].replace("/", "\\")
        f["request"]["intake"]["artifacts"].append(row)
        f["request"]["sharing_review"]["artifacts"]["caldova-intake:aliased-prd"] = approved()
        save(f)
        f["out"].write_bytes(b"old-good")
        code, result = self.invoke(f)
        self.assertEqual(code, 1)
        self.assertEqual(result["error"], "FACTORY_COLLISION")
        self.assertEqual(f["out"].read_bytes(), b"old-good")
```

Add complete failure-preserves-output loop to `FactoryExport`:

```python
def test_bad_selected_evidence_never_replaces_output_or_leaks_private_tokens(self):
    from tests.factory_fixture import encode
    cases = ("transfer", "owner", "acquisition", "private-name", "unsupported")
    for case in cases:
        with self.subTest(case=case), tempfile.TemporaryDirectory() as d:
            f = prepare(Path(d))
            r = f["request"]
            if case == "transfer":
                r["intake"]["transfer"]["approval"] = None
            elif case == "owner":
                r["intake"]["selected_solutions"][0]["owners"] = []
            elif case == "acquisition":
                r["template"]["acquisition"]["status"] = "failed"
            elif case == "private-name":
                original = f["source"] / "blueprint.json"
                bp = json.loads(original.read_bytes())
                bp["meta"]["internal_terms"] = ["private-fixture-token"]
                original.write_bytes(encode(bp))
                r["intake"]["source"]["references"] = ["private-fixture-token"]
            else:
                r["intake"]["artifacts"][0]["source"]["path"] = "selected.html"
                (f["source"] / "selected.html").write_bytes(b"<html>not an equivalent</html>")
            save(f)
            f["out"].write_bytes(b"old-good")
            code, result = self.invoke(f)
            self.assertEqual(code, 1)
            self.assertNotIn("private-fixture-token", json.dumps(result))
            self.assertEqual(f["out"].read_bytes(), b"old-good")
```

Test neither downloaded `tools/intake.py` nor any selected file is imported:
replace the template script body with a trap in a *test profile unit fixture*,
and separately monkeypatch subprocess/network entry points to fail if called
by the installed exporter. The actual CLI still accepts only its fixed profile;
never add a production bypass for the test. For original authentic-template
integration, execution of its receiver occurs **later**, by a separate
developer command, not inside export.

Run all `test_factory*.py` focused tests. Refactor only after real GREEN;
preserve unchanged source bytes, no output leakage and the public interfaces.
Commit W3 only after contract, archive, privacy and optional-financial tests
are GREEN together.
During that refactor remove unused imports and annotate the deliberately
late script-local imports with `# noqa: E402`, as the existing plugin scripts
do. Do not ignore other lint findings or loosen repository rules.

## 13. Task 11 — W4 ninth-skill maturity, installer and registration

RED before code: extend `tests/unit/test_skill_maturity.py` with:

```python
def test_factory_is_optional_preview_without_a_cost_ack_gate(self):
    lib = load("tools/fe_lib.py")
    expected = {"maturity": "preview", "optional": True, "requires_preview_ack": False}
    self.assertEqual(lib.maturity_errors("frontier-agent-factory", expected), [])
    for field, value in (("maturity", "ga"), ("optional", False), ("requires_preview_ack", True)):
        bad = dict(expected, **{field: value})
        self.assertTrue(lib.maturity_errors("frontier-agent-factory", bad))
    self.assertEqual(lib.maturity_errors("frontier-finops", {
        "maturity": "preview", "optional": True, "requires_preview_ack": True}), [])
    self.assertTrue(lib.maturity_errors("frontier-finops", {
        "maturity": "preview", "optional": True, "requires_preview_ack": False}))
```

Run `python -m unittest tests.unit.test_skill_maturity -v` and observe RED.
Replace only `tools/fe_lib.py::maturity_errors` with:

```python
def maturity_errors(name: str, fields: dict) -> list[str]:
    errors = []
    preview = name in {"frontier-finops", "frontier-agent-factory"}
    expected = "preview" if preview else "ga"
    if fields.get("maturity") != expected:
        errors.append(f"{name}: product maturity must be {expected}")
    for key in ("optional", "requires_preview_ack"):
        if type(fields.get(key)) is not bool:
            errors.append(f"{name}: {key} must be an explicit boolean")
    if name == "frontier-finops":
        if fields.get("optional") is not True or fields.get("requires_preview_ack") is not True:
            errors.append(f"{name}: FinOps must be optional Preview with acknowledgement required")
    elif name == "frontier-agent-factory":
        if fields.get("optional") is not True or fields.get("requires_preview_ack") is not False:
            errors.append(f"{name}: Factory must be optional Preview without a cost acknowledgement gate")
    elif fields.get("requires_preview_ack") is not False:
        errors.append(f"{name}: GA core must not require FinOps Preview acknowledgement")
    return errors
```

The installed installer cannot import `tools.fe_lib`. Add the equivalent
precise Factory invariant alongside its existing FinOps branch:

```python
if name == "frontier-agent-factory" and maturity != {
    "maturity": "preview", "optional": True, "requires_preview_ack": False,
}:
    problems.append(f"{folder}: current Factory must be optional Preview without a cost acknowledgement gate")
```

Test it with the existing temporary installer probe pattern: correct Factory
metadata succeeds without persisted acknowledgement; wrong maturity,
nonoptional and acknowledgement-true cases fail with no copy calls. Preserve
the FinOps notice and true acknowledgement invariant. Change `preview_notice`
to include a separate Factory Preview sentence when Factory is present, even
when FinOps is absent; installation is neither transfer nor use permission.
Do not make Factory use require the cost-only confirmation.

The complete notice replacement, immediately before constructing `result`,
is:

```python
notices = []
if any(s.get("requires_preview_ack") is True for s in skills_out):
    notices.append(
        "Frontier FinOps is Preview; its grounding and model are not GA and need refinement. "
        "Installation is not acknowledgement of use; explicit acknowledgement is required before cost operations."
    )
if any(s.get("name") == "frontier-agent-factory" for s in skills_out):
    notices.append(
        "Envisioning Agent Factory is optional Preview. Installation grants no source-transfer, "
        "review, repository, tenant or deployment permission. Actual Cowork validation is not performed."
    )
```

Set the existing result key to `"preview_notice": " ".join(notices)`.
Do not add an installer consent flag or persist acknowledgement.

Add to `plugin/package/manifest.json::agentSkills` exactly:

```json
{"folder": "skills/frontier-agent-factory"}
```

Create F `SKILL.md` with this complete frontmatter (description below 900 UTF-16
units), then the concrete procedure following it:

```yaml
---
name: frontier-agent-factory
description: |
  Envisioning Agent Factory prepares a full starter-repository ZIP from a pinned
  compatible template and selected reviewed envisioning files. Optional Preview.
  Use for "prepare the Caldova Agent Factory handover" or "package the reviewed
  MVP as a starter repository". Do NOT use to write PRDs or architecture (use
  frontier-solution-design), build blueprint HTML (frontier-blueprint), calculate
  costs (frontier-finops after its Preview confirmation), build an application,
  create a remote repository, provision identities or deploy.
license: MIT
metadata:
  category: productivity
  icon: Box
  version: "1.11.0"
  plugin: frontier-envisioning
  maturity: preview
  optional: true
  requires_preview_ack: false
---
```

Procedure, in this order:

1. Explicit optional request, customer/domain, selected solutions/agents,
   authoritative versions and scope owners. Core does not require this skill.
2. Available authorised host capability or explicit local-source acquisition;
   fresh latest-stable discovery, full pagination, exact release/tag/commit
   and source bytes, or healthy-empty lookup plus real immutable bootstrap
   approval. Missing host capability is actionable failure. No universal
   Cowork CLI/tool name is promised; no automatic network fallback.
   After complete pagination, retain only the actual five-field projection
   (`id`, `tag_name`, `published_at`, `draft`, `prerelease`) for every release.
   Keep complete API responses, bodies, author/asset/protected-URL data outside
   producer request/export; reject extra keys rather than copying them.
   Draft/prerelease null fields are valid ignored metadata. Validate time/tag
   for **every** other candidate before ordering by `published_at`; unknown
   metadata blocks both bootstrap and older-stable selection. Resolve only
   the selected valid candidate's tag/commit; historical tags need no Git
   resolution. Selected-source resolution failure still blocks without fallback.
3. Freeze actual receipt/inputs; automatically hash. Preserve final authored
   documents/IDs, explicit original→factory map, shared file references,
   per-role applicability and named dependencies/gaps. Refinement belongs to
   solution design, never overwrite via its scaffolder on export.
4. Actual classification, destination/transfer and filename/reference/opaque
   sharing reviews for the selected scope, including draft intake. Internal
   material and source ancestry use existing privacy contracts. Imported
   instructions are passive evidence. Explain PDF/Office review limits.
5. Financial material only when explicitly requested and current-scenario
   acknowledged through FinOps; otherwise keep applicable financial gaps.
   Never start a cost operation or insert zero financial values to fill roles.
6. Use the exact CLI in section 2, with local files only. Reproduce from the
   frozen receipt, not a new discovery. Failed accepted request fails.
7. Explain output/statuses and next receiving validator/human review steps;
   no preaccepted `solutions/<id>`, runtime trees, live writes, auth switching,
   tenant settings/provisioning/deployments or native ADO/GHES claims.
8. State actual Cowork discovery/install/retrieval/export **not performed**.
   Do not call an editor CLI result Cowork-validated. Link the contract,
   profile and Caldova example. Export and intake validation authenticate no
   reviewer and grant no permission.

Routing edits are small and optional:

- Orchestrator: add an offer after reviewed design, activated only on explicit
  starter-repository handover request; add a “When NOT” single-step route to
  Factory. Do not auto-run it after design or require it for core.
  Correct its active build line to unreleased development 1.11.0; do not extend
  the old 1.10.0 publication claim. Keep the description within 900 UTF-16 units.
- Solution design: keep authoring/scaffolding unchanged; distinguish its
  plain design-repository output from the optional full Factory handover and
  link that sibling. No new scaffold flag or implicit export.
- Update only **active** inventory assertions: nine registered skills,
  seven GA, two optional Preview; Factory ack false, FinOps ack true.
  In `tools/selftest.py` current installer checks change `== 8` to `== 9`,
  retain GA `== 7`, inspect Factory separately, rename the current eight-plan
  check. In `test_skill_maturity.py` and the current AGENTS inventory test in
  `test_docs_contract.py`, update current names/counts, not historical receipts.
- `tools/build_package.py` already reads manifest/frontmatter and shared
  maturity validation; no hardcoded new inventory or new package format is
  necessary. Prove its direct-consumer behaviour with package tests.

Run maturity/docs-contract tests, then `python tools\dev.py package`.
Regenerate `plugin/install/plugin-install.json`; never hand edit it.
Commit the bounded integration scope after GREEN.

## 14. Task 12 — W4 installed exact-package proof and self-test

Add `tests/unit/test_factory_package.py`. Use actual `build_package.main` in
a temporary dist, extract the candidate, run its exact installer and exporter
in subprocesses with `cwd` outside the repository. No `PYTHONPATH` pointing
at repository `tools` or scripts. `PYTHONNOUSERSITE=1` is process-only.
This complete smoke-test body belongs in a `unittest.TestCase`:

```python
def test_exact_zip_exporter_is_offline_and_reproducible(self):
    import hashlib
    import json
    import os
    import subprocess
    import sys
    import tempfile
    import zipfile
    from pathlib import Path
    from tests.unit._util import ROOT, load
    from tests.factory_fixture import prepare
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        package = load("tools/build_package.py")
        self.assertEqual(package.main(["--dist", str(root / "dist")]), 0)
        candidate = root / "dist/frontier-envisioning-plugin-1.11.0.zip"
        self.assertTrue(candidate.is_file())
        extracted = root / "installed"
        with zipfile.ZipFile(candidate) as archive:
            archive.extractall(extracted)  # Trusted just-built plugin, not source intake.
        fixture = prepare(root / "fixture")
        env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)
        empty = root / "empty"
        empty.mkdir()
        install = subprocess.run(
            [sys.executable, "-B", str(extracted / "install/prepare_install.py"),
             "--root", str(extracted), "--installed", str(empty)],
            cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertEqual(install.returncode, 0, install.stdout)
        plan = json.loads(install.stdout)
        self.assertTrue(plan["verified"])
        self.assertEqual(len(plan["skills"]), 9)
        self.assertEqual(sum(r["maturity"] == "ga" for r in plan["skills"]), 7)
        exporter = extracted / "skills/frontier-agent-factory/scripts/export_factory.py"
        args = [sys.executable, "-B", str(exporter),
                "--request", str(fixture["request_file"]), "--template", str(fixture["template"]),
                "--source-root", str(fixture["source"]), "--baseline-root", str(fixture["baseline"]),
                "--out", str(fixture["out"])]
        results, data = [], []
        for _ in range(2):
            result = subprocess.run(args, cwd=root, env=env, capture_output=True,
                                    text=True, encoding="utf-8", timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(result.stderr, "")
            results.append(json.loads(result.stdout))
            data.append(fixture["out"].read_bytes())
        self.assertEqual(data[0], data[1])
        self.assertEqual(results[0]["zip_sha256"], hashlib.sha256(data[0]).hexdigest())
        self.assertEqual(results[0], results[1])
```

RED: run before registration/CLI integration; it must expose a real missing
package/behaviour condition. GREEN after Task 11 and fixes, not by changing the
test to a repository-script invocation. Add accepted synthetic, missing design,
tampered install inventory and core-with-FinOps-absent cases. Run installed
scripts with Python `-S` as an additional stdlib-only proof (no dependencies).
Do not remove FinOps from the delivered package; absence is isolated testing.

Extend `tools/selftest.py` with `factory_cli_checks(pkg, work, check)`:
load `tests/factory_fixture.py` using its existing `load` helper, call
`prepare(work / "factory")`, invoke **pkg**'s exporter twice with the exact
arguments above using existing `installed_run`, compare actual ZIP bytes and
summary hashes, check the passive foundation/licences and default disposition,
then select unsupported HTML and check failure/old-good preservation.
Call it alongside `baseline_cli_checks` in the extracted-package branch.
Use actual returned results; no static “passed” JSON or repo-exporter substitute.

Complete new self-test function:

```python
def factory_cli_checks(package: Path, work: Path, check) -> None:
    fixture_module = load(ROOT / "tests/factory_fixture.py")
    fixture = fixture_module.prepare(work / "factory")
    exporter = package / "skills/frontier-agent-factory/scripts/export_factory.py"
    args = ["--request", str(fixture["request_file"]),
            "--template", str(fixture["template"]), "--source-root", str(fixture["source"]),
            "--baseline-root", str(fixture["baseline"]), "--out", str(fixture["out"])]
    first = installed_run(exporter, args, work)
    check("installed Factory exports a review starter", first.returncode == 0, first.stdout[-300:])
    if first.returncode:
        return
    before = fixture["out"].read_bytes()
    summary = json.loads(first.stdout)
    check("Factory reports unperformed host/receiver checks truthfully",
          summary["intake_disposition"] == "needs-clarification" and
          summary["cowork_validation"] == summary["receiver_validation"] == "not-performed")
    second = installed_run(exporter, args, work)
    check("installed Factory frozen inputs reproduce exact ZIP bytes",
          second.returncode == 0 and fixture["out"].read_bytes() == before,
          second.stdout[-300:])
    import hashlib
    check("Factory ZIP digest is computed, not a manual user step",
          summary["zip_sha256"] == hashlib.sha256(before).hexdigest())
    with zipfile.ZipFile(fixture["out"]) as archive:
        check("Factory preserves passive foundation and vendor material",
              {"LICENSE", ".agents/skills/LICENSE.superpowers",
               ".agents/superpowers.lock.json", "START_HERE.md",
               "handover/manifest.json"} <= set(archive.namelist()))
    row = fixture["request"]["intake"]["artifacts"][0]
    row["source"]["path"] = "selected.html"
    (fixture["source"] / "selected.html").write_bytes(b"<html>not an ordinary equivalent</html>")
    fixture_module.save(fixture)
    refused = installed_run(exporter, args, work)
    check("Factory refuses selected HTML without damaging previous good ZIP",
          refused.returncode == 1 and fixture["out"].read_bytes() == before,
          refused.stdout[-300:])
```

## 15. Task 13 — W4 actual retained-reference receiver integration

New `tests/pipeline/test_factory_receiver.py` is developer-only and explicit.
Its required environment variables are `FRONTIER_FACTORY_REFERENCE` and
`FRONTIER_FACTORY_RECEIVER_PYTHON`. Without them, the dedicated command fails
with a prerequisite message; general offline unit tests do not claim this
integration ran. Do not install anything or modify the retained checkout/env.

The test:

1. Verifies retained reference HEAD/clean status using read-only Git commands,
   exact schema/validator fingerprints and actual `git ls-tree -r` modes.
2. Creates an owned temporary ZIP with the complete test's local
   `git("archive", "--format=zip", "--output=" + str(template), COMMIT)` call,
   bound to the retained reference and owned `Path` destination below.
   This is a developer reference acquisition, not “latest” for a real handover.
   Replace the synthetic fixture foundation with those **actual** archive bytes
   using `prepare(root / "fixture", foundation=template_bytes)`; label its receipt
   `synthetic-compatibility`/developer reference, not real customer bootstrap consent.
3. Builds the 1.11.0 plugin twice into two separate temporary dist directories,
   compares exact plugin ZIP hashes/bytes, extracts the exact candidate and
   invokes its exporter twice outside the repo. Compare the full output ZIPs.
4. Before adding generated files, compare output foundation names/bytes/modes
   with every `git ls-tree -r` blob (`git show <commit>:<path>`). Require actual
   149 / 726,850 for this fixed developer reference; those are not general
   future-release limits. Preserve workflows, locks and both licence notices.
5. Extracts only the already validated producer ZIP into owned test storage.
   Runs the pinned **reference** receiver against that output and its separately
   retained originals, using the retained interpreter and process-only isolation.
   Does not execute a downloaded/template script during export.
6. Exercises default needs-clarification and synthetic accepted complete packets.
   For negative receiver probes, mutate only temporary producer output/records:
   missing design/approval, restricted baseline, approved transfer/null approval,
   generic transformation/equal digest, invalid JSON, digest mismatch, junction
   and the real exact/over shared-budget case. Both producer and receiver must
   reject applicable cases; receiver fixture gaps do not waive producer tests.
7. Checks baseline-only output explicitly says original files were not checked;
   fullsource output must report original bytes checked. Do not infer identity
   authentication, Node readiness or Cowork success from either.

Use these actual developer commands; variables are fully specified:

```powershell
$reference = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-reference-0bb2b1b'
$receiver = 'C:\Users\urruegg\.copilot\session-state\abb9649a-dc0a-4b73-9a05-bdc993ea7335\files\factory111-receiver-env\Scripts\python.exe'
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
$env:PYTHONNOUSERSITE = '1'
$env:FRONTIER_FACTORY_REFERENCE = $reference
$env:FRONTIER_FACTORY_RECEIVER_PYTHON = $receiver
$env:FRONTIER_FACTORY_RECEIVER_REQUIRED = '1'
& $receiver --version
if ($LASTEXITCODE -ne 0) { throw 'Retained receiver interpreter unavailable' }
& $receiver -c "import importlib.metadata; assert importlib.metadata.version('jsonschema') == '4.25.1'"
if ($LASTEXITCODE -ne 0) { throw 'Retained pinned receiver dependencies unavailable' }
python -m unittest tests.pipeline.test_factory_receiver -v
if ($LASTEXITCODE -ne 0) { throw 'Exact packaged producer/reference receiver integration failed' }
```

Inside that test the **complete executable receiver invocation** is:

```python
env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
env.pop("PYTHONHOME", None)
env.pop("PYTHONPATH", None)
command = [receiver_python, "-B", "-m", "tools.intake", "validate",
           str(output_root / "docs/intake/records/caldova-intake/intake.json"),
           "--root", str(output_root), "--source-root", str(originals)]
result = subprocess.run(command, cwd=reference, env=env, capture_output=True,
                        text=True, encoding="utf-8", timeout=120)
self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
```

Here `receiver_python`, `reference` are the required environment values;
`output_root`, `originals` are that test's actual extracted output and
`prepare` source paths, not guessed global directories. Use `import os,
subprocess` and `Path` in that test. Record actual counts/skips/output.
The original receiver suite can be checked without reinstalling:

```powershell
Push-Location -LiteralPath $reference
try {
    & $receiver -B -m unittest discover -s tests -p test_intake.py -v
    if ($LASTEXITCODE -ne 0) { throw 'Pinned receiver regression failed' }
} finally {
    Pop-Location
}
```

The W0 count is historical until this command actually runs again. Python
receiver compatibility is the acceptance target; Node 24 LTS is still not
demonstrated by Node 26.13.1. Full factory `tools.dev check`, Cowork and native
ADO/GHES tests are not claimed.

Use the following complete pipeline test as the executable positive proof.
Its negative mutations listed above are added as separate failing methods,
then minimal GREEN producer fixes. No upstream file is mutated.

```python
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from tests.factory_fixture import COMMIT, approved, prepare, save
from tests.unit._util import ROOT, load

class FactoryReceiver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        names = ("FRONTIER_FACTORY_REFERENCE", "FRONTIER_FACTORY_RECEIVER_PYTHON")
        if not all(os.environ.get(name) for name in names):
            if os.environ.get("FRONTIER_FACTORY_RECEIVER_REQUIRED") == "1":
                raise RuntimeError("Explicit receiver integration requires the retained reference and interpreter")
            raise unittest.SkipTest("Explicit retained receiver integration not requested")
        cls.reference = Path(os.environ[names[0]])
        cls.receiver = os.environ[names[1]]

    def test_exact_package_actual_foundation_and_receiver(self):
        env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)
        def git(*args):
            return subprocess.run(["git", "-C", str(self.reference), *args],
                                  check=True, capture_output=True, env=env, timeout=120).stdout
        self.assertEqual(git("rev-parse", "HEAD").decode().strip(), COMMIT)
        self.assertEqual(git("status", "--porcelain"), b"")
        expected = {}
        for line in git("ls-tree", "-r", COMMIT).splitlines():
            description, name = line.split(b"\t", 1)
            mode, kind, _ = description.split()
            self.assertEqual((mode, kind), (b"100644", b"blob"))
            path = name.decode("utf-8")
            expected[path] = git("show", COMMIT + ":" + path)
        self.assertEqual(len(expected), 149)
        self.assertEqual(sum(map(len, expected.values())), 726850)
        self.assertEqual(hashlib.sha256(expected["docs/intake/intake.schema.json"]).hexdigest(),
                         "04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f")
        self.assertEqual(hashlib.sha256(expected["tools/intake.py"]).hexdigest(),
                         "4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            template = root / "reference.zip"
            git("archive", "--format=zip", "--output=" + str(template), COMMIT)
            template_bytes = template.read_bytes()
            package = load("tools/build_package.py")
            candidates = []
            for name in ("package-a", "package-b"):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(package.main(["--dist", str(root / name)]), 0)
                candidates.append((root / name / "frontier-envisioning-plugin-1.11.0.zip").read_bytes())
            self.assertEqual(candidates[0], candidates[1])
            installed = root / "installed"
            with zipfile.ZipFile(io.BytesIO(candidates[0])) as archive:
                archive.extractall(installed)
            exporter = installed / "skills/frontier-agent-factory/scripts/export_factory.py"
            for accepted in (False, True):
                fixture = prepare(root / ("accepted" if accepted else "clarification"),
                                  accepted=accepted, foundation=template_bytes)
                command = [sys.executable, "-S", "-B", str(exporter),
                           "--request", str(fixture["request_file"]),
                           "--template", str(fixture["template"]),
                           "--source-root", str(fixture["source"]),
                           "--baseline-root", str(fixture["baseline"]),
                           "--out", str(fixture["out"])]
                outputs = []
                for _ in range(2):
                    result = subprocess.run(command, cwd=root, env=env, capture_output=True,
                                            text=True, encoding="utf-8", timeout=120)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(result.stderr, "")
                    raw = fixture["out"].read_bytes()
                    self.assertEqual(json.loads(result.stdout)["zip_sha256"],
                                     hashlib.sha256(raw).hexdigest())
                    outputs.append(raw)
                self.assertEqual(outputs[0], outputs[1])
                output_root = fixture["out"].parent / "receiver-output"
                with zipfile.ZipFile(io.BytesIO(outputs[0])) as archive:
                    for name, raw in expected.items():
                        self.assertEqual(archive.read(name), raw, name)
                        self.assertEqual(stat.S_IMODE(archive.getinfo(name).external_attr >> 16), 0o644)
                    archive.extractall(output_root)
                record = output_root / "docs/intake/records/caldova-intake/intake.json"
                base_command = [self.receiver, "-B", "-m", "tools.intake", "validate",
                                str(record), "--root", str(output_root)]
                for originals in (False, True):
                    args = base_command + (["--source-root", str(fixture["source"])] if originals else [])
                    result = subprocess.run(args, cwd=self.reference, env=env, capture_output=True,
                                            text=True, encoding="utf-8", timeout=120)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    expected_scope = ("baseline and source bytes" if originals else
                                      "baseline bytes and recorded source evidence (original bytes not checked)")
                    self.assertIn(expected_scope, result.stdout)
                    self.assertIn("human approvals are not authenticated", result.stdout)
                raw_record = record.read_bytes()
                self.assertLess(len(raw_record), 1024 * 1024)
                for extra, code in ((0, 0), (1, 1)):
                    record.write_bytes(raw_record + b" " * (1024 * 1024 - len(raw_record) + extra))
                    result = subprocess.run(
                        base_command + ["--source-root", str(fixture["source"])],
                        cwd=self.reference, env=env, capture_output=True,
                        text=True, encoding="utf-8", timeout=120)
                    self.assertEqual(result.returncode, code, result.stdout + result.stderr)
                record.write_bytes(raw_record)

    def test_windows_path_history_is_preserved_and_validates_with_actual_receiver(self):
        env = dict(os.environ, PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
        env.pop("PYTHONHOME", None)
        env.pop("PYTHONPATH", None)
        def git(*args):
            return subprocess.run(["git", "-C", str(self.reference), *args],
                                  check=True, capture_output=True, env=env, timeout=120).stdout
        self.assertEqual(git("rev-parse", "HEAD").decode().strip(), COMMIT)
        self.assertEqual(git("status", "--porcelain"), b"")
        common = load("plugin/skills/frontier-agent-factory/scripts/factory_common.py")
        upstream = self.reference / "tests/fixtures/intake"
        old_raw = (upstream / "accepted.json").read_bytes()
        old = json.loads(old_raw)
        provided = [row for row in old["artifacts"] if row["status"] == "provided"]
        self.assertTrue(any("\\" in row["baseline"]["path"] for row in provided))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            template = root / "reference.zip"
            git("archive", "--format=zip", "--output=" + str(template), COMMIT)
            package = load("tools/build_package.py")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(package.main(["--dist", str(root / "dist")]), 0)
            installed = root / "installed"
            with zipfile.ZipFile(root / "dist/frontier-envisioning-plugin-1.11.0.zip") as archive:
                archive.extractall(installed)
            fixture = prepare(root / "with-history", foundation=template.read_bytes())
            old_path = f"docs/intake/records/{old['intake_id']}/intake.json"
            target = fixture["baseline"] / old_path
            target.parent.mkdir(parents=True)
            target.write_bytes(old_raw)
            expected_files = {}
            for row in provided:
                raw_path = row["baseline"]["path"]
                name = common.portable(raw_path)
                raw = common.read(upstream / "workspace", raw_path, 16 * 1024 * 1024)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["baseline"]["sha256"])
                destination = fixture["baseline"] / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(raw)
                expected_files[name] = raw
                fixture["request"]["sharing_review"]["artifacts"][
                    old["intake_id"] + ":" + row["id"]] = approved("synthetic-history-transfer-only")
            fixture["request"]["history"] = [old["intake_id"]]
            fixture["request"]["intake"]["supersedes"] = old["intake_id"]
            # Current input paths/descriptors exercise the same canonical
            # lookups as the immutable Windows-spelled historical record.
            for row in fixture["request"]["intake"]["artifacts"]:
                if row["status"] == "provided":
                    row["baseline"]["path"] = row["baseline"]["path"].replace("/", "\\")
            descriptor = fixture["request"]["blueprint"]
            descriptor["baseline_path"] = descriptor["baseline_path"].replace("/", "\\")
            save(fixture)
            source_before = {p: p.read_bytes() for p in fixture["source"].rglob("*") if p.is_file()}
            exporter = installed / "skills/frontier-agent-factory/scripts/export_factory.py"
            command = [sys.executable, "-S", "-B", str(exporter),
                       "--request", str(fixture["request_file"]),
                       "--template", str(fixture["template"]), "--source-root", str(fixture["source"]),
                       "--baseline-root", str(fixture["baseline"]), "--out", str(fixture["out"])]
            result = subprocess.run(command, cwd=root, env=env, capture_output=True,
                                    text=True, encoding="utf-8", timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            output_root = root / "history-output"
            with zipfile.ZipFile(fixture["out"]) as archive:
                self.assertTrue(all("\\" not in name for name in archive.namelist()))
                self.assertEqual(archive.read(old_path), old_raw)
                for name, raw in expected_files.items():
                    self.assertEqual(archive.read(name), raw)
                archive.extractall(output_root)
            self.assertEqual((fixture["baseline"] / old_path).read_bytes(), old_raw)
            self.assertEqual(source_before, {p: p.read_bytes()
                                            for p in fixture["source"].rglob("*") if p.is_file()})
            records = [
                (output_root / "docs/intake/records/caldova-intake/intake.json", fixture["source"]),
                (output_root / old_path, upstream / "source")]
            for record, originals in records:
                result = subprocess.run(
                    [self.receiver, "-B", "-m", "tools.intake", "validate", str(record),
                     "--root", str(output_root), "--source-root", str(originals)],
                    cwd=self.reference, env=env, capture_output=True,
                    text=True, encoding="utf-8", timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("baseline and source bytes", result.stdout)
                self.assertIn("human approvals are not authenticated", result.stdout)
```

Expected GREEN is actual zero exits for both dispositions and both receiver
modes, byte-identical plugin/output pairs, and preserved actual source.
That is not full upstream tooling or real human acceptance. The test only
extracts trusted just-built plugin ZIPs and ZIPs that the producer has already
validated; untrusted source archives are always handled by the bounded reader.
The history test uses the actual retained upstream accepted fixture, including
its Windows path strings and original Markdown bytes. It neither reformats
that record nor promotes its synthetic approvals to human authorisation.

## 16. Task 14 — W4 product/engineering prose, not historical rewriting

Use proportionate document validation, not invented RED/GREEN for prose.
Parent retains planning catalogue/idea/spec/W0 plan/sprint ownership. Arrange
these implementation documentation edits with it; do not blanket-reformat.

1. F `references/handover-contract.md`: write the complete request/receipt,
   paths, strict intake versus sidecar schemas, eight roles, source/baseline
   digests, exact shared budget, history, bounds and errors from this plan.
   Include actual-source acquisition, genuine evidence and lack of
   authentication, opaque review, optional finance and deferred Cowork.
2. F `examples/caldova-handover.json`: the fixture's fully populated request
   shape, explicitly `synthetic-compatibility`. Generate automatic archive/
   file digests during the documented preparation; do not put fake approvals
   or empty acquisition into a real-handover example. Reference example paths
   are local synthetic ordinary files created by the documented fixture,
   not promised attached customer files.
3. Current `README.md`, `plugin/README.md`, `AGENTS.md` section 1 and FinOps
   body's active skill-count paragraph: nine / seven GA / two optional
   Preview. Add Factory's explicit optional nature and offline Preview limit.
   Preserve existing FinOps confirmation rules. Do not rewrite old
   eight-skill release receipts, historical B.8/B.9 tables or ADR-0028 history.
4. `docs/prd.md`: prepend `## 1.11.0 Agent Factory offline Preview` with
   AF-01–16 requirements/acceptance linked to the approved spec and this plan;
   no invented old FR/AC IDs. A.12 gets a current 1.11.0 factory-only
   qualification, #58 systems/D365 later unspecified. A.13 records actual
   written decisions/receipts and separate pending host/manual/permission
   matters. Do not alter original requirement/decision tables or migration IDs.
5. `docs/solution-design.md`: same bounded development heading, host receipt →
   offline validation → passive full ZIP → separate receiver/human review flow;
   B.9 gets actual candidate verification only after it runs and explicit
   deferred Cowork/Node profile status. Keep historical release tables intact.
6. `docs/adr/0032-offline-agent-factory-handover.md`: six-field metadata,
   **Proposed**, Context/Decision/Consequences/Alternatives/Status. Record
   full-foundation versus overlay/network alternative, offline/host boundary,
   strict intake separate sidecar, no executed imports, safe deterministic
   atomic archive, shared raw ZIP mechanism and unchanged authority. Add the
   exact local link to `docs/adr/README.md`; approval of this plan does not
   automatically accept an ADR.
7. `CHANGELOG.md` under unreleased 1.11.0: optional Preview ninth skill,
   supported ordinary-file intake and offline deterministic ZIP; actual
   Cowork unavailable/not tested; no runtime/deployment/native-host claim.

For the existing `tests/unit/test_docs_contract.py` historical identifier
contract, add a narrowly bounded optional 1.11 heading pair allowing **only**
`ADR-0032`; AF IDs are not old FR/AC IDs. Add a mutation regression showing
`ADR-0033` and an unrelated FR/AC still fail. Preserve historical content hashes
and the original-section extraction: place current A.12/A.13/B.9 qualification
inside their existing current-qualification region, before original table
boundaries, so historical hashes do not change. Do not update golden receipts
to accept rewritten historical prose.

Check active counts with targeted search, review each hit's historical context,
then run:

```powershell
python -m unittest tests.unit.test_docs_contract tests.unit.test_skill_maturity -v
if ($LASTEXITCODE -ne 0) { throw 'Current inventory/history documentation contract failed' }
python tools\dev.py docs --strict
if ($LASTEXITCODE -ne 0) { throw 'Documentation contract failed' }
git --no-pager diff --check
if ($LASTEXITCODE -ne 0) { throw 'Whitespace check failed' }
```

Do not fix protected legacy session-start routing; report **pending human #8
action**. No `.github/hooks`, CODEOWNERS, root/plugin licence, release records,
release/Azure workflows, vendored `.agents/skills` or denylist edits.

## 17. Acceptance map and final execution order

| Acceptance | Exact proof in this plan |
|---|---|
| AF-01 | Task 11 registration/maturity/routing tests; Task 12 extracted installer/core-without-Factory and without-FinOps checks |
| AF-02 | Task 3 receipt latest stable/error/pin tests; Task 13 genuine reference bytes; new actual host lookup required per real handover |
| AF-03 | Task 3 healthy-empty versus failure/bootstrap tests; Task 13 explicitly synthetic developer reference, not real bootstrap approval |
| AF-04 | Tasks 5–6 passive raw foundation/security tests; Task 13 all 149 blobs/modes/licence/lock/policy comparison |
| AF-05 | Tasks 7–8 explicit mapping/scope/shared-file/author-byte/dependency-gap/history tests |
| AF-06 | Tasks 3–4 schema and per-solution roles; Task 13 actual receiver with originals, correct ordinary-file destinations |
| AF-07 | Tasks 3, 7–10 default clarification, explicit accepted refusal and synthetic accepted compatibility; no solution units or false authority |
| AF-08 | Task 7 privacy/content/ancestry/name/reference/opaque-review tests; Task 10 fixed diagnostics/old-output preservation |
| AF-09 | Tasks 6–7 unsupported formats, renamed-content/signature tests and equivalent guidance; no bypass directory |
| AF-10 | Tasks 2, 4, 6, 10 actual limits, raw CRC/EOF, paths/modes/collisions/junctions/atomic failure tests |
| AF-11 | Tasks 6, 7, 12–13 exact frozen metadata, two producer ZIP builds and two exact plugin packages; automatic hashes |
| AF-12 | Task 13 retained pinned Python receiver actual generated Caldova packets; missing prerequisites fail honestly |
| AF-13 | Tasks 12–13 exact packaged offline CLI and actual receiver; actual Cowork discovery/install/acquisition/export explicitly not performed |
| AF-14 | Task 9 lazy optional financial/current-invocation checks and genuine existing helpers; core has no cost operation or manufactured zero |
| AF-15 | Tasks 7, 10–11 no process/network/live-write route; START_HERE/procedure and permission/status separation |
| AF-16 | Every code task's observed RED→minimal GREEN→refactor; Tasks 1, 5, 11–14 historical/version/package/gate preservation |

### Final exact-candidate gate sequence

Run smallest tests first, then all focused tests, then package/installed/receiver,
then repository gates. Do not claim a combined pass by adding counts from
different heads. Capture head, commands, actual exit codes, counts and skips.

```powershell
python -m unittest tests.unit.test_factory_contract -v
if ($LASTEXITCODE -ne 0) { throw 'Factory contract failed' }
python -m unittest tests.unit.test_factory_shared_zip tests.unit.test_factory_archive tests.unit.test_release_evidence -v
if ($LASTEXITCODE -ne 0) { throw 'Shared ZIP/archive/release regressions failed' }
python -m unittest tests.unit.test_factory_export tests.unit.test_factory_privacy tests.unit.test_factory_finops -v
if ($LASTEXITCODE -ne 0) { throw 'Factory projection/export failed' }
python -m unittest tests.unit.test_skill_maturity tests.unit.test_docs_contract tests.unit.test_demo_raster_111 -v
if ($LASTEXITCODE -ne 0) { throw 'Integration/history contracts failed' }
python tools\dev.py package
if ($LASTEXITCODE -ne 0) { throw 'Package generation failed' }
python -m unittest tests.unit.test_factory_package -v
if ($LASTEXITCODE -ne 0) { throw 'Exact installed package failed' }
python -m unittest tests.pipeline.test_factory_receiver -v
if ($LASTEXITCODE -ne 0) { throw 'Actual receiver compatibility failed' }
python tools\dev.py check --strict
if ($LASTEXITCODE -ne 0) { throw 'Strict full gate failed' }
git --no-pager diff --check
if ($LASTEXITCODE -ne 0) { throw 'Whitespace check failed' }
```

The dedicated receiver command uses Task 13's explicitly set environment.
General pipeline discovery must not falsely label absent integration a pass:
put its test behind an explicit class condition for general gates and record
that skip, while the dedicated invocation requires the variables. Implement
that distinction with a separate command-line/environment opt-in
`FRONTIER_FACTORY_RECEIVER_REQUIRED=1` set in Task 13 and the dedicated final
invocation: absent prerequisites raise `RuntimeError` when required, otherwise
`unittest.SkipTest("Explicit retained receiver integration not requested")`.
Do not suppress failure when the integration was explicitly requested.

Local `--strict` does not enable networking. A local release status
`not-performed` must retain the runner's truthful
`LOCAL CHECKS COMPLETED; published-release verification NOT PERFORMED`, not a
fabricated `ALL GATES PASSED`; it is not the final AGENTS completion gate.
Invalid evidence/reproduction is a failure. A standalone
`python tools\verify_release.py --online` reports its own exact-version
development/verified outcome only. Development absence is not cached as
published-release evidence, so a later ordinary offline check may still be
not-performed. That probe never upgrades a later whole-check result.

After the local sequence above, open a **fresh validation-only PowerShell at
the exact candidate worktree root**. Use normal existing `gh` read-only
authentication, no token inspection/output or auth switching. Run:

```powershell
$env:CI = 'true'
python tools\dev.py check --strict
if ($LASTEXITCODE -ne 0) { throw 'Authoritative online full candidate gate failed' }
```

This is the supported developer runner's process-local authenticated online
full gate, not a workflow dispatch/settings change. It must perform fresh
exact-version lookup and all strict gates on the actual candidate, and end
with actual **ALL GATES PASSED** (`development` or `verified` as appropriate).
Access/network/tool/comparison errors fail; none are waived or converted to
absence. Close that shell afterwards. Preserve all 1.10.x records and do not write new release
manifests. Report actual CI separately; agents do not dispatch protected
workflows, publish or invent a server result.

After actual tests, prepare a draft PR using the existing
`.github/PULL_REQUEST_TEMPLATE.md`: real work-package links, AI involvement,
observed RED/GREEN and gate summaries, exact candidate/package/receiver
evidence, deferred Cowork/manual checks, human #8 dependency and sole-maintainer
sign-off boundary. The Summary is written by a person as its heading requires.
Do not tick unrun gates or release-only Cowork checkboxes. No formal self-
approval, merge, tag, protected label or release action is authorised.
Parent handles committed review/handoff and actual issue/evidence updates.

The final two development validation commands run in that fresh online
validation context (`CI=true` makes the final ordinary `check` strict and
online too), not in a later offline shell. Their actual summary must end
`ALL GATES PASSED` before completion:

```powershell
$env:CI = 'true'
python tools\dev.py docs --strict
python tools\dev.py check
```

## 18. Plan self-review and planning-session verification

- Coverage: AF-01–16 map to concrete tests, installed output or deliberately
  deferred real-host evidence. W0 source/receiver evidence is not a producer
  pass or permission to implement this unwritten-at-W0 plan.
- API consistency: public CLI has five required local paths and one optional
  current-action financial flag; sibling APIs are existing installed helpers,
  never `tools` imports from plugin distribution. Intake schema is unextended;
  request and handover schemas are separate; blueprint schema does not change.
- Method: the parent is using its active writing-plans/Superpowers workflow.
  This planning worker has a limited read/search/patch tool surface; its
  earlier path search did not establish global installation/availability.
  It applies writing-plans principles through the AGENTS method here and
  does not imply Superpowers is absent globally, disabled in the parent,
  or activated for this worker by skills inside the passive reference tree.
- Security/resources: raw actual bytes/CRC/EOF before structural ZIP checks;
  one source-plus-baseline receiver budget; real exact/one-over tests; reparse
  refusal on Python 3.11; atomic replace only after all validation; no private
  exception detail or restricted exclusion inventory.
- History/version: bump follows baseline and precedes plugin edits; named
  finite raster profile only; immutable old hashes/records/accepted input
  bytes; source documents are never regenerated.
- Readiness: this complete plan still needs its **one actual human approval**
  and recorded linked readiness before fresh implementation workers. No
  repeated human micro-approvals between already approved tasks. A meaningful
  new boundary question returns NEEDS_CONTEXT.
- Planning-only scope: no production/test/tool/package/version edit, dependency
  installation, commit, push, PR, issue, label or agent dispatch is performed
  by writing this file. Existing parent records remain untouched.
- Validation limitation: the planning tool surface provides file reads/search/
  patches but no command runner. No Python, PowerShell parser, strict docs,
  unit test, `git diff --check` or full gate execution is claimed here.
  The parent must run strict docs after adding its intended catalogue link.
  Targeted metadata/link/coverage/placeholder checks are static review only.
- Revision 0.2 static review: one H1, the six metadata fields in order and
  16 AF acceptance-map rows; targeted searches found no stale original-tree
  selection call, 24-character N/A threshold, all-release commit requirement,
  broad CLI programming-exception catch or forward-slash PowerShell script
  command. Lowercase rejected-sentinel test literals are intentional data,
  not unfinished instructions. This is not a new AST/JSON parsing, strict
  docs or Git whitespace-gate pass; the parent's earlier syntax result
  applies to the preceding draft and must be repeated for this revision.
- Direct-review consistency: selected-release-only Git resolution and strict
  minimal complete-enumeration receipts (no raw API objects); unknown stable
  metadata blocks absence/older selection. Upstream N/A normalisation; safe-tree selection; strict
  request prevalidation before work; explicit legacy financial detection;
  root passive catalogues versus populated units; canonical map/ZIP paths
  without rewriting accepted records; and actual Windows-history receiver
  regression are now written together. Normal Factory remains independent
  of FinOps. One approval still covers all W1–W4 tasks.
- Final-gate evidence: a standalone online lookup does not make a subsequent
  offline whole-check authoritative. Baseline and final candidate require
  the written fresh-shell, process-local `CI=true` online full gate with
  actual `ALL GATES PASSED`; actual server CI remains separate.
- Human dependency: protected legacy session-start routing remains pending
  **human #8 action**; actual Cowork and full receiver Node profile remain
  unverified. They are disclosed limitations, not invented offline product
  blockers or a release/manual-review waiver.
