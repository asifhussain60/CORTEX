"""
Vacuum Automation - Automated Cleanup Operations

Consolidates cleanup logic from multiple vacuum scripts.

**Source Scripts:**
- .cortex/run_vacuum.py
- scripts/vacuum-runner.py

**Authority:** Phase 90 S-90-05
**Author:** Asif Hussain
**Created:** 2026-02-16
"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    
    strategy: str
    files_removed: int
    directories_removed: int
    bytes_freed: int
    errors: List[str]


class VacuumAutomation:
    """
    Automated cleanup and vacuum operations.
    
    Consolidates cleanup strategies for markdown sprawl, debug markers,
    pycache, session data, and other temporary files.
    """
    
    def __init__(self, workspace_root: Optional[Path] = None, dry_run: bool = False):
        """
        Initialize vacuum automation.
        
        Args:
            workspace_root: Root directory of CORTEX workspace.
                           Defaults to current working directory.
            dry_run: If True, only report what would be cleaned without
                    actually removing files.
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.dry_run = dry_run
        self.results: Dict[str, CleanupResult] = {}
    
    def cleanup_all(self) -> Dict[str, CleanupResult]:
        """
        Run all cleanup strategies.
        
        Returns:
            Dictionary of cleanup results by strategy name.
        """
        self.results = {}
        
        self.cleanup_markdown_sprawl()
        self.cleanup_debug_markers()
        self.cleanup_pycache()
        self.cleanup_session_data()
        self.cleanup_build_artifacts()
        
        return self.results
    
    def cleanup_markdown_sprawl(self) -> CleanupResult:
        """
        Clean up markdown sprawl (CORE-002 enforcement).
        
        Removes unauthorized markdown files outside allowed directories.
        
        Allowed:
        - .github/prompts/*.md
        - .github/agents/*.md
        - README.md (root only)
        - docs/**/*.md (documentation)
        
        Returns:
            Cleanup result with files removed count.
        """
        allowed_patterns = [
            ".github/prompts/",
            ".github/agents/",
            "README.md",
            "docs/",
            "cortex-docs/",
            ".cortex/",  # Archive area
            "_archives/",  # Archive area
        ]
        
        files_removed = 0
        bytes_freed = 0
        errors = []
        
        # Scan for .md files
        for md_file in self.workspace_root.rglob("*.md"):
            # Skip if in allowed directory
            rel_path = md_file.relative_to(self.workspace_root)
            
            is_allowed = any(
                str(rel_path).startswith(pattern) or str(rel_path) == pattern
                for pattern in allowed_patterns
            )
            
            if not is_allowed:
                try:
                    file_size = md_file.stat().st_size
                    
                    if not self.dry_run:
                        md_file.unlink()
                    
                    files_removed += 1
                    bytes_freed += file_size
                    
                except Exception as e:
                    errors.append(f"Failed to remove {md_file}: {e}")
        
        result = CleanupResult(
            strategy="markdown_sprawl",
            files_removed=files_removed,
            directories_removed=0,
            bytes_freed=bytes_freed,
            errors=errors,
        )
        
        self.results["markdown_sprawl"] = result
        return result
    
    def cleanup_debug_markers(self) -> CleanupResult:
        """
        Remove CORTEX_DEBUG markers from source code.
        
        Returns:
            Cleanup result with files cleaned count.
        """
        files_cleaned = 0
        errors = []
        
        # Scan Python files for debug markers
        for py_file in self.workspace_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                
                if "CORTEX_DEBUG" in content:
                    if not self.dry_run:
                        # Remove lines containing CORTEX_DEBUG
                        lines = content.split("\n")
                        cleaned_lines = [
                            line for line in lines
                            if "CORTEX_DEBUG" not in line
                        ]
                        py_file.write_text("\n".join(cleaned_lines))
                    
                    files_cleaned += 1
                    
            except Exception as e:
                errors.append(f"Failed to clean {py_file}: {e}")
        
        result = CleanupResult(
            strategy="debug_markers",
            files_removed=files_cleaned,
            directories_removed=0,
            bytes_freed=0,  # Hard to estimate without actually cleaning
            errors=errors,
        )
        
        self.results["debug_markers"] = result
        return result
    
    def cleanup_pycache(self) -> CleanupResult:
        """
        Remove __pycache__ directories and .pyc files.
        
        Returns:
            Cleanup result with directories removed count.
        """
        dirs_removed = 0
        files_removed = 0
        bytes_freed = 0
        errors = []
        
        # Remove __pycache__ directories
        for pycache_dir in self.workspace_root.rglob("__pycache__"):
            if pycache_dir.is_dir():
                try:
                    dir_size = sum(f.stat().st_size for f in pycache_dir.rglob("*") if f.is_file())
                    
                    if not self.dry_run:
                        shutil.rmtree(pycache_dir)
                    
                    dirs_removed += 1
                    bytes_freed += dir_size
                    
                except Exception as e:
                    errors.append(f"Failed to remove {pycache_dir}: {e}")
        
        # Remove standalone .pyc files
        for pyc_file in self.workspace_root.rglob("*.pyc"):
            try:
                file_size = pyc_file.stat().st_size
                
                if not self.dry_run:
                    pyc_file.unlink()
                
                files_removed += 1
                bytes_freed += file_size
                
            except Exception as e:
                errors.append(f"Failed to remove {pyc_file}: {e}")
        
        result = CleanupResult(
            strategy="pycache",
            files_removed=files_removed,
            directories_removed=dirs_removed,
            bytes_freed=bytes_freed,
            errors=errors,
        )
        
        self.results["pycache"] = result
        return result
    
    def cleanup_session_data(self) -> CleanupResult:
        """
        Remove temporary session data.
        
        Returns:
            Cleanup result with files removed count.
        """
        session_patterns = [
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            "*.log",
        ]
        
        files_removed = 0
        dirs_removed = 0
        bytes_freed = 0
        errors = []
        
        for pattern in session_patterns:
            if pattern.endswith("/"):
                # Directory pattern
                dir_name = pattern.rstrip("/")
                for session_dir in self.workspace_root.rglob(dir_name):
                    if session_dir.is_dir():
                        try:
                            dir_size = sum(f.stat().st_size for f in session_dir.rglob("*") if f.is_file())
                            
                            if not self.dry_run:
                                shutil.rmtree(session_dir)
                            
                            dirs_removed += 1
                            bytes_freed += dir_size
                            
                        except Exception as e:
                            errors.append(f"Failed to remove {session_dir}: {e}")
            else:
                # File pattern
                for session_file in self.workspace_root.rglob(pattern):
                    if session_file.is_file():
                        try:
                            file_size = session_file.stat().st_size
                            
                            if not self.dry_run:
                                session_file.unlink()
                            
                            files_removed += 1
                            bytes_freed += file_size
                            
                        except Exception as e:
                            errors.append(f"Failed to remove {session_file}: {e}")
        
        result = CleanupResult(
            strategy="session_data",
            files_removed=files_removed,
            directories_removed=dirs_removed,
            bytes_freed=bytes_freed,
            errors=errors,
        )
        
        self.results["session_data"] = result
        return result
    
    def cleanup_build_artifacts(self) -> CleanupResult:
        """
        Remove build artifacts (.egg-info, dist/, build/).
        
        Returns:
            Cleanup result with directories removed count.
        """
        build_patterns = [
            "*.egg-info/",
            "dist/",
            "build/",
        ]
        
        dirs_removed = 0
        bytes_freed = 0
        errors = []
        
        for pattern in build_patterns:
            dir_name = pattern.rstrip("/")
            for build_dir in self.workspace_root.rglob(dir_name):
                if build_dir.is_dir():
                    try:
                        dir_size = sum(f.stat().st_size for f in build_dir.rglob("*") if f.is_file())
                        
                        if not self.dry_run:
                            shutil.rmtree(build_dir)
                        
                        dirs_removed += 1
                        bytes_freed += dir_size
                        
                    except Exception as e:
                        errors.append(f"Failed to remove {build_dir}: {e}")
        
        result = CleanupResult(
            strategy="build_artifacts",
            files_removed=0,
            directories_removed=dirs_removed,
            bytes_freed=bytes_freed,
            errors=errors,
        )
        
        self.results["build_artifacts"] = result
        return result
    
    def generate_report(self) -> str:
        """
        Generate formatted cleanup report.
        
        Returns:
            Formatted text report of cleanup operations.
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CORTEX VACUUM AUTOMATION REPORT")
        lines.append("=" * 80)
        lines.append("")
        
        if self.dry_run:
            lines.append("⚠️  DRY RUN MODE (no files actually removed)")
            lines.append("")
        
        total_files = sum(r.files_removed for r in self.results.values())
        total_dirs = sum(r.directories_removed for r in self.results.values())
        total_bytes = sum(r.bytes_freed for r in self.results.values())
        total_errors = sum(len(r.errors) for r in self.results.values())
        
        lines.append(f"Total Files Removed: {total_files}")
        lines.append(f"Total Directories Removed: {total_dirs}")
        lines.append(f"Total Space Freed: {total_bytes / 1024:.2f} KB")
        lines.append(f"Errors: {total_errors}")
        lines.append("")
        
        for strategy, result in self.results.items():
            lines.append(f"Strategy: {strategy}")
            lines.append(f"  Files: {result.files_removed}")
            lines.append(f"  Directories: {result.directories_removed}")
            lines.append(f"  Bytes Freed: {result.bytes_freed}")
            
            if result.errors:
                lines.append(f"  Errors: {len(result.errors)}")
                for error in result.errors[:5]:  # Show first 5 errors
                    lines.append(f"    - {error}")
                if len(result.errors) > 5:
                    lines.append(f"    ... and {len(result.errors) - 5} more")
            
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
