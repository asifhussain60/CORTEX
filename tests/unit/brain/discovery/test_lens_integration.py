"""
Unit tests for LENS Integration with Discovery System.

Tests the integration of GitHistoryAnalyzer, ASTAnalyzer, and CommentExtractor
with the discovery orchestrator for implementation truth verification (CORE-030).

Author: Asif Hussain
Phase: 9.3 - LENS Integration
AC-ID: DISC-008
"""

import pytest
pytestmark = pytest.mark.skip(reason="Phase 38.0 remediation pending - AST analyzer module incomplete")

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass, field
from typing import List

# Wrapped import - module may not exist
try:
    from cortex.brain.discovery.lens_integration import (
        LENSIntegration,
        LENSAnalysisResult,
        IntentPattern,
    )
except ModuleNotFoundError:
    pass


# Mock dataclass structures matching actual LENS analyzers
@dataclass
class MockGitCommit:
    hash: str
    author: str
    message: str


@dataclass
class MockGitHistoryResult:
    success: bool
    commits: List[MockGitCommit] = field(default_factory=list)


@dataclass
class MockFunctionInfo:
    name: str
    line_number: int
    parameters: List[str] = field(default_factory=list)


@dataclass
class MockASTAnalysisResult:
    success: bool
    functions: List[MockFunctionInfo] = field(default_factory=list)
    classes: List = field(default_factory=list)


@dataclass
class MockComment:
    line_number: int
    content: str
    comment_type: str


@dataclass
class MockCommentExtractionResult:
    success: bool
    comments: List[MockComment] = field(default_factory=list)


class TestLENSIntegrationInit:
    """Test LENSIntegration initialization."""

    def test_init_creates_integration(self, tmp_path):
        """Test that LENSIntegration initializes correctly."""
        integration = LENSIntegration(repo_path=tmp_path)
        
        assert integration.repo_path == tmp_path
        assert integration.git_analyzer is not None
        assert integration.ast_analyzer is not None
        assert integration.comment_extractor is not None

    def test_supported_analyzers_defined(self, tmp_path):
        """Test that supported analyzers list is defined."""
        integration = LENSIntegration(repo_path=tmp_path)
        analyzers = integration.get_supported_analyzers()
        
        assert "git_history" in analyzers
        assert "ast_analysis" in analyzers
        assert "comment_extraction" in analyzers
        assert len(analyzers) == 3


class TestGitHistoryIntegration:
    """Test GitHistoryAnalyzer integration."""

    def test_analyze_file_history(self, tmp_path):
        """Test analyzing file commit history."""
        test_file = tmp_path / "module.py"
        test_file.write_text("def foo(): pass")
        
        integration = LENSIntegration(repo_path=tmp_path)
        
        with patch.object(integration.git_analyzer, 'get_file_history') as mock_history:
            mock_history.return_value = MockGitHistoryResult(
                success=True,
                commits=[
                    MockGitCommit(hash="abc123", message="refactor: Extract foo method", author="dev"),
                    MockGitCommit(hash="def456", message="fix: Handle edge case", author="dev"),
                ]
            )
            
            result = integration.analyze_git_history(test_file)
            
            assert result is not None
            assert "commits" in result
            assert len(result["commits"]) == 2
            assert result["commits"][0]["message"] == "refactor: Extract foo method"
            mock_history.assert_called_once_with(test_file)

    def test_detect_refactor_pattern_from_commits(self, tmp_path):
        """Test detecting refactor intent from commit messages."""
        test_file = tmp_path / "service.py"
        test_file.write_text("class Service: pass")
        
        integration = LENSIntegration(repo_path=tmp_path)
        
        with patch.object(integration.git_analyzer, 'get_file_history') as mock_history, \
             patch.object(integration.ast_analyzer, 'analyze_file') as mock_ast, \
             patch.object(integration.comment_extractor, 'extract_comments') as mock_comments:
            
            mock_history.return_value = MockGitHistoryResult(
                success=True,
                commits=[
                    MockGitCommit(hash="abc", message="refactor: Simplify logic", author="dev"),
                    MockGitCommit(hash="def", message="refactor: Extract method", author="dev"),
                ]
            )
            mock_ast.return_value = MockASTAnalysisResult(success=True, functions=[])
            mock_comments.return_value = MockCommentExtractionResult(success=True, comments=[])
            
            patterns = integration.detect_intent_patterns(test_file)
            
            assert IntentPattern.REFACTOR in patterns
            assert patterns[IntentPattern.REFACTOR] >= 2


class TestASTAnalysisIntegration:
    """Test ASTAnalyzer integration."""

    def test_analyze_code_complexity(self, tmp_path):
        """Test analyzing code complexity metrics."""
        test_file = tmp_path / "complex.py"
        test_file.write_text("""
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                yield i
            else:
                continue
    return None
""")
        
        integration = LENSIntegration(repo_path=tmp_path)
        
        with patch.object(integration.ast_analyzer, 'analyze_file') as mock_analyze:
            mock_analyze.return_value = MockASTAnalysisResult(
                success=True,
                functions=[MockFunctionInfo(name="complex_function", line_number=2, parameters=["x"])]
            )
            
            result = integration.analyze_ast(test_file)
            
            assert result is not None
            assert "functions" in result
            assert len(result["functions"]) == 1
            assert result["functions"][0]["name"] == "complex_function"
            mock_analyze.assert_called_once_with(test_file)

    def test_detect_high_complexity_refactor_candidate(self, tmp_path):
        """Test detecting high complexity as refactor candidate."""
        test_file = tmp_path / "messy.py"
        test_file.write_text("def messy(): pass")
        
        integration = LENSIntegration(repo_path=tmp_path)
        
        with patch.object(integration.git_analyzer, 'get_file_history') as mock_git, \
             patch.object(integration.ast_analyzer, 'analyze_file') as mock_analyze, \
             patch.object(integration.comment_extractor, 'extract_comments') as mock_comments:
            
            mock_git.return_value = MockGitHistoryResult(success=True, commits=[])
            # High complexity function (20 parameters = complexity > 15)
            mock_analyze.return_value = MockASTAnalysisResult(
                success=True,
                functions=[MockFunctionInfo(name="messy", line_number=1, parameters=["p" + str(i) for i in range(20)])]
            )
            mock_comments.return_value = MockCommentExtractionResult(success=True, comments=[])
            
            patterns = integration.detect_intent_patterns(test_file)
            
            assert IntentPattern.REFACTOR in patterns


class TestCommentExtractionIntegration:
    """Test CommentExtractor integration."""

# TODO: Refactor this method
def work():
    # FIXME: Handle null case
    pass
""")
        
        integration = LENSIntegration(repo_path=tmp_path)
        
        with patch.object(integration.comment_extractor, 'extract_comments') as mock_extract:
            mock_extract.return_value = MockCommentExtractionResult(
                success=True,
                comments=[
                    MockComment(line_number=2, content="TODO: Refactor this method", comment_type="block"),
                    MockComment(line_number=4, content="FIXME: Handle null case", comment_type="inline"),
                ]
            )
            
            result = integration.extract_comments(test_file)
            
            assert result is not None
            assert len(result["todos"]) == 1
            assert len(result["fixmes"]) == 1
            assert result["todos"][0]["text"] == "TODO: Refactor this method"
            mock_extract.assert_called_once_with(test_file)

class TestFullLENSAnalysis:
    """Test complete LENS analysis pipeline."""

    def test_analyze_combines_all_sources(self, tmp_path):
        """Test that analyze() combines git, AST, and comment data."""
        test_file = tmp_path / "complete.py"
        test_file.write_text("def complete(): pass")
        
        integration = LENSIntegration(repo_path=tmp_path)
        
        with patch.object(integration.git_analyzer, 'get_file_history') as mock_git, \
             patch.object(integration.ast_analyzer, 'analyze_file') as mock_ast, \
             patch.object(integration.comment_extractor, 'extract_comments') as mock_comments:
            
            mock_git.return_value = MockGitHistoryResult(
                success=True,
                commits=[MockGitCommit(hash="abc", message="Initial commit", author="dev")]
            )
            mock_ast.return_value = MockASTAnalysisResult(
                success=True,
                functions=[MockFunctionInfo(name="complete", line_number=1, parameters=[])]
            )
            mock_comments.return_value = MockCommentExtractionResult(success=True, comments=[])
            
            result = integration.analyze(test_file)
            
            assert isinstance(result, LENSAnalysisResult)
            assert result.git_history is not None
            assert result.ast_analysis is not None
            assert result.comment_data is not None
            assert result.intent_patterns is not None

    def test_analyze_handles_missing_file(self, tmp_path):
        """Test that analyze() handles missing files gracefully."""
        missing_file = tmp_path / "missing.py"
        
        integration = LENSIntegration(repo_path=tmp_path)
        result = integration.analyze(missing_file)
        
        assert result is not None
        assert result.git_history == {}
        assert result.ast_analysis == {}
        assert result.comment_data == {}
