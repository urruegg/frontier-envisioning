# Internal user documentation design

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted design |
| Status | Recommended scope authorised for execution in conversation |
| Scope | Reader documentation and reproducible, offline Caldova showcase |
| References | [Catalogue](README.md), [Issue #31](https://github.com/urruegg/frontier-envisioning/issues/31), [Idea and decision](../ideas/2026-11-12-internal-user-documentation.md), [Plan](../plans/2026-11-12-internal-user-documentation-plan.md), [SPRINT-005](../sprints/SPRINT-005-internal-user-documentation.md) |

## Design

Use the existing plugin and core demo, not a new app or documentation service.
The root README explains outcomes, entry points and current maturity. A short
getting-started guide explains install, evidence-led preparation and review.
Two Mermaid diagrams show the engagement flow and source/output boundaries.
The documentation catalogue separates using the plugin from engineering and
historical evidence.

`docs/demo/caldova-blueprint.html` is generated from the existing core demo,
with identity, ordinary value and requested ontology, without FinOps.
GitHub does not execute this HTML: download/open locally in Edge or Chrome.
It is a fictitious example, not proof of a real engagement, tenant import,
deployment, actual Cowork installation or universal output quality.

Five real Chromium/Playwright images under `docs/images/caldova/` show Overview,
Org model, the Service Report agent canvas/workflow, Agent identity and
Ontology. Captures use a fixed viewport, light scheme, reduced motion, locale
and timezone with fresh browser storage. Record browser/tool versions and
hashes. Do not assert cross-platform PNG byte determinism or fake captures.

One Python tool orchestrates core build, temporary capture, validation and
publication of the named assets. One Node script uses the installed Playwright
package to open the actual offline file and capture the five routes. No new
dependency, service, network lookup or deployment is needed.

The generated manifest binds the sample and screenshot bytes to the current
demo-relevant sources. A check compares the stored HTML with a freshly built
core demo, normalising only the documented volatile `meta.generated` date.
Never suppress substantive differences. Strict L1 runs that check after the
core demo build; focused tests exercise corruption and stale-source refusal.

## Starter prompt

Provide a short parameterised prompt and a separate fictitious Caldova example.
The prompt requests the standard Blueprint, evidence log, Sales/Services
hypotheses, qualitative prioritisation, workshop agenda and clear gaps. It
permits only new outputs in an approved workspace; reference sources remain
read-only. Connected tools and project storage must actually exist and succeed.
Missing tools are reported with attached-material/manual alternatives.
Do not invent metrics, sources, branding rights, workspace links or ROI.
Ontology is optional when requested; FinOps is excluded unless separately
requested and acknowledged through the existing Preview procedure.

## Acceptance

| ID | Testable outcome |
|---|---|
| DOC-01 | README and user guide remove migration/local-intake presentation and stale delivery-pending claims; archival evidence remains intact |
| DOC-02 | Mermaid explains actual workflow and read-only input/new-output boundaries without unsupported execution claims |
| DOC-03 | Tracked self-contained core HTML opens offline with all five requested routes and no automatic FinOps data |
| DOC-04 | Exactly five real labelled screenshots, fixed capture settings and source/version/hash provenance accompany the sample |
| DOC-05 | Regeneration and drift checks reject changed sources, HTML or PNG bytes, malformed manifests and partial capture failure |
| DOC-06 | Starter prompt preserves source integrity, conditional tool access, factual limits, manual storage fallback and FinOps boundaries |
| DOC-07 | Existing historical product/hash contracts, privacy checks and protected paths remain unchanged |
| DOC-08 | Strict L1, relevant browser tests and internal distribution validation pass; draft PR includes exact evidence |

## Version and sharing boundary

1.9.1 is still unreleased; no new version or raster profile is needed. Updating
the packaged user README requires ordinary package/inventory regeneration, not
hand editing. A successful internal technical check does not change repository
visibility or establish external/IP clearance. Retain Microsoft icon notices.
