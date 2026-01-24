"""
Knowledge Ecosystem Components - Tier 3.

Provides knowledge management, governance, curation, and synthesis capabilities.
"""

from cortex_brain.tier3.knowledge.knowledge_governance import KnowledgeGovernanceManager, GovernanceRule
from cortex_brain.tier3.knowledge.expert_registry import ExpertRegistry, Expert
from cortex_brain.tier3.knowledge.ai_curator import AICurator, CurationResult
from cortex_brain.tier3.knowledge.knowledge_indexer import KnowledgeIndexer, IndexEntry
from cortex_brain.tier3.knowledge.synthesis_engine import SynthesisEngine, SynthesisResult

__all__ = [
    "KnowledgeGovernanceManager",
    "GovernanceRule",
    "ExpertRegistry",
    "Expert",
    "AICurator",
    "CurationResult",
    "KnowledgeIndexer",
    "IndexEntry",
    "SynthesisEngine",
    "SynthesisResult",
]
