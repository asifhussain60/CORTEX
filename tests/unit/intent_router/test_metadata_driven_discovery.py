# AC_START: AC-PHASE81-S3-P4-002
"""
Tests for Metadata-Driven MCP Tool Discovery

Tests metadata parser integration, tool mapping, and executor registration.

Module: tests/unit/intent_router/test_metadata_driven_discovery.py
Authority: Phase 81 S3 Part 4 - Metadata Parser Integration
Version: 1.0
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from typing import Dict, List, Any

from cortex.intent_router.metadata_driven_discovery import (
    MetadataDrivenDiscovery,
    AgentToolMapping
)
from cortex.intent_router.mcp_executor import MCPToolExecutor
from cortex.agents.metadata_parser import AgentMetadata


class TestAgentToolMapping:
    """Test AgentToolMapping dataclass."""
    
    @pytest.fixture
    def sample_metadata(self):
        """Create sample agent metadata."""
        return AgentMetadata(
            agent_id="cortex-test-agent",
            version="1.0",
            status="active",
            layer="core",
            capabilities=["test_capability"],
            modes_served=["TEST"],
            mcp_tools=["cortex_test_tool1", "cortex_test_tool2"],
            priority="P1",
            token_cost_estimate=2000
        )
    
    def test_mapping_creation(self, sample_metadata):
        """Test AgentToolMapping creation."""
        mapping = AgentToolMapping(
            agent_id="cortex-test",
            agent_metadata=sample_metadata,
            mcp_tools=["tool1", "tool2"]
        )
        
        assert mapping.agent_id == "cortex-test"
        assert mapping.agent_metadata == sample_metadata
        assert len(mapping.mcp_tools) == 2
    
    def test_get_primary_tool(self, sample_metadata):
        """Test getting primary tool from mapping."""
        mapping = AgentToolMapping(
            agent_id="cortex-test",
            agent_metadata=sample_metadata,
            mcp_tools=["tool_primary", "tool_secondary"]
        )
        
        assert mapping.get_primary_tool() == "tool_primary"
    
    def test_has_tool(self, sample_metadata):
        """Test checking tool presence."""
        mapping = AgentToolMapping(
            agent_id="cortex-test",
            agent_metadata=sample_metadata,
            mcp_tools=["tool1", "tool2"]
        )
        
        assert mapping.has_tool("tool1") is True
        assert mapping.has_tool("tool3") is False


class TestMetadataDrivenDiscovery:
    """Test MetadataDrivenDiscovery system."""
    
    @pytest.fixture
    def discovery(self):
        """Create discovery instance."""
        return MetadataDrivenDiscovery(agents_dir=".github/agents/core")
    
    @pytest.fixture
    def mock_metadata(self):
        """Create mock agent metadata."""
        return {
            "cortex-meta-auditor": AgentMetadata(
                agent_id="cortex-meta-auditor",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["governance_validation", "audit"],
                modes_served=["META-AUDIT"],
                mcp_tools=["cortex_meta_audit", "cortex_validate_governance"],
                priority="P0",
                token_cost_estimate=3000
            ),
            "cortex-auditor": AgentMetadata(
                agent_id="cortex-auditor",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["code_audit", "security_check"],
                modes_served=["AUDIT"],
                mcp_tools=["cortex_audit_codebase", "cortex_scan_security"],
                priority="P1",
                token_cost_estimate=2500
            )
        }
    
    def test_discovery_initialization(self, discovery):
        """Test discovery initialization."""
        assert discovery.parser is not None
        assert not discovery._is_initialized
        assert len(discovery._agent_tool_map) == 0
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_initialize_loads_metadata(self, mock_load, discovery, mock_metadata):
        """Test initialization loads agent metadata."""
        mock_load.return_value = mock_metadata
        
        discovery.initialize()
        
        assert discovery._is_initialized is True
        assert len(discovery._agent_tool_map) == 2
        assert "cortex-meta-auditor" in discovery._agent_tool_map
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_get_agent_tools(self, mock_load, discovery, mock_metadata):
        """Test getting tools for specific agent."""
        mock_load.return_value = mock_metadata
        discovery.initialize()
        
        tools = discovery.get_agent_tools("cortex-meta-auditor")
        
        assert len(tools) == 2
        assert "cortex_meta_audit" in tools
        assert "cortex_validate_governance" in tools
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_get_primary_tool(self, mock_load, discovery, mock_metadata):
        """Test getting primary tool for agent."""
        mock_load.return_value = mock_metadata
        discovery.initialize()
        
        primary = discovery.get_primary_tool("cortex-meta-auditor")
        
        assert primary == "cortex_meta_audit"
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_get_agents_by_tool(self, mock_load, discovery, mock_metadata):
        """Test finding agents by tool name."""
        mock_load.return_value = mock_metadata
        discovery.initialize()
        
        agents = discovery.get_agents_by_tool("cortex_audit_codebase")
        
        assert len(agents) == 1
        assert "cortex-auditor" in agents
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_get_agents_by_capability(self, mock_load, discovery, mock_metadata):
        """Test finding agents by capability."""
        mock_load.return_value = mock_metadata
        discovery.initialize()
        
        agents = discovery.get_agents_by_capability("governance_validation")
        
        assert len(agents) == 1
        assert "cortex-meta-auditor" in agents
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_build_agent_tool_map(self, mock_load, discovery, mock_metadata):
        """Test building complete agent-tool mapping."""
        mock_load.return_value = mock_metadata
        discovery.initialize()
        
        map_result = discovery.build_agent_tool_map()
        
        assert len(map_result) == 2
        assert all(isinstance(v, AgentToolMapping) for v in map_result.values())
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_get_all_tools(self, mock_load, discovery, mock_metadata):
        """Test getting all unique tools."""
        mock_load.return_value = mock_metadata
        discovery.initialize()
        
        all_tools = discovery.get_all_tools()
        
        assert len(all_tools) == 4
        assert "cortex_meta_audit" in all_tools
        assert "cortex_audit_codebase" in all_tools
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_get_agent_metadata(self, mock_load, discovery, mock_metadata):
        """Test retrieving agent metadata."""
        mock_load.return_value = mock_metadata
        discovery.initialize()
        
        metadata = discovery.get_agent_metadata("cortex-meta-auditor")
        
        assert metadata is not None
        assert metadata.agent_id == "cortex-meta-auditor"
        assert metadata.priority == "P0"


class TestMetadataExecutorIntegration:
    """Test integration of metadata discovery with MCP executor."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        return MCPToolExecutor()
    
    @pytest.fixture
    def mock_metadata(self):
        """Create mock metadata."""
        return {
            "cortex-test-1": AgentMetadata(
                agent_id="cortex-test-1",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["test"],
                modes_served=["TEST"],
                mcp_tools=["cortex_test_1"],
                priority="P1",
                token_cost_estimate=2000
            ),
            "cortex-test-2": AgentMetadata(
                agent_id="cortex-test-2",
                version="1.0",
                status="active",
                layer="support",
                capabilities=["test"],
                modes_served=["TEST"],
                mcp_tools=["cortex_test_2a", "cortex_test_2b"],
                priority="P2",
                token_cost_estimate=2500
            )
        }
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_register_with_executor(self, mock_load, executor, mock_metadata):
        """Test registering agents with executor from metadata."""
        mock_load.return_value = mock_metadata
        
        registered = executor.initialize_from_metadata()
        
        assert registered == 2
        assert executor.get_agent_tools("cortex-test-1") == ["cortex_test_1"]
        assert executor.get_agent_tools("cortex-test-2") == ["cortex_test_2a", "cortex_test_2b"]
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_executor_has_discovery_reference(self, mock_load, executor, mock_metadata):
        """Test executor maintains reference to discovery."""
        mock_load.return_value = mock_metadata
        
        executor.initialize_from_metadata()
        
        assert executor._metadata_discovery is not None
        assert len(executor._metadata_discovery._agent_tool_map) == 2


class TestDiscoveryStatistics:
    """Test discovery statistics and reporting."""
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_get_discovery_statistics(self, mock_load):
        """Test gathering discovery statistics."""
        mock_metadata = {
            "cortex-test": AgentMetadata(
                agent_id="cortex-test",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["capability1", "capability2"],
                modes_served=["MODE1"],
                mcp_tools=["tool1", "tool2"],
                priority="P0",
                token_cost_estimate=2000
            )
        }
        
        mock_load.return_value = mock_metadata
        
        discovery = MetadataDrivenDiscovery()
        discovery.initialize()
        
        stats = discovery.get_discovery_statistics()
        
        assert stats["total_agents"] == 1
        assert stats["total_tools"] == 2
        assert stats["total_capabilities"] == 2
        assert stats["agents_by_layer"]["core"] == 1


class TestMetadataValidation:
    """Test metadata validation in discovery."""
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_validate_tools_consistency(self, mock_load):
        """Test tool consistency validation."""
        mock_metadata = {
            "cortex-good": AgentMetadata(
                agent_id="cortex-good",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["test"],
                modes_served=["TEST"],
                mcp_tools=["cortex_good_tool"],  # Valid format
                priority="P1",
                token_cost_estimate=2000
            ),
            "cortex-bad": AgentMetadata(
                agent_id="cortex-bad",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["test"],
                modes_served=["TEST"],
                mcp_tools=["InvalidTool"],  # Invalid: no cortex_ prefix
                priority="P1",
                token_cost_estimate=2000
            )
        }
        
        mock_load.return_value = mock_metadata
        
        discovery = MetadataDrivenDiscovery()
        discovery.initialize()
        
        valid, issues_count, issues = discovery.validate_tools_consistency()
        
        assert valid == 1
        assert issues_count >= 1
        assert len(issues) >= 1


class TestMetadataMultiAgentScenarios:
    """Test metadata discovery in complex multi-agent scenarios."""
    
    @patch('cortex.intent_router.metadata_driven_discovery.AgentMetadataParser.load_all_agents')
    def test_shared_tool_discovery(self, mock_load):
        """Test discovering agents that share same tool."""
        mock_metadata = {
            "cortex-agent-1": AgentMetadata(
                agent_id="cortex-agent-1",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["audit"],
                modes_served=["AUDIT"],
                mcp_tools=["cortex_shared_tool", "cortex_tool_1"],
                priority="P1",
                token_cost_estimate=2000
            ),
            "cortex-agent-2": AgentMetadata(
                agent_id="cortex-agent-2",
                version="1.0",
                status="active",
                layer="core",
                capabilities=["analysis"],
                modes_served=["ANALYZE"],
                mcp_tools=["cortex_shared_tool", "cortex_tool_2"],
                priority="P1",
                token_cost_estimate=2000
            )
        }
        
        mock_load.return_value = mock_metadata
        
        discovery = MetadataDrivenDiscovery()
        discovery.initialize()
        
        agents_with_shared = discovery.get_agents_by_tool("cortex_shared_tool")
        
        assert len(agents_with_shared) == 2
        assert "cortex-agent-1" in agents_with_shared
        assert "cortex-agent-2" in agents_with_shared


# AC_COMPLETE: AC-PHASE81-S3-P4-002 ✅ Metadata-Driven Discovery Tests
