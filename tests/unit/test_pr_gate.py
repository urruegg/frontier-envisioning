# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Offline synthetic snapshots: consistency tests, NOT authenticated GitHub proof."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.unit._util import ROOT, load

REPOSITORY = "urruegg/frontier-envisioning"
SOURCE = "a" * 40
BASE = "b" * 40
CONTROL = "c" * 40
INTENT = "d" * 40
MERGE = "e" * 40
RELEASE_SOURCE = "2d5a7ccfe684b052197697e3e65d265ca2fd6cb9"
TAG_OBJECT = "5f9d21953db9c968ae56ac6d485baff3fc09b0ce"


def policy():
    return {
        "schema": "frontier-pr-policy/1.0",
        "repository": REPOSITORY,
        "maintainer": {"login": "urruegg", "type": "User", "id": 174321},
        "machine_author": {
            "login": "frontier-proposals[bot]", "type": "Bot", "id": 246810, "app_id": 987654,
        },
        "source_sha": SOURCE, "base_sha": BASE, "control_sha": CONTROL,
        "allowed_paths": ["tools/", "tests/", "docs/", "drafts/", ".github/"],
        "protected_paths": [
            ".github/hooks/", ".github/agent-policy/", ".github/CODEOWNERS",
            ".github/workflows/release.yml",
        ],
        "actions": ["merge", "publish"],
        "checks": [
            {"name": name, "workflow_path": ".github/workflows/candidate.yml", "app_id": 15368}
            for name in ("L1 quality gate", "L2 browser tests", "IaC validation")
        ],
        "eligibility": {
            "name": "PR eligibility", "workflow_path": ".github/workflows/eligibility.yml",
            "app_id": 987654,
        },
    }


def proposal():
    return {
        "schema": "frontier-proposal/1.0", "repository": REPOSITORY,
        "source_sha": SOURCE, "base_sha": BASE,
        "paths": ["tools/example.py", "tests/unit/test_example.py"],
        "workflow_effects": [],
    }


def run(run_id=112233, workflow_path=".github/workflows/candidate.yml"):
    return {
        "id": run_id, "attempt": 1, "repository": REPOSITORY,
        "workflow_path": workflow_path, "workflow_sha": CONTROL, "head_sha": CONTROL,
        "source_sha": SOURCE, "base_sha": BASE, "ref": "refs/heads/main",
        "event": "workflow_dispatch", "status": "completed", "conclusion": "success",
    }


def check(name, check_id, run_id=112233, app_id=15368):
    return {
        "id": check_id, "name": name, "app_id": app_id,
        "run_id": run_id, "run_attempt": 1, "head_sha": SOURCE,
        "status": "completed", "conclusion": "success",
    }


def candidate():
    return {
        "schema": "frontier-pr-state/1.0", "repository": REPOSITORY, "pr_number": 149,
        "author": policy()["machine_author"],
        "head_sha": SOURCE, "tested_base_sha": BASE, "current_base_sha": BASE,
        "control_sha": CONTROL, "base_ref": "main", "pr_state": "OPEN", "draft": False,
        "proposal": proposal(), "runs": [run()],
        "checks": [
            check(name, 445566 + index)
            for index, name in enumerate(("L1 quality gate", "L2 browser tests", "IaC validation"))
        ],
    }


def action_intent(action="merge", release=None):
    result = {
        "schema": "frontier-action-intent/1.0", "repository": REPOSITORY,
        "action": action, "head_sha": SOURCE, "intent_sha": INTENT,
    }
    if release is not None:
        result["release"] = release
    return result


def reviewed():
    result = candidate()
    result.update({
        "intent_sha": INTENT,
        "effective_owner_review": {
            "id": 778899, "reviewer": policy()["maintainer"],
            "state": "APPROVED", "commit_id": SOURCE, "intent_sha": INTENT,
        },
        "native_review_decision": "APPROVED",
        "eligibility": check("PR eligibility", 445570, 112234, 987654),
    })
    result["runs"].append(run(112234, ".github/workflows/eligibility.yml"))
    return result


def release_intent(source_mode="merged-pr", publish=True):
    return {
        "schema": "frontier-release-intent/1.0", "repository": REPOSITORY,
        "publish": publish, "version": "1.10.0", "tag": "v1.10.0",
        "source_mode": source_mode,
        "source": (
            {"pr_number": 149} if source_mode == "merged-pr"
            else {"commit_sha": RELEASE_SOURCE, "tag_object_sha": TAG_OBJECT}
        ),
        "assets": [
            "frontier-envisioning-plugin-1.10.0.zip", "release-manifest.json",
            "sbom-spdx.zip", "SHA256SUMS.txt",
        ],
    }


def workflow_effect(path):
    return {
        "schema": "frontier-workflow-facts/1.0", "path": path,
        "parser_control_sha": CONTROL, "execution": "data-only",
        "permissions": {"contents": "read"}, "secrets": [],
        "executes_proposal": False, "privileged_effects": [],
    }


def change(data, dotted, value):
    """Mutate a deep-copied fixture, including list indices."""
    result = copy.deepcopy(data)
    keys = dotted.split(".")
    node = result
    for key in keys[:-1]:
        node = node[int(key)] if isinstance(node, list) else node[key]
    key = int(keys[-1]) if isinstance(node, list) else keys[-1]
    node[key] = value
    return result


class GateTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(
            (ROOT / "tools/pr_gate.py").is_file(),
            "missing pure contract implementation tools/pr_gate.py",
        )
        self.gate = load("tools/pr_gate.py")

    def rejected(self, function, data, message, *args):
        with self.assertRaisesRegex(self.gate.GateError, message):
            getattr(self.gate, function)(data, *args, policy())


class ProposalTests(GateTests):
    def test_scoped_proposal_is_valid(self):
        self.assertTrue(self.gate.validate_proposal(proposal(), policy()))

    def test_rejects_unsafe_paths(self):
        for path in (
            "../tools/x.py", "/tools/x.py", r"tools\x.py", "C:/tools/x.py",
            "tools//x.py", "tools/./x.py", "tools/../x.py", "tools/x.py/",
            "tools/x.py ", "tools/x.py.", "tools/CON.py", ".git/config",
            "tools/.env", "tools/.ssh/config", "infra/admin.bicep",
        ):
            with self.subTest(path=path):
                self.rejected("validate_proposal", change(proposal(), "paths", [path]), "path")

    def test_rejects_duplicates_case_aliases_and_empty_scope(self):
        for paths in ([], ["tools/x.py", "tools/x.py"], ["tools/x.py", "TOOLS/X.py"]):
            with self.subTest(paths=paths):
                self.rejected("validate_proposal", change(proposal(), "paths", paths), "paths")

    def test_rejects_active_policy_and_credentials(self):
        for path in (
            ".github/hooks/scripts/guard.py", ".github/agent-policy/authority.json",
            ".github/CODEOWNERS", ".github/workflows/release.yml", ".github/credentials/key",
        ):
            with self.subTest(path=path):
                self.rejected("validate_proposal", change(proposal(), "paths", [path]), "path")

    def test_drafts_are_data_not_a_blanket_guard_filename_ban(self):
        data = change(proposal(), "paths", ["drafts/.github/hooks/scripts/guard.py"])
        self.assertTrue(self.gate.validate_proposal(data, policy()))

    def test_workflow_proposal_needs_bound_normalized_facts(self):
        path = ".github/workflows/new-validation.yml"
        data = change(proposal(), "paths", [path])
        self.rejected("validate_proposal", data, "workflow_effects")
        data["workflow_effects"] = [workflow_effect(path)]
        self.assertTrue(self.gate.validate_proposal(data, policy()))

    def test_id_token_read_is_not_a_valid_readonly_permission(self):
        path = ".github/workflows/new-validation.yml"
        data = change(proposal(), "paths", [path])
        data["workflow_effects"] = [workflow_effect(path)]
        data["workflow_effects"][0]["permissions"] = {"id-token": "read"}
        self.rejected("validate_proposal", data, "permissions")

    def test_unsafe_workflow_effects_and_caller_boolean_rejected(self):
        path = "drafts/.github/workflows/release.yml"
        data = change(proposal(), "paths", [path])
        data["workflow_effects"] = [workflow_effect(path)]
        for field, value in (
            ("permissions", {"contents": "write"}), ("permissions", {"id-token": "write"}),
            ("secrets", ["TOKEN"]), ("execution", "execute"),
            ("executes_proposal", True), ("executes_proposal", 0),
            ("privileged_effects", ["publish"]), ("parser_control_sha", SOURCE),
            ("schema", "raw-yaml"), ("safe", True),
        ):
            with self.subTest(field=field, value=value):
                self.rejected(
                    "validate_proposal", change(data, f"workflow_effects.0.{field}", value),
                    "workflow_effects",
                )
        data["workflow_effects"] = [{"path": path, "safe": True}]
        self.rejected("validate_proposal", data, "workflow_effects")

    def test_source_base_and_unknown_fields_fail_closed(self):
        for field, value in (
            ("source_sha", CONTROL), ("base_sha", SOURCE), ("source_sha", None),
            ("repository", "other/repo"), ("schema", "unknown"), ("approved", True),
        ):
            with self.subTest(field=field):
                self.rejected("validate_proposal", change(proposal(), field, value), field)


class CandidateTests(GateTests):
    def test_candidate_precedes_review_and_eligibility(self):
        self.assertTrue(self.gate.validate_candidate(candidate(), policy()))
        self.assertTrue(self.gate.validate_candidate(change(candidate(), "draft", True), policy()))

    def test_rejects_non_successful_or_missing_checks(self):
        for field, value in (
            ("conclusion", "failure"), ("conclusion", "skipped"), ("conclusion", "neutral"),
            ("conclusion", "unknown"), ("conclusion", None), ("status", "queued"),
        ):
            with self.subTest(field=field, value=value):
                self.rejected("validate_candidate", change(candidate(), f"checks.0.{field}", value), "check")
        for index in range(3):
            data = candidate()
            del data["checks"][index]
            self.rejected("validate_candidate", data, "missing required check")

    def test_duplicate_ambiguous_and_unknown_checks_rejected(self):
        data = candidate()
        data["checks"].append(copy.deepcopy(data["checks"][0]))
        self.rejected("validate_candidate", data, "duplicate")
        data["checks"][-1]["id"] += 10
        self.rejected("validate_candidate", data, "duplicate")
        self.rejected("validate_candidate", change(candidate(), "checks.1.id", 445566), "duplicate")
        self.rejected("validate_candidate", change(candidate(), "checks.0.name", "custom"), "unknown check")

    def test_wrong_check_origin_or_binding_rejected(self):
        for field, value in (
            ("app_id", 999), ("run_id", 999), ("run_attempt", 2), ("head_sha", CONTROL),
            ("id", True), ("id", 0), ("run_id", "112233"),
        ):
            with self.subTest(field=field):
                self.rejected("validate_candidate", change(candidate(), f"checks.0.{field}", value), "check")

    def test_wrong_run_origin_workflow_control_source_and_base_rejected(self):
        for field, value in (
            ("repository", "other/repo"), ("workflow_path", ".github/workflows/untrusted.yml"),
            ("workflow_sha", SOURCE), ("head_sha", SOURCE), ("source_sha", CONTROL),
            ("base_sha", SOURCE), ("ref", "refs/heads/proposal"),
            ("event", "pull_request_target"), ("status", "in_progress"),
            ("conclusion", "skipped"), ("attempt", False),
        ):
            with self.subTest(field=field):
                self.rejected("validate_candidate", change(candidate(), f"runs.0.{field}", value), "run")

    def test_duplicate_or_orphan_runs_rejected(self):
        data = candidate()
        data["runs"].append(copy.deepcopy(data["runs"][0]))
        self.rejected("validate_candidate", data, "duplicate")
        data["runs"][-1]["id"] += 7
        self.rejected("validate_candidate", data, "unused run")

    def test_source_current_base_control_and_target_rejected(self):
        for field, value in (
            ("head_sha", CONTROL), ("tested_base_sha", SOURCE), ("current_base_sha", SOURCE),
            ("control_sha", SOURCE), ("base_ref", "feature"), ("draft", "false"),
            ("pr_number", True), ("schema", "frontier-pr-state/2.0"),
        ):
            with self.subTest(field=field):
                self.rejected("validate_candidate", change(candidate(), field, value), field)

    def test_candidate_validates_proposal_not_only_check_names(self):
        self.rejected(
            "validate_candidate", change(candidate(), "proposal.paths", ["../x.py"]), "path",
        )

    def test_present_optional_facts_have_strict_types_without_requiring_approval(self):
        for field, value in (
            ("merge_commit_sha", False), ("tag", {"name": "v1.10.0", "approved": True}),
            ("intent_sha", []), ("effective_owner_review", True),
            ("native_review_decision", True),
        ):
            with self.subTest(field=field):
                self.rejected("validate_candidate", change(candidate(), field, value), field)
        data = candidate()
        data["effective_owner_review"] = change(
            reviewed()["effective_owner_review"], "state", "CHANGES_REQUESTED",
        )
        data["native_review_decision"] = "CHANGES_REQUESTED"
        self.assertTrue(self.gate.validate_candidate(data, policy()))

    def test_malformed_types_shas_and_missing_fields_are_explicit(self):
        for value in ("a" * 39, "A" * 40, "z" * 40, "0" * 40, [], False):
            with self.subTest(value=value):
                self.rejected("validate_candidate", change(candidate(), "head_sha", value), "head_sha")
        for field in candidate():
            data = candidate()
            del data[field]
            with self.subTest(missing=field):
                self.rejected("validate_candidate", data, field)
        for value in (None, [], True):
            self.rejected("validate_candidate", value, "state")


class ActionTests(GateTests):
    def test_current_owner_review_allows_declared_engineering_merge(self):
        self.assertTrue(self.gate.authorize_action(reviewed(), action_intent(), policy()))

    def test_effective_review_regressions_rejected(self):
        for field, value in (
            ("state", "COMMENTED"), ("state", "CHANGES_REQUESTED"), ("state", "DISMISSED"),
            ("reviewer.type", "Bot"), ("reviewer.login", "other"),
            ("reviewer.login", "frontier-proposals[bot]"), ("reviewer.id", 999),
            ("commit_id", BASE), ("intent_sha", BASE), ("id", True), ("approved", True),
        ):
            with self.subTest(field=field, value=value):
                self.rejected(
                    "authorize_action", change(reviewed(), f"effective_owner_review.{field}", value),
                    "review", action_intent(),
                )

    def test_current_native_review_decision_is_required(self):
        for decision in ("CHANGES_REQUESTED", "REVIEW_REQUIRED", "COMMENTED", None):
            with self.subTest(decision=decision):
                self.rejected(
                    "authorize_action", change(reviewed(), "native_review_decision", decision),
                    "native_review_decision", action_intent(),
                )

    def test_new_head_or_latest_intent_invalidates_old_approval(self):
        self.rejected("authorize_action", change(reviewed(), "head_sha", BASE), "head_sha", action_intent())
        self.rejected("authorize_action", change(reviewed(), "intent_sha", BASE), "intent_sha", action_intent())
        self.rejected(
            "authorize_action", reviewed(), "intent_sha", change(action_intent(), "intent_sha", BASE),
        )

    def test_configured_actual_machine_author_required(self):
        for field, value in (
            ("login", "urruegg"), ("login", "other[bot]"), ("type", "User"),
            ("id", True), ("app_id", 999),
        ):
            with self.subTest(field=field):
                self.rejected("authorize_action", change(reviewed(), f"author.{field}", value), "author", action_intent())

    def test_missing_review_eligibility_or_core_checks_rejected(self):
        for field in ("effective_owner_review", "native_review_decision", "eligibility", "intent_sha"):
            data = reviewed()
            del data[field]
            with self.subTest(field=field):
                self.rejected("authorize_action", data, field, action_intent())
        data = reviewed()
        data["checks"].pop()
        self.rejected("authorize_action", data, "missing required check", action_intent())
        for field, value in (
            ("app_id", 15368), ("head_sha", BASE), ("conclusion", "failure"), ("run_id", 112233),
        ):
            self.rejected(
                "authorize_action", change(reviewed(), f"eligibility.{field}", value),
                "eligibility", action_intent(),
            )

    def test_draft_closed_merged_or_undeclared_merge_rejected(self):
        for field, value in (("draft", True), ("pr_state", "CLOSED"), ("pr_state", "MERGED")):
            self.rejected("authorize_action", change(reviewed(), field, value), field, action_intent())
        restricted = change(policy(), "actions", ["publish"])
        with self.assertRaisesRegex(self.gate.GateError, "action"):
            self.gate.authorize_action(reviewed(), action_intent(), restricted)
        for intent in (None, {}, change(action_intent(), "action", "deploy"), change(action_intent(), "head_sha", BASE)):
            self.rejected("authorize_action", reviewed(), "intent", intent)

    def test_publish_requires_explicit_true_intent_and_actual_merge(self):
        state = reviewed()
        state.update(pr_state="MERGED", merge_commit_sha=MERGE, current_base_sha=MERGE)
        intent = action_intent("publish", release_intent())
        self.assertTrue(self.gate.authorize_action(state, intent, policy()))
        self.rejected("authorize_action", state, "release", action_intent("publish"))
        self.rejected("authorize_action", state, "publish", action_intent("publish", release_intent(publish=False)))
        self.rejected("authorize_action", reviewed(), "pr_state", intent)
        del state["merge_commit_sha"]
        self.rejected("authorize_action", state, "merge_commit_sha", intent)

    def test_existing_tag_publication_requires_exact_objects_and_merged_request(self):
        state = reviewed()
        state.update(
            pr_state="MERGED", merge_commit_sha=MERGE, current_base_sha=MERGE,
            tag={"name": "v1.10.0", "commit_sha": RELEASE_SOURCE, "object_sha": TAG_OBJECT},
        )
        intent = action_intent("publish", release_intent("existing-tag"))
        self.assertTrue(self.gate.authorize_action(state, intent, policy()))
        for field, value in (("name", "v1.10.1"), ("commit_sha", SOURCE), ("object_sha", CONTROL)):
            self.rejected("authorize_action", change(state, f"tag.{field}", value), "tag", intent)
        del state["tag"]
        self.rejected("authorize_action", state, "tag", intent)
        self.rejected("authorize_action", reviewed(), "pr_state", intent)

    def test_publication_binds_actual_main_merge_without_changing_tested_base(self):
        state = reviewed()
        state.update(pr_state="MERGED", merge_commit_sha=MERGE, current_base_sha=MERGE)
        intent = action_intent("publish", release_intent())
        self.assertTrue(self.gate.authorize_action(state, intent, policy()))
        for field, value in (
            ("current_base_sha", BASE), ("current_base_sha", CONTROL),
            ("tested_base_sha", MERGE), ("merge_commit_sha", BASE),
        ):
            self.rejected("authorize_action", change(state, field, value), "base_sha", intent)
        existing = action_intent("publish", release_intent("existing-tag"))
        state["tag"] = {"name": "v1.10.0", "commit_sha": RELEASE_SOURCE, "object_sha": TAG_OBJECT}
        del state["merge_commit_sha"]
        self.rejected("authorize_action", state, "merge_commit_sha", existing)

    def test_merge_with_release_false_still_does_not_publish(self):
        intent = action_intent("merge", release_intent(publish=False))
        self.assertTrue(self.gate.authorize_action(reviewed(), intent, policy()))
        self.rejected(
            "authorize_action", reviewed(), "pr_number",
            action_intent("merge", change(release_intent(), "source.pr_number", 999)),
        )


class ReleaseIntentTests(GateTests):
    def test_both_source_modes_and_explicit_false_structurally_valid(self):
        for mode in ("merged-pr", "existing-tag"):
            for publish in (False, True):
                self.assertTrue(self.gate.validate_release_intent(release_intent(mode, publish), policy()))

    def test_strict_publish_schema_identity_version_and_assets(self):
        for field, value in (
            ("publish", None), ("publish", 1), ("publish", "true"), ("schema", "unknown"),
            ("repository", "other/repo"), ("version", "01.10.0"), ("version", "1.10"),
            ("version", "1.10.0-rc1"), ("tag", "1.10.0"), ("tag", "v1.10.1"),
            ("source_mode", "branch"), ("destination", "registry"), ("azure", {}),
            ("visibility", "public"), ("assets", []),
            ("assets", release_intent()["assets"] + ["other.zip"]),
            ("assets", ["https://example.test/plugin.zip", *release_intent()["assets"][1:]]),
        ):
            with self.subTest(field=field, value=value):
                self.rejected("validate_release_intent", change(release_intent(), field, value), field)
        for field in release_intent():
            data = release_intent()
            del data[field]
            self.rejected("validate_release_intent", data, field)
        data = release_intent()
        data["assets"][0] = "frontier-envisioning-plugin-1.10.1.zip"
        self.rejected("validate_release_intent", data, "assets")

    def test_source_modes_cannot_invent_future_sha_or_omit_tag_identity(self):
        for source in (
            {}, {"pr_number": True}, {"pr_number": 0},
            {"pr_number": 149, "commit_sha": MERGE},
            {"commit_sha": RELEASE_SOURCE, "tag_object_sha": TAG_OBJECT},
        ):
            self.rejected("validate_release_intent", change(release_intent(), "source", source), "source")
        for source in (
            {}, {"commit_sha": RELEASE_SOURCE}, {"commit_sha": "abc", "tag_object_sha": TAG_OBJECT},
            {"commit_sha": RELEASE_SOURCE, "tag_object_sha": True},
            {"commit_sha": RELEASE_SOURCE, "tag_object_sha": TAG_OBJECT, "repository": "other/repo"},
        ):
            self.rejected(
                "validate_release_intent", change(release_intent("existing-tag"), "source", source), "source",
            )

    def test_policy_is_explicit_trusted_input_not_candidate_override(self):
        for field, value in (
            ("maintainer", None), ("machine_author.type", "User"), ("control_sha", SOURCE),
            ("checks", []), ("actions", []), ("actions", ["admin"]), ("allowed_paths", []),
            ("protected_paths", []), ("schema", "unknown"), ("repository", "other/repo"),
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(self.gate.GateError, "policy"):
                    self.gate.validate_candidate(candidate(), change(policy(), field, value))
        data = candidate()
        data["policy"] = policy()
        self.rejected("validate_candidate", data, "policy")


class CliTests(GateTests):
    def invoke(self, mode, data, intent=None, raw=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_path = root / "input.json"
            policy_path = root / "policy.json"
            input_path.write_text(raw if raw is not None else json.dumps(data), encoding="utf-8", newline="\n")
            policy_path.write_text(json.dumps(policy()), encoding="utf-8", newline="\n")
            argv = [mode, "--input", str(input_path), "--policy", str(policy_path)]
            if intent is not None:
                intent_path = root / "intent.json"
                intent_path.write_text(json.dumps(intent), encoding="utf-8", newline="\n")
                argv.extend(["--intent", str(intent_path)])
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            output, errors = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                code = self.gate.main(argv)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, before)
            return code, output.getvalue(), errors.getvalue()

    def test_cli_checks_each_complete_contract(self):
        for mode, data, intent in (
            ("proposal", proposal(), None), ("candidate", candidate(), None),
            ("action", reviewed(), action_intent()), ("release-intent", release_intent(), None),
        ):
            with self.subTest(mode=mode):
                self.assertEqual(self.invoke(mode, data, intent), (0, f"VALID {mode}\n", ""))

    def test_cli_invalid_input_missing_intent_and_json_are_nonzero(self):
        for mode, data, raw, message in (
            ("candidate", change(candidate(), "head_sha", "bad"), None, "head_sha"),
            ("action", reviewed(), None, "intent"),
            ("candidate", None, "{", "invalid JSON"),
            ("candidate", None, '{"schema":"x","schema":"y"}', "duplicate JSON field"),
            ("candidate", None, '{"schema":NaN}', "non-finite JSON"),
            ("candidate", [], None, "state"),
        ):
            with self.subTest(mode=mode, message=message):
                code, output, error = self.invoke(mode, data, raw=raw)
                self.assertEqual(code, 1)
                self.assertEqual(output, "")
                self.assertIn(message, error)
                self.assertNotIn("Traceback", error)

    def test_missing_file_or_invalid_utf8_is_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            args = ["candidate", "--input", str(path), "--policy", str(path)]
            for content, message in ((None, "cannot read"), (b"\xff", "UTF-8")):
                if content is not None:
                    path.write_bytes(content)
                errors = io.StringIO()
                with contextlib.redirect_stderr(errors):
                    self.assertEqual(self.gate.main(args), 1)
                self.assertIn(message, errors.getvalue())

    def test_unexpected_intent_parameter_is_not_silently_ignored(self):
        code, output, errors = self.invoke("candidate", candidate(), action_intent())
        self.assertEqual(code, 1)
        self.assertEqual(output, "")
        self.assertIn("--intent", errors)

    def test_extreme_json_integer_and_nesting_fail_without_traceback(self):
        for raw, message in (
            ('{"id":' + "9" * 5000 + "}", "JSON integer"),
            ("[" * 2000 + "0" + "]" * 2000, "JSON nesting"),
        ):
            with self.subTest(message=message):
                code, output, error = self.invoke("candidate", None, raw=raw)
                self.assertEqual(code, 1)
                self.assertEqual(output, "")
                self.assertIn(message, error)
                self.assertNotIn("Traceback", error)

    def test_actual_checking_cli_has_deterministic_utf8_lf_and_no_write_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            for name, data in (("input", candidate()), ("policy", policy())):
                (path / f"{name}.json").write_text(json.dumps(data), encoding="utf-8", newline="\n")
            args = [
                sys.executable, str(ROOT / "tools/pr_gate.py"), "candidate",
                "--input", str(path / "input.json"), "--policy", str(path / "policy.json"),
            ]
            first = subprocess.run(args, capture_output=True, check=False)
            second = subprocess.run(args, capture_output=True, check=False)
            self.assertEqual((first.returncode, first.stdout, first.stderr), (0, b"VALID candidate\n", b""))
            self.assertEqual((second.returncode, second.stdout, second.stderr), (0, first.stdout, b""))
            bad = subprocess.run(args + ["--write"], capture_output=True, check=False)
            self.assertEqual(bad.returncode, 2)
            self.assertIn(b"unrecognized arguments", bad.stderr)
            help_result = subprocess.run(args[:2] + ["--help"], capture_output=True, check=False)
            self.assertEqual(help_result.returncode, 0)
            self.assertIn(b"does not authenticate", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
