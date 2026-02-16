"""Unit Tests for LENS Intelligence Facade

Tests the unified entry point for LENS intelligence operations.

Author: CORTEX Framework
Phase: PHASE-97 S2
CORE Rules: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from cortex.lens.facade import LENSIntelligenceFacade, WorkflowType


@pytest.fixture
def facade(tmp_path: Path) -> LENSIntelligenceFacade:
    """Create LENS facade instance.
    
    Args:
        tmp_path: Pytest temporary directory
    
    Returns:
        LENSIntelligenceFacade instance
    """
    return LENSIntelligenceFacade(repo_path=tmp_path)


@pytest.fixture
def sample_path(tmp_path: Path) -> Path:
    """Create sample file for analysis.
    
    Args:
        tmp_path: Pytest temporary directory
    
    Returns:
        Path to sample file
    """
    sample_file = tmp_path / "test.py"
    sample_file.write_text("def foo(): pass")
    return sample_file


class TestLENSFacadeInitialization:
    """Test suite for facade initialization."""
    
    def test_init_default(self, tmp_path: Path) -> None:
        """Test default initialization.
        
        Args:
            tmp_path: Pytest temporary directory
        """
        facade = LENSIntelligenceFacade(repo_path=tmp_path)
        
        assert facade._cache_enabled is True
        assert facade._orchestrator is not None
        assert facade._repo_path == tmp_path
    
    def test_init_cache_disabled(self, tmp_path: Path) -> None:
        """Test initialization with cache disabled.
        
        Args:
            tmp_path: Pytest temporary directory
        """
        facade = LENSIntelligenceFacade(repo_path=tmp_path, cache_enabled=False)
        
        assert facade._cache_enabled is False


class TestRefactorWorkflow:
    """Test suite for refactor workflow."""
    
    @patch("cortex.lens.facade.LENSOrchestrator")
    def test_refactor_workflow(
        self, mock_orchestrator_class: Mock, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test refactoring workflow execution.
        
        Args:
            mock_orchestrator_class: Mock orchestrator class
            facade: LENS facade instance
            sample_path: Sample file path
        """
        # Mock orchestrator response
        mock_orch = Mock()
        mock_orch.analyze.return_value = {
            "complexity_score": 15,
            "duplicate_count": 2,
            "suggestions": ["Extract method", "Reduce complexity"],
        }
        facade._orchestrator = mock_orch
        
        result = facade.analyze(
            workflow=WorkflowType.REFACTOR,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "refactor"
        assert result["complexity_score"] == 15
        assert result["duplicate_count"] == 2
        assert len(result["suggestions"]) == 2


class TestSecurityWorkflow:
    """Test suite for security workflow."""
    
    @patch("cortex.lens.facade.LENSOrchestrator")
    def test_security_workflow(
        self, mock_orchestrator_class: Mock, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test security workflow execution.
        
        Args:
            mock_orchestrator_class: Mock orchestrator class
            facade: LENS facade instance
            sample_path: Sample file path
        """
        mock_orch = Mock()
        mock_orch.analyze.return_value = {
            "vulnerabilities": ["SQL injection risk"],
            "secrets_detected": [],
            "security_score": 85,
        }
        facade._orchestrator = mock_orch
        
        result = facade.analyze(
            workflow=WorkflowType.SECURITY,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "security"
        assert len(result["vulnerabilities"]) == 1
        assert result["security_score"] == 85


class TestImplementationWorkflow:
    """Test suite for implementation workflow."""
    
    @patch("cortex.lens.facade.LENSOrchestrator")
    def test_implementation_workflow(
        self, mock_orchestrator_class: Mock, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test implementation workflow execution.
        
        Args:
            mock_orchestrator_class: Mock orchestrator class
            facade: LENS facade instance
            sample_path: Sample file path
        """
        mock_orch = Mock()
        mock_orch.analyze.return_value = {
            "dependencies": ["numpy", "pandas"],
            "apis": ["/api/v1/users"],
            "test_coverage": 85,
        }
        facade._orchestrator = mock_orch
        
        result = facade.analyze(
            workflow=WorkflowType.IMPLEMENTATION,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "implementation"
        assert len(result["dependencies"]) == 2
        assert result["test_coverage"] == 85


class TestOnboardingWorkflow:
    """Test suite for onboarding workflow."""
    
    @patch("cortex.lens.facade.LENSOrchestrator")
    def test_onboarding_workflow(
        self, mock_orchestrator_class: Mock, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test onboarding workflow execution.
        
        Args:
            mock_orchestrator_class: Mock orchestrator class
            facade: LENS facade instance
            sample_path: Sample file path
        """
        mock_orch = Mock()
        mock_orch.analyze.return_value = {
            "tech_stack": {"language": "Python", "framework": "FastAPI"},
            "entry_points": ["main.py"],
            "documentation_score": 75,
        }
        facade._orchestrator = mock_orch
        
        result = facade.analyze(
            workflow=WorkflowType.ONBOARDING,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "onboarding"
        assert "Python" in str(result["tech_stack"])
        assert result["documentation_score"] == 75


class TestEvolutionWorkflow:
    """Test suite for evolution workflow."""
    
    def test_evolution_workflow(
        self, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test evolution workflow execution.
        
        Args:
            facade: LENS facade instance
            sample_path: Sample file path
        """
        result = facade.analyze(
            workflow=WorkflowType.EVOLUTION,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "evolution"
        assert "timeline" in result
        assert "milestones" in result


class TestDebuggingWorkflow:
    """Test suite for debugging workflow."""
    
    def test_debugging_workflow(
        self, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test debugging workflow execution.
        
        Args:
            facade: LENS facade instance
            sample_path: Sample file path
        """
        result = facade.analyze(
            workflow=WorkflowType.DEBUGGING,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "debugging"
        assert "error_patterns" in result


class TestMigrationWorkflow:
    """Test suite for migration workflow."""
    
    def test_migration_workflow(
        self, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test migration workflow execution.
        
        Args:
            facade: LENS facade instance
            sample_path: Sample file path
        """
        result = facade.analyze(
            workflow=WorkflowType.MIGRATION,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "migration"
        assert "migration_paths" in result


class TestDocumentationWorkflow:
    """Test suite for documentation workflow."""
    
    def test_documentation_workflow(
        self, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test documentation workflow execution.
        
        Args:
            facade: LENS facade instance
            sample_path: Sample file path
        """
        result = facade.analyze(
            workflow=WorkflowType.DOCUMENTATION,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "documentation"
        assert "missing_docs" in result


class TestComplianceWorkflow:
    """Test suite for compliance workflow."""
    
    def test_compliance_workflow(
        self, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test compliance workflow execution.
        
        Args:
            facade: LENS facade instance
            sample_path: Sample file path
        """
        result = facade.analyze(
            workflow=WorkflowType.COMPLIANCE,
            target_path=sample_path,
        )
        
        assert result["workflow"] == "compliance"
        assert "violations" in result
        assert result["compliance_score"] == 100


class TestErrorHandling:
    """Test suite for error handling."""
    
    def test_unsupported_workflow(
        self, facade: LENSIntelligenceFacade, sample_path: Path
    ) -> None:
        """Test error on unsupported workflow.
        
        Args:
            facade: LENS facade instance
            sample_path: Sample file path
        """
        # Create invalid workflow type
        with pytest.raises(ValueError, match="Unsupported workflow"):
            facade.analyze(
                workflow="invalid_workflow",  # type: ignore
                target_path=sample_path,
            )
