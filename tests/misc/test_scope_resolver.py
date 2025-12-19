"""
Tests for Scope Resolver

RED PHASE: Tests written first, expecting failures.

Author: Asif Hussain
Version: 1.0.0
"""

import pytest
from pathlib import Path

from src.operations.modules.discovery.scope_resolver import ScopeResolver
from src.operations.modules.discovery.models import DiscoveryScope, DiscoveryDepth


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    project = tmp_path / "test_project"
    project.mkdir()
    (project / "src").mkdir()
    (project / "tests").mkdir()
    return project


@pytest.fixture
def resolver(temp_project):
    """Create ScopeResolver instance."""
    return ScopeResolver(project_root=temp_project)


class TestScopeResolverInitialization:
    """Test scope resolver initialization."""
    
    def test_init_resolves_project_root(self, temp_project):
        """Test that project root is resolved correctly."""
        resolver = ScopeResolver(project_root=temp_project)
        assert resolver.project_root == temp_project.resolve()
    
    def test_init_with_relative_path(self, temp_project):
        """Test initialization with relative path."""
        resolver = ScopeResolver(project_root=str(temp_project))
        assert resolver.project_root.is_absolute()


class TestScopeResolverResolve:
    """Test resolve() method."""
    
    def test_resolve_project_keyword(self, resolver, temp_project):
        """Test resolving 'project' keyword."""
        scope = resolver.resolve(scope_input="project", depth="moderate")
        assert isinstance(scope, DiscoveryScope)
        assert scope.root_path == temp_project.resolve()
        assert scope.depth == DiscoveryDepth.MODERATE
    
    def test_resolve_path_string(self, resolver, temp_project):
        """Test resolving path string."""
        scope = resolver.resolve(scope_input=str(temp_project / "src"))
        assert isinstance(scope, DiscoveryScope)
        assert scope.root_path == (temp_project / "src").resolve()
    
    def test_resolve_path_object(self, resolver, temp_project):
        """Test resolving Path object."""
        scope = resolver.resolve(scope_input=temp_project / "src")
        assert isinstance(scope, DiscoveryScope)
        assert scope.root_path == (temp_project / "src").resolve()
    
    def test_resolve_dict_input(self, resolver, temp_project):
        """Test resolving dictionary specification."""
        scope_dict = {
            "root_path": str(temp_project),
            "include_patterns": ["*.py"],
            "exclude_patterns": ["__pycache__"],
            "max_depth": 5
        }
        scope = resolver.resolve(scope_input=scope_dict)
        assert isinstance(scope, DiscoveryScope)
        assert scope.root_path == temp_project.resolve()
        assert "*.py" in scope.include_patterns
        assert "__pycache__" in scope.exclude_patterns
        assert scope.max_depth == 5
    
    def test_resolve_invalid_type(self, resolver):
        """Test that invalid types raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported scope input type"):
            resolver.resolve(scope_input=123)
    
    def test_resolve_applies_depth(self, resolver, temp_project):
        """Test that depth parameter is applied."""
        scope = resolver.resolve(scope_input="project", depth="quick")
        assert isinstance(scope, DiscoveryScope)
        assert scope.depth == DiscoveryDepth.QUICK


class TestScopeResolverValidation:
    """Test validate_scope() method."""
    
    def test_validate_scope_valid(self, resolver, temp_project):
        """Test validation of valid scope."""
        scope = DiscoveryScope(root_path=temp_project)
        assert resolver.validate_scope(scope) is True
    
    def test_validate_scope_nonexistent_path(self, resolver, temp_project):
        """Test validation fails for nonexistent path."""
        scope = DiscoveryScope(root_path=temp_project / "nonexistent")
        with pytest.raises(ValueError, match="Path does not exist"):
            resolver.validate_scope(scope)
    
    def test_validate_scope_file_not_directory(self, resolver, temp_project):
        """Test validation fails when path is a file."""
        file_path = temp_project / "file.txt"
        file_path.write_text("content")
        scope = DiscoveryScope(root_path=file_path)
        with pytest.raises(ValueError, match="Path is not a directory"):
            resolver.validate_scope(scope)


class TestScopeResolverEstimation:
    """Test estimate_file_count() method."""
    
    def test_estimate_file_count_empty_directory(self, resolver, temp_project):
        """Test estimation for empty directory."""
        empty_dir = temp_project / "empty"
        empty_dir.mkdir()
        scope = DiscoveryScope(root_path=empty_dir)
        # RED PHASE: Returns 0 (placeholder)
        # Should return actual count in GREEN phase
        count = resolver.estimate_file_count(scope)
        assert count == 0  # Currently returns 0
    
    def test_estimate_file_count_with_files(self, resolver, temp_project):
        """Test estimation with actual files."""
        # Create some files
        (temp_project / "file1.py").write_text("code")
        (temp_project / "file2.py").write_text("code")
        scope = DiscoveryScope(root_path=temp_project)
        # RED PHASE: Returns 0 (placeholder)
        count = resolver.estimate_file_count(scope)
        # Should be > 0 in GREEN phase
        assert isinstance(count, int)


# RED PHASE SUMMARY:
# - Tests define expected behavior
# - Most tests expect NotImplementedError
# - Some tests expect ValueError for invalid input
# - Next: GREEN phase - implement to make tests pass
