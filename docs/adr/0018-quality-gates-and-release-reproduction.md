# ADR-0018: Quality gates L0 to L3 and release reproduction

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Proposed |
| Scope | Quality gates and release reproduction decision; document revision, not product version |
| References | [ADR catalogue](README.md), [Testing strategy](../engineering/testing-strategy.md), [Solution design](../solution-design.md#b9-quality-and-testing) |

**Status:** Proposed (8 November 2026)

## Context
Quality in 1.0 to 1.4 relied on a self-test and manual checks run in Cowork. The intake must prove nothing was lost and keep quality enforceable for people and agents.

## Decision
Four gates with one command each (`tools/dev.py`): L0 on commit (drift, lint, repository rules, neutrality), L1 on every pull request (unit tests, plugin self-test, package and install check, Caldova demo, release reproduction, DOM tests), L2 browser tests and deployment to dev, L3 on release tags. `releases/<version>/manifest.json` records the published artefacts; while the plugin version is a released one, L1 rebuilds and compares them byte for byte (the demo after normalising its build date).

## Consequences
The import is verified objectively. Strict mode in CI makes optional tools mandatory. Cowork-only checks remain a release checklist item.

## Alternatives considered
Snapshot tests of selected HTML fragments (weaker than full reproduction); manual release checks only (not enforceable for agents).
