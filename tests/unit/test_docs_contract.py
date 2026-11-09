"""Contracts for repository-owned documentation and the product-document split."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from tests.unit._util import ROOT, load

fe_lib = load("tools/fe_lib.py")


class DocsAgentContract(unittest.TestCase):
    def test_definition_has_minimal_tools_and_boundaries(self) -> None:
        path = ROOT / ".github" / "agents" / "docs-agent.agent.md"
        self.assertTrue(path.is_file(), "docs-agent definition missing")
        text = path.read_text(encoding="utf-8")
        frontmatter = fe_lib.frontmatter(text)

        self.assertEqual(frontmatter["name"], "docs-agent")
        self.assertEqual(frontmatter["tools"], "[read, search, edit, todo]")
        self.assertEqual(frontmatter["user-invocable"], "true")
        self.assertNotIn("model", frontmatter)
        self.assertEqual(
            set(frontmatter), {"name", "description", "tools", "user-invocable"}
        )
        for topic in (r"maintain", r"headers?", r"links?|references", r"catalogue"):
            with self.subTest(description_topic=topic):
                self.assertRegex(frontmatter["description"].lower(), topic)

        self.assertTrue(text.startswith("---\n"), "YAML must precede the H1")
        self.assertEqual(len(re.findall(r"(?m)^# .+$", text)), 1)
        yaml_end = text.find("\n---", 4)
        self.assertGreater(yaml_end, 0, "YAML closing delimiter missing")
        body = text[yaml_end + 4:].lstrip()
        self.assertTrue(body.startswith("# "), "H1 must follow YAML")
        header = body.split("\n\n", 2)[1]
        fields = dict(re.findall(r"(?m)^\| (\w+) \| (.+) \|$", header))
        fields.pop("Field", None)
        self.assertEqual(
            set(fields), {"Version", "Date", "Author", "Status", "Scope", "References"}
        )
        self.assertRegex(fields["Version"], r"^\d+\.\d+(?:\.\d+)?$")
        self.assertEqual(fields["Date"], "2026-11-09")
        self.assertRegex(fields["Author"], r"(?i)AI-assisted|Copilot")
        self.assertRegex(fields["Status"], r"(?i)no approval")
        self.assertRegex(fields["Scope"], r"(?i)approved.*repository-owned")

        links = dict(re.findall(r"\[([^]]+)\]\(([^)]+)\)", fields["References"]))
        for label, target in (
            ("AGENTS", ROOT / "AGENTS.md"),
            ("Docs", ROOT / "docs" / "README.md"),
        ):
            with self.subTest(reference=label):
                self.assertIn(label, links)
                self.assertFalse(Path(links[label]).is_absolute())
                self.assertEqual((path.parent / links[label]).resolve(), target)
                self.assertTrue(target.is_file())

        prose = " ".join(body.split())
        for requirement in (
            r"(?i)maintain.*approved.*repository-owned.*prose",
            r"(?i)read.*AGENTS.*issue.*spec.*plan.*sprint",
            r"(?i)identify.*authorit.*audience.*owner.*status",
            r"(?i)preserve.*YAML frontmatter.*machine.*product.*exclusions",
            r"(?i)real dates/authorship.*status",
            r"(?i)direct-child catalogues.*backlinks.*same PR",
            r"(?i)request.*header/link/traceability validation.*parent/CI",
            r"(?i)report.*edits.*evidence.*unresolved decisions",
            r"(?i)author is not.*owner.*approver",
            r"(?i)no terminal.*administrative.*merge.*release.*deployment authority",
            r"(?i)never change classification.*distribute internal",
        ):
            with self.subTest(requirement=requirement):
                self.assertRegex(prose, requirement)

        for prohibition, required_terms in (
            (
                r"(?i)(?:do not|never) edit ([^.]+)\.",
                (
                    "CODEOWNERS", "hooks", "licences", "releases", "vendored",
                    "generated output", "workflows", "infrastructure",
                    "permissions", "code",
                ),
            ),
            (
                r"(?i)(?:do not|never) blanket-change ([^.]+)\.",
                ("packaged Markdown", "identity-template inputs"),
            ),
            (
                r"(?i)(?:do not|never) invent ([^.]+)\.",
                (
                    "issues", "approval", "owners", "dates", "authorship",
                    "status", "released capability", "completed validation",
                ),
            ),
        ):
            with self.subTest(prohibition=prohibition):
                match = re.search(prohibition, prose)
                if match is None:
                    self.fail(f"missing explicit prohibition: {prohibition}")
                for term in required_terms:
                    with self.subTest(boundary=term):
                        self.assertIn(term.casefold(), match.group(1).casefold())


class ProductDocumentSplit(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = json.loads(
            (ROOT / "tests" / "fixtures" / "prd-design-identifiers.json")
            .read_text(encoding="utf-8")
        )
        self.documents = {}
        for name in ("prd.md", "solution-design.md"):
            path = ROOT / "docs" / name
            self.assertTrue(path.is_file(), f"missing {name}")
            self.documents[name] = path.read_text(encoding="utf-8")

    @staticmethod
    def headings(text: str) -> list[str]:
        """Ignore fenced examples when counting actual Markdown headings."""
        lines = []
        fence = ""
        for line in text.splitlines():
            marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
            if marker:
                token = marker.group(1)
                if not fence:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = ""
            elif not fence and re.match(r"^#{1,6} ", line):
                lines.append(line)
        return lines

    @staticmethod
    def slug(heading: str) -> str:
        return re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")

    @staticmethod
    def content_digest(text: str) -> str:
        """Allow companion links, but no prose, table or result rewrites."""
        text = re.sub(
            r"\[([^]]+)\]\((?:prd|solution-design)\.md#[^)]+\)", r"\1", text
        )
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def test_one_actual_h1_and_truthful_document_metadata(self) -> None:
        texts = dict(self.documents)
        texts["prd-and-solution-design.md"] = (
            ROOT / "docs" / "prd-and-solution-design.md"
        ).read_text(encoding="utf-8")
        for name, text in texts.items():
            with self.subTest(document=name):
                self.assertTrue(text.startswith("# "))
                self.assertEqual(
                    len([h for h in self.headings(text) if h.startswith("# ")]), 1
                )
                header = text.split("\n\n", 2)[1]
                fields = dict(re.findall(r"(?m)^\| (\w+) \| (.+) \|$", header))
                fields.pop("Field", None)
                self.assertEqual(
                    set(fields),
                    {"Version", "Date", "Author", "Status", "Scope", "References"},
                )
                self.assertRegex(fields["Version"], r"^\d+\.\d+(?:\.\d+)?$")
                self.assertNotEqual(fields["Version"], "1.6.1")
                self.assertEqual(fields["Date"], "2026-11-09")
                self.assertIn("Urs Rüegg", fields["Author"])
                self.assertIn("Copilot", fields["Author"])
                self.assertRegex(fields["Status"], r"(?i)no.*approval")
                self.assertIn("document revision", text.lower())

    def test_original_identifiers_and_section_headings_are_retained(self) -> None:
        joined = "\n".join(self.documents.values())
        ids = sorted(set(re.findall(r"\b(?:FR|NFR|AC|D|TD|ADR)-\d+\b", joined)))
        self.assertEqual(ids, self.baseline["identifiers"])
        self.assertEqual(ids, sorted(set(ids)))
        self.assertRegex(self.baseline["source_sha256"], r"^[0-9a-f]{64}$")
        for section in self.baseline["sections"]:
            with self.subTest(section=section):
                name = "prd.md" if section.startswith("A.") else "solution-design.md"
                expected_level = "### " if re.match(r"B\.\d+\.\d+", section) else "## "
                self.assertIn(expected_level + section, self.headings(self.documents[name]))

    def test_substantive_original_section_content_is_unchanged(self) -> None:
        actual = {}
        for text in self.documents.values():
            matches = list(re.finditer(r"(?m)^#{2,3} ([AB]\.\d[^\n]*)$", text))
            for index, match in enumerate(matches):
                end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                block = text[match.start():end].split("## Appendix — File inventory")[0]
                actual[match.group(1)] = self.content_digest(block)
        self.assertEqual(set(actual), set(self.baseline["content_sha256"]))
        for section, expected in self.baseline["content_sha256"].items():
            with self.subTest(section=section):
                self.assertEqual(
                    actual[section], expected, f"original prose/table/result changed: {section}"
                )

    def test_original_product_context_unreleased_note_and_inventory_are_retained(self) -> None:
        prd = self.documents["prd.md"]
        context = prd.split("## Product context and provenance\n", 1)[1]
        context = context[context.index("| Field | Value |"):].split("\n---\n", 1)[0]
        self.assertEqual(
            self.content_digest(context), self.baseline["shared_context_sha256"]
        )
        patch = prd[prd.index("## 1.6.1 patch:"):].split("## Part A —", 1)[0]
        self.assertEqual(self.content_digest(patch), self.baseline["patch_sha256"])
        design = self.documents["solution-design.md"]
        inventory_heading = "## Appendix — File inventory (1.6.0)"
        self.assertIn(inventory_heading, self.headings(design))
        inventory = design.split(inventory_heading, 1)[1]
        self.assertEqual(
            self.content_digest(inventory), self.baseline["inventory_sha256"]
        )
        self.assertRegex(prd, r"(?i)historical.*(?:results|claims)")
        self.assertRegex(design, r"(?i)historical.*(?:results|claims)")

    def test_companion_references_resolve_to_the_correct_document(self) -> None:
        prd = self.documents["prd.md"]
        design = self.documents["solution-design.md"]
        self.assertIn("[B.9](solution-design.md#b9-quality-and-testing)", prd)
        self.assertIn("[B.14](solution-design.md#b14-sources)", prd)
        self.assertIn("[D-05](prd.md#a13-open-decisions)", design)
        self.assertRegex(design, r"\[[^]]+\]\(prd\.md(?:#[^)]+)?\)")
        for name, text in self.documents.items():
            for target, anchor in re.findall(
                r"\]\((prd\.md|solution-design\.md)(?:#([^)]+))?\)", text
            ):
                with self.subTest(document=name, target=target, anchor=anchor):
                    if anchor:
                        self.assertIn(
                            anchor,
                            [self.slug(h.lstrip("# ")) for h in self.headings(self.documents[target])],
                        )

    def test_legacy_index_explicitly_maps_every_original_heading(self) -> None:
        old = (ROOT / "docs" / "prd-and-solution-design.md").read_text(encoding="utf-8")
        self.assertIn('id="a12-release-plan"', old)
        self.assertIn('id="b9-quality-and-testing"', old)
        self.assertLess(len(old.splitlines()), 200, "legacy path is an index, not a third copy")
        self.assertNotIn("| FR-0001 |", old)
        self.assertNotRegex(old, r"(?i)<meta[^>]+refresh|window\.location")
        self.assertIn("not an automatic redirect", old)
        target = "prd.md"
        for index, original in enumerate(self.baseline["headings"]):
            heading = original.lstrip("# ")
            if heading == "Part B — Solution Design":
                target = "solution-design.md"
            anchor = self.slug(heading)
            destination = "product-context-and-provenance" if index < 2 else anchor
            with self.subTest(legacy_anchor=anchor):
                self.assertEqual(old.count(f'<a id="{anchor}"></a>'), 1)
                self.assertIn(
                    f'<a id="{anchor}"></a>\n[{heading}]({target}#{destination})',
                    old,
                )
                self.assertIn(
                    destination,
                    [self.slug(h.lstrip("# ")) for h in self.headings(self.documents[target])],
                )

    def test_docs_catalogue_links_authoritative_documents_and_keeps_planning(self) -> None:
        catalogue = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        for name in ("prd.md", "solution-design.md", "prd-and-solution-design.md"):
            self.assertIn(f"]({name})", catalogue)
        for target in (
            "idea/README.md", "spec/README.md", "plan/README.md", "plans/README.md",
            "sprint/SPRINT-001-docs-governance-and-accessibility.md",
        ):
            self.assertIn(f"]({target})", catalogue)
