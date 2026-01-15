import argparse
import shutil
import subprocess
from pathlib import Path
import sys


def _run_pandoc(input_path, output_path):
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc is required for PDF export.")
    subprocess.run([pandoc, input_path, "-o", output_path], check=True)


def _run_wkhtmltopdf(input_path, output_path):
    wkhtmltopdf = shutil.which("wkhtmltopdf")
    if not wkhtmltopdf:
        raise SystemExit("wkhtmltopdf is required for PDF export.")
    subprocess.run([wkhtmltopdf, input_path, output_path], check=True)


def main():
    parser = argparse.ArgumentParser(description="Export a report to PDF.")
    parser.add_argument("--input", required=True, help="Input markdown path.")
    parser.add_argument("--output", required=True, help="Output PDF path.")
    parser.add_argument(
        "--engine",
        default="pandoc",
        choices=["pandoc", "wkhtmltopdf"],
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.engine == "pandoc":
        _run_pandoc(str(input_path), str(output_path))
    else:
        _run_wkhtmltopdf(str(input_path), str(output_path))


if __name__ == "__main__":
    main()
