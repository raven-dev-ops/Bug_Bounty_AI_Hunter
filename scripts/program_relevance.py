import argparse
from datetime import datetime, timezone

from .lib.io_utils import dump_data, load_data


KEYWORDS = [
    "ai",
    "llm",
    "machine learning",
    "ml",
    "model",
    "gpt",
    "openai",
    "anthropic",
    "chatbot",
    "assistant",
    "copilot",
    "rag",
    "embedding",
    "embeddings",
    "vector",
    "prompt",
    "inference",
    "fine-tuning",
]


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_registry(path):
    data = load_data(path)
    if isinstance(data, dict) and "programs" in data:
        return data.get("programs") or []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def _collect_text(program):
    parts = []
    for key in ("name", "policy_url", "url", "notes"):
        value = program.get(key)
        if value:
            parts.append(str(value))
    restrictions = program.get("restrictions") or []
    for item in _list(restrictions):
        parts.append(str(item))
    scope = program.get("scope") or {}
    for item in _list(scope.get("in_scope")):
        if isinstance(item, dict):
            value = item.get("value")
            if value:
                parts.append(str(value))
        else:
            parts.append(str(item))
    return " ".join(parts).lower()


def _keyword_matches(text):
    matches = []
    for keyword in KEYWORDS:
        if keyword in text:
            matches.append(keyword)
    return sorted(set(matches))


def _score(match_count):
    if match_count <= 0:
        return 0.0
    return min(1.0, match_count / 5.0)


def _label(score):
    if score >= 0.6:
        return "high"
    if score >= 0.3:
        return "medium"
    if score > 0:
        return "low"
    return "none"


def _build_entry(program):
    text = _collect_text(program)
    matches = _keyword_matches(text)
    score = _score(len(matches))
    return {
        "program_id": program.get("id"),
        "name": program.get("name"),
        "platform": program.get("platform"),
        "handle": program.get("handle"),
        "policy_url": program.get("policy_url"),
        "relevance_score": round(score, 2),
        "relevance": _label(score),
        "keywords": matches,
        "signals": {
            "text_length": len(text),
            "match_count": len(matches),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Classify program relevance to AI/LLM surfaces (metadata-only)."
    )
    parser.add_argument(
        "--input",
        default="data/program_registry.json",
        help="Program registry JSON/YAML.",
    )
    parser.add_argument(
        "--output",
        default="data/program_relevance_output.json",
        help="Relevance output JSON/YAML.",
    )
    args = parser.parse_args()

    programs = _load_registry(args.input)
    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "programs": [
            _build_entry(program) for program in programs if isinstance(program, dict)
        ],
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
