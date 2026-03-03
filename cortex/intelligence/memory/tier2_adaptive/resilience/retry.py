"""
Retry — RetryPolicy, RetryPolicyBuilder, RetryResult, ExponentialBackoffRetry.

Phase 103-f: extracted from resilience.py (1,876L) god-object.
noqa: CORE-035 — domain-scoped; RetryPolicy/RetryResult intentionally parallel infrastructure copies.
"""
from __future__ import annotations

import logging
import time
from threading import RLock
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RetryPolicy:
    """Configuration for retry behavior with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff_ms: int = 100,
        max_backoff_ms: int = 32000,
        backoff_multiplier: float = 2.0,
        use_jitter: bool = False,
    ) -> None:
        """Initialize retry policy."""
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self.backoff_multiplier = backoff_multiplier
        self.use_jitter = use_jitter
        self.non_retryable_exceptions: List[type] = []

    def calculate_backoff(self, attempt: int) -> float:
        """Calculate backoff time for given attempt number (milliseconds)."""
        import random
        backoff = self.initial_backoff_ms * (self.backoff_multiplier ** (attempt - 1))
        backoff = min(backoff, self.max_backoff_ms)
        if self.use_jitter:
            jitter = random.uniform(0, backoff * 0.1)
            backoff += jitter
        return backoff


class RetryPolicyBuilder:
    """Builder for creating RetryPolicy instances with fluent API."""

    def __init__(self) -> None:
        """Initialize builder with default values."""
        self._max_retries = 3
        self._initial_backoff = 100
        self._max_backoff = 32000
        self._multiplier = 2.0
        self._use_jitter = False

    def with_max_retries(self, max_retries: int) -> RetryPolicyBuilder:
        """Set maximum number of retries."""
        self._max_retries = max_retries
        return self

    def with_initial_backoff(self, backoff_ms: int) -> RetryPolicyBuilder:
        """Set initial backoff duration."""
        self._initial_backoff = backoff_ms
        return self

    def with_max_backoff(self, backoff_ms: int) -> RetryPolicyBuilder:
        """Set maximum backoff duration."""
        self._max_backoff = backoff_ms
        return self

    def with_multiplier(self, multiplier: float) -> RetryPolicyBuilder:
        """Set backoff multiplier."""
        self._multiplier = multiplier
        return self

    def with_jitter(self, use_jitter: bool) -> RetryPolicyBuilder:
        """Enable/disable jitter in backoff."""
        self._use_jitter = use_jitter
        return self

    def build(self) -> RetryPolicy:
        """Build the RetryPolicy instance."""
        return RetryPolicy(
            max_retries=self._max_retries,
            initial_backoff_ms=self._initial_backoff,
            max_backoff_ms=self._max_backoff,
            backoff_multiplier=self._multiplier,
            use_jitter=self._use_jitter,
        )


class RetryResult:
    """Result of a retry operation."""

    def __init__(
        self,
        success: bool,
        attempt_count: int,
        total_time_ms: float,
        exception: Optional[Exception] = None,
        data: Any = None,
    ) -> None:
        """Initialize retry result."""
        self.success = success
        self.attempt_count = attempt_count
        self.total_time_ms = total_time_ms
        self.exception = exception
        self.data = data

    def is_success(self) -> bool:
        """Check if operation succeeded."""
        return self.success

    def get_data(self) -> Any:
        """Get result data."""
        return self.data

    def get_exception(self) -> Optional[Exception]:
        """Get exception if failed."""
        return self.exception


class ExponentialBackoffRetry:
    """Retry handler with exponential backoff strategy."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff_ms: int = 100,
        max_backoff_ms: int = 32000,
    ) -> None:
        """Initialize retry handler."""
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self._lock = RLock()
        self._retry_count: Dict[str, int] = {}
        logger.debug(
            f"ExponentialBackoffRetry initialized: "
            f"max_retries={max_retries}, initial_backoff_ms={initial_backoff_ms}"
        )

    def execute_with_retry(
        self,
        operation: Callable[..., Any],
        policy: Optional[RetryPolicy] = None,
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        raise_on_retry_failure: bool = True,
    ) -> Any:
        """Execute operation with retry and exponential backoff."""
        if policy is None:
            policy = RetryPolicy(
                max_retries=self.max_retries,
                initial_backoff_ms=self.initial_backoff_ms,
                max_backoff_ms=self.max_backoff_ms,
            )
        if kwargs is None:
            kwargs = {}

        last_exception: Optional[Exception] = None
        start_time = time.time()

        for attempt in range(policy.max_retries + 1):
            try:
                result = operation(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"Operation succeeded on attempt {attempt + 1}, elapsed: {elapsed_ms:.2f}ms"
                )
                return result
            except Exception as exc:
                last_exception = exc
                if any(isinstance(exc, t) for t in policy.non_retryable_exceptions):
                    logger.warning(f"Non-retryable exception on attempt {attempt + 1}: {exc}")
                    raise
                if attempt >= policy.max_retries:
                    elapsed_ms = (time.time() - start_time) * 1000
                    logger.error(
                        f"Operation failed after {attempt + 1} attempts, "
                        f"total time: {elapsed_ms:.2f}ms"
                    )
                    if raise_on_retry_failure:
                        raise
                    return None
                backoff_ms = policy.calculate_backoff(attempt + 1)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {exc}. Retrying in {backoff_ms:.2f}ms..."
                )
                time.sleep(backoff_ms / 1000.0)

        if raise_on_retry_failure and last_exception:
            raise last_exception
        return None
