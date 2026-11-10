# Anonymised distribution design

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-10 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Bounded maintainer-requested cleanup; internal distribution assumed |
| Scope | Portable current documentation, transparent receipt redaction and fail-closed package privacy checks |
| References | [Catalogue](README.md), [Issue #20](https://github.com/urruegg/frontier-envisioning/issues/20), [Idea](../ideas/2026-11-10-anonymised-distribution.md), [Plan](../plans/2026-11-10-anonymised-distribution-plan.md), [Sprint](../sprints/SPRINT-002-anonymised-distribution.md) |

## Architecture and acceptance

1. Remove the literal legacy enterprise handle from current tracked file
   contents. Replace machine-specific examples with workspace-neutral paths
   and bootstrap test identities with synthetic values. Do not remove the
   intended public-cloud maintainer or copyright/licence attribution.
2. Mark the current intake owner field as explicitly redacted; retain the
   original receipt in private history. Its 249 file records must retain
   canonical SHA-256
   `6ea788a8cf56423fcbec5a20eca1bf60f2ee077c9247fbe7dbd4138220f35845`.
   Do not relabel an original enterprise owner as the current owner.
3. Keep one shared `distribution_errors(entries)` validator in the existing
   package builder. Both package and complete-bundle builders call it before
   writing the inventory, archive or checksum output. A failed build returns
   an explicit error and must not overwrite previously valid output.
4. Inspect member names, UTF-8 text, nested ZIP members and archive/member
   comments. Reject enterprise-suffix identifiers, Windows/macOS personal
   profile paths, forbidden secret-file names, existing credential-pattern
   matches and explicitly internal classified Markdown metadata. Decode common
   percent/HTML/unicode escapes for inspection, not by rewriting source bytes.
5. Bound ZIP inspection to three ZIP containers per path, including the outer
   container, and eight MiB per inspected
   archive/member. Malformed, encrypted or oversized content must fail rather
   than be silently skipped. These are bounded technical checks, not exhaustive
   PII, image/OCR or legal clearance.
6. Preserve legitimate privacy-feature strings in code. The complete bundle
   uses its explicit named distribution documents/demo; remove the analysis
   folder wildcard. Retain PRD, solution design, licences and notices.
7. Preserve archive ordering, fixed dates/permissions and source bytes for valid
   entries. Keep the existing install manifest/skill contract and offline runtime.
   The existing unreleased 1.6.1 can change; older release/raster records cannot.
8. Rebuild normally; inspect the exact finished archives, checksums and install
   plan. Require targeted regression and strict full-gate success. No Cowork
   installation, tag, release, deployment or external-distribution approval is
   inferred from the local offline verification.

## Explicit boundaries

The real local checkout directory, Git metadata/remotes, prior commits, original
release records and the private session assessment are not renamed or rewritten.
Removing a string from current content does not erase it from those surfaces.
The repository remains private. Protected hooks, ownership, licences and release
workflows remain human-controlled. Implementation is inline, not delegated.
