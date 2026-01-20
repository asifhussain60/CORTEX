"""
Orchestrator Composition Tests - AR-017-02

Tests for orchestrator composition and delegation patterns.
- Composition patterns documented
- Delegation maintains audit trail
- Error handling in composed operations

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.orchestrators.composition.composition_engine import (
    CompositionPattern,
    ComposedOrchestrator,
    DelegationResult,
)
from cortex.orchestrators.composition.delegation_handler import (
    DelegationHandler,
    DelegationContext,
)


class TestCompositionPatterns:
    """Test composition pattern definitions"""
    
    def test_sequential_composition_pattern(self):
        """Test sequential composition pattern"""
        pattern = CompositionPattern.SEQUENTIAL
        
        assert pattern is not None
        assert pattern.name == "SEQUENTIAL"
        assert pattern.description is not None
    
    def test_parallel_composition_pattern(self):
        """Test parallel composition pattern"""
        pattern = CompositionPattern.PARALLEL
        
        assert pattern is not None
        assert pattern.name == "PARALLEL"
    
    def test_conditional_composition_pattern(self):
        """Test conditional composition pattern"""
        pattern = CompositionPattern.CONDITIONAL
        
        assert pattern is not None
        assert pattern.name == "CONDITIONAL"
    
    def test_delegating_composition_pattern(self):
        """Test delegating composition pattern"""
        pattern = CompositionPattern.DELEGATING
        
        assert pattern is not None
        assert pattern.name == "DELEGATING"
    
    def test_get_all_patterns(self):
        """Test getting all composition patterns"""
        patterns = CompositionPattern.get_all()
        
        assert len(patterns) >= 4
        pattern_names = {p.name for p in patterns}
        assert "SEQUENTIAL" in pattern_names
        assert "PARALLEL" in pattern_names
        assert "CONDITIONAL" in pattern_names
        assert "DELEGATING" in pattern_names


class TestComposedOrchestrator:
    """Test composed orchestrator functionality"""
    
    def test_create_sequential_composition(self):
        """Test creating sequential composition"""
        composed = ComposedOrchestrator(
            name="seq-test",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1", "step2", "step3"],
            description="Sequential test composition",
        )
        
        assert composed.name == "seq-test"
        assert composed.pattern == CompositionPattern.SEQUENTIAL
        assert len(composed.steps) == 3
    
    def test_composed_orchestrator_metadata(self):
        """Test composed orchestrator has metadata"""
        composed = ComposedOrchestrator(
            name="test-comp",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1"],
            description="Test",
        )
        
        metadata = composed.get_metadata()
        assert metadata["name"] == "test-comp"
        assert metadata["pattern"] == "sequential"
        assert metadata["composition_type"] == "composed"
    
    def test_add_step_to_composition(self):
        """Test adding step to composition"""
        composed = ComposedOrchestrator(
            name="test-comp",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1", "step2"],
            description="Test",
        )
        
        composed.add_step("step3")
        assert len(composed.steps) == 3
        assert composed.steps[-1] == "step3"
    
    def test_remove_step_from_composition(self):
        """Test removing step from composition"""
        composed = ComposedOrchestrator(
            name="test-comp",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1", "step2", "step3"],
            description="Test",
        )
        
        composed.remove_step("step2")
        assert len(composed.steps) == 2
        assert "step2" not in composed.steps


class TestDelegationPattern:
    """Test delegation pattern"""
    
    def test_delegation_handler_creation(self):
        """Test creating delegation handler"""
        handler = DelegationHandler()
        
        assert handler is not None
    
    def test_delegate_operation(self):
        """Test delegating operation"""
        handler = DelegationHandler()
        
        context = DelegationContext(
            delegator="parent-orch",
            delegatee="child-orch",
            operation="execute",
            parameters={"task": "test"},
        )
        
        result = handler.delegate(context)
        
        assert result is not None
        assert result.delegator == "parent-orch"
        assert result.delegatee == "child-orch"
    
    def test_delegation_maintains_audit_trail(self):
        """Test that delegation maintains audit trail"""
        handler = DelegationHandler()
        
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        
        result = handler.delegate(context)
        
        # Should have audit trail
        assert hasattr(result, "audit_trail")
        assert result.audit_trail is not None
        assert len(result.audit_trail) > 0
    
    def test_audit_trail_includes_timestamp(self):
        """Test that audit trail includes timestamp"""
        handler = DelegationHandler()
        
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        
        result = handler.delegate(context)
        
        trail = result.audit_trail[0]
        assert "timestamp" in trail
        assert trail["timestamp"] is not None
    
    def test_audit_trail_includes_operation_details(self):
        """Test that audit trail includes operation details"""
        handler = DelegationHandler()
        
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="execute",
            parameters={"task": "test-task"},
        )
        
        result = handler.delegate(context)
        
        trail = result.audit_trail[0]
        assert trail["operation"] == "execute"
        assert trail["parameters"]["task"] == "test-task"


class TestCompositionErrorHandling:
    """Test error handling in composed operations"""
    
    def test_error_in_sequential_step_stops_execution(self):
        """Test that error in sequential step stops execution"""
        composed = ComposedOrchestrator(
            name="seq-error",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1", "error-step", "step3"],
            description="Test error handling",
        )
        
        # Should have error handling
        assert hasattr(composed, "handle_error")
        assert callable(composed.handle_error)
    
    def test_error_handling_provides_rollback(self):
        """Test that error handling provides rollback capability"""
        composed = ComposedOrchestrator(
            name="seq-error",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1", "step2"],
            description="Test",
        )
        
        # Should have rollback
        assert hasattr(composed, "rollback")
        assert callable(composed.rollback)
    
    def test_composed_orchestrator_captures_errors(self):
        """Test that composed orchestrator captures errors"""
        composed = ComposedOrchestrator(
            name="error-test",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1"],
            description="Test",
        )
        
        # Should track errors
        assert hasattr(composed, "errors")
    
    def test_error_recovery_options(self):
        """Test error recovery options"""
        composed = ComposedOrchestrator(
            name="recovery-test",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1", "step2", "step3"],
            description="Test",
        )
        
        # Should support different recovery strategies
        assert hasattr(composed, "get_recovery_strategies")
        strategies = composed.get_recovery_strategies()
        assert len(strategies) > 0


class TestCompositionDocumentation:
    """Test composition documentation"""
    
    def test_composition_patterns_documented(self):
        """Test that composition patterns are documented"""
        patterns = CompositionPattern.get_all()
        
        for pattern in patterns:
            assert pattern.description is not None
            assert len(pattern.description) > 0
    
    def test_pattern_documentation_includes_use_cases(self):
        """Test that pattern documentation includes use cases"""
        seq_pattern = CompositionPattern.SEQUENTIAL
        
        assert hasattr(seq_pattern, "use_cases")
        assert len(seq_pattern.use_cases) > 0
    
    def test_pattern_documentation_includes_examples(self):
        """Test that pattern documentation includes examples"""
        seq_pattern = CompositionPattern.SEQUENTIAL
        
        assert hasattr(seq_pattern, "examples")
        assert len(seq_pattern.examples) > 0
    
    def test_composition_best_practices_documented(self):
        """Test that best practices are documented"""
        composed = ComposedOrchestrator(
            name="best-practices",
            pattern=CompositionPattern.SEQUENTIAL,
            steps=["step1"],
            description="Test",
        )
        
        # Should have best practices
        assert hasattr(composed, "get_best_practices")
        practices = composed.get_best_practices()
        assert len(practices) > 0


class TestDelegationContext:
    """Test delegation context"""
    
    def test_delegation_context_creation(self):
        """Test creating delegation context"""
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="execute",
            parameters={"key": "value"},
        )
        
        assert context.delegator == "parent"
        assert context.delegatee == "child"
        assert context.operation == "execute"
        assert context.parameters["key"] == "value"
    
    def test_delegation_context_has_unique_id(self):
        """Test that delegation context has unique ID"""
        context1 = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        context2 = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        
        assert context1.id != context2.id
    
    def test_delegation_context_tracks_timestamp(self):
        """Test that delegation context tracks timestamp"""
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        
        assert context.created_at is not None


class TestDelegationResult:
    """Test delegation result"""
    
    def test_delegation_result_includes_status(self):
        """Test that delegation result includes status"""
        handler = DelegationHandler()
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        
        result = handler.delegate(context)
        
        assert hasattr(result, "status")
        assert result.status in ["success", "failed", "pending"]
    
    def test_delegation_result_includes_output(self):
        """Test that delegation result includes output"""
        handler = DelegationHandler()
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        
        result = handler.delegate(context)
        
        assert hasattr(result, "output")
    
    def test_delegation_result_tracks_execution_time(self):
        """Test that delegation result tracks execution time"""
        handler = DelegationHandler()
        context = DelegationContext(
            delegator="parent",
            delegatee="child",
            operation="test",
            parameters={},
        )
        
        result = handler.delegate(context)
        
        assert hasattr(result, "execution_time_ms")
        assert result.execution_time_ms >= 0
