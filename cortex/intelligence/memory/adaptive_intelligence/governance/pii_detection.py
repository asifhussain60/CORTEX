"""Tier2 Governance: Pii Detection

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set
import re


class PIIType(Enum):
    """PII data types."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    NAME = "name"
    ADDRESS = "address"


@dataclass
class PIIDetectionResult:
    """Result of PII detection.
    
    Attributes:
        detected: Whether PII was detected
        pii_types: Types of PII found
        locations: Positions of PII in text
    """
    detected: bool = False
    pii_types: Set[PIIType] = field(default_factory=set)
    locations: List[tuple] = field(default_factory=list)


class PIIDetector:
    """Detect PII in data.
    
    Attributes:
        strict_mode: Enable strict PII detection
        patterns: Regex patterns for PII types
    """
    
    def __init__(self, strict_mode: bool = True):
        """Initialize PII detector.
        
        Args:
            strict_mode: Enable strict detection mode
        """
        self.strict_mode = strict_mode
        self.patterns = {
            PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            PIIType.PHONE: re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'),
            PIIType.SSN: re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        }
    
    def detect_pii(self, text: str) -> PIIDetectionResult:
        """Detect PII in text.
        
        Args:
            text: Text to scan for PII
            
        Returns:
            PIIDetectionResult with detected PII types
        """
        result = PIIDetectionResult()
        
        for pii_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                result.detected = True
                result.pii_types.add(pii_type)
                result.locations.append((match.start(), match.end()))
        
        return result
    
    def sanitize_pii(self, text: str) -> str:
        """Sanitize PII from text.
        
        Args:
            text: Text containing PII
            
        Returns:
            Text with PII redacted
        """
        sanitized = text
        
        for pii_type, pattern in self.patterns.items():
            sanitized = pattern.sub("[REDACTED]", sanitized)
        
        return sanitized
    
    def detect(self, text: str) -> list:
        """Detect PII (backward compatibility).
        
        Args:
            text: Text to scan
            
        Returns:
            List of detected PII types
        """
        result = self.detect_pii(text)
        return list(result.pii_types)


__all__ = ["PIIType", "PIIDetectionResult", "PIIDetector"]
