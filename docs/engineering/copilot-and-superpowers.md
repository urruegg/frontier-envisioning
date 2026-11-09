# AI-assisted engineering: GitHub Copilot and Superpowers

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Copilot and Superpowers engineering guide; document revision, not product version |
| References | [Documentation](../README.md), [Working agreement](../../AGENTS.md), [Engineering handbook](handbook.md), [Work packages](../plan/README.md) |

This repository is built with GitHub Copilot as the coding agent and **Superpowers** (obra/superpowers, MIT) as the engineering method: brainstorm, plan, test first, debug systematically, verify before completion, review, finish the branch. The repository adds its own instructions, agents, skills and deterministic guardrails so that agents work through pull requests and people keep the decisions.

## 1. Copilot surfaces and what they read

| Surface | Repository instructions and `AGENTS.md` | Path instructions | Custom agents | Skills | Hooks |
|---|---|---|---|---|---|
| VS Code agent mode | yes | yes | yes (`.github/agents`) | project and personal | preview |
| Copilot CLI | yes | yes | yes | project, personal, plugins | yes |
| Copilot cloud agent (GitHub) | yes | yes | yes | project skills | yes (`bash` entries) |
| Copilot code review | yes | yes | | yes | |

Project skills are read from `.github/skills`, `.claude/skills` or `.agents/skills`; personal skills from `~/.copilot/skills` or `~/.agents/skills`. Cloud agent sessions on GitHub Actions do not load personal skills. Sources: GitHub Docs, *Copilot customization cheat sheet*, *About agent skills*, *Hooks reference*.

## 2. What is configured here

| File | Purpose |
|---|---|
| `.github/copilot-instructions.md` | Always-on rules: map, customer neutrality, standard-library plugin, generated files, test first, verification, versions, icons, human-only actions |
| `AGENTS.md` | The full working agreement for every agent and person |
| `.github/instructions/*.instructions.md` | Rules per area: plugin skills, renderer, Python tools, infrastructure, workflows, documentation |
| `.github/agents/frontier-planner.agent.md` | Issue to spec and test-first plan; checks the Definition of Ready |
| `.github/agents/frontier-builder.agent.md` | Implements a plan test-first, runs the gates, opens a draft pull request |
| `.github/agents/frontier-renderer.agent.md` | Blueprint HTML specialist (views, DOM and browser tests, accessibility, CSP) |
| `.github/agents/frontier-reviewer.agent.md` | Reviews against the plan and the rules; reports by severity; no edits |
| `.github/agents/frontier-release-manager.agent.md` | Prepares the release pull request; never tags or publishes |
| `.github/skills/frontier-dev-loop` | Gates L0 to L3, commands, fixing failures |
| `.github/skills/frontier-skill-authoring` | Adding or changing plugin skills |
| `.github/skills/frontier-renderer-change` | Changing the blueprint HTML |
| `.github/skills/frontier-release` | Preparing and verifying a release |
| `.github/skills/frontier-intake` | From request to ready work item |
| `.github/hooks/guardrails.json` | `sessionStart` (working agreement in a few lines) and `preToolUse` (guard) |
| `.github/workflows/copilot-setup-steps.yml` | Python, Node, dev dependencies and Chromium for cloud agent sessions |
| `.vscode/mcp.json` | Microsoft Learn MCP server (grounding in Microsoft documentation), Playwright MCP server |

In VS Code the custom agents offer hand-offs: planner to builder, builder to reviewer, reviewer back to builder.

## 3. Superpowers

Superpowers v7.0.2 provides, among others: `brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `requesting-code-review`, `receiving-code-review`, `using-git-worktrees`, `finishing-a-development-branch`, `dispatching-parallel-agents`, `writing-skills`, `using-superpowers`.

| Surface | How to get it |
|---|---|
| Copilot CLI (recommended) | `copilot plugin marketplace add obra/superpowers-marketplace`, then `copilot plugin install superpowers@superpowers-marketplace` |
| VS Code agent mode | `python tools/superpowers.py install-user` (copies the pinned skills to `~/.copilot/skills`), or a plugin marketplace in VS Code if your version offers Superpowers |
| Copilot cloud agent | Decision ENG-D2: `python tools/superpowers.py vendor` copies the pinned skills with a lock file and licence notice into `.agents/skills`; `python tools/superpowers.py verify` runs in CI |

`python tools/superpowers.py status` shows what is installed. The guard hook lets agents run `status` and `verify` but not `vendor` or `install-user` (a person decides on third-party code).

## 4. From issue to release

| Step | Superpowers skill | Repository practice | Gate | Who |
|---|---|---|---|---|
| Ready | | Definition of Ready, `status:ready` | | person |
| Spec | `brainstorming` | `docs/spec/...-design.md`; `approved:design` for big changes | | planner agent, person approves |
| Plan | `writing-plans` | `docs/plan/...-plan.md` with failing tests first | | planner agent |
| Branch | `using-git-worktrees` | `feat/<issue>-<topic>` | | builder agent |
| Build | `test-driven-development`, `subagent-driven-development` or `executing-plans` | stdlib plugin, generated files via tools | L0 on commit | builder or renderer agent |
| Debug | `systematic-debugging` | regression test for every bug | | agent |
| Verify | `verification-before-completion` | `python tools/dev.py check` (+ `site e2e`) | L1, L2 | agent |
| Review | `requesting-code-review`, `receiving-code-review` | draft pull request, reviewer agent, Copilot code review, code owner | L1 and L2 required | agents, person |
| Finish | `finishing-a-development-branch` | squash merge by a person | | person |
| Release | | release pull request, tag, approval, publish | L3 | release-manager agent prepares, person releases |

New work links the real issue, [idea](../idea/README.md),
[spec](../spec/README.md), [plan](../plan/README.md) and
[sprint](../sprint/README.md). [Legacy plans](../plans/README.md) remain historical.

## 5. Working with the Copilot cloud agent

1. Make the issue ready and link the plan; add `agent:copilot`.
2. Assign the issue to Copilot and choose the custom agent (builder for code, renderer for the HTML, planner when only a plan is wanted).
3. The agent works on a branch in its own environment (`copilot-setup-steps.yml`), with the hooks active, and opens a pull request.
4. Review like any pull request; ask for changes in review comments. A person merges.

## 6. Prompts that work

- "Use the frontier-planner agent: plan issue INT-11. Ask me before choosing between the options."
- "Implement docs/plan/2026-11-12-closeout-pack-plan.md test-first; stop after each task and show the test output."
- "Add a DOM test that fails today: the FinOps page must show the purchase options for the Caldova MVP agents."
- "Review this branch with the frontier-reviewer agent and list Critical and Important findings only."
- "Prepare the 1.5.0 release pull request; do not tag."

## 7. Guardrails

The `preToolUse` hook (`.github/hooks/scripts/guard.py`, tested in `tests/unit/test_guard_hook.py`) denies, with a reason the agent can act on:

- merging, approving, releases and release tags, force pushes and pushes to `main`, repository settings, secrets and variables, protected labels, running workflows by hand, writes to the GitHub API;
- `azd` and `az` changes (agents may run `az bicep build`), piping downloads into a shell, reading tokens or secrets, bypassing commit hooks;
- edits to generated files, the guardrails, `CODEOWNERS`, the licence, the release and deployment workflows, release manifests, the neutrality denylist and vendored skills;
- new content that contains a denylisted customer name.

The hook never crashes into a denial: on an internal error it allows the call and reports on stderr. Rulesets, environment approvals and code owner reviews remain the authoritative controls; the hook makes agents fail early with a clear reason. Changing the hooks is a human pull request.

## 8. Limits

- Hooks run in Copilot CLI and the cloud agent; VS Code support is in preview. Instructions alone are not a permission boundary; rulesets and approvals are.
- Prompt files run only in VS Code's local harness; this repository uses skills instead, which work on every surface.
- Custom agent hand-offs are a VS Code feature; the cloud agent ignores them.
