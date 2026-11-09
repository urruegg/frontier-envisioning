---
id: BUILD-01
title: "Epic: ready-for-build handover with infrastructure as code"
milestone: "Later"
labels: [type:epic, type:spike, area:plugin, area:infra, priority:P2, size:L]
---
## Context

The Agent Factory journey ends at 'Ready for build' (eight handover checks). Generate the customer's build repository from the blueprint: AGENTS.md and Copilot instructions, the engineering method, agent definitions for the validated agents, the identity kit's validate and stamp pipelines, and Bicep (Azure Verified Modules) for the agent landing zone per journey with DEV, TEST and PROD, plus the evaluation gates. Start with a time-boxed spike.

## Acceptance criteria

- [ ] Spike report: scope, the Azure Verified Modules to use, how the landing-zone areas map to modules, what stays a customer decision
- [ ] Generated repository builds and validates (bicep build, lint) for the Caldova demo
- [ ] No customer data in templates

## Source

Agent Factory canon in plugin/skills/frontier-blueprint/templates/blueprint-defaults.json; docs/analysis/visualisation-and-reuse-evaluation.md
