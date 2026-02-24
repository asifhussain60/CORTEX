"""
AC-054A-S1-01,02,03: LoadRepoOverviewUseCase Implementation

Use case for loading repository overview (basic metadata extraction).

Author: Phase 54-A Implementation (TDD)
Created: 2026-02-15
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class RepoMetadata:
    """Repository metadata model."""
    name: str
    url: str
    language: str
    stars: int = 0
    forks: int = 0
    last_updated: str = ""


class LoadRepoOverviewUseCase:
    """
    Load repository overview metadata.
    
    Extracts basic repository information:
    - Name, description, owner
    - Primary language
    - File/directory structure
    """
    
    def __init__(self, repository: Any = None) -> None:
        """Initialize overview loader.
        
        Args:
            repository: Optional repository interface for persistence.
                        Defaults to JSONProfileRepository when not provided.
        """
        if repository is None:
            try:
                from cortex.infrastructure.repositories.json_profile_repository import (
                    JSONProfileRepository,
                )
                _default_path = Path(__file__).parent.parent.parent.parent.parent / ".cortex-runtime" / "profiles"
                repository = JSONProfileRepository(storage_path=_default_path)
            except Exception:
                pass
        self.repository = repository
    
    def execute(self, repo_data: Any) -> RepoMetadata:
        """
        Execute overview loading.
        
        Args:
            repo_data: Repository data (dict or path string)
        
        Returns:
            RepoMetadata object
        """
        # Handle dict input (pre-analyzed metadata)
        if isinstance(repo_data, dict):
            return RepoMetadata(
                name=repo_data.get("name", "unknown"),
                url=repo_data.get("url", ""),
                language=repo_data.get("language", "Unknown"),
                stars=repo_data.get("stars", 0),
                forks=repo_data.get("forks", 0),
                last_updated=repo_data.get("last_updated", "")
            )
        
        # Handle string path
        path = Path(repo_data)
        
        # Extract basic info
        name = path.name
        primary_language = self._detect_primary_language(path)
        
        return RepoMetadata(
            name=name,
            url="",
            language=primary_language
        )
    
    def _detect_primary_language(self, path: Path) -> str:
        """Detect primary programming language."""
        # Simple detection based on file extensions
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cs": "C#"
        }
        
        if path.exists():
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    ext = file_path.suffix
                    if ext in extensions:
                        return extensions[ext]
        
        return "Unknown"
    
    def _count_files(self, path: Path) -> int:
        """Count total files in repository."""
        if not path.exists():
            return 0
        
        count = 0
        for file_path in path.rglob("*"):
            if file_path.is_file():
                count += 1
        
        return count
