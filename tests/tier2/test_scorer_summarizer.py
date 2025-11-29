"""
Tests for Activity Scorer and Auto-Summarizer (Phase 4.4)

Tests activity scoring and summarization components.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms

NOTE: These tests are skipped - ambient daemon removed from CORTEX 3.0
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
import sys
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))


@pytest.mark.skip(reason="Ambient daemon removed from CORTEX 3.0 - manual capture hints used instead")
class TestActivityScorer:
    """Test suite for ActivityScorer (DEPRECATED)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scorer = ActivityScorer()
    
    # ========================================================================
    # File Type Scoring
    # ========================================================================
    
    def test_score_python_file(self):
        """Should give high score to Python source files."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert score >= 70  # High priority
    
    def test_score_typescript_file(self):
        """Should give high score to TypeScript files."""
        event = {
            "file": "src/component.tsx",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert score >= 70
    
    def test_score_config_file(self):
        """Should give medium score to config files."""
        event = {
            "file": "config.json",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "CONFIG")
        assert 40 <= score <= 70
    
    def test_score_documentation(self):
        """Should give lower score to documentation."""
        event = {
            "file": "README.md",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "DOCS")
        assert 30 <= score <= 60  # Adjusted range
    
    # ========================================================================
    # Event Type Scoring
    # ========================================================================
    
    def test_score_created_file(self):
        """Should give high magnitude score to created files."""
        event = {
            "file": "src/new.py",
            "event": "created"
        }
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert score >= 70  # New file = high impact
    
    def test_score_deleted_file(self):
        """Should give significant score to deleted files."""
        event = {
            "file": "src/old.py",
            "event": "deleted"
        }
        
        score = self.scorer.score_activity(event, "REFACTOR")
        assert score >= 60
    
    def test_score_modified_file(self):
        """Should give moderate score to modified files."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "BUGFIX")
        assert 40 <= score <= 90
    
    # ========================================================================
    # Pattern Scoring
    # ========================================================================
    
    def test_score_feature_pattern(self):
        """Should give highest pattern score to features."""
        event = {
            "file": "src/module.py",
            "event": "created"
        }
        
        feature_score = self.scorer.score_activity(event, "FEATURE")
        bugfix_score = self.scorer.score_activity(event, "BUGFIX")
        
        assert feature_score > bugfix_score
    
    def test_score_bugfix_pattern(self):
        """Should give medium-high pattern score to bug fixes."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        bugfix_score = self.scorer.score_activity(event, "BUGFIX")
        docs_score = self.scorer.score_activity(event, "DOCS")
        
        assert bugfix_score > docs_score
    
    # ========================================================================
    # Path Importance Scoring
    # ========================================================================
    
    def test_score_core_source(self):
        """Should give highest importance to core source."""
        event = {
            "file": "src/core/engine.py",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert score >= 75
    
    def test_score_test_files(self):
        """Should give high importance to test files."""
        event = {
            "file": "tests/test_module.py",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "BUGFIX")
        assert score >= 60
    
    def test_score_scripts(self):
        """Should give moderate importance to scripts."""
        event = {
            "file": "scripts/deploy.sh",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert 50 <= score <= 80
    
    def test_score_docs_path(self):
        """Should give lower importance to docs directory."""
        event = {
            "file": "docs/guide.md",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "DOCS")
        assert 20 <= score <= 60  # Adjusted range
    
    # ========================================================================
    # Composite Scoring
    # ========================================================================
    
    def test_score_high_priority_change(self):
        """Should give 80+ score to high-priority changes."""
        event = {
            "file": "src/core.py",  # Core source
            "event": "created"  # New file
        }
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert score >= 80
    
    def test_score_low_priority_change(self):
        """Should give <50 score to low-priority changes."""
        event = {
            "file": "docs/notes.txt",  # Documentation
            "event": "modified"  # Modification
        }
        
        score = self.scorer.score_activity(event, "DOCS")
        assert score < 50  # Adjusted threshold
    
    def test_score_capped_at_100(self):
        """Should cap scores at 100."""
        event = {
            "file": "src/core.py",
            "event": "created"
        }
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert score <= 100
    
    # ========================================================================
    # Edge Cases
    # ========================================================================
    
    def test_score_unknown_pattern(self):
        """Should handle unknown patterns."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "UNKNOWN")
        assert 0 <= score <= 100
    
    def test_score_unknown_file_type(self):
        """Should handle unknown file types."""
        event = {
            "file": "data.dat",
            "event": "modified"
        }
        
        score = self.scorer.score_activity(event, "UNKNOWN")
        assert 0 <= score <= 100
    
    def test_score_malformed_event(self):
        """Should handle malformed events gracefully."""
        event = {}  # Missing fields
        
        score = self.scorer.score_activity(event, "FEATURE")
        assert score == 50  # Default middle score


class TestAutoSummarizer:
    """Test suite for AutoSummarizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.summarizer = AutoSummarizer()
    
    # ========================================================================
    # Event Summarization
    # ========================================================================
    
    def test_summarize_created_event(self):
        """Should summarize file creation."""
        event = {
            "file": "src/module.py",
            "event": "created"
        }
        
        summary = self.summarizer.summarize_event(event, "FEATURE", 85)
        
        assert "created" in summary.lower()
        assert "src/module.py" in summary.lower()
        assert "feature" in summary.lower()
    
    def test_summarize_modified_event(self):
        """Should summarize file modification."""
        event = {
            "file": "src/module.py",
            "event": "modified"
        }
        
        summary = self.summarizer.summarize_event(event, "BUGFIX", 60)
        
        assert "modified" in summary.lower()
        assert "src/module.py" in summary.lower()
        assert "bug fix" in summary.lower()
    
    def test_summarize_deleted_event(self):
        """Should summarize file deletion."""
        event = {
            "file": "src/old.py",
            "event": "deleted"
        }
        
        summary = self.summarizer.summarize_event(event, "REFACTOR", 70)
        
        assert "deleted" in summary.lower()
        assert "src/old.py" in summary.lower()
    
    def test_summarize_high_priority_event(self):
        """Should mark high-priority events."""
        event = {
            "file": "src/core.py",
            "event": "created"
        }
        
        summary = self.summarizer.summarize_event(event, "FEATURE", 90)
        
        assert "HIGH PRIORITY" in summary or "high priority" in summary.lower()
    
    def test_summarize_normal_priority_event(self):
        """Should not mark normal-priority events."""
        event = {
            "file": "docs/readme.md",
            "event": "modified"
        }
        
        summary = self.summarizer.summarize_event(event, "DOCS", 30)
        
        assert "high priority" not in summary.lower()
    
    # ========================================================================
    # Batch Summarization
    # ========================================================================
    
    def test_summarize_empty_batch(self):
        """Should handle empty batch."""
        summary = self.summarizer.summarize_batch([])
        assert "no changes" in summary.lower()
    
    def test_summarize_single_event_batch(self):
        """Should summarize single-event batch."""
        events = [
            {
                "file": "src/module.py",
                "event": "modified",
                "pattern": "BUGFIX",
                "score": 70
            }
        ]
        
        summary = self.summarizer.summarize_batch(events)
        
        assert "1" in summary
        assert "bugfix" in summary.lower()
    
    def test_summarize_multi_event_batch(self):
        """Should summarize multiple events."""
        events = [
            {"file": "src/a.py", "pattern": "FEATURE", "score": 80},
            {"file": "src/b.py", "pattern": "FEATURE", "score": 75},
            {"file": "src/c.py", "pattern": "BUGFIX", "score": 60}
        ]
        
        summary = self.summarizer.summarize_batch(events)
        
        assert "2 feature" in summary.lower()
        assert "1 bugfix" in summary.lower()
        assert "files: 3" in summary.lower()
    
    def test_batch_summary_includes_avg_score(self):
        """Should include average score in batch summary."""
        events = [
            {"file": "a.py", "pattern": "FEATURE", "score": 80},
            {"file": "b.py", "pattern": "BUGFIX", "score": 60}
        ]
        
        summary = self.summarizer.summarize_batch(events)
        
        assert "avg score: 70/100" in summary.lower()
    
    # ========================================================================
    # Session Summarization
    # ========================================================================
    
    def test_summarize_session(self):
        """Should summarize work session."""
        start = datetime(2025, 11, 9, 14, 0, 0)
        end = datetime(2025, 11, 9, 16, 30, 0)
        
        events = [
            {"file": "src/a.py", "pattern": "FEATURE", "score": 85},
            {"file": "src/b.py", "pattern": "BUGFIX", "score": 60},
            {"file": "src/a.py", "pattern": "REFACTOR", "score": 70}
        ]
        
        summary = self.summarizer.summarize_session(start, end, events)
        
        assert "2025-11-09" in summary
        assert "14:00" in summary
        assert "16:30" in summary
        assert "2.5h" in summary or "2.5 h" in summary.lower()
    
    def test_session_summary_includes_high_priority(self):
        """Should mention high-priority changes in session."""
        start = datetime(2025, 11, 9, 14, 0, 0)
        end = datetime(2025, 11, 9, 15, 0, 0)
        
        events = [
            {"file": "src/core.py", "pattern": "FEATURE", "score": 90},
            {"file": "docs/readme.md", "pattern": "DOCS", "score": 30}
        ]
        
        summary = self.summarizer.summarize_session(start, end, events)
        
        assert "1 high-priority" in summary.lower()
    
    def test_session_summary_includes_top_files(self):
        """Should list most active files."""
        start = datetime(2025, 11, 9, 14, 0, 0)
        end = datetime(2025, 11, 9, 15, 0, 0)
        
        events = [
            {"file": "src/a.py", "score": 80},
            {"file": "src/a.py", "score": 75},
            {"file": "src/a.py", "score": 70},
            {"file": "src/b.py", "score": 65}
        ]
        
        summary = self.summarizer.summarize_session(start, end, events)
        
        assert "a.py" in summary.lower()
    
    # ========================================================================
    # Edge Cases
    # ========================================================================
    
    def test_summarize_malformed_event(self):
        """Should handle malformed events gracefully."""
        event = {}  # Missing fields
        
        summary = self.summarizer.summarize_event(event, "UNKNOWN", 50)
        assert "unknown" in summary.lower()
    
    def test_summarize_long_filenames(self):
        """Should handle long filenames."""
        event = {
            "file": "src/very/deep/directory/structure/with/long/filename.py",
            "event": "modified"
        }
        
        summary = self.summarizer.summarize_event(event, "FEATURE", 70)
        
        # Should still include the filename
        assert len(summary) < 250  # Reasonable length
        assert "filename.py" in summary.lower()


class TestScorerSummarizerIntegration:
    """Integration tests for scorer and summarizer."""
    
    def test_score_and_summarize_flow(self):
        """Should score and summarize events in sequence."""
        scorer = ActivityScorer()
        summarizer = AutoSummarizer()
        
        event = {
            "file": "src/core.py",
            "event": "created"
        }
        
        # Score
        pattern = "FEATURE"
        score = scorer.score_activity(event, pattern)
        
        # Summarize
        summary = summarizer.summarize_event(event, pattern, score)
        
        assert score >= 80
        assert "created" in summary.lower()
        assert "feature" in summary.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
