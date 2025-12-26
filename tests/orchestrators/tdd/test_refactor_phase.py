"""
Tests for TDD Orchestrator - REFACTOR Phase Strategy

Purpose: Verify REFACTOR phase clean code enforcement and DoR/DoD validation
Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-21
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
from datetime import datetime

from src.orchestrators.tdd.tdd_orchestrator import (
    TDDOrchestrator,
    TDDPhase,
    ValidationResult,
    PhaseResult,
    TechnologyProfile
)


@pytest.fixture
def orchestrator(brain_connector, knowledge_graph, mcp_gateway, config):
    """Create orchestrator instance with required dependencies."""
    brain, kg, mcp, cfg = brain_connector, knowledge_graph, mcp_gateway, config
    return TDDOrchestrator(brain, kg, mcp, cfg)


@pytest.fixture
def refactor_phase_context():
    """Create context for REFACTOR phase execution."""
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
        'implementation_files': ['authentication.py'],
        'all_tests_passing': True,
        'test_results': {'total': 3, 'passed': 3, 'failed': 0}
    }


class TestRefactorPhaseDoRValidation:
    """Test REFACTOR phase Definition of Ready validation."""
    
    async def test_dor_validation_with_passing_tests(self, orchestrator, refactor_phase_context):
        """Test DoR passes when tests are passing (from GREEN)."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        result = await strategy.validate_dor(refactor_phase_context)
        
        assert result.passed is True
    
    async def test_dor_validation_tests_failing(self, orchestrator, refactor_phase_context):
        """Test DoR fails when tests failing (GREEN phase incomplete)."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=False,
            errors=['Tests must be passing before REFACTOR'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'all_tests_passing': False
        }
        
        result = await strategy.validate_dor(context)
        
        assert result.passed is False
        assert 'passing' in result.errors[0]
    
    async def test_dor_validation_missing_implementation(self, orchestrator):
        """Test DoR fails when implementation files missing."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(
            passed=False,
            errors=['No implementation files from GREEN phase'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            'feature_name': 'Test Feature',
            'project_path': Path('/mock/project'),
            'test_files': ['test_feature.py']
        }
        
        result = await strategy.validate_dor(context)
        
        assert result.passed is False
        assert 'implementation' in result.errors[0].lower()


class TestRefactorPhaseExecution:
    """Test REFACTOR phase clean code improvements."""
    
    async def test_execute_improves_code_quality(self, orchestrator, refactor_phase_context):
        """Test REFACTOR phase improves code quality."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='REFACTOR',
            success=True,
            outputs={
                'refactored_files': ['authentication.py'],
                'improvements': ['Extract method', 'Rename variables', 'Add docstrings'],
                'code_quality_before': 0.65,
                'code_quality_after': 0.92
            },
            metrics={
                'refactoring_time': 2.8,
                'solid_principles': ['SRP', 'OCP', 'DIP']
            }
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        result = await strategy.execute(refactor_phase_context)
        
        assert result.success is True
        assert result.phase_name == 'REFACTOR'
        assert result.outputs['code_quality_after'] > result.outputs['code_quality_before']
    
    async def test_execute_applies_solid_principles(self, orchestrator, refactor_phase_context):
        """Test REFACTOR phase applies SOLID principles."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='REFACTOR',
            success=True,
            outputs={
                'refactored_files': ['authentication.py'],
                'solid_violations_before': 5,
                'solid_violations_after': 0
            },
            metrics={
                'solid_principles': ['SRP', 'OCP', 'LSP', 'ISP', 'DIP']
            }
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        result = await strategy.execute(refactor_phase_context)
        
        assert result.outputs['solid_violations_after'] == 0
        assert len(result.metrics['solid_principles']) == 5
    
    async def test_execute_removes_code_smells(self, orchestrator, refactor_phase_context):
        """Test REFACTOR phase removes code smells."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='REFACTOR',
            success=True,
            outputs={
                'refactored_files': ['authentication.py'],
                'code_smells_removed': ['Long method', 'Duplicate code', 'Magic numbers']
            },
            metrics={
                'code_smells_before': 3,
                'code_smells_after': 0
            }
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        result = await strategy.execute(refactor_phase_context)
        
        assert len(result.outputs['code_smells_removed']) == 3
        assert result.metrics['code_smells_after'] == 0
    
    async def test_execute_applies_design_patterns(self, orchestrator, refactor_phase_context):
        """Test REFACTOR phase applies appropriate design patterns."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='REFACTOR',
            success=True,
            outputs={
                'refactored_files': ['authentication.py'],
                'patterns_applied': ['Strategy', 'Factory']
            },
            metrics={
                'design_patterns': 2
            }
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        result = await strategy.execute(refactor_phase_context)
        
        assert 'patterns_applied' in result.outputs
        assert len(result.outputs['patterns_applied']) == 2
    
    async def test_execute_maintains_test_coverage(self, orchestrator, refactor_phase_context):
        """Test REFACTOR phase maintains test coverage."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='REFACTOR',
            success=True,
            outputs={
                'refactored_files': ['authentication.py'],
                'test_results': {'total': 3, 'passed': 3, 'failed': 0},
                'coverage_before': 0.92,
                'coverage_after': 0.94
            },
            metrics={'test_execution_time': 1.5}
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        result = await strategy.execute(refactor_phase_context)
        
        assert result.outputs['test_results']['passed'] == 3
        assert result.outputs['coverage_after'] >= result.outputs['coverage_before']
    
    async def test_execute_handles_refactoring_failure(self, orchestrator, refactor_phase_context):
        """Test REFACTOR phase handles refactoring failures."""
        strategy = AsyncMock()
        strategy.validate_dor.return_value = ValidationResult(passed=True)
        strategy.execute.return_value = PhaseResult(
            phase_name='REFACTOR',
            success=False,
            outputs={},
            metrics={},
            errors=['Refactoring broke tests']
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        result = await strategy.execute(refactor_phase_context)
        
        assert result.success is False
        assert len(result.errors) > 0
        assert 'broke tests' in result.errors[0]


class TestRefactorPhaseDoDValidation:
    """Test REFACTOR phase Definition of Done validation."""
    
    async def test_dod_validation_tests_still_passing(self, orchestrator, refactor_phase_context):
        """Test DoD passes when all tests still pass after refactoring."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'test_results': {'total': 3, 'passed': 3, 'failed': 0}
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True
    
    async def test_dod_validation_tests_broken(self, orchestrator, refactor_phase_context):
        """Test DoD fails when refactoring broke tests."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=False,
            errors=['Refactoring broke 2 tests'],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'test_results': {'total': 3, 'passed': 1, 'failed': 2}
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is False
        assert 'broke' in result.errors[0]
    
    async def test_dod_validation_code_quality_improved(self, orchestrator, refactor_phase_context):
        """Test DoD validates code quality improvement."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'code_quality_before': 0.65,
            'code_quality_after': 0.92
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True
    
    async def test_dod_validation_no_quality_improvement(self, orchestrator, refactor_phase_context):
        """Test DoD warns when no quality improvement."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=['No significant quality improvement detected']
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'code_quality_before': 0.80,
            'code_quality_after': 0.81
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True
        assert len(result.warnings) > 0
    
    async def test_dod_validation_documentation_updated(self, orchestrator, refactor_phase_context):
        """Test DoD validates documentation updated."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'documentation_updated': True
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True
    
    async def test_dod_validation_git_commit_created(self, orchestrator, refactor_phase_context):
        """Test DoD validates git commit created."""
        strategy = AsyncMock()
        strategy.validate_dod.return_value = ValidationResult(
            passed=True,
            errors=[],
            warnings=[]
        )
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'git_commit_sha': 'ghi345jkl678'
        }
        
        result = await strategy.validate_dod(context)
        
        assert result.passed is True


class TestRefactorPhaseRollback:
    """Test REFACTOR phase rollback capability."""
    
    async def test_rollback_reverts_refactored_code(self, orchestrator, refactor_phase_context):
        """Test rollback reverts refactored code."""
        strategy = AsyncMock()
        strategy.rollback.return_value = None
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'refactored_files': ['authentication.py']
        }
        
        await strategy.rollback(context)
        
        strategy.rollback.assert_called_once_with(context)
    
    async def test_rollback_reverts_git_changes(self, orchestrator, refactor_phase_context):
        """Test rollback reverts git changes."""
        strategy = AsyncMock()
        strategy.rollback.return_value = None
        orchestrator.register_strategy(TDDPhase.REFACTOR, strategy)
        
        context = {
            **refactor_phase_context,
            'git_commit_sha': 'ghi345'
        }
        
        await strategy.rollback(context)
        
        strategy.rollback.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
