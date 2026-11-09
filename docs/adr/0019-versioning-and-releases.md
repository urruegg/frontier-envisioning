# ADR-0019: Versioning and releases

**Status:** Proposed (8 November 2026), decision ENG-D4

## Context
The plugin version appears in eleven places; the Microsoft 365 app manifest accepts digits only. Releases were zipped by hand.

## Decision
Semantic versioning (MAJOR for incompatible schema, skill-contract or install changes; MINOR for capability; PATCH for fixes). `tools/bump_version.py` changes every carrier. Released versions are immutable: the first change to `plugin/` after a release bumps the version. Releases are built only from a tag `vX.Y.Z` by the `release` workflow: strict L1, bundle, release manifest, SPDX SBOM (Microsoft SBOM tool), build provenance attestation, draft release after the `prod` approval; a person publishes.

## Consequences
Every published artefact is traceable to a commit and verifiable. Main always carries the version in development.

## Alternatives considered
Pre-release suffixes (not accepted by the app manifest); releases from a branch without tags (no provenance anchor).
