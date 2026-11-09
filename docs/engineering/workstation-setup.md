# Workstation setup

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Development environment setup guide; document revision, not product version |
| References | [Documentation](../README.md), [Contributing](../../CONTRIBUTING.md), [Engineering handbook](handbook.md), [Testing strategy](testing-strategy.md) |

## Option A: dev container (recommended)

Open the repository in VS Code with the Dev Containers extension (or in GitHub Codespaces). The container brings Python 3.12, Node.js 22, GitHub CLI, Azure CLI with Bicep and the Azure Developer CLI, runs `python tools/dev.py setup` (pytest, ruff, PyYAML, happy-dom, ESLint, Playwright Chromium), installs the pre-commit hook and prints `python tools/dev.py doctor`.

## Option B: local machine

| Tool | Windows (winget) | macOS (Homebrew) |
|---|---|---|
| Python 3.11+ | `winget install Python.Python.3.12` | `brew install python@3.12` |
| Node.js 22+ | `winget install OpenJS.NodeJS.LTS` | `brew install node@22` |
| Git | `winget install Git.Git` | `brew install git` |
| GitHub CLI | `winget install GitHub.cli` | `brew install gh` |
| Azure CLI (Bicep) | `winget install Microsoft.AzureCLI`, then `az bicep install` | `brew install azure-cli` |
| Azure Developer CLI | `winget install Microsoft.Azd` | `brew install azure/azd/azd` |
| VS Code | `winget install Microsoft.VisualStudioCode` | `brew install --cask visual-studio-code` |

Then, in the repository:

For Windows local development, select an installed supported interpreter and use a virtual environment. An inherited `PYTHONHOME` can override that interpreter and must be cleared in this shell only:

```powershell
if (Test-Path Env:PYTHONHOME) { Remove-Item Env:PYTHONHOME }
py -3.11 -m venv .venv
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + ';' + $env:PATH
$env:PYTHONUTF8 = '1'
python tools\dev.py setup
python tools\dev.py doctor
python tools\dev.py ci
```

The checked local intake environment is Python 3.11/Node 24; the preferred CI/devcontainer environment remains Python 3.12/Node 22. Do not recreate an existing environment unnecessarily. Playwright installation and `e2e` use `build/playwright-browsers` by default; an explicit `PLAYWRIGHT_BROWSERS_PATH` override is preserved.

```bash
python tools/dev.py setup        # development dependencies and Chromium
pre-commit install               # gate L0 on every commit
python tools/dev.py doctor       # what is installed
python tools/dev.py check        # gate L1
```

Windows: if long-path support is needed, configure this repository only (`git config --local core.longpaths true`). Line endings are normalised to LF by `.gitattributes`; keep it that way, the package checksums depend on it.

## VS Code

- Accept the recommended extensions (`.vscode/extensions.json`): GitHub Copilot Chat, Python, Ruff, ESLint, Playwright, Bicep, Azure Developer CLI, GitHub Actions, EditorConfig.
- `.vscode/settings.json` marks generated files read-only and enables `AGENTS.md` and instruction files for Copilot.
- `.vscode/tasks.json` has tasks for the gates, the demo, the showcase and the tests.
- `.vscode/mcp.json` adds the Microsoft Learn MCP server (Microsoft documentation for grounding, for example Frontier, Copilot Studio, Azure landing zone) and the Playwright MCP server.

## GitHub Copilot CLI and Superpowers

```bash
npm install -g @github/copilot          # Copilot CLI
copilot                                  # sign in, then in the session:
copilot plugin marketplace add obra/superpowers-marketplace
copilot plugin install superpowers@superpowers-marketplace
```

For VS Code agent mode without the plugin: `python tools/superpowers.py install-user`. Check with `python tools/superpowers.py status`. A working install starts with brainstorming when you ask for a new feature.

## Copilot Cowork

To try a change in Cowork: `python tools/dev.py package`, attach `dist/frontier-envisioning-plugin-<version>.zip` in a Cowork chat and say "Install the Frontier PlugIn".
