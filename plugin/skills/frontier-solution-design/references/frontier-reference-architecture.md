# Microsoft Frontier reference architecture (Innovation Hub canon)

Research date: 22 October 2026. Public Microsoft sources only; numbers in brackets refer to the source list at the end. Product names and availability change often, especially around Microsoft announcement events: re-check before a workshop and before any build decision.

For optional 1.9.2 process design, also use the
[process method and dated Fabric source IDs](../../frontier-process/references/ontology-method.md).
Fabric ontology/agent integrations and operations agents remain Preview, with
unverified mapping/tenant gaps. The process canon's recorded 11 November 2026
date is not a new independent availability check. Neither the GA product-wrapper
designation nor the older snapshot below certifies those dependencies or import.

> **Naming caution.** "Frontier Firm" is the Work Trend Index concept; "Microsoft 365 E7: The Frontier Suite" is a licence; the "Frontier program" gives early access to previews; "Microsoft Frontier Company" is a Microsoft services unit launched in July 2026 [5]. The Hub's "Frontier Company Blueprint" is a method name; say which one you mean.

## 1. Frontier Firm in brief

- Work Trend Index 2025: the Frontier Firm combines intelligence on demand, human-agent teams and a new role for every employee, the **agent boss** who builds, delegates to and manages agents [1].
- Three phases, which can coexist: (1) human with assistant, (2) human-agent teams, agents as digital colleagues at a person's direction, (3) human-led, agent-operated, where agents run processes and check in as needed [1].
- The **human-agent ratio** balances human oversight and agent efficiency; the **Work Chart** organises outcome-based teams; **Intelligence Resources** brings IT and HR together for digital labour [1].
- Work Trend Index 2026: organisational factors explain more than twice the AI impact of individual factors; firms become learning systems that decide who reviews agent performance and who may change agent workflows; IT becomes the control plane for agent operations [2]. Four collaboration patterns, author, editor, director, orchestrator, should be matched per workstream [3].
- Microsoft frames the transformation as intelligence plus trust: Copilot as the experience, Microsoft IQ as the intelligence, Agent 365 as the trust layer [4][6].

## 2. Layers (the canon used in every blueprint and solution design)

The layer names are an Innovation Hub synthesis; Microsoft does not publish this exact stack. The components are Microsoft's.

| # | Layer | Purpose | Microsoft components | Questions to ask |
|---|---|---|---|---|
| 0 | Journey & operating model | Journeys, outcomes, human-agent ratio, decision rights | Work Trend Index guidance, collaboration patterns, Agents hub adoption patterns and maturity [1][2][3][44] | Which journey and KPI? Which pattern per step? Who owns each agent and may change it? |
| 1 | Experience & channels | Where people delegate, review and approve | Microsoft 365 Copilot (Chat, Cowork), Teams, Outlook, Microsoft 365 Agents SDK [7][8][9][10] | Where do users already work? Where do approvals surface? |
| 2 | Orchestration & agents | Lead agents coordinating specialists and deterministic workflows | Copilot Studio (multi-agent, A2A, workflows, agent flows), Foundry Agent Service, Microsoft Agent Framework, Power Automate [11][12][14][16][17] | Is one agent enough? Which pattern? Which steps must be deterministic? SaaS, low-code or pro-code? |
| 3 | Knowledge & context (IQ) | Permission-aware grounding and memory | Work IQ, Fabric IQ, Fabric data agents, Foundry IQ on Azure AI Search, web grounding [19][21][23][24][25] | Sources of truth? Permissions passed through? Memory scope? Residency? |
| 4 | Tools & actions | Read and write systems of record | Power Platform connectors, MCP servers, Foundry toolboxes, A2A, OpenAPI [11][15][26] | Which actions change state? Least privilege per tool? Approved MCP servers? |
| 5 | Models | Reasoning matched to the task | Foundry model catalog and model router, model choice in Copilot Studio, multi-model Copilot [4][27] | Smallest adequate model? Quotas and fallbacks? Data boundaries of third-party models? |
| 6 | Identity, security & governance | Every agent identifiable, governed, protected | Microsoft Entra Agent ID, Microsoft Agent 365 (registry, policies), Microsoft Purview, Microsoft Defender, Power Platform environments and DLP [26][28][30][31] | One identity per agent? Delegated or own access? Owner? Risk tier and release gate? Kill switch? |
| 7 | Observability, evaluation & operations | Quality, safety, cost and value | Foundry Control Plane, Agent 365 analytics, Azure Monitor and Application Insights, cost management [26][27][32] | Who reviews agent performance? Evaluations in CI/CD? Cost alerts? Drift? |
| + | Approval seams (cross-cutting) | Human checkpoints between agent steps | Copilot Studio "request information" step, Agent Framework tool approval, Foundry human-in-the-loop (preview), Cowork checkpoints, maker-checker [13][18][39][41][42] | Mandatory or optional? State persisted at the gate? Escalation target? |

## 3. Build choice and agent count (Cloud Adoption Framework)

- Adopt a ready-made SaaS agent when one fits; otherwise build in Copilot Studio (SaaS, low-code) or Microsoft Foundry (PaaS, pro-code); infrastructure-level builds are the exception [36].
- Start with a single agent with tools. Go multi-agent only when the use case crosses security or compliance boundaries, involves several owning teams, or is planned to grow beyond a few functions; distinct roles alone do not justify more agents [37].
- CAF lifecycle: plan, govern and secure, build, manage (integrate and operate) [34][35]. Build guidance: an agent charter with responsibilities and prohibited actions, deterministic workflows for critical logic, human confirmation for high-impact actions, knowledge segmented by role [27].
- Governance: a control plane and registry, one identity per agent, cross-platform policies, cost alerts, incident plans that include disabling agents, and a named person who approves deployments; Responsible AI principles are fairness, reliability and safety, privacy and security, inclusiveness, transparency and accountability [26].
- Shared responsibility grows from SaaS to PaaS to IaaS; human oversight of high-impact actions always stays with the customer [38].

## 4. Orchestration patterns (Azure Architecture Center)

Use the lowest complexity that works: a direct model call, then a single agent with tools (often the right enterprise default), then multi-agent [18].

| Pattern | Use when | Avoid when |
|---|---|---|
| Sequential | Clear linear dependencies; draft, review, polish | Steps could run in parallel; backtracking or dynamic routing needed |
| Concurrent | Independent perspectives, ensembles, latency-sensitive parallel work | Agents build on each other; strict ordering; no rule to resolve conflicts |
| Group chat (incl. maker-checker) | Debate, consensus, structured review with an auditable thread | Simple delegation suffices; real-time needs; more than about three agents |
| Handoff | The right specialist emerges during processing; escalation to people | The right agent is known upfront (use a deterministic dispatcher); ping-pong risk |
| Magentic | Open-ended problems without a known plan; a reviewable plan is needed | Deterministic paths; low complexity; time-sensitive work |

Implementation advice: keep context compact and persist state; use timeouts, retries and circuit breakers; validate outputs between agents; apply least privilege per agent; run content safety on inputs, tool calls, tool responses and outputs; test with rubrics or model-graded evaluations; scope human approval gates to sensitive tool calls [18].

## 5. Automation levels and autonomy

- Microsoft's three levels of process automation: traditional business process automation (scripts, rules), digital process automation (end-to-end orchestration; RPA is a form of it), agentic process automation (agents that plan, reason and act toward goals). Microsoft recommends a digital foundation with agentic reasoning layered on top [43].
- The Hub's autonomy levels (Assist, Act with approval, Act within guardrails) are a synthesis, anchored in CAF's productivity, action and automation agent types [34], the Agents hub's risk tiers and controls [45], and the distinction between agents acting on behalf of a user and agents with their own access [28].

## 6. Availability snapshot (22 October 2026)

| Capability | Status per sources |
|---|---|
| Microsoft 365 E7 "Frontier Suite"; Microsoft Agent 365 | Generally available since 1 May 2026 [29][56] |
| Microsoft Entra Agent ID | Generally available; extended features need Agent 365 [28][46] |
| Copilot Cowork | Generally available since 16 June 2026 [8] |
| Copilot Studio multi-agent orchestration and A2A | Generally available since April 2026 [11] |
| Copilot Studio workflows | Underlying harness available; check the new workflows experience on Learn [12][58]; classic agent flows remain [55] |
| Microsoft Agent Framework | Version 1.0 for .NET and Python [17][54] |
| Foundry Agent Service | Hosted agents and toolboxes available; routines available; long-running human-in-the-loop in preview [14][15][16][41] |
| Foundry Control Plane | Mix of available and preview features [32] |
| Microsoft IQ; Work IQ APIs | Available since June 2026 [19][21] |
| Fabric IQ; Fabric data agent | Available; some sharing features in preview [23][24][59] |
| Foundry IQ | Mix of available and preview; Copilot Studio integration available [25][57] |
| Web IQ / web grounding | Announced June 2026; verify [19] |
| Purview and Defender features for agents | Supported; verify feature by feature [31] |

Verify on Microsoft Learn before stating availability to a customer; write "verify" when unsure.

## 7. Frontier program

Early access to preview AI features and agents across Microsoft 365 Copilot before general availability; work users need a Microsoft 365 Copilot licence and tenant opt-in; admins control access and how usage-based billing applies [49]. Previews trade earlier capability for changing documentation and features that can change or be withdrawn: give every preview dependency a status and an owner.

## Sources

1. https://www.microsoft.com/en-us/worklab/work-trend-index/2025-the-year-the-frontier-firm-is-born
2. https://www.microsoft.com/en-us/worklab/work-trend-index/agents-human-agency-and-the-opportunity-for-every-organization
3. https://blogs.microsoft.com/blog/2026/05/05/how-frontier-firms-are-rebuilding-the-operating-model-for-the-age-of-ai/
4. https://blogs.microsoft.com/blog/2026/03/09/introducing-the-first-frontier-suite-built-on-intelligence-trust/
5. https://blogs.microsoft.com/blog/2026/07/02/microsoft-frontier-company-ai-engineering-that-amplifies-and-protects-your-intelligence/
6. https://blogs.microsoft.com/blog/2026/07/28/looking-back-on-microsofts-fy26-from-ai-experimentation-to-frontier-transformation/
7. https://blogs.microsoft.com/blog/2026/09/25/introducing-the-new-copilot-with-home-code-and-autopilot/
8. https://www.microsoft.com/en-us/copilot/blog/2026/06/16/copilot-cowork-is-now-generally-available/
9. https://devblogs.microsoft.com/microsoft365dev/build-collaborative-agents-where-work-happens/
10. https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agents-sdk-overview
11. https://www.microsoft.com/en-us/copilot/blog/copilot-studio/new-and-improved-multi-agent-orchestration-connected-experiences-and-faster-prompt-iteration/
12. https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flows-overview
13. https://learn.microsoft.com/en-us/microsoft-copilot-studio/workflows-experience/flows-request-for-information
14. https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents
15. https://devblogs.microsoft.com/foundry/whats-new-in-microsoft-foundry-july-august-2026/
16. https://devblogs.microsoft.com/foundry/from-chatbots-to-automated-assistants-routines-in-microsoft-foundry-are-now-generally-available/
17. https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/
18. https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
19. https://blogs.microsoft.com/blog/2026/06/02/microsoft-build-2026-be-yourself-at-work/
20. https://learn.microsoft.com/en-us/microsoft-iq/
21. https://www.microsoft.com/en-us/copilot/blog/2026/06/02/announcing-the-new-work-iq-apis/
22. https://www.microsoft.com/en-us/dynamics-365/blog/it-professional/2026/09/25/work-iq-business-and-workplace-intelligence-in-the-flow-of-work/
23. https://blogs.microsoft.com/blog/2026/09/28/new-microsoft-data-innovations-unlock-what-only-your-business-knows/
24. https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent
25. https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/what-is-foundry-iq
26. https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/governance-security-across-organization
27. https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/build-secure-process
28. https://learn.microsoft.com/en-us/entra/agent-id/whats-new-agent-id
29. https://www.microsoft.com/en-us/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/
30. https://www.microsoft.com/en-us/microsoft-agent-365
31. https://learn.microsoft.com/en-us/purview/ai-agent-365
32. https://learn.microsoft.com/en-us/azure/foundry/control-plane/overview
33. https://learn.microsoft.com/en-us/entra/agent-id/agent-registry-convergence
34. https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/
35. https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/integrate-manage-operate
36. https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/technology-solutions-plan-strategy
37. https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/single-agent-multiple-agents
38. https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility-ai-agent
39. https://learn.microsoft.com/en-us/agent-framework/agents/tools/tool-approval
40. https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
41. https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/add-human-in-the-loop
42. https://www.microsoft.com/en-us/copilot/blog/2026/03/09/copilot-cowork-a-new-way-of-getting-work-done/
43. https://www.microsoft.com/en-us/microsoft-365-copilot/microsoft-copilot-studio/process-automation
44. https://learn.microsoft.com/en-us/agents/adoption-patterns/
45. https://learn.microsoft.com/en-us/agents/center-of-excellence/govern-agents-risk
46. https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
49. https://www.microsoft.com/en-us/copilot/resources/frontier-program
54. https://azure.microsoft.com/updates?id=560982
55. https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview
56. https://partner.microsoft.com/en-us/blog/article/microsoft-365-e7-general-availability
57. https://www.microsoft.com/en-us/copilot/blog/copilot-studio/new-and-improved-build-apps-extend-agents-and-transform-business-processes-in-microsoft-copilot-studio/
58. https://www.microsoft.com/en-us/copilot/blog/copilot-studio/new-and-improved-github-copilot-harness-agent-skills-and-richer-context/
59. https://learn.microsoft.com/en-us/fabric/data-science/data-agent-add-datasources
