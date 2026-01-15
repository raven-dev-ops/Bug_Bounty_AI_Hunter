import argparse
from pathlib import Path

from .lib.io_utils import dump_data, load_data
from .pipeline_orchestrator import build_command


def _ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def _rewrite_output_paths(config, output_dir):
    output_dir = Path(output_dir)
    for stage in config.get("stages", []):
        config_map = stage.get("config", {}) or {}
        output_value = config_map.get("output")
        if isinstance(output_value, str) and output_value.strip():
            filename = Path(output_value).name
            config_map["output"] = str(output_dir / filename)
        output_dir_value = config_map.get("output_dir")
        if isinstance(output_dir_value, str) and output_dir_value.strip():
            config_map["output_dir"] = str(output_dir / Path(output_dir_value).name)
        stage["config"] = config_map
    return config


def _write_command_log(commands, output_path):
    payload = {
        "schema_version": "0.1.0",
        "plan": [{"stage": cmd["stage"], "argv": cmd["argv"]} for cmd in commands],
    }
    dump_data(output_path, payload)


def _run_command(command, dry_run):
    if dry_run:
        return
    import subprocess

    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description="Run the demo pipeline.")
    parser.add_argument(
        "--config",
        default="examples/pipeline_config.yaml",
        help="Pipeline config path.",
    )
    parser.add_argument(
        "--output-dir",
        default="output/demo",
        help="Output directory for demo artifacts.",
    )
    parser.add_argument(
        "--mode",
        default="plan",
        choices=["plan", "run"],
        help="Plan or run the pipeline.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    _ensure_dir(output_dir)

    # Normalize outputs into the demo directory.
    config_path = Path(args.config)
    config = load_data(config_path)
    if config_path.name == "pipeline_config.yaml":
        demo_config = output_dir / "pipeline_config.demo.yaml"
        config = _rewrite_output_paths(config, output_dir)
        dump_data(demo_config, config)
        config_path = demo_config

    stages = config.get("stages", [])
    commands = []
    for stage in stages:
        cmd = build_command(stage)
        commands.append({"stage": stage.get("name"), "argv": cmd})

    _write_command_log(commands, output_dir / "pipeline_plan.json")

    if args.mode == "plan":
        return

    for command in commands:
        _run_command(command["argv"], dry_run=False)


if __name__ == "__main__":
    main()
