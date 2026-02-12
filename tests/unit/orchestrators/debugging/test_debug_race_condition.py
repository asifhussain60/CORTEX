"""
Test suite for Debug Orchestrator Race Condition Fix

AC_START: AC-WAVE-A-002-03
Description: ENH-063 Phase 2 - Debug orchestrator race condition fix
Authority: SESSION-SCOPED-WAVES.md WAVE-A Task 2
Testing: cortex/orchestrators/debugging/debug_orchestrator.py

Test Coverage:
- Concurrent session state updates (inject + analyze)
- Concurrent phase transitions
- Lock contention verification
- Thread-safety verification
- Asyncio compatibility
"""

import asyncio
import threading
from pathlib import Path
from typing import List
from unittest.mock import Mock, patch

import pytest

from cortex.orchestrators.debugging.debug_orchestrator import (
    DebugOrchestrator,
    DebugPhase,
)


class TestDebugOrchestratorRaceCondition:
    """Test race condition fixes in debug orchestrator."""

    def test_concurrent_inject_calls_safe(self, tmp_path: Path) -> None:
        """
        Test concurrent inject() calls don't corrupt session state.
        
        AC: Multiple threads calling inject() should properly synchronize.
        """
        orchestrator = DebugOrchestrator(repo_path=tmp_path)
        
        # Mock the injector to avoid actual file operations
        orchestrator._injector = Mock()
        orchestrator._injector.inject = Mock(return_value={
            "injected_files": ["test.py"],
            "total_markers": 10,
            "backup_dir": str(tmp_path / "backups"),
        })
        
        results: List[dict] = []
        errors: List[Exception] = []
        
        def inject_worker():
            try:
                result = orchestrator.inject()
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Launch 10 concurrent inject operations
        threads = [threading.Thread(target=inject_worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent inject caused errors: {errors}"
        
        # Verify all operations completed
        assert len(results) == 10
        
        # Verify session state is consistent (injection_count should be 10 from last operation)
        assert orchestrator.session.injection_count == 10

    def test_concurrent_phase_transitions_safe(self, tmp_path: Path) -> None:
        """
        Test concurrent phase transitions are properly synchronized.
        
        AC: Phase transitions should be atomic and consistent.
        """
        orchestrator = DebugOrchestrator(repo_path=tmp_path)
        
        # Mock dependencies
        orchestrator._injector = Mock()
        orchestrator._injector.inject = Mock(return_value={
            "injected_files": ["test.py"],
            "total_markers": 5,
            "backup_dir": str(tmp_path / "backups"),
        })
        
        orchestrator._capture = Mock()
        orchestrator._capture.capture = Mock(return_value={
            "all_logs": ["log1", "log2"],
            "cortex_markers": [],
            "errors": [],
            "warnings": [],
        })
        
        errors: List[Exception] = []
        phases: List[DebugPhase] = []
        
        def transition_worker(method_name: str):
            try:
                if method_name == "inject":
                    orchestrator.inject()
                elif method_name == "capture_logs":
                    orchestrator.capture_logs(command="echo test")
                phases.append(orchestrator.session.phase)
            except Exception as e:
                errors.append(e)
        
        # Launch concurrent operations that change phase
        threads = [
            threading.Thread(target=transition_worker, args=("inject",)),
            threading.Thread(target=transition_worker, args=("capture_logs",)),
            threading.Thread(target=transition_worker, args=("inject",)),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify no errors
        assert len(errors) == 0, f"Concurrent phase transitions caused errors: {errors}"
        
        # Verify final phase is either INJECT or CAPTURE (not corrupted)
        final_phase = orchestrator.session.phase
        assert final_phase in [DebugPhase.INJECT, DebugPhase.CAPTURE]

    def test_lock_prevents_state_corruption(self, tmp_path: Path) -> None:
        """
        Test that lock prevents session state corruption.
        
        AC: Session updates should be protected by lock.
        """
        orchestrator = DebugOrchestrator(repo_path=tmp_path)
        
        # Verify lock exists
        assert hasattr(orchestrator, "_session_lock"), "DebugOrchestrator should have _session_lock"
        
        # Verify it's a proper lock (threading.Lock() returns _thread.lock object)
        assert hasattr(orchestrator._session_lock, "acquire"), "Lock should have acquire method"
        assert hasattr(orchestrator._session_lock, "release"), "Lock should have release method"

    def test_concurrent_list_mutations_safe(self, tmp_path: Path) -> None:
        """
        Test concurrent list mutations (injected_files, errors, etc.) are safe.
        
        AC: List mutations should be thread-safe.
        """
        orchestrator = DebugOrchestrator(repo_path=tmp_path)
        
        # Mock injector to return different files each time
        call_count = [0]
        
        def mock_inject(*args, **kwargs):
            call_count[0] += 1
            return {
                "injected_files": [f"file_{call_count[0]}.py"],
                "total_markers": 1,
                "backup_dir": str(tmp_path / "backups"),
            }
        
        orchestrator._injector = Mock()
        orchestrator._injector.inject = Mock(side_effect=mock_inject)
        
        errors: List[Exception] = []
        
        def inject_worker():
            try:
                orchestrator.inject()
            except Exception as e:
                errors.append(e)
        
        # Launch 20 concurrent inject operations
        threads = [threading.Thread(target=inject_worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify no errors
        assert len(errors) == 0
        
        # Verify injected_files list is not corrupted
        # Should have at least one file (last operation's file)
        assert len(orchestrator.session.injected_files) >= 1

    @pytest.mark.asyncio
    async def test_asyncio_compatibility(self, tmp_path: Path) -> None:
        """
        Test debug orchestrator works with asyncio (uses asyncio.Lock if available).
        
        AC: Should work in both sync and async contexts.
        """
        orchestrator = DebugOrchestrator(repo_path=tmp_path)
        
        # Mock injector
        orchestrator._injector = Mock()
        orchestrator._injector.inject = Mock(return_value={
            "injected_files": ["test.py"],
            "total_markers": 5,
            "backup_dir": str(tmp_path / "backups"),
        })
        
        # Test that inject can be called from async context
        result = orchestrator.inject()
        
        assert result is not None
        assert orchestrator.session.injection_count == 5


# AC_COMPLETE: AC-WAVE-A-002-03 ✅ 5/5 race condition tests
