# ADR-0017: Repository layout

**Status:** Proposed (8 November 2026)

## Context
Release 1.4.0 was built in Copilot Cowork: one folder with the plugin, tools and documentation, and the renderer sources and checks in separate working folders with absolute paths. A controlled engineering approach needs one repository that people and agents can build and test anywhere.

## Decision
- `plugin/` is the packaged unit, exactly what goes into the Cowork package (skills, manifest, install check, user README, MIT, notices).
- `src/renderer/` holds the blueprint HTML sources; `tools/assemble_template.py` writes the template into the plugin. The generated template and `plugin/install/plugin-install.json` stay committed (Cowork users get them inside the package) and CI fails on drift.
- `tools/` holds repository tools in standard-library Python with one entry point, `tools/dev.py`; `tests/`, `infra/`, `site/`, `docs/`, `backlog/` and `releases/` complete the layout.

## Consequences
The package builds byte-identical to 1.4.0 from the new layout. Contributors edit sources, never generated files (the guard hook enforces it for agents). The packaged README keeps a short developer section until 1.6.0 (INT-10).

## Alternatives considered
Plugin at the repository root (mixes engineering files with the packaged unit); generated template not committed (Cowork users and reviewers would lose the artefact; drift checks cover the risk).
