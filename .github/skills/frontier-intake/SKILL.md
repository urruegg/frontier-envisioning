---
name: frontier-intake
description: Turn a request or backlog issue for Frontier Envisioning into a ready work item - Definition of Ready, decisions, spec and plan locations, labels and milestones. Use when asked to triage or refine an issue, check whether work is ready, create follow-up issues, or start work on a new feature or epic.
---
# From request to ready

1. **Classify**: `type:feature | bug | chore | docs | decision | spike | epic`, one or more `area:*`, `priority:P1-P3`, `size:S|M|L` (split anything larger than M before starting). Use the milestone of the release it belongs to (`docs/prd-and-solution-design.md` A.12).
2. **Definition of Ready** (all true, then a person sets `status:ready`):
   - problem and outcome stated in user terms; acceptance criteria testable;
   - blocking decisions resolved (`type:decision` issues, PRD A.13 D-xx, engineering ENG-Dx);
   - affected skills, scripts, views or workflows named;
   - customer-neutral sample data available (Caldova);
   - plugin version impact known (bump needed?).
3. **Decisions** get their own issue (`type:decision`, `human-only`) with options, a recommendation and an owner; the outcome becomes an ADR in `docs/adr/` or an entry in the PRD.
4. **Spec and plan** follow the method in `AGENTS.md` section 3: `docs/plans/YYYY-MM-DD-<topic>-design.md`, then `...-plan.md`. Big changes need `approved:design` (set by a person) before the build starts.
5. **Copilot cloud agent**: label `agent:copilot` only when the plan exists and the work needs no human-only step; assign the issue to Copilot with the plan linked.
6. Never write real customer names into issues; refer to engagements by their CE Hub number only if the repository is private and the decision ENG-D1 allows it.
