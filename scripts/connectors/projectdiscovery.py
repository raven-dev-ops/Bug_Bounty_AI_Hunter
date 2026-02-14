import os
import re

from scripts.lib import catalog_parsers
from scripts.lib.scope_utils import normalize_scope_assets

from .base import Connector
from .registry import register
from .utils import (
    apply_provenance,
    coerce_list,
    extract_records,
    first_value,
    load_json_source,
)


DEFAULT_URLS = [
    "https://raw.githubusercontent.com/projectdiscovery/public-bugbounty-programs/main/chaos-bugbounty-list.json"
]
ENV_VAR = "BBHAI_PROJECTDISCOVERY_URL"
SLUG_RE = re.compile(r"[^a-z0-9]+")


def _dataset_urls():
    override = os.environ.get(ENV_VAR, "").strip()
    if override:
        return [item for item in override.replace(",", " ").split() if item]
    return DEFAULT_URLS


def _slugify(value):
    text = SLUG_RE.sub("-", str(value or "").lower()).strip("-")
    return text or "unknown"


def _flatten_targets(value):
    items = coerce_list(value)
    cleaned = []
    for item in items:
        if isinstance(item, dict):
            candidate = first_value(item, ("target", "asset", "value", "url", "name"))
            if candidate:
                cleaned.append(candidate)
        else:
            cleaned.append(item)
    return cleaned


def _extract_scope(record):
    targets = first_value(record, ("targets", "scope", "assets"))
    in_scope = first_value(record, ("in_scope", "inScope"))
    out_scope = first_value(record, ("out_of_scope", "outScope"))
    if isinstance(targets, dict):
        if not in_scope:
            in_scope = first_value(targets, ("in_scope", "inScope", "targets"))
        if not out_scope:
            out_scope = first_value(targets, ("out_of_scope", "outScope"))
    elif isinstance(targets, list) and not in_scope:
        in_scope = targets

    in_items = _flatten_targets(in_scope)
    out_items = _flatten_targets(out_scope)
    in_scope_norm, in_errors = normalize_scope_assets(in_items)
    out_scope_norm, out_errors = normalize_scope_assets(out_items)
    scope = {}
    if in_scope_norm:
        scope["in_scope"] = in_scope_norm
    if out_scope_norm:
        scope["out_of_scope"] = out_scope_norm
    return scope, in_errors + out_errors


def _build_program(record, source):
    name = first_value(record, ("name", "program", "organization"))
    handle = first_value(record, ("handle", "slug", "program_handle", "code"))
    platform = first_value(record, ("platform", "platform_name"))
    policy_url = first_value(record, ("policy_url", "program_url", "url"))
    reward_value = first_value(record, ("reward", "rewards", "bounty"))
    safe_harbor_text = first_value(
        record, ("safe_harbor", "safeHarbor", "safe_harbor_text")
    )
    response_time_text = first_value(record, ("response_time", "responseTime"))
    restriction_value = first_value(record, ("restrictions", "rules", "notes"))

    program = {
        "source": source,
        "platform": platform,
        "handle": handle,
        "name": name,
        "policy_url": policy_url,
        "url": policy_url,
    }
    if handle and platform:
        program["source_id"] = f"{platform}:{handle}"
    elif handle:
        program["source_id"] = f"{source}:{handle}"
    elif name:
        program["source_id"] = f"{source}:{_slugify(name)}"

    if reward_value is not None:
        if isinstance(reward_value, dict):
            program["rewards"] = reward_value
        else:
            reward = catalog_parsers.parse_reward_range(str(reward_value))
            if reward:
                program["rewards"] = reward

    response = catalog_parsers.parse_response_time(response_time_text)
    if response:
        program["response_time"] = response

    safe_harbor = catalog_parsers.parse_safe_harbor(safe_harbor_text)
    if safe_harbor:
        program["safe_harbor"] = safe_harbor

    restrictions = catalog_parsers.extract_restrictions(restriction_value)
    if restrictions:
        program["restrictions"] = restrictions

    scope, scope_errors = _extract_scope(record)
    if scope:
        program["scope"] = scope
    if scope_errors:
        program["notes"] = "Scope normalization issues: " + "; ".join(scope_errors)

    return program


class ProjectDiscoveryConnector(Connector):
    name = "projectdiscovery"

    def list_programs(self, fetcher, fixtures_dir=None):
        sources = []
        if fixtures_dir:
            data, metadata, artifact_hash, artifact_path = load_json_source(
                fetcher,
                fixtures_dir,
                "projectdiscovery",
                "programs.json",
                None,
            )
            sources.append(
                (extract_records(data), metadata, artifact_hash, artifact_path)
            )
        else:
            for url in _dataset_urls():
                data, metadata, artifact_hash, artifact_path = load_json_source(
                    fetcher,
                    fixtures_dir,
                    "projectdiscovery",
                    "programs.json",
                    url,
                )
                sources.append(
                    (extract_records(data), metadata, artifact_hash, artifact_path)
                )

        programs = []
        for records, metadata, artifact_hash, artifact_path in sources:
            for record in records:
                if not isinstance(record, dict):
                    continue
                program = _build_program(record, self.name)
                apply_provenance(program, metadata, artifact_hash, artifact_path)
                programs.append(program)
        return programs

    def fetch_details(self, fetcher, program, fixtures_dir=None):
        return program


register(ProjectDiscoveryConnector())
