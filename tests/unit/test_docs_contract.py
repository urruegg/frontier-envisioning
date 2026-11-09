"""Contract for the repository-owned documentation maintenance persona."""
from __future__ import annotations

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
