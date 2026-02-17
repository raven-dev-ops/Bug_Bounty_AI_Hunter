import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _render_text(text: str) -> str:
    return text.rstrip() + "\n"


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_text(text), encoding="utf-8", newline="\n")


def main() -> None:
    os.chdir(REPO_ROOT)

    copies = [
        (Path("BUGCROWD.md"), Path("docs/BUGCROWD.md")),
        (Path("GUIDE.md"), Path("docs/GUIDE.md")),
    ]

    for src, dst in copies:
        if not src.exists():
            raise SystemExit(f"Missing source file: {src}")

        rendered = _render_text(src.read_text(encoding="utf-8", errors="replace"))
        dst_exists = dst.exists()
        if dst_exists:
            current_text = _render_text(
                dst.read_text(encoding="utf-8", errors="replace")
            )
            current_bytes = dst.read_bytes()
            if current_text == rendered and b"\r\n" not in current_bytes:
                continue

        _write_text(dst, rendered)


if __name__ == "__main__":
    main()
