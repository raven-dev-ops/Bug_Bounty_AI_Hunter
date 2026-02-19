from pathlib import Path
import sys

import uvicorn

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from command_center_api.app import create_app  # noqa: E402


def main() -> None:
    db_path = Path("data/command_center.e2e.db")
    if db_path.exists():
        db_path.unlink()
    app = create_app(db_path=db_path)
    uvicorn.run(app, host="127.0.0.1", port=8787, reload=False)


if __name__ == "__main__":
    main()
