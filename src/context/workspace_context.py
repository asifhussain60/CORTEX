"""
WorkspaceContext: Universal context container for CORTEX operations.

Provides explicit workspace paths with validation and metadata.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkspaceContext:
    """
    Universal workspace context for CORTEX operations.
    
    Attributes:
        repo_root: Absolute path to target repository root
        cortex_root: Absolute path to CORTEX installation
        metadata: Additional context (source, confidence, warnings)
    """
    
    repo_root: Path
    cortex_root: Path
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure paths are absolute Path objects."""
        if not isinstance(self.repo_root, Path):
            self.repo_root = Path(self.repo_root).resolve()
        if not isinstance(self.cortex_root, Path):
            self.cortex_root = Path(self.cortex_root).resolve()
    
    @property
    def source(self) -> str:
        """How this context was resolved (explicit, copilot, env, config, cwd)."""
        return self.metadata.get('source', 'unknown')
    
    @property
    def confidence(self) -> float:
        """Confidence in context accuracy (0.0-1.0)."""
        return self.metadata.get('confidence', 0.5)
    
    @property
    def warnings(self) -> list:
        """Context resolution warnings."""
        return self.metadata.get('warnings', [])
    
    def validate(self) -> bool:
        """
        Validate context paths exist and are reasonable.
        
        Returns:
            True if valid, False otherwise
        """
        issues = []
        
        # Check repo_root exists
        if not self.repo_root.exists():
            issues.append(f"repo_root does not exist: {self.repo_root}")
        elif not self.repo_root.is_dir():
            issues.append(f"repo_root is not a directory: {self.repo_root}")
        
        # Check cortex_root exists
        if not self.cortex_root.exists():
            issues.append(f"cortex_root does not exist: {self.cortex_root}")
        elif not self.cortex_root.is_dir():
            issues.append(f"cortex_root is not a directory: {self.cortex_root}")
        
        # Check they're not the same (unless CORTEX is target repo)
        if self.repo_root == self.cortex_root:
            # Valid if repo_root contains CORTEX markers
            if not (self.repo_root / "cortex-brain").exists():
                issues.append(
                    f"repo_root == cortex_root but no CORTEX markers found: {self.repo_root}"
                )
        
        if issues:
            for issue in issues:
                logger.error(f"Context validation failed: {issue}")
            self.metadata.setdefault('warnings', []).extend(issues)
            return False
        
        return True
    
    def is_cortex_repo(self) -> bool:
        """Check if repo_root is CORTEX itself."""
        return (self.repo_root / "cortex-brain").exists()
    
    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"WorkspaceContext(\n"
            f"  repo_root={self.repo_root},\n"
            f"  cortex_root={self.cortex_root},\n"
            f"  source={self.source},\n"
            f"  confidence={self.confidence:.0%}\n"
            f")"
        )
