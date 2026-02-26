"""
cortex_train MCP Tool Tests — TDD verification.

AC-TRAIN-MCP-001: cortex_train tool exposed via MCP
AC-TRAIN-MCP-002: Supports scan, propose, execute operations
AC-TRAIN-MCP-003: Returns structured results

Author: GitHub Copilot
Date: 2026-02-26
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest


class TestCortexTrainToolImport:
    """AC-TRAIN-MCP-001: cortex_train tool importable."""

    def test_cortex_train_importable(self) -> None:
        """cortex_train should be importable."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        assert cortex_train is not None
        assert callable(cortex_train)

    def test_get_tool_definition_importable(self) -> None:
        """get_tool_definition should be importable."""
        from cortex.mcp.tools.trainer_tool import get_tool_definition

        assert get_tool_definition is not None
        assert callable(get_tool_definition)


class TestCortexTrainToolDefinition:
    """Test MCP tool definition structure."""

    def test_tool_definition_has_name(self) -> None:
        """Tool definition should have name."""
        from cortex.mcp.tools.trainer_tool import get_tool_definition

        definition = get_tool_definition()
        assert "name" in definition
        assert definition["name"] == "cortex_train"

    def test_tool_definition_has_description(self) -> None:
        """Tool definition should have description."""
        from cortex.mcp.tools.trainer_tool import get_tool_definition

        definition = get_tool_definition()
        assert "description" in definition
        assert len(definition["description"]) > 50

    def test_tool_definition_has_parameters(self) -> None:
        """Tool definition should have parameters schema."""
        from cortex.mcp.tools.trainer_tool import get_tool_definition

        definition = get_tool_definition()
        assert "parameters" in definition
        assert "properties" in definition["parameters"]
        assert "op" in definition["parameters"]["properties"]


class TestCortexTrainOperations:
    """AC-TRAIN-MCP-002: Test scan, propose, execute operations."""

    def test_scan_operation_requires_target_path(self) -> None:
        """Scan operation should require target_path."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        result = cortex_train(op="scan")
        assert result["status"] == "error"
        assert "target_path" in result["error"]

    def test_scan_operation_with_path(self, tmp_path: Path) -> None:
        """Scan operation should work with valid path."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        # Create target
        target = tmp_path / "test_repo"
        target.mkdir()
        (target / "main.py").write_text("def hello(): pass")

        result = cortex_train(op="scan", target_path=str(target))
        assert result["status"] == "success"
        assert "analysis" in result
        assert "proposal" in result

    def test_propose_operation_requires_gaps(self) -> None:
        """Propose operation should require gaps."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        result = cortex_train(op="propose")
        assert result["status"] == "error"
        assert "gaps" in result["error"]

    def test_propose_operation_with_gaps(self) -> None:
        """Propose operation should work with gaps."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        gaps = {"missing": [], "enhance": [], "obsolete": []}
        result = cortex_train(op="propose", gaps=gaps)
        assert result["status"] == "success"
        assert "proposal" in result

    def test_execute_operation_requires_proposal(self) -> None:
        """Execute operation should require proposal."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        result = cortex_train(op="execute")
        assert result["status"] == "error"
        assert "proposal" in result["error"]

    def test_execute_operation_with_unapproved_proposal(self) -> None:
        """Execute operation should require approved proposal."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        proposal = {"actions": [], "approved": False}
        result = cortex_train(op="execute", proposal=proposal)
        assert result["status"] == "pending_approval"

    def test_unknown_operation_returns_error(self) -> None:
        """Unknown operation should return error."""
        from cortex.mcp.tools.trainer_tool import cortex_train

        result = cortex_train(op="unknown")
        assert result["status"] == "error"
        assert "Unknown operation" in result["error"]
        assert "supported_operations" in result
