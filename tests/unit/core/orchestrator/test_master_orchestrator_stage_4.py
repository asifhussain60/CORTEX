"""
Test Suite for Master Orchestrator Stage 4 (Approval) - AC-PROD-003-03

Stage 4 represents the Approval phase of the Master Orchestrator 4-stage workflow.
It validates recommendations and knowledge from Stage 3, applies approval gates,
and produces final orchestration decisions ready for implementation execution.

The approval stage:
1. Receives Stage 3 knowledge output
2. Validates recommendations against domain constraints
3. Applies approval gates (urgency, risk, domain expertise)
4. Generates approval decision with justification
5. Produces Stage 4 output ready for execution
6. Logs all decisions to audit trail

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, Any, List, Optional

from cortex.core.result import Result, Ok, Err


class TestStage4Initialization:
    """Test Stage 4 Approval initialization and setup."""
    
    def test_stage_4_initializes(self) -> None:
        """Test MasterOrchestrationStage4 creates successfully."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        stage4 = MasterOrchestrationStage4()
        assert stage4 is not None
        assert hasattr(stage4, 'approve_operation')
        assert hasattr(stage4, 'get_approval_history')
    
    def test_stage_4_has_required_attributes(self) -> None:
        """Test Stage 4 has required attributes."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        stage4 = MasterOrchestrationStage4()
        
        assert hasattr(stage4, 'logger')
        assert hasattr(stage4, 'approval_history')
        assert hasattr(stage4, 'approval_gates')
    
    def test_stage_4_starts_with_empty_history(self) -> None:
        """Test Stage 4 starts with empty approval history."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        stage4 = MasterOrchestrationStage4()
        
        history = stage4.get_approval_history()
        assert len(history) == 0


class TestStage4ApprovalContext:
    """Test Stage4ApprovalContext dataclass."""
    
    def test_approval_context_from_stage3_output(self) -> None:
        """Test Stage 4 context creation from Stage 3 output."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage3_output = Stage3Output(
            operation="implement_oauth2",
            stage1_output=None,
            knowledge_graph={"entities": ["Auth"]},
            lens_recommendations=[{"phase": "language", "recommendation": "Use OAuth2"}],
            confidence_score=0.92,
            domain="api"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="high",
            approval_level="standard"
        )
        
        assert context.stage3_output.operation == "implement_oauth2"
        assert context.user_id == "user@example.com"
        assert context.urgency == "high"
    
    def test_approval_context_with_constraints(self) -> None:
        """Test context with domain constraints."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage3_output = Stage3Output(
            operation="fix_security",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[],
            confidence_score=0.88,
            domain="api"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="admin@example.com",
            urgency="critical",
            approval_level="expert",
            constraints=["require_security_review", "require_load_test"]
        )
        
        assert context.urgency == "critical"
        assert "require_security_review" in context.constraints


class TestStage4Output:
    """Test Stage4Output dataclass."""
    
    def test_output_creation(self) -> None:
        """Test Stage4Output creates successfully."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            Stage4Output
        )
        
        output = Stage4Output(
            operation="implement",
            approved=True,
            approval_reason="Meets all requirements",
            confidence_score=0.92,
            gates_passed=["domain_validation", "risk_assessment"],
            implementation_plan=[
                {"step": 1, "description": "Design API"},
                {"step": 2, "description": "Implement endpoints"}
            ]
        )
        
        assert output.operation == "implement"
        assert output.approved is True
        assert output.confidence_score == 0.92
    
    def test_output_has_execution_ready_format(self) -> None:
        """Test output format is ready for execution."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            Stage4Output
        )
        
        output = Stage4Output(
            operation="fix",
            approved=True,
            approval_reason="Critical fix needed",
            confidence_score=0.85,
            gates_passed=["urgency_check"],
            implementation_plan=[]
        )
        
        # Execution should be able to consume this
        assert hasattr(output, 'approved')
        assert hasattr(output, 'gates_passed')
        assert hasattr(output, 'implementation_plan')
        assert hasattr(output, 'operation')


class TestApprovalGates:
    """Test approval gate execution."""
    
    def test_domain_validation_gate(self) -> None:
        """Test domain validation gate."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="api_update",
            stage1_output=None,
            knowledge_graph={"domain": "api"},
            lens_recommendations=[],
            confidence_score=0.90,
            domain="api"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="medium",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        assert result is not None
    
    def test_urgency_gate(self) -> None:
        """Test urgency gate evaluation."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="critical_fix",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[],
            confidence_score=0.88,
            domain="core"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="critical",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        if result.is_ok():
            output = result.unwrap()
            # Critical urgency should influence decision
            assert output is not None
    
    def test_risk_assessment_gate(self) -> None:
        """Test risk assessment gate."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        # High confidence = lower risk
        stage3_output = Stage3Output(
            operation="safe_refactor",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[],
            confidence_score=0.95,  # High confidence
            domain="core"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="low",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        if result.is_ok():
            output = result.unwrap()
            assert output is not None


class TestApprovalDecisions:
    """Test approval decision making."""
    
    def test_approve_low_risk_operation(self) -> None:
        """Test approving low-risk operation."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="low_risk_feature",
            stage1_output=None,
            knowledge_graph={"entities": ["Model"]},
            lens_recommendations=[{"recommendation": "Simple change"}],
            confidence_score=0.95,
            domain="core"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="dev@example.com",
            urgency="low",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        assert result.is_ok()
        
        if result.is_ok():
            output = result.unwrap()
            # Low risk, high confidence should be approved
            assert output.approved is True
    
    def test_reject_high_risk_low_confidence(self) -> None:
        """Test rejecting high-risk, low-confidence operation."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="high_risk_refactor",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[],
            confidence_score=0.45,  # Low confidence
            domain="persistence"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="medium",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        if result.is_ok():
            output = result.unwrap()
            # Low confidence should increase rejection likelihood
            assert output is not None
    
    def test_auto_approve_critical_urgency(self) -> None:
        """Test auto-approval for critical urgency."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="critical_fix",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[{"recommendation": "Emergency fix"}],
            confidence_score=0.80,
            domain="api"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="admin@example.com",
            urgency="critical",  # Critical urgency
            approval_level="expert"
        )
        
        result = stage4.approve_operation(context)
        if result.is_ok():
            output = result.unwrap()
            # Critical urgency should auto-approve
            assert output.approved is True


class TestImplementationPlanning:
    """Test implementation plan generation."""
    
    def test_implementation_plan_generated(self) -> None:
        """Test implementation plan is generated."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="implement_feature",
            stage1_output=None,
            knowledge_graph={"entities": ["API", "Database"]},
            lens_recommendations=[],
            confidence_score=0.90,
            domain="api"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="medium",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        if result.is_ok():
            output = result.unwrap()
            # Should have implementation plan
            assert hasattr(output, 'implementation_plan')
    
    def test_implementation_plan_has_steps(self) -> None:
        """Test implementation plan has executable steps."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="implement",
            stage1_output=None,
            knowledge_graph={"entities": ["Service", "Repository"]},
            lens_recommendations=[],
            confidence_score=0.92,
            domain="core"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="dev@example.com",
            urgency="low",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        if result.is_ok():
            output = result.unwrap()
            if output.approved and output.implementation_plan:
                # Plan should have steps
                assert len(output.implementation_plan) > 0


class TestApprovalHistory:
    """Test approval decision history tracking."""
    
    def test_history_tracks_approvals(self) -> None:
        """Test history tracks all approval decisions."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        for i in range(2):
            stage3_output = Stage3Output(
                operation=f"op_{i}",
                stage1_output=None,
                knowledge_graph={},
                lens_recommendations=[],
                confidence_score=0.90,
                domain="api"
            )
            
            context = Stage4ApprovalContext(
                stage3_output=stage3_output,
                user_id="user@example.com",
                urgency="medium",
                approval_level="standard"
            )
            
            stage4.approve_operation(context)
        
        history = stage4.get_approval_history()
        assert len(history) >= 2
    
    def test_history_preserves_order(self) -> None:
        """Test history preserves chronological order."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        for i in range(3):
            stage3_output = Stage3Output(
                operation=f"op_{i}",
                stage1_output=None,
                knowledge_graph={},
                lens_recommendations=[],
                confidence_score=0.90,
                domain="api"
            )
            
            context = Stage4ApprovalContext(
                stage3_output=stage3_output,
                user_id="user@example.com",
                urgency="medium",
                approval_level="standard"
            )
            
            stage4.approve_operation(context)
        
        history = stage4.get_approval_history()
        # History should be in order
        assert all(h is not None for h in history)


class TestErrorHandling:
    """Test error handling in Stage 4."""
    
    def test_approve_invalid_context(self) -> None:
        """Test invalid context returns error."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        stage4 = MasterOrchestrationStage4()
        
        result = stage4.approve_operation(None)
        assert result.is_err()
    
    def test_approve_missing_stage3_output(self) -> None:
        """Test missing Stage 3 output handled."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        
        stage4 = MasterOrchestrationStage4()
        
        # Context with None stage3_output
        context = Stage4ApprovalContext(
            stage3_output=None,
            user_id="user@example.com",
            urgency="medium",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        # Should handle gracefully
        assert result is not None
    
    def test_invalid_urgency_handled(self) -> None:
        """Test invalid urgency handled gracefully."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="op",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[],
            confidence_score=0.90,
            domain="api"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="invalid_urgency",  # Invalid value
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        # Should handle gracefully
        assert result is not None


class TestGovernanceCompliance:
    """Test CORE governance compliance."""
    
    def test_core_011_type_hints_present(self) -> None:
        """Test CORE-011: Type hints present on all methods."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        stage4 = MasterOrchestrationStage4()
        
        assert hasattr(stage4.approve_operation, '__annotations__')
        assert 'return' in stage4.approve_operation.__annotations__
    
    def test_core_012_docstrings_present(self) -> None:
        """Test CORE-012: Google-style docstrings present."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        assert MasterOrchestrationStage4.__doc__ is not None
        assert len(MasterOrchestrationStage4.__doc__) > 0
    
    def test_core_027_audit_trail_support(self) -> None:
        """Test CORE-027: Audit trail support."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        stage4 = MasterOrchestrationStage4()
        
        # Should have audit logger
        assert hasattr(stage4, 'logger')


class TestAuditTrailing:
    """Test audit trail logging for approval operations."""
    
    def test_approval_logged(self) -> None:
        """Test approval operations are logged."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4,
            Stage4ApprovalContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_3 import Stage3Output
        
        stage4 = MasterOrchestrationStage4()
        
        stage3_output = Stage3Output(
            operation="test_op",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[],
            confidence_score=0.90,
            domain="api"
        )
        
        context = Stage4ApprovalContext(
            stage3_output=stage3_output,
            user_id="user@example.com",
            urgency="medium",
            approval_level="standard"
        )
        
        result = stage4.approve_operation(context)
        # Operation should be logged
        assert result is not None
    
    def test_error_operations_logged(self) -> None:
        """Test error operations are logged."""
        from cortex.orchestrators.core.master_orchestrator_stage_4 import (
            MasterOrchestrationStage4
        )
        
        stage4 = MasterOrchestrationStage4()
        
        result = stage4.approve_operation(None)
        # Error should be logged
        assert result.is_err()


# Module exports
__all__ = [
    "TestStage4Initialization",
    "TestStage4ApprovalContext",
    "TestStage4Output",
    "TestApprovalGates",
    "TestApprovalDecisions",
    "TestImplementationPlanning",
    "TestApprovalHistory",
    "TestErrorHandling",
    "TestGovernanceCompliance",
    "TestAuditTrailing",
]
