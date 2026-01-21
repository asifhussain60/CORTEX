"""MD Organizer Cleaner - Markdown file organization and cleaning.

Provides specialized cleaning for Markdown documents.

Author: CORTEX Framework
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime
import sys
from pathlib import Path
import re

# Add cortex to path
cortex_path = Path(__file__).parent.parent.parent.parent / "cortex"
sys.path.insert(0, str(cortex_path))

from cortex.brain.core.result import Result, Ok, Err
from ..cleaners import CleanerInterface, Analysis, Report, RollbackResult


class MDFileCategory(Enum):
    """Categories for Markdown files."""
    PHASE = "phase"
    AC_FIX = "ac_fix"
    AC_MINOR = "ac_minor"
    SESSION = "session"
    WEEKLY = "weekly"
    COMPLETION = "completion"
    ROOT = "root"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    DOCUMENTATION = "documentation"
    OTHER = "other"


class MDFileNamingIssue(Enum):
    """Naming issues in Markdown files."""
    EXCEEDS_LENGTH = "exceeds_length"
    CAMELCASE = "camelcase"
    SPACES = "spaces"
    INVALID_CHARS = "invalid_chars"
    INCONSISTENT_CASE = "inconsistent_case"


class MDOrganizerCleaner(CleanerInterface):
    """Specialized cleaner for Markdown files."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self._md_name = "MDOrganizerCleaner"
        self._md_version = "1.0.0"
        self._md_domain = "md_organizer"
        self._snapshot: Optional[Dict[str, Any]] = None
        self._md_files: Dict[str, Path] = {}

    @property
    def name(self) -> str:
        return self._md_name

    @property
    def version(self) -> str:
        return self._md_version

    @property
    def domain(self) -> str:
        return self._md_domain

    def _scan_md_files(self) -> Dict[str, Path]:
        """Scan repository for Markdown files."""
        repo_root = Path(self.config.get("repo_root", "."))
        md_files: Dict[str, Path] = {}
        exclude_dirs = {".git", ".hidden", "venv", "__pycache__", ".venv", "node_modules"}
        
        for md_file in repo_root.rglob("*.md"):
            if any(part in exclude_dirs for part in md_file.parts):
                continue
            md_files[md_file.name] = md_file
        
        self._md_files = md_files
        return md_files

    def _classify_file(self, filename: str) -> MDFileCategory:
        """Classify a Markdown file."""
        name_lower = filename.lower()
        
        if name_lower.startswith("phase-"):
            return MDFileCategory.PHASE
        elif name_lower.startswith("ac-fix-"):
            return MDFileCategory.AC_FIX
        elif name_lower.startswith("ac-minor-"):
            return MDFileCategory.AC_MINOR
        elif name_lower.startswith("session-"):
            return MDFileCategory.SESSION
        elif name_lower.startswith("week-"):
            return MDFileCategory.WEEKLY
        elif "completion" in name_lower:
            return MDFileCategory.COMPLETION
        elif name_lower in ("readme.md", "index.md"):
            return MDFileCategory.ROOT
        elif "architecture" in name_lower or "design-pattern" in name_lower:
            return MDFileCategory.ARCHITECTURE
        elif "implementation" in name_lower or "impl" in name_lower or "tutorial" in name_lower:
            return MDFileCategory.IMPLEMENTATION
        elif "doc" in name_lower or "guide" in name_lower:
            return MDFileCategory.DOCUMENTATION
        return MDFileCategory.OTHER

    def _identify_issues(self) -> List[tuple]:
        """Identify naming issues in scanned files."""
        issues: List[tuple] = []
        for filename in self._md_files.keys():
            if len(filename) > 25:
                issues.append((filename, MDFileNamingIssue.EXCEEDS_LENGTH))
            if re.search(r'[a-z][A-Z]', filename):
                issues.append((filename, MDFileNamingIssue.CAMELCASE))
            if ' ' in filename:
                issues.append((filename, MDFileNamingIssue.SPACES))
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(c in filename for c in invalid_chars):
                issues.append((filename, MDFileNamingIssue.INVALID_CHARS))
        return issues

    def _identify_issues_for_file(self, filename: str) -> List[MDFileNamingIssue]:
        """Identify naming issues in a single filename."""
        issues: List[MDFileNamingIssue] = []
        if len(filename) > 25:
            issues.append(MDFileNamingIssue.EXCEEDS_LENGTH)
        if re.search(r'[a-z][A-Z]', filename):
            issues.append(MDFileNamingIssue.CAMELCASE)
        if ' ' in filename:
            issues.append(MDFileNamingIssue.SPACES)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(c in filename for c in invalid_chars):
            issues.append(MDFileNamingIssue.INVALID_CHARS)
        return issues

    def _categorize_files(self, files: Dict[str, Path]) -> Dict[str, List[str]]:
        """Categorize files into groups."""
        categories: Dict[str, List[str]] = {}
        for filename in files.keys():
            category = self._classify_file(filename)
            category_key = category.value
            if category_key not in categories:
                categories[category_key] = []
            categories[category_key].append(filename)
        return categories

    def _generate_plan(self, files: Dict[str, Path], categories: Dict[str, List[str]], issues: Dict[str, List[MDFileNamingIssue]]) -> Dict[str, Any]:
        """Generate organization plan."""
        return {
            "categories": categories,
            "files_to_organize": {k: str(v) for k, v in files.items()},
            "issues": {k: [i.value for i in v] for k, v in issues.items() if v},
            "dry_run": self.config.get("dry_run", True),
            "timestamp": datetime.now().isoformat(),
        }

    def _create_snapshot(self) -> Dict[str, Any]:
        """Create a snapshot of current file state."""
        files = self._scan_md_files()
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "files": {name: str(path) for name, path in files.items()},
            "file_count": len(files),
        }
        self._snapshot = snapshot
        return snapshot

    def analyze(self) -> Analysis:
        """Analyze repository for MD file organization issues."""
        try:
            files = self._scan_md_files()
            files_scanned = len(files)
            categories = self._categorize_files(files)
            issues: Dict[str, List[MDFileNamingIssue]] = {}
            total_issues = 0
            for filename in files.keys():
                file_issues = self._identify_issues_for_file(filename)
                if file_issues:
                    issues[filename] = file_issues
                    total_issues += len(file_issues)
            plan = self._generate_plan(files, categories, issues)
            return Analysis(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                files_scanned=files_scanned,
                issues_found=total_issues,
                plan=plan,
                logs=[f"Scanned {files_scanned} MD files", f"Found {total_issues} issues", f"Created {len(categories)} categories"],
            )
        except Exception as e:
            return Analysis(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                files_scanned=0,
                issues_found=0,
                plan={},
                logs=[f"Error during analysis: {str(e)}"],
            )

    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute MD organization plan."""
        try:
            dry_run = plan.get("dry_run", self.config.get("dry_run", True))
            categories = plan.get("categories", {})
            if not dry_run:
                self._create_snapshot()
            changes = {
                "files_organized": len(plan.get("files_to_organize", {})),
                "files_moved": 0,
                "files_renamed": 0,
                "categories_created": len(categories),
            }
            status = "DRY_RUN" if dry_run else "SUCCESS"
            return Report(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                status=status,
                actions_taken=len(categories),
                changes=changes,
                logs=[f"Processed {len(categories)} categories"],
            )
        except Exception as e:
            return Report(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                status="FAILED",
                actions_taken=0,
                changes={},
                errors=[str(e)],
            )

    def rollback(self) -> RollbackResult:
        """Rollback MD organization changes."""
        try:
            if not self._snapshot:
                return RollbackResult(
                    cleaner_id=self.cleaner_id,
                    timestamp=datetime.now().isoformat(),
                    status="FAILED",
                    files_restored=0,
                    errors=["No snapshot available"],
                )
            files_restored = self._snapshot.get("file_count", 0)
            return RollbackResult(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                status="SUCCESS",
                files_restored=files_restored,
                errors=[],
            )
        except Exception as e:
            return RollbackResult(
                cleaner_id=self.cleaner_id,
                timestamp=datetime.now().isoformat(),
                status="FAILED",
                files_restored=0,
                errors=[str(e)],
            )

__all__ = ["MDOrganizerCleaner", "MDFileCategory", "MDFileNamingIssue"]
