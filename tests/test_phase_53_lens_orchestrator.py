"""
Tests for Phase 53 LENS Pipeline Orchestrator - Track 4 Part A.

Tests orchestrator initialization, stage execution, and LENS integration.

AC_START: AC-WAVE7T4-PA-TEST-001
Tests: 18 total (initialization: 3, stages: 6, pipeline: 5, integration: 4)
"""

import pytest
from cortex.orchestrators.phase_53_lens_orchestrator import (
    Phase53LENSOrchestrator,
    Phase53Config,
    Phase53Stage,
    LENSComponent,
)


class TestPhase53Initialization:
    """Tests for orchestrator initialization."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization with config."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        
        assert orchestrator is not None
        assert orchestrator.config.phase_id == "phase-53-test"
        assert orchestrator.lens_available is True
        assert orchestrator.factory_available is True

    def test_context_initialization(self):
        """Test context initialization."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        
        result = orchestrator.initialize()
        assert result is True
        assert orchestrator.context is not None
        assert orchestrator.context.current_stage == Phase53Stage.DISCOVERY

    def test_get_initial_status(self):
        """Test getting initial status."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        status = orchestrator.get_status()
        assert status["phase_id"] == "phase-53-test"
        assert status["current_stage"] == "discovery"
        assert status["lens_available"] is True


class TestPhase53StageExecution:
    """Tests for individual stage execution."""

    def test_execute_discovery_stage(self):
        """Test discovery stage execution."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert result.status == "success"
        assert result.stage_completed == Phase53Stage.DISCOVERY
        assert len(result.lens_components_used) > 0

    def test_execute_analysis_stage(self):
        """Test analysis stage execution."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        orchestrator.progress_to_next_stage()
        
        result = orchestrator.execute()
        assert result.status == "success"
        assert result.stage_completed == Phase53Stage.ANALYSIS
        assert LENSComponent.EXAMINATION in result.lens_components_used

    def test_execute_planning_stage(self):
        """Test planning stage execution."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        # Progress to planning stage
        orchestrator.progress_to_next_stage()
        orchestrator.progress_to_next_stage()
        
        result = orchestrator.execute()
        assert result.status == "success"
        assert result.stage_completed == Phase53Stage.PLANNING

    def test_execute_implementation_stage(self):
        """Test implementation stage execution."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        # Progress to implementation stage
        for _ in range(3):
            orchestrator.progress_to_next_stage()
        
        result = orchestrator.execute()
        assert result.status == "success"
        assert result.stage_completed == Phase53Stage.IMPLEMENTATION

    def test_execute_validation_stage(self):
        """Test validation stage execution."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        # Progress to validation stage
        for _ in range(4):
            orchestrator.progress_to_next_stage()
        
        result = orchestrator.execute()
        assert result.status == "success"
        assert result.stage_completed == Phase53Stage.VALIDATION

    def test_execute_deployment_stage(self):
        """Test deployment stage execution."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        # Progress to deployment stage
        for _ in range(5):
            orchestrator.progress_to_next_stage()
        
        result = orchestrator.execute()
        assert result.status == "success"
        assert result.stage_completed == Phase53Stage.DEPLOYMENT


class TestPhase53LENSIntegration:
    """Tests for LENS component integration."""

    def test_lens_components_activated(self):
        """Test LENS components are activated per stage."""
        config = Phase53Config(phase_id="phase-53-test", enable_lens=True)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert len(result.lens_components_used) > 0
        assert LENSComponent.LANGUAGE_ANALYZER in result.lens_components_used

    def test_discovery_activates_language_analyzer(self):
        """Test discovery stage activates language analyzer."""
        config = Phase53Config(phase_id="phase-53-test", enable_lens=True)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert LENSComponent.LANGUAGE_ANALYZER in result.lens_components_used

    def test_analysis_activates_examination(self):
        """Test analysis stage activates examination."""
        config = Phase53Config(phase_id="phase-53-test", enable_lens=True)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        orchestrator.progress_to_next_stage()
        
        result = orchestrator.execute()
        assert LENSComponent.EXAMINATION in result.lens_components_used

    def test_lens_disabled(self):
        """Test LENS can be disabled."""
        config = Phase53Config(phase_id="phase-53-test", enable_lens=False)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert len(result.lens_components_used) == 0


class TestPhase53FactoryIntegration:
    """Tests for factory orchestrator integration."""

    def test_orchestrator_chain_created(self):
        """Test orchestrator chain is created."""
        config = Phase53Config(phase_id="phase-53-test", enable_factory=True)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert len(result.orchestrators_invoked) > 0

    def test_discovery_invokes_orchestrators(self):
        """Test discovery invokes appropriate orchestrators."""
        config = Phase53Config(phase_id="phase-53-test", enable_factory=True)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert "discovery_orchestrator" in result.orchestrators_invoked
        assert "lens_orchestrator" in result.orchestrators_invoked

    def test_factory_disabled(self):
        """Test factory can be disabled."""
        config = Phase53Config(phase_id="phase-53-test", enable_factory=False)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert len(result.orchestrators_invoked) == 0

    def test_implementation_stage_orchestrators(self):
        """Test implementation stage has specific orchestrators."""
        config = Phase53Config(phase_id="phase-53-test", enable_factory=True)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        # Progress to implementation
        for _ in range(3):
            orchestrator.progress_to_next_stage()
        
        result = orchestrator.execute()
        assert "implementation_orchestrator" in result.orchestrators_invoked
        assert "refactoring_orchestrator" in result.orchestrators_invoked


class TestPhase53PipelineExecution:
    """Tests for full pipeline execution."""

    def test_progress_to_next_stage(self):
        """Test progression to next stage."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        assert orchestrator.context is not None
        assert orchestrator.context.current_stage == Phase53Stage.DISCOVERY
        orchestrator.progress_to_next_stage()
        assert orchestrator.context.current_stage == Phase53Stage.ANALYSIS

    def test_run_full_pipeline(self):
        """Test running full pipeline."""
        config = Phase53Config(phase_id="phase-53-test", max_iterations=6)
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        results = orchestrator.run_full_pipeline()
        assert len(results) == 6
        assert all(r.status == "success" for r in results)

    def test_execution_history(self):
        """Test execution history is tracked."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        orchestrator.execute()
        orchestrator.execute()
        
        assert len(orchestrator.execution_history) == 2

    def test_get_execution_summary(self):
        """Test execution summary."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        orchestrator.execute()
        orchestrator.progress_to_next_stage()
        orchestrator.execute()
        
        summary = orchestrator.get_execution_summary()
        assert summary["total_executions"] == 2
        assert summary["successful"] == 2
        assert summary["success_rate"] == 100.0


class TestPhase53OutputAndMetrics:
    """Tests for output generation and metrics."""

    def test_execution_result_contains_output(self):
        """Test execution result contains stage output."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert result.output is not None
        assert "discovered_patterns" in result.output

    def test_execution_metrics(self):
        """Test execution metrics are collected."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert "orchestrators_count" in result.metrics
        assert "lens_components_count" in result.metrics
        assert result.metrics["lens_components_count"] > 0

    def test_execution_timing(self):
        """Test execution timing is recorded."""
        config = Phase53Config(phase_id="phase-53-test")
        orchestrator = Phase53LENSOrchestrator(config)
        orchestrator.initialize()
        
        result = orchestrator.execute()
        assert result.execution_time >= 0
        assert result.execution_time < 1.0  # Should be very fast


# AC_COMPLETE: AC-WAVE7T4-PA-TEST-001 ✅ 18 test cases for Phase 53 orchestrator
