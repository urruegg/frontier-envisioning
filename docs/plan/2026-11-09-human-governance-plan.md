# Human Governance and Acceptance Implementation Plan

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; human handoff preparation; AI-assisted maintenance |
| Status | Final human sign-off recorded on #8; sole-public-cloud-account refinement directed by the user; protected execution remains human-only |
| Scope | DG-06, protected intake routing and manual accessibility acceptance |
| References | [Plan catalogue](README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/8), [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md), [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [Sprint](../sprint/SPRINT-001-docs-governance-and-accessibility.md), [Master](2026-11-09-docs-governance-implementation.md) |

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

## Account and acceptance refinement (2026-11-10)

The user clarified that `@urruegg_microsoft` is their enterprise-only GitHub
account, whereas `@urruegg` is their account for this repository on GitHub's
public-cloud platform. The repository is private and single-user.
This explicit decision supersedes the earlier second-contributor invitation,
shared ownership and infrastructure-owner exception. No second account is
required or to be invited for review.

The user's [final governance/manual-accessibility sign-off](https://github.com/urruegg/frontier-envisioning/issues/8#issuecomment-6768225688)
is recorded. It does not prove execution of protected changes or supply
scenario-level AT evidence that was not provided.

For the scoped documentation refinement under the existing #8 work package:

1. Update active account/review guidance and the linked spec/sprint.
2. Keep historical intake/release evidence and bootstrap test fixtures intact.
3. Validate documentation contracts and the required repository gate; open a
   documentation-only PR with actual results and the human-applied target below.
4. Leave CODEOWNERS, hooks, labels, permissions, settings and merge to the user.

## H1: sole public-cloud ownership (person only)

- [x] User decision: use `@urruegg` only; no enterprise-account invitation or
      collaborator-eligibility exercise is part of this repository's plan.
- [ ] Verify the repository remains private `urruegg/frontier-envisioning`
      and the actual owner account has the needed repository access.
- [ ] The person replaces the protected CODEOWNERS content with this minimal
      all-path ownership rule, removing the imported enterprise-account rules:

```text
# Sole public-cloud maintainer; every path, including infrastructure/governance
*                       @urruegg
```

- [ ] Verify GitHub's CODEOWNERS errors display/API and base-branch behaviour.
      The default covers all requested docs, product, infrastructure, data and
      governance paths. Any retained later rule must also use only `@urruegg`,
      because last matching rules override the default.
- [ ] Verify actual review settings separately against the
      [sole-maintainer model](../engineering/github-setup.md#4-sole-maintainer-review-and-merge).
      Ownership does not grant self-approval rights. Draft PRs do not request
      owner review automatically. No server setting is inferred from this plan.

The infrastructure entry is intentionally corrected to the same person's
eligible public-cloud account, not left on the ineligible enterprise account.
No permission, protected-file edit or settings change is performed by an agent.

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
            self.assertEqual(session.main(), 0)
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

- [x] The user's final governance/manual-accessibility sign-off is recorded
      on #8; no further approval request is needed for that decision.
- [ ] Record design and separate plan approval and required readiness labels
      against real issues. Do not backdate them or label implementation complete
      merely because this plan exists.
- [ ] Review Proposed policies and record actual acceptance before changing
      their state to active. Verify effective repository controls separately.
- [ ] The maintainer reviews the current PR head and passing L1/L2/IaC checks,
      records explicit sign-off and performs the human merge when permitted.
      GitHub does not allow formal self-approval of an authored PR or approval
      of a Copilot PR assigned by that user. Agent review is advisory, not
      independent human approval. An unmet server requirement needs a human
      governance decision, never an agent bypass or invented review.
- [ ] Link actual owner-access verification, CODEOWNERS/routing PR and sign-off
      evidence from #8 and SPRINT-001. The enterprise invitation is no longer
      applicable. Keep actual unperformed operations explicitly open.
- [ ] Releases, tags, publication and deployment remain separate human decisions;
      this plan is not authority to execute them.

## H4: manual accessibility acceptance (person only)

Prerequisite: renderer automation and the scoped PR screenshots/evidence exist.

- [x] Final acceptance sign-off received from the user on 10 November 2026.
      The following scenario records remain separate evidence requirements;
      no tool/OS version or performed test is invented from the sign-off.
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
