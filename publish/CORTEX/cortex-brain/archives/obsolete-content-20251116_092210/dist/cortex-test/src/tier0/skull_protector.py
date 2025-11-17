"""
SKULL Protection Layer - Safety, Knowledge, Validation & Learning Layer

Prevents development violations by enforcing test validation requirements.

Created: 2025-11-09
Trigger: CSS + Vision API testing failures incident
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger("cortex.skull")


class SkullRuleId(Enum):
    """SKULL protection rule identifiers."""
    TEST_BEFORE_CLAIM = "SKULL-001"
    INTEGRATION_VERIFICATION = "SKULL-002"
    VISUAL_REGRESSION = "SKULL-003"
    RETRY_WITHOUT_LEARNING = "SKULL-004"


class EnforcementLevel(Enum):
    """Enforcement levels for SKULL rules."""
    BLOCKING = "BLOCKING"  # Prevents execution
    WARNING = "WARNING"    # Warns but allows
    INFO = "INFO"          # Informational only


@dataclass
class SkullValidation:
    """Result of SKULL validation check."""
    passed: bool
    rule_id: Optional[SkullRuleId]
    rule_name: str
    message: str
    enforcement: EnforcementLevel
    tests_required: List[str]
    tests_found: List[str]


@dataclass
class FixValidationRequest:
    """Request to validate a fix against SKULL rules."""
    fix_type: str  # "css_change", "integration", "bug_fix", "feature", "refactor"
    tests_run: List[str]
    verification: Optional[Dict[str, Any]]
    description: str


class SkullProtector:
    """
    SKULL Protection Layer - Enforces quality standards and test requirements.
    
    The SKULL protects the CORTEX brain from untested changes, false claims,
    and quality degradation.
    """
    
    def __init__(self):
        """Initialize SKULL protector."""
        self.rules = self._load_rules()
        
    def _load_rules(self) -> Dict[SkullRuleId, Dict]:
        """Load SKULL protection rules."""
        return {
            SkullRuleId.TEST_BEFORE_CLAIM: {
                "name": "Test Before Claim",
                "description": "Never claim a fix is complete without test validation",
                "enforcement": EnforcementLevel.BLOCKING,
                "applies_to": ["bug_fix", "feature", "refactor", "css_change", "integration"]
            },
            SkullRuleId.INTEGRATION_VERIFICATION: {
                "name": "Integration Verification",
                "description": "Integration must be tested end-to-end",
                "enforcement": EnforcementLevel.BLOCKING,
                "applies_to": ["integration"]
            },
            SkullRuleId.VISUAL_REGRESSION: {
                "name": "Visual Regression",
                "description": "UI/CSS changes require visual validation",
                "enforcement": EnforcementLevel.WARNING,
                "applies_to": ["css_change", "ui_change"]
            },
            SkullRuleId.RETRY_WITHOUT_LEARNING: {
                "name": "Retry Without Learning",
                "description": "Must diagnose failures before retrying",
                "enforcement": EnforcementLevel.WARNING,
                "applies_to": ["bug_fix", "retry"]
            }
        }
    
    def validate_fix(self, request: FixValidationRequest) -> SkullValidation:
        """
        Validate a fix against SKULL protection rules.
        
        Args:
            request: Fix validation request with test info
            
        Returns:
            SkullValidation result
            
        Raises:
            SkullProtectionError: If BLOCKING rule violated
        """
        logger.info(f"[SKULL] Validating fix: {request.description}")
        
        # Check applicable rules
        violations = []
        
        for rule_id, rule_config in self.rules.items():
            if request.fix_type not in rule_config["applies_to"]:
                continue
                
            # Check rule
            validation = self._check_rule(rule_id, rule_config, request)
            
            if not validation.passed:
                violations.append(validation)
                
                # If blocking, fail immediately
                if validation.enforcement == EnforcementLevel.BLOCKING:
                    logger.error(f"[SKULL] BLOCKING violation: {validation.message}")
                    return validation
        
        # If warnings but no blocking violations
        if violations:
            # Return first warning
            return violations[0]
        
        # All checks passed
        logger.info(f"[SKULL] Validation passed: {request.description}")
        return SkullValidation(
            passed=True,
            rule_id=None,
            rule_name="All Rules",
            message="All SKULL protection checks passed",
            enforcement=EnforcementLevel.INFO,
            tests_required=[],
            tests_found=request.tests_run
        )
    
    def _check_rule(
        self, 
        rule_id: SkullRuleId, 
        rule_config: Dict,
        request: FixValidationRequest
    ) -> SkullValidation:
        """Check a specific SKULL rule."""
        
        if rule_id == SkullRuleId.TEST_BEFORE_CLAIM:
            return self._check_test_before_claim(rule_config, request)
            
        elif rule_id == SkullRuleId.INTEGRATION_VERIFICATION:
            return self._check_integration_verification(rule_config, request)
            
        elif rule_id == SkullRuleId.VISUAL_REGRESSION:
            return self._check_visual_regression(rule_config, request)
            
        elif rule_id == SkullRuleId.RETRY_WITHOUT_LEARNING:
            return self._check_retry_without_learning(rule_config, request)
        
        # Unknown rule - pass
        return SkullValidation(
            passed=True,
            rule_id=rule_id,
            rule_name=rule_config["name"],
            message="Rule check not implemented",
            enforcement=EnforcementLevel.INFO,
            tests_required=[],
            tests_found=[]
        )
    
    def _check_test_before_claim(
        self, 
        rule_config: Dict, 
        request: FixValidationRequest
    ) -> SkullValidation:
        """Check SKULL-001: Test Before Claim."""
        
        # Must have at least one test run
        if not request.tests_run:
            return SkullValidation(
                passed=False,
                rule_id=SkullRuleId.TEST_BEFORE_CLAIM,
                rule_name=rule_config["name"],
                message=f"SKULL-001 VIOLATION: No tests run for {request.fix_type}. "
                        f"Cannot claim fix is complete without test validation.",
                enforcement=rule_config["enforcement"],
                tests_required=["At least one automated test"],
                tests_found=[]
            )
        
        # Test validation present
        return SkullValidation(
            passed=True,
            rule_id=SkullRuleId.TEST_BEFORE_CLAIM,
            rule_name=rule_config["name"],
            message=f"SKULL-001 PASSED: {len(request.tests_run)} test(s) validated fix",
            enforcement=rule_config["enforcement"],
            tests_required=["At least one automated test"],
            tests_found=request.tests_run
        )
    
    def _check_integration_verification(
        self,
        rule_config: Dict,
        request: FixValidationRequest
    ) -> SkullValidation:
        """Check SKULL-002: Integration Verification."""
        
        # For integrations, need end-to-end test
        integration_tests = [
            t for t in request.tests_run 
            if "integration" in t.lower() or "e2e" in t.lower() or "end_to_end" in t.lower()
        ]
        
        if not integration_tests:
            return SkullValidation(
                passed=False,
                rule_id=SkullRuleId.INTEGRATION_VERIFICATION,
                rule_name=rule_config["name"],
                message=f"SKULL-002 VIOLATION: No end-to-end integration test for {request.description}. "
                        f"Integration must be tested across component boundaries.",
                enforcement=rule_config["enforcement"],
                tests_required=["End-to-end integration test"],
                tests_found=request.tests_run
            )
        
        return SkullValidation(
            passed=True,
            rule_id=SkullRuleId.INTEGRATION_VERIFICATION,
            rule_name=rule_config["name"],
            message=f"SKULL-002 PASSED: Integration verified by {len(integration_tests)} test(s)",
            enforcement=rule_config["enforcement"],
            tests_required=["End-to-end integration test"],
            tests_found=integration_tests
        )
    
    def _check_visual_regression(
        self,
        rule_config: Dict,
        request: FixValidationRequest
    ) -> SkullValidation:
        """Check SKULL-003: Visual Regression."""
        
        # For CSS/UI changes, need visual test or computed style verification
        visual_tests = [
            t for t in request.tests_run
            if any(keyword in t.lower() for keyword in ["visual", "css", "style", "computed", "browser"])
        ]
        
        if not visual_tests:
            return SkullValidation(
                passed=False,
                rule_id=SkullRuleId.VISUAL_REGRESSION,
                rule_name=rule_config["name"],
                message=f"SKULL-003 VIOLATION: No visual validation for {request.description}. "
                        f"CSS/UI changes require visual regression test or computed style verification.",
                enforcement=rule_config["enforcement"],
                tests_required=["Visual regression test or computed style check"],
                tests_found=request.tests_run
            )
        
        return SkullValidation(
            passed=True,
            rule_id=SkullRuleId.VISUAL_REGRESSION,
            rule_name=rule_config["name"],
            message=f"SKULL-003 PASSED: Visual regression verified by {len(visual_tests)} test(s)",
            enforcement=rule_config["enforcement"],
            tests_required=["Visual regression test or computed style check"],
            tests_found=visual_tests
        )
    
    def _check_retry_without_learning(
        self,
        rule_config: Dict,
        request: FixValidationRequest
    ) -> SkullValidation:
        """Check SKULL-004: Retry Without Learning."""
        
        # Check if this is a retry
        if request.fix_type != "retry":
            return SkullValidation(
                passed=True,
                rule_id=SkullRuleId.RETRY_WITHOUT_LEARNING,
                rule_name=rule_config["name"],
                message="SKULL-004 N/A: Not a retry attempt",
                enforcement=rule_config["enforcement"],
                tests_required=[],
                tests_found=[]
            )
        
        # For retries, verification must include diagnosis
        if not request.verification or "diagnosis" not in request.verification:
            return SkullValidation(
                passed=False,
                rule_id=SkullRuleId.RETRY_WITHOUT_LEARNING,
                rule_name=rule_config["name"],
                message=f"SKULL-004 VIOLATION: Retry without diagnosis for {request.description}. "
                        f"Must diagnose WHY previous fix failed before retrying.",
                enforcement=rule_config["enforcement"],
                tests_required=["Root cause diagnosis"],
                tests_found=[]
            )
        
        return SkullValidation(
            passed=True,
            rule_id=SkullRuleId.RETRY_WITHOUT_LEARNING,
            rule_name=rule_config["name"],
            message="SKULL-004 PASSED: Retry includes root cause diagnosis",
            enforcement=rule_config["enforcement"],
            tests_required=["Root cause diagnosis"],
            tests_found=["Diagnosis completed"]
        )


class SkullProtectionError(Exception):
    """Raised when a BLOCKING SKULL rule is violated."""
    
    def __init__(self, validation: SkullValidation):
        self.validation = validation
        super().__init__(validation.message)


def enforce_skull(request: FixValidationRequest) -> SkullValidation:
    """
    Convenience function to enforce SKULL protection.
    
    Args:
        request: Fix validation request
        
    Returns:
        SkullValidation result
        
    Raises:
        SkullProtectionError: If BLOCKING rule violated
    """
    skull = SkullProtector()
    validation = skull.validate_fix(request)
    
    if not validation.passed and validation.enforcement == EnforcementLevel.BLOCKING:
        raise SkullProtectionError(validation)
    
    return validation
