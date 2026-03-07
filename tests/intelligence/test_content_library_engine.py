"""Tests for ContentLibraryEngine + EpochShuffler + cortex_content MCP tool (GAP-130-03).

Validates:
  - EpochShuffler provides Fisher-Yates epoch guarantees (no repeats within epoch)
  - ContentLibraryEngine manages 3 pools: quotes, principles, ai_sparks
  - ContentLibraryEngine.select_across() enforces mutual exclusion between pools
  - cortex_content MCP tool is registered and responds to select|history|reset|stats
  - ContentLibraryOrchestrator is importable and has orchestrate() method

AC-ID: AC-CLE-001
GAP-REF: GAP-130-03 (Phase 130-c — Foundation Backport)
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# EpochShuffler tests
# ---------------------------------------------------------------------------

class TestEpochShuffler:
    """EpochShuffler — Fisher-Yates shuffle per epoch, anti-repetition guarantee."""

    def test_import(self) -> None:
        """EpochShuffler must be importable from content_library_engine."""
        from cortex.intelligence.content_library_engine import EpochShuffler  # noqa: F401

    def test_instantiation(self) -> None:
        """EpochShuffler must accept a list of items at construction."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        items = ["a", "b", "c", "d", "e"]
        shuffler = EpochShuffler(items)
        assert shuffler is not None

    def test_next_returns_item_from_pool(self) -> None:
        """next() must return an item from the original pool."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        items = ["alpha", "beta", "gamma"]
        shuffler = EpochShuffler(items)
        result = shuffler.next()
        assert result in items

    def test_full_epoch_no_repeats(self) -> None:
        """Within a single epoch all N items must appear exactly once."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        items = list(range(10))
        shuffler = EpochShuffler(items)
        seen = [shuffler.next() for _ in range(len(items))]
        assert sorted(seen) == sorted(items), (
            "Each item must appear exactly once within an epoch"
        )
        assert len(set(seen)) == len(items), (
            "No duplicates allowed within an epoch"
        )

    def test_new_epoch_starts_after_exhaustion(self) -> None:
        """After N draws a new epoch begins automatically."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        items = ["x", "y", "z"]
        shuffler = EpochShuffler(items)
        # Exhaust first epoch
        first_epoch = [shuffler.next() for _ in range(len(items))]
        # Draw one from second epoch — should be in items
        second_start = shuffler.next()
        assert second_start in items

    def test_epoch_counter_increments(self) -> None:
        """epoch_number must increment after each full epoch is exhausted."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        items = ["p", "q"]
        shuffler = EpochShuffler(items)
        assert shuffler.epoch_number == 0
        shuffler.next()
        shuffler.next()  # epoch 0 exhausted
        assert shuffler.epoch_number == 1

    def test_single_item_pool(self) -> None:
        """Single-item pool must always return that item."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        shuffler = EpochShuffler(["only"])
        for _ in range(5):
            assert shuffler.next() == "only"

    def test_history_tracks_last_n_items(self) -> None:
        """history property must return the last n drawn items."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        items = list(range(20))
        shuffler = EpochShuffler(items, ring_buffer_size=5)
        draws = [shuffler.next() for _ in range(10)]
        history = shuffler.history
        assert len(history) <= 5, "Ring buffer must not exceed ring_buffer_size"
        assert all(h in items for h in history)

    def test_reset_restarts_epoch(self) -> None:
        """reset() must clear history and restart at epoch 0."""
        from cortex.intelligence.content_library_engine import EpochShuffler

        items = ["a", "b", "c"]
        shuffler = EpochShuffler(items)
        shuffler.next()
        shuffler.next()
        shuffler.reset()
        assert shuffler.epoch_number == 0
        assert shuffler.history == []


# ---------------------------------------------------------------------------
# ContentLibraryEngine tests
# ---------------------------------------------------------------------------

class TestContentLibraryEngine:
    """ContentLibraryEngine — manages quotes, principles, ai_sparks pools."""

    def test_import(self) -> None:
        """ContentLibraryEngine must be importable."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine  # noqa: F401

    def test_instantiation_no_args(self) -> None:
        """ContentLibraryEngine() must instantiate with no required arguments."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        assert engine is not None

    def test_has_three_pools(self) -> None:
        """Engine must expose quotes, principles, and ai_sparks pools."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        assert hasattr(engine, "quotes")
        assert hasattr(engine, "principles")
        assert hasattr(engine, "ai_sparks")

    def test_select_quote_returns_dict(self) -> None:
        """select('quotes') must return a dict with at least a 'text' key."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        result = engine.select("quotes")
        assert isinstance(result, dict), "select() must return a dict"
        assert "text" in result or "quote" in result, (
            "Quote result must have 'text' or 'quote' key"
        )

    def test_select_principle_returns_dict(self) -> None:
        """select('principles') must return a dict with a 'title' key."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        result = engine.select("principles")
        assert isinstance(result, dict)
        assert "title" in result, "Principle result must have 'title' key"

    def test_select_ai_spark_returns_dict(self) -> None:
        """select('ai_sparks') must return a dict with a 'body' key."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        result = engine.select("ai_sparks")
        assert isinstance(result, dict)
        assert "body" in result, "AI Spark result must have 'body' key"

    def test_select_invalid_pool_raises(self) -> None:
        """select() with unknown pool name must raise ValueError."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        with pytest.raises((ValueError, KeyError)):
            engine.select("nonexistent_pool")

    def test_select_across_mutual_exclusion(self) -> None:
        """select_across() must return exactly one item from one pool per call."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        # Run 20 selections — each must come from exactly one pool
        for _ in range(20):
            result = engine.select_across(["principles", "ai_sparks"])
            assert isinstance(result, dict)
            assert "pool" in result, "select_across() must declare which pool was selected"
            assert result["pool"] in ("principles", "ai_sparks")

    def test_history_method_exists(self) -> None:
        """engine.history(pool) must return a list."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        engine.select("quotes")
        hist = engine.history("quotes")
        assert isinstance(hist, list)

    def test_reset_method_exists(self) -> None:
        """engine.reset(pool) must be callable and return None."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        engine.select("principles")
        result = engine.reset("principles")
        assert result is None

    def test_stats_method_returns_dict(self) -> None:
        """engine.stats() must return a dict with pool stats."""
        from cortex.intelligence.content_library_engine import ContentLibraryEngine

        engine = ContentLibraryEngine()
        stats = engine.stats()
        assert isinstance(stats, dict)
        for pool_name in ("quotes", "principles", "ai_sparks"):
            assert pool_name in stats, f"stats() must include '{pool_name}' pool info"


# ---------------------------------------------------------------------------
# ContentLibraryOrchestrator tests
# ---------------------------------------------------------------------------

class TestContentLibraryOrchestrator:
    """ContentLibraryOrchestrator — response-layer wiring."""

    def test_import(self) -> None:
        """ContentLibraryOrchestrator must be importable."""
        from cortex.orchestrators.response.content_library_orchestrator import (  # noqa: F401
            ContentLibraryOrchestrator,
        )

    def test_instantiation(self) -> None:
        """ContentLibraryOrchestrator() must instantiate without required args."""
        from cortex.orchestrators.response.content_library_orchestrator import (
            ContentLibraryOrchestrator,
        )

        orch = ContentLibraryOrchestrator()
        assert orch is not None

    def test_has_orchestrate_method(self) -> None:
        """ContentLibraryOrchestrator must expose an orchestrate() method."""
        from cortex.orchestrators.response.content_library_orchestrator import (
            ContentLibraryOrchestrator,
        )

        assert hasattr(ContentLibraryOrchestrator, "orchestrate")

    def test_orchestrate_returns_dict(self) -> None:
        """orchestrate(pool='quotes') must return a dict."""
        from cortex.orchestrators.response.content_library_orchestrator import (
            ContentLibraryOrchestrator,
        )

        orch = ContentLibraryOrchestrator()
        result = orch.orchestrate(pool="quotes")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# cortex_content MCP tool registration tests
# ---------------------------------------------------------------------------

class TestCortexContentMcpTool:
    """cortex_content must be registered in PRODUCTION_TOOLS."""

    def test_cortex_content_in_registry(self) -> None:
        """cortex_content must be present in PRODUCTION_TOOLS dict."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS

        assert "cortex_content" in PRODUCTION_TOOLS, (
            "cortex_content must be registered in PRODUCTION_TOOLS (mcp_registry.py)"
        )

    def test_cortex_content_has_select_operation(self) -> None:
        """cortex_content must declare the 'select' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS

        ops = PRODUCTION_TOOLS["cortex_content"].get("operations", [])
        assert "select" in ops

    def test_cortex_content_has_history_operation(self) -> None:
        """cortex_content must declare the 'history' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS

        ops = PRODUCTION_TOOLS["cortex_content"].get("operations", [])
        assert "history" in ops

    def test_cortex_content_has_reset_operation(self) -> None:
        """cortex_content must declare the 'reset' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS

        ops = PRODUCTION_TOOLS["cortex_content"].get("operations", [])
        assert "reset" in ops

    def test_cortex_content_has_stats_operation(self) -> None:
        """cortex_content must declare the 'stats' operation."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS

        ops = PRODUCTION_TOOLS["cortex_content"].get("operations", [])
        assert "stats" in ops

    def test_tool_file_exists(self) -> None:
        """cortex/mcp/tools/cortex_content.py must exist."""
        tool_file = Path(__file__).parent.parent.parent / "cortex" / "mcp" / "tools" / "cortex_content.py"
        assert tool_file.exists(), (
            f"cortex_content.py tool implementation not found at {tool_file}"
        )

    def test_registry_tool_count_is_34(self) -> None:
        """Total registered tool count must be 34 after adding cortex_content."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS

        assert len(PRODUCTION_TOOLS) == 34, (
            f"Expected 34 tools in PRODUCTION_TOOLS, got {len(PRODUCTION_TOOLS)}"
        )

    def test_content_library_routing_yaml_exists(self) -> None:
        """content-library-routing.yaml workflow template must exist."""
        routing_yaml = (
            Path(__file__).parent.parent.parent
            / "cortex-registry"
            / "workflows"
            / "templates"
            / "lifecycle"
            / "content-library-routing.yaml"
        )
        assert routing_yaml.exists(), (
            f"content-library-routing.yaml not found at {routing_yaml}"
        )
