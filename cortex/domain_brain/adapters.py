"""Domain Brain Adapters

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class GitAdapter:
    """Git repository adapter."""
    repo_path: str
    branch: str = "main"


@dataclass
class CommentsAdapter:
    """Adapter for comments."""
    source: str
    
    def get_comments(self) -> list:
        """Get comments."""
        return []


@dataclass
class RelationshipsAdapter:
    """Adapter for relationships between entities."""
    source: str
    
    def get_relationships(self) -> list:
        """Get relationships."""
        return []



class ASTAdapter:
    """Abstract syntax tree adapter."""
    
    def parse(self, code: str) -> dict:
        """Parse code to AST."""
        return {}

__all__ = ["GitAdapter", "ASTAdapter"]
