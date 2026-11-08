# ADR-0022: Deterministic guardrails for agents and customer neutrality

**Status:** Proposed (8 November 2026)

## Context
Instructions guide agents but are not a permission boundary. The repository must never contain real customer names, and agents must not merge, release, deploy or weaken the guardrails.

## Decision
A `preToolUse` hook (`.github/hooks/scripts/guard.py`) denies human-only actions, edits to protected and generated files, and new content containing a denylisted customer term, with a reason the agent can act on. A `sessionStart` hook injects the working agreement. Customer terms are stored as salted SHA-256 hashes of normalised one- or two-word terms (`tools/neutrality-denylist.txt`), so the list does not disclose which customers the Hub works with; extra terms can come from an environment variable. The same scanner runs in L0, L1 and on every archive.

## Consequences
Agents fail early and visibly; people remain the authority through rulesets, code owners and environment approvals. Hashes of short names can be guessed with a dictionary, so the repository stays private (ENG-D1).

## Alternatives considered
Plain-text denylist (discloses customers); instructions only (not enforceable); a secret-only denylist (not available to local and agent hooks).
