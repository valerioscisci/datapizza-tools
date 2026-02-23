from __future__ import annotations

import json


def safe_parse_json_list(json_str: str | None) -> list[str]:
    """Parse a JSON string containing a list of strings, returning [] on failure."""
    if not json_str:
        return []
    try:
        result = json.loads(json_str)
        if isinstance(result, list) and all(isinstance(x, str) for x in result):
            return result
        return []
    except (json.JSONDecodeError, TypeError):
        return []
