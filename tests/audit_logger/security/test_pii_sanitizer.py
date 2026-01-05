"""
Tests for PII Sanitizer - Phase 4 Security Component

Tests cover:
- SSN detection and redaction
- Credit card detection and redaction
- API key detection and redaction
- Password detection and redaction
- Token detection and redaction
- Email address sanitization
- Phone number sanitization
- Nested JSON structure sanitization
- Multiple PII types in single text
- Custom redaction placeholders

TDD Cycle: RED → GREEN → REFACTOR
"""

import pytest
from src.audit_logger.security.pii_sanitizer import PIISanitizer


class TestPIISanitizer:
    """Test suite for PII sanitization functionality."""
    
    @pytest.fixture
    def sanitizer(self):
        """Create sanitizer instance for tests."""
        return PIISanitizer()
    
    # RED: SSN Detection
    def test_sanitize_ssn_standard_format(self, sanitizer):
        """Test detection of SSN in standard format (XXX-XX-XXXX)."""
        text = "User SSN is 123-45-6789 for verification"
        result = sanitizer.sanitize(text)
        assert "123-45-6789" not in result
        assert "[REDACTED_SSN]" in result
    
    def test_sanitize_ssn_no_dashes(self, sanitizer):
        """Test detection of SSN without dashes (XXXXXXXXX)."""
        text = "SSN: 123456789"
        result = sanitizer.sanitize(text)
        assert "123456789" not in result
        assert "[REDACTED_SSN]" in result
    
    # RED: Credit Card Detection
    def test_sanitize_credit_card_16_digits(self, sanitizer):
        """Test detection of 16-digit credit card numbers."""
        text = "Card number: 4532015112830366"
        result = sanitizer.sanitize(text)
        assert "4532015112830366" not in result
        assert "[REDACTED_CC]" in result
    
    def test_sanitize_credit_card_with_spaces(self, sanitizer):
        """Test detection of credit card with spaces."""
        text = "Card: 4532 0151 1283 0366"
        result = sanitizer.sanitize(text)
        assert "4532 0151 1283 0366" not in result
        assert "[REDACTED_CC]" in result
    
    # RED: API Key Detection
    def test_sanitize_api_key_openai_format(self, sanitizer):
        """Test detection of OpenAI-style API keys."""
        text = "API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz"
        result = sanitizer.sanitize(text)
        assert "sk-1234567890abcdefghijklmnopqrstuvwxyz" not in result
        assert "[REDACTED_API_KEY]" in result
    
    def test_sanitize_api_key_aws_format(self, sanitizer):
        """Test detection of AWS-style API keys."""
        text = "aws_access_key_id=AKIAIOSFODNN7EXAMPLE"
        result = sanitizer.sanitize(text)
        assert "AKIAIOSFODNN7EXAMPLE" not in result
        assert "[REDACTED_API_KEY]" in result
    
    # RED: Password Detection
    def test_sanitize_password_in_code(self, sanitizer):
        """Test detection of hardcoded passwords."""
        text = 'password = "MyS3cr3tP@ssw0rd"'
        result = sanitizer.sanitize(text)
        assert "MyS3cr3tP@ssw0rd" not in result
        assert "[REDACTED_PASSWORD]" in result
    
    def test_sanitize_password_in_config(self, sanitizer):
        """Test detection of passwords in config format."""
        text = "PASSWORD=admin123456"
        result = sanitizer.sanitize(text)
        assert "admin123456" not in result
        assert "[REDACTED_PASSWORD]" in result
    
    # RED: Token Detection
    def test_sanitize_jwt_token(self, sanitizer):
        """Test detection of JWT tokens."""
        text = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = sanitizer.sanitize(text)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
        assert "[REDACTED_TOKEN]" in result
    
    # RED: Email Sanitization
    def test_sanitize_email_address(self, sanitizer):
        """Test sanitization of email addresses (partial redaction)."""
        text = "Contact: john.doe@example.com"
        result = sanitizer.sanitize(text)
        assert "john.doe@example.com" not in result
        # Email should be partially visible: j***e@[DOMAIN]
        assert "@" not in result or "[DOMAIN]" in result
    
    # RED: Phone Number Sanitization
    def test_sanitize_phone_us_format(self, sanitizer):
        """Test sanitization of US phone numbers."""
        text = "Phone: (555) 123-4567"
        result = sanitizer.sanitize(text)
        assert "555" not in result or "[REDACTED_PHONE]" in result
    
    # RED: Nested JSON Sanitization
    def test_sanitize_nested_json(self, sanitizer):
        """Test sanitization of nested JSON structures."""
        import json
        data = {
            "user": {
                "name": "John Doe",
                "ssn": "123-45-6789",
                "credit_card": "4532015112830366",
                "api_key": "sk-abcdefghijklmnop"
            }
        }
        text = json.dumps(data)
        result = sanitizer.sanitize(text)
        assert "123-45-6789" not in result
        assert "4532015112830366" not in result
        assert "sk-abcdefghijklmnop" not in result
    
    # RED: Multiple PII Types
    def test_sanitize_multiple_pii_types(self, sanitizer):
        """Test sanitization when multiple PII types present."""
        text = """
        User: john@example.com
        SSN: 123-45-6789
        Card: 4532015112830366
        API: sk-1234567890abcdef
        """
        result = sanitizer.sanitize(text)
        assert "john@example.com" not in result
        assert "123-45-6789" not in result
        assert "4532015112830366" not in result
        assert "sk-1234567890abcdef" not in result
        # Should have different placeholders for each type
        assert "[REDACTED_SSN]" in result
        assert "[REDACTED_CC]" in result
        assert "[REDACTED_API_KEY]" in result
    
    # RED: Custom Placeholders
    def test_custom_placeholders(self, sanitizer):
        """Test custom placeholder generation."""
        text = "SSN: 123-45-6789"
        result = sanitizer.sanitize(text, placeholder_template="***REMOVED***")
        assert "123-45-6789" not in result
        assert "***REMOVED***" in result
    
    # RED: Validation Check
    def test_sanitization_completeness(self, sanitizer):
        """Test that sanitization is complete (no PII leaked)."""
        text = "SSN: 123-45-6789, Card: 4532015112830366"
        result = sanitizer.sanitize(text)
        # Run sanitizer again - should find nothing
        second_pass = sanitizer.sanitize(result)
        assert second_pass == result  # No changes on second pass
    
    # RED: Performance Test
    def test_sanitization_performance(self, sanitizer):
        """Test sanitization performance on large text."""
        import time
        large_text = "Some text with SSN 123-45-6789 repeated. " * 1000
        start = time.time()
        result = sanitizer.sanitize(large_text)
        duration = time.time() - start
        assert duration < 1.0  # Should complete in under 1 second
        assert "123-45-6789" not in result
    
    # RED: Edge Cases
    def test_sanitize_empty_string(self, sanitizer):
        """Test sanitization of empty string."""
        assert sanitizer.sanitize("") == ""
    
    def test_sanitize_none_value(self, sanitizer):
        """Test sanitization of None."""
        assert sanitizer.sanitize(None) == ""
    
    def test_sanitize_no_pii(self, sanitizer):
        """Test text with no PII (should remain unchanged)."""
        text = "This is a normal message with no sensitive data."
        result = sanitizer.sanitize(text)
        assert result == text
