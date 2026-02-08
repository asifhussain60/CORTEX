"""
Unit Tests for EnvironmentIntegrityAgent - Phase 51 Stage 2

Tests environment validation and MCP availability detection.

AC-ID: PHASE-51-S2-001
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import os
import socket

from cortex.governance.enforcement.agents.environment_integrity_agent import (
    EnvironmentIntegrityAgent,
    ValidationResult,
    MCPAvailability,
)
from cortex.models.canonical_enums import IntentType


@pytest.fixture
def agent():
    """Create EnvironmentIntegrityAgent instance."""
    return EnvironmentIntegrityAgent()


class TestInitialization:
    """Test EnvironmentIntegrityAgent initialization."""
    
    def test_agent_initialization(self):
        """Test agent initializes correctly."""
        agent = EnvironmentIntegrityAgent()
        
        assert agent is not None
        assert hasattr(agent, 'validate_pre_flight')
        assert hasattr(agent, 'check_mcp_availability')


class TestMCPAvailabilityDetection:
    """Test MCP availability detection methods."""
    
    def test_check_mcp_tool_available(self, agent):
        """Test MCP detection via tool availability."""
        with patch.object(agent, '_check_tool_exists', return_value=True):
            result = agent.check_mcp_availability()
            
            assert result.available is True
            assert result.detection_method == 'tool_query'
    
    def test_check_mcp_env_vars(self, agent):
        """Test MCP detection via environment variables."""
        with patch.object(agent, '_check_tool_exists', return_value=False), \
             patch.dict(os.environ, {'MCP_SERVER_PORT': '8000'}):
            
            result = agent.check_mcp_availability()
            
            assert result.available is True
            assert result.detection_method == 'environment_variables'
    
    def test_check_mcp_network_port(self, agent):
        """Test MCP detection via network port check."""
        with patch.object(agent, '_check_tool_exists', return_value=False), \
             patch.dict(os.environ, {}, clear=True), \
             patch.object(agent, '_check_port_open', return_value=True):
            
            result = agent.check_mcp_availability()
            
            assert result.available is True
            assert result.detection_method == 'network_port'
    
    def test_mcp_unavailable_all_methods(self, agent):
        """Test MCP unavailable when all detection methods fail."""
        with patch.object(agent, '_check_tool_exists', return_value=False), \
             patch.dict(os.environ, {}, clear=True), \
             patch.object(agent, '_check_port_open', return_value=False):
            
            result = agent.check_mcp_availability()
            
            assert result.available is False
            assert result.detection_method == 'none'


class TestPreFlightValidation:
    """Test pre-flight validation for different intents."""
    
    def test_implement_intent_blocks_when_mcp_unavailable(self, agent):
        """Test IMPLEMENT intent blocked when MCP unavailable."""
        with patch.object(agent, 'check_mcp_availability', return_value=MCPAvailability(False, 'none')):
            
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            assert result.passed is False
            assert result.severity == 'CRITICAL'
            assert 'MCP' in result.reason
            assert 'BLOCKED' in result.action
    
    def test_fix_intent_blocks_when_mcp_unavailable(self, agent):
        """Test FIX intent blocked when MCP unavailable."""
        with patch.object(agent, 'check_mcp_availability', return_value=MCPAvailability(False, 'none')):
            
            result = agent.validate_pre_flight(IntentType.FIX)
            
            assert result.passed is False
            assert result.severity == 'CRITICAL'
            assert 'MCP' in result.reason
    
    def test_refactor_intent_blocks_when_mcp_unavailable(self, agent):
        """Test REFACTOR intent blocked when MCP unavailable."""
        with patch.object(agent, 'check_mcp_availability', return_value=MCPAvailability(False, 'none')):
            
            result = agent.validate_pre_flight(IntentType.REFACTOR)
            
            assert result.passed is False
            assert result.severity == 'CRITICAL'
            assert 'MCP' in result.reason
    
    def test_analyze_intent_allows_when_mcp_unavailable(self, agent):
        """Test ANALYZE intent allowed even when MCP unavailable (read-only)."""
        with patch.object(agent, 'check_mcp_availability', return_value=MCPAvailability(False, 'none')):
            
            result = agent.validate_pre_flight(IntentType.ANALYZE)
            
            assert result.passed is True  # Read-only operations OK
    
    def test_implement_intent_passes_with_mcp(self, agent):
        """Test IMPLEMENT intent passes when MCP available."""
        with patch.object(agent, 'check_mcp_availability', return_value=MCPAvailability(True, 'tool_query')):
            
            result = agent.validate_pre_flight(IntentType.IMPLEMENT)
            
            assert result.passed is True
            assert result.severity == 'PASSED'


class TestPythonDependencyCheck:
    """Test Python dependency verification."""
    
    def test_check_python_dependencies_all_present(self, agent):
        """Test dependency check passes when all present."""
        result = agent.check_python_dependencies(['pytest', 'yaml'])
        
        assert result.passed is True
        assert len(result.missing_packages) == 0
    
    def test_check_python_dependencies_missing(self, agent):
        """Test dependency check fails when packages missing."""
        result = agent.check_python_dependencies(['nonexistent_package_12345'])
        
        assert result.passed is False
        assert len(result.missing_packages) > 0
        assert 'nonexistent_package_12345' in result.missing_packages


class TestGitStateValidation:
    """Test git clean state validation."""
    
    def test_git_clean_state_passes(self, agent):
        """Test git state check passes when clean."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='')
            
            result = agent.check_git_clean_state()
            
            assert result.passed is True
    
    def test_git_dirty_state_warns(self, agent):
        """Test git state check warns when dirty."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='M file.py\n')
            
            result = agent.check_git_clean_state()
            
            assert result.passed is False
            assert result.severity == 'WARNING'


class TestIntegration:
    """Test EnvironmentIntegrityAgent integration with EnforcementOrchestrator."""
    
    def test_integration_with_enforcement_orchestrator(self, agent):
        """Test agent can be integrated into EnforcementOrchestrator."""
        # Verify agent has required interface
        assert hasattr(agent, 'validate_pre_flight')
        assert callable(agent.validate_pre_flight)
        
        # Verify ValidationResult structure
        result = agent.validate_pre_flight(IntentType.IMPLEMENT)
        assert hasattr(result, 'passed')
        assert hasattr(result, 'severity')
        assert hasattr(result, 'reason')
        assert hasattr(result, 'action')
