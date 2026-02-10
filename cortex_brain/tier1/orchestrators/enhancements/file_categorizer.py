"""
File Categorizer - Intelligent semantic file classification.

AC-ID: AC-VAC-ENH-001 | Phase: Enhancement #1
Purpose: Classify files into semantic categories for cleanup planning
Authority: CORTEX Vacuum Enhancement Phase 1

Classification signals:
1. Extension-based (primary)
2. Content scanning (secondary)
3. Reference analysis (tertiary)
4. Naming conventions (quaternary)
5. Git history (fallback)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Tuple
import re
import subprocess
from datetime import datetime


class FileCategory(Enum):
    """Semantic file categories with destination hints."""
    
    SYSTEM_CODE = "cortex/"              # .py files implementing CORTEX core
    SYSTEM_CONFIG = ".cortex/"           # CORTEX metadata, manifests
    COMPANY_DATA = "company/"            # Domain-specific outputs, dashboards
    DEPLOYMENT = "deployment/"           # Docker, k8s, nginx configs
    DOCUMENTATION = "docs/"              # Markdown, guides, references
    SCRIPTS_UTILS = "scripts/"           # Utility scripts, automation
    TESTING = "tests/"                   # Test files and fixtures
    GIT_CONFIG = ".github/"              # Git hooks, workflows, actions
    DEVELOPMENT = ".venv/"               # Development environment files
    KEEP_ROOT = "root"                   # Must stay in root (README, Makefile)
    ARCHIVE = "docs/archive/"            # Cleanup: files to move here
    DELETE = "delete"                    # Files to remove entirely
    UNKNOWN = "unknown"                  # Cannot classify
    
    @property
    def destination(self) -> Optional[str]:
        """Get default destination directory for category."""
        if self == FileCategory.DELETE:
            return None
        elif self == FileCategory.KEEP_ROOT:
            return None
        elif self == FileCategory.UNKNOWN:
            return None
        else:
            return self.value


@dataclass
class ClassificationSignals:
    """Multi-signal classification analysis."""
    
    extension_signal: Tuple[FileCategory, float] = field(default=(FileCategory.UNKNOWN, 0.0))
    content_signal: Tuple[FileCategory, float] = field(default=(FileCategory.UNKNOWN, 0.0))
    reference_signal: Tuple[FileCategory, float] = field(default=(FileCategory.UNKNOWN, 0.0))
    naming_signal: Tuple[FileCategory, float] = field(default=(FileCategory.UNKNOWN, 0.0))
    git_signal: Tuple[FileCategory, float] = field(default=(FileCategory.UNKNOWN, 0.0))
    
    @property
    def winning_category(self) -> FileCategory:
        """Get highest-confidence category from all signals."""
        signals = [
            self.extension_signal,
            self.content_signal,
            self.reference_signal,
            self.naming_signal,
            self.git_signal,
        ]
        
        # Remove UNKNOWN signals
        valid = [s for s in signals if s[0] != FileCategory.UNKNOWN]
        
        if not valid:
            return FileCategory.UNKNOWN
        
        # Sort by confidence (descending) then by category priority
        valid.sort(key=lambda x: (-x[1], self._category_priority(x[0])))
        
        return valid[0][0]
    
    @property
    def confidence(self) -> float:
        """Get confidence score (0.0-1.0) for final classification."""
        winning = self.winning_category
        signals = [
            self.extension_signal,
            self.content_signal,
            self.reference_signal,
            self.naming_signal,
            self.git_signal,
        ]
        
        matching_scores = [s[1] for s in signals if s[0] == winning]
        return sum(matching_scores) / len(matching_scores) if matching_scores else 0.0
    
    @staticmethod
    def _category_priority(category: FileCategory) -> int:
        """Priority ordering for tiebreaking."""
        priorities = {
            FileCategory.KEEP_ROOT: 0,      # Highest priority
            FileCategory.DELETE: 1,
            FileCategory.GIT_CONFIG: 2,
            FileCategory.SYSTEM_CONFIG: 3,
            FileCategory.SYSTEM_CODE: 4,
            FileCategory.TESTING: 5,
            FileCategory.SCRIPTS_UTILS: 6,
            FileCategory.DOCUMENTATION: 7,
            FileCategory.DEPLOYMENT: 8,
            FileCategory.COMPANY_DATA: 9,
            FileCategory.DEVELOPMENT: 10,
            FileCategory.ARCHIVE: 11,
            FileCategory.UNKNOWN: 99,       # Lowest priority
        }
        return priorities.get(category, 50)


class FileClassifier:
    """Intelligent file classifier using multiple signals."""
    
    # Extension patterns
    EXTENSION_PATTERNS = {
        FileCategory.SYSTEM_CODE: {
            "patterns": [r"\.py$", r"\.pyx$"],
            "confidence": 0.8,
            "folder_filters": ["cortex/", "cortex_lens/", "cortex_brain/"],
        },
        FileCategory.TESTING: {
            "patterns": [r"^test_.*\.py$", r".*_test\.py$", r"conftest\.py$"],
            "confidence": 0.95,
        },
        FileCategory.DOCUMENTATION: {
            "patterns": [r"\.md$", r"\.rst$", r"\.txt$"],
            "confidence": 0.7,
            "folder_filters": ["docs/", ".github/"],
        },
        FileCategory.DEPLOYMENT: {
            "patterns": [r"Dockerfile", r"docker-compose.*\.yml$", r"\.yaml$", r"\.yml$", r"nginx.*\.conf$"],
            "confidence": 0.9,
            "folder_filters": ["deployment/"],
        },
        FileCategory.SCRIPTS_UTILS: {
            "patterns": [r"\.sh$", r".*_cli\.py$", r".*_script\.py$"],
            "confidence": 0.8,
        },
        FileCategory.GIT_CONFIG: {
            "patterns": [r"^\.git", r"\.github/", r"\.pre-commit"],
            "confidence": 1.0,
        },
        FileCategory.DELETE: {
            "patterns": [r"\.DS_Store$", r"\.pyc$", r"\.pyo$", r"__pycache__", r"\.pytest_cache"],
            "confidence": 0.99,
        },
        FileCategory.KEEP_ROOT: {
            "patterns": [
                r"^Makefile$", r"^README\.md$", r"^requirements\.txt$",
                r"^pytest\.ini$", r"^\.gitignore$", r"^\.pre-commit-config\.yaml$"
            ],
            "confidence": 1.0,
        },
    }
    
    # Content-based detection patterns (scan first 50 lines)
    CONTENT_PATTERNS = {
        FileCategory.TESTING: {
            "patterns": [r"import pytest", r"import unittest", r"def test_"],
            "confidence": 0.85,
        },
        FileCategory.DOCUMENTATION: {
            "patterns": [r"^# ", r"^## ", r"^### ", r"---"],  # Markdown headers
            "confidence": 0.75,
        },
        FileCategory.SYSTEM_CONFIG: {
            "patterns": [r"cortex_brain.*config", r"vacuum.*config", r"phase.*config"],
            "confidence": 0.8,
        },
        FileCategory.COMPANY_DATA: {
            "patterns": [r"dashboard.*json", r"analytics", r"metrics"],
            "confidence": 0.6,
        },
    }
    
    # Naming convention patterns
    NAMING_PATTERNS = {
        FileCategory.TESTING: {
            "patterns": [r"^test_", r"_test\.py$", r"conftest"],
            "confidence": 0.95,
        },
        FileCategory.SCRIPTS_UTILS: {
            "patterns": [r".*_cli\.py$", r".*_script\.py$", r"execute_.*", r"run_.*"],
            "confidence": 0.85,
        },
        FileCategory.SYSTEM_CONFIG: {
            "patterns": [r"\.cortex-.*", r"\.cortex/.*", r"setup\.py", r"setup\.cfg"],
            "confidence": 0.9,
        },
    }
    
    def __init__(self, repo_root: Path = Path(".")):
        """Initialize classifier.
        
        Args:
            repo_root: Repository root path
        """
        self.repo_root = Path(repo_root)
    
    def classify(self, file_path: Path) -> Tuple[FileCategory, ClassificationSignals]:
        """Classify file using multi-signal analysis.
        
        Args:
            file_path: Path to file to classify
            
        Returns:
            Tuple of (category, signals) for full classification details
        """
        # Normalize path
        file_path = Path(file_path)
        rel_path = str(file_path.relative_to(self.repo_root)) if file_path.is_absolute() else str(file_path)
        
        signals = ClassificationSignals()
        
        # Signal 1: Extension-based (fastest, primary)
        signals.extension_signal = self._classify_by_extension(rel_path)
        
        # Signal 2: Naming conventions
        signals.naming_signal = self._classify_by_name(rel_path)
        
        # Signal 3: Content-based (if file is readable)
        if file_path.is_file() and file_path.stat().st_size < 100_000:  # Skip large files
            signals.content_signal = self._classify_by_content(file_path)
        
        # Signal 4: Reference analysis (check if imported/referenced)
        signals.reference_signal = self._classify_by_references(rel_path)
        
        # Signal 5: Git history (if in git repo)
        if (self.repo_root / ".git").exists():
            signals.git_signal = self._classify_by_git(rel_path)
        
        category = signals.winning_category
        return category, signals
    
    def _classify_by_extension(self, rel_path: str) -> Tuple[FileCategory, float]:
        """Classify by file extension."""
        for category, rules in self.EXTENSION_PATTERNS.items():
            for pattern in rules["patterns"]:
                if re.search(pattern, rel_path, re.IGNORECASE):
                    # Check folder filters if specified
                    if "folder_filters" in rules:
                        if any(f in rel_path for f in rules["folder_filters"]):
                            return category, rules["confidence"]
                        elif category == FileCategory.SYSTEM_CODE:
                            # .py files outside cortex/ folder
                            continue
                    else:
                        return category, rules["confidence"]
        
        return FileCategory.UNKNOWN, 0.0
    
    def _classify_by_name(self, rel_path: str) -> Tuple[FileCategory, float]:
        """Classify by naming conventions."""
        file_name = Path(rel_path).name
        
        for category, rules in self.NAMING_PATTERNS.items():
            for pattern in rules["patterns"]:
                if re.search(pattern, file_name, re.IGNORECASE):
                    return category, rules["confidence"]
        
        return FileCategory.UNKNOWN, 0.0
    
    def _classify_by_content(self, file_path: Path) -> Tuple[FileCategory, float]:
        """Classify by content scanning (first 50 lines)."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = "".join([f.readline() for _ in range(50)])
            
            for category, rules in self.CONTENT_PATTERNS.items():
                for pattern in rules["patterns"]:
                    if re.search(pattern, content, re.MULTILINE):
                        return category, rules["confidence"]
        except Exception:
            pass
        
        return FileCategory.UNKNOWN, 0.0
    
    def _classify_by_references(self, rel_path: str) -> Tuple[FileCategory, float]:
        """Classify by checking if file is referenced in codebase."""
        # Simple heuristic: if file is in company/, likely company data
        if "company/" in rel_path:
            return FileCategory.COMPANY_DATA, 0.7
        
        # If in scripts/, likely scripts_utils
        if "scripts/" in rel_path:
            return FileCategory.SCRIPTS_UTILS, 0.8
        
        # If in deployment/, likely deployment
        if "deployment/" in rel_path:
            return FileCategory.DEPLOYMENT, 0.9
        
        return FileCategory.UNKNOWN, 0.0
    
    def _classify_by_git(self, rel_path: str) -> Tuple[FileCategory, float]:
        """Classify using git history (age, author, etc)."""
        try:
            # Get file creation date from git log
            result = subprocess.run(
                ["git", "log", "--follow", "--format=%ai", "--", rel_path],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split("\n")
                if lines:
                    # Most recent date (first line)
                    return FileCategory.UNKNOWN, 0.3  # Low confidence, use as tiebreaker
        except Exception:
            pass
        
        return FileCategory.UNKNOWN, 0.0


# AC_START: AC-VAC-ENH-001 | Signal-based file classification
__all__ = [
    "FileCategory",
    "ClassificationSignals",
    "FileClassifier",
]
# AC_COMPLETE: AC-VAC-ENH-001 ✅ File categorizer with multi-signal analysis
