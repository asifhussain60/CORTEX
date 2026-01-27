"""TroubleshootingInquiryHandler - CORTEX debugging help.

AC-ID: INQUIRY-012
Purpose: Answer CORTEX troubleshooting and debugging questions
Author: Asif Hussain
Date: 2026-01-27
"""

from typing import Any, Dict

from cortex.models.inquiry_models import AssembledContext
from cortex.orchestrators.domain.inquiry.base_inquiry_handler import (
    BaseInquiryHandler,
)


class TroubleshootingInquiryHandler(BaseInquiryHandler):
    """Specialized handler for CORTEX troubleshooting questions."""
    
    def handle(self, context: AssembledContext) -> Dict[str, Any]:
        """Handle troubleshooting inquiry."""
        answer = self._generate_troubleshooting_answer(context)
        
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
    
    def _generate_troubleshooting_answer(self, context: AssembledContext) -> str:
        """Generate troubleshooting answer."""
        if len(context.evidence_sources) == 0:
            return "No error patterns found. Check logs, run tests with -v flag, or review CORE governance rules for common issues."
        
        files = [ev.file_path for ev in context.evidence_sources[:2]]
        return f"Potential issue locations: {', '.join(files)}. Review evidence for error handling and validation logic."
