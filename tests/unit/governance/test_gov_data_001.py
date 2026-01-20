"""Test for DATA-001: PII Detection"""
import pytest
from cortex.core.governance.pii_detection import (
    PIIDetector,
    PIIType,
)

class TestPIIDetection:
    def test_detect_email(self):
        detector = PIIDetector()
        result = detector.detect_pii("Contact: user@example.com")
        assert result.detected
        assert PIIType.EMAIL in result.pii_types
    
    def test_detect_phone(self):
        detector = PIIDetector()
        result = detector.detect_pii("Call 555-123-4567")
        assert result.detected
        assert PIIType.PHONE in result.pii_types
    
    def test_detect_ssn(self):
        detector = PIIDetector()
        result = detector.detect_pii("SSN: 123-45-6789")
        assert result.detected
        assert PIIType.SSN in result.pii_types
    
    def test_no_pii(self):
        detector = PIIDetector()
        result = detector.detect_pii("This is safe text")
        assert not result.detected
    
    def test_sanitize(self):
        detector = PIIDetector()
        text = "Email: test@example.com"
        sanitized = detector.sanitize_pii(text)
        assert "test@example.com" not in sanitized
        assert "[REDACTED]" in sanitized
