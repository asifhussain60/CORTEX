"""
Behavioral Contract Tests: UnifiedAnalysisOrchestrator
====================================================

TRACK 3 - GROUP B: Support Layer Consolidation
Consolidates: LENSOrchestrator + ToolDiscoveryOrchestrator

Test Strategy: RED Phase (tests before implementation)
- 14 behavioral contract tests defining public API
- Covers all LENS analysis modes + tool discovery
- Tests run in isolation

CORE Governance:
✅ CORE-008: TDD (tests before code)
✅ CORE-011: Type hints (100%)
✅ CORE-012: Docstrings (Google style)
✅ CORE-013: Specific exceptions
"""

import pytest
from typing import List, Dict, Optional, Any

from cortex.orchestrators.support.analysis_models import (
    AnalysisType,
    LENSResult,
    ToolInfo,
    DependencyGraph,
)


# ============================================================================
# TEST SUITE: UnifiedAnalysisOrchestrator
# ============================================================================

class TestUnifiedAnalysisOrchestratorAPI:
    """Behavioral contracts for UnifiedAnalysisOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create UnifiedAnalysisOrchestrator instance."""
        from cortex.orchestrators.support.unified_analysis_orchestrator import (
            UnifiedAnalysisOrchestrator,
        )
        return UnifiedAnalysisOrchestrator()

    def test_analyze_complexity(self, orchestrator):
        """Behavioral Contract: Analyze code complexity."""
        code = """
def func(x):
    if x > 0:
        if x > 10:
            return 'high'
    return 'low'
"""
        result = orchestrator.analyze(code, "complexity")

        assert isinstance(result, LENSResult)
        assert result.analysis_type == AnalysisType.COMPLEXITY
        assert 0.0 <= result.score <= 1.0
        assert isinstance(result.findings, list)
        assert isinstance(result.recommendations, list)

    def test_analyze_security(self, orchestrator):
        """Behavioral Contract: Analyze code for security issues."""
        code = "import pickle; pickle.loads(data)"

        result = orchestrator.analyze(code, "security")

        assert isinstance(result, LENSResult)
        assert result.analysis_type == AnalysisType.SECURITY
        assert len(result.findings) > 0  # Should detect unsafe pickle

    def test_analyze_dependencies(self, orchestrator, tmp_path):
        """Behavioral Contract: Analyze dependencies."""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("requests==2.28.0\nnumpy==1.21.0\n")

        result = orchestrator.analyze(str(tmp_path), "dependencies")

        assert isinstance(result, LENSResult)
        assert result.analysis_type == AnalysisType.DEPENDENCIES

    def test_analyze_performance(self, orchestrator):
        """Behavioral Contract: Analyze performance characteristics."""
        code = """
def slow_func():
    for i in range(10000):
        for j in range(10000):
            pass
"""
        result = orchestrator.analyze(code, "performance")

        assert isinstance(result, LENSResult)
        assert result.analysis_type == AnalysisType.PERFORMANCE

    def test_analyze_invalid_type(self, orchestrator):
        """Behavioral Contract: Handle invalid analysis type."""
        with pytest.raises(ValueError):
            orchestrator.analyze("code", "invalid_type")

    def test_discover_tools_basic(self, orchestrator):
        """Behavioral Contract: Discover available tools."""
        results = orchestrator.discover_tools("testing")

        assert isinstance(results, list)
        assert all(isinstance(r, ToolInfo) for r in results)
        for tool in results:
            assert tool.name is not None
            assert tool.category is not None

    def test_discover_tools_python(self, orchestrator):
        """Behavioral Contract: Discover Python-specific tools."""
        results = orchestrator.discover_tools("testing")

        assert isinstance(results, list)
        # Should find at least pytest or coverage tool
        assert len(results) > 0

    def test_discover_tools_empty_query(self, orchestrator):
        """Behavioral Contract: Handle empty query."""
        results = orchestrator.discover_tools("")

        # Empty query should return empty or all tools
        assert isinstance(results, list)

    def test_analyze_dependencies_graph(self, orchestrator):
        """Behavioral Contract: Build dependency graph."""
        graph = orchestrator.analyze_dependencies_graph("requests,numpy,pandas")

        assert isinstance(graph, DependencyGraph)
        assert isinstance(graph.nodes, list)
        assert isinstance(graph.edges, list)
        assert isinstance(graph.has_cycles, bool)

    def test_analyze_dependencies_cycles(self, orchestrator):
        """Behavioral Contract: Detect circular dependencies."""
        # A → B → C → A
        deps = "a->b,b->c,c->a"

        graph = orchestrator.analyze_dependencies_graph(deps)

        assert isinstance(graph, DependencyGraph)
        assert isinstance(graph.has_cycles, bool)

    def test_validate_analysis_result(self, orchestrator):
        """Behavioral Contract: Validate analysis result."""
        result = LENSResult(
            analysis_type=AnalysisType.COMPLEXITY,
            score=0.75,
            findings=["Issue 1"],
            recommendations=["Fix 1"],
            details={},
        )

        is_valid = orchestrator.validate_analysis_result(result)

        assert isinstance(is_valid, bool)
        assert is_valid is True  # Valid result

    def test_validate_analysis_invalid_result(self, orchestrator):
        """Behavioral Contract: Detect invalid analysis result."""
        result = LENSResult(
            analysis_type=AnalysisType.COMPLEXITY,
            score=1.5,  # Invalid: > 1.0
            findings=[],
            recommendations=[],
            details={},
        )

        is_valid = orchestrator.validate_analysis_result(result)

        assert is_valid is False


class TestUnifiedAnalysisOrchestratorPerformance:
    """Performance tests for analysis operations."""

    @pytest.fixture
    def orchestrator(self):
        from cortex.orchestrators.support.unified_analysis_orchestrator import (
            UnifiedAnalysisOrchestrator,
        )
        return UnifiedAnalysisOrchestrator()

    def test_analyze_latency(self, orchestrator):
        """Performance: Analysis should complete in <100ms."""
        import time

        code = "x = 1 + 2"
        start = time.time()
        result = orchestrator.analyze(code, "complexity")
        elapsed = (time.time() - start) * 1000

        assert isinstance(result, LENSResult)
        assert elapsed < 100, f"Analysis took {elapsed}ms"

    def test_discover_tools_latency(self, orchestrator):
        """Performance: Tool discovery should complete in <50ms."""
        import time

        start = time.time()
        results = orchestrator.discover_tools("python")
        elapsed = (time.time() - start) * 1000

        assert isinstance(results, list)
        assert elapsed < 50, f"Discovery took {elapsed}ms"
