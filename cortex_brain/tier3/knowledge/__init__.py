"""
Tier 3 Knowledge Module
======================
Knowledge repository management with auto-indexing, retrieval, and governance.
"""

from .knowledge_indexer import KnowledgeIndexer
from .knowledge_governance import KnowledgeGovernanceManager
from .expert_registry import ExpertRegistry
from .ai_curator import AICurator
from .synthesis_engine import SynthesisEngine
from .retrieval_optimizer import RetrievalOptimizer

__all__ = ["KnowledgeIndexer", "KnowledgeGovernanceManager", "ExpertRegistry", "AICurator", "SynthesisEngine", "RetrievalOptimizer"]
