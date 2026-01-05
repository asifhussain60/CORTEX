"""
PII Sanitizer - Phase 4 Security Component

Detects and redacts personally identifiable information (PII) and secrets from text.

Supports:
- SSN (Social Security Numbers)
- Credit Cards
- API Keys (OpenAI, AWS, etc.)
- Passwords
- JWT Tokens
- Email Addresses
- Phone Numbers
- Nested JSON structures

Usage:
    sanitizer = PIISanitizer()
    clean_text = sanitizer.sanitize("SSN: 123-45-6789")
    # Result: "SSN: [REDACTED_SSN]"
"""

import re
import json
from typing import Dict, List, Optional, Tuple


class PIISanitizer:
    """Sanitizes PII and secrets from text using regex patterns."""
    
    # Regex patterns for PII detection
    PATTERNS: Dict[str, Tuple[str, str]] = {
        # SSN patterns
        'ssn_dashed': (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]'),
        'ssn_plain': (r'\b\d{9}\b', '[REDACTED_SSN]'),
        
        # Credit card patterns (13-19 digits)
        'cc_plain': (r'\b\d{13,19}\b', '[REDACTED_CC]'),
        'cc_spaced': (r'\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b', '[REDACTED_CC]'),
        
        # API keys (order matters - check longer patterns first)
        'openai_key': (r'sk-[a-zA-Z0-9]{10,}', '[REDACTED_API_KEY]'),  # Lowered threshold from 32
        'aws_key': (r'AKIA[0-9A-Z]{16}', '[REDACTED_API_KEY]'),
        'generic_api_key': (r'api[_-]?key["\']?\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{20,})', '[REDACTED_API_KEY]'),
        
        # Passwords
        'password_assignment': (r'password\s*=\s*["\']([^"\']{6,})["\']', '[REDACTED_PASSWORD]'),
        'password_env': (r'PASSWORD=([^\s]{6,})', '[REDACTED_PASSWORD]'),
        
        # JWT tokens
        'jwt': (r'eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+', '[REDACTED_TOKEN]'),
        
        # Email (partial redaction)
        'email': (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', '[REDACTED_EMAIL]'),
        
        # Phone numbers (must come after API keys to avoid false positives)
        'phone_us': (r'\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', '[REDACTED_PHONE]'),
    }
    
    def __init__(self):
        """Initialize PIISanitizer with compiled regex patterns."""
        self.compiled_patterns: List[Tuple[re.Pattern, str]] = [
            (re.compile(pattern, re.IGNORECASE), placeholder)
            for pattern, placeholder in self.PATTERNS.values()
        ]
    
    def sanitize(
        self,
        text: Optional[str],
        placeholder_template: Optional[str] = None
    ) -> str:
        """
        Sanitize PII and secrets from text.
        
        Args:
            text: Input text to sanitize
            placeholder_template: Optional custom placeholder (overrides defaults)
        
        Returns:
            Sanitized text with PII replaced by placeholders
        """
        if text is None:
            return ""
        
        if not text:
            return text
        
        result = text
        
        # Apply all patterns
        for pattern, default_placeholder in self.compiled_patterns:
            placeholder = placeholder_template if placeholder_template else default_placeholder
            result = pattern.sub(placeholder, result)
        
        return result
    
    def sanitize_dict(
        self,
        data: Dict,
        placeholder_template: Optional[str] = None
    ) -> Dict:
        """
        Recursively sanitize PII in dictionary/JSON structures.
        
        Args:
            data: Dictionary to sanitize
            placeholder_template: Optional custom placeholder
        
        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.sanitize(value, placeholder_template)
            elif isinstance(value, dict):
                result[key] = self.sanitize_dict(value, placeholder_template)
            elif isinstance(value, list):
                result[key] = [
                    self.sanitize_dict(item, placeholder_template) if isinstance(item, dict)
                    else self.sanitize(item, placeholder_template) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
