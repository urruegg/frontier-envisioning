# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Offline bootstrap proposals: generation is never adoption or permission."""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import socket
import stat
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

from tests.unit._util import ROOT, load

SOURCE_PATHS = (
    "AGENTS.md", ".gitignore", ".github/pull_request_template.md",
    ".github/CODEOWNERS", ".github/hooks/guardrails.json",
    ".github/hooks/scripts/guard.py", ".github/hooks/scripts/session_start.py",
    ".github/workflows/ci.yml", ".github/workflows/release.yml",
    ".github/workflows/azure-dev.yml",
    *(".github/agent-policy/" + name + ".md" for name in (
        "README", "AGENT_WORKFLOW", "NON_DELEGABLE_WORK", "BREAK_GLASS", "KPI_BASELINE",
    )),
    *(".github/agents/" + name + ".agent.md" for name in (
        "docs-agent", "frontier-builder", "frontier-planner", "frontier-release-manager",
        "frontier-renderer", "frontier-reviewer",
    )),
    *(".github/skills/" + name + "/SKILL.md" for name in (
        "frontier-dev-loop", "frontier-intake", "frontier-release",
        "frontier-renderer-change", "frontier-skill-authoring",
    )),
    ".github/copilot-instructions.md",
    ".github/instructions/python-tools.instructions.md",
    ".github/instructions/workflows.instructions.md",
)
OUTPUT_NAMES = {
    "migration-proposal.patch", "settings-proposal.json", "app-descriptor.json",
    "validation-report.json", "operator-checklist.md",
}
AMENDMENT_ANCHORS = (
    (".github/skills/frontier-release/SKILL.md", "## Publish (people only; hooks block agents)"),
    (".github/agents/frontier-release-manager.agent.md", "5. Hand over to the release manager"),
    (".github/instructions/python-tools.instructions.md", "- The hook scripts in"),
    (".github/instructions/workflows.instructions.md", "- Top-level `permissions`"),
    (".github/copilot-instructions.md", "8. **Human-only:**"),
    (".github/copilot-instructions.md", "- Protected session-start routing"),
)


def seed(root: Path) -> None:
    """Copy actual read-only sources into temporary fixtures, never edit checkout."""
    for relative in SOURCE_PATHS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    for relative in (
        "LICENSE", "plugin/MIT.md", "tools/neutrality-denylist.txt",
        "releases/1.10.0/immutable.txt", ".agents/skills/vendored/immutable.txt",
        "plugin/install/plugin-install.json",
        "plugin/skills/frontier-blueprint/templates/frontier-blueprint-template.html",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"Protected fixture: preserve every byte.\r\n")


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*") if path.is_file()
    }


def apply_review_patch(original: str, patch_text: str, relative: str) -> str:
    """Reconstruct one unified diff in memory; never apply it to the checkout."""
    lines = patch_text.splitlines(keepends=True)
    header = "--- a/" + relative + "\n"
    start = lines.index(header) + 2
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("--- a/")), len(lines))
    source = original.replace("\r\n", "\n").splitlines(keepends=True)
    result = []
    cursor = 0
    for line in lines[start:end]:
        if line.startswith("@@"):
            match = re.match(r"@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@", line)
            if match is None:
                raise AssertionError("Invalid review hunk")
            position = int(match[1]) - 1
            result.extend(source[cursor:position])
            cursor = position
        elif line.startswith((" ", "-")):
            if source[cursor] != line[1:]:
                raise AssertionError("Proposal does not match actual source")
            if line[0] == " ":
                result.append(line[1:])
            cursor += 1
        elif line.startswith("+"):
            result.append(line[1:])
        else:
            raise AssertionError("Unexpected diff line")
    result.extend(source[cursor:])
    return "".join(result)


def current_anchor(source: str, prefix: str) -> str:
    """Select actual source text independently of the generator's replacements."""
    if prefix.startswith("## Publish"):
        return source[source.index(prefix):]
    return next(line for line in source.splitlines(keepends=True) if line.startswith(prefix))


class BootstrapGenerationTests(unittest.TestCase):
    def test_generation_only_creates_review_output_and_preserves_active_bytes_offline(self):
        self.assertTrue(
            (ROOT / "tools/governance_bootstrap.py").is_file(),
            "Missing offline bootstrap-generator behavior",
        )
        module = load("tools/governance_bootstrap.py")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            seed(root)
            before = snapshot(root)
            with (
                patch.object(module, "ROOT", root),
                patch.object(subprocess, "Popen", side_effect=AssertionError("No process execution")),
                patch.object(socket, "socket", side_effect=AssertionError("No network")),
                patch.object(urllib.request, "urlopen", side_effect=AssertionError("No HTTP")),
            ):
                module.generate()
            after = snapshot(root)
            self.assertEqual(before, {name: after[name] for name in before})
            added = set(after) - set(before)
            self.assertEqual(
                added, {"build/governance-bootstrap/" + name for name in OUTPUT_NAMES},
            )
            for name in added:
                self.assertNotIn(b"\r", after[name])
                after[name].decode("utf-8")


class BootstrapContractTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            (ROOT / "tools/governance_bootstrap.py").is_file(),
            "Missing offline bootstrap-generator behavior",
        )
        self.module = load("tools/governance_bootstrap.py")
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        seed(self.root)
        self.root_patch = patch.object(self.module, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def outputs(self):
        self.module.generate()
        return {
            path.name: path.read_text(encoding="utf-8")
            for path in (self.root / "build/governance-bootstrap").iterdir()
        }

    def call(self, argv=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = self.module.main([] if argv is None else argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_deterministic_output_is_independent_of_absolute_root(self):
        first = self.outputs()
        with tempfile.TemporaryDirectory() as temporary:
            other = Path(temporary)
            seed(other)
            with patch.object(self.module, "ROOT", other):
                self.module.generate()
            second = {
                path.name: path.read_text(encoding="utf-8")
                for path in (other / "build/governance-bootstrap").iterdir()
            }
        self.assertEqual(first, second)
        self.assertNotIn(str(self.root), "".join(first.values()))

    def test_template_amendment_preserves_every_other_byte_and_release_field(self):
        original = (self.root / ".github/pull_request_template.md").read_text(encoding="utf-8")
        proposal = self.outputs()["migration-proposal.patch"]
        revised = apply_review_patch(original, proposal, ".github/pull_request_template.md")
        expected = original.replace(
            "## Summary (written by a person, in your own words)",
            "## Summary", 1,
        ).replace(
            "<!-- What changes for the users of the plugin or for the engineers, and why. -->",
            "<!-- What changes for the users of the plugin or for the engineers, and why. -->\n"
            "<!-- Human verification required: @urruegg verifies this summary against the reviewed head; "
            "machine text is not physically human-written. -->", 1,
        )
        self.assertEqual(expected, revised)
        self.assertIn("Behavioural prompts of PRD B.9", revised)
        self.assertIn("Install from the built package tested in a Cowork chat", revised)

    def test_reconstructed_release_skill_retires_legacy_activation(self):
        relative = ".github/skills/frontier-release/SKILL.md"
        source = (self.root / relative).read_text(encoding="utf-8")
        revised = apply_review_patch(source, self.outputs()["migration-proposal.patch"], relative)
        # Inspect operative source BEFORE the generic alignment appendix.
        operative = revised.split("\n\n## #50 bootstrap proposal", 1)[0]
        self.assertNotIn("before setting `RELEASE_ENABLED=true`", operative)
        self.assertNotIn("waits for `release-approval`", operative)
        self.assertNotIn("builds the bundle, pinned SBOM and provenance attestation", operative)
        self.assertNotIn("1. Merge the release pull request.", operative)
        self.assertNotIn("2. `git tag vX.Y.Z <merge commit>`", operative)
        self.assertIn("retired", operative.lower())
        self.assertIn("RELEASE_ENABLED", operative)
        self.assertIn("SHOWCASE_ENABLED", operative)
        self.assertIn("unset/false", operative)
        self.assertIn("GitHub Pro", operative)
        self.assertIn("unsupported", operative)
        self.assertIn("BLOCKED", operative)
        self.assertIn("future", operative.lower())
        self.assertIn("isolated trusted publisher", operative)
        self.assertIn("actual human approval", operative)
        self.assertEqual(source.split("## Publish", 1)[0], revised.split("## Publish", 1)[0])
        self.assertIn("Keep released records immutable.", revised)

    def test_reconstructed_release_manager_no_longer_prescribes_legacy_sequence(self):
        relative = ".github/agents/frontier-release-manager.agent.md"
        source = (self.root / relative).read_text(encoding="utf-8")
        revised = apply_review_patch(source, self.outputs()["migration-proposal.patch"], relative)
        operative = revised.split("\n\n## #50 bootstrap proposal", 1)[0]
        handoff = next(line for line in operative.splitlines() if line.startswith("5. "))
        self.assertNotIn("enable `RELEASE_ENABLED`", handoff)
        self.assertNotIn("approve `release-approval`", handoff)
        self.assertNotIn("push the tag", handoff)
        for requirement in (
            "BLOCKED", "@urruegg", "SHOWCASE_ENABLED", "RELEASE_ENABLED", "unset/false",
            "GitHub Pro", "unsupported", "person-only", "future", "isolated trusted publisher",
            "actual human approval", "Never enable, merge, tag, publish",
        ):
            self.assertIn(requirement, handoff)
        prefix = "5. Hand over to the release manager"
        self.assertTrue(revised.startswith(source[:source.index(prefix)]))
        old_handoff = current_anchor(source, prefix)
        self.assertIn(source.split(old_handoff, 1)[1], revised)
        self.assertEqual(source.split("---", 2)[:2], revised.split("---", 2)[:2])

    def test_reconstructed_instruction_proposals_align_current_and_future_roles(self):
        outputs = self.outputs()
        proposal = outputs["migration-proposal.patch"]
        revised = {}
        for relative in (
            ".github/copilot-instructions.md",
            ".github/instructions/python-tools.instructions.md",
            ".github/instructions/workflows.instructions.md",
        ):
            self.assertTrue(
                "--- a/" + relative + "\n" in proposal,
                "Missing applicable instruction amendment: " + relative,
            )
            source = (self.root / relative).read_text(encoding="utf-8")
            revised[relative] = apply_review_patch(source, proposal, relative)
            self.assertIn(relative, json.loads(outputs["validation-report.json"])["source_sha256"])
            self.assertNotRegex(revised[relative], r"(?m)^(?:tools|model|permissionDecision|uses|run):")
        workflows = revised[".github/instructions/workflows.instructions.md"]
        self.assertNotIn("`contents: write` only for publishing a release", workflows)
        for requirement in (
            "Current", "human-only", "future", "accepted trusted proposal coordinator",
            "dedicated feature-branch", "per-repository/per-job", "protected main", "no routine bypass",
            "candidate", "no secrets/write/OIDC", "metadata-only reporter", "cross-job",
            "owner-scoped", "missing", "BLOCKED",
        ):
            self.assertIn(requirement, workflows)
        self.assertIn("never use `pull_request_target` with a checkout of the pull request", workflows)
        self.assertIn("`release.yml` and `azure-dev.yml` are human-maintained", workflows)
        copilot = revised[".github/copilot-instructions.md"]
        for requirement in (
            "**Current human-only:**", "future", "accepted trusted roles", "not permission",
            "no tools/models", "candidate", "owner keys", "person completes #8", "legacy",
        ):
            self.assertIn(requirement, copilot)
        source = (self.root / ".github/copilot-instructions.md").read_text(encoding="utf-8")
        route = next(line for line in source.splitlines() if line.startswith("- Route eligible prose"))
        self.assertIn(route, copilot)
        python = revised[".github/instructions/python-tools.instructions.md"]
        for requirement in (
            "standard library only", "UTF-8", "temporary folders", "people only",
            "source-qualified", "build/governance-bootstrap/", "no credential",
            "no candidate execution", "not adoption",
        ):
            self.assertIn(requirement, python)
        self.assertFalse(json.loads(outputs["validation-report.json"])["adoption_ready"])

    def test_amendment_anchor_drift_fails_before_generating_any_output(self):
        for relative, prefix in AMENDMENT_ANCHORS:
            with self.subTest(relative=relative, prefix=prefix), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                seed(root)
                path = root / relative
                source = path.read_text(encoding="utf-8")
                anchor = current_anchor(source, prefix)
                drifted = anchor.replace("\n", " drifted\n", 1)
                path.write_text(source.replace(anchor, drifted, 1), encoding="utf-8", newline="\n")
                with patch.object(self.module, "ROOT", root):
                    code, stdout, stderr = self.call()
                self.assertEqual(1, code)
                self.assertEqual("", stdout)
                self.assertIn(relative, stderr)
                self.assertIn("source", stderr)
                self.assertFalse((root / "build").exists())

    def test_duplicate_amendment_anchors_fail_before_generating_any_output(self):
        for relative, prefix in AMENDMENT_ANCHORS:
            with self.subTest(relative=relative, prefix=prefix), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                seed(root)
                path = root / relative
                source = path.read_text(encoding="utf-8")
                path.write_text(source + current_anchor(source, prefix), encoding="utf-8", newline="\n")
                with patch.object(self.module, "ROOT", root):
                    code, stdout, stderr = self.call()
                self.assertEqual(1, code)
                self.assertEqual("", stdout)
                self.assertIn(relative, stderr)
                self.assertFalse((root / "build").exists())

    def test_missing_affected_instruction_sources_fail_before_any_output(self):
        for relative in (
            ".github/copilot-instructions.md", ".github/instructions/workflows.instructions.md",
            ".github/instructions/python-tools.instructions.md",
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                seed(root)
                (root / relative).unlink()
                with patch.object(self.module, "ROOT", root):
                    code, stdout, stderr = self.call()
                self.assertEqual(1, code)
                self.assertEqual("", stdout)
                self.assertIn(Path(relative).name, stderr)
                self.assertFalse((root / "build").exists())

    def test_migration_is_grounded_in_actual_hook_and_preserves_denials(self):
        hook = self.root / ".github/hooks/scripts/session_start.py"
        hook.write_text(
            hook.read_text(encoding="utf-8").replace("Human-only:", "Actual source marker. Human-only:"),
            encoding="utf-8", newline="\n",
        )
        output = self.outputs()
        proposal = output["migration-proposal.patch"]
        current = hook.read_text(encoding="utf-8")
        revised = apply_review_patch(current, proposal, ".github/hooks/scripts/session_start.py")
        self.assertNotIn("write the spec and plan to docs/plans/", revised)
        self.assertIn("write the spec to docs/specs/ and plan to docs/plans/", revised)
        self.assertIn("Actual source marker. Human-only:", revised)
        guard_path = ".github/hooks/scripts/guard.py"
        guard = (self.root / guard_path).read_text(encoding="utf-8")
        proposed_guard = apply_review_patch(guard, proposal, guard_path)
        # Only an inert comment is proposed; all existing executable denial code stays exact.
        self.assertEqual(
            guard, proposed_guard.replace(
                "# #50 proposal only: retain every current deny rule; trusted enforcement/adoption is missing.\n", "",
            ),
        )
        for relative in (
            "AGENTS.md", ".github/agent-policy/README.md",
            ".github/agent-policy/AGENT_WORKFLOW.md", ".github/agent-policy/NON_DELEGABLE_WORK.md",
            ".github/agents/frontier-builder.agent.md", ".github/skills/frontier-intake/SKILL.md",
            ".github/workflows/ci.yml", ".github/workflows/release.yml", ".github/workflows/azure-dev.yml",
        ):
            self.assertIn("--- a/" + relative + "\n", proposal)
        for relative in SOURCE_PATHS:
            if relative.startswith((".github/agents/", ".github/skills/")):
                self.assertIn("--- a/" + relative + "\n", proposal)
        self.assertNotIn("--- a/releases/", proposal)
        self.assertNotIn("--- a/.agents/", proposal)
        self.assertNotIn("--- a/LICENSE", proposal)

    def test_report_is_honest_even_when_local_policy_says_accepted(self):
        policy = self.root / ".github/agent-policy/README.md"
        policy.write_text(
            policy.read_text(encoding="utf-8").replace("Proposed; human acceptance pending", "Accepted"),
            encoding="utf-8", newline="\n",
        )
        report = json.loads(self.outputs()["validation-report.json"])
        self.assertFalse(report["adoption_ready"])
        self.assertFalse(report["publication_authorized"])
        self.assertEqual("BLOCKED", report["next_stage"])
        self.assertFalse(report["live_verified"])
        self.assertIn("integration", report["blockers"])
        self.assertIn("provisioning", report["blockers"])
        self.assertIn("provider_capability", report["blockers"])
        self.assertIn("human_adoption", report["blockers"])
        self.assertIn("#8", report["blockers"]["routing"])
        self.assertIn("pure", report["blockers"]["integration"])
        self.assertIn("not", report["blockers"]["integration"])

    def test_report_records_exact_source_hashes_and_observed_routing(self):
        report = json.loads(self.outputs()["validation-report.json"])
        self.assertEqual(set(SOURCE_PATHS), set(report["source_sha256"]))
        for relative in SOURCE_PATHS:
            self.assertEqual(
                self.module.sha256_bytes((self.root / relative).read_bytes()),
                report["source_sha256"][relative],
            )
        self.assertEqual(
            "write the spec and plan to docs/plans/", report["observed"]["legacy_session_start"],
        )
        self.assertEqual("@urruegg", report["observed"]["codeowner"])
        self.assertIn("not a dedicated credential-isolated sandbox", report["blockers"]["isolation"])

    def test_settings_are_proposed_not_current_and_contain_native_requirements(self):
        settings = json.loads(self.outputs()["settings-proposal.json"])
        self.assertEqual("Proposed; not applied", settings["status"])
        self.assertIsNone(settings["verified_current"])
        desired = settings["desired"]
        self.assertEqual({"SHOWCASE_ENABLED": False, "RELEASE_ENABLED": False}, desired["flags"])
        protection = desired["main"]
        self.assertTrue(protection["require_pull_request"])
        self.assertEqual(1, protection["required_eligible_human_approvals"])
        self.assertEqual("@urruegg", protection["codeowner"])
        for key in ("dismiss_stale_reviews", "require_latest_push_approval", "resolve_conversations"):
            self.assertTrue(protection[key])
        self.assertEqual([], protection["routine_bypass"])
        self.assertEqual(
            ["L1 quality gate", "L2 browser tests", "IaC validation", "Governance eligibility"],
            protection["required_checks"],
        )
        self.assertIn("App-origin", protection["origins"])
        self.assertIn("current source/base/control", protection["origins"])
        self.assertFalse(desired["private_environment_reviewers_supported"])
        self.assertFalse(desired["native_artifact_attestations_supported"])

    def test_app_actual_metadata_is_null_and_manifest_never_supplies_fake_identities(self):
        app = json.loads(self.outputs()["app-descriptor.json"])
        self.assertIsNone(app["actual_public_metadata"])
        self.assertFalse(app["independently_verified"])
        self.assertIsNone(app["proposed_manifest"]["name"])
        self.assertFalse(app["proposed_manifest"]["public"])
        self.assertIn("person-only", app["provisioning"])
        self.assertNotIn("private_key", app["proposed_manifest"])
        self.assertNotIn("client_id", app["proposed_manifest"])
        self.assertNotIn("987654", json.dumps(app))
        self.assertNotIn("246810", json.dumps(app))
        for job in app["installation_token_jobs"].values():
            self.assertEqual(["frontier-envisioning"], job["repositories"])
            self.assertTrue(job["permissions"])
            self.assertFalse(job["all_installation_defaults"])
        self.assertEqual(
            {"checks": "write", "actions": "read", "contents": "read", "pull_requests": "read"},
            app["installation_token_jobs"]["reporter"]["permissions"],
        )

    def test_reporter_is_pinned_metadata_only_without_token_output(self):
        app = json.loads(self.outputs()["app-descriptor.json"])
        example = app["trusted_metadata_reporter_example"]
        for expected in (
            "actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510 # v3",
            "id: app-token", "client-id: ${{ vars.GOVERNANCE_APP_CLIENT_ID }}",
            "private-key: ${{ secrets.GOVERNANCE_APP_PRIVATE_KEY }}",
            "repositories: frontier-envisioning", "permission-checks: write",
            "permission-actions: read", "permission-contents: read", "permission-pull-requests: read",
        ):
            self.assertIn(expected, example)
        for forbidden in ("outputs:", ".outputs.token", "permission-contents: write", "run:"):
            self.assertNotIn(forbidden, example)
        self.assertIn("never", app["token_boundary"])
        self.assertIn("candidate", app["token_boundary"])

    def test_one_checklist_preserves_history_and_stops_for_real_adoption(self):
        output = self.outputs()
        checklist = output["operator-checklist.md"]
        self.assertEqual(["operator-checklist.md"], [name for name in output if name.endswith(".md")])
        for expected in (
            "STOP", "@urruegg", "#8", "Accepted", "current-head", "latest-push", "CODEOWNERS",
            "SHOWCASE_ENABLED", "RELEASE_ENABLED", "GitHub Pro", "no routine bypass",
            "dedicated private proposal-input", "validator", "no secrets/write/OIDC",
            "accepted control", "reporter", "publishing isolated", "no privileged candidate checkout",
            "adoption revision", "capability proof", "No keys/tokens", "owner-scoped",
            "5f9d21953db9c968ae56ac6d485baff3fc09b0ce",
            "2d5a7ccfe684b052197697e3e65d265ca2fd6cb9",
            "9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89",
            "aa838fbb6df96766a632d6f6ec3151ca93c7803d",
            "release-manifest.json", "sbom-spdx.zip", "SHA256SUMS.txt",
            "no registry", "no retag", "no old publisher rerun", "no automatic-context relabelling",
        ):
            self.assertIn(expected.lower(), checklist.lower())
        self.assertIn("Customer neutrality", checklist)
        self.assertIn("licences", checklist)
        self.assertIn("no azure/admin/destructive/visibility/secret-rotation", checklist.lower())

    def test_report_observes_changed_hook_registration_instead_of_inventing_current_config(self):
        path = self.root / ".github/hooks/guardrails.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["hooks"]["sessionStart"] = []
        path.write_text(json.dumps(data) + "\n", encoding="utf-8", newline="\n")
        report = json.loads(self.outputs()["validation-report.json"])
        self.assertIsInstance(report["observed"]["hooks"], dict, "Missing actual hook-registration observations")
        self.assertFalse(report["observed"]["hooks"]["session_start_registered"])
        self.assertTrue(report["observed"]["hooks"]["guard_registered"])
        self.assertIn("source_configuration", report["blockers"])
        self.assertFalse(report["adoption_ready"])

    def test_invalid_or_duplicate_hook_json_is_nonzero_input_failure(self):
        path = self.root / ".github/hooks/guardrails.json"
        for value in (
            "{invalid\n", '{"hooks": {}, "hooks": {}}\n', '{"hooks": []}\n',
        ):
            with self.subTest(value=value):
                path.write_text(value, encoding="utf-8", newline="\n")
                code, stdout, stderr = self.call()
                self.assertEqual(1, code)
                self.assertEqual("", stdout)
                self.assertIn("source", stderr)
                self.assertFalse((self.root / "build").exists())

    def test_no_credential_environment_or_file_reads_and_no_source_execution(self):
        original = Path.read_bytes
        reads = []

        def recorded(path):
            reads.append(path.relative_to(self.root).as_posix())
            return original(path)

        hook = self.root / ".github/hooks/scripts/session_start.py"
        hook.write_text(
            hook.read_text(encoding="utf-8") + '\nraise RuntimeError("Source must never execute")\n',
            encoding="utf-8", newline="\n",
        )
        class UnreadableEnvironment(dict):
            def __getitem__(self, key):
                raise AssertionError("No environment reads")

            def get(self, key, default=None):
                raise AssertionError("No environment reads")

            def __iter__(self):
                raise AssertionError("No environment reads")

        with (
            patch.object(Path, "read_bytes", recorded),
            patch.object(os, "getenv", side_effect=AssertionError("No environment inspection")),
            patch.object(os, "environ", UnreadableEnvironment({"GH_TOKEN": "DO-NOT-READ"})),
            patch.object(subprocess, "Popen", side_effect=AssertionError("No process execution")),
            patch.object(socket, "socket", side_effect=AssertionError("No network")),
            patch.object(urllib.request, "urlopen", side_effect=AssertionError("No HTTP")),
        ):
            self.module.generate()
        self.assertEqual(sorted(SOURCE_PATHS), sorted(reads))
        self.assertNotIn("DO-NOT-READ", "".join(
            path.read_text(encoding="utf-8") for path in (self.root / "build/governance-bootstrap").iterdir()
        ))

    def test_cli_generation_reports_only_review_output_not_activation(self):
        code, stdout, stderr = self.call()
        self.assertEqual(0, code)
        self.assertEqual("", stderr)
        self.assertIn("review output only", stdout)
        self.assertIn("adoption BLOCKED", stdout)
        self.assertEqual(OUTPUT_NAMES, {path.name for path in (self.root / "build/governance-bootstrap").iterdir()})

    def test_cli_rejects_mutation_metadata_approval_and_arbitrary_output_arguments(self):
        for argv in (
            ["--apply"], ["--force"], ["--output", "../.github"],
            ["--output", str(self.root / ".github")], ["--output", "build/../.github"],
            ["--output", "BUILD/governance-bootstrap"], ["--approved", "true"],
            ["--app-metadata", '{"client_id":"fake","approved":true}'],
            ["--private-key", "DO-NOT-PRINT"],
        ):
            with self.subTest(argv=argv):
                code, stdout, stderr = self.call(argv)
                self.assertEqual(2, code)
                self.assertEqual("", stdout)
                self.assertNotIn("DO-NOT-PRINT", stderr)
                self.assertFalse((self.root / "build/governance-bootstrap").exists())

    def test_help_is_non_mutating(self):
        code, stdout, stderr = self.call(["--help"])
        self.assertEqual(0, code)
        self.assertIn("offline", stdout)
        self.assertEqual("", stderr)
        self.assertFalse((self.root / "build").exists())

    def test_missing_source_is_nonzero_before_any_output(self):
        (self.root / ".github/hooks/scripts/session_start.py").unlink()
        code, stdout, stderr = self.call()
        self.assertEqual(1, code)
        self.assertEqual("", stdout)
        self.assertIn("session_start.py", stderr)
        self.assertFalse((self.root / "build").exists())

    def test_invalid_utf8_is_nonzero_before_any_output(self):
        (self.root / "AGENTS.md").write_bytes(b"\xff")
        code, stdout, stderr = self.call()
        self.assertEqual(1, code)
        self.assertEqual("", stdout)
        self.assertIn("UTF-8", stderr)
        self.assertFalse((self.root / "build").exists())

    def test_unrecognised_template_or_routing_never_gets_a_fabricated_migration(self):
        for relative, old in (
            (".github/pull_request_template.md", "## Summary (written by a person, in your own words)"),
            (".github/hooks/scripts/session_start.py", "write the spec and plan to docs/plans/"),
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                seed(root)
                path = root / relative
                path.write_text(path.read_text(encoding="utf-8").replace(old, "unexpected"), encoding="utf-8", newline="\n")
                with patch.object(self.module, "ROOT", root):
                    code, stdout, stderr = self.call()
                self.assertEqual(1, code)
                self.assertEqual("", stdout)
                self.assertIn("source", stderr)
                self.assertFalse((root / "build").exists())

    def test_nonignored_build_is_an_input_failure(self):
        (self.root / ".gitignore").write_text("# No ignored output\n", encoding="utf-8", newline="\n")
        code, stdout, stderr = self.call()
        self.assertEqual(1, code)
        self.assertEqual("", stdout)
        self.assertIn("ignored", stderr)
        self.assertFalse((self.root / "build").exists())

    def test_existing_output_is_never_overwritten_even_if_empty_or_hardlinked(self):
        output = self.root / "build/governance-bootstrap"
        output.mkdir(parents=True)
        code, stdout, stderr = self.call()
        self.assertEqual(1, code)
        self.assertEqual("", stdout)
        self.assertIn("exists", stderr)
        os.link(self.root / "AGENTS.md", output / "migration-proposal.patch")
        before = (self.root / "AGENTS.md").read_bytes()
        self.assertEqual(1, self.call()[0])
        self.assertEqual(before, (self.root / "AGENTS.md").read_bytes())

    def test_output_directory_file_and_case_aliases_fail_without_source_mutation(self):
        for relative in ("build", "build/governance-bootstrap", "BUILD", "build/Governance-Bootstrap"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                seed(root)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"Never overwrite")
                before = snapshot(root)
                with patch.object(self.module, "ROOT", root):
                    self.assertEqual(1, self.call()[0])
                self.assertEqual(before, snapshot(root))

    def make_symlink(self, link, target, *, directory):
        try:
            link.symlink_to(target, target_is_directory=directory)
        except OSError as error:
            self.skipTest(f"OS symlink creation unavailable: {error}")

    def test_build_symlink_cannot_redirect_writes_into_active_source(self):
        self.make_symlink(self.root / "build", self.root / ".github", directory=True)
        before = snapshot(self.root / ".github")
        self.assertEqual(1, self.call()[0])
        self.assertEqual(before, snapshot(self.root / ".github"))
        self.assertFalse((self.root / ".github/governance-bootstrap").exists())

    def test_output_symlink_cannot_redirect_writes_into_active_source(self):
        (self.root / "build").mkdir()
        self.make_symlink(self.root / "build/governance-bootstrap", self.root / ".github", directory=True)
        before = snapshot(self.root / ".github")
        self.assertEqual(1, self.call()[0])
        self.assertEqual(before, snapshot(self.root / ".github"))

    def test_source_symlink_is_rejected_before_reading_its_target(self):
        source = self.root / ".github/pull_request_template.md"
        source.unlink()
        credential = self.root / "not-an-input.key"
        credential.write_bytes(b"DO-NOT-READ")
        self.make_symlink(source, credential, directory=False)
        with patch.object(Path, "read_bytes", side_effect=AssertionError("No source read before preflight")):
            self.assertEqual(1, self.call()[0])
        self.assertFalse((self.root / "build").exists())

    def test_root_symlink_is_not_an_arbitrary_output_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            alias = Path(temporary) / "alias"
            self.make_symlink(alias, self.root, directory=True)
            with patch.object(self.module, "ROOT", alias):
                self.assertEqual(1, self.call()[0])
        self.assertFalse((self.root / "build").exists())

    def test_windows_reparse_directory_is_rejected_without_following_it(self):
        original = Path.lstat

        def reparse(path):
            value = original(path)
            if path == self.root / ".github":
                class Reparse:
                    st_mode = value.st_mode
                    st_file_attributes = stat.FILE_ATTRIBUTE_REPARSE_POINT
                return Reparse()
            return value

        with patch.object(Path, "lstat", reparse):
            code, _, stderr = self.call()
        self.assertEqual(1, code)
        self.assertIn("reparse", stderr)
        self.assertFalse((self.root / "build").exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction regression")
    def test_actual_windows_junctions_cannot_redirect_output_or_source(self):
        # Windows' stdlib helper needs no symlink privilege and starts no process.
        import _winapi

        for kind in ("build", "output", "source", "root"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temporary:
                outer = Path(temporary)
                root = outer / "repository"
                root.mkdir()
                seed(root)
                target = root / ".github"
                invocation_root = root
                if kind == "build":
                    link = root / "build"
                elif kind == "output":
                    (root / "build").mkdir()
                    link = root / "build/governance-bootstrap"
                elif kind == "source":
                    target = outer / "source"
                    (root / ".github").rename(target)
                    link = root / ".github"
                else:
                    target = root
                    link = outer / "alias"
                    invocation_root = link
                _winapi.CreateJunction(str(target), str(link))
                before = snapshot(target)
                with (
                    patch.object(self.module, "ROOT", invocation_root),
                    patch.object(subprocess, "Popen", side_effect=AssertionError("No process execution")),
                ):
                    code, stdout, stderr = self.call()
                self.assertEqual(1, code)
                self.assertEqual("", stdout)
                self.assertRegex(stderr, "reparse|alias|link|exists")
                self.assertEqual(before, snapshot(target))

    def test_io_failure_is_nonzero_and_does_not_print_success(self):
        original = Path.open

        def denied_write(path, mode="r", *args, **kwargs):
            if mode == "x":
                raise PermissionError("Simulated write denial")
            return original(path, mode, *args, **kwargs)

        with patch.object(Path, "open", denied_write):
            code, stdout, stderr = self.call()
        self.assertEqual(1, code)
        self.assertEqual("", stdout)
        self.assertIn("denial", stderr)
        self.assertFalse((self.root / "build/governance-bootstrap/validation-report.json").exists())

    def test_unexpected_errors_are_not_swallowed(self):
        with patch.object(self.module, "sha256_bytes", side_effect=RuntimeError("Unexpected bug")):
            with self.assertRaisesRegex(RuntimeError, "Unexpected bug"):
                self.call()


if __name__ == "__main__":
    unittest.main()
