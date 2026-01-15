SEVERITY_MODEL_NAME = "owasp-llm-top-10"
SEVERITY_MODEL_VERSION = "2023"
SEVERITY_MODEL_METHOD = "overall_severity_is_max_axis"
SEVERITY_MODEL_REFERENCE = "docs/SEVERITY_MODEL.md"
SEVERITY_MODEL_CATEGORY_DEFAULT = "unassigned"
SEVERITY_AXIS_DEFAULT = "unscored"
SEVERITY_AXES = ("data_exposure", "integrity", "autonomy", "cost_dos")


def _normalize_axis_value(value):
    if value is None:
        return SEVERITY_AXIS_DEFAULT
    if isinstance(value, str):
        cleaned = value.strip().lower()
        return cleaned or SEVERITY_AXIS_DEFAULT
    return str(value)


def _normalize_axes(axes):
    normalized = {axis: SEVERITY_AXIS_DEFAULT for axis in SEVERITY_AXES}
    if not isinstance(axes, dict):
        return normalized
    for axis in SEVERITY_AXES:
        normalized[axis] = _normalize_axis_value(axes.get(axis))
    return normalized


def build_severity_model(item=None):
    category = SEVERITY_MODEL_CATEGORY_DEFAULT
    axes = _normalize_axes(None)
    if isinstance(item, dict):
        existing = item.get("severity_model")
        if isinstance(existing, dict):
            model = dict(existing)
            model.setdefault("name", SEVERITY_MODEL_NAME)
            model.setdefault("version", SEVERITY_MODEL_VERSION)
            model.setdefault("category", SEVERITY_MODEL_CATEGORY_DEFAULT)
            model.setdefault("method", SEVERITY_MODEL_METHOD)
            model.setdefault("reference", SEVERITY_MODEL_REFERENCE)
            model["axes"] = _normalize_axes(model.get("axes"))
            return model
        category = (
            item.get("owasp_llm_category")
            or item.get("llm_top10_category")
            or SEVERITY_MODEL_CATEGORY_DEFAULT
        )
        axes = _normalize_axes(item.get("severity_axes") or item.get("impact_axes"))
    return {
        "name": SEVERITY_MODEL_NAME,
        "version": SEVERITY_MODEL_VERSION,
        "category": category,
        "axes": axes,
        "method": SEVERITY_MODEL_METHOD,
        "reference": SEVERITY_MODEL_REFERENCE,
    }


def ensure_severity_model(item):
    if not isinstance(item, dict):
        return item
    model = item.get("severity_model")
    if not isinstance(model, dict):
        item["severity_model"] = build_severity_model(item)
        return item
    model.setdefault("name", SEVERITY_MODEL_NAME)
    model.setdefault("version", SEVERITY_MODEL_VERSION)
    model.setdefault("category", SEVERITY_MODEL_CATEGORY_DEFAULT)
    model.setdefault("method", SEVERITY_MODEL_METHOD)
    model.setdefault("reference", SEVERITY_MODEL_REFERENCE)
    model["axes"] = _normalize_axes(model.get("axes"))
    return item


def format_severity_model(model):
    if not isinstance(model, dict):
        model = build_severity_model()
    name = model.get("name", SEVERITY_MODEL_NAME)
    version = model.get("version", SEVERITY_MODEL_VERSION)
    category = model.get("category", SEVERITY_MODEL_CATEGORY_DEFAULT)
    axes = _normalize_axes(model.get("axes"))
    axis_summary = ", ".join(
        f"{axis}={axes.get(axis, SEVERITY_AXIS_DEFAULT)}" for axis in SEVERITY_AXES
    )
    return f"{name} {version}; category {category}; axes {axis_summary}"


def severity_model_note():
    axes = ", ".join(SEVERITY_AXES)
    return (
        f"{SEVERITY_MODEL_NAME} {SEVERITY_MODEL_VERSION}. "
        f"Axes: {axes}. Overall severity uses the highest scored axis."
    )
