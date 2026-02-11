"""
Tests for Stage Execution Strategy Pattern.

ENH-087 Track 1.1: Behavioral contract tests for StageExecutionStrategy.

Test Structure:
    - TestStageContextDataclass: Validate StageContext fields
    - TestStageExecutionStrategyProtocol: Validate abstract base
    - TestStageExecutionStrategyContract: Behavioral contract

Authority:
    - ENH-087: Orchestrator Consolidation
    - CORE-008: TDD Mandatory
    - CORE-011: Type Hints

Author: Asif Hussain (ENH-087)
Created: 2026-02-11
"""

import pytest

from cortex.core.result import Err, Ok
from cortex.orchestrators.strategies import (
    StageContext,
    StageExecutionStrategy,
)


# ============================================================================
# TEST SUITE 1: StageContext Dataclass
# ============================================================================


class TestStageContextDataclass:
    """Test StageContext dataclass structure and initialization."""
    
    def test_stage_context_has_user_request_field(self):
        """StageContext MUST have user_request field."""
        context = StageContext(user_request="test request")
        assert context.user_request == "test request"
    
    def test_stage_context_has_intent_field(self):
        """StageContext MUST have optional intent field."""
        context = StageContext(user_request="test")
        assert context.intent is None
        
        context.intent = "IMPLEMENT"
        assert context.intent == "IMPLEMENT"
    
    def test_stage_context_has_confidence_field(self):
        """StageContext MUST have optional confidence field."""
        context = StageContext(user_request="test")
        assert context.confidence is None
        
        context.confidence = 0.95
        assert context.confidence == 0.95
    
    def test_stage_context_has_challenge_result_field(self):
        """StageContext MUST have optional challenge_result field."""
        context = StageContext(user_request="test")
        assert context.challenge_result is None
        
        context.challenge_result = {"status": "passed"}
        assert context.challenge_result == {"status": "passed"}
    
    def test_stage_context_has_compliance_status_field(self):
        """StageContext MUST have optional compliance_status field."""
        context = StageContext(user_request="test")
        assert context.compliance_status is None
        
        context.compliance_status = {"compliant": True}
        assert context.compliance_status == {"compliant": True}
    
    def test_stage_context_has_domain_result_field(self):
        """StageContext MUST have optional domain_result field."""
        context = StageContext(user_request="test")
        assert context.domain_result is None
        
        context.domain_result = {"success": True}
        assert context.domain_result == {"success": True}
    
    def test_stage_context_initializes_metadata_dict(self):
        """StageContext MUST initialize metadata as empty dict."""
        context = StageContext(user_request="test")
        assert context.metadata == {}
        assert isinstance(context.metadata, dict)
    
    def test_stage_context_allows_metadata_customization(self):
        """StageContext MUST allow metadata customization."""
        context = StageContext(
            user_request="test",
            metadata={"custom_key": "custom_value"}
        )
        assert context.metadata == {"custom_key": "custom_value"}


# ============================================================================
# TEST SUITE 2: StageExecutionStrategy Protocol
# ============================================================================


class TestStageExecutionStrategyProtocol:
    """Test StageExecutionStrategy abstract base class."""
    
    def test_stage_execution_strategy_is_abstract(self):
        """StageExecutionStrategy MUST be abstract (cannot instantiate)."""
        with pytest.raises(TypeError, match="abstract"):
            StageExecutionStrategy()  # type: ignore
    
    def test_stage_execution_strategy_requires_execute_method(self):
        """Subclasses MUST implement execute() method."""
        class IncompleteStrategy(StageExecutionStrategy):
            def get_stage_name(self) -> str:
                return "Incomplete"
            
            def get_dependencies(self) -> list[str]:
                return []
        
        with pytest.raises(TypeError, match="abstract"):
            IncompleteStrategy()  # type: ignore
    
    def test_stage_execution_strategy_requires_get_stage_name(self):
        """Subclasses MUST implement get_stage_name() method."""
        class IncompleteStrategy(StageExecutionStrategy):
            def execute(self, context: StageContext):
                return Ok(context)
            
            def get_dependencies(self) -> list[str]:
                return []
        
        with pytest.raises(TypeError, match="abstract"):
            IncompleteStrategy()  # type: ignore
    
    def test_stage_execution_strategy_requires_get_dependencies(self):
        """Subclasses MUST implement get_dependencies() method."""
        class IncompleteStrategy(StageExecutionStrategy):
            def execute(self, context: StageContext):
                return Ok(context)
            
            def get_stage_name(self) -> str:
                return "Incomplete"
        
        with pytest.raises(TypeError, match="abstract"):
            IncompleteStrategy()  # type: ignore


# ============================================================================
# TEST SUITE 3: Behavioral Contract
# ============================================================================


class TestStageExecutionStrategyContract:
    """Test behavioral contract for StageExecutionStrategy implementations."""
    
    @pytest.fixture
    def minimal_strategy(self):
        """Create minimal valid strategy for testing."""
        class MinimalStrategy(StageExecutionStrategy):
            def execute(self, context: StageContext):
                # Minimal: just return context unchanged
                return Ok(context)
            
            def get_stage_name(self) -> str:
                return "MinimalStage"
            
            def get_dependencies(self) -> list[str]:
                return []
        
        return MinimalStrategy()
    
    def test_execute_accepts_stage_context(self, minimal_strategy):
        """execute() MUST accept StageContext parameter."""
        context = StageContext(user_request="test")
        result = minimal_strategy.execute(context)
        assert result.is_ok()
    
    def test_execute_returns_result(self, minimal_strategy):
        """execute() MUST return Result type."""
        context = StageContext(user_request="test")
        result = minimal_strategy.execute(context)
        
        # Result has is_ok() and is_err() methods
        assert hasattr(result, 'is_ok')
        assert hasattr(result, 'is_err')
    
    def test_execute_returns_stage_context_on_success(self, minimal_strategy):
        """execute() MUST return StageContext on success."""
        context = StageContext(user_request="test")
        result = minimal_strategy.execute(context)
        
        assert result.is_ok()
        returned_context = result.unwrap()
        assert isinstance(returned_context, StageContext)
    
    def test_execute_returns_error_string_on_failure(self):
        """execute() MUST return error string on failure."""
        class FailingStrategy(StageExecutionStrategy):
            def execute(self, context: StageContext):
                return Err("Stage failed due to X")
            
            def get_stage_name(self) -> str:
                return "FailingStage"
            
            def get_dependencies(self) -> list[str]:
                return []
        
        strategy = FailingStrategy()
        context = StageContext(user_request="test")
        result = strategy.execute(context)
        
        assert result.is_err()
        error_result = result  # Err object
        assert isinstance(error_result.error, str)
        assert "failed" in error_result.error.lower()
    
    def test_get_stage_name_returns_string(self, minimal_strategy):
        """get_stage_name() MUST return string."""
        name = minimal_strategy.get_stage_name()
        assert isinstance(name, str)
        assert len(name) > 0
    
    def test_get_dependencies_returns_list(self, minimal_strategy):
        """get_dependencies() MUST return list of strings."""
        deps = minimal_strategy.get_dependencies()
        assert isinstance(deps, list)
        assert all(isinstance(d, str) for d in deps)
    
    def test_validate_dependencies_succeeds_when_deps_available(self, minimal_strategy):
        """validate_dependencies() MUST succeed when all deps available."""
        # Minimal strategy has no dependencies
        result = minimal_strategy.validate_dependencies()
        assert result.is_ok()
    
    def test_validate_dependencies_fails_when_deps_missing(self):
        """validate_dependencies() MUST fail when deps missing."""
        class DependentStrategy(StageExecutionStrategy):
            def execute(self, context: StageContext):
                return Ok(context)
            
            def get_stage_name(self) -> str:
                return "DependentStage"
            
            def get_dependencies(self) -> list[str]:
                return ["NonExistentOrchestrator"]
        
        strategy = DependentStrategy()
        result = strategy.validate_dependencies()
        
        assert result.is_err()
        error_result = result  # Err object
        assert "missing" in error_result.error.lower()
        assert "NonExistentOrchestrator" in error_result.error


# ============================================================================
# EXECUTION CHECK
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
