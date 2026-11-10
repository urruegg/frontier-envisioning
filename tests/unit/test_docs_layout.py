# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Plural documentation layout, retired paths and historical-record boundaries."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.unit._util import ROOT, load

docs = load("tools/check_docs.py", "docs_layout_checker")


def header() -> str:
    return (
        "# Record\n\n| Field | Value |\n|---|---|\n"
        "| Version | 0.1 |\n| Date | 2026-11-10 |\n| Author | Maintainer |\n"
        "| Status | Proposed |\n| Scope | Layout test |\n"
        "| References | [Issue](https://github.com/urruegg/frontier-envisioning/issues/18) |\n"
    )


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def catalogues(root: Path) -> None:
    for folder in ("ideas", "specs", "plans", "sprints"):
        write(root, f"docs/{folder}/README.md", header())


class PluralDocumentationLayout(unittest.TestCase):
    def test_only_plural_folders_are_canonical(self):
        self.assertEqual(docs.FOLDERS, ("ideas", "specs", "plans", "sprints"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalogues(root)
            self.assertEqual(docs.check_documents(root, list(root.rglob("*.md"))), [])

    def test_active_plans_require_metadata_instead_of_blanket_legacy_exemption(self):
        self.assertTrue(docs.eligible(Path("docs/plans/current-plan.md")))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalogues(root)
            path = write(root, "docs/plans/current-plan.md", "# Missing metadata\n")
            write(root, "docs/plans/README.md", header() + "\n[Plan](current-plan.md)\n")
            errors = docs.check_documents(root, [path])
            self.assertIn("docs/plans/current-plan.md: six-field metadata must follow the H1", errors)

    def test_historical_records_keep_format_but_not_broken_links(self):
        relative = "docs/specs/2026-11-09-workflow-legend-design.md"
        self.assertFalse(docs.eligible(Path(relative)))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalogues(root)
            path = write(root, relative, "# Historical design\n\n[Missing](absent.md)\n")
            write(root, "docs/specs/README.md", header() + "\n[Design](2026-11-09-workflow-legend-design.md)\n")
            errors = docs.check_documents(root, [path])
            self.assertIn(f"{relative}: local link missing: absent.md", errors)
            self.assertFalse(any("metadata" in error for error in errors))

    def test_retired_singular_directory_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalogues(root)
            (root / "docs" / "plan").mkdir()
            self.assertIn("docs/plan: retired documentation directory exists",
                          docs.check_documents(root, list(root.rglob("*.md"))))

    def test_logical_work_kinds_resolve_plural_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            catalogues(root)
            for folder in ("ideas", "specs", "plans"):
                write(root, f"docs/{folder}/record.md", header())
            text = (
                "[Issue](https://github.com/urruegg/frontier-envisioning/issues/18) "
                "[Idea](../ideas/record.md) [Spec](../specs/record.md) [Plan](../plans/record.md)"
            )
            kinds, errors = docs.work_kinds(root, root / "docs" / "sprints" / "S-001.md", text)
            self.assertEqual(errors, [])
            self.assertEqual(kinds, {"issue", "idea", "spec", "plan"})

    def test_repository_has_no_retired_index_or_singular_directories(self):
        self.assertFalse((ROOT / "docs" / "prd-and-solution-design.md").exists())
        for folder in ("idea", "spec", "plan", "sprint"):
            self.assertFalse((ROOT / "docs" / folder).exists(), folder)
