"""
Test Failure Marker Injection Strategy

Analyzes Python tracebacks to identify user code locations and inject markers.

Strategy:
    1. Parse traceback from test failure event
    2. Skip test framework lines (pytest, unittest)
    3. Identify first user code line
    4. Inject marker at failure location

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Stage 2

AC-ID: AC-WAVE-R-S2-004
"""

import traceback
from typing import List
from pathlib import Path

from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import AbstractInjectionStrategy, MarkerContext


class TestFailureStrategy(AbstractInjectionStrategy):
    """
    Strategy for injecting markers on test failures.
    
    Parses Python tracebacks to find user code locations.
    """
    
    def analyze(self, context: MarkerContext) -> List[int]:
        """
        Analyze test failure context to find marker injection point.
        
        Args:
            context: MarkerContext with failure_reason containing traceback
        
        Returns:
            List containing single line number (first user code line)
        """
        failure_reason = context.additional_context.get("failure_reason", "")
        
        # Parse traceback
        user_line = self._find_first_user_code_line(
            failure_reason,
            context.file_path
        )
        
        if user_line is None:
            # Fallback to line_number from context
            return [context.line_number] if context.line_number > 0 else []
        
        return [user_line]
    
    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """
        Format test failure marker.
        
        Args:
            context: MarkerContext
            line_number: Target line number
        
        Returns:
            Formatted marker string
        """
        test_name = context.additional_context.get("test_name", "unknown")
        timestamp = context.additional_context.get("timestamp", "")
        
        marker = (
            f"test={test_name} | time={timestamp}"
        )
        
        return marker
    
    def _find_first_user_code_line(
        self,
        traceback_text: str,
        file_path: str
    ) -> int:
        """
        Parse traceback to find first user code line.
        
        Args:
            traceback_text: Traceback string from test failure
            file_path: Path to source file
        
        Returns:
            Line number of first user code, or None if not found
        """
        if not traceback_text:
            return None
        
        # Framework patterns to skip
        framework_patterns = [
            "/pytest/",
            "/unittest/",
            "/_pytest/",
            "/pluggy/",
            "/python3.",
        ]
        
        # Parse traceback lines
        for line in traceback_text.split('\n'):
            if 'File "' in line and ', line ' in line:
                # Extract file and line number
                try:
                    file_part = line.split('File "')[1].split('"')[0]
                    line_part = line.split(', line ')[1].split(',')[0]
                    line_num = int(line_part.strip())
                    
                    # Skip framework lines
                    if any(pattern in file_part for pattern in framework_patterns):
                        continue
                    
                    # Check if matches target file
                    if Path(file_part).name == Path(file_path).name:
                        return line_num - 1  # 0-indexed
                
                except (IndexError, ValueError):
                    continue
        
        return None
