# ADR-0021: AI-assisted engineering with GitHub Copilot and Superpowers

**Status:** Proposed (8 November 2026), decision ENG-D2 for the cloud agent

## Context
The team wants to refine and extend the plugin with GitHub Copilot, using the Superpowers method that was already applied in other Hub repositories, while keeping control of design, merges, releases and deployments.

## Decision
GitHub Copilot is the coding agent on all surfaces (VS Code, CLI, cloud agent, code review). The repository provides always-on instructions, `AGENTS.md`, path instructions, five custom agents (planner, builder, renderer, reviewer, release manager) and five project skills. Superpowers v7.0.2 is the method: the Copilot CLI plugin for engineers, personal skills for VS Code, and, if ENG-D2 agrees, the pinned skills vendored into `.agents/skills` with a lock file and licence notice for the cloud agent.

## Consequences
Consistent behaviour across surfaces; reproducible agent context in Git. Vendoring adds third-party files that change only through `tools/superpowers.py` and a reviewed pull request.

## Alternatives considered
Prompt files (VS Code local harness only); no method beyond instructions (less consistent plans and testing).
