"""
ISSUE #5: LLM Output Validation Layer

Comprehensive validation for LLM responses to ensure safety, correctness,
and proper formatting.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity level of validation violations."""
    ERROR = "error"      # Response must be rejected
    WARNING = "warning"  # Response should be reviewed
    INFO = "info"        # Informational, accept anyway


@dataclass
class ValidationViolation:
    """A single validation rule violation."""
    rule: str
    severity: ValidationSeverity
    message: str
    line_number: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of validating LLM output."""
    is_valid: bool
    score: float  # 0-1 confidence score
    violations: List[ValidationViolation]
    sanitized: str
    metadata: Dict[str, Any]


class LLMOutputValidator:
    """Validates LLM responses against safety and format rules."""
    
    # Token count (approximate words)
    DEFAULT_MAX_TOKENS = 4096
    WARNING_TOKEN_THRESHOLD = 3500
    
    # Patterns that indicate harmful content
    HARMFUL_PATTERNS = [
        r"delete\s+\*",
        r"rm\s+-rf",
        r"DROP\s+TABLE",
        r"exec\s*\(",
        r"eval\s*\(",
        r"__import__",
        r"subprocess\s*\.",
    ]
    
    # Patterns that indicate prompt leakage
    LEAKAGE_PATTERNS = [
        r"system\s+prompt",
        r"system\s+message",
        r"your\s+instructions",
        r"original\s+prompt",
        r"<|system|>",
    ]
    
    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS):
        """
        Initialize validator.
        
        Args:
            max_tokens: Maximum allowed tokens in response
        """
        self.max_tokens = max_tokens
    
    def validate(self, output: str) -> ValidationResult:
        """
        Validate LLM output comprehensively.
        
        Args:
            output: LLM response text
        
        Returns:
            ValidationResult with violations and sanitized output
        """
        violations: List[ValidationViolation] = []
        metadata: Dict[str, Any] = {}
        
        # Check 1: JSON formatting
        is_json = self._check_json_format(output)
        metadata["is_json"] = is_json
        
        if not is_json:
            violations.append(ValidationViolation(
                rule="json_format",
                severity=ValidationSeverity.ERROR,
                message="Response is not valid JSON"
            ))
        
        # Check 2: Token limit
        token_count = self._count_tokens(output)
        metadata["token_count"] = token_count
        
        if token_count > self.max_tokens:
            violations.append(ValidationViolation(
                rule="token_limit",
                severity=ValidationSeverity.ERROR,
                message=f"Response exceeds {self.max_tokens} tokens ({token_count} provided)"
            ))
        elif token_count > int(self.max_tokens * 0.9):
            violations.append(ValidationViolation(
                rule="token_limit_warning",
                severity=ValidationSeverity.WARNING,
                message=f"Response approaching token limit ({token_count}/{self.max_tokens})"
            ))
        
        # Check 3: Harmful content
        harmful_match = self._check_harmful_content(output)
        if harmful_match:
            violations.append(ValidationViolation(
                rule="harmful_content",
                severity=ValidationSeverity.ERROR,
                message=f"Detected potentially harmful pattern: {harmful_match}"
            ))
        
        # Check 4: Prompt leakage
        leakage_match = self._check_prompt_leakage(output)
        if leakage_match:
            violations.append(ValidationViolation(
                rule="prompt_leakage",
                severity=ValidationSeverity.ERROR,
                message=f"Detected prompt leakage: {leakage_match}"
            ))
        
        # Check 5: Response structure (if JSON)
        if is_json:
            structure_violations = self._check_json_structure(output)
            violations.extend(structure_violations)
        
        # Check 6: Character encoding
        encoding_ok = self._check_encoding(output)
        metadata["encoding"] = encoding_ok
        if not encoding_ok:
            violations.append(ValidationViolation(
                rule="encoding",
                severity=ValidationSeverity.ERROR,
                message="Response contains invalid character encoding"
            ))
        
        # Compute validity and score
        error_violations = [v for v in violations 
                           if v.severity == ValidationSeverity.ERROR]
        is_valid = len(error_violations) == 0
        
        # Score: 1.0 = perfect, 0.5 = warnings, 0.0 = errors
        if is_valid and not violations:
            score = 1.0
        elif is_valid:
            score = 0.8  # Has warnings but no errors
        else:
            score = 0.0  # Has errors
        
        # Sanitize output
        sanitized = self._sanitize_output(output)
        
        logger.debug(
            f"Output validation: valid={is_valid}, score={score:.2f}, "
            f"violations={len(violations)}"
        )
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            violations=violations,
            sanitized=sanitized,
            metadata=metadata,
        )
    
    def _check_json_format(self, output: str) -> bool:
        """Check if output is valid JSON."""
        try:
            json.loads(output)
            return True
        except json.JSONDecodeError:
            return False
    
    def _count_tokens(self, output: str) -> int:
        """Approximate token count (words + punctuation)."""
        # Simple approximation: split on whitespace and punctuation
        tokens = re.findall(r'\w+|[.,!?;:\'"()[\]{}]', output)
        return len(tokens)
    
    def _check_harmful_content(self, output: str) -> Optional[str]:
        """Check for harmful instructions or patterns."""
        output_lower = output.lower()
        
        for pattern in self.HARMFUL_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                return pattern
        
        return None
    
    def _check_prompt_leakage(self, output: str) -> Optional[str]:
        """Check if system prompt is leaking through."""
        output_lower = output.lower()
        
        for pattern in self.LEAKAGE_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                return pattern
        
        return None
    
    def _check_json_structure(self, output: str) -> List[ValidationViolation]:
        """Check JSON structure for expected fields."""
        violations: List[ValidationViolation] = []
        
        try:
            data = json.loads(output)
            
            # Expected fields for typical LLM responses
            expected_fields = ["response", "status"]
            
            # At least one expected field should exist
            has_expected_field = any(field in data for field in expected_fields)
            
            if not has_expected_field:
                violations.append(ValidationViolation(
                    rule="json_structure",
                    severity=ValidationSeverity.WARNING,
                    message=f"Missing expected fields: {expected_fields}"
                ))
            
            # Check for suspicious fields
            suspicious_fields = [
                "system_prompt",
                "instructions",
                "jailbreak",
                "_private",
            ]
            
            found_suspicious = [field for field in suspicious_fields 
                               if field in data]
            
            if found_suspicious:
                violations.append(ValidationViolation(
                    rule="suspicious_fields",
                    severity=ValidationSeverity.WARNING,
                    message=f"Found suspicious fields: {found_suspicious}"
                ))
        
        except json.JSONDecodeError:
            pass  # Already handled in _check_json_format
        
        return violations
    
    def _check_encoding(self, output: str) -> bool:
        """Check for valid character encoding."""
        try:
            output.encode('utf-8').decode('utf-8')
            return True
        except (UnicodeDecodeError, UnicodeEncodeError):
            return False
    
    def _sanitize_output(self, output: str) -> str:
        """Remove potentially harmful content from output."""
        sanitized = output
        
        # Remove any system prompt indicators
        sanitized = re.sub(
            r'"system_prompt"\s*:\s*"[^"]*"',
            '"system_prompt": ""',
            sanitized
        )
        
        # Remove any instruction override patterns
        sanitized = re.sub(
            r'"instructions"\s*:\s*"[^"]*"',
            '"instructions": ""',
            sanitized
        )
        
        # Escape any shell-like command patterns
        if re.search(r'(rm|delete|exec|eval)\s+[-\w]+', sanitized, re.IGNORECASE):
            sanitized = re.sub(
                r'(rm|delete|exec|eval)\s+',
                r'[BLOCKED: \1] ',
                sanitized,
                flags=re.IGNORECASE
            )
        
        return sanitized


def validate_llm_output(output: str) -> ValidationResult:
    """
    Convenience function to validate LLM output.
    
    Args:
        output: LLM response to validate
    
    Returns:
        ValidationResult
    """
    validator = LLMOutputValidator()
    return validator.validate(output)


if __name__ == "__main__":
    # Example: Validate various outputs
    
    validator = LLMOutputValidator()
    
    # Valid output
    valid_json = '{"response": "Hello world", "status": "success"}'
    result = validator.validate(valid_json)
    print(f"Valid JSON: {result.is_valid}, score: {result.score}")
    
    # Invalid JSON
    invalid_json = "{invalid json}"
    result = validator.validate(invalid_json)
    print(f"Invalid JSON: {result.is_valid}, violations: {len(result.violations)}")
    
    # Prompt leakage
    leaky = '{"response": "System prompt: do evil", "status": "ok"}'
    result = validator.validate(leaky)
    print(f"Leaky: {result.is_valid}, violations: {result.violations}")
