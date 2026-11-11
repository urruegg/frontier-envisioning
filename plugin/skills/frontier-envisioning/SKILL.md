---
name: frontier-envisioning
description: |
  Runs a Microsoft Innovation Hub Frontier envisioning engagement end to end: gathers
  context from Work IQ and transcripts, builds the hypothesis Frontier Company Blueprint
  (17 views in Vision, Design, Build and Workshops: HAIRO, journeys, PRD, Agent Factory
  Plan, risks and evidenced attendees), updates it after the workshop, prepares IT readiness,
  solution design and agent identity kit.
  Use when asked to "prepare the Frontier envisioning for <customer>", "run the
  envisioning prep end to end", "Frontier Company Blueprint for <customer> from scratch"
  or "what is next in the <customer> envisioning". Do NOT use for a single step: use
  frontier-context-discovery for context only, use frontier-blueprint for the blueprint
  HTML only, use frontier-solution-design for the PRD or architecture only,
  use frontier-agent-identity for agent names, colours and icons only.
license: MIT
metadata:
  category: productivity
  icon: Rocket
  version: "1.7.1"
  plugin: frontier-envisioning
---

# Frontier solution envisioning (end to end)

The Innovation Hub method for helping a customer see itself as a Frontier company: **human-led, agent-operated**. It chains three skills over the life of an engagement and keeps every artefact tied to evidence:

1. **Discover** with **frontier-context-discovery**: Work IQ (meetings, transcripts, mail, chats, files) and public sources become a cited context pack.
2. **Hypothesise** with **frontier-blueprint**: seventeen views in four parts. Vision: Overview with Microsoft's digital feedback loop, Org model, Blueprint, Journeys (including Agent Factory), Use cases and PRD. Design: Agents, Agent identity, Target architecture and IT readiness. Build: Roadmap, Plan and FinOps. Workshops: Attendees, Discovery, Risks and Evidence.
3. **Validate** in the workshop: the blueprint is presented and corrected live; notes and verdicts are exported and merged.
4. **Design** with **frontier-solution-design**: scaffold the agreed MVP PRD from the same canonical Python model as the page, then solution design and ADRs grounded in Microsoft's Frontier architecture guidance.

The full method, phases, gates and timings are in [references/method.md](references/method.md); the organisation model in [references/hairo-model.md](references/hairo-model.md).

## Quick Start

```
User: "Prepare the Frontier envisioning for Caldova, workshop on 12 November"
1. Locate the engagement folder (none) -> phase Discover
2. frontier-context-discovery: ListCalendarView + GetMeetingTranscript + SearchM365 -> customer-context.json
3. frontier-blueprint: seed, write the hypothesis, build with the identity kit -> Caldova Frontier Company Blueprint.html + agent identity package (proposal)
3b. frontier-value-case and frontier-finops: value case and cost model for the MVP agents -> business value in Use cases, FinOps page (gates V1, F1)
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
- Agent costs, credits or guardrails only: use frontier-finops instead.
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
Load **frontier-blueprint**: seed, write the hypothesis, build the blueprint together with the agent identity kit (a proposal until Gate E). When the evidence holds volumes and handling times, add the value case (**frontier-value-case**, gate V1) and the cost model (**frontier-finops**, gate F1) and rebuild with `--value --finops`; their top assumptions go on the workshop agenda. Gate B: the build reports no errors; every MVP candidate has its canvas and seven declarations; internal evidence is marked.

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

### Step 6a: Value and cost validated (gates V2, F2)
Merge the workshop's assumption verdicts (`merge_value_feedback.py` in **frontier-value-case**) and rebuild. Gate V2: the five most sensitive assumptions confirmed or adjusted by their owners. Gate F2: guardrails designed with owners (**frontier-finops**) and handed to **frontier-solution-design** as FinOps NFRs and a purchase-model ADR.

### Step 6b: Agent identity approval (before the agents are built)
Load **frontier-agent-identity**: the blueprint already carries a proposal kit; collect the customer's own brand, review the names with the user (and the workshop's identity feedback), then rebuild the kit and the blueprint together. Gate E: validator 0 errors, unit tests passed, decisions N-1 to N-6 listed with owners.

### Step 6c: Architecture design workshop and IT readiness (gate R)
1. About ten working days before the architecture design workshop, send the preparation items (P-) from the blueprint's IT readiness page, or `design/it-readiness.md` from **frontier-solution-design**, to the customer's IT with owners and due stages.
2. In the workshop, walk the Target architecture: landing zone per journey (DEV, TEST, PROD; data classes), the ADRs, then the IT readiness decisions (D-01 engineering control plane first). Verdicts and statuses are captured live in the HTML and merged with **frontier-blueprint** step 5.
3. Move the MVP agents along the Agent Factory board: validated, designed, then ready for build when all eight handover checks pass. Gate R: readiness checks (R-) for the prototype stage passed, D-01 decided, the MVP agents ready for build.

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
