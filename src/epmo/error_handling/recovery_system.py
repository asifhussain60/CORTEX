"""
CORTEX 3.0 Recovery System
===========================

Intelligent error recovery system with multiple recovery strategies
and automated retry mechanisms for production resilience.
"""

import time
import asyncio
import random
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import math


logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Recovery strategy types."""
    IMMEDIATE_RETRY = "immediate_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK = "fallback"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    CUSTOM = "custom"


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter_range: float = 0.1  # Add randomness to prevent thundering herd
    timeout_per_attempt: Optional[float] = None
    
    # Conditional retry settings
    retry_on_exceptions: List[type] = field(default_factory=list)
    retry_on_status_codes: List[int] = field(default_factory=list)
    retry_on_predicates: List[Callable] = field(default_factory=list)


@dataclass
class FallbackConfig:
    """Configuration for fallback mechanisms."""
    fallback_function: Optional[Callable] = None
    cached_response: Optional[Any] = None
    default_value: Optional[Any] = None
    error_response: Optional[Dict] = None
    degraded_service: Optional[Callable] = None


@dataclass
class RecoveryResult:
    """Result of a recovery operation."""
    success: bool
    attempts_made: int
    total_time: float
    strategy_used: RecoveryStrategy
    final_result: Any = None
    final_error: Optional[Exception] = None
    recovery_details: Dict[str, Any] = field(default_factory=dict)


class RecoverySystem:
    """
    Intelligent recovery system that provides multiple strategies for
    handling failures and implementing resilient error recovery.
    """
    
    def __init__(
        self,
        default_retry_config: Optional[RetryConfig] = None,
        default_fallback_config: Optional[FallbackConfig] = None,
        enable_metrics: bool = True
    ):
        self.default_retry_config = default_retry_config or RetryConfig()
        self.default_fallback_config = default_fallback_config or FallbackConfig()
        self.enable_metrics = enable_metrics
        
        # Strategy registry
        self._strategies: Dict[RecoveryStrategy, Callable] = {
            RecoveryStrategy.IMMEDIATE_RETRY: self._immediate_retry,
            RecoveryStrategy.EXPONENTIAL_BACKOFF: self._exponential_backoff,
            RecoveryStrategy.LINEAR_BACKOFF: self._linear_backoff,
            RecoveryStrategy.FIXED_DELAY: self._fixed_delay,
            RecoveryStrategy.FALLBACK: self._fallback,
            RecoveryStrategy.GRACEFUL_DEGRADATION: self._graceful_degradation
        }
        
        # Metrics tracking
        self._recovery_metrics: Dict[str, Any] = {
            'total_recoveries': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'strategy_usage': {strategy: 0 for strategy in RecoveryStrategy},
            'avg_recovery_time': 0.0,
            'recovery_times': []
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Recovery callbacks
        self._recovery_callbacks: List[Callable] = []
    
    def recover(
        self,
        func: Callable,
        *args,
        strategy: RecoveryStrategy = RecoveryStrategy.EXPONENTIAL_BACKOFF,
        retry_config: Optional[RetryConfig] = None,
        fallback_config: Optional[FallbackConfig] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> RecoveryResult:
        """
        Attempt to recover from failures using the specified strategy.
        
        Args:
            func: Function to execute with recovery
            *args: Function arguments
            strategy: Recovery strategy to use
            retry_config: Custom retry configuration
            fallback_config: Custom fallback configuration
            context: Additional context for recovery decisions
            **kwargs: Function keyword arguments
            
        Returns:
            RecoveryResult with details of the recovery attempt
        """
        start_time = time.time()
        
        # Use provided configs or defaults
        retry_config = retry_config or self.default_retry_config
        fallback_config = fallback_config or self.default_fallback_config
        context = context or {}
        
        # Update metrics
        with self._lock:
            self._recovery_metrics['total_recoveries'] += 1
            self._recovery_metrics['strategy_usage'][strategy] += 1
        
        try:
            # Execute recovery strategy
            recovery_func = self._strategies.get(strategy, self._exponential_backoff)
            result = recovery_func(
                func, args, kwargs,
                retry_config, fallback_config, context
            )
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Create result
            recovery_result = RecoveryResult(
                success=result.get('success', False),
                attempts_made=result.get('attempts', 0),
                total_time=total_time,
                strategy_used=strategy,
                final_result=result.get('result'),
                final_error=result.get('error'),
                recovery_details=result.get('details', {})
            )
            
            # Update metrics
            with self._lock:
                if recovery_result.success:
                    self._recovery_metrics['successful_recoveries'] += 1
                else:
                    self._recovery_metrics['failed_recoveries'] += 1
                
                self._recovery_metrics['recovery_times'].append(total_time)
                if len(self._recovery_metrics['recovery_times']) > 1000:
                    self._recovery_metrics['recovery_times'] = self._recovery_metrics['recovery_times'][-500:]
                
                if self._recovery_metrics['recovery_times']:
                    self._recovery_metrics['avg_recovery_time'] = (
                        sum(self._recovery_metrics['recovery_times']) / 
                        len(self._recovery_metrics['recovery_times'])
                    )
            
            # Execute callbacks
            for callback in self._recovery_callbacks:
                try:
                    callback(recovery_result)
                except Exception as e:
                    logger.warning(f"Recovery callback error: {e}")
            
            return recovery_result
        
        except Exception as e:
            logger.error(f"Recovery system error: {e}")
            return RecoveryResult(
                success=False,
                attempts_made=0,
                total_time=time.time() - start_time,
                strategy_used=strategy,
                final_error=e
            )
    
    async def recover_async(
        self,
        coro_func: Callable,
        *args,
        strategy: RecoveryStrategy = RecoveryStrategy.EXPONENTIAL_BACKOFF,
        retry_config: Optional[RetryConfig] = None,
        fallback_config: Optional[FallbackConfig] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> RecoveryResult:
        """
        Async version of recover method for coroutines.
        
        Args:
            coro_func: Coroutine function to execute with recovery
            *args: Function arguments
            strategy: Recovery strategy to use
            retry_config: Custom retry configuration
            fallback_config: Custom fallback configuration
            context: Additional context for recovery decisions
            **kwargs: Function keyword arguments
            
        Returns:
            RecoveryResult with details of the recovery attempt
        """
        start_time = time.time()
        
        retry_config = retry_config or self.default_retry_config
        fallback_config = fallback_config or self.default_fallback_config
        context = context or {}
        
        # Update metrics
        with self._lock:
            self._recovery_metrics['total_recoveries'] += 1
            self._recovery_metrics['strategy_usage'][strategy] += 1
        
        try:
            result = await self._async_exponential_backoff(
                coro_func, args, kwargs,
                retry_config, fallback_config, context
            )
            
            total_time = time.time() - start_time
            
            recovery_result = RecoveryResult(
                success=result.get('success', False),
                attempts_made=result.get('attempts', 0),
                total_time=total_time,
                strategy_used=strategy,
                final_result=result.get('result'),
                final_error=result.get('error'),
                recovery_details=result.get('details', {})
            )
            
            # Update metrics
            with self._lock:
                if recovery_result.success:
                    self._recovery_metrics['successful_recoveries'] += 1
                else:
                    self._recovery_metrics['failed_recoveries'] += 1
            
            return recovery_result
        
        except Exception as e:
            logger.error(f"Async recovery system error: {e}")
            return RecoveryResult(
                success=False,
                attempts_made=0,
                total_time=time.time() - start_time,
                strategy_used=strategy,
                final_error=e
            )
    
    def register_recovery_callback(self, callback: Callable[[RecoveryResult], None]) -> None:
        """Register callback for recovery events."""
        self._recovery_callbacks.append(callback)
    
    def get_recovery_metrics(self) -> Dict[str, Any]:
        """Get comprehensive recovery system metrics."""
        with self._lock:
            return {
                'total_recoveries': self._recovery_metrics['total_recoveries'],
                'successful_recoveries': self._recovery_metrics['successful_recoveries'],
                'failed_recoveries': self._recovery_metrics['failed_recoveries'],
                'success_rate': (
                    self._recovery_metrics['successful_recoveries'] / 
                    max(self._recovery_metrics['total_recoveries'], 1) * 100.0
                ),
                'avg_recovery_time': self._recovery_metrics['avg_recovery_time'],
                'strategy_usage': {
                    strategy.value: count 
                    for strategy, count in self._recovery_metrics['strategy_usage'].items()
                }
            }
    
    def _immediate_retry(
        self, 
        func: Callable, 
        args: tuple, 
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: FallbackConfig,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Immediate retry without delay."""
        for attempt in range(retry_config.max_attempts):
            try:
                result = func(*args, **kwargs)
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'details': {'strategy': 'immediate_retry'}
                }
            except Exception as e:
                if not self._should_retry(e, retry_config):
                    break
                
                if attempt == retry_config.max_attempts - 1:
                    return self._handle_final_failure(e, attempt + 1, fallback_config)
        
        return {'success': False, 'attempts': retry_config.max_attempts}
    
    def _exponential_backoff(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: FallbackConfig,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Exponential backoff retry strategy."""
        for attempt in range(retry_config.max_attempts):
            try:
                result = func(*args, **kwargs)
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'details': {'strategy': 'exponential_backoff'}
                }
            except Exception as e:
                if not self._should_retry(e, retry_config):
                    break
                
                if attempt == retry_config.max_attempts - 1:
                    return self._handle_final_failure(e, attempt + 1, fallback_config)
                
                # Calculate delay with exponential backoff
                delay = min(
                    retry_config.initial_delay * (retry_config.backoff_multiplier ** attempt),
                    retry_config.max_delay
                )
                
                # Add jitter to prevent thundering herd
                jitter = random.uniform(-retry_config.jitter_range, retry_config.jitter_range)
                delay = max(0, delay * (1 + jitter))
                
                logger.debug(f"Retrying after {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                time.sleep(delay)
        
        return {'success': False, 'attempts': retry_config.max_attempts}
    
    def _linear_backoff(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: FallbackConfig,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Linear backoff retry strategy."""
        for attempt in range(retry_config.max_attempts):
            try:
                result = func(*args, **kwargs)
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'details': {'strategy': 'linear_backoff'}
                }
            except Exception as e:
                if not self._should_retry(e, retry_config):
                    break
                
                if attempt == retry_config.max_attempts - 1:
                    return self._handle_final_failure(e, attempt + 1, fallback_config)
                
                # Linear increase in delay
                delay = min(
                    retry_config.initial_delay * (attempt + 1),
                    retry_config.max_delay
                )
                
                # Add jitter
                jitter = random.uniform(-retry_config.jitter_range, retry_config.jitter_range)
                delay = max(0, delay * (1 + jitter))
                
                logger.debug(f"Retrying after {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                time.sleep(delay)
        
        return {'success': False, 'attempts': retry_config.max_attempts}
    
    def _fixed_delay(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: FallbackConfig,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fixed delay retry strategy."""
        for attempt in range(retry_config.max_attempts):
            try:
                result = func(*args, **kwargs)
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'details': {'strategy': 'fixed_delay'}
                }
            except Exception as e:
                if not self._should_retry(e, retry_config):
                    break
                
                if attempt == retry_config.max_attempts - 1:
                    return self._handle_final_failure(e, attempt + 1, fallback_config)
                
                # Fixed delay with jitter
                jitter = random.uniform(-retry_config.jitter_range, retry_config.jitter_range)
                delay = max(0, retry_config.initial_delay * (1 + jitter))
                
                logger.debug(f"Retrying after {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                time.sleep(delay)
        
        return {'success': False, 'attempts': retry_config.max_attempts}
    
    def _fallback(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: FallbackConfig,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback strategy - try main function once, then fallback."""
        try:
            result = func(*args, **kwargs)
            return {
                'success': True,
                'result': result,
                'attempts': 1,
                'details': {'strategy': 'fallback', 'used_primary': True}
            }
        except Exception as e:
            logger.warning(f"Primary function failed, using fallback: {e}")
            
            # Try fallback mechanisms
            if fallback_config.fallback_function:
                try:
                    fallback_result = fallback_config.fallback_function(*args, **kwargs)
                    return {
                        'success': True,
                        'result': fallback_result,
                        'attempts': 1,
                        'details': {'strategy': 'fallback', 'used_fallback_function': True}
                    }
                except Exception as fallback_error:
                    logger.error(f"Fallback function also failed: {fallback_error}")
            
            # Use cached response if available
            if fallback_config.cached_response is not None:
                return {
                    'success': True,
                    'result': fallback_config.cached_response,
                    'attempts': 1,
                    'details': {'strategy': 'fallback', 'used_cached_response': True}
                }
            
            # Use default value
            if fallback_config.default_value is not None:
                return {
                    'success': True,
                    'result': fallback_config.default_value,
                    'attempts': 1,
                    'details': {'strategy': 'fallback', 'used_default_value': True}
                }
            
            # Use error response
            if fallback_config.error_response is not None:
                return {
                    'success': False,
                    'result': fallback_config.error_response,
                    'attempts': 1,
                    'error': e,
                    'details': {'strategy': 'fallback', 'used_error_response': True}
                }
            
            return {'success': False, 'attempts': 1, 'error': e}
    
    def _graceful_degradation(
        self,
        func: Callable,
        args: tuple,
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: FallbackConfig,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Graceful degradation strategy."""
        try:
            result = func(*args, **kwargs)
            return {
                'success': True,
                'result': result,
                'attempts': 1,
                'details': {'strategy': 'graceful_degradation', 'full_service': True}
            }
        except Exception as e:
            logger.warning(f"Full service failed, attempting degraded service: {e}")
            
            # Try degraded service
            if fallback_config.degraded_service:
                try:
                    degraded_result = fallback_config.degraded_service(*args, **kwargs)
                    return {
                        'success': True,
                        'result': degraded_result,
                        'attempts': 1,
                        'details': {'strategy': 'graceful_degradation', 'degraded_service': True}
                    }
                except Exception as degraded_error:
                    logger.error(f"Degraded service also failed: {degraded_error}")
            
            # Fall back to minimal service (default value or cached response)
            if fallback_config.default_value is not None:
                return {
                    'success': True,
                    'result': fallback_config.default_value,
                    'attempts': 1,
                    'details': {'strategy': 'graceful_degradation', 'minimal_service': True}
                }
            
            return {'success': False, 'attempts': 1, 'error': e}
    
    async def _async_exponential_backoff(
        self,
        coro_func: Callable,
        args: tuple,
        kwargs: dict,
        retry_config: RetryConfig,
        fallback_config: FallbackConfig,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Async exponential backoff retry strategy."""
        for attempt in range(retry_config.max_attempts):
            try:
                if asyncio.iscoroutinefunction(coro_func):
                    result = await coro_func(*args, **kwargs)
                else:
                    result = coro_func(*args, **kwargs)
                
                return {
                    'success': True,
                    'result': result,
                    'attempts': attempt + 1,
                    'details': {'strategy': 'async_exponential_backoff'}
                }
            except Exception as e:
                if not self._should_retry(e, retry_config):
                    break
                
                if attempt == retry_config.max_attempts - 1:
                    return self._handle_final_failure(e, attempt + 1, fallback_config)
                
                # Calculate delay
                delay = min(
                    retry_config.initial_delay * (retry_config.backoff_multiplier ** attempt),
                    retry_config.max_delay
                )
                
                # Add jitter
                jitter = random.uniform(-retry_config.jitter_range, retry_config.jitter_range)
                delay = max(0, delay * (1 + jitter))
                
                logger.debug(f"Async retrying after {delay:.2f}s (attempt {attempt + 1}/{retry_config.max_attempts})")
                await asyncio.sleep(delay)
        
        return {'success': False, 'attempts': retry_config.max_attempts}
    
    def _should_retry(self, exception: Exception, retry_config: RetryConfig) -> bool:
        """Determine if an exception should trigger a retry."""
        # Check specific exception types
        if retry_config.retry_on_exceptions:
            if not any(isinstance(exception, exc_type) for exc_type in retry_config.retry_on_exceptions):
                return False
        
        # Check status codes (for HTTP-like exceptions)
        if retry_config.retry_on_status_codes and hasattr(exception, 'status_code'):
            if exception.status_code not in retry_config.retry_on_status_codes:
                return False
        
        # Check custom predicates
        if retry_config.retry_on_predicates:
            for predicate in retry_config.retry_on_predicates:
                try:
                    if not predicate(exception):
                        return False
                except:
                    return False
        
        return True
    
    def _handle_final_failure(
        self,
        exception: Exception,
        attempts: int,
        fallback_config: FallbackConfig
    ) -> Dict[str, Any]:
        """Handle the final failure after all retries exhausted."""
        logger.error(f"All retry attempts failed after {attempts} tries: {exception}")
        
        # Try fallback mechanisms even after retries fail
        if fallback_config.fallback_function:
            try:
                fallback_result = fallback_config.fallback_function()
                return {
                    'success': True,
                    'result': fallback_result,
                    'attempts': attempts,
                    'details': {'used_fallback_after_retries': True}
                }
            except Exception as fallback_error:
                logger.error(f"Final fallback also failed: {fallback_error}")
        
        if fallback_config.default_value is not None:
            return {
                'success': True,
                'result': fallback_config.default_value,
                'attempts': attempts,
                'details': {'used_default_after_retries': True}
            }
        
        return {
            'success': False,
            'attempts': attempts,
            'error': exception,
            'details': {'all_recovery_methods_exhausted': True}
        }


# Global recovery system instance
default_recovery_system = RecoverySystem()