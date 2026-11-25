---
name: frontier-release
description: Prepare and verify a Frontier Envisioning release - version bump, changelog, PRD release table, release bundle and evidence, then hand over to the person who runs the release workflow. Use when asked to prepare a release, cut version X.Y.Z, write release notes or check that a release reproduces.
---
# Releasing Frontier Envisioning

## Prepare (agent or person, in a pull request)

Read `AGENTS.md` and the linked real issue/idea/spec/plan/sprint, with explicit human plan approval and readiness evidence. New records use plural `docs/ideas/`, `docs/specs/`, `docs/plans/`, `docs/sprints/`; preserve historical `docs/plans/` links. Verify live issue/approval evidence separately from local docs checks. Human decisions do not prove protected label fields changed.

1. `python tools/dev.py bump X.Y.Z --date YYYY-MM-DD` (plugin.json, manifest.json, seven SKILL.md, build_blueprint.PLUGIN_VERSION, plugin README, archive date, CHANGELOG section).
2. Write the CHANGELOG section (user-facing, by area), update `docs/prd.md` (A.9 acceptance criteria and A.12 release plan), `docs/solution-design.md#b9-quality-and-testing` (actual quality results) and the plugin README. Keep released records immutable.
3. `python tools/dev.py check bundle`; quote the actual summary. Local checks are offline: without validated exact-version cached evidence, published-release verification is `not-performed`, not a release reproduction pass. CI performs fresh authoritative lookup; local `--strict` only requires installed tools. See the [verification modes](../../../docs/engineering/testing-strategy.md#release-evidence-modes).
4. Release checklist in the pull request (template): Cowork skill validators and behavioural prompts (solution design B.9) run in Copilot Cowork by a person; install from the package in a Cowork chat. Record actual results only; missing checks remain pending.

Eligible prose may go to `docs-agent`; checker/code stays with `frontier-builder`, HTML with `frontier-renderer` where supported, without tool/model broadening or universal handoff claims. Protected session-start still uses legacy routing until human #8 action; report that dependency. Policy remains Proposed, and files/status do not grant approval or access.

## Publish (people only; hooks block agents)

The owner-dispatched workflow adopted under #55/#57 replaces the legacy
tag-first publisher. The [one-time evidence-access handover](../../../docs/engineering/release-evidence-adoption.md)
is still pending human application; it is not a new per-release ceremony.
Keep legacy `RELEASE_ENABLED` and `SHOWCASE_ENABLED` unset/false. Do not
reactivate `release-approval`, native attestation or manual draft publication,
or activate #48's App model.

1. The maintainer reviews the exact release head, passing required checks and actual Cowork/manual evidence, then merges the release pull request. Missing evidence remains pending.
2. After the one-time handover is applied, `urruegg` chooses **Actions > release > Run workflow** on `main`, enters the matching `version` (`X.Y.Z`) and confirms `manual_checks` and `publish`. These are maintainer reports, not independent approval.
3. Automation runs strict L1/L2, independently compares plugin builds and verifies the source-bound manifest, SBOM, checksums and publisher handover. The separate publisher creates/verifies the annotated tag and publishes the normal release. Failures stop publication; do not move tags or overwrite assets to recover.
4. Exact-version release assets are canonical evidence for subsequent automatic checks, never `latest`. No routine manual download, hash comparison, manifest copy under `releases/` or retention pull request is required. Historical tags, assets, records and explicit manifests remain usable and unchanged; #52 supersession awaits verified replacement and human adoption.
5. Distribute the published plugin ZIP to authorised Cowork users (chat install or the organisation catalogue, decision D-02). The four downloads are plugin ZIP, `release-manifest.json`, `sbom-spdx.zip` and `SHA256SUMS.txt`; the checksum file has three payload rows. Demo/identity/catalogue reproduction outputs are not additional downloads. Checksums/cache consistency are not signatures or independent approval.

Agents never dispatch, merge, tag, publish, change settings or apply the
protected workflow handover. Repository metadata reporting `private:false`
conflicts with the intended private/internal policy; the maintainer must
[reconcile it](../../../docs/engineering/release-evidence-adoption.md#classification-and-access)
without inferring external sharing clearance.
