"""Root Artifacts Cleaner

Detects and moves log/report files from repository root to proper locations.

AC-VACUUM-002: Root cleanup
Author: CORTEX Framework
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set
import shutil

# Import from base module using relative import
from .base import Analysis, CleanerInterface, Report, RollbackResult


class RootArtifactsCleaner(CleanerInterface):
    """Cleaner for organizing root artifacts into proper locations."""
    
    # Essential files that must remain in root
    ESSENTIAL_FILES = {
        "README.md",
        "Makefile",
        "requirements.txt",
        "pytest.ini",
        "conftest.py",
        ".gitignore",
        ".pre-commit-config.yaml",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "package.json",  # Node.js config
        "tsconfig.json",  # TypeScript config
        "jsconfig.json",  # JavaScript config
    }
    
    # Artifact patterns and their target directories
    ARTIFACT_PATTERNS = {
        "*.log": "reports/logs/",
        "*-report.json": "reports/",
        "*-summary.json": "reports/",
        "*-metrics.json": "reports/",
        "*-report.yaml": "reports/",
        "production-*.json": "reports/",
    }
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize root artifacts cleaner.
        
        Args:
            config: Configuration with repo_root
        """
        super().__init__(config)
        self.repo_root = Path(config.get("repo_root", "."))
        self.essential_files = self.ESSENTIAL_FILES.copy()
        
        # Allow custom essential files
        custom_essential = config.get("essential_root_files", [])
        if custom_essential:
            self.essential_files.update(custom_essential)
    
    @property
    def name(self) -> str:
        """Get cleaner name."""
        return "RootArtifactsCleaner"
    
    @property
    def version(self) -> str:
        """Get cleaner version."""
        return "1.0.0"
    
    @property
    def domain(self) -> str:
        """Get cleaner domain."""
        return "root_artifacts"
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches glob pattern.
        
        Args:
            filename: Filename to check
            pattern: Glob pattern
        
        Returns:
            True if matches
        """
        from fnmatch import fnmatch
        return fnmatch(filename, pattern)
    
    def analyze(self) -> Analysis:
        """Analyze repository root for artifacts.
        
        Returns:
            Analysis with detected artifacts
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        issues: List[Dict[str, Any]] = []
        files_scanned = 0
        
        # Scan root directory only (not subdirectories)
        for item in self.repo_root.iterdir():
            if not item.is_file():
                continue
            
            if item.name.startswith("."):
                continue
            
            files_scanned += 1
            
            # Skip essential files
            if item.name in self.essential_files:
                continue
            
            # Check against artifact patterns
            for pattern, target_dir in self.ARTIFACT_PATTERNS.items():
                if self._matches_pattern(item.name, pattern):
                    target_path = self.repo_root / target_dir / item.name
                    
                    issues.append({
                        "file": str(item),
                        "target": str(target_path),
                        "size_kb": item.stat().st_size / 1024,
                        "pattern": pattern,
                    })
                    
                    logs.append(f"Found {item.name} → {target_dir}")
                    break
        
        plan = {
            "actions": [
                {
                    "action": "move",
                    "source": issue["file"],
                    "target": issue["target"],
                }
                for issue in issues
            ]
        }
        
        return Analysis(
            cleaner_id=self.domain,
            timestamp=timestamp,
            files_scanned=files_scanned,
            issues_found=len(issues),
            plan=plan,
            logs=logs,
        )
    
    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute artifact migration plan.
        
        Args:
            plan: Migration plan from analyze()
        
        Returns:
            Execution report
        """
        timestamp = datetime.now().isoformat()
        logs: List[str] = []
        errors: List[str] = []
        actions_taken = 0
        changes: Dict[str, Any] = {"moved_files": []}
        
        for action in plan.get("actions", []):
            if action["action"] == "move":
                source = Path(action["source"])
                target = Path(action["target"])
                
                try:
                    if self.dry_run:
                        logs.append(f"[DRY RUN] Would move {source} → {target}")
                        actions_taken += 1
                    else:
                        # Create target directory
                        target.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Move file
                        shutil.move(str(source), str(target))
                        
                        changes["moved_files"].append({
                            "from": str(source),
                            "to": str(target),
                        })
                        
                        logs.append(f"Moved {source.name} → {target.parent}")
                        actions_taken += 1
                        
                except Exception as e:
                    errors.append(f"Failed to move {source}: {e}")
        
        status = "SUCCESS" if not errors else "PARTIAL"
        
        return Report(
            cleaner_id=self.domain,
            timestamp=timestamp,
            status=status,
            actions_taken=actions_taken,
            changes=changes,
            errors=errors,
            logs=logs,
        )
    
    def rollback(self) -> RollbackResult:
        """Rollback artifact migrations (not implemented).
        
        Returns:
            Rollback result
        """
        return RollbackResult(
            cleaner_id=self.domain,
            timestamp=datetime.now().isoformat(),
            status="NOT_IMPLEMENTED",
            files_restored=0,
            errors=["Artifact rollback requires manual intervention"],
        )


__all__ = ["RootArtifactsCleaner"]
