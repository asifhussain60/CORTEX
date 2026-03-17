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
import re

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
        self.marker_pattern = re.compile(r"CORTEX_DEBUG")

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
        if session_id in self._tracked_files:
            files = self._tracked_files.pop(session_id, [])
        else:
            # Fallback: scan for any files with markers
            logger.info("cleanup_session: no tracked files for %s, scanning via _find_files_with_markers", session_id)
            files = [str(p) for p in self._find_files_with_markers()]

        cleaned = 0
        for file_path in files:
            try:
                self._strip_markers(str(file_path))
                cleaned += 1
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to clean %s: %s", file_path, exc)

        self._cleaned_sessions.add(session_id)
        logger.info("AutoCleanupManager: cleaned %d files for session %s", cleaned, session_id)
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

        # Also clean up any orphaned marker files not tracked by session
        # Only clean orphaned marker files when there are no active sessions
        if not active_sessions:
            orphaned_files = self._find_files_with_markers()
            for file_path in orphaned_files:
                try:
                    self._strip_markers(str(file_path))
                except Exception as exc:  # noqa: BLE001
                    logger.error("Failed to clean orphaned file %s: %s", str(file_path), exc)

        logger.info(
            "cleanup_resolved_sessions: cleaned %d resolved sessions", len(resolved)
        )
        return resolved

    def _find_files_with_markers(self, search_paths: Optional[List[str]] = None) -> List[Path]:
        """Scan for files containing CORTEX debug markers.

        Args:
            search_paths: Optional list of directory/file paths to scan.
                          Defaults to an empty list (no scan unless overridden).

        Returns:
            List of Path objects for files containing markers.
        """
        found: List[Path] = []
        paths_to_search = search_paths or []
        for path_str in paths_to_search:
            path = Path(path_str)
            if path.is_file():
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    if self.marker_pattern.search(content):
                        found.append(path)
                except Exception:  # noqa: BLE001
                    pass
            elif path.is_dir():
                for file_path in path.rglob("*.py"):
                    try:
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        if self.marker_pattern.search(content):
                            found.append(file_path)
                    except Exception:  # noqa: BLE001
                        pass
        return found

    def check_stale_markers(self, max_age_hours: int = 24) -> List[Dict]:
        """Scan marker files and return those older than *max_age_hours*.

        Args:
            max_age_hours: Markers injected more than this many hours ago are stale.

        Returns:
            List of dicts with keys: ``session_id``, ``age_hours``, ``file_path``.
        """
        from datetime import datetime, timezone
        stale: List[Dict] = []
        files = self._find_files_with_markers()
        for file_path in files:
            try:
                content = Path(str(file_path)).read_text(encoding="utf-8", errors="ignore")
                # Extract injection timestamp from "# Injected: <ISO-timestamp>" line
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("# Injected:"):
                        ts_str = stripped.split(":", 1)[1].strip()
                        try:
                            injected_at = datetime.fromisoformat(ts_str)
                            # Make naive comparison (strip timezone info)
                            now = datetime.now()
                            if injected_at.tzinfo is not None:
                                now = datetime.now(timezone.utc)
                            delta = now - injected_at
                            age_hours = delta.total_seconds() / 3600
                            if age_hours > max_age_hours:
                                stale.append({
                                    "session_id": "unknown",
                                    "age_hours": age_hours,
                                    "file_path": str(file_path),
                                })
                        except ValueError:
                            pass
                        break
            except Exception:  # noqa: BLE001
                pass
        return stale

    def _remove_marker(self, content: str, session_id: str) -> str:
        """Remove marker blocks tagged with *session_id* from *content*.

        If the marker blocks do not carry a session tag, they are left
        untouched so that markers belonging to other sessions are preserved.

        Args:
            content: Text content of a source file.
            session_id: ID of the session whose markers should be removed.

        Returns:
            Content with the matching session's markers removed.
        """
        import re
        # Only remove blocks explicitly tagged with this session_id
        # e.g. "# CORTEX_DEBUG_START: session-001"
        # Plain "# CORTEX_DEBUG_START" blocks (no session tag) are left untouched
        # so that other sessions' content is preserved.
        pattern = re.compile(
            r"#\s*CORTEX_DEBUG_START:\s*" + re.escape(session_id) + r"\n"
            r".*?"
            r"#\s*CORTEX_DEBUG_END[^\n]*\n?",
            re.DOTALL,
        )
        return pattern.sub("", content)

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

    # Phase 86 — multi-language marker patterns (regex fragments matched per line)
    _MULTI_LANG_MARKER_PATTERNS: List[str] = [
        "CORTEX_DEBUG",          # universal token (Python, JS, SQL, C#)
        "console.debug.*CORTEX", # FrontendConsoleStrategy
        "data-cortex-debug",     # HtmlVisionMappingStrategy
        "CORTEX_DEBUG_API_TRACE",# ApiTraceStrategy
        r"-- CORTEX_DEBUG",      # SqlTraceStrategy
        r"_logger\.LogDebug.*CORTEX_DEBUG",  # DotNetTraceStrategy
        r"cortex_trace_request", # ApiTraceStrategy helper
        r"// CORTEX_DEBUG",      # C# single-line comment marker
        r"<!-- CORTEX_DEBUG",    # HTML comment marker
    ]

    def _strip_markers(self, file_path: str) -> None:
        """Remove CORTEX debug marker blocks from a source file in-place.

        Phase 86: Handles Python block markers (CORTEX_DEBUG_MARKER_START/END),
        JavaScript console.debug markers, HTML data-cortex-debug comments,
        SQL -- CORTEX_DEBUG comments, and C# ILogger.LogDebug markers.

        Args:
            file_path: Path to the file to clean.
        """
        import re
        path = Path(file_path)
        if not path.exists():
            logger.debug("_strip_markers: %s does not exist, skipping", file_path)
            return

        original = path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)

        cleaned: List[str] = []
        inside_marker = False
        removed = 0
        for line in lines:
            # Python block markers
            if self._MARKER_START in line:
                inside_marker = True
                removed += 1
                continue
            if self._MARKER_END in line:
                inside_marker = False
                removed += 1
                continue
            if inside_marker:
                removed += 1
                continue
            # Phase 86: single-line multi-language markers
            stripped = line.strip()
            is_marker = any(
                re.search(pattern, stripped)
                for pattern in self._MULTI_LANG_MARKER_PATTERNS
            )
            if is_marker:
                removed += 1
                continue
            cleaned.append(line)

        if removed > 0:
            path.write_text("".join(cleaned), encoding="utf-8")
            logger.info(
                "_strip_markers: removed %d debug marker lines from %s", removed, file_path
            )
