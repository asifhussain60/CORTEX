"""
AC-054A-S1-01,02,03: LoadRepoOverviewUseCase Implementation

Use case for loading repository overview (basic metadata extraction).

Author: Phase 54-A Implementation (TDD)
Created: 2026-02-15
"""

from pathlib import Path
from typing import Any, Dict


class LoadRepoOverviewUseCase:
    """
    Load repository overview metadata.
    
    Extracts basic repository information:
    - Name, description, owner
    - Primary language
    - File/directory structure
    """
    
    def __init__(self) -> None:
        """Initialize overview loader."""
        pass
    
    def execute(self, repo_path: str) -> Dict[str, Any]:
        """
        Execute overview loading.
        
        Args:
            repo_path: Path to repository root
        
        Returns:
            Repository overview metadata
        """
        path = Path(repo_path)
        
        # Extract basic info
        name = path.name
        primary_language = self._detect_primary_language(path)
        
        # Count files
        file_count = self._count_files(path)
        
        return {
            "name": name,
            "path": str(path),
            "primary_language": primary_language,
            "file_count": file_count,
            "description": f"{name} repository"
        }
    
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
