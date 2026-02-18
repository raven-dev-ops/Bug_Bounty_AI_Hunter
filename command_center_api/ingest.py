from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from command_center_api import db


def _load_json(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"expected object JSON at {path}")
    return data


def _slug_from_path(path: Path) -> str:
    return path.stem.strip().lower().replace(" ", "-")


def _extract_program_from_markdown(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    title = lines[0].lstrip("#").strip()
    if not title:
        return None
    slug = _slug_from_path(path)
    return {
        "id": f"board:{slug}",
        "name": title,
        "platform": "board",
        "handle": slug,
        "policy_url": "",
        "rewards": {"summary": ""},
        "notes": f"ingested from {path.as_posix()}",
    }


def ingest_existing_artifacts(
    *,
    db_path: Path | str,
    program_registry_path: Path | str = Path("data/program_registry.json"),
    findings_db_path: Path | str = Path("data/findings_db.json"),
    bounty_board_root: Path | str = Path("bounty_board"),
) -> dict[str, int]:
    registry_path = Path(program_registry_path)
    findings_path = Path(findings_db_path)
    board_root = Path(bounty_board_root)

    counts = {
        "programs_registry": 0,
        "programs_board": 0,
        "findings": 0,
    }

    db.init_schema(db_path)

    with db.get_connection(db_path) as connection:
        if registry_path.exists():
            registry_data = _load_json(registry_path)
            programs = registry_data.get("programs", [])
            if isinstance(programs, list):
                counts["programs_registry"] = db.upsert_programs(
                    connection,
                    [item for item in programs if isinstance(item, dict)],
                    source="program_registry",
                )

        if findings_path.exists():
            findings_data = _load_json(findings_path)
            findings = findings_data.get("findings", [])
            if isinstance(findings, list):
                counts["findings"] = db.upsert_findings(
                    connection,
                    [item for item in findings if isinstance(item, dict)],
                    source="findings_db",
                )

        if board_root.exists():
            extracted: list[dict[str, Any]] = []
            for markdown_file in board_root.rglob("*.md"):
                if markdown_file.name.upper() == "INDEX.MD":
                    continue
                program = _extract_program_from_markdown(markdown_file)
                if program is not None:
                    extracted.append(program)
            if extracted:
                counts["programs_board"] = db.upsert_programs(
                    connection,
                    extracted,
                    source="bounty_board",
                )

    return counts

