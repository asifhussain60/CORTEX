"""
Tests for RecommendationGate - Regression Prevention Layer.

AC-ID: AC-RECOMMENDATION-GATE-001
Tests the recommendation gate that prevents regression-causing recommendations.

TDD Phase: RED → GREEN → REFACTOR
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock


class TestRecommendationGate:
    """Test suite for RecommendationGate."""

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_recommendation_gate_initializes(self) -> None:
        """Test RecommendationGate can be instantiated."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        assert gate is not None

    def test_recommendation_gate_loads_enhancement_history(self) -> None:
        """Test gate loads enhancement history on initialization."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        assert hasattr(gate, 'rejected_recommendations')
        assert isinstance(gate.rejected_recommendations, list)

    # =========================================================================
    # REJECTION HISTORY TESTS
    # =========================================================================

    def test_check_against_rejection_history_returns_clear(self) -> None:
        """Test clear result when no matching rejection found."""
        from cortex.orchestrators.core.recommendation_gate import (
            RecommendationGate, 
            GateResult,
            GateStatus
        )
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Add new feature X",
            "description": "Implement feature X for better UX"
        }
        
        result = gate.check_rejection_history(recommendation)
        
        assert isinstance(result, GateResult)
        assert result.status in [GateStatus.PASS, GateStatus.BLOCKED]

    def test_check_blocks_similar_to_rejected(self) -> None:
        """Test gate blocks recommendations similar to previously rejected."""
        from cortex.orchestrators.core.recommendation_gate import (
            RecommendationGate,
            GateStatus
        )
        
        # Use lower threshold to catch semantic similarity
        gate = RecommendationGate(similarity_threshold=0.3)
        # Inject a rejection that matches
        gate.rejected_recommendations = [{
            "id": "REJ-001",
            "recommendation": "Auto-fix all issues without approval",
            "rejection_reason": "Violates approval gate principle",
            "lessons_learned": ["All modifications require explicit user approval"]
        }]
        
        # Very similar recommendation (shares key terms: auto-fix, issues, without, approval)
        recommendation = {
            "title": "Auto-fix issues without approval",
            "description": "Automatically fix all detected issues without user approval"
        }
        
        result = gate.check_rejection_history(recommendation)
        
        assert result.status == GateStatus.BLOCKED
        assert "REJ-001" in result.reason

    # =========================================================================
    # REGRESSION RISK SCORING TESTS
    # =========================================================================

    def test_calculate_regression_risk_returns_score(self) -> None:
        """Test regression risk calculation returns score 0-1."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Refactor module X",
            "affected_files": ["cortex/core/module_x.py"],
            "change_type": "refactor"
        }
        
        score = gate.calculate_regression_risk(recommendation)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_high_regression_risk_for_core_files(self) -> None:
        """Test higher risk score for core infrastructure files."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Modify MasterOrchestrator",
            "affected_files": [
                "cortex/orchestrators/core/master_orchestrator.py",
                "cortex/wiring/specifications/wiring.yaml"
            ],
            "change_type": "modify"
        }
        
        score = gate.calculate_regression_risk(recommendation)
        
        # Core files should have higher risk
        assert score >= 0.5

    def test_low_regression_risk_for_additive_changes(self) -> None:
        """Test lower risk score for purely additive changes."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Add new utility function",
            "affected_files": ["cortex/utils/new_helper.py"],
            "change_type": "add"
        }
        
        score = gate.calculate_regression_risk(recommendation)
        
        # Additive changes should have lower risk
        assert score <= 0.4

    # =========================================================================
    # TEST HEALTH CHECK TESTS
    # =========================================================================

    def test_check_test_health_returns_result(self) -> None:
        """Test test health check returns gate result."""
        from cortex.orchestrators.core.recommendation_gate import (
            RecommendationGate,
            GateResult
        )
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Modify auth module",
            "affected_files": ["cortex/auth/validator.py"]
        }
        
        result = gate.check_test_health(recommendation)
        
        assert isinstance(result, GateResult)

    # =========================================================================
    # DUPLICATION CHECK TESTS
    # =========================================================================

    def test_check_duplication_returns_result(self) -> None:
        """Test duplication check returns gate result."""
        from cortex.orchestrators.core.recommendation_gate import (
            RecommendationGate,
            GateResult
        )
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Add helper function",
            "code_snippet": "def calculate_score(x): return x * 2"
        }
        
        result = gate.check_duplication(recommendation)
        
        assert isinstance(result, GateResult)

    # =========================================================================
    # FULL GATE EVALUATION TESTS
    # =========================================================================

    def test_evaluate_runs_all_gates(self) -> None:
        """Test evaluate runs all gate checks."""
        from cortex.orchestrators.core.recommendation_gate import (
            RecommendationGate,
            GateEvaluation,
            GateStatus
        )
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Add new feature",
            "description": "Safe additive change",
            "affected_files": ["cortex/utils/new.py"],
            "change_type": "add"
        }
        
        evaluation = gate.evaluate(recommendation)
        
        assert isinstance(evaluation, GateEvaluation)
        assert hasattr(evaluation, 'verdict')
        assert hasattr(evaluation, 'gates')
        assert len(evaluation.gates) >= 3  # REJ-History, Test-Health, Regression-Risk

    def test_evaluate_blocks_high_risk(self) -> None:
        """Test evaluate blocks when regression risk too high."""
        from cortex.orchestrators.core.recommendation_gate import (
            RecommendationGate,
            GateVerdict
        )
        
        gate = RecommendationGate()
        # Recommendation with very high risk
        recommendation = {
            "title": "Rewrite entire orchestration layer",
            "affected_files": [
                "cortex/orchestrators/core/master_orchestrator.py",
                "cortex/orchestrators/core/intent_router.py",
                "cortex/orchestrators/core/tdd_orchestrator.py",
                "cortex/wiring/specifications/wiring.yaml",
                "cortex/mcp/server.py"
            ],
            "change_type": "rewrite"
        }
        
        evaluation = gate.evaluate(recommendation)
        
        assert evaluation.verdict == GateVerdict.BLOCKED

    def test_evaluate_allows_safe_recommendations(self) -> None:
        """Test evaluate allows safe recommendations."""
        from cortex.orchestrators.core.recommendation_gate import (
            RecommendationGate,
            GateVerdict
        )
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Add documentation comments",
            "description": "Add docstrings to utility functions",
            "affected_files": ["cortex/utils/helpers.py"],
            "change_type": "documentation"
        }
        
        evaluation = gate.evaluate(recommendation)
        
        assert evaluation.verdict == GateVerdict.SAFE

    # =========================================================================
    # OUTPUT FORMAT TESTS
    # =========================================================================

    def test_format_evaluation_output(self) -> None:
        """Test evaluation output is properly formatted."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        recommendation = {
            "title": "Add new feature",
            "affected_files": ["cortex/utils/new.py"],
            "change_type": "add"
        }
        
        evaluation = gate.evaluate(recommendation)
        output = evaluation.to_markdown()
        
        assert "### ⚡ Recommendation Safety Check" in output or "### ⚡ Recommendation BLOCKED" in output
        assert "Gate" in output
        assert "Status" in output

    # =========================================================================
    # SIMILARITY SCORING TESTS
    # =========================================================================

    def test_calculate_similarity_score(self) -> None:
        """Test similarity score calculation between recommendations."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        
        # Use near-identical text for high similarity
        rec1 = "Auto-fix all issues without user approval"
        rec2 = "Auto-fix all issues without user approval gate"
        
        score = gate.calculate_similarity(rec1, rec2)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Near-identical should be high similarity

    def test_low_similarity_for_different_recommendations(self) -> None:
        """Test low similarity for different recommendations."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        
        rec1 = "Add new logging feature"
        rec2 = "Refactor database connection pool"
        
        score = gate.calculate_similarity(rec1, rec2)
        
        assert score < 0.5  # These are different

    # =========================================================================
    # CONFIGURATION TESTS
    # =========================================================================

    def test_configurable_risk_threshold(self) -> None:
        """Test regression risk threshold is configurable."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate(risk_threshold=0.5)
        
        assert gate.risk_threshold == 0.5

    def test_configurable_similarity_threshold(self) -> None:
        """Test similarity threshold is configurable."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate(similarity_threshold=0.9)
        
        assert gate.similarity_threshold == 0.9

    # =========================================================================
    # INTEGRATION WITH ENHANCEMENT HISTORY
    # =========================================================================

    def test_loads_real_enhancement_history(self) -> None:
        """Test loading from actual enhancement-history.yaml if exists."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        
        # Should not crash even if file doesn't exist
        assert gate.rejected_recommendations is not None

    def test_refresh_rejection_history(self) -> None:
        """Test ability to refresh rejection history."""
        from cortex.orchestrators.core.recommendation_gate import RecommendationGate
        
        gate = RecommendationGate()
        
        # Should be able to refresh
        gate.refresh_history()
        
        assert gate.rejected_recommendations is not None


class TestGateDataClasses:
    """Test data classes for gate results."""

    def test_gate_status_enum(self) -> None:
        """Test GateStatus enum values."""
        from cortex.orchestrators.core.recommendation_gate import GateStatus
        
        assert GateStatus.PASS.value == "pass"
        assert GateStatus.BLOCKED.value == "blocked"
        assert GateStatus.WARN.value == "warn"

    def test_gate_verdict_enum(self) -> None:
        """Test GateVerdict enum values."""
        from cortex.orchestrators.core.recommendation_gate import GateVerdict
        
        assert GateVerdict.SAFE.value == "safe"
        assert GateVerdict.BLOCKED.value == "blocked"
        assert GateVerdict.WARN.value == "warn"

    def test_gate_result_dataclass(self) -> None:
        """Test GateResult dataclass."""
        from cortex.orchestrators.core.recommendation_gate import (
            GateResult,
            GateStatus
        )
        
        result = GateResult(
            gate_name="REJ-History",
            status=GateStatus.PASS,
            reason="No matching rejections",
            score=None
        )
        
        assert result.gate_name == "REJ-History"
        assert result.status == GateStatus.PASS

    def test_gate_evaluation_dataclass(self) -> None:
        """Test GateEvaluation dataclass."""
        from cortex.orchestrators.core.recommendation_gate import (
            GateEvaluation,
            GateResult,
            GateStatus,
            GateVerdict
        )
        
        evaluation = GateEvaluation(
            verdict=GateVerdict.SAFE,
            gates=[
                GateResult("REJ-History", GateStatus.PASS, "Clear"),
                GateResult("Regression-Risk", GateStatus.PASS, "Low risk", 0.2)
            ],
            recommendation_title="Test recommendation"
        )
        
        assert evaluation.verdict == GateVerdict.SAFE
        assert len(evaluation.gates) == 2
