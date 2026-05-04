"""Generate a releases.json aggregate from markdown release notes.

This script is intentionally dependency-free so it can run in CI without
installing extra packages. It expects release notes in `releases/*.md` with
front matter fields like `component`, `sha`, `deploy_time`, `environment`,
`category`, and `user_facing`, followed by a `# Title` heading and a summary
paragraph.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


RE_FRONT_MATTER = re.compile(r"^---\s*$")

# Map incoming categories to a normalized set while preserving the original.
CATEGORY_MAP = {
    "feature": "Feature",
    "improvement": "Improvement",
    "security": "Security",
    "internal": "Internal",
    "update": "Improvement",
    "fix": "Improvement",
}


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


@dataclass
class Release:
    path: Path
    component: str
    sha: str
    deploy_time: str
    environment: str
    category: str
    display_category: str
    user_facing: bool
    title: str
    summary: str
    deployments: list

    @property
    def id(self) -> str:
        return self.path.stem

    @property
    def short_sha(self) -> str:
        return self.sha[:7]

    @property
    def date(self) -> Optional[str]:
        # Expected format: YYYYMMDDTHHMMSSZ
        try:
            dt = _dt.datetime.strptime(self.deploy_time, "%Y%m%dT%H%M%SZ")
            return dt.date().isoformat()
        except Exception:
            return None


def parse_front_matter(lines: Iterable[str]) -> dict:
    """Parse YAML front matter including lists and nested structures."""
    data = {}
    current_key = None
    current_list = None
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        
        # Check for list item starting with "- "
        if stripped.startswith("- "):
            if current_list is not None:
                # Parse list item
                item_text = stripped[2:]  # Remove "- "
                if ":" in item_text:
                    # Start of a new dict in list
                    current_list.append({})
                    key, _, value = item_text.partition(":")
                    current_list[-1][key.strip()] = _unquote(value)
                else:
                    # List of strings
                    current_list.append(_unquote(item_text))
            continue
        
        # Check for continuation of list dict (indented property)
        if line.startswith("  ") and not line.startswith("   ") and current_list is not None:
            if ":" in stripped:
                # This is a property of the current list item
                if current_list and isinstance(current_list[-1], dict):
                    key, _, value = stripped.partition(":")
                    current_list[-1][key.strip()] = _unquote(value)
            continue
        
        # Check for key-value pair at root level
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            
            # Check if this might be a list (empty value or next line is a list)
            if not value or value == "[]":
                data[key] = []
                current_key = key
                current_list = data[key]
            else:
                # Simple key-value
                data[key] = _unquote(value)
                current_key = key
                current_list = None
    
    return data


def extract_summary(body_lines: List[str]) -> str:
    # Remove metadata lines like **Component:** ...
    cleaned = []
    for line in body_lines:
        stripped = line.strip()
        if not stripped:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        if stripped.startswith("# "):
            continue
        if (
            stripped.startswith("**Component:**")
            or stripped.startswith("**Date:**")
            or stripped.startswith("**Environment:**")
            or stripped.startswith("**Category:**")
        ):
            continue
        if stripped.startswith("_More details"):
            continue
        cleaned.append(stripped)

    # Grab first non-empty block as summary
    block: List[str] = []
    for line in cleaned:
        if line == "":
            if block:
                break
            continue
        block.append(line)
    return " ".join(block).strip()


def parse_release(path: Path, root: Path) -> Optional[Release]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # Parse front matter
    if not lines or not RE_FRONT_MATTER.match(lines[0]):
        return None

    try:
        end_idx = next(i for i, line in enumerate(lines[1:], start=1) if RE_FRONT_MATTER.match(line))
    except StopIteration:
        return None

    front_matter = parse_front_matter(lines[1:end_idx])
    body_lines = lines[end_idx + 1 :]

    # Title is first H1 after front matter
    title = ""
    for line in body_lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    
    # Strip HES-XXX: prefix from title if present
    title = re.sub(r'^hes-\d+:\s*', '', title, flags=re.IGNORECASE)

    summary = extract_summary(body_lines)

    raw_category = front_matter.get("category", "Update")
    norm_category = CATEGORY_MAP.get(raw_category.lower(), "Improvement")

    # Prefer explicit `component` written by the workflow. For aggregated
    # ISSUE_HES-* notes, the workflow also writes a `components` list, but we
    # expose the combined string via `component` for backward compatibility.
    component = front_matter.get("component", "").strip() or "unknown"
    
    # Extract deployments array (for multi-component releases)
    deployments = front_matter.get("deployments", [])
    # If no deployments array, use latest_deploy from frontmatter or fallback to deploy_time
    if not deployments:
        # For single-deployment releases, use the frontmatter sha/deploy_time
        latest_deploy = front_matter.get("latest_deploy") or front_matter.get("deploy_time", "")
        sha = front_matter.get("sha", "")
        if sha and latest_deploy:
            deployments = [{
                "component": component,
                "sha": sha,
                "deploy_time": latest_deploy
            }]

    return Release(
        path=path.relative_to(root),
        component=component,
        sha=front_matter.get("sha", ""),
        deploy_time=front_matter.get("latest_deploy") or front_matter.get("deploy_time", ""),
        environment=front_matter.get("environment", ""),
        category=raw_category,
        display_category=norm_category,
        user_facing=str(front_matter.get("user_facing", "true")).lower() != "false",
        title=title or path.stem,
        summary=summary,
        deployments=deployments,
    )


def load_releases(root: Path, source_dir: str = "releases") -> List[Release]:
    releases_dir = root / source_dir
    items: List[Release] = []
    if not releases_dir.exists():
        return items
    for path in sorted(releases_dir.glob("*.md")):
        release = parse_release(path, root)
        if release:
            items.append(release)
    # Newest first by deploy_time string (filename ordering matches)
    items.sort(key=lambda r: r.deploy_time, reverse=True)
    return items


def to_payload(items: List[Release]) -> dict:
    generated_at = _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "generated_at": generated_at,
        "items": [
            {
                "id": r.id,
                "title": r.title,
                "summary": r.summary,
                "component": r.component,
                "environment": r.environment,
                "category": r.category,
                "display_category": r.display_category,
                "user_facing": r.user_facing,
                "sha": r.sha,
                "short_sha": r.short_sha,
                "deploy_time": r.deploy_time,
                "date": r.date,
                "path": str(r.path).replace("\\", "/"),
                "deployments": r.deployments,
            }
            for r in items
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a releases JSON aggregate from markdown release notes.")
    parser.add_argument(
        "--include-internal",
        action="store_true",
        help="Include user_facing:false notes in the generated JSON.",
    )
    parser.add_argument(
        "--source-dir",
        default="releases",
        help="Directory (relative to repo root) to read markdown release notes from. Default: releases.",
    )
    parser.add_argument(
        "--output",
        default="data/releases.json",
        help="Path (relative to repo root) to write the aggregate JSON to. Default: data/releases.json.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    items = load_releases(root, source_dir=args.source_dir)
    if not args.include_internal:
        items = [it for it in items if it.user_facing]
    payload = to_payload(items)

    out_file = root / args.output
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_file} with {len(items)} releases (source: {args.source_dir})")


if __name__ == "__main__":
    main()
