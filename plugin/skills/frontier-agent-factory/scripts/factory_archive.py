# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Bounded passive foundation data and deterministic local archive publication."""
import datetime as dt
import io
import os
from pathlib import Path
import stat
import struct
import tempfile
import zipfile
import zlib

from factory_common import FactoryError, MIB, digest, need, parts, plain_path, timestamp
from zip_stream import raw_member

FORBIDDEN = {".git", ".factory-local", "node_modules", "__pycache__", ".venv", "venv",
             ".pytest_cache", ".ruff_cache", ".azure", ".aws", ".ssh", ".env",
             ".ds_store", "thumbs.db"}


def safe_name(name):
    components = parts(name)
    need(not any(part.casefold() in FORBIDDEN or part.casefold().endswith((".pyc", ".pyo"))
                 for part in components), "FACTORY_STATE")
    return "/".join(components)


def foundation_shape(name, *, directory=False):
    components = parts(name)
    folded = tuple(part.casefold() for part in components)
    for root in (("docs", "intake", "records"), ("solutions",)):
        if folded[:len(root)] != root:
            continue
        if len(components) == len(root):
            need(directory, "FACTORY_TEMPLATE")
        else:
            need(not directory and len(components) == len(root) + 1
                 and Path(components[-1]).suffix.lower() == ".md", "FACTORY_TEMPLATE")


def _claim(seen, name, *, directory=False):
    """Track implicit directories separately from explicit members and files."""
    components = name.split("/")
    for index in range(1, len(components) + 1):
        spelling = "/".join(components[:index])
        key = spelling.casefold()
        leaf = index == len(components)
        is_directory = not leaf or directory
        if key in seen:
            previous, was_directory, explicit = seen[key]
            need(previous == spelling and was_directory and is_directory
                 and not (leaf and explicit), "FACTORY_COLLISION")
        else:
            explicit = False
        seen[key] = (spelling, is_directory, explicit or leaf)


def capacity(entries, *, expanded=128 * MIB, members=4096):
    need(isinstance(entries, dict), "FACTORY_MODE")
    need(type(expanded) is int and expanded >= 0 and type(members) is int and members >= 0,
         "FACTORY_LIMIT")
    need(len(entries) <= members, "FACTORY_LIMIT")
    seen, total = {}, 0
    for name, value in entries.items():
        name = safe_name(name)
        need(isinstance(value, tuple) and len(value) == 2, "FACTORY_MODE")
        raw, mode = value
        need(isinstance(raw, bytes) and type(mode) is int and mode in (0o644, 0o755), "FACTORY_MODE")
        _claim(seen, name)
        total += len(raw)
        need(total <= expanded, "FACTORY_LIMIT")


def foundation(raw, prefix, profile):
    need(isinstance(raw, bytes) and 0 < len(raw) <= 32 * MIB, "FACTORY_LIMIT")
    prefix = safe_name(prefix.rstrip("/\\")) + "/" if prefix else ""
    result = {}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members = archive.infolist()
            need(len(members) <= 4096, "FACTORY_LIMIT")
            seen, total = {}, 0
            for entry in members:
                need(entry.filename == entry.orig_filename and not entry.flag_bits & (1 | 64), "FACTORY_ZIP")
                name = entry.filename.replace("\\", "/")
                directory = name.endswith("/")
                full = safe_name(name[:-1] if directory else name)
                _claim(seen, full, directory=directory)
                need(".gitmodules" not in (part.casefold() for part in full.split("/")), "FACTORY_TEMPLATE")
                mode = entry.external_attr >> 16
                kind = stat.S_IFMT(mode)
                need(kind in (0, stat.S_IFREG, stat.S_IFDIR)
                     and not entry.external_attr & 0x400, "FACTORY_LINK")
                need(kind == 0 or (kind == stat.S_IFDIR) == directory, "FACTORY_MODE")
                need(entry.file_size <= 64 * MIB - total, "FACTORY_LIMIT")
                # The pure helper checks the whole raw span before ZipExtFile
                # can hide an oversized stream behind a forged declared length.
                total += raw_member(raw, entry, 64 * MIB - total)
                if prefix:
                    need(name.startswith(prefix), "FACTORY_TEMPLATE")
                    name = name[len(prefix):]
                if directory:
                    need(entry.file_size == 0, "FACTORY_ZIP")
                    if name:
                        foundation_shape(name.rstrip("/"), directory=True)
                    # Keep ZipFile's local-name and overlap validation for directories too.
                    need(archive.read(entry) == b"", "FACTORY_ZIP")
                    continue
                name = safe_name(name)
                foundation_shape(name)
                permissions = stat.S_IMODE(mode) if mode else 0o644
                need(permissions in (0o644, 0o755), "FACTORY_MODE")
                result[name] = (archive.read(entry), permissions)
        capacity(result, expanded=64 * MIB)
        need(isinstance(profile, dict) and isinstance(profile.get("required"), list)
             and all(isinstance(name, str) for name in profile["required"]), "FACTORY_TEMPLATE")
        need(set(profile["required"]) <= set(result)
             and {"docs/intake/intake.schema.json", "tools/intake.py"} <= set(result), "FACTORY_TEMPLATE")
        need(digest(result["docs/intake/intake.schema.json"][0]) == profile.get("intake_schema_sha256")
             and digest(result["tools/intake.py"][0]) == profile.get("intake_validator_sha256"),
             "FACTORY_COMPATIBILITY")
        return result
    except FactoryError:
        raise
    except (ValueError, OSError, RuntimeError, EOFError, NotImplementedError,
            zipfile.BadZipFile, struct.error, zlib.error):
        raise FactoryError("FACTORY_ZIP") from None


def archive_bytes(entries, created_at):
    capacity(entries)
    try:
        time = timestamp(created_at).astimezone(dt.timezone.utc)
    except (ValueError, OverflowError):
        raise FactoryError("FACTORY_DATE") from None
    need(1980 <= time.year <= 2107, "FACTORY_DATE")
    stamp = (time.year, time.month, time.day, time.hour, time.minute, time.second)
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", allowZip64=False) as archive:
        for name, (raw, permissions) in sorted(entries.items(), key=lambda row: safe_name(row[0])):
            info = zipfile.ZipInfo(safe_name(name), stamp)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | permissions) << 16
            info.compress_type = zipfile.ZIP_STORED
            archive.writestr(info, raw)
    return out.getvalue()


def _destination(output):
    output = plain_path(output, missing=True)
    try:
        need(output.parent.is_dir(), "FACTORY_OUTPUT")
        try:
            info = output.lstat()
        except FileNotFoundError:
            return output
        need(stat.S_ISREG(info.st_mode), "FACTORY_OUTPUT")
    except OSError:
        raise FactoryError("FACTORY_IO") from None
    return output


def publish(output, raw):
    """Publish completed archive bytes; input-inventory alias checks belong to the caller."""
    need(isinstance(raw, bytes), "FACTORY_ZIP")
    # Maximum expanded bytes plus bounded local/central headers and UTF-8 names.
    need(len(raw) <= 128 * MIB + 4096 * (2 * 260 * 4 + 100) + 22, "FACTORY_LIMIT")
    output = _destination(output)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".factory-", suffix=".tmp",
                                         dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            need(stream.write(raw) == len(raw), "FACTORY_IO")
            stream.flush()
            os.fsync(stream.fileno())
        _destination(output)
        os.replace(temporary, output)
    except OSError:
        raise FactoryError("FACTORY_IO") from None
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                raise FactoryError("FACTORY_IO") from None
