"""
Base Strategy for Debug Marker Injection

Defines the interface for all marker injection strategies.

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - Strategy Pattern (Gang of Four)
    - WAVE-R Stage 2

AC-ID: AC-WAVE-R-S2-002
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MarkerContext:
    """Context information for marker injection."""
    trigger_type: str  # test_failure | refactor_regression | governance_violation
    session_id: str
    file_path: str
    line_number: int
    additional_context: Dict[str, Any]


@dataclass
class InjectionResult:
    """Result of marker injection operation."""
    success: bool
    file_path: str
    lines_injected: List[int]
    error: Optional[str] = None


class AbstractInjectionStrategy(ABC):
    """
    Base class for all marker injection strategies.
    
    Subclasses must implement:
        - analyze(): Determine marker injection locations
        - format_marker(): Format marker content
    """
    
    @abstractmethod
    def analyze(self, context: MarkerContext) -> List[int]:
        """
        Analyze context to determine marker injection locations.
        
        Args:
            context: Marker injection context
        
        Returns:
            List of line numbers where markers should be injected
        """
        pass
    
    @abstractmethod
    def format_marker(self, context: MarkerContext, line_number: int) -> str:
        """
        Format marker content for injection.
        
        Args:
            context: Marker injection context
            line_number: Target line number
        
        Returns:
            Formatted marker string (multi-line if needed)
        """
        pass
    
    def inject(self, context: MarkerContext) -> InjectionResult:
        """
        Execute marker injection.
        
        Args:
            context: Marker injection context
        
        Returns:
            InjectionResult with success status and details
        """
        try:
            # Analyze to find injection points
            target_lines = self.analyze(context)
            
            if not target_lines:
                return InjectionResult(
                    success=False,
                    file_path=context.file_path,
                    lines_injected=[],
                    error="No valid injection points found"
                )
            
            # Read file content
            file_path = Path(context.file_path)
            if not file_path.exists():
                return InjectionResult(
                    success=False,
                    file_path=context.file_path,
                    lines_injected=[],
                    error=f"File not found: {context.file_path}"
                )
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Inject markers (reverse order to preserve line numbers)
            for line_num in sorted(target_lines, reverse=True):
                if 0 <= line_num < len(lines):
                    marker = self.format_marker(context, line_num)
                    
                    # Check if marker already exists
                        continue  # Skip if already present
                    
                    # Insert marker above target line
                    indent = self._get_indent(lines[line_num])
                    marker_line = f"{indent}# {marker}\n"
                    lines.insert(line_num, marker_line)
            
            # Atomic write (tempfile + rename)
            import tempfile
            import os
            
            fd, temp_path = tempfile.mkstemp(dir=file_path.parent, text=True)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                os.replace(temp_path, file_path)
            except Exception as e:
                os.unlink(temp_path)
                raise e
            
            return InjectionResult(
                success=True,
                file_path=context.file_path,
                lines_injected=target_lines
            )
        
        except Exception as e:
            return InjectionResult(
                success=False,
                file_path=context.file_path,
                lines_injected=[],
                error=str(e)
            )
    
    def _get_indent(self, line: str) -> str:
        """Extract indentation from line."""
        return line[:len(line) - len(line.lstrip())]
