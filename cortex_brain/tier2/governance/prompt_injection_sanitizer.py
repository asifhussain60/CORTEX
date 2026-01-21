"""Tier2 Governance: Prompt Injection Sanitizer

Implements CORE-032: Prompt Injection Prevention & Input Sanitization.
Detects and sanitizes malicious prompt injection attempts.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import html
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class InjectionThreatLevel(Enum):
    """Injection threat levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SanitizationMethod(Enum):
    """Sanitization method types."""
    STRIP = "strip"
    ESCAPE = "escape"
    ENCODE = "encode"
    BLOCK = "block"


@dataclass
class InjectionPattern:
    """Injection attack pattern."""
    pattern: str
    threat_level: InjectionThreatLevel
    description: str
    pattern_type: str = "regex"


@dataclass
class SanitizationResult:
    """Sanitization result."""
    original_input: str
    sanitized_input: str
    threats_detected: List[str]
    is_safe: bool
    threat_level: InjectionThreatLevel = InjectionThreatLevel.SAFE
    methods_applied: List[SanitizationMethod] = field(default_factory=list)


@dataclass
class Result:
    """Generic result wrapper."""
    success: bool
    value: Any = None
    error: Optional[str] = None


class PromptInjectionSanitizer:
    """Sanitize prompt injections.
    
    Detects various injection attack patterns including:
    - System prompt manipulation
    - SQL injection
    - XSS injection
    - Template injection
    - Path traversal
    - Instruction override attempts
    """
    
    def __init__(self):
        """Initialize the sanitizer with default patterns."""
        self.injection_patterns: List[InjectionPattern] = []
        self.sanitization_history: List[SanitizationResult] = []
        self.blocked_inputs: List[str] = []
        
        self._initialize_patterns()
    
    def _initialize_patterns(self) -> None:
        """Initialize default injection patterns."""
        patterns = [
            # Critical - System/instruction override
            InjectionPattern(
                pattern=r"(?i)(ignore|disregard|forget|override).*(instruction|prompt|rule|constraint|guideline)",
                threat_level=InjectionThreatLevel.CRITICAL,
                description="System instruction override attempt",
                pattern_type="regex"
            ),
            InjectionPattern(
                pattern=r"(?i)(bypass|evade|circumvent).*(safety|security|filter|protection|rule)",
                threat_level=InjectionThreatLevel.CRITICAL,
                description="Security bypass attempt",
                pattern_type="regex"
            ),
            InjectionPattern(
                pattern=r"(?i)system\s*prompt\s*:",
                threat_level=InjectionThreatLevel.CRITICAL,
                description="System prompt manipulation",
                pattern_type="regex"
            ),
            
            # High - SQL Injection
            InjectionPattern(
                pattern=r"(?i)(;|')\s*(drop|delete|truncate|alter)\s+(table|database)",
                threat_level=InjectionThreatLevel.HIGH,
                description="SQL injection attempt",
                pattern_type="regex"
            ),
            InjectionPattern(
                pattern=r"(?i)(union|select|insert|update).*from",
                threat_level=InjectionThreatLevel.HIGH,
                description="SQL query injection",
                pattern_type="regex"
            ),
            
            # High - XSS
            InjectionPattern(
                pattern=r"<script[^>]*>.*?</script>",
                threat_level=InjectionThreatLevel.HIGH,
                description="XSS script injection",
                pattern_type="regex"
            ),
            InjectionPattern(
                pattern=r"javascript:",
                threat_level=InjectionThreatLevel.HIGH,
                description="JavaScript protocol injection",
                pattern_type="regex"
            ),
            
            # Medium - Template injection
            InjectionPattern(
                pattern=r"\$\{[^}]+\}",
                threat_level=InjectionThreatLevel.MEDIUM,
                description="Template variable injection",
                pattern_type="regex"
            ),
            InjectionPattern(
                pattern=r"\{\{[^}]+\}\}",
                threat_level=InjectionThreatLevel.MEDIUM,
                description="Template expression injection",
                pattern_type="regex"
            ),
            
            # Medium - Path traversal
            InjectionPattern(
                pattern=r"\.\./",
                threat_level=InjectionThreatLevel.MEDIUM,
                description="Path traversal attempt",
                pattern_type="regex"
            ),
        ]
        
        self.injection_patterns.extend(patterns)
    
    def add_pattern(
        self,
        pattern: str,
        threat_level: InjectionThreatLevel,
        description: str
    ) -> None:
        """Add a custom injection pattern.
        
        Args:
            pattern: Regex pattern to detect
            threat_level: Threat level for this pattern
            description: Description of the threat
        """
        self.injection_patterns.append(
            InjectionPattern(
                pattern=pattern,
                threat_level=threat_level,
                description=description
            )
        )
    
    def _detect_threats(self, input_text: str) -> Tuple[List[str], InjectionThreatLevel]:
        """Detect threats in input text.
        
        Args:
            input_text: Text to analyze
            
        Returns:
            Tuple of (detected threats, overall threat level)
        """
        detected_threats = []
        max_threat_level = InjectionThreatLevel.SAFE
        
        for pattern_obj in self.injection_patterns:
            if re.search(pattern_obj.pattern, input_text, re.IGNORECASE):
                detected_threats.append(pattern_obj.description)
                
                # Update max threat level
                threat_levels = [
                    InjectionThreatLevel.SAFE,
                    InjectionThreatLevel.LOW,
                    InjectionThreatLevel.MEDIUM,
                    InjectionThreatLevel.HIGH,
                    InjectionThreatLevel.CRITICAL
                ]
                if threat_levels.index(pattern_obj.threat_level) > threat_levels.index(max_threat_level):
                    max_threat_level = pattern_obj.threat_level
        
        return detected_threats, max_threat_level
    
    def sanitize(self, input_text: str) -> Result:
        """Sanitize input text.
        
        Args:
            input_text: Text to sanitize
            
        Returns:
            Result with SanitizationResult
        """
        # Detect threats
        threats, threat_level = self._detect_threats(input_text)
        
        # Apply sanitization based on threat level
        sanitized = self._apply_sanitization(input_text, threat_level)
        
        # Determine if safe
        is_safe = threat_level in [InjectionThreatLevel.SAFE, InjectionThreatLevel.LOW]
        
        # Get sanitization methods
        methods = self._get_sanitization_methods(threat_level)
        
        result = SanitizationResult(
            original_input=input_text,
            sanitized_input=sanitized,
            threats_detected=threats,
            is_safe=is_safe,
            threat_level=threat_level,
            methods_applied=methods
        )
        
        # Track in history
        self.sanitization_history.append(result)
        
        # Track blocked inputs
        if threat_level == InjectionThreatLevel.CRITICAL:
            self.blocked_inputs.append(input_text)
            return Result(success=False, error="Critical threat detected - input blocked")
        
        return Result(success=True, value=result)
    
    def _apply_sanitization(
        self,
        input_text: str,
        threat_level: InjectionThreatLevel
    ) -> str:
        """Apply sanitization based on threat level.
        
        Args:
            input_text: Text to sanitize
            threat_level: Threat level
            
        Returns:
            Sanitized text
        """
        if threat_level == InjectionThreatLevel.SAFE:
            return input_text
        
        sanitized = input_text
        
        # Apply stripping for all non-safe levels
        sanitized = self._strip_suspicious_chars(sanitized)
        
        # Apply escaping for high threat
        if threat_level in [InjectionThreatLevel.HIGH, InjectionThreatLevel.CRITICAL]:
            sanitized = self._escape_special_chars(sanitized)
        
        return sanitized
    
    def _escape_special_chars(self, text: str) -> str:
        """Escape special HTML characters.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        return html.escape(text)
    
    def _strip_suspicious_chars(self, text: str) -> str:
        """Strip suspicious characters.
        
        Args:
            text: Text to strip
            
        Returns:
            Stripped text
        """
        # Remove template markers
        text = re.sub(r'[$`{}]', '', text)
        
        # Remove command separators
        text = re.sub(r'[;|]', '', text)
        
        return text
    
    def _encode_safe(self, text: str) -> str:
        """Encode text safely.
        
        Args:
            text: Text to encode
            
        Returns:
            Encoded text
        """
        return text.encode('utf-8', errors='ignore').decode('utf-8')
    
    def _get_sanitization_methods(
        self,
        threat_level: InjectionThreatLevel
    ) -> List[SanitizationMethod]:
        """Get sanitization methods for threat level.
        
        Args:
            threat_level: Threat level
            
        Returns:
            List of sanitization methods
        """
        methods = []
        
        if threat_level == InjectionThreatLevel.SAFE:
            methods.append(SanitizationMethod.STRIP)
        elif threat_level == InjectionThreatLevel.LOW:
            methods.extend([SanitizationMethod.STRIP])
        elif threat_level == InjectionThreatLevel.MEDIUM:
            methods.extend([SanitizationMethod.STRIP, SanitizationMethod.ENCODE])
        elif threat_level == InjectionThreatLevel.HIGH:
            methods.extend([SanitizationMethod.STRIP, SanitizationMethod.ESCAPE])
        elif threat_level == InjectionThreatLevel.CRITICAL:
            methods.append(SanitizationMethod.BLOCK)
        
        return methods
    
    def validate_parameter_binding(
        self,
        template: str,
        parameters: Dict[str, str]
    ) -> Result:
        """Validate parameter binding.
        
        Args:
            template: Template string
            parameters: Parameters to bind
            
        Returns:
            Result with bound string or error
        """
        # Check each parameter for injection attempts
        for key, value in parameters.items():
            threats, threat_level = self._detect_threats(value)
            if threat_level in [InjectionThreatLevel.HIGH, InjectionThreatLevel.CRITICAL]:
                return Result(success=False, error=f"Injection detected in parameter: {key}")
        
        # Safe binding
        try:
            result = template.format(**parameters)
            return Result(success=True, value=result)
        except Exception as e:
            return Result(success=False, error=str(e))
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.sanitization_history:
            return {
                "total_sanitizations": 0,
                "safe_inputs": 0,
                "blocked_inputs": 0
            }
        
        safe_count = sum(1 for r in self.sanitization_history if r.is_safe)
        
        return {
            "total_sanitizations": len(self.sanitization_history),
            "safe_inputs": safe_count,
            "unsafe_inputs": len(self.sanitization_history) - safe_count,
            "blocked_inputs": len(self.blocked_inputs)
        }


__all__ = [
    "InjectionThreatLevel",
    "SanitizationResult",
    "PromptInjectionSanitizer",
    "SanitizationMethod",
    "InjectionPattern",
    "Result"
]
