#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""sessionStart hook: give every Copilot agent session the repository's working agreement in a few lines."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def main() -> int:
    try:
        vendored = (REPO / ".agents" / "skills" / "superpowers.lock.json").exists()
        sp = ("Superpowers skills are vendored in .agents/skills: use them (brainstorming, writing-plans, "
              "test-driven-development, systematic-debugging, verification-before-completion, requesting-code-review)."
              if vendored else
              "If the Superpowers skills are available, use them for brainstorming, plans, TDD, debugging, verification and review.")
        ctx = ("Frontier Envisioning repository (Copilot Cowork plugin, MIT). Read AGENTS.md before changing anything. "
               "Work from a real issue and linked idea/spec/plan/sprint package; new records use docs/ideas/, docs/specs/, docs/plans/ and docs/sprints/; historical specs/plans retain their evidence; test first; "
               "run 'python tools/dev.py check' before you finish and paste the summary into the pull request. "
               "Human-only: merging, approvals, releases and tags, deployments, repository settings, readiness and approval labels, "
               "the guardrail files. Never write real customer names; the demo company is the fictitious Caldova. " + sp)
        print(json.dumps({"additionalContext": ctx}))
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
