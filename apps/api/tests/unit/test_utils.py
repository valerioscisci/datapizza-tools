"""Tests for utility functions (api/utils.py).

Covers safe_parse_json_list with valid JSON arrays, invalid JSON,
non-list JSON values, and edge cases.
"""

from __future__ import annotations

from api.utils import safe_parse_json_list


class TestSafeParseJsonList:
    """Tests for the safe_parse_json_list function."""

    def test_valid_json_array(self):
        """Should parse a valid JSON array of strings into a Python list."""
        result = safe_parse_json_list('["Python", "FastAPI", "React"]')
        assert result == ["Python", "FastAPI", "React"]

    def test_empty_json_array(self):
        """Should return an empty list for an empty JSON array."""
        result = safe_parse_json_list("[]")
        assert result == []

    def test_single_element_array(self):
        """Should parse a single-element JSON array correctly."""
        result = safe_parse_json_list('["Python"]')
        assert result == ["Python"]

    def test_invalid_json_returns_empty_list(self):
        """Should return an empty list for malformed JSON."""
        result = safe_parse_json_list("not valid json{{{")
        assert result == []

    def test_non_list_json_returns_empty_list(self):
        """Should return an empty list for valid JSON that is not a list (e.g., object)."""
        result = safe_parse_json_list('{"key": "value"}')
        assert result == []

    def test_json_string_returns_empty_list(self):
        """Should return an empty list for a JSON string (not array)."""
        result = safe_parse_json_list('"just a string"')
        assert result == []

    def test_json_number_returns_empty_list(self):
        """Should return an empty list for a JSON number."""
        result = safe_parse_json_list("42")
        assert result == []

    def test_none_returns_empty_list(self):
        """Should return an empty list for None input."""
        result = safe_parse_json_list(None)
        assert result == []

    def test_empty_string_returns_empty_list(self):
        """Should return an empty list for an empty string."""
        result = safe_parse_json_list("")
        assert result == []

    def test_list_with_non_string_elements_returns_empty_list(self):
        """Should return an empty list for a JSON array containing non-string elements."""
        result = safe_parse_json_list("[1, 2, 3]")
        assert result == []

    def test_mixed_types_returns_empty_list(self):
        """Should return an empty list for a JSON array with mixed types."""
        result = safe_parse_json_list('["Python", 42, true]')
        assert result == []
