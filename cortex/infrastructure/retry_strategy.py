"""
Retry Strategy with Exponential Backoff and Jitter.

AC-INFRA-001-04: Implements intelligent retry with:
- Exponential backoff with jitter
- Idempotency token tracking
- Transient vs permanent failure detection
- Retry budget limits
"""

import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

T = TypeVar('T')


class RetryExhaustedError(Exception):
    """Raised when retry budget is exhausted."""
    pass


class NonRetriableError(Exception):
    """Raised for errors that should not be retried."""
    pass


@dataclass
class IdempotencyToken:
    """Token for tracking idempotent operations."""
    value: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class RetryConfig:
    """Configuration for retry strategy."""

    max_attempts: int = 5
    initial_delay_ms: float = 100.0
    max_delay_ms: float = 5000.0
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.25  # ±25% randomization

    retriable_exceptions: Tuple[type, ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )

    non_retriable_exceptions: Tuple[type, ...] = (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        PermissionError,
        NotImplementedError,
    )

    def __post_init__(self) -> None:
        """Validate configuration on initialization."""
        self.validate()

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.max_attempts <= 0:
            raise ValueError("max_attempts must be positive")
        if self.initial_delay_ms <= 0:
            raise ValueError("initial_delay_ms must be positive")
        if self.max_delay_ms <= 0:
            raise ValueError("max_delay_ms must be positive")
        if self.backoff_multiplier < 1.0:
            raise ValueError("backoff_multiplier must be >= 1.0")
        if not 0 <= self.jitter_factor <= 1.0:
            raise ValueError("jitter_factor must be between 0 and 1")


class RetryStrategy:
    """
    Intelligent retry strategy with exponential backoff and jitter.

    Features:
    - Exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms
    - Jitter: ±25% randomization to prevent thundering herd
    - Idempotency tracking: Prevents duplicate operations
    - Smart failure detection: Retries transient, skips permanent errors
    - Metrics: Tracks retry attempts and success/failure rates

    Example:
        >>> strategy = RetryStrategy()
        >>> def flaky_api_call():
        ...     response = call_external_api()
        ...     return response.json()
        >>> result = strategy.execute(flaky_api_call)
    """

    def __init__(self, config: Optional[RetryConfig] = None) -> None:
        """
        Initialize retry strategy.

        Args:
            config: Retry configuration (uses defaults if None)
        """
        self.config = config or RetryConfig()
        self.config.validate()

        # Metrics tracking
        self._total_operations = 0
        self._successful_operations = 0
        self._failed_operations = 0
        self._total_retries = 0

        # Idempotency tracking
        self._idempotency_cache: Dict[str, Any] = {}

    def execute(self, func: Callable[[], T]) -> T:
        """
        Execute function with retry logic.

        Args:
            func: Callable to execute (should take no args)

        Returns:
            Result from func

        Raises:
            RetryExhaustedError: If all retry attempts exhausted
            NonRetriableError: If non-retriable error encountered
        """
        self._total_operations += 1
        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_attempts):
            try:
                result = func()
                self._successful_operations += 1
                if attempt > 0:
                    self._total_retries += attempt
                return result

            except self.config.non_retriable_exceptions as e:
                # Don't retry permanent failures
                self._failed_operations += 1
                raise NonRetriableError(f"Non-retriable error: {e}") from e

            except self.config.retriable_exceptions as e:
                last_exception = e

                # If this was the last attempt, raise exhausted error
                if attempt == self.config.max_attempts - 1:
                    self._failed_operations += 1
                    raise RetryExhaustedError(
                        f"Retry exhausted after {self.config.max_attempts} attempts"
                    ) from last_exception

                # Calculate delay and wait before retry
                delay = self._calculate_delay(attempt)
                time.sleep(delay)
                self._total_retries += 1

            except Exception as e:
                # Unknown exception type - treat as non-retriable for safety
                self._failed_operations += 1
                raise NonRetriableError(f"Unknown error type: {e}") from e

        # Should never reach here, but handle gracefully
        self._failed_operations += 1
        raise RetryExhaustedError("Retry logic error") from last_exception

    def execute_with_idempotency(
        self,
        func: Callable[[], T],
        token: IdempotencyToken
    ) -> T:
        """
        Execute function with idempotency tracking.

        If the same token is used multiple times, returns cached result
        instead of re-executing the operation.

        Args:
            func: Callable to execute
            token: Idempotency token

        Returns:
            Result from func or cached result
        """
        # Check if we already have a result for this token
        if token.value in self._idempotency_cache:
            return self._idempotency_cache[token.value]

        # Execute and cache result
        result = self.execute(func)
        self._idempotency_cache[token.value] = result

        return result

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for retry attempt with exponential backoff and jitter.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Calculate base delay with exponential backoff
        base_delay_ms = self.config.initial_delay_ms * (
            self.config.backoff_multiplier ** attempt
        )

        # Cap at maximum delay
        base_delay_ms = min(base_delay_ms, self.config.max_delay_ms)

        # Add jitter (±jitter_factor%)
        jitter_range = base_delay_ms * self.config.jitter_factor
        jitter = random.uniform(-jitter_range, jitter_range)

        final_delay_ms = base_delay_ms + jitter

        # Ensure we don't exceed max delay after jitter
        final_delay_ms = max(0, min(final_delay_ms, self.config.max_delay_ms))

        # Convert to seconds
        return final_delay_ms / 1000.0

    def generate_idempotency_token(self) -> IdempotencyToken:
        """
        Generate a new idempotency token.

        Returns:
            New unique idempotency token
        """
        return IdempotencyToken()

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get retry strategy metrics.

        Returns:
            Dictionary with metrics including operations, retries, success rate
        """
        success_rate = 0.0
        if self._total_operations > 0:
            success_rate = self._successful_operations / self._total_operations

        return {
            "total_operations": self._total_operations,
            "successful_operations": self._successful_operations,
            "failed_operations": self._failed_operations,
            "total_retries": self._total_retries,
            "success_rate": success_rate,
            "idempotency_cache_size": len(self._idempotency_cache),
        }

    def clear_idempotency_cache(self) -> None:
        """Clear the idempotency cache."""
        self._idempotency_cache.clear()
