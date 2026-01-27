"""GenericCodeInquiryHandler - Universal code Q&A for any repository.

AC-ID: INQUIRY-006-NEW
Purpose: Answer questions about any codebase using generic code analysis
Author: Asif Hussain
Date: 2026-01-27

Capabilities:
- AST-based architecture analysis
- Git history pattern detection
- Comment-based intent detection
- Generic code pattern recognition
- Function/class discovery

Limitations:
- No Tier3 knowledge (domain-agnostic)
- No CORE rule context (CORTEX-specific)
- No peer validation (user repos private)
- Generic answers only
"""

from typing import Dict, List, Any

from cortex.models.inquiry_models import AssembledContext, EvidenceSource


class GenericCodeInquiryHandler:
    """Universal code inquiry handler for any repository.
    
    Provides code analysis without CORTEX-specific domain knowledge.
    Uses evidence from LENS analyzers (Git/AST/Comment) to answer
    questions about any codebase.
    """
    
    def handle(self, context: AssembledContext) -> Dict[str, Any]:
        """Handle inquiry using generic code analysis.
        
        Args:
            context: Assembled context with evidence
            
        Returns:
            Response dictionary with answer, evidence, confidence, disclaimer
        """
        # Format response from evidence
        response = self._format_response(
            question=context.question,
            evidence_sources=context.evidence_sources,
            confidence=context.confidence,
        )
        
        # Add disclaimer for user repos
        response = self._add_disclaimer(
            response,
            is_cortex=context.repo_context.is_cortex_repo(),
        )
        
        return response
    
    def _format_response(
        self,
        question: str,
        evidence_sources: List[EvidenceSource],
        confidence: float,
    ) -> Dict[str, Any]:
        """Format response from evidence sources.
        
        Args:
            question: Original question
            evidence_sources: List of code evidence
            confidence: Confidence score
            
        Returns:
            Response dictionary with answer and evidence
        """
        # Generate answer from evidence
        if len(evidence_sources) == 0:
            answer = self._generate_no_evidence_answer(question)
        else:
            answer = self._generate_answer_from_evidence(
                question,
                evidence_sources,
            )
        
        # Format evidence references
        evidence_refs = [
            {
                "file": ev.file_path,
                "line": ev.line_number,
                "content": ev.content,
                "reference": ev.format_reference(),
            }
            for ev in evidence_sources
        ]
        
        return {
            "answer": answer,
            "evidence": evidence_refs,
            "confidence": confidence,
        }
    
    def _generate_answer_from_evidence(
        self,
        question: str,
        evidence_sources: List[EvidenceSource],
    ) -> str:
        """Generate answer from evidence sources.
        
        Args:
            question: Original question
            evidence_sources: List of code evidence
            
        Returns:
            Generated answer (40-60 words target)
        """
        # Extract file paths and locations
        files = [ev.file_path for ev in evidence_sources[:3]]  # Top 3
        
        # Generate generic answer
        if len(evidence_sources) == 1:
            ev = evidence_sources[0]
            answer = (
                f"Based on code analysis, relevant implementation found in "
                f"{ev.file_path} at line {ev.line_number}. "
                f"The code shows: {ev.content[:50]}... "
                f"This appears to be the main entry point for your question."
            )
        elif len(evidence_sources) <= 3:
            file_list = ", ".join([f"{ev.file_path}:{ev.line_number}" for ev in evidence_sources])
            answer = (
                f"Code analysis found {len(evidence_sources)} relevant locations: "
                f"{file_list}. These files contain the implementation details "
                f"related to your question about the codebase structure."
            )
        else:
            file_list = ", ".join(files)
            answer = (
                f"Analysis identified {len(evidence_sources)} code locations "
                f"across {len(set(files))} files including {file_list}. "
                f"The implementation spans multiple modules indicating a "
                f"distributed architecture for this feature."
            )
        
        return answer
    
    def _generate_no_evidence_answer(self, question: str) -> str:
        """Generate answer when no evidence found.
        
        Args:
            question: Original question
            
        Returns:
            Generic low-confidence answer
        """
        return (
            f"No direct code evidence found for this question in the repository. "
            f"This could mean: (1) the feature doesn't exist yet, "
            f"(2) it's named differently than expected, or "
            f"(3) it's implemented in external dependencies. "
            f"Try rephrasing your question with specific file or function names."
        )
    
    def _add_disclaimer(
        self,
        response: Dict[str, Any],
        is_cortex: bool,
    ) -> Dict[str, Any]:
        """Add disclaimer for user repository responses.
        
        Args:
            response: Response dictionary
            is_cortex: Whether repo is CORTEX
            
        Returns:
            Response with disclaimer field
        """
        if not is_cortex:
            response["disclaimer"] = (
                "🔍 Generic code analysis (no domain-specific knowledge). "
                "For CORTEX-specific questions, mention 'CORTEX' explicitly."
            )
        else:
            response["disclaimer"] = ""
        
        return response
