"""
Tests for WorkspaceContext.
"""

import pytest
from pathlib import Path
from src.context.workspace_context import WorkspaceContext


class TestWorkspaceContext:
    """Test WorkspaceContext creation and validation."""
    
    def test_create_with_paths(self):
        """Test creating context with Path objects."""
        repo = Path("D:/PROJECTS/NOOR CANVAS")
        cortex = Path("D:/PROJECTS/CORTEX")
        
        ctx = WorkspaceContext(repo_root=repo, cortex_root=cortex)
        
        assert ctx.repo_root == repo.resolve()
        assert ctx.cortex_root == cortex.resolve()
    
    def test_create_with_strings(self):
        """Test creating context with string paths."""
        repo = "D:/PROJECTS/NOOR CANVAS"
        cortex = "D:/PROJECTS/CORTEX"
        
        ctx = WorkspaceContext(repo_root=repo, cortex_root=cortex)
        
        assert ctx.repo_root == Path(repo).resolve()
        assert ctx.cortex_root == Path(cortex).resolve()
    
    def test_metadata_defaults(self):
        """Test default metadata."""
        ctx = WorkspaceContext(
            repo_root=Path("."),
            cortex_root=Path(".")
        )
        
        assert ctx.source == 'unknown'
        assert ctx.confidence == 0.5
        assert ctx.warnings == []
    
    def test_metadata_custom(self):
        """Test custom metadata."""
        ctx = WorkspaceContext(
            repo_root=Path("."),
            cortex_root=Path("."),
            metadata={
                'source': 'explicit',
                'confidence': 1.0,
                'warnings': ['test warning']
            }
        )
        
        assert ctx.source == 'explicit'
        assert ctx.confidence == 1.0
        assert ctx.warnings == ['test warning']
    
    def test_is_cortex_repo_true(self):
        """Test is_cortex_repo when repo is CORTEX."""
        cortex_root = Path(__file__).parent.parent.parent
        
        ctx = WorkspaceContext(
            repo_root=cortex_root,
            cortex_root=cortex_root
        )
        
        assert ctx.is_cortex_repo() is True
    
    def test_is_cortex_repo_false(self):
        """Test is_cortex_repo when repo is not CORTEX."""
        cortex_root = Path(__file__).parent.parent.parent
        other_repo = Path("D:/PROJECTS/NOOR CANVAS")
        
        ctx = WorkspaceContext(
            repo_root=other_repo,
            cortex_root=cortex_root
        )
        
        assert ctx.is_cortex_repo() is False
    
    def test_validate_existing_paths(self):
        """Test validation with existing paths."""
        cortex_root = Path(__file__).parent.parent.parent
        
        ctx = WorkspaceContext(
            repo_root=cortex_root,
            cortex_root=cortex_root
        )
        
        assert ctx.validate() is True
    
    def test_validate_nonexistent_paths(self):
        """Test validation with non-existent paths."""
        ctx = WorkspaceContext(
            repo_root=Path("/nonexistent/repo"),
            cortex_root=Path("/nonexistent/cortex")
        )
        
        assert ctx.validate() is False
        assert len(ctx.warnings) > 0
    
    def test_repr(self):
        """Test string representation."""
        ctx = WorkspaceContext(
            repo_root=Path("."),
            cortex_root=Path(".."),
            metadata={'source': 'explicit', 'confidence': 1.0}
        )
        
        repr_str = repr(ctx)
        assert 'WorkspaceContext' in repr_str
        assert 'repo_root' in repr_str
        assert 'explicit' in repr_str
        assert '100%' in repr_str
