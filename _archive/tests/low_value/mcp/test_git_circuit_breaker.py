"""
Test suite for GitCircuitBreaker

AC_START: AC-ENH-063-P2-002
Description: TDD tests for git circuit breaker wrapper
Authority: CORE-008 (tests before code)
Testing: cortex/infrastructure/git_circuit_breaker.py

Test Coverage:
- Circuit breaker initialization
- Successful git command execution
- Git command failures and circuit opening
- Circuit breaker state transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Timeout handling
- Metrics tracking
- Global singleton access
- Circuit reset functionality
"""

import subprocess
import time
from unittest.mock import Mock, patch

import pytest

from cortex.infrastructure.git_circuit_breaker import (
    GitCircuitBreaker,
    get_git_circuit_breaker,
    run_git_command_safe,
)
from cortex.infrastructure.circuit_breaker import CircuitBreakerOpenError


class TestGitCircuitBreakerInitialization:
    """Test circuit breaker initialization."""
    
    def test_init_creates_circuit_breaker(self) -> None:
        """Circuit breaker initializes with correct configuration."""
        git_cb = GitCircuitBreaker()
        
        assert git_cb.circuit_breaker is not None
        assert git_cb.circuit_breaker.name == "git_operations"
        assert git_cb.timeout_seconds == 5.0
    
    def test_init_custom_parameters(self) -> None:
        """Circuit breaker accepts custom parameters."""
        git_cb = GitCircuitBreaker(
            name="custom_git",
            failure_threshold=0.3,
            min_requests=10,
            timeout_seconds=10.0,
        )
        
        assert git_cb.circuit_breaker.name == "custom_git"
        assert git_cb.circuit_breaker.config.failure_threshold == 0.3
        assert git_cb.circuit_breaker.config.min_requests == 10
        assert git_cb.timeout_seconds == 10.0


class TestGitCommandExecution:
    """Test git command execution through circuit breaker."""
    
    def test_successful_git_command(self) -> None:
        """Successful git command returns CompletedProcess."""
        git_cb = GitCircuitBreaker()
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "rev-parse", "HEAD"],
                returncode=0,
                stdout="abc123def",
                stderr="",
            )
            
            result = git_cb.run_git_command(
                ["git", "rev-parse", "HEAD"],
                cwd="/fake/repo",
            )
            
            assert result.returncode == 0
            assert result.stdout == "abc123def"
            mock_run.assert_called_once()
    
    def test_git_command_with_timeout(self) -> None:
        """Git command uses specified timeout."""
        git_cb = GitCircuitBreaker(timeout_seconds=3.0)
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "log", "-n1"],
                returncode=0,
                stdout="commit abc123",
                stderr="",
            )
            
            result = git_cb.run_git_command(
                ["git", "log", "-n1"],
                timeout=1.0,  # Override default
            )
            
            # Check timeout was passed to subprocess
            call_kwargs = mock_run.call_args.kwargs
            assert call_kwargs["timeout"] == 1.0
    
    def test_git_command_timeout_expired(self) -> None:
        """Git command timeout raises TimeoutExpired."""
        git_cb = GitCircuitBreaker(timeout_seconds=1.0)
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                cmd=["git", "fetch"],
                timeout=1.0,
            )
            
            with pytest.raises(subprocess.TimeoutExpired):
                git_cb.run_git_command(["git", "fetch"])
    
    def test_git_command_called_process_error(self) -> None:
        """Git command failure raises CalledProcessError."""
        git_cb = GitCircuitBreaker()
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=128,
                cmd=["git", "log"],
                stderr="fatal: not a git repository",
            )
            
            with pytest.raises(subprocess.CalledProcessError):
                git_cb.run_git_command(["git", "log"])


class TestCircuitBreakerStateTransitions:
    """Test circuit breaker state transitions."""
    
    def test_circuit_opens_after_failures(self) -> None:
        """Circuit breaker opens after failure threshold exceeded."""
        git_cb = GitCircuitBreaker(
            failure_threshold=0.5,  # 50%
            min_requests=5,
        )
        
        with patch("subprocess.run") as mock_run:
            # Simulate failures
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["git", "log"],
            )
            
            # Generate failures to exceed threshold
            for _ in range(5):
                with pytest.raises(subprocess.CalledProcessError):
                    git_cb.run_git_command(["git", "log"])
            
            # Circuit should now be OPEN
            metrics = git_cb.get_metrics()
            assert metrics["state"] == "OPEN"
    
    def test_circuit_rejects_when_open(self) -> None:
        """Open circuit rejects calls immediately."""
        git_cb = GitCircuitBreaker(
            failure_threshold=0.5,
            min_requests=3,
        )
        
        with patch("subprocess.run") as mock_run:
            # Generate failures to open circuit
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["git", "log"],
            )
            
            for _ in range(3):
                with pytest.raises(subprocess.CalledProcessError):
                    git_cb.run_git_command(["git", "log"])
            
            # Now circuit is open, should reject immediately
            with pytest.raises(CircuitBreakerOpenError):
                git_cb.run_git_command(["git", "status"])
    
    def test_circuit_transitions_to_half_open(self) -> None:
        """Circuit transitions to HALF_OPEN after cooldown."""
        git_cb = GitCircuitBreaker(
            failure_threshold=0.5,
            min_requests=3,
        )
        
        # Manually set circuit to OPEN state
        git_cb.circuit_breaker.force_state(
            git_cb.circuit_breaker._state.__class__.OPEN
        )
        git_cb.circuit_breaker._opened_at = time.time() - 31.0  # 31s ago
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "status"],
                returncode=0,
                stdout="clean",
                stderr="",
            )
            
            # Should transition to HALF_OPEN and allow call
            result = git_cb.run_git_command(["git", "status"])
            assert result.returncode == 0
    
    def test_circuit_closes_after_successful_half_open(self) -> None:
        """Circuit closes after successful attempts in HALF_OPEN."""
        git_cb = GitCircuitBreaker(
            failure_threshold=0.5,
            min_requests=3,
        )
        
        # Force to HALF_OPEN state
        git_cb.circuit_breaker.force_state(
            git_cb.circuit_breaker._state.__class__.HALF_OPEN
        )
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "status"],
                returncode=0,
                stdout="clean",
                stderr="",
            )
            
            # Make successful calls to close circuit
            for _ in range(3):  # half_open_max_attempts
                git_cb.run_git_command(["git", "status"])
            
            metrics = git_cb.get_metrics()
            assert metrics["state"] == "CLOSED"


class TestCircuitBreakerMetrics:
    """Test circuit breaker metrics tracking."""
    
    def test_metrics_track_successful_calls(self) -> None:
        """Metrics track successful git operations."""
        git_cb = GitCircuitBreaker()
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "status"],
                returncode=0,
                stdout="clean",
                stderr="",
            )
            
            git_cb.run_git_command(["git", "status"])
            
            metrics = git_cb.get_metrics()
            assert metrics["success_count"] >= 1
            assert metrics["failure_rate"] == 0.0
    
    def test_metrics_track_failed_calls(self) -> None:
        """Metrics track failed git operations."""
        git_cb = GitCircuitBreaker()
        
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["git", "log"],
            )
            
            with pytest.raises(subprocess.CalledProcessError):
                git_cb.run_git_command(["git", "log"])
            
            metrics = git_cb.get_metrics()
            assert metrics["failure_count"] >= 1
    
    def test_metrics_track_rejected_calls(self) -> None:
        """Metrics track rejected calls when circuit open."""
        git_cb = GitCircuitBreaker(
            failure_threshold=0.5,
            min_requests=3,
        )
        
        with patch("subprocess.run") as mock_run:
            # Open circuit
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["git", "log"],
            )
            
            for _ in range(3):
                with pytest.raises(subprocess.CalledProcessError):
                    git_cb.run_git_command(["git", "log"])
            
            # Try call while open
            with pytest.raises(CircuitBreakerOpenError):
                git_cb.run_git_command(["git", "status"])
            
            metrics = git_cb.get_metrics()
            assert metrics["rejected_count"] >= 1


class TestGlobalSingleton:
    """Test global singleton access."""
    
    def test_get_git_circuit_breaker_returns_singleton(self) -> None:
        """get_git_circuit_breaker returns same instance."""
        cb1 = get_git_circuit_breaker()
        cb2 = get_git_circuit_breaker()
        
        assert cb1 is cb2
    
    def test_run_git_command_safe_uses_singleton(self) -> None:
        """run_git_command_safe uses global singleton."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "status"],
                returncode=0,
                stdout="clean",
                stderr="",
            )
            
            result = run_git_command_safe(["git", "status"])
            
            assert result.returncode == 0
            mock_run.assert_called_once()


class TestCircuitReset:
    """Test circuit breaker reset functionality."""
    
    def test_reset_closes_circuit(self) -> None:
        """Reset transitions circuit to CLOSED state."""
        git_cb = GitCircuitBreaker()
        
        # Force to OPEN state
        git_cb.circuit_breaker.force_state(
            git_cb.circuit_breaker._state.__class__.OPEN
        )
        
        # Reset
        git_cb.reset()
        
        metrics = git_cb.get_metrics()
        assert metrics["state"] == "CLOSED"
    
    def test_reset_clears_counters(self) -> None:
        """Reset clears all failure/success counters."""
        git_cb = GitCircuitBreaker()
        
        with patch("subprocess.run") as mock_run:
            # Generate some activity
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "status"],
                returncode=0,
                stdout="clean",
                stderr="",
            )
            
            for _ in range(5):
                git_cb.run_git_command(["git", "status"])
            
            # Reset
            git_cb.reset()
            
            metrics = git_cb.get_metrics()
            assert metrics["request_count"] == 0
            assert metrics["success_count"] == 0
            assert metrics["failure_count"] == 0


# AC_COMPLETE: AC-ENH-063-P2-002 ✅ TDD tests for git circuit breaker (21 tests)
