"""
Unit tests for EnvironmentDetector.

Tests environment detection logic for MCP/Copilot/Development modes
and configuration of appropriate tool adapters.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 specification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from pathlib import Path

from cortex.brain.core.environment_detector import (
    EnvironmentType,
    EnvironmentDetector,
    EnvironmentConfig,
)


class TestEnvironmentType:
    """Test EnvironmentType enum."""
    
    def test_environment_types_defined(self):
        """Test that all environment types are defined."""
        assert EnvironmentType.MCP_SERVER
        assert EnvironmentType.COPILOT
        assert EnvironmentType.DEVELOPMENT
        
        # Should have exactly 3 types
        types = list(EnvironmentType)
        assert len(types) == 3


class TestEnvironmentDetector:
    """Test environment detection logic."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance with cleared cache."""
        det = EnvironmentDetector()
        det._cached_environment = None  # Clear cache
        return det
    
    def test_detect_mcp_environment(self, detector):
        """Test detection of MCP server environment."""
        with patch.dict(os.environ, {'CORTEX_MCP_SERVER': 'true'}, clear=True):
            with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=True):
                env_type = detector.detect_environment()
                assert env_type == EnvironmentType.MCP_SERVER
    
    def test_detect_copilot_environment(self, detector):
        """Test detection of Copilot environment."""
        with patch.dict(os.environ, {'TERM_PROGRAM': 'vscode'}, clear=True):
            with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=False):
                with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_copilot', return_value=True):
                    detector._cached_environment = None  # Clear cache
                    env_type = detector.detect_environment()
                    assert env_type == EnvironmentType.COPILOT
    
    def test_detect_development_environment(self, detector):
        """Test detection of development environment (default)."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=False):
                with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_copilot', return_value=False):
                    detector._cached_environment = None  # Clear cache
                    env_type = detector.detect_environment()
                    assert env_type == EnvironmentType.DEVELOPMENT
    
    def test_is_mcp_available_when_true(self, detector):
        """Test MCP availability detection when true."""
        with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=True):
            assert detector.is_mcp_available() is True
    
    def test_is_mcp_available_when_false(self, detector):
        """Test MCP availability detection when false."""
        with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=False):
            assert detector.is_mcp_available() is False
    
    def test_is_copilot_available_when_true(self, detector):
        """Test Copilot availability detection when true."""
        with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_copilot', return_value=True):
            assert detector.is_copilot_available() is True
    
    def test_is_copilot_available_when_false(self, detector):
        """Test Copilot availability detection when false."""
        with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_copilot', return_value=False):
            assert detector.is_copilot_available() is False
    
    def test_get_environment_config_mcp(self, detector):
        """Test environment config generation for MCP."""
        with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=True):
            with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_copilot', return_value=False):
                detector._cached_environment = None
                config = detector.get_environment_config()
                
                assert isinstance(config, EnvironmentConfig)
                assert config.environment_type == EnvironmentType.MCP_SERVER
                assert config.is_mcp_available is True
                assert "MCPToolAdapter" in config.tool_adapter_class
    
    def test_get_environment_config_copilot(self, detector):
        """Test environment config generation for Copilot."""
        with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=False):
            with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_copilot', return_value=True):
                detector._cached_environment = None
                config = detector.get_environment_config()
                
                assert config.environment_type == EnvironmentType.COPILOT
                assert config.is_copilot_available is True
                assert "CopilotToolAdapter" in config.tool_adapter_class
    
    def test_get_environment_config_development(self, detector):
        """Test environment config generation for development."""
        with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_mcp_server', return_value=False):
            with patch('cortex.brain.core.environment_detector.EnvironmentDetector._is_copilot', return_value=False):
                detector._cached_environment = None
                config = detector.get_environment_config()
                
                assert config.environment_type == EnvironmentType.DEVELOPMENT
                assert "DevelopmentToolAdapter" in config.tool_adapter_class


class TestEnvironmentConfig:
    """Test EnvironmentConfig dataclass."""
    
    def test_config_creation(self):
        """Test EnvironmentConfig can be created."""
        config = EnvironmentConfig(
            environment_type=EnvironmentType.MCP_SERVER,
            is_mcp_available=True,
            is_copilot_available=False,
            is_development=False,
            cortex_root=Path("/test/path"),
            tool_adapter_class="cortex.brain.core.tool_adapter.MCPToolAdapter"
        )
        
        assert config.environment_type == EnvironmentType.MCP_SERVER
        assert config.is_mcp_available is True
        assert config.is_copilot_available is False
        assert "MCPToolAdapter" in config.tool_adapter_class
    
    def test_config_to_dict(self):
        """Test EnvironmentConfig can be converted to dict."""
        config = EnvironmentConfig(
            environment_type=EnvironmentType.COPILOT,
            is_mcp_available=False,
            is_copilot_available=True,
            is_development=False,
            cortex_root=Path("/test/path"),
            tool_adapter_class="cortex.brain.core.tool_adapter.CopilotToolAdapter"
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["environment_type"] == "copilot"
        assert config_dict["adapter_type"] == "CopilotToolAdapter"
