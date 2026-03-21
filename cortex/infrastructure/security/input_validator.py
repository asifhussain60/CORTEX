"""InputValidator compatibility implementation for security validation tests."""

import html
import json
import re
import unicodedata
from pathlib import PurePosixPath
from typing import Any, Dict
from urllib.parse import urlparse


class InputValidator:  # CORE-035-scoped - security boundary validation variant
    """Validates and sanitizes user-provided input."""

    _SQL_PATTERNS = [
        r"(?i)\bunion\b\s+\bselect\b",
        r"(?i)\bdrop\b\s+\btable\b",
        r"(?i)\bwaitfor\b\s+\bdelay\b",
        r"--",
        r";",
    ]
    _SCRIPT_TAG_RE = re.compile(r"(?is)<\s*script.*?>.*?<\s*/\s*script\s*>")
    _EVENT_HANDLER_RE = re.compile(r"(?i)on[a-z]+\s*=\s*([\"']).*?\1")

    def sanitize_sql(self, value: str) -> str:
        sanitized = value
        for pattern in self._SQL_PATTERNS:
            sanitized = re.sub(pattern, "", sanitized)
        return sanitized.strip()

    def prevent_xss(self, value: str) -> str:
        sanitized = self._SCRIPT_TAG_RE.sub("", value)
        sanitized = self._EVENT_HANDLER_RE.sub("", sanitized)
        if sanitized.lower().startswith("data:text/html"):
            sanitized = ""
        return sanitized

    def encode_output(self, value: str) -> str:
        return html.escape(value)

    def validate_type(self, value: Any, expected_type: type) -> bool:
        return isinstance(value, expected_type)

    def validate_email(self, value: str) -> bool:
        return bool(re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", value))

    def validate_url(self, value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def validate_string_length(self, value: str, max_length: int = 1000) -> str:
        if len(value) <= max_length:
            return value
        return value[:max_length]

    def validate(self, value: Any) -> bool:
        if isinstance(value, list):
            return len(value) <= 10000
        if isinstance(value, dict):
            return self.validate_request_size(value)
        return True

    def validate_request_size(self, request: Dict[str, Any], max_bytes: int = 10 * 1024 * 1024) -> bool:
        encoded = json.dumps(request, ensure_ascii=False).encode("utf-8")
        return len(encoded) <= max_bytes

    def validate_json_schema(self, data: Any, schema: Dict[str, Any]) -> bool:
        return self._validate_node(data, schema)

    def _validate_node(self, data: Any, schema: Dict[str, Any]) -> bool:
        expected_type = schema.get("type")
        if expected_type == "object" and not isinstance(data, dict):
            return False
        if expected_type == "string" and not isinstance(data, str):
            return False
        if expected_type == "integer" and not isinstance(data, int):
            return False

        required = schema.get("required", [])
        if isinstance(data, dict):
            for field in required:
                if field not in data:
                    return False

            properties = schema.get("properties", {})
            for key, subschema in properties.items():
                if key in data and not self._validate_node(data[key], subschema):
                    return False

        enum_values = schema.get("enum")
        if enum_values is not None and data not in enum_values:
            return False

        return True

    def sanitize_null_bytes(self, value: str) -> str:
        return value.replace("\x00", "")

    def normalize_unicode(self, value: str) -> str:
        return unicodedata.normalize("NFC", value)

    def prevent_path_traversal(self, path: str) -> str:
        safe_parts = [p for p in PurePosixPath(path).parts if p not in ("..", ".")]
        return "/".join(safe_parts)


__all__ = ["InputValidator"]
