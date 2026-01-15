import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data
from lib.rate_limit import RateLimiter


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_templates(templates_dir):
    templates = []
    path = Path(templates_dir)
    if not path.exists():
        raise SystemExit(f"Templates directory not found: {path}")

    for template_path in sorted(path.rglob("*")):
        if template_path.suffix.lower() not in (".yaml", ".yml", ".json"):
            continue
        template = load_data(template_path)
        if not isinstance(template, dict):
            continue
        if not template.get("id") or not template.get("name"):
            continue
        template["path"] = str(template_path)
        templates.append(template)
    return templates


def _targets_from_input(data):
    if isinstance(data, dict) and "assets" in data:
        return _list(data.get("assets"))
    if isinstance(data, dict) and "scope" in data:
        scope = data.get("scope", {})
        return _list(scope.get("in_scope"))
    return _list(data)


def _target_types_for_asset(asset_type):
    asset_type = (asset_type or "").lower()
    types = {asset_type} if asset_type else set()
    if asset_type in ("domain", "subdomain"):
        types.add("url")
    return types


def _base_url(value):
    if value.startswith("http://") or value.startswith("https://"):
        return value.rstrip("/")
    return f"https://{value}".rstrip("/")


def _render_text(text, context):
    return str(text).format_map(SafeDict(context))


def _render_test_case(template, asset, index, canary):
    asset_value = asset.get("value", "")
    context = {
        "target": asset_value,
        "asset": asset_value,
        "type": asset.get("type", ""),
        "base_url": _base_url(asset_value),
        "canary": canary,
    }
    steps = [_render_text(step, context) for step in _list(template.get("steps"))]
    expected = [
        _render_text(item, context) for item in _list(template.get("expected_results"))
    ]
    stop_conditions = [
        _render_text(item, context) for item in _list(template.get("stop_conditions"))
    ]

    return {
        "schema_version": "0.1.0",
        "id": f"tc-{template['id']}-{index:04d}",
        "title": f"{template['name']} on {asset_value}",
        "objective": template.get("description", ""),
        "steps": steps,
        "stop_conditions": stop_conditions,
        "expected_results": expected,
        "safety_notes": "Follow ROE and use canary strings only.",
        "template_id": template["id"],
        "target": asset_value,
    }


def _matches_template(template, asset):
    target_types = _list(template.get("target_types"))
    if not target_types:
        return True
    asset_types = _target_types_for_asset(asset.get("type"))
    return bool(asset_types.intersection({t.lower() for t in target_types}))


def build_scan_plan(templates, assets, canary, limits):
    tasks = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        for template in templates:
            if _matches_template(template, asset):
                tasks.append((template, asset))

    limiter = RateLimiter(limits.get("min_delay_seconds"))
    max_workers = max(1, int(limits.get("max_concurrency") or 1))
    results = []

    def worker(item_index, task):
        limiter.wait()
        template, asset = task
        return _render_test_case(template, asset, item_index, canary)

    if max_workers == 1:
        for index, task in enumerate(tasks, start=1):
            results.append(worker(index, task))
        return results

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(worker, index, task): index
            for index, task in enumerate(tasks, start=1)
        }
        for future in as_completed(future_map):
            results.append(future.result())

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate scan plans from templates and targets."
    )
    parser.add_argument("--templates", required=True, help="Templates directory.")
    parser.add_argument("--targets", required=True, help="Target profile or discovery.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    parser.add_argument("--canary", default="CANARY-1234")
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--min-delay-seconds", type=float, default=0.0)
    args = parser.parse_args()

    templates = _load_templates(args.templates)
    target_data = load_data(args.targets)
    assets = _targets_from_input(target_data)
    limits = {
        "max_concurrency": args.max_concurrency,
        "min_delay_seconds": args.min_delay_seconds,
    }

    tests = build_scan_plan(templates, assets, args.canary, limits)
    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "plan",
        "templates": [template["id"] for template in templates],
        "targets": [asset.get("value") for asset in assets if isinstance(asset, dict)],
        "tests": tests,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
