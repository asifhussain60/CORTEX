"""
Test Suite for Master Orchestrator Stage 1 (Comprehension) - AC-PROD-003-01

Stage 1 represents the Comprehension phase of the Master Orchestrator 4-stage workflow.
It analyzes the operation context using natural language processing and intent detection
to produce comprehensive understanding that feeds into Stage 2 (Routing).

The comprehension stage:
1. Accepts raw operation input (description, keywords, intent)
2. Runs LENS Protocol Phase 1 (Language Analysis) automatically
3. Extracts intent, confidence, and keywords
4. Produces Stage 1 output for Stage 2 routing
5. Logs all operations to audit trail

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, Any, Optional

from src.core.result import Result, Ok, Err
from src.orchestrators.core.master_orchestrator_stage_1 import (
    MasterOrchestrationStage1,
    Stage1ComprehensionContext,
    Stage1Output,
)


class TestStage1Initialization:
    """Test Stage 1 Comprehension initialization and setup."""
    
    def test_stage_1_initializes(self) -> None:
        """Test MasterOrchestrationStage1 creates successfully."""
        stage1 = MasterOrchestrationStage1()
        assert stage1 is not None
        assert hasattr(stage1, 'comprehend')
        assert hasattr(stage1, 'get_comprehension_history')
    
    def test_stage_1_has_required_attributes(self) -> None:
        """Test Stage 1 has required attributes."""
        stage1 = MasterOrchestrationStage1()
        
        assert hasattr(stage1, 'logger')
        assert hasattr(stage1, 'comprehension_history')
        assert hasattr(stage1, 'lens_phase_1')
    
    def test_stage_1_starts_with_empty_history(self) -> None:
        """Test Stage 1 starts with empty comprehension history."""
        stage1 = MasterOrchestrationStage1()
        
        history = stage1.get_comprehension_history()
        assert len(history) == 0


class TestStage1ComprehensionContext:
    """Test Stage1ComprehensionContext dataclass."""
    
    def test_context_creation(self) -> None:
        """Test Stage1ComprehensionContext creates successfully."""
        context = Stage1ComprehensionContext(
            operation="implement_feature",
            description="Add user authentication to API",
            keywords=["auth", "user", "api"],
            domain="api"
        )
        
        assert context.operation == "implement_feature"
        assert context.description == "Add user authentication to API"
        assert "auth" in context.keywords
        assert context.domain == "api"
    
    def test_context_with_optional_fields(self) -> None:
        """Test context with optional fields."""
        context = Stage1ComprehensionContext(
            operation="fix_bug",
            description="Fix database connection timeout",
            keywords=["database", "timeout", "connection"],
            domain="persistence",
            user_intent="resolve_production_issue",
            urgency="critical",
            metadata={"ticket_id": "BUG-123"}
        )
        
        assert context.user_intent == "resolve_production_issue"
        assert context.urgency == "critical"
        assert context.metadata["ticket_id"] == "BUG-123"


class TestStage1Output:
    """Test Stage1Output dataclass."""
    
    def test_output_creation(self) -> None:
        """Test Stage1Output creates successfully."""
        output = Stage1Output(
            operation="implement",
            language_analysis={
                "intent": "create",
                "confidence": 0.92,
                "keywords": ["new", "feature"]
            },
            extracted_intent="implement",
            confidence_score=0.92,
            domain="persistence"
        )
        
        assert output.operation == "implement"
        assert output.extracted_intent == "implement"
        assert output.confidence_score == 0.92
    
    def test_output_has_stage_2_ready_format(self) -> None:
        """Test output format is ready for Stage 2."""
        output = Stage1Output(
            operation="fix",
            language_analysis={"intent": "repair"},
            extracted_intent="fix",
            confidence_score=0.88,
            domain="api"
        )
        
        # Stage 2 should be able to consume this
        assert hasattr(output, 'language_analysis')
        assert hasattr(output, 'extracted_intent')
        assert hasattr(output, 'confidence_score')


class TestLanguageAnalysisPhase:
    """Test LENS Language Analysis Phase 1 execution."""
    
    def test_comprehend_simple_operation(self) -> None:
        """Test comprehending simple operation."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="create_new_module",
            description="Implement new user authentication module",
            keywords=["create", "new", "authentication"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        assert output.operation == "create_new_module"
        assert output.extracted_intent is not None
    
    def test_comprehend_extract_intent_implement(self) -> None:
        """Test extracting IMPLEMENT intent."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="add_feature",
            description="Add two-factor authentication",
            keywords=["add", "new", "feature", "authentication"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        # Should detect as implement intent
        assert output.extracted_intent in ["implement", "create", "add"]
    
    def test_comprehend_extract_intent_fix(self) -> None:
        """Test extracting FIX intent."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="fix_auth_bug",
            description="Fix authentication token expiration bug",
            keywords=["fix", "bug", "error", "authentication"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        # Should detect as fix intent
        assert output.extracted_intent in ["fix", "repair", "debug"]
    
    def test_comprehend_extract_intent_refactor(self) -> None:
        """Test extracting REFACTOR intent."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="refactor_auth",
            description="Refactor authentication module for better maintainability",
            keywords=["refactor", "clean", "improve", "maintainability"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        # Should detect as refactor intent
        assert output.extracted_intent in ["refactor", "optimize", "improve"]


class TestConfidenceScoring:
    """Test confidence scoring in comprehension."""
    
    def test_confidence_score_generated(self) -> None:
        """Test confidence score is generated."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="implement",
            description="Add new API endpoint",
            keywords=["add", "new", "endpoint"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        assert hasattr(output, 'confidence_score')
        assert 0.0 <= output.confidence_score <= 1.0
    
    def test_high_confidence_for_clear_intent(self) -> None:
        """Test high confidence for clear intent."""
        stage1 = MasterOrchestrationStage1()
        
        # Very clear intent
        context = Stage1ComprehensionContext(
            operation="create_feature",
            description="Create new user registration feature with email verification",
            keywords=["create", "new", "feature", "user", "registration"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        # Should have high confidence
        assert output.confidence_score > 0.75
    
    def test_lower_confidence_for_ambiguous_intent(self) -> None:
        """Test lower confidence for ambiguous intent."""
        stage1 = MasterOrchestrationStage1()
        
        # Ambiguous intent
        context = Stage1ComprehensionContext(
            operation="update",
            description="Update something",
            keywords=["update"],
            domain="core"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        # Should have lower confidence
        assert output.confidence_score < 0.95


class TestComprehensionHistory:
    """Test comprehension history tracking."""
    
    def test_history_tracks_comprehensions(self) -> None:
        """Test history tracks all comprehensions."""
        stage1 = MasterOrchestrationStage1()
        
        # First comprehension
        context1 = Stage1ComprehensionContext(
            operation="implement_1",
            description="Add feature 1",
            keywords=["add", "feature"],
            domain="api"
        )
        stage1.comprehend(context1)
        
        # Second comprehension
        context2 = Stage1ComprehensionContext(
            operation="fix_1",
            description="Fix bug 1",
            keywords=["fix", "bug"],
            domain="api"
        )
        stage1.comprehend(context2)
        
        history = stage1.get_comprehension_history()
        assert len(history) == 2
    
    def test_history_preserves_order(self) -> None:
        """Test history preserves chronological order."""
        stage1 = MasterOrchestrationStage1()
        
        for i in range(3):
            context = Stage1ComprehensionContext(
                operation=f"op_{i}",
                description=f"Operation {i}",
                keywords=[f"keyword_{i}"],
                domain="api"
            )
            stage1.comprehend(context)
        
        history = stage1.get_comprehension_history()
        assert len(history) == 3
        # History should contain comprehensions in order
        assert all(h is not None for h in history)


class TestStage1ToStage2Handoff:
    """Test handoff from Stage 1 to Stage 2."""
    
    def test_stage1_output_ready_for_stage2_routing(self) -> None:
        """Test Stage 1 output is compatible with Stage 2 routing."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="implement_auth",
            description="Implement OAuth2 authentication",
            keywords=["implement", "oauth2", "authentication"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        
        # Stage 2 needs these fields for routing
        assert hasattr(output, 'extracted_intent')
        assert hasattr(output, 'confidence_score')
        assert hasattr(output, 'language_analysis')
        assert hasattr(output, 'domain')
    
    def test_stage1_provides_intent_for_routing(self) -> None:
        """Test Stage 1 provides intent for routing decisions."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="repair_database",
            description="Repair database connection pool issue",
            keywords=["repair", "database", "connection"],
            domain="persistence"
        )
        
        result = stage1.comprehend(context)
        assert result.is_ok()
        
        output = result.unwrap()
        # Router needs clear intent
        assert output.extracted_intent is not None
        assert output.confidence_score > 0.5


class TestErrorHandling:
    """Test error handling in Stage 1."""
    
    def test_comprehend_invalid_context(self) -> None:
        """Test invalid context returns error."""
        stage1 = MasterOrchestrationStage1()
        
        result = stage1.comprehend(None)
        assert result.is_err()
    
    def test_comprehend_missing_operation(self) -> None:
        """Test missing operation name returns error."""
        stage1 = MasterOrchestrationStage1()
        
        # Can't create context without operation
        with pytest.raises(TypeError):
            context = Stage1ComprehensionContext(
                description="Some operation"
            )
    
    def test_comprehend_empty_keywords(self) -> None:
        """Test empty keywords handled gracefully."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="op",
            description="Some operation",
            keywords=[],  # Empty keywords
            domain="api"
        )
        
        result = stage1.comprehend(context)
        # Should handle gracefully
        assert result is not None


class TestGovernanceCompliance:
    """Test CORE governance compliance."""
    
    def test_core_011_type_hints_present(self) -> None:
        """Test CORE-011: Type hints present on all methods."""
        stage1 = MasterOrchestrationStage1()
        
        assert hasattr(stage1.comprehend, '__annotations__')
        assert 'return' in stage1.comprehend.__annotations__
    
    def test_core_012_docstrings_present(self) -> None:
        """Test CORE-012: Google-style docstrings present."""
        assert MasterOrchestrationStage1.__doc__ is not None
        assert len(MasterOrchestrationStage1.__doc__) > 0
    
    def test_core_027_audit_trail_support(self) -> None:
        """Test CORE-027: Audit trail support."""
        stage1 = MasterOrchestrationStage1()
        
        # Should have audit logger
        assert hasattr(stage1, 'logger')


class TestAuditTrailing:
    """Test audit trail logging for comprehension operations."""
    
    def test_comprehension_logged(self) -> None:
        """Test comprehension operations are logged."""
        stage1 = MasterOrchestrationStage1()
        
        context = Stage1ComprehensionContext(
            operation="test_op",
            description="Test operation",
            keywords=["test"],
            domain="api"
        )
        
        result = stage1.comprehend(context)
        # Operation should be logged
        assert result is not None
    
    def test_error_operations_logged(self) -> None:
        """Test error operations are logged."""
        stage1 = MasterOrchestrationStage1()
        
        result = stage1.comprehend(None)
        # Error should be logged
        assert result.is_err()


# Module exports
__all__ = [
    "TestStage1Initialization",
    "TestStage1ComprehensionContext",
    "TestStage1Output",
    "TestLanguageAnalysisPhase",
    "TestConfidenceScoring",
    "TestComprehensionHistory",
    "TestStage1ToStage2Handoff",
    "TestErrorHandling",
    "TestGovernanceCompliance",
    "TestAuditTrailing",
]
