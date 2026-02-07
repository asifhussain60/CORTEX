"""
Hidden issue detector - finds performance, memory, concurrency issues.

Module: cortex.orchestrators.response.hidden_issue_detector
Author: Asif Hussain
Created: 2026-02-07
Version: 1.0
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass
import re


# ============================================================================
# ENUMERATIONS
# ============================================================================


class IssueType(str, Enum):
    """Type of hidden issue."""
    
    PERFORMANCE = "performance"
    """Performance bottleneck"""
    
    MEMORY = "memory"
    """Memory leak or excessive allocation"""
    
    CONCURRENCY = "concurrency"
    """Thread-safety or race condition"""


class IssueSeverity(str, Enum):
    """Severity of issue."""
    
    INFO = "info"
    """Informational"""
    
    WARNING = "warning"
    """Warning"""
    
    CRITICAL = "critical"
    """Critical issue"""


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class HiddenIssue:
    """A hidden issue in code."""
    
    issue_type: IssueType
    severity: IssueSeverity
    location: str
    message: str
    impact: str
    suggestion: str


@dataclass
class CodeAnalysisContext:
    """Context for code analysis."""
    
    function_name: str
    code: str
    language: str = "python"


# ============================================================================
# PERFORMANCE DETECTOR
# ============================================================================


class PerformanceDetector:
    """Detects performance issues."""
    
    def detect(self, context: CodeAnalysisContext) -> List[HiddenIssue]:
        """Detect performance issues."""
        issues = []
        
        # Check for nested loops
        if self._has_nested_loops(context.code):
            issues.append(HiddenIssue(
                issue_type=IssueType.PERFORMANCE,
                severity=IssueSeverity.WARNING,
                location=f"{context.function_name}:1",
                message="Nested loops detected - O(n²) time complexity",
                impact="High - quadratic scaling on input size",
                suggestion="Consider using sets, dicts, or sorting for O(n log n) solution"
            ))
        
        # Check for list operations in loops
        if "append" in context.code and "for " in context.code:
            issues.append(HiddenIssue(
                issue_type=IssueType.PERFORMANCE,
                severity=IssueSeverity.INFO,
                location=f"{context.function_name}:append",
                message="List append in loop may allocate memory repeatedly",
                impact="Medium - repeated allocations slow execution",
                suggestion="Use list comprehension or pre-allocate list with fixed size"
            ))
        
        return issues
    
    @staticmethod
    def _has_nested_loops(code: str) -> bool:
        """Check if code has nested loops."""
        for_count = 0
        for line in code.split('\n'):
            if 'for ' in line and not line.strip().startswith('#'):
                for_count += 1
                if for_count > 1:
                    return True
        return False


# ============================================================================
# MEMORY DETECTOR
# ============================================================================


class MemoryDetector:
    """Detects memory issues."""
    
    def detect(self, context: CodeAnalysisContext) -> List[HiddenIssue]:
        """Detect memory issues."""
        issues = []
        
        # Check for unbounded list growth
        if "append" in context.code and "while " in context.code:
            issues.append(HiddenIssue(
                issue_type=IssueType.MEMORY,
                severity=IssueSeverity.WARNING,
                location=f"{context.function_name}:append",
                message="Unbounded list growth in loop - potential memory leak",
                impact="High - memory grows without limit",
                suggestion="Add bounds checking or use a fixed-size data structure"
            ))
        
        # Check for deep recursion
        if context.code.count(context.function_name + "(") > 1:
            issues.append(HiddenIssue(
                issue_type=IssueType.MEMORY,
                severity=IssueSeverity.INFO,
                location=f"{context.function_name}:recursive",
                message="Recursive function detected - risk of stack overflow",
                impact="Medium - deep recursion consumes stack memory",
                suggestion="Consider iterative solution or increase recursion limit"
            ))
        
        # Check for large object copies
        if ".copy()" in context.code:
            issues.append(HiddenIssue(
                issue_type=IssueType.MEMORY,
                severity=IssueSeverity.INFO,
                location=f"{context.function_name}:copy",
                message="Explicit object copy - doubles memory usage",
                impact="Medium - temporary memory spike",
                suggestion="Review if copy is necessary; consider references or views"
            ))
        
        return issues


# ============================================================================
# CONCURRENCY DETECTOR
# ============================================================================


class ConcurrencyDetector:
    """Detects concurrency issues."""
    
    def detect(self, context: CodeAnalysisContext) -> List[HiddenIssue]:
        """Detect concurrency issues."""
        issues = []
        
        # Check for shared mutable state
        if "global " in context.code and any(op in context.code for op in ["=", "append", "pop"]):
            issues.append(HiddenIssue(
                issue_type=IssueType.CONCURRENCY,
                severity=IssueSeverity.CRITICAL,
                location=f"{context.function_name}:global",
                message="Unprotected global state modification - race condition",
                impact="Critical - data corruption in multithreaded context",
                suggestion="Use locks (threading.Lock) or thread-safe data structures"
            ))
        
        # Check for lock operations
        if "acquire()" in context.code and context.code.count("acquire()") > 1:
            issues.append(HiddenIssue(
                issue_type=IssueType.CONCURRENCY,
                severity=IssueSeverity.WARNING,
                location=f"{context.function_name}:locks",
                message="Multiple lock acquisitions - potential deadlock",
                impact="High - circular wait may freeze program",
                suggestion="Use context managers (with statement) or ensure consistent lock order"
            ))
        
        # Check for thread-unsafe collections
        if "shared_list" in context.code or ("[]" in context.code and "thread" in context.code.lower()):
            issues.append(HiddenIssue(
                issue_type=IssueType.CONCURRENCY,
                severity=IssueSeverity.WARNING,
                location=f"{context.function_name}:collection",
                message="Shared collection without synchronization",
                impact="High - concurrent modifications cause data loss",
                suggestion="Use queue.Queue, threading.Lock, or concurrent.futures"
            ))
        
        return issues


# ============================================================================
# HIDDEN ISSUE DETECTOR (ORCHESTRATOR)
# ============================================================================


class HiddenIssueDetector:
    """Orchestrator for hidden issue detection."""
    
    def __init__(self):
        """Initialize detector."""
        self.performance = PerformanceDetector()
        self.memory = MemoryDetector()
        self.concurrency = ConcurrencyDetector()
    
    def detect(self, context: CodeAnalysisContext) -> List[HiddenIssue]:
        """
        Detect all hidden issues.
        
        Args:
            context: Code analysis context
        
        Returns:
            List of hidden issues
        """
        issues = []
        
        # Run all detectors
        issues.extend(self.performance.detect(context))
        issues.extend(self.memory.detect(context))
        issues.extend(self.concurrency.detect(context))
        
        return issues


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "IssueType",
    "IssueSeverity",
    "HiddenIssue",
    "CodeAnalysisContext",
    "PerformanceDetector",
    "MemoryDetector",
    "ConcurrencyDetector",
    "HiddenIssueDetector",
]
