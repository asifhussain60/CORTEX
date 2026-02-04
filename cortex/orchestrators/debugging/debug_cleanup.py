"""
CORTEX Debug Cleanup
====================

Safe cleanup tool that removes ONLY CORTEX debug markers from injected files,
leaving the original code intact and production-ready.

Author: CORTEX
Version: 1.0.0
Phase: Phase 21.5 - Universal Debugging

Safety Features:
- Only removes lines containing CORTEX_DEBUG_ markers
- Verifies cleanup by scanning for remaining markers
- Can restore from backup if cleanup fails
- Logs all changes for audit trail
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import logging
import re
import shutil

logger = logging.getLogger(__name__)

# Marker prefix constant
CORTEX_DEBUG_MARKER = "CORTEX_DEBUG_"


@dataclass
class CleanupResult:
    """Result of cleanup operation for a single file."""
    
    file_path: Path
    original_line_count: int
    cleaned_line_count: int
    markers_removed: int
    success: bool = True
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": str(self.file_path),
            "original_lines": self.original_line_count,
            "cleaned_lines": self.cleaned_line_count,
            "markers_removed": self.markers_removed,
            "success": self.success,
            "error": self.error,
        }


class DebugCleanup:
    """
    Safe cleanup tool for removing CORTEX debug markers.
    
    Removes ONLY lines that contain CORTEX_DEBUG_ markers,
    ensuring the original code logic remains intact.
    """
    
    def __init__(
        self,
        session_id: str,
        repo_path: Path,
        output_dir: Path,
    ):
        self.session_id = session_id
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = Path(output_dir)
        self.backup_dir = self.output_dir / "backups"
        
        logger.info(f"DebugCleanup initialized for session {session_id}")
    
    def cleanup(
        self,
        injected_files: List[str],
        verify: bool = True,
    ) -> Dict[str, Any]:
        """
        Remove all CORTEX debug markers from injected files.
        
        Args:
            injected_files: List of files that were injected
            verify: Run verification after cleanup
        
        Returns:
            Cleanup result with verification status
        """
        logger.info(f"Starting cleanup for {len(injected_files)} files")
        
        results = {
            "session_id": self.session_id,
            "cleanup_time": datetime.now().isoformat(),
            "cleaned_files": [],
            "total_markers_removed": 0,
            "files_processed": 0,
            "files_failed": 0,
            "verified": False,
            "remaining_markers": [],
            "errors": [],
        }
        
        for rel_path in injected_files:
            file_path = self.repo_path / rel_path
            
            if not file_path.exists():
                logger.warning(f"File not found for cleanup: {file_path}")
                results["errors"].append(f"File not found: {rel_path}")
                results["files_failed"] += 1
                continue
            
            try:
                cleanup_result = self._cleanup_file(file_path)
                
                if cleanup_result.success:
                    results["cleaned_files"].append(str(rel_path))
                    results["total_markers_removed"] += cleanup_result.markers_removed
                    results["files_processed"] += 1
                    logger.info(f"Cleaned {rel_path}: removed {cleanup_result.markers_removed} markers")
                else:
                    results["errors"].append(cleanup_result.error)
                    results["files_failed"] += 1
            
            except Exception as e:
                error_msg = f"Failed to cleanup {rel_path}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
                results["files_failed"] += 1
        
        # Verify cleanup
        if verify:
            verification = self._verify_cleanup()
            results["verified"] = verification["clean"]
            results["remaining_markers"] = verification["remaining"]
            
            if not verification["clean"]:
                logger.warning(f"Verification failed: {len(verification['remaining'])} markers remain")
        
        # Save cleanup report
        self._save_cleanup_report(results)
        
        logger.info(f"Cleanup complete: {results['total_markers_removed']} markers removed from {results['files_processed']} files")
        
        return results
    
    def _cleanup_file(self, file_path: Path) -> CleanupResult:
        """Clean a single file by removing CORTEX debug markers."""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_lines = content.split('\n')
            original_count = len(original_lines)
            
            # Remove lines containing CORTEX_DEBUG_ markers
            cleaned_lines = []
            markers_removed = 0
            
            for line in original_lines:
                if CORTEX_DEBUG_MARKER in line:
                    # Check if it's a standalone debug line (only console.log/print)
                    stripped = line.strip()
                    
                    # JavaScript: console.log('[CORTEX_DEBUG_...]');
                    if stripped.startswith('console.log(') and CORTEX_DEBUG_MARKER in stripped:
                        markers_removed += 1
                        continue
                    
                    # JavaScript: console.error('[CORTEX_DEBUG_...]');
                    if stripped.startswith('console.error(') and CORTEX_DEBUG_MARKER in stripped:
                        markers_removed += 1
                        continue
                    
                    # JavaScript: console.warn('[CORTEX_DEBUG_...]');
                    if stripped.startswith('console.warn(') and CORTEX_DEBUG_MARKER in stripped:
                        markers_removed += 1
                        continue
                    
                    # Python: print("[CORTEX_DEBUG_...]")
                    if stripped.startswith('print(') and CORTEX_DEBUG_MARKER in stripped:
                        markers_removed += 1
                        continue
                    
                    # If it's embedded in other code, we need to be more careful
                    # For now, keep the line but log a warning
                    logger.warning(f"Found embedded marker in {file_path}:{original_lines.index(line)+1}")
                
                cleaned_lines.append(line)
            
            # Write cleaned content
            cleaned_content = '\n'.join(cleaned_lines)
            file_path.write_text(cleaned_content, encoding='utf-8')
            
            return CleanupResult(
                file_path=file_path,
                original_line_count=original_count,
                cleaned_line_count=len(cleaned_lines),
                markers_removed=markers_removed,
                success=True,
            )
        
        except Exception as e:
            return CleanupResult(
                file_path=file_path,
                original_line_count=0,
                cleaned_line_count=0,
                markers_removed=0,
                success=False,
                error=str(e),
            )
    
    def _verify_cleanup(self) -> Dict[str, Any]:
        """Verify that no CORTEX markers remain in the repository."""
        remaining = []
        
        # Scan all supported file types
        patterns = ["**/*.js", "**/*.ts", "**/*.py", "**/*.html"]
        exclude = ["**/node_modules/**", "**/.git/**", "**/.cortex-debug/**", "**/vendor/**"]
        
        for pattern in patterns:
            for file_path in self.repo_path.glob(pattern):
                # Check exclusions
                rel_path = str(file_path.relative_to(self.repo_path))
                skip = False
                for exc in exclude:
                    if rel_path.startswith(exc.replace("**/*", "").replace("**", "")):
                        skip = True
                        break
                
                if skip:
                    continue
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if CORTEX_DEBUG_MARKER in content:
                        # Find specific lines
                        for i, line in enumerate(content.split('\n'), 1):
                            if CORTEX_DEBUG_MARKER in line:
                                remaining.append({
                                    "file": str(file_path.relative_to(self.repo_path)),
                                    "line": i,
                                    "content": line.strip()[:100],
                                })
                except Exception as e:
                    logger.warning(f"Could not read {file_path} during verification: {e}")
        
        return {
            "clean": len(remaining) == 0,
            "remaining": remaining,
        }
    
    def restore_from_backup(self) -> Dict[str, Any]:
        """Restore all files from backup (emergency recovery)."""
        results = {
            "restored_files": [],
            "errors": [],
        }
        
        if not self.backup_dir.exists():
            results["errors"].append("No backup directory found")
            return results
        
        # Load injection map to get file mappings
        map_path = self.output_dir / "injection-map.json"
        if not map_path.exists():
            results["errors"].append("No injection map found")
            return results
        
        try:
            with open(map_path, 'r') as f:
                injection_map = json.load(f)
            
            for rel_path, file_info in injection_map.get("files", {}).items():
                backup_path = Path(file_info.get("backup", ""))
                target_path = self.repo_path / rel_path
                
                if backup_path.exists():
                    try:
                        backup_content = backup_path.read_text(encoding='utf-8')
                        target_path.write_text(backup_content, encoding='utf-8')
                        results["restored_files"].append(rel_path)
                        logger.info(f"Restored {rel_path} from backup")
                    except Exception as e:
                        results["errors"].append(f"Failed to restore {rel_path}: {e}")
                else:
                    results["errors"].append(f"Backup not found for {rel_path}")
        
        except Exception as e:
            results["errors"].append(f"Failed to load injection map: {e}")
        
        return results
    
    def _save_cleanup_report(self, results: Dict[str, Any]):
        """Save cleanup report to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = self.output_dir / "cleanup-report.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Cleanup report saved to {report_path}")


def verify_no_markers(repo_path: Path) -> Dict[str, Any]:
    """
    Standalone verification function to check for any CORTEX markers.
    
    Can be used as a pre-commit hook or CI check.
    
    Args:
        repo_path: Path to repository to scan
    
    Returns:
        Verification result with any remaining markers
    """
    cleanup = DebugCleanup(
        session_id="verify",
        repo_path=repo_path,
        output_dir=repo_path / ".cortex-debug",
    )
    return cleanup._verify_cleanup()
