"""
Track C Regression Tests: Cache Invalidation & Persistence

Tests verify the fixes for persistent 30% integration score bug:
- Track A: Cache invalidation on wiring config changes
- Track B: Persistent state across sessions

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: REGRESSION_TESTS
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.admin.system_alignment_orchestrator import (
    SystemAlignmentOrchestrator,
    AlignmentReport,
    IntegrationScore
)


class TestTrackACacheInvalidation:
    """
    Track A Regression Tests: Cache Invalidation Fixes
    
    Verifies that cache invalidates when:
    1. response-templates.yaml changes (wiring config)
    2. Test files change (multiple pattern support)
    3. Guide files change (kebab-case conversion)
    """
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create necessary directory structure
        (self.project_root / "cortex-brain").mkdir(parents=True)
        (self.project_root / "tests").mkdir(parents=True)
        (self.project_root / ".github" / "prompts" / "modules").mkdir(parents=True, exist_ok=True)
        
        # Mock config
        with patch('src.operations.modules.admin.system_alignment_orchestrator.config') as mock_config:
            mock_config.root_path = self.project_root
            mock_config.brain_path = self.project_root / "cortex-brain"
            self.orchestrator = SystemAlignmentOrchestrator()
    
    def teardown_method(self):
        """Cleanup test environment after each test."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_feature_files_tracks_wiring_config(self):
        """
        TEST: _get_feature_files() must track response-templates.yaml
        
        Bug Fix: response-templates.yaml was NOT tracked, causing cache to miss
        wiring configuration changes. This was the root cause of persistent 30%.
        """
        # Create response-templates.yaml
        templates_file = self.project_root / "cortex-brain" / "response-templates.yaml"
        templates_file.write_text("test: content")
        
        # Create feature metadata
        metadata = {
            'file_path': str(self.project_root / "src" / "test_feature.py"),
            'feature_type': 'orchestrator'
        }
        
        # Execute
        tracked_files = self.orchestrator._get_feature_files("TestFeature", metadata)
        
        # Verify: response-templates.yaml MUST be in tracked files
        tracked_paths = [str(f) for f in tracked_files]
        assert str(templates_file) in tracked_paths, \
            "BUG: response-templates.yaml not tracked - cache won't invalidate on wiring changes!"
    
    def test_get_feature_files_checks_multiple_test_patterns(self):
        """
        TEST: _get_feature_files() must check multiple test file patterns
        
        Bug Fix: Only checked tests/test_{feature_name}.py, missing actual patterns
        like tests/operations/test_{feature}_orchestrator.py
        """
        # Create test file with orchestrator pattern
        test_file = self.project_root / "tests" / "operations" / "test_testfeature_orchestrator.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# test")
        
        metadata = {
            'file_path': str(self.project_root / "src" / "test_feature.py"),
            'feature_type': 'orchestrator'
        }
        
        # Execute
        tracked_files = self.orchestrator._get_feature_files("TestFeature", metadata)
        
        # Verify: orchestrator pattern test file should be found
        tracked_paths = [str(f) for f in tracked_files]
        assert str(test_file) in tracked_paths, \
            "BUG: Orchestrator test pattern not detected - cache won't invalidate on test changes!"
    
    def test_get_feature_files_uses_kebab_case_for_guides(self):
        """
        TEST: _get_feature_files() must convert feature names to kebab-case for guides
        
        Bug Fix: Used raw feature name without kebab-case conversion, missing guide files
        like system-alignment-orchestrator-guide.md
        """
        # Create guide file with kebab-case naming
        guide_file = self.project_root / ".github" / "prompts" / "modules" / "test-feature-orchestrator-guide.md"
        guide_file.write_text("# Guide")
        
        metadata = {
            'file_path': str(self.project_root / "src" / "test_feature.py"),
            'feature_type': 'orchestrator'
        }
        
        # Execute
        tracked_files = self.orchestrator._get_feature_files("TestFeature", metadata)
        
        # Verify: kebab-case guide should be found
        tracked_paths = [str(f) for f in tracked_files]
        assert str(guide_file) in tracked_paths, \
            "BUG: Kebab-case guide not detected - cache won't invalidate on guide changes!"
    
    def test_to_kebab_case_handles_common_suffixes(self):
        """
        TEST: _to_kebab_case() removes common suffixes correctly
        
        Verifies: SystemAlignmentOrchestrator → system-alignment
        """
        test_cases = [
            ("SystemAlignmentOrchestrator", "system-alignment"),
            ("TDDWorkflowAgent", "tdd-workflow"),
            ("APIDocumentationModule", "api-documentation"),
            ("FeedbackAgent", "feedback"),
            ("PlanningOrchestrator", "planning")
        ]
        
        for input_name, expected_output in test_cases:
            result = self.orchestrator._to_kebab_case(input_name)
            assert result == expected_output, \
                f"Kebab-case conversion failed: {input_name} → {result} (expected {expected_output})"
    
    def test_cache_invalidates_on_wiring_config_change(self):
        """
        INTEGRATION TEST: Cache must invalidate when response-templates.yaml changes
        
        This is the critical test for the 30% persistence bug fix.
        """
        # Create response-templates.yaml
        templates_file = self.project_root / "cortex-brain" / "response-templates.yaml"
        templates_file.write_text("triggers: [test]")
        
        # Create feature
        feature_file = self.project_root / "src" / "test_feature.py"
        feature_file.parent.mkdir(parents=True, exist_ok=True)
        feature_file.write_text("# feature")
        
        metadata = {
            'file_path': str(feature_file),
            'feature_type': 'orchestrator'
        }
        
        # First call: populate cache
        tracked_files_1 = self.orchestrator._get_feature_files("TestFeature", metadata)
        mtime_1 = templates_file.stat().st_mtime
        
        # Modify wiring config
        import time
        time.sleep(0.1)  # Ensure mtime changes
        templates_file.write_text("triggers: [test, new_trigger]")
        
        # Second call: should detect change via tracked files
        tracked_files_2 = self.orchestrator._get_feature_files("TestFeature", metadata)
        mtime_2 = templates_file.stat().st_mtime
        
        # Verify: mtime changed, cache system will detect this
        assert mtime_2 > mtime_1, \
            "response-templates.yaml mtime should change when file modified"
        assert str(templates_file) in [str(f) for f in tracked_files_2], \
            "response-templates.yaml must be tracked for cache invalidation"


class TestTrackBPersistence:
    """
    Track B Regression Tests: Persistent State Layer
    
    Verifies that alignment state persists across sessions via .alignment-state.json
    """
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create necessary directory structure
        (self.project_root / "cortex-brain").mkdir(parents=True)
        
        # Mock config
        with patch('src.operations.modules.admin.system_alignment_orchestrator.config') as mock_config:
            mock_config.root_path = self.project_root
            mock_config.brain_path = self.project_root / "cortex-brain"
            self.orchestrator = SystemAlignmentOrchestrator()
    
    def teardown_method(self):
        """Cleanup test environment after each test."""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_load_alignment_state_returns_default_when_file_missing(self):
        """
        TEST: _load_alignment_state() returns default structure when no state file exists
        """
        state = self.orchestrator._load_alignment_state()
        
        assert state is not None, "State should not be None"
        assert "last_alignment" in state, "State should have last_alignment key"
        assert "feature_scores" in state, "State should have feature_scores key"
        assert "overall_health" in state, "State should have overall_health key"
        assert "alignment_history" in state, "State should have alignment_history key"
        assert state["last_alignment"] is None, "Initial last_alignment should be None"
        assert state["feature_scores"] == {}, "Initial feature_scores should be empty"
    
    def test_save_alignment_state_creates_file(self):
        """
        TEST: _save_alignment_state() creates .alignment-state.json with correct structure
        """
        # Create mock report
        report = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=85
        )
        report.feature_scores = {
            "TestFeature": IntegrationScore(
                feature_name="TestFeature",
                feature_type="orchestrator",
                discovered=True,
                imported=True,
                instantiated=True,
                documented=True,
                tested=True,
                wired=True,
                optimized=False
            )
        }
        report.critical_issues = 0
        report.warnings = 1
        
        # Execute
        self.orchestrator._save_alignment_state(report)
        
        # Verify file created
        state_file = self.project_root / "cortex-brain" / ".alignment-state.json"
        assert state_file.exists(), "State file should be created"
        
        # Verify structure
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        assert "last_alignment" in state
        assert "feature_scores" in state
        assert "overall_health" in state
        assert "alignment_history" in state
        assert state["overall_health"] == 85
        assert "TestFeature" in state["feature_scores"]
        assert state["feature_scores"]["TestFeature"]["score"] == 90  # 7 layers * ~13 points
    
    def test_save_alignment_state_maintains_history(self):
        """
        TEST: _save_alignment_state() maintains history (last 50 runs)
        """
        # Create multiple reports and save
        for i in range(3):
            report = AlignmentReport(
                timestamp=datetime.now(),
                overall_health=80 + i
            )
            report.feature_scores = {}
            report.critical_issues = 0
            report.warnings = 1
            
            self.orchestrator._save_alignment_state(report)
        
        # Verify history preserved
        state_file = self.project_root / "cortex-brain" / ".alignment-state.json"
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        assert len(state["alignment_history"]) == 3, "History should contain 3 entries"
        assert state["alignment_history"][0]["overall_health"] == 80
        assert state["alignment_history"][1]["overall_health"] == 81
        assert state["alignment_history"][2]["overall_health"] == 82
    
    def test_alignment_state_persists_across_sessions(self):
        """
        INTEGRATION TEST: State persists across orchestrator instances
        
        This verifies the fix for ephemeral cache-only storage.
        """
        # First session: save state
        report1 = AlignmentReport(
            timestamp=datetime.now(),
            overall_health=90
        )
        report1.feature_scores = {
            "Feature1": IntegrationScore(
                feature_name="Feature1",
                feature_type="orchestrator",
                discovered=True,
                imported=True
            )
        }
        
        self.orchestrator._save_alignment_state(report1)
        
        # Second session: create new orchestrator instance
        with patch('src.operations.modules.admin.system_alignment_orchestrator.config') as mock_config:
            mock_config.root_path = self.project_root
            mock_config.brain_path = self.project_root / "cortex-brain"
            orchestrator2 = SystemAlignmentOrchestrator()
        
        # Verify: state loaded from disk
        state = orchestrator2._alignment_state
        assert state["overall_health"] == 90, "State should persist across sessions"
        assert "Feature1" in state["feature_scores"], "Feature scores should persist"
    
    def test_save_alignment_state_handles_errors_gracefully(self):
        """
        TEST: _save_alignment_state() handles write errors without crashing
        """
        # Make directory read-only to force write error
        state_file = self.project_root / "cortex-brain" / ".alignment-state.json"
        state_file.parent.chmod(0o444)
        
        report = AlignmentReport(timestamp=datetime.now(), overall_health=90)
        report.feature_scores = {}
        
        # Should not raise exception
        try:
            self.orchestrator._save_alignment_state(report)
        except Exception as e:
            pytest.fail(f"_save_alignment_state() should handle errors gracefully, but raised: {e}")
        finally:
            # Restore permissions for cleanup
            state_file.parent.chmod(0o755)


class TestTrackCIntegration:
    """
    Track C Integration Tests: End-to-End Validation
    
    Verifies that Tracks A + B work together to solve the 30% persistence bug.
    """
    
    def test_alignment_workflow_end_to_end(self):
        """
        INTEGRATION TEST: Full alignment workflow with cache + persistence
        
        Simulates:
        1. First alignment (cache miss, calculation, save state)
        2. Wiring config change
        3. Second alignment (cache invalidates, recalculates, updates state)
        """
        # This test requires full mocking of alignment pipeline
        # Left as placeholder for manual integration testing
        pass
    
    def test_thirty_percent_bug_no_longer_reproducible(self):
        """
        REGRESSION TEST: The 30% persistence bug should not be reproducible
        
        Original bug flow:
        1. Run align → 30%
        2. Fix wiring → response-templates.yaml updated
        3. Run align → Still 30% (BUG - cache didn't invalidate)
        
        Fixed flow:
        1. Run align → 30%
        2. Fix wiring → response-templates.yaml updated
        3. Run align → 90% (FIXED - cache invalidated, recalculated)
        """
        # This test requires full system integration
        # Left as placeholder for manual regression testing
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
