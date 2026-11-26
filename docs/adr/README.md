# Architecture decision records

| Field | Value |
|---|---|
| Version | 0.8 |
| Date | 2026-11-26 |
| Author | Original author not recorded; Copilot AI-assisted maintenance; AI assistant (AI-assisted #70 release evidence rationale); Copilot (AI-assisted #78 Factory rationale) |
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
| [0026](0026-process-ontology-fabric-iq.md) | Optional process ontology wrapper and local OWL/Turtle handover (1.9.1 development intake) | Proposed |
| [0027](0027-cdm-grounding-and-data-products.md) | Proposed CDM mappings, medallion semantic layer and governed data products; not FinOps | Proposed |
| [0028](0028-versioned-agent-finops-baselines.md) | Offline versioned FinOps baselines, explicit legacy compatibility and strict financial build-handover evidence | Proposed; architecture choice recorded on #35/#36, written/PR acceptance separate |
| [0030](0030-pr-gated-engineering-automation.md) | Human native PR approval with isolated App authorship, trusted execution and engineering/release automation | Proposed; written proposal approved at `8de16ca` for planning on #48, PR acceptance pending |
| [0031](0031-release-assets-as-evidence.md) | Exact-version release assets, validated offline cache and strict CI without recurring manual retention | Proposed; #67 spec/plan approved, protected evidence-access adoption pending |
| [0032](0032-offline-agent-factory-handover.md) | Optional Preview offline full-foundation Factory handover, strict intake and separate host/review authority | Proposed; #72 spec/full plan approved, ninth skill registered with maturity/installer metadata, final candidate verification pending |

Template: Context, Decision, Consequences, Alternatives considered, Status.

ADR-0029 is already allocated to the
[unmerged #46/#47 manual-publication proposal](https://github.com/urruegg/frontier-envisioning/blob/4450e46b2e5930ec41dee0f5218751b28d090dba/docs/adr/0029-free-private-release-preparation.md).
Preserve that number and its commit-qualified evidence; it is not a missing
current file or an accepted main-branch decision.
