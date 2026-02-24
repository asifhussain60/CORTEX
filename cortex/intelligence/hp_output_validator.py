"""
Output Validation and Sanitization for LLM Responses.

CORE-CRIT-HALL-001: Validates and sanitizes all LLM-generated output
before downstream processing to prevent injection attacks and hallucinations.

Author: CORTEX Framework
"""

import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import ValidationLevel


class OutputValidationError(Exception):
    """Raised when output validation fails."""
    pass


class LLMOutputValidator:
    """Validates and sanitizes LLM-generated output.

    Implements CORE-CRIT-HALL-001: All LLM output must be validated before
    downstream processing to prevent:
    - Code injection attacks
    - SQL injection attacks
    - Prompt injection attacks
    - Malformed data propagation
    """

    def __init__(self, level: ValidationLevel = ValidationLevel.STRICT) -> None:
        """Initialize validator.

        Args:
            level: Validation severity level
        """
        self.level = level

        # Dangerous patterns to detect
        self.dangerous_patterns = {
            "sql_injection": [
                r"(?i)(union|select|insert|update|delete|drop|create)\s+(from|into|table|database)",
                r"(?i)(;|'|\")\s*(union|select|insert|update|delete)",
            ],
            "code_injection": [
                r"__.*__",  # Python dunder methods
                r"import\s+\w+",  # Import statements
                r"exec\s*\(",  # exec() function
                r"eval\s*\(",  # eval() function
                r"subprocess\.",  # subprocess module
                r"os\.(system|popen)",  # OS system calls
            ],
            "xml_injection": [
                r"<!\[CDATA\[",
                r"<!ENTITY",
                r"<!DOCTYPE",
            ],
            "prompt_injection": [
                r"(?i)(ignore|forget|disregard)\s+(previous|prior|instructions|rules)",
                r"(?i)(system\s+)?prompt",
                r"(?i)(hidden|secret)\s+instruction",
            ],
        }

    def validate(
        self,
        output: Any,
        schema: Optional[Dict[str, Any]] = None,
        allow_dangerous: bool = False,
    ) -> Any:
        """Validate LLM output.

        Args:
            output: LLM output to validate
            schema: Expected output schema (optional)
            allow_dangerous: If True, only log dangerous patterns (don't block)

        Returns:
            Validated output

        Raises:
            OutputValidationError: If validation fails in STRICT mode
        """
        # Check for None
        if output is None:
            raise OutputValidationError("LLM output is None")

        # Validate type if schema provided
        if schema:
            self._validate_schema(output, schema)

        # Check for dangerous content
        dangerous_found = self._check_dangerous_patterns(str(output))
        if dangerous_found:
            message = f"Dangerous pattern detected in LLM output: {dangerous_found}"
            if self.level == ValidationLevel.STRICT and not allow_dangerous:
                raise OutputValidationError(message)
            elif self.level == ValidationLevel.NORMAL:
                import logging
                logging.warning(f"CORE-CRIT-HALL-001: {message}")

        # Validate JSON if output is JSON string
        if isinstance(output, str) and output.strip().startswith("{"):
            try:
                json.loads(output)
            except json.JSONDecodeError as e:
                raise OutputValidationError(f"Invalid JSON in LLM output: {e}")

        return output

    def validate_list(
        self,
        outputs: List[Any],
        schema: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """Validate list of outputs.

        Args:
            outputs: List of outputs to validate
            schema: Expected schema for each item

        Returns:
            Validated outputs
        """
        return [self.validate(item, schema) for item in outputs]

    def sanitize(self, output: str) -> str:
        """Sanitize LLM output by removing dangerous patterns.

        Args:
            output: Output to sanitize

        Returns:
            Sanitized output
        """
        sanitized = output

        # Remove SQL injection patterns
        for pattern in self.dangerous_patterns["sql_injection"]:
            sanitized = re.sub(pattern, "[SANITIZED]", sanitized, flags=re.IGNORECASE)

        # Remove code injection patterns
        for pattern in self.dangerous_patterns["code_injection"]:
            sanitized = re.sub(pattern, "[SANITIZED]", sanitized, flags=re.IGNORECASE)

        # Remove XML injection patterns
        for pattern in self.dangerous_patterns["xml_injection"]:
            sanitized = re.sub(pattern, "[SANITIZED]", sanitized)

        # Remove prompt injection patterns
        for pattern in self.dangerous_patterns["prompt_injection"]:
            sanitized = re.sub(pattern, "[SANITIZED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    def _validate_schema(
        self,
        output: Any,
        schema: Dict[str, Any],
    ) -> None:
        """Validate output against schema.

        Args:
            output: Output to validate
            schema: Expected schema

        Raises:
            OutputValidationError: If schema validation fails
        """
        # Schema is always a dict by type annotation
        if not isinstance(output, dict):
            raise OutputValidationError(
                f"Expected dict output, got {type(output).__name__}"
            )

        # Check required keys
        required_keys = schema.get("required_keys", [])
        for key in required_keys:
            if key not in output:
                raise OutputValidationError(f"Missing required key: {key}")

    def _check_dangerous_patterns(self, content: str) -> Optional[str]:
        """Check for dangerous patterns in content.

        Args:
            content: Content to check

        Returns:
            Name of dangerous pattern found, or None
        """
        for category, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return f"{category}: {pattern}"
        return None


# Singleton instance for global use
_global_validator: Optional[LLMOutputValidator] = None


def get_validator(level: ValidationLevel = ValidationLevel.STRICT) -> LLMOutputValidator:
    """Get global output validator instance.

    Args:
        level: Validation level

    Returns:
        LLMOutputValidator instance
    """
    global _global_validator
    if _global_validator is None or _global_validator.level != level:
        _global_validator = LLMOutputValidator(level)
    return _global_validator


def validate_llm_output(
    output: Any,
    schema: Optional[Dict[str, Any]] = None,
    allow_dangerous: bool = False,
) -> Any:
    """Validate LLM output using global validator.

    Args:
        output: Output to validate
        schema: Expected schema
        allow_dangerous: If True, only log dangerous patterns

    Returns:
        Validated output
    """
    return get_validator().validate(output, schema, allow_dangerous)


def sanitize_llm_output(output: str) -> str:
    """Sanitize LLM output.

    Args:
        output: Output to sanitize

    Returns:
        Sanitized output
    """
    return get_validator().sanitize(output)
