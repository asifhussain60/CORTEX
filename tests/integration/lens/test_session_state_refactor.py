"""
ENH-087 Track 5 Stage 3: Session State Persistence - REFACTOR Phase Tests

Performance profiling and optimization validation for SessionStateOrchestrator.
Verifies that GREEN implementation meets production performance requirements.

AC_START: AC-ENH087-T5-S3-REFACTOR-001
Description: 7 REFACTOR phase tests validating performance + optimization
"""

import pytest
import tempfile
import shutil
import time
from pathlib import Path
from typing import Generator

from cortex.orchestrators.lens.session_state_orchestrator import (
    SessionStateOrchestrator,
    SessionStatus,
)


@pytest.fixture
def temp_cortex_brain() -> Generator[Path, None, None]:
    """Create temporary cortex_brain directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="cortex_brain_perf_"))
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


class TestSessionStatePersistencePerformance:
    """Test orchestrator performance and optimizations."""
    
    def test_create_session_performance_under_100ms(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test session creation completes within 100ms performance target."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        start_time = time.perf_counter()
        session = orchestrator.create_session(
            session_id="perf-test-001",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        assert session is not None
        assert elapsed < 100.0, f"Session creation took {elapsed:.2f}ms, target: <100ms"
    
    def test_get_session_performance_under_50ms(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test session read completes within 50ms."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create session first
        session = orchestrator.create_session(
            session_id="perf-test-002",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        # Measure read performance
        start_time = time.perf_counter()
        retrieved = orchestrator.get_session("perf-test-002")
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        assert retrieved is not None
        assert elapsed < 50.0, f"Session read took {elapsed:.2f}ms, target: <50ms"
    
    def test_update_session_performance_under_100ms(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test session update completes within 100ms."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create session
        session = orchestrator.create_session(
            session_id="perf-test-003",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        # Update with timing
        session.status = SessionStatus.COMPLETED
        start_time = time.perf_counter()
        success = orchestrator.update_session("perf-test-003", session)
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        assert success is True
        assert elapsed < 100.0, f"Session update took {elapsed:.2f}ms, target: <100ms"
    
    def test_batch_session_operations(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test batch operations with multiple sessions."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create 10 sessions and measure batch performance
        start_time = time.perf_counter()
        for i in range(10):
            session = orchestrator.create_session(
                session_id=f"batch-{i}",
                repo_id=f"repo-{i}",
                repo_path=f"/path/{i}",
            )
            assert session is not None
        batch_elapsed = (time.perf_counter() - start_time) * 1000
        
        # Average per session should be <100ms
        avg_per_session = batch_elapsed / 10
        assert avg_per_session < 100.0, f"Avg {avg_per_session:.2f}ms per session"
        
        # List active should be fast
        start_time = time.perf_counter()
        active = orchestrator.list_active_sessions()
        list_elapsed = (time.perf_counter() - start_time) * 1000
        
        assert len(active) == 10
        assert list_elapsed < 50.0, f"List active took {list_elapsed:.2f}ms, target: <50ms"
    
    def test_session_metadata_efficiency(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test session metadata storage is efficient."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create session with metadata
        session = orchestrator.create_session(
            session_id="meta-test",
            repo_id="repo-123",
            repo_path="/path/to/repo",
            orchestrator="LENSOrchestrator",
            operation="ANALYZE",
        )
        assert session is not None
        
        # Check file size is reasonable (YAML overhead)
        session_file = temp_cortex_brain / "sessions" / "meta-test.yaml"
        file_size = session_file.stat().st_size
        
        # File should be < 1KB for minimal metadata
        assert file_size < 1024, f"Session file {file_size} bytes, expect <1KB"
    
    def test_concurrent_read_performance(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test repeated reads benefit from filesystem caching."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create session
        session = orchestrator.create_session(
            session_id="cache-test",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        # First read (cold cache)
        start_time = time.perf_counter()
        retrieved1 = orchestrator.get_session("cache-test")
        first_read = (time.perf_counter() - start_time) * 1000
        
        # Second read (warm cache)
        start_time = time.perf_counter()
        retrieved2 = orchestrator.get_session("cache-test")
        second_read = (time.perf_counter() - start_time) * 1000
        
        # Third read (warm cache)
        start_time = time.perf_counter()
        retrieved3 = orchestrator.get_session("cache-test")
        third_read = (time.perf_counter() - start_time) * 1000
        
        assert retrieved1 is not None
        assert retrieved2 is not None
        assert retrieved3 is not None
        
        # Warm cache should not be significantly slower
        # (may be same or slightly faster due to OS caching)
        assert second_read <= first_read * 1.5
        assert third_read <= first_read * 1.5
    
    def test_archive_operation_performance(
        self,
        temp_cortex_brain: Path,
    ) -> None:
        """Test archive operation completes efficiently."""
        orchestrator = SessionStateOrchestrator(cortex_brain_path=temp_cortex_brain)
        
        # Create session
        session = orchestrator.create_session(
            session_id="archive-perf",
            repo_id="repo-123",
            repo_path="/path/to/repo",
        )
        assert session is not None
        
        # Archive with timing
        start_time = time.perf_counter()
        success = orchestrator.archive_session("archive-perf")
        elapsed = (time.perf_counter() - start_time) * 1000
        
        assert success is True
        assert elapsed < 50.0, f"Archive took {elapsed:.2f}ms, target: <50ms"


# AC_COMPLETE: AC-ENH087-T5-S3-REFACTOR-001 ✅ REFACTOR phase tests complete
# Total tests: 7
# All tests validate performance + optimization
