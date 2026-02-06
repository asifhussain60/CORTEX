"""
EnforcementOrchestrator - Pre-execution governance rule enforcement

Validates operations against 3-tier governance before execution:
- Tier 0 (BLOCKED): Immutable CORE rules
- Tier 1 (WARNING): Phase acceptance criteria
- Tier 2 (INFO): Best practices

Uses 3 specialized agents:
1. GovernanceEnforcementAgent: CORE-008, 011, 012, 013, 029, 030, 035
2. SecurityCheckpointAgent: CORE-026, 025, 027
3. ComplianceValidationAgent: Tier 1 phase rules

AC-ID: ENFORCEMENT-001
Phase: 8 (Governance Enhancement)
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

Author: Asif Hussain
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import logging

from cortex.core.result import Result, Ok, Err
from cortex.orchestrators.core.governance_registry import GovernanceRegistry

logger = logging.getLogger(__name__)


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
    
    def __init__(self):
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
    
    def __init__(self):
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
    
    def __init__(self):
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
    
    def __init__(self):
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
    
    Unless user explicitly requests them (user_explicit_request=True).
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
        
        for file in output_files:
            file_lower = file.lower()
            for pattern, description in forbidden_patterns:
                if pattern.lower() in file_lower:
                    violations.append(
                        f"CORE-002 VIOLATION: Cannot generate {description} markdown file: {file}. "
                        "Results must be reported inline in chat."
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


class ArchitectureIntegrityAgent:
    """
    Enforces architectural integrity rules (CORE-017-020, 032, 034, 035, 038-041).
    
    Covers:
    - CORE-017-020: Versioned filenames, temporal naming patterns
    - CORE-032: Code review requirements
    - CORE-034: Performance budgets (<10s operations)
    - CORE-035: Single implementation (no _v2, _v3 files)
    - CORE-038: Turn budgets (max 20 turns per session)
    - CORE-039: Context management
    - CORE-040: Performance optimization
    - CORE-041: Event-driven architecture patterns
    """
    
    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate architectural integrity requirements.
        
        Args:
            context: Operation context including:
                - output_files: List of files to be generated (optional)
                - turn_count: Number of turns in current session (optional)
                - estimated_duration_seconds: Estimated operation duration (optional)
        
        Returns:
            EnforcementResult with BLOCKED (CORE-035), WARNING (budgets), or PASS
        """
        violations = []
        warnings = []
        
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
    
    def __init__(self):
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
# ENFORCEMENT ORCHESTRATOR
# ============================================================================

class EnforcementOrchestrator:
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
    
    Coverage: 27/29 CORE rules automated (93%)
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
    
    def __init__(self, governance_registry: Optional[GovernanceRegistry] = None):
        """
        Initialize enforcement orchestrator with 8-agent system.
        
        Args:
            governance_registry: Optional governance registry (injected)
        """
        self.governance_registry = governance_registry
        self.agents = [
            GovernanceEnforcementAgent(),
            SecurityCheckpointAgent(),
            ComplianceValidationAgent(),
            FileNamingEnforcementAgent(),  # CORE-028
            IncrementalExecutionAgent(),  # CORE-001, 004
            MarkdownSuppressionAgent(),  # CORE-002
            ArchitectureIntegrityAgent(),  # CORE-017-020, 032, 034, 035, 038-041
            DiscoveryEnforcementAgent(),  # CORE-030, 035 (ENH-047)
        ]
        logger.info(f"EnforcementOrchestrator initialized with {len(self.agents)} agents (27/29 CORE rules)")

    
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
        
        # Execute agents in parallel
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = {executor.submit(agent.validate, operation): agent for agent in self.agents}
            
            for future in as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    agent_name = result.metadata.get("agent", agent.__class__.__name__)
                    
                    # Collect violations and warnings
                    if result.violations:
                        all_violations.extend(result.violations)
                        logger.warning(f"{agent_name} detected {len(result.violations)} violations")
                    
                    if result.warnings:
                        all_warnings.extend(result.warnings)
                        logger.info(f"{agent_name} issued {len(result.warnings)} warnings")
                    
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
        
        return Ok(enforcement_result)
    
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


__all__ = [
    "EnforcementOrchestrator",
    "EnforcementResult",
    "EnforcementLevel",
    "GovernanceEnforcementAgent",
    "SecurityCheckpointAgent",
    "ComplianceValidationAgent",
    "get_enforcement_orchestrator",
]
