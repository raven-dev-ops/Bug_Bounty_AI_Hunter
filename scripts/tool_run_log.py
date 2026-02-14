import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from .lib.io_utils import dump_data


def _hash_file(path, algorithm):
    hasher = hashlib.new(algorithm)
    size_bytes = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            size_bytes += len(chunk)
            hasher.update(chunk)
    return hasher.hexdigest(), size_bytes


def _parse_approval(value):
    parts = [part.strip() for part in value.split("|", maxsplit=2)]
    if len(parts) < 2:
        raise SystemExit("Approval must be formatted as 'approver|approved_at|notes'.")
    entry = {"approver": parts[0], "approved_at": parts[1]}
    if len(parts) > 2 and parts[2]:
        entry["notes"] = parts[2]
    return entry


def main():
    parser = argparse.ArgumentParser(
        description="Create a tool run log for evidence tracking."
    )
    parser.add_argument("--tool", required=True, help="Tool name.")
    parser.add_argument("--version", default="", help="Tool version.")
    parser.add_argument(
        "--mode",
        choices=["passive", "active", "lab"],
        required=True,
        help="Execution mode.",
    )
    parser.add_argument("--scope-reference", default="", help="Scope reference.")
    parser.add_argument("--target", default="", help="Target identifier.")
    parser.add_argument("--command", default="", help="Command or workflow note.")
    parser.add_argument(
        "--artifact",
        action="append",
        default=[],
        help="Artifact path to include (repeatable).",
    )
    parser.add_argument(
        "--hash-algorithm",
        default="sha256",
        help="Hash algorithm for artifacts (default sha256).",
    )
    parser.add_argument(
        "--approval",
        action="append",
        default=[],
        help="Approval in 'approver|approved_at|notes' format.",
    )
    parser.add_argument("--notes", default="", help="Notes for the tool run.")
    parser.add_argument("--schema-version", default="0.1.0", help="Schema version.")
    parser.add_argument(
        "--id",
        default="",
        help="Tool run id (default tool-run-YYYYMMDDHHMMSS).",
    )
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    args = parser.parse_args()

    run_id = args.id or f"tool-run-{datetime.now(timezone.utc):%Y%m%d%H%M%S}"

    hashes = []
    outputs = []
    for artifact in args.artifact:
        path = Path(artifact)
        outputs.append(str(path))
        if not path.exists():
            hashes.append(
                {
                    "path": str(path),
                    "algorithm": args.hash_algorithm,
                    "status": "missing",
                }
            )
            continue
        digest, size_bytes = _hash_file(path, args.hash_algorithm)
        hashes.append(
            {
                "path": str(path),
                "algorithm": args.hash_algorithm,
                "hash": digest,
                "computed_at": datetime.now(timezone.utc).isoformat(),
                "size_bytes": size_bytes,
                "status": "ok",
            }
        )

    approvals = [_parse_approval(value) for value in args.approval]

    payload = {
        "schema_version": args.schema_version,
        "id": run_id,
        "tool": args.tool,
        "version": args.version,
        "mode": args.mode,
        "scope_reference": args.scope_reference,
        "target": args.target,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "command": args.command,
        "outputs": outputs,
        "hashes": hashes,
        "approvals": approvals,
        "notes": args.notes,
    }

    dump_data(args.output, payload)


if __name__ == "__main__":
    main()
