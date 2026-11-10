# Anonymised repository references and clean distribution

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; maintainer-requested, AI-assisted maintenance |
| Status | Direct cleanup request; internal-audience assumption, not external publication approval |
| Scope | Current source anonymisation and technically validated plugin/bundle output; repository remains private |
| References | [Catalogue](README.md), [Issue #20](https://github.com/urruegg/frontier-envisioning/issues/20), [Spec](../specs/2026-11-10-anonymised-distribution-design.md), [Plan](../plans/2026-11-10-anonymised-distribution-plan.md), [Sprint](../sprints/SPRINT-002-anonymised-distribution.md) |

The maintainer requests removal of their enterprise-account identifier from the
current repository and a clean plugin package. The original scan found eighteen
literal references in eleven tracked files, all outside the packaged plugin.
The existing plugin ZIP had no such literal value, but the complete bundle
included an explicitly internal repository analysis.

Use current-tree anonymisation plus pre-write artifact validation. Package-only
rebuilding would not clean the source; history rewriting would unnecessarily
damage provenance. Retain the public-cloud maintainer, copyright and licences.
Keep original history and immutable releases private and unchanged.

The clarification form was unavailable. Conservatively prepare for
Microsoft-internal distribution only. This is an assumption, not a human
external/IP approval, formal plan approval or protected-label change.
