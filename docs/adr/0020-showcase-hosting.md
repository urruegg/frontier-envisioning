# ADR-0020: Showcase hosting

**Status:** Proposed (8 November 2026), decision ENG-D3

## Context
The original idea drew on public showcases of the HAIRO model and its architecture. The Caldova blueprint, the identity catalogue and the plugin download should be reachable by a link for Hub colleagues, deployed from the repository with infrastructure as code.

## Decision
Azure Static Web Apps (Standard) provisioned with Bicep through the Azure Developer CLI; GitHub Actions deploy with OpenID Connect (`azd pipeline config`), dev from `main`, prod by hand with an environment approval. Every route requires a signed-in user of one Microsoft Entra tenant. Each page gets a Content-Security-Policy that allows exactly its inline script by SHA-256 hash; security headers on every response; the local server applies the same headers for the browser tests.

## Consequences
A small monthly cost for the Standard plan and an app registration with a client secret per environment (tenant policy permitting). The site never contains customer data.

## Alternatives considered
GitHub Pages (no tenant sign-in for private content); the Free plan with the pre-configured provider (any Microsoft account could sign in unless role invitations are managed); no hosting (release assets only).
