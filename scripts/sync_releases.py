#!/usr/bin/env python3
"""Pull published GitHub Releases from each EHS Dashboard service repo and
write them as markdown release notes for the public changelog aggregator.

Phase 2 of the release-notes migration: this replaces the legacy
repository_dispatch + AI-rewrite pipeline. For Phase 2 it writes to a
parallel directory (--output-dir, default releases-next/) so the existing
live aggregator (releases/, data/releases.json) is not disturbed. Phase 3
will cut over to releases/.

For each tracked service:
1. Fetch the most recent ~50 Releases via the GitHub API.
2. Filter out drafts (drafts stay invisible).
3. Idempotently write one .md per Release at <output-dir>/<service>_<tag>.md
   with frontmatter compatible with scripts/build_releases_json.py.

Required env vars:
- GH_TOKEN: a token with read access to each tracked service repo's contents.
  In CI this is sourced from REPO_READER_TOKEN, the same secret the legacy
  aggregator uses for cross-repo `gh` calls.

Idempotency:
- File contents are normalized; existing files are only rewritten when
  the new content differs. Stable content => no commits => no needless CI.

Dependencies: stdlib only. No pip install needed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

GITHUB_API = "https://api.github.com"
USER_AGENT = "ehs-dashboard-sync-releases/1.0"
ACCEPT = "application/vnd.github+json"
API_VERSION = "2022-11-28"

# Tracked service repos. (component slug used in filenames, GitHub owner/repo).
TRACKED_SERVICES: list[tuple[str, str]] = [
    ("dashboard-api", "Higher-Elevation-Software/dashboard-api"),
    ("dashboard-webapp", "Higher-Elevation-Software/dashboard-webapp"),
    ("dashboard-ui", "Higher-Elevation-Software/dashboard-ui"),
]


def env(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        sys.exit(f"missing required env var: {name}")
    return val


def fetch_releases(token: str, repo: str, per_page: int = 50) -> list[dict]:
    req = urllib.request.Request(
        f"{GITHUB_API}/repos/{repo}/releases?per_page={per_page}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": ACCEPT,
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def to_deploy_time(published_at: str) -> str:
    """ISO8601 (e.g. 2026-05-04T14:30:00Z) -> YYYYMMDDTHHMMSSZ."""
    if not published_at:
        return ""
    parsed = dt.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    return parsed.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sanitize_tag(tag: str) -> str:
    """Make a tag safe to use as a filename component."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", tag).strip("-") or "untagged"


def render_release_md(component: str, release: dict) -> str:
    name = (release.get("name") or release.get("tag_name") or "").strip() or "Untitled"
    body = (release.get("body") or "").strip()
    sha = release.get("target_commitish") or ""
    deploy_time = to_deploy_time(release.get("published_at") or "")
    tag = release.get("tag_name") or ""
    html_url = release.get("html_url") or ""
    is_prerelease = bool(release.get("prerelease"))

    # Hide prereleases from the public feed without dropping them entirely.
    user_facing = "false" if is_prerelease else "true"

    # category=Update is the validator-allowed bucket for auto-generated Release
    # entries that aggregate multiple PRs across categories. The display
    # normalizer in build_releases_json.py maps it to "Improvement".
    # Future enhancement: parse PR labels in the body to pick a dominant category.
    lines = [
        "---",
        f"component: {component}",
        f"sha: {sha}",
        f"deploy_time: {deploy_time}",
        "environment: production",
        "category: Update",
        f"user_facing: {user_facing}",
        f"release_tag: {tag}",
        f"release_url: {html_url}",
        "---",
        "",
        f"# {name}",
        "",
    ]
    if body:
        lines.append(body)
        lines.append("")
    return "\n".join(lines)


def write_if_changed(path: Path, content: str) -> bool:
    """Write content to path only if different. Returns True if written."""
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def sync_service(token: str, component: str, repo: str, output_dir: Path) -> tuple[int, int]:
    """Sync one service repo. Returns (written, eligible_total)."""
    releases = fetch_releases(token, repo)
    eligible = [r for r in releases if not r.get("draft")]
    written = 0
    for release in eligible:
        tag = release.get("tag_name") or ""
        slug = sanitize_tag(tag)
        path = output_dir / f"{component}_{slug}.md"
        content = render_release_md(component, release)
        if write_if_changed(path, content):
            written += 1
            print(f"  wrote {path.name}")
    return written, len(eligible)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync GitHub Releases from EHS Dashboard service repos."
    )
    parser.add_argument(
        "--output-dir",
        default="releases-next",
        help="Directory (relative to --root) to write release markdown files. "
             "Defaults to releases-next/ for Phase 2 parallel comparison.",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root. Defaults to the parent of this script's directory.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    output_dir = root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    token = env("GH_TOKEN")
    total_written = 0
    total_eligible = 0
    for component, repo in TRACKED_SERVICES:
        print(f"Syncing {repo} ({component})")
        try:
            written, eligible = sync_service(token, component, repo, output_dir)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"  ERROR: GitHub API {e.code}: {body}", file=sys.stderr)
            return 1
        print(f"  {written} updated of {eligible} published Releases")
        total_written += written
        total_eligible += eligible
    print(f"Total: {total_written} updated of {total_eligible} published Releases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
