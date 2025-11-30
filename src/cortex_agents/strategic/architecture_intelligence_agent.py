"""
CORTEX Architecture Intelligence Agent

Strategic agent for holistic architecture review, trend analysis, and
technical debt forecasting. Does NOT modify architecture - read-only analysis.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from src.validation.integration_scorer import IntegrationScorer
from src.tier3.architecture_health_history import ArchitectureHealthHistory
from src.discovery.orchestrator_scanner import OrchestratorScanner
from src.discovery.agent_scanner import AgentScanner

logger = logging.getLogger(__name__)


class ArchitectureIntelligenceAgent(BaseAgent):
    """
    Strategic architecture health and evolution analysis agent.
    
    Responsibilities:
    - Holistic architecture review (leverages IntegrationScorer)
    - Trend analysis (health over time)
    - Technical debt forecasting
    - ADR auto-generation for CORTEX 4.0 recommendations
    - Cross-layer dependency validation
    
    Does NOT:
    - Modify architecture (read-only)
    - Duplicate System Alignment (extends it)
    - Replace Brain Protection (augments it)
    
    Intents Handled:
    - review_architecture
    - analyze_architectural_health
    - forecast_technical_debt
    - track_architecture_evolution
    """
    
    def __init__(self, cortex_root: Path):
        """
        Initialize Architecture Intelligence Agent.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        super().__init__(name="ArchitectureIntelligenceAgent")
        self.cortex_root = Path(cortex_root)
        self.agent_name = "ArchitectureIntelligenceAgent"
        
        # Initialize dependencies
        self.scorer = IntegrationScorer(self.cortex_root)
        self.health_history = ArchitectureHealthHistory()
        self.orchestrator_scanner = OrchestratorScanner(self.cortex_root)
        self.agent_scanner = AgentScanner(self.cortex_root)
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: Agent request to evaluate
            
        Returns:
            True if agent can handle this intent
        """
        handled_intents = [
            "review_architecture",
            "analyze_architectural_health",
            "forecast_technical_debt",
            "track_architecture_evolution",
            "architecture_report"
        ]
        return request.intent in handled_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute architecture intelligence analysis.
        
        Args:
            request: Agent request with intent and context
            
        Returns:
            AgentResponse with analysis results
        """
        start_time = datetime.now()
        
        try:
            # Route to appropriate handler
            if request.intent == "review_architecture":
                result = self._conduct_full_review(request)
            elif request.intent == "analyze_architectural_health":
                result = self._analyze_current_health(request)
            elif request.intent == "forecast_technical_debt":
                result = self._forecast_debt(request)
            elif request.intent == "track_architecture_evolution":
                result = self._track_evolution(request)
            elif request.intent == "architecture_report":
                result = self._generate_report(request)
            else:
                return AgentResponse(
                    success=False,
                    result={},
                    message=f"Unknown intent: {request.intent}",
                    agent_name=self.agent_name,
                    error="Intent not recognized"
                )
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=True,
                result=result,
                message=result.get("summary", "Architecture analysis complete"),
                agent_name=self.agent_name,
                duration_ms=duration,
                next_actions=result.get("next_actions", [])
            )
        
        except Exception as e:
            logger.error(f"Architecture intelligence agent error: {e}", exc_info=True)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=False,
                result={},
                message=f"Analysis failed: {str(e)}",
                agent_name=self.agent_name,
                duration_ms=duration,
                error=str(e)
            )
    
    def _conduct_full_review(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Conduct comprehensive architecture review.
        
        Returns:
            Full review results with current health, trends, and forecast
        """
        # 1. Get current architecture health
        current_health = self._analyze_current_health(request)
        
        # 2. Analyze trends
        trend_analysis = self.health_history.analyze_trends(days=30)
        
        # 3. Forecast future health
        forecast_3month = self.health_history.forecast_health(months=3)
        forecast_6month = self.health_history.forecast_health(months=6)
        
        # 4. Generate recommendations for CORTEX 4.0
        recommendations = self._generate_cortex4_recommendations(
            current_health,
            trend_analysis,
            forecast_3month
        )
        
        # 5. Record this review snapshot
        snapshot_id = self.health_history.record_health_snapshot(
            overall_score=current_health["overall_score"],
            layer_scores=current_health["layer_breakdown"],
            feature_breakdown=current_health["feature_breakdown"],
            recommendations=recommendations[:3],
            metadata={
                "review_type": "full",
                "trend": trend_analysis["direction"],
                "forecast_3m": forecast_3month.get("predicted_score")
            }
        )
        
        # 6. Save report to cortex-brain/documents/analysis/
        report_path = self._save_review_report({
            "current_health": current_health,
            "trend_analysis": trend_analysis,
            "forecast_3month": forecast_3month,
            "forecast_6month": forecast_6month,
            "recommendations": recommendations
        })
        
        return {
            "summary": f"Architecture review complete - Health: {current_health['overall_score']:.1f}%",
            "current_health": current_health,
            "trend_analysis": trend_analysis,
            "forecast": {
                "3_months": forecast_3month,
                "6_months": forecast_6month
            },
            "cortex_4_recommendations": recommendations,
            "snapshot_id": snapshot_id,
            "report_path": str(report_path),
            "next_actions": self._suggest_next_actions(current_health, trend_analysis)
        }
    
    def _analyze_current_health(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Analyze current architecture health.
        
        Returns:
            Current health metrics
        """
        # Discover all features
        orchestrators = self.orchestrator_scanner.discover()
        agents = self.agent_scanner.discover()
        
        # Convert dictionaries to lists if needed
        all_features = list(orchestrators.values()) if isinstance(orchestrators, dict) else orchestrators
        all_features.extend(list(agents.values()) if isinstance(agents, dict) else agents)
        total_features = len(all_features)
        
        if total_features == 0:
            return {
                "overall_score": 0.0,
                "feature_breakdown": {"total": 0, "healthy": 0, "warning": 0, "critical": 0},
                "layer_breakdown": {},
                "summary": "No features discovered"
            }
        
        # Calculate scores for each feature
        scores = []
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        
        layer_totals = {
            "discovered": 0,
            "imported": 0,
            "instantiated": 0,
            "documented": 0,
            "tested": 0,
            "wired": 0,
            "optimized": 0
        }
        
        for feature in all_features:
            feature_type = "orchestrator" if "orchestrator" in feature.get("module_path", "").lower() else "agent"
            
            score_result = self.scorer.calculate_score(
                feature_name=feature["name"],
                metadata={"module_path": feature.get("module_path"), "class_name": feature["name"]},
                feature_type=feature_type,
                documentation_validated=feature.get("has_documentation", False),
                test_coverage_pct=0.0,  # TODO: Get actual coverage
                is_wired=feature.get("is_wired", False),
                performance_validated=False
            )
            
            overall_score = score_result if isinstance(score_result, (int, float)) else score_result.get("overall_score", 0)
            scores.append(overall_score)
            
            # Categorize feature
            if overall_score >= 90:
                healthy_count += 1
            elif overall_score >= 70:
                warning_count += 1
            else:
                critical_count += 1
            
            # Accumulate layer scores (if detailed breakdown available)
            if isinstance(score_result, dict) and "layers" in score_result:
                for layer, points in score_result["layers"].items():
                    layer_totals[layer] += points
        
        # Calculate overall score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        # Normalize layer totals
        layer_breakdown = {
            layer: round(total / total_features, 2)
            for layer, total in layer_totals.items()
        }
        
        return {
            "overall_score": round(overall_score, 2),
            "feature_breakdown": {
                "total": total_features,
                "healthy": healthy_count,
                "warning": warning_count,
                "critical": critical_count
            },
            "layer_breakdown": layer_breakdown,
            "orchestrator_count": len(orchestrators),
            "agent_count": len(agents),
            "summary": f"{total_features} features analyzed - {healthy_count} healthy, {warning_count} warnings, {critical_count} critical"
        }
    
    def _forecast_debt(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Forecast technical debt at 3 and 6 month horizons.
        
        Returns:
            Debt forecast data
        """
        forecast_3m = self.health_history.forecast_health(months=3)
        forecast_6m = self.health_history.forecast_health(months=6)
        
        return {
            "summary": "Technical debt forecast generated",
            "forecast_3_months": forecast_3m,
            "forecast_6_months": forecast_6m,
            "next_actions": [
                "Review forecasted issues",
                "Prioritize high-impact items",
                "Schedule remediation work"
            ]
        }
    
    def _track_evolution(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Track architecture evolution over time.
        
        Returns:
            Evolution data with historical trends
        """
        stats = self.health_history.get_health_statistics()
        trend_analysis = self.health_history.analyze_trends(days=90)
        
        return {
            "summary": "Architecture evolution tracked",
            "statistics": stats,
            "trend_90_days": trend_analysis,
            "next_actions": [
                "Monitor for degradation patterns",
                "Celebrate improvements",
                "Address declining areas"
            ]
        }
    
    def _generate_report(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Generate detailed architecture report.
        
        Returns:
            Report generation result
        """
        # Leverage full review
        review_result = self._conduct_full_review(request)
        
        return {
            "summary": "Architecture report generated",
            "report_path": review_result["report_path"],
            "health_score": review_result["current_health"]["overall_score"],
            "next_actions": ["Review report", "Share with team", "Plan improvements"]
        }
    
    def _generate_cortex4_recommendations(
        self,
        current_health: Dict[str, Any],
        trend_analysis: Dict[str, Any],
        forecast: Dict[str, Any]
    ) -> list[str]:
        """Generate prioritized recommendations for CORTEX 4.0."""
        recommendations = []
        
        # Health-based recommendations
        if current_health["overall_score"] < 70:
            recommendations.append("CRITICAL: System health below 70% - immediate remediation required")
        
        # Trend-based recommendations
        if trend_analysis["direction"] == "degrading":
            recommendations.append(f"WARNING: Health declining at {abs(trend_analysis['velocity']):.2f} pts/day - investigate root cause")
        
        # Forecast-based recommendations
        if forecast.get("intervention_needed"):
            recommendations.append(f"PLANNING: Forecast predicts health drop to {forecast['predicted_score']:.1f}% - schedule preventive work")
        
        # Feature-based recommendations
        critical_count = current_health["feature_breakdown"]["critical"]
        if critical_count > 0:
            recommendations.append(f"TECHNICAL DEBT: {critical_count} critical features need attention")
        
        # Layer-based recommendations
        layer_scores = current_health["layer_breakdown"]
        if layer_scores.get("tested", 0) < 10:
            recommendations.append("TESTING: Low test coverage across features - prioritize test creation")
        
        if layer_scores.get("wired", 0) < 10:
            recommendations.append("INTEGRATION: Features not wired to entry point - complete integration")
        
        # Default recommendations if all healthy
        if not recommendations:
            recommendations.extend([
                "✅ Maintain current health levels",
                "✅ Continue regular reviews",
                "✅ Monitor for new issues"
            ])
        
        return recommendations
    
    def _suggest_next_actions(
        self,
        current_health: Dict[str, Any],
        trend_analysis: Dict[str, Any]
    ) -> list[str]:
        """Suggest immediate next actions based on health and trends."""
        actions = []
        
        if current_health["overall_score"] < 70:
            actions.append("Address critical features immediately")
        
        if trend_analysis["direction"] == "degrading":
            actions.append("Investigate root cause of degradation")
        
        if current_health["feature_breakdown"]["critical"] > 0:
            actions.append("Review critical features list")
        
        actions.append("Schedule next architecture review")
        
        return actions
    
    def _save_review_report(self, review_data: Dict[str, Any]) -> Path:
        """
        Save architecture review report to cortex-brain/documents/analysis/.
        
        Args:
            review_data: Complete review results
            
        Returns:
            Path to saved report
        """
        # Create output directory
        output_dir = self.cortex_root / "cortex-brain" / "documents" / "analysis"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = output_dir / f"architecture-review-{timestamp}.md"
        
        # Format report content
        current = review_data["current_health"]
        trends = review_data["trend_analysis"]
        forecast_3m = review_data["forecast_3month"]
        forecast_6m = review_data["forecast_6month"]
        recommendations = review_data["recommendations"]
        
        content = f"""# CORTEX Architecture Review
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Agent:** Architecture Intelligence Agent  
**Type:** Holistic Review

---

## 📊 Current Health

**Overall Score:** {current['overall_score']:.1f}%  
**Status:** {"✅ Healthy" if current['overall_score'] >= 90 else "⚠️ Needs Attention" if current['overall_score'] >= 70 else "🚨 Critical"}

### Feature Breakdown
- **Total Features:** {current['feature_breakdown']['total']}
- **Healthy (≥90%):** {current['feature_breakdown']['healthy']}
- **Warning (70-89%):** {current['feature_breakdown']['warning']}
- **Critical (<70%):** {current['feature_breakdown']['critical']}

### Layer Scores
```
Discovered:    {current['layer_breakdown'].get('discovered', 0)}/20
Imported:      {current['layer_breakdown'].get('imported', 0)}/20
Instantiated:  {current['layer_breakdown'].get('instantiated', 0)}/20
Documented:    {current['layer_breakdown'].get('documented', 0)}/10
Tested:        {current['layer_breakdown'].get('tested', 0)}/10
Wired:         {current['layer_breakdown'].get('wired', 0)}/10
Optimized:     {current['layer_breakdown'].get('optimized', 0)}/10
```

---

## 📈 Trend Analysis (30 Days)

**Direction:** {trends['direction'].upper()}  
**Velocity:** {trends['velocity']:+.3f} points/day  
**Score Change:** {trends['score_change']:+.2f} points  
**Volatility:** {trends['volatility']:.2f}

### Insights
{"".join(f"- {insight}" + chr(10) for insight in trends['insights'])}

---

## 🔮 Forecast

### 3-Month Projection
- **Current Score:** {forecast_3m.get('current_score', 0):.1f}%
- **Predicted Score:** {forecast_3m.get('predicted_score', 0):.1f}%
- **Change:** {forecast_3m.get('predicted_change', 0):+.1f} points
- **Confidence:** {forecast_3m.get('confidence_percentage', 0):.1f}%
- **Intervention Needed:** {"⚠️ YES" if forecast_3m.get('intervention_needed') else "✅ NO"}

### 6-Month Projection
- **Predicted Score:** {forecast_6m.get('predicted_score', 0):.1f}%
- **Change:** {forecast_6m.get('predicted_change', 0):+.1f} points
- **Confidence:** {forecast_6m.get('confidence_percentage', 0):.1f}%

---

## 💡 CORTEX 4.0 Recommendations

{"".join(f"{i+1}. {rec}" + chr(10) for i, rec in enumerate(recommendations))}

---

## 📋 Next Actions

1. Review critical features if any
2. Monitor trend direction
3. Schedule remediation work if forecast shows decline
4. Re-run review in 7-14 days to track progress

---

**Note:** This is a read-only analysis. No architecture changes were made.
"""
        
        # Write report
        report_path.write_text(content, encoding="utf-8")
        
        logger.info(f"Architecture review report saved: {report_path}")
        
        return report_path
