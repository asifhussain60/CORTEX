"""
Tests for Stage 1 Comprehension Strategy.

ENH-087 Track 1.1: Behavioral tests for Stage1ComprehensionStrategy.

Authority:
    - ENH-087: Orchestrator Consolidation
    - CORE-008: TDD Mandatory

Author: Asif Hussain (ENH-087)
Created: 2026-02-11
"""

import pytest

from cortex.orchestrators.strategies import StageContext
from cortex.orchestrators.strategies.stage1_comprehension_strategy import (
    Stage1ComprehensionStrategy,
)


class MockInteractionOrchestrator:
    """Mock InteractionOrchestrator for testing."""
    
    def comprehend(self, request: str) -> dict:
        """Mock comprehension."""
        return {"status": "comprehended"}


class TestStage1ComprehensionStrategy:
    """Test Stage 1 Comprehension Strategy."""
    
    @pytest.fixture
    def mock_interaction_orch(self):
        """Create mock interaction orchestrator."""
        return MockInteractionOrchestrator()
    
    @pytest.fixture
    def stage1_strategy(self, mock_interaction_orch):
        """Create Stage1 strategy with mocks."""
        return Stage1ComprehensionStrategy(
            interaction_orchestrator=mock_interaction_orch
        )
    
    def test_stage1_strategy_has_correct_name(self, stage1_strategy):
        """Stage1 MUST have name 'Stage1_Comprehension'."""
        assert stage1_strategy.get_stage_name() == "Stage1_Comprehension"
    
    def test_stage1_lists_dependencies(self, stage1_strategy):
        """Stage1 MUST list required dependencies."""
        deps = stage1_strategy.get_dependencies()
        
        assert "InteractionOrchestrator" in deps
        assert "ChallengeGenerator" in deps
        assert "DoRApprovalGate" in deps
    
    def test_stage1_executes_successfully(self, stage1_strategy):
        """Stage1 MUST execute and return updated context."""
        context = StageContext(user_request="implement feature X")
        
        result = stage1_strategy.execute(context)
        
        assert result.is_ok()
        updated_context = result.unwrap()
        assert isinstance(updated_context, StageContext)
    
    def test_stage1_adds_comprehension_metadata(self, stage1_strategy):
        """Stage1 MUST add comprehension metadata to context."""
        context = StageContext(user_request="implement feature X")
        
        result = stage1_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert "comprehension" in updated_context.metadata
        assert updated_context.metadata["comprehension"]["status"] == "comprehended"
    
    def test_stage1_adds_challenge_result(self, stage1_strategy):
        """Stage1 MUST add challenge result to context."""
        context = StageContext(user_request="implement feature X")
        
        result = stage1_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert updated_context.challenge_result is not None
        assert "status" in updated_context.challenge_result
    
    def test_stage1_adds_confidence_score(self, stage1_strategy):
        """Stage1 MUST add DoR confidence score."""
        context = StageContext(user_request="implement feature X")
        
        result = stage1_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert "confidence" in updated_context.metadata
        assert isinstance(updated_context.metadata["confidence"], (int, float))
        assert 0.0 <= updated_context.metadata["confidence"] <= 1.0
    
    def test_stage1_preserves_original_request(self, stage1_strategy):
        """Stage1 MUST preserve original user request."""
        original_request = "implement feature X"
        context = StageContext(user_request=original_request)
        
        result = stage1_strategy.execute(context)
        updated_context = result.unwrap()
        
        assert updated_context.user_request == original_request
    
    def test_stage1_handles_exception_gracefully(self):
        """Stage1 MUST handle exceptions in interaction orchestrator."""
        class FailingOrchestrator:
            """Mock orchestrator that raises exception."""
            def comprehend(self, request: str):
                raise RuntimeError("Mock orchestrator failure")
        
        strategy = Stage1ComprehensionStrategy(
            interaction_orchestrator=FailingOrchestrator()
        )
        
        context = StageContext(user_request="test")
        result = strategy.execute(context)
        
        # Should return Err instead of raising exception
        assert result.is_err()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
