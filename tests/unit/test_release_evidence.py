# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Offline resolver tests: real Git, ZIP, JSON, hashes and cache; fake only gh."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from tools import release_evidence as evidence
from tools.verify_release import standard_artefacts


REPOSITORY = "urruegg/frontier-envisioning"
BASE = "repos/" + REPOSITORY
VERSION = "1.10.0"
TAG = "v" + VERSION
PLUGIN = f"frontier-envisioning-plugin-{VERSION}.zip"
NAMES = (PLUGIN, "release-manifest.json", "sbom-spdx.zip", "SHA256SUMS.txt")
REAL_POPEN = subprocess.Popen


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, ensure_ascii=False).encode()


def tiny_zip(name="synthetic.txt", data=b"offline fixture", symlink=False, compression=zipfile.ZIP_STORED):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        info = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = (0o120777 if symlink else 0o100644) << 16
        info.compress_type = compression
        archive.writestr(info, data)
    return stream.getvalue()


class FakeProcess:
    def __init__(self, data, returncode=0):
        self.stdout = io.BytesIO(data)
        self.returncode = returncode

    def wait(self, timeout=None):
        return self.returncode

    def kill(self):
        self.returncode = -1


class ReleaseEvidence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "--quiet")
        self.git("-c", "user.name=Offline Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--quiet", "--allow-empty", "-m", "Synthetic source")
        self.source = self.git("rev-parse", "HEAD")
        self.git("-c", "user.name=Offline Fixture", "-c", "user.email=fixture@example.invalid",
                 "tag", "-a", TAG, "-m", "Synthetic annotated tag")
        self.tag_object = self.git("rev-parse", "refs/tags/" + TAG)
        self.expected = standard_artefacts(VERSION)
        self.assets = {PLUGIN: tiny_zip(), "sbom-spdx.zip": tiny_zip("sbom.json", b"{}")}
        rows = []
        for name, path, how in self.expected:
            data = self.assets.get(name, b"synthetic build output")
            row = {"name": name, "build_path": path, "bytes": len(data), "sha256": digest(data)}
            if how:
                row.update(normalise=how, sha256_normalised=digest(data))
            rows.append(row)
        self.manifest = {
            "schema": "frontier-release-manifest/1.0", "version": VERSION, "date": "2026-11-25",
            "provenance": "Local generation; no CI run claimed.", "artefacts": rows, "not_reproduced": [],
            "build_evidence": {
                "profile": "local-tag-manual-publication/1.0", "repository": REPOSITORY,
                "source_commit": self.source, "source_tag": TAG, "tag_object": self.tag_object,
                "control_commit": "a" * 40, "native_attestation": "not-provided", "publication": "not-performed",
            },
        }
        self.release = {"id": 123, "tag_name": TAG, "draft": False, "published_at": "2026-11-25T00:00:00Z",
                        "target_commitish": "main", "assets": []}
        self.refs = [{"ref": "refs/tags/" + TAG, "object": {"type": "tag", "sha": self.tag_object}}]
        self.tag = {"sha": self.tag_object, "tag": TAG, "object": {"type": "commit", "sha": self.source}}
        self.routes = {}
        self.requests = []
        self.refresh()
        self.patcher = patch.object(evidence.subprocess, "Popen", side_effect=self.fake_popen)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def git(self, *args):
        # Only known non-secret process settings enter the synthetic Git fixture.
        env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "TEMP", "TMP", "PYTHONUTF8") if key in os.environ}
        env.update(GIT_AUTHOR_DATE="2026-01-01T00:00:00+00:00", GIT_COMMITTER_DATE="2026-01-01T00:00:00+00:00",
                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
        return subprocess.run(["git", "--no-pager", "-C", str(self.root), *args], check=True, capture_output=True,
                              text=True, encoding="utf-8", env=env).stdout.strip()

    @property
    def version_cache(self):
        return self.root / "build/release-evidence" / VERSION

    @property
    def cache(self):
        return self.version_cache / self.source

    def refresh(self):
        self.assets["release-manifest.json"] = encode(self.manifest)
        self.assets["SHA256SUMS.txt"] = "".join(
            f"{digest(self.assets[name])}  {name}\n" for name in NAMES[:3]).encode()
        self.release["assets"] = [
            {"id": 100 + i, "name": name, "size": len(self.assets[name]), "state": "uploaded",
             "browser_download_url": "https://untrusted.invalid/never-use-this"} for i, name in enumerate(NAMES)
        ]
        self.routes = {
            BASE: {"full_name": REPOSITORY},
            BASE + "/releases?per_page=100&page=1": [self.release],
            BASE + "/git/matching-refs/tags/" + TAG: self.refs,
            BASE + "/git/tags/" + self.tag_object: self.tag,
            **{BASE + f"/releases/assets/{100 + i}": self.assets[name] for i, name in enumerate(NAMES)},
        }

    def fake_popen(self, args, **kwargs):
        if args[0] != "gh":
            return REAL_POPEN(args, **kwargs)
        self.requests.append((list(args), kwargs))
        self.assertIsInstance(args, list)
        self.assertFalse(kwargs.get("shell", False))
        self.assertEqual(kwargs["stderr"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(args[:7], ["gh", "api", "--hostname", "github.com", "--method", "GET", args[6]])
        endpoint = args[6]
        self.assertIn(endpoint, self.routes, f"Unexpected GitHub request: {args}")
        if "/releases/assets/" in endpoint:
            self.assertEqual(args[7:], ["--header", "Accept: application/octet-stream"])
        else:
            self.assertEqual(args[7:], [])
        value = self.routes[endpoint]
        if isinstance(value, BaseException):
            raise value
        if isinstance(value, tuple):
            return FakeProcess(*value)
        return FakeProcess(value if isinstance(value, bytes) else encode(value))

    def resolve(self, online=True, version=VERSION):
        return evidence.resolve(self.root, version, self.expected, online=online)

    def assert_rejected(self, online=True):
        before = {p.relative_to(self.version_cache): p.read_bytes()
                  for p in self.version_cache.rglob("*") if p.is_file()} if self.version_cache.exists() else None
        with self.assertRaises(evidence.EvidenceError):
            self.resolve(online)
        after = {p.relative_to(self.version_cache): p.read_bytes()
                 for p in self.version_cache.rglob("*") if p.is_file()} if self.version_cache.exists() else None
        self.assertEqual(after, before, "Failure must not change or partly populate the cache")

    def test_exact_published_version_is_validated_and_cached(self):
        result = self.resolve()
        self.assertEqual(result, {"status": "published", "version": VERSION, "source_commit": self.source,
                                  "manifest": self.manifest, "message": f"Published evidence validated for {TAG}"})
        self.assertEqual({p.name for p in self.cache.iterdir()}, {*NAMES, "evidence.json"})
        record = json.loads((self.cache / "evidence.json").read_bytes())
        self.assertEqual(record["schema"], "frontier-release-evidence-cache/1.0")
        self.assertEqual(record["files"], {n: digest(self.assets[n]) for n in NAMES})
        self.assertFalse(any("releases/latest" in str(request) for request in self.requests))
        for name in NAMES:
            self.assertEqual((self.cache / name).read_bytes(), self.assets[name])
        self.assertEqual(self.resolve(), result)  # Identical validated cache is reusable.
        self.assertEqual(sum(r[0][6] == BASE for r in self.requests), 2)  # Online is always fresh.

    def test_offline_absence_is_not_a_published_or_development_pass(self):
        result = self.resolve(False)
        self.assertEqual(result["status"], "not-performed")
        self.assertIsNone(result["manifest"])
        self.assertIsNone(result["source_commit"])
        self.assertIn("not performed", result["message"].lower())
        self.assertEqual(self.requests, [])

    def test_workflow_profile_preserves_generation_facts(self):
        self.manifest["build_evidence"] = {
            "profile": "github-owner-dispatch-publication/1.0", "repository": REPOSITORY,
            "source_commit": self.source, "control_commit": self.source, "intended_tag": TAG,
            "run_id": "123", "run_attempt": "1", "run_url": f"https://github.com/{REPOSITORY}/actions/runs/123",
            "manual_checks": "confirmed by dispatching maintainer", "native_attestation": "not-provided",
        }
        self.refresh()
        self.assertEqual(self.resolve()["manifest"], self.manifest)

    def test_healthy_paginated_absence_is_development_never_cached(self):
        self.routes[BASE + "/releases?per_page=100&page=1"] = [
            {"tag_name": "v0.0." + str(i), "draft": False} for i in range(100)]
        self.routes[BASE + "/releases?per_page=100&page=2"] = []
        self.routes[BASE + "/git/matching-refs/tags/" + TAG] = [
            {"ref": "refs/tags/" + TAG + "1", "object": {"type": "tag", "sha": "b" * 40}}]
        result = self.resolve()
        self.assertEqual(result["status"], "development")
        self.assertIsNone(result["manifest"])
        self.assertIsNone(result["source_commit"])
        self.assertFalse(self.version_cache.exists())

    def test_remote_errors_fail_closed(self):
        for endpoint in (BASE, BASE + "/releases?per_page=100&page=1",
                         BASE + "/git/matching-refs/tags/" + TAG, BASE + "/git/tags/" + self.tag_object,
                         BASE + "/releases/assets/100"):
            for value in ((b"HTTP 404", 1), (b"HTTP 401", 1), (b"HTTP 403", 1),
                          subprocess.TimeoutExpired("gh", 30), OSError("network unavailable"), b"{bad json"):
                with self.subTest(endpoint=endpoint, failure=str(value)):
                    self.refresh()
                    self.routes[endpoint] = value
                    self.assert_rejected()

    def test_wrong_repository_and_malformed_metadata(self):
        for value in ({"full_name": "other/repo"}, [], None, b'{"full_name":"x","full_name":"y"}', b"x" * (1024 * 1024 + 1)):
            with self.subTest(value=str(value)[:80]):
                self.refresh()
                self.routes[BASE] = value
                self.assert_rejected()

    def test_incomplete_or_duplicate_release_enumeration_is_error(self):
        for value in ({}, [None], [self.release, self.release]):
            with self.subTest(value=value):
                self.refresh()
                self.routes[BASE + "/releases?per_page=100&page=1"] = value
                self.assert_rejected()
        for page in range(1, 21):
            self.routes[BASE + f"/releases?per_page=100&page={page}"] = [{"tag_name": "other", "draft": False}] * 100
        self.assert_rejected()

    def test_draft_unpublished_and_tag_without_release_are_errors(self):
        for change in ({"draft": True}, {"published_at": None}, {"draft": "false"}, {"id": True}):
            with self.subTest(change=change):
                self.refresh()
                self.release.update(change)
                self.assert_rejected()
                self.release.update(draft=False, published_at="2026-11-25T00:00:00Z", id=123)
        self.refresh()
        self.routes[BASE + "/releases?per_page=100&page=1"] = []
        self.assert_rejected()

    def test_annotated_exact_tag_must_resolve_to_commit(self):
        for change in ({"tag": "v9.9.9"}, {"sha": "b" * 40}, {"object": {"type": "tag", "sha": self.source}},
                       {"object": {"type": "commit", "sha": "main"}}):
            with self.subTest(change=change):
                original = copy.deepcopy(self.tag)
                self.tag.update(change)
                self.refresh()
                self.assert_rejected()
                self.tag = original
        self.refresh()
        self.routes[BASE + "/git/matching-refs/tags/" + TAG] = []
        self.assert_rejected()
        self.routes[BASE + "/git/matching-refs/tags/" + TAG] = [
            {"ref": "refs/tags/" + TAG, "object": {"type": "commit", "sha": self.source}}]
        self.assert_rejected()

    def test_missing_duplicate_unexpected_and_unsafe_assets(self):
        for mode in ("missing", "duplicate", "extra", "escape", "bad-id", "bad-state"):
            with self.subTest(mode=mode):
                self.refresh()
                rows = self.release["assets"]
                if mode == "missing":
                    rows.pop()
                elif mode == "duplicate":
                    rows.append(rows[0])
                elif mode == "extra":
                    rows.append({"name": "unexpected.txt", "id": 200, "size": 1})
                else:
                    rows[0].update({"escape": {"name": "../" + PLUGIN}, "bad-id": {"id": "../evil"},
                                    "bad-state": {"state": "new"}}[mode])
                self.assert_rejected()

    def test_advertised_sizes_and_total_limit(self):
        for index, size in ((0, 32 * 1024 * 1024 + 1), (1, 1024 * 1024 + 1),
                            (3, 16 * 1024 + 1), (0, -1), (0, True)):
            with self.subTest(index=index, size=size):
                self.refresh()
                self.release["assets"][index]["size"] = size
                self.assert_rejected()
        self.refresh()
        for row in self.release["assets"]:
            row["size"] = 32 * 1024 * 1024 if row["name"].endswith(".zip") else 1
        self.assert_rejected()

    def test_actual_size_is_bounded_and_matches_advertisement(self):
        for i, data in ((0, b"x" * (32 * 1024 * 1024 + 1)), (1, b"x" * (1024 * 1024 + 1)),
                        (3, b"x" * (16 * 1024 + 1)), (0, self.assets[PLUGIN] + b"extra")):
            with self.subTest(index=i, size=len(data)):
                self.refresh()
                self.routes[BASE + f"/releases/assets/{100 + i}"] = data
                self.assert_rejected()

    def test_checksums_require_exact_unique_lowercase_basename_rows(self):
        valid = self.assets["SHA256SUMS.txt"]
        rows = valid.decode().splitlines()
        invalid = [b"", valid.upper(), valid + rows[0].encode() + b"\n",
                   ("\n".join(rows[:2]) + "\n").encode(), b"g" * 64 + b"  " + PLUGIN.encode() + b"\n"]
        for name in ("../" + PLUGIN, "/" + PLUGIN, "nested/" + PLUGIN, "C:\\" + PLUGIN, ".\\" + PLUGIN):
            invalid.append(valid.replace(PLUGIN.encode(), name.encode()))
        invalid.append(valid.replace(rows[0][:64].encode(), b"0" * 64))
        for data in invalid:
            with self.subTest(data=data[:100]):
                self.refresh()
                self.assets["SHA256SUMS.txt"] = data
                self.release["assets"][3]["size"] = len(data)
                self.routes[BASE + "/releases/assets/103"] = data
                self.assert_rejected()

    def test_tampered_payloads_fail_even_with_valid_zip(self):
        for index in range(3):
            with self.subTest(index=index):
                self.refresh()
                data = self.assets[NAMES[index]]
                self.routes[BASE + f"/releases/assets/{100 + index}"] = data[:-1] + bytes([data[-1] ^ 1])
                self.assert_rejected()

    def test_manifest_shape_paths_hashes_and_normalisation(self):
        original = copy.deepcopy(self.manifest)
        mutations = [
            lambda m: m.update(schema="unknown"), lambda m: m.update(version="1.11.0"),
            lambda m: m.update(not_reproduced=["something"]), lambda m: m.pop("build_evidence"),
            lambda m: m["artefacts"].pop(), lambda m: m["artefacts"].append(m["artefacts"][0]),
            lambda m: m["artefacts"][0].update(build_path="../outside"),
            lambda m: m["artefacts"][0].update(name="/outside"),
            lambda m: m["artefacts"][0].update(sha256="A" * 64),
            lambda m: m["artefacts"][0].update(sha256="0" * 64),
            lambda m: m["artefacts"][0].update(bytes=True),
            lambda m: m["artefacts"][0].update(bytes=1),
            lambda m: m["artefacts"][0].update(normalise="generated-date", sha256_normalised="a" * 64),
            lambda m: m["artefacts"][1].update(normalise="arbitrary"),
            lambda m: m["artefacts"][1].pop("sha256_normalised"),
            lambda m: m["artefacts"][2].update(build_path=m["artefacts"][0]["build_path"]),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                self.manifest = copy.deepcopy(original)
                mutation(self.manifest)
                self.refresh()
                self.assert_rejected()

    def test_source_profiles_are_bound_not_relabelled(self):
        original = copy.deepcopy(self.manifest["build_evidence"])
        for field, value in (("profile", "unknown"), ("repository", "other/repo"), ("source_commit", "a" * 40),
                             ("source_tag", "v1.11.0"), ("tag_object", "b" * 40), ("control_commit", "main"),
                             ("publication", "published"), ("native_attestation", "verified")):
            with self.subTest(field=field):
                self.manifest["build_evidence"] = dict(original, **{field: value})
                self.refresh()
                self.assert_rejected()
        self.manifest["build_evidence"] = {k: v for k, v in original.items() if k != "profile"}
        self.refresh()
        self.assert_rejected()

    def test_invalid_and_unsafe_zip_contents(self):
        plugin = self.assets[PLUGIN]
        for name in (PLUGIN, "sbom-spdx.zip"):
            for data in (b"not a zip", tiny_zip("../escape"), tiny_zip("/absolute"), tiny_zip("link", symlink=True)):
                with self.subTest(name=name, data=data[:30]):
                    self.assets[PLUGIN] = plugin
                    self.manifest["artefacts"][0].update(bytes=len(plugin), sha256=digest(plugin))
                    self.assets[name] = data
                    if name == PLUGIN:
                        self.manifest["artefacts"][0].update(bytes=len(data), sha256=digest(data))
                    self.refresh()
                    self.assert_rejected()

    def test_corrupt_zip_crc_is_checked(self):
        data = bytearray(self.assets[PLUGIN])
        offset = data.index(b"offline fixture")
        data[offset] ^= 1
        self.assets[PLUGIN] = bytes(data)
        self.manifest["artefacts"][0].update(sha256=digest(data))
        self.refresh()
        self.assert_rejected()

    def test_deflate_failure_is_an_evidence_error_not_a_raw_exception(self):
        data = bytearray(tiny_zip(compression=zipfile.ZIP_DEFLATED))
        offset = 30 + len("synthetic.txt")
        data[offset:offset + 2] = b"\xff\xff"
        self.assets[PLUGIN] = bytes(data)
        self.manifest["artefacts"][0].update(bytes=len(data), sha256=digest(data))
        self.refresh()
        try:
            self.assert_rejected()
        except evidence.EvidenceError:
            raise
        except Exception as exc:
            self.fail(f"Invalid compressed bytes must raise EvidenceError, not {type(exc).__name__}: {exc}")

    def test_malformed_nonexact_tag_response_cannot_prove_development(self):
        self.routes[BASE + "/releases?per_page=100&page=1"] = []
        for ref in ({"ref": "refs/tags/" + TAG + "1", "object": {}},
                    {"ref": "refs/heads/main", "object": {"type": "commit", "sha": self.source}},
                    {"ref": "refs/tags/" + TAG + "1", "object": {"type": "tag", "sha": "main"}}):
            with self.subTest(ref=ref):
                self.routes[BASE + "/git/matching-refs/tags/" + TAG] = [ref]
                self.assert_rejected()

    def test_workflow_evidence_rejects_mismatched_intent_and_run_metadata(self):
        source = {
            "profile": "github-owner-dispatch-publication/1.0", "repository": REPOSITORY,
            "source_commit": self.source, "control_commit": self.source, "intended_tag": TAG,
            "run_id": "123", "run_attempt": "1", "run_url": f"https://github.com/{REPOSITORY}/actions/runs/123",
            "manual_checks": "confirmed by dispatching maintainer", "native_attestation": "not-provided",
        }
        for key, value in (("intended_tag", "v9.9.9"), ("control_commit", "b" * 40), ("run_id", "latest"),
                           ("run_attempt", 1), ("run_url", "https://untrusted.invalid/123"), ("manual_checks", False)):
            with self.subTest(key=key):
                self.manifest["build_evidence"] = dict(source, **{key: value})
                self.refresh()
                self.assert_rejected()

    def test_published_lookup_does_not_substitute_another_version(self):
        other = dict(self.release, tag_name="v9.9.9")
        self.routes[BASE + "/releases?per_page=100&page=1"] = [other, self.release]
        self.assertEqual(self.resolve()["version"], VERSION)

    def test_duplicate_zip_members_are_rejected(self):
        import warnings
        stream = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(stream, "w") as archive:
                archive.writestr("duplicate.txt", "first")
                archive.writestr("duplicate.txt", "second")
        self.assets["sbom-spdx.zip"] = stream.getvalue()
        self.refresh()
        self.assert_rejected()

    def test_offline_cache_hit_revalidates_without_gh_even_in_ci(self):
        published = self.resolve()
        self.requests.clear()
        # The complete selector is also run with inherited CI=true; no CI-only networking.
        self.assertEqual(self.resolve(False), published)
        self.assertEqual(self.requests, [])

    def test_tool_only_descendant_head_is_not_the_immutable_release_source(self):
        self.git("-c", "user.name=Offline Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--quiet", "--allow-empty", "-m", "Synthetic tooling descendant")
        self.assertNotEqual(self.git("rev-parse", "HEAD"), self.source)
        published = self.resolve()
        self.assertEqual(published["source_commit"], self.source)
        self.requests.clear()
        self.assertEqual(self.resolve(False), published)
        self.assertEqual(self.requests, [])

    def test_offline_cache_tampering_is_error(self):
        self.resolve()
        self.requests.clear()
        for name in (*NAMES, "evidence.json"):
            path = self.cache / name
            original = path.read_bytes()
            path.write_bytes(b"tampered")
            with self.subTest(name=name):
                self.assert_rejected(False)
            path.write_bytes(original)
        self.assertEqual(self.requests, [])

    def test_offline_cache_revalidates_payload_beyond_cache_digests(self):
        self.resolve()
        path = self.cache / PLUGIN
        path.write_bytes(tiny_zip(data=b"replacement zip"))
        record_path = self.cache / "evidence.json"
        record = json.loads(record_path.read_bytes())
        record["files"][PLUGIN] = digest(path.read_bytes())
        record_path.write_bytes(encode(record))
        self.assert_rejected(False)

    def test_offline_manifest_is_revalidated_after_consistent_file_digest_update(self):
        self.resolve()
        self.manifest["version"] = "9.9.9"
        self.refresh()
        for name, data in self.assets.items():
            (self.cache / name).write_bytes(data)
        record_path = self.cache / "evidence.json"
        record = json.loads(record_path.read_bytes())
        record["files"] = {name: digest(data) for name, data in self.assets.items()}
        record_path.write_bytes(encode(record))
        self.assert_rejected(False)

    def test_offline_wrong_or_missing_local_tag_is_error(self):
        self.resolve()
        self.git("tag", "-d", TAG)
        self.assert_rejected(False)
        self.git("tag", TAG)
        self.assert_rejected(False)  # Lightweight tag.
        self.git("tag", "-d", TAG)
        self.git("-c", "user.name=Offline Fixture", "-c", "user.email=fixture@example.invalid",
                 "tag", "-a", TAG, "-m", "Different tag object")
        self.assert_rejected(False)
        self.assertEqual(len([r for r in self.requests if r[0][6] == BASE]), 1)

    def test_stale_wrong_source_partial_or_extra_cache_is_not_absence(self):
        self.version_cache.mkdir(parents=True)
        self.assert_rejected(False)  # A partial directory is not a cache miss.
        (self.version_cache / ("b" * 40)).mkdir()
        self.assert_rejected(False)

    def test_cache_identity_fields_are_revalidated(self):
        self.resolve()
        path = self.cache / "evidence.json"
        original = json.loads(path.read_bytes())
        for field, value in (("schema", "unknown"), ("repository", "other/repo"), ("version", "9.9.9"),
                             ("source_commit", "b" * 40), ("tag_object", "b" * 40), ("release_id", True),
                             ("files", {})):
            with self.subTest(field=field):
                path.write_bytes(encode(dict(original, **{field: value})))
                self.assert_rejected(False)

    def test_cache_symlink_is_rejected(self):
        self.resolve()
        path = self.cache / PLUGIN
        path.unlink()
        target = self.root / "not-the-cache.zip"
        target.write_bytes(self.assets[PLUGIN])
        try:
            path.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"Host cannot create test symlinks: {exc}")
        self.assert_rejected(False)

    def test_failure_does_not_replace_previously_valid_cache(self):
        self.resolve()
        self.routes[BASE + "/releases/assets/100"] = b"bad"
        self.assert_rejected()

    def test_invalid_existing_cache_is_never_replaced(self):
        self.resolve()
        (self.cache / "evidence.json").write_bytes(b"invalid")
        self.assert_rejected()

    def test_extra_cache_file_is_rejected(self):
        self.resolve()
        (self.cache / "extra.txt").write_bytes(b"unexpected")
        self.assert_rejected(False)

    def test_invalid_version_and_expected_paths_are_rejected(self):
        for version in ("../outside", "01.10.0", "v1.10.0", "1.10.0\n"):
            with self.subTest(version=version), self.assertRaises(evidence.EvidenceError):
                self.resolve(version=version)
        self.expected[0] = (PLUGIN, "../outside", None)
        self.assert_rejected(False)


if __name__ == "__main__":
    unittest.main()
