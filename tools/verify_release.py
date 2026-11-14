#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Compare freshly built artefacts with a release manifest (releases/<version>/manifest.json).

  python tools/verify_release.py [--manifest releases/1.4.0/manifest.json] [--force]

A release manifest records hashes of the plugin and internal reproduction outputs, not the upload list.
Building the same version from the
repository must give the same bytes: the plugin package, the identity kit and the catalogue exactly, the
demo blueprint after normalising its build date ("generated"). Run tools/build_package.py and
tools/build_demo.py first (python tools/dev.py check does both).

By default the manifest of the current plugin version is used. When the plugin version has no manifest
(work towards the next release), the check is skipped - unless --force names a manifest explicitly.

  python tools/verify_release.py --write release-manifest.json
      write a manifest for the current version from the built artefacts (the release workflow attaches it;
      the release manager commits it as releases/<version>/manifest.json after publishing)

CI-only --inspect-source, --prepare-source and --finalize-candidate prepare a read-only exact-tag
handover. --verify-candidate compares downloaded files with a separate clean checkout's rebuilt package.
These checks do not provide cryptographic attestation or authorise human publication.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import DEMO_HTML_NAME, ROOT, plugin_version, sha256_bytes, sha256_file  # noqa: E402

GENERATED = re.compile(rb'"generated":"\d{4}-\d{2}-\d{2}"')
REPOSITORY = "urruegg/frontier-envisioning"
PROFILE = "github-free-private-manual-publication/1.0"


def git_value(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True,
        capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()


def source_identity(source: Path, tag: str, expected: str) -> dict[str, str]:
    if not re.fullmatch(r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", tag):
        raise ValueError("release tag must be canonical vX.Y.Z")
    if not re.fullmatch(r"[0-9a-f]{40}", expected):
        raise ValueError("expected source commit must be a full SHA")
    source = source.resolve()
    if Path(git_value(source, "rev-parse", "--show-toplevel")).resolve() != source:
        raise ValueError("source must be the checkout root")
    ref = "refs/tags/" + tag
    if git_value(source, "cat-file", "-t", ref) != "tag":
        raise ValueError("release tag must be annotated")
    actual = git_value(source, "rev-parse", ref + "^{commit}")
    if actual != expected or git_value(source, "rev-parse", "HEAD") != expected:
        raise ValueError("tag, expected commit and source HEAD must agree")
    if git_value(source, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("source has tracked changes")
    value = json.loads((source / "plugin/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("version") != tag[1:]:
        raise ValueError("tag does not match the source plugin version")
    return {"source_tag": tag, "source_commit": actual,
            "tag_object": git_value(source, "rev-parse", ref)}


def github_build_evidence(identity: dict[str, str]) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch":
        raise ValueError("CI preparation requires workflow_dispatch on GitHub Actions")
    if os.environ.get("GITHUB_REF") != "refs/heads/main":
        raise ValueError("preparation control must run from main")
    if os.environ.get("GITHUB_REPOSITORY") != REPOSITORY:
        raise ValueError("unexpected preparation repository")
    workflow_ref = REPOSITORY + "/.github/workflows/release.yml@refs/heads/main"
    if os.environ.get("GITHUB_WORKFLOW_REF") != workflow_ref:
        raise ValueError("unexpected preparation workflow reference")
    workflow_commit = os.environ.get("GITHUB_WORKFLOW_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", workflow_commit) \
            or git_value(ROOT, "rev-parse", "HEAD") != workflow_commit:
        raise ValueError("workflow commit does not match the control checkout")
    if git_value(ROOT, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("control checkout has tracked changes")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "")
    if not re.fullmatch(r"[1-9]\d*", run_id) or not re.fullmatch(r"[1-9]\d*", attempt):
        raise ValueError("run ID and attempt must be positive integers")
    return {
        "profile": PROFILE, "repository": REPOSITORY, **identity,
        "workflow_ref": workflow_ref, "workflow_commit": workflow_commit,
        "run_id": int(run_id), "run_attempt": int(attempt),
        "run_url": f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
        "native_attestation": "not-provided",
    }


def normalise(data: bytes, how: str | None) -> bytes:
    if how == "generated-date":
        return GENERATED.sub(b'"generated":"0000-00-00"', data)
    return data


def verify(manifest: dict, base: Path = ROOT) -> list[str]:
    problems = []
    for art in manifest.get("artefacts", []):
        path = base / art["build_path"]
        if not path.exists():
            problems.append(f"missing: {art['build_path']} (build it first)")
            continue
        data = path.read_bytes()
        if art.get("normalise"):
            got = sha256_bytes(normalise(data, art["normalise"]))
            want = art["sha256_normalised"]
        else:
            got, want = sha256_bytes(data), art["sha256"]
        status = "ok" if got == want else "DIFFERENT"
        print(f"{status:9} {art['name']}")
        if got != want:
            problems.append(f"{art['name']}: sha256 {got} != released {want}")
    return problems


def standard_artefacts(version: str) -> list[tuple[str, str, str | None]]:
    """(name, build path, normalisation) of the plugin and internal reproduction outputs."""
    return [
        (f"frontier-envisioning-plugin-{version}.zip", f"dist/frontier-envisioning-plugin-{version}.zip", None),
        (DEMO_HTML_NAME, f"build/demo/{DEMO_HTML_NAME}", "generated-date"),
        ("Caldova - agent identity package v1.0.zip", "build/demo/identity/Caldova - agent identity package v1.0.zip", None),
        ("Caldova - agent identity catalogue.html", "build/demo/identity/caldova-agent-identity/catalog.html", None),
    ]


def write_manifest(out: Path, version: str, base: Path | None = None, evidence: dict | None = None) -> int:
    import datetime as dt
    base = ROOT if base is None else base
    arts = []
    for name, build_path, how in standard_artefacts(version):
        data = (base / build_path).read_bytes()
        art = {"name": name, "build_path": build_path, "bytes": len(data), "sha256": sha256_bytes(data)}
        if how:
            art["normalise"] = how
            art["sha256_normalised"] = sha256_bytes(normalise(data, how))
        arts.append(art)
    manifest = {"schema": "frontier-release-manifest/1.0", "version": version, "date": dt.date.today().isoformat(),
                "provenance": "Built by the release workflow from the tag v" + version + ".", "artefacts": arts, "not_reproduced": []}
    if evidence is not None:
        manifest["build_evidence"] = evidence
        manifest["provenance"] = preparation_provenance(evidence)
    out.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"manifest written: {out}")
    return 0


def publication_names(version: str) -> tuple[str, ...]:
    return (standard_artefacts(version)[0][0], "release-manifest.json", "sbom-spdx.zip", "SHA256SUMS.txt")


def json_object(path: Path) -> dict:
    if path.is_symlink():
        raise ValueError(f"JSON file must not be a symlink: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path.name}")
    return value


def validate_evidence(evidence: object) -> dict:
    fields = {"profile", "repository", "source_tag", "source_commit", "tag_object",
              "workflow_ref", "workflow_commit", "run_id", "run_attempt", "run_url", "native_attestation"}
    if not isinstance(evidence, dict) or set(evidence) != fields:
        raise ValueError("invalid build evidence fields")
    if evidence["profile"] != PROFILE or evidence["repository"] != REPOSITORY \
            or evidence["native_attestation"] != "not-provided":
        raise ValueError("unexpected build evidence profile or attestation claim")
    for field in ("source_commit", "tag_object", "workflow_commit"):
        if not isinstance(evidence[field], str) or not re.fullmatch(r"[0-9a-f]{40}", evidence[field]):
            raise ValueError(f"invalid build evidence {field}")
    tag = evidence["source_tag"]
    if not isinstance(tag, str) or not re.fullmatch(r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", tag):
        raise ValueError("invalid build evidence source tag")
    for field in ("run_id", "run_attempt"):
        if type(evidence[field]) is not int or evidence[field] < 1:
            raise ValueError(f"build evidence {field} must be a positive integer")
    if evidence["workflow_ref"] != REPOSITORY + "/.github/workflows/release.yml@refs/heads/main" \
            or evidence["run_url"] != f"https://github.com/{REPOSITORY}/actions/runs/{evidence['run_id']}":
        raise ValueError("invalid build evidence workflow or run URL")
    return evidence


def preparation_provenance(evidence: dict) -> str:
    return (f"Prepared from {evidence['source_tag']} at {evidence['source_commit']} "
            f"by workflow {evidence['workflow_commit']}; no cryptographic attestation.")


def prepare_source(source: Path, tag: str, expected: str) -> int:
    source = source.resolve()
    candidate = ROOT / "build/release-preparation"
    resolved = candidate.resolve()
    if resolved.is_relative_to(source) or source.is_relative_to(resolved) \
            or not resolved.is_relative_to(ROOT.resolve()):
        raise ValueError("source and candidate output overlap or escape the control checkout")
    if candidate.exists() or candidate.is_symlink():
        raise ValueError("candidate output already exists; use a clean preparation workspace")
    evidence = github_build_evidence(source_identity(source, tag, expected))
    for _, relative, _ in standard_artefacts(tag[1:]):
        path = source / relative
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError(f"missing or unsafe source artefact: {relative}")
    assets = candidate / "release"
    assets.mkdir(parents=True)
    write_manifest(assets / "release-manifest.json", tag[1:], base=source, evidence=evidence)
    name = publication_names(tag[1:])[0]
    shutil.copyfile(source / "dist" / name, assets / name)
    print("candidate prepared; SBOM, finalization and human verification remain required")
    return 0


def candidate_contract(candidate: Path, complete: bool) -> tuple[dict, dict, Path]:
    assets = candidate / "release"
    if candidate.is_symlink() or assets.is_symlink() or not assets.is_dir():
        raise ValueError("invalid candidate asset directory")
    manifest = json_object(assets / "release-manifest.json")
    if manifest.get("schema") != "frontier-release-manifest/1.0":
        raise ValueError("unsupported candidate manifest schema")
    evidence = validate_evidence(manifest.get("build_evidence"))
    version = evidence["source_tag"][1:]
    if manifest.get("version") != version or manifest.get("provenance") != preparation_provenance(evidence):
        raise ValueError("candidate manifest version or provenance mismatch")
    names = set(publication_names(version))
    if not complete:
        names.remove("SHA256SUMS.txt")
    entries = list(assets.iterdir())
    if {p.name for p in entries} != names or any(p.is_symlink() or not p.is_file() for p in entries):
        raise ValueError("candidate assets do not match the exact publication allowlist")
    records = manifest.get("artefacts")
    expected = standard_artefacts(version)
    if not isinstance(records, list) or len(records) != len(expected):
        raise ValueError("invalid candidate reproduction records")
    for record, (name, relative, how) in zip(records, expected):
        if not isinstance(record, dict) or record.get("name") != name \
                or record.get("build_path") != relative or record.get("normalise") != how \
                or type(record.get("bytes")) is not int or record["bytes"] < 0:
            raise ValueError("invalid candidate reproduction entry")
        for key in ("sha256", "sha256_normalised") if how else ("sha256",):
            value = record.get(key)
            if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("invalid candidate reproduction digest")
    package = assets / publication_names(version)[0]
    if package.stat().st_size != records[0]["bytes"] or sha256_file(package) != records[0]["sha256"]:
        raise ValueError("candidate package does not match the reproduction manifest")
    return manifest, evidence, assets


def checksum_text(assets: Path, version: str) -> str:
    return "".join(f"{sha256_file(assets / name)}  {name}\n"
                   for name in sorted(publication_names(version)) if name != "SHA256SUMS.txt")


def verify_candidate_files(candidate: Path) -> tuple[dict, dict, Path]:
    manifest, evidence, assets = candidate_contract(candidate, complete=True)
    version = manifest["version"]
    if (assets / "SHA256SUMS.txt").read_bytes() != checksum_text(assets, version).encode("utf-8"):
        raise ValueError("candidate checksum contents mismatch")
    receipt = json_object(candidate / "receipt.json")
    if set(receipt) != {"schema", "build_evidence", "files"} \
            or receipt["schema"] != "frontier-release-preparation/1.0" \
            or receipt["build_evidence"] != evidence:
        raise ValueError("candidate receipt schema or evidence mismatch")
    actual = {name: sha256_file(assets / name) for name in publication_names(version)}
    if receipt["files"] != actual:
        raise ValueError("candidate receipt file digests mismatch")
    return manifest, evidence, assets


def finalize_candidate() -> int:
    candidate = ROOT / "build/release-preparation"
    manifest, evidence, assets = candidate_contract(candidate, complete=False)
    identity = {key: evidence[key] for key in ("source_tag", "source_commit", "tag_object")}
    if github_build_evidence(identity) != evidence:
        raise ValueError("candidate evidence does not match the current CI context")
    version = manifest["version"]
    (assets / "SHA256SUMS.txt").write_text(checksum_text(assets, version), encoding="utf-8", newline="\n")
    receipt = {"schema": "frontier-release-preparation/1.0", "build_evidence": evidence,
               "files": {name: sha256_file(assets / name) for name in publication_names(version)}}
    (candidate / "receipt.json").write_text(json.dumps(receipt, indent=1) + "\n", encoding="utf-8", newline="\n")
    verify_candidate_files(candidate)
    print("candidate files verified; independent reproduction and human publication remain required")
    return 0


def verify_candidate(candidate: Path, source: Path, tag: str, expected: str, workflow: str) -> int:
    if not re.fullmatch(r"[0-9a-f]{40}", workflow):
        raise ValueError("expected workflow commit must be a full SHA")
    if candidate.resolve().is_relative_to(source.resolve()) or source.resolve().is_relative_to(candidate.resolve()):
        raise ValueError("candidate and independent source must not overlap")
    identity = source_identity(source, tag, expected)
    manifest, evidence, assets = verify_candidate_files(candidate)
    if any(evidence[key] != value for key, value in identity.items()):
        raise ValueError("candidate evidence does not match the independent source identity")
    if evidence["workflow_commit"] != workflow:
        raise ValueError("candidate workflow does not match the reviewed workflow commit")
    name = publication_names(manifest["version"])[0]
    independent = source / "dist" / name
    if not independent.is_file() or independent.is_symlink() \
            or not independent.resolve().is_relative_to(source.resolve()):
        raise ValueError("independent rebuilt package is missing or unsafe")
    if sha256_file(independent) != sha256_file(assets / name) \
            or independent.read_bytes() != (assets / name).read_bytes():
        raise ValueError("candidate bytes differ from the independent rebuilt package")
    print("candidate verified against independent package bytes; human sign-off/publication still required")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", help="release manifest (default: releases/<plugin version>/manifest.json)")
    ap.add_argument("--force", action="store_true", help="verify even when the manifest is for another version")
    modes = ap.add_mutually_exclusive_group()
    modes.add_argument("--write", help="write a manifest for the current version from the built artefacts")
    modes.add_argument("--inspect-source", type=Path, help="inspect exact tagged source and CI preparation context")
    modes.add_argument("--prepare-source", type=Path, help="prepare plugin and manifest from exact tagged source")
    modes.add_argument("--finalize-candidate", action="store_true", help="finalize CI checksums and internal receipt")
    modes.add_argument("--verify-candidate", type=Path, help="verify a downloaded handover against an independent build")
    ap.add_argument("--tag", help="existing annotated source tag")
    ap.add_argument("--expected-commit", help="reviewed full source commit SHA")
    ap.add_argument("--independent-source", type=Path, help="separate clean source checkout containing its rebuilt package")
    ap.add_argument("--expected-workflow", help="reviewed preparation workflow commit SHA")
    a = ap.parse_args(argv)
    if a.inspect_source or a.prepare_source or a.verify_candidate or a.finalize_candidate:
        if a.manifest is not None or a.force:
            ap.error("legacy --manifest/--force arguments do not apply to preparation modes")
        if a.finalize_candidate and (a.tag is not None or a.expected_commit is not None):
            ap.error("--finalize-candidate uses its prepared manifest, not source identity arguments")
        if not a.finalize_candidate and (a.tag is None or a.expected_commit is None):
            ap.error("source modes require --tag and --expected-commit")
        if a.verify_candidate and (a.independent_source is None or a.expected_workflow is None):
            ap.error("--verify-candidate requires --independent-source and --expected-workflow")
        if not a.verify_candidate and (a.independent_source is not None or a.expected_workflow is not None):
            ap.error("independent verification arguments require --verify-candidate")
        try:
            if a.prepare_source:
                return prepare_source(a.prepare_source, a.tag, a.expected_commit)
            if a.finalize_candidate:
                return finalize_candidate()
            if a.verify_candidate:
                return verify_candidate(a.verify_candidate, a.independent_source,
                                        a.tag, a.expected_commit, a.expected_workflow)
            evidence = github_build_evidence(source_identity(a.inspect_source, a.tag, a.expected_commit))
        except subprocess.CalledProcessError as error:
            print("ERROR Git inspection: " + error.stderr.strip(), file=sys.stderr)
            return 1
        except (ValueError, OSError) as error:
            print("ERROR " + str(error), file=sys.stderr)
            return 1
        print(json.dumps(evidence, indent=1))
        return 0
    if a.tag is not None or a.expected_commit is not None \
            or a.independent_source is not None or a.expected_workflow is not None:
        ap.error("source identity arguments require a preparation mode")
    version = plugin_version()
    if a.write:
        return write_manifest(Path(a.write), version)
    path = Path(a.manifest) if a.manifest else ROOT / "releases" / version / "manifest.json"
    if not path.exists():
        print(f"no release manifest for {version}: nothing to compare (work towards the next release)")
        return 0
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("version") != version and not a.force:
        print(f"manifest is for {manifest.get('version')}, the plugin is {version}: skipped")
        return 0
    problems = verify(manifest)
    for p in problems:
        print("ERROR " + p)
    if problems and manifest.get("version") == version:
        print(f"The sources no longer reproduce the released {version}. A released version is immutable: "
              "bump the version for the next release (python tools/dev.py bump X.Y.Z) before changing the plugin.")
    print(f"release {manifest.get('version')}: {len(manifest.get('artefacts', [])) - len(problems)} of "
          f"{len(manifest.get('artefacts', []))} artefacts reproduced")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
