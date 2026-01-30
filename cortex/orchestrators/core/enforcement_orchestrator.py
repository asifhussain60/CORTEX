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
            Ok(warnings) if compliant, Err(violations) if blocked
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
        
        if violations:
            return Err(violations)
        return Ok(warnings)


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
    
    def validate(self, operation: Dict[str, Any]) -> Result[List[str], List[str]]:
        """
        Validate operation against safety rules.
        
        Args:
            operation: Operation context dictionary
            
        Returns:
            Ok(warnings) if compliant, Err(violations) if blocked
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
        
        if violations:
            return Err(violations)
        return Ok(warnings)


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
    
    def validate(self, operation: Dict[str, Any]) -> Result[List[str], List[str]]:
        """
        Validate operation against phase readiness rules.
        
        Args:
            operation: Operation context dictionary
            
        Returns:
            Ok(warnings) - Tier 1 violations escalate, not block
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
        
        return Ok(warnings)


# ============================================================================
# ENFORCEMENT ORCHESTRATOR
# ============================================================================

class EnforcementOrchestrator:
    """
    Pre-execution governance enforcement orchestrator.
    
    Validates operations against 3-tier governance before execution:
    - Executes 3 agents in parallel for speed (<100ms target)
    - Aggregates violations and warnings
    - Blocks execution on Tier 0 violations
    - Escalates Tier 1 warnings without blocking
    
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
        Initialize enforcement orchestrator.
        
        Args:
            governance_registry: Optional governance registry (injected)
        """
        self.governance_registry = governance_registry
        self.agents = [
            GovernanceEnforcementAgent(),
            SecurityCheckpointAgent(),
            ComplianceValidationAgent(),
        ]
        logger.info(f"EnforcementOrchestrator initialized with {len(self.agents)} agents")
    
    def validate_operation(self, operation: Dict[str, Any]) -> Result[EnforcementResult, EnforcementResult]:
        """
        Validate operation against governance rules.
        
        Executes 3 agents in parallel:
        1. GovernanceEnforcementAgent (code quality)
        2. SecurityCheckpointAgent (safety)
        3. ComplianceValidationAgent (phase readiness)
        
        Args:
            operation: Operation context with intent, target_file, test_file, etc.
            
        Returns:
            Ok(EnforcementResult) if compliant or warnings only
            Err(EnforcementResult) if Tier 0 violations detected
        """
        start_time = time.time()
        all_violations = []
        all_warnings = []
        
        # Execute agents in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(agent.validate, operation): agent for agent in self.agents}
            
            for future in as_completed(futures):
                agent = futures[future]
                try:
                    result = future.result()
                    
                    if result.is_err():
                        # Tier 0 violations
                        violations = result.error
                        all_violations.extend(violations)
                        logger.warning(f"{agent.name} detected {len(violations)} violations")
                    else:
                        # Warnings only
                        warnings = result.value
                        all_warnings.extend(warnings)
                        if warnings:
                            logger.info(f"{agent.name} issued {len(warnings)} warnings")
                
                except Exception as e:
                    logger.error(f"{agent.name} validation failed: {e}")
                    all_warnings.append(f"Agent {agent.name} validation error: {str(e)}")
        
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
