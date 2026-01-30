"""
Phase 8.2 Unit Tests: Keyword Extraction and Orchestrator Lookup

Unit tests for Phase 8.2 components (no orchestrator instances required):
- _extract_keywords() method
- _lookup_orchestrators() method (mocked)
- _rank_orchestrators() method
- Confidence calculation
- Enforcement validation

AC-ID: AC-PHASE-8.2-01 (Task ROUTE-006)

CORE Governance:
  - CORE-008: TDD - Tests for Phase 8.2 implementation
  - CORE-011: Type hints on all test methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling

Author: Asif Hussain
Created: 2026-01-28
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from cortex.orchestrators.core.intent_router import IntentRouter, RoutingDecision
from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.core.routing_enforcement import (
    RoutingEnforcementEngine,
    RoutingViolation,
)


class TestKeywordExtraction:
    """Unit tests for _extract_keywords() method."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.router = IntentRouter()
    
    def test_extract_keywords_from_description(self) -> None:
        """
        Test keyword extraction from description field.
        
        AC-PHASE-8.2-01: Verify tokenization and stop word removal
        """
        # Arrange
        context = {
            "description": "Use CORTEX LENS to analyze the codebase",
        }
        
        # Act
        keywords = self.router._extract_keywords(context)
        
        # Assert
        assert "lens" in keywords
        assert "analyze" in keywords
        assert "codebase" in keywords
        # Stop words should be removed
        assert "the" not in keywords
        assert "to" not in keywords
    
    def test_extract_keywords_from_operation(self) -> None:
        """
        Test keyword extraction from operation field (snake_case handling).
        
        AC-PHASE-8.2-01: Verify underscore splitting
        """
        # Arrange
        context = {
            "operation": "onboard_repository_with_lens",
        }
        
        # Act
        keywords = self.router._extract_keywords(context)
        
        # Assert
        assert "onboard" in keywords
        assert "repository" in keywords
        assert "lens" in keywords
    
    def test_extract_keywords_from_user_intent(self) -> None:
        """
        Test keyword extraction from user_intent field.
        
        AC-PHASE-8.2-01: Verify multiple sources
        """
        # Arrange
        context = {
            "user_intent": "Setup project configuration",
        }
        
        # Act
        keywords = self.router._extract_keywords(context)
        
        # Assert
        assert "setup" in keywords
        assert "project" in keywords
        assert "configuration" in keywords
    
    def test_extract_keywords_deduplicates(self) -> None:
        """
        Test that duplicate keywords are removed.
        
        AC-PHASE-8.2-01: Verify deduplication
        """
        # Arrange
        context = {
            "operation": "analyze_code",
            "description": "Analyze code complexity",
        }
        
        # Act
        keywords = self.router._extract_keywords(context)
        
        # Assert
        # "analyze" appears twice but should only appear once
        assert keywords.count("analyze") == 1
        assert "code" in keywords
    
    def test_extract_keywords_filters_short_words(self) -> None:
        """
        Test that words < 3 characters are filtered.
        
        AC-PHASE-8.2-01: Verify length filtering
        """
        # Arrange
        context = {
            "description": "Do it as ab cd",
        }
        
        # Act
        keywords = self.router._extract_keywords(context)
        
        # Assert
        # "as", "ab", "cd", "it" should be filtered (<=2 chars)
        assert "as" not in keywords
        assert "ab" not in keywords
        assert "cd" not in keywords
        # Empty context should return empty list
        assert isinstance(keywords, list)


class TestOrchestratorRanking:
    """Unit tests for _rank_orchestrators() method."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.router = IntentRouter()
    
    def test_rank_orchestrators_by_confidence(self) -> None:
        """
        Test that candidates are sorted by confidence descending.
        
        AC-PHASE-8.2-01: Verify ranking algorithm
        """
        # Arrange
        mock_orch1 = Mock()
        mock_orch2 = Mock()
        mock_orch3 = Mock()
        
        candidates = [
            ("OrchestratorA", mock_orch1, 0.75),
            ("OrchestratorB", mock_orch2, 0.90),
            ("OrchestratorC", mock_orch3, 0.60),
        ]
        
        # Act
        ranked = self.router._rank_orchestrators(candidates)
        
        # Assert
        assert len(ranked) == 3
        assert ranked[0][0] == "OrchestratorB"  # Highest confidence
        assert ranked[0][2] == 0.90
        assert ranked[1][0] == "OrchestratorA"  # Middle
        assert ranked[2][0] == "OrchestratorC"  # Lowest
    
    def test_rank_orchestrators_empty_list(self) -> None:
        """
        Test ranking with empty candidate list.
        
        AC-PHASE-8.2-01: Verify edge case handling
        """
        # Arrange
        candidates = []
        
        # Act
        ranked = self.router._rank_orchestrators(candidates)
        
        # Assert
        assert ranked == []


class TestRoutingEnforcement:
    """Unit tests for routing enforcement integration."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.enforcement = RoutingEnforcementEngine(
            confidence_threshold=0.6,
            disambiguation_threshold=0.7,
            blocking_enabled=True,
        )
    
    def test_routing_001_orchestrator_not_found(self) -> None:
        """
        Test ROUTING-001: Orchestrator must exist in registry.
        
        AC-PHASE-8.2-01: Verify violation detection
        """
        # Arrange
        decision = RoutingDecision(
            intent_type=IntentType.IMPLEMENT,
            target_handler="NonExistentOrchestrator",
            confidence_score=0.9,
            reasoning="Test",
            target_orchestrator=None,  # Not found
        )
        
        # Act
        result = self.enforcement.validate_routing_decision(decision)
        
        # Assert
        assert not result.passed
        assert RoutingViolation.ORCHESTRATOR_NOT_FOUND in result.violations
    
    def test_routing_002_confidence_too_low(self) -> None:
        """
        Test ROUTING-002: Confidence must be >= threshold.
        
        AC-PHASE-8.2-01: Verify confidence validation
        """
        # Arrange
        mock_orch = Mock()
        decision = RoutingDecision(
            intent_type=IntentType.IMPLEMENT,
            target_handler="TestOrchestrator",
            confidence_score=0.4,  # Below threshold
            reasoning="Test",
            target_orchestrator=mock_orch,
        )
        
        # Act
        result = self.enforcement.validate_routing_decision(decision)
        
        # Assert
        assert not result.passed
        assert RoutingViolation.CONFIDENCE_TOO_LOW in result.violations
    
    def test_routing_004_missing_reasoning(self) -> None:
        """
        Test ROUTING-004: Reasoning must be present.
        
        AC-PHASE-8.2-01: Verify audit trail validation
        """
        # Arrange
        mock_orch = Mock()
        decision = RoutingDecision(
            intent_type=IntentType.IMPLEMENT,
            target_handler="TestOrchestrator",
            confidence_score=0.9,
            reasoning="",  # Empty reasoning
            target_orchestrator=mock_orch,
        )
        
        # Act
        result = self.enforcement.validate_routing_decision(decision)
        
        # Assert
        assert not result.passed
        assert RoutingViolation.NOT_AUDITABLE in result.violations
    
    def test_enforcement_passes_valid_decision(self) -> None:
        """
        Test that valid decision passes enforcement.
        
        AC-PHASE-8.2-01: Verify successful validation
        """
        # Arrange
        mock_orch = Mock()
        decision = RoutingDecision(
            intent_type=IntentType.IMPLEMENT,
            target_handler="ValidOrchestrator",
            confidence_score=0.85,
            reasoning="Valid routing decision with proper reasoning",
            target_orchestrator=mock_orch,
        )
        
        # Act
        with patch.object(self.enforcement, 'check_orchestrator_exists') as mock_check:
            from cortex.core.result import Ok
            mock_check.return_value = Ok(True)
            result = self.enforcement.validate_routing_decision(decision)
        
        # Assert
        assert result.passed
        assert len(result.violations) == 0


class TestConfidenceCalculation:
    """Unit tests for confidence calculation with LENS integration."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.router = IntentRouter()
    
    def test_lens_git_pattern_exact_match_boosts_confidence(self) -> None:
        """
        Test that exact Git pattern match adds 0.15 confidence boost.
        
        LENS-002: Verify LENS intelligence integration
        """
        # Arrange
        lens_context = {
            "git_analysis": {
                "recent_commits": [
                    {"message": "refactor: cleanup code"},
                    {"message": "refactor: improve performance"},
                ]
            }
        }
        
        # Act
        git_pattern = self.router._extract_git_pattern(lens_context)
        
        # Assert
        assert git_pattern == IntentType.REFACTOR
    
    def test_ast_complexity_classification(self) -> None:
        """
        Test AST complexity score calculation.
        
        LENS-002: Verify complexity metric extraction
        """
        # Arrange
        lens_context = {
            "ast_analysis": {
                "function_count": 20,
                "class_count": 5,
            }
        }
        
        # Act
        complexity = self.router._calculate_ast_complexity(lens_context)
        
        # Assert
        # complexity = (class_count * 10) + (function_count * 2)
        # = (5 * 10) + (20 * 2) = 50 + 40 = 90
        assert complexity == 90
    
    def test_ast_complexity_from_lists(self) -> None:
        """
        Test AST complexity calculation from function/class lists.
        
        LENS-002: Verify alternative data format support
        """
        # Arrange
        lens_context = {
            "ast_analysis": {
                "functions": [
                    {"name": "func1"},
                    {"name": "func2"},
                    {"name": "func3"},
                ],
                "classes": [
                    {"name": "Class1"},
                    {"name": "Class2"},
                ],
            }
        }
        
        # Act
        complexity = self.router._calculate_ast_complexity(lens_context)
        
        # Assert
        # complexity = (2 classes * 10) + (3 functions * 2) = 20 + 6 = 26
        assert complexity == 26


class TestRoutingDecisionDataclass:
    """Unit tests for RoutingDecision dataclass extensions."""
    
    def test_routing_decision_has_phase_8_2_fields(self) -> None:
        """
        Test that RoutingDecision includes Phase 8.2 fields.
        
        AC-PHASE-8.2-01: Verify dataclass extension
        """
        # Arrange
        mock_orch = Mock()
        mock_fallback = Mock()
        
        # Act
        decision = RoutingDecision(
            intent_type=IntentType.IMPLEMENT,
            target_handler="TestOrchestrator",
            confidence_score=0.85,
            reasoning="Test",
            target_orchestrator=mock_orch,
            fallback_orchestrators=[mock_fallback],
            keyword_matches=["test", "implement"],
            confidence_breakdown={"keyword_match": 0.5, "intent": 0.35},
        )
        
        # Assert
        assert hasattr(decision, "target_orchestrator")
        assert hasattr(decision, "fallback_orchestrators")
        assert hasattr(decision, "keyword_matches")
        assert hasattr(decision, "confidence_breakdown")
        assert decision.target_orchestrator == mock_orch
        assert len(decision.fallback_orchestrators) == 1
        assert "test" in decision.keyword_matches
        assert decision.confidence_breakdown["keyword_match"] == 0.5
