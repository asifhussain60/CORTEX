"""
Load Repository Overview Use Case (Phase 54-A S1)

AC_START: AC-PHASE54A-S1-UC01
Description: Extract basic repository metadata
Authority: phase-54-A-incremental-onboarding-refactor.yaml, S1 task 1
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.brain.core.result import Err, Ok, Result


@dataclass
class RepoOverview:
    """Repository overview model."""
    name: str
    path: str
    file_count: int
    language_distribution: Dict[str, int]
    has_tests: bool
    test_framework: Optional[str]
    has_docs: bool
    doc_format: Optional[str]
    created_at: datetime


class LoadRepoOverviewUseCase:
    """Extract basic repository metadata (SOLID: Single Responsibility)."""

    def __init__(self) -> None:
        """Initialize use case."""
        self.logger = None  # Optional logging

    def execute(self, repo_path: Path) -> Result[RepoOverview]:
        """
        Extract repository overview.

        Args:
            repo_path: Path to repository

        Returns:
            Result containing RepoOverview or error
        """
        try:
            # Ensure path is a Path object
            if isinstance(repo_path, str):
                repo_path = Path(repo_path)

            # Check existence first
            if not repo_path.exists():
                return Err(f"Repository not found: {repo_path}")

            if not repo_path.is_dir():
                return Err(f"Path is not a directory: {repo_path}")

            # Extract basic metadata
            name = repo_path.name
            file_count = self._count_files(repo_path)
            language_dist = self._detect_languages(repo_path)
            has_tests, test_framework = self._detect_tests(repo_path)
            has_docs, doc_format = self._detect_docs(repo_path)

            overview = RepoOverview(
                name=name,
                path=str(repo_path),
                file_count=file_count,
                language_distribution=language_dist,
                has_tests=has_tests,
                test_framework=test_framework,
                has_docs=has_docs,
                doc_format=doc_format,
                created_at=datetime.now(),
            )

            return Ok(overview)

        except Exception as e:
            return Err(f"Failed to load repository overview: {str(e)}")

    def _count_files(self, repo_path: Path) -> int:
        """Count total files in repository."""
        try:
            return sum(1 for _ in repo_path.rglob("*") if _.is_file())
        except Exception:
            return 0

    def _detect_languages(self, repo_path: Path) -> Dict[str, int]:
        """Detect programming languages."""
        extensions = {}
        try:
            for file_path in repo_path.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext:
                        extensions[ext] = extensions.get(ext, 0) + 1
        except Exception:
            pass
        return extensions

    def _detect_tests(self, repo_path: Path) -> tuple[bool, Optional[str]]:
        """Detect test framework."""
        test_indicators = {
            "pytest": ["pytest.ini", "tests/", "test_*.py"],
            "unittest": ["test_*.py", "tests/"],
            "jest": ["jest.config.js", "__tests__/"],
            "mocha": ["mocha.opts", "test/"],
        }

        for framework, patterns in test_indicators.items():
            for pattern in patterns:
                try:
                    if "*" in pattern:
                        if list(repo_path.rglob(pattern)):
                            return (True, framework)
                    else:
                        if (repo_path / pattern).exists():
                            return (True, framework)
                except Exception:
                    pass

        return (False, None)

    def _detect_docs(self, repo_path: Path) -> tuple[bool, Optional[str]]:
        """Detect documentation."""
        if (repo_path / "docs").exists():
            return (True, "markdown")
        if (repo_path / "README.md").exists():
            return (True, "markdown")
        return (False, None)


# AC_COMPLETE: AC-PHASE54A-S1-UC01 ✅
