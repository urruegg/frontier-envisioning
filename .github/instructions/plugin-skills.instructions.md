---
applyTo: "plugin/skills/**"
---
# Plugin skills (Copilot Cowork)

- Each skill folder holds `SKILL.md` with YAML frontmatter: `name` equals the folder name, `description` (what it does, when to use it with quoted example requests, and `Do NOT use for ...` lines that route to the sibling skill or the built-in skill), `license: MIT`, `metadata.version` equal to the plugin version, `metadata.plugin: frontier-envisioning`.
- Keep `description` within 900 UTF-16 units (house rule for routing quality; the Agent Skills limit is 1,024 characters). `python tools/check_repo.py` enforces both.
- The body is the procedure the Cowork agent follows: numbered steps, gates, inputs and outputs, the exact script calls, and what to tell the user. Long material goes to `references/`; keep `SKILL.md` focused.
- Scripts in `scripts/` use the Python standard library only, run offline, accept `main(argv) -> int`, print a JSON summary on success and write UTF-8 files. They must stay deterministic: the release check compares outputs byte for byte.
- Examples use the fictitious Caldova Industrial AG only. Evidence, quotes and numbers in examples are invented.
- Shared code that two skills need (for example `fv_expr.py`) stays byte-identical in both; the repository check fails otherwise.
- A new script is covered by the self-test (`tools/selftest.py`) and by unit tests in `tests/unit/`.
- A new skill is registered in `plugin/package/manifest.json` (`agentSkills`) and described in the plugin README and the PRD.
- Any change here changes the package: bump the version first when the current version is released (`python tools/dev.py bump X.Y.Z`).
