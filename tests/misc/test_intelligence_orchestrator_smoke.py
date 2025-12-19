"""
Smoke tests for Intelligence Orchestrator.
Tests AI-powered operations (feature completion, clarification, refactoring).
"""

import pytest
from pathlib import Path

from src.orchestration_3_0.orchestrators.intelligence import (
    IntelligenceOrchestrator,
    create_intelligence_orchestrator,
    FeatureCompletionResult,
    ClarificationResult,
    RefactoringResult
)
from src.orchestration_3_0.core.base_orchestrator import WorkflowContext


class TestIntelligenceOrchestrator:
    """Smoke tests for Intelligence Orchestrator."""
    
    def test_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = create_intelligence_orchestrator()
        
        assert orchestrator is not None
        assert orchestrator.orchestrator_name == "IntelligenceOrchestrator"
        assert orchestrator.state_machine is not None
        assert orchestrator.session_manager is not None
    
    def test_feature_completion_workflow(self):
        """Test feature completion workflow executes successfully."""
        orchestrator = create_intelligence_orchestrator()
        
        # Execute feature completion
        result = orchestrator.complete_feature(
            feature_description="Add user authentication endpoint",
            codebase_context={"existing_auth": False, "framework": "flask"}
        )
        
        # Verify result structure
        assert isinstance(result, FeatureCompletionResult)
        assert result.success is True
        assert result.confidence_score >= 0.7
        assert result.implementation_code is not None
        assert result.test_code is not None
        assert len(result.suggested_improvements) > 0
    
    def test_clarification_workflow(self):
        """Test requirements clarification workflow."""
        orchestrator = create_intelligence_orchestrator()
        
        # Execute clarification
        result = orchestrator.clarify_requirements(
            ambiguous_request="add payment processing",
            workflow_context={"project_type": "ecommerce"}
        )
        
        # Verify result structure
        assert isinstance(result, ClarificationResult)
        assert result.success is True
        assert result.confidence_score >= 0.7
        # Should have either inferred requirements or questions
        assert result.inferred_requirements or result.clarification_questions
    
    def test_refactoring_workflow(self):
        """Test code refactoring workflow."""
        orchestrator = create_intelligence_orchestrator()
        
        # Execute refactoring
        result = orchestrator.refactor_code(
            file_paths=["src/test.py", "src/utils.py"],
            language="python",
            refactoring_goals=["apply SOLID principles", "remove code smells"]
        )
        
        # Verify result structure
        assert isinstance(result, RefactoringResult)
        assert result.success is True
        assert len(result.refactored_files) == 2
        assert result.changes_summary is not None
        assert len(result.architectural_improvements) > 0
    
    def test_dor_validation(self):
        """Test Definition of Ready validation."""
        orchestrator = create_intelligence_orchestrator()
        
        context = WorkflowContext(
            tenant_id="test_tenant",
            project_id="test_project",
            user_id="test_user",
            session_id="test_session",
            inputs={},
            metadata={"operation_type": "complete_feature"}
        )
        
        result = orchestrator.validate_dor(context)
        
        # Should pass (stub mode)
        assert result.passed is True
    
    def test_dod_validation_success(self):
        """Test Definition of Done validation with successful result."""
        orchestrator = create_intelligence_orchestrator()
        
        # Create context with successful AI result
        ai_result = FeatureCompletionResult(
            success=True,
            implementation_code="# code",
            test_code="# tests",
            documentation="# docs",
            confidence_score=0.85
        )
        
        context = WorkflowContext(
            tenant_id="test_tenant",
            project_id="test_project",
            user_id="test_user",
            session_id="test_session",
            inputs={},
            metadata={"operation_type": "complete_feature"},
            outputs={"result": ai_result}  # DoD validation reads from outputs
        )
        
        result = orchestrator.validate_dod(context)
        
        # Should pass (confidence >= 0.7)
        assert result.passed is True
        assert len(result.errors) == 0
        # Check confidence in warnings
        confidence_warning = [w for w in result.warnings if "confidence" in w]
        assert len(confidence_warning) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
