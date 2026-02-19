"""
AutoCleanupManager - Manages automatic cleanup of debug markers after test passes.

Purpose:
    Tracks injected debug marker files and removes them when test sessions
    complete successfully, keeping the codebase free of temporary markers.

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - CORE-035 (Single Canonical Implementation)

AC-ID: AC-WAVE-R-005
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)


class AutoCleanupManager:
    """
    Manages automatic cleanup of debug marker files injected during debugging sessions.

    Tracks which files have been modified by the MarkerInjectionEngine and
    restores them to their original state once test sessions succeed or are
    explicitly completed.
    """

    def __init__(self) -> None:
        """Initialise the cleanup manager with empty tracking state."""
        self._tracked_files: Dict[str, List[str]] = {}  # session_id -> [file_paths]
        self._cleaned_sessions: Set[str] = set()

    def register_file(self, session_id: str, file_path: str) -> None:
        """
        Register a file as having been modified by a debug session.

        Args:
            session_id: The debug session that modified the file.
            file_path: Absolute or relative path to the modified file.
        """
        if session_id not in self._tracked_files:
            self._tracked_files[session_id] = []
        if file_path not in self._tracked_files[session_id]:
            self._tracked_files[session_id].append(file_path)
            logger.debug("Registered file %s for session %s cleanup", file_path, session_id)

    def cleanup_session(self, session_id: str) -> bool:
        """
        Remove debug markers from all files registered under the given session.

        Args:
            session_id: The session whose files should be cleaned up.

        Returns:
            True if cleanup completed (even if some files were already clean),
            False if the session was not found.
        """
        if session_id not in self._tracked_files:
            logger.warning("cleanup_session: unknown session_id=%s", session_id)
            return False

        files = self._tracked_files.pop(session_id, [])
        for file_path in files:
            try:
                self._strip_markers(file_path)
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to clean %s: %s", file_path, exc)

        self._cleaned_sessions.add(session_id)
        logger.info("AutoCleanupManager: cleaned %d files for session %s", len(files), session_id)
        return True

    def cleanup_resolved_sessions(self, active_sessions: Dict) -> List[str]:
        """
        Clean up all sessions whose status is 'resolved' in *active_sessions*.

        This is called by DebuggerOrchestrator on TESTS_PASSED events.
        After cleanup the session files are stripped of debug markers.

        Args:
            active_sessions: Dict mapping session_id → DebugSession objects
                             (must have a ``.status`` attribute).

        Returns:
            List of session IDs that were cleaned up.
        """
        resolved: List[str] = []
        for session_id, session in list(active_sessions.items()):
            status = getattr(session, "status", None)
            if status == "resolved":
                self.cleanup_session(session_id)
                resolved.append(session_id)

        logger.info(
            "cleanup_resolved_sessions: cleaned %d resolved sessions", len(resolved)
        )
        return resolved

    def cleanup_all(self) -> int:
        """
        Clean up all currently tracked sessions.

        Returns:
            Number of sessions cleaned.
        """
        session_ids = list(self._tracked_files.keys())
        for sid in session_ids:
            self.cleanup_session(sid)
        return len(session_ids)

    def get_tracked_files(self, session_id: str) -> List[str]:
        """
        Return the list of files currently tracked for a session.

        Args:
            session_id: The session to query.

        Returns:
            List of file paths (may be empty if session is unknown or already cleaned).
        """
        return list(self._tracked_files.get(session_id, []))

    def is_session_cleaned(self, session_id: str) -> bool:
        """
        Check whether a session has already been cleaned up.

        Args:
            session_id: The session to query.

        Returns:
            True if the session was already cleaned, False otherwise.
        """
        return session_id in self._cleaned_sessions

    # ──────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────

    _MARKER_START = "# CORTEX_DEBUG_MARKER_START"
    _MARKER_END = "# CORTEX_DEBUG_MARKER_END"

    def _strip_markers(self, file_path: str) -> None:
        """
        Remove CORTEX debug marker blocks from a source file in-place.

        Marker blocks are delimited by ``# CORTEX_DEBUG_MARKER_START`` and
        ``# CORTEX_DEBUG_MARKER_END`` comment lines.

        Args:
            file_path: Path to the file to clean.
        """
        path = Path(file_path)
        if not path.exists():
            logger.debug("_strip_markers: %s does not exist, skipping", file_path)
            return

        original = path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)

        cleaned: List[str] = []
        inside_marker = False
        for line in lines:
            if self._MARKER_START in line:
                inside_marker = True
                continue
            if self._MARKER_END in line:
                inside_marker = False
                continue
            if not inside_marker:
                cleaned.append(line)

        if len(cleaned) != len(lines):
            path.write_text("".join(cleaned), encoding="utf-8")
            logger.info("_strip_markers: removed debug markers from %s", file_path)
