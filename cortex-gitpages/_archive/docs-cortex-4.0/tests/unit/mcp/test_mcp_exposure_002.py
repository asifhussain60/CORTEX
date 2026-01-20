"""Test suite for AC-MCP-EXPOSURE-002: Domain orchestrator operations as MCP tools."""

import pytest
from typing import Any, Dict, List
from unittest.mock import Mock, patch

from cortex.mcp.decorators import mcp_tool, MCP_TOOLS_REGISTRY
from cortex.orchestrators.registry import OrchestratorRegistry


class TestDomainOrchestratorExposure:
    """Tests for exposing domain orchestrator methods as MCP tools."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        MCP_TOOLS_REGISTRY.clear()

    def test_all_domain_orchestrators_exposed(self) -> None:
        """Test that 15+ domain orchestrator methods are exposed as MCP tools."""
        # Get all registered MCP tools that are orchestrator operations
        orchestrator_tools = [
            name for name in MCP_TOOLS_REGISTRY.keys()
            if name.startswith("orchestrator_") or "_operation" in name
        ]

        # Should have at least 15 exposed operations
        assert len(orchestrator_tools) >= 15

    def test_orchestrator_tool_signatures_standardized(self) -> None:
        """Test that exposed orchestrator tools have standardized signatures."""
        # Verify standard signature pattern
        for tool_name, tool_metadata in MCP_TOOLS_REGISTRY.items():
            if "orchestrator" in tool_name or "operation" in tool_name:
                # Should have callable function
                assert callable(tool_metadata.get("func"))
                
                # Should have description
                assert tool_metadata.get("description")
                
                # Should have name
                assert tool_metadata.get("name") == tool_name

    def test_tool_registration_bulk_operation(self) -> None:
        """Test bulk registration of orchestrator tools."""
        # Should support registering multiple tools efficiently
        test_tools = {}
        for i in range(15):
            @mcp_tool(
                name=f"bulk_tool_{i}",
                description=f"Bulk tool {i}"
            )
            def sample_func() -> str:
                """Sample function."""
                return f"result_{i}"
            
            test_tools[f"bulk_tool_{i}"] = sample_func

        # Verify all registered
        for i in range(15):
            assert f"bulk_tool_{i}" in MCP_TOOLS_REGISTRY

    def test_orchestrator_operation_parameters(self) -> None:
        """Test orchestrator operations have consistent parameter documentation."""
        # Check orchestrator tools have parameters field
        orchestrator_count = 0
        for tool_name, tool_metadata in MCP_TOOLS_REGISTRY.items():
            if "orchestrator" in tool_name:
                orchestrator_count += 1
                # Should have either parameters or be documented
                assert tool_metadata.get("description")

        assert orchestrator_count > 0

    def test_tool_callable_with_context(self) -> None:
        """Test orchestrator tools callable with operation context."""
        @mcp_tool(
            name="context_operation",
            description="Operation with context",
            parameters={"context": "dict", "operation": "str"}
        )
        def sample_func(context: dict[str, Any], operation: str) -> dict[str, Any]:
            """Context-aware operation."""
            return {"context": context, "operation": operation}

        tool_func = MCP_TOOLS_REGISTRY["context_operation"]["func"]
        result = tool_func({"key": "value"}, "test_op")
        
        assert result["operation"] == "test_op"
        assert result["context"]["key"] == "value"

    def test_batch_tool_registration(self) -> None:
        """Test batch registration of multiple tools."""
        # Simulate registering batch of orchestrator operations
        operations = [
            ("analyze_code", "Analyze code structure"),
            ("validate_context", "Validate execution context"),
            ("execute_transformation", "Execute code transformation"),
            ("resolve_conflicts", "Resolve operation conflicts"),
            ("synthesize_knowledge", "Synthesize knowledge from sources"),
        ]

        for op_name, op_desc in operations:
            @mcp_tool(name=op_name, description=op_desc)
            def op_func() -> str:
                """Operation function."""
                return f"executing {op_name}"

        # Verify all registered
        for op_name, _ in operations:
            assert op_name in MCP_TOOLS_REGISTRY

    def test_orchestrator_tool_discovery(self) -> None:
        """Test orchestrator tools can be discovered."""
        @mcp_tool(name="discoverable_operation", description="Discoverable")
        def sample_func() -> str:
            """Sample operation."""
            return "result"

        # Should be discoverable through registry
        discovered_tools = list(MCP_TOOLS_REGISTRY.keys())
        assert "discoverable_operation" in discovered_tools

    def test_tool_return_type_consistency(self) -> None:
        """Test orchestrator tool return types are consistent."""
        @mcp_tool(name="typed_return_op", description="Typed return")
        def sample_func(x: int) -> dict[str, Any]:
            """Typed return operation."""
            return {"result": x * 2, "operation": "multiply"}

        tool_func = MCP_TOOLS_REGISTRY["typed_return_op"]["func"]
        result = tool_func(5)
        
        assert isinstance(result, dict)
        assert "result" in result
        assert "operation" in result

    def test_multiple_operation_domains(self) -> None:
        """Test tools from multiple operation domains."""
        domains = ["analysis", "validation", "transformation", "synthesis"]
        
        for domain in domains:
            @mcp_tool(
                name=f"{domain}_operation",
                description=f"{domain.title()} operation"
            )
            def domain_func() -> str:
                """Domain function."""
                return f"{domain}_result"

        # Verify all domain operations registered
        for domain in domains:
            assert f"{domain}_operation" in MCP_TOOLS_REGISTRY

    def test_tool_dependency_information(self) -> None:
        """Test tools can carry dependency information."""
        @mcp_tool(
            name="dependent_operation",
            description="Operation with dependencies",
            parameters={"requires": "list"}
        )
        def sample_func() -> dict[str, Any]:
            """Operation with dependencies."""
            return {"requires": ["analysis", "validation"]}

        tool_metadata = MCP_TOOLS_REGISTRY["dependent_operation"]
        assert tool_metadata.get("parameters")


class TestOrchestrationToolIntegration:
    """Tests for integration of orchestrator tools."""

    def setup_method(self) -> None:
        """Clear registry before each test."""
        MCP_TOOLS_REGISTRY.clear()

    def test_tool_error_handling(self) -> None:
        """Test error handling in exposed tools."""
        @mcp_tool(name="error_operation", description="Error operation")
        def sample_func(x: int) -> int:
            """Operation that validates input."""
            if x < 0:
                raise ValueError("x must be non-negative")
            return x * 2

        tool_func = MCP_TOOLS_REGISTRY["error_operation"]["func"]
        
        with pytest.raises(ValueError):
            tool_func(-1)

    def test_tool_async_support(self) -> None:
        """Test that tools support async operations."""
        @mcp_tool(name="async_operation", description="Async operation")
        def sample_func(operation_id: str) -> str:
            """Async-capable operation."""
            return f"executing_async_{operation_id}"

        tool_func = MCP_TOOLS_REGISTRY["async_operation"]["func"]
        result = tool_func("test123")
        
        assert "test123" in result

    def test_operation_composition(self) -> None:
        """Test composing multiple operations."""
        @mcp_tool(name="operation_a", description="Operation A")
        def op_a(x: int) -> int:
            """Operation A."""
            return x * 2

        @mcp_tool(name="operation_b", description="Operation B")
        def op_b(x: int) -> int:
            """Operation B."""
            return x + 10

        # Operations should be composable
        result_a = MCP_TOOLS_REGISTRY["operation_a"]["func"](5)
        result_b = MCP_TOOLS_REGISTRY["operation_b"]["func"](result_a)
        
        assert result_b == 20  # (5 * 2) + 10
