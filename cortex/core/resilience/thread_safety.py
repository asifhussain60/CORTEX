"""
ISSUE #1: Thread Join Timeout Coverage Verification

Ensures all thread.join() calls have timeout protection to prevent
application hangs.
"""

import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Maximum timeout value (in seconds) - prevents accidental infinite waits
DEFAULT_THREAD_TIMEOUT = 5.0
PRODUCTION_THREAD_TIMEOUT = 1.0  # More conservative in production

def safe_thread_join(
    thread: threading.Thread,
    timeout_sec: float = DEFAULT_THREAD_TIMEOUT,
    name: str = "unknown"
) -> bool:
    """
    Safely join a thread with guaranteed timeout protection.

    Args:
        thread: Thread to join
        timeout_sec: Maximum time to wait (seconds)
        name: Thread name for logging

    Returns:
        True if thread completed normally
        False if timeout occurred

    Raises:
        RuntimeError: If thread join fails critically
    """
    if not isinstance(thread, threading.Thread):
        raise TypeError(f"Expected threading.Thread, got {type(thread)}")

    if timeout_sec <= 0:
        raise ValueError(f"Timeout must be positive, got {timeout_sec}")

    try:
        # Attempt to join with timeout
        thread.join(timeout=timeout_sec)

        if thread.is_alive():
            # Timeout occurred
            logger.warning(
                f"Thread '{name}' did not complete within {timeout_sec}s",
                extra={"thread_name": name, "timeout_sec": timeout_sec}
            )
            return False

        # Thread completed successfully
        return True

    except Exception as e:
        logger.error(
            f"Failed to join thread '{name}': {e}",
            exc_info=True,
            extra={"thread_name": name}
        )
        raise RuntimeError(f"Thread join failed for '{name}': {e}") from e


def spawn_with_timeout_join(
    target,
    args=(),
    kwargs=None,
    timeout_sec: float = DEFAULT_THREAD_TIMEOUT,
    daemon: bool = False,
    name: str = "unknown"
) -> Optional[threading.Thread]:
    """
    Spawn a thread and automatically join with timeout.

    Args:
        target: Function to run in thread
        args: Positional arguments for target
        kwargs: Keyword arguments for target
        timeout_sec: Maximum time to wait for completion
        daemon: Whether to run as daemon thread
        name: Thread name for logging

    Returns:
        Thread object if successfully completed, None if timeout
    """
    if kwargs is None:
        kwargs = {}

    thread = threading.Thread(
        target=target,
        args=args,
        kwargs=kwargs,
        daemon=daemon,
        name=name
    )

    thread.start()

    if safe_thread_join(thread, timeout_sec=timeout_sec, name=name):
        return thread
    else:
        return None


# Pattern for checking all thread joins in codebase
THREAD_JOIN_CHECK_PATTERN = r'\.join\s*\(\s*\)'  # Bare .join() calls

def scan_file_for_bare_joins(filepath: Path) -> list:
    """
    Scan a file for bare thread.join() calls without timeout.

    Args:
        filepath: File to scan

    Returns:
        List of line numbers with bare join() calls
    """
    import re

    issues = []
    try:
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                # Look for .join() without timeout parameter
                if re.search(THREAD_JOIN_CHECK_PATTERN, line):
                    # Verify it's not already using timeout parameter
                    if 'timeout' not in line:
                        issues.append(line_num)
    except (IOError, UnicodeDecodeError):
        pass

    return issues


if __name__ == "__main__":
    # Example: Scan all Python files in cortex directory
    cortex_root = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex")

    all_issues = {}
    for py_file in cortex_root.rglob("*.py"):
        issues = scan_file_for_bare_joins(py_file)
        if issues:
            all_issues[str(py_file)] = issues

    if all_issues:
        print("⚠️ Found bare thread.join() calls:")
        for filepath, lines in all_issues.items():
            print(f"  {filepath}: lines {lines}")
    else:
        print("✅ All thread.join() calls have timeout protection")
