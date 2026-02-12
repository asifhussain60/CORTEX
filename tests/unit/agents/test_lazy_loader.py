"""
Tests for lazy_loader.py (phase-81 S1).

Tests intent-based agent loading system with token savings verification.

Authority: cortex-registry/_cortex-master/index.yaml WAVE-L
Created: 2026-02-12
AC-ID: AC-WAVE-L-001
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cortex.agents.lazy_loader import (
    IntentType,
    AgentMetadata,
    IntentAgentMapper,
    load_agents_for_intent,
)


class TestAgentMetadata:
    """Test AgentMetadata dataclass."""
    
    def test_agent_metadata_creation(self):
        """Test creating agent metadata."""
        metadata = AgentMetadata(
            name="cortex-executor",
            file_path=Path("/test/cortex-executor.md"),
            capabilities={"implement", "fix"},
            intents={IntentType.IMPLEMENT, IntentType.FIX},
            token_cost=20000,
            priority=10,
        )
        
        assert metadata.name == "cortex-executor"
        assert metadata.token_cost == 20000
        assert metadata.priority == 10
        assert IntentType.IMPLEMENT in metadata.intents
    
    def test_agent_metadata_hashable(self):
        """Test that AgentMetadata is hashable for set operations."""
        metadata1 = AgentMetadata(name="test", file_path=Path("/test.md"))
        metadata2 = AgentMetadata(name="test", file_path=Path("/test.md"))
        
        # Should be hashable
        agent_set = {metadata1, metadata2}
        assert len(agent_set) >= 1  # At least one (may dedupe)


class TestIntentAgentMapper:
    """Test IntentAgentMapper class."""
    
    def test_intent_agent_map_complete(self):
        """Test that all intents have agent mappings."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        
        # All IntentTypes should have mappings
        for intent in IntentType:
            agents = mapper.INTENT_AGENT_MAP.get(intent)
            assert agents is not None, f"No mapping for {intent}"
            assert len(agents) > 0, f"Empty mapping for {intent}"
    
    def test_get_agents_for_implement_intent(self):
        """Test loading agents for IMPLEMENT intent."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        
        # Mock registry with test agents
        mapper.agent_registry = {
            "cortex-executor": AgentMetadata(
                name="cortex-executor",
                file_path=Path("/test/cortex-executor.md"),
                token_cost=20000,
                priority=10,
            ),
            "cortex-architect": AgentMetadata(
                name="cortex-architect",
                file_path=Path("/test/cortex-architect.md"),
                token_cost=25000,
                priority=20,
            ),
            "cortex-holistic-validator": AgentMetadata(
                name="cortex-holistic-validator",
                file_path=Path("/test/cortex-holistic-validator.md"),
                token_cost=18000,
                priority=15,
            ),
        }
        
        agents = mapper.get_agents_for_intent(IntentType.IMPLEMENT)
        
        assert len(agents) == 3
        # Should be sorted by priority
        assert agents[0].name == "cortex-executor"  # priority 10
        assert agents[1].name == "cortex-holistic-validator"  # priority 15
        assert agents[2].name == "cortex-architect"  # priority 20
    
    def test_get_agents_for_analyze_intent(self):
        """Test loading agents for ANALYZE intent."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        
        expected_agents = {
            "cortex-auditor",
            "cortex-holistic-validator",
            "cortex-meta-auditor",
        }
        
        # Get mapped agent names
        mapped_names = mapper.INTENT_AGENT_MAP[IntentType.ANALYZE]
        
        assert mapped_names == expected_agents
    
    def test_get_token_cost(self):
        """Test calculating token cost for an intent."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        
        mapper.agent_registry = {
            "cortex-auditor": AgentMetadata(
                name="cortex-auditor",
                file_path=Path("/test.md"),
                token_cost=15000,
            ),
            "cortex-holistic-validator": AgentMetadata(
                name="cortex-holistic-validator",
                file_path=Path("/test.md"),
                token_cost=18000,
            ),
            "cortex-meta-auditor": AgentMetadata(
                name="cortex-meta-auditor",
                file_path=Path("/test.md"),
                token_cost=12000,
            ),
        }
        
        cost = mapper.get_token_cost(IntentType.ANALYZE)
        
        # Should be sum of 3 agents
        assert cost == 45000  # 15000 + 18000 + 12000
    
    def test_lazy_vs_eager_token_comparison(self):
        """Test token savings from lazy loading."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        
        # Simulate 11 agents with varying token costs
        mapper.agent_registry = {
            f"agent-{i}": AgentMetadata(
                name=f"agent-{i}",
                file_path=Path(f"/test/agent-{i}.md"),
                token_cost=15000 + (i * 1000),
            )
            for i in range(11)
        }
        
        # Create a local copy of the map for this test (don't modify class-level)
        original_map = mapper.INTENT_AGENT_MAP.copy()
        try:
            # Temporarily override IMPLEMENT mapping
            mapper.INTENT_AGENT_MAP = original_map.copy()
            mapper.INTENT_AGENT_MAP[IntentType.IMPLEMENT] = {
                "agent-0", "agent-1", "agent-2"
            }
            
            savings = mapper.get_token_savings(IntentType.IMPLEMENT)
            
            assert "eager_loading" in savings
            assert "lazy_loading" in savings
            assert "savings" in savings
            assert "savings_percent" in savings
            
            # Eager should load all 11
            # Lazy should load only 3
            assert savings["eager_loading"] > savings["lazy_loading"]
            assert savings["savings"] > 0
            assert savings["savings_percent"] > 50  # Should save >50%
        finally:
            # Restore original map
            mapper.INTENT_AGENT_MAP = original_map
    
    def test_get_all_agents(self):
        """Test retrieving all registered agents."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        
        mapper.agent_registry = {
            "agent-a": AgentMetadata(
                name="agent-a",
                file_path=Path("/test.md"),
                priority=30,
            ),
            "agent-b": AgentMetadata(
                name="agent-b",
                file_path=Path("/test.md"),
                priority=10,
            ),
            "agent-c": AgentMetadata(
                name="agent-c",
                file_path=Path("/test.md"),
                priority=20,
            ),
        }
        
        all_agents = mapper.get_all_agents()
        
        assert len(all_agents) == 3
        # Should be sorted by priority
        assert all_agents[0].name == "agent-b"  # priority 10
        assert all_agents[1].name == "agent-c"  # priority 20
        assert all_agents[2].name == "agent-a"  # priority 30
    
    def test_empty_registry_handling(self):
        """Test handling of empty agent registry."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        mapper.agent_registry = {}
        
        agents = mapper.get_agents_for_intent(IntentType.IMPLEMENT)
        assert agents == []
        
        cost = mapper.get_token_cost(IntentType.IMPLEMENT)
        assert cost == 0
    
    def test_unknown_intent_handling(self):
        """Test handling of unknown intent types."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        mapper.agent_registry = {"test": AgentMetadata(name="test", file_path=Path("/test.md"))}
        
        # Create a mock intent not in the map
        with patch.object(mapper, 'INTENT_AGENT_MAP', {}):
            agents = mapper.get_agents_for_intent(IntentType.IMPLEMENT)
            assert agents == []


class TestLoadAgentsForIntent:
    """Test load_agents_for_intent helper function."""
    
    def test_load_agents_for_intent_function(self):
        """Test the convenience function."""
        with patch('cortex.agents.lazy_loader.IntentAgentMapper') as MockMapper:
            mock_mapper_instance = Mock()
            mock_mapper_instance.get_agents_for_intent.return_value = [
                AgentMetadata(name="test", file_path=Path("/test.md"))
            ]
            MockMapper.return_value = mock_mapper_instance
            
            agents = load_agents_for_intent(IntentType.IMPLEMENT)
            
            assert len(agents) == 1
            MockMapper.assert_called_once()
            mock_mapper_instance.get_agents_for_intent.assert_called_once_with(
                IntentType.IMPLEMENT
            )


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_implement_intent_loads_execution_agents(self):
        """Test that IMPLEMENT intent loads execution-related agents."""
        # Use the class-level constant directly (no instance needed for this test)
        agent_names = IntentAgentMapper.INTENT_AGENT_MAP[IntentType.IMPLEMENT]
        
        # Should include execution agents (verify the mapping exists)
        expected_agents = {
            "cortex-executor",
            "cortex-architect",
            "cortex-holistic-validator",
        }
        assert agent_names == expected_agents
    
    def test_audit_intent_loads_audit_agents(self):
        """Test that AUDIT intent loads audit-related agents."""
        # Use the class-level constant directly
        agent_names = IntentAgentMapper.INTENT_AGENT_MAP[IntentType.AUDIT]
        
        # Should include audit agents
        expected_agents = {
            "cortex-auditor",
            "cortex-meta-auditor",
            "cortex-master-plan-auditor",
        }
        assert agent_names == expected_agents
    
    def test_token_savings_calculation_realistic(self):
        """Test token savings with realistic numbers."""
        mapper = IntentAgentMapper(agents_dir=Path("/nonexistent"))
        
        # Simulate realistic token costs (11 agents, ~15k each = 190k total)
        mapper.agent_registry = {
            "cortex-executor": AgentMetadata(name="cortex-executor", file_path=Path("/test.md"), token_cost=20000),
            "cortex-architect": AgentMetadata(name="cortex-architect", file_path=Path("/test.md"), token_cost=25000),
            "cortex-auditor": AgentMetadata(name="cortex-auditor", file_path=Path("/test.md"), token_cost=15000),
            "cortex-designer": AgentMetadata(name="cortex-designer", file_path=Path("/test.md"), token_cost=18000),
            "cortex-holistic-validator": AgentMetadata(name="cortex-holistic-validator", file_path=Path("/test.md"), token_cost=18000),
            "cortex-meta-auditor": AgentMetadata(name="cortex-meta-auditor", file_path=Path("/test.md"), token_cost=12000),
            "cortex-master-plan-auditor": AgentMetadata(name="cortex-master-plan-auditor", file_path=Path("/test.md"), token_cost=14000),
            "cortex-phase-resolver": AgentMetadata(name="cortex-phase-resolver", file_path=Path("/test.md"), token_cost=16000),
            "master-planner": AgentMetadata(name="master-planner", file_path=Path("/test.md"), token_cost=22000),
            "cortex-digest": AgentMetadata(name="cortex-digest", file_path=Path("/test.md"), token_cost=13000),
            "cortex-storyteller": AgentMetadata(name="cortex-storyteller", file_path=Path("/test.md"), token_cost=17000),
        }
        
        savings = mapper.get_token_savings(IntentType.IMPLEMENT)
        
        # Total eager loading: 190k
        assert savings["eager_loading"] == 190000.0
        
        # Lazy loading for IMPLEMENT (3 agents): 20k + 25k + 18k = 63k
        expected_lazy = 20000 + 25000 + 18000  # cortex-executor + cortex-architect + cortex-holistic-validator
        assert savings["lazy_loading"] == float(expected_lazy)
        
        # Savings: 190k - 63k = 127k
        assert savings["savings"] == 190000.0 - float(expected_lazy)
        
        # Savings percent: ~67%
        expected_percent = ((190000 - expected_lazy) / 190000) * 100
        assert abs(savings["savings_percent"] - expected_percent) < 0.1
