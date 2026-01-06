"""
Knowledge Module - Phase 1 Implementation
CORTEX 5.5 Enhancement Epic

Provides company-specific knowledge integration without corrupting CORTEX core.
"""

from .company_knowledge_provider import CompanyKnowledgeProvider, CompanyKnowledge
from .knowledge_merger import KnowledgeMerger

__all__ = [
    "CompanyKnowledgeProvider",
    "CompanyKnowledge",
    "KnowledgeMerger",
]
