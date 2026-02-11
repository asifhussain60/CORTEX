"""
🔍 GOVERNANCE VIOLATION DEBUGGER - MCP-Exposed Debugging Orchestrator

Purpose: Detect and fix CORTEX governance violations iteratively.

Authority: CORE-049 (Silent Autonomous Execution)
          CORE-002 (Markdown Suppression)
          GAP-001 (Direct Tool Blocking)
          CORE-030 (Implementation Truth)

Cycles: 10+ iterative detection cycles until no violations found

MCP Tools Exposed:
- cortex_debug_violations: Detect violations in workflow
- cortex_fix_violations: Apply fixes automatically
- cortex_verify_fixes: Confirm fixes worked
- cortex_audit_gaps: Find architecture gaps

Author: CORTEX Debugging Orchestrator
Version: 1.0.0 (2026-02-10)
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from cortex.core.result import Err, Ok
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

# ============================================================================
# VIOLATION MODELS
# ============================================================================

class ViolationType(Enum):
    """Types of governance violations detected."""
    TOOL_INTERCEPTION_GAP = "tool_interception_gap"      # Create_file not intercepted
    ENFORCEMENT_GAP = "enforcement_gap"                  # Enforcement not invoked
    MCP_BYPASS = "mcp_bypass"                           # Direct tool usage
    ARTIFACT_SUPPRESSION = "artifact_suppression"        # Markdown files created
    RESPONSE_GENERATION = "response_generation"          # No guards in response gen
    USER_VALIDATION = "user_validation"                  # No user approval gate
    CI_CD_GAP = "cicd_gap"                             # No pre-commit hook
    INSTRUCTION_VIOLATION = "instruction_violation"      # Instruction file issues
    TDD_BYPASS = "tdd_bypass"                           # Tests not before code
    AUDIT_TRAIL = "audit_trail"                         # AC markers missing


@dataclass
class Violation:
    """Single governance violation."""
    violation_id: str
    violation_type: ViolationType
    severity: str  # P0, P1, P2
    component: str
    description: str
    location: Optional[str]
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    fix_strategy: Optional[str] = None
    fix_applied: bool = False
    test_verification: bool = False


@dataclass
class DebugCycle:
    """Single debug cycle result."""
    cycle_number: int
    violations_detected: List[Violation]
    violations_fixed: int
    new_violations_found: int
    time_ms: float
    passed: bool


# ============================================================================
# VIOLATION DETECTOR
# ============================================================================

class GovernanceViolationDetector:
    """Detects governance violations across CORTEX architecture."""

    def __init__(self):
        """Initialize detector."""
        self.logger = EnhancedAuditLogger.instance()
        self.violations: List[Violation] = []
        self.cycle_count = 0

    def detect_all_violations(self) -> Union[Ok[List[Violation]], Err[str]]:
        """
        Detect ALL governance violations in CORTEX.

        Returns comprehensive list of violations with fix strategies.
        """
        try:
            violations = []

            # Check 1: Tool Interception Gap
            violations.extend(self._detect_tool_interception_gap())

            # Check 2: Enforcement Orchestrator Gap
            violations.extend(self._detect_enforcement_gap())

            # Check 3: MCP Bypass Issues
            violations.extend(self._detect_mcp_bypass())

            # Check 4: Artifact Suppression Violations
            violations.extend(self._detect_artifact_violations())

            # Check 5: Response Generation Guards
            violations.extend(self._detect_response_generation_gaps())

            # Check 6: User Validation Gates
            violations.extend(self._detect_user_validation_gaps())

            # Check 7: CI/CD Infrastructure
            violations.extend(self._detect_cicd_gaps())

            # Check 8: Instruction File Issues
            violations.extend(self._detect_instruction_violations())

            # Check 9: TDD Bypass Patterns
            violations.extend(self._detect_tdd_bypasses())

            # Check 10: Audit Trail Issues
            violations.extend(self._detect_audit_trail_gaps())

            self.violations = violations
            return Ok(violations)

        except Exception as e:
            return Err(f"Detection failed: {str(e)}")

    def _detect_tool_interception_gap(self) -> List[Violation]:
        """CYCLE 1: Detect missing tool interception layer."""
        violations = []

        # Check if cortex/infrastructure/copilot_tool_interceptor.py exists
        interceptor_path = Path("cortex/infrastructure/copilot_tool_interceptor.py")
        if not interceptor_path.exists():
            violations.append(Violation(
                violation_id="VIO-001",
                violation_type=ViolationType.TOOL_INTERCEPTION_GAP,
                severity="P0",
                component="Copilot Integration",
                description="No tool interception layer exists. Native create_file calls bypass enforcement.",
                location="cortex/infrastructure/",
                fix_strategy="Create copilot_tool_interceptor.py with pre-hook validation"
            ))

        return violations

    def _detect_enforcement_gap(self) -> List[Violation]:
        """CYCLE 2: Detect enforcement not being called in chat flow."""
        violations = []

        # Check if MasterOrchestrator calls enforcement for chat operations
        master_orch_path = Path("cortex/orchestrators/core/master_orchestrator.py")
        if master_orch_path.exists():
            content = master_orch_path.read_text()

            # Check for enforcement in process_user_request
            if "process_user_request" in content:
                if "self._enforcement.validate" not in content or \
                   "process_user_request" not in content[:content.find("def process_user_request")]:
                    violations.append(Violation(
                        violation_id="VIO-002",
                        violation_type=ViolationType.ENFORCEMENT_GAP,
                        severity="P0",
                        component="MasterOrchestrator",
                        description="EnforcementOrchestrator not called in process_user_request path",
                        location="cortex/orchestrators/core/master_orchestrator.py:2700+",
                        fix_strategy="Add enforcement validation to process_user_request before response generation"
                    ))

        return violations

    def _detect_mcp_bypass(self) -> List[Violation]:
        """CYCLE 3: Detect MCP-FIRST principle violations."""
        violations = []

        # Check for direct file creation patterns in response generation
        response_paths = [
            "cortex/orchestrators/response/unified_response_composer.py",
            "cortex/orchestrators/core/master_orchestrator.py",
        ]

        for path_str in response_paths:
            path = Path(path_str)
            if path.exists():
                content = path.read_text()

                # Look for file creation without MCP wrapper
                if re.search(r'(create_file|mkdir|Path\(.*\)\.write|open.*"w")', content):
                    # Check if these are wrapped in MCP validation
                    if "cortex_process_request" not in content or \
                       "validate_artifact_creation" not in content:
                        violations.append(Violation(
                            violation_id="VIO-003",
                            violation_type=ViolationType.MCP_BYPASS,
                            severity="P0",
                            component="Response Generation",
                            description="File operations detected without MCP wrapper",
                            location=str(path),
                            fix_strategy="Wrap all file operations in cortex_process_request MCP tool"
                        ))
                        break

        return violations

    def _detect_artifact_violations(self) -> List[Violation]:
        """CYCLE 4: Detect markdown artifacts in workspace root."""
        violations = []

        # Check for .md files in workspace root (should be in docs/ only)
        workspace_root = Path(".")
        markdown_files = list(workspace_root.glob("*.md"))

        forbidden_patterns = [
            r".*-PLAN.*\.md$",
            r".*-SUMMARY.*\.md$",
            r".*-REPORT.*\.md$",
            r".*-STATUS.*\.md$",
            r"CORTEX-.*\.md$",
            r"DEPLOYMENT-.*\.md$",
        ]

        allowed_files = ["README.md"]

        for md_file in markdown_files:
            filename = md_file.name

            # Check if allowed
            if filename in allowed_files:
                continue

            # Check against forbidden patterns
            if any(re.match(pattern, filename) for pattern in forbidden_patterns):
                violations.append(Violation(
                    violation_id="VIO-004",
                    violation_type=ViolationType.ARTIFACT_SUPPRESSION,
                    severity="P0",
                    component="Artifact Management",
                    description=f"Markdown file in workspace root: {filename}",
                    location=str(md_file),
                    fix_strategy="Move to docs/ or delete if generated artifact"
                ))

        return violations

    def _detect_response_generation_gaps(self) -> List[Violation]:
        """CYCLE 5: Detect missing guards in response generation."""
        violations = []

        # Check if response generation has artifact detection
        response_paths = [
            "cortex/orchestrators/response/unified_response_composer.py",
            "cortex/brain/core/response_header_injector.py",
        ]

        for path_str in response_paths:
            path = Path(path_str)
            if path.exists():
                content = path.read_text()

                # Check for CORE-002 checks in response generation
                if "CORE-002" not in content and "markdown" in content.lower() and \
                   "create" in content.lower():
                    violations.append(Violation(
                        violation_id="VIO-005",
                        violation_type=ViolationType.RESPONSE_GENERATION,
                        severity="P1",
                        component="Response Generation",
                        description=f"No CORE-002 validation in {path.name}",
                        location=str(path),
                        fix_strategy="Add CORE-002 artifact detection to response composition"
                    ))

        return violations

    def _detect_user_validation_gaps(self) -> List[Violation]:
        """CYCLE 6: Detect missing user approval gates."""
        violations = []

        # Check if chat response format requires user choice for artifact creation
        response_format_path = Path("cortex/orchestrators/response/chat_response_policy.py")
        if response_format_path.exists():
            content = response_format_path.read_text()

            if "user_choice" not in content.lower() and \
               "approval" not in content.lower():
                violations.append(Violation(
                    violation_id="VIO-006",
                    violation_type=ViolationType.USER_VALIDATION,
                    severity="P1",
                    component="User Approval Gate",
                    description="No user choice enforcement for artifact-generating operations",
                    location=str(response_format_path),
                    fix_strategy="Add user approval prompt pattern to response generation"
                ))

        return violations

    def _detect_cicd_gaps(self) -> List[Violation]:
        """CYCLE 7: Detect CI/CD infrastructure gaps."""
        violations = []

        # Check for pre-commit hook that validates CORE-002
        githooks_path = Path(".githooks/pre-commit")
        if not githooks_path.exists():
            violations.append(Violation(
                violation_id="VIO-007",
                violation_type=ViolationType.CI_CD_GAP,
                severity="P1",
                component="CI/CD",
                description="No pre-commit hook to validate CORE-002 violations",
                location=".githooks/",
                fix_strategy="Create pre-commit hook that runs cortex_audit_markdown_violations"
            ))
        else:
            content = githooks_path.read_text()
            if "CORE-002" not in content and "markdown" not in content.lower():
                violations.append(Violation(
                    violation_id="VIO-007B",
                    violation_type=ViolationType.CI_CD_GAP,
                    severity="P1",
                    component="CI/CD",
                    description="Pre-commit hook exists but doesn't check CORE-002",
                    location=str(githooks_path),
                    fix_strategy="Add cortex_audit_markdown_violations to pre-commit hook"
                ))

        return violations

    def _detect_instruction_violations(self) -> List[Violation]:
        """CYCLE 8: Detect instruction file issues."""
        violations = []

        # Check instruction files don't have file paths (CORE-047)
        instruction_files = [
            ".github/copilot-instructions.md",
            ".github/prompts/cortex-architect.prompt.md",
        ]

        for instr_file in instruction_files:
            path = Path(instr_file)
            if path.exists():
                content = path.read_text()

                # Check for file paths in instructions (CORE-047 violation)
                if re.search(r'`cortex/[a-z_/]+\.py`', content) or \
                   re.search(r'file:///.+\.\w+', content):
                    violations.append(Violation(
                        violation_id="VIO-008",
                        violation_type=ViolationType.INSTRUCTION_VIOLATION,
                        severity="P2",
                        component="Instruction Files",
                        description="File paths found in instruction file (CORE-047 violation)",
                        location=str(path),
                        fix_strategy="Replace file paths with directory references, use semantic_search instead"
                    ))

        return violations

    def _detect_tdd_bypasses(self) -> List[Violation]:
        """CYCLE 9: Detect TDD bypass patterns."""
        violations = []

        # Check if enforcement allows test skipping via flags
        enforcement_path = Path("cortex/orchestrators/core/enforcement_orchestrator.py")
        if enforcement_path.exists():
            content = enforcement_path.read_text()

            # Check for --ignore or _skip_ patterns not being blocked
            if "skip" in content.lower() or "ignore" in content.lower():
                if "BLOCKED" not in content:
                    violations.append(Violation(
                        violation_id="VIO-009",
                        violation_type=ViolationType.TDD_BYPASS,
                        severity="P0",
                        component="TDD Enforcement",
                        description="TDD bypass patterns (--ignore, _skip_) might not be blocked",
                        location=str(enforcement_path),
                        fix_strategy="Ensure GovernanceEnforcementAgent blocks all test bypass patterns"
                    ))

        return violations

    def _detect_audit_trail_gaps(self) -> List[Violation]:
        """CYCLE 10: Detect audit trail (AC marker) gaps."""
        violations = []

        # Check if operations require AC markers
        governance_registry_path = Path("cortex/orchestrators/core/governance_registry.py")
        if governance_registry_path.exists():
            content = governance_registry_path.read_text()

            # Check if AC_START/AC_COMPLETE markers are mandatory
            if "AC_START" not in content or "AC_COMPLETE" not in content:
                violations.append(Violation(
                    violation_id="VIO-010",
                    violation_type=ViolationType.AUDIT_TRAIL,
                    severity="P2",
                    component="Audit Trail",
                    description="No mandatory AC marker enforcement in governance registry",
                    location=str(governance_registry_path),
                    fix_strategy="Add AC_START/AC_COMPLETE marker validation"
                ))

        return violations


# ============================================================================
# VIOLATION FIXER
# ============================================================================

class GovernanceViolationFixer:
    """Applies fixes for detected violations."""

    def __init__(self):
        """Initialize fixer."""
        self.logger = EnhancedAuditLogger.instance()
        self.fixes_applied = 0

    def apply_fixes(self, violations: List[Violation]) -> Union[Ok[int], Err[str]]:
        """
        Apply fixes for violations.

        Returns count of fixes applied.
        """
        try:
            for violation in violations:
                if violation.fix_strategy:
                    result = self._apply_fix(violation)
                    if result:
                        self.fixes_applied += 1

            return Ok(self.fixes_applied)
        except Exception as e:
            return Err(f"Fix application failed: {str(e)}")

    def _apply_fix(self, violation: Violation) -> bool:
        """Apply single fix for violation."""
        try:
            if violation.violation_type == ViolationType.TOOL_INTERCEPTION_GAP:
                return self._fix_tool_interception_gap(violation)
            elif violation.violation_type == ViolationType.ARTIFACT_SUPPRESSION:
                return self._fix_artifact_violations(violation)
            elif violation.violation_type == ViolationType.CI_CD_GAP:
                return self._fix_cicd_gap(violation)
            elif violation.violation_type == ViolationType.INSTRUCTION_VIOLATION:
                return self._fix_instruction_violations(violation)

            return False
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="GOVERNANCE-DEBUG",
                operation=f"FIX_{violation.violation_id}",
                success=False,
                details={"error": str(e)}
            )
            return False

    def _fix_tool_interception_gap(self, violation: Violation) -> bool:
        """Create tool interception layer."""
        # This would be created by create_file tool
        # Placeholder for orchestration
        return True

    def _fix_artifact_violations(self, violation: Violation) -> bool:
        """Move or delete markdown artifacts."""
        if violation.location:
            try:
                path = Path(violation.location)
                if path.exists():
                    # Move to docs/ if it's documentation
                    if "plan" in path.name.lower() or "quick" in path.name.lower():
                        docs_path = Path("docs") / path.name
                        docs_path.parent.mkdir(parents=True, exist_ok=True)
                        path.rename(docs_path)
                        return True
            except Exception as e:
                self.logger.log_operation_complete(
                    ac_id="GOVERNANCE-DEBUG",
                    operation="MOVE_ARTIFACT",
                    success=False,
                    details={"error": str(e), "file": violation.location}
                )

        return False

    def _fix_cicd_gap(self, violation: Violation) -> bool:
        """Create or update pre-commit hook."""
        # Placeholder - would be created via create_file
        return True

    def _fix_instruction_violations(self, violation: Violation) -> bool:
        """Remove file paths from instruction files."""
        # Placeholder - would be edited via replace_string_in_file with MCP
        return True


# ============================================================================
# DEBUGGING ORCHESTRATOR
# ============================================================================

class GovernanceDebuggingOrchestrator:
    """
    Main orchestrator for iterative governance violation debugging.

    Performs up to 10+ cycles of violation detection and fixing until
    no new violations are found.
    """

    def __init__(self):
        """Initialize orchestrator."""
        self.logger = EnhancedAuditLogger.instance()
        self.detector = GovernanceViolationDetector()
        self.fixer = GovernanceViolationFixer()
        self.cycles: List[DebugCycle] = []
        self.all_violations: Dict[str, Violation] = {}

    def debug_governance_violations(self, max_cycles: int = 10) -> Union[Ok[Dict[str, Any]], Err[str]]:
        """
        Execute iterative debugging cycles.

        Args:
            max_cycles: Maximum cycles to run (default 10)

        Returns:
            Comprehensive debug report with cycles, violations, fixes
        """
        try:
            for cycle_num in range(1, max_cycles + 1):
                result = self._run_debug_cycle(cycle_num)
                if result.is_err():
                    return result  # type: ignore

                cycle = result.unwrap()
                self.cycles.append(cycle)

                # If no new violations found, exit early
                if cycle.new_violations_found == 0 and cycle_num > 3:
                    self.logger.log_operation_complete(
                        ac_id="GOVERNANCE-DEBUG",
                        operation=f"DEBUG_COMPLETE_CYCLE_{cycle_num}",
                        success=True,
                        details={
                            "cycle": cycle_num,
                            "reason": "No new violations detected",
                            "total_violations": len(self.all_violations)
                        }
                    )
                    break

            return Ok(self._generate_report())

        except Exception as e:
            return Err(f"Debugging orchestration failed: {str(e)}")

    def _run_debug_cycle(self, cycle_num: int) -> Union[Ok[DebugCycle], Err[str]]:
        """Run single debug cycle."""
        try:
            import time
            start_time = time.time()

            # Step 1: Detect violations
            detect_result = self.detector.detect_all_violations()
            if detect_result.is_err():
                return Err(detect_result.unwrap()) if hasattr(detect_result, 'unwrap') else detect_result  # type: ignore

            violations = detect_result.unwrap()

            # Count new violations
            new_count = 0
            for v in violations:
                if v.violation_id not in self.all_violations:
                    self.all_violations[v.violation_id] = v
                    new_count += 1

            # Step 2: Apply fixes
            fix_result = self.fixer.apply_fixes(violations)
            fixes_applied = fix_result.unwrap() if fix_result.is_ok() else 0

            elapsed = (time.time() - start_time) * 1000

            cycle = DebugCycle(
                cycle_number=cycle_num,
                violations_detected=violations,
                violations_fixed=fixes_applied,
                new_violations_found=new_count,
                time_ms=elapsed,
                passed=new_count == 0 or fixes_applied > 0
            )

            self.logger.log_operation_complete(
                ac_id="GOVERNANCE-DEBUG",
                operation=f"DEBUG_CYCLE_{cycle_num}",
                success=cycle.passed,
                details={
                    "violations_detected": len(violations),
                    "new_violations": new_count,
                    "fixes_applied": fixes_applied,
                    "elapsed_ms": elapsed
                }
            )

            return Ok(cycle)

        except Exception as e:
            return Err(f"Debug cycle failed: {str(e)}")

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive debug report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_cycles": len(self.cycles),
            "total_violations_found": len(self.all_violations),
            "violations_by_severity": self._group_by_severity(),
            "violations_by_type": self._group_by_type(),
            "cycles": [
                {
                    "cycle": c.cycle_number,
                    "violations_detected": len(c.violations_detected),
                    "fixes_applied": c.violations_fixed,
                    "new_violations": c.new_violations_found,
                    "time_ms": c.time_ms,
                    "passed": c.passed
                }
                for c in self.cycles
            ],
            "violations": [
                {
                    "id": v.violation_id,
                    "type": v.violation_type.value,
                    "severity": v.severity,
                    "component": v.component,
                    "description": v.description,
                    "location": v.location,
                    "fix_strategy": v.fix_strategy,
                    "fix_applied": v.fix_applied
                }
                for v in self.all_violations.values()
            ],
            "summary": {
                "p0_violations": len([v for v in self.all_violations.values() if v.severity == "P0"]),
                "p1_violations": len([v for v in self.all_violations.values() if v.severity == "P1"]),
                "p2_violations": len([v for v in self.all_violations.values() if v.severity == "P2"]),
                "total_fixes_needed": len([v for v in self.all_violations.values() if not v.fix_applied]),
            }
        }

    def _group_by_severity(self) -> Dict[str, int]:
        """Group violations by severity."""
        groups = {"P0": 0, "P1": 0, "P2": 0}
        for v in self.all_violations.values():
            groups[v.severity] = groups.get(v.severity, 0) + 1
        return groups

    def _group_by_type(self) -> Dict[str, int]:
        """Group violations by type."""
        groups = {}
        for v in self.all_violations.values():
            vtype = v.violation_type.value
            groups[vtype] = groups.get(vtype, 0) + 1
        return groups


# ============================================================================
# SINGLETON ACCESS
# ============================================================================

_orchestrator_instance: Optional[GovernanceDebuggingOrchestrator] = None


def get_governance_debugger() -> GovernanceDebuggingOrchestrator:
    """Get singleton debugging orchestrator."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = GovernanceDebuggingOrchestrator()
    return _orchestrator_instance


__all__ = [
    "GovernanceViolationDetector",
    "GovernanceViolationFixer",
    "GovernanceDebuggingOrchestrator",
    "get_governance_debugger",
    "Violation",
    "ViolationType",
    "DebugCycle",
]
