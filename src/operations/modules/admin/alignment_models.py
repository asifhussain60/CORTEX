"""
System Alignment Data Models

Data classes for system alignment validation and reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: IMPLEMENTATION
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.validation.conflict_detector import Conflict
from src.validation.remediation_engine import FixTemplate


@dataclass
class IntegrationScore:
    """Integration depth score for a feature (0-100%)."""
    feature_name: str
    feature_type: str  # 'orchestrator', 'agent', etc.
    discovered: bool = False  # 20 points
    imported: bool = False  # +20 points
    instantiated: bool = False  # +20 points
    documented: bool = False  # +10 points
    tested: bool = False  # +10 points
    wired: bool = False  # +10 points
    optimized: bool = False  # +10 points
    
    @property
    def score(self) -> int:
        """Calculate 0-100 integration score."""
        total = 0
        if self.discovered:
            total += 20
        if self.imported:
            total += 20
        if self.instantiated:
            total += 20
        if self.documented:
            total += 10
        if self.tested:
            total += 10
        if self.wired:
            total += 10
        if self.optimized:
            total += 10
        return total
    
    @property
    def status(self) -> str:
        """Get status text based on score."""
        score = self.score
        if score >= 90:
            return "[OK] Healthy"
        elif score >= 70:
            return "[WARN] Warning"
        else:
            return "[CRIT] Critical"
    
    @property
    def issues(self) -> List[str]:
        """List integration issues."""
        issues = []
        if not self.documented:
            issues.append("Missing documentation")
        if not self.tested:
            issues.append("No test coverage")
        if not self.wired:
            issues.append("Not wired to entry point")
        if not self.optimized:
            issues.append("Performance not validated")
        return issues


@dataclass
class RemediationSuggestion:
    """Auto-remediation suggestion for a feature."""
    feature_name: str
    suggestion_type: str  # 'wiring', 'test', 'documentation'
    content: str  # Generated code/template
    file_path: Optional[str] = None  # Where to save suggestion


@dataclass
class AlignmentReport:
    """System alignment validation report."""
    timestamp: datetime
    overall_health: int  # 0-100%
    critical_issues: int = 0
    warnings: int = 0
    feature_scores: Dict[str, IntegrationScore] = field(default_factory=dict)
    remediation_suggestions: List[RemediationSuggestion] = field(default_factory=list)
    orphaned_triggers: List[str] = field(default_factory=list)  # Triggers without features
    ghost_features: List[str] = field(default_factory=list)  # Features without triggers
    deployment_gate_results: Optional[Dict[str, Any]] = None  # Deployment quality gates
    package_purity_results: Optional[Dict[str, Any]] = None  # Admin leak detection
    suggestions: List[Dict[str, str]] = field(default_factory=list)
    # New validation fields
    organization_violations: List[Any] = field(default_factory=list)  # File organization issues
    organization_score: int = 100  # 0-100% file organization compliance
    header_violations: List[Any] = field(default_factory=list)  # Template header issues
    header_compliance_score: int = 100  # 0-100% template header compliance
    # Document governance fields
    doc_governance_violations: List[Any] = field(default_factory=list)  # Duplicate/overlapping docs
    doc_governance_score: int = 100  # 0-100% documentation governance compliance
    # Align 2.0 enhancements
    conflicts: List[Conflict] = field(default_factory=list)  # Detected ecosystem conflicts
    fix_templates: List[FixTemplate] = field(default_factory=list)  # Generated fix templates
    dashboard_report: Optional[str] = None  # Visual dashboard HTML/text
    
    @property
    def is_healthy(self) -> bool:
        """Check if system is healthy (>80% overall)."""
        return self.overall_health >= 80 and self.critical_issues == 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if system has non-critical warnings."""
        return self.warnings > 0 and self.critical_issues == 0
    
    @property
    def has_errors(self) -> bool:
        """Check if system has critical errors."""
        return self.critical_issues > 0
    
    @property
    def issues_found(self) -> int:
        """Total issues (critical + warnings)."""
        return self.critical_issues + self.warnings
