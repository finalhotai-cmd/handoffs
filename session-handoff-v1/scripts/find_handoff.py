#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable

from handoff_format import parse_frontmatter

DEFAULT_ROOT = Path("/Volumes/OSX ExtNVME/code_projects/handoffs")
DEFAULT_REPORTS = DEFAULT_ROOT / "reports"
QUALITY_TOKENS = [
    "PROJECT_MISSION",
    "PROJECT_STAGE",
    "INSPIRATIONS",
    "ROADMAP",
    "WAIT_FOR_ACK",
    "NO_MUTATION_BEFORE_ACK",
]


@dataclass
class Report:
    path: Path
    metadata: dict[str, object]
    body: str
    score: int = 0
    reasons: list[str] = field(default_factory=list)

    @property
    def created_at(self) -> datetime:
        raw = str(self.metadata.get("created_at", "")).strip()
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y%m%d-%H%M"):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        match = re.match(r"^(\d{8})-(\d{4})-", self.path.name)
        if match:
            return datetime.strptime("".join(match.groups()), "%Y%m%d%H%M")
        return datetime.fromtimestamp(self.path.stat().st_mtime)

def load_reports(report_dir: Path) -> list[Report]:
    reports: list[Report] = []
    for path in sorted(report_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(text)
        reports.append(Report(path=path, metadata=metadata, body=body))
    return reports


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_./-]+", text.lower()))


def score_report(
    report: Report,
    workspace_root: str | None,
    query: str | None,
    status: str | None,
    latest_name: str | None,
) -> None:
    report.score = 0
    report.reasons = []
    report_workspace = str(report.metadata.get("workspace_root", ""))
    report_status = str(report.metadata.get("status", ""))
    haystack = " ".join(
        [
            report.path.name,
            str(report.metadata.get("project_name", "")),
            str(report.metadata.get("task_title", "")),
            " ".join(report.metadata.get("key_files", []) if isinstance(report.metadata.get("key_files"), list) else []),
            " ".join(report.metadata.get("tags", []) if isinstance(report.metadata.get("tags"), list) else []),
            report.body[:1200],
        ]
    ).lower()
    if workspace_root and report_workspace == workspace_root:
        report.score += 8
        report.reasons.append("workspace_root match")
    elif workspace_root and workspace_root in report_workspace:
        report.score += 4
        report.reasons.append("workspace_root prefix")
    if status and report_status == status:
        report.score += 25
        report.reasons.append(f"status={status}")
    elif report_status == "in_progress":
        report.score += 10
        report.reasons.append("in_progress")
    if latest_name and report.path.name == latest_name:
        report.score += 24
        report.reasons.append("latest index")
    if query:
        query_tokens = tokenize(query)
        matches = sum(1 for token in query_tokens if token in haystack)
        if matches:
            report.score += matches * 12
            report.reasons.append(f"query token matches={matches}")
    key_files = report.metadata.get("key_files")
    if isinstance(key_files, list) and key_files:
        report.score += min(len(key_files), 8) * 4
        report.reasons.append(f"key_files={len(key_files)}")
        if query:
            query_tokens = tokenize(query)
            key_hits = sum(
                1 for file_path in key_files if any(token in str(file_path).lower() for token in query_tokens)
            )
            if key_hits:
                report.score += key_hits * 18
                report.reasons.append(f"key_file token matches={key_hits}")
    quality_hits = sum(1 for token in QUALITY_TOKENS if token in report.body)
    if quality_hits:
        report.score += quality_hits * 15
        report.reasons.append(f"quality_tokens={quality_hits}")
    report.score += int(report.created_at.timestamp() // 600)


def report_to_dict(report: Report) -> dict[str, object]:
    return {
        "path": str(report.path),
        "created_at": report.created_at.isoformat(timespec="minutes"),
        "score": report.score,
        "reasons": report.reasons,
        "metadata": report.metadata,
    }


def choose_reports(reports: Iterable[Report]) -> list[Report]:
    return sorted(reports, key=lambda report: report.score, reverse=True)


def load_latest_report_path(root: Path) -> Path | None:
    latest_path = root / "index" / "latest.json"
    if not latest_path.exists():
        return None
    try:
        data = json.loads(latest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    latest = data.get("latest")
    if not isinstance(latest, str) or not latest.strip():
        return None
    candidate = root / "reports" / latest
    return candidate if candidate.exists() else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Find the best matching OH report.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    parser.add_argument("--workspace-root")
    parser.add_argument("--query")
    parser.add_argument("--status")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.root)
    report_dir = root / "reports"
    if not report_dir.exists():
        raise SystemExit(f"report directory does not exist: {report_dir}")

    reports = load_reports(report_dir)
    if not reports:
        raise SystemExit(f"no handoff reports found in {report_dir}")

    latest_report = load_latest_report_path(root)
    latest_name = latest_report.name if latest_report is not None else None

    for report in reports:
        if args.latest:
            report.score = int(report.created_at.timestamp() // 60)
            report.reasons = ["latest"]
        else:
            score_report(report, args.workspace_root, args.query, args.status, latest_name)

    ranked = choose_reports(reports)[: max(1, args.limit)]
    if args.json:
        print(json.dumps([report_to_dict(report) for report in ranked], indent=2, ensure_ascii=False))
    elif len(ranked) == 1:
        print(str(ranked[0].path))
    else:
        for report in ranked:
            print(str(report.path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
