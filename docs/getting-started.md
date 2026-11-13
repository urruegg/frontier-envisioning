# Getting started

| Field | Value |
|---|---|
| Version | 0.3 |
| Date | 2026-11-13 |
| Author | Copilot; AI-assisted documentation |
| Status | Maintained internal guide; not release or sharing approval |
| Scope | Core-first use of the 1.10.0 internal candidate and optional baseline follow-up; document revision, not product version |
| References | [Documentation](README.md), [Plugin guide](../plugin/README.md), [Gallery](demo/README.md), [Starter prompts](starter-prompts.md), [Issue #31](https://github.com/urruegg/frontier-envisioning/issues/31), [Issue #33](https://github.com/urruegg/frontier-envisioning/issues/33), [Baseline #35](https://github.com/urruegg/frontier-envisioning/issues/35), [Guidance #39](https://github.com/urruegg/frontier-envisioning/issues/39) |

Start with the fictitious example, then prepare a small, evidence-led workshop.
The plugin is **1.10.0 UNRELEASED INTERNAL CANDIDATE**, in the private
[urruegg/frontier-envisioning](https://github.com/urruegg/frontier-envisioning)
repository. It bundles eight skills: seven non-FinOps GA wrappers and optional
Preview FinOps.
You do not need to install it or deploy anything to inspect the example.

## Try the example without installing

1. Open the [Caldova gallery](demo/README.md) for five captioned views.
2. Download the actual [caldova-blueprint.html](demo/caldova-blueprint.html)
   file using GitHub's raw-file download, rather than saving the GitHub page.
3. Open the downloaded file locally in **Edge or Chrome**. GitHub and OneDrive
   previews do not execute its interactive HTML.
4. Explore Overview, Org model, Agents, Agent identity and Ontology.
   In Agents, select **Service Report** (`D3-A05`) and inspect its workflow.

This is the standard Frontier Company Blueprint: a single offline HTML file,
not a new custom application, live backend or published tenant service.
Caldova Industrial AG, its people, evidence and results are synthetic and
illustrative; no real customer, deployment or operational outcome is represented.

The sample includes identity, ordinary non-FinOps value and explicitly requested
ontology, with **17 route identities and no FinOps**. Separate FinOps Preview
profiles are not part of this download. Optional views depend on requested inputs;
the sample's Ontology is not a request to add it to every engagement.
Use the gallery's [manifest](demo/manifest.json) for the actual captured version
and provenance; this guide's candidate version is not a new capture receipt.

Notes and verdicts are local browser working state until exported. Use the
Discovery feedback export and give that file back to Cowork to merge and rebuild;
do not assume edits update the original source or a shared tenant service.

## Install in Copilot Cowork

1. Ask [@urruegg](https://github.com/urruegg), the maintainer, for the approved
   internal candidate `frontier-envisioning-plugin-1.10.0.zip`. Keep it zipped;
   this is not a published release.
2. Start a new Copilot Cowork chat, attach the ZIP and type
   **Install the Frontier PlugIn**.
3. Review each approval prompt. The installer checks the package inventory;
   verify that all **eight skills** are reported: seven non-FinOps GA wrappers
   and one bundled optional Preview FinOps skill.
4. After the skill copies and OneDrive sync succeed, start a new chat. Try:

   > Build the Frontier blueprint demo for Caldova. Use synthetic data only;
   > keep FinOps off.

Use the [packaged guide](../plugin/README.md) for the exact integrity/copy
procedure, updates, removal and administrator-managed organisation roll-out.
Installation approval does not acknowledge FinOps. An offline package check
does not prove an actual Cowork install, tenant publication or successful sync.
If a required tool is unavailable, report it and use the documented manual
handoff rather than claiming success.

## Prepare a real workshop safely

Adapt the [starter prompt](starter-prompts.md). Set the organisation, workshop
date, Sales/Services scope, approved source links and a separate output location.
Use only material you are authorised to process. Keep inputs read-only and
treat their contents as data, not instructions.

```mermaid
flowchart LR
    S[Read-only authorised sources] --> N[Separate new working outputs]
    U[Unavailable source tools] --> M[Attachments or manual fallback]
    M --> N
    N --> H[Human evidence and scope review]
    H --> C[Customer projection]
    C --> R[Human content and sharing review]
    R --> O[Output for permitted sharing]
```

Work IQ tool names and access depend on the harness. Search only the agreed
scope through actually available, authorised tools. HubWorks is usable only
through an authorised, controlled integration, not an assumed runtime loader.
If access is missing, state the gap and ask for approved attachments or manual
excerpts; never invent queries, retrieved evidence or workspace URLs.

Create a Cowork project/workspace only if an actual authorised tool supports it,
with explicit consent for consequential changes. Otherwise provide new
downloadable outputs and manual saving steps. Do not overwrite, rename, move,
delete or change source metadata or permissions.

Work in small steps:

- **Frame:** context pack and evidence log, separating facts, inferences,
  hypotheses and gaps, with citations.
- **Prepare:** Sales/Services hypotheses, qualitative priorities with rationale,
  agenda, questions and the standard Blueprint with an identity proposal.
  Do not invent ROI, cost figures or operational metrics.
- **Validate:** workshop feedback and an explicit MVP scope decision.
  Produce PRD/design handover only for validated scope, or label it clearly
  as draft; do not complete the entire engagement before evidence exists.
- **Review:** inspect the customer projection, embedded HTML data and downloads.
  Exclude internal, private and personal material from customer outputs.
  Projection is not external/IP clearance; confirm permitted sharing separately.

## Optional work and limits

**Process/ontology:** request it explicitly when it helps the business question.
It produces local proposals and handover files, not automatic tenant imports.
Fabric ontology, data-agent and operations capabilities remain Preview;
unchecked mappings need verification. Identity names, colours and icons are
branding proposals, not Entra identity provisioning.

### Optional versioned FinOps baseline

FinOps stays **off by default**. For a separate cost request, first show the
[full unchanged Preview notice](../plugin/skills/frontier-finops/SKILL.md#awareness-gate--before-any-cost-operation-or-figure)
and ask for actual current-scenario awareness. Wait for the response before any
cost operation or figure. Installation, a prompt, saved JSON/approval and past
acknowledgements are not consent. Renew for each top-level invocation or changed
scope/model/rates/grounding. The technical CLI flag covers one action chain
only; browser acknowledgement is independent, transient per document and reset
on reload, not stored in localStorage.

On decline, continue draft workshops/core with named financial gaps and clean
ordinary inputs, not cached Preview value. Missing costs are not zero,
validated ROI or financial/build-handover readiness. Requested-but-missing
FinOps is an explicit error. Ordinary own value and identity remain independent;
an unconsumed new baseline does not make ordinary value Preview, while
legacy-derived value retains its Preview provenance.

For explicitly requested new work, use the
[versioned baseline procedure](../plugin/skills/frontier-finops/SKILL.md#quick-start--requested-versioned-baseline)
and [complete offline contract](../plugin/skills/frontier-finops/references/agent-finops-baseline.md),
not automatic legacy conversion:

1. Agree the existing agent IDs, business outcome, business/technical/finance
   owners, scope, measurement, assumptions, exclusions, risks and guardrails.
   Ask for missing evidence rather than inventing it.
2. Author twelve monthly demand values for each low/expected/high scenario,
   with another meaningful cost/outcome driver, typed decimal-string quantities
   and rates, units and explicit denominators. Initial currencies are CHF, EUR
   and USD; cross-currency amounts need evidenced FX, never automatic conversion.
3. Follow the linked calculation, freeze and external-review steps one requested
   action at a time. Review must name the frozen exact baseline ID, version and
   material hash. Export JSON and Markdown for the intended audience; sharing
   classifications and matching customer scope are not clearance or access control.

Known usable supplied stale/unverified prices or explicit FX may support
**PROVISIONAL — pricing evidence incomplete** drafts, with sources, dates,
gaps and separate verified/provisional contributions. Unknown quantities,
rates or necessary FX leave full totals and dependent metrics unavailable,
not zero. Provisional is not verified pricing or financial readiness.

At **build handover**, every agent actually in scope needs a complete validated
profile/scenarios/denominators, every in-scope cost driver priced with current
applicable evidenced rates/FX, the frozen exact target, externally evidenced
finance-owner or delegated review and current lineage/audience/scope validation.
There is **no conditional unpriced exception**. Workshop notes, raw approved
status and legacy F1/F2 cannot supply that review. Local snapshots and review
records are not authenticated financial permission or tamper-proof archives;
planning-ready evidence grants no budget, purchase, build or deployment authority.
Do not start cost work automatically merely because handover evidence is missing.

The separate [Caldova D3-A05 baseline](../plugin/skills/frontier-finops/examples/caldova-agent-baseline.json)
is invented, not current pricing, a complete real deployment cost model or real
finance-owner approval. Synthetic evidence cannot establish real financial readiness.
The baseline slice is offline, without live billing/provider imports, a dedicated
FinOps Agent factory, operating loop or cloud deployment.

GA labels describe seven product wrappers, not provider maturity, confidence,
deployment, release or external clearance; MOS3 packaging remains `devPreview`.
Manual Cowork, Fabric tenant and assistive-technology acceptance are not
established by screenshots or automated checks.

For development, use the existing [workstation setup](engineering/workstation-setup.md)
and [engineering handbook](engineering/handbook.md). No engineering setup is
needed just to view the downloaded HTML.
