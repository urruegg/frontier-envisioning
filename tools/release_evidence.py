# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Resolve exact-version developer release evidence, never plugin runtime data.

GitHub reads use existing gh authentication. An offline cache proves consistency,
not a signature or protection against a local actor replacing all the evidence.
No historical retained manifest is rewritten or implicitly upgraded here.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import tempfile
import threading
import zipfile
import zlib

REPOSITORY = "urruegg/frontier-envisioning"
BASE = "repos/" + REPOSITORY
JSON_LIMIT = 1024 * 1024
SUMS_LIMIT = 16 * 1024
ZIP_LIMIT = 32 * 1024 * 1024
TOTAL_LIMIT = 64 * 1024 * 1024
SHA = re.compile(r"[0-9a-f]{40}")
HASH = re.compile(r"[0-9a-f]{64}")
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")


class EvidenceError(ValueError):
    """Release evidence could not be established or validated."""


def _require(condition, message):
    if not condition:
        raise EvidenceError(message)


def _matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _positive(value):
    return type(value) is int and value > 0


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _names(version):
    return (f"frontier-envisioning-plugin-{version}.zip", "release-manifest.json", "sbom-spdx.zip", "SHA256SUMS.txt")


def _limit(name):
    return ZIP_LIMIT if name.endswith(".zip") else SUMS_LIMIT if name == "SHA256SUMS.txt" else JSON_LIMIT


def _path(value, *, basename=False, directory=False):
    _require(isinstance(value, str) and value and not any(c in value for c in ("\\", ":", "\0", "\r", "\n")),
             "Unsafe evidence path")
    text = value[:-1] if directory and value.endswith("/") else value
    _require(all(part not in ("", ".", "..") for part in text.split("/")), "Escaping or empty evidence path")
    _require(not basename or "/" not in text, "Expected an evidence basename")


def _json(data):
    _require(len(data) <= JSON_LIMIT, "Evidence JSON exceeds 1 MiB")

    def pairs(items):
        result = {}
        for key, value in items:
            _require(key not in result, "Duplicate JSON key")
            result[key] = value
        return result

    def constant(_value):
        raise EvidenceError("Non-finite JSON value")

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise EvidenceError("Malformed evidence JSON") from exc


def _gh(endpoint, *, limit=JSON_LIMIT, download=False):
    """Bound stdout while reading; do not capture or expose gh credential diagnostics."""
    args = ["gh", "api", "--hostname", "github.com", "--method", "GET", endpoint]
    if download:
        args += ["--header", "Accept: application/octet-stream"]
    seconds = 120 if download else 30
    process = None
    timer = None
    expired = threading.Event()

    def expire():
        expired.set()
        try:
            process.kill()
        except OSError:
            pass

    try:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False)
        timer = threading.Timer(seconds, expire)
        timer.daemon = True
        timer.start()
        chunks = []
        size = 0
        while True:
            chunk = process.stdout.read(min(65536, limit + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
            _require(size <= limit, "GitHub response exceeds evidence size limit")
        code = process.wait(timeout=seconds)
        _require(not expired.is_set(), "GitHub evidence request timed out")
        _require(code == 0, "GitHub evidence request failed (access, authentication or transport)")
        return b"".join(chunks)
    except (OSError, subprocess.SubprocessError) as exc:
        raise EvidenceError("GitHub evidence request failed or timed out") from exc
    finally:
        if timer is not None:
            timer.cancel()
        if process is not None:
            # Also reap on a size/parse/transport failure; never leave a helper running.
            if process.returncode is None:
                process.kill()
            process.wait()
            process.stdout.close()


def _get(endpoint):
    return _json(_gh(endpoint))


def _remote(version):
    metadata = _get(BASE)
    _require(isinstance(metadata, dict) and metadata.get("full_name") == REPOSITORY,
             "GitHub repository identity does not match")
    found = []
    for page in range(1, 21):
        releases = _get(BASE + f"/releases?per_page=100&page={page}")
        _require(isinstance(releases, list) and len(releases) <= 100, "Malformed release enumeration")
        for release in releases:
            _require(isinstance(release, dict) and isinstance(release.get("tag_name"), str)
                     and type(release.get("draft")) is bool, "Malformed release metadata")
            if release["tag_name"] == "v" + version:
                found.append(release)
        if len(releases) < 100:
            break
    else:
        raise EvidenceError("Release enumeration exceeded 20 pages")
    _require(len(found) <= 1, "Duplicate exact-version release")
    tag_name = "v" + version
    refs = _get(BASE + "/git/matching-refs/tags/" + tag_name)
    _require(isinstance(refs, list), "Malformed tag enumeration")
    exact = []
    seen_refs = set()
    for ref in refs:
        _require(isinstance(ref, dict) and isinstance(ref.get("ref"), str)
                 and isinstance(ref.get("object"), dict), "Malformed tag ref")
        _require(ref["ref"].startswith("refs/tags/" + tag_name) and ref["ref"] not in seen_refs
                 and ref["object"].get("type") in ("tag", "commit")
                 and _matches(SHA, ref["object"].get("sha")), "Malformed or duplicate matching tag ref")
        seen_refs.add(ref["ref"])
        if ref["ref"] == "refs/tags/" + tag_name:
            exact.append(ref)
    _require(len(exact) <= 1, "Duplicate exact tag ref")
    if not found:
        _require(not exact, "Exact tag exists without a complete published release")
        return None
    release = found[0]
    _require(release["draft"] is False and isinstance(release.get("published_at"), str)
             and release["published_at"] and _positive(release.get("id")), "Release is draft, unpublished or malformed")
    _require(len(exact) == 1, "Published release lacks an exact annotated tag")
    obj = exact[0]["object"]
    _require(obj.get("type") == "tag" and _matches(SHA, obj.get("sha")), "Release tag must be annotated")
    tag = _get(BASE + "/git/tags/" + obj["sha"])
    _require(isinstance(tag, dict) and tag.get("sha") == obj["sha"] and tag.get("tag") == tag_name
             and isinstance(tag.get("object"), dict), "Annotated tag identity mismatch")
    target = tag["object"]
    _require(target.get("type") == "commit" and _matches(SHA, target.get("sha"))
             and target["sha"] != obj["sha"], "Annotated tag must directly target a full source commit")
    return release, {"repository": REPOSITORY, "version": version, "release_id": release["id"],
                     "tag_object": obj["sha"], "source_commit": target["sha"]}


def _downloads(release, version):
    names = _names(version)
    rows = release.get("assets")
    _require(isinstance(rows, list) and len(rows) == 4, "Expected exactly four release assets")
    by_name = {}
    ids = set()
    for row in rows:
        _require(isinstance(row, dict), "Malformed release asset")
        name = row.get("name")
        _require(isinstance(name, str) and name in names and name not in by_name, "Unexpected or duplicate release asset")
        _require(_positive(row.get("id")) and row["id"] not in ids and row.get("state") == "uploaded",
                 "Invalid release asset identity or state")
        size = row.get("size")
        _require(type(size) is int and 0 < size <= _limit(name), "Invalid advertised release asset size")
        by_name[name] = row
        ids.add(row["id"])
    _require(sum(row["size"] for row in rows) <= TOTAL_LIMIT, "Advertised downloads exceed 64 MiB")
    assets = {}
    with tempfile.TemporaryDirectory(prefix="frontier-release-evidence-") as directory:
        for name in names:
            row = by_name[name]
            data = _gh(BASE + f"/releases/assets/{row['id']}", limit=_limit(name), download=True)
            _require(len(data) == row["size"], "Downloaded asset differs from advertised size")
            _require(sum(map(len, assets.values())) + len(data) <= TOTAL_LIMIT, "Downloads exceed 64 MiB")
            # No manifest URL, archive member or metadata path chooses a filesystem destination.
            (Path(directory) / name).write_bytes(data)
            assets[name] = data
    return assets


def _expected(rows, version):
    _require(isinstance(rows, list) and len(rows) == 4, "Expected exactly four reproduction artefacts")
    result = {}
    paths = set()
    normalised = 0
    for row in rows:
        _require(isinstance(row, (list, tuple)) and len(row) == 3, "Malformed expected artefact")
        name, path, how = row
        _path(name, basename=True)
        _path(path)
        _require(name.casefold() not in {n.casefold() for n in result} and path.casefold() not in paths,
                 "Duplicate expected artefact")
        _require(how is None or how == "generated-date" and name.endswith(".html"),
                 "Only HTML generated-date normalisation is supported")
        normalised += how is not None
        result[name] = (path, how)
        paths.add(path.casefold())
    _require(normalised == 1 and _names(version)[0] in result, "Unexpected reproduction contract")
    return result


def _zip_member(data, entry, remaining):
    """Validate the full raw STORED/DEFLATED span, not ZipExtFile's truncated view."""
    _require(entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
             "Unsupported ZIP compression method; only STORED and DEFLATED are accepted")
    offset = entry.header_offset
    _require(0 <= offset <= len(data) - 30, "Invalid ZIP local header offset")
    header = struct.unpack_from("<4s5H3I2H", data, offset)
    _require(header[0] == b"PK\x03\x04" and header[2] == entry.flag_bits and header[3] == entry.compress_type,
             "ZIP local/central header mismatch")
    if not entry.flag_bits & 8:  # Streaming writers may leave sizes/CRC to a data descriptor.
        _require(header[6:9] == (entry.CRC, entry.compress_size, entry.file_size), "ZIP local/central size or CRC mismatch")
    position = offset + 30 + header[-2] + header[-1]
    end = position + entry.compress_size
    _require(position <= end <= len(data), "ZIP compressed span exceeds archive")
    allowed = min(entry.file_size, remaining)
    count = crc = 0
    decoder = zlib.decompressobj(-zlib.MAX_WBITS) if entry.compress_type == zipfile.ZIP_DEFLATED else None
    pending = b""
    while True:
        # A one-byte sentinel detects a dishonest length without expanding the rest.
        maximum = min(65536, allowed - count + 1)
        if decoder is None:
            output = data[position:min(end, position + maximum)]
            position += len(output)
        else:
            if not pending and position < end:
                pending = data[position:min(end, position + 65536)]
                position += len(pending)
            output = decoder.decompress(pending, maximum)
            pending = decoder.unconsumed_tail
        count += len(output)
        _require(count <= allowed, f"ZIP expanded content exceeds allowed size ({count} > {allowed})")
        crc = zlib.crc32(output, crc)
        if decoder is None:
            if position == end:
                break
        elif decoder.eof:
            _require(not decoder.unused_data and not pending and position == end, "Extra bytes after complete DEFLATE stream")
            break
        else:
            _require(pending or position < end or output, "Incomplete DEFLATE stream")
    _require(count == entry.file_size, "ZIP actual decoded size differs from declared size")
    _require(crc == entry.CRC, "ZIP actual decoded CRC mismatch")
    return count


def _zip(data):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            seen = set()
            expanded = 0
            for entry in archive.infolist():
                _path(entry.filename, directory=entry.is_dir())
                _require(entry.filename == entry.orig_filename, "Truncated ZIP member name")
                key = entry.filename.rstrip("/").casefold()
                _require(key not in seen, "Duplicate ZIP member")
                seen.add(key)
                mode = entry.external_attr >> 16
                _require(stat.S_IFMT(mode) in (0, stat.S_IFREG, stat.S_IFDIR), "Symlink or special ZIP member")
                _require(not entry.flag_bits & 1, "Encrypted ZIP is not supported")
                _require(entry.file_size <= TOTAL_LIMIT - expanded, "ZIP expanded content exceeds 64 MiB")
                expanded += _zip_member(data, entry, TOTAL_LIMIT - expanded)
            # Retain the reader's structural/local-name/overlap checks, but only
            # after raw streams have passed complete, bounded size/CRC validation.
            _require(archive.testzip() is None, "ZIP integrity check failed")
    except (zipfile.BadZipFile, zlib.error, struct.error, RuntimeError, NotImplementedError, OSError, EOFError) as exc:
        raise EvidenceError("Invalid release ZIP") from exc


def _checksums(assets, version):
    data = assets["SHA256SUMS.txt"]
    _require(len(data) <= SUMS_LIMIT, "Checksums exceed 16 KiB")
    try:
        text = data.decode("ascii")
    except UnicodeError as exc:
        raise EvidenceError("Malformed checksums") from exc
    rows = text.splitlines()
    _require(len(rows) == 3, "Expected exactly three checksum rows")
    seen = set()
    for row in rows:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", row)
        _require(match is not None, "Malformed lowercase SHA-256 checksum row")
        checksum, name = match.groups()
        _path(name, basename=True)
        _require(name in _names(version)[:3] and name not in seen, "Unexpected or duplicate checksum name")
        _require(_hash(assets[name]) == checksum, "Downloaded payload checksum mismatch")
        seen.add(name)
    _require(seen == set(_names(version)[:3]), "Missing payload checksum")


def _source(manifest, identity):
    source = manifest.get("build_evidence")
    _require(isinstance(source, dict), "Missing build evidence")
    _require(source.get("repository") == REPOSITORY and source.get("source_commit") == identity["source_commit"]
             and _matches(SHA, source.get("control_commit")), "Build evidence source/repository mismatch")
    _require(source.get("native_attestation") == "not-provided", "Unsupported native attestation claim")
    _require("publication" not in source or source["publication"] == "not-performed",
             "Unsupported build-time publication claim")
    profile = source.get("profile")
    if profile == "local-tag-manual-publication/1.0":
        _require(source.get("source_tag") == "v" + identity["version"]
                 and source.get("tag_object") == identity["tag_object"]
                 and source.get("publication") == "not-performed", "Local tag build evidence mismatch")
    elif profile == "github-owner-dispatch-publication/1.0":
        _require(source.get("intended_tag") == "v" + identity["version"]
                 and source["control_commit"] == identity["source_commit"], "Workflow tag/source mismatch")
        for field in ("run_id", "run_attempt"):
            _require(isinstance(source.get(field), str) and re.fullmatch(r"[1-9][0-9]*", source[field]),
                     "Invalid workflow run identity")
        _require(source.get("run_url") == f"https://github.com/{REPOSITORY}/actions/runs/{source['run_id']}"
                 and source.get("manual_checks") == "confirmed by dispatching maintainer", "Workflow evidence mismatch")
    else:
        raise EvidenceError("Unknown build evidence profile; use explicit retained legacy verification")


def _validate(assets, identity, expected):
    version = identity["version"]
    _require(set(assets) == set(_names(version)), "Unexpected evidence files")
    _require(sum(map(len, assets.values())) <= TOTAL_LIMIT, "Evidence files exceed 64 MiB")
    for name, data in assets.items():
        _require(0 < len(data) <= _limit(name), "Evidence file exceeds size limit")
    _checksums(assets, version)
    for name in (_names(version)[0], "sbom-spdx.zip"):
        _zip(assets[name])
    manifest = _json(assets["release-manifest.json"])
    _require(isinstance(manifest, dict) and manifest.get("schema") == "frontier-release-manifest/1.0"
             and manifest.get("version") == version and manifest.get("not_reproduced") == [],
             "Manifest schema/version/reproduction mismatch")
    _require(isinstance(manifest.get("provenance"), str) and bool(manifest["provenance"]), "Missing manifest provenance")
    try:
        dt.date.fromisoformat(manifest["date"])
    except (KeyError, TypeError, ValueError) as exc:
        raise EvidenceError("Malformed manifest date") from exc
    rows = manifest.get("artefacts")
    _require(isinstance(rows, list) and len(rows) == 4, "Expected exactly four manifest artefacts")
    seen = set()
    for row in rows:
        _require(isinstance(row, dict), "Malformed manifest artefact")
        name = row.get("name")
        _require(isinstance(name, str) and name in expected and name not in seen, "Unexpected or duplicate manifest artefact")
        path, how = expected[name]
        _require(row.get("build_path") == path, "Manifest build path mismatch")
        _require(type(row.get("bytes")) is int and row["bytes"] > 0 and _matches(HASH, row.get("sha256")),
                 "Malformed artefact size/hash")
        fields = {"name", "build_path", "bytes", "sha256"}
        if how:
            fields |= {"normalise", "sha256_normalised"}
            _require(row.get("normalise") == how and _matches(HASH, row.get("sha256_normalised")),
                     "Malformed HTML generated-date normalisation")
        _require(set(row) == fields, "Unexpected artefact fields or normalisation")
        if name == _names(version)[0]:
            _require(row["sha256"] == _hash(assets[name]) and row["bytes"] == len(assets[name]),
                     "Plugin reproduction hash/size differs from actual download")
        seen.add(name)
    _source(manifest, identity)
    return manifest


def _git(root, *args, missing=False):
    try:
        result = subprocess.run(["git", "--no-pager", "-C", str(root), *args], capture_output=True, text=True,
                                encoding="utf-8", timeout=30, check=False)
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        raise EvidenceError("Cannot establish local annotated tag identity") from exc
    if missing and result.returncode == 1:
        return None
    _require(result.returncode == 0, "Cannot establish local annotated tag identity")
    return result.stdout.strip()


def _local(root, version, *, required):
    ref = "refs/tags/v" + version
    obj = _git(root, "rev-parse", "--verify", "--quiet", ref, missing=True)
    if obj is None:
        _require(not required, "Offline cache requires the exact local annotated tag")
        return None
    _require(_matches(SHA, obj) and _git(root, "cat-file", "-t", ref) == "tag", "Local exact tag must be annotated")
    header = _git(root, "cat-file", "-p", ref).split("\n\n", 1)[0].splitlines()
    _require(len(header) >= 3 and header[0].startswith("object ") and header[1] == "type commit"
             and header[2] == "tag v" + version, "Local annotated tag identity mismatch")
    commit = header[0][7:]
    _require(_matches(SHA, commit) and _git(root, "cat-file", "-t", commit) == "commit",
             "Local annotated tag must target a real commit")
    return {"source_commit": commit, "tag_object": obj}


def _cache_path(root, version):
    path = root
    for part in ("", "build", "release-evidence", version):
        path = path / part
        _require(not path.is_symlink() and (not path.exists() or path.is_dir()), "Unsafe cache directory")
    return path


def _file(path, limit):
    _require(not path.is_symlink() and path.is_file() and stat.S_ISREG(path.stat().st_mode), "Unsafe cache file")
    _require(0 < path.stat().st_size <= limit, "Cache file exceeds size limit")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    _require(0 < len(data) <= limit, "Cache file exceeds size limit")
    return data


def _cached(root, version, expected, *, identity=None):
    directory = _cache_path(root, version)
    if not directory.exists():
        return None
    entries = list(directory.iterdir())
    _require(len(entries) == 1, "Partial, duplicate or unexpected evidence cache")
    source_path = entries[0]
    _require(_matches(SHA, source_path.name) and not source_path.is_symlink() and source_path.is_dir(),
             "Malformed cache source directory")
    _require({p.name for p in source_path.iterdir()} == {*_names(version), "evidence.json"}, "Unexpected cache file inventory")
    record = _json(_file(source_path / "evidence.json", JSON_LIMIT))
    fields = {"schema", "repository", "version", "release_id", "tag_object", "source_commit", "files"}
    _require(isinstance(record, dict) and set(record) == fields
             and record["schema"] == "frontier-release-evidence-cache/1.0" and record["repository"] == REPOSITORY
             and record["version"] == version and record["source_commit"] == source_path.name
             and _positive(record["release_id"]) and _matches(SHA, record["tag_object"])
             and record["tag_object"] != record["source_commit"], "Malformed cache identity")
    if identity is None:
        local = _local(root, version, required=True)
        _require(all(record[key] == value for key, value in local.items()), "Offline cache source/tag differs from local tag")
    else:
        _require(all(record[key] == value for key, value in identity.items()), "Existing cache conflicts with published identity")
    digests = record["files"]
    _require(isinstance(digests, dict) and set(digests) == set(_names(version))
             and all(_matches(HASH, value) for value in digests.values()), "Malformed cached file digests")
    assets = {name: _file(source_path / name, _limit(name)) for name in _names(version)}
    _require(all(_hash(data) == digests[name] for name, data in assets.items()), "Cached evidence digest mismatch")
    manifest = _validate(assets, record, expected)
    return manifest, record, assets


def _store(root, identity, expected, assets):
    version = identity["version"]
    existing = _cached(root, version, expected, identity=identity)
    if existing is not None:
        _require(existing[2] == assets, "Existing validated cache differs from fresh published bytes")
        return
    directory = _cache_path(root, version)
    directory.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix=".pending-", dir=directory) as staging:
            stage = Path(staging)
            for name, data in assets.items():
                (stage / name).write_bytes(data)
            record = {"schema": "frontier-release-evidence-cache/1.0", **identity,
                      "files": {name: _hash(data) for name, data in assets.items()}}
            (stage / "evidence.json").write_text(json.dumps(record, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
            # rename is atomic within this filesystem. Never overwrite an existing cache.
            destination = directory / identity["source_commit"]
            _require(not destination.exists() and not destination.is_symlink(), "Cache appeared during validation")
            os.rename(stage, destination)
    finally:
        if directory.exists() and not any(directory.iterdir()):
            directory.rmdir()


def _outcome(status, version, message, manifest=None, source=None):
    return {"status": status, "version": version, "source_commit": source, "manifest": manifest, "message": message}


def resolve(root: Path, version: str, expected_artefacts: list, *, online=False) -> dict:
    """Return validated evidence or an explicit absence outcome.

    CI callers use online=True, which always queries GitHub afresh. Explicit
    offline calls never contact GitHub, including when executed inside CI.
    """
    _require(_matches(VERSION, version), "Release version must be canonical X.Y.Z")
    expected = _expected(expected_artefacts, version)
    root = Path(root)
    try:
        if not online:
            cached = _cached(root, version, expected)
            if cached is None:
                return _outcome("not-performed", version, "Published-release comparison not performed: no offline evidence")
            manifest, identity, _assets = cached
        else:
            remote = _remote(version)
            if remote is None:
                return _outcome("development", version, f"No exact published release or conflicting tag for v{version}")
            release, identity = remote
            local = _local(root, version, required=False)
            _require(local is None or all(identity[key] == value for key, value in local.items()),
                     "Published source/tag conflicts with the local exact tag")
            assets = _downloads(release, version)
            manifest = _validate(assets, identity, expected)
            _store(root, identity, expected, assets)
        return _outcome("published", version, f"Published evidence validated for v{version}", manifest, identity["source_commit"])
    except (OSError, ValueError, RecursionError, OverflowError) as exc:
        if isinstance(exc, EvidenceError):
            raise
        raise EvidenceError("Release evidence could not be validated or cached") from exc
