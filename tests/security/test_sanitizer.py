"""
Test suite for PII sanitizer.

Tests cover:
- Email sanitization
- Phone number sanitization
- SSN sanitization
- Credit card sanitization
- API key sanitization
- Password sanitization
- IP address sanitization
- Recursive sanitization (dicts, lists)
- Partial masking
- PII detection
"""

import pytest
from src.logging.security import (
    PIISanitizer,
    PartialMaskSanitizer,
    PIIType,
    create_sanitizer
)


class TestPIISanitizer:
    """Test full PII sanitization."""
    
    @pytest.fixture
    def sanitizer(self):
        """Create sanitizer instance."""
        return PIISanitizer()
    
    def test_sanitize_email(self, sanitizer):
        """Test email address sanitization."""
        text = "Contact me at john.doe@example.com for details"
        sanitized = sanitizer.sanitize(text)
        
        assert "john.doe@example.com" not in sanitized
        assert "***EMAIL***" in sanitized
    
    def test_sanitize_multiple_emails(self, sanitizer):
        """Test multiple email sanitization."""
        text = "Emails: alice@test.com, bob@test.org, charlie@test.net"
        sanitized = sanitizer.sanitize(text)
        
        assert "alice@test.com" not in sanitized
        assert "bob@test.org" not in sanitized
        assert "charlie@test.net" not in sanitized
        assert sanitized.count("***EMAIL***") == 3
    
    def test_sanitize_phone_number(self, sanitizer):
        """Test phone number sanitization."""
        text = "Call me at 555-123-4567 or (555) 987-6543"
        sanitized = sanitizer.sanitize(text)
        
        assert "555-123-4567" not in sanitized
        assert "(555) 987-6543" not in sanitized
        assert "***PHONE***" in sanitized
    
    def test_sanitize_ssn(self, sanitizer):
        """Test SSN sanitization."""
        text = "SSN: 123-45-6789"
        sanitized = sanitizer.sanitize(text)
        
        assert "123-45-6789" not in sanitized
        assert "***SSN***" in sanitized
    
    def test_sanitize_credit_card(self, sanitizer):
        """Test credit card sanitization."""
        text = "Card: 4532015112830366 (Visa)"
        sanitized = sanitizer.sanitize(text)
        
        assert "4532015112830366" not in sanitized
        assert "***CARD***" in sanitized
    
    def test_sanitize_api_key(self, sanitizer):
        """Test API key sanitization."""
        text = 'api_key="sk_test_1234567890abcdefghijklmnopqrst"'
        sanitized = sanitizer.sanitize(text)
        
        assert "sk_test_1234567890abcdefghijklmnopqrst" not in sanitized
        assert "***API_KEY***" in sanitized
    
    def test_sanitize_aws_key(self, sanitizer):
        """Test AWS access key sanitization."""
        text = "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE"
        sanitized = sanitizer.sanitize(text)
        
        assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
        assert "***AWS_KEY***" in sanitized
    
    def test_sanitize_jwt_token(self, sanitizer):
        """Test JWT token sanitization."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        text = f"Token: {token}"
        sanitized = sanitizer.sanitize(text)
        
        assert token not in sanitized
        assert "***JWT***" in sanitized
    
    def test_sanitize_github_token(self, sanitizer):
        """Test GitHub token sanitization."""
        text = "GITHUB_TOKEN=ghp_1234567890abcdefghijklmnopqrstuvwx"
        sanitized = sanitizer.sanitize(text)
        
        assert "ghp_1234567890abcdefghijklmnopqrstuvwx" not in sanitized
        assert "***GITHUB_TOKEN***" in sanitized
    
    def test_sanitize_password(self, sanitizer):
        """Test password sanitization."""
        text = 'password="MySecretPass123!"'
        sanitized = sanitizer.sanitize(text)
        
        assert "MySecretPass123!" not in sanitized
        assert "***PASSWORD***" in sanitized
    
    def test_sanitize_ip_address(self, sanitizer):
        """Test IP address sanitization."""
        text = "Server IP: 192.168.1.100"
        sanitized = sanitizer.sanitize(text)
        
        assert "192.168.1.100" not in sanitized
        assert "***IP***" in sanitized
    
    def test_sanitize_dict(self, sanitizer):
        """Test dictionary sanitization."""
        data = {
            "user": "john",
            "email": "john@example.com",
            "password": "secret123",
            "message": "Call me at 555-1234"
        }
        
        sanitized = sanitizer.sanitize(data)
        
        assert sanitized["user"] == "john"  # Not sensitive
        assert "***EMAIL***" in sanitized["email"]
        assert sanitized["password"] == "***REDACTED***"  # Sensitive key
        assert "***PHONE***" in sanitized["message"]
    
    def test_sanitize_nested_dict(self, sanitizer):
        """Test nested dictionary sanitization."""
        data = {
            "user": {
                "name": "Alice",
                "email": "alice@test.com",
                "settings": {  # Not a sensitive key
                    "theme": "dark",
                    "contact": "Call 555-1234"
                }
            }
        }
        
        sanitized = sanitizer.sanitize(data)
        
        assert sanitized["user"]["name"] == "Alice"
        assert "***EMAIL***" in sanitized["user"]["email"]
        assert sanitized["user"]["settings"]["theme"] == "dark"
        assert "***PHONE***" in sanitized["user"]["settings"]["contact"]
    
    def test_sanitize_list(self, sanitizer):
        """Test list sanitization."""
        data = [
            "Normal text",
            "Email: test@example.com",
            {"password": "secret"},
            ["Phone: 555-1234", "Another normal text"]
        ]
        
        sanitized = sanitizer.sanitize(data)
        
        assert sanitized[0] == "Normal text"
        assert "***EMAIL***" in sanitized[1]
        assert sanitized[2]["password"] == "***REDACTED***"
        assert "***PHONE***" in sanitized[3][0]
    
    def test_sanitize_mixed_content(self, sanitizer):
        """Test sanitization with mixed PII types."""
        text = """
        Contact: john@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        Card: 4532015112830366
        """
        
        sanitized = sanitizer.sanitize(text)
        
        assert "john@example.com" not in sanitized
        assert "555-123-4567" not in sanitized
        assert "123-45-6789" not in sanitized
        assert "4532015112830366" not in sanitized
        assert "***EMAIL***" in sanitized
        assert "***PHONE***" in sanitized
        assert "***SSN***" in sanitized
        assert "***CARD***" in sanitized
    
    def test_sanitization_stats(self, sanitizer):
        """Test sanitization statistics."""
        text = "Email: test@example.com, Phone: 555-1234"
        sanitizer.sanitize(text)
        
        stats = sanitizer.get_sanitization_stats()
        
        assert stats["total_sanitizations"] >= 2
        assert stats["patterns_configured"] > 0
        assert stats["mask_strategy"] == "full"
    
    def test_detect_pii(self, sanitizer):
        """Test PII detection without sanitization."""
        text = "Email: test@example.com, Phone: 555-1234"
        detections = sanitizer.detect_pii(text)
        
        assert len(detections) >= 2
        assert any(d["type"] == "email" for d in detections)
        assert any(d["type"] == "phone" for d in detections)
    
    def test_detect_pii_in_dict(self, sanitizer):
        """Test PII detection in dictionary."""
        data = {
            "email": "test@example.com",
            "password": "secret",
            "message": "Call 555-1234"
        }
        
        detections = sanitizer.detect_pii(data)
        
        # Should detect sensitive key and PII in values
        assert len(detections) >= 2
        assert any(d["type"] == "sensitive_key" for d in detections)


class TestPartialMaskSanitizer:
    """Test partial masking sanitization."""
    
    @pytest.fixture
    def sanitizer(self):
        """Create partial mask sanitizer."""
        return PartialMaskSanitizer()
    
    def test_partial_mask_email(self, sanitizer):
        """Test partial email masking."""
        text = "Contact: john.doe@example.com"
        sanitized = sanitizer.sanitize(text)
        
        # Should show first char and domain extension
        assert "j***@e***.com" in sanitized
        assert "john.doe@example.com" not in sanitized
    
    def test_partial_mask_phone(self, sanitizer):
        """Test partial phone masking."""
        text = "Phone: 555-123-4567"
        sanitized = sanitizer.sanitize(text)
        
        # Should show last 4 digits
        assert "***-***-4567" in sanitized or "4567" in sanitized
        assert "555-123" not in sanitized
    
    def test_partial_mask_credit_card(self, sanitizer):
        """Test partial credit card masking."""
        text = "Card: 4532015112830366"
        sanitized = sanitizer.sanitize(text)
        
        # Should show last 4 digits
        assert "0366" in sanitized
        assert "4532015112830366" not in sanitized


class TestCustomPatterns:
    """Test custom pattern sanitization."""
    
    def test_custom_pattern(self):
        """Test custom regex pattern."""
        custom_patterns = [
            (r'\b(CUSTOM-\d{6})\b', '***CUSTOM_ID***')
        ]
        
        sanitizer = PIISanitizer(custom_patterns=custom_patterns)
        text = "Reference: CUSTOM-123456"
        sanitized = sanitizer.sanitize(text)
        
        assert "CUSTOM-123456" not in sanitized
        assert "***CUSTOM_ID***" in sanitized
    
    def test_multiple_custom_patterns(self):
        """Test multiple custom patterns."""
        custom_patterns = [
            (r'\bINVOICE-\d+\b', '***INVOICE***'),
            (r'\bORDER-\d+\b', '***ORDER***')
        ]
        
        sanitizer = PIISanitizer(custom_patterns=custom_patterns)
        text = "INVOICE-12345 for ORDER-67890"
        sanitized = sanitizer.sanitize(text)
        
        assert "INVOICE-12345" not in sanitized
        assert "ORDER-67890" not in sanitized
        assert "***INVOICE***" in sanitized
        assert "***ORDER***" in sanitized


class TestSanitizerFactory:
    """Test sanitizer factory function."""
    
    def test_create_full_sanitizer(self):
        """Test creating full sanitizer."""
        sanitizer = create_sanitizer("full")
        
        assert isinstance(sanitizer, PIISanitizer)
        assert not isinstance(sanitizer, PartialMaskSanitizer)
    
    def test_create_partial_sanitizer(self):
        """Test creating partial sanitizer."""
        sanitizer = create_sanitizer("partial")
        
        assert isinstance(sanitizer, PartialMaskSanitizer)
    
    def test_default_sanitizer(self):
        """Test default sanitizer creation."""
        sanitizer = create_sanitizer()
        
        assert isinstance(sanitizer, PIISanitizer)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def sanitizer(self):
        """Create sanitizer instance."""
        return PIISanitizer()
    
    def test_sanitize_none(self, sanitizer):
        """Test sanitizing None."""
        result = sanitizer.sanitize(None)
        assert result is None
    
    def test_sanitize_empty_string(self, sanitizer):
        """Test sanitizing empty string."""
        result = sanitizer.sanitize("")
        assert result == ""
    
    def test_sanitize_empty_dict(self, sanitizer):
        """Test sanitizing empty dict."""
        result = sanitizer.sanitize({})
        assert result == {}
    
    def test_sanitize_empty_list(self, sanitizer):
        """Test sanitizing empty list."""
        result = sanitizer.sanitize([])
        assert result == []
    
    def test_sanitize_numbers(self, sanitizer):
        """Test sanitizing numbers (should pass through)."""
        assert sanitizer.sanitize(123) == 123
        assert sanitizer.sanitize(45.67) == 45.67
    
    def test_sanitize_boolean(self, sanitizer):
        """Test sanitizing booleans (should pass through)."""
        assert sanitizer.sanitize(True) is True
        assert sanitizer.sanitize(False) is False
    
    def test_no_pii_in_text(self, sanitizer):
        """Test text with no PII."""
        text = "This is just normal text without any sensitive information."
        sanitized = sanitizer.sanitize(text)
        
        assert sanitized == text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
