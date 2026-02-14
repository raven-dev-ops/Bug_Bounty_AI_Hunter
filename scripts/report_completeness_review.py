import argparse
import json
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from .lib.io_utils import dump_data, load_data


def _timestamp():
    return datetime.now(timezone.utc).isoformat()


def _list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _load_findings(path):
    if not path:
        return []
    data = load_data(path)
    if isinstance(data, dict) and "findings" in data:
        return _list(data.get("findings"))
    if isinstance(data, dict):
        return [data]
    return _list(data)


def _load_repro_steps(path):
    if not path:
        return []
    data = load_data(path)
    if isinstance(data, dict) and "steps" in data:
        steps = data.get("steps")
    else:
        steps = data
    if not isinstance(steps, list):
        raise SystemExit("Repro steps must be a list of strings.")
    return [str(step) for step in steps if step]


def _missing_impact(findings):
    missing = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        if not finding.get("impact"):
            missing.append(finding.get("id") or finding.get("title") or "unknown")
    return missing


def _missing_evidence(findings):
    missing = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        refs = finding.get("evidence_refs")
        if not refs:
            missing.append(finding.get("id") or finding.get("title") or "unknown")
    return missing


def _scope_proof_missing(report_text):
    if not report_text:
        return True
    if "## Scope" not in report_text:
        return True
    if "Scope not provided." in report_text:
        return True
    return False


def _roe_confirmed(checklist_text):
    if not checklist_text:
        return None
    for line in checklist_text.splitlines():
        if "ROE confirmed" in line:
            return "[x]" in line.lower()
    return None


def _ai_prompt(summary, report_text, mode):
    lines = [
        "You are a report completeness reviewer. Respond with JSON only.",
        "Keys: missing_repro_steps, missing_impact, missing_evidence, missing_scope, missing_roe_notes, notes.",
        "Do not generate exploit steps or prohibited guidance.",
        "Summary:",
        summary,
    ]
    if mode == "full" and report_text:
        lines.append("Report text:")
        lines.append(report_text[:4000])
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
            {"role": "system", "content": "You are a report completeness reviewer."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    request = Request(endpoint, data=json.dumps(payload).encode("utf-8"))
    request.add_header("Content-Type", "application/json")
    request.add_header("Authorization", f"Bearer {api_key}")
    with urlopen(request, timeout=config.get("timeout_seconds", 10)) as response:
        data = json.loads(response.read().decode("utf-8"))
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return _parse_ai_json(content or "")


def _load_ai_config(
    path, provider, model, endpoint, api_key_env, allow_data, input_mode
):
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


def _ai_review(summary, report_text, config):
    input_mode = config.get("input_mode", "minimal")
    if input_mode == "full" and not config.get("allow_data"):
        raise SystemExit("Full AI input requires allow_data: true in config.")
    prompt = _ai_prompt(summary, report_text, input_mode)
    provider = config.get("provider", "ollama")
    if provider == "ollama":
        return _call_ollama(prompt, config)
    if provider == "openai":
        return _call_openai(prompt, config)
    raise SystemExit(f"Unsupported AI provider: {provider}")


def main():
    parser = argparse.ArgumentParser(
        description="Review report completeness without generating exploit steps."
    )
    parser.add_argument("--report", help="Report markdown path.")
    parser.add_argument("--findings", help="Findings JSON/YAML path.")
    parser.add_argument("--repro-steps", help="Repro steps JSON/YAML path.")
    parser.add_argument("--compliance-checklist", help="Compliance checklist path.")
    parser.add_argument(
        "--output",
        default="data/report_completeness_review.json",
        help="Review output JSON/YAML path.",
    )
    parser.add_argument("--ai-enabled", action="store_true", help="Enable AI review.")
    parser.add_argument("--ai-config", help="AI config JSON/YAML path.")
    parser.add_argument("--ai-provider", help="AI provider (ollama or openai).")
    parser.add_argument("--ai-model", help="Model name.")
    parser.add_argument("--ai-endpoint", help="Override AI endpoint.")
    parser.add_argument("--ai-api-key-env", help="Env var holding API key.")
    parser.add_argument("--ai-allow-data", action="store_true")
    parser.add_argument(
        "--ai-input", choices=["minimal", "full"], help="AI input detail level."
    )
    args = parser.parse_args()

    report_text = ""
    if args.report:
        report_text = open(args.report, "r", encoding="utf-8").read()
    checklist_text = ""
    if args.compliance_checklist:
        checklist_text = open(args.compliance_checklist, "r", encoding="utf-8").read()

    findings = _load_findings(args.findings)
    repro_steps = _load_repro_steps(args.repro_steps)

    missing_impact = _missing_impact(findings)
    missing_evidence = _missing_evidence(findings)
    missing_scope = _scope_proof_missing(report_text)
    roe_confirmed = _roe_confirmed(checklist_text)

    summary = {
        "findings_total": len(findings),
        "missing_impact_count": len(missing_impact),
        "missing_evidence_count": len(missing_evidence),
        "missing_repro_steps": len(repro_steps) == 0,
        "missing_scope_proof": missing_scope,
        "roe_confirmed": roe_confirmed,
    }

    ai_result = None
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
        ai_result = _ai_review(json.dumps(summary), report_text, ai_config)

    output = {
        "schema_version": "0.1.0",
        "generated_at": _timestamp(),
        "summary": summary,
        "missing": {
            "impact": missing_impact,
            "evidence_refs": missing_evidence,
            "repro_steps": len(repro_steps) == 0,
            "scope_proof": missing_scope,
            "roe_confirmed": roe_confirmed is False,
        },
        "ai_used": bool(args.ai_enabled),
        "ai_review": ai_result,
    }
    dump_data(args.output, output)


if __name__ == "__main__":
    main()
