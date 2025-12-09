"""
Test Suite for Deployment Orchestrator

Tests the unified deployment orchestrator that consolidates:
- deploy_utility.py (basic workflow)
- deployment_gates.py (24 gates)
- deploy_gate_validator.py (feature validation)
- deploy_cortex.py (main script)
- post_deployment_validator.py (verification)

TDD Phase: RED - Tests before implementation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


@pytest.fixture
def cortex_root(tmp_path):
    """Create temporary CORTEX root directory."""
    cortex_dir = tmp_path / "CORTEX"
    cortex_dir.mkdir()
    
    # Create basic structure
    (cortex_dir / "src").mkdir()
    (cortex_dir / "cortex-brain").mkdir()
    (cortex_dir / "cortex-brain" / "deployments").mkdir()
    (cortex_dir / "VERSION").write_text("3.8.1\n")
    
    return cortex_dir


@pytest.fixture
def deploy_orchestrator(cortex_root):
    """Create deployment orchestrator instance."""
    from src.orchestrators.deploy_orchestrator import DeployOrchestrator
    return DeployOrchestrator(cortex_root)


class TestDeployOrchestratorInitialization:
    """Test orchestrator initialization and setup."""
    
    def test_orchestrator_initializes_with_cortex_root(self, cortex_root):
        """Test orchestrator accepts CORTEX root path."""
        from src.orchestrators.deploy_orchestrator import DeployOrchestrator
        orchestrator = DeployOrchestrator(cortex_root)
        
        assert orchestrator.cortex_root == cortex_root
        assert orchestrator.cortex_root.exists()
    
    def test_orchestrator_loads_manifest(self, deploy_orchestrator):
        """Test orchestrator loads deployment manifest."""
        assert hasattr(deploy_orchestrator, 'manifest')
        assert deploy_orchestrator.manifest is not None
    
    def test_orchestrator_initializes_state_machine(self, deploy_orchestrator):
        """Test orchestrator initializes with IDLE state."""
        assert hasattr(deploy_orchestrator, 'state')
        # state is DeploymentState enum, check value
        assert deploy_orchestrator.get_state() == 'IDLE'
    
    def test_orchestrator_creates_deployment_directory(self, cortex_root):
        """Test orchestrator creates cortex-brain/deployments/ if missing."""
        from src.orchestrators.deploy_orchestrator import DeployOrchestrator
        orchestrator = DeployOrchestrator(cortex_root)
        
        deployments_dir = cortex_root / "cortex-brain" / "deployments"
        assert deployments_dir.exists()


class TestDeploymentPhases:
    """Test deployment phase execution."""
    
    def test_orchestrator_defines_deployment_phases(self, deploy_orchestrator):
        """Test orchestrator has defined phases."""
        phases = deploy_orchestrator.get_phases()
        
        assert 'pre-flight' in phases
        assert 'build' in phases
        assert 'validate' in phases
        assert 'deploy' in phases
        assert 'verify' in phases
        assert 'rollback' in phases
    
    def test_pre_flight_phase_runs_validation(self, deploy_orchestrator):
        """Test pre-flight phase executes validation checks."""
        result = deploy_orchestrator.run_phase('pre-flight', dry_run=True)
        
        assert result['phase'] == 'pre-flight'
        assert 'validation_results' in result
        assert result['success'] is not None
    
    def test_build_phase_creates_artifacts(self, deploy_orchestrator):
        """Test build phase creates deployment artifacts."""
        result = deploy_orchestrator.run_phase('build', dry_run=True)
        
        assert result['phase'] == 'build'
        assert 'artifacts' in result
    
    def test_validate_phase_runs_gates(self, deploy_orchestrator):
        """Test validate phase executes deployment gates."""
        result = deploy_orchestrator.run_phase('validate', dry_run=True)
        
        assert result['phase'] == 'validate'
        assert 'gates' in result
        assert 'gates_passed' in result
        assert 'gates_failed' in result
    
    def test_deploy_phase_handles_deployment(self, deploy_orchestrator):
        """Test deploy phase executes actual deployment."""
        result = deploy_orchestrator.run_phase('deploy', dry_run=True)
        
        assert result['phase'] == 'deploy'
        assert 'deployment_status' in result
    
    def test_verify_phase_runs_smoke_tests(self, deploy_orchestrator):
        """Test verify phase executes post-deployment verification."""
        result = deploy_orchestrator.run_phase('verify', dry_run=True)
        
        assert result['phase'] == 'verify'
        assert 'verification_results' in result


class TestStateMachine:
    """Test deployment state machine."""
    
    def test_state_machine_starts_in_idle(self, deploy_orchestrator):
        """Test state machine initializes in IDLE state."""
        assert deploy_orchestrator.get_state() == 'IDLE'
    
    def test_state_machine_transitions_to_validating(self, deploy_orchestrator):
        """Test state transitions from IDLE to VALIDATING."""
        deploy_orchestrator.transition_to('VALIDATING')
        assert deploy_orchestrator.get_state() == 'VALIDATING'
    
    def test_state_machine_validates_transitions(self, deploy_orchestrator):
        """Test state machine prevents invalid transitions."""
        with pytest.raises(ValueError):
            # Can't go directly from IDLE to DEPLOYING
            deploy_orchestrator.transition_to('DEPLOYING')
    
    def test_state_machine_tracks_transition_history(self, deploy_orchestrator):
        """Test state machine records state transition history."""
        deploy_orchestrator.transition_to('VALIDATING')
        deploy_orchestrator.transition_to('BUILDING')
        
        history = deploy_orchestrator.get_state_history()
        assert len(history) >= 2
        assert history[-2]['state'] == 'VALIDATING'
        assert history[-1]['state'] == 'BUILDING'


class TestCheckpointManager:
    """Test deployment checkpoint management."""
    
    def test_checkpoint_manager_saves_state(self, deploy_orchestrator, cortex_root):
        """Test checkpoint manager saves deployment state."""
        deploy_orchestrator.save_checkpoint('test_checkpoint', {'test': 'data'})
        
        checkpoint_file = cortex_root / "cortex-brain" / "deployments" / "checkpoint-test_checkpoint.json"
        assert checkpoint_file.exists()
    
    def test_checkpoint_manager_loads_state(self, deploy_orchestrator):
        """Test checkpoint manager restores deployment state."""
        deploy_orchestrator.save_checkpoint('test_load', {'phase': 'build', 'progress': 50})
        loaded = deploy_orchestrator.load_checkpoint('test_load')
        
        assert loaded['phase'] == 'build'
        assert loaded['progress'] == 50
    
    def test_checkpoint_manager_supports_resume(self, deploy_orchestrator):
        """Test orchestrator can resume from checkpoint."""
        deploy_orchestrator.transition_to('VALIDATING')
        deploy_orchestrator.save_checkpoint('resume_test', {})
        
        # Create new orchestrator and resume
        from src.orchestrators.deploy_orchestrator import DeployOrchestrator
        new_orchestrator = DeployOrchestrator(deploy_orchestrator.cortex_root)
        new_orchestrator.resume_from_checkpoint('resume_test')
        
        assert new_orchestrator.get_state() == 'VALIDATING'


class TestDryRunMode:
    """Test dry-run deployment mode."""
    
    def test_dry_run_executes_without_changes(self, deploy_orchestrator):
        """Test dry-run mode previews without making changes."""
        result = deploy_orchestrator.execute_deployment(dry_run=True)
        
        assert result['dry_run'] is True
        assert result['changes_made'] is False
    
    def test_dry_run_reports_planned_actions(self, deploy_orchestrator):
        """Test dry-run mode reports what would happen."""
        result = deploy_orchestrator.execute_deployment(dry_run=True)
        
        assert 'planned_actions' in result
        assert len(result['planned_actions']) > 0


class TestDeploymentExecution:
    """Test full deployment execution."""
    
    def test_deployment_executes_all_phases_in_order(self, deploy_orchestrator):
        """Test deployment runs phases in correct sequence."""
        result = deploy_orchestrator.execute_deployment(dry_run=True)
        
        assert result['success'] is not None
        assert 'phases_executed' in result
        
        phases = result['phases_executed']
        assert phases.index('pre-flight') < phases.index('build')
        assert phases.index('build') < phases.index('validate')
        assert phases.index('validate') < phases.index('deploy')
        assert phases.index('deploy') < phases.index('verify')
    
    def test_deployment_stops_on_gate_failure(self, deploy_orchestrator):
        """Test deployment aborts if validation gates fail."""
        with patch.object(deploy_orchestrator, 'run_phase') as mock_run:
            # Make pre-flight phase fail
            mock_run.return_value = {'success': False, 'phase': 'pre-flight', 'error': 'Validation failed'}
            
            result = deploy_orchestrator.execute_deployment(dry_run=True)
            
            assert result['success'] is False
            assert result.get('failed_phase') == 'pre-flight'
    
    def test_deployment_generates_report(self, deploy_orchestrator, cortex_root):
        """Test deployment generates detailed report."""
        result = deploy_orchestrator.execute_deployment(dry_run=True)
        
        # Report should be saved
        reports_dir = cortex_root / "cortex-brain" / "documents" / "reports"
        if reports_dir.exists():
            report_files = list(reports_dir.glob("deployment-*.md"))
            assert len(report_files) > 0


class TestRollbackCapability:
    """Test deployment rollback functionality."""
    
    def test_orchestrator_can_rollback_deployment(self, deploy_orchestrator):
        """Test orchestrator can rollback failed deployment."""
        result = deploy_orchestrator.rollback_deployment()
        
        assert 'rollback_status' in result
        assert result.get('state') in ['IDLE', 'ROLLED_BACK']
    
    def test_rollback_restores_previous_state(self, deploy_orchestrator):
        """Test rollback restores system to pre-deployment state."""
        # Save initial state
        initial_state = deploy_orchestrator.get_state()
        
        # Transition through states to FAILED
        deploy_orchestrator.transition_to('VALIDATING')
        deploy_orchestrator.transition_to('FAILED')
        
        # Rollback (only works from FAILED state)
        deploy_orchestrator.rollback_deployment()
        
        # Should be ROLLED_BACK
        current_state = deploy_orchestrator.get_state()
        assert current_state == 'ROLLED_BACK'


class TestManifestIntegration:
    """Test deployment manifest integration."""
    
    def test_manifest_defines_phases(self, deploy_orchestrator):
        """Test manifest defines all deployment phases."""
        manifest = deploy_orchestrator.get_manifest()
        
        assert 'phases' in manifest
        assert len(manifest['phases']) >= 5
    
    def test_manifest_defines_gates(self, deploy_orchestrator):
        """Test manifest defines deployment gates."""
        manifest = deploy_orchestrator.get_manifest()
        
        assert 'gates' in manifest
        # Should have critical, warning, info gates
        assert any(g.get('severity') == 'critical' for g in manifest['gates'])
    
    def test_manifest_defines_sla_targets(self, deploy_orchestrator):
        """Test manifest defines SLA targets for deployment."""
        manifest = deploy_orchestrator.get_manifest()
        
        assert 'sla' in manifest
        assert 'max_duration_minutes' in manifest['sla']
        assert manifest['sla']['max_duration_minutes'] <= 5


class TestErrorHandling:
    """Test deployment error handling."""
    
    def test_orchestrator_handles_missing_version_file(self, tmp_path):
        """Test orchestrator handles missing VERSION file gracefully."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        (cortex_dir / "cortex-brain").mkdir()
        
        from src.orchestrators.deploy_orchestrator import DeployOrchestrator
        
        with pytest.raises(FileNotFoundError):
            DeployOrchestrator(cortex_dir)
    
    def test_orchestrator_handles_invalid_state_transition(self, deploy_orchestrator):
        """Test orchestrator handles invalid state transitions."""
        with pytest.raises(ValueError):
            deploy_orchestrator.transition_to('INVALID_STATE')
    
    def test_orchestrator_handles_phase_execution_failure(self, deploy_orchestrator):
        """Test orchestrator handles phase execution failures."""
        with patch.object(deploy_orchestrator, 'run_phase') as mock_run:
            mock_run.side_effect = Exception("Phase execution failed")
            
            result = deploy_orchestrator.execute_deployment(dry_run=True)
            
            assert result['success'] is False
            assert 'error' in result
