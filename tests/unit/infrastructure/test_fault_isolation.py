"""Unit tests for fault isolation and error containment."""

import pytest
from typing import Any, Dict, List
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import time

from cortex.infrastructure.fault_isolator import (
    FaultIsolator,
    FailureDomain,
    DomainHealth,
    ErrorBudget,
    DomainStatus,
    IsolationPolicy,
)


class TestFailureDomain:
    """Test failure domain definition."""
    
    def test_domain_creation(self) -> None:
        """Test creating failure domain."""
        domain = FailureDomain(
            name="governance",
            error_budget_per_hour=10,
            timeout_seconds=5.0,
            auto_disable_threshold=5
        )
        
        assert domain.name == "governance"
        assert domain.error_budget_per_hour == 10
        assert domain.timeout_seconds == 5.0
    
    def test_predefined_domains(self) -> None:
        """Test predefined domain configurations."""
        domains = FailureDomain.predefined_domains()
        
        assert "governance" in [d.name for d in domains]
        assert "audit" in [d.name for d in domains]
        assert "knowledge" in [d.name for d in domains]
        assert "orchestration" in [d.name for d in domains]


class TestErrorBudget:
    """Test error budget tracking."""
    
    def test_budget_initialization(self) -> None:
        """Test error budget starts at max."""
        budget = ErrorBudget(max_errors_per_hour=10)
        
        assert budget.remaining() == 10
        assert not budget.is_exhausted()
    
    def test_budget_consumption(self) -> None:
        """Test error budget consumed on failure."""
        budget = ErrorBudget(max_errors_per_hour=10)
        
        budget.record_failure()
        assert budget.remaining() == 9
        
        budget.record_failure()
        assert budget.remaining() == 8
    
    def test_budget_exhaustion(self) -> None:
        """Test error budget exhaustion."""
        budget = ErrorBudget(max_errors_per_hour=3)
        
        budget.record_failure()
        budget.record_failure()
        budget.record_failure()
        
        assert budget.is_exhausted()
    
    @pytest.mark.timeout(5)  # Short timeout since we're testing the mechanism
    def test_budget_reset_after_window(self) -> None:
        """Test error budget resets after time window.
        
        Note: This test uses a very short window (1 second) instead of 1 minute
        to avoid long sleeps that would exceed pytest timeout. The mechanism is
        the same - testing that failures are cleaned up after the window expires.
        """
        budget = ErrorBudget(max_errors_per_hour=10, window_minutes=1/60)  # 1 second window
        
        budget.record_failure()
        assert budget.remaining() == 9
        
        # Wait for short window to expire (1 second + buffer)
        time.sleep(1.1)
        
        # Budget should reset after window expires
        assert budget.remaining() == 10
    
    def test_success_restores_budget_gradually(self) -> None:
        """Test successful operations restore budget gradually."""
        budget = ErrorBudget(max_errors_per_hour=10)
        
        # Consume budget
        budget.record_failure()
        budget.record_failure()
        assert budget.remaining() == 8
        
        # Successes restore
        budget.record_success()
        assert budget.remaining() == 9
        
        budget.record_success()
        assert budget.remaining() == 10


class TestDomainHealth:
    """Test domain health tracking."""
    
    def test_healthy_domain(self) -> None:
        """Test healthy domain status."""
        health = DomainHealth(domain_name="test", error_budget=ErrorBudget(10))
        
        health.record_success()
        health.record_success()
        
        assert health.status == DomainStatus.HEALTHY
        assert health.consecutive_failures == 0
    
    def test_degraded_domain(self) -> None:
        """Test domain becomes degraded after failures."""
        health = DomainHealth(domain_name="test", error_budget=ErrorBudget(10))
        
        health.record_failure()
        health.record_failure()
        health.record_failure()
        
        assert health.status == DomainStatus.DEGRADED
        assert health.consecutive_failures == 3
    
    def test_disabled_domain_after_threshold(self) -> None:
        """Test domain disabled after threshold failures."""
        health = DomainHealth(
            domain_name="test",
            error_budget=ErrorBudget(10),
            disable_threshold=5
        )
        
        for _ in range(5):
            health.record_failure()
        
        assert health.status == DomainStatus.DISABLED
    
    def test_domain_recovery(self) -> None:
        """Test domain recovers after successes."""
        health = DomainHealth(domain_name="test", error_budget=ErrorBudget(10))
        
        # Degrade
        health.record_failure()
        health.record_failure()
        health.record_failure()
        assert health.status == DomainStatus.DEGRADED
        
        # Recover
        health.record_success()
        health.record_success()
        health.record_success()
        
        assert health.status == DomainStatus.HEALTHY
        assert health.consecutive_failures == 0


class TestFaultIsolator:
    """Test fault isolation orchestration."""
    
    @pytest.fixture
    def isolator(self) -> FaultIsolator:
        """Create fault isolator with default domains."""
        return FaultIsolator()
    
    def test_domain_independence(self, isolator: FaultIsolator) -> None:
        """Test failure in one domain doesn't affect others."""
        # Fail governance domain
        isolator.record_failure("governance", Exception("governance error"))
        
        # Other domains should remain healthy
        assert isolator.is_domain_available("audit")
        assert isolator.is_domain_available("knowledge")
    
    def test_domain_automatically_disabled(self, isolator: FaultIsolator) -> None:
        """Test domain disabled after error budget exhausted."""
        # Exhaust error budget
        for _ in range(10):
            isolator.record_failure("governance", Exception("error"))
        
        # Domain should be disabled
        assert not isolator.is_domain_available("governance")
    
    def test_domain_re_enabled_after_health_check(self, isolator: FaultIsolator) -> None:
        """Test domain re-enabled after health check passes."""
        # Disable domain
        for _ in range(10):
            isolator.record_failure("audit", Exception("error"))
        
        assert not isolator.is_domain_available("audit")
        
        # Simulate successful health check
        isolator.record_success("audit")
        isolator.record_success("audit")
        
        # Should re-enable gradually
        assert isolator.is_domain_available("audit")
    
    def test_timeout_propagation(self, isolator: FaultIsolator) -> None:
        """Test parent timeout split among child operations."""
        parent_timeout = 10.0
        
        child_timeouts = isolator.split_timeout(
            parent_timeout,
            num_children=3,
            domains=["governance", "audit", "knowledge"]
        )
        
        # Each child gets portion of parent timeout
        assert len(child_timeouts) == 3
        assert sum(child_timeouts) <= parent_timeout
        assert all(t > 0 for t in child_timeouts)
    
    def test_timeout_respects_domain_limits(self, isolator: FaultIsolator) -> None:
        """Test timeout doesn't exceed domain maximum."""
        parent_timeout = 100.0
        
        child_timeouts = isolator.split_timeout(
            parent_timeout,
            num_children=2,
            domains=["governance", "audit"]
        )
        
        # Each domain has max timeout limit
        gov_timeout = isolator.get_domain_timeout("governance")
        assert child_timeouts[0] <= gov_timeout
    
    def test_cascading_failure_prevented(self, isolator: FaultIsolator) -> None:
        """Test single component failure doesn't cascade."""
        # Audit fails
        for _ in range(10):
            isolator.record_failure("audit", Exception("audit down"))
        
        # Audit disabled but others still work
        assert not isolator.is_domain_available("audit")
        assert isolator.is_domain_available("governance")
        assert isolator.is_domain_available("orchestration")
    
    def test_all_domains_failing_system_degradation(self, isolator: FaultIsolator) -> None:
        """Test system-wide degradation when all domains fail."""
        # Fail all domains
        for domain in ["governance", "audit", "knowledge", "orchestration"]:
            for _ in range(10):
                isolator.record_failure(domain, Exception("error"))
        
        # System should be in degraded mode
        assert isolator.is_system_degraded()
    
    def test_domain_flip_flop_backoff(self, isolator: FaultIsolator) -> None:
        """Test backoff increases on repeated failures."""
        domain = "governance"
        
        # First failure
        isolator.record_failure(domain, Exception("error"))
        backoff1 = isolator.get_backoff_duration(domain)
        
        # Recover
        isolator.record_success(domain)
        
        # Fail again
        isolator.record_failure(domain, Exception("error"))
        backoff2 = isolator.get_backoff_duration(domain)
        
        # Backoff should increase
        assert backoff2 > backoff1
    
    def test_partial_domain_failure_isolation(self, isolator: FaultIsolator) -> None:
        """Test isolating failure to specific operations."""
        # Fail specific operation type
        isolator.record_operation_failure(
            domain="governance",
            operation="phase_validation",
            error=Exception("validation error")
        )
        
        # Domain still available for other operations
        assert isolator.is_domain_available("governance")
        
        # But specific operation may be disabled
        assert not isolator.is_operation_available("governance", "phase_validation")
    
    def test_error_budget_gradual_restoration(self, isolator: FaultIsolator) -> None:
        """Test error budget gradually restored after recovery."""
        domain = "governance"
        
        # Consume budget
        for _ in range(5):
            isolator.record_failure(domain, Exception("error"))
        
        budget_before = isolator.get_error_budget_remaining(domain)
        
        # Successes restore budget
        for _ in range(3):
            isolator.record_success(domain)
        
        budget_after = isolator.get_error_budget_remaining(domain)
        
        assert budget_after > budget_before
    
    def test_isolation_metrics(self, isolator: FaultIsolator) -> None:
        """Test fault isolation metrics collected."""
        isolator.record_failure("governance", Exception("error"))
        isolator.record_success("audit")
        
        metrics = isolator.get_metrics()
        
        assert "domain_health" in metrics
        assert "error_budgets" in metrics
        assert "isolation_triggers" in metrics


class TestIsolationPolicy:
    """Test isolation policy configuration."""
    
    def test_default_policy(self) -> None:
        """Test default isolation policy."""
        policy = IsolationPolicy.default()
        
        assert policy.enable_auto_disable is True
        assert policy.error_budget_per_hour > 0
        assert policy.health_check_interval_seconds > 0
    
    def test_custom_policy(self) -> None:
        """Test custom isolation policy."""
        policy = IsolationPolicy(
            enable_auto_disable=False,
            error_budget_per_hour=50,
            disable_threshold=10
        )
        
        assert policy.enable_auto_disable is False
        assert policy.error_budget_per_hour == 50


class TestIsolationIntegration:
    """Integration tests for fault isolation scenarios."""
    
    def test_end_to_end_isolation(self) -> None:
        """Test complete fault isolation flow."""
        isolator = FaultIsolator()
        
        # Governance working fine
        assert isolator.is_domain_available("governance")
        isolator.record_success("governance")
        
        # Audit starts failing
        for _ in range(10):
            isolator.record_failure("audit", Exception("audit error"))
        
        # Audit disabled, governance still works
        assert not isolator.is_domain_available("audit")
        assert isolator.is_domain_available("governance")
        
        # Audit recovers
        for _ in range(5):
            isolator.record_success("audit")
        
        # Audit re-enabled
        assert isolator.is_domain_available("audit")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
