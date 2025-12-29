"""
Self-Healing Engine for CORTEX 4.0

Provides automatic error recovery strategies for autonomous execution:
- Retry with exponential backoff
- Alternative approach attempts
- Rollback and retry

Phase 0.5 Component
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, List, Optional


class RecoveryStrategy(Enum):
    """Self-healing recovery strategies."""
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    ALTERNATIVE_APPROACH = "alternative_approach"
    ROLLBACK_AND_RETRY = "rollback_and_retry"


@dataclass
class SelfHealingResult:
    """Result of self-healing attempt."""
    success: bool
    strategy: RecoveryStrategy
    attempt: int
    message: str
    recovery_actions: List[str] = field(default_factory=list)
    elapsed_time_seconds: float = 0.0


@dataclass
class ErrorContext:
    """Context for error that needs healing."""
    error_type: str
    error_message: str
    phase_name: str
    attempt_count: int
    is_transient: bool = False  # Network issues, flaky tests
    is_validation_error: bool = False  # Test failures
    is_breaking_change: bool = False  # Integration failures
    is_critical: bool = False  # Data loss risk


class SelfHealingEngine:
    """
    Self-healing engine for automatic error recovery.
    
    Strategies:
    1. retry_with_backoff: Exponential backoff for transient errors (1s, 2s, 4s)
    2. alternative_approach: Try different implementation for validation errors (max 2 attempts)
    3. rollback_and_retry: Rollback changes and retry for breaking changes (max 1 attempt)
    
    Usage:
        engine = SelfHealingEngine(logger, max_attempts=3)
        result = engine.attempt_recovery(
            operation=lambda: run_tests(),
            error_context=ErrorContext(
                error_type="TestFailure",
                error_message="5/10 tests failed",
                phase_name="Phase 1",
                attempt_count=1,
                is_validation_error=True
            )
        )
    """
    
    def __init__(
        self,
        logger: logging.Logger,
        max_attempts: int = 3,
        enable_recovery: bool = True
    ):
        """
        Initialize self-healing engine.
        
        Args:
            logger: Logger instance
            max_attempts: Maximum recovery attempts per operation
            enable_recovery: Enable self-healing (False = fail immediately)
        """
        self.logger = logger
        self.max_attempts = max_attempts
        self.enable_recovery = enable_recovery
    
    def attempt_recovery(
        self,
        operation: Callable[[], Any],
        error_context: ErrorContext,
        rollback_fn: Optional[Callable[[], bool]] = None
    ) -> SelfHealingResult:
        """
        Attempt recovery for failed operation.
        
        Args:
            operation: Operation to retry (lambda or function)
            error_context: Error context with metadata
            rollback_fn: Optional rollback function
        
        Returns:
            SelfHealingResult with recovery outcome
        """
        if not self.enable_recovery:
            return SelfHealingResult(
                success=False,
                strategy=RecoveryStrategy.RETRY_WITH_BACKOFF,
                attempt=0,
                message="Self-healing disabled"
            )
        
        # Check attempt threshold
        if error_context.attempt_count >= self.max_attempts:
            return SelfHealingResult(
                success=False,
                strategy=RecoveryStrategy.RETRY_WITH_BACKOFF,
                attempt=error_context.attempt_count,
                message=f"Max attempts ({self.max_attempts}) exceeded"
            )
        
        # Select recovery strategy
        strategy = self._select_strategy(error_context)
        
        self.logger.info(f"🔧 Self-healing attempt {error_context.attempt_count}/{self.max_attempts}")
        self.logger.info(f"   Strategy: {strategy.value}")
        
        # Execute recovery
        start_time = time.time()
        
        if strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
            result = self._retry_with_backoff(operation, error_context)
        
        elif strategy == RecoveryStrategy.ALTERNATIVE_APPROACH:
            result = self._alternative_approach(operation, error_context)
        
        elif strategy == RecoveryStrategy.ROLLBACK_AND_RETRY:
            result = self._rollback_and_retry(operation, error_context, rollback_fn)
        
        else:
            result = SelfHealingResult(
                success=False,
                strategy=strategy,
                attempt=error_context.attempt_count,
                message="Unknown recovery strategy"
            )
        
        result.elapsed_time_seconds = time.time() - start_time
        
        if result.success:
            self.logger.info(f"   ✅ Recovery successful ({result.elapsed_time_seconds:.1f}s)")
        else:
            self.logger.warning(f"   ❌ Recovery failed ({result.elapsed_time_seconds:.1f}s)")
        
        return result
    
    def _select_strategy(self, error_context: ErrorContext) -> RecoveryStrategy:
        """
        Select recovery strategy based on error type.
        
        Rules:
        - Transient errors → retry_with_backoff
        - Validation errors → alternative_approach
        - Breaking changes → rollback_and_retry
        """
        if error_context.is_transient:
            return RecoveryStrategy.RETRY_WITH_BACKOFF
        
        if error_context.is_validation_error:
            return RecoveryStrategy.ALTERNATIVE_APPROACH
        
        if error_context.is_breaking_change:
            return RecoveryStrategy.ROLLBACK_AND_RETRY
        
        # Default: retry with backoff
        return RecoveryStrategy.RETRY_WITH_BACKOFF
    
    def _retry_with_backoff(
        self,
        operation: Callable[[], Any],
        error_context: ErrorContext
    ) -> SelfHealingResult:
        """
        Retry operation with exponential backoff.
        
        Backoff: 1s, 2s, 4s (exponential)
        Max attempts: 3
        """
        wait_time = 2 ** (error_context.attempt_count - 1)  # 1s, 2s, 4s
        
        self.logger.info(f"   ⏳ Waiting {wait_time}s before retry...")
        time.sleep(wait_time)
        
        try:
            # Retry operation
            operation()
            
            return SelfHealingResult(
                success=True,
                strategy=RecoveryStrategy.RETRY_WITH_BACKOFF,
                attempt=error_context.attempt_count,
                message="Retry succeeded after backoff",
                recovery_actions=[f"Waited {wait_time}s", "Retried operation"]
            )
        
        except Exception as e:
            return SelfHealingResult(
                success=False,
                strategy=RecoveryStrategy.RETRY_WITH_BACKOFF,
                attempt=error_context.attempt_count,
                message=f"Retry failed: {str(e)}",
                recovery_actions=[f"Waited {wait_time}s", "Retried operation", "Failed again"]
            )
    
    def _alternative_approach(
        self,
        operation: Callable[[], Any],
        error_context: ErrorContext
    ) -> SelfHealingResult:
        """
        Try alternative implementation approach.
        
        For validation errors (test failures), this could:
        1. Run with different parameters
        2. Skip non-critical tests
        3. Use alternative validation method
        
        Max attempts: 2
        """
        if error_context.attempt_count > 2:
            return SelfHealingResult(
                success=False,
                strategy=RecoveryStrategy.ALTERNATIVE_APPROACH,
                attempt=error_context.attempt_count,
                message="Max alternative attempts (2) exceeded"
            )
        
        self.logger.info("   🔄 Trying alternative approach...")
        
        # In production, this would apply alternative implementation
        # For Phase 0.5, we simulate (always fails)
        
        return SelfHealingResult(
            success=False,
            strategy=RecoveryStrategy.ALTERNATIVE_APPROACH,
            attempt=error_context.attempt_count,
            message="Alternative approach not implemented (Phase 0.5)",
            recovery_actions=["Analyzed failure", "No alternative available"]
        )
    
    def _rollback_and_retry(
        self,
        operation: Callable[[], Any],
        error_context: ErrorContext,
        rollback_fn: Optional[Callable[[], bool]]
    ) -> SelfHealingResult:
        """
        Rollback changes and retry operation.
        
        For breaking changes or integration failures.
        Max attempts: 1
        """
        if error_context.attempt_count > 1:
            return SelfHealingResult(
                success=False,
                strategy=RecoveryStrategy.ROLLBACK_AND_RETRY,
                attempt=error_context.attempt_count,
                message="Max rollback attempts (1) exceeded"
            )
        
        self.logger.info("   ↩️  Rolling back and retrying...")
        
        # Attempt rollback
        if rollback_fn:
            try:
                rollback_success = rollback_fn()
                if not rollback_success:
                    return SelfHealingResult(
                        success=False,
                        strategy=RecoveryStrategy.ROLLBACK_AND_RETRY,
                        attempt=error_context.attempt_count,
                        message="Rollback failed",
                        recovery_actions=["Attempted rollback", "Rollback failed"]
                    )
            except Exception as e:
                return SelfHealingResult(
                    success=False,
                    strategy=RecoveryStrategy.ROLLBACK_AND_RETRY,
                    attempt=error_context.attempt_count,
                    message=f"Rollback error: {str(e)}",
                    recovery_actions=["Attempted rollback", f"Rollback error: {str(e)}"]
                )
        
        # Retry operation after rollback
        try:
            operation()
            
            return SelfHealingResult(
                success=True,
                strategy=RecoveryStrategy.ROLLBACK_AND_RETRY,
                attempt=error_context.attempt_count,
                message="Retry succeeded after rollback",
                recovery_actions=["Rolled back changes", "Retried operation", "Success"]
            )
        
        except Exception as e:
            return SelfHealingResult(
                success=False,
                strategy=RecoveryStrategy.ROLLBACK_AND_RETRY,
                attempt=error_context.attempt_count,
                message=f"Retry failed after rollback: {str(e)}",
                recovery_actions=["Rolled back changes", "Retried operation", "Failed again"]
            )
