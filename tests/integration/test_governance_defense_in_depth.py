"""
Integration Tests: Governance Defense-in-Depth (4-Layer Enforcement)

Tests end-to-end enforcement system validating that CORE rules cannot
be bypassed at any layer.

Test Coverage:
- Layer 1: Pre-execution gate validation
- Layer 2: Runtime monitoring and circuit breaker
- Layer 4: Production readiness enforcement check
- End-to-End: Full defense-in-depth workflow

AC-ID: REM-003-INTEGRATION-TESTS
Phase: 16 (Remediation Framework)
Author: Asif Hussain
"""

import pytest
from typing import Dict, Any
from cortex.orchestrators.core.enforcement_orchestrator import (
    EnforcementOrchestrator,
    EnforcementResult,
    EnforcementLevel,
)
from cortex.brain.core.state_manager import StateManager
from cortex.brain.production.readiness_assessment import (
    ProductionReadinessAssessment,
    ProductionTier,
)


class TestLayer1PreExecutionGate:
    """Test Layer 1: Pre-Execution Gate (EnforcementOrchestrator)."""
    
    def test_validate_intent_classification_success(self):
        """Test intent classification validation with complete fields."""
        orchestrator = EnforcementOrchestrator()
        
        intent_reflection = {
            "intent_type": "IMPLEMENT",
            "target_handler": "TDDOrchestrator",
            "dor_confidence": 0.85,
            "scope": "MODULE",
            "governance_rules": ["CORE-008", "CORE-011"],
            "business_principles": {
                "Quality First": "TDD (CORE-008)",
                "Maintainability": "Type Safety (CORE-011)",
            },
        }
        
        result = orchestrator.validate_intent_classification(intent_reflection)
        
        assert result.is_ok()
        assert result.value == []
    
    def test_validate_intent_classification_missing_fields(self):
        """Test intent classification validation with missing required fields."""
        orchestrator = EnforcementOrchestrator()
        
        intent_reflection = {
            "intent_type": "IMPLEMENT",
            # Missing: target_handler, dor_confidence, scope
        }
        
        result = orchestrator.validate_intent_classification(intent_reflection)
        
        assert result.is_err()
        violations = result.error
        assert len(violations) >= 3
        assert any("target_handler" in v for v in violations)
        assert any("dor_confidence" in v for v in violations)
        assert any("scope" in v for v in violations)
    
    def test_validate_intent_classification_missing_business_principles(self):
        """Test validation fails when governance rules present but principles missing."""
        orchestrator = EnforcementOrchestrator()
        
        intent_reflection = {
            "intent_type": "IMPLEMENT",
            "target_handler": "TDDOrchestrator",
            "dor_confidence": 0.85,
            "scope": "MODULE",
            "governance_rules": ["CORE-008", "CORE-011"],
            "business_principles": {},  # Empty!
        }
        
        result = orchestrator.validate_intent_classification(intent_reflection)
        
        assert result.is_err()
        violations = result.error
        assert any("business_principles not populated" in v for v in violations)
    
    def test_validate_dor_confidence_justified(self):
        """Test DoR confidence validation with sufficient context."""
        orchestrator = EnforcementOrchestrator()
        
        result = orchestrator.validate_dor_confidence(
            promised_confidence=0.80,
            intent_type="IMPLEMENT",
            available_context={
                "target_file_exists": True,
                "test_file_exists": True,
                "similar_patterns_found": True,
                "clear_requirements": True,
                "dependencies_known": False,
            },
        )
        
        assert result.is_ok()
        assert result.value == []
    
    def test_validate_dor_confidence_artificially_inflated(self):
        """Test DoR confidence validation detects manipulation."""
        orchestrator = EnforcementOrchestrator()
        
        result = orchestrator.validate_dor_confidence(
            promised_confidence=0.95,  # Very high!
            intent_type="IMPLEMENT",
            available_context={
                "target_file_exists": False,
                "test_file_exists": False,
                "similar_patterns_found": False,
                "clear_requirements": False,
                "dependencies_known": False,
            },  # No context = 0.0 quality
        )
        
        assert result.is_err()
        violations = result.error
        assert any("suspiciously high" in v for v in violations)
    
    def test_validate_dor_confidence_too_low(self):
        """Test DoR confidence validation enforces minimums."""
        orchestrator = EnforcementOrchestrator()
        
        result = orchestrator.validate_dor_confidence(
            promised_confidence=0.40,  # Too low for IMPLEMENT
            intent_type="IMPLEMENT",
            available_context={
                "target_file_exists": True,
                "test_file_exists": False,
            },
        )
        
        assert result.is_err()
        violations = result.error
        assert any("too low for IMPLEMENT" in v for v in violations)
    
    def test_validate_business_principles_mapping_success(self):
        """Test business principles mapping validation."""
        orchestrator = EnforcementOrchestrator()
        
        result = orchestrator.validate_business_principles_mapping(
            governance_rules=["CORE-008", "CORE-011"],
            business_principles={
                "Quality First": "TDD (CORE-008)",
                "Maintainability": "Type Safety (CORE-011)",
            },
        )
        
        assert result.is_ok()
        assert result.value == []
    
    def test_validate_business_principles_mapping_incomplete(self):
        """Test validation detects unmapped rules."""
        orchestrator = EnforcementOrchestrator()
        
        result = orchestrator.validate_business_principles_mapping(
            governance_rules=["CORE-008", "CORE-011", "CORE-012"],
            business_principles={
                "Quality First": "TDD (CORE-008)",
                # Missing CORE-011 and CORE-012
            },
        )
        
        assert result.is_err()
        violations = result.error
        assert any("not mapped" in v for v in violations)


class TestLayer2RuntimeMonitoring:
    """Test Layer 2: Runtime Monitoring (StateManager)."""
    
    def test_track_governance_violation(self):
        """Test tracking governance violations during runtime."""
        state_mgr = StateManager()
        
        # Create operation
        state = state_mgr.create_operation("test_op_001", "Test operation")
        
        # Track violations
        success = state_mgr.track_governance_violation(
            operation_id="test_op_001",
            rule_id="CORE-008",
            severity="CRITICAL",
            description="Test file missing before implementation",
        )
        
        assert success is True
        
        # Verify violation tracked
        violation_count = state_mgr.get_violation_count("test_op_001")
        assert violation_count == 1
    
    def test_circuit_breaker_threshold(self):
        """Test circuit breaker trips after 3 violations."""
        state_mgr = StateManager()
        
        # Create operation
        state = state_mgr.create_operation("test_op_002", "Test operation")
        
        # Track 3 violations
        for i in range(3):
            state_mgr.track_governance_violation(
                operation_id="test_op_002",
                rule_id=f"CORE-00{i+8}",
                severity="CRITICAL",
                description=f"Violation {i+1}",
            )
        
        # Circuit breaker should be tripped
        assert state_mgr.is_circuit_breaker_tripped("test_op_002") is True
        
        # Violation count should be 3
        assert state_mgr.get_violation_count("test_op_002") == 3
    
    def test_circuit_breaker_not_tripped_below_threshold(self):
        """Test circuit breaker does not trip below threshold."""
        state_mgr = StateManager()
        
        # Create operation
        state = state_mgr.create_operation("test_op_003", "Test operation")
        
        # Track only 2 violations
        for i in range(2):
            state_mgr.track_governance_violation(
                operation_id="test_op_003",
                rule_id=f"CORE-00{i+8}",
                severity="HIGH",
                description=f"Violation {i+1}",
            )
        
        # Circuit breaker should NOT be tripped
        assert state_mgr.is_circuit_breaker_tripped("test_op_003") is False
    
    def test_get_statistics_includes_governance_metrics(self):
        """Test statistics include governance violation metrics."""
        state_mgr = StateManager()
        
        # Create operations with violations
        state1 = state_mgr.create_operation("test_op_004", "Test 1")
        state2 = state_mgr.create_operation("test_op_005", "Test 2")
        
        # Add violations
        state_mgr.track_governance_violation("test_op_004", "CORE-008", "CRITICAL", "Test")
        state_mgr.track_governance_violation("test_op_004", "CORE-011", "HIGH", "Test")
        state_mgr.track_governance_violation("test_op_005", "CORE-012", "MEDIUM", "Test")
        
        stats = state_mgr.get_statistics()
        
        assert "governance_violations_total" in stats
        assert stats["governance_violations_total"] >= 3
        assert "circuit_breakers_tripped" in stats


class TestLayer4ProductionReadinessGate:
    """Test Layer 4: Production Readiness Gate."""
    
    def test_enforcement_integrity_check_passes(self):
        """Test enforcement integrity check passes when all layers operational."""
        assessment = ProductionReadinessAssessment()
        
        check = assessment.check_enforcement_integrity()
        
        assert check.status == "PASS"
        assert "All 4 layers operational" in check.details
        assert check.severity == "critical"
    
    def test_production_readiness_includes_enforcement(self):
        """Test production readiness assessment includes enforcement check."""
        assessment = ProductionReadinessAssessment()
        
        results = assessment.run_all_checks()
        
        # Find enforcement check
        enforcement_check = None
        for check in results:
            if "Enforcement System Integrity" in check.name:
                enforcement_check = check
                break
        
        assert enforcement_check is not None
        assert enforcement_check.check_id == "PROD-CHECK-004"
        assert enforcement_check.severity == "critical"


class TestEndToEndDefenseInDepth:
    """Test end-to-end defense-in-depth workflow."""
    
    def test_complete_enforcement_workflow(self):
        """Test complete workflow from validation to production gate."""
        # Layer 1: Pre-Execution Validation
        enforcement = EnforcementOrchestrator()
        
        intent_reflection = {
            "intent_type": "IMPLEMENT",
            "target_handler": "TDDOrchestrator",
            "dor_confidence": 0.85,
            "scope": "MODULE",
            "governance_rules": ["CORE-008"],
            "business_principles": {"Quality First": "TDD (CORE-008)"},
        }
        
        layer1_result = enforcement.validate_intent_classification(intent_reflection)
        assert layer1_result.is_ok(), "Layer 1 should pass validation"
        
        # Layer 2: Runtime Monitoring
        state_mgr = StateManager()
        operation = state_mgr.create_operation("e2e_test_001", "End-to-end test")
        
        # Simulate violation during execution
        state_mgr.track_governance_violation(
            "e2e_test_001", "CORE-011", "MEDIUM", "Type hint missing"
        )
        
        violation_count = state_mgr.get_violation_count("e2e_test_001")
        assert violation_count == 1, "Layer 2 should track violations"
        
        # Layer 4: Production Readiness
        assessment = ProductionReadinessAssessment()
        enforcement_check = assessment.check_enforcement_integrity()
        
        assert enforcement_check.status == "PASS", "Layer 4 should validate system integrity"
    
    def test_enforcement_blocks_invalid_intent(self):
        """Test that invalid intent is blocked at Layer 1."""
        enforcement = EnforcementOrchestrator()
        
        # Invalid: Missing required fields
        invalid_intent = {
            "intent_type": "IMPLEMENT",
            # Missing everything else
        }
        
        result = enforcement.validate_intent_classification(invalid_intent)
        
        assert result.is_err(), "Layer 1 should block invalid intent"
        assert len(result.error) >= 3, "Should report multiple violations"
    
    def test_circuit_breaker_prevents_cascade(self):
        """Test that circuit breaker stops operation after threshold."""
        state_mgr = StateManager()
        
        # Create operation
        operation = state_mgr.create_operation("cascade_test", "Cascade prevention test")
        
        # Simulate multiple violations
        violations = [
            ("CORE-008", "Test file missing"),
            ("CORE-011", "Type hints missing"),
            ("CORE-012", "Docstring missing"),
            ("CORE-013", "Bare except used"),
        ]
        
        for i, (rule_id, desc) in enumerate(violations):
            state_mgr.track_governance_violation(
                "cascade_test", rule_id, "CRITICAL", desc
            )
            
            # Check if circuit breaker tripped
            if state_mgr.is_circuit_breaker_tripped("cascade_test"):
                # Should trip after 3rd violation
                assert i >= 2, "Circuit breaker should trip after 3 violations"
                break
        
        # Verify final state
        assert state_mgr.is_circuit_breaker_tripped("cascade_test") is True
        assert state_mgr.get_violation_count("cascade_test") >= 3


class TestPerformanceBenchmarks:
    """Performance benchmarks for enforcement system."""
    
    def test_layer1_validation_performance(self):
        """Test Layer 1 validation completes in <100ms."""
        import time
        
        enforcement = EnforcementOrchestrator()
        
        intent_reflection = {
            "intent_type": "IMPLEMENT",
            "target_handler": "TDDOrchestrator",
            "dor_confidence": 0.85,
            "scope": "MODULE",
            "governance_rules": ["CORE-008", "CORE-011", "CORE-012"],
            "business_principles": {
                "Quality First": "TDD (CORE-008)",
                "Maintainability": "Type Safety (CORE-011)",
                "Documentation": "Docstrings (CORE-012)",
            },
        }
        
        start = time.perf_counter()
        
        # Run all 3 validations
        enforcement.validate_intent_classification(intent_reflection)
        enforcement.validate_dor_confidence(0.85, "IMPLEMENT", {
            "target_file_exists": True,
            "test_file_exists": True,
            "similar_patterns_found": True,
            "clear_requirements": True,
        })
        enforcement.validate_business_principles_mapping(
            ["CORE-008", "CORE-011", "CORE-012"],
            intent_reflection["business_principles"],
        )
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Should complete in <100ms
        assert elapsed_ms < 100, f"Layer 1 validation took {elapsed_ms:.2f}ms (target: <100ms)"
    
    def test_layer2_tracking_performance(self):
        """Test Layer 2 violation tracking is fast."""
        import time
        
        state_mgr = StateManager()
        operation = state_mgr.create_operation("perf_test", "Performance test")
        
        start = time.perf_counter()
        
        # Track 10 violations
        for i in range(10):
            state_mgr.track_governance_violation(
                "perf_test", f"CORE-{i:03d}", "MEDIUM", f"Test violation {i}"
            )
        
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        # Should be fast (arbitrary threshold: 50ms for 10 violations)
        assert elapsed_ms < 50, f"Layer 2 tracking took {elapsed_ms:.2f}ms for 10 violations"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
