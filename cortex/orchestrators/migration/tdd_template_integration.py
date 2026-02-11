"""
Template Integration Script for TDDOrchestrator.

Migrates TDDOrchestrator to use BaseResponseTemplate with chainable blocks
for consistent, hierarchy-enforced response formatting.

Module: cortex.orchestrators.migration.tdd_template_integration
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
Authority: ENH-064 Response Template Migration
"""

from typing import Any, Dict, List

from cortex.orchestrators.core.base_response_template import (
    BaseResponseTemplate,
    SeverityLevel,
)
from cortex.orchestrators.response.chainable_blocks import BlockComposer


class TDDTemplateIntegration(BaseResponseTemplate):
    """
    Template integration mixin for TDDOrchestrator.

    Add this as a base class to TDDOrchestrator:

    class TDDOrchestrator(OrchestratorBaseProtocol, TDDTemplateIntegration):
        ...

    Then replace response generation with compose() method calls.
    """

    def compose(
        self,
        operation: str,
        tdd_phase: str,
        test_results: List[Dict[str, Any]],
        coverage_metrics: Dict[str, float],
        guidance: Dict[str, Any],
        recommendations: List[str],
        next_steps: List[Dict[str, Any]],
        brittleness_score: float = 0.0,
        security_findings: List[str] = None,
        **kwargs
    ) -> str:
        """
        Compose TDD orchestrator response with proper hierarchy.

        Args:
            operation: TDD operation (RED/GREEN/REFACTOR)
            tdd_phase: Current phase in TDD cycle
            test_results: List of test execution results
            coverage_metrics: Coverage percentages by metric
            guidance: Knowledge guidance from TDD rules
            recommendations: Best practice recommendations
            next_steps: Next steps with priority and effort
            brittleness_score: Code brittleness score (0-1)
            security_findings: Security issues detected
            **kwargs: Additional context

        Returns:
            Fully formatted response with single header and proper cascade
        """
        # MANDATORY: Single header
        response = self.header(operation)

        # Section 1: TDD Phase Status (h2)
        response += self.section(f"TDD Phase: {tdd_phase}", "🔴" if tdd_phase == "RED" else "🟢" if tdd_phase == "GREEN" else "🔄")

        # Use chainable blocks for complex sections
        composer = BlockComposer()

        # Test Results (subsection under Phase Status)
        if test_results:
            composer.add_test_results(test_results, "Test Execution")

        # Coverage Metrics (subsection)
        if coverage_metrics:
            composer.add_coverage(coverage_metrics, "Coverage Metrics")

        response += composer.build()

        # Section 2: Knowledge Guidance (h2)
        if guidance:
            response += self.section("Knowledge Guidance", "📚")

            # TDD rules (subsection - h3)
            if guidance.get("rules"):
                response += self.subsection("TDD Rules")
                for rule in guidance["rules"][:5]:  # Top 5 rules
                    response += f"- **{rule.get('rule_id')}:** {rule.get('description')}\n"
                response += "\n"

            # Best practices (subsection - h3)
            if guidance.get("best_practices"):
                response += self.subsection("Best Practices")
                for practice in guidance["best_practices"][:3]:
                    response += f"- {practice}\n"
                response += "\n"

        # Section 3: Quality Assessment (h2)
        response += self.section("Quality Assessment", "🔍")

        # Brittleness score (subsection - h3)
        if brittleness_score > 0:
            severity = SeverityLevel.CRITICAL if brittleness_score > 0.7 else SeverityLevel.WARNING
            response += self.challenge_box(
                "Brittleness Warning",
                f"Code brittleness score: {brittleness_score:.2f}/1.0\n\n"
                f"High brittleness indicates fragile code that breaks easily with changes. "
                f"Consider refactoring for better resilience.",
                severity
            )

        # Security findings (subsection - h3)
        if security_findings:
            response += self.subsection("Security Findings")
            for finding in security_findings:
                response += f"- ⚠️ {finding}\n"
            response += "\n"

        # Section 4: Recommendations (h2)
        if recommendations:
            composer = BlockComposer()
            composer.add_recommendations(recommendations, "Recommendations")
            response += composer.build()

        # Section 5: Next Steps (h2)
        if next_steps:
            composer = BlockComposer()
            composer.add_next_steps(next_steps, "Next Steps")
            response += composer.build()

        return response

    def format_tdd_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        reason: str
    ) -> str:
        """
        Format TDD phase transition message.

        Args:
            from_phase: Current phase
            to_phase: Next phase
            reason: Reason for transition

        Returns:
            Formatted transition message
        """
        return self.challenge_box(
            f"Phase Transition: {from_phase} → {to_phase}",
            reason,
            SeverityLevel.INFO
        )

    def format_test_failure_analysis(
        self,
        failed_tests: List[Dict[str, Any]]
    ) -> str:
        """
        Format test failure analysis with problem/solution pairs.

        Args:
            failed_tests: List of failed test details

        Returns:
            Formatted analysis
        """
        pairs = []
        for test in failed_tests:
            problem = f"{test.get('name')}: {test.get('error_message', 'Unknown error')}"
            solution = test.get('suggested_fix', 'Review test expectations and implementation')
            pairs.append((problem, solution))

        return self.problem_solution_table(pairs, "Test Failures")


# ============================================================================
# USAGE EXAMPLE FOR TDD ORCHESTRATOR
# ============================================================================

"""
# In tdd_orchestrator.py:

from cortex.orchestrators.migration.tdd_template_integration import TDDTemplateIntegration

class TDDOrchestrator(OrchestratorBaseProtocol, TDDTemplateIntegration):
    '''TDDOrchestrator with template integration.'''

    def execute_tdd_cycle(self, request: Dict[str, Any]) -> str:
        '''Execute TDD cycle with formatted response.'''

        # ... existing TDD logic ...

        # Generate response using template
        response = self.compose(
            operation="IMPLEMENT",
            tdd_phase=current_phase,
            test_results=test_results,
            coverage_metrics=coverage,
            guidance=guidance_data,
            recommendations=recommendations,
            next_steps=next_steps,
            brittleness_score=brittleness_score,
            security_findings=security_issues
        )

        return response

# Benefits:
# 1. Single header enforced (no repetition)
# 2. Proper h2→h3→h4 cascade
# 3. Challenge boxes for warnings
# 4. Problem/solution tables for errors
# 5. Chainable blocks for complex sections
"""
