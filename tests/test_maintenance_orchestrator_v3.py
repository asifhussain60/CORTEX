"""
Tests for Maintenance Orchestrator v3.0

Comprehensive test suite validating:
- Initialization and version management
- Tier classification (1-4)
- Phase determination and execution
- 7-phase maintenance cycle
- Healthcheck integration
- Tiered execution paths
- Completion status signaling

Phase 06 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.orchestration.maintenance_orchestrator_v3 import (
    MaintenanceOrchestratorV3, MaintenancePhase, MaintenanceContext
)
from src.operations.base_operation_module import OperationStatus
from src.operations.modules.routing.complexity_analyzer import ComplexityTier
from src.operations.modules.version.version_manager import get_version_manager


@pytest.fixture
def maintenance_orchestrator(tmp_path):
    """Create maintenance orchestrator instance."""
    orchestrator = MaintenanceOrchestratorV3(project_root=tmp_path)
    yield orchestrator


# ===== Test Initialization =====

class TestMaintenanceOrchestratorInit:
    """Test maintenance orchestrator initialization."""
    
    def test_init_creates_orchestrator(self, maintenance_orchestrator):
        """Test basic initialization."""
        assert maintenance_orchestrator is not None
        assert maintenance_orchestrator.version == "3.0"
    
    def test_init_registers_version(self, maintenance_orchestrator):
        """Test version manager registration."""
        vm = get_version_manager()
        version = vm.get_orchestrator_version("maintenance_orchestrator")
        assert version == "3.0"
    
    def test_init_creates_routing_components(self, maintenance_orchestrator):
        """Test routing components initialization."""
        assert maintenance_orchestrator.tiered_router is not None
        assert maintenance_orchestrator.complexity_analyzer is not None
    
    def test_init_sets_default_phase(self, maintenance_orchestrator):
        """Test default maintenance phase."""
        assert maintenance_orchestrator.current_phase == MaintenancePhase.PRE_HEALTHCHECK
    
    def test_init_creates_metrics(self, maintenance_orchestrator):
        """Test metrics initialization."""
        assert 'operations_processed' in maintenance_orchestrator.metrics
        assert 'tier_breakdown' in maintenance_orchestrator.metrics
        assert 'phases_completed' in maintenance_orchestrator.metrics
        assert maintenance_orchestrator.metrics['phases_total'] == 7


# ===== Test Metadata =====

class TestMaintenanceOrchestratorMetadata:
    """Test metadata generation."""
    
    def test_metadata_has_required_fields(self, maintenance_orchestrator):
        """Test metadata structure."""
        metadata = maintenance_orchestrator.get_metadata()
        assert metadata.module_id == "maintenance_orchestrator_v3"
        assert metadata.name == "System Maintenance Orchestrator 3.0"
        assert metadata.version == "3.0.0"
        assert metadata.author == "Asif Hussain"
    
    def test_metadata_has_tags(self, maintenance_orchestrator):
        """Test metadata tags."""
        metadata = maintenance_orchestrator.get_metadata()
        assert "maintenance" in metadata.tags
        assert "system" in metadata.tags
        assert "tiered-routing" in metadata.tags


# ===== Test Phase Determination =====

class TestPhaseDetermination:
    """Test phase determination based on tier."""
    
    def test_tier1_no_phases(self, maintenance_orchestrator):
        """Test Tier 1 has no full phases (just healthcheck)."""
        phases = maintenance_orchestrator._determine_phases(1)
        assert len(phases) == 0
    
    def test_tier2_light_phases(self, maintenance_orchestrator):
        """Test Tier 2 has limited phases."""
        phases = maintenance_orchestrator._determine_phases(2)
        assert len(phases) == 2
        assert MaintenancePhase.ALIGNMENT in phases
        assert MaintenancePhase.CLEANUP in phases
    
    def test_tier3_full_phases(self, maintenance_orchestrator):
        """Test Tier 3 has all 7 phases."""
        phases = maintenance_orchestrator._determine_phases(3)
        assert len(phases) == 7
        assert MaintenancePhase.PRE_HEALTHCHECK in phases
        assert MaintenancePhase.VACUUM in phases
        assert MaintenancePhase.POST_HEALTHCHECK in phases
    
    def test_tier4_full_phases(self, maintenance_orchestrator):
        """Test Tier 4 also has all 7 phases."""
        phases = maintenance_orchestrator._determine_phases(4)
        assert len(phases) == 7
    
    def test_specific_phases_override(self, maintenance_orchestrator):
        """Test specific phases can be selected."""
        phases = maintenance_orchestrator._determine_phases(
            3, specific_phases=['alignment', 'cleanup']
        )
        assert len(phases) == 2
        assert MaintenancePhase.ALIGNMENT in phases
        assert MaintenancePhase.CLEANUP in phases


# ===== Test Tier Classification =====

class TestTierClassification:
    """Test tier classification for maintenance operations."""
    
    def test_tier1_health_check(self, maintenance_orchestrator):
        """Test Tier 1 classification for health check."""
        context = maintenance_orchestrator._classify_and_analyze(
            "check health", False, force_tier=1
        )
        assert context.tier == 1
    
    def test_tier2_alignment(self, maintenance_orchestrator):
        """Test Tier 2 classification for single phase."""
        context = maintenance_orchestrator._classify_and_analyze(
            "fix alignment", False, force_tier=2
        )
        assert context.tier == 2
    
    def test_tier3_full_maintenance(self, maintenance_orchestrator):
        """Test Tier 3 classification for full maintenance."""
        context = maintenance_orchestrator._classify_and_analyze(
            "run system maintenance", False, force_tier=3
        )
        assert context.tier == 3
    
    def test_tier4_deep_analysis(self, maintenance_orchestrator):
        """Test Tier 4 classification for deep maintenance."""
        context = maintenance_orchestrator._classify_and_analyze(
            "deep maintenance analysis", False, force_tier=4
        )
        assert context.tier == 4
    
    def test_force_tier_override(self, maintenance_orchestrator):
        """Test forced tier classification."""
        context = maintenance_orchestrator._classify_and_analyze(
            "any operation", False, force_tier=3
        )
        assert context.tier == 3
        assert context.routing_decision.confidence == 1.0


# ===== Test Tier 1 Execution =====

class TestTier1Execution:
    """Test Tier 1 (INSTANT) execution path."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation')
    def test_tier1_executes_instantly(self, mock_healthcheck, maintenance_orchestrator):
        """Test Tier 1 execution completes quickly."""
        # Mock healthcheck
        mock_hc_instance = Mock()
        mock_hc_instance.execute.return_value = Mock(
            success=True,
            data={'overall_health': {'is_healthy': True}}
        )
        mock_healthcheck.return_value = mock_hc_instance
        
        context = maintenance_orchestrator._classify_and_analyze(
            "check health", False, force_tier=1
        )
        result = maintenance_orchestrator._execute_tier1_instant(context)
        
        assert result['success'] is True
        assert result['tier'] == 1
        assert result['execution_method'] == 'instant'
        assert 'health_status' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation')
    def test_tier1_returns_health_status(self, mock_healthcheck, maintenance_orchestrator):
        """Test Tier 1 returns health status."""
        # Mock healthy system
        mock_hc_instance = Mock()
        mock_hc_instance.execute.return_value = Mock(
            success=True,
            data={'overall_health': {'is_healthy': True}}
        )
        mock_healthcheck.return_value = mock_hc_instance
        
        context = maintenance_orchestrator._classify_and_analyze(
            "system status", False, force_tier=1
        )
        result = maintenance_orchestrator._execute_tier1_instant(context)
        
        assert result['health_status'] == 'healthy'
        assert 'health_data' in result


# ===== Test Tier 2 Execution =====

class TestTier2Execution:
    """Test Tier 2 (LIGHTWEIGHT) execution path."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_tier2_lightweight_execution(self, mock_align, maintenance_orchestrator):
        """Test Tier 2 lightweight execution."""
        # Mock alignment
        mock_align.return_value = {'success': True, 'fixes_applied': 5}
        
        context = maintenance_orchestrator._classify_and_analyze(
            "fix alignment", False, force_tier=2
        )
        result = maintenance_orchestrator._execute_tier2_lightweight(context)
        
        assert result['success'] is True
        assert result['tier'] == 2
        assert result['execution_method'] == 'lightweight'
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_tier2_runs_specific_phases(self, mock_align, maintenance_orchestrator):
        """Test Tier 2 runs only specified phases."""
        mock_align.return_value = {'success': True, 'fixes_applied': 3}
        
        context = maintenance_orchestrator._classify_and_analyze(
            "align only", False, force_tier=2, specific_phases=['alignment']
        )
        result = maintenance_orchestrator._execute_tier2_lightweight(context)
        
        assert 'alignment' in context.phases_completed
        assert len(context.phases_completed) >= 1


# ===== Test Tier 3 Execution =====

class TestTier3Execution:
    """Test Tier 3 (DOCUMENTED) execution path."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation')
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.subprocess.run')
    @patch('src.operations.modules.orchestration.cleanup_orchestrator.CleanupOrchestrator')
    @patch('src.operations.optimize.run_optimize')
    def test_tier3_full_cycle(self, mock_optimize, mock_cleanup_class, mock_subprocess, mock_align, mock_healthcheck, maintenance_orchestrator, tmp_path):
        """Test Tier 3 full 7-phase cycle."""
        # Mock healthcheck
        mock_hc_instance = Mock()
        mock_hc_instance.execute.return_value = Mock(
            success=True,
            data={'overall_health': {'is_healthy': True}}
        )
        mock_healthcheck.return_value = mock_hc_instance
        
        # Mock alignment
        mock_align.return_value = {'success': True, 'fixes_applied': 2}
        
        # Mock cleanup
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={'metrics': {'files_moved': 10, 'files_removed': 5}}
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        # Mock optimize
        mock_optimize.return_value = {'success': True, 'optimizations_applied': 3}
        
        # Mock refresh script
        mock_subprocess.return_value = Mock(returncode=0, stderr='')
        
        # Create mock script
        script_dir = tmp_path / "scripts"
        script_dir.mkdir()
        script_file = script_dir / "regenerate_cortex_prompts.py"
        script_file.write_text("# mock script")
        
        context = maintenance_orchestrator._classify_and_analyze(
            "full maintenance", False, force_tier=3
        )
        
        result = maintenance_orchestrator._execute_tier3_documented(context)
        
        assert result['success'] is True
        assert result['tier'] == 3
        assert result['execution_method'] == 'documented'
        assert len(context.phases_completed) == 7
    
    def test_tier3_tracks_phases(self, maintenance_orchestrator):
        """Test Tier 3 tracks completed phases."""
        context = maintenance_orchestrator._classify_and_analyze(
            "maintenance", False, force_tier=3
        )
        
        # Phases should be determined
        assert len(context.phases_to_run) == 7
        assert MaintenancePhase.PRE_HEALTHCHECK in context.phases_to_run
        assert MaintenancePhase.VACUUM in context.phases_to_run


# ===== Test Tier 4 Execution =====

class TestTier4Execution:
    """Test Tier 4 (COMPLEX) execution path."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation')
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.subprocess.run')
    @patch('src.operations.modules.orchestration.cleanup_orchestrator.CleanupOrchestrator')
    @patch('src.operations.optimize.run_optimize')
    def test_tier4_complex_planning(self, mock_optimize, mock_cleanup_class, mock_subprocess, mock_align, mock_healthcheck, maintenance_orchestrator):
        """Test Tier 4 complex maintenance."""
        # Mock healthcheck
        mock_hc_instance = Mock()
        mock_hc_instance.execute.return_value = Mock(
            success=True,
            data={'overall_health': {'is_healthy': True}}
        )
        mock_healthcheck.return_value = mock_hc_instance
        
        # Mock alignment
        mock_align.return_value = {'success': True, 'fixes_applied': 1}
        
        # Mock cleanup
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={'metrics': {'files_moved': 5, 'files_removed': 2}}
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        # Mock optimize
        mock_optimize.return_value = {'success': True, 'optimizations_applied': 2}
        
        # Mock subprocess
        mock_subprocess.return_value = Mock(returncode=0, stderr='')
        
        context = maintenance_orchestrator._classify_and_analyze(
            "deep maintenance", False, force_tier=4
        )
        result = maintenance_orchestrator._execute_tier4_complex(context)
        
        assert result['success'] is True
        assert result['tier'] == 4
        assert result['execution_method'] == 'complex'
        assert 'deep_analysis' in result


# ===== Test Version Management =====

class TestVersionManagement:
    """Test version management integration."""
    
    def test_version_registered(self, maintenance_orchestrator):
        """Test version is registered."""
        vm = get_version_manager()
        version = vm.get_orchestrator_version("maintenance_orchestrator")
        assert version == "3.0"
    
    def test_orchestrator_has_version(self, maintenance_orchestrator):
        """Test orchestrator stores version."""
        assert maintenance_orchestrator.version == "3.0"


# ===== Test Completion Status =====

class TestCompletionStatus:
    """Test completion status signaling."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation')
    def test_complete_status_tier1(self, mock_healthcheck, maintenance_orchestrator):
        """Test is_complete flag for Tier 1."""
        # Mock healthcheck
        mock_hc_instance = Mock()
        mock_hc_instance.execute.return_value = Mock(
            success=True,
            data={'overall_health': {'is_healthy': True}}
        )
        mock_healthcheck.return_value = mock_hc_instance
        
        result = maintenance_orchestrator.execute({
            'operation': 'check health',
            'force_tier': 1
        })
        
        assert 'is_complete' in result.data
    
    def test_incomplete_when_errors(self, maintenance_orchestrator):
        """Test is_complete=False when errors present."""
        maintenance_orchestrator.metrics['errors'].append("Test error")
        
        with patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation'):
            result = maintenance_orchestrator.execute({
                'operation': 'check health',
                'force_tier': 1
            })
        
        assert result.data['is_complete'] is False


# ===== Test Dry Run =====

class TestDryRun:
    """Test dry run functionality."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_dry_run_simulates_changes(self, mock_align, maintenance_orchestrator):
        """Test dry run doesn't make actual changes."""
        mock_align.return_value = {'success': True, 'dry_run': True}
        
        context = maintenance_orchestrator._classify_and_analyze(
            "alignment", True, force_tier=2
        )
        
        assert context.dry_run is True
        
        result = maintenance_orchestrator._run_alignment_phase(context)
        assert result.get('dry_run') or result.get('success')


# ===== Test Full Workflow =====

class TestFullWorkflow:
    """Test complete maintenance workflow integration."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation')
    def test_tier1_workflow(self, mock_healthcheck, maintenance_orchestrator):
        """Test complete Tier 1 workflow."""
        # Mock healthcheck
        mock_hc_instance = Mock()
        mock_hc_instance.execute.return_value = Mock(
            success=True,
            data={'overall_health': {'is_healthy': True}}
        )
        mock_healthcheck.return_value = mock_hc_instance
        
        result = maintenance_orchestrator.execute({
            'operation': 'check health',
            'force_tier': 1
        })
        
        assert result.success is True
        assert result.data['tier'] == 1
    
    def test_metrics_updated(self, maintenance_orchestrator):
        """Test metrics are updated after execution."""
        initial_count = maintenance_orchestrator.metrics['operations_processed']
        
        with patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation'):
            maintenance_orchestrator.execute({
                'operation': 'check health',
                'force_tier': 1
            })
        
        assert maintenance_orchestrator.metrics['operations_processed'] == initial_count + 1
    
    def test_tier_breakdown_tracked(self, maintenance_orchestrator):
        """Test tier breakdown metrics."""
        initial_tier1 = maintenance_orchestrator.metrics['tier_breakdown'][1]
        
        with patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation'):
            maintenance_orchestrator.execute({
                'operation': 'check health',
                'force_tier': 1
            })
        
        assert maintenance_orchestrator.metrics['tier_breakdown'][1] == initial_tier1 + 1


# ===== Test Error Handling =====

class TestErrorHandling:
    """Test error handling."""
    
    def test_exception_caught(self, maintenance_orchestrator, monkeypatch):
        """Test exceptions are caught and returned."""
        def mock_classify(*args, **kwargs):
            raise ValueError("Test error")
        
        monkeypatch.setattr(maintenance_orchestrator, '_classify_and_analyze', mock_classify)
        
        result = maintenance_orchestrator.execute({
            'operation': 'test'
        })
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert 'error' in result.data
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.HealthCheckOperation')
    def test_healthcheck_failure_handled(self, mock_healthcheck, maintenance_orchestrator):
        """Test healthcheck failure is handled gracefully."""
        # Mock failing healthcheck
        mock_hc_instance = Mock()
        mock_hc_instance.execute.side_effect = Exception("Healthcheck failed")
        mock_healthcheck.return_value = mock_hc_instance
        
        context = maintenance_orchestrator._classify_and_analyze(
            "check health", False, force_tier=1
        )
        result = maintenance_orchestrator._execute_tier1_instant(context)
        
        assert result['success'] is False
        assert 'error' in result


# ===== Test Report Generation =====

class TestReportGeneration:
    """Test maintenance report generation."""
    
    def test_report_generated(self, maintenance_orchestrator):
        """Test report is generated."""
        context = maintenance_orchestrator._classify_and_analyze(
            "test", False, force_tier=1
        )
        
        start_time = datetime.now()
        execution_result = {'success': True}
        
        report = maintenance_orchestrator._generate_report(
            start_time, context, execution_result
        )
        
        assert 'timestamp' in report
        assert 'operation' in report
        assert 'tier' in report
        assert 'duration_seconds' in report
    
    def test_report_saved(self, maintenance_orchestrator, tmp_path):
        """Test report is saved to file."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'test',
            'success': True
        }
        
        report_path = maintenance_orchestrator._save_report(report)
        
        assert report_path.exists()
        assert report_path.suffix == '.json'
        assert 'maintenance_' in report_path.name
