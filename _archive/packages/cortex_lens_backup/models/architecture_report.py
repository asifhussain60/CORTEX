"""
Phase 66 Stage 1: Architecture Report Data Model

Represents the output of architectural pattern analysis.

AC_START: AC-PHASE66-S1-002
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class ArchitectureReport:
    """
    Report from architectural pattern analysis.
    
    Contains detected patterns, violations, component hierarchy,
    and dependency graph information.
    
    Attributes:
        repo_path: Path to analyzed repository
        patterns_detected: List of detected architectural patterns
        violations: List of architectural violations found
        component_hierarchy: Hierarchical structure of components
        dependency_graph: Graph of file dependencies
        total_files_analyzed: Count of files processed
        analysis_timestamp: When analysis was performed
    
    Example:
        >>> report = ArchitectureReport(
        ...     repo_path=Path("/repo"),
        ...     patterns_detected=[{"pattern_type": "MVC"}],
        ...     violations=[],
        ...     component_hierarchy={"presentation": []},
        ...     dependency_graph={},
        ...     total_files_analyzed=10,
        ...     analysis_timestamp="2026-02-09T12:00:00Z"
        ... )
        >>> report.get_violation_summary()
        {'total_violations': 0, 'by_type': {}, 'by_severity': {}}
    """
    
    repo_path: Path
    patterns_detected: List[Dict[str, Any]] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    component_hierarchy: Dict[str, Any] = field(default_factory=dict)
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)
    total_files_analyzed: int = 0
    analysis_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary for JSON export.
        
        Returns:
            Dictionary representation of report
        """
        return {
            "repo_path": str(self.repo_path),
            "patterns_detected": self.patterns_detected,
            "violations": self.violations,
            "component_hierarchy": self.component_hierarchy,
            "dependency_graph": {
                str(k): [str(v) for v in vals]
                for k, vals in self.dependency_graph.items()
            },
            "total_files_analyzed": self.total_files_analyzed,
            "analysis_timestamp": self.analysis_timestamp,
        }
    
    def get_violation_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics for violations.
        
        Returns:
            Dictionary with total counts, breakdown by type and severity
            
        Example:
            >>> report.violations = [
            ...     {"violation_type": "circular", "severity": "high"},
            ...     {"violation_type": "layering", "severity": "medium"}
            ... ]
            >>> summary = report.get_violation_summary()
            >>> summary["total_violations"]
            2
        """
        summary = {
            "total_violations": len(self.violations),
            "by_type": {},
            "by_severity": {},
        }
        
        for violation in self.violations:
            # Count by type
            vtype = violation.get("violation_type", "unknown")
            summary["by_type"][vtype] = summary["by_type"].get(vtype, 0) + 1
            
            # Count by severity
            severity = violation.get("severity", "unknown")
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        return summary
    
    def get_critical_violations(self) -> List[Dict[str, Any]]:
        """
        Get only critical and high severity violations.
        
        Returns:
            Filtered list of high-priority violations
        """
        return [
            v for v in self.violations
            if v.get("severity") in ["critical", "high"]
        ]
    
    def has_violations(self) -> bool:
        """Check if any violations were detected."""
        return len(self.violations) > 0
    
    def get_pattern_summary(self) -> Dict[str, int]:
        """
        Get count of each detected pattern type.
        
        Returns:
            Dictionary mapping pattern types to counts
        """
        summary = {}
        for pattern in self.patterns_detected:
            ptype = pattern.get("pattern_type", "unknown")
            summary[ptype] = summary.get(ptype, 0) + 1
        return summary


# AC_COMPLETE: AC-PHASE66-S1-002 ✅ ArchitectureReport model complete
