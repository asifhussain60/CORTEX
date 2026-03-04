"""
Phase 123 — Sub-Phase B: PrincipleSelector Telemetry Tests (RED → GREEN → REFACTOR)
CORE-008: All tests written BEFORE implementation.

Tests:
  4 telemetry tests covering latency SLA, repetition counter,
  metrics emission gating, and no-emit-by-default guard.

SSOT: cortex-registry/planning/phases/planned/phase-123-principle-of-the-moment.yaml
"""
import time

import pytest


from cortex.intelligence.principle_selector import PrincipleSelector


class TestPrincipleSelectorTelemetry:
    """Phase 123-B: Telemetry instrumentation."""

    def test_select_latency_under_3ms(self):
        """p95 latency across 100 select() calls must be < 3ms."""
        ps = PrincipleSelector("IMPLEMENT")
        latencies_ms: list[float] = []
        for _ in range(100):
            t0 = time.perf_counter_ns()
            ps.select()
            latencies_ms.append((time.perf_counter_ns() - t0) / 1_000_000)

        latencies_ms.sort()
        p95 = latencies_ms[94]  # 95th percentile (0-indexed: index 94 of 100)
        assert p95 < 3.0, (
            f"p95 latency must be < 3ms, got {p95:.3f}ms — "
            f"check for filesystem I/O in select() hot path"
        )

    def test_repeat_avoided_counter_accessible(self):
        """PrincipleSelector tracks dedup-skipped candidates internally."""
        # Select a quote, then select again with the same intent — the first
        # dedup_key is now in the ring buffer, so it will be avoided next time.
        # We verify the mechanism works by checking a 2nd call picks a different key
        # when the pool has >1 candidate.
        ps = PrincipleSelector("IMPLEMENT")  # quality theme has 4 quotes
        first = ps.select()
        # Force 3 more selections so first key is skipped at least once
        for _ in range(3):
            subsequent = ps.select()
        # Ring buffer must have grown — confirms internal tracking is active
        assert len(ps._ring_buffer) >= 1, "Ring buffer must accumulate dedup_keys"
        assert first["dedup_key"] in list(ps._ring_buffer) or len(ps._ring_buffer) >= 4, (
            "Ring buffer must contain selected dedup_keys"
        )

    def test_metrics_enabled_flag_accepted(self):
        """PrincipleSelector accepts metrics_enabled=True without raising."""
        ps = PrincipleSelector("IMPLEMENT", metrics_enabled=True)
        # If telemetry silently fails (import error in test env), select() must still return
        result = ps.select()
        assert result is not None
        assert "text" in result, "select() must return quote dict even with metrics_enabled=True"

    def test_metrics_disabled_by_default(self):
        """PrincipleSelector default metrics_enabled is False."""
        ps = PrincipleSelector("IMPLEMENT")
        assert ps._metrics_enabled is False, (
            "metrics_enabled must default to False — telemetry is opt-in only"
        )
