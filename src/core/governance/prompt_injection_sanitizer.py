"""
CORE-032: Prompt Injection Prevention & Input Sanitization

Prevents prompt injection attacks through:
- Input pattern detection and filtering
- Malicious payload identification
- Safe parameter binding
- Output encoding and escaping
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Any
import re


class InjectionThreatLevel(Enum):
    """Threat level of detected injection."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SanitizationMethod(Enum):
    """Method used for sanitization."""
    STRIP = "strip"
    ESCAPE = "escape"
    PARAMETERIZE = "parameterize"
    BLOCK = "block"
    ENCODE = "encode"


@dataclass
class InjectionPattern:
    """Pattern for detecting injection attempts."""
    pattern: str  # Regex pattern
    threat_level: InjectionThreatLevel
    description: str
    detection_count: int = 0


@dataclass
class SanitizationResult:
    """Result of input sanitization."""
    original_input: str
    sanitized_input: str
    threats_detected: List[str] = field(default_factory=list)
    threat_level: InjectionThreatLevel = InjectionThreatLevel.SAFE
    methods_applied: List[SanitizationMethod] = field(default_factory=list)
    is_safe: bool = True
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Result:
    """Generic result type for error handling."""
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: Any) -> Result:
        """Create successful result."""
        return cls(success=True, value=value)
    
    @classmethod
    def error(cls, error: str) -> Result:
        """Create error result."""
        return cls(success=False, error=error)


class PromptInjectionSanitizer:
    """Prevents prompt injection attacks through input sanitization."""
    
    # Common injection patterns
    DEFAULT_PATTERNS = [
        InjectionPattern(
            pattern=r"(ignore|forget|override|bypass).*(instruction|prompt|rule|constraint)",
            threat_level=InjectionThreatLevel.CRITICAL,
            description="Instruction override attempt"
        ),
        InjectionPattern(
            pattern=r"(\$\{.*?\}|`.*?`|\{\{.*?\}\})",
            threat_level=InjectionThreatLevel.HIGH,
            description="Template injection pattern"
        ),
        InjectionPattern(
            pattern=r"(system\s*:|system\s*=|<system>|[Ss]ystem\s*[Pp]rompt)",
            threat_level=InjectionThreatLevel.CRITICAL,
            description="System prompt manipulation"
        ),
        InjectionPattern(
            pattern=r"(sql\s+injection|'; DROP|exec\(|eval\()",
            threat_level=InjectionThreatLevel.HIGH,
            description="SQL/code injection pattern"
        ),
        InjectionPattern(
            pattern=r"(<script|javascript:|onerror=|onclick=)",
            threat_level=InjectionThreatLevel.HIGH,
            description="XSS injection pattern"
        ),
        InjectionPattern(
            pattern=r"(\.\.\\/|\.\.\\|%2e%2e)",
            threat_level=InjectionThreatLevel.MEDIUM,
            description="Path traversal pattern"
        ),
    ]
    
    def __init__(self):
        """Initialize the sanitizer with default patterns."""
        self.injection_patterns: List[InjectionPattern] = self.DEFAULT_PATTERNS.copy()
        self.sanitization_history: List[SanitizationResult] = []
        self.blocked_inputs: List[str] = []
    
    def add_pattern(
        self,
        pattern: str,
        threat_level: InjectionThreatLevel,
        description: str
    ) -> None:
        """
        Add a custom injection pattern.
        
        Args:
            pattern: Regex pattern to detect.
            threat_level: Threat level of this pattern.
            description: Description of the threat.
        """
        self.injection_patterns.append(
            InjectionPattern(
                pattern=pattern,
                threat_level=threat_level,
                description=description
            )
        )
    
    def sanitize(self, user_input: str) -> Result:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            user_input: Raw user input to sanitize.
            
        Returns:
            Result with SanitizationResult or error.
        """
        try:
            if not user_input:
                return Result.ok(SanitizationResult(
                    original_input="",
                    sanitized_input="",
                    is_safe=True
                ))
            
            # Detect threats
            threats, max_threat_level = self._detect_threats(user_input)
            
            # Determine if input should be blocked
            if max_threat_level == InjectionThreatLevel.CRITICAL:
                self.blocked_inputs.append(user_input)
                return Result.error(f"Input blocked due to {max_threat_level.value} threat")
            
            # Sanitize based on threat level
            sanitized = self._apply_sanitization(user_input, max_threat_level)
            methods = self._get_sanitization_methods(max_threat_level)
            
            result = SanitizationResult(
                original_input=user_input,
                sanitized_input=sanitized,
                threats_detected=threats,
                threat_level=max_threat_level,
                methods_applied=methods,
                is_safe=max_threat_level in (InjectionThreatLevel.SAFE, InjectionThreatLevel.LOW)
            )
            
            self.sanitization_history.append(result)
            return Result.ok(result)
            
        except Exception as e:
            return Result.error(f"Sanitization failed: {str(e)}")
    
    def _detect_threats(self, user_input: str) -> tuple:
        """
        Detect injection threats in user input.
        
        Args:
            user_input: Input to analyze.
            
        Returns:
            Tuple of (threat_list, max_threat_level).
        """
        threats = []
        max_threat_level = InjectionThreatLevel.SAFE
        
        for pattern_obj in self.injection_patterns:
            try:
                if re.search(pattern_obj.pattern, user_input, re.IGNORECASE):
                    threats.append(pattern_obj.description)
                    pattern_obj.detection_count += 1
                    
                    # Track highest threat level
                    threat_values = {
                        InjectionThreatLevel.SAFE: 0,
                        InjectionThreatLevel.LOW: 1,
                        InjectionThreatLevel.MEDIUM: 2,
                        InjectionThreatLevel.HIGH: 3,
                        InjectionThreatLevel.CRITICAL: 4,
                    }
                    
                    if threat_values[pattern_obj.threat_level] > threat_values[max_threat_level]:
                        max_threat_level = pattern_obj.threat_level
            except re.error:
                # Invalid regex pattern - skip
                pass
        
        return threats, max_threat_level
    
    def _apply_sanitization(
        self,
        user_input: str,
        threat_level: InjectionThreatLevel
    ) -> str:
        """
        Apply appropriate sanitization based on threat level.
        
        Args:
            user_input: Input to sanitize.
            threat_level: Detected threat level.
            
        Returns:
            Sanitized input string.
        """
        sanitized = user_input
        
        # Strip suspicious characters
        if threat_level in (InjectionThreatLevel.MEDIUM, InjectionThreatLevel.HIGH):
            sanitized = self._strip_suspicious_chars(sanitized)
        
        # Escape special characters
        if threat_level == InjectionThreatLevel.HIGH:
            sanitized = self._escape_special_chars(sanitized)
        
        # Encode for safety
        if threat_level == InjectionThreatLevel.CRITICAL:
            sanitized = self._encode_safe(sanitized)
        
        return sanitized
    
    def _strip_suspicious_chars(self, text: str) -> str:
        """
        Remove suspicious characters.
        
        Args:
            text: Text to clean.
            
        Returns:
            Cleaned text.
        """
        # Remove template injection markers
        text = re.sub(r'[\$`\{\}]', '', text)
        # Remove command separators
        text = re.sub(r'[;&|]', '', text)
        return text.strip()
    
    def _escape_special_chars(self, text: str) -> str:
        """
        Escape special characters.
        
        Args:
            text: Text to escape.
            
        Returns:
            Escaped text.
        """
        escape_map = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
            '&': '&amp;',
        }
        
        for char, escape in escape_map.items():
            text = text.replace(char, escape)
        
        return text
    
    def _encode_safe(self, text: str) -> str:
        """
        Encode text for safety.
        
        Args:
            text: Text to encode.
            
        Returns:
            Encoded text.
        """
        # Use URL encoding for maximum safety
        import urllib.parse
        return urllib.parse.quote(text, safe='')
    
    def _get_sanitization_methods(
        self,
        threat_level: InjectionThreatLevel
    ) -> List[SanitizationMethod]:
        """
        Determine which sanitization methods to apply.
        
        Args:
            threat_level: Detected threat level.
            
        Returns:
            List of sanitization methods.
        """
        if threat_level == InjectionThreatLevel.SAFE:
            return [SanitizationMethod.STRIP]
        elif threat_level == InjectionThreatLevel.LOW:
            return [SanitizationMethod.STRIP]
        elif threat_level == InjectionThreatLevel.MEDIUM:
            return [SanitizationMethod.STRIP, SanitizationMethod.ESCAPE]
        elif threat_level == InjectionThreatLevel.HIGH:
            return [SanitizationMethod.STRIP, SanitizationMethod.ESCAPE, SanitizationMethod.ENCODE]
        else:  # CRITICAL
            return [SanitizationMethod.BLOCK]
    
    def validate_parameter_binding(
        self,
        template: str,
        params: Dict[str, str]
    ) -> Result:
        """
        Validate safe parameter binding.
        
        Args:
            template: Template string with placeholders.
            params: Parameter dictionary.
            
        Returns:
            Result with validation outcome.
        """
        try:
            # Check for injection in parameter values
            for key, value in params.items():
                result = self.sanitize(value)
                if not result.success:
                    return Result.error(f"Parameter '{key}' contains injection: {result.error}")
            
            # Perform safe substitution
            bound = template
            for key, value in params.items():
                placeholder = "{" + key + "}"
                bound = bound.replace(placeholder, value)
            
            return Result.ok(bound)
            
        except Exception as e:
            return Result.error(f"Parameter binding failed: {str(e)}")
    
    def get_threat_statistics(self) -> Dict[str, Any]:
        """
        Get statistics on detected threats.
        
        Returns:
            Dictionary with threat statistics.
        """
        if not self.sanitization_history:
            return {
                "total_sanitizations": 0,
                "safe_inputs": 0,
                "blocked_inputs": len(self.blocked_inputs),
                "threat_distribution": {},
            }
        
        threat_counts = {}
        safe_count = 0
        
        for result in self.sanitization_history:
            if result.is_safe:
                safe_count += 1
            threat = result.threat_level.value
            threat_counts[threat] = threat_counts.get(threat, 0) + 1
        
        return {
            "total_sanitizations": len(self.sanitization_history),
            "safe_inputs": safe_count,
            "unsafe_inputs": len(self.sanitization_history) - safe_count,
            "blocked_inputs": len(self.blocked_inputs),
            "threat_distribution": threat_counts,
        }
