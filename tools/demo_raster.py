# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Replay verified 1.4.0 rasters only when all version-approved generated inputs match.

The archived PNG bytes avoid undeclared SVG converters and platform-dependent floating-point
rasterisation. This does not replay the golden ZIP: code still generates its remaining files,
and any changed input or tampered raster blocks the build.
The finite 1.6.1 and 1.7.1 input profiles retain 1.6.0 raster provenance. A present
current release record is authority for the finished rebuilt ZIP, not the old rasters.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from fe_lib import ROOT

PROFILE = ROOT / "tests" / "fixtures" / "caldova-raster-1.4.0"
SUPPORTED_VERSIONS = {"1.4.0", "1.5.0", "1.6.0"}
PREVIEW_VERSIONS = {"1.6.1", "1.7.1", "1.9.1", "1.9.2"}
BASE_PROFILE_SHA256 = "46d37eef1a55f8655c4d09447b6335e39ec3b356621186339404c813ecfa5d15"
CURRENT_INPUT_PROFILE = "tests/fixtures/caldova-raster-1.6.1-inputs.json"
CURRENT_INPUT_PROFILE_SHA256 = "27e0277754cecfa6239f4138e810aecd4908622ff6537da456dc2fc222108236"
INTEGRATED_INPUT_PROFILE = "tests/fixtures/caldova-raster-1.7.1-inputs.json"
INTEGRATED_INPUT_PROFILE_SHA256 = "d9bd99a7a5ac020f1ade201e898dacd4cb8a6230839707188bb62f250e251a58"
PROCESS_INPUT_PROFILE = "tests/fixtures/caldova-raster-1.9.1-inputs.json"
PROCESS_INPUT_PROFILE_SHA256 = "d91044f03bb34f6559eddc8debf035a5d3aa697d7800d723a700528b23004453"
CANDIDATE_INPUT_PROFILE = "tests/fixtures/caldova-raster-1.9.2-inputs.json"
CANDIDATE_INPUT_PROFILE_SHA256 = "b3326eb48d42862979f537c788aa88f16bd40caa0fb96185bc410b9c3e1851c0"
CURRENT_INPUT_PATHS = {"catalog.html", "scripts/identity_docs.py"}
IDENTITY_ARCHIVE = "Caldova - agent identity package v1.0.zip"


class RasterProfileError(Exception):
    pass


def _path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise RasterProfileError(f"invalid raster profile path: {relative!r}")
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts or not path.resolve().is_relative_to(root.resolve()):
        raise RasterProfileError(f"raster profile path escapes its root: {relative!r}")
    return path


def _verify(data: bytes, expected: str, label: str) -> None:
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected) or hashlib.sha256(data).hexdigest() != expected:
        raise RasterProfileError(f"raster profile {label} hash differs")


def _read_record(path: Path, label: str) -> dict:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RasterProfileError(f"{label} is missing or malformed: {path.name}") from exc
    if not isinstance(record, dict):
        raise RasterProfileError(f"{label} must be an object")
    return record


def _release_identity_digest(version: str) -> str:
    release = _read_record(ROOT / "releases" / version / "manifest.json", f"{version} release record")
    artefacts = release.get("artefacts")
    if not isinstance(artefacts, list) or not all(isinstance(a, dict) for a in artefacts):
        raise RasterProfileError(f"{version} release record artefacts are malformed")
    identities = [a.get("sha256") for a in artefacts if a.get("name") == IDENTITY_ARCHIVE]
    if len(identities) != 1 or not isinstance(identities[0], str) or not re.fullmatch(r"[0-9a-f]{64}", identities[0]):
        raise RasterProfileError(f"{version} release record identity digest is missing or malformed")
    return identities[0]


def _current_inputs(inputs: dict, version: str) -> tuple[dict, dict]:
    profiles = {
        "1.6.1": (CURRENT_INPUT_PROFILE, CURRENT_INPUT_PROFILE_SHA256),
        "1.7.1": (INTEGRATED_INPUT_PROFILE, INTEGRATED_INPUT_PROFILE_SHA256),
        "1.9.1": (PROCESS_INPUT_PROFILE, PROCESS_INPUT_PROFILE_SHA256),
        "1.9.2": (CANDIDATE_INPUT_PROFILE, CANDIDATE_INPUT_PROFILE_SHA256),
    }
    if version not in profiles:
        raise RasterProfileError(f"current input profile is not approved for {version}")
    relative, profile_digest = profiles[version]
    path = ROOT / relative
    record = _read_record(path, "current input profile")
    _verify(path.read_bytes(), profile_digest, "current input profile")
    if (set(record) != {"schema", "version", "base_profile_sha256", "inputs"}
            or record["schema"] != "frontier-demo-current-inputs/1.0" or record["version"] != version
            or record["base_profile_sha256"] != BASE_PROFILE_SHA256):
        raise RasterProfileError("current input profile schema, version or base hash differs")
    overrides = record["inputs"]
    if not isinstance(overrides, dict) or set(overrides) != CURRENT_INPUT_PATHS:
        raise RasterProfileError("current input profile must override exactly the two approved paths")
    for name, digest in overrides.items():
        if (name not in inputs or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or digest == inputs[name]):
            raise RasterProfileError(f"current input profile override is invalid: {name}")
    return dict(inputs, **overrides), {
        "version": version, "path": relative, "sha256": profile_digest,
        "changed_paths": sorted(overrides),
    }


def verify_release_identity(archive: Path, report: dict) -> None:
    """Verify the completed canonical archive; only the explicit unreleased preview has no digest."""
    expected = report.get("expected_release_identity_sha256")
    if expected is None:
        if report.get("version") in PREVIEW_VERSIONS and report.get("preview") is True:
            return
        raise RasterProfileError("finished identity archive has no authoritative release digest")
    _verify(archive.read_bytes(), expected, "finished identity archive")


def replay(kit: Path, profile_dir: Path = PROFILE, version: str = "1.4.0") -> dict:
    if version not in SUPPORTED_VERSIONS | PREVIEW_VERSIONS:
        raise RasterProfileError(f"historical raster replay is not approved for {version}")
    manifest_path = profile_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RasterProfileError("verified 1.4.0 raster profile is missing")
    if version in PREVIEW_VERSIONS:
        _verify(manifest_path.read_bytes(), BASE_PROFILE_SHA256, "current input profile base")
    manifest = _read_record(manifest_path, "historical raster profile")
    if manifest.get("schema") != "frontier-demo-raster/1.0" or manifest.get("version") != "1.4.0":
        raise RasterProfileError("unsupported historical raster profile")
    reference_version = "1.6.0" if version in PREVIEW_VERSIONS else version
    release_path = ROOT / "releases" / reference_version / "manifest.json"
    if not release_path.is_file():
        raise RasterProfileError(f"raster reference release record is missing: {reference_version}")
    expected_source = _release_identity_digest(reference_version)
    if manifest.get("source_archive_sha256") != expected_source:
        raise RasterProfileError("raster profile provenance does not match the release record")
    inputs, assets = manifest.get("inputs"), manifest.get("assets")
    if not isinstance(inputs, dict) or not inputs or not isinstance(assets, dict) or not assets:
        raise RasterProfileError("raster profile inputs or assets are missing")
    current_profile = None
    expected_release = expected_source
    preview = version in PREVIEW_VERSIONS and not (ROOT / "releases" / version / "manifest.json").exists()
    if version in PREVIEW_VERSIONS:
        inputs, current_profile = _current_inputs(inputs, version)
        expected_release = None if preview else _release_identity_digest(version)
    files = [p for p in kit.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    generated = {p.relative_to(kit).as_posix() for p in files if p.suffix.lower() != ".png" and p != kit / "README.md"}
    if generated != set(inputs):
        raise RasterProfileError("generated input inventory differs from the historical raster profile")
    existing_rasters = {p.relative_to(kit).as_posix() for p in files if p.suffix.lower() == ".png"}
    if not existing_rasters.issubset(assets):
        raise RasterProfileError("generated raster inventory differs from the historical profile")
    for name, digest in inputs.items():
        _verify(_path(kit, name).read_bytes(), digest, f"input {name}")
    pending = []
    for name, digest in assets.items():
        target = _path(kit, name)
        source = _path(profile_dir / "assets", name)
        if target.suffix.lower() != ".png" or not source.is_file():
            raise RasterProfileError(f"raster profile asset is missing or not PNG: {name}")
        data = source.read_bytes()
        _verify(data, digest, f"asset {name}")
        pending.append((target, data))
    readme_hash = manifest.get("readme_sha256")
    if not isinstance(readme_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", readme_hash):
        raise RasterProfileError("raster profile README hash is missing")
    for target, data in pending:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    visuals = sum(Path(name).name == "card.png" or Path(name).parent.as_posix() == "visuals" for name in assets)
    return {"method": "frozen-release-raster", "converted": 0, "restored": len(pending), "restored_visuals": visuals,
            "profile_version": "1.4.0", "source_archive_sha256": expected_source, "readme_sha256": readme_hash,
            "version": version, "reference_version": reference_version, "preview": preview,
            "current_input_profile": current_profile, "verified_inputs": len(inputs),
            "expected_release_identity_sha256": expected_release}
