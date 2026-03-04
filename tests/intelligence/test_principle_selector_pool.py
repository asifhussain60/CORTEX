"""
Phase 124-C: Tests for PrincipleSelector pool='principles' extension.

RED gate: All tests fail (pool parameter not yet supported).
GREEN gate: All tests pass after pool extension implemented.

Governance: CORE-008 (TDD mandatory), CORE-002 (no .md report files).
"""
from __future__ import annotations

import time

import pytest

from cortex.intelligence.principle_selector import PrincipleSelector


REQUIRED_PRINCIPLE_FIELDS = {"id", "title", "body", "domain", "tags", "intent_types"}


class TestPrincipleSelectorPoolExtension:
    def test_pool_principles_returns_dict(self):
        """PrincipleSelector with pool='principles' must return a dict."""
        ps = PrincipleSelector("QUERY", pool="principles")
        result = ps.select()
        assert isinstance(result, dict), "select() must return a dict"

    def test_pool_principles_has_required_fields(self):
        """Principle result must have id, title, body, domain, tags, intent_types."""
        ps = PrincipleSelector("QUERY", pool="principles")
        result = ps.select()
        missing = REQUIRED_PRINCIPLE_FIELDS - set(result.keys())
        assert not missing, f"Principle result missing fields: {missing}"

    def test_pool_principles_filters_by_intent(self):
        """DESIGN intent should prefer architecture/api_design/security domains."""
        ps = PrincipleSelector("DESIGN", pool="principles")
        results = [ps.select() for _ in range(20)]
        domains = {r["domain"] for r in results}
        # Architecture-related domains must appear in 20 samples
        arch_domains = {"architecture", "api_design", "security"}
        assert domains & arch_domains, (
            f"DESIGN intent produced no arch domains in 20 samples: {domains}"
        )

    def test_pool_principles_anti_repetition(self):
        """Consecutive selects from principles pool should not repeat immediately."""
        import cortex.intelligence.principle_selector as ps_mod

        ps_mod._ring_buffer.clear()
        ps = PrincipleSelector("QUERY", pool="principles")
        seen = set()
        duplicates = 0
        for _ in range(10):
            r = ps.select()
            key = r["id"]
            if key in seen:
                duplicates += 1
            seen.add(key)
        # With 30 principles and a ring buffer of 10, duplicates in 10 draws should be 0
        assert duplicates == 0, (
            f"Got {duplicates} immediate repeats in 10 selections from principles pool"
        )

    def test_pool_quotes_still_works(self):
        """Default pool='quotes' must still work after pool extension."""
        ps = PrincipleSelector("IMPLEMENT", pool="quotes")
        result = ps.select()
        assert "text" in result or "body" in result, (
            "Default quotes pool must return a quote dict"
        )

    def test_pool_default_is_quotes(self):
        """Omitting pool= must default to quotes pool behaviour."""
        ps_default = PrincipleSelector("IMPLEMENT")
        ps_quotes = PrincipleSelector("IMPLEMENT", pool="quotes")
        r1 = ps_default.select()
        r2 = ps_quotes.select()
        # Both should have 'text' (quote field), not 'body' (principle field)
        assert "text" in r1, "Default pool must return quote with 'text' field"
        assert "text" in r2, "Explicit pool='quotes' must return quote with 'text' field"

    def test_pool_principles_latency_under_5ms(self):
        """p95 latency for principles pool must be under 5ms."""
        ps = PrincipleSelector("QUERY", pool="principles")
        # Warm up
        ps.select()
        latencies = []
        for _ in range(100):
            t0 = time.perf_counter_ns()
            ps.select()
            latencies.append((time.perf_counter_ns() - t0) / 1_000_000)
        latencies.sort()
        p95 = latencies[94]
        assert p95 < 5.0, f"p95 latency {p95:.2f}ms exceeds 5ms budget"

    def test_pool_invalid_raises_value_error(self):
        """Unsupported pool name must raise ValueError immediately."""
        with pytest.raises(ValueError, match="pool"):
            ps = PrincipleSelector("QUERY", pool="invalid_pool_xyz")
            ps.select()

    def test_pool_principles_tdd_intent_returns_tdd_domain(self):
        """TDD intent must return at least one tdd or testing domain in 20 samples."""
        ps = PrincipleSelector("TDD", pool="principles")
        results = [ps.select() for _ in range(20)]
        domains = {r["domain"] for r in results}
        assert domains & {"tdd", "testing"}, (
            f"TDD intent returned no tdd/testing domain in 20 samples: {domains}"
        )

    def test_pool_principles_unknown_intent_returns_any_principle(self):
        """Unknown intent with pool='principles' must still return a valid principle."""
        ps = PrincipleSelector("UNKNOWN_INTENT_XYZ", pool="principles")
        result = ps.select()
        assert result is not None
        assert "id" in result, "Unknown intent fallback must return a principle with id"
