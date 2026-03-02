"""Temporary Script Cleaner — Cleans up phase-specific and ad-hoc scripts.

Detects and removes temporary scripts from scripts/ folder that are:
1. Phase-specific (e.g., phase-81-*.py) where phase is closed
2. One-time migration scripts older than 30 days
3. Ad-hoc validation scripts no longer needed

Safety:
- Git-aware: Won't delete files with uncommitted changes
- Age-aware: Respects minimum age threshold
- Pattern-based: Only targets known temp patterns

AC-ID: AC-VAC-SCRIPTS-001
Authority: Phase 104 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set
import re
import subprocess

from .base import Analysis, CleanerInterface, Report, RollbackResult


class TempScriptCleaner(CleanerInterface):
    """Cleaner for temporary and phase-specific scripts."""
    
    # Scripts that must NEVER be deleted
    PROTECTED_SCRIPTS: Set[str] = {
        "vacuum-runner.py",
        "setup-mcp.py",
        "run-tests.sh",
        "build-docs-site.py",
        "enhanced_cleanup.py",
    }
    
    # Patterns indicating temporary/phase-specific scripts
    TEMP_PATTERNS: List[str] = [
        r"^phase[-_]?\d+[-_].*\.py$",       # phase-81-*, phase25_*
        r"^consolidate[-_].*\.py$",          # consolidate_phases.py
        r"^restore[-_].*\.py$",              # restore_cortex_master.py
        r"^migrate[-_].*\.py$",              # migration scripts
        r"^fix[-_].*\.py$",                  # fix_*.py one-time fixes
        r"^validate[-_].*\.py$",             # validate-production.py
        r"^execute[-_].*\.py$",              # execute_validation_suite.py
        r"^batch[-_].*\.py$",                # batch_generate_tests.py
        r"^cleanup[-_](?!\.py$).*\.py$",     # cleanup-*.py (not cleanup.py)
        r"^eliminate[-_].*\.py$",            # eliminate_redirect_stubs.py
        r"^sanitize[-_].*\.py$",             # sanitize-company-refs.py
        r"^enforce[-_].*\.py$",              # enforce-test-naming.py
        r"^add[-_].*\.py$",                  # add_cortex_semantic_ids.py
        r"^update[-_].*\.py$",               # update_archived_paths.py
    ]
    
    # Shell script patterns
    TEMP_SHELL_PATTERNS: List[str] = [
        r"^restore[-_].*\.sh$",
        r"^restructure[-_].*\.sh$",
        r"^update[-_].*\.sh$",
    ]
    
    # Minimum age in days before a script can be cleaned
    MIN_AGE_DAYS: int = 30
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize temp script cleaner.
        
        Args:
            config: Configuration with repo_root and optional min_age_days
        """
        super().__init__(config)
        self.repo_root = Path(config.get("repo_root", "."))
        self.scripts_dir = self.repo_root / "scripts"
        self.min_age_days = config.get("min_age_days", self.MIN_AGE_DAYS)
        self.dry_run = config.get("dry_run", False)
        
        # Compile patterns for efficiency
        self._temp_patterns = [re.compile(p, re.IGNORECASE) for p in self.TEMP_PATTERNS]
        self._shell_patterns = [re.compile(p, re.IGNORECASE) for p in self.TEMP_SHELL_PATTERNS]
    
    @property
    def name(self) -> str:
        """Get cleaner name."""
        return "TempScriptCleaner"
    
    @property
    def version(self) -> str:
        """Get cleaner version."""
        return "1.0.0"
    
    @property
    def domain(self) -> str:
        """Get cleaner domain."""
        return "temp_scripts"
    
    def _is_temp_script(self, filename: str) -> bool:
        """Check if filename matches temporary script patterns.
        
        Args:
            filename: Script filename to check
        
        Returns:
            True if matches temp pattern
        """
        # Check Python patterns
        for pattern in self._temp_patterns:
            if pattern.match(filename):
                return True
        
        # Check shell patterns
        for pattern in self._shell_patterns:
            if pattern.match(filename):
                return True
        
        return False
    
    def _is_protected(self, filename: str) -> bool:
        """Check if script is protected from deletion.
        
        Args:
            filename: Script filename to check
        
        Returns:
            True if protected
        """
        return filename in self.PROTECTED_SCRIPTS
    
    def _get_file_age_days(self, file_path: Path) -> int:
        """Get file age in days based on modification time.
        
        Args:
            file_path: Path to file
        
        Returns:
            Age in days
        """
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - mtime
            return age.days
        except OSError:
            return 0
    
    def _has_uncommitted_changes(self, file_path: Path) -> bool:
        """Check if file has uncommitted git changes.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if has uncommitted changes
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", str(file_path)],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            # If output is non-empty, file has uncommitted changes
            return bool(result.stdout.strip())
        except (subprocess.SubprocessError, FileNotFoundError):
            # If git check fails, assume file has changes (safe default)
            return True
    
    def _is_tracked_by_git(self, file_path: Path) -> bool:
        """Check if file is tracked by git.
        
        Args:
            file_path: Path to file
        
        Returns:
            True if tracked by git
        """
        try:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(file_path)],
                cwd=self.repo_root,
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def analyze(self) -> Analysis:
        """Analyze scripts folder for temporary scripts.
        
        Returns:
            Analysis with detected temporary scripts
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        issues: List[Dict[str, Any]] = []
        files_scanned = 0
        
        if not self.scripts_dir.exists():
            logs.append(f"Scripts directory not found: {self.scripts_dir}")
            return Analysis(
                cleaner_id=self.name,
                timestamp=timestamp,
                files_scanned=0,
                issues_found=0,
                plan={"issues": []},
                logs=logs,
            )
        
        logs.append(f"Scanning scripts directory: {self.scripts_dir}")
        
        # Scan for temporary scripts
        for script_file in self.scripts_dir.iterdir():
            if not script_file.is_file():
                continue
            
            files_scanned += 1
            filename = script_file.name
            
            # Skip protected scripts
            if self._is_protected(filename):
                logs.append(f"Protected: {filename}")
                continue
            
            # Check if matches temp pattern
            if not self._is_temp_script(filename):
                continue
            
            # Check age
            age_days = self._get_file_age_days(script_file)
            if age_days < self.min_age_days:
                logs.append(f"Too young ({age_days}d < {self.min_age_days}d): {filename}")
                continue
            
            # Check git status
            if self._has_uncommitted_changes(script_file):
                logs.append(f"Has uncommitted changes: {filename}")
                continue
            
            # Add as cleanup candidate
            issues.append({
                "type": "temp_script",
                "path": str(script_file),
                "filename": filename,
                "age_days": age_days,
                "size_bytes": script_file.stat().st_size,
                "action": "delete",
                "reason": f"Temporary script, {age_days} days old",
            })
            logs.append(f"Candidate: {filename} ({age_days} days old)")
        
        return Analysis(
            cleaner_id=self.name,
            timestamp=timestamp,
            files_scanned=files_scanned,
            issues_found=len(issues),
            plan={"issues": issues},
            logs=logs,
        )
    
    def execute(self, plan: Any) -> Report:
        """Execute cleanup of temporary scripts.
        
        Args:
            plan: Execution plan (either Analysis object or dict with issues)
        
        Returns:
            Report with cleanup results
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        actions_taken: List[Dict[str, Any]] = []
        errors: List[str] = []
        
        # Handle both Analysis object and dict
        if hasattr(plan, 'plan'):
            # It's an Analysis object
            issues = plan.plan.get("issues", [])
        elif isinstance(plan, dict):
            # It's the plan dict directly
            issues = plan.get("issues", [])
        else:
            issues = []
        
        for issue in issues:
            file_path = Path(issue["path"])
            
            try:
                if self.dry_run:
                    logs.append(f"[DRY RUN] Would delete: {file_path.name}")
                    actions_taken.append({
                        "action": "delete",
                        "path": str(file_path),
                        "dry_run": True,
                    })
                else:
                    # Actually delete the file
                    file_path.unlink()
                    logs.append(f"Deleted: {file_path.name}")
                    actions_taken.append({
                        "action": "delete",
                        "path": str(file_path),
                        "dry_run": False,
                    })
            except Exception as e:
                error_msg = f"Failed to delete {file_path.name}: {e}"
                errors.append(error_msg)
                logs.append(f"ERROR: {error_msg}")
        
        deleted_count = len([a for a in actions_taken if not a.get("dry_run")])
        status = "SUCCESS" if len(errors) == 0 else ("PARTIAL" if deleted_count > 0 else "FAILED")
        
        return Report(
            cleaner_id=self.name,
            timestamp=timestamp,
            status=status,
            actions_taken=len(actions_taken),
            changes={"deleted": deleted_count},
            errors=errors,
            logs=logs,
        )
    
    def rollback(self, report: Report) -> RollbackResult:
        """Rollback is not supported for deletions.
        
        Args:
            report: Report from execute phase
        
        Returns:
            RollbackResult indicating not supported
        """
        return RollbackResult(
            cleaner_id=self.name,
            timestamp=datetime.now().isoformat(),
            status="FAILED",
            files_restored=0,
            errors=["Rollback not supported for file deletions. Use git to restore."],
        )
