"""
Template Integration Script for LENSSynthesis.

Migrates LENSSynthesis to use BaseResponseTemplate with chainable blocks
for consistent, hierarchy-enforced response formatting.

Module: cortex.orchestrators.migration.lens_template_integration
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
Authority: ENH-064 Response Template Migration
"""

from typing import Any, Dict, List, Optional

from cortex.orchestrators.core.base_response_template import (
    BaseResponseTemplate,
    SeverityLevel,
)
from cortex.orchestrators.response.chainable_blocks import BlockComposer


class LENSTemplateIntegration(BaseResponseTemplate):
    """
    Template integration mixin for LENSSynthesis.

    Add this as a base class to LENSSynthesis:

    class LENSSynthesis(LENSTemplateIntegration):
        ...

    Then replace response generation with compose() method calls.
    """

    def compose(
        self,
        operation: str,
        language_insights: Dict[str, Any],
        examination_findings: Dict[str, Any],
        navigation_results: Dict[str, Any],
        synthesis_recommendations: List[Dict[str, Any]],
        confidence_score: float,
        routing_decision: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        Compose LENS synthesis response with proper hierarchy.

        Args:
            operation: LENS operation (ANALYZE, SYNTHESIZE, etc.)
            language_insights: Phase 1 - Language analysis results
            examination_findings: Phase 2 - Code examination results
            navigation_results: Phase 3 - Domain navigation results
            synthesis_recommendations: Phase 4 - Synthesis recommendations
            confidence_score: Overall confidence (0-1)
            routing_decision: Next orchestrator routing decision
            **kwargs: Additional context

        Returns:
            Fully formatted response with single header and proper cascade
        """
        # MANDATORY: Single header
        response = self.header(operation)

        # Section 1: LENS Protocol Overview (h2)
        response += self.section("LENS Protocol Execution", "🔍")
        response += self._format_lens_phases(
            language_insights,
            examination_findings,
            navigation_results
        )

        # Section 2: Intent Classification (h2)
        response += self.section("Intent Classification", "🎯")

        # Confidence level (subsection - h3)
        response += self.subsection("Confidence Assessment")
        confidence_emoji = "🟢" if confidence_score >= 0.8 else "🟡" if confidence_score >= 0.6 else "🔴"
        response += f"{confidence_emoji} **Confidence:** {confidence_score:.0%}\n\n"

        # Classification table (subsection - h3)
        if language_insights:
            response += self.subsection("Classification Details")
            response += "| Field | Value |\n"
            response += "|-------|-------|\n"
            response += f"| **Intent** | {language_insights.get('intent_type', 'Unknown')} |\n"
            response += f"| **Domain** | {language_insights.get('domain', 'General')} |\n"
            response += f"| **Complexity** | {language_insights.get('complexity', 'Medium')} |\n"
            response += f"| **Scope** | {language_insights.get('scope', 'Module')} |\n\n"

        # Low confidence challenge (if needed)
        if confidence_score < 0.6:
            response += self.challenge_box(
                "Low Confidence Warning",
                f"Classification confidence is {confidence_score:.0%}, below the 60% threshold.\n\n"
                "**Recommendations:**\n"
                "- Provide more context about your request\n"
                "- Specify target files or modules\n"
                "- Clarify expected outcomes\n\n"
                "Would you like to refine your request for better analysis?",
                SeverityLevel.WARNING
            )

        # Section 3: Feature Analysis (h2)
        if examination_findings:
            response += self.section("Feature Analysis", "📊")

            # Code examination (subsection - h3)
            response += self.subsection("Code Examination")

            # Metrics table
            if examination_findings.get("metrics"):
                response += "| Metric | Value | Status |\n"
                response += "|--------|-------|--------|\n"

                for metric, value in examination_findings["metrics"].items():
                    status = "✅" if value > 0 else "⚪"
                    response += f"| {metric} | {value} | {status} |\n"

                response += "\n"

            # Code patterns (subsection - h3)
            if examination_findings.get("patterns"):
                response += self.subsection("Detected Patterns")
                for pattern in examination_findings["patterns"][:5]:
                    response += f"- {pattern}\n"
                response += "\n"

        # Section 4: Domain Navigation (h2)
        if navigation_results:
            response += self.section("Domain Knowledge", "📚")

            # Knowledge sources (subsection - h3)
            if navigation_results.get("sources"):
                response += self.subsection("Knowledge Sources")
                for source in navigation_results["sources"][:3]:
                    response += f"- **{source.get('domain')}:** {source.get('relevance', 'N/A')} relevance\n"
                response += "\n"

            # Best practices (subsection - h3)
            if navigation_results.get("best_practices"):
                response += self.subsection("Applicable Best Practices")
                for practice in navigation_results["best_practices"][:3]:
                    response += f"- {practice}\n"
                response += "\n"

        # Section 5: Synthesis Recommendations (h2)
        if synthesis_recommendations:
            response += self.section("Synthesis Recommendations", "💡")

            # Group by priority
            high_priority = [r for r in synthesis_recommendations if r.get("priority") == "high"]
            medium_priority = [r for r in synthesis_recommendations if r.get("priority") == "medium"]

            if high_priority:
                response += self.subsection("High Priority")
                for rec in high_priority[:3]:
                    response += f"**{rec.get('source_phase', 'Unknown')}:** {rec.get('insight', '')}\n\n"
                    response += f"- *Reasoning:* {rec.get('reasoning', 'N/A')}\n"
                    response += f"- *Confidence:* {rec.get('confidence', 0):.0%}\n\n"

            if medium_priority:
                response += self.subsection("Medium Priority")
                for rec in medium_priority[:3]:
                    response += f"- **{rec.get('source_phase')}:** {rec.get('insight')}\n"
                response += "\n"

        # Section 6: Routing Decision (h2)
        if routing_decision:
            response += self.section("Next Steps", "⏭️")

            response += self.subsection("Orchestrator Routing")
            response += "| Field | Value |\n"
            response += "|-------|-------|\n"
            response += f"| **Target Orchestrator** | {routing_decision.get('orchestrator', 'Unknown')} |\n"
            response += f"| **Reason** | {routing_decision.get('reason', 'N/A')} |\n"
            response += f"| **Priority** | {routing_decision.get('priority', 'P2')} |\n"
            response += f"| **Estimated Effort** | {routing_decision.get('effort', 'N/A')} |\n\n"

        return response

    def _format_lens_phases(
        self,
        language: Dict[str, Any],
        examination: Dict[str, Any],
        navigation: Dict[str, Any]
    ) -> str:
        """
        Format LENS 4-phase execution status.

        Args:
            language: Phase 1 results
            examination: Phase 2 results
            navigation: Phase 3 results

        Returns:
            Formatted phase status
        """
        output = self.subsection("Phase Execution Status")
        output += "| Phase | Status | Duration | Insights |\n"
        output += "|-------|--------|----------|----------|\n"

        # Phase 1: Language
        lang_status = "✅" if language else "⚪"
        lang_duration = language.get("duration_ms", 0) if language else 0
        lang_insights = len(language.get("insights", [])) if language else 0
        output += f"| 1. Language | {lang_status} | {lang_duration}ms | {lang_insights} |\n"

        # Phase 2: Examination
        exam_status = "✅" if examination else "⚪"
        exam_duration = examination.get("duration_ms", 0) if examination else 0
        exam_insights = len(examination.get("findings", [])) if examination else 0
        output += f"| 2. Examination | {exam_status} | {exam_duration}ms | {exam_insights} |\n"

        # Phase 3: Navigation
        nav_status = "✅" if navigation else "⚪"
        nav_duration = navigation.get("duration_ms", 0) if navigation else 0
        nav_insights = len(navigation.get("recommendations", [])) if navigation else 0
        output += f"| 3. Navigation | {nav_status} | {nav_duration}ms | {nav_insights} |\n"

        # Phase 4: Synthesis (always complete if we're here)
        output += "| 4. Synthesis | 🔵 | In Progress | — |\n\n"

        return output

    def format_lens_challenge(
        self,
        disagreement: str,
        alternative: str,
        reasoning: str
    ) -> str:
        """
        Format LENS-based challenge with alternative proposal.

        Args:
            disagreement: What LENS disagrees with
            alternative: LENS alternative proposal
            reasoning: Why LENS recommends the alternative

        Returns:
            Formatted challenge box
        """
        content = f"**Current Request:** {disagreement}\n\n"
        content += f"**LENS Proposal:** {alternative}\n\n"
        content += f"**Reasoning:** {reasoning}\n"

        return self.challenge_box(
            "LENS Challenge",
            content,
            SeverityLevel.WARNING
        )


# ============================================================================
# USAGE EXAMPLE FOR LENS SYNTHESIS
# ============================================================================

"""
# In lens_synthesis.py:

from cortex.orchestrators.migration.lens_template_integration import LENSTemplateIntegration

class LENSSynthesis(LENSTemplateIntegration):
    '''LENSSynthesis with template integration.'''

    def synthesize(self, context: LENSContext) -> Result[str, str]:
        '''Synthesize LENS insights with formatted response.'''

        # ... existing LENS logic ...

        # Generate response using template
        response = self.compose(
            operation="ANALYZE",
            language_insights=context.language_analysis,
            examination_findings=context.code_examination,
            navigation_results=context.domain_navigation,
            synthesis_recommendations=recommendations,
            confidence_score=confidence,
            routing_decision=routing_info
        )

        return Ok(response)

# Benefits:
# 1. Single header enforced (no repetition)
# 2. Proper h2→h3→h4 cascade for 4 phases
# 3. Challenge boxes for low confidence
# 4. Phase status table shows execution progress
# 5. Routing decision clearly formatted
"""
