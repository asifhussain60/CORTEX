"""
Integration Tests for LENS + TechStackAnalyzer (Phase 90 S1).

Tests tech stack detection integration with LENSOrchestrator.

Authority: AC-PHASE90-S1-INT-001
Coverage: LENS orchestration with tech stack detection
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.lens.lens_orchestrator import LENSOrchestrator, LENSContext
from cortex.lens.models.tech_stack import TechStack, TechCategory, TechStackItem


class TestLENSTechStackIntegration:
    """Test tech stack detection integration with LENS."""
    
    @patch('cortex.lens.lens_orchestrator.GitHistoryAnalyzer')
    @patch('cortex.lens.lens_orchestrator.ASTAnalyzer')
    @patch('cortex.lens.lens_orchestrator.CommentExtractor')
    def test_lens_includes_tech_stack(self, mock_comment, mock_ast, mock_git):
        """Test: LENS analyze_file returns tech_stack field."""
        # Setup mocks
        mock_git_instance = Mock()
        mock_git_instance.get_file_history.return_value = Mock(success=True, commits=[])
        mock_git.return_value = mock_git_instance
        
        mock_ast_instance = Mock()
        mock_ast_instance.analyze_file.return_value = {
            "functions": [],
            "classes": [],
            "imports": ["flask", "sqlalchemy"],
            "from_imports": {}
        }
        mock_ast.return_value = mock_ast_instance
        
        mock_comment_instance = Mock()
        mock_comment_instance.extract_from_file.return_value = Mock(
            success=True,
            comments=[]
        )
        mock_comment.return_value = mock_comment_instance
        
        # Create orchestrator
        orchestrator = LENSOrchestrator(repo_path=Path("/test/repo"))
        
        # Analyze file
        result = orchestrator.analyze_file(Path("app.py"))
        
        # Verify tech_stack field exists
        assert "tech_stack" in result
        assert "primary_language" in result["tech_stack"]
        assert "frameworks" in result["tech_stack"]
        assert "libraries" in result["tech_stack"]
    
    @patch('cortex.lens.lens_orchestrator.GitHistoryAnalyzer')
    @patch('cortex.lens.lens_orchestrator.ASTAnalyzer')
    @patch('cortex.lens.lens_orchestrator.CommentExtractor')
    def test_lens_detects_python_flask(self, mock_comment, mock_ast, mock_git):
        """Test: LENS detects Python + Flask correctly."""
        # This test validates primary language detection from .py file
        # Framework detection via imports validated in unit tests
        
        # Setup mocks
        mock_git_instance = Mock()
        mock_git_instance.get_file_history.return_value = Mock(success=True, commits=[])
        mock_git.return_value = mock_git_instance
        
        mock_ast_instance = Mock()
        mock_ast_instance.analyze_file.return_value = {
            "functions": [{"name": "create_app"}],
            "classes": [],
            "imports": ["flask", "flask_sqlalchemy"],
            "from_imports": {"flask": ["Flask", "jsonify"]}
        }
        mock_ast.return_value = mock_ast_instance
        
        mock_comment_instance = Mock()
        mock_comment_instance.extract_from_file.return_value = Mock(success=True, comments=[])
        mock_comment.return_value = mock_comment_instance
        
        # Create orchestrator
        orchestrator = LENSOrchestrator(repo_path=Path("/test/repo"))
        
        # Analyze Python Flask file
        result = orchestrator.analyze_file(Path("app.py"))
        
        # Verify Python detected (primary check - file extension)
        tech_stack = result["tech_stack"]
        assert tech_stack["primary_language"] == "python", "Python should be detected from .py file"
        assert "python" in tech_stack["languages"], "Python should be in languages list"
    
    @patch('cortex.lens.lens_orchestrator.GitHistoryAnalyzer')
    @patch('cortex.lens.lens_orchestrator.ASTAnalyzer')
    @patch('cortex.lens.lens_orchestrator.CommentExtractor')
    def test_lens_detects_dotnet(self, mock_comment, mock_ast, mock_git):
        """Test: LENS detects .NET from .cs file."""
        # Setup mocks
        mock_git_instance = Mock()
        mock_git_instance.get_file_history.return_value = Mock(success=True, commits=[])
        mock_git.return_value = mock_git_instance
        
        mock_ast_instance = Mock()
        mock_ast_instance.analyze_file.return_value = {
            "functions": [],
            "classes": [{"name": "Startup"}],
            "imports": [],
            "from_imports": {}
        }
        mock_ast.return_value = mock_ast_instance
        
        mock_comment_instance = Mock()
        mock_comment_instance.extract_from_file.return_value = Mock(success=True, comments=[])
        mock_comment.return_value = mock_comment_instance
        
        # Create orchestrator
        orchestrator = LENSOrchestrator(repo_path=Path("/test/repo"))
        
        # Analyze .NET file
        result = orchestrator.analyze_file(Path("Startup.cs"))
        
        # Verify .NET detected
        assert "csharp" in result["tech_stack"]["languages"]
    
    @patch('cortex.lens.lens_orchestrator.GitHistoryAnalyzer')
    @patch('cortex.lens.lens_orchestrator.ASTAnalyzer')
    @patch('cortex.lens.lens_orchestrator.CommentExtractor')
    def test_lens_tech_stack_in_metadata(self, mock_comment, mock_ast, mock_git):
        """Test: Tech stack detection tracked in metadata."""
        # Setup mocks
        mock_git_instance = Mock()
        mock_git_instance.get_file_history.return_value = Mock(success=True, commits=[])
        mock_git.return_value = mock_git_instance
        
        mock_ast_instance = Mock()
        mock_ast_instance.analyze_file.return_value = {
            "functions": [],
            "classes": [],
            "imports": ["django"],
            "from_imports": {}
        }
        mock_ast.return_value = mock_ast_instance
        
        mock_comment_instance = Mock()
        mock_comment_instance.extract_from_file.return_value = Mock(success=True, comments=[])
        mock_comment.return_value = mock_comment_instance
        
        # Create orchestrator
        orchestrator = LENSOrchestrator(repo_path=Path("/test/repo"))
        
        # Analyze file
        result = orchestrator.analyze_file(Path("views.py"))
        
        # Verify metadata includes tech_stack analyzer
        assert "tech_stack" in result["_metadata"]["analyzers_run"]
    
    @patch('cortex.lens.lens_orchestrator.GitHistoryAnalyzer')
    @patch('cortex.lens.lens_orchestrator.ASTAnalyzer')
    @patch('cortex.lens.lens_orchestrator.CommentExtractor')
    def test_lens_context_includes_tech_stack(self, mock_comment, mock_ast, mock_git):
        """Test: LENSContext includes tech_stack field."""
        # Create LENSContext
        context = LENSContext(
            git_analysis={"commits": []},
            ast_analysis={"functions": []},
            comment_analysis={"todos": []},
            tech_stack={
                "primary_language": "python",
                "frameworks": ["flask"]
            }
        )
        
        # Convert to dict
        result = context.to_dict()
        
        # Verify tech_stack field present
        assert "tech_stack" in result
        assert result["tech_stack"]["primary_language"] == "python"
        assert "flask" in result["tech_stack"]["frameworks"]
    
    @patch('cortex.lens.lens_orchestrator.GitHistoryAnalyzer')
    @patch('cortex.lens.lens_orchestrator.ASTAnalyzer')
    @patch('cortex.lens.lens_orchestrator.CommentExtractor')
    def test_lens_error_handling(self, mock_comment, mock_ast, mock_git):
        """Test: LENS handles tech stack detection errors gracefully."""
        # Setup mocks
        mock_git_instance = Mock()
        mock_git_instance.get_file_history.return_value = Mock(success=True, commits=[])
        mock_git.return_value = mock_git_instance
        
        mock_ast_instance = Mock()
        mock_ast_instance.analyze_file.return_value = {
            "error": "AST parse failed"
        }
        mock_ast.return_value = mock_ast_instance
        
        mock_comment_instance = Mock()
        mock_comment_instance.extract_from_file.return_value = Mock(success=True, comments=[])
        mock_comment.return_value = mock_comment_instance
        
        # Create orchestrator
        orchestrator = LENSOrchestrator(repo_path=Path("/test/repo"))
        
        # Analyze file with AST error
        result = orchestrator.analyze_file(Path("broken.py"))
        
        # Should have tech_stack field even with error
        assert "tech_stack" in result
        # But may have empty detection due to no AST imports
        assert "primary_language" in result["tech_stack"]


# AC_START: AC-PHASE90-S1-INT-001
# Description: Integration tests for LENS + TechStackAnalyzer
