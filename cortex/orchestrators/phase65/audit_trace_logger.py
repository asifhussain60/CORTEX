# AC_START: AC-PHASE65-AUDIT-001
# Description: Enhanced audit trace logging for Phase 65 intelligence pipeline
# Author: Asif Hussain
# Date: 2026-02-09
# Phase: 65, Component: Audit Trace

"""
Phase 65 Intelligence Pipeline Audit Trace Logger.

Provides structured audit logging for the complete LENS intelligence pipeline:
- Knowledge synthesis operations (YAML loading, merging, caching)
- LENS analysis operations (AST, git, comments, security, performance)
- Violation detection with severity and remediation
- Guidance generation with rule citations
- Cross-turn intelligence accumulation
- Performance metrics (latency, cache hit rates)

This module extends EnhancedAuditLogger with Phase 65-specific operations
while maintaining backward compatibility with existing AC-ID patterns.

CORE Compliance:
- CORE-027: Audit trail with AC_START/AC_COMPLETE markers
- CORE-030: Implementation Truth validation
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

# ============================================================================
# PHASE 65 AUDIT OPERATION TYPES
# ============================================================================

class Phase65Operation(str, Enum):
    """Phase 65-specific operation types for audit logging."""

    # S1: YAML Best Practice Loading
    YAML_INDEX_PARSE = "YAML_INDEX_PARSE"
    YAML_LOAD = "YAML_LOAD"
    YAML_CACHE_HIT = "YAML_CACHE_HIT"
    YAML_CACHE_MISS = "YAML_CACHE_MISS"
    YAML_LOAD_ERROR = "YAML_LOAD_ERROR"

    # S2: LENS Warmer Operations
    LENS_WARM_START = "LENS_WARM_START"
    LENS_AST_ANALYSIS = "LENS_AST_ANALYSIS"
    LENS_GIT_ANALYSIS = "LENS_GIT_ANALYSIS"
    LENS_COMMENT_ANALYSIS = "LENS_COMMENT_ANALYSIS"
    LENS_SECURITY_CHECK = "LENS_SECURITY_CHECK"
    LENS_PERFORMANCE_CHECK = "LENS_PERFORMANCE_CHECK"
    LENS_WARM_COMPLETE = "LENS_WARM_COMPLETE"

    # S3: Challenge Engine LENS Integration
    CHALLENGE_BUILD_LENS_CONTEXT = "CHALLENGE_BUILD_LENS_CONTEXT"
    CHALLENGE_ANALYZE_SCOPE = "CHALLENGE_ANALYZE_SCOPE"
    CHALLENGE_GENERATE = "CHALLENGE_GENERATE"

    # S4: Unified Intelligence Provider
    INTELLIGENCE_SYNTHESIS_START = "INTELLIGENCE_SYNTHESIS_START"
    INTELLIGENCE_MERGE_RULES = "INTELLIGENCE_MERGE_RULES"
    INTELLIGENCE_DETECT_VIOLATIONS = "INTELLIGENCE_DETECT_VIOLATIONS"
    INTELLIGENCE_GENERATE_GUIDANCE = "INTELLIGENCE_GENERATE_GUIDANCE"
    INTELLIGENCE_SYNTHESIS_COMPLETE = "INTELLIGENCE_SYNTHESIS_COMPLETE"

    # S5: Cross-Turn Accumulation
    INTELLIGENCE_ACCUMULATE = "INTELLIGENCE_ACCUMULATE"
    INTELLIGENCE_CACHE_RESTORE = "INTELLIGENCE_CACHE_RESTORE"
    INTELLIGENCE_CACHE_UPDATE = "INTELLIGENCE_CACHE_UPDATE"

    # S6: CORE-035 Remediation
    DUPLICATE_DETECTION = "DUPLICATE_DETECTION"
    DUPLICATE_CONSOLIDATION = "DUPLICATE_CONSOLIDATION"

    # S8: Integration Testing
    E2E_TEST_START = "E2E_TEST_START"
    E2E_TEST_COMPLETE = "E2E_TEST_COMPLETE"
    E2E_VALIDATION_PASSED = "E2E_VALIDATION_PASSED"
    E2E_VALIDATION_FAILED = "E2E_VALIDATION_FAILED"


# ============================================================================
# PHASE 65 AUDIT TRACE DATA MODELS
# ============================================================================

@dataclass
class YAMLLoadTrace:
    """Audit trace for YAML loading operations."""
    yaml_file: str
    intent_type: str
    load_time_ms: float
    rules_loaded: int
    cache_hit: bool
    error: Optional[str] = None


@dataclass
class LENSAnalysisTrace:
    """Audit trace for LENS analysis operations."""
    file_path: str
    analysis_type: str  # "ast", "git", "comments", "security", "performance"
    analysis_time_ms: float
    findings_count: int
    severity: Optional[str] = None  # For security/performance checks
    cache_hit: bool = False


@dataclass
class ViolationTrace:
    """Audit trace for violation detection."""
    violation_type: str
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    rule_id: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    remediation: Optional[str] = None


@dataclass
class IntelligenceSynthesisTrace:
    """Audit trace for complete intelligence synthesis operation."""
    ac_id: str
    intent_type: str
    file_path: Optional[str]
    start_time: float
    end_time: float
    duration_ms: float

    # Knowledge sources
    cortex_rules_loaded: int
    company_rules_loaded: int
    lens_analyses: List[str] = field(default_factory=list)

    # Synthesis results
    merged_rules_count: int = 0
    violations_detected: int = 0
    guidance_generated: int = 0
    citations_count: int = 0

    # Performance
    cache_hits: int = 0
    cache_misses: int = 0

    # Outcome
    success: bool = True
    errors: List[str] = field(default_factory=list)


@dataclass
class CrossTurnAccumulationTrace:
    """Audit trace for cross-turn intelligence accumulation."""
    session_id: str
    turn_number: int
    file_path: str
    previous_context_restored: bool
    new_intelligence_added: bool
    accumulated_analyses: List[str] = field(default_factory=list)
    cache_size_bytes: int = 0


# ============================================================================
# PHASE 65 AUDIT TRACE LOGGER
# ============================================================================

class Phase65AuditTraceLogger:
    """
    Enhanced audit trace logger for Phase 65 intelligence pipeline.

    Provides structured logging with performance metrics, violation tracking,
    and cross-turn accumulation history.

    Example:
        >>> logger = Phase65AuditTraceLogger()
        >>>
        >>> # Log YAML loading
        >>> trace = YAMLLoadTrace(
        ...     yaml_file="tdd-best-practices.yaml",
        ...     intent_type="IMPLEMENT",
        ...     load_time_ms=12.5,
        ...     rules_loaded=15,
        ...     cache_hit=False
        ... )
        >>> logger.log_yaml_load(trace)
        >>>
        >>> # Log intelligence synthesis
        >>> synthesis_trace = IntelligenceSynthesisTrace(
        ...     ac_id="AC-PHASE65-001",
        ...     intent_type="IMPLEMENT",
        ...     file_path="/src/auth.py",
        ...     start_time=time.time(),
        ...     end_time=time.time() + 0.245,
        ...     duration_ms=245.0,
        ...     cortex_rules_loaded=35,
        ...     company_rules_loaded=5,
        ...     merged_rules_count=40,
        ...     violations_detected=2,
        ...     guidance_generated=8
        ... )
        >>> logger.log_intelligence_synthesis(synthesis_trace)
    """

    def __init__(self):
        """Initialize Phase 65 audit trace logger."""
        self.base_logger = EnhancedAuditLogger.instance()
        self.session_start = time.time()

        # Performance tracking
        self.yaml_load_times: List[float] = []
        self.lens_analysis_times: List[float] = []
        self.synthesis_times: List[float] = []

        # Cache metrics
        self.cache_stats = {
            "yaml_hits": 0,
            "yaml_misses": 0,
            "lens_hits": 0,
            "lens_misses": 0,
            "intelligence_hits": 0,
            "intelligence_misses": 0
        }

        # Violation tracking
        self.violations_by_severity: Dict[str, int] = {
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0
        }

        # Cross-turn tracking
        self.turn_history: List[CrossTurnAccumulationTrace] = []

    # ========================================================================
    # S1: YAML LOADING OPERATIONS
    # ========================================================================

    def log_yaml_load(self, trace: YAMLLoadTrace) -> None:
        """
        Log YAML file loading operation.

        Args:
            trace: YAMLLoadTrace with load details
        """
        self.yaml_load_times.append(trace.load_time_ms)

        if trace.cache_hit:
            self.cache_stats["yaml_hits"] += 1
        else:
            self.cache_stats["yaml_misses"] += 1

        operation = (
            Phase65Operation.YAML_CACHE_HIT if trace.cache_hit
            else Phase65Operation.YAML_LOAD
        )

        self.base_logger.log_operation_complete(
            ac_id="AC-PHASE65-S1-YAML",
            operation=operation.value,
            success=trace.error is None,
            details={
                "yaml_file": trace.yaml_file,
                "intent_type": trace.intent_type,
                "load_time_ms": trace.load_time_ms,
                "rules_loaded": trace.rules_loaded,
                "cache_hit": trace.cache_hit,
                "error": trace.error
            }
        )

    def log_yaml_load_error(
        self,
        yaml_file: str,
        intent_type: str,
        error: str
    ) -> None:
        """
        Log YAML loading error.

        Args:
            yaml_file: YAML file that failed to load
            intent_type: Intent type attempted
            error: Error message
        """
        self.base_logger.log_operation_complete(
            ac_id="AC-PHASE65-S1-ERROR",
            operation=Phase65Operation.YAML_LOAD_ERROR.value,
            success=False,
            details={
                "yaml_file": yaml_file,
                "intent_type": intent_type,
                "error": error
            }
        )

    # ========================================================================
    # S2: LENS ANALYSIS OPERATIONS
    # ========================================================================

    def log_lens_analysis(self, trace: LENSAnalysisTrace) -> None:
        """
        Log LENS analysis operation.

        Args:
            trace: LENSAnalysisTrace with analysis details
        """
        self.lens_analysis_times.append(trace.analysis_time_ms)

        if trace.cache_hit:
            self.cache_stats["lens_hits"] += 1
        else:
            self.cache_stats["lens_misses"] += 1

        # Map analysis type to operation
        operation_map = {
            "ast": Phase65Operation.LENS_AST_ANALYSIS,
            "git": Phase65Operation.LENS_GIT_ANALYSIS,
            "comments": Phase65Operation.LENS_COMMENT_ANALYSIS,
            "security": Phase65Operation.LENS_SECURITY_CHECK,
            "performance": Phase65Operation.LENS_PERFORMANCE_CHECK
        }

        operation = operation_map.get(
            trace.analysis_type,
            Phase65Operation.LENS_WARM_COMPLETE
        )

        self.base_logger.log_operation_complete(
            ac_id=f"AC-PHASE65-S2-LENS-{trace.analysis_type.upper()}",
            operation=operation.value,
            success=True,
            details={
                "file_path": trace.file_path,
                "analysis_type": trace.analysis_type,
                "analysis_time_ms": trace.analysis_time_ms,
                "findings_count": trace.findings_count,
                "severity": trace.severity,
                "cache_hit": trace.cache_hit
            }
        )

    # ========================================================================
    # S4: INTELLIGENCE SYNTHESIS OPERATIONS
    # ========================================================================

    def log_intelligence_synthesis(
        self,
        trace: IntelligenceSynthesisTrace
    ) -> None:
        """
        Log complete intelligence synthesis operation.

        Args:
            trace: IntelligenceSynthesisTrace with synthesis details
        """
        self.synthesis_times.append(trace.duration_ms)

        self.cache_stats["intelligence_hits"] += trace.cache_hits
        self.cache_stats["intelligence_misses"] += trace.cache_misses

        self.base_logger.log_operation_complete(
            ac_id=trace.ac_id,
            operation=Phase65Operation.INTELLIGENCE_SYNTHESIS_COMPLETE.value,
            success=trace.success,
            details={
                "intent_type": trace.intent_type,
                "file_path": trace.file_path,
                "duration_ms": trace.duration_ms,
                "cortex_rules_loaded": trace.cortex_rules_loaded,
                "company_rules_loaded": trace.company_rules_loaded,
                "lens_analyses": trace.lens_analyses,
                "merged_rules_count": trace.merged_rules_count,
                "violations_detected": trace.violations_detected,
                "guidance_generated": trace.guidance_generated,
                "citations_count": trace.citations_count,
                "cache_hits": trace.cache_hits,
                "cache_misses": trace.cache_misses,
                "errors": trace.errors
            }
        )

    def log_violation(self, trace: ViolationTrace) -> None:
        """
        Log violation detection.

        Args:
            trace: ViolationTrace with violation details
        """
        self.violations_by_severity[trace.severity] += 1

        self.base_logger.log_operation_complete(
            ac_id="AC-PHASE65-S4-VIOLATION",
            operation=Phase65Operation.INTELLIGENCE_DETECT_VIOLATIONS.value,
            success=True,
            details={
                "violation_type": trace.violation_type,
                "severity": trace.severity,
                "rule_id": trace.rule_id,
                "description": trace.description,
                "file_path": trace.file_path,
                "line_number": trace.line_number,
                "remediation": trace.remediation
            }
        )

    # ========================================================================
    # S5: CROSS-TURN ACCUMULATION OPERATIONS
    # ========================================================================

    def log_cross_turn_accumulation(
        self,
        trace: CrossTurnAccumulationTrace
    ) -> None:
        """
        Log cross-turn intelligence accumulation.

        Args:
            trace: CrossTurnAccumulationTrace with accumulation details
        """
        self.turn_history.append(trace)

        self.base_logger.log_operation_complete(
            ac_id=f"AC-PHASE65-S5-TURN-{trace.turn_number}",
            operation=Phase65Operation.INTELLIGENCE_ACCUMULATE.value,
            success=True,
            details={
                "session_id": trace.session_id,
                "turn_number": trace.turn_number,
                "file_path": trace.file_path,
                "previous_context_restored": trace.previous_context_restored,
                "new_intelligence_added": trace.new_intelligence_added,
                "accumulated_analyses": trace.accumulated_analyses,
                "cache_size_bytes": trace.cache_size_bytes
            }
        )

    # ========================================================================
    # PERFORMANCE METRICS & REPORTING
    # ========================================================================

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary for all Phase 65 operations.

        Returns:
            Dict with performance metrics:
            - avg_yaml_load_ms: Average YAML load time
            - avg_lens_analysis_ms: Average LENS analysis time
            - avg_synthesis_ms: Average synthesis time
            - cache_hit_rate: Overall cache hit rate
            - violations_by_severity: Violation counts by severity
        """
        def avg(times: List[float]) -> float:
            return sum(times) / len(times) if times else 0.0

        total_hits = sum(
            v for k, v in self.cache_stats.items() if k.endswith("_hits")
        )
        total_misses = sum(
            v for k, v in self.cache_stats.items() if k.endswith("_misses")
        )
        total_cache_ops = total_hits + total_misses
        cache_hit_rate = (
            total_hits / total_cache_ops if total_cache_ops > 0 else 0.0
        )

        return {
            "avg_yaml_load_ms": avg(self.yaml_load_times),
            "avg_lens_analysis_ms": avg(self.lens_analysis_times),
            "avg_synthesis_ms": avg(self.synthesis_times),
            "cache_hit_rate": cache_hit_rate,
            "cache_stats": self.cache_stats,
            "violations_by_severity": self.violations_by_severity,
            "total_turns": len(self.turn_history),
            "session_duration_seconds": time.time() - self.session_start
        }

    def generate_audit_report(self) -> str:
        """
        Generate human-readable audit report.

        Returns:
            Formatted audit report string
        """
        summary = self.get_performance_summary()

        report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 PHASE 65 INTELLIGENCE PIPELINE AUDIT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  PERFORMANCE METRICS
   • YAML Loading: {summary['avg_yaml_load_ms']:.1f}ms avg
   • LENS Analysis: {summary['avg_lens_analysis_ms']:.1f}ms avg
   • Synthesis: {summary['avg_synthesis_ms']:.1f}ms avg

💾 CACHE EFFICIENCY
   • Hit Rate: {summary['cache_hit_rate']:.1%}
   • YAML: {summary['cache_stats']['yaml_hits']} hits / {summary['cache_stats']['yaml_misses']} misses
   • LENS: {summary['cache_stats']['lens_hits']} hits / {summary['cache_stats']['lens_misses']} misses
   • Intelligence: {summary['cache_stats']['intelligence_hits']} hits / {summary['cache_stats']['intelligence_misses']} misses

⚠️  VIOLATIONS DETECTED
   • CRITICAL: {summary['violations_by_severity']['CRITICAL']}
   • ERROR: {summary['violations_by_severity']['ERROR']}
   • WARNING: {summary['violations_by_severity']['WARNING']}
   • INFO: {summary['violations_by_severity']['INFO']}

🔄 CROSS-TURN ACCUMULATION
   • Total Turns: {summary['total_turns']}
   • Session Duration: {summary['session_duration_seconds']:.1f}s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        return report.strip()


# ============================================================================
# GLOBAL INSTANCE (Singleton Pattern)
# ============================================================================

_phase65_logger_instance: Optional[Phase65AuditTraceLogger] = None


def get_phase65_audit_logger() -> Phase65AuditTraceLogger:
    """
    Get or create singleton Phase65AuditTraceLogger instance.

    Returns:
        Phase65AuditTraceLogger singleton instance
    """
    global _phase65_logger_instance
    if _phase65_logger_instance is None:
        _phase65_logger_instance = Phase65AuditTraceLogger()
    return _phase65_logger_instance


# AC_COMPLETE: AC-PHASE65-AUDIT-001 ✅ Enhanced audit trace logging for intelligence pipeline
