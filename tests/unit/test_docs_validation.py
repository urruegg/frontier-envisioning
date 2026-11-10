# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Offline documentation-contract tests; fixtures live only in temporary folders."""
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.unit._util import ROOT, load

ISSUE = "https://github.com/urruegg/frontier-envisioning/issues/10"


def header(references: str = f"[Issue]({ISSUE})") -> str:
    return (
        "# Test\n\n| Field | Value |\n|---|---|\n"
        "| Version | 0.1 |\n| Date | 2026-11-09 |\n| Author | Maintainers |\n"
        "| Status | Proposed |\n| Scope | Test |\n"
        f"| References | {references} |\n"
    )


def put(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def package(root: Path) -> tuple[Path, str]:
    """A local, proposed work package; no inference of live approval."""
    for folder in ("idea", "spec", "plan", "sprint"):
        put(root, f"docs/{folder}/README.md", header())
    for folder in ("idea", "spec", "plan"):
        put(root, f"docs/{folder}/x.md", header())
        put(root, f"docs/{folder}/README.md", header() + "\n[Child](x.md)\n")
    governing = (
        f"[Issue]({ISSUE}), [Idea](../idea/x.md), "
        "[Spec](../spec/x.md), [Plan](../plan/x.md)"
    )
    text = header(governing) + (
        "\n| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |\n"
        "|---|---|---|---|---|---|---|---|\n"
        f"| [#10]({ISSUE}) | [Idea](../idea/x.md) | [Spec](../spec/x.md) "
        "| [Plan](../plan/x.md) | Maintainer | None | Proposed | Not implemented |\n"
    )
    path = put(root, "docs/sprint/S-001.md", text)
    put(root, "docs/sprint/README.md", header() + "\n[Sprint](S-001.md)\n")
    return path, text


class CheckerPresence(unittest.TestCase):
    def test_documentation_checker_exists(self):
        self.assertTrue((ROOT / "tools/check_docs.py").is_file(), "D4 documentation checker missing")


class DocumentationValidation(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / "tools/check_docs.py").is_file(), "D4 documentation checker missing")
        self.docs = load("tools/check_docs.py")

    def test_metadata_requires_exact_fields_and_real_date(self):
        self.assertEqual(self.docs.metadata_errors(header()), [])
        for invalid in (
            header().replace("2026-11-09", "2026-02-30"),
            header().replace("| Scope | Test |\n", ""),
            "# Missing metadata\n",
            header() + "| Extra | Invalid |\n",
            header().replace("| Author | Maintainers |", "| Author |  |"),
            header().replace("0.1", "release-next"),
            header().replace("|---|---|", "|--|not a separator|"),
        ):
            with self.subTest(invalid=invalid):
                self.assertTrue(self.docs.metadata_errors(invalid))

    def test_fences_duplicates_and_explicit_anchors(self):
        text = "# Title\n## Repeated\n## Repeated\n<a id=\"legacy\"></a>\n```md\n# Not a heading\n```\n"
        self.assertTrue({"title", "repeated", "repeated-1", "legacy"}.issubset(self.docs.anchors(text)))
        self.assertNotIn("not-a-heading", self.docs.anchors(text))
        self.assertEqual(self.docs.metadata_errors(header() + "\n~~~md\n# Sample\n~~~\n"), [])
        self.assertTrue(self.docs.metadata_errors(header() + "\n# Second H1\n"))

    def test_links_cover_parentheses_and_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.md"
            put(root, "target (sample).md", "# Destination\n")
            for text in ("[OK](<target (sample).md#destination>)", "[OK](target (sample).md#destination)"):
                self.assertEqual(self.docs.link_errors(root, source, text), [])
            for text, diagnostic in (
                ("[Bad](missing.md)", "local link missing"),
                ("[Bad](<target (sample).md#absent>)", "local anchor missing"),
                ("[Bad](../../outside.md)", "escapes repository"),
                ("[Broken](unfinished", "unclosed inline Markdown link"),
            ):
                with self.subTest(text=text):
                    self.assertIn(diagnostic, "\n".join(self.docs.link_errors(root, source, text)))

    def test_unmatched_prose_bracket_does_not_hide_later_invalid_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package(root)
            put(root, "docs/recovery.md", header() + (
                "\nUnmatched [prose\n\n[Bad](missing.md)\n[Escape](../../outside.md)\n"
            ))
            errors = self.docs.check_documents(root, list(root.rglob("*.md")))
            self.assertIn("docs/recovery.md: local link missing: missing.md", errors)
            self.assertIn("docs/recovery.md: local link escapes repository: ../../outside.md", errors)

    def test_deeply_nested_labels_do_not_crash_document_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package(root)
            nested = "[" * 1200 + "x" + "]" * 1200
            put(root, "docs/nested.md", header() + "\n" + nested + "\n")
            self.assertEqual(self.docs.check_documents(root, list(root.rglob("*.md"))), [])
            put(root, "docs/nested.md", header() + "\n## " + nested + "\n[Section](#x)\n")
            self.assertEqual(self.docs.check_documents(root, list(root.rglob("*.md"))), [])

    def test_deeply_nested_labels_still_validate_inner_and_following_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package(root)
            nested = "[" * 1200 + "[Bad](missing.md)" + "]" * 1200
            put(root, "docs/nested.md", header() + "\n" + nested + "\n[Escape](../../outside.md)\n")
            self.assertEqual(self.docs.check_documents(root, list(root.rglob("*.md"))), [
                "docs/nested.md: local link escapes repository: ../../outside.md",
                "docs/nested.md: local link missing: missing.md",
            ])

    def test_eligibility_excludes_historical_and_product_contracts(self):
        for path in ("docs/spec/new.md", "docs/engineering/guide.md", ".github/agent-policy/review.md",
                     "README.md", "CONTRIBUTING.md", "SECURITY.md", "backlog/README.md", "infra/README.md",
                     "site/README.md", "src/renderer/README.md", "tests/README.md"):
            self.assertTrue(self.docs.eligible(Path(path)), path)
        for path in ("plugin/README.md", "docs/intake/receipt.md", "docs/plans/old.md", "releases/README.md",
                     ".agents/skills/x/SKILL.md", "backlog/issues/INT-01.md", ".github/PULL_REQUEST_TEMPLATE.md",
                     ".github/agents/docs-agent.agent.md", "CHANGELOG.md", "AGENTS.md", "docs/spec/input.json"):
            self.assertFalse(self.docs.eligible(Path(path)), path)

    def test_reference_links_percent_encoding_and_non_markdown_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.md"
            put(root, "a b.md", "# Destination\n")
            put(root, "sample.json", "{}")
            text = "[Label][REF]\n[ref]: <a%20b.md#destination>\n[Data](sample.json)\n"
            self.assertEqual(self.docs.link_errors(root, source, text), [])
            self.assertIn("undefined Markdown reference", "\n".join(self.docs.link_errors(root, source, "[Missing][absent]")))
            self.assertIn("unsupported local target", "\n".join(self.docs.link_errors(root, source, "[Bad](sample.json#unsupported)")))

    def test_sprint_links_rows_and_catalogues_are_real_local_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, text = package(root)
            self.assertEqual(self.docs.sprint_errors(root, path, text), [])
            self.assertTrue(self.docs.sprint_errors(root, path, text.replace("[Plan](../plan/x.md)", "Missing")))
            self.assertTrue(self.docs.sprint_errors(root, path, text.replace("| Maintainer |", "||")))
            self.assertEqual(self.docs.check_documents(root, list(root.rglob("*.md"))), [])
            put(root, "docs/sprint/README.md", header())
            self.assertIn("uncatalogued child S-001.md", "\n".join(self.docs.check_documents(root, list(root.rglob("*.md")))))

    def test_sprint_metadata_and_rows_share_whole_document_reference_definitions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, text = package(root)
            definitions = {"issue": ISSUE, "idea": "../idea/x.md", "spec": "../spec/x.md", "plan": "../plan/x.md"}
            for kind, target in definitions.items():
                label = kind.title()
                text = text.replace(f"[{label}]({target})", f"[{label}][{kind}]")
            text = text.replace(f"[#10]({ISSUE})", "[#10][ISSUE]")
            text += "\n" + "\n".join(f"[{key}]: {value}" for key, value in definitions.items()) + "\n"
            put(root, "docs/sprint/S-001.md", text)
            self.assertEqual(self.docs.link_errors(root, path, text), [])
            self.assertEqual(self.docs.sprint_errors(root, path, text), [])
            self.assertEqual(self.docs.check_documents(root, list(root.rglob("*.md"))), [])
            for invalid in (
                text.replace("[Plan][plan]", "Missing", 1),
                text.replace("| [Plan][plan] | Maintainer", "| Missing | Maintainer"),
            ):
                with self.subTest(invalid=invalid):
                    self.assertTrue(self.docs.sprint_errors(root, path, invalid))

    def test_malformed_angle_target_has_an_explicit_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = self.docs.link_errors(Path(tmp), Path(tmp) / "source.md", "[Bad](<missing.md)")
            self.assertIn("unclosed angle-bracket", "\n".join(errors))

    def test_all_four_canonical_catalogues_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = self.docs.check_documents(Path(tmp), [])
            self.assertEqual(len(errors), 4)
            self.assertTrue(all("directory missing" in error for error in errors))

    def test_metadata_preserves_yaml_and_truthful_status_but_rejects_misplacement(self):
        text = "---\nname: example\nsample: '# Not an H1'\n---\n" + header()
        self.assertEqual(self.docs.metadata_errors(text), [])
        self.assertEqual(self.docs.metadata_errors(header().replace("Proposed", "Historical; not approved")), [])
        for invalid in (
            header().replace("# Test", "# Test\n\nUnrelated introduction"),
            header().replace("| Scope | Test |", "| Date | 2026-11-09 |"),
            header().replace("2026-11-09", "20261109"),
            header().replace("| References |", "| References | extra |"),
            header().replace("| Field | Value |", "| Field | Other |"),
            header() + "\n| Field | Value |\n|---|---|\n| Version | 1.0 |\n",
        ):
            with self.subTest(invalid=invalid):
                self.assertTrue(self.docs.metadata_errors(invalid))

    def test_metadata_allows_an_ordinary_field_value_table_in_the_body(self):
        body = (
            "\n## Product context\n\n| Field | Value |\n|---|---|\n"
            "| Product | Sample |\n| Version | 1.6.1 development patch |\n"
            "| Date | 9 November 2026 |\n| Owner | Maintainer |\n"
        )
        self.assertEqual(self.docs.metadata_errors(header() + body), [])

    def test_empty_atx_h1_is_still_a_second_actual_heading(self):
        self.assertTrue(self.docs.metadata_errors(header() + "\n#\n"))

    def test_actual_headings_include_setext_and_indented_atx_not_inline_code(self):
        self.assertEqual(self.docs.metadata_errors(header().replace("# Test", "Test\n====")), [])
        self.assertTrue(self.docs.metadata_errors(header() + "\nAnother title\n====\n"))
        text = "  ## **A** [link](https://example.test) `code` & stuff! ##\n## café_é\n"
        self.assertTrue({"a-link-code--stuff", "café_é"}.issubset(self.docs.anchors(text)))
        self.assertEqual(self.docs.anchors("## X\n## X-1\n## X\n<a id='old'></a>\n"),
                         {"x", "x-1", "x-2", "old"})

    def test_fence_lengths_and_inline_code_examples_do_not_create_links(self):
        text = (
            "````md\n# Sample\n```\n[Ignored](absent.md)\n````\n"
            "~~~md\n[Ignored][undefined]\n~~~\n"
            "`[inline](absent.md)` and ``[inline ` excerpt](absent.md)``\n"
        )
        self.assertNotIn("Sample", self.docs.prose(text))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(self.docs.link_errors(root, root / "source.md", text), [])

    def test_repo_root_query_fragments_html_and_directory_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "docs/source.md"
            put(root, "docs/target.md", "# Destination\n")
            put(root, "page.html", "<h2 id='local'>Here</h2>")
            valid = (
                "[Root](/docs/target.md?view=1#destination)\n[Dir](/docs/)\n"
                "[HTML](/page.html#local)\n[Outside](https://example.test/a?x=(1)#fragment)"
            )
            self.assertEqual(self.docs.link_errors(root, source, valid), [])
            self.assertIn("directory fragment", "\n".join(self.docs.link_errors(root, source, "[Bad](/docs/#destination)")))
            self.assertIn("escapes repository", "\n".join(self.docs.link_errors(root, source, "[Bad](/%2e%2e/out.md)")))

    def test_reference_labels_collapse_whitespace_and_support_collapsed_and_shortcut(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root, "a b.md", "# Destination\n")
            text = '[Label][A   B]\n[a b][]\n[A B]\n[a b]: <a%20b.md#destination> "A title"\n'
            self.assertEqual(self.docs.link_errors(root, root / "source.md", text), [])
            self.assertEqual(self.docs.link_errors(root, root / "source.md", "[ ] Task\n[ordinary prose]\n"), [])

    def test_images_and_nested_alt_do_not_create_spurious_reference_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root, "icon.svg", "<svg/>")
            put(root, "guide.md", "# Guide\n")
            text = "[![alt [example][not-a-ref] `code`](icon.svg)](guide.md)\n"
            self.assertEqual(self.docs.link_errors(root, root / "source.md", text), [])
            self.assertIn("local link missing", "\n".join(self.docs.link_errors(root, root / "source.md", "![alt](absent.svg)")))

    def test_escaped_parentheses_and_optional_titles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root, "a(b).md", "# Destination\n")
            for text in ('[A](a\\(b\\).md "Title")', "[A](<a(b).md> 'Title')", "[A](a(b).md#destination)"):
                with self.subTest(text=text):
                    self.assertEqual(self.docs.link_errors(root, root / "source.md", text), [])

    def test_angle_whitespace_and_title_parentheses_do_not_change_destinations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root, "a(b).md", "# Destination\n")
            for text in ('[A](  <a(b).md> "Title ) ( text"  )', "[A](a(b).md 'Title )')"):
                with self.subTest(text=text):
                    self.assertEqual(self.docs.link_errors(root, root / "source.md", text), [])

    def test_anchor_link_labels_do_not_include_balanced_destinations_or_reference_ids(self):
        text = "## A [link](a(b).md)\n## A [label][ref]\n\n[ref]: a.md\n"
        self.assertEqual(self.docs.anchors(text), {"a-link", "a-label"})

    def test_invalid_http_shapes_are_reported_without_reachability_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for text in ("[Bad](https://)", "[Bad](http:relative)"):
                with self.subTest(text=text):
                    self.assertIn("malformed URL", "\n".join(self.docs.link_errors(root, root / "source.md", text)))

    def test_reference_destinations_reject_empty_and_unbalanced_bare_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root, "bad(.md", "# Present\n")
            source = put(root, "source.md", "# Source\n")
            for text, expected in (
                ("[Ref][ref]\n[ref]: bad(.md\n", "unbalanced parentheses"),
                ("[Ref][ref]\n[ref]:\n", "empty Markdown reference destination"),
            ):
                with self.subTest(text=text):
                    self.assertIn(expected, "\n".join(self.docs.link_errors(root, source, text)))
            self.assertEqual(self.docs.link_errors(root, source, "[Ref][ref]\n[ref]: <bad(.md>\n"), [])

    def test_encoded_drive_paths_are_non_portable_even_before_existence_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = self.docs.link_errors(root, root / "source.md", "[Bad](C%3A/not-portable.md)")
            self.assertIn("invalid local path", "\n".join(errors))

    def test_data_id_is_not_an_explicit_anchor(self):
        text = '<a data-id="not-an-id"></a>\n<a id="real"></a>\n'
        self.assertEqual(self.docs.anchors(text), {"real"})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            put(root, "page.html", '<h2 data-id="not-an-id">Text</h2>')
            errors = self.docs.link_errors(root, root / "source.md", "[Bad](page.html#not-an-id)")
            self.assertIn("local anchor missing", "\n".join(errors))

    def test_bad_urls_and_destinations_are_diagnostics_not_exceptions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for text, expected in (
                ("[Bad](file:///tmp/x.md)", "unsupported non-portable link scheme"),
                ("[Bad](https://[broken)", "malformed URL"),
                ("[Bad](bad%ZZ.md)", "malformed percent encoding"),
                ("[Bad](bad%FF.md)", "invalid UTF-8"),
                ("[Bad](bad%00.md)", "invalid local path"),
                ("[Bad](<missing.md> junk)", "malformed angle-bracket"),
                ('[Bad](missing.md "unfinished)', "malformed link title"),
                ("[Bad][unclosed", "unclosed Markdown reference"),
            ):
                with self.subTest(text=text):
                    self.assertIn(expected, "\n".join(self.docs.link_errors(root, root / "source.md", text)))

    def test_sprint_references_are_the_metadata_row_not_incidental_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, text = package(root)
            governing = text.split("| References | ", 1)[1].split(" |\n", 1)[0]
            invalid = text.replace(governing, f"[Issue]({ISSUE})", 1)
            self.assertIn("sprint References", "\n".join(self.docs.sprint_errors(root, path, invalid)))
            yaml = "---\n" + "\n".join(f"key{i}: value" for i in range(20)) + "\n---\n"
            self.assertEqual(self.docs.sprint_errors(root, path, yaml + text), [])

    def test_sprint_requires_each_column_link_and_well_formed_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, text = package(root)
            for invalid in (
                text.replace("|---|---|---|---|---|---|---|---|", "|bad|---|---|---|---|---|---|---|"),
                text.rsplit("\n| [#10]", 1)[0] + "\n",
                text.replace("| Maintainer | None | Proposed |", "| Maintainer |"),
                text.replace("| Maintainer | None | Proposed |", "| Maintainer | None ||"),
                text.replace("| [Plan](../plan/x.md) | Maintainer", "| Missing | Maintainer"),
                text.replace("| [Spec](../spec/x.md) | [Plan](../plan/x.md)", "| [Plan](../plan/x.md) | [Spec](../spec/x.md)"),
                text.replace(ISSUE, "https://github.com/elsewhere/project/issues/10"),
                text.replace(ISSUE, "https://github.com/urruegg/frontier-envisioning/issues/not-an-id"),
            ):
                with self.subTest(invalid=invalid):
                    self.assertTrue(self.docs.sprint_errors(root, path, invalid))
            self.assertEqual(self.docs.sprint_errors(root, path, text.replace(ISSUE, ISSUE + "?view=1#issuecomment-1")), [])

    def test_sprint_validates_evidence_and_body_links_as_well_as_governing_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, text = package(root)
            invalid = text.replace("Not implemented", "[Missing evidence](absent.txt)") + "\n[Bad](<missing.md)\n"
            errors = self.docs.sprint_errors(root, path, invalid)
            self.assertIn("local link missing: absent.txt", errors)
            self.assertIn("unclosed angle-bracket link target", errors)

    def test_broken_sprint_and_catalogue_targets_share_parser_diagnostics(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, text = package(root)
            (root / "docs/plan/x.md").unlink()
            self.assertIn("local link missing", "\n".join(self.docs.sprint_errors(root, path, text)))
            for relative in ("docs/idea/README.md", "docs/sprint/S-001.md"):
                put(root, relative, header() + "\n[Bad](<missing.md)\n")
            errors = self.docs.check_documents(root, list(root.rglob("*.md")))
            for relative in ("docs/idea/README.md", "docs/sprint/S-001.md"):
                self.assertTrue(any(error.startswith(relative + ":") and "unclosed angle-bracket" in error for error in errors))
            self.assertIn("local link missing: x.md", "\n".join(errors))

    def test_catalogue_lists_only_actual_direct_children_and_checks_links_without_input_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package(root)
            put(root, "docs/idea/sub/extra.md", header())
            put(root, "docs/idea/README.md", header() + "\n[Wrong](sub/extra.md)\n[Bad](missing.md)\n")
            errors = self.docs.check_documents(root, [])
            self.assertIn("docs/idea: uncatalogued child x.md", errors)
            self.assertTrue(any("local link missing: missing.md" in error for error in errors))
            self.assertFalse(any("uncatalogued child extra.md" in error for error in errors))

    def test_check_documents_is_deterministic_reports_utf8_and_rejects_outside_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package(root)
            bad = put(root, "docs/bad.md", "")
            bad.write_bytes(b"\xff")
            paths = [root / "docs/missing.md", bad, root.parent / "outside.md"]
            errors = self.docs.check_documents(root, paths)
            self.assertEqual(errors, self.docs.check_documents(root, list(reversed(paths))))
            self.assertTrue(any("docs/bad.md: cannot read UTF-8" in error for error in errors))
            self.assertTrue(any("docs/missing.md: cannot read UTF-8" in error for error in errors))
            self.assertTrue(any("outside repository" in error for error in errors))

    def test_cli_reports_explicit_docs_paths_real_count_and_no_live_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package(root)
            with mock.patch.object(self.docs, "ROOT", root), \
                    mock.patch.object(self.docs, "tracked_files", side_effect=lambda: sorted(root.rglob("*.md"))):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.docs.main(["--strict"]), 0)
                self.assertIn("documentation check: 0 errors", output.getvalue())
                self.assertIn("external issue existence/approval not verified", output.getvalue())
                put(root, "docs/broken.md", "# No metadata\n\n[Bad](absent.md)")
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(self.docs.main([]), 1)
                self.assertIn("DOCS docs/broken.md:", output.getvalue())
                self.assertIn("documentation check: 2 errors", output.getvalue())


class DocumentationRunner(unittest.TestCase):
    def test_docs_command_fails_on_contract_error(self):
        dev = load("tools/dev.py")
        with mock.patch.dict(dev.os.environ, {"CI": ""}), mock.patch.object(dev, "tool", return_value=1) as tool, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dev.main(["docs"]), 1)
        tool.assert_called_once_with("check_docs", [])
        self.assertEqual(dev.RESULTS[0][0], "documentation metadata, links and traceability")

    def test_docs_command_succeeds_when_checker_passes(self):
        dev = load("tools/dev.py")
        with mock.patch.object(dev, "tool", return_value=0) as tool, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dev.main(["docs", "--strict"]), 0)
        tool.assert_called_once_with("check_docs", ["--strict"])

    def test_aggregate_gates_call_docs_immediately_after_lint(self):
        for command in ("precommit", "check"):
            with self.subTest(command=command):
                dev = load("tools/dev.py")
                names = ("cmd_template_check", "cmd_lint", "cmd_docs", "cmd_scan", "cmd_test", "cmd_selftest",
                         "cmd_package", "cmd_demo", "cmd_verify_release", "cmd_dom")
                calls = []
                steps = {name: mock.Mock(side_effect=lambda *a, name=name, **kw: calls.append(name)) for name in names}
                with mock.patch.multiple(dev, create=True, **steps), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(dev.main([command]), 0)
                self.assertEqual(calls[:3], ["cmd_template_check", "cmd_lint", "cmd_docs"])
                steps["cmd_docs"].assert_called_once_with()

    def test_aggregate_gates_stop_at_docs_failure(self):
        for command in ("precommit", "check"):
            with self.subTest(command=command):
                dev = load("tools/dev.py")
                before = ("cmd_template_check", "cmd_lint")
                after = ("cmd_scan", "cmd_test", "cmd_selftest", "cmd_package", "cmd_demo", "cmd_verify_release", "cmd_dom")
                steps = {name: mock.Mock() for name in (*before, *after)}
                with mock.patch.multiple(dev, **steps), mock.patch.object(dev, "tool", return_value=1), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(dev.main([command]), 1)
                for name in before:
                    steps[name].assert_called_once_with()
                for name in after:
                    steps[name].assert_not_called()

    def test_help_names_documentation_command(self):
        dev = load("tools/dev.py")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(dev.main(["--help"]), 0)
        self.assertIn("  docs ", output.getvalue())


if __name__ == "__main__":
    unittest.main()
