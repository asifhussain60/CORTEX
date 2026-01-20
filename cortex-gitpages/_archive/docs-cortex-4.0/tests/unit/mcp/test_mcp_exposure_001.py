"""Test suite for AC-MCP-EXPOSURE-001: @mcp_tool decorator for knowledge operations."""

import pytest
from typing import Any, Callable
from unittest.mock import Mock, patch, MagicMock

from cortex.mcp.decorators import mcp_tool, MCP_TOOLS_REGISTRY
from cortex.orchestrators.domain_brain import get_relevant_business_knowledge_for_operation


class TestMcpToolDecorator:
    """Tests for @mcp_tool decorator implementation."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        MCP_TOOLS_REGISTRY.clear()

    def test_decorator_registers_function(self) -> None:
        """Test that @mcp_tool decorator registers function in registry."""
        @mcp_tool(name="test_func", description="Test function")
        def sample_func() -> str:
            """Sample function for testing."""
            return "result"

        assert "test_func" in MCP_TOOLS_REGISTRY
        assert MCP_TOOLS_REGISTRY["test_func"]["func"] == sample_func

    def test_decorator_preserves_function_metadata(self) -> None:
        """Test that decorator preserves original function metadata."""
        @mcp_tool(name="test_meta", description="Test metadata")
        def sample_func() -> str:
            """Original docstring."""
            return "result"

        assert sample_func.__doc__ == "Original docstring."
        assert sample_func.__name__ == "sample_func"

    def test_decorator_stores_metadata(self) -> None:
        """Test that decorator stores tool metadata correctly."""
        @mcp_tool(
            name="test_meta_storage",
            description="Test metadata storage",
            parameters={"arg1": "string", "arg2": "int"}
        )
        def sample_func() -> str:
            """Sample function."""
            return "result"

        tool_metadata = MCP_TOOLS_REGISTRY["test_meta_storage"]
        assert tool_metadata["name"] == "test_meta_storage"
        assert tool_metadata["description"] == "Test metadata storage"
        assert tool_metadata["parameters"] == {"arg1": "string", "arg2": "int"}

    def test_decorator_with_type_hints(self) -> None:
        """Test decorator with typed parameters."""
        @mcp_tool(name="typed_func", description="Typed function")
        def sample_func(operation_id: str, context: dict[str, Any]) -> dict[str, Any]:
            """Typed function example."""
            return {"operation_id": operation_id, "context": context}

        tool_entry = MCP_TOOLS_REGISTRY["typed_func"]
        assert callable(tool_entry["func"])
        assert tool_entry["func"]("op123", {}) == {"operation_id": "op123", "context": {}}

    def test_knowledge_operation_decorated(self) -> None:
        """Test that get_relevant_business_knowledge_for_operation is decorated."""
        # Should be decorated and registered
        assert "get_relevant_business_knowledge_for_operation" in MCP_TOOLS_REGISTRY

    def test_decorated_function_callable(self) -> None:
        """Test that decorated functions remain callable."""
        @mcp_tool(name="callable_test", description="Callable test")
        def sample_func(x: int) -> int:
            """Simple function."""
            return x * 2

        result = sample_func(5)
        assert result == 10

    def test_multiple_functions_registered(self) -> None:
        """Test multiple functions can be decorated and registered."""
        @mcp_tool(name="func1", description="First function")
        def func_one() -> str:
            """First function."""
            return "one"

        @mcp_tool(name="func2", description="Second function")
        def func_two() -> str:
            """Second function."""
            return "two"

        assert len(MCP_TOOLS_REGISTRY) == 2
        assert "func1" in MCP_TOOLS_REGISTRY
        assert "func2" in MCP_TOOLS_REGISTRY

    def test_decorator_with_return_type(self) -> None:
        """Test decorator preserves return type hints."""
        @mcp_tool(name="return_typed", description="Return typed")
        def sample_func() -> dict[str, str]:
            """Return typed function."""
            return {"key": "value"}

        result = sample_func()
        assert isinstance(result, dict)
        assert result == {"key": "value"}

    def test_tool_discovery_metadata(self) -> None:
        """Test tool metadata accessible for discovery."""
        @mcp_tool(
            name="discoverable_tool",
            description="A discoverable tool",
            parameters={"param1": "type1"}
        )
        def sample_func() -> None:
            """Sample function."""
            pass

        tool_metadata = MCP_TOOLS_REGISTRY["discoverable_tool"]
        assert "name" in tool_metadata
        assert "description" in tool_metadata
        assert "func" in tool_metadata
        assert "parameters" in tool_metadata


class TestMcpToolExposure:
    """Tests for knowledge operation exposure through MCP."""

    def test_knowledge_operation_exposed(self) -> None:
        """Test that knowledge operations are exposed through MCP."""
        # Verify decorator is applied
        assert "get_relevant_business_knowledge_for_operation" in MCP_TOOLS_REGISTRY

    def test_tool_metadata_accessible(self) -> None:
        """Test tool metadata is accessible."""
        tool_name = "get_relevant_business_knowledge_for_operation"
        assert tool_name in MCP_TOOLS_REGISTRY
        
        metadata = MCP_TOOLS_REGISTRY[tool_name]
        assert "name" in metadata
        assert "description" in metadata
        assert "func" in metadata

    def test_tool_callable_through_registry(self) -> None:
        """Test tool is callable through MCP registry."""
        tool_name = "get_relevant_business_knowledge_for_operation"
        tool_metadata = MCP_TOOLS_REGISTRY[tool_name]
        
        # Should be callable
        assert callable(tool_metadata["func"])

    def test_knowledge_discovery_integration(self) -> None:
        """Test knowledge operation integrates with tool discovery."""
        tool_name = "get_relevant_business_knowledge_for_operation"
        assert tool_name in MCP_TOOLS_REGISTRY
        
        # Metadata should be complete
        metadata = MCP_TOOLS_REGISTRY[tool_name]
        assert metadata.get("description")  # Should have description


class TestMcpDecoratorEdgeCases:
    """Tests for edge cases in @mcp_tool decorator."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        MCP_TOOLS_REGISTRY.clear()

    def test_decorator_with_no_parameters(self) -> None:
        """Test decorator with no parameters specified."""
        @mcp_tool(name="no_params", description="No params")
        def sample_func() -> str:
            """No params function."""
            return "result"

        assert "no_params" in MCP_TOOLS_REGISTRY

    def test_decorator_with_empty_description(self) -> None:
        """Test decorator with empty description."""
        @mcp_tool(name="empty_desc", description="")
        def sample_func() -> str:
            """Function with empty description."""
            return "result"

        assert "empty_desc" in MCP_TOOLS_REGISTRY

    def test_decorator_exception_handling(self) -> None:
        """Test decorated function exception handling."""
        @mcp_tool(name="exception_func", description="Exception function")
        def sample_func(x: int) -> int:
            """Function that may raise."""
            if x < 0:
                raise ValueError("x must be positive")
            return x * 2

        with pytest.raises(ValueError):
            sample_func(-1)

    def test_registry_persistence(self) -> None:
        """Test registry persists across multiple decorations."""
        @mcp_tool(name="persist1", description="Persist 1")
        def func1() -> str:
            """Func 1."""
            return "1"

        count_after_first = len(MCP_TOOLS_REGISTRY)

        @mcp_tool(name="persist2", description="Persist 2")
        def func2() -> str:
            """Func 2."""
            return "2"

        assert len(MCP_TOOLS_REGISTRY) == count_after_first + 1
