"""
Debug Marker Cleanup - Remove all CORTEX_DEBUG_ markers

One-shot cleanup of all debug markers with verification.

Author: Asif Hussain
Created: January 4, 2026
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DebugMarkerCleanup:
    """Cleans up debug markers from workspace."""
    
    MARKER_PATTERNS = [
        r'# CORTEX_DEBUG_START.*?# CORTEX_DEBUG_END\n',  # Python block
        r'// CORTEX_DEBUG_START.*?// CORTEX_DEBUG_END\n',  # JavaScript block
        r'/\* CORTEX_DEBUG_START.*?\* CORTEX_DEBUG_END \*/\n',  # C-style block
    ]
    
    def __init__(self, workspace_root: Path):
        """Initialize marker cleanup."""
        self.workspace_root = workspace_root
        self.logger = logger
    
    def cleanup_all_markers(
        self,
        session_id: Optional[str] = None,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Remove all debug markers in one operation.
        
        Implements: DBG-004 (One-Shot Marker Cleanup)
        
        Args:
            session_id: Optional session ID to clean only specific session markers
            verify: Whether to verify zero markers remain
            
        Returns:
            Cleanup results with verification status
        """
        self.logger.info(f"Starting marker cleanup (session_id: {session_id or 'all'})")
        
        # Find all files with markers
        files_with_markers = self._find_files_with_markers(session_id)
        
        markers_removed = 0
        files_cleaned = []
        
        for file_path in files_with_markers:
            removed = self._clean_file(file_path, session_id)
            if removed > 0:
                markers_removed += removed
                files_cleaned.append(str(file_path))
        
        # Verify cleanup
        verification_passed = True
        if verify:
            remaining = self.count_remaining_markers(session_id)
            verification_passed = remaining == 0
            
            if not verification_passed:
                self.logger.error(f"Verification failed: {remaining} markers remain")
            else:
                self.logger.info("Verification passed: zero markers remain")
        
        return {
            "status": "success" if verification_passed else "incomplete",
            "markers_removed": markers_removed,
            "files_cleaned": files_cleaned,
            "file_count": len(files_cleaned),
            "verification_passed": verification_passed,
        }
    
    def _find_files_with_markers(self, session_id: Optional[str] = None) -> List[Path]:
        """Find all files containing debug markers."""
        files_with_markers = []
        
        # Search in common source directories
        search_dirs = ['src', 'tests', 'scripts']
        
        for search_dir in search_dirs:
            dir_path = self.workspace_root / search_dir
            if not dir_path.exists():
                continue
            
            # Find Python and JavaScript files
            for ext in ['*.py', '*.js', '*.jsx', '*.ts', '*.tsx']:
                for file_path in dir_path.rglob(ext):
                    if self._file_contains_markers(file_path, session_id):
                        files_with_markers.append(file_path)
        
        self.logger.info(f"Found {len(files_with_markers)} files with markers")
        return files_with_markers
    
    def _file_contains_markers(self, file_path: Path, session_id: Optional[str] = None) -> bool:
        """Check if file contains debug markers."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for marker start tags
            if session_id:
                return f"CORTEX_DEBUG_START - Session: {session_id}" in content
            else:
                return "CORTEX_DEBUG_START" in content
        
        except Exception as e:
            self.logger.warning(f"Error reading {file_path}: {e}")
            return False
    
    def _clean_file(self, file_path: Path, session_id: Optional[str] = None) -> int:
        """Clean markers from a single file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            markers_removed = 0
            
            # Apply each pattern
            for pattern in self.MARKER_PATTERNS:
                if session_id:
                    # Make pattern session-specific
                    session_pattern = pattern.replace(
                        r'CORTEX_DEBUG_START',
                        rf'CORTEX_DEBUG_START - Session: {session_id}'
                    )
                    matches = re.findall(session_pattern, content, re.DOTALL)
                    content = re.sub(session_pattern, '', content, flags=re.DOTALL)
                else:
                    matches = re.findall(pattern, content, re.DOTALL)
                    content = re.sub(pattern, '', content, flags=re.DOTALL)
                
                markers_removed += len(matches)
            
            # Write cleaned content (dry-run mode - commented out)
            # if content != original_content:
            #     with open(file_path, 'w') as f:
            #         f.write(content)
            #     self.logger.info(f"Cleaned {markers_removed} markers from {file_path}")
            
            # For now, just log what would be done
            if content != original_content:
                self.logger.info(f"Would clean {markers_removed} markers from {file_path}")
            
            return markers_removed
        
        except Exception as e:
            self.logger.error(f"Error cleaning {file_path}: {e}")
            return 0
    
    def count_remaining_markers(self, session_id: Optional[str] = None) -> int:
        """Count remaining markers in workspace."""
        files_with_markers = self._find_files_with_markers(session_id)
        
        total_markers = 0
        for file_path in files_with_markers:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Count START markers
                if session_id:
                    count = content.count(f"CORTEX_DEBUG_START - Session: {session_id}")
                else:
                    count = content.count("CORTEX_DEBUG_START")
                
                total_markers += count
            except Exception as e:
                self.logger.warning(f"Error counting markers in {file_path}: {e}")
        
        return total_markers
