# Frontier Envisioning

| Field | Value |
|---|---|
| Version | 0.4 |
| Date | 2026-11-11 |
| Author | Urs Rüegg; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Repository overview and developer entry points; document revision, not product version |
| References | [Documentation](docs/README.md), [Product requirements](docs/prd.md), [Solution design](docs/solution-design.md), [Contributing](CONTRIBUTING.md) |

**Innovation Hub Frontier solution envisioning and architecture design, as a Copilot Cowork plugin.**

Frontier Envisioning helps Microsoft Innovation Hub solution engineers prepare and run Frontier envisioning and architecture design workshops. It gathers the customer context from Work IQ and workshop transcripts, builds the interactive **Frontier Company Blueprint** along the Hub journey (Vision, Design, Build, Workshops in the development intake), writes the PRD, solution design, ADRs and IT readiness checklist, creates the agent identity kit and models the business value and what the agents cost.

The identity kit supplies branding, not Entra identity provisioning. HubWorks is controlled source integration, not an assumed runtime loader; documents or harness selection do not prove deployed capability.

| | |
|---|---|
| Current product baseline | **1.6.0** (8 November 2026), imported from Copilot Cowork; 1.4.0 records retained |
| Received handover | **1.9.0**: [source/manifest receipt](docs/intake/handover-1.9.0.md); incoming release/publication claims are not independently verified; [1.7 receipt](docs/intake/handover-1.7.0.md) retained |
| Integrated development version | **1.9.1 — UNRELEASED**: selective process/ontology intake, seven GA product wrappers and optional acknowledged Preview FinOps; final integrated acceptance pending |
| Repository home | [urruegg/frontier-envisioning](https://github.com/urruegg/frontier-envisioning), private; use approved work material only |
| Sole maintainer | [@urruegg](https://github.com/urruegg), the public-cloud account; no second collaborator is implied |
| Plugin licence | MIT (Microsoft product icons: see [THIRD-PARTY-NOTICES.md](plugin/THIRD-PARTY-NOTICES.md)) |
| Demo data | the fictitious Caldova Industrial AG only |
| Status | [#25](https://github.com/urruegg/frontier-envisioning/issues/25): design and written plan approved; D1–D3 returned SPEC PASS / QUALITY CLEAR; D4 prose and D5 final validation/handoff tracked in [SPRINT-004](docs/sprints/SPRINT-004-handover-1.9-preview-finops.md). [M0 intake](docs/engineering/intake-plan.md) remains historical evidence |

## Use the plugin

1. Obtain an approved `frontier-envisioning-plugin-<version>.zip` (keep it zipped). The current 1.9.1 intake is not a published release.
2. Attach it in a new Copilot Cowork chat and type **Install the Frontier PlugIn**.
3. Approve each step. The user guide is [plugin/README.md](plugin/README.md).

The package registers **eight skills**: seven non-FinOps GA product wrappers
(including optional `frontier-process` when requested) and bundled optional
Preview `frontier-finops`. Core engagement/value/identity/blueprint/design/
process work does not require FinOps. GA is the maintainer's designation, not
result confidence, provider GA, release/deployment or public/IP clearance.
Fabric ontology/agent/operations Preview, unchecked mappings and dated canon
remain explicit; MOS3 manifest `devPreview` is unchanged.

FinOps may load to explain limitations, but before any cost operation,
recommendation or figure it must show:

> Frontier FinOps is Preview. Its grounding and cost model are not GA and need refinement. Results are provisional planning estimates, not validated pricing, budget approval or purchase/commitment advice. Verify rates and assumptions independently before decisions.

Obtain actual current-scenario confirmation first; installation, old JSON or
earlier runs are not consent. Each top-level CLI needs
`--acknowledge-finops-preview`; wrapper forwarding covers one action chain only.
Renew for a new invocation/scope/model/rates/grounding. Browser acknowledgement
is separate, document-local and reset on reload, not localStorage or access
control. Decline/absent unrequested FinOps continues core with honest budget
gaps; requested missing FinOps errors. Preserve legacy Preview originals and
use clean ordinary core inputs on decline, not cached Preview value; no automatic
cleansing is promised. See the [FinOps procedure](plugin/skills/frontier-finops/SKILL.md).

## Develop

Use an isolated Python environment; see [workstation setup](docs/engineering/workstation-setup.md). The local intake uses Python 3.11 and Node 24 within the supported ranges; CI and the dev container retain Python 3.12 and Node 22. Playwright downloads stay in `build/playwright-browsers` unless `PLAYWRIGHT_BROWSERS_PATH` is explicitly set.

Open the repository in the dev container (VS Code or Codespaces), or install Python 3.11+, Node.js 22+ and Git, then:

```bash
python tools/dev.py setup      # pytest, ruff, PyYAML, happy-dom, ESLint, Playwright Chromium
python tools/dev.py doctor     # what is installed
python tools/dev.py docs --strict  # local metadata, links and work-package contracts
python tools/dev.py check      # gate L1: everything CI runs (a few minutes)
```

Default `python tools/dev.py demo` uses core value/identity plus the curated
process example, without FinOps. The explicit developer Preview profile is
isolated and needs technical acknowledgement:

```bash
python tools/build_demo.py --out build/demo-finops-preview --with-finops-preview --acknowledge-finops-preview
```

That flag is not human pricing/budget approval. Normal `build/site` is core-only;
test fixtures isolate core/Preview HTML under `build/site-e2e` with real hashed
CSP. The default complete bundle has fifteen allowlisted entries, including
four ontology documents, excluding explicit Preview demo/cost JSON and private
analysis/intake. Final runtime skill-file counts and digests are measured at
D5 after prose changes, not copied from an older handoff.

How we work is in [AGENTS.md](AGENTS.md) (for people and coding agents), [CONTRIBUTING.md](CONTRIBUTING.md) and the [engineering handbook](docs/engineering/handbook.md). GitHub Copilot is configured for this repository (instructions, custom agents, skills, hooks); the engineering method is Superpowers: see [Copilot and Superpowers](docs/engineering/copilot-and-superpowers.md).

The private repository above is the approved source/issue/PR host. [PRD](docs/prd.md) owns requirements and release decisions; [solution design](docs/solution-design.md) owns architecture and verification; [ADRs](docs/adr/README.md) record engineering rationale. New implementation uses linked [idea](docs/ideas/README.md), [spec](docs/specs/README.md), [plan](docs/plans/README.md) and [sprint](docs/sprints/README.md) records with real human design/readiness evidence and explicit plan approval. Draft a sprint early; link a real issue, owner and testable acceptance before readiness. Labels remain human-only and are not inferred from approval. Local checks do not verify live issues/approvals.

The [sole-maintainer review model](docs/engineering/github-setup.md#4-sole-maintainer-review-and-merge)
uses passing gates and recorded human sign-off, not an impossible formal
self-approval. Hosting on GitHub's public-cloud platform does not change this
repository's private visibility.

Where supported, eligible prose goes to `docs-agent`, checker/code to `frontier-builder`, HTML to `frontier-renderer`. Handoffs are harness-dependent; available Superpowers skills or the AGENTS method provide the workflow. The [policy catalogue](.github/agent-policy/README.md) remains Proposed, not an access control. Protected session-start routing still names legacy paths pending human [#8](https://github.com/urruegg/frontier-envisioning/issues/8); preserve historical links and report the limitation.

## Repository map

| Path | What it holds |
|---|---|
| [`plugin/`](plugin) | The Copilot Cowork plugin: eight skills (seven GA, one optional Preview), manifest, install check, user guide, licence and notices |
| [`src/renderer/`](src/renderer) | Sources of the blueprint HTML (assembled into the plugin's template) |
| [`tools/`](tools) | `dev.py` task runner; build, package, demo, site, release, checks, bootstrap |
| [`tests/`](tests) | Unit and pipeline tests (Python), DOM tests (happy-dom), browser tests (Playwright) |
| [`infra/`](infra), [`site/`](site), [`azure.yaml`](azure.yaml) | The showcase site on Azure Static Web Apps (Bicep, Azure Developer CLI) |
| [`docs/`](docs) | PRD and solution design, ADRs, engineering guides, analyses, plans |
| [`backlog/`](backlog) | Seed backlog for the intake (labels, milestones, issues) |
| [`releases/`](releases) | Release manifests: hashes of the published artefacts |
| [`.github/`](.github) | Workflows, Copilot instructions, agents, skills and hooks, issue and pull request templates |

## Quality gates

| Gate | Where | What |
|---|---|---|
| L0 | pre-commit, CI | template drift, Python compile, repository rules, ruff, ESLint, customer neutrality |
| L1 | CI `L1 quality gate` | L0, unit and pipeline tests, plugin self-test, package and install check, Caldova demo, release reproduction, DOM tests |
| L2 | CI `L2 browser tests`, deploy to dev | showcase site with the hosting headers, Playwright on Chromium, screenshots |
| L3 | tag `vX.Y.Z` (people, enabled explicitly) | strict L1 and L2 on the tag, bundle, pinned SBOM, provenance and `release-approval` before the draft release |

## Local intake status

The received 1.9.0 process features are selectively integrated as unreleased
1.9.1. The four-part blueprint keeps Vision, Design, Build and Workshops;
Ontology is optional in Design and FinOps is optional Preview in Build.
The [current design evidence](docs/solution-design.md#191-development-intake)
qualifies local process, gating, browser/CSP and finite raster checks by commit.
The shared Python PRD model
keeps page/scaffold IDs aligned for selected subsets. The risk register retains
normalised source bindings and retired-ID history; discarding that record
cannot guarantee old ID-only feedback identity. Attendee contributions cite
evidence and transcript times.

Plan CSV is handover data, not a live connector or native import certification.
WIP/readiness and document metadata are not permission. Customer exports remove
internal-derived content before final model generation, but are not external/IP
clearance. The private source host and Microsoft-internal distribution boundary
remain unchanged. See the [current PRD intake](docs/prd.md#191-development-intake)
and [design intake](docs/solution-design.md#191-development-intake).
The parent pre-D4 strict L1 at `c64a815` passed; it is not post-doc validation.
Final L1/L2, rebuilt distribution/offline installation preparation, advisory
review and maintainer handoff remain D5 work. Manual Cowork validators/behaviour,
Fabric tenant import/data-agent checks and AT certification are not proven by
the read-only pressure simulation or automated tests. No actual Cowork install,
publication, deployment or external clearance is claimed.

The 1.6.1 development patch addresses [issue #4](https://github.com/urruegg/frontier-envisioning/issues/4). The sticky agent list is bounded by the upper summary; the workflow remains full width below it. Historical product records remain unchanged.

On 9 November 2026 the user confirmed Microsoft approval to use the private repository above. The intake branch is based on that repository's existing `main`; the original work-repository branch and connection are preserved. Server protections, CODEOWNERS eligibility and tenant rollout remain maintainer checks, not consequences of this migration.

The 1.6.0 intake adds the Overview digital feedback loop and each agent's workflow designer, including validation, workshop feedback and solution-design output. Strict L1, 34 plugin checks, 14 DOM checks, 7 Chromium tests and all four original artifact hashes pass. The 1.4.0 records remain unchanged. See [1.6.0 intake evidence](docs/intake/handover-1.6.0.md), [design](docs/specs/2026-11-09-handover-1.6-design.md) and [historical M0 evidence](docs/intake/m0-evidence.md).

The 1.4/1.5/1.6 baselines explicitly share [verified historical raster inputs](tests/fixtures/caldova-raster-1.4.0/README.md), because their identity ZIP hashes are identical. All 205 regenerated non-raster inputs and each current release record are checked. No golden ZIP is copied and no live converter is pretended. Later versions require separate approval/rendering evidence. `python tools/build_demo.py --no-png` remains development-only; comparison rules are not weakened.

The release workflow is disabled unless a maintainer sets `RELEASE_ENABLED=true` after verifying the `release-approval` environment and its version-tag/reviewer policy. Showcase deployment remains separately controlled by `SHOWCASE_ENABLED`; neither flag was enabled during intake.

## Deploy the showcase

`azd up` provisions an Azure Static Web App with Microsoft Entra sign-in and deploys the Caldova blueprint, the identity catalogue and the plugin download. CI deploys with OpenID Connect after `azd pipeline config`. See [docs/engineering/deployment.md](docs/engineering/deployment.md).

## Licence

MIT, see [LICENSE](LICENSE). Copyright (c) 2026 Urs Rüegg. Microsoft product icons are trademarks of Microsoft and are used under Microsoft's icon terms; see [plugin/THIRD-PARTY-NOTICES.md](plugin/THIRD-PARTY-NOTICES.md).
