import ipaddress
import re
from urllib.parse import urlparse


_DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9-]+$", re.IGNORECASE)
_PORT_SPEC_RE = re.compile(r"^[0-9,\\-]+$")


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _coerce_port(value, errors, label):
    try:
        port = int(value)
    except (TypeError, ValueError):
        errors.append(f"{label} port must be an integer.")
        return None
    if port < 1 or port > 65535:
        errors.append(f"{label} port out of range: {port}.")
        return None
    return port


def _collect_port_ranges(raw, ranges, errors):
    if raw is None:
        return

    if isinstance(raw, list):
        for item in raw:
            _collect_port_ranges(item, ranges, errors)
        return

    if isinstance(raw, dict):
        start = _coerce_port(raw.get("start"), errors, "Start")
        end = _coerce_port(raw.get("end", raw.get("start")), errors, "End")
        if start is None or end is None:
            return
        if start > end:
            errors.append(f"Port range start {start} is greater than end {end}.")
            return
        ranges.append((start, end))
        return

    if isinstance(raw, int):
        port = _coerce_port(raw, errors, "Port")
        if port is not None:
            ranges.append((port, port))
        return

    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return
        for part in text.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                if part.count("-") != 1:
                    errors.append(f"Invalid port range: {part}.")
                    continue
                start_text, end_text = [item.strip() for item in part.split("-", 1)]
                start = _coerce_port(start_text, errors, "Start")
                end = _coerce_port(end_text, errors, "End")
                if start is None or end is None:
                    continue
                if start > end:
                    errors.append(
                        f"Port range start {start} is greater than end {end}."
                    )
                    continue
                ranges.append((start, end))
            else:
                port = _coerce_port(part, errors, "Port")
                if port is not None:
                    ranges.append((port, port))
        return

    errors.append("Ports must be a number, string, list, or mapping.")


def normalize_port_ranges(raw):
    ranges = []
    errors = []
    _collect_port_ranges(raw, ranges, errors)

    deduped = []
    seen = set()
    for start, end in ranges:
        key = (start, end)
        if key in seen:
            continue
        seen.add(key)
        deduped.append({"start": start, "end": end})

    deduped.sort(key=lambda item: (item["start"], item["end"]))

    previous = None
    for entry in deduped:
        if previous and entry["start"] <= previous["end"]:
            errors.append(
                "Port ranges overlap: "
                f"{previous['start']}-{previous['end']} and "
                f"{entry['start']}-{entry['end']}."
            )
        previous = entry

    return deduped, errors


def _looks_like_port_spec(value):
    return bool(_PORT_SPEC_RE.match(value))


def _split_value_ports(value):
    errors = []
    if value.count(":") != 1:
        return value, [], errors

    head, tail = value.rsplit(":", 1)
    if not head or not tail:
        return value, [], errors
    if "/" in tail or not _looks_like_port_spec(tail):
        return value, [], errors

    ports, port_errors = normalize_port_ranges(tail)
    errors.extend(port_errors)
    if port_errors:
        return value, [], errors
    return head, ports, errors


def _normalize_hostname(value):
    value = value.strip().lower().rstrip(".")
    return value


def _validate_hostname(value, allow_wildcard):
    errors = []
    if not value:
        return ["Hostname value is required."]
    if ".." in value:
        errors.append("Hostname contains empty labels.")

    labels = value.split(".")
    for index, label in enumerate(labels):
        if not label:
            errors.append("Hostname contains empty labels.")
            continue
        if label == "*":
            if not allow_wildcard or index != 0:
                errors.append("Wildcard labels are only allowed as the first label.")
            continue
        if "*" in label:
            errors.append("Wildcard characters are only allowed as the first label.")
        if not _DOMAIN_LABEL_RE.match(label):
            errors.append(f"Hostname label has invalid characters: {label}.")

    return errors


def _validate_cidr(value):
    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError:
        return [f"CIDR value is invalid: {value}."]
    return []


def _validate_ip(value):
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return [f"IP address is invalid: {value}."]
    return []


def _validate_ip_range(value):
    if "-" not in value:
        return ["IP range must include '-' delimiter."]
    start_text, end_text = [item.strip() for item in value.split("-", 1)]
    errors = []
    errors.extend(_validate_ip(start_text))
    errors.extend(_validate_ip(end_text))
    return errors


def _extract_ports_input(asset):
    for key in ("ports", "port", "port_range", "port_ranges"):
        if key in asset:
            return asset.get(key)
    return None


def validate_scope_asset(asset, validate_ports=True):
    if not isinstance(asset, dict):
        return ["Asset must be a mapping."]

    errors = []
    asset_type = _clean_text(asset.get("type")).lower()
    value = _clean_text(asset.get("value"))
    ports = asset.get("ports") or []

    if asset_type in ("domain", "subdomain"):
        errors.extend(_validate_hostname(value, allow_wildcard=False))
        if "*" in value:
            errors.append("Wildcard characters are not allowed for domain assets.")
    elif asset_type == "wildcard":
        if value.count("*") > 1:
            errors.append("Nested wildcard patterns are not supported.")
        if not value.startswith("*."):
            errors.append("Wildcard values must start with '*.'.")
        errors.extend(_validate_hostname(value, allow_wildcard=True))
    elif asset_type == "cidr":
        errors.extend(_validate_cidr(value))
    elif asset_type == "ip":
        errors.extend(_validate_ip(value))
    elif asset_type == "ip-range":
        errors.extend(_validate_ip_range(value))

    if ports and validate_ports:
        port_ranges, port_errors = normalize_port_ranges(ports)
        errors.extend(port_errors)
        if port_ranges != ports:
            asset["ports"] = port_ranges

    return errors


def normalize_scope_asset(asset):
    errors = []
    if isinstance(asset, str):
        asset = {"type": "domain", "value": asset}

    if not isinstance(asset, dict):
        return None, ["Asset must be a mapping."]

    normalized = dict(asset)
    asset_type = _clean_text(asset.get("type")).lower()
    value = _clean_text(asset.get("value"))

    if not asset_type:
        errors.append("Asset type is required.")
    if not value:
        errors.append("Asset value is required.")

    if asset_type in ("domain", "subdomain", "wildcard"):
        if "://" in value:
            parsed = urlparse(value)
            if parsed.hostname:
                value = parsed.hostname
                if parsed.port and "ports" not in asset:
                    ports, port_errors = normalize_port_ranges(parsed.port)
                    if port_errors:
                        errors.extend(port_errors)
                    elif ports:
                        normalized["ports"] = ports

        value = _normalize_hostname(value)

        if asset_type != "wildcard" and "*" in value:
            asset_type = "wildcard"

    ports_input = _extract_ports_input(asset)
    if ports_input is not None:
        ports, port_errors = normalize_port_ranges(ports_input)
        errors.extend(port_errors)
        if ports:
            normalized["ports"] = ports
        if ports and _split_value_ports(value)[1]:
            errors.append("Ports specified in both value and ports field.")
    else:
        if asset_type in ("domain", "subdomain", "wildcard"):
            updated_value, ports, port_errors = _split_value_ports(value)
            errors.extend(port_errors)
            if ports:
                value = updated_value
                normalized["ports"] = ports

    normalized["type"] = asset_type or asset.get("type")
    normalized["value"] = value or asset.get("value")

    if "ports" in normalized and not normalized["ports"]:
        normalized.pop("ports", None)

    errors.extend(validate_scope_asset(normalized, validate_ports=False))
    return normalized, errors


def normalize_scope_assets(assets):
    if assets is None:
        return [], []

    if isinstance(assets, list):
        items = assets
    else:
        items = [assets]

    normalized = []
    errors = []
    for index, asset in enumerate(items):
        entry, entry_errors = normalize_scope_asset(asset)
        if entry is not None:
            normalized.append(entry)
        for error in entry_errors:
            errors.append(f"asset[{index}]: {error}")

    return normalized, errors


def asset_key(asset):
    if not isinstance(asset, dict):
        return ""

    asset_type = _clean_text(asset.get("type")).lower()
    value = _clean_text(asset.get("value")).lower()
    ports, _ = normalize_port_ranges(asset.get("ports"))
    if ports:
        port_key = ",".join(f"{entry['start']}-{entry['end']}" for entry in ports)
        return f"{asset_type}:{value}:{port_key}"
    return f"{asset_type}:{value}"
