from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


PLUGIN_DIR = Path("plugins")
REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = (REPO_ROOT / "plugins").resolve()


def _load_python_module(path: Path) -> Any:
    module_name = f"command_center_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load plugin module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def discover_plugins(*, plugin_dir: Path | str = PLUGIN_DIR) -> list[dict[str, Any]]:
    _ = plugin_dir
    root = PLUGIN_ROOT
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
                    "error": "failed to load plugin",
                    "error_type": exc.__class__.__name__,
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
