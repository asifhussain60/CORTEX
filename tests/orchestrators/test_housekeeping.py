"""
CORTEX 6.0 Phase 2 - Housekeeping Orchestrator Enhancement Tests

Tests for Phase 2 housekeeping enhancements:
- AC-CLEAN-201: Phase-Boundary Cleanup Framework + Intent Registry
- AC-CLEAN-202: Infrastructure Cleanup Daemon

These tests validate the three-tier housekeeping strategy:
1. Phase-boundary cleanup (mandatory, integrated with phase completion)
2. Semantic cleanup (manual with approval, intent-driven)
3. Infrastructure daemon (autonomous, .gitignore-scoped)

Design reference: cortex-brain/documents/strategy/HOUSEKEEPING-ORCHESTRATOR-ANALYSIS.md

RED PHASE: All tests will fail initially (implementation pending)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

# Import the housekeeping orchestrator (will fail until implementation)
from src.orchestrators.housekeeping_orchestrator import (
    HousekeepingOrchestrator,
    HousekeepingConfig,
    HousekeepingReport,
    PhaseResult,
    HealthScore,
)


# ==============================================================================
# AC-CLEAN-201: Phase-Boundary Cleanup Framework + Intent Registry
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201")
class TestPhaseBoundaryCleanup:
    """Test that housekeeping runs ONLY on manual trigger, never automatically."""
    
    def test_no_automatic_scheduling(self):
        """Test: No cron jobs, file watchers, or automatic triggers."""
        config = HousekeepingConfig(
            workspace_root=Path("/tmp/test"),
            manual_only=True  # Must be True per DOR Q4/Q9
        )
        
        orchestrator = HousekeepingOrchestrator(config)
        
        # Should not have any automatic scheduling
        assert not hasattr(orchestrator, 'scheduler')
        assert not hasattr(orchestrator, 'file_watcher')
        assert not hasattr(orchestrator, 'cron_job')
        assert config.manual_only is True
    
    def test_no_git_hooks(self):
        """Test: No git hooks installed by housekeeping."""
        config = HousekeepingConfig(
            workspace_root=Path("/tmp/test"),
            manual_only=True
        )
        
        orchestrator = HousekeepingOrchestrator(config)
        
        # Should not install git hooks
        assert not hasattr(orchestrator, 'install_git_hooks')
        assert not hasattr(orchestrator, 'pre_commit_hook')
        assert not hasattr(orchestrator, 'post_commit_hook')
    
    def test_manual_execution_required(self):
        """Test: Execution only via explicit execute() call."""
        temp_dir = tempfile.mkdtemp()
        config = HousekeepingConfig(
            workspace_root=Path(temp_dir),
            manual_only=True
        )
        
        orchestrator = HousekeepingOrchestrator(config)
        
        # Should have execute() method for manual invocation
        assert hasattr(orchestrator, 'execute')
        assert callable(orchestrator.execute)
        
        # Execution should require explicit call (not automatic)
        # This is validated by absence of __init__ side effects
    
    def test_user_control_prioritized(self):
        """Test: User has full control over execution timing."""
        config = HousekeepingConfig(
            workspace_root=Path("/tmp/test"),
            manual_only=True,
            allow_background=False  # User must see execution
        )
        
        orchestrator = HousekeepingOrchestrator(config)
        
        # Should respect user control settings
        assert config.manual_only is True
        assert config.allow_background is False


# ==============================================================================
# AC-CLEAN-201: Phase-Boundary Cleanup Workflow Execution
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201")
class TestNinePhaseWorkflow:
    """Test 9-phase housekeeping workflow execution."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nine_phases_defined(self):
        """Test: All 9 phases are defined in orchestrator."""
        phases = self.orchestrator.get_phases()
        
        assert len(phases) == 9
        
        expected_phases = [
            "governance_validation",
            "test_coverage_analysis",
            "audit_log_health_check",
            "brain_tier_sync",
            "cache_cleanup",
            "git_isolation_check",
            "manifest_validation",
            "ac_gap_detection",
            "health_report_generation"
        ]
        
        phase_names = [p.name for p in phases]
        for expected in expected_phases:
            assert expected in phase_names
    
    def test_sequential_execution(self):
        """Test: Phases execute sequentially in correct order."""
        report = self.orchestrator.execute()
        
        # Phases should execute in order
        assert len(report.phase_results) == 9
        
        for i, phase_result in enumerate(report.phase_results):
            assert phase_result.phase_number == i + 1
            
            # Each phase should complete before next starts
            if i > 0:
                prev_phase = report.phase_results[i - 1]
                assert prev_phase.end_time <= phase_result.start_time
    
    def test_phase_failure_handling(self):
        """Test: Phase failures are logged but don't stop execution."""
        # Mock a phase to fail
        with patch.object(self.orchestrator, '_execute_phase_3') as mock_phase:
            mock_phase.side_effect = Exception("Phase 3 failed")
            
            report = self.orchestrator.execute()
            
            # Should still complete all 9 phases
            assert len(report.phase_results) == 9
            
            # Phase 3 should be marked as failed
            phase_3 = report.phase_results[2]
            assert phase_3.status == "FAILED"
            assert "Phase 3 failed" in phase_3.error_message
    
    def test_execution_performance(self):
        """Test: Complete execution in <60 seconds."""
        start_time = datetime.now()
        report = self.orchestrator.execute()
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        
        # Should complete in under 60 seconds
        assert execution_time < 60
        assert report.total_duration_seconds < 60
    
    def test_health_report_generation(self):
        """Test: Health report generated with all phase results."""
        report = self.orchestrator.execute()
        
        assert isinstance(report, HousekeepingReport)
        assert report.timestamp is not None
        assert len(report.phase_results) == 9
        assert hasattr(report, 'overall_health_score')
        assert 0 <= report.overall_health_score <= 100


# ==============================================================================
# AC-CLEAN-201: Governance Rule Validation in Phase Boundary
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201")
class TestGovernanceValidation:
    """Test Phase 1: Governance rule validation."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_governance_rules_loaded(self):
        """Test: Loads CORE governance rules from tier0."""
        # Create mock core-rules.yaml
        governance_dir = Path(self.temp_dir) / "cortex-brain" / "tier0" / "governance"
        governance_dir.mkdir(parents=True, exist_ok=True)
        
        rules_file = governance_dir / "core-rules.yaml"
        rules_file.write_text(yaml.dump({
            'schema_version': '6.0',
            'rules': [
                {'id': 'CORE-001', 'name': 'Test Rule 1'},
                {'id': 'CORE-002', 'name': 'Test Rule 2'}
            ]
        }))
        
        result = self.orchestrator._execute_phase_1()
        
        assert result.status == "SUCCESS"
        assert result.rules_validated >= 2
    
    def test_governance_rule_conflicts_detected(self):
        """Test: Detects conflicting governance rules."""
        governance_dir = Path(self.temp_dir) / "cortex-brain" / "tier0" / "governance"
        governance_dir.mkdir(parents=True, exist_ok=True)
        
        # Create rules with conflicts
        rules_file = governance_dir / "core-rules.yaml"
        rules_file.write_text(yaml.dump({
            'schema_version': '6.0',
            'rules': [
                {'id': 'CORE-001', 'name': 'Rule 1', 'priority': 'P0_CRITICAL'},
                {'id': 'CORE-001', 'name': 'Duplicate Rule', 'priority': 'P1_HIGH'}  # Conflict
            ]
        }))
        
        result = self.orchestrator._execute_phase_1()
        
        assert result.conflicts_detected >= 1
        assert 'CORE-001' in str(result.details)
    
    def test_governance_validation_metrics(self):
        """Test: Reports governance health metrics."""
        result = self.orchestrator._execute_phase_1()
        
        assert hasattr(result, 'rules_validated')
        assert hasattr(result, 'conflicts_detected')
        assert hasattr(result, 'rules_passed')
        assert hasattr(result, 'rules_failed')


# ==============================================================================
# AC-CLEAN-201: Test Coverage Analysis in Phase Boundary
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201")
class TestCoverageAnalysis:
    """Test Phase 2: Test coverage analysis."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_test_suite_analysis(self):
        """Test: Analyzes test suite for coverage gaps."""
        # Create mock test files
        tests_dir = Path(self.temp_dir) / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        
        (tests_dir / "test_example.py").write_text("""
import pytest

@pytest.mark.ac_id("AC-TEST-001")
def test_example():
    pass
""")
        
        result = self.orchestrator._execute_phase_2()
        
        assert result.status == "SUCCESS"
        assert result.test_files_scanned >= 1
        assert hasattr(result, 'coverage_percentage')
    
    def test_orphaned_tests_detected(self):
        """Test: Detects tests without AC-ID markers."""
        tests_dir = Path(self.temp_dir) / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        
        # Test without AC-ID marker
        (tests_dir / "test_orphan.py").write_text("""
def test_orphan():
    pass
""")
        
        result = self.orchestrator._execute_phase_2()
        
        assert result.orphaned_tests_count >= 1
    
    def test_coverage_metrics_reported(self):
        """Test: Reports detailed coverage metrics."""
        result = self.orchestrator._execute_phase_2()
        
        assert hasattr(result, 'test_files_scanned')
        assert hasattr(result, 'total_tests')
        assert hasattr(result, 'tests_with_ac_markers')
        assert hasattr(result, 'orphaned_tests_count')
        assert hasattr(result, 'coverage_percentage')


# ==============================================================================
# AC-CLEAN-201: Audit Log Health Check in Phase Boundary
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201")
class TestAuditLogHealth:
    """Test Phase 3: Audit log health check."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_audit_log_analysis(self):
        """Test: Analyzes audit logs for health issues."""
        # Create mock audit log
        audit_dir = Path(self.temp_dir) / "cortex-brain" / "audit-logs"
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        audit_db = audit_dir / "cortex_audit.db"
        import sqlite3
        conn = sqlite3.connect(audit_db)
        conn.execute("""
            CREATE TABLE audit_log (
                timestamp TEXT,
                level TEXT,
                component TEXT,
                message TEXT
            )
        """)
        conn.execute("""
            INSERT INTO audit_log VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), 'ERROR', 'test', 'Test error'))
        conn.commit()
        conn.close()
        
        result = self.orchestrator._execute_phase_3()
        
        assert result.status == "SUCCESS"
        assert result.audit_entries_analyzed >= 1
    
    def test_error_pattern_detection(self):
        """Test: Detects error patterns in audit logs."""
        audit_dir = Path(self.temp_dir) / "cortex-brain" / "audit-logs"
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        audit_db = audit_dir / "cortex_audit.db"
        import sqlite3
        conn = sqlite3.connect(audit_db)
        conn.execute("""
            CREATE TABLE audit_log (
                timestamp TEXT,
                level TEXT,
                component TEXT,
                message TEXT
            )
        """)
        
        # Insert repeated errors
        for i in range(5):
            conn.execute("""
                INSERT INTO audit_log VALUES (?, ?, ?, ?)
            """, (datetime.now().isoformat(), 'ERROR', 'test', 'Same error repeated'))
        conn.commit()
        conn.close()
        
        result = self.orchestrator._execute_phase_3()
        
        assert result.error_patterns_detected >= 1


# ==============================================================================
# AC-CLEAN-201: Brain Tier Synchronization in Phase Boundary
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201")
class TestBrainTierSync:
    """Test Phase 4: Brain tier synchronization."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_tier_structure_validation(self):
        """Test: Validates 4-tier brain structure exists."""
        # Create mock tier structure
        brain_dir = Path(self.temp_dir) / "cortex-brain"
        for tier in ['tier0', 'tier1', 'tier2', 'tier3']:
            (brain_dir / tier).mkdir(parents=True, exist_ok=True)
        
        result = self.orchestrator._execute_phase_4()
        
        assert result.status == "SUCCESS"
        assert result.tiers_validated == 4
    
    def test_tier_synchronization(self):
        """Test: Synchronizes data across tiers."""
        result = self.orchestrator._execute_phase_4()
        
        assert hasattr(result, 'tiers_validated')
        assert hasattr(result, 'sync_issues_found')
        assert hasattr(result, 'sync_issues_fixed')


# ==============================================================================
# AC-CLEAN-202: Infrastructure Cache Cleanup (Daemon Compatible)
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-202")
class TestCacheCleanup:
    """Test Phase 5: Cache cleanup."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_cleanup_execution(self):
        """Test: Cleans up old cache files."""
        # Create mock cache files
        cache_dir = Path(self.temp_dir) / "cortex-brain" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Old cache file (should be deleted)
        old_cache = cache_dir / "old_cache.json"
        old_cache.write_text("{}")
        
        # Set modification time to 31 days ago
        old_time = (datetime.now() - timedelta(days=31)).timestamp()
        import os
        os.utime(old_cache, (old_time, old_time))
        
        result = self.orchestrator._execute_phase_5()
        
        assert result.status == "SUCCESS"
        assert result.cache_files_deleted >= 1
        assert result.space_reclaimed_mb >= 0
    
    def test_recent_cache_preserved(self):
        """Test: Preserves recent cache files."""
        cache_dir = Path(self.temp_dir) / "cortex-brain" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Recent cache file (should be kept)
        recent_cache = cache_dir / "recent_cache.json"
        recent_cache.write_text("{}")
        
        result = self.orchestrator._execute_phase_5()
        
        # Recent file should still exist
        assert recent_cache.exists()


# ==============================================================================
# AC-CLEAN-202: Git Isolation Verification (Daemon Scope)
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-202")
class TestGitIsolation:
    """Test Phase 6: Git isolation verification."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_git_isolation_check(self):
        """Test: Verifies CORTEX code never commits to user repos."""
        result = self.orchestrator._execute_phase_6()
        
        assert result.status == "SUCCESS"
        assert hasattr(result, 'isolation_violations_found')
        assert result.isolation_violations_found == 0
    
    def test_gitignore_validation(self):
        """Test: Validates .gitignore contains CORTEX patterns."""
        # Create mock .gitignore
        gitignore = Path(self.temp_dir) / ".gitignore"
        gitignore.write_text("cortex-brain/\n")
        
        result = self.orchestrator._execute_phase_6()
        
        assert result.gitignore_valid is True


# ==============================================================================
# AC-CLEAN-201: Acceptance Criteria Gap Detection in Phase Boundary
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201")
class TestACGapDetection:
    """Test Phase 8: AC gap detection."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = HousekeepingConfig(
            workspace_root=Path(self.temp_dir),
            manual_only=True
        )
        self.orchestrator = HousekeepingOrchestrator(self.config)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ac_gap_detection(self):
        """Test: Detects AC without test coverage."""
        result = self.orchestrator._execute_phase_8()
        
        assert result.status == "SUCCESS"
        assert hasattr(result, 'total_ac_defined')
        assert hasattr(result, 'ac_without_tests')
        assert hasattr(result, 'coverage_percentage')
    
    def test_critical_gaps_flagged(self):
        """Test: Flags P0_CRITICAL AC without coverage."""
        result = self.orchestrator._execute_phase_8()
        
        assert hasattr(result, 'critical_gaps')
        assert isinstance(result.critical_gaps, list)


# ==============================================================================
# Integration Tests
# ==============================================================================

@pytest.mark.ac_id("AC-CLEAN-201", "AC-CLEAN-202")
class TestHousekeepingIntegration:
    """Integration tests for full housekeeping workflow."""
    
    def test_full_housekeeping_execution(self):
        """Test: Complete housekeeping run from start to finish."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            config = HousekeepingConfig(
                workspace_root=Path(temp_dir),
                manual_only=True
            )
            
            orchestrator = HousekeepingOrchestrator(config)
            report = orchestrator.execute()
            
            # Should complete all 9 phases
            assert len(report.phase_results) == 9
            
            # Should have overall health score
            assert 0 <= report.overall_health_score <= 100
            
            # Should generate report file
            assert report.report_path is not None
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_health_score_calculation(self):
        """Test: Health score calculated based on phase results."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            config = HousekeepingConfig(
                workspace_root=Path(temp_dir),
                manual_only=True
            )
            
            orchestrator = HousekeepingOrchestrator(config)
            report = orchestrator.execute()
            
            # Health score should be weighted average of phase scores
            assert isinstance(report.overall_health_score, (int, float))
            assert 0 <= report.overall_health_score <= 100
            
            # Each phase should contribute to score
            for phase_result in report.phase_results:
                assert hasattr(phase_result, 'health_contribution')
            
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
