# Seed backlog

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained intake catalogue; approval not inferred |
| Scope | Seed backlog routing; document revision, not product version |
| References | [Documentation](../docs/README.md), [Intake record](../docs/engineering/intake-plan.md), [Product release plan](../docs/prd.md#a12-release-plan) |

`backlog.json` holds the labels and milestones, `issues/*.md` the seed issues (frontmatter: id, title, milestone, labels; body: context, acceptance criteria, source). `python tools/bootstrap_github.py --owner <owner> --apply` creates them on GitHub (issue titles start with the id, so the script skips existing ones). After the bootstrap, GitHub issues are the source of truth; this folder stays as the record of the intake.

| Milestone | Content |
|---|---|
| M0 · Intake baseline | INT-01 to INT-08, INT-11, INT-12, INT-14, INT-15, ENG-D1, ENG-D3, ENG-D4 |
| 1.7.0 · Operate loop and HubWorks | HubWorks epic with F-01 to F-06 and F-08, operate loop (OPS-01, OPS-02), E-02, E-05, L10N-01, TD-03, PROTO-01, INT-09, INT-10, D-05, D-07, D-08 |
| 1.8.0 · FOCUS and shared engagement data | F-07, FOCUS-01, TD-01, D-03 |
| Later | E-01, BUILD-01 (ready-for-build handover with IaC), INT-13, TD-02, REG-01, TD-05 |
| No milestone | D-01, D-02, D-04, D-06 |
