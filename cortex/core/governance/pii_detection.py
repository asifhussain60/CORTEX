"""PII detection and redaction module."""

import re
from typing import List, Dict, Any, Tuple


class PIIDetector:
    """Detect personally identifiable information."""
    
    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"
    }
    
    def __init__(self):
        self.detected_pii: List[Dict[str, Any]] = []
    
    def detect(self, content: str) -> List[Tuple[str, str]]:
        """Detect PII in content."""
        findings = []
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                findings.append((pii_type, match.group()))
                self.detected_pii.append({
                    "type": pii_type,
                    "value": match.group(),
                    "position": match.start()
                })
        
        return findings
    
    def redact(self, content: str) -> str:
        """Redact PII from content."""
        result = content
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            result = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", result)
        
        return result
