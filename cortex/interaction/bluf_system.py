"""Adaptive BLUF Communication System - Phase 13 Implementation.

BLUF = Bottom Line Up Front

Three response formats with progressive disclosure:
1. BLUF_ONLY: Executive summary, one paragraph
2. HYBRID: BLUF + essential details  
3. FULL_DETAIL: Complete analysis with all context
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for operations."""
    LOW = "low"          # No code modification
    MEDIUM = "medium"    # Reversible changes
    HIGH = "high"        # Irreversible changes


class ComplexityLevel(Enum):
    """Complexity score (1-13) mapping."""
    TRIVIAL = 1           # Doc updates
    VERY_SIMPLE = 2       # Config changes
    SIMPLE = 3            # Single file fixes
    MODERATE = 4          # Multi-file changes
    COMPLEX = 5           # Moderate refactoring
    VERY_COMPLEX = 6      # Significant changes
    HIGHLY_COMPLEX = 7    # Major refactoring
    EXTREME = 8           # System-wide impact
    CRITICAL = 9          # High uncertainty
    SYSTEM_CRITICAL = 10  # Multiple systems affected
    ARCHITECTURAL = 11    # Architecture changes
    TRANSFORMATIONAL = 12 # Business-model level
    UNKNOWN = 13          # Completely unknown


class ResponseFormat(Enum):
    """Response formats."""
    BLUF_ONLY = "bluf_only"        # Executive summary only
    HYBRID = "hybrid"              # Summary + essentials
    FULL_DETAIL = "full_detail"    # Complete analysis


class UserPreferenceMode(Enum):
    """User preference modes."""
    EXECUTIVE = "executive"        # Prefers BLUF
    TECHNICAL = "technical"        # Prefers details
    BALANCED = "balanced"          # Wants summary + essentials
    ADAPTIVE = "adaptive"          # System decides


@dataclass
class OperationContext:
    """Context for operation analysis.
    
    Attributes:
        operation_type: Type of operation (IMPLEMENT, FIX, REFACTOR, etc.)
        description: Operation description
        files_affected: Number of files affected
        services_affected: Number of services affected
        reversible: Can operation be easily reversed
        has_dependencies: Has complex dependencies
    """
    operation_type: str
    description: str
    files_affected: int = 0
    services_affected: int = 0
    reversible: bool = True
    has_dependencies: bool = False


@dataclass
class ResponseMetadata:
    """Metadata about response format selection.
    
    Attributes:
        risk_level: Assessed risk level
        complexity_score: Complexity (1-13)
        recommended_format: Recommended format
        rationale: Why this format
    """
    risk_level: RiskLevel
    complexity_score: int
    recommended_format: ResponseFormat
    rationale: str


class ResponseFormatAnalyzer:
    """Phase 13 BLUF-1: Response Format Analyzer.
    
    Classifies operations by:
    - Risk level (LOW/MEDIUM/HIGH)
    - Complexity score (1-13)
    
    Risk Matrix:
    - LOW: ANALYZE, DOCUMENT, READ (no modification)
    - MEDIUM: REFACTOR, TEST, CONFIG (reversible)
    - HIGH: IMPLEMENT, FIX, DEPLOY, DELETE (irreversible)
    
    Complexity factors:
    - Scope: single file (1-3), multi-file (4-6), system (7-9), unknown (10-13)
    - Dependencies: simple (↓2), moderate (→0), complex (↑2)
    - Reversibility: fully reversible (↓1), partially (→0), not reversible (↑1)
    
    AC-BLUF-1-01: Classify operation risk correctly
    AC-BLUF-1-02: Score complexity 1-13
    AC-BLUF-1-03: Select appropriate format
    AC-BLUF-1-04: Explain format rationale
    """
    
    RISK_MATRIX = {
        "ANALYZE": RiskLevel.LOW,
        "DOCUMENT": RiskLevel.LOW,
        "READ": RiskLevel.LOW,
        "REFACTOR": RiskLevel.MEDIUM,
        "TEST": RiskLevel.MEDIUM,
        "CONFIG": RiskLevel.MEDIUM,
        "IMPLEMENT": RiskLevel.HIGH,
        "FIX": RiskLevel.HIGH,
        "DEPLOY": RiskLevel.HIGH,
        "DELETE": RiskLevel.HIGH,
    }
    
    def classify_risk(self, context: OperationContext) -> RiskLevel:
        """Classify operation risk level.
        
        Phase 13 AC-BLUF-1-01: Classify operation risk correctly
        
        Args:
            context: Operation context
            
        Returns:
            Risk level classification
        """
        op_type = context.operation_type.upper()
        
        # Use risk matrix if operation type known
        if op_type in self.RISK_MATRIX:
            return self.RISK_MATRIX[op_type]
        
        # Default to HIGH if reversible is false
        if not context.reversible:
            return RiskLevel.HIGH
        
        # Default to MEDIUM otherwise
        return RiskLevel.MEDIUM
    
    def score_complexity(self, context: OperationContext) -> int:
        """Score complexity on 1-13 scale.
        
        Phase 13 AC-BLUF-1-02: Score complexity 1-13
        
        Args:
            context: Operation context
            
        Returns:
            Complexity score (1-13)
        """
        score = 0
        
        # Base score from file count
        if context.files_affected == 0:
            score = 1  # Trivial
        elif context.files_affected <= 1:
            score = 3  # Simple
        elif context.files_affected <= 5:
            score = 5  # Moderate
        elif context.files_affected <= 20:
            score = 8  # Complex
        else:
            score = 11  # Highly complex
        
        # Adjust for services affected
        if context.services_affected > 0:
            score += min(2, context.services_affected)  # Up to +2
        
        # Adjust for dependencies
        if context.has_dependencies:
            score += 1
        
        # Adjust for reversibility
        if not context.reversible:
            score += 1
        
        # Clamp to 1-13
        return max(1, min(13, score))
    
    def analyze_operation(self, context: OperationContext) -> ResponseMetadata:
        """Analyze operation for format selection.
        
        Phase 13 AC-BLUF-1-04: Explain format rationale
        
        Args:
            context: Operation context
            
        Returns:
            Response metadata with recommendations
        """
        risk = self.classify_risk(context)
        complexity = self.score_complexity(context)
        
        # Select format based on risk + complexity
        if risk == RiskLevel.LOW or complexity <= 3:
            recommended_format = ResponseFormat.BLUF_ONLY
            rationale = "Low risk, simple operation - executive summary sufficient"
        elif risk == RiskLevel.MEDIUM or complexity <= 7:
            recommended_format = ResponseFormat.HYBRID
            rationale = "Medium complexity - summary + key details needed"
        else:
            recommended_format = ResponseFormat.FULL_DETAIL
            rationale = "High risk, complex operation - full transparency required"
        
        return ResponseMetadata(
            risk_level=risk,
            complexity_score=complexity,
            recommended_format=recommended_format,
            rationale=rationale,
        )


@dataclass
class BLUFTemplate:
    """BLUF response template.
    
    Attributes:
        format_type: Response format
        bottom_line: Executive summary (1-2 sentences)
        key_points: 3-5 essential points
        risks: Identified risks
        details: Full details (if applicable)
        timeline: Expected timeline
        next_steps: Recommended actions
    """
    format_type: ResponseFormat
    bottom_line: str = ""
    key_points: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    details: str = ""
    timeline: str = ""
    next_steps: List[str] = field(default_factory=list)


class BLUFTemplateEngine:
    """Phase 13 BLUF-2: BLUF Template Engine.
    
    Generates responses in three formats:
    1. BLUF_ONLY: One paragraph, actionable, no details
    2. HYBRID: BLUF + 3-5 key points + risks
    3. FULL_DETAIL: Complete analysis + rationale + dependencies
    
    AC-BLUF-2-01: Generate BLUF_ONLY template
    AC-BLUF-2-02: Generate HYBRID template
    AC-BLUF-2-03: Generate FULL_DETAIL template
    AC-BLUF-2-04: Ensure progressive disclosure of information
    """
    
    @staticmethod
    def generate_bluf_only(
        bottom_line: str,
        timeline: str = "Immediate"
    ) -> BLUFTemplate:
        """Generate BLUF_ONLY response.
        
        Phase 13 AC-BLUF-2-01: Generate BLUF_ONLY template
        
        Args:
            bottom_line: Executive summary
            timeline: Timeline estimate
            
        Returns:
            BLUF template
        """
        return BLUFTemplate(
            format_type=ResponseFormat.BLUF_ONLY,
            bottom_line=bottom_line,
            timeline=timeline,
            next_steps=["Proceed" if "approved" in bottom_line.lower() else "Review"],
        )
    
    @staticmethod
    def generate_hybrid(
        bottom_line: str,
        key_points: List[str],
        risks: List[str],
        timeline: str = ""
    ) -> BLUFTemplate:
        """Generate HYBRID response.
        
        Phase 13 AC-BLUF-2-02: Generate HYBRID template
        
        Args:
            bottom_line: Executive summary
            key_points: List of key points (3-5)
            risks: List of identified risks
            timeline: Timeline estimate
            
        Returns:
            BLUF template
        """
        return BLUFTemplate(
            format_type=ResponseFormat.HYBRID,
            bottom_line=bottom_line,
            key_points=key_points[:5],
            risks=risks,
            timeline=timeline,
            next_steps=[
                "Review key points",
                "Assess risks",
                "Proceed if approved"
            ],
        )
    
    @staticmethod
    def generate_full_detail(
        bottom_line: str,
        key_points: List[str],
        risks: List[str],
        details: str,
        timeline: str = "",
        next_steps: List[str] = None
    ) -> BLUFTemplate:
        """Generate FULL_DETAIL response.
        
        Phase 13 AC-BLUF-2-03: Generate FULL_DETAIL template
        
        Args:
            bottom_line: Executive summary
            key_points: Key points
            risks: Identified risks
            details: Full details
            timeline: Timeline estimate
            next_steps: Recommended steps
            
        Returns:
            BLUF template
        """
        if next_steps is None:
            next_steps = []
        
        return BLUFTemplate(
            format_type=ResponseFormat.FULL_DETAIL,
            bottom_line=bottom_line,
            key_points=key_points,
            risks=risks,
            details=details,
            timeline=timeline,
            next_steps=next_steps or [
                "Review full analysis",
                "Discuss with stakeholders",
                "Document decision",
                "Execute plan"
            ],
        )


class AdaptiveRouter:
    """Phase 13 BLUF-3: Adaptive Router.
    
    Routes responses based on:
    - User preference mode
    - Operation risk/complexity
    - Audience (executive vs technical)
    
    Implements smart routing:
    - EXECUTIVE preference + HIGH risk → FULL_DETAIL (compliance)
    - EXECUTIVE preference + LOW risk → BLUF_ONLY
    - TECHNICAL preference → Prefer FULL_DETAIL/HYBRID
    - BALANCED preference → HYBRID
    - ADAPTIVE mode → Decide based on risk/complexity
    
    AC-BLUF-3-01: Support 4 user preference modes
    AC-BLUF-3-02: Route based on risk + preference
    AC-BLUF-3-03: Implement smart format selection
    AC-BLUF-3-04: Respect user overrides
    """
    
    @staticmethod
    def route_response(
        metadata: ResponseMetadata,
        user_preference: UserPreferenceMode = UserPreferenceMode.ADAPTIVE,
        override_format: Optional[ResponseFormat] = None
    ) -> ResponseFormat:
        """Route response to appropriate format.
        
        Phase 13 AC-BLUF-3-02: Route based on risk + preference
        
        Args:
            metadata: Response metadata
            user_preference: User preference mode
            override_format: User-specified format override
            
        Returns:
            Selected response format
        """
        # User override takes precedence
        if override_format:
            return override_format
        
        # Route based on preference
        if user_preference == UserPreferenceMode.EXECUTIVE:
            # Executives want BLUF for low complexity, FULL_DETAIL for high risk
            if metadata.risk_level == RiskLevel.HIGH:
                return ResponseFormat.FULL_DETAIL
            elif metadata.complexity_score <= 3:
                return ResponseFormat.BLUF_ONLY
            else:
                return ResponseFormat.HYBRID
        
        elif user_preference == UserPreferenceMode.TECHNICAL:
            # Technical users want details
            return ResponseFormat.FULL_DETAIL if metadata.complexity_score > 5 else ResponseFormat.HYBRID
        
        elif user_preference == UserPreferenceMode.BALANCED:
            # Balanced users want summary + essentials
            return ResponseFormat.HYBRID
        
        else:  # ADAPTIVE
            # Use recommended format
            return metadata.recommended_format
    
    @staticmethod
    def format_response(
        template: BLUFTemplate,
        format_type: ResponseFormat
    ) -> str:
        """Format template for output.
        
        Phase 13 AC-BLUF-3-04: Support multiple output formats
        
        Args:
            template: BLUF template
            format_type: Output format type
            
        Returns:
            Formatted response string
        """
        lines = []
        
        # Always include bottom line
        if template.bottom_line:
            lines.append(f"**Bottom Line:** {template.bottom_line}")
            lines.append("")
        
        # HYBRID and above include key points
        if format_type in [ResponseFormat.HYBRID, ResponseFormat.FULL_DETAIL]:
            if template.key_points:
                lines.append("**Key Points:**")
                for i, point in enumerate(template.key_points, 1):
                    lines.append(f"{i}. {point}")
                lines.append("")
            
            if template.risks:
                lines.append("**Risks:**")
                for risk in template.risks:
                    lines.append(f"- {risk}")
                lines.append("")
        
        # FULL_DETAIL includes all details
        if format_type == ResponseFormat.FULL_DETAIL:
            if template.details:
                lines.append("**Details:**")
                lines.append(template.details)
                lines.append("")
        
        # Include timeline and next steps if available
        if template.timeline:
            lines.append(f"**Timeline:** {template.timeline}")
        
        if template.next_steps:
            lines.append("**Next Steps:**")
            for step in template.next_steps:
                lines.append(f"- {step}")
        
        return "\n".join(lines)


class AnalyticsOrchestrator:
    """Phase 13 BLUF-5: Analytics Orchestrator.
    
    Tracks format effectiveness and user satisfaction.
    
    Metrics:
    - Format usage distribution
    - User satisfaction by format
    - Average response time
    - Format-to-action conversion
    
    AC-BLUF-5-01: Track format usage
    AC-BLUF-5-02: Measure user satisfaction
    AC-BLUF-5-03: Calculate format ROI
    AC-BLUF-5-04: Recommend format improvements
    """
    
    def __init__(self):
        """Initialize AnalyticsOrchestrator."""
        self.format_usage: Dict[ResponseFormat, int] = {fmt: 0 for fmt in ResponseFormat}
        self.satisfaction_scores: Dict[ResponseFormat, List[float]] = {fmt: [] for fmt in ResponseFormat}
    
    def record_format_usage(self, format_type: ResponseFormat) -> None:
        """Record format usage.
        
        Phase 13 AC-BLUF-5-01: Track format usage
        
        Args:
            format_type: Format used
        """
        self.format_usage[format_type] = self.format_usage.get(format_type, 0) + 1
    
    def record_satisfaction(self, format_type: ResponseFormat, score: float) -> None:
        """Record user satisfaction score.
        
        Phase 13 AC-BLUF-5-02: Measure user satisfaction
        
        Args:
            format_type: Format used
            score: Satisfaction score (1-5)
        """
        if format_type not in self.satisfaction_scores:
            self.satisfaction_scores[format_type] = []
        self.satisfaction_scores[format_type].append(score)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics summary.
        
        Returns:
            Analytics dictionary
        """
        total_responses = sum(self.format_usage.values())
        
        format_satisfaction = {}
        for fmt, scores in self.satisfaction_scores.items():
            if scores:
                avg_score = sum(scores) / len(scores)
                format_satisfaction[fmt.value] = {
                    "avg_satisfaction": f"{avg_score:.2f}/5",
                    "responses": len(scores),
                }
        
        return {
            "total_responses": total_responses,
            "format_distribution": {fmt.value: count for fmt, count in self.format_usage.items()},
            "satisfaction_by_format": format_satisfaction,
        }


if __name__ == "__main__":
    logger.info("Adaptive BLUF Communication System - Phase 13")
