"""Domain Brain Adapters

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class GitAdapter:
    """Git repository adapter."""
    repo_path: str
    branch: str = "main"

__all__ = ["GitAdapter"]
