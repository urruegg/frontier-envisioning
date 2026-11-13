---
name: frontier-envisioning
description: |
  Runs a Frontier envisioning engagement end to end: cited discovery, blueprint, workshop,
  value, identity and design. Offers process ontology when requested; FinOps is optional
  Preview, never automatic. Use for "prepare the Frontier envisioning for <customer>",
  "run the envisioning prep end to end" or "what is next in the <customer> envisioning".
  Do NOT use for a single step: route context to frontier-context-discovery, HTML to
  frontier-blueprint, PRD/architecture to frontier-solution-design, names/icons to
  frontier-agent-identity, value to frontier-value-case, ontology to frontier-process,
  or cost questions to frontier-finops for its Preview notice and confirmation first.
license: MIT
metadata:
  category: productivity
  icon: Rocket
  version: "1.10.0"
  plugin: frontier-envisioning
  maturity: ga
  optional: false
  requires_preview_ack: false
---

# Frontier solution envisioning (end to end)

*AI-assisted procedure maintenance, 13 November 2026; original authorship retained.*

The Innovation Hub method for helping a customer see itself as a Frontier company: **human-led, agent-operated**. It coordinates the skills over an engagement and keeps every artefact tied to evidence:

1. **Discover** with **frontier-context-discovery**: Work IQ (meetings, transcripts, mail, chats, files) and public sources become a cited context pack.
2. **Hypothesise** with **frontier-blueprint** in four parts. Vision: Overview with Microsoft's digital feedback loop, Org model, Blueprint, Journeys (including Agent Factory), Use cases and PRD. Design: Agents, Agent identity, Target architecture and IT readiness, plus Ontology when requested. Build: Roadmap and Plan; FinOps only as acknowledged Preview. Workshops: Attendees, Discovery, Risks and Evidence.
3. **Validate** in the workshop: the blueprint is presented and corrected live; notes and verdicts are exported and merged.
4. **Design** with **frontier-solution-design**: scaffold the agreed MVP PRD from the same canonical Python model as the page, then solution design and ADRs grounded in Microsoft's Frontier architecture guidance.

The full method, phases, gates and timings are in [references/method.md](references/method.md); the organisation model in [references/hairo-model.md](references/hairo-model.md).

Eight skills are bundled: seven non-FinOps GA product wrappers and optional
Preview FinOps. GA is the maintainer's designation, not result confidence,
provider GA, release/deployment or public/IP clearance. Fabric ontology/agent/
operations Preview and unverified mappings remain explicit.
**1.10.0 is an unreleased internal candidate.** Agent identity branding is not
Entra identity provisioning; HubWorks is controlled source integration, not
an assumed runtime loader.

## Quick Start

```
User: "Prepare the Frontier envisioning for Caldova, workshop on 12 November"
1. Locate the engagement folder (none) -> phase Discover
2. frontier-context-discovery: ListCalendarView + GetMeetingTranscript + SearchM365 -> customer-context.json
3. frontier-blueprint: seed, write the hypothesis, build with the identity kit -> Caldova Frontier Company Blueprint.html + agent identity package (proposal)
3b. frontier-value-case: value case from ordinary evidence/assumptions, without FinOps (gate V1); missing cost/budget evidence stays open
3c. If requested, frontier-process: process ontology and local design/import files (Fabric Preview caveats retained)
3d. Only if cost work is requested: show frontier-finops' full Preview notice and obtain actual current-scenario confirmation, then follow its versioned baseline Quick Start for new work; otherwise skip with named financial gaps
4. Prepare: customer version, agenda, ten key questions
5. Save the engagement folder; reply with phase, gates and next actions in a short table
```

## When to Use

- "Prepare the Frontier envisioning for Caldova" (nothing exists yet)
- "Run the envisioning prep end to end for Caldova procurement, workshop on 12 November"
- "What is next in the Caldova envisioning?" (pick up an engagement folder and continue)
- "Take the Caldova workshop transcript and finish the design"

## When NOT to Use

- Business value of the agents only: use frontier-value-case instead.
- Agent costs, credits or guardrails only: load frontier-finops to explain Preview and obtain confirmation before cost work.
- Process ontology only: use frontier-process instead.
- Only gathering or refreshing context: use frontier-context-discovery instead
- Only building, updating or customer-proofing the blueprint HTML: use frontier-blueprint instead
- Only the PRD, solution design or ADRs: use frontier-solution-design instead
- A general question about Microsoft's agent architecture with no customer: answer directly
- Scheduling the workshop or sending invitations: calendar skills

## Workflow

### Step 1: Locate or start the engagement
1. Resolve the customer, scope (company or function), workshop date and the user (`GetMyDetails`).
2. Look for an engagement folder: OneDrive `Documents/Cowork/frontier-envisioning/<slug>/`, then `input/`. Read `engagement.json` if present (phase, versions, file list).
3. Decide the phase from what exists:

| Exists | Phase | Next action |
|---|---|---|
| Nothing | Discover | Step 2 |
| Context pack only | Hypothesise | Step 3 |
| Blueprint, workshop not yet held | Prepare workshop | Step 4 |
| Feedback export or workshop transcript | Consolidate | Step 5 |
| Validated blueprint | Design | Step 6 |
| PRD for the MVP agents | Identity | Step 6b |
| Design drafted, architecture design workshop ahead | Architecture design | Step 6c |

Create tasks for the remaining phases so the user sees progress.

### Step 2: Discover
Load **frontier-context-discovery** and follow it: meetings and transcripts, mail, chats, files, public sources, then `customer-context.json` and the evidence log. Gate A: no validation errors; at least one transcript or the gap stated.

### Step 3: Hypothesise
Load **frontier-blueprint**: seed, write the hypothesis, build with the identity
kit (a proposal until Gate E). When evidence holds volumes and handling times,
add **frontier-value-case** (V1) with `--value value.json`, without FinOps.
Offer **frontier-process** when process/ontology work is requested; add
`--ontology ontology.json` and retain its mapping and Fabric Preview gaps.

FinOps is not required for draft workshops, ordinary value, identity, blueprint,
design or optional process work. Financial completeness becomes mandatory only
at build handover (Step 6c). A financial gap does not trigger a cost operation:
first follow [frontier-finops](../frontier-finops/SKILL.md), show its full
Preview notice and obtain actual confirmation for the current scenario before
any operation, cost recommendation or figure. Each new
top-level invocation or changed scope/model/rates/grounding needs renewed
acknowledgement; the wrapper forwards it only within one action chain.
Installation, an old JSON acknowledgement, notes, a calculation request, an
old approval/GA claim or yesterday's acknowledgement is not consent.
CLI acknowledgement is technical only, not financial permission.

#### Requested new baseline — optional offline path

Follow the [FinOps versioned Quick Start](../frontier-finops/SKILL.md#quick-start--requested-versioned-baseline)
and [offline baseline contract](../frontier-finops/references/agent-finops-baseline.md).
Link each baseline to an existing agent profile and model twelve monthly
demand values in each low/expected/high scenario, with another meaningful
cost/outcome dependency. Use decimal-string quantities/rates, explicit units,
denominators, reporting currency and evidenced FX where necessary. Unknown
inputs remain gaps, not defaults; supplied usable stale/unverified prices may
support explicitly provisional drafts, not financial handover.

Pass authoritative drafts or frozen snapshots and matching recorded reviews
to the existing Blueprint wrapper with
`--agent-finops <baseline-or-snapshot.json> --as-of YYYY-MM-DD --acknowledge-finops-preview`.
Repeat `--agent-finops` for additional explicit baselines and
`--agent-finops-review <recorded-review.json>` for each external review of a
supplied frozen target. Set `--audience internal` or `--audience customer`;
for customer-specific output add the matching `--customer-scope <scope>`.
Scope is not sharing clearance or access control. Reports, applied views and
cached DTOs are derivatives, not authoritative inputs or review evidence.

Independent ordinary value does not become Preview merely because a new,
unconsumed baseline is present. Do not feed new amounts automatically into
legacy CHF NPV/ROI; legacy-derived value remains Preview. The baseline slice
is offline: no dedicated FinOps Agent factory, operating loop, live billing/
provider imports, cloud deployment or identity provisioning.

#### Legacy costs — explicit separate path

For explicitly selected `frontier-finops/1.0` work, retain the legacy
`--finops finops.json --acknowledge-finops-preview` wrapper path after fresh
confirmation. Do not automatically choose it for new baseline work or mix
legacy and successor sources. Only [explicit migration](../frontier-finops/SKILL.md#explicit-migration-never-automatic-conversion)
creates a successor draft: preserve originals and provenance; unproved numeric
mappings remain context-only gaps. Inherit no approval, acknowledgement,
licence coverage or implicit legacy FX.

#### Declined or unavailable FinOps

On decline, skip FinOps and state the cost/budget gap. With the optional module
absent, continue the core without requesting it; a requested-but-missing module
is an explicit error, not success. Preserve old embedded Preview originals.
For a declined core path, use clean core inputs and ordinary non-FinOps value
assumptions, not a cached Preview-derived value model. There is no automatic
cleansing or `--no-finops` flag; do not strip provenance or relabel old costs GA.
Gate B still requires a clean build, MVP canvases/seven declarations and marked
internal evidence, not an automatically passed budget check. Assign actual
owners to financial gaps; continue drafts/core without claiming financial or
build-handover readiness.

### Step 4: Prepare the workshop
1. Build the customer version (`--audience customer`) if the file will be shown or shared outside Microsoft.
2. Draft the workshop agenda from [references/method.md](references/method.md) (section 4) with the customer's journeys and MVP candidates; offer it as a document or a meeting description.
3. List the ten discovery questions that matter most and who in the room can answer them.
4. Review the PRD hypothesis before architecture; use Risks to agree ratings,
   mitigations and owners. Attendees must cite contributions with sources and
   transcript times, not inferred participation. Plan supports handover planning.

### Step 5: Consolidate after the workshop
1. Get the feedback export(s) and the workshop transcript.
2. Run **frontier-context-discovery** on the transcript (new evidence ids), then **frontier-blueprint** step 5 (merge feedback, update hypothesis, update the attendees' contributions, rebuild). Gate C: MVPs confirmed by the customer, `meta.status` = validated.
3. Write the workshop summary: decisions, MVPs, owners, next steps (offer email or document).
4. Merge risk ratings/status/notes and `prd:scope` with the exported feedback.
   Keep the normalised source bindings and retired-ID history; discarding it
   cannot guarantee old ID-only feedback identity after a source edit.

### Step 6: Design
Load **frontier-solution-design** for the MVP agents. Gate D: PRD Definition of Ready either met or the missing items assigned.

Selecting fewer agents must retain canonical requirement IDs. Computed factory
readiness and WIP limits display planning state; they do not approve execution.
Plan CSV is a mapped handover format, not a live connector or native import certification.

### Step 6a: Value review and optional Preview cost handoff (V2, F2)
Merge ordinary value verdicts and rebuild without FinOps. V2 requires the five
most sensitive assumptions confirmed or adjusted by their real owners; missing
costs are not zero or validated ROI. If FinOps is requested, repeat its awareness
gate before feedback, recalculation or application. Legacy F1 checks model
completeness and F2 checks guardrail design with named owners; neither is the
successor's financial handover check, budget or purchase approval. Carry the Preview
notice, limitations, sources, rates/model versions and assumptions into any
cost-derived ROI/NPV, PRD/design, comparison and export. The budget owner retains
accountability. A fresh browser viewer acknowledgement is independent of CLI
acknowledgement, transient per document and reset on reload. It does not
authorise scripts, authenticate review or permit purchases.

### Step 6b: Agent identity approval (before the agents are built)
Load **frontier-agent-identity**: the blueprint already carries a proposal kit; collect the customer's own brand, review the names with the user (and the workshop's identity feedback), then rebuild the kit and the blueprint together. Gate E: validator 0 errors, unit tests passed, decisions N-1 to N-6 listed with owners.

### Step 6c: Architecture design workshop and IT readiness (gate R)
1. About ten working days before the architecture design workshop, send the preparation items (P-) from the blueprint's IT readiness page, or `design/it-readiness.md` from **frontier-solution-design**, to the customer's IT with owners and due stages.
2. In the workshop, walk the Target architecture: landing zone per journey (DEV, TEST, PROD; data classes), the ADRs, then the IT readiness decisions (D-01 engineering control plane first). Verdicts and statuses are captured live in the HTML and merged with **frontier-blueprint** step 5.
3. Move the MVP agents along the Agent Factory board: validated, then designed.
   Record which agent IDs are actually in the agreed build-handover scope.
   At build handover, mark an agent ready only when the handover checks,
   including the financial baseline check below, pass. Gate R requires the
   prototype readiness checks (R-), D-01 decided and the per-agent financial
   check for every agent in that scope; a subset does not make all MVP agents
   ready.

#### Financial baseline check — build handover only

For each agent actually in the build-handover scope, use the
[FinOps handover contract](../frontier-finops/references/agent-finops-baseline.md#frozen-snapshot-and-external-review-shapes)
and [strict financial guardrails](../frontier-finops/references/guardrails.md#strict-financial-build-handover).
Require:

- A complete validated linked profile with business, technical and finance
  owners, explicit scope/outcome, assumptions, exclusions, risks, confidence,
  measurement and owner-set guardrails.
- Twelve monthly demand values in each meaningful low/expected/high scenario,
  differing cost/outcome dependencies, typed quantities and explicit unit
  denominators and cost/period basis.
- Every in-scope cost driver priced with current applicable evidenced rates
  and any necessary evidenced FX. There is **no conditional unpriced
  exception**; missing, provisional, stale, unverified or synthetic dependencies
  block financial readiness.
- The frozen exact baseline ID, version and material hash, with external
  finance-owner review or externally evidenced delegation matching that target.
  Material edits need a new version and new review; preserve earlier snapshots.
- Current receipt/source lineage, evidence freshness and audience/customer-scope
  validation. Historical approval does not override today's gaps.

Keep structural validity, pricing completeness, recorded review and current
readiness separate. Raw `approved` status, workshop notes/verdicts, a cached
view or technical acknowledgement cannot supply review authority. Offline
review records are externally asserted, not authenticated financial permission;
local frozen files/hashes are not tamper-proof archival storage. Independently
verify the finance owner/delegation and evidence. Even planning-ready grants
no spending, purchase, build, deployment or protected-label authority.

Before any operation to resolve these gaps, obtain fresh actual scenario
awareness through FinOps; the handover check itself does not authorise cost
work. On decline, continue draft workshops, design, ordinary value and identity
with named gaps, but do not claim financial/build-handover readiness or waive
the mandatory baseline for an agent being handed over.

### Step 7: Keep the engagement
Save the folder to OneDrive with `CopyArtifact(surface="user", source="working/frontier/<slug>", destination="frontier-envisioning/<slug>", recursive=true, overwrite=true)` and update `engagement.json`:
`{"customer", "slug", "phase", "workshop_date", "blueprint_version", "identity_version", "value_version", "finops_version", "files": [], "updated"}`.

## Output format (reply)

- Where the engagement stands (phase, versions) and what was produced in this turn, by file name.
- A short table of gate results: gate, pass or missing items, owner.
- The next two actions, with owners, as bullets.

## Guardrails

- Never fabricate: hypotheses are labelled, nothing is invented to fill a gap, and open points stay open with an owner.
- Never let Microsoft-internal context reach a customer version; always build the customer version before anything leaves Microsoft.
- Always confirm before sharing outside Microsoft: show the user the customer version and review before sending or posting it.
- Customer generation must remove internal-derived attendee/risk/PRD content,
  resolving risk provenance before scrubbing and deriving final models afterwards.
  Customer export is not external/IP approval; private/internal distribution
  boundaries and actual install/publication/deployment decisions remain separate.
- Do not use real customer data unless an NDA or the customer's consent covers it; ask when unsure.
- Never let an agent decide about a person; any use case that shapes decisions about people names the human decision-maker before it starts.
- Always state product availability with its source date and mark previews.
- Do not evaluate individual people's performance from transcripts or chats.
- Always keep every artefact tied to its evidence ids so the customer can trace each statement.

## Failure handling

- If a phase skill fails a gate: stop the chain, report the gate and what is missing, and offer to continue with the gap documented.
- If the engagement folder belongs to another customer or version: ask which one to continue before writing anything.
- If no Work IQ evidence is found: continue only with the user's agreement and flag the blueprint as "secondary sources only".
- If a tool is unavailable (for example transcripts are not enabled): say which source is missing and use the next best one (meeting chat, notes, attached files).

## Files

- `references/method.md` — phases, gates, timeline, workshop agenda, artefact list
- `references/hairo-model.md` — the Human-AI Role Organisation model and how it maps to Microsoft's Frontier Firm concepts
- [FinOps versioned Quick Start](../frontier-finops/SKILL.md#quick-start--requested-versioned-baseline) — requested offline baseline procedure; separate from legacy costs
- [Offline baseline contract](../frontier-finops/references/agent-finops-baseline.md) — schema, exact commands, frozen review target and projected reports
