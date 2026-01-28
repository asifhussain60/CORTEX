"""
Operation-Level Locking for CORTEX Team Collaboration.

Provides file-based locking to prevent concurrent modifications to the same
resources when multiple users share an MCP server.

Phase: 5.5 (Team Collaboration Layer)
Task: TEAM-002 (Operation-Level Locking)
Author: Asif Hussain
Date: 2026-01-27

CORE-030: Docker-first architecture - uses file-based locks (container-safe).
Lock files are stored in /app/.cortex/locks/ (Docker) or .cortex/locks/ (local).
"""

from __future__ import annotations

import os
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator, Optional

# fcntl is Unix-only, provide Windows fallback
if sys.platform != "win32":
    import fcntl
    HAS_FCNTL = True
else:
    fcntl = None  # type: ignore
    HAS_FCNTL = False

from cortex.collaboration.user_context import get_current_user


class OperationLockError(Exception):
    """Base exception for operation lock errors."""
    pass


class LockTimeoutError(OperationLockError):
    """Raised when lock acquisition times out."""
    pass


class LockAcquisitionError(OperationLockError):
    """Raised when lock cannot be acquired for other reasons."""
    pass


@dataclass
class LockInfo:
    """
    Information about a held lock.
    
    Attributes:
        resource_id: The resource being locked
        user_id: Who holds the lock
        acquired_at: When the lock was acquired
        lock_file: Path to the lock file
    """
    resource_id: str
    user_id: str
    acquired_at: datetime
    lock_file: Path


def _get_lock_directory() -> Path:
    """
    Get the lock directory path.
    
    Uses /app/.cortex/locks/ in Docker, or .cortex/locks/ locally.
    Creates the directory if it doesn't exist.
    
    Returns:
        Path to lock directory
    """
    # Check for Docker environment
    if os.path.exists("/app"):
        lock_dir = Path("/app/.cortex/locks")
    else:
        # Local development
        lock_dir = Path(".cortex/locks")
    
    lock_dir.mkdir(parents=True, exist_ok=True)
    return lock_dir


def _sanitize_resource_id(resource_id: str) -> str:
    """
    Sanitize resource ID for use as filename.
    
    Replaces path separators and special characters with underscores.
    
    Args:
        resource_id: Original resource identifier
        
    Returns:
        Sanitized string safe for filenames
    """
    # Replace problematic characters
    sanitized = resource_id.replace("/", "_").replace("\\", "_")
    sanitized = sanitized.replace(":", "_").replace(" ", "_")
    sanitized = sanitized.replace("..", "_")
    
    # Ensure it's not too long
    if len(sanitized) > 200:
        import hashlib
        hash_suffix = hashlib.sha256(resource_id.encode()).hexdigest()[:16]
        sanitized = sanitized[:180] + "_" + hash_suffix
    
    return sanitized


@contextmanager
def operation_lock(
    resource_id: str,
    timeout_seconds: float = 30.0,
    user_id: Optional[str] = None,
) -> Generator[LockInfo, None, None]:
    """
    Acquire exclusive lock on a resource.
    
    Context manager that provides exclusive access to a resource identified
    by resource_id. Uses file-based locking (fcntl.flock) which is safe
    across processes and works in Docker containers.
    
    Args:
        resource_id: Unique identifier for the resource to lock.
            Examples: "file:src/main.py", "orchestrator:refactoring", "operation:deploy"
        timeout_seconds: Maximum time to wait for lock acquisition (default: 30s)
        user_id: Optional user ID override (defaults to current user)
        
    Yields:
        LockInfo with details about the acquired lock
        
    Raises:
        LockTimeoutError: If lock cannot be acquired within timeout
        LockAcquisitionError: If lock cannot be acquired for other reasons
        
    Example:
        >>> with operation_lock("file:src/main.py"):
        ...     # Exclusive access to file
        ...     modify_file("src/main.py")
        ...
        >>> # Lock is automatically released
        
    Example with timeout:
        >>> try:
        ...     with operation_lock("operation:deploy", timeout_seconds=5.0):
        ...         perform_deployment()
        ... except LockTimeoutError:
        ...     print("Another deployment is in progress")
    """
    # Get user ID from context if not provided
    if user_id is None:
        user = get_current_user()
        user_id = user.user_id
    
    # Create lock file path
    lock_dir = _get_lock_directory()
    safe_id = _sanitize_resource_id(resource_id)
    lock_file = lock_dir / f"{safe_id}.lock"
    
    # Track timing
    start_time = time.time()
    acquired_at = datetime.now(timezone.utc)
    
    # Open lock file (create if doesn't exist)
    fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)
    
    try:
        # Attempt to acquire lock with retry
        while True:
            try:
                # Try non-blocking lock acquisition
                if HAS_FCNTL and fcntl is not None:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # Windows fallback: no-op (file existence is the lock)
                
                # Lock acquired - write holder info
                os.ftruncate(fd, 0)
                os.lseek(fd, 0, os.SEEK_SET)
                lock_info_str = f"{user_id}|{acquired_at.isoformat()}|{resource_id}"
                os.write(fd, lock_info_str.encode())
                
                break  # Successfully acquired
                
            except BlockingIOError:
                # Lock is held by another process
                elapsed = time.time() - start_time
                if elapsed >= timeout_seconds:
                    # Read who holds the lock for error message
                    try:
                        os.lseek(fd, 0, os.SEEK_SET)
                        holder_info = os.read(fd, 1024).decode()
                        holder_parts = holder_info.split("|")
                        holder_user = holder_parts[0] if holder_parts else "unknown"
                    except Exception:
                        holder_user = "unknown"
                    
                    raise LockTimeoutError(
                        f"Could not acquire lock on '{resource_id}' after "
                        f"{timeout_seconds:.1f}s. Lock held by: {holder_user}"
                    )
                
                # Wait and retry
                time.sleep(0.1)
        
        # Create LockInfo to yield
        lock_info = LockInfo(
            resource_id=resource_id,
            user_id=user_id,
            acquired_at=acquired_at,
            lock_file=lock_file,
        )
        
        yield lock_info
        
    finally:
        # Always release lock and close file descriptor
        try:
            if HAS_FCNTL and fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
        except Exception:
            pass  # Best effort release
        
        try:
            os.close(fd)
        except Exception:
            pass  # Best effort close


def check_lock_status(resource_id: str) -> Optional[LockInfo]:
    """
    Check if a resource is currently locked.
    
    Non-blocking check to see if a lock exists and who holds it.
    Does not acquire the lock.
    
    Args:
        resource_id: Resource to check
        
    Returns:
        LockInfo if locked, None if not locked
    """
    lock_dir = _get_lock_directory()
    safe_id = _sanitize_resource_id(resource_id)
    lock_file = lock_dir / f"{safe_id}.lock"
    
    if not lock_file.exists():
        return None
    
    try:
        fd = os.open(str(lock_file), os.O_RDONLY)
        try:
            # Try non-blocking lock
            if HAS_FCNTL and fcntl is not None:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # If we got the lock, it wasn't locked
                fcntl.flock(fd, fcntl.LOCK_UN)
            return None
        except BlockingIOError:
            # Lock is held - read info
            os.lseek(fd, 0, os.SEEK_SET)
            holder_info = os.read(fd, 1024).decode()
            parts = holder_info.split("|")
            
            if len(parts) >= 2:
                return LockInfo(
                    resource_id=resource_id,
                    user_id=parts[0],
                    acquired_at=datetime.fromisoformat(parts[1]),
                    lock_file=lock_file,
                )
            return None
        finally:
            os.close(fd)
    except Exception:
        return None


def clear_stale_locks(max_age_seconds: float = 3600.0) -> int:
    """
    Clear locks older than max_age_seconds.
    
    Safety cleanup function to remove locks that may have been orphaned
    due to process crashes.
    
    Args:
        max_age_seconds: Maximum age for a lock before it's considered stale
        
    Returns:
        Number of stale locks cleared
    """
    lock_dir = _get_lock_directory()
    cleared = 0
    now = time.time()
    
    for lock_file in lock_dir.glob("*.lock"):
        try:
            # Check file modification time
            mtime = lock_file.stat().st_mtime
            age = now - mtime
            
            if age > max_age_seconds:
                lock_file.unlink()
                cleared += 1
        except Exception:
            pass  # Best effort cleanup
    
    return cleared
