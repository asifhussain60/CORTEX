"""
Refactor Regression Marker Injection Strategy

Analyzes git diffs to identify affected lines and inject markers.

Strategy:
    1. Parse git diff from refactor regression event
    2. Identify modified/deleted lines
    3. Inject markers at regression locations

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Stage 2

AC-ID: AC-WAVE-R-S2-005
"""

from typing import List
from pathlib import Path

from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import AbstractInjectionStrategy, MarkerContext


class RefactorRegressionStrategy(AbstractInjectionStrategy):
    """
    Strategy for injecting markers on refactor regressions.
    
    Parses git diffs to find affected code locations.
    """
    
    def analyze(self, context: MarkerContext) -> List[int]:
        """
        Analyze refactor regression context to find marker injection points.
        
        Args:
            context: MarkerContext with git_diff in additional_context
        
        Returns:
            List of line numbers affected by regression
        """
        git_diff = context.additional_context.get("git_diff", "")
        
        # Parse diff to find affected lines
        affected_lines = self._parse_git_diff(git_diff, context.file_path)
        
        if not affected_lines:
            # Fallback to line_number from context
            return [context.line_number] if context.line_number > 0 else []
        
        return affected_lines
    
    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """
        Format refactor regression marker.
        
        Args:
            context: MarkerContext
            line_number: Target line number
        
        Returns:
            Formatted marker string
        """
        regression_type = context.additional_context.get("regression_type", "unknown")
        timestamp = context.additional_context.get("timestamp", "")
        
        marker = (
            f"type={regression_type} | time={timestamp}"
        )
        
        return marker
    
    def _parse_git_diff(self, git_diff: str, file_path: str) -> List[int]:
        """
        Parse git diff to find affected lines.
        
        Args:
            git_diff: Git diff output
            file_path: Path to source file
        
        Returns:
            List of line numbers affected by diff
        """
        if not git_diff:
            return []
        
        affected_lines = []
        current_file = None
        current_line = 0
        
        for line in git_diff.split('\n'):
            # Track file changes
            if line.startswith('+++'):
                current_file = line.split('+++')[1].strip()
                if current_file.startswith('b/'):
                    current_file = current_file[2:]
            
            # Parse hunk headers (@@ -old,len +new,len @@)
            elif line.startswith('@@'):
                try:
                    new_part = line.split('+')[1].split('@@')[0].strip()
                    current_line = int(new_part.split(',')[0])
                except (IndexError, ValueError):
                    continue
            
            # Track line changes
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                if current_file and Path(current_file).name == Path(file_path).name:
                    affected_lines.append(current_line - 1)  # 0-indexed
                current_line += 1
            
            elif line.startswith('-') and not line.startswith('---'):
                # Deleted line (don't increment current_line)
                pass
            
            else:
                # Unchanged line
                current_line += 1
        
        return affected_lines
