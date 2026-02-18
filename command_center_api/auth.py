from __future__ import annotations

import base64
import hashlib
import json
import secrets
import time
from datetime import datetime, timezone
from typing import Any

from command_center_api import db


DEFAULT_SESSION_TTL_SECONDS = 3600


def _parse_timestamp(text: str) -> datetime | None:
    cleaned = text.strip()
    if not cleaned:
        return None
    if cleaned.endswith("Z"):
        cleaned = f"{cleaned[:-1]}+00:00"
    try:
        value = datetime.fromisoformat(cleaned)
    except ValueError:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _b64url_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)


def decode_jwt_payload(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("invalid JWT format")
    payload_raw = _b64url_decode(parts[1])
    payload = json.loads(payload_raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid JWT payload")
    return payload


def parse_oidc_assertion(
    *,
    id_token: str,
    expected_issuer: str | None = None,
    expected_audience: str | None = None,
) -> dict[str, Any]:
    payload = decode_jwt_payload(id_token)
    subject = str(payload.get("sub") or "").strip()
    if not subject:
        raise ValueError("OIDC token missing sub claim")
    expires_at = payload.get("exp")
    if isinstance(expires_at, (int, float)) and int(expires_at) < int(time.time()):
        raise ValueError("OIDC token expired")
    if expected_issuer:
        issuer = str(payload.get("iss") or "").strip()
        if issuer != expected_issuer:
            raise ValueError("OIDC token issuer mismatch")
    if expected_audience:
        audience = payload.get("aud")
        if isinstance(audience, list):
            valid = expected_audience in audience
        else:
            valid = str(audience or "") == expected_audience
        if not valid:
            raise ValueError("OIDC token audience mismatch")
    return payload


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def issue_session_token(
    connection: Any,
    *,
    principal_id: str,
    org_id: str,
    ttl_seconds: int = DEFAULT_SESSION_TTL_SECONDS,
) -> dict[str, str | int]:
    now = int(time.time())
    ttl = max(60, int(ttl_seconds))
    token = f"ccs_{secrets.token_urlsafe(32)}"
    db.create_session(
        connection,
        session_id=f"session:{secrets.token_hex(16)}",
        principal_id=principal_id,
        org_id=org_id,
        token_hash=hash_session_token(token),
        issued_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        expires_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + ttl)),
    )
    return {"access_token": token, "token_type": "Bearer", "expires_in": ttl}


def get_session_context(connection: Any, bearer_token: str) -> dict[str, Any] | None:
    session = db.get_session_by_token_hash(connection, hash_session_token(bearer_token))
    if session is None:
        return None
    expires_at = _parse_timestamp(str(session.get("expires_at") or ""))
    if expires_at is not None and expires_at <= datetime.now(timezone.utc):
        return None
    principal = db.get_principal(connection, session["principal_id"])
    if principal is None:
        return None
    bindings = db.list_role_bindings_for_principal(
        connection,
        principal_id=session["principal_id"],
        org_id=str(session["org_id"]),
    )
    roles = sorted({binding["role"] for binding in bindings})
    all_bindings = db.list_role_bindings_for_principal(
        connection,
        principal_id=session["principal_id"],
    )
    all_roles = sorted({binding["role"] for binding in all_bindings})
    return {
        "session": session,
        "principal": principal,
        "org_id": session["org_id"],
        "bindings": all_bindings,
        "roles": roles,
        "all_roles": all_roles,
    }


def ensure_roles(
    context: dict[str, Any] | None,
    required_roles: set[str],
    *,
    org_id: str | None = None,
) -> None:
    if context is None:
        raise PermissionError("authentication required")
    if org_id is None:
        roles = set(context.get("all_roles") or context.get("roles") or [])
    else:
        bindings = context.get("bindings") or []
        roles = {
            str(binding.get("role") or "")
            for binding in bindings
            if str(binding.get("org_id") or "") == org_id
        }
    if roles.intersection(required_roles):
        return
    raise PermissionError("insufficient role")
