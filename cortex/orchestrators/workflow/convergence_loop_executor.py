"""
ConvergenceLoopExecutor — Phase 45 Stage 2.

Retry logic with exponential backoff and convergence detection.

AC_START: AC-WORKFLOW-CONVERGENCE-20260223T000000Z
Phase: 45 | Stage: 2 | Priority: P0
Description: GREEN phase implementation for ConvergenceLoopExecutor
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Any, Optional


logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================
@dataclass
class ConvergenceConfig:
    """Configuration for convergence loop execution.
    
    Attributes:
        max_retries: Maximum number of retry attempts.
        initial_backoff_seconds: Initial backoff delay in seconds.
        backoff_multiplier: Multiplier for exponential backoff.
        max_backoff_seconds: Maximum backoff delay in seconds.
        timeout_seconds: Optional timeout for entire execution.
    """
    max_retries: int = 5
    initial_backoff_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_backoff_seconds: float = 60.0
    timeout_seconds: Optional[float] = None


# =============================================================================
# RESULT
# =============================================================================
@dataclass
class ConvergenceResult:
    """Result of convergence loop execution.
    
    Attributes:
        converged: Whether convergence was achieved.
        attempts: Number of attempts made.
        duration_seconds: Total duration in seconds.
        final_value: Final value returned by execution function.
        error_message: Error message if execution failed.
    """
    converged: bool
    attempts: int
    duration_seconds: float
    final_value: Any = None
    error_message: Optional[str] = None


# =============================================================================
# EXECUTOR
# =============================================================================
class ConvergenceLoopExecutor:
    """Executes functions with retry logic and convergence detection.
    
    Implements exponential backoff: 1s, 2s, 4s, 8s, 16s, ...
    Retries until convergence criteria met or max retries exceeded.
    
    Example:
        >>> executor = ConvergenceLoopExecutor()
        >>> def check_service():
        ...     return service.is_ready()
        >>> def is_ready(value):
        ...     return value is True
        >>> result = executor.execute(check_service, is_ready)
        >>> if result.converged:
        ...     print(f"Service ready after {result.attempts} attempts")
    """
    
    def __init__(self, config: Optional[ConvergenceConfig] = None) -> None:
        """Initialize executor with configuration.
        
        Args:
            config: Optional convergence configuration. Uses defaults if None.
        """
        self.config = config or ConvergenceConfig()
    
    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay for given attempt.
        
        Args:
            attempt: Attempt number (1-indexed).
        
        Returns:
            Backoff delay in seconds.
        """
        backoff = self.config.initial_backoff_seconds * (
            self.config.backoff_multiplier ** (attempt - 1)
        )
        return min(backoff, self.config.max_backoff_seconds)
    
    def execute(
        self,
        fn: Callable[[], Any],
        check_convergence: Callable[[Any], bool],
    ) -> ConvergenceResult:
        """Execute function with retry logic until convergence.
        
        Args:
            fn: Function to execute (no arguments).
            check_convergence: Function to check if result has converged.
        
        Returns:
            ConvergenceResult with execution outcome.
        """
        start_time = time.time()
        attempts = 0
        last_error: Optional[str] = None
        last_value: Any = None
        
        while attempts < self.config.max_retries:
            # Check timeout
            if self.config.timeout_seconds:
                elapsed = time.time() - start_time
                if elapsed >= self.config.timeout_seconds:
                    duration = time.time() - start_time
                    return ConvergenceResult(
                        converged=False,
                        attempts=attempts,
                        duration_seconds=duration,
                        error_message="Timeout exceeded",
                    )
            
            attempts += 1
            
            try:
                # Execute function
                value = fn()
                last_value = value
                
                # Check convergence
                if check_convergence(value):
                    duration = time.time() - start_time
                    logger.info(
                        f"Convergence achieved after {attempts} attempts "
                        f"in {duration:.2f}s"
                    )
                    return ConvergenceResult(
                        converged=True,
                        attempts=attempts,
                        duration_seconds=duration,
                        final_value=value,
                    )
                
                # Not converged, apply backoff if more retries remain
                if attempts < self.config.max_retries:
                    backoff = self._calculate_backoff(attempts)
                    logger.debug(
                        f"Attempt {attempts}/{self.config.max_retries} "
                        f"not converged, backing off {backoff:.2f}s"
                    )
                    time.sleep(backoff)
            
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Attempt {attempts}/{self.config.max_retries} failed: {e}"
                )
                
                # Apply backoff if more retries remain
                if attempts < self.config.max_retries:
                    backoff = self._calculate_backoff(attempts)
                    time.sleep(backoff)
        
        # Max retries exceeded
        duration = time.time() - start_time
        error_msg = last_error or "Max retries exceeded without convergence"
        logger.error(
            f"Convergence failed after {attempts} attempts in {duration:.2f}s: {error_msg}"
        )
        
        return ConvergenceResult(
            converged=False,
            attempts=attempts,
            duration_seconds=duration,
            final_value=last_value,
            error_message=error_msg,
        )


# =============================================================================
# AC_COMPLETE: AC-WORKFLOW-CONVERGENCE-20260223T000000Z (GREEN phase implementation)
# =============================================================================
