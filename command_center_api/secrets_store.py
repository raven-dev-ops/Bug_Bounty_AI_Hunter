from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class SecretProvider:
    name = "base"

    def resolve(self, key: str) -> str:
        raise NotImplementedError


class EnvSecretProvider(SecretProvider):
    name = "env"

    def resolve(self, key: str) -> str:
        value = os.getenv(key)
        if value is None:
            raise KeyError(f"missing environment secret: {key}")
        return value


class JsonFileSecretProvider(SecretProvider):
    name = "file"

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def resolve(self, key: str) -> str:
        if not self.path.exists():
            raise KeyError(f"secrets file not found: {self.path}")
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise KeyError("secrets file must contain a JSON object")
        value = payload.get(key)
        if value is None:
            raise KeyError(f"secret key missing in file: {key}")
        return str(value)


class VaultAliasProvider(SecretProvider):
    name = "vault"

    def resolve(self, key: str) -> str:
        env_name = f"VAULT_{key.upper().replace('-', '_')}"
        value = os.getenv(env_name)
        if value is None:
            raise KeyError(f"missing vault alias secret: {env_name}")
        return value


def parse_secret_ref(ref: str) -> tuple[str, str]:
    text = ref.strip()
    if text.startswith("vault://"):
        return "vault", text[len("vault://") :]
    if ":" in text:
        provider, key = text.split(":", 1)
        return provider.strip().lower(), key.strip()
    return "env", text


def resolve_secret(
    ref: str,
    *,
    file_path: str | None = None,
) -> str:
    provider_name, key = parse_secret_ref(ref)
    providers: dict[str, SecretProvider] = {
        "env": EnvSecretProvider(),
        "vault": VaultAliasProvider(),
    }
    if file_path:
        providers["file"] = JsonFileSecretProvider(file_path)
    provider = providers.get(provider_name)
    if provider is None:
        raise KeyError(f"unsupported secret provider: {provider_name}")
    return provider.resolve(key)


def redact_secret(value: str, *, keep: int = 4) -> str:
    if len(value) <= keep:
        return "*" * len(value)
    return "*" * (len(value) - keep) + value[-keep:]


def build_rotation_plan(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for item in items:
        ref = str(item.get("ref") or "").strip()
        if not ref:
            continue
        interval_days = int(item.get("rotation_days") or 90)
        plan.append(
            {
                "ref": ref,
                "rotation_days": max(1, interval_days),
                "owner": str(item.get("owner") or "security"),
            }
        )
    return plan
