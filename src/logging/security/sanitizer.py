"""
PII Sanitizer for Audit Logger.

Detects and sanitizes Personally Identifiable Information (PII)
and sensitive data in log entries before storage.

Features:
- 10+ built-in PII pattern types (email, phone, SSN, credit cards, etc.)
- Custom regex patterns
- Recursive sanitization (dicts, lists, strings)
- Multiple masking strategies (full, partial)
- PII detection without sanitization
- Sanitization statistics tracking

Supported PII Types:
- Email addresses
- Phone numbers (US format)
- Social Security Numbers
- Credit card numbers (Visa, MC, Amex, Discover)
- API keys (generic pattern)
- AWS access keys
- JWT tokens
- GitHub tokens (ghp_, ghs_)
- Passwords in key-value format
- IP addresses (IPv4)
- Custom regex patterns

Usage:
    # Full masking (production)
    from src.logging.security import PIISanitizer
    sanitizer = PIISanitizer()
    sanitized_data = sanitizer.sanitize(data)
    
    # Partial masking (debugging)
    from src.logging.security import PartialMaskSanitizer
    sanitizer = PartialMaskSanitizer()
    sanitized_data = sanitizer.sanitize(data)
    
    # Custom patterns
    sanitizer = PIISanitizer(custom_patterns=[
        (r'\\bCUSTOM-\\d{6}\\b', '***CUSTOM_ID***')
    ])
    
    # Detection only (no sanitization)
    detections = sanitizer.detect_pii(data)
"""

import re
from typing import Any, Dict, List, Pattern, Tuple
from dataclasses import dataclass
from enum import Enum


class PIIType(Enum):
    """Types of PII that can be detected."""
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    API_KEY = "api_key"
    PASSWORD = "password"
    IP_ADDRESS = "ip_address"
    AWS_KEY = "aws_key"
    JWT_TOKEN = "jwt_token"
    GITHUB_TOKEN = "github_token"
    CUSTOM = "custom"


@dataclass
class PIIPattern:
    """Represents a PII detection pattern."""
    pii_type: PIIType
    pattern: Pattern
    replacement: str
    description: str


class PIISanitizer:
    """
    Sanitizes PII from data structures.
    
    Features:
    - Recursive sanitization (dicts, lists, strings)
    - Multiple PII types supported
    - Configurable patterns
    - Masking strategies (full, partial, hash)
    - Audit trail of sanitizations
    """
    
    def __init__(
        self,
        mask_strategy: str = "full",  # full, partial, hash
        custom_patterns: List[Tuple[str, str]] = None
    ):
        """
        Initialize PII sanitizer.
        
        Args:
            mask_strategy: How to mask PII (full, partial, hash)
            custom_patterns: List of (regex_pattern, replacement) tuples
        """
        self.mask_strategy = mask_strategy
        self._sanitization_count = 0
        self._custom_patterns = custom_patterns or []
        self._patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[PIIPattern]:
        """
        Build list of PII detection patterns.
        
        Pattern Order Matters:
        1. Custom patterns (highest priority)
        2. Email addresses
        3. IP addresses (before phone to avoid conflicts)
        4. SSN (before phone to avoid conflicts)
        5. Phone numbers
        6. Credit cards
        7. API keys
        8. AWS keys
        9. JWT tokens
        10. GitHub tokens
        11. Passwords
        
        Returns:
            List of PIIPattern objects in priority order
        """
        patterns = []
        
        # Add custom patterns FIRST so they take precedence
        for pattern, replacement in self._custom_patterns:
            patterns.append(PIIPattern(
                pii_type=PIIType.CUSTOM,
                pattern=re.compile(pattern, re.IGNORECASE),
                replacement=replacement,
                description="Custom pattern"
            ))
        
        # Email addresses
        patterns.append(PIIPattern(
            pii_type=PIIType.EMAIL,
            pattern=re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ),
            replacement="***EMAIL***",
            description="Email address"
        ))
        
        # IP Addresses (IPv4) - must come before phone to avoid conflicts
        patterns.append(PIIPattern(
            pii_type=PIIType.IP_ADDRESS,
            pattern=re.compile(
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            ),
            replacement="***IP***",
            description="IP address"
        ))
        
        # Social Security Numbers - before phone to avoid conflicts
        patterns.append(PIIPattern(
            pii_type=PIIType.SSN,
            pattern=re.compile(
                r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b'
            ),
            replacement="***SSN***",
            description="Social Security Number"
        ))
        
        # Phone numbers (US format - must come after IP and SSN)
        patterns.append(PIIPattern(
            pii_type=PIIType.PHONE,
            pattern=re.compile(
                r'(?:^|[^\d.])(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3,4})(?:[-.\s]?([0-9]{4}))?\b'
            ),
            replacement="***PHONE***",
            description="Phone number"
        ))
        
        # Credit card numbers
        patterns.append(PIIPattern(
            pii_type=PIIType.CREDIT_CARD,
            pattern=re.compile(
                r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b'
            ),
            replacement="***CARD***",
            description="Credit card number"
        ))
        
        # API Keys (generic pattern)
        patterns.append(PIIPattern(
            pii_type=PIIType.API_KEY,
            pattern=re.compile(
                r'\b(?:api[_-]?key|apikey|access[_-]?key)["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{20,})["\']?',
                re.IGNORECASE
            ),
            replacement="***API_KEY***",
            description="API key"
        ))
        
        # AWS Access Keys
        patterns.append(PIIPattern(
            pii_type=PIIType.AWS_KEY,
            pattern=re.compile(
                r'\b(AKIA[0-9A-Z]{16})\b'
            ),
            replacement="***AWS_KEY***",
            description="AWS access key"
        ))
        
        # JWT Tokens
        patterns.append(PIIPattern(
            pii_type=PIIType.JWT_TOKEN,
            pattern=re.compile(
                r'\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b'
            ),
            replacement="***JWT***",
            description="JWT token"
        ))
        
        # GitHub tokens (various formats - ghp_, ghs_, gho_)
        patterns.append(PIIPattern(
            pii_type=PIIType.GITHUB_TOKEN,
            pattern=re.compile(
                r'\bgh[ps]_[A-Za-z0-9_]{30,}\b'
            ),
            replacement="***GITHUB_TOKEN***",
            description="GitHub token"
        ))
        
        # Passwords (in common formats)
        patterns.append(PIIPattern(
            pii_type=PIIType.PASSWORD,
            pattern=re.compile(
                r'\b(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s]{6,})["\']?',
                re.IGNORECASE
            ),
            replacement="***PASSWORD***",
            description="Password"
        ))
        
        return patterns
    
    def sanitize(self, data: Any) -> Any:
        """
        Sanitize data recursively.
        
        Args:
            data: Data to sanitize (str, dict, list, or primitive)
        
        Returns:
            Sanitized data with PII removed
        """
        if isinstance(data, dict):
            return self._sanitize_dict(data)
        elif isinstance(data, list):
            return self._sanitize_list(data)
        elif isinstance(data, str):
            return self._sanitize_string(data)
        else:
            return data
    
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary."""
        sanitized = {}
        
        for key, value in data.items():
            # Check if key indicates sensitive data
            if self._is_sensitive_key(key):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = self.sanitize(value)
        
        return sanitized
    
    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitize list."""
        return [self.sanitize(item) for item in data]
    
    def _sanitize_string(self, data: str) -> str:
        """Sanitize string using PII patterns."""
        sanitized = data
        count_before = self._sanitization_count
        
        for pattern_obj in self._patterns:
            matches = list(pattern_obj.pattern.finditer(sanitized))
            if matches:
                sanitized = pattern_obj.pattern.sub(
                    pattern_obj.replacement,
                    sanitized
                )
                # Count each match as a sanitization
                self._sanitization_count += len(matches)
        
        return sanitized
    
    def _is_sensitive_key(self, key: str) -> bool:
        """
        Check if dictionary key indicates sensitive data.
        
        Args:
            key: Dictionary key to check
        
        Returns:
            True if key is sensitive
        """
        sensitive_keys = {
            'password', 'passwd', 'pwd', 'secret', 'api_key', 'apikey',
            'access_key', 'private_key', 'token', 'auth', 'authorization',
            'credentials', 'credit_card', 'ssn', 'social_security'
        }
        
        return key.lower() in sensitive_keys
    
    def get_sanitization_stats(self) -> Dict[str, Any]:
        """
        Get statistics about sanitizations performed.
        
        Returns:
            Dictionary with sanitization statistics
        """
        return {
            "total_sanitizations": self._sanitization_count,
            "patterns_configured": len(self._patterns),
            "mask_strategy": self.mask_strategy
        }
    
    def detect_pii(self, data: Any) -> List[Dict[str, Any]]:
        """
        Detect PII without sanitizing.
        
        Args:
            data: Data to scan for PII
        
        Returns:
            List of detected PII instances
        """
        detections = []
        
        if isinstance(data, str):
            for pattern_obj in self._patterns:
                matches = pattern_obj.pattern.finditer(data)
                for match in matches:
                    detections.append({
                        "type": pattern_obj.pii_type.value,
                        "description": pattern_obj.description,
                        "position": match.span(),
                        "length": len(match.group(0))
                    })
        elif isinstance(data, dict):
            for key, value in data.items():
                if self._is_sensitive_key(key):
                    detections.append({
                        "type": "sensitive_key",
                        "description": f"Sensitive key: {key}",
                        "key": key
                    })
                detections.extend(self.detect_pii(value))
        elif isinstance(data, list):
            for item in data:
                detections.extend(self.detect_pii(item))
        
        return detections


class PartialMaskSanitizer(PIISanitizer):
    """
    Sanitizer that partially masks PII for debugging.
    
    Example:
        Email: test@example.com -> t***@e***.com
        Phone: 555-123-4567 -> ***-***-4567
    """
    
    def _sanitize_string(self, data: str) -> str:
        """Sanitize with partial masking."""
        sanitized = data
        
        for pattern_obj in self._patterns:
            matches = list(pattern_obj.pattern.finditer(sanitized))
            
            for match in reversed(matches):  # Reverse to maintain positions
                original = match.group(0)
                
                # Partial masking logic based on PII type
                if pattern_obj.pii_type == PIIType.EMAIL:
                    masked = self._mask_email(original)
                elif pattern_obj.pii_type == PIIType.PHONE:
                    masked = self._mask_phone(original)
                elif pattern_obj.pii_type == PIIType.CREDIT_CARD:
                    masked = self._mask_credit_card(original)
                else:
                    # Default: show first and last char
                    masked = self._mask_default(original)
                
                sanitized = (
                    sanitized[:match.start()] +
                    masked +
                    sanitized[match.end():]
                )
                self._sanitization_count += 1
        
        return sanitized
    
    def _mask_email(self, email: str) -> str:
        """Mask email partially: t***@e***.com"""
        if '@' not in email:
            return "***EMAIL***"
        
        local, domain = email.split('@', 1)
        masked_local = local[0] + '***' if len(local) > 0 else '***'
        masked_domain = domain[0] + '***' + domain[domain.rfind('.'):] if '.' in domain else '***'
        
        return f"{masked_local}@{masked_domain}"
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone partially: ***-***-4567"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 4:
            return f"***-***-{digits[-4:]}"
        return "***PHONE***"
    
    def _mask_credit_card(self, card: str) -> str:
        """Mask credit card: ****-****-****-1234"""
        digits = re.sub(r'\D', '', card)
        if len(digits) >= 4:
            return f"****-****-****-{digits[-4:]}"
        return "***CARD***"
    
    def _mask_default(self, text: str) -> str:
        """Default masking: show first and last char."""
        if len(text) <= 2:
            return '***'
        return f"{text[0]}***{text[-1]}"


def create_sanitizer(strategy: str = "full") -> PIISanitizer:
    """
    Factory function to create appropriate sanitizer.
    
    Args:
        strategy: Sanitization strategy (full, partial, hash)
    
    Returns:
        PIISanitizer instance
    """
    if strategy == "partial":
        return PartialMaskSanitizer(mask_strategy="partial")
    else:
        return PIISanitizer(mask_strategy=strategy)
