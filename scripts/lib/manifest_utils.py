REQUIRED_FIELDS = ("schema_version", "name", "version", "capabilities", "schemas")


def validate_manifest(manifest):
    errors = []
    if not isinstance(manifest, dict):
        return ["Manifest must be a mapping."]

    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    if "schema_version" in manifest and not isinstance(manifest["schema_version"], str):
        errors.append("Field 'schema_version' must be a string.")
    if "capabilities" in manifest and not isinstance(manifest["capabilities"], list):
        errors.append("Field 'capabilities' must be a list.")
    if "schemas" in manifest and not isinstance(manifest["schemas"], dict):
        errors.append("Field 'schemas' must be a mapping.")

    return errors
