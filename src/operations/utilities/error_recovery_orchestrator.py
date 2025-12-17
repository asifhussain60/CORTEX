"""
Error Recovery Orchestrator

Provides sophisticated error recovery mechanisms with:
- Exponential backoff retry with jitter
- Circuit breaker pattern for failing services
- Fallback strategy chains
- Error classification and pattern recognition
- Recovery statistics and telemetry

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0.0
Feature: Orchestrator Enhancement Plan v2.0 - Feature 17
"""

import asyncio
import random
import time
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict


class ErrorRecoveryOrchestrator:
    """
    Orchestrates error recovery across operations with retry policies,
    circuit breakers, and fallback strategies
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        circuit_threshold: int = 5,
        circuit_timeout: float = 60.0
    ):
        """
        Initialize error recovery orchestrator
        
        Args:
            max_retries: Maximum retry attempts
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay cap (seconds)
            jitter: Whether to add randomization to delays
            circuit_threshold: Failures before opening circuit
            circuit_timeout: Time before circuit transitions to half-open
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.circuit_threshold = circuit_threshold
        self.circuit_timeout = circuit_timeout
        
        # Circuit breaker state
        self._circuit_state: Dict[str, Dict] = {}
        
        # Recovery statistics
        self._stats: Dict[str, Dict] = defaultdict(lambda: {
            "total_attempts": 0,
            "successes": 0,
            "failures": 0,
            "error_types": defaultdict(int)
        })
        
        # Error classification patterns
        self._transient_errors = (
            TimeoutError,
            ConnectionError,
            ConnectionRefusedError,
            ConnectionResetError,
            asyncio.TimeoutError
        )
        
        self._permanent_errors = (
            ValueError,
            TypeError,
            KeyError,
            AttributeError
        )
    
    def calculate_backoff(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay
        
        Args:
            attempt: Current attempt number (0-indexed)
        
        Returns:
            Delay in seconds with optional jitter
        """
        # Exponential: 2^attempt
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        
        # Add jitter: randomize ±25%
        if self.jitter:
            jitter_factor = random.uniform(0.75, 1.25)
            delay *= jitter_factor
        
        return delay
    
    async def retry_with_backoff(
        self,
        operation: Callable,
        max_attempts: Optional[int] = None,
        operation_name: Optional[str] = None
    ) -> Any:
        """
        Retry operation with exponential backoff
        
        Args:
            operation: Async or sync function to retry
            max_attempts: Override default max attempts
            operation_name: Name for tracking statistics
        
        Returns:
            Result of successful operation
        
        Raises:
            Last exception if all attempts fail
        """
        attempts = max_attempts or self.max_retries
        op_name = operation_name or getattr(operation, '__name__', 'unknown')
        last_error = None
        
        for attempt in range(attempts):
            try:
                # Handle both async and sync operations
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = operation()
                
                # Track success
                self.track_recovery_attempt(op_name, attempt + 1, True, None)
                self.record_success(op_name)
                
                return result
            
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                
                # Track failure
                self.track_recovery_attempt(op_name, attempt + 1, False, error_type)
                self.record_failure(op_name)
                
                # Check if retryable
                if not self.is_retryable(e):
                    raise
                
                # Last attempt - don't wait
                if attempt == attempts - 1:
                    raise
                
                # Wait with backoff
                delay = self.calculate_backoff(attempt)
                await asyncio.sleep(delay)
        
        # All attempts exhausted
        raise last_error
    
    def record_failure(self, operation_name: str) -> None:
        """
        Record operation failure for circuit breaker
        
        Args:
            operation_name: Name of the operation
        """
        if operation_name not in self._circuit_state:
            self._circuit_state[operation_name] = {
                "state": "closed",
                "failures": 0,
                "last_failure_time": None,
                "successes_in_half_open": 0
            }
        
        circuit = self._circuit_state[operation_name]
        circuit["failures"] += 1
        circuit["last_failure_time"] = datetime.now()
        
        # Open circuit if threshold exceeded
        if circuit["failures"] >= self.circuit_threshold:
            circuit["state"] = "open"
    
    def record_success(self, operation_name: str) -> None:
        """
        Record operation success for circuit breaker
        
        Args:
            operation_name: Name of the operation
        """
        if operation_name not in self._circuit_state:
            return
        
        circuit = self._circuit_state[operation_name]
        
        if circuit["state"] == "half-open":
            circuit["successes_in_half_open"] += 1
            
            # Close circuit after successful test
            if circuit["successes_in_half_open"] >= 2:
                circuit["state"] = "closed"
                circuit["failures"] = 0
                circuit["successes_in_half_open"] = 0
    
    def is_circuit_open(self, operation_name: str) -> bool:
        """
        Check if circuit breaker is open for operation
        
        Args:
            operation_name: Name of the operation
        
        Returns:
            True if circuit is open (blocking requests)
        """
        if operation_name not in self._circuit_state:
            return False
        
        circuit = self._circuit_state[operation_name]
        
        # Check if timeout elapsed (transition to half-open)
        if circuit["state"] == "open":
            time_since_failure = (
                datetime.now() - circuit["last_failure_time"]
            ).total_seconds()
            
            if time_since_failure >= self.circuit_timeout:
                circuit["state"] = "half-open"
                circuit["successes_in_half_open"] = 0
                return False
            
            return True
        
        return False
    
    async def execute_with_fallback(
        self,
        strategies: List[Callable],
        operation_name: Optional[str] = None
    ) -> Any:
        """
        Execute with fallback strategy chain
        
        Args:
            strategies: List of async functions to try in order
            operation_name: Name for tracking
        
        Returns:
            Result from first successful strategy
        
        Raises:
            Last exception if all strategies fail
        """
        last_error = None
        op_name = operation_name or "fallback_chain"
        
        for i, strategy in enumerate(strategies):
            try:
                result = await strategy()
                
                # Track which strategy succeeded
                self.track_recovery_attempt(
                    f"{op_name}_strategy_{i}",
                    1,
                    True,
                    None
                )
                
                return result
            
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                
                # Track failure
                self.track_recovery_attempt(
                    f"{op_name}_strategy_{i}",
                    1,
                    False,
                    error_type
                )
                
                # Continue to next strategy
                continue
        
        # All strategies failed
        raise last_error
    
    def classify_error(self, error: Exception) -> str:
        """
        Classify error as transient or permanent
        
        Args:
            error: Exception instance
        
        Returns:
            "transient" or "permanent"
        """
        if isinstance(error, self._transient_errors):
            return "transient"
        elif isinstance(error, self._permanent_errors):
            return "permanent"
        else:
            # Default to permanent for safety
            return "permanent"
    
    def is_retryable(self, error: Exception) -> bool:
        """
        Check if error should be retried
        
        Args:
            error: Exception instance
        
        Returns:
            True if error is retryable
        """
        return self.classify_error(error) == "transient"
    
    def track_recovery_attempt(
        self,
        operation: str,
        attempt: int,
        success: bool,
        error_type: Optional[str]
    ) -> None:
        """
        Track recovery attempt statistics
        
        Args:
            operation: Operation name
            attempt: Attempt number
            success: Whether attempt succeeded
            error_type: Type of error if failed
        """
        stats = self._stats[operation]
        stats["total_attempts"] += 1
        
        if success:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
            if error_type:
                stats["error_types"][error_type] += 1
    
    def get_recovery_stats(self, operation: str) -> Optional[Dict]:
        """
        Get recovery statistics for operation
        
        Args:
            operation: Operation name
        
        Returns:
            Statistics dictionary or None if no data
        """
        if operation not in self._stats:
            return None
        
        stats = dict(self._stats[operation])
        stats["error_types"] = dict(stats["error_types"])
        
        # Calculate success rate
        total = stats["total_attempts"]
        if total > 0:
            stats["success_rate"] = stats["successes"] / total
        else:
            stats["success_rate"] = 0.0
        
        return stats
    
    def get_global_stats(self) -> Dict:
        """
        Get global recovery statistics
        
        Returns:
            Aggregated statistics across all operations
        """
        total_operations = len(self._stats)
        total_attempts = 0
        total_successes = 0
        total_failures = 0
        all_error_types = defaultdict(int)
        
        for stats in self._stats.values():
            total_attempts += stats["total_attempts"]
            total_successes += stats["successes"]
            total_failures += stats["failures"]
            
            for error_type, count in stats["error_types"].items():
                all_error_types[error_type] += count
        
        success_rate = (
            total_successes / total_attempts
            if total_attempts > 0
            else 0.0
        )
        
        return {
            "total_operations": total_operations,
            "total_attempts": total_attempts,
            "total_recoveries": total_successes,
            "total_failures": total_failures,
            "success_rate": success_rate,
            "error_types": dict(all_error_types)
        }
    
    def reset_circuit(self, operation_name: str) -> None:
        """
        Manually reset circuit breaker
        
        Args:
            operation_name: Name of operation to reset
        """
        if operation_name in self._circuit_state:
            self._circuit_state[operation_name] = {
                "state": "closed",
                "failures": 0,
                "last_failure_time": None,
                "successes_in_half_open": 0
            }
    
    def reset_all_circuits(self) -> None:
        """Reset all circuit breakers"""
        self._circuit_state.clear()
    
    def get_circuit_state(self, operation_name: str) -> str:
        """
        Get current circuit breaker state
        
        Args:
            operation_name: Name of operation
        
        Returns:
            "closed", "open", or "half-open"
        """
        if operation_name not in self._circuit_state:
            return "closed"
        
        return self._circuit_state[operation_name]["state"]


# Export
__all__ = ["ErrorRecoveryOrchestrator"]
