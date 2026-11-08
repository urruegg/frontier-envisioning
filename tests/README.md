# Tests

| Folder | Runner | Command |
|---|---|---|
| `unit/` | unittest (pytest in CI) | `python tools/dev.py test` |
| `pipeline/` | unittest (slow: plugin self-test, release reproduction) | `python tools/dev.py test-all` |
| `dom/` | `node:test` with happy-dom on `build/demo` | `python tools/dev.py dom` |
| `e2e/` | Playwright (Chromium) on `build/site` served with the hosting headers | `python tools/dev.py site e2e` |

Strategy: `docs/engineering/testing-strategy.md`. Fictitious data only.
