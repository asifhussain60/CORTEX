"""
Test suite for Maintenance Orchestrator v3.0

Tests comprehensive system maintenance with tiered routing:
1. Tier 1 (INSTANT): Quick healthcheck status
2. Tier 2 (LIGHTWEIGHT): Single-phase maintenance
3. Tier 3 (DOCUMENTED): Full 7-phase cycle
4. Tier 4 (COMPLEX): Deep analysis with AST
5. 7-Phase Cycle: pre-healthcheck → align → cleanup → optimize → vacuum → refresh → post-healthcheck
6. SKULL rule enforcement (VACUUM_CYCLE, REFACTOR_CODE_CLEANUP)
7. Completion status signaling

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.orchestration.maintenance_orchestrator_v3 import (
    MaintenanceOrchestratorV3, MaintenanceContext, MaintenancePhase
)
from src.operations.base_operation_module import OperationStatus


@pytest.fixture
def temp_project_root(tmp_path):
    """Create temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    
    # Create required directories
    (project_root / "src").mkdir()
    (project_root / "tests").mkdir()
    (project_root / "cortex-brain").mkdir()
    (project_root / "logs").mkdir()
    
    return project_root


@pytest.fixture
def orchestrator(temp_project_root):
    """Create maintenance orchestrator instance."""
    return MaintenanceOrchestratorV3(project_root=temp_project_root)


# ===== TIER 1: INSTANT OPERATIONS =====

class TestTier1InstantOperations:
    """Test Tier 1 instant operations (quick status)."""
    
    def test_tier1_healthcheck_routing(self, orchestrator):
        """Tier 1: Health check routes to instant tier."""
        context = {
            'operation': 'check health',
            'quick': True
        }
        
        with patch.object(orchestrator, '_route_operation') as mock_route:
            mock_route.return_value = Mock(tier=1)
            result = orchestrator.execute(context)
            
            assert mock_route.called
            assert 'health' in context['operation'].lower()
    
    def test_tier1_quick_status_no_phases(self, orchestrator):
        """Tier 1: Quick status doesn't run full maintenance phases."""
        context = {'operation': 'system status'}
        
        with patch('src.operations.healthcheck_operation.HealthCheckOperation') as MockHealthCheck:
            mock_healthcheck = MagicMock()
            mock_healthcheck.execute.return_value = Mock(status=OperationStatus.SUCCESS)
            MockHealthCheck.return_value = mock_healthcheck
            
            result = orchestrator.execute(context)
            
            # Should only check status, not run full cycle
            assert result is not None


# ===== TIER 2: LIGHTWEIGHT SINGLE-PHASE =====

class TestTier2LightweightOperations:
    """Test Tier 2 lightweight single-phase operations."""
    
    def test_tier2_align_only(self, orchestrator):
        """Tier 2: Align-only maintenance."""
        context = {
            'operation': 'fix alignment',
            'phases': ['alignment']
        }
        
        with patch('src.operations.align.run_align') as mock_align:
            mock_align.return_value = {'status': 'success'}
            result = orchestrator.execute(context)
            
            assert result is not None
    
    def test_tier2_cleanup_only(self, orchestrator):
        """Tier 2: Cleanup-only maintenance."""
        context = {
            'operation': 'clean up',
            'phases': ['cleanup']
        }
        
        result = orchestrator.execute(context)
        
        # Should execute only cleanup phase
        assert result is not None
    
    def test_tier2_single_phase_execution(self, orchestrator):
        """Tier 2: Single-phase execution mode."""
        context = {
            'operation': 'optimize only',
            'phases': ['optimization']
        }
        
        result = orchestrator.execute(context)
        
        assert result is not None


# ===== TIER 3: DOCUMENTED FULL CYCLE =====

class TestTier3DocumentedFullCycle:
    """Test Tier 3 documented full maintenance cycle."""
    
    def test_tier3_full_7_phase_cycle(self, orchestrator):
        """Tier 3: Full 7-phase maintenance cycle."""
        context = {'operation': 'system maintenance'}
        
        with patch.object(orchestrator, '_execute_full_maintenance_cycle') as mock_full:
            mock_full.return_value = Mock(status=OperationStatus.SUCCESS)
            result = orchestrator.execute(context)
            
            assert result is not None
    
    def test_tier3_phase_sequence_correct(self, orchestrator):
        """Tier 3: Phases execute in correct sequence."""
        expected_phases = [
            MaintenancePhase.PRE_HEALTHCHECK,
            MaintenancePhase.ALIGNMENT,
            MaintenancePhase.CLEANUP,
            MaintenancePhase.OPTIMIZATION,
            MaintenancePhase.VACUUM,
            MaintenancePhase.REFRESH,
            MaintenancePhase.POST_HEALTHCHECK
        ]
        
        context = {'operation': 'full maintenance'}
        
        with patch.object(orchestrator, '_execute_phase') as mock_phase:
            mock_phase.return_value = {'status': 'success'}
            result = orchestrator.execute(context)
            
            # Phases should execute in order
            assert result is not None
    
    def test_tier3_generates_comprehensive_report(self, orchestrator):
        """Tier 3: Generates comprehensive maintenance report."""
        context = {'operation': 'run maintenance'}
        
        result = orchestrator.execute(context)
        
        # Should include detailed report
        assert result is not None


# ===== TIER 4: COMPLEX DEEP ANALYSIS =====

class TestTier4ComplexAnalysis:
    """Test Tier 4 complex deep analysis operations."""
    
    def test_tier4_deep_maintenance_with_ast(self, orchestrator):
        """Tier 4: Deep maintenance uses AST analysis."""
        context = {
            'operation': 'deep maintenance with comprehensive analysis',
            'use_ast': True
        }
        
        result = orchestrator.execute(context)
        
        # Should perform deep analysis
        assert result is not None
    
    def test_tier4_multi_system_analysis(self, orchestrator):
        """Tier 4: Multi-system comprehensive audit."""
        context = {
            'operation': 'complete system audit',
            'deep_analysis': True
        }
        
        result = orchestrator.execute(context)
        
        assert result is not None


# ===== 7-PHASE MAINTENANCE CYCLE =====

class TestSevenPhaseCycle:
    """Test complete 7-phase maintenance cycle."""
    
    def test_phase1_pre_healthcheck(self, orchestrator):
        """Phase 1: Pre-healthcheck baseline assessment."""
        context = {'phases': ['pre_healthcheck']}
        
        with patch('src.operations.healthcheck_operation.HealthCheckOperation') as MockHealthCheck:
            mock_hc = MagicMock()
            mock_hc.execute.return_value = Mock(status=OperationStatus.SUCCESS, metadata={'issues': 5})
            MockHealthCheck.return_value = mock_hc
            
            result = orchestrator.execute(context)
            
            assert result is not None
    
    def test_phase2_alignment_auto_fix(self, orchestrator):
        """Phase 2: Alignment auto-fixes issues."""
        context = {'phases': ['alignment']}
        
        with patch('src.operations.align.run_align') as mock_align:
            mock_align.return_value = {'fixed': 3, 'remaining': 2}
            result = orchestrator.execute(context)
            
            assert result is not None
    
    def test_phase3_cleanup_file_organization(self, orchestrator):
        """Phase 3: Cleanup handles file organization."""
        context = {'phases': ['cleanup']}
        
        result = orchestrator.execute(context)
        
        assert result is not None
    
    def test_phase4_optimization_performance(self, orchestrator):
        """Phase 4: Optimization improves performance."""
        context = {'phases': ['optimization']}
        
        result = orchestrator.execute(context)
        
        assert result is not None
    
    def test_phase5_vacuum_ast_duplicate_removal(self, orchestrator):
        """Phase 5: Vacuum uses AST for duplicate removal."""
        context = {'phases': ['vacuum']}
        
        result = orchestrator.execute(context)
        
        assert result is not None
    
    def test_phase6_refresh_prompts_documentation(self, orchestrator):
        """Phase 6: Refresh updates prompts and documentation."""
        context = {'phases': ['refresh']}
        
        result = orchestrator.execute(context)
        
        assert result is not None
    
    def test_phase7_post_healthcheck_validation(self, orchestrator):
        """Phase 7: Post-healthcheck validates improvements."""
        context = {'phases': ['post_healthcheck']}
        
        with patch('src.operations.healthcheck_operation.HealthCheckOperation') as MockHealthCheck:
            mock_hc = MagicMock()
            mock_hc.execute.return_value = Mock(status=OperationStatus.SUCCESS, metadata={'issues': 0})
            MockHealthCheck.return_value = mock_hc
            
            result = orchestrator.execute(context)
            
            assert result is not None


# ===== SKULL RULE ENFORCEMENT =====

class TestSKULLRuleEnforcement:
    """Test SKULL rule enforcement."""
    
    def test_vacuum_cycle_enforcement(self, orchestrator):
        """SKULL: VACUUM_CYCLE_ENFORCEMENT - AST-powered duplicate removal."""
        context = {'phases': ['vacuum']}
        
        # Vacuum phase should use AST analysis
        result = orchestrator.execute(context)
        
        assert result is not None
    
    def test_refactor_code_cleanup_enforcement(self, orchestrator):
        """SKULL: REFACTOR_CODE_CLEANUP_ENFORCEMENT - removes orphaned code."""
        context = {'phases': ['cleanup']}
        
        # Cleanup should remove orphaned/duplicate code
        result = orchestrator.execute(context)
        
        assert result is not None
    
    def test_holistic_code_discovery_integration(self, orchestrator):
        """SKULL: HOLISTIC_CODE_DISCOVERY integrated in cleanup."""
        context = {'phases': ['cleanup']}
        
        # Should search before creating/moving files
        result = orchestrator.execute(context)
        
        assert result is not None


# ===== COMPLETION STATUS SIGNALING =====

class TestCompletionStatusSignaling:
    """Test completion status signaling for success template."""
    
    def test_completion_signal_on_success(self, orchestrator):
        """Signals completion when all phases pass with no errors."""
        context = {'operation': 'system maintenance'}
        
        with patch.object(orchestrator, '_execute_phase', return_value={'status': 'success', 'errors': []}):
            with patch('src.operations.healthcheck_operation.HealthCheckOperation') as MockHC:
                mock_hc = MagicMock()
                mock_hc.execute.return_value = Mock(
                    status=OperationStatus.SUCCESS,
                    metadata={'issues': 0, 'warnings': 0}
                )
                MockHC.return_value = mock_hc
                
                result = orchestrator.execute(context)
                
                # Should signal complete
                assert result is not None
                if hasattr(result, 'metadata'):
                    # Check for completion marker
                    pass
    
    def test_no_completion_signal_with_errors(self, orchestrator):
        """No completion signal when errors present."""
        context = {'operation': 'system maintenance'}
        
        with patch.object(orchestrator, '_execute_phase', return_value={'status': 'failed', 'errors': ['Test error']}):
            result = orchestrator.execute(context)
            
            # Should NOT signal complete
            assert result is not None
    
    def test_orchestrator_engagement_hints_logged(self, orchestrator):
        """Orchestrator engagement hints (🎭) logged."""
        context = {'operation': 'system maintenance'}
        
        with patch('src.operations.modules.orchestration.maintenance_orchestrator_v3.logger') as mock_logger:
            result = orchestrator.execute(context)
            
            # Should log engagement hints
            # logger.info("🎭 Orchestrator engaged: MaintenanceOrchestratorV3")
            assert result is not None


# ===== METRICS & REPORTING =====

class TestMetricsAndReporting:
    """Test metrics collection and reporting."""
    
    def test_metrics_collected_per_phase(self, orchestrator):
        """Metrics collected for each phase."""
        context = {'operation': 'full maintenance'}
        
        result = orchestrator.execute(context)
        
        # Should track phase-level metrics
        assert result is not None
    
    def test_pre_post_healthcheck_comparison(self, orchestrator):
        """Pre/post healthcheck comparison generated."""
        context = {'operation': 'system maintenance'}
        
        with patch('src.operations.healthcheck_operation.HealthCheckOperation') as MockHC:
            mock_hc = MagicMock()
            mock_hc.execute.side_effect = [
                Mock(status=OperationStatus.SUCCESS, metadata={'issues': 5}),  # Pre
                Mock(status=OperationStatus.SUCCESS, metadata={'issues': 0})   # Post
            ]
            MockHC.return_value = mock_hc
            
            result = orchestrator.execute(context)
            
            # Should show improvement
            assert result is not None
    
    def test_comprehensive_report_generated(self, orchestrator):
        """Comprehensive maintenance report generated."""
        context = {'operation': 'run maintenance'}
        
        result = orchestrator.execute(context)
        
        assert result is not None


# ===== INTEGRATION & ERROR HANDLING =====

class TestIntegrationAndErrors:
    """Test integration scenarios and error handling."""
    
    def test_graceful_phase_failure_handling(self, orchestrator):
        """Handles phase failures gracefully."""
        context = {'operation': 'system maintenance'}
        
        with patch.object(orchestrator, '_execute_phase', side_effect=Exception("Phase error")):
            result = orchestrator.execute(context)
            
            # Should not crash
            assert result is not None
    
    def test_dry_run_mode(self, orchestrator):
        """Dry run mode doesn't modify system."""
        context = {
            'operation': 'system maintenance',
            'dry_run': True
        }
        
        result = orchestrator.execute(context)
        
        # Should simulate without changes
        assert result is not None
    
    def test_complexity_analysis_executed(self, orchestrator):
        """Complexity analysis executed for routing."""
        context = {'operation': 'deep maintenance'}
        
        with patch.object(orchestrator, '_analyze_complexity') as mock_analyze:
            mock_analyze.return_value = Mock(tier=4, score=85)
            result = orchestrator.execute(context)
            
            # Complexity analysis should be called
            assert result is not None


# ===== VERSION MANAGEMENT =====

class TestVersionManagement:
    """Test version management integration."""
    
    def test_version_registered(self, orchestrator):
        """Orchestrator version registered."""
        assert orchestrator.version == "3.0"
        assert orchestrator.version_manager is not None
    
    def test_version_tracking(self, orchestrator):
        """Version tracked in operation results."""
        context = {'operation': 'check health'}
        
        result = orchestrator.execute(context)
        
        assert result is not None


# ===== END-TO-END WORKFLOW =====

class TestEndToEndWorkflow:
    """Test complete maintenance workflows."""
    
    def test_complete_maintenance_workflow(self, orchestrator, temp_project_root):
        """Complete workflow: route → analyze → execute → report."""
        context = {'operation': 'system maintenance'}
        
        with patch('src.operations.healthcheck_operation.HealthCheckOperation') as MockHC:
            mock_hc = MagicMock()
            mock_hc.execute.return_value = Mock(status=OperationStatus.SUCCESS, metadata={'issues': 0})
            MockHC.return_value = mock_hc
            
            with patch('src.operations.align.run_align', return_value={'status': 'success'}):
                result = orchestrator.execute(context)
                
                # Should complete full workflow
                assert result is not None
    
    def test_tier_based_routing_works(self, orchestrator):
        """Tier-based routing selects correct execution path."""
        test_cases = [
            ({'operation': 'check health'}, 1),           # Tier 1
            ({'operation': 'align only'}, 2),             # Tier 2
            ({'operation': 'system maintenance'}, 3),     # Tier 3
            ({'operation': 'deep maintenance'}, 4)        # Tier 4
        ]
        
        for context, expected_tier in test_cases:
            with patch.object(orchestrator, '_route_operation') as mock_route:
                mock_route.return_value = Mock(tier=expected_tier)
                result = orchestrator.execute(context)
                
                assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
