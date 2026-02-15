"""
Auto-Cleanup Manager - Automatic Debug Marker Removal

Purpose:
    Prevents marker pollution by automatically removing CORTEX_DEBUG markers
    when debug sessions are resolved (tests pass, issues fixed).

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Execution Plan Stage 3

Strategies:
    - on_success: Remove markers when all tests pass
    - time_based: Notify developer if markers > 24 hours old

AC-ID: AC-WAVE-R-005
"""

from typing import Dict, List, Set
from pathlib import Path
from datetime import datetime, timedelta
import re


class AutoCleanupManager:
    """
    Manages automatic cleanup of debug markers.
    
    Strategies:
    - Detect resolved sessions (all tests passing)
    - Remove markers for resolved sessions
    - Identify stale markers (> 24 hours)
    - Notify developer of stale markers
    
    Example:
        >>> manager = AutoCleanupManager()
        >>> resolved = manager.cleanup_resolved_sessions(active_sessions)
        >>> # Returns list of resolved session IDs
    """
    
    def __init__(self):
        """Initialize AutoCleanupManager."""
        self.marker_pattern = re.compile(
            r"# CORTEX_DEBUG_START.*?# CORTEX_DEBUG_END",
            re.DOTALL
        )
    
    def cleanup_resolved_sessions(
        self,
        active_sessions: Dict[str, any]
    ) -> List[str]:
        """
        Cleanup markers for resolved sessions.
        
        Logic:
        1. Identify active sessions with status="active"
        2. Scan all tracked files for markers
        3. Remove markers for sessions NOT in active list
        
        Args:
            active_sessions: Dict of session_id -> DebugSession
        
        Returns:
            List of resolved session IDs
        """
        resolved_sessions = []
        
        # Get list of session IDs that should remain active
        active_session_ids = {
            session_id
            for session_id, session in active_sessions.items()
            if session.status == "active"
        }
        
        # Collect all files with markers
        files_with_markers = self._find_files_with_markers()
        
        for file_path in files_with_markers:
            try:
                content = file_path.read_text()
                
                # Find all markers in file
                matches = self.marker_pattern.findall(content)
                
                for session_id in matches:
                    # If session not in active list, remove markers
                    if session_id not in active_session_ids:
                        content = self._remove_marker(content, session_id)
                        resolved_sessions.append(session_id)
                
                # Write cleaned content
                file_path.write_text(content)
                
            except Exception as e:
                print(f"Error cleaning {file_path}: {e}")
                continue
        
        return list(set(resolved_sessions))  # Deduplicate
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        Cleanup markers for specific session.
        
        Args:
            session_id: Session ID to cleanup
        
        Returns:
            True if cleanup successful
        """
        files_with_markers = self._find_files_with_markers()
        cleaned = False
        
        for file_path in files_with_markers:
            try:
                content = file_path.read_text()
                
                if session_id in content:
                    content = self._remove_marker(content, session_id)
                    file_path.write_text(content)
                    cleaned = True
                    
            except Exception:
                continue
        
        return cleaned
    
    def check_stale_markers(self, max_age_hours: int = 24) -> List[Dict[str, any]]:
        """
        Identify stale markers (older than max_age_hours).
        
        Args:
            max_age_hours: Maximum age in hours before marker is stale
        
        Returns:
            List of dicts with {session_id, file_path, age_hours, timestamp}
        """
        stale_markers = []
        files_with_markers = self._find_files_with_markers()
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        for file_path in files_with_markers:
            try:
                content = file_path.read_text()
                
                # Find markers with timestamps
                marker_pattern_with_timestamp = re.compile(
                    r'.*?# Injected: ([^\n]+)\n',
                    re.DOTALL
                )
                
                matches = marker_pattern_with_timestamp.findall(content)
                
                for session_id, timestamp_str in matches:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
                        
                        if timestamp < cutoff:
                            stale_markers.append({
                                "session_id": session_id,
                                "file_path": str(file_path),
                                "age_hours": age_hours,
                                "timestamp": timestamp_str
                            })
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return stale_markers
    
    def _find_files_with_markers(self) -> List[Path]:
        """
        Find all files containing CORTEX_DEBUG markers.
        
        Returns:
            List of file paths
        """
        # Search in cortex/ directory for .py files
        cortex_dir = Path("cortex")
        if not cortex_dir.exists():
            return []
        
        files_with_markers = []
        
        for py_file in cortex_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "CORTEX_DEBUG" in content:
                    files_with_markers.append(py_file)
            except Exception:
                continue
        
        return files_with_markers
    
    def _remove_marker(self, content: str, session_id: str) -> str:
        """
        Remove marker for specific session from content.
        
        Args:
            content: File content
            session_id: Session ID to remove
        
        Returns:
            Content with marker removed
        """
        # Pattern to match specific session marker
        pattern = re.compile(
            r'# CORTEX_DEBUG_START.*?# CORTEX_DEBUG_END\n?',
            re.DOTALL
        )
        
        return pattern.sub('', content)
