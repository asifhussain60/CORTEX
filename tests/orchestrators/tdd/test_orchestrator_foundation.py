"""
Test orchestrator foundation for TDD v4.0

Tests:
- Orchestrator initialization
- Phase enum and dataclasses
- Engagement hints (🎭 pattern)
- Metrics tracking
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime
from src.orchestrators.tdd.tdd_orchestrator_v4 import (
    TDDPhase,
    ValidationResult,
    PhaseResult,
    TechnologyProfile,
    TDDOrchestratorV4
)

# Get CORTEX root directory
CORTEX_ROOT = Path(__file__).parent.parent.parent.parent


class TestTDDPhaseEnum:
    """Test TDD phase enumeration."""
    
    def test_phase_enum_values(self):
        """Test all TDD phases are defined."""
        assert TDDPhase.RED.value == "RED"
        assert TDDPhase.GREEN.value == "GREEN"
        assert TDDPhase.REFACTOR.value == "REFACTOR"
    
    def test_phase_enum_members(self):
        """Test phase enum has exactly 3 members."""
        assert len(TDDPhase) == 3


class TestValidationResult:
    """Test ValidationResult dataclass."""
    
    def test_validation_result_passed(self):
        """Test successful validation result."""
        result = ValidationResult(passed=True, errors=[], warnings=[])
        assert result.passed is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert result.timestamp is not None
    
    def test_validation_result_failed(self):
        """Test failed validation result with errors."""
        result = ValidationResult(
            passed=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"]
        )
        assert result.passed is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1


class TestPhaseResult:
    """Test PhaseResult dataclass."""
    
    def test_phase_result_success(self):
        """Test successful phase result."""
        result = PhaseResult(
            phase_name="RED",
            success=True,
            outputs={"test_file": "tests/test_auth.py"},
            metrics={"test_count": 5}
        )
        assert result.phase_name == "RED"
        assert result.success is True
        assert result.outputs["test_file"] == "tests/test_auth.py"
        assert result.metrics["test_count"] == 5
    
    def test_phase_result_with_git_commit(self):
        """Test phase result includes git commit SHA."""
        result = PhaseResult(
            phase_name="GREEN",
            success=True,
            outputs={},
            metrics={},
            git_commit_sha="abc123def456"
        )
        assert result.git_commit_sha == "abc123def456"


class TestTechnologyProfile:
    """Test TechnologyProfile dataclass."""
    
    def test_technology_profile_creation(self):
        """Test technology profile initialization."""
        profile = TechnologyProfile(
            language="Python",
            frameworks=["FastAPI", "Django"],
            test_frameworks=["pytest", "unittest"],
            version_info={"python": "3.11"},
            last_updated=datetime.now()
        )
        assert profile.language == "Python"
        assert len(profile.frameworks) == 2
        assert profile.confidence_score == 0.5
        assert profile.patterns_learned == 0


class TestTDDOrchestratorFoundation:
    """Test TDD orchestrator foundation."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mocked dependencies."""
        brain = Mock()
        brain.get_patterns = Mock(return_value=[])
        brain.learn_pattern = Mock(return_value=True)
        
        kg = Mock()
        kg.search = Mock(return_value=[])
        kg.search_patterns = Mock(return_value=[])  # AgentLearningEngine uses this
        kg.add_node = Mock(return_value=True)
        kg.add_relationship = Mock(return_value=True)
        kg.save_pattern = Mock(return_value=True)
        
        mcp = Mock()
        mcp.call = Mock(return_value={"status": "success"})
        
        config = {'workspace_root': Path(CORTEX_ROOT) / "".replace("/", os.sep)}
        return TDDOrchestratorV4(brain, kg, mcp, config)
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test TDD orchestrator initializes correctly."""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'execute_tdd_cycle')
        assert hasattr(orchestrator, 'brain')
        assert hasattr(orchestrator, 'kg')
        assert hasattr(orchestrator, 'mcp')
    
    def test_orchestrator_has_metrics(self, orchestrator):
        """Test orchestrator tracks metrics."""
        assert orchestrator.metrics is not None
        assert 'total_cycles' in orchestrator.metrics
        assert 'successful_cycles' in orchestrator.metrics
        assert 'patterns_learned' in orchestrator.metrics
        assert 'technologies_discovered' in orchestrator.metrics
    
    def test_orchestrator_engagement_logged(self, caplog):
        """Test orchestrator logs engagement hints (🎭 pattern)."""
        brain = Mock()
        brain.get_patterns = Mock(return_value=[])
        brain.learn_pattern = Mock(return_value=True)
        
        kg = Mock()
        kg.search = Mock(return_value=[])
        kg.search_patterns = Mock(return_value=[])
        kg.add_node = Mock(return_value=True)
        kg.add_relationship = Mock(return_value=True)
        kg.save_pattern = Mock(return_value=True)
        
        mcp = Mock()
        mcp.call = Mock(return_value={"status": "success"})
        
        config = {'workspace_root': Path(CORTEX_ROOT) / "".replace("/", os.sep)}
        TDDOrchestratorV4(brain, kg, mcp, config)
        
        # Verify engagement hint pattern in initialization
        assert any('🎭' in record.message for record in caplog.records)
    
    def test_orchestrator_strategy_registry(self, orchestrator):
        """Test orchestrator has strategy registry."""
        assert orchestrator.strategies is not None
        assert isinstance(orchestrator.strategies, dict)
    
    def test_orchestrator_technology_discovery(self, orchestrator):
        """Test orchestrator has technology discovery engine."""
        assert orchestrator.tech_discovery is not None
        assert hasattr(orchestrator.tech_discovery, 'discover_project_tech_stack')
    
    def test_orchestrator_clean_code_enforcer(self, orchestrator):
        """Test orchestrator has clean code enforcer."""
        assert orchestrator.clean_code is not None
        assert hasattr(orchestrator.clean_code, 'analyze_code_quality')
