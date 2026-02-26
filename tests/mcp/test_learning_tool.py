"""
Tests for Phase 83-c: CortexLearning MCP Tool.

Authority: phase-83-unified-reinforcement-signal.yaml GAP-83-05
AC-ID: AC-83-MCP-LEARNING-20260226

RED Phase: All tests must FAIL before implementation begins.

Validates:
- CortexLearning class-based tool follows MCP Tool protocol
- Supports operations: emit, history, decay, promote, quarantine, metrics
- emit operation writes reinforcement signal to learning loop
- history operation returns filtered signal history
- decay/promote/quarantine delegate to EffectivenessAnalyzer
- Tool registered in ALL_TOOLS

CORE Rules:
- CORE-008: TDD mandatory ✅
- CORE-011: Type hints required ✅
- CORE-012: Docstrings required ✅
"""

from __future__ import annotations

from typing import Any, Dict

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# 1. Tool class exists and follows MCP protocol
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexLearningToolProtocol:
    """GAP-83-05: CortexLearning tool follows MCP Tool protocol."""

    def test_cortex_learning_importable(self) -> None:
        """CortexLearning must be importable from cortex.mcp.tools."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        assert CortexLearning is not None

    def test_cortex_learning_is_tool_subclass(self) -> None:
        """CortexLearning must extend mcp_tool_base.Tool."""
        from cortex.mcp.mcp_tool_base import Tool
        from cortex.mcp.tools.learning_tool import CortexLearning

        assert issubclass(CortexLearning, Tool)

    def test_cortex_learning_has_definition(self) -> None:
        """CortexLearning must expose a ToolDefinition via .definition property."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        defn = tool.definition

        assert defn.name == "cortex_learning"
        assert len(defn.description) > 0
        assert len(defn.parameters) > 0

    def test_cortex_learning_name_property(self) -> None:
        """CortexLearning.name must return 'cortex_learning'."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        assert tool.name == "cortex_learning"

    def test_cortex_learning_has_execute(self) -> None:
        """CortexLearning must implement execute() method."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        assert hasattr(tool, "execute")
        assert callable(tool.execute)

    def test_cortex_learning_has_op_parameter(self) -> None:
        """CortexLearning must accept 'op' parameter."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        param_names = [p.name for p in tool.definition.parameters]
        assert "op" in param_names

    def test_cortex_learning_supported_ops(self) -> None:
        """CortexLearning 'op' parameter must list all supported operations."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        op_param = next(p for p in tool.definition.parameters if p.name == "op")
        assert op_param.enum is not None
        expected_ops = {"emit", "history", "decay", "promote", "quarantine", "metrics"}
        assert set(op_param.enum) == expected_ops


# ─────────────────────────────────────────────────────────────────────────────
# 2. emit operation
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexLearningEmit:
    """GAP-83-05: emit operation writes signal to learning loop."""

    def test_emit_returns_success(self) -> None:
        """emit with valid params must return success=True."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(
            op="emit",
            signal_type="STRONG_REWARD",
            pattern_id="test-pattern-001",
            source_orchestrator="TestOrch",
        )

        assert result.success is True

    def test_emit_returns_signal_id(self) -> None:
        """emit must return signal_id in result data."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(
            op="emit",
            signal_type="MILD_PUNISHMENT",
            pattern_id="test-pattern-002",
            source_orchestrator="TestOrch",
        )

        assert result.data is not None
        assert "signal_id" in result.data

    def test_emit_with_invalid_signal_type(self) -> None:
        """emit with unknown signal_type must return success=False."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(
            op="emit",
            signal_type="INVALID_TYPE",
            pattern_id="test-pattern",
            source_orchestrator="TestOrch",
        )

        assert result.success is False


# ─────────────────────────────────────────────────────────────────────────────
# 3. history operation
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexLearningHistory:
    """GAP-83-05: history operation returns signal history."""

    def test_history_returns_list(self) -> None:
        """history must return a list of signals in result data."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(op="history")

        assert result.success is True
        assert result.data is not None
        assert "signals" in result.data
        assert isinstance(result.data["signals"], list)

    def test_history_filterable_by_pattern_id(self) -> None:
        """history with pattern_id must filter results."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()

        # Emit two signals for different patterns
        tool.execute(
            op="emit",
            signal_type="STRONG_REWARD",
            pattern_id="filter-test-a",
            source_orchestrator="TestOrch",
        )
        tool.execute(
            op="emit",
            signal_type="MILD_PUNISHMENT",
            pattern_id="filter-test-b",
            source_orchestrator="TestOrch",
        )

        result = tool.execute(op="history", pattern_id="filter-test-a")

        assert result.success is True
        for signal in result.data["signals"]:
            assert signal["pattern_id"] == "filter-test-a"


# ─────────────────────────────────────────────────────────────────────────────
# 4. decay / promote / quarantine operations
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexLearningLifecycle:
    """GAP-83-05: decay/promote/quarantine operations."""

    def test_decay_returns_success(self) -> None:
        """decay operation must return success=True."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(op="decay")

        assert result.success is True
        assert result.data is not None
        assert "decayed" in result.data

    def test_promote_returns_success(self) -> None:
        """promote operation must return success=True."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(op="promote")

        assert result.success is True
        assert result.data is not None
        assert "promoted" in result.data

    def test_quarantine_returns_success(self) -> None:
        """quarantine operation must return success=True."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(op="quarantine")

        assert result.success is True
        assert result.data is not None
        assert "quarantined" in result.data


# ─────────────────────────────────────────────────────────────────────────────
# 5. metrics operation
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexLearningMetrics:
    """GAP-83-05: metrics operation returns learning metrics."""

    def test_metrics_returns_success(self) -> None:
        """metrics operation must return success=True."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(op="metrics")

        assert result.success is True
        assert result.data is not None
        assert "total_learnings" in result.data

    def test_metrics_includes_signal_count(self) -> None:
        """metrics must include reinforcement signal statistics."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(op="metrics")

        assert "signal_count" in result.data


# ─────────────────────────────────────────────────────────────────────────────
# 6. Unknown operation returns error
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexLearningErrors:
    """GAP-83-05: Error handling for invalid operations."""

    def test_unknown_op_returns_error(self) -> None:
        """Unknown operation must return success=False."""
        from cortex.mcp.tools.learning_tool import CortexLearning

        tool = CortexLearning()
        result = tool.execute(op="nonexistent_operation")

        assert result.success is False
        assert result.error is not None


# ─────────────────────────────────────────────────────────────────────────────
# 7. Registration in ALL_TOOLS
# ─────────────────────────────────────────────────────────────────────────────


class TestCortexLearningRegistration:
    """GAP-83-05: CortexLearning registered in ALL_TOOLS."""

    def test_cortex_learning_in_all_tools(self) -> None:
        """CortexLearning must be in ALL_TOOLS list."""
        from cortex.mcp.tools import ALL_TOOLS
        from cortex.mcp.tools.learning_tool import CortexLearning

        assert CortexLearning in ALL_TOOLS

    def test_cortex_learning_in_exports(self) -> None:
        """CortexLearning must be in __all__ exports."""
        from cortex.mcp.tools import __all__ as exports

        assert "CortexLearning" in exports
