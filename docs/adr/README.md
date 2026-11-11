# Architecture decision records

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-11 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained catalogue; decision approval not inferred |
| Scope | Architecture decision routing; document revision, not product version |
| References | [Documentation](../README.md), [Product requirements](../prd.md), [Technical decision records](../solution-design.md#b12-architecture-decisions) |

Product and plugin decisions ADR-0001 to ADR-0016 are recorded in the [solution design, section B.12](../solution-design.md#b12-architecture-decisions). Decisions about the repository and the engineering setup start at ADR-0017 and live here, one file per decision; product decisions taken after the move (from ADR-0023) live here too. Status is *Proposed* until a person accepts it in a pull request.

| ADR | Title | Status |
|---|---|---|
| [0017](0017-repository-layout.md) | Repository layout: the plugin as the packaged unit, renderer sources, generated files committed with drift checks | Proposed |
| [0018](0018-quality-gates-and-release-reproduction.md) | Quality gates L0 to L3 and release reproduction | Proposed |
| [0019](0019-versioning-and-releases.md) | Versioning, immutable releases, tag-driven release with SBOM and provenance | Proposed |
| [0020](0020-showcase-hosting.md) | Showcase on Azure Static Web Apps with azd, Bicep, OpenID Connect and Entra sign-in | Proposed |
| [0021](0021-ai-assisted-engineering.md) | AI-assisted engineering with GitHub Copilot and Superpowers | Proposed |
| [0022](0022-deterministic-guardrails.md) | Deterministic guardrails: hooks and a hashed customer denylist | Proposed |
| [0023](0023-digital-feedback-loop.md) | Digital feedback loop on the Overview: SVG animation, official Microsoft names only (product, 1.5.0) | Proposed |
| [0024](0024-agent-workflow-view.md) | Agent workflow in the Copilot Studio workflow designer style, derived from the plan until authored (product, 1.6.0) | Proposed |
| [0025](0025-four-part-journey-structure.md) | Four-part journey, shared PRD model, Plan board, risks and evidenced attendees (selective 1.7.1 intake) | Proposed |

Template: Context, Decision, Consequences, Alternatives considered, Status.
