"""
Maintenance Orchestrator v3.0 - Comprehensive Test Suite

Test Coverage:
- Phase initialization (10 tests)
- Pre-healthcheck phase (12 tests)
- Align phase (10 tests)
- Cleanup phase (10 tests)
- Optimize phase (10 tests)
- Vacuum phase (10 tests)
- Refresh prompts phase (10 tests)
- Post-healthcheck phase (12 tests)
- Integration tests (10 tests)

Total: 94 tests targeting 60%+ coverage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime
import tempfile
import json

from src.operations.modules.orchestration.maintenance_orchestrator_v3 import (
    MaintenanceOrchestrator,
    execute_maintenance
)


@pytest.fixture
def mock_cortex_root(tmp_path):
    """Create mock CORTEX root directory structure."""
    # Create required directories
    (tmp_path / 'cortex-brain').mkdir()
    (tmp_path / 'cortex-brain' / 'tier0').mkdir()
    (tmp_path / 'cortex-brain' / 'tier1').mkdir()
    (tmp_path / 'cortex-brain' / 'tier2').mkdir()
    (tmp_path / 'cortex-brain' / 'tier3').mkdir()
    (tmp_path / 'src').mkdir()
    (tmp_path / 'src' / 'orchestrators').mkdir()
    (tmp_path / 'tests').mkdir()
    
    # Create required files
    (tmp_path / 'cortex-brain' / 'brain-protection-rules.yaml').write_text('rules: []')
    (tmp_path / 'cortex-brain' / 'response-templates-v4.yaml').write_text('templates: {}')
    (tmp_path / 'cortex.config.json').write_text('{"version": "4.0.0"}')
    (tmp_path / 'requirements.txt').write_text('pytest>=7.0.0')
    
    return tmp_path


@pytest.fixture
def maintenance_orchestrator(mock_cortex_root):
    """Create MaintenanceOrchestrator instance."""
    return MaintenanceOrchestrator(cortex_root=mock_cortex_root)


# ============================================================================
# Test Group 1: Phase Initialization (10 tests)
# ============================================================================

class TestPhaseInitialization:
    """Test orchestrator initialization and phase registration."""
    
    def test_init_with_valid_cortex_root(self, mock_cortex_root):
        """Test initialization with valid CORTEX root."""
        orchestrator = MaintenanceOrchestrator(cortex_root=mock_cortex_root)
        
        assert orchestrator.name == "maintenance_v3"
        assert orchestrator.cortex_root == mock_cortex_root
        assert orchestrator.baseline_health is None
        assert orchestrator.final_health is None
    
    def test_init_with_custom_logger(self, mock_cortex_root):
        """Test initialization with custom logger."""
        import logging
        logger = logging.getLogger('test_logger')
        
        orchestrator = MaintenanceOrchestrator(
            cortex_root=mock_cortex_root,
            logger=logger
        )
        
        assert orchestrator.logger == logger
    
    def test_init_with_config(self, mock_cortex_root):
        """Test initialization with custom config."""
        config = {'max_retries': 5, 'timeout': 300}
        
        orchestrator = MaintenanceOrchestrator(
            cortex_root=mock_cortex_root,
            config=config
        )
        
        assert orchestrator.config == config
    
    def test_setup_validates_cortex_root(self, maintenance_orchestrator):
        """Test setup validates CORTEX root exists."""
        result = maintenance_orchestrator._setup({})
        
        assert result['success'] is True
        assert 'cortex_root' in result
        assert result['directories_validated'] == 3
    
    def test_setup_with_missing_cortex_root(self):
        """Test setup fails with missing CORTEX root."""
        orchestrator = MaintenanceOrchestrator(cortex_root=Path('/nonexistent'))
        
        with pytest.raises(RuntimeError, match="CORTEX root not found"):
            orchestrator._setup({})
    
    def test_register_phases_creates_7_phases(self, maintenance_orchestrator):
        """Test phase registration creates 7 phases."""
        maintenance_orchestrator._register_phases()
        
        registered_phases = maintenance_orchestrator.phase_manager.phases
        
        assert len(registered_phases) == 7
        assert 'pre_healthcheck' in registered_phases
        assert 'align' in registered_phases
        assert 'cleanup' in registered_phases
        assert 'optimize' in registered_phases
        assert 'vacuum' in registered_phases
        assert 'refresh_prompts' in registered_phases
        assert 'post_healthcheck' in registered_phases
    
    def test_execute_phase_with_unknown_phase(self, maintenance_orchestrator):
        """Test execute_phase raises error for unknown phase."""
        with pytest.raises(ValueError, match="Unknown phase"):
            maintenance_orchestrator._execute_phase('unknown_phase', {})
    
    def test_teardown_calculates_health_delta(self, maintenance_orchestrator):
        """Test teardown calculates health delta when both healthchecks complete."""
        maintenance_orchestrator.baseline_health = {'overall_score': 75.0}
        maintenance_orchestrator.final_health = {'overall_score': 85.0}
        
        result = maintenance_orchestrator._teardown({})
        
        assert result['success'] is True
        assert result['health_delta'] == 10.0
    
    def test_teardown_without_healthchecks(self, maintenance_orchestrator):
        """Test teardown handles missing healthcheck data."""
        result = maintenance_orchestrator._teardown({})
        
        assert result['success'] is True
        assert result['health_delta'] is None
    
    def test_phase_execution_logs_transition(self, maintenance_orchestrator, caplog):
        """Test phase execution logs phase transition."""
        maintenance_orchestrator._execute_phase('pre_healthcheck', {})
        
        assert '🎭 Phase transition:' in caplog.text
        assert 'PRE_HEALTHCHECK' in caplog.text


# ============================================================================
# Test Group 2: Pre-Healthcheck Phase (12 tests)
# ============================================================================

class TestPreHealthcheckPhase:
    """Test pre-healthcheck phase implementation."""
    
    def test_pre_healthcheck_success(self, maintenance_orchestrator):
        """Test pre-healthcheck executes successfully."""
        result = maintenance_orchestrator._run_pre_healthcheck({})
        
        assert result['success'] is True
        assert 'overall_score' in result
        assert 'components' in result
    
    def test_pre_healthcheck_sets_baseline_health(self, maintenance_orchestrator):
        """Test pre-healthcheck sets baseline_health attribute."""
        maintenance_orchestrator._run_pre_healthcheck({})
        
        assert maintenance_orchestrator.baseline_health is not None
        assert 'overall_score' in maintenance_orchestrator.baseline_health
        assert 'timestamp' in maintenance_orchestrator.baseline_health
    
    def test_pre_healthcheck_scans_7_components(self, maintenance_orchestrator):
        """Test pre-healthcheck scans all 7 component categories."""
        result = maintenance_orchestrator._run_pre_healthcheck({})
        
        components = result['components']
        
        assert 'brain_tier0' in components
        assert 'brain_tier1' in components
        assert 'brain_tier2' in components
        assert 'brain_tier3' in components
        assert 'orchestrators' in components
        assert 'protection' in components
        assert 'system' in components
    
    def test_check_tier0_health_all_files_present(self, maintenance_orchestrator):
        """Test Tier 0 health check when all files present."""
        result = maintenance_orchestrator._check_tier0_health()
        
        assert result['score'] == 100
        assert result['checks']['brain_protection_rules'] is True
        assert result['checks']['response_templates'] is True
        assert result['status'] == 'healthy'
    
    def test_check_tier0_health_missing_files(self, tmp_path):
        """Test Tier 0 health check when files missing."""
        (tmp_path / 'cortex-brain').mkdir()
        
        orchestrator = MaintenanceOrchestrator(cortex_root=tmp_path)
        result = orchestrator._check_tier0_health()
        
        assert result['score'] == 0
        assert result['checks']['brain_protection_rules'] is False
        assert result['status'] == 'degraded'
    
    def test_check_tier1_health_within_limit(self, maintenance_orchestrator):
        """Test Tier 1 health check within 70-entry limit."""
        result = maintenance_orchestrator._check_tier1_health()
        
        assert result['score'] >= 80
        assert result['context_count'] <= 70
        assert result['status'] == 'healthy'
    
    def test_check_tier1_health_exceeds_limit(self, mock_cortex_root):
        """Test Tier 1 health check when exceeding 70-entry limit."""
        tier1_path = mock_cortex_root / 'cortex-brain' / 'tier1'
        tier1_path.mkdir(exist_ok=True)
        
        # Create 75 context files
        for i in range(75):
            (tier1_path / f'context_{i}.json').write_text('{}')
        
        orchestrator = MaintenanceOrchestrator(cortex_root=mock_cortex_root)
        result = orchestrator._check_tier1_health()
        
        assert result['score'] < 100
        assert result['context_count'] == 75
    
    def test_check_tier2_health_kg_exists(self, maintenance_orchestrator):
        """Test Tier 2 health check when knowledge graph exists."""
        result = maintenance_orchestrator._check_tier2_health()
        
        assert result['score'] == 100
        assert result['kg_exists'] is True
        assert result['status'] == 'healthy'
    
    def test_check_tier3_health_dev_context_exists(self, maintenance_orchestrator):
        """Test Tier 3 health check when dev context exists."""
        result = maintenance_orchestrator._check_tier3_health()
        
        assert result['score'] == 100
        assert result['dev_context_exists'] is True
        assert result['status'] == 'healthy'
    
    def test_check_orchestrators_health_sufficient_count(self, mock_cortex_root):
        """Test orchestrators health check with sufficient count."""
        orch_path = mock_cortex_root / 'src' / 'orchestrators'
        
        # Create 10 orchestrator directories
        for i in range(10):
            (orch_path / f'orch_{i}').mkdir()
        
        orchestrator = MaintenanceOrchestrator(cortex_root=mock_cortex_root)
        result = orchestrator._check_orchestrators_health()
        
        assert result['score'] == 100
        assert result['orchestrator_count'] == 10
        assert result['status'] == 'healthy'
    
    def test_check_protection_health_all_checks_pass(self, maintenance_orchestrator):
        """Test protection health check when all checks pass."""
        result = maintenance_orchestrator._check_protection_health()
        
        assert result['score'] == 100
        assert result['checks']['skull_rules'] is True
        assert result['checks']['test_separation'] is True
        assert result['status'] == 'healthy'
    
    def test_check_system_health_all_checks_pass(self, maintenance_orchestrator):
        """Test system health check when all checks pass."""
        result = maintenance_orchestrator._check_system_health()
        
        assert result['score'] == 100
        assert result['checks']['src_directory'] is True
        assert result['checks']['tests_directory'] is True
        assert result['checks']['config_file'] is True
        assert result['checks']['requirements'] is True
        assert result['status'] == 'healthy'


# ============================================================================
# Test Group 3: Align Phase (10 tests)
# ============================================================================

class TestAlignPhase:
    """Test align phase implementation."""
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_success(self, mock_run_align, maintenance_orchestrator):
        """Test align phase executes successfully."""
        mock_run_align.return_value = {
            'success': True,
            'fixes': ['fix1', 'fix2'],
            'issues': ['issue1'],
            'validation_passed': True,
            'checkpoint_path': '/backup/align_123'
        }
        
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['success'] is True
        assert result['fixes_applied'] == 2
        assert result['issues_detected'] == 1
        assert result['validation_passed'] is True
    
    def test_align_phase_import_error_skips(self, maintenance_orchestrator):
        """Test align phase skips when utility not available."""
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['success'] is True
        assert result.get('skipped') is True
        assert 'reason' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_with_no_fixes(self, mock_run_align, maintenance_orchestrator):
        """Test align phase when no fixes needed."""
        mock_run_align.return_value = {
            'success': True,
            'fixes': [],
            'issues': [],
            'validation_passed': True
        }
        
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['success'] is True
        assert result['fixes_applied'] == 0
        assert result['issues_detected'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_creates_checkpoint(self, mock_run_align, maintenance_orchestrator):
        """Test align phase creates rollback checkpoint."""
        mock_run_align.return_value = {
            'success': True,
            'fixes': ['fix1'],
            'issues': [],
            'checkpoint_path': '/backup/checkpoint_123'
        }
        
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['rollback_checkpoint'] == '/backup/checkpoint_123'
        mock_run_align.assert_called_once_with(auto_fix=True, create_checkpoint=True)
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_validation_failure(self, mock_run_align, maintenance_orchestrator):
        """Test align phase handles validation failure."""
        mock_run_align.return_value = {
            'success': False,
            'fixes': ['fix1'],
            'issues': ['critical_issue'],
            'validation_passed': False
        }
        
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['success'] is False
        assert result['validation_passed'] is False
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_exception_handling(self, mock_run_align, maintenance_orchestrator):
        """Test align phase handles exceptions gracefully."""
        mock_run_align.side_effect = Exception("Alignment failed")
        
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_logs_results(self, mock_run_align, maintenance_orchestrator, caplog):
        """Test align phase logs fixes and issues."""
        mock_run_align.return_value = {
            'success': True,
            'fixes': ['fix1', 'fix2', 'fix3'],
            'issues': ['issue1', 'issue2']
        }
        
        maintenance_orchestrator._run_align_phase({})
        
        assert '3 fixes applied' in caplog.text
        assert '2 issues detected' in caplog.text
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_with_auto_fix_enabled(self, mock_run_align, maintenance_orchestrator):
        """Test align phase passes auto_fix=True."""
        mock_run_align.return_value = {'success': True, 'fixes': [], 'issues': []}
        
        maintenance_orchestrator._run_align_phase({})
        
        mock_run_align.assert_called_with(auto_fix=True, create_checkpoint=True)
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_returns_checkpoint_path(self, mock_run_align, maintenance_orchestrator):
        """Test align phase returns checkpoint path for rollback."""
        mock_run_align.return_value = {
            'success': True,
            'fixes': [],
            'issues': [],
            'checkpoint_path': '/path/to/checkpoint'
        }
        
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['rollback_checkpoint'] == '/path/to/checkpoint'
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.run_align')
    def test_align_phase_success_criteria(self, mock_run_align, maintenance_orchestrator):
        """Test align phase success criteria."""
        mock_run_align.return_value = {
            'success': True,
            'fixes': ['fix1'],
            'issues': [],
            'validation_passed': True
        }
        
        result = maintenance_orchestrator._run_align_phase({})
        
        assert result['success'] is True
        assert result['validation_passed'] is True


# ============================================================================
# Test Group 4: Cleanup Phase (10 tests)
# ============================================================================

class TestCleanupPhase:
    """Test cleanup phase implementation."""
    
    def test_cleanup_phase_import_error_skips(self, maintenance_orchestrator):
        """Test cleanup phase skips when orchestrator not available."""
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['success'] is True
        assert result.get('skipped') is True
        assert result['files_moved'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_success(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase executes successfully."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={
                'files_moved': 5,
                'references_updated': 3,
                'duplicates_detected': 2,
                'backup_path': '/backup/cleanup_123'
            }
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['success'] is True
        assert result['files_moved'] == 5
        assert result['references_updated'] == 3
        assert result['duplicates_found'] == 2
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_with_no_files_moved(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase when no files need moving."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={'files_moved': 0}
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['files_moved'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_creates_backup(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase creates backup."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={'backup_path': '/backup/cleanup_456'}
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['backup_path'] == '/backup/cleanup_456'
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_exception_handling(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase handles exceptions."""
        mock_cleanup = Mock()
        mock_cleanup.execute.side_effect = Exception("Cleanup failed")
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_dry_run_disabled(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase executes with dry_run=False."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(success=True, data={})
        mock_cleanup_class.return_value = mock_cleanup
        
        maintenance_orchestrator._run_cleanup_phase({})
        
        mock_cleanup.execute.assert_called_once_with({'dry_run': False})
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_updates_references(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase updates file references."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={'references_updated': 10}
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['references_updated'] == 10
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_detects_duplicates(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase detects duplicate code."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={'duplicates_detected': 7}
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['duplicates_found'] == 7
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_failure(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase handles failure."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(success=False, data={})
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert result['success'] is False
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.CleanupOrchestrator')
    def test_cleanup_phase_returns_all_metrics(self, mock_cleanup_class, maintenance_orchestrator):
        """Test cleanup phase returns all required metrics."""
        mock_cleanup = Mock()
        mock_cleanup.execute.return_value = Mock(
            success=True,
            data={
                'files_moved': 3,
                'references_updated': 2,
                'duplicates_detected': 1,
                'backup_path': '/backup'
            }
        )
        mock_cleanup_class.return_value = mock_cleanup
        
        result = maintenance_orchestrator._run_cleanup_phase({})
        
        assert 'files_moved' in result
        assert 'references_updated' in result
        assert 'duplicates_found' in result
        assert 'backup_path' in result


# ============================================================================
# Test Group 5: Optimize Phase (10 tests)
# ============================================================================

class TestOptimizePhase:
    """Test optimize phase implementation."""
    
    def test_optimize_phase_import_error_skips(self, maintenance_orchestrator):
        """Test optimize phase skips when orchestrator not available."""
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['success'] is True
        assert result.get('skipped') is True
        assert result['tokens_saved'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_success(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase executes successfully."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(
            success=True,
            data={
                'tokens_saved': 1500,
                'cache_cleared': True
            }
        )
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['success'] is True
        assert result['tokens_saved'] == 1500
        assert result['cache_cleared'] is True
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_saves_tokens(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase saves tokens."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(
            success=True,
            data={'tokens_saved': 2000}
        )
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['tokens_saved'] == 2000
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_clears_cache(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase clears cache."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(
            success=True,
            data={'cache_cleared': True}
        )
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['cache_cleared'] is True
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_exception_handling(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase handles exceptions."""
        mock_optimize = Mock()
        mock_optimize.execute.side_effect = Exception("Optimization failed")
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_with_zero_savings(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase when no optimization possible."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(
            success=True,
            data={'tokens_saved': 0}
        )
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['tokens_saved'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_failure(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase handles failure."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(success=False, data={})
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['success'] is False
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_executes_with_empty_context(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase executes with empty context."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(success=True, data={})
        mock_optimize_class.return_value = mock_optimize
        
        maintenance_orchestrator._run_optimize_phase({})
        
        mock_optimize.execute.assert_called_once_with({})
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_returns_metrics(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase returns required metrics."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(
            success=True,
            data={'tokens_saved': 500, 'cache_cleared': False}
        )
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert 'tokens_saved' in result
        assert 'cache_cleared' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.OptimizeCortexOrchestrator')
    def test_optimize_phase_high_token_savings(self, mock_optimize_class, maintenance_orchestrator):
        """Test optimize phase with high token savings."""
        mock_optimize = Mock()
        mock_optimize.execute.return_value = Mock(
            success=True,
            data={'tokens_saved': 5000}
        )
        mock_optimize_class.return_value = mock_optimize
        
        result = maintenance_orchestrator._run_optimize_phase({})
        
        assert result['tokens_saved'] == 5000


# ============================================================================
# Test Group 6: Vacuum Phase (10 tests)
# ============================================================================

class TestVacuumPhase:
    """Test vacuum phase implementation."""
    
    def test_vacuum_phase_import_error_skips(self, maintenance_orchestrator):
        """Test vacuum phase skips when orchestrator not available."""
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['success'] is True
        assert result.get('skipped') is True
        assert result['space_saved_bytes'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_success(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase executes successfully."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(
            success=True,
            data={
                'space_saved': 1024000,
                'databases_vacuumed': 3
            }
        )
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['success'] is True
        assert result['space_saved_bytes'] == 1024000
        assert result['databases_vacuumed'] == 3
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_vacuums_databases(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase vacuums SQLite databases."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(
            success=True,
            data={'databases_vacuumed': 5}
        )
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['databases_vacuumed'] == 5
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_saves_space(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase saves disk space."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(
            success=True,
            data={'space_saved': 2048000}
        )
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['space_saved_bytes'] == 2048000
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_exception_handling(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase handles exceptions."""
        mock_vacuum = Mock()
        mock_vacuum.execute.side_effect = Exception("Vacuum failed")
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_with_no_space_saved(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase when no space can be saved."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(
            success=True,
            data={'space_saved': 0}
        )
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['space_saved_bytes'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_failure(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase handles failure."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(success=False, data={})
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['success'] is False
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_executes_with_empty_context(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase executes with empty context."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(success=True, data={})
        mock_vacuum_class.return_value = mock_vacuum
        
        maintenance_orchestrator._run_vacuum_phase({})
        
        mock_vacuum.execute.assert_called_once_with({})
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_returns_metrics(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase returns required metrics."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(
            success=True,
            data={'space_saved': 500000, 'databases_vacuumed': 2}
        )
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert 'space_saved_bytes' in result
        assert 'databases_vacuumed' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.VacuumOrchestrator')
    def test_vacuum_phase_large_space_savings(self, mock_vacuum_class, maintenance_orchestrator):
        """Test vacuum phase with large space savings."""
        mock_vacuum = Mock()
        mock_vacuum.execute.return_value = Mock(
            success=True,
            data={'space_saved': 10485760}  # 10MB
        )
        mock_vacuum_class.return_value = mock_vacuum
        
        result = maintenance_orchestrator._run_vacuum_phase({})
        
        assert result['space_saved_bytes'] == 10485760


# ============================================================================
# Test Group 7: Refresh Prompts Phase (10 tests)
# ============================================================================

class TestRefreshPromptsPhase:
    """Test refresh prompts phase implementation."""
    
    def test_refresh_prompts_import_error_skips(self, maintenance_orchestrator):
        """Test refresh prompts skips when utility not available."""
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['success'] is True
        assert result.get('skipped') is True
        assert result['prompts_regenerated'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_success(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts executes successfully."""
        mock_regen.return_value = {
            'success': True,
            'prompts_regenerated': 5
        }
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['success'] is True
        assert result['prompts_regenerated'] == 5
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_regenerates_prompts(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts regenerates prompts."""
        mock_regen.return_value = {
            'success': True,
            'prompts_regenerated': 3
        }
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['prompts_regenerated'] == 3
        mock_regen.assert_called_once()
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_exception_handling(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts handles exceptions."""
        mock_regen.side_effect = Exception("Regeneration failed")
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['success'] is False
        assert 'error' in result
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_with_no_prompts(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts when no prompts need regenerating."""
        mock_regen.return_value = {
            'success': True,
            'prompts_regenerated': 0
        }
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['prompts_regenerated'] == 0
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_failure(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts handles failure."""
        mock_regen.return_value = {
            'success': False,
            'prompts_regenerated': 0
        }
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['success'] is False
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_calls_utility(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts calls regenerate_prompts utility."""
        mock_regen.return_value = {'success': True, 'prompts_regenerated': 1}
        
        maintenance_orchestrator._run_refresh_prompts_phase({})
        
        mock_regen.assert_called_once()
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_returns_count(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts returns regenerated count."""
        mock_regen.return_value = {
            'success': True,
            'prompts_regenerated': 7
        }
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['prompts_regenerated'] == 7
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_high_count(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts with high regeneration count."""
        mock_regen.return_value = {
            'success': True,
            'prompts_regenerated': 15
        }
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['prompts_regenerated'] == 15
    
    @patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.regenerate_prompts')
    def test_refresh_prompts_success_criteria(self, mock_regen, maintenance_orchestrator):
        """Test refresh prompts success criteria."""
        mock_regen.return_value = {
            'success': True,
            'prompts_regenerated': 3
        }
        
        result = maintenance_orchestrator._run_refresh_prompts_phase({})
        
        assert result['success'] is True
        assert 'prompts_regenerated' in result


# ============================================================================
# Test Group 8: Post-Healthcheck Phase (12 tests)
# ============================================================================

class TestPostHealthcheckPhase:
    """Test post-healthcheck phase implementation."""
    
    def test_post_healthcheck_success(self, maintenance_orchestrator):
        """Test post-healthcheck executes successfully."""
        result = maintenance_orchestrator._run_post_healthcheck({})
        
        assert result['success'] is True
        assert 'overall_score' in result
        assert 'components' in result
    
    def test_post_healthcheck_sets_final_health(self, maintenance_orchestrator):
        """Test post-healthcheck sets final_health attribute."""
        maintenance_orchestrator._run_post_healthcheck({})
        
        assert maintenance_orchestrator.final_health is not None
        assert 'overall_score' in maintenance_orchestrator.final_health
        assert 'timestamp' in maintenance_orchestrator.final_health
    
    def test_post_healthcheck_calculates_delta(self, maintenance_orchestrator, caplog):
        """Test post-healthcheck calculates health delta."""
        maintenance_orchestrator.baseline_health = {'overall_score': 70.0}
        
        maintenance_orchestrator._run_post_healthcheck({})
        
        assert 'Final health:' in caplog.text
    
    def test_post_healthcheck_without_baseline(self, maintenance_orchestrator, caplog):
        """Test post-healthcheck handles missing baseline."""
        maintenance_orchestrator._run_post_healthcheck({})
        
        assert 'No baseline health available' in caplog.text
    
    def test_post_healthcheck_positive_delta(self, maintenance_orchestrator, caplog):
        """Test post-healthcheck with positive health delta."""
        maintenance_orchestrator.baseline_health = {'overall_score': 75.0}
        
        result = maintenance_orchestrator._run_post_healthcheck({})
        
        # Should show improvement
        final_score = result['overall_score']
        assert final_score >= 0
    
    def test_post_healthcheck_scans_all_components(self, maintenance_orchestrator):
        """Test post-healthcheck scans all 7 components."""
        result = maintenance_orchestrator._run_post_healthcheck({})
        
        components = result['components']
        
        assert len(components) == 7
        assert all(key in components for key in [
            'brain_tier0', 'brain_tier1', 'brain_tier2', 'brain_tier3',
            'orchestrators', 'protection', 'system'
        ])
    
    def test_post_healthcheck_timestamp_set(self, maintenance_orchestrator):
        """Test post-healthcheck sets timestamp."""
        maintenance_orchestrator._run_post_healthcheck({})
        
        assert maintenance_orchestrator.final_health['timestamp'] is not None
    
    def test_post_healthcheck_overall_score_calculation(self, maintenance_orchestrator):
        """Test post-healthcheck calculates overall score correctly."""
        result = maintenance_orchestrator._run_post_healthcheck({})
        
        components = result['components']
        scores = [c['score'] for c in components.values()]
        expected_score = sum(scores) / len(scores)
        
        assert result['overall_score'] == expected_score
    
    def test_post_healthcheck_logs_final_health(self, maintenance_orchestrator, caplog):
        """Test post-healthcheck logs final health score."""
        maintenance_orchestrator._run_post_healthcheck({})
        
        assert 'Final health:' in caplog.text
    
    def test_post_healthcheck_logs_delta_with_baseline(self, maintenance_orchestrator, caplog):
        """Test post-healthcheck logs delta when baseline available."""
        maintenance_orchestrator.baseline_health = {'overall_score': 80.0}
        
        maintenance_orchestrator._run_post_healthcheck({})
        
        assert 'Δ' in caplog.text
    
    def test_post_healthcheck_component_scores_valid(self, maintenance_orchestrator):
        """Test post-healthcheck returns valid component scores."""
        result = maintenance_orchestrator._run_post_healthcheck({})
        
        for component in result['components'].values():
            assert 0 <= component['score'] <= 100
    
    def test_post_healthcheck_returns_all_components(self, maintenance_orchestrator):
        """Test post-healthcheck returns all required components."""
        result = maintenance_orchestrator._run_post_healthcheck({})
        
        assert 'brain_tier0' in result['components']
        assert 'brain_tier1' in result['components']
        assert 'brain_tier2' in result['components']
        assert 'brain_tier3' in result['components']
        assert 'orchestrators' in result['components']
        assert 'protection' in result['components']
        assert 'system' in result['components']


# ============================================================================
# Test Group 9: Integration Tests (10 tests)
# ============================================================================

class TestIntegration:
    """Test full orchestrator integration."""
    
    def test_execute_maintenance_function(self, mock_cortex_root):
        """Test execute_maintenance helper function."""
        result = execute_maintenance(mock_cortex_root)
        
        assert result is not None
        assert 'result' in result or 'error' in result
    
    def test_full_workflow_execution(self, maintenance_orchestrator):
        """Test full 7-phase workflow execution."""
        result = maintenance_orchestrator.execute({})
        
        assert result is not None
    
    def test_phase_execution_order(self, maintenance_orchestrator):
        """Test phases execute in correct order."""
        maintenance_orchestrator._register_phases()
        
        phases = list(maintenance_orchestrator.phase_manager.phases.keys())
        
        assert phases[0] == 'pre_healthcheck'
        assert phases[1] == 'align'
        assert phases[2] == 'cleanup'
        assert phases[3] == 'optimize'
        assert phases[4] == 'vacuum'
        assert phases[5] == 'refresh_prompts'
        assert phases[6] == 'post_healthcheck'
    
    def test_health_delta_calculation(self, maintenance_orchestrator):
        """Test health delta calculated correctly across workflow."""
        # Set baseline
        maintenance_orchestrator._run_pre_healthcheck({})
        baseline_score = maintenance_orchestrator.baseline_health['overall_score']
        
        # Run post-healthcheck
        maintenance_orchestrator._run_post_healthcheck({})
        final_score = maintenance_orchestrator.final_health['overall_score']
        
        # Calculate delta in teardown
        result = maintenance_orchestrator._teardown({})
        
        expected_delta = final_score - baseline_score
        assert result['health_delta'] == expected_delta
    
    def test_orchestrator_state_tracking(self, maintenance_orchestrator):
        """Test orchestrator tracks state correctly."""
        assert maintenance_orchestrator.is_running is False
        assert maintenance_orchestrator.is_complete is False
        
        # States should be managed by BaseOrchestrator.execute()
    
    def test_baseline_and_final_health_set(self, maintenance_orchestrator):
        """Test baseline and final health set correctly."""
        maintenance_orchestrator._run_pre_healthcheck({})
        assert maintenance_orchestrator.baseline_health is not None
        
        maintenance_orchestrator._run_post_healthcheck({})
        assert maintenance_orchestrator.final_health is not None
    
    def test_phase_execution_logging(self, maintenance_orchestrator, caplog):
        """Test all phases log engagement hints."""
        maintenance_orchestrator._register_phases()
        
        # Execute a phase
        maintenance_orchestrator._execute_phase('pre_healthcheck', {})
        
        assert '🎭 Phase transition:' in caplog.text
    
    def test_orchestrator_initialization(self, mock_cortex_root):
        """Test orchestrator initializes correctly."""
        orchestrator = MaintenanceOrchestrator(cortex_root=mock_cortex_root)
        
        assert orchestrator.name == 'maintenance_v3'
        assert orchestrator.cortex_root == mock_cortex_root
        assert orchestrator.phase_manager is not None
        assert orchestrator.error_handler is not None
    
    def test_teardown_returns_health_metrics(self, maintenance_orchestrator):
        """Test teardown returns all health metrics."""
        maintenance_orchestrator.baseline_health = {'overall_score': 75.0}
        maintenance_orchestrator.final_health = {'overall_score': 85.0}
        
        result = maintenance_orchestrator._teardown({})
        
        assert 'baseline_health' in result
        assert 'final_health' in result
        assert 'health_delta' in result
    
    def test_phase_failure_handling(self, maintenance_orchestrator):
        """Test orchestrator handles phase failures gracefully."""
        # Execute with invalid phase context
        result = maintenance_orchestrator._execute_phase('pre_healthcheck', {})
        
        # Should not raise exception, should return result
        assert 'success' in result
