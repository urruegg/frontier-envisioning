# Authoring guide: writing the Frontier hypothesis

The blueprint is a hypothesis, written so the customer can correct it. Good hypotheses are specific, evidenced where possible, honest where not, and small enough to discuss in a workshop.

## 1. The model in one picture

| Layer (HAIRO) | In the blueprint | Microsoft Frontier term |
|---|---|---|
| Human-led centre | `leaders`: the accountable roles who set direction and own agents | Human-led, agent-operated; agent boss |
| Lead agents (inner ring) | `domains[].orchestrator`: one per journey, the only agent people talk to | Orchestrator agent |
| Specialist agents (outer ring) | `domains[].agents`: 3 to 6 per journey | Specialist agents, digital colleagues |
| Departments (outer arcs) | `domains`: journeys or functions | Work Chart: outcome-based teams |
| Tools around the circle | `domains[].systems` | Systems of record, connectors, MCP |
| Role card and role profile | agent fields, `profile` (9 sections) | Agent charter and instructions |
| Lifecycle | `lifecycle`: Planned, Prototype, Pilot, Active, Upskilling, Retired | Agent lifecycle (Agent 365 registry) |
| Intelligence Resources | `intelligence_resources` | IT and HR jointly managing digital labour |

## 2. Journeys and stages

- 3 to 6 journeys for a company, 3 to 5 inside one function; name them as verbs-to-outcomes ("Source-to-Pay", "Request-to-Resolution").
- 4 to 6 stages per journey. Each stage has: what happens today, the pain (cite `src`), what changes with agents, the owning agent (or "workflow" when no reasoning is needed).
- Write pains as observable facts ("quotes take five to eight days"), not opinions.

## 3. Agents

**Lead agent.** Mission (one sentence), memory (what it remembers across runs), planning (how it chooses the path), goals (the KPIs it plans against), agent boss (a role).

**Specialist agents.** Name by the job ("Service Report Agent"), not by the technology. One clear capability each. 3 to 6 per journey; if you need more, the journey is too broad or some are workflows.

**Workflow-first test.** Ask for every step: could a rule do it the same way every time? Then it is a workflow step with an optional agent node for the exceptions. An agent placed where a rule belongs is less governable, not more agentic.

**Autonomy levels** (Innovation Hub synthesis, anchored in Microsoft's productivity / action / automation agent types and risk tiers):

| Level | Label | Use when | Seam |
|---|---|---|---|
| 1 | Assist | The output informs a person who acts | The person decides and acts |
| 2 | Act with approval | The agent prepares a state change | A person approves before any write |
| 3 | Act within guardrails | High volume, low risk, reversible, clear mandate | People handle exceptions and audit |

Start one level lower than the customer's ambition; autonomy is earned with evidence from the pilot.

**Horizons.** H1 now (0 to 6 months, Microsoft 365 Copilot and Copilot Studio with existing data), H2 next (6 to 18 months, orchestrated agents integrated with systems of record and data products), H3 later (bounded autonomy).

**Lifecycle.** New hypotheses are `Planned`. Use `Prototype` or `Pilot` only when something exists.

## 4. The seven declarations (required for every MVP candidate)

| Declaration | The question it answers |
|---|---|
| write_envelope | Which systems and fields may it change, under which conditions? Never writes outside it. |
| refusal_set | When does it stop, and how does it record why? |
| escalation_path | Which named role does it hand over to, and through which channel? |
| grounding_sources | What may it read and cite? |
| data_classification | How sensitive is the data it touches? |
| people_decisions | Does its output shape decisions about people? Who decides? |
| measurement | How are success, quality and cost measured? |

An agent that cannot answer all seven is not ready to build, whatever its priority.

## 5. Trigger canvas (MVP candidates)

`trigger` (events or schedules), `instructions` (identity, scope, limits, in plain language), `plan` (5 to 8 steps), `outcome`, `data_sources`, `connectors` (who holds them: the workflow, not the agent, for writes), `approval` (each seam), `autonomy`, `skills` (reusable instruction sets or scripts), `pattern` (sequential, concurrent, group chat, handoff, magentic), `build` (Copilot Studio, Foundry, Agent Framework, Microsoft 365 Copilot).

### 5a. Workflow: from trigger to outcome (MVP candidates)

Under the trigger canvas the plan is drawn as a **Copilot Studio workflow**, the way a maker builds it in the workflow designer (powered by the GitHub Copilot harness): a trigger, typed nodes, branches, and the desired outcome. A plan without an authored workflow is turned into one by rule on every build and marked "Derived from the plan"; for each MVP candidate, author `canvas.workflow` in the workshop or right after it:

1. **Trigger**: what starts it, with the official trigger type: Manual, Recurrence, Connector event (name the system and the event), When an HTTP request is received, or When an agent calls the workflow (the agent hands over after the conversation; end with Respond to the agent).
2. **Deterministic first**: Variable, Connector (read and write in the connected system, `system` names it), Function (code), If/Else, Loop and Scope wherever a rule can do the work. Writes are connector steps held by the workflow, never by the agent.
3. **AI steps only where reasoning is needed**: Agent (the agent itself, `agent` = its id), Classify (route by category: list the categories as `defaults`, the special path as a branch), Extract (fields and tables from documents and photos), Copilot (Microsoft 365 Copilot, Researcher, Analyst or Cowork for open research or drafting). Their results can vary: say what checks them.
4. **People decide**: a Human review before every write that leaves the company or affects a person (approval or request for information; `approver` names the role). Branches show what happens on "Changes needed" or "Missing" (rejoin, or end at a named end node).
5. **Outcome**: the measurable result, in the customer's words (use the KPI of the journey).
6. **Notes** for the decisions behind a step (who holds a connection, which expert approves new knowledge).

Keep labels short (about 20 characters, two lines at most); the detail goes into `detail`. The build lists AI, deterministic and human steps in the workflow bar and warns about unknown node types or agents. The solution-design scaffold turns each MVP workflow into the build table of the process design.

The agent selector remains sticky only within the upper summary and trigger canvas. The full-width workflow follows below that boundary, so its node-type legend remains visible and receives pointer and keyboard input when scrolling.

## 6. Role profile (nine sections)

1. Starting point & contribution (starting_point, contribution, impact)
2. Mission & output (mission, trigger, input, output)
3. Tasks
4. Team & leadership (reports_to, works_with, hands_off_to)
5. Interaction & autonomy (autonomous, approval, escalation)
6. Knowledge, rules & limits (knowledge, rules, not_allowed)
7. Systems & channels
8. Communication & personality (tone, language)
9. Success & measurement (kpis)

The role profile becomes the agent's versioned instructions.

## 7. Scoring use cases

| Score | Value (business impact) | Feasibility (can we build it now?) |
|---|---|---|
| 5 | Large, measurable, strategic; many users daily | Data and APIs available; low risk; reversible; Copilot Studio fit |
| 4 | Clear KPI impact for one journey | Minor integration or data work |
| 3 | Useful, moderate impact | Real integration work or data quality to fix |
| 2 | Nice to have | Dependent on a programme (ERP, data platform) |
| 1 | Unclear | Not possible today |

Quadrants: Quick wins (value 3 or more, feasibility 3 or more), Invest (high value, low feasibility), Test and learn, Park.

**MVP selection.** Prefer: a narrow, reversible write after a human confirms; a daily pain for many people; data the customer can share under NDA; a second MVP in another journey that proves reuse of the platform; nothing that decides about people.

**Use-case template (MVP candidates and anything shown in detail).** Follow the Hub business-envisioning template the workshops use:
- **General**: the problem statement as provenance pairs, so the room sees where each sentence comes from: `["workshop", "…"]`, `["transcript", "…"]`, `["customer", "…"]`, `["microsoft", "…"]`, `["hypothesis", "…"]`; then today, the pain and the idea.
- **Value**: objective, two or three key results, figures only with their source, the personas affected and why the value proposition appeals; the business value block comes from frontier-value-case.
- **Feasibility**: technical fit, change resistance, timeframe, risk with safeguards, dependencies on programmes or data.

## 7a. Attendees, Agent Factory, landing zone and IT readiness

- **Attendees**: one card per person who shaped the hypothesis: role, organisation, the journeys and use cases they spoke to, and what they contributed (cite the transcript or notes). Microsoft people too. Use names only with consent.
- **Agent Factory**: keep the canon journey; it is how every agent goes from hypothesis to operate. Adapt the build steps to the customer's tools only when they have decided; the control plane stays open (GitHub, Azure DevOps or both) until decision D-01.
- **Landing zone**: per journey, mark DEV, TEST and PROD as now, next or later, and the data classes allowed. Keep the CAF areas generic; add customer systems through the journeys.
- **ADRs**: the canon ADRs (ADR-F01…) are a starting position the workshop confirms or adapts; customer decisions get their own ids. Write context, decision, consequences and alternatives.
- **IT readiness**: send the preparation items before the architecture design workshop; record owners and status; the readiness checks (R-) prove the setup before the prototype.

## 7b. Digital feedback loop (Overview)

The Overview explains the data-driven part of the hypothesis with Microsoft's digital feedback loop: **signals → Microsoft IQ → proposed action → human approval → measured outcome**, and the outcome becomes the next signal. Write it in the customer's context, from the discovered evidence:

1. **Map every business journey to one of the four areas**, with the official names: Engage customers, Optimize operations, Empower employees, Transform products. The canon proposes a mapping by keyword; correct it (a service journey can engage customers, empower technicians or transform products). An area without a journey stays "To be discovered" and becomes a workshop question.
2. **Signals: what already exists, where, through which Microsoft IQ layer.** Work IQ for work signals in Microsoft 365 (requests, meetings, chats, files, people, skills); Fabric IQ for business data and live operational signals (ERP, CRM, HR systems, telemetry, modelled as business entities); Foundry IQ for organisational knowledge (manuals, policies, contracts, templates as knowledge bases); Web IQ for public, fresh information (company news, markets, regulation, suppliers). Name the customer's systems; cite the transcript or mail that mentions them.
3. **Actions: what agents propose, and the person who approves.** Link the agents by id; take the approval from the journey's approval seam. Nothing leaves the company without a person signing it off.
4. **Outcomes: what is measured, and how it feeds back.** Use the journeys' KPI names (baseline and target are shown) and the value-case assumption ids, so the hypotheses to confirm appear next to the outcome. One outcome per area should say how the result returns as a new signal.
5. **Workshop question per area**: the one question that confirms or rejects the area. Verdicts are captured live and merged as `loop:<area>`.

Use only official Microsoft names: Microsoft IQ, Work IQ, Fabric IQ, Foundry IQ, Web IQ, and the product names (Microsoft 365 Copilot, Microsoft Fabric, Microsoft Foundry, Microsoft Copilot Studio, Microsoft Entra, Microsoft Purview, Microsoft Agent 365). Never invent an "… IQ" (the build warns). Keep the card lines short (about 40 characters); details go into the lists.

## 8. Writing style

- Plain business language; sentences under 25 words; the customer's vocabulary.
- Numbers only from evidence, with `src`; estimates say "estimate".
- Every statement Microsoft proposes stays `status: hypothesis` until the workshop validates it.
- Product names exactly as Microsoft writes them; anything not verified is "to confirm".

## 9. Journey pattern library (starting points, adapt to evidence)

| Journey | Typical stages | Lead agent | Candidate specialists |
|---|---|---|---|
| Source-to-Pay | Need & intake, Source & negotiate, Contract, Order & receive, Invoice & pay | Procurement Lead Agent | Guided Buying, Tail Spend Negotiation, Contract Compliance, Supplier Risk, Invoice Exception |
| Lead-to-Order | Signal & lead, Discover & qualify, Configure & quote, Negotiate & close, Order & handover | Commercial Lead Agent | Lead Qualification, Account Research, Quote Builder, Deal Desk, Order Handover |
| Request-to-Resolution | Detect & request, Diagnose, Plan & dispatch, Fix on site, Report & learn | Service Lead Agent | Service Triage, Remote Diagnostics, Dispatch Planning, Technician Assistant, Service Report |
| Record-to-Report | Capture & post, Reconcile, Close, Analyse & explain, Report & audit | Finance Close Lead Agent | Close Cockpit, Reconciliation, Variance Analysis, Audit Evidence |
| Hire-to-Retire | Plan & attract, Select, Pre-board & onboard, Develop, Offboard | People Lead Agent | Job Description, Candidate Communication, Master Data Completion, Onboarding Assistant, Policy Assistant |
| Plan-to-Deliver | Demand sensing, Supply planning, Production scheduling, Logistics, Exceptions | Supply Chain Lead Agent | Demand Signal, Supply Risk, Schedule Proposal, Shipment Exception |
| Incident-to-Resolve (IT) | Intake, Triage, Diagnose, Resolve, Learn | IT Service Lead Agent | Ticket Triage, Knowledge, Remediation Proposal, Problem Analysis |
| Contact-to-Resolution (customer service) | Contact, Understand, Resolve, Follow up, Learn | Customer Care Lead Agent | Intent & Routing, Case Summary, Answer Drafting, Follow-up |
