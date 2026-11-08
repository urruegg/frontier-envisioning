---
id: INT-14
title: "First release from the repository: tag v1.4.0 on the import commit"
milestone: "M0"
labels: [type:chore, area:engineering, human-only, priority:P2, size:S]
---
## Context

The release workflow builds, attests and drafts a GitHub release from a tag. Tagging the import commit as v1.4.0 proves the pipeline without changing the plugin.

## Acceptance criteria

- [ ] The release manager pushes tag v1.4.0
- [ ] Draft release with the plugin package, demo, identity kit, catalogue, bundle, SBOM and checksums
- [ ] Assets match releases/1.4.0/manifest.json
- [ ] Install from the release asset in a Cowork chat succeeds
