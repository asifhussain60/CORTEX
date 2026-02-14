"""
P0 FIX: MCP Tool Decorator — RED Phase Tests

Tests for cortex.mcp.decorators module that provides the @mcp_tool decorator
used by MasterOrchestrator and other orchestrators for MCP tool registration.

Authority: MCP-FIRST, CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-P0-MCP-DECORATOR-001
"""

import pytest
from typing import Dict, Any, Optional


class TestMcpToolDecorator:
    """Tests for @mcp_tool decorator."""

    def test_mcp_tool_decorator_importable(self) -> None:
        """mcp_tool decorator must be importable from cortex.mcp.decorators."""
        from cortex.mcp.decorators import mcp_tool

        assert callable(mcp_tool)

    def test_mcp_tool_decorator_with_name_and_description(self) -> None:
        """Decorator must accept name and description kwargs."""
        from cortex.mcp.decorators import mcp_tool

        @mcp_tool(name="test_tool", description="A test tool")
        def sample_func(self, x: int) -> int:
            return x * 2

        assert hasattr(sample_func, "_mcp_tool_name")
        assert sample_func._mcp_tool_name == "test_tool"
        assert hasattr(sample_func, "_mcp_tool_description")
        assert sample_func._mcp_tool_description == "A test tool"

    def test_decorated_function_still_callable(self) -> None:
        """Decorated function must remain callable with original behavior."""
        from cortex.mcp.decorators import mcp_tool

        @mcp_tool(name="adder", description="Adds numbers")
        def add(a: int, b: int) -> int:
            return a + b

        result = add(3, 4)
        assert result == 7

    def test_decorator_preserves_function_name(self) -> None:
        """Decorator must preserve original function __name__."""
        from cortex.mcp.decorators import mcp_tool

        @mcp_tool(name="my_tool", description="My tool")
        def my_function() -> str:
            return "hello"

        assert my_function.__name__ == "my_function"

    def test_decorator_preserves_docstring(self) -> None:
        """Decorator must preserve original function docstring."""
        from cortex.mcp.decorators import mcp_tool

        @mcp_tool(name="doc_tool", description="Documented tool")
        def documented() -> None:
            """This is the original docstring."""
            pass

        assert documented.__doc__ == "This is the original docstring."

    def test_decorator_on_class_method(self) -> None:
        """Decorator must work on class methods (MasterOrchestrator pattern)."""
        from cortex.mcp.decorators import mcp_tool

        class SampleOrchestrator:
            @mcp_tool(
                name="register_orchestrator",
                description="Register a domain orchestrator"
            )
            def register(self, domain: str) -> Dict[str, Any]:
                """Register orchestrator."""
                return {"domain": domain, "registered": True}

        instance = SampleOrchestrator()
        result = instance.register("governance")
        assert result == {"domain": "governance", "registered": True}
        assert instance.register._mcp_tool_name == "register_orchestrator"

    def test_get_mcp_tools_from_class(self) -> None:
        """Must be able to discover all @mcp_tool decorated methods on a class."""
        from cortex.mcp.decorators import mcp_tool, get_mcp_tools

        class MyOrchestrator:
            @mcp_tool(name="tool_a", description="Tool A")
            def method_a(self) -> str:
                return "a"

            @mcp_tool(name="tool_b", description="Tool B")
            def method_b(self) -> str:
                return "b"

            def regular_method(self) -> str:
                return "not a tool"

        instance = MyOrchestrator()
        tools = get_mcp_tools(instance)

        assert len(tools) == 2
        tool_names = {t["name"] for t in tools}
        assert "tool_a" in tool_names
        assert "tool_b" in tool_names

    def test_decorator_with_optional_params(self) -> None:
        """Decorator must support optional category parameter."""
        from cortex.mcp.decorators import mcp_tool

        @mcp_tool(
            name="categorized_tool",
            description="A categorized tool",
            category="governance"
        )
        def categorized() -> None:
            pass

        assert categorized._mcp_tool_name == "categorized_tool"
        assert categorized._mcp_tool_category == "governance"


class TestMcpToolDecoratorEdgeCases:
    """Edge case tests for mcp_tool decorator."""

    def test_decorator_requires_name(self) -> None:
        """Decorator must require name parameter."""
        from cortex.mcp.decorators import mcp_tool

        with pytest.raises(TypeError):
            @mcp_tool(description="Missing name")
            def no_name() -> None:
                pass

    def test_decorator_requires_description(self) -> None:
        """Decorator must require description parameter."""
        from cortex.mcp.decorators import mcp_tool

        with pytest.raises(TypeError):
            @mcp_tool(name="no_desc")
            def no_desc() -> None:
                pass

    def test_multiple_decorators_independent(self) -> None:
        """Each decorated function must have independent metadata."""
        from cortex.mcp.decorators import mcp_tool

        @mcp_tool(name="func_1", description="First")
        def func_1() -> None:
            pass

        @mcp_tool(name="func_2", description="Second")
        def func_2() -> None:
            pass

        assert func_1._mcp_tool_name == "func_1"
        assert func_2._mcp_tool_name == "func_2"
        assert func_1._mcp_tool_description == "First"
        assert func_2._mcp_tool_description == "Second"


# AC_COMPLETE: AC-P0-MCP-DECORATOR-001
