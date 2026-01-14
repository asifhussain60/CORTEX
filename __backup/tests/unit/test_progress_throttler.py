"""
Tests for Progress Throttler
============================
Tests progress update throttling logic.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 3 Task: 3.2
TDD Phase: RED → GREEN → REFACTOR
"""

import pytest
import time
from datetime import datetime, timedelta

from src.orchestrators.middleware.progress_throttler import (
    ProgressThrottler,
    ProgressUpdate
)


class TestProgressThrottler:
    """Test progress throttler"""
    
    def test_initializes_with_default_interval(self):
        """Should initialize with 5 second default interval"""
        throttler = ProgressThrottler()
        assert throttler.min_interval == timedelta(seconds=5.0)
    
    def test_can_set_custom_interval(self):
        """Should allow setting custom interval"""
        throttler = ProgressThrottler(min_interval_seconds=10.0)
        assert throttler.min_interval == timedelta(seconds=10.0)
    
    def test_first_update_always_allowed(self):
        """Should always allow first update for a task"""
        throttler = ProgressThrottler()
        assert throttler.should_update("task1") is True
    
    def test_immediate_second_update_suppressed(self):
        """Should suppress immediate second update"""
        throttler = ProgressThrottler(min_interval_seconds=1.0)
        
        throttler.should_update("task1")  # First update
        assert throttler.should_update("task1") is False  # Immediate second
    
    def test_update_allowed_after_interval(self):
        """Should allow update after minimum interval"""
        throttler = ProgressThrottler(min_interval_seconds=0.1)  # 100ms
        
        throttler.should_update("task1")  # First update
        time.sleep(0.15)  # Wait longer than interval
        assert throttler.should_update("task1") is True
    
    def test_tracks_suppressed_count(self):
        """Should track suppressed update count"""
        throttler = ProgressThrottler()
        
        throttler.should_update("task1")  # Allowed
        throttler.should_update("task1")  # Suppressed
        throttler.should_update("task1")  # Suppressed
        
        assert throttler.get_suppressed_count("task1") == 2
    
    def test_different_tasks_tracked_separately(self):
        """Should track different tasks separately"""
        throttler = ProgressThrottler()
        
        assert throttler.should_update("task1") is True
        assert throttler.should_update("task2") is True  # Different task, allowed
    
    def test_reset_clears_task_state(self):
        """Should clear state for specific task"""
        throttler = ProgressThrottler()
        
        throttler.should_update("task1")
        throttler.reset("task1")
        
        assert "task1" not in throttler.last_updates
    
    def test_reset_all_clears_everything(self):
        """Should clear all state when no task specified"""
        throttler = ProgressThrottler()
        
        throttler.should_update("task1")
        throttler.should_update("task2")
        throttler.reset()
        
        assert len(throttler.last_updates) == 0
    
    def test_get_time_until_next_update(self):
        """Should calculate time until next update"""
        throttler = ProgressThrottler(min_interval_seconds=1.0)
        
        throttler.should_update("task1")
        time_remaining = throttler.get_time_until_next_update("task1")
        
        assert time_remaining is not None
        assert 0 < time_remaining <= 1.0
    
    def test_time_until_next_update_none_when_allowed(self):
        """Should return None when update is allowed"""
        throttler = ProgressThrottler()
        
        assert throttler.get_time_until_next_update("task1") is None
