import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CASES = {
    "report": "examples/outputs/report.md",
    "program_brief": "examples/outputs/program_brief_example.md",
    "master_catalog": "examples/outputs/master_catalog.md",
}
PDF_SOURCE_DATE_EPOCH = "1700000000"


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_pdf(input_path, output_path, engine):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.export_pdf",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--engine",
            engine,
        ],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description="Update PDF golden hashes.")
    parser.add_argument(
        "--engine",
        default="pandoc",
        choices=["pandoc", "wkhtmltopdf"],
    )
    parser.add_argument(
        "--output",
        default="tests/fixtures/pdf_hashes.json",
        help="Output hashes JSON path.",
    )
    args = parser.parse_args()

    if shutil.which(args.engine) is None:
        raise SystemExit(f"{args.engine} is required to generate PDF hashes.")

    os.environ.setdefault("SOURCE_DATE_EPOCH", PDF_SOURCE_DATE_EPOCH)

    hashes = {}
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        for key, source in CASES.items():
            output_path = temp_dir / f"{key}.pdf"
            _render_pdf(Path(source), output_path, args.engine)
            hashes[key] = _sha256(output_path)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
