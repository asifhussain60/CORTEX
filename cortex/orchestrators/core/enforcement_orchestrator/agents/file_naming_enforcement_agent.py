"""
FileNamingEnforcementAgent — CORE-028 file naming convention enforcement.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rule: CORE-028 (Intelligent file naming with Python module compliance).

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-004
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class FileNamingEnforcementAgent:
    """
    Enforces CORE-028 file naming conventions.

    Rules:
    - CORE-028: Intelligent file naming with Python module compliance
    - NO SCREAMING_CASE (e.g., PHASE-21-... is INVALID)
    - kebab-case for non-Python files (lowercase-with-hyphens)
    - snake_case for Python modules (per PEP 8)
    - Max 30 chars general, 40 chars for plan files
    - Plan files: must end with -plan.yaml, -spec.yaml, or -system.yaml

    Authority: CORE-028 updated 2026-02-04 with plan file exception
    """

    def __init__(self) -> None:
        """Initialize file naming enforcement agent."""
        self.name = "FileNamingEnforcementAgent"
        self.rules = ["CORE-028"]

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation against file naming rules.

        Args:
            operation: Operation context dictionary with file paths

        Returns:
            EnforcementResult with violations if blocked, warnings if concerns found
        """
        violations: List[str] = []
        warnings: List[str] = []

        # Check output file paths if present
        output_files = operation.get("output_files", [])
        if not output_files:
            target_file = operation.get("target_file")
            if target_file:
                output_files = [target_file]

        for file_path in output_files:
            if not file_path:
                continue

            filename = Path(file_path).name

            if self._should_skip_validation(filename):
                continue

            validation_result = self._validate_filename(filename)
            if validation_result["violations"]:
                violations.extend(validation_result["violations"])
            if validation_result["warnings"]:
                warnings.extend(validation_result["warnings"])

        level = EnforcementLevel.BLOCKED if violations else (
            EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS
        )

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "FileNamingEnforcementAgent",
                "rules_checked": ["CORE-028"],
            },
        )

    def _should_skip_validation(self, filename: str) -> bool:
        """Check if filename should skip validation (third-party, generated, etc.)."""
        skip_patterns = [
            "__init__.py",
            "setup.py",
            "conftest.py",
            "README.md",
            "node_modules",
            ".git",
            "__pycache__",
        ]
        return any(pattern in filename for pattern in skip_patterns)

    def _validate_filename(self, filename: str) -> Dict[str, Any]:
        """
        Validate single filename against CORE-028.

        Args:
            filename: Filename string to validate

        Returns:
            dict: {"violations": [], "warnings": []}
        """
        violations: List[str] = []
        warnings: List[str] = []

        # Check for SCREAMING_CASE (BLOCKED)
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        if base_name != base_name.lower():
            violations.append(
                f"CORE-028 VIOLATION: SCREAMING_CASE detected in '{filename}'. "
                f"Must use lowercase kebab-case. Convert to: {base_name.lower()}.{filename.split('.')[-1] if '.' in filename else ''}"
            )
            return {"violations": violations, "warnings": warnings}

        # Check length
        is_plan_file = filename.endswith(("-plan.yaml", "-spec.yaml", "-system.yaml"))
        max_length = 40 if is_plan_file else 30

        if len(filename) > max_length:
            file_type = "plan file" if is_plan_file else "file"
            violations.append(
                f"CORE-028 VIOLATION: Filename too long ({len(filename)} chars, max: {max_length} for {file_type}): {filename}"
            )

        # Check for spaces
        if " " in filename:
            violations.append(
                f"CORE-028 VIOLATION: Spaces not allowed in filename: {filename}. Use hyphens instead."
            )

        # Check kebab-case for non-Python files
        if not filename.endswith(".py"):
            if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+$", filename):
                warnings.append(
                    f"CORE-028 WARNING: Non-Python file should use kebab-case: {filename}"
                )

        return {"violations": violations, "warnings": warnings}
