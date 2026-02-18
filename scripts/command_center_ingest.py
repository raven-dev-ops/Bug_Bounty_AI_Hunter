import argparse
import json
from pathlib import Path

from command_center_api.ingest import ingest_existing_artifacts


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Import existing program registry, findings DB, and bounty board artifacts "
            "into the Command Center SQLite database."
        )
    )
    parser.add_argument("--db", default="data/command_center.db")
    parser.add_argument("--registry", default="data/program_registry.json")
    parser.add_argument("--findings-db", default="data/findings_db.json")
    parser.add_argument("--bounty-dir", default="bounty_board")
    args = parser.parse_args(argv)

    counts = ingest_existing_artifacts(
        db_path=Path(args.db),
        program_registry_path=Path(args.registry),
        findings_db_path=Path(args.findings_db),
        bounty_board_root=Path(args.bounty_dir),
    )
    print(json.dumps({"ok": True, "counts": counts}, indent=2))


if __name__ == "__main__":
    main()

