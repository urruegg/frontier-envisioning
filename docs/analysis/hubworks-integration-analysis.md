# HubWorks × Frontier Envisioning — Integration Analysis

## How to connect the Frontier Envisioning plugin with HubWorks, CE Hub engagements and workshop transcripts

| Field | Value |
|---|---|
| Document | Integration analysis and extension proposal |
| Version | 0.9.5 — draft for discussion (sharing copy, 8 Nov 2026: Frontier release numbers updated; 1.1.0 shipped the agent identity kit, 1.2.0 the identity page, 1.3.0 business value and FinOps, 1.4.0 the Innovation Hub journey structure with the Agent Factory, landing zone, ADRs and IT readiness, 1.5.0 the digital feedback loop on the Overview, 1.6.0 the agent workflow in the Copilot Studio designer style; the HubWorks changes move to 1.7 and 1.8) |
| Date | 22 October 2026 |
| Author | Urs Rüegg, Sr Solution Engineer, Microsoft Innovation Hub Switzerland |
| Proposed reviewers | HubWorks core team (Brendon Colburn, Rich Ross, Bryan Roberts) · CE Hub closeout contributors (Jay Leask, Yuri Lausberg) · Hub engagement standards (Powlo, Innovation Hub) · Engagement IQ (Andreas Krüger) · Innovation Hub Switzerland |
| Scope | HubWorks 1.0 Cowork plugin (SE package) and HubWorks-Director · Frontier Envisioning plugin 1.0.1 · CE Hub engagement records (Plan & Debrief) · Teams meeting transcripts and the engagement folder |
| Evidence base | Tools-AI-HubWorks channel (119 posts, Oct 2025 – Oct 2026) · HubWorks Monthly Call of 12 Oct 2026 (transcript) · HubWorks October 2026 sprint summary · Hubworks Tool Comparison Guide · Engagement Guides – Hub SE and Manager Overview (Nov 2025) · CEHub MSX Request Integration – Business Requirements · the author's calendar, transcripts and OneDrive engagement folders (last 60 days) · Frontier Envisioning PRD and Solution Design 1.0.1 |
| Limitation | HubWorks is installed in the author's Cowork but was switched off for this analysis session, so its skills were not run. Statements about HubWorks behaviour come from its skill catalogue and the community sources above; verify them in a chat with HubWorks and the Dynamics 365 Sales plugin turned on (section 13, step 1). |
| Classification | Microsoft internal. This sharing copy names no customers; share it within Microsoft only. |

---

## 1. Executive summary

**The short answer.** HubWorks and Frontier Envisioning do different jobs. They should stay separate products that share one engagement.

- **HubWorks runs the engagement.** It finds the CE Hub record, creates tasks and the engagement folder, renders the official agenda, closes the engagement out in CE Hub and drafts the follow-up mail.
- **Frontier Envisioning produces the content** of envisioning and architecture-design engagements: the evidence-based context pack, the Frontier Company Blueprint, and the PRD, solution design and ADRs.

Today neither knows the other exists. Frontier asks you for the customer, date and transcripts that CE Hub and HubWorks already know. HubWorks closeout re-reads the transcripts and fills the Debrief without the use cases, architecture and next steps that the blueprint already holds. The result is double work and a CE Hub record that under-reports what a Frontier engagement delivered.

**Recommendation: connect now, contribute next, standardise together.**

1. **Connect (now – 4 weeks).** Introduce a shared engagement contract: one engagement folder and one `engagement.json`, keyed by the CE Hub engagement number. HubWorks engagement-initiator writes the CE Hub block and Frontier reads it. Both plugins use one transcript archive and one evidence register. Frontier hands a *closeout pack* to HubWorks engagement-closeout, which stays the only writer to CE Hub; a person still presses *Complete Plan and Debrief*.
2. **Contribute (next one or two HubWorks monthly releases).** Offer Frontier as an opt-in *HubWorks Frontier* package in the Innovation-Hub-Agentic-Toolkit repository, following the precedent of the separate HubWorks-Director package. Add small pull requests to the HubWorks skills it touches: chiefly engagement-initiator, agenda-builder, engagement-closeout and architecture-diagram-builder, plus the coming anonymizer.
3. **Standardise (with the Hub standards and Engagement IQ teams).** Move the method knowledge into the shared, version-controlled standards store the HubWorks core team is discussing: Frontier phases, HAIRO declarations, question bank, outcome definitions and the CE Hub field mapping. HubWorks, Frontier and Engagement IQ then point to the same definition of a good envisioning output.

**Rejected options:**

- *Merging Frontier into the HubWorks SE package*: scope creep, routing conflicts, and noise for SEs who never run envisioning.
- *Letting Frontier talk to CE Hub itself*: a second writer, and duplicated option-set logic that already drifted once in October.

**Why it matters.**

| Today | After integration |
|---|---|
| CE Hub number, customer, dates and attendees typed again in every tool | Read once from CE Hub by engagement-initiator and reused by every skill |
| Transcripts found by searching meetings; out of reach after about 60 days unless filed by hand | Matched to the engagement, archived in the engagement folder and parsed once into evidence ids |
| Closeout drafted from transcripts only; Frontier outcomes under-reported | Outcomes, Frontier Success Framework pillars, Discovery & Insights, Handover and new opportunities pre-filled from the validated blueprint, each with evidence |
| Two agendas, two follow-up mails, two folders | One official agenda with Frontier content blocks, one follow-up draft, one folder |
| Anonymised engagement output written by hand | The customer-safe blueprint build plus the lighthouse anonymizer produce it |

**Top extensions** (full backlog in section 8):

| ID | Extension | Owner | Effort |
|---|---|---|---|
| F-01 / H-01 | Shared `engagement.json` with the CE Hub block, written by engagement-initiator and read by Frontier | Frontier + HubWorks | S |
| F-03 / H-05 | Transcript harvest: match meetings to the CE Hub engagement, archive them well within 60 days, parse them into evidence ids | Frontier, later shared | M |
| F-05 / H-04 | Closeout pack: blueprint mapped to the CE Hub Plan & Debrief fields; engagement-closeout reads it | Frontier + HubWorks | M |
| F-06 / H-03 | Agenda blocks: Frontier workshop content rendered by agenda-builder on the official template | Frontier + HubWorks | S |
| H-02 | "Frontier envisioning" engagement type (task template set) in engagement-initiator | HubWorks | S |
| F-07 | Hub outcome pack: the standard use-case, prioritisation, solution-mapping and next-steps slides generated from the blueprint | Frontier | M |
| H-07 | Lighthouse anonymizer accepts the blueprint and its customer build | HubWorks | S |
| S-01 to S-04 | Shared standards: excellence criteria, field mapping, engagement and evidence schemas, transcript conventions | Hub standards + both teams | M |

---

## 2. Where things stand (October 2026)

### 2.1 HubWorks

**What it is.** HubWorks is the Innovation Hub Agentic Toolkit. It is a skills repository (`mcaps-microsoft/Innovation-Hub-Agentic-Toolkit`, landing page aka.ms/hubworks), led by Brendon Colburn with a growing contributor community. The repository deliberately carries skills only and no application code. The CE Hub MCP server added in PR #222 was rolled back on 3 Sep 2026 because HubWorks "carries no application code base" (Rich Ross); that code is maintained elsewhere.

**Direction and distribution.**

- **24 Jul 2026:** the team announced a "very Cowork-centric approach to the repo and solution".
- **16 Sep 2026:** HubWorks 1.0 became an official Cowork plugin in the Microsoft internal catalog. The earlier 0.6.x line is expected to become a dev channel.
- **12 Oct 2026 (monthly call):**
  - Releases move to a monthly cadence.
  - Several people can now publish through the Microsoft Digital web app. A publish takes two to three days to appear, and only one request can be in flight at a time.
  - An access-group change temporarily limited 1.0 to the core team. The workaround is the 0.6.17 dev version; 1.1 follows once the access fix lands.
- **October sprint:** HubWorks was split into an SE package and a separate HubWorks-Director package (PR #262), so that people only see the skills relevant to their role.
- **Runtimes:** Cowork is the path the team supports. The CLI toolkit (GitHub Copilot CLI) and Scout/Clawpilot remain for tinkering and local automation. The working rule heard on 12 Oct: use Cowork for customer work and Scout for internal automation, and create drafts rather than send.
- **Size limit:** each skill must stay under 20,000 characters. This is one reason the core team is discussing a version-controlled "knowledge vault" for standards that skills point to.

**SE package skills (as installed in the author's Cowork).**

| Skill | Role in the engagement | Notes |
|---|---|---|
| engagement-initiator | Starts an engagement. Finds the CE Hub record (scheduled-engagement table, by delivery date, hub location and customer name). Captures the event URL, engagement ID, event name and TPID. Creates tasks from engagement-type template sets, with Planner and an account-team precall. | CE Hub lookup added in PR #175 (Jun 2026); a missing match never blocks initiation |
| cehub | CE Hub lookups and updates through the Dynamics 365 Sales connection | Needs the Dynamics 365 Sales plugin turned on |
| agenda-builder | Previews the agenda in chat, iterates with you, then renders it on the official template hosted in the HubWorks Teams SharePoint | Transcript-grounded agenda detail restored in PR #277 |
| cet-catalog-search | Searches the CE Hub content catalogue (experiences and content items) | Closeout uses it to name real catalogue items |
| engagement-closeout | Drafts the CE Hub Plan & Debrief from the CE Hub record and the Work IQ transcript. Uses live selection lists and nudges you about the floor tour. Writes the follow-up mail as an Outlook draft. Hands completion to the native *Complete Plan and Debrief* button. | #NEW / #UNVERIFIED opportunity tags (PR #274) stay account-team-only |
| architecture-diagram-builder | Draws architecture diagrams | Rendering only; no envisioning method |
| journey-update | Updates CE Hub customer journeys | Natural target for Frontier next steps |
| customer-story-writer | Writes customer stories | Later stage |
| schedule-meetings | Schedules engagement meetings | Could stamp the CE Hub number into meeting subjects |
| hubworks | Entry point and help | — |
| hub-feedback | Turns the friction in a session into a structured report for a GitHub issue | The feedback loop the Frontier skills should join |

The CLI toolkit adds skills that are not in the Cowork SE package. Among them:

- **customer-insights:** an HTML pre-brief from Power BI, MSX and Work IQ, triggered by a CE Hub URL or TPID.
- **Other SE skills:** followup-email, task-generator, lesson-lifecycle and journey-promoter.
- **Reporting skills:** hub-insights, hub-business-audit, engagement-trends and solutionarea-trends.

Appendix A lists them all.

**CE Hub connectivity is the weak spot.**

- CE Hub is a Dataverse application (Dynamics 365 Event Management). Engagements live in the `msevtmgt_event` table.
- In Cowork, HubWorks reaches CE Hub only when the Dynamics 365 Sales plugin is turned on, and that plugin sometimes switches itself off (12 Oct call).
- **11 Aug 2026:** the HubWorks Cowork plugin could not connect to CE Hub at all, because Dataverse connector calls were refused pre-flight.
- **28 Sep 2026:** Scout users reported CE Hub issues again.
- **October release:** adds a prerequisite check across the 14 CE Hub-dependent skills that tells the user how to turn the connection on (PR #281).

Any integration must therefore work without CE Hub and treat it as an enrichment, not a dependency.

**Closeout state.**

- **31 Aug release:**
  - Selection lists are read live from CE Hub.
  - Content items are matched to the real catalogue.
  - A nudge reminds you about the floor tour, which is not in transcripts.
  - The "false done" bug is fixed by handing completion back to the native button.
- **14 Oct:** Jay Leask reported that closeout no longer matched the changed Plan & Debrief form. The field list in section 2.3 is the current one.

**What is coming.**

- **Lighthouse architecture anonymizer** (UK Hub), planned for the next release. It supports the expectation that every architect publishes at least one anonymised engagement output.
- **Lynx MCP server** for M365 licensing and usage data, including Copilot (proposed 14 Oct).
- **Engagement IQ** as a separate, complementary product.
- **Coaching:** interest in using these tools for it.

### 2.2 Frontier Envisioning 1.0.1

| Element | What it does today | Gap against Hub operations |
|---|---|---|
| frontier-envisioning (orchestrator) | Runs the phases Discover → Hypothesise → Prepare → Consolidate → Design with gates A–D. Keeps `engagement.json` (customer, slug, phase, workshop date, blueprint version, files). | Asks you for customer, scope and date. Has no CE Hub number, TPID or engagement type. Uses its own folder in `Documents/Cowork/frontier-envisioning/<slug>/`. |
| frontier-context-discovery | Searches Work IQ (meetings, transcripts, mail, chats, files) and public sources and writes `customer-context.json` with evidence ids. Parses .vtt, .txt, .md, .docx and .json transcripts. | Finds transcripts by searching, not by engagement. Nothing archives them before they age out. |
| frontier-blueprint | Seeds, builds and validates the Frontier Company Blueprint: journeys, agents, use cases with value, feasibility and horizon, MVP options, next steps, target architecture, and evidence with visibility. Its customer build strips internal content. Merges workshop feedback. | Outputs are not mapped to CE Hub Outcomes, Frontier Success Framework pillars or Handover. No slides in the Hub's standard outcome format. |
| frontier-solution-design | Writes the PRD, solution design and ADRs for the MVP agents, grounded in Microsoft Frontier guidance | Architecture diagrams are not drawn with the Hub's diagram builder |
| Distribution | Personal skills in the author's Cowork (MIT, Copyright Urs Rüegg) | Outside the HubWorks catalogue, release cadence and feedback loop |

All four SKILL.md files are between 7,500 and 10,700 characters, comfortably inside the HubWorks 20,000-character limit.

### 2.3 The Hub engagement standard both plugins must serve

**Engagement types.** The CE Hub request requirements list Executive Briefing, Strategy Session, Envisioning Workshop, Architecture Design Session, Hackathon and Rapid Prototype.

**Consistent engagement outcomes** (Engagement Guides, aka.ms/hub/guides, Nov 2025). The guidance is "send it out, check in closeout":

| Engagement type | Minimum outputs |
|---|---|
| Business envisioning | Agenda · up to 5 use cases (2 slides each) · prioritisation matrix (1 slide) · next steps (1 slide) |
| Solution envisioning | Agenda · solution mapping (1 slide) · next steps (1 slide) |
| Architecture design | Agenda · architecture diagram and decisions document (1 whiteboard, 1 short document) · next steps (1 slide) |
| Rapid prototype | Agenda · code + configuration · next steps (1 slide) |

**CE Hub Plan & Debrief form** (as of 14 Oct 2026):

- **PLAN:** Industry · Solution Area · Regional Programs · Content Items & Experiences Used · Engagement Agenda
- **DEBRIEF:** Outcomes · Frontier Success Framework · Discovery & Insights · Handover · What worked well? · What did not work well? · What new opportunities were discovered?
- **Retired, never to be written:** Conversations; Next Steps & Timeframe.

The form lines up closely with what a Frontier blueprint holds:

- The five CE Hub *Outcomes* options mirror the consistent outcomes exactly: use cases + prioritisation matrix, solution mapping, architecture, code + configuration, next steps.
- The four *Frontier Success Framework* pillars are exactly what a Frontier blueprint describes: enriching employee experiences, reinventing customer engagement, reshaping business processes, bending the curve on innovation.

That makes the validated blueprint the natural source for the Debrief. Appendix B lists the field names and option values.

### 2.4 What the author's engagements show

From the author's calendar, transcripts and OneDrive (last 60 days):

- **Naming patterns link meetings to engagements.**
  - Customer days are titled `<Customer> @Microsoft Innovation Hub Switzerland`.
  - Internal planning calls such as `Innohub Engagements: <Customer A> & <Customer B>` cover more than one engagement.
  - At least one internal call already carries the CE Hub engagement number: `[Internal Call] 000xxxxx - <Customer> | <Title>`.
- **Multi-part days:** one engagement can produce several transcripts (two for one customer day on 20 Oct, three for another on 21 Sep).
- **Language:** Swiss engagements mix German and English. One architecture call in September was titled and held in German.
- **Availability:** transcripts are only reachable for meetings you organised or attended, and only for about 60 days. 31 recent meetings returned "access denied".
- **Manual archive:** the author already files transcripts by hand in `Documents/Projects/<Customer>/<Engagement name year>/` (.docx exports, .vtt bundles in .zip files), next to summaries and wrap-up decks.
- **Combined days:** at least one recent workshop ran "Part 1 – Solution envisioning" and "Part 2 – Design target architecture" on the same day. One CE Hub engagement can therefore owe two outcome sets.

These observations drive the transcript design in section 6.

---

## 3. How the two plugins fit

### 3.1 Engagement lifecycle

| Stage | HubWorks today | Frontier today | Integration point |
|---|---|---|---|
| 1 Request and qualification | CE Hub request; internal qualification call; customer-insights pre-brief (CLI) | Context discovery from Work IQ | Qualification notes and engagement goals enter the context pack as internal facts |
| 2 Initiation | engagement-initiator: CE Hub record, ID, URL, TPID, tasks, folder, precall | Step 1 asks for customer and date | Initiator writes `engagement.json`; Frontier reads it; a "Frontier envisioning" task set adds the Frontier tasks |
| 3 Preparation | agenda-builder, cet-catalog-search, schedule-meetings | Context pack → hypothesis blueprint → customer build → agenda draft and discovery questions | Frontier delivers agenda blocks and questions; agenda-builder renders the official agenda; demos come from the catalogue |
| 4 Delivery | Teams transcription; Engagement IQ (separate, experimental) | Blueprint used live; verdicts and answers exported as feedback | Transcripts and feedback exports land in the engagement folder; later, Engagement IQ capture feeds the same feedback format |
| 5 Consolidation | — | Transcript parsing, feedback merge, validated blueprint | Shared transcript archive and evidence register |
| 6 Closeout | engagement-closeout (Plan & Debrief); follow-up mail draft | Workshop summary | Frontier closeout pack pre-fills the Debrief; HubWorks writes it after you confirm; one follow-up draft |
| 7 Follow-on design | architecture-diagram-builder | PRD, solution design, ADRs | Frontier owns the architecture content; the diagram builder draws it; the ADRs are the "decisions document" |
| 8 Journey and impact | journey-update, customer-story-writer, Director reporting | Next steps and MVP options | MVPs become journey steps and #NEW opportunities; Director reports show Frontier outcomes; the anonymised blueprint becomes a lighthouse pattern |
| 9 Improvement | hub-feedback → GitHub issues | — | Frontier skills join hub-feedback |

### 3.2 Overlaps and how to resolve them

| Overlap | Resolution | Principle |
|---|---|---|
| Workshop agenda (Frontier Step 4 vs agenda-builder) | Frontier produces content blocks only; agenda-builder renders the official template | The Hub template wins |
| Transcript reading (closeout and agenda-builder vs the Frontier parser) | One archive and one evidence register; HubWorks may still read raw transcripts | Parse once, cite everywhere |
| Architecture (diagram builder vs solution design) | Frontier owns layers, blocks and decisions; the diagram builder draws them | Content vs rendering |
| Summary mail (Frontier workshop summary vs closeout follow-up mode) | One HubWorks follow-up draft, fed by the Frontier workshop summary | One customer mail, always a draft |
| CE Hub writes | HubWorks only, after your confirmation; completion via the native button | Single writer |
| Skill routing ("prepare the agenda", "close out", "draw the architecture") | Frontier descriptions name the HubWorks skill in their "Do NOT use for…" lines; conflict scan with both plugins enabled | No double triggering |

---

## 4. Integration options

| Option | Description |
|---|---|
| A — Side by side with a shared contract | Two plugins, one engagement folder, and file contracts: `engagement.json`, evidence register, agenda blocks, closeout pack |
| B — Opt-in HubWorks Frontier package | Frontier contributed to the HubWorks repository as a separate package (like HubWorks-Director), plus small PRs to existing skills, released through the HubWorks catalogue |
| C — Merge into the SE package | The four Frontier skills become part of the HubWorks SE package |
| D — Frontier talks to CE Hub directly | Frontier reads and writes CE Hub through its own Dataverse calls |

| Criterion | A | B | C | D |
|---|---|---|---|---|
| Time to value | ●●● weeks | ●●○ one or two releases | ●○○ needs broad consensus | ●●○ |
| Experience for SEs | ●●○ two plugins | ●●● one catalogue, opt-in | ●●○ more noise for SEs who never run envisioning | ●●○ |
| Fit with HubWorks direction | ●●○ | ●●● follows the Director split | ●○○ scope creep; HubWorks lead: not everything needs to belong to HubWorks | ●○○ duplicates the cehub skill |
| Maintainability | ●●○ you maintain it alone | ●●● shared release and feedback loop | ●●○ | ●○○ form drift (as on 14 Oct) hits two code bases |
| Risk | ●●● low | ●●○ release and access lag | ●○○ routing conflicts, pressure on the 20,000-character limit | ●○○ two writers to CE Hub |
| Data integrity | ●●● | ●●● | ●●● | ●○○ |

●●● = best.

**Recommendation: A now, B within the next two monthly releases; C and D rejected.**

- Option A is a prerequisite for B anyway: the contracts in section 5 are what the HubWorks skills will read once Frontier is a package.
- Option D survives only as a manual fallback. When CE Hub is unreachable, Frontier asks once for the engagement number and URL and carries on.
- Engagement IQ is not an alternative to these options. It is a future live input (section 6.1).

---

## 5. Target integration architecture

### 5.1 Principles

1. **One engagement, one key.** The CE Hub engagement number, together with the event URL, keys the folder, the transcripts and every artefact.
2. **One writer per system.** HubWorks writes CE Hub; Frontier writes the blueprint and the design documents. A person confirms every CE Hub change and presses *Complete Plan and Debrief*.
3. **Files are the contract.** Versioned JSON and markdown in the engagement folder. No skill calls another plugin's internals, so the same contract works in Cowork, the CLI and Scout.
4. **Evidence first.** Every blueprint statement, closeout field and follow-up point carries evidence ids that lead back to a transcript passage or a document.
5. **Visibility on every item.** Each item is customer, internal or account-team-only. #NEW and #UNVERIFIED opportunities never reach a customer document, and customer builds strip internal content.
6. **Degrade gracefully.** Without CE Hub or HubWorks, Frontier still works. Without Frontier, HubWorks works as today.
7. **Standards outside the skills.** Method, field mappings and excellence criteria live in versioned reference files that skills point to.
8. **Drafts, not sends.** Customer mail and CE Hub completion stay human actions.

### 5.2 Component view

```
 Microsoft 365 and Work IQ: Teams meetings and transcripts, Outlook, Teams chats, OneDrive, SharePoint
                          │                                                   │
                          ▼                                                   ▼
┌─ HubWorks (SE package) ──────────────────────────┐   ┌─ HubWorks Frontier / Frontier Envisioning ─┐
│ engagement-initiator     agenda-builder          │   │ frontier-envisioning (orchestrator)        │
│ cehub                    cet-catalog-search      │   │ frontier-context-discovery                 │
│ schedule-meetings        engagement-closeout     │   │    + transcript harvest                    │
│ journey-update           customer-story-writer   │   │ frontier-blueprint                         │
│ architecture-diagram-builder   hub-feedback      │   │    + closeout pack, agenda blocks          │
│                                                  │   │ frontier-solution-design                   │
│                                                  │   │    + Hub outcome pack                      │
└──────────────────────────────────────────────────┘   └────────────────────────────────────────────┘
          │                       ▲                              ▲                       │
          │ writes                │ reads                        │ reads                 │ writes
          ▼                       │                              │                       ▼
┌─ Engagement folder (OneDrive) ────────────────────────────────────────────────────────────────────┐
│ engagement.json (CE Hub block, phases, file index)    transcripts/ (archived parts + index.json)  │
│ evidence/register.json   frontier/ (context pack, blueprint)   handoff/ (agenda, closeout)        │
│ design/ (PRD, solution design, ADRs)   hubworks/ (agenda, closeout review, follow-up draft)       │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
          │ CE Hub reads and writes only through HubWorks (cehub, engagement-closeout,
          │ journey-update), always after your confirmation
          ▼
 CE Hub (Dataverse engagement records), reached through the Dynamics 365 Sales connection
```

### 5.3 The engagement contract

`engagement.json` grows from Frontier's internal state file into a shared, versioned contract (`hub-engagement/1.0`). Each writer owns one block and merges the others rather than overwriting them.

```json
{
  "schema": "hub-engagement/1.0",
  "cehub": {
    "engagement_number": "000xxxxx",
    "event_id": "<CE Hub event GUID>",
    "event_url": "<CE Hub event URL>",
    "event_name": "<official event name>",
    "engagement_type": "Envisioning Workshop",
    "hub": "Switzerland",
    "delivery_dates": ["2026-11-12"],
    "tpid": "<TPID>",
    "account": "<primary account>",
    "lead": "<Hub lead>",
    "status": "Scheduled",
    "read_at": "2026-10-22T14:00:00+02:00"
  },
  "customer": { "name": "<Customer>", "slug": "<customer-slug>", "industry": "<industry label>" },
  "folder": "Documents/Projects/<Customer>/<Engagement name year>",
  "meetings": [
    {
      "title": "<Customer> @Microsoft Innovation Hub Switzerland",
      "start": "2026-11-12T09:00:00+01:00",
      "kind": "customer",
      "transcripts": ["transcripts/2026-11-12_part1.vtt"],
      "evidence": ["W01"]
    }
  ],
  "frontier": {
    "phase": "Consolidate",
    "blueprint_version": "1.2",
    "context_pack": "frontier/customer-context.json",
    "closeout_pack": "handoff/closeout-pack.json"
  },
  "outcomes": {
    "planned": ["Use cases + prioritization matrix", "Solution mapping", "Next steps"],
    "evidenced": [{ "outcome": "Solution mapping", "file": "frontier/<Customer> Frontier Company Blueprint.html" }]
  },
  "writers": { "cehub": "hubworks/engagement-initiator", "frontier": "frontier-envisioning" },
  "updated": "2026-10-22T14:05:00+02:00"
}
```

Rules:

- engagement-initiator creates the file and the `cehub` block. Frontier never edits that block.
- Frontier owns `frontier`, `meetings[].evidence` and `outcomes.evidenced`. HubWorks closeout reads them.
- The file holds no tokens, no transcript text, and no personal data beyond names and roles.
- Without HubWorks, Frontier creates the file with an empty `cehub` block and asks once for the engagement number.

### 5.4 One engagement folder

Today there are three conventions:

- HubWorks saves to its configured OneDrive engagement folder (reliable since the 31 Aug release).
- The author files by hand under `Documents/Projects/<Customer>/<Engagement name year>/`.
- Frontier keeps its own folder under `Documents/Cowork/frontier-envisioning/<slug>/`.

**Proposal:** the HubWorks engagement folder is the home. Frontier writes into a `frontier/` subfolder when `engagement.json` points to that folder. It falls back to its Cowork folder only when no engagement folder exists.

```
<Engagement folder>/
  engagement.json
  transcripts/   archived .vtt/.docx per meeting part, plus index.json
  evidence/      register.json (E-ids for documents, W-ids for workshop transcripts)
  frontier/      customer-context.json, blueprint.json, blueprint HTML (internal and customer), feedback/
  handoff/       agenda-blocks.json, closeout-pack.json, closeout-review.md
  design/        prd.md, solution-design.md, adr/
  hubworks/      agenda, closeout review, follow-up draft text
```

Writing into an arbitrary OneDrive folder needs an upload into that folder instead of the Cowork folder sync. This is a small change in the orchestrator's save step (F-02).

### 5.5 End-to-end flow

```
 1  CE Hub      engagement approved
 2  HubWorks    engagement-initiator  -> CE Hub record (number, URL, TPID, type, dates)
                                      -> folder + engagement.json + tasks (Frontier task set for
                                         Envisioning Workshop and Architecture Design Session)
 3  Frontier    context discovery     -> scoped by engagement.json (TPID, dates, attendees)
                                      -> context pack + evidence register
 4  Frontier    hypothesis blueprint  -> customer build -> agenda-blocks.json + top discovery questions
 5  HubWorks    agenda-builder        -> official agenda with the Frontier blocks -> PLAN: Engagement Agenda
 6  Workshop    Teams transcription on; blueprint used live; feedback export saved to the folder
 7  Frontier    transcript harvest    -> match meetings to the engagement -> archive -> parse -> W-ids
 8  Frontier    consolidation         -> feedback merged -> validated blueprint -> closeout-pack.json + review
 9  HubWorks    engagement-closeout   -> CE Hub record + closeout pack -> review draft -> you confirm
                                      -> fields written -> you press Complete Plan and Debrief
                                      -> follow-up mail as an Outlook draft
10  Frontier    solution design       -> PRD, solution design, ADRs
    HubWorks    architecture-diagram-builder -> diagram from the blueprint architecture block
11  HubWorks    journey-update        -> MVP next steps on the customer journey; #NEW opportunities to the account team
12  Both        anonymizer + customer build -> anonymised Frontier pattern; hub-feedback after the session
```

### 5.6 What it feels like for an SE

| You say | What happens |
|---|---|
| "Initiate the engagement for <Customer> on 12 November" | HubWorks finds the CE Hub record and creates the folder, `engagement.json` and the Frontier task set |
| "Prepare the Frontier envisioning for this engagement" | Frontier reads the CE Hub block, gathers context, and builds the hypothesis blueprint and the agenda blocks |
| "Build the agenda" | agenda-builder previews and renders the official agenda with the Frontier sessions |
| "Archive and analyse the workshop transcripts" | Every part of the workshop day is archived and turned into evidence ids |
| "Update the blueprint with the workshop feedback" | Validated blueprint, plus the closeout pack and its review |
| "Close out the engagement" | Plan & Debrief pre-filled from the closeout pack; you confirm and press *Complete Plan and Debrief*; the follow-up draft is created |
| "Write the PRD and target architecture for the MVP", then "Draw the architecture diagram" | Frontier writes the design documents; HubWorks draws the diagram |
| "Anonymise the blueprint as a lighthouse pattern" | The customer build plus the anonymizer produce the shareable pattern |

---

## 6. Transcript integration

### 6.1 Sources and their limits

| Source | What it gives | Limits | Role |
|---|---|---|---|
| Teams meeting transcripts | Speaker-attributed, timestamped text per meeting part | Only meetings you organised or attended; about 60 days; transcription must be on; one file per part | Primary evidence |
| Archived transcript files in the engagement folder | Durable .vtt and .docx copies | Filed by hand today | System of record after 60 days |
| Blueprint feedback export | Verdicts on agents and use cases, discovery answers | Only what was captured live | Primary for validation |
| Teams recap and custom recap templates | Summaries and action items | No verbatim evidence | Secondary |
| Facilitator notes, whiteboard photos | Canvases and sketches | Unstructured; must be typed or described | Secondary |
| Floor tour and demos | — | Not in transcripts | Ask explicitly, as closeout already does |
| Engagement IQ | Near-real-time transcript, live gap spotting and artefact filling | Experimental; the 12 Oct call recalled the guidance not to use it on customer engagements yet | Future live input |

### 6.2 Matching transcripts to the CE Hub engagement

Rules, strongest first. Each match records its rule and confidence in `transcripts/index.json`.

| Rule | Signal | Confidence | Action |
|---|---|---|---|
| R1 | CE Hub engagement number in the meeting subject | Exact | Link |
| R2 | Meeting created from the engagement (schedule-meetings, or a session link stored in CE Hub) | Exact | Link |
| R3 | Customer name + Hub naming pattern + delivery date | High | Link and list it in the reply |
| R4 | Customer name + date window (−30 to +30 days) + attendee overlap with the CE Hub attendees | Medium | Ask before linking |
| R5 | Meeting about several engagements (`<Customer A> & <Customer B>`) | Split | Link, but quote only the passages about this customer |

**Classification.**

- Meetings with only Microsoft attendees, or marked "[Internal Call]", are internal.
- Meetings with customer attendees are customer meetings. Their evidence still defaults to internal until you review it.

**One convention fixes most of the matching: put the CE Hub engagement number in every engagement meeting subject**, for example `[CE Hub 000xxxxx] <Customer> @Microsoft Innovation Hub Switzerland`. Some internal calls in the Swiss Hub already do this. schedule-meetings and engagement-initiator can do it automatically (H-01).

### 6.3 Pipeline

```
harvest  ->  archive  ->  parse  ->  register  ->  consume
```

1. **Harvest.** Run on demand ("archive the transcripts for this engagement") or as a scheduled Cowork task during the engagement window. Find meetings with rules R1–R5 and fetch every transcript part.
2. **Archive.** Save `transcripts/<date>_<part>_<short-title>.vtt` and update `index.json`: meeting title, start, part, language, kind, rule and confidence. Do this well within the 60 days, ideally within five working days.
3. **Parse.** The existing Frontier transcript parser turns each part into turns and signals with timestamps: decisions, actions, pains, KPIs and questions.
4. **Register.** Each part becomes one evidence entry (W-id) in `evidence/register.json`, with participants by role, visibility, a summary and short timestamped quotes.
5. **Consume.**
   - Frontier cites the W-ids in the blueprint.
   - HubWorks closeout uses the same register for Discovery & Insights and the retrospective questions.
   - agenda-builder uses the precall evidence.
   - The follow-up draft and customer-story-writer quote from the register.

### 6.4 Quality and compliance rules

- **Language:** keep quotes in the original language (German or English) and write summaries in the document language.
- **Multi-part days:** one W-id per part, ordered by start time. The blueprint cites the part.
- **People:** map speakers to roles in anything customer-facing. Never evaluate individuals' performance from transcripts.
- **Confidentiality:** customer transcripts are confidential customer information. Use real data only under an NDA or with consent; nothing internal reaches a customer build.
- **Consent:** transcription follows Teams policy, and the customer is told at the start of the session.
- **Retention:** the archive follows Microsoft records rules for customer engagement material; delete on request.

---

## 7. CE Hub data mapping

### 7.1 Read: CE Hub → Frontier

| CE Hub data | Frontier target | Use |
|---|---|---|
| Engagement number, event URL, event name | `engagement.json` CE Hub block; blueprint `meta.cehub` | Key and links |
| Engagement type | `meta.engagement`; planned outcomes | Which outcome set to produce (section 7.3) |
| Delivery dates | `meta.workshop_date`; transcript window | Harvest and timeline |
| Primary account, TPID, industry, segment | Context pack `customer` | Scoping; industry patterns |
| Engagement goals and qualification notes (desired outcomes, drivers and use cases identified, time frames, topics, risks and hot buttons, success criteria, stakeholders, partner) | Context pack facts, constraints and open questions, all internal | Hypothesis and question bank |
| Attendees (customer, partner, Microsoft) | Context pack stakeholders (role, organisation) | Leaders, personas, and who answers which discovery question |
| Solution area | Technology hints for domains and agents | Architecture layers |
| Content items and experiences | Evidence (internal) | Demo choice and the PLAN field |
| Customer journeys and linked opportunities | Next steps; MVP options | Follow-on and opportunity linking |

The qualification-note fields are those listed in the CE Hub request integration requirements. How many are filled in practice varies, so every one is optional.

### 7.2 Write: closeout pack → Plan & Debrief (through HubWorks)

Frontier writes `handoff/closeout-pack.json`. engagement-closeout then:

1. reads the closeout pack;
2. resolves the option values live from CE Hub, because the codes are non-sequential and change;
3. shows you the review draft;
4. writes only after you confirm.

| CE Hub field | Frontier source | Rule |
|---|---|---|
| PLAN · Industry | Context pack industry | Match the live option label |
| PLAN · Solution Area | Technologies of the agents and the architecture layers, mapped to solution areas | Proposal; you confirm |
| PLAN · Regional Programs | — | HubWorks or you |
| PLAN · Content Items & Experiences Used | Demo list from the agenda blocks | HubWorks matches the catalogue; add the floor tour |
| PLAN · Engagement Agenda | Agenda rendered by agenda-builder from the Frontier blocks | As sent to the customer |
| DEBRIEF · Outcomes | Use cases with value and feasibility → *Use cases + prioritization matrix* · agents mapped to Microsoft technology → *Solution mapping* · architecture layers and ADRs → *Architecture* · prototype repository or Copilot Studio solution → *Code + configuration* · next steps → *Next steps* | Tick an outcome only when its artefact exists in the folder |
| DEBRIEF · Frontier Success Framework | Union of the pillars of the validated use cases (new field `frontier_pillar`) | Multi-select; you confirm |
| DEBRIEF · Discovery & Insights | Three to five insights from the validated blueprint and the register (pains, KPIs, constraints, decisions), with W-ids | Short, factual, internal |
| DEBRIEF · Handover | Owner of the first follow-on step → ATU, STU, CSU, ISD, ISE/FDE, Partner or Other | Single-select |
| DEBRIEF · What worked well? / What did not work well? | Not in the blueprint; you answer, prompted by the end of the transcript | Your voice |
| DEBRIEF · New opportunities discovered | MVP options and horizon-1 use cases not yet linked to an MSX opportunity, tagged #NEW or #UNVERIFIED | Account-team-only |
| Conversations; Next Steps & Timeframe | — | Retired: never written |

**Default pillar for `frontier_pillar`** (a person always confirms it):

| The use case mainly… | Default pillar |
|---|---|
| Helps employees do their work (assistants, copilots, knowledge) | Enriching employee experiences |
| Changes how customers, partners or suppliers are served | Reinventing customer engagement |
| Re-plumbs an end-to-end process with agents | Reshaping business processes |
| Creates new products or services, or speeds up R&D | Bending the curve on innovation |

**Example closeout pack.** It uses labels, not codes; HubWorks resolves the codes live.

```json
{
  "schema": "frontier-closeout/1.0",
  "engagement_number": "000xxxxx",
  "blueprint_version": "1.2 (validated)",
  "outcomes": [
    { "label": "Use cases + prioritization matrix", "file": "frontier/<Customer> Frontier Company Blueprint.html", "evidence": ["W01", "W02"] },
    { "label": "Solution mapping", "file": "frontier/<Customer> Frontier Company Blueprint.html" },
    { "label": "Next steps", "evidence": ["W02"] }
  ],
  "frontier_success_framework": [
    { "label": "Reshaping business processes", "use_cases": ["uc-01"] },
    { "label": "Enriching employee experiences", "use_cases": ["uc-02"] }
  ],
  "discovery_insights": [
    { "text": "<insight>", "evidence": ["W01 00:42:10"], "visibility": "internal" }
  ],
  "handover": { "label": "STU", "reason": "<who owns the architecture session and prototype>" },
  "new_opportunities": [
    { "text": "#NEW <MVP option>", "visibility": "account-team-only", "evidence": ["W02 01:12:30"] }
  ],
  "agenda": "hubworks/<agenda file>",
  "excluded_fields": ["Conversations", "Next Steps & Timeframe"]
}
```

### 7.3 Consistent outcomes check

| Engagement type | Required output | Frontier artefact | Gap and extension |
|---|---|---|---|
| Business envisioning | Up to 5 use cases, 2 slides each | Blueprint use-case portfolio | Slides missing → F-07 outcome pack |
| Business envisioning | Prioritisation matrix | Value × feasibility view | Slide export → F-07 |
| Business envisioning | Next steps | `next_steps` | Slide export → F-07 |
| Solution envisioning | Solution mapping | Agents and journeys mapped to Microsoft technology (solution view) | Slide export → F-07 |
| Architecture design | Architecture diagram and decisions document | Target-architecture layers and ADRs from the solution design | Diagram drawn by architecture-diagram-builder (H-06) |
| Rapid prototype | Code + configuration | Out of scope of Frontier 1.0.1 | Link the prototype repository or solution in `outcomes.evidenced` |
| All types | Agenda | Agenda blocks → agenda-builder | H-03 and F-06 |

Before it writes the closeout pack, a new orchestrator gate compares the planned outcomes of the engagement type with what exists in the folder.

### 7.4 Opportunities and customer journeys

- **MVP options become opportunities.** Link to an existing MSX opportunity when CE Hub or the account team names one. Otherwise tag #NEW (new idea) or #UNVERIFIED (not yet checked), visible to the account team only.
- **journey-update records the follow-on path** (architecture design → rapid prototype → pilot), with owners and dates from `next_steps`.
- **Director reporting can then show** which engagements produced which Frontier pillars and outcomes, and the gap between engagements and attached opportunities narrows.

---

## 8. Extension backlog

### 8.1 Proposed HubWorks changes (pull requests)

| ID | Skill | Change | Effort | Phase |
|---|---|---|---|---|
| H-01 | engagement-initiator | Write `engagement.json` (`hub-engagement/1.0`) with the CE Hub block into the engagement folder; stamp the CE Hub number into meeting subjects | S–M | 1 |
| H-02 | engagement-initiator | "Frontier envisioning" engagement type (task template set): precall, context discovery, hypothesis blueprint, agenda, workshop, transcript archive, consolidation, closeout, design | S | 1 |
| H-03 | agenda-builder | Accept `handoff/agenda-blocks.json` (sessions, timings, objectives, discovery questions) | S | 1 |
| H-04 | engagement-closeout | Read `handoff/closeout-pack.json`; pre-select Outcomes, Frontier Success Framework and Handover; draft Discovery & Insights with evidence ids; keep live option resolution and the native completion button | M | 2 |
| H-05 | engagement-closeout or a new skill | Transcript archive step shared with Frontier (rules R1–R5, `transcripts/index.json`) | M | 2 |
| H-06 | architecture-diagram-builder | Accept the blueprint `architecture` block (layers, blocks, flows) as input | S–M | 2 |
| H-07 | lighthouse anonymizer | Accept the blueprint JSON and the Frontier customer build (internal terms, alias map) | S | 2 |
| H-08 | hub-feedback | Cover the Frontier skills; label issues `frontier` | S | 2 |
| H-09 | journey-update | Accept next steps and MVP options from the closeout pack | S | 3 |

### 8.2 Frontier Envisioning changes (1.7 and 1.8)

| ID | Change | Detail | Effort | Release |
|---|---|---|---|---|
| F-01 | Engagement link | Orchestrator Step 1 reads `engagement.json` from the engagement folder. If it is absent, asks once for the CE Hub number and URL. Never queries CE Hub itself. | S | 1.7 |
| F-02 | Folder alignment | Save into `<engagement folder>/frontier/` by uploading into that folder; the Cowork folder is only the fallback | M | 1.7 |
| F-03 | Transcript harvest | Rules R1–R5, multi-part merge, language tag, internal/customer classification, archive and W-ids | M | 1.7 |
| F-04 | Schema 1.1 | Adds `meta.cehub`, `use_cases[].frontier_pillar`, `next_steps[].handover`, `mvp_options[].opportunity` (MSX id, #NEW or #UNVERIFIED), `outcomes_evidenced[]` and `evidence[].meeting` | S | 1.7 |
| F-05 | Closeout pack | New script: blueprint + register → `closeout-pack.json` and a review markdown. Labels only, retired fields excluded, with self-test cases. | M | 1.7 |
| F-06 | Agenda blocks | New script: method agenda + journeys + discovery questions → `agenda-blocks.json`. Frontier stops rendering its own agenda when HubWorks is present. | S | 1.7 |
| F-07 | Hub outcome pack | Standard slides from the blueprint: up to 5 use cases (2 slides each), prioritisation matrix, solution mapping, next steps | M | 1.8 |
| F-08 | Routing hygiene | "Do NOT use for…" lines naming agenda-builder, engagement-closeout, schedule-meetings and architecture-diagram-builder; conflict scan with both plugins enabled | S | 1.7 |
| F-09 | Engagement IQ adapter | Convert live-captured decisions and answers into the `frontier-blueprint-feedback` format | M–L | Later |
| F-10 | Adoption signals | Lynx (M365 and Copilot usage) and MSX as internal evidence for the blueprint's current Frontier phase | M | Later |
| F-11 | Repository fit | HubWorks layout, CHANGELOG and licence alignment; SKILL.md under 20,000 characters (today 7.5k–10.7k) | S | 1.8 |

### 8.3 Shared standards

| ID | Standard | Content | Partners |
|---|---|---|---|
| S-01 | What excellence looks like | Machine-readable criteria for solution-envisioning and architecture-design outputs: method phases and gates, the seven declarations, HAIRO roles, question bank, target-architecture layers | Powlo (Hub engagement guides), HubWorks core team, Engagement IQ |
| S-02 | CE Hub field mapping | Plan & Debrief fields mapped to outcome artefacts and option labels; versioned, updated whenever the form changes | Jay Leask, HubWorks core team |
| S-03 | Engagement and evidence schemas | `hub-engagement/1.0`, the evidence register and the transcript index | HubWorks core team, Engagement IQ |
| S-04 | Transcript conventions | Meeting naming with the CE Hub number, archive timing, retention | Hub operations |

S-01 fits an initiative already under way. On the 12 Oct call, Powlo proposed machine-readable "what excellence looks like" definitions, starting with the qualification call, the customer call and the business envisioning output. The point is that HubWorks and Engagement IQ stop encoding one person's opinion. The Frontier method is a ready contribution for the solution-envisioning and architecture-design outputs.

---

## 9. Packaging, distribution and governance

**Release path.**

| Step | Where | Who uses it | Exit criterion |
|---|---|---|---|
| 1 | Personal skills in the author's Cowork (today, 1.0.1) | The author and the Swiss Hub pilot | Pilot engagement closed out end to end |
| 2 | Pull request to the HubWorks repository as a separate package folder, released on the dev channel | HubWorks champions | Two Hubs ran it on real engagements; hub-feedback items triaged |
| 3 | Official catalogue release in the monthly HubWorks cadence | All Hub SEs who opt in | Access group and release request in place (allow for the two-to-three-day publish lag and one request at a time) |

**Repository fit.** HubWorks accepts skills, not applications. Frontier's helper scripts are standard-library Python inside the skill folders. Confirm with the maintainers that this fits; shared Python helpers already exist in the CLI toolkit. Keep anything like an MCP server out.

**Licence.** Frontier is MIT-licensed with the author as copyright holder. The HubWorks repository sits in an internal Microsoft organisation with its own terms. Before the first PR, decide whether the contribution moves under the repository's terms. Check with the repository owners, and with CELA if a public variant stays MIT.

**Security and privacy.**

- **CE Hub data:** CE Hub data and qualification notes are Microsoft-internal. They stay internal evidence and never reach a customer build.
- **CE Hub writes:** only through HubWorks, after your confirmation. Completion stays with the native button.
- **Customer mail:** always a draft.
- **Engagement state:** kept in files, not in Cowork memory, which is small and shared across all your work.
- **Dynamics 365 Sales plugin:** a prerequisite for CE Hub access. Frontier must keep working when it is off.

**Support.**

- **Issues:** hub-feedback.
- **Questions:** the champions chat.
- **Releases:** the monthly call.

---

## 10. Roadmap

| Phase | When | Deliverables | Done when |
|---|---|---|---|
| 0 Align and verify | 22 Oct – 6 Nov 2026 | Run HubWorks with the Dynamics 365 Sales plugin on a recent Swiss engagement to verify the CE Hub fields and the folder; share this analysis with the HubWorks core team; agree the contract (S-03) and the A → B path | Contract agreed; assumptions verified |
| 1 Connect | By 20 Nov 2026 | Frontier 1.7 (F-01 to F-06, F-08); PRs H-01 to H-03; meeting naming convention in the Swiss Hub; pilot on one engagement | Pilot closed out from the closeout pack, with no re-keying |
| 2 Contribute | Dec 2026 – Jan 2027 | HubWorks Frontier package on the dev channel; H-04 to H-08; F-07; standards S-01, S-02 and S-04 | Two Hubs using it; closeout field accuracy confirmed by the CE Hub owners |
| 3 Scale | From Feb 2027 | Official catalogue release; Engagement IQ adapter (F-09) once it is cleared for customer use; Lynx and MSX signals (F-10); Director reporting on Frontier outcomes | Monthly releases include Frontier; adoption tracked |

**Proposed pilot: a recent procurement envisioning engagement in the Swiss Hub.**

- **It has the inputs:** the workshop day has two transcript parts and a blueprint mockup.
- **It covers every outcome type:** the agreed next steps (PRD, architecture session, rapid prototype on Copilot Studio) exercise all of them.
- **It stays internal:** real data only under the customer's NDA.

**Success measures.** Take the baseline in the pilot, then set targets.

| Measure | Definition |
|---|---|
| Re-keying | Number of CE Hub facts typed by hand in Frontier (aim: zero) |
| Closeout completeness | Share of Frontier engagements whose Outcomes, Frontier Success Framework and Handover come pre-filled with evidence |
| Transcript coverage | Share of engagement meetings archived and parsed within five working days |
| Consistent outcomes | Share of envisioning and architecture-design engagements that deliver the full standard outcome set |
| Effort | Hours for preparation and for closeout per engagement, before and after |
| Reuse | Number of anonymised Frontier patterns published |

---

## 11. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| The CE Hub connection in Cowork drops (Dynamics 365 Sales plugin off; outages as on 11 Aug) | High | Medium | Prerequisite check (PR #281); Frontier never blocks; manual engagement number |
| HubWorks distribution hiccups (access group, publish lag) | Medium | Medium | Pilot on the dev channel; align with the monthly cadence |
| The CE Hub form changes again | Medium | Medium | Labels, not codes; live resolution in HubWorks; versioned mapping (S-02) |
| Routing conflicts between the plugins | Medium | Medium | Explicit "Do NOT use for…" lines; conflict scan with both plugins enabled |
| Scope creep in HubWorks | Medium | Medium | Separate, opt-in package |
| Transcript gaps (tours, whiteboards, side conversations, meetings you did not attend, older than 60 days) | High | Medium | Nudges; archive early; notes and photos as secondary evidence |
| Confidential data reaches a customer document | Low | High | Visibility on every item; the customer build refuses internal terms; opportunities stay account-team-only |
| Engagement IQ not cleared for customer engagements | Medium | Low | Keep it to internal and pilot use until the guidance changes |
| Licence mismatch (MIT vs repository terms) | Medium | Low | Decide before the first PR |
| Two folder conventions persist | Medium | Low | `engagement.json` pointer; migration note in the README |

---

## 12. Decisions needed

| # | Decision | Proposed owner |
|---|---|---|
| 1 | A separate HubWorks Frontier package, or a folder in the SE package | Brendon Colburn, Rich Ross |
| 2 | Where the shared contract and standards live (a repository folder or the knowledge vault) | Rich Ross, Bryan Roberts, Powlo |
| 3 | Which engagement types get the Frontier task set (Envisioning Workshop, Architecture Design Session, others) | Hub leadership |
| 4 | Frontier Success Framework rule: per use case or per engagement | Jay Leask |
| 5 | Handover rule when several teams follow on | Jay Leask |
| 6 | Transcript archive location and retention | Hub operations |
| 7 | Timing of the Engagement IQ interop, and its use in customer engagements | Andreas Krüger |
| 8 | Licence for the contributed code | Repository owners |
| 9 | Whether CE Hub can store session meeting links, which would make rule R2 exact | CE Hub team |

---

## 13. Next steps (author)

1. **Verify:** turn on HubWorks and the Dynamics 365 Sales plugin in a Cowork chat, and run engagement-initiator on a recent Swiss engagement. Note the fields and the folder it creates; this verifies sections 2.1 and 7.1.
2. **Pick the pilot:** choose the pilot engagement and confirm the NDA scope.
3. **Share:** post this analysis in the Tools-AI-HubWorks channel and ask for a slot in the November monthly call.
4. **Build:** build Frontier 1.7 (F-01 to F-06, F-08) so the pilot can start.
5. **Align:** on standards with Powlo, on the closeout mapping with Jay Leask, and on live capture with Andreas Krüger.

---

## Appendix A — HubWorks skill catalogue

| Package | Skills |
|---|---|
| Cowork SE package (as installed in the author's Cowork) | agenda-builder, architecture-diagram-builder, cehub, cet-catalog-search, customer-story-writer, engagement-closeout, engagement-initiator, hubworks, journey-update, schedule-meetings, hub-feedback |
| HubWorks-Director (Cowork, since the October sprint) | Director-facing skills, split out of the SE package in PR #262 |
| CLI toolkit | agenda-builder, architecture-diagram-builder, cehub-account-search, cehub-my-engagements, cet-catalog-search, code-app-builder, customer-insights, engagement-closeout, engagement-initiator, followup-email, hub-insights, journey-promoter, journey-update, lesson-lifecycle, task-generator, toolkit-setup; also hub-business-audit, engagement-trends, solutionarea-trends, cehub-resource-availability, release-summary |
| Community contributions in flight | Lighthouse architecture anonymizer (UK Hub); engagement qualification (NL Hub); Lynx-based insights (proposal) |

The CLI toolkit shares one configuration file, `~/.innovation-hub/config.json`. It holds the CRM user id, hub, team, audit workspace and CRM base URL. CE Hub and MSX are reached as Dataverse through shared Python clients.

## Appendix B — CE Hub Plan & Debrief reference (14 Oct 2026)

| Field | Logical name | Type | Options (value — label) |
|---|---|---|---|
| Outcomes | `cet_outcomes` | Multi-select | 766100000 Use cases + prioritization matrix · 766100001 Solution mapping · 766100002 Architecture · 766100003 Code + configuration · 766100004 Next steps |
| Frontier Success Framework | `cet_usecase` (relabelled) | Multi-select | 766100000 Enriching employee experiences · 766100001 Reinventing customer engagement · 766100002 Reshaping business processes · 766100003 Bending the curve on innovation |
| Handover | `cet_hubhandover` | Single-select | 766100000 ATU · 766100001 STU · 766100002 CSU · 766100003 ISD · 766100004 ISE/FDE · 766100005 Partner · 766100006 Other |
| Solution Area | `cet_solutionareadomains` | Multi-select | Read live |
| Industry | `cet_industry` | Choice | Codes are non-sequential; read live |
| Conversations (retired) | `cet_frontierconversations` | — | Never write |
| Next Steps & Timeframe (retired) | `cet_provideguidanceonnextstepsandtimeframe` | — | Never write |

Option sets are read from the Dataverse string maps of the engagement table (`msevtmgt_event`). Always resolve them live; the values above are a snapshot.

## Appendix C — Sources

**Tools-AI-HubWorks channel (HubTechCommunity team):**

- "Engagement Initator Skill – CE Hub Lookup PR #175" (Jay Leask, 8 Jun 2026)
- "Directional Change Incoming" (Brendon Colburn, 24 Jul 2026)
- "Engagement IQ – Turn every live conversation into intelligence you can act on" (Andreas Krüger, 30 Jul 2026)
- "HubWorks is not connecting to CEHUB, help amplify" (Brendon Colburn, 11 Aug 2026)
- "HubWorks update — closeout gets smarter, agendas get easier" (Brendon Colburn, 31 Aug 2026)
- "HubWorks: CEHub MCP Server removed (PR #222 rolled back)" (Rich Ross, 3 Sep 2026)
- "Pinoccio is now a real boy": HubWorks 1.0 as an official Cowork plugin (Brendon Colburn, 16 Sep 2026)
- "CEHub Issues via Scout Desktop?" (Chris Bortlik, 28 Sep 2026)
- "Hub Feedback: engagement-closeout is out of sync with the CE Hub Plan & Debrief form" (Jay Leask, 14 Oct 2026)
- "HubWorks Skill Enhancement Idea – Pulling in Lynx Information" (Chris Bortlik, 14 Oct 2026)

**Meetings and documents:**

- Innovation Hub – HubWorks Monthly Call, 12 Oct 2026 (meeting transcript)
- HubWorks October 2026 sprint summary (Rich Ross), covering PRs #262, #272, #274, #277 and #281
- Hubworks_Tool_Comparison_Guide (Ali Mazaheri, HubTechCommunity)
- Engagement Guides – Hub SE and Manager Overview (MTC Readiness, Nov 2025) and aka.ms/hub/guides
- CEHub MSX Request Integration – Business Requirements (ProjectX-NewCETPlatform)
- Frontier Envisioning Plugin – PRD and Solution Design 1.0.1 (22 Oct 2026)
- The author's calendar, meeting transcripts and OneDrive engagement folders, 23 Aug – 22 Oct 2026
