"""
Sanitization Engine - Pattern-Based Sensitive Data Detection

Centralized pattern registry consolidating regex patterns from:
- src/tier3/privacy/anonymizer.py
- src/operations/modules/feedback/privacy.py
- src/orchestration_4_0/orchestrators/documentation/enhanced_guardrails.py
- src/tier3/metrics/privacy_safe_export.py

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


logger = logging.getLogger(__name__)


class PatternCategory(Enum):
    """Categories of sensitive patterns"""
    CRITICAL_SECRETS = "critical_secrets"
    PII = "pii"
    PHI = "phi"
    PCI = "pci"
    PATHS = "paths"
    COMPANY = "company"
    HASHES = "hashes"  # For exclusion


class ReplacementStrategy(Enum):
    """How to replace detected sensitive data"""
    REMOVE = "remove"                    # Complete removal
    PLACEHOLDER = "placeholder"          # [REDACTED_TYPE]
    HASH = "hash"                       # SHA-256 hash
    PARTIAL = "partial"                 # ***-****-3456
    GENERIC = "generic"                 # user@example.com


@dataclass
class SanitizationMatch:
    """Single pattern match result"""
    category: PatternCategory
    pattern_name: str
    matched_text: str
    start_pos: int
    end_pos: int
    confidence: float
    replacement_strategy: ReplacementStrategy
    suggested_replacement: str


@dataclass
class PatternDefinition:
    """Pattern definition with metadata"""
    name: str
    regex: str
    category: PatternCategory
    confidence: float
    strategy: ReplacementStrategy
    priority: int  # Higher = checked first
    case_sensitive: bool = False


class PatternRegistry:
    """
    Centralized pattern registry for all sensitive data detection.
    
    Consolidates patterns from 5 existing CORTEX modules with
    priority-based matching and configurable strategies.
    """
    
    def __init__(self):
        """Initialize pattern registry with consolidated patterns."""
        self.patterns: Dict[PatternCategory, List[PatternDefinition]] = {}
        self._initialize_patterns()
        self.logger = logging.getLogger(__name__)
    
    def _initialize_patterns(self):
        """Load all patterns organized by category."""
        
        # ===== CRITICAL SECRETS (Priority 100+) =====
        self.patterns[PatternCategory.CRITICAL_SECRETS] = [
            PatternDefinition(
                name="password",
                regex=r'password["\']?\s*[:=]\s*["\']?([^"\'}\s]+)["\']?',
                category=PatternCategory.CRITICAL_SECRETS,
                confidence=0.99,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=110,
            ),
            PatternDefinition(
                name="api_key",
                regex=r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{32,})["\']?',
                category=PatternCategory.CRITICAL_SECRETS,
                confidence=0.95,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=109,
            ),
            PatternDefinition(
                name="token",
                regex=r'token["\']?\s*[:=]\s*["\']?([\w\.-]+)["\']?',
                category=PatternCategory.CRITICAL_SECRETS,
                confidence=0.95,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=108,
            ),
            PatternDefinition(
                name="secret",
                regex=r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s]+)["\']?',
                category=PatternCategory.CRITICAL_SECRETS,
                confidence=0.90,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=107,
            ),
            PatternDefinition(
                name="private_key",
                regex=r'-----BEGIN [A-Z ]+PRIVATE KEY-----.*?-----END [A-Z ]+PRIVATE KEY-----',
                category=PatternCategory.CRITICAL_SECRETS,
                confidence=0.999,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=115,
            ),
        ]
        
        # ===== PII (Priority 80-99) =====
        self.patterns[PatternCategory.PII] = [
            PatternDefinition(
                name="email",
                regex=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                category=PatternCategory.PII,
                confidence=0.95,
                strategy=ReplacementStrategy.GENERIC,
                priority=90,
            ),
            PatternDefinition(
                name="phone",
                regex=r'\b\+?1?\d{10,15}\b',
                category=PatternCategory.PII,
                confidence=0.85,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=88,
            ),
            PatternDefinition(
                name="ssn",
                regex=r'\b\d{3}-\d{2}-\d{4}\b',
                category=PatternCategory.PII,
                confidence=0.99,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=95,
            ),
            PatternDefinition(
                name="ip_address",
                regex=r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                category=PatternCategory.PII,
                confidence=0.90,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=85,
            ),
            PatternDefinition(
                name="passport",
                regex=r'\b[A-Z]{1,2}\d{6,9}\b',
                category=PatternCategory.PII,
                confidence=0.75,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=82,
                case_sensitive=True,
            ),
        ]
        
        # ===== PHI (Priority 70-79) =====
        self.patterns[PatternCategory.PHI] = [
            PatternDefinition(
                name="mrn",
                regex=r'\bMRN[:\s]*\d{6,10}\b',
                category=PatternCategory.PHI,
                confidence=0.99,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=78,
                case_sensitive=True,
            ),
            PatternDefinition(
                name="icd10",
                regex=r'\b[A-Z]\d{2}(?:\.\d{1,3})?\b',
                category=PatternCategory.PHI,
                confidence=0.85,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=75,
                case_sensitive=True,
            ),
        ]
        
        # ===== PCI (Priority 60-69) =====
        self.patterns[PatternCategory.PCI] = [
            PatternDefinition(
                name="credit_card",
                regex=r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
                category=PatternCategory.PCI,
                confidence=0.90,
                strategy=ReplacementStrategy.PARTIAL,
                priority=68,
            ),
            PatternDefinition(
                name="cvv",
                regex=r'\bCVV[:\s]*\d{3,4}\b',
                category=PatternCategory.PCI,
                confidence=0.99,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=67,
                case_sensitive=True,
            ),
        ]
        
        # ===== PATHS (Priority 50-59) =====
        self.patterns[PatternCategory.PATHS] = [
            PatternDefinition(
                name="unix_path",
                regex=r'/(?:[^/\s]+/)+[^/\s]*',
                category=PatternCategory.PATHS,
                confidence=0.80,
                strategy=ReplacementStrategy.GENERIC,
                priority=55,
            ),
            PatternDefinition(
                name="windows_path",
                regex=r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*',
                category=PatternCategory.PATHS,
                confidence=0.85,
                strategy=ReplacementStrategy.GENERIC,
                priority=56,
            ),
        ]
        
        # ===== COMPANY (Priority 40-49) =====
        self.patterns[PatternCategory.COMPANY] = [
            PatternDefinition(
                name="domain",
                regex=r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b',
                category=PatternCategory.COMPANY,
                confidence=0.70,
                strategy=ReplacementStrategy.GENERIC,
                priority=45,
            ),
            PatternDefinition(
                name="internal_ip",
                regex=r'\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.(?:\d{1,3}\.)\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3})\b',
                category=PatternCategory.COMPANY,
                confidence=0.99,
                strategy=ReplacementStrategy.PLACEHOLDER,
                priority=48,
            ),
        ]
        
        # ===== HASHES (Priority 10 - for exclusion) =====
        self.patterns[PatternCategory.HASHES] = [
            PatternDefinition(
                name="hash",
                regex=r'\b[a-f0-9]{32,64}\b',
                category=PatternCategory.HASHES,
                confidence=0.95,
                strategy=ReplacementStrategy.REMOVE,  # Don't sanitize hashes
                priority=10,
            ),
        ]
    
    def get_all_patterns(self, exclude_categories: Optional[List[PatternCategory]] = None) -> List[PatternDefinition]:
        """Get all patterns sorted by priority (highest first)."""
        if exclude_categories is None:
            exclude_categories = [PatternCategory.HASHES]  # Exclude hashes by default
        
        all_patterns = []
        for category, patterns in self.patterns.items():
            if category not in exclude_categories:
                all_patterns.extend(patterns)
        
        return sorted(all_patterns, key=lambda p: p.priority, reverse=True)
    
    def add_custom_pattern(self, pattern: PatternDefinition):
        """Add custom pattern to registry."""
        if pattern.category not in self.patterns:
            self.patterns[pattern.category] = []
        self.patterns[pattern.category].append(pattern)
        self.logger.info(f"Added custom pattern: {pattern.name} (category: {pattern.category.value})")


class SanitizationEngine:
    """
    Core sanitization engine with pattern-based detection.
    
    Features:
    - Priority-based pattern matching
    - Configurable replacement strategies
    - False positive detection (hash exclusion)
    - Performance optimization (compiled regex)
    """
    
    def __init__(self, registry: Optional[PatternRegistry] = None):
        """Initialize engine with pattern registry."""
        self.registry = registry or PatternRegistry()
        self.logger = logging.getLogger(__name__)
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile all regex patterns for performance."""
        for pattern_def in self.registry.get_all_patterns(exclude_categories=[]):
            flags = 0 if pattern_def.case_sensitive else re.IGNORECASE
            try:
                self._compiled_patterns[pattern_def.name] = re.compile(
                    pattern_def.regex, 
                    flags | re.DOTALL
                )
            except re.error as e:
                self.logger.error(f"Failed to compile pattern {pattern_def.name}: {e}")
    
    def detect_all(self, text: str, exclude_hashes: bool = True) -> List[SanitizationMatch]:
        """
        Detect all sensitive patterns in text.
        
        Args:
            text: Text to scan
            exclude_hashes: Skip hash patterns (default: True)
            
        Returns:
            List of matches sorted by priority
        """
        matches = []
        
        # Get patterns to check
        exclude_categories = [PatternCategory.HASHES] if exclude_hashes else []
        patterns = self.registry.get_all_patterns(exclude_categories=exclude_categories)
        
        for pattern_def in patterns:
            compiled = self._compiled_patterns.get(pattern_def.name)
            if not compiled:
                continue
            
            try:
                for match in compiled.finditer(text):
                    matched_text = match.group(0)
                    
                    # Generate suggested replacement
                    suggested = self._generate_replacement(
                        matched_text, 
                        pattern_def.name,
                        pattern_def.strategy
                    )
                    
                    matches.append(SanitizationMatch(
                        category=pattern_def.category,
                        pattern_name=pattern_def.name,
                        matched_text=matched_text,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=pattern_def.confidence,
                        replacement_strategy=pattern_def.strategy,
                        suggested_replacement=suggested,
                    ))
            except Exception as e:
                self.logger.error(f"Error matching pattern {pattern_def.name}: {e}")
        
        return sorted(matches, key=lambda m: m.start_pos)
    
    def _generate_replacement(self, text: str, pattern_name: str, strategy: ReplacementStrategy) -> str:
        """Generate replacement text based on strategy."""
        
        if strategy == ReplacementStrategy.REMOVE:
            return ""
        
        elif strategy == ReplacementStrategy.PLACEHOLDER:
            return f"[REDACTED_{pattern_name.upper()}]"
        
        elif strategy == ReplacementStrategy.HASH:
            import hashlib
            hash_obj = hashlib.sha256(text.encode())
            return hash_obj.hexdigest()[:16]
        
        elif strategy == ReplacementStrategy.PARTIAL:
            # Show last 4 chars for credit cards
            if len(text) > 4:
                return "*" * (len(text) - 4) + text[-4:]
            return "*" * len(text)
        
        elif strategy == ReplacementStrategy.GENERIC:
            # Pattern-specific generic replacements
            if pattern_name == "email":
                return "user@example.com"
            elif pattern_name == "unix_path":
                return "/Users/USER/project/file"
            elif pattern_name == "windows_path":
                return "C:\\Users\\USER\\project\\file"
            elif pattern_name == "domain":
                return "example.com"
            else:
                return f"[GENERIC_{pattern_name.upper()}]"
        
        return f"[REDACTED_{pattern_name.upper()}]"
    
    def sanitize_text(self, text: str) -> Tuple[str, List[SanitizationMatch]]:
        """
        Sanitize text by replacing all sensitive patterns.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Tuple of (sanitized_text, matches_found)
        """
        matches = self.detect_all(text)
        
        if not matches:
            return text, []
        
        # Replace in reverse order to maintain positions
        sanitized = text
        for match in reversed(matches):
            sanitized = (
                sanitized[:match.start_pos] + 
                match.suggested_replacement + 
                sanitized[match.end_pos:]
            )
        
        return sanitized, matches
    
    def sanitize_file(self, file_path: Path) -> Tuple[str, List[SanitizationMatch], bool]:
        """
        Sanitize file contents.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (sanitized_content, matches, success)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sanitized, matches = self.sanitize_text(content)
            return sanitized, matches, True
            
        except UnicodeDecodeError:
            self.logger.warning(f"Binary file skipped: {file_path}")
            return "", [], False
        except Exception as e:
            self.logger.error(f"Error sanitizing {file_path}: {e}")
            return "", [], False
    
    def validate_sanitization(self, text: str, min_confidence: float = 0.8) -> Tuple[bool, List[SanitizationMatch]]:
        """
        Validate that text contains no high-confidence sensitive data.
        
        Args:
            text: Text to validate
            min_confidence: Minimum confidence threshold
            
        Returns:
            Tuple of (is_clean, remaining_matches)
        """
        matches = self.detect_all(text)
        high_confidence_matches = [
            m for m in matches 
            if m.confidence >= min_confidence
        ]
        
        return len(high_confidence_matches) == 0, high_confidence_matches
