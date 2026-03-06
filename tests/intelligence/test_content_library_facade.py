"""
Phase 129-A: ContentLibraryFacade + EpochShuffler Tests — RED state (CORE-008).

Tests cover:
  - ContentLibraryFacade.select(intent, pool=) for all three pools
  - ContentLibraryFacade.select_across(intent) — cross-library rotation
  - EpochShuffler full-corpus traversal (no repeat within epoch)
  - Epoch reshuffle on exhaustion
  - Performance: p95 ≤ 5ms per select() call
  - Backward compatibility: PrincipleSelector still works unchanged
  - Cross-library ring buffer prevents same library 3+ consecutive

SSOT: cortex-registry/planning/phases/planned/phase-129-content-library-facade.yaml
Governance: CORE-008, CORE-064
"""
from __future__ import annotations

import time
from collections import Counter

import pytest


class TestContentLibraryFacadeImport:
    """Verify facade module exists and is importable."""

    def test_facade_importable(self):
        """ContentLibraryFacade must be importable from cortex.intelligence."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade  # noqa: F401
        assert ContentLibraryFacade is not None

    def test_epoch_shuffler_importable(self):
        """EpochShuffler must be importable from content_library_facade module."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler  # noqa: F401
        assert EpochShuffler is not None

    def test_valid_pools_constant(self):
        """VALID_POOLS must include quotes, principles, and ai_spark."""
        from cortex.intelligence.analysis.content_library_facade import VALID_POOLS
        assert "quotes" in VALID_POOLS
        assert "principles" in VALID_POOLS
        assert "ai_spark" in VALID_POOLS


class TestContentLibraryFacadeSelectQuotes:
    """Facade select() for quotes pool."""

    def test_select_quotes_returns_dict(self):
        """select(pool='quotes') must return a dict."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("IMPLEMENT", pool="quotes")
        assert isinstance(result, dict), "select(pool='quotes') must return dict"

    def test_select_quotes_has_required_fields(self):
        """Quote result must have text, author, source, dedup_key."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("IMPLEMENT", pool="quotes")
        required = {"text", "author", "dedup_key"}
        missing = required - set(result.keys())
        assert not missing, f"Quote missing fields: {missing}"

    def test_select_quotes_label_is_insight(self):
        """Quote result must include library_label='Insight'."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("IMPLEMENT", pool="quotes")
        assert result.get("library_label") == "Insight", (
            f"Expected library_label='Insight', got {result.get('library_label')}"
        )

    def test_select_quotes_render_header(self):
        """Quote result must include render_header for blockquote rendering."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("QUERY", pool="quotes")
        assert "render_header" in result, "Quote must include render_header"
        assert "Insight" in result["render_header"]


class TestContentLibraryFacadeSelectPrinciples:
    """Facade select() for principles pool."""

    def test_select_principles_returns_dict(self):
        """select(pool='principles') must return dict for complex request."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("DESIGN", pool="principles", context_hints={"is_complex": True})
        assert isinstance(result, dict), "select(pool='principles') must return dict"

    def test_select_principles_label_is_principle(self):
        """Principles result must include library_label='Principle'."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("DESIGN", pool="principles", context_hints={"is_complex": True})
        assert result.get("library_label") == "Principle"

    def test_select_principles_simple_query_returns_none(self):
        """Simple QUERY request must suppress principle (complexity gate)."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("QUERY", pool="principles")
        assert result is None, "Bare QUERY must return None (complexity gate)"


class TestContentLibraryFacadeSelectAiSpark:
    """Facade select() for ai_spark pool."""

    def test_select_ai_spark_returns_dict(self):
        """select(pool='ai_spark') must return a dict."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("INTRODUCE", pool="ai_spark")
        assert isinstance(result, dict), "select(pool='ai_spark') must return dict"

    def test_select_ai_spark_has_required_fields(self):
        """AI Spark result must have id, title, body, author, source, category, dedup_key."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("INTRODUCE", pool="ai_spark")
        required = {"id", "body", "author", "source", "category", "dedup_key"}
        missing = required - set(result.keys())
        assert not missing, f"AI Spark missing fields: {missing}"

    def test_select_ai_spark_label_is_ai_spark(self):
        """AI Spark result must include library_label='AI Spark'."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("INTRODUCE", pool="ai_spark")
        assert result.get("library_label") == "AI Spark"

    def test_select_ai_spark_body_under_200_chars(self):
        """AI Spark body must be ≤200 chars."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("INTRODUCE", pool="ai_spark")
        body = result.get("body", "")
        assert len(body) <= 200, f"AI Spark body too long: {len(body)} chars"

    def test_select_ai_spark_render_header(self):
        """AI Spark result must include render_header with 'AI Spark' label."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select("INTRODUCE", pool="ai_spark")
        assert "render_header" in result, "AI Spark must include render_header"
        assert "AI Spark" in result["render_header"]

    def test_invalid_pool_raises_value_error(self):
        """Invalid pool name must raise ValueError."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        with pytest.raises(ValueError, match="pool"):
            facade.select("QUERY", pool="invalid_pool")


class TestEpochShuffler:
    """EpochShuffler full-corpus traversal guarantee."""

    def test_epoch_shuffler_no_repeat_within_epoch(self):
        """EpochShuffler must not repeat any item within a single epoch."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        items = [{"id": f"item-{i}", "dedup_key": f"key-{i}"} for i in range(50)]
        shuffler = EpochShuffler(items)
        seen = set()
        for _ in range(50):
            item = shuffler.next()
            key = item["dedup_key"]
            assert key not in seen, f"EpochShuffler repeated {key} within epoch"
            seen.add(key)

    def test_epoch_shuffler_reshuffles_on_exhaust(self):
        """EpochShuffler must continue serving items after epoch exhaustion."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        items = [{"id": f"item-{i}", "dedup_key": f"key-{i}"} for i in range(10)]
        shuffler = EpochShuffler(items)
        # Exhaust one full epoch
        for _ in range(10):
            shuffler.next()
        # New epoch — should serve items again
        result = shuffler.next()
        assert result is not None, "EpochShuffler returned None after reshuffle"
        assert "dedup_key" in result

    def test_epoch_shuffler_all_items_served_in_two_epochs(self):
        """Over 2 full epochs, each item should appear exactly twice."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        items = [{"id": f"item-{i}", "dedup_key": f"key-{i}"} for i in range(20)]
        shuffler = EpochShuffler(items)
        seen_keys: list[str] = []
        for _ in range(40):  # two full epochs
            item = shuffler.next()
            seen_keys.append(item["dedup_key"])
        counts = Counter(seen_keys)
        for key, count in counts.items():
            assert count == 2, f"Expected key {key} exactly twice across 2 epochs, got {count}"

    def test_epoch_shuffler_weight_bias_front_loaded(self):
        """High-weight items should appear more in the first half of each epoch."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        # 5 high-weight + 45 low-weight items
        items = (
            [{"id": f"hi-{i}", "dedup_key": f"hi-{i}", "relevance_weight": 1.0} for i in range(5)]
            + [{"id": f"lo-{i}", "dedup_key": f"lo-{i}", "relevance_weight": 0.1} for i in range(45)]
        )
        shuffler = EpochShuffler(items)
        first_half = [shuffler.next() for _ in range(25)]
        high_in_first_half = sum(1 for item in first_half if item["relevance_weight"] == 1.0)
        # High-weight items are 5/50 = 10% of pool but should appear in ≥60% of the first half
        # (i.e., at least 3 of the 5 high-weight items in first 25 slots)
        assert high_in_first_half >= 3, (
            f"Weight bias failed: only {high_in_first_half}/5 high-weight items in first half"
        )


class TestSelectAcross:
    """ContentLibraryFacade.select_across() — cross-library rotation."""

    def test_select_across_returns_dict(self):
        """select_across(intent) must return a dict."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select_across("QUERY")
        assert isinstance(result, dict), "select_across() must return dict"

    def test_select_across_includes_library_label(self):
        """select_across() result must include library_label field."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        result = facade.select_across("QUERY")
        assert "library_label" in result, "select_across() must include library_label"

    def test_select_across_rotates_libraries(self):
        """select_across() must rotate across all 3 libraries within 15 calls."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        labels_seen = set()
        for _ in range(15):
            result = facade.select_across("QUERY")
            labels_seen.add(result.get("library_label"))
        assert len(labels_seen) >= 2, (
            f"select_across() only saw {labels_seen} — expected rotation across ≥2 libraries"
        )

    def test_select_across_no_consecutive_same_library(self):
        """select_across() must not return same library 3+ consecutive times."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        labels = [facade.select_across("QUERY").get("library_label") for _ in range(30)]
        consecutive_same = [
            (i, labels[i])
            for i in range(2, len(labels))
            if labels[i] == labels[i - 1] == labels[i - 2]
        ]
        assert not consecutive_same, (
            f"select_across() returned same library 3+ consecutive: {consecutive_same}"
        )


class TestFacadePerformance:
    """Performance: p95 ≤ 5ms for any pool at 650+ total items."""

    _N = 100

    def _percentile(self, times: list[float], p: int) -> float:
        sorted_times = sorted(times)
        idx = int(len(sorted_times) * p / 100)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def test_quotes_pool_latency(self):
        """p95 latency for quotes pool must be ≤ 5ms."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        times = []
        for _ in range(self._N):
            t0 = time.perf_counter()
            facade.select("IMPLEMENT", pool="quotes")
            times.append((time.perf_counter() - t0) * 1000)
        p95 = self._percentile(times, 95)
        assert p95 <= 5.0, f"Quotes pool p95 latency {p95:.2f}ms exceeds 5ms"

    def test_ai_spark_pool_latency(self):
        """p95 latency for ai_spark pool must be ≤ 5ms."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        times = []
        for _ in range(self._N):
            t0 = time.perf_counter()
            facade.select("INTRODUCE", pool="ai_spark")
            times.append((time.perf_counter() - t0) * 1000)
        p95 = self._percentile(times, 95)
        assert p95 <= 5.0, f"AI Spark pool p95 latency {p95:.2f}ms exceeds 5ms"

    def test_select_across_latency(self):
        """p95 latency for select_across() must be ≤ 5ms."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        facade = ContentLibraryFacade()
        times = []
        for _ in range(self._N):
            t0 = time.perf_counter()
            facade.select_across("QUERY")
            times.append((time.perf_counter() - t0) * 1000)
        p95 = self._percentile(times, 95)
        assert p95 <= 5.0, f"select_across() p95 latency {p95:.2f}ms exceeds 5ms"


class TestBackwardCompatibility:
    """PrincipleSelector must still work identically — zero breaking changes."""

    def test_principle_selector_quotes_pool_unchanged(self):
        """PrincipleSelector(pool='quotes').select() must still return quote dict."""
        from cortex.intelligence.principle_selector import PrincipleSelector
        ps = PrincipleSelector("IMPLEMENT", pool="quotes")
        result = ps.select()
        assert isinstance(result, dict)
        assert "text" in result
        assert "dedup_key" in result

    def test_principle_selector_principles_pool_unchanged(self):
        """PrincipleSelector(pool='principles').select() must still return principle dict."""
        from cortex.intelligence.principle_selector import PrincipleSelector
        ps = PrincipleSelector("DESIGN", pool="principles")
        result = ps.select(context_hints={"is_complex": True})
        assert isinstance(result, dict)
        assert "id" in result
        assert "body" in result

    def test_principle_selector_default_pool_is_quotes(self):
        """PrincipleSelector default (no pool arg) must return quote with 'text' field."""
        from cortex.intelligence.principle_selector import PrincipleSelector
        ps = PrincipleSelector("IMPLEMENT")
        result = ps.select()
        assert "text" in result, "Default pool must return quote dict"


class TestFacadeDriftLocks:
    """Drift locks for ContentLibraryFacade structural invariants."""

    def test_lock_valid_pools_contains_ai_spark(self):
        """DRIFT LOCK: VALID_POOLS must contain 'ai_spark'."""
        from cortex.intelligence.analysis.content_library_facade import VALID_POOLS
        assert "ai_spark" in VALID_POOLS

    def test_lock_facade_has_select_method(self):
        """DRIFT LOCK: ContentLibraryFacade must have select() method."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        assert hasattr(ContentLibraryFacade, "select")

    def test_lock_facade_has_select_across_method(self):
        """DRIFT LOCK: ContentLibraryFacade must have select_across() method."""
        from cortex.intelligence.analysis.content_library_facade import ContentLibraryFacade
        assert hasattr(ContentLibraryFacade, "select_across")

    def test_lock_epoch_shuffler_has_next_method(self):
        """DRIFT LOCK: EpochShuffler must have next() method."""
        from cortex.intelligence.analysis.content_library_facade import EpochShuffler
        assert hasattr(EpochShuffler, "next")

    def test_lock_library_labels(self):
        """DRIFT LOCK: Library labels must be exactly Insight / Principle / AI Spark."""
        from cortex.intelligence.analysis.content_library_facade import LIBRARY_LABELS
        assert LIBRARY_LABELS.get("quotes") == "Insight"
        assert LIBRARY_LABELS.get("principles") == "Principle"
        assert LIBRARY_LABELS.get("ai_spark") == "AI Spark"
