# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Check pure proposal, candidate, action and release-intent contracts offline.

This checks consistency of trusted, normalised DATA ONLY: it does not authenticate
GitHub, attest a build, grant operational authority or execute an action. No
network, credential access, execution or write mode exists. Success is not proof
of review, credential isolation, policy adoption or publication. Current guards
remain active; collector, trusted workflow parser, native protection and publisher
are later stages.

All objects have exact fields (unknown/missing fields fail). Full SHAs are
lower-case 40-digit hex; IDs/attempts are positive integers, never booleans.
Functions return True on consistency, otherwise raise GateError. Inputs are not
mutated. CLI: MODE --input snapshot.json --policy policy.json; action also needs
--intent action.json. Expected invalid input returns 1; usage errors return 2.
The JSON reader rejects duplicate fields, non-finite constants, integer literals
over 100 digits and nesting beyond the standard decoder's recursion limit.

Normalised v1 contracts (see the synthetic unittest fixtures for complete shapes):
* frontier-pr-policy/1.0: repository, maintainer {login,type,id}, machine_author
  {login,type,id,app_id}, source_sha, base_sha, control_sha, allowed_paths,
  protected_paths, actions, checks [{name,workflow_path,app_id}], eligibility
  {name,workflow_path,app_id}. This is ACCEPTED TRUSTED CONTROLLER policy, never
  candidate policy. Scope entries are exact paths or directory prefixes ending /.
* frontier-proposal/1.0: repository, source_sha, base_sha, paths, workflow_effects.
  Workflow paths require frontier-workflow-facts/1.0 records: path,
  parser_control_sha, execution=data-only, permissions (read/none), secrets=[],
  executes_proposal=false, privileged_effects=[]. These are facts from a later
  trusted parser at control_sha, NOT a caller's assertion that raw YAML is safe.
  Draft guard/workflow documents can be data within explicitly adopted scope;
  active policy paths remain protected by the trusted policy.
* frontier-pr-state/1.0: repository, pr_number, author, head_sha, tested_base_sha,
  current_base_sha, control_sha, base_ref, pr_state, draft, proposal, runs, checks.
  Runs: id,attempt,repository,workflow_path,workflow_sha,head_sha,source_sha,
  base_sha,ref,event,status,conclusion. Trusted-main dispatch runs execute CONTROL,
  not proposal code; source_sha/base_sha identify the tested checkout. Checks:
  id,name,app_id,run_id,run_attempt,head_sha,status,conclusion. Their head_sha
  binds the SOURCE result, not the controller run head. Collectors must verify
  these origin/binding facts against actual runs/checks, not copy PR claims.
  Optional eligibility uses the same check shape. Candidate validation requires
  the three core checks only: no circular review/eligibility dependency. Optional
  facts, when present, must have valid shapes but do not grant candidate approval.
* Action additionally requires state intent_sha, effective_owner_review
  {id,reviewer:{login,type,id},state,commit_id,intent_sha}, native_review_decision.
  The collector must supply the EFFECTIVE owner review and CURRENT native
  decision, including later changes/dismissals; no comment/history inference.
  frontier-action-intent/1.0: repository,action,head_sha,intent_sha, optional
  release. intent_sha denotes the immutable latest intent revision, bound by the
  collector to these exact contents and the review; it is not a caller approval
  boolean or a locally verified cryptographic attestation.
  Engineering merge uses current_base_sha=policy.base_sha. Publication requires
  actual merge_commit_sha of the reviewed PR and current_base_sha equal to that
  protected main merge, while tested_base_sha/proposal/runs stay bound to the
  original policy.base_sha. Further main advancement fails closed.
* frontier-release-intent/1.0: repository,publish (explicit bool),version,tag,
  source_mode,source,assets. merged-pr source={pr_number}, resolved to actual
  state merge_commit_sha only after protected merge, never a future SHA.
  existing-tag source={commit_sha,tag_object_sha}, compared to actual state
  tag={name,commit_sha,object_sha}; an approved machine-authored intent PR must
  already be merged. Only GitHub Releases in urruegg/frontier-envisioning and
  frontier-envisioning-plugin-VERSION.zip, release-manifest.json, sbom-spdx.zip,
  SHA256SUMS.txt are in scope. publish=false is valid data but never publication.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPOSITORY = "urruegg/frontier-envisioning"
CORE_CHECKS = {"L1 quality gate", "L2 browser tests", "IaC validation"}
STATE_FIELDS = {
    "schema", "repository", "pr_number", "author", "head_sha", "tested_base_sha",
    "current_base_sha", "control_sha", "base_ref", "pr_state", "draft", "proposal",
    "runs", "checks",
}
STATE_OPTIONAL = {
    "eligibility", "intent_sha", "effective_owner_review", "native_review_decision",
    "merge_commit_sha", "tag",
}


class GateError(ValueError):
    """An explicit contract violation, not an operational error or approval."""


def _object(value, required: set[str], optional: set[str], label: str) -> dict:
    if not isinstance(value, dict):
        raise GateError(f"{label}: expected object")
    if any(not isinstance(key, str) for key in value):
        raise GateError(f"{label}: expected string field names")
    missing = required - value.keys()
    if missing:
        raise GateError(f"{label}: missing fields: {', '.join(sorted(missing))}")
    unknown = value.keys() - required - optional
    if unknown:
        raise GateError(f"{label}: unknown fields: {', '.join(sorted(unknown))}")
    return value


def _equal(value, expected, label: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise GateError(f"{label}: does not match required value")


def _positive(value, label: str) -> None:
    if type(value) is not int or value <= 0:
        raise GateError(f"{label}: expected positive integer")


def _sha(value, label: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value) or value == "0" * 40:
        raise GateError(f"{label}: expected full lower-case nonzero SHA")


def _boolean(value, label: str) -> None:
    if type(value) is not bool:
        raise GateError(f"{label}: expected boolean")


def _list(value, label: str, *, nonempty: bool = False) -> list:
    if not isinstance(value, list) or (nonempty and not value):
        raise GateError(f"{label}: expected {'nonempty ' if nonempty else ''}list")
    return value


def _text(value, label: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise GateError(f"{label}: expected nonempty canonical string")


def _identity(value, label: str, *, machine: bool) -> dict:
    keys = {"login", "type", "id"} | ({"app_id"} if machine else set())
    result = _object(value, keys, set(), label)
    _text(result["login"], f"{label}.login")
    pattern = r"[A-Za-z0-9-]+\[bot\]" if machine else r"[A-Za-z0-9-]+"
    if not re.fullmatch(pattern, result["login"]):
        raise GateError(f"{label}.login: invalid GitHub identity")
    _equal(result["type"], "Bot" if machine else "User", f"{label}.type")
    _positive(result["id"], f"{label}.id")
    if machine:
        _positive(result["app_id"], f"{label}.app_id")
    return result


def _path(value, label: str, *, scope: bool = False, sensitive: bool = True) -> str:
    _text(value, label)
    path = value[:-1] if scope and value.endswith("/") else value
    if not re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", path):
        raise GateError(f"{label}: unsafe repository path")
    reserved = {"con", "prn", "aux", "nul"} | {
        f"{prefix}{number}" for prefix in ("com", "lpt") for number in range(1, 10)
    }
    for part in path.split("/"):
        folded = part.casefold()
        if part in {".", ".."} or part.endswith(".") or folded.split(".")[0] in reserved:
            raise GateError(f"{label}: noncanonical repository path")
        if sensitive and (
            folded in {".git", ".ssh", ".azure", "credentials"}
            or folded == ".env" or folded.startswith(".env.")
        ):
            raise GateError(f"{label}: credential or repository-control path")
    return value


def _paths(value, label: str, *, scope: bool = False, sensitive: bool = True) -> list:
    paths = _list(value, label, nonempty=True)
    seen = set()
    for item in paths:
        _path(item, label, scope=scope, sensitive=sensitive)
        folded = item.casefold()
        if folded in seen:
            raise GateError(f"{label}: duplicate or case-ambiguous paths")
        seen.add(folded)
    return paths


def _within(path: str, scopes: list) -> bool:
    folded = path.casefold()
    return any(
        folded.startswith(scope.casefold()) if scope.endswith("/")
        else folded == scope.casefold()
        for scope in scopes
    )


def _workflow(path: str) -> bool:
    return (path.startswith(".github/workflows/") or "/.github/workflows/" in path) and (
        path.endswith(".yml") or path.endswith(".yaml")
    )


def _descriptor(value, label: str) -> dict:
    result = _object(value, {"name", "workflow_path", "app_id"}, set(), label)
    _text(result["name"], f"{label}.name")
    _path(result["workflow_path"], f"{label}.workflow_path")
    if not result["workflow_path"].startswith(".github/workflows/") or not _workflow(result["workflow_path"]):
        raise GateError(f"{label}.workflow_path: expected active workflow path")
    _positive(result["app_id"], f"{label}.app_id")
    return result


def _policy(policy) -> dict:
    p = _object(policy, {
        "schema", "repository", "maintainer", "machine_author", "source_sha", "base_sha",
        "control_sha", "allowed_paths", "protected_paths", "actions", "checks", "eligibility",
    }, set(), "policy")
    _equal(p["schema"], "frontier-pr-policy/1.0", "policy.schema")
    _equal(p["repository"], REPOSITORY, "policy.repository")
    _identity(p["maintainer"], "policy.maintainer", machine=False)
    _equal(p["maintainer"]["login"], "urruegg", "policy.maintainer.login")
    _identity(p["machine_author"], "policy.machine_author", machine=True)
    for field in ("source_sha", "base_sha", "control_sha"):
        _sha(p[field], f"policy.{field}")
    if p["source_sha"] == p["control_sha"]:
        raise GateError("policy.control_sha: source and control must be distinct")
    _paths(p["allowed_paths"], "policy.allowed_paths", scope=True, sensitive=False)
    _paths(p["protected_paths"], "policy.protected_paths", scope=True, sensitive=False)
    actions = _list(p["actions"], "policy.actions", nonempty=True)
    for action in actions:
        _text(action, "policy.actions")
        if action not in {"merge", "publish"}:
            raise GateError("policy.actions: unsupported action")
    if len(set(actions)) != len(actions):
        raise GateError("policy.actions: duplicate action")
    checks = _list(p["checks"], "policy.checks", nonempty=True)
    names = []
    for item in checks:
        names.append(_descriptor(item, "policy.checks")["name"])
    if len(set(names)) != len(names) or set(names) != CORE_CHECKS:
        raise GateError("policy.checks: expected exactly the three core checks")
    eligibility = _descriptor(p["eligibility"], "policy.eligibility")
    _equal(eligibility["name"], "PR eligibility", "policy.eligibility.name")
    _equal(eligibility["app_id"], p["machine_author"]["app_id"], "policy.eligibility.app_id")
    return p


def _proposal(proposal, p: dict) -> bool:
    data = _object(proposal, {
        "schema", "repository", "source_sha", "base_sha", "paths", "workflow_effects",
    }, set(), "proposal")
    _equal(data["schema"], "frontier-proposal/1.0", "proposal.schema")
    _equal(data["repository"], p["repository"], "proposal.repository")
    for field in ("source_sha", "base_sha"):
        _sha(data[field], f"proposal.{field}")
        _equal(data[field], p[field], f"proposal.{field}")
    paths = _paths(data["paths"], "proposal.paths")
    for path in paths:
        if not _within(path, p["allowed_paths"]) or _within(path, p["protected_paths"]):
            raise GateError("proposal.paths: path outside scope or protected active policy")
    workflow_paths = {path for path in paths if _workflow(path)}
    effects = _list(data["workflow_effects"], "proposal.workflow_effects")
    seen = set()
    for effect in effects:
        label = "proposal.workflow_effects"
        facts = _object(effect, {
            "schema", "path", "parser_control_sha", "execution", "permissions", "secrets",
            "executes_proposal", "privileged_effects",
        }, set(), label)
        _equal(facts["schema"], "frontier-workflow-facts/1.0", f"{label}.schema")
        _path(facts["path"], f"{label}.path")
        if facts["path"] not in workflow_paths or facts["path"] in seen:
            raise GateError(f"{label}.path: unexpected or duplicate workflow")
        seen.add(facts["path"])
        _sha(facts["parser_control_sha"], f"{label}.parser_control_sha")
        _equal(facts["parser_control_sha"], p["control_sha"], f"{label}.parser_control_sha")
        _equal(facts["execution"], "data-only", f"{label}.execution")
        permissions = _object(facts["permissions"], set(), {
            "actions", "attestations", "checks", "contents", "deployments", "discussions",
            "id-token", "issues", "packages", "pages", "pull-requests", "security-events", "statuses",
        }, f"{label}.permissions")
        for name, permission in permissions.items():
            allowed = {"none"} if name == "id-token" else {"read", "none"}
            if not isinstance(permission, str) or permission not in allowed:
                raise GateError(f"{label}.permissions: privileged or unknown permission")
        _equal(facts["secrets"], [], f"{label}.secrets")
        _boolean(facts["executes_proposal"], f"{label}.executes_proposal")
        _equal(facts["executes_proposal"], False, f"{label}.executes_proposal")
        _equal(facts["privileged_effects"], [], f"{label}.privileged_effects")
    if seen != workflow_paths:
        raise GateError("proposal.workflow_effects: missing trusted workflow facts")
    return True


def validate_proposal(proposal, policy) -> bool:
    """Validate scoped proposal data; raw workflow YAML is never accepted here."""
    return _proposal(proposal, _policy(policy))


def _run(value, p: dict) -> dict:
    label = "state.run"
    record = _object(value, {
        "id", "attempt", "repository", "workflow_path", "workflow_sha", "head_sha",
        "source_sha", "base_sha", "ref", "event", "status", "conclusion",
    }, set(), label)
    for field in ("id", "attempt"):
        _positive(record[field], f"{label}.{field}")
    _path(record["workflow_path"], f"{label}.workflow_path")
    _equal(record["repository"], p["repository"], f"{label}.repository")
    for field, expected in (
        ("workflow_sha", p["control_sha"]), ("head_sha", p["control_sha"]),
        ("source_sha", p["source_sha"]), ("base_sha", p["base_sha"]),
    ):
        _sha(record[field], f"{label}.{field}")
        _equal(record[field], expected, f"{label}.{field}")
    for field, expected in (
        ("ref", "refs/heads/main"), ("event", "workflow_dispatch"),
        ("status", "completed"), ("conclusion", "success"),
    ):
        _equal(record[field], expected, f"{label}.{field}")
    return record


def _check(value, descriptor: dict, runs: dict, p: dict, label: str) -> dict:
    record = _object(value, {
        "id", "name", "app_id", "run_id", "run_attempt", "head_sha", "status", "conclusion",
    }, set(), label)
    for field in ("id", "app_id", "run_id", "run_attempt"):
        _positive(record[field], f"{label}.{field}")
    _equal(record["name"], descriptor["name"], f"{label}.name")
    _equal(record["app_id"], descriptor["app_id"], f"{label}.app_id")
    _sha(record["head_sha"], f"{label}.head_sha")
    _equal(record["head_sha"], p["source_sha"], f"{label}.head_sha")
    _equal(record["status"], "completed", f"{label}.status")
    _equal(record["conclusion"], "success", f"{label}.conclusion")
    if record["run_id"] not in runs:
        raise GateError(f"{label}.run_id: missing bound run")
    run = runs[record["run_id"]]
    _equal(record["run_attempt"], run["attempt"], f"{label}.run_attempt")
    _equal(run["workflow_path"], descriptor["workflow_path"], f"{label}.run.workflow_path")
    return record


def _review(value) -> dict:
    label = "state.effective_owner_review"
    review = _object(value, {
        "id", "reviewer", "state", "commit_id", "intent_sha",
    }, set(), label)
    _positive(review["id"], f"{label}.id")
    _identity(review["reviewer"], f"{label}.reviewer", machine=False)
    _text(review["state"], f"{label}.state")
    if review["state"] not in {"APPROVED", "COMMENTED", "CHANGES_REQUESTED", "DISMISSED", "PENDING"}:
        raise GateError(f"{label}.state: unknown review state")
    for field in ("commit_id", "intent_sha"):
        _sha(review[field], f"{label}.{field}")
    return review


def _tag_record(value) -> dict:
    tag = _object(value, {"name", "commit_sha", "object_sha"}, set(), "state.tag")
    _text(tag["name"], "state.tag.name")
    for field in ("commit_sha", "object_sha"):
        _sha(tag[field], f"state.tag.{field}")
    return tag


def _optional_facts(data: dict) -> None:
    for field in ("merge_commit_sha", "intent_sha"):
        if field in data:
            _sha(data[field], f"state.{field}")
    if "effective_owner_review" in data:
        _review(data["effective_owner_review"])
    if "native_review_decision" in data:
        _text(data["native_review_decision"], "state.native_review_decision")
        if data["native_review_decision"] not in {"APPROVED", "CHANGES_REQUESTED", "REVIEW_REQUIRED"}:
            raise GateError("state.native_review_decision: unknown native decision")
    if "tag" in data:
        _tag_record(data["tag"])


def _candidate(state, p: dict, *, current_base_sha: str | None = None) -> bool:
    data = _object(state, STATE_FIELDS, STATE_OPTIONAL, "state")
    _equal(data["schema"], "frontier-pr-state/1.0", "state.schema")
    _equal(data["repository"], p["repository"], "state.repository")
    _positive(data["pr_number"], "state.pr_number")
    _identity(data["author"], "state.author", machine=True)
    _equal(data["author"], p["machine_author"], "state.author")
    for field, expected in (
        ("head_sha", p["source_sha"]), ("tested_base_sha", p["base_sha"]),
        ("current_base_sha", p["base_sha"] if current_base_sha is None else current_base_sha),
        ("control_sha", p["control_sha"]),
    ):
        _sha(data[field], f"state.{field}")
        _equal(data[field], expected, f"state.{field}")
    _equal(data["base_ref"], "main", "state.base_ref")
    _text(data["pr_state"], "state.pr_state")
    if data["pr_state"] not in {"OPEN", "MERGED", "CLOSED"}:
        raise GateError("state.pr_state: unknown native PR state")
    _boolean(data["draft"], "state.draft")
    _optional_facts(data)
    _proposal(data["proposal"], p)
    runs = {}
    for item in _list(data["runs"], "state.runs", nonempty=True):
        record = _run(item, p)
        if record["id"] in runs:
            raise GateError("state.runs: duplicate or ambiguous run")
        runs[record["id"]] = record
    descriptors = {item["name"]: item for item in p["checks"]}
    names, ids, used_runs = set(), set(), set()
    for item in _list(data["checks"], "state.checks", nonempty=True):
        _object(item, {
            "id", "name", "app_id", "run_id", "run_attempt", "head_sha", "status", "conclusion",
        }, set(), "state.check")
        _text(item["name"], "state.check.name")
        if item["name"] not in descriptors:
            raise GateError("state.check.name: unknown check")
        record = _check(item, descriptors[item["name"]], runs, p, "state.check")
        if record["id"] in ids or record["name"] in names:
            raise GateError("state.checks: duplicate or ambiguous check")
        ids.add(record["id"])
        names.add(record["name"])
        used_runs.add(record["run_id"])
    missing = CORE_CHECKS - names
    if missing:
        raise GateError(f"state.checks: missing required check: {', '.join(sorted(missing))}")
    if "eligibility" in data:
        record = _check(data["eligibility"], p["eligibility"], runs, p, "state.eligibility")
        if record["id"] in ids:
            raise GateError("state.eligibility: duplicate check ID")
        used_runs.add(record["run_id"])
    if used_runs != runs.keys():
        raise GateError("state.runs: unused run")
    return True


def validate_candidate(state, policy) -> bool:
    """Validate core candidate evidence without requiring/granting human approval."""
    return _candidate(state, _policy(policy))


def _release_intent(intent, p: dict) -> bool:
    data = _object(intent, {
        "schema", "repository", "publish", "version", "tag", "source_mode", "source", "assets",
    }, set(), "release intent")
    _equal(data["schema"], "frontier-release-intent/1.0", "release intent.schema")
    _equal(data["repository"], p["repository"], "release intent.repository")
    _boolean(data["publish"], "release intent.publish")
    version = data["version"]
    if not isinstance(version, str) or not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", version):
        raise GateError("release intent.version: expected canonical numeric version")
    _equal(data["tag"], f"v{version}", "release intent.tag")
    mode = data["source_mode"]
    if mode == "merged-pr":
        source = _object(data["source"], {"pr_number"}, set(), "release intent.source")
        _positive(source["pr_number"], "release intent.source.pr_number")
    elif mode == "existing-tag":
        source = _object(data["source"], {"commit_sha", "tag_object_sha"}, set(), "release intent.source")
        for field in ("commit_sha", "tag_object_sha"):
            _sha(source[field], f"release intent.source.{field}")
    else:
        raise GateError("release intent.source_mode: expected merged-pr or existing-tag")
    assets = _list(data["assets"], "release intent.assets", nonempty=True)
    expected = {
        f"frontier-envisioning-plugin-{version}.zip", "release-manifest.json",
        "sbom-spdx.zip", "SHA256SUMS.txt",
    }
    for asset in assets:
        _text(asset, "release intent.assets")
    if len(assets) != len(expected) or set(assets) != expected:
        raise GateError("release intent.assets: expected only the four exact release assets")
    return True


def validate_release_intent(intent, policy) -> bool:
    """Validate explicit release data; structurally valid publish=false grants nothing."""
    return _release_intent(intent, _policy(policy))


def _action_intent(intent, p: dict) -> dict:
    data = _object(intent, {
        "schema", "repository", "action", "head_sha", "intent_sha",
    }, {"release"}, "action intent")
    _equal(data["schema"], "frontier-action-intent/1.0", "action intent.schema")
    _equal(data["repository"], p["repository"], "action intent.repository")
    _text(data["action"], "action intent.action")
    if data["action"] not in p["actions"]:
        raise GateError("action intent.action: undeclared or unsupported action")
    for field in ("head_sha", "intent_sha"):
        _sha(data[field], f"action intent.{field}")
    _equal(data["head_sha"], p["source_sha"], "action intent.head_sha")
    if "release" in data:
        _release_intent(data["release"], p)
    return data


def authorize_action(state, intent, policy) -> bool:
    """Check declared action consistency, never perform it or grant live authority."""
    p = _policy(policy)
    action = _action_intent(intent, p)
    needed = {"eligibility", "intent_sha", "effective_owner_review", "native_review_decision"}
    data = _object(state, STATE_FIELDS | needed, STATE_OPTIONAL - needed, "state")
    _equal(data["pr_state"], "OPEN" if action["action"] == "merge" else "MERGED", "state.pr_state")
    current_base = p["base_sha"]
    if action["action"] == "publish":
        if "merge_commit_sha" not in data:
            raise GateError("state.merge_commit_sha: actual protected merge required")
        _sha(data["merge_commit_sha"], "state.merge_commit_sha")
        current_base = data["merge_commit_sha"]
    _candidate(data, p, current_base_sha=current_base)
    _equal(data["draft"], False, "state.draft")
    _sha(data["intent_sha"], "state.intent_sha")
    _equal(data["intent_sha"], action["intent_sha"], "state.intent_sha")
    review = _review(data["effective_owner_review"])
    _equal(review["reviewer"], p["maintainer"], "state.effective_owner_review.reviewer")
    _equal(review["state"], "APPROVED", "state.effective_owner_review.state")
    _equal(review["commit_id"], data["head_sha"], "state.effective_owner_review.commit_id")
    _equal(review["intent_sha"], data["intent_sha"], "state.effective_owner_review.intent_sha")
    _equal(data["native_review_decision"], "APPROVED", "state.native_review_decision")
    release = action.get("release")
    if release is not None and release["source_mode"] == "merged-pr":
        _equal(release["source"]["pr_number"], data["pr_number"], "release intent.source.pr_number")
    if action["action"] == "merge":
        return True
    if release is None:
        raise GateError("action intent.release: explicit release intent required")
    _equal(release["publish"], True, "release intent.publish")
    if release["source_mode"] == "merged-pr":
        if "tag" in data:
            _tag(data["tag"], release["tag"], data["merge_commit_sha"])
    else:
        if "tag" not in data:
            raise GateError("state.tag: actual existing tag required")
        tag = _tag(data["tag"], release["tag"], release["source"]["commit_sha"])
        _equal(tag["object_sha"], release["source"]["tag_object_sha"], "state.tag.object_sha")
    return True


def _tag(value, name: str, commit_sha: str) -> dict:
    tag = _tag_record(value)
    _equal(tag["name"], name, "state.tag.name")
    _equal(tag["commit_sha"], commit_sha, "state.tag.commit_sha")
    return tag


def _json_pairs(pairs) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise GateError("duplicate JSON field")
        result[key] = value
    return result


def _json_constant(_value):
    raise GateError("non-finite JSON value")


def _json_integer(value: str) -> int:
    if len(value.lstrip("-")) > 100:
        raise GateError("JSON integer exceeds 100 digits")
    return int(value)


def _read(path: Path, label: str):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise GateError(f"{label}: expected UTF-8 JSON") from error
    except OSError as error:
        raise GateError(f"{label}: cannot read JSON file") from error
    try:
        return json.loads(
            text, object_pairs_hook=_json_pairs, parse_constant=_json_constant,
            parse_int=_json_integer,
        )
    except json.JSONDecodeError as error:
        raise GateError(f"{label}: invalid JSON at line {error.lineno}, column {error.colno}") from error
    except RecursionError as error:
        raise GateError(f"{label}: JSON nesting exceeds decoder limit") from error


def main(argv=None) -> int:
    """Read checking inputs only and return nonzero for expected contract failures."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("proposal", "candidate", "action", "release-intent"))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--intent", type=Path, help="Required only for action checks")
    args = parser.parse_args(argv)
    try:
        if args.mode != "action" and args.intent is not None:
            raise GateError("--intent: only valid for action")
        if args.mode == "action" and args.intent is None:
            raise GateError("--intent: required for action")
        data = _read(args.input, "input")
        policy = _read(args.policy, "policy")
        if args.mode == "action":
            authorize_action(data, _read(args.intent, "intent"), policy)
        else:
            function = {
                "proposal": validate_proposal, "candidate": validate_candidate,
                "release-intent": validate_release_intent,
            }[args.mode]
            function(data, policy)
    except GateError as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(f"VALID {args.mode}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    sys.stderr.reconfigure(encoding="utf-8", newline="\n")
    raise SystemExit(main())
