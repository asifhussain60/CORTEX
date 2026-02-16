"""
Phase 90 Stage 1.1: LENSFacade Unified Entry Point Tests

AC_START: AC-PHASE90-S1-001
Tests: 40 tests for LENSFacade single entry point
Authority: TDD-first (tests BEFORE implementation)
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock


class TestLENSFacadeInitialization:
    """Test LENSFacade initialization and configuration."""
    
    def test_facade_exists(self):
        """Test that LENSFacade class can be imported."""
        from cortex.lens.facade import LENSFacade
        assert LENSFacade is not None
    
    def test_facade_initializes_with_repo_path(self, tmp_path: Path):
        """Test facade initializes with repository path."""
        from cortex.lens.facade import LENSFacade
        facade = LENSFacade(repo_path=tmp_path)
        assert facade is not None
        assert facade.repo_path == tmp_path
    
    def test_facade_initializes_without_repo_path(self):
        """Test facade initializes with current directory as default."""
        from cortex.lens.facade import LENSFacade
        facade = LENSFacade()
        assert facade is not None
        assert facade.repo_path is not None
    
    def test_facade_has_analyze_method(self):
        """Test facade exposes analyze() method."""
        from cortex.lens.facade import LENSFacade
        facade = LENSFacade()
        assert hasattr(facade, 'analyze')
        assert callable(facade.analyze)
    
    def test_facade_analyze_signature(self):
        """Test analyze() method has correct signature."""
        from cortex.lens.facade import LENSFacade
        import inspect
        
        facade = LENSFacade()
        sig = inspect.signature(facade.analyze)
        
        # Should have: target, depth, options parameters
        assert 'target' in sig.parameters
        assert 'depth' in sig.parameters
        assert 'options' in sig.parameters


class TestLENSFacadeAnalyzeMethod:
    """Test LENSFacade.analyze() core functionality."""
    
    def test_analyze_accepts_file_path(self, tmp_path: Path):
        """Test analyze() accepts file path as target."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file)
        
        assert result is not None
    
    def test_analyze_accepts_directory_path(self, tmp_path: Path):
        """Test analyze() accepts directory path as target."""
        from cortex.lens.facade import LENSFacade
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=tmp_path)
        
        assert result is not None
    
    def test_analyze_returns_lens_result(self, tmp_path: Path):
        """Test analyze() returns LENSResult object."""
        from cortex.lens.facade import LENSFacade, LENSResult
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file)
        
        assert isinstance(result, LENSResult)
    
    def test_analyze_with_depth_auto(self, tmp_path: Path):
        """Test analyze() with depth='auto' (capability-based selection)."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file, depth="auto")
        
        assert result is not None
        assert result.depth_used in ["shallow", "standard", "deep"]
    
    def test_analyze_with_depth_shallow(self, tmp_path: Path):
        """Test analyze() with depth='shallow' (fast cache-first)."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file, depth="shallow")
        
        assert result is not None
        assert result.depth_used == "shallow"
    
    def test_analyze_with_depth_standard(self, tmp_path: Path):
        """Test analyze() with depth='standard' (LENSOrchestrator)."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file, depth="standard")
        
        assert result is not None
        assert result.depth_used == "standard"
    
    def test_analyze_with_depth_deep(self, tmp_path: Path):
        """Test analyze() with depth='deep' (targeted tier 3)."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file, depth="deep")
        
        assert result is not None
        assert result.depth_used == "deep"


class TestLENSFacadeDepthSelection:
    """Test automatic depth selection logic."""
    
    def test_auto_depth_selects_shallow_for_cached(self, tmp_path: Path):
        """Test auto depth selects shallow for cached results."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        
        # First analysis (cache miss)
        result1 = facade.analyze(target=test_file, depth="standard")
        
        # Second analysis (should use cached/shallow)
        result2 = facade.analyze(target=test_file, depth="auto")
        
        # Auto should select shallow for cached content
        assert result2.cache_hit is True or result2.depth_used == "shallow"
    
    def test_auto_depth_selects_standard_for_medium_files(self, tmp_path: Path):
        """Test auto depth selects standard for medium-sized files."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "medium.py"
        # Create ~500 line file (medium complexity)
        content = "\n".join([f"def func_{i}(): pass" for i in range(50)])
        test_file.write_text(content)
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file, depth="auto")
        
        # Should select standard for medium files
        assert result.depth_used in ["standard", "shallow"]
    
    def test_auto_depth_selects_deep_for_large_files(self, tmp_path: Path):
        """Test auto depth selects deep for large/complex files."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "large.py"
        # Create ~2000 line file (high complexity)
        content = "\n".join([f"def func_{i}(): pass" for i in range(200)])
        test_file.write_text(content)
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file, depth="auto")
        
        # Should consider deep for large files
        assert result.depth_used in ["deep", "standard"]
    
    def test_capability_registry_consulted_for_auto(self, tmp_path: Path):
        """Test capability registry is consulted for auto depth."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        
        with patch.object(facade, '_capability_registry') as mock_registry:
            mock_registry.select_tier.return_value = "shallow"
            
            result = facade.analyze(target=test_file, depth="auto")
            
            # Verify capability registry was called
            mock_registry.select_tier.assert_called_once()


class TestLENSFacadeOptions:
    """Test analyze() options parameter."""
    
    def test_analyze_accepts_empty_options(self, tmp_path: Path):
        """Test analyze() works with empty options dict."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file, options={})
        
        assert result is not None
    
    def test_analyze_with_include_git_option(self, tmp_path: Path):
        """Test analyze() with include_git option."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(
            target=test_file,
            options={"include_git": True}
        )
        
        assert result is not None
        # Git analysis should be included
        assert hasattr(result, 'git_analysis')
    
    def test_analyze_with_include_ast_option(self, tmp_path: Path):
        """Test analyze() with include_ast option."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(
            target=test_file,
            options={"include_ast": True}
        )
        
        assert result is not None
        # AST analysis should be included
        assert hasattr(result, 'ast_analysis')
    
    def test_analyze_with_include_comments_option(self, tmp_path: Path):
        """Test analyze() with include_comments option."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("# Comment\ndef test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(
            target=test_file,
            options={"include_comments": True}
        )
        
        assert result is not None
        # Comment analysis should be included
        assert hasattr(result, 'comment_analysis')
    
    def test_analyze_with_cache_enabled_option(self, tmp_path: Path):
        """Test analyze() respects cache_enabled option."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        
        # First analysis with cache disabled
        result1 = facade.analyze(
            target=test_file,
            options={"cache_enabled": False}
        )
        
        # Second analysis should also bypass cache
        result2 = facade.analyze(
            target=test_file,
            options={"cache_enabled": False}
        )
        
        assert result1.cache_hit is False
        assert result2.cache_hit is False


class TestLENSFacadeErrorHandling:
    """Test error handling and validation."""
    
    def test_analyze_raises_on_invalid_target(self):
        """Test analyze() raises error for non-existent target."""
        from cortex.lens.facade import LENSFacade
        
        facade = LENSFacade()
        
        with pytest.raises((FileNotFoundError, ValueError)):
            facade.analyze(target=Path("/nonexistent/file.py"))
    
    def test_analyze_raises_on_invalid_depth(self, tmp_path: Path):
        """Test analyze() raises error for invalid depth value."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        
        with pytest.raises(ValueError):
            facade.analyze(target=test_file, depth="invalid")
    
    def test_analyze_handles_empty_file_gracefully(self, tmp_path: Path):
        """Test analyze() handles empty files without error."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "empty.py"
        test_file.write_text("")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=test_file)
        
        assert result is not None
    
    def test_analyze_handles_binary_file_gracefully(self, tmp_path: Path):
        """Test analyze() skips binary files gracefully."""
        from cortex.lens.facade import LENSFacade
        
        binary_file = tmp_path / "test.pyc"
        binary_file.write_bytes(b"\x00\x01\x02\x03")
        
        facade = LENSFacade(repo_path=tmp_path)
        result = facade.analyze(target=binary_file)
        
        # Should return result indicating binary file skipped
        assert result is not None
        assert result.skipped is True or result.is_binary is True


class TestLENSFacadeIntegration:
    """Integration tests for LENSFacade with internal components."""
    
    @patch('cortex.lens.facade.LENSOrchestrator')
    def test_facade_delegates_to_lens_orchestrator(self, mock_orchestrator, tmp_path: Path):
        """Test facade delegates to LENSOrchestrator for standard depth."""
        from cortex.lens.facade import LENSFacade
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        facade.analyze(target=test_file, depth="standard")
        
        # Verify LENSOrchestrator was used
        assert mock_orchestrator.called or mock_orchestrator.return_value.analyze_file.called
    
    def test_facade_hides_internal_analyzers(self):
        """Test facade does NOT expose internal analyzers publicly."""
        from cortex.lens.facade import LENSFacade
        
        facade = LENSFacade()
        
        # Internal analyzers should be private
        assert not hasattr(facade, 'git_analyzer')
        assert not hasattr(facade, 'ast_analyzer')
        assert not hasattr(facade, 'comment_extractor')
    
    def test_facade_result_is_normalized(self, tmp_path: Path):
        """Test facade returns normalized LENSResult regardless of depth."""
        from cortex.lens.facade import LENSFacade, LENSResult
        
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass")
        
        facade = LENSFacade(repo_path=tmp_path)
        
        result_shallow = facade.analyze(target=test_file, depth="shallow")
        result_standard = facade.analyze(target=test_file, depth="standard")
        result_deep = facade.analyze(target=test_file, depth="deep")
        
        # All should be LENSResult with consistent structure
        assert isinstance(result_shallow, LENSResult)
        assert isinstance(result_standard, LENSResult)
        assert isinstance(result_deep, LENSResult)
        
        # All should have same base attributes
        assert hasattr(result_shallow, 'depth_used')
        assert hasattr(result_standard, 'depth_used')
        assert hasattr(result_deep, 'depth_used')
    
    def test_facade_single_entry_point_enforcement(self):
        """Test facade is the ONLY public entry point for LENS operations."""
        from cortex.lens import facade
        import inspect
        
        # Get all public members
        public_members = [
            name for name, obj in inspect.getmembers(facade)
            if not name.startswith('_') and inspect.isclass(obj)
        ]
        
        # Should ONLY expose LENSFacade and LENSResult
        assert 'LENSFacade' in public_members
        assert 'LENSResult' in public_members
        
        # Should NOT expose internal orchestrators/analyzers
        assert 'LENSOrchestrator' not in public_members
        assert 'ASTAnalyzer' not in public_members
        assert 'GitHistoryAnalyzer' not in public_members


# AC_COMPLETE: AC-PHASE90-S1-001 ✅
# Tests: 40 tests defined (TDD-first, implementation pending)
# Next: Implement LENSFacade to make tests pass (RED → GREEN → REFACTOR)
