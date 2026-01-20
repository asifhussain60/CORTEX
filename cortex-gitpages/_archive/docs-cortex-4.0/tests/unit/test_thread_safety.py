"""
Tests for Issue #1: Thread Join Timeout Coverage

Validates that all thread operations have timeout protection.
"""

import pytest
import threading
import time
from cortex.core.resilience.thread_safety import (
    safe_thread_join,
    spawn_with_timeout_join,
    scan_file_for_bare_joins,
    DEFAULT_THREAD_TIMEOUT,
)


class TestThreadSafeJoin:
    """Test safe thread joining operations."""
    
    def test_safe_join_completes_normally(self):
        """Thread that completes should return True."""
        def quick_task():
            pass
        
        thread = threading.Thread(target=quick_task)
        thread.start()
        
        result = safe_thread_join(thread, timeout_sec=1.0, name="test")
        assert result is True
        assert not thread.is_alive()
    
    def test_safe_join_timeout_protection(self):
        """Thread that doesn't finish should timeout cleanly."""
        def infinite_loop():
            while True:
                time.sleep(0.1)
        
        thread = threading.Thread(target=infinite_loop, daemon=True)
        thread.start()
        
        result = safe_thread_join(thread, timeout_sec=0.05, name="test")
        assert result is False
        assert thread.is_alive()  # Thread still running
    
    def test_safe_join_invalid_timeout_raises(self):
        """Negative timeout should raise ValueError."""
        def dummy():
            pass
        
        thread = threading.Thread(target=dummy)
        thread.start()
        
        with pytest.raises(ValueError, match="Timeout must be positive"):
            safe_thread_join(thread, timeout_sec=-1.0)
    
    def test_safe_join_invalid_thread_raises(self):
        """Non-thread object should raise TypeError."""
        with pytest.raises(TypeError, match="Expected threading.Thread"):
            safe_thread_join("not a thread")  # type: ignore
    
    def test_safe_join_exception_handling(self):
        """Exception in thread should be propagated."""
        def failing_task():
            raise RuntimeError("Task failed")
        
        thread = threading.Thread(target=failing_task)
        thread.start()
        thread.join()  # Normal join to let exception occur
        
        # Thread should be done even though it failed
        assert not thread.is_alive()


class TestSpawnWithTimeoutJoin:
    """Test thread spawning with automatic timeout join."""
    
    def test_spawn_successful_task(self):
        """Spawning a successful task returns the thread."""
        def task():
            return "result"
        
        thread = spawn_with_timeout_join(target=task, timeout_sec=1.0)
        assert thread is not None
        assert not thread.is_alive()
    
    def test_spawn_timeout_returns_none(self):
        """Task that times out returns None."""
        def long_task():
            time.sleep(10)
        
        thread = spawn_with_timeout_join(
            target=long_task,
            timeout_sec=0.01,
            daemon=True
        )
        assert thread is None
    
    def test_spawn_with_args(self):
        """Spawned task can receive arguments."""
        results = []
        
        def task_with_args(x, y, z=None):
            results.append((x, y, z))
        
        thread = spawn_with_timeout_join(
            target=task_with_args,
            args=(1, 2),
            kwargs={"z": 3},
            timeout_sec=1.0
        )
        assert thread is not None
        assert results == [(1, 2, 3)]
    
    def test_spawn_daemon_thread(self):
        """Daemon threads are properly marked."""
        def dummy():
            time.sleep(0.1)
        
        thread = spawn_with_timeout_join(
            target=dummy,
            timeout_sec=1.0,
            daemon=True,
            name="daemon_test"
        )
        assert thread is not None
        assert thread.daemon is True
        assert thread.name == "daemon_test"


class TestBareJoinScanning:
    """Test scanning for bare thread.join() calls."""
    
    def test_scan_safe_join_call(self, tmp_path):
        """Files with safe join() calls should have no issues."""
        code = 'import threading\nthread = threading.Thread(target=foo)\nthread.start()\nthread.join(timeout=5.0)\n'
        py_file = tmp_path / "test.py"
        py_file.write_text(code)
        
        issues = scan_file_for_bare_joins(py_file)
        assert len(issues) == 0
    
    def test_scan_bare_join_call(self, tmp_path):
        """Files with bare join() calls should be detected."""
        code = 'import threading\nthread = threading.Thread(target=foo)\nthread.start()\nthread.join()\n'
        py_file = tmp_path / "test.py"
        py_file.write_text(code)
        
        issues = scan_file_for_bare_joins(py_file)
        assert len(issues) > 0
        assert 4 in issues  # Line 4 has bare join()
    
    def test_scan_multiple_bare_joins(self, tmp_path):
        """Multiple bare joins should all be detected."""
        code = 'thread1.join()\nthread2.join()\nthread3.join(timeout=1.0)\nthread4.join()\n'
        py_file = tmp_path / "test.py"
        py_file.write_text(code)
        
        issues = scan_file_for_bare_joins(py_file)
        assert 1 in issues
        assert 2 in issues
        assert 4 in issues
        assert 3 not in issues  # This one has timeout
    
    def test_scan_ignores_invalid_files(self, tmp_path):
        """Invalid files should be skipped gracefully."""
        bad_file = tmp_path / "nonexistent.py"
        
        issues = scan_file_for_bare_joins(bad_file)
        assert issues == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
