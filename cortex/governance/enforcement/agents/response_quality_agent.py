"""
Response Quality Agent - Layer 3 Quality Enhancement.

Extends EnforcementOrchestrator with 8th agent for response validation.
Provides runtime monitoring and telemetry (warning-only, never blocks).

Module: cortex.governance.enforcement.agents.response_quality_agent
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
Authority: ENH-064 Phase 3 - Quality Enhancement
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re

from cortex.governance.enforcement.agents.base_agent import (
    BaseEnforcementAgent,
    EnforcementResult,
    EnforcementSeverity
)


@dataclass
class ResponseMetrics:
    """Metrics for response quality validation."""
    
    length: int
    """Total response length in characters"""
    
    header_count: int
    """Number of markdown headers"""
    
    has_single_h1: bool
    """Whether response has exactly one h1 header"""
    
    hierarchy_violations: List[str]
    """List of hierarchy violations detected"""
    
    duplicate_sections: List[str]
    """List of potentially duplicate sections"""
    
    performance_ms: float
    """Time taken to generate response (ms)"""
    
    zones_used: int = 0
    """Number of content zones used"""
    
    template_count: int = 1
    """Number of templates assembled"""


@dataclass
class QualityViolation:
    """Single quality violation."""
    
    severity: EnforcementSeverity
    rule_id: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


class ResponseQualityAgent(BaseEnforcementAgent):
    """
    Response Quality Agent (8th EnforcementOrchestrator agent).
    
    Validates:
    - Response structure (header, hierarchy, sections)
    - Content duplication (warning-only)
    - Length bounds (<100KB per response)
    - Performance monitoring (<50ms overhead budget)
    - Template quality metrics
    
    Never blocks production responses (telemetry only).
    """
    
    def __init__(self):
        """Initialize response quality agent."""
        super().__init__(
            agent_name="ResponseQualityAgent",
            agent_id="RQA-001"
        )
        
        # Configuration
        self.max_length = 100 * 1024  # 100KB
        self.max_overhead_ms = 50  # 50ms budget
        self.similarity_threshold = 0.85
        
        # Telemetry storage
        self._metrics_history: List[ResponseMetrics] = []
    
    def validate(self, response: str, metadata: Optional[Dict] = None) -> EnforcementResult:
        """
        Validate response quality (warning-only mode).
        
        Args:
            response: Generated response content
            metadata: Optional metadata (zones, templates, timing)
        
        Returns:
            EnforcementResult with warnings (never blocks)
        """
        start_time = datetime.now()
        violations = []
        metadata = metadata or {}
        
        # Extract metrics
        metrics = self._extract_metrics(response, metadata)
        
        # Validation checks
        violations.extend(self._check_structure(response, metrics))
        violations.extend(self._check_length(metrics))
        violations.extend(self._check_duplication(response, metrics))
        violations.extend(self._check_performance(metrics))
        
        # Store metrics
        self._metrics_history.append(metrics)
        self._trim_history()
        
        # Calculate overhead
        overhead_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Always pass (warning-only mode)
        return EnforcementResult(
            passed=True,  # Never block
            agent_id=self.agent_id,
            severity=self._max_severity(violations),
            violations=[v.message for v in violations],
            metadata={
                "metrics": metrics,
                "overhead_ms": overhead_ms,
                "warning_count": len(violations),
                "mode": "WARNING_ONLY"
            }
        )
    
    def _extract_metrics(self, response: str, metadata: Dict) -> ResponseMetrics:
        """Extract quality metrics from response."""
        # Count headers
        h1_count = len(re.findall(r"^# ", response, re.MULTILINE))
        h2_count = len(re.findall(r"^## ", response, re.MULTILINE))
        h3_count = len(re.findall(r"^### ", response, re.MULTILINE))
        
        # Check hierarchy
        hierarchy_violations = self._check_hierarchy(response)
        
        # Detect duplicates
        duplicate_sections = self._detect_duplicate_sections(response)
        
        return ResponseMetrics(
            length=len(response),
            header_count=h1_count + h2_count + h3_count,
            has_single_h1=(h1_count == 1),
            hierarchy_violations=hierarchy_violations,
            duplicate_sections=duplicate_sections,
            performance_ms=metadata.get("generation_time_ms", 0),
            zones_used=metadata.get("zones_used", 0),
            template_count=metadata.get("template_count", 1)
        )
    
    def _check_structure(self, response: str, metrics: ResponseMetrics) -> List[QualityViolation]:
        """Validate response structure."""
        violations = []
        
        # Check single header
        if not metrics.has_single_h1:
            violations.append(QualityViolation(
                severity=EnforcementSeverity.WARNING,
                rule_id="RQA-STRUCT-001",
                message="Response should have exactly one h1 header",
                suggestion="Use BaseResponseTemplate.header() once per response"
            ))
        
        # Check hierarchy violations
        if metrics.hierarchy_violations:
            violations.append(QualityViolation(
                severity=EnforcementSeverity.WARNING,
                rule_id="RQA-STRUCT-002",
                message=f"Hierarchy violations: {len(metrics.hierarchy_violations)} found",
                location="; ".join(metrics.hierarchy_violations[:3]),
                suggestion="Maintain h1 → h2 → h3 → h4 cascade"
            ))
        
        return violations
    
    def _check_length(self, metrics: ResponseMetrics) -> List[QualityViolation]:
        """Validate response length."""
        violations = []
        
        if metrics.length > self.max_length:
            violations.append(QualityViolation(
                severity=EnforcementSeverity.WARNING,
                rule_id="RQA-LENGTH-001",
                message=f"Response exceeds 100KB limit: {metrics.length} chars",
                suggestion="Consider pagination or summary mode"
            ))
        
        return violations
    
    def _check_duplication(self, response: str, metrics: ResponseMetrics) -> List[QualityViolation]:
        """Detect duplicate content."""
        violations = []
        
        if metrics.duplicate_sections:
            violations.append(QualityViolation(
                severity=EnforcementSeverity.WARNING,
                rule_id="RQA-DUP-001",
                message=f"Potential duplicate sections: {len(metrics.duplicate_sections)}",
                location="; ".join(metrics.duplicate_sections[:3]),
                suggestion="Review content zones for overlap"
            ))
        
        return violations
    
    def _check_performance(self, metrics: ResponseMetrics) -> List[QualityViolation]:
        """Validate performance metrics."""
        violations = []
        
        if metrics.performance_ms > self.max_overhead_ms:
            violations.append(QualityViolation(
                severity=EnforcementSeverity.INFO,
                rule_id="RQA-PERF-001",
                message=f"Response generation took {metrics.performance_ms:.1f}ms (budget: {self.max_overhead_ms}ms)",
                suggestion="Consider template optimization or caching"
            ))
        
        return violations
    
    def _check_hierarchy(self, response: str) -> List[str]:
        """Check for hierarchy violations (h1 → h2 → h3)."""
        violations = []
        lines = response.split("\n")
        prev_level = 0
        
        for i, line in enumerate(lines):
            if match := re.match(r"^(#{1,6}) ", line):
                level = len(match.group(1))
                
                # Check for skipped levels
                if level > prev_level + 1:
                    violations.append(
                        f"Line {i+1}: h{level} after h{prev_level} (skipped levels)"
                    )
                
                prev_level = level
        
        return violations
    
    def _detect_duplicate_sections(self, response: str) -> List[str]:
        """Detect potentially duplicate sections."""
        duplicates = []
        
        # Split by headers
        sections = re.split(r"^##+ ", response, flags=re.MULTILINE)
        
        # Compare sections pairwise
        seen_fingerprints = set()
        for i, section in enumerate(sections[1:], 1):  # Skip preamble
            # Create fingerprint (first 100 chars, normalized)
            normalized = " ".join(section[:100].lower().split())
            fingerprint = normalized
            
            if fingerprint in seen_fingerprints:
                duplicates.append(f"Section {i}")
            else:
                seen_fingerprints.add(fingerprint)
        
        return duplicates
    
    def _max_severity(self, violations: List[QualityViolation]) -> EnforcementSeverity:
        """Get maximum severity from violations."""
        if not violations:
            return EnforcementSeverity.INFO
        
        severity_order = {
            EnforcementSeverity.CRITICAL: 4,
            EnforcementSeverity.WARNING: 3,
            EnforcementSeverity.INFO: 2,
            EnforcementSeverity.SUCCESS: 1
        }
        
        max_sev = max(violations, key=lambda v: severity_order.get(v.severity, 0))
        return max_sev.severity
    
    def _trim_history(self, max_size: int = 1000) -> None:
        """Trim metrics history to prevent memory growth."""
        if len(self._metrics_history) > max_size:
            self._metrics_history = self._metrics_history[-max_size:]
    
    def get_quality_score(self) -> float:
        """
        Calculate template quality score (0-10).
        
        Returns:
            Quality score based on recent metrics
        """
        if not self._metrics_history:
            return 8.5  # Default
        
        # Analyze last 100 responses
        recent = self._metrics_history[-100:]
        
        # Scoring factors
        avg_violations = sum(
            len(m.hierarchy_violations) + len(m.duplicate_sections)
            for m in recent
        ) / len(recent)
        
        single_header_rate = sum(m.has_single_h1 for m in recent) / len(recent)
        avg_performance = sum(m.performance_ms for m in recent) / len(recent)
        
        # Calculate score (0-10)
        score = 10.0
        score -= min(avg_violations * 0.5, 3.0)  # Max -3 for violations
        score -= (1.0 - single_header_rate) * 2.0  # Max -2 for header issues
        score -= min((avg_performance / self.max_overhead_ms) * 1.0, 2.0)  # Max -2 for performance
        
        return max(0.0, min(10.0, score))
    
    def get_telemetry_dashboard(self) -> Dict:
        """Generate telemetry dashboard data."""
        if not self._metrics_history:
            return {"status": "no_data"}
        
        recent = self._metrics_history[-100:]
        
        return {
            "quality_score": self.get_quality_score(),
            "total_responses": len(self._metrics_history),
            "recent_sample": len(recent),
            "avg_length": sum(m.length for m in recent) / len(recent),
            "single_header_rate": sum(m.has_single_h1 for m in recent) / len(recent),
            "avg_violations": sum(
                len(m.hierarchy_violations) + len(m.duplicate_sections)
                for m in recent
            ) / len(recent),
            "avg_performance_ms": sum(m.performance_ms for m in recent) / len(recent),
            "max_overhead_ms": self.max_overhead_ms,
            "mode": "WARNING_ONLY"
        }


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "ResponseQualityAgent",
    "ResponseMetrics",
    "QualityViolation",
]
