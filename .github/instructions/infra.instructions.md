---
applyTo: "infra/**,azure.yaml,site/**,.github/workflows/azure-dev.yml"
---
# Showcase hosting (Bicep, azd, Azure Static Web Apps)

- Infrastructure is Bicep, deployed with the Azure Developer CLI (`azd provision`, `azd deploy`). Keep `azure.yaml`, `infra/main.bicep`, `infra/main.parameters.json` and the workflow consistent.
- Secure by default: sign-in restricted to one Microsoft Entra tenant, no secrets in parameter files or outputs (`@secure()` parameters from the azd environment), least-privilege identities, tags `azd-env-name` and `azd-service-name`.
- Prefer Azure Verified Modules where one fits; pin API versions; run `az bicep build --file infra/main.bicep` before you push.
- Security headers and the Content-Security-Policy come from `tools/build_site.py`; test them with `tools/serve_site.py` and the browser tests.
- Agents do not provision or deploy: deployments run in the `azure-dev` workflow with environment approvals.
