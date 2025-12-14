"""
Tests for Planning Orchestrator v3.0 - INTEGRATION TESTS

**NO MOCKS - Uses real TieredRouter, ComplexityAnalyzer, VersionManager**

Validates tiered routing, complexity analysis integration,
version management, and cycle invocation with actual components.

Phase 03 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator


@pytest.fixture
def orchestrator():
    """Create PlanningOrchestrator with real integrations."""
    return PlanningOrchestrator(project_root=Path("/test"))


class TestInitialization:
    """Test orchestrator initialization with real components."""
    
    def test_initialization(self, orchestrator):
        """Validate all real components initialized."""
        assert orchestrator.version == "3.0"
        assert orchestrator.tiered_router is not None
        assert orchestrator.complexity_analyzer is not None
        assert orchestrator.version_manager is not None
        assert orchestrator.metrics['operations_processed'] == 0
        
        # Verify real version registration
        registered_version = orchestrator.version_manager.get_orchestrator_version("planning_orchestrator")
        assert registered_version == "3.0"
    
    def test_metadata(self, orchestrator):
        """Verify orchestrator metadata."""
        metadata = orchestrator.get_metadata()
        assert metadata.module_id == "planning_orchestrator_v3"
        assert metadata.version == "3.0.0"
        assert metadata.name == "Planning Orchestrator 3.0"
        assert "planning-system-3.0" in metadata.tags


class TestRealTierClassification:
    """Test with REAL TieredRouter - no mocks."""
    
    def test_tier1_instant(self, orchestrator):
        """Tier 1: healthcheck → instant execution."""
        result = orchestrator.execute({'operation': 'healthcheck'})
        
        assert result.success is True
        assert result.data['tier'] == 1
        assert orchestrator.metrics['tier_breakdown'][1] == 1
    
    def test_tier2_lightweight(self, orchestrator):
        """Tier 2: single-file edit → lightweight planning."""
        result = orchestrator.execute({'operation': 'fix typo in config.py'})
        
        assert result.success is True
        assert result.data['tier'] == 2
        assert result.data['execution_result']['plan_type'] == 'inline'
        assert orchestrator.metrics['tier_breakdown'][2] == 1
    
    def test_tier3_documented(self, orchestrator):
        """Tier 3: multi-file feature → documented planning."""
        result = orchestrator.execute({'operation': 'implement JWT authentication'})
        
        assert result.success is True
        assert result.data['tier'] == 3
        assert result.data['execution_result']['plan_created'] is True
        assert result.data['execution_result']['plan_type'] == 'markdown'
        assert orchestrator.metrics['tier_breakdown'][3] == 1
        assert orchestrator.metrics['refactor_cycles_run'] == 1
        assert orchestrator.metrics['vacuum_cycles_run'] == 1
    
    def test_tier4_complex(self, orchestrator):
        """Tier 4: architecture + security → complex planning."""
        # Security keywords trigger HIGH complexity → Tier 4
        result = orchestrator.execute({'operation': 'redesign authentication system with OAuth2'})
        
        assert result.success is True
        assert result.data['tier'] == 4
        assert result.data['execution_result']['plan_created'] is True
        assert result.data['execution_result']['plan_type'] == 'nested_markdown'
        assert orchestrator.metrics['tier_breakdown'][4] == 1
        assert orchestrator.metrics['refactor_cycles_run'] == 1
        assert orchestrator.metrics['vacuum_cycles_run'] == 1


class TestForceTierOverride:
    """Test manual tier override (bypasses routing)."""
    
    def test_force_tier4(self, orchestrator):
        """Force Tier 4 on simple operation."""
        result = orchestrator.execute({
            'operation': 'simple task',
            'force_tier': 4
        })
        
        assert result.success is True
        assert result.data['tier'] == 4
        assert orchestrator.metrics['refactor_cycles_run'] == 1
        assert orchestrator.metrics['vacuum_cycles_run'] == 1


class TestCycleIntegration:
    """Test refactor/vacuum cycle invocation."""
    
    def test_cycles_run_tier3(self, orchestrator):
        """Tier 3+ operations trigger refactor/vacuum."""
        result = orchestrator.execute({'operation': 'add feature X'})
        
        assert result.success is True
        assert result.data['tier'] == 3
        assert orchestrator.metrics['refactor_cycles_run'] == 1
        assert orchestrator.metrics['vacuum_cycles_run'] == 1
    
    def test_cycles_skip_tier1(self, orchestrator):
        """Tier 1 operations skip cycles."""
        result = orchestrator.execute({'operation': 'healthcheck'})
        
        assert result.success is True
        assert result.data['tier'] == 1
        assert orchestrator.metrics['refactor_cycles_run'] == 0
        assert orchestrator.metrics['vacuum_cycles_run'] == 0
    
    def test_skip_refactor_flag(self, orchestrator):
        """skip_refactor flag disables refactor cycle."""
        result = orchestrator.execute({
            'operation': 'add feature Y',
            'skip_refactor': True
        })
        
        assert result.success is True
        assert orchestrator.metrics['refactor_cycles_run'] == 0
        assert orchestrator.metrics['vacuum_cycles_run'] == 1  # Still runs


class TestVersionIntegration:
    """Test real VersionManager integration."""
    
    def test_version_registration(self, orchestrator):
        """Orchestrator registers with VersionManager."""
        version = orchestrator.version_manager.get_orchestrator_version("planning_orchestrator")
        assert version == "3.0"
    
    def test_version_info(self, orchestrator):
        """Can retrieve version info dict."""
        version_info = orchestrator.get_version_info()
        assert version_info['version'] == "3.0"
        assert version_info['orchestrator'] == "planning_orchestrator"


class TestMetricsTracking:
    """Test metrics accumulation across operations."""
    
    def test_metrics_updated(self, orchestrator):
        """Metrics track multiple operations."""
        orchestrator.execute({'operation': 'feature 1'})
        orchestrator.execute({'operation': 'feature 2'})
        
        metrics = orchestrator.get_metrics()
        assert metrics['operations_processed'] == 2
        assert sum(metrics['tier_breakdown'].values()) == 2


class TestErrorHandling:
    """Test error scenarios."""
    
    def test_empty_operation(self, orchestrator):
        """Empty operation returns error."""
        result = orchestrator.execute({'operation': ''})
        
        assert result.success is False
        assert 'error' in result.message.lower() or result.status.value == 'failed'
    
    def test_missing_operation_key(self, orchestrator):
        """Missing 'operation' key returns error."""
        result = orchestrator.execute({})
        
        assert result.success is False
        assert 'error' in result.message.lower() or result.status.value == 'failed'


class TestCompletionStatus:
    """Test is_complete flag behavior."""
    
    def test_is_complete_true_no_errors(self, orchestrator):
        """Success + no errors → is_complete=True."""
        result = orchestrator.execute({'operation': 'add feature Z'})
        
        assert result.success is True
        assert result.data['is_complete'] is True
    
    def test_is_complete_false_with_errors(self, orchestrator):
        """Success + errors → is_complete=False."""
        # Force error by adding to metrics
        orchestrator.metrics['errors'].append("Test error")
        result = orchestrator.execute({'operation': 'add feature W'})
        
        assert result.success is True  # Execution succeeds
        assert result.data['is_complete'] is False  # But has errors
