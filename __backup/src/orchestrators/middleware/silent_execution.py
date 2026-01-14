"""
Silent Execution Middleware
============================
Suppresses verbose output during execution, showing only essential information.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 3 Task: 3.1
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import sys
from io import StringIO


class OutputLevel(Enum):
    """Output verbosity levels"""
    SILENT = "silent"  # No output
    ESSENTIAL = "essential"  # Only critical information
    NORMAL = "normal"  # Standard output
    VERBOSE = "verbose"  # Full details


@dataclass
class OutputMessage:
    """Represents a captured output message"""
    content: str
    level: OutputLevel
    source: str


class SilentExecutionMiddleware:
    """Middleware for controlling execution output verbosity"""
    
    def __init__(self, output_level: OutputLevel = OutputLevel.ESSENTIAL):
        """
        Initialize silent execution middleware
        
        Args:
            output_level: Desired output verbosity level
        """
        self.output_level = output_level
        self.captured_output: List[OutputMessage] = []
        self._original_stdout = None
        self._original_stderr = None
        self._buffer = None
        self._is_suppressing = False
    
    def start_suppression(self) -> None:
        """Start suppressing output"""
        if self._is_suppressing:
            return
            
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._buffer = StringIO()
        
        if self.output_level == OutputLevel.SILENT:
            sys.stdout = self._buffer
            sys.stderr = self._buffer
        
        self._is_suppressing = True
    
    def stop_suppression(self) -> str:
        """
        Stop suppressing output and return captured content
        
        Returns:
            Captured output as string
        """
        if not self._is_suppressing:
            return ""
        
        # Restore original streams
        if self._original_stdout:
            sys.stdout = self._original_stdout
        if self._original_stderr:
            sys.stderr = self._original_stderr
        
        # Get captured output
        captured = self._buffer.getvalue() if self._buffer else ""
        
        # Reset state
        self._is_suppressing = False
        self._buffer = None
        
        return captured
    
    def capture_message(
        self,
        message: str,
        level: OutputLevel,
        source: str = "unknown"
    ) -> None:
        """
        Capture a message with specified level
        
        Args:
            message: Message content
            level: Output level
            source: Source of the message
        """
        msg = OutputMessage(content=message, level=level, source=source)
        self.captured_output.append(msg)
        
        # Only output if level is appropriate
        if self._should_output(level):
            print(message)
    
    def _should_output(self, level: OutputLevel) -> bool:
        """
        Check if message should be output based on current output level
        
        Args:
            level: Message output level
            
        Returns:
            True if message should be output
        """
        level_order = {
            OutputLevel.SILENT: 0,
            OutputLevel.ESSENTIAL: 1,
            OutputLevel.NORMAL: 2,
            OutputLevel.VERBOSE: 3
        }
        
        return level_order[level] <= level_order[self.output_level]
    
    def get_captured_output(
        self,
        level_filter: Optional[OutputLevel] = None
    ) -> List[OutputMessage]:
        """
        Get captured output messages
        
        Args:
            level_filter: Optional filter by output level
            
        Returns:
            List of captured messages
        """
        if level_filter:
            return [msg for msg in self.captured_output if msg.level == level_filter]
        return self.captured_output
    
    def clear_captured(self) -> None:
        """Clear captured output"""
        self.captured_output.clear()
