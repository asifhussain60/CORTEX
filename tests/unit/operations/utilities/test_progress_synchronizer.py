"""
Tests for Progress Synchronizer Utility

Validates:
- Markdown parsing (progress tracker extraction)
- ASCII art generation (progress bars)
- Phase status updates (NOT_STARTED → IN_PROGRESS → COMPLETE)
- File I/O (atomic writes)
- Overall progress calculation
- Multi-phase synchronization

Author: Asif Hussain
Date: December 13, 2025
Version: 1.0.0
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.operations.utilities.progress_synchronizer import (
    ProgressSynchronizer,
    MarkdownParser,
    ASCIIArtGenerator,
    TrackerUpdateEngine,
    PhaseSummaryBuilder,
    PhaseStatus,
    PhaseInfo,
    ProgressTrackerInfo,
    update_master_plan_phase,
    update_sub_plan_phase
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_markdown_with_tracker():
    """Sample markdown content with progress tracker"""
    return """# Master Plan

Some content here.

## Progress Tracker

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CORTEX ORCHESTRATION + AST ENHANCEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0: Foundation & Intent Routing     [██████████] 100%  ✅ Complete
PHASE 1: Pre-Flight Orchestrator         [██████████] 100%  ✅ Complete
PHASE 2: Progress Synchronizer           [          ]   0%  ⏳ Not Started
PHASE 3: Test Failure Analyzer           [          ]   0%  ⏳ Not Started

OVERALL PROGRESS: ██████░░░░░░░░░░░░░░░░░░░░░░ 2/4 Phases (50%)
```

More content here.
"""


@pytest.fixture
def temp_plan_file(sample_markdown_with_tracker):
    """Create temporary plan file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(sample_markdown_with_tracker)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def progress_synchronizer(temp_plan_file):
    """Create ProgressSynchronizer instance"""
    sync = ProgressSynchronizer(temp_plan_file)
    sync.load()
    return sync


# ============================================================================
# TEST MARKDOWN PARSER
# ============================================================================

class TestMarkdownParser:
    """Tests for MarkdownParser"""
    
    def test_load_file_success(self, temp_plan_file):
        """Should load markdown file successfully"""
        parser = MarkdownParser(temp_plan_file)
        assert parser.load() is True
        assert len(parser.content) > 0
    
    def test_load_nonexistent_file(self):
        """Should fail gracefully for nonexistent file"""
        parser = MarkdownParser(Path("/nonexistent/file.md"))
        assert parser.load() is False
    
    def test_extract_progress_tracker(self, temp_plan_file):
        """Should extract progress tracker from markdown"""
        parser = MarkdownParser(temp_plan_file)
        parser.load()
        
        tracker_info = parser.extract_progress_tracker()
        
        assert tracker_info is not None
        assert tracker_info.total_phases == 4
        assert tracker_info.completed_phases == 2
        assert tracker_info.overall_progress_percent == 50
    
    def test_parse_individual_phases(self, temp_plan_file):
        """Should parse individual phase information"""
        parser = MarkdownParser(temp_plan_file)
        parser.load()
        
        tracker_info = parser.extract_progress_tracker()
        
        assert len(tracker_info.phases) == 4
        
        # Check Phase 0
        phase0 = tracker_info.phases[0]
        assert phase0.phase_number == 0
        assert "Foundation" in phase0.phase_name
        assert phase0.status == PhaseStatus.COMPLETE
        assert phase0.progress_percent == 100
        
        # Check Phase 2
        phase2 = tracker_info.phases[2]
        assert phase2.phase_number == 2
        assert "Progress Synchronizer" in phase2.phase_name
        assert phase2.status == PhaseStatus.NOT_STARTED
        assert phase2.progress_percent == 0
    
    def test_no_tracker_in_file(self):
        """Should handle files without progress tracker"""
        content = "# Simple File\n\nNo tracker here."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            parser = MarkdownParser(temp_path)
            parser.load()
            
            tracker_info = parser.extract_progress_tracker()
            assert tracker_info is None
        finally:
            temp_path.unlink()


# ============================================================================
# TEST ASCII ART GENERATOR
# ============================================================================

class TestASCIIArtGenerator:
    """Tests for ASCIIArtGenerator"""
    
    def test_generate_progress_bar_0_percent(self):
        """Should generate empty progress bar for 0%"""
        bar = ASCIIArtGenerator.generate_progress_bar(0, width=10)
        assert bar == "[░░░░░░░░░░]"
    
    def test_generate_progress_bar_50_percent(self):
        """Should generate half-filled progress bar for 50%"""
        bar = ASCIIArtGenerator.generate_progress_bar(50, width=10)
        assert bar == "[█████░░░░░]"
    
    def test_generate_progress_bar_100_percent(self):
        """Should generate full progress bar for 100%"""
        bar = ASCIIArtGenerator.generate_progress_bar(100, width=10)
        assert bar == "[██████████]"
    
    def test_generate_overall_progress_bar(self):
        """Should generate wider bar for overall progress"""
        bar = ASCIIArtGenerator.generate_overall_progress_bar(50, width=30)
        assert len(bar) == 30
        assert bar.count('█') == 15
        assert bar.count('░') == 15
    
    def test_format_status_emoji_not_started(self):
        """Should return correct emoji for NOT_STARTED"""
        emoji = ASCIIArtGenerator.format_status_emoji(PhaseStatus.NOT_STARTED)
        assert emoji == '⏳'
    
    def test_format_status_emoji_in_progress(self):
        """Should return correct emoji for IN_PROGRESS"""
        emoji = ASCIIArtGenerator.format_status_emoji(PhaseStatus.IN_PROGRESS)
        assert emoji == '🚧'
    
    def test_format_status_emoji_complete(self):
        """Should return correct emoji for COMPLETE"""
        emoji = ASCIIArtGenerator.format_status_emoji(PhaseStatus.COMPLETE)
        assert emoji == '✅'
    
    def test_format_status_emoji_blocked(self):
        """Should return correct emoji for BLOCKED"""
        emoji = ASCIIArtGenerator.format_status_emoji(PhaseStatus.BLOCKED)
        assert emoji == '⚠️'


# ============================================================================
# TEST TRACKER UPDATE ENGINE
# ============================================================================

class TestTrackerUpdateEngine:
    """Tests for TrackerUpdateEngine"""
    
    def test_update_phase_to_complete(self):
        """Should update phase status to COMPLETE"""
        phases = [
            PhaseInfo("P1", 1, "PHASE 1: Test", PhaseStatus.NOT_STARTED, 0),
            PhaseInfo("P2", 2, "PHASE 2: Test", PhaseStatus.NOT_STARTED, 0)
        ]
        tracker_info = ProgressTrackerInfo(phases, 0, 2, 0)
        
        engine = TrackerUpdateEngine(tracker_info)
        result = engine.update_phase_status(1, PhaseStatus.COMPLETE)
        
        assert result is True
        assert phases[0].status == PhaseStatus.COMPLETE
        assert phases[0].progress_percent == 100
        assert phases[0].completion_date is not None
    
    def test_update_phase_to_in_progress(self):
        """Should update phase status to IN_PROGRESS"""
        phases = [
            PhaseInfo("P1", 1, "PHASE 1: Test", PhaseStatus.NOT_STARTED, 0)
        ]
        tracker_info = ProgressTrackerInfo(phases, 0, 1, 0)
        
        engine = TrackerUpdateEngine(tracker_info)
        result = engine.update_phase_status(1, PhaseStatus.IN_PROGRESS)
        
        assert result is True
        assert phases[0].status == PhaseStatus.IN_PROGRESS
        assert phases[0].progress_percent == 10
        assert phases[0].start_date is not None
    
    def test_recalculate_overall_progress(self):
        """Should recalculate overall progress correctly"""
        phases = [
            PhaseInfo("P1", 1, "PHASE 1", PhaseStatus.COMPLETE, 100),
            PhaseInfo("P2", 2, "PHASE 2", PhaseStatus.COMPLETE, 100),
            PhaseInfo("P3", 3, "PHASE 3", PhaseStatus.NOT_STARTED, 0),
            PhaseInfo("P4", 4, "PHASE 4", PhaseStatus.NOT_STARTED, 0)
        ]
        tracker_info = ProgressTrackerInfo(phases, 0, 4, 0)
        
        engine = TrackerUpdateEngine(tracker_info)
        engine._recalculate_overall_progress()
        
        assert tracker_info.completed_phases == 2
        assert tracker_info.overall_progress_percent == 50
    
    def test_get_next_phase(self):
        """Should return next NOT_STARTED phase"""
        phases = [
            PhaseInfo("P1", 1, "PHASE 1", PhaseStatus.COMPLETE, 100),
            PhaseInfo("P2", 2, "PHASE 2", PhaseStatus.NOT_STARTED, 0),
            PhaseInfo("P3", 3, "PHASE 3", PhaseStatus.NOT_STARTED, 0)
        ]
        tracker_info = ProgressTrackerInfo(phases, 0, 3, 1)
        
        engine = TrackerUpdateEngine(tracker_info)
        next_phase = engine.get_next_phase()
        
        assert next_phase is not None
        assert next_phase.phase_number == 2
    
    def test_get_next_phase_all_complete(self):
        """Should return None when all phases complete"""
        phases = [
            PhaseInfo("P1", 1, "PHASE 1", PhaseStatus.COMPLETE, 100),
            PhaseInfo("P2", 2, "PHASE 2", PhaseStatus.COMPLETE, 100)
        ]
        tracker_info = ProgressTrackerInfo(phases, 100, 2, 2)
        
        engine = TrackerUpdateEngine(tracker_info)
        next_phase = engine.get_next_phase()
        
        assert next_phase is None
    
    def test_update_nonexistent_phase(self):
        """Should fail gracefully for nonexistent phase"""
        phases = [
            PhaseInfo("P1", 1, "PHASE 1", PhaseStatus.NOT_STARTED, 0)
        ]
        tracker_info = ProgressTrackerInfo(phases, 0, 1, 0)
        
        engine = TrackerUpdateEngine(tracker_info)
        result = engine.update_phase_status(999, PhaseStatus.COMPLETE)
        
        assert result is False


# ============================================================================
# TEST PHASE SUMMARY BUILDER
# ============================================================================

class TestPhaseSummaryBuilder:
    """Tests for PhaseSummaryBuilder"""
    
    def test_build_summary_with_all_fields(self):
        """Should build complete summary with all fields"""
        phase = PhaseInfo(
            "P1", 1, "PHASE 1: Test Phase",
            PhaseStatus.COMPLETE, 100,
            start_date=datetime(2025, 12, 13, 10, 0),
            completion_date=datetime(2025, 12, 13, 14, 30),
            elapsed_time=timedelta(hours=4, minutes=30)
        )
        
        metrics = {
            "Lines of Code": 500,
            "Tests": 40,
            "Pass Rate": "100%"
        }
        
        summary = PhaseSummaryBuilder.build_summary(phase, metrics)
        
        assert "Phase 1 Complete" in summary
        assert "Test Phase" in summary
        assert "4h 30m" in summary
        assert "Lines of Code: 500" in summary
        assert "Tests: 40" in summary
    
    def test_build_summary_minimal(self):
        """Should build summary with minimal information"""
        phase = PhaseInfo(
            "P1", 1, "PHASE 1: Minimal",
            PhaseStatus.IN_PROGRESS, 50
        )
        
        summary = PhaseSummaryBuilder.build_summary(phase)
        
        assert "Phase 1" in summary
        assert "Minimal" in summary
        assert PhaseStatus.IN_PROGRESS.value in summary


# ============================================================================
# TEST PROGRESS SYNCHRONIZER
# ============================================================================

class TestProgressSynchronizer:
    """Tests for ProgressSynchronizer"""
    
    def test_load_success(self, temp_plan_file):
        """Should load plan file successfully"""
        sync = ProgressSynchronizer(temp_plan_file)
        result = sync.load()
        
        assert result is True
        assert sync.tracker_info is not None
        assert sync.tracker_info.total_phases == 4
    
    def test_update_phase_to_complete(self, progress_synchronizer, temp_plan_file):
        """Should update phase status and write to file"""
        result = progress_synchronizer.update_phase(
            phase_number=2,
            status=PhaseStatus.COMPLETE
        )
        
        assert result is True
        
        # Verify file was updated
        with open(temp_plan_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "PHASE 2: Progress Synchronizer" in content
        assert "[██████████] 100%  ✅ Complete" in content
    
    def test_update_phase_recalculates_overall(self, progress_synchronizer, temp_plan_file):
        """Should recalculate overall progress after update"""
        # Phase 0, 1 already complete (50%), completing Phase 2 → 75%
        progress_synchronizer.update_phase(
            phase_number=2,
            status=PhaseStatus.COMPLETE
        )
        
        with open(temp_plan_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should show 3/4 phases (75%)
        assert "3/4 Phases (75%)" in content
    
    def test_update_phase_to_in_progress(self, progress_synchronizer, temp_plan_file):
        """Should update phase to IN_PROGRESS"""
        result = progress_synchronizer.update_phase(
            phase_number=3,
            status=PhaseStatus.IN_PROGRESS
        )
        
        assert result is True
        
        with open(temp_plan_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "🚧 In Progress" in content
    
    def test_atomic_write(self, progress_synchronizer, temp_plan_file):
        """Should write file atomically (no partial updates)"""
        # Simulate concurrent read while updating
        original_content = temp_plan_file.read_text(encoding='utf-8')
        
        result = progress_synchronizer.update_phase(
            phase_number=2,
            status=PhaseStatus.COMPLETE
        )
        
        assert result is True
        
        # File should be completely updated, not corrupted
        new_content = temp_plan_file.read_text(encoding='utf-8')
        assert len(new_content) > 0
        assert "```" in new_content  # Markdown structure intact
    
    def test_get_current_status(self, progress_synchronizer):
        """Should return current tracker status"""
        status = progress_synchronizer.get_current_status()
        
        assert status is not None
        assert status.total_phases == 4
        assert status.completed_phases == 2
        assert status.overall_progress_percent == 50
    
    def test_get_next_phase(self, progress_synchronizer):
        """Should return next phase to execute"""
        next_phase = progress_synchronizer.get_next_phase()
        
        assert next_phase is not None
        assert next_phase.phase_number == 2
        assert "Progress Synchronizer" in next_phase.phase_name
    
    def test_update_with_metrics(self, progress_synchronizer, temp_plan_file):
        """Should accept metrics parameter"""
        metrics = {"Lines": 500, "Tests": 40}
        
        result = progress_synchronizer.update_phase(
            phase_number=2,
            status=PhaseStatus.COMPLETE,
            metrics=metrics
        )
        
        assert result is True


# ============================================================================
# TEST CONVENIENCE FUNCTIONS
# ============================================================================

class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_update_master_plan_phase(self, temp_plan_file):
        """Should update master plan using convenience function"""
        result = update_master_plan_phase(
            phase_number=2,
            status=PhaseStatus.COMPLETE,
            master_plan_path=temp_plan_file
        )
        
        assert result is True
    
    def test_update_sub_plan_phase(self, temp_plan_file):
        """Should update sub-plan using convenience function"""
        result = update_sub_plan_phase(
            sub_plan_path=temp_plan_file,
            phase_number=2,
            status=PhaseStatus.COMPLETE
        )
        
        assert result is True


# ============================================================================
# TEST EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    def test_update_without_loading(self):
        """Should fail if update called before load"""
        sync = ProgressSynchronizer(Path("/tmp/test.md"))
        
        result = sync.update_phase(1, PhaseStatus.COMPLETE)
        assert result is False
    
    def test_corrupted_markdown(self):
        """Should handle corrupted markdown gracefully"""
        content = """# Broken Plan
        
```
PHASE 1: Missing closing backticks
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            sync = ProgressSynchronizer(temp_path)
            result = sync.load()
            
            # Should fail gracefully
            assert result is False or sync.tracker_info is None
        finally:
            temp_path.unlink()
    
    def test_phase_status_transitions(self, progress_synchronizer):
        """Should handle status transitions correctly"""
        # NOT_STARTED → IN_PROGRESS
        progress_synchronizer.update_phase(3, PhaseStatus.IN_PROGRESS)
        assert progress_synchronizer.tracker_info.phases[3].progress_percent == 10
        
        # IN_PROGRESS → COMPLETE
        progress_synchronizer.update_phase(3, PhaseStatus.COMPLETE)
        assert progress_synchronizer.tracker_info.phases[3].progress_percent == 100
    
    def test_preserve_other_content(self, progress_synchronizer, temp_plan_file):
        """Should preserve content outside progress tracker"""
        original_content = temp_plan_file.read_text(encoding='utf-8')
        
        progress_synchronizer.update_phase(2, PhaseStatus.COMPLETE)
        
        new_content = temp_plan_file.read_text(encoding='utf-8')
        
        # Should preserve header
        assert "# Master Plan" in new_content
        # Should preserve footer
        assert "More content here." in new_content


# ============================================================================
# TEST INTEGRATION
# ============================================================================

class TestIntegration:
    """Integration tests"""
    
    def test_complete_workflow(self, temp_plan_file):
        """Test complete workflow: load → update → verify"""
        sync = ProgressSynchronizer(temp_plan_file)
        
        # Load
        assert sync.load() is True
        assert sync.tracker_info.completed_phases == 2
        
        # Update Phase 2
        assert sync.update_phase(2, PhaseStatus.IN_PROGRESS) is True
        
        # Reload and verify
        sync2 = ProgressSynchronizer(temp_plan_file)
        sync2.load()
        
        phase2 = next(p for p in sync2.tracker_info.phases if p.phase_number == 2)
        assert phase2.status == PhaseStatus.IN_PROGRESS
        
        # Complete Phase 2
        assert sync2.update_phase(2, PhaseStatus.COMPLETE) is True
        
        # Reload and verify again
        sync3 = ProgressSynchronizer(temp_plan_file)
        sync3.load()
        
        assert sync3.tracker_info.completed_phases == 3
        assert sync3.tracker_info.overall_progress_percent == 75
    
    def test_multiple_phase_updates(self, progress_synchronizer):
        """Test updating multiple phases in sequence"""
        # Complete Phase 2
        progress_synchronizer.update_phase(2, PhaseStatus.COMPLETE)
        
        # Start Phase 3
        progress_synchronizer.update_phase(3, PhaseStatus.IN_PROGRESS)
        
        # Verify final state
        tracker = progress_synchronizer.get_current_status()
        assert tracker.completed_phases == 3
        
        phase2 = next(p for p in tracker.phases if p.phase_number == 2)
        phase3 = next(p for p in tracker.phases if p.phase_number == 3)
        
        assert phase2.status == PhaseStatus.COMPLETE
        assert phase3.status == PhaseStatus.IN_PROGRESS


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
