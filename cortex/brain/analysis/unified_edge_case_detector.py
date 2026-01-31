"""
Phase 8.5: Unified Edge Case Detector

Aggregates edge cases from all Microsoft stack analyzers and provides
priority classification, remediation suggestions, and impact analysis.

AC-ID: AC-PHASE-8.5-04 (Task LENS-MS-004)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class EdgeCaseSeverity(Enum):
    """Edge case severity levels."""
    CRITICAL = "critical"  # Security, data loss
    HIGH = "high"  # Bugs, performance, reliability
    MEDIUM = "medium"  # Code quality, maintainability
    LOW = "low"  # Style, warnings


@dataclass
class AggregatedEdgeCase:
    """
    Aggregated edge case with remediation guidance.
    
    Attributes:
        type: Edge case type identifier
        severity: Severity level
        occurrences: Number of occurrences
        files: List of affected files
        lines: List of line numbers
        messages: List of detection messages
        remediation: Suggested fix
        impact: Potential impact description
        priority_score: Calculated priority (0-100)
    """
    type: str
    severity: EdgeCaseSeverity
    occurrences: int
    files: List[str]
    lines: List[int]
    messages: List[str]
    remediation: str
    impact: str
    priority_score: int


class UnifiedEdgeCaseDetector:
    """
    Aggregates and prioritizes edge cases from multiple analyzers.
    
    Combines results from:
    - CSharpASTAnalyzer
    - SQLOracleAnalyzer
    - AngularTypeScriptAnalyzer
    
    Provides:
    - Severity classification
    - Priority scoring
    - Remediation guidance
    - Impact analysis
    
    Example:
        detector = UnifiedEdgeCaseDetector()
        
        # Add edge cases from analyzers
        detector.add_edge_cases(csharp_result.edge_cases, "C#")
        detector.add_edge_cases(sql_result.edge_cases, "SQL")
        detector.add_edge_cases(angular_result.edge_cases, "Angular")
        
        # Get aggregated results
        critical = detector.get_by_severity(EdgeCaseSeverity.CRITICAL)
        top_10 = detector.get_top_priority(10)
    """
    
    def __init__(self) -> None:
        """Initialize unified edge case detector."""
        self.logger = EnhancedAuditLogger.instance()
        self.edge_cases: Dict[str, AggregatedEdgeCase] = {}
        self.raw_edge_cases: List[Dict[str, Any]] = []
        
        # Remediation templates
        self.remediations: Dict[str, str] = {
            # C# edge cases
            "missing_null_check": "Add null parameter validation: if (param == null) throw new ArgumentNullException(nameof(param));",
            "async_void": "Change async void to async Task for proper exception handling",
            "deadlock_risk": "Use ConfigureAwait(false) or await directly instead of .Result/.Wait()",
            "missing_dispose": "Wrap IDisposable objects in using statement: using (var obj = new ...)",
            
            # SQL edge cases
            "sql_injection": "Use parameterized queries: cmd.Parameters.AddWithValue(\"@param\", value)",
            "select_star": "Specify required columns explicitly: SELECT col1, col2 FROM table",
            "missing_where": "Add WHERE clause to limit affected rows",
            "missing_transaction": "Wrap DML statements in explicit transaction with COMMIT/ROLLBACK",
            "cursor_usage": "Replace cursor with set-based operation (JOIN, UPDATE with subquery)",
            
            # Angular edge cases
            "memory_leak": "Unsubscribe in ngOnDestroy: this.subscription.unsubscribe() or use takeUntil()",
            "unsafe_html": "Sanitize HTML input or use [textContent] instead of [innerHTML]",
            "missing_error_handler": "Add .pipe(catchError(error => ...)) to handle HTTP errors",
            "any_type": "Replace 'any' with specific interface or type",
        }
        
        # Impact descriptions
        self.impacts: Dict[str, str] = {
            # C# impacts
            "missing_null_check": "NullReferenceException at runtime, application crash",
            "async_void": "Unhandled exceptions crash application, no async/await propagation",
            "deadlock_risk": "Thread pool starvation, application hang",
            "missing_dispose": "Resource leak, file handles/connections exhausted",
            
            # SQL impacts
            "sql_injection": "CRITICAL: Data breach, unauthorized access, data manipulation",
            "select_star": "Poor performance, unnecessary network traffic, schema coupling",
            "missing_where": "CRITICAL: Accidental data modification/deletion of all rows",
            "missing_transaction": "Data inconsistency, partial updates, orphaned records",
            "cursor_usage": "Slow performance, RBAR (Row-By-Agonizing-Row) anti-pattern",
            
            # Angular impacts
            "memory_leak": "Increasing memory usage, application slowdown, eventual crash",
            "unsafe_html": "CRITICAL: XSS vulnerability, code injection, session hijacking",
            "missing_error_handler": "Silent failures, poor user experience, no error logging",
            "any_type": "Type safety compromised, IDE autocomplete broken, runtime errors",
        }
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.5-04",
            operation="EDGE_CASE_DETECTOR_INIT",
            success=True,
            details={
                "remediations": len(self.remediations),
                "impacts": len(self.impacts),
            },
        )
    
    def add_edge_cases(
        self,
        edge_cases: List[Dict[str, Any]],
        source: str,
    ) -> None:
        """
        Add edge cases from analyzer result.
        
        AC-PHASE-8.5-04: Aggregate edge cases from multiple sources
        
        Args:
            edge_cases: List of edge case dicts from analyzer
            source: Source analyzer name (C#, SQL, Angular)
        """
        for ec in edge_cases:
            ec["source"] = source
            self.raw_edge_cases.append(ec)
        
        self._aggregate_edge_cases()
    
    def _aggregate_edge_cases(self) -> None:
        """Aggregate edge cases by type."""
        # Group by type
        grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for ec in self.raw_edge_cases:
            grouped[ec["type"]].append(ec)
        
        # Create aggregated edge cases
        self.edge_cases = {}
        for edge_type, cases in grouped.items():
            # Parse severity
            severity_str = cases[0].get("severity", "medium")
            severity = EdgeCaseSeverity(severity_str)
            
            # Collect files and lines
            files = list(set(ec.get("file", "unknown") for ec in cases))
            lines = [ec.get("line", 0) for ec in cases]
            messages = [ec.get("message", "") for ec in cases]
            
            # Calculate priority score (0-100)
            priority = self._calculate_priority(severity, len(cases))
            
            self.edge_cases[edge_type] = AggregatedEdgeCase(
                type=edge_type,
                severity=severity,
                occurrences=len(cases),
                files=files,
                lines=lines,
                messages=messages,
                remediation=self.remediations.get(edge_type, "Manual review required"),
                impact=self.impacts.get(edge_type, "Unknown impact"),
                priority_score=priority,
            )
    
    def _calculate_priority(
        self,
        severity: EdgeCaseSeverity,
        occurrence_count: int,
    ) -> int:
        """
        Calculate priority score (0-100).
        
        Formula: (severity_weight * 50) + (min(occurrences, 10) * 5)
        
        Args:
            severity: Edge case severity
            occurrence_count: Number of occurrences
        
        Returns:
            int: Priority score (0-100)
        """
        severity_weights = {
            EdgeCaseSeverity.CRITICAL: 1.0,
            EdgeCaseSeverity.HIGH: 0.7,
            EdgeCaseSeverity.MEDIUM: 0.4,
            EdgeCaseSeverity.LOW: 0.2,
        }
        
        base_score = severity_weights[severity] * 50
        occurrence_score = min(occurrence_count, 10) * 5
        
        return int(base_score + occurrence_score)
    
    def get_by_severity(
        self,
        severity: EdgeCaseSeverity,
    ) -> List[AggregatedEdgeCase]:
        """
        Get edge cases filtered by severity.
        
        AC-PHASE-8.5-04: Filter by severity level
        
        Args:
            severity: Severity level to filter by
        
        Returns:
            List[AggregatedEdgeCase]: Filtered edge cases
        """
        return [
            ec for ec in self.edge_cases.values()
            if ec.severity == severity
        ]
    
    def get_top_priority(self, limit: int = 10) -> List[AggregatedEdgeCase]:
        """
        Get top priority edge cases.
        
        AC-PHASE-8.5-04: Prioritization for remediation planning
        
        Args:
            limit: Maximum number of results
        
        Returns:
            List[AggregatedEdgeCase]: Top priority edge cases
        """
        sorted_cases = sorted(
            self.edge_cases.values(),
            key=lambda x: x.priority_score,
            reverse=True,
        )
        return sorted_cases[:limit]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics.
        
        Returns:
            Dict: Summary statistics with counts by severity
        """
        stats = {
            "total_edge_cases": len(self.edge_cases),
            "total_occurrences": sum(ec.occurrences for ec in self.edge_cases.values()),
            "by_severity": {
                severity.value: len(self.get_by_severity(severity))
                for severity in EdgeCaseSeverity
            },
            "top_priority": self.get_top_priority(5),
        }
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.5-04",
            operation="EDGE_CASE_SUMMARY",
            success=True,
            details=stats,
        )
        
        return stats
    
    def format_report(self) -> str:
        """
        Format human-readable edge case report.
        
        Returns:
            str: Formatted report
        """
        lines = [
            "═" * 80,
            "UNIFIED EDGE CASE DETECTION REPORT",
            "═" * 80,
            "",
        ]
        
        stats = self.get_summary_stats()
        lines.append(f"Total Edge Cases: {stats['total_edge_cases']}")
        lines.append(f"Total Occurrences: {stats['total_occurrences']}")
        lines.append("")
        
        lines.append("By Severity:")
        for severity, count in stats["by_severity"].items():
            lines.append(f"  {severity.upper()}: {count}")
        lines.append("")
        
        lines.append("─" * 80)
        lines.append("TOP 10 PRIORITY EDGE CASES")
        lines.append("─" * 80)
        
        for i, ec in enumerate(self.get_top_priority(10), 1):
            lines.append(f"\n{i}. {ec.type.upper()} ({ec.severity.value})")
            lines.append(f"   Priority Score: {ec.priority_score}")
            lines.append(f"   Occurrences: {ec.occurrences}")
            lines.append(f"   Impact: {ec.impact}")
            lines.append(f"   Remediation: {ec.remediation}")
        
        lines.append("\n" + "═" * 80)
        
        return "\n".join(lines)
