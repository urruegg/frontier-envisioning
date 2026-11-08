# Architecture decision records

Product and plugin decisions ADR-0001 to ADR-0016 are recorded in the PRD (`docs/prd-and-solution-design.md`, section B.12). Decisions about the repository and the engineering setup start at ADR-0017 and live here, one file per decision. Status is *Proposed* until a person accepts it in a pull request.

| ADR | Title | Status |
|---|---|---|
| [0017](0017-repository-layout.md) | Repository layout: the plugin as the packaged unit, renderer sources, generated files committed with drift checks | Proposed |
| [0018](0018-quality-gates-and-release-reproduction.md) | Quality gates L0 to L3 and release reproduction | Proposed |
| [0019](0019-versioning-and-releases.md) | Versioning, immutable releases, tag-driven release with SBOM and provenance | Proposed |
| [0020](0020-showcase-hosting.md) | Showcase on Azure Static Web Apps with azd, Bicep, OpenID Connect and Entra sign-in | Proposed |
| [0021](0021-ai-assisted-engineering.md) | AI-assisted engineering with GitHub Copilot and Superpowers | Proposed |
| [0022](0022-deterministic-guardrails.md) | Deterministic guardrails: hooks and a hashed customer denylist | Proposed |

Template: Context, Decision, Consequences, Alternatives considered, Status.
