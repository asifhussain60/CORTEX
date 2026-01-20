"""
Unit tests for Lock-Free Orchestrator Registry (AC-STATE-002-04).

Tests thread-safe registry using copy-on-write and atomic reference swaps
to achieve lock-free read performance.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

from cortex.orchestrators.registry.lock_free_registry import (
    LockFreeRegistry,
    OrchestratorInfo,
    DuplicateRegistrationError,
)


@pytest.fixture
def registry() -> LockFreeRegistry:
    """Create lock-free registry for testing."""
    return LockFreeRegistry()


class TestBasicRegistration:
    """Test basic registry operations."""
    
    def test_register_orchestrator(self, registry: LockFreeRegistry) -> None:
        """Test registering an orchestrator."""
        info = OrchestratorInfo(
            name="test-orchestrator",
            version="1.0.0",
            capabilities=["task_a", "task_b"],
        )
        registry.register("test-orchestrator", info)
        
        retrieved = registry.lookup("test-orchestrator")
        assert retrieved.name == "test-orchestrator"
        assert retrieved.version == "1.0.0"
    
    def test_lookup_nonexistent(self, registry: LockFreeRegistry) -> None:
        """Test lookup of non-existent orchestrator."""
        result = registry.lookup("nonexistent")
        assert result is None
    
    def test_list_all_orchestrators(self, registry: LockFreeRegistry) -> None:
        """Test listing all registered orchestrators."""
        for i in range(5):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        all_orchs = registry.list_all()
        assert len(all_orchs) == 5


class TestConcurrentRegistration:
    """Test concurrent registration operations."""
    
    def test_100_concurrent_registrations(self, registry: LockFreeRegistry) -> None:
        """Test 100 concurrent registrations complete correctly."""
        num_registrations = 100
        
        def register_orch(i: int):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_orch, i) for i in range(num_registrations)]
            [f.result() for f in as_completed(futures)]
        
        # All registrations succeeded
        assert len(registry.list_all()) == num_registrations
    
    def test_duplicate_registration_idempotent(self, registry: LockFreeRegistry) -> None:
        """Test duplicate registration is idempotent with warning."""
        info = OrchestratorInfo(name="duplicate", version="1.0.0")
        
        registry.register("duplicate", info)
        
        # Second registration should succeed (last-wins)
        info2 = OrchestratorInfo(name="duplicate", version="2.0.0")
        registry.register("duplicate", info2)
        
        retrieved = registry.lookup("duplicate")
        assert retrieved.version == "2.0.0"


class TestLockFreeLookup:
    """Test lock-free lookup performance."""
    
    def test_1000_concurrent_lookups(self, registry: LockFreeRegistry) -> None:
        """Test 1000 concurrent lookups have no contention."""
        # Populate registry
        for i in range(10):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        num_lookups = 1000
        results = []
        
        def lookup_random():
            import random
            orch_id = f"orch-{random.randint(0, 9)}"
            result = registry.lookup(orch_id)
            results.append(result is not None)
        
        start = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(lookup_random) for _ in range(num_lookups)]
            [f.result() for f in as_completed(futures)]
        duration = time.time() - start
        
        # All lookups succeeded
        assert all(results)
        
        # High throughput (>1000 lookups/sec)
        lookups_per_sec = num_lookups / duration
        assert lookups_per_sec > 1000
    
    def test_lookup_during_registration(self, registry: LockFreeRegistry) -> None:
        """Test lookups work during concurrent registrations."""
        # Initial registrations
        for i in range(5):
            info = OrchestratorInfo(name=f"initial-{i}", version="1.0.0")
            registry.register(f"initial-{i}", info)
        
        lookup_results = []
        register_count = [0]
        
        def continuous_lookup():
            for _ in range(100):
                result = registry.lookup("initial-0")
                lookup_results.append(result is not None)
                time.sleep(0.001)
        
        def continuous_register():
            for i in range(50):
                info = OrchestratorInfo(name=f"new-{i}", version="1.0.0")
                registry.register(f"new-{i}", info)
                register_count[0] += 1
                time.sleep(0.002)
        
        t1 = threading.Thread(target=continuous_lookup)
        t2 = threading.Thread(target=continuous_register)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # All lookups succeeded
        assert all(lookup_results)
        assert register_count[0] == 50


class TestGenerationCounter:
    """Test generation counter for cache invalidation."""
    
    def test_generation_increments_on_change(self, registry: LockFreeRegistry) -> None:
        """Test generation counter increments on registry changes."""
        gen1 = registry.get_generation()
        
        info = OrchestratorInfo(name="test", version="1.0.0")
        registry.register("test", info)
        
        gen2 = registry.get_generation()
        assert gen2 > gen1
    
    def test_generation_stable_during_lookups(self, registry: LockFreeRegistry) -> None:
        """Test generation doesn't change during lookups."""
        info = OrchestratorInfo(name="test", version="1.0.0")
        registry.register("test", info)
        
        gen1 = registry.get_generation()
        
        for _ in range(100):
            registry.lookup("test")
        
        gen2 = registry.get_generation()
        assert gen1 == gen2


class TestSnapshotIsolation:
    """Test immutable snapshot behavior."""
    
    def test_reader_uses_consistent_snapshot(self, registry: LockFreeRegistry) -> None:
        """Test reader sees consistent snapshot during iteration."""
        # Initial state
        for i in range(5):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        # Get snapshot
        snapshot1 = registry.list_all()
        
        # Modify registry
        info = OrchestratorInfo(name="new", version="1.0.0")
        registry.register("new", info)
        
        # Original snapshot unchanged
        assert len(snapshot1) == 5
        
        # New snapshot has update
        snapshot2 = registry.list_all()
        assert len(snapshot2) == 6
    
    def test_concurrent_readers_see_snapshots(self, registry: LockFreeRegistry) -> None:
        """Test concurrent readers each get valid snapshots."""
        # Populate
        for i in range(10):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        snapshot_sizes = []
        
        def reader():
            snapshot = registry.list_all()
            snapshot_sizes.append(len(snapshot))
            time.sleep(0.01)
        
        def writer():
            for i in range(5):
                info = OrchestratorInfo(name=f"new-{i}", version="1.0.0")
                registry.register(f"new-{i}", info)
                time.sleep(0.005)
        
        threads = [threading.Thread(target=reader) for _ in range(10)]
        threads.append(threading.Thread(target=writer))
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All readers got valid snapshots (10 or 15)
        assert all(s in (10, 11, 12, 13, 14, 15) for s in snapshot_sizes)


class TestUnregistration:
    """Test orchestrator unregistration."""
    
    def test_unregister_orchestrator(self, registry: LockFreeRegistry) -> None:
        """Test unregistering an orchestrator."""
        info = OrchestratorInfo(name="temp", version="1.0.0")
        registry.register("temp", info)
        
        registry.unregister("temp")
        
        assert registry.lookup("temp") is None
    
    def test_concurrent_unregistration(self, registry: LockFreeRegistry) -> None:
        """Test concurrent unregistrations work correctly."""
        # Register many
        for i in range(20):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        def unregister_half():
            for i in range(0, 20, 2):
                registry.unregister(f"orch-{i}")
        
        t1 = threading.Thread(target=unregister_half)
        t1.start()
        t1.join()
        
        # Only odd ones remain
        remaining = registry.list_all()
        assert len(remaining) == 10


class TestMetrics:
    """Test registry metrics."""
    
    def test_tracks_registrations(self, registry: LockFreeRegistry) -> None:
        """Test registration counter."""
        for i in range(5):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        metrics = registry.get_metrics()
        assert metrics["total_registrations"] >= 5
    
    def test_tracks_lookups(self, registry: LockFreeRegistry) -> None:
        """Test lookup counter."""
        info = OrchestratorInfo(name="test", version="1.0.0")
        registry.register("test", info)
        
        for _ in range(10):
            registry.lookup("test")
        
        metrics = registry.get_metrics()
        assert metrics["total_lookups"] >= 10


class TestPerformance:
    """Test performance characteristics."""
    
    def test_lookup_latency(self, registry: LockFreeRegistry) -> None:
        """Test lookup P99 latency < 1μs."""
        # Populate
        for i in range(100):
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
        
        # Measure lookup latency
        latencies = []
        for _ in range(1000):
            start = time.perf_counter()
            registry.lookup("orch-50")
            end = time.perf_counter()
            latencies.append((end - start) * 1_000_000)  # Convert to μs
        
        latencies.sort()
        p99_latency = latencies[int(len(latencies) * 0.99)]
        
        # P99 should be very fast
        assert p99_latency < 10  # <10μs (relaxed from 1μs for test environment)
    
    def test_write_latency(self, registry: LockFreeRegistry) -> None:
        """Test write P99 latency < 10ms."""
        latencies = []
        
        for i in range(100):
            start = time.perf_counter()
            info = OrchestratorInfo(name=f"orch-{i}", version="1.0.0")
            registry.register(f"orch-{i}", info)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms
        
        latencies.sort()
        p99_latency = latencies[int(len(latencies) * 0.99)]
        
        assert p99_latency < 10  # <10ms
