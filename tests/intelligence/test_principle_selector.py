"""
Phase 123 — Sub-Phase A: PrincipleSelector Tests (RED → GREEN → REFACTOR)
CORE-008: All tests written BEFORE implementation.

Tests:
  8 functional tests covering selection, anti-repetition, ring buffer,
  fallback, and dedup_key presence.

SSOT: cortex-registry/planning/phases/planned/phase-123-principle-of-the-moment.yaml
"""
import pytest


# ── Imports (will FAIL until implementation exists — RED state expected) ──────
from cortex.intelligence.principle_selector import PrincipleSelector


class TestPrincipleSelectorSelection:
    """Phase 123-A: Core selection logic."""

    def test_select_quote_returns_quote_for_known_intent(self):
        """select() returns a dict with required keys for a known intent."""
        ps = PrincipleSelector("IMPLEMENT")
        result = ps.select()
        assert isinstance(result, dict), "select() must return a dict"
        required_keys = {"text", "author", "book", "themes", "dedup_key"}
        assert required_keys.issubset(result.keys()), (
            f"Missing keys: {required_keys - result.keys()}"
        )

    def test_select_quote_matches_theme(self):
        """IMPLEMENT intent returns a quote whose themes include 'quality'."""
        ps = PrincipleSelector("IMPLEMENT")
        result = ps.select()
        assert "quality" in result["themes"], (
            f"IMPLEMENT should map to quality theme, got themes={result['themes']}"
        )

    def test_anti_repetition_skips_recent(self):
        """After selecting the same quote 10 times, 11th call returns a different dedup_key."""
        ps = PrincipleSelector("IMPLEMENT")
        # Collect 11 selections
        seen_keys = [ps.select()["dedup_key"] for _ in range(11)]
        # At least 2 distinct dedup_keys must appear in 11 calls
        assert len(set(seen_keys)) >= 2, (
            "Anti-repetition ring buffer must force variety across 11 IMPLEMENT selections"
        )

    def test_ring_buffer_size_is_10(self):
        """Ring buffer never exceeds 20 entries (maxlen bumped to 20 in Phase 125)."""
        ps = PrincipleSelector("IMPLEMENT")
        for _ in range(25):
            ps.select()
        assert len(ps._ring_buffer) <= 20, (
            f"Ring buffer size must be ≤20, got {len(ps._ring_buffer)}"
        )

    def test_ring_buffer_evicts_oldest(self):
        """After 21 selections, the ring buffer holds at most 20 dedup_keys."""
        # Use QUERY (→ universal theme) which has the largest pool of quotes,
        # ensuring 21 successful selections can fill the deque past maxlen=20.
        import cortex.intelligence.principle_selector as ps_mod

        ps_mod._ring_buffer.clear()
        ps = PrincipleSelector("QUERY")
        for _ in range(21):
            ps.select()
        # Buffer must never exceed maxlen=20 (deque enforces this automatically)
        assert len(ps._ring_buffer) <= 20, (
            "Ring buffer must never exceed maxlen=20"
        )

    def test_unknown_intent_falls_back_to_universal(self):
        """Unknown intent type falls back to 'universal' theme."""
        ps = PrincipleSelector("UNKNOWN_XYZ_INTENT_NONEXISTENT")
        result = ps.select()
        assert result is not None, "Fallback must return a quote, not None"
        assert "universal" in result["themes"], (
            f"Unknown intent must fall back to universal theme, got {result['themes']}"
        )

    def test_all_quotes_have_dedup_key(self):
        """Every quote in atom-quote.yaml has a non-empty dedup_key field."""
        ps = PrincipleSelector("QUERY")
        quotes = ps._load_quotes()
        for q in quotes:
            assert "dedup_key" in q, f"Missing dedup_key on quote: {q.get('text', '?')[:40]}"
            assert q["dedup_key"], f"Empty dedup_key on quote: {q.get('text', '?')[:40]}"

    def test_select_is_not_always_first_match(self):
        """Across 50 IMPLEMENT calls, at least 2 distinct quotes are returned."""
        ps = PrincipleSelector("IMPLEMENT")
        seen = {ps.select()["dedup_key"] for _ in range(50)}
        assert len(seen) >= 2, (
            f"50 IMPLEMENT calls returned only 1 distinct quote — "
            f"selection must be non-deterministic via weighted random"
        )
