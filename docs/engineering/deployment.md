# Deployment

Two deployable units:

| Unit | Built by | Delivered to |
|---|---|---|
| Plugin package `frontier-envisioning-plugin-<version>.zip` | `release` workflow from a tag | GitHub release, then Copilot Cowork (chat install or the organisation catalogue, decision D-02) |
| Showcase site (Caldova blueprint, identity catalogue, plugin download) | `azure-dev` workflow or `azd up` | Azure Static Web Apps, environments `dev` and `prod` |

## Showcase: architecture

- `azure.yaml`: azd project with one service `site` (host `staticwebapp`); the `prepackage` hook runs `tools/build_site.py`, which builds the demo when needed.
- `infra/main.bicep` (subscription scope): resource group `rg-<environment>` and `infra/modules/static-site.bicep` (Static Web App, plan Standard, sign-in client settings as app settings). Outputs `SITE_URL` and `SITE_NAME`.
- `staticwebapp.config.json` (generated): every route requires a signed-in user of one Microsoft Entra tenant; GitHub sign-in is off; each HTML page has a Content-Security-Policy that allows exactly its own inline script by hash; security headers on every response.

## First deployment (people, once per environment)

Prerequisites: decision ENG-D3, an Azure subscription with permission to create resource groups, and permission to register an application in Microsoft Entra ID.

1. **Sign-in app registration** (single tenant). Redirect URI `https://<site host>/.auth/login/aad/callback` (add it after the first provision when the host name is known). Create a client secret if your tenant allows it; if it does not, decide with ENG-D3 (for example the Free plan with Static Web Apps role invitations, or release assets only).
2. **azd environment**
   ```bash
   azd auth login
   azd env new frontier-dev
   azd env set AZURE_LOCATION westeurope
   azd env set SITE_AUTH_MODE entra
   azd env set SITE_AUTH_TENANT_ID <tenant id>
   azd env set SITE_AUTH_CLIENT_ID <application (client) id>
   azd env set SITE_AUTH_CLIENT_SECRET <client secret>
   azd up
   python tools/smoke_site.py --url "$(azd env get-value SITE_URL)"
   ```
   `.azure/` holds the environment values and is ignored by Git.
3. **CI with OpenID Connect**: `azd pipeline config --provider github` creates the service principal with federated credentials and sets the variables. The workflow uses GitHub environments, so add federated credentials for them:
   ```bash
   az ad app federated-credential create --id <app id of the deployment principal> --parameters \
     '{"name":"gh-env-dev","issuer":"https://token.actions.githubusercontent.com","subject":"repo:<owner>/frontier-envisioning:environment:dev","audiences":["api://AzureADTokenExchange"]}'
   ```
   and the same with `prod`. In each GitHub environment set the variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_ENV_NAME`, `AZURE_LOCATION`, `SITE_AUTH_MODE`, `SITE_AUTH_TENANT_ID`, `SITE_AUTH_CLIENT_ID` and the secret `SITE_AUTH_CLIENT_SECRET`. Finally set the repository variable `SHOWCASE_ENABLED` to `true`.
4. `prod` requires a reviewer (set by the bootstrap). Deploy prod with *Run workflow* on `azure-dev`, environment `prod`.

## Operations

- Every push to `main` that touches the site, the plugin, the renderer or the infrastructure deploys dev.
- Roll back by running `azure-dev` from an earlier commit or tag.
- Remove an environment with `azd down --purge`.
- Cost and owner are recorded in INT-05.
