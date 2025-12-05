import re


def _sanitize_label(label: str| None) -> str| None:
    """Sanitize a generic entity label by replacing non-alphanumeric characters with plus signs."""
    if label is None:
        return None

    if sanitization_level == SanitizationLevel.NONE:
        return label

    sanitized_label = re.sub(pattern=r"[^a-zA-Z0-9]", repl="+", string=label).removeprefix("+").removesuffix("+")
    return sanitized_label
