# Frontier Envisioning: Cowork intake analysis and design

Date: 2026-11-08

Status: local source intake and engineering changes executed; full M0/release readiness blocked by recorded evidence.

## 1. Approval and scope

The selected product boundary is a standalone Cowork package maintained in this
repository, with a controlled integration/export into HubWorks.

The user approved this preservation-first design and writing this document.
That initial approval was **documentation only**. It did not authorize source import,
execution of exported scripts or hooks, dependency installation, commits,
pushes, tags, GitHub settings, releases, or Azure provisioning/deployment.

Subsequently the user approved local intake on a new branch, planned local
engineering fixes and isolated Python 3.11/Node 24 validation. No commits,
pushes, administration, vendoring or deployments were approved. See
[M0 evidence](../intake/m0-evidence.md) for actual results and unresolved gates.

This specification defines the intake baseline and engineering readiness gates.
Native HubWorks adaptation, showcase deployment, and new customer-facing agent
infrastructure are separate delivery slices requiring their own approved plans.
They must not be hidden inside the initial import.

## 2. Sources and evidence

### 2.1 Repository boundaries

| Boundary | Location and state |
|---|---|
| Target repository | `urruegg_microsoft/frontier-envisioning`; existing Git history and `origin`; clean `main` tracking `origin/main` before this document |
| Export container | `C:\Users\urruegg\source\urruegg_microsoft\frontier-envisioning-github-repo` |
| Exported engineering source | The `frontier-envisioning` subdirectory of the export container |
| Product baseline | Frontier Envisioning 1.4.0, dated 2026-11-08 |
| Upstream research | Innovation-Hub-Agentic-Toolkit at commit `5e85bbe8f9d94e4abddf60fb8f834790838f4f37` |

Source links below now point to imported repository files. The original export
remains untouched and is not a remote runtime dependency.

Primary handover sources:

- [Retained exporter intake proposal](../engineering/intake-plan.md).
- [Export README](../../README.md).
- [Engineering working agreement](../../AGENTS.md).
- [Product requirements and design](../../docs/prd-and-solution-design.md).
- [Existing HubWorks integration analysis](../../docs/analysis/hubworks-integration-analysis.md).

### 2.2 Read-only analysis evidence (historical)

The following records the initial analysis phase. Current execution results
supersede its pending checks in the [M0 evidence](../intake/m0-evidence.md).

**Verified by read-only inspection:**

- The plugin contains seven skills, 79 files and 31 Python files.
- All 69 indexed skill files match the hashes in the supplied installation index.
- Static renderer assembly matches the generated blueprint template.
- All seven descriptions are below 1,024 characters; all seven skill documents
  are below 20,000 characters.
- Engineering configuration, task-runner wiring, workflows, hooks, tests and
  showcase infrastructure exist and were inspected.
- The exported checkout has no `build/`, `dist/`, Node lockfile, vendored
  Superpowers lock, or approved `.azure/deployment-plan.md`.
- The six checked GitHub Actions version tags resolve to real public refs.
- The exported code-owner account currently has no access to the target repo.

**Handover assertions, not rerun here:**

- Publication and successful use in Cowork.
- 29/29 plugin self-tests, 39/39 engineering unit tests, 12/12 DOM tests,
  and 2/2 pipeline tests.
- Reproduction of published ZIPs and demo artifacts.
- Lint, neutrality, local hosting and release-bundle results.

**Not yet verified:**

- Ruff, pytest, Playwright, Bicep, azd and GitHub workflow execution.
- Native Cowork/catalogue acceptance and complete installed workflow behavior.
- Actual connector availability, subprocess execution and artifact persistence.
- Authenticated Azure access, tenant restriction and deployment approvals.
- Original published artifact provenance and full release ZIP reproduction.
- Native HubWorks runtime compatibility.

During the original analysis phase, no exported program was executed or source
imported. Later local execution and its limits are recorded in the M0 evidence;
no external resource was changed.

## 3. Actual product and runtime

### 3.1 Inventory

| Product surface | Files | Python files | Responsibility |
|---|---:|---:|---|
| frontier-envisioning | 3 | 0 | Orchestration from framing to handover |
| frontier-context-discovery | 7 | 2 | Context, transcripts, evidence and validation |
| frontier-blueprint | 12 | 5 | Blueprint generation and workshop feedback |
| frontier-solution-design | 4 | 1 | PRD, design, ADR and readiness scaffolding |
| frontier-agent-identity | 24 | 13 | Branding, names, icons, cards, catalogue and kit |
| frontier-value-case | 9 | 5 | Value assumptions and economic calculations |
| frontier-finops | 10 | 4 | Usage, costs, credits and commercial assumptions |
| Packaging, installation and notices | 10 | 1 | Package metadata and installation integrity |
| Total plugin | 79 | 31 | 1,482,322 bytes; 7,365 Python physical lines |

The renderer has three implementation files totaling 2,834 lines and fourteen
declared views. Some views are conditional on data; fourteen declared views do
not mean fourteen screens appear for every input.

Sources: [installation index](../../plugin/install/plugin-install.json),
[renderer sources](../../src/renderer/).

### 3.2 Boundaries that must remain distinct

1. Cowork routes intent and supplies model judgment and approved M365 tools.
2. Skill Markdown defines the procedures and required evidence.
3. Python parses, validates, calculates, merges and generates local artifacts.
4. The host supplies writable storage, subprocess execution and publication.
5. The generated browser application supports offline workshop interaction.
6. GitHub/VS Code provides the engineering harness, not the customer runtime.
7. Azure hosts the optional static showcase, not the customer agent platform.

The product is not a Markdown-only library. Removing Python during intake would
remove material functionality rather than merely change its packaging.

The identity kit primarily implements branding and solution stamping. It is not
Microsoft Entra Agent ID provisioning. FinOps models costs and guardrails; it
does not deploy live cost controls.

### 3.3 State and generated artifacts

Preserve the engagement record, normalized blueprint JSON, stable entity IDs,
identity configuration/palette, value assumptions and FinOps inputs.
Generated HTML, images, catalogues, ZIPs and design documents are outputs, not
alternative canonical inputs.

Workshop notes are keyed by blueprint identity/version in browser storage.
Feedback exports span discovery, agents, use cases, identity review, assumptions,
readiness and ADRs. Intake tests must exercise the complete round trip.

Blueprint generation calls sibling identity/value/FinOps components. Preserve
their relative layout. Keep the two identical `fv_expr.py` copies during the
baseline import; consolidating them changes independent skill dependencies.

### 3.4 Python and optional converters

Core processing is standard-library Python, but optional SVG/raster conversion
can use CairoSVG, rsvg-convert or Node/Sharp.

Document the SVG-only fallback and the converter environment used for artifact
reproduction. Do not promise identical identity ZIPs across different converter
environments. Do not install optional converters merely to satisfy a generic
"all dependencies installed" claim.

## 4. Packaging and HubWorks compatibility

The export contains three different metadata contracts:

- [Claude-style plugin metadata](../../plugin/.claude-plugin/plugin.json).
- [Microsoft 365 devPreview package manifest](../../plugin/package/manifest.json).
- [Custom installation index](../../plugin/install/plugin-install.json).

These establish intended package structure, not actual tenant acceptance.
The installer assumes host-specific mounted skill storage, CopyArtifact
operations, OneDrive persistence and a fresh chat. Verify those capabilities in
the intended deployment channel rather than inferring them from metadata.

### 4.1 Static fit

| Skill | Description characters | SKILL.md characters |
|---|---:|---:|
| Envisioning | 866 | 10,560 |
| Context discovery | 664 | 10,894 |
| Blueprint | 781 | 17,255 |
| Solution design | 677 | 8,670 |
| Agent identity | 811 | 11,461 |
| Value case | 769 | 8,590 |
| FinOps | 692 | 8,289 |

Names match folders. No skill needs shortening solely for the inspected limits.
The local checker also has a 900 UTF-16-unit house limit for product descriptions.
Character counts, UTF-16 units and file sizes must not be conflated.

Full package checks still need to cover companion-file limits, references,
assets, manifest/tree parity, schema acceptance and discoverability.

### 4.2 Upstream integration

HubWorks supports managed Cowork Suite/Director packages. Most CLI distribution
is frozen. Repo-local VS Code execution is an engineering convenience.

The inspected upstream builders use in-repository source paths and registered
bundle identities. An external-source override or runtime repository loader was
not demonstrated. A later export must materialize approved content through an
upstream PR and registration change.

The upstream generic verifier accepts a directory or ZIP. Prefer its pinned
reuse, subject to permission and licensing, over immediately duplicating its
validation implementation. Do not fork the whole monorepo build/release system.

The upstream documentation's Markdown-focused approach is not proof that this
Python-backed export can execute there, nor an independently verified universal
platform prohibition. Perform an actual-host capability test before claiming
equivalence. If capabilities are unavailable, explicitly approve a reduced
adapter or an execution bridge; neither is a transparent preservation change.

Sources: [upstream execution model](https://github.com/mcaps-microsoft/Innovation-Hub-Agentic-Toolkit/blob/5e85bbe8f9d94e4abddf60fb8f834790838f4f37/docs/cli-vs-cowork.md),
[verifier](https://github.com/mcaps-microsoft/Innovation-Hub-Agentic-Toolkit/blob/5e85bbe8f9d94e4abddf60fb8f834790838f4f37/cowork-plugins/verify_bundle.py),
[builder](https://github.com/mcaps-microsoft/Innovation-Hub-Agentic-Toolkit/blob/5e85bbe8f9d94e4abddf60fb8f834790838f4f37/cowork-plugins/scripts/build_hubworks_package.py).

## 5. Engineering findings requiring disposition

| Finding | Required disposition |
|---|---|
| Existing target already has Git history and origin | Import on a branch; do not reinitialize Git, create another remote or blindly run bootstrap --apply |
| CODEOWNERS uses an account without target access | Personalize to an authorized maintainer/team and verify review eligibility |
| Bootstrap initially requires only L1 | Establish L1, L2 and applicable IaC checks; do not claim the full gate set is required until policy is verified |
| Bootstrap skips unavailable controls | Treat missing mandatory controls as readiness blockers, not successful setup |
| dev.py check/ci runs unit tests but not tests/pipeline | Wire the two pipeline wrappers into the intended strict CI coverage |
| Local check can skip missing optional tools | Use strict checks for readiness evidence and show skipped checks separately |
| Node lockfile and exact Python dependency pins absent | Resolve and commit an approved dependency graph in the engineering lane |
| Actions use valid mutable tags; SBOM download uses latest | Pin approved revisions and verify downloaded tooling before production release |
| Superpowers vendoring is proposed, not delivered | Keep the working personal install; approve a pinned, licensed cloud-agent configuration separately |
| Hook tests call the decision function, not every host harness | Verify activation/input/output on each supported Copilot surface |
| Guard intentionally allows calls on internal errors | Rulesets, reviews and environment protections remain authoritative |
| Release and showcase share prod but use different refs | Verify private-repo feature availability and distinct branch/tag policies; separate approval environments if necessary |
| Azure deployment is independent of CI completion | Require successful checks for the exact deployed SHA |
| Local server does not emulate Entra roles | Do not equate local browser success with authenticated deployment verification |
| Entra smoke checks only unauthenticated access behavior | Add authorized access, tenant rejection, downloads and response-header evidence |
| Complete bundle automatically includes docs/analysis | Review and explicitly classify its internal documentation payload before distribution |

These are intake dispositions, not fixes already made.

Engineering sources: [task runner](../../tools/dev.py),
[bootstrap](../../tools/bootstrap_github.py),
[CI](../../.github/workflows/ci.yml),
[release workflow](../../.github/workflows/release.yml),
[deployment workflow](../../.github/workflows/azure-dev.yml),
[guard](../../.github/hooks/scripts/guard.py),
[complete bundle builder](../../tools/build_release.py).

Current first-party documentation supports the exported camelCase/version-1
Copilot hook format. Do not "repair" it based on another harness's schema.
The six checked Actions tags exist; they are not missing-action failures.

References: [VS Code hooks](https://code.visualstudio.com/docs/agent-customization/hooks),
[Copilot hooks](https://docs.github.com/en/copilot/reference/hooks-reference),
[GitHub environments and branches/tags](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).

## 6. Known product limitations: preserve, then fix explicitly

1. The blueprint skill advertises `--canon` and `--no-product-icons`, but the
   wrapper parser does not accept them; the lower-level builder does.
2. Dependent identity/value/FinOps failures can produce reduced output with an
   overall zero exit status. Zero alone does not prove complete delivery.
3. Blueprint feedback merge checks identity but not source version; assumption
   merge also needs engagement/version compatibility consideration.
4. Some installation documentation still refers to five rather than seven skills.
5. Scrubbing designated fields and denylisted names is not universal anonymization.

Record these against the preserved 1.4.0 baseline. Do not hide behavior repairs,
renames, icon replacements or helper refactors inside import. Runtime corrections
require a separately reviewed version bump and regression tests.

Sources: [blueprint wrapper](../../plugin/skills/frontier-blueprint/scripts/build_with_identity.py),
[feedback merge](../../plugin/skills/frontier-blueprint/scripts/merge_feedback.py),
[blueprint builder](../../plugin/skills/frontier-blueprint/scripts/build_blueprint.py).

## 7. Source, privacy and licensing policy

- Keep the repository private during intake.
- Preserve product MIT notices and existing license meaning.
- Do not describe product icons/trademarks as MIT; retain third-party notices.
- Review the internal HubWorks analysis separately from product documentation.
- A fictitious example or successful name scan is not public-release clearance.
- Do not import real engagements, transcripts, identities, credentials, personal
  configuration, caches, build outputs or dependency directories.
- Review HTML, JSON, kits, configurations, catalogues, design documents and
  feedback exports, not only visible citations.
- Keep live customer output in approved engagement storage, outside Git.
- Never copy enterprise credentials into CI. Approve least-privilege access to
  any private cross-repository validator or dependency.

Sources: [notices](../../plugin/THIRD-PARTY-NOTICES.md),
[internal integration analysis](../../docs/analysis/hubworks-integration-analysis.md).

The complete bundle builder includes all analysis Markdown automatically. Keep
that bundle internal until its payload is explicitly cleared. Later public
packaging needs a deliberate allowlist and appropriate rights; do not publish
the repository merely to gain unavailable GitHub protection features.

## 8. Approved preservation-first architecture

### 8.1 Retain the supplied layout

Use the supplied `plugin/skills`, `src/renderer`, `tools`, `tests`, documentation
and metadata layout. Do not relocate canonical product content into
`cowork-skills/` during baseline preservation.

- Product source: seven skill trees, scripts, references, defaults and rates.
- Renderer source: the three implementation files.
- Tracked generated files: blueprint template and installation index, reproduced
  by their existing generators.
- Build output: ignored `build/` and `dist/`.
- Engineering source: existing task runner, test suites and CI, hardened separately.
- Documentation: classified product/internal material plus approved specifications.

After approval for import, reconcile the target's starter README, ignore rules
and license carefully. Preserve target Git metadata and this specification.
An import inventory must distinguish untouched source from reviewed configuration
personalization and excluded local/internal-distribution material.

### 8.2 Delivery slices and dependencies

| Slice | Outcome | Prerequisites and boundary |
|---|---|---|
| M0-A: audited preservation | Reviewable source import and baseline evidence | Written spec approved; exact source/exclusion inventory; no runtime rewrite |
| M0-B: engineering readiness | Strict local/CI gates, authorized ownership and release controls | M0-A; approved configuration edits; mandatory controls actually available |
| M1: HubWorks integration | Versioned source export, routing and ownership contract | Baseline green; native-host capability proof; upstream maintainer review |
| M2: showcase | Controlled static demonstration deployment | Separate Azure approval, identity/cost/owner decisions, successful exact-SHA checks |
| Future customer BUILD track | Deployable customer agent architecture | Separate requirements, service identity, IaC, security and operations design |

M1 and M2 are independent after the required baseline evidence. Neither is a
condition for declaring the source preservation complete. Do not promise the
handover's proposed November 20 combined scope before measuring baseline failures.

### 8.3 Data ownership for later integration

Frontier produces workshop content and artifacts. HubWorks remains the owner of
CEHub writes unless maintainers approve an explicit changed boundary.

Shared engagement schemas, agenda blocks, closeout packs and transcript archives
in the source analysis are future proposals, not shipped 1.4.0 functionality.
Use explicit schema/version mappings and one writer for each shared record.

Additional upstream governance applies to engagement, journey, opportunity and
pipeline data. Pure workshop-content generation does not automatically inherit
every additional data-governance sign-off.

## 9. End-to-end gates and measurable acceptance

### 9.1 Preservation and provenance

- Exactly seven skill trees and 69 indexed skill files; every indexed hash matches.
- All ten other plugin files inventoried and reviewed; no missing package-root assets.
- Renderer assembly exactly matches the tracked template.
- The four recorded build artifacts reproduce their expected hashes.
- Raw comparisons apply to the plugin ZIP, identity ZIP and catalogue.
- Blueprint normalization applies only to the specified JSON generated-date field;
  retain and report raw and normalized results.
- Obtain original published ZIPs where possible and verify them independently.
  If unavailable, state that reproduction is against supplied records, not
  independently authenticated publication.
- Original complete/source archives marked not reproduced remain explicitly out
  of the reproduction claim.
- Do not regenerate an expected hash from a changed build merely to make it pass.

Source: [release manifest](../../releases/1.4.0/manifest.json),
[reproduction verifier](../../tools/verify_release.py).

### 9.2 Engineering

- L0: renderer drift, Python syntax, repository contracts, lint and neutrality.
- L1: strict tool availability; unit and pipeline tests; plugin self-test;
  package/demo build; mandatory 1.4.0 reproduction; DOM and archive checks.
- L2: Chromium on the built site, meaningful populated/absent-data cases for all
  fourteen views, storage/export/printing/navigation behavior and CSP evidence.
- IaC: compilation plus the separately approved Azure readiness workflow before
  deployment; compilation alone does not prove deployability.
- Server policy: eligible code owner, required status checks, protection and
  approval behavior demonstrated on a test PR.
- Copilot: demonstrate discovery of instructions/skills and actual hook execution
  on each claimed surface; distinguish Copilot harness from other harnesses.
- Locks/pins: approved dependency graph, Actions/tooling revisions and third-party
  notices; no implicit use of latest for release tooling.

Use the existing commands after execution/import approval, not as instructions
to run them during this documentation phase:

```powershell
python tools\dev.py doctor
python tools\dev.py ci
python tools\dev.py test-all --strict
python tools\dev.py site e2e --strict
```

The current implementation needs the pipeline-test wiring disposition before
the strict CI command alone can claim the entire intended L1 suite.

CI/devcontainer target Python 3.12 and Node 22. The local Python 3.14 and Node 24
commands run, but their availability is not proof of the baseline toolchain's
compatibility. Use an isolated, reproducible approved environment.

### 9.3 Actual customer runtime

- Fresh-chat installation and discovery of all seven skills.
- Correct trigger routing and rejection/handoff of unrelated requests.
- Host workspace, subprocess, sibling dependency and publication capabilities.
- Complete demo: blueprint HTML/JSON, identity kit/catalogue, value and FinOps;
  missing dependent outputs must not be described as complete.
- Evidence-backed workshop feedback round trip, stable IDs and version behavior.
- Worked-example economic results; distinguish value, budget, capacity and risk.
- Historical rates retained for reproduction; current commercial assumptions
  verified separately before current-customer recommendations.
- Explicit missing-input, connector, converter and publication failure behavior.
- Approved storage/persistence and customer-output classification.

### 9.4 Release and deployment

- A release references an immutable version and exact verified source SHA.
- L1/L2 and relevant IaC evidence correspond to that SHA, not an unrelated run.
- Human-controlled tag, release approval and publication are verified, not assumed.
- Private-repository feature limitations have a compliant fallback or block release.
- Branch/tag restrictions match the distinct release and showcase workflows.
- Release assets have retained checksums, provenance and the intended SBOM scope.
- Internal analysis is not accidentally included in an externally cleared package.
- Retain a known-good package and deployment evidence for rollback.

GitHub release publication is not Cowork installation, and a showcase deployment
is not customer agent infrastructure deployment. Record each separately.

## 10. Azure showcase: separate approval lane

The supplied showcase is Azure Static Web Apps with Bicep, azd, an Entra
registration, app settings and generated authentication/CSP configuration.
Keep `SHOWCASE_ENABLED` unset/false until this lane is approved.

Custom authentication requires Standard. If Entra custom auth is selected,
enforce that plan/configuration combination and mandatory registration inputs.
Decide region, subscription, ownership, cost, permissions, callback URI, credential
lifecycle and federated deployment identity before provisioning.

Local browser testing deliberately bypasses authentication emulation. Deployment
acceptance must demonstrate authorized success, unauthenticated rejection,
wrong-tenant rejection, package-download authorization and expected headers.

An approved Azure deployment plan is absent. No formal Azure validation was run;
do not set a plan to Validated or infer permission to deploy from this document.
Use prepare -> validate -> deploy only after the applicable approvals.

Sources: [showcase deployment guide](../../docs/engineering/deployment.md),
[site builder](../../tools/build_site.py),
[local server](../../tools/serve_site.py),
[smoke check](../../tools/smoke_site.py),
[official custom-auth documentation](https://learn.microsoft.com/en-us/azure/static-web-apps/authentication-custom).

## 11. Decisions and next review

Resolved:

- Standalone Cowork product plus controlled HubWorks integration/export.
- Preservation-first; retain the supplied product layout and functionality.
- Separate engineering corrections, native adapter and showcase deployment.
- Detailed specification in `docs/plans/`.
- Written specification reviewed and approved for documentation-only M0 planning.
- Subsequent local intake/engineering execution approved; no commits or external changes.

Before implementing M0:

1. Approve execution and the exact initial import/exclusion scope.
2. Confirm eligible ownership/reviewers and mandatory private-repository controls.
3. Approve any human-maintained configuration files that need personalization.
4. Define original-artifact provenance evidence or explicitly accepted limitations.
5. Classify internal documents and release payloads.

The documentation-only [M0 implementation plan](2026-11-08-cowork-m0-implementation-plan.md)
records exact files, targeted tests, expected outputs and human-operation
boundaries. Its execution gates remain open. HubWorks and Azure plans remain
separate. No ready/deployed/fully migrated claim is justified by the current
read-only analysis.
