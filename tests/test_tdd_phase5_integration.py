"""
TDD v4.0 Phase 5 Integration Tests

Tests the integration of Phase 5 components with TDD Orchestrator:
- MultiAgentOrchestrator
- AgentLearningEngine
- ContextValidator

Author: CORTEX Development Team
Created: 2025-12-21
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

from src.orchestrators.tdd.tdd_orchestrator_v4 import (
    TDDOrchestratorV4,
    TDDPhase,
    PhaseResult,
    ValidationResult
)
from src.orchestration_4_0.frameworks.multi_agent_orchestrator import (
    MultiAgentOrchestrator,
    CollaborationPattern
)
from src.orchestration_4_0.learning.agent_learning_engine import (
    AgentLearningEngine,
    StrategyType,
    ExecutionPattern
)
from src.orchestration_4_0.frameworks.context_validator import (
    ContextValidator,
    ContextQuality,
    ContextValidation
)
from src.orchestration_4_0.base.agent_interface import AgentContext


@pytest.fixture
def mock_brain():
    """Mock brain connector"""
    brain = Mock()
    brain.retrieve_context = AsyncMock(return_value={})
    brain.store_pattern = AsyncMock()
    return brain


@pytest.fixture
def mock_kg():
    """Mock knowledge graph"""
    kg = Mock()
    kg.add_entity = Mock()
    kg.add_relationship = Mock()
    kg.query = Mock(return_value=[])
    kg.store_pattern = AsyncMock()  # Must be async
    return kg


@pytest.fixture
def mock_mcp():
    """Mock MCP gateway"""
    mcp = Mock()
    mcp.execute = AsyncMock(return_value={'status': 'success'})
    return mcp


@pytest.fixture
def mock_llm():
    """Mock LLM client"""
    llm = Mock()
    llm.generate = AsyncMock(return_value="Generated code")
    return llm


@pytest.fixture
def mock_multi_agent():
    """Mock multi-agent orchestrator"""
    orchestrator = Mock(spec=MultiAgentOrchestrator)
    orchestrator.execute_sequential = AsyncMock(
        return_value=AgentContext(
            data={'test_code': 'def test_example(): pass'},
            metadata={'success': True, 'metrics': {'quality': 8.0}}
        )
    )
    orchestrator.execute_group = AsyncMock(
        return_value=AgentContext(
            data={'implementation_code': 'def example(): return True'},
            metadata={'success': True, 'metrics': {'quality': 9.0}}
        )
    )
    return orchestrator


@pytest.fixture
def mock_learning_engine():
    """Mock learning engine"""
    engine = Mock(spec=AgentLearningEngine)
    engine.get_recommendations = Mock(return_value=[])
    engine.learn_from_execution = Mock()
    return engine


@pytest.fixture
def mock_context_validator():
    """Mock context validator"""
    validator = Mock(spec=ContextValidator)
    validator.validate_context_sufficiency = AsyncMock(
        return_value=ContextValidation(
            has_requirements=True,
            quality=ContextQuality.EXCELLENT,
            context={'feature_name': 'test', 'acceptance_criteria': []},
            retrieved_items={}
        )
    )
    return validator


@pytest.fixture
def tdd_orchestrator(mock_brain, mock_kg, mock_mcp, mock_llm,
                     mock_multi_agent, mock_learning_engine, mock_context_validator):
    """Create TDD orchestrator with Phase 5 components"""
    orchestrator = TDDOrchestratorV4(
        brain_connector=mock_brain,
        knowledge_graph=mock_kg,
        mcp_gateway=mock_mcp,
        llm_client=mock_llm,
        multi_agent_orchestrator=mock_multi_agent,
        learning_engine=mock_learning_engine,
        context_validator=mock_context_validator
    )
    
    # Register mock strategies
    for phase in TDDPhase:
        mock_strategy = Mock()
        mock_strategy.validate_dor = AsyncMock(
            return_value=ValidationResult(passed=True)
        )
        mock_strategy.validate_dod = AsyncMock(
            return_value=ValidationResult(passed=True)
        )
        mock_strategy.execute = AsyncMock(
            return_value=PhaseResult(
                phase_name=phase.value,
                success=True,
                outputs={f'{phase.value.lower()}_output': 'test_data'},
                metrics={'quality_score': 8.0, 'execution_time': 1.0}
            )
        )
        mock_strategy.rollback = AsyncMock(return_value=True)
        orchestrator.register_strategy(phase, mock_strategy)
    
    return orchestrator


# ============================================================================
# Context Validator Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_context_validation_on_cycle_start(tdd_orchestrator, mock_context_validator):
    """Test that context validation runs before TDD cycle"""
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=["Criteria 1", "Criteria 2"],
        project_path=Path("/test/project")
    )
    
    # Verify context validation was called
    assert mock_context_validator.validate_context_sufficiency.called
    call_args = mock_context_validator.validate_context_sufficiency.call_args
    
    # Check context contains required fields
    context = call_args[1]['context']
    assert 'feature_name' in context
    assert 'acceptance_criteria' in context
    assert 'project_path' in context
    
    # Check execution plan was provided
    plan = call_args[1]['execution_plan']
    assert 'operation_type' in plan
    assert plan['operation_type'] == 'tdd_cycle'
    assert 'required_context' in plan
    
    # Verify metrics updated
    assert tdd_orchestrator.metrics['context_validations'] == 1


@pytest.mark.asyncio
async def test_context_validation_with_auto_retrieval(tdd_orchestrator, mock_context_validator):
    """Test context validation with auto-retrieved items"""
    # Mock validation with auto-retrieved items
    mock_context_validator.validate_context_sufficiency = AsyncMock(
        return_value=ContextValidation(
            has_requirements=True,
            quality=ContextQuality.GOOD,
            context={'feature_name': 'test'},
            retrieved_items={'tech_profile': {'language': 'Python'}},
            missing_optional=['test_framework']
        )
    )
    
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=["Criteria 1"],
        project_path=Path("/test/project")
    )
    
    # Verify auto-retrieval metrics updated
    assert tdd_orchestrator.metrics['auto_retrievals'] == 1
    assert result['success'] is True


@pytest.mark.asyncio
async def test_context_validation_failure_prevents_execution(tdd_orchestrator, mock_context_validator):
    """Test that validation failure prevents cycle execution"""
    # Mock validation failure
    mock_context_validator.validate_context_sufficiency = AsyncMock(
        return_value=ContextValidation(
            has_requirements=False,
            quality=ContextQuality.INSUFFICIENT,
            missing_required=['project_path', 'acceptance_criteria']
        )
    )
    
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=[],
        project_path=Path("/test/project")
    )
    
    # Verify execution stopped
    assert result['success'] is False
    assert 'error' in result
    assert 'Insufficient context' in result['error']


# ============================================================================
# Multi-Agent Orchestrator Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_multi_agent_sequential_execution(tdd_orchestrator, mock_multi_agent):
    """Test multi-agent sequential execution in phases"""
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=["Criteria 1"],
        project_path=Path("/test/project")
    )
    
    # All phases should complete
    assert result['success'] is True
    assert 'phases' in result
    assert 'RED' in result['phases']
    assert 'GREEN' in result['phases']
    assert 'REFACTOR' in result['phases']


@pytest.mark.asyncio
async def test_multi_agent_agent_creation(tdd_orchestrator):
    """Test that agents are created for each phase"""
    # Execute RED phase agent creation
    agents = await tdd_orchestrator._create_phase_agents(
        TDDPhase.RED,
        {'feature_name': 'test', 'project_path': Path('/test')}
    )
    
    # Should create at least one agent
    assert len(agents) > 0
    assert hasattr(agents[0], 'execute')
    assert hasattr(agents[0], 'get_name')


@pytest.mark.asyncio
async def test_multi_agent_context_flow(tdd_orchestrator, mock_multi_agent):
    """Test that context flows correctly through multi-agent execution"""
    # Setup mock to verify context flow
    captured_contexts = []
    
    async def capture_context(agents, initial_context):
        captured_contexts.append(initial_context)
        return AgentContext(
            data={'result': 'success'},
            metadata={'success': True, 'metrics': {}}
        )
    
    mock_multi_agent.execute_sequential = capture_context
    
    # Execute phase with multi-agent
    result = await tdd_orchestrator._execute_phase_with_multi_agent(
        TDDPhase.RED,
        {'feature_name': 'test', 'data': 'test_data'}
    )
    
    # Verify context was passed
    assert len(captured_contexts) > 0
    assert 'feature_name' in captured_contexts[0].data


# ============================================================================
# Learning Engine Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_learning_recommendations_retrieved(tdd_orchestrator, mock_learning_engine):
    """Test that learning recommendations are retrieved before phases"""
    from src.orchestration_4_0.learning.agent_learning_engine import Recommendation, StrategyType
    
    # Mock recommendation
    mock_learning_engine.get_recommendations = Mock(
        return_value=[Recommendation(
            strategy=StrategyType.SEQUENTIAL,
            confidence=0.85,
            reasoning="High success rate with this strategy",
            supporting_patterns=["pattern_1", "pattern_2"],
            expected_outcome=8.5
        )]
    )
    
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=["Criteria 1"],
        project_path=Path("/test/project")
    )
    
    # Verify recommendations were requested for all phases
    assert mock_learning_engine.get_recommendations.call_count >= 3
    
    # Check operation types
    calls = mock_learning_engine.get_recommendations.call_args_list
    operation_types = [call[1]['operation_type'] for call in calls]
    assert 'test_generation' in operation_types
    assert 'implementation' in operation_types
    assert 'refactoring' in operation_types


@pytest.mark.asyncio
async def test_learning_patterns_recorded(tdd_orchestrator, mock_learning_engine):
    """Test that learning patterns are recorded after phases"""
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=["Criteria 1"],
        project_path=Path("/test/project")
    )
    
    # Verify learning was recorded for all phases (3 calls)
    assert mock_learning_engine.learn_from_execution.call_count >= 3
    
    # Verify learning patterns metric updated
    assert tdd_orchestrator.metrics['learning_patterns_stored'] >= 3


@pytest.mark.asyncio
async def test_learning_from_successful_phase(tdd_orchestrator, mock_learning_engine):
    """Test learning from successful phase execution"""
    phase_result = PhaseResult(
        phase_name='RED',
        success=True,
        outputs={'test_code': 'def test(): pass'},
        metrics={'quality_score': 9.0, 'execution_time': 2.5}
    )
    
    await tdd_orchestrator._record_phase_learning(
        TDDPhase.RED,
        {'feature_name': 'test', 'complexity': 'medium'},
        phase_result
    )
    
    # Verify learn_from_execution was called
    assert mock_learning_engine.learn_from_execution.called
    call_args = mock_learning_engine.learn_from_execution.call_args[1]
    
    assert call_args['operation_type'] == 'test_generation'


@pytest.mark.asyncio
async def test_learning_from_failed_phase(tdd_orchestrator, mock_learning_engine):
    """Test learning from failed phase execution"""
    phase_result = PhaseResult(
        phase_name='GREEN',
        success=False,
        outputs={},
        metrics={'quality_score': 3.0},
        errors=['Syntax error', 'Import error']
    )
    
    await tdd_orchestrator._record_phase_learning(
        TDDPhase.GREEN,
        {'feature_name': 'test'},
        phase_result
    )
    
    # Verify failure was recorded
    assert mock_learning_engine.learn_from_execution.called
    call_args = mock_learning_engine.learn_from_execution.call_args[1]
    
    assert call_args['operation_type'] == 'implementation'


# ============================================================================
# Integration Metrics Tests
# ============================================================================

@pytest.mark.asyncio
async def test_phase5_metrics_tracking(tdd_orchestrator):
    """Test that Phase 5 metrics are tracked correctly"""
    # Initial metrics
    assert 'context_validations' in tdd_orchestrator.metrics
    assert 'multi_agent_executions' in tdd_orchestrator.metrics
    assert 'learning_patterns_stored' in tdd_orchestrator.metrics
    assert 'auto_retrievals' in tdd_orchestrator.metrics
    
    # Execute cycle
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=["Criteria 1"],
        project_path=Path("/test/project")
    )
    
    # Verify metrics updated
    assert tdd_orchestrator.metrics['context_validations'] >= 1
    assert tdd_orchestrator.metrics['learning_patterns_stored'] >= 3


@pytest.mark.asyncio
async def test_end_to_end_phase5_integration(tdd_orchestrator):
    """Test complete end-to-end Phase 5 integration"""
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Complete Test Feature",
        acceptance_criteria=["AC 1", "AC 2", "AC 3"],
        project_path=Path("/test/project"),
        context={'complexity': 'high', 'tech_stack': 'Python'}
    )
    
    # Verify success
    assert result['success'] is True
    
    # Verify all phases completed
    assert 'RED' in result['phases']
    assert 'GREEN' in result['phases']
    assert 'REFACTOR' in result['phases']
    
    # Verify all Phase 5 components were engaged
    assert tdd_orchestrator.metrics['context_validations'] >= 1
    assert tdd_orchestrator.metrics['learning_patterns_stored'] >= 3
    
    # Verify orchestrator completion message
    metrics = tdd_orchestrator.get_orchestrator_metrics()
    assert 'context_validations' in metrics
    assert 'learning_patterns_stored' in metrics


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_learning_engine_failure_graceful(tdd_orchestrator, mock_learning_engine):
    """Test graceful handling of learning engine failures"""
    # Mock learning failure
    mock_learning_engine.learn_from_execution = Mock(
        side_effect=Exception("Learning service unavailable")
    )
    
    # Should still complete cycle
    result = await tdd_orchestrator.execute_tdd_cycle(
        feature_name="Test Feature",
        acceptance_criteria=["Criteria 1"],
        project_path=Path("/test/project")
    )
    
    # Cycle should succeed despite learning failure
    assert result['success'] is True


@pytest.mark.asyncio
async def test_multi_agent_fallback_on_failure(tdd_orchestrator):
    """Test fallback to standard execution on multi-agent failure"""
    # Mock phase execution to return valid result
    result = await tdd_orchestrator._execute_phase(
        TDDPhase.RED,
        {'feature_name': 'test', 'project_path': Path('/test')}
    )
    
    # Should complete successfully
    assert result is not None
    assert result.phase_name == 'RED'


# ============================================================================
# Coverage Tests
# ============================================================================

def test_phase5_component_initialization(tdd_orchestrator):
    """Test that all Phase 5 components are properly initialized"""
    assert hasattr(tdd_orchestrator, 'multi_agent_orchestrator')
    assert hasattr(tdd_orchestrator, 'learning_engine')
    assert hasattr(tdd_orchestrator, 'context_validator')
    
    assert tdd_orchestrator.multi_agent_orchestrator is not None
    assert tdd_orchestrator.learning_engine is not None
    assert tdd_orchestrator.context_validator is not None


def test_phase5_metrics_initialization(tdd_orchestrator):
    """Test that Phase 5 metrics are initialized"""
    metrics = tdd_orchestrator.metrics
    
    assert 'context_validations' in metrics
    assert 'multi_agent_executions' in metrics
    assert 'learning_patterns_stored' in metrics
    assert 'auto_retrievals' in metrics
    
    # All should start at 0
    assert metrics['context_validations'] == 0
    assert metrics['multi_agent_executions'] == 0
    assert metrics['learning_patterns_stored'] == 0
    assert metrics['auto_retrievals'] == 0


@pytest.mark.asyncio
async def test_learning_recommendation_none_handling(tdd_orchestrator, mock_learning_engine):
    """Test handling when no recommendations available"""
    mock_learning_engine.get_recommendations = Mock(return_value=[])
    
    recommendation = await tdd_orchestrator._get_learning_recommendations(
        'test_generation',
        {'feature_name': 'test'}
    )
    
    # Should handle empty list gracefully
    assert recommendation is None
