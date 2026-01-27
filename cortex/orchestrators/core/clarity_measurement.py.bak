"""
Clarity Measurement System - Scope C Implementation

AC-ID: AC-PLANNING-REFINE-QC-001 - Clarity Measurement (Scope C)
CORE-008: TDD (tests before implementation)

Measures DoR clarity through:
1. CORTEX heuristic analysis (question-answer quality, detail completeness)
2. User confirmation ("yes, plan is clear")
3. Combined score: (heuristic_score * 0.6) + (user_confidence * 0.4)

Tests: test_clarity_measurement.py
- test_heuristic_clarity_measurement
- test_combined_clarity_score
- test_dor_threshold_detection
"""

from __future__ import annotations

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json


class ClarityComponent(Enum):
    """Components contributing to clarity measurement."""
    REQUIREMENTS_DEFINED = "requirements_defined"  # Requirements fully specified
    SCOPE_DEFINED = "scope_defined"  # Scope boundaries clear
    CONSTRAINTS_EXPLICIT = "constraints_explicit"  # Constraints documented
    TIMELINE_CLEAR = "timeline_clear"  # Timeline defined
    ACCEPTANCE_CRITERIA = "acceptance_criteria"  # ACs documented
    RISKS_IDENTIFIED = "risks_identified"  # Known risks
    DEPENDENCIES_MAPPED = "dependencies_mapped"  # Dependencies clear
    QUESTIONS_ANSWERED = "questions_answered"  # All key questions answered


@dataclass
class ClarityComponentScore:
    """Score for single clarity component."""
    component: ClarityComponent
    score: float  # 0.0 - 1.0
    evidence: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ClarityMeasurement:
    """Complete clarity measurement for a plan."""
    turn_number: int
    heuristic_score: float  # 0.0 - 1.0 (CORTEX analysis)
    user_confidence: float  # 0.0 - 1.0 (User explicit confirmation, -1 if not provided)
    combined_score: float  # Overall clarity
    threshold: float = 0.95
    dor_achieved: bool = False
    components: List[ClarityComponentScore] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def is_above_threshold(self) -> bool:
        """Check if clarity >= threshold."""
        return self.combined_score >= self.threshold


class ClarityMeasurer:
    """Measures plan clarity through heuristic + user confirmation."""
    
    def __init__(self, threshold: float = 0.95) -> None:
        """Initialize clarity measurer.
        
        Args:
            threshold: Clarity threshold for DoR achievement (default 0.95)
        
        AC-PLANNING-REFINE-QC-001: Clarity measurement
        """
        self.threshold = threshold
        self.measurement_history: List[ClarityMeasurement] = []
        self._component_weights: Dict[ClarityComponent, float] = {
            ClarityComponent.REQUIREMENTS_DEFINED: 0.15,
            ClarityComponent.SCOPE_DEFINED: 0.15,
            ClarityComponent.CONSTRAINTS_EXPLICIT: 0.10,
            ClarityComponent.TIMELINE_CLEAR: 0.10,
            ClarityComponent.ACCEPTANCE_CRITERIA: 0.15,
            ClarityComponent.RISKS_IDENTIFIED: 0.10,
            ClarityComponent.DEPENDENCIES_MAPPED: 0.10,
            ClarityComponent.QUESTIONS_ANSWERED: 0.15,
        }
    
    def measure_heuristic(self, plan_context: Dict[str, Any]) -> float:
        """
        Measure clarity using CORTEX heuristic analysis.
        
        Analyzes:
        - Requirements completeness (are they specific, measurable?)
        - Scope boundaries (are edges defined?)
        - Constraints (are they explicit?)
        - Timeline (is it realistic given scope?)
        - Acceptance criteria (are ACs clear?)
        - Risks (are known risks documented?)
        - Dependencies (are they mapped?)
        - Questions (have user questions been answered?)
        
        Args:
            plan_context: Plan details including:
                - requirements: List of requirements
                - scope: Scope description
                - constraints: Known constraints
                - timeline: Timeline definition
                - acceptance_criteria: List of ACs
                - known_risks: List of identified risks
                - dependencies: List of dependencies
                - user_questions: List of user questions asked
                - user_answers: List of user answers provided
        
        Returns:
            Heuristic clarity score (0.0 - 1.0)
        
        AC-PLANNING-REFINE-QC-001: Heuristic analysis
        """
        component_scores = {}
        
        # Requirements defined
        requirements = plan_context.get("requirements", [])
        if len(requirements) > 0:
            # Score based on specificity
            avg_requirement_length = sum(len(str(r)) for r in requirements) / len(requirements) if requirements else 0
            specificity_score = min(1.0, avg_requirement_length / 100)  # Longer = more specific
            component_scores[ClarityComponent.REQUIREMENTS_DEFINED] = specificity_score
        else:
            component_scores[ClarityComponent.REQUIREMENTS_DEFINED] = 0.0
        
        # Scope defined
        scope = plan_context.get("scope", "")
        if scope and len(scope) > 20:
            component_scores[ClarityComponent.SCOPE_DEFINED] = min(1.0, len(scope) / 200)
        else:
            component_scores[ClarityComponent.SCOPE_DEFINED] = 0.3 if scope else 0.0
        
        # Constraints explicit
        constraints = plan_context.get("constraints", [])
        component_scores[ClarityComponent.CONSTRAINTS_EXPLICIT] = min(1.0, len(constraints) * 0.2)
        
        # Timeline clear
        timeline = plan_context.get("timeline", "")
        if timeline:
            # Check if timeline has specific dates/durations
            has_dates = any(c.isdigit() for c in timeline)
            component_scores[ClarityComponent.TIMELINE_CLEAR] = 0.8 if has_dates else 0.5
        else:
            component_scores[ClarityComponent.TIMELINE_CLEAR] = 0.0
        
        # Acceptance criteria
        acs = plan_context.get("acceptance_criteria", [])
        component_scores[ClarityComponent.ACCEPTANCE_CRITERIA] = min(1.0, len(acs) * 0.15)
        
        # Risks identified
        risks = plan_context.get("known_risks", [])
        component_scores[ClarityComponent.RISKS_IDENTIFIED] = min(1.0, len(risks) * 0.2)
        
        # Dependencies mapped
        dependencies = plan_context.get("dependencies", [])
        component_scores[ClarityComponent.DEPENDENCIES_MAPPED] = min(1.0, len(dependencies) * 0.15)
        
        # Questions answered
        questions = plan_context.get("user_questions", [])
        answers = plan_context.get("user_answers", [])
        if questions:
            answer_ratio = len(answers) / len(questions)
            component_scores[ClarityComponent.QUESTIONS_ANSWERED] = answer_ratio
        else:
            component_scores[ClarityComponent.QUESTIONS_ANSWERED] = 0.8  # No questions = clear
        
        # Calculate weighted score
        heuristic_score = 0.0
        for component, score in component_scores.items():
            weight = self._component_weights.get(component, 0.0)
            heuristic_score += score * weight
        
        return min(1.0, heuristic_score)
    
    def measure_user_confirmation(self, user_response: Optional[str]) -> float:
        """
        Measure user confidence from explicit confirmation.
        
        Scope C: CORTEX suggests ready, user confirms.
        
        Args:
            user_response: User's explicit response to CORTEX suggestion
                - "yes" / "approve" / "ready" → 1.0
                - "mostly" / "almost" → 0.7-0.8
                - "no" / "not_ready" / None → 0.0
        
        Returns:
            User confidence score (0.0 - 1.0), or -1 if not provided
        
        AC-PLANNING-REFINE-QC-001: User confirmation
        """
        if user_response is None:
            return -1.0  # Not provided yet
        
        response_lower = str(user_response).lower().strip()
        
        if any(word in response_lower for word in ["yes", "approve", "ready", "confirmed", "confirmed", "okay"]):
            return 1.0
        elif any(word in response_lower for word in ["mostly", "almost", "close", "nearly"]):
            return 0.75
        elif any(word in response_lower for word in ["no", "not", "not_ready", "wait", "unclear"]):
            return 0.0
        else:
            # Neutral/unclear response
            return 0.5
    
    def measure_combined(
        self,
        plan_context: Dict[str, Any],
        user_response: Optional[str] = None,
        turn_number: int = 1,
    ) -> ClarityMeasurement:
        """
        Measure combined clarity (heuristic + user confirmation).
        
        Scope C: CORTEX heuristic (60%) + user confirmation (40%)
        
        Args:
            plan_context: Plan details for heuristic analysis
            user_response: User's explicit confirmation response
            turn_number: Which turn of refinement this is
        
        Returns:
            Complete ClarityMeasurement with:
            - heuristic_score (CORTEX analysis): 0.0-1.0
            - user_confidence (user confirmation): -1 (not yet) or 0.0-1.0
            - combined_score (weighted): 0.0-1.0
            - dor_achieved: True if >= threshold
        
        AC-PLANNING-REFINE-QC-001: Combined measurement
        """
        # Measure heuristic
        heuristic = self.measure_heuristic(plan_context)
        
        # Measure user confirmation
        user_conf = self.measure_user_confirmation(user_response)
        
        # Calculate combined score
        if user_conf < 0:
            # User hasn't confirmed yet - use heuristic only
            combined = heuristic
        else:
            # Both available - weighted combination
            combined = (heuristic * 0.6) + (user_conf * 0.4)
        
        # Determine if DoR achieved
        dor_achieved = combined >= self.threshold
        
        # Create measurement
        measurement = ClarityMeasurement(
            turn_number=turn_number,
            heuristic_score=heuristic,
            user_confidence=user_conf,
            combined_score=combined,
            threshold=self.threshold,
            dor_achieved=dor_achieved,
        )
        
        # Store in history
        self.measurement_history.append(measurement)
        
        return measurement
    
    def get_cortex_suggestion(self, measurement: ClarityMeasurement) -> str:
        """
        Generate CORTEX suggestion based on clarity measurement.
        
        Scope C: CORTEX suggests readiness to user.
        
        Args:
            measurement: Clarity measurement result
        
        Returns:
            CORTEX suggestion for user
        
        AC-PLANNING-REFINE-QC-001: CORTEX suggestion
        """
        if measurement.combined_score >= 0.95:
            return "PLAN_READY: Plan has reached 100% clarity. Ready to proceed?"
        elif measurement.combined_score >= 0.85:
            return "PLAN_MOSTLY_READY: Plan is 85% clear. Any remaining questions?"
        elif measurement.combined_score >= 0.70:
            return "PLAN_PARTIALLY_CLEAR: Plan is 70% clear. Need more clarification on:"
        else:
            return "PLAN_NEEDS_WORK: Plan needs further refinement. Please provide more details on:"
    
    def get_clarity_gap_analysis(self, measurement: ClarityMeasurement) -> Dict[str, Any]:
        """
        Analyze what's missing for full clarity.
        
        Args:
            measurement: Clarity measurement
        
        Returns:
            Analysis of gaps preventing 100% clarity
        """
        gap_threshold = 0.8
        gaps = []
        
        for component in measurement.components:
            if component.score < gap_threshold:
                gaps.append({
                    "component": component.component.value,
                    "current_score": component.score,
                    "target_score": gap_threshold,
                    "gap": gap_threshold - component.score,
                    "evidence": component.evidence,
                })
        
        return {
            "total_gaps": len(gaps),
            "gaps": sorted(gaps, key=lambda x: x["gap"], reverse=True),
            "recommendation": f"Address {len(gaps)} gaps to reach 100% clarity"
        }
    
    def get_measurement_history(self) -> List[Dict[str, Any]]:
        """Get complete measurement history as dictionaries."""
        return [
            {
                "turn": m.turn_number,
                "heuristic": round(m.heuristic_score, 3),
                "user_confidence": round(m.user_confidence, 3) if m.user_confidence >= 0 else "not_yet",
                "combined": round(m.combined_score, 3),
                "dor_achieved": m.dor_achieved,
                "timestamp": m.timestamp,
            }
            for m in self.measurement_history
        ]
    
    def estimate_next_clarity(self, current_measurement: ClarityMeasurement) -> float:
        """
        Estimate clarity after next refinement turn.
        
        Simple heuristic: if user is engaged, expect ~0.15 improvement per turn.
        
        Args:
            current_measurement: Current clarity measurement
        
        Returns:
            Estimated clarity score for next turn
        """
        if current_measurement.user_confidence >= 0:
            # User is engaged - expect good progress
            improvement = 0.15
        else:
            # User hasn't confirmed yet - expect modest progress
            improvement = 0.10
        
        estimated = min(1.0, current_measurement.combined_score + improvement)
        return estimated


# Convenience singleton
_clarity_measurer_instance: Optional[ClarityMeasurer] = None


def get_clarity_measurer(threshold: float = 0.95) -> ClarityMeasurer:
    """Get or create clarity measurer singleton.
    
    Args:
        threshold: Clarity threshold (default 0.95)
    
    Returns:
        ClarityMeasurer instance
    """
    global _clarity_measurer_instance
    if _clarity_measurer_instance is None:
        _clarity_measurer_instance = ClarityMeasurer(threshold=threshold)
    return _clarity_measurer_instance
