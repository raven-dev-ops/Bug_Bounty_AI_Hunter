from __future__ import annotations

from collections import Counter
from typing import Any

from command_center_api import db


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _layout_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {"program": [], "finding": [], "task": [], "workspace": []}
    for node in nodes:
        grouped.setdefault(str(node.get("type") or "other"), []).append(node)
    y_map = {"program": 12.0, "finding": 38.0, "task": 64.0, "workspace": 88.0}
    for node_type, items in grouped.items():
        total = max(1, len(items))
        for index, item in enumerate(items):
            item["x"] = round(((index + 1) * 100.0) / (total + 1), 2)
            item["y"] = y_map.get(node_type, 50.0)
    return nodes


def build_scope_map(
    connection: Any,
    *,
    limit: int = 200,
) -> dict[str, Any]:
    safe_limit = max(10, min(500, int(limit)))
    programs = db.list_programs(connection, limit=min(200, safe_limit))
    findings = db.list_findings(connection, limit=min(400, safe_limit * 2))
    tasks = db.list_tasks(connection, limit=min(600, safe_limit * 3))
    workspaces = db.list_workspaces(connection, limit=min(300, safe_limit))
    runs = db.list_tool_runs(connection, limit=min(300, safe_limit))
    metrics = db.list_metric_snapshots(connection, scope="global", limit=min(300, safe_limit))

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_ids: set[str] = set()

    def add_node(item: dict[str, Any]) -> None:
        node_id = _safe_text(item.get("id"))
        if not node_id or node_id in node_ids:
            return
        node_ids.add(node_id)
        nodes.append(item)

    for item in programs:
        add_node(
            {
                "id": item["id"],
                "type": "program",
                "label": _safe_text(item.get("name")) or item["id"],
                "platform": _safe_text(item.get("platform")) or "unknown",
            }
        )

    for item in findings:
        severity = (_safe_text(item.get("severity")) or "unknown").lower()
        add_node(
            {
                "id": item["id"],
                "type": "finding",
                "label": _safe_text(item.get("title")) or item["id"],
                "severity": severity,
            }
        )
        raw = item.get("raw_json")
        program_id = ""
        if isinstance(raw, dict):
            program_id = _safe_text(raw.get("program_id") or raw.get("programId") or raw.get("program"))
        if program_id and program_id in node_ids:
            edges.append(
                {
                    "source": item["id"],
                    "target": program_id,
                    "relation": "reported_in",
                }
            )

    for item in tasks:
        add_node(
            {
                "id": item["id"],
                "type": "task",
                "label": _safe_text(item.get("title")) or item["id"],
                "status": (_safe_text(item.get("status")) or "open").lower(),
            }
        )
        linked_program_id = _safe_text(item.get("linked_program_id"))
        linked_finding_id = _safe_text(item.get("linked_finding_id"))
        if linked_program_id and linked_program_id in node_ids:
            edges.append(
                {
                    "source": item["id"],
                    "target": linked_program_id,
                    "relation": "tracks_program",
                }
            )
        if linked_finding_id and linked_finding_id in node_ids:
            edges.append(
                {
                    "source": item["id"],
                    "target": linked_finding_id,
                    "relation": "tracks_finding",
                }
            )

    for item in workspaces:
        add_node(
            {
                "id": item["id"],
                "type": "workspace",
                "label": _safe_text(item.get("name")) or item["id"],
                "platform": _safe_text(item.get("platform")) or "unknown",
            }
        )

    _layout_nodes(nodes)

    severity_counts = Counter(
        (_safe_text(item.get("severity")) or "unknown").lower() for item in findings
    )
    finding_status_counts = Counter((_safe_text(item.get("status")) or "open").lower() for item in findings)
    task_status_counts = Counter((_safe_text(item.get("status")) or "open").lower() for item in tasks)
    run_status_counts = Counter((_safe_text(item.get("status")) or "unknown").lower() for item in runs)

    weights = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1, "unknown": 1}
    threat_score = 0
    for severity, count in severity_counts.items():
        threat_score += weights.get(severity, 1) * count

    timeline: list[dict[str, Any]] = []
    for snapshot in metrics:
        timeline.append(
            {
                "metric_name": snapshot.get("metric_name"),
                "value": snapshot.get("metric_value"),
                "captured_at": snapshot.get("captured_at"),
            }
        )

    return {
        "graph": {
            "nodes": nodes,
            "edges": edges,
            "counts": {
                "programs": len(programs),
                "findings": len(findings),
                "tasks": len(tasks),
                "workspaces": len(workspaces),
                "runs": len(runs),
            },
        },
        "overlays": {
            "threat_score": threat_score,
            "severity_counts": dict(severity_counts),
            "finding_status_counts": dict(finding_status_counts),
            "task_status_counts": dict(task_status_counts),
            "run_status_counts": dict(run_status_counts),
            "timeline": timeline,
        },
    }
