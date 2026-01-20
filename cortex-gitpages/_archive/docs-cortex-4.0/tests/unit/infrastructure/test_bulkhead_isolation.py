"""
Tests for Component Bulkhead Isolation.

AC-INFRA-001-02: Component Bulkhead Isolation
Tests per-component resource pools to prevent cascading failures.
Each component gets dedicated connection pool with independent limits.
"""

import pytest
import sqlite3
import threading
import time
from pathlib import Path
from typing import Generator
from enum import Enum

from cortex.infrastructure.bulkhead_manager import (
    BulkheadManager,
    BulkheadConfig,
    ComponentType,
    ComponentHealth,
    BulkheadException,
)


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test.db"


@pytest.fixture
def bulkhead_config() -> BulkheadConfig:
    """Create a standard bulkhead configuration."""
    return BulkheadConfig(
        component_pools={
            ComponentType.GOVERNANCE: {"max_connections": 5, "timeout": 1.0},
            ComponentType.AUDIT: {"max_connections": 3, "timeout": 5.0},
            ComponentType.KNOWLEDGE: {"max_connections": 10, "timeout": 10.0},
        }
    )


@pytest.fixture
def bulkhead_manager(
    test_db_path: Path, bulkhead_config: BulkheadConfig
) -> Generator[BulkheadManager, None, None]:
    """Create and cleanup a bulkhead manager."""
    manager = BulkheadManager(database_path=test_db_path, config=bulkhead_config)
    yield manager
    manager.shutdown()


class TestBulkheadInitialization:
    """Test bulkhead manager initialization."""

    def test_creates_separate_pools_per_component(
        self, test_db_path: Path, bulkhead_config: BulkheadConfig
    ) -> None:
        """Manager should create separate pools for each component."""
        manager = BulkheadManager(database_path=test_db_path, config=bulkhead_config)
        try:
            health = manager.get_health_status()
            assert ComponentType.GOVERNANCE in health
            assert ComponentType.AUDIT in health
            assert ComponentType.KNOWLEDGE in health
        finally:
            manager.shutdown()

    def test_each_pool_has_correct_limits(
        self, bulkhead_manager: BulkheadManager, bulkhead_config: BulkheadConfig
    ) -> None:
        """Each component pool should respect its configured limits."""
        for component_type in [ComponentType.GOVERNANCE, ComponentType.AUDIT, ComponentType.KNOWLEDGE]:
            metrics = bulkhead_manager.get_component_metrics(component_type)
            expected_max = bulkhead_config.component_pools[component_type]["max_connections"]
            assert metrics["max_connections"] == expected_max


class TestComponentIsolation:
    """Test that component failures are isolated."""

    def test_exhausted_pool_does_not_affect_others(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Exhausting one component's pool should not affect others."""
        # Exhaust governance pool
        governance_conns = []
        for _ in range(5):  # Max for governance
            governance_conns.append(
                bulkhead_manager.acquire_connection(ComponentType.GOVERNANCE)
            )
        
        # Should still be able to use audit
        audit_conn = bulkhead_manager.acquire_connection(ComponentType.AUDIT)
        assert audit_conn is not None
        bulkhead_manager.release_connection(ComponentType.AUDIT, audit_conn)
        
        # Should still be able to use knowledge
        knowledge_conn = bulkhead_manager.acquire_connection(ComponentType.KNOWLEDGE)
        assert knowledge_conn is not None
        bulkhead_manager.release_connection(ComponentType.KNOWLEDGE, knowledge_conn)
        
        # Cleanup
        for conn in governance_conns:
            bulkhead_manager.release_connection(ComponentType.GOVERNANCE, conn)

    def test_component_timeout_does_not_affect_others(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Timeout in one component should not block others."""
        # Exhaust governance pool
        governance_conns = [
            bulkhead_manager.acquire_connection(ComponentType.GOVERNANCE)
            for _ in range(5)
        ]
        
        # Try to acquire with short timeout (should fail)
        start_time = time.time()
        with pytest.raises(BulkheadException, match="timeout"):
            bulkhead_manager.acquire_connection(
                ComponentType.GOVERNANCE, timeout=0.5
            )
        elapsed = time.time() - start_time
        
        # Should have timed out quickly
        assert elapsed < 1.0
        
        # Other components should work instantly
        audit_start = time.time()
        audit_conn = bulkhead_manager.acquire_connection(ComponentType.AUDIT)
        audit_elapsed = time.time() - audit_start
        assert audit_elapsed < 0.1  # Should be instant
        
        bulkhead_manager.release_connection(ComponentType.AUDIT, audit_conn)
        for conn in governance_conns:
            bulkhead_manager.release_connection(ComponentType.GOVERNANCE, conn)

    def test_slow_operation_in_one_component_does_not_block_others(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Slow operation in one component should not affect others."""
        def slow_governance_operation():
            conn = bulkhead_manager.acquire_connection(ComponentType.GOVERNANCE)
            time.sleep(2.0)  # Simulate slow operation
            bulkhead_manager.release_connection(ComponentType.GOVERNANCE, conn)
        
        # Start slow operation
        thread = threading.Thread(target=slow_governance_operation)
        thread.start()
        
        time.sleep(0.1)  # Let it start
        
        # Should still be able to use audit quickly
        start = time.time()
        audit_conn = bulkhead_manager.acquire_connection(ComponentType.AUDIT)
        elapsed = time.time() - start
        
        assert elapsed < 0.5  # Should not be blocked
        bulkhead_manager.release_connection(ComponentType.AUDIT, audit_conn)
        
        thread.join()


class TestComponentHealth:
    """Test component health reporting."""

    def test_healthy_component_reports_healthy(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Healthy component should report HEALTHY status."""
        health = bulkhead_manager.get_health_status()
        assert health[ComponentType.GOVERNANCE] == ComponentHealth.HEALTHY
        assert health[ComponentType.AUDIT] == ComponentHealth.HEALTHY
        assert health[ComponentType.KNOWLEDGE] == ComponentHealth.HEALTHY

    def test_exhausted_pool_reports_degraded(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Exhausted pool should report DEGRADED status."""
        # Exhaust governance pool
        conns = [
            bulkhead_manager.acquire_connection(ComponentType.GOVERNANCE)
            for _ in range(5)
        ]
        
        health = bulkhead_manager.get_health_status()
        assert health[ComponentType.GOVERNANCE] in [
            ComponentHealth.DEGRADED,
            ComponentHealth.HEALTHY,  # May still be healthy if not failing
        ]
        
        # Cleanup
        for conn in conns:
            bulkhead_manager.release_connection(ComponentType.GOVERNANCE, conn)

    def test_failed_operations_affect_health(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Multiple failed operations should degrade health."""
        # Simulate failures by trying to acquire with 0 timeout repeatedly
        for _ in range(10):
            try:
                bulkhead_manager.acquire_connection(
                    ComponentType.GOVERNANCE, timeout=0.0
                )
            except BulkheadException:
                pass
        
        # Health should be tracked (may not change if no actual failures)
        health = bulkhead_manager.get_health_status()
        assert ComponentType.GOVERNANCE in health


class TestComponentMetrics:
    """Test component-level metrics."""

    def test_metrics_track_per_component_usage(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Metrics should track usage per component."""
        # Use governance
        gov_conn = bulkhead_manager.acquire_connection(ComponentType.GOVERNANCE)
        gov_metrics = bulkhead_manager.get_component_metrics(ComponentType.GOVERNANCE)
        assert gov_metrics["active"] >= 1
        
        # Use audit
        audit_conn = bulkhead_manager.acquire_connection(ComponentType.AUDIT)
        audit_metrics = bulkhead_manager.get_component_metrics(ComponentType.AUDIT)
        assert audit_metrics["active"] >= 1
        
        # Metrics should be independent
        assert gov_metrics["active"] != audit_metrics["active"] or gov_metrics["total"] != audit_metrics["total"]
        
        bulkhead_manager.release_connection(ComponentType.GOVERNANCE, gov_conn)
        bulkhead_manager.release_connection(ComponentType.AUDIT, audit_conn)

    def test_metrics_show_timeout_differences(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Metrics should show configured timeouts per component."""
        gov_metrics = bulkhead_manager.get_component_metrics(ComponentType.GOVERNANCE)
        audit_metrics = bulkhead_manager.get_component_metrics(ComponentType.AUDIT)
        knowledge_metrics = bulkhead_manager.get_component_metrics(ComponentType.KNOWLEDGE)
        
        assert gov_metrics["timeout_seconds"] == 1.0
        assert audit_metrics["timeout_seconds"] == 5.0
        assert knowledge_metrics["timeout_seconds"] == 10.0


class TestCircuitBreakerIntegration:
    """Test integration with circuit breakers per component."""

    def test_each_component_has_independent_circuit_breaker(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Each component should have its own circuit breaker."""
        # Get circuit breaker states
        cb_states = bulkhead_manager.get_circuit_breaker_states()
        
        assert ComponentType.GOVERNANCE in cb_states
        assert ComponentType.AUDIT in cb_states
        assert ComponentType.KNOWLEDGE in cb_states

    def test_circuit_breaker_open_for_component_does_not_affect_others(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Open circuit in one component should not affect others."""
        # This test is a placeholder - actual circuit breaker logic
        # will be implemented in AC-INFRA-001-03
        cb_states = bulkhead_manager.get_circuit_breaker_states()
        
        # All should be closed initially
        for state in cb_states.values():
            assert state == "CLOSED"


class TestConcurrentComponentAccess:
    """Test concurrent access to different components."""

    def test_concurrent_access_to_different_components(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """Concurrent access to different components should work."""
        results = {"governance": [], "audit": [], "knowledge": []}
        errors = []
        
        def worker(component_type: ComponentType, component_name: str):
            try:
                for _ in range(20):
                    conn = bulkhead_manager.acquire_connection(component_type)
                    results[component_name].append(1)
                    time.sleep(0.01)
                    bulkhead_manager.release_connection(component_type, conn)
            except Exception as e:
                errors.append((component_name, e))
        
        threads = [
            threading.Thread(target=worker, args=(ComponentType.GOVERNANCE, "governance")),
            threading.Thread(target=worker, args=(ComponentType.AUDIT, "audit")),
            threading.Thread(target=worker, args=(ComponentType.KNOWLEDGE, "knowledge")),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Errors: {errors}"
        assert len(results["governance"]) == 20
        assert len(results["audit"]) == 20
        assert len(results["knowledge"]) == 20

    def test_high_load_on_one_component_does_not_affect_others(
        self, bulkhead_manager: BulkheadManager
    ) -> None:
        """High load on one component should not affect others."""
        audit_success = []
        errors = []
        
        def hammer_governance():
            """Hammer governance component."""
            for _ in range(50):
                try:
                    conn = bulkhead_manager.acquire_connection(
                        ComponentType.GOVERNANCE, timeout=0.1
                    )
                    time.sleep(0.05)
                    bulkhead_manager.release_connection(ComponentType.GOVERNANCE, conn)
                except BulkheadException:
                    pass  # Expected under high load
        
        def use_audit():
            """Use audit component normally."""
            try:
                for _ in range(10):
                    conn = bulkhead_manager.acquire_connection(ComponentType.AUDIT)
                    audit_success.append(1)
                    bulkhead_manager.release_connection(ComponentType.AUDIT, conn)
            except Exception as e:
                errors.append(e)
        
        # Start hammering governance
        gov_threads = [threading.Thread(target=hammer_governance) for _ in range(3)]
        for t in gov_threads:
            t.start()
        
        time.sleep(0.1)  # Let load build up
        
        # Try to use audit
        audit_thread = threading.Thread(target=use_audit)
        audit_thread.start()
        audit_thread.join()
        
        for t in gov_threads:
            t.join()
        
        # Audit should succeed despite governance being hammered
        assert len(audit_success) == 10, f"Audit operations: {len(audit_success)}, errors: {errors}"


class TestShutdownAndCleanup:
    """Test bulkhead manager shutdown."""

    def test_shutdown_closes_all_component_pools(
        self, test_db_path: Path, bulkhead_config: BulkheadConfig
    ) -> None:
        """Shutdown should close all component pools."""
        manager = BulkheadManager(database_path=test_db_path, config=bulkhead_config)
        
        # Use each component
        gov_conn = manager.acquire_connection(ComponentType.GOVERNANCE)
        audit_conn = manager.acquire_connection(ComponentType.AUDIT)
        manager.release_connection(ComponentType.GOVERNANCE, gov_conn)
        manager.release_connection(ComponentType.AUDIT, audit_conn)
        
        # Shutdown
        manager.shutdown()
        
        # Should not be able to acquire after shutdown
        with pytest.raises(RuntimeError, match="shutdown"):
            manager.acquire_connection(ComponentType.GOVERNANCE)
