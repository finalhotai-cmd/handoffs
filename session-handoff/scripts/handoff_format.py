from __future__ import annotations

import json
import re

SECTION_ORDER = [
    "Goal DSL",
    "State DSL",
    "Context DSL",
    "Evidence DSL",
    "Work DSL",
    "Resume DSL",
    "Risk DSL",
    "User Gate DSL",
]

REQUIRED_SECTION_KEYS = {
    "Goal DSL": ["PROJECT_MISSION", "CURRENT_TASK", "OUTPUT", "DONE_WHEN"],
    "State DSL": ["PROJECT_STAGE", "SESSION_FOCUS", "DONE", "IN_FLIGHT"],
    "Context DSL": ["PROJECT_SCOPE", "USER_REQ", "DECISIONS", "CONSTRAINTS", "INSPIRATIONS"],
    "Evidence DSL": ["FILES", "CMDS", "ARTIFACTS"],
    "Work DSL": ["COMPLETED", "NEXT", "ROADMAP"],
    "Resume DSL": ["READ_FIRST", "CHECK_FIRST", "PLAN_BRIEF_CN", "EXECUTE_AFTER_ACK"],
    "Risk DSL": ["MISREAD", "DUP_WORK", "NO_GO"],
    "User Gate DSL": ["ASK_USER", "WAIT_FOR_ACK", "NO_MUTATION_BEFORE_ACK", "BRIEF_CN"],
}


def parse_scalar(value: str) -> object:
    if not value:
        return ""
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def parse_mapping_block(text: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current_list_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list_key:
            data.setdefault(current_list_key, [])
            assert isinstance(data[current_list_key], list)
            data[current_list_key].append(parse_scalar(line[4:].strip()))
            continue
        current_list_key = None
        if ": " in line:
            key, value = line.split(": ", 1)
            if value == "":
                data[key] = []
                current_list_key = key
            else:
                data[key] = parse_scalar(value.strip())
        elif line.endswith(":"):
            key = line[:-1]
            data[key] = []
            current_list_key = key
    return data


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    metadata = parse_mapping_block(text[4:end])
    body = text[end + 5 :]
    return metadata, body


def extract_section_blocks(body: str) -> list[tuple[int, str, str]]:
    pattern = re.compile(
        r"^## (\d+)\. (.+?)\n\n```handoff\n(.*?)\n```\n?",
        re.MULTILINE | re.DOTALL,
    )
    return [(int(index), name, block) for index, name, block in pattern.findall(body)]
