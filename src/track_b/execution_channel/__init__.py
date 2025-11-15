"""
CORTEX 3.0 Track B: Execution Channel
=====================================

The Execution Channel captures real-time development activity through:
- Ambient Daemon: Central coordination and orchestration
- File Monitor: Filesystem change detection and analysis  
- Git Monitor: Repository operation tracking
- Terminal Tracker: Command execution monitoring

This module provides automatic context capture without user intervention,
feeding development intelligence to the CORTEX brain system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from .ambient_daemon import AmbientDaemon, DaemonConfig, ExecutionEvent
from .file_monitor import FileMonitor, FileChangeEvent
from .git_monitor import GitMonitor, GitEvent  
from .terminal_tracker import TerminalTracker, TerminalEvent

__all__ = [
    "AmbientDaemon",
    "DaemonConfig", 
    "ExecutionEvent",
    "FileMonitor",
    "FileChangeEvent",
    "GitMonitor",
    "GitEvent",
    "TerminalTracker", 
    "TerminalEvent",
]