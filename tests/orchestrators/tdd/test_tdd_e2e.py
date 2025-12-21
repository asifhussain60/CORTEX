"""
Tests for TDD Orchestrator v4.0 - End-to-End Workflow

Purpose: Verify complete RED→GREEN→REFACTOR cycles and orchestrator features
Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-21
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.orchestrators.tdd.tdd_orchestrator_v4 import (
    TDDOrchestratorV4,
    TDDPhase,
    ValidationResult,
    PhaseResult,
    TechnologyProfile
)


@pytest.fixture
def orchestrator(brain_connector, knowledge_graph, mcp_gateway, config):
    """Create orchestrator instance with required dependencies."""
    brain, kg, mcp, cfg = brain_connector, knowledge_graph, mcp_gateway, config
    return TDDOrchestratorV4(brain, kg, mcp, cfg)


@pytest.fixture
def full_cycle_context():
    """Create context for full TDD cycle."""
    return {
        'feature_name': 'User Registration',
        'acceptance_criteria': [
            'Users can register with email and password',
            'Email must be unique',
            'Password must be at least 8 characters'
        ],
        'project_path': Path('/mock/project')
    }


class TestTDDFullCycle:
    """Test complete RED→GREEN→REFACTOR workflows."""
    
    async def test_complete_cycle_success(self, orchestrator, full_cycle_context):
        """Test successful complete TDD cycle."""
        # Mock technology discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['FastAPI'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Mock strategies for all phases
        for phase in [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR]:
            strategy = AsyncMock()
            strategy.validate_dor.return_value = ValidationResult(passed=True)
            strategy.validate_dod.return_value = ValidationResult(passed=True)
            strategy.execute.return_value = PhaseResult(
                phase_name=phase.value,
                success=True,
                outputs={'phase_complete': True},
                metrics={'execution_time': 2.0}
            )
            orchestrator.register_strategy(phase, strategy)
        
        # Mock learning method
        orchestrator._learn_from_cycle = AsyncMock()
        
        # Execute cycle
        result = await orchestrator.execute_tdd_cycle(
            feature_name=full_cycle_context['feature_name'],
            acceptance_criteria=full_cycle_context['acceptance_criteria'],
            project_path=full_cycle_context['project_path']
        )
        
        assert result['success'] is True
        assert 'RED' in result['phases']
        assert 'GREEN' in result['phases']
        assert 'REFACTOR' in result['phases']
        assert result['feature'] == 'User Registration'
    
    async def test_cycle_failure_in_red_phase(self, orchestrator, full_cycle_context):
        """Test cycle handles RED phase failure."""
        # Mock technology discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['FastAPI'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Mock RED strategy to fail DoD
        red_strategy = AsyncMock()
        red_strategy.validate_dor.return_value = ValidationResult(passed=True)
        red_strategy.validate_dod.return_value = ValidationResult(
            passed=False,
            errors=['Tests not failing as expected']
        )
        red_strategy.execute.return_value = PhaseResult(
            phase_name='RED',
            success=True,
            outputs={},
            metrics={}
        )
        red_strategy.rollback = AsyncMock()
        orchestrator.register_strategy(TDDPhase.RED, red_strategy)
        
        # Execute cycle
        result = await orchestrator.execute_tdd_cycle(
            feature_name=full_cycle_context['feature_name'],
            acceptance_criteria=full_cycle_context['acceptance_criteria'],
            project_path=full_cycle_context['project_path']
        )
        
        assert result['success'] is False
        assert 'error' in result
        assert 'RED' in result['completed_phases'] or 'completed_phases' in result
    
    async def test_cycle_metrics_tracking(self, orchestrator, full_cycle_context):
        """Test cycle tracks metrics correctly."""
        # Mock technology discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['FastAPI'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Mock strategies
        for phase in [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR]:
            strategy = AsyncMock()
            strategy.validate_dor.return_value = ValidationResult(passed=True)
            strategy.validate_dod.return_value = ValidationResult(passed=True)
            strategy.execute.return_value = PhaseResult(
                phase_name=phase.value,
                success=True,
                outputs={},
                metrics={'execution_time': 2.5}
            )
            orchestrator.register_strategy(phase, strategy)
        
        orchestrator._learn_from_cycle = AsyncMock()
        
        initial_cycles = orchestrator.metrics['total_cycles']
        
        # Execute cycle
        result = await orchestrator.execute_tdd_cycle(
            feature_name=full_cycle_context['feature_name'],
            acceptance_criteria=full_cycle_context['acceptance_criteria'],
            project_path=full_cycle_context['project_path']
        )
        
        assert orchestrator.metrics['total_cycles'] == initial_cycles + 1
        assert 'metrics' in result
    
    async def test_phase_transition_logging(self, orchestrator, full_cycle_context, caplog):
        """Test phase transitions are logged with 🎭 pattern."""
        # Mock technology discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['FastAPI'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Mock strategies
        for phase in [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR]:
            strategy = AsyncMock()
            strategy.validate_dor.return_value = ValidationResult(passed=True)
            strategy.validate_dod.return_value = ValidationResult(passed=True)
            strategy.execute.return_value = PhaseResult(
                phase_name=phase.value,
                success=True,
                outputs={},
                metrics={}
            )
            orchestrator.register_strategy(phase, strategy)
        
        orchestrator._learn_from_cycle = AsyncMock()
        
        # Execute cycle
        await orchestrator.execute_tdd_cycle(
            feature_name=full_cycle_context['feature_name'],
            acceptance_criteria=full_cycle_context['acceptance_criteria'],
            project_path=full_cycle_context['project_path']
        )
        
        # Verify engagement hints in logs
        log_text = caplog.text
        assert '🎭' in log_text or 'Phase transition' in log_text


class TestTechnologyDiscovery:
    """Test adaptive technology discovery."""
    
    async def test_technology_discovery_triggers(self, orchestrator, full_cycle_context):
        """Test technology discovery runs at cycle start."""
        # Mock technology discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['Django'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Mock strategies
        for phase in [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR]:
            strategy = AsyncMock()
            strategy.validate_dor.return_value = ValidationResult(passed=True)
            strategy.validate_dod.return_value = ValidationResult(passed=True)
            strategy.execute.return_value = PhaseResult(
                phase_name=phase.value,
                success=True,
                outputs={},
                metrics={}
            )
            orchestrator.register_strategy(phase, strategy)
        
        orchestrator._learn_from_cycle = AsyncMock()
        
        # Execute cycle
        result = await orchestrator.execute_tdd_cycle(
            feature_name=full_cycle_context['feature_name'],
            acceptance_criteria=full_cycle_context['acceptance_criteria'],
            project_path=full_cycle_context['project_path']
        )
        
        # Verify technology discovery was called
        orchestrator.tech_discovery.discover_project_tech_stack.assert_called_once()
        assert result['tech_profile'].language == 'Python'


class TestLearningEngine:
    """Test adaptive learning from TDD cycles."""
    
    async def test_learning_from_successful_cycle(self, orchestrator, full_cycle_context):
        """Test orchestrator learns from successful cycles."""
        # Mock technology discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['FastAPI'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Mock strategies
        for phase in [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR]:
            strategy = AsyncMock()
            strategy.validate_dor.return_value = ValidationResult(passed=True)
            strategy.validate_dod.return_value = ValidationResult(passed=True)
            strategy.execute.return_value = PhaseResult(
                phase_name=phase.value,
                success=True,
                outputs={},
                metrics={'techniques': ['boundary_testing']}
            )
            orchestrator.register_strategy(phase, strategy)
        
        # Mock learning method
        orchestrator._learn_from_cycle = AsyncMock()
        
        # Execute cycle
        await orchestrator.execute_tdd_cycle(
            feature_name=full_cycle_context['feature_name'],
            acceptance_criteria=full_cycle_context['acceptance_criteria'],
            project_path=full_cycle_context['project_path']
        )
        
        # Verify learning was triggered
        orchestrator._learn_from_cycle.assert_called_once()


class TestRollbackCapability:
    """Test orchestrator rollback on failures."""
    
    async def test_rollback_on_dod_failure(self, orchestrator, full_cycle_context):
        """Test rollback triggers on DoD failure."""
        # Mock technology discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['FastAPI'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Mock RED strategy to fail DoD
        red_strategy = AsyncMock()
        red_strategy.validate_dor.return_value = ValidationResult(passed=True)
        red_strategy.validate_dod.return_value = ValidationResult(
            passed=False,
            errors=['DoD validation failed']
        )
        red_strategy.execute.return_value = PhaseResult(
            phase_name='RED',
            success=True,
            outputs={},
            metrics={}
        )
        red_strategy.rollback = AsyncMock()
        orchestrator.register_strategy(TDDPhase.RED, red_strategy)
        
        # Execute cycle
        result = await orchestrator.execute_tdd_cycle(
            feature_name=full_cycle_context['feature_name'],
            acceptance_criteria=full_cycle_context['acceptance_criteria'],
            project_path=full_cycle_context['project_path']
        )
        
        # Verify rollback was called
        red_strategy.rollback.assert_called_once()


class TestStrategyRegistration:
    """Test strategy pattern registration."""
    
    def test_register_strategy_success(self, orchestrator):
        """Test strategy registration."""
        strategy = AsyncMock()
        
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        assert 'RED' in orchestrator.strategies
        assert orchestrator.strategies['RED'] == strategy
    
    def test_register_multiple_strategies(self, orchestrator):
        """Test registering strategies for all phases."""
        strategies = {}
        
        for phase in [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR]:
            strategy = AsyncMock()
            strategies[phase] = strategy
            orchestrator.register_strategy(phase, strategy)
        
        assert len(orchestrator.strategies) == 3
        assert all(phase.value in orchestrator.strategies for phase in strategies.keys())


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
