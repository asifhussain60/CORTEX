"""
BRT-029: Error Recovery & Compensation

Implements error recovery mechanisms and compensation logic for
distributed operations.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from threading import Lock
import time


class ErrorType(Enum):
    """Types of errors."""
    TRANSIENT = "transient"  # Can be retried
    PERMANENT = "permanent"  # Should not retry
    TIMEOUT = "timeout"
    NETWORK = "network"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Error recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    TIMEOUT = "timeout"
    ROLLBACK = "rollback"
    COMPENSATE = "compensate"


@dataclass
class ErrorContext:
    """Context for an error."""
    error_type: ErrorType
    message: str
    code: str
    source: str
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)
    retry_count: int = 0
    last_retry_ms: Optional[float] = None
    recovery_attempt: Optional[RecoveryStrategy] = None


class ErrorClassifier:
    """Classifies errors and determines handling strategy."""
    
    def __init__(self):
        self._error_patterns: Dict[str, ErrorType] = {}
        self._lock = Lock()
    
    def register_pattern(self, pattern: str, error_type: ErrorType) -> bool:
        """Register an error pattern."""
        with self._lock:
            if pattern in self._error_patterns:
                return False
            
            self._error_patterns[pattern] = error_type
            return True
    
    def classify_error(self, error_message: str) -> ErrorType:
        """Classify error based on message."""
        with self._lock:
            for pattern, error_type in self._error_patterns.items():
                if pattern.lower() in error_message.lower():
                    return error_type
            
            # Default classification
            if "timeout" in error_message.lower():
                return ErrorType.TIMEOUT
            elif "connection" in error_message.lower():
                return ErrorType.NETWORK
            
            return ErrorType.UNKNOWN
    
    def is_retriable(self, error_type: ErrorType) -> bool:
        """Check if error is retriable."""
        retriable_types = {
            ErrorType.TRANSIENT,
            ErrorType.TIMEOUT,
            ErrorType.NETWORK
        }
        return error_type in retriable_types


class CompensationAction(ABC):
    """Base class for compensation actions."""
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute compensation action."""
        pass
    
    @abstractmethod
    def can_compensate(self, context: Dict[str, Any]) -> bool:
        """Check if compensation is possible."""
        pass


class RollbackAction(CompensationAction):
    """Rollback a failed operation."""
    
    def __init__(self, operation_id: str, rollback_fn: Callable[[Dict[str, Any]], bool]):
        self.operation_id = operation_id
        self.rollback_fn = rollback_fn
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute rollback."""
        try:
            return self.rollback_fn(context)
        except Exception:
            return False
    
    def can_compensate(self, context: Dict[str, Any]) -> bool:
        """Check if rollback is possible."""
        return context.get("operation_id") == self.operation_id


class ReverseAction(CompensationAction):
    """Reverse an operation."""
    
    def __init__(self, reverse_fn: Callable[[Dict[str, Any]], bool]):
        self.reverse_fn = reverse_fn
    
    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute reverse operation."""
        try:
            return self.reverse_fn(context)
        except Exception:
            return False
    
    def can_compensate(self, context: Dict[str, Any]) -> bool:
        """Check if reverse is possible."""
        return "data" in context


class CompensationManager:
    """Manages compensation transactions."""
    
    def __init__(self):
        self._actions: List[CompensationAction] = []
        self._executed: List[CompensationAction] = []
        self._lock = Lock()
    
    def register_action(self, action: CompensationAction) -> bool:
        """Register an action for potential compensation."""
        with self._lock:
            self._actions.append(action)
            return True
    
    def execute_compensation(self, context: Dict[str, Any]) -> bool:
        """Execute compensation (undo previous actions)."""
        with self._lock:
            # Execute in reverse order (LIFO)
            for action in reversed(self._executed):
                if action.can_compensate(context):
                    if not action.execute(context):
                        return False
            
            self._executed.clear()
            return True
    
    def mark_success(self, action: CompensationAction) -> bool:
        """Mark action as successfully executed."""
        with self._lock:
            self._executed.append(action)
            return True
    
    def get_pending_compensation(self) -> int:
        """Get number of actions pending compensation."""
        with self._lock:
            return len(self._executed)


class FallbackHandler:
    """Handles fallback operations."""
    
    def __init__(self):
        self._fallbacks: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._lock = Lock()
    
    def register_fallback(
        self,
        operation_id: str,
        fallback_fn: Callable[[Dict[str, Any]], Any]
    ) -> bool:
        """Register a fallback for an operation."""
        with self._lock:
            if operation_id in self._fallbacks:
                return False
            
            self._fallbacks[operation_id] = fallback_fn
            return True
    
    def execute_fallback(
        self,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Execute fallback for an operation."""
        with self._lock:
            fallback = self._fallbacks.get(operation_id)
            if not fallback:
                return None
            
            try:
                return fallback(context)
            except Exception:
                return None


class ErrorRecoveryManager:
    """Main error recovery manager."""
    
    def __init__(
        self,
        classifier: ErrorClassifier,
        compensation_mgr: CompensationManager,
        fallback_handler: FallbackHandler
    ):
        self.classifier = classifier
        self.compensation_mgr = compensation_mgr
        self.fallback_handler = fallback_handler
        self._error_history: List[ErrorContext] = []
        self._lock = Lock()
    
    def handle_error(
        self,
        error: Exception,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Optional[Any]:
        """Handle an error with recovery strategy."""
        error_type = self.classifier.classify_error(str(error))
        
        error_context = ErrorContext(
            error_type=error_type,
            message=str(error),
            code=type(error).__name__,
            source=operation_id
        )
        
        with self._lock:
            self._error_history.append(error_context)
        
        # Try fallback first
        fallback_result = self.fallback_handler.execute_fallback(operation_id, context)
        if fallback_result is not None:
            return fallback_result
        
        # If not retriable, compensate
        if not self.classifier.is_retriable(error_type):
            self.compensation_mgr.execute_compensation(context)
            return None
        
        # Retriable error - caller should retry
        return None
    
    def record_error(self, error_context: ErrorContext) -> bool:
        """Record an error."""
        with self._lock:
            self._error_history.append(error_context)
            return True
    
    def get_error_history(self, operation_id: Optional[str] = None) -> List[ErrorContext]:
        """Get error history."""
        with self._lock:
            if operation_id:
                return [e for e in self._error_history if e.source == operation_id]
            return self._error_history.copy()


class DeadLetterQueue:
    """Queue for handling failed operations."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queue: List[Dict[str, Any]] = []
        self._lock = Lock()
    
    def enqueue(
        self,
        operation_id: str,
        data: Dict[str, Any],
        error: ErrorContext
    ) -> bool:
        """Enqueue a failed operation."""
        with self._lock:
            if len(self._queue) >= self.max_size:
                # Remove oldest
                self._queue.pop(0)
            
            self._queue.append({
                "operation_id": operation_id,
                "data": data,
                "error": error,
                "timestamp_ms": time.time() * 1000
            })
            return True
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Dequeue a failed operation."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue.pop(0)
    
    def peek(self) -> Optional[Dict[str, Any]]:
        """Peek at next item without removing."""
        with self._lock:
            if not self._queue:
                return None
            return self._queue[0]
    
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._queue)


class CircuitBreakerWithRecovery:
    """Circuit breaker with recovery capability."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_ms: int = 60000
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_ms = recovery_timeout_ms
        self._failure_count = 0
        self._state = "closed"  # closed, open, half-open
        self._opened_at_ms = 0
        self._lock = Lock()
    
    def record_success(self) -> None:
        """Record successful operation."""
        with self._lock:
            if self._state == "half-open":
                self._state = "closed"
                self._failure_count = 0
            elif self._state == "closed":
                self._failure_count = max(0, self._failure_count - 1)
    
    def record_failure(self) -> None:
        """Record failed operation."""
        with self._lock:
            self._failure_count += 1
            
            if self._failure_count >= self.failure_threshold:
                self._state = "open"
                self._opened_at_ms = time.time() * 1000
    
    def should_attempt_operation(self) -> bool:
        """Check if operation should be attempted."""
        with self._lock:
            if self._state == "closed":
                return True
            
            if self._state == "open":
                now = time.time() * 1000
                if now - self._opened_at_ms > self.recovery_timeout_ms:
                    self._state = "half-open"
                    return True
                return False
            
            # half-open
            return True
    
    def get_state(self) -> str:
        """Get circuit breaker state."""
        with self._lock:
            return self._state


# ============================================================================
# TEST SUITE
# ============================================================================

class TestErrorClassifier:
    """Test ErrorClassifier functionality."""
    
    def test_register_pattern(self):
        """Test registering error pattern."""
        classifier = ErrorClassifier()
        assert classifier.register_pattern("Connection refused", ErrorType.NETWORK)
    
    def test_classify_error_by_pattern(self):
        """Test classifying error by pattern."""
        classifier = ErrorClassifier()
        classifier.register_pattern("Connection refused", ErrorType.NETWORK)
        
        error_type = classifier.classify_error("Connection refused: Unable to connect")
        assert error_type == ErrorType.NETWORK
    
    def test_classify_timeout_error(self):
        """Test classifying timeout error."""
        classifier = ErrorClassifier()
        error_type = classifier.classify_error("Operation TIMEOUT after 5s")
        assert error_type == ErrorType.TIMEOUT
    
    def test_is_retriable(self):
        """Test checking if error is retriable."""
        classifier = ErrorClassifier()
        
        assert classifier.is_retriable(ErrorType.TRANSIENT)
        assert classifier.is_retriable(ErrorType.TIMEOUT)
        assert not classifier.is_retriable(ErrorType.PERMANENT)


class TestCompensationManager:
    """Test CompensationManager functionality."""
    
    def test_register_action(self):
        """Test registering compensation action."""
        manager = CompensationManager()
        action = RollbackAction("op1", lambda ctx: True)
        
        assert manager.register_action(action)
    
    def test_mark_success(self):
        """Test marking action as successful."""
        manager = CompensationManager()
        action = RollbackAction("op1", lambda ctx: True)
        
        assert manager.mark_success(action)
    
    def test_get_pending_compensation(self):
        """Test getting pending compensation count."""
        manager = CompensationManager()
        action = RollbackAction("op1", lambda ctx: True)
        
        manager.mark_success(action)
        assert manager.get_pending_compensation() == 1
    
    def test_execute_compensation(self):
        """Test executing compensation."""
        manager = CompensationManager()
        
        def rollback_fn(ctx):
            ctx["rolled_back"] = True
            return True
        
        action = RollbackAction("op1", rollback_fn)
        manager.mark_success(action)
        
        context = {"operation_id": "op1"}
        assert manager.execute_compensation(context)
        assert context["rolled_back"]


class TestFallbackHandler:
    """Test FallbackHandler functionality."""
    
    def test_register_fallback(self):
        """Test registering fallback."""
        handler = FallbackHandler()
        fallback_fn = lambda ctx: "fallback_value"
        
        assert handler.register_fallback("op1", fallback_fn)
    
    def test_execute_fallback(self):
        """Test executing fallback."""
        handler = FallbackHandler()
        fallback_fn = lambda ctx: "fallback_value"
        handler.register_fallback("op1", fallback_fn)
        
        result = handler.execute_fallback("op1", {})
        assert result == "fallback_value"
    
    def test_execute_nonexistent_fallback(self):
        """Test executing nonexistent fallback."""
        handler = FallbackHandler()
        result = handler.execute_fallback("nonexistent", {})
        assert result is None


class TestErrorRecoveryManager:
    """Test ErrorRecoveryManager functionality."""
    
    def test_handle_retriable_error(self):
        """Test handling retriable error."""
        classifier = ErrorClassifier()
        compensation_mgr = CompensationManager()
        fallback_handler = FallbackHandler()
        
        manager = ErrorRecoveryManager(classifier, compensation_mgr, fallback_handler)
        
        error = TimeoutError("Operation timed out")
        result = manager.handle_error(error, "op1", {})
        
        # Should return None for retriable error (caller retries)
        assert result is None
    
    def test_handle_permanent_error(self):
        """Test handling permanent error."""
        classifier = ErrorClassifier()
        classifier.register_pattern("Invalid input", ErrorType.PERMANENT)
        
        compensation_mgr = CompensationManager()
        fallback_handler = FallbackHandler()
        
        manager = ErrorRecoveryManager(classifier, compensation_mgr, fallback_handler)
        
        error = ValueError("Invalid input")
        result = manager.handle_error(error, "op1", {})
        
        # Should execute compensation for non-retriable error
        assert result is None


class TestDeadLetterQueue:
    """Test DeadLetterQueue functionality."""
    
    def test_enqueue(self):
        """Test enqueuing item."""
        dlq = DeadLetterQueue()
        error = ErrorContext(ErrorType.PERMANENT, "error", "ERR", "op1")
        
        assert dlq.enqueue("op1", {"data": "test"}, error)
    
    def test_dequeue(self):
        """Test dequeuing item."""
        dlq = DeadLetterQueue()
        error = ErrorContext(ErrorType.PERMANENT, "error", "ERR", "op1")
        
        dlq.enqueue("op1", {"data": "test"}, error)
        item = dlq.dequeue()
        
        assert item["operation_id"] == "op1"
        assert dlq.size() == 0
    
    def test_peek(self):
        """Test peeking at item."""
        dlq = DeadLetterQueue()
        error = ErrorContext(ErrorType.PERMANENT, "error", "ERR", "op1")
        
        dlq.enqueue("op1", {"data": "test"}, error)
        item = dlq.peek()
        
        assert item["operation_id"] == "op1"
        assert dlq.size() == 1  # Still in queue


class TestCircuitBreakerWithRecovery:
    """Test CircuitBreakerWithRecovery functionality."""
    
    def test_circuit_breaker_closed(self):
        """Test circuit breaker in closed state."""
        breaker = CircuitBreakerWithRecovery()
        
        assert breaker.should_attempt_operation()
        assert breaker.get_state() == "closed"
    
    def test_circuit_breaker_opens(self):
        """Test circuit breaker opens after failures."""
        breaker = CircuitBreakerWithRecovery(failure_threshold=3)
        
        for _ in range(3):
            breaker.record_failure()
        
        assert not breaker.should_attempt_operation()
        assert breaker.get_state() == "open"
    
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery."""
        breaker = CircuitBreakerWithRecovery(
            failure_threshold=3,
            recovery_timeout_ms=100
        )
        
        # Open the breaker
        for _ in range(3):
            breaker.record_failure()
        
        assert breaker.get_state() == "open"
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Should transition to half-open
        assert breaker.should_attempt_operation()
        assert breaker.get_state() == "half-open"
    
    def test_record_success_closes_breaker(self):
        """Test success closes breaker from half-open."""
        breaker = CircuitBreakerWithRecovery(
            failure_threshold=3,
            recovery_timeout_ms=100
        )
        
        # Open and transition to half-open
        for _ in range(3):
            breaker.record_failure()
        time.sleep(0.15)
        breaker.should_attempt_operation()
        
        # Record success
        breaker.record_success()
        
        assert breaker.get_state() == "closed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
