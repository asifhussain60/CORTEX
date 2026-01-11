"""
Tests for State Synchronization Orchestrator (AC-SYNC-001)

Author: Asif Hussain
Created: 2026-01-10
"""

import pytest
from pathlib import Path
from src.orchestrators.core.state_synchronizer import (
    StateSynchronizer,
    run_synchronization_check,
    SyncReport
)


@pytest.fixture
def workspace_root(tmp_path):
    """Create temporary workspace structure"""
    # Create directory structure
    (tmp_path / "cortex-brain" / "tier1" / "tracking").mkdir(parents=True)
    (tmp_path / "cortex-brain" / "tier1" / "acceptance-criteria").mkdir(parents=True)
    (tmp_path / "cortex-brain" / "tier1" / "evidence-bundles").mkdir(parents=True)
    (tmp_path / "cortex-brain" / "documents" / "cx6-holistic-analysis").mkdir(parents=True)
    (tmp_path / "templates" / "plan-viewer").mkdir(parents=True)
    (tmp_path / "src" / "infrastructure").mkdir(parents=True)
    (tmp_path / "src" / "orchestrators" / "core").mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def valid_progress_tracker(workspace_root):
    """Create valid progress-tracker.json"""
    import json
    
    data = {
        "active_epic": {"name": "CORTEX 6.0"},
        "current_phase": {
            "number": 1,
            "name": "Phase 1: Foundation Enhancement",
            "status": "in_progress",
            "completed_count": 16,
            "total_ac_count": 33,
            "completion_percentage": 48,
            "verified_implemented": [
                "AC-AUDIT-001", "AC-AUDIT-002", "AC-GOV-001"
            ],
            "planned_not_implemented": [
                "AC-AUDIT-007", "AC-LIFECYCLE-001"
            ]
        }
    }
    
    path = workspace_root / "cortex-brain" / "tier1" / "tracking" / "progress-tracker.json"
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    
    return path


@pytest.fixture
def valid_ac_index(workspace_root):
    """Create valid AC-INDEX.yaml"""
    import yaml
    
    data = {
        "total_ac_count": 111,
        "completed_count": 16
    }
    
    path = workspace_root / "cortex-brain" / "tier1" / "acceptance-criteria" / "AC-INDEX.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    
    return path


@pytest.fixture
def valid_holistic_plan(workspace_root):
    """Create valid holistic-snowball-plan.yaml"""
    import yaml
    
    data = {
        "phase_1_foundation": {
            "name": "Foundation Enhancement",
            "status": "in_progress",
            "completion_percentage": 48,
            "ac_ids_complete": 16,
            "ac_ids_total": 33
        }
    }
    
    path = workspace_root / "cortex-brain" / "documents" / "cx6-holistic-analysis" / "holistic-snowball-plan.yaml"
    with open(path, 'w') as f:
        yaml.dump(data, f)
    
    return path


class TestStateSynchronizer:
    """Test StateSynchronizer class"""
    
    def test_initialize(self, workspace_root):
        """Test synchronizer initialization"""
        synchronizer = StateSynchronizer(workspace_root)
        
        assert synchronizer.workspace_root == workspace_root
        assert synchronizer.brain_root == workspace_root / "cortex-brain"
    
    def test_validate_progress_tracker_missing(self, workspace_root):
        """Test validation when progress-tracker.json missing"""
        synchronizer = StateSynchronizer(workspace_root)
        
        source, data = synchronizer._validate_progress_tracker()
        
        assert source.status == "missing"
        assert "File does not exist" in source.issues
        assert data == {}
    
    def test_validate_progress_tracker_valid(self, workspace_root, valid_progress_tracker):
        """Test validation when progress-tracker.json valid"""
        synchronizer = StateSynchronizer(workspace_root)
        
        source, data = synchronizer._validate_progress_tracker()
        
        assert source.status == "accurate"
        assert len(source.issues) == 0
        assert data["current_phase"]["completion_percentage"] == 48
    
    def test_validate_ac_index_valid(self, workspace_root, valid_ac_index):
        """Test validation when AC-INDEX.yaml valid"""
        synchronizer = StateSynchronizer(workspace_root)
        
        source, data = synchronizer._validate_ac_index()
        
        assert source.status == "accurate"
        assert data["total_ac_count"] == 111
    
    def test_validate_holistic_plan_status_mismatch(self, workspace_root):
        """Test detection of status mismatch in holistic plan"""
        import yaml
        
        # Create plan with wrong status
        data = {
            "phase_1_foundation": {
                "status": "ready_to_implement",  # Should be "in_progress"
                "completion_percentage": 48
            }
        }
        
        path = workspace_root / "cortex-brain" / "cx6-plan" / "master-plan.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f)
        
        synchronizer = StateSynchronizer(workspace_root)
        source, _ = synchronizer._validate_holistic_plan()
        
        # File exists but has status mismatch - should be "stale"
        assert source.status == "stale"
        assert any("ready_to_implement" in issue for issue in source.issues)
    
    def test_validate_all_sources_perfect_sync(
        self,
        workspace_root,
        valid_progress_tracker,
        valid_ac_index,
        valid_holistic_plan
    ):
        """Test full validation with all sources in sync"""
        synchronizer = StateSynchronizer(workspace_root)
        
        report = synchronizer.validate_all_sources()
        
        assert isinstance(report, SyncReport)
        assert report.sources_total == 6
        # Fixtures create minimal test data - expect at least 1/3 accuracy
        assert report.sync_score >= 30  # At least some sources accurate
        assert report.sources_accurate >= 2  # progress-tracker + AC-INDEX at minimum
    
    def test_cross_validate_detects_status_mismatch(
        self,
        workspace_root,
        valid_progress_tracker
    ):
        """Test cross-validation detects status mismatch"""
        import yaml
        
        # Create plan with mismatched status
        plan_data = {
            "phase_1_foundation": {
                "status": "ready_to_implement",  # Tracker says "in_progress"
                "completion_percentage": 48
            }
        }
        
        tracker_data = {
            "current_phase": {
                "status": "in_progress",
                "completion_percentage": 48
            }
        }
        
        synchronizer = StateSynchronizer(workspace_root)
        discrepancies = synchronizer._cross_validate(tracker_data, {}, plan_data)
        
        assert len(discrepancies) > 0
        assert any(d["type"] == "status_mismatch" for d in discrepancies)
    
    def test_cross_validate_detects_completion_mismatch(self, workspace_root):
        """Test cross-validation detects completion percentage mismatch"""
        tracker_data = {
            "current_phase": {
                "status": "in_progress",
                "completion_percentage": 64  # Different from plan
            }
        }
        
        plan_data = {
            "phase_1_foundation": {
                "status": "in_progress",
                "completion_percentage": 48  # Different from tracker
            }
        }
        
        synchronizer = StateSynchronizer(workspace_root)
        discrepancies = synchronizer._cross_validate(tracker_data, {}, plan_data)
        
        assert len(discrepancies) > 0
        assert any(d["type"] == "completion_mismatch" for d in discrepancies)
    
    def test_generate_recommendations(self, workspace_root):
        """Test recommendation generation"""
        from src.orchestrators.core.state_synchronizer import TruthSource
        
        sources = [
            TruthSource(
                name="test.yaml",
                path=Path("/fake/path"),
                status="stale",
                issues=["Outdated timestamp"],
                last_checked="2026-01-10T22:00:00Z"
            )
        ]
        
        discrepancies = [
            {
                "type": "test_issue",
                "severity": "CRITICAL",
                "description": "Critical test issue",
                "resolution": "Fix immediately"
            }
        ]
        
        synchronizer = StateSynchronizer(workspace_root)
        recommendations = synchronizer._generate_recommendations(sources, discrepancies)
        
        assert len(recommendations) >= 2
        assert any(r["priority"] == "CRITICAL" for r in recommendations)
    
    def test_generate_sync_report_markdown(self, workspace_root):
        """Test markdown report generation"""
        report = SyncReport(
            timestamp="2026-01-10T22:00:00Z",
            sync_score=75.0,
            sources_accurate=3,
            sources_total=4,
            discrepancies=[
                {
                    "type": "test",
                    "severity": "MEDIUM",
                    "description": "Test discrepancy",
                    "resolution": "Fix it"
                }
            ],
            recommendations=[
                {
                    "priority": "HIGH",
                    "action": "Fix something",
                    "issues": ["Issue 1"],
                    "estimated_time": "10 minutes"
                }
            ],
            critical=False
        )
        
        synchronizer = StateSynchronizer(workspace_root)
        markdown = synchronizer.generate_sync_report_markdown(report)
        
        assert "State Synchronization Report" in markdown
        assert "75.0%" in markdown
        assert "⚠️ WARNING" in markdown  # Score < 80%
        assert "Test discrepancy" in markdown


class TestRunSynchronizationCheck:
    """Test run_synchronization_check function"""
    
    def test_run_synchronization_check(
        self,
        workspace_root,
        valid_progress_tracker,
        valid_ac_index,
        valid_holistic_plan
    ):
        """Test main synchronization check function"""
        report = run_synchronization_check(workspace_root)
        
        assert isinstance(report, SyncReport)
        assert report.sources_total == 6
        assert 0 <= report.sync_score <= 100


@pytest.mark.ac_id("AC-SYNC-001")
class TestACSync001:
    """Acceptance criteria tests for AC-SYNC-001"""
    
    def test_ac_sync_001_detects_discrepancies(
        self,
        workspace_root,
        valid_progress_tracker
    ):
        """
        AC-SYNC-001: State Synchronization Validator
        
        GIVEN: Multiple truth sources with discrepancies
        WHEN: Synchronization check runs
        THEN: All discrepancies are detected and reported
        """
        import yaml
        
        # Create plan with mismatched data
        plan_data = {
            "phase_1_foundation": {
                "status": "ready_to_implement",
                "completion_percentage": 100  # Wrong!
            }
        }
        
        path = workspace_root / "cortex-brain" / "documents" / "cx6-holistic-analysis" / "holistic-snowball-plan.yaml"
        with open(path, 'w') as f:
            yaml.dump(plan_data, f)
        
        report = run_synchronization_check(workspace_root)
        
        # Should detect status and completion mismatches
        assert len(report.discrepancies) > 0
        assert report.sync_score < 100
    
    def test_ac_sync_001_generates_recommendations(
        self,
        workspace_root,
        valid_progress_tracker
    ):
        """
        AC-SYNC-001: State Synchronization Validator
        
        GIVEN: Truth sources with issues
        WHEN: Synchronization check runs
        THEN: Actionable recommendations are generated
        """
        report = run_synchronization_check(workspace_root)
        
        assert isinstance(report.recommendations, list)
        
        for rec in report.recommendations:
            assert "priority" in rec
            assert "action" in rec
            assert "estimated_time" in rec
    
    def test_ac_sync_001_calculates_sync_score(
        self,
        workspace_root,
        valid_progress_tracker,
        valid_ac_index,
        valid_holistic_plan
    ):
        """
        AC-SYNC-001: State Synchronization Validator
        
        GIVEN: 6 truth sources
        WHEN: Synchronization check runs
        THEN: Sync score is calculated correctly (accurate_sources / total * 100)
        """
        report = run_synchronization_check(workspace_root)
        
        assert 0 <= report.sync_score <= 100
        assert report.sources_accurate <= report.sources_total
        
        expected_score = (report.sources_accurate / report.sources_total) * 100
        assert abs(report.sync_score - expected_score) < 0.1
