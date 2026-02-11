"""
CORTEX MCP Server Wiring File Watcher.

Watches wiring.yaml for changes and reloads without restart in development.

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
"""

import os
import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional


class WiringFileWatcher:
    """
    Watches wiring.yaml for changes and triggers reload callback.

    Thread-safe file watcher for development environment that monitors
    the wiring specification file and calls a reload callback when
    the file is modified.
    """

    def __init__(
        self,
        wiring_path: str = "cortex/wiring/specifications/wiring.yaml",
        on_change_callback: Optional[Callable[[], Any]] = None,
        check_interval: float = 1.0
    ) -> None:
        """
        Initialize wiring file watcher.

        Args:
            wiring_path: Path to wiring.yaml file.
            on_change_callback: Callback function to call when file changes.
            check_interval: Interval in seconds to check for changes.
        """
        self.wiring_path = Path(wiring_path)
        self.on_change_callback = on_change_callback
        self.check_interval = check_interval
        self._last_mtime: float = 0.0
        self._watching = False
        self._watch_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """
        Start watching wiring file for changes.

        Starts a background thread that monitors the wiring file.
        """
        if self._watching:
            return

        with self._lock:
            if not self._watching:
                self._watching = True
                self._watch_thread = threading.Thread(
                    target=self._watch_loop,
                    daemon=True,
                    name="WiringFileWatcher"
                )
                self._watch_thread.start()

    def stop(self) -> None:
        """
        Stop watching wiring file.

        Stops the background watch thread.
        """
        with self._lock:
            self._watching = False

    def _watch_loop(self) -> None:
        """
        Background watch loop.

        Continuously monitors file modification time and calls
        callback when file is modified.
        """
        while self._watching:
            try:
                if self.wiring_path.exists():
                    current_mtime = os.path.getmtime(self.wiring_path)

                    if self._last_mtime == 0:
                        # First check
                        self._last_mtime = current_mtime
                    elif current_mtime > self._last_mtime:
                        # File was modified
                        self._last_mtime = current_mtime

                        if self.on_change_callback:
                            try:
                                self.on_change_callback()
                            except Exception as e:
                                print(f"Error in wiring reload callback: {e}")

                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Error in wiring file watcher: {e}")
                time.sleep(self.check_interval)

    def is_watching(self) -> bool:
        """
        Check if watcher is running.

        Returns:
            True if watcher is actively watching.
        """
        return self._watching


# Global watcher instance
_wiring_watcher: Optional[WiringFileWatcher] = None


def get_wiring_watcher() -> WiringFileWatcher:
    """
    Get or create global wiring file watcher instance.

    Returns:
        Global WiringFileWatcher instance.
    """
    global _wiring_watcher
    if _wiring_watcher is None:
        _wiring_watcher = WiringFileWatcher()
    return _wiring_watcher


def start_wiring_watcher(
    on_change_callback: Optional[Callable[[], Any]] = None
) -> None:
    """
    Start watching wiring file for changes.

    Args:
        on_change_callback: Optional callback to call on file change.
    """
    watcher = get_wiring_watcher()
    if on_change_callback:
        watcher.on_change_callback = on_change_callback
    watcher.start()


def stop_wiring_watcher() -> None:
    """Stop watching wiring file."""
    watcher = get_wiring_watcher()
    watcher.stop()
