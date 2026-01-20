"""Prompt injection attack prevention and sanitization."""

import re
from typing import List, Dict, Any


class PromptInjectionSanitizer:
    """Detect and prevent prompt injection attacks."""
    
    DANGEROUS_PATTERNS = [
        r"ignore.*previous",
        r"override.*instruction",
        r"execute.*command",
        r"run.*code"
    ]
    
    def __init__(self):
        self.blocked_attempts: List[Dict[str, Any]] = []
    
    def sanitize(self, prompt: str) -> str:
        """Sanitize prompt against injection attacks."""
        sanitized = prompt
        
        for pattern in self.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, "[BLOCKED]", sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    def detect_injection(self, prompt: str) -> bool:
        """Detect potential injection attempts."""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, prompt, flags=re.IGNORECASE):
                self.blocked_attempts.append({
                    "prompt": prompt[:100],
                    "pattern_matched": pattern
                })
                return True
        return False
