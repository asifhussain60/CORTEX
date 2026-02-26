"""
Tests for phase-81-a: Knowledge MCP Tool Wiring to KnowledgeRegistryProxy.

AC_START: AC-81-KNOWLEDGE-GOLDEN-2026-02-26
Tests verify that cortex_knowledge MCP tool returns real results from
KnowledgeRegistryProxy, not hardcoded empty stubs.

Author: CORTEX Phase 81
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List

# These tests FAIL until implementation is complete (RED phase)


class TestCortexKnowledgeSearch:
    """Test that cortex_knowledge search operation wires to KnowledgeRegistryProxy."""

    @pytest.mark.asyncio
    async def test_cortex_knowledge_search_returns_results(self) -> None:
        """
        cortex_knowledge(op='search', query='tdd') must return non-empty results.

        Expected: ≥1 result from the 30 YAMLs in cortex-registry/knowledge/
        Current state: Returns hardcoded empty list (GAP-81-01)
        """
        # Import at test time to ensure stub is replaced during GREEN phase
        from cortex.mcp.tools.intelligence import CortexKnowledge

        tool = CortexKnowledge()
        result = await tool.execute(
            operation="search",
            query="tdd",
            domain=None,
        )

        assert result.success, f"Search failed: {result.error}"
        assert isinstance(result.data, dict), "Result data must be dict"
        assert "results" in result.data, "Result must have 'results' key"

        results = result.data["results"]
        assert isinstance(results, list), "Results must be list"
        assert len(results) > 0, (
            "Search for 'tdd' should return ≥1 results from knowledge YAMLs, "
            "but got empty list (hardcoded stub in cortex/mcp/tools/intelligence.py:491)"
        )

    @pytest.mark.asyncio
    async def test_cortex_knowledge_search_filters_by_domain(self) -> None:
        """cortex_knowledge search with domain parameter filters results."""
        from cortex.mcp.tools.intelligence import CortexKnowledge

        tool = CortexKnowledge()
        result = await tool.execute(
            operation="search",
            query="tdd",
            domain="testing-validation",
        )

        assert result.success, f"Search failed: {result.error}"
        results = result.data["results"]
        assert len(results) > 0, (
            "Search for 'tdd' in 'testing-validation' domain should return ≥1 results"
        )

        # All results should be from the specified domain
        for knowledge_item in results:
            assert (
                knowledge_item.get("domain") == "testing-validation"
            ), f"Expected domain 'testing-validation', got {knowledge_item.get('domain')}"


class TestCortexKnowledgeDomain:
    """Test that cortex_knowledge domain operation wires to KnowledgeRegistryProxy."""

    @pytest.mark.asyncio
    async def test_cortex_knowledge_domain_returns_entries(self) -> None:
        """
        cortex_knowledge(op='domain', query='backend-python') must return knowledge_items.

        Expected: ≥1 entry from backend-python domain in knowledge registry
        Current state: Returns hardcoded empty list (GAP-81-02)
        """
        from cortex.mcp.tools.intelligence import CortexKnowledge

        tool = CortexKnowledge()
        result = await tool.execute(
            operation="domain",
            query="backend-python",
            domain=None,
        )

        assert result.success, f"Domain lookup failed: {result.error}"
        assert isinstance(result.data, dict), "Result data must be dict"
        assert "knowledge_items" in result.data, "Result must have 'knowledge_items' key"

        knowledge_items = result.data["knowledge_items"]
        assert isinstance(knowledge_items, list), "Knowledge items must be list"
        assert len(knowledge_items) > 0, (
            "Domain 'backend-python' should return ≥1 knowledge items "
            "but got empty list (hardcoded stub in cortex/mcp/tools/intelligence.py:499)"
        )


class TestCortexKnowledgeGaps:
    """Test that cortex_knowledge gaps operation computes real coverage."""

    @pytest.mark.asyncio
    async def test_cortex_knowledge_gaps_returns_real_coverage(self) -> None:
        """
        cortex_knowledge(op='gaps') must return computed coverage, not hardcoded 0.85.

        Expected: coverage_score computed from actual domains in KnowledgeRegistryProxy
        Current state: Returns hardcoded 0.85 (GAP-81-03)
        """
        from cortex.mcp.tools.intelligence import CortexKnowledge

        tool = CortexKnowledge()
        result = await tool.execute(
            operation="gaps",
            query=None,
            domain=None,
        )

        assert result.success, f"Gaps lookup failed: {result.error}"
        assert isinstance(result.data, dict), "Result data must be dict"
        assert "coverage_score" in result.data, "Result must have 'coverage_score' key"

        coverage = result.data["coverage_score"]
        assert isinstance(coverage, (int, float)), "Coverage score must be numeric"
        assert 0 <= coverage <= 1, f"Coverage must be 0-1, got {coverage}"

        # The critical assertion: we should NOT get the hardcoded 0.85
        # unless the actual coverage happens to be exactly 0.85 (very unlikely)
        assert coverage != 0.85, (
            "Coverage should be computed from proxy.domains(), not hardcoded as 0.85 "
            "(see cortex/mcp/tools/intelligence.py:519)"
        )


class TestKnowledgeSynthesisEngineNoDuplicate:
    """Test that only one KnowledgeSynthesisEngine canonical implementation exists."""

    def test_no_duplicate_knowledge_synthesis_engine(self) -> None:
        """
        Only cortex/intelligence/knowledge/knowledge_synthesis_engine.py should exist.

        The stub at cortex/intelligence/knowledge_synthesis_engine.py must be deleted
        (CORE-035 violation: duplicate class names).

        Expected: Import succeeds from canonical path only
        Current state: Two files define KnowledgeSynthesisEngine (GAP-81-04)
        """
        # Canonical path should exist
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        assert KnowledgeSynthesisEngine is not None

        # The stub path should NOT exist — should raise ModuleNotFoundError
        # The stub at cortex/intelligence/knowledge_synthesis_engine.py was deleted in GREEN phase
        try:
            from cortex.intelligence.knowledge_synthesis_engine import (  # noqa: F401
                KnowledgeSynthesisEngine as KnowledgeSynthesisEngineStub,
            )
            # If we reach here, stub still exists (test should fail — call it out explicitly)
            pytest.fail(
                "Stub file cortex/intelligence/knowledge_synthesis_engine.py still exists. "
                "It should be deleted (only canonical at cortex/intelligence/knowledge/ remains)."
            )
        except (ModuleNotFoundError, ImportError):
            # Good — stub is deleted
            pass


@pytest.mark.integration
class TestMCPKnowledgeIntegration:
    """Integration test: MCP tool wires to proxy and returns real knowledge."""

    @pytest.mark.asyncio
    async def test_cortex_knowledge_end_to_end(self) -> None:
        """
        End-to-end: cortex_knowledge tool works with KnowledgeRegistryProxy.

        Flow: MCP request → CortexKnowledge.execute() → proxy.query() → real YAML data
        """
        from cortex.mcp.tools.intelligence import CortexKnowledge
        from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy

        tool = CortexKnowledge()
        proxy = KnowledgeRegistryProxy()

        # Both should be importable and functional
        assert tool is not None
        assert proxy is not None

        # Query via MCP tool should return same results as direct proxy.query()
        mcp_result = await tool.execute(
            operation="search",
            query="testing",
            domain=None,
        )
        assert mcp_result.success

        proxy_results = proxy.query(key_contains="testing")
        assert len(proxy_results) > 0

        # MCP results should match proxy results (in format, not necessarily exact order)
        assert len(mcp_result.data["results"]) == len(proxy_results), (
            f"MCP and proxy should return same number of results for 'testing' query. "
            f"MCP: {len(mcp_result.data['results'])}, Proxy: {len(proxy_results)}"
        )
