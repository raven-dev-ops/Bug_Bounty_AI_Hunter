import argparse
from pathlib import Path

from .lib.io_utils import dump_data, load_data


def _parse_list(values, default):
    if not values:
        return list(default)
    parsed = []
    for value in values:
        parsed.extend(item.strip() for item in value.split(",") if item.strip())
    return parsed


def _iter_example_files(roots, extensions, exclude):
    exclude_set = {Path(path) for path in exclude}
    for root in roots:
        base = Path(root)
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path in exclude_set:
                continue
            if path.suffix.lower().lstrip(".") not in extensions:
                continue
            yield path


def _emit_file(path):
    data = load_data(path)
    dump_data(path, data)


def main():
    parser = argparse.ArgumentParser(
        description="Re-emit example artifacts deterministically."
    )
    parser.add_argument(
        "--roots",
        action="append",
        help="Root directories to scan (default: examples,data,evidence).",
    )
    parser.add_argument(
        "--extensions",
        action="append",
        help="Extensions to include (default: json).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Explicit files to exclude.",
    )
    args = parser.parse_args()

    roots = _parse_list(args.roots, ["examples", "data", "evidence"])
    extensions = set(_parse_list(args.extensions, ["json"]))
    exclude = _parse_list(args.exclude, [])

    for path in _iter_example_files(roots, extensions, exclude):
        _emit_file(path)


if __name__ == "__main__":
    main()
