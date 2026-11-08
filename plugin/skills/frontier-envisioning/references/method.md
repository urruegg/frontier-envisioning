# The Innovation Hub Frontier envisioning method

## 1. Purpose

Help a customer see, in its own terms, how a journey, a function or the whole company could run **human-led and agent-operated**, and leave the workshop with an evidenced blueprint, MVP candidates with owners, and a design path. The method combines:

- the HAIRO organisation model (Human-AI Role Organisation, Journai showcase): people in the centre, lead agents, specialist agents, departments, tools, role cards and role profiles, an agent lifecycle run by Intelligence Resources;
- Microsoft's Frontier Firm concepts (agent boss, human-agent ratio, the three phases) and Microsoft's agent architecture guidance (Cloud Adoption Framework, Azure Architecture Center patterns, Agent 365, Entra Agent ID, Microsoft IQ);
- the Innovation Hub's design-repository practice: platform requirements once, workflow-first, systems of record authoritative, seven declarations per agent.

## 2. Phases, artefacts and gates

| Phase | Skill | Artefacts | Gate |
|---|---|---|---|
| 0 Frame | frontier-envisioning | Scope, sponsor, workshop date, NDA status | Scope agreed with the account team |
| 1 Discover | frontier-context-discovery | `customer-context.json`, evidence log | A: no validation errors; at least one transcript or the gap stated |
| 2 Hypothesise | frontier-blueprint | Blueprint JSON and HTML v0.x (internal): Part 1 Vision with the Agent Factory journey and attendees, Part 2 Design with landing zone, ADRs, use cases, IT readiness | B: build clean; MVP candidates have canvas and seven declarations |
| 3 Prepare | frontier-blueprint, frontier-envisioning | Customer version, agenda, top questions | Customer version strips internal evidence |
| 4 Workshop | (live) | Notes and verdicts exported from the HTML; transcript | Feedback exported before the room empties |
| 5 Consolidate | frontier-context-discovery, frontier-blueprint | Blueprint v1.0 validated, workshop summary | C: MVPs confirmed by the customer; owners named |
| 6 Design | frontier-solution-design | PRD, solution design, ADRs (optionally a repository) | D: Definition of Ready met or gaps assigned |
| 3b Value and cost | frontier-value-case, frontier-finops | Value case (value tree, assumption register, NPV, ROI, payback) and cost model per agent (credits, licences, Azure, people, purchase options) shown in the blueprint | V1 value hypothesis complete; F1 cost model complete (rates no older than 90 days) |
| 6a Value validated | frontier-value-case, frontier-finops | Workshop verdicts merged; guardrails and purchase model for the design | V2 top-5 assumptions confirmed by owners; F2 guardrails with owners; V3 baseline before go-live |
| 6b Identity | frontier-agent-identity | Approve the agent identity kit (a first proposal is built with every blueprint): naming convention, colours, icons, catalogue, stamp and validate scripts | E: validator 0 errors; tests pass; naming decisions listed with owners |
| 6c Architecture design | frontier-blueprint, frontier-solution-design | IT readiness checklist (P-, R-, W-, Q-, D-), landing zone per journey, ADRs agreed, engineering control plane decided | R: readiness checks for the prototype stage passed; D-01 decided; MVP agents ready for build |
| 7 Handover | frontier-envisioning | Handover package per MVP agent (Definition of Ready), prototype plan in the Agent Factory | Owners and dates agreed |

## 3. Timeline (typical)

| When | What |
|---|---|
| Workshop minus 10 working days | Frame; request access to meetings and documents; NDA status |
| Minus 7 | Discover; context pack v1 |
| Minus 5 | Blueprint v0.1 internal review with the account team |
| Minus 2 | Customer version; agenda; question list |
| Workshop day | Present, validate, capture; export feedback at the end of each block |
| Plus 1 | Merge feedback; workshop summary; blueprint v1.0 |
| Plus 5 | PRD and solution design draft 0.1; architecture session invite |
| Plus 5 to 10 | IT readiness items sent (architecture workshop minus 10 working days) |
| Architecture design workshop | Landing zone, ADRs and readiness decisions; verdicts merged; MVP agents ready for build |
| Before the first DEV save | Agent identity kit v1.0: MVP names and publisher prefix confirmed |

## 4. Workshop agenda (one day, adapt to half a day)

| Block | Duration | Blueprint view | Output |
|---|---|---|---|
| Why we are here: mission and the Frontier phases | 30 min | Overview | Mission confirmed or reworded; phase today and target |
| The hybrid organisation | 45 min | Org model, Blueprint | Journeys and lead agents confirmed; agent bosses named |
| Journeys deep-dive (one per break-out) | 90 min | Journeys, Agents | Stages, pains, agents validated or adjusted |
| Portfolio and MVP choice | 45 min | Use cases, Roadmap | Scores agreed; 2 MVP candidates selected |
| MVP agent canvases | 60 min | Agents (canvas, seven declarations) | Canvas and declarations completed live |
| Architecture and governance | 45 min | Target architecture | Build choice, identity, data access, open decisions |
| Discovery questions and next steps | 30 min | Discovery, Roadmap | Answers captured, owners and dates |

## 5. Roles

| Role | Responsibility |
|---|---|
| Facilitator (Innovation Hub solution engineer) | Method, blueprint, live capture, design |
| Account team | Access, sponsor alignment, commercial context (internal only) |
| Customer sponsor | Mission, priorities, MVP decision |
| Customer process owners | Journey validation; become agent bosses |
| Customer IT and security | Architecture, identity, data access, governance |
| Works council or data protection (where relevant) | People-decision surface, voice or location data, retention |

## 6. Naming

Agent names follow the identity kit's rule `<PO> <Domain> [Scope] [DEV|TEST]` (frontier-agent-identity); blueprint working names such as "Service Report Agent" stay in the blueprint as `workingName`.

"Frontier Company Blueprint" is the Hub's method name. Microsoft also uses "Frontier Firm" (Work Trend Index), "Frontier Suite" (Microsoft 365 E7), "Frontier program" (early access) and "Microsoft Frontier Company" (a services unit). Say which one you mean in customer material.

## 7. The Innovation Hub journey in the blueprint

| Hub session | Blueprint part | Views used |
|---|---|---|
| Business envisioning | Part 1 Vision | Overview, Org model, Blueprint, Journeys (business journeys and the Agent Factory), Attendees |
| Solution envisioning | Part 2 Design | Agents, Agent identity, Use cases (problem, value, feasibility), FinOps |
| Architecture design | Part 2 Design | Target architecture (landing zone, layers, flows, ADRs), IT readiness |
| Rapid prototype and build | Agent Factory | Factory board and handover table: hypothesis, validated, designed, ready for build, build, release, operate |

The Agent Factory journey is the same for every customer: specification-driven development with GitHub Copilot (or the customer's Azure DevOps), evaluations as the definition of done, security review, release with human approval and operations with Agent 365. Reusable CAT agent skills (MIT) are named per factory step; check them on their site before use.
