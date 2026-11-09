# Infrastructure (showcase)

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Showcase infrastructure guide; document revision, not product version |
| References | [Documentation](../docs/README.md), [Deployment](../docs/engineering/deployment.md), [Showcase decision](../docs/adr/0020-showcase-hosting.md) |

- `main.bicep` (subscription scope): resource group `rg-<environment>` and the static web app module; outputs `SITE_URL`, `SITE_NAME`, `AZURE_RESOURCE_GROUP`.
- `modules/static-site.bicep`: Azure Static Web App (Standard by default, staging environments off) and the sign-in client settings as app settings (`AAD_CLIENT_ID`, `AAD_CLIENT_SECRET`) when a client id is given.
- `main.parameters.json`: values from the azd environment (`AZURE_ENV_NAME`, `AZURE_LOCATION`, `SITE_LOCATION`, `SITE_SKU`, `SITE_AUTH_CLIENT_ID`, `SITE_AUTH_CLIENT_SECRET`).

Validate with `az bicep build --file infra/main.bicep`; deploy with `azd up` or the `azure-dev` workflow. See [deployment](../docs/engineering/deployment.md).
