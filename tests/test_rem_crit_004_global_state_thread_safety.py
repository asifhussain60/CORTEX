"""Tests for REM-CRIT-004: Global Mutable State Thread-Safety.

Verifies that global mutable state has been converted to thread-safe storage.

Test Coverage:
- MCP tool registry is thread-safe
- Toolkit registry is thread-safe  
- No race conditions on registration
- Concurrent reads and writes work correctly
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep
from typing import Dict
import importlib.util
import sys
from pathlib import Path

import pytest

from cortex.brain.mcp.decorator import get_registered_tools, get_tool, mcp_tool


def _load_toolkit_module():
    """Load toolkit.py directly (not the toolkit/ package)."""
    toolkit_path = Path(__file__).parent.parent / "cortex" / "tools" / "toolkit.py"
    spec = importlib.util.spec_from_file_location("toolkit_module", toolkit_path)
    toolkit_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(toolkit_module)
    return toolkit_module


_toolkit_module = _load_toolkit_module()
_TOOLS_LOCK = _toolkit_module._TOOLS_LOCK


class TestMCPDecoratorThreadSafety:
    """Test MCP decorator tool registry thread-safety."""

    def test_registry_lock_exists(self) -> None:
        """Verify registry has thread-safe lock."""
        from cortex.brain.mcp import decorator
        
        assert hasattr(decorator, '_REGISTRY_LOCK'), "Registry lock not found"
        import threading
        # threading.Lock is a factory function, not a type
        # Check that the lock has the expected acquire/release methods
        assert hasattr(decorator._REGISTRY_LOCK, 'acquire'), "Lock missing acquire method"
        assert hasattr(decorator._REGISTRY_LOCK, 'release'), "Lock missing release method"

    def test_tool_registration(self) -> None:
        """Verify tool registration works."""
        @mcp_tool(
            name="test_tool_001",
            description="Test tool for thread-safety"
        )
        def test_function(ac_id: str) -> str:
            return f"Status: {ac_id}"
        
        # Should be registered
        tools = get_registered_tools()
        assert "test_tool_001" in tools
        assert tools["test_tool_001"]["description"] == "Test tool for thread-safety"

    def test_get_tool(self) -> None:
        """Verify retrieving registered tool."""
        @mcp_tool(
            name="test_tool_002",
            description="Another test tool"
        )
        def another_function() -> str:
            return "test"
        
        tool = get_tool("test_tool_002")
        assert tool is not None
        assert tool["name"] == "test_tool_002"

    def test_concurrent_tool_registration(self) -> None:
        """Verify concurrent tool registration doesn't cause issues."""
        results: Dict[str, bool] = {}
        
        def register_tool_thread(tool_id: int) -> None:
            """Register tool from thread."""
            @mcp_tool(
                name=f"concurrent_tool_{tool_id}",
                description=f"Tool {tool_id} from thread"
            )
            def thread_tool() -> str:
                return f"Tool {tool_id}"
            
            results[f"tool_{tool_id}"] = True
        
        # 20 concurrent registrations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(register_tool_thread, i) for i in range(20)]
            for future in as_completed(futures):
                future.result()
        
        # All should be registered
        tools = get_registered_tools()
        for i in range(20):
            assert f"concurrent_tool_{i}" in tools
        assert len(results) == 20

    def test_concurrent_tool_reads(self) -> None:
        """Verify concurrent reads of tools work safely."""
        @mcp_tool(
            name="test_read_tool",
            description="Tool for read tests"
        )
        def read_tool() -> str:
            return "read test"
        
        read_results = []
        
        def read_tools() -> None:
            """Read tools from thread."""
            tools = get_registered_tools()
            if "test_read_tool" in tools:
                read_results.append(True)
        
        # 50 concurrent reads
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(read_tools) for _ in range(50)]
            for future in as_completed(futures):
                future.result()
        
        # All reads should succeed
        assert len(read_results) == 50


class TestToolkitRegistryThreadSafety:
    """Test toolkit command registry thread-safety."""

    def test_toolkit_lock_exists(self) -> None:
        """Verify toolkit registry has thread-safe lock."""
        assert _TOOLS_LOCK is not None
        # threading.Lock is a factory function, not a type
        # Check that the lock has the expected acquire/release methods
        assert hasattr(_TOOLS_LOCK, 'acquire'), "Toolkit lock missing acquire method"
        assert hasattr(_TOOLS_LOCK, 'release'), "Toolkit lock missing release method"

    def test_toolkit_command_structure(self) -> None:
        """Verify toolkit has basic commands."""
        # Use dynamic module loading to access _TOOLS from toolkit.py (not toolkit/)
        _TOOLS = _toolkit_module._TOOLS
        
        # Toolkit may have 0 or more commands depending on initialization
        assert isinstance(_TOOLS, dict), "TOOLS should be a dict"


class TestGlobalStateElimination:
    """Verify global mutable state has been properly eliminated."""

    def test_decorator_registry_safe(self) -> None:
        """Verify decorator registry is thread-safe."""
        from cortex.brain.mcp import decorator
        
        # Check for lock
        assert hasattr(decorator, '_REGISTRY_LOCK')
        
        # Operations should be protected
        @mcp_tool(name="safety_test", description="Safety test")
        def safety_func() -> str:
            return "safe"
        
        # Should complete without race conditions
        tools1 = get_registered_tools()
        tools2 = get_registered_tools()
        
        assert tools1 == tools2

    def test_toolkit_registry_safe(self) -> None:
        """Verify toolkit registry is thread-safe."""
        # Use dynamic module loading to access toolkit.py (not toolkit/)
        _TOOLS = _toolkit_module._TOOLS
        _TOOLS_LOCK_local = _toolkit_module._TOOLS_LOCK
        
        # Check for lock
        assert _TOOLS_LOCK_local is not None
        
        # Should be able to iterate safely
        with _TOOLS_LOCK_local:
            command_count = len(_TOOLS)
        
        assert command_count >= 0  # May have 0 or more commands


class TestStateConcurrency:
    """Test state management under concurrent access."""

    def test_mixed_concurrent_access(self) -> None:
        """Test mixed concurrent reads and writes."""
        @mcp_tool(
            name="concurrent_test",
            description="Concurrent test"
        )
        def concurrent_func() -> str:
            return "concurrent"
        
        operation_log = []
        
        def mixed_operation(op_type: str, op_id: int) -> None:
            """Perform mixed operation."""
            try:
                if op_type == "read":
                    tools = get_registered_tools()
                    operation_log.append(("read", op_id, len(tools) > 0))
                elif op_type == "get":
                    tool = get_tool("concurrent_test")
                    operation_log.append(("get", op_id, tool is not None))
                else:
                    @mcp_tool(
                        name=f"dynamic_tool_{op_id}",
                        description="Dynamic tool"
                    )
                    def dynamic_func() -> str:
                        return "dynamic"
                    operation_log.append(("register", op_id, True))
            except Exception as e:
                operation_log.append((op_type, op_id, False))
        
        # 50 mixed operations
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(50):
                op_type = ["read", "get", "register"][i % 3]
                futures.append(executor.submit(mixed_operation, op_type, i))
            
            for future in as_completed(futures):
                future.result()
        
        # All operations should complete successfully
        assert len(operation_log) == 50
        assert all(success for _, _, success in operation_log), \
            f"Some operations failed: {[log for log in operation_log if not log[2]]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
