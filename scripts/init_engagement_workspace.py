import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


TEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json", ".csv"}


def _utc_now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _render_template(text, mapping):
    rendered = text
    for key, value in mapping.items():
        rendered = rendered.replace(key, value)
    return rendered


def _copy_template_tree(template_root, dest_root, mapping, *, force):
    template_root = Path(template_root)
    dest_root = Path(dest_root)

    if not template_root.exists():
        raise SystemExit(f"Missing template directory: {template_root}")
    if not template_root.is_dir():
        raise SystemExit(f"Template root is not a directory: {template_root}")

    if dest_root.exists():
        if not force and any(dest_root.iterdir()):
            raise SystemExit(
                f"Destination exists and is not empty: {dest_root} (use --force to overwrite)."
            )
    dest_root.mkdir(parents=True, exist_ok=True)

    for src in sorted(template_root.rglob("*")):
        rel = src.relative_to(template_root)
        dst = dest_root / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue

        if dst.exists() and not force:
            continue

        suffix = src.suffix.lower()
        if suffix in TEXT_EXTENSIONS:
            raw = src.read_text(encoding="utf-8", errors="replace")
            rendered = _render_template(raw, mapping)
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(rendered.rstrip() + "\n", encoding="utf-8", newline="\n")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)


@dataclass(frozen=True)
class WorkspacePlan:
    platform: str
    slug: str
    engagement_url: str
    created_at_utc: str
    output_dir: Path
    template_dir: Path


def plan_workspace(
    *,
    platform,
    slug,
    engagement_url,
    out_root,
    template_dir,
):
    platform = str(platform or "").strip()
    slug = str(slug or "").strip()
    if not platform:
        raise SystemExit("Missing --platform.")
    if not slug:
        raise SystemExit("Missing --slug.")

    created_at = _utc_now_iso()
    out_root = Path(out_root)
    template_dir = Path(template_dir)

    url = str(engagement_url or "").strip()
    if not url and platform.lower() == "bugcrowd":
        url = f"https://bugcrowd.com/engagements/{slug}"

    output_dir = out_root / platform / slug
    return WorkspacePlan(
        platform=platform,
        slug=slug,
        engagement_url=url,
        created_at_utc=created_at,
        output_dir=output_dir,
        template_dir=template_dir,
    )


def create_workspace(plan, *, force=False):
    mapping = {
        "{{platform}}": plan.platform,
        "{{slug}}": plan.slug,
        "{{engagement_url}}": plan.engagement_url,
        "{{created_at_utc}}": plan.created_at_utc,
    }
    _copy_template_tree(plan.template_dir, plan.output_dir, mapping, force=force)
    return plan.output_dir


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Scaffold a local engagement workspace (notes, recon log, report draft)."
    )
    parser.add_argument(
        "--platform",
        default="bugcrowd",
        help="Platform name for workspace grouping (default: bugcrowd).",
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Engagement slug or short identifier (required).",
    )
    parser.add_argument(
        "--engagement-url",
        default="",
        help="Engagement URL to embed in templates (optional).",
    )
    parser.add_argument(
        "--out-root",
        default="output/engagements",
        help="Root folder for workspaces (default: output/engagements).",
    )
    parser.add_argument(
        "--template-dir",
        default="templates/engagement_workspace/skeleton",
        help="Template directory to copy (default: templates/engagement_workspace/skeleton).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files in the destination.",
    )
    args = parser.parse_args(argv)

    plan = plan_workspace(
        platform=args.platform,
        slug=args.slug,
        engagement_url=args.engagement_url,
        out_root=args.out_root,
        template_dir=args.template_dir,
    )
    out_dir = create_workspace(plan, force=args.force)
    print(str(out_dir))


if __name__ == "__main__":
    main()
