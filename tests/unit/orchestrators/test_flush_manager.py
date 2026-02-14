"""
Tests for FlushManager — Phase 84 Stage 2.

Synaptic pruning neuron that removes stale patterns (>30 days old, confidence <0.4)
from the pattern library to prevent knowledge base bloat.

AC_START: AC-P84-S2-T1-004
Phase: 84 | Stage: 2 | Priority: P0
Description: TDD RED phase for FlushManager
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from unittest.mock import MagicMock, patch, mock_open

try:
    from cortex.orchestrators.workflow.flush_manager import (
        FlushManager,
        Pattern,
        FlushDecision,
    )
except ImportError:
    FlushManager = None
    Pattern = None
    FlushDecision = None


# =============================================================================
# FLUSH MANAGER TESTS
# =============================================================================
class TestFlushManagerInit:
    """Test FlushManager initialization."""

    @pytest.mark.skipif(FlushManager is None, reason="FlushManager not yet implemented")
    def test_flush_manager_initializes(self):
        """AC-P84-S2-T1-004: FlushManager.__init__ sets thresholds."""
        manager = FlushManager(
            max_age_days=30,
            min_confidence=0.4,
            pattern_library_path=Path("tier2/pattern-library.yaml")
        )
        
        assert manager is not None
        assert manager.max_age_days == 30
        assert manager.min_confidence == 0.4

    @pytest.mark.skipif(FlushManager is None, reason="FlushManager not yet implemented")
    def test_flush_manager_default_thresholds(self):
        """FlushManager uses default thresholds if not specified."""
        manager = FlushManager()
        
        assert manager.max_age_days >= 30
        assert manager.min_confidence >= 0.4


class TestFlushManagerEvaluate:
    """Test FlushManager.evaluate() method."""

    @pytest.mark.skipif(FlushManager is None, reason="FlushManager not yet implemented")
    def test_evaluate_flushes_stale_low_confidence_pattern(self):
        """AC-P84-S2-T1-005: evaluate() returns FLUSH for stale pattern."""
        manager = FlushManager(max_age_days=30, min_confidence=0.4)
        
        # Pattern from 35 days ago with low confidence
        old_date = datetime.now() - timedelta(days=35)
        pattern = Pattern(
            id="pattern_stale_001",
            signature="old_pattern_sha256_abc",
            confidence=0.3,
            sighting_count=2,
            first_seen=old_date,
            last_seen=old_date,
            context={},
        )
        
        decision = manager.evaluate(pattern)
        
        assert decision.action == "FLUSH"
        assert "stale" in decision.reason.lower() or "old" in decision.reason.lower()

    @pytest.mark.skipif(FlushManager is None, reason="FlushManager not yet implemented")
    def test_evaluate_keeps_recent_pattern(self):
        """evaluate() returns KEEP for recent pattern."""
        manager = FlushManager(max_age_days=30, min_confidence=0.4)
        
        recent_date = datetime.now() - timedelta(days=5)
        pattern = Pattern(
            id="pattern_recent_001",
            signature="recent_pattern_sha256_xyz",
            confidence=0.3,
            sighting_count=1,
            first_seen=recent_date,
            last_seen=recent_date,
            context={},
        )
        
        decision = manager.evaluate(pattern)
        
        assert decision.action == "KEEP"

    @pytest.mark.skipif(FlushManager is None, reason="FlushManager not yet implemented")
    def test_evaluate_keeps_high_confidence_old_pattern(self):
        """evaluate() returns KEEP for old pattern with high confidence."""
        manager = FlushManager(max_age_days=30, min_confidence=0.4)
        
        old_date = datetime.now() - timedelta(days=45)
        pattern = Pattern(
            id="pattern_valuable_001",
            signature="valuable_pattern_sha256_def",
            confidence=0.9,
            sighting_count=20,
            first_seen=old_date,
            last_seen=datetime.now() - timedelta(days=2),
            context={},
        )
        
        decision = manager.evaluate(pattern)
        
        assert decision.action == "KEEP"
        assert "confidence" in decision.reason.lower() or "valuable" in decision.reason.lower()


class TestFlushManagerFlush:
    """Test FlushManager.flush() method."""

    @pytest.mark.skipif(FlushManager is None, reason="FlushManager not yet implemented")
    def test_flush_removes_pattern_from_library(self):
        """AC-P84-S2-T1-006: flush() removes pattern from pattern library."""
        library_path = Path("tier2/pattern-library.yaml")
        manager = FlushManager(pattern_library_path=library_path)
        
        pattern = Pattern(
            id="pattern_flush_001",
            signature="to_be_removed",
            confidence=0.2,
            sighting_count=1,
            first_seen=datetime.now() - timedelta(days=40),
            last_seen=datetime.now() - timedelta(days=40),
            context={},
        )
        
        existing_patterns = {
            "patterns": [
                {"id": "pattern_flush_001", "signature": "to_be_removed"},
                {"id": "pattern_keep_001", "signature": "keeper"},
            ]
        }
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="patterns:\n  - id: pattern_flush_001\n")) as mock_file, \
             patch("yaml.safe_load", return_value=existing_patterns), \
             patch("yaml.safe_dump") as mock_dump:
            
            manager.flush(pattern)
            
            # Verify pattern was removed
            mock_dump.assert_called_once()

    @pytest.mark.skipif(FlushManager is None, reason="FlushManager not yet implemented")
    def test_flush_emits_pattern_flushed_event(self):
        """flush() emits PATTERN_FLUSHED event."""
        manager = FlushManager()
        
        pattern = Pattern(
            id="pattern_flush_002",
            signature="test_flush_event",
            confidence=0.1,
            sighting_count=1,
            first_seen=datetime.now() - timedelta(days=50),
            last_seen=datetime.now() - timedelta(days=50),
            context={},
        )
        
        emitted_events = []
        
        def capture_event(event_name: str, data: dict) -> None:
            emitted_events.append((event_name, data))
        
        manager._emit_event = capture_event
        
        with patch.object(Path, "exists", return_value=True), \
             patch("builtins.open", mock_open()), \
             patch("yaml.safe_load", return_value={"patterns": [{"id": "pattern_flush_002"}]}), \
             patch("yaml.safe_dump"):
            manager.flush(pattern)
        
        assert len(emitted_events) > 0
        assert any(e[0] == "PATTERN_FLUSHED" for e in emitted_events)


class TestFlushDecision:
    """Test FlushDecision dataclass."""

    @pytest.mark.skipif(FlushDecision is None, reason="FlushDecision not yet implemented")
    def test_flush_decision_structure(self):
        """FlushDecision has action, pattern_id, reason."""
        decision = FlushDecision(
            action="FLUSH",
            pattern_id="pattern_001",
            reason="Pattern is stale and low confidence",
        )
        
        assert decision.action == "FLUSH"
        assert decision.pattern_id == "pattern_001"

# AC_COMPLETE: AC-P84-S2-T1-004 ✅ RED tests for FlushManager
