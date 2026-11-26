# Offline Agent Factory data contract

This contract checks recorded evidence and ordinary file bytes. It does not
authenticate reviewers, grant sharing or tenant permission, acquire source,
or authorise a build. Imported documents, policies and validator text are
passive data. Nothing from the supplied foundation is imported or executed.

## Producer request and receiver record

`factory_contract.request_shape(upstream)` returns a separate strict
`frontier-agent-factory-request/1.0` schema. The installed receiver schema is
fingerprinted and deep-copied, never extended or edited. In the **request**,
provided `source.sha256` and `baseline.sha256` must be absent. The producer
computes them separately from actual bytes. All other receiver fields and
unknown-field restrictions remain intact.

The request has exactly these fields:

- `schema`, `export_id`, `created_at`, `customer_scope`, `evidence_kind`;
- `template`: repository, selection, commit, release, discovery,
  bootstrap approval, acquisition and root prefix;
- `intake`: receiver 1.0 data, except the two computed hashes are absent;
- `blueprint`: `source_path` and `baseline_path`;
- `id_map`: original-to-factory `solutions`, `agents` and `requirements` maps;
- `selection_evidence`: selected solution, original solution and agents,
  rationale and unique dependency-gap IDs (exact lowercase hyphenated IDs,
  at most 80 characters; reference resolution belongs to projection);
- `sharing_review`: matching customer scope, metadata approval and an
  artefact approval map keyed by `<intake-id>:<artifact-id>`;
- `history`: up to 127 prior accepted record IDs;
- `financial`: `requested`, `as_of`, `claim`, `packets`.

Call `prevalidate_request(request, upstream)` **before** indexing the request,
materialising files or invoking a sibling. It checks every nested shape,
typed dynamic map, path and approval. It returns `None` on success and raises
`FactoryError` with a fixed, non-private diagnostic on refusal. An engineering
gap is not an excuse for absent owners, acquisition or transfer evidence.

`materialize(data, baseline_root, source_root, read_file)` independently checks
the input intake shape first. It returns
`(detached_record, baseline_by_portable_path, originals_by_portable_path)`.
The maps contain bytes, with forward-slash lookup keys. The record retains
the original path spellings, including valid Windows backslashes. Input
records and files are never mutated. `read_file(root, relative, limit)` must
return bounded ordinary bytes; `factory_common.read` supplies that contract.
Materialisation alone is not semantic acceptance.

`validate_intake(data, schema, baseline, originals=None, history=None)`
returns `None` or raises `FactoryError`. Byte-map keys are portable paths;
case or delimiter aliases are refused before any dictionary overwrite.
Every requested history ID passes the exact lowercase, hyphenated, maximum
80-character identity check before materialisation. History is an
ID-to-decoded-record map. Keep each historical JSON file's
original raw bytes separately for publication; never re-encode it to change
path style. Without `originals`, validation checks baseline bytes and recorded
source hashes only. It must not be reported as original-byte verification.

`claim_path` reserves **FILE** paths. It refuses canonical ancestor/descendant
conflicts in either order, including case and delimiter aliases, before
artefact reads. Component boundaries matter: `specs.md` does not conflict
with `specs.md2/design.md`. Only explicitly requested exact source-file reuse
is allowed. Future ZIP handling must treat directory entries separately:
a valid directory and its child are not conflicting FILE claims.

## Source receipt

`source_receipt(receipt, export_id, created_at, archive_bytes)` checks frozen
receipt consistency and the actual archive digest offline. It returns `None`
or raises `FactoryError`; it performs no discovery or acquisition.

The repository is exactly `urruegg/frontier-agent-factory`. Commits are exact
lowercase 40-hex IDs. Discovery must be successful, completely paginated and
bound to this export ID. Its observation is no later than acquisition, which
is no later than creation. A new export needs its own discovery evidence.
Reproduction reuses the frozen receipt and bytes, not a fictional fresh lookup.
Receipt chronology, latest selection and time equality retain every fractional
digit and normalise timezone offsets. `timestamp_key(value)` returns an exact
`(UTC_whole_second_ordinal, fractional_digits_without_trailing_zeroes)` tuple
for comparisons; a zero fraction is the empty string. No float, decimal context
or six-digit precision cap is used. `timestamp(value)` still returns an aware
`datetime` for calendar/ZIP use, with that type's microsecond resolution.

Each release-enumeration row has exactly five fields: `id`, `tag_name`,
`published_at`, `draft`, `prerelease`. Raw API bodies, authors, assets and
historical resolved commits are not retained. Draft/prerelease tag and date
may be null. Every stable candidate must have a usable tag and valid date.
Tags follow Git ref syntax under `refs/tags/`, not an ASCII naming policy;
build metadata such as `v1.0+build.1` and valid Unicode names are allowed.
The uniquely latest published stable candidate must match `release` and
the top-level commit; only that selected tag needs resolution.

Only a healthy complete enumeration with no stable candidates permits
`unreleased-bootstrap`. That selection requires an explicit recorded approval
whose reference contains the exact immutable commit. Errors, authentication
failures, incomplete lookup, unknown stable metadata or incompatibility
never justify bootstrap or an older fallback. A local file does not prove a
fresh latest-source lookup. `root_prefix` is empty or the exact single wrapper
directory, not an arbitrary extraction path.

Acquisition records `succeeded`, `authorised-host` or `explicit-local-source`,
reviewer, time, evidence and the automatically computed raw archive digest.
These checks do not prove identity, signatures, authority or live freshness.

## Intake, privacy and limits

Each selected solution declares all eight roles: PRD, solution design,
decisions, IT readiness, identity, blueprint, value and FinOps. A role is
provided, missing or specifically not applicable. Multiple provided files
are allowed; conflicting declarations are not. Share one file through one
row's `solution_ids`, not duplicate destinations. PRD and solution design
cannot be not applicable. Short specific reasons such as “No runtime.” are
valid. The receiver's exact normalised placeholder sentinel set is refused.

Every provided file needs approved transfer evidence, even for a rejected or
needs-clarification intake. Restricted material is prohibited. Accepted
records also need recorded review approval, requirements and acceptance
criteria per solution, all applicable material, and no unresolved blocking
gap or decision. Explicit invalid acceptance fails; it is never downgraded.
Legitimate draft engineering gaps remain possible.

Originals are relative to the explicit staging root. Baselines are ordinary
files under the exact `docs/intake/records/<intake-id>/artifacts/` prefix,
including descendants such as `specs/prd.md`. Authored path spellings are
preserved, not flattened or rewritten. Allowed
extensions are `.md`, `.txt`, `.json`, `.pdf`, `.docx`, `.xlsx`, `.pptx`,
`.csv`; archives and policy replacement paths are refused. No transformation
requires identical hashes and null transformation approval. Redaction or
transformation requires distinct hashes and genuine recorded approval.
Retain authored PRD/design bytes; review a customer-safe blueprint baseline
separately. Sharing review includes metadata, filenames, references and
every provided current/historical artefact, not merely document content.

- Intake JSON: at most 1 MiB, strict UTF-8, no duplicate keys, non-finite
  numbers, overflow, trailing data, invalid dates or excessive depth.
- Each source or baseline read: nonempty, at most 16 MiB.
- One cumulative 64 MiB budget for **both** roots, including repeated
  source references. A baseline-only pass may still fail with originals.
- History: at most 128 records including current; matching accepted IDs,
  resolvable supersedes chain, no cycles or reuse of the current ID.

Paths must be relative and portable. Absolute/UNC/device/ADS, traversal,
control characters, empty components and trailing-dot/space names are
refused. Safe local reads lstat every ancestor before resolving, refuse
symlinks and Windows reparse junctions on Python 3.11, check regular-file
device/inode identity with fstat and bound the actual read with a sentinel.
This is not an OS sandbox or protection against every concurrent hostile
writer. Diagnostics never contain supplied private values or OS details.

The stdlib schema evaluator implements only the fingerprinted schema's
fixed vocabulary, with local `#/$defs` references and depth bounded to 128.
It is not a general schema framework and has no external resolver,
network access or `jsonschema` runtime dependency.

## Synthetic example and implementation boundary

The [Caldova example](../examples/caldova-handover.json) is synthetic
compatibility data, **not real consent, discovery or acquisition**. Its
approvals authenticate nobody. `tests.factory_fixture.prepare` constructs
its tiny passive foundation and reviewed ordinary files in a temporary
directory. The example's checksum identifies that synthetic ZIP, not the
complete authentic upstream checkout. `accepted=True` is also wholly
synthetic. `save` recomputes an actual template checksum, never authority.

W1 supplies data helpers and contracts only. ZIP preservation, projection,
CLI, registration and installed receiver verification are later integration
work. The financial packet shape is reserved: baseline packets need a model
path; reviewed-document packets have null model path and empty review paths;
both carry qualified artefact IDs and owner review. No financial operation
is performed here. The default is false/null/review/empty packets.

Actual Cowork discovery, install, acquisition and export remain deferred and
not performed. Node 26 is not Node 24 receiver certification. Protected
session-start still has legacy routing until a person completes #8.

## Pinned source and schema attribution

The copied [receiver schema](intake.schema.json) is from the MIT reference
`urruegg/frontier-agent-factory@0bb2b1ba13cff77ee0bc3f271baddd3f89f9165d`:
8,381 bytes, SHA256
`04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f`.
The receiver validator is retained as **test text only**, 15,736 bytes,
SHA256 `4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370`.
The [fixed profile](template-profile.json) is not configurable.
The exact upstream MIT notice for the copied packaged schema follows.

```text
MIT License

Copyright (c) 2026 Urs Rüegg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
