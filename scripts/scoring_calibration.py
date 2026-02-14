import argparse
from datetime import datetime, timezone

from .lib.io_utils import dump_data, load_data


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _load_scoring(path):
    data = load_data(path)
    if isinstance(data, dict) and "programs" in data:
        return data.get("programs") or []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def _load_labels(path):
    data = load_data(path)
    if isinstance(data, dict) and "labels" in data:
        return data.get("labels") or []
    if isinstance(data, list):
        return data
    return []


def _build_index(scored):
    index = {}
    for entry in scored:
        if not isinstance(entry, dict):
            continue
        program_id = entry.get("program_id")
        if program_id:
            index[program_id] = entry
    return index


def main():
    parser = argparse.ArgumentParser(
        description="Compare scoring output against a labeled calibration dataset."
    )
    parser.add_argument(
        "--scoring",
        default="data/program_scoring_output.json",
        help="Program scoring JSON/YAML.",
    )
    parser.add_argument(
        "--labels",
        default="examples/scoring_calibration_dataset.json",
        help="Calibration labels JSON/YAML.",
    )
    parser.add_argument(
        "--output",
        default="data/scoring_calibration_report.json",
        help="Calibration report output JSON/YAML.",
    )
    args = parser.parse_args()

    scored = _load_scoring(args.scoring)
    labels = _load_labels(args.labels)
    index = _build_index(scored)

    total = 0
    matched = 0
    missing = 0
    mismatches = []

    for label in labels:
        if not isinstance(label, dict):
            continue
        program_id = label.get("program_id")
        expected = label.get("expected_bucket")
        if not program_id or not expected:
            continue
        total += 1
        scored_entry = index.get(program_id)
        if not scored_entry:
            missing += 1
            mismatches.append(
                {
                    "program_id": program_id,
                    "expected_bucket": expected,
                    "actual_bucket": None,
                    "reason": "Program not found in scoring output.",
                }
            )
            continue
        actual = scored_entry.get("bucket")
        if actual == expected:
            matched += 1
        else:
            mismatches.append(
                {
                    "program_id": program_id,
                    "expected_bucket": expected,
                    "actual_bucket": actual,
                    "reason": "Bucket mismatch.",
                }
            )

    accuracy = round(matched / float(total), 2) if total else 0.0
    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "summary": {
            "total_labels": total,
            "matched": matched,
            "missing": missing,
            "accuracy": accuracy,
        },
        "mismatches": mismatches,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
