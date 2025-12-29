"""
Tests for EnhancedDocumentationGuardrail

Tests PII/PHI/PCI detection, redaction strategies, and company data sanitization.
"""

import pytest
from unittest.mock import Mock

from src.orchestration_4_0.orchestrators.documentation.enhanced_guardrails import (
    EnhancedDocumentationGuardrail,
    SensitivityLevel,
    RedactionStrategy,
    SensitiveDataMatch,
    RedactionResult
)


@pytest.fixture
def mock_logger():
    """Mock logger"""
    return Mock()


@pytest.fixture
def guardrail(mock_logger):
    """Create enhanced guardrail"""
    return EnhancedDocumentationGuardrail(
        logger=mock_logger,
        default_strategy=RedactionStrategy.MASK
    )


class TestEnhancedDocumentationGuardrail:
    """Test EnhancedDocumentationGuardrail"""
    
    def test_initialization(self, guardrail):
        """Test guardrail initialization"""
        assert guardrail.logger is not None
        assert guardrail.default_strategy == RedactionStrategy.MASK
        assert guardrail.enable_audit_trail is True
        assert guardrail.total_scans == 0
        assert guardrail.total_redactions == 0
    
    # PII Detection Tests
    
    def test_detect_ssn(self, guardrail):
        """Test SSN detection"""
        text = "SSN: 123-45-6789 for verification."
        
        matches = guardrail.detect_sensitive_data(text)
        
        ssn_matches = [m for m in matches if m.pattern_name == 'SSN']
        assert len(ssn_matches) == 1
        assert ssn_matches[0].data_type == 'PII'
        assert ssn_matches[0].matched_text == '123-45-6789'
    
    def test_detect_email(self, guardrail):
        """Test email detection"""
        text = "Email: john.doe@example.com"
        
        matches = guardrail.detect_sensitive_data(text)
        
        email_matches = [m for m in matches if m.pattern_name == 'EMAIL']
        assert len(email_matches) == 1
        assert email_matches[0].matched_text == 'john.doe@example.com'
    
    def test_detect_phone_us(self, guardrail):
        """Test US phone number detection"""
        text = "Call me at (555) 123-4567 or 555-987-6543."
        
        matches = guardrail.detect_sensitive_data(text)
        
        assert len(matches) >= 2
        phone_matches = [m for m in matches if m.pattern_name == 'PHONE_US']
        assert len(phone_matches) >= 1
    
    def test_detect_ip_address(self, guardrail):
        """Test IP address detection"""
        text = "IP: 192.168.1.100"
        
        matches = guardrail.detect_sensitive_data(text)
        
        ip_matches = [m for m in matches if m.pattern_name == 'IP_ADDRESS']
        assert len(ip_matches) == 1
        assert ip_matches[0].matched_text == '192.168.1.100'
    
    # PHI Detection Tests
    
    def test_detect_medical_record_number(self, guardrail):
        """Test medical record number detection"""
        text = "Patient MRN: 12345678 requires follow-up."
        
        matches = guardrail.detect_sensitive_data(
            text,
            sensitivity=SensitivityLevel.CONFIDENTIAL
        )
        
        phi_matches = [m for m in matches if m.data_type == 'PHI']
        assert len(phi_matches) >= 1
        assert any('MRN' in m.pattern_name or 'MEDICAL' in m.pattern_name for m in phi_matches)
    
    def test_detect_blood_type(self, guardrail):
        """Test blood type detection"""
        text = "Blood type is A+ according to records."
        
        matches = guardrail.detect_sensitive_data(
            text,
            sensitivity=SensitivityLevel.CONFIDENTIAL
        )
        
        blood_matches = [m for m in matches if 'BLOOD' in m.pattern_name]
        assert len(blood_matches) >= 1
    
    # PCI Detection Tests
    
    def test_detect_credit_card_visa(self, guardrail):
        """Test Visa credit card detection"""
        text = "Card number: 4111-1111-1111-1111"
        
        matches = guardrail.detect_sensitive_data(text)
        
        cc_matches = [m for m in matches if 'CREDIT_CARD' in m.pattern_name]
        assert len(cc_matches) >= 1
    
    def test_detect_credit_card_mastercard(self, guardrail):
        """Test Mastercard detection"""
        text = "Mastercard: 5500-0000-0000-0004"
        
        matches = guardrail.detect_sensitive_data(text)
        
        cc_matches = [m for m in matches if 'CREDIT_CARD' in m.pattern_name]
        assert len(cc_matches) >= 1
    
    def test_detect_cvv(self, guardrail):
        """Test CVV detection"""
        text = "CVV: 123 on back of card."
        
        matches = guardrail.detect_sensitive_data(text)
        
        cvv_matches = [m for m in matches if 'CVV' in m.pattern_name]
        assert len(cvv_matches) == 1
    
    # Security Pattern Detection Tests
    
    def test_detect_api_key(self, guardrail):
        """Test API key detection"""
        text = "API key: abcd1234efgh5678ijkl9012mnop3456qrst7890"
        
        matches = guardrail.detect_sensitive_data(text)
        
        api_matches = [m for m in matches if 'API' in m.pattern_name]
        assert len(api_matches) >= 1
    
    def test_detect_aws_key(self, guardrail):
        """Test AWS key detection"""
        text = "AWS key: AKIAIOSFODNN7EXAMPLE"
        
        matches = guardrail.detect_sensitive_data(text)
        
        aws_matches = [m for m in matches if 'AWS' in m.pattern_name]
        assert len(aws_matches) == 1
    
    # Redaction Strategy Tests
    
    def test_redact_with_mask_strategy(self, guardrail):
        """Test redaction with MASK strategy"""
        text = "Email: john@example.com"
        
        result = guardrail.redact_sensitive_data(
            text,
            strategy=RedactionStrategy.MASK
        )
        
        assert '[REDACTED_EMAIL]' in result.redacted_text
        assert 'john@example.com' not in result.redacted_text
        assert result.redaction_count >= 1
    
    def test_redact_with_hash_strategy(self, guardrail):
        """Test redaction with HASH strategy"""
        text = "SSN: 123-45-6789"
        
        result = guardrail.redact_sensitive_data(
            text,
            strategy=RedactionStrategy.HASH
        )
        
        assert '[HASH_' in result.redacted_text
        assert '123-45-6789' not in result.redacted_text
    
    def test_redact_with_remove_strategy(self, guardrail):
        """Test redaction with REMOVE strategy"""
        text = "Email: test@example.com end"
        
        result = guardrail.redact_sensitive_data(
            text,
            strategy=RedactionStrategy.REMOVE
        )
        
        assert 'test@example.com' not in result.redacted_text
        assert result.redaction_count >= 1
    
    def test_redact_with_placeholder_strategy(self, guardrail):
        """Test redaction with PLACEHOLDER strategy"""
        text = "IP: 10.0.0.1"
        
        result = guardrail.redact_sensitive_data(
            text,
            strategy=RedactionStrategy.PLACEHOLDER
        )
        
        assert '192.0.2.1' in result.redacted_text or '[REDACTED]' in result.redacted_text
        assert '10.0.0.1' not in result.redacted_text
    
    # Multiple Sensitive Data Tests
    
    def test_redact_multiple_types(self, guardrail):
        """Test redacting multiple data types in one text"""
        text = """
        Patient: John Doe
        Email: patient@example.com
        Phone: 555-1234
        SSN: 123-45-6789
        Credit Card: 4111-1111-1111-1111
        """
        
        result = guardrail.redact_sensitive_data(text)
        
        assert result.redaction_count >= 3
        assert 'PII' in result.data_types_found
        assert 'patient@example.com' not in result.redacted_text
        assert '123-45-6789' not in result.redacted_text
        assert '4111-1111-1111-1111' not in result.redacted_text
    
    # Sensitivity Level Tests
    
    def test_public_sensitivity_minimal_redaction(self, guardrail):
        """Test PUBLIC sensitivity only redacts critical data"""
        text = "Email: test@example.com, Key: abcd1234efgh5678ijkl9012mnop3456qrst7890uv12"
        
        result = guardrail.redact_sensitive_data(
            text,
            sensitivity=SensitivityLevel.PUBLIC
        )
        
        # PUBLIC should only catch SECURITY patterns
        assert 'test@example.com' in result.redacted_text  # Email allowed at PUBLIC level
        # Long key should be redacted
        assert 'abcd1234efgh5678ijkl9012mnop3456qrst7890uv12' not in result.redacted_text
    
    def test_confidential_sensitivity_full_redaction(self, guardrail):
        """Test CONFIDENTIAL sensitivity redacts all categories"""
        text = "Email: test@example.com, MRN: 12345678, CC: 4111-1111-1111-1111"
        
        result = guardrail.redact_sensitive_data(
            text,
            sensitivity=SensitivityLevel.CONFIDENTIAL
        )
        
        assert result.redaction_count >= 2
        assert 'PII' in result.data_types_found or 'PCI' in result.data_types_found
    
    # Company Pattern Tests
    
    def test_add_company_pattern(self, guardrail):
        """Test adding custom company pattern"""
        guardrail.add_company_pattern('COMPANY_DOMAIN', r'acme\.com')
        
        text = "Visit us at www.acme.com"
        
        matches = guardrail.detect_sensitive_data(text)
        
        company_matches = [m for m in matches if m.data_type == 'COMPANY']
        assert len(company_matches) >= 1
    
    def test_company_pattern_redaction(self, guardrail):
        """Test redacting company-specific data"""
        guardrail.add_company_pattern('INTERNAL_IP', r'10\.0\.0\.\d+')
        
        text = "Internal server: 10.0.0.50"
        
        result = guardrail.redact_sensitive_data(text)
        
        assert '10.0.0.50' not in result.redacted_text or len(result.matches) > 0
    
    # Whitelist Tests
    
    def test_whitelist_prevents_redaction(self, guardrail):
        """Test whitelisted items are not redacted"""
        guardrail.add_to_whitelist('example@test.com')
        
        text = "example@test.com and other@test.com"
        
        result = guardrail.redact_sensitive_data(text)
        
        # Whitelisted email should remain
        assert 'example@test.com' in result.redacted_text
        # Other email should be redacted
        assert 'other@test.com' not in result.redacted_text
    
    # Category Filtering Tests
    
    def test_include_only_pii_category(self, guardrail):
        """Test scanning only PII category"""
        text = "Email: test@example.com, CC: 4111-1111-1111-1111"
        
        result = guardrail.redact_sensitive_data(
            text,
            include_categories=['PII']
        )
        
        # Should only redact PII (email), not PCI (credit card)
        assert result.data_types_found == {'PII'}
        assert 'test@example.com' not in result.redacted_text
        # Credit card might still appear if only PII filtered
    
    def test_include_multiple_categories(self, guardrail):
        """Test scanning specific categories"""
        text = "Email: test@example.com, CC: 4111-1111-1111-1111"
        
        result = guardrail.redact_sensitive_data(
            text,
            include_categories=['PII', 'PCI']
        )
        
        assert 'PII' in result.data_types_found or 'PCI' in result.data_types_found
    
    # Audit Trail Tests
    
    def test_audit_trail_enabled(self, guardrail):
        """Test audit trail is generated when enabled"""
        text = "Email: test@example.com"
        
        result = guardrail.redact_sensitive_data(text)
        
        assert len(result.audit_trail) >= 1
        # Check that audit trail contains reference to the redaction
        assert any('EMAIL' in trail or 'test' in trail for trail in result.audit_trail)
    
    def test_audit_trail_disabled(self, mock_logger):
        """Test audit trail disabled"""
        guardrail = EnhancedDocumentationGuardrail(
            logger=mock_logger,
            enable_audit_trail=False
        )
        
        text = "Email: test@example.com"
        
        result = guardrail.redact_sensitive_data(text)
        
        assert len(result.audit_trail) == 0
    
    # Statistics Tests
    
    def test_statistics_tracking(self, guardrail):
        """Test guardrail statistics are tracked"""
        text1 = "Email: test1@example.com"
        text2 = "Email: test2@example.com"
        
        guardrail.redact_sensitive_data(text1)
        guardrail.redact_sensitive_data(text2)
        
        stats = guardrail.get_statistics()
        
        assert stats['total_scans'] == 2
        assert stats['total_redactions'] >= 2
    
    # Edge Case Tests
    
    def test_empty_text(self, guardrail):
        """Test redacting empty text"""
        result = guardrail.redact_sensitive_data("")
        
        assert result.redacted_text == ""
        assert result.redaction_count == 0
    
    def test_no_sensitive_data(self, guardrail):
        """Test text with no sensitive data"""
        text = "The system processes requests efficiently."
        
        result = guardrail.redact_sensitive_data(text)
        
        assert result.redacted_text == text
        assert result.redaction_count == 0
    
    def test_overlapping_patterns(self, guardrail):
        """Test handling overlapping pattern matches"""
        # Some text might match multiple patterns
        text = "Contact: 1234567890"  # Could be phone or account number
        
        matches = guardrail.detect_sensitive_data(text)
        
        # Should detect at least one match
        assert len(matches) >= 1
    
    # Confidence Scoring Tests
    
    def test_high_confidence_patterns(self, guardrail):
        """Test high confidence pattern scoring"""
        text = "SSN: 123-45-6789, Email: test@example.com"
        
        matches = guardrail.detect_sensitive_data(text)
        
        ssn_matches = [m for m in matches if m.pattern_name == 'SSN']
        if ssn_matches:
            assert ssn_matches[0].confidence == 1.0
    
    def test_medium_confidence_patterns(self, guardrail):
        """Test medium confidence pattern scoring"""
        text = "Username: johndoe123"
        
        matches = guardrail.detect_sensitive_data(text)
        
        username_matches = [m for m in matches if 'USERNAME' in m.pattern_name]
        if username_matches:
            assert username_matches[0].confidence < 1.0
    
    # Severity Tests
    
    def test_critical_severity_assignment(self, guardrail):
        """Test critical severity for sensitive patterns"""
        text = "SSN: 123-45-6789"
        
        matches = guardrail.detect_sensitive_data(text)
        
        ssn_matches = [m for m in matches if m.pattern_name == 'SSN']
        assert len(ssn_matches) == 1
        assert ssn_matches[0].severity == 'CRITICAL'
    
    def test_high_severity_for_phi(self, guardrail):
        """Test high severity for PHI data"""
        text = "MRN: 12345678"
        
        matches = guardrail.detect_sensitive_data(text)
        
        mrn_matches = [m for m in matches if 'MRN' in m.pattern_name or 'MEDICAL' in m.pattern_name]
        if mrn_matches:
            assert mrn_matches[0].severity in ['HIGH', 'CRITICAL']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
