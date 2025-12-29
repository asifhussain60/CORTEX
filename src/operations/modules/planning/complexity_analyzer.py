"""
Complexity Analyzer - Single vs Multi-Phase Format Selection
============================================================

Analyzes plan complexity to determine format:
- Single-phase: Master plan only (simple features)
- Multi-phase: Master plan + worker plans (complex features)

Decision Criteria:
- Phase count: <3 phases → single, ≥3 phases → multi
- Task count: <10 tasks → single, ≥10 tasks → multi
- Duration: <1 week → single, ≥1 week → multi

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from src.operations.modules.orchestration.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


@dataclass
class ComplexityAnalysis:
    """Result of complexity analysis."""
    is_single_phase: bool
    phase_count: int
    task_count: int
    estimated_days: float
    format_recommendation: str  # "single" or "multi-phase"
    rationale: str  # One-sentence explanation
    complexity_score: float  # 0-100


class ComplexityAnalyzer:
    """
    Analyzes plan complexity to determine format.
    
    Thresholds:
    - Single-phase: 1-2 phases, <10 tasks, <5 days
    - Multi-phase: 3+ phases, ≥10 tasks, ≥5 days
    """
    
    # Thresholds
    SINGLE_PHASE_THRESHOLD = 2
    SINGLE_TASK_THRESHOLD = 10
    SINGLE_DURATION_THRESHOLD = 5  # days
    
    def analyze(self, plan_data: Dict[str, Any]) -> ComplexityAnalysis:
        """
        Analyze plan complexity.
        
        Args:
            plan_data: Plan dictionary with phases, tasks, metadata
            
        Returns:
            ComplexityAnalysis result
        """
        logger.info("🔍 Analyzing plan complexity")
        
        # Extract metrics
        phases = plan_data.get("phases", [])
        phase_count = len(phases)
        
        # Count total tasks
        task_count = 0
        for phase in phases:
            task_count += len(phase.get("tasks", []))
        
        # Estimate duration
        estimated_days = 0.0
        for phase in phases:
            estimated = phase.get("estimated", "0h")
            # Parse estimated time (e.g., "2h", "3d")
            days = self._parse_duration(estimated)
            estimated_days += days
        
        # Calculate complexity score (0-100)
        complexity_score = self._calculate_complexity_score(
            phase_count, task_count, estimated_days
        )
        
        # Determine format
        is_single_phase = (
            phase_count <= self.SINGLE_PHASE_THRESHOLD and
            task_count < self.SINGLE_TASK_THRESHOLD and
            estimated_days < self.SINGLE_DURATION_THRESHOLD
        )
        
        format_recommendation = "single" if is_single_phase else "multi-phase"
        
        # Generate rationale
        if is_single_phase:
            rationale = f"Simple feature: {phase_count} phases, {task_count} tasks, {estimated_days:.1f} days"
        else:
            rationale = f"Complex feature: {phase_count} phases, {task_count} tasks, {estimated_days:.1f} days"
        
        logger.info(f"✅ Complexity analysis: {format_recommendation} (score: {complexity_score:.0f})")
        
        result = ComplexityAnalysis(
            is_single_phase=is_single_phase,
            phase_count=phase_count,
            task_count=task_count,
            estimated_days=estimated_days,
            format_recommendation=format_recommendation,
            rationale=rationale,
            complexity_score=complexity_score
        )
        
        # Audit: Complexity analyzed
        plan_id = plan_data.get("plan_id", "unknown")
        session_id = plan_data.get("session_id", "unknown")
        audit_logger.log_event(
            event_type="complexity_analyzed",
            session_id=session_id,
            plan_id=plan_id,
            orchestrator="ComplexityAnalyzer",
            phase="analysis",
            metadata={
                "is_single_phase": is_single_phase,
                "phase_count": phase_count,
                "task_count": task_count,
                "estimated_days": estimated_days,
                "complexity_score": complexity_score,
                "format_recommendation": format_recommendation
            }
        )
        
        return result
    
    def _parse_duration(self, duration_str: str) -> float:
        """
        Parse duration string to days.
        
        Args:
            duration_str: Duration string (e.g., "2h", "3d", "1w")
            
        Returns:
            Duration in days
        """
        duration_str = duration_str.lower().strip()
        
        # Extract number
        num_str = ""
        for char in duration_str:
            if char.isdigit() or char == '.':
                num_str += char
        
        if not num_str:
            return 0.0
        
        num = float(num_str)
        
        # Parse unit
        if 'h' in duration_str:
            return num / 8  # 8-hour days
        elif 'd' in duration_str:
            return num
        elif 'w' in duration_str:
            return num * 5  # 5-day weeks
        else:
            return num  # Assume days
    
    def _calculate_complexity_score(
        self,
        phase_count: int,
        task_count: int,
        estimated_days: float
    ) -> float:
        """
        Calculate complexity score (0-100).
        
        Args:
            phase_count: Number of phases
            task_count: Total task count
            estimated_days: Estimated duration in days
            
        Returns:
            Complexity score (0-100)
        """
        # Weighted scoring
        phase_weight = 0.3
        task_weight = 0.4
        duration_weight = 0.3
        
        # Normalize each metric (0-100)
        phase_score = min(100, (phase_count / 5) * 100)  # 5 phases = 100
        task_score = min(100, (task_count / 20) * 100)  # 20 tasks = 100
        duration_score = min(100, (estimated_days / 10) * 100)  # 10 days = 100
        
        # Weighted average
        complexity_score = (
            phase_score * phase_weight +
            task_score * task_weight +
            duration_score * duration_weight
        )
        
        return complexity_score
