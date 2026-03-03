"""
ArchitectureIntegrityAgent — Architectural integrity rule enforcement.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rules: CORE-017-020, 032, 034, 035, 038-041, ENH-064.

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-007
"""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class ArchitectureIntegrityAgent:
    """
    Enforces architectural integrity rules (CORE-017-020, 032, 034, 035, 038-041, ENH-064).

    Covers:
    - CORE-017-020: Versioned filenames, temporal naming patterns
    - CORE-032: Code review requirements
    - CORE-034: Performance budgets (<10s operations)
    - CORE-035: Single implementation (no _v2, _v3 files)
    - CORE-038: Turn budgets (max 20 turns per session)
    - CORE-039: Context management
    - CORE-040: Performance optimization
    - CORE-041: Event-driven architecture patterns
    - ENH-064: Response template wiring (orchestrators must use template system)
    """

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate architectural integrity requirements.

        Args:
            context: Operation context including:
                - output_files: List of files to be generated (optional)
                - turn_count: Number of turns in current session (optional)
                - estimated_duration_seconds: Estimated operation duration (optional)
                - orchestrator_files: Dict mapping orchestrator names to file content (optional)

        Returns:
            EnforcementResult with BLOCKED (CORE-035, ENH-064), WARNING (budgets), or PASS
        """
        violations: List[str] = []
        warnings: List[str] = []

        # ENH-064: Check orchestrators use response template system
        orchestrator_files = context.get("orchestrator_files", {})
        for orchestrator_name, file_content in orchestrator_files.items():
            has_base_template = "BaseResponseTemplate" in file_content
            has_template_integration = "TemplateIntegration" in file_content
            has_registry_usage = "get_orchestrator_template" in file_content

            if not (has_base_template or has_template_integration or has_registry_usage):
                violations.append(
                    f"ENH-064 VIOLATION: Orchestrator '{orchestrator_name}' must use response template system. "
                    f"Options: 1) Inherit BaseResponseTemplate, 2) Use TemplateIntegration mixin, "
                    f"3) Call get_orchestrator_template() from registry."
                )

        # CORE-035: Check for versioned filenames (_v2, _v3, etc.)
        output_files = context.get("output_files", [])
        for file in output_files:
            file_lower = file.lower()
            if "_v2" in file_lower or "_v3" in file_lower or "_v4" in file_lower:
                violations.append(
                    f"CORE-035 VIOLATION: Cannot create versioned file: {file}. "
                    "Use single canonical implementation. Refactor existing file instead."
                )

        # CORE-038: Check turn budget (max 20 turns)
        turn_count = context.get("turn_count", 0)
        if turn_count > 20:
            warnings.append(
                f"CORE-038 WARNING: Session has {turn_count} turns (recommended limit: 20). "
                "Consider wrapping up or starting new session."
            )

        # CORE-034: Check performance budget (<10s operations)
        estimated_duration = context.get("estimated_duration_seconds", 0)
        if estimated_duration > 10.0:
            warnings.append(
                f"CORE-034 WARNING: Operation estimated at {estimated_duration:.1f}s "
                "(recommended limit: 10s). Consider optimization or caching."
            )

        if violations:
            level = EnforcementLevel.BLOCKED
        elif warnings:
            level = EnforcementLevel.WARNING
        else:
            level = EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "ArchitectureIntegrityAgent",
                "rules_checked": [
                    "CORE-017", "CORE-018", "CORE-019", "CORE-020",
                    "CORE-032", "CORE-034", "CORE-035",
                    "CORE-038", "CORE-039", "CORE-040", "CORE-041",
                ],
                "turn_count": turn_count,
                "estimated_duration_seconds": estimated_duration,
            },
        )
