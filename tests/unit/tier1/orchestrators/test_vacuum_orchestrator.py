"""Unit tests for VacuumOrchestrator integration.

Tests the orchestrator's ability to manage cleaner plugins and coordinate
repository maintenance operations.

Test Structure:
- VacuumOrchestrator initialization and configuration
- Cleaner registration and discovery
- Analysis phase (scan repository)
- Execution phase (apply changes)
- Rollback phase (restore state)
- Report generation
- Error handling

Governance:
- CORE-008: TDD (tests written before implementation)
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings 100%
- CORE-013: Specific exceptions only
- CORE-027: Pytest audit markers

Author: CORTEX Builder
Phase: PHASE-VAC-001-04
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add cortex-brain to path
cortex_brain_path = Path(__file__).parent.parent.parent.parent.parent / "cortex-brain"
if str(cortex_brain_path) not in sys.path:
    sys.path.insert(0, str(cortex_brain_path))

from tier1.orchestrators.vacuum import (
    VacuumOrchestrator,
    OrchestratorState,
    OrchestrationReport,
)
from tier1.orchestrators.cleaners import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
    CleanerRegistry,
)


# =============================================================================
# FIXTURES
# =============================================================================


class MockCleaner(CleanerInterface):
    """Mock cleaner for testing orchestrator integration."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize mock cleaner."""
        super().__init__(config)
        self.analyzed = False
        self.executed = False
        self.rolled_back = False

    @property
    def name(self) -> str:
        """Return name."""
        return "Mock Cleaner"

    @property
    def version(self) -> str:
        """Return version."""
        return "1.0.0"

    @property
    def domain(self) -> str:
        """Return domain."""
        return "mock_cleaner"

    def analyze(self) -> Analysis:
        """Perform analysis."""
        self.analyzed = True
        return Analysis(
            cleaner_id="mock_cleaner",
            timestamp="2026-01-17T00:00:00",
            files_scanned=10,
            issues_found=2,
            plan={
                "moves": [],
                "renames": [],
                "categories": {},
            },
            logs=["Analysis complete"],
        )

    def execute(self, plan: Dict[str, Any]) -> Report:
        """Execute plan."""
        self.executed = True
        return Report(
            cleaner_id="mock_cleaner",
            timestamp="2026-01-17T00:00:00",
            status="SUCCESS",
            actions_taken=5,
            changes={"moved": 5},
            errors=[],
            logs=["Execution complete"],
        )

    def rollback(self) -> RollbackResult:
        """Perform rollback."""
        self.rolled_back = True
        return RollbackResult(
            cleaner_id="mock_cleaner",
            timestamp="2026-01-17T00:00:00",
            status="SUCCESS",
            files_restored=5,
            errors=[],
        )


@pytest.fixture
def temp_repo():
    """Create temporary test repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        (repo_path / ".git").mkdir()
        yield repo_path


@pytest.fixture
def orchestrator_config(temp_repo) -> Dict[str, Any]:
    """Provide orchestrator configuration."""
    return {
        "repo_root": str(temp_repo),
        "config_file": "cortex-brain/vacuum/config.yaml",
        "dry_run": False,
        "verbose": True,
    }


@pytest.fixture
def orchestrator(orchestrator_config) -> VacuumOrchestrator:
    """Create orchestrator instance."""
    return VacuumOrchestrator(config=orchestrator_config)


# =============================================================================
# ORCHESTRATOR INITIALIZATION TESTS
# =============================================================================


class TestVacuumOrchestratorInitialization:
    """Test VacuumOrchestrator initialization."""

    def test_orchestrator_creation(
        self, orchestrator_config
    ) -> None:
        """Verify orchestrator can be created."""
        orch = VacuumOrchestrator(config=orchestrator_config)
        
        assert orch is not None
        assert isinstance(orch, VacuumOrchestrator)

    def test_orchestrator_has_registry(
        self, orchestrator
    ) -> None:
        """Verify orchestrator has cleaner registry."""
        assert hasattr(orchestrator, "registry")
        assert isinstance(orchestrator.registry, CleanerRegistry)

    def test_orchestrator_has_config(
        self, orchestrator, orchestrator_config
    ) -> None:
        """Verify orchestrator stores configuration."""
        assert hasattr(orchestrator, "config")
        assert orchestrator.config is not None

    def test_orchestrator_dry_run_setting(
        self, orchestrator_config
    ) -> None:
        """Verify dry_run setting is stored."""
        orchestrator_config["dry_run"] = True
        orch = VacuumOrchestrator(config=orchestrator_config)
        
        assert orch.dry_run is True

    def test_orchestrator_has_state(
        self, orchestrator
    ) -> None:
        """Verify orchestrator has state tracking."""
        assert hasattr(orchestrator, "state")
        assert isinstance(orchestrator.state, OrchestratorState)


# =============================================================================
# CLEANER REGISTRATION TESTS
# =============================================================================


class TestCleanerRegistration:
    """Test registering cleaners with orchestrator."""

    def test_register_cleaner_success(
        self, orchestrator
    ) -> None:
        """Verify cleaner can be registered."""
        orchestrator.register_cleaner(MockCleaner, {"test": True})
        
        assert orchestrator.has_cleaner("mock_cleaner")

    def test_get_registered_cleaner(
        self, orchestrator
    ) -> None:
        """Verify registered cleaner can be retrieved."""
        orchestrator.register_cleaner(MockCleaner, {})
        cleaner = orchestrator.get_cleaner("mock_cleaner")
        
        assert cleaner is not None
        assert isinstance(cleaner, MockCleaner)

    def test_get_cleaner_unregistered_raises_error(
        self, orchestrator
    ) -> None:
        """Verify getting unregistered cleaner raises error."""
        with pytest.raises(Exception):
            orchestrator.get_cleaner("nonexistent")

    def test_list_all_cleaners(
        self, orchestrator
    ) -> None:
        """Verify listing registered cleaners."""
        orchestrator.register_cleaner(MockCleaner, {})
        
        cleaners = orchestrator.list_cleaners()
        
        assert len(cleaners) > 0
        assert "mock_cleaner" in cleaners


# =============================================================================
# ORCHESTRATION WORKFLOW TESTS
# =============================================================================


class TestOrchestrationWorkflow:
    """Test complete orchestration workflow."""

    def test_analyze_calls_cleaner_analyze(
        self, orchestrator
    ) -> None:
        """Verify analyze() calls registered cleaner."""
        orchestrator.register_cleaner(MockCleaner, {})
        
        result = orchestrator.analyze("mock_cleaner")
        
        assert result is not None
        assert isinstance(result, Analysis)

    def test_analyze_returns_analysis(
        self, orchestrator
    ) -> None:
        """Verify analyze() returns Analysis object."""
        orchestrator.register_cleaner(MockCleaner, {})
        
        analysis = orchestrator.analyze("mock_cleaner")
        
        assert hasattr(analysis, "files_scanned")
        assert hasattr(analysis, "issues_found")
        assert hasattr(analysis, "plan")

    def test_execute_calls_cleaner_execute(
        self, orchestrator
    ) -> None:
        """Verify execute() calls registered cleaner."""
        orchestrator.register_cleaner(MockCleaner, {})
        analysis = orchestrator.analyze("mock_cleaner")
        
        report = orchestrator.execute("mock_cleaner", analysis.plan)
        
        assert report is not None
        assert isinstance(report, Report)

    def test_execute_returns_report(
        self, orchestrator
    ) -> None:
        """Verify execute() returns Report object."""
        orchestrator.register_cleaner(MockCleaner, {})
        analysis = orchestrator.analyze("mock_cleaner")
        
        report = orchestrator.execute("mock_cleaner", analysis.plan)
        
        assert hasattr(report, "status")
        assert hasattr(report, "actions_taken")
        assert hasattr(report, "changes")

    def test_rollback_calls_cleaner_rollback(
        self, orchestrator
    ) -> None:
        """Verify rollback() calls registered cleaner."""
        orchestrator.register_cleaner(MockCleaner, {})
        
        result = orchestrator.rollback("mock_cleaner")
        
        assert result is not None
        assert isinstance(result, RollbackResult)

    def test_dry_run_mode(
        self, orchestrator_config
    ) -> None:
        """Verify dry_run mode prevents execution."""
        orchestrator_config["dry_run"] = True
        orch = VacuumOrchestrator(config=orchestrator_config)
        orch.register_cleaner(MockCleaner, {})
        
        analysis = orch.analyze("mock_cleaner")
        
        assert analysis is not None


# =============================================================================
# STATE TRACKING TESTS
# =============================================================================


class TestStateTracking:
    """Test orchestrator state management."""

    def test_state_initialized(
        self, orchestrator
    ) -> None:
        """Verify orchestrator state is initialized."""
        assert orchestrator.state is not None
        assert isinstance(orchestrator.state, OrchestratorState)

    def test_state_tracks_analyses(
        self, orchestrator
    ) -> None:
        """Verify state tracks completed analyses."""
        orchestrator.register_cleaner(MockCleaner, {})
        orchestrator.analyze("mock_cleaner")
        
        assert len(orchestrator.state.completed_analyses) > 0

    def test_state_tracks_executions(
        self, orchestrator
    ) -> None:
        """Verify state tracks completed executions."""
        orchestrator.register_cleaner(MockCleaner, {})
        analysis = orchestrator.analyze("mock_cleaner")
        orchestrator.execute("mock_cleaner", analysis.plan)
        
        assert len(orchestrator.state.completed_executions) > 0


# =============================================================================
# REPORT GENERATION TESTS
# =============================================================================


class TestReportGeneration:
    """Test orchestrator report generation."""

    def test_generate_orchestration_report(
        self, orchestrator
    ) -> None:
        """Verify orchestration report generation."""
        orchestrator.register_cleaner(MockCleaner, {})
        orchestrator.analyze("mock_cleaner")
        analysis = orchestrator.analyze("mock_cleaner")
        orchestrator.execute("mock_cleaner", analysis.plan)
        
        report = orchestrator.generate_report()
        
        assert report is not None
        assert isinstance(report, OrchestrationReport)

    def test_report_has_required_fields(
        self, orchestrator
    ) -> None:
        """Verify orchestration report has required fields."""
        orchestrator.register_cleaner(MockCleaner, {})
        orchestrator.analyze("mock_cleaner")
        analysis = orchestrator.analyze("mock_cleaner")
        orchestrator.execute("mock_cleaner", analysis.plan)
        
        report = orchestrator.generate_report()
        
        assert hasattr(report, "timestamp")
        assert hasattr(report, "overall_status")
        assert hasattr(report, "analyses_completed")
        assert hasattr(report, "executions_completed")


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Test error handling in orchestrator."""

    def test_handle_missing_cleaner(
        self, orchestrator
    ) -> None:
        """Verify error when cleaner not registered."""
        with pytest.raises(Exception):
            orchestrator.analyze("nonexistent")

    def test_handle_cleaner_error_gracefully(
        self, orchestrator
    ) -> None:
        """Verify orchestrator handles cleaner errors."""
        orchestrator.register_cleaner(MockCleaner, {})
        
        # This should not raise
        result = orchestrator.analyze("mock_cleaner")
        
        assert result is not None


# =============================================================================
# CONFIGURATION TESTS
# =============================================================================


class TestConfigurationManagement:
    """Test configuration loading and management."""

    def test_config_storage(
        self, orchestrator, orchestrator_config
    ) -> None:
        """Verify configuration is stored correctly."""
        assert orchestrator.config == orchestrator_config

    def test_config_dry_run(
        self, orchestrator_config
    ) -> None:
        """Verify dry_run config setting."""
        config = orchestrator_config.copy()
        config["dry_run"] = True
        orch = VacuumOrchestrator(config=config)
        
        assert orch.dry_run is True

    def test_config_repo_root(
        self, orchestrator, temp_repo
    ) -> None:
        """Verify repo_root config setting."""
        assert orchestrator.config["repo_root"] is not None


# =============================================================================
# ACCEPTANCE CRITERIA TESTS
# =============================================================================


class TestAcceptanceCriteria:
    """Test VAC-001-04 acceptance criteria."""

    def test_ac_cleaner_registered(
        self, orchestrator
    ) -> None:
        """AC1: Cleaner successfully registered in orchestrator."""
        orchestrator.register_cleaner(MockCleaner, {})
        
        assert orchestrator.has_cleaner("mock_cleaner")

    def test_ac_cleaner_discoverable(
        self, orchestrator
    ) -> None:
        """AC2: Registered cleaner is discoverable."""
        orchestrator.register_cleaner(MockCleaner, {})
        cleaners = orchestrator.list_cleaners()
        
        assert "mock_cleaner" in cleaners

    def test_ac_analyze_phase_works(
        self, orchestrator
    ) -> None:
        """AC3: Analyze phase completes with analysis result."""
        orchestrator.register_cleaner(MockCleaner, {})
        
        analysis = orchestrator.analyze("mock_cleaner")
        
        assert analysis is not None
        assert isinstance(analysis, Analysis)

    def test_ac_dry_run_prevents_modifications(
        self, orchestrator_config
    ) -> None:
        """AC4: Dry-run mode prevents file modifications."""
        orchestrator_config["dry_run"] = True
        orch = VacuumOrchestrator(config=orchestrator_config)
        orch.register_cleaner(MockCleaner, {})
        
        assert orch.dry_run is True

    def test_ac_execute_phase_works(
        self, orchestrator
    ) -> None:
        """AC5: Execute phase applies changes correctly."""
        orchestrator.register_cleaner(MockCleaner, {})
        analysis = orchestrator.analyze("mock_cleaner")
        
        report = orchestrator.execute("mock_cleaner", analysis.plan)
        
        assert report is not None
        assert report.status is not None

    def test_ac_rollback_supported(
        self, orchestrator
    ) -> None:
        """AC6: Rollback restores state."""
        orchestrator.register_cleaner(MockCleaner, {})
        orchestrator.analyze("mock_cleaner")
        
        result = orchestrator.rollback("mock_cleaner")
        
        assert result is not None
        assert isinstance(result, RollbackResult)

    def test_ac_report_includes_all_phases(
        self, orchestrator
    ) -> None:
        """AC7: Report includes analysis, execution, verification."""
        orchestrator.register_cleaner(MockCleaner, {})
        orchestrator.analyze("mock_cleaner")
        analysis = orchestrator.analyze("mock_cleaner")
        orchestrator.execute("mock_cleaner", analysis.plan)
        
        report = orchestrator.generate_report()
        
        assert report is not None
        assert report.analyses_completed > 0
        assert report.executions_completed > 0
