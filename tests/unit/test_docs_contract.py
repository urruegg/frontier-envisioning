"""Contracts for repository-owned documentation and the product-document split."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from datetime import date
from pathlib import Path

import yaml

from tests.unit._util import ROOT, load

fe_lib = load("tools/fe_lib.py")


def assert_iso_calendar_date(case: unittest.TestCase, value: str) -> None:
    """Revision dates may advance, but must be strict ISO calendar dates."""
    case.assertRegex(value, r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        case.fail(f"invalid ISO calendar date: {value}")
    case.assertEqual(parsed.isoformat(), value)


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
        assert_iso_calendar_date(self, fields["Date"])
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
        """Allow companion links; hash every remaining prose/table/result byte."""
        text = re.sub(
            r"\[([^]]+)\]\((?:prd|solution-design)\.md#[^)]+\)", r"\1", text
        )
        return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

    def split_development_block(
        self, text: str, start: str, end: str = ""
    ) -> tuple[str, str]:
        """Separate one explicit #7 addition, retaining its original neighbours."""
        self.assertEqual(text.count(start), 1, f"missing/duplicate addition: {start}")
        prefix, addition = text.split(start, 1)
        if end:
            self.assertEqual(text.count(end), 1, f"missing/duplicate boundary: {end}")
            self.assertIn(end, addition, "development addition must precede its boundary")
            addition, suffix = addition.split(end, 1)
            return prefix + end + suffix, start + addition
        return prefix, start + addition

    def original_section_content(self, section: str, block: str) -> str:
        """Keep the D2 migration receipt while admitting only approved A5 deltas."""
        if section == "A.8 Non-functional requirements":
            rows = re.findall(r"(?m)^\| NFR-0012 \| [^\n]+$", block)
            self.assertEqual(len(rows), 1, "NFR-0012 must remain one table row")
            # Original source: 19ec70f460f0d06dc3bca090bdb8973a9397ab8b,
            # docs/prd-and-solution-design.md. Its SHA-256 was verified against
            # source_sha256 in the unchanged migration receipt during implementation.
            original = (
                "| NFR-0012 | Accessibility | Keyboard navigation (arrows, Enter, Escape), "
                "ARIA roles and labels, visible focus, logical CSS properties, "
                "light and dark colour schemes |"
            )
            return block.replace(rows[0], original, 1)
        if section == "B.5 Blueprint HTML design":
            return self.split_development_block(
                block,
                "\n\n**Unreleased 1.6.1 accessibility implementation (#7).**",
                "\n\n**Agent identity.**",
            )[0]
        if section == "B.9 Quality and testing":
            return self.split_development_block(
                block,
                "\n\n### Development accessibility evidence (",
                "\n\nBehavioural tests to run before organisation-wide release "
                "(isolated skill-validator runs):",
            )[0]
        return block

    def test_one_actual_h1_and_truthful_document_metadata(self) -> None:
        texts = dict(self.documents)
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
                assert_iso_calendar_date(self, fields["Date"])
                self.assertIn("Urs Rüegg", fields["Author"])
                self.assertIn("Copilot", fields["Author"])
                self.assertRegex(fields["Status"], r"(?i)no.*approval")
                self.assertIn("document revision", text.lower())

    def test_original_identifiers_and_section_headings_are_retained(self) -> None:
        joined = "\n".join(self.documents.values())
        ids = sorted(set(re.findall(r"\b(?:FR|NFR|AC|D|TD|ADR)-\d+\b", joined)))
        additions = {f"FR-{i:04d}" for i in range(119, 128)} | {f"AC-{i:03d}" for i in range(26, 31)} | {"ADR-0025"}
        boundaries = tuple(self.headings(text).count("## 1.9.1 development intake") for text in self.documents.values())
        self.assertIn(boundaries, ((0, 0), (1, 1)), "1.9.1 additions need one explicit boundary in each product document")
        if boundaries == (1, 1):
            additions |= {f"FR-{i:04d}" for i in range(128, 142)} | {f"AC-{i:03d}" for i in range(31, 45)} | {"ADR-0026", "ADR-0027"}
        candidate = tuple(self.headings(text).count("## 1.10.0 development candidate") for text in self.documents.values())
        self.assertIn(candidate, ((0, 0), (1, 1)), "1.10.0 additions need one explicit boundary in each product document")
        if candidate == (1, 1):
            additions |= {f"FR-{i:04d}" for i in range(142, 154)} | {f"AC-{i:03d}" for i in range(45, 57)} | {"ADR-0028"}
        self.assertEqual(ids, sorted(set(self.baseline["identifiers"]) | additions))
        self.assertEqual(ids, sorted(set(ids)))
        self.assertRegex(self.baseline["source_sha256"], r"^[0-9a-f]{64}$")
        for section in self.baseline["sections"]:
            with self.subTest(section=section):
                name = "prd.md" if section.startswith("A.") else "solution-design.md"
                expected_level = "### " if re.match(r"B\.\d+\.\d+", section) else "## "
                self.assertIn(expected_level + section, self.headings(self.documents[name]))

    def test_integrated_development_scope_is_separate_from_historical_results(self) -> None:
        prd = self.documents["prd.md"]
        design = self.documents["solution-design.md"]
        for text in (prd, design):
            self.assertTrue("## 1.7.1 development intake" in text, "1.7.1 development section missing")
            self.assertIn("not a release", text.lower())
        block = prd.split("## 1.7.1 development intake", 1)[1].split("## Product context and provenance", 1)[0]
        self.assertEqual(set(re.findall(r"(?m)^\| (FR-\d+) \|", block)), {f"FR-{i:04d}" for i in range(119, 128)})
        acceptance = re.findall(r"(?m)^\| (AC-\d+) \| (.*)$", block)
        self.assertEqual({name for name, _ in acceptance}, {f"AC-{i:03d}" for i in range(26, 31)})
        self.assertTrue(all("Pending" in row and "Passed" not in row for _, row in acceptance))

    def test_substantive_original_section_content_is_unchanged(self) -> None:
        actual = {}
        for text in self.documents.values():
            matches = list(re.finditer(r"(?m)^#{2,3} ([AB]\.\d[^\n]*)$", text))
            for index, match in enumerate(matches):
                end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                block = text[match.start():end].split("## Appendix — File inventory")[0]
                section = match.group(1)
                actual[section] = self.content_digest(
                    self.original_section_content(section, block)
                )
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
        patch, _ = self.split_development_block(
            patch, "\n\n### Measured accessibility delivery ("
        )
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

    def test_current_accessibility_delta_is_truthful(self) -> None:
        """Approved current requirements/evidence are not historical release results."""
        prd = self.documents["prd.md"]
        rows = re.findall(r"(?m)^\| NFR-0012 \| [^\n]+$", prd)
        self.assertEqual(len(rows), 1)
        for requirement in (
            "| NFR-0012 | Accessibility | Target WCAG 2.2 AA, not certified conformance.",
            "Visible focus", "Tab/Shift+Tab containment", "Escape and exact trigger return",
            "Arrow/Home/End activation", "pressed-state filters",
            "keyboard-operable SVG groups", "both colour schemes", "24 × 24 CSS pixels",
            "all fourteen pages reflow at 320 CSS pixels without document overflow",
            "retaining local 2D diagram/table scrolling",
            "Automated browser checks do not replace manual",
            "Catalogue AA must pass the unchanged browser checks",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, rows[0])

        design = self.documents["solution-design.md"]
        _, implementation = self.split_development_block(
            design,
            "\n\n**Unreleased 1.6.1 accessibility implementation (#7).**",
            "\n\n**Agent identity.**",
        )
        implementation = " ".join(implementation.split())
        for detail in (
            "Tab/Shift+Tab", 'aria-modal="true"', "exact prior states",
            "roving tab stops", "Arrow/Home/End", "keyboard-operable",
            "24 × 24 CSS pixel hit areas", "320px", "no global overflow-hiding workaround",
        ):
            with self.subTest(implementation=detail):
                self.assertIn(detail, implementation)

        _, patch = self.split_development_block(
            prd[prd.index("## 1.6.1 patch:"):].split("## Part A —", 1)[0],
            "\n\n### Measured accessibility delivery (",
        )
        _, evidence = self.split_development_block(
            design,
            "\n\n### Development accessibility evidence (",
            "\n\nBehavioural tests to run before organisation-wide release "
            "(isolated skill-validator runs):",
        )
        for label, block in (("patch", patch), ("evidence", evidence)):
            prose = " ".join(block.split())
            with self.subTest(current_delta=label):
                self.assertIn("Later wave 4.40:1", prose)
                self.assertIn("Finance header 4.33:1", prose)
                self.assertIn("both colour schemes", prose)
                self.assertRegex(prose, r"Full L2 (?:remains red|is blocking)")
                self.assertIn("#8", prose)
                self.assertRegex(prose, r"(?:acceptance is incomplete|acceptance .*not claimed)")
                self.assertRegex(prose, r"(?:no gate waiver is approved|no assertion is skipped or waived)")
        prose = " ".join(evidence.split())
        self.assertIn("41 passed and 2 failed tests", prose)
        self.assertIn("Manual Narrator, zoom, real Windows high-contrast and voice checks are pending", prose)
        self.assertIn("not release results", prose)
        self.assertIn("above remains the historical 1.6.0 record", prose)

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

    def test_original_heading_targets_survive_without_a_compatibility_index(self) -> None:
        self.assertFalse((ROOT / "docs" / "prd-and-solution-design.md").exists())
        target = "prd.md"
        for index, original in enumerate(self.baseline["headings"]):
            heading = original.lstrip("# ")
            if heading == "Part B — Solution Design":
                target = "solution-design.md"
            anchor = self.slug(heading)
            destination = "product-context-and-provenance" if index < 2 else anchor
            with self.subTest(legacy_anchor=anchor):
                self.assertIn(
                    destination,
                    [self.slug(h.lstrip("# ")) for h in self.headings(self.documents[target])],
                )

    def test_docs_catalogue_links_authoritative_documents_and_keeps_planning(self) -> None:
        catalogue = (ROOT / "docs" / "README.md").read_text(encoding="utf-8")
        for name in ("prd.md", "solution-design.md"):
            self.assertIn(f"]({name})", catalogue)
        for target in (
            "ideas/README.md", "specs/README.md", "plans/README.md",
            "sprints/SPRINT-001-docs-governance-and-accessibility.md",
        ):
            self.assertIn(f"]({target})", catalogue)


class PreviewMaturityDocumentation(unittest.TestCase):
    def test_current_product_scope_has_bounded_191_requirements_and_acceptance(self) -> None:
        blocks = {}
        for name in ("prd.md", "solution-design.md"):
            text = (ROOT / "docs" / name).read_text(encoding="utf-8")
            headings = ProductDocumentSplit.headings(text)
            self.assertEqual(headings.count("## 1.9.1 development intake"), 1, name)
            self.assertLess(headings.index("## 1.9.1 development intake"), headings.index("## 1.7.1 development intake"))
            blocks[name] = text.split("## 1.9.1 development intake", 1)[1].split("## 1.7.1 development intake", 1)[0]
        self.assertEqual(
            set(re.findall(r"(?m)^\| (FR-\d+) \|", blocks["prd.md"])),
            {f"FR-{number:04d}" for number in range(128, 142)},
        )
        self.assertEqual(
            set(re.findall(r"(?m)^\| (AC-\d+) \|", blocks["prd.md"])),
            {f"AC-{number:03d}" for number in range(31, 45)},
        )
        scope = "\n".join(blocks.values())
        for term in ("FinOps", "Preview", "--acknowledge-finops-preview", "devPreview", "ADR-0026", "ADR-0027"):
            with self.subTest(term=term):
                self.assertIn(term, scope)
        self.assertRegex(scope, r"(?i)unreleased")

    def test_finops_notice_and_process_reference_are_available_to_skill_readers(self) -> None:
        preview = load("plugin/skills/frontier-finops/scripts/finops_preview.py")
        text = (ROOT / "plugin" / "skills" / "frontier-finops" / "SKILL.md").read_text(encoding="utf-8")
        prose = " ".join(re.sub(r"(?m)^\s*>\s?", "", text).replace("**", "").split())
        self.assertIn(preview.NOTICE, prose)
        self.assertIn("--acknowledge-finops-preview", text)
        self.assertTrue((ROOT / "plugin" / "skills" / "frontier-process" / "references" / "ontology-method.md").is_file())

    def test_working_agreement_catalogue_names_all_eight_registered_skills(self) -> None:
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        names = set(re.findall(r"(?m)^\| `?(frontier-[a-z-]+)`? \|", text))
        expected = {path.parent.name for path in (ROOT / "plugin" / "skills").glob("*/SKILL.md")}
        self.assertEqual(len(expected), 8)
        self.assertEqual(names, expected)
        self.assertNotRegex(text, r"(?i)\bseven\s+skills\b")


class ProductDocumentPreservationRegressions(unittest.TestCase):
    """Exercise the contracts in memory; never rewrite docs or the migration receipt."""

    def setUp(self) -> None:
        self.contract = ProductDocumentSplit()
        self.contract.setUp()

    def test_approved_191_identifiers_are_bounded_without_rewriting_history(self) -> None:
        original = {}
        for name, text in self.contract.documents.items():
            if "## 1.10.0 development candidate" in self.contract.headings(text):
                text, _ = self.contract.split_development_block(
                    text, "\n\n## 1.10.0 development candidate", "\n\n## 1.9.2 internal build candidate"
                )
            if "## 1.9.1 development intake" in self.contract.headings(text):
                text, _ = self.contract.split_development_block(
                    text, "\n\n## 1.9.1 development intake", "\n\n## 1.7.1 development intake"
                )
            original[name] = text
        additions = {
            "prd.md": "\n".join(
                [f"| FR-{number:04d} | Planned requirement |" for number in range(128, 142)]
                + [f"| AC-{number:03d} | Pending verification |" for number in range(31, 45)]
            ),
            "solution-design.md": "ADR-0026 and ADR-0027 remain Proposed.",
        }
        approved = {
            name: text.replace(
                "## 1.7.1 development intake",
                "## 1.9.1 development intake\n\n" + additions[name] + "\n\n## 1.7.1 development intake",
                1,
            )
            for name, text in original.items()
        }
        self.contract.documents = approved
        self.contract.test_original_identifiers_and_section_headings_are_retained()
        self.contract.test_substantive_original_section_content_is_unchanged()
        self.contract.test_original_product_context_unreleased_note_and_inventory_are_retained()
        for extra in ("FR-0142", "AC-045", "ADR-0028", "NFR-9999"):
            with self.subTest(unapproved_identifier=extra):
                self.contract.documents = {**approved, "prd.md": approved["prd.md"] + "\n" + extra}
                with self.assertRaises(AssertionError):
                    self.contract.test_original_identifiers_and_section_headings_are_retained()
        marker = "## 1.9.1 development intake"
        for name in approved:
            for replacement in ("## Unnamed development intake", marker + "\n\n" + marker):
                with self.subTest(document=name, development_boundary=replacement):
                    self.contract.documents = {
                        **approved,
                        name: approved[name].replace(marker, replacement, 1),
                    }
                    with self.assertRaises(AssertionError):
                        self.contract.test_original_identifiers_and_section_headings_are_retained()

    def test_approved_110_identifiers_are_bounded_without_rewriting_history(self) -> None:
        original = {}
        marker = "## 1.10.0 development candidate"
        for name, text in self.contract.documents.items():
            if marker in self.contract.headings(text):
                text, _ = self.contract.split_development_block(
                    text, "\n\n" + marker, "\n\n## 1.9.2 internal build candidate"
                )
            original[name] = text
        additions = {
            "prd.md": "\n".join(
                [f"| FR-{number:04d} | Planned requirement |" for number in range(142, 154)]
                + [f"| AC-{number:03d} | Pending verification |" for number in range(45, 57)]
            ),
            "solution-design.md": "ADR-0028 remains Proposed.",
        }
        approved = {
            name: text.replace(
                "## 1.9.2 internal build candidate",
                marker + "\n\n" + additions[name] + "\n\n## 1.9.2 internal build candidate",
                1,
            )
            for name, text in original.items()
        }
        self.contract.documents = approved
        self.contract.test_original_identifiers_and_section_headings_are_retained()
        self.contract.test_substantive_original_section_content_is_unchanged()
        self.contract.test_original_product_context_unreleased_note_and_inventory_are_retained()
        for extra in ("FR-0154", "AC-057", "ADR-0029", "NFR-9999"):
            with self.subTest(unapproved_identifier=extra):
                self.contract.documents = {**approved, "prd.md": approved["prd.md"] + "\n" + extra}
                with self.assertRaises(AssertionError):
                    self.contract.test_original_identifiers_and_section_headings_are_retained()
        for name in approved:
            for replacement in ("## Unnamed development candidate", marker + "\n\n" + marker):
                with self.subTest(document=name, development_boundary=replacement):
                    self.contract.documents = {
                        **approved,
                        name: approved[name].replace(marker, replacement, 1),
                    }
                    with self.assertRaises(AssertionError):
                        self.contract.test_original_identifiers_and_section_headings_are_retained()

    def assert_mutation_rejected(
        self, document: str, original: str, replacement: str, check: str
    ) -> None:
        verify = getattr(self.contract, check)
        verify()  # A rejection must not be caused by an unrelated existing failure.
        text = self.contract.documents[document]
        # Current prose may be rewrapped without changing the asserted evidence.
        match = re.search(r"\s+".join(re.escape(word) for word in original.split()), text)
        self.assertIsNotNone(match, f"mutation target missing: {original}")
        self.assertNotEqual(original, replacement)
        try:
            self.contract.documents[document] = (
                text[:match.start()] + replacement + text[match.end():]
            )
            with self.assertRaises(AssertionError):
                verify()
        finally:
            self.contract.documents[document] = text

    def test_metadata_accepts_real_revision_dates(self) -> None:
        documents = dict(self.contract.documents)
        for value in ("2026-11-10", "2028-02-29", "2027-01-01"):
            with self.subTest(date=value):
                self.contract.documents = {
                    name: re.sub(r"(?m)^\| Date \| .+ \|$", f"| Date | {value} |", text)
                    for name, text in documents.items()
                }
                self.contract.test_one_actual_h1_and_truthful_document_metadata()

    def test_metadata_rejects_invalid_iso_calendar_dates(self) -> None:
        original = re.search(
            r"(?m)^\| Date \| .+ \|$", self.contract.documents["prd.md"]
        ).group()
        for value in (
            "2026-02-29", "2026-11-31", "2026-13-01", "0000-01-01",
            "2026-1-01", "20261110", "2026-W46-2", "2026-11-10T00:00:00",
        ):
            with self.subTest(date=value):
                self.assert_mutation_rejected(
                    "prd.md", original, f"| Date | {value} |",
                    "test_one_actual_h1_and_truthful_document_metadata",
                )

    def test_original_sections_still_reject_result_and_prose_mutations(self) -> None:
        for document, original, replacement in (
            ("prd.md", "all 34 checks | Passed |", "all 34 checks | Failed |"),
            ("prd.md", "Current Edge and Chrome;", "Only a legacy browser;"),
            (
                "solution-design.md",
                "Passed; one expected warning (builder metadata)",
                "Failed; no warnings",
            ),
            ("solution-design.md", "print rules that hide navigation", "no print rules"),
            (
                "solution-design.md", "Behavioural tests to run before",
                "Behavioural tests NOT to run before",
            ),
            ("solution-design.md", "**Agent identity.** When", "**Agent identity.** Never"),
        ):
            with self.subTest(document=document, mutation=original):
                self.assert_mutation_rejected(
                    document, original, replacement,
                    "test_substantive_original_section_content_is_unchanged",
                )

    def test_original_patch_and_provenance_still_reject_mutations(self) -> None:
        for original, replacement in (
            ("This is an unreleased correction", "This is a released correction"),
            ("| Date | 9 November 2026 |", "| Date | 10 November 2026 |"),
        ):
            with self.subTest(mutation=original):
                self.assert_mutation_rejected(
                    "prd.md", original, replacement,
                    "test_original_product_context_unreleased_note_and_inventory_are_retained",
                )
        inventory = self.contract.documents["solution-design.md"].split(
            "## Appendix — File inventory (1.6.0)", 1
        )[1]
        original = next(line for line in inventory.splitlines() if line.startswith("| `"))
        self.assert_mutation_rejected(
            "solution-design.md", original, original.replace("| `", "| `invented/", 1),
            "test_original_product_context_unreleased_note_and_inventory_are_retained",
        )

    def test_identifiers_and_anchors_still_reject_mutations(self) -> None:
        self.assert_mutation_rejected(
            "prd.md", "| NFR-0013 |", "| NFR-9999 |",
            "test_original_identifiers_and_section_headings_are_retained",
        )
        self.assert_mutation_rejected(
            "prd.md", "(solution-design.md#b9-quality-and-testing)",
            "(solution-design.md#b9-invented-anchor)",
            "test_companion_references_resolve_to_the_correct_document",
        )

    def test_missing_or_duplicate_delta_boundaries_are_rejected(self) -> None:
        for document, marker in (
            ("prd.md", "| NFR-0012 |"),
            ("solution-design.md", "**Unreleased 1.6.1 accessibility implementation (#7).**"),
            ("solution-design.md", "**Agent identity.**"),
            ("solution-design.md", "### Development accessibility evidence ("),
            (
                "solution-design.md", "Behavioural tests to run before organisation-wide release "
                "(isolated skill-validator runs):",
            ),
        ):
            for replacement in ("", marker + "\n\n" + marker):
                with self.subTest(document=document, marker=marker, replacement=replacement):
                    self.assert_mutation_rejected(
                        document, marker, replacement,
                        "test_substantive_original_section_content_is_unchanged",
                    )
        marker = "### Measured accessibility delivery ("
        for replacement in ("", marker + "\n\n" + marker):
            with self.subTest(patch_boundary=replacement):
                self.assert_mutation_rejected(
                    "prd.md", marker, replacement,
                    "test_original_product_context_unreleased_note_and_inventory_are_retained",
                )

    def test_current_delta_cannot_silence_targets_or_failed_evidence(self) -> None:
        for document, original, replacement in (
            ("prd.md", "not certified conformance", "certified conformance"),
            ("prd.md", "Tab/Shift+Tab containment", "no keyboard containment"),
            ("prd.md", "reflow at 320 CSS pixels", "reflow at 1280 CSS pixels"),
            ("prd.md", "Catalogue AA must pass the unchanged browser checks",
             "Catalogue AA checks may be skipped"),
            ("prd.md", "Later wave\n4.40:1", "Later wave\n4.50:1"),
            ("prd.md", "Finance header 4.33:1", "Finance header 4.50:1"),
            ("prd.md", "Full L2 remains\nred", "Full L2 remains\ngreen"),
            ("prd.md", "A4/A5 acceptance is incomplete", "A4/A5 acceptance is complete"),
            ("prd.md", "no gate waiver is approved", "a gate waiver is approved"),
            ("solution-design.md", "Later wave 4.40:1", "Later wave 4.50:1"),
            ("solution-design.md", "Finance header 4.33:1", "Finance header 4.50:1"),
            ("solution-design.md", "Full L2 is blocking", "Full L2 is passing"),
            ("solution-design.md", "41 passed\nand 2 failed tests", "43 passed\nand 0 failed tests"),
            ("solution-design.md", "voice checks are pending", "voice checks are complete"),
        ):
            with self.subTest(document=document, mutation=original):
                self.assert_mutation_rejected(
                    document, original, replacement, "test_current_accessibility_delta_is_truthful"
                )

    def test_current_additions_can_evolve_without_changing_original_hashes(self) -> None:
        documents = dict(self.contract.documents)
        for document, marker, addition in (
            (
                "prd.md", "Catalogue AA must pass the unchanged browser checks;",
                "Catalogue AA must pass the unchanged browser checks; further manual evidence is pending;",
            ),
            ("prd.md", "## Part A —", "Further development evidence is pending.\n\n## Part A —"),
            (
                "solution-design.md", "**Agent identity.**",
                "Further implementation review is pending.\n\n**Agent identity.**",
            ),
            (
                "solution-design.md", "Behavioural tests to run before",
                "Further development evidence is pending.\n\nBehavioural tests to run before",
            ),
        ):
            with self.subTest(document=document, addition=addition):
                self.contract.documents = dict(documents)
                self.assertIn(marker, documents[document])
                self.contract.documents[document] = documents[document].replace(marker, addition, 1)
                self.contract.test_substantive_original_section_content_is_unchanged()
                self.contract.test_original_product_context_unreleased_note_and_inventory_are_retained()
                self.contract.test_current_accessibility_delta_is_truthful()


class IssueWorkPackage(unittest.TestCase):
    def test_existing_forms_collect_real_governing_links(self) -> None:
        baseline = {
            "feature.yml": (
                {"problem", "area", "acceptance", "source", "neutral"},
                {"problem", "area", "acceptance"},
                ["type:feature"],
            ),
            "bug.yml": (
                {"version", "what", "steps", "logs", "neutral"},
                {"version", "what", "steps"},
                ["type:bug"],
            ),
            "decision.yml": (
                {"question", "options", "recommendation", "owner", "due"},
                {"question", "options", "owner"},
                ["type:decision", "human-only"],
            ),
        }
        for name, (existing, mandatory, labels) in baseline.items():
            with self.subTest(form=name):
                path = ROOT / ".github" / "ISSUE_TEMPLATE" / name
                form = yaml.safe_load(path.read_text(encoding="utf-8"))
                entries = [field for field in form["body"] if "id" in field]
                fields = {field["id"]: field for field in entries}
                self.assertEqual(len(fields), len(entries), "duplicate field id")
                self.assertTrue(existing.issubset(fields))
                self.assertEqual(form["labels"], labels)
                self.assertEqual(
                    {
                        key for key in existing
                        if fields[key].get("validations", {}).get("required") is True
                    },
                    mandatory,
                )
                if "neutral" in fields:
                    options = fields["neutral"]["attributes"]["options"]
                    self.assertEqual(options, [{
                        "label": "This issue names no real customer, person or engagement detail.",
                        "required": True,
                    }])
                if name == "feature.yml":
                    self.assertIn(
                        "Use the fictitious Caldova Industrial AG in examples; never a real customer.",
                        form["body"][0]["attributes"]["value"],
                    )
                if name == "bug.yml":
                    self.assertIn("Caldova", fields["steps"]["attributes"]["label"])
                    self.assertEqual(
                        fields["logs"]["attributes"]["description"],
                        "Remove customer content before you paste.",
                    )
                self.assertIn("work-package", fields)
                package = fields["work-package"]
                self.assertEqual(package["type"], "textarea")
                self.assertIs(package["validations"]["required"], True)
                description = package["attributes"]["description"]
                for stage in ("real issue", "idea", "approved spec", "approved plan", "sprint"):
                    self.assertIn(stage, description.lower())
                self.assertRegex(description, r"(?i)draft.*unapproved")
                self.assertRegex(description, r"(?i)readiness requires all real.*links")

    def test_pr_template_keeps_its_sections_and_adds_work_package(self) -> None:
        text = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
        original = """## Summary (written by a person, in your own words)

<!-- What changes for the users of the plugin or for the engineers, and why. -->

Closes #

## How it was built

- [ ] Spec and plan: `docs/plans/...` (or: small change agreed in the issue)
- [ ] Tests written first; new behaviour covered (unit, self-test, DOM, browser)
- [ ] Agent involvement disclosed: <!-- none / Copilot agent mode / Copilot CLI / Copilot cloud agent; Superpowers skills used -->

## Gates

- [ ] `python tools/dev.py check` ends with ALL GATES PASSED (paste the summary below)
- [ ] Renderer changes: `python tools/dev.py site e2e` and screenshots attached
- [ ] Generated files regenerated, not hand-edited (template, `plugin-install.json`)

```
<gate summary>
```

## Rules

- [ ] Customer-neutral (Caldova only); no secrets
- [ ] Plugin changed after a release: version bumped (`python tools/dev.py bump X.Y.Z`) and CHANGELOG updated
- [ ] SKILL.md, references, PRD or ADR updated where behaviour or design changed
- [ ] Microsoft product icons used within their terms; notices updated

## Release pull requests only

- [ ] Cowork skill validators run in Copilot Cowork (structure, score, conflicts, security, package)
- [ ] Behavioural prompts of PRD B.9 route to the expected skills
- [ ] Install from the built package tested in a Cowork chat
"""
        expected = original.replace(
            "- [ ] Spec and plan: `docs/plans/...` (or: small change agreed in the issue)\n",
            "- [ ] Spec and plan: `docs/specs/...` and `docs/plans/...` (or: small change agreed in the issue)\n"
            "- [ ] Linked work package: real issue, idea, approved spec, approved plan and sprint records are linked in this PR\n",
        )
        self.assertEqual(text, expected)
