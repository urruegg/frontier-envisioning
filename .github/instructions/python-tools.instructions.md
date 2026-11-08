---
applyTo: "tools/**/*.py,tests/**/*.py,.github/hooks/**/*.py"
---
# Python tools and tests

- Python 3.11 or later, standard library only (development extras such as pytest and ruff are optional at run time; tools degrade with a clear "skipped" message and fail in strict mode).
- Entry point `main(argv=None) -> int`; argparse with a module docstring as help; paths from `tools/fe_lib.py` (`ROOT`, `PLUGIN`, `SKILLS`, ...), never absolute paths.
- Write files as UTF-8 with LF (`newline="\n"`), so outputs and checksums are identical on Windows, macOS and Linux.
- Tests are `unittest.TestCase` classes (pytest runs them too), deterministic, offline, and write only to temporary folders.
- The hook scripts in `.github/hooks/scripts/` are human-maintained guardrails; propose changes in the pull request description instead of editing them.
