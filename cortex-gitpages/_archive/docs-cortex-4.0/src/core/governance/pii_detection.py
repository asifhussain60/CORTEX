"""DATA-001: PII Detection & Sanitization"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import re

class PIIType(Enum):
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    NAME = "name"

@dataclass
class PIIDetectionResult:
    detected: bool
    pii_types: List[PIIType] = field(default_factory=list)
    locations: List[tuple] = field(default_factory=list)

class PIIDetector:
    PATTERNS = {
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
        PIIType.CREDIT_CARD: r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    }
    
    def detect_pii(self, text: str) -> PIIDetectionResult:
        detected = False
        pii_types = []
        locations = []
        
        for pii_type, pattern in self.PATTERNS.items():
            matches = list(re.finditer(pattern, text))
            if matches:
                detected = True
                pii_types.append(pii_type)
                for match in matches:
                    locations.append((pii_type, match.start(), match.end()))
        
        return PIIDetectionResult(
            detected=detected,
            pii_types=pii_types,
            locations=locations
        )
    
    def sanitize_pii(self, text: str) -> str:
        result = text
        for pii_type, pattern in self.PATTERNS.items():
            result = re.sub(pattern, "[REDACTED]", result)
        return result
