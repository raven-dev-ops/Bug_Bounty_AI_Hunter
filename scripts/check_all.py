import argparse
import os
import shutil
import subprocess
import sys
import sysconfig
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Check:
    name: str
    argv: list[str]
    slow: bool = False


def _py(*args: str) -> list[str]:
    return [sys.executable, *args]


def _bbhai_console() -> list[str]:
    found = shutil.which("bbhai")
    if found:
        return [found]

    scripts_dir = Path(sysconfig.get_path("scripts"))
    if os.name == "nt":
        exe = scripts_dir / "bbhai.exe"
        if exe.exists():
            return [str(exe)]
        script = scripts_dir / "bbhai-script.py"
        if script.exists():
            return [sys.executable, str(script)]
        bat = scripts_dir / "bbhai.bat"
        if bat.exists():
            return [str(bat)]
    else:
        script = scripts_dir / "bbhai"
        if script.exists():
            return [str(script)]

    return ["bbhai"]


def _run(check):
    print(f"\n==> {check.name}")
    print("$ " + " ".join(check.argv))
    subprocess.run(check.argv, check=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run CI-style checks locally.")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slower checks (pip-audit, packaging smoke, golden examples, demo runner, mkdocs).",
    )
    args = parser.parse_args(argv)

    os.chdir(REPO_ROOT)

    checks = [
        Check(
            "Dependency audit",
            _py(
                "-m",
                "pip_audit",
                "-r",
                "requirements.txt",
                "-r",
                "requirements-dev.txt",
            ),
            slow=True,
        ),
        Check(
            "Packaging smoke test", _py("-m", "pip", "install", "-e", "."), slow=True
        ),
        Check("bbhai --help", _bbhai_console() + ["--help"], slow=True),
        Check("bbhai --version", _bbhai_console() + ["--version"], slow=True),
        Check("Validate schemas", _py("-m", "scripts.validate_schemas")),
        Check("Ruff lint", _py("-m", "ruff", "check", "scripts", "tests")),
        Check(
            "Ruff format",
            _py("-m", "ruff", "format", "--check", "scripts", "tests"),
        ),
        Check("Markdown links", _py("-m", "scripts.validate_markdown_links")),
        Check("Markdown ASCII", _py("-m", "scripts.validate_markdown_ascii")),
        Check("Knowledge lint", _py("-m", "scripts.knowledge_lint")),
        Check(
            "Tests (coverage)",
            _py("-m", "coverage", "run", "-m", "unittest", "discover", "-s", "tests"),
        ),
        Check("Coverage report", _py("-m", "coverage", "report", "-m")),
        Check(
            "Knowledge index",
            _py("-m", "scripts.knowledge_index", "--output", "knowledge/INDEX.md"),
        ),
        Check(
            "Knowledge index clean",
            ["git", "diff", "--exit-code", "--", "knowledge/INDEX.md"],
        ),
        Check(
            "Publish knowledge docs",
            _py("-m", "scripts.publish_knowledge_docs"),
        ),
        Check(
            "Knowledge docs clean",
            [
                "git",
                "diff",
                "--exit-code",
                "--",
                "docs/KNOWLEDGE_INDEX.md",
                "docs/knowledge",
            ],
        ),
        Check(
            "Coverage matrix",
            _py(
                "-m",
                "scripts.coverage_matrix",
                "--input",
                "docs/coverage_matrix.yaml",
                "--output",
                "docs/COVERAGE_MATRIX.md",
            ),
        ),
        Check(
            "Coverage matrix clean",
            ["git", "diff", "--exit-code", "--", "docs/COVERAGE_MATRIX.md"],
        ),
        Check(
            "Component registry index",
            _py(
                "-m",
                "scripts.component_registry_index",
                "--output",
                "data/component_registry_index.json",
            ),
        ),
        Check(
            "Component registry index clean",
            ["git", "diff", "--exit-code", "--", "data/component_registry_index.json"],
        ),
        Check(
            "Golden examples",
            _py(
                "-m",
                "scripts.golden_examples",
                "--roots",
                "examples",
                "--roots",
                "data",
                "--roots",
                "evidence",
                "--extensions",
                "json",
            ),
            slow=True,
        ),
        Check(
            "Golden examples clean",
            ["git", "diff", "--exit-code", "--", "examples", "data", "evidence"],
            slow=True,
        ),
        Check(
            "Demo runner plan",
            _py("-m", "scripts.demo_runner", "--mode", "plan"),
            slow=True,
        ),
        Check("MkDocs build", _py("-m", "mkdocs", "build", "--strict"), slow=True),
    ]

    for entry in checks:
        if args.fast and entry.slow:
            continue
        _run(entry)

    print("\nAll checks passed.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode) from exc
    except KeyboardInterrupt:
        print("\nInterrupted.")
        raise SystemExit(130)
