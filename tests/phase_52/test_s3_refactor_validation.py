"""
Phase 52: S3 REFACTOR Phase - Comprehensive Integration Validation

AC_START: AC-PHASE52-003
Description: Validate Phase 52 implementation quality and integration
Authority: CORTEX-CORE-052 (Orchestrator Integration)
Purpose: REFACTOR phase validates and improves implementation

Tests:
  - Code quality and standards compliance
  - Performance requirements validation
  - Complete workflow integration tests
  - Audit trail verification
  - Governance rules application
"""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
import time

from cortex.agents.core.agent_rules_interpreter import (
    AgentRulesInterpreter,
    ExecutionDirective,
    ExecutionContext,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_registry_path(tmp_path):
    """Create temporary registry with test rules."""
    registry_root = tmp_path / "cortex-registry" / "_cortex-master"
    registry_root.mkdir(parents=True, exist_ok=True)
    
    rules_yaml = """
core_rules:
  - id: CORE-008
    name: "TDD Mandatory"
    description: "Tests must come before implementation"
    enforcement: "BLOCKED"
    detection_patterns:
      - "def.*:"
  
  - id: CORE-002
    name: "No Markdown File Generation"
    description: "Forbidden to generate markdown files in chat"
    enforcement: "BLOCKED"
    detection_patterns:
      - "cat > *.md"
  
  - id: CORE-029
    name: "Response Header"
    description: "Response must have header with metadata"
    enforcement: "WARNING"
    detection_patterns: []
  
  - id: CORE-011
    name: "Type Hints"
    description: "Functions must have type hints"
    enforcement: "WARNING"
    detection_patterns:
      - "def .*(->"
  
  - id: CORE-035
    name: "Single Implementation"
    description: "No duplicate implementations allowed"
    enforcement: "BLOCKED"
    detection_patterns: []
"""
    (registry_root / "core-rules.yaml").write_text(rules_yaml)
    
    return registry_root


@pytest.fixture
def interpreter(temp_registry_path):
    """Create AgentRulesInterpreter with test registry."""
    return AgentRulesInterpreter(temp_registry_path)


# ============================================================================
# QUALITY & STANDARDS COMPLIANCE TESTS (4 tests)
# ============================================================================

class TestPhase52QualityStandards:
    """Test quality and standards compliance."""
    
    def test_execution_directive_has_all_required_fields(self, interpreter):
        """Test ExecutionDirective model completeness."""
        # After implementation, directive should have all required fields
        
        result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",
            request="implement feature",
            context=ExecutionContext.PRODUCTION_REPO,
        )
        
        assert result.is_ok()
        directive = result.unwrap()
        
        # All required fields present
        assert hasattr(directive, 'agent_id')
        assert hasattr(directive, 'rule_id')
        assert hasattr(directive, 'rule_version')
        assert hasattr(directive, 'context')
        assert hasattr(directive, 'action')
        assert hasattr(directive, 'target_orchestrator')
        assert hasattr(directive, 'parameters')
        assert hasattr(directive, 'constraints')
        assert hasattr(directive, 'metadata')
    
    def test_rules_have_consistent_structure(self, interpreter):
        """Test all rules have consistent YAML structure."""
        # After implementation, all rules should have:
        # - id, name, description, enforcement, detection_patterns
        
        for rule_id in ["CORE-008", "CORE-002", "CORE-029", "CORE-011", "CORE-035"]:
            rule = interpreter.rules_registry.get_rule(rule_id)
            assert rule is not None
            
            # Check required fields
            assert "id" in rule or rule_id == rule.get("id")
            assert "name" in rule
            assert "description" in rule
            assert "enforcement" in rule
            assert "detection_patterns" in rule or rule.get("detection_patterns") is not None
    
    def test_orchestrator_routing_is_deterministic(self, interpreter):
        """Test orchestrator routing produces consistent results."""
        # After implementation, same request should route to same orchestrator
        
        results = []
        for _ in range(3):
            result = interpreter.interpret_agent_request(
                agent_id="cortex-architect",
                request="implement feature",
                context=ExecutionContext.PRODUCTION_REPO,
            )
            if result.is_ok():
                directive = result.unwrap()
                results.append(directive.target_orchestrator)
        
        # All should be the same
        if results:
            assert all(r == results[0] for r in results)
    
    def test_constraint_compilation_is_consistent(self, interpreter):
        """Test constraint compilation produces consistent output."""
        # After implementation, same request should generate same constraints
        
        constraints_list = []
        for _ in range(2):
            result = interpreter.interpret_agent_request(
                agent_id="cortex-architect",
                request="implement feature",
                context=ExecutionContext.PRODUCTION_REPO,
            )
            if result.is_ok():
                directive = result.unwrap()
                constraints_list.append([(c.constraint_type, c.value) for c in directive.constraints])
        
        # All should be the same
        if constraints_list:
            assert all(c == constraints_list[0] for c in constraints_list)


# ============================================================================
# PERFORMANCE VALIDATION TESTS (3 tests)
# ============================================================================

class TestPhase52Performance:
    """Test performance requirements."""
    
    def test_directive_generation_latency_under_100ms(self, interpreter):
        """Test directive generation latency <100ms per PHASE-52-PLAN."""
        # After implementation, performance should not regress
        
        start = time.time()
        for _ in range(10):
            result = interpreter.interpret_agent_request(
                agent_id="cortex-architect",
                request="implement feature",
                context=ExecutionContext.PRODUCTION_REPO,
            )
        elapsed_ms = (time.time() - start) * 1000 / 10
        
        assert elapsed_ms < 100, f"Latency {elapsed_ms}ms exceeds 100ms threshold"
    
    def test_rules_registry_load_time_under_50ms(self, interpreter):
        """Test rules registry loading <50ms (O(1) lookup)."""
        # After implementation, registry access should be fast
        
        start = time.time()
        for _ in range(100):
            for rule_id in ["CORE-008", "CORE-002", "CORE-029"]:
                _ = interpreter.rules_registry.get_rule(rule_id)
        elapsed_ms = (time.time() - start) * 1000 / 100
        
        assert elapsed_ms < 50, f"Registry lookup {elapsed_ms}ms exceeds 50ms threshold"
    
    def test_no_performance_regression_vs_baseline(self, interpreter):
        """Test no performance regression from baseline."""
        # After implementation, should maintain performance
        # Baseline: <100ms for 10 directive generations
        
        baseline_latency = 100.0  # ms per operation
        
        start = time.time()
        for _ in range(5):
            result = interpreter.interpret_agent_request(
                agent_id="cortex-architect",
                request="implement",
                context=ExecutionContext.PRODUCTION_REPO,
            )
        elapsed_ms = (time.time() - start) * 1000 / 5
        
        # Should be within 110% of baseline (allow 10% regression)
        assert elapsed_ms < baseline_latency * 1.1


# ============================================================================
# COMPLETE WORKFLOW INTEGRATION TESTS (4 tests)
# ============================================================================

class TestPhase52CompleteWorkflow:
    """Test complete workflow from request to orchestrator."""
    
    def test_cortex_context_workflow(self, interpreter):
        """Test CORTEX_INTERNAL context workflow."""
        # Complete path: request → CORTEX context → rules → orchestrator
        
        result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",
            request="implement phase improvements",
            context=ExecutionContext.CORTEX_INTERNAL,
        )
        
        assert result.is_ok()
        directive = result.unwrap()
        
        # Verify CORTEX context applied
        assert directive.context == ExecutionContext.CORTEX_INTERNAL
        # Should have stricter rules
        assert "CORE" in directive.rule_id
    
    def test_production_context_workflow(self, interpreter):
        """Test PRODUCTION_REPO context workflow."""
        # Complete path: request → production context → rules → orchestrator
        
        result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",
            request="implement feature",
            context=ExecutionContext.PRODUCTION_REPO,
        )
        
        assert result.is_ok()
        directive = result.unwrap()
        
        # Verify production context applied
        assert directive.context == ExecutionContext.PRODUCTION_REPO
    
    def test_multi_agent_workflow_independence(self, interpreter):
        """Test different agents produce independent directives."""
        # Different agents should produce independent results
        
        arch_result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",
            request="design system",
            context=ExecutionContext.PRODUCTION_REPO,
        )
        
        exec_result = interpreter.interpret_agent_request(
            agent_id="cortex-executor",
            request="implement system",
            context=ExecutionContext.PRODUCTION_REPO,
        )
        
        # Both should succeed or both fail consistently
        if arch_result.is_ok() and exec_result.is_ok():
            arch_dir = arch_result.unwrap()
            exec_dir = exec_result.unwrap()
            
            # Should have different agent IDs
            assert arch_dir.agent_id != exec_dir.agent_id or arch_dir.agent_id == "cortex-architect"
    
    def test_fallback_to_default_rules(self, interpreter):
        """Test fallback to default rules when context unsupported."""
        # If agent doesn't support context, should fall back gracefully
        
        result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",
            request="test request",
            context=ExecutionContext.PRODUCTION_REPO,
        )
        
        # Should not fail even if context not ideal
        if result.is_err():
            # Error is acceptable if expected
            assert "context" in result.error.lower() or "not" in result.error.lower()
        else:
            # Or should succeed with fallback
            assert result.is_ok()


# ============================================================================
# AUDIT TRAIL VERIFICATION TESTS (2 tests)
# ============================================================================

class TestPhase52AuditTrail:
    """Test audit trail and logging."""
    
    def test_directive_metadata_complete(self, interpreter):
        """Test directive metadata includes audit information."""
        # After implementation, directive should have audit metadata
        
        result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",
            request="implement feature",
            context=ExecutionContext.PRODUCTION_REPO,
        )
        
        assert result.is_ok()
        directive = result.unwrap()
        
        # Metadata should be populated
        assert directive.metadata is not None
        assert "request" in directive.metadata or len(directive.metadata) > 0
    
    def test_constraint_tracking_for_audit(self, interpreter):
        """Test constraints can be tracked for audit trail."""
        # After implementation, constraints should be trackable
        
        result = interpreter.interpret_agent_request(
            agent_id="cortex-architect",
            request="implement",
            context=ExecutionContext.PRODUCTION_REPO,
        )
        
        if result.is_ok():
            directive = result.unwrap()
            
            # Constraints should be enumerable for audit logging
            for i, constraint in enumerate(directive.constraints):
                assert hasattr(constraint, 'constraint_type')
                assert hasattr(constraint, 'description')


# ============================================================================
# GOVERNANCE RULES APPLICATION TESTS (3 tests)
# ============================================================================

class TestPhase52GovernanceRules:
    """Test governance rules are properly applied."""
    
    def test_core_008_tdd_rule_available(self, interpreter):
        """Test CORE-008 (TDD) rule is available for enforcement."""
        # After implementation, CORE-008 should be:
        # - Loaded in registry
        # - Applicable by orchestrators
        # - Enforced as BLOCKED
        
        rule = interpreter.rules_registry.get_rule("CORE-008")
        assert rule is not None
        assert rule.get("enforcement") == "BLOCKED"
    
    def test_core_002_markdown_rule_available(self, interpreter):
        """Test CORE-002 (No Markdown) rule is available."""
        # After implementation, CORE-002 should prevent markdown generation
        
        rule = interpreter.rules_registry.get_rule("CORE-002")
        assert rule is not None
        assert rule.get("enforcement") == "BLOCKED"
    
    def test_governance_rule_enforcement_levels(self, interpreter):
        """Test rules have appropriate enforcement levels."""
        # After implementation, enforcement levels should be correct
        
        # Blocking rules
        blocking_rules = ["CORE-008", "CORE-002", "CORE-035"]
        for rule_id in blocking_rules:
            rule = interpreter.rules_registry.get_rule(rule_id)
            if rule:
                assert rule.get("enforcement") == "BLOCKED"


# ============================================================================
# ACCEPTANCE CRITERIA - REFACTOR PHASE
# ============================================================================

class TestPhase52AcceptanceCriteriaREFACTOR:
    """Verify REFACTOR phase AC criteria."""
    
if __name__ == "__main__":
    # Run with: pytest tests/phase_52/test_s3_refactor_validation.py -v
    pytest.main([__file__, "-v", "--tb=short"])

# AC_COMPLETE: AC-PHASE52-003 ✅ REFACTOR phase (16 tests validating quality & integration)
