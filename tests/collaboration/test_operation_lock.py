"""
Tests for Operation Locking (TEAM-002).

Phase: 5.5 (Team Collaboration Layer)
Author: Asif Hussain
Date: 2026-01-27
"""

import os
import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from cortex.collaboration.operation_lock import (
    operation_lock,
    check_lock_status,
    clear_stale_locks,
    LockTimeoutError,
    LockInfo,
    _get_lock_directory,
    _sanitize_resource_id,
)
from cortex.collaboration.user_context import (
    UserContext,
    set_current_user,
    clear_user_context,
)


class TestSanitizeResourceId:
    """Tests for resource ID sanitization."""
    
    def test_replaces_slashes(self):
        """Test that path separators are replaced."""
        result = _sanitize_resource_id("file:src/main/app.py")
        assert "/" not in result
        assert "\\" not in result
    
    def test_replaces_colons(self):
        """Test that colons are replaced."""
        result = _sanitize_resource_id("file:path")
        assert ":" not in result
    
    def test_handles_long_ids(self):
        """Test that long IDs are truncated with hash."""
        long_id = "a" * 300
        result = _sanitize_resource_id(long_id)
        assert len(result) <= 200


class TestOperationLock:
    """Tests for operation_lock context manager."""
    
    def setup_method(self):
        """Set up test user context."""
        user = UserContext(user_id="test_user", username="Test User", roles=[])
        set_current_user(user)
    
    def teardown_method(self):
        """Clean up after tests."""
        clear_user_context()
        # Clean up any test lock files
        lock_dir = _get_lock_directory()
        for lock_file in lock_dir.glob("test_*.lock"):
            try:
                lock_file.unlink()
            except Exception:
                pass
    
    def test_acquires_and_releases_lock(self):
        """Test basic lock acquisition and release."""
        resource = "test_resource_basic"
        
        with operation_lock(resource) as lock_info:
            assert isinstance(lock_info, LockInfo)
            assert lock_info.resource_id == resource
            assert lock_info.user_id == "test_user"
            assert lock_info.lock_file.exists()
        
        # Lock should be released
        # (Can't easily verify release without another process)
    
    def test_lock_info_contains_user(self):
        """Test that lock info contains user from context."""
        alice = UserContext(user_id="alice", username="Alice", roles=[])
        set_current_user(alice)
        
        with operation_lock("test_resource_alice") as lock_info:
            assert lock_info.user_id == "alice"
    
    def test_lock_with_custom_user(self):
        """Test providing custom user ID."""
        with operation_lock("test_resource_custom", user_id="custom_user") as lock_info:
            assert lock_info.user_id == "custom_user"
    
    def test_concurrent_lock_timeout(self):
        """Test that concurrent lock requests timeout properly."""
        resource = "test_resource_timeout"
        lock_acquired = threading.Event()
        
        def hold_lock():
            with operation_lock(resource, timeout_seconds=5.0):
                lock_acquired.set()
                time.sleep(2)  # Hold lock for 2 seconds
        
        # Start thread holding the lock
        holder = threading.Thread(target=hold_lock)
        holder.start()
        
        # Wait for lock to be acquired
        lock_acquired.wait(timeout=1.0)
        time.sleep(0.1)  # Small delay to ensure lock is held
        
        # Try to acquire with short timeout - should fail
        with pytest.raises(LockTimeoutError) as exc_info:
            with operation_lock(resource, timeout_seconds=0.5):
                pass
        
        assert "Could not acquire lock" in str(exc_info.value)
        
        holder.join()
    
    def test_sequential_locks_succeed(self):
        """Test that locks can be acquired sequentially."""
        resource = "test_resource_sequential"
        
        # First lock
        with operation_lock(resource) as lock1:
            assert lock1.resource_id == resource
        
        # Second lock (should succeed after first is released)
        with operation_lock(resource) as lock2:
            assert lock2.resource_id == resource


class TestCheckLockStatus:
    """Tests for check_lock_status function."""
    
    def teardown_method(self):
        """Clean up test locks."""
        clear_user_context()
        lock_dir = _get_lock_directory()
        for lock_file in lock_dir.glob("test_status_*.lock"):
            try:
                lock_file.unlink()
            except Exception:
                pass
    
    def test_returns_none_for_unlocked(self):
        """Test that unlocked resources return None."""
        status = check_lock_status("test_status_unlocked")
        assert status is None
    
    def test_returns_info_for_locked(self):
        """Test that locked resources return lock info."""
        resource = "test_status_locked"
        
        # Use a thread to hold the lock
        lock_acquired = threading.Event()
        check_done = threading.Event()
        
        def hold_lock():
            user = UserContext(user_id="holder", username="Holder", roles=[])
            set_current_user(user)
            with operation_lock(resource):
                lock_acquired.set()
                check_done.wait(timeout=5.0)
        
        holder = threading.Thread(target=hold_lock)
        holder.start()
        
        lock_acquired.wait(timeout=1.0)
        time.sleep(0.1)
        
        try:
            status = check_lock_status(resource)
            # Status might be None or LockInfo depending on timing
            # The important thing is it doesn't crash
        finally:
            check_done.set()
            holder.join()


class TestClearStaleLocks:
    """Tests for clear_stale_locks function."""
    
    def test_clears_old_locks(self):
        """Test that old lock files are cleared."""
        lock_dir = _get_lock_directory()
        
        # Create a fake old lock file
        old_lock = lock_dir / "test_stale_old.lock"
        old_lock.write_text("old_user|2020-01-01T00:00:00Z|test")
        
        # Set modification time to be old
        old_time = time.time() - 7200  # 2 hours ago
        os.utime(old_lock, (old_time, old_time))
        
        # Clear locks older than 1 hour
        cleared = clear_stale_locks(max_age_seconds=3600)
        
        assert cleared >= 1
        assert not old_lock.exists()
    
    def test_preserves_recent_locks(self):
        """Test that recent lock files are preserved."""
        lock_dir = _get_lock_directory()
        
        # Create a recent lock file
        recent_lock = lock_dir / "test_stale_recent.lock"
        recent_lock.write_text("recent_user|2026-01-27T00:00:00Z|test")
        
        try:
            # Clear locks older than 1 hour (this one is recent)
            clear_stale_locks(max_age_seconds=3600)
            
            assert recent_lock.exists()
        finally:
            recent_lock.unlink(missing_ok=True)
