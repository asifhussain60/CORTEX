"""
RED Phase Tests for Privacy Anonymizer

Tests centralized anonymization with SHA-256, PII detection, and SKULL compliance.
These tests MUST fail initially (ModuleNotFoundError for Anonymizer).
"""

import pytest
from datetime import date, datetime
from pathlib import Path
import hashlib
import re

# Will fail initially - module doesn't exist yet
from src.tier3.privacy.anonymizer import (
    Anonymizer,
    AnonymizationResult,
    PIIDetectionResult,
    PIIType
)


class TestAnonymizer:
    """Test suite for privacy anonymization"""
    
    def test_anonymizer_initialization(self):
        """Test anonymizer can be instantiated with optional salt"""
        # Default initialization (no salt)
        anon1 = Anonymizer()
        assert anon1 is not None
        assert anon1.salt == ""
        
        # With custom salt
        anon2 = Anonymizer(salt="custom_salt")
        assert anon2.salt == "custom_salt"
    
    def test_anonymize_string_basic(self):
        """Test basic string anonymization with SHA-256"""
        anon = Anonymizer()
        
        # Same input should produce same hash
        result1 = anon.anonymize("john.doe@example.com")
        result2 = anon.anonymize("john.doe@example.com")
        
        assert result1 == result2
        assert len(result1) == 64  # SHA-256 produces 64 hex chars
        assert result1 != "john.doe@example.com"  # Should be hashed
        
        # Different input should produce different hash
        result3 = anon.anonymize("jane.smith@example.com")
        assert result3 != result1
    
    def test_anonymize_with_salt(self):
        """Test that salt affects hash output"""
        anon1 = Anonymizer(salt="salt1")
        anon2 = Anonymizer(salt="salt2")
        
        input_str = "john.doe@example.com"
        hash1 = anon1.anonymize(input_str)
        hash2 = anon2.anonymize(input_str)
        
        assert hash1 != hash2  # Different salts = different hashes
        assert len(hash1) == 64
        assert len(hash2) == 64
    
    def test_anonymize_empty_string(self):
        """Test anonymization handles empty string"""
        anon = Anonymizer()
        result = anon.anonymize("")
        
        # Empty string should still produce valid hash
        assert len(result) == 64
        assert result == hashlib.sha256("".encode('utf-8')).hexdigest()
    
    def test_detect_email_pii(self):
        """Test email detection"""
        anon = Anonymizer()
        
        # Valid emails
        assert anon.detect_pii("john.doe@example.com").has_pii is True
        assert PIIType.EMAIL in anon.detect_pii("john.doe@example.com").pii_types
        
        # Multiple emails
        text = "Contact john@example.com or jane@test.org"
        result = anon.detect_pii(text)
        assert result.has_pii is True
        assert PIIType.EMAIL in result.pii_types
        assert len(result.matches) == 2
    
    def test_detect_username_pii(self):
        """Test username detection (github_username, email prefix)"""
        anon = Anonymizer()
        
        # GitHub usernames (alphanumeric with hyphens)
        result = anon.detect_pii("github_user123")
        assert result.has_pii is True
        assert PIIType.USERNAME in result.pii_types
        
        # Email prefix extraction
        result = anon.detect_pii("john.doe@example.com")
        assert PIIType.USERNAME in result.pii_types  # Email prefix counts as username
    
    def test_detect_no_pii(self):
        """Test detection when no PII present"""
        anon = Anonymizer()
        
        # Generic text with no identifiers
        result = anon.detect_pii("This is a test message with no personal information")
        assert result.has_pii is False
        assert len(result.pii_types) == 0
        assert len(result.matches) == 0
    
    def test_strip_pii_from_text(self):
        """Test PII stripping replaces identifiers with hashes"""
        anon = Anonymizer()
        
        # Email replacement
        text = "Contact john.doe@example.com for details"
        result = anon.strip_pii(text)
        
        assert "john.doe@example.com" not in result.sanitized_text
        assert result.sanitized_text.startswith("Contact ")
        assert len(result.sanitized_text) > len("Contact ")  # Hash added
        assert result.pii_found.has_pii is True
    
    def test_strip_pii_preserves_structure(self):
        """Test PII stripping maintains text structure"""
        anon = Anonymizer()
        
        text = "User john@example.com requested feature X on 2025-12-05"
        result = anon.strip_pii(text)
        
        # Structure preserved
        assert "User" in result.sanitized_text
        assert "requested feature X on 2025-12-05" in result.sanitized_text
        
        # Email replaced with hash
        assert "john@example.com" not in result.sanitized_text
    
    def test_anonymize_dict_basic(self):
        """Test dictionary anonymization with field specification"""
        anon = Anonymizer()
        
        data = {
            "engineer_id": "john.doe@example.com",
            "team": "Platform",
            "date": "2025-12-05"
        }
        
        result = anon.anonymize_dict(data, fields=["engineer_id"])
        
        assert result.original_keys == ["engineer_id"]
        assert "engineer_id" in result.anonymized_data
        assert result.anonymized_data["engineer_id"] != "john.doe@example.com"
        assert result.anonymized_data["team"] == "Platform"  # Unchanged
        assert result.anonymized_data["date"] == "2025-12-05"  # Unchanged
    
    def test_anonymize_dict_multiple_fields(self):
        """Test anonymizing multiple dictionary fields"""
        anon = Anonymizer()
        
        data = {
            "user_email": "john@example.com",
            "manager_email": "jane@example.com",
            "project": "CORTEX"
        }
        
        result = anon.anonymize_dict(data, fields=["user_email", "manager_email"])
        
        assert len(result.original_keys) == 2
        assert result.anonymized_data["user_email"] != "john@example.com"
        assert result.anonymized_data["manager_email"] != "jane@example.com"
        assert result.anonymized_data["project"] == "CORTEX"  # Unchanged
        
        # Different emails should hash differently
        assert result.anonymized_data["user_email"] != result.anonymized_data["manager_email"]
    
    def test_anonymize_dict_nested(self):
        """Test anonymization handles nested dictionaries"""
        anon = Anonymizer()
        
        data = {
            "user": {
                "email": "john@example.com",
                "name": "John Doe"
            },
            "project": "CORTEX"
        }
        
        result = anon.anonymize_dict(data, fields=["user.email", "user.name"])
        
        assert result.anonymized_data["user"]["email"] != "john@example.com"
        assert result.anonymized_data["user"]["name"] != "John Doe"
        assert result.anonymized_data["project"] == "CORTEX"
    
    def test_validate_anonymization_success(self):
        """Test validation passes when no PII detected"""
        anon = Anonymizer()
        
        # Hash with no PII
        text = "a1b2c3d4e5f6g7h8i9j0"
        validation = anon.validate_anonymization(text)
        
        assert validation.is_valid is True
        assert validation.pii_detected.has_pii is False
        assert len(validation.violations) == 0
    
    def test_validate_anonymization_failure(self):
        """Test validation fails when PII still present"""
        anon = Anonymizer()
        
        # Text with email PII
        text = "Contact john.doe@example.com"
        validation = anon.validate_anonymization(text)
        
        assert validation.is_valid is False
        assert validation.pii_detected.has_pii is True
        assert PIIType.EMAIL in validation.pii_detected.pii_types
        assert len(validation.violations) > 0
    
    def test_skull_compliance_check(self):
        """Test SKULL_PRIVACY_PROTECTION compliance validation"""
        anon = Anonymizer()
        
        # Compliant data (hashed)
        compliant_data = {
            "engineer_hash": "a1b2c3d4e5f6...",
            "metrics": {"requests": 100}
        }
        assert anon.check_skull_compliance(compliant_data) is True
        
        # Non-compliant data (email present)
        non_compliant_data = {
            "engineer_id": "john@example.com",
            "metrics": {"requests": 100}
        }
        assert anon.check_skull_compliance(non_compliant_data) is False
    
    def test_batch_anonymization(self):
        """Test anonymizing multiple strings in batch"""
        anon = Anonymizer()
        
        inputs = [
            "john@example.com",
            "jane@example.com",
            "bob@example.com"
        ]
        
        results = anon.batch_anonymize(inputs)
        
        assert len(results) == 3
        assert all(len(h) == 64 for h in results)  # All SHA-256
        assert len(set(results)) == 3  # All unique
        
        # Same input in batch should produce same hash
        inputs_with_dup = ["john@example.com", "jane@example.com", "john@example.com"]
        results_with_dup = anon.batch_anonymize(inputs_with_dup)
        assert results_with_dup[0] == results_with_dup[2]
    
    def test_reversibility_check(self):
        """Test that anonymization is truly one-way (irreversible)"""
        anon = Anonymizer()
        
        original = "john.doe@example.com"
        hashed = anon.anonymize(original)
        
        # Should not be able to reverse
        assert anon.can_reverse(hashed) is False
        
        # Even with salt known, should be irreversible
        anon_with_salt = Anonymizer(salt="known_salt")
        hashed_with_salt = anon_with_salt.anonymize(original)
        assert anon_with_salt.can_reverse(hashed_with_salt) is False


class TestAnonymizationResult:
    """Test AnonymizationResult data class"""
    
    def test_anonymization_result_structure(self):
        """Test AnonymizationResult has correct fields"""
        result = AnonymizationResult(
            original_keys=["email"],
            anonymized_data={"email": "hash123"},
            algorithm="SHA-256",
            salt_used=True
        )
        
        assert result.original_keys == ["email"]
        assert result.anonymized_data == {"email": "hash123"}
        assert result.algorithm == "SHA-256"
        assert result.salt_used is True


class TestPIIDetectionResult:
    """Test PIIDetectionResult data class"""
    
    def test_pii_detection_result_structure(self):
        """Test PIIDetectionResult has correct fields"""
        result = PIIDetectionResult(
            has_pii=True,
            pii_types=[PIIType.EMAIL],
            matches=["john@example.com"],
            confidence=0.95
        )
        
        assert result.has_pii is True
        assert PIIType.EMAIL in result.pii_types
        assert "john@example.com" in result.matches
        assert result.confidence == 0.95
