"""
Test LENS Integration with IntentRouter (LENS-002)

This test suite verifies the integration of LENS code intelligence
into the IntentRouter for enhanced confidence scoring.

AC: LENS-002 - Wire LENS to IntentRouter Stage 2
Phase: 7.1 - LENS Protocol Formalization

CORE Governance:
  - CORE-008: TDD (tests written first, RED → GREEN → REFACTOR)
  - CORE-011: Type hints on all test functions
  - CORE-012: Docstrings (Google style)
  - CORE-027: Audit trail validation
"""

import pytest
import json
from typing import Dict, Any
from unittest.mock import Mock, patch

from cortex.orchestrators.core.intent_router import (
    IntentRouter,
    RoutingDecision
)
from cortex.models.canonical_enums import IntentType


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def intent_router() -> IntentRouter:
    """Create IntentRouter instance for testing."""
    return IntentRouter()


@pytest.fixture
def mock_lens_context() -> Dict[str, Any]:
    """Create mock LENS context with code intelligence data."""
    return {
        "git_analysis": {
            "recent_commits": [
                {"hash": "abc123", "message": "fix: resolve race condition"},
                {"hash": "def456", "message": "fix: handle edge case"}
            ]
        },
        "ast_analysis": {
            "functions": [{"name": "process_data", "complexity": 15}],
            "classes": [{"name": "DataProcessor", "methods": 8}]
        },
        "comment_analysis": {
            "todos": [{"content": "Refactor this", "priority": "high"}]
        }
    }


# ============================================================================
# TEST: Basic LENS Context Injection
# ============================================================================

def test_route_accepts_lens_context(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test that route() accepts lens_context parameter.
    
    RED Phase: This test should fail initially as lens_context
    parameter doesn't exist yet.
    """
    context = {
        "operation": "fix_bug",
        "description": "Fix race condition",
        "keywords": ["fix", "bug"],
        "lens_context": mock_lens_context
    }
    
    result = intent_router.route(context)
    
    assert result is not None
    assert isinstance(result, RoutingDecision)


def test_route_without_lens_context_backward_compat(intent_router: IntentRouter) -> None:
    """
    Test routing without LENS context (backward compatibility).
    
    Existing code without lens_context should continue to work.
    """
    context = {
        "operation": "implement_feature",
        "description": "Add new feature",
        "keywords": ["implement", "new"]
    }
    
    result = intent_router.route(context)
    
    assert result is not None
    assert result.intent_type == IntentType.IMPLEMENT


def test_lens_context_stored_in_metadata(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test that LENS context is stored in routing decision metadata.
    
    RED Phase: metadata won't contain lens_context initially.
    """
    context = {
        "operation": "refactor_code",
        "keywords": ["refactor"],
        "lens_context": mock_lens_context
    }
    
    result = intent_router.route(context)
    
    assert "lens_enhanced" in result.metadata
    assert result.metadata["lens_enhanced"] is True


# ============================================================================
# TEST: Confidence Score Enhancement
# ============================================================================

def test_lens_boosts_confidence_for_matching_pattern(intent_router: IntentRouter) -> None:
    """
    Test that LENS data boosts confidence when patterns match.
    
    When git history shows fix commits and intent is FIX,
    confidence should be higher than without LENS.
    
    RED Phase: No confidence boost mechanism exists yet.
    """
    # Context without LENS
    context_no_lens = {
        "operation": "fix_issue",
        "keywords": ["fix"],
        "description": "Fix the bug"
    }
    
    # Context with LENS showing fix pattern
    context_with_lens = {
        **context_no_lens,
        "lens_context": {
            "git_analysis": {
                "recent_commits": [
                    {"message": "fix: bug 1"},
                    {"message": "fix: bug 2"},
                    {"message": "fix: bug 3"}
                ]
            },
            "ast_analysis": {"functions": [], "classes": []},
            "comment_analysis": {"todos": []}
        }
    }
    
    result_no_lens = intent_router.route(context_no_lens)
    result_with_lens = intent_router.route(context_with_lens)
    
    assert result_with_lens.confidence_score > result_no_lens.confidence_score


def test_lens_detects_complexity_for_refactor(intent_router: IntentRouter) -> None:
    """
    Test that AST complexity detection boosts refactor confidence.
    
    When LENS AST shows high complexity (many functions/classes),
    refactor intent confidence should increase.
    
    RED Phase: No AST complexity analysis exists yet.
    """
    context = {
        "operation": "refactor_module",
        "keywords": ["refactor", "complex"],
        "lens_context": {
            "git_analysis": {"recent_commits": []},
            "ast_analysis": {
                "functions": [{"name": f"func{i}", "complexity": 10} for i in range(20)],
                "classes": [{"name": f"Class{i}", "methods": 15} for i in range(10)]
            },
            "comment_analysis": {"todos": []}
        }
    }
    
    result = intent_router.route(context)
    
    assert result.intent_type == IntentType.REFACTOR
    assert result.confidence_score >= 0.85
    assert "ast_complexity_detected" in result.metadata


def test_lens_identifies_todos_for_refactor_intent(intent_router: IntentRouter) -> None:
    """
    Test that TODO comments influence refactor intent detection.
    
    When LENS finds TODO/FIXME comments about refactoring,
    refactor intent confidence should increase.
    
    RED Phase: No TODO analysis for intent detection exists yet.
    """
    context = {
        "operation": "improve_code",
        "keywords": ["improve"],
        "lens_context": {
            "git_analysis": {"recent_commits": []},
            "ast_analysis": {"functions": [], "classes": []},
            "comment_analysis": {
                "todos": [
                    {"content": "TODO: Refactor this mess", "priority": "high"},
                    {"content": "FIXME: Clean up this code", "priority": "medium"}
                ]
            }
        }
    }
    
    result = intent_router.route(context)
    
    assert result.intent_type == IntentType.REFACTOR
    assert "todo_refactor_hints" in result.metadata


# ============================================================================
# TEST: LENS Intelligence Extraction
# ============================================================================

def test_extract_git_pattern_from_lens(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test extraction of git commit patterns from LENS.
    
    Should identify predominant commit type from recent history.
    
    RED Phase: _extract_git_pattern method doesn't exist yet.
    """
    pattern = intent_router._extract_git_pattern(mock_lens_context)
    
    assert pattern is not None
    assert pattern in [IntentType.FIX, IntentType.IMPLEMENT, IntentType.REFACTOR]


def test_calculate_ast_complexity_from_lens(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test calculation of code complexity from AST data.
    
    Should return complexity score based on functions/classes.
    
    RED Phase: _calculate_ast_complexity method doesn't exist yet.
    """
    complexity = intent_router._calculate_ast_complexity(mock_lens_context)
    
    assert isinstance(complexity, (int, float))
    assert complexity >= 0


def test_analyze_comment_intent_hints(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test analysis of intent hints from comments.
    
    Should extract refactor/fix/implement hints from TODOs.
    
    RED Phase: _analyze_comment_hints method doesn't exist yet.
    """
    hints = intent_router._analyze_comment_hints(mock_lens_context)
    
    assert isinstance(hints, dict)
    assert "refactor_hints" in hints or "fix_hints" in hints or "implement_hints" in hints


# ============================================================================
# TEST: Confidence Calculation with LENS
# ============================================================================

def test_calculate_lens_confidence_boost(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test LENS confidence boost calculation.
    
    Should return a boost value (0.0-0.3) based on LENS evidence.
    
    RED Phase: _calculate_lens_boost method doesn't exist yet.
    """
    base_confidence = 0.7
    intent_type = IntentType.FIX
    
    boost = intent_router._calculate_lens_boost(intent_type, mock_lens_context)
    
    assert isinstance(boost, float)
    assert 0.0 <= boost <= 0.3


def test_final_confidence_capped_at_one(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test that final confidence never exceeds 1.0.
    
    Even with maximum LENS boost, confidence should be capped.
    
    RED Phase: Will pass initially, tests the cap logic.
    """
    # Start with high base confidence
    high_confidence_context = {
        "operation": "fix_critical_bug",
        "keywords": ["fix", "bug", "critical", "urgent", "emergency"],
        "lens_context": mock_lens_context
    }
    
    result = intent_router.route(high_confidence_context)
    
    assert result.confidence_score <= 1.0


# ============================================================================
# TEST: Error Handling
# ============================================================================

def test_handles_malformed_lens_context(intent_router: IntentRouter) -> None:
    """
    Test graceful handling of malformed LENS context.
    
    Should not crash when LENS context has unexpected structure.
    """
    malformed_lens = {
        "git_analysis": "not_a_dict",  # Should be dict
        "invalid_key": 123
    }
    
    context = {
        "operation": "test_op",
        "keywords": ["test"],
        "lens_context": malformed_lens
    }
    
    # Should not raise exception
    result = intent_router.route(context)
    
    assert result is not None
    assert isinstance(result, RoutingDecision)


def test_handles_none_lens_context(intent_router: IntentRouter) -> None:
    """
    Test handling when lens_context is explicitly None.
    
    Should fall back to non-LENS routing.
    """
    context = {
        "operation": "implement_feature",
        "keywords": ["implement"],
        "lens_context": None
    }
    
    result = intent_router.route(context)
    
    assert result is not None
    assert result.metadata.get("lens_enhanced", False) is False


def test_handles_empty_lens_data(intent_router: IntentRouter) -> None:
    """
    Test handling when LENS returns empty analysis.
    
    Should work with base confidence when no LENS insights available.
    """
    empty_lens = {
        "git_analysis": {"recent_commits": []},
        "ast_analysis": {"functions": [], "classes": []},
        "comment_analysis": {"todos": []}
    }
    
    context = {
        "operation": "refactor_code",
        "keywords": ["refactor"],
        "lens_context": empty_lens
    }
    
    result = intent_router.route(context)
    
    assert result is not None
    # Should use base confidence (0.5-0.8 range typical)
    assert 0.4 <= result.confidence_score <= 0.9


# ============================================================================
# TEST: Audit Trail
# ============================================================================

def test_lens_usage_logged_to_audit_trail(intent_router: IntentRouter, mock_lens_context: Dict[str, Any]) -> None:
    """
    Test that LENS usage is logged in audit trail.
    
    Should create audit entry when LENS context is used.
    
    RED Phase: No LENS-specific audit logging exists yet.
    """
    context = {
        "operation": "fix_bug",
        "keywords": ["fix"],
        "lens_context": mock_lens_context
    }
    
    result = intent_router.route(context)
    
    # Check audit trail
    audit_result = intent_router.get_audit_trail(limit=5)
    assert audit_result.is_ok()
    
    audit_entries = audit_result.unwrap()
    # Should have at least one entry with LENS reference
    lens_entries = [e for e in audit_entries if "LENS" in json.dumps(e)]
    assert len(lens_entries) > 0
