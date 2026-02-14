import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .lib.io_utils import load_data
from .lib.template_utils import load_template, render_template


DEFAULT_TEMPLATE = "templates/reporting/program_brief.md"
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


def _scope_summary(program):
    scope = program.get("scope") or {}
    in_scope = [item.get("value") for item in _list(scope.get("in_scope")) if item]
    out_scope = [item.get("value") for item in _list(scope.get("out_of_scope")) if item]
    lines = []
    if in_scope:
        lines.append("In scope: " + ", ".join(in_scope))
    if out_scope:
        lines.append("Out of scope: " + ", ".join(out_scope))
    return "\n".join(lines) if lines else "Scope not provided."


def _rewards_summary(program):
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
    return "Rewards not listed."


def _response_time_summary(program):
    response = program.get("response_time")
    if isinstance(response, dict):
        first = response.get("first_response_hours")
        resolution = response.get("resolution_time_hours")
        parts = []
        if first is not None:
            parts.append(f"First response: {first} hours")
        if resolution is not None:
            parts.append(f"Resolution: {resolution} hours")
        return ", ".join(parts) if parts else "Response time not provided."
    if response:
        return str(response)
    return "Response time not provided."


def _safe_harbor_summary(program):
    safe_harbor = program.get("safe_harbor")
    if isinstance(safe_harbor, dict):
        if safe_harbor.get("present") is True:
            return safe_harbor.get("notes") or "Safe harbor present."
        if safe_harbor.get("present") is False:
            return safe_harbor.get("notes") or "Safe harbor not stated."
        return safe_harbor.get("notes") or "Safe harbor not stated."
    if isinstance(safe_harbor, bool):
        return "Safe harbor present." if safe_harbor else "Safe harbor not stated."
    if safe_harbor:
        return str(safe_harbor)
    return "Safe harbor not stated."


def _restrictions_summary(program, limit=6):
    restrictions = []
    for item in _list(program.get("restrictions")):
        if isinstance(item, dict):
            text = item.get("text") or item.get("notes")
            if text:
                restrictions.append(text)
        else:
            restrictions.append(str(item))
    scope = program.get("scope") or {}
    for item in _list(scope.get("restrictions")):
        restrictions.append(str(item))
    cleaned = [text.strip() for text in restrictions if str(text).strip()]
    deduped = []
    seen = set()
    for text in cleaned:
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(text)
    if not deduped:
        return "Restrictions not listed."
    return "\n".join(f"- {item}" for item in deduped[:limit])


def _provenance_summary(program):
    sources = program.get("sources") or []
    if not sources:
        return "No provenance entries."
    lines = []
    for source in sources:
        name = source.get("source") or "source"
        fetched_at = source.get("fetched_at") or "unknown"
        status = source.get("http_status")
        if status is not None:
            lines.append(f"- {name}: {status} at {fetched_at}")
        else:
            lines.append(f"- {name}: fetched at {fetched_at}")
    return "\n".join(lines)


def render_program_brief(program, template_text):
    context = {
        "program_name": program.get("name", "Unknown Program"),
        "platform": program.get("platform", "unknown"),
        "handle": program.get("handle", "unknown"),
        "policy_url": program.get("policy_url", "unknown"),
        "generated_at": _timestamp(),
        "scope_summary": _scope_summary(program),
        "rewards_summary": _rewards_summary(program),
        "response_time_summary": _response_time_summary(program),
        "safe_harbor_summary": _safe_harbor_summary(program),
        "restrictions_summary": _restrictions_summary(program),
        "provenance_summary": _provenance_summary(program),
    }
    return render_template(template_text, context)


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
    parser = argparse.ArgumentParser(description="Generate program brief markdown.")
    parser.add_argument(
        "--input",
        default="data/program_registry.json",
        help="Program registry JSON/YAML.",
    )
    parser.add_argument("--program-id", help="Optional program id to render.")
    parser.add_argument(
        "--output-dir",
        default="output/program_briefs",
        help="Output directory for program briefs.",
    )
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Render PDF files using the configured engine.",
    )
    parser.add_argument(
        "--pdf-engine",
        default="pandoc",
        choices=["pandoc", "wkhtmltopdf"],
    )
    args = parser.parse_args()

    programs = _load_programs(args.input)
    if args.program_id:
        programs = [
            program
            for program in programs
            if isinstance(program, dict) and program.get("id") == args.program_id
        ]
    template_text = load_template(args.template)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for program in programs:
        if not isinstance(program, dict):
            continue
        slug = _program_slug(program)
        md_path = output_dir / f"{slug}.md"
        content = render_program_brief(program, template_text)
        md_path.write_text(content + "\n", encoding="utf-8")
        if args.pdf:
            pdf_path = output_dir / f"{slug}.pdf"
            _write_pdf(md_path, pdf_path, args.pdf_engine)


if __name__ == "__main__":
    main()
