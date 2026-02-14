import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .lib.io_utils import load_data
from .lib.template_utils import load_template, render_template
from .program_brief import render_program_brief


CATALOG_TEMPLATE = "templates/reporting/master_catalog.md"
BRIEF_TEMPLATE = "templates/reporting/program_brief.md"
SLUG_RE = re.compile(r"[^a-z0-9]+")


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_programs(path):
    data = load_data(path)
    if isinstance(data, dict) and "programs" in data:
        return data.get("programs") or []
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    return []


def _slugify(value):
    text = SLUG_RE.sub("-", str(value or "").lower()).strip("-")
    return text or "program"


def _program_slug(program):
    program_id = program.get("id")
    if program_id:
        return _slugify(program_id.replace("program:", ""))
    name = program.get("name")
    if name:
        return _slugify(name)
    handle = program.get("handle")
    if handle:
        return _slugify(handle)
    return "program"


def _reward_summary(program):
    rewards = program.get("rewards")
    if isinstance(rewards, dict):
        summary = rewards.get("summary")
        if summary:
            return summary
        minimum = rewards.get("min")
        maximum = rewards.get("max")
        currency = rewards.get("currency") or ""
        if minimum is not None or maximum is not None:
            return f"{currency} {minimum}-{maximum}".strip()
    if rewards:
        return str(rewards)
    return "Unlisted"


def _format_policy_url(policy_url):
    if not policy_url:
        return "unknown"
    if policy_url.startswith(("http://", "https://")):
        return f"<{policy_url}>"
    return policy_url


def _sort_programs(programs, sort_key):
    if sort_key == "platform":
        return sorted(
            programs, key=lambda p: (p.get("platform") or "", p.get("name") or "")
        )
    if sort_key == "reward":
        return sorted(programs, key=lambda p: _reward_summary(p))
    return sorted(programs, key=lambda p: (p.get("name") or "", p.get("id") or ""))


def _build_table(programs, brief_dir, brief_ext):
    lines = [
        "| Program | Platform | Rewards | Policy | Brief |",
        "| --- | --- | --- | --- | --- |",
    ]
    for program in programs:
        name = program.get("name", "Unknown Program")
        platform = program.get("platform") or "unknown"
        rewards = _reward_summary(program)
        policy_url = _format_policy_url(program.get("policy_url"))
        slug = _program_slug(program)
        brief_path = f"{brief_dir}/{slug}.{brief_ext}"
        brief_link = f"[Brief]({brief_path})"
        lines.append(
            f"| {name} | {platform} | {rewards} | {policy_url} | {brief_link} |"
        )
    return "\n".join(lines)


def _write_pdf(md_path, pdf_path, engine):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.export_pdf",
            "--input",
            str(md_path),
            "--output",
            str(pdf_path),
            "--engine",
            engine,
        ],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Render a master program catalog and optional PDF."
    )
    parser.add_argument(
        "--input",
        default="data/program_registry.json",
        help="Program registry JSON/YAML.",
    )
    parser.add_argument(
        "--output",
        default="output/catalog/master_catalog.md",
        help="Master catalog markdown path.",
    )
    parser.add_argument(
        "--brief-dir",
        default="output/catalog/program_briefs",
        help="Directory for program brief outputs.",
    )
    parser.add_argument(
        "--sort",
        default="name",
        choices=["name", "platform", "reward"],
        help="Sort order for the catalog.",
    )
    parser.add_argument("--catalog-template", default=CATALOG_TEMPLATE)
    parser.add_argument("--brief-template", default=BRIEF_TEMPLATE)
    parser.add_argument(
        "--generate-briefs",
        action="store_true",
        help="Generate per-program brief markdown files.",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Render master catalog PDF.",
    )
    parser.add_argument(
        "--pdf-engine",
        default="pandoc",
        choices=["pandoc", "wkhtmltopdf"],
    )
    parser.add_argument(
        "--brief-pdf",
        action="store_true",
        help="Render per-program PDF briefs.",
    )
    args = parser.parse_args()

    programs = [
        program for program in _load_programs(args.input) if isinstance(program, dict)
    ]
    programs = _sort_programs(programs, args.sort)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    brief_dir = Path(args.brief_dir)
    brief_dir.mkdir(parents=True, exist_ok=True)

    brief_ext = "pdf" if args.brief_pdf else "md"
    table = _build_table(programs, brief_dir.name, brief_ext)
    template_text = load_template(args.catalog_template)
    content = render_template(
        template_text,
        {
            "generated_at": _timestamp(),
            "program_count": len(programs),
            "program_table": table,
        },
    )
    output_path.write_text(content + "\n", encoding="utf-8")

    if args.generate_briefs:
        brief_template_text = load_template(args.brief_template)
        for program in programs:
            slug = _program_slug(program)
            md_path = brief_dir / f"{slug}.md"
            md_body = render_program_brief(program, brief_template_text)
            md_path.write_text(md_body + "\n", encoding="utf-8")
            if args.brief_pdf:
                pdf_path = brief_dir / f"{slug}.pdf"
                _write_pdf(md_path, pdf_path, args.pdf_engine)

    if args.pdf:
        pdf_path = output_path.with_suffix(".pdf")
        _write_pdf(output_path, pdf_path, args.pdf_engine)


if __name__ == "__main__":
    main()
