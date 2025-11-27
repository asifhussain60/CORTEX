"""
CORTEX 3.0 Circuit Breaker
===========================

Circuit breaker pattern implementation for preventing cascading failures
and providing graceful degradation in production systems.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import statistics


logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5          # Failures before opening
    timeout_duration: float = 60.0     # Seconds to stay open
    recovery_timeout: float = 30.0     # Seconds in half-open before closing
    success_threshold: int = 3          # Successes needed to close from half-open
    sliding_window_size: int = 100      # Size of sliding window for statistics
    minimum_throughput: int = 10        # Minimum requests before considering opening
    
    # Advanced settings
    slow_request_threshold: float = 5.0  # Seconds - requests slower than this count as failures
    error_percentage_threshold: float = 50.0  # Percentage of errors that trigger opening
    enable_half_open_max_calls: bool = True   # Limit calls in half-open state
    max_half_open_calls: int = 5        # Maximum calls allowed in half-open


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    slow_requests: int = 0
    rejected_requests: int = 0
    state_changes: int = 0
    avg_response_time: float = 0.0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100.0


@dataclass
class CallResult:
    """Result of a circuit breaker protected call."""
    success: bool
    result: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    was_circuit_open: bool = False


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""
    def __init__(self, message: str, state: CircuitBreakerState):
        super().__init__(message)
        self.state = state


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting against cascading failures
    with configurable thresholds and recovery mechanisms.
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        on_state_change: Optional[Callable] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.on_state_change = on_state_change
        
        # State management
        self._state = CircuitBreakerState.CLOSED
        self._state_changed_time = time.time()
        self._lock = threading.RLock()
        
        # Metrics and tracking
        self.metrics = CircuitBreakerMetrics()
        self._call_history: List[Dict[str, Any]] = []
        self._response_times: List[float] = []
        
        # Half-open state management
        self._half_open_calls = 0
        self._half_open_successes = 0
        self._half_open_start_time = None
        
        # Callbacks
        self._failure_callbacks: List[Callable] = []
        self._recovery_callbacks: List[Callable] = []
    
    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit breaker is closed (normal operation)."""
        return self._state == CircuitBreakerState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit breaker is open (blocking requests)."""
        return self._state == CircuitBreakerState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit breaker is half-open (testing recovery)."""
        return self._state == CircuitBreakerState.HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> CallResult:
        """
        Execute a function protected by the circuit breaker.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            CallResult with execution details
            
        Raises:
            CircuitBreakerError: If circuit breaker is open
        """
        with self._lock:
            # Check if we should allow the call
            if not self._should_allow_request():
                self.metrics.rejected_requests += 1
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is {self._state.value}",
                    self._state
                )
            
            # If half-open, track the call
            if self._state == CircuitBreakerState.HALF_OPEN:
                self._half_open_calls += 1
        
        # Execute the protected function
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record successful call
            self._record_success(execution_time)
            
            return CallResult(
                success=True,
                result=result,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failed call
            self._record_failure(execution_time, e)
            
            return CallResult(
                success=False,
                error=e,
                execution_time=execution_time
            )
    
    def call_async(self, coro_func: Callable, *args, **kwargs):
        """
        Async version of call method.
        Note: This is a simplified implementation. In production,
        you'd want proper async/await support.
        """
        # This would need proper async implementation
        return self.call(coro_func, *args, **kwargs)
    
    def force_open(self) -> None:
        """Manually force circuit breaker to open state."""
        with self._lock:
            self._change_state(CircuitBreakerState.OPEN)
        logger.warning(f"Circuit breaker '{self.name}' manually forced open")
    
    def force_close(self) -> None:
        """Manually force circuit breaker to close state."""
        with self._lock:
            self._reset_half_open_state()
            self._change_state(CircuitBreakerState.CLOSED)
        logger.info(f"Circuit breaker '{self.name}' manually forced closed")
    
    def force_half_open(self) -> None:
        """Manually force circuit breaker to half-open state."""
        with self._lock:
            self._reset_half_open_state()
            self._change_state(CircuitBreakerState.HALF_OPEN)
        logger.info(f"Circuit breaker '{self.name}' manually set to half-open")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive circuit breaker metrics."""
        with self._lock:
            return {
                'name': self.name,
                'state': self._state.value,
                'state_duration': time.time() - self._state_changed_time,
                'metrics': {
                    'total_requests': self.metrics.total_requests,
                    'successful_requests': self.metrics.successful_requests,
                    'failed_requests': self.metrics.failed_requests,
                    'slow_requests': self.metrics.slow_requests,
                    'rejected_requests': self.metrics.rejected_requests,
                    'failure_rate': self.metrics.failure_rate,
                    'success_rate': self.metrics.success_rate,
                    'avg_response_time': self.metrics.avg_response_time,
                    'state_changes': self.metrics.state_changes
                },
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'timeout_duration': self.config.timeout_duration,
                    'error_percentage_threshold': self.config.error_percentage_threshold,
                    'slow_request_threshold': self.config.slow_request_threshold
                },
                'half_open_state': {
                    'calls_made': self._half_open_calls,
                    'successes': self._half_open_successes,
                    'max_calls': self.config.max_half_open_calls
                } if self._state == CircuitBreakerState.HALF_OPEN else None
            }
    
    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        with self._lock:
            self._change_state(CircuitBreakerState.CLOSED)
            self.metrics = CircuitBreakerMetrics()
            self._call_history.clear()
            self._response_times.clear()
            self._reset_half_open_state()
        
        logger.info(f"Circuit breaker '{self.name}' reset")
    
    def add_failure_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for when circuit breaker opens."""
        self._failure_callbacks.append(callback)
    
    def add_recovery_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for when circuit breaker closes after being open."""
        self._recovery_callbacks.append(callback)
    
    def _should_allow_request(self) -> bool:
        """Determine if a request should be allowed through."""
        current_time = time.time()
        
        if self._state == CircuitBreakerState.CLOSED:
            return True
        
        elif self._state == CircuitBreakerState.OPEN:
            # Check if timeout period has elapsed
            if current_time - self._state_changed_time >= self.config.timeout_duration:
                self._change_state(CircuitBreakerState.HALF_OPEN)
                return True
            return False
        
        elif self._state == CircuitBreakerState.HALF_OPEN:
            # Limit calls in half-open state if configured
            if (self.config.enable_half_open_max_calls and 
                self._half_open_calls >= self.config.max_half_open_calls):
                return False
            
            # Check if recovery timeout has elapsed
            if (self._half_open_start_time and 
                current_time - self._half_open_start_time >= self.config.recovery_timeout):
                # If we've had some successes, close; otherwise, open
                if self._half_open_successes > 0:
                    self._change_state(CircuitBreakerState.CLOSED)
                else:
                    self._change_state(CircuitBreakerState.OPEN)
                return self._should_allow_request()  # Re-evaluate
            
            return True
        
        return False
    
    def _record_success(self, execution_time: float) -> None:
        """Record a successful call."""
        with self._lock:
            self.metrics.total_requests += 1
            self.metrics.last_success_time = time.time()
            
            # Check if this is a slow request
            if execution_time > self.config.slow_request_threshold:
                self.metrics.slow_requests += 1
                # Treat slow requests as partial failures
                self._update_call_history(False, execution_time)
            else:
                self.metrics.successful_requests += 1
                self._update_call_history(True, execution_time)
            
            # Update response time tracking
            self._response_times.append(execution_time)
            if len(self._response_times) > self.config.sliding_window_size:
                self._response_times = self._response_times[-self.config.sliding_window_size:]
            
            self.metrics.avg_response_time = statistics.mean(self._response_times)
            
            # Handle half-open state transitions
            if self._state == CircuitBreakerState.HALF_OPEN:
                if execution_time <= self.config.slow_request_threshold:
                    self._half_open_successes += 1
                    
                    # Check if we should close the circuit
                    if self._half_open_successes >= self.config.success_threshold:
                        self._change_state(CircuitBreakerState.CLOSED)
    
    def _record_failure(self, execution_time: float, error: Exception) -> None:
        """Record a failed call."""
        with self._lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.metrics.last_failure_time = time.time()
            
            self._update_call_history(False, execution_time)
            
            # Update response time tracking
            self._response_times.append(execution_time)
            if len(self._response_times) > self.config.sliding_window_size:
                self._response_times = self._response_times[-self.config.sliding_window_size:]
            
            # Handle state transitions
            if self._state == CircuitBreakerState.CLOSED:
                self._check_should_open()
            elif self._state == CircuitBreakerState.HALF_OPEN:
                # Any failure in half-open should open the circuit
                self._change_state(CircuitBreakerState.OPEN)
    
    def _update_call_history(self, success: bool, execution_time: float) -> None:
        """Update sliding window of call history."""
        call_record = {
            'timestamp': time.time(),
            'success': success,
            'execution_time': execution_time
        }
        
        self._call_history.append(call_record)
        
        # Maintain sliding window
        if len(self._call_history) > self.config.sliding_window_size:
            self._call_history = self._call_history[-self.config.sliding_window_size:]
    
    def _check_should_open(self) -> None:
        """Check if circuit should be opened based on failure criteria."""
        # Need minimum throughput before considering opening
        if len(self._call_history) < self.config.minimum_throughput:
            return
        
        # Check failure threshold
        recent_failures = sum(1 for call in self._call_history[-self.config.failure_threshold:] 
                             if not call['success'])
        
        if recent_failures >= self.config.failure_threshold:
            self._change_state(CircuitBreakerState.OPEN)
            return
        
        # Check error percentage threshold
        recent_calls = self._call_history[-self.config.sliding_window_size:]
        if len(recent_calls) >= self.config.minimum_throughput:
            failed_calls = sum(1 for call in recent_calls if not call['success'])
            error_percentage = (failed_calls / len(recent_calls)) * 100.0
            
            if error_percentage >= self.config.error_percentage_threshold:
                self._change_state(CircuitBreakerState.OPEN)
    
    def _change_state(self, new_state: CircuitBreakerState) -> None:
        """Change circuit breaker state and handle transitions."""
        old_state = self._state
        
        if old_state == new_state:
            return
        
        self._state = new_state
        self._state_changed_time = time.time()
        self.metrics.state_changes += 1
        
        # Handle state-specific setup
        if new_state == CircuitBreakerState.HALF_OPEN:
            self._reset_half_open_state()
            self._half_open_start_time = time.time()
        
        # Execute callbacks
        if old_state == CircuitBreakerState.CLOSED and new_state == CircuitBreakerState.OPEN:
            # Circuit opened (failure)
            for callback in self._failure_callbacks:
                try:
                    callback(self.name)
                except Exception as e:
                    logger.warning(f"Failure callback error: {e}")
        
        elif old_state == CircuitBreakerState.OPEN and new_state == CircuitBreakerState.CLOSED:
            # Circuit recovered
            for callback in self._recovery_callbacks:
                try:
                    callback(self.name)
                except Exception as e:
                    logger.warning(f"Recovery callback error: {e}")
        
        # Notify external state change handler
        if self.on_state_change:
            try:
                self.on_state_change(self.name, old_state, new_state)
            except Exception as e:
                logger.warning(f"State change callback error: {e}")
        
        logger.info(f"Circuit breaker '{self.name}' changed state: {old_state.value} -> {new_state.value}")
    
    def _reset_half_open_state(self) -> None:
        """Reset half-open state variables."""
        self._half_open_calls = 0
        self._half_open_successes = 0
        self._half_open_start_time = None