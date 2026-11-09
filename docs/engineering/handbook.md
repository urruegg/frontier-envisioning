# Engineering handbook

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Engineering practice guide; document revision, not product version |
| References | [Documentation](../README.md), [Working agreement](../../AGENTS.md), [Product requirements](../prd.md), [Solution design](../solution-design.md) |

How Frontier Envisioning is built, tested, versioned, released and deployed. The short version for people and agents is [AGENTS.md](../../AGENTS.md).

## 1. Principles

- **Outcome first.** Every change starts from an issue that states the user outcome and testable acceptance criteria.
- **Small batches.** Short-lived branches, small pull requests, frequent merges to `main`.
- **Test first, evidence over claims.** A change is done when the gates say so, not when it looks done.
- **Customer-neutral by construction.** Fictitious Caldova data only; scans and hooks enforce it.
- **People decide, agents assist.** Copilot plans, builds and reviews through pull requests; people approve designs, merge, release and deploy.
- **Reproducible.** The same sources give the same package and demo, byte for byte.

## 2. Branches, commits and pull requests

- Target operating model: `main` is protected by reviewed PRs and `L1 quality gate`, `L2 browser tests`, and `IaC validation`. Local configuration is not proof that these server controls are enabled.
- Branch names: `feat/<issue-id>-<topic>`, `fix/...`, `chore/...`, `docs/...`, `test/...`.
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`, `build:`, `ci:`; the issue id in the body.
- Pull requests use the template: a human-written summary, the linked issue, the gate summary, agent disclosure, screenshots for visual changes. Squash merge.

## 3. Definition of Ready and Done

See AGENTS.md sections 3 and 4. A person sets `status:ready` and, for larger changes, `approved:design` after the spec review.

## 4. Quality gates

| Gate | Trigger | Command | Contents | Blocking |
|---|---|---|---|---|
| L0 | every commit (pre-commit), CI | `python tools/dev.py precommit` | template drift, Python compile, repository rules (versions, skill frontmatter and description limits, licence, JSON and YAML, Copilot files, workflow pins, secrets), ruff, ESLint, customer neutrality | yes |
| L1 | every pull request and push to `main` | `python tools/dev.py ci` | L0, unit and pipeline tests, plugin self-test (34 checks for 1.6.0), package with install check, Caldova demo, release reproduction, DOM tests, scan of built archives, generated files committed | yes (required check) |
| L2 | every pull request after L1; push to `main` | `python tools/dev.py package demo site` + `npx playwright test` | showcase built with the hosting headers; 14 views in Chromium, no CSP violation or script error, screenshots | yes after INT-04 |
| L2 deploy | push to `main` (when enabled) | `azure-dev` workflow | provision and deploy the showcase to dev; smoke check | no (environment) |
| L3 | tag `vX.Y.Z`, explicitly enabled | `release` workflow | tag equals the plugin version, strict L1 and L2 on the tag, bundle, release manifest, pinned SBOM (SPDX), provenance, draft release after `release-approval` | yes |

Copilot Cowork checks that cannot run in GitHub (skill structure and score, routing conflicts, security scan, package validation, behavioural prompts of PRD B.9) run in Cowork before a release; the release pull request records them.

## 5. Versions and releases

- **Semantic versioning of the plugin.** MAJOR: an incompatible change of the blueprint schema, a skill contract or the install format. MINOR: new capability (most releases). PATCH: fixes without new behaviour.
- **Version carriers** (kept in step by `python tools/dev.py bump X.Y.Z`): `plugin/.claude-plugin/plugin.json`, `plugin/package/manifest.json` (Microsoft 365 app manifest: digits only), the `metadata.version` of the seven `SKILL.md`, `PLUGIN_VERSION` in `build_blueprint.py`, the plugin README, the archive date in `tools/build_package.py`, a CHANGELOG section.
- **Immutability (ENG-D4, proposed).** A released version never changes. While the version is released, L1 rebuilds the release manifest's artefacts and fails on any difference; the first change to `plugin/` after a release bumps the version.
- **Release steps.** Verify evidence and the `release-approval` environment/reviewer/tag policy, explicitly enable `RELEASE_ENABLED`, review and merge, tag the approved commit, run strict L1/L2, approve the draft release and record its manifest. These are human operations. Showcase `prod` is a separate boundary.
- **Distribution.** The plugin package from the GitHub release goes to Cowork users: chat install ("Install the Frontier PlugIn") or the organisation catalogue (decision D-02).

## 6. Environments

| Unit | Development | Test | Production |
|---|---|---|---|
| Plugin | the engineer's own Cowork (install from `dist/`) | pilot engineers install a release candidate package | Hub engineers install the published release |
| Showcase | `python tools/dev.py site serve` locally | GitHub environment `dev` (deployed from `main`) | GitHub environment `prod` (manual, approval) |

## 7. Security and compliance

- Secrets: none in the repository; Azure through OpenID Connect; environment secrets for the showcase sign-in. Secret scanning and push protection where the plan allows.
- Dependencies: development only (pip, npm), pinned and updated weekly by Dependabot; plugin scripts use the standard library.
- Code scanning: CodeQL for Python, JavaScript and workflows (needs GitHub Code Security on private repositories).
- Releases: SBOM (Microsoft SBOM tool, SPDX) and build provenance attestations.
- Agents: hooks deny human-only actions and edits to guardrails; see [Copilot and Superpowers](copilot-and-superpowers.md).
- Licences: plugin MIT; Microsoft product icons under Microsoft's icon terms (architecture diagrams and documentation, unmodified); third-party skills keep their notices.

## 8. Documentation and decisions

- Product: [requirements](../prd.md), [release plan](../prd.md#a12-release-plan) and [open decisions D-xx](../prd.md#a13-open-decisions); [solution design](../solution-design.md) and [product ADR-0001 to ADR-0016](../solution-design.md#b12-architecture-decisions).
- Engineering decisions: [docs/adr/](../adr/README.md) from ADR-0017, status *Proposed* until a person accepts.
- New work: [ideas](../idea/README.md), [specs](../spec/README.md), [plans](../plan/README.md) and [sprints](../sprint/README.md). [Legacy plans](../plans/README.md) remain historical. User guide: `plugin/README.md`. Release notes: `CHANGELOG.md`.

## 9. Toolchain

`python tools/dev.py` is the single entry point (standard library; runs on Windows, macOS and Linux). Optional tools are used when present and required in strict mode (CI): pytest, ruff, PyYAML, happy-dom, ESLint, Playwright. See [workstation setup](workstation-setup.md).
