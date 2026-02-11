"""ArchitectureInquiryHandler - CORTEX architecture questions.

AC-ID: INQUIRY-009
Purpose: Answer CORTEX architecture and design questions
Author: Asif Hussain
Date: 2026-01-27
"""

from typing import Any, Dict

from cortex.models.inquiry_models import AssembledContext
from cortex.orchestrators.domain.inquiry.base_inquiry_handler import (
    BaseInquiryHandler,
)


class ArchitectureInquiryHandler(BaseInquiryHandler):
    """Specialized handler for CORTEX architecture questions.

    Focuses on: System design, component integration, wiring patterns,
    orchestrator relationships, phase dependencies.
    """

    def handle(self, context: AssembledContext) -> Dict[str, Any]:
        """Handle architecture inquiry.

        Args:
            context: Assembled context with CORTEX evidence

        Returns:
            Response with architecture-focused answer
        """
        answer = self._generate_architecture_answer(context)

        evidence_refs = [
            {
                "file": ev.file_path,
                "line": ev.line_number,
                "content": ev.content,
                "reference": ev.format_reference(),
            }
            for ev in context.evidence_sources
        ]

        return {
            "answer": answer,
            "evidence": evidence_refs,
            "confidence": context.confidence,
            "tier3_knowledge": context.tier3_knowledge or [],
            "core_rules": context.core_rules or [],
        }

    def _generate_architecture_answer(
        self,
        context: AssembledContext,
    ) -> str:
        """Generate architecture-focused answer.

        Args:
            context: Assembled context

        Returns:
            Architecture answer (40-60 words)
        """
        if len(context.evidence_sources) == 0:
            return (
                "No direct architectural evidence found. This could indicate "
                "the component is planned but not yet implemented, or it uses "
                "a different naming convention. Check the DatabaseBackedRegistry "
                "for orchestrator wiring or review phase specifications."
            )

        # Extract architecture-relevant info
        files = [ev.file_path for ev in context.evidence_sources[:3]]
        file_summary = ", ".join(files)

        return (
            f"Architecture analysis: Found implementation across {len(context.evidence_sources)} "
            f"files ({file_summary}). Key components show orchestrator integration patterns. "
            f"Review evidence for wiring details and phase dependencies. "
            f"Tier3 knowledge available: {', '.join(context.tier3_knowledge or ['none'])}."
        )
