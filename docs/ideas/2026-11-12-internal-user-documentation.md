# Internal user documentation and Caldova showcase

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted intake |
| Status | Maintainer directed implementation in conversation; label state not inferred |
| Scope | Internal reader journey, generated sample, five screenshots and starter prompt |
| References | [Catalogue](README.md), [Issue #31](https://github.com/urruegg/frontier-envisioning/issues/31), [Design](../specs/2026-11-12-internal-user-documentation-design.md), [Plan](../plans/2026-11-12-internal-user-documentation-plan.md), [SPRINT-005](../sprints/SPRINT-005-internal-user-documentation.md) |

## Outcome

An internal reader can understand, install and try the plugin, inspect a real
fictitious Caldova outcome and start an evidence-led engagement without reading
the repository's migration history first.

The maintainer requested this on 12 November, including Mermaid diagrams, the
Caldova HTML, Playwright images of Overview, Org model, Agents, Agent identity
and Ontology, and adaptation of a supplied workshop-preparation prompt.

## Decision evidence and boundaries

The recommended design was presented in conversation. The maintainer then
explicitly directed: "stop planning and start implementing" and "Keep working
autonomously until the task is truly finished". This authorises execution of
that proposed scope without another approval round; it is not a claim that the
subsequently written plan was separately reviewed or that protected labels
were changed.

Remove local-intake narrative from reader-facing entry points. Preserve
historical receipts, manifests, tests and commit-qualified evidence in place.
No visibility change, external clearance, release, deployment or new plugin
runtime capability is part of this work. Protected #8/#30 remain human-owned.

## Prompt assessment

Retain business-first Sales/Services framing, read-only sources, source-backed
facts versus hypotheses, synthetic demonstrations and separate new outputs.
Replace engagement-specific document identifiers with inputs. Do not promise
HubWorks loading, universal Work IQ access, custom application generation or
Cowork project APIs. Explain authorised-tool checks and manual fallback.
Use the standard Blueprint, optional requested ontology and FinOps off by
default; a cost request still needs its separate Preview-awareness procedure.
