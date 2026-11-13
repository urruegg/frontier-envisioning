# Caldova gallery extension design

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-13 |
| Author | Copilot SDK in VS Code; AI-assisted design |
| Status | Written spec and plan/readiness approved; local implementation verified, PR/CI separate |
| Scope | Ten reproducible core-gallery captures and existing HTML navigation |
| References | [Catalogue](README.md), [Issue #41](https://github.com/urruegg/frontier-envisioning/issues/41), [Idea](../ideas/2026-11-13-caldova-gallery-extension.md), [Plan](../plans/2026-11-13-caldova-gallery-extension-plan.md), [SPRINT-008](../sprints/SPRINT-008-caldova-gallery-extension.md), [Gallery](../demo/README.md) |

## 1. Outcome and actual choice

Expand **Caldova Blueprint gallery** from five to ten captioned screenshots
of the same interactive offline core HTML. Accountable human owner: `@urruegg`.
The 13 November conversation choice **`approve-ten-captures`** approved this
scope over links-only documentation. The separate
**`approve-written-gallery-spec`** response approves the written spec at
`4ef63d110a72dc9a301496317e2e5ef1311becee`. The later
**`approve-inline-gallery`** response approved the linked plan/readiness at
`8be6aa815ca54878bd6d7e95f454c9b2e3364d80` and selected inline execution
before implementation. No ready/approved labels are inferred.

The base is human-merged PR #40, commit `9115ccc8`. Product version remains
the unreleased internal candidate 1.10.0. No plugin runtime changes are needed.

## 2. Gallery content

Retain Overview, Org model, Agents, Agent identity and Ontology. Add:

| Capture | Existing HTML route | Required visible state |
|---|---|---|
| `landing-zone.png` | `#/architecture` | Landing zone tab selected; landing-zone diagram rendered |
| `architecture-layers.png` | `#/architecture` | Layers and integrations tab selected; layered architecture rendered |
| `discovery.png` | `#/discovery` | Discovery questions and feedback controls |
| `risks.png` | `#/risks` | Risks, assumptions and open decisions |
| `evidence.png` | `#/evidence` | Evidence behind the blueprint |

Group the two architecture captures under Target architecture and the three
workshop captures under Workshop, with the requested titles as subsections.
Each has meaningful alt text, a short explanation and an existing HTML route
link. Explain that readers must download/open the HTML locally; GitHub and
OneDrive previews do not execute it.

Both architecture tabs share one route. The Layers caption must tell readers
to select **Layers and integrations** after opening Target architecture;
do not claim a tab-specific deep link exists. Document proposal boundaries:
architecture is not a deployed landing zone/integration, workshop notes need
export/merge, and synthetic evidence is not an actual engagement record.

## 3. Capture and manifest contract

Extend `tools/capture_docs.mjs` and `tools/build_docs_demo.py`, not renderer
sources or hand-edited generated assets. Retain the current 1440 × 1000 light
viewport, reduced motion, en-GB, UTC, fresh storage and network refusal.
These are selected viewport samples, not full-page or accessibility coverage.

For each new view, wait for the intended route and substantive content.
Explicitly select the architecture tab through its accessible control, verify
its selected state and visible panel, then capture. An error, missing content
or unexpected network request fails generation instead of producing a
success-shaped image.

Keep all ten image identities/routes in the manifest. Add explicit selected-tab
metadata for both architecture images and validate it, since their routes alone
cannot distinguish the content. Retain actual PNG dimensions/hash checking,
HTML/source fingerprinting and browser/tool settings. Missing, duplicate,
unexpected or wrong-tab records fail validation before replacing previous
tracked outputs. Capture browser assertions establish the actual selected
state; metadata/hash checks alone do not authenticate image content.

## 4. Direct dependencies and exclusions

Update the active gallery/count references in the root reader guide,
getting-started guide and documentation catalogue. Update the existing focused
generator tests and any directly affected capture-count assertions.
Preserve historical five-image sprint/release claims as dated evidence.

Regenerate HTML, all ten PNGs and the manifest through the existing generator;
visually inspect the five new captures. Do not copy images from external
sources, generate mock screenshots or alter the synthetic Blueprint data.
Core-only/no-FinOps checks and previous-output preservation remain unchanged.

No plugin edits/version bump, new navigation routes, new standalone HTML
variants, architectural product decision, cloud resources, deployment,
publication or protected guardrail changes are included. Continue the
Microsoft icon terms and private/internal-sharing limits.

## 5. Acceptance and verification

| ID | Testable acceptance |
|---|---|
| G41-01 | The gallery retains five original views and adds exactly the five requested captures with captions, alt text and correct HTML navigation instructions. |
| G41-02 | Actual architecture screenshots show their distinct selected tabs/panels; workshop screenshots show Discovery, Risks and Evidence, with no network or console errors. |
| G41-03 | Manifest validation requires exactly ten unique expected records and correct architecture-tab metadata, and preserves existing outputs on failed generation/validation. |
| G41-04 | All actual image hashes/dimensions, source fingerprint and fresh core HTML comparison pass; default HTML remains core-only with no FinOps. |
| G41-05 | Changed tooling is test-first; focused tests and strict docs pass; `python tools/dev.py check` ends `ALL GATES PASSED` and its actual summary is pasted into the follow-up draft PR. |

Use the existing unit tests for capture/manifest failures before changing
tooling. Run the real Playwright capture generator, inspect the new images,
and validate the manifest against the freshly built core. No browser mock
counts as screenshot evidence. All results, actual approval evidence and the
final source head belong in the linked sprint record and draft PR.
