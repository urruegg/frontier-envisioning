"""Actual identity catalogue HTML keeps text accessible without changing artwork inputs."""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from tests.unit._util import ROOT, load

IDENTITY = ROOT / "plugin/skills/frontier-agent-identity"


class CatalogueParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chips = []
        self.headers = []
        self.tags = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if attrs.get("class") == "chip":
            self.chips.append(attrs)
        if attrs.get("class") == "jhead":
            self.headers.append(attrs)


def declarations(style):
    return dict(part.strip().split(":", 1) for part in style.split(";") if ":" in part)


class IdentityCatalogue(unittest.TestCase):
    def setUp(self):
        modules, path = sys.modules.copy(), sys.path[:]

        def restore():
            sys.path[:] = path
            for name in set(sys.modules) - set(modules):
                if Path(getattr(sys.modules[name], "__file__", "") or ".").is_relative_to(IDENTITY):
                    del sys.modules[name]
            for name, module in modules.items():
                if name not in sys.modules or sys.modules[name] is not module:
                    sys.modules[name] = module

        self.addCleanup(restore)
        maker = load("plugin/skills/frontier-agent-identity/scripts/make_kit.py", "catalogue_maker")
        self.builder = maker.load_kit_module(IDENTITY / "kit/scripts", "build_identity_assets")
        self.docs = maker.load_kit_module(IDENTITY / "kit/scripts", "identity_docs")
        self.cfg = copy.deepcopy(json.loads((IDENTITY / "examples/caldova-agent-identity.json").read_text(encoding="utf-8")))
        self.palette = copy.deepcopy(json.loads((IDENTITY / "examples/caldova-palette.json").read_text(encoding="utf-8")))

    def render(self):
        for agent in self.cfg["agents"]:
            agent["derived"] = self.builder.L.derive(self.cfg, agent, self.palette)
        with tempfile.TemporaryDirectory() as tmp:
            html = self.docs.catalog_html(self.cfg, self.palette, self.builder.by_journey(self.cfg, self.palette), Path(tmp))
        parsed = CatalogueParser()
        parsed.feed(html)
        return html, parsed

    def test_every_rendered_status_has_aa_text_contrast_without_mutating_palette(self):
        original = copy.deepcopy(self.palette)
        _, parsed = self.render()
        self.assertEqual(len(parsed.chips), len(self.cfg["agents"]))
        for chip in parsed.chips:
            style = declarations(chip["style"])
            with self.subTest(style=style):
                self.assertGreaterEqual(self.builder.L.contrast(style["color"], style["background"]), 4.5)
        self.assertEqual(self.palette, original)

    def test_finance_header_subtitle_has_no_contrast_lowering_opacity(self):
        html, parsed = self.render()
        rule = re.search(r"\.jhead small\s*\{([^}]+)}", html)
        self.assertIsNotNone(rule)
        self.assertEqual(float(declarations(rule[1]).get("opacity", "1")), 1)
        finance = next(j for j in self.palette["journeys"].values() if j["short"] == "Finance")
        style = {"background": finance["background"], "color": finance["glyph"]}
        self.assertIn(style, [declarations(header["style"]) for header in parsed.headers])
        self.assertGreaterEqual(self.builder.L.contrast(style["color"], style["background"]), 4.5)

    def test_catalogue_still_escapes_customer_status_and_agent_text(self):
        text = '<script>alert("Caldova & test")</script>'
        self.cfg["customer"]["short"] = text
        self.cfg["agents"][0]["shortDescription"] = text
        for status in self.palette["statusStyles"].values():
            status["label"] = text
        html, parsed = self.render()
        self.assertNotIn("script", parsed.tags)
        self.assertNotIn(text, html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&amp; test", html)


if __name__ == "__main__":
    unittest.main()
