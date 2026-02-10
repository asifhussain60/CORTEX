"""
Unit tests for enhanced @mcp_tool decorator (Phase 54 S4).

Tests for:
- Intelligence context injection
- Backward compatibility (inject_intelligence=False)
- Graceful degradation on synthesis failure
- Metadata preservation

CORE Rules:
- CORE-008: TDD (tests before code) ✅
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from cortex.mcp.decorators import mcp_tool, get_registered_tools, clear_tools


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear registry before/after each test."""
    clear_tools()
    yield
    clear_tools()


class TestEnhancedMcpToolDecorator:
    """Test enhanced @mcp_tool decorator with intelligence injection."""

    def test_decorator_registers_tool(self):
        """Decorator should register tool with metadata."""
        @mcp_tool(name="test_tool", description="Test tool")
        def test_func():
            return "result"

        tools = get_registered_tools()
        assert "test_tool" in tools
        assert tools["test_tool"]["description"] == "Test tool"

    def test_decorator_preserves_function(self):
        """Decorator should preserve original function behavior."""
        @mcp_tool(name="test_tool", description="Test")
        def test_func(a, b):
            return a + b

        result = test_func(2, 3)
        assert result == 5

    def test_decorator_metadata_on_function(self):
        """Decorator should attach metadata to function."""
        @mcp_tool(name="test_tool", description="Test")
        assert hasattr(test_func, "_mcp_tool_metadata")
        assert test_func._mcp_tool_metadata["name"] == "test_tool"

    def test_decorator_invalid_name(self):
        """Decorator should reject empty names."""
        with pytest.raises(ValueError):
            @mcp_tool(name="", description="Test")
    def test_decorator_invalid_description(self):
        """Decorator should reject empty descriptions."""
        with pytest.raises(ValueError):
            @mcp_tool(name="test_tool", description="")
    def test_inject_intelligence_enabled(self):
        """Decorator should inject intelligence when enabled."""
        mock_context = Mock()
        mock_context.rules = []

        @mcp_tool(
            name="test_tool",
            description="Test",
            inject_intelligence=True
        )
        def test_func(value, unified_intelligence=None):
            return unified_intelligence is not None

        with patch("cortex.mcp.decorators.get_synthesis_engine") as mock_engine:
            with patch("cortex.mcp.decorators.IntelligenceGate") as mock_gate:
                mock_engine.return_value.synthesize_unified_context.return_value = mock_context
                mock_gate_instance = Mock()
                mock_gate.return_value = mock_gate_instance

                # Call without intelligence parameter
                result = test_func(value=1)

                # Should have attempted injection
                assert mock_engine.called

    def test_inject_intelligence_disabled(self):
        """Decorator should not inject when disabled."""
        @mcp_tool(
            name="test_tool",
            description="Test",
            inject_intelligence=False
        )
        def test_func(value, unified_intelligence=None):
            return unified_intelligence

        with patch("cortex.mcp.decorators.get_synthesis_engine") as mock_engine:
            result = test_func(value=1)

            # Should NOT have called synthesis engine
            assert not mock_engine.called
            assert result is None

    def test_inject_intelligence_already_present(self):
        """Decorator should not re-inject if already present."""
        provided_context = {"test": "context"}

        @mcp_tool(name="test_tool", description="Test", inject_intelligence=True)
        def test_func(unified_intelligence=None):
            return unified_intelligence

        with patch("cortex.mcp.decorators.get_synthesis_engine") as mock_engine:
            result = test_func(unified_intelligence=provided_context)

            # Should NOT have called synthesis engine (already provided)
            assert not mock_engine.called
            assert result == provided_context

    def test_inject_intelligence_handles_exception(self):
        """Decorator should handle synthesis failures gracefully."""
        @mcp_tool(name="test_tool", description="Test", inject_intelligence=True)
        def test_func(unified_intelligence=None):
            return unified_intelligence

        with patch("cortex.mcp.decorators.get_synthesis_engine") as mock_engine:
            mock_engine.return_value.synthesize_unified_context.side_effect = Exception("Synthesis failed")

            result = test_func()

            # Should gracefully degrade to None
            assert result is None

    def test_inject_intelligence_passes_intent(self):
        """Decorator should pass intent_type to synthesis engine."""
        mock_context = Mock()

        @mcp_tool(name="test_tool", description="Test", inject_intelligence=True)
        def test_func(intent_type="IMPLEMENT", unified_intelligence=None):
            return unified_intelligence

        with patch("cortex.mcp.decorators.get_synthesis_engine") as mock_engine:
            with patch("cortex.mcp.decorators.IntelligenceGate") as mock_gate:
                mock_engine.return_value.synthesize_unified_context.return_value = mock_context
                mock_gate.return_value = Mock()

                test_func(intent_type="FIX")

                # Should have called synthesis with FIX intent
                call_args = mock_engine.return_value.synthesize_unified_context.call_args
                assert call_args[1]["intent_type"] == "FIX"

    def test_decorator_with_parameters(self):
        """Decorator should store parameter information."""
        @mcp_tool(
            name="test_tool",
            description="Test",
            parameters={"arg1": "string", "arg2": "int"}
        )
        def test_func(arg1, arg2):
            return arg1, arg2

        tools = get_registered_tools()
        assert "arg1" in tools["test_tool"]["parameters"]
        assert "arg2" in tools["test_tool"]["parameters"]

    def test_decorator_with_category(self):
        """Decorator should store category information."""
        @mcp_tool(
            name="test_tool",
            description="Test",
            category="analysis"
        )
        tools = get_registered_tools()
        assert tools["test_tool"]["category"] == "analysis"

    def test_multiple_tools_registered(self):
        """Multiple decorated functions should all be registered."""
        @mcp_tool(name="tool1", description="Tool 1")
        def func1():
            return 1

        @mcp_tool(name="tool2", description="Tool 2")
        def func2():
            return 2

        tools = get_registered_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_decorator_returns_callable(self):
        """Decorator should return a callable."""
        @mcp_tool(name="test_tool", description="Test")
        def test_func():
            return "result"

        assert callable(test_func)
        assert test_func() == "result"

    def test_inject_intelligence_with_file_path(self):
        """Decorator should pass file_path to synthesis engine."""
        mock_context = Mock()

        @mcp_tool(name="test_tool", description="Test", inject_intelligence=True)
        def test_func(file_path="test.py", unified_intelligence=None):
            return unified_intelligence

        with patch("cortex.mcp.decorators.get_synthesis_engine") as mock_engine:
            with patch("cortex.mcp.decorators.IntelligenceGate"):
                mock_engine.return_value.synthesize_unified_context.return_value = mock_context

                test_func(file_path="/src/main.py")

                # Should have called synthesis with file_path
                call_args = mock_engine.return_value.synthesize_unified_context.call_args
                assert call_args[1]["file_path"] == "/src/main.py"

    def test_inject_intelligence_ac_marker_logged(self):
        """Decorator should log AC markers for intelligence injection."""
        @mcp_tool(name="test_tool", description="Test", inject_intelligence=True)
        def test_func(unified_intelligence=None):
            return unified_intelligence

        with patch("cortex.mcp.decorators.logger") as mock_logger:
            with patch("cortex.mcp.decorators.get_synthesis_engine") as mock_engine:
                with patch("cortex.mcp.decorators.IntelligenceGate"):
                    mock_engine.return_value.synthesize_unified_context.return_value = Mock()

                    test_func()

                    # Should have logged AC marker
                    assert mock_logger.debug.called
                    log_message = mock_logger.debug.call_args[0][0]
                    assert "AC_PHASE54-S4-001" in log_message
