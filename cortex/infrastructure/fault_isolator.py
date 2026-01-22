"""Fault isolation and error containment via bulkheads.

Implements failure domains to isolate failures and prevent cascading,
with error budgets and automatic degradation/recovery.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import logging
import threading
from collections import deque


logger = logging.getLogger(__name__)


class DomainStatus(str, Enum):
    """Health status of failure domain."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    DISABLED = "DISABLED"


@dataclass
class FailureDomain:
    """Isolated failure domain configuration.
    
    Args:
        name: Domain identifier
        error_budget_per_hour: Maximum errors allowed per hour
        timeout_seconds: Maximum operation timeout
        auto_disable_threshold: Consecutive failures before auto-disable
    """
    name: str
    error_budget_per_hour: int
    timeout_seconds: float
    auto_disable_threshold: int = 5
    
    @classmethod
    def predefined_domains(cls) -> List["FailureDomain"]:
        """Get predefined failure domains.
        
        Returns:
            List of standard domains
        """
        return [
            cls(name="governance", error_budget_per_hour=10, timeout_seconds=5.0),
            cls(name="audit", error_budget_per_hour=20, timeout_seconds=10.0),
            cls(name="knowledge", error_budget_per_hour=50, timeout_seconds=30.0),
            cls(name="orchestration", error_budget_per_hour=10, timeout_seconds=300.0),
        ]


@dataclass
class ErrorBudget:
    """Tracks error budget for domain.
    
    Args:
        max_errors_per_hour: Maximum errors allowed
        window_minutes: Time window for budget calculation
    """
    max_errors_per_hour: int
    window_minutes: int = 60
    _failures: deque = field(default_factory=lambda: deque(maxlen=1000))
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def record_failure(self) -> None:
        """Record failure in budget."""
        with self._lock:
            self._failures.append(datetime.utcnow())
    
    def record_success(self) -> None:
        """Record success (gradually restores budget)."""
        with self._lock:
            # Remove oldest failure to restore budget
            if self._failures:
                self._failures.popleft()
    
    def remaining(self) -> int:
        """Get remaining error budget.
        
        Returns:
            Number of errors remaining in budget
        """
        self._cleanup_old_failures()
        with self._lock:
            recent_failures = len(self._failures)
            return max(0, self.max_errors_per_hour - recent_failures)
    
    def is_exhausted(self) -> bool:
        """Check if error budget is exhausted.
        
        Returns:
            True if no budget remaining
        """
        return self.remaining() == 0
    
    def _cleanup_old_failures(self) -> None:
        """Remove failures outside time window."""
        cutoff = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        with self._lock:
            while self._failures and self._failures[0] < cutoff:
                self._failures.popleft()


@dataclass
class DomainHealth:
    """Tracks health of failure domain.
    
    Args:
        domain_name: Domain identifier
        error_budget: Error budget tracker
        disable_threshold: Consecutive failures before disable
    """
    domain_name: str
    error_budget: ErrorBudget
    disable_threshold: int = 5
    consecutive_failures: int = 0
    status: DomainStatus = DomainStatus.HEALTHY
    last_failure: Optional[datetime] = None
    last_success: Optional[datetime] = None
    
    def record_failure(self) -> None:
        """Record failure in domain."""
        self.consecutive_failures += 1
        self.last_failure = datetime.utcnow()
        self.error_budget.record_failure()
        
        # Update status
        if self.consecutive_failures >= self.disable_threshold:
            self.status = DomainStatus.DISABLED
            logger.warning(f"Domain {self.domain_name} disabled after {self.consecutive_failures} failures")
        elif self.error_budget.is_exhausted():
            self.status = DomainStatus.DEGRADED
            logger.warning(f"Domain {self.domain_name} degraded - error budget exhausted")
        elif self.consecutive_failures >= 3:
            self.status = DomainStatus.DEGRADED
    
    def record_success(self) -> None:
        """Record success in domain."""
        # Decay failures faster when recovering
        if self.status == DomainStatus.DISABLED:
            # Rapid recovery for disabled domains - each success removes 3 failures
            # This allows a disabled domain to recover to degraded with 2 successes
            self.consecutive_failures = max(0, self.consecutive_failures - 3)
        else:
            self.consecutive_failures = max(0, self.consecutive_failures - 1)
        
        self.last_success = datetime.utcnow()
        self.error_budget.record_success()
        
        # Gradual recovery: DISABLED -> DEGRADED -> HEALTHY
        if self.status == DomainStatus.DISABLED:
            # Allow disabled domain to recover to degraded quickly
            # After 2 successes with 10 failures, consecutive_failures = 10 - 6 = 4 (below threshold of 5)
            if self.consecutive_failures < self.disable_threshold:
                self.status = DomainStatus.DEGRADED
                logger.info(f"Domain {self.domain_name} recovered to degraded (from disabled)")
        
        # Recover to degraded if failures reduced
        if self.status == DomainStatus.DISABLED and self.consecutive_failures < self.disable_threshold:
            self.status = DomainStatus.DEGRADED
        
        # Recover to healthy if enough successes
        if self.consecutive_failures == 0:
            if self.status != DomainStatus.HEALTHY:
                logger.info(f"Domain {self.domain_name} recovered to healthy")
            self.status = DomainStatus.HEALTHY


@dataclass
class IsolationPolicy:
    """Policy for fault isolation.
    
    Args:
        enable_auto_disable: Whether to auto-disable failing domains
        error_budget_per_hour: Default error budget
        disable_threshold: Failures before disable
        health_check_interval_seconds: How often to check health
    """
    enable_auto_disable: bool = True
    error_budget_per_hour: int = 10
    disable_threshold: int = 5
    health_check_interval_seconds: int = 60
    
    @classmethod
    def default(cls) -> "IsolationPolicy":
        """Get default isolation policy.
        
        Returns:
            Default policy
        """
        return cls()


class FaultIsolator:
    """Isolates failures to prevent cascading.
    
    Args:
        domains: Failure domains to manage
        policy: Isolation policy
    """
    
    def __init__(
        self,
        domains: Optional[List[FailureDomain]] = None,
        policy: Optional[IsolationPolicy] = None
    ):
        self.domains = {d.name: d for d in (domains or FailureDomain.predefined_domains())}
        self.policy = policy or IsolationPolicy.default()
        
        # Health tracking
        self._health: Dict[str, DomainHealth] = {}
        for name, domain in self.domains.items():
            self._health[name] = DomainHealth(
                domain_name=name,
                error_budget=ErrorBudget(domain.error_budget_per_hour),
                disable_threshold=domain.auto_disable_threshold
            )
        
        # Backoff tracking for flip-flop prevention
        self._backoff: Dict[str, float] = {name: 1.0 for name in self.domains}
        self._last_state: Dict[str, DomainStatus] = {name: DomainStatus.HEALTHY for name in self.domains}
        
        # Operation-level isolation
        self._operation_health: Dict[str, Dict[str, int]] = {}
        
        # Metrics
        self._metrics = {
            "isolation_triggers": 0,
            "domain_disables": 0,
            "domain_recoveries": 0
        }
    
    def record_failure(self, domain: str, error: Exception) -> None:
        """Record failure in domain.
        
        Args:
            domain: Domain name
            error: Error that occurred
        """
        if domain not in self._health:
            logger.warning(f"Unknown domain: {domain}")
            return
        
        health = self._health[domain]
        previous_status = health.status
        
        health.record_failure()
        
        # Track status changes
        if health.status != previous_status:
            self._metrics["isolation_triggers"] += 1
            if health.status == DomainStatus.DISABLED:
                self._metrics["domain_disables"] += 1
                self._increase_backoff(domain)
        
        # Track flip-flop: if domain recovered then failed again, increase backoff
        last_state = self._last_state.get(domain, DomainStatus.HEALTHY)
        if last_state == DomainStatus.HEALTHY and health.consecutive_failures > 0:
            # Domain was healthy, now has failures - potential flip-flop
            if health.consecutive_failures == 1:  # First failure after recovery
                self._increase_backoff(domain)
        
        self._last_state[domain] = health.status
        
        logger.warning(f"Failure in domain {domain}: {error}")
    
    def record_success(self, domain: str) -> None:
        """Record success in domain.
        
        Args:
            domain: Domain name
        """
        if domain not in self._health:
            return
        
        health = self._health[domain]
        previous_status = health.status
        
        health.record_success()
        
        # Track recovery
        if previous_status != DomainStatus.HEALTHY and health.status == DomainStatus.HEALTHY:
            self._metrics["domain_recoveries"] += 1
            self._last_state[domain] = DomainStatus.HEALTHY  # Mark as recovered
            logger.info(f"Domain {domain} recovered")
        
        # Update last state
        if health.status == DomainStatus.HEALTHY:
            self._last_state[domain] = DomainStatus.HEALTHY
    
    def record_operation_failure(
        self,
        domain: str,
        operation: str,
        error: Exception
    ) -> None:
        """Record failure for specific operation type.
        
        Args:
            domain: Domain name
            operation: Operation type
            error: Error that occurred
        """
        if domain not in self._operation_health:
            self._operation_health[domain] = {}
        
        if operation not in self._operation_health[domain]:
            self._operation_health[domain][operation] = 0
        
        self._operation_health[domain][operation] += 1
        
        # Also record at domain level
        self.record_failure(domain, error)
    
    def is_domain_available(self, domain: str) -> bool:
        """Check if domain is available.
        
        Args:
            domain: Domain name
            
        Returns:
            True if domain is available
        """
        if domain not in self._health:
            return False
        
        health = self._health[domain]
        return health.status != DomainStatus.DISABLED
    
    def is_operation_available(self, domain: str, operation: str) -> bool:
        """Check if specific operation is available.
        
        Args:
            domain: Domain name
            operation: Operation type
            
        Returns:
            True if operation is available
        """
        if not self.is_domain_available(domain):
            return False
        
        # Check operation-specific health
        if domain in self._operation_health:
            failures = self._operation_health[domain].get(operation, 0)
            if failures >= 1:  # Threshold for operation-level disable (lower than domain-level)
                return False
        
        return True
    
    def is_system_degraded(self) -> bool:
        """Check if entire system is degraded.
        
        Returns:
            True if all domains are unhealthy
        """
        if not self._health:
            return False
        
        healthy_count = sum(
            1 for h in self._health.values()
            if h.status == DomainStatus.HEALTHY
        )
        
        # System degraded if <25% domains healthy
        return healthy_count < len(self._health) * 0.25
    
    def split_timeout(
        self,
        parent_timeout: float,
        num_children: int,
        domains: List[str]
    ) -> List[float]:
        """Split parent timeout among child operations.
        
        Args:
            parent_timeout: Total timeout available
            num_children: Number of child operations
            domains: Domains for each child
            
        Returns:
            List of timeouts for each child
        """
        if num_children == 0:
            return []
        
        # Equal split with domain limits
        base_timeout = parent_timeout / num_children
        
        timeouts = []
        for domain in domains:
            domain_config = self.domains.get(domain)
            if domain_config:
                # Respect domain maximum
                timeout = min(base_timeout, domain_config.timeout_seconds)
            else:
                timeout = base_timeout
            
            timeouts.append(timeout)
        
        return timeouts
    
    def get_domain_timeout(self, domain: str) -> float:
        """Get maximum timeout for domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Maximum timeout in seconds
        """
        domain_config = self.domains.get(domain)
        return domain_config.timeout_seconds if domain_config else 30.0
    
    def get_error_budget_remaining(self, domain: str) -> int:
        """Get remaining error budget for domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Remaining error count
        """
        health = self._health.get(domain)
        if not health:
            return 0
        
        return health.error_budget.remaining()
    
    def get_backoff_duration(self, domain: str) -> float:
        """Get current backoff duration for domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Backoff duration in seconds
        """
        return self._backoff.get(domain, 1.0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get fault isolation metrics.
        
        Returns:
            Metrics dictionary
        """
        return {
            **self._metrics,
            "domain_health": {
                name: {
                    "status": health.status.value,
                    "consecutive_failures": health.consecutive_failures,
                    "error_budget_remaining": health.error_budget.remaining()
                }
                for name, health in self._health.items()
            },
            "error_budgets": {
                name: health.error_budget.remaining()
                for name, health in self._health.items()
            }
        }
    
    def _increase_backoff(self, domain: str) -> None:
        """Increase backoff for domain (flip-flop prevention).
        
        Args:
            domain: Domain name
        """
        current = self._backoff.get(domain, 1.0)
        self._backoff[domain] = min(current * 2, 3600.0)  # Max 1 hour
        logger.info(f"Increased backoff for {domain} to {self._backoff[domain]}s")
