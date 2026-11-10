---
name: frontier-release
description: Prepare and verify a Frontier Envisioning release - version bump, changelog, PRD release table, release bundle, release manifest and the hand-over to the person who tags and publishes. Use when asked to prepare a release, cut version X.Y.Z, write release notes or check that a release reproduces.
---
# Releasing Frontier Envisioning

## Prepare (agent or person, in a pull request)

Read `AGENTS.md` and the linked real issue/idea/spec/plan/sprint, with explicit human plan approval and readiness evidence. New records use plural `docs/ideas/`, `docs/specs/`, `docs/plans/`, `docs/sprints/`; preserve historical `docs/plans/` links. Verify live issue/approval evidence separately from local docs checks. Human decisions do not prove protected label fields changed.

1. `python tools/dev.py bump X.Y.Z --date YYYY-MM-DD` (plugin.json, manifest.json, seven SKILL.md, build_blueprint.PLUGIN_VERSION, plugin README, archive date, CHANGELOG section).
2. Write the CHANGELOG section (user-facing, by area), update `docs/prd.md` (A.9 acceptance criteria and A.12 release plan), `docs/solution-design.md#b9-quality-and-testing` (actual quality results) and the plugin README. Keep released records immutable.
3. `python tools/dev.py check bundle`; quote the summary.
4. Release checklist in the pull request (template): Cowork skill validators and behavioural prompts (solution design B.9) run in Copilot Cowork by a person; install from the package in a Cowork chat. Record actual results only; missing checks remain pending.

Eligible prose may go to `docs-agent`; checker/code stays with `frontier-builder`, HTML with `frontier-renderer` where supported, without tool/model broadening or universal handoff claims. Protected session-start still uses legacy routing until human #8 action; report that dependency. Policy remains Proposed, and files/status do not grant approval or access.

## Publish (people only; hooks block agents)

1. Merge the release pull request.
2. `git tag vX.Y.Z <merge commit>` and `git push origin vX.Y.Z`.
3. A maintainer verifies `release-approval` and its version-tag/reviewer policy before setting `RELEASE_ENABLED=true`. The workflow runs strict L1 and L2 on the tag, builds the bundle, pinned SBOM and provenance attestation, and waits for `release-approval` before drafting the release. Missing baseline evidence or private-repository approval controls blocks publication.
4. Review and publish the draft. Then add `releases/X.Y.Z/manifest.json` from the release asset `release-manifest.json` in a follow-up pull request, so later builds of X.Y.Z can be verified.
5. Distribute: the plugin package goes to Cowork users (chat install or the organisation catalogue, decision D-02).
