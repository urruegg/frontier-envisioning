---
name: frontier-skill-authoring
description: Add or change a skill of the Frontier Envisioning Copilot Cowork plugin (plugin/skills) - SKILL.md frontmatter and routing, procedure, references, standard-library scripts, Caldova examples, self-test and manifest registration. Use when asked to create a new Frontier skill, change a skill's behaviour, add a script or reference, or fix skill routing.
---
# Authoring Frontier plugin skills

## Frontmatter

```yaml
---
name: frontier-<topic>            # equals the folder name
description: |
  What it does in one or two sentences. Use when asked to "<example request>", "<example>".
  Do NOT use for <neighbour task> (use <sibling or built-in skill>).
license: MIT
metadata:
  category: productivity
  icon: <Fluent icon name>
  version: "<plugin version>"
  plugin: frontier-envisioning
---
```

- Description within 900 UTF-16 units; `python tools/check_repo.py` checks. Keep the "Do NOT use" lines: they prevent routing collisions with sibling skills and Cowork's built-in skills (meeting recap, HTML, documents, HubWorks).

## Body

- Steps the Cowork agent follows, with gates and the exact script calls (`python scripts/<x>.py --flag ...`), inputs and outputs, what to tell the user, and failure handling.
- Long material goes to `references/*.md`; data to `templates/` or `examples/`; examples use the fictitious Caldova Industrial AG.

## Scripts

- Python standard library only, offline, `main(argv) -> int`, JSON summary on stdout, UTF-8 files, deterministic.
- Cover them in `tools/selftest.py` (end to end) and `tests/unit/` (focused).

## Registration and release

- New skill: add it to `plugin/package/manifest.json` `agentSkills`, the plugin README skill table, the PRD (A.7, B.2.1) and `AGENTS.md` section 1.
- Bump the version first if the current one is released; run `python tools/dev.py package` and commit `plugin/install/plugin-install.json`.
- Before release, a person runs the Cowork skill validators and the behavioural prompts of PRD B.9 in Copilot Cowork.
