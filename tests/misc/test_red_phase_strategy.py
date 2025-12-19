"""
Unit Tests for RED Phase Strategy

Tests test generation, edge case analysis, and DoR/DoD validation.

Version: 4.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.orchestrators.tdd.strategies import REDPhaseStrategy
from src.orchestrators.tdd import ValidationResult, PhaseResult, TechnologyProfile


@pytest.fixture
def mock_dependencies():
    """Create mock dependencies."""
    mcp = Mock()
    mcp.call_tool = AsyncMock(return_value={'status': 'success'})
    
    brain = Mock()
    brain.query = AsyncMock(return_value=[])
    
    kg = Mock()
    kg.store_pattern = AsyncMock(return_value=None)
    kg.query_patterns = AsyncMock(return_value=[])
    
    tech_discovery = Mock()
    tech_discovery.get_best_practices = AsyncMock(return_value={
        'recommendations': ['Use type hints', 'Write docstrings']
    })
    
    return mcp, brain, kg, tech_discovery


@pytest.fixture
def red_strategy(mock_dependencies):
    """Create RED phase strategy."""
    mcp, brain, kg, tech_discovery = mock_dependencies
    return REDPhaseStrategy(mcp, brain, kg, tech_discovery)


@pytest.fixture
def valid_context():
    """Create valid context for RED phase."""
    return {
        'feature_name': 'User Authentication',
        'acceptance_criteria': ['Users can login', 'Passwords hashed'],
        'project_path': Path('./test-project'),
        'tech_profile': TechnologyProfile(
            language='Python',
            frameworks=['Django'],
            test_frameworks=['pytest'],
            version_info={'Python': '3.11'},
            last_updated=datetime.now()
        )
    }


class TestREDPhaseDoR:
    """Test RED phase DoR validation."""
    
    @pytest.mark.asyncio
    async def test_dor_valid(self, red_strategy, valid_context):
        """Test DoR passes with valid context."""
        result = await red_strategy.validate_dor(valid_context)
        assert result.passed is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_dor_missing_feature_name(self, red_strategy, valid_context):
        """Test DoR fails without feature name."""
        invalid_context = {**valid_context, 'feature_name': None}
        result = await red_strategy.validate_dor(invalid_context)
        assert result.passed is False
        assert len(result.errors) > 0
        # Check for error message (case-insensitive)
        assert any(e and 'feature' in e.lower() for e in result.errors if e is not None)
    
    @pytest.mark.asyncio
    async def test_dor_missing_acceptance_criteria(self, red_strategy, valid_context):
        """Test DoR fails without acceptance criteria."""
        invalid_context = {**valid_context, 'acceptance_criteria': None}
        result = await red_strategy.validate_dor(invalid_context)
        assert result.passed is False


class TestREDPhaseExecution:
    """Test RED phase execution."""
    
    @pytest.mark.asyncio
    async def test_execute_success(self, red_strategy, valid_context):
        """Test successful RED phase execution."""
        result = await red_strategy.execute(valid_context)
        
        assert isinstance(result, PhaseResult)
        assert result.success is True
        assert result.phase_name == 'RED'
        assert 'test_file' in result.outputs
        assert 'test_count' in result.outputs
    
    @pytest.mark.asyncio
    async def test_edge_case_extraction(self, red_strategy):
        """Test edge case extraction."""
        feature_analysis = {
            'boundaries': {'min_value': 0, 'max_value': 100}
        }
        
        edge_cases = await red_strategy._extract_edge_cases(feature_analysis)
        
        assert len(edge_cases) > 0
        assert any(ec['type'] == 'null' for ec in edge_cases)
        assert any(ec['type'] == 'empty' for ec in edge_cases)


class TestREDPhaseDoD:
    """Test RED phase DoD validation."""
    
    @pytest.mark.asyncio
    async def test_dod_valid(self, red_strategy):
        """Test DoD passes with valid outputs."""
        context = {
            'test_file': './tests/test_feature.py',
            'tests_failing': 5,
            'tests_passing': 0,
            'git_commit_sha': 'abc123',
            'documentation_updated': True,
            'edge_cases': [{'type': 'null'}]
        }
        
        # Create mock file
        Path(context['test_file']).parent.mkdir(parents=True, exist_ok=True)
        Path(context['test_file']).write_text('# test')
        
        result = await red_strategy.validate_dod(context)
        assert result.passed is True
        
        # Cleanup
        Path(context['test_file']).unlink()
    
    @pytest.mark.asyncio
    async def test_dod_tests_passing_violation(self, red_strategy):
        """Test DoD fails if tests are passing (RED violation)."""
        context = {
            'test_file': './tests/test_feature.py',
            'tests_failing': 3,
            'tests_passing': 2,  # Should be 0 in RED phase
            'git_commit_sha': 'abc123'
        }
        
        result = await red_strategy.validate_dod(context)
        assert result.passed is False
        assert any('passing' in e.lower() for e in result.errors)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
