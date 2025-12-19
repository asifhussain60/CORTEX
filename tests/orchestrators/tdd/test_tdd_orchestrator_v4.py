"""
Unit Tests for TDD Orchestrator v4.0

Tests the core orchestrator functionality, technology discovery, and clean code enforcement.

Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.orchestrators.tdd import (
    TDDOrchestratorV4,
    TechnologyDiscoveryEngine,
    CleanCodeEnforcer,
    TDDPhase,
    PhaseResult,
    ValidationResult,
    TechnologyProfile
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_brain_connector():
    """Mock brain connector."""
    mock = Mock()
    mock.query = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_knowledge_graph():
    """Mock knowledge graph."""
    mock = Mock()
    mock.store_pattern = AsyncMock(return_value=None)
    mock.query_patterns = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_mcp_gateway():
    """Mock MCP gateway."""
    mock = Mock()
    mock.call_tool = AsyncMock(return_value={'status': 'success'})
    return mock


@pytest.fixture
def orchestrator(mock_brain_connector, mock_knowledge_graph, mock_mcp_gateway):
    """Create orchestrator instance."""
    return TDDOrchestratorV4(
        brain_connector=mock_brain_connector,
        knowledge_graph=mock_knowledge_graph,
        mcp_gateway=mock_mcp_gateway
    )


@pytest.fixture
def mock_strategy():
    """Mock phase strategy."""
    strategy = Mock()
    strategy.validate_dor = AsyncMock(return_value=ValidationResult(passed=True))
    strategy.execute = AsyncMock(return_value=PhaseResult(
        phase_name='TEST',
        success=True,
        outputs={'test': 'value'},
        metrics={'metric': 1}
    ))
    strategy.validate_dod = AsyncMock(return_value=ValidationResult(passed=True))
    strategy.rollback = AsyncMock(return_value=True)
    return strategy


# ============================================================================
# TDDOrchestratorV4 Tests
# ============================================================================

class TestTDDOrchestratorV4:
    """Test TDD orchestrator core functionality."""
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator is not None
        assert orchestrator.tech_discovery is not None
        assert orchestrator.clean_code is not None
        assert orchestrator.strategies == {}
        assert orchestrator.metrics['total_cycles'] == 0
    
    def test_register_strategy(self, orchestrator, mock_strategy):
        """Test strategy registration."""
        orchestrator.register_strategy(TDDPhase.RED, mock_strategy)
        
        assert 'RED' in orchestrator.strategies
        assert orchestrator.strategies['RED'] == mock_strategy
    
    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_success(self, orchestrator, mock_strategy):
        """Test successful TDD cycle execution."""
        # Register strategies for all phases
        orchestrator.register_strategy(TDDPhase.RED, mock_strategy)
        orchestrator.register_strategy(TDDPhase.GREEN, mock_strategy)
        orchestrator.register_strategy(TDDPhase.REFACTOR, mock_strategy)
        
        # Mock tech discovery
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=['Django'],
            test_frameworks=['pytest'],
            version_info={'Python': '3.11'},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        # Execute cycle
        result = await orchestrator.execute_tdd_cycle(
            feature_name='Test Feature',
            acceptance_criteria=['Criterion 1', 'Criterion 2'],
            project_path=Path('./test-project')
        )
        
        assert result['success'] is True
        assert result['feature'] == 'Test Feature'
        assert 'RED' in result['phases']
        assert 'GREEN' in result['phases']
        assert 'REFACTOR' in result['phases']
        assert orchestrator.metrics['total_cycles'] == 1
        assert orchestrator.metrics['successful_cycles'] == 1
    
    @pytest.mark.asyncio
    async def test_execute_tdd_cycle_dor_failure(self, orchestrator, mock_strategy):
        """Test TDD cycle with DoR failure."""
        # Make DoR fail
        mock_strategy.validate_dor = AsyncMock(
            return_value=ValidationResult(
                passed=False,
                errors=['DoR validation failed']
            )
        )
        
        orchestrator.register_strategy(TDDPhase.RED, mock_strategy)
        orchestrator.register_strategy(TDDPhase.GREEN, mock_strategy)
        orchestrator.register_strategy(TDDPhase.REFACTOR, mock_strategy)
        
        tech_profile = TechnologyProfile(
            language='Python',
            frameworks=[],
            test_frameworks=['pytest'],
            version_info={},
            last_updated=datetime.now()
        )
        orchestrator.tech_discovery.discover_project_tech_stack = AsyncMock(
            return_value=tech_profile
        )
        
        result = await orchestrator.execute_tdd_cycle(
            feature_name='Test Feature',
            acceptance_criteria=['Criterion 1'],
            project_path=Path('./test-project')
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_get_orchestrator_metrics(self, orchestrator):
        """Test metrics retrieval."""
        orchestrator.metrics['total_cycles'] = 10
        orchestrator.metrics['successful_cycles'] = 8
        orchestrator.metrics['patterns_learned'] = 20
        
        metrics = orchestrator.get_orchestrator_metrics()
        
        assert metrics['total_cycles'] == 10
        assert metrics['successful_cycles'] == 8
        assert metrics['success_rate'] == 0.8
        assert metrics['avg_patterns_per_cycle'] == 2.0


# ============================================================================
# TechnologyDiscoveryEngine Tests
# ============================================================================

class TestTechnologyDiscoveryEngine:
    """Test technology discovery engine."""
    
    @pytest.fixture
    def tech_discovery(self, mock_brain_connector, mock_knowledge_graph):
        """Create tech discovery engine."""
        return TechnologyDiscoveryEngine(mock_brain_connector, mock_knowledge_graph)
    
    @pytest.mark.asyncio
    async def test_discover_python_project(self, tech_discovery, tmp_path):
        """Test Python project discovery."""
        # Create Python project structure
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "requirements.txt").write_text("pytest\ndjango")
        
        profile = await tech_discovery.discover_project_tech_stack(tmp_path)
        
        assert profile.language == 'Python'
        assert 'Django' in profile.frameworks
        assert 'pytest' in profile.test_frameworks
    
    @pytest.mark.asyncio
    async def test_discover_javascript_project(self, tech_discovery, tmp_path):
        """Test JavaScript project discovery."""
        import json
        
        # Create JS project structure
        (tmp_path / "index.js").write_text("console.log('hello');")
        package_json = {
            "dependencies": {"react": "^18.0.0"},
            "devDependencies": {"jest": "^29.0.0"}
        }
        (tmp_path / "package.json").write_text(json.dumps(package_json))
        
        profile = await tech_discovery.discover_project_tech_stack(tmp_path)
        
        assert profile.language == 'JavaScript'
        assert 'React' in profile.frameworks
        assert 'jest' in profile.test_frameworks
    
    @pytest.mark.asyncio
    async def test_learn_from_patterns(self, tech_discovery, tmp_path):
        """Test pattern learning."""
        # Create minimal project
        (tmp_path / "test.py").write_text("pass")
        
        patterns_learned = await tech_discovery.learn_from_patterns(
            tmp_path,
            'test_generation',
            {'test_count': 5, 'edge_cases': 3}
        )
        
        assert patterns_learned == 1
    
    @pytest.mark.asyncio
    async def test_get_best_practices_python(self, tech_discovery):
        """Test best practices retrieval for Python."""
        best_practices = await tech_discovery.get_best_practices(
            language='Python',
            framework='Django'
        )
        
        assert best_practices['language'] == 'Python'
        assert best_practices['framework'] == 'Django'
        assert len(best_practices['recommendations']) > 0
        assert 'type hints' in best_practices['recommendations'][0].lower()


# ============================================================================
# CleanCodeEnforcer Tests
# ============================================================================

class TestCleanCodeEnforcer:
    """Test clean code enforcement."""
    
    @pytest.fixture
    def clean_code(self):
        """Create clean code enforcer."""
        return CleanCodeEnforcer()
    
    @pytest.mark.asyncio
    async def test_analyze_clean_code(self, clean_code, tmp_path):
        """Test analysis of clean code."""
        clean_file = tmp_path / "clean.py"
        clean_file.write_text("""
def add(a: int, b: int) -> int:
    '''Add two numbers.'''
    return a + b
""")
        
        report = await clean_code.analyze_code_quality(
            clean_file,
            clean_file.read_text()
        )
        
        assert report['quality_score'] >= 9.0
        assert len(report['violations']) == 0
    
    @pytest.mark.asyncio
    async def test_analyze_code_with_violations(self, clean_code, tmp_path):
        """Test analysis of code with violations."""
        dirty_file = tmp_path / "dirty.py"
        # Long function with high complexity (simulated)
        dirty_file.write_text("""
def complex_function():
    x = 1
    y = 2
    z = 3
    return x + y + z
""")
        
        report = await clean_code.analyze_code_quality(
            dirty_file,
            dirty_file.read_text()
        )
        
        assert 'quality_score' in report
        assert 'violations' in report
        assert isinstance(report['violations'], list)
    
    def test_calculate_quality_score_no_violations(self, clean_code):
        """Test quality score calculation with no violations."""
        score = clean_code._calculate_quality_score([])
        assert score == 10.0
    
    def test_calculate_quality_score_with_violations(self, clean_code):
        """Test quality score calculation with violations."""
        violations = [
            {'severity': 'critical'},
            {'severity': 'high'},
            {'severity': 'medium'}
        ]
        score = clean_code._calculate_quality_score(violations)
        assert score < 10.0
        assert score >= 0.0


# ============================================================================
# Domain Model Tests
# ============================================================================

class TestDomainModels:
    """Test domain models."""
    
    def test_validation_result_passed(self):
        """Test ValidationResult with passed validation."""
        result = ValidationResult(passed=True)
        assert result.passed is True
        assert len(result.errors) == 0
    
    def test_validation_result_failed(self):
        """Test ValidationResult with failed validation."""
        result = ValidationResult(
            passed=False,
            errors=['Error 1', 'Error 2'],
            warnings=['Warning 1']
        )
        assert result.passed is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
    
    def test_phase_result_success(self):
        """Test PhaseResult for successful phase."""
        result = PhaseResult(
            phase_name='RED',
            success=True,
            outputs={'test_file': 'test.py'},
            metrics={'test_count': 5},
            git_commit_sha='abc123'
        )
        assert result.success is True
        assert result.phase_name == 'RED'
        assert result.outputs['test_file'] == 'test.py'
        assert result.git_commit_sha == 'abc123'
    
    def test_technology_profile(self):
        """Test TechnologyProfile creation."""
        profile = TechnologyProfile(
            language='Python',
            frameworks=['Django', 'FastAPI'],
            test_frameworks=['pytest'],
            version_info={'Python': '3.11'},
            last_updated=datetime.now()
        )
        assert profile.language == 'Python'
        assert len(profile.frameworks) == 2
        assert profile.patterns_learned == 0
        assert profile.confidence_score == 0.5


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for full workflow."""
    
    @pytest.mark.asyncio
    async def test_full_red_green_refactor_cycle(self, orchestrator):
        """Test complete RED→GREEN→REFACTOR cycle."""
        # This would require more complex mocking or actual implementations
        # Placeholder for future integration test
        pass
    
    @pytest.mark.asyncio
    async def test_pattern_learning_across_cycles(self, orchestrator):
        """Test pattern learning persists across cycles."""
        # Placeholder for future integration test
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
