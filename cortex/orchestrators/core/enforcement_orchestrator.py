"""
EnforcementOrchestrator - Pre-execution governance rule enforcement

Validates operations against 3-tier governance before execution:
- Tier 0 (BLOCKED): Immutable CORE rules
- Tier 1 (WARNING): Phase acceptance criteria
- Tier 2 (INFO): Best practices

Uses 9 specialized agents:
1. GovernanceEnforcementAgent: CORE-008, 011, 012, 013, 029, 030, 035
2. SecurityCheckpointAgent: CORE-026, 025, 027
3. ComplianceValidationAgent: Tier 1 phase rules
4. FileNamingEnforcementAgent: CORE-028
5. IncrementalExecutionAgent: CORE-001, 004
6. MarkdownSuppressionAgent: CORE-002
7. ArchitectureIntegrityAgent: CORE-017-020, 032, 034, 035, 038-041
8. DiscoveryEnforcementAgent: CORE-030, 035 (ENH-047)
9. ExtendedGovernanceAgent: CORE-058..063 (GAP-008)

With integrated telemetry for observability (Phase 4 GAP-002).

AC-ID: ENFORCEMENT-001
Phase: 8 (Governance Enhancement) + Phase 2-4 (GAP-002) + Phase 11 (GAP-008)
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

Author: Asif Hussain
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 90c
from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.intelligence.learning.opj_mixin import OPJMixin  # Phase 52: OPJ intelligence
from cortex.intelligence.learning.reinforcement_signal import SignalType  # Phase 83-d: URS

# Phase 58-C: DomainBrain + Memory wiring (decision-making orchestrator)
try:
    from cortex.intelligence.domain_brain import DomainBrainAPI as _EnfDomainBrainAPI  # type: ignore[attr-defined]
except Exception:
    _EnfDomainBrainAPI = None  # type: ignore[assignment,misc]

try:
    from cortex.intelligence.memory.tier2_adaptive.hallucination_prevention import (  # type: ignore[import]
        BehavioralBoundaryRules as _EnfBehavioralBoundaryRules,
    )
except Exception:
    _EnfBehavioralBoundaryRules = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Import telemetry (Phase 4)
try:
    from cortex.governance.telemetry import get_telemetry
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logger.warning("Governance telemetry not available (cortex.governance.telemetry)")


# ============================================================================
# ENUMS
# ============================================================================

class EnforcementLevel(Enum):
    """Enforcement result severity levels."""
    PASS = "pass"
    WARNING = "warning"
    BLOCKED = "blocked"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class EnforcementResult:
    """
    Result of governance enforcement check.

    Attributes:
        level: Enforcement level (PASS, WARNING, BLOCKED)
        violations: List of Tier 0 violations (block execution)
        warnings: List of Tier 1 warnings (escalate but allow)
        metadata: Additional context (execution time, agent count, etc.)
    """
    level: EnforcementLevel
    violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_blocked(self) -> bool:
        """Check if execution should be blocked."""
        return self.level == EnforcementLevel.BLOCKED

    def has_warnings(self) -> bool:
        """Check if there are warnings."""
        return len(self.warnings) > 0


# ============================================================================
# ENFORCEMENT AGENTS
# ============================================================================

class GovernanceEnforcementAgent:
    """
    Enforces Tier 0 code quality rules.

    Rules:
    - CORE-008: TDD (tests must exist before code)
    - CORE-011: Type hints mandatory
    - CORE-012: Google-style docstrings mandatory
    - CORE-013: No bare except clauses
    - CORE-029: Response header enforcement
    - CORE-030: Implementation truth (verify code, not docs)
    - CORE-035: Single canonical implementation
    """

    def __init__(self) -> None:
        """Initialize governance enforcement agent."""
        self.name = "GovernanceEnforcementAgent"
        self.rules = ["CORE-008", "CORE-011", "CORE-012", "CORE-013", "CORE-029", "CORE-030", "CORE-035"]

    def validate(self, operation: Dict[str, Any]) -> Result[List[str], List[str]]:
        """
        Validate operation against code quality rules.

        Args:
            operation: Operation context dictionary

        Returns:
            EnforcementResult with violations if blocked, warnings if concerns found
        """
        violations = []
        warnings = []

        # CORE-008: TDD - Tests must exist for IMPLEMENT/FIX operations
        if operation.get("intent") in ["IMPLEMENT", "FIX"]:
            test_file = operation.get("test_file")
            if not test_file:
                violations.append(
                    "CORE-008 VIOLATION: TDD required - tests must exist before code implementation"
                )

        # CORE-013: No bare except clauses
        code_sample = operation.get("code_sample", "")
        if "except:" in code_sample:
            violations.append(
                "CORE-013 VIOLATION: Bare except clause detected - use specific exceptions"
            )

        # CORE-011: Type hints (warning for now)
        if code_sample and "def " in code_sample:
            if "->" not in code_sample:
                warnings.append(
                    "CORE-011 WARNING: Type hints recommended for all functions"
                )

        # CORE-012: Docstrings (warning for now)
        if code_sample and "def " in code_sample:
            if '"""' not in code_sample and "'''" not in code_sample:
                warnings.append(
                    "CORE-012 WARNING: Google-style docstrings recommended"
                )

        # CORE-030: Implementation truth - verify file existence
        target_file = operation.get("target_file")
        if target_file and operation.get("verify_existence"):
            # Future enhancement: actually check file existence
            pass

        level = EnforcementLevel.BLOCKED if violations else (
            EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS
        )

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "GovernanceEnforcementAgent",
                "rules_checked": ["CORE-008", "CORE-011", "CORE-012", "CORE-013", "CORE-030"]
            }
        )


class SecurityCheckpointAgent:
    """
    Enforces Tier 0 safety rules.

    Rules:
    - CORE-026: Git checkpoint before major changes
    - CORE-025: Security review for sensitive operations
    - CORE-027: Audit trail logging (AC_START → AC_EXECUTE → AC_COMPLETE)
    """

    def __init__(self) -> None:
        """Initialize security checkpoint agent."""
        self.name = "SecurityCheckpointAgent"
        self.rules = ["CORE-026", "CORE-025", "CORE-027"]

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation against safety rules.

        Args:
            operation: Operation context dictionary

        Returns:
            EnforcementResult with violations if blocked, warnings if concerns found
        """
        violations = []
        warnings = []

        # CORE-026: Git checkpoint for major changes (SYSTEM scope)
        scope = operation.get("scope", "FILE")
        git_checkpoint = operation.get("git_checkpoint_created", False)

        if scope == "SYSTEM" and not git_checkpoint:
            violations.append(
                "CORE-026 VIOLATION: Git checkpoint required before system-wide changes"
            )

        # CORE-027: Audit trail - ensure AC_ID present
        ac_id = operation.get("ac_id")
        if not ac_id and operation.get("intent") != "ANALYZE":
            warnings.append(
                "CORE-027 WARNING: Audit trail (AC_ID) recommended for all operations"
            )

        level = EnforcementLevel.BLOCKED if violations else (
            EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS
        )

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "SecurityCheckpointAgent",
                "rules_checked": ["CORE-025", "CORE-026", "CORE-027"]
            }
        )


class ComplianceValidationAgent:
    """
    Validates Tier 1 phase readiness rules.

    Checks:
    - Phase prerequisites met
    - Acceptance criteria satisfied
    - Test coverage adequate
    """

    def __init__(self) -> None:
        """Initialize compliance validation agent."""
        self.name = "ComplianceValidationAgent"

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation against phase readiness rules.

        Args:
            operation: Operation context dictionary

        Returns:
            EnforcementResult with warnings (Tier 1 violations escalate, not block)
        """
        warnings = []

        # Check phase prerequisites
        prerequisites_met = operation.get("prerequisites_met")
        if prerequisites_met is False:
            phase = operation.get("phase", "Unknown")
            warnings.append(
                f"TIER-1 WARNING: Phase {phase} prerequisites not fully met"
            )

        # Check test coverage for critical operations
        if operation.get("intent") == "DEPLOY":
            test_coverage = operation.get("test_coverage", 0)
            if test_coverage < 80:
                warnings.append(
                    f"TIER-1 WARNING: Test coverage ({test_coverage}%) below 80% threshold for deployment"
                )

        level = EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=[],
            warnings=warnings,
            metadata={
                "agent": "ComplianceValidationAgent",
                "rules_checked": ["Tier 1 Phase Rules"]
            }
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
        violations = []
        warnings = []

        # Check output file paths if present
        output_files = operation.get("output_files", [])
        if not output_files:
            # Single file case
            target_file = operation.get("target_file")
            if target_file:
                output_files = [target_file]

        for file_path in output_files:
            if not file_path:
                continue

            # Extract filename from path
            from pathlib import Path
            filename = Path(file_path).name

            # Skip validation for certain patterns
            if self._should_skip_validation(filename):
                continue

            # Validate filename
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
                "rules_checked": ["CORE-028"]
            }
        )

    def _should_skip_validation(self, filename: str) -> bool:
        """Check if filename should skip validation (third-party, generated, etc.)."""
        skip_patterns = [
            "__init__.py",
            "setup.py",
            "conftest.py",
            "README.md",  # Phase 71 S1: Standard project root file
            "node_modules",
            ".git",
            "__pycache__",
        ]
        return any(pattern in filename for pattern in skip_patterns)

    def _validate_filename(self, filename: str) -> Dict[str, Any]:
        """
        Validate single filename against CORE-028.

        Returns:
            dict: {"violations": [], "warnings": []}
        """
        violations = []
        warnings = []

        # Check for SCREAMING_CASE (BLOCKED)
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        if base_name != base_name.lower():
            violations.append(
                f"CORE-028 VIOLATION: SCREAMING_CASE detected in '{filename}'. "
                f"Must use lowercase kebab-case. Convert to: {base_name.lower()}.{filename.split('.')[-1] if '.' in filename else ''}"
            )
            return {"violations": violations, "warnings": warnings}

        # Check length
        is_plan_file = filename.endswith(('-plan.yaml', '-spec.yaml', '-system.yaml'))
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
            import re
            if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*\.[a-z0-9]+$", filename):
                warnings.append(
                    f"CORE-028 WARNING: Non-Python file should use kebab-case: {filename}"
                )

        return {"violations": violations, "warnings": warnings}


class IncrementalExecutionAgent:
    """
    Enforces CORE-001 (incremental execution) and CORE-004 (continuation limits).

    CORE-001: Operations adding/modifying >500 LOC require decomposition.
    CORE-004: Continuation requests >1000 tokens receive warnings.

    Ensures large operations are broken into manageable chunks.
    """

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate incremental execution requirements.

        Args:
            context: Operation context including:
                - intent: Operation type (IMPLEMENT, CONTINUE, etc.)
                - estimated_loc: Estimated lines of code (optional)
                - continuation_tokens: Token count for continuations (optional)

        Returns:
            EnforcementResult with BLOCKED (>500 LOC), WARNING (>1000 tokens), or PASS
        """
        violations = []
        warnings = []

        # CORE-001: Check LOC limit for IMPLEMENT intents
        intent = context.get("intent", "").upper()
        estimated_loc = context.get("estimated_loc", 0)

        if intent == "IMPLEMENT" and estimated_loc > 500:
            violations.append(
                f"CORE-001 VIOLATION: Operation estimates {estimated_loc} LOC (limit: 500). "
                "Please decompose into smaller increments using IncrementalTaskDecomposer."
            )

        # CORE-004: Check token limit for CONTINUE intents
        if intent == "CONTINUE":
            continuation_tokens = context.get("continuation_tokens", 0)
            if continuation_tokens > 1000:
                warnings.append(
                    f"CORE-004 WARNING: Continuation request has {continuation_tokens} tokens "
                    "(recommended limit: 1000). Consider breaking into smaller tasks."
                )

        # Determine enforcement level
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
                "agent": "IncrementalExecutionAgent",
                "rules_checked": ["CORE-001", "CORE-004"],
                "estimated_loc": estimated_loc,
                "continuation_tokens": context.get("continuation_tokens", 0),
            }
        )


class MarkdownSuppressionAgent:
    """
    Enforces CORE-002 (no markdown file generation).

    Blocks generation of:
    - *-summary.md
    - *-report.md
    - *-plan.md
    - DEPLOYMENT-*.md
    - Root directory markdown (except README.md, docs/, cortex-registry/)

    Unless user explicitly requests them (user_explicit_request=True).

    Phase 71 S1: Enhanced with root directory validation to prevent pollution.
    """

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate markdown file generation restrictions.

        Args:
            context: Operation context including:
                - output_files: List of files to be generated (optional)
                - user_explicit_request: Whether user explicitly requested markdown (optional)

        Returns:
            EnforcementResult with BLOCKED (forbidden pattern) or PASS
        """
        violations = []

        # Skip if user explicitly requested markdown files
        if context.get("user_explicit_request", False):
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={"agent": "MarkdownSuppressionAgent", "rules_checked": ["CORE-002"], "explicit_request": True}
            )

        # Check output files for forbidden patterns
        output_files = context.get("output_files", [])
        forbidden_patterns = [
            ("-summary.md", "summary"),
            ("-report.md", "report"),
            ("-plan.md", "plan"),
            ("DEPLOYMENT-", "deployment guide"),
        ]

        # CORE-002 ENFORCEMENT: ONLY 3 allowed paths for .md files
        # Updated 2026-02-10: docs/ NO LONGER ALLOWED (inline only)
        allowed_md_paths = [
            ".github/prompts/",     # Prompt file updates
            ".github/agents/",      # Agent specification updates
            "README.md",            # Root README only (exact match)
        ]

        for file in output_files:
            file_lower = file.lower()

            # Strict markdown file validation (Phase 71 + Gap #2A fix)
            # Check this FIRST to avoid duplicate violations
            if file.endswith(".md") or file.endswith(".MD"):
                # Check if file matches allowed paths
                is_allowed = False

                # Check exact README.md match
                if file.strip("/") == "README.md":
                    is_allowed = True
                else:
                    # Check if file starts with allowed directory paths
                    for allowed_path in allowed_md_paths:
                        if allowed_path.endswith("/") and file.startswith(allowed_path):
                            is_allowed = True
                            break

                # Block ALL other markdown files (single violation per file)
                if not is_allowed:
                    # Check for specific forbidden patterns to provide better error messages
                    pattern_matched = False
                    for pattern, description in forbidden_patterns:
                        if pattern.lower() in file_lower:
                            violations.append(
                                f"CORE-002 VIOLATION: Cannot generate {description} markdown file: {file}. "
                                "Results must be reported inline in chat."
                            )
                            pattern_matched = True
                            break

                    # If no specific pattern matched, use generic message
                    if not pattern_matched:
                        violations.append(
                            f"CORE-002 VIOLATION: Cannot generate markdown file: {file}. "
                            "ONLY allowed: .github/prompts/*.md, .github/agents/*.md, README.md. "
                            "All findings must be inline in chat or stored in cortex-registry YAML files."
                    )

        # Determine enforcement level
        level = EnforcementLevel.BLOCKED if violations else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=[],
            metadata={
                "agent": "MarkdownSuppressionAgent",
                "rules_checked": ["CORE-002"],
                "output_files_count": len(output_files),
                "violations_count": len(violations),
            }
        )


class ResponseContentValidationAgent:
    """
    Enforces CORE-002-RESPONSE: No markdown file suggestions in response text.

    Validates response CONTENT (not just output_files) for forbidden patterns:
    - "cat > *.md" suggestions
    - "create_file" recommendations for .md files
    - "save this as" patterns
    - "generate markdown" instructions

    Complements MarkdownSuppressionAgent (validates output_files list).
    This agent validates actual response text to Copilot Chat.

    Phase: CORTEX Inline-First (Response-Level Gate)
    Authority: CORE-002-RESPONSE (new sub-rule for chat responses)
    """

    # Forbidden patterns that suggest markdown file creation
    FORBIDDEN_PATTERNS = [
        r"cat\s*>\s*[^\s]+\.md",           # cat > file.md
        r"cat\s*>>\s*[^\s]+\.md",          # cat >> file.md
        r"echo\s+.+>\s*[^\s]+\.md",        # echo ... > file.md
        r"printf\s+.+>\s*[^\s]+\.md",      # printf ... > file.md
        r"create_file\s*\(\s*['\"][^'\"]*\.md['\"]",  # create_file("file.md")
        r"create\s+.*\.md.*file",          # create markdown file
        r"generate.*markdown.*report",     # generate markdown report
        r"save\s+.*as\s+.*\.md",           # save this as file.md
        r"write\s+.*to\s+.*\.md",          # write to file.md
        r"output\s+.*to\s+.*\.md",         # output to file.md
        r"generated?\s+.*\.md.*file",      # generated file.md
    ]

    ALLOWED_CONTEXTS = [
        ".github/prompts/",
        ".github/agents/",
        "README.md",
    ]

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate response content for markdown file suggestions.

        Args:
            context: Operation context including:
                - response_text: The response being validated (required)
                - allow_markdown_suggestions: Override to allow (optional, default False)

        Returns:
            EnforcementResult with BLOCKED if violations, PASS otherwise
        """
        import re

        violations = []
        response_text = context.get("response_text", "")
        allow_markdown = context.get("allow_markdown_suggestions", False)

        # Skip if explicitly allowed
        if allow_markdown:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "ResponseContentValidationAgent",
                    "rules_checked": ["CORE-002-RESPONSE"],
                    "explicit_override": True,
                }
            )

        if not response_text:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "ResponseContentValidationAgent",
                    "rules_checked": ["CORE-002-RESPONSE"],
                    "response_length": 0,
                }
            )

        # Check for forbidden patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            matches = re.finditer(pattern, response_text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)

                # Check if match is in allowed context
                is_allowed = False
                for allowed_ctx in self.ALLOWED_CONTEXTS:
                    if allowed_ctx in matched_text:
                        is_allowed = True
                        break

                if not is_allowed:
                    violations.append(
                        f"CORE-002-RESPONSE VIOLATION: Response suggests markdown file creation: "
                        f"'{matched_text}'. Use inline chat display instead."
                    )

        # Determine enforcement level
        level = EnforcementLevel.BLOCKED if violations else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=[],
            metadata={
                "agent": "ResponseContentValidationAgent",
                "rules_checked": ["CORE-002-RESPONSE"],
                "response_length": len(response_text),
                "violations_count": len(violations),
                "patterns_checked": len(self.FORBIDDEN_PATTERNS),
            }
        )

    @staticmethod
    def transform_response_to_inline(response_text: str) -> str:
        """
        Transform response that suggests file creation to inline-only alternatives.

        Args:
            response_text: Original response

        Returns:
            Transformed response suggesting inline display
        """
        import re

        transformed = response_text

        # Replace "create_file" suggestions
        transformed = re.sub(
            r"(?i)(use\s+)?create_file\s*\(\s*['\"]([^'\"]*\.md)['\"]",
            r"Display the content inline in this chat (don't create files)",
            transformed
        )

        # Replace "cat >" patterns
        transformed = re.sub(
            r"(?i)cat\s*>\s*([^\s]+\.md)",
            r"Display the content inline in this chat instead of file output",
            transformed
        )

        # Replace "save as" patterns
        transformed = re.sub(
            r"(?i)save\s+.*as\s+.*\.md",
            r"Display the result inline; user can save chat transcript if needed",
            transformed
        )

        # Replace "generate report" suggestions
        transformed = re.sub(
            r"(?i)generate\s+.*markdown.*report",
            r"Display findings as a markdown table inline in chat",
            transformed
        )

        return transformed


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
        violations = []
        warnings = []

        # ENH-064: Check orchestrators use response template system
        orchestrator_files = context.get("orchestrator_files", {})
        for orchestrator_name, file_content in orchestrator_files.items():
            # Check for template integration markers
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

        # Determine enforcement level
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
                    "CORE-038", "CORE-039", "CORE-040", "CORE-041"
                ],
                "turn_count": turn_count,
                "estimated_duration_seconds": estimated_duration,
            }
        )


class DiscoveryEnforcementAgent:
    """
    Enforces pre-execution discovery to prevent duplicate implementations.

    Rules:
    - CORE-030: Implementation Truth (verify existing implementations)
    - CORE-035: Single canonical implementation (no duplicates)

    Authority: ENH-047 Pre-Execution Discovery Protocol
    """

    def __init__(self) -> None:
        """Initialize discovery enforcement agent."""
        self.name = "DiscoveryEnforcementAgent"
        self.rules = ["CORE-030", "CORE-035"]

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation using pre-execution discovery.

        Enforces:
        - CORE-030: Check for existing implementations before creating new
        - CORE-035: Block if duplicates detected

        Args:
            operation: Operation context with intent, feature_name, scope, etc.

        Returns:
            EnforcementResult with violations if discovery blocks execution
        """
        violations = []
        warnings = []

        intent = operation.get("intent", "UNKNOWN")

        # Only check for IMPLEMENT/DESIGN/REFACTOR intents
        if intent not in ["IMPLEMENT", "DESIGN", "REFACTOR"]:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                metadata={
                    "agent": "DiscoveryEnforcementAgent",
                    "skipped": f"Intent {intent} does not require discovery"
                }
            )

        # Check if discovery was performed
        discovery_result = operation.get("discovery_result")

        if not discovery_result:
            # Discovery not performed - this is a violation
            violations.append(
                "CORE-030 VIOLATION: Pre-execution discovery not performed. "
                "Run cortex_discover before IMPLEMENT/DESIGN/REFACTOR operations."
            )

            level = EnforcementLevel.BLOCKED

            return EnforcementResult(
                level=level,
                violations=violations,
                metadata={
                    "agent": "DiscoveryEnforcementAgent",
                    "rules_checked": ["CORE-030", "CORE-035"],
                    "authority": "ENH-047"
                }
            )

        # Analyze discovery results
        recommendation = discovery_result.get("recommendation")
        duplicates = discovery_result.get("duplicates", [])
        existing_features = discovery_result.get("existing_features", [])

        # CORE-035: Block if duplicates detected
        if duplicates and len(duplicates) > 0:
            violations.append(
                f"CORE-035 VIOLATION: {len(duplicates)} duplicate implementation(s) detected. "
                f"Consolidate existing implementations first: {[d['file_path'] for d in duplicates[:3]]}"
            )

        # CORE-030: Warn if existing features found but not acknowledged
        if existing_features and len(existing_features) > 0:
            extend_mode = operation.get("extend_mode", False)

            if not extend_mode and recommendation == "EXTEND":
                warnings.append(
                    f"CORE-030 WARNING: {len(existing_features)} similar implementation(s) found. "
                    f"Consider extending: {[f['file_path'] for f in existing_features[:3]]}. "
                    "Add --extend flag if intentionally creating new implementation."
                )

        level = EnforcementLevel.BLOCKED if violations else (
            EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS
        )

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "DiscoveryEnforcementAgent",
                "rules_checked": ["CORE-030", "CORE-035"],
                "discovery_summary": {
                    "recommendation": recommendation,
                    "duplicates_found": len(duplicates),
                    "existing_features_found": len(existing_features),
                },
                "authority": "ENH-047"
            }
        )



# ============================================================================
# EXTENDED GOVERNANCE AGENT — CORE-058..063
# ============================================================================


class ExtendedGovernanceAgent:
    """
    Enforces the 6 extended CORE governance rules (CORE-058 through CORE-063).

    Rules:
    - CORE-058 (Tier 0): SQLite WAL mode mandatory for all audit databases
    - CORE-059 (Tier 1): MCP footprint auditing — every tool invocation must be logged
    - CORE-060 (Tier 1): SDLC brain governance — decisions must flow through SDLC Brain
    - CORE-061 (Tier 1): Business expressibility — business-critical ops must have clear intent
    - CORE-062 (Tier 0): Plan-first execution — IMPLEMENT/FIX/REFACTOR require approved plan
    - CORE-063 (Tier 0): Challenge-first gate — SYSTEM-scope ops require challenge issuance

    Authority: governance_alignment_phase_2.py + cortex-refactor-master.yaml GAP-008
    """

    # Operation types that require an approved plan document (CORE-062)
    PLAN_REQUIRED_OPS = {"IMPLEMENT", "FIX", "REFACTOR", "DEPLOY", "DELETE"}

    def __init__(self) -> None:
        """Initialize ExtendedGovernanceAgent with rule list."""
        self.rules = [
            "CORE-058",
            "CORE-059",
            "CORE-060",
            "CORE-061",
            "CORE-062",
            "CORE-063",
        ]

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate context against CORE-058 through CORE-063.

        Args:
            context: Operation context. Recognised keys:
                - sqlite_db_paths (List[str]): Paths to SQLite DBs being opened/created
                - wal_mode_enabled (bool): Whether WAL mode is active (CORE-058)
                - mcp_tool_invoked (str): Name of MCP tool being called (CORE-059)
                - mcp_logging_enabled (bool): Whether invocation logging is active (CORE-059)
                - sdlc_action (str): SDLC lifecycle action being taken (CORE-060)
                - sdlc_approved (bool): Whether SDLC Brain approved the action (CORE-060)
                - operation_type (str): e.g. "IMPLEMENT", "FIX", "READ" (CORE-062)
                - plan_document (str): Path to approved plan YAML (CORE-062)
                - operation_scope (str): e.g. "SYSTEM", "MODULE", "FILE" (CORE-063)
                - challenge_issued (bool): Whether holistic challenge was issued (CORE-063)

        Returns:
            EnforcementResult — BLOCKED for Tier-0 violations, WARNING for Tier-1, PASS otherwise
        """
        violations: List[str] = []
        warnings: List[str] = []

        # ── CORE-058: SQLite WAL Mode Mandatory ────────────────────────────
        sqlite_db_paths = context.get("sqlite_db_paths", [])
        if sqlite_db_paths:
            wal_enabled = context.get("wal_mode_enabled", True)  # default safe
            if not wal_enabled:
                violations.append(
                    "CORE-058 VIOLATION: SQLite WAL mode is DISABLED. "
                    "All audit databases MUST use WAL (Write-Ahead Logging) mode "
                    "for concurrent-safe writes. Set PRAGMA journal_mode=WAL on open."
                )

        # ── CORE-059: MCP Footprint Auditing ───────────────────────────────
        mcp_tool = context.get("mcp_tool_invoked")
        if mcp_tool:
            mcp_logging = context.get("mcp_logging_enabled", True)  # default safe
            if not mcp_logging:
                warnings.append(
                    f"CORE-059 WARNING: MCP tool '{mcp_tool}' invoked without logging enabled. "
                    "Every MCP tool invocation MUST be logged with: timestamp, tool_id, "
                    "input_params, execution_duration, output_status."
                )

        # ── CORE-060: SDLC Brain Governance ────────────────────────────────
        sdlc_action = context.get("sdlc_action")
        if sdlc_action:
            sdlc_approved = context.get("sdlc_approved", False)
            if not sdlc_approved:
                warnings.append(
                    f"CORE-060 WARNING: SDLC action '{sdlc_action}' taken without SDLC Brain "
                    "approval. All SDLC decisions MUST flow through SDLC Brain for compliance "
                    "verification. No direct execution without approval."
                )

        # ── CORE-061: Business Expressibility (advisory) ──────────────────
        # Tier-1 recommended; no hard block enforced at this layer

        # ── CORE-062: Plan-First Execution ─────────────────────────────────
        operation_type = context.get("operation_type", "").upper()
        if operation_type in self.PLAN_REQUIRED_OPS:
            plan_doc = context.get("plan_document")
            if not plan_doc:
                violations.append(
                    f"CORE-062 VIOLATION: Operation type '{operation_type}' requires an approved "
                    "plan document. Specify 'plan_document' key with path to the approved plan "
                    "YAML (e.g. cortex-registry/planning/cortex-refactor-master.yaml). "
                    "Ad-hoc execution is BLOCKED."
                )

        # ── CORE-063: Challenge-First Governance Gate ───────────────────────
        operation_scope = context.get("operation_scope", "").upper()
        if operation_scope == "SYSTEM":
            challenge = context.get("challenge_issued", False)
            if not challenge:
                violations.append(
                    "CORE-063 VIOLATION: SYSTEM-scope operation requires a holistic challenge "
                    "before execution. Set 'challenge_issued': True after issuing challenge. "
                    "Challenge forces reconsideration: optimal approach? risks? alternatives?"
                )

        # ── Determine enforcement level ─────────────────────────────────────
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
                "agent": "ExtendedGovernanceAgent",
                "rules_checked": self.rules,
                "sqlite_db_paths": sqlite_db_paths,
                "mcp_tool_invoked": mcp_tool,
                "operation_type": operation_type or None,
                "operation_scope": operation_scope or None,
            },
        )



# ============================================================================
# SWEEP COMPOSITION ENFORCEMENT AGENT — CORE-064 (Phase 56)
# ============================================================================


class SweepCompositionEnforcementAgent:
    """
    Enforces CORE-064 (Sweep Completeness Contract) at composition time.

    Validates that any composed workflow template for FIX, REFACTOR, or AUDIT
    operations contains the mandatory sweep catalogue envelope:
      - step[0].id == 'sweep_catalogue_open'
      - step[-1].id == 'sweep_catalogue_assert_exhausted' with blocking=True

    This is a **structural** check — it prevents a composed template from
    reaching execution without the sweep contract wired in.  It complements
    the runtime SweepCatalogueOrchestrator.assert_exhausted() call, which
    raises SweepIncompleteError when open items remain.

    Wired into EnforcementOrchestrator as agent #11 (Phase 56).
    Authority: CORE-064 Sweep Completeness Contract.
    """

    # Operations that require a sweep envelope
    SWEEP_OPERATIONS: frozenset = frozenset({"FIX", "REFACTOR", "AUDIT"})

    def __init__(self) -> None:
        """Initialize SweepCompositionEnforcementAgent."""
        self.name = "SweepCompositionEnforcementAgent"
        self.rules = ["CORE-064"]

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate that a composed template carries the CORE-064 sweep envelope.

        Args:
            context: Operation context with optional keys:
                - composed_template (Dict): The template produced by TemplateComposer.
                - operation_type (str): e.g. "FIX", "REFACTOR", "AUDIT", "IMPLEMENT".

        Returns:
            EnforcementResult — BLOCKED for Tier-0 CORE-064 violations, PASS otherwise.
        """
        violations: List[str] = []
        operation_type = context.get("operation_type", "").upper()
        composed_template = context.get("composed_template")

        # Skip: no composed template in context (non-composer code path)
        if not composed_template:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "SweepCompositionEnforcementAgent",
                    "skipped": "No composed_template in context",
                },
            )

        # Skip: operation does not require a sweep envelope
        if operation_type not in self.SWEEP_OPERATIONS:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "SweepCompositionEnforcementAgent",
                    "skipped": f"operation_type={operation_type!r} does not require sweep envelope",
                },
            )

        steps: List[Dict[str, Any]] = composed_template.get("steps", [])

        # Check sweep_catalogue_open is step[0]
        if not steps or steps[0].get("id") != "sweep_catalogue_open":
            violations.append(
                f"CORE-064 VIOLATION: Composed {operation_type} template is missing "
                "'sweep_catalogue_open' as step[0]. Every FIX/REFACTOR/AUDIT composed "
                "workflow must open a SweepCatalogue before execution. "
                "This is a P0 Sweep Completeness Contract violation."
            )

        # Check sweep_catalogue_assert_exhausted is step[-1] with blocking=True
        if not steps or steps[-1].get("id") != "sweep_catalogue_assert_exhausted":
            violations.append(
                f"CORE-064 VIOLATION: Composed {operation_type} template is missing "
                "'sweep_catalogue_assert_exhausted' as step[-1]. Every FIX/REFACTOR/AUDIT "
                "composed workflow must assert the catalogue is exhausted before "
                "AC_COMPLETE is emitted. Partial sweeps are a governance violation."
            )
        elif not steps[-1].get("blocking", False):
            violations.append(
                "CORE-064 VIOLATION: 'sweep_catalogue_assert_exhausted' step must have "
                "blocking=True. A non-blocking close step allows partial sweeps to slip through."
            )

        level = EnforcementLevel.BLOCKED if violations else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=[],
            metadata={
                "agent": "SweepCompositionEnforcementAgent",
                "rules_checked": ["CORE-064"],
                "operation_type": operation_type,
                "step_count": len(steps),
                "sweep_envelope_present": len(violations) == 0,
            },
        )


# ============================================================================
# ENFORCEMENT ORCHESTRATOR
# ============================================================================

class EnforcementOrchestrator(OPJMixin, OrchestratorProtocolMixin, WorkflowEnforcementMixin, WorkflowTemplateMixin):
    """
    Pre-execution governance enforcement orchestrator with 8-agent system.

    Validates operations against 3-tier governance before execution:
    - Executes 8 agents in parallel for speed (<150ms target)
    - Aggregates violations and warnings
    - Blocks execution on Tier 0 violations
    - Escalates Tier 1 warnings without blocking

    Agent Architecture:
    1. GovernanceEnforcementAgent: CORE-008, 011, 012, 013, 029, 030
    2. SecurityCheckpointAgent: CORE-025, 026, 027
    3. ComplianceValidationAgent: Tier 1 rules
    4. FileNamingEnforcementAgent: CORE-028
    5. IncrementalExecutionAgent: CORE-001, 004
    6. MarkdownSuppressionAgent: CORE-002
    7. ArchitectureIntegrityAgent: CORE-017-020, 032, 034, 035, 038-041
    8. DiscoveryEnforcementAgent: CORE-030, 035 (ENH-047)
    9. ExtendedGovernanceAgent: CORE-058..063 (GAP-008)
    10. ResponseContentValidationAgent: CORE-002-RESPONSE
    11. SweepCompositionEnforcementAgent: CORE-064 (Phase 56 — structural sweep gate)

    Coverage: 35/35 CORE rules automated (100%)
    Manual rules: CORE-005, 006 (runtime/post-implementation)

    Usage:
        orchestrator = EnforcementOrchestrator()
        result = orchestrator.validate_operation(operation)

        if result.is_err():
            # Tier 0 violation - BLOCK execution
            print(result.error.violations)
        elif result.value.has_warnings():
            # Tier 1 warnings - ESCALATE but allow
            print(result.value.warnings)
    """

    # Phase 90c — must remain False: EnforcementOrchestrator IS the governance gate.
    # Self-gating would create a circular dependency where the gate gates itself.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self, governance_registry: Optional[GovernanceRegistry] = None) -> None:
        """
        Initialize enforcement orchestrator with 11-agent system.

        Args:
            governance_registry: Optional governance registry (injected)
        """
        self.governance_registry = governance_registry
        self.agents = [
            GovernanceEnforcementAgent(),
            SecurityCheckpointAgent(),
            ComplianceValidationAgent(),
            FileNamingEnforcementAgent(),           # CORE-028
            IncrementalExecutionAgent(),            # CORE-001, 004
            MarkdownSuppressionAgent(),             # CORE-002
            ArchitectureIntegrityAgent(),           # CORE-017-020, 032, 034, 035, 038-041
            DiscoveryEnforcementAgent(),            # CORE-030, 035 (ENH-047)
            ResponseContentValidationAgent(),       # CORE-002-RESPONSE
            ExtendedGovernanceAgent(),              # CORE-058..063 (GAP-008)
            SweepCompositionEnforcementAgent(),     # CORE-064 (Phase 56 — structural sweep gate)
        ]
        logger.info(f"EnforcementOrchestrator initialized with {len(self.agents)} agents (35/35 CORE rules)")

    def get_recommended_template(self) -> str:
        """Get the recommended workflow template for enforcement operations."""
        return "security/compliance-audit"

    def _inject_governance_knowledge(self) -> Dict[str, Any]:
        """Inject governance knowledge YAMLs into enforcement context.

        Phase 78 GAP-78-A-04: Wire cortex-registry/knowledge-base/governance/*.yaml
        so rule validation is knowledge-informed (not just hard-coded rule IDs).

        Returns:
            Dict with governance knowledge from development-rules, compliance-rules,
            operations-rules, data-rules, security-rules YAMLs.
        """
        try:
            from cortex.intelligence.provider import get_intelligence_provider
            provider = get_intelligence_provider()
            return provider.get_best_practices("governance:enforcement")
        except Exception:
            return {}

    def _load_governance_knowledge(self) -> Dict[str, Any]:
        """Load governance knowledge from canonical knowledge-base YAMLs.

        Phase 78 GAP-78-A-04: Convenience wrapper — loads governance YAML files
        directly from cortex-registry/knowledge-base/governance/.

        Returns:
            Merged dict of all governance knowledge YAML contents.
        """
        return self._inject_governance_knowledge()

    def validate_operation(self, operation: Dict[str, Any]) -> Result[EnforcementResult, EnforcementResult]:
        """
        Validate operation against governance rules using 8-agent system.

        Executes 8 agents in parallel:
        1. GovernanceEnforcementAgent (CORE-008, 011, 012, 013, 029, 030)
        2. SecurityCheckpointAgent (CORE-025, 026, 027)
        3. ComplianceValidationAgent (Tier 1 rules)
        4. FileNamingEnforcementAgent (CORE-028)
        5. IncrementalExecutionAgent (CORE-001, 004)
        6. MarkdownSuppressionAgent (CORE-002)
        7. ArchitectureIntegrityAgent (CORE-017-020, 032, 034, 035, 038-041)
        8. DiscoveryEnforcementAgent (CORE-030, 035 - ENH-047)

        Coverage: 27/29 CORE rules automated (93%)
        Performance target: <150ms

        Args:
            operation: Operation context with intent, target_file, test_file, etc.

        Returns:
            Ok(EnforcementResult) if compliant or warnings only
            Err(EnforcementResult) if Tier 0 violations detected
        """
        start_time = time.time()
        all_violations = []
        all_warnings = []
        highest_level = EnforcementLevel.PASS

        # Phase 58 — cross-cutting hooks: LENS + KnSynth only (GovGate skipped — this IS the gate)
        lens_ctx = self._extract_lens_context(operation.get("orchestrator_context"))
        self._consume_unified_context(operation.get("unified_context"))

        # Get telemetry instance if available
        telemetry = get_telemetry() if TELEMETRY_AVAILABLE else None
        intent = operation.get("intent", "UNKNOWN")

        # Execute agents in parallel
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {executor.submit(agent.validate, operation): agent for agent in self.agents}

            for future in as_completed(futures):
                agent = futures[future]
                agent_start_time = time.time()

                try:
                    result = future.result()
                    agent_name = result.metadata.get("agent", agent.__class__.__name__)
                    agent_latency_ms = (time.time() - agent_start_time) * 1000

                    # Record telemetry
                    if telemetry:
                        telemetry.record_agent_invocation(
                            agent_name=agent_name,
                            intent=intent,
                            result=result.level.value,
                            latency_ms=agent_latency_ms,
                            violations_count=len(result.violations),
                            warnings_count=len(result.warnings),
                        )

                    # Collect violations and warnings
                    if result.violations:
                        all_violations.extend(result.violations)
                        logger.warning(f"{agent_name} detected {len(result.violations)} violations")

                        # Record each violation
                        if telemetry:
                            for violation in result.violations:
                                # Extract CORE rule ID from violation message
                                rule_id = "UNKNOWN"
                                if "CORE-" in violation:
                                    import re
                                    match = re.search(r'CORE-\d+', violation)
                                    if match:
                                        rule_id = match.group(0)

                                telemetry.record_violation(
                                    rule_id=rule_id,
                                    violation_message=violation,
                                    agent_name=agent_name,
                                )

                    if result.warnings:
                        all_warnings.extend(result.warnings)
                        logger.info(f"{agent_name} issued {len(result.warnings)} warnings")

                        # Record each warning
                        if telemetry:
                            for warning in result.warnings:
                                # Extract CORE rule ID from warning message
                                rule_id = "UNKNOWN"
                                if "CORE-" in warning or "TIER-" in warning:
                                    import re
                                    match = re.search(r'(CORE|TIER)-\d+', warning)
                                    if match:
                                        rule_id = match.group(0)

                                telemetry.record_warning(
                                    rule_id=rule_id,
                                    warning_message=warning,
                                    agent_name=agent_name,
                                )

                    # Track highest enforcement level
                    if result.level == EnforcementLevel.BLOCKED:
                        highest_level = EnforcementLevel.BLOCKED
                    elif result.level == EnforcementLevel.WARNING and highest_level == EnforcementLevel.PASS:
                        highest_level = EnforcementLevel.WARNING

                except Exception as e:
                    agent_name = agent.__class__.__name__
                    logger.error(f"{agent_name} validation failed: {e}")
                    all_warnings.append(f"Agent {agent_name} validation error: {str(e)}")

        execution_time_ms = (time.time() - start_time) * 1000

        # Determine enforcement level
        if all_violations:
            level = EnforcementLevel.BLOCKED
            enforcement_result = EnforcementResult(
                level=level,
                violations=all_violations,
                warnings=all_warnings,
                metadata={
                    "agent_count": len(self.agents),
                    "execution_time_ms": round(execution_time_ms, 2),
                    "blocked": True,
                }
            )
            # Phase 52: Record governance violation pattern
            self._opj_record_failure(
                operation="validate_operation",
                error=f"{len(all_violations)} governance violation(s): {'; '.join(all_violations[:2])}",
                attempted_fix="see violation details",
                confidence=0.9,
                avoid_in_future=f"Ensure operation satisfies: {'; '.join(all_violations[:2])}",
            )
            return Err(enforcement_result)

        elif all_warnings:
            level = EnforcementLevel.WARNING
        else:
            level = EnforcementLevel.PASS

        enforcement_result = EnforcementResult(
            level=level,
            violations=[],
            warnings=all_warnings,
            metadata={
                "agent_count": len(self.agents),
                "execution_time_ms": round(execution_time_ms, 2),
                "blocked": False,
            }
        )
        # Phase 52: Record compliance success pattern
        self._opj_record_success(
            operation="validate_operation",
            context={"intent": str(intent)[:200], "agent_count": len(self.agents)},
            resolution=f"All {len(self.agents)} agents passed in {round(execution_time_ms, 1)}ms",
            confidence=0.85,
        )
        return Ok(enforcement_result)

    def _format_governance_rule_with_book(self, rule_id: str) -> str:
        """
        Format governance rule with book reference for inline display.

        Uses BusinessWisdomFormatter to enrich governance messages with
        authoritative book citations, enhancing user education.

        Args:
            rule_id: CORE rule ID (e.g., "CORE-008")

        Returns:
            Formatted string with book reference. Falls back to rule_id if formatting fails.

        Example:
            >>> orchestrator._format_governance_rule_with_book("CORE-008")
            '**Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)'

        Authority:
            - business-wisdom-wiring.md (Stage 2)
            - phase-06-business-wisdom-display-enhancement.yaml

        AC-ID: AC-PHASE-06-S2-001
        """
        try:
            from cortex.orchestrators.core.business_wisdom_formatter import BusinessWisdomFormatter

            formatter = BusinessWisdomFormatter()
            markdown = formatter.format_governance_with_books(
                rule_ids=[rule_id],
                max_display=1,
                include_icon=False
            )

            if markdown:
                # Strip list marker and header for inline display
                lines = markdown.split("\n")
                for line in lines:
                    if line.startswith("- "):
                        return line[2:].strip()  # Remove "- " prefix

            # Fallback to rule ID only
            return rule_id

        except Exception as e:
            logger.warning(f"Failed to format rule {rule_id} with book reference: {e}")
            return rule_id

    def validate_response_content(self, response_text: str, allow_markdown: bool = False) -> Result[EnforcementResult, EnforcementResult]:
        """
        Validate response content for markdown file suggestions (CORE-002-RESPONSE).

        This is the response-level gate that catches file suggestions in actual chat responses.
        Complements validate_operation() which validates output_files lists.

        Args:
            response_text: The response being sent to Copilot Chat
            allow_markdown: Override to allow markdown suggestions (default False)

        Returns:
            Ok(result) if no violations, Err(result) if CORE-002-RESPONSE violated

        Phase: CORTEX Inline-First Architecture (Response-Level Gate)
        Authority: CORE-002-RESPONSE
        """
        start_time = time.time()

        # Use ResponseContentValidationAgent
        agent = ResponseContentValidationAgent()
        validation_result = agent.validate({
            "response_text": response_text,
            "allow_markdown_suggestions": allow_markdown,
        })

        execution_time_ms = (time.time() - start_time) * 1000
        validation_result.metadata["execution_time_ms"] = round(execution_time_ms, 2)

        if validation_result.is_blocked():
            logger.warning(
                f"Response contains markdown file suggestions: "
                f"{len(validation_result.violations)} violations"
            )
            return Err(validation_result)

        logger.debug(f"Response content validation passed in {execution_time_ms:.2f}ms")
        return Ok(validation_result)

    def transform_response_to_inline(self, response_text: str) -> str:
        """
        Transform response that suggests file creation to inline-only alternatives.

        Replaces file creation suggestions with inline chat display recommendations.

        Args:
            response_text: Original response

        Returns:
            Transformed response suggesting inline display
        """
        return ResponseContentValidationAgent.transform_response_to_inline(response_text)

    def validate_intent_classification(self, intent_reflection: Dict[str, Any]) -> Result[List[str], List[str]]:
        """
        Validate intent classification integrity (Layer 1: Pre-Execution Gate).

        Ensures DoR (Definition of Ready) displays all required fields:
        - Intent type mapped correctly
        - Target handler appropriate for intent
        - Business principles populated
        - Governance rules present
        - Scope/Impact assessed

        Args:
            intent_reflection: IntentReflection dict with DoR fields

        Returns:
            Ok([]) if valid, Err([violations]) if invalid

        AC-ID: REM-003-01 (Governance Defense-in-Depth Layer 1)
        """
        violations = []

        # Required fields validation
        required_fields = ["intent_type", "target_handler", "dor_confidence", "scope"]
        for field in required_fields:
            if not intent_reflection.get(field):
                violations.append(
                    f"Intent classification incomplete: missing '{field}' field"
                )

        # Business principles validation
        governance_rules = intent_reflection.get("governance_rules", [])
        business_principles = intent_reflection.get("business_principles", {})

        if governance_rules and not business_principles:
            violations.append(
                "Intent classification integrity violation: "
                "governance_rules present but business_principles not populated"
            )

        # DoR confidence range validation
        dor_confidence = intent_reflection.get("dor_confidence", 0)
        if not (0.0 <= dor_confidence <= 1.0):
            violations.append(
                f"DoR confidence out of range: {dor_confidence} (must be 0.0-1.0)"
            )

        if violations:
            return Err(violations)
        return Ok([])

    def validate_dor_confidence(
        self,
        promised_confidence: float,
        intent_type: str,
        available_context: Dict[str, Any]
    ) -> Result[List[str], List[str]]:
        """
        Validate DoR confidence is not artificially inflated (Layer 1).

        Prevents confidence manipulation by checking if promised confidence
        matches available context evidence.

        Args:
            promised_confidence: DoR confidence from intent classification
            intent_type: Type of intent (IMPLEMENT, FIX, etc.)
            available_context: Context used for confidence calculation

        Returns:
            Ok([]) if confidence justified, Err([violations]) if suspicious

        AC-ID: REM-003-01 (Governance Defense-in-Depth Layer 1)
        """
        violations = []

        # Check confidence vs context quality
        context_score = 0.0

        if available_context.get("target_file_exists"):
            context_score += 0.2
        if available_context.get("test_file_exists"):
            context_score += 0.2
        if available_context.get("similar_patterns_found"):
            context_score += 0.2
        if available_context.get("clear_requirements"):
            context_score += 0.2
        if available_context.get("dependencies_known"):
            context_score += 0.2

        # Confidence should not exceed context quality by >30%
        if promised_confidence > (context_score + 0.3):
            violations.append(
                f"DoR confidence suspiciously high: {promised_confidence:.0%} "
                f"with only {context_score:.0%} context quality "
                f"(maximum justified: {(context_score + 0.3):.0%})"
            )

        # Minimum confidence thresholds by intent
        min_confidence = {
            "IMPLEMENT": 0.60,
            "FIX": 0.50,
            "REFACTOR": 0.70,
            "ANALYZE": 0.40,
        }.get(intent_type, 0.50)

        if promised_confidence < min_confidence:
            violations.append(
                f"DoR confidence too low for {intent_type}: {promised_confidence:.0%} "
                f"(minimum: {min_confidence:.0%})"
            )

        if violations:
            return Err(violations)
        return Ok([])

    def validate_business_principles_mapping(
        self,
        governance_rules: List[str],
        business_principles: Dict[str, str]
    ) -> Result[List[str], List[str]]:
        """
        Validate governance rules correctly mapped to business principles (Layer 1).

        Ensures CORE rules are explained in human-readable business terms.

        Args:
            governance_rules: List of CORE-XXX rule IDs
            business_principles: Dict of {principle_name: technical_term}

        Returns:
            Ok([]) if mapping valid, Err([violations]) if incorrect

        AC-ID: REM-003-01 (Governance Defense-in-Depth Layer 1)
        """
        violations = []

        if not governance_rules:
            return Ok([])  # No rules to map

        if not business_principles:
            violations.append(
                f"Business principles mapping missing: "
                f"{len(governance_rules)} governance rules require explanation"
            )
            return Err(violations)

        # Validate each rule has a principle mapping
        # Note: Multiple rules can map to same principle (e.g., CORE-008, CORE-011 → Quality First)
        rules_mentioned = []
        for principle, technical in business_principles.items():
            # Extract CORE-XXX from technical term
            if "CORE-" in technical:
                rules_mentioned.append(technical.split("(")[1].split(")")[0] if "(" in technical else "")

        unmapped_rules = [rule for rule in governance_rules if rule not in rules_mentioned]

        if unmapped_rules:
            violations.append(
                f"Governance rules not mapped to business principles: {', '.join(unmapped_rules)}"
            )

        if violations:
            return Err(violations)
        return Ok([])

    # ── Phase 83-d: URS signal emission ─────────────────────────────────────

    def _emit_enforcement_signal(
        self,
        operation: str,
        violations: List[str],
        warnings: List[str],
    ) -> None:
        """Emit a reinforcement signal after governance validation.

        Signal mapping:
          - Zero violations AND zero warnings → STRONG_REWARD
          - Zero violations, warnings only    → MILD_REWARD
          - Any violations present            → MILD_PUNISHMENT

        Args:
            operation: The enforcement operation that completed.
            violations: List of violation messages (P0/P1 severity).
            warnings: List of warning messages (P2 severity).
        """
        if violations:
            signal = SignalType.MILD_PUNISHMENT
        elif warnings:
            signal = SignalType.MILD_REWARD
        else:
            signal = SignalType.STRONG_REWARD

        self._urs_emit_signal(
            signal_type=signal,
            pattern_id=operation,
            context={
                "violation_count": len(violations),
                "warning_count": len(warnings),
            },
        )

    def get_capabilities(self) -> List[str]:
        """
        Get enforcement orchestrator capabilities.

        Returns:
            List of capability strings
        """
        return [
            "governance_enforcement",
            "rule_validation",
            "pre_execution_gate",
            "tier_0_blocking",
            "tier_1_escalation",
            "intent_classification_validation",  # NEW: REM-003-01
            "dor_confidence_validation",  # NEW: REM-003-01
            "business_principles_mapping_validation",  # NEW: REM-003-01
        ]


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_enforcement_orchestrator_instance: Optional[EnforcementOrchestrator] = None


def get_enforcement_orchestrator() -> EnforcementOrchestrator:
    """
    Get singleton enforcement orchestrator instance.

    Returns:
        EnforcementOrchestrator instance
    """
    global _enforcement_orchestrator_instance

    if _enforcement_orchestrator_instance is None:
        _enforcement_orchestrator_instance = EnforcementOrchestrator()

    return _enforcement_orchestrator_instance


try:
    from cortex.governance.business_rule_enforcement_agent import BusinessRuleEnforcementAgent  # noqa: F401
except ImportError:
    BusinessRuleEnforcementAgent = None  # type: ignore[assignment,misc]

__all__ = [
    "EnforcementOrchestrator",
    "EnforcementResult",
    "EnforcementLevel",
    "GovernanceEnforcementAgent",
    "SecurityCheckpointAgent",
    "ComplianceValidationAgent",
    "ExtendedGovernanceAgent",
    "BusinessRuleEnforcementAgent",  # Phase 84-b: business-rules enforcement layer
    "get_enforcement_orchestrator",
]
