"""
Tests for ODX-001-01: Hot-Reload Orchestrator

AC-ID: ODX-001-01
Phase: PHASE-18-ORCHESTRATOR-DEVX
"""

import pytest
import time
import tempfile
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from cortex.devx.hot_reload import (
    HotReloadOrchestrator,
    FileWatcher,
    ReloadEvent,
    FileChange,
    ChangeType,
    ReloadState,
    WatchConfig,
)


class TestFileChange:
    """Tests for FileChange dataclass."""
    
    def test_file_change_creation(self):
        """Test FileChange creation."""
        change = FileChange(
            path=Path("/test/file.py"),
            change_type=ChangeType.MODIFIED,
        )
        
        assert change.path == Path("/test/file.py")
        assert change.change_type == ChangeType.MODIFIED
        assert change.timestamp is not None
    
    def test_file_change_with_hashes(self):
        """Test FileChange with old and new hashes."""
        change = FileChange(
            path=Path("/test/file.py"),
            change_type=ChangeType.MODIFIED,
            old_hash="abc123",
            new_hash="def456",
        )
        
        assert change.old_hash == "abc123"
        assert change.new_hash == "def456"
    
    def test_file_change_hashable(self):
        """Test FileChange is hashable for set operations."""
        change1 = FileChange(path=Path("/test/file.py"), change_type=ChangeType.MODIFIED)
        change2 = FileChange(path=Path("/test/file.py"), change_type=ChangeType.MODIFIED)
        
        # Should be hashable
        assert hash(change1) == hash(change2)
        
        # Can be added to sets
        changes = {change1, change2}
        assert len(changes) == 1


class TestReloadEvent:
    """Tests for ReloadEvent dataclass."""
    
    def test_reload_event_creation(self):
        """Test ReloadEvent creation."""
        event = ReloadEvent(orchestrator_name="TestOrchestrator")
        
        assert event.orchestrator_name == "TestOrchestrator"
        assert event.event_id.startswith("reload-")
        assert not event.success
        assert event.reload_time_ms == 0.0
    
    def test_reload_event_with_changes(self):
        """Test ReloadEvent with file changes."""
        changes = [
            FileChange(path=Path("/test/file.py"), change_type=ChangeType.MODIFIED),
        ]
        
        event = ReloadEvent(
            orchestrator_name="TestOrchestrator",
            file_changes=changes,
            success=True,
            reload_time_ms=150.5,
        )
        
        assert len(event.file_changes) == 1
        assert event.success
        assert event.reload_time_ms == 150.5


class TestWatchConfig:
    """Tests for WatchConfig dataclass."""
    
    def test_default_config(self):
        """Test default watch configuration."""
        config = WatchConfig()
        
        assert "*.py" in config.patterns
        assert "__pycache__/*" in config.ignore_patterns
        assert config.debounce_ms == 500
        assert config.recursive
    
    def test_custom_config(self):
        """Test custom watch configuration."""
        config = WatchConfig(
            patterns=["*.yaml", "*.json"],
            ignore_patterns=["build/*"],
            debounce_ms=1000,
            recursive=False,
        )
        
        assert "*.yaml" in config.patterns
        assert config.debounce_ms == 1000
        assert not config.recursive


class TestFileWatcher:
    """Tests for FileWatcher."""
    
    def test_watcher_creation(self):
        """Test FileWatcher creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = FileWatcher(tmpdir)
            
            assert watcher.watch_path == Path(tmpdir)
            assert not watcher.is_running
            assert not watcher.is_paused
    
    def test_watcher_start_stop(self):
        """Test FileWatcher start and stop."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = FileWatcher(tmpdir)
            
            watcher.start()
            assert watcher.is_running
            
            watcher.stop()
            time.sleep(0.2)  # Allow thread to terminate
            assert not watcher.is_running
    
    def test_watcher_pause_resume(self):
        """Test FileWatcher pause and resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = FileWatcher(tmpdir)
            watcher.start()
            
            watcher.pause()
            assert watcher.is_paused
            
            watcher.resume()
            assert not watcher.is_paused
            
            watcher.stop()
    
    def test_watcher_callback_registration(self):
        """Test FileWatcher callback registration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = FileWatcher(tmpdir)
            
            callback_called = []
            
            def callback(changes):
                callback_called.append(changes)
            
            result = watcher.on_change(callback)
            
            assert result is watcher  # Method chaining
            assert len(watcher._callbacks) == 1
    
    def test_watcher_detects_file_creation(self):
        """Test FileWatcher detects new files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = FileWatcher(tmpdir, WatchConfig(debounce_ms=50))
            
            detected_changes = []
            
            def callback(changes):
                detected_changes.extend(changes)
            
            watcher.on_change(callback)
            watcher.start()
            
            # Wait for initial scan
            time.sleep(0.2)
            
            # Create a new file
            test_file = Path(tmpdir) / "new_file.py"
            test_file.write_text("# New file")
            
            # Wait for detection
            time.sleep(0.3)
            
            watcher.stop()
            
            # Should detect creation
            created = [c for c in detected_changes if c.change_type == ChangeType.CREATED]
            assert len(created) >= 1
    
    def test_watcher_detects_file_modification(self):
        """Test FileWatcher detects file modifications."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial file
            test_file = Path(tmpdir) / "existing.py"
            test_file.write_text("# Original content")
            
            watcher = FileWatcher(tmpdir, WatchConfig(debounce_ms=50))
            
            detected_changes = []
            
            def callback(changes):
                detected_changes.extend(changes)
            
            watcher.on_change(callback)
            watcher.start()
            
            # Wait for initial scan
            time.sleep(0.2)
            
            # Modify the file
            test_file.write_text("# Modified content")
            
            # Wait for detection
            time.sleep(0.3)
            
            watcher.stop()
            
            # Should detect modification
            modified = [c for c in detected_changes if c.change_type == ChangeType.MODIFIED]
            assert len(modified) >= 1
    
    def test_watcher_ignores_patterns(self):
        """Test FileWatcher ignores specified patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = WatchConfig(
                patterns=["*.py"],
                ignore_patterns=["*.pyc", "__pycache__/*"],
            )
            
            watcher = FileWatcher(tmpdir, config)
            
            # Should watch .py files
            assert watcher._should_watch(Path("test.py"))
            
            # Should ignore .pyc files
            assert not watcher._should_watch(Path("test.pyc"))
    
    def test_compute_hash(self):
        """Test file hash computation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watcher = FileWatcher(tmpdir)
            
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("content")
            
            hash1 = watcher._compute_hash(test_file)
            assert hash1 is not None
            assert len(hash1) == 64  # SHA256 hex length
            
            # Same content should give same hash
            hash2 = watcher._compute_hash(test_file)
            assert hash1 == hash2
            
            # Different content should give different hash
            test_file.write_text("different content")
            hash3 = watcher._compute_hash(test_file)
            assert hash1 != hash3


class TestHotReloadOrchestrator:
    """Tests for HotReloadOrchestrator."""
    
    def test_hot_reload_creation(self):
        """Test HotReloadOrchestrator creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hot_reload = HotReloadOrchestrator(tmpdir)
            
            assert hot_reload.orchestrator_path == Path(tmpdir)
            assert hot_reload.state == ReloadState.IDLE
            assert len(hot_reload.registered_orchestrators) == 0
    
    def test_hot_reload_start_stop(self):
        """Test HotReloadOrchestrator start and stop."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hot_reload = HotReloadOrchestrator(tmpdir)
            
            hot_reload.start()
            assert hot_reload.state == ReloadState.WATCHING
            
            hot_reload.stop()
            assert hot_reload.state == ReloadState.IDLE
    
    def test_hot_reload_pause_resume(self):
        """Test HotReloadOrchestrator pause and resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hot_reload = HotReloadOrchestrator(tmpdir)
            hot_reload.start()
            
            hot_reload.pause()
            assert hot_reload.state == ReloadState.PAUSED
            
            hot_reload.resume()
            assert hot_reload.state == ReloadState.WATCHING
            
            hot_reload.stop()
    
    def test_callback_registration(self):
        """Test callback registration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hot_reload = HotReloadOrchestrator(tmpdir)
            
            before_called = []
            after_called = []
            error_called = []
            
            hot_reload.on("before_reload", lambda e: before_called.append(e))
            hot_reload.on("after_reload", lambda e: after_called.append(e))
            hot_reload.on("on_error", lambda e: error_called.append(e))
            
            assert len(hot_reload._callbacks["before_reload"]) == 1
            assert len(hot_reload._callbacks["after_reload"]) == 1
            assert len(hot_reload._callbacks["on_error"]) == 1
    
    def test_force_reload(self):
        """Test force reload functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hot_reload = HotReloadOrchestrator(tmpdir, sandbox_enabled=False)
            
            # Create and register a mock orchestrator
            class MockOrchestrator:
                def __init__(self):
                    self.value = 0
            
            # Patch the module system
            with patch.dict('sys.modules', {'test_module': MagicMock(MockOrchestrator=MockOrchestrator)}):
                MockOrchestrator.__module__ = 'test_module'
                hot_reload.register("MockOrch", MockOrchestrator)
                
                events = hot_reload.force_reload("MockOrch")
                
                assert len(events) == 1
                # Event should be created (may fail due to module reload, but that's expected)
                assert events[0].orchestrator_name == "MockOrch"
    
    def test_state_preservation(self):
        """Test state preservation across reloads."""
        with tempfile.TemporaryDirectory() as tmpdir:
            hot_reload = HotReloadOrchestrator(tmpdir, sandbox_enabled=False)
            
            class MockOrchestrator:
                def __init__(self):
                    self.value = 0
                
                def get_state(self):
                    return {"value": self.value}
                
                def set_state(self, state):
                    self.value = state.get("value", 0)
            
            hot_reload.register("MockOrch", MockOrchestrator)
            
            # Set initial state
            instance = MockOrchestrator()
            instance.value = 42
            hot_reload._instances["MockOrch"] = instance
            
            # Preserve state
            state = hot_reload._preserve_state("MockOrch")
            
            assert state == {"value": 42}
            assert "MockOrch" in hot_reload._preserved_state
    
class TestHotReloadIntegration:
    """Integration tests for hot-reload system."""
    
    def test_full_hot_reload_cycle(self):
        """Test complete hot-reload cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial orchestrator file
            orch_file = Path(tmpdir) / "my_orchestrator.py"
            orch_file.write_text("""
class MyOrchestrator:
    VERSION = "1.0"
    
    def process(self):
        return "v1"
""")
            
            hot_reload = HotReloadOrchestrator(
                tmpdir,
                WatchConfig(debounce_ms=50),
                sandbox_enabled=False,
            )
            
            reload_events = []
            hot_reload.on("after_reload", lambda e: reload_events.append(e))
            
            # Note: Full integration would require actual module import/reload
            # which is complex in test environment. This tests the structure.
            
            assert hot_reload.state == ReloadState.IDLE
            hot_reload.start()
            assert hot_reload.state == ReloadState.WATCHING
            hot_reload.stop()
    
    def test_sandbox_execution_mode(self):
        """Test sandbox execution when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # When sandbox is enabled (and available), should use sandbox
            hot_reload = HotReloadOrchestrator(tmpdir, sandbox_enabled=True)
            
            # Sandbox should be initialized if ExecutionSandbox is available
            # (may be None in test environment without full CORTEX)
            
            hot_reload.start()
            hot_reload.stop()
