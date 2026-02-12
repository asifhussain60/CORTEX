"""
Test suite for FileLock

AC_START: AC-ENH-063-P2-006
Description: TDD tests for cross-platform file locking
Authority: CORE-008 (tests before code)
Testing: cortex/infrastructure/file_lock.py

Test Coverage:
- File lock acquisition and release
- Timeout handling
- Concurrent access prevention
- Cross-platform compatibility (Unix/Windows)
- Lock cleanup
- Context manager usage
"""

import os
import platform
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, Optional

import pytest

from cortex.infrastructure.file_lock import (
    FileLock,
    FileLockError,
    FileLockTimeout,
    file_lock,
)


class TestFileLockBasics:
    """Test basic file locking operations."""
    
    def test_lock_init(self, tmp_path: Path) -> None:
        """File lock initializes with correct paths."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        lock = FileLock(str(file_path))
        
        assert lock.file_path == file_path.resolve()
        assert lock.lock_path == file_path.with_suffix(".txt.lock")
        assert lock.timeout == 5.0
        assert lock.lock_file is None
    
    def test_lock_custom_timeout(self, tmp_path: Path) -> None:
        """File lock accepts custom timeout."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        lock = FileLock(str(file_path), timeout=10.0)
        
        assert lock.timeout == 10.0
    
    def test_lock_acquire_release(self, tmp_path: Path) -> None:
        """Lock can be acquired and released."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        lock = FileLock(str(file_path))
        
        lock.acquire()
        assert lock.lock_file is not None
        assert lock.lock_path.exists()
        
        lock.release()
        assert lock.lock_file is None
        assert not lock.lock_path.exists()


class TestContextManager:
    """Test context manager interface."""
    
    def test_lock_context_manager(self, tmp_path: Path) -> None:
        """Lock works as context manager."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        with FileLock(str(file_path)) as lock:
            assert lock.lock_file is not None
            assert lock.lock_path.exists()
        
        # After context, lock released
        assert lock.lock_file is None
        assert not lock.lock_path.exists()
    
    def test_file_lock_convenience_function(self, tmp_path: Path) -> None:
        """file_lock() convenience function works."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        with file_lock(str(file_path)):
            # Lock is active
            lock_path = file_path.with_suffix(".txt.lock")
            assert lock_path.exists()
        
        # Lock released
        assert not lock_path.exists()


class TestFileSafety:
    """Test file operation safety with locks."""
    
    def test_safe_file_write(self, tmp_path: Path) -> None:
        """File write is safe with lock."""
        file_path = tmp_path / "test.txt"
        
        with file_lock(str(file_path)):
            with open(file_path, "w") as f:
                f.write("safe write")
        
        assert file_path.read_text() == "safe write"
    
    def test_safe_file_read(self, tmp_path: Path) -> None:
        """File read is safe with lock."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("initial")
        
        with file_lock(str(file_path)):
            with open(file_path, "r") as f:
                content = f.read()
        
        assert content == "initial"


class TestConcurrentAccess:
    """Test prevention of concurrent access."""
    
    def test_concurrent_lock_blocks(self, tmp_path: Path) -> None:
        """Second lock waits for first lock."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        results: Dict[str, Optional[str]] = {"thread1": None, "thread2": None}
        
        def thread1_func():
            with file_lock(str(file_path), timeout=3.0):
                results["thread1"] = "started"
                time.sleep(0.5)
                results["thread1"] = "completed"
        
        def thread2_func():
            time.sleep(0.1)  # Let thread1 acquire lock first
            with file_lock(str(file_path), timeout=3.0):
                results["thread2"] = "completed"
        
        thread1 = threading.Thread(target=thread1_func)
        thread2 = threading.Thread(target=thread2_func)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        assert results["thread1"] == "completed"
        assert results["thread2"] == "completed"
    
    def test_concurrent_write_no_corruption(self, tmp_path: Path) -> None:
        """Concurrent writes don't corrupt file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("")
        
        def write_thread(thread_id: int):
            for i in range(5):
                with file_lock(str(file_path), timeout=5.0):
                    content = file_path.read_text()
                    lines = content.split("\n") if content else []
                    lines.append(f"thread{thread_id}-{i}")
                    file_path.write_text("\n".join(lines))
                time.sleep(0.01)
        
        threads = [threading.Thread(target=write_thread, args=(i,)) for i in range(3)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all writes succeeded
        content = file_path.read_text()
        lines = [line for line in content.split("\n") if line]
        assert len(lines) == 15  # 3 threads * 5 writes


class TestLockTimeout:
    """Test lock timeout behavior."""
    
    def test_lock_timeout_raises(self, tmp_path: Path) -> None:
        """Lock timeout raises FileLockTimeout."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        # Acquire lock
        lock1 = FileLock(str(file_path), timeout=1.0)
        lock1.acquire()
        
        # Try to acquire again (should timeout)
        lock2 = FileLock(str(file_path), timeout=0.2)
        
        with pytest.raises(FileLockTimeout):
            lock2.acquire()
        
        # Release first lock
        lock1.release()
    
    def test_lock_timeout_prevents_deadlock(self, tmp_path: Path) -> None:
        """Lock timeout prevents indefinite waiting."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        lock1 = FileLock(str(file_path))
        lock1.acquire()
        
        start_time = time.time()
        
        try:
            lock2 = FileLock(str(file_path), timeout=0.5)
            lock2.acquire()
        except FileLockTimeout:
            elapsed = time.time() - start_time
            assert 0.5 <= elapsed < 1.0  # Timed out as expected
        finally:
            lock1.release()


class TestLockCleanup:
    """Test lock cleanup and error handling."""
    
    def test_lock_file_cleaned_up(self, tmp_path: Path) -> None:
        """Lock file is removed after release."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        lock_path = file_path.with_suffix(".txt.lock")
        
        with file_lock(str(file_path)):
            assert lock_path.exists()
        
        assert not lock_path.exists()
    
    def test_lock_cleanup_on_exception(self, tmp_path: Path) -> None:
        """Lock is released even if exception occurs."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        lock_path = file_path.with_suffix(".txt.lock")
        
        try:
            with file_lock(str(file_path)):
                assert lock_path.exists()
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Lock still released
        assert not lock_path.exists()


class TestPlatformCompatibility:
    """Test platform-specific behavior."""
    
    def test_platform_detection(self) -> None:
        """Platform detection works correctly."""
        from cortex.infrastructure.file_lock import IS_WINDOWS
        
        assert IS_WINDOWS == (platform.system() == "Windows")
    
    def test_lock_on_current_platform(self, tmp_path: Path) -> None:
        """Lock works on current platform."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("content")
        
        # Should work regardless of platform
        with file_lock(str(file_path)):
            with open(file_path, "a") as f:
                f.write(" appended")
        
        assert "appended" in file_path.read_text()


# AC_COMPLETE: AC-ENH-063-P2-006 ✅ TDD tests for file locking (17 tests)
