"""FeatureInquiryHandler - CORTEX feature discovery.

AC-ID: INQUIRY-010
Purpose: Answer CORTEX feature availability and capability questions
Author: Asif Hussain
Date: 2026-01-27
"""

from typing import Any, Dict

from cortex.models.inquiry_models import AssembledContext
from cortex.orchestrators.domain.inquiry.base_inquiry_handler import (
    BaseInquiryHandler,
)


class FeatureInquiryHandler(BaseInquiryHandler):
    """Specialized handler for CORTEX feature questions."""
    
    def handle(self, context: AssembledContext) -> Dict[str, Any]:
        """Handle feature inquiry."""
        answer = self._generate_feature_answer(context)
        
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
    
    def _generate_feature_answer(self, context: AssembledContext) -> str:
        """Generate feature-focused answer."""
        if len(context.evidence_sources) == 0:
            return "Feature not found in codebase. Use TotalRecallAgent for discovery or check roadmap specifications."
        
        files = [ev.file_path for ev in context.evidence_sources[:2]]
        return f"Feature implemented in {', '.join(files)}. See evidence for entry points and usage patterns."
