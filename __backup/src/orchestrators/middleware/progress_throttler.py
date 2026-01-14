"""
Progress Throttler
==================
Throttles progress updates to prevent overwhelming output.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 3 Task: 3.2
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


@dataclass
class ProgressUpdate:
    """Represents a progress update"""
    task_id: str
    progress: float
    message: str
    timestamp: datetime


class ProgressThrottler:
    """Throttles progress updates based on time intervals"""
    
    def __init__(self, min_interval_seconds: float = 5.0):
        """
        Initialize progress throttler
        
        Args:
            min_interval_seconds: Minimum seconds between updates for same task
        """
        self.min_interval = timedelta(seconds=min_interval_seconds)
        self.last_updates: Dict[str, datetime] = {}
        self.suppressed_count: Dict[str, int] = {}
    
    def should_update(self, task_id: str) -> bool:
        """
        Check if progress update should be allowed
        
        Args:
            task_id: Identifier for the task
            
        Returns:
            True if update should be allowed
        """
        now = datetime.now()
        
        if task_id not in self.last_updates:
            self.last_updates[task_id] = now
            return True
        
        last_update = self.last_updates[task_id]
        time_since_last = now - last_update
        
        if time_since_last >= self.min_interval:
            self.last_updates[task_id] = now
            return True
        
        # Track suppressed updates
        self.suppressed_count[task_id] = self.suppressed_count.get(task_id, 0) + 1
        return False
    
    def record_update(self, task_id: str) -> None:
        """
        Record that an update was made
        
        Args:
            task_id: Identifier for the task
        """
        self.last_updates[task_id] = datetime.now()
    
    def get_suppressed_count(self, task_id: str) -> int:
        """
        Get count of suppressed updates for a task
        
        Args:
            task_id: Identifier for the task
            
        Returns:
            Number of suppressed updates
        """
        return self.suppressed_count.get(task_id, 0)
    
    def reset(self, task_id: Optional[str] = None) -> None:
        """
        Reset throttler state
        
        Args:
            task_id: Optional specific task to reset, or None for all
        """
        if task_id:
            self.last_updates.pop(task_id, None)
            self.suppressed_count.pop(task_id, None)
        else:
            self.last_updates.clear()
            self.suppressed_count.clear()
    
    def get_time_until_next_update(self, task_id: str) -> Optional[float]:
        """
        Get seconds until next update is allowed
        
        Args:
            task_id: Identifier for the task
            
        Returns:
            Seconds until next update, or None if update allowed now
        """
        if task_id not in self.last_updates:
            return None
        
        last_update = self.last_updates[task_id]
        elapsed = datetime.now() - last_update
        remaining = self.min_interval - elapsed
        
        if remaining.total_seconds() <= 0:
            return None
        
        return remaining.total_seconds()
