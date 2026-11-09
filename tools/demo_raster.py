# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Replay verified 1.4.0 raster inputs only when all regenerated non-raster inputs match.

The archived PNG bytes avoid undeclared SVG converters and platform-dependent floating-point
rasterisation. This does not replay the golden ZIP: code still generates its remaining files,
and any changed input or tampered raster blocks the build.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from fe_lib import ROOT

PROFILE = ROOT / "tests" / "fixtures" / "caldova-raster-1.4.0"


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


def replay(kit: Path, profile_dir: Path = PROFILE) -> dict:
    manifest_path = profile_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RasterProfileError("verified 1.4.0 raster profile is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "frontier-demo-raster/1.0" or manifest.get("version") != "1.4.0":
        raise RasterProfileError("unsupported historical raster profile")
    release = json.loads((ROOT / "releases" / "1.4.0" / "manifest.json").read_text(encoding="utf-8"))
    expected_source = next(a["sha256"] for a in release["artefacts"] if a["name"] == "Caldova - agent identity package v1.0.zip")
    if manifest.get("source_archive_sha256") != expected_source:
        raise RasterProfileError("raster profile provenance does not match the release record")
    inputs, assets = manifest.get("inputs"), manifest.get("assets")
    if not isinstance(inputs, dict) or not inputs or not isinstance(assets, dict) or not assets:
        raise RasterProfileError("raster profile inputs or assets are missing")
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
            "profile_version": "1.4.0", "source_archive_sha256": expected_source, "readme_sha256": readme_hash}
