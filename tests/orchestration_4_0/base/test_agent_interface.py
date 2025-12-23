"""
Comprehensive unit tests for agent_interface.py (Multi-Agent Collaboration).

Target Coverage: 90%+ on src/orchestration_4_0/base/agent_interface.py (~90 statements)

Test Organization:
- TestAgentContext: Dataclass initialization and methods (15 tests)
- TestAgentContextHistory: History tracking and timestamps (8 tests)
- TestAgentContextErrors: Error management (6 tests)
- TestAgentInterface: Abstract Agent class (10 tests)
- TestManagerAgent: Manager/group chat pattern (12 tests)
- TestCoordinatorAgent: Coordinator/nested chat pattern (12 tests)
- TestMultiAgentIntegration: End-to-end patterns (8 tests)

Coverage Strategy:
- All AgentContext methods: add_to_history, add_error, has_errors, get_last_agent
- All Agent abstract interface contracts
- All ManagerAgent methods: synthesize, execute fallback
- All CoordinatorAgent methods: coordinate, execute fallback
- Sequential chat, group chat, nested chat patterns
- Error propagation and state management
"""

import pytest
from datetime import datetime
from typing import Dict, List

from src.orchestration_4_0.base.agent_interface import (
    AgentContext,
    Agent,
    ManagerAgent,
    CoordinatorAgent,
)


# ============================================================================
# Concrete Test Implementations (needed for ABC testing)
# ============================================================================

class ConcreteTestAgent(Agent):
    """Concrete agent for testing abstract interface."""
    
    def __init__(self, name: str):
        """Initialize test agent."""
        super().__init__(name)
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Add agent execution marker to context."""
        context.add_to_history(self.name)
        context.data[f"{self.name}_executed"] = True
        return context


class ConcreteManagerAgent(ManagerAgent):
    """Concrete manager for testing synthesis pattern."""
    
    def __init__(self, name: str):
        """Initialize test manager."""
        super().__init__(name)
    
    async def synthesize(self, results: List[AgentContext]) -> AgentContext:
        """Synthesize all results into single context."""
        combined = AgentContext()
        combined.add_to_history(f"{self.name}_synthesized")
        
        # Merge all data
        for result in results:
            combined.data.update(result.data)
            combined.errors.extend(result.errors)
        
        combined.data["synthesis_count"] = len(results)
        return combined


class ConcreteCoordinatorAgent(CoordinatorAgent):
    """Concrete coordinator for testing nested chat pattern."""
    
    def __init__(self, name: str):
        """Initialize test coordinator."""
        super().__init__(name)
    
    async def coordinate(self, team_results: Dict[str, AgentContext]) -> AgentContext:
        """Coordinate all team results."""
        coordinated = AgentContext()
        coordinated.add_to_history(f"{self.name}_coordinated")
        
        # Merge team results
        for team_name, context in team_results.items():
            coordinated.data[f"{team_name}_data"] = context.data
            coordinated.errors.extend(context.errors)
        
        coordinated.data["coordination_teams"] = list(team_results.keys())
        return coordinated


# ============================================================================
# Test Class: AgentContext (15 tests)
# ============================================================================

class TestAgentContext:
    """Test AgentContext dataclass initialization and basic usage."""
    
    def test_agent_context_is_dataclass(self):
        """AgentContext should be a dataclass."""
        ctx = AgentContext()
        assert hasattr(ctx, "__dataclass_fields__")
    
    def test_default_data_empty_dict(self):
        """Default data should be empty dictionary."""
        ctx = AgentContext()
        assert ctx.data == {}
        assert isinstance(ctx.data, dict)
    
    def test_default_metadata_empty_dict(self):
        """Default metadata should be empty dictionary."""
        ctx = AgentContext()
        assert ctx.metadata == {}
        assert isinstance(ctx.metadata, dict)
    
    def test_default_history_empty_list(self):
        """Default history should be empty list."""
        ctx = AgentContext()
        assert ctx.history == []
        assert isinstance(ctx.history, list)
    
    def test_default_errors_empty_list(self):
        """Default errors should be empty list."""
        ctx = AgentContext()
        assert ctx.errors == []
        assert isinstance(ctx.errors, list)
    
    def test_custom_data(self):
        """Should accept custom data dictionary."""
        data = {"user_id": 123, "action": "query"}
        ctx = AgentContext(data=data)
        assert ctx.data == data
        assert ctx.data["user_id"] == 123
    
    def test_custom_metadata(self):
        """Should accept custom metadata dictionary."""
        metadata = {"source": "api", "version": "v1"}
        ctx = AgentContext(metadata=metadata)
        assert ctx.metadata == metadata
        assert ctx.metadata["source"] == "api"
    
    def test_custom_history(self):
        """Should accept custom history list."""
        history = ["Agent1", "Agent2"]
        ctx = AgentContext(history=history)
        assert ctx.history == history
        assert len(ctx.history) == 2
    
    def test_custom_errors(self):
        """Should accept custom errors list."""
        errors = ["Error 1", "Error 2"]
        ctx = AgentContext(errors=errors)
        assert ctx.errors == errors
        assert len(ctx.errors) == 2
    
    def test_all_custom_fields(self):
        """Should accept all fields with custom values."""
        ctx = AgentContext(
            data={"key": "value"},
            metadata={"meta": "data"},
            history=["Agent1"],
            errors=["Error1"]
        )
        assert ctx.data["key"] == "value"
        assert ctx.metadata["meta"] == "data"
        assert ctx.history[0] == "Agent1"
        assert ctx.errors[0] == "Error1"
    
    def test_data_mutation(self):
        """Should support data dictionary mutations."""
        ctx = AgentContext()
        ctx.data["new_key"] = "new_value"
        assert ctx.data["new_key"] == "new_value"
        assert len(ctx.data) == 1
    
    def test_metadata_mutation(self):
        """Should support metadata dictionary mutations."""
        ctx = AgentContext()
        ctx.metadata["timestamp"] = "2024-01-01"
        assert ctx.metadata["timestamp"] == "2024-01-01"
    
    def test_independent_instances(self):
        """Separate instances should have independent data."""
        ctx1 = AgentContext()
        ctx2 = AgentContext()
        ctx1.data["key"] = "value1"
        ctx2.data["key"] = "value2"
        assert ctx1.data["key"] != ctx2.data["key"]
    
    def test_nested_data_structures(self):
        """Should support nested data structures."""
        ctx = AgentContext(data={
            "user": {"id": 123, "name": "Alice"},
            "actions": [{"type": "create"}, {"type": "update"}]
        })
        assert ctx.data["user"]["name"] == "Alice"
        assert len(ctx.data["actions"]) == 2
    
    def test_empty_context_creation(self):
        """Should create valid empty context."""
        ctx = AgentContext()
        assert not ctx.has_errors()
        assert ctx.get_last_agent() is None


# ============================================================================
# Test Class: AgentContext History (8 tests)
# ============================================================================

class TestAgentContextHistory:
    """Test history tracking and timestamp management."""
    
    def test_add_to_history_appends_agent(self):
        """add_to_history should append agent name to history."""
        ctx = AgentContext()
        ctx.add_to_history("Agent1")
        assert "Agent1" in ctx.history
        assert len(ctx.history) == 1
    
    def test_add_to_history_multiple_agents(self):
        """Should track multiple agents in order."""
        ctx = AgentContext()
        ctx.add_to_history("Agent1")
        ctx.add_to_history("Agent2")
        ctx.add_to_history("Agent3")
        assert ctx.history == ["Agent1", "Agent2", "Agent3"]
    
    def test_add_to_history_creates_timestamp(self):
        """add_to_history should create timestamp in metadata."""
        ctx = AgentContext()
        ctx.add_to_history("Agent1")
        assert "Agent1_timestamp" in ctx.metadata
    
    def test_timestamp_is_iso_format(self):
        """Timestamp should be ISO 8601 format."""
        ctx = AgentContext()
        ctx.add_to_history("Agent1")
        timestamp = ctx.metadata["Agent1_timestamp"]
        # Should parse as ISO datetime
        datetime.fromisoformat(timestamp)
    
    def test_get_last_agent_returns_most_recent(self):
        """get_last_agent should return most recent agent."""
        ctx = AgentContext()
        ctx.add_to_history("Agent1")
        ctx.add_to_history("Agent2")
        assert ctx.get_last_agent() == "Agent2"
    
    def test_get_last_agent_empty_history(self):
        """get_last_agent should return None for empty history."""
        ctx = AgentContext()
        assert ctx.get_last_agent() is None
    
    def test_get_last_agent_single_entry(self):
        """get_last_agent should work with single entry."""
        ctx = AgentContext()
        ctx.add_to_history("OnlyAgent")
        assert ctx.get_last_agent() == "OnlyAgent"
    
    def test_history_preserves_order(self):
        """History should preserve execution order."""
        ctx = AgentContext()
        agents = ["Alpha", "Beta", "Gamma", "Delta"]
        for agent in agents:
            ctx.add_to_history(agent)
        assert ctx.history == agents


# ============================================================================
# Test Class: AgentContext Errors (6 tests)
# ============================================================================

class TestAgentContextErrors:
    """Test error management in AgentContext."""
    
    def test_add_error_appends_to_list(self):
        """add_error should append error to errors list."""
        ctx = AgentContext()
        ctx.add_error("Test error")
        assert "Test error" in ctx.errors
        assert len(ctx.errors) == 1
    
    def test_add_multiple_errors(self):
        """Should track multiple errors."""
        ctx = AgentContext()
        ctx.add_error("Error 1")
        ctx.add_error("Error 2")
        ctx.add_error("Error 3")
        assert len(ctx.errors) == 3
        assert ctx.errors == ["Error 1", "Error 2", "Error 3"]
    
    def test_has_errors_returns_false_initially(self):
        """has_errors should return False for new context."""
        ctx = AgentContext()
        assert ctx.has_errors() is False
    
    def test_has_errors_returns_true_after_error(self):
        """has_errors should return True after adding error."""
        ctx = AgentContext()
        ctx.add_error("Some error")
        assert ctx.has_errors() is True
    
    def test_has_errors_with_multiple_errors(self):
        """has_errors should work with multiple errors."""
        ctx = AgentContext()
        ctx.add_error("Error 1")
        ctx.add_error("Error 2")
        assert ctx.has_errors() is True
        assert len(ctx.errors) == 2
    
    def test_errors_cleared_manually(self):
        """Should support manual error clearing."""
        ctx = AgentContext()
        ctx.add_error("Error")
        assert ctx.has_errors()
        ctx.errors.clear()
        assert not ctx.has_errors()


# ============================================================================
# Test Class: Agent Interface (10 tests)
# ============================================================================

class TestAgentInterface:
    """Test abstract Agent class and interface."""
    
    def test_agent_is_abstract(self):
        """Agent should be abstract (cannot instantiate)."""
        with pytest.raises(TypeError):
            Agent("test")  # Missing execute implementation
    
    def test_concrete_agent_instantiation(self):
        """Concrete agent should instantiate successfully."""
        agent = ConcreteTestAgent("TestAgent1")
        assert agent is not None
        assert agent.name == "TestAgent1"
    
    def test_agent_has_name(self):
        """Agent should store name attribute."""
        agent = ConcreteTestAgent("MyAgent")
        assert hasattr(agent, "name")
        assert agent.name == "MyAgent"
    
    def test_get_name_method(self):
        """get_name should return agent name."""
        agent = ConcreteTestAgent("Agent123")
        assert agent.get_name() == "Agent123"
    
    @pytest.mark.asyncio
    async def test_agent_execute_receives_context(self):
        """execute should receive AgentContext parameter."""
        agent = ConcreteTestAgent("Agent1")
        ctx = AgentContext()
        result = await agent.execute(ctx)
        assert isinstance(result, AgentContext)
    
    @pytest.mark.asyncio
    async def test_agent_execute_updates_context(self):
        """execute should update context."""
        agent = ConcreteTestAgent("Agent1")
        ctx = AgentContext()
        result = await agent.execute(ctx)
        assert result.data.get("Agent1_executed") is True
    
    @pytest.mark.asyncio
    async def test_agent_execute_adds_history(self):
        """execute should add agent to history."""
        agent = ConcreteTestAgent("Agent1")
        ctx = AgentContext()
        result = await agent.execute(ctx)
        assert "Agent1" in result.history
    
    @pytest.mark.asyncio
    async def test_agent_sequential_execution(self):
        """Multiple agents should execute sequentially."""
        agent1 = ConcreteTestAgent("Agent1")
        agent2 = ConcreteTestAgent("Agent2")
        ctx = AgentContext()
        ctx = await agent1.execute(ctx)
        ctx = await agent2.execute(ctx)
        assert ctx.history == ["Agent1", "Agent2"]
        assert ctx.data["Agent1_executed"] is True
        assert ctx.data["Agent2_executed"] is True
    
    @pytest.mark.asyncio
    async def test_agent_context_carries_state(self):
        """Context should carry state between agents."""
        agent1 = ConcreteTestAgent("Agent1")
        agent2 = ConcreteTestAgent("Agent2")
        ctx = AgentContext(data={"initial": "value"})
        ctx = await agent1.execute(ctx)
        ctx = await agent2.execute(ctx)
        # Initial data preserved
        assert ctx.data["initial"] == "value"
        # New data added
        assert "Agent1_executed" in ctx.data
        assert "Agent2_executed" in ctx.data
    
    @pytest.mark.asyncio
    async def test_agent_execute_returns_context(self):
        """execute must return AgentContext."""
        agent = ConcreteTestAgent("Agent1")
        ctx = AgentContext()
        result = await agent.execute(ctx)
        assert isinstance(result, AgentContext)


# ============================================================================
# Test Class: ManagerAgent (12 tests)
# ============================================================================

class TestManagerAgent:
    """Test ManagerAgent for group chat pattern."""
    
    def test_manager_agent_is_agent_subclass(self):
        """ManagerAgent should inherit from Agent."""
        manager = ConcreteManagerAgent("Manager1")
        assert isinstance(manager, Agent)
    
    def test_manager_agent_has_synthesize(self):
        """ManagerAgent should have synthesize method."""
        manager = ConcreteManagerAgent("Manager1")
        assert hasattr(manager, "synthesize")
    
    @pytest.mark.asyncio
    async def test_manager_synthesize_receives_list(self):
        """synthesize should receive list of contexts."""
        manager = ConcreteManagerAgent("Manager1")
        results = [
            AgentContext(data={"agent1": "result1"}),
            AgentContext(data={"agent2": "result2"}),
        ]
        combined = await manager.synthesize(results)
        assert isinstance(combined, AgentContext)
    
    @pytest.mark.asyncio
    async def test_manager_synthesize_combines_data(self):
        """synthesize should combine data from all contexts."""
        manager = ConcreteManagerAgent("Manager1")
        results = [
            AgentContext(data={"key1": "value1"}),
            AgentContext(data={"key2": "value2"}),
            AgentContext(data={"key3": "value3"}),
        ]
        combined = await manager.synthesize(results)
        assert combined.data["key1"] == "value1"
        assert combined.data["key2"] == "value2"
        assert combined.data["key3"] == "value3"
    
    @pytest.mark.asyncio
    async def test_manager_synthesize_tracks_count(self):
        """synthesize should track number of results."""
        manager = ConcreteManagerAgent("Manager1")
        results = [AgentContext() for _ in range(5)]
        combined = await manager.synthesize(results)
        assert combined.data["synthesis_count"] == 5
    
    @pytest.mark.asyncio
    async def test_manager_synthesize_aggregates_errors(self):
        """synthesize should aggregate errors from all contexts."""
        manager = ConcreteManagerAgent("Manager1")
        results = [
            AgentContext(errors=["Error1"]),
            AgentContext(errors=["Error2", "Error3"]),
        ]
        combined = await manager.synthesize(results)
        assert len(combined.errors) == 3
        assert "Error1" in combined.errors
        assert "Error2" in combined.errors
    
    @pytest.mark.asyncio
    async def test_manager_synthesize_adds_history(self):
        """synthesize should add manager to history."""
        manager = ConcreteManagerAgent("Manager1")
        results = [AgentContext()]
        combined = await manager.synthesize(results)
        assert "Manager1_synthesized" in combined.history
    
    @pytest.mark.asyncio
    async def test_manager_execute_fallback(self):
        """execute should delegate to synthesize for single context."""
        manager = ConcreteManagerAgent("Manager1")
        ctx = AgentContext(data={"test": "data"})
        result = await manager.execute(ctx)
        # Should have wrapped in list and called synthesize
        assert isinstance(result, AgentContext)
    
    @pytest.mark.asyncio
    async def test_manager_execute_preserves_data(self):
        """execute fallback should preserve context data."""
        manager = ConcreteManagerAgent("Manager1")
        ctx = AgentContext(data={"key": "value"})
        result = await manager.execute(ctx)
        assert result.data["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_manager_empty_results(self):
        """synthesize should handle empty results list."""
        manager = ConcreteManagerAgent("Manager1")
        combined = await manager.synthesize([])
        assert isinstance(combined, AgentContext)
        assert combined.data["synthesis_count"] == 0
    
    @pytest.mark.asyncio
    async def test_manager_single_result(self):
        """synthesize should handle single result."""
        manager = ConcreteManagerAgent("Manager1")
        results = [AgentContext(data={"only": "one"})]
        combined = await manager.synthesize(results)
        assert combined.data["only"] == "one"
        assert combined.data["synthesis_count"] == 1
    
    @pytest.mark.asyncio
    async def test_manager_many_results(self):
        """synthesize should handle many parallel results."""
        manager = ConcreteManagerAgent("Manager1")
        results = [AgentContext(data={f"agent{i}": i}) for i in range(10)]
        combined = await manager.synthesize(results)
        assert combined.data["synthesis_count"] == 10
        assert combined.data["agent5"] == 5


# ============================================================================
# Test Class: CoordinatorAgent (12 tests)
# ============================================================================

class TestCoordinatorAgent:
    """Test CoordinatorAgent for nested chat pattern."""
    
    def test_coordinator_agent_is_agent_subclass(self):
        """CoordinatorAgent should inherit from Agent."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        assert isinstance(coordinator, Agent)
    
    def test_coordinator_agent_has_coordinate(self):
        """CoordinatorAgent should have coordinate method."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        assert hasattr(coordinator, "coordinate")
    
    @pytest.mark.asyncio
    async def test_coordinator_coordinate_receives_dict(self):
        """coordinate should receive dict of team results."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        team_results = {
            "team1": AgentContext(data={"result": "A"}),
            "team2": AgentContext(data={"result": "B"}),
        }
        coordinated = await coordinator.coordinate(team_results)
        assert isinstance(coordinated, AgentContext)
    
    @pytest.mark.asyncio
    async def test_coordinator_coordinate_combines_teams(self):
        """coordinate should combine data from all teams."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        team_results = {
            "team_alpha": AgentContext(data={"alpha_key": "alpha_value"}),
            "team_beta": AgentContext(data={"beta_key": "beta_value"}),
        }
        coordinated = await coordinator.coordinate(team_results)
        assert "team_alpha_data" in coordinated.data
        assert "team_beta_data" in coordinated.data
        assert coordinated.data["team_alpha_data"]["alpha_key"] == "alpha_value"
    
    @pytest.mark.asyncio
    async def test_coordinator_coordinate_tracks_teams(self):
        """coordinate should track team names."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        team_results = {
            "team1": AgentContext(),
            "team2": AgentContext(),
            "team3": AgentContext(),
        }
        coordinated = await coordinator.coordinate(team_results)
        assert "coordination_teams" in coordinated.data
        assert len(coordinated.data["coordination_teams"]) == 3
        assert "team1" in coordinated.data["coordination_teams"]
    
    @pytest.mark.asyncio
    async def test_coordinator_coordinate_aggregates_errors(self):
        """coordinate should aggregate errors from all teams."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        team_results = {
            "team1": AgentContext(errors=["Team1Error"]),
            "team2": AgentContext(errors=["Team2Error1", "Team2Error2"]),
        }
        coordinated = await coordinator.coordinate(team_results)
        assert len(coordinated.errors) == 3
        assert "Team1Error" in coordinated.errors
    
    @pytest.mark.asyncio
    async def test_coordinator_coordinate_adds_history(self):
        """coordinate should add coordinator to history."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        team_results = {"team1": AgentContext()}
        coordinated = await coordinator.coordinate(team_results)
        assert "Coordinator1_coordinated" in coordinated.history
    
    @pytest.mark.asyncio
    async def test_coordinator_execute_fallback(self):
        """execute should delegate to coordinate for single context."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        ctx = AgentContext(data={"test": "data"})
        result = await coordinator.execute(ctx)
        assert isinstance(result, AgentContext)
    
    @pytest.mark.asyncio
    async def test_coordinator_execute_wraps_default(self):
        """execute should wrap context in 'default' team."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        ctx = AgentContext(data={"key": "value"})
        result = await coordinator.execute(ctx)
        # Should have wrapped as {"default": ctx}
        assert "default_data" in result.data
        assert result.data["default_data"]["key"] == "value"
    
    @pytest.mark.asyncio
    async def test_coordinator_empty_teams(self):
        """coordinate should handle empty team results."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        coordinated = await coordinator.coordinate({})
        assert isinstance(coordinated, AgentContext)
        assert coordinated.data["coordination_teams"] == []
    
    @pytest.mark.asyncio
    async def test_coordinator_single_team(self):
        """coordinate should handle single team."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        team_results = {"only_team": AgentContext(data={"solo": "data"})}
        coordinated = await coordinator.coordinate(team_results)
        assert len(coordinated.data["coordination_teams"]) == 1
        assert "only_team_data" in coordinated.data
    
    @pytest.mark.asyncio
    async def test_coordinator_many_teams(self):
        """coordinate should handle many teams."""
        coordinator = ConcreteCoordinatorAgent("Coordinator1")
        team_results = {f"team{i}": AgentContext(data={"num": i}) for i in range(10)}
        coordinated = await coordinator.coordinate(team_results)
        assert len(coordinated.data["coordination_teams"]) == 10
        assert "team5_data" in coordinated.data


# ============================================================================
# Test Class: Multi-Agent Integration (8 tests)
# ============================================================================

class TestMultiAgentIntegration:
    """Test end-to-end multi-agent patterns."""
    
    @pytest.mark.asyncio
    async def test_sequential_chat_pattern(self):
        """Sequential chat: Agent1 → Agent2 → Agent3."""
        agent1 = ConcreteTestAgent("Agent1")
        agent2 = ConcreteTestAgent("Agent2")
        agent3 = ConcreteTestAgent("Agent3")
        
        ctx = AgentContext(data={"start": "value"})
        ctx = await agent1.execute(ctx)
        ctx = await agent2.execute(ctx)
        ctx = await agent3.execute(ctx)
        
        assert ctx.history == ["Agent1", "Agent2", "Agent3"]
        assert ctx.data["start"] == "value"  # Preserved
        assert ctx.data["Agent3_executed"] is True
    
    @pytest.mark.asyncio
    async def test_group_chat_pattern(self):
        """Group chat: Parallel agents → Manager synthesis."""
        agent1 = ConcreteTestAgent("Worker1")
        agent2 = ConcreteTestAgent("Worker2")
        agent3 = ConcreteTestAgent("Worker3")
        manager = ConcreteManagerAgent("Manager")
        
        # Parallel execution (simulated)
        ctx1 = await agent1.execute(AgentContext())
        ctx2 = await agent2.execute(AgentContext())
        ctx3 = await agent3.execute(AgentContext())
        
        # Manager synthesis
        combined = await manager.synthesize([ctx1, ctx2, ctx3])
        
        assert combined.data["synthesis_count"] == 3
        assert combined.data["Worker1_executed"] is True
        assert combined.data["Worker2_executed"] is True
        assert combined.data["Worker3_executed"] is True
    
    @pytest.mark.asyncio
    async def test_nested_chat_pattern(self):
        """Nested chat: Multiple teams → Coordinator integration."""
        # Team 1
        team1_agent1 = ConcreteTestAgent("Team1_Agent1")
        team1_agent2 = ConcreteTestAgent("Team1_Agent2")
        team1_ctx = AgentContext()
        team1_ctx = await team1_agent1.execute(team1_ctx)
        team1_ctx = await team1_agent2.execute(team1_ctx)
        
        # Team 2
        team2_agent1 = ConcreteTestAgent("Team2_Agent1")
        team2_ctx = await team2_agent1.execute(AgentContext())
        
        # Coordinator
        coordinator = ConcreteCoordinatorAgent("Coordinator")
        result = await coordinator.coordinate({
            "team1": team1_ctx,
            "team2": team2_ctx,
        })
        
        assert len(result.data["coordination_teams"]) == 2
        assert "team1_data" in result.data
        assert "team2_data" in result.data
    
    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Errors should propagate through agent chain."""
        agent1 = ConcreteTestAgent("Agent1")
        agent2 = ConcreteTestAgent("Agent2")
        
        ctx = AgentContext()
        ctx.add_error("Initial error")
        ctx = await agent1.execute(ctx)
        ctx.add_error("Agent1 error")
        ctx = await agent2.execute(ctx)
        
        assert ctx.has_errors()
        assert len(ctx.errors) == 2
        assert "Initial error" in ctx.errors
        assert "Agent1 error" in ctx.errors
    
    @pytest.mark.asyncio
    async def test_manager_error_aggregation(self):
        """Manager should aggregate errors from parallel agents."""
        agent1 = ConcreteTestAgent("Agent1")
        agent2 = ConcreteTestAgent("Agent2")
        manager = ConcreteManagerAgent("Manager")
        
        ctx1 = await agent1.execute(AgentContext())
        ctx1.add_error("Agent1 failed")
        
        ctx2 = await agent2.execute(AgentContext())
        ctx2.add_error("Agent2 warning")
        
        combined = await manager.synthesize([ctx1, ctx2])
        assert len(combined.errors) == 2
    
    @pytest.mark.asyncio
    async def test_coordinator_error_aggregation(self):
        """Coordinator should aggregate errors from teams."""
        team1_ctx = AgentContext(errors=["Team1 error"])
        team2_ctx = AgentContext(errors=["Team2 error1", "Team2 error2"])
        
        coordinator = ConcreteCoordinatorAgent("Coordinator")
        result = await coordinator.coordinate({
            "team1": team1_ctx,
            "team2": team2_ctx,
        })
        
        assert len(result.errors) == 3
    
    @pytest.mark.asyncio
    async def test_data_immutability_between_agents(self):
        """Each agent should see consistent data."""
        agent1 = ConcreteTestAgent("Agent1")
        agent2 = ConcreteTestAgent("Agent2")
        
        ctx = AgentContext(data={"shared": "initial"})
        ctx = await agent1.execute(ctx)
        # Agent1 adds data but doesn't change shared
        assert ctx.data["shared"] == "initial"
        ctx = await agent2.execute(ctx)
        # Agent2 sees Agent1's additions
        assert ctx.data["Agent1_executed"] is True
    
    @pytest.mark.asyncio
    async def test_complex_nested_pattern(self):
        """Complex: Sequential → Group chat → Nested coordinator."""
        # Sequential preprocessing
        preprocessor = ConcreteTestAgent("Preprocessor")
        ctx = await preprocessor.execute(AgentContext(data={"input": "data"}))
        
        # Group chat (parallel workers)
        worker1 = ConcreteTestAgent("Worker1")
        worker2 = ConcreteTestAgent("Worker2")
        manager = ConcreteManagerAgent("Manager")
        
        ctx1 = await worker1.execute(AgentContext(data=ctx.data.copy()))
        ctx2 = await worker2.execute(AgentContext(data=ctx.data.copy()))
        group_result = await manager.synthesize([ctx1, ctx2])
        
        # Nested coordination
        coordinator = ConcreteCoordinatorAgent("Coordinator")
        final = await coordinator.coordinate({
            "preprocessing": ctx,
            "group_chat": group_result,
        })
        
        assert "coordination_teams" in final.data
        assert len(final.data["coordination_teams"]) == 2
        assert "preprocessing_data" in final.data
        assert "group_chat_data" in final.data
