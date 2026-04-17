#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from handoff_format import REQUIRED_SECTION_KEYS, SECTION_ORDER, extract_section_blocks, parse_frontmatter, parse_mapping_block

DEFAULT_ROOT = Path.home() / "0-handoff"
FILENAME_RE = re.compile(r"^(?P<stamp>\d{8}-\d{4})-(?P<project>[a-z0-9]+(?:-[a-z0-9]+)*)-(?P<topic>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
FRONTMATTER_ORDER = [
    "id",
    "created_at",
    "project_name",
    "workspace_root",
    "branch",
    "task_title",
    "status",
    "execution_mode",
    "user_gate",
    "brief_lang",
    "tags",
    "key_files",
    "next_step",
]
REQUIRED_METADATA_KEYS = [
    "id",
    "created_at",
    "project_name",
    "workspace_root",
    "task_title",
    "status",
    "execution_mode",
    "user_gate",
    "brief_lang",
    "tags",
    "key_files",
    "next_step",
]
SECTION_BLOCK_RE = re.compile(r"```handoff\n(.*?)\n```", re.DOTALL)


def fail(message: str) -> None:
    raise SystemExit(message)


def quote(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def dump_list(items: list[object]) -> str:
    return "\n".join(f"  - {quote(item)}" for item in items)


def render_frontmatter(metadata: dict[str, object]) -> str:
    lines = ["---"]
    seen: set[str] = set()
    for key in FRONTMATTER_ORDER:
        if key == "branch" and key not in metadata:
            continue
        if key not in metadata:
            continue
        seen.add(key)
        value = metadata[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.append(dump_list(value))
        else:
            lines.append(f"{key}: {quote(value)}")
    for key in sorted(metadata):
        if key in seen:
            continue
        value = metadata[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.append(dump_list(value))
        else:
            lines.append(f"{key}: {quote(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def extract_frontmatter_block(text: str) -> tuple[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    return text[: end + 5], text[end + 5 :]


def validate_filename(path: Path) -> tuple[str, datetime]:
    match = FILENAME_RE.match(path.name)
    if not match:
        fail("filename must match YYYYMMDD-HHMM-<project-slug>-<topic-slug>.md")
    stamp = match.group("stamp")
    return path.stem, datetime.strptime(stamp, "%Y%m%d-%H%M")


def validate_metadata(metadata: dict[str, object], report_id: str, created_at: datetime) -> dict[str, object]:
    missing = [key for key in REQUIRED_METADATA_KEYS if metadata.get(key) in (None, "", [], {})]
    if missing:
        fail(f"frontmatter missing required key(s): {', '.join(missing)}")
    if metadata.get("id") != report_id:
        fail("frontmatter id must equal the filename stem")
    if metadata.get("execution_mode") != "plan_then_wait":
        fail("execution_mode must be plan_then_wait")
    if metadata.get("user_gate") != "required":
        fail("user_gate must be required")
    workspace_root = metadata.get("workspace_root")
    if not isinstance(workspace_root, str) or not workspace_root.startswith("/"):
        fail("workspace_root must be an absolute path")
    if not str(metadata.get("project_name", "")).strip():
        fail("project_name must be non-empty")
    if not str(metadata.get("task_title", "")).strip():
        fail("task_title must be non-empty")
    tags = metadata.get("tags")
    if not isinstance(tags, list) or not tags:
        fail("tags must be a non-empty list")
    key_files = metadata.get("key_files")
    if not isinstance(key_files, list) or not key_files:
        fail("key_files must be a non-empty list")
    if len(str(metadata.get("next_step", "")).strip()) < 12:
        fail("next_step must be a concrete action")
    normalized = dict(metadata)
    normalized["created_at"] = created_at.strftime("%Y-%m-%d %H:%M")
    return normalized


def parse_section_payload(section_name: str, block: str) -> dict[str, object]:
    payload = parse_mapping_block(block)
    absent = [key for key in REQUIRED_SECTION_KEYS[section_name] if payload.get(key) in (None, "", [], {})]
    if absent:
        fail(f"{section_name} missing required key(s): {', '.join(absent)}")
    return payload


def validate_sections(body: str) -> None:
    sections = extract_section_blocks(body)
    if len(sections) != len(SECTION_ORDER):
        fail("report must contain exactly 8 canonical sections with fenced handoff blocks")
    for expected_index, expected_name in enumerate(SECTION_ORDER, start=1):
        section_index, section_name, block = sections[expected_index - 1]
        if section_index != expected_index or section_name != expected_name:
            fail("section headings must match the canonical order in handoff-schema.md")
        if len(SECTION_BLOCK_RE.findall(f"```handoff\n{block}\n```")) != 1:
            fail(f"{section_name} must contain exactly one fenced handoff block")
        payload = parse_section_payload(section_name, block)
        if section_name == "Goal DSL" and len(str(payload.get("PROJECT_MISSION", "")).strip()) < 20:
            fail("Goal DSL PROJECT_MISSION is too thin")
        if section_name == "Context DSL":
            inspirations = payload.get("INSPIRATIONS")
            if not isinstance(inspirations, list) or not inspirations:
                fail("Context DSL INSPIRATIONS must be a non-empty list")
        if section_name == "Work DSL":
            roadmap = payload.get("ROADMAP")
            if not isinstance(roadmap, list) or not roadmap:
                fail("Work DSL ROADMAP must be a non-empty list")
        if section_name == "User Gate DSL":
            if payload.get("ASK_USER") is not True:
                fail("User Gate DSL ASK_USER must be true")
            if payload.get("WAIT_FOR_ACK") is not True:
                fail("User Gate DSL WAIT_FOR_ACK must be true")
            if payload.get("NO_MUTATION_BEFORE_ACK") is not True:
                fail("User Gate DSL NO_MUTATION_BEFORE_ACK must be true")


def normalize_report(path: Path, metadata: dict[str, object], body: str) -> None:
    content = render_frontmatter(metadata) + "\n" + body.lstrip("\n")
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def update_latest_index(root: Path, filename: str, metadata: dict[str, object]) -> None:
    index_dir = root / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    latest_path = index_dir / "latest.json"
    latest_path.write_text(
        json.dumps(
            {
                "latest": filename,
                "metadata": {
                    "project_name": metadata["project_name"],
                    "workspace_root": metadata["workspace_root"],
                    "task_title": metadata["task_title"],
                    "status": metadata["status"],
                    "next_step": metadata["next_step"],
                },
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and register a handoff report.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--report-path", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    report_dir = root / "reports"
    path = Path(args.report_path)
    if not path.exists() or not path.is_file():
        fail("report-path must point to an existing Markdown file")
    if path.suffix != ".md":
        fail("report-path must point to a .md file")
    try:
        path.relative_to(report_dir)
    except ValueError:
        fail(f"report-path must live under {report_dir}")

    report_id, created_at = validate_filename(path)
    raw = path.read_text(encoding="utf-8")
    frontmatter = extract_frontmatter_block(raw)
    if frontmatter is None:
        fail("report must start with a valid frontmatter block")
    metadata, body = parse_frontmatter(raw)
    if not metadata:
        fail("frontmatter could not be parsed")
    normalized_metadata = validate_metadata(metadata, report_id, created_at)
    validate_sections(body)
    normalize_report(path, normalized_metadata, body)
    update_latest_index(root, path.name, normalized_metadata)
    print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
