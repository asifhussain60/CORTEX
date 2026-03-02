"""
Blind Spot Detector for finding untested code paths.

Detects:
- Uncovered branches (if/else paths not tested)
- Untested error handlers (except blocks not covered)
- Dead code paths (unreachable code after returns)

Part of WAVE-2 Stage 2: Intelligent Test Generation.
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Set


class BlindSpotType(Enum):
    """Types of blind spots in code coverage."""
    
    UNCOVERED_BRANCH = "uncovered_branch"
    UNTESTED_ERROR_HANDLER = "untested_error_handler"
    DEAD_CODE = "dead_code"


@dataclass
class CoverageData:
    """Coverage data for a file."""
    
    file_path: Path
    covered_lines: Set[int]
    missing_lines: Set[int]
    branch_coverage: float  # 0.0 to 1.0


@dataclass
class BlindSpot:
    """Represents a blind spot in test coverage."""
    
    type: BlindSpotType
    file_path: Path
    line_number: int
    description: str
    severity: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW


class BlindSpotDetector:
    """
    Detects untested code paths and blind spots in test coverage.
    
    Uses coverage data and AST analysis to find:
    - Branches with low coverage
    - Exception handlers without tests
    - Dead code that can never execute
    
    Args:
        min_coverage_threshold: Minimum coverage % to flag (default 80.0)
        include_dead_code: Whether to detect dead code (default True)
        
    Raises:
        ValueError: If coverage threshold not in valid range
    """
    
    def __init__(
        self,
        min_coverage_threshold: float = 80.0,
        include_dead_code: bool = True
    ) -> None:
        """Initialize BlindSpotDetector with configuration."""
        if not 0 <= min_coverage_threshold <= 100:
            raise ValueError("Coverage threshold must be between 0 and 100")
        
        self.min_coverage_threshold = min_coverage_threshold
        self.include_dead_code = include_dead_code
    
    def find_uncovered_branches(self, coverage_data: CoverageData) -> List[BlindSpot]:
        """
        Find uncovered branches in code.
        
        Identifies if/else branches, loops, and conditional paths that
        lack test coverage.
        
        Args:
            coverage_data: Coverage information for the file
            
        Returns:
            List of blind spots for uncovered branches
        """
        blind_spots = []
        
        # Calculate overall coverage
        total_lines = len(coverage_data.covered_lines) + len(coverage_data.missing_lines)
        if total_lines == 0:
            return blind_spots
        
        coverage_pct = (len(coverage_data.covered_lines) / total_lines) * 100
        
        # If coverage meets threshold, no blind spots
        if coverage_pct >= self.min_coverage_threshold:
            return blind_spots
        
        # Flag branches with low coverage
        if coverage_data.branch_coverage < (self.min_coverage_threshold / 100):
            for line_num in sorted(coverage_data.missing_lines):
                blind_spots.append(BlindSpot(
                    type=BlindSpotType.UNCOVERED_BRANCH,
                    file_path=coverage_data.file_path,
                    line_number=line_num,
                    description=f"Uncovered branch at line {line_num}",
                    severity="HIGH" if coverage_data.branch_coverage < 0.5 else "MEDIUM"
                ))
        
        return blind_spots
    
    def find_untested_error_handlers(
        self,
        coverage_data: CoverageData,
        file_content: str
    ) -> List[BlindSpot]:
        """
        Find untested error handlers (except blocks).
        
        Parses the file AST to locate exception handlers and checks
        if they are covered by tests.
        
        Args:
            coverage_data: Coverage information for the file
            file_content: Source code content
            
        Returns:
            List of blind spots for untested error handlers
        """
        blind_spots = []
        
        try:
            tree = ast.parse(file_content)
        except SyntaxError:
            return blind_spots
        
        # Find all except handlers
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                # Get line number of except block
                handler_line = node.lineno
                
                # Check if except handler or its body is in missing lines
                is_untested = handler_line in coverage_data.missing_lines
                
                # Also check if body lines are missing
                if node.body:
                    for body_node in node.body:
                        if hasattr(body_node, 'lineno'):
                            if body_node.lineno in coverage_data.missing_lines:
                                is_untested = True
                                break
                
                if is_untested:
                    exception_type = "Exception"
                    if node.type:
                        if isinstance(node.type, ast.Name):
                            exception_type = node.type.id
                    
                    # Use body line number if available, else handler line
                    report_line = node.body[0].lineno if node.body else handler_line
                    
                    blind_spots.append(BlindSpot(
                        type=BlindSpotType.UNTESTED_ERROR_HANDLER,
                        file_path=coverage_data.file_path,
                        line_number=report_line,
                        description=f"Untested {exception_type} handler at line {report_line}",
                        severity="HIGH"  # Error handlers are critical
                    ))
        
        return blind_spots
    
    def find_dead_code_paths(
        self,
        coverage_data: CoverageData,
        file_content: str
    ) -> List[BlindSpot]:
        """
        Find dead code paths that can never execute.
        
        Detects code after return statements, unreachable branches,
        and other patterns that indicate dead code.
        
        Args:
            coverage_data: Coverage information for the file
            file_content: Source code content
            
        Returns:
            List of blind spots for dead code
        """
        if not self.include_dead_code:
            return []
        
        blind_spots = []
        lines = file_content.split('\n')
        
        # Simple heuristic: code after return in same block
        for i, line in enumerate(lines):
            stripped = line.strip()
            line_num = i + 1  # Convert to 1-indexed
            
            # If line is a return statement
            if stripped.startswith('return '):
                # Get indentation level of return
                return_indent = len(line) - len(line.lstrip())
                
                # Check all following lines at same/deeper indentation
                for j in range(i + 1, len(lines)):
                    next_line = lines[j]
                    next_stripped = next_line.strip()
                    
                    # Skip empty lines
                    if not next_stripped:
                        continue
                    
                    next_indent = len(next_line) - len(next_line.lstrip())
                    next_line_num = j + 1
                    
                    # If we've dedented, we're out of the block
                    if next_indent < return_indent:
                        break
                    
                    # If at same/deeper indent and not a function/class def, it's dead code
                    if (next_indent >= return_indent and
                        not next_stripped.startswith('def ') and
                        not next_stripped.startswith('class ') and
                        next_line_num in coverage_data.missing_lines):
                        
                        blind_spots.append(BlindSpot(
                            type=BlindSpotType.DEAD_CODE,
                            file_path=coverage_data.file_path,
                            line_number=next_line_num,
                            description=f"Dead code after return at line {next_line_num}",
                            severity="LOW"  # Dead code is less critical than untested handlers
                        ))
        
        return blind_spots
    
    def analyze_file(
        self,
        coverage_data: CoverageData,
        file_content: str
    ) -> List[BlindSpot]:
        """
        Perform comprehensive blind spot analysis on a file.
        
        Combines all detection methods to provide complete analysis
        of untested code paths.
        
        Args:
            coverage_data: Coverage information for the file
            file_content: Source code content
            
        Returns:
            List of all blind spots found in the file
        """
        blind_spots = []
        
        # Find all types of blind spots
        blind_spots.extend(self.find_uncovered_branches(coverage_data))
        blind_spots.extend(self.find_untested_error_handlers(coverage_data, file_content))
        blind_spots.extend(self.find_dead_code_paths(coverage_data, file_content))
        
        return blind_spots
