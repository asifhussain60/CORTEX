"""Phase S3: Security Tab (🔒) - TDD Test Suite
Tests for security assessments, compliance, and encryption
"""

import pytest
from pydantic import ValidationError
from cortex.orchestrators.onboarding.dashboard_schema_models import SecurityTab


@pytest.fixture
def valid_security():
    """Valid security metrics with all fields"""
    return {
        "security_score": 8.5,
        "security_posture": "Strong",
        "frameworks": [
            {
                "name": "OWASP",
                "status": "compliant",
                "score": 85.0,
                "issues": 2
            }
        ],
        "authentication": {
            "implemented": "OAuth2 + MFA",
            "standards": ["OAuth2", "OpenID"],
            "multi_factor": True
        },
        "encryption": {
            "at_rest": True,
            "in_transit": True,
            "key_management": "Azure Key Vault"
        },
        "data_protection": {
            "pii_detection": 5,
            "masking": True,
            "retention_policy": "90 days"
        }
    }


class TestSecurityScore:
    """Test security score validation"""
    
    def test_valid_security_score(self, valid_security):
        """Test valid security score (8.5)"""
        sec = SecurityTab(**valid_security)
        assert sec.security_score == 8.5
        assert 0 <= sec.security_score <= 10
    
    def test_perfect_security_score(self, valid_security):
        """Test perfect security (10.0)"""
        data = valid_security.copy()
        data["security_score"] = 10.0
        sec = SecurityTab(**data)
        assert sec.security_score == 10.0
    
    def test_minimum_security_score(self, valid_security):
        """Test minimum security score (0.0)"""
        data = valid_security.copy()
        data["security_score"] = 0.0
        sec = SecurityTab(**data)
        assert sec.security_score == 0.0
    
    def test_security_score_exceeds_maximum(self, valid_security):
        """Test security exceeding maximum (invalid)"""
        data = valid_security.copy()
        data["security_score"] = 10.5
        with pytest.raises(ValidationError):
            SecurityTab(**data)


class TestSecurityPosture:
    """Test security posture validation"""
    
    def test_strong_posture(self, valid_security):
        """Test strong security posture"""
        sec = SecurityTab(**valid_security)
        assert sec.security_posture == "Strong"


class TestAuthentication:
    """Test authentication configuration"""
    
    def test_auth_with_mfa(self, valid_security):
        """Test authentication with MFA enabled"""
        sec = SecurityTab(**valid_security)
        assert sec.authentication is not None
        assert sec.authentication.multi_factor == True
        assert "OAuth2" in sec.authentication.standards
    
    def test_auth_without_mfa(self, valid_security):
        """Test authentication without MFA"""
        data = valid_security.copy()
        data["authentication"] = {
            "implemented": "Basic",
            "standards": ["HTTP-Basic"],
            "multi_factor": False
        }
        sec = SecurityTab(**data)
        assert sec.authentication.multi_factor == False


class TestEncryption:
    """Test encryption status"""
    
    def test_encryption_at_rest_and_transit(self, valid_security):
        """Test encryption at rest and in transit enabled"""
        sec = SecurityTab(**valid_security)
        assert sec.encryption is not None
        assert sec.encryption.at_rest == True
        assert sec.encryption.in_transit == True
    
    def test_partial_encryption(self, valid_security):
        """Test partial encryption (at rest only)"""
        data = valid_security.copy()
        data["encryption"] = {
            "at_rest": True,
            "in_transit": False
        }
        sec = SecurityTab(**data)
        assert sec.encryption.at_rest == True
        assert sec.encryption.in_transit == False


class TestDataProtection:
    """Test data protection measures"""
    
    def test_pii_detection_and_masking(self, valid_security):
        """Test PII detection with masking enabled"""
        sec = SecurityTab(**valid_security)
        assert sec.data_protection is not None
        assert sec.data_protection.pii_detection >= 0
        assert sec.data_protection.masking == True
    
    def test_retention_policy(self, valid_security):
        """Test retention policy"""
        sec = SecurityTab(**valid_security)
        assert sec.data_protection.retention_policy is not None


class TestComplianceFrameworks:
    """Test compliance framework tracking"""
    
    def test_single_framework(self, valid_security):
        """Test single compliance framework"""
        sec = SecurityTab(**valid_security)
        assert len(sec.frameworks) == 1
        assert sec.frameworks[0].name == "OWASP"
    
    def test_framework_score_range(self, valid_security):
        """Test framework compliance score in valid range (0-100)"""
        sec = SecurityTab(**valid_security)
        for framework in sec.frameworks:
            assert 0 <= framework.score <= 100
    
    def test_framework_issues_count(self, valid_security):
        """Test framework issues count is non-negative"""
        sec = SecurityTab(**valid_security)
        for framework in sec.frameworks:
            assert framework.issues >= 0
    
    def test_multiple_frameworks(self, valid_security):
        """Test multiple compliance frameworks"""
        data = valid_security.copy()
        data["frameworks"] = [
            {
                "name": "OWASP",
                "status": "compliant",
                "score": 85.0,
                "issues": 2
            },
            {
                "name": "SOC2",
                "status": "compliant",
                "score": 90.0,
                "issues": 0
            },
            {
                "name": "HIPAA",
                "status": "partial",
                "score": 75.0,
                "issues": 5
            }
        ]
        sec = SecurityTab(**data)
        assert len(sec.frameworks) == 3
