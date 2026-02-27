"""
Phase 87 — cortex_learning op='rca' MCP Tool Tests (RED phase — CORE-008)
Tests for the CortexLearning._op_rca() method added in Phase 87.

AC-PHASE87-007: cortex_learning rca op tests
CORE-008: TDD mandatory
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

import pytest


@pytest.fixture
def learning_tool():
    """Return a CortexLearning tool instance."""
    from cortex.mcp.tools.learning_tool import CortexLearning
    return CortexLearning()


# ---------------------------------------------------------------------------
# op='rca' dispatch
# ---------------------------------------------------------------------------
class TestCortexLearningRCADispatch:
    """cortex_learning must route op='rca' to the RCA handler."""

    def test_op_rca_is_supported(self, learning_tool) -> None:
        """op='rca' must not return 'Unknown operation' error."""
        result = learning_tool.execute(op="rca", action="summary")
        assert result.success is True or (
            result.success is False and "Unknown operation" not in (result.error or "")
        )

    def test_supported_ops_include_rca(self, learning_tool) -> None:
        """Calling an unknown op must list 'rca' in supported_operations."""
        result = learning_tool.execute(op="__unknown__")
        ops = result.data.get("supported_operations", [])
        assert "rca" in ops


# ---------------------------------------------------------------------------
# action='analyze'
# ---------------------------------------------------------------------------
class TestCortexLearningRCAAnalyze:
    """Tests for op='rca' action='analyze'."""

    def test_analyze_returns_success(self, learning_tool) -> None:
        """action='analyze' must return success=True."""
        result = learning_tool.execute(
            op="rca",
            action="analyze",
            failure_id="MCP-test-001",
            symptom="Timeout in MCP handler",
            category="technology",
        )
        assert result.success is True

    def test_analyze_returns_rca_id(self, learning_tool) -> None:
        """action='analyze' result data must contain rca_id."""
        result = learning_tool.execute(
            op="rca",
            action="analyze",
            failure_id="MCP-test-002",
            symptom="NullPointerException in orchestrator",
            category="technology",
        )
        assert "rca_id" in result.data
        assert result.data["rca_id"].startswith("RCA-")

    def test_analyze_includes_root_cause(self, learning_tool) -> None:
        """action='analyze' result data must contain root_cause."""
        result = learning_tool.execute(
            op="rca",
            action="analyze",
            failure_id="MCP-test-003",
            symptom="Import error on module load",
            category="technology",
        )
        assert "root_cause" in result.data
        assert len(result.data["root_cause"]) > 0

    def test_analyze_includes_gate_level(self, learning_tool) -> None:
        """action='analyze' result data must contain gate_level."""
        result = learning_tool.execute(
            op="rca",
            action="analyze",
            failure_id="MCP-test-004",
            symptom="Type error in response handler",
            category="technology",
        )
        assert "gate_level" in result.data

    def test_analyze_accepts_methodology_override(self, learning_tool) -> None:
        """action='analyze' must accept explicit methodology param."""
        result = learning_tool.execute(
            op="rca",
            action="analyze",
            failure_id="MCP-test-005",
            symptom="Build failure after dependency upgrade",
            category="process",
            methodology="fishbone",
        )
        assert result.success is True
        assert result.data.get("methodology") == "fishbone"


# ---------------------------------------------------------------------------
# action='summary'
# ---------------------------------------------------------------------------
class TestCortexLearningRCASummary:
    """Tests for op='rca' action='summary'."""

    def test_summary_returns_success(self, learning_tool) -> None:
        """action='summary' must return success=True."""
        result = learning_tool.execute(op="rca", action="summary")
        assert result.success is True

    def test_summary_returns_count(self, learning_tool) -> None:
        """action='summary' result data must contain 'count' integer."""
        result = learning_tool.execute(op="rca", action="summary")
        assert "count" in result.data
        assert isinstance(result.data["count"], int)

    def test_summary_returns_analyses_list(self, learning_tool) -> None:
        """action='summary' result data must contain 'analyses' list."""
        result = learning_tool.execute(op="rca", action="summary")
        assert "analyses" in result.data
        assert isinstance(result.data["analyses"], list)


# ---------------------------------------------------------------------------
# action='review_required'
# ---------------------------------------------------------------------------
class TestCortexLearningRCAReviewRequired:
    """Tests for op='rca' action='review_required'."""

    def test_review_required_returns_success(self, learning_tool) -> None:
        """action='review_required' must return success=True."""
        result = learning_tool.execute(op="rca", action="review_required")
        assert result.success is True

    def test_review_required_returns_count(self, learning_tool) -> None:
        """action='review_required' result data must contain 'count'."""
        result = learning_tool.execute(op="rca", action="review_required")
        assert "count" in result.data


# ---------------------------------------------------------------------------
# action='bypass_gate'
# ---------------------------------------------------------------------------
class TestCortexLearningRCABypassGate:
    """Tests for op='rca' action='bypass_gate'."""

    def test_bypass_gate_returns_success(self, learning_tool) -> None:
        """action='bypass_gate' must return success=True."""
        result = learning_tool.execute(
            op="rca",
            action="bypass_gate",
            rule_id="RULE-001",
            reason="False positive — reviewed by senior engineer",
        )
        assert result.success is True

    def test_bypass_gate_echoes_rule_id(self, learning_tool) -> None:
        """action='bypass_gate' result data must echo the bypassed rule_id."""
        result = learning_tool.execute(
            op="rca",
            action="bypass_gate",
            rule_id="RULE-BYPASS-001",
            reason="Manual review completed",
        )
        assert result.data.get("bypassed") == "RULE-BYPASS-001"


# ---------------------------------------------------------------------------
# action='query'
# ---------------------------------------------------------------------------
class TestCortexLearningRCAQuery:
    """Tests for op='rca' action='query'."""

    def test_query_returns_error_for_unknown_id(self, learning_tool) -> None:
        """action='query' with unknown rca_id must return success=False."""
        result = learning_tool.execute(
            op="rca",
            action="query",
            rca_id="NONEXISTENT-RCA-9999",
        )
        assert result.success is False

    def test_query_unknown_action_returns_error(self, learning_tool) -> None:
        """Unknown action must return success=False with supported_actions list."""
        result = learning_tool.execute(op="rca", action="__bad_action__")
        assert result.success is False
        assert "supported_actions" in result.data
