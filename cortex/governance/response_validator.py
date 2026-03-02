"""
CORE-002 Response Validation Module

Enforces inline-only responses across all CORTEX components.
Prevents markdown/text file generation in responses.

Authority: CORE-002-RESPONSE.yaml
Phase: CORTEX Inline-First Architecture
"""

import re
from typing import Dict, List, Tuple


class ResponseValidator:
    """
    Validates responses for CORE-002 compliance.

    Ensures no markdown/text file creation suggestions in responses.
    """

    # Forbidden patterns that suggest file creation
    FORBIDDEN_PATTERNS = [
        (r"cat\s*>\s*[^\s]+\.(md|txt)", "Shell redirection to file"),
        (r"cat\s*>>\s*[^\s]+\.(md|txt)", "Shell append to file"),
        (r"echo\s+.+>\s*[^\s]+\.(md|txt)", "Echo to file"),
        (r"printf\s+.+>\s*[^\s]+\.(md|txt)", "Printf to file"),
        (r"create_file\s*\(\s*['\"][^'\"]*\.(md|txt)['\"]", "create_file() for reports"),
        (r"(?:create|write|generate)\s+.*\.(md|txt).*file", "File creation suggestion"),
        (r"(?:create|write)\s+.*\.(md|txt)", "File creation reference"),
        (r"generate.*(?:markdown|text).*report", "Report generation"),
        (r"(?:create|write|generate)\s+.*?(?:report|summary|analysis)", "Report/summary generation"),
        (r"save\s+.*as\s+.*\.(md|txt)", "Save as file"),
        (r"write\s+.*to\s+.*\.(md|txt)", "Write to file"),
        (r"output\s+.*to\s+.*\.(md|txt)", "Output to file"),
        (r"Created\s+\[.*\]\(file:///.*\.(md|txt)\)", "File creation confirmation"),
    ]

    # Allowed contexts (exceptions to CORE-002)
    ALLOWED_CONTEXTS = [
        ".github/prompts/",
        ".github/agents/",
        "README.md",
    ]

    @classmethod
    def validate(cls: object, response_text: str) -> Tuple[bool, List[str]]:
        """
        Validate response for CORE-002 compliance.

        Args:
            response_text: Response to validate

        Returns:
            Tuple of (is_valid, violations)
            - is_valid: True if no violations found
            - violations: List of violation descriptions
        """
        violations = []

        for pattern, description in cls.FORBIDDEN_PATTERNS:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)

            for match in matches:
                matched_text = match.group(0)

                # Check if match is in allowed context
                is_allowed = any(
                    ctx in matched_text for ctx in cls.ALLOWED_CONTEXTS
                )

                if not is_allowed:
                    violations.append(
                        f"CORE-002 VIOLATION ({description}): '{matched_text}'"
                    )

        return (len(violations) == 0, violations)

    @classmethod
    def transform_to_inline(cls: object, response_text: str) -> str:
        """
        Transform response to use inline display instead of file creation.

        Args:
            response_text: Original response

        Returns:
            Transformed response with inline suggestions
        """
        transformed = response_text

        # Transform create_file suggestions
        transformed = re.sub(
            r"create_file\s*\(\s*['\"]([^'\"]*\.(md|txt))['\"]",
            r"Display inline in chat (CORE-002: no file creation)",
            transformed,
            flags=re.IGNORECASE
        )

        # Transform "cat >" patterns
        transformed = re.sub(
            r"cat\s*>\s*([^\s]+\.(md|txt))",
            r"Display inline in chat instead of file output",
            transformed,
            flags=re.IGNORECASE
        )

        # Transform "save as" patterns
        transformed = re.sub(
            r"save\s+.*as\s+.*\.(md|txt)",
            r"Display inline; user can save chat transcript if needed",
            transformed,
            flags=re.IGNORECASE
        )

        # Transform "generate report" patterns
        transformed = re.sub(
            r"(?:generate|create|write)\s+(?:comprehensive\s+)?(?:markdown\s+)?(?:report|summary|analysis)",
            r"Display findings as inline markdown table",
            transformed,
            flags=re.IGNORECASE
        )

        # Transform general file references (e.g., "create report.md")
        transformed = re.sub(
            r"(?:create|write)\s+([^\s]+\.(md|txt))",
            r"Display inline (CORE-002: no \1 file)",
            transformed,
            flags=re.IGNORECASE
        )

        # Transform "Created [file]" confirmations
        transformed = re.sub(
            r"Created\s+\[.*\]\(file:///.*\.(md|txt)\)",
            r"Displayed results inline (CORE-002 compliance)",
            transformed,
            flags=re.IGNORECASE
        )

        return transformed

    @classmethod
    def enforce(cls: object, response_text: str, auto_transform: bool = True) -> Dict[str, any]:
        """
        Enforce CORE-002 compliance on response.

        Args:
            response_text: Response to check
            auto_transform: If True, auto-transform violations to inline

        Returns:
            Dict with:
            - compliant: bool
            - violations: List[str]
            - transformed_text: str (if auto_transform=True)
            - action: str (description of action taken)
        """
        is_valid, violations = cls.validate(response_text)

        if is_valid:
            return {
                "compliant": True,
                "violations": [],
                "transformed_text": response_text,
                "action": "No violations detected",
            }

        if auto_transform:
            transformed = cls.transform_to_inline(response_text)
            return {
                "compliant": False,
                "violations": violations,
                "transformed_text": transformed,
                "action": f"Auto-transformed {len(violations)} violations to inline display",
            }

        return {
            "compliant": False,
            "violations": violations,
            "transformed_text": response_text,
            "action": "Violations detected, no transformation applied",
        }


def validate_response(response_text: str) -> Tuple[bool, List[str]]:
    """
    Convenience function for response validation.

    Args:
        response_text: Response to validate

    Returns:
        Tuple of (is_valid, violations)
    """
    return ResponseValidator.validate(response_text)


def transform_response(response_text: str) -> str:
    """
    Convenience function for response transformation.

    Args:
        response_text: Response to transform

    Returns:
        Transformed response with inline suggestions
    """
    return ResponseValidator.transform_to_inline(response_text)


__all__ = ["ResponseValidator", "validate_response", "transform_response"]
