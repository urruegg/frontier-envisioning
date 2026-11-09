# Frontier Envisioning

**Innovation Hub Frontier solution envisioning and architecture design, as a Copilot Cowork plugin.**

Frontier Envisioning helps Microsoft Innovation Hub solution engineers prepare and run Frontier envisioning and architecture design workshops. It gathers the customer context from Work IQ and workshop transcripts, builds the interactive **Frontier Company Blueprint** along the Hub journey (vision, design, workshop), writes the PRD, solution design, ADRs and IT readiness checklist, creates the agent identity kit and models the business value and what the agents cost.

| | |
|---|---|
| Current release | **1.4.0** (8 November 2026), imported from Copilot Cowork as the engineering baseline |
| Repository home | [urruegg/frontier-envisioning](https://github.com/urruegg/frontier-envisioning), private; use approved work material only |
| Plugin licence | MIT (Microsoft product icons: see [THIRD-PARTY-NOTICES.md](plugin/THIRD-PARTY-NOTICES.md)) |
| Demo data | the fictitious Caldova Industrial AG only |
| Status | Intake: see [docs/engineering/intake-plan.md](docs/engineering/intake-plan.md) and milestone *M0 · Intake baseline* |

## Use the plugin

1. Download `frontier-envisioning-plugin-<version>.zip` from the latest release (keep it zipped).
2. Attach it in a new Copilot Cowork chat and type **Install the Frontier PlugIn**.
3. Approve each step. The user guide is [plugin/README.md](plugin/README.md).

## Develop

Use an isolated Python environment; see [workstation setup](docs/engineering/workstation-setup.md). The local intake uses Python 3.11 and Node 24 within the supported ranges; CI and the dev container retain Python 3.12 and Node 22. Playwright downloads stay in `build/playwright-browsers` unless `PLAYWRIGHT_BROWSERS_PATH` is explicitly set.

Open the repository in the dev container (VS Code or Codespaces), or install Python 3.11+, Node.js 22+ and Git, then:

```bash
python tools/dev.py setup      # pytest, ruff, PyYAML, happy-dom, ESLint, Playwright Chromium
python tools/dev.py doctor     # what is installed
python tools/dev.py check      # gate L1: everything CI runs (a few minutes)
```

How we work is in [AGENTS.md](AGENTS.md) (for people and coding agents), [CONTRIBUTING.md](CONTRIBUTING.md) and the [engineering handbook](docs/engineering/handbook.md). GitHub Copilot is configured for this repository (instructions, custom agents, skills, hooks); the engineering method is Superpowers: see [Copilot and Superpowers](docs/engineering/copilot-and-superpowers.md).

## Repository map

| Path | What it holds |
|---|---|
| [`plugin/`](plugin) | The Copilot Cowork plugin, the packaged unit: seven skills, manifest, install check, user guide, licence and notices |
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

On 9 November 2026 the user confirmed Microsoft approval to use the private repository above. The intake branch is based on that repository's existing `main`; the original work-repository branch and connection are preserved. Server protections, CODEOWNERS eligibility and tenant rollout remain maintainer checks, not consequences of this migration.

All four 1.4.0 artifacts reproduce their immutable release hashes, including the complete identity ZIP. The original OneDrive artifacts were recovered and verified; shipped product/renderer source bytes remain unchanged. Local strict L1 passes. See [M0 evidence](docs/intake/m0-evidence.md).

The 1.4.0 build uses [verified historical raster inputs](tests/fixtures/caldova-raster-1.4.0/README.md), guarded by all 205 regenerated non-raster inputs. It does not copy the golden ZIP or pretend a live converter ran. Other versions require their own rendering setup. `python tools/build_demo.py --no-png` remains an explicitly SVG-only development variant, not release reproduction. Text/ZIP metadata is canonicalised without weakening comparison rules.

The release workflow is disabled unless a maintainer sets `RELEASE_ENABLED=true` after verifying the `release-approval` environment and its version-tag/reviewer policy. Showcase deployment remains separately controlled by `SHOWCASE_ENABLED`; neither flag was enabled during intake.

## Deploy the showcase

`azd up` provisions an Azure Static Web App with Microsoft Entra sign-in and deploys the Caldova blueprint, the identity catalogue and the plugin download. CI deploys with OpenID Connect after `azd pipeline config`. See [docs/engineering/deployment.md](docs/engineering/deployment.md).

## Licence

MIT, see [LICENSE](LICENSE). Copyright (c) 2026 Urs Rüegg. Microsoft product icons are trademarks of Microsoft and are used under Microsoft's icon terms; see [plugin/THIRD-PARTY-NOTICES.md](plugin/THIRD-PARTY-NOTICES.md).
