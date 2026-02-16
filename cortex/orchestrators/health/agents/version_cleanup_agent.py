"""Version Cleanup Agent - Detects Version Artifacts

Identifies:
- Files with *_v* or *-v* version patterns
- Backup files (*.bak, *.backup)
- Version headers in prompts/docs
- Duplicate versioned files

Author: CORTEX Framework
Phase: PHASE-95
CORE Rules: CORE-028 (file naming), CORE-035 (no duplicates)
"""

import re
import time
from pathlib import Path
from typing import List

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


class VersionCleanupAgent(BaseHealthAgent):
    """Agent for detecting version artifacts and backup files.
    
    Detects:
    - Version patterns in filenames (_v1.0, -v2, etc.)
    - Backup files (.bak, .backup, .old)
    - Version headers in markdown
    
    Attributes:
        name: Agent name
        description: Agent description
        config: Configuration
    """
    
    def __init__(self, config: dict = None) -> None:
        """Initialize Version Cleanup Agent.
        
        Args:
            config: Optional configuration with:
                - version_patterns: Regex patterns for versions
                - backup_extensions: File extensions to flag
        """
        super().__init__(
            name="VersionCleanupAgent",
            description="Detects version artifacts and backup files",
            config=config,
        )
        
        self.version_patterns = self.config.get("version_patterns", [
            r".*[_-]v\d+(\.\d+)*",  # file_v1.0.py, file-v2.py
            r".*\.\d+\.py$",        # file.1.py
            r".*_old\.py$",         # file_old.py
            r".*_backup\.py$",      # file_backup.py
        ])
        
        self.backup_extensions = self.config.get("backup_extensions", [
            ".bak",
            ".backup",
            ".old",
            ".orig",
            ".tmp",
        ])
        
        self.exclude_patterns = self.config.get("exclude_patterns", [
            "*/_archives/*",
            "*/_workspaces/*",
            "*/.venv/*",
            "*/.git/*",
            "*/__pycache__/*",
            "*/node_modules/*",
        ])
    
    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run version cleanup check.
        
        Args:
            workspace_root: Root path of workspace to check
        
        Returns:
            HealthCheckResult with detected issues
        """
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0
        
        # Check all files
        for file_path in workspace_root.rglob("*"):
            if not file_path.is_file():
                continue
            
            if self._should_exclude(file_path, workspace_root):
                continue
            
            try:
                # Check filename patterns
                version_issues = self._check_version_patterns(file_path, workspace_root)
                issues.extend(version_issues)
                
                # Check backup extensions
                backup_issues = self._check_backup_extensions(file_path, workspace_root)
                issues.extend(backup_issues)
                
                # Check version headers in markdown
                if file_path.suffix == ".md":
                    header_issues = self._check_version_headers(file_path, workspace_root)
                    issues.extend(header_issues)
                
                files_scanned += 1
            except Exception:
                continue
        
        duration = time.time() - start_time
        
        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "patterns_checked": len(self.version_patterns),
                "extensions_checked": len(self.backup_extensions),
            },
        )
    
    def _check_version_patterns(self, file_path: Path, workspace_root: Path) -> List[HealthIssue]:
        """Check if filename matches version patterns.
        
        Args:
            file_path: File to check
            workspace_root: Workspace root
        
        Returns:
            List of issues found
        """
        issues: List[HealthIssue] = []
        filename = file_path.name
        
        for pattern in self.version_patterns:
            if re.match(pattern, filename):
                rel_path = file_path.relative_to(workspace_root)
                
                # Suggest clean name
                clean_name = re.sub(r"[_-]v\d+(\.\d+)*", "", filename)
                clean_name = re.sub(r"\.\d+\.py$", ".py", clean_name)
                clean_name = re.sub(r"_(old|backup)\.py$", ".py", clean_name)
                
                issues.append(HealthIssue(
                    category=HealthIssueCategory.VERSION,
                    severity=HealthIssueSeverity.MEDIUM,
                    file_path=rel_path,
                    description=f"Version pattern in filename: {filename}",
                    suggested_fix=f"Rename to {clean_name} or archive",
                    metadata={
                        "pattern": pattern,
                        "clean_name": clean_name,
                    },
                ))
                break  # Only report once per file
        
        return issues
    
    def _check_backup_extensions(self, file_path: Path, workspace_root: Path) -> List[HealthIssue]:
        """Check if file has backup extension.
        
        Args:
            file_path: File to check
            workspace_root: Workspace root
        
        Returns:
            List of issues found
        """
        issues: List[HealthIssue] = []
        
        for ext in self.backup_extensions:
            if file_path.suffix == ext:
                rel_path = file_path.relative_to(workspace_root)
                
                issues.append(HealthIssue(
                    category=HealthIssueCategory.VERSION,
                    severity=HealthIssueSeverity.LOW,
                    file_path=rel_path,
                    description=f"Backup file extension: {ext}",
                    suggested_fix="Archive or delete if no longer needed",
                    metadata={
                        "extension": ext,
                    },
                ))
                break
        
        return issues
    
    def _check_version_headers(self, file_path: Path, workspace_root: Path) -> List[HealthIssue]:
        """Check for version headers in markdown files.
        
        Args:
            file_path: Markdown file to check
            workspace_root: Workspace root
        
        Returns:
            List of issues found
        """
        issues: List[HealthIssue] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for version headers
            version_header_pattern = r"^\*\*Version:\*\*\s+\d+\.\d+"
            
            if re.search(version_header_pattern, content, re.MULTILINE):
                rel_path = file_path.relative_to(workspace_root)
                
                issues.append(HealthIssue(
                    category=HealthIssueCategory.VERSION,
                    severity=HealthIssueSeverity.LOW,
                    file_path=rel_path,
                    description="Version header in markdown file",
                    suggested_fix="Use git tags instead of version headers",
                    metadata={
                        "file_type": "markdown",
                    },
                ))
        except Exception:
            pass
        
        return issues
    
    def _should_exclude(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file should be excluded.
        
        Args:
            file_path: File path to check
            workspace_root: Workspace root
        
        Returns:
            True if should exclude
        """
        rel_path = str(file_path.relative_to(workspace_root))
        
        for pattern in self.exclude_patterns:
            pattern_clean = pattern.replace("*", "").replace("/", "")
            if pattern_clean in rel_path:
                return True
        
        return False


__all__ = ["VersionCleanupAgent"]
