"""
Tests for Stage 2/3/4 Strategies.

ENH-087 Track 1.2: Behavioral tests for remaining stage strategies.

Authority:
    - ENH-087: Orchestrator Consolidation
    - CORE-008: TDD Mandatory

Author: Asif Hussain (ENH-087)
Created: 2026-02-11
"""

import pytest

from cortex.orchestrators.strategies import StageContext
from cortex.orchestrators.strategies.stage234_strategies import (
    Stage2IntentClassificationStrategy,
    Stage3ComplianceValidationStrategy,
    Stage4DomainExecutionStrategy,
)


# ============================================================================
# MOCK DEPENDENCIES
# ============================================================================


class MockIntentRouter:
    """Mock IntentRouter for testing."""
    
    def classify(self, request: str) -> dict:
        """Mock classification."""
        return {
            "intent": "IMPLEMENT",
            "confidence": 0.95
        }


class MockEnforcementOrchestrator:
    """Mock EnforcementOrchestrator for testing."""
    
    def validate(self, intent: str, request: str) -> dict:
        """Mock validation."""
        return {
            "passed": True,
            "violations": [],
            "warnings": []
        }


class MockDomainOrchestrator:
    """Mock domain orchestrator for testing."""
    
    def execute(self, request: str) -> dict:
        """Mock execution."""
        return {"status": "success", "output": "Feature implemented"}


# ============================================================================
# TEST SUITE: STAGE 2 - INTENT CLASSIFICATION
# ============================================================================


class TestStage2IntentClassificationStrategy:
    """Test Stage 2 Intent Classification Strategy."""
    
    @pytest.fixture
    def mock_intent_router(self):
        """Create mock intent router."""
        return MockIntentRouter()
    
    @pytest.fixture
    def stage2_strategy(self, mock_intent_router):
        """Create Stage2 strategy."""
        return Stage2IntentClassificationStrategy(mock_intent_router)
    
    def test_stage2_has_correct_name(self, stage2_strategy):
        """Stage2 MUST have name 'Stage2_IntentClassification'."""
        assert stage2_strategy.get_stage_name() == "Stage2_IntentClassification"
    
    def test_stage2_lists_dependencies(self, stage2_strategy):
        """Stage2 MUST list IntentRouter dependency."""
        deps = stage2_strategy.get_dependencies()
        assert "IntentRouter" in deps
    
    def test_stage2_classifies_intent(self, stage2_strategy):
        """Stage2 MUST classify user intent."""
        context = StageContext(user_request="implement feature X")
        
        result = stage2_strategy.execute(context)
        
        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.intent == "IMPLEMENT"
    
    def test_stage2_adds_confidence_score(self, stage2_strategy):
        """Stage2 MUST add confidence score."""
        context = StageContext(user_request="implement feature X")
        
        result = stage2_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert updated_context.confidence is not None
        assert 0.0 <= updated_context.confidence <= 1.0
    
    def test_stage2_adds_classification_metadata(self, stage2_strategy):
        """Stage2 MUST add classification metadata."""
        context = StageContext(user_request="implement feature X")
        
        result = stage2_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert "intent_classification" in updated_context.metadata
    
    def test_stage2_preserves_previous_stages(self, stage2_strategy):
        """Stage2 MUST preserve Stage 1 results."""
        context = StageContext(user_request="implement feature X")
        context.metadata["comprehension"] = {"status": "done"}
        
        result = stage2_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert updated_context.metadata["comprehension"] == {"status": "done"}


# ============================================================================
# TEST SUITE: STAGE 3 - COMPLIANCE VALIDATION
# ============================================================================


class TestStage3ComplianceValidationStrategy:
    """Test Stage 3 Compliance Validation Strategy."""
    
    @pytest.fixture
    def mock_enforcement_orch(self):
        """Create mock enforcement orchestrator."""
        return MockEnforcementOrchestrator()
    
    @pytest.fixture
    def stage3_strategy(self, mock_enforcement_orch):
        """Create Stage3 strategy."""
        return Stage3ComplianceValidationStrategy(mock_enforcement_orch)
    
    def test_stage3_has_correct_name(self, stage3_strategy):
        """Stage3 MUST have name 'Stage3_ComplianceValidation'."""
        assert stage3_strategy.get_stage_name() == "Stage3_ComplianceValidation"
    
    def test_stage3_lists_dependencies(self, stage3_strategy):
        """Stage3 MUST list governance dependencies."""
        deps = stage3_strategy.get_dependencies()
        assert "EnforcementOrchestrator" in deps
        assert "GovernanceRegistry" in deps
    
    def test_stage3_validates_compliance(self, stage3_strategy):
        """Stage3 MUST validate governance compliance."""
        context = StageContext(user_request="implement feature X")
        context.intent = "IMPLEMENT"
        
        result = stage3_strategy.execute(context)
        
        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.compliance_status is not None
    
    def test_stage3_adds_governance_metadata(self, stage3_strategy):
        """Stage3 MUST add governance metadata."""
        context = StageContext(user_request="implement feature X")
        context.intent = "IMPLEMENT"
        
        result = stage3_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert "governance" in updated_context.metadata
    
    def test_stage3_passes_when_compliant(self, stage3_strategy):
        """Stage3 MUST pass when request is compliant."""
        context = StageContext(user_request="implement feature X")
        context.intent = "IMPLEMENT"
        
        result = stage3_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert updated_context.compliance_status["passed"] == True


# ============================================================================
# TEST SUITE: STAGE 4 - DOMAIN EXECUTION
# ============================================================================


class TestStage4DomainExecutionStrategy:
    """Test Stage 4 Domain Execution Strategy."""
    
    @pytest.fixture
    def mock_orchestrator_registry(self):
        """Create mock orchestrator registry."""
        return {
            "IMPLEMENT": MockDomainOrchestrator(),
            "FIX": MockDomainOrchestrator(),
            "REFACTOR": MockDomainOrchestrator()
        }
    
    @pytest.fixture
    def stage4_strategy(self, mock_orchestrator_registry):
        """Create Stage4 strategy."""
        return Stage4DomainExecutionStrategy(mock_orchestrator_registry)
    
    def test_stage4_has_correct_name(self, stage4_strategy):
        """Stage4 MUST have name 'Stage4_DomainExecution'."""
        assert stage4_strategy.get_stage_name() == "Stage4_DomainExecution"
    
    def test_stage4_lists_dependencies(self, stage4_strategy):
        """Stage4 MUST list orchestrator registry dependency."""
        deps = stage4_strategy.get_dependencies()
        assert "OrchestratorRegistry" in deps
    
    def test_stage4_delegates_to_orchestrator(self, stage4_strategy):
        """Stage4 MUST delegate to domain orchestrator."""
        context = StageContext(user_request="implement feature X")
        context.intent = "IMPLEMENT"
        context.compliance_status = {"passed": True}
        
        result = stage4_strategy.execute(context)
        
        assert result.is_ok()
        updated_context = result.unwrap()
        assert updated_context.domain_result is not None
    
    def test_stage4_adds_execution_metadata(self, stage4_strategy):
        """Stage4 MUST add execution metadata."""
        context = StageContext(user_request="implement feature X")
        context.intent = "IMPLEMENT"
        context.compliance_status = {"passed": True}
        
        result = stage4_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert "execution" in updated_context.metadata
    
    def test_stage4_fails_when_compliance_failed(self, stage4_strategy):
        """Stage4 MUST fail when compliance validation failed."""
        context = StageContext(user_request="implement feature X")
        context.intent = "IMPLEMENT"
        context.compliance_status = {"passed": False, "violations": ["TDD required"]}
        
        result = stage4_strategy.execute(context)
        
        assert result.is_err()
    
    def test_stage4_fails_when_no_orchestrator(self, stage4_strategy):
        """Stage4 MUST fail when no orchestrator for intent."""
        context = StageContext(user_request="unknown operation")
        context.intent = "UNKNOWN"
        context.compliance_status = {"passed": True}
        
        result = stage4_strategy.execute(context)
        
        assert result.is_err()


# ============================================================================
# EXECUTION CHECK
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
