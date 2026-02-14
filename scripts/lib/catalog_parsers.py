import re


CURRENCY_MAP = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "USD": "USD",
    "EUR": "EUR",
    "GBP": "GBP",
    "JPY": "JPY",
}


def _clean_text(text):
    if text is None:
        return ""
    return str(text).strip()


def _parse_number(value):
    value = value.replace(",", "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_reward_range(text):
    text = _clean_text(text)
    if not text:
        return {}
    lower = text.lower()
    if "no bounty" in lower or "no rewards" in lower:
        return {"summary": text}

    currency = None
    for token, code in CURRENCY_MAP.items():
        if token in text:
            currency = code
            break

    numbers = re.findall(r"[\d,]+(?:\.\d+)?", text)
    values = [_parse_number(item) for item in numbers]
    values = [item for item in values if item is not None]

    reward = {"summary": text}
    if currency:
        reward["currency"] = currency

    if values:
        if "up to" in lower or "max" in lower:
            reward["min"] = 0
            reward["max"] = values[0]
        elif len(values) == 1:
            reward["min"] = values[0]
            reward["max"] = values[0]
        else:
            reward["min"] = min(values)
            reward["max"] = max(values)

    return reward


def parse_response_time(text):
    text = _clean_text(text)
    if not text:
        return {}

    def _to_hours(value, unit):
        if unit.startswith("day"):
            return value * 24
        return value

    response = {}
    lower = text.lower()

    first_match = re.search(
        r"first response[^0-9]*([\d.]+)\s*(hour|hours|day|days)",
        lower,
    )
    if first_match:
        value = _parse_number(first_match.group(1))
        if value is not None:
            response["first_response_hours"] = _to_hours(value, first_match.group(2))

    resolution_match = re.search(
        r"(resolution|fix|remediation)[^0-9]*([\d.]+)\s*(hour|hours|day|days)",
        lower,
    )
    if resolution_match:
        value = _parse_number(resolution_match.group(2))
        if value is not None:
            response["resolution_time_hours"] = _to_hours(
                value, resolution_match.group(3)
            )

    if response:
        response["notes"] = text
    return response


def extract_restrictions(text):
    if text is None:
        return []
    if isinstance(text, list):
        items = text
    else:
        items = re.split(r"[\n\r]+", str(text))
    cleaned = []
    for item in items:
        item = _clean_text(item)
        if not item:
            continue
        cleaned.append(item.lstrip("- ").strip())
    return cleaned


def parse_safe_harbor(text):
    text = _clean_text(text)
    if not text:
        return {}
    lower = text.lower()
    if "no safe harbor" in lower:
        return {"present": False, "notes": text}
    if "safe harbor" in lower or "authorized" in lower:
        return {"present": True, "notes": text}
    return {"notes": text}


def classify_feasibility(restrictions, safe_harbor):
    restrictions = extract_restrictions(restrictions)
    lower = " ".join(item.lower() for item in restrictions)
    if "do not test" in lower or "no testing" in lower:
        return {"feasibility": "blocked", "notes": "Testing is disallowed."}
    if "no automated" in lower or "no scanning" in lower or "no fuzzing" in lower:
        return {"feasibility": "limited", "notes": "Automation constraints apply."}
    if safe_harbor and safe_harbor.get("present") is False:
        return {"feasibility": "limited", "notes": "Safe harbor absent."}
    return {"feasibility": "ok", "notes": "No blocking restrictions found."}
