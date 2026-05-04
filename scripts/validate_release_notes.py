#!/usr/bin/env python3
"""
Validate release note markdown files in releases/.

Goals:
- Prevent hidden/bidi/control characters from landing in the repo.
- Enforce a minimal frontmatter/schema so aggregates are reliable.

This is intentionally lightweight (no external deps).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable, List, Tuple


DISALLOWED_RANGES: List[Tuple[int, int]] = [
    (0x202A, 0x202E),  # bidi embeddings/overrides
    (0x2066, 0x2069),  # bidi isolates
]
DISALLOWED_SINGLE = {0x200E, 0x200F, 0x061C, 0xFEFF}  # LRM/RLM/ALM/BOM

LATEST_DEPLOY_RE = re.compile(r"^\d{8}T\d{6}Z$")
ALLOWED_CATEGORIES = {"Feature", "Improvement", "Security", "Internal", "Update"}


def is_disallowed_cp(cp: int) -> bool:
    if cp in DISALLOWED_SINGLE:
        return True
    for a, b in DISALLOWED_RANGES:
        if a <= cp <= b:
            return True
    # C0 controls (except newline/tab)
    if cp < 0x20 and cp not in (0x0A, 0x09):
        return True
    if cp == 0x7F:
        return True
    return False


def find_disallowed_chars(text: str) -> List[Tuple[int, int]]:
    """
    Returns list of (index, codepoint) for disallowed chars.
    """
    out: List[Tuple[int, int]] = []
    for i, ch in enumerate(text):
        cp = ord(ch)
        if is_disallowed_cp(cp):
            out.append((i, cp))
    return out


def split_frontmatter(md: str) -> Tuple[str, str]:
    md = md.lstrip()
    if not md.startswith("---\n"):
        return "", md
    parts = md.split("---", 2)
    if len(parts) < 3:
        return "", md
    fm = parts[1]
    body = parts[2].lstrip("\n")
    return fm, body


def fm_get_scalar(fm_lines: Iterable[str], key: str) -> str:
    prefix = f"{key}:"
    for ln in fm_lines:
        if ln.startswith(prefix):
            return ln.split(":", 1)[1].strip()
    return ""


def validate_file(path: Path) -> List[str]:
    problems: List[str] = []
    text = path.read_text(encoding="utf-8")

    bad = find_disallowed_chars(text)
    for _, cp in bad[:10]:
        problems.append(f"disallowed_char: U+{cp:04X}")
    if len(bad) > 10:
        problems.append(f"disallowed_char: ... ({len(bad)} total)")

    fm, body = split_frontmatter(text)
    if not fm:
        problems.append("missing_frontmatter")
        return problems

    fm_lines = [ln.rstrip("\n") for ln in fm.splitlines() if ln.strip()]

    latest = fm_get_scalar(fm_lines, "latest_deploy") or fm_get_scalar(fm_lines, "deploy_time")
    if not latest or not LATEST_DEPLOY_RE.match(latest):
        problems.append(f"invalid_latest_deploy: {latest or 'missing'}")

    env = fm_get_scalar(fm_lines, "environment")
    if not env:
        problems.append("missing_environment")

    cat = fm_get_scalar(fm_lines, "category")
    if cat and cat not in ALLOWED_CATEGORIES:
        problems.append(f"invalid_category: {cat}")

    uf = fm_get_scalar(fm_lines, "user_facing")
    if uf and uf not in {"true", "false"}:
        problems.append(f"invalid_user_facing: {uf}")

    # Basic title presence
    if not re.search(r"^#\s+.+", body, flags=re.MULTILINE):
        problems.append("missing_h1_title")

    return problems


def expand_paths(args_paths: List[str]) -> List[Path]:
    if not args_paths:
        return sorted(Path("releases").glob("*.md"))
    out: List[Path] = []
    for p in args_paths:
        pp = Path(p)
        if pp.is_dir():
            out.extend(sorted(pp.glob("*.md")))
        else:
            out.append(pp)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paths", nargs="*", help="Files or directories to validate (defaults to releases/*.md).")
    ns = ap.parse_args()

    paths = expand_paths(ns.paths or [])
    if not paths:
        print("No release notes found to validate.", file=sys.stderr)
        return

    failed = False
    for p in paths:
        probs = validate_file(p)
        if probs:
            failed = True
            for pr in probs:
                print(f"{p}: {pr}", file=sys.stderr)

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

