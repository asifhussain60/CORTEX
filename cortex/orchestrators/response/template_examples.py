"""
Example implementations of BaseResponseTemplate for CORTEX orchestrators.

Demonstrates:
1. TDDOrchestrator — Test-driven development responses
2. LENSSynthesis — Analysis and intelligence responses
3. PlanOrchestrator — Phase planning responses

Module: cortex.orchestrators.response.template_examples
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
"""

from typing import Dict, List, Any
from cortex.orchestrators.core.base_response_template import (
    BaseResponseTemplate,
    SeverityLevel,
    SectionType
)


# ============================================================================
# EXAMPLE 1: TDD ORCHESTRATOR
# ============================================================================


class TDDOrchestratorTemplate(BaseResponseTemplate):
    """Template for TDD Orchestrator responses."""
    
    def __init__(self):
        super().__init__(orchestrator_name="TDDOrchestrator", mode="CORTEX")
    
    def compose(
        self,
        operation: str = "IMPLEMENT",
        tests: List[Dict[str, Any]] = None,
        coverage: float = 0.0,
        implementation: str = "",
        challenges: List[Dict[str, str]] = None
    ) -> str:
        """
        Compose TDD response.
        
        Args:
            operation: Operation type (IMPLEMENT, FIX, etc.)
            tests: List of test results
            coverage: Code coverage percentage
            implementation: Implementation code summary
            challenges: List of design challenges
        
        Returns:
            Formatted TDD response
        """
        tests = tests or []
        challenges = challenges or []
        
        # Start with header (ONCE)
        response = self.header(operation)
        
        # Test Results Section
        response += self.section("Test Results", "🧪", SectionType.TESTING)
        response += self._format_test_results(tests)
        
        # Coverage Metrics
        response += self.subsection("Coverage Metrics")
        response += self._format_coverage(coverage)
        
        # Implementation Section
        if implementation:
            response += self.section("Implementation", "🔨", SectionType.IMPLEMENTATION)
            response += f"\n{implementation}\n"
        
        # Challenges (if any)
        for challenge in challenges:
            response += self.challenge_box(
                title=challenge.get("title", "Design Question"),
                content=challenge.get("content", ""),
                severity=SeverityLevel.WARNING
            )
        
        # Next Steps
        response += self.section("Next Steps", "⏭️", SectionType.NEXT_STEPS)
        response += self._format_next_steps(tests, coverage)
        
        return response
    
    def _format_test_results(self, tests: List[Dict[str, Any]]) -> str:
        """Format test results table."""
        if not tests:
            return "\n_No tests executed._\n"
        
        passing = sum(1 for t in tests if t.get("passed", False))
        total = len(tests)
        
        table = f"\n**Status:** {passing}/{total} tests passing\n\n"
        table += "| Test | Status | Duration |\n"
        table += "|------|--------|----------|\n"
        
        for test in tests:
            status = "✅" if test.get("passed") else "❌"
            name = test.get("name", "Unknown")
            duration = test.get("duration_ms", 0)
            table += f"| {name} | {status} | {duration}ms |\n"
        
        return table
    
    def _format_coverage(self, coverage: float) -> str:
        """Format coverage metrics."""
        status = "✅" if coverage >= 80 else "⚠️" if coverage >= 60 else "❌"
        return f"\n{status} **Coverage:** {coverage:.1f}%\n"
    
    def _format_next_steps(self, tests: List[Dict[str, Any]], coverage: float) -> str:
        """Format next steps based on test results."""
        steps = []
        
        failing = [t for t in tests if not t.get("passed", False)]
        if failing:
            steps.append(f"1. Fix {len(failing)} failing test(s)")
        
        if coverage < 80:
            steps.append(f"2. Increase coverage from {coverage:.1f}% to 80%+")
        
        if not steps:
            steps.append("1. ✅ All tests passing, proceed with deployment")
        
        return "\n" + "\n".join(steps) + "\n"


# ============================================================================
# EXAMPLE 2: LENS SYNTHESIS ORCHESTRATOR
# ============================================================================


class LENSSynthesisTemplate(BaseResponseTemplate):
    """Template for LENS Synthesis responses."""
    
    def __init__(self):
        super().__init__(orchestrator_name="LENSSynthesis", mode="CORTEX")
    
    def compose(
        self,
        operation: str = "ANALYZE",
        intent: str = "",
        confidence: float = 0.0,
        features: List[str] = None,
        problems: List[Tuple[str, str]] = None,
        routing: str = "",
        recommendations: List[str] = None
    ) -> str:
        """
        Compose LENS analysis response.
        
        Args:
            operation: Operation type
            intent: Classified intent
            confidence: Classification confidence
            features: Identified features
            problems: List of (problem, solution) tuples
            routing: Routing decision
            recommendations: List of recommendations
        
        Returns:
            Formatted LENS response
        """
        features = features or []
        problems = problems or []
        recommendations = recommendations or []
        
        # Header
        response = self.header(operation)
        
        # Intent Classification
        response += self.section("Intent Classification", "🔍", SectionType.ANALYSIS)
        response += self._format_intent(intent, confidence)
        
        # Feature Analysis
        if features:
            response += self.subsection("Identified Features")
            response += "\n" + "\n".join(f"- {f}" for f in features) + "\n"
        
        # Problems & Solutions
        if problems:
            response += self.section("Issues & Solutions", "📋", SectionType.FINDINGS)
            response += self.problem_solution_table(problems)
        
        # Routing Decision
        if routing:
            response += self.section("Routing Decision", "🚀", SectionType.RECOMMENDATIONS)
            response += f"\n**Orchestrator:** {routing}\n"
        
        # Recommendations
        if recommendations:
            response += self.subsection("Recommendations")
            response += "\n" + "\n".join(f"{i+1}. {r}" for i, r in enumerate(recommendations)) + "\n"
        
        return response
    
    def _format_intent(self, intent: str, confidence: float) -> str:
        """Format intent classification."""
        conf_emoji = "✅" if confidence >= 0.8 else "⚠️" if confidence >= 0.6 else "❌"
        
        return (
            f"\n| Field | Value |\n"
            f"|-------|-------|\n"
            f"| **Intent** | {intent} |\n"
            f"| **Confidence** | {conf_emoji} {confidence:.1%} |\n"
        )


# ============================================================================
# EXAMPLE 3: PLAN ORCHESTRATOR
# ============================================================================


class PlanOrchestratorTemplate(BaseResponseTemplate):
    """Template for Plan Orchestrator responses."""
    
    def __init__(self):
        super().__init__(orchestrator_name="PlanOrchestrator", mode="CORTEX")
    
    def compose(
        self,
        operation: str = "PLAN",
        phase_name: str = "",
        stages: List[Dict[str, Any]] = None,
        acceptance_criteria: List[str] = None,
        metrics: Dict[str, Any] = None,
        challenges: List[Dict[str, str]] = None
    ) -> str:
        """
        Compose phase planning response.
        
        Args:
            operation: Operation type
            phase_name: Phase name
            stages: List of stage specifications
            acceptance_criteria: List of ACs
            metrics: Success metrics
            challenges: Planning challenges
        
        Returns:
            Formatted plan response
        """
        stages = stages or []
        acceptance_criteria = acceptance_criteria or []
        metrics = metrics or {}
        challenges = challenges or []
        
        # Header
        response = self.header(operation)
        
        # Phase Overview
        response += self.section(f"Phase: {phase_name}", "📋")
        response += self._format_phase_overview(stages)
        
        # Stage Breakdown
        response += self.section("Stage Breakdown", "🔨", SectionType.IMPLEMENTATION)
        response += self._format_stages(stages)
        
        # Acceptance Criteria
        if acceptance_criteria:
            response += self.section("Acceptance Criteria", "✅", SectionType.TESTING)
            response += self._format_acceptance_criteria(acceptance_criteria)
        
        # Success Metrics
        if metrics:
            response += self.section("Success Metrics", "📊", SectionType.METRICS)
            response += self._format_metrics(metrics)
        
        # Challenges
        for challenge in challenges:
            response += self.challenge_box(
                title=challenge.get("title", "Planning Question"),
                content=challenge.get("content", ""),
                severity=SeverityLevel.INFO
            )
        
        return response
    
    def _format_phase_overview(self, stages: List[Dict[str, Any]]) -> str:
        """Format phase overview."""
        total_days = sum(s.get("duration_days", 0) for s in stages)
        return (
            f"\n**Stages:** {len(stages)}\n"
            f"**Duration:** {total_days} days\n"
        )
    
    def _format_stages(self, stages: List[Dict[str, Any]]) -> str:
        """Format stage table."""
        if not stages:
            return "\n_No stages defined._\n"
        
        table = "\n| Stage | Duration | Priority | Tasks |\n"
        table += "|-------|----------|----------|-------|\n"
        
        for stage in stages:
            name = stage.get("name", "Unknown")
            duration = stage.get("duration_days", 0)
            priority = stage.get("priority", "P2")
            tasks = len(stage.get("tasks", []))
            table += f"| {name} | {duration}d | {priority} | {tasks} |\n"
        
        return table
    
    def _format_acceptance_criteria(self, criteria: List[str]) -> str:
        """Format acceptance criteria checklist."""
        return "\n" + "\n".join(f"- [ ] {c}" for c in criteria) + "\n"
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format success metrics table."""
        table = "\n| Metric | Target | Validation |\n"
        table += "|--------|--------|------------|\n"
        
        for key, value in metrics.items():
            target = value.get("target", "N/A")
            validation = value.get("validation", "N/A")
            table += f"| {key} | {target} | {validation} |\n"
        
        return table


# ============================================================================
# USAGE EXAMPLES
# ============================================================================


def example_tdd_response():
    """Example TDD response."""
    template = TDDOrchestratorTemplate()
    
    return template.compose(
        operation="IMPLEMENT",
        tests=[
            {"name": "test_user_creation", "passed": True, "duration_ms": 12},
            {"name": "test_user_validation", "passed": True, "duration_ms": 8},
            {"name": "test_user_deletion", "passed": False, "duration_ms": 15},
        ],
        coverage=75.0,
        implementation="Created User model with validation logic",
        challenges=[
            {
                "title": "Soft Delete Strategy",
                "content": "Should we implement soft delete (flag) or hard delete (remove)?",
            }
        ]
    )


def example_lens_response():
    """Example LENS response."""
    template = LENSSynthesisTemplate()
    
    return template.compose(
        operation="ANALYZE",
        intent="IMPLEMENT",
        confidence=0.92,
        features=["User authentication", "API endpoints", "Data validation"],
        problems=[
            ("Static routing", "Dynamic multi-orchestrator routing"),
            ("Stub examination data", "Real AST/Git analysis"),
        ],
        routing="TDDOrchestrator",
        recommendations=[
            "Implement semantic intent classification",
            "Integrate knowledge base with Phase 4",
            "Add confidence scoring with historical data",
        ]
    )


def example_plan_response():
    """Example Plan response."""
    template = PlanOrchestratorTemplate()
    
    return template.compose(
        operation="PLAN",
        phase_name="Phase 53: LENS Intelligence Upgrade",
        stages=[
            {"name": "S1: Foundation Fixes", "duration_days": 2, "priority": "P0", "tasks": ["T1", "T2"]},
            {"name": "S2: Knowledge Integration", "duration_days": 2, "priority": "P0", "tasks": ["T1", "T2", "T3"]},
            {"name": "S3: Semantic Classification", "duration_days": 3, "priority": "P1", "tasks": ["T1", "T2"]},
        ],
        acceptance_criteria=[
            "AC-001: Phase 2 connected to LENSOrchestrator",
            "AC-002: Phase 4 loads 45+ YAML files",
            "AC-003: Intent accuracy ≥95%",
        ],
        metrics={
            "Intent Accuracy": {"target": "95%", "validation": "Test suite"},
            "Latency P95": {"target": "<50ms", "validation": "Load testing"},
        },
        challenges=[
            {
                "title": "NLP Model Selection",
                "content": "Should we use sentence-transformers or custom embeddings?",
            }
        ]
    )


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "TDDOrchestratorTemplate",
    "LENSSynthesisTemplate",
    "PlanOrchestratorTemplate",
    "example_tdd_response",
    "example_lens_response",
    "example_plan_response",
]
