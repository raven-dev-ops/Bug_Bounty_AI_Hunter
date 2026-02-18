from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


PLUGIN_DIR = Path("plugins")


def _load_python_module(path: Path) -> Any:
    module_name = f"command_center_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load plugin module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_plugins(*, plugin_dir: Path | str = PLUGIN_DIR) -> list[dict[str, Any]]:
    root = Path(plugin_dir)
    if not root.exists():
        return []
    results: list[dict[str, Any]] = []
    for candidate in sorted(root.glob("*.py")):
        if candidate.name.startswith("_"):
            continue
        try:
            module = _load_python_module(candidate)
        except Exception as exc:  # pragma: no cover - surfaced in API response
            results.append(
                {
                    "name": candidate.stem,
                    "status": "error",
                    "error": str(exc),
                }
            )
            continue
        plugin_meta = getattr(module, "PLUGIN", None)
        if isinstance(plugin_meta, dict):
            item = dict(plugin_meta)
            item.setdefault("name", candidate.stem)
            item["status"] = "loaded"
            results.append(item)
        else:
            results.append(
                {
                    "name": candidate.stem,
                    "status": "loaded",
                    "type": "generic",
                }
            )
    return results
