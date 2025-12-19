import time
import pytest

from src.operations.data_collectors.real_time_collectors import (
    BaseDataCollector,
    DataCollectionCoordinator,
)


class _StubCollector(BaseDataCollector):
    def __init__(self):
        super().__init__("stub", "stub desc")
        self._count = 0
    def collect(self):
        self._count += 1
        return {"value": self._count}


@pytest.mark.unit
def test_collect_with_cache_and_force_refresh():
    c = _StubCollector()
    c.cache_duration_seconds = 60

    r1 = c.collect_with_cache()
    r2 = c.collect_with_cache()
    assert r1.success and r2.success
    # Cached: same value and timestamp newer only if forced
    assert r1.data["value"] == 1
    assert r2.data["value"] == 1  # cached

    r3 = c.collect_with_cache(force_refresh=True)
    assert r3.data["value"] == 2  # forced refresh increments


@pytest.mark.unit
def test_coordinator_collect_all_handles_failures_and_returns_results():
    class _FailingCollector(BaseDataCollector):
        def __init__(self):
            super().__init__("fail", "always fails")
        def collect(self):
            raise RuntimeError("boom")

    coord = DataCollectionCoordinator()
    coord.collectors["stub"] = _StubCollector()
    coord.collectors["fail"] = _FailingCollector()

    results = coord.collect_all(force_refresh=True)
    assert set(results.keys()) >= {"stub", "fail"}
    assert results["stub"].success is True
    assert results["fail"].success is False


@pytest.mark.unit
def test_scheduler_tick_runs_collection(monkeypatch):
    # We will import the scheduler after defining a minimal stub using monkeypatch
    from src.operations.data_collectors.real_time_collectors import DataCollectionCoordinator

    coord = DataCollectionCoordinator()

    collected = {}
    def fake_collect_all(force_refresh=False):
        collected["called"] = collected.get("called", 0) + 1
        return {"brain_metrics": type("R", (), {"success": True})()}

    monkeypatch.setattr(coord, "collect_all", fake_collect_all)

    # Import here to avoid circulars
    from src.operations.data_collectors.scheduler import DataCollectionScheduler

    sched = DataCollectionScheduler(coordinator=coord, interval_seconds=60)
    # tick should invoke collect_all exactly once
    sched.tick()
    assert collected.get("called", 0) == 1
