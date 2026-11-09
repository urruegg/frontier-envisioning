---
id: INT-05
title: "Azure dev environment for the showcase site"
milestone: "M0"
labels: [type:chore, area:infra, human-only, status:needs-decision, priority:P2, size:M]
---
## Context

The showcase (Caldova blueprint, identity catalogue, plugin download) is hosted on Azure Static Web Apps, provisioned with Bicep through azd, deployed by the `azure-dev` workflow with OpenID Connect. Waits for ENG-D3.

## Acceptance criteria

- [ ] Subscription, region and naming agreed (ENG-D3)
- [ ] `azd pipeline config` run: federated credentials, variables in the `dev` and `prod` environments
- [ ] Microsoft Entra app registration for sign-in (single tenant), settings stored as described in docs/engineering/deployment.md
- [ ] `azure-dev` deploys dev from main; the site requires sign-in; the smoke check passes
- [ ] Cost and owner recorded

## Source

infra/; azure.yaml; docs/engineering/deployment.md
