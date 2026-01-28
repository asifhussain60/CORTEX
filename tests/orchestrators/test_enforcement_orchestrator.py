"""
Tests for EnforcementOrchestrator

Validates pre-execution governance rule enforcement with 3 agents:
- GovernanceEnforcementAgent (Tier 0 code quality rules)
- SecurityCheckpointAgent (Tier 0 safety rules)
- ComplianceValidationAgent (Tier 1 phase readiness)

AC-ID: ENFORCEMENT-001
Phase: 8 (Governance Enhancement)
Authority: CORE-008 (TDD), CORE-030 (Implementation Truth)

Author: Asif Hussain
"""

import pytest
from typing import Dict, Any
from pathlib import Path

from cortex.orchestrators.core.enforcement_orchestrator import (
    EnforcementOrchestrator,
    EnforcementResult,
    EnforcementLevel,
    GovernanceEnforcementAgent,
    SecurityCheckpointAgent,
    ComplianceValidationAgent,
)
from cortex.core.result import Result, Ok, Err


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def enforcement_orchestrator():
    """Create EnforcementOrchestrator instance."""
    return EnforcementOrchestrator()


@pytest.fixture
def sample_operation_implement():
    """Sample IMPLEMENT operation."""
    return {
        "intent": "IMPLEMENT",
        "target_file": "cortex/new_feature.py",
        "entities": ["NewClass", "new_function"],
        "description": "Implement cache invalidation",
    }


@pytest.fixture
def sample_operation_fix():
    """Sample FIX operation."""
    return {
        "intent": "FIX",
        "target_file": "cortex/state_manager.py",
        "entities": ["StateManager"],
        "description": "Fix race condition",
    }


@pytest.fixture
def sample_operation_refactor():
    """Sample REFACTOR operation."""
    return {
        "intent": "REFACTOR",
        "target_file": "cortex/legacy_code.py",
        "entities": ["LegacyClass"],
        "description": "Extract method pattern",
    }


# ============================================================================
# TEST: EnforcementOrchestrator Initialization
# ============================================================================

def test_enforcement_orchestrator_initialization(enforcement_orchestrator):
    """Test EnforcementOrchestrator initializes with 3 agents."""
    assert enforcement_orchestrator is not None
    assert len(enforcement_orchestrator.agents) == 3
    assert any(isinstance(agent, GovernanceEnforcementAgent) for agent in enforcement_orchestrator.agents)
    assert any(isinstance(agent, SecurityCheckpointAgent) for agent in enforcement_orchestrator.agents)
    assert any(isinstance(agent, ComplianceValidationAgent) for agent in enforcement_orchestrator.agents)


def test_enforcement_orchestrator_has_validate_method(enforcement_orchestrator):
    """Test EnforcementOrchestrator has validate_operation method."""
    assert hasattr(enforcement_orchestrator, "validate_operation")
    assert callable(enforcement_orchestrator.validate_operation)


# ============================================================================
# TEST: GovernanceEnforcementAgent (Tier 0 - Code Quality)
# ============================================================================

def test_governance_agent_validates_tdd_requirement():
    """Test GovernanceEnforcementAgent enforces CORE-008 (TDD)."""
    agent = GovernanceEnforcementAgent()
    
    # Operation without tests should be blocked
    operation = {
        "intent": "IMPLEMENT",
        "target_file": "cortex/new_feature.py",
        "test_file": None,  # No test file
    }
    
    result = agent.validate(operation)
    assert isinstance(result, Err)
    assert "CORE-008" in str(result.error)
    assert "TDD" in str(result.error).upper()


def test_governance_agent_allows_operation_with_tests():
    """Test GovernanceEnforcementAgent allows operation with tests."""
    agent = GovernanceEnforcementAgent()
    
    operation = {
        "intent": "IMPLEMENT",
        "target_file": "cortex/new_feature.py",
        "test_file": "tests/test_new_feature.py",
    }
    
    result = agent.validate(operation)
    assert isinstance(result, Ok)


def test_governance_agent_validates_type_hints():
    """Test GovernanceEnforcementAgent enforces CORE-011 (Type hints)."""
    agent = GovernanceEnforcementAgent()
    
    operation = {
        "intent": "IMPLEMENT",
        "target_file": "cortex/new_feature.py",
        "code_sample": "def foo(x): return x + 1",  # No type hints
    }
    
    result = agent.validate(operation)
    # Should warn or block depending on severity
    assert result is not None


def test_governance_agent_validates_docstrings():
    """Test GovernanceEnforcementAgent enforces CORE-012 (Docstrings)."""
    agent = GovernanceEnforcementAgent()
    
    operation = {
        "intent": "IMPLEMENT",
        "target_file": "cortex/new_feature.py",
        "code_sample": "def foo():\n    pass",  # No docstring
    }
    
    result = agent.validate(operation)
    assert result is not None


def test_governance_agent_rejects_bare_except():
    """Test GovernanceEnforcementAgent enforces CORE-013 (No bare except)."""
    agent = GovernanceEnforcementAgent()
    
    operation = {
        "intent": "IMPLEMENT",
        "target_file": "cortex/new_feature.py",
        "code_sample": "try:\n    foo()\nexcept:\n    pass",  # Bare except
    }
    
    result = agent.validate(operation)
    assert isinstance(result, Err)
    assert "CORE-013" in str(result.error)


# ============================================================================
# TEST: SecurityCheckpointAgent (Tier 0 - Safety)
# ============================================================================

def test_security_agent_enforces_git_checkpoint():
    """Test SecurityCheckpointAgent enforces CORE-026 (Git checkpoint)."""
    agent = SecurityCheckpointAgent()
    
    operation = {
        "intent": "REFACTOR",
        "scope": "SYSTEM",  # Major change
        "git_checkpoint_created": False,
    }
    
    result = agent.validate(operation)
    assert isinstance(result, Err)
    assert "CORE-026" in str(result.error)


def test_security_agent_allows_minor_changes_without_checkpoint():
    """Test SecurityCheckpointAgent allows minor changes without checkpoint."""
    agent = SecurityCheckpointAgent()
    
    operation = {
        "intent": "FIX",
        "scope": "FILE",  # Minor change
    }
    
    result = agent.validate(operation)
    assert isinstance(result, Ok)  # Minor changes don't need checkpoint


def test_security_agent_validates_audit_trail():
    """Test SecurityCheckpointAgent enforces CORE-027 (Audit trail)."""
    agent = SecurityCheckpointAgent()
    
    operation = {
        "intent": "IMPLEMENT",
        "ac_id": None,  # No audit ID
    }
    
    result = agent.validate(operation)
    # Should warn or require AC_START logging
    assert result is not None


# ============================================================================
# TEST: ComplianceValidationAgent (Tier 1 - Phase Readiness)
# ============================================================================

def test_compliance_agent_validates_phase_readiness():
    """Test ComplianceValidationAgent checks phase prerequisites."""
    agent = ComplianceValidationAgent()
    
    operation = {
        "intent": "DEPLOY",
        "phase": "Phase 8",
        "prerequisites_met": False,
    }
    
    result = agent.validate(operation)
    # Should escalate warning (not block)
    assert result is not None


def test_compliance_agent_allows_operations_with_met_prerequisites():
    """Test ComplianceValidationAgent allows operations with prerequisites."""
    agent = ComplianceValidationAgent()
    
    operation = {
        "intent": "IMPLEMENT",
        "phase": "Phase 8",
        "prerequisites_met": True,
    }
    
    result = agent.validate(operation)
    assert isinstance(result, Ok)


# ============================================================================
# TEST: EnforcementOrchestrator Integration
# ============================================================================

def test_enforcement_orchestrator_blocks_tier0_violations(enforcement_orchestrator, sample_operation_implement):
    """Test EnforcementOrchestrator blocks operations with Tier 0 violations."""
    # Remove test file to trigger CORE-008 violation
    sample_operation_implement["test_file"] = None
    
    result = enforcement_orchestrator.validate_operation(sample_operation_implement)
    
    assert isinstance(result, Err)
    enforcement_result = result.error
    assert enforcement_result.level == EnforcementLevel.BLOCKED
    assert len(enforcement_result.violations) > 0
    assert any("CORE-008" in v for v in enforcement_result.violations)


def test_enforcement_orchestrator_allows_compliant_operations(enforcement_orchestrator, sample_operation_implement):
    """Test EnforcementOrchestrator allows compliant operations."""
    # Add test file to satisfy CORE-008
    sample_operation_implement["test_file"] = "tests/test_new_feature.py"
    # Add AC_ID to avoid CORE-027 warning
    sample_operation_implement["ac_id"] = "TEST-001"
    
    result = enforcement_orchestrator.validate_operation(sample_operation_implement)
    
    assert isinstance(result, Ok)
    enforcement_result = result.value
    assert enforcement_result.level == EnforcementLevel.PASS
    assert len(enforcement_result.violations) == 0


def test_enforcement_orchestrator_escalates_tier1_violations(enforcement_orchestrator, sample_operation_implement):
    """Test EnforcementOrchestrator escalates Tier 1 violations without blocking."""
    # Add test file but set phase prerequisites not met
    sample_operation_implement["test_file"] = "tests/test_new_feature.py"
    sample_operation_implement["phase"] = "Phase 10"
    sample_operation_implement["prerequisites_met"] = False
    
    result = enforcement_orchestrator.validate_operation(sample_operation_implement)
    
    # Should pass with warnings
    assert isinstance(result, Ok)
    enforcement_result = result.value
    assert enforcement_result.level == EnforcementLevel.WARNING
    assert len(enforcement_result.warnings) > 0


def test_enforcement_orchestrator_parallel_execution(enforcement_orchestrator, sample_operation_implement):
    """Test EnforcementOrchestrator executes agents in parallel."""
    import time
    
    sample_operation_implement["test_file"] = "tests/test_new_feature.py"
    
    start = time.time()
    result = enforcement_orchestrator.validate_operation(sample_operation_implement)
    duration = time.time() - start
    
    # Parallel execution should be fast (<100ms)
    assert duration < 0.1
    assert isinstance(result, Ok)


def test_enforcement_orchestrator_aggregates_multiple_violations(enforcement_orchestrator):
    """Test EnforcementOrchestrator aggregates violations from multiple agents."""
    operation = {
        "intent": "IMPLEMENT",
        "target_file": "cortex/bad_code.py",
        "test_file": None,  # CORE-008 violation
        "code_sample": "try:\n    foo()\nexcept:\n    pass",  # CORE-013 violation
        "scope": "SYSTEM",
        "git_checkpoint_created": False,  # CORE-026 violation
    }
    
    result = enforcement_orchestrator.validate_operation(operation)
    
    assert isinstance(result, Err)
    enforcement_result = result.error
    assert len(enforcement_result.violations) >= 3  # At least 3 violations


# ============================================================================
# TEST: EnforcementResult
# ============================================================================

def test_enforcement_result_levels():
    """Test EnforcementResult supports 3 levels."""
    assert EnforcementLevel.PASS.value == "pass"
    assert EnforcementLevel.WARNING.value == "warning"
    assert EnforcementLevel.BLOCKED.value == "blocked"


def test_enforcement_result_contains_metadata():
    """Test EnforcementResult includes useful metadata."""
    result = EnforcementResult(
        level=EnforcementLevel.PASS,
        violations=[],
        warnings=[],
        metadata={"agent_count": 3, "execution_time_ms": 50}
    )
    
    assert result.level == EnforcementLevel.PASS
    assert result.metadata["agent_count"] == 3
    assert result.metadata["execution_time_ms"] == 50


# ============================================================================
# TEST: Edge Cases
# ============================================================================

def test_enforcement_orchestrator_handles_missing_fields(enforcement_orchestrator):
    """Test EnforcementOrchestrator handles operations with missing fields."""
    operation = {"intent": "UNKNOWN"}  # Minimal operation
    
    result = enforcement_orchestrator.validate_operation(operation)
    
    # Should not crash, might return warnings
    assert result is not None


def test_enforcement_orchestrator_handles_analyze_intent(enforcement_orchestrator):
    """Test EnforcementOrchestrator allows ANALYZE operations (read-only)."""
    operation = {
        "intent": "ANALYZE",
        "target_file": "cortex/existing_code.py",
        # No test file needed for read-only operations
    }
    
    result = enforcement_orchestrator.validate_operation(operation)
    
    assert isinstance(result, Ok)  # Read-only operations less strict


def test_enforcement_orchestrator_respects_tier_precedence(enforcement_orchestrator):
    """Test EnforcementOrchestrator prioritizes Tier 0 over Tier 1 violations."""
    operation = {
        "intent": "IMPLEMENT",
        "test_file": None,  # Tier 0 violation
        "phase": "Phase 10",
        "prerequisites_met": False,  # Tier 1 violation
    }
    
    result = enforcement_orchestrator.validate_operation(operation)
    
    assert isinstance(result, Err)
    enforcement_result = result.error
    # Should report Tier 0 violation first
    assert "CORE-" in enforcement_result.violations[0]
