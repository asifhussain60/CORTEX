"""
Retry Handler with Exponential Backoff for CORTEX

Implements automatic retry logic with exponential backoff
to handle transient failures gracefully.

AC-NFR-002-02: Automatic retry with exponential backoff
"""

import logging
import time
from typing import Any, Callable, Optional, TypeVar
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryPolicy(Enum):
    """Retry policies."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    initial_delay: float = 0.5  # seconds
    max_delay: float = 30.0     # seconds
    backoff_multiplier: float = 2.0
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL_BACKOFF
    retryable_exceptions: tuple = (Exception,)
    
    def validate(self):
        """Validate retry configuration."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.initial_delay < 0:
            raise ValueError("initial_delay must be >= 0")
        if self.max_delay < self.initial_delay:
            raise ValueError("max_delay must be >= initial_delay")
        if self.backoff_multiplier <= 1.0:
            raise ValueError("backoff_multiplier must be > 1.0")


@dataclass
class RetryResult:
    """Result of a retry operation."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    attempts: int = 0
    final_exception: Optional[Exception] = None
    total_delay_seconds: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class RetryHandler:
    """Manages retry logic with various backoff strategies."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.config.validate()
        self.retry_history: list[tuple[int, float, Optional[Exception]]] = []
    
    def execute_with_retry(
        self,
        fn: Callable[..., T],
        *args,
        config: Optional[RetryConfig] = None,
        **kwargs
    ) -> RetryResult:
        """
        Execute function with retry logic.
        
        Args:
            fn: Function to execute
            *args: Positional arguments for function
            config: Optional retry config override
            **kwargs: Keyword arguments for function
        
        Returns:
            RetryResult with success, data, and attempt count
        """
        config = config or self.config
        config.validate()
        
        last_exception: Optional[Exception] = None
        total_delay = 0.0
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                result = fn(*args, **kwargs)
                logger.debug(f"Succeeded on attempt {attempt}")
                return RetryResult(
                    success=True,
                    data=result,
                    attempts=attempt,
                    total_delay_seconds=total_delay
                )
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not isinstance(e, config.retryable_exceptions):
                    logger.error(f"Non-retryable exception: {type(e).__name__}")
                    return RetryResult(
                        success=False,
                        error=str(e),
                        attempts=attempt,
                        final_exception=e,
                        total_delay_seconds=total_delay
                    )
                
                # Last attempt
                if attempt == config.max_attempts:
                    logger.error(f"Failed after {attempt} attempts: {str(e)}")
                    return RetryResult(
                        success=False,
                        error=str(e),
                        attempts=attempt,
                        final_exception=e,
                        total_delay_seconds=total_delay
                    )
                
                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt, config)
                logger.warning(
                    f"Attempt {attempt} failed ({type(e).__name__}). "
                    f"Retrying in {delay:.2f}s (max attempts: {config.max_attempts})"
                )
                
                self.retry_history.append((attempt, delay, e))
                total_delay += delay
                time.sleep(delay)
        
        # Should never reach here
        return RetryResult(
            success=False,
            error="Retry exhausted",
            attempts=config.max_attempts,
            final_exception=last_exception,
            total_delay_seconds=total_delay
        )
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        """Calculate delay for given attempt number."""
        if config.policy == RetryPolicy.EXPONENTIAL_BACKOFF:
            delay = config.initial_delay * (config.backoff_multiplier ** (attempt - 1))
        elif config.policy == RetryPolicy.LINEAR_BACKOFF:
            delay = config.initial_delay * attempt
        elif config.policy == RetryPolicy.FIXED_DELAY:
            delay = config.initial_delay
        else:
            delay = config.initial_delay
        
        # Cap at max delay
        delay = min(delay, config.max_delay)
        return delay
    
    def get_retry_history(self) -> list[tuple[int, float, Optional[Exception]]]:
        """Get retry history."""
        return self.retry_history.copy()
    
    def clear_history(self):
        """Clear retry history."""
        self.retry_history.clear()
    
    @staticmethod
    def create_exponential_config(
        max_attempts: int = 3,
        initial_delay: float = 0.5,
        backoff_multiplier: float = 2.0
    ) -> RetryConfig:
        """Create exponential backoff configuration."""
        return RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            backoff_multiplier=backoff_multiplier,
            policy=RetryPolicy.EXPONENTIAL_BACKOFF
        )
    
    @staticmethod
    def create_linear_config(
        max_attempts: int = 3,
        initial_delay: float = 0.5
    ) -> RetryConfig:
        """Create linear backoff configuration."""
        return RetryConfig(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            policy=RetryPolicy.LINEAR_BACKOFF
        )
    
    @staticmethod
    def create_fixed_config(
        max_attempts: int = 3,
        delay: float = 0.5
    ) -> RetryConfig:
        """Create fixed delay configuration."""
        return RetryConfig(
            max_attempts=max_attempts,
            initial_delay=delay,
            policy=RetryPolicy.FIXED_DELAY
        )
