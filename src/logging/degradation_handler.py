"""
CORTEX Audit Logger - Graceful Degradation Handler
Version: 1.0.0
Purpose: Resilient operations with fallback strategies and health monitoring
"""

import logging
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class OperationalMode(Enum):
    """Audit logger operational modes"""
    NORMAL = "normal"
    MEMORY_ONLY = "memory_only"
    STDERR_ONLY = "stderr_only"
    REDUCED_LOGGING = "reduced_logging"
    DISABLED = "disabled"


class HealthStatus(Enum):
    """Health check statuses"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class DegradationReason(Enum):
    """Reasons for degradation"""
    DISK_FULL = "disk_full"
    PERMISSION_DENIED = "permission_denied"
    HIGH_ERROR_RATE = "high_error_rate"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MEMORY_PRESSURE = "memory_pressure"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    EXTERNAL_DEPENDENCY_FAILURE = "external_dependency_failure"


class CircuitBreaker:
    """
    Circuit breaker pattern for fault tolerance
    
    States: CLOSED → OPEN → HALF_OPEN → CLOSED
    """
    
    def __init__(
        self,
        threshold: int = 50,
        timeout: int = 60,
        half_open_max_calls: int = 5
    ):
        self.threshold = threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"
        self.half_open_calls = 0
        self._lock = threading.Lock()
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        with self._lock:
            if self.state == "OPEN":
                # Check if timeout has elapsed
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.timeout:
                        self.state = "HALF_OPEN"
                        self.half_open_calls = 0
                    else:
                        raise Exception("Circuit breaker is OPEN")
                        
            if self.state == "HALF_OPEN":
                if self.half_open_calls >= self.half_open_max_calls:
                    raise Exception("Circuit breaker HALF_OPEN limit reached")
                self.half_open_calls += 1
                
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure()
            raise e
            
    def _record_success(self) -> None:
        """Record successful call"""
        with self._lock:
            self.success_count += 1
            
            if self.state == "HALF_OPEN":
                if self.half_open_calls >= self.half_open_max_calls:
                    # Enough successful calls, close circuit
                    self.state = "CLOSED"
                    self.failure_count = 0
                    
    def _record_failure(self) -> None:
        """Record failed call"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == "HALF_OPEN":
                # Failure in half-open state, reopen circuit
                self.state = "OPEN"
            elif self.failure_count >= self.threshold:
                # Too many failures, open circuit
                self.state = "OPEN"
                
    def reset(self) -> None:
        """Reset circuit breaker"""
        with self._lock:
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.state = "CLOSED"
            self.half_open_calls = 0
            
    def get_state(self) -> str:
        """Get current circuit breaker state"""
        return self.state


class DegradationHandler:
    """
    Graceful degradation handler with fallback strategies
    
    Features:
    - Automatic mode switching based on failures
    - Circuit breaker pattern
    - Fallback to stderr
    - In-memory-only mode
    - Reduced logging mode
    - Health check endpoint
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Operational state
        self.current_mode = OperationalMode.NORMAL
        self.degradation_reasons: List[DegradationReason] = []
        self.mode_changed_at: Optional[datetime] = None
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreaker(
            threshold=self.config.get("circuit_breaker_threshold", 50),
            timeout=self.config.get("circuit_breaker_timeout_seconds", 60),
            half_open_max_calls=self.config.get("circuit_breaker_half_open_calls", 5)
        )
        
        # Error tracking
        self.recent_errors: List[Dict[str, Any]] = []
        self.error_window_seconds = 60
        self.error_threshold = self.config.get("error_threshold_per_minute", 100)
        
        # Memory buffer for fallback
        self.memory_buffer: List[Dict[str, Any]] = []
        self.max_memory_buffer_size = 10000
        
        # Health status
        self.health_status = HealthStatus.HEALTHY
        self.last_health_check: Optional[datetime] = None
        
        # Thread safety
        self._lock = threading.Lock()
        
    def handle_write_failure(
        self,
        error: Exception,
        log_entry: Dict[str, Any]
    ) -> bool:
        """
        Handle log write failure with graceful degradation
        
        Returns:
            True if handled successfully, False otherwise
        """
        with self._lock:
            # Record error
            self._record_error(error, log_entry)
            
            # Check error rate
            if self._should_degrade():
                self._degrade_mode()
                
            # Try fallback strategies
            return self._try_fallback(log_entry)
            
    def _record_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """Record error for tracking"""
        error_entry = {
            "timestamp": datetime.now(),
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context
        }
        
        self.recent_errors.append(error_entry)
        
        # Trim old errors
        cutoff = datetime.now() - timedelta(seconds=self.error_window_seconds)
        self.recent_errors = [
            e for e in self.recent_errors
            if e["timestamp"] > cutoff
        ]
        
    def _should_degrade(self) -> bool:
        """Check if system should degrade operational mode"""
        # Check error rate
        error_count = len(self.recent_errors)
        if error_count > self.error_threshold:
            self.degradation_reasons.append(DegradationReason.HIGH_ERROR_RATE)
            return True
            
        # Check circuit breaker
        if self.circuit_breaker.get_state() == "OPEN":
            self.degradation_reasons.append(DegradationReason.CIRCUIT_BREAKER_OPEN)
            return True
            
        # Check disk space (if applicable)
        if self._is_disk_full():
            self.degradation_reasons.append(DegradationReason.DISK_FULL)
            return True
            
        return False
        
    def _is_disk_full(self) -> bool:
        """Check if disk is full"""
        try:
            import shutil
            log_path = self.config.get("log_base_path", "logs/audit")
            stat = shutil.disk_usage(log_path)
            
            # Consider disk full if < 5% free
            free_percent = (stat.free / stat.total) * 100
            return free_percent < 5
        except Exception:
            return False
            
    def _degrade_mode(self) -> None:
        """Degrade operational mode"""
        if self.current_mode == OperationalMode.NORMAL:
            # First degradation: switch to memory-only
            self.current_mode = OperationalMode.MEMORY_ONLY
            self.mode_changed_at = datetime.now()
            logger.warning(
                f"Degraded to {self.current_mode.value} mode. "
                f"Reasons: {[r.value for r in self.degradation_reasons]}"
            )
            
        elif self.current_mode == OperationalMode.MEMORY_ONLY:
            # Second degradation: switch to stderr-only
            self.current_mode = OperationalMode.STDERR_ONLY
            self.mode_changed_at = datetime.now()
            logger.warning(f"Degraded to {self.current_mode.value} mode")
            
        elif self.current_mode == OperationalMode.STDERR_ONLY:
            # Third degradation: reduce logging
            self.current_mode = OperationalMode.REDUCED_LOGGING
            self.mode_changed_at = datetime.now()
            logger.warning(f"Degraded to {self.current_mode.value} mode")
            
        elif self.current_mode == OperationalMode.REDUCED_LOGGING:
            # Final degradation: disable
            self.current_mode = OperationalMode.DISABLED
            self.mode_changed_at = datetime.now()
            logger.critical("Audit logging DISABLED due to repeated failures")
            
        # Update health status
        self._update_health_status()
        
    def _try_fallback(self, log_entry: Dict[str, Any]) -> bool:
        """Try fallback strategies based on current mode"""
        if self.current_mode == OperationalMode.MEMORY_ONLY:
            return self._write_to_memory(log_entry)
            
        elif self.current_mode == OperationalMode.STDERR_ONLY:
            return self._write_to_stderr(log_entry)
            
        elif self.current_mode == OperationalMode.REDUCED_LOGGING:
            # Only log critical entries
            if log_entry.get("level") in ["CRITICAL", "ERROR"]:
                return self._write_to_stderr(log_entry)
            return True  # Silently drop
            
        elif self.current_mode == OperationalMode.DISABLED:
            return True  # Silently drop
            
        return False
        
    def _write_to_memory(self, log_entry: Dict[str, Any]) -> bool:
        """Write to in-memory buffer"""
        try:
            if len(self.memory_buffer) >= self.max_memory_buffer_size:
                # Drop oldest entry
                self.memory_buffer.pop(0)
                
            self.memory_buffer.append(log_entry)
            return True
        except Exception as e:
            logger.error(f"Failed to write to memory buffer: {e}")
            return False
            
    def _write_to_stderr(self, log_entry: Dict[str, Any]) -> bool:
        """Write to stderr as last resort"""
        try:
            import json
            sys.stderr.write(json.dumps(log_entry) + "\n")
            sys.stderr.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to write to stderr: {e}")
            return False
            
    def attempt_recovery(self) -> bool:
        """
        Attempt to recover to normal mode
        
        Returns:
            True if recovery successful, False otherwise
        """
        with self._lock:
            if self.current_mode == OperationalMode.NORMAL:
                return True  # Already in normal mode
                
            # Check if enough time has passed
            if self.mode_changed_at:
                elapsed = (datetime.now() - self.mode_changed_at).total_seconds()
                if elapsed < 60:
                    return False  # Too soon to recover
                    
            # Clear error history
            self.recent_errors = []
            self.degradation_reasons = []
            
            # Reset circuit breaker
            self.circuit_breaker.reset()
            
            # Try to recover one level
            if self.current_mode == OperationalMode.DISABLED:
                self.current_mode = OperationalMode.REDUCED_LOGGING
            elif self.current_mode == OperationalMode.REDUCED_LOGGING:
                self.current_mode = OperationalMode.STDERR_ONLY
            elif self.current_mode == OperationalMode.STDERR_ONLY:
                self.current_mode = OperationalMode.MEMORY_ONLY
            elif self.current_mode == OperationalMode.MEMORY_ONLY:
                # Try to flush memory buffer to disk
                if self._flush_memory_buffer():
                    self.current_mode = OperationalMode.NORMAL
                else:
                    return False
                    
            self.mode_changed_at = datetime.now()
            self._update_health_status()
            
            logger.info(f"Recovered to {self.current_mode.value} mode")
            return True
            
    def _flush_memory_buffer(self) -> bool:
        """Flush memory buffer to disk"""
        try:
            # This would integrate with actual log writer
            # For now, just clear buffer on success
            self.memory_buffer = []
            return True
        except Exception as e:
            logger.error(f"Failed to flush memory buffer: {e}")
            return False
            
    def _update_health_status(self) -> None:
        """Update health status based on operational mode"""
        if self.current_mode == OperationalMode.NORMAL:
            self.health_status = HealthStatus.HEALTHY
        elif self.current_mode == OperationalMode.MEMORY_ONLY:
            self.health_status = HealthStatus.DEGRADED
        elif self.current_mode == OperationalMode.STDERR_ONLY:
            self.health_status = HealthStatus.UNHEALTHY
        else:
            self.health_status = HealthStatus.CRITICAL
            
    def get_health_check(self) -> Dict[str, Any]:
        """
        Get health check response
        
        Returns:
            Health check dictionary with status and details
        """
        self.last_health_check = datetime.now()
        
        return {
            "status": self.health_status.value,
            "operational_mode": self.current_mode.value,
            "degradation_reasons": [r.value for r in self.degradation_reasons],
            "mode_changed_at": self.mode_changed_at.isoformat() if self.mode_changed_at else None,
            "recent_error_count": len(self.recent_errors),
            "circuit_breaker_state": self.circuit_breaker.get_state(),
            "memory_buffer_size": len(self.memory_buffer),
            "timestamp": self.last_health_check.isoformat()
        }
        
    def get_current_mode(self) -> OperationalMode:
        """Get current operational mode"""
        return self.current_mode
        
    def force_mode(self, mode: OperationalMode) -> None:
        """Force operational mode (for testing)"""
        with self._lock:
            self.current_mode = mode
            self.mode_changed_at = datetime.now()
            self._update_health_status()
