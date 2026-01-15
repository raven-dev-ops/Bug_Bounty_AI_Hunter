import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data


SEVERITY_PRIORITY = {
    "critical": "p0",
    "high": "p1",
    "medium": "p2",
    "low": "p3",
    "info": "p3",
}


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_severity(item):
    severity = str(item.get("severity", "")).lower()
    if severity in SEVERITY_PRIORITY:
        return severity

    impact = str(item.get("impact", "")).lower()
    for key in ("critical", "high", "medium", "low"):
        if key in impact:
            return key
    return "info"


def _triage_item(item, index, source):
    severity = _normalize_severity(item)
    return {
        "id": item.get("id") or f"triage-{index:04d}",
        "title": item.get("title") or item.get("name") or "Untitled item",
        "severity": severity,
        "priority": SEVERITY_PRIORITY.get(severity, "p3"),
        "status": "triaged" if source == "findings" else "needs-validation",
        "source": source,
        "rationale": f"Severity derived as {severity}.",
    }


def main():
    parser = argparse.ArgumentParser(description="Triage findings or scan plans.")
    parser.add_argument("--input", required=True, help="Input JSON/YAML path.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    args = parser.parse_args()

    data = load_data(args.input)
    if isinstance(data, dict) and "findings" in data:
        items = _list(data.get("findings"))
        source = "findings"
    elif isinstance(data, dict) and "tests" in data:
        items = _list(data.get("tests"))
        source = "tests"
    else:
        items = _list(data)
        source = "items"

    triaged = [_triage_item(item, index, source) for index, item in enumerate(items, 1)]

    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": triaged,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
