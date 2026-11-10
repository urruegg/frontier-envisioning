# Tests

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Test-suite entry points; document revision, not product version |
| References | [Documentation](../docs/README.md), [Testing strategy](../docs/engineering/testing-strategy.md), [Engineering handbook](../docs/engineering/handbook.md) |

| Folder | Runner | Command |
|---|---|---|
| `unit/` | unittest (pytest in CI) | `python tools/dev.py test` |
| `pipeline/` | unittest (slow: plugin self-test, release reproduction) | `python tools/dev.py test-all` |
| `dom/` | `node:test` with happy-dom on `build/demo` | `python tools/dev.py dom` |
| `e2e/` | Playwright (Chromium) on `build/site` served with the hosting headers | `python tools/dev.py site e2e` |

Strategy: [testing strategy](../docs/engineering/testing-strategy.md). Fictitious data only.
