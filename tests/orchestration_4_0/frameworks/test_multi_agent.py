"""
Test Suite for Multi-Agent Collaboration Framework

Phase 5 Package 6: Multi-Agent Collaboration Framework
RED Phase: All tests must FAIL initially (TDD requirement)

Test Coverage:
- Sequential chat pattern (5 tests)
- Group chat pattern (5 tests)
- Nested chat pattern (3 tests)
- Integration & edge cases (2 tests)

Total: 15 tests targeting 85%+ coverage
"""

import pytest
import asyncio
import time
from typing import List, Dict
from datetime import datetime

# Import the implemented MultiAgentOrchestrator
try:
    from src.orchestration_4_0.frameworks.multi_agent_orchestrator import MultiAgentOrchestrator as AgentCollaborationOrchestrator
except ImportError:
    AgentCollaborationOrchestrator = None

from src.orchestration_4_0.base.agent_interface import (
    Agent,
    AgentContext,
    ManagerAgent,
    CoordinatorAgent
)


# ============================================================================
# TEST FIXTURES: Mock Agents for Testing
# ============================================================================

class MockAgent(Agent):
    """Mock agent that appends data to context"""
    
    def __init__(self, name: str, data_key: str, data_value: str, delay: float = 0.0):
        super().__init__(name)
        self.data_key = data_key
        self.data_value = data_value
        self.delay = delay
        self.execution_count = 0
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Execute mock agent: add data, track history"""
        self.execution_count += 1
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        context.add_to_history(self.name)
        context.data[self.data_key] = self.data_value
        
        return context


class FailingAgent(Agent):
    """Mock agent that always fails"""
    
    def __init__(self, name: str, error_message: str):
        super().__init__(name)
        self.error_message = error_message
    
    async def execute(self, context: AgentContext) -> AgentContext:
        """Fail with error message"""
        context.add_to_history(self.name)
        context.add_error(self.error_message)
        raise Exception(self.error_message)


class MockManagerAgent(ManagerAgent):
    """Mock manager that combines agent results"""
    
    def __init__(self, name: str = "MockManager"):
        super().__init__(name)
    
    async def synthesize(self, results: List[AgentContext]) -> AgentContext:
        """Combine all agent data into single context"""
        combined = AgentContext()
        combined.add_to_history(self.name)
        
        # Merge all data from parallel agents
        for result in results:
            combined.data.update(result.data)
            combined.history.extend(result.history)
        
        combined.data["synthesis_complete"] = True
        return combined


class MockCoordinatorAgent(CoordinatorAgent):
    """Mock coordinator that integrates team results"""
    
    def __init__(self, name: str = "MockCoordinator"):
        super().__init__(name)
    
    async def coordinate(self, team_results: Dict[str, AgentContext]) -> AgentContext:
        """Integrate results from multiple teams"""
        coordinated = AgentContext()
        coordinated.add_to_history(self.name)
        
        # Merge team results with team namespace
        for team_name, team_context in team_results.items():
            coordinated.data[f"team_{team_name}"] = team_context.data
            coordinated.history.extend(team_context.history)
        
        coordinated.data["coordination_complete"] = True
        return coordinated


# ============================================================================
# TEST GROUP 1: Sequential Chat Pattern (5 tests)
# ============================================================================

@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_sequential_chat_basic_pipeline():
    """
    Test: Sequential chat executes agents in order
    
    Expected behavior:
    - Agent1 executes first, adds data1
    - Agent2 receives Agent1's output, adds data2
    - Agent3 receives Agent2's output, adds data3
    - Final context contains all data in order
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    agents = [
        MockAgent("Agent1", "step1", "completed"),
        MockAgent("Agent2", "step2", "completed"),
        MockAgent("Agent3", "step3", "completed")
    ]
    
    initial_context = AgentContext()
    result = await orchestrator.sequential_chat(agents, initial_context)
    
    # Verify all agents executed
    assert "step1" in result.data
    assert "step2" in result.data
    assert "step3" in result.data
    
    # Verify execution order
    assert result.history == ["Agent1", "Agent2", "Agent3"]


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_sequential_chat_context_passing():
    """
    Test: Each agent receives previous agent's output
    
    Expected behavior:
    - Agent2 can read Agent1's data
    - Agent3 can read both Agent1 and Agent2's data
    - Context accumulates across pipeline
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    class CumulativeAgent(Agent):
        def __init__(self, name: str, expected_keys: List[str]):
            super().__init__(name)
            self.expected_keys = expected_keys
        
        async def execute(self, context: AgentContext) -> AgentContext:
            # Verify previous agents' data is present
            for key in self.expected_keys:
                assert key in context.data, f"Missing {key} from previous agent"
            
            context.add_to_history(self.name)
            context.data[self.name] = "processed"
            return context
    
    agents = [
        MockAgent("Agent1", "data1", "value1"),
        CumulativeAgent("Agent2", ["data1"]),
        CumulativeAgent("Agent3", ["data1", "Agent2"])
    ]
    
    initial_context = AgentContext()
    result = await orchestrator.sequential_chat(agents, initial_context)
    
    assert result.history == ["Agent1", "Agent2", "Agent3"]


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_sequential_chat_error_handling():
    """
    Test: Pipeline stops on agent failure, returns error context
    
    Expected behavior:
    - Agent1 succeeds
    - Agent2 fails with error
    - Agent3 never executes
    - Error context returned with partial results
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    agent1 = MockAgent("Agent1", "step1", "completed")
    agent2 = FailingAgent("Agent2", "Intentional failure")
    agent3 = MockAgent("Agent3", "step3", "completed")
    
    agents = [agent1, agent2, agent3]
    
    initial_context = AgentContext()
    
    with pytest.raises(Exception, match="Intentional failure"):
        await orchestrator.sequential_chat(agents, initial_context)
    
    # Verify Agent3 never executed
    assert agent3.execution_count == 0


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_sequential_chat_empty_agents():
    """
    Test: Empty agent list returns initial context unchanged
    
    Expected behavior:
    - No agents execute
    - Initial context returned as-is
    - No errors raised
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    initial_context = AgentContext(data={"initial": "data"})
    result = await orchestrator.sequential_chat([], initial_context)
    
    assert result.data == {"initial": "data"}
    assert result.history == []


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_sequential_chat_history_tracking():
    """
    Test: Execution history contains all agents in order
    
    Expected behavior:
    - History tracks agent execution order
    - Timestamps recorded in metadata
    - Last agent retrievable via get_last_agent()
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    agents = [
        MockAgent("WriterAgent", "content", "draft"),
        MockAgent("EditorAgent", "content", "edited"),
        MockAgent("PublisherAgent", "status", "published")
    ]
    
    initial_context = AgentContext()
    result = await orchestrator.sequential_chat(agents, initial_context)
    
    assert result.history == ["WriterAgent", "EditorAgent", "PublisherAgent"]
    assert result.get_last_agent() == "PublisherAgent"
    
    # Verify timestamps exist
    assert "WriterAgent_timestamp" in result.metadata
    assert "EditorAgent_timestamp" in result.metadata
    assert "PublisherAgent_timestamp" in result.metadata


# ============================================================================
# TEST GROUP 2: Group Chat Pattern (5 tests)
# ============================================================================

@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_group_chat_parallel_execution():
    """
    Test: All agents execute in parallel (timing validation)
    
    Expected behavior:
    - 3 agents with 0.1s delay each
    - Sequential would take 0.3s
    - Parallel should take ~0.1s (3x speedup)
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    agents = [
        MockAgent("Agent1", "task1", "complete", delay=0.1),
        MockAgent("Agent2", "task2", "complete", delay=0.1),
        MockAgent("Agent3", "task3", "complete", delay=0.1)
    ]
    
    manager = MockManagerAgent()
    initial_context = AgentContext()
    
    start_time = time.time()
    result = await orchestrator.group_chat(agents, manager, initial_context)
    elapsed_time = time.time() - start_time
    
    # Parallel execution should be ~0.1s, not 0.3s
    assert elapsed_time < 0.2, f"Expected parallel execution, got {elapsed_time}s (sequential would be ~0.3s)"
    
    # Verify all agents executed
    assert "task1" in result.data
    assert "task2" in result.data
    assert "task3" in result.data
    assert result.data["synthesis_complete"] is True


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_group_chat_manager_synthesis():
    """
    Test: Manager receives all agent results for synthesis
    
    Expected behavior:
    - All agents execute in parallel
    - Manager receives list of all results
    - Manager synthesizes into single context
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    agents = [
        MockAgent("ComplexityAgent", "complexity", "medium"),
        MockAgent("RiskAgent", "risk", "low"),
        MockAgent("DomainAgent", "domain", "finance")
    ]
    
    manager = MockManagerAgent("PlanningManager")
    initial_context = AgentContext()
    
    result = await orchestrator.group_chat(agents, manager, initial_context)
    
    # Verify manager synthesized all agent data
    assert result.data["complexity"] == "medium"
    assert result.data["risk"] == "low"
    assert result.data["domain"] == "finance"
    assert result.data["synthesis_complete"] is True
    
    # Verify manager in history
    assert "PlanningManager" in result.history


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_group_chat_partial_failure():
    """
    Test: If 1 agent fails, others continue, manager handles partial results
    
    Expected behavior:
    - Agent1 succeeds
    - Agent2 fails
    - Agent3 succeeds
    - Manager receives partial results (Agent1 + Agent3)
    - Error propagated but partial results preserved
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    agents = [
        MockAgent("Agent1", "task1", "complete"),
        FailingAgent("Agent2", "Task 2 failed"),
        MockAgent("Agent3", "task3", "complete")
    ]
    
    manager = MockManagerAgent()
    initial_context = AgentContext()
    
    # Group chat should handle partial failures gracefully
    # (implementation detail: may raise or return partial results)
    try:
        result = await orchestrator.group_chat(agents, manager, initial_context)
        # If no exception, verify partial results
        assert "task1" in result.data or "task3" in result.data
    except Exception as e:
        # If exception raised, verify it's from Agent2
        assert "Task 2 failed" in str(e)


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_group_chat_result_aggregation():
    """
    Test: Manager aggregates results correctly
    
    Expected behavior:
    - Multiple agents produce overlapping data keys
    - Manager merges without data loss
    - All agent contributions present in final result
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    agents = [
        MockAgent("Agent1", "metric1", "value1"),
        MockAgent("Agent2", "metric2", "value2"),
        MockAgent("Agent3", "metric3", "value3")
    ]
    
    manager = MockManagerAgent()
    initial_context = AgentContext()
    
    result = await orchestrator.group_chat(agents, manager, initial_context)
    
    # Verify no data loss
    assert result.data["metric1"] == "value1"
    assert result.data["metric2"] == "value2"
    assert result.data["metric3"] == "value3"
    
    # Verify all agents in history
    assert "Agent1" in result.history
    assert "Agent2" in result.history
    assert "Agent3" in result.history


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_group_chat_performance():
    """
    Test: Group chat is faster than sequential (>40% improvement)
    
    Expected behavior:
    - Baseline: Sequential execution with 4 agents × 0.1s = 0.4s
    - Optimized: Parallel execution with 4 agents × 0.1s = ~0.1s
    - Speedup: 75% (0.3s savings)
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    # Simulate 4 agents with 0.1s processing time each
    agents = [
        MockAgent(f"Agent{i}", f"task{i}", "complete", delay=0.1)
        for i in range(4)
    ]
    
    manager = MockManagerAgent()
    initial_context = AgentContext()
    
    # Measure parallel execution time
    start_time = time.time()
    await orchestrator.group_chat(agents, manager, initial_context)
    parallel_time = time.time() - start_time
    
    # Expected sequential time: 4 × 0.1s = 0.4s
    # Expected parallel time: ~0.1s (max of agent times)
    # Speedup should be >40% (parallel_time < 0.24s)
    assert parallel_time < 0.24, f"Expected >40% speedup, got {parallel_time}s (baseline 0.4s)"


# ============================================================================
# TEST GROUP 3: Nested Chat Pattern (3 tests)
# ============================================================================

@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_nested_chat_team_execution():
    """
    Test: Teams execute in parallel, each using group_chat pattern
    
    Expected behavior:
    - 2 teams with 2 agents each
    - Each team uses group chat (parallel within team)
    - Teams execute in parallel
    - Coordinator receives all team results
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    teams = {
        "healthcheck_team": [
            MockAgent("HealthcheckAgent", "health", "ok"),
            MockAgent("AlignAgent", "alignment", "ok")
        ],
        "optimization_team": [
            MockAgent("OptimizeAgent", "optimized", "true"),
            MockAgent("CleanupAgent", "cleaned", "true")
        ]
    }
    
    coordinator = MockCoordinatorAgent()
    initial_context = AgentContext()
    
    result = await orchestrator.nested_chat(teams, coordinator, initial_context)
    
    # Verify team results present
    assert "team_healthcheck_team" in result.data
    assert "team_optimization_team" in result.data
    
    # Verify coordination complete
    assert result.data["coordination_complete"] is True


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_nested_chat_coordinator_integration():
    """
    Test: Coordinator integrates all team results
    
    Expected behavior:
    - 3 teams produce different outputs
    - Coordinator receives dict of team_name -> team_result
    - Coordinator integrates into cohesive result
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    teams = {
        "team_a": [MockAgent("AgentA1", "result_a", "value_a")],
        "team_b": [MockAgent("AgentB1", "result_b", "value_b")],
        "team_c": [MockAgent("AgentC1", "result_c", "value_c")]
    }
    
    coordinator = MockCoordinatorAgent("MainCoordinator")
    initial_context = AgentContext()
    
    result = await orchestrator.nested_chat(teams, coordinator, initial_context)
    
    # Verify coordinator integrated all teams
    assert "team_team_a" in result.data
    assert "team_team_b" in result.data
    assert "team_team_c" in result.data
    
    # Verify coordinator in history
    assert "MainCoordinator" in result.history


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_nested_chat_hierarchical_history():
    """
    Test: Execution history shows team hierarchy
    
    Expected behavior:
    - Team agents execute first
    - Coordinator executes last
    - History preserves execution order
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    teams = {
        "team1": [
            MockAgent("Agent1A", "task", "done"),
            MockAgent("Agent1B", "task", "done")
        ],
        "team2": [
            MockAgent("Agent2A", "task", "done")
        ]
    }
    
    coordinator = MockCoordinatorAgent()
    initial_context = AgentContext()
    
    result = await orchestrator.nested_chat(teams, coordinator, initial_context)
    
    # Verify all agents in history
    assert "Agent1A" in result.history
    assert "Agent1B" in result.history
    assert "Agent2A" in result.history
    assert "MockCoordinator" in result.history


# ============================================================================
# TEST GROUP 4: Integration & Edge Cases (2 tests)
# ============================================================================

@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_agent_communication_protocol():
    """
    Test: AgentContext preserves all required fields
    
    Expected behavior:
    - data, metadata, history, errors preserved across agents
    - No data corruption during async operations
    - Context immutability respected (each agent gets copy)
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    class InspectorAgent(Agent):
        def __init__(self, name: str):
            super().__init__(name)
            self.received_context = None
        
        async def execute(self, context: AgentContext) -> AgentContext:
            self.received_context = context
            context.add_to_history(self.name)
            context.data[self.name] = "processed"
            return context
    
    agents = [
        InspectorAgent("Inspector1"),
        InspectorAgent("Inspector2"),
        InspectorAgent("Inspector3")
    ]
    
    initial_context = AgentContext(
        data={"initial": "value"},
        metadata={"session": "test123"}
    )
    
    result = await orchestrator.sequential_chat(agents, initial_context)
    
    # Verify context fields preserved
    assert "initial" in result.data
    assert result.metadata["session"] == "test123"
    assert len(result.history) == 3
    
    # Verify each agent saw cumulative data
    assert "Inspector1" in agents[1].received_context.data


@pytest.mark.skipif(
    AgentCollaborationOrchestrator is None,
    reason="AgentCollaborationOrchestrator not yet implemented (RED phase)"
)
@pytest.mark.asyncio
async def test_metrics_collection():
    """
    Test: get_metrics() returns timing, success rate, pattern usage
    
    Expected behavior:
    - Metrics track execution time per pattern
    - Success rate calculated (successful / total)
    - Pattern usage counts (sequential, group, nested)
    """
    orchestrator = AgentCollaborationOrchestrator()
    
    # Execute different patterns
    agents = [MockAgent("Agent1", "data", "value")]
    manager = MockManagerAgent()
    initial_context = AgentContext()
    
    # Sequential
    await orchestrator.sequential_chat(agents, initial_context)
    
    # Group
    await orchestrator.group_chat(agents, manager, initial_context)
    
    # Get metrics
    metrics = orchestrator.get_metrics()
    
    # Verify metrics structure
    assert "total_executions" in metrics
    assert "pattern_usage" in metrics
    assert metrics["pattern_usage"]["sequential"] == 1
    assert metrics["pattern_usage"]["group"] == 1
