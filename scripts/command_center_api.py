import argparse
from pathlib import Path

import uvicorn


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run the Command Center FastAPI backend."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    parser.add_argument("--db", default="data/command_center.db")
    args = parser.parse_args(argv)

    db_path = Path(args.db).as_posix()
    app_ref = f"command_center_api.app:create_app(db_path='{db_path}')"
    uvicorn.run(app_ref, host=args.host, port=args.port, reload=False, factory=True)


if __name__ == "__main__":
    main()
