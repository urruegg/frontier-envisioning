# Human Governance and Acceptance Implementation Plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Copilot SDK in VS Code; human handoff preparation |
| Status | Proposed human-only procedure; no protected action performed |
| Scope | DG-06, protected intake routing and manual accessibility acceptance |
| References | [Issue](https://github.com/urruegg/frontier-envisioning/issues/8), [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md), [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [Sprint](../sprint/SPRINT-001-docs-governance-and-accessibility.md), [Master](2026-11-09-docs-governance-implementation.md) |

> **For agentic workers:** Do not execute H1-H4. Prepare evidence and hand
> this plan to a person. Delegated implementation authority excludes these
> tasks even after the implementation plan is approved.

**Goal:** Align actual ownership, collaboration and runtime routing while
retaining human controls and honest assistive-technology acceptance.

**Architecture:** Humans apply protected files/settings in a separate reviewed
PR and record actual control evidence; agents implement only non-protected
prerequisites. No emergency shortcut is part of this migration.

**Tech Stack:** GitHub collaboration/review UI, protected repository files,
existing Python gates and actual Microsoft Edge/assistive technology.

---

## H1: collaborator eligibility and ownership (person only)

- [ ] Verify the repository is the approved private `urruegg/frontier-envisioning`.
      Confirm whether `@urruegg_microsoft` is already an accepted collaborator
      with effective write access and whether account/enterprise policy permits
      external collaboration with this personal repository.
- [ ] If eligible and missing, the person sends the invitation and verifies
      actual acceptance/effective access. Do not grant admin merely to satisfy
      CODEOWNERS. If account policy prevents it, stop and record that decision;
      do not bypass enterprise restrictions or silently change source host.
- [ ] The person applies this ownership content in their governed branch:

```text
# Default accountable maintainer
*                       @urruegg

# Documentation and Frontier domain design, including lifecycle records
/docs/                  @urruegg @urruegg_microsoft

# Product and immutable release records
/plugin/                @urruegg @urruegg_microsoft
/releases/              @urruegg @urruegg_microsoft

# Preserve current infrastructure ownership
/infra/                 @urruegg_microsoft

# Future repository-owned data definitions; no data folder is created
/data/                  @urruegg @urruegg_microsoft

# Repository governance
/.github/               @urruegg @urruegg_microsoft
/AGENTS.md              @urruegg @urruegg_microsoft
```

- [ ] Verify GitHub's CODEOWNERS errors display/API and base-branch behaviour.
      `/docs/` covers all requested children. Last matching line wins; owners
      are not accumulated from multiple matching lines.
- [ ] Verify actual review settings separately. Two listed owners do not
      require two approvals; draft PRs do not automatically request owner review.
      Do not claim enabled rulesets/approvals from a local configuration file.

No ownership transfer of `/infra/` is inferred. Any later transfer needs a
separate explicit human decision.

## H2: protected session-start routing (person only)

Prerequisite: authoritative new docs/catalogues and accepted routing prose are
available. The person edits `.github/hooks/scripts/session_start.py`, replacing
only the old route phrase in its `ctx` construction:

```python
"Work from a real issue and linked idea/spec/plan/sprint package; "
"new records use docs/idea/, docs/spec/, docs/plan/ and docs/sprint/; "
"legacy docs/plans/ remains historical; test first; "
```

Keep all existing quality-gate, human-only and Superpowers context. Do not
relax `guard.py`, change event schemas, add agent exceptions or grant bypass.

- [ ] Add/update the human-owned routing test in
      `tests/unit/test_guard_hook.py` so the session context includes each
      singular directory and still includes `AGENTS.md`, the quality command
      and the human-only boundary.

Merge the imports into the existing import block and add this test class:

```python
import contextlib
import io
import json
import unittest
from pathlib import Path
from tests.unit._util import load

class IntakeContextRouting(unittest.TestCase):
    def test_context_retains_controls_and_names_all_work_package_paths(self):
        session = load(str(Path(".github") / "hooks" / "scripts" / "session_start.py"))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(session.main([]), 0)
        context = json.loads(output.getvalue())["additionalContext"]
        for expected in ("docs/idea/", "docs/spec/", "docs/plan/", "docs/sprint/",
                         "AGENTS.md", "python tools/dev.py check", "Human-only"):
            self.assertIn(expected, context)
```

- [ ] Confirm ordinary new document paths are allowed by the existing guard;
      protected files/actions remain denied. No guard regex change is needed
      merely because a new documentation directory exists.
- [ ] Run:

```powershell
python -m pytest tests\unit\test_guard_hook.py -q
python tools\dev.py precommit --strict
python tools\dev.py check --strict
```

Expected: existing denials pass unchanged, routing reflects the agreed work
package and full strict gates pass. This person-owned PR is separate from the
agent's prose/renderer PRs.

## H3: real approval and activation records (person only)

- [ ] Record design and separate plan approval and required readiness labels
      against real issues. Do not backdate them or label implementation complete
      merely because this plan exists.
- [ ] Review Proposed policies and record actual acceptance before changing
      their state to active. Verify effective repository controls separately.
- [ ] Review/merge the relevant PRs through normal governance. No agent approves
      or merges its own work or configures protection to make CI pass.
- [ ] Link actual invitation/access, CODEOWNERS, routing PR and approval evidence
      from #8 and SPRINT-001. Keep any prevented/missing action explicitly open.
- [ ] Releases, tags, publication and deployment remain separate human decisions;
      this plan is not authority to execute them.

## H4: manual accessibility acceptance (person only)

Prerequisite: renderer automation and the scoped PR screenshots/evidence exist.

- [ ] In current Edge test the fourteen views and important dialog/tab/workflow
      states at 200% and 400% browser zoom. Check reading order, visible focus,
      reachability and no page-level horizontal overflow; distinguish real 2D
      diagram scrolling from broken page reflow.
- [ ] With Narrator or another screen reader verify landmarks, dialog title/
      modal boundary, tab selection, filter states, SVG nodes, form labels,
      announcements and Escape/focus return.
- [ ] Test real Windows high-contrast settings, not only media emulation, and
      check icons/controls/text are legible without colour-only meaning.
- [ ] Test voice input or record why that acceptance is still outstanding.
      Include testers with assistive needs when available.
- [ ] Record browser/OS/AT versions, scenario, expected/actual result, reviewer,
      date and any open finding in the accessibility issue/sprint.

Automated axe results do not prove these checks or full WCAG certification.
Identity-catalogue best-practice headers remain separately tracked until the
guarded product-output change is explicitly approved. Do not mask them in the
showcase or rewrite historical profile hashes.
