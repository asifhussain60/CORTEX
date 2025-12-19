"""
Tests for ContextResolver.
"""

import pytest
from pathlib import Path
import os
from src.context.context_resolver import ContextResolver, resolve_context


class TestContextResolver:
    """Test context resolution with graceful degradation."""
    
    def test_explicit_parameters_priority(self):
        """Test that explicit parameters have highest priority."""
        resolver = ContextResolver()
        
        repo = Path("D:/PROJECTS/NOOR CANVAS")
        cortex = Path("D:/PROJECTS/CORTEX")
        
        ctx = resolver.resolve(repo_root=repo, cortex_root=cortex)
        
        assert ctx.repo_root == repo.resolve()
        assert ctx.cortex_root == cortex.resolve()
        assert ctx.source == 'explicit'
        assert ctx.confidence == 1.0
    
    def test_partial_explicit_parameters(self):
        """Test with only one explicit parameter (should degrade)."""
        resolver = ContextResolver()
        
        repo = Path("D:/PROJECTS/NOOR CANVAS")
        
        ctx = resolver.resolve(repo_root=repo)
        
        # Should get repo from explicit, cortex from fallback
        assert ctx.repo_root == repo.resolve()
        assert ctx.cortex_root is not None
        # Source depends on what's available (env, config, or cwd)
        assert ctx.source in ['environment', 'config', 'cwd_fallback']
    
    def test_copilot_context_degradation(self):
        """Test that Copilot context degrades gracefully when unavailable."""
        resolver = ContextResolver()
        
        # In POC, Copilot is always unavailable
        ctx = resolver.resolve()
        
        # Should degrade to env, config, or cwd
        assert ctx.source in ['environment', 'config', 'cwd_fallback']
        assert ctx.repo_root is not None
        assert ctx.cortex_root is not None
    
    def test_environment_variables(self, monkeypatch):
        """Test resolution from environment variables."""
        monkeypatch.setenv('CORTEX_TARGET_REPO', 'D:/PROJECTS/NOOR CANVAS')
        monkeypatch.setenv('CORTEX_ROOT', 'D:/PROJECTS/CORTEX')
        
        resolver = ContextResolver()
        ctx = resolver.resolve()
        
        assert ctx.source == 'environment'
        assert ctx.confidence == 0.80
        assert 'NOOR CANVAS' in str(ctx.repo_root)
        assert 'CORTEX' in str(ctx.cortex_root)
    
    def test_cwd_fallback(self, monkeypatch):
        """Test fallback to Path.cwd()."""
        # Clear environment variables
        monkeypatch.delenv('CORTEX_TARGET_REPO', raising=False)
        monkeypatch.delenv('CORTEX_ROOT', raising=False)
        
        resolver = ContextResolver()
        ctx = resolver.resolve()
        
        # Should fall back to cwd (unless config exists)
        if ctx.source == 'cwd_fallback':
            assert ctx.confidence == 0.50
            assert len(ctx.warnings) > 0
            assert 'FALLBACK' in ctx.warnings[0]
    
    def test_warnings_on_fallback(self):
        """Test that fallback generates warnings."""
        resolver = ContextResolver()
        ctx = resolver.resolve()
        
        if ctx.source == 'cwd_fallback':
            assert len(ctx.warnings) > 0
            assert any('FALLBACK' in w for w in ctx.warnings)
            assert any('RECOMMENDATION' in w for w in ctx.warnings)
    
    def test_convenience_function(self):
        """Test resolve_context convenience function."""
        repo = Path("D:/PROJECTS/NOOR CANVAS")
        cortex = Path("D:/PROJECTS/CORTEX")
        
        ctx = resolve_context(repo_root=repo, cortex_root=cortex)
        
        assert ctx.repo_root == repo.resolve()
        assert ctx.cortex_root == cortex.resolve()
        assert ctx.source == 'explicit'
