"""
Phase 86 — Multi-Stack Debug Strategy Tests (RED phase — CORE-008)
Tests for the 5 new AbstractInjectionStrategy implementations:
  FrontendConsoleStrategy, HtmlVisionMappingStrategy, ApiTraceStrategy,
  SqlTraceStrategy, DotNetTraceStrategy

AC-PHASE86-001-005: Strategy tests
CORE-008: TDD mandatory
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

import pytest
from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import (
    MarkerContext,
)


def _ctx(trigger: str = "test_failure", file_path: str = "app.py") -> MarkerContext:
    """Build a minimal MarkerContext for tests."""
    return MarkerContext(
        trigger_type=trigger,
        session_id="SESSION-86-TEST",
        file_path=file_path,
        line_number=10,
        additional_context={},
    )


# ============================================================================
# FrontendConsoleStrategy — GAP-86-01
# ============================================================================
class TestFrontendConsoleStrategyImport:
    """FrontendConsoleStrategy must be importable and satisfy the ABC."""

    def test_is_importable(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        assert FrontendConsoleStrategy is not None

    def test_implements_analyze(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        assert hasattr(FrontendConsoleStrategy, "analyze")

    def test_implements_format_marker(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        assert hasattr(FrontendConsoleStrategy, "format_marker")

    def test_is_subclass_of_abstract(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import AbstractInjectionStrategy
        assert issubclass(FrontendConsoleStrategy, AbstractInjectionStrategy)


class TestFrontendConsoleStrategyBehavior:
    """FrontendConsoleStrategy behavioral tests."""

    def test_analyze_returns_list(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        s = FrontendConsoleStrategy()
        result = s.analyze(_ctx(file_path="app.tsx"))
        assert isinstance(result, list)

    def test_analyze_returns_at_least_one_line(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        s = FrontendConsoleStrategy()
        ctx = _ctx(file_path="component.tsx")
        ctx.line_number = 5
        result = s.analyze(ctx)
        assert len(result) >= 1

    def test_format_marker_returns_console_log(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        s = FrontendConsoleStrategy()
        marker = s.format_marker(_ctx(file_path="app.js"), 10)
        assert "console" in marker.lower() or "CORTEX_DEBUG" in marker

    def test_format_marker_is_string(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        s = FrontendConsoleStrategy()
        marker = s.format_marker(_ctx(file_path="app.ts"), 20)
        assert isinstance(marker, str)
        assert len(marker) > 0

    def test_supports_tsx_extension(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        s = FrontendConsoleStrategy()
        ctx = _ctx(file_path="Component.tsx")
        lines = s.analyze(ctx)
        assert isinstance(lines, list)

    def test_supports_vue_extension(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.frontend_console_strategy import FrontendConsoleStrategy
        s = FrontendConsoleStrategy()
        ctx = _ctx(file_path="Page.vue")
        lines = s.analyze(ctx)
        assert isinstance(lines, list)


# ============================================================================
# HtmlVisionMappingStrategy — GAP-86-02
# ============================================================================
class TestHtmlVisionMappingStrategyImport:
    """HtmlVisionMappingStrategy must be importable and satisfy the ABC."""

    def test_is_importable(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.html_vision_mapping_strategy import HtmlVisionMappingStrategy
        assert HtmlVisionMappingStrategy is not None

    def test_is_subclass_of_abstract(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.html_vision_mapping_strategy import HtmlVisionMappingStrategy
        from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import AbstractInjectionStrategy
        assert issubclass(HtmlVisionMappingStrategy, AbstractInjectionStrategy)


class TestHtmlVisionMappingStrategyBehavior:
    """HtmlVisionMappingStrategy behavioral tests."""

    def test_analyze_returns_list(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.html_vision_mapping_strategy import HtmlVisionMappingStrategy
        s = HtmlVisionMappingStrategy()
        result = s.analyze(_ctx(file_path="index.html"))
        assert isinstance(result, list)

    def test_format_marker_contains_data_attribute(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.html_vision_mapping_strategy import HtmlVisionMappingStrategy
        s = HtmlVisionMappingStrategy()
        marker = s.format_marker(_ctx(file_path="index.html"), 5)
        assert "data-cortex-debug" in marker or "CORTEX_DEBUG" in marker

    def test_format_marker_is_non_empty(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.html_vision_mapping_strategy import HtmlVisionMappingStrategy
        s = HtmlVisionMappingStrategy()
        marker = s.format_marker(_ctx(file_path="page.html"), 1)
        assert isinstance(marker, str)
        assert len(marker) > 0


# ============================================================================
# ApiTraceStrategy — GAP-86-03
# ============================================================================
class TestApiTraceStrategyImport:
    """ApiTraceStrategy must be importable and satisfy the ABC."""

    def test_is_importable(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.api_trace_strategy import ApiTraceStrategy
        assert ApiTraceStrategy is not None

    def test_is_subclass_of_abstract(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.api_trace_strategy import ApiTraceStrategy
        from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import AbstractInjectionStrategy
        assert issubclass(ApiTraceStrategy, AbstractInjectionStrategy)


class TestApiTraceStrategyBehavior:
    """ApiTraceStrategy behavioral tests."""

    def test_analyze_returns_list(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.api_trace_strategy import ApiTraceStrategy
        s = ApiTraceStrategy()
        result = s.analyze(_ctx(file_path="routes.py"))
        assert isinstance(result, list)

    def test_format_marker_contains_trace_keyword(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.api_trace_strategy import ApiTraceStrategy
        s = ApiTraceStrategy()
        marker = s.format_marker(_ctx(file_path="api.py"), 15)
        lower = marker.lower()
        assert "trace" in lower or "cortex_debug" in lower or "request" in lower

    def test_format_marker_is_non_empty(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.api_trace_strategy import ApiTraceStrategy
        s = ApiTraceStrategy()
        marker = s.format_marker(_ctx(file_path="views.py"), 30)
        assert isinstance(marker, str)
        assert len(marker) > 0


# ============================================================================
# SqlTraceStrategy — GAP-86-04
# ============================================================================
class TestSqlTraceStrategyImport:
    """SqlTraceStrategy must be importable and satisfy the ABC."""

    def test_is_importable(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.sql_trace_strategy import SqlTraceStrategy
        assert SqlTraceStrategy is not None

    def test_is_subclass_of_abstract(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.sql_trace_strategy import SqlTraceStrategy
        from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import AbstractInjectionStrategy
        assert issubclass(SqlTraceStrategy, AbstractInjectionStrategy)


class TestSqlTraceStrategyBehavior:
    """SqlTraceStrategy behavioral tests."""

    def test_analyze_returns_list(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.sql_trace_strategy import SqlTraceStrategy
        s = SqlTraceStrategy()
        result = s.analyze(_ctx(file_path="queries.sql"))
        assert isinstance(result, list)

    def test_format_marker_contains_sql_comment(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.sql_trace_strategy import SqlTraceStrategy
        s = SqlTraceStrategy()
        marker = s.format_marker(_ctx(file_path="schema.sql"), 1)
        # SQL marker must be a SQL comment or CORTEX_DEBUG label
        assert "--" in marker or "/*" in marker or "CORTEX_DEBUG" in marker

    def test_format_marker_non_empty(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.sql_trace_strategy import SqlTraceStrategy
        s = SqlTraceStrategy()
        marker = s.format_marker(_ctx(file_path="proc.sql"), 5)
        assert isinstance(marker, str)
        assert len(marker) > 0


# ============================================================================
# DotNetTraceStrategy — GAP-86-05
# ============================================================================
class TestDotNetTraceStrategyImport:
    """DotNetTraceStrategy must be importable and satisfy the ABC."""

    def test_is_importable(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.dotnet_trace_strategy import DotNetTraceStrategy
        assert DotNetTraceStrategy is not None

    def test_is_subclass_of_abstract(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.dotnet_trace_strategy import DotNetTraceStrategy
        from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import AbstractInjectionStrategy
        assert issubclass(DotNetTraceStrategy, AbstractInjectionStrategy)


class TestDotNetTraceStrategyBehavior:
    """DotNetTraceStrategy behavioral tests."""

    def test_analyze_returns_list(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.dotnet_trace_strategy import DotNetTraceStrategy
        s = DotNetTraceStrategy()
        result = s.analyze(_ctx(file_path="Service.cs"))
        assert isinstance(result, list)

    def test_format_marker_contains_ilogger_or_debug(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.dotnet_trace_strategy import DotNetTraceStrategy
        s = DotNetTraceStrategy()
        marker = s.format_marker(_ctx(file_path="Controller.cs"), 25)
        lower = marker.lower()
        assert "logger" in lower or "debug" in lower or "cortex_debug" in lower or "//" in marker

    def test_format_marker_non_empty(self) -> None:
        from cortex.orchestrators.support.debugging.strategies.dotnet_trace_strategy import DotNetTraceStrategy
        s = DotNetTraceStrategy()
        marker = s.format_marker(_ctx(file_path="Program.cs"), 1)
        assert isinstance(marker, str)
        assert len(marker) > 0
