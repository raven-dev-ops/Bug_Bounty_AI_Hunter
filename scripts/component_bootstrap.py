import argparse
from pathlib import Path

from .lib.io_utils import dump_data


def _parse_csv(value, default=None):
    if value is None:
        return default or []
    if isinstance(value, list):
        return [item.strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _parse_entrypoints(values):
    entrypoints = {}
    for value in values or []:
        if "=" not in value:
            raise SystemExit("Entry point must be capability=module:function")
        capability, target = value.split("=", 1)
        capability = capability.strip()
        target = target.strip()
        if not capability or not target:
            raise SystemExit("Entry point must include both capability and target")
        entrypoints[capability] = target
    return entrypoints


def _render_readme(name, description):
    desc = description or "Component description."
    return "\n".join(
        [
            f"# {name}",
            "",
            desc,
            "",
            "## Purpose",
            "- Describe the component capability and its scope.",
            "- Align with hub schemas and safe review guidance.",
            "",
            "## Usage",
            "- Update `component_manifest.yaml` with capabilities and schemas.",
            "- Add scripts, modules, or CLI entrypoints as needed.",
            "",
            "## Structure",
            "- `component_manifest.yaml`",
            "- `README.md`",
            "- `docs/` (optional)",
            "- `examples/` (optional)",
            "- `tests/` (optional)",
            "",
            "## Safety",
            "Follow the hub ROE guidance and keep content non-weaponized.",
            "",
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="Scaffold a component repo.")
    parser.add_argument("--name", required=True, help="Component name.")
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: components/<name>).",
    )
    parser.add_argument("--description", help="Short component description.")
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument(
        "--schema-version",
        default="0.1.0",
        help="Component manifest schema version.",
    )
    parser.add_argument(
        "--capabilities",
        default="review",
        help="Comma-separated capabilities (default: review).",
    )
    parser.add_argument("--repository", help="Repository URL.")
    parser.add_argument("--license", default="Apache-2.0")
    parser.add_argument("--contact", default="support@ravdevops.com")
    parser.add_argument(
        "--entrypoint",
        action="append",
        help="Capability entrypoint mapping: capability=module:function",
    )
    parser.add_argument(
        "--schema-target-profile",
        default=">=0.2.0",
        help="TargetProfile schema constraint.",
    )
    parser.add_argument(
        "--schema-test-case",
        default=">=0.1.0",
        help="TestCase schema constraint.",
    )
    parser.add_argument(
        "--schema-finding",
        default=">=0.1.0",
        help="Finding schema constraint.",
    )
    parser.add_argument(
        "--schema-evidence",
        default=">=0.1.0",
        help="Evidence schema constraint.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files in the output directory.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir or f"components/{args.name}")
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.force:
        existing = [path for path in output_dir.iterdir()]
        if existing:
            raise SystemExit(
                f"Output directory is not empty: {output_dir}. Use --force to overwrite."
            )

    capabilities = _parse_csv(args.capabilities, default=["review"])
    if not capabilities:
        raise SystemExit("At least one capability is required.")

    manifest = {
        "schema_version": args.schema_version,
        "name": args.name,
        "version": args.version,
        "capabilities": capabilities,
        "schemas": {
            "target_profile": args.schema_target_profile,
            "test_case": args.schema_test_case,
            "finding": args.schema_finding,
            "evidence": args.schema_evidence,
        },
        "description": args.description or "Component description.",
        "license": args.license,
        "contact": args.contact,
    }
    if args.repository:
        manifest["repository"] = args.repository
    entrypoints = _parse_entrypoints(args.entrypoint)
    if entrypoints:
        manifest["entrypoints"] = entrypoints

    manifest_path = output_dir / "component_manifest.yaml"
    dump_data(manifest_path, manifest)

    readme_path = output_dir / "README.md"
    readme_path.write_text(
        _render_readme(args.name, args.description), encoding="utf-8"
    )

    print(f"Component scaffold created at {output_dir}")


if __name__ == "__main__":
    main()
