# Internal user documentation implementation plan

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted planning |
| Status | Execution directed in conversation; no separate written-plan review asserted |
| Scope | Issue #31 reader documentation, generated showcase and verification |
| References | [Catalogue](README.md), [Issue #31](https://github.com/urruegg/frontier-envisioning/issues/31), [Idea](../ideas/2026-11-12-internal-user-documentation.md), [Design](../specs/2026-11-12-internal-user-documentation-design.md), [SPRINT-005](../sprints/SPRINT-005-internal-user-documentation.md) |

> **For agentic workers:** Follow the approved scope and repository gates.
> Use executing-plans for the parent sequence. A bounded docs-agent may write
> disjoint prose; no approval, merge, release or deployment is delegated.

**Goal:** Give internal readers an accurate guide, a real offline sample and
five reproducible Playwright images, plus a usable starter prompt.

**Architecture:** Reuse `build_demo.py` and Playwright. Generate named assets
and a provenance manifest; check them against the built core HTML and source
fingerprint. Keep prose separate from capture/build code and preserve archives.

**Tech stack:** Python standard library/unittest, existing Node/Playwright,
Markdown and Mermaid. No dependency installation unless a tool is missing.

## Task 1: Work package and failing generation tests (DOC-03..05,07)

Files: this plan, linked idea/spec/sprint and their catalogues;
`tests/unit/test_docs_demo.py`.

- [ ] Record the maintainer's instruction to execute without inventing formal
  design/plan/ready-label changes; preserve primary main.
- [ ] Write `unittest.TestCase` cases that call the new tool's `main` and fail
  because it is absent. Cases cover core-only HTML, expected five routes,
  malformed/provisional input, missing screenshot, HTML/PNG/source drift and
  capture failure preserving previous output.
- [ ] Run:

```powershell
python -m pytest tests\unit\test_docs_demo.py -q --tb=short
```

Expected RED: missing tool; later negative tests must fail for their exact
behavior, not dependency errors.

## Task 2: Generate and verify the showcase (DOC-03..05)

Create `tools/build_docs_demo.py`, `tools/capture_docs.mjs`;
generate `docs/demo/caldova-blueprint.html`, `docs/demo/manifest.json` and
`docs/images/caldova/{overview,org-model,agents,agent-identity,ontology}.png`.
Modify only the directly related runner wiring in `tools/dev.py`.

- [ ] Use these exact interfaces:

```python
from tools.build_docs_demo import canonical_html

first = b'<script id="bp-data">{"meta":{"generated":"2026-11-12"}}</script>'
next_day = first.replace(b"2026-11-12", b"2026-11-13")
reformatted = first.replace(b'{"meta":', b'{ "meta":')
assert canonical_html(first) == canonical_html(next_day)
assert canonical_html(first) != canonical_html(reformatted)
```

The tool entry point is `main(argv=None) -> int`. Default generation builds
core, captures into a temporary directory, validates and publishes. `--check`
verifies named assets, hashes and source fingerprint; `--demo <directory>`
also checks freshly generated HTML. Errors print an actionable message and
return non-zero. Locate the direct `meta.generated` string in the JSON token
stream, require an ISO calendar date and replace only that value for comparison.
Keep every other JSON/HTML byte intact; parse-and-reserialise is not sufficient.
Validate PNG chunk CRCs, complete pixel rows and end marker, not only dimensions.

- [ ] Capture actual file routes `#/overview`, `#/org`, `#/agents/D3-A05`,
  `#/identity`, `#/ontology` at 1440 x 1000, light/reduced-motion, en-GB/UTC.
  Wait for real view/identity/ontology content; block/report external requests,
  collect browser errors and retain only the five expected screenshot names.
- [ ] Record the browser/Playwright versions, actual dimensions, route and
  SHA-256 per screenshot. Validate all staged outputs before replacing assets.
- [ ] Add `docs-demo` generation and a strict L1 `--check --demo build/demo`
  step after the core build. Missing/stale/corrupt output must fail explicitly.
- [ ] Run focused tests GREEN, then:

```powershell
python tools\build_docs_demo.py
python tools\build_docs_demo.py --check --demo build\demo
```

Expected: five genuine images, core-only HTML and matching manifest/source.
No automatic cost model, new runtime behavior or PNG cross-platform claim.

## Task 3: Reader prose and prompt (DOC-01,02,06)

Modify `README.md`, `plugin/README.md`, `docs/README.md` and directly related
catalogue state text. Create `docs/getting-started.md`, `docs/starter-prompts.md`
and `docs/demo/README.md`. Update the unreleased changelog.

- [ ] Give docs-agent this exact outcome and allowlist; keep it off generated
  HTML/PNGs/manifest, code, historical record bodies and protected files.
- [ ] Include two Mermaid diagrams, download/open instructions, five captioned
  images with alt text and a short parameterised starter plus Caldova example.
- [ ] Remove reader-facing migration/local-intake sections, not archival files.
  Replace stale D4/D5-pending summaries with qualified merged #29 evidence.
- [ ] Add focused document contracts before prose edits: real links, no
  stale local-intake heading, expected prompt safeguards and five-image gallery.
  Run RED before edits, GREEN after.
- [ ] Run:

```powershell
python tools\dev.py docs --strict
python -m pytest tests\unit\test_docs_demo.py tests\unit\test_docs_contract.py -q --tb=short
```

## Task 4: Review, verify and internal handoff (DOC-07,08)

- [ ] Review exact source changes and the actual five screenshots; inspect the
  real offline HTML in Chromium and confirm the sample has no FinOps model.
- [ ] Regenerate package/install inventory normally; do not change versions,
  original release records, identity profiles, guardrails or historical hashes.
- [ ] Run `python tools/dev.py check --strict` and `python tools/dev.py site
  e2e --strict`. Record returned results and manual limitations accurately.
- [ ] Rebuild the isolated internal distribution and validate its exact
  allowlist, nested privacy checks and installer plan; update changed hashes,
  never reuse previous 1.9.1 ZIP digests after packaged prose changes.
- [ ] Commit scoped changes with #31 and the required co-author trailer, push
  the feature branch only and open a draft PR using the original template,
  actual gate summary and screenshot evidence.

No human-only action is delegated. Keep the worktree and deliverables available
for review. Approval, merge, tag/release, deployment, external clearance and
protected #8/#30 changes remain separate.
