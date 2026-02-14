import hashlib
import json
import re
from pathlib import Path


def read_fixture(fixtures_dir, connector, filename):
    if not fixtures_dir:
        return None
    path = Path(fixtures_dir) / connector / filename
    return path.read_text(encoding="utf-8")


def _hash_text(text):
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_text_source(fetcher, fixtures_dir, connector, filename, url):
    if fixtures_dir:
        text = read_fixture(fixtures_dir, connector, filename)
        if text is None:
            raise SystemExit(f"Missing fixture: {connector}/{filename}")
        metadata = {"status": 200, "from_fixture": True}
        if url:
            metadata["url"] = url
        artifact_path = str(Path(connector) / filename)
    else:
        if fetcher is None:
            raise SystemExit("Fetcher is required for live requests.")
        text, metadata = fetcher.fetch_text(url)
        artifact_path = None
    artifact_hash = _hash_text(text)
    return text, metadata, artifact_hash, artifact_path


def load_json_source(fetcher, fixtures_dir, connector, filename, url):
    text, metadata, artifact_hash, artifact_path = load_text_source(
        fetcher, fixtures_dir, connector, filename, url
    )
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON for {connector}: {exc}") from exc
    return data, metadata, artifact_hash, artifact_path


def apply_provenance(record, metadata, artifact_hash, artifact_path=None):
    if not isinstance(record, dict):
        return
    if metadata:
        status = metadata.get("status")
        if status is not None:
            record["http_status"] = status
    if artifact_hash:
        record["artifact_hash"] = artifact_hash
        record["hash_algorithm"] = "sha256"
    if artifact_path:
        record["artifact_path"] = artifact_path


def extract_records(data):
    if isinstance(data, dict):
        for key in ("programs", "data", "items", "entries"):
            value = data.get(key)
            if isinstance(value, list):
                return value
        return [data]
    if isinstance(data, list):
        return data
    return []


def coerce_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def first_value(record, keys):
    if not isinstance(record, dict):
        return None
    for key in keys:
        value = record.get(key)
        if value is None or value == "" or value == [] or value == {}:
            continue
        return value
    return None


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _strip_tags(text):
    return re.sub(r"<[^>]+>", "", text or "")


def _extract_attribute(tag, name):
    match = re.search(rf'{name}="([^"]+)"', tag)
    return _clean_text(match.group(1)) if match else ""


def parse_program_cards(html):
    cards = []
    for tag in re.findall(r'<div class="program-card"[^>]*>', html):
        handle = _extract_attribute(tag, "data-handle")
        name = _extract_attribute(tag, "data-name")
        url = _extract_attribute(tag, "data-url")
        reward = _extract_attribute(tag, "data-reward")
        if not (handle or name or url):
            continue
        cards.append(
            {
                "handle": handle,
                "name": name,
                "url": url,
                "reward": reward,
            }
        )
    return cards


def _extract_list(html, class_name):
    match = re.search(
        rf'<ul class="{class_name}">(.*?)</ul>',
        html,
        re.S,
    )
    if not match:
        return []
    items = []
    for item in re.findall(r"<li>(.*?)</li>", match.group(1), re.S):
        text = _clean_text(_strip_tags(item))
        if text:
            items.append(text)
    return items


def _extract_field(html, field_name):
    match = re.search(
        rf'<div class="program-field" data-field="{field_name}">(.*?)</div>',
        html,
        re.S,
    )
    if not match:
        return ""
    return _clean_text(_strip_tags(match.group(1)))


def parse_program_detail(html):
    name_match = re.search(r'<h1 class="program-name">(.*?)</h1>', html, re.S)
    name = _clean_text(_strip_tags(name_match.group(1))) if name_match else ""

    detail_tag = ""
    detail_match = re.search(r'<div class="program-detail"[^>]*>', html)
    if detail_match:
        detail_tag = detail_match.group(0)

    return {
        "handle": _extract_attribute(detail_tag, "data-handle"),
        "url": _extract_attribute(detail_tag, "data-url"),
        "name": name,
        "rewards": _extract_field(html, "rewards"),
        "response_time": _extract_field(html, "response-time"),
        "safe_harbor": _extract_field(html, "safe-harbor"),
        "in_scope": _extract_list(html, "scope-in"),
        "out_scope": _extract_list(html, "scope-out"),
        "restrictions": _extract_list(html, "restrictions"),
    }
