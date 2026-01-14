"""
Infrastructure Cleanup Daemon (AC-CLEAN-202)

Autonomous background cleanup of .gitignore-d artifacts.
Zero false positives by design (gitignore-scoped only).

Author: GitHub Copilot + Asif Hussain
Date: 2026-01-12
Status: Implementation for AC-CLEAN-202
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import threading
import time
import subprocess


@dataclass
class DaemonCleanupSummary:
    """Summary of daemon cleanup execution."""
    execution_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + 'Z')
    total_files_deleted: int = 0
    total_bytes_freed: int = 0
    total_errors: int = 0
    duration_ms: int = 0
    patterns_checked: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for audit logging."""
        return {
            'execution_timestamp': self.execution_timestamp,
            'total_files_deleted': self.total_files_deleted,
            'total_bytes_freed': self.total_bytes_freed,
            'total_errors': self.total_errors,
            'duration_ms': self.duration_ms,
            'patterns_checked': self.patterns_checked
        }


class GitignoreScanner:
    """Parse and apply .gitignore patterns for cleanup scope."""
    
    def __init__(self, workspace_root: Path):
        """Initialize scanner."""
        self.workspace_root = workspace_root
        self.patterns: List[str] = []
        self.negations: List[str] = []
        self._parse_gitignore()
    
    def _parse_gitignore(self) -> None:
        """Parse .gitignore file."""
        gitignore_path = self.workspace_root / ".gitignore"
        
        if not gitignore_path.exists():
            return
        
        try:
            with open(gitignore_path, 'r') as f:
                for line in f:
                    line = line.rstrip('\n')
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Handle negations
                    if line.startswith('!'):
                        self.negations.append(line[1:])
                    else:
                        self.patterns.append(line)
        except Exception:
            pass
    
    def should_delete(self, file_path: Path) -> bool:
        """Check if file should be deleted per .gitignore rules."""
        rel_path = file_path.relative_to(self.workspace_root)
        rel_str = str(rel_path)
        
        # Check negations first (higher precedence)
        for neg_pattern in self.negations:
            if self._matches_pattern(rel_str, neg_pattern):
                return False
        
        # Check inclusion patterns
        for pattern in self.patterns:
            if self._matches_pattern(rel_str, pattern):
                return True
        
        return False
    
    def _matches_pattern(self, path_str: str, pattern: str) -> bool:
        """Check if path matches gitignore pattern."""
        import fnmatch
        
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            return path_str.startswith(pattern) or fnmatch.fnmatch(path_str, pattern + '/*')
        
        # Handle ** wildcard
        if '**' in pattern:
            # Simplified: treat ** as wildcard at any depth
            pattern = pattern.replace('**/', '*/')
            pattern = pattern.replace('/**', '/*')
        
        return fnmatch.fnmatch(path_str, pattern)


class InfrastructureCleanupDaemon:
    """Autonomous cleanup daemon for .gitignore-d files."""
    
    def __init__(self, workspace_root: Path, schedule: str = 'hourly',
                 audit_logger=None, enabled: bool = True):
        """Initialize daemon."""
        self.workspace_root = workspace_root
        self.schedule = schedule  # 'hourly' or 'background'
        self.audit_logger = audit_logger
        self.enabled = enabled
        self.logger = logging.getLogger(__name__)
        
        self.gitignore_scanner = GitignoreScanner(workspace_root)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_execution: Optional[datetime] = None
        self._protected_patterns = [
            ".git/*",
            ".github/*",
            "cortex-brain/tier0/*",
            "cortex-brain/tier1/*",
            "cortex-brain/database/*",
            ".env*",
            ".secrets*"
        ]
    
    def start(self) -> None:
        """Start daemon if enabled."""
        if not self.enabled:
            return
        
        if self.schedule == 'background':
            self._thread = threading.Thread(target=self._background_loop, daemon=True)
            self._thread.start()
    
    def stop(self) -> None:
        """Stop daemon gracefully."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
    
    def cleanup_now(self) -> DaemonCleanupSummary:
        """Execute cleanup immediately."""
        if not self.enabled:
            return DaemonCleanupSummary()
        
        return self._execute_cleanup_cycle()
    
    def _background_loop(self) -> None:
        """Background daemon loop (hourly execution)."""
        while not self._stop_event.is_set():
            now = datetime.utcnow()
            
            # Execute cleanup if needed (hourly)
            if (self._last_execution is None or 
                (now - self._last_execution) >= timedelta(hours=1)):
                self._execute_cleanup_cycle()
                self._last_execution = now
            
            # Sleep briefly before checking again
            self._stop_event.wait(timeout=60)
    
    def _execute_cleanup_cycle(self) -> DaemonCleanupSummary:
        """Execute one cleanup cycle."""
        start_time = time.time()
        summary = DaemonCleanupSummary()
        
        try:
            # Find all files in workspace
            for file_path in self.workspace_root.rglob('*'):
                if file_path.is_file():
                    self._process_file(file_path, summary)
                elif file_path.is_dir():
                    self._process_directory(file_path, summary)
                
                summary.patterns_checked += 1
        
        except Exception as e:
            self.logger.error(f"Cleanup cycle error: {e}")
            summary.total_errors += 1
        
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            summary.duration_ms = duration_ms
            
            # Log to audit trail
            self._log_summary(summary)
        
        return summary
    
    def _process_file(self, file_path: Path, summary: DaemonCleanupSummary) -> None:
        """Process single file for cleanup."""
        # Check if protected
        if self._is_protected(file_path):
            return
        
        # Check if gitignored
        if self.gitignore_scanner.should_delete(file_path):
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                summary.total_files_deleted += 1
                summary.total_bytes_freed += file_size
            except Exception as e:
                self.logger.warning(f"Could not delete {file_path}: {e}")
                summary.total_errors += 1
    
    def _process_directory(self, dir_path: Path, summary: DaemonCleanupSummary) -> None:
        """Process directory for cleanup."""
        # Check if protected
        if self._is_protected(dir_path):
            return
        
        # Check if gitignored
        if self.gitignore_scanner.should_delete(dir_path):
            # Only delete if directory is empty or contains only gitignored items
            try:
                import shutil
                # Check if empty
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    summary.total_files_deleted += 1
                    return
                
                # Try to delete tree
                try:
                    dir_size = self._get_directory_size(dir_path)
                    shutil.rmtree(dir_path, ignore_errors=False)
                    summary.total_files_deleted += 1
                    summary.total_bytes_freed += dir_size
                except Exception:
                    # If rmtree fails, just skip this directory
                    pass
            
            except Exception as e:
                self.logger.warning(f"Could not cleanup {dir_path}: {e}")
                summary.total_errors += 1
    
    def _is_protected(self, file_path: Path) -> bool:
        """Check if file matches protected patterns."""
        rel_path = file_path.relative_to(self.workspace_root)
        rel_str = str(rel_path)
        
        for pattern in self._protected_patterns:
            import fnmatch
            if pattern.endswith('*'):
                pattern_base = pattern[:-1]
                if rel_str.startswith(pattern_base):
                    return True
            elif fnmatch.fnmatch(rel_str, pattern):
                return True
        
        return False
    
    def _get_directory_size(self, dir_path: Path) -> int:
        """Calculate directory size."""
        total = 0
        try:
            for item in dir_path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total
    
    def _log_summary(self, summary: DaemonCleanupSummary) -> None:
        """Log cleanup summary to audit trail."""
        if self.audit_logger:
            self.audit_logger.log_event(
                category="INFRASTRUCTURE",
                level="INFO",
                message=f"Infrastructure cleanup executed: {summary.total_files_deleted} files deleted, {summary.total_bytes_freed} bytes freed in {summary.duration_ms}ms",
                ac_id="AC-CLEAN-202",
                correlation_id=f"daemon-cleanup-{summary.execution_timestamp}",
                extra=summary.to_dict()
            )
        
        self.logger.info(
            f"Cleanup cycle: {summary.total_files_deleted} files deleted, "
            f"{summary.total_bytes_freed} bytes freed, {summary.duration_ms}ms"
        )
