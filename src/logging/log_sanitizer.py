"""
Log Sanitizer - PII and Sensitive Data Removal

Automatically detects and redacts sensitive information from logs:
- PII (emails, phone numbers, SSNs, credit cards)
- API keys, tokens, passwords
- File paths (user directories)
- IP addresses (optional)

Author: Asif Hussain
Created: 2026-01-05
"""

import re
from typing import Dict, Any, List, Pattern
from dataclasses import dataclass
import hashlib


@dataclass
class SanitizationRule:
    """Defines a sanitization pattern and replacement strategy"""
    name: str
    pattern: Pattern
    replacement: str
    severity: str  # 'critical', 'high', 'medium', 'low'


class LogSanitizer:
    """
    Sanitizes log entries by detecting and redacting sensitive information.
    
    Uses regex patterns and heuristics to identify:
    - PII (emails, phones, SSNs, credit cards)
    - Credentials (API keys, passwords, tokens)
    - File paths containing user directories
    - Optional: IP addresses
    """
    
    def __init__(self, enable_ip_redaction: bool = False):
        """
        Initialize the log sanitizer.
        
        Args:
            enable_ip_redaction: If True, redact IP addresses (default: False)
        """
        self.enable_ip_redaction = enable_ip_redaction
        self.rules = self._build_sanitization_rules()
        self._sanitization_stats: Dict[str, int] = {}
    
    def _build_sanitization_rules(self) -> List[SanitizationRule]:
        """Build the complete set of sanitization rules"""
        rules = [
            # Email addresses
            SanitizationRule(
                name='email',
                pattern=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                replacement='<EMAIL_REDACTED>',
                severity='high'
            ),
            
            # Phone numbers (US format)
            SanitizationRule(
                name='phone',
                pattern=re.compile(r'\b(\+?1[-.]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
                replacement='<PHONE_REDACTED>',
                severity='high'
            ),
            
            # Social Security Numbers
            SanitizationRule(
                name='ssn',
                pattern=re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
                replacement='<SSN_REDACTED>',
                severity='critical'
            ),
            
            # Credit card numbers (basic pattern)
            SanitizationRule(
                name='credit_card',
                pattern=re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
                replacement='<CC_REDACTED>',
                severity='critical'
            ),
            
            # API keys (common patterns - handles api_key, apiKey, API-KEY, etc.)
            SanitizationRule(
                name='api_key',
                pattern=re.compile(r'(["\']?[Aa][Pp][Ii][-_]?[Kk][Ee][Yy]["\']?\s*[:=]\s*["\']?)([A-Za-z0-9_\-]{16,})["\']?', re.IGNORECASE),
                replacement=r'\1<API_KEY_REDACTED>',
                severity='critical'
            ),
            
            # Standalone API key patterns (sk_live_, sk_test_, etc.)
            SanitizationRule(
                name='standalone_api_key',
                pattern=re.compile(r'\b(sk_(?:live|test)_[A-Za-z0-9]{20,})\b'),
                replacement='<API_KEY_REDACTED>',
                severity='critical'
            ),
            
            # Bearer tokens
            SanitizationRule(
                name='bearer_token',
                pattern=re.compile(r'[Bb]earer\s+([A-Za-z0-9_\-\.]+)'),
                replacement='Bearer <TOKEN_REDACTED>',
                severity='critical'
            ),
            
            # Password fields
            SanitizationRule(
                name='password',
                pattern=re.compile(r'(["\']?[Pp]assword["\']?\s*[:=]\s*["\']?)([^"\'\s]{6,})["\']?'),
                replacement=r'\1<PASSWORD_REDACTED>',
                severity='critical'
            ),
            
            # JWT tokens
            SanitizationRule(
                name='jwt',
                pattern=re.compile(r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*'),
                replacement='<JWT_REDACTED>',
                severity='critical'
            ),
            
            # User home directories
            SanitizationRule(
                name='home_dir',
                pattern=re.compile(r'/Users/[A-Za-z0-9_-]+|/home/[A-Za-z0-9_-]+|C:\\Users\\[A-Za-z0-9_-]+'),
                replacement='/home/<USER_REDACTED>',
                severity='medium'
            ),
        ]
        
        # Add IP address redaction if enabled
        if self.enable_ip_redaction:
            rules.append(
                SanitizationRule(
                    name='ip_address',
                    pattern=re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
                    replacement='<IP_REDACTED>',
                    severity='low'
                )
            )
        
        return rules
    
    def sanitize(self, data: Any) -> Any:
        """
        Sanitize a log entry (recursively handles dicts, lists, strings).
        
        Args:
            data: The data to sanitize (can be dict, list, str, or primitive)
        
        Returns:
            Sanitized version of the data
        """
        if isinstance(data, dict):
            return {k: self.sanitize(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize(item) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data)
        else:
            return data
    
    def _sanitize_string(self, text: str) -> str:
        """
        Apply all sanitization rules to a string.
        
        Args:
            text: The string to sanitize
        
        Returns:
            Sanitized string
        """
        sanitized = text
        
        for rule in self.rules:
            matches = rule.pattern.findall(sanitized)
            if matches:
                # Track statistics
                self._sanitization_stats[rule.name] = self._sanitization_stats.get(rule.name, 0) + len(matches)
                
                # Apply redaction
                sanitized = rule.pattern.sub(rule.replacement, sanitized)
        
        return sanitized
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get sanitization statistics.
        
        Returns:
            Dictionary mapping rule names to redaction counts
        """
        return self._sanitization_stats.copy()
    
    def reset_stats(self):
        """Reset sanitization statistics"""
        self._sanitization_stats.clear()
    
    def hash_sensitive_value(self, value: str, prefix: str = '') -> str:
        """
        Create a consistent hash of a sensitive value for correlation.
        
        Useful when you need to track the same entity across logs
        without storing the actual value.
        
        Args:
            value: The sensitive value to hash
            prefix: Optional prefix for the hash (e.g., 'user_', 'email_')
        
        Returns:
            Hashed value with prefix (e.g., 'user_a3f8b92c')
        """
        hash_obj = hashlib.sha256(value.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        return f"{prefix}{hash_hex}" if prefix else hash_hex


# Global singleton instance
_sanitizer_instance = None


def get_sanitizer(enable_ip_redaction: bool = False) -> LogSanitizer:
    """
    Get the global LogSanitizer instance (singleton pattern).
    
    Args:
        enable_ip_redaction: If True, enable IP address redaction
    
    Returns:
        LogSanitizer instance
    """
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = LogSanitizer(enable_ip_redaction)
    return _sanitizer_instance
