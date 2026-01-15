from pathlib import Path


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def load_template(path):
    return Path(path).read_text(encoding="utf-8")


def render_template(template_text, context):
    return template_text.format_map(SafeDict(context))
