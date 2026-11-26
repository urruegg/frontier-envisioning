# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Behavioural producer contract tests; upstream validator is passive text only."""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tests.unit._util import ROOT

F = ROOT / "plugin/skills/frontier-agent-factory"
sys.path.insert(0, str(F / "scripts"))
c = importlib.import_module("factory_common")
m = importlib.import_module("factory_contract")
MIB = 1024 ** 2
AT = "2026-11-25T12:00:00Z"


class Behaviour(unittest.TestCase):
    def works(self, function, *args, **kwargs):
        try:
            return function(*args, **kwargs)
        except c.FactoryError as error:
            self.fail(f"required valid behaviour refused: {error}")


class FactoryCommon(Behaviour):
    def test_strict_json_and_real_manifest_boundary(self):
        self.assertEqual(self.works(c.decode, b"{}" + b" " * (MIB - 2)), {})
        for raw in (b"{}" + b" " * (MIB - 1), b'{"a":1,"a":2}',
                    b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
                    b'{"x":1e9999}', b'"\\ud800"', b"\xff", b"{} {}",
                    b"[" * 1500, b"[" * 300 + b"0" + b"]" * 300):
            with self.subTest(size=len(raw)), self.assertRaises(c.FactoryError) as raised:
                c.decode(raw)
            self.assertRegex(str(raised.exception), r"^FACTORY_[A-Z_]+$")
        self.assertEqual(self.works(c.encoded, {"z": "ü", "a": [1]}),
                         b'{\n  "a": [\n    1\n  ],\n  "z": "\xc3\xbc"\n}\n')
        for value in (float("nan"), float("inf"), "\ud800", {1: "not a JSON key"}):
            with self.subTest(kind=type(value)), self.assertRaises(c.FactoryError):
                c.encoded(value)

    def test_dates_and_nested_evidence_are_data_not_defaults(self):
        self.works(c.timestamp, AT)
        self.works(c.timestamp, "2024-02-29t23:59:59.2+01:30")
        for value in ("2026-02-29T12:00:00Z", "2026-01-01T24:00:00Z",
                      "2026-01-01T00:00:00+24:00", "2026-01-01", AT + "x", None):
            with self.subTest(value=value), self.assertRaises(c.FactoryError):
                c.timestamp(value)
        self.works(c.approval, {"by": "Synthetic reviewer", "at": AT, "reference": "synthetic-only"})
        for value in ({}, {"by": " ", "at": AT, "reference": "x"},
                      {"by": "x", "at": AT, "reference": "x", "authenticated": True}):
            with self.subTest(value=value), self.assertRaises(c.FactoryError):
                c.approval(value)
        self.works(c.identity, "caldova-1")
        self.works(c.text, "Caldova")
        for function, value in ((c.identity, "Caldova"), (c.identity, "a" * 81),
                                (c.text, " "), (c.text, "a" * 4001)):
            with self.assertRaises(c.FactoryError):
                function(value)

    def test_portable_paths_preserve_raw_spelling_and_refuse_aliases(self):
        self.assertEqual(self.works(c.parts, r"docs\intake\a.md"), ("docs", "intake", "a.md"))
        self.assertEqual(self.works(c.portable, r"docs\intake\a.md"), "docs/intake/a.md")
        self.assertEqual(self.works(c.path_key, "DOCS/a.md"), "docs/a.md")
        for value in ("../a", "/a", "//host/a", "C:/a", "a:b", "a//b",
                      "a/./b", r"\\host\a", r"a\..\b", "a.", "a ", "CON.txt",
                      "a/\x00b", "a/\x7fb", "a/\ud800"):
            with self.subTest(value=repr(value)), self.assertRaises(c.FactoryError):
                c.parts(value)
        spellings = {}
        self.works(c.claim_path, spellings, r"docs\a.md")
        self.works(c.claim_path, spellings, r"docs\a.md", repeat=True)
        for value, repeat in ((r"docs\a.md", False), ("docs/a.md", True), ("DOCS/a.md", True)):
            with self.subTest(value=value), self.assertRaises(c.FactoryError):
                c.claim_path(spellings, value, repeat=repeat)
        self.assertEqual(len(spellings), 1)

    def test_safe_regular_reads_and_actual_byte_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            p = root / "a.md"
            p.write_bytes(b"A" * (16 * MIB))
            self.assertEqual(len(self.works(c.read, root, "a.md", 16 * MIB)), 16 * MIB)
            with p.open("ab") as stream:
                stream.write(b"B")
            for path, limit in (("a.md", 16 * MIB), ("missing.md", 16 * MIB), ("../a.md", MIB)):
                with self.subTest(path=path), self.assertRaises(c.FactoryError):
                    c.read(root, path, limit)
            self.assertEqual(self.works(c.plain_path, root / "new.zip", missing=True), root / "new.zip")
            with self.assertRaises(c.FactoryError):
                c.plain_path(root / "absent" / "new.zip", missing=True)
            with self.assertRaises(c.FactoryError):
                c.plain_path("bad\x00path", missing=True)

    def test_file_claims_reject_ancestor_conflicts_in_both_orders_not_string_prefixes(self):
        ancestor = r"docs\intake\records\caldova-intake\artifacts\specs.md"
        descendant = "docs/intake/records/caldova-intake/artifacts/SPECS.md/design.md"
        for first, second in ((ancestor, descendant), (descendant, ancestor)):
            spellings = {}
            self.works(c.claim_path, spellings, first)
            before = dict(spellings)
            with self.subTest(first=first), self.assertRaisesRegex(c.FactoryError, "FACTORY_PATH_COLLISION"):
                c.claim_path(spellings, second, repeat=True)
            self.assertEqual(spellings, before, "a refused FILE claim must not mutate existing claims")
        for paths in (("specs.md", "SPECS.md2/design.md"), ("SPECS.md2/design.md", "specs.md")):
            spellings = {}
            for path in paths:
                self.works(c.claim_path, spellings, path)
            self.assertEqual(len(spellings), 2)

    @unittest.skipUnless(os.name == "nt", "Windows junction behaviour")
    def test_junction_ancestry_is_rejected_before_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, link = root / "real", root / "junction"
            target.mkdir()
            (target / "a.txt").write_bytes(b"synthetic")
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                    capture_output=True, check=False)
            self.assertEqual(result.returncode, 0, "test requires an ordinary local junction")
            try:
                with self.assertRaises(c.FactoryError):
                    c.read(link, "a.txt", MIB)
                with self.assertRaises(c.FactoryError):
                    c.plain_path(link / "new.zip", missing=True)
            finally:
                link.rmdir()

    def test_schema_subset_checks_real_nested_rules_and_rejects_unknown_vocabulary(self):
        rule = {"type": "object", "additionalProperties": False, "required": ["review"],
                "$defs": {"approval": {"type": "string", "pattern": "review", "minLength": 8}},
                "properties": {"review": {"oneOf": [{"$ref": "#/$defs/approval"}, {"type": "null"}]}}}
        self.assertTrue(self.works(c.conforms, rule, {"review": "a review"}))
        for value in ({"review": 3}, {"review": "no"}, {}, {"review": None, "extra": True}):
            self.assertFalse(self.works(c.conforms, rule, value))
        self.assertFalse(self.works(c.conforms, {"type": "integer"}, True))
        for rule in ({"type": "string", "minProperties": 2},
                     {"$ref": "https://invalid.example/schema"},
                     {"properties": {"unused": {"minProperties": 2}}},
                     {"type": "string", "format": "hostname"}):
            with self.subTest(rule=rule), self.assertRaises(c.FactoryError):
                c.conforms(rule, "Caldova")


class FactoryFixture(Behaviour):
    def test_tiny_fixture_is_synthetic_sha_omitted_and_saved_with_actual_archive_hash(self):
        from tests import factory_fixture as fixture
        with tempfile.TemporaryDirectory() as directory:
            try:
                f = fixture.prepare(Path(directory))
            except ValueError as error:
                self.fail(f"required synthetic fixture unavailable: {error}")
            self.assertEqual(set(f), {"request", "request_file", "template", "source",
                                      "baseline", "out", "originals"})
            request = f["request"]
            self.assertEqual(request["evidence_kind"], "synthetic-compatibility")
            self.assertEqual(request["intake"]["review"]["status"], "needs-clarification")
            self.assertEqual(request["financial"], {"requested": False, "as_of": None,
                                                     "claim": "review", "packets": []})
            for row in request["intake"]["artifacts"]:
                if row["status"] == "provided":
                    self.assertNotIn("sha256", row["source"])
                    self.assertNotIn("sha256", row["baseline"])
            self.assertEqual(len([r for r in request["intake"]["artifacts"]
                                  if r["status"] == "provided"]), 3)
            self.assertEqual(fixture.encode(request), f["request_file"].read_bytes())
            f["template"].write_bytes(fixture.zip_bytes({"synthetic.txt": b"changed"}))
            fixture.save(f)
            saved = json.loads(f["request_file"].read_bytes())
            self.assertEqual(saved["template"]["acquisition"]["archive_sha256"],
                             hashlib.sha256(f["template"].read_bytes()).hexdigest())


class ContractCase(Behaviour):
    def setUp(self):
        from tests.factory_fixture import prepare
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f = prepare(Path(self.temp.name), accepted=True)
        self.schema = c.decode((F / "references/intake.schema.json").read_bytes())


class FactoryFileClaims(ContractCase):
    def test_file_ancestors_refused_by_prevalidation_materialisation_and_intake_before_reads(self):
        good, baseline, originals = m.materialize(self.f["request"]["intake"],
                                                 self.f["baseline"], self.f["source"], c.read)
        prefix = "docs/intake/records/caldova-intake/artifacts/"
        for field in ("source", "baseline"):
            for reverse in (False, True):
                request = copy.deepcopy(self.f["request"])
                data = copy.deepcopy(good)
                baselines, sources = dict(baseline), dict(originals)
                names = ["specs.md", r"SPECS.md\design.md"]
                if field == "baseline":
                    names = [prefix + name for name in names]
                if reverse:
                    names.reverse()
                files = baselines if field == "baseline" else sources
                for row, name in zip(data["artifacts"][:2], names):
                    raw = files.pop(c.portable(row[field]["path"]))
                    row[field]["path"] = name
                    files[c.portable(name)] = raw
                for row, name in zip(request["intake"]["artifacts"][:2], names):
                    row[field]["path"] = name
                for boundary in ("prevalidate", "materialize", "validate"):
                    with self.subTest(field=field, reverse=reverse, boundary=boundary):
                        with self.assertRaisesRegex(c.FactoryError, "FACTORY_PATH_COLLISION"):
                            if boundary == "prevalidate":
                                m.prevalidate_request(request, self.schema)
                            elif boundary == "materialize":
                                m.materialize(request["intake"], self.f["baseline"], self.f["source"],
                                              lambda *args: self.fail("FILE conflict reached artifact read callback"))
                            else:
                                m.validate_intake(data, self.schema, baselines, sources)


class FactoryRequest(ContractCase):
    def test_receiver_schema_is_pinned_and_request_copy_removes_only_computed_hashes(self):
        for path, size, expected in (
            (F / "references/intake.schema.json", 8381,
             "04d8e85767c03e7cc101b85e67bcd9377fa5f069842c0e01ce92f9acf12c923f"),
            (ROOT / "tests/fixtures/factory/intake-reference.py.txt", 15736,
             "4592262543f4bc42ce1c12c47f25e2a5be88b91b669f4513b3f019ebc1553370"),
        ):
            raw = path.read_bytes()
            self.assertEqual((len(raw), c.digest(raw)), (size, expected))
        before = copy.deepcopy(self.schema)
        shape = self.works(m.request_shape, self.schema)
        self.assertTrue(c.conforms(shape, self.f["request"]))
        self.assertEqual(self.schema, before)
        receiver = copy.deepcopy(self.f["request"]["intake"])
        self.assertFalse(c.conforms(self.schema, receiver))
        for row in receiver["artifacts"]:
            if row["status"] == "provided":
                row["source"]["sha256"] = row["baseline"]["sha256"] = "a" * 64
        self.assertTrue(c.conforms(self.schema, receiver))
        poisoned = copy.deepcopy(self.f["request"])
        poisoned["intake"] = receiver
        self.assertFalse(c.conforms(shape, poisoned))

    def test_prevalidation_rejects_complete_nested_malformed_data_before_io(self):
        request = self.f["request"]
        self.works(m.prevalidate_request, request, self.schema)
        mutations = [
            (("intake", "selected_solutions", 0, "owners"), []),
            (("intake", "selected_solutions", 0, "scope"), " "),
            (("intake", "artifacts", 0, "source"), {"path": "prd.md"}),
            (("intake", "artifacts", 0, "source", "sha256"), "a" * 64),
            (("intake", "acquisition", "verified_at"), "2026-02-29T00:00:00Z"),
            (("template", "discovery", "releases"), [{}]),
            (("blueprint", "source_path"), 4),
            (("id_map", "solutions"), []),
            (("selection_evidence",), [{}]),
            (("sharing_review", "metadata"), None),
            (("sharing_review", "artifacts"), []),
            (("financial", "requested"), 1),
            (("financial", "packets"), [{"kind": "baseline"}]),
            (("history",), ["prior"] * 128),
            (("unknown",), True),
        ]
        for location, value in mutations:
            changed = copy.deepcopy(request)
            target = changed
            for key in location[:-1]:
                target = target[key]
            target[location[-1]] = value
            with self.subTest(location=location), self.assertRaises(c.FactoryError):
                m.prevalidate_request(changed, self.schema)
        malformed = copy.deepcopy(request["intake"])
        malformed["selected_solutions"][0]["owners"] = []
        with self.assertRaises(c.FactoryError):
            m.materialize(malformed, self.f["baseline"], self.f["source"],
                          lambda *args: self.fail("malformed input reached file IO"))

    def test_fixed_template_profile_has_only_reviewed_fingerprints_and_required_paths(self):
        # A missing fixed profile is a feature assertion, not an import failure.
        path = F / "references/template-profile.json"
        self.assertTrue(path.is_file(), "fixed reviewed template profile is required")
        self.assertEqual(c.decode(path.read_bytes()), {
            "schema": "frontier-agent-factory-template-profile/1.0",
            "intake_schema_sha256": c.digest((F / "references/intake.schema.json").read_bytes()),
            "intake_validator_sha256": c.digest((ROOT / "tests/fixtures/factory/intake-reference.py.txt").read_bytes()),
            "required": ["LICENSE", ".agents/skills/LICENSE.superpowers", ".agents/superpowers.lock.json",
                         "docs/intake/intake.schema.json", "tools/intake.py", "AGENTS.md"]})

    def test_producer_ids_are_exact_and_current_sharing_keys_cannot_name_unknown_files(self):
        self.works(m.prevalidate_request, self.f["request"], self.schema)
        for case in ("export-newline", "solution-newline", "extra-sharing", "mutable-schema"):
            request = copy.deepcopy(self.f["request"])
            schema = copy.deepcopy(self.schema)
            if case == "export-newline":
                request["export_id"] += "\n"
            elif case == "solution-newline":
                request["intake"]["selected_solutions"][0]["solution_id"] += "\n"
                for row in request["intake"]["artifacts"]:
                    row["solution_ids"][0] += "\n"
                request["intake"]["requirements"][0]["solution_id"] += "\n"
                request["selection_evidence"][0]["solution_id"] += "\n"
                request["id_map"]["solutions"]["D1"] += "\n"
            elif case == "extra-sharing":
                from tests.factory_fixture import approved
                request["sharing_review"]["artifacts"]["caldova-intake:unknown-file"] = approved()
            else:
                schema["additionalProperties"] = True
            with self.subTest(case=case), self.assertRaises(c.FactoryError):
                m.prevalidate_request(request, schema)

    def test_dependency_gap_refs_are_unique_exact_ids_before_materialisation(self):
        request = copy.deepcopy(self.f["request"])
        request["selection_evidence"][0]["dependency_gaps"] = ["boundary-gap", "risk-2"]
        # W1 validates references as IDs; W3 resolves them against declarations.
        self.works(m.prevalidate_request, request, self.schema)
        shape = m.request_shape(self.schema)
        for gaps in (["not an id"], ["boundary-gap", "boundary-gap"], ["Boundary-gap"],
                     ["-boundary"], ["a" * 81], [None], [True]):
            request["selection_evidence"][0]["dependency_gaps"] = gaps
            with self.subTest(gaps=gaps):
                with self.assertRaises(c.FactoryError):
                    m.prevalidate_request(request, self.schema)
                self.assertFalse(c.conforms(shape, request), "request schema must reject invalid/duplicate gap IDs")
        request["selection_evidence"][0]["dependency_gaps"] = ["boundary-gap\n"]
        with self.assertRaises(c.FactoryError):
            m.prevalidate_request(request, self.schema)

    def test_every_history_id_is_exact_before_materialisation_or_io(self):
        request = copy.deepcopy(self.f["request"])
        request["history"] = ["prior-intake"]
        self.works(m.prevalidate_request, request, self.schema)
        for prior in ("prior\n", "Prior", "not an id", "-prior", "a" * 81, "", None):
            request["history"] = [prior]
            with self.subTest(prior=prior), self.assertRaises(c.FactoryError):
                m.prevalidate_request(request, self.schema)
                self.fail("invalid history ID reached the materialisation/IO boundary")


class FactoryReceipt(ContractCase):
    def receipt(self, receipt=None, export_id="caldova-export", created_at=AT, archive=None):
        return m.source_receipt(self.f["request"]["template"] if receipt is None else receipt,
                                export_id, created_at,
                                self.f["template"].read_bytes() if archive is None else archive)

    def stable(self):
        receipt = copy.deepcopy(self.f["request"]["template"])
        receipt.update(selection="stable-release", bootstrap_approval=None,
                       release={"id": 2, "tag": "v1.0", "commit": receipt["commit"], "published_at": AT})
        receipt["discovery"]["releases"] = [
            {"id": 1, "tag_name": "historical-unresolved", "published_at": "2025-01-01T12:00:00Z",
             "draft": False, "prerelease": False},
            {"id": 2, "tag_name": "v1.0", "published_at": AT, "draft": False, "prerelease": False},
            {"id": 3, "tag_name": None, "published_at": None, "draft": True, "prerelease": False},
            {"id": 4, "tag_name": None, "published_at": None, "draft": False, "prerelease": True},
        ]
        return receipt

    def test_selected_latest_stable_only_needs_resolution_and_ignored_rows_may_be_null(self):
        self.works(self.receipt, self.stable())
        stable = self.stable()
        for field in ("tag", "commit", "published_at", "id"):
            changed = copy.deepcopy(stable)
            changed["release"][field] = {"tag": "old", "commit": "f" * 40,
                                         "published_at": "2025-01-01T12:00:00Z", "id": 1}[field]
            with self.subTest(field=field), self.assertRaises(c.FactoryError):
                self.receipt(changed)
        changed = copy.deepcopy(stable)
        changed["discovery"]["releases"][0]["published_at"] = AT
        with self.assertRaises(c.FactoryError):
            self.receipt(changed)

    def test_bootstrap_requires_healthy_empty_stable_lookup_and_exact_commit_approval(self):
        self.works(self.receipt)
        original = self.f["request"]["template"]
        for location, value in (
            (("bootstrap_approval",), None),
            (("bootstrap_approval", "reference"), "synthetic approval omits commit"),
            (("discovery", "status"), "failed"),
            (("discovery", "complete"), False),
            (("discovery", "export_id"), "another-export"),
            (("acquisition", "status"), "failed"),
            (("acquisition", "at"), "2026-11-25T11:59:59Z"),
            (("acquisition", "archive_sha256"), "0" * 64),
            (("commit",), "A" * 40),
        ):
            changed = copy.deepcopy(original)
            target = changed
            for key in location[:-1]:
                target = target[key]
            target[location[-1]] = value
            with self.subTest(location=location), self.assertRaises(c.FactoryError):
                self.receipt(changed)
        with self.assertRaises(c.FactoryError):
            self.receipt(archive=b"unreviewed different bytes")
        with self.assertRaises(c.FactoryError):
            self.receipt(created_at="2026-11-25T11:59:59Z")
        with self.assertRaises(c.FactoryError):
            self.receipt(export_id="fresh-export-needs-new-discovery")

    def test_unknown_stable_metadata_and_raw_api_payloads_never_fallback(self):
        stable = self.stable()
        self.works(self.receipt, stable)
        for field, value in (("tag_name", None), ("published_at", None),
                             ("published_at", "2026-02-29T12:00:00Z")):
            changed = copy.deepcopy(stable)
            changed["discovery"]["releases"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(c.FactoryError) as raised:
                self.receipt(changed)
            self.assertIn("DISCOVERY", str(raised.exception))
        for extra in ("body", "author", "assets", "commit"):
            changed = copy.deepcopy(stable)
            changed["discovery"]["releases"][0][extra] = "not a minimal five-field row"
            with self.subTest(extra=extra), self.assertRaises(c.FactoryError):
                self.receipt(changed)
        bootstrap = copy.deepcopy(self.f["request"]["template"])
        bootstrap["discovery"]["releases"] = stable["discovery"]["releases"]
        with self.assertRaises(c.FactoryError):
            self.receipt(bootstrap)

    def test_unusable_stable_tags_are_unknown_discovery_not_bootstrap(self):
        receipt = self.stable()
        self.works(self.receipt, receipt)
        for tag in ("not a usable tag", "v1..0", "v1@{0}", "v1.lock", ".hidden/v1",
                    "release/.hidden", "release/v1.", "release/v1.lock/part", "release//v1",
                    "release/../v1", "/v1", "v1/", r"release\v1", "v1[0]", "v1~0",
                    "v1^0", "v1:0", "v1?0", "v1*0", "v1\x00", "v1\x1f", "v1\x7f", "v1\n"):
            changed = copy.deepcopy(receipt)
            changed["discovery"]["releases"][0]["tag_name"] = tag
            with self.subTest(tag=tag), self.assertRaisesRegex(c.FactoryError, "FACTORY_DISCOVERY"):
                self.receipt(changed)

    def test_selected_stable_tag_uses_git_ref_syntax_not_an_ascii_naming_policy(self):
        for tag in ("v1.0+build.1", "版本-1.0", "release!candidate", "release./v1",
                    "refs/heads/main", "-option", "@"):
            receipt = self.stable()
            receipt["discovery"]["releases"][1]["tag_name"] = tag
            receipt["release"]["tag"] = tag
            with self.subTest(tag=tag):
                self.works(self.receipt, receipt)

    def test_commit_is_exact_lower_40_hex_not_regex_end_before_newline(self):
        receipt = self.stable()
        self.works(self.receipt, receipt)
        receipt["commit"] += "\n"
        receipt["release"]["commit"] += "\n"
        with self.assertRaisesRegex(c.FactoryError, "FACTORY_DISCOVERY"):
            self.receipt(receipt)

    def test_submicrosecond_reversed_receipt_chronology_is_rejected(self):
        earlier = "2026-11-25T11:00:00.0000001Z"
        later = "2026-11-25T11:00:00.0000002Z"
        for case in ("observation-after-acquisition", "acquisition-after-creation", "publication-after-observation"):
            receipt = self.stable()
            created = AT
            if case == "observation-after-acquisition":
                receipt["discovery"]["observed_at"] = later
                receipt["acquisition"]["at"] = earlier
                receipt["discovery"]["releases"][1]["published_at"] = earlier
                receipt["release"]["published_at"] = earlier
            elif case == "acquisition-after-creation":
                receipt["discovery"]["observed_at"] = earlier
                receipt["acquisition"]["at"] = later
                receipt["discovery"]["releases"][1]["published_at"] = earlier
                receipt["release"]["published_at"] = earlier
                created = earlier
            else:
                receipt["discovery"]["observed_at"] = earlier
                receipt["discovery"]["releases"][1]["published_at"] = later
                receipt["release"]["published_at"] = later
            with self.subTest(case=case), self.assertRaisesRegex(c.FactoryError, "FACTORY_DISCOVERY"):
                self.receipt(receipt, created_at=created)

    def test_latest_stable_uses_all_fraction_digits_without_false_ties(self):
        for zeroes in (6, 100):
            receipt = self.stable()
            receipt["discovery"]["releases"][0]["published_at"] = "2026-11-25T11:00:00." + "0" * zeroes + "1Z"
            receipt["discovery"]["releases"][1]["published_at"] = "2026-11-25T11:00:00." + "0" * zeroes + "2Z"
            receipt["release"]["published_at"] = receipt["discovery"]["releases"][1]["published_at"]
            with self.subTest(fraction_digits=zeroes + 1):
                self.works(self.receipt, receipt)
                older = copy.deepcopy(receipt)
                older["release"].update(id=1, tag="historical-unresolved",
                                        published_at=receipt["discovery"]["releases"][0]["published_at"])
                with self.assertRaisesRegex(c.FactoryError, "FACTORY_DISCOVERY"):
                    self.receipt(older)

    def test_equivalent_offsets_and_fraction_spellings_compare_as_exact_instants(self):
        receipt = self.stable()
        receipt["discovery"]["releases"][1]["published_at"] = "2026-11-25T11:00:00.000000200Z"
        receipt["release"]["published_at"] = "2026-11-25T12:30:00.0000002+01:30"
        receipt["discovery"]["observed_at"] = "2026-11-25T13:00:00.000000200+02:00"
        receipt["acquisition"]["at"] = "2026-11-25T11:00:00.0000002Z"
        self.works(self.receipt, receipt, created_at="2026-11-25T10:00:00.0000002000-01:00")
        # A second stable release at exactly the same instant is still an ambiguous tie.
        receipt["discovery"]["releases"][0]["published_at"] = receipt["release"]["published_at"]
        with self.assertRaisesRegex(c.FactoryError, "FACTORY_DISCOVERY"):
            self.receipt(receipt)
        bootstrap = copy.deepcopy(self.f["request"]["template"])
        bootstrap["discovery"]["observed_at"] = "2026-11-25T00:00:00.0000002+01:00"
        bootstrap["acquisition"]["at"] = "2026-11-24T23:00:00.000000200Z"
        self.works(self.receipt, bootstrap, created_at="2026-11-24T23:00:00.0000002Z")


class FactoryMaterialize(ContractCase):
    def test_hashes_actual_bytes_detaches_input_and_preserves_windows_spelling(self):
        request = copy.deepcopy(self.f["request"]["intake"])
        for row in request["artifacts"]:
            if row["status"] == "provided":
                # Both roots really contain these ordinary files.
                for field in ("source", "baseline"):
                    root = self.f[field]
                    old = root.joinpath(*c.parts(row[field]["path"]))
                    if field == "source":
                        new = root / "selected" / old.name
                        new.parent.mkdir(exist_ok=True)
                        new.write_bytes(old.read_bytes())
                        row[field]["path"] = "selected\\" + old.name
                    else:
                        row[field]["path"] = row[field]["path"].replace("/", "\\")
        before = copy.deepcopy(request)
        result, baselines, originals = self.works(m.materialize, request, self.f["baseline"],
                                                  self.f["source"], c.read)
        self.assertEqual(request, before)
        self.assertIsNot(result, request)
        for row in result["artifacts"]:
            if row["status"] == "provided":
                self.assertIn("\\", row["source"]["path"])
                self.assertIn("\\", row["baseline"]["path"])
                self.assertEqual(row["source"]["sha256"], c.digest(originals[c.portable(row["source"]["path"])]))
                self.assertEqual(row["baseline"]["sha256"], c.digest(baselines[c.portable(row["baseline"]["path"])]))

    def test_nested_artifact_bytes_with_windows_paths_are_valid_without_flattening(self):
        request = copy.deepcopy(self.f["request"]["intake"])
        data, baselines, originals = m.materialize(request, self.f["baseline"], self.f["source"], c.read)
        paths = {
            "source": r"selected\specs\prd.md",
            "baseline": r"docs\intake\records\caldova-intake\artifacts\specs\prd.md",
        }
        for field, files in (("source", originals), ("baseline", baselines)):
            old_path = data["artifacts"][0][field]["path"]
            raw = files.pop(c.portable(old_path))
            path = self.f[field].joinpath(*c.parts(paths[field]))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            files[c.portable(paths[field])] = path.read_bytes()
            request["artifacts"][0][field]["path"] = paths[field]
            data["artifacts"][0][field]["path"] = paths[field]
        before = copy.deepcopy(request)
        self.works(m.validate_intake, data, self.schema, baselines, originals)
        result, actual_baselines, actual_originals = self.works(
            m.materialize, request, self.f["baseline"], self.f["source"], c.read)
        self.assertEqual(request, before)
        self.assertEqual((result, actual_baselines, actual_originals), (data, baselines, originals))
        self.assertEqual(result["artifacts"][0]["baseline"]["path"], paths["baseline"])
        self.assertEqual(actual_baselines[c.portable(paths["baseline"])], self.f["originals"]["prd.md"])

    def test_collisions_rejected_before_io_but_exact_source_reuse_is_explicit(self):
        intake = self.f["request"]["intake"]
        result = self.works(m.materialize, intake, self.f["baseline"], self.f["source"], c.read)
        self.assertEqual(len(result), 3)
        for change in ("slash", "case", "destination", "format", "prefix",
                       "nested-traversal", "nested-format", "nested-alias"):
            data = copy.deepcopy(intake)
            row = copy.deepcopy(data["artifacts"][0])
            row["id"] = "another-prd"
            row["source"]["path"] = "PRD.md" if change == "case" else "prd.md"
            row["baseline"]["path"] = "docs/intake/records/caldova-intake/artifacts/another.md"
            if change == "slash":
                data["artifacts"][0]["source"]["path"] = r"selected\prd.md"
                row["source"]["path"] = "selected/prd.md"
            elif change == "destination":
                row["baseline"]["path"] = data["artifacts"][0]["baseline"]["path"].upper()
            elif change == "format":
                row["source"]["path"] = "archive.zip"
            elif change == "prefix":
                row["baseline"]["path"] = "docs/intake/records/unselected/artifacts/nested/a.md"
            elif change == "nested-traversal":
                row["baseline"]["path"] = "docs/intake/records/caldova-intake/artifacts/specs/../a.md"
            elif change == "nested-format":
                row["baseline"]["path"] = "docs/intake/records/caldova-intake/artifacts/specs/a.zip"
            elif change == "nested-alias":
                data["artifacts"][0]["baseline"]["path"] = "docs/intake/records/caldova-intake/artifacts/specs/prd.md"
                row["baseline"]["path"] = r"docs\intake\records\caldova-intake\artifacts\SPECS\PRD.md"
            data["artifacts"].append(row)
            with self.subTest(change=change), self.assertRaises(c.FactoryError):
                m.materialize(data, self.f["baseline"], self.f["source"],
                              lambda *args: self.fail("path planning must finish before artifact IO"))
        data = copy.deepcopy(intake)
        row = copy.deepcopy(data["artifacts"][0])
        row["id"] = "another-prd"
        row["baseline"]["path"] = "docs/intake/records/caldova-intake/artifacts/another.md"
        self.f["baseline"].joinpath(*c.parts(row["baseline"]["path"])).write_bytes(self.f["originals"]["prd.md"])
        data["artifacts"].append(row)
        _result, baselines, originals = self.works(m.materialize, data, self.f["baseline"], self.f["source"], c.read)
        self.assertEqual((len(baselines), len(originals)), (4, 3))

    def large_input(self, size):
        data = copy.deepcopy(self.f["request"]["intake"])
        prototype = data["artifacts"][0]
        data["artifacts"] = []
        for index, role in enumerate(("prd", "solution-design", "blueprint", "decisions")):
            row = copy.deepcopy(prototype)
            row.update(id=f"large-{index}", role=role)
            row["source"]["path"] = f"large-{index}.txt"
            row["baseline"]["path"] = f"docs/intake/records/caldova-intake/artifacts/large-{index}.txt"
            data["artifacts"].append(row)
            raw = b"A" * size
            (self.f["source"] / row["source"]["path"]).write_bytes(raw)
            self.f["baseline"].joinpath(*c.parts(row["baseline"]["path"])).write_bytes(raw)
        return data

    def test_real_shared_64mib_exact_then_one_byte_over_and_split_root_failure(self):
        data = self.large_input(8 * MIB)
        result, baselines, originals = self.works(m.materialize, data, self.f["baseline"], self.f["source"], c.read)
        self.assertEqual(sum(map(len, baselines.values())) + sum(map(len, originals.values())), 64 * MIB)
        p = self.f["source"] / data["artifacts"][-1]["source"]["path"]
        with p.open("ab") as stream:
            stream.write(b"B")
        with self.assertRaises(c.FactoryError):
            m.materialize(data, self.f["baseline"], self.f["source"], c.read)
        self.assertNotIn("sha256", data["artifacts"][0]["source"])

    def test_nonempty_and_actual_16mib_per_file_not_just_budget(self):
        data = copy.deepcopy(self.f["request"]["intake"])
        data["artifacts"] = [data["artifacts"][0]]
        for size in (16 * MIB, 16 * MIB + 1, 0):
            raw = b"A" * size
            row = data["artifacts"][0]
            (self.f["source"] / row["source"]["path"]).write_bytes(raw)
            self.f["baseline"].joinpath(*c.parts(row["baseline"]["path"])).write_bytes(raw)
            if size == 16 * MIB:
                _result, baselines, originals = self.works(m.materialize, data, self.f["baseline"], self.f["source"], c.read)
                self.assertEqual(sum(map(len, baselines.values())) + sum(map(len, originals.values())), 32 * MIB)
            else:
                with self.subTest(size=size), self.assertRaises(c.FactoryError):
                    m.materialize(data, self.f["baseline"], self.f["source"], c.read)


class FactoryIntake(ContractCase):
    def setUp(self):
        super().setUp()
        self.data, self.baselines, self.originals = m.materialize(
            self.f["request"]["intake"], self.f["baseline"], self.f["source"], c.read)

    def validate(self, data=None, baselines=None, originals=None, history=None, baseline_only=False):
        return m.validate_intake(self.data if data is None else data, self.schema,
                         self.baselines if baselines is None else baselines,
                         None if baseline_only else self.originals if originals is None else originals,
                         history)

    def test_all_eight_roles_required_per_solution_with_short_specific_na_and_shared_rows(self):
        self.works(self.validate)
        for role in c.ROLES:
            data = copy.deepcopy(self.data)
            data["artifacts"] = [row for row in data["artifacts"] if row["role"] != role]
            with self.subTest(role=role), self.assertRaises(c.FactoryError):
                self.validate(data)
        data = copy.deepcopy(self.data)
        identity = next(row for row in data["artifacts"] if row["role"] == "identity")
        identity["rationale"] = "No runtime."
        self.works(self.validate, data)
        for sentinel in ("n/a", "na", "none", "unknown", "not applicable", "not-applicable", "tbd", "todo"):
            identity["rationale"] = " \t" + sentinel.upper() + "... "
            with self.subTest(sentinel=sentinel), self.assertRaises(c.FactoryError):
                self.validate(data)
        data = copy.deepcopy(self.data)
        selected = copy.deepcopy(data["selected_solutions"][0])
        selected.update(solution_id="caldova-second", agent_ids=["second-agent"])
        data["selected_solutions"].append(selected)
        for row in data["artifacts"]:
            row["solution_ids"].append("caldova-second")
        requirement = copy.deepcopy(data["requirements"][0])
        requirement.update(id="fr-002", solution_id="caldova-second")
        data["requirements"].append(requirement)
        self.works(self.validate, data)

    def test_draft_engineering_gaps_allowed_but_missing_structural_owner_is_not(self):
        data = copy.deepcopy(self.data)
        data["review"].update(status="needs-clarification", approval=None)
        design = next(row for row in data["artifacts"] if row["role"] == "solution-design")
        design.update(status="missing", source=None, baseline=None, transformation=None)
        data["requirements"] = []
        self.works(self.validate, data)
        for field, value in (("owners", []), ("scope", " "), ("agent_ids", [])):
            changed = copy.deepcopy(data)
            changed["selected_solutions"][0][field] = value
            with self.subTest(field=field), self.assertRaises(c.FactoryError):
                self.validate(changed)
        data["review"] = copy.deepcopy(self.data["review"])
        with self.assertRaises(c.FactoryError):
            self.validate(data)
        self.assertEqual(data["review"]["status"], "accepted", "explicit acceptance is never downgraded")

    def test_recorded_transfer_review_acquisition_and_transform_evidence_always_required(self):
        from tests.factory_fixture import approved
        self.works(self.validate)
        for status in ("accepted", "needs-clarification", "rejected"):
            for case in ("restricted", "null-transfer", "pending-transfer", "wrong-acquisition",
                 "missing-verifier", "equal-redaction", "equal-transformation", "none-approval"):
                data = copy.deepcopy(self.data)
                data["review"]["status"] = status
                if case == "restricted":
                    data["transfer"]["classification"] = "restricted"
                elif case == "null-transfer":
                    data["transfer"]["approval"] = None
                elif case == "pending-transfer":
                    data["transfer"].update(permission="pending", approval=None)
                elif case == "wrong-acquisition":
                    data["acquisition"]["method"] = "exact-file-download"
                elif case == "missing-verifier":
                    data["acquisition"]["verified_by"] = " "
                else:
                    transform = data["artifacts"][0]["transformation"]
                    transform.update(kind={"equal-redaction": "redaction", "equal-transformation": "transformation",
                                           "none-approval": "none"}[case], approval=approved())
                with self.subTest(status=status, case=case), self.assertRaises(c.FactoryError):
                    self.validate(data)
        for case in ("review-approval", "requirement", "blocking-gap", "blocking-decision", "missing-transform"):
            data = copy.deepcopy(self.data)
            if case == "review-approval":
                data["review"]["approval"] = None
            elif case == "requirement":
                data["requirements"] = []
            elif case == "missing-transform":
                next(row for row in data["artifacts"] if row["role"] == "blueprint")["transformation"]["approval"] = None
            else:
                data["gaps" if case == "blocking-gap" else "decisions"] = [
            {"id": "unresolved", "solution_id": "caldova-service", "description": "Review boundary.",
             "blocking": True, "status": "open", "resolution": None}]
            with self.subTest(case=case), self.assertRaises(c.FactoryError):
                self.validate(data)

    def test_duplicate_ids_unselected_refs_and_conflicting_applicability_fail(self):
        self.works(self.validate)
        for field in ("selected_solutions", "artifacts", "requirements", "gaps", "decisions"):
            data = copy.deepcopy(self.data)
            if field in ("gaps", "decisions"):
                data[field] = [{"id": "issue-one", "solution_id": "caldova-service",
                        "description": "Resolved synthetic issue.", "blocking": True,
                        "status": "resolved", "resolution": "Reviewed locally."}]
            data[field].append(copy.deepcopy(data[field][0]))
            with self.subTest(field=field), self.assertRaises(c.FactoryError):
                self.validate(data)
        for case in ("unselected", "cross-id", "conflict", "prd-na"):
            data = copy.deepcopy(self.data)
            if case == "unselected":
                data["requirements"][0]["solution_id"] = "unselected"
            elif case == "cross-id":
                data["requirements"][0]["id"] = data["artifacts"][0]["id"]
            elif case == "prd-na":
                data["artifacts"][0].update(status="not-applicable", rationale="No runtime.",
                                     source=None, baseline=None, transformation=None)
            else:
                row = copy.deepcopy(data["artifacts"][0])
                row.update(id="missing-prd", status="missing", source=None, baseline=None, transformation=None)
                data["artifacts"].append(row)
            with self.subTest(case=case), self.assertRaises(c.FactoryError):
                self.validate(data)

    def test_baseline_only_pass_does_not_hide_full_source_shared_budget_failure(self):
        from tests.factory_fixture import approved
        roles = ("prd", "solution-design", "blueprint", "decisions")
        data = copy.deepcopy(self.data)
        data["artifacts"] = [row for row in data["artifacts"] if row["role"] not in roles]
        baselines, originals = {}, {}
        for index, role in enumerate(roles):
            row = copy.deepcopy(self.data["artifacts"][0])
            row.update(id=f"large-{index}", role=role)
            raw = b"A" * (8 * MIB)
            row["source"].update(path=f"large-{index}.txt", sha256=c.digest(raw))
            row["baseline"].update(path=f"docs/intake/records/caldova-intake/artifacts/large-{index}.txt",
                           sha256=c.digest(raw))
            originals[row["source"]["path"]] = baselines[row["baseline"]["path"]] = raw
            data["artifacts"].append(row)
        self.works(self.validate, data, baselines, originals)
        last = data["artifacts"][-1]
        changed = originals[last["source"]["path"]] + b"B"
        originals[last["source"]["path"]] = changed
        last["source"]["sha256"] = c.digest(changed)
        last["transformation"].update(kind="transformation", approval=approved())
        self.works(self.validate, data, baselines, baseline_only=True)
        with self.assertRaises(c.FactoryError):
            self.validate(data, baselines, originals)
        # A real per-file cap failure, even with ample remaining total budget.
        data = copy.deepcopy(self.data)
        baselines = dict(self.baselines)
        first = next(row for row in data["artifacts"] if row["status"] == "provided")
        raw = b"A" * (16 * MIB + 1)
        first["source"]["sha256"] = first["baseline"]["sha256"] = c.digest(raw)
        baselines[first["baseline"]["path"]] = raw
        with self.assertRaises(c.FactoryError):
            self.validate(data, baselines, baseline_only=True)

    def test_history_chain_preserves_raw_windows_json_and_refuses_mixed_alias_maps(self):
        previous = copy.deepcopy(self.data)
        previous["intake_id"] = "prior-intake"
        for row in previous["artifacts"]:
            if row["status"] == "provided":
                row["source"]["path"] = "selected\\" + row["source"]["path"]
                row["baseline"]["path"] = row["baseline"]["path"].replace("caldova-intake", "prior-intake").replace("/", "\\")
        raw = json.dumps(previous, ensure_ascii=False, indent=1).encode("utf-8") + b"\n "
        frozen = c.decode(raw)
        current = copy.deepcopy(self.data)
        current["supersedes"] = "prior-intake"
        history = {"prior-intake": frozen}
        before = copy.deepcopy(history)
        self.works(self.validate, current, history=history)
        self.assertEqual(history, before)
        self.assertEqual(c.decode(raw), frozen)
        self.assertIn(b"selected\\\\", raw)
        aliases = dict(self.baselines)
        name, content = next(iter(aliases.items()))
        aliases[name.replace("/", "\\")] = content
        with self.assertRaises(c.FactoryError):
            self.validate(current, baselines=aliases, history=history)
        for case in ("missing", "unaccepted", "bad-schema", "wrong-id", "cycle", "current-reused"):
            changed = copy.deepcopy(history)
            if case == "missing":
                changed = {}
            elif case == "unaccepted":
                changed["prior-intake"]["review"]["status"] = "needs-clarification"
            elif case == "bad-schema":
                changed["prior-intake"]["unexpected"] = True
            elif case == "wrong-id":
                changed["prior-intake"]["intake_id"] = "another"
            elif case == "cycle":
                changed["prior-intake"]["supersedes"] = "prior-intake"
            else:
                changed["caldova-intake"] = copy.deepcopy(self.data)
            with self.subTest(case=case), self.assertRaises(c.FactoryError):
                self.validate(current, history=changed)

    def test_history_real_128_record_boundary(self):
        current = copy.deepcopy(self.data)
        history = {}
        current["supersedes"] = "prior-0"
        for index in range(127):
            previous = copy.deepcopy(self.data)
            previous.update(intake_id=f"prior-{index}", supersedes=f"prior-{index + 1}" if index < 126 else None)
            history[f"prior-{index}"] = previous
        self.works(self.validate, current, history=history)
        history["prior-126"]["supersedes"] = "prior-127"
        history["prior-127"] = copy.deepcopy(self.data)
        history["prior-127"]["intake_id"] = "prior-127"
        with self.assertRaises(c.FactoryError):
            self.validate(current, history=history)

    def test_actual_encoded_manifest_exact_1mib_then_one_byte_over(self):
        data = copy.deepcopy(self.data)
        data["requirements"] = [
            {"id": f"boundary-{index}", "solution_id": "caldova-service", "description": "x",
             "acceptance_criteria": ["Visible reviewed status."]} for index in range(512)]
        remaining = MIB - len(c.encoded(data))
        for row in data["requirements"]:
            amount = min(3999, remaining)
            row["description"] += "x" * amount
            remaining -= amount
        self.assertEqual(remaining, 0)
        self.assertEqual(len(c.encoded(data)), MIB)
        self.works(self.validate, data)
        row = next(row for row in data["requirements"] if len(row["description"]) < 4000)
        row["description"] += "x"
        self.assertEqual(len(c.encoded(data)), MIB + 1)
        with self.assertRaisesRegex(c.FactoryError, "FACTORY_LIMIT"):
            self.validate(data)
