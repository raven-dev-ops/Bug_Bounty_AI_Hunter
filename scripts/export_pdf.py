import argparse
import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PANDOC_HEADER = REPO_ROOT / "templates" / "reporting" / "pandoc_header.tex"
FONTCONFIG_FILE = REPO_ROOT / "templates" / "reporting" / "fontconfig.conf"


def _run_pandoc(input_path, output_path, pdf_engine=None):
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise SystemExit("pandoc is required for PDF export.")
    command = [pandoc, input_path, "-o", output_path]
    if PANDOC_HEADER.exists():
        command.extend(["--include-in-header", str(PANDOC_HEADER)])
    if pdf_engine:
        if shutil.which(pdf_engine) is None:
            raise SystemExit(f"{pdf_engine} is required for PDF export.")
        command.extend(["--pdf-engine", pdf_engine])
    env = os.environ.copy()
    if FONTCONFIG_FILE.exists():
        env.setdefault("FONTCONFIG_FILE", str(FONTCONFIG_FILE))
    subprocess.run(command, check=True, env=env)


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
        pandoc_pdf_engine = os.environ.get("BBHAI_PANDOC_PDF_ENGINE")
        _run_pandoc(str(input_path), str(output_path), pandoc_pdf_engine)
    else:
        _run_wkhtmltopdf(str(input_path), str(output_path))


if __name__ == "__main__":
    main()
