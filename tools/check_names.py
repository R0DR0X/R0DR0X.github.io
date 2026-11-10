#!/usr/bin/env python3
"""Scan files for denylisted names (case-insensitive, whole words).

Usage: check_names.py --denylist FILE PATH...

Directories are scanned recursively. HTML entities are decoded and tags are
ignored, so "ACME&nbsp;Foods" matches "Acme Foods". PDFs are read through
pdftotext. Prints "name found: <term> in <file>" per hit and exits 1, or
"ok: no denylisted names" and exits 0. Exits 2 when a file cannot be read.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TAG = re.compile(r"<[^>]*>")


def load_terms(path):
    terms = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def pattern(term):
    words = [re.escape(word) for word in term.split()]
    return re.compile(r"(?<!\w)" + r"\s+".join(words) + r"(?!\w)", re.IGNORECASE)


def iter_files(paths):
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            for dirpath, dirnames, filenames in os.walk(path):
                dirnames.sort()
                for name in sorted(filenames):
                    yield Path(dirpath) / name
        else:
            yield path


def read_text(path):
    """Return the searchable text of a file, None for binary files."""
    if path.suffix.lower() == ".pdf":
        pdftotext = shutil.which("pdftotext")
        if not pdftotext:
            raise OSError("pdftotext not found")
        result = subprocess.run([pdftotext, "-q", str(path), "-"], capture_output=True, text=True)
        if result.returncode != 0:
            raise OSError(f"pdftotext failed ({result.returncode})")
        return result.stdout
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    if path.suffix.lower() in (".html", ".htm", ".xml", ".svg"):
        # Keep the raw source (attributes, scripts) and the decoded visible text.
        return raw + "\n" + html.unescape(TAG.sub(" ", raw))
    return raw


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan files for denylisted names.")
    parser.add_argument("--denylist", required=True, help="file with one name per line; # starts a comment")
    parser.add_argument("paths", nargs="+", help="files or directories to scan")
    args = parser.parse_args(argv)

    terms = [(term, pattern(term)) for term in load_terms(args.denylist)]
    hits = 0
    for path in iter_files(args.paths):
        try:
            text = read_text(path)
        except OSError as exc:
            print(f"check error: {path}: {exc}", file=sys.stderr)
            return 2
        if text is None:
            continue
        for term, regex in terms:
            if regex.search(text):
                print(f"name found: {term} in {path}")
                hits += 1
    if hits:
        return 1
    print("ok: no denylisted names")
    return 0


if __name__ == "__main__":
    sys.exit(main())
