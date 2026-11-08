#!/usr/bin/env python3
# Copyright (c) 2026 Urs Rüegg
# SPDX-License-Identifier: MIT
"""Customer-neutrality scan: the repository and every package must name no real customer.

The plugin's demo company is the fictitious Caldova Industrial AG. Real customer names from Innovation
Hub engagements must never enter the repository, the packages or the showcase site.

The denylist (tools/neutrality-denylist.txt) holds SHA-256 hashes of normalised terms, not the names
themselves, so the list does not disclose which customers the Hub works with. A term is one word or two
words (for example a first and last name of a company). Matching is case-insensitive and whole-word.

  python tools/neutrality.py scan [PATH ...] [--zips]   scan tracked text files (default) or the given paths;
                                                        --zips also scans text members of .zip archives
  python tools/neutrality.py hash "Term"                print the hash line for a term
  python tools/neutrality.py add "Term"                 append a term's hash to the denylist
  python tools/neutrality.py check-text                 read text on stdin, exit 1 on a hit (used by hooks)

Extra terms that should not even be hashed into the repository can come from the environment variable
FRONTIER_NEUTRALITY_EXTRA (comma-separated plain terms), e.g. from a CI secret. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fe_lib import ROOT, is_text, tracked_files  # noqa: E402

DENYLIST = Path(__file__).resolve().parent / "neutrality-denylist.txt"
SALT = b"frontier-neutrality/v1\x00"
TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
MAX_BYTES = 8 * 1024 * 1024


def norm(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def term_hash(term: str) -> str:
    words = TOKEN.findall(norm(term))
    if not 1 <= len(words) <= 2:
        raise ValueError("a term is one or two words")
    return hashlib.sha256(SALT + " ".join(words).encode("utf-8")).hexdigest()


def load_hashes() -> set[str]:
    hashes = set()
    if DENYLIST.exists():
        for line in DENYLIST.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if re.fullmatch(r"[0-9a-f]{64}", line):
                hashes.add(line)
    for extra in filter(None, (x.strip() for x in os.environ.get("FRONTIER_NEUTRALITY_EXTRA", "").split(","))):
        try:
            hashes.add(term_hash(extra))
        except ValueError:
            pass
    return hashes


def find_terms(text: str, hashes: set[str] | None = None) -> list[tuple[int, str]]:
    """Return (line number, matched words) for every denylisted unigram or bigram in text."""
    hashes = load_hashes() if hashes is None else hashes
    hits: list[tuple[int, str]] = []
    if not hashes:
        return hits
    for lineno, line in enumerate(text.splitlines(), 1):
        words = TOKEN.findall(norm(line))
        prev = None
        for w in words:
            for cand in ((w,) if prev is None else (w, prev + " " + w)):
                if hashlib.sha256(SALT + cand.encode("utf-8")).hexdigest() in hashes:
                    hits.append((lineno, cand))
            prev = w
    return hits


def scan_paths(paths: list[Path], zips: bool = False) -> list[str]:
    hashes = load_hashes()
    findings = []
    for p in paths:
        if p.resolve() == DENYLIST:
            continue
        try:
            rel = p.relative_to(ROOT).as_posix()
        except ValueError:
            rel = str(p)
        if zips and p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p) as zf:
                for info in zf.infolist():
                    if info.is_dir() or info.file_size > MAX_BYTES:
                        continue
                    member = Path(info.filename)
                    data = zf.read(info)
                    if member.suffix.lower() == ".zip":
                        import io
                        with zipfile.ZipFile(io.BytesIO(data)) as inner:
                            for ii in inner.infolist():
                                if not ii.is_dir() and is_text(Path(ii.filename)) and ii.file_size <= MAX_BYTES:
                                    for ln, w in find_terms(inner.read(ii).decode("utf-8", "replace"), hashes):
                                        findings.append(f"{rel}!{info.filename}!{ii.filename}:{ln}: '{w}'")
                        continue
                    if is_text(member):
                        for ln, w in find_terms(data.decode("utf-8", "replace"), hashes):
                            findings.append(f"{rel}!{info.filename}:{ln}: '{w}'")
            continue
        if not is_text(p) or p.stat().st_size > MAX_BYTES:
            continue
        for ln, w in find_terms(p.read_text(encoding="utf-8", errors="replace"), hashes):
            findings.append(f"{rel}:{ln}: '{w}'")
        # file names count too
        for ln, w in find_terms(rel, hashes):
            findings.append(f"{rel} (path): '{w}'")
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("scan")
    sc.add_argument("paths", nargs="*")
    sc.add_argument("--zips", action="store_true", help="also scan text members of zip archives")
    h = sub.add_parser("hash")
    h.add_argument("term")
    ad = sub.add_parser("add")
    ad.add_argument("term")
    sub.add_parser("check-text")
    a = ap.parse_args(argv)
    if a.cmd == "hash":
        print(term_hash(a.term))
        return 0
    if a.cmd == "add":
        line = term_hash(a.term)
        existing = load_hashes()
        if line in existing:
            print("already in the denylist")
            return 0
        with open(DENYLIST, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
        print("added (the plain term is not stored)")
        return 0
    if a.cmd == "check-text":
        hits = find_terms(sys.stdin.read())
        for ln, w in hits:
            print(f"line {ln}: '{w}'")
        return 1 if hits else 0
    if not load_hashes():
        print("ERROR: the denylist is empty")
        return 2
    if a.paths:
        paths = []
        for raw in a.paths:
            p = Path(raw)
            p = p if p.is_absolute() else (Path.cwd() / p)
            paths.extend(sorted(x for x in p.rglob("*") if x.is_file()) if p.is_dir() else [p])
    else:
        paths = tracked_files()
    findings = scan_paths(paths, zips=a.zips)
    for f in findings:
        print("CUSTOMER NAME: " + f)
    print(f"neutrality scan: {len(paths)} files, {len(findings)} findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
