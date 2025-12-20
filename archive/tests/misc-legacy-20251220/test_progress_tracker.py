"""
Tests for CORTEX 4.0 Progress Tracker

Validates automated MASTER-PLAN.md updates.
"""

import pytest
from pathlib import Path
from src.core.progress_tracker import ProgressTracker, update_master_plan_progress
import tempfile
import shutil


@pytest.fixture
def temp_master_plan():
    """Create temporary MASTER-PLAN.md for testing."""
    # Create temp directory
    temp_dir = Path(tempfile.mkdtemp())
    master_plan = temp_dir / "MASTER-PLAN.md"
    
    # Minimal master plan content
    content = """# CORTEX 3.0 → 4.0 Migration Master Plan

**Version:** 1.3
**Last Updated:** December 18, 2025
**Current Phase:** Phase 3 (Orchestrator Consolidation)
**Week:** 7 Day 5
**Overall:** 45% Complete

## 📊 MIGRATION PROGRESS TRACKER

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Orchestrator Consolidation                       [███░░░░░░░░░]  25% │
│ Week 7 Days 6-7: TDDOrchestrator v4.0                   [░░░░░]  0%         │
│ Week 8-9: Planning + Scaffolding                        [░░░░░]  0%         │
├─────────────────────────────────────────────────────────────────────────────┤
```

🎯 MILESTONES
├─ ✅ Foundation Validation (Week 3)
├─ ☐ TDD Orchestrator v4.0 Complete (Week 7 Day 7)
├─ ☐ Planning System Migrated (Week 8 End)

📈 METRICS
├─ Orchestrators Migrated: 2/14 (14%)  # ExecutionOrchestrator, DocumentationOrchestrator
├─ Tests Passing: 123/123 (100%)
├─ Test Coverage (Current): 72.5% average → Target: 90%+
│  ├─ phase_manager: 67.15% ⚠️
│  └─ type_extractor: 87.27% ✅
├─ Documentation: 10/200+ docs generated
"""
    
    master_plan.write_text(content, encoding='utf-8')
    
    yield master_plan
    
    # Cleanup
    shutil.rmtree(temp_dir)


class TestProgressTracker:
    """Test ProgressTracker functionality."""
    
    def test_initialization(self, temp_master_plan):
        """Test tracker initializes correctly."""
        tracker = ProgressTracker(master_plan_path=temp_master_plan)
        assert tracker.master_plan == temp_master_plan
    
    def test_initialization_auto_detect(self):
        """Test tracker can auto-detect MASTER-PLAN.md."""
        # This will fail if file doesn't exist, which is expected
        repo_root = Path(__file__).parent.parent.parent
        expected_path = repo_root / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0" / "MASTER-PLAN.md"
        
        if expected_path.exists():
            tracker = ProgressTracker()
            assert tracker.master_plan == expected_path
    
    def test_update_header(self, temp_master_plan):
        """Test header timestamp update."""
        tracker = ProgressTracker(master_plan_path=temp_master_plan)
        content = temp_master_plan.read_text(encoding='utf-8')
        
        updated = tracker._update_header(content, phase="3", week="7", day="7")
        
        assert "Week: 7 Day 7" in updated
        assert "Current Phase: Phase 3" in updated
    
    def test_update_phase_progress(self, temp_master_plan):
        """Test phase progress bar update."""
        tracker = ProgressTracker(master_plan_path=temp_master_plan)
        content = temp_master_plan.read_text(encoding='utf-8')
        
        updated = tracker._update_phase_progress(
            content,
            phase="3",
            week="7",
            day="6-7",
            completion=100,
            orchestrator_name="TDDOrchestrator v4.0"
        )
        
        assert "[█████]  100% ✅ DONE" in updated
    
    def test_update_milestone(self, temp_master_plan):
        """Test milestone completion marking."""
        tracker = ProgressTracker(master_plan_path=temp_master_plan)
        content = temp_master_plan.read_text(encoding='utf-8')
        
        updated = tracker._update_milestone(
            content,
            "TDD Orchestrator v4.0 Complete (Week 7 Day 7)"
        )
        
        assert "✅ TDD Orchestrator v4.0 Complete" in updated
    
    def test_update_metrics(self, temp_master_plan):
        """Test metrics update."""
        tracker = ProgressTracker(master_plan_path=temp_master_plan)
        content = temp_master_plan.read_text(encoding='utf-8')
        
        metrics = {
            "test_count": 26,
            "test_passing": 26,
            "coverage": 81.5,
            "docs_count": 3
        }
        
        updated = tracker._update_metrics(
            content,
            orchestrator_name="TDDOrchestrator v4.0",
            metrics=metrics
        )
        
        # Should increment orchestrator count
        assert "3/14" in updated
        # Should add to orchestrator list
        assert "TDDOrchestrator v4.0" in updated
    
    def test_full_update(self, temp_master_plan):
        """Test complete progress update."""
        tracker = ProgressTracker(master_plan_path=temp_master_plan)
        
        result = tracker.update_master_plan_progress(
            phase="3",
            week="7",
            day="6-7",
            completion_percentage=100,
            milestone_completed="TDD Orchestrator v4.0 Complete (Week 7 Day 7)",
            orchestrator_name="TDDOrchestrator v4.0",
            metrics={
                "test_count": 26,
                "test_passing": 26,
                "coverage": 81.5,
                "docs_count": 3
            }
        )
        
        assert result is True
        
        # Verify file was updated
        updated_content = temp_master_plan.read_text(encoding='utf-8')
        assert "Week: 7 Day 6-7" in updated_content
        assert "✅ TDD Orchestrator v4.0 Complete" in updated_content
        assert "3/14" in updated_content  # Orchestrator count incremented


class TestConvenienceFunction:
    """Test module-level convenience function."""
    
    def test_update_master_plan_progress_function(self, temp_master_plan, monkeypatch):
        """Test convenience function works."""
        # Mock ProgressTracker to use temp file
        original_init = ProgressTracker.__init__
        
        def mock_init(self, master_plan_path=None):
            original_init(self, master_plan_path=temp_master_plan)
        
        monkeypatch.setattr(ProgressTracker, "__init__", mock_init)
        
        result = update_master_plan_progress(
            phase="3",
            week="7",
            day="6-7",
            completion_percentage=100
        )
        
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
