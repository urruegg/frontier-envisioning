# The HAIRO model and the Frontier Firm

The Human-AI Role Organisation model (HAIRO), shown in the Journai showcase ("How we work at Journai: Human-led, Agent-operated" and "How we built our hybrid organisation"), describes a company as one organisation with two halves and a seam between them. The blueprint uses it as the visual and conceptual frame for every customer.

## 1. The rings

| Ring | Who | What they do |
|---|---|---|
| Centre | People (founders, executives, accountable leaders) | Set direction, own agents, judge the cases policy did not foresee, keep relationships |
| Inner ring | Lead agents (one per team or journey) | The only agent people talk to; plan, delegate, bring results together, report back |
| Outer ring | Specialist agents | One job each: prepare, check, draft, publish, reconcile, monitor |
| Outer arcs | Departments | Marketing, sales, projects, operations, intelligence resources (in the showcase); journeys or functions for a customer |
| Around | Tools and systems | Where the work happens: business systems, Microsoft 365, the web |

The showcase reveals the organisation step by step: people first, then delegation of management to lead agents, then delegation of routine work to agent teams. The blueprint's Org model view does the same.

## 2. Role card and role profile

**Role card** (one screen): department, org role (lead or specialist), team, lifecycle, channels, technology, responsibility.

**Role profile** (nine sections): starting point and contribution; mission and output (with trigger and input); tasks; team and leadership; interaction and autonomy (autonomous, approval, escalation); knowledge, rules and limits (with an explicit "not allowed" list); systems and channels; communication and personality; success and measurement. The role profile becomes the agent's versioned instructions.

## 3. The hybrid organisation blueprint (architecture view)

From top to bottom: business outcomes (and how they are measured); the hybrid workforce (human-led: direction, accountability, judgement, relationships; agent-operated: a lead agent with its specialist team); the **approval seam** (nothing leaves the company without a person signing it off); governance (policies, risk classification, data protection, records) feeding rules into Intelligence Resources; Intelligence Resources (the merged IT and HR function: the lifecycle of a digital colleague from planned position to retirement, its personnel file, where it runs and is watched) producing evidence for security and trust (injection defence, least privilege, conditional access, audit trail, data residency); knowledge, channels, build and run; and a foundation shared by people and agents (Microsoft Entra, Microsoft 365, Microsoft Graph).

## 4. Mapping to Microsoft's Frontier Firm

| HAIRO | Microsoft Frontier Firm and architecture |
|---|---|
| Human-led, agent-operated | Phase 3 of the Frontier Firm journey |
| A person behind every digital colleague | Agent boss; human-agent ratio |
| Intelligence Resources | Work Trend Index: IT and HR for digital labour; IT as the agent control plane |
| Lifecycle and personnel file | Agent 365 registry, Entra Agent ID, versioned instructions, evaluations |
| Lead agent and specialists | Orchestrator and specialist agents; Azure Architecture Center patterns (handoff, sequential, concurrent, group chat, magentic) |
| Approval seam | Human-in-the-loop gates: Copilot Studio request information, Agent Framework tool approval, Cowork checkpoints |
| Knowledge scoped per agent | Microsoft IQ (Work IQ, Fabric IQ, Foundry IQ) with permission-aware grounding |
| Foundation | Microsoft Entra, Microsoft 365, Microsoft Graph, Microsoft Fabric, Microsoft Purview |

## 5. How the blueprint adapts it for enterprises

- Departments become **journeys** (or functions), each with a lead agent and an agent boss from the customer's leadership.
- Persona names for agents are optional (`alias`); many enterprises prefer functional names.
- Every agent carries an **autonomy level**, a **horizon**, a **status** (hypothesis until validated) and, for MVP candidates, the **seven declarations** that make it governable.
- Evidence ids connect every customer statement to its source, and internal sources are removed from the customer version.
