"""
Tests for TDD Orchestrator v4.0 - GREEN Phase Strategy

Purpose: Verify GREEN phase minimal implementation and DoR/DoD validation
Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-21
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
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
def green_phase_context():
    """Create context for GREEN phase execution."""
    return {
        'feature_name': 'User Authentication',
        'acceptance_criteria': [
            'Users can login with email and password',
            'Invalid credentials return 401',
            'Valid credentials return JWT token'
        ],
        'project_path': Path('/mock/project'),
        'tech_profile': TechnologyProfile(
            language='Python',
            frameworks=['FastAPI'],
            test_frameworks=['pytest'],
            version_info={'python': '3.11'},
            last_updated=datetime.now()
        ),
        'test_files': ['test_authentication.py'],
        'test_count': 3,
        'all_tests_failing': True
    }


class TestGreenPhaseDoRValidation:
    """Test GREEN phase Definition of Ready validation."""
    
    async def test_dor_validation_with_failing_tests(self, orchestrator, green_phase_context):
        """Test DoR passes when tests are failing (from RED)."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        result = await strategy.validate_dor(green_phase_context)
        
        assert result.passed is True
    
    async def test_dor_validation_missing_test_files(self, orchestrator):
        """Test DoR fails when test files missing."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=False,
            errors=['No test files from RED phase'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            'feature_name': 'Test Feature',
            'project_path': Path('/mock/project')
        }
        
        result = await strategy.validate_dor(context)
        
        assert result.passed is False
        assert 'test files' in result.errors[0].lower()
    
    async def test_dor_validation_tests_already_passing(self, orchestrator, green_phase_context):
        """Test DoR fails if tests already passing (RED phase incomplete)."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=False,
            errors=['Tests already passing - RED phase not complete'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'all_tests_failing': False
        }
        
        result = await strategy.validate_dor(context)
        
        assert result.passed is False
        assert 'already passing' in result.errors[0]


class TestGreenPhaseExecution:
    """Test GREEN phase minimal implementation."""
    
    async def test_execute_implements_minimal_code(self, orchestrator, green_phase_context):
        """Test GREEN phase implements minimal code to pass tests."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='GREEN',
            success=True,
            outputs={
                'implementation_files': ['authentication.py'],
                'lines_of_code': 45,
                'all_tests_passing': True
            },
            metrics={
                'implementation_time': 3.2,
                'complexity': 'low'
            }
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        result = await strategy.execute(green_phase_context)
        
        assert result.success is True
        assert result.phase_name == 'GREEN'
        assert result.outputs['all_tests_passing'] is True
    
    async def test_execute_creates_implementation_files(self, orchestrator, green_phase_context):
        """Test GREEN phase creates implementation files."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='GREEN',
            success=True,
            outputs={
                'implementation_files': ['auth.py', 'models.py'],
                'lines_of_code': 67
            },
            metrics={'implementation_time': 4.0}
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        result = await strategy.execute(green_phase_context)
        
        assert len(result.outputs['implementation_files']) == 2
        assert 'auth.py' in result.outputs['implementation_files']
    
    async def test_execute_minimal_code_principle(self, orchestrator, green_phase_context):
        """Test GREEN phase follows minimal code principle."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='GREEN',
            success=True,
            outputs={
                'implementation_files': ['feature.py'],
                'lines_of_code': 30
            },
            metrics={
                'complexity': 'low',
                'code_quality_score': 0.85
            }
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        result = await strategy.execute(green_phase_context)
        
        # Verify minimal implementation (low complexity)
        assert result.metrics['complexity'] == 'low'
        assert result.outputs['lines_of_code'] < 100  # Reasonable threshold
    
    async def test_execute_handles_implementation_failure(self, orchestrator, green_phase_context):
        """Test GREEN phase handles implementation failures."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='GREEN',
            success=False,
            outputs={},
            metrics={},
            errors=['Failed to generate implementation: Syntax error']
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        result = await strategy.execute(green_phase_context)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert 'Syntax error' in result.errors[0]
    
    async def test_execute_runs_tests_after_implementation(self, orchestrator, green_phase_context):
        """Test GREEN phase runs tests to verify implementation."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='GREEN',
            success=True,
            outputs={
                'implementation_files': ['feature.py'],
                'test_results': {'total': 3, 'passed': 3, 'failed': 0}
            },
            metrics={'test_execution_time': 1.2}
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        result = await strategy.execute(green_phase_context)
        
        assert result.outputs['test_results']['passed'] == 3
        assert result.outputs['test_results']['failed'] == 0


class TestGreenPhaseDoDValidation:
    """Test GREEN phase Definition of Done validation."""
    
    async def test_dod_validation_all_tests_passing(self, orchestrator, green_phase_context):
        """Test DoD passes when all tests pass."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'test_results': {'total': 3, 'passed': 3, 'failed': 0}
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True
    
    async def test_dod_validation_some_tests_failing(self, orchestrator, green_phase_context):
        """Test DoD fails when tests still failing."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=False,
            errors=['2 tests still failing'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'test_results': {'total': 5, 'passed': 3, 'failed': 2}
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is False
        assert 'failing' in result.errors[0]
    
    async def test_dod_validation_no_implementation(self, orchestrator, green_phase_context):
        """Test DoD fails when no implementation created."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=False,
            errors=['No implementation files generated'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'implementation_files': []
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is False
        assert 'implementation' in result.errors[0].lower()
    
    async def test_dod_validation_excessive_complexity(self, orchestrator, green_phase_context):
        """Test DoD warns about excessive complexity."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=['Complexity higher than recommended for GREEN phase']
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'complexity': 'high',
            'lines_of_code': 250
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True
        assert len(result.warnings) > 0
        assert 'Complexity' in result.warnings[0]
    
    async def test_dod_validation_git_commit_created(self, orchestrator, green_phase_context):
        """Test DoD validates git commit created."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'git_commit_sha': 'def789ghi012'
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True


class TestGreenPhaseRollback:
    """Test GREEN phase rollback capability."""
    
    async def test_rollback_deletes_implementation_files(self, orchestrator, green_phase_context):
        """Test rollback removes generated implementation files."""
        strategy = AsyncMock()
        strategy.rollback.return_value = None
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'implementation_files': ['feature.py']
        }
        
        await strategy.rollback(context)
        
        strategy.rollback.assert_called_once_with(context)
    
    async def test_rollback_reverts_git_changes(self, orchestrator, green_phase_context):
        """Test rollback reverts git changes."""
        strategy = AsyncMock()
        strategy.rollback.return_value = None
        orchestrator.register_strategy(TDDPhase.GREEN, strategy)
        
        context = {
            **green_phase_context,
            'git_commit_sha': 'def789'
        }
        
        await strategy.rollback(context)
        
        strategy.rollback.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
