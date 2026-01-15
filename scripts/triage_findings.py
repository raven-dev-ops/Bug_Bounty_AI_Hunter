import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from lib.io_utils import dump_data, load_data


SEVERITY_PRIORITY = {
    "critical": "p0",
    "high": "p1",
    "medium": "p2",
    "low": "p3",
    "info": "p3",
}

SEVERITY_CONFIDENCE = {
    "critical": 0.85,
    "high": 0.75,
    "medium": 0.6,
    "low": 0.5,
    "info": 0.4,
}


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_severity(item):
    severity = str(item.get("severity", "")).lower()
    if severity in SEVERITY_PRIORITY:
        return severity

    impact = str(item.get("impact", "")).lower()
    for key in ("critical", "high", "medium", "low"):
        if key in impact:
            return key
    return "info"


def _triage_item(item, index, source):
    severity = _normalize_severity(item)
    return {
        "id": item.get("id") or f"triage-{index:04d}",
        "title": item.get("title") or item.get("name") or "Untitled item",
        "severity": severity,
        "priority": SEVERITY_PRIORITY.get(severity, "p3"),
        "status": "triaged" if source == "findings" else "needs-validation",
        "source": source,
        "rationale": f"Severity derived as {severity}.",
        "confidence": SEVERITY_CONFIDENCE.get(severity, 0.4),
        "next_tests": [],
        "ai_used": False,
    }


def _ai_prompt(item, input_mode):
    title = item.get("title") or item.get("name") or "Untitled item"
    severity = item.get("severity", "")
    impact = item.get("impact", "")
    description = item.get("description", "")
    remediation = item.get("remediation", "")

    lines = [
        "You are a security triage assistant. Respond with JSON only.",
        "Keys: severity, confidence (0-1), rationale, next_tests (array).",
        "Use safe, non-weaponized phrasing.",
        f"Title: {title}",
        f"Severity hint: {severity}",
        f"Impact: {impact}",
    ]

    if input_mode == "full":
        lines.append(f"Description: {description}")
        lines.append(f"Remediation: {remediation}")

    return "\n".join(line for line in lines if line.strip())


def _parse_ai_json(text):
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return {}


def _call_ollama(prompt, config):
    endpoint = config.get("endpoint") or "http://localhost:11434/api/generate"
    payload = {
        "model": config.get("model") or "llama3",
        "prompt": prompt,
        "stream": False,
    }
    request = Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=config.get("timeout_seconds", 10)) as response:
        data = json.loads(response.read().decode("utf-8"))
    return _parse_ai_json(data.get("response", ""))


def _call_openai(prompt, config):
    endpoint = config.get("endpoint") or "https://api.openai.com/v1/chat/completions"
    api_key = config.get("api_key")
    if not api_key:
        raise SystemExit("OpenAI API key not provided.")
    payload = {
        "model": config.get("model") or "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a security triage assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    request = Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    with urlopen(request, timeout=config.get("timeout_seconds", 10)) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )
    return _parse_ai_json(content or "")


def _ai_triage(item, config):
    input_mode = config.get("input_mode", "minimal")
    if input_mode == "full" and not config.get("allow_data"):
        raise SystemExit("Full AI input requires allow_data: true in config.")

    prompt = _ai_prompt(item, input_mode)
    provider = config.get("provider", "ollama")
    if provider == "ollama":
        return _call_ollama(prompt, config)
    if provider == "openai":
        return _call_openai(prompt, config)
    raise SystemExit(f"Unsupported AI provider: {provider}")


def _load_ai_config(path, provider, model, endpoint, api_key_env, allow_data, input_mode):
    config = {}
    if path:
        config = load_data(path)
        if not isinstance(config, dict):
            raise SystemExit("AI config must be a mapping.")
    if provider:
        config["provider"] = provider
    if model:
        config["model"] = model
    if endpoint:
        config["endpoint"] = endpoint
    if api_key_env:
        config["api_key_env"] = api_key_env
    if allow_data is not None:
        config["allow_data"] = allow_data
    if input_mode:
        config["input_mode"] = input_mode

    if config.get("provider") == "openai" and not config.get("api_key_env"):
        config["api_key_env"] = "OPENAI_API_KEY"

    api_key_env = config.get("api_key_env")
    if api_key_env and not config.get("api_key"):
        config["api_key"] = os.environ.get(api_key_env)
    return config


def main():
    parser = argparse.ArgumentParser(description="Triage findings or scan plans.")
    parser.add_argument("--input", required=True, help="Input JSON/YAML path.")
    parser.add_argument("--output", required=True, help="Output JSON/YAML path.")
    parser.add_argument("--ai-enabled", action="store_true", help="Enable AI triage.")
    parser.add_argument("--ai-config", help="AI config JSON/YAML path.")
    parser.add_argument("--ai-provider", help="AI provider (ollama or openai).")
    parser.add_argument("--ai-model", help="Model name.")
    parser.add_argument("--ai-endpoint", help="Override AI endpoint.")
    parser.add_argument(
        "--ai-api-key-env",
        help="Environment variable holding the API key.",
    )
    parser.add_argument(
        "--ai-allow-data",
        action="store_true",
        help="Allow sending full input to AI.",
    )
    parser.add_argument(
        "--ai-input",
        choices=["minimal", "full"],
        help="Input detail level for AI.",
    )
    args = parser.parse_args()

    data = load_data(args.input)
    if isinstance(data, dict) and "findings" in data:
        items = _list(data.get("findings"))
        source = "findings"
    elif isinstance(data, dict) and "tests" in data:
        items = _list(data.get("tests"))
        source = "tests"
    else:
        items = _list(data)
        source = "items"

    ai_config = {}
    if args.ai_enabled:
        ai_config = _load_ai_config(
            args.ai_config,
            args.ai_provider,
            args.ai_model,
            args.ai_endpoint,
            args.ai_api_key_env,
            args.ai_allow_data if args.ai_enabled else None,
            args.ai_input,
        )

    triaged = []
    for index, item in enumerate(items, 1):
        triage = _triage_item(item, index, source)
        if args.ai_enabled:
            try:
                ai_result = _ai_triage(item, ai_config)
                ai_severity = str(ai_result.get("severity", "")).lower()
                if ai_severity in SEVERITY_PRIORITY:
                    triage["severity"] = ai_severity
                    triage["priority"] = SEVERITY_PRIORITY[ai_severity]
                ai_confidence = ai_result.get("confidence")
                if isinstance(ai_confidence, (int, float)):
                    triage["confidence"] = max(0.0, min(1.0, float(ai_confidence)))
                ai_rationale = ai_result.get("rationale")
                if ai_rationale:
                    triage["rationale"] = f"{triage['rationale']} AI: {ai_rationale}"
                ai_tests = ai_result.get("next_tests")
                if isinstance(ai_tests, list):
                    triage["next_tests"] = [str(test) for test in ai_tests if test]
                triage["ai_used"] = True
            except Exception as exc:
                triage["rationale"] = f"{triage['rationale']} AI: {exc}"
        triaged.append(triage)

    output = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": triaged,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
