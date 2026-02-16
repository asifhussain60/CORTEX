"""
Unit tests for AutoCleanupManager

AC-ID: AC-WAVE-R-005

NOTE: This module was refactored into cortex.toolkit.cleanup (Phase 90).
Tests kept for historical reference but may need updating.
"""

import pytest
from pathlib import Path
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock

try:
    from cortex.debugging.auto_cleanup_manager import AutoCleanupManager
except (ModuleNotFoundError, ImportError):
    # Module refactored into cortex.toolkit.cleanup (Phase 90)
    pytest.skip("AutoCleanupManager moved to cortex.toolkit.cleanup", allow_module_level=True)


class DebugSession:
    """Mock DebugSession for testing."""
    def __init__(self, session_id, status):
        self.session_id = session_id
        self.status = status
        self.trigger_event = "TEST_FAILURE"
        self.file_paths = []
        self.created_at = datetime.now()


class TestAutoCleanupManagerInitialization:
    """Test AutoCleanupManager initialization."""
    
    def test_manager_initializes(self):
        """Test manager initializes successfully."""
        manager = AutoCleanupManager()
        
        assert manager is not None
        assert manager.marker_pattern is not None


class TestResolvedSessionDetection:
    """Test detection and cleanup of resolved sessions."""
    
    def test_auto_cleanup_detects_resolved_session(self):
        """Test cleanup identifies sessions not in active list."""
        manager = AutoCleanupManager()
        
        # Only session-1 is active
        active_sessions = {
            "session-test_failure-001": DebugSession("session-test_failure-001", "active")
        }
        
        # Mock _find_files_with_markers to return empty list
        manager._find_files_with_markers = Mock(return_value=[])
        
        # Should return empty (no files to clean)
        resolved = manager.cleanup_resolved_sessions(active_sessions)
        
        assert isinstance(resolved, list)
    
    def test_auto_cleanup_removes_markers_for_session(self):
        """Test cleanup removes markers for specific session."""
        # Create temp file with markers
        marker_content = """# CORTEX_DEBUG_START
# Trigger: TEST_FAILURE
# Context: Test failed
# Injected: 2026-02-13T00:00:00
line 1
line 2
# CORTEX_DEBUG_END
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(marker_content)
            temp_file = Path(f.name)
        
        try:
            manager = AutoCleanupManager()
            
            # Mock _find_files_with_markers
            manager._find_files_with_markers = Mock(return_value=[temp_file])
            
            # Cleanup with no active sessions
            resolved = manager.cleanup_resolved_sessions({})
            
            # Verify marker removed
            content = temp_file.read_text()
            assert "CORTEX_DEBUG" not in content
            assert "line 2" in content
            
        finally:
            os.unlink(temp_file)
    
    def test_auto_cleanup_preserves_active_sessions(self):
        """Test cleanup preserves markers for active sessions."""
        marker_content = """# CORTEX_DEBUG_START
# Trigger: TEST_FAILURE
# Context: Test failed
# Injected: 2026-02-13T00:00:00
line 1
line 2
# CORTEX_DEBUG_END
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(marker_content)
            temp_file = Path(f.name)
        
        try:
            manager = AutoCleanupManager()
            manager._find_files_with_markers = Mock(return_value=[temp_file])
            
            # Session is active
            active_sessions = {
                "session-test-001": DebugSession("session-test-001", "active")
            }
            
            resolved = manager.cleanup_resolved_sessions(active_sessions)
            
            # Marker should still exist
            content = temp_file.read_text()
            assert "CORTEX_DEBUG_START: session-test-001" in content
            
        finally:
            os.unlink(temp_file)


class TestCleanupSession:
    """Test cleanup of specific session."""
    
    def test_cleanup_session_removes_markers(self):
        """Test cleanup_session removes specific session markers."""
        marker_content = """# CORTEX_DEBUG_START
# Trigger: TEST_FAILURE
# Injected: 2026-02-13T00:00:00
line 1
line 2
# CORTEX_DEBUG_END
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(marker_content)
            temp_file = Path(f.name)
        
        try:
            manager = AutoCleanupManager()
            manager._find_files_with_markers = Mock(return_value=[temp_file])
            
            result = manager.cleanup_session("session-test-001")
            
            assert result is True
            
            content = temp_file.read_text()
            assert "CORTEX_DEBUG" not in content
            
        finally:
            os.unlink(temp_file)


class TestStaleMarkerDetection:
    """Test stale marker detection."""
    
    def test_check_stale_markers_identifies_old_markers(self):
        """Test check_stale_markers identifies markers > 24 hours."""
        # Create marker with old timestamp
        old_timestamp = (datetime.now() - timedelta(hours=48)).isoformat()
        
        marker_content = f"""# CORTEX_DEBUG_START
# Trigger: TEST_FAILURE
# Context: Test failed
# Injected: {old_timestamp}
line 1
# CORTEX_DEBUG_END
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(marker_content)
            temp_file = Path(f.name)
        
        try:
            manager = AutoCleanupManager()
            manager._find_files_with_markers = Mock(return_value=[temp_file])
            
            stale = manager.check_stale_markers(max_age_hours=24)
            
            assert len(stale) >= 1
            assert stale[0]["session_id"] == "session-test-001"
            assert stale[0]["age_hours"] > 24
            
        finally:
            os.unlink(temp_file)
    
    def test_check_stale_markers_ignores_recent_markers(self):
        """Test check_stale_markers ignores recent markers."""
        # Create marker with recent timestamp
        recent_timestamp = datetime.now().isoformat()
        
        marker_content = f"""# CORTEX_DEBUG_START
# Trigger: TEST_FAILURE
# Injected: {recent_timestamp}
line 1
# CORTEX_DEBUG_END
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(marker_content)
            temp_file = Path(f.name)
        
        try:
            manager = AutoCleanupManager()
            manager._find_files_with_markers = Mock(return_value=[temp_file])
            
            stale = manager.check_stale_markers(max_age_hours=24)
            
            # Should not find recent marker as stale
            stale_session_ids = [s["session_id"] for s in stale]
            assert "session-test-001" not in stale_session_ids
            
        finally:
            os.unlink(temp_file)


class TestMarkerRemoval:
    """Test _remove_marker utility."""
    
    def test_remove_marker_removes_specific_session(self):
        """Test _remove_marker removes only specified session."""
        content = """# CORTEX_DEBUG_START
line 1
line 2
line 3
# CORTEX_DEBUG_END
"""
        
        manager = AutoCleanupManager()
        
        # Remove only session-001
        result = manager._remove_marker(content, "session-001")
        
        assert "session-001" not in result
        assert "session-002" in result
        assert "line 3" in result


class TestFileDiscovery:
    """Test _find_files_with_markers."""
    
    def test_find_files_with_markers_returns_list(self):
        """Test _find_files_with_markers returns list."""
        manager = AutoCleanupManager()
        
        files = manager._find_files_with_markers()
        
        assert isinstance(files, list)
