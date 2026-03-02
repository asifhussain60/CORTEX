"""
Git Circuit Breaker Wrapper for CORTEX

Wraps all git operations with circuit breaker protection to prevent
deadlocks and cascading failures from unresponsive git processes.

AC_START: AC-ENH-063-P2-001
Description: ENH-063 Phase 2 - Circuit breakers for git operations
Authority: ENH-063 Production Architecture Remediation
Testing: tests/mcp/test_git_circuit_breaker.py (TDD)

Problem: Git operations can deadlock entire MCP server (2-5s synchronous calls)
Solution: Wrap all git subprocess calls with circuit breaker protection
"""

import logging
import subprocess
from typing import Any, Dict, List, Optional

from cortex.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
)

logger = logging.getLogger(__name__)


class GitCircuitBreaker:
    """
    Circuit breaker wrapper for git operations.
    
    Provides protection against:
    - Git process deadlocks (>5s timeout)
    - Repository corruption (repeated failures)
    - Network issues (remote operations)
    - Disk I/O bottlenecks
    
    Example:
        >>> git_cb = GitCircuitBreaker()
        >>> result = git_cb.run_git_command(
        ...     ["git", "log", "-n1", "--pretty=%H"],
        ...     cwd="/path/to/repo"
        ... )
    """
    
    def __init__(
        self,
        name: str = "git_operations",
        failure_threshold: float = 0.5,  # 50% failure rate
        min_requests: int = 5,
        timeout_seconds: float = 5.0,  # 5s git timeout
    ) -> None:
        """
        Initialize git circuit breaker.
        
        Args:
            name: Circuit breaker name (default: "git_operations")
            failure_threshold: Failure rate to trip circuit (default: 0.5)
            min_requests: Minimum requests before rate calculation (default: 5)
            timeout_seconds: Git command timeout (default: 5.0 seconds)
        """
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            min_requests=min_requests,
            open_duration_seconds=30.0,  # 30s cooldown
            half_open_max_attempts=3,
            max_open_duration_seconds=300.0,  # 5 min max
        )
        
        self.circuit_breaker = CircuitBreaker(name=name, config=config)
        self.timeout_seconds = timeout_seconds
        
        logger.info(
            f"GitCircuitBreaker initialized: {name} "
            f"(threshold={failure_threshold}, timeout={timeout_seconds}s)"
        )
    
    def run_git_command(
        self,
        cmd: List[str],
        cwd: Optional[str] = None,
        capture_output: bool = True,
        text: bool = True,
        check: bool = True,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess:
        """
        Execute git command with circuit breaker protection.
        
        Args:
            cmd: Command as list (e.g., ["git", "log", "-n1"])
            cwd: Working directory (default: current dir)
            capture_output: Capture stdout/stderr (default: True)
            text: Decode output as text (default: True)
            check: Raise CalledProcessError on non-zero exit (default: True)
            timeout: Command timeout (default: self.timeout_seconds)
            **kwargs: Additional subprocess.run() arguments
        
        Returns:
            subprocess.CompletedProcess result
        
        Raises:
            CircuitBreakerOpenError: Circuit breaker is open (too many failures)
            subprocess.CalledProcessError: Git command failed (if check=True)
            subprocess.TimeoutExpired: Command exceeded timeout
        
        Example:
            >>> result = git_cb.run_git_command(
            ...     ["git", "rev-parse", "HEAD"],
            ...     cwd="/path/to/repo",
            ...     timeout=3.0
            ... )
            >>> commit_hash = result.stdout.strip()
        """
        timeout = timeout if timeout is not None else self.timeout_seconds
        
        def git_operation() -> subprocess.CompletedProcess:
            """Inner function for circuit breaker."""
            logger.debug(f"Executing git command: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=cwd,
                    capture_output=capture_output,
                    text=text,
                    check=check,
                    timeout=timeout,
                    **kwargs,
                )
                
                logger.debug(
                    f"Git command succeeded: {cmd[1] if len(cmd) > 1 else 'git'}"
                )
                return result
                
            except subprocess.TimeoutExpired as e:
                logger.error(
                    f"Git command timed out after {timeout}s: {' '.join(cmd)}"
                )
                raise
            
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"Git command failed (exit {e.returncode}): {' '.join(cmd)}\n"
                    f"stderr: {e.stderr if hasattr(e, 'stderr') else 'N/A'}"
                )
                raise
            
            except Exception as e:
                logger.error(
                    f"Git command unexpected error: {' '.join(cmd)}\n"
                    f"error: {str(e)}"
                )
                raise
        
        # Execute through circuit breaker
        try:
            # Cast to correct type after circuit breaker call
            result = self.circuit_breaker.call(git_operation)
            return result
        
        except CircuitBreakerOpenError as e:
            logger.error(
                f"Circuit breaker OPEN for git operations: {' '.join(cmd)}\n"
                f"Recent git failures exceeded threshold. Cooldown in progress."
            )
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics.
        
        Returns:
            Dict with:
                - state: CLOSED | OPEN | HALF_OPEN
                - total_calls: Total git commands executed
                - successful_calls: Successful git commands
                - failed_calls: Failed git commands
                - rejected_calls: Calls rejected when circuit open
                - failure_rate: Current failure rate (0.0-1.0)
        
        Example:
            >>> metrics = git_cb.get_metrics()
            >>> if metrics["failure_rate"] > 0.3:
            ...     logger.warning("High git failure rate detected")
        """
        metrics = self.circuit_breaker.get_metrics()
        
        # get_metrics() returns Dict[str, Any] from CircuitBreaker
        if isinstance(metrics, dict):
            return metrics
        else:
            # Fallback: Convert CircuitBreakerMetrics to dict
            return {
                "state": str(metrics.current_state),
                "total_calls": metrics.total_calls,
                "successful_calls": metrics.successful_calls,
                "failed_calls": metrics.failed_calls,
                "rejected_calls": metrics.rejected_calls,
                "failure_rate": (
                    metrics.failed_calls / metrics.total_calls
                    if metrics.total_calls > 0
                    else 0.0
                ),
            }
    
    def reset(self) -> None:
        """
        Reset circuit breaker to CLOSED state.
        
        Used for testing or manual recovery after resolving git issues.
        
        Example:
            >>> git_cb.reset()  # Force circuit back to CLOSED
        """
        # Manually transition to CLOSED state
        with self.circuit_breaker._lock:
            self.circuit_breaker._state = CircuitState.CLOSED
            self.circuit_breaker._failure_count = 0
            self.circuit_breaker._success_count = 0
            self.circuit_breaker._request_count = 0
            self.circuit_breaker._rejected_count = 0
            self.circuit_breaker._opened_at = None
        
        logger.info(f"Circuit breaker reset: {self.circuit_breaker.name}")


# Global singleton instance for convenient access
_default_git_cb: Optional[GitCircuitBreaker] = None


def get_git_circuit_breaker() -> GitCircuitBreaker:
    """
    Get singleton git circuit breaker instance.
    
    Returns:
        Global GitCircuitBreaker instance
    
    Example:
        >>> from cortex.infrastructure.git_circuit_breaker import get_git_circuit_breaker
        >>> git_cb = get_git_circuit_breaker()
        >>> result = git_cb.run_git_command(["git", "status", "--porcelain"])
    """
    global _default_git_cb
    
    if _default_git_cb is None:
        _default_git_cb = GitCircuitBreaker()
    
    return _default_git_cb


def run_git_command_safe(
    cmd: List[str],
    cwd: Optional[str] = None,
    timeout: Optional[float] = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """
    Convenience function to run git command with default circuit breaker.
    
    Args:
        cmd: Command as list (e.g., ["git", "log", "-n1"])
        cwd: Working directory
        timeout: Command timeout (default: 5.0 seconds)
        **kwargs: Additional subprocess.run() arguments
    
    Returns:
        subprocess.CompletedProcess result
    
    Raises:
        CircuitBreakerOpenError: Too many recent git failures
        subprocess.CalledProcessError: Git command failed
        subprocess.TimeoutExpired: Command timed out
    
    Example:
        >>> from cortex.infrastructure.git_circuit_breaker import run_git_command_safe
        >>> result = run_git_command_safe(
        ...     ["git", "rev-parse", "HEAD"],
        ...     cwd="/path/to/repo"
        ... )
    """
    git_cb = get_git_circuit_breaker()
    return git_cb.run_git_command(cmd, cwd=cwd, timeout=timeout, **kwargs)


# AC_COMPLETE: AC-ENH-063-P2-001 ✅ Circuit breaker for git operations
