"""
CORTEX 2.0 - Debouncer Tests

Tests for event debouncing and batching.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "cortex"))

from auto_capture_daemon import Debouncer


class TestDebouncer:
    """Test Debouncer component."""
    
    def test_debouncer_initialization(self):
        """Should initialize with default delay."""
        debouncer = Debouncer()
        
        assert debouncer.delay == 5
        assert debouncer.buffer == []
        assert debouncer.lock is not None
        assert debouncer.timer is None
    
    def test_custom_delay_initialization(self):
        """Should initialize with custom delay."""
        debouncer = Debouncer(delay_seconds=10)
        
        assert debouncer.delay == 10
    
    def test_buffers_single_event(self):
        """Should buffer events without immediate flush."""
        debouncer = Debouncer(delay_seconds=60)  # Long delay
        
        context = {
            "type": "file_change",
            "file": "test.py",
            "timestamp": "2025-11-08T10:00:00"
        }
        
        debouncer.add_event(context)
        
        # Event should be in buffer
        assert len(debouncer.buffer) == 1
        assert debouncer.buffer[0] == context
        
        # Cancel timer to prevent flush
        if debouncer.timer:
            debouncer.timer.cancel()
    
    def test_buffers_multiple_events(self):
        """Should buffer multiple events."""
        debouncer = Debouncer(delay_seconds=60)
        
        events = [
            {"type": "file_change", "file": "file1.py", "timestamp": "2025-11-08T10:00:00"},
            {"type": "file_change", "file": "file2.py", "timestamp": "2025-11-08T10:00:01"},
            {"type": "terminal_command", "command": "pytest", "timestamp": "2025-11-08T10:00:02"}
        ]
        
        for event in events:
            debouncer.add_event(event)
        
        assert len(debouncer.buffer) == 3
        
        # Cancel timer
        if debouncer.timer:
            debouncer.timer.cancel()
    
    def test_resets_timer_on_new_event(self):
        """Should reset timer when new event arrives."""
        debouncer = Debouncer(delay_seconds=1)
        
        debouncer.add_event({"type": "test1", "timestamp": "2025-11-08T10:00:00"})
        first_timer = debouncer.timer
        
        time.sleep(0.5)
        
        debouncer.add_event({"type": "test2", "timestamp": "2025-11-08T10:00:01"})
        second_timer = debouncer.timer
        
        # Timer should be different (reset)
        assert first_timer is not second_timer
        
        # Cancel timer
        if debouncer.timer:
            debouncer.timer.cancel()
    
    def test_merges_duplicate_events(self):
        """Should merge events for same file."""
        debouncer = Debouncer(delay_seconds=60)
        
        # Add duplicate events for same file
        events = [
            {"type": "file_change", "file": "test.py", "event": "modified", "timestamp": "2025-11-08T10:00:00"},
            {"type": "file_change", "file": "test.py", "event": "modified", "timestamp": "2025-11-08T10:00:01"},
            {"type": "file_change", "file": "test.py", "event": "modified", "timestamp": "2025-11-08T10:00:02"}
        ]
        
        for event in events:
            debouncer.add_event(event)
        
        # Merge events
        merged = debouncer._merge_events(debouncer.buffer)
        
        # Should merge to single event with latest timestamp
        assert len(merged) == 1
        assert merged[0]["timestamp"] == "2025-11-08T10:00:02"
        
        # Cancel timer
        if debouncer.timer:
            debouncer.timer.cancel()
    
    def test_does_not_merge_different_files(self):
        """Should not merge events for different files."""
        debouncer = Debouncer(delay_seconds=60)
        
        events = [
            {"type": "file_change", "file": "file1.py", "timestamp": "2025-11-08T10:00:00"},
            {"type": "file_change", "file": "file2.py", "timestamp": "2025-11-08T10:00:01"}
        ]
        
        for event in events:
            debouncer.add_event(event)
        
        merged = debouncer._merge_events(debouncer.buffer)
        
        # Should keep both events
        assert len(merged) == 2
        
        # Cancel timer
        if debouncer.timer:
            debouncer.timer.cancel()
    
    @patch('src.tier1.working_memory.WorkingMemory')
    def test_writes_to_tier1_on_flush(self, mock_wm_class):
        """Should write events to Tier 1 on flush."""
        # Create mock working memory instance
        mock_wm = MagicMock()
        mock_wm_class.return_value = mock_wm
        
        # Mock session creation
        mock_wm.start_conversation.return_value = "test-session-id"
        
        debouncer = Debouncer(delay_seconds=0.5)
        
        # Add event
        debouncer.add_event({
            "type": "file_change",
            "file": "test.py",
            "timestamp": "2025-11-08T10:00:00"
        })
        
        # Wait for flush
        time.sleep(1)
        
        # WorkingMemory should have been called
        assert mock_wm.store_message.called
    
    def test_concurrent_event_handling(self):
        """Should handle concurrent events safely."""
        debouncer = Debouncer(delay_seconds=60)
        
        def add_events(prefix):
            for i in range(10):
                debouncer.add_event({
                    "type": "test",
                    "id": f"{prefix}-{i}",
                    "timestamp": f"2025-11-08T10:00:{i:02d}"
                })
        
        # Add events from multiple threads
        threads = [
            threading.Thread(target=add_events, args=("thread1",)),
            threading.Thread(target=add_events, args=("thread2",)),
            threading.Thread(target=add_events, args=("thread3",))
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # All events should be buffered
        assert len(debouncer.buffer) == 30
        
        # Cancel timer
        if debouncer.timer:
            debouncer.timer.cancel()
    
    def test_clears_buffer_after_flush(self):
        """Should clear buffer after successful flush."""
        debouncer = Debouncer(delay_seconds=60)
        
        # Add events
        debouncer.add_event({"type": "test1", "timestamp": "2025-11-08T10:00:00"})
        debouncer.add_event({"type": "test2", "timestamp": "2025-11-08T10:00:01"})
        
        assert len(debouncer.buffer) > 0
        
        # Mock flush
        with patch.object(debouncer, '_write_to_tier1'):
            debouncer._flush()
        
        # Buffer should be cleared
        assert len(debouncer.buffer) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
