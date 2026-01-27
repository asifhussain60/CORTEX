"""BestPracticeInquiryHandler - CORTEX best practices.

AC-ID: INQUIRY-011
Purpose: Answer CORTEX best practice and guideline questions
Author: Asif Hussain
Date: 2026-01-27
"""

from typing import Any, Dict

from cortex.models.inquiry_models import AssembledContext
from cortex.orchestrators.domain.inquiry.base_inquiry_handler import (
    BaseInquiryHandler,
)


class BestPracticeInquiryHandler(BaseInquiryHandler):
    """Specialized handler for CORTEX best practice questions."""
    
    def handle(self, context: AssembledContext) -> Dict[str, Any]:
        """Handle best practice inquiry."""
        answer = self._generate_best_practice_answer(context)
        
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
    
    def _generate_best_practice_answer(self, context: AssembledContext) -> str:
        """Generate best practice answer."""
        tier3 = context.tier3_knowledge or []
        core = context.core_rules or []
        
        if tier3 or core:
            return f"Best practices: Review Tier3 knowledge ({', '.join(tier3[:2] or ['none'])}) and CORE rules ({', '.join(core[:2] or ['none'])}). See evidence for implementation examples."
        
        return "Best practices: Check Tier3 knowledge repository and CORE governance rules for guidelines."
