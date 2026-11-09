# Showcase site sources

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Original author not recorded; Copilot AI-assisted maintenance |
| Status | Maintained; approval not inferred |
| Scope | Showcase source guide; document revision, not product version |
| References | [Documentation](../docs/README.md), [Deployment](../docs/engineering/deployment.md), [Infrastructure](../infra/README.md) |

`index.html` is the landing page template (placeholders filled by `tools/build_site.py`). The site is assembled into `build/site` (or `site/dist` for azd) from the Caldova demo; `staticwebapp.config.json` is generated with the sign-in rules and the security headers. See [deployment](../docs/engineering/deployment.md).
