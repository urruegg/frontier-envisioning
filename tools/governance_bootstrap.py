# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Generate offline, inert #50 bootstrap proposals, never apply or activate them.

Run with no arguments. The fixed output directory is build/governance-bootstrap/
under fe_lib.ROOT; existing output (even empty) is refused. Review/remove old
output separately before regenerating. No input metadata, approval flags,
credentials, subprocesses, network, candidate execution or mutation mode.

Only explicitly listed current source files are read. Links, Windows reparse
points, case aliases and overwrites are rejected. This is an offline generator,
not a credential-isolated sandbox against concurrent privileged filesystem
changes. An interrupted I/O operation may leave incomplete review output; it
returns nonzero, never readiness. Expected input/I/O errors return 1, usage 2;
unexpected errors propagate. Successful generation always leaves adoption and
publication BLOCKED.
"""
from __future__ import annotations

import argparse
import difflib
import json
import stat
import sys
from pathlib import Path

from fe_lib import ROOT, sha256_bytes

SOURCES = (
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
LEGACY_ROUTING = "write the spec and plan to docs/plans/"
SUMMARY = "## Summary (written by a person, in your own words)"
SUMMARY_COMMENT = "<!-- What changes for the users of the plugin or for the engineers, and why. -->"
HUMAN_VERIFICATION = (
    "<!-- Human verification required: @urruegg verifies this summary against the reviewed head; "
    "machine text is not physically human-written. -->"
)
BLOCKERS = {
    "routing": "#8 requires a person to review/adopt the actual session_start.py routing proposal; active routing is legacy.",
    "integration": (
        "#49 pr_gate APIs are pure consistency checks, not authentication or permission. "
        "Trusted collectors, workflow parser, coordinator, current source/base/control/run/check-origin "
        "binding, effective native owner review/latest intent collection and isolated publisher are not implemented/adopted here."
    ),
    "provisioning": (
        "Last maintainer-reported inventory: no verified governance App/client/key/private store/restricted worker, "
        "repository variables/secrets or main protections. Offline source inspection cannot verify current live settings."
    ),
    "provider_capability": (
        "Owner must prove supported restricted machine/human credential split and native PR/check enforcement. "
        "GitHub Pro on private repositories lacks private environment reviewers/native artifact attestations; "
        "unsupported capability BLOCKS activation, with no crypto/SLSA promise."
    ),
    "isolation": (
        "This shared owner-authenticated environment is not a dedicated credential-isolated sandbox "
        "and this worker is not a machine GitHub App. Never fall back to owner-scoped agent authentication."
    ),
    "human_adoption": (
        "Actual App/private-store creation, key storage, provider configuration, protections and active protected edits "
        "are person-only. An Accepted file, caller metadata or synthetic approval cannot prove adoption/authority; "
        "@urruegg must record the actual adoption revision and capability proof."
    ),
}
ALIGNMENT = """

## #50 bootstrap proposal — NOT adopted

This review-only proposal does not grant authority. @urruegg remains the sole
accountable human owner. Keep every current human-only restriction and deny
rule until supported external trusted enforcement is implemented, verified and
explicitly adopted by the owner. Design/readiness approval, an Accepted file,
caller metadata, synthetic booleans and pure pr_gate checks are not operational
permission. Never fall back to shared owner-scoped agent authentication.

Linked issue/idea/spec/plan/sprint evidence governs bounded test-first work.
AGENTS is the entry point; PRD A.12/A.13 governs releases/decisions, solution
design B.9 verification and ADRs engineering rationale. Policy, hooks/harness
routing, project skills/agents and workflow authority must agree at the actual
adoption revision; handoffs add no tools/models or approval. Human #8 adoption
must repair the actual session_start.py legacy spec/plan route, not docs alone.

Integration gaps: trusted collectors/parser/coordinator must bind actual current
source/base/control, workflow/run/check origins, effective native owner review
and latest immutable intent. A restricted worker writes only a dedicated private
proposal-input repository, without base contents/review/publishing writes or
owner keys. Trusted coordination applies inert data using accepted control code;
the validator has no secrets/write/OIDC. The metadata reporter never executes
candidate code or passes installation tokens to workers/cross-job outputs.
Publishing remains isolated and blocked until actual human approval/adoption.
No privileged candidate checkout or edited candidate policy is trusted authority.

Preserve customer neutrality, generators, licences, immutable records and
credential boundaries. Do not activate release/deployment paths: both
SHOWCASE_ENABLED and legacy RELEASE_ENABLED stay unset/false. No Azure/admin/
destructive/visibility/secret-rotation authority is added. Native Releases ZIP
only, no registry wrapper. Existing history is not reclassified or retagged.
"""
WORKFLOW_NOTE = (
    "# #50 review-only authority proposal; no executable workflow change or activation.\n"
    "# Keep current restrictions/flags; accepted trusted collectors/coordinator and native human review are missing.\n"
    "# Candidate policy/code is not trusted control; validator must have no secrets/write/OIDC.\n"
    "# Reporter is metadata-only; publishing is isolated after real approval, never owner-scoped agent authentication.\n"
)
REPORTER_EXAMPLE = """# Proposed TRUSTED metadata-only reporter step, not a complete workflow.
# Never run candidate/generated code here or return a token to a worker/cross-job output.
- uses: actions/create-github-app-token@64ab729a6294000f5aa4a4bc0b73d1f32bc45510 # v3
  id: app-token
  with:
    client-id: ${{ vars.GOVERNANCE_APP_CLIENT_ID }}
    private-key: ${{ secrets.GOVERNANCE_APP_PRIVATE_KEY }}
    repositories: frontier-envisioning
    permission-checks: write
    permission-actions: read
    permission-contents: read
    permission-pull-requests: read
"""
# Exact current source segments, not suffix notes that leave conflicting steps operative.
# Drift/duplicates are input failures; these replacements exist only in the inert patch.
AMENDMENTS = {
    ".github/skills/frontier-release/SKILL.md": ((
        "## Publish (people only; hooks block agents)\n\n"
        "1. Merge the release pull request.\n"
        "2. `git tag vX.Y.Z <merge commit>` and `git push origin vX.Y.Z`.\n"
        "3. A maintainer verifies `release-approval` and its version-tag/reviewer policy before setting `RELEASE_ENABLED=true`. "
        "The workflow runs strict L1 and L2 on the tag, builds the bundle, pinned SBOM and provenance attestation, "
        "and waits for `release-approval` before drafting the release. "
        "Missing baseline evidence or private-repository approval controls blocks publication.\n"
        "4. Review and publish the draft. Then add `releases/X.Y.Z/manifest.json` from the release asset `release-manifest.json` "
        "in a follow-up pull request, so later builds of X.Y.Z can be verified.\n"
        "5. Distribute: the plugin package goes to Cowork users (chat install or the organisation catalogue, decision D-02).\n",
        "## Publish (people only; hooks block agents)\n\n"
        "The legacy activation sequence is retired in this proposed private-Pro engineering profile. "
        "This is review data, not current activation or permission; active protected sources/history stay unchanged.\n\n"
        "1. Keep SHOWCASE_ENABLED and legacy RELEASE_ENABLED unset/false; do not enable or rerun legacy release.yml.\n"
        "2. GitHub Pro private environment reviewers (`release-approval`) and native artifact attestations are unsupported. "
        "Publication is BLOCKED rather than falling back to that legacy path or promising crypto/SLSA evidence.\n"
        "3. STOP for @urruegg: actual App/store/key/provider/native protection setup, eligible current-head human review, "
        "accepted control/adoption revision and supported capability proof are person-only prerequisites. Missing proof blocks activation.\n"
        "4. A future separately implemented/adopted isolated trusted publisher may process a declared release intent only after "
        "actual human approval and verified accepted controls. Only four native Releases assets: frontier-envisioning-plugin-VERSION.zip, "
        "release-manifest.json, sbom-spdx.zip, SHA256SUMS.txt; no registry wrapper. Workers receive no publishing credentials.\n"
        "5. Only after separately authorised publication, hand the immutable release-manifest record to the person for a follow-up PR "
        "and distribute the plugin to Cowork users (decision D-02). Preserve #47/manual history; no retag, old publisher rerun or relabelling.\n",
    ),),
    ".github/agents/frontier-release-manager.agent.md": ((
        "5. Hand over to the release manager with the exact next steps: verify baseline evidence and the `release-approval` reviewer/tag policy, "
        "enable `RELEASE_ENABLED`, merge, tag the approved commit, push the tag, approve `release-approval`, publish the draft, "
        "then record the release manifest in a follow-up pull request. Never enable, merge, tag, publish or deploy yourself.\n",
        "5. Hand over a BLOCKED release-intent review package to @urruegg. Keep SHOWCASE_ENABLED and RELEASE_ENABLED unset/false; "
        "do not enable or rerun legacy release.yml. GitHub Pro private environment reviewers/native artifact attestations are unsupported. "
        "Actual App/store/key/provider/native protection and accepted control/adoption proof are person-only prerequisites; "
        "missing capability stops activation, with no owner-scoped authentication fallback. Only a future separately implemented/adopted "
        "isolated trusted publisher may process a declared release intent after actual human approval. "
        "Never enable, merge, tag, publish, dispatch or deploy yourself.\n",
    ),),
    ".github/instructions/python-tools.instructions.md": ((
        "- The hook scripts in `.github/hooks/scripts/` are human-maintained guardrails; "
        "propose changes in the pull request description instead of editing them.\n",
        "- The hook scripts in `.github/hooks/scripts/` are human-maintained guardrails (people only); "
        "propose changes in the pull request description instead of editing them.\n"
        "- The offline bootstrap generator produces only source-qualified inert review proposals under ignored "
        "`build/governance-bootstrap/`, through the tool rather than manual output edits. "
        "Missing/drifted/duplicate source anchors fail clearly before output; no credential access, no candidate execution, "
        "no GitHub/Azure calls or apply mode. Generated output is not adoption or permission; current protected bytes/denials stay unchanged.\n",
    ),),
    ".github/instructions/workflows.instructions.md": ((
        "- Top-level `permissions` with the least privilege; widen per job only where needed "
        "(`id-token: write` for OpenID Connect, `contents: write` only for publishing a release).\n",
        "- Top-level `permissions` stay least-privilege/read-only. Current write/manual actions and protected changes remain human-only; "
        "SHOWCASE_ENABLED and RELEASE_ENABLED stay unset/false. This proposal neither enables a workflow nor grants current agents permission.\n"
        "- A future accepted trusted proposal coordinator may have `contents: write` for dedicated feature-branch writes only, "
        "with explicit per-repository/per-job permissions in urruegg/frontier-envisioning. "
        "Accepted control and actual native protections must enforce protected main/current source/base/control, eligible human review "
        "and no routine bypass; no proposal worker receives base contents/review/publishing writes or owner keys. "
        "Do not execute a candidate or trust edited candidate policy in a privileged job.\n"
        "- Candidate validator: no secrets/write/OIDC. The trusted metadata-only reporter binds actual source/control/run/check origins; "
        "never print/return an installation token to a worker or pass it as a cross-job output. "
        "A future isolated publisher is separate from validation/coordination and requires actual human approval of a declared release intent.\n"
        "- These future roles require implemented trusted enforcement and real person-only App/store/key/provider/native/adoption proof. "
        "If capability/isolation is missing, activation remains BLOCKED; no owner-scoped agent authentication fallback. "
        "GitHub Pro private environment reviewers/native artifact attestations are unsupported, not an alternate release gate.\n"
        "- `id-token: write` is only for separately approved Azure OpenID Connect workflows, not this engineering validator/profile. "
        "No Azure/admin/destructive/visibility/secret-rotation authority is added.\n",
    ),),
    ".github/copilot-instructions.md": (
        (
            "8. **Human-only:** merging, approvals, releases and tags, deployments, repository settings, "
            "the `status:ready` and `approved:*` labels, and `.github/hooks/`. Hooks enforce this.\n",
            "8. **Current human-only:** merging, approvals, releases and tags, deployments, repository settings, "
            "the `status:ready` and `approved:*` labels, and `.github/hooks/`. Keep active hooks/denials unchanged. "
            "Possible future accepted trusted roles are not permission for current agents or this shared owner-authenticated environment. "
            "Only separately implemented/adopted accepted control, real native human review and person-verified capability proof can govern "
            "a restricted proposal coordinator or isolated publisher; no tools/models or guard-opening path is added here. "
            "Never expose candidate execution to write/publishing credentials or pass owner keys to a worker; "
            "the validator has no secrets/write/OIDC and missing isolation blocks activation.\n",
        ),
        (
            "- Protected session-start routing still names legacy paths; a human must update it under #8. "
            "Report that limitation, do not edit or hide it.\n",
            "- Protected session-start routing remains legacy until a person completes #8. "
            "The inert source-qualified migration contains the actual route repair, not adoption evidence or authority to edit active hooks. "
            "Report the current limitation; do not hide it or infer activation from a file/status.\n",
        ),
    ),
}
CHECKLIST = """# #50 operator checklist — review output only

STOP: @urruegg alone performs App/private-store creation, key storage, provider
configuration, protections and active protected edits. No keys/tokens requested
in chat. This package neither applies settings nor authorises activation,
merge, tag, publication, workflow dispatch or deployment.

- [ ] Review the source hashes/diff against the actual current-head. Preserve
  Customer neutrality, generators, licences, immutable records and human-only
  denials. Policy may say Accepted without proving adoption.
- [ ] Review the PR template's sole Summary/human-verification amendment;
  preserve all other headings/comments/checklists/order and truthful release
  acceptance fields. Until adopted, do not call machine text human-written.
- [ ] Complete human #8: adopt the actual session_start.py spec/plan routing
  repair and align AGENTS/policy/hooks/harness/project skills/agents and workflow
  authority. Keep current deny behavior; no turnkey guard-opening executable.
- [ ] Record actual public App metadata (IDs/login/client ID/installation ID)
  only after live verification; null here means missing, not a production
  identity. Provision the dedicated private proposal-input store and supported
  restricted worker. Configure keys privately, never in chat/worker outputs.
- [ ] Prove the worker lacks base contents/review/publishing writes and owner
  keys. This shared owner-authenticated environment is not isolation; no
  owner-scoped authentication fallback. No Azure/admin/destructive/visibility/secret-rotation scope.
- [ ] Verify actual main PR requirements: one eligible human-owner CODEOWNERS
  @urruegg approval; stale dismissal/current-head/latest-push freshness;
  conversations resolved; no routine bypass. A same-person second account or
  PR-author self-approval is not eligible independent/native approval.
- [ ] Bind required L1 quality gate/L2 browser tests/IaC validation/trusted
  App-origin Governance eligibility to actual current source/base/control/check
  origins. Source CI names alone do not prove native protection or check origin.
- [ ] Implement/review trusted collectors, workflow parser and coordinator
  using accepted control code. Apply inert proposal data only; validator:
  no secrets/write/OIDC. No privileged candidate checkout or candidate policy
  as authority. Pure pr_gate consistency PASS is not live authentication.
- [ ] Prove reporter pins actual source/control/run facts, uses explicit
  per-repository/per-job installation permissions and never prints/returns a
  token to a worker or as a cross-job output. Review the pinned v3 example.
- [ ] Keep publishing isolated after actual human approval; verify effective
  native review, latest intent, source/base freshness and accepted controls.
  File status/caller approval booleans are never an authorisation pathway.
- [ ] Keep SHOWCASE_ENABLED and legacy RELEASE_ENABLED unset/false. These
  desired settings are not verified current settings. GitHub Pro private
  environment reviewers/native artifact attestations are unsupported; no
  crypto/SLSA guarantee. Missing provisioning/capability BLOCKS next stage.
- [ ] Owner records actual adoption revision and capability proof before any
  activation. Do not restart automatically when a descriptor looks complete.
- [ ] Preserve v1.10.0 annotated tag object
  5f9d21953db9c968ae56ac6d485baff3fc09b0ce -> product source
  2d5a7ccfe684b052197697e3e65d265ca2fd6cb9 and unchanged native plugin SHA256
  9e7985731040ee05d83c8dbcee92ad20bc09c584b70b4e994f7fde71dfaf4b89.
  Keep #47 manual-preparation history aa838fbb6df96766a632d6f6ec3151ca93c7803d:
  no automatic-context relabelling, no old publisher rerun, no retag.
- [ ] Future release has four assets only: frontier-envisioning-plugin-VERSION.zip,
  release-manifest.json, sbom-spdx.zip, SHA256SUMS.txt. Native Releases ZIP,
  no registry packaging. This checklist does not publish them.
"""


class BootstrapError(ValueError):
    """Expected unsafe or unsupported input, never readiness."""


class UsageError(BootstrapError):
    """Unsupported CLI arguments; do not echo possible credential values."""


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise UsageError("unsupported arguments; this offline generator accepts only --help or no arguments")


def _safe(path: Path, *, directory: bool) -> tuple[int, int]:
    """Inspect every component without following links/reparse points."""
    for component in (*reversed(path.parents), path):
        info = component.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise BootstrapError(f"source/output link or reparse point refused: {component.name}")
        expected_directory = component != path or directory
        if expected_directory and not stat.S_ISDIR(info.st_mode):
            raise BootstrapError(f"source/output directory required: {component.name}")
        if not expected_directory and not stat.S_ISREG(info.st_mode):
            raise BootstrapError(f"source/output regular file required: {component.name}")
        if not expected_directory and info.st_nlink != 1:
            raise BootstrapError(f"multiply-linked source file refused: {component.name}")
    return info.st_dev, info.st_ino


def _entry(parent: Path, name: str) -> Path | None:
    """Reject case aliases on case-sensitive hosts as well as Windows."""
    matches = sorted(path for path in parent.iterdir() if path.name.casefold() == name.casefold())
    if any(path.name != name for path in matches) or len(matches) > 1:
        raise BootstrapError(f"source/output case alias refused: {name}")
    return matches[0] if matches else None


def _read_sources() -> tuple[dict[str, str], dict[str, str]]:
    if not ROOT.is_absolute() or ROOT != ROOT.resolve():
        raise BootstrapError("source ROOT must be canonical, not an alias or link")
    _safe(ROOT, directory=True)
    # Preflight ALL source components before reading anything (including credential links).
    for relative in SOURCES:
        _safe(ROOT / relative, directory=False)
    text, hashes = {}, {}
    for relative in SOURCES:
        _safe(ROOT / relative, directory=False)
        data = (ROOT / relative).read_bytes()
        try:
            decoded = data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise BootstrapError(f"source is not UTF-8: {relative}") from error
        text[relative] = decoded.replace("\r\n", "\n")
        if not text[relative].endswith("\n") or "\x00" in decoded or "\r" in text[relative]:
            raise BootstrapError(f"unsupported source text shape: {relative}")
        hashes[relative] = sha256_bytes(data)
    ignore = text[".gitignore"].splitlines()
    if "/build/" not in ignore or any(line.strip().startswith("!") for line in ignore):
        raise BootstrapError("build output must be unambiguously ignored by .gitignore")
    return text, hashes


def _replace_once(source: str, old: str, new: str, relative: str) -> str:
    if source.count(old) != 1:
        raise BootstrapError(f"unsupported source shape: {relative}")
    return source.replace(old, new, 1)


def _migration(sources: dict[str, str]) -> str:
    proposed = {}
    template = ".github/pull_request_template.md"
    if not sources[template].startswith(SUMMARY + "\n"):
        raise BootstrapError(f"unsupported source heading: {template}")
    proposed[template] = _replace_once(sources[template], SUMMARY, "## Summary", template)
    proposed[template] = _replace_once(
        proposed[template], SUMMARY_COMMENT, SUMMARY_COMMENT + "\n" + HUMAN_VERIFICATION, template,
    )
    hook = ".github/hooks/scripts/session_start.py"
    proposed[hook] = _replace_once(
        sources[hook], LEGACY_ROUTING, "write the spec to docs/specs/ and plan to docs/plans/", hook,
    )
    guard = ".github/hooks/scripts/guard.py"
    proposed[guard] = _replace_once(
        sources[guard], "from __future__ import annotations\n",
        "# #50 proposal only: retain every current deny rule; trusted enforcement/adoption is missing.\n"
        "from __future__ import annotations\n", guard,
    )
    for relative in SOURCES:
        if (
            relative == "AGENTS.md"
            or relative.startswith((".github/agent-policy/", ".github/agents/", ".github/skills/"))
        ):
            proposed[relative] = sources[relative] + ALIGNMENT
        elif relative.startswith(".github/workflows/"):
            proposed[relative] = WORKFLOW_NOTE + sources[relative]
    for relative, replacements in AMENDMENTS.items():
        revised = proposed.get(relative, sources[relative])
        for old, new in replacements:
            revised = _replace_once(revised, old, new, relative)
        proposed[relative] = revised
    return "".join(
        "".join(difflib.unified_diff(
            sources[relative].splitlines(keepends=True), proposed[relative].splitlines(keepends=True),
            fromfile="a/" + relative, tofile="b/" + relative, lineterm="\n",
        ))
        for relative in sorted(proposed)
    )


def _json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _hook_observations(source: str) -> dict:
    """Inspect registration data only; do not run hooks or infer enforcement."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise BootstrapError("duplicate source JSON field in guardrails.json")
            result[key] = value
        return result

    def nonfinite(_value):
        raise BootstrapError("non-finite source JSON constant in guardrails.json")

    try:
        value = json.loads(source, object_pairs_hook=unique, parse_constant=nonfinite)
    except BootstrapError:
        raise
    except (ValueError, RecursionError) as error:
        raise BootstrapError("invalid source JSON in guardrails.json") from error
    if not isinstance(value, dict) or not isinstance(value.get("hooks"), dict):
        raise BootstrapError("unsupported source hooks shape in guardrails.json")
    hooks = value["hooks"]

    def registered(event, script):
        entries = hooks.get(event, [])
        if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
            raise BootstrapError("unsupported source hook entries in guardrails.json")
        return any(
            entry.get("type") == "command" and entry.get("cwd") == "."
            and entry.get("bash") == f"python3 .github/hooks/scripts/{script}"
            and entry.get("powershell") == f"python .github/hooks/scripts/{script}"
            for entry in entries
        )

    return {
        "session_start_registered": registered("sessionStart", "session_start.py"),
        "guard_registered": registered("preToolUse", "guard.py"),
        "live_enforcement_verified": False,
    }


def _documents(sources: dict[str, str], hashes: dict[str, str]) -> dict[str, str]:
    hooks = _hook_observations(sources[".github/hooks/guardrails.json"])
    blockers = dict(BLOCKERS)
    blockers["source_configuration"] = (
        "Source registration is not live enforcement; inspect all hashes at adoption. "
        "Missing/changed hooks, privileged existing workflows and absent trusted workflow adaptation are integration gaps."
    )
    if not hooks["session_start_registered"] or not hooks["guard_registered"]:
        blockers["source_configuration"] += " Expected source hook registration is missing/changed."
    settings = {
        "schema": "frontier-bootstrap-settings/1.0",
        "status": "Proposed; not applied", "verified_current": None,
        "repository": "urruegg/frontier-envisioning", "visibility": "private",
        "desired": {
            "flags": {"SHOWCASE_ENABLED": False, "RELEASE_ENABLED": False},
            "main": {
                "require_pull_request": True, "required_eligible_human_approvals": 1,
                "codeowner": "@urruegg", "dismiss_stale_reviews": True,
                "require_latest_push_approval": True, "resolve_conversations": True,
                "routine_bypass": [],
                "required_checks": [
                    "L1 quality gate", "L2 browser tests", "IaC validation", "Governance eligibility",
                ],
                "origins": "Owner verifies trusted App-origin eligibility and current source/base/control/run/check origins.",
            },
            "private_environment_reviewers_supported": False,
            "native_artifact_attestations_supported": False,
        },
    }
    jobs = {
        "reporter": {"checks": "write", "actions": "read", "contents": "read", "pull_requests": "read"},
        "coordinator": {"contents": "write", "pull_requests": "write"},
        "publisher": {"contents": "write", "actions": "read"},
    }
    app = {
        "schema": "frontier-bootstrap-app/1.0", "status": "Incomplete proposed descriptor; not provisioned",
        "actual_public_metadata": None, "independently_verified": False,
        "metadata_boundary": "Caller-provided public metadata would not be independently verified live evidence.",
        "proposed_manifest": {
            "name": None, "url": None, "public": False, "hook_attributes": {"url": None},
            "default_permissions": {
                "checks": "write", "actions": "read", "contents": "write", "pull_requests": "write",
            },
            "default_events": ["pull_request", "pull_request_review", "check_run", "workflow_run"],
        },
        "provisioning": "STOP: actual App/private-store creation and private key storage are person-only; no keys requested in chat.",
        "installation_token_jobs": {
            name: {
                "repositories": ["frontier-envisioning"], "permissions": permissions,
                "all_installation_defaults": False,
            } for name, permissions in jobs.items()
        },
        "job_boundary": (
            "These are future trusted roles, not current delegated rights. Coordinator/publisher write grants "
            "are restricted to accepted control after real adoption/approval. Proposal worker uses a separate "
            "private proposal-input store identity and has no base write/review/publishing rights or owner keys; "
            "validator has no secrets/write/OIDC or installation token."
        ),
        "token_boundary": (
            "Trusted metadata-only reporter never executes candidate/generated code, prints/returns a token "
            "to a worker or passes it as a cross-job output. Every token is per-repository/per-job, never all-installation."
        ),
        "trusted_metadata_reporter_example": REPORTER_EXAMPLE,
    }
    owner_lines = [
        line.split() for line in sources[".github/CODEOWNERS"].splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    report = {
        "schema": "frontier-bootstrap-validation/1.0",
        "generation": "inert review output only", "adoption_ready": False,
        "publication_authorized": False, "next_stage": "BLOCKED", "live_verified": False,
        "source_sha256": hashes,
        "observed": {
            "legacy_session_start": LEGACY_ROUTING,
            "codeowner": "@urruegg" if ["*", "@urruegg"] in owner_lines else None,
            "hooks": hooks,
            "workflow_authority": "Source hashes only; trusted workflow parsing/adaptation and live native/check-origin verification are absent.",
        },
        "maintainer_reported_inventory": {
            "source": "#50 approved execution brief; last reported, not independently verified offline",
            "repository": "urruegg/frontier-envisioning", "visibility": "private", "plan": "GitHub Pro",
            "repository_variables": [], "repository_secrets": [], "main_protections": None,
            "governance_app": None, "private_store": None, "restricted_worker": None,
            "SHOWCASE_ENABLED": None, "RELEASE_ENABLED": None,
        },
        "evidence_boundary": "Hashes prove read source bytes only, not live facts, accepted controls, native approvals or capability.",
        "blockers": blockers,
    }
    # Report is written last: a prior I/O failure cannot leave a success-shaped report.
    return {
        "migration-proposal.patch": _migration(sources),
        "settings-proposal.json": _json(settings),
        "app-descriptor.json": _json(app),
        "operator-checklist.md": CHECKLIST,
        "validation-report.json": _json(report),
    }


def generate() -> tuple[Path, ...]:
    """Generate at the sole fixed location, with exclusive creation only."""
    sources, hashes = _read_sources()
    documents = _documents(sources, hashes)
    root_identity = _safe(ROOT, directory=True)
    build = _entry(ROOT, "build")
    if build is None:
        build = ROOT / "build"
        build.mkdir()
    build_identity = _safe(build, directory=True)
    if _entry(build, "governance-bootstrap") is not None:
        raise BootstrapError("output already exists; refusing overwrite (including empty directories)")
    output = build / "governance-bootstrap"
    if _safe(ROOT, directory=True) != root_identity or _safe(build, directory=True) != build_identity:
        raise BootstrapError("output parent identity changed")
    output.mkdir()
    output_identity = _safe(output, directory=True)
    written = []
    for name, content in documents.items():
        for directory, identity in ((ROOT, root_identity), (build, build_identity), (output, output_identity)):
            if _safe(directory, directory=True) != identity:
                raise BootstrapError("output directory identity changed")
        if _entry(output, name) is not None:
            raise BootstrapError("output file already exists; refusing overwrite")
        path = output / name
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        written.append(path)
    return tuple(written)


def main(argv=None) -> int:
    parser = Parser(description=__doc__, formatter_class=lambda prog: argparse.HelpFormatter(prog, width=80))
    try:
        parser.parse_args(argv)
    except UsageError as error:
        print(f"bootstrap: {error}", file=sys.stderr)
        return 2
    except SystemExit as error:
        return int(error.code)
    try:
        paths = generate()
    except (BootstrapError, OSError) as error:
        print(f"bootstrap: {error}", file=sys.stderr)
        return 1
    print(f"Generated {len(paths)} files in build/governance-bootstrap/: review output only; adoption BLOCKED, publication not authorised.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
