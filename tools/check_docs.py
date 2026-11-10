#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Check active documentation metadata, local links, catalogues and sprint records.

Supports fenced/inline code, ATX/setext headings, inline links/images with balanced
parentheses, angle destinations, quoted titles and case-insensitive references.
This is a deliberately bounded Markdown checker, not a CommonMark renderer.
Historical intake, packaged/vendor contracts and tracker/PR prose are not
eligible. Named historical work records retain their format but their links
are checked. External URLs are never fetched; issue shape is not live existence,
readiness, permission or approval.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import SplitResult, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import ROOT, tracked_files  # noqa: E402

FIELDS = ("Version", "Date", "Author", "Status", "Scope", "References")
GUIDES = {"README.md", "CONTRIBUTING.md", "SECURITY.md", "backlog/README.md",
          "infra/README.md", "site/README.md", "src/renderer/README.md", "tests/README.md"}
FOLDERS = ("ideas", "specs", "plans", "sprints")
RETIRED_FOLDERS = ("idea", "spec", "plan", "sprint")
WORK_FOLDERS = {"idea": "ideas", "spec": "specs", "plan": "plans"}
HISTORICAL_RECORDS = {
    "docs/specs/2026-11-08-cowork-intake-design.md",
    "docs/specs/2026-11-09-handover-1.6-design.md",
    "docs/specs/2026-11-09-workflow-legend-design.md",
    "docs/plans/2026-11-08-cowork-m0-implementation-plan.md",
    "docs/plans/2026-11-09-handover-1.6-plan.md",
    "docs/plans/2026-11-09-workflow-legend-plan.md",
}
WORK_KINDS = {"issue", "idea", "spec", "plan"}
SPRINT_COLUMNS = ("Issue", "Idea", "Spec", "Plan", "Owner", "Dependencies", "State", "PR/evidence")
ISSUE = re.compile(r"^https://github\.com/urruegg/frontier-envisioning/issues/[1-9]\d*$")
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[([^\]\n]+)\]:[ \t]*(.*)$", re.M)


def eligible(relative: Path) -> bool:
    value = relative.as_posix()
    return not relative.is_absolute() and ".." not in relative.parts and relative.suffix == ".md" and (
        (value.startswith("docs/") and not value.startswith("docs/intake/") and value not in HISTORICAL_RECORDS)
        or value.startswith(".github/agent-policy/") or value in GUIDES
    )


def prose(text: str) -> str:
    """Mask fenced samples, preserving line boundaries (including long fences)."""
    lines = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            lines.append("")
        elif marker:
            fence = (marker[1][0], len(marker[1]))
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines)


def _body(text: str) -> str:
    """Required YAML frontmatter is not Markdown prose."""
    return prose(re.sub(r"\A---\r?\n.*?\r?\n---[ \t]*(?:\r?\n|\Z)", "", text, count=1, flags=re.S))


def _mask_code(text: str) -> str:
    pattern = r"(?<![`\\])(`+)(?!`)(.*?)(?<!`)\1(?!`)"
    return re.sub(pattern, lambda m: re.sub(r"[^\n]", " ", m[0]), text, flags=re.S)


def _headings(lines: list[str]) -> list[tuple[int, int, str]]:
    result = []
    for index, line in enumerate(lines):
        match = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*))?$", line)
        if match:
            result.append((index, len(match[1]), re.sub(r"(?:\s+|^)#+\s*$", "", (match[2] or "").strip())))
        elif index and re.fullmatch(r" {0,3}(?:=+|-+)\s*", line) and lines[index - 1].strip() \
                and not re.match(r"^\s*[|>#*-]", lines[index - 1]):
            result.append((index, 1 if line.lstrip().startswith("=") else 2, lines[index - 1].strip()))
    return result


def _cells(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return []
    # A pipe inside an inline-code sample is not a column boundary.
    masked = _mask_code(line)
    cuts = [i for i, char in enumerate(masked) if char == "|" and (i == 0 or masked[i - 1] != "\\")]
    return [line[a + 1:b].strip() for a, b in zip(cuts, cuts[1:])]


def _separator(line: str, count: int) -> bool:
    cells = _cells(line)
    return len(cells) == count and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _metadata(text: str) -> tuple[dict[str, str], list[str]]:
    lines = _body(text).splitlines()
    headings = [end for end, level, _ in _headings(lines) if level == 1]
    if len(headings) != 1:
        return {}, ["expected exactly one H1"]
    start = headings[0] + 1
    while start < len(lines) and not lines[start].strip():
        start += 1
    if start >= len(lines) or _cells(lines[start]) != ["Field", "Value"]:
        return {}, ["six-field metadata must follow the H1"]
    errors = []
    if start + 1 >= len(lines) or not _separator(lines[start + 1], 2):
        errors.append("metadata table separator is malformed")
    values = {}
    for index, field in enumerate(FIELDS, start + 2):
        cells = _cells(lines[index]) if index < len(lines) else []
        if len(cells) != 2 or cells[0] != field:
            errors.append(f"missing or misplaced metadata field: {field}")
        elif not cells[1]:
            errors.append(f"metadata field is empty: {field}")
        else:
            values[field] = cells[1]
    if start + 8 < len(lines) and lines[start + 8].lstrip().startswith("|"):
        errors.append("metadata has fields beyond the six-field contract")
    for index in range(start + 8, len(lines) - 2):
        first_row = _cells(lines[index + 2])
        if _cells(lines[index]) == ["Field", "Value"] and first_row and first_row[0] in FIELDS:
            errors.append("duplicate metadata table")
            break
    if "Version" in values and not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", values["Version"]):
        errors.append("document Version must be numeric, separate from release state")
    if "Date" in values:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", values["Date"]):
                raise ValueError("not ISO calendar form")
            date.fromisoformat(values["Date"])
        except ValueError:
            errors.append("Date must be a real ISO calendar date")
    return values, errors


def metadata_errors(text: str) -> list[str]:
    return _metadata(text)[1]


def anchors(text: str) -> set[str]:
    body = _body(text)
    result = set(re.findall(r"""<a\b[^>]*\sid\s*=\s*["']([^"']+)["']""", _mask_code(body), re.I))
    used: set[str] = set()
    for _, _, title in _headings(body.splitlines()):
        title = _heading_text(title)
        title = re.sub(r"<[^>]*>", "", title).lower()
        slug = "".join(char for char in title if unicodedata.category(char)[0] in "LN" or char in "_- \t")
        slug = re.sub(r"[ \t]", "-", slug)
        candidate, suffix = slug, 0
        while candidate in used:
            suffix += 1
            candidate = f"{slug}-{suffix}"
        used.add(candidate)
        result.add(candidate)
    return result


def _label(label: str) -> str:
    return " ".join(label.split()).casefold()


def _reference_definitions(text: str) -> dict[str, str]:
    """Resolve fragments against definitions from the enclosing document's prose."""
    return {_label(match[1]): match[2].strip()
            for match in REFERENCE_DEFINITION.finditer(_mask_code(_body(text)))}


def _closing_bracket(body: str, start: int) -> int | None:
    depth, index = 1, start + 1
    while index < len(body):
        if body[index] == "\\":
            index += 2
            continue
        if body[index] == "[":
            depth += 1
        elif body[index] == "]":
            depth -= 1
            if not depth:
                return index
        index += 1
    return None


def _inline_target(body: str, start: int) -> tuple[str | None, int, str | None]:
    """Read through balanced parentheses; angle-wrapped filenames may contain them."""
    while start < len(body) and body[start] in " \t":
        start += 1
    index, depth = start, 1
    angle = False
    quote = None
    while index < len(body) and body[index] != "\n":
        char = body[index]
        if char == "\\":
            index += 2
            continue
        if quote:
            if char == quote:
                quote = None
        elif index == start and char == "<":
            angle = True
        elif angle and char == ">":
            angle = False
        elif not angle:
            if char in "\"'" and index > start and body[index - 1].isspace() and depth == 1:
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return body[start:index].strip(), index + 1, None
        index += 1
    error = "unclosed angle-bracket link target" if angle else (
        "malformed link title" if quote else "unclosed inline Markdown link")
    return None, index, error


def _heading_text(title: str) -> str:
    """Keep displayed labels, not inline destinations or reference identifiers."""
    result = []
    pending = [(title, 0)]
    while pending:
        title, index = pending.pop()
        masked = _mask_code(title)
        while index < len(title):
            if masked[index] != "[":
                result.append(title[index])
                index += 1
                continue
            close = _closing_bracket(masked, index)
            if close is None:
                result.append(title[index:])
                break
            label = title[index + 1:close]
            index = close + 1
            if index < len(title) and title[index] == "(":
                _, end, error = _inline_target(title, index + 1)
                if not error:
                    index = end
            elif index < len(title) and title[index] == "[":
                end = _closing_bracket(title, index)
                if end is not None:
                    index = end + 1
            pending.append((title, index))
            title, index = label, 0
            masked = _mask_code(title)
    return "".join(result)


def links(text: str, definitions: dict[str, str] | None = None) -> tuple[list[str], list[str]]:
    """Return raw targets and syntax errors; never scan inside image alt text."""
    body = _mask_code(_body(text))
    targets, errors = [], []
    definitions = dict(definitions or {})

    def definition(match: re.Match[str]) -> str:
        key, value = _label(match[1]), match[2].strip()
        if key in definitions and definitions[key] != value:
            errors.append(f"conflicting Markdown reference: {key}")
        if not value:
            errors.append(f"empty Markdown reference destination: {key}")
        definitions[key] = value
        targets.append(value)
        return ""

    body = REFERENCE_DEFINITION.sub(definition, body)

    pending = [(body, 0)]
    while pending:
        part, index = pending.pop()
        while index < len(part):
            if part[index] == "\\":
                index += 2
                continue
            if part[index] != "[":
                index += 1
                continue
            start = index
            close = _closing_bracket(part, start)
            if close is None:
                index += 1
                continue
            label = part[start + 1:close]
            image = start > 0 and part[start - 1] == "!"
            index = close + 1
            if index < len(part) and part[index] == "(":
                raw, index, error = _inline_target(part, index + 1)
                if error:
                    errors.append(error)
                elif raw is not None:
                    targets.append(raw)
            elif index < len(part) and part[index] == "[":
                end = _closing_bracket(part, index)
                if end is None:
                    errors.append("unclosed Markdown reference")
                    break
                key = _label(part[index + 1:end] or label)
                if key not in definitions:
                    errors.append(f"undefined Markdown reference: {key}")
                else:
                    targets.append(definitions[key])
                index = end + 1
            elif _label(label) in definitions:
                targets.append(definitions[_label(label)])
            if not image:
                pending.append((part, index))
                part, index = label, 0

    return targets, errors


def destination(target: str) -> str:
    """Strip optional quoted titles and Markdown escapes, not filename parentheses."""
    target = target.strip()
    if target.startswith("<"):
        close = target.find(">")
        if close < 0:
            raise ValueError("unclosed angle-bracket link target")
        tail = target[close + 1:].strip()
        if tail and not re.fullmatch(r"""(?:"[^"]*"|'[^']*')""", tail):
            raise ValueError("malformed angle-bracket link target")
        target = target[1:close]
    else:
        title = re.search(r"""\s+(["'])(.*?)\1$""", target)
        if title:
            target = target[:title.start()]
        elif re.search(r"""\s+["']""", target):
            raise ValueError("malformed link title")
        depth, escaped = 0, False
        for char in target:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth < 0:
                    raise ValueError("unbalanced parentheses in link target")
        if depth:
            raise ValueError("unbalanced parentheses in link target")
    return re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", target)


def destinations(text: str, definitions: dict[str, str] | None = None) -> tuple[list[str], list[str]]:
    raw_targets, errors = links(text, definitions)
    targets = []
    for raw in raw_targets:
        try:
            targets.append(destination(raw))
        except ValueError as error:
            errors.append(str(error))
    return list(dict.fromkeys(targets)), errors


def _url(target: str) -> SplitResult:
    if re.search(r"%(?![0-9a-fA-F]{2})", target):
        raise ValueError("malformed percent encoding")
    try:
        url = urlsplit(target)
        if url.scheme in ("http", "https"):
            if not url.hostname or re.search(r"\s", url.netloc):
                raise ValueError("HTTP URL requires a host")
            _ = url.port  # Access validates the optional port without fetching anything.
        return url
    except ValueError as error:
        raise ValueError("malformed URL") from error


def _local_path(root: Path, source: Path, url: SplitResult) -> Path:
    try:
        path = unquote(url.path, errors="strict")
    except UnicodeError as error:
        raise ValueError("invalid UTF-8 in local link") from error
    if "\\" in path or re.match(r"^[A-Za-z]:", path) or any(ord(char) < 32 for char in path):
        raise ValueError("invalid local path")
    if not path:
        return source.resolve()
    return ((root / path.lstrip("/")) if path.startswith("/") else (source.parent / path)).resolve()


def link_errors(root: Path, source: Path, text: str, definitions: dict[str, str] | None = None) -> list[str]:
    targets, errors = destinations(text, definitions)
    for target in targets:
        try:
            url = _url(target)
            if url.scheme in ("http", "https", "mailto", "tel") or (url.netloc and not url.scheme):
                continue
            if url.scheme:
                errors.append(f"unsupported non-portable link scheme: {target}")
                continue
            path = _local_path(root, source, url)
            if not path.is_relative_to(root.resolve()):
                errors.append(f"local link escapes repository: {target}")
            elif not path.exists():
                errors.append(f"local link missing: {target}")
            elif url.fragment:
                fragment = unquote(url.fragment, errors="strict")
                if path.is_dir():
                    errors.append(f"directory fragment requires an explicit document: {target}")
                    continue
                if path.suffix not in (".md", ".html", ".htm"):
                    errors.append(f"fragment on unsupported local target: {target}")
                    continue
                content = text if path == source.resolve() else path.read_text(encoding="utf-8")
                available = anchors(content) if path.suffix == ".md" else set(
                    re.findall(r"""\sid\s*=\s*["']([^"']+)["']""", content, re.I))
                if fragment not in available:
                    errors.append(f"local anchor missing: {target}")
        except (ValueError, OSError, UnicodeError) as error:
            errors.append(f"{error}: {target}")
    return list(dict.fromkeys(errors))


def work_kinds(root: Path, source: Path, text: str,
               definitions: dict[str, str] | None = None) -> tuple[set[str], list[str]]:
    kinds: set[str] = set()
    targets, _ = destinations(text, definitions)
    errors = link_errors(root, source, text, definitions)
    for target in targets:
        try:
            url = _url(target)
            if ISSUE.fullmatch(f"{url.scheme}://{url.netloc}{url.path}"):
                kinds.add("issue")
            elif not url.scheme and not url.netloc:
                path = _local_path(root, source, url)
                for kind, folder in WORK_FOLDERS.items():
                    if path.is_relative_to((root / "docs" / folder).resolve()) and path.is_file() \
                            and path.suffix == ".md" and path.name != "README.md":
                        kinds.add(kind)
        except (ValueError, OSError, UnicodeError):
            # link_errors above owns the diagnostic; do not silently accept the kind.
            continue
    return kinds, errors


def sprint_errors(root: Path, path: Path, text: str) -> list[str]:
    if not path.is_relative_to(root / "docs" / "sprints") or path.name == "README.md":
        return []
    values, _ = _metadata(text)
    definitions = _reference_definitions(text)
    kinds, reference_errors = work_kinds(root, path, values.get("References", ""), definitions)
    errors = link_errors(root, path, text) + reference_errors
    if not WORK_KINDS.issubset(kinds):
        errors.append("sprint References must link issue, idea, spec and plan")
    lines = _body(text).splitlines()
    tables = [index for index, line in enumerate(lines) if _cells(line) == list(SPRINT_COLUMNS)]
    if not tables:
        return errors + ["sprint work-item table missing"]
    for index in tables:
        if index + 1 >= len(lines) or not _separator(lines[index + 1], len(SPRINT_COLUMNS)):
            errors.append("sprint work-item table separator is malformed")
        rows = []
        for line in lines[index + 2:]:
            if not line.lstrip().startswith("|"):
                break
            rows.append(line)
        if not rows:
            errors.append("sprint work-item table has no records")
        for number, row in enumerate(rows, 1):
            cells = _cells(row)
            if len(cells) != len(SPRINT_COLUMNS):
                errors.append(f"sprint row {number} has malformed columns")
                errors.extend(link_errors(root, path, row, definitions))
                continue
            if not cells[4] or not cells[6]:
                errors.append(f"sprint row {number} has missing owner or state")
            for kind, cell in zip(("issue", "idea", "spec", "plan"), cells):
                kinds, cell_errors = work_kinds(root, path, cell, definitions)
                errors.extend(cell_errors)
                if kind not in kinds:
                    errors.append(f"sprint row {number} lacks {kind} link in its column")
    return list(dict.fromkeys(errors))


def check_documents(root: Path, paths: list[Path]) -> list[str]:
    root = root.resolve()
    errors = []
    texts: dict[Path, str] = {}
    candidates = set(paths)
    for folder in RETIRED_FOLDERS:
        if (root / "docs" / folder).exists():
            errors.append(f"docs/{folder}: retired documentation directory exists")
    if (root / "docs" / "prd-and-solution-design.md").exists():
        errors.append("docs: retired combined product-document index exists")
    for folder in FOLDERS:
        directory = root / "docs" / folder
        if not directory.is_dir():
            errors.append(f"docs/{folder}: canonical directory missing")
        elif not (directory / "README.md").is_file():
            errors.append(f"docs/{folder}: catalogue README missing")
        else:
            candidates.add(directory / "README.md")
    for path in sorted(candidates):
        if not path.is_absolute():
            path = root / path
        if not path.is_relative_to(root) or not path.resolve().is_relative_to(root):
            errors.append(f"{path.name}: document outside repository")
            continue
        relative = path.relative_to(root)
        if not eligible(relative) and relative.as_posix() not in HISTORICAL_RECORDS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"{relative.as_posix()}: cannot read UTF-8 document ({type(error).__name__})")
            continue
        texts[path] = text
        metadata = metadata_errors(text) if eligible(relative) else []
        for error in metadata + link_errors(root, path, text) + sprint_errors(root, path, text):
            errors.append(f"{relative.as_posix()}: {error}")
    for folder in FOLDERS:
        directory = root / "docs" / folder
        readme = directory / "README.md"
        if readme not in texts:
            continue
        linked: set[Path] = set()
        targets, _ = destinations(texts[readme])
        for target in targets:
            try:
                url = _url(target)
                if not url.scheme and not url.netloc:
                    linked.add(_local_path(root, readme, url))
            except (ValueError, OSError, UnicodeError):
                continue  # The document link pass has already reported this target.
        for child in sorted(directory.glob("*.md")):
            if child != readme and child.resolve() not in linked:
                errors.append(f"docs/{folder}: uncatalogued child {child.name}")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="accepted for dev-runner parity; all documentation errors fail")
    parser.parse_args(argv)
    errors = check_documents(ROOT, [path for path in tracked_files() if path.suffix == ".md"])
    for error in errors:
        print("DOCS " + error)
    print(f"documentation check: {len(errors)} errors; external issue existence/approval not verified")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
