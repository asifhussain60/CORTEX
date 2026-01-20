"""
Tests for Secret Redactor

AC-NFR-003-01: Secrets redacted from all logs

Test scenarios:
- API keys redacted
- Tokens redacted
- Passwords redacted
- Connection strings redacted
- Private keys redacted
- Dictionary redaction
- JSON redaction
- Redaction report generation
"""

import pytest
from cortex.infrastructure.secret_redactor import RedactionRule, SecretRedactor


class TestSecretRedactor:
    """Test suite for SecretRedactor."""
    
    @pytest.fixture
    def redactor(self):
        """Create redactor with default rules."""
        return SecretRedactor()
    
    def test_redact_aws_key(self, redactor):
        """Test AWS API key redaction."""
        text = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        redacted = redactor.redact_string(text)
        assert "AKIA" not in redacted
        assert "***REDACTED***" in redacted
    
    def test_redact_bearer_token(self, redactor):
        """Test Bearer token redaction."""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        redacted = redactor.redact_string(text)
        assert "Bearer" not in redacted or "***REDACTED***" in redacted
        assert "eyJh" not in redacted
    
    def test_redact_jwt_token(self, redactor):
        """Test JWT token redaction."""
        text = "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        redacted = redactor.redact_string(text)
        assert "eyJh" not in redacted
        assert "***REDACTED***" in redacted
    
    def test_redact_password(self, redactor):
        """Test password field redaction."""
        text = "password: super_secret_password_123"
        redacted = redactor.redact_string(text)
        assert "super_secret" not in redacted
        assert "***REDACTED***" in redacted
    
    def test_redact_github_token(self, redactor):
        """Test GitHub token redaction."""
        text = "GITHUB_TOKEN: gh_1234567890abcdefghijklmnopqrstuvwxyz"
        redacted = redactor.redact_string(text)
        assert "gh_1234567890" not in redacted
        assert "***REDACTED***" in redacted
    
    def test_redact_private_key(self, redactor):
        """Test private key redaction."""
        text = """
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEA2Z3qX2BTLS5000...
        -----END RSA PRIVATE KEY-----
        """
        redacted = redactor.redact_string(text)
        assert "BEGIN RSA PRIVATE KEY" not in redacted
        assert "***REDACTED***" in redacted
    
    def test_redact_credit_card(self, redactor):
        """Test credit card number redaction."""
        text = "Card: 4532-1234-5678-9010"
        redacted = redactor.redact_string(text)
        assert "4532" not in redacted
        assert "***REDACTED***" in redacted
    
    def test_redact_dict_password_key(self, redactor):
        """Test dictionary redaction with password key."""
        data = {
            "username": "user123",
            "password": "secret_password_123",
            "api_key": "sk_test_1234567890",
        }
        redacted = redactor.redact_dict(data)
        assert redacted["username"] == "user123"
        assert redacted["password"] == "***REDACTED***"
        assert redacted["api_key"] == "***REDACTED***"
    
    def test_redact_dict_nested(self, redactor):
        """Test nested dictionary redaction."""
        data = {
            "user": {
                "name": "Alice",
                "credentials": {
                    "password": "my_secure_pass_456",
                    "token": "gh_abcdefghijklmnopqrstuvwxyz1234567890"
                }
            }
        }
        redacted = redactor.redact_dict(data)
        assert redacted["user"]["name"] == "Alice"
        assert redacted["user"]["credentials"]["password"] == "***REDACTED***"
        assert redacted["user"]["credentials"]["token"] == "***REDACTED***"
    
    def test_redact_dict_list_values(self, redactor):
        """Test dictionary with list values."""
        data = {
            "items": ["item1", "password: test123", "item3"],
            "tokens": ["gh_1234567890abcdefghijklmnopqrstuvwxyz"],
        }
        redacted = redactor.redact_dict(data)
        assert redacted["items"][0] == "item1"
        assert "test123" not in redacted["items"][1]
        assert "gh_1234" not in redacted["tokens"][0]
    
    def test_redact_json_valid(self, redactor):
        """Test JSON string redaction."""
        json_str = '{"user":"alice","password":"secret123","token":"gh_abcdef"}'
        result = redactor.redact_json(json_str)
        assert result.is_ok()
        redacted_json = result.unwrap()
        assert "secret123" not in redacted_json or "***REDACTED***" in redacted_json
        assert "gh_abcdef" not in redacted_json or "***REDACTED***" in redacted_json
        assert "***REDACTED***" in redacted_json
    
    def test_redact_json_invalid(self, redactor):
        """Test JSON redaction with invalid JSON."""
        json_str = '{"invalid": json"}'
        result = redactor.redact_json(json_str)
        assert result.is_err()
    
    def test_get_redaction_report(self, redactor):
        """Test redaction report generation."""
        text = """
        API Key: AKIAIOSFODNN7EXAMPLE
        Password: super_secret_123
        Token: gh_1234567890abcdefghijklmnopqrstuvwxyz
        """
        report = redactor.get_redaction_report(text)
        assert report['secrets_found'] > 0
        assert len(report['rules_matched']) > 0
        assert report['total_matches'] > 0
    
    def test_custom_rule(self):
        """Test custom redaction rule."""
        custom_rules = [
            RedactionRule(
                id="custom_secret",
                pattern=r'CUSTOM_SECRET[0-9]+',
                description="Custom Secret Pattern",
            )
        ]
        redactor = SecretRedactor(custom_rules=custom_rules)
        text = "Found: CUSTOM_SECRET123456"
        redacted = redactor.redact_string(text)
        assert "CUSTOM_SECRET" not in redacted
        assert "***REDACTED***" in redacted
    
    def test_empty_string(self, redactor):
        """Test redaction of empty string."""
        result = redactor.redact_string("")
        assert result == ""
    
    def test_empty_dict(self, redactor):
        """Test redaction of empty dictionary."""
        result = redactor.redact_dict({})
        assert result == {}
    
    def test_no_secrets_in_text(self, redactor):
        """Test text with no secrets."""
        text = "This is a normal log message with no secrets."
        redacted = redactor.redact_string(text)
        assert redacted == text
    
    def test_disabled_rule(self):
        """Test that disabled rules are not applied."""
        rules = [
            RedactionRule(
                id="disabled_rule",
                pattern=r'SECRET',
                description="Disabled Rule",
                enabled=False,
            )
        ]
        redactor = SecretRedactor(custom_rules=rules)
        text = "This contains SECRET data"
        redacted = redactor.redact_string(text)
        assert "SECRET" in redacted
    
    def test_performance_large_text(self, redactor):
        """Test performance with large text."""
        # Create a large text with multiple secrets
        text = """
        API Key: AKIAIOSFODNN7EXAMPLE
        """ * 1000
        
        # Should not timeout
        redacted = redactor.redact_string(text)
        assert "AKIA" not in redacted
    
    def test_is_likely_secret(self, redactor):
        """Test secret detection."""
        assert redactor._is_likely_secret("AKIAIOSFODNN7EXAMPLE") is True
        assert redactor._is_likely_secret("normal_text_123") is False
        assert redactor._is_likely_secret("password: mysecret") is True
    
    def test_preserve_data_structure(self, redactor):
        """Test that redaction preserves data structure."""
        data = {
            "level": "INFO",
            "message": "User logged in with password: secret123",
            "timestamp": "2026-01-14T10:30:00Z",
            "user_id": 12345,
        }
        redacted = redactor.redact_dict(data)
        assert redacted["level"] == data["level"]
        assert redacted["timestamp"] == data["timestamp"]
        assert redacted["user_id"] == data["user_id"]
        assert "secret123" not in redacted["message"]
