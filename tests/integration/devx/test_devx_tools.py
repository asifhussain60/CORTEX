"""Tests for Developer Experience Tools."""

import pytest
from typing import Dict, Any
from cortex.devx.devx_formatter import DevxFormatter
from cortex.devx.devx_debugger import DevxDebugger, DebugContext
from cortex.devx.devx_profiler import DevxProfiler, ProfileResult
from cortex.devx.ide_integration import IDEIntegration


class TestDevxFormatter:
    """Tests for code formatting."""

    def test_formatter_init(self) -> None:
        """Test formatter initialization."""
        formatter = DevxFormatter()
        assert formatter is not None

    def test_formatter_formats_code(self) -> None:
        """Test formatter formats Python code."""
        formatter = DevxFormatter()
        code = "x=1+2"
        formatted = formatter.format_code(code)
        assert isinstance(formatted, str)

    def test_formatter_formats_output(self) -> None:
        """Test formatter formats output."""
        formatter = DevxFormatter()
        output = formatter.format_output({"key": "value"})
        assert isinstance(output, str)

    def test_formatter_formats_logs(self) -> None:
        """Test formatter formats log output."""
        formatter = DevxFormatter()
        logs = ["log1", "log2"]
        formatted = formatter.format_logs(logs)
        assert isinstance(formatted, str)

    def test_formatter_consistency(self) -> None:
        """Test formatter produces consistent output."""
        formatter = DevxFormatter()
        code1 = formatter.format_code("x = 1")
        code2 = formatter.format_code("x = 1")
        assert code1 == code2


class TestDevxDebugger:
    """Tests for debugging tools."""

    def test_debugger_init(self) -> None:
        """Test debugger initialization."""
        debugger = DevxDebugger()
        assert debugger is not None

    def test_debugger_create_context(self) -> None:
        """Test debugger creates debug context."""
        debugger = DevxDebugger()
        context = debugger.create_context("test_operation")
        assert isinstance(context, DebugContext)

    def test_debugger_inspect_variable(self) -> None:
        """Test debugger inspects variables."""
        debugger = DevxDebugger()
        context = debugger.create_context("test")
        
        inspection = debugger.inspect_variable(context, "test_var", 42)
        assert "value" in inspection or "type" in inspection

    def test_debugger_stack_trace(self) -> None:
        """Test debugger captures stack traces."""
        debugger = DevxDebugger()
        context = debugger.create_context("test")
        
        try:
            raise ValueError("Test error")
        except ValueError:
            trace = debugger.get_stack_trace(context)
            assert isinstance(trace, str)
            assert "ValueError" in trace

    def test_debugger_breakpoint(self) -> None:
        """Test debugger handles breakpoints."""
        debugger = DevxDebugger()
        context = debugger.create_context("test")
        
        debugger.set_breakpoint(context, "line_10")
        assert len(context.breakpoints) > 0

    def test_debugger_variable_inspection(self) -> None:
        """Test debugger variable inspection."""
        debugger = DevxDebugger()
        context = debugger.create_context("test")
        
        result = debugger.inspect_variable(context, "x", {"nested": "value"})
        assert result is not None


class TestDevxProfiler:
    """Tests for performance profiling."""

    def test_profiler_init(self) -> None:
        """Test profiler initialization."""
        profiler = DevxProfiler()
        assert profiler is not None

    def test_profiler_measures_execution_time(self) -> None:
        """Test profiler measures execution time."""
        profiler = DevxProfiler()
        
        with profiler.measure("test_operation"):
            x = 1 + 1
        
        result = profiler.get_results()
        assert "test_operation" in result or len(result) > 0

    def test_profiler_memory_tracking(self) -> None:
        """Test profiler tracks memory usage."""
        profiler = DevxProfiler()
        
        with profiler.measure("memory_test"):
            data = [i for i in range(1000)]
        
        result = profiler.get_profile_result("memory_test")
        assert isinstance(result, ProfileResult)

    def test_profiler_results_format(self) -> None:
        """Test profiler results are properly formatted."""
        profiler = DevxProfiler()
        
        with profiler.measure("test"):
            x = 1 + 1
        
        results = profiler.get_results()
        assert isinstance(results, dict)

class TestIDEIntegration:
    """Tests for IDE integration."""

    def test_ide_init(self) -> None:
        """Test IDE integration initialization."""
        ide = IDEIntegration()
        assert ide is not None

    def test_ide_syntax_highlighting_config(self) -> None:
        """Test IDE syntax highlighting configuration."""
        ide = IDEIntegration()
        config = ide.get_syntax_highlighting_config()
        assert config is not None

    def test_ide_goto_definition(self) -> None:
        """Test IDE go-to-definition feature."""
        ide = IDEIntegration()
        location = ide.goto_definition("test_symbol", 10)
        assert isinstance(location, dict)

    def test_ide_autocomplete_suggestions(self) -> None:
        """Test IDE autocomplete suggestions."""
        ide = IDEIntegration()
        suggestions = ide.get_autocomplete_suggestions("test_", 0)
        assert isinstance(suggestions, list)

    def test_ide_hover_information(self) -> None:
        """Test IDE hover information."""
        ide = IDEIntegration()
        info = ide.get_hover_info("test_symbol")
        assert isinstance(info, str)


class TestDevxIntegration:
    """Integration tests for DevX tools."""

    def test_formatter_debugger_integration(self) -> None:
        """Test formatter and debugger work together."""
        formatter = DevxFormatter()
        debugger = DevxDebugger()
        
        context = debugger.create_context("test")
        output = formatter.format_output({"debug": context})
        
        assert output is not None

    def test_debugger_profiler_integration(self) -> None:
        """Test debugger and profiler work together."""
        debugger = DevxDebugger()
        profiler = DevxProfiler()
        
        context = debugger.create_context("profiled")
        with profiler.measure("operation"):
            debugger.inspect_variable(context, "x", 10)
        
        results = profiler.get_results()
        assert len(results) > 0

    def test_all_tools_together(self) -> None:
        """Test all DevX tools together."""
        formatter = DevxFormatter()
        debugger = DevxDebugger()
        profiler = DevxProfiler()
        ide = IDEIntegration()
        
        # Simulate a development workflow
        context = debugger.create_context("workflow")
        
        with profiler.measure("execution"):
            debugger.inspect_variable(context, "data", [1, 2, 3])
        
        output = formatter.format_output({"result": "success"})
        suggestions = ide.get_autocomplete_suggestions("test", 0)
        
        assert output is not None
        assert suggestions is not None

    def test_devx_cli_integration(self) -> None:
        """Test DevX tools integrate with CLI."""
        formatter = DevxFormatter()
        profiler = DevxProfiler()
        
        # Simulate CLI command execution
        with profiler.measure("cli_command"):
            output = formatter.format_output({"status": "ok"})
        
        report = profiler.generate_report()
        assert "cli_command" in report or len(report) > 0
