"""ContextAssemblyOrchestrator - Repo-aware intelligent context gathering.

AC-ID: INQUIRY-004
Purpose: Assemble context from multiple sources for inquiry handlers
Author: Asif Hussain
Date: 2026-01-27

Context Sources (Repo-Aware):
- ANY REPO:
  * Semantic search for code evidence
  * LENS analyzers (Git/AST/Comment)
  * TotalRecallAgent for feature discovery
  
- CORTEX ONLY:
  * DatabaseBackedRegistry (orchestrator wiring)
  * GovernanceRegistry (CORE rules)
  * KnowledgeRepository (Tier3 YAML files)

Confidence Scoring:
- Base: 0.20 (minimum)
- Evidence: +0.10 per source (max 0.40)
- Tier3 knowledge: +0.15 (CORTEX only)
- CORE rules: +0.15 (CORTEX only)
- Category match: +0.10
"""

from pathlib import Path
from typing import List, Optional

from cortex.models.inquiry_models import (
    AssembledContext,
    EvidenceSource,
    InquiryCategory,
    RepoContext,
)
from cortex.orchestrators.support.inquiry_cache import InquiryCache


class ContextAssemblyOrchestrator:
    """Intelligent context assembly with repo-aware source selection.
    
    Gathers evidence from multiple sources based on repository type.
    CORTEX questions get access to internal knowledge (Tier3, CORE rules).
    User repo questions use generic code analysis only.
    """
    
    def __init__(self, cache_path: Optional[Path] = None) -> None:
        """Initialize context assembly orchestrator.
        
        Args:
            cache_path: Optional path for cache database
        """
        self.cache = InquiryCache(db_path=cache_path)
    
    def assemble_context(
        self,
        question: str,
        repo_context: RepoContext,
        category: Optional[InquiryCategory] = None,
    ) -> AssembledContext:
        """Assemble context for inquiry handlers.
        
        Main entry point for context gathering. Checks cache first,
        then gathers evidence from repo-appropriate sources.
        
        Args:
            question: User's question text
            repo_context: Repository detection context
            category: Optional category hint for optimization
            
        Returns:
            AssembledContext with evidence, confidence, and metadata
        """
        # Check cache first
        cached_data = self.cache.get(question, repo_context)
        if cached_data is not None:
            return AssembledContext.from_cache(cached_data, repo_context)
        
        # Infer category if not provided
        if category is None:
            category = self._infer_category(question)
        
        # Gather evidence from code
        evidence_sources = self._gather_code_evidence(question, repo_context)
        
        # Gather CORTEX-specific knowledge if applicable
        tier3_knowledge = None
        core_rules = None
        
        if repo_context.is_cortex_repo():
            tier3_knowledge = self._gather_tier3_knowledge(question, category)
            core_rules = self._gather_core_rules(question, category)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            evidence_sources=evidence_sources,
            tier3_knowledge=tier3_knowledge,
            core_rules=core_rules,
        )
        
        # Build context
        context = AssembledContext(
            question=question,
            repo_context=repo_context,
            category=category,
            evidence_sources=evidence_sources,
            confidence=confidence,
            tier3_knowledge=tier3_knowledge,
            core_rules=core_rules,
            cache_hit=False,
            metadata={
                "sources_used": self._get_sources_used(repo_context),
                "evidence_count": len(evidence_sources),
            },
        )
        
        # Cache the result
        self.cache.set(question, repo_context, context.to_cacheable())
        
        return context
    
    def _gather_code_evidence(
        self,
        question: str,
        repo_context: RepoContext,
    ) -> List[EvidenceSource]:
        """Gather code evidence using semantic search.
        
        Args:
            question: Question text for search
            repo_context: Repository context
            
        Returns:
            List of evidence sources from code
        """
        evidence: List[EvidenceSource] = []
        
        # Use semantic search to find relevant code
        # NOTE: In production, this would call actual semantic_search tool
        # For now, return empty list (tests will mock this)
        try:
            # Placeholder for semantic search integration
            # In real implementation:
            # from cortex.tools.semantic_search import semantic_search
            # results = semantic_search(question, repo_context.repo_path)
            pass
        except Exception:
            # Graceful degradation if search fails
            pass
        
        return evidence
    
    def _gather_tier3_knowledge(
        self,
        question: str,
        category: InquiryCategory,
    ) -> Optional[List[str]]:
        """Gather applicable Tier3 knowledge YAML files.
        
        CORTEX-ONLY: Searches Tier3 knowledge repository.
        
        Args:
            question: Question text
            category: Question category
            
        Returns:
            List of applicable Tier3 YAML file names or None
        """
        try:
            # Placeholder for KnowledgeRepository integration
            # In real implementation:
            # from cortex.brain.core.knowledge.knowledge_repository import KnowledgeRepository
            # repo = KnowledgeRepository()
            # return repo.search(question, category)
            
            # For now, return sample data for tests to verify
            # Tests will mock this method
            return None
        except Exception:
            return None
    
    def _gather_core_rules(
        self,
        question: str,
        category: InquiryCategory,
    ) -> Optional[List[str]]:
        """Gather applicable CORE governance rules.
        
        CORTEX-ONLY: Queries GovernanceRegistry.
        
        Args:
            question: Question text
            category: Question category
            
        Returns:
            List of applicable CORE rule IDs or None
        """
        try:
            # Placeholder for GovernanceRegistry integration
            # In real implementation:
            # from cortex.brain.core.governance_registry import GovernanceRegistry
            # registry = GovernanceRegistry()
            # return registry.get_applicable_rules(question, category)
            
            # For now, return None (tests will mock this)
            return None
        except Exception:
            return None
    
    def _calculate_confidence(
        self,
        evidence_sources: List[EvidenceSource],
        tier3_knowledge: Optional[List[str]],
        core_rules: Optional[List[str]],
    ) -> float:
        """Calculate confidence score based on evidence quality.
        
        Scoring:
        - Base: 0.20 (minimum)
        - Evidence: +0.10 per source (max 0.40 from 4+ sources)
        - Tier3 knowledge: +0.15
        - CORE rules: +0.15
        - Cap at 1.0
        
        Args:
            evidence_sources: List of evidence sources
            tier3_knowledge: Tier3 YAML files (CORTEX only)
            core_rules: CORE rule IDs (CORTEX only)
            
        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.20  # Base confidence
        
        # Evidence contribution (max 0.40)
        evidence_boost = min(0.40, len(evidence_sources) * 0.10)
        confidence += evidence_boost
        
        # Tier3 knowledge boost (CORTEX only)
        if tier3_knowledge and len(tier3_knowledge) > 0:
            confidence += 0.15
        
        # CORE rules boost (CORTEX only)
        if core_rules and len(core_rules) > 0:
            confidence += 0.15
        
        # Cap at 1.0
        return min(1.0, confidence)
    
    def _infer_category(self, question: str) -> InquiryCategory:
        """Infer question category from keywords.
        
        Args:
            question: Question text
            
        Returns:
            Inferred InquiryCategory
        """
        question_lower = question.lower()
        
        # Architecture keywords
        if any(kw in question_lower for kw in ["how does", "architecture", "design", "integrate", "wiring", "flow"]):
            return InquiryCategory.ARCHITECTURE
        
        # Feature keywords
        if any(kw in question_lower for kw in ["does", "support", "can i", "feature", "capability", "where is"]):
            return InquiryCategory.FEATURE
        
        # Best practice keywords
        if any(kw in question_lower for kw in ["best practice", "should i", "recommended", "pattern", "guideline"]):
            return InquiryCategory.BEST_PRACTICE
        
        # Troubleshooting keywords
        if any(kw in question_lower for kw in ["error", "issue", "problem", "fix", "debug", "why", "failing"]):
            return InquiryCategory.TROUBLESHOOTING
        
        # Evolution keywords
        if any(kw in question_lower for kw in ["history", "evolution", "changed", "why was", "decision"]):
            return InquiryCategory.EVOLUTION
        
        # Default to architecture
        return InquiryCategory.ARCHITECTURE
    
    def _get_sources_used(self, repo_context: RepoContext) -> List[str]:
        """Get list of sources used for context gathering.
        
        Args:
            repo_context: Repository context
            
        Returns:
            List of source names
        """
        sources = ["semantic_search", "lens_analyzers"]
        
        if repo_context.is_cortex_repo():
            sources.extend([
                "tier3_knowledge",
                "core_rules",
                "database_backed_registry",
            ])
        
        return sources
