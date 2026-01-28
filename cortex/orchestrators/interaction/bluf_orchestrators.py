"""Adaptive BLUF Communication System - Phase 13 Orchestrators.

Phase 13 - Adaptive BLUF Communication System

This module provides orchestrators for context-aware response formatting
with BLUF (Bottom Line Up Front) military communication standard.

Key components:
- ResponseFormatAnalyzer: Classifies operation risk and complexity
- BLUFTemplateEngine: Renders 3 response formats with progressive disclosure
- AdaptiveRouter: Routes to appropriate format based on context + user preferences
- AnalyticsOrchestrator: Tracks format effectiveness and improves routing

Implementation Status: IMPLEMENTED (Phase 13)

CORE-035: Uses canonical enums from cortex.models.canonical_enums
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

# CORE-035: Import from canonical location
from cortex.models.canonical_enums import (
    RiskLevel,
    ComplexityLevel,
    ResponseFormat,
    UserPreferenceMode,
)


logger = logging.getLogger(__name__)


@dataclass
class OperationContext:
    """Context about the operation being executed.
    
    Attributes:
        intent: Intent type (IMPLEMENT, FIX, ANALYZE, etc.)
        target: Target entity (file, module, system)
        scope: Scope level (FILE, MODULE, SYSTEM, DOMAIN)
        estimated_hours: Estimated effort
        dependencies_count: Number of affected dependencies
        reversible: Whether changes are reversible
    """
    intent: str
    target: str
    scope: str
    estimated_hours: Optional[float] = None
    dependencies_count: int = 0
    reversible: bool = True


@dataclass
class FormatAnalysisResult:
    """Result of format analysis decision.
    
    Attributes:
        risk_level: Calculated risk level
        complexity_level: Calculated complexity
        recommended_format: Recommended response format
        confidence: Confidence in recommendation (0.0-1.0)
        decision_factors: Factors influencing the decision
    """
    risk_level: RiskLevel
    complexity_level: ComplexityLevel
    recommended_format: ResponseFormat
    confidence: float
    decision_factors: Dict[str, Any]


class ResponseFormatAnalyzer:
    """Analyzes operation context to determine response format.
    
    Responsibilities:
    - Classify operation risk (LOW/MEDIUM/HIGH)
    - Calculate operation complexity score
    - Route to appropriate response format
    - Extract key decision factors
    
    Implementation Status: IMPLEMENTED (Phase 13 - BLUF-1)
    """
    
    # Risk classification by intent
    LOW_RISK_INTENTS = {"ANALYZE", "DOCUMENT", "READ", "QUERY", "LIST", "STATUS"}
    MEDIUM_RISK_INTENTS = {"REFACTOR", "TEST", "CONFIG", "LINT", "FORMAT"}
    HIGH_RISK_INTENTS = {"IMPLEMENT", "FIX", "DEPLOY", "DELETE", "MIGRATE", "UPGRADE"}
    
    def classify_risk(self, context: OperationContext) -> RiskLevel:
        """Classify operation risk level.
        
        Phase 13 AC-BLUF-1-01: Risk classifier categorizes operations correctly
        
        Risk matrix:
        - LOW: ANALYZE, DOCUMENT, READ (no code modification)
        - MEDIUM: REFACTOR, TEST, CONFIG (reversible changes)
        - HIGH: IMPLEMENT, FIX, DEPLOY, DELETE (irreversible)
        
        Args:
            context: Operation context
            
        Returns:
            Risk level classification
        """
        intent_upper = context.intent.upper()
        
        # Check reversibility - non-reversible operations are always HIGH risk
        if not context.reversible:
            return RiskLevel.HIGH
        
        # Classify by intent type
        if intent_upper in self.LOW_RISK_INTENTS:
            return RiskLevel.LOW
        elif intent_upper in self.MEDIUM_RISK_INTENTS:
            return RiskLevel.MEDIUM
        elif intent_upper in self.HIGH_RISK_INTENTS:
            return RiskLevel.HIGH
        
        # Default to MEDIUM for unknown intents
        logger.warning(f"Unknown intent '{context.intent}' - defaulting to MEDIUM risk")
        return RiskLevel.MEDIUM
    
    def calculate_complexity(self, context: OperationContext) -> int:
        """Calculate complexity score (1-13 points).
        
        Phase 13 AC-BLUF-1-02: Complexity scorer calculates scores accurately
        
        Scoring:
        - Scope: FILE (1), MODULE (2), SYSTEM (3), DOMAIN (4)
        - Impact: Low (1), Medium (2), High (3)
        - Dependencies: 0-2 (1), 3-5 (2), 6+ (3)
        - Hours: <2h (1), 2-8h (2), 8+ (3)
        
        Args:
            context: Operation context
            
        Returns:
            Complexity score (1-13)
        """
        score = 0
        
        # Scope scoring
        scope_scores = {"FILE": 1, "MODULE": 2, "SYSTEM": 3, "DOMAIN": 4}
        score += scope_scores.get(context.scope.upper(), 2)  # Default MODULE
        
        # Impact scoring (based on risk - approximation)
        risk = self.classify_risk(context)
        impact_scores = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3}
        score += impact_scores.get(risk, 2)
        
        # Dependencies scoring
        deps = context.dependencies_count
        if deps <= 2:
            score += 1
        elif deps <= 5:
            score += 2
        else:
            score += 3
        
        # Hours scoring
        hours = context.estimated_hours or 2.0  # Default 2 hours
        if hours < 2:
            score += 1
        elif hours <= 8:
            score += 2
        else:
            score += 3
        
        return min(13, max(1, score))  # Clamp to 1-13
    
    def complexity_to_level(self, score: int) -> ComplexityLevel:
        """Convert score to complexity level.
        
        Verifies:
        - 1-4 → LOW
        - 5-8 → MEDIUM
        - 9-13 → HIGH
        
        Args:
            score: Complexity score
            
        Returns:
            Complexity level
        """
        if score <= 4:
            return ComplexityLevel.LOW
        elif score <= 8:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.HIGH
    
    def route_to_format(self, risk: RiskLevel, complexity: ComplexityLevel) -> ResponseFormat:
        """Route operation to appropriate response format.
        
        Phase 13 AC-BLUF-1-03: Format router selects appropriate format
        
        Format routing matrix:
        | Risk | Complexity | Format |
        |------|-----------|--------|
        | LOW | LOW | BLUF_ONLY |
        | LOW | MEDIUM | BLUF_HYBRID |
        | LOW | HIGH | BLUF_HYBRID |
        | MEDIUM | LOW | BLUF_HYBRID |
        | MEDIUM | MEDIUM | BLUF_HYBRID |
        | MEDIUM | HIGH | FULL_DETAIL |
        | HIGH | * | FULL_DETAIL |
        
        Args:
            risk: Risk level
            complexity: Complexity level
            
        Returns:
            Recommended response format
        """
        # HIGH risk always gets FULL_DETAIL
        if risk == RiskLevel.HIGH:
            return ResponseFormat.FULL_DETAIL
        
        # LOW risk routing
        if risk == RiskLevel.LOW:
            if complexity == ComplexityLevel.LOW:
                return ResponseFormat.BLUF_ONLY
            else:
                return ResponseFormat.BLUF_HYBRID
        
        # MEDIUM risk routing
        if complexity == ComplexityLevel.HIGH:
            return ResponseFormat.FULL_DETAIL
        else:
            return ResponseFormat.BLUF_HYBRID
    
    def analyze_format(self, context: OperationContext) -> FormatAnalysisResult:
        """Analyze operation and determine response format.
        
        Phase 13 AC-BLUF-1-04: Key extractor generates concise executive summary
        
        Args:
            context: Operation context
            
        Returns:
            Format analysis result with recommendation
        """
        # Calculate all components
        risk = self.classify_risk(context)
        complexity_score = self.calculate_complexity(context)
        complexity = self.complexity_to_level(complexity_score)
        recommended_format = self.route_to_format(risk, complexity)
        
        # Build decision factors
        decision_factors = {
            "intent": context.intent,
            "scope": context.scope,
            "target": context.target,
            "complexity_score": complexity_score,
            "dependencies": context.dependencies_count,
            "estimated_hours": context.estimated_hours,
            "reversible": context.reversible,
        }
        
        # Calculate confidence based on how clearly the context maps
        # Higher confidence when intent is explicitly known
        if context.intent.upper() in self.LOW_RISK_INTENTS | self.MEDIUM_RISK_INTENTS | self.HIGH_RISK_INTENTS:
            confidence = 0.9
        else:
            confidence = 0.7  # Unknown intent
        
        return FormatAnalysisResult(
            risk_level=risk,
            complexity_level=complexity,
            recommended_format=recommended_format,
            confidence=confidence,
            decision_factors=decision_factors,
        )


class BLUFTemplateEngine:
    """Renders response templates with appropriate detail level.
    
    Template types:
    1. BLUF_ONLY: Executive summary only (50 lines max)
    2. BLUF_HYBRID: Summary + decision factors + collapsible details
    3. FULL_DETAIL: All existing detail with BLUF header
    
    Implementation Status: IMPLEMENTED (Phase 13 - BLUF-2)
    """
    
    def render_bluf_only(self, context: OperationContext) -> str:
        """Render BLUF-only template.
        
        Phase 13 AC-BLUF-2-01: BLUF-only template renders executive summary
        
        Format:
        - Header with phase/orchestrator
        - BLUF section (action, risk, impact)
        - Recommendation
        
        Args:
            context: Operation context
            
        Returns:
            Formatted BLUF-only response
        """
        analyzer = ResponseFormatAnalyzer()
        analysis = analyzer.analyze_format(context)
        
        bluf = f"""## 🧠 CORTEX {context.intent.upper()}
**Author:** Asif Hussain | **Phase:** 13 | **Orchestrator:** BLUFOrchestrator ✅

---

### 📋 BLUF (Bottom Line Up Front)

| Field | Value |
|-------|-------|
| **Action** | `{context.intent.upper()}` |
| **Target** | `{context.target}` |
| **Risk** | {self._format_risk_badge(analysis.risk_level)} |
| **Complexity** | {self._format_complexity_badge(analysis.complexity_level)} |
| **Reversible** | {'✅ Yes' if context.reversible else '❌ No'} |

**Recommendation:** Proceed with {analysis.recommended_format.value} response format.
"""
        return bluf
    
    def render_bluf_hybrid(self, context: OperationContext, decision_factors: Dict[str, Any]) -> str:
        """Render BLUF-hybrid template with progressive disclosure.
        
        Phase 13 AC-BLUF-2-02: BLUF-hybrid template with collapsible sections
        
        Format:
        - Header
        - BLUF section
        - Decision factors table
        - Collapsible details (<details> tag)
        
        Args:
            context: Operation context
            decision_factors: Quick decision factors
            
        Returns:
            Formatted BLUF-hybrid response
        """
        analyzer = ResponseFormatAnalyzer()
        analysis = analyzer.analyze_format(context)
        
        # Build decision factors table
        factors_rows = "\n".join(
            f"| **{k.replace('_', ' ').title()}** | `{v}` |"
            for k, v in decision_factors.items()
            if v is not None
        )
        
        bluf = f"""## 🧠 CORTEX {context.intent.upper()}
**Author:** Asif Hussain | **Phase:** 13 | **Orchestrator:** BLUFOrchestrator ✅

---

### 📋 BLUF (Bottom Line Up Front)

| Field | Value |
|-------|-------|
| **Action** | `{context.intent.upper()}` |
| **Target** | `{context.target}` |
| **Risk** | {self._format_risk_badge(analysis.risk_level)} |
| **Complexity** | {self._format_complexity_badge(analysis.complexity_level)} |

---

### 🎯 Decision Factors

| Factor | Value |
|--------|-------|
{factors_rows}

---

<details>
<summary>📚 Click for Full Details</summary>

**Scope:** {context.scope}  
**Dependencies:** {context.dependencies_count}  
**Estimated Hours:** {context.estimated_hours or 'N/A'}  
**Reversible:** {'Yes' if context.reversible else 'No'}  

</details>
"""
        return bluf
    
    def render_full_detail(self, context: OperationContext, full_response: str) -> str:
        """Render full detail template with BLUF header.
        
        Phase 13 AC-BLUF-2-03: Full detail template preserves existing behavior
        
        Args:
            context: Operation context
            full_response: Full detailed response
            
        Returns:
            Full response with BLUF header prepended
        """
        analyzer = ResponseFormatAnalyzer()
        analysis = analyzer.analyze_format(context)
        
        bluf_header = f"""## 🧠 CORTEX {context.intent.upper()}
**Author:** Asif Hussain | **Phase:** 13 | **Orchestrator:** BLUFOrchestrator ✅

---

### 📋 BLUF (Bottom Line Up Front)

| Field | Value |
|-------|-------|
| **Action** | `{context.intent.upper()}` |
| **Target** | `{context.target}` |
| **Risk** | {self._format_risk_badge(analysis.risk_level)} |
| **Complexity** | {self._format_complexity_badge(analysis.complexity_level)} |

---

### 📄 Full Details

{full_response}
"""
        return bluf_header
    
    def _format_risk_badge(self, risk: RiskLevel) -> str:
        """Format risk level as badge."""
        badges = {
            RiskLevel.LOW: "🟢 LOW",
            RiskLevel.MEDIUM: "🟡 MEDIUM",
            RiskLevel.HIGH: "🔴 HIGH",
        }
        return badges.get(risk, "⚪ UNKNOWN")
    
    def _format_complexity_badge(self, complexity: ComplexityLevel) -> str:
        """Format complexity level as badge."""
        badges = {
            ComplexityLevel.LOW: "🔵 LOW",
            ComplexityLevel.MEDIUM: "🟡 MEDIUM",
            ComplexityLevel.HIGH: "🔴 HIGH",
        }
        return badges.get(complexity, "⚪ UNKNOWN")


class AdaptiveRouter:
    """Routes response to appropriate format based on context and preferences.
    
    Modes:
    - AUTO: Context-aware routing (default)
    - BLUF: Always BLUF (with expandable details)
    - FULL: Always full detail
    - BLUF_ONLY: BLUF only (no expandable)
    
    Implementation Status: IMPLEMENTED (Phase 13 - BLUF-3)
    """
    
    def __init__(self, user_preference: UserPreferenceMode = UserPreferenceMode.AUTO):
        """Initialize router with user preference.
        
        Args:
            user_preference: User's format preference mode
        """
        self.user_preference = user_preference
    
    def route_response(self, context: OperationContext, format_analysis: FormatAnalysisResult) -> ResponseFormat:
        """Route response to appropriate format.
        
        Phase 13 AC-BLUF-3-01: Router respects user preferences
        
        Args:
            context: Operation context
            format_analysis: Format analysis result
            
        Returns:
            Final response format to use
        """
        # User preference overrides context-aware routing
        if self.user_preference == UserPreferenceMode.BLUF:
            return ResponseFormat.BLUF_HYBRID
        elif self.user_preference == UserPreferenceMode.FULL:
            return ResponseFormat.FULL_DETAIL
        elif self.user_preference == UserPreferenceMode.BLUF_ONLY:
            return ResponseFormat.BLUF_ONLY
        
        # AUTO mode - use context-aware routing from analysis
        return format_analysis.recommended_format


class AnalyticsOrchestrator:
    """Tracks response format effectiveness and improves routing.
    
    Metrics tracked:
    - Approval rate by format
    - Time-to-decision by format
    - User format preferences
    - Format effectiveness trends
    
    Implementation Status: IMPLEMENTED (Phase 13 - BLUF-5)
    """
    
    def __init__(self):
        """Initialize analytics with empty metrics."""
        self._metrics: Dict[ResponseFormat, Dict[str, Any]] = {
            ResponseFormat.BLUF_ONLY: {"approved": 0, "total": 0, "times": []},
            ResponseFormat.BLUF_HYBRID: {"approved": 0, "total": 0, "times": []},
            ResponseFormat.FULL_DETAIL: {"approved": 0, "total": 0, "times": []},
        }
        self._history: list = []
    
    def record_response(self, context: OperationContext, format_used: ResponseFormat, approved: bool):
        """Record response format usage and outcome.
        
        Phase 13 AC-BLUF-5-01: Analytics tracks approval rate by format
        
        Args:
            context: Operation context
            format_used: Format that was used
            approved: Whether operation was approved/executed
        """
        if format_used not in self._metrics:
            self._metrics[format_used] = {"approved": 0, "total": 0, "times": []}
        
        self._metrics[format_used]["total"] += 1
        if approved:
            self._metrics[format_used]["approved"] += 1
        
        # Record history for trend analysis
        self._history.append({
            "context": context,
            "format": format_used,
            "approved": approved,
        })
        
        logger.debug(f"Recorded response: {format_used.value}, approved={approved}")
    
    def get_format_effectiveness(self) -> Dict[ResponseFormat, Dict[str, float]]:
        """Get effectiveness metrics for each response format.
        
        Returns:
            Format effectiveness: {format: {approval_rate, time_to_decision}}
        """
        effectiveness = {}
        
        for format_type, metrics in self._metrics.items():
            total = metrics["total"]
            approved = metrics["approved"]
            
            effectiveness[format_type] = {
                "approval_rate": (approved / total * 100) if total > 0 else 0.0,
                "total_uses": total,
                "approved_count": approved,
            }
        
        return effectiveness
    
    def generate_improvement_report(self) -> Dict[str, Any]:
        """Generate weekly improvement report.
        
        Phase 13 AC-BLUF-5-02: Analytics generates improvement reports
        
        Returns:
            Report with trends, recommendations, and formatting suggestions
        """
        effectiveness = self.get_format_effectiveness()
        
        # Find best performing format
        best_format = None
        best_rate = -1
        for fmt, metrics in effectiveness.items():
            if metrics["total_uses"] > 0 and metrics["approval_rate"] > best_rate:
                best_rate = metrics["approval_rate"]
                best_format = fmt
        
        # Generate recommendations
        recommendations = []
        for fmt, metrics in effectiveness.items():
            if metrics["total_uses"] > 5 and metrics["approval_rate"] < 50:
                recommendations.append(
                    f"Consider reducing use of {fmt.value} (approval rate: {metrics['approval_rate']:.1f}%)"
                )
        
        if best_format:
            recommendations.append(
                f"Best performing format: {best_format.value} ({best_rate:.1f}% approval)"
            )
        
        return {
            "effectiveness": {fmt.value: metrics for fmt, metrics in effectiveness.items()},
            "total_responses": len(self._history),
            "best_format": best_format.value if best_format else None,
            "recommendations": recommendations,
        }


if __name__ == "__main__":
    logger.info("Adaptive BLUF Communication System - Phase 13 Orchestrators")
    logger.info("Implementation status: PLANNED")
