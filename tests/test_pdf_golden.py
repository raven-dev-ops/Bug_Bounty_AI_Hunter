import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "pdf_hashes.json"
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


def _load_hashes():
    if not FIXTURE_PATH.exists():
        return {}
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


class PdfGoldenTests(unittest.TestCase):
    def _should_run(self):
        return os.environ.get("BBHAI_PDF_TESTS") == "1"

    def _engine(self):
        return os.environ.get("BBHAI_PDF_ENGINE") or "pandoc"

    def _require_engine(self, engine):
        if shutil.which(engine) is None:
            self.skipTest(f"{engine} not available for PDF tests.")

    def _render_pdf(self, input_path, output_path, engine):
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

    def test_pdf_golden_hashes(self):
        if not self._should_run():
            self.skipTest("Set BBHAI_PDF_TESTS=1 to run PDF golden tests.")

        engine = self._engine()
        os.environ.setdefault("SOURCE_DATE_EPOCH", PDF_SOURCE_DATE_EPOCH)
        self._require_engine(engine)
        hashes = _load_hashes()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            for key, source in CASES.items():
                expected = hashes.get(key)
                if not expected:
                    self.skipTest(f"Missing golden hash for {key}.")
                output_path = temp_dir / f"{key}.pdf"
                self._render_pdf(Path(source), output_path, engine)
                actual = _sha256(output_path)
                self.assertEqual(
                    actual,
                    expected,
                    msg=f"PDF hash mismatch for {key}.",
                )


if __name__ == "__main__":
    unittest.main()
