# Security

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Security reporting and repository protections; document revision, not product version |
| References | [Documentation](docs/README.md), [Working agreement](AGENTS.md), [Engineering handbook](docs/engineering/handbook.md) |

## Reporting

Report a vulnerability privately to the repository owner (GitHub private vulnerability reporting when enabled, otherwise e-mail the maintainer). Do not open a public issue. Include the affected version, the steps to reproduce and the impact.

## What this repository protects

- **Customer data.** The repository, the packages and the showcase contain fictitious data only (Caldova Industrial AG). A hashed denylist (`tools/neutrality.py`) and the agent hooks block real customer names. Report any leak immediately; it is handled like a security incident.
- **Secrets.** No secrets in the repository. Azure sign-in from GitHub uses OpenID Connect (federated credentials); the showcase's sign-in secret is an environment secret. Secret scanning and push protection are on where the plan allows; `tools/check_repo.py` blocks key files and common token formats.
- **Supply chain.** Plugin scripts use the Python standard library only. Development dependencies are pinned and updated by Dependabot; actions are pinned by version (by commit SHA after INT-07). Releases carry an SPDX SBOM and a build provenance attestation.
- **The showcase.** Microsoft Entra sign-in for one tenant, strict Content-Security-Policy (inline scripts by hash only, no external resources, no framing) and security headers.
- **AI-assisted engineering.** Coding agents work through pull requests; hooks deny human-only actions (merge, release, tags, deployments, settings) and edits to the guardrails. See `.github/hooks/`.

## Supported versions

The latest release receives fixes. Earlier releases are superseded.
