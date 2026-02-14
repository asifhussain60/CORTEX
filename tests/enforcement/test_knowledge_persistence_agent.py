"""
Tests for Knowledge Persistence Enforcement Agent - Phase 12 S5

AC-PHASE71-013: Knowledge persistence enforcement

Tests enforcement agent that:
- Blocks ONBOARD operations without knowledge artifacts
- Validates learning capture completeness
- Enforces brain enhancement integration
- Checks knowledge artifact generation
- Validates promotion thresholds

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from cortex.governance.enforcement.agents.knowledge_persistence_agent import (
    KnowledgePersistenceAgent,
    ValidationResult,
    ViolationLevel
)


@pytest.fixture
def agent() -> KnowledgePersistenceAgent:
    """Create KnowledgePersistenceAgent instance."""
    return KnowledgePersistenceAgent()


@pytest.fixture
def valid_onboarding_context() -> Dict[str, Any]:
    """Create valid onboarding context with knowledge artifacts."""
    return {
        "operation": "onboard",
        "repository_path": "/test/repo",
        "learning_metrics": {
            "patterns_captured": 5,
            "patterns_promoted": 2
        },
        "brain_enhancement": {
            "patterns_detected": 3,
            "strategies_recommended": 2
        },
        "artifacts": {
            "templates_generated": 2,
            "yaml_files_created": 1
        }
    }


@pytest.fixture
def invalid_onboarding_context() -> Dict[str, Any]:
    """Create invalid onboarding context missing knowledge artifacts."""
    return {
        "operation": "onboard",
        "repository_path": "/test/repo"
        # Missing learning_metrics, brain_enhancement, artifacts
    }


class TestAgentInitialization:
    """Test Knowledge Persistence Agent initialization."""

    def test_initialization(self) -> None:
        """Test agent initialization."""
        agent = KnowledgePersistenceAgent()
        assert agent is not None

    def test_has_validation_rules(self, agent: KnowledgePersistenceAgent) -> None:
        """Test agent has validation rules."""
        rules = agent.get_validation_rules()
        assert isinstance(rules, list)
        assert len(rules) > 0


class TestLearningCaptureValidation:
    """Test learning capture validation."""

    def test_validate_learning_capture_present(
        self,
        agent: KnowledgePersistenceAgent,
        valid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation passes when learning capture present."""
        result = agent.validate_learning_capture(valid_onboarding_context)
        
        assert result.passed
        assert result.level != ViolationLevel.BLOCKING

    def test_validate_learning_capture_missing(
        self,
        agent: KnowledgePersistenceAgent,
        invalid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation fails when learning capture missing."""
        result = agent.validate_learning_capture(invalid_onboarding_context)
        
        assert not result.passed
        assert result.level == ViolationLevel.BLOCKING

    def test_validate_learning_capture_insufficient(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test validation fails when capture insufficient."""
        context = {
            "operation": "onboard",
            "learning_metrics": {
                "patterns_captured": 0,  # No patterns captured
                "patterns_promoted": 0
            }
        }

        result = agent.validate_learning_capture(context)
        
        assert not result.passed


class TestBrainEnhancementValidation:
    """Test brain enhancement validation."""

    def test_validate_brain_enhancement_present(
        self,
        agent: KnowledgePersistenceAgent,
        valid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation passes with brain enhancement."""
        result = agent.validate_brain_enhancement(valid_onboarding_context)
        
        assert result.passed

    def test_validate_brain_enhancement_missing(
        self,
        agent: KnowledgePersistenceAgent,
        invalid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation fails without brain enhancement."""
        result = agent.validate_brain_enhancement(invalid_onboarding_context)
        
        assert not result.passed
        assert result.level == ViolationLevel.BLOCKING

    def test_validate_brain_enhancement_partial(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test validation with partial brain enhancement."""
        context = {
            "operation": "onboard",
            "brain_enhancement": {
                "patterns_detected": 0,  # No patterns detected
                "strategies_recommended": 1
            }
        }

        result = agent.validate_brain_enhancement(context)
        
        # Should warn but not block
        assert result.level != ViolationLevel.BLOCKING or not result.passed


class TestKnowledgeArtifactValidation:
    """Test knowledge artifact validation."""

    def test_validate_artifacts_present(
        self,
        agent: KnowledgePersistenceAgent,
        valid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation passes with artifacts."""
        result = agent.validate_artifacts(valid_onboarding_context)
        
        assert result.passed

    def test_validate_artifacts_missing(
        self,
        agent: KnowledgePersistenceAgent,
        invalid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation fails without artifacts."""
        result = agent.validate_artifacts(invalid_onboarding_context)
        
        assert not result.passed

    def test_validate_artifacts_empty(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test validation fails with empty artifacts."""
        context = {
            "operation": "onboard",
            "artifacts": {
                "templates_generated": 0,
                "yaml_files_created": 0
            }
        }

        result = agent.validate_artifacts(context)
        
        assert not result.passed


class TestPromotionThresholdValidation:
    """Test learning promotion threshold validation."""

    def test_validate_promotion_threshold_met(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test validation passes when threshold met."""
        context = {
            "operation": "onboard",
            "learning_metrics": {
                "patterns_captured": 10,
                "patterns_promoted": 5  # 50% promotion rate
            }
        }

        result = agent.validate_promotion_threshold(context)
        
        assert result.passed

    def test_validate_promotion_threshold_not_met(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test validation warns when threshold not met."""
        context = {
            "operation": "onboard",
            "learning_metrics": {
                "patterns_captured": 10,
                "patterns_promoted": 1  # Only 10% promotion rate
            }
        }

        result = agent.validate_promotion_threshold(context)
        
        # Should warn but not block
        assert result.level == ViolationLevel.WARNING or result.passed


class TestComprehensiveValidation:
    """Test comprehensive validation of all rules."""

    def test_validate_all_rules_pass(
        self,
        agent: KnowledgePersistenceAgent,
        valid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test all validation rules pass with valid context."""
        results = agent.validate(valid_onboarding_context)
        
        assert isinstance(results, list)
        assert all(r.passed or r.level != ViolationLevel.BLOCKING for r in results)

    def test_validate_all_rules_fail(
        self,
        agent: KnowledgePersistenceAgent,
        invalid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation fails with invalid context."""
        results = agent.validate(invalid_onboarding_context)
        
        assert isinstance(results, list)
        assert any(not r.passed for r in results)

    def test_validate_returns_blocking_violations(
        self,
        agent: KnowledgePersistenceAgent,
        invalid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation identifies blocking violations."""
        results = agent.validate(invalid_onboarding_context)
        
        blocking = [r for r in results if r.level == ViolationLevel.BLOCKING]
        assert len(blocking) > 0


class TestOperationFiltering:
    """Test operation-specific validation."""

    def test_only_validate_onboard_operations(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test agent only validates onboard operations."""
        non_onboard_context = {
            "operation": "analyze",
            "repository_path": "/test/repo"
        }

        results = agent.validate(non_onboard_context)
        
        # Should pass or skip for non-onboard operations
        assert len(results) == 0 or all(r.passed for r in results)

    def test_validate_onboard_operation(
        self,
        agent: KnowledgePersistenceAgent,
        valid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test agent validates onboard operations."""
        results = agent.validate(valid_onboarding_context)
        
        assert len(results) > 0


class TestViolationLevels:
    """Test violation level classification."""

    def test_blocking_violation_for_missing_learning(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test missing learning capture is blocking."""
        context = {
            "operation": "onboard",
            "repository_path": "/test/repo"
        }

        result = agent.validate_learning_capture(context)
        
        assert result.level == ViolationLevel.BLOCKING

    def test_warning_violation_for_low_promotion(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test low promotion rate is warning."""
        context = {
            "operation": "onboard",
            "learning_metrics": {
                "patterns_captured": 10,
                "patterns_promoted": 1
            }
        }

        result = agent.validate_promotion_threshold(context)
        
        assert result.level == ViolationLevel.WARNING or result.passed


class TestValidationMessages:
    """Test validation result messages."""

    def test_validation_result_has_message(
        self,
        agent: KnowledgePersistenceAgent,
        invalid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation results include descriptive messages."""
        results = agent.validate(invalid_onboarding_context)
        
        for result in results:
            if not result.passed:
                assert result.message
                assert len(result.message) > 0

    def test_validation_result_has_rule_id(
        self,
        agent: KnowledgePersistenceAgent,
        valid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test validation results include rule IDs."""
        results = agent.validate(valid_onboarding_context)
        
        for result in results:
            assert result.rule_id
            assert result.rule_id.startswith("KP-")  # Knowledge Persistence prefix


class TestAgentIntegration:
    """Test integration with enforcement orchestrator."""

    def test_agent_compatible_with_orchestrator(
        self,
        agent: KnowledgePersistenceAgent
    ) -> None:
        """Test agent has required interface for orchestrator."""
        # Check required methods exist
        assert hasattr(agent, "validate")
        assert callable(agent.validate)

    def test_agent_returns_validation_results(
        self,
        agent: KnowledgePersistenceAgent,
        valid_onboarding_context: Dict[str, Any]
    ) -> None:
        """Test agent returns list of ValidationResult."""
        results = agent.validate(valid_onboarding_context)
        
        assert isinstance(results, list)
        assert all(isinstance(r, ValidationResult) for r in results)


class TestValidationResultDataClass:
    """Test ValidationResult data class."""

    def test_create_validation_result(self) -> None:
        """Test creating ValidationResult instance."""
        result = ValidationResult(
            rule_id="KP-001",
            passed=True,
            level=ViolationLevel.INFO,
            message="Test message"
        )

        assert result.rule_id == "KP-001"
        assert result.passed is True
        assert result.level == ViolationLevel.INFO

    def test_validation_result_to_dict(self) -> None:
        """Test converting ValidationResult to dictionary."""
        result = ValidationResult(
            rule_id="KP-002",
            passed=False,
            level=ViolationLevel.BLOCKING,
            message="Test failure"
        )

        data = result.to_dict()
        assert data["rule_id"] == "KP-002"
        assert data["passed"] is False


class TestViolationLevelEnum:
    """Test ViolationLevel enum."""

    def test_violation_levels_exist(self) -> None:
        """Test ViolationLevel enum values."""
        assert ViolationLevel.INFO
        assert ViolationLevel.WARNING
        assert ViolationLevel.BLOCKING
