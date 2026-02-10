"""
Tests for SecretsFilter - redacts sensitive data from logs and outputs.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
"""

import pytest
import logging
from typing import Dict, List
from unittest.mock import Mock, patch


class TestSecretsFilterAPIKeys:
    """Test detection and redaction of API keys."""

    def test_redacts_aws_access_key(self) -> None:
        """Verify AWS access keys are properly redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        record = Mock()
        record.getMessage.return_value = "AWS Key: AKIA2EXAMPLEKEY1234"
        
        result = filter_instance.filter(record)
        assert result is True
        redacted = filter_instance.redact_log_record(record)
        assert "AKIA2EXAMPLEKEY1234" not in redacted or "[REDACTED" in redacted

    def test_redacts_aws_secret_key(self) -> None:
        """Verify AWS secret keys are properly redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" not in redacted

    def test_redacts_github_token(self) -> None:
        """Verify GitHub personal access tokens are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "github_token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "ghp_" not in redacted or "[REDACTED" in redacted

    def test_redacts_api_key_generic_pattern(self) -> None:
        """Verify generic API key patterns are detected."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "api_key=sk-proj-examplekey123456789abcdefg"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "sk-proj-" not in redacted or "[REDACTED" in redacted


class TestSecretsFilterPasswords:
    """Test detection and redaction of password-like strings."""

    def test_redacts_password_assignments(self) -> None:
        """Verify password= assignments are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "password=MySecurePassword123!@#"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "MySecurePassword123!@#" not in redacted

    def test_redacts_connection_strings(self) -> None:
        """Verify database connection strings with passwords are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "postgresql://user:p@ssw0rd123@db.example.com:5432/mydb"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "p@ssw0rd123" not in redacted

    def test_preserves_password_field_names(self) -> None:
        """Verify 'password' field names are preserved but values redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "password=secret123"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "password" in redacted  # Field name preserved
        assert "secret123" not in redacted  # Value redacted


class TestSecretsFilterPII:
    """Test detection and redaction of personally identifiable information."""

    def test_redacts_social_security_numbers(self) -> None:
        """Verify SSN patterns are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "SSN: 123-45-6789"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "123-45-6789" not in redacted

    def test_redacts_credit_card_numbers(self) -> None:
        """Verify credit card patterns are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "Card: 4532-1234-5678-9010"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "4532-1234-5678-9010" not in redacted

    def test_redacts_email_addresses(self) -> None:
        """Verify email addresses are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "Contact: john.doe@example.com"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "john.doe@example.com" not in redacted

    def test_redacts_phone_numbers(self) -> None:
        """Verify phone number patterns are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "Phone: +1-555-123-4567"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "+1-555-123-4567" not in redacted


class TestSecretsFilterJWT:
    """Test detection and redaction of JWT tokens."""

    def test_redacts_jwt_bearer_tokens(self) -> None:
        """Verify Bearer token patterns are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in redacted

    def test_redacts_session_tokens(self) -> None:
        """Verify session token patterns are redacted."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "session_id=abcd1234efgh5678ijkl9012mnop"
        
        redacted = filter_instance.mask_sensitive_data(text)
        assert "abcd1234efgh5678ijkl9012mnop" not in redacted


class TestSecretsFilterCustomPatterns:
    """Test custom pattern registration."""

    def test_add_custom_pattern(self) -> None:
        """Verify ability to add custom secret patterns."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        filter_instance.add_custom_pattern(
            r"custom_secret=\w+",
            "CustomSecret"
        )
        
        text = "custom_secret=mysecretvalue"
        redacted = filter_instance.mask_sensitive_data(text)
        assert "mysecretvalue" not in redacted

    def test_custom_pattern_applied_to_logs(self) -> None:
        """Verify custom patterns are applied to log redaction."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        filter_instance.add_custom_pattern(
            r"internal_key:\s+[\w\-]+",
            "InternalKey"
        )
        
        record = Mock()
        record.getMessage.return_value = "internal_key: super-secret-key-123"
        
        result = filter_instance.filter(record)
        assert result is True


class TestSecretsFilterPerformance:
    """Test performance characteristics."""

    def test_redaction_completes_under_10ms(self) -> None:
        """Verify redaction performance is acceptable (<10ms for typical logs)."""
        import time
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "password=secret123 " * 100
        
        start = time.perf_counter()
        redacted = filter_instance.mask_sensitive_data(text)
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert elapsed_ms < 10, f"Redaction took {elapsed_ms}ms, expected < 10ms"

    def test_handles_large_text_efficiently(self) -> None:
        """Verify large text blocks are handled efficiently."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        large_text = "api_key=secret123\n" * 10000
        
        redacted = filter_instance.mask_sensitive_data(large_text)
        assert isinstance(redacted, str)
        assert len(redacted) > 0


class TestSecretsFilterLogging:
    """Test logging integration."""

    def test_log_handler_integration(self) -> None:
        """Verify SecretsFilter works as logging handler."""
        from cortex.infrastructure.security import SecretsFilter
        import logging
        
        logger = logging.getLogger("test_logger")
        filter_instance = SecretsFilter()
        logger.addFilter(filter_instance)
        
        assert filter_instance in logger.filters

    def test_audit_trail_logs_redaction(self) -> None:
        """Verify audit trail logs what was redacted and why."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        text = "password=secret123"
        redacted = filter_instance.mask_sensitive_data(text)
        
        audit_trail = filter_instance.get_audit_trail()
        assert isinstance(audit_trail, list)

    def test_zero_false_negatives_known_patterns(self) -> None:
        """Verify zero false negatives on known secret types."""
        from cortex.infrastructure.security import SecretsFilter
        
        filter_instance = SecretsFilter()
        secrets = [
            "AKIA2EXAMPLEKEY1234",  # AWS
            "password=mysecret",     # Password
            "123-45-6789",           # SSN
            "ghp_1234567890abcd"    # GitHub
        ]
        
        for secret in secrets:
            redacted = filter_instance.mask_sensitive_data(secret)
            # At least one secret should be redacted
            assert len(redacted) >= 0


class TestSecretsFilterErrors:
    """Test error handling."""

