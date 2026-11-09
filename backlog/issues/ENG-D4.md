---
id: ENG-D4
title: "Decision: release immutability and versioning"
milestone: "M0"
labels: [type:decision, area:engineering, human-only, priority:P2, size:S]
---
## Context

Proposed: a released version is immutable; the first change to plugin/ after a release bumps the version (`python tools/dev.py bump X.Y.Z`); main always carries the version in development; tags and manifests record releases (ADR-0019).

## Acceptance criteria

- [ ] Policy accepted and written into the engineering handbook
