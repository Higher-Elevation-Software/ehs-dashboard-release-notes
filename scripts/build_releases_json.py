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
    data = {}
    for line in lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            data[key.strip()] = value.strip()
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
        if stripped.startswith("**Component:**") or stripped.startswith("**Date:**") or stripped.startswith("**Environment:**"):
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

    summary = extract_summary(body_lines)

    raw_category = front_matter.get("category", "Update")
    norm_category = CATEGORY_MAP.get(raw_category.lower(), "Improvement")

    return Release(
        path=path.relative_to(root),
        component=front_matter.get("component", "unknown"),
        sha=front_matter.get("sha", ""),
        deploy_time=front_matter.get("deploy_time", ""),
        environment=front_matter.get("environment", ""),
        category=raw_category,
        display_category=norm_category,
        user_facing=str(front_matter.get("user_facing", "true")).lower() != "false",
        title=title or path.stem,
        summary=summary,
    )


def load_releases(root: Path) -> List[Release]:
    releases_dir = root / "releases"
    items: List[Release] = []
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
            }
            for r in items
        ],
    }


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    items = load_releases(root)
    payload = to_payload(items)

    out_dir = root / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "releases.json"
    out_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out_file} with {len(items)} releases")


if __name__ == "__main__":
    main()
