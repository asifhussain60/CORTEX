"""EvolutionInquiryHandler - CORTEX code history.

AC-ID: INQUIRY-013
Purpose: Answer CORTEX evolution and history questions
Author: Asif Hussain
Date: 2026-01-27
"""

from typing import Any, Dict

from cortex.models.inquiry_models import AssembledContext
from cortex.orchestrators.domain.inquiry.base_inquiry_handler import (
    BaseInquiryHandler,
)


class EvolutionInquiryHandler(BaseInquiryHandler):
    """Specialized handler for CORTEX evolution questions."""

    def handle(self, context: AssembledContext) -> Dict[str, Any]:
        """Handle evolution inquiry."""
        answer = self._generate_evolution_answer(context)

        evidence_refs = [
            {"file": ev.file_path, "line": ev.line_number, "content": ev.content, "reference": ev.format_reference()}
            for ev in context.evidence_sources
        ]

        return {
            "answer": answer,
            "evidence": evidence_refs,
            "confidence": context.confidence,
            "tier3_knowledge": context.tier3_knowledge or [],
            "core_rules": context.core_rules or [],
        }

    def _generate_evolution_answer(self, context: AssembledContext) -> str:
        """Generate evolution answer."""
        return f"Code evolution: Found {len(context.evidence_sources)} relevant changes. Use git blame and LENS GitHistoryAnalyzer for detailed commit history and architectural decisions."
