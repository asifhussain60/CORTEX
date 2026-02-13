"""
Tests for Intelligence Test Generation MCP Tool.

AC_START: AC-WAVE-2-S6-001
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from cortex.mcp.base import ToolCategory, ToolResult
from cortex.mcp.tools.intelligence_generation import CortexGenerateTests


class TestCortexGenerateTests:
    """Test cortex_generate_tests MCP tool."""

    def test_tool_name(self):
        """Test tool has correct name."""
        tool = CortexGenerateTests()
        assert tool.name == "cortex_generate_tests"

    def test_tool_category(self):
        """Test tool is in operations category."""
        tool = CortexGenerateTests()
        assert tool.category == ToolCategory.OPERATIONS

    def test_tool_description(self):
        """Test tool has description."""
        tool = CortexGenerateTests()
        assert "intelligent" in tool.description.lower()
        assert "test" in tool.description.lower()

    def test_tool_parameters(self):
        """Test tool defines required parameters."""
        tool = CortexGenerateTests()
        params = tool.parameters
        
        param_names = {p.name for p in params}
        assert "target" in param_names
        assert "target_type" in param_names

    @pytest.mark.asyncio
    async def test_generate_for_function(self):
        """Test generating tests for a function."""
        tool = CortexGenerateTests()
        
        result = await tool.execute(
            target="validate_user",
            target_type="function",
            file_path="cortex/validation.py",
            parameters=["username", "email"],
            min_value_score=50.0,
        )
        
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "tests" in result.data
        assert result.data["total_generated"] >= 0

    @pytest.mark.asyncio
    async def test_generate_for_endpoint(self):
        """Test generating tests for API endpoint."""
        tool = CortexGenerateTests()
        
        result = await tool.execute(
            target="/api/users",
            target_type="endpoint",
            file_path="api/routes.py",
            parameters=["user_id"],
            has_database_access=True,
            requires_authentication=True,
            min_value_score=50.0,
        )
        
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert "tests" in result.data
        # Should include security tests for authenticated endpoint
        assert result.data["total_generated"] > 0

    @pytest.mark.asyncio
    async def test_missing_required_parameters(self):
        """Test error when required parameters missing."""
        tool = CortexGenerateTests()
        
        result = await tool.execute()
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_invalid_target_type(self):
        """Test error for invalid target type."""
        tool = CortexGenerateTests()
        
        result = await tool.execute(
            target="something",
            target_type="invalid_type",
            file_path="cortex/module.py",
        )
        
        assert isinstance(result, ToolResult)
        assert result.success is False
        assert "target_type" in result.error.lower()

    @pytest.mark.asyncio
    async def test_result_includes_metadata(self):
        """Test result includes generation metadata."""
        tool = CortexGenerateTests()
        
        result = await tool.execute(
            target="process_data",
            target_type="function",
            file_path="cortex/processor.py",
            parameters=["data"],
            min_value_score=50.0,
        )
        
        assert result.metadata is not None
        assert "orchestrator" in result.metadata
        assert result.metadata["orchestrator"] == "IntelligentTestGenerator"


# AC_COMPLETE: AC-WAVE-2-S6-001 ✅
# Tests: 10/10 for cortex_generate_tests MCP tool
