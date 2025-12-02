"""
CORTEX 3.0 - Data Collection Scheduler (Phase 3.1)

Lightweight scheduler for triggering data collectors at a fixed interval.
Test-friendly design using a tick() method to avoid sleep in unit tests.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Callable
import time


@dataclass
class SchedulerStats:
    runs: int = 0
    last_run_ms: float = 0.0


class DataCollectionScheduler:
    """Simple, test-friendly scheduler that triggers coordinator collections.

    Usage:
      sched = DataCollectionScheduler(coordinator, interval_seconds=60)
      # In production you might call run_forever(); in tests, call tick().
    """

    def __init__(self, coordinator, interval_seconds: int = 60, on_after_run: Optional[Callable] = None):
        self.coordinator = coordinator
        self.interval_seconds = max(1, int(interval_seconds))
        self.on_after_run = on_after_run
        self._last_run_time = 0.0
        self.stats = SchedulerStats()

    def _should_run(self, now: float) -> bool:
        return (now - self._last_run_time) >= self.interval_seconds

    def tick(self, force_refresh: bool = False):
        """Trigger one run if interval elapsed since last run (or always if first run)."""
        now = time.time()
        if self._last_run_time == 0.0 or self._should_run(now):
            t0 = time.perf_counter()
            self.coordinator.collect_all(force_refresh=force_refresh)
            dt_ms = (time.perf_counter() - t0) * 1000.0
            self._last_run_time = now
            self.stats.runs += 1
            self.stats.last_run_ms = dt_ms
            if self.on_after_run:
                try:
                    self.on_after_run(self)
                except Exception:
                    # non-fatal callback
                    pass

    def run_forever(self, force_refresh: bool = False):
        """Naive loop runner (useful for manual runs)."""
        try:
            while True:
                self.tick(force_refresh=force_refresh)
                time.sleep(1)
        except KeyboardInterrupt:
            return
