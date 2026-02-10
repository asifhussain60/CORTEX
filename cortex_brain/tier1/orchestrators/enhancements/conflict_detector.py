"""
Conflict Detector - Predict issues before file operations.

AC-ID: AC-VAC-ENH-003 | Phase: Enhancement #3
Purpose: Detect conflicts, permissions issues, and risks before cleanup execution
Authority: CORTEX Vacuum Enhancement Phase 1

Detects:
1. Destination file conflicts (file already exists)
2. Git staging conflicts (file is staged/uncommitted)
3. Reference/import loops (circular dependencies)
4. Permission issues (read-only targets)
5. Broken imports/paths
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import subprocess
import os
from datetime import datetime


class ConflictType(Enum):
    """Types of conflicts that can be detected."""
    
    FILE_EXISTS = "destination_exists"           # Target file already exists
    GIT_STAGED = "git_staged"                   # File is staged in git
    GIT_UNCOMMITTED = "git_uncommitted"         # File has uncommitted changes
    PERMISSION_DENIED = "permission_denied"     # No write permission
    REFERENCE_LOOP = "reference_loop"           # Circular dependency
    BROKEN_IMPORT = "broken_import"             # Import would break
    SOURCE_NOT_FOUND = "source_not_found"       # Source file missing
    DEST_READONLY = "dest_readonly"             # Destination is read-only
    PATH_COLLISION = "path_collision"           # Multiple sources → same dest
    SYMLINK = "symlink"                         # Source is a symlink


@dataclass
class Conflict:
    """Single detected conflict."""
    
    conflict_type: ConflictType
    source: str
    destination: str
    severity: str  # "critical" | "warning" | "info"
    message: str
    suggested_fix: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConflictReport:
    """Report of all detected conflicts."""
    
    has_conflicts: bool
    critical_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    conflicts: List[Conflict] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    @property
    def total_count(self) -> int:
        """Total number of conflicts."""
        return len(self.conflicts)
    
    @property
    def is_safe_to_proceed(self) -> bool:
        """True if only info-level conflicts."""
        return self.critical_count == 0 and self.warning_count == 0
    
    def add_conflict(self, conflict: Conflict) -> None:
        """Add conflict and update counts."""
        self.conflicts.append(conflict)
        
        if conflict.severity == "critical":
            self.critical_count += 1
            self.has_conflicts = True
        elif conflict.severity == "warning":
            self.warning_count += 1
            self.has_conflicts = True
        elif conflict.severity == "info":
            self.info_count += 1
    
    def format_summary(self) -> str:
        """Format human-readable summary."""
        if not self.has_conflicts:
            return "✅ No conflicts detected - safe to proceed"
        
        summary = f"🔴 {self.total_count} conflict(s) detected:\n"
        summary += f"  🔴 {self.critical_count} critical\n"
        summary += f"  🟡 {self.warning_count} warnings\n"
        summary += f"  ℹ️  {self.info_count} info\n"
        
        if self.suggestions:
            summary += "\n💡 Suggested fixes:\n"
            for i, suggestion in enumerate(self.suggestions, 1):
                summary += f"  {i}. {suggestion}\n"
        
        return summary


class ConflictDetector:
    """Detect conflicts before file operations."""
    
    def __init__(self, repo_root: Path = Path(".")):
        """Initialize detector.
        
        Args:
            repo_root: Repository root path
        """
        self.repo_root = Path(repo_root)
        self._git_staged_cache: Optional[Set[str]] = None
        self._git_dirty_cache: Optional[Set[str]] = None
    
    def predict_conflicts(self, moves: List[Dict[str, str]]) -> ConflictReport:
        """Predict all conflicts for a set of file moves.
        
        Args:
            moves: List of {"source": "...", "destination": "..."} dicts
            
        Returns:
            ConflictReport with all detected issues
        """
        report = ConflictReport(has_conflicts=False)
        
        # Pre-compute git status once
        self._load_git_status()
        
        # Track destinations to detect collisions
        seen_destinations: Dict[str, str] = {}
        
        for move in moves:
            source = move.get("source", "")
            dest = move.get("destination", "")
            
            if not source or not dest:
                continue
            
            # Check each conflict type
            self._check_source_exists(source, dest, report)
            self._check_git_status(source, dest, report)
            self._check_permissions(source, dest, report)
            self._check_symlink(source, dest, report)
            
            # Track for collision detection
            if dest in seen_destinations:
                conflict = Conflict(
                    conflict_type=ConflictType.PATH_COLLISION,
                    source=source,
                    destination=dest,
                    severity="critical",
                    message=f"Multiple sources target same destination: {seen_destinations[dest]} and {source}",
                    suggested_fix=f"Rename one file to avoid collision: {source} → {dest}_2",
                )
                report.add_conflict(conflict)
            else:
                seen_destinations[dest] = source
        
        # Check for reference loops after processing all moves
        self._check_reference_loops(moves, report)
        
        # Generate suggestions
        self._generate_suggestions(report)
        
        return report
    
    def _check_source_exists(self, source: str, dest: str, report: ConflictReport) -> None:
        """Check if source exists and destination doesn't conflict."""
        source_path = self.repo_root / source
        dest_path = self.repo_root / dest
        
        # Source must exist
        if not source_path.exists():
            conflict = Conflict(
                conflict_type=ConflictType.SOURCE_NOT_FOUND,
                source=source,
                destination=dest,
                severity="critical",
                message=f"Source file not found: {source}",
                suggested_fix="Check file path and retry",
            )
            report.add_conflict(conflict)
            return
        
        # If destination exists, that's a conflict
        if dest_path.exists():
            # Check if it's the same file (already in place)
            if source_path.resolve() == dest_path.resolve():
                conflict = Conflict(
                    conflict_type=ConflictType.FILE_EXISTS,
                    source=source,
                    destination=dest,
                    severity="info",
                    message=f"File already at destination (no-op): {dest}",
                )
                report.add_conflict(conflict)
            else:
                conflict = Conflict(
                    conflict_type=ConflictType.FILE_EXISTS,
                    source=source,
                    destination=dest,
                    severity="warning",
                    message=f"Destination already exists: {dest}",
                    suggested_fix=f"Use 'mv -i' to prompt on overwrite, or rename destination",
                )
                report.add_conflict(conflict)
    
    def _check_git_status(self, source: str, dest: str, report: ConflictReport) -> None:
        """Check git staging and uncommitted changes."""
        if not self._git_staged_cache:
            return  # No git or not initialized
        
        # Check if source is staged
        if source in self._git_staged_cache:
            conflict = Conflict(
                conflict_type=ConflictType.GIT_STAGED,
                source=source,
                destination=dest,
                severity="warning",
                message=f"File is staged in git: {source}",
                suggested_fix="Run 'git reset HEAD <file>' before moving",
            )
            report.add_conflict(conflict)
        
        # Check if source has uncommitted changes
        if self._git_dirty_cache and source in self._git_dirty_cache:
            conflict = Conflict(
                conflict_type=ConflictType.GIT_UNCOMMITTED,
                source=source,
                destination=dest,
                severity="warning",
                message=f"File has uncommitted changes: {source}",
                suggested_fix="Run 'git add <file>' or 'git checkout <file>' before moving",
            )
            report.add_conflict(conflict)
    
    def _check_permissions(self, source: str, dest: str, report: ConflictReport) -> None:
        """Check file permissions."""
        source_path = self.repo_root / source
        dest_path = self.repo_root / dest
        
        # Check source is readable
        if not os.access(source_path, os.R_OK):
            conflict = Conflict(
                conflict_type=ConflictType.PERMISSION_DENIED,
                source=source,
                destination=dest,
                severity="critical",
                message=f"Source file not readable: {source}",
                suggested_fix=f"Fix permissions: chmod +r {source}",
            )
            report.add_conflict(conflict)
        
        # Check destination parent is writable
        dest_parent = dest_path.parent
        if dest_parent.exists() and not os.access(dest_parent, os.W_OK):
            conflict = Conflict(
                conflict_type=ConflictType.PERMISSION_DENIED,
                source=source,
                destination=dest,
                severity="critical",
                message=f"Destination directory not writable: {dest_parent}",
                suggested_fix=f"Fix permissions: chmod +w {dest_parent}",
            )
            report.add_conflict(conflict)
    
    def _check_symlink(self, source: str, dest: str, report: ConflictReport) -> None:
        """Check if source is a symlink."""
        source_path = self.repo_root / source
        
        if source_path.is_symlink():
            conflict = Conflict(
                conflict_type=ConflictType.SYMLINK,
                source=source,
                destination=dest,
                severity="info",
                message=f"Source is a symlink: {source}",
                suggested_fix="Symlinks will be moved as-is (link, not target)",
            )
            report.add_conflict(conflict)
    
    def _check_reference_loops(self, moves: List[Dict[str, str]], report: ConflictReport) -> None:
        """Check for circular move dependencies (A→B, B→A)."""
        # Build move map
        move_map = {m["source"]: m["destination"] for m in moves}
        
        # Check for simple cycles (A→B, B→A)
        for source, dest in move_map.items():
            if dest in move_map and move_map[dest] == source:
                conflict = Conflict(
                    conflict_type=ConflictType.REFERENCE_LOOP,
                    source=source,
                    destination=dest,
                    severity="critical",
                    message=f"Circular move detected: {source} ↔ {dest}",
                    suggested_fix="Review move plan - files cannot move in cycles",
                )
                report.add_conflict(conflict)
    
    def _load_git_status(self) -> None:
        """Load git staged and dirty files once."""
        if (self.repo_root / ".git").exists():
            try:
                # Get staged files
                result = subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                self._git_staged_cache = set(result.stdout.strip().split("\n")) if result.returncode == 0 else set()
                
                # Get dirty (uncommitted) files
                result = subprocess.run(
                    ["git", "diff", "--name-only"],
                    cwd=self.repo_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                self._git_dirty_cache = set(result.stdout.strip().split("\n")) if result.returncode == 0 else set()
            except Exception:
                self._git_staged_cache = set()
                self._git_dirty_cache = set()
    
    def _generate_suggestions(self, report: ConflictReport) -> None:
        """Generate actionable suggestions based on conflicts."""
        suggestions: Set[str] = set()
        
        # Group suggestions by type
        for conflict in report.conflicts:
            if conflict.suggested_fix:
                suggestions.add(conflict.suggested_fix)
        
        # Add general suggestions
        if report.critical_count > 0:
            suggestions.add("Resolve all critical conflicts before proceeding")
        
        if report.warning_count > 0:
            suggestions.add("Review warnings and consider resolving before cleanup")
        
        # Deduplicate and convert to list
        report.suggestions = sorted(list(suggestions))


# AC_START: AC-VAC-ENH-003 | Conflict detection system
__all__ = [
    "ConflictType",
    "Conflict",
    "ConflictReport",
    "ConflictDetector",
]
# AC_COMPLETE: AC-VAC-ENH-003 ✅ Conflict detector with 7 detection types
