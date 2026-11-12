# SPRINT-005: Internal user documentation

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-12 |
| Author | Copilot SDK in VS Code; AI-assisted delivery |
| Status | Local implementation and technical verification complete; PR/CI handoff separate |
| Scope | Reader-first documentation, generated Caldova sample, screenshots and starter prompt |
| References | [Catalogue](README.md), [Issue #31](https://github.com/urruegg/frontier-envisioning/issues/31), [Idea](../ideas/2026-11-12-internal-user-documentation.md), [Design](../specs/2026-11-12-internal-user-documentation-design.md), [Plan](../plans/2026-11-12-internal-user-documentation-plan.md) |

| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |
|---|---|---|---|---|---|---|---|
| [#31](https://github.com/urruegg/frontier-envisioning/issues/31) | [Reader journey](../ideas/2026-11-12-internal-user-documentation.md) | [Design](../specs/2026-11-12-internal-user-documentation-design.md) | [Implementation](../plans/2026-11-12-internal-user-documentation-plan.md) | `@urruegg`; parent implementation | Existing merged #29 capabilities; explicit instruction to proceed | Locally verified; no ready/approval label inferred | Implementation `4338f76`; strict L1/L2 and generated-output proof below; live PR/CI status on #31 |

The user explicitly directed implementation after the recommended scope was
presented. See the idea for exact decision evidence and the distinction from
separate written-plan review or human-only metadata changes.

Historical intake evidence remains in place. No plugin runtime feature,
visibility change, release, deployment or protected #8/#30 edit is included.

## Local implementation evidence

The checked implementation is `4338f76372bcdb7be7f591641837dd4096b76008`.
This record is a verification checkpoint, not a live PR-status tracker.

- Reader-facing local-intake narrative is replaced by a concise overview,
  getting-started guide, two Mermaid diagrams and the five-view gallery.
  Historical receipts, release records, fixtures and protected paths remain
  unchanged; none was deleted.
- The supplied long prompt is adapted into a 319-word reusable prompt and a
  separate fictitious Caldova input example. Document contracts verify
  read-only sources, conditional authorised tools, manual storage fallback,
  factual limits, customer review and FinOps off by default. This is not a
  live Cowork behaviour or installation test.
- `python tools/dev.py check --strict` ended `ALL GATES PASSED`: 414 tests,
  one expected unreleased-manifest skip, 1473 subtests, 48 self-test checks
  and 75 DOM tests. The new documentation drift gate passed against the
  freshly rebuilt core. Repository/docs/neutrality checks reported no errors
  or findings; six pre-existing ESLint warnings remain.
- `python tools/dev.py site e2e --strict` ended `ALL GATES PASSED`: 69 browser
  tests. Two new tests open the tracked HTML offline across all five pictured
  routes, reject external requests and verify the actual Turtle download
  against Python output. The inherited 32-state Preview matrix remains green.
- Initial missing-feature tests failed before implementation. Review exposed
  incomplete PNG validation, over-broad JSON normalisation, missing input
  dependencies and incomplete ordinary-value fallback. Persisted RED
  regressions drove the corrections, including CRC-valid malformed/duplicate
  PNG headers. All 15 focused tests/33 subtests pass; bounded independent
  generator review is CLEAR.
- All seven generated showcase assets match their committed bytes. The sample
  is core-only, with identity, ordinary value and requested ontology, not an
  automatic FinOps model. Screenshot/browser/source provenance is recorded in
  the generated manifest; no cross-platform PNG byte-determinism is claimed.

Ignored local logs are `build/evidence/sharing-l1.log` and
`build/evidence/sharing-l2.log`. Actual screenshots are committed and linked
from the [gallery](../demo/README.md), not represented only by temporary logs.

## Internal candidate verification

The updated user README changes the unreleased package bytes; prior 1.9.1
handoff hashes do not describe this candidate. Two package/bundle builds
produced the same three files:

| File | Bytes | SHA-256 |
|---|---:|---|
| `frontier-envisioning-plugin-1.9.1.zip` | 727282 | `5f105830008da80489d2a5c57d63fb135fdabda70a5ef19b35168c7b36833fd6` |
| `frontier-envisioning-1.9.1-complete.zip` | 4466313 | `789158405959b40f441746bfaf0a9d34e7f43186f26e985ae23ba34ce3d4bbb1` |
| `SHA256SUMS.txt` | 210 | `9854a2e577c7a8a4acd80424b072c95ede4e1dea0fac6ace5b242a2e9ec52622` |

Actual archive checks verify 93 plugin entries against committed source,
eight skills/85 skill files (seven GA, one optional Preview), fifteen complete
entries, matching embedded content/checksums and a clean nested privacy guard.
Read-only installation preparation returned eight verified copy plans and
no implicit acknowledgement or actual copies. Core identity proof still
checks 205 inputs and 223 PNGs with the unchanged corrected A6 archive hash.

Version 1.9.1 remains unreleased. Source-qualified automated evidence is not
human sign-off, actual Cowork/Fabric acceptance, manual AT certification,
repository visibility change, external/IP clearance or release permission.
