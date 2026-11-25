# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Bounded offline data helpers. Supplied values never enter diagnostics."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

MIB = 1024 ** 2
ROLES = ("prd", "solution-design", "decisions", "it-readiness",
         "identity", "blueprint", "value", "finops")
EXTENSIONS = {".md", ".txt", ".json", ".pdf", ".docx", ".xlsx", ".pptx", ".csv"}


class FactoryError(ValueError):
    """Malformed input or unavailable local evidence."""


def need(condition, code="FACTORY_INPUT"):
    if not condition:
        raise FactoryError(code)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _json_tree(value):
    pending = [(value, 0)]
    while pending:
        item, depth = pending.pop()
        need(depth <= 128, "FACTORY_JSON")
        if isinstance(item, dict):
            need(all(isinstance(key, str) for key in item), "FACTORY_JSON")
            pending.extend((key, depth + 1) for key in item)
            pending.extend((child, depth + 1) for child in item.values())
        elif isinstance(item, list):
            pending.extend((child, depth + 1) for child in item)
        elif isinstance(item, str):
            need(not any(0xD800 <= ord(char) <= 0xDFFF for char in item), "FACTORY_JSON")
        elif isinstance(item, float):
            need(math.isfinite(item), "FACTORY_JSON")
        else:
            need(item is None or type(item) in (bool, int), "FACTORY_JSON")


def encoded(value):
    _json_tree(value)
    try:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                           indent=2, allow_nan=False) + "\n").encode("utf-8")
    except (ValueError, UnicodeError, OverflowError):
        raise FactoryError("FACTORY_JSON") from None


def decode(raw, limit=MIB):
    need(type(limit) is int and limit >= 0 and isinstance(raw, bytes), "FACTORY_JSON")
    need(len(raw) <= limit, "FACTORY_LIMIT")

    def pairs(rows):
        result = {}
        for key, value in rows:
            need(key not in result, "FACTORY_JSON")
            result[key] = value
        return result

    def constant(_value):
        raise FactoryError("FACTORY_JSON")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
    except (ValueError, UnicodeError, RecursionError, OverflowError):
        raise FactoryError("FACTORY_JSON") from None
    _json_tree(value)
    return value


def keys(value, expected):
    need(isinstance(value, dict) and set(value) == set(expected))


def text(value):
    need(isinstance(value, str) and bool(value.strip()) and len(value) <= 4000)


def identity(value):
    need(isinstance(value, str) and len(value) <= 80
         and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value) is not None)


def timestamp(value):
    need(isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})", value
    ) is not None, "FACTORY_DATE")
    # datetime accepts offsets whose minutes overflow; RFC3339 does not.
    if value[-1].lower() != "z":
        need(int(value[-5:-3]) <= 23 and int(value[-2:]) <= 59, "FACTORY_DATE")
    try:
        return dt.datetime.fromisoformat(value[:-1] + "+00:00" if value[-1].lower() == "z" else value)
    except ValueError:
        raise FactoryError("FACTORY_DATE") from None


def approval(value):
    keys(value, ("by", "at", "reference"))
    text(value["by"])
    timestamp(value["at"])
    text(value["reference"])


def parts(value):
    need(isinstance(value, str) and 0 < len(value) <= 260, "FACTORY_PATH")
    result = tuple(value.replace("\\", "/").split("/"))
    for part in result:
        need(part not in ("", ".", "..") and not part.endswith((" ", "."))
             and re.search(r'[<>:"|?*\x00-\x1f\x7f-\x9f\ud800-\udfff]', part) is None
             and re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?", part) is None,
             "FACTORY_PATH")
    return result


def portable(value):
    return "/".join(parts(value))


def path_key(value):
    return portable(value).casefold()


def claim_path(spellings, value, *, repeat=False):
    key = path_key(value)
    if key in spellings:
        need(repeat and spellings[key] == value, "FACTORY_PATH_COLLISION")
    else:
        spellings[key] = value
    return portable(value)


def _ordinary(info):
    need(not stat.S_ISLNK(info.st_mode) and not getattr(info, "st_file_attributes", 0) & 0x400,
         "FACTORY_LINK")


def plain_path(path, *, missing=False):
    need(isinstance(path, (str, os.PathLike)), "FACTORY_PATH")
    raw = os.fspath(path)
    need(isinstance(raw, str) and "\x00" not in raw
         and not raw.startswith(("\\\\?\\", "\\\\.\\")), "FACTORY_PATH")
    given = Path(raw)
    need(".." not in given.parts, "FACTORY_PATH")
    absolute = given.absolute()
    current = Path(absolute.anchor)
    try:
        _ordinary(current.lstat())
        for index, part in enumerate(absolute.parts[1:]):
            current /= part
            try:
                info = current.lstat()
            except FileNotFoundError:
                need(missing and index == len(absolute.parts) - 2, "FACTORY_FILE")
                return current
            _ordinary(info)
        return absolute.resolve(strict=True)
    except OSError:
        raise FactoryError("FACTORY_FILE") from None


def read(root, relative, limit):
    need(type(limit) is int and limit >= 0, "FACTORY_LIMIT")
    root = plain_path(root)
    path = plain_path(root.joinpath(*parts(relative)))
    need(path.is_relative_to(root), "FACTORY_PATH")
    try:
        before = path.lstat()
        _ordinary(before)
        need(stat.S_ISREG(before.st_mode), "FACTORY_FILE")
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            need(stat.S_ISREG(opened.st_mode)
                 and (before.st_dev, before.st_ino) == (opened.st_dev, opened.st_ino), "FACTORY_FILE")
            need(opened.st_size <= limit, "FACTORY_LIMIT")
            raw = stream.read(limit + 1)
            need(len(raw) <= limit, "FACTORY_LIMIT")
            return raw
    except OSError:
        raise FactoryError("FACTORY_FILE") from None


_KEYWORDS = {
    "$schema", "$id", "title", "description", "$defs", "$ref", "type", "additionalProperties",
    "required", "properties", "const", "enum", "oneOf", "allOf", "if", "then", "else",
    "minItems", "maxItems", "uniqueItems", "items", "minLength", "maxLength", "pattern", "format",
}


def _vocabulary(rule, depth=0):
    need(depth <= 128 and isinstance(rule, dict) and set(rule) <= _KEYWORDS, "FACTORY_SCHEMA")
    if "$ref" in rule:
        need(isinstance(rule["$ref"], str)
             and re.fullmatch(r"#/\$defs/[A-Za-z0-9_-]+", rule["$ref"]) is not None, "FACTORY_SCHEMA")
    if "format" in rule:
        need(rule["format"] in ("date-time", "date"), "FACTORY_SCHEMA")
    for field in ("properties", "$defs"):
        for child in rule.get(field, {}).values():
            _vocabulary(child, depth + 1)
    for field in ("oneOf", "allOf"):
        for child in rule.get(field, []):
            _vocabulary(child, depth + 1)
    for field in ("if", "then", "else", "items"):
        if field in rule:
            _vocabulary(rule[field], depth + 1)


def conforms(rule, value, root=None, depth=0):
    """Evaluate only the pinned intake vocabulary, never resolve external schemas."""
    need(depth <= 128, "FACTORY_SCHEMA")
    if depth == 0:
        _vocabulary(rule)
    root = rule if root is None else root

    def match(child, item=value):
        return conforms(child, item, root, depth + 1)

    if "$ref" in rule:
        name = rule["$ref"].split("/")[-1]
        need(name in root.get("$defs", {}), "FACTORY_SCHEMA")
        if not match(root["$defs"][name]):
            return False
    kind = rule.get("type")
    types = {"object": isinstance(value, dict), "array": isinstance(value, list),
             "string": isinstance(value, str), "integer": type(value) is int,
             "number": type(value) in (int, float), "boolean": type(value) is bool,
             "null": value is None}
    if kind is not None:
        need(kind in types, "FACTORY_SCHEMA")
        if not types[kind]:
            return False
    if "const" in rule and encoded(value) != encoded(rule["const"]):
        return False
    if "enum" in rule and all(encoded(value) != encoded(item) for item in rule["enum"]):
        return False
    if "oneOf" in rule and sum(match(child) for child in rule["oneOf"]) != 1:
        return False
    if "allOf" in rule and not all(match(child) for child in rule["allOf"]):
        return False
    if "if" in rule:
        branch = "then" if match(rule["if"]) else "else"
        if branch in rule and not match(rule[branch]):
            return False
    if isinstance(value, dict):
        properties = rule.get("properties", {})
        if not set(rule.get("required", [])) <= value.keys():
            return False
        if rule.get("additionalProperties") is False and not value.keys() <= properties.keys():
            return False
        if any(not match(properties[key], item) for key, item in value.items() if key in properties):
            return False
    if isinstance(value, list):
        if not rule.get("minItems", 0) <= len(value) <= rule.get("maxItems", len(value)):
            return False
        if rule.get("uniqueItems") and len({encoded(item) for item in value}) != len(value):
            return False
        if "items" in rule and not all(match(rule["items"], item) for item in value):
            return False
    if isinstance(value, str):
        if not rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", len(value)):
            return False
        if "pattern" in rule and re.search(rule["pattern"], value) is None:
            return False
        if "format" in rule:
            try:
                if rule["format"] == "date-time":
                    timestamp(value)
                else:
                    need(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None, "FACTORY_DATE")
                    dt.date.fromisoformat(value)
            except (FactoryError, ValueError):
                return False
    return True
