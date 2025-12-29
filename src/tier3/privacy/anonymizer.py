"""
Privacy Anonymizer Module

Centralized privacy protection for adoption analytics.
Implements SHA-256 hashing, PII detection, and SKULL_PRIVACY_PROTECTION compliance.

Author: Asif Hussain
Version: 1.0.0
"""

import hashlib
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class PIIType(Enum):
    """Types of Personally Identifiable Information"""
    EMAIL = "email"
    USERNAME = "username"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    NAME = "name"


@dataclass
class PIIDetectionResult:
    """Result of PII detection scan"""
    has_pii: bool
    pii_types: List[PIIType] = field(default_factory=list)
    matches: List[str] = field(default_factory=list)
    confidence: float = 1.0  # Detection confidence (0.0-1.0)


@dataclass
class AnonymizationResult:
    """Result of anonymization operation"""
    original_keys: List[str]
    anonymized_data: Dict[str, Any]
    algorithm: str = "SHA-256"
    salt_used: bool = False


@dataclass
class ValidationResult:
    """Result of anonymization validation"""
    is_valid: bool
    pii_detected: PIIDetectionResult
    violations: List[str] = field(default_factory=list)


class Anonymizer:
    """
    Centralized privacy anonymization with SHA-256 hashing.
    
    Features:
    - Deterministic hashing (same input → same output)
    - Optional salt for additional security
    - PII detection (email, username, phone, IP)
    - PII stripping with hash replacement
    - Dictionary field anonymization (including nested)
    - SKULL compliance validation
    - Batch processing support
    
    Usage:
        anon = Anonymizer(salt="optional_salt")
        hashed = anon.anonymize("john.doe@example.com")
        
        # Dictionary anonymization
        data = {"email": "john@example.com", "team": "Platform"}
        result = anon.anonymize_dict(data, fields=["email"])
        
        # PII detection and stripping
        detection = anon.detect_pii("Contact john@example.com")
        stripped = anon.strip_pii("Contact john@example.com")
    """
    
    # PII detection patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    # More restrictive: must contain numbers/underscores OR be 8+ chars (avoid common words)
    USERNAME_PATTERN = re.compile(r'\b(?=.*[0-9_-])[a-zA-Z0-9_-]{3,20}\b|\b[a-zA-Z0-9_-]{8,20}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')  # US phone numbers
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')  # IPv4 addresses
    HASH_PATTERN = re.compile(r'\b[a-f0-9]{32,}\b')  # Hexadecimal hashes (MD5/SHA-256/etc)
    
    def __init__(self, salt: str = ""):
        """
        Initialize anonymizer with optional salt.
        
        Args:
            salt: Optional salt string for additional hash security
        """
        self.salt = salt
    
    def anonymize(self, value: str) -> str:
        """
        Anonymize string using SHA-256 hash.
        
        Args:
            value: String to anonymize
            
        Returns:
            64-character hexadecimal SHA-256 hash
        """
        combined = f"{value}{self.salt}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()
    
    def detect_pii(self, text: str) -> PIIDetectionResult:
        """
        Detect personally identifiable information in text.
        
        Args:
            text: Text to scan for PII
            
        Returns:
            PIIDetectionResult with detected types and matches
        """
        pii_types = []
        matches = []
        
        # Email detection
        email_matches = self.EMAIL_PATTERN.findall(text)
        if email_matches:
            pii_types.append(PIIType.EMAIL)
            matches.extend(email_matches)
            
            # Email prefix counts as username
            if PIIType.USERNAME not in pii_types:
                pii_types.append(PIIType.USERNAME)
        
        # Hash detection (for exclusion from PII)
        hash_matches = self.HASH_PATTERN.findall(text)
        
        # Username detection (only if contains numbers/underscores OR 12+ chars)
        # This avoids false positives on common words and hashes
        username_matches = self.USERNAME_PATTERN.findall(text)
        if username_matches and PIIType.USERNAME not in pii_types:
            # Filter: must contain digit OR underscore OR be 12+ chars
            # Exclude: hashes, email prefixes, and hash-like patterns
            valid_usernames = [
                u for u in username_matches 
                if (any(c.isdigit() for c in u) or '_' in u or '-' in u or len(u) >= 12)
                and u not in [e.split('@')[0] for e in email_matches]  # Exclude email prefixes
                and u not in hash_matches  # Exclude hexadecimal hashes
                and not self.HASH_PATTERN.match(u)  # Exclude hash-like strings
                and not self._looks_like_hash(u)  # Exclude hash-like patterns
            ]
            if valid_usernames:
                pii_types.append(PIIType.USERNAME)
                matches.extend(valid_usernames)
        
        # Phone detection
        phone_matches = self.PHONE_PATTERN.findall(text)
        if phone_matches:
            pii_types.append(PIIType.PHONE)
            matches.extend(phone_matches)
        
        # IP address detection
        ip_matches = self.IP_PATTERN.findall(text)
        if ip_matches:
            pii_types.append(PIIType.IP_ADDRESS)
            matches.extend(ip_matches)
        
        return PIIDetectionResult(
            has_pii=len(pii_types) > 0,
            pii_types=pii_types,
            matches=matches,
            confidence=1.0 if matches else 0.0
        )
    
    def strip_pii(self, text: str) -> 'StripResult':
        """
        Strip PII from text and replace with hashes.
        
        Args:
            text: Text to sanitize
            
        Returns:
            StripResult with sanitized text and detection info
        """
        detection = self.detect_pii(text)
        sanitized = text
        
        if detection.has_pii:
            # Replace each match with its hash
            for match in detection.matches:
                hashed = self.anonymize(match)
                sanitized = sanitized.replace(match, hashed[:16])  # Use first 16 chars of hash
        
        return StripResult(
            sanitized_text=sanitized,
            pii_found=detection,
            replacements_made=len(detection.matches)
        )
    
    def anonymize_dict(self, data: Dict[str, Any], fields: List[str]) -> AnonymizationResult:
        """
        Anonymize specific fields in dictionary.
        
        Args:
            data: Dictionary to anonymize
            fields: List of field paths to anonymize (supports nested with dot notation)
            
        Returns:
            AnonymizationResult with anonymized data
        """
        anonymized = data.copy()
        original_keys = []
        
        for field_path in fields:
            parts = field_path.split('.')
            
            # Navigate to nested field
            current = anonymized
            for part in parts[:-1]:
                if part in current and isinstance(current[part], dict):
                    current = current[part]
                else:
                    break  # Field path doesn't exist
            else:
                # Anonymize final field
                final_key = parts[-1]
                if final_key in current:
                    original_value = current[final_key]
                    if isinstance(original_value, str):
                        current[final_key] = self.anonymize(original_value)
                        original_keys.append(field_path)
        
        return AnonymizationResult(
            original_keys=original_keys,
            anonymized_data=anonymized,
            algorithm="SHA-256",
            salt_used=len(self.salt) > 0
        )
    
    def validate_anonymization(self, text: str) -> ValidationResult:
        """
        Validate that text contains no PII (proper anonymization).
        
        Args:
            text: Text to validate
            
        Returns:
            ValidationResult with validation status and violations
        """
        detection = self.detect_pii(text)
        violations = []
        
        if detection.has_pii:
            for pii_type in detection.pii_types:
                violations.append(f"PII detected: {pii_type.value}")
        
        return ValidationResult(
            is_valid=not detection.has_pii,
            pii_detected=detection,
            violations=violations
        )
    
    def check_skull_compliance(self, data: Dict[str, Any]) -> bool:
        """
        Check if data complies with SKULL_PRIVACY_PROTECTION rules.
        
        Args:
            data: Dictionary to check for PII
            
        Returns:
            True if compliant (no PII in values), False otherwise
        """
        # Check only values (recursively), not keys
        def check_values(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    if not check_values(value):
                        return False
            elif isinstance(obj, list):
                for item in obj:
                    if not check_values(item):
                        return False
            elif isinstance(obj, str):
                # Check string for PII
                detection = self.detect_pii(obj)
                if detection.has_pii:
                    return False
            return True
        
        return check_values(data)
    
    def batch_anonymize(self, values: List[str]) -> List[str]:
        """
        Anonymize multiple strings in batch.
        
        Args:
            values: List of strings to anonymize
            
        Returns:
            List of hashed values (same order as input)
        """
        return [self.anonymize(v) for v in values]
    
    def can_reverse(self, hashed_value: str) -> bool:
        """
        Check if hash can be reversed (should always be False for SHA-256).
        
        Args:
            hashed_value: Hash to check
            
        Returns:
            False (SHA-256 is one-way)
        """
        return False  # SHA-256 is cryptographically irreversible
    
    def _looks_like_hash(self, text: str) -> bool:
        """
        Check if text looks like a hash (high alphanumeric density, no clear words).
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be a hash-like sequence
        """
        # Must be 12+ chars and have good digit/letter distribution
        if len(text) < 12:
            return False
        
        digit_count = sum(1 for c in text if c.isdigit())
        letter_count = sum(1 for c in text if c.isalpha())
        
        # Hash-like if 30%+ digits and 30%+ letters (mixed well)
        total = len(text)
        return (digit_count / total >= 0.3) and (letter_count / total >= 0.3)


@dataclass
class StripResult:
    """Result of PII stripping operation"""
    sanitized_text: str
    pii_found: PIIDetectionResult
    replacements_made: int
