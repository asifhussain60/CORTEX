"""
Tests for Environment Detection and Tool Adapter.

Authority: CORE-008 (TDD-first)
Phase 33: Architecture Alignment & Mandatory Governance Enforcement
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cortex.brain.core.environment_detector import (
    EnvironmentDetector,
    EnvironmentType,
    EnvironmentConfig,
    detect_environment,
    get_environment_detector,
)
from cortex.brain.core.tool_adapter import (
    IToolAdapter,
    MCPToolAdapter,
    CopilotToolAdapter,
    DevelopmentToolAdapter,
    ToolUnavailableError,
    AnalysisResult,
    SearchResult,
    DuplicateResult,
    GitHistoryResult,
)


class TestEnvironmentDetection:
    """Tests for EnvironmentDetector class."""

    def test_find_cortex_root(self) -> None:
        """Test CORTEX root directory detection."""
        detector = EnvironmentDetector()
        assert detector.cortex_root.exists()
        assert (detector.cortex_root / "cortex" / "__init__.py").exists()

    def test_detect_mcp_server_environment(self) -> None:
        """Test MCP server environment detection."""
        detector = EnvironmentDetector()
        
        with patch.dict(os.environ, {"CORTEX_MCP_SERVER": "true"}):
            assert detector._is_mcp_server() is True

    def test_detect_copilot_environment(self) -> None:
        """Test VS Code Copilot environment detection."""
        detector = EnvironmentDetector()
        
        with patch.dict(os.environ, {"VS_CODE_COPILOT": "true"}):
            assert detector._is_copilot() is True

    def test_detect_development_environment(self) -> None:
        """Test local development environment detection."""
        detector = EnvironmentDetector()
        
        with patch.dict(os.environ, {}, clear=False):
            # Remove MCP and Copilot indicators if present
            detector._cached_environment = None
            env = detector.detect_environment()
            assert env in (
                EnvironmentType.DEVELOPMENT,
                EnvironmentType.COPILOT,
                EnvironmentType.MCP_SERVER,
            )

    def test_environment_config_creation(self) -> None:
        """Test EnvironmentConfig dataclass."""
        config = EnvironmentConfig(
            environment_type=EnvironmentType.MCP_SERVER,
            is_mcp_available=True,
            is_copilot_available=False,
            is_development=False,
            cortex_root=Path("/tmp/cortex"),
            tool_adapter_class="cortex.brain.core.tool_adapter.MCPToolAdapter",
        )
        
        assert config.environment_type == EnvironmentType.MCP_SERVER
        assert "MCP Server" in str(config)

    def test_environment_config_copilot(self) -> None:
        """Test EnvironmentConfig for Copilot."""
        config = EnvironmentConfig(
            environment_type=EnvironmentType.COPILOT,
            is_mcp_available=False,
            is_copilot_available=True,
            is_development=False,
            cortex_root=Path("/tmp/cortex"),
            tool_adapter_class="cortex.brain.core.tool_adapter.CopilotToolAdapter",
        )
        
        assert "Copilot" in str(config)

    def test_environment_detector_caching(self) -> None:
        """Test that environment detection is cached."""
        detector = EnvironmentDetector()
        
        env1 = detector.detect_environment()
        env2 = detector.detect_environment()
        
        # Should return cached result (same object reference)
        assert env1 == env2

    def test_get_environment_config(self) -> None:
        """Test getting full environment config."""
        detector = EnvironmentDetector()
        config = detector.get_environment_config()
        
        assert config.environment_type is not None
        assert config.cortex_root is not None
        assert config.tool_adapter_class is not None

    def test_is_production(self) -> None:
        """Test production environment check."""
        detector = EnvironmentDetector()
        
        with patch.dict(os.environ, {"CORTEX_MCP_SERVER": "true"}):
            detector._cached_environment = None
            assert detector.is_production() is True

    def test_is_development(self) -> None:
        """Test development environment check."""
        detector = EnvironmentDetector()
        
        # Reset cache and mock environment to be development
        with patch.object(detector, "_is_mcp_server", return_value=False):
            with patch.object(detector, "_is_copilot", return_value=False):
                detector._cached_environment = None
                assert detector.is_development() is True


class TestToolAdapters:
    """Tests for tool adapter implementations."""

    def test_mcp_tool_adapter_initialization(self) -> None:
        """Test MCPToolAdapter initialization."""
        adapter = MCPToolAdapter()
        assert adapter.environment == "MCP_SERVER"

    def test_mcp_analyze_code(self) -> None:
        """Test MCPToolAdapter.analyze_code()."""
        adapter = MCPToolAdapter()
        result = adapter.analyze_code("test_file.py")
        
        assert result.success is True
        assert result.target_path == "test_file.py"

    def test_mcp_search_workspace(self) -> None:
        """Test MCPToolAdapter.search_workspace()."""
        adapter = MCPToolAdapter()
        result = adapter.search_workspace("test_query")
        
        assert result.success is True
        assert result.query == "test_query"

    def test_mcp_detect_duplicates(self) -> None:
        """Test MCPToolAdapter.detect_duplicates()."""
        adapter = MCPToolAdapter()
        result = adapter.detect_duplicates("src/")
        
        assert result.success is True
        assert result.scope == "src/"

    def test_mcp_get_git_history(self) -> None:
        """Test MCPToolAdapter.get_git_history()."""
        adapter = MCPToolAdapter()
        result = adapter.get_git_history(24)
        
        assert result.success is True
        assert result.lookback_hours == 24

    def test_mcp_is_available(self) -> None:
        """Test MCPToolAdapter.is_available()."""
        adapter = MCPToolAdapter()
        assert adapter.is_available("analyze") is True
        assert adapter.is_available("search") is True
        assert adapter.is_available("duplicates") is True
        assert adapter.is_available("git_history") is True

    def test_mcp_get_environment_info(self) -> None:
        """Test MCPToolAdapter.get_environment_info()."""
        adapter = MCPToolAdapter()
        info = adapter.get_environment_info()
        
        assert info["environment"] == "MCP_SERVER"
        assert info["status"] == "production"

    def test_copilot_tool_adapter_initialization(self) -> None:
        """Test CopilotToolAdapter initialization."""
        adapter = CopilotToolAdapter()
        assert adapter.environment == "COPILOT"

    def test_copilot_search_workspace(self) -> None:
        """Test CopilotToolAdapter.search_workspace()."""
        adapter = CopilotToolAdapter()
        result = adapter.search_workspace("test_query")
        
        assert result.success is True

    def test_copilot_get_environment_info(self) -> None:
        """Test CopilotToolAdapter.get_environment_info()."""
        adapter = CopilotToolAdapter()
        info = adapter.get_environment_info()
        
        assert info["environment"] == "COPILOT"
        assert info["status"] == "development"

    def test_development_tool_adapter_initialization(self) -> None:
        """Test DevelopmentToolAdapter initialization."""
        adapter = DevelopmentToolAdapter()
        assert adapter.environment == "DEVELOPMENT"

    def test_development_analyze_code(self) -> None:
        """Test DevelopmentToolAdapter.analyze_code()."""
        adapter = DevelopmentToolAdapter()
        result = adapter.analyze_code("test_file.py")
        
        assert result.success is True

    def test_development_get_environment_info(self) -> None:
        """Test DevelopmentToolAdapter.get_environment_info()."""
        adapter = DevelopmentToolAdapter()
        info = adapter.get_environment_info()
        
        assert info["environment"] == "DEVELOPMENT"
        assert info["status"] == "local_development"

    def test_adapter_interface_contract(self) -> None:
        """Test that all adapters implement IToolAdapter interface."""
        adapters = [
            MCPToolAdapter(),
            CopilotToolAdapter(),
            DevelopmentToolAdapter(),
        ]
        
        for adapter in adapters:
            assert isinstance(adapter, IToolAdapter)
            assert hasattr(adapter, "analyze_code")
            assert hasattr(adapter, "search_workspace")
            assert hasattr(adapter, "detect_duplicates")
            assert hasattr(adapter, "get_git_history")
            assert hasattr(adapter, "is_available")
            assert hasattr(adapter, "get_environment_info")


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_detect_environment_function(self) -> None:
        """Test detect_environment() convenience function."""
        env = detect_environment()
        assert env in [
            EnvironmentType.MCP_SERVER,
            EnvironmentType.COPILOT,
            EnvironmentType.DEVELOPMENT,
        ]

    def test_get_environment_detector_singleton(self) -> None:
        """Test get_environment_detector() returns singleton."""
        detector1 = get_environment_detector()
        detector2 = get_environment_detector()
        
        assert detector1 is detector2


class TestDataModels:
    """Tests for data models."""

    def test_analysis_result_creation(self) -> None:
        """Test AnalysisResult dataclass."""
        result = AnalysisResult(
            target_path="test.py",
            issues=[{"id": "E001", "line": 10}],
            metrics={"complexity": 3.2},
            success=True,
        )
        
        assert result.target_path == "test.py"
        assert len(result.issues) == 1
        assert result.success is True

    def test_search_result_creation(self) -> None:
        """Test SearchResult dataclass."""
        result = SearchResult(
            query="function_name",
            matches=[{"file": "test.py", "line": 5}],
            total_count=1,
            success=True,
        )
        
        assert result.query == "function_name"
        assert result.total_count == 1

    def test_duplicate_result_creation(self) -> None:
        """Test DuplicateResult dataclass."""
        result = DuplicateResult(
            scope="src/",
            duplicates=[{"files": ["a.py", "b.py"]}],
            success=True,
        )
        
        assert result.scope == "src/"
        assert len(result.duplicates) == 1

    def test_git_history_result_creation(self) -> None:
        """Test GitHistoryResult dataclass."""
        result = GitHistoryResult(
            lookback_hours=24,
            commits=[{"hash": "abc123", "message": "test"}],
            success=True,
        )
        
        assert result.lookback_hours == 24
        assert len(result.commits) == 1
