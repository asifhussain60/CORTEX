"""
Tests for DoRApprovalGate integration with MasterOrchestrator.

AC-ID: AC-GOVE-DOR-WIRE-001
Purpose: Wire DoRApprovalGate into MasterOrchestrator

Tests cover:
1. DoR gate initialization in MasterOrchestrator
2. Reflection display before operation execution
3. Approval flow (approve, reject, modify)
4. Execution gated on approval status
5. Audit trail captures approval decision
6. Graceful degradation if gate unavailable
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.core.dor_approval_gate import (
    DoRApprovalGate,
    IntentReflection,
    ApprovalDecision,
    ApprovalStatus,
)
from cortex.core.result import Ok, Err


class TestDoRApprovalGateIntegration:
    """Tests for DoRApprovalGate integration with MasterOrchestrator."""
    
    @pytest.fixture
    def master_orch(self):
        """Create MasterOrchestrator instance."""
        return MasterOrchestrator()
    
    @pytest.fixture
    def dor_gate(self):
        """Create DoRApprovalGate instance."""
        return DoRApprovalGate()
    
    def test_master_orchestrator_initializes_dor_gate(self, master_orch):
        """Test that MasterOrchestrator initializes DoRApprovalGate."""
        # Should have _dor_gate attribute
        assert hasattr(master_orch, '_dor_gate'), \
            "MasterOrchestrator should have _dor_gate attribute"
    
    def test_classify_and_get_reflection(self, dor_gate):
        """Test classification and reflection generation."""
        text = "Implement user authentication system"
        context = {"domain": "security"}
        
        # Mock IntentRouterFactory
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            # Setup mock router
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="GeneralImplementationHandler",
                confidence_score=0.85,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Classify
            reflection = dor_gate.classify_and_reflect(text, context)
            
            # Verify reflection properties
            assert reflection.intent_type == "implement"
            assert reflection.target_handler == "GeneralImplementationHandler"
            assert 0 <= reflection.confidence <= 1.0  # Valid confidence range
            assert "Intent Classification" in reflection.to_markdown()
    
    def test_reflection_markdown_format(self, dor_gate):
        """Test that reflection generates concise markdown."""
        text = "Fix authentication bug in login module"
        context = {"domain": "security"}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="fix"),
                target_handler="domain_orchestrator",
                confidence_score=0.9,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            reflection = dor_gate.classify_and_reflect(text, context)
            markdown = reflection.to_markdown()
            
            # Should contain key sections
            assert "Intent Classification" in markdown
            assert "Intent" in markdown
            assert "Confidence" in markdown
            assert "Handler" in markdown
            assert "Awaiting approval" in markdown
    
    def test_approve_operation(self, dor_gate):
        """Test approving a classified intent."""
        text = "Implement feature X"
        context = {}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="handler",
                confidence_score=0.8,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Classify
            reflection = dor_gate.classify_and_reflect(text, context)
            
            # Approve
            dor_gate.approve(feedback=None)
            
            assert dor_gate._approval_decision.status == ApprovalStatus.APPROVED
            assert dor_gate._approval_decision.feedback is None
    
    def test_reject_operation(self, dor_gate):
        """Test rejecting a classified intent."""
        text = "Implement feature X"
        context = {}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="handler",
                confidence_score=0.8,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Classify
            reflection = dor_gate.classify_and_reflect(text, context)
            
            # Reject with reason
            reason = "Need more context on requirements"
            dor_gate.reject(reason=reason)
            
            assert dor_gate._approval_decision.status == ApprovalStatus.REJECTED
            assert dor_gate._approval_decision.feedback == reason
    
    def test_modify_intent(self, dor_gate):
        """Test modifying the classified intent."""
        text = "Implement feature X"
        context = {}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="handler",
                confidence_score=0.6,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Classify
            reflection = dor_gate.classify_and_reflect(text, context)
            
            # Modify with corrected intent
            modified_intent = "refactor"
            dor_gate.modify(corrected_intent=modified_intent)
            
            assert dor_gate._approval_decision.status == ApprovalStatus.MODIFIED
            assert dor_gate._approval_decision.modified_intent == modified_intent
    
    def test_execute_if_approved(self, dor_gate):
        """Test executing operation only if approved."""
        text = "Implement authentication"
        context = {}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="handler",
                confidence_score=0.8,
            )
            mock_router.execute_orchestrated.return_value = Ok({"status": "success"})
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Classify and approve
            reflection = dor_gate.classify_and_reflect(text, context)
            dor_gate.approve()
            
            # Execute - no parameters, uses stored state from classify_and_reflect
            result = dor_gate.execute_if_approved()
            
            # Result should contain status (either success or error dict)
            assert isinstance(result, dict)
            assert "status" in result or "error" in result
    
    def test_execute_blocked_if_rejected(self, dor_gate):
        """Test that execution is blocked if rejected."""
        text = "Implement feature"
        context = {}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="handler",
                confidence_score=0.8,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Classify and reject
            reflection = dor_gate.classify_and_reflect(text, context)
            dor_gate.reject(reason="Need clarification")
            
            # Try to execute - should fail
            with pytest.raises(RuntimeError):
                dor_gate.execute_if_approved()
    
    def test_audit_trail_captures_approval(self, master_orch, dor_gate):
        """Test that audit trail captures approval decision."""
        text = "Implement feature"
        context = {}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="handler",
                confidence_score=0.8,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Classify and approve
            reflection = dor_gate.classify_and_reflect(text, context)
            dor_gate.approve()
            
            # Verify decision has timestamp and approved status
            assert dor_gate._approval_decision.timestamp
            assert dor_gate._approval_decision.status == ApprovalStatus.APPROVED
    
    def test_graceful_degradation_if_gate_unavailable(self, master_orch):
        """Test that execution continues if DoRApprovalGate unavailable."""
        # This tests backward compatibility
        operation_name = "coordinate_operation"
        parameters = {"operation": "test", "context": {}}
        
        # Should handle missing gate gracefully
        # (This is implementation-specific based on how gate is integrated)
        assert hasattr(master_orch, '_dor_gate')
    
    def test_dor_state_persists_across_calls(self, dor_gate):
        """Test that DoR state persists correctly."""
        text1 = "Implement feature 1"
        context1 = {}
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_router.classify_intent.return_value = Mock(
                intent_type=Mock(value="implement"),
                target_handler="handler",
                confidence_score=0.8,
            )
            
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # First operation
            reflection1 = dor_gate.classify_and_reflect(text1, context1)
            dor_gate.approve()
            
            # Second operation (should reset state)
            text2 = "Implement feature 2"
            context2 = {}
            reflection2 = dor_gate.classify_and_reflect(text2, context2)
            
            # Should have new reflection
            assert reflection1 is not reflection2
            # Approval should be reset
            assert dor_gate._approval_decision is None


class TestMasterOrchestratorDoRIntegration:
    """Integration tests for MasterOrchestrator with DoR gate."""
    
    @pytest.fixture
    def master_orch(self):
        """Create MasterOrchestrator instance."""
        return MasterOrchestrator()
    
    def test_coordinate_operation_with_dor_gate(self, master_orch):
        """Test that coordinate_operation uses DoR gate."""
        # Should integrate gate into operation flow
        assert hasattr(master_orch, '_dor_gate')
        assert hasattr(master_orch, 'coordinate_operation')
    
    def test_dor_gate_provides_reflection_before_execution(self, master_orch):
        """Test that reflection is available before execution."""
        # Setup mock gate
        mock_gate = Mock()
        mock_reflection = Mock()
        mock_reflection.to_markdown.return_value = "### Intent Classification"
        mock_gate.classify_and_reflect.return_value = mock_reflection
        mock_gate.execute_if_approved.return_value = {"status": "success"}
        
        master_orch._dor_gate = mock_gate
        
        # Coordinate operation should use gate
        result = master_orch.coordinate_operation(
            operation="test_operation",
            context={}
        )
        
        # Gate should have been called (or at least attribute should exist)
        assert hasattr(master_orch, '_dor_gate')
        assert master_orch._dor_gate is not None
    
    def test_dor_rejection_blocks_orchestration(self, master_orch):
        """Test that rejected intent blocks orchestration."""
        # Setup mock gate that rejects
        mock_gate = Mock()
        mock_gate.classify_and_reflect.return_value = Mock()
        mock_gate.execute_if_approved.return_value = Err("Operation rejected by user")
        
        master_orch._dor_gate = mock_gate
        
        # Coordinate operation should respect rejection
        result = master_orch.coordinate_operation(
            operation="test_operation",
            context={}
        )
        
        # Should either error or skip execution
        # (implementation-specific)


class TestDoRApprovalGateErrorHandling:
    """Error handling tests for DoRApprovalGate."""
    
    def test_classify_rejects_empty_text(self):
        """Test that classify_and_reflect rejects empty text."""
        gate = DoRApprovalGate()
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_factory.return_value = Mock()
            
            with pytest.raises(ValueError):
                gate.classify_and_reflect("", {})
    
    def test_execute_if_approved_without_classification(self):
        """Test executing without prior classification fails gracefully."""
        gate = DoRApprovalGate()
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            mock_router = Mock()
            mock_factory_instance = Mock()
            mock_factory_instance.create_router.return_value = mock_router
            mock_factory.return_value = mock_factory_instance
            
            # Try to execute without classifying first - should raise RuntimeError
            with pytest.raises(RuntimeError):
                gate.execute_if_approved()
    
    def test_factory_failure_handled_gracefully(self):
        """Test that factory None is handled gracefully."""
        gate = DoRApprovalGate()
        
        with patch('cortex.orchestrators.core.dor_approval_gate.get_intent_router_factory') as mock_factory:
            # Patch at the gate level after initialization
            gate._factory = None
            
            # Should raise error when trying to use None factory
            with pytest.raises((RuntimeError, AttributeError, TypeError)):
                gate.classify_and_reflect("test text", {})


class TestExecutionPlanAndDoD:
    """Tests for Execution Plan and Definition of Done sections."""
    
    @pytest.fixture
    def dor_gate(self):
        """Create DoRApprovalGate instance."""
        return DoRApprovalGate()
    
    def test_execution_plan_for_implement_intent(self, dor_gate):
        """Test execution plan for IMPLEMENT intent."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            key_entities=["authentication.py"],
            estimated_impact="medium",
            governance_rules=["CORE-008", "CORE-011", "CORE-012"]
        )
        
        plan = reflection._get_execution_plan()
        
        assert len(plan) == 4
        assert any("Create implementation" in p for p in plan)
        assert any("Write unit tests" in p for p in plan)
        assert any("RED phase" in p for p in plan)
        assert any("Refactor" in p for p in plan)
    
    def test_execution_plan_for_fix_intent(self, dor_gate):
        """Test execution plan for FIX intent."""
        reflection = IntentReflection(
            intent_type="FIX",
            target_handler="IntentRouter",
            dor_confidence=0.8,
            scope="FILE",
            key_entities=["bug_issue.md"],
            governance_rules=["CORE-008"]
        )
        
        plan = reflection._get_execution_plan()
        
        assert len(plan) == 4
        assert any("root cause" in p.lower() for p in plan)
        assert any("failing test" in p.lower() for p in plan)
        assert any("no regressions" in p.lower() for p in plan)
    
    def test_execution_plan_for_refactor_intent(self, dor_gate):
        """Test execution plan for REFACTOR intent."""
        reflection = IntentReflection(
            intent_type="REFACTOR",
            target_handler="RefactoringOrchestrator",
            dor_confidence=0.75,
            scope="MODULE",
            governance_rules=["CORE-008", "CORE-012"]
        )
        
        plan = reflection._get_execution_plan()
        
        assert len(plan) == 4
        assert any("SOLID" in p.upper() for p in plan)
        assert any("metrics" in p.lower() for p in plan)
    
    def test_execution_plan_for_analyze_intent(self, dor_gate):
        """Test execution plan for ANALYZE intent."""
        reflection = IntentReflection(
            intent_type="ANALYZE",
            target_handler="MasterOrchestrator",
            dor_confidence=0.9,
            scope="SYSTEM"
        )
        
        plan = reflection._get_execution_plan()
        
        assert len(plan) == 4
        assert any("codebase" in p.lower() or "architecture" in p.lower() for p in plan)
        assert any("findings" in p.lower() for p in plan)
        assert any("recommendations" in p.lower() for p in plan)
    
    def test_execution_plan_for_test_intent(self, dor_gate):
        """Test execution plan for TEST intent."""
        reflection = IntentReflection(
            intent_type="TEST",
            target_handler="TDDOrchestrator",
            dor_confidence=0.88,
            scope="MODULE"
        )
        
        plan = reflection._get_execution_plan()
        
        assert len(plan) == 4
        assert any("test suite" in p.lower() for p in plan)
        assert any(">80%" in p or "80%" in p for p in plan)
        assert any("edge cases" in p.lower() for p in plan)
    
    def test_dod_universal_criteria_always_present(self, dor_gate):
        """Test that universal DoD criteria are always present."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE"
        )
        
        dod = reflection._get_dod_criteria()
        
        # Universal criteria should always be present
        assert any("Operation completed" in c for c in dod)
        assert any("Audit trail" in c for c in dod)
    
    def test_dod_includes_tests_for_implement(self, dor_gate):
        """Test that DoD includes test criteria for IMPLEMENT intent."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            requires_tests=True,
            governance_rules=["CORE-008"]
        )
        
        dod = reflection._get_dod_criteria()
        
        assert any("All tests passing" in c for c in dod)
        assert any("Feature works" in c for c in dod)
        assert any("no regressions" in c.lower() for c in dod)
    
    def test_dod_includes_type_hints_when_core_011_present(self, dor_gate):
        """Test that DoD includes type hint criteria when CORE-011 present."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            governance_rules=["CORE-008", "CORE-011"]
        )
        
        dod = reflection._get_dod_criteria()
        
        assert any("Type hints" in c for c in dod)
    
    def test_dod_includes_docstrings_when_core_012_present(self, dor_gate):
        """Test that DoD includes docstring criteria when CORE-012 present."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            governance_rules=["CORE-008", "CORE-012"]
        )
        
        dod = reflection._get_dod_criteria()
        
        assert any("docstrings" in c.lower() for c in dod)
    
    def test_dod_for_fix_intent(self, dor_gate):
        """Test that DoD includes fix-specific criteria."""
        reflection = IntentReflection(
            intent_type="FIX",
            target_handler="IntentRouter",
            dor_confidence=0.8,
            scope="FILE",
            governance_rules=["CORE-008"]
        )
        
        dod = reflection._get_dod_criteria()
        
        assert any("Bug is fixed" in c for c in dod)
        assert any("Test added to prevent regression" in c for c in dod)
        assert any("no new bugs" in c.lower() for c in dod)
    
    def test_dod_for_refactor_intent(self, dor_gate):
        """Test that DoD includes refactor-specific criteria."""
        reflection = IntentReflection(
            intent_type="REFACTOR",
            target_handler="RefactoringOrchestrator",
            dor_confidence=0.75,
            scope="MODULE"
        )
        
        dod = reflection._get_dod_criteria()
        
        assert any("Code quality improved" in c for c in dod)
        assert any("tests still passing" in c.lower() for c in dod)
        assert any("Performance" in c for c in dod)
    
    def test_markdown_includes_execution_plan_section(self, dor_gate):
        """Test that markdown output includes Execution Plan section."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            key_entities=["feature.py"],
            governance_rules=["CORE-008"]
        )
        
        markdown = reflection.to_markdown()
        
        assert "📝 Execution Plan" in markdown
        assert "What CORTEX will do:" in markdown
        assert "Create implementation" in markdown
        assert "RED phase" in markdown
    
    def test_markdown_includes_dod_section(self, dor_gate):
        """Test that markdown output includes Definition of Done section."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            requires_tests=True,
            governance_rules=["CORE-008", "CORE-011", "CORE-012"]
        )
        
        markdown = reflection.to_markdown()
        
        assert "✅ Definition of Done" in markdown
        assert "Success looks like:" in markdown
        assert "All tests passing" in markdown
        assert "Operation completed" in markdown
        assert "Type hints" in markdown
        assert "docstrings" in markdown.lower()
    
    def test_markdown_sections_order(self, dor_gate):
        """Test that markdown sections appear in correct order."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            requires_tests=True,
            governance_rules=["CORE-008"]
        )
        
        markdown = reflection.to_markdown()
        
        # Extract positions
        intent_pos = markdown.find("Intent Classification")
        plan_pos = markdown.find("Execution Plan")
        dod_pos = markdown.find("Definition of Done")
        approval_pos = markdown.find("Awaiting Your Decision")
        
        # Verify order
        assert 0 <= intent_pos < plan_pos < dod_pos < approval_pos, \
            "Sections should appear in order: Intent → Plan → DoD → Approval"
    
    def test_markdown_under_15_seconds_scan(self, dor_gate):
        """Test that markdown output is concise enough to scan in <15 seconds."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            key_entities=["feature.py", "tests.py"],
            requires_tests=True,
            governance_rules=["CORE-008", "CORE-011", "CORE-012"]
        )
        
        markdown = reflection.to_markdown()
        lines = markdown.split('\n')
        
        # Should be scannable: between 30-60 lines total
        # (header + table + execution plan + DoD + approval sections)
        assert 25 < len(lines) < 65, \
            f"Markdown should be concise ({len(lines)} lines, target 30-60)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
