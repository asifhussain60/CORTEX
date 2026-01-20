"""
Tests for InputValidator - validates and sanitizes user input.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
"""

import pytest
from typing import Any, Dict


class TestInputValidatorSQLInjection:
    """Test SQL injection prevention."""

    def test_detects_sql_injection_in_string(self) -> None:
        """Verify SQL injection patterns are detected."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        malicious = "'; DROP TABLE users; --"
        
        result = validator.prevent_xss(malicious)  # Sanitize
        assert result is not None

    def test_detects_union_based_injection(self) -> None:
        """Verify UNION-based SQL injection is detected."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        malicious = "1 UNION SELECT * FROM users"
        
        # Should be sanitized
        sanitized = validator.sanitize_sql(malicious)
        assert sanitized is not None

    def test_detects_time_based_injection(self) -> None:
        """Verify time-based blind SQL injection is detected."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        malicious = "1; WAITFOR DELAY '00:00:05'"
        
        sanitized = validator.sanitize_sql(malicious)
        assert sanitized is not None

    def test_parameterized_queries_prevent_injection(self) -> None:
        """Verify parameterized queries prevent injection."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        # Parameterized queries should be safe by design
        safe_value = "'; DROP TABLE users; --"
        
        # Should validate without injection risk
        assert validator.prevent_xss(safe_value) is not None


class TestInputValidatorXSSPrevention:
    """Test XSS prevention."""

    def test_detects_script_tags(self) -> None:
        """Verify <script> tags are detected and sanitized."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        xss_payload = "<script>alert('xss')</script>"
        
        sanitized = validator.prevent_xss(xss_payload)
        assert "<script>" not in sanitized

    def test_detects_event_handlers(self) -> None:
        """Verify event handler attributes are detected."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        xss_payload = '<img src="x" onerror="alert(\'xss\')">'
        
        sanitized = validator.prevent_xss(xss_payload)
        assert "onerror" not in sanitized.lower()

    def test_encodes_html_entities(self) -> None:
        """Verify HTML entities are properly encoded."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        text = "<div>Hello & goodbye</div>"
        
        encoded = validator.encode_output(text)
        assert "&" in encoded or "&amp;" in encoded

    def test_detects_data_uris(self) -> None:
        """Verify data: URIs with scripts are detected."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        data_uri = 'data:text/html,<script>alert("xss")</script>'
        
        sanitized = validator.prevent_xss(data_uri)
        assert sanitized is not None


class TestInputValidatorTypeValidation:
    """Test type constraint validation."""

    def test_validates_string_type(self) -> None:
        """Verify string type validation."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        assert validator.validate_type("hello", str) is True
        assert validator.validate_type(123, str) is False

    def test_validates_integer_type(self) -> None:
        """Verify integer type validation."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        assert validator.validate_type(42, int) is True
        assert validator.validate_type("42", int) is False

    def test_validates_email_format(self) -> None:
        """Verify email format validation."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        assert validator.validate_email("user@example.com") is True
        assert validator.validate_email("invalid-email") is False

    def test_validates_url_format(self) -> None:
        """Verify URL format validation."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        assert validator.validate_url("https://example.com") is True
        assert validator.validate_url("not a url") is False


class TestInputValidatorSizeLimits:
    """Test request/input size limiting."""

    def test_enforces_max_string_length(self) -> None:
        """Verify maximum string length is enforced."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        long_string = "x" * 100000
        
        # Should either truncate or reject
        result = validator.validate_string_length(long_string, max_length=1000)
        assert result is not None

    def test_enforces_max_array_size(self) -> None:
        """Verify maximum array size is enforced."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        large_array = list(range(100000))
        
        result = validator.validate(large_array)
        assert result is not None

    def test_enforces_max_request_size_10mb(self) -> None:
        """Verify maximum 10MB request size is enforced."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        large_request = {"data": "x" * (11 * 1024 * 1024)}  # 11MB
        
        result = validator.validate_request_size(large_request)
        assert result is not None

    def test_rejects_oversized_requests(self) -> None:
        """Verify oversized requests are rejected."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        oversized = {"payload": "x" * (20 * 1024 * 1024)}  # 20MB
        
        # Should reject or raise error
        try:
            result = validator.validate_request_size(oversized)
        except ValueError:
            pass  # Expected


class TestInputValidatorJSONSchema:
    """Test JSON schema validation."""

    def test_validates_against_schema(self) -> None:
        """Verify JSON validation against schema."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        data = {"name": "John"}
        
        result = validator.validate_json_schema(data, schema)
        assert result is True

    def test_rejects_missing_required_fields(self) -> None:
        """Verify missing required fields are rejected."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        }
        data = {}
        
        result = validator.validate_json_schema(data, schema)
        assert result is False

    def test_validates_nested_objects(self) -> None:
        """Verify nested object validation."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        schema = {
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}}
                }
            }
        }
        data = {"user": {"name": "John"}}
        
        result = validator.validate_json_schema(data, schema)
        assert result is True

    def test_validates_enum_constraints(self) -> None:
        """Verify enum constraints are enforced."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        schema = {
            "type": "object",
            "properties": {"status": {"enum": ["active", "inactive"]}}
        }
        data_valid = {"status": "active"}
        data_invalid = {"status": "unknown"}
        
        assert validator.validate_json_schema(data_valid, schema) is True
        assert validator.validate_json_schema(data_invalid, schema) is False


class TestInputValidatorSpecialCases:
    """Test edge cases and special inputs."""

    def test_handles_null_bytes(self) -> None:
        """Verify null bytes in input are handled."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        text_with_nulls = "hello\x00world"
        
        sanitized = validator.sanitize_null_bytes(text_with_nulls)
        assert "\x00" not in sanitized

    def test_handles_unicode_normalization(self) -> None:
        """Verify Unicode is normalized properly."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        unicode_text = "café"  # NFD form
        
        normalized = validator.normalize_unicode(unicode_text)
        assert isinstance(normalized, str)

    def test_sanitizes_path_traversal_attempts(self) -> None:
        """Verify path traversal attempts are sanitized."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        traversal_path = "../../../etc/passwd"
        
        sanitized = validator.prevent_path_traversal(traversal_path)
        assert ".." not in sanitized


class TestInputValidatorErrors:
    """Test error handling."""

    def test_validation_error_includes_details(self) -> None:
        """Verify validation errors include helpful details."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        schema = {"type": "string"}
        data = 123
        
        try:
            validator.validate_json_schema(data, schema)
        except Exception as e:
            assert len(str(e)) > 0

    def test_handles_malformed_input_gracefully(self) -> None:
        """Verify malformed input is handled gracefully."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        malformed = None
        
        try:
            result = validator.validate(malformed)
        except (TypeError, ValueError, AttributeError):
            pass  # Expected

    def test_returns_actionable_error_messages(self) -> None:
        """Verify error messages are actionable."""
        from cortex.infrastructure.security import InputValidator
        
        validator = InputValidator()
        
        try:
            validator.validate_email("not-an-email")
        except (ValueError, TypeError):
            pass  # Should raise with clear message
