"""Reproducible, core-only documentation samples and honest user entry points."""
from __future__ import annotations

import contextlib
import io
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load


def html(day="2026-11-12", **changes):
    data = {"meta": {"generated": day, "plugin_version": "1.9.1", "customer": "Caldova Industrial AG"},
            "identity": {"kit": "fictitious"}, "ontology": {"entity_types": [{"id": "Customer"}]},
            "title": "Caf\u00e9 workshop",
            "value_case": {"totals": {"npv": 2, "economic_year": 1, "budget_year": 1}, "inputs_needed": []},
            "domains": [{"use_cases": [
                {"id": name, "business_value": {"npv": 2, "economic_year": 1, "budget_year": 1}}
                for name in ("UC05", "UC09")
            ]}], **changes}
    return ('<!doctype html><script id="bp-data" type="application/json">'
            + json.dumps(data) + '</script><script>console.log("demo");</script>').encode()


def png_chunk(kind, payload):
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))


PNG = (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1440, 1000, 8, 6, 0, 0, 0))
       + png_chunk(b"IDAT", zlib.compress(bytes(1000 * (1 + 1440 * 4))))
       + png_chunk(b"IEND", b""))


class DocsDemo(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / "tools" / "build_docs_demo.py").is_file(), "documentation demo generator is missing")
        self.tool = load("tools/build_docs_demo.py")

    def capture(self, source, output):
        output.mkdir(parents=True, exist_ok=True)
        shots = []
        for name, route in self.tool.VIEWS:
            path = output / (name + ".png")
            path.write_bytes(PNG)
            shots.append({"name": name, "route": route, "file": path.name, "width": 1440, "height": 1000})
        return {"browser": "Chromium fixture", "playwright": "test fixture", "screenshots": shots,
                "viewport": {"width": 1440, "height": 1000}, "color_scheme": "light",
                "reduced_motion": "reduce", "locale": "en-GB", "timezone": "UTC"}

    def publish(self, root, source=None, capture=None):
        source = source or root / "built.html"
        if not source.exists():
            source.write_bytes(html())
        self.tool.publish(source, root, capture=capture or self.capture)
        return source

    def test_publishes_exactly_five_images_and_checks_the_actual_html(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.publish(root)
            self.assertEqual(self.tool.verify(root, source), [])
            self.assertEqual((root / "docs/demo/caldova-blueprint.html").read_bytes(), source.read_bytes())
            self.assertEqual({p.name for p in (root / "docs/images/caldova").iterdir()},
                             {"overview.png", "org-model.png", "agents.png", "agent-identity.png", "ontology.png"})
            manifest = json.loads((root / "docs/demo/manifest.json").read_text())
            self.assertEqual(manifest["profile"], "core")
            self.assertEqual(manifest["plugin_version"], "1.9.1")
            self.assertNotIn(str(root), json.dumps(manifest))

    def test_only_the_volatile_generation_day_is_normalised(self):
        self.assertEqual(self.tool.canonical_html(html("2026-11-12")),
                         self.tool.canonical_html(html("2026-11-13")))
        self.assertNotEqual(self.tool.canonical_html(html()),
                            self.tool.canonical_html(html(title="Changed hypothesis")))
        with self.assertRaises(ValueError):
            self.tool.canonical_html(b"not a blueprint")

    def test_comparison_preserves_json_format_escaping_and_requires_a_real_date(self):
        raw = html()
        for changed in (raw.replace(b', "', b',  "'), raw.replace(b"\\u00e9", "é".encode())):
            with self.subTest(changed=changed[:100]):
                self.assertNotEqual(self.tool.canonical_html(raw), self.tool.canonical_html(changed))
        for changed in (raw.replace(b'"generated": "2026-11-12", ', b""),
                        raw.replace(b"2026-11-12", b"2026-99-99")):
            with self.subTest(invalid_date=changed[:100]), self.assertRaises(ValueError):
                self.tool.canonical_html(changed)

    def test_identity_kit_and_shared_helper_mutations_invalidate_the_sample(self):
        for name in ("plugin/skills/frontier-agent-identity/kit/glyph.svg",
                     "plugin/skills/frontier-agent-identity/kit/scripts/builder.py",
                     "tools/fe_lib.py", "plugin/.claude-plugin/plugin.json", "plugin/package/manifest.json",
                     "tests/fixtures/caldova-raster-1.9.2-inputs.json",
                     "tests/fixtures/caldova-raster-1.10.0-inputs.json"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = root.joinpath(*name.split("/"))
                path.parent.mkdir(parents=True)
                path.write_bytes(b"original")
                source = self.publish(root)
                path.write_bytes(b"modified")
                self.assertTrue(self.tool.verify(root, source))

    def test_invalid_png_capture_preserves_all_previous_assets(self):
        invalid = (
            PNG[:33],
            PNG[:-12],
            PNG[:40] + bytes([PNG[40] ^ 1]) + PNG[41:],
            PNG[:33] + png_chunk(b"IDAT", b"invalid pixels") + png_chunk(b"IEND", b""),
            PNG[:8] + png_chunk(b"IHDR", PNG[16:29] + b"\x00") + PNG[33:],
            PNG[:33] + PNG[8:],
        )
        for payload in invalid:
            with self.subTest(length=len(payload)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = self.publish(root)
                previous = {p: p.read_bytes() for p in (root / "docs").rglob("*") if p.is_file()}

                def corrupt(source, output):
                    report = self.capture(source, output)
                    for image in output.iterdir():
                        image.write_bytes(payload)
                    return report

                with self.assertRaises(ValueError):
                    self.tool.publish(source, root, capture=corrupt)
                self.assertTrue(all(path.read_bytes() == data for path, data in previous.items()))

    def test_missing_ordinary_value_results_cannot_replace_the_sample(self):
        for change in ({"value_case": None}, {"value_case": {}}, {"domains": []}):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = self.publish(root)
                previous = (root / "docs/demo/manifest.json").read_bytes()
                source.write_bytes(html(**change))
                with self.assertRaises(ValueError):
                    self.tool.publish(source, root, capture=self.capture)
                self.assertEqual((root / "docs/demo/manifest.json").read_bytes(), previous)

    def test_detects_html_image_source_and_fresh_build_drift(self):
        for drift in ("html", "png", "source", "built"):
            with self.subTest(drift=drift), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source_file = root / "src/renderer/template.js"
                source_file.parent.mkdir(parents=True)
                source_file.write_text("original", encoding="utf-8")
                source = self.publish(root)
                if drift == "html":
                    target = root / "docs/demo/caldova-blueprint.html"
                    target.write_bytes(target.read_bytes() + b"changed")
                elif drift == "png":
                    target = root / "docs/images/caldova/overview.png"
                    target.write_bytes(target.read_bytes() + b"changed")
                elif drift == "source":
                    source_file.write_text("modified", encoding="utf-8")
                else:
                    source.write_bytes(html(title="different"))
                self.assertTrue(self.tool.verify(root, source), drift)

    def test_refuses_preview_or_invalid_inputs_without_replacing_previous_output(self):
        for data in (html(finops={"agents": []}), html(value_case={"finops_preview": {"maturity": "preview"}}),
                     html(agent_finops={"schema": "frontier-agent-finops-view/1.0", "records": []}),
                     html(annotations={"agent_finops": {}}),
                     b"<html>not a blueprint</html>"):
            with self.subTest(data=data[:60]), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = self.publish(root)
                manifest = root / "docs/demo/manifest.json"
                previous = manifest.read_bytes()
                source.write_bytes(data)
                with self.assertRaises(ValueError):
                    self.tool.publish(source, root, capture=self.capture)
                self.assertEqual(manifest.read_bytes(), previous)

    def test_incomplete_capture_preserves_all_existing_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.publish(root)
            previous = {p: p.read_bytes() for p in (root / "docs").rglob("*") if p.is_file()}

            def incomplete(source, output):
                result = self.capture(source, output)
                result["screenshots"].pop()
                return result

            with self.assertRaises(ValueError):
                self.tool.publish(source, root, capture=incomplete)
            self.assertTrue(all(path.read_bytes() == data for path, data in previous.items()))

    def test_check_reports_malformed_manifest_and_missing_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.publish(root)
            (root / "docs/images/caldova/ontology.png").unlink()
            self.assertTrue(self.tool.verify(root, source))
            (root / "docs/demo/manifest.json").write_text("[]", encoding="utf-8")
            self.assertTrue(self.tool.verify(root, source))

    def test_check_rejects_unexpected_images_and_inconsistent_capture_provenance(self):
        for field in ("extra", "locale", "browser", "width", "capture-shape"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = self.publish(root)
                path = root / "docs/demo/manifest.json"
                manifest = json.loads(path.read_text())
                if field == "extra":
                    (root / "docs/images/caldova/unexpected.png").write_bytes(b"unexpected")
                elif field == "width":
                    manifest["capture"]["screenshots"][0]["width"] = 1
                elif field == "capture-shape":
                    manifest["capture"] = []
                else:
                    manifest["capture"][field] = "" if field == "browser" else "unexpected"
                path.write_text(json.dumps(manifest), encoding="utf-8")
                self.assertTrue(self.tool.verify(root, source), field)

    def test_invalid_blueprint_shapes_are_explicit_errors(self):
        for data in (html(ontology=[]), html(ontology="invalid"), html(meta=[])):
            with self.subTest(data=data[:70]), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "sample.html"
                source.write_bytes(data)
                with self.assertRaises(ValueError):
                    self.tool.publish(source, Path(directory), capture=self.capture)

    def test_strict_gate_checks_sample_after_building_core(self):
        dev = load("tools/dev.py")
        with mock.patch.multiple(dev, cmd_template_check=mock.DEFAULT, cmd_lint=mock.DEFAULT,
                                 cmd_docs=mock.DEFAULT, cmd_scan=mock.DEFAULT, cmd_test=mock.DEFAULT,
                                 cmd_selftest=mock.DEFAULT, cmd_package=mock.DEFAULT, cmd_demo=mock.DEFAULT,
                                 cmd_verify_release=mock.DEFAULT, cmd_dom=mock.DEFAULT), \
                mock.patch.object(dev, "tool", return_value=0) as tool, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dev.main(["check"]), 0)
        tool.assert_any_call("build_docs_demo", ["--check", "--demo", str(dev.DEMO_DIR)])


class ReaderDocumentation(unittest.TestCase):
    def test_reader_entry_points_and_five_view_gallery(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("## Local intake status", readme)
        self.assertIn("docs/getting-started.md", readme)
        self.assertIn("docs/demo/README.md", readme)
        gallery = ROOT / "docs/demo/README.md"
        self.assertTrue(gallery.is_file(), "Caldova gallery is missing")
        text = gallery.read_text(encoding="utf-8")
        for name in ("overview", "org-model", "agents", "agent-identity", "ontology"):
            self.assertIn(f"{name}.png", text)
        self.assertIn("caldova-blueprint.html", text)

    def test_starter_prompt_and_mermaid_explain_real_boundaries(self):
        prompt = ROOT / "docs/starter-prompts.md"
        guide = ROOT / "docs/getting-started.md"
        self.assertTrue(prompt.is_file(), "adapted starter prompt is missing")
        self.assertTrue(guide.is_file(), "user guide is missing")
        text = prompt.read_text(encoding="utf-8")
        for phrase in ("read-only", "FinOps", "available", "manual", "hypoth", "Caldova"):
            self.assertIn(phrase.lower(), text.lower())
        self.assertNotRegex(text, r"\b[A-Z]+-\d{5,}\.pdf\b")
        diagrams = text + guide.read_text(encoding="utf-8") + (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(diagrams.count("```mermaid"), 2)
