"""
Unit tests for Tool Adapter Pattern.

Tests unified tool interface for MCP/Copilot/Development environments
with proper error handling and result formatting.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 specification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cortex.brain.core.tool_adapter import (
    IToolAdapter,
    MCPToolAdapter,
    CopilotToolAdapter,
    DevelopmentToolAdapter,
    AnalysisResult,
    SearchResult,
    DuplicateResult,
    GitHistoryResult,
    ToolError,
    ToolUnavailableError,
)


class TestResultDataclasses:
    """Test result dataclass structures."""
    
    def test_analysis_result_creation(self):
        """Test AnalysisResult can be created."""
        result = AnalysisResult(
            target_path="/test/path",
            issues=[{"type": "error", "message": "test"}],
            metrics={"loc": 100},
            success=True
        )
        
        assert result.target_path == "/test/path"
        assert len(result.issues) == 1
        assert result.success is True
        assert result.error is None
    
    def test_search_result_creation(self):
        """Test SearchResult can be created."""
        result = SearchResult(
            query="test query",
            matches=[{"file": "test.py", "line": 10}],
            total_count=1,
            success=True
        )
        
        assert result.query == "test query"
        assert result.total_count == 1
        assert result.success is True
    
    def test_duplicate_result_creation(self):
        """Test DuplicateResult can be created."""
        result = DuplicateResult(
            scope="cortex/",
            duplicates=[{"file1": "a.py", "file2": "b.py"}],
            success=True
        )
        
        assert result.scope == "cortex/"
        assert len(result.duplicates) == 1
        assert result.success is True
    
    def test_git_history_result_creation(self):
        """Test GitHistoryResult can be created."""
        result = GitHistoryResult(
            lookback_hours=24,
            commits=[{"hash": "abc123", "message": "test"}],
            success=True
        )
        
        assert result.lookback_hours == 24
        assert len(result.commits) == 1
        assert result.success is True


class TestMCPToolAdapter:
    """Test MCP tool adapter for production environment."""
    
    @pytest.fixture
    def adapter(self):
        """Create MCP adapter instance."""
        return MCPToolAdapter()
    
    def test_adapter_implements_interface(self, adapter):
        """Test that MCPToolAdapter implements IToolAdapter."""
        assert isinstance(adapter, IToolAdapter)
    
    def test_analyze_code_success(self, adapter):
        """Test code analysis with MCP tools."""
        result = adapter.analyze_code("cortex/")
        
        assert isinstance(result, AnalysisResult)
        assert result.success is True
        assert result.target_path == "cortex/"
    
    def test_search_workspace_success(self, adapter):
        """Test workspace search with MCP tools."""
        result = adapter.search_workspace("test query")
        
        assert isinstance(result, SearchResult)
        assert result.success is True
        assert result.query == "test query"
    
    def test_detect_duplicates_success(self, adapter):
        """Test duplicate detection with MCP tools."""
        result = adapter.detect_duplicates("cortex/")
        
        assert isinstance(result, DuplicateResult)
        assert result.success is True
        assert result.scope == "cortex/"
    
    def test_git_history_success(self, adapter):
        """Test git history with MCP tools."""
        result = adapter.get_git_history(lookback_hours=24)
        
        assert isinstance(result, GitHistoryResult)
        assert result.success is True
        assert result.lookback_hours == 24
    
    def test_is_available_returns_bool(self, adapter):
        """Test is_available method."""
        result = adapter.is_available("cortex_lens_analyze")
        assert isinstance(result, bool)


class TestCopilotToolAdapter:
    """Test Copilot tool adapter for VS Code environment."""
    
    @pytest.fixture
    def adapter(self):
        """Create Copilot adapter instance."""
        return CopilotToolAdapter()
    
    def test_adapter_implements_interface(self, adapter):
        """Test that CopilotToolAdapter implements IToolAdapter."""
        assert isinstance(adapter, IToolAdapter)
    
    def test_analyze_code_uses_vscode_tools(self, adapter):
        """Test code analysis uses VS Code tools."""
        result = adapter.analyze_code("cortex/")
        
        assert isinstance(result, AnalysisResult)
        assert result.target_path == "cortex/"
        assert result.success is True
    
    def test_search_workspace_uses_vscode_search(self, adapter):
        """Test workspace search uses VS Code search."""
        result = adapter.search_workspace("test query")
        
        assert isinstance(result, SearchResult)
        assert result.query == "test query"
        assert result.success is True
    
    def test_detect_duplicates_fallback(self, adapter):
        """Test duplicate detection with fallback implementation."""
        result = adapter.detect_duplicates("cortex/")
        
        assert isinstance(result, DuplicateResult)
        assert result.success is True
    
    def test_git_history_uses_vscode_git(self, adapter):
        """Test git history uses VS Code git integration."""
        result = adapter.get_git_history(lookback_hours=24)
        
        assert isinstance(result, GitHistoryResult)
        assert result.success is True
    
    def test_is_available_returns_bool(self, adapter):
        """Test is_available method."""
        result = adapter.is_available("grep_search")
        assert isinstance(result, bool)


class TestDevelopmentToolAdapter:
    """Test Development tool adapter for local environment."""
    
    @pytest.fixture
    def adapter(self):
        """Create Development adapter instance."""
        return DevelopmentToolAdapter()
    
    def test_adapter_implements_interface(self, adapter):
        """Test that DevelopmentToolAdapter implements IToolAdapter."""
        assert isinstance(adapter, IToolAdapter)
    
    def test_analyze_code_local_implementation(self, adapter):
        """Test code analysis with local tools."""
        result = adapter.analyze_code("cortex/")
        
        assert isinstance(result, AnalysisResult)
        assert result.success is True
    
    def test_search_workspace_local_grep(self, adapter):
        """Test workspace search with local grep."""
        result = adapter.search_workspace("test query")
        
        assert isinstance(result, SearchResult)
        assert result.success is True
    
    def test_detect_duplicates_local_analysis(self, adapter):
        """Test duplicate detection with local analysis."""
        result = adapter.detect_duplicates("cortex/")
        
        assert isinstance(result, DuplicateResult)
        assert result.success is True
    
    def test_git_history_local_git_command(self, adapter):
        """Test git history with local git commands."""
        result = adapter.get_git_history(lookback_hours=24)
        
        assert isinstance(result, GitHistoryResult)
        assert result.success is True
    
    def test_is_available_returns_bool(self, adapter):
        """Test is_available method."""
        result = adapter.is_available("git")
        assert isinstance(result, bool)


class TestToolAdapterErrorHandling:
    """Test error handling across all adapters."""
    
    def test_tool_error_inheritance(self):
        """Test ToolError is base exception."""
        assert issubclass(ToolUnavailableError, ToolError)
        assert issubclass(ToolError, Exception)
    
    def test_analysis_result_with_error(self):
        """Test AnalysisResult can capture errors."""
        result = AnalysisResult(
            target_path="/test",
            issues=[],
            metrics={},
            success=False,
            error="Tool unavailable"
        )
        
        assert result.success is False
        assert result.error == "Tool unavailable"
    
    def test_search_result_with_error(self):
        """Test SearchResult can capture errors."""
        result = SearchResult(
            query="test",
            matches=[],
            total_count=0,
            success=False,
            error="Search failed"
        )
        
        assert result.success is False
        assert result.error == "Search failed"
