"""
Test Suite for TDD Orchestrator Agentic Enhancements

Phase 6 Task 6.10: Test agentic AI integration
- Multi-agent parallel test generation
- Agent learning from TDD cycles
- Context validation pre-execution
- LLM-as-judge test quality evaluation

Target: 90%+ coverage on new agentic methods
"""

import pytest
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.orchestrators.tdd.tdd_orchestrator_migrated import (
    TDDOrchestrator,
    TDDPhase,
    TechnologyProfile,
    ValidationResult,
    PhaseResult
)
from src.orchestration_4_0.frameworks.context_validator import ContextQuality
from src.orchestration_4_0.learning.agent_learning_engine import StrategyType
from src.orchestration_4_0.frameworks.agent_evaluator import (
    EvaluationResult,
    EvaluationCategory
)


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for TDD orchestrator."""
    return {
        'brain_connector': Mock(),
        'knowledge_graph': Mock(),
        'mcp_gateway': Mock()
    }


@pytest.fixture
def tech_profile():
    """Create sample technology profile."""
    return TechnologyProfile(
        language="Python",
        frameworks=["FastAPI", "SQLAlchemy"],
        test_frameworks=["pytest", "pytest-asyncio"],
        version_info={"python": "3.11"},
        last_updated=datetime.now(),
        patterns_learned=5,
        confidence_score=0.85
    )


@pytest.fixture
def tdd_orchestrator(mock_dependencies):
    """Create TDD orchestrator with agentic enhancements enabled."""
    return TDDOrchestrator(
        brain_connector=mock_dependencies['brain_connector'],
        knowledge_graph=mock_dependencies['knowledge_graph'],
        mcp_gateway=mock_dependencies['mcp_gateway'],
        config={
            'enable_multi_agent': True,
            'enable_learning': True,
            'enable_context_validation': True,
            'execution_mode': 'AUTONOMOUS'
        }
    )


@pytest.fixture
def tdd_orchestrator_no_agentic(mock_dependencies):
    """Create TDD orchestrator with agentic features disabled."""
    return TDDOrchestrator(
        brain_connector=mock_dependencies['brain_connector'],
        knowledge_graph=mock_dependencies['knowledge_graph'],
        mcp_gateway=mock_dependencies['mcp_gateway'],
        config={
            'enable_multi_agent': False,
            'enable_learning': False,
            'enable_context_validation': False
        }
    )


# ============================================================================
# TEST GROUP 1: Context Validation (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_validate_context_pre_execution_valid(tdd_orchestrator):
    """
    Test: Context validation passes with complete context
    
    Expected:
    - Returns ContextQuality.ACCEPTABLE or better
    - No errors raised
    - Metrics updated
    """
    context = {
        'feature_name': 'User Authentication',
        'acceptance_criteria': ['Login works', 'Logout works'],
        'project_path': '/test/project'
    }
    
    with patch.object(
        tdd_orchestrator.context_validator,
        'validate_context_sufficiency',
        new_callable=AsyncMock
    ) as mock_validate:
        from src.orchestration_4_0.frameworks.context_validator import ContextValidation, ContextQuality
        
        mock_validate.return_value = ContextValidation(
            has_requirements=True,
            quality=ContextQuality.GOOD
        )
        
        quality = await tdd_orchestrator.validate_context_pre_execution(context)
    
    assert quality in [ContextQuality.GOOD, ContextQuality.EXCELLENT, ContextQuality.ACCEPTABLE]
    assert tdd_orchestrator.metrics['context_validations'] == 1


@pytest.mark.asyncio
async def test_validate_context_pre_execution_missing_field(tdd_orchestrator):
    """
    Test: Context validation fails with missing required field
    
    Expected:
    - ValueError raised for missing field
    - Error message contains field name
    """
    context = {
        'feature_name': 'User Auth'
        # Missing acceptance_criteria and project_path
    }
    
    with pytest.raises(ValueError, match="Critical context missing"):
        await tdd_orchestrator.validate_context_pre_execution(context)


@pytest.mark.asyncio
async def test_validate_context_auto_retrieval_project_path(tdd_orchestrator):
    """
    Test: Auto-retrieval fills in project_path when missing
    
    Expected:
    - project_path auto-filled with current directory
    - Validation succeeds after retrieval
    """
    context = {
        'feature_name': 'User Auth',
        'acceptance_criteria': ['Works']
        # project_path missing, should be auto-retrieved
    }
    
    with patch.object(
        tdd_orchestrator.context_validator,
        'validate_context_sufficiency',
        new_callable=AsyncMock
    ) as mock_validate:
        from src.orchestration_4_0.frameworks.context_validator import ContextValidation, ContextQuality
        
        mock_validate.return_value = ContextValidation(
            has_requirements=True,
            quality=ContextQuality.ACCEPTABLE
        )
        
        quality = await tdd_orchestrator.validate_context_pre_execution(context)
    
    assert 'project_path' in context
    assert context['project_path'] == Path.cwd()
    assert quality in [ContextQuality.ACCEPTABLE, ContextQuality.GOOD]


@pytest.mark.asyncio
async def test_validate_context_disabled(tdd_orchestrator_no_agentic):
    """
    Test: Context validation disabled returns ACCEPTABLE immediately
    
    Expected:
    - No validation performed
    - ACCEPTABLE returned without checks
    - Metrics not updated
    """
    context = {}  # Empty context
    
    quality = await tdd_orchestrator_no_agentic.validate_context_pre_execution(context)
    
    from src.orchestration_4_0.frameworks.context_validator import ContextQuality
    assert quality == ContextQuality.ACCEPTABLE
    assert tdd_orchestrator_no_agentic.metrics['context_validations'] == 0


@pytest.mark.asyncio
async def test_validate_context_insufficient_quality(tdd_orchestrator):
    """
    Test: Validation fails when context quality insufficient
    
    Expected:
    - ValueError raised
    - Error message indicates insufficient quality
    """
    context = {
        'feature_name': 'User Auth',
        'acceptance_criteria': ['Works'],
        'project_path': '/test'
    }
    
    with patch.object(
        tdd_orchestrator.context_validator,
        'validate_context_sufficiency',
        new_callable=AsyncMock
    ) as mock_validate:
        from src.orchestration_4_0.frameworks.context_validator import ContextValidation, ContextQuality
        
        mock_validate.return_value = ContextValidation(
            has_requirements=False,
            missing_required=['tech_profile'],
            quality=ContextQuality.INSUFFICIENT
        )
        
        with pytest.raises(ValueError, match="Context quality insufficient"):
            await tdd_orchestrator.validate_context_pre_execution(context)


# ============================================================================
# TEST GROUP 2: Multi-Agent Parallel Test Generation (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_generate_tests_parallel_multiple_files(tdd_orchestrator, tech_profile):
    """
    Test: Parallel test generation for multiple files
    
    Expected:
    - Multi-agent execution triggered
    - All files processed
    - Metrics updated
    """
    files = ['src/auth.py', 'src/user.py', 'src/session.py']
    
    with patch.object(
        tdd_orchestrator.multi_agent,
        'execute_group',
        new_callable=AsyncMock
    ) as mock_execute:
        from src.orchestration_4_0.base.agent_interface import AgentContext
        
        result_context = AgentContext()
        result_context.data = {
            'TestGen_auth': {'tests_generated': 5, 'coverage': 85.0},
            'TestGen_user': {'tests_generated': 4, 'coverage': 82.0},
            'TestGen_session': {'tests_generated': 3, 'coverage': 78.0}
        }
        result_context.metadata = {'execution_time': 2.5}
        mock_execute.return_value = result_context
        
        result = await tdd_orchestrator.generate_tests_parallel(files, tech_profile)
    
    assert result['tests_generated'] == 12
    assert result['files_processed'] == 3
    assert tdd_orchestrator.metrics['multi_agent_executions'] == 1


@pytest.mark.asyncio
async def test_generate_tests_parallel_single_file_fallback(tdd_orchestrator, tech_profile):
    """
    Test: Single file falls back to sequential generation
    
    Expected:
    - Sequential method called instead of parallel
    - Result contains 'mode': 'sequential'
    """
    files = ['src/auth.py']
    
    result = await tdd_orchestrator.generate_tests_parallel(files, tech_profile)
    
    assert result['mode'] == 'sequential'
    assert result['files_processed'] == 1
    assert tdd_orchestrator.metrics['multi_agent_executions'] == 0


@pytest.mark.asyncio
async def test_generate_tests_parallel_disabled(tdd_orchestrator_no_agentic, tech_profile):
    """
    Test: Multi-agent disabled falls back to sequential
    
    Expected:
    - Sequential execution even with multiple files
    - No multi-agent metrics updated
    """
    files = ['src/auth.py', 'src/user.py']
    
    result = await tdd_orchestrator_no_agentic.generate_tests_parallel(files, tech_profile)
    
    assert result['mode'] == 'sequential'
    assert tdd_orchestrator_no_agentic.metrics['multi_agent_executions'] == 0


@pytest.mark.asyncio
async def test_generate_tests_parallel_agent_creation(tdd_orchestrator, tech_profile):
    """
    Test: Agents created correctly per file
    
    Expected:
    - One agent per file
    - Agent names match file stems
    - Tech profile passed to agents
    """
    files = ['src/models/auth.py', 'src/services/user.py']
    
    with patch.object(
        tdd_orchestrator.multi_agent,
        'execute_group',
        new_callable=AsyncMock
    ) as mock_execute:
        from src.orchestration_4_0.base.agent_interface import AgentContext
        
        # Capture agents argument
        result_context = AgentContext()
        result_context.data = {'TestGen_auth': {'tests_generated': 3}}
        mock_execute.return_value = result_context
        
        await tdd_orchestrator.generate_tests_parallel(files, tech_profile)
        
        # Verify agents were created
        call_args = mock_execute.call_args
        agents = call_args.kwargs['agents']
        
        assert len(agents) == 2
        assert agents[0].name == 'TestGen_auth'
        assert agents[1].name == 'TestGen_user'


@pytest.mark.asyncio
async def test_generate_tests_parallel_execution_time_tracking(tdd_orchestrator, tech_profile):
    """
    Test: Execution time tracked in results
    
    Expected:
    - execution_time present in result
    - Time value from agent context metadata
    """
    files = ['src/auth.py', 'src/user.py']
    
    with patch.object(
        tdd_orchestrator.multi_agent,
        'execute_group',
        new_callable=AsyncMock
    ) as mock_execute:
        from src.orchestration_4_0.base.agent_interface import AgentContext
        
        result_context = AgentContext()
        result_context.data = {'agent1': {'tests_generated': 2}}
        result_context.metadata = {'execution_time': 4.75}
        mock_execute.return_value = result_context
        
        result = await tdd_orchestrator.generate_tests_parallel(files, tech_profile)
    
    assert result['execution_time'] == 4.75


# ============================================================================
# TEST GROUP 3: Agent Learning from TDD Cycles (5 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_learn_from_tdd_cycle_successful(tdd_orchestrator, tech_profile):
    """
    Test: Learning from successful TDD cycle
    
    Expected:
    - Pattern learned and stored
    - Metrics updated
    - Strategy recommendation returned
    """
    tdd_orchestrator.tech_profile = tech_profile
    
    cycle_result = {
        'RED': {'outputs': {'test_count': 5}, 'metrics': {}},
        'GREEN': {'outputs': {}, 'metrics': {'complexity': 3}},
        'REFACTOR': {'outputs': {}, 'metrics': {'final_quality_score': 0.92}}
    }
    
    with patch.object(
        tdd_orchestrator.learning_engine,
        'learn_from_execution',
        return_value=Mock(pattern_id="tdd_001")
    ) as mock_learn, \
    patch.object(
        tdd_orchestrator.learning_engine,
        'get_recommendations',
        return_value=[Mock(strategy=StrategyType.SEQUENTIAL, confidence=0.85)]
    ):
        strategy = await tdd_orchestrator.learn_from_tdd_cycle(
            cycle_result=cycle_result,
            cycle_success=True,
            cycle_duration=15.5,
            tokens_used=850
        )
    
    assert strategy == StrategyType.SEQUENTIAL
    assert tdd_orchestrator.metrics['patterns_learned'] == 1
    assert tdd_orchestrator.metrics['learning_recommendations'] == 1


@pytest.mark.asyncio
async def test_learn_from_tdd_cycle_failed(tdd_orchestrator, tech_profile):
    """
    Test: Learning from failed TDD cycle
    
    Expected:
    - Pattern still learned (negative example)
    - Success=False passed to learning engine
    """
    tdd_orchestrator.tech_profile = tech_profile
    
    cycle_result = {
        'RED': {'outputs': {'test_count': 3}, 'metrics': {}},
        'GREEN': {'outputs': {}, 'metrics': {'complexity': 5}},
        'REFACTOR': {'outputs': {}, 'metrics': {'final_quality_score': 0.45}}
    }
    
    with patch.object(
        tdd_orchestrator.learning_engine,
        'learn_from_execution',
        return_value=Mock(pattern_id="tdd_002")
    ) as mock_learn, \
    patch.object(
        tdd_orchestrator.learning_engine,
        'get_recommendations',
        return_value=[]
    ):
        strategy = await tdd_orchestrator.learn_from_tdd_cycle(
            cycle_result=cycle_result,
            cycle_success=False,
            cycle_duration=20.0,
            tokens_used=1200
        )
    
    assert strategy is None  # No recommendation for failed pattern
    assert tdd_orchestrator.metrics['patterns_learned'] == 1


@pytest.mark.asyncio
async def test_learn_from_tdd_cycle_disabled(tdd_orchestrator_no_agentic):
    """
    Test: Learning disabled returns None immediately
    
    Expected:
    - No learning engine called
    - None returned
    - Metrics not updated
    """
    cycle_result = {'RED': {}, 'GREEN': {}, 'REFACTOR': {}}
    
    strategy = await tdd_orchestrator_no_agentic.learn_from_tdd_cycle(
        cycle_result=cycle_result,
        cycle_success=True,
        cycle_duration=10.0,
        tokens_used=500
    )
    
    assert strategy is None
    assert tdd_orchestrator_no_agentic.metrics['patterns_learned'] == 0


@pytest.mark.asyncio
async def test_learn_from_tdd_cycle_low_confidence_recommendation(tdd_orchestrator, tech_profile):
    """
    Test: Low confidence recommendation not returned
    
    Expected:
    - Pattern learned
    - No strategy returned (confidence < 0.7)
    - Recommendation metric not updated
    """
    tdd_orchestrator.tech_profile = tech_profile
    
    cycle_result = {
        'RED': {'outputs': {'test_count': 2}, 'metrics': {}},
        'GREEN': {'outputs': {}, 'metrics': {'complexity': 2}},
        'REFACTOR': {'outputs': {}, 'metrics': {'final_quality_score': 0.80}}
    }
    
    with patch.object(
        tdd_orchestrator.learning_engine,
        'learn_from_execution',
        return_value=Mock(pattern_id="tdd_003")
    ), \
    patch.object(
        tdd_orchestrator.learning_engine,
        'get_recommendations',
        return_value=[Mock(strategy=StrategyType.PARALLEL, confidence=0.55)]
    ):
        strategy = await tdd_orchestrator.learn_from_tdd_cycle(
            cycle_result=cycle_result,
            cycle_success=True,
            cycle_duration=12.0,
            tokens_used=600
        )
    
    assert strategy is None
    assert tdd_orchestrator.metrics['patterns_learned'] == 1
    assert tdd_orchestrator.metrics['learning_recommendations'] == 0


@pytest.mark.asyncio
async def test_determine_cycle_strategy_parallel(tdd_orchestrator):
    """
    Test: Determine strategy from cycle with parallel execution
    
    Expected:
    - StrategyType.PARALLEL returned
    """
    cycle_result = {'parallel_execution': True}
    
    strategy = tdd_orchestrator._determine_cycle_strategy(cycle_result)
    
    assert strategy == StrategyType.PARALLEL


# ============================================================================
# TEST GROUP 4: LLM-as-Judge Test Quality Evaluation (3 tests)
# ============================================================================

@pytest.mark.asyncio
async def test_evaluate_test_quality_llm_high_quality(tdd_orchestrator):
    """
    Test: LLM evaluates high-quality tests
    
    Expected:
    - Quality score > 0.8
    - All metrics present
    """
    test_code = "def test_user_login(): ..."
    impl_code = "def user_login(): ..."
    criteria = ["Login succeeds with valid credentials"]
    
    with patch.object(
        tdd_orchestrator.test_evaluator,
        'evaluate_reasoning',
        new_callable=AsyncMock,
        return_value=EvaluationResult(
            agent_name="test_generator",
            category=EvaluationCategory.REASONING,
            score=9.2,
            reasoning="High-quality tests with good coverage"
        )
    ) as mock_eval:
        metrics = await tdd_orchestrator.evaluate_test_quality_llm(
            test_code, impl_code, criteria
        )
    
    assert metrics.score > 8.0
    mock_eval.assert_called_once()


@pytest.mark.asyncio
async def test_evaluate_test_quality_llm_low_quality(tdd_orchestrator):
    """
    Test: LLM evaluates low-quality tests
    
    Expected:
    - Quality score < 0.6
    - Identifies issues
    """
    test_code = "def test(): pass"  # Minimal test
    impl_code = "def complex_function(): ..."
    criteria = ["Multiple criteria", "Edge cases covered"]
    
    with patch.object(
        tdd_orchestrator.test_evaluator,
        'evaluate_reasoning',
        new_callable=AsyncMock,
        return_value=EvaluationResult(
            agent_name="test_generator",
            category=EvaluationCategory.REASONING,
            score=4.5,
            reasoning="Minimal test with insufficient coverage"
        )
    ):
        metrics = await tdd_orchestrator.evaluate_test_quality_llm(
            test_code, impl_code, criteria
        )
    
    assert metrics.score < 6.0


@pytest.mark.asyncio
async def test_evaluate_test_quality_llm_with_tech_profile(tdd_orchestrator, tech_profile):
    """
    Test: Evaluation uses tech profile for context
    
    Expected:
    - Tech profile test framework passed to evaluator
    - Context includes implementation
    """
    tdd_orchestrator.tech_profile = tech_profile
    
    test_code = "def test_user_auth(): ..."
    impl_code = "def authenticate_user(): ..."
    criteria = ["Auth works"]
    
    with patch.object(
        tdd_orchestrator.test_evaluator,
        'evaluate_reasoning',
        new_callable=AsyncMock,
        return_value=EvaluationResult(
            agent_name="test_generator",
            category=EvaluationCategory.REASONING,
            score=8.5,
            reasoning="Good test quality with pytest framework"
        )
    ) as mock_eval:
        await tdd_orchestrator.evaluate_test_quality_llm(
            test_code, impl_code, criteria
        )
        
        # Verify context passed
        call_args = mock_eval.call_args
        input_context = call_args.kwargs['input_context']
        
        assert 'pytest' in input_context or 'test_framework' in input_context


# ============================================================================
# TEST GROUP 5: Orchestrator Metrics & Integration (4 tests)
# ============================================================================

def test_get_orchestrator_metrics_agentic_enabled(tdd_orchestrator):
    """
    Test: Metrics include agentic alignment status
    
    Expected:
    - agentic_alignment = '95%'
    - Agentic flags present
    """
    metrics = tdd_orchestrator.get_orchestrator_metrics()
    
    assert metrics['agentic_alignment'] == '95%'
    assert metrics['multi_agent_enabled'] is True
    assert metrics['learning_enabled'] is True
    assert metrics['context_validation_enabled'] is True


def test_get_orchestrator_metrics_agentic_disabled(tdd_orchestrator_no_agentic):
    """
    Test: Metrics show agentic features disabled
    
    Expected:
    - All agentic flags False
    """
    metrics = tdd_orchestrator_no_agentic.get_orchestrator_metrics()
    
    assert metrics['multi_agent_enabled'] is False
    assert metrics['learning_enabled'] is False
    assert metrics['context_validation_enabled'] is False


def test_orchestrator_initialization_agentic_components(tdd_orchestrator):
    """
    Test: Agentic components initialized correctly
    
    Expected:
    - multi_agent, learning_engine, context_validator present
    - test_evaluator initialized
    """
    assert hasattr(tdd_orchestrator, 'multi_agent')
    assert hasattr(tdd_orchestrator, 'learning_engine')
    assert hasattr(tdd_orchestrator, 'context_validator')
    assert hasattr(tdd_orchestrator, 'test_evaluator')


def test_orchestrator_metrics_tracking():
    """
    Test: New agentic metrics tracked correctly
    
    Expected:
    - multi_agent_executions counter
    - learning_recommendations counter
    - context_validations counter
    """
    mock_deps = {
        'brain_connector': Mock(),
        'knowledge_graph': Mock(),
        'mcp_gateway': Mock()
    }
    
    orchestrator = TDDOrchestrator(**mock_deps)
    
    assert 'multi_agent_executions' in orchestrator.metrics
    assert 'learning_recommendations' in orchestrator.metrics
    assert 'context_validations' in orchestrator.metrics
    assert orchestrator.metrics['multi_agent_executions'] == 0
    assert orchestrator.metrics['learning_recommendations'] == 0
    assert orchestrator.metrics['context_validations'] == 0
