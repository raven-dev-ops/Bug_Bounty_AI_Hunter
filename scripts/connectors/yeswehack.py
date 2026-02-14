from scripts.lib import catalog_parsers
from scripts.lib.scope_utils import normalize_scope_assets

from .base import Connector
from .registry import register
from .utils import (
    apply_provenance,
    load_text_source,
    parse_program_cards,
    parse_program_detail,
)


LIST_URL = "https://yeswehack.com/programs"


def _load_html(fetcher, fixtures_dir, connector_name, filename, url):
    return load_text_source(fetcher, fixtures_dir, connector_name, filename, url)


def _build_program(platform, card):
    handle = card.get("handle")
    program = {
        "source": platform,
        "platform": platform,
        "handle": handle,
        "name": card.get("name"),
        "policy_url": card.get("url"),
        "url": card.get("url"),
    }
    if handle:
        program["source_id"] = f"{platform}:{handle}"

    reward_text = card.get("reward")
    reward = catalog_parsers.parse_reward_range(reward_text)
    if reward:
        program["rewards"] = reward

    return program


def _apply_detail(program, detail, platform):
    merged = dict(program)
    if detail.get("name"):
        merged["name"] = detail["name"]
    if detail.get("url"):
        merged["policy_url"] = detail["url"]
        merged["url"] = detail["url"]
    if detail.get("handle"):
        merged["handle"] = detail["handle"]
        merged["source_id"] = f"{platform}:{detail['handle']}"

    reward = catalog_parsers.parse_reward_range(detail.get("rewards"))
    if reward:
        merged["rewards"] = reward

    response = catalog_parsers.parse_response_time(detail.get("response_time"))
    if response:
        merged["response_time"] = response

    safe_harbor = catalog_parsers.parse_safe_harbor(detail.get("safe_harbor"))
    if safe_harbor:
        merged["safe_harbor"] = safe_harbor

    restrictions = catalog_parsers.extract_restrictions(detail.get("restrictions"))
    if restrictions:
        merged["restrictions"] = restrictions

    in_scope, in_errors = normalize_scope_assets(detail.get("in_scope"))
    out_scope, out_errors = normalize_scope_assets(detail.get("out_scope"))
    scope = {}
    if in_scope:
        scope["in_scope"] = in_scope
    if out_scope:
        scope["out_of_scope"] = out_scope
    if scope:
        merged["scope"] = scope

    errors = in_errors + out_errors
    if errors:
        merged["notes"] = "Scope normalization issues: " + "; ".join(errors)

    return merged


class YesWeHackConnector(Connector):
    name = "yeswehack"

    def list_programs(self, fetcher, fixtures_dir=None):
        html, _, _, _ = _load_html(
            fetcher, fixtures_dir, self.name, "programs.html", LIST_URL
        )
        cards = parse_program_cards(html)
        return [_build_program(self.name, card) for card in cards]

    def fetch_details(self, fetcher, program, fixtures_dir=None):
        handle = program.get("handle")
        if fixtures_dir:
            filename = f"program-{handle}.html"
        else:
            filename = None
        url = program.get("policy_url") or program.get("url")
        html, metadata, artifact_hash, artifact_path = _load_html(
            fetcher, fixtures_dir, self.name, filename, url
        )
        detail = parse_program_detail(html)
        merged = _apply_detail(program, detail, self.name)
        apply_provenance(merged, metadata, artifact_hash, artifact_path)
        return merged


register(YesWeHackConnector())
