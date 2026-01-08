"""
Circuit Breaker Middleware - CORTEX 6.0

Implements circuit breaker pattern for resilience:
- Automatic failure detection and recovery
- State transitions: CLOSED → OPEN → HALF_OPEN → CLOSED
- Prevents cascading failures
- Configurable thresholds and timeouts

Author: CORTEX Autonomous Executor
Feature: feat05-resilience Phase 2
Correlation ID: FEAT05-P2-T2.1
"""

import time
import threading
import functools
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any, Optional, Dict

from src.orchestrators.audit_logger import EnterpriseAuditLogger, AuditLevel, AuditCategory


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 60
    half_open_max_calls: int = 1
    
    def validate(self):
        """Validate configuration."""
        if self.failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if self.success_threshold <= 0:
            raise ValueError("success_threshold must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


class CircuitBreakerError(Exception):
    """Base exception for circuit breaker errors."""
    
    def __init__(self, message: str, service: str, state: CircuitBreakerState):
        super().__init__(message)
        self.service = service
        self.state = state


class CircuitBreakerOpen(CircuitBreakerError):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, service: str, retry_after_seconds: float):
        message = f"Circuit breaker OPEN for {service}. Retry after {retry_after_seconds}s"
        super().__init__(message, service, CircuitBreakerState.OPEN)
        self.retry_after_seconds = retry_after_seconds


class CircuitBreaker:
    """
    Circuit breaker implementation for resilience.
    
    Prevents cascading failures by monitoring operation failures and
    temporarily blocking calls when failure threshold is exceeded.
    
    States:
    - CLOSED: Normal operation, calls allowed
    - OPEN: Failure threshold exceeded, calls blocked
    - HALF_OPEN: Testing recovery, limited calls allowed
    
    Usage:
        breaker = CircuitBreaker("external_api")
        
        # Direct call
        result = breaker.call(api_function, arg1, arg2)
        
        # Decorator
        @breaker.protect
        def my_function():
            return "result"
    """
    
    def __init__(
        self,
        service_name: str,
        config: Optional[CircuitBreakerConfig] = None,
        audit_logger: Optional[EnterpriseAuditLogger] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            service_name: Name of the service being protected
            config: Circuit breaker configuration
            audit_logger: Optional audit logger
        """
        self.service_name = service_name
        self.config = config or CircuitBreakerConfig()
        self.config.validate()
        
        self.audit_logger = audit_logger or EnterpriseAuditLogger()
        
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._opened_at: Optional[float] = None
        self._lock = threading.RLock()
        
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.MIDDLEWARE,
            component="circuit_breaker",
            operation="initialize",
            message=f"Circuit breaker initialized for {service_name}",
            correlation_id="FEAT05-P2-T2.1",
            context={
                "service": service_name,
                "config": {
                    "failure_threshold": self.config.failure_threshold,
                    "success_threshold": self.config.success_threshold,
                    "timeout_seconds": self.config.timeout_seconds
                }
            }
        )
        
    @property
    def state(self) -> CircuitBreakerState:
        """Get current state."""
        with self._lock:
            return self._state
            
    @property
    def failure_count(self) -> int:
        """Get failure count."""
        with self._lock:
            return self._failure_count
            
    @property
    def success_count(self) -> int:
        """Get success count."""
        with self._lock:
            return self._success_count
            
    def can_attempt(self) -> bool:
        """
        Check if a call attempt is allowed.
        
        Returns:
            True if call is allowed, False otherwise
        """
        with self._lock:
            if self._state == CircuitBreakerState.CLOSED:
                return True
                
            if self._state == CircuitBreakerState.OPEN:
                # Check if timeout has passed
                if self._opened_at is not None:
                    elapsed = time.time() - self._opened_at
                    if elapsed >= self.config.timeout_seconds:
                        # Transition to HALF_OPEN
                        self._transition_to_half_open()
                        return True
                return False
                
            # HALF_OPEN state - allow limited calls
            return True
            
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpen: If circuit breaker is open
            Exception: Any exception raised by the function
        """
        if not self.can_attempt():
            retry_after = self.config.timeout_seconds
            if self._opened_at is not None:
                retry_after = self.config.timeout_seconds - (time.time() - self._opened_at)
                
            raise CircuitBreakerOpen(self.service_name, max(0, retry_after))
            
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
            
        except Exception as e:
            self.record_failure()
            raise
            
    def protect(self, func: Callable) -> Callable:
        """
        Decorator to protect a function with circuit breaker.
        
        Args:
            func: Function to protect
            
        Returns:
            Wrapped function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
        
    def record_success(self):
        """Record a successful operation."""
        with self._lock:
            self._success_count += 1
            
            if self._state == CircuitBreakerState.HALF_OPEN:
                if self._success_count >= self.config.success_threshold:
                    self._transition_to_closed()
                    
    def record_failure(self):
        """Record a failed operation."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitBreakerState.CLOSED:
                if self._failure_count >= self.config.failure_threshold:
                    self._transition_to_open()
                    
            elif self._state == CircuitBreakerState.HALF_OPEN:
                # Any failure in HALF_OPEN goes back to OPEN
                self._transition_to_open()
                
    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._opened_at = None
        
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.MIDDLEWARE,
            component="circuit_breaker",
            operation="state_transition",
            message=f"Circuit breaker CLOSED for {self.service_name}",
            correlation_id="FEAT05-P2-T2.1",
            context={"service": self.service_name, "new_state": "CLOSED"}
        )
        
    def _transition_to_open(self):
        """Transition to OPEN state."""
        self._state = CircuitBreakerState.OPEN
        self._opened_at = time.time()
        
        self.audit_logger.log(
            level=AuditLevel.WARNING,
            category=AuditCategory.MIDDLEWARE,
            component="circuit_breaker",
            operation="state_transition",
            message=f"Circuit breaker OPEN for {self.service_name}",
            correlation_id="FEAT05-P2-T2.1",
            context={
                "service": self.service_name,
                "new_state": "OPEN",
                "failure_count": self._failure_count,
                "timeout_seconds": self.config.timeout_seconds
            }
        )
        
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        self._state = CircuitBreakerState.HALF_OPEN
        self._failure_count = 0
        self._success_count = 0
        
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.MIDDLEWARE,
            component="circuit_breaker",
            operation="state_transition",
            message=f"Circuit breaker HALF_OPEN for {self.service_name}",
            correlation_id="FEAT05-P2-T2.1",
            context={"service": self.service_name, "new_state": "HALF_OPEN"}
        )
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get circuit breaker statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            total_calls = self._success_count + self._failure_count
            failure_rate = self._failure_count / total_calls if total_calls > 0 else 0.0
            
            return {
                "service": self.service_name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "failure_rate": failure_rate,
                "opened_at": self._opened_at,
                "last_failure_time": self._last_failure_time
            }
            
    def reset(self):
        """Reset circuit breaker to initial state."""
        with self._lock:
            self._state = CircuitBreakerState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._opened_at = None
            self._last_failure_time = None
            
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.MIDDLEWARE,
                component="circuit_breaker",
                operation="reset",
                message=f"Circuit breaker reset for {self.service_name}",
                correlation_id="FEAT05-P2-T2.1",
                context={"service": self.service_name}
            )
