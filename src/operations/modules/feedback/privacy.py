"""
Privacy Sanitization Engine

Removes sensitive data from feedback reports based on privacy level.

Privacy Levels:
- full: Remove all potentially sensitive data (paths, usernames, etc.)
- medium: Remove obvious sensitive data (passwords, keys, emails)
- minimal: Remove only critical secrets (passwords, API keys)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import re
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class PrivacySanitizer:
    """Sanitize feedback reports for privacy protection."""
    
    def __init__(self, privacy_level: str = 'medium'):
        """
        Initialize sanitizer with privacy level.
        
        Args:
            privacy_level: 'full', 'medium', or 'minimal'
        """
        self.privacy_level = privacy_level
        
        # Patterns to always remove (critical secrets)
        self.critical_patterns = {
            'password': r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
            'api_key': r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
            'token': r'token["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
            'secret': r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s]+)',
            'private_key': r'-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----'
        }
        
        # Patterns for medium level (PII)
        self.medium_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
        }
        
        # Patterns for full level (identifying info)
        self.full_patterns = {
            'file_path': r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*',
            'unix_path': r'/(?:[^/\s]+/)+[^/\s]*',
            'username': r'\b(?:user|username)["\']?\s*[:=]\s*["\']?([^"\'}\s]+)'
        }
    
    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize feedback report based on privacy level.
        
        Args:
            data: Feedback report dictionary
        
        Returns:
            Sanitized feedback report
        """
        try:
            # Always remove critical secrets
            data = self._sanitize_dict(data, self.critical_patterns)
            
            # Remove medium-level PII if privacy >= medium
            if self.privacy_level in ['medium', 'full']:
                data = self._sanitize_dict(data, self.medium_patterns)
            
            # Remove full-level identifying info if privacy = full
            if self.privacy_level == 'full':
                data = self._sanitize_dict(data, self.full_patterns)
            
            logger.info(f"Privacy sanitization complete (level: {self.privacy_level})")
            return data
            
        except Exception as e:
            logger.warning(f"Privacy sanitization encountered issues: {e}")
            return data
    
    def _sanitize_dict(
        self,
        data: Dict[str, Any],
        patterns: Dict[str, str]
    ) -> Dict[str, Any]:
        """Recursively sanitize dictionary values."""
        if isinstance(data, dict):
            return {
                key: self._sanitize_dict(value, patterns)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._sanitize_dict(item, patterns) for item in data]
        elif isinstance(data, str):
            return self._sanitize_string(data, patterns)
        else:
            return data
    
    def _sanitize_string(self, text: str, patterns: Dict[str, str]) -> str:
        """Sanitize string by removing sensitive patterns."""
        for pattern_name, pattern in patterns.items():
            text = re.sub(pattern, f'[REDACTED_{pattern_name.upper()}]', text, flags=re.IGNORECASE | re.DOTALL)
        return text
    
    def redact_file_paths(self, text: str) -> str:
        """Redact file paths from text."""
        if self.privacy_level == 'full':
            # Windows paths
            text = re.sub(r'[A-Za-z]:\\[^\s<>"]+', '[REDACTED_PATH]', text)
            # Unix paths
            text = re.sub(r'/(?:[^/\s]+/)+[^/\s]*', '[REDACTED_PATH]', text)
        return text
    
    def anonymize_user_identifier(self, user_id: str) -> str:
        """Convert user identifier to non-reversible hash."""
        import hashlib
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
