"""
File Locking Utility for CORTEX

Provides cross-platform file locking for safe concurrent file operations.
Prevents race conditions in DebugOrchestrator and other file operations.

AC_START: AC-ENH-063-P2-005
Description: ENH-063 Phase 2 - File locking for concurrent operations
Authority: ENH-063 Production Architecture Remediation
Testing: tests/unit/infrastructure/test_file_lock.py (TDD)

Platform Support:
- Unix/Linux/macOS: fcntl module (POSIX file locking)
- Windows: msvcrt module (Windows file locking)

Usage:
    from cortex.infrastructure.file_lock import FileLock

    with FileLock("/path/to/file.txt", timeout=5.0):
        # Exclusive access to file
        with open("/path/to/file.txt", "w") as f:
            f.write("data")
"""

import logging
import platform
import time
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Optional

logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    import msvcrt  # type: ignore
else:
    import fcntl


class FileLockError(Exception):
    """Raised when file locking fails."""
    pass


class FileLockTimeout(FileLockError):
    """Raised when lock acquisition times out."""
    pass


class FileLock:
    """
    Cross-platform file locking context manager.

    Provides exclusive file locking to prevent race conditions
    during concurrent file operations.

    Features:
    - Cross-platform (Unix/Windows)
    - Timeout support (prevents deadlocks)
    - Automatic lock release
    - Audit logging

    Example:
        >>> from cortex.infrastructure.file_lock import FileLock
        >>>
        >>> with FileLock("/path/to/file.txt", timeout=5.0):
        ...     with open("/path/to/file.txt", "w") as f:
        ...         f.write("safe write")
    """

    def __init__(
        self,
        file_path: str,
        timeout: float = 5.0,
        check_interval: float = 0.1,
    ) -> None:
        """
        Initialize file lock.

        Args:
            file_path: Path to file to lock
            timeout: Maximum time to wait for lock (seconds)
            check_interval: Interval between lock attempts (seconds)
        """
        self.file_path = Path(file_path).resolve()
        self.lock_path = self.file_path.with_suffix(self.file_path.suffix + ".lock")
        self.timeout = timeout
        self.check_interval = check_interval
        self.lock_file: Optional[IO[str]] = None

        logger.debug(f"FileLock initialized: {self.file_path}")

    def __enter__(self) -> "FileLock":
        """Acquire file lock."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Release file lock."""
        self.release()

    def acquire(self) -> None:
        """
        Acquire exclusive file lock.

        Raises:
            FileLockTimeout: If lock acquisition times out
            FileLockError: If lock acquisition fails
        """
        start_time = time.time()

        logger.debug(f"Acquiring lock: {self.lock_path}")

        while True:
            try:
                # Create lock file and acquire lock
                self.lock_file = open(self.lock_path, "w")

                if IS_WINDOWS:
                    # Windows file locking
                    msvcrt.locking(  # type: ignore
                        self.lock_file.fileno(),
                        msvcrt.LK_NBLCK,  # type: ignore # Non-blocking exclusive lock
                        1,
                    )
                else:
                    # Unix file locking
                    fcntl.flock(
                        self.lock_file.fileno(),
                        fcntl.LOCK_EX | fcntl.LOCK_NB,  # Exclusive non-blocking
                    )

                logger.info(f"Lock acquired: {self.lock_path}")
                return

            except (IOError, OSError) as e:
                # Lock failed, check timeout
                elapsed = time.time() - start_time

                if elapsed >= self.timeout:
                    if self.lock_file:
                        self.lock_file.close()
                        self.lock_file = None

                    logger.error(
                        f"Lock acquisition timeout after {elapsed:.2f}s: {self.lock_path}"
                    )
                    raise FileLockTimeout(
                        f"Failed to acquire lock on {self.file_path} "
                        f"after {elapsed:.2f}s (timeout: {self.timeout}s)"
                    )

                # Wait and retry
                time.sleep(self.check_interval)

                if self.lock_file:
                    self.lock_file.close()
                    self.lock_file = None

            except Exception as e:
                if self.lock_file:
                    self.lock_file.close()
                    self.lock_file = None

                logger.error(f"Unexpected error acquiring lock: {self.lock_path}: {e}")
                raise FileLockError(f"Failed to acquire lock: {e}")

    def release(self) -> None:
        """
        Release file lock.

        Automatically called on context manager exit.
        """
        if self.lock_file is None:
            return

        try:
            if IS_WINDOWS:
                # Windows unlock
                try:
                    msvcrt.locking(  # type: ignore
                        self.lock_file.fileno(),
                        msvcrt.LK_UNLCK,  # type: ignore
                        1,
                    )
                except (ValueError, OSError) as e:
                    # CORE-013: Specific exception handling for unlock failures
                    logger.debug(f"Lock unlock warning: {type(e).__name__}: {e}")
            else:
                # Unix unlock
                try:
                    fcntl.flock(
                        self.lock_file.fileno(),
                        fcntl.LOCK_UN,
                    )
                except (ValueError, OSError) as e:
                    # CORE-013: Specific exception handling for unlock failures
                    logger.debug(f"Lock unlock warning: {type(e).__name__}: {e}")

            self.lock_file.close()
            self.lock_file = None

            # Clean up lock file
            try:
                self.lock_path.unlink()
            except FileNotFoundError:
                pass

            logger.info(f"Lock released: {self.lock_path}")

        except Exception as e:
            logger.error(f"Error releasing lock: {self.lock_path}: {e}")
            raise FileLockError(f"Failed to release lock: {e}")


@contextmanager
def file_lock(file_path: str, timeout: float = 5.0) -> None:
    """
    Context manager for file locking.

    Convenience function that creates and manages FileLock automatically.

    Args:
        file_path: Path to file to lock
        timeout: Maximum time to wait for lock (seconds)

    Yields:
        None (lock is active within context)

    Raises:
        FileLockTimeout: If lock acquisition times out
        FileLockError: If lock acquisition fails

    Example:
        >>> from cortex.infrastructure.file_lock import file_lock
        >>>
        >>> with file_lock("/path/to/file.txt"):
        ...     with open("/path/to/file.txt", "w") as f:
        ...         f.write("safe write")
    """
    lock = FileLock(file_path, timeout=timeout)
    try:
        lock.acquire()
        yield
    finally:
        lock.release()


# AC_COMPLETE: AC-ENH-063-P2-005 ✅ Cross-platform file locking module
