import argparse
import re
from pathlib import Path


DEFAULT_PATTERNS = [
    r"Bearer\\s+[A-Za-z0-9\\-._~+/]+=*",
    r"(?i)api[_-]?key\\s*[:=]\\s*[A-Za-z0-9\\-._]+",
    r"(?i)token\\s*[:=]\\s*[A-Za-z0-9\\-._]+",
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}",
]


def _load_patterns(patterns):
    combined = list(DEFAULT_PATTERNS)
    for item in patterns:
        combined.append(item)
    return combined


def main():
    parser = argparse.ArgumentParser(description="Redact sensitive data in files.")
    parser.add_argument("--input", required=True, help="Input text file.")
    parser.add_argument("--output", required=True, help="Output redacted file.")
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="Additional regex pattern to redact (repeatable).",
    )
    parser.add_argument(
        "--replacement",
        default="<redacted>",
        help="Replacement value (default <redacted>).",
    )
    parser.add_argument(
        "--case-insensitive",
        action="store_true",
        help="Apply case-insensitive matching to custom patterns.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8", errors="replace")
    patterns = _load_patterns(args.pattern)
    for pattern in patterns:
        flags = re.IGNORECASE if args.case_insensitive else 0
        text = re.sub(pattern, args.replacement, text, flags=flags)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
