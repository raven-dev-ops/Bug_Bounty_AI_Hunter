import argparse
from datetime import datetime, timezone

from .lib.io_utils import dump_data, load_data


APPROACH_BY_BUCKET = {
    "Easy": {
        "summary": "Low friction entry with clear scope and manageable limits.",
        "steps": [
            "Confirm scope and ROE before any action.",
            "Draft a canary-first test plan for high-impact surfaces.",
            "Review restrictions and plan manual validation only.",
        ],
    },
    "Medium": {
        "summary": "Moderate scope or restrictions; requires careful planning.",
        "steps": [
            "Confirm scope boundaries and safe harbor wording.",
            "Prioritize manual review of access controls and data flows.",
            "Plan for tighter evidence capture and approval checks.",
        ],
    },
    "Hard": {
        "summary": "Complex scope or heavy restrictions; planning only.",
        "steps": [
            "Request clarification on ambiguous scope or rules.",
            "Focus on documentation review and threat modeling.",
            "Avoid testing without explicit written approval.",
        ],
    },
    "Impossible": {
        "summary": "Testing is disallowed or requires approval; do not proceed.",
        "steps": [
            "Document the restrictions and safe harbor status.",
            "Skip testing and mark as review-only.",
            "Escalate for manual approval if needed.",
        ],
    },
    "God Mode": {
        "summary": "High friction and limited access; treat as out-of-scope for now.",
        "steps": [
            "Document why the program is unsuitable for a case study.",
            "Skip testing and focus on other candidates.",
            "Revisit only with explicit authorization.",
        ],
    },
}


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


def _approach_for_bucket(bucket):
    return APPROACH_BY_BUCKET.get(bucket) or {
        "summary": "Unknown bucket; use manual review.",
        "steps": ["Confirm scope and ROE before proceeding."],
    }


def _build_entry(scored):
    bucket = scored.get("bucket") or "Unknown"
    approach = _approach_for_bucket(bucket)
    signals = scored.get("signals") or {}
    restrictions_count = signals.get("restrictions_count")
    steps = list(approach.get("steps", []))
    if restrictions_count is not None and restrictions_count > 0:
        steps.append(f"Review {restrictions_count} restriction(s) before planning.")
    if scored.get("review_required"):
        steps.append("Flag for manual review before any execution.")

    return {
        "program_id": scored.get("program_id"),
        "name": scored.get("name"),
        "platform": scored.get("platform"),
        "handle": scored.get("handle"),
        "policy_url": scored.get("policy_url"),
        "bucket": bucket,
        "score": scored.get("score"),
        "approach": {
            "summary": approach.get("summary"),
            "steps": steps,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate suggested approaches based on scoring buckets."
    )
    parser.add_argument(
        "--input",
        default="data/program_scoring_output.json",
        help="Program scoring JSON/YAML.",
    )
    parser.add_argument(
        "--output",
        default="data/suggested_approach_output.json",
        help="Suggested approach output JSON/YAML.",
    )
    args = parser.parse_args()

    scored = _load_scoring(args.input)
    approaches = [_build_entry(entry) for entry in scored if isinstance(entry, dict)]

    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "programs": approaches,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
