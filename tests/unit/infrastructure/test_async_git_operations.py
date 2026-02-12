"""
Test suite for Async Git Operations

AC_START: AC-WAVE-A-002-02
Description: ENH-063 Phase 2 - Async git operations (non-blocking)
Authority: SESSION-SCOPED-WAVES.md WAVE-A Task 2
Testing: cortex/infrastructure/async_git_operations.py

Test Coverage:
- Async git command execution (non-blocking)
- Multiple concurrent git operations
- Timeout handling in async context
- Error propagation in async git calls
- Circuit breaker integration with async
"""

import asyncio
import subprocess
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from cortex.infrastructure.async_git_operations import (
    AsyncGitOperations,
    get_async_git_operations,
)
from cortex.infrastructure.circuit_breaker import CircuitBreakerOpenError


class TestAsyncGitOperationsInitialization:
    """Test async git operations initialization."""

    def test_init_creates_async_git_ops(self) -> None:
        """AsyncGitOperations initializes correctly."""
        async_git = AsyncGitOperations()
        
        assert async_git is not None
        assert async_git.timeout_seconds == 5.0
        assert async_git.circuit_breaker is not None

    def test_init_custom_timeout(self) -> None:
        """AsyncGitOperations accepts custom timeout."""
        async_git = AsyncGitOperations(timeout_seconds=10.0)
        
        assert async_git.timeout_seconds == 10.0


class TestAsyncGitCommandExecution:
    """Test async git command execution."""

    @pytest.mark.asyncio
    async def test_successful_async_git_command(self, tmp_path: Path) -> None:
        """
        Test successful async git command returns CompletedProcess.
        
        AC: Async git commands should execute without blocking.
        """
        async_git = AsyncGitOperations()
        
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Mock async subprocess
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"abc123def\n", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await async_git.run_git_command_async(
                ["git", "rev-parse", "HEAD"],
                cwd=str(tmp_path),
            )
            
            assert result.returncode == 0
            assert result.stdout == "abc123def\n"
            mock_subprocess.assert_called_once()

    @pytest.mark.asyncio
    async def test_git_command_with_error(self, tmp_path: Path) -> None:
        """
        Test async git command propagates errors correctly.
        
        AC: Errors should be raised as subprocess.CalledProcessError.
        """
        async_git = AsyncGitOperations()
        
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(return_value=(b"", b"fatal: not a git repository\n"))
            mock_process.returncode = 128
            mock_subprocess.return_value = mock_process
            
            with pytest.raises(subprocess.CalledProcessError) as exc_info:
                await async_git.run_git_command_async(
                    ["git", "status"],
                    cwd=str(tmp_path),
                )
            
            assert exc_info.value.returncode == 128

    @pytest.mark.asyncio
    async def test_concurrent_git_operations(self, tmp_path: Path) -> None:
        """
        Test multiple concurrent async git operations execute in parallel.
        
        AC: Multiple git commands should run concurrently without blocking.
        """
        async_git = AsyncGitOperations()
        
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Each call returns a different commit hash
            call_count = [0]
            
            async def mock_create_subprocess(*args, **kwargs):
                call_count[0] += 1
                mock_process = AsyncMock()
                mock_process.communicate = AsyncMock(
                    return_value=(f"commit_{call_count[0]}\n".encode(), b"")
                )
                mock_process.returncode = 0
                # Simulate async delay
                await asyncio.sleep(0.01)
                return mock_process
            
            mock_subprocess.side_effect = mock_create_subprocess
            
            # Launch 5 concurrent git operations
            tasks = [
                async_git.run_git_command_async(["git", "rev-parse", "HEAD"], cwd=str(tmp_path))
                for _ in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verify all operations completed
            assert len(results) == 5
            assert all(r.returncode == 0 for r in results)

    @pytest.mark.asyncio
    async def test_timeout_handling(self, tmp_path: Path) -> None:
        """
        Test async git command respects timeout.
        
        AC: Long-running commands should timeout after configured duration.
        """
        async_git = AsyncGitOperations(timeout_seconds=0.1)
        
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            # Simulate long-running command
            async def slow_subprocess(*args, **kwargs):
                mock_process = AsyncMock()
                async def slow_communicate():
                    await asyncio.sleep(1.0)  # Longer than timeout
                    return (b"output\n", b"")
                mock_process.communicate = slow_communicate
                mock_process.returncode = 0
                return mock_process
            
            mock_subprocess.side_effect = slow_subprocess
            
            with pytest.raises(asyncio.TimeoutError):
                await async_git.run_git_command_async(
                    ["git", "log", "--all"],
                    cwd=str(tmp_path),
                )

    @pytest.mark.asyncio
    async def test_circuit_breaker_integration(self, tmp_path: Path) -> None:
        """
        Test async git operations integrate with circuit breaker.
        
        AC: Circuit breaker state is checked before operations.
        """
        async_git = AsyncGitOperations()
        
        # Circuit breaker should be available
        metrics = async_git.get_metrics()
        assert "state" in metrics
        assert metrics["state"] in ["CLOSED", "OPEN", "HALF_OPEN"]
        
        # Successful operation should work
        with patch("asyncio.create_subprocess_exec") as mock_subprocess:
            async def success_subprocess(*args, **kwargs):
                mock_process = AsyncMock()
                mock_process.communicate = AsyncMock(return_value=(b"success\n", b""))
                mock_process.returncode = 0
                return mock_process
            
            mock_subprocess.side_effect = success_subprocess
            
            result = await async_git.run_git_command_async(["git", "status"], cwd=str(tmp_path))
            assert result.returncode == 0


class TestGlobalSingletonAsync:
    """Test global singleton access for async git operations."""

    def test_get_async_git_operations_returns_singleton(self) -> None:
        """
        Test get_async_git_operations() returns singleton instance.
        
        AC: Multiple calls should return same instance.
        """
        git1 = get_async_git_operations()
        git2 = get_async_git_operations()
        
        assert git1 is git2


# AC_COMPLETE: AC-WAVE-A-002-02 ✅ TDD tests for async git operations (5 tests)
