# Documentation Foundation Implementation Plan

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-11-09 |
| Author | Copilot SDK in VS Code; AI-assisted maintenance |
| Status | Plan and readiness approved by the user on [#6](https://github.com/urruegg/frontier-envisioning/issues/6); delivery evidence separate |
| Scope | DG-01, DG-02, DG-04 and DG-07; no protected or packaged-output edits |
| References | [Plan catalogue](README.md), [Issue](https://github.com/urruegg/frontier-envisioning/issues/10), [Idea](../idea/2026-11-09-docs-governance-and-accessibility.md), [Spec](../spec/2026-11-09-docs-governance-and-accessibility-design.md), [Sprint](../sprint/SPRINT-001-docs-governance-and-accessibility.md), [Master](2026-11-09-docs-governance-implementation.md) |

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `subagent-driven-development` after plan approval. A fresh worker owns one
> D-task; use checkbox steps and spec/correctness review before the next task.

**Goal:** Add a constrained docs agent, split the repository product documents,
and validate the linked documentation work package through existing tooling.

**Architecture:** Preserve content/identifiers and old-path compatibility;
keep metadata/links/sprint checks in one stdlib tool and the existing dev runner.
Only active owned documents are normalised; immutable and product contracts
remain unchanged.

**Tech Stack:** Markdown, Python 3.11+/unittest, existing GitHub/Copilot tools.

---

## File ownership map

| Surface | Owner in this plan |
|---|---|
| `.github/agents/docs-agent.agent.md` | D1 |
| `docs/prd.md`, `docs/solution-design.md`, legacy landing page | D2 |
| `tools/build_release.py` and bundle tests | D3 |
| `tools/check_docs.py`, `tools/dev.py`, documentation unit tests | D4 |
| Eligible owned headers, catalogues, issue-form link fields | D5 |
| Copilot/AGENTS/policy prose | Governance plan, not this writer |
| CODEOWNERS/hooks/settings/permissions | Human plan only |
| `plugin/`, historical release/intake/legacy plan content | No edits in this workstream |

Update current code targets against the base revision before applying snippets.
Do not replace an entire existing module when the plan shows an insertion.
For new document metadata use the real execution revision date, preserving
original authorship and explicitly disclosing AI assistance.

## Task D1: docs-agent contract and definition

**Create:** `.github/agents/docs-agent.agent.md`,
`tests/unit/test_docs_contract.py`.
**Read:** `.github/agents/frontier-planner.agent.md`, `tools/fe_lib.py`.

- [ ] Add this test class first:

```python
from pathlib import Path
import unittest
from tests.unit._util import ROOT, load

fe = load(str(Path("tools") / "fe_lib.py"))

class DocsAgentContract(unittest.TestCase):
    def test_definition_has_minimal_tools_and_boundaries(self):
        path = ROOT / ".github" / "agents" / "docs-agent.agent.md"
        self.assertTrue(path.is_file(), "docs-agent definition missing")
        text = path.read_text(encoding="utf-8")
        fm = fe.frontmatter(text)
        self.assertEqual(fm["name"], "docs-agent")
        self.assertEqual(fm["tools"], "[read, search, edit, todo]")
        self.assertNotIn("model", fm)
        for required in ("CODEOWNERS", "generated", "approval", "catalogue"):
            self.assertIn(required, text)
        self.assertNotIn("tools: [execute", text)
```

- [ ] Run `python -m pytest tests\unit\test_docs_contract.py -q`.
      Expected red: `docs-agent definition missing`, not a missing dependency.
- [ ] Create the complete definition below. The date is the authored example;
      update it to the real revision date if execution is later.

```markdown
---
name: docs-agent
description: "Maintain, review, relocate and catalogue Frontier Envisioning documentation; standardise eligible Markdown headers and references while preserving truthful status and source contracts."
tools: [read, search, edit, todo]
user-invocable: true
---
# Frontier documentation maintenance agent

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-11-09 |
| Author | Frontier Envisioning maintainers; AI-assisted definition |
| Status | Maintained definition; no approval or permission is implied |
| Scope | Approved repository-owned documentation tasks |
| References | [AGENTS](../../AGENTS.md), [Docs](../../docs/README.md) |

Maintain current, concise, correctly placed and cross-linked documentation.
Read AGENTS and the approved issue/spec/plan/sprint before editing.

1. Identify authoritative content, audience, owner and document status.
2. Change only the approved prose and catalogue paths.
3. Preserve required YAML frontmatter and product/version contracts.
4. Apply eligible six-field headers with real dates/authorship and status.
5. Update direct-child catalogues and backlinks in the same PR.
6. Request local header/link/traceability validation and report its result.
7. List changed documents, evidence, unresolved decisions and handoff.

Do not edit CODEOWNERS, hooks, licences, releases, vendored skills, generated
output, workflows, infrastructure, permissions or production code.
Do not blanket-change packaged Markdown or identity-template inputs.
Do not invent issues, approval, owners, dates, status, released capability
or completed validation. Author is not owner or approver.
Never change classification or distribute internal material independently.
Use the existing parent/CI dev loop for execution; this agent has no terminal,
administrative, merge, release or deployment authority.
```

- [ ] Run the D1 test and `python tools\dev.py lint --strict`.
      Expected green: contract passes and existing discovery/version rules pass.
- [ ] Commit only D1 paths:

```powershell
git add -- .github\agents\docs-agent.agent.md tests\unit\test_docs_contract.py
git commit -m "feat: add constrained documentation maintenance agent" -m "Refs #10." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Task D2: lossless product-document split and compatibility

**Create:** `docs/prd.md`, `docs/solution-design.md`,
`tests/fixtures/prd-design-identifiers.json`.
**Modify:** `docs/prd-and-solution-design.md`, `docs/README.md`,
`tests/unit/test_docs_contract.py`.

- [ ] Generate the identifier/heading fixture from the untouched combined
      document before splitting. This is generated test data, not a release
      record or a hand-edited golden hash:

```powershell
@'
import hashlib, json, re
from pathlib import Path
source = Path("docs") / "prd-and-solution-design.md"
data = source.read_bytes()
text = data.decode("utf-8")
fixture = {
    "source_sha256": hashlib.sha256(data).hexdigest(),
    "identifiers": sorted(set(re.findall(r"\b(?:FR|NFR|AC|D|TD|ADR)-\d+\b", text))),
    "sections": re.findall(r"(?m)^#{2,3} ([AB]\.\d[^\n]*)$", text),
}
target = Path("tests") / "fixtures" / "prd-design-identifiers.json"
target.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8", newline="\n")
'@ | python -
```

- [ ] Merge the `json`/`re` imports into the existing import block and add this
      test class below the D1 class:

```python
import json
import re

class ProductDocumentSplit(unittest.TestCase):
    def test_two_documents_preserve_ids_sections_and_legacy_links(self):
        paths = [ROOT / "docs" / "prd.md", ROOT / "docs" / "solution-design.md"]
        for path in paths:
            self.assertTrue(path.is_file(), f"missing {path.name}")
        texts = [p.read_text(encoding="utf-8") for p in paths]
        baseline = json.loads(
            (ROOT / "tests" / "fixtures" / "prd-design-identifiers.json")
            .read_text(encoding="utf-8")
        )
        joined = "\n".join(texts)
        ids = set(re.findall(r"\b(?:FR|NFR|AC|D|TD|ADR)-\d+\b", joined))
        self.assertTrue(set(baseline["identifiers"]).issubset(ids))
        for section in baseline["sections"]:
            self.assertIn(section, joined)
        for text in texts:
            self.assertEqual(len(re.findall(r"(?m)^# ", text)), 1)
        old = (ROOT / "docs" / "prd-and-solution-design.md").read_text(encoding="utf-8")
        for expected in ("prd.md", "solution-design.md",
                         'id="a12-release-plan"', 'id="b9-quality-and-testing"'):
            self.assertIn(expected, old)
        self.assertIn("solution-design.md", texts[0])
        self.assertIn("prd.md", texts[1])
```

- [ ] Run `python -m pytest tests\unit\test_docs_contract.py -q`.
      Expected red: the authoritative new files do not exist.
- [ ] Use `apply_patch` to perform this exact content mapping:

| Original content | Destination/change |
|---|---|
| Shared product/basis/licence/provenance | PRD product-context section; preserve source statements and owner attribution |
| 1.6.1 requirement note | PRD, clearly unreleased |
| Part A, A.1-A.13 and their subsection headings/tables | PRD; preserve headings/IDs and historical release results |
| Part B, B.1-B.14 and their subsections | Solution design; preserve headings/IDs and historical claims |
| Appendix file inventory | Solution design; demote its H1 to H2 and identify the 1.6.0 baseline |
| Cross-part B.9/source references | Real companion-document links, not bare references implying one file |
| Combined path | Short metadata-bearing landing page, companion links and explicit legacy anchor map |

Use one H1 and six-field header per authoritative document. Do not alter
requirements, pricing, release dates, approvals or plugin behaviour during the
split. Keep the current A/B section identifiers for link stability.

For each original section retain its GitHub anchor on the landing page, using
an HTML anchor and companion link, for example:

```markdown
<a id="a12-release-plan"></a>
[A.12 Release plan](prd.md#a12-release-plan)

<a id="b9-quality-and-testing"></a>
[B.9 Quality and testing](solution-design.md#b9-quality-and-testing)
```

Do not describe this as an automatic GitHub redirect. Update the root docs
catalogue to link both authoritative documents. Preserve legacy intake,
source inventories, earlier plans and immutable release records.

- [ ] Run the D2 tests. Review all original sections against the mapping, not
      only identifier counts; add any missing content before proceeding.
- [ ] Commit:

```powershell
git add -- docs\prd.md docs\solution-design.md docs\prd-and-solution-design.md docs\README.md tests\unit\test_docs_contract.py tests\fixtures\prd-design-identifiers.json
git commit -m "docs: separate product requirements and solution design" -m "Refs #10. Preserve identifiers, historical claims and legacy links." -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Task D3: complete release-bundle consumers

**Modify:** `tools/build_release.py`, `tests/unit/test_release_tools.py`.

- [ ] Add a `ReleaseDocuments` unittest using the existing `load` helper and
      imported `tempfile`, `mock`, `contextlib`, `io`, `Path`; add `zipfile`.

```python
class ReleaseDocuments(unittest.TestCase):
    def test_complete_bundle_contains_both_authoritative_documents(self):
        bundle = load(str(Path("tools") / "build_release.py"))
        packager = load(str(Path("tools") / "build_package.py"))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dist = root / "dist"
            demo = root / "build" / "demo"
            plugin = root / "plugin"
            files = {
                dist / "frontier-envisioning-plugin-1.6.1.zip": b"package",
                demo / bundle.DEMO_HTML_NAME: b"blueprint",
                demo / "identity" / "caldova-agent-identity" / "catalog.html": b"catalogue",
                plugin / "README.md": b"guide",
                plugin / "MIT.md": b"licence",
                plugin / "THIRD-PARTY-NOTICES.md": b"notices",
                root / "CHANGELOG.md": b"history",
                root / "docs" / "prd-and-solution-design.md": b"legacy links",
                root / "docs" / "prd.md": b"requirements",
                root / "docs" / "solution-design.md": b"architecture",
            }
            for path, data in files.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            with mock.patch.object(bundle, "ROOT", root), \
                    mock.patch.object(bundle, "PLUGIN", plugin), \
                    mock.patch.object(bundle, "DEMO_DIR", demo), \
                    mock.patch.object(bundle, "plugin_version", return_value="1.6.1"), \
                    mock.patch.object(bundle, "load_module", return_value=packager), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(bundle.main(["--dist", str(dist)]), 0)
            with zipfile.ZipFile(dist / "frontier-envisioning-1.6.1-complete.zip") as archive:
                prefix = "frontier-envisioning-1.6.1/"
                self.assertEqual(archive.read(prefix + "docs/prd.md"), b"requirements")
                self.assertEqual(archive.read(prefix + "docs/solution-design.md"), b"architecture")
                start = archive.read(prefix + "START-HERE.md").decode()
                self.assertIn("docs/prd.md", start)
                self.assertIn("docs/solution-design.md", start)
```

- [ ] Run `python -m pytest tests\unit\test_release_tools.py -q -k ReleaseDocuments`.
      Expected red: the new document entries/START-HERE references are absent.
- [ ] In the existing `entries` list, replace the one combined-document entry
      with these three entries. The third is only the compatibility index:

```python
        ((ROOT / "docs" / "prd.md").read_bytes(), "docs/prd.md"),
        ((ROOT / "docs" / "solution-design.md").read_bytes(), "docs/solution-design.md"),
        ((ROOT / "docs" / "prd-and-solution-design.md").read_bytes(), "docs/prd-and-solution-design.md"),
```

In the `START` Markdown table replace the generic documentation row with:

```markdown
| `docs/prd.md` | Product requirements, release plan and product decisions |
| `docs/solution-design.md` | Architecture, components, flows and verification |
| `docs/prd-and-solution-design.md` | Legacy companion links only |
| `docs/analysis/` | Existing analysis documents |
```

Keep ZIP canonicalisation and existing analysis inclusion unchanged. Do not add
engineering policy, sprint or raw intake audit files to the release bundle.

- [ ] Run the D3 selector, then `python tools\dev.py package demo bundle`.
      Expected green: exact entries/bytes and START-HERE links; real bundle builds.
- [ ] Commit the two D3 files with message `fix: bundle the separate product documents`,
      issue body `Refs #10.` and the standard Copilot co-author trailer.

## Task D4: deterministic metadata, local links and work-package gate

**Create:** `tools/check_docs.py`, `tests/unit/test_docs_validation.py`.
**Modify:** `tools/dev.py`.

- [ ] Add these initial tests. All new functions below are defined in the
      implementation block; tests use temporary files, not repository mutations.

```python
import tempfile
import unittest
from pathlib import Path
from tests.unit._util import load

class DocumentationValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = load(str(Path("tools") / "check_docs.py"))

    def header(self, references="[Issue](https://github.com/urruegg/frontier-envisioning/issues/10)"):
        return (
            "# Test\n\n| Field | Value |\n|---|---|\n"
            "| Version | 0.1 |\n| Date | 2026-11-09 |\n| Author | Maintainers |\n"
            "| Status | Proposed |\n| Scope | Test |\n"
            f"| References | {references} |\n"
        )

    def test_metadata_requires_exact_fields_and_real_date(self):
        self.assertEqual(self.docs.metadata_errors(self.header()), [])
        self.assertTrue(self.docs.metadata_errors(self.header().replace("2026-11-09", "2026-02-30")))
        self.assertTrue(self.docs.metadata_errors(self.header().replace("| Scope | Test |\n", "")))
        self.assertTrue(self.docs.metadata_errors("# Missing metadata\n"))
        self.assertTrue(self.docs.metadata_errors(self.header() + "| Extra | Invalid |\n"))
        self.assertTrue(self.docs.metadata_errors(
            self.header().replace("| Author | Maintainers |", "| Author |  |")
        ))

    def test_fences_duplicates_and_explicit_anchors(self):
        text = "# Title\n## Repeated\n## Repeated\n<a id=\"legacy\"></a>\n```md\n# Not a heading\n```\n"
        anchors = self.docs.anchors(text)
        self.assertTrue({"title", "repeated", "repeated-1", "legacy"}.issubset(anchors))
        self.assertNotIn("not-a-heading", anchors)

    def test_links_cover_parentheses_and_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.md"
            target = root / "target (sample).md"
            target.write_text("# Destination\n", encoding="utf-8")
            text = "[OK](<target (sample).md#destination>)\n"
            self.assertEqual(self.docs.link_errors(root, source, text), [])
            self.assertTrue(self.docs.link_errors(root, source, "[Bad](missing.md)"))
            self.assertTrue(self.docs.link_errors(root, source, "[Bad](<target (sample).md#absent>)"))
            self.assertTrue(self.docs.link_errors(root, source, "[Bad](../../outside.md)"))
            self.assertTrue(self.docs.link_errors(root, source, "[Broken](unfinished"))

    def test_eligibility_excludes_historical_and_product_contracts(self):
        self.assertTrue(self.docs.eligible(Path("docs") / "spec" / "new.md"))
        for path in ("plugin/README.md", "docs/intake/receipt.md", "docs/plans/old.md",
                     "releases/README.md", ".agents/skills/x/SKILL.md",
                     "backlog/issues/INT-01.md", ".github/PULL_REQUEST_TEMPLATE.md"):
            self.assertFalse(self.docs.eligible(Path(path)))

    def test_reference_links_percent_encoding_and_non_markdown_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.md"
            (root / "a b.md").write_text("# Destination\n", encoding="utf-8")
            (root / "sample.json").write_text("{}", encoding="utf-8")
            text = "[Label][REF]\n[ref]: <a%20b.md#destination>\n[Data](sample.json)\n"
            self.assertEqual(self.docs.link_errors(root, source, text), [])
            self.assertTrue(self.docs.link_errors(root, source, "[Missing][absent]"))
            self.assertTrue(self.docs.link_errors(root, source, "[Bad](sample.json#unsupported)"))

    def test_sprint_links_rows_and_catalogues_are_real_local_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for folder in ("idea", "spec", "plan", "sprint"):
                directory = root / "docs" / folder
                directory.mkdir(parents=True)
                (directory / "README.md").write_text(self.header(), encoding="utf-8")
            for folder in ("idea", "spec", "plan"):
                child = root / "docs" / folder / "x.md"
                child.write_text(self.header(), encoding="utf-8")
                (child.parent / "README.md").write_text(
                    self.header() + "\n[Child](x.md)\n", encoding="utf-8"
                )
            path = root / "docs" / "sprint" / "S-001.md"
            governing = (
                "[Issue](https://github.com/urruegg/frontier-envisioning/issues/10), "
                "[Idea](../idea/x.md), [Spec](../spec/x.md), [Plan](../plan/x.md)"
            )
            table = (
                "\n| Issue | Idea | Spec | Plan | Owner | Dependencies | State | PR/evidence |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| [#10](https://github.com/urruegg/frontier-envisioning/issues/10) "
                "| [Idea](../idea/x.md) | [Spec](../spec/x.md) | [Plan](../plan/x.md) "
                "| Maintainer | None | Proposed | Not implemented |\n"
            )
            text = self.header(governing) + table
            path.write_text(text, encoding="utf-8")
            (path.parent / "README.md").write_text(
                self.header() + "\n[Sprint](S-001.md)\n", encoding="utf-8"
            )
            self.assertEqual(self.docs.sprint_errors(root, path, text), [])
            self.assertTrue(self.docs.sprint_errors(root, path, text.replace("[Plan](../plan/x.md)", "Missing")))
            self.assertTrue(self.docs.sprint_errors(root, path, text.replace("| Maintainer |", "||")))
            self.assertEqual(self.docs.check_documents(root, list(root.rglob("*.md"))), [])
            (path.parent / "README.md").write_text(self.header(), encoding="utf-8")
            self.assertTrue(self.docs.check_documents(root, list(root.rglob("*.md"))))

    def test_malformed_angle_target_has_an_explicit_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "source.md"
            self.assertTrue(self.docs.link_errors(root, path, "[Bad](<missing.md)"))

    def test_all_four_canonical_catalogues_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = self.docs.check_documents(Path(tmp), [])
            self.assertEqual(len(errors), 4)
            self.assertTrue(all("directory missing" in error for error in errors))
```

- [ ] Run `python -m pytest tests\unit\test_docs_validation.py -q`.
      Expected red: new checker module absent. Add explicit       the additional cases below before implementing their behaviour.
- [ ] Create the checker with this complete baseline. Keep its supported syntax
      and exclusions documented; do not claim full CommonMark or live GitHub verification.

```python
#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check eligible metadata, local Markdown links, catalogues and sprint records.

Uses the standard library only. External issue URLs are checked for shape,
not existence, permission or human approval.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import ROOT, tracked_files  # noqa: E402

FIELDS = ("Version", "Date", "Author", "Status", "Scope", "References")
GUIDES = {"README.md", "CONTRIBUTING.md", "SECURITY.md", "backlog/README.md",
          "infra/README.md", "site/README.md", "src/renderer/README.md", "tests/README.md"}
FOLDERS = ("idea", "spec", "plan", "sprint")
ISSUE = re.compile(r"^https://github\.com/urruegg/frontier-envisioning/issues/[1-9]\d*$")

def eligible(relative: Path) -> bool:
    value = relative.as_posix()
    if value.startswith(("docs/intake/", "docs/plans/")):
        return False
    return relative.suffix == ".md" and (
        value.startswith("docs/") or value.startswith(".github/agent-policy/")
        or value in GUIDES
    )

def prose(text: str) -> str:
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1]:
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return "\n".join(lines)

def metadata_errors(text: str) -> list[str]:
    lines = prose(text).splitlines()
    headings = [i for i, line in enumerate(lines) if line.startswith("# ")]
    if len(headings) != 1:
        return ["expected exactly one H1"]
    tail = lines[headings[0] + 1:]
    while tail and not tail[0].strip():
        tail.pop(0)
    if len(tail) < 8 or tail[0].replace(" ", "") != "|Field|Value|":
        return ["six-field metadata must follow the H1"]
    if not re.fullmatch(r"\|[: -]+\|[: -]+\|", tail[1]):
        return ["metadata table separator is malformed"]
    values, errors = {}, []
    if len(tail) > 8 and tail[8].lstrip().startswith("|"):
        errors.append("metadata has fields beyond the six-field contract")
    for name, line in zip(FIELDS, tail[2:8]):
        match = re.fullmatch(r"\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|", line)
        if not match or match.group(1).strip("* ") != name:
            errors.append(f"missing or misplaced metadata field: {name}")
        else:
            value = match.group(2).strip()
            if not value:
                errors.append(f"metadata field is empty: {name}")
            else:
                values[name] = value
    if "Version" in values and not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", values["Version"]):
        errors.append("document Version must be numeric, separate from release state")
    if "Date" in values:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", values["Date"]):
                raise ValueError("not ISO calendar form")
            date.fromisoformat(values["Date"])
        except ValueError:
            errors.append("Date must be a real ISO calendar date")
    return errors

def anchors(text: str) -> set[str]:
    result = set(re.findall(r'<a\s+id="([^"]+)"', prose(text)))
    used = {}
    for title in re.findall(r"(?m)^#{1,6}\s+(.+)$", prose(text)):
        slug = re.sub(r"[^\w -]", "", title.lower()).replace(" ", "-")
        count = used.get(slug, 0)
        used[slug] = count + 1
        result.add(f"{slug}-{count}" if count else slug)
    return result

def links(text: str) -> tuple[list[str], list[str]]:
    body = re.sub(r"`[^`\n]*`", "", prose(text))
    targets, errors = [], []
    definitions = {key.casefold(): value for key, value in
                   re.findall(r"(?m)^\s*\[([^\]\n]+)\]:\s*(.+)$", body)}
    for match in re.finditer(r"\[[^\]\n]*\]\(", body):
        start, depth, index, escaped = match.end(), 1, match.end(), False
        while index < len(body) and depth:
            char = body[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            index += 1
        if depth:
            errors.append("unclosed inline Markdown link")
        else:
            targets.append(body[start:index - 1].strip())
    for label, reference in re.findall(r"\[([^\]\n]+)\]\[([^\]\n]*)\]", body):
        key = (reference or label).casefold()
        if key not in definitions:
            errors.append(f"undefined Markdown reference: {key}")
        else:
            targets.append(definitions[key])
    return targets, errors

def destination(target: str) -> str:
    if target.startswith("<"):
        close = target.find(">")
        if close < 0:
            raise ValueError("unclosed angle-bracket link target")
        return target[1:close]
    return re.sub(r"""\s+["'][^"']*["']$""", "", target)

def destinations(text: str) -> tuple[list[str], list[str]]:
    raw_targets, errors = links(text)
    targets = []
    for raw in raw_targets:
        try:
            targets.append(destination(raw))
        except ValueError as error:
            errors.append(str(error))
    return targets, errors

def link_errors(root: Path, source: Path, text: str) -> list[str]:
    targets, errors = destinations(text)
    for target in targets:
        url = urlsplit(target)
        if url.scheme in ("http", "https", "mailto", "tel") or (url.netloc and not url.scheme):
            continue
        if url.scheme:
            errors.append(f"unsupported non-portable link scheme: {target}")
            continue
        path = (source.parent / unquote(url.path)).resolve() if url.path else source.resolve()
        if not path.is_relative_to(root.resolve()):
            errors.append(f"local link escapes repository: {target}")
        elif not path.exists():
            errors.append(f"local link missing: {target}")
        elif url.fragment and path.is_dir():
            errors.append(f"directory fragment requires an explicit document: {target}")
        elif url.fragment and path.is_file():
            if path.suffix == ".md":
                available = anchors(path.read_text(encoding="utf-8"))
            elif path.suffix in (".html", ".htm"):
                available = set(re.findall(r'\bid="([^"]+)"', path.read_text(encoding="utf-8")))
            else:
                errors.append(f"fragment on unsupported local target: {target}")
                continue
            if unquote(url.fragment) not in available:
                errors.append(f"local anchor missing: {target}")
    return errors

def work_kinds(root: Path, source: Path, text: str) -> tuple[set[str], list[str]]:
    result = set()
    targets, errors = destinations(text)
    for target in targets:
        if ISSUE.fullmatch(target):
            result.add("issue")
        elif not urlsplit(target).scheme:
            path = (source.parent / unquote(urlsplit(target).path)).resolve()
            for folder in ("idea", "spec", "plan"):
                if path.is_relative_to(root / "docs" / folder) and path.suffix == ".md":
                    result.add(folder)
    return result, errors

def sprint_errors(root: Path, path: Path, text: str) -> list[str]:
    if path.parent != root / "docs" / "sprint" or path.name == "README.md":
        return []
    header = "\n".join(text.splitlines()[:12])
    kinds, errors = work_kinds(root, path, header)
    if not {"issue", "idea", "spec", "plan"}.issubset(kinds):
        errors.append("sprint References must link issue, idea, spec and plan")
    wanted = ["Issue", "Idea", "Spec", "Plan", "Owner", "Dependencies", "State", "PR/evidence"]
    lines = text.splitlines()
    index = next((i for i, line in enumerate(lines)
                  if [cell.strip() for cell in line.strip("|").split("|")] == wanted), None)
    if index is None:
        return errors + ["sprint work-item table missing"]
    rows = []
    for line in lines[index + 2:]:
        if not line.startswith("|"):
            break
        rows.append(line)
    if not rows:
        errors.append("sprint work-item table has no records")
    for number, row in enumerate(rows, 1):
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        kinds, row_errors = work_kinds(root, path, row)
        errors.extend(row_errors)
        if len(cells) != len(wanted) or not cells[4] or not cells[6]:
            errors.append(f"sprint row {number} has malformed/missing owner or state")
        elif not {"issue", "idea", "spec", "plan"}.issubset(kinds):
            errors.append(f"sprint row {number} lacks verified-shape governing links")
    return errors

def check_documents(root: Path, paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        relative = path.relative_to(root)
        if not eligible(relative):
            continue
        text = path.read_text(encoding="utf-8")
        for error in metadata_errors(text) + link_errors(root, path, text) + sprint_errors(root, path, text):
            errors.append(f"{relative.as_posix()}: {error}")
    for folder in FOLDERS:
        directory = root / "docs" / folder
        if not directory.exists():
            errors.append(f"docs/{folder}: canonical directory missing")
            continue
        readme = directory / "README.md"
        if not readme.is_file():
            errors.append(f"docs/{folder}: catalogue README missing")
            continue
        linked = set()
        targets, target_errors = destinations(readme.read_text(encoding="utf-8"))
        errors.extend(f"docs/{folder}/README.md: {error}" for error in target_errors)
        for target in targets:
            if not urlsplit(target).scheme:
                linked.add((directory / unquote(urlsplit(target).path)).resolve())
        for child in directory.glob("*.md"):
            if child != readme and child.resolve() not in linked:
                errors.append(f"docs/{folder}: uncatalogued child {child.name}")
    return errors

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.parse_args(argv)
    errors = check_documents(ROOT, [p for p in tracked_files() if p.suffix == ".md"])
    for error in errors:
        print("DOCS " + error)
    print(f"documentation check: {len(errors)} errors; external issue existence/approval not verified")
    return int(bool(errors))

if __name__ == "__main__":
    raise SystemExit(main())
```

Malformed targets have an explicit diagnostic shared by link, sprint and
catalogue parsing. Reference labels are case-normalised. Extend test coverage
when a concrete repository syntax mismatch is found; do not silently skip a
failed active document.

- [ ] Run the unit selector; correct any parser mismatch against the actual
      supported Markdown syntax. Expected green: date/header, escaped-root,
      duplicate-anchor, balanced-target and exclusion tests pass.
- [ ] Add this dev-runner insertion and command registration:

```python
@step("documentation metadata, links and traceability")
def cmd_docs():
    if tool("check_docs", ["--strict"] if STRICT else []):
        raise GateFailure("documentation contract")
```

Register `"docs": cmd_docs` in `gated`. Add `cmd_docs()` after `cmd_lint()` in
both `precommit` and `check`; document `docs` in the command help. No workflow
edit is necessary: existing L0/L1 call the runner and existing L2 is unchanged.

- [ ] Add a runner test in `tests/unit/test_docs_validation.py`:

```python
from unittest import mock
import contextlib
import io

class DocumentationRunner(unittest.TestCase):
    def test_docs_command_and_quality_gate_fail_on_contract_error(self):
        dev = load(str(Path("tools") / "dev.py"))
        with mock.patch.object(dev, "tool", return_value=1), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dev.main(["docs"]), 1)

    def test_docs_command_succeeds_when_checker_passes(self):
        dev = load(str(Path("tools") / "dev.py"))
        with mock.patch.object(dev, "tool", return_value=0), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(dev.main(["docs"]), 0)

    def test_aggregate_gates_call_documentation_check(self):
        for command in ("precommit", "check"):
            dev = load(str(Path("tools") / "dev.py"))
            names = ("cmd_template_check", "cmd_lint", "cmd_docs", "cmd_scan",
                     "cmd_test", "cmd_selftest", "cmd_package", "cmd_demo",
                     "cmd_verify_release", "cmd_dom")
            steps = {name: mock.Mock() for name in names}
            with mock.patch.multiple(dev, **steps), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(dev.main([command]), 0)
            steps["cmd_docs"].assert_called_once_with()
```

Run these red before registration, then green after registration. The aggregate
test mocks other steps and does not run builds.

## Task D5: coherent eligible-header migration and real intake surfaces

**Modify:** the eligible guides below, four new catalogues, active product docs,
`docs/plans/README.md`, `.github/ISSUE_TEMPLATE/feature.yml`,
`.github/ISSUE_TEMPLATE/bug.yml`, `.github/ISSUE_TEMPLATE/decision.yml`,
`.github/PULL_REQUEST_TEMPLATE.md`.
**Tests:** `tests/unit/test_docs_validation.py`, `tests/unit/test_docs_contract.py`.

Complete D4 and D5 on the same branch before enabling a green strict gate.
An intermediate commit may be red; do not publish it as a completed feature.
No blanket waiver or silent exclusion of active docs is allowed.

- [ ] Run `python tools\dev.py docs --strict` to observe the real header/link/
      catalogue failures. Save the exact errors and work through their paths.
- [ ] Add truthful six-field metadata to active `docs/**` except historical
      `docs/intake/**` and legacy `docs/plans/**`; add the ordinary guide headers:

```text
README.md
CONTRIBUTING.md
SECURITY.md
backlog/README.md
infra/README.md
site/README.md
src/renderer/README.md
tests/README.md
```

Do not edit the contents of old plans, archived intake, licences/notices,
backlog issue YAML, vendor files, central CHANGELOG or any `plugin/**` Markdown.
The legacy plans README gets a routing note only, explicitly exempt from the
new header gate with the preserved legacy area.

Header values: actual revision date; existing credited author plus AI-assisted
maintenance disclosure; `Maintained; approval not inferred` for an existing
guide, existing Proposed status for decisions, actual approved-design status
only where recorded. References must be real relevant links, not padding.
Preserve the internal classification in the HubWorks analysis.

- [ ] Add this block to each feature/bug/decision form before its final fields:

```yaml
  - type: textarea
    id: work-package
    attributes:
      label: Governing work package
      description: Links to the idea, approved spec, implementation plan and sprint. Draft intake may leave missing stages explicitly unapproved; readiness requires all real links.
    validations:
      required: true
```

The form collects links; it does not invent artifacts, grant approval or force
a fully written plan before an initial idea can be filed. Readiness and real
external issue verification remain human/parent controls.

Add this checkbox immediately after the existing spec/plan checkbox in the PR
template, preserving all original headings, comments and checklist ordering:

```markdown
- [ ] Linked work package: real issue, idea, approved spec, approved plan and sprint records are linked in this PR
```

Update the original spec/plan path hint to the new singular directories.
The local checker validates recorded artifacts; it does not discover every
GitHub item or prove every PR's association. The parent and human PR review
verify that the actual work is the linked ready item. Do not claim a new
external synchronisation or approval service.

- [ ] Extend the contract test with this class; merge the `yaml` import into
      its import block. Run red before form insertion, then green. PyYAML is
      an existing development dependency; the production checker stays stdlib.

```python
import yaml

class IssueWorkPackage(unittest.TestCase):
    def test_existing_forms_collect_real_governing_links(self):
        baseline = {
            "feature.yml": {"problem", "area", "acceptance", "source", "neutral"},
            "bug.yml": {"version", "what", "steps", "logs", "neutral"},
            "decision.yml": {"question", "options", "recommendation", "owner", "due"},
        }
        for name, existing in baseline.items():
            path = ROOT / ".github" / "ISSUE_TEMPLATE" / name
            form = yaml.safe_load(path.read_text(encoding="utf-8"))
            fields = {field.get("id"): field for field in form["body"] if "id" in field}
            self.assertTrue(existing.issubset(fields))
            self.assertIn("work-package", fields)
            self.assertTrue(fields["work-package"]["validations"]["required"])
            if "neutral" in fields:
                options = fields["neutral"]["attributes"]["options"]
                self.assertTrue(options[0]["required"])

    def test_pr_template_keeps_its_sections_and_adds_work_package(self):
        text = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
        for heading in ("## Summary (written by a person, in your own words)",
                        "## How it was built", "## Gates", "## Rules",
                        "## Release pull requests only"):
            self.assertIn(heading, text)
        self.assertIn("Linked work package", text)
        self.assertIn("<!-- What changes", text)
```
- [ ] Update catalogue/backlinks and active document links to the split
      documents. Keep historic anchors/records intact and all new sprint rows
      linked to real issues.
- [ ] Run the combined selectors:

```powershell
python -m pytest tests\unit\test_docs_contract.py tests\unit\test_docs_validation.py tests\unit\test_release_tools.py -q
python tools\dev.py docs --strict
python tools\dev.py check --strict
```

Expected: all targeted tests and strict local contract/gates pass. Existing
unreleased-version reproduction skip is reported honestly, not turned into a
new release manifest.

- [ ] Verify `git diff --name-only origin/main...HEAD -- plugin releases .github\hooks .github\CODEOWNERS`
      has no D-workstream changes. Run `git diff --check`.
- [ ] Commit D4/D5 owned paths with `feat: validate linked documentation work packages`,
      body `Refs #10.` and the standard co-author trailer.
- [ ] Return owned paths, exact tests/results, preserved IDs/legacy links,
      unchanged protected/product data, commit and unresolved human routing.
      Parent reviews against DG-01/02/04/07 and publishes a scoped draft PR.
