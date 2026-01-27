"""
Unit tests for LENSOrchestrator.

Tests the unified LENS intelligence orchestrator that coordinates
GitHistoryAnalyzer, ASTAnalyzer, and CommentExtractor.

Authority: CORE-008 (TDD), LENS-003
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, patch

# Test will import once implemented:
# from cortex.orchestrators.support.lens_orchestrator import (
#     LENSOrchestrator,
#     LENSAnalysisResult,
#     LENSContext,
# )


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_git_analyzer() -> Mock:
    """Mock GitHistoryAnalyzer for testing."""
    mock = Mock()
    mock.get_file_history.return_value = Mock(
        success=True,
        commits=[
            Mock(hash="abc123", author="test", message="fix: bug", files_changed=["file.py"]),
            Mock(hash="def456", author="test", message="feat: feature", files_changed=["file.py"]),
        ],
        error="",
    )
    return mock


@pytest.fixture
def mock_ast_analyzer() -> Mock:
    """Mock ASTAnalyzer for testing."""
    mock = Mock()
    mock.analyze_file.return_value = Mock(
        success=True,
        functions=[Mock(name="func1", line_number=10)],
        classes=[Mock(name="Class1", line_number=20, methods=["method1"])],
        imports=[],
        error="",
    )
    return mock


@pytest.fixture
def mock_comment_extractor() -> Mock:
    """Mock CommentExtractor for testing."""
    mock = Mock()
    mock.extract_from_file.return_value = Mock(
        success=True,
        comments=[Mock(line_number=5, content="TODO: refactor", comment_type="block")],
        docstrings=[],
        error="",
    )
    return mock


@pytest.fixture
def test_file_path() -> Path:
    """Test file path."""
    return Path("/test/repo/src/module.py")


@pytest.fixture
def test_repo_path() -> Path:
    """Test repository path."""
    return Path("/test/repo")


# ============================================================================
# TEST: Initialization
# ============================================================================

def test_lens_orchestrator_initialization(test_repo_path: Path) -> None:
    """
    Test LENSOrchestrator can be initialized.
    
    Should create orchestrator with repo path and initialize analyzers.
    
    RED Phase: LENSOrchestrator class doesn't exist yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(repo_path=test_repo_path)
    
    assert orchestrator is not None
    assert orchestrator.repo_path == test_repo_path


def test_lens_orchestrator_accepts_custom_analyzers() -> None:
    """
    Test LENSOrchestrator accepts custom analyzer instances.
    
    Allows dependency injection for testing.
    
    RED Phase: Constructor doesn't accept analyzer parameters yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    mock_git = Mock()
    mock_ast = Mock()
    mock_comment = Mock()
    
    orchestrator = LENSOrchestrator(
        repo_path=Path("/test"),
        git_analyzer=mock_git,
        ast_analyzer=mock_ast,
        comment_extractor=mock_comment,
    )
    
    assert orchestrator.git_analyzer is mock_git
    assert orchestrator.ast_analyzer is mock_ast
    assert orchestrator.comment_extractor is mock_comment


# ============================================================================
# TEST: Unified Analysis
# ============================================================================

def test_analyze_file_returns_lens_context(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test analyze_file() coordinates all three analyzers.
    
    Should return unified LENSContext with git, ast, and comment data.
    
    RED Phase: analyze_file() method doesn't exist yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    result = orchestrator.analyze_file(test_file_path)
    
    assert result is not None
    # Should have git data (with either key name for backward compatibility)
    assert "git_history" in result or "git_analysis" in result
    assert "ast_analysis" in result
    assert "comment_analysis" in result


def test_analyze_file_calls_all_analyzers(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test analyze_file() invokes all three analyzers.
    
    Should call git_analyzer.get_file_history(), ast_analyzer.analyze_file(),
    and comment_extractor.extract_from_file().
    
    RED Phase: Analyzer methods not called yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    orchestrator.analyze_file(test_file_path)
    
    mock_git_analyzer.get_file_history.assert_called_once()
    mock_ast_analyzer.analyze_file.assert_called_once_with(test_file_path)
    mock_comment_extractor.extract_from_file.assert_called_once_with(test_file_path)


def test_analyze_file_formats_for_intent_router(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test analyze_file() output is compatible with IntentRouter.
    
    Should return dict with git_analysis, ast_analysis, comment_analysis keys
    matching the format expected by IntentRouter LENS-002 integration.
    
    RED Phase: Output format not standardized yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    result = orchestrator.analyze_file(test_file_path)
    
    # Check IntentRouter-compatible format
    assert "git_analysis" in result or "git_history" in result
    assert "ast_analysis" in result
    assert "comment_analysis" in result
    
    # Git data should have commits
    git_data = result.get("git_analysis") or result.get("git_history")
    assert "commits" in git_data or "recent_commits" in git_data
    
    # AST data should have functions/classes
    ast_data = result["ast_analysis"]
    assert "functions" in ast_data or "function_count" in ast_data
    assert "classes" in ast_data or "class_count" in ast_data
    
    # Comment data should have todos
    comment_data = result["comment_analysis"]
    assert "todos" in comment_data or "comments" in comment_data


# ============================================================================
# TEST: Caching
# ============================================================================

def test_analyze_file_caches_results(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test analyze_file() caches results for repeated calls.
    
    Second call to same file should return cached result without
    calling analyzers again.
    
    RED Phase: No caching mechanism exists yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    # First call
    result1 = orchestrator.analyze_file(test_file_path)
    
    # Second call (should use cache)
    result2 = orchestrator.analyze_file(test_file_path)
    
    # Analyzers should only be called once
    assert mock_git_analyzer.get_file_history.call_count == 1
    assert mock_ast_analyzer.analyze_file.call_count == 1
    assert mock_comment_extractor.extract_from_file.call_count == 1
    
    # Results should be identical
    assert result1 == result2


def test_cache_can_be_cleared(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test cache can be explicitly cleared.
    
    After clearing cache, next analyze_file() should call analyzers again.
    
    RED Phase: No clear_cache() method exists yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    # First call
    orchestrator.analyze_file(test_file_path)
    
    # Clear cache
    orchestrator.clear_cache()
    
    # Second call (should re-analyze)
    orchestrator.analyze_file(test_file_path)
    
    # Analyzers should be called twice
    assert mock_git_analyzer.get_file_history.call_count == 2
    assert mock_ast_analyzer.analyze_file.call_count == 2
    assert mock_comment_extractor.extract_from_file.call_count == 2


# ============================================================================
# TEST: Batch Analysis
# ============================================================================

def test_analyze_batch_processes_multiple_files(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_repo_path: Path,
) -> None:
    """
    Test analyze_batch() processes multiple files efficiently.
    
    Should analyze multiple files and return dict mapping paths to contexts.
    
    RED Phase: analyze_batch() method doesn't exist yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    file_paths = [
        Path("/test/repo/file1.py"),
        Path("/test/repo/file2.py"),
        Path("/test/repo/file3.py"),
    ]
    
    results = orchestrator.analyze_batch(file_paths)
    
    assert len(results) == 3
    assert all(path in results for path in file_paths)
    assert all("git_analysis" in ctx or "git_history" in ctx for ctx in results.values())


# ============================================================================
# TEST: Error Handling
# ============================================================================

def test_handles_git_analyzer_failure(
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test graceful handling of git analyzer failures.
    
    Should continue with AST and comment analysis even if git fails.
    
    RED Phase: No error handling exists yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    # Mock git analyzer that fails
    mock_git = Mock()
    mock_git.get_file_history.return_value = Mock(success=False, error="Git error")
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    result = orchestrator.analyze_file(test_file_path)
    
    # Should still have AST and comment data
    assert "ast_analysis" in result
    assert "comment_analysis" in result
    
    # Git data should indicate failure
    git_data = result.get("git_analysis") or result.get("git_history", {})
    assert git_data.get("error") or len(git_data.get("commits", [])) == 0


def test_handles_ast_analyzer_failure(
    mock_git_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test graceful handling of AST analyzer failures.
    
    Should continue with git and comment analysis even if AST fails.
    
    RED Phase: No error handling exists yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    # Mock AST analyzer that fails
    mock_ast = Mock()
    mock_ast.analyze_file.return_value = Mock(success=False, error="Parse error")
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast,
        comment_extractor=mock_comment_extractor,
    )
    
    result = orchestrator.analyze_file(test_file_path)
    
    # Should still have git and comment data
    assert "git_analysis" in result or "git_history" in result
    assert "comment_analysis" in result


# ============================================================================
# TEST: Integration with IntentRouter
# ============================================================================

def test_output_directly_usable_by_intent_router(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test LENSOrchestrator output can be passed directly to IntentRouter.
    
    Output should be compatible with IntentRouter's lens_context parameter.
    
    RED Phase: Format compatibility not guaranteed yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    from cortex.orchestrators.core.intent_router import IntentRouter
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    lens_context = orchestrator.analyze_file(test_file_path)
    
    # Should be usable with IntentRouter
    router = IntentRouter()
    context = {
        "operation": "refactor_code",
        "keywords": ["refactor"],
        "lens_context": lens_context  # Direct usage
    }
    
    decision = router.route(context)
    
    # Should have LENS enhancement
    assert decision.metadata.get("lens_enhanced") is True


# ============================================================================
# TEST: Performance & Metrics
# ============================================================================

def test_tracks_analysis_time(
    mock_git_analyzer: Mock,
    mock_ast_analyzer: Mock,
    mock_comment_extractor: Mock,
    test_file_path: Path,
    test_repo_path: Path,
) -> None:
    """
    Test analysis time is tracked in result metadata.
    
    Should include timing information for performance monitoring.
    
    RED Phase: No timing tracking exists yet.
    """
    from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
    
    orchestrator = LENSOrchestrator(
        repo_path=test_repo_path,
        git_analyzer=mock_git_analyzer,
        ast_analyzer=mock_ast_analyzer,
        comment_extractor=mock_comment_extractor,
    )
    
    result = orchestrator.analyze_file(test_file_path)
    
    # Should have metadata with timing
    metadata = result.get("_metadata", {})
    assert "analysis_time_ms" in metadata or "duration_ms" in metadata
