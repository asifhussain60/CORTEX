"""
Unit Tests for Path Resolver

Tests cross-platform path resolution functionality.
"""

import os
from pathlib import Path

import pytest


class TestGetProjectRoot:
    """Tests for get_project_root function."""
    
    def test_uses_env_variable_when_set(self, temp_dir, monkeypatch):
        """Should use CORTEX_ROOT env var when set."""
        from src.core import path_resolver
        
        monkeypatch.setenv("CORTEX_ROOT", str(temp_dir))
        path_resolver.reset_project_root()
        
        result = path_resolver.get_project_root()
        
        assert result == temp_dir
    
    def test_finds_git_root(self, temp_dir, monkeypatch):
        """Should find .git directory and use its parent."""
        from src.core import path_resolver
        
        # Clear env var
        monkeypatch.delenv("CORTEX_ROOT", raising=False)
        
        # Create fake git directory
        git_dir = temp_dir / ".git"
        git_dir.mkdir()
        
        # Change to subdirectory
        subdir = temp_dir / "src" / "core"
        subdir.mkdir(parents=True)
        
        monkeypatch.chdir(subdir)
        path_resolver.reset_project_root()
        
        result = path_resolver.get_project_root()
        
        assert result == temp_dir
    
    def test_caches_result(self, temp_dir, monkeypatch):
        """Should cache the project root."""
        from src.core import path_resolver
        
        monkeypatch.setenv("CORTEX_ROOT", str(temp_dir))
        path_resolver.reset_project_root()
        
        # First call
        result1 = path_resolver.get_project_root()
        
        # Change env (shouldn't affect cached result)
        monkeypatch.setenv("CORTEX_ROOT", "/different/path")
        
        # Second call
        result2 = path_resolver.get_project_root()
        
        assert result1 == result2 == temp_dir


class TestResolvePath:
    """Tests for resolve_path function."""
    
    def test_resolves_single_part(self, mock_project_root):
        """Should resolve single path component."""
        from src.core.path_resolver import resolve_path
        
        result = resolve_path("cortex-brain")
        
        assert result == mock_project_root / "cortex-brain"
    
    def test_resolves_multiple_parts(self, mock_project_root):
        """Should resolve multiple path components."""
        from src.core.path_resolver import resolve_path
        
        result = resolve_path("cortex-brain", "tier0", "governance")
        
        assert result == mock_project_root / "cortex-brain" / "tier0" / "governance"


class TestTierPath:
    """Tests for tier_path function."""
    
    @pytest.mark.parametrize("tier", [0, 1, 2, 3])
    def test_valid_tiers(self, mock_project_root, tier):
        """Should return correct path for valid tiers."""
        from src.core.path_resolver import tier_path
        
        result = tier_path(tier)
        
        assert result == mock_project_root / "cortex-brain" / f"tier{tier}"
    
    @pytest.mark.parametrize("invalid_tier", [-1, 4, 5, 100])
    def test_invalid_tiers_raise_error(self, mock_project_root, invalid_tier):
        """Should raise ValueError for invalid tiers."""
        from src.core.path_resolver import tier_path
        
        with pytest.raises(ValueError, match="Invalid tier"):
            tier_path(invalid_tier)
