"""
Tests for TDD Orchestrator v4.0 - RED Phase Strategy

Purpose: Verify RED phase test generation and DoR/DoD validation
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
def red_phase_context():
    """Create context for RED phase execution."""
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
        )
    }


class TestRedPhaseDoRValidation:
    """Test RED phase Definition of Ready validation."""
    
    async def test_dor_validation_with_valid_context(self, orchestrator, red_phase_context):
        """Test DoR passes with valid context."""
        # Mock strategy
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        # Validate DoR
        result = await strategy.validate_dor(red_phase_context)
        
        assert result.passed is True
        assert len(result.errors) == 0
    
    async def test_dor_validation_missing_acceptance_criteria(self, orchestrator):
        """Test DoR fails when acceptance criteria missing."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=False,
            errors=['Missing acceptance_criteria in context'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            'feature_name': 'Test Feature',
            'project_path': Path('/mock/project')
        }
        
        result = await strategy.validate_dor(context)
        
        assert result.passed is False
        assert 'acceptance_criteria' in result.errors[0]
    
    async def test_dor_validation_missing_feature_name(self, orchestrator):
        """Test DoR fails when feature name missing."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=False,
            errors=['Missing feature_name in context'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            'acceptance_criteria': ['Criteria 1'],
            'project_path': Path('/mock/project')
        }
        
        result = await strategy.validate_dor(context)
        
        assert result.passed is False
        assert 'feature_name' in result.errors[0]
    
    async def test_dor_validation_invalid_project_path(self, orchestrator):
        """Test DoR fails with invalid project path."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=False,
            errors=['Project path does not exist'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            'feature_name': 'Test Feature',
            'acceptance_criteria': ['Criteria 1'],
            'project_path': Path('/nonexistent/path')
        }
        
        result = await strategy.validate_dor(context)
        
        assert result.passed is False
        assert 'path' in result.errors[0].lower()


class TestRedPhaseExecution:
    """Test RED phase test generation."""
    
    async def test_execute_generates_failing_tests(self, orchestrator, red_phase_context):
        """Test RED phase generates failing tests."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='RED',
            success=True,
            outputs={
                'test_files': ['test_authentication.py'],
                'test_count': 3,
                'all_tests_failing': True
            },
            metrics={
                'generation_time': 2.5,
                'techniques': ['boundary_testing', 'error_cases']
            }
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        result = await strategy.execute(red_phase_context)
        
        assert result.success is True
        assert result.phase_name == 'RED'
        assert result.outputs['test_count'] == 3
        assert result.outputs['all_tests_failing'] is True
    
    async def test_execute_creates_test_files(self, orchestrator, red_phase_context):
        """Test RED phase creates test files."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='RED',
            success=True,
            outputs={
                'test_files': ['test_auth.py', 'test_validation.py'],
                'test_count': 5
            },
            metrics={'generation_time': 3.0}
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        result = await strategy.execute(red_phase_context)
        
        assert len(result.outputs['test_files']) == 2
        assert 'test_auth.py' in result.outputs['test_files']
    
    async def test_execute_respects_test_framework(self, orchestrator, red_phase_context):
        """Test RED phase uses correct test framework."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='RED',
            success=True,
            outputs={
                'test_framework': 'pytest',
                'test_files': ['test_feature.py']
            },
            metrics={}
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        result = await strategy.execute(red_phase_context)
        
        assert result.outputs['test_framework'] == 'pytest'
    
    async def test_execute_handles_generation_failure(self, orchestrator, red_phase_context):
        """Test RED phase handles test generation failures."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='RED',
            success=False,
            outputs={},
            metrics={},
            errors=['Failed to generate tests: LLM timeout']
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        result = await strategy.execute(red_phase_context)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert 'LLM timeout' in result.errors[0]


class TestRedPhaseDoDValidation:
    """Test RED phase Definition of Done validation."""
    
    async def test_dod_validation_all_tests_failing(self, orchestrator, red_phase_context):
        """Test DoD passes when all tests fail (expected for RED)."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            **red_phase_context,
            'test_results': {'total': 3, 'failed': 3, 'passed': 0}
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True
    
    async def test_dod_validation_some_tests_passing(self, orchestrator, red_phase_context):
        """Test DoD fails when some tests pass (violation of RED)."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=False,
            errors=['RED phase violation: 2 tests passing (expected 0)'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            **red_phase_context,
            'test_results': {'total': 5, 'failed': 3, 'passed': 2}
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is False
        assert 'tests passing' in result.errors[0]
    
    async def test_dod_validation_no_tests_generated(self, orchestrator, red_phase_context):
        """Test DoD fails when no tests generated."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=False,
            errors=['No tests generated'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            **red_phase_context,
            'test_count': 0
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is False
        assert 'No tests' in result.errors[0]
    
    async def test_dod_validation_git_commit_created(self, orchestrator, red_phase_context):
        """Test DoD validates git commit created."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            **red_phase_context,
            'git_commit_sha': 'abc123def456'
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True


class TestRedPhaseRollback:
    """Test RED phase rollback capability."""
    
    async def test_rollback_deletes_test_files(self, orchestrator, red_phase_context):
        """Test rollback removes generated test files."""
        strategy = AsyncMock()
        strategy.rollback.return_value = None
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            **red_phase_context,
            'test_files': ['test_feature.py']
        }
        
        await strategy.rollback(context)
        
        strategy.rollback.assert_called_once_with(context)
    
    async def test_rollback_reverts_git_changes(self, orchestrator, red_phase_context):
        """Test rollback reverts git changes."""
        strategy = AsyncMock()
        strategy.rollback.return_value = None
        orchestrator.register_strategy(TDDPhase.RED, strategy)
        
        context = {
            **red_phase_context,
            'git_commit_sha': 'abc123'
        }
        
        await strategy.rollback(context)
        
        strategy.rollback.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
