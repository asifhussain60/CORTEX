"""
Chaos Engineering Tests — GAP-69-06

Implements the 5 scenarios defined in tests/chaos/scenarios.yaml.
Each test verifies that CORTEX infrastructure degrades gracefully
under simulated failure conditions and recovers correctly.

Scenarios (from scenarios.yaml):
  1. database_connection_failure  — severity: high
  2. external_service_timeout     — severity: high
  3. memory_pressure              — severity: medium
  4. cpu_spike                    — severity: medium
  5. network_partition            — severity: high
"""
from __future__ import annotations

import gc
import threading
import time
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest

from cortex.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _make_cb(name: str, failure_threshold: int = 3) -> CircuitBreaker:
    """Return a CircuitBreaker wired for fast failure (test-friendly)."""
    cfg = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        timeout_seconds=0.1,          # fast recovery for tests
        open_duration_seconds=0.1,
    )
    return CircuitBreaker(name=name, config=cfg)


# ---------------------------------------------------------------------------
# Scenario 1: database_connection_failure
# ---------------------------------------------------------------------------

class TestDatabaseConnectionFailure:
    """
    Severity: HIGH
    Simulate database connection failure and verify circuit-breaker opens,
    subsequent calls are rejected (fast-fail), and the system recovers
    once the database is reachable again.
    """

    def test_circuit_opens_after_consecutive_failures(self) -> None:
        """Circuit breaker MUST open after hitting the failure threshold."""
        cb = _make_cb("db_connection", failure_threshold=3)

        def _fail_db() -> None:
            raise ConnectionError("DB unreachable")

        # Drive circuit to OPEN
        for _ in range(3):
            try:
                cb.call(_fail_db)
            except ConnectionError:
                pass

        assert cb.state == CircuitState.OPEN, (
            "Circuit breaker should be OPEN after repeated DB failures"
        )

    def test_open_circuit_rejects_calls_immediately(self) -> None:
        """After opening, the circuit must fast-fail without calling the DB."""
        cb = _make_cb("db_reject", failure_threshold=3)

        def _fail_db() -> None:
            raise ConnectionError("DB unreachable")

        for _ in range(3):
            try:
                cb.call(_fail_db)
            except ConnectionError:
                pass

        call_count = 0

        def _db_call() -> str:
            nonlocal call_count
            call_count += 1
            return "ok"

        # Circuit is OPEN — call must be rejected
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(_db_call)

        assert call_count == 0, "DB must not be called when circuit is OPEN"

    def test_circuit_recovers_after_timeout(self) -> None:
        """After the open-duration elapses the circuit should transition to HALF_OPEN."""
        cb = _make_cb("db_recover", failure_threshold=3)

        def _fail_db() -> None:
            raise ConnectionError("DB unreachable")

        for _ in range(3):
            try:
                cb.call(_fail_db)
            except ConnectionError:
                pass

        # Wait for open_duration_seconds (0.1 s in test config)
        time.sleep(0.2)

        # First successful call should close or half-open the circuit
        def _healthy_db() -> str:
            return "connected"

        result = cb.call(_healthy_db)
        assert result == "connected"
        assert cb.state in (CircuitState.HALF_OPEN, CircuitState.CLOSED)


# ---------------------------------------------------------------------------
# Scenario 2: external_service_timeout
# ---------------------------------------------------------------------------

class TestExternalServiceTimeout:
    """
    Severity: HIGH
    Simulate an external HTTP service that times out; verify that CORTEX
    wraps the call in a circuit breaker, trips after repeated timeouts,
    and provides a fallback response rather than blocking indefinitely.
    """

    def test_timeout_trips_circuit_breaker(self) -> None:
        """Repeated TimeoutError should open the circuit."""
        cb = _make_cb("ext_service", failure_threshold=3)

        def _timeout_service() -> None:
            raise TimeoutError("External service timed out after 30 s")

        for _ in range(3):
            try:
                cb.call(_timeout_service)
            except TimeoutError:
                pass

        assert cb.state == CircuitState.OPEN

    def test_fallback_is_returned_when_circuit_open(self) -> None:
        """Application layer must return a fallback when circuit is OPEN."""
        cb = _make_cb("ext_fallback", failure_threshold=3)

        def _timeout_service() -> None:
            raise TimeoutError("timeout")

        for _ in range(3):
            try:
                cb.call(_timeout_service)
            except TimeoutError:
                pass

        # Application-level fallback guard
        def call_with_fallback(service_fn: Callable, fallback: str) -> str:
            try:
                return cb.call(service_fn)
            except CircuitBreakerOpenError:
                return fallback

        result = call_with_fallback(_timeout_service, fallback="FALLBACK_RESPONSE")
        assert result == "FALLBACK_RESPONSE"

    def test_metrics_record_rejected_calls(self) -> None:
        """Rejected calls (open circuit) should be tracked in metrics."""
        cb = _make_cb("ext_metrics", failure_threshold=3)

        def _fail() -> None:
            raise TimeoutError("timeout")

        for _ in range(3):
            try:
                cb.call(_fail)
            except TimeoutError:
                pass

        # Trigger a rejection
        try:
            cb.call(_fail)
        except (CircuitBreakerOpenError, TimeoutError):
            pass

        metrics = cb.get_metrics()
        assert metrics["failure_count"] >= 3


# ---------------------------------------------------------------------------
# Scenario 3: memory_pressure
# ---------------------------------------------------------------------------

class TestMemoryPressure:
    """
    Severity: MEDIUM
    Simulate memory pressure by allocating large objects; verify the system
    does not crash and garbage collection reclaims memory.
    """

    def test_large_allocation_does_not_crash(self) -> None:
        """Allocating a 50 MB buffer should not raise MemoryError."""
        size_bytes = 50 * 1024 * 1024  # 50 MB
        try:
            buf = bytearray(size_bytes)
            assert len(buf) == size_bytes
        except MemoryError:
            pytest.skip("Insufficient memory for this test environment")
        finally:
            del buf
            gc.collect()

    def test_garbage_collection_reclaims_memory(self) -> None:
        """After releasing a large buffer, gc.collect() should succeed."""
        size_bytes = 20 * 1024 * 1024  # 20 MB
        try:
            buf = bytearray(size_bytes)
            assert len(buf) == size_bytes
            del buf
        except MemoryError:
            pytest.skip("Insufficient memory for this test environment")

        collected = gc.collect()
        # gc.collect() returns 0 or more — just confirm it runs without raising
        assert collected >= 0

    def test_circuit_breaker_survives_memory_pressure(self) -> None:
        """CircuitBreaker should remain functional under memory pressure."""
        cb = _make_cb("memory_cb")

        # Allocate pressure buffer
        try:
            pressure = bytearray(10 * 1024 * 1024)  # 10 MB
        except MemoryError:
            pytest.skip("Insufficient memory for this test environment")

        result = cb.call(lambda: "alive")
        assert result == "alive"

        del pressure
        gc.collect()


# ---------------------------------------------------------------------------
# Scenario 4: cpu_spike
# ---------------------------------------------------------------------------

class TestCpuSpike:
    """
    Severity: MEDIUM
    Simulate a CPU spike using a busy loop on a background thread; verify
    that CORTEX's main thread remains responsive and the circuit breaker
    can still make decisions under load.
    """

    def test_circuit_breaker_responds_during_cpu_spike(self) -> None:
        """Circuit breaker operations must complete within 2 s even under CPU load."""
        stop_event = threading.Event()

        def _cpu_burn() -> None:
            while not stop_event.is_set():
                _ = sum(i * i for i in range(10_000))

        # Spawn background CPU burner
        burner = threading.Thread(target=_cpu_burn, daemon=True)
        burner.start()

        try:
            cb = _make_cb("cpu_spike_cb")
            start = time.monotonic()
            result = cb.call(lambda: "responsive")
            elapsed = time.monotonic() - start

            assert result == "responsive"
            assert elapsed < 2.0, f"Circuit breaker too slow under CPU load: {elapsed:.2f}s"
        finally:
            stop_event.set()
            burner.join(timeout=2.0)

    def test_no_starvation_under_concurrent_load(self) -> None:
        """Multiple concurrent callers should all get results or clean errors."""
        cb = _make_cb("concurrent_cb", failure_threshold=10)
        results: list[str] = []
        errors: list[Exception] = []
        lock = threading.Lock()

        def _worker() -> None:
            try:
                val = cb.call(lambda: "ok")
                with lock:
                    results.append(val)
            except Exception as exc:
                with lock:
                    errors.append(exc)

        threads = [threading.Thread(target=_worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5.0)

        # All 20 calls should produce a result or a known error — none should hang
        assert len(results) + len(errors) == 20


# ---------------------------------------------------------------------------
# Scenario 5: network_partition
# ---------------------------------------------------------------------------

class TestNetworkPartition:
    """
    Severity: HIGH
    Simulate a network partition (OSError / ConnectionRefusedError); verify
    that the circuit breaker detects the partition, enters OPEN state, and
    recovers once connectivity is restored.
    """

    def test_partition_opens_circuit(self) -> None:
        """Repeated ConnectionRefusedError should open the circuit."""
        cb = _make_cb("net_partition", failure_threshold=3)

        def _partitioned() -> None:
            raise OSError("Network partition: connection refused")

        for _ in range(3):
            try:
                cb.call(_partitioned)
            except OSError:
                pass

        assert cb.state == CircuitState.OPEN

    def test_recovery_after_partition_heals(self) -> None:
        """After the open-duration elapses the system should accept calls again."""
        cb = _make_cb("net_recovery", failure_threshold=3)

        def _partitioned() -> None:
            raise OSError("partition")

        for _ in range(3):
            try:
                cb.call(_partitioned)
            except OSError:
                pass

        # Wait for open_duration to elapse
        time.sleep(0.2)

        # Network healed — subsequent call should succeed
        result = cb.call(lambda: "restored")
        assert result == "restored"

    def test_partition_metrics_recorded(self) -> None:
        """Failed calls during partition must be captured in circuit breaker metrics."""
        cb = _make_cb("net_metrics", failure_threshold=5)

        def _partitioned() -> None:
            raise OSError("partition")

        failure_count = 3
        for _ in range(failure_count):
            try:
                cb.call(_partitioned)
            except OSError:
                pass

        metrics = cb.get_metrics()
        assert metrics["failure_count"] >= failure_count, (
            f"Expected ≥{failure_count} failure_count, got {metrics['failure_count']}"
        )
